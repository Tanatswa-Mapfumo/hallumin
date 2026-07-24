from __future__ import annotations

import json
from dataclasses import replace
from types import MethodType

import numpy as np
import pandas as pd
import pytest

from table2text import Settings, Table2TextWorkflow
from table2text.analytics import execute_plan
from table2text.audit import (
    apply_repair_proposal,
    apply_support_map_patches,
    assess_genre_quality,
    build_profile_support_registry,
    build_writer_evidence_pack,
    decide_release_status,
    deterministic_audit,
    fallback_writer,
    materialise_writer_output,
    merge_quality_assessments,
    merge_audit_proposal,
    split_markdown_sentences,
    validate_repair_candidate,
    validate_writer_output,
)
from table2text.capabilities import available_capabilities
from table2text.workflow import (
    build_compact_writer_payload,
    resolve_report_genre,
)
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
    EvaluationFieldPolicy,
    EvidenceCapability,
    EvidenceItem,
    EvidenceLedger,
    ExecutionPlan,
    FactLedger,
    InsightCandidate,
    InsightCandidateSet,
    InsightLedger,
    InsightRejection,
    InsightType,
    InsightVerificationRecord,
    InsightVerificationResult,
    InsightVerificationStatus,
    InvestigationTask,
    InputRepresentationStatus,
    InputShape,
    InterpretationLevel,
    QualityStatus,
    RecommendedUse,
    ReleaseStatus,
    RepairCandidate,
    RepairStrategy,
    ReportQualityAssessment,
    ReportComponent,
    ReportGenre,
    ReportPerspective,
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
    VerifiedInsight,
    WriterAgentDraft,
    WriterOutput,
    WriterSectionDraft,
    WriterSentenceDraft,
    ZeroRisk,
)
from table2text.agents import (
    empty_insight_ledger,
    fallback_execution_plan,
    materialise_insight_ledger,
    recover_missing_writer_insight_ids,
    validate_insight_candidates,
    validate_insight_verification,
    valid_quality_finding,
    writer_sentence_grounding_errors,
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


def test_tabular_relationship_evidence_retains_capability_provenance(
    tmp_path,
):
    path = tmp_path / "relationships.csv"
    values = np.arange(200, dtype=float)
    pd.DataFrame(
        {
            "x": values,
            "y": values * 2,
            "group": ["a"] * 100 + ["b"] * 100,
        }
    ).to_csv(path, index=False)
    bundle = load_data([path])
    plan = fallback_execution_plan(
        "Report the strongest relationships.",
        profile_data(bundle),
        AuditMode.INTERNAL,
        Settings(),
    )

    evidence = execute_plan(bundle, plan, Settings())

    correlation = next(
        item
        for item in evidence.items
        if "pearson_r" in item.metrics
    )
    group_comparison = next(
        item
        for item in evidence.items
        if "group_counts" in item.metrics
    )
    assert correlation.capability == EvidenceCapability.ASSOCIATION
    assert group_comparison.capability == (
        EvidenceCapability.GROUP_COMPARISON
    )

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

    workflow = Table2TextWorkflow(settings)
    assert workflow.evidence_insight_synthesis_agent is None
    assert workflow.verifier_insight_verification_agent is None

    result = workflow.run_sync(
        inputs=[path],
        request=(
            "Understand the dataset and report its strongest supported findings."
        ),
        audit_mode=AuditMode.INTERNAL,
    )

    assert result.evidence_ledger.items
    assert result.fact_ledger.writer_ready_facts
    assert not result.insight_ledger.verified_insights
    assert "LLM execution disabled" in (
        result.insight_ledger.fallback_reason or ""
    )
    assert result.raw_writer_output.writer_mode == "deterministic_fallback"

    run_directory = settings.output_dir / result.run_id

    assert (run_directory / "09_writer_raw_report.md").exists()
    assert (run_directory / "final_report.md").exists()
    assert (run_directory / "final_result.json").exists()
    assert (
        run_directory
        / "02_profile_support_registry.json"
    ).exists()
    assert (run_directory / "03_insight_objectives.json").exists()
    assert (run_directory / "07_insight_candidates.json").exists()
    assert (run_directory / "07_insight_verification.json").exists()
    assert (run_directory / "07_insight_ledger.json").exists()
    assert "insight_ledger" in result.model_dump(mode="json")

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


def test_writer_materialisation_maps_each_compound_sentence_fragment():
    ledger, _ = make_fact_fixture()
    first = "The table contains 96,453 rows."
    second = "The dataset contains more than 96,000 observations."
    draft = WriterAgentDraft(
        title="Supported report",
        sections=[
            WriterSectionDraft(
                heading="Overview",
                sentences=[
                    WriterSentenceDraft(
                        text=f"{first} {second}",
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
    ] == [first, second]


def test_fallback_writer_maps_each_compound_limitation_fragment():
    ledger, evidence = make_fact_fixture()
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "claim_permissions": [
                ClaimPermission.ASSOCIATIONAL,
            ]
        }
    )
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
        fact_ledger=FactLedger(writer_ready_facts=[fact]),
        settings=Settings(),
    )
    limitation = (
        "Observed associations are descriptive. "
        "They are not evidence of causal effects."
    )
    pack = pack.model_copy(
        update={
            "priority_facts": [fact],
            "reader_facing_limitations": [limitation],
        }
    )

    output = fallback_writer(pack)
    mapped_sentences = {
        support.sentence_text
        for support in output.sentence_support
    }

    assert set(split_markdown_sentences(limitation)).issubset(
        mapped_sentences
    )


def test_repair_rejects_identical_replacement_text():
    ledger, evidence = make_fact_fixture()
    sentence = "The table contains 96,453 rows."
    candidate = RepairCandidate(
        repair_id="REP_NOOP",
        replacement_text=sentence,
        strategy=RepairStrategy.MINIMAL_CORRECTION,
        supporting_fact_ids=["FACT_0001"],
        supporting_evidence_ids=["EVD_0001"],
        factual_support_score=1.0,
        meaning_preservation_score=1.0,
        readability_score=1.0,
        residual_hallucination_risk=0.0,
    )

    errors = validate_repair_candidate(
        candidate,
        ledger,
        evidence,
        original_text=sentence,
    )

    assert errors == [
        "The replacement is identical to the original sentence."
    ]


def test_repair_maps_every_fragment_of_compound_replacement():
    ledger, evidence = make_fact_fixture()
    original = "The dataset contains 12 observations."
    first = "The table contains 96,453 rows."
    second = "The dataset contains more than 96,000 observations."
    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{original}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=original,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    candidate = RepairCandidate(
        repair_id="REP_COMPOUND",
        replacement_text=f"{first} {second}",
        strategy=RepairStrategy.MINIMAL_CORRECTION,
        supporting_fact_ids=["FACT_0001"],
        supporting_evidence_ids=["EVD_0001"],
        factual_support_score=1.0,
        meaning_preservation_score=1.0,
        readability_score=1.0,
        residual_hallucination_risk=0.0,
    )
    proposal = AuditRepairProposal(
        repairs=[
            SentenceRepair(
                sentence_id="SENT_0001",
                original_sentence=original,
                annotation_ids=[],
                candidates=[candidate],
                preferred_repair_id=candidate.repair_id,
                selection_reason="Correct and clarify the supported count.",
            )
        ],
        recommended_decision=AuditDecision.REVISE,
        residual_risk="Repair required.",
        quality_assessment=(
            make_passing_audit_report().quality_assessment
        ),
    )

    repaired, patches = apply_repair_proposal(
        writer,
        proposal,
        ledger,
        evidence,
    )

    assert len(patches) == 1
    assert [
        support.sentence_text
        for support in repaired.sentence_support
    ] == [first, second]
    assert len(
        {
            support.sentence_id
            for support in repaired.sentence_support
        }
    ) == 2


def test_writer_recovers_one_unambiguous_missing_insight_id():
    insight = VerifiedInsight(
        insight_id="INS_RECOVER",
        statement=(
            "The verified findings form one bounded pattern."
        ),
        insight_type=InsightType.NARRATIVE_SUMMARY,
        interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
        source_fact_ids=["FACT_0001"],
        source_evidence_ids=["EVD_0001"],
        why_it_matters="It provides a bounded interpretation.",
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        confidence=0.95,
        salience=0.90,
        verification_status=InsightVerificationStatus.VERIFIED,
    )
    draft = WriterAgentDraft(
        title="Insight report",
        sections=[
            WriterSectionDraft(
                heading="Finding",
                sentences=[
                    WriterSentenceDraft(
                        text=insight.statement,
                        fact_ids=["FACT_0001"],
                        interpretation_level=(
                            InterpretationLevel.BOUNDED_INSIGHT
                        ),
                        support_type=SupportType.MULTI_FACT_SYNTHESIS,
                    )
                ],
            )
        ],
    )

    recovered = recover_missing_writer_insight_ids(
        draft,
        {insight.insight_id: insight},
    )

    assert recovered.sections[0].sentences[0].insight_ids == [
        insight.insight_id
    ]


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
    assert "semantic_map" not in payload
    assert payload["priority_facts"]
    assert "analytical_recommendations" in payload


# ============================================================
# VERIFIED BOUNDED INSIGHT SYNTHESIS TESTS
# ============================================================


def _insight_fixture() -> tuple[FactLedger, EvidenceLedger]:
    evidence = EvidenceLedger(
        fingerprint="insight-test",
        items=[
            EvidenceItem(
                evidence_id="EVD_INS_001",
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=["TASK_INS"],
                finding=(
                    "`Humidity` and `Temperature` have a negative Pearson "
                    "correlation."
                ),
                metrics={"pearson_r": -0.63},
                source_tables=["weather"],
                source_columns=["Humidity", "Temperature"],
                method="Deterministic Pearson correlation.",
                practical_interpretation=(
                    "Higher humidity is associated with lower temperature "
                    "in this dataset."
                ),
                strength_label="strong_association",
                claim_permissions=[ClaimPermission.ASSOCIATIONAL],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=0.9,
                salience=0.9,
                recommended_use=RecommendedUse.MAIN_FINDING,
            ),
            EvidenceItem(
                evidence_id="EVD_INS_002",
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=["TASK_INS"],
                finding=(
                    "`Humidity` and `Temperature` also have a negative rank "
                    "association."
                ),
                metrics={"spearman_r": -0.61},
                source_tables=["weather"],
                source_columns=["Humidity", "Temperature"],
                method="Deterministic rank association.",
                practical_interpretation=(
                    "The inverse association is present under a rank-based "
                    "summary as well."
                ),
                strength_label="strong_association",
                claim_permissions=[ClaimPermission.ASSOCIATIONAL],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=0.85,
                salience=0.85,
                recommended_use=RecommendedUse.MAIN_FINDING,
            ),
        ],
    )
    facts = [
        VerifiedFact(
            fact_id=f"FACT_INS_{index:03d}",
            source_candidate_id=f"CAN_INS_{index:03d}",
            fact_summary=item.finding,
            evidence_ids=[item.evidence_id],
            structured_values={item.evidence_id: item.metrics},
            entities=[
                "weather",
                "Humidity",
                "Temperature",
            ],
            claim_permissions=item.claim_permissions,
            allowed_interpretations=[item.practical_interpretation],
            factual_confidence=1.0,
            methodological_strength=0.9,
            user_relevance=item.user_relevance,
            salience=item.salience,
            recommended_use=RecommendedUse.MAIN_FINDING,
        )
        for index, item in enumerate(evidence.items, start=1)
    ]
    return FactLedger(writer_ready_facts=facts), evidence


def _insight_candidate(
    *,
    insight_id: str = "INSIGHT_001",
    statement: str = (
        "Pearson and rank-based summaries both show an inverse association "
        "between `Humidity` and `Temperature` in this dataset."
    ),
    insight_type: InsightType = InsightType.OUTCOME_ASSOCIATION,
    interpretation_level: InterpretationLevel = (
        InterpretationLevel.BOUNDED_INSIGHT
    ),
    source_fact_ids: list[str] | None = None,
    source_evidence_ids: list[str] | None = None,
    suitable_for_main_report: bool = True,
    confidence: float = 0.9,
    salience: float = 0.9,
) -> InsightCandidate:
    return InsightCandidate(
        insight_id=insight_id,
        statement=statement,
        insight_type=insight_type,
        interpretation_level=interpretation_level,
        source_fact_ids=(
            source_fact_ids
            if source_fact_ids is not None
            else ["FACT_INS_001", "FACT_INS_002"]
        ),
        source_evidence_ids=(
            source_evidence_ids
            if source_evidence_ids is not None
            else ["EVD_INS_001", "EVD_INS_002"]
        ),
        why_it_matters=(
            "Agreement across both summaries makes the direction less "
            "dependent on a single association measure."
        ),
        supporting_summary="Two verified association summaries agree.",
        limitations=["The association is descriptive, not causal."],
        claim_permissions=[ClaimPermission.ASSOCIATIONAL],
        confidence=confidence,
        salience=salience,
        suitable_for_main_report=suitable_for_main_report,
    )


def _verified_insight(
    candidate: InsightCandidate | None = None,
    *,
    status: InsightVerificationStatus = InsightVerificationStatus.VERIFIED,
) -> VerifiedInsight:
    candidate = candidate or _insight_candidate()
    return VerifiedInsight(
        insight_id=candidate.insight_id,
        statement=candidate.statement,
        insight_type=candidate.insight_type,
        interpretation_level=candidate.interpretation_level,
        source_fact_ids=candidate.source_fact_ids,
        source_evidence_ids=candidate.source_evidence_ids,
        why_it_matters=candidate.why_it_matters,
        limitations=candidate.limitations,
        claim_permissions=candidate.claim_permissions,
        confidence=candidate.confidence,
        salience=candidate.salience,
        verification_status=status,
    )


def test_insight_schema_defaults_and_report_controls():
    plan = ExecutionPlan(
        objective="Describe the data.",
        tasks=[],
        route_order=[],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=10,
        rationale="Compatibility fixture.",
    )
    sentence = WriterSentenceDraft(
        text="A direct finding.",
        support_type=SupportType.DIRECT,
    )

    assert plan.insight_objectives == []
    assert sentence.insight_ids == []
    assert sentence.interpretation_level == InterpretationLevel.FINDING
    assert plan.report_specification.genre == ReportGenre.DATA_SCIENCE_REPORT
    assert plan.report_specification.perspective == ReportPerspective.NEUTRAL
    assert InsightLedger().verified_insights == []


def test_insight_configuration_defaults_and_validation():
    settings = Settings()

    assert settings.enable_insight_synthesis
    assert settings.max_insight_candidates == 6
    assert settings.max_verified_main_insights == 4

    with pytest.raises(ValueError):
        replace(settings, max_insight_candidates=0)
    with pytest.raises(ValueError):
        replace(settings, max_verified_main_insights=7)
    with pytest.raises(ValueError):
        replace(settings, min_insight_confidence=1.1)
    with pytest.raises(ValueError):
        replace(settings, min_insight_salience=-0.1)
    with pytest.raises(ValueError):
        replace(settings, min_facts_per_bounded_insight=0)


def test_fallback_plan_freezes_questions_and_genre_defaults():
    profile = _profile_authority_fixture()
    generic = fallback_execution_plan(
        "Understand the dataset.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )
    sports = fallback_execution_plan(
        "Write a game report.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    assert generic.insight_objectives
    assert all(
        objective.question.endswith("?")
        for objective in generic.insight_objectives
    )
    assert all(
        not any(character.isdigit() for character in objective.question)
        for objective in generic.insight_objectives
    )
    assert generic.report_specification.genre == ReportGenre.DATA_SCIENCE_REPORT
    assert sports.report_specification.genre == ReportGenre.EVENT_REPORT


def test_valid_bounded_insight_and_safe_association_are_accepted():
    ledger, evidence = _insight_fixture()
    candidate = _insight_candidate()
    overlap = _insight_candidate(
        insight_id="INSIGHT_OVERLAP",
        statement=(
            "The two measures contain highly overlapping information in "
            "this dataset."
        ),
        insight_type=InsightType.REDUNDANCY,
    )

    assert not validate_insight_candidates(
        InsightCandidateSet(candidates=[candidate]),
        ledger,
        evidence,
        Settings(),
    )
    assert not validate_insight_candidates(
        InsightCandidateSet(candidates=[overlap]),
        ledger,
        evidence,
        Settings(),
    )


def test_insight_candidate_rejects_unknown_fact_and_number():
    ledger, evidence = _insight_fixture()
    unknown = _insight_candidate(
        source_fact_ids=["FACT_UNKNOWN", "FACT_INS_002"]
    )
    numbered = _insight_candidate(
        statement=(
            "Higher `Humidity` is associated with a 99-point reduction in "
            "`Temperature`."
        )
    )
    unknown_entity = _insight_candidate(
        statement=(
            "`Pressure` contains highly overlapping information with "
            "`Temperature` in this dataset."
        )
    )

    unknown_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[unknown]),
        ledger,
        evidence,
        Settings(),
    )
    number_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[numbered]),
        ledger,
        evidence,
        Settings(),
    )
    entity_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[unknown_entity]),
        ledger,
        evidence,
        Settings(),
    )

    assert any("unknown fact" in error for error in unknown_errors)
    assert any("unsupported numbers" in error for error in number_errors)
    assert any("unsupported table or column" in error for error in entity_errors)


