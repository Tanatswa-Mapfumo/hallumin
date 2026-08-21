from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from table2text import Settings, Table2TextWorkflow
from table2text.agents import materialise_insight_ledger
from table2text.data import load_data
from table2text.evaluation.datasets import merge_examples, normalise_row
from table2text.evaluation.diagnostics import number_diagnostics
from table2text.evaluation.generation import (
    focus_scope_for_task,
    materialise_input,
    workflow_contract_for_variant,
)
from table2text.evaluation.deepeval_metrics import input_for_judge
from table2text.evaluation.human_evaluation import make_blinded_pairs
from table2text.evaluation.llm_judge_annotations import (
    OpenAIJudgeAnnotationConfig,
    build_annotation_judge_input,
)
from table2text.evaluation.models import (
    BenchmarkExample,
    DatasetConfig,
    DatasetSource,
    DeepEvalConfig,
    GenerationBackend,
    GenerationRecord,
    OutputMode,
    ReferenceMetricConfig,
    TaskFamily,
    VariantConfig,
)
from table2text.evaluation_backends import build_single_agent_prompt
from table2text.schemas import (
    AuditMode,
    ClaimPermission,
    CommunicationTask,
    EvidenceCapability,
    InsightCandidate,
    InsightCandidateSet,
    InsightContribution,
    InsightType,
    InsightVerificationRecord,
    InsightVerificationResult,
    InsightVerificationStatus,
    InputRepresentationStatus,
    InputShape,
    InputStructureProfile,
    InterpretationLevel,
    OutputForm as WorkflowOutputForm,
    ReportGenre,
    ReportSelectionSource,
)
from table2text.evaluation.notebook import (
    generate_reports_for_notebook,
    init_notebook_evaluation,
)
from table2text.evaluation import reference_metrics as reference_metrics_module
from table2text.evaluation.external_factuality import ExternalFactualityResult
from table2text.evaluation.reference_metrics import (
    evaluate_reference_metrics,
    factuality_context,
    normalized_event_source_context,
    plain_text,
)
from table2text.workflow import task_contract_fields
from table2text.task_contracts import infer_task_contract, resolve_task_contract
from table2text.evaluation.statistics import paired_bootstrap


def e2e_config() -> DatasetConfig:
    return DatasetConfig(
        dataset_id="e2e",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="e2e",
        task_family=TaskFamily.ATTRIBUTE_VERBALISATION,
        output_mode=OutputMode.SHORT_TEXT,
        language="en",
        sample_size=None,
        reference_fields=["references", "target"],
        id_fields=["gem_parent_id", "gem_id"],
    )


def webnlg_config() -> DatasetConfig:
    return DatasetConfig(
        dataset_id="web_nlg",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="webnlg",
        task_family=TaskFamily.TRIPLE_VERBALISATION,
        output_mode=OutputMode.SHORT_TEXT,
        language="en",
        sample_size=None,
        reference_fields=["target"],
        id_fields=["gem_id"],
    )


def dart_config() -> DatasetConfig:
    return DatasetConfig(
        dataset_id="dart",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="dart",
        task_family=TaskFamily.TRIPLE_VERBALISATION,
        output_mode=OutputMode.SHORT_TEXT,
        language="en",
        sample_size=None,
        reference_fields=["target"],
        id_fields=["gem_id"],
    )


def test_e2e_normalisation_excludes_reference():
    row = {
        "gem_id": "e2e-test-1",
        "gem_parent_id": "e2e-parent-1",
        "meaning_representation": "name[The Eagle], area[riverside]",
        "target": "The Eagle is in the riverside area.",
        "references": ["The Eagle is by the river."],
    }

    example = normalise_row(row, e2e_config(), 0)

    assert example.source_payload == {
        "meaning_representation": "name[The Eagle], area[riverside]"
    }
    assert "The Eagle is by the river." not in example.source_text
    assert len(example.references) == 2
    assert example.parent_table == [["name", "The Eagle"], ["area", "riverside"]]


def test_single_agent_baseline_prompt_excludes_references():
    example = BenchmarkExample(
        dataset_id="sportsett_basketball",
        example_id="fixture-1",
        task_family=TaskFamily.EVENT_REPORT,
        output_mode=OutputMode.MULTI_PARAGRAPH_REPORT,
        language="en",
        source_payload={"winner": "Home", "score": "10-8"},
        source_text='{"winner":"Home","score":"10-8"}',
        references=["Home won by two points."],
        request="Write a short event report.",
        source_sha256="source",
        reference_sha256="reference",
    )

    messages = build_single_agent_prompt(example)
    prompt_text = "\n".join(message["content"] for message in messages)

    assert '{"winner":"Home","score":"10-8"}' in prompt_text
    assert "Write a short event report." in prompt_text
    assert "Home won by two points." not in prompt_text
    assert "Dataset ID" not in prompt_text
    assert "Example ID" not in prompt_text
    assert "sportsett_basketball" not in prompt_text
    assert "fixture-1" not in prompt_text
    assert "Task type: event report" in prompt_text
    assert "Expected form: multi paragraph report" in prompt_text


def test_single_agent_generic_prompt_excludes_task_metadata():
    example = BenchmarkExample(
        dataset_id="sportsett_basketball",
        example_id="fixture-1",
        task_family=TaskFamily.EVENT_REPORT,
        output_mode=OutputMode.MULTI_PARAGRAPH_REPORT,
        language="en",
        source_payload={"winner": "Home", "score": "10-8"},
        source_text='{"winner":"Home","score":"10-8"}',
        references=["Home won by two points."],
        request="Understand the supplied data and report its strongest supported findings.",
        source_sha256="source",
        reference_sha256="reference",
    )

    messages = build_single_agent_prompt(example, prompt_style="generic")
    prompt_text = "\n".join(message["content"] for message in messages)

    assert '{"winner":"Home","score":"10-8"}' in prompt_text
    assert "Understand the supplied data" in prompt_text
    assert "Home won by two points." not in prompt_text
    assert "Task type:" not in prompt_text
    assert "Expected form:" not in prompt_text
    assert "Language:" not in prompt_text
    assert "sportsett_basketball" not in prompt_text
    assert "fixture-1" not in prompt_text


def test_event_benchmark_uses_reference_recap_focus_scope():
    assert focus_scope_for_task(TaskFamily.EVENT_REPORT) == "reference_recap"
    assert (
        focus_scope_for_task(TaskFamily.CROSS_LINGUAL_EVENT_REPORT)
        == "reference_recap"
    )


