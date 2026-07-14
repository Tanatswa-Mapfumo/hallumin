from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from table2text import Settings, Table2TextWorkflow
from table2text.analytics import execute_plan
from table2text.audit import (
    apply_repair_proposal,
    build_writer_evidence_pack,
    decide_release_status,
    deterministic_audit,
    fallback_writer,
    validate_repair_candidate,
    validate_writer_output,
)
from table2text.data import load_data, profile_data
from table2text.schemas import (
    AnalysisRoute,
    AuditAnnotation,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    ClaimPermission,
    DataUnderstanding,
    ErrorType,
    EvidenceItem,
    EvidenceLedger,
    ExecutionPlan,
    FactLedger,
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
    TargetStatus,
    ValidationStrategy,
    VerifiedFact,
    WriterOutput,
    ZeroRisk,
)
from table2text.agents import (
    fallback_execution_plan,
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
        markdown="Strength: Large group difference\n",
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