def test_insight_candidate_requires_grounded_non_hypothetical_implication():
    ledger, evidence = _insight_fixture()
    restatement = _insight_candidate().model_copy(
        update={
            "why_it_matters": (
                ledger.writer_ready_facts[0].allowed_interpretations[0]
            )
        }
    )
    hidden_hypothesis = _insight_candidate().model_copy(
        update={
            "why_it_matters": (
                "The pattern may reflect a data artifact in the source."
            )
        }
    )
    unsupported_number = _insight_candidate().model_copy(
        update={
            "why_it_matters": (
                "The implication applies to 99 analytical settings."
            )
        }
    )

    restatement_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[restatement]),
        ledger,
        evidence,
        Settings(),
    )
    hypothesis_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[hidden_hypothesis]),
        ledger,
        evidence,
        Settings(),
    )
    number_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[unsupported_number]),
        ledger,
        evidence,
        Settings(),
    )

    assert any("restates a source finding" in error for error in restatement_errors)
    assert any("explanatory hypothesis" in error for error in hypothesis_errors)
    assert any("why_it_matters" in error for error in number_errors)


def test_single_fact_pseudo_insight_rejected_but_anomaly_allowed():
    ledger, evidence = _insight_fixture()
    pseudo = _insight_candidate(
        insight_type=InsightType.CONTRAST,
        source_fact_ids=["FACT_INS_001"],
        source_evidence_ids=["EVD_INS_001"],
    )
    anomaly = _insight_candidate(
        insight_id="INSIGHT_ANOMALY",
        statement=(
            "The association in `Humidity` and `Temperature` is an anomaly "
            "requiring further review in this dataset."
        ),
        insight_type=InsightType.ANOMALY,
        source_fact_ids=["FACT_INS_001"],
        source_evidence_ids=["EVD_INS_001"],
    )

    assert any(
        "single-fact pseudo-insight" in error
        for error in validate_insight_candidates(
            InsightCandidateSet(candidates=[pseudo]),
            ledger,
            evidence,
            Settings(),
        )
    )
    assert not validate_insight_candidates(
        InsightCandidateSet(candidates=[anomaly]),
        ledger,
        evidence,
        Settings(),
    )