def test_reference_recap_contract_removes_visible_report_scaffolding():
    contract = task_contract_fields(
        genre=ReportGenre.EVENT_REPORT,
        communication_task=CommunicationTask.EVENT_REPORT,
        output_form=WorkflowOutputForm.MULTI_PARAGRAPH_REPORT,
        focus_scope="reference_recap",
    )

    assert contract["allow_headings"] is False
    assert contract["preferred_sections"] == []
    assert "scope_limitations" not in contract["required_content_slots"]
    assert "markdown_headings" in contract["prohibited_claim_types"]


def test_event_source_context_normalizes_structured_source_without_reference():
    source = {
        "game": {
            "stadium": "Wells Fargo Center",
            "dayname": "Sunday",
        },
        "teams": {
            "home": {
                "name": "76ers",
                "place": "Philadelphia",
                "line_score": {
                    "Q1": {"PTS": "26"},
                    "game": {"PTS": "103", "TREB": "44"},
                },
                "box_score": [
                    {"name": "J.J. Redick", "PTS": "24", "FGM": "9"},
                ],
            },
            "vis": {
                "name": "Grizzlies",
                "place": "Memphis",
                "line_score": {
                    "Q1": {"PTS": "25"},
                    "game": {"PTS": "95", "TREB": "35"},
                },
                "box_score": [
                    {"name": "Mike Conley", "PTS": "21", "AST": "5"},
                ],
            },
        },
    }
    record = GenerationRecord(
        generation_id="g1",
        dataset_id="event_fixture",
        example_id="1",
        variant_id="full_system",
        repetition=0,
        seed=42,
        task_family=TaskFamily.EVENT_REPORT,
        output_mode=OutputMode.MULTI_PARAGRAPH_REPORT,
        language="en",
        source_text=json.dumps(source),
        references=["A held-out human reference that must not be copied."],
        parent_table=None,
        request="Write an event report.",
        generated_text="Philadelphia defeated Memphis 103-95.",
        backend=GenerationBackend.TABLE2TEXT,
    )

    context = normalized_event_source_context(record)

    assert context is not None
    assert "Event result: Philadelphia scored 103 and Memphis scored 95" in context
    assert "Wells Fargo Center" in context
    assert "Record for J.J. Redick" in context
    assert "held-out human reference" not in context

    config = ReferenceMetricConfig(
        enabled_metrics=["hhem"],
        external_factuality_context="source_text",
    )
    assert factuality_context(record, config) == context


def test_attribute_verbalisation_materialises_structured_record(
    tmp_path: Path,
):
    row = {
        "gem_id": "e2e-test-1",
        "meaning_representation": (
            "name[Clowns], eatType[pub], customer rating[5 out of 5], "
            "near[Crowne Plaza Hotel]"
        ),
        "target": (
            "The pub Clowns is near Crowne Plaza Hotel and has a customer "
            "rating of 5 out of 5."
        ),
    }
    example = normalise_row(row, e2e_config(), 0)
    input_path = materialise_input(example, tmp_path / "inputs")
    bundle = load_data([input_path])
    table = next(iter(bundle.tables.values()))

    assert {"attribute_name", "attribute_value"}.issubset(table.columns)
    assert table["attribute_name"].tolist() == [
        "name",
        "eatType",
        "customer rating",
        "near",
    ]
    assert table["attribute_value"].tolist() == [
        "Clowns",
        "pub",
        "5 out of 5",
        "Crowne Plaza Hotel",
    ]


def test_generic_contract_inference_uses_source_structure_not_benchmark_labels():
    input_structure = InputStructureProfile(
        shape=InputShape.NESTED_RECORD,
        representation_status=InputRepresentationStatus.VALID,
        row_semantics="one record",
        confidence=0.95,
    )
    decision = infer_task_contract(
        request=(
            "Understand the supplied data and report its strongest supported "
            "findings."
        ),
        structured_inputs={
            "input": {
                "__table2text_benchmark_example__": True,
                "dataset_id": "misleading_event_name",
                "task_family": "event_report",
                "output_mode": "multi_paragraph_report",
                "source_payload": {
                    "meaning_representation": "name[Clowns], eatType[pub]",
                },
            }
        },
        input_structure=input_structure,
    )

    assert decision.communication_task == CommunicationTask.ATTRIBUTE_VERBALISATION
    assert decision.output_form == WorkflowOutputForm.SHORT_TEXT
    assert decision.report_genre == ReportGenre.DATASET_OVERVIEW
    assert decision.selection_source == ReportSelectionSource.STRUCTURED_INFERENCE
    assert decision.confidence == pytest.approx(0.97)


def test_inferred_evaluation_variant_uses_source_only_and_omits_contract(
    tmp_path: Path,
):
    example = normalise_row(
        {
            "gem_id": "e2e-test-1",
            "meaning_representation": "name[Clowns], eatType[pub]",
            "target": "Clowns is a pub.",
        },
        e2e_config(),
        0,
    )
    variant = VariantConfig(
        variant_id="full_inferred_contract",
        task_contract_mode="inferred",
        request_override=(
            "Understand the supplied data and report its strongest supported "
            "findings."
        ),
    )
    input_path = materialise_input(
        example,
        tmp_path,
        source_only=True,
    )
    payload = json.loads(input_path.read_text(encoding="utf-8"))

    assert payload == example.source_payload
    assert "task_family" not in payload
    assert all(
        value is None
        for value in workflow_contract_for_variant(example, variant).values()
    )


def test_configured_contract_fields_override_inferred_values():
    input_structure = InputStructureProfile(
        shape=InputShape.NESTED_RECORD,
        representation_status=InputRepresentationStatus.VALID,
        row_semantics="one record",
        confidence=0.95,
    )
    inferred = infer_task_contract(
        request="Understand the supplied data.",
        structured_inputs={
            "input": {
                "table": [["Name", "Value"], ["A", "1"]],
                "highlighted_cells": [[1, 1]],
            }
        },
        input_structure=input_structure,
    )
    resolved = resolve_task_contract(
        inferred=inferred,
        selected_genre=ReportGenre.DATASET_OVERVIEW,
        genre_source=ReportSelectionSource.EXPERIMENT_CONFIGURATION,
        genre_confidence=1.0,
        configured_communication_task=CommunicationTask.TRIPLE_VERBALISATION,
        configured_output_form=WorkflowOutputForm.SHORT_TEXT,
        configured_focus_scope=None,
    )

    assert resolved.communication_task == CommunicationTask.TRIPLE_VERBALISATION
    assert resolved.output_form == WorkflowOutputForm.SHORT_TEXT
    assert resolved.focus_scope is None
    assert resolved.confidence == 1.0


