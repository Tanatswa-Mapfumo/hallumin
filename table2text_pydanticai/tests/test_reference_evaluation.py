from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from table2text.data import load_data
from table2text.evaluation.datasets import merge_examples, normalise_row
from table2text.evaluation.diagnostics import number_diagnostics
from table2text.evaluation.generation import materialise_input
from table2text.evaluation.human_evaluation import make_blinded_pairs
from table2text.evaluation.models import (
    DatasetConfig,
    DatasetSource,
    GenerationBackend,
    GenerationRecord,
    OutputMode,
    ReferenceMetricConfig,
    TaskFamily,
)
from table2text.evaluation.notebook import (
    generate_reports_for_notebook,
    init_notebook_evaluation,
)
from table2text.evaluation.reference_metrics import evaluate_reference_metrics, plain_text
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