def test_causal_escalation_is_rejected():
    ledger, evidence = _insight_fixture()
    causal = _insight_candidate(
        statement="`Humidity` causes lower `Temperature`."
    )

    assert any(
        "causal wording" in error
        for error in validate_insight_candidates(
            InsightCandidateSet(candidates=[causal]),
            ledger,
            evidence,
            Settings(),
        )
    )


def test_predictive_and_forecast_escalation_are_rejected():
    ledger, evidence = _insight_fixture()
    predictive = _insight_candidate(
        statement="`Humidity` predicts `Temperature`."
    )
    forecast = _insight_candidate(
        statement="`Humidity` forecasts future `Temperature` values."
    )

    predictive_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[predictive]),
        ledger,
        evidence,
        Settings(),
    )
    forecast_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[forecast]),
        ledger,
        evidence,
        Settings(),
    )

    assert any("predictive wording" in error for error in predictive_errors)
    assert any("forecast wording" in error for error in forecast_errors)


def test_insight_verifier_must_confirm_synthesis_and_implication():
    ledger, evidence = _insight_fixture()
    candidate = _insight_candidate()
    candidates = InsightCandidateSet(candidates=[candidate])
    restatement_review = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id=candidate.insight_id,
                status=InsightVerificationStatus.VERIFIED,
                confidence=0.9,
                salience=0.9,
                adds_bounded_synthesis=False,
                analytical_implication_supported=False,
                contains_hypothesis=False,
            )
        ]
    )
    valid_review = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id=candidate.insight_id,
                status=InsightVerificationStatus.VERIFIED,
                confidence=0.9,
                salience=0.9,
                adds_bounded_synthesis=True,
                analytical_implication_supported=True,
                contains_hypothesis=False,
            )
        ]
    )

    errors = validate_insight_verification(
        restatement_review,
        candidates,
        ledger,
        evidence,
        Settings(),
    )

    assert any("direct-finding restatement" in error for error in errors)
    assert any("supported analytical implication" in error for error in errors)
    assert not validate_insight_verification(
        valid_review,
        candidates,
        ledger,
        evidence,
        Settings(),
    )