@pytest.mark.parametrize(
    ("payload", "expected_task", "expected_form", "expected_text"),
    [
        (
            {
                "meaning_representation": (
                    "name[Clowns], eatType[pub], customer rating[5 out of 5], "
                    "near[Crowne Plaza Hotel]"
                )
            },
            CommunicationTask.ATTRIBUTE_VERBALISATION,
            WorkflowOutputForm.SHORT_TEXT,
            "Clowns",
        ),
        (
            {
                "triples": [
                    ["ALCO_RS-3", "engine", "Four-stroke_engine"],
                    ["ALCO_RS-3", "cylinderCount", "12"],
                ]
            },
            CommunicationTask.TRIPLE_VERBALISATION,
            WorkflowOutputForm.SHORT_TEXT,
            "ALCO RS-3",
        ),
        (
            {
                "table_page_title": "Election",
                "table_section_title": "Results",
                "table": [
                    [
                        {"value": "Candidate", "is_header": True},
                        {"value": "Vote share", "is_header": True},
                    ],
                    [
                        {"value": "Ma Ying-jeou", "is_header": False},
                        {"value": "58.45%", "is_header": False},
                    ],
                ],
                "highlighted_cells": [[1, 1]],
            },
            CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
            WorkflowOutputForm.ONE_SENTENCE,
            "58.45%",
        ),
    ],
)
def test_generic_workflow_infers_short_form_contract_from_source_only(
    tmp_path: Path,
    payload: dict,
    expected_task: CommunicationTask,
    expected_form: WorkflowOutputForm,
    expected_text: str,
):
    input_path = tmp_path / f"{expected_task.value}.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    workflow = Table2TextWorkflow(
        Settings(use_llm=False, output_dir=tmp_path / "runs")
    )

    result = workflow.run_sync(
        inputs=[input_path],
        request=(
            "Understand the supplied data and report its strongest supported "
            "findings."
        ),
        audit_mode=AuditMode.INTERNAL,
    )

    specification = result.execution_plan.report_specification
    assert specification.communication_task == expected_task
    assert specification.output_form == expected_form
    assert specification.selection_source == ReportSelectionSource.STRUCTURED_INFERENCE
    assert expected_text in plain_text(result.final_writer_output.markdown)


def test_attribute_verbalisation_workflow_avoids_dataset_profile(
    tmp_path: Path,
):
    row = {
        "gem_id": "e2e-test-1",
        "meaning_representation": (
            "name[Clowns], eatType[pub], customer rating[5 out of 5], "
            "near[Crowne Plaza Hotel]"
        ),
        "target": (
            "The pub Clowns is near Crowne Plaza Hotel and has a customer "
            "rating of 5 out of 5."
        ),
    }
    example = normalise_row(row, e2e_config(), 0)
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.ATTRIBUTE_VERBALISATION,
        output_form=WorkflowOutputForm.SHORT_TEXT,
    )
    report = plain_text(result.final_writer_output.markdown)

    assert "Clowns" in report
    assert "pub" in report
    assert "Crowne Plaza Hotel" in report
    assert "5 out of 5" in report
    assert "Dataset overview" not in report
    assert "1 rows" not in report
    assert "meaning_representation" not in report
    assert result.final_writer_output.writer_mode == (
        "deterministic_short_form_writer"
    )
    assert result.primary_evaluation_eligible
    assert (
        EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
        in result.execution_plan.selected_capabilities
    )


def test_webnlg_serialized_triples_use_structured_verbalisation(
    tmp_path: Path,
):
    example = normalise_row(
        {
            "gem_id": "webnlg-test-1",
            "input": [
                ["ALCO_RS-3", "engine", "Four-stroke_engine"],
                ["ALCO_RS-3", "cylinderCount", "12"],
                ["ALCO_RS-3", "length", "17068.8 (millimetres)"],
            ],
            "target": (
                "The ALCO RS-3 has a four-stroke engine, 12 cylinders, "
                "and a length of 17068.8 millimetres."
            ),
        },
        webnlg_config(),
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(use_llm=False, output_dir=tmp_path / "runs")
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.TRIPLE_VERBALISATION,
        output_form=WorkflowOutputForm.SHORT_TEXT,
    )
    report = plain_text(result.final_writer_output.markdown)

    assert "ALCO RS-3" in report
    assert "12 cylinders" in report
    assert "17068.8" in report
    assert "millimetres" in report
    assert "seventeen" not in report.casefold()
    assert result.final_writer_output.writer_mode == (
        "deterministic_short_form_writer"
    )
    assert result.primary_evaluation_eligible
    assert (
        EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
        in result.execution_plan.selected_capabilities
    )


def test_dart_rank_triple_uses_ordinal_phrasing(tmp_path: Path):
    example = normalise_row(
        {
            "gem_id": "dart-test-1",
            "tripleset": [
                ["Place A", "RANK", "11"],
                ["Place A", "TOTAL", "211.5"],
            ],
            "target": "Place A ranks 11th and has a total of 211.5.",
        },
        dart_config(),
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(use_llm=False, output_dir=tmp_path / "runs")
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.TRIPLE_VERBALISATION,
        output_form=WorkflowOutputForm.SHORT_TEXT,
    )
    report = plain_text(result.final_writer_output.markdown)

    assert "ranks 11th" in report
    assert "total of 211.5" in report
    assert "eleventh" not in report.casefold()
    assert result.final_writer_output.writer_mode == (
        "deterministic_short_form_writer"
    )
    assert result.primary_evaluation_eligible


def test_multiple_reference_rows_are_merged():
    config = e2e_config()
    first = normalise_row(
        {
            "gem_parent_id": "shared",
            "meaning_representation": "name[A]",
            "target": "A is a venue.",
            "references": [],
        },
        config,
        0,
    )
    second = normalise_row(
        {
            "gem_parent_id": "shared",
            "meaning_representation": "name[A]",
            "target": "The venue is named A.",
            "references": [],
        },
        config,
        1,
    )

    merged = merge_examples([first, second])

    assert len(merged) == 1
    assert merged[0].references == ["A is a venue.", "The venue is named A."]


