from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from table2text import Settings, Table2TextWorkflow
from table2text.analytics import execute_plan
from table2text.audit import (
    apply_repair_proposal,
    apply_support_map_patches,
    build_profile_support_registry,
    build_writer_evidence_pack,
    decide_release_status,
    deterministic_audit,
    fallback_writer,
    materialise_writer_output,
    merge_quality_assessments,
    merge_audit_proposal,
    validate_repair_candidate,
    validate_writer_output,
)
from table2text.workflow import build_compact_writer_payload
from table2text.data import load_data, profile_data
from table2text.schemas import (
    AnalysisRoute,
    AnalyticalRecommendation,
    AuditAnnotation,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    ClaimPermission,
    ColumnProfile,
    DataUnderstanding,
    DataProfile,
    ErrorType,
    EvidenceItem,
    EvidenceLedger,
    ExecutionPlan,
    FactLedger,
    InvestigationTask,
    QualityStatus,
    RecommendedUse,
    ReleaseStatus,
    RepairCandidate,
    RepairStrategy,
    ReportQualityAssessment,
    ReportComponent,
    ReportSpecification,
    SentenceRepair,
    SentenceSupport,
    Severity,
    SupportType,
    TableProfile,
    TableUnderstanding,
    TargetStatus,
    ValidationStrategy,
    VerifiedFact,
    WriterAgentDraft,
    WriterOutput,
    WriterSectionDraft,
    WriterSentenceDraft,
    ZeroRisk,
)
from table2text.agents import (
    fallback_execution_plan,
    valid_quality_finding,
)


def make_passing_audit_report() -> AuditReport:
    return AuditReport(
        mode=AuditMode.INTERNAL,
        decision=AuditDecision.PASS,
        release_status=ReleaseStatus.APPROVED,
        annotations=[],
        applied_patches=[],
        factual_sentence_count=1,
        supported_sentence_count=1,
        support_rate=1.0,
        residual_risk="No high-confidence factual issue detected.",
        revision_instructions=[],
        quality_assessment=ReportQualityAssessment(
            status=QualityStatus.PASS,
            request_responsiveness=1.0,
            finding_selection=1.0,
            coherence=1.0,
            concision=1.0,
            caveat_integration=1.0,
            data_science_interpretation=1.0,
        ),
    )


def test_profile_detects_constant_and_suspicious_zero(tmp_path):
    path = tmp_path / "quality.csv"

    frame = pd.DataFrame(
        {
            "constant": [0] * 200,
            "pressure_like": [0] * 3 + list(np.linspace(990, 1030, 197)),
            "temperature": np.linspace(-10, 30, 200),
        }
    )
    frame.to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    table = profile.tables[0]

    constant = next(
        column
        for column in table.columns
        if column.name == "constant"
    )
    pressure = next(
        column
        for column in table.columns
        if column.name == "pressure_like"
    )

    assert constant.constant
    assert pressure.suspicious_zero_values


def test_constant_outcome_not_group_compared(tmp_path):
    path = tmp_path / "groups.csv"

    pd.DataFrame(
        {
            "group": ["rain", "snow"] * 100,
            "constant": [0] * 200,
            "variable": np.arange(200),
        }
    ).to_csv(path, index=False)

    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Describe the strongest relationships.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    evidence = execute_plan(
        bundle,
        plan,
        Settings(),
    )

    constant_comparisons = [
        item
        for item in evidence.items
        if item.route == AnalysisRoute.ASSOCIATION_COMPARISON
        and "constant" in item.source_columns
    ]

    assert not constant_comparisons


def test_weak_correlations_are_filtered(tmp_path):
    rng = np.random.default_rng(42)
    path = tmp_path / "weak.csv"

    pd.DataFrame(
        {
            "x": rng.normal(size=1_000),
            "y": rng.normal(size=1_000),
            "z": rng.normal(size=1_000),
        }
    ).to_csv(path, index=False)

    settings = replace(
        Settings(),
        min_abs_correlation=0.20,
    )

    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Report the strongest associations.",
        profile,
        AuditMode.INTERNAL,
        settings,
    )

    evidence = execute_plan(
        bundle,
        plan,
        settings,
    )

    correlations = [
        item.metrics["pearson_r"]
        for item in evidence.items
        if "pearson_r" in item.metrics
    ]

    assert all(abs(value) >= 0.20 for value in correlations)

def test_final_approved_status_cannot_have_block_decision():
    release_status = (
        ReleaseStatus.APPROVED_WITH_WARNINGS
    )

    final_decision = (
        AuditDecision.BLOCK
        if release_status
        == ReleaseStatus.HUMAN_REVIEW_REQUIRED
        else AuditDecision.PASS
    )

    assert final_decision == AuditDecision.PASS
    
def test_semantic_block_without_serious_annotations_is_advisory():
    deterministic = make_passing_audit_report()

    proposal = AuditRepairProposal(
        annotations=[],
        repairs=[],
        recommended_decision=AuditDecision.BLOCK,
        residual_risk=(
            "The model requested blocking without "
            "supporting serious annotations."
        ),
        quality_assessment=(
            deterministic.quality_assessment
        ),
    )

    merged = merge_audit_proposal(
        deterministic,
        proposal,
    )

    assert merged.decision == AuditDecision.PASS
    assert merged.release_status in {
        ReleaseStatus.APPROVED,
        ReleaseStatus.APPROVED_WITH_WARNINGS,
    }
    