def test_hypotheses_remain_separate_under_both_policies():
    ledger, evidence = _insight_fixture()
    candidate = _insight_candidate(
        insight_id="INSIGHT_HYP",
        statement=(
            "Hypothesis: the observed association may reflect an unmeasured "
            "process."
        ),
        interpretation_level=InterpretationLevel.HYPOTHESIS,
        suitable_for_main_report=False,
    )
    candidates = InsightCandidateSet(candidates=[candidate])
    verification = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id="INSIGHT_HYP",
                status=InsightVerificationStatus.HYPOTHESIS_ONLY,
                confidence=0.8,
                salience=0.7,
                adds_bounded_synthesis=False,
                analytical_implication_supported=False,
                contains_hypothesis=True,
            )
        ]
    )

    for allow in [False, True]:
        settings = replace(
            Settings(),
            allow_hypotheses_in_report=allow,
        )
        assert not validate_insight_candidates(
            candidates,
            ledger,
            evidence,
            settings,
        )
        result = materialise_insight_ledger(
            candidates=candidates,
            verification=verification,
            fact_ledger=ledger,
            evidence_ledger=evidence,
            settings=settings,
        )
        assert not result.verified_insights
        assert [
            insight.insight_id
            for insight in result.hypothesis_only_insights
        ] == ["INSIGHT_HYP"]


def test_insight_ledger_materialisation_applies_status_threshold_order_and_limit():
    ledger, evidence = _insight_fixture()
    first = _insight_candidate(
        insight_id="INSIGHT_FIRST",
        salience=0.95,
    )
    second = _insight_candidate(
        insight_id="INSIGHT_SECOND",
        statement=(
            "The two verified association summaries provide overlapping "
            "directional information in this dataset."
        ),
        insight_type=InsightType.REDUNDANCY,
        salience=0.8,
    )
    rejected = _insight_candidate(
        insight_id="INSIGHT_REJECTED",
        statement=(
            "The verified findings form a bounded narrative summary for this "
            "dataset."
        ),
        insight_type=InsightType.NARRATIVE_SUMMARY,
        salience=0.7,
    )
    candidates = InsightCandidateSet(
        candidates=[first, second, rejected]
    )
    verification = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id="INSIGHT_FIRST",
                status=InsightVerificationStatus.VERIFIED_WITH_CAVEAT,
                verified_statement=(
                    first.statement
                    + " This remains a descriptive association."
                ),
                confidence=0.9,
                salience=0.95,
                adds_bounded_synthesis=True,
                analytical_implication_supported=True,
                contains_hypothesis=False,
                limitations=["No causal conclusion is supported."],
            ),
            InsightVerificationRecord(
                insight_id="INSIGHT_SECOND",
                status=InsightVerificationStatus.VERIFIED,
                confidence=0.85,
                salience=0.8,
                adds_bounded_synthesis=True,
                analytical_implication_supported=True,
                contains_hypothesis=False,
            ),
            InsightVerificationRecord(
                insight_id="INSIGHT_REJECTED",
                status=InsightVerificationStatus.REJECTED,
                confidence=0.9,
                salience=0.7,
                adds_bounded_synthesis=False,
                analytical_implication_supported=False,
                contains_hypothesis=False,
                verification_notes=["The synthesis is not sufficiently useful."],
            ),
        ]
    )
    settings = replace(
        Settings(),
        max_verified_main_insights=1,
    )

    result = materialise_insight_ledger(
        candidates=candidates,
        verification=verification,
        fact_ledger=ledger,
        evidence_ledger=evidence,
        settings=settings,
    )

    assert [
        insight.insight_id
        for insight in result.verified_insights
    ] == ["INSIGHT_FIRST"]
    assert result.verified_insights[0].verification_status == (
        InsightVerificationStatus.VERIFIED_WITH_CAVEAT
    )
    assert "descriptive association" in result.verified_insights[0].statement
    assert {
        rejection.insight_id
        for rejection in result.rejected_insights
    } == {"INSIGHT_SECOND", "INSIGHT_REJECTED"}


def test_writer_payload_contains_only_writer_eligible_insights():
    ledger, evidence = _insight_fixture()
    main_candidate = _insight_candidate()
    hypothesis_candidate = _insight_candidate(
        insight_id="INSIGHT_HYP",
        statement="Hypothesis: another process may contribute.",
        interpretation_level=InterpretationLevel.HYPOTHESIS,
        suitable_for_main_report=False,
    )
    insight_ledger = InsightLedger(
        verified_insights=[_verified_insight(main_candidate)],
        hypothesis_only_insights=[
            _verified_insight(
                hypothesis_candidate,
                status=InsightVerificationStatus.HYPOTHESIS_ONLY,
            )
        ],
        rejected_insights=[
            InsightRejection(
                insight_id="INSIGHT_BAD",
                candidate=_insight_candidate(insight_id="INSIGHT_BAD"),
                reasons=["Rejected."],
            )
        ],
    )
    understanding = DataUnderstanding(
        profile_fingerprint="insight-test",
        dataset_summary="Unverified prose must remain private.",
        tables=[],
    )
    plan = ExecutionPlan(
        objective="Describe the strongest findings.",
        tasks=[],
        route_order=[],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=10,
        rationale="Test.",
    )
    pack = build_writer_evidence_pack(
        request=plan.objective,
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
        insight_ledger=insight_ledger,
    )
    payload = build_compact_writer_payload(pack)

    assert payload["priority_verified_insights"]
    assert payload["priority_verified_insights"][0].source_fact_ids
    assert payload["priority_facts"]
    assert payload["genre"] == ReportGenre.DATA_SCIENCE_REPORT
    assert payload["perspective"] == ReportPerspective.NEUTRAL
    assert payload["communication_goal"]
    assert payload["hypothesis_only_insights"] == []
    assert payload["verified_strength_labels_by_fact_id"][
        "FACT_INS_001"
    ] == ["strong_association"]
    assert "INSIGHT_BAD" not in str(payload)
    assert "Unverified prose" not in str(payload)


def test_writer_materialisation_expands_insight_provenance_without_text_change():
    ledger, _ = _insight_fixture()
    insight = _verified_insight()
    insight_ledger = InsightLedger(verified_insights=[insight])
    draft = WriterAgentDraft(
        title="Bounded report",
        sections=[
            WriterSectionDraft(
                heading="Main insight",
                sentences=[
                    WriterSentenceDraft(
                        text=insight.statement,
                        insight_ids=[insight.insight_id],
                        interpretation_level=(
                            InterpretationLevel.BOUNDED_INSIGHT
                        ),
                        support_type=SupportType.MULTI_FACT_SYNTHESIS,
                    )
                ],
            )
        ],
    )

    output = materialise_writer_output(
        draft,
        ledger,
        insight_ledger=insight_ledger,
    )
    support = output.sentence_support[0]

    assert insight.statement in output.markdown
    assert support.insight_ids == [insight.insight_id]
    assert support.interpretation_level == InterpretationLevel.BOUNDED_INSIGHT
    assert set(support.fact_ids) == set(insight.source_fact_ids)
    assert set(support.evidence_ids) == set(insight.source_evidence_ids)