def test_highlighted_table_examples_materialise_as_cell_table(tmp_path: Path):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Election",
            "table_section_title": "Results",
            "table": [
                [
                    {"value": "Candidate", "is_header": True},
                    {"value": "Vote share", "is_header": True},
                ],
                [
                    {"value": "Ma Ying-jeou", "is_header": False},
                    {"value": "58.45%", "is_header": False},
                ],
            ],
            "highlighted_cells": [[1, 1]],
            "target": "Ma Ying-jeou received 58.45% of the vote.",
        },
        config,
        0,
    )

    input_path = materialise_input(example, tmp_path)
    bundle = load_data([input_path])
    frame = next(iter(bundle.tables.values()))

    assert frame.shape[0] == 4
    assert "cell_value" in frame.columns
    assert "is_highlighted" in frame.columns
    highlighted = frame[frame["is_highlighted"]]
    assert highlighted["cell_value"].tolist() == ["58.45%"]
    assert highlighted["request"].iloc[0] == example.request


def test_highlighted_table_task_uses_focused_one_sentence_contract(tmp_path: Path):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Election",
            "table_section_title": "Results",
            "table": [
                [
                    {"value": "Candidate", "is_header": True},
                    {"value": "Vote share", "is_header": True},
                ],
                [
                    {"value": "Ma Ying-jeou", "is_header": False},
                    {"value": "58.45%", "is_header": False},
                ],
            ],
            "highlighted_cells": [[1, 1]],
            "target": "Ma Ying-jeou received 58.45% of the vote.",
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )

    report = result.final_writer_output.markdown.strip()

    assert "#" not in report
    assert "58.45%" in report
    assert "Ma Ying-jeou" in report
    assert "rows" not in report.lower()
    assert "columns" not in report.lower()
    assert "correlation" not in report.lower()
    assert result.execution_plan.selected_capabilities == [
        EvidenceCapability.FOCUSED_TABLE_REGION
    ]
    assert len(result.execution_plan.insight_objectives) == 1
    assert (
        result.execution_plan.insight_objectives[0].objective_id
        == "INSIGHT_FOCUSED_TABLE_RELATION"
    )
    assert (
        "table-local proposition"
        in result.execution_plan.insight_objectives[0].question
    )
    assert any(
        item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
        for item in result.evidence_ledger.items
    )


def test_highlighted_table_logical_row_context_uses_spans(tmp_path: Path):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Ma Ying-jeou",
            "table_section_title": "Inauguration",
            "table": [
                [
                    {
                        "value": "Party",
                        "is_header": True,
                        "row_span": 2,
                        "column_span": 2,
                    },
                    {
                        "value": "Candidate",
                        "is_header": True,
                        "row_span": 1,
                        "column_span": 2,
                    },
                    {
                        "value": "Votes",
                        "is_header": True,
                        "row_span": 2,
                        "column_span": 1,
                    },
                    {
                        "value": "Percentage",
                        "is_header": True,
                        "row_span": 2,
                        "column_span": 2,
                    },
                ],
                [
                    {
                        "value": "President",
                        "is_header": False,
                        "row_span": 1,
                        "column_span": 1,
                    },
                    {
                        "value": "Vice president",
                        "is_header": False,
                        "row_span": 1,
                        "column_span": 1,
                    },
                ],
                [
                    {"value": "", "is_header": False},
                    {"value": "-", "is_header": False},
                    {"value": "-", "is_header": False},
                    {"value": "Vincent Siew", "is_header": False},
                    {"value": "7,659,014", "is_header": False},
                    {"value": "58.45%", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {"value": "", "is_header": False},
                    {"value": "-", "is_header": False},
                    {"value": "Other candidate", "is_header": False},
                    {"value": "Other running mate", "is_header": False},
                    {"value": "5,444,949", "is_header": False},
                    {"value": "41.55%", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Total",
                        "is_header": False,
                        "column_span": 4,
                    },
                    {"value": "13,103,963", "is_header": False},
                    {
                        "value": "100.00%",
                        "is_header": False,
                        "column_span": 2,
                    },
                ],
            ],
            "highlighted_cells": [[2, 5]],
            "target": "Ma won the presidency by 58.45% of the vote.",
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")
    frame = next(iter(load_data([input_path]).tables.values()))

    president_header = frame[
        (frame["row_index"] == 1)
        & (frame["cell_value"] == "President")
    ].iloc[0]
    vice_header = frame[
        (frame["row_index"] == 1)
        & (frame["cell_value"] == "Vice president")
    ].iloc[0]
    assert int(president_header["column_index"]) == 2
    assert int(vice_header["column_index"]) == 3

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )
    evidence = next(
        item
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    )
    metrics = evidence.metrics

    def has_pair(
        pairs: list[dict[str, object]],
        headers: list[str],
        value: str,
    ) -> bool:
        return any(
            pair.get("headers") == headers
            and pair.get("value") == value
            for pair in pairs
        )

    assert has_pair(
        metrics["highlighted_role_value_pairs"],
        ["Percentage"],
        "58.45%",
    )
    assert result.final_writer_output.writer_mode == (
        "deterministic_short_form_writer"
    )
    assert result.primary_evaluation_eligible
    assert has_pair(
        metrics["logical_row_context"],
        ["Candidate", "Vice president"],
        "Vincent Siew",
    )
    assert has_pair(
        metrics["logical_row_context"],
        ["Votes"],
        "7,659,014",
    )
    assert has_pair(
        metrics["logical_row_placeholders"],
        ["Candidate", "President"],
        "-",
    )
    assert {
        "value": "Ma Ying-jeou",
        "related_headers": ["Candidate", "President"],
        "basis": (
            "page title with placeholder value under this logical header path "
            "in the same row"
        ),
    } in metrics["page_title_subject_candidates"]
    comparison = metrics["highlighted_measure_comparisons"][0]
    assert comparison["highlighted_value"] == "58.45%"
    assert comparison["headers"] == ["Percentage"]
    assert comparison["rank_descending"] == 1
    assert comparison["comparable_value_count"] == 2
    assert comparison["is_highest_comparable_value"] is True
    assert comparison["is_majority_percentage"] is True
    assert comparison["excluded_aggregate_values"][0]["value"] == "100.00%"