def test_generic_request_does_not_invent_prediction_target(tmp_path):
    path = tmp_path / "weather.csv"

    pd.DataFrame(
        {
            "Formatted Date": pd.date_range(
                "2020-01-01",
                periods=300,
                freq="h",
            ),
            "Temperature (C)": np.sin(np.arange(300) / 24),
            "Humidity": np.linspace(0.3, 0.9, 300),
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))

    plan = fallback_execution_plan(
        "Understand the dataset and report its strongest findings.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    assert not any(
        task.route == AnalysisRoute.PREDICTIVE
        for task in plan.tasks
    )


def test_explicit_prediction_uses_selected_target(tmp_path):
    path = tmp_path / "model.csv"

    dates = pd.date_range(
        "2020-01-01",
        periods=500,
        freq="h",
    )

    temperature = np.sin(np.arange(500) / 24)

    pd.DataFrame(
        {
            "Formatted Date": dates,
            "Temperature": temperature,
            "Apparent Temperature": temperature + 0.001,
            "Humidity": np.linspace(0.2, 0.9, 500),
        }
    ).to_csv(path, index=False)

    settings = Settings()
    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Predict Temperature from the available variables.",
        profile,
        AuditMode.INTERNAL,
        settings,
    )

    predictive_task = next(
        task
        for task in plan.tasks
        if task.route == AnalysisRoute.PREDICTIVE
    )

    assert predictive_task.target_column == "Temperature"
    assert predictive_task.target_status == TargetStatus.USER_SELECTED
    assert predictive_task.validation_strategy == (
        ValidationStrategy.CHRONOLOGICAL_HOLDOUT
    )

    evidence = execute_plan(bundle, plan, settings)

    predictive_evidence = next(
        item
        for item in evidence.items
        if item.route == AnalysisRoute.PREDICTIVE
    )

    excluded = predictive_evidence.metrics.get(
        "features_excluded",
        [],
    )

    assert any(
        item.get("risk_type") == "target_proxy"
        for item in excluded
    )


def test_hourly_forecast_uses_longer_rolling_windows(tmp_path):
    path = tmp_path / "forecast.csv"
    length = 5_000

    pd.DataFrame(
        {
            "time": pd.date_range(
                "2020-01-01",
                periods=length,
                freq="h",
            ),
            "target": (
                10
                + np.sin(np.arange(length) * 2 * np.pi / 24)
            ),
        }
    ).to_csv(path, index=False)

    settings = Settings()
    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Forecast target.",
        profile,
        AuditMode.INTERNAL,
        settings,
    )

    evidence = execute_plan(bundle, plan, settings)

    forecast = next(
        item
        for item in evidence.items
        if item.route == AnalysisRoute.FORECASTING
    )

    assert forecast.validation_strategy == ValidationStrategy.ROLLING_ORIGIN
    assert forecast.metrics["test_window_points"] >= 168
    assert forecast.metrics["fold_count"] >= 1
    assert any(
        name.startswith("seasonal_naive_")
        for name in forecast.metrics["mean_mae"]
    )