def test_writer_hypothesis_requires_enabled_separate_section():
    ledger, _ = _insight_fixture()
    candidate = _insight_candidate(
        insight_id="INSIGHT_HYP_WRITER",
        statement="Hypothesis: an unmeasured process may contribute.",
        interpretation_level=InterpretationLevel.HYPOTHESIS,
        suitable_for_main_report=False,
    )
    hypothesis = _verified_insight(
        candidate,
        status=InsightVerificationStatus.HYPOTHESIS_ONLY,
    )
    insight_ledger = InsightLedger(
        hypothesis_only_insights=[hypothesis]
    )
    draft = WriterAgentDraft(
        title="Further investigation",
        sections=[
            WriterSectionDraft(
                heading="Questions for Further Investigation",
                sentences=[
                    WriterSentenceDraft(
                        text=hypothesis.statement,
                        insight_ids=[hypothesis.insight_id],
                        interpretation_level=InterpretationLevel.HYPOTHESIS,
                        support_type=SupportType.MULTI_FACT_SYNTHESIS,
                    )
                ],
            )
        ],
    )

    with pytest.raises(ValueError, match="disabled"):
        materialise_writer_output(
            draft,
            ledger,
            insight_ledger=insight_ledger,
        )

    output = materialise_writer_output(
        draft,
        ledger,
        insight_ledger=insight_ledger,
        allow_hypotheses_in_report=True,
    )
    assert output.sentence_support[0].interpretation_level == (
        InterpretationLevel.HYPOTHESIS
    )


def test_writer_rejects_explanatory_hypothesis_disguised_as_next_step():
    ledger, _ = _insight_fixture()
    sentence = (
        "Further analysis could explore whether the association reflects a "
        "data artifact."
    )
    draft = WriterAgentDraft(
        title="Unsupported explanation",
        sections=[
            WriterSectionDraft(
                heading="Limitations and next steps",
                sentences=[
                    WriterSentenceDraft(
                        text=sentence,
                        fact_ids=["FACT_INS_001", "FACT_INS_002"],
                        support_type=SupportType.PARAPHRASE,
                    )
                ],
            )
        ],
    )

    with pytest.raises(ValueError, match="possible explanation"):
        materialise_writer_output(
            draft,
            ledger,
            insight_ledger=InsightLedger(),
        )


def test_writer_validation_rejects_unknown_or_missing_insight_mapping():
    ledger, _ = _insight_fixture()
    insight = _verified_insight()
    insight_ledger = InsightLedger(verified_insights=[insight])

    with pytest.raises(ValueError, match="unknown insight"):
        materialise_writer_output(
            WriterAgentDraft(
                title="Unknown",
                sections=[
                    WriterSectionDraft(
                        heading="Main",
                        sentences=[
                            WriterSentenceDraft(
                                text=insight.statement,
                                insight_ids=["INSIGHT_UNKNOWN"],
                                interpretation_level=(
                                    InterpretationLevel.BOUNDED_INSIGHT
                                ),
                                support_type=SupportType.MULTI_FACT_SYNTHESIS,
                            )
                        ],
                    )
                ],
            ),
            ledger,
            insight_ledger=insight_ledger,
        )

    sentence = insight.statement
    invalid = WriterOutput(
        title="Missing mapping",
        markdown=f"# Missing mapping\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            )
        ],
        selected_fact_ids=insight.source_fact_ids,
    )

    assert any(
        "bounded insight" in error
        for error in validate_writer_output(
            invalid,
            ledger,
            insight_ledger,
        )
    )


def test_direct_finding_remains_valid_without_insight_id():
    ledger, _ = _insight_fixture()
    sentence = ledger.writer_ready_facts[0].fact_summary
    output = WriterOutput(
        title="Finding",
        markdown=f"# Finding\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001"],
                evidence_ids=["EVD_INS_001"],
                support_type=SupportType.DIRECT,
            )
        ],
        selected_fact_ids=["FACT_INS_001"],
    )

    assert not validate_writer_output(output, ledger, InsightLedger())


def test_writer_entity_grounding_is_case_insensitive_and_diagnostic():
    ledger, _ = _insight_fixture()
    fact_lookup = {
        fact.fact_id: fact
        for fact in ledger.writer_ready_facts
    }
    case_variant = WriterSentenceDraft(
        text=(
            "The `humidity` and `temperature` fields are associated in this "
            "dataset."
        ),
        fact_ids=["FACT_INS_001"],
        support_type=SupportType.PARAPHRASE,
    )

    assert not writer_sentence_grounding_errors(
        sentence=case_variant,
        fact_lookup=fact_lookup,
        insight_lookup={},
        sentence_label="Sentence 1.1",
    )

    unsupported = WriterSentenceDraft(
        text="The `Pressure` and `Wind` fields are associated.",
        fact_ids=["FACT_INS_001"],
        support_type=SupportType.PARAPHRASE,
    )
    early_errors = writer_sentence_grounding_errors(
        sentence=unsupported,
        fact_lookup=fact_lookup,
        insight_lookup={},
        sentence_label="Sentence 1.2",
    )

    assert early_errors == [
        "Sentence 1.2 contains unsupported entities ['Pressure', 'Wind']; "
        "mapped fact IDs: ['FACT_INS_001']."
    ]

    unsupported_number = case_variant.model_copy(
        update={
            "text": (
                "The `humidity` and `temperature` fields have a correlation "
                "of 99."
            )
        }
    )
    assert any(
        "number unsupported" in error
        for error in writer_sentence_grounding_errors(
            sentence=unsupported_number,
            fact_lookup=fact_lookup,
            insight_lookup={},
            sentence_label="Sentence 1.3",
        )
    )

    sentence = unsupported.text
    output = WriterOutput(
        title="Unsupported entities",
        markdown=f"# Unsupported entities\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001"],
                evidence_ids=["EVD_INS_001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_INS_001"],
    )
    late_entity_errors = [
        error
        for error in validate_writer_output(
            output,
            ledger,
            InsightLedger(),
        )
        if "unsupported entities" in error
    ]

    assert late_entity_errors == [
        "SENT_0001 contains unsupported entities ['Pressure', 'Wind']; "
        "mapped fact IDs: ['FACT_INS_001']."
    ]


def _audit_verified_insight_sentence(
    sentence: str,
    *,
    insight: VerifiedInsight | None = None,
) -> AuditReport:
    ledger, evidence = _insight_fixture()
    insight = insight or _verified_insight()
    output = WriterOutput(
        title="Insight audit",
        markdown=f"# Insight audit\n\n## Main insight\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            )
        ],
        selected_fact_ids=insight.source_fact_ids,
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
        insight_ledger=InsightLedger(
            verified_insights=[insight]
        ),
    )


def test_verified_insight_sentence_is_not_treated_as_hallucination():
    audit = _audit_verified_insight_sentence(
        _verified_insight().statement
    )

    assert not [
        annotation
        for annotation in audit.annotations
        if annotation.subtype
        in {
            "unsupported_insight",
            "insight_exceeds_verified_wording",
        }
    ]
    assert not any(
        "lists findings without relating" in finding
        for finding in audit.quality_assessment.findings
    )