def test_rectangular_table_does_not_use_previous_data_rows_as_headers(
    tmp_path: Path,
):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "List of offices",
            "table_section_title": "Office holders",
            "table": [
                [
                    {"value": "#", "is_header": True},
                    {"value": "Name", "is_header": True},
                    {"value": "Start", "is_header": True},
                    {"value": "End", "is_header": True},
                ],
                [
                    {"value": "1", "is_header": True},
                    {"value": "Alice Example", "is_header": False},
                    {"value": "1 January 2001", "is_header": False},
                    {"value": "2 January 2002", "is_header": False},
                ],
                [
                    {"value": "2", "is_header": True},
                    {"value": "Bob Example", "is_header": False},
                    {"value": "3 January 2003", "is_header": False},
                    {"value": "4 January 2004", "is_header": False},
                ],
            ],
            "highlighted_cells": [[2, 1], [2, 2], [2, 3]],
            "target": "Bob Example held the office from 2003 to 2004.",
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )
    evidence = next(
        item
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    )
    highlighted_pairs = evidence.metrics["highlighted_role_value_pairs"]

    assert evidence.metrics["page_title_subject_candidates"] == []
    assert evidence.metrics["concise_output_focus"][
        "primary_subject_candidates"
    ] == []
    assert result.fact_ledger.writer_ready_facts
    assert {
        "headers": ["Name"],
        "value": "Bob Example",
        "column_index": 1,
    } in highlighted_pairs
    assert {
        "headers": ["Start"],
        "value": "3 January 2003",
        "column_index": 2,
    } in highlighted_pairs
    assert {
        "headers": ["End"],
        "value": "4 January 2004",
        "column_index": 3,
    } in highlighted_pairs
    assert all(
        "Alice Example" not in pair["headers"]
        for pair in highlighted_pairs
    )


def test_highlighted_table_numeric_header_supports_fact_summary(
    tmp_path: Path,
):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Tax table",
            "table_section_title": "Rates",
            "table": [
                [
                    {"value": "Country", "is_header": True},
                    {
                        "value": "Corporate income tax rate (2016)",
                        "is_header": True,
                    },
                    {
                        "value": "Combined corporate tax rate (2016)",
                        "is_header": True,
                    },
                ],
                [
                    {"value": "France", "is_header": False},
                    {"value": "34.43%", "is_header": False},
                    {"value": "34.43%", "is_header": False},
                ],
                [
                    {"value": "Switzerland", "is_header": False},
                    {"value": "8.50%", "is_header": False},
                    {"value": "21.15%", "is_header": False},
                ],
            ],
            "highlighted_cells": [[1, 0], [1, 1], [2, 0], [2, 1]],
            "target": (
                "France had a 34.43% corporate income tax rate, while "
                "Switzerland had an 8.50% rate."
            ),
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )

    assert result.fact_ledger.writer_ready_facts
    fact = result.fact_ledger.writer_ready_facts[0]
    assert "Corporate income tax rate (2016)" in fact.fact_summary
    assert "34.43%" in fact.fact_summary
    assert "8.50%" in fact.fact_summary
    assert "# Evidence-grounded data-science report" not in (
        result.final_writer_output.markdown.strip()
    )


def test_irregular_highlighted_table_context_ignores_placeholders(tmp_path: Path):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Election page",
            "table_section_title": "Results",
            "table": [
                [
                    {"value": "Party", "is_header": True},
                    {"value": "Candidate", "is_header": True},
                    {"value": "Votes", "is_header": True},
                    {"value": "Percentage", "is_header": True},
                ],
                [
                    {"value": "President", "is_header": True},
                    {"value": "Vice president", "is_header": True},
                ],
                [
                    {"value": "", "is_header": False},
                    {"value": "-", "is_header": False},
                    {"value": "-", "is_header": False},
                    {"value": "Named candidate", "is_header": False},
                    {"value": "7,659,014", "is_header": False},
                    {"value": "58.45%", "is_header": False},
                    {"value": "", "is_header": False},
                ],
            ],
            "highlighted_cells": [[2, 5]],
            "target": "The highlighted value is 58.45%.",
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )

    evidence = next(
        item
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    )
    report = result.final_writer_output.markdown.strip()

    assert evidence.metrics["row_context"] == [
        "Named candidate",
        "7,659,014",
    ]
    assert evidence.metrics["header_context"][0] == "Percentage"
    assert "58.45%" in report
    assert "Named candidate" in report
    assert "Percentage" in report
    assert " for Party" not in report
    assert not report.startswith("-")


def test_focused_table_relation_insight_can_be_verified_without_implication(
    tmp_path: Path,
):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Election page",
            "table_section_title": "Results",
            "table": [
                [
                    {"value": "Candidate", "is_header": True},
                    {"value": "Vote share", "is_header": True},
                ],
                [
                    {"value": "Candidate A", "is_header": False},
                    {"value": "58.45%", "is_header": False},
                ],
            ],
            "highlighted_cells": [[1, 1]],
            "target": "Candidate A had 58.45% of the vote.",
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")
    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )
    fact_ids = [
        fact.fact_id
        for fact in result.fact_ledger.writer_ready_facts
        if EvidenceCapability.FOCUSED_TABLE_REGION in fact.source_capabilities
    ]
    evidence_ids = [
        item.evidence_id
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    ]

    ledger = materialise_insight_ledger(
        candidates=InsightCandidateSet(
            candidates=[
                InsightCandidate(
                    insight_id="INSIGHT_FOCUSED_001",
                    statement=(
                        "Candidate A had 58.45% of the vote in the "
                        "Election page table."
                    ),
                    insight_type=InsightType.NARRATIVE_SUMMARY,
                    interpretation_level=InterpretationLevel.FINDING,
                    contribution=InsightContribution.DESCRIPTIVE_SYNTHESIS,
                    source_fact_ids=fact_ids,
                    source_evidence_ids=evidence_ids,
                    supporting_summary=(
                        "The highlighted focused-table evidence supplies the "
                        "value, row context, header and table context."
                    ),
                    claim_permissions=[ClaimPermission.DESCRIPTIVE],
                    confidence=0.95,
                    salience=0.95,
                )
            ]
        ),
        verification=InsightVerificationResult(
            records=[
                InsightVerificationRecord(
                    insight_id="INSIGHT_FOCUSED_001",
                    status=InsightVerificationStatus.VERIFIED,
                    confidence=0.95,
                    salience=0.95,
                    adds_bounded_synthesis=False,
                    analytical_implication_supported=False,
                    contains_hypothesis=False,
                )
            ]
        ),
        fact_ledger=result.fact_ledger,
        evidence_ledger=result.evidence_ledger,
        settings=Settings(),
        report_genre=ReportGenre.DATASET_OVERVIEW,
    )

    assert [insight.insight_id for insight in ledger.verified_insights] == [
        "INSIGHT_FOCUSED_001"
    ]
    assert (
        ledger.verified_insights[0].interpretation_level
        == InterpretationLevel.BOUNDED_INSIGHT
    )