def make_fact_fixture() -> tuple[FactLedger, EvidenceLedger]:
    evidence = EvidenceLedger(
        fingerprint="test",
        items=[
            EvidenceItem(
                evidence_id="EVD_0001",
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=["TASK_001"],
                finding="The table contains 96,453 rows.",
                metrics={"row_count": 96_453},
                source_tables=["weather"],
                source_columns=[],
                method="Direct row count.",
                validation_strategy=ValidationStrategy.NONE,
                practical_interpretation="The dataset is large.",
                strength_label="dataset_overview",
                limitations=[],
                prohibited_interpretations=[],
                recommendations=[],
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ],
    )

    ledger = FactLedger(
        writer_ready_facts=[
            VerifiedFact(
                fact_id="FACT_0001",
                source_candidate_id="CAN_0001",
                fact_summary="The table contains 96,453 rows.",
                evidence_ids=["EVD_0001"],
                structured_values={
                    "EVD_0001": {"row_count": 96_453}
                },
                entities=["weather"],
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ]
    )

    return ledger, evidence


def test_approximate_number_is_allowed():
    ledger, evidence = make_fact_fixture()

    sentence = "The dataset contains more than 96,000 observations."

    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )

    plan_spec = ReportSpecification(
        report_purpose="Test",
        target_length_words=300,
        maximum_main_findings=5,
        prioritisation_rule="Test",
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        plan_spec,
    )

    assert audit.decision == AuditDecision.PASS


def test_wrong_number_triggers_repair():
    ledger, evidence = make_fact_fixture()

    wrong_sentence = "The dataset contains 12 observations."

    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{wrong_sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=wrong_sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )

    replacement = "The dataset contains 96,453 observations."

    candidate = RepairCandidate(
        repair_id="REP_001",
        replacement_text=replacement,
        strategy=RepairStrategy.MINIMAL_CORRECTION,
        supporting_fact_ids=["FACT_0001"],
        supporting_evidence_ids=["EVD_0001"],
        factual_support_score=1.0,
        meaning_preservation_score=1.0,
        readability_score=1.0,
        residual_hallucination_risk=0.0,
    )

    assert not validate_repair_candidate(
        candidate,
        ledger,
        evidence,
    )

    proposal = AuditRepairProposal(
        annotations=[],
        repairs=[
            SentenceRepair(
                sentence_id="SENT_0001",
                original_sentence=wrong_sentence,
                annotation_ids=[],
                candidates=[candidate],
                preferred_repair_id="REP_001",
                selection_reason="Correct the unsupported number.",
            )
        ],
        recommended_decision=AuditDecision.REVISE,
        residual_risk="Repair required.",
        quality_assessment=ReportQualityAssessment(
            status=QualityStatus.PASS,
            request_responsiveness=1.0,
            finding_selection=1.0,
            coherence=1.0,
            concision=1.0,
            caveat_integration=1.0,
            data_science_interpretation=1.0,
        ),
    )

    repaired, patches = apply_repair_proposal(
        writer,
        proposal,
        ledger,
        evidence,
    )

    assert patches
    assert replacement in repaired.markdown
    assert wrong_sentence not in repaired.markdown


def test_full_workflow_without_llm(tmp_path):
    path = tmp_path / "example.csv"

    frame = pd.DataFrame(
        {
            "category": ["a", "b"] * 100,
            "value": np.arange(200),
            "constant": [0] * 200,
        }
    )

    frame.to_csv(path, index=False)

    settings = replace(
        Settings(),
        use_llm=False,
        output_dir=tmp_path / "runs",
        max_revision_rounds=1,
    )

    result = Table2TextWorkflow(settings).run_sync(
        inputs=[path],
        request=(
            "Understand the dataset and report its strongest supported findings."
        ),
        audit_mode=AuditMode.INTERNAL,
    )

    assert result.evidence_ledger.items
    assert result.fact_ledger.writer_ready_facts
    assert result.raw_writer_output.writer_mode == "deterministic_fallback"

    run_directory = settings.output_dir / result.run_id

    assert (run_directory / "09_writer_raw_report.md").exists()
    assert (run_directory / "final_report.md").exists()
    assert (run_directory / "final_result.json").exists()
    assert (
        run_directory
        / "02_profile_support_registry.json"
    ).exists()

    assert result.release_status in {
        ReleaseStatus.APPROVED,
        ReleaseStatus.APPROVED_WITH_WARNINGS,
        ReleaseStatus.HUMAN_REVIEW_REQUIRED,
    }


def test_zero_wind_bearing_is_likely_valid(tmp_path):
    path = tmp_path / "bearing.csv"
    pd.DataFrame(
        {
            "Wind Bearing (degrees)": [0, 10, 90, 180, 270] * 20,
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    column = profile.tables[0].columns[0]

    assert column.zero_risk == ZeroRisk.LIKELY_VALID
    assert not column.suspicious_zero_values


def test_zero_visibility_is_context_dependent(tmp_path):
    path = tmp_path / "visibility.csv"
    pd.DataFrame(
        {
            "Visibility (km)": [0, 1, 5, 10, 16] * 20,
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    column = profile.tables[0].columns[0]

    assert column.zero_risk == ZeroRisk.CONTEXT_DEPENDENT
    assert not column.suspicious_zero_values


def test_zero_pressure_is_possible_sentinel(tmp_path):
    path = tmp_path / "pressure.csv"
    pd.DataFrame(
        {
            "Pressure (millibars)": [0] * 2 + list(np.linspace(990, 1030, 198)),
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    column = profile.tables[0].columns[0]

    assert column.zero_risk == ZeroRisk.POSSIBLE_SENTINEL
    assert column.suspicious_zero_values


def test_generic_dataset_report_requires_overview(tmp_path):
    path = tmp_path / "overview.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    plan = fallback_execution_plan(
        "Understand the dataset and report the strongest findings.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    required = set(plan.report_specification.required_components)
    assert ReportComponent.DATASET_OVERVIEW in required
    assert ReportComponent.DATA_QUALITY in required
    assert ReportComponent.STRONGEST_RELATIONSHIPS in required


def test_writer_output_rejects_internal_guardrail_leakage():
    ledger, _ = make_fact_fixture()
    markdown = """
## Global Prohibited Interpretations
- Do not say group membership caused the difference.
"""
    output = WriterOutput(
        title="Leak",
        markdown=markdown,
        sentence_support=[],
        selected_fact_ids=[],
    )

    assert validate_writer_output(output, ledger)


def test_writer_output_rejects_ledger_field_rendering():
    ledger, _ = make_fact_fixture()
    output = WriterOutput(
        title="Leak",
        markdown="Finding: Rain is warmer.\n\nImportant Note: Do not say causal.\n",
        sentence_support=[],
        selected_fact_ids=[],
    )

    assert validate_writer_output(output, ledger)


def test_writer_output_accepts_natural_effect_interpretation():
    ledger, _ = make_fact_fixture()
    sentence = (
        "Rain observations were on average 17.3°C warmer than snow "
        "observations, representing a large difference."
    )
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "fact_summary": sentence,
            "structured_values": {"EVD_0001": {"difference": 17.3}},
            "entities": ["Rain", "snow"],
        }
    )
    ledger = FactLedger(writer_ready_facts=[fact])
    output = WriterOutput(
        title="Natural",
        markdown=f"# Natural\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )

    assert not validate_writer_output(output, ledger)


def test_materialise_writer_output_splits_multi_sentence_draft_text():
    ledger, _ = make_fact_fixture()
    draft = WriterAgentDraft(
        title="Weather summary",
        sections=[
            WriterSectionDraft(
                heading="Dataset overview",
                sentences=[
                    WriterSentenceDraft(
                        text=(
                            "The table contains 96,453 rows. "
                            "The dataset is large."
                        ),
                        fact_ids=["FACT_0001"],
                        support_type=SupportType.PARAPHRASE,
                    )
                ],
            )
        ],
    )

    output = materialise_writer_output(draft, ledger)

    assert [
        support.sentence_text
        for support in output.sentence_support
    ] == [
        "The table contains 96,453 rows.",
        "The dataset is large.",
    ]
    assert output.selected_fact_ids == ["FACT_0001"]
    assert not validate_writer_output(output, ledger)


def test_quality_warning_results_in_approved_with_warnings():
    quality = ReportQualityAssessment(
        status=QualityStatus.WARNING,
        request_responsiveness=0.8,
        finding_selection=0.8,
        coherence=0.9,
        concision=0.9,
        caveat_integration=0.8,
        data_science_interpretation=0.9,
        findings=["The report omits a requested overview."],
    )

    status = decide_release_status(
        annotations=[],
        quality=quality,
        methodological_warnings=[],
        repair_budget_exhausted=False,
        audit_mode=AuditMode.INTERNAL,
    )

    assert status == ReleaseStatus.APPROVED_WITH_WARNINGS


def test_missing_required_component_is_quality_warning_not_human_review():
    ledger, evidence = make_fact_fixture()
    sentence = "The table contains 96,453 rows."
    writer = WriterOutput(
        title="Overview only",
        markdown=f"# Overview only\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    spec = ReportSpecification(
        report_purpose="Describe the data.",
        target_length_words=300,
        maximum_main_findings=5,
        prioritisation_rule="Cover required components.",
        required_components=[
            ReportComponent.DATASET_OVERVIEW,
            ReportComponent.DATA_QUALITY,
        ],
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
    )

    assert audit.quality_assessment.status == QualityStatus.REVISE
    assert audit.release_status == ReleaseStatus.APPROVED_WITH_WARNINGS


def test_imbalance_bias_wording_is_methodological_warning():
    evidence = EvidenceLedger(
        fingerprint="test",
        items=[
            EvidenceItem(
                evidence_id="EVD_0001",
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=["TASK_001"],
                finding="Rain and snow groups have different mean temperatures.",
                metrics={"rain_mean": 12.38, "snow_mean": -4.95},
                source_tables=["weather"],
                source_columns=["Temperature (°C)", "Precip Type"],
                method="Unadjusted group comparison.",
                validation_strategy=ValidationStrategy.NONE,
                practical_interpretation=(
                    "The groups differ descriptively, and unequal group sizes "
                    "may affect precision and stability."
                ),
                strength_label="large_group_difference",
                limitations=[],
                prohibited_interpretations=[],
                recommendations=[],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.COMPARATIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ],
    )
    ledger = FactLedger(
        writer_ready_facts=[
            VerifiedFact(
                fact_id="FACT_0001",
                source_candidate_id="CAN_0001",
                fact_summary=(
                    "Rain and snow groups have different mean temperatures."
                ),
                evidence_ids=["EVD_0001"],
                structured_values={
                    "EVD_0001": {"rain_mean": 12.38, "snow_mean": -4.95}
                },
                entities=["Temperature (°C)", "Precip Type", "rain", "snow"],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.COMPARATIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ]
    )
    sentence = "The imbalanced group sizes may bias the observed means."
    writer = WriterOutput(
        title="Groups",
        markdown=f"# Groups\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    spec = ReportSpecification(
        report_purpose="Describe group differences.",
        target_length_words=200,
        maximum_main_findings=3,
        prioritisation_rule="Use supported comparisons.",
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
    )

    assert any(
        annotation.subtype == "unsupported_methodological_interpretation"
        and annotation.severity == Severity.MEDIUM
        for annotation in audit.annotations
    )
    assert audit.release_status == ReleaseStatus.APPROVED_WITH_WARNINGS


def test_precision_stability_imbalance_wording_is_allowed():
    ledger, evidence = make_fact_fixture()
    sentence = (
        "Unequal group sizes may affect precision and stability of the "
        "observed means."
    )
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "fact_summary": sentence,
            "claim_permissions": [
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
        }
    )
    ledger = FactLedger(writer_ready_facts=[fact])
    writer = WriterOutput(
        title="Groups",
        markdown=f"# Groups\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    spec = ReportSpecification(
        report_purpose="Describe group differences.",
        target_length_words=200,
        maximum_main_findings=3,
        prioritisation_rule="Use supported comparisons.",
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
    )

    assert not [
        annotation
        for annotation in audit.annotations
        if annotation.subtype == "unsupported_methodological_interpretation"
    ]


def test_unresolved_high_factual_error_requires_human_review():
    quality = ReportQualityAssessment(
        status=QualityStatus.PASS,
        request_responsiveness=1.0,
        finding_selection=1.0,
        coherence=1.0,
        concision=1.0,
        caveat_integration=1.0,
        data_science_interpretation=1.0,
    )
    status = decide_release_status(
        annotations=[
            AuditAnnotation(
                annotation_id="ANN_0001",
                sentence="The table has 12 rows.",
                text_span="12",
                error_type=ErrorType.INCORRECT_NUMBER,
                subtype="unsupported_number",
                severity=Severity.HIGH,
                explanation="Wrong number.",
                correction_goal="Use the supported number.",
                confidence=0.95,
            )
        ],
        quality=quality,
        methodological_warnings=[],
        repair_budget_exhausted=True,
        audit_mode=AuditMode.INTERNAL,
    )

    assert status == ReleaseStatus.HUMAN_REVIEW_REQUIRED


def test_targeted_repair_preserves_unflagged_sentences():
    ledger, evidence = make_fact_fixture()
    bad_sentence = "The dataset contains 12 observations."
    good_sentence = "The table contains 96,453 rows."
    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{bad_sentence}\n\n{good_sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=bad_sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            ),
            SentenceSupport(
                sentence_id="SENT_0002",
                sentence_text=good_sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.DIRECT,
            ),
        ],
        selected_fact_ids=["FACT_0001"],
    )
    proposal = AuditRepairProposal(
        annotations=[],
        repairs=[
            SentenceRepair(
                sentence_id="SENT_0001",
                original_sentence=bad_sentence,
                annotation_ids=[],
                candidates=[
                    RepairCandidate(
                        repair_id="REP_001",
                        replacement_text="The dataset contains 96,453 observations.",
                        strategy=RepairStrategy.MINIMAL_CORRECTION,
                        supporting_fact_ids=["FACT_0001"],
                        supporting_evidence_ids=["EVD_0001"],
                        factual_support_score=1.0,
                        meaning_preservation_score=1.0,
                        readability_score=1.0,
                        residual_hallucination_risk=0.0,
                    )
                ],
                preferred_repair_id="REP_001",
                selection_reason="Correct the number.",
            )
        ],
        recommended_decision=AuditDecision.REVISE,
        residual_risk="Repair required.",
        quality_assessment=ReportQualityAssessment(
            status=QualityStatus.PASS,
            request_responsiveness=1.0,
            finding_selection=1.0,
            coherence=1.0,
            concision=1.0,
            caveat_integration=1.0,
            data_science_interpretation=1.0,
        ),
    )

    repaired, _ = apply_repair_proposal(writer, proposal, ledger, evidence)

    assert good_sentence in repaired.markdown


def test_deterministic_writer_fallback_is_not_primary_evaluation():
    ledger, evidence = make_fact_fixture()
    understanding = DataUnderstanding(
        profile_fingerprint="test",
        dataset_summary="Test.",
        tables=[],
    )
    plan = ExecutionPlan(
        objective="Describe the data.",
        tasks=[],
        route_order=[],
        report_specification=ReportSpecification(
            report_purpose="Describe the data.",
            target_length_words=300,
            maximum_main_findings=5,
            prioritisation_rule="Use verified facts.",
            required_components=[ReportComponent.DATASET_OVERVIEW],
        ),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=10,
        rationale="Test plan.",
    )
    pack = build_writer_evidence_pack(
        request="Describe the data.",
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
    )

    output = fallback_writer(pack)

    assert output.writer_mode == "deterministic_fallback"
    assert not output.eligible_for_primary_evaluation
# ============================================================
# REPORT-COVERAGE REGRESSION TESTS
# ============================================================


def _coverage_evidence_item(
    *,
    evidence_id,
    finding,
    route,
    metrics,
    strength_label,
    recommended_use,
    permissions,
    relevance=0.95,
    salience=0.95,
):
    return EvidenceItem(
        evidence_id=evidence_id,
        route=route,
        task_ids=["TASK_COVERAGE"],
        finding=finding,
        metrics=metrics,
        source_tables=["weather"],
        source_columns=list(
            metrics.get(
                "source_columns",
                [],
            )
        ),
        method="Deterministic test evidence.",
        validation_strategy=ValidationStrategy.NONE,
        practical_interpretation=finding,
        strength_label=strength_label,
        limitations=[],
        prohibited_interpretations=[],
        recommendations=[],
        claim_permissions=permissions,
        factual_confidence=1.0,
        methodological_strength=0.95,
        user_relevance=relevance,
        salience=salience,
        recommended_use=recommended_use,
        eligible_for_writer=True,
    )


def _coverage_fact(
    item,
    fact_id,
):
    return VerifiedFact(
        fact_id=fact_id,
        source_candidate_id=(
            f"CAN_{fact_id}"
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=[
            "weather",
            *item.source_columns,
        ],
        claim_permissions=(
            item.claim_permissions
        ),
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )


def _coverage_fixture():
    overview = _coverage_evidence_item(
        evidence_id="EVD_COV_001",
        finding=(
            "Table `weather` contains 96,453 "
            "rows and 12 columns."
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        metrics={
            "row_count": 96_453,
            "column_count": 12,
        },
        strength_label="dataset_overview",
        recommended_use=RecommendedUse.HEADLINE,
        permissions=[
            ClaimPermission.DESCRIPTIVE
        ],
    )

    quality = _coverage_evidence_item(
        evidence_id="EVD_COV_002",
        finding=(
            "`Loud Cover` is constant at `0` "
            "across all observations."
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        metrics={
            "constant": True,
            "constant_value": 0,
        },
        strength_label="constant_column",
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.DESCRIPTIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    correlation = _coverage_evidence_item(
        evidence_id="EVD_COV_003",
        finding=(
            "`Temperature (C)` and "
            "`Apparent Temperature (C)` have "
            "a Pearson correlation of 0.9926."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "pearson_r": 0.9926,
            "complete_pairs": 96_453,
        },
        strength_label=(
            "very_strong_association"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.ASSOCIATIONAL,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    large_group = _coverage_evidence_item(
        evidence_id="EVD_COV_004",
        finding=(
            "Rain observations have a mean "
            "temperature of 12.36 compared with "
            "-4.97 for snow, a difference of "
            "17.33."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "highest_group": {
                "group": "rain",
                "mean": 12.36,
            },
            "lowest_group": {
                "group": "snow",
                "mean": -4.97,
            },
            "difference": 17.33,
            "standardised_difference": 1.0,
        },
        strength_label=(
            "large_group_difference"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.COMPARATIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    small_group = _coverage_evidence_item(
        evidence_id="EVD_COV_005",
        finding=(
            "Rain observations have a mean wind "
            "speed of 10.97 compared with 9.482 "
            "for snow, a difference of 1.489."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "highest_group": {
                "group": "rain",
                "mean": 10.97,
            },
            "lowest_group": {
                "group": "snow",
                "mean": 9.482,
            },
            "difference": 1.489,
            "standardised_difference": 0.22,
        },
        strength_label=(
            "small_group_difference"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.COMPARATIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
        relevance=0.80,
        salience=0.75,
    )

    evidence = EvidenceLedger(
        fingerprint="coverage-test",
        items=[
            overview,
            quality,
            correlation,
            large_group,
            small_group,
        ],
    )

    facts = {
        item.evidence_id: _coverage_fact(
            item,
            f"FACT_COV_{index:03d}",
        )
        for index, item in enumerate(
            evidence.items,
            start=1,
        )
    }

    return evidence, facts


def test_report_coverage_recovery_regression():
    from table2text.audit import (
        augment_fact_ledger_for_report_coverage,
    )
    from table2text.schemas import (
        VerificationMethod,
    )

    evidence, facts = _coverage_fixture()

    thin_ledger = FactLedger(
        writer_ready_facts=[
            facts["EVD_COV_005"]
        ]
    )

    recovered = (
        augment_fact_ledger_for_report_coverage(
            fact_ledger=thin_ledger,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            settings=Settings(),
        )
    )

    assert (
        len(recovered.writer_ready_facts)
        > len(thin_ledger.writer_ready_facts)
    )

    assert (
        recovered
        .deterministically_recovered_fact_ids
    )

    recovered_facts = [
        fact
        for fact in recovered.writer_ready_facts
        if fact.fact_id
        in recovered
        .deterministically_recovered_fact_ids
    ]

    assert recovered_facts

    assert all(
        fact.verification_method
        == VerificationMethod
        .DETERMINISTIC_EVIDENCE_RECOVERY
        for fact in recovered_facts
    )

    represented = {
        evidence_id
        for fact in recovered.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }

    assert "EVD_COV_001" in represented
    assert "EVD_COV_002" in represented
    assert "EVD_COV_003" in represented
    assert "EVD_COV_004" in represented


def test_priority_selection_never_refills_with_small_effect():
    from table2text.audit import (
        select_balanced_priority_facts,
    )

    evidence, facts = _coverage_fixture()

    ledger = FactLedger(
        writer_ready_facts=list(
            facts.values()
        )
    )

    selected = (
        select_balanced_priority_facts(
            facts=ledger.writer_ready_facts,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
            ],
            settings=Settings(),
        )
    )

    selected_evidence_ids = {
        evidence_id
        for fact in selected
        for evidence_id in fact.evidence_ids
    }

    assert "EVD_COV_001" in selected_evidence_ids
    assert "EVD_COV_002" in selected_evidence_ids
    assert "EVD_COV_003" in selected_evidence_ids
    assert "EVD_COV_004" in selected_evidence_ids
    assert "EVD_COV_005" not in selected_evidence_ids


def test_minimum_report_words_never_exceeds_target():
    from table2text.audit import (
        minimum_useful_report_words,
    )

    minimum = minimum_useful_report_words(
        target_words=150,
        required_component_count=4,
        settings=Settings(),
    )

    assert minimum <= 150
    assert minimum > 0


def test_recovered_balanced_fallback_is_not_two_sentence_report():
    from table2text.audit import (
        augment_fact_ledger_for_report_coverage,
    )

    evidence, facts = _coverage_fixture()

    thin_ledger = FactLedger(
        writer_ready_facts=[
            facts["EVD_COV_005"]
        ]
    )

    ledger = (
        augment_fact_ledger_for_report_coverage(
            fact_ledger=thin_ledger,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            settings=Settings(),
        )
    )

    understanding = DataUnderstanding(
        profile_fingerprint="coverage-test",
        dataset_summary=(
            "Weather observations."
        ),
        tables=[],
    )

    plan = ExecutionPlan(
        objective=(
            "Understand the weather dataset and "
            "report its strongest findings."
        ),
        tasks=[],
        route_order=[],
        report_specification=ReportSpecification(
            report_purpose=(
                "Understand the weather dataset."
            ),
            target_length_words=300,
            maximum_main_findings=8,
            prioritisation_rule=(
                "Cover required components using "
                "the strongest evidence."
            ),
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
        ),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=20,
        rationale="Regression test.",
    )

    pack = build_writer_evidence_pack(
        request=plan.objective,
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
    )

    output = fallback_writer(pack)

    assert "## Dataset overview" in output.markdown
    assert "## Data quality" in output.markdown
    assert (
        "## Strongest observed relationships"
        in output.markdown
    )
    assert "1.489" not in output.markdown
    assert len(output.sentence_support) >= 4
    assert (
        output.writer_mode
        == "deterministic_fallback"
    )
    assert not output.eligible_for_primary_evaluation


# ============================================================
# PROFILE-SUPPORT AND AUDIT-AUTHORITY REGRESSION TESTS
# ============================================================


def _profile_authority_fixture() -> DataProfile:
    return DataProfile(
        fingerprint="profile-authority",
        source_paths=["memory.csv"],
        tables=[
            TableProfile(
                table_name="weather",
                source_path="memory.csv",
                row_count=4,
                column_count=4,
                duplicate_row_count=1,
                candidate_keys=["Timestamp"],
                columns=[
                    ColumnProfile(
                        name="Timestamp",
                        dtype="object",
                        semantic_type="datetime",
                        missing_count=0,
                        missing_rate=0.0,
                        unique_count=4,
                        sample_values=[
                            "2020-01-01 00:00",
                            "2020-01-01 01:00",
                        ],
                        datetime_parse_rate=1.0,
                        candidate_key=True,
                    ),
                    ColumnProfile(
                        name="Constant",
                        dtype="int64",
                        semantic_type="numeric",
                        missing_count=0,
                        missing_rate=0.0,
                        unique_count=1,
                        sample_values=["0"],
                        numeric_summary={
                            "count": 4,
                            "mean": 0.0,
                            "minimum": 0.0,
                            "maximum": 0.0,
                        },
                        constant=True,
                    ),
                    ColumnProfile(
                        name="Pressure",
                        dtype="float64",
                        semantic_type="numeric",
                        missing_count=0,
                        missing_rate=0.0,
                        unique_count=3,
                        numeric_summary={
                            "count": 4,
                            "mean": 750.0,
                            "median": 1000.0,
                            "minimum": 0.0,
                            "maximum": 1010.0,
                            "zero_count": 1,
                            "zero_rate": 0.25,
                        },
                        suspicious_zero_values=True,
                        possible_sentinel_values=True,
                        zero_risk=ZeroRisk.POSSIBLE_SENTINEL,
                        zero_risk_reason=(
                            "Zero is separated from positive pressure values."
                        ),
                    ),
                    ColumnProfile(
                        name="Precip Type",
                        dtype="object",
                        semantic_type="categorical",
                        missing_count=1,
                        missing_rate=0.25,
                        unique_count=2,
                    ),
                ],
            )
        ],
    )


def _basic_spec() -> ReportSpecification:
    return ReportSpecification(
        report_purpose="Understand the dataset.",
        target_length_words=300,
        maximum_main_findings=5,
        prioritisation_rule="Use supported facts.",
    )


def _audit_sentence(
    sentence: str,
    *,
    support: SentenceSupport | None = None,
    profile_records=None,
    ledger: FactLedger | None = None,
    evidence: EvidenceLedger | None = None,
):
    ledger = ledger or make_fact_fixture()[0]
    evidence = evidence or make_fact_fixture()[1]
    support = support or SentenceSupport(
        sentence_id="SENT_0001",
        sentence_text=sentence,
        fact_ids=["FACT_0001"],
        evidence_ids=["EVD_0001"],
        support_type=SupportType.PARAPHRASE,
    )
    output = WriterOutput(
        title="Audit",
        markdown=f"# Audit\n\n{sentence}\n",
        sentence_support=[support],
        selected_fact_ids=support.fact_ids,
    )
    return deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        profile_support_records=profile_records or [],
    ), output


def test_profile_support_registry_contains_structural_records():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    by_kind = {record.fact_kind for record in records}

    assert "table_dimensions" in by_kind
    assert "duplicate_rows" in by_kind
    assert "constant_column" in by_kind
    assert "column_missingness" in by_kind
    assert "numeric_summary" in by_kind
    assert "zero_diagnostic" in by_kind
    assert "datetime_presence" in by_kind
    assert "candidate_key" in by_kind


def test_execute_plan_emits_duplicate_row_evidence(tmp_path):
    path = tmp_path / "dupes.csv"
    pd.DataFrame(
        {
            "a": [1, 1, 2],
            "b": ["x", "x", "y"],
        }
    ).to_csv(path, index=False)
    bundle = load_data([path])
    plan = ExecutionPlan(
        objective="Describe duplicates.",
        tasks=[
            InvestigationTask(
                task_id="TASK_DUP",
                question="Check duplicate rows.",
                route=AnalysisRoute.DESCRIPTIVE,
                priority=1,
                table_name="dupes",
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE
                ],
                answerability_note="Deterministic profile.",
            )
        ],
        route_order=[AnalysisRoute.DESCRIPTIVE],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=20,
        rationale="Test.",
    )

    evidence = execute_plan(bundle, plan, Settings())
    duplicate_items = [
        item
        for item in evidence.items
        if item.strength_label == "duplicate_rows"
    ]

    assert len(duplicate_items) == 1
    assert (
        duplicate_items[0]
        .metrics["duplicate_row_count"]
        == 1
    )


def test_profile_supported_unmapped_number_creates_hidden_patch():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    sentence = "The dataset contains 1 exact duplicate row."
    audit, output = _audit_sentence(
        sentence,
        profile_records=records,
    )

    assert any(
        annotation.error_type
        == ErrorType.SUPPORT_MAPPING_ERROR
        and annotation.severity == Severity.MEDIUM
        for annotation in audit.annotations
    )
    assert not any(
        annotation.subtype == "unsupported_number"
        and annotation.severity == Severity.HIGH
        for annotation in audit.annotations
    )
    assert audit.support_map_patches

    patched = apply_support_map_patches(
        output,
        audit.support_map_patches,
        {record.support_id for record in records},
    )

    assert patched.markdown == output.markdown
    assert (
        patched.sentence_support[0].sentence_text
        == sentence
    )
    assert patched.sentence_support[0].profile_support_ids

    post_audit = deterministic_audit(
        patched,
        make_fact_fixture()[0],
        make_fact_fixture()[1],
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        profile_support_records=records,
    )

    assert not any(
        annotation.error_type
        == ErrorType.SUPPORT_MAPPING_ERROR
        for annotation in post_audit.annotations
    )


def test_wrong_profile_number_remains_high_error():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    audit, _ = _audit_sentence(
        "The dataset contains 2 exact duplicate rows.",
        profile_records=records,
    )

    assert not audit.support_map_patches
    assert any(
        annotation.subtype == "unsupported_number"
        and annotation.severity == Severity.HIGH
        for annotation in audit.annotations
    )


def test_data_understanding_is_not_factual_authority_for_metadata():
    audit, _ = _audit_sentence(
        "The dataset contains hourly observations at a specific location."
    )

    subtypes = {
        annotation.subtype
        for annotation in audit.annotations
    }
    assert "unsupported_temporal_cadence" in subtypes
    assert "unsupported_location_metadata" in subtypes


def test_datetime_parse_rate_does_not_prove_hourly_cadence():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    audit, _ = _audit_sentence(
        "The dataset contains hourly observations.",
        profile_records=records,
    )

    assert any(
        annotation.subtype
        == "unsupported_temporal_cadence"
        for annotation in audit.annotations
    )


def test_wording_guardrails_for_constant_zero_missing_duplicate_and_pearson():
    examples = {
        "The Constant column provides no analytical value.": (
            "overbroad_constant_interpretation"
        ),
        "Pressure zeros likely represents encoded missingness.": (
            "overconfident_zero_interpretation"
        ),
        "The missingness is unlikely to cause major issues.": (
            "unsupported_missingness_impact"
        ),
        "Duplicate rows should likely be removed.": (
            "unsupported_duplicate_removal"
        ),
        "Pearson correlation may be influenced by non-linear patterns.": (
            "imprecise_pearson_limitation"
        ),
    }

    for sentence, subtype in examples.items():
        audit, _ = _audit_sentence(sentence)
        assert any(
            annotation.subtype == subtype
            for annotation in audit.annotations
        )


def test_safe_profile_supported_wording_is_allowed_after_hidden_patch():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    constant_id = next(
        record.support_id
        for record in records
        if record.fact_kind == "constant_column"
    )
    sentence = (
        "The Constant column contains no observed variation for analyses "
        "that depend on variation."
    )
    support = SentenceSupport(
        sentence_id="SENT_0001",
        sentence_text=sentence,
        fact_ids=[],
        evidence_ids=[],
        profile_support_ids=[constant_id],
        support_type=SupportType.PARAPHRASE,
    )
    audit, _ = _audit_sentence(
        sentence,
        support=support,
        profile_records=records,
    )

    assert not audit.annotations


def test_unsupported_and_supported_future_recommendations():
    unsupported, _ = _audit_sentence(
        "Future work should explore temporal trends."
    )
    assert any(
        annotation.subtype
        == "unsupported_analytical_recommendation"
        for annotation in unsupported.annotations
    )

    evidence = EvidenceLedger(
        fingerprint="recommendation",
        items=[
            EvidenceItem(
                evidence_id="EVD_REC",
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=["TASK_REC"],
                finding="The table contains 4 rows.",
                metrics={"row_count": 4},
                source_tables=["weather"],
                source_columns=[],
                method="Direct count.",
                validation_strategy=ValidationStrategy.NONE,
                practical_interpretation="Small table.",
                strength_label="dataset_overview",
                limitations=[],
                prohibited_interpretations=[],
                recommendations=[
                    AnalyticalRecommendation(
                        recommendation_id="REC_TEMPORAL",
                        action=(
                            "Future work should explore temporal trends."
                        ),
                        recommendation_type="additional_analysis",
                        priority="low",
                        justification=(
                            "The source includes a timestamp field."
                        ),
                    )
                ],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.8,
                salience=0.7,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )
        ],
    )
    ledger = FactLedger(
        writer_ready_facts=[
            VerifiedFact(
                fact_id="FACT_REC",
                source_candidate_id="CAN_REC",
                fact_summary="The table contains 4 rows.",
                evidence_ids=["EVD_REC"],
                structured_values={
                    "EVD_REC": {"row_count": 4}
                },
                entities=["weather"],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.8,
                salience=0.7,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )
        ]
    )
    sentence = "Future work should explore temporal trends."
    support = SentenceSupport(
        sentence_id="SENT_0001",
        sentence_text=sentence,
        fact_ids=["FACT_REC"],
        evidence_ids=["EVD_REC"],
        support_type=SupportType.PARAPHRASE,
    )
    supported, _ = _audit_sentence(
        sentence,
        support=support,
        ledger=ledger,
        evidence=evidence,
    )

    assert not any(
        annotation.subtype
        == "unsupported_analytical_recommendation"
        for annotation in supported.annotations
    )


def test_quality_finding_validation_and_conservative_merge():
    assert not valid_quality_finding(
        "The dataset contains 24 duplicate rows."
    )
    assert valid_quality_finding(
        "The report recommends duplicate removal without sufficient justification."
    )

    deterministic = ReportQualityAssessment(
        status=QualityStatus.REVISE,
        request_responsiveness=0.9,
        finding_selection=0.8,
        coherence=0.7,
        concision=0.8,
        caveat_integration=0.9,
        data_science_interpretation=0.8,
        findings=["The report omits a required limitation."],
        recommendations=["Add the missing limitation."],
    )
    semantic = ReportQualityAssessment(
        status=QualityStatus.PASS,
        request_responsiveness=1.0,
        finding_selection=0.6,
        coherence=0.9,
        concision=0.9,
        caveat_integration=1.0,
        data_science_interpretation=0.9,
        findings=["The report repeats closely related findings."],
        recommendations=["Consolidate repeated findings."],
    )

    merged = merge_quality_assessments(
        deterministic,
        semantic,
    )

    assert merged.status == QualityStatus.REVISE
    assert "The report omits a required limitation." in merged.findings
    assert "The report repeats closely related findings." in merged.findings
    assert merged.finding_selection == 0.6


def test_writer_payload_removes_data_understanding_factual_prose():
    ledger, evidence = make_fact_fixture()
    understanding = DataUnderstanding(
        profile_fingerprint="payload",
        dataset_summary=(
            "The data are hourly and collected at a specific location."
        ),
        tables=[
            TableUnderstanding(
                table_name="weather",
                unit_of_observation="hourly weather station measurement",
                summary="Location-specific hourly weather station data.",
            )
        ],
    )
    plan = ExecutionPlan(
        objective="Understand the data.",
        tasks=[],
        route_order=[],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=20,
        rationale="Test.",
    )
    pack = build_writer_evidence_pack(
        request=plan.objective,
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
    )

    payload = build_compact_writer_payload(pack)

    assert "dataset_summary" not in payload
    assert "table_context" not in payload
    assert payload["priority_facts"]
    assert "analytical_recommendations" in payload