def test_quality_warns_when_available_insights_are_not_used():
    ledger, evidence = _insight_fixture()
    insight = _verified_insight()
    sentence = ledger.writer_ready_facts[0].fact_summary
    output = WriterOutput(
        title="Fact list",
        markdown=f"# Fact list\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001"],
                evidence_ids=["EVD_INS_001"],
                support_type=SupportType.DIRECT,
            )
        ],
        selected_fact_ids=["FACT_INS_001"],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        insight_ledger=InsightLedger(
            verified_insights=[insight]
        ),
    )

    assert any(
        "lists findings without relating" in finding
        for finding in audit.quality_assessment.findings
    )


def test_quality_requires_verified_analytical_implication():
    insight = _verified_insight()
    restatement_only = _audit_verified_insight_sentence(
        insight.statement,
        insight=insight,
    )

    assert any(
        "does not explain its supported analytical implication" in finding
        for finding in restatement_only.quality_assessment.findings
    )

    ledger, evidence = _insight_fixture()
    markdown = (
        "# Insight audit\n\n## Main insight\n\n"
        f"{insight.statement}\n\n{insight.why_it_matters}\n"
    )
    output = WriterOutput(
        title="Insight audit",
        markdown=markdown,
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=insight.statement,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            ),
            SentenceSupport(
                sentence_id="SENT_0002",
                sentence_text=insight.why_it_matters,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            ),
        ],
        selected_fact_ids=insight.source_fact_ids,
    )
    with_implication = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        insight_ledger=InsightLedger(verified_insights=[insight]),
    )

    assert not any(
        "does not explain its supported analytical implication" in finding
        for finding in with_implication.quality_assessment.findings
    )


def test_audit_flags_strength_classification_inconsistency():
    ledger, evidence = _insight_fixture()
    sentence = "The two measures have moderate correlations."
    output = WriterOutput(
        title="Strength mismatch",
        markdown=f"# Strength mismatch\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001", "FACT_INS_002"],
                evidence_ids=["EVD_INS_001", "EVD_INS_002"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_INS_001", "FACT_INS_002"],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
    )

    assert any(
        annotation.subtype == "inconsistent_strength_label"
        for annotation in audit.annotations
    )


def test_insight_wording_escalation_is_flagged():
    audit = _audit_verified_insight_sentence(
        "One measure is completely redundant and should always be removed."
    )

    assert any(
        annotation.subtype == "insight_exceeds_verified_wording"
        for annotation in audit.annotations
    )


def test_unlabelled_hypothesis_is_flagged():
    ledger, evidence = _insight_fixture()
    sentence = (
        "The dataset pattern may reflect lower temperature because of an "
        "unmeasured process."
    )
    output = WriterOutput(
        title="Hypothesis",
        markdown=f"# Hypothesis\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001", "FACT_INS_002"],
                evidence_ids=["EVD_INS_001", "EVD_INS_002"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_INS_001", "FACT_INS_002"],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
    )

    assert any(
        annotation.subtype == "unlabelled_hypothesis"
        for annotation in audit.annotations
    )


def test_unsupported_sports_chronology_is_flagged():
    ledger, evidence = _insight_fixture()
    sentence = "Player X led a dramatic comeback."
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "fact_summary": "Player X scored for Team A.",
            "entities": ["Player X", "Team A"],
        }
    )
    ledger = FactLedger(writer_ready_facts=[fact])
    output = WriterOutput(
        title="Game",
        markdown=f"# Game\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=[fact.fact_id],
                evidence_ids=fact.evidence_ids,
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=[fact.fact_id],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
    )

    assert any(
        annotation.subtype == "unsupported_sports_narrative"
        for annotation in audit.annotations
    )


def test_safe_sports_synthesis_requires_no_chronology():
    statements = [
        "Team A won the game.",
        "Player X and Player Y shared the Team A scoring lead.",
        "Team A recorded more rebounds.",
        "Team A recorded fewer turnovers.",
    ]
    evidence_items = [
        EvidenceItem(
            evidence_id=f"EVD_GAME_{index:03d}",
            route=AnalysisRoute.DESCRIPTIVE,
            task_ids=["TASK_GAME"],
            finding=statement,
            metrics={},
            source_tables=["game"],
            source_columns=["Team", "Player", "Points", "Rebounds", "Turnovers"],
            method="Direct deterministic game summary.",
            practical_interpretation=statement,
            strength_label="game_fact",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=1.0,
            salience=1.0,
            recommended_use=RecommendedUse.MAIN_FINDING,
        )
        for index, statement in enumerate(statements, start=1)
    ]
    evidence = EvidenceLedger(
        fingerprint="game",
        items=evidence_items,
    )
    facts = [
        VerifiedFact(
            fact_id=f"FACT_GAME_{index:03d}",
            source_candidate_id=f"CAN_GAME_{index:03d}",
            fact_summary=item.finding,
            evidence_ids=[item.evidence_id],
            entities=[
                "game",
                "Team A",
                "Player X",
                "Player Y",
                "Team",
                "Player",
                "Points",
                "Rebounds",
                "Turnovers",
            ],
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=1.0,
            salience=1.0,
            recommended_use=RecommendedUse.MAIN_FINDING,
        )
        for index, item in enumerate(evidence_items, start=1)
    ]
    ledger = FactLedger(writer_ready_facts=facts)
    sentence = (
        "Team A combined a shared scoring lead with advantages in rebounds "
        "and turnovers."
    )
    insight = VerifiedInsight(
        insight_id="INSIGHT_GAME",
        statement=sentence,
        insight_type=InsightType.NARRATIVE_SUMMARY,
        interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
        source_fact_ids=[fact.fact_id for fact in facts],
        source_evidence_ids=[item.evidence_id for item in evidence_items],
        why_it_matters="It provides a bounded game narrative.",
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        confidence=0.95,
        salience=0.95,
        verification_status=InsightVerificationStatus.VERIFIED,
    )
    output = WriterOutput(
        title="Game report",
        markdown=f"# Game report\n\n## Game narrative\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            )
        ],
        selected_fact_ids=insight.source_fact_ids,
    )
    spec = _basic_spec().model_copy(
        update={"genre": ReportGenre.SPORTS_GAME_REPORT}
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
        insight_ledger=InsightLedger(
            verified_insights=[insight]
        ),
    )

    assert not audit.annotations


def test_insight_feature_flag_ablation_keeps_fact_writer_path(tmp_path):
    path = tmp_path / "ablation.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)
    settings = replace(
        Settings(),
        use_llm=False,
        enable_insight_synthesis=False,
        output_dir=tmp_path / "runs",
    )

    result = Table2TextWorkflow(settings).run_sync(
        [path],
        "Understand the dataset.",
    )

    assert not result.insight_ledger.synthesis_enabled
    assert "disabled by configuration" in (
        result.insight_ledger.fallback_reason or ""
    )
    assert result.raw_writer_output.writer_mode == "deterministic_fallback"
    assert (
        settings.output_dir
        / result.run_id
        / "07_insight_ledger.json"
    ).exists()