def test_focused_table_highlighted_set_contrast_is_scoped_locally(
    tmp_path: Path,
):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Corporate tax",
            "table_section_title": "International corporate tax rates",
            "table": [
                [
                    {"value": "Country", "is_header": True},
                    {
                        "value": "Corporate income tax rate (2016)",
                        "is_header": True,
                    },
                ],
                [
                    {"value": "France", "is_header": False},
                    {"value": "34.43%", "is_header": False},
                ],
                [
                    {"value": "Switzerland", "is_header": False},
                    {"value": "8.50%", "is_header": False},
                ],
                [
                    {"value": "United States", "is_header": False},
                    {"value": "35.00%", "is_header": False},
                ],
            ],
            "highlighted_cells": [[1, 0], [1, 1], [2, 0], [2, 1]],
            "target": (
                "Among the highlighted countries, Switzerland had the lower "
                "corporate tax rate and France had the higher rate."
            ),
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")
    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )
    evidence = next(
        item
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    )
    contrast = evidence.metrics["highlighted_set_contrasts"][0]

    assert contrast["scope"] == "highlighted_values_only"
    assert contrast["measure_headers"] == [
        "Corporate income tax rate (2016)"
    ]
    assert contrast["lower"]["subject"] == "Switzerland"
    assert contrast["lower"]["value"] == "8.50%"
    assert contrast["higher"]["subject"] == "France"
    assert contrast["higher"]["value"] == "34.43%"
    assert "Among the highlighted countries" in contrast["contrast_summary"]

    report = plain_text(result.final_writer_output.markdown)
    assert "Switzerland" in report
    assert "lower" in report
    assert "France" in report
    assert "higher" in report
    assert "United States" not in report


def test_focused_table_uses_raw_highlight_coordinates_with_colspan(
    tmp_path: Path,
):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Ernest Burton (American football)",
            "table_section_title": "Head coaching record",
            "table": [
                [
                    {"value": "Year", "is_header": True},
                    {"value": "Team", "is_header": True},
                    {"value": "Overall", "is_header": True},
                    {"value": "Conference", "is_header": True},
                    {"value": "Standing", "is_header": True},
                    {"value": "Bowl/playoffs", "is_header": True},
                ],
                [
                    {
                        "value": (
                            "Maine Black Bears "
                            "(Maine Intercollegiate Athletic Association) "
                            "(1900)"
                        ),
                        "is_header": False,
                        "column_span": 9,
                    },
                ],
                [
                    {"value": "1900", "is_header": False},
                    {"value": "Maine", "is_header": False},
                    {"value": "4–4", "is_header": False},
                    {"value": "", "is_header": False},
                    {"value": "", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Maine:",
                        "is_header": False,
                        "column_span": 2,
                    },
                    {"value": "4–4", "is_header": False},
                    {"value": "", "is_header": False},
                    {"value": "", "is_header": False, "column_span": 5},
                ],
                [
                    {
                        "value": "Total:",
                        "is_header": False,
                        "column_span": 2,
                    },
                    {"value": "4–4", "is_header": False},
                    {"value": "", "is_header": False, "column_span": 7},
                ],
            ],
            "highlighted_cells": [[1, 0], [4, 1]],
            "target": (
                "C. Ernest Burton was the head coach of Maine's football "
                "team in 1900 and compiled a 4–4 record."
            ),
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")
    frame = next(iter(load_data([input_path]).tables.values()))
    highlighted_values = frame[
        frame["is_highlighted"].fillna(False).astype(bool)
    ]["cell_value"].tolist()

    assert highlighted_values == [
        "Maine Black Bears (Maine Intercollegiate Athletic Association) (1900)",
        "4–4",
    ]
    assert "Total:" not in highlighted_values

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )
    evidence = next(
        item
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    )
    relation = evidence.metrics["focused_record_relation"]
    report = plain_text(result.final_writer_output.markdown)

    assert relation["compact_group_label"] == "Maine Black Bears"
    assert relation["year"] == "1900"
    assert relation["value"] == "4–4"
    assert "Ernest Burton" in report
    assert "Maine Black Bears" in report
    assert "1900" in report
    assert "4–4" in report
    assert "Total:" not in report


def test_focused_table_list_page_uses_structural_header_not_previous_rows(
    tmp_path: Path,
):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": (
                "List of NWA/WCW closed-circuit events and "
                "pay-per-view events"
            ),
            "table_section_title": "1993",
            "table": [
                [
                    {"value": "Date", "is_header": True},
                    {"value": "Event", "is_header": True},
                    {"value": "Venue", "is_header": True},
                    {"value": "Location", "is_header": True},
                    {"value": "Main event", "is_header": True},
                ],
                [
                    {"value": "February 21", "is_header": False},
                    {"value": "SuperBrawl III", "is_header": False},
                    {"value": "Asheville Civic Center", "is_header": False},
                    {
                        "value": "Asheville, North Carolina",
                        "is_header": False,
                    },
                    {"value": "Big Van Vader vs. Sting", "is_header": False},
                ],
                [
                    {"value": "December 27", "is_header": False},
                    {"value": "Starrcade", "is_header": False},
                    {"value": "Independence Arena", "is_header": False},
                    {
                        "value": "Charlotte, North Carolina",
                        "is_header": False,
                    },
                    {
                        "value": "Big Van Vader vs. Ric Flair",
                        "is_header": False,
                    },
                ],
            ],
            "highlighted_cells": [[2, 1]],
            "target": (
                "In 1993, Starrcade was a pay-per-view event by World "
                "Championship Wrestling."
            ),
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )
    evidence = next(
        item
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    )
    highlighted_pairs = evidence.metrics["highlighted_role_value_pairs"]
    relation = evidence.metrics["focused_list_relation"]
    report = plain_text(result.final_writer_output.markdown)

    assert highlighted_pairs == [
        {
            "headers": ["Event"],
            "value": "Starrcade",
            "column_index": 1,
        }
    ]
    assert relation["value"] == "Starrcade"
    assert relation["section_title"] == "1993"
    assert relation["member_category"] == "pay-per-view event"
    assert "Starrcade" in report
    assert "1993" in report
    assert "pay-per-view event" in report
    assert "SuperBrawl" not in report
    assert not report.endswith("vs.")