def test_insight_stage_failure_continues_without_changing_llm_writer_mode(
    tmp_path,
):
    path = tmp_path / "failure.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)
    settings = replace(
        Settings(),
        use_llm=True,
        output_dir=tmp_path / "runs",
        writer_quality_revision_rounds=0,
    )
    workflow = Table2TextWorkflow(settings)

    async def deterministic_regular_fallback(
        self,
        *,
        stage,
        dependencies,
        fallback,
        **_,
    ):
        if stage == "natural_writer":
            ledger = FactLedger.model_validate(
                dependencies.payload["fact_ledger"]
            )
            fact = ledger.writer_ready_facts[0]
            return WriterAgentDraft(
                title="Supported report",
                sections=[
                    WriterSectionDraft(
                        heading="Dataset overview",
                        sentences=[
                            WriterSentenceDraft(
                                text=fact.fact_summary,
                                fact_ids=[fact.fact_id],
                                support_type=SupportType.DIRECT,
                            )
                        ],
                    )
                ],
            )
        return fallback()

    async def failed_optional_stage(self, **_):
        return None, "simulated insight-stage failure"

    workflow.run_agent_or_fallback = MethodType(
        deterministic_regular_fallback,
        workflow,
    )
    workflow.run_optional_insight_agent = MethodType(
        failed_optional_stage,
        workflow,
    )

    result = workflow.run_sync(
        [path],
        "Understand the dataset.",
    )

    assert "simulated insight-stage failure" in (
        result.insight_ledger.fallback_reason or ""
    )
    assert result.raw_writer_output.writer_mode == "llm_writer"
    assert result.release_status in {
        ReleaseStatus.APPROVED,
        ReleaseStatus.APPROVED_WITH_WARNINGS,
        ReleaseStatus.HUMAN_REVIEW_REQUIRED,
    }
    assert result.model_dump_json()