def test_focused_table_preserves_grouped_highlighted_records_with_rowspans(
    tmp_path: Path,
):
    config = DatasetConfig(
        dataset_id="totto",
        source=DatasetSource.HUGGINGFACE,
        hub_id="fixture",
        normalizer="totto",
        task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        output_mode=OutputMode.ONE_SENTENCE,
        reference_fields=["target"],
    )
    example = normalise_row(
        {
            "table_page_title": "Ryan Hart",
            "table_section_title": "Some Achievements",
            "table": [
                [
                    {"value": "Tournament", "is_header": True},
                    {"value": "Game", "is_header": True},
                    {"value": "Place", "is_header": True},
                    {"value": "Note", "is_header": True},
                ],
                [
                    {
                        "value": "Hypespotting",
                        "is_header": False,
                        "row_span": 2,
                    },
                    {
                        "value": "Super Street Fighter IV: Arcade Edition",
                        "is_header": False,
                    },
                    {"value": "1st", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Street Fighter III: 3rd Strike",
                        "is_header": False,
                    },
                    {"value": "2nd", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Stunfest 2012",
                        "is_header": False,
                        "row_span": 2,
                    },
                    {
                        "value": "Super Street Fighter IV: Arcade Edition",
                        "is_header": False,
                    },
                    {"value": "4th", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Street Fighter X Tekken",
                        "is_header": False,
                    },
                    {"value": "1st", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Cross Up Gamerbase #3",
                        "is_header": False,
                    },
                    {
                        "value": "Street Fighter X Tekken",
                        "is_header": False,
                    },
                    {"value": "1st", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Cross Up Gamerbase #2",
                        "is_header": False,
                    },
                    {
                        "value": "Street Fighter X Tekken",
                        "is_header": False,
                    },
                    {"value": "1st", "is_header": False},
                    {"value": "", "is_header": False},
                ],
                [
                    {
                        "value": "Cross Up Gamerbase",
                        "is_header": False,
                    },
                    {
                        "value": "Street Fighter X Tekken",
                        "is_header": False,
                    },
                    {"value": "1st", "is_header": False},
                    {"value": "", "is_header": False},
                ],
            ],
            "highlighted_cells": [
                [1, 0],
                [2, 0],
                [2, 1],
                [3, 0],
                [4, 0],
                [4, 1],
                [5, 0],
                [5, 2],
                [6, 0],
                [6, 2],
                [7, 0],
                [7, 2],
            ],
            "target": (
                "Hart placed 2nd in Street Fighter III: 3rd Strike at "
                "Hypespotting, placing 1st in Street Fighter X Tekken at "
                "Stunfest 2012, and won three times in a row in Cross Up "
                "tournament."
            ),
        },
        config,
        0,
    )
    input_path = materialise_input(example, tmp_path / "inputs")

    workflow = Table2TextWorkflow(
        Settings(
            use_llm=False,
            output_dir=tmp_path / "runs",
        )
    )
    result = workflow.run_sync(
        inputs=[input_path],
        request=example.request,
        audit_mode=AuditMode.INTERNAL,
        report_genre=ReportGenre.DATASET_OVERVIEW,
        communication_task=CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
        output_form=WorkflowOutputForm.ONE_SENTENCE,
        focus_scope="highlighted_cells",
    )
    evidence = next(
        item
        for item in result.evidence_ledger.items
        if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
    )
    summary = evidence.metrics["highlighted_record_group_summary"]
    records = evidence.metrics["highlighted_record_groups"]
    report = plain_text(result.final_writer_output.markdown)

    assert len(records) == 5
    assert len(evidence.metrics["highlighted_role_value_pairs"]) == 9
    assert "Hypespotting" in summary
    assert "Stunfest 2012" in summary
    assert "Cross Up Gamerbase" in summary
    assert "three times in a row in Street Fighter X Tekken" in summary
    assert "Hypespotting" in report
    assert "Stunfest 2012" in report
    assert "Cross Up Gamerbase" in report


def generation(*, variant: str, text: str) -> GenerationRecord:
    return GenerationRecord(
        generation_id=f"dataset__1__{variant}__r0__s42",
        dataset_id="dataset",
        example_id="1",
        variant_id=variant,
        repetition=0,
        seed=42,
        task_family=TaskFamily.ATTRIBUTE_VERBALISATION,
        output_mode=OutputMode.SHORT_TEXT,
        language="en",
        source_text="name[A], area[riverside]",
        references=["A is located by the riverside."],
        parent_table=[["name", "A"], ["area", "riverside"]],
        request="Write one sentence.",
        generated_text=text,
        backend=GenerationBackend.PRECOMPUTED,
        primary_evaluation_eligible=True,
    )


def test_plain_text_removes_markdown_heading():
    assert plain_text("# Report\n\n**A result.**") == "Report A result."


def test_deepeval_input_includes_focused_table_task_guidance():
    record = generation(
        variant="full",
        text="Ma Ying-jeou received 58.45% of the vote.",
    ).model_copy(
        update={
            "dataset_id": "totto",
            "task_family": TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
            "output_mode": OutputMode.ONE_SENTENCE,
            "source_text": (
                "page_title: Ma Ying-jeou\n"
                "section_title: Inauguration\n"
                "row: Ma Ying-jeou | Vincent Siew | 7,659,014 | 58.45%"
            ),
            "request": "Describe the highlighted table region.",
        }
    )

    judge_input = input_for_judge(record, DeepEvalConfig())

    assert "focused-table task" in judge_input
    assert "table-local proposition" in judge_input
    assert "row co-entity" in judge_input
    assert "Ma Ying-jeou" in judge_input


def test_openai_annotation_judge_input_uses_source_output_and_taxonomy_only():
    record = generation(
        variant="full",
        text="Ma Ying-jeou received 58.45% of the vote.",
    ).model_copy(
        update={
            "dataset_id": "totto",
            "task_family": TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
            "output_mode": OutputMode.ONE_SENTENCE,
            "source_text": (
                "page_title: Ma Ying-jeou\n"
                "section_title: Inauguration\n"
                "row: Ma Ying-jeou | Vincent Siew | 7,659,014 | 58.45%"
            ),
            "request": "Describe the highlighted table region.",
            "references": ["Ma won the presidency by 58.45% of the vote."],
        }
    )

    judge_input = build_annotation_judge_input(
        record,
        OpenAIJudgeAnnotationConfig(),
    )

    assert "SOURCE DATA" in judge_input
    assert "GENERATED OUTPUT" in judge_input
    assert "ERROR TAXONOMY" in judge_input
    assert "NAME" in judge_input
    assert "NUMBER" in judge_input
    assert "NOT CHECKABLE" in judge_input
    assert "HUMAN REFERENCES" not in judge_input
    assert "Ma won the presidency" not in judge_input