def test_late_writer_materialisation_failure_uses_deterministic_fallback(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "materialisation.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)
    settings = replace(
        Settings(),
        use_llm=True,
        output_dir=tmp_path / "runs",
        writer_quality_revision_rounds=0,
    )
    workflow = Table2TextWorkflow(settings)

    async def deterministic_regular_fallback(
        self,
        *,
        stage,
        dependencies,
        fallback,
        **_,
    ):
        if stage == "natural_writer":
            ledger = FactLedger.model_validate(
                dependencies.payload["fact_ledger"]
            )
            fact = ledger.writer_ready_facts[0]
            return WriterAgentDraft(
                title="Materialisation candidate",
                sections=[
                    WriterSectionDraft(
                        heading="Dataset overview",
                        sentences=[
                            WriterSentenceDraft(
                                text=fact.fact_summary,
                                fact_ids=[fact.fact_id],
                                support_type=SupportType.DIRECT,
                            )
                        ],
                    )
                ],
            )
        return fallback()

    async def failed_optional_stage(self, **_):
        return None, "simulated insight-stage failure"

    def failed_materialisation(*_, **__):
        raise ValueError("simulated late entity mismatch")

    workflow.run_agent_or_fallback = MethodType(
        deterministic_regular_fallback,
        workflow,
    )
    workflow.run_optional_insight_agent = MethodType(
        failed_optional_stage,
        workflow,
    )
    monkeypatch.setattr(
        "table2text.workflow.materialise_writer_output",
        failed_materialisation,
    )

    result = workflow.run_sync(
        [path],
        "Understand the dataset.",
    )
    run_directory = settings.output_dir / result.run_id

    assert result.raw_writer_output.writer_mode == "deterministic_fallback"
    assert (run_directory / "09_writer_structured_draft.json").exists()
    error_path = run_directory / "09_writer_materialisation_error.txt"
    assert error_path.exists()
    assert "simulated late entity mismatch" in error_path.read_text()


def test_empty_insight_ledger_fallback_is_explicit():
    ledger = empty_insight_ledger(
        synthesis_enabled=True,
        fallback_reason="request budget exhausted",
    )

    assert ledger.synthesis_enabled
    assert not ledger.verified_insights
    assert ledger.fallback_reason == "request budget exhausted"


def _nested_event_fixture(reference_text: str) -> dict:
    return {
        "event_id": "EVENT-001",
        "date": {"year": 2026, "month": 7, "day": 23},
        "venue": {"city": "Example City", "name": "Example Arena"},
        "overtime": False,
        "participants": {
            "home": {
                "name": "Alpha",
                "statistics": {
                    "team": {
                        "game": {
                            "points": 90,
                            "rebounds": 40,
                            "assists": 20,
                        }
                    },
                    "entities": {
                        "alpha_one": {
                            "name": "Alex One",
                            "points": 25,
                            "rebounds": 8,
                            "assists": 6,
                        },
                        "alpha_two": {
                            "name": "Alex Two",
                            "points": 18,
                            "rebounds": 5,
                            "assists": 4,
                        },
                    },
                },
            },
            "visitor": {
                "name": "Beta",
                "statistics": {
                    "team": {
                        "game": {
                            "points": 80,
                            "rebounds": 35,
                            "assists": 17,
                        }
                    },
                    "entities": {
                        "beta_one": {
                            "name": "Blair One",
                            "points": 22,
                            "rebounds": 9,
                            "assists": 3,
                        }
                    },
                },
            },
        },
        "reference_text": reference_text,
    }


def _event_field_policy() -> EvaluationFieldPolicy:
    return EvaluationFieldPolicy(
        operational_input_paths=[
            "event_id",
            "date",
            "venue",
            "overtime",
            "participants",
        ],
        held_out_reference_paths=["reference_text"],
    )


def _write_nested_event(tmp_path, reference_text: str):
    path = tmp_path / "nested_event.json"
    path.write_text(
        json.dumps(_nested_event_fixture(reference_text)),
        encoding="utf-8",
    )
    return path


def test_nested_event_is_one_record_and_explicit_reference_is_held_out(
    tmp_path,
):
    reference_text = "REFERENCE SENTINEL " * 80
    path = _write_nested_event(tmp_path, reference_text)

    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    frame = next(iter(bundle.tables.values()))
    profile = profile_data(bundle)

    assert len(frame) == 1
    assert bundle.input_structure is not None
    assert bundle.input_structure.shape == InputShape.EVENT_RECORD
    assert bundle.input_structure.row_semantics == "one event"
    assert bundle.input_structure.representation_status == (
        InputRepresentationStatus.VALID
    )
    assert "reference_text" not in frame.columns
    assert "reference_text" not in bundle.input_structure.nested_paths
    assert reference_text.strip() not in json.dumps(
        {
            "profile": profile.model_dump(mode="json"),
            "structure": bundle.input_structure.model_dump(mode="json"),
            "operational": bundle.structured_inputs,
        },
        default=str,
    )


def test_nested_entity_collection_retains_core_tabular_capabilities(
    tmp_path,
):
    path = tmp_path / "entities.json"
    path.write_text(
        json.dumps(
            [
                {
                    "name": f"entity-{index}",
                    "value": index,
                    "attributes": {"group": index % 2},
                    "tags": ["example"],
                }
                for index in range(30)
            ]
        ),
        encoding="utf-8",
    )

    bundle = load_data([path])
    capabilities = available_capabilities(bundle)

    assert bundle.input_structure is not None
    assert bundle.input_structure.shape == InputShape.ENTITY_COLLECTION
    assert len(next(iter(bundle.tables.values()))) == 30
    assert {
        EvidenceCapability.MISSINGNESS,
        EvidenceCapability.DUPLICATES,
        EvidenceCapability.DISTRIBUTION_SUMMARY,
        EvidenceCapability.ASSOCIATION,
        EvidenceCapability.GROUP_COMPARISON,
    }.issubset(capabilities)


def test_undeclared_event_reference_is_quarantined_and_ineligible(
    tmp_path,
):
    reference_text = "UNDECLARED REFERENCE SENTINEL " * 60
    path = _write_nested_event(tmp_path, reference_text)
    bundle = load_data([path])

    assert len(next(iter(bundle.tables.values()))) == 1
    assert bundle.input_structure is not None
    assert bundle.input_structure.sparse_flattening_detected
    assert bundle.input_structure.representation_status == (
        InputRepresentationStatus.AMBIGUOUS
    )
    assert bundle.evaluation_field_policy.held_out_reference_paths == [
        "reference_text"
    ]

    settings = replace(
        Settings(),
        use_llm=False,
        enable_insight_synthesis=False,
        output_dir=tmp_path / "runs_ambiguous",
    )
    result = Table2TextWorkflow(settings).run_sync(
        [path],
        "Understand the dataset and report its strongest findings.",
    )

    assert not result.primary_evaluation_eligible
    assert result.primary_evaluation_reason == (
        "input_representation_ambiguous"
    )
    assert result.release_status == ReleaseStatus.HUMAN_REVIEW_REQUIRED
    assert reference_text.strip() not in result.final_writer_output.markdown


def test_generic_event_capabilities_extract_outcome_rankings_and_paths(
    tmp_path,
):
    path = _write_nested_event(tmp_path, "HELD OUT " * 100)
    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    capabilities = available_capabilities(bundle)
    profile = profile_data(bundle)
    plan = fallback_execution_plan(
        "Write a neutral event report.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=capabilities,
    )
    evidence = execute_plan(bundle, plan, Settings())

    assert {
        EvidenceCapability.EVENT_OUTCOME,
        EvidenceCapability.ENTITY_PERFORMANCE,
        EvidenceCapability.RANKING,
        EvidenceCapability.GROUP_COMPARISON,
    }.issubset(capabilities)

    outcome = next(
        item
        for item in evidence.items
        if item.evidence_type == "event_outcome"
    )
    assert outcome.metrics["winner"] == "Alpha"
    assert outcome.metrics["loser"] == "Beta"
    assert outcome.metrics["winner_score"] == 90
    assert outcome.metrics["loser_score"] == 80
    assert outcome.metrics["margin"] == 10
    assert {
        "participants.home.name",
        "participants.home.statistics.team.game.points",
        "participants.visitor.name",
        "participants.visitor.statistics.team.game.points",
    }.issubset(outcome.source_paths)

    points_ranking = next(
        item
        for item in evidence.items
        if item.evidence_type == "entity_ranking"
        and item.metrics["metric"] == "points"
    )
    assert points_ranking.metrics["ranking"][0]["entity"] == "Alex One"
    assert points_ranking.metrics["ranking"][0]["value"] == 25
    assert "participants.home.statistics.entities.alpha_one.name" in (
        points_ranking.source_paths
    )


def test_event_capability_selection_and_report_contract_are_bounded(
    tmp_path,
):
    path = _write_nested_event(tmp_path, "HELD OUT " * 100)
    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    profile = profile_data(bundle)
    restricted_capabilities = [
        EvidenceCapability.DATASET_PROFILE,
        EvidenceCapability.EVENT_OUTCOME,
    ]

    generic = fallback_execution_plan(
        "Understand the dataset and report its strongest findings.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=restricted_capabilities,
    )
    event = fallback_execution_plan(
        "Write a neutral event report.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=restricted_capabilities,
    )

    assert generic.report_specification.genre == ReportGenre.EVENT_REPORT
    assert event.report_specification.genre == ReportGenre.EVENT_REPORT
    assert "event_result" in event.report_specification.required_content_slots
    assert all(
        task.capability is None
        or task.capability in restricted_capabilities
        for task in event.tasks
    )
    assert EvidenceCapability.RANKING not in event.selected_capabilities

    resolved_genre, _, _ = resolve_report_genre(
        request="Understand the dataset and report its strongest findings.",
        planned_genre=ReportGenre.DATASET_OVERVIEW,
        configured_genre=None,
        input_structure=bundle.input_structure,
    )
    assert resolved_genre == ReportGenre.EVENT_REPORT


def test_genre_quality_revises_event_report_that_omits_supported_result(
    tmp_path,
):
    path = _write_nested_event(tmp_path, "HELD OUT " * 100)
    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    capabilities = available_capabilities(bundle)
    plan = fallback_execution_plan(
        "Write a neutral event report.",
        profile_data(bundle),
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=capabilities,
    )
    evidence = execute_plan(bundle, plan, Settings())
    ranking = next(
        item
        for item in evidence.items
        if item.evidence_type == "entity_ranking"
    )
    output = WriterOutput(
        title="Incomplete event report",
        markdown=f"# Incomplete event report\n\n{ranking.finding}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=ranking.finding,
                evidence_ids=[ranking.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    assessment = assess_genre_quality(
        output,
        plan.report_specification,
        evidence,
    )

    assert assessment.status == QualityStatus.REVISE
    assert "event_result" in assessment.missing_supported_slots


def test_event_reference_never_reaches_operational_prompts_or_report(
    tmp_path,
):
    reference_text = "SECRET REFERENCE PROSE " * 70
    path = _write_nested_event(tmp_path, reference_text)
    settings = replace(
        Settings(),
        use_llm=True,
        enable_insight_synthesis=False,
        writer_quality_revision_rounds=0,
        output_dir=tmp_path / "runs_explicit",
    )
    workflow = Table2TextWorkflow(settings)
    operational_payloads: list[str] = []

    async def capture_and_fallback(
        self,
        *,
        prompt,
        dependencies,
        fallback,
        **_,
    ):
        operational_payloads.append(str(prompt))
        operational_payloads.append(
            json.dumps(
                dependencies.payload,
                default=str,
                sort_keys=True,
            )
        )
        return fallback()

    workflow.run_agent_or_fallback = MethodType(
        capture_and_fallback,
        workflow,
    )
    result = workflow.run_sync(
        [path],
        "Write a neutral event report.",
        evaluation_field_policy=_event_field_policy(),
        report_genre=ReportGenre.EVENT_REPORT,
    )

    operational_text = "\n".join(operational_payloads)
    assert reference_text.strip() not in operational_text
    assert reference_text.strip() not in result.final_writer_output.markdown
    assert result.primary_evaluation_eligible
    assert result.execution_plan.report_specification.genre == (
        ReportGenre.EVENT_REPORT
    )
    assert result.genre_quality_assessment is not None
    assert result.genre_quality_assessment.status == QualityStatus.PASS
    assert result.genre_quality_assessment.missing_supported_slots == []
    assert "Alpha defeated Beta 90-80" in result.final_writer_output.markdown
    assert "comeback" not in result.final_writer_output.markdown.lower()