def test_reference_metrics_score_identical_text(tmp_path: Path):
    record = generation(variant="full", text="A is located by the riverside.")

    observations = evaluate_reference_metrics(
        [record],
        ReferenceMetricConfig(enabled_metrics=["bleu", "rougeL", "chrf"]),
        tmp_path / "metrics.jsonl",
    )
    scored = {
        item.metric_name: item.score
        for item in observations
        if item.status.value == "scored"
    }

    assert scored["rougeL"] == 1.0
    assert scored["chrf"] > 0.99
    assert scored["bleu"] > 0.99


def test_reference_metrics_can_include_ineligible_generations_for_smoke_tests(
    tmp_path: Path,
):
    record = generation(
        variant="full",
        text="A is located by the riverside.",
    ).model_copy(
        update={
            "primary_evaluation_eligible": False,
            "primary_evaluation_reason": "deterministic fallback",
        }
    )

    default_observations = evaluate_reference_metrics(
        [record],
        ReferenceMetricConfig(enabled_metrics=["rougeL"]),
        tmp_path / "default_metrics.jsonl",
    )
    assert default_observations[0].status.value == "skipped"

    smoke_observations = evaluate_reference_metrics(
        [record],
        ReferenceMetricConfig(enabled_metrics=["rougeL"]),
        tmp_path / "smoke_metrics.jsonl",
        include_ineligible=True,
    )
    scored = [
        item
        for item in smoke_observations
        if item.metric_name == "rougeL"
        and item.status.value == "scored"
    ]

    assert scored
    assert scored[0].score == 1.0


def test_hhem_metric_records_sentence_level_support(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    record = generation(
        variant="full",
        text="A is located by the riverside. It has outdoor seating.",
    )

    class FakeHHEMEvaluator:
        def __init__(self, **_: object) -> None:
            pass

        def evaluate(self, *, context: str, generated_text: str) -> ExternalFactualityResult:
            assert "A is located by the riverside" in context
            assert "outdoor seating" in generated_text
            return ExternalFactualityResult(
                metric_name="hhem_2_1_open",
                status="scored",
                overall_score=0.6,
                sentence_scores=[0.9, 0.3],
                minimum_sentence_score=0.3,
                unsupported_sentence_rate=0.5,
                threshold=0.5,
                details={"sentence_count": 2},
            )

    monkeypatch.setattr(
        reference_metrics_module,
        "HHEMEvaluator",
        FakeHHEMEvaluator,
    )

    observations = evaluate_reference_metrics(
        [record],
        ReferenceMetricConfig(enabled_metrics=["hhem"]),
        tmp_path / "hhem_metrics.jsonl",
    )
    scored = {
        item.metric_name: item
        for item in observations
        if item.status.value == "scored"
    }

    assert scored["hhem_2_1_open_mean_support"].score == 0.6
    assert scored["hhem_2_1_open_min_sentence_support"].score == 0.3
    assert scored["hhem_2_1_open_unsupported_sentence_rate"].score == 0.5
    assert scored["hhem_2_1_open_unsupported_sentence_rate"].higher_is_better is False
    assert scored["hhem_2_1_open_mean_support"].details["sentence_scores"] == [0.9, 0.3]


def test_alignscore_metric_is_unavailable_without_worker_python(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    record = generation(variant="full", text="A is located by the riverside.")
    monkeypatch.setattr(
        reference_metrics_module,
        "default_alignscore_python_executable",
        lambda: None,
    )

    observations = evaluate_reference_metrics(
        [record],
        ReferenceMetricConfig(enabled_metrics=["alignscore"]),
        tmp_path / "alignscore_metrics.jsonl",
    )

    assert len(observations) == 1
    assert observations[0].metric_name == "alignscore_base"
    assert observations[0].status.value == "unavailable"
    assert "alignscore_python_executable" in str(observations[0].error)


def test_numeric_diagnostics():
    result = number_diagnostics(
        "The result was 111-95.",
        "Home scored 111 and visitors scored 95.",
        ["The home team won 111 to 95."],
    )

    assert result["generated_number_source_precision"] == 1.0


def test_human_pair_order_is_deterministic():
    first = generation(variant="baseline", text="A is riverside.")
    second = generation(variant="full", text="A is located by the riverside.")

    pairs_one = make_blinded_pairs([first, second], seed=42)
    pairs_two = make_blinded_pairs([first, second], seed=42)

    assert pairs_one[0].model_dump() == pairs_two[0].model_dump()


def test_paired_bootstrap_positive_difference():
    result = paired_bootstrap(
        baseline=pd.Series([0.1, 0.2, 0.3]).to_numpy(),
        candidate=pd.Series([0.3, 0.4, 0.5]).to_numpy(),
        resamples=1000,
        confidence_level=0.95,
        seed=42,
    )

    assert result["mean_difference"] > 0
    assert result["probability_candidate_better"] > 0.95


@pytest.mark.asyncio
async def test_notebook_helpers_generate_from_precomputed_variant(tmp_path: Path):
    paths = init_notebook_evaluation(tmp_path)
    example = normalise_row(
        {
            "gem_parent_id": "notebook-example",
            "meaning_representation": "name[A]",
            "target": "A is a venue.",
        },
        e2e_config(),
        0,
    )
    examples_path = tmp_path / "examples.jsonl"
    precomputed_path = tmp_path / "precomputed.jsonl"
    variants_path = tmp_path / "variants.json"
    output_path = tmp_path / "generations.jsonl"

    examples_path.write_text(
        json.dumps(example.model_dump(mode="json"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    precomputed = generation(variant="precomputed_full", text="A is a venue.").model_copy(
        update={
            "dataset_id": example.dataset_id,
            "example_id": example.example_id,
            "generation_id": (
                f"{example.dataset_id}__{example.example_id}__"
                "precomputed_full__r0__s42"
            ),
        }
    )
    precomputed_path.write_text(
        json.dumps(precomputed.model_dump(mode="json"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    variants_path.write_text(
        json.dumps(
            {
                "variants": [
                    {
                        "variant_id": "precomputed_full",
                        "backend": "precomputed",
                        "precomputed_path": str(precomputed_path),
                        "repetitions": 1,
                        "seeds": [42],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    frame = await generate_reports_for_notebook(
        tmp_path,
        examples_path=examples_path,
        variants_path=variants_path,
        output_path=output_path,
        run_root=paths["run_root"],
    )

    assert len(frame) == 1
    assert frame.loc[0, "generated_text"] == "A is a venue."
