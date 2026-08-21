"""Notebook-friendly wrappers around the evaluation framework."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from .cli import write_default_metrics, write_default_variants
from table2text.config import load_env_files
from .datasets import (
    load_dataset_configs,
    prepare_datasets,
    read_examples,
    save_default_dataset_configs,
)
from .diagnostics import write_diagnostics
from .deepeval_metrics import evaluate_deepeval
from .generation import generate_all_async, load_variants, read_generations
from .llm_judge_annotations import (
    OpenAIJudgeAnnotationConfig,
    annotate_generations_with_openai_judge,
)
from .models import ExperimentConfig
from .reference_metrics import evaluate_reference_metrics
from .statistics import write_analysis


def default_paths(project_dir: Path) -> dict[str, Path]:
    project_dir = Path(project_dir)
    return {
        "dataset_config": project_dir / "evaluation/config/datasets.json",
        "variant_config": project_dir / "evaluation/config/variants.json",
        "metric_config": project_dir / "evaluation/config/metrics.json",
        "prepared_examples": project_dir / "evaluation/prepared/all_examples.jsonl",
        "generations": project_dir / "evaluation/generations/generations.jsonl",
        "run_root": project_dir / "evaluation/generations/runs",
        "reference_metrics": project_dir / "evaluation/results/reference_metrics.jsonl",
        "deepeval_metrics": project_dir / "evaluation/results/deepeval_metrics.jsonl",
        "llm_judge_annotations": project_dir
        / "evaluation/results/llm_judge_annotations.jsonl",
        "diagnostics": project_dir / "evaluation/results/diagnostics.csv",
        "analysis": project_dir / "evaluation/results/analysis",
    }


def load_project_env(project_dir: Path) -> None:
    project_dir = Path(project_dir)
    load_env_files(
        [
            project_dir.parent / ".env",
            project_dir / ".env",
            project_dir.parent / ".env.local",
            project_dir / ".env.local",
        ]
    )


def init_notebook_evaluation(project_dir: Path) -> dict[str, Path]:
    paths = default_paths(project_dir)
    save_default_dataset_configs(paths["dataset_config"])
    write_default_variants(paths["variant_config"])
    write_default_metrics(paths["metric_config"])
    for key in ("prepared_examples", "generations", "reference_metrics", "diagnostics"):
        paths[key].parent.mkdir(parents=True, exist_ok=True)
    paths["analysis"].mkdir(parents=True, exist_ok=True)
    return paths


def prepare_examples_for_notebook(
    project_dir: Path,
    *,
    dataset_config_path: Path | None = None,
    output_directory: Path | None = None,
    skip_unavailable: bool = True,
) -> pd.DataFrame:
    paths = default_paths(project_dir)
    statuses = prepare_datasets(
        load_dataset_configs(dataset_config_path or paths["dataset_config"]),
        output_directory or paths["prepared_examples"].parent,
        skip_unavailable=skip_unavailable,
    )
    return pd.DataFrame([status.model_dump(mode="json") for status in statuses])


async def generate_reports_for_notebook(
    project_dir: Path,
    *,
    examples_path: Path | None = None,
    variants_path: Path | None = None,
    output_path: Path | None = None,
    run_root: Path | None = None,
    resume: bool = True,
) -> pd.DataFrame:
    paths = default_paths(project_dir)
    records = await generate_all_async(
        read_examples(examples_path or paths["prepared_examples"]),
        load_variants(variants_path or paths["variant_config"]),
        output_path or paths["generations"],
        run_root or paths["run_root"],
        resume=resume,
    )
    return pd.DataFrame([record.model_dump(mode="json") for record in records])


def score_reference_metrics_for_notebook(
    project_dir: Path,
    *,
    generations_path: Path | None = None,
    metric_config_path: Path | None = None,
    output_path: Path | None = None,
    include_ineligible: bool = False,
) -> pd.DataFrame:
    paths = default_paths(project_dir)
    experiment = ExperimentConfig.model_validate(
        json.loads((metric_config_path or paths["metric_config"]).read_text(encoding="utf-8"))
    )
    observations = evaluate_reference_metrics(
        read_generations(generations_path or paths["generations"]),
        experiment.reference_metrics,
        output_path or paths["reference_metrics"],
        include_ineligible=include_ineligible,
    )
    return pd.DataFrame([item.model_dump(mode="json") for item in observations])


def score_deepeval_for_notebook(
    project_dir: Path,
    *,
    generations_path: Path | None = None,
    metric_config_path: Path | None = None,
    output_path: Path | None = None,
    resume: bool = True,
) -> pd.DataFrame:
    load_project_env(project_dir)
    paths = default_paths(project_dir)
    experiment = ExperimentConfig.model_validate(
        json.loads((metric_config_path or paths["metric_config"]).read_text(encoding="utf-8"))
    )
    observations = evaluate_deepeval(
        read_generations(generations_path or paths["generations"]),
        experiment.deepeval,
        output_path or paths["deepeval_metrics"],
        resume=resume,
    )
    return pd.DataFrame([item.model_dump(mode="json") for item in observations])


def score_openai_judge_for_notebook(
    project_dir: Path,
    *,
    generations_path: Path | None = None,
    metric_config_path: Path | None = None,
    output_path: Path | None = None,
    judge_model: str = "gpt-5.6-sol",
    judge_repetitions: int = 1,
    max_source_characters: int | None = None,
    run_summarization: bool | None = None,
    run_faithfulness: bool | None = None,
    run_factual_correctness: bool | None = None,
    run_reference_adequacy: bool | None = None,
    run_task_relevance: bool | None = None,
    run_coherence: bool | None = None,
    run_usefulness: bool | None = None,
    resume: bool = True,
) -> pd.DataFrame:
    """Run the configured DeepEval judge metrics with an OpenAI judge model.

    This is a notebook convenience wrapper around the same evaluator used by
    ``score_deepeval_for_notebook``. It keeps the metric toggles from the
    selected metrics config unless an override is supplied here.
    """

    load_project_env(project_dir)
    paths = default_paths(project_dir)
    experiment = ExperimentConfig.model_validate(
        json.loads((metric_config_path or paths["metric_config"]).read_text(encoding="utf-8"))
    )
    updates: dict[str, Any] = {
        "enabled": True,
        "judge_provider": "openai",
        "judge_model": judge_model,
        "judge_repetitions": judge_repetitions,
    }
    optional_updates = {
        "max_source_characters": max_source_characters,
        "run_summarization": run_summarization,
        "run_faithfulness": run_faithfulness,
        "run_factual_correctness": run_factual_correctness,
        "run_reference_adequacy": run_reference_adequacy,
        "run_task_relevance": run_task_relevance,
        "run_coherence": run_coherence,
        "run_usefulness": run_usefulness,
    }
    updates |= {
        key: value
        for key, value in optional_updates.items()
        if value is not None
    }
    config = experiment.deepeval.model_copy(update=updates)
    observations = evaluate_deepeval(
        read_generations(generations_path or paths["generations"]),
        config,
        output_path
        or (paths["deepeval_metrics"].parent / "openai_judge_metrics.jsonl"),
        resume=resume,
    )
    return pd.DataFrame([item.model_dump(mode="json") for item in observations])


def annotate_with_openai_judge_for_notebook(
    project_dir: Path,
    *,
    generations_path: Path | None = None,
    output_path: Path | None = None,
    judge_model: str | None = None,
    judge_repetitions: int = 1,
    reasoning_effort: str | None = None,
    max_source_characters: int = 50_000,
    max_output_tokens: int = 2_500,
    include_references: bool = False,
    include_system_identity: bool = False,
    include_metric_scores: bool = False,
    resume: bool = True,
) -> pd.DataFrame:
    """Run the OpenAI LLM judge as a structured error annotator.

    Unlike the scalar DeepEval wrapper, this sends each generated output
    independently and returns span-level error annotations using the configured
    taxonomy. Human references and metric scores are excluded by default.
    """

    load_project_env(project_dir)
    paths = default_paths(project_dir)
    config = OpenAIJudgeAnnotationConfig(
        judge_model=(
            judge_model
            or os.getenv("T2T_OPENAI_JUDGE_ANNOTATION_MODEL")
            or os.getenv("T2T_DEEPEVAL_JUDGE_MODEL")
            or "gpt-5.6-sol"
        ),
        judge_repetitions=judge_repetitions,
        reasoning_effort=(
            reasoning_effort
            or os.getenv("T2T_OPENAI_JUDGE_REASONING_EFFORT")
            or "high"
        ),
        max_source_characters=max_source_characters,
        max_output_tokens=max_output_tokens,
        include_references=include_references,
        include_system_identity=include_system_identity,
        include_metric_scores=include_metric_scores,
    )
    annotations = annotate_generations_with_openai_judge(
        read_generations(generations_path or paths["generations"]),
        config,
        output_path or paths["llm_judge_annotations"],
        resume=resume,
    )
    return pd.DataFrame([item.model_dump(mode="json") for item in annotations])


def diagnostics_for_notebook(
    project_dir: Path,
    *,
    generations_path: Path | None = None,
    output_path: Path | None = None,
) -> pd.DataFrame:
    paths = default_paths(project_dir)
    return write_diagnostics(
        generations_path or paths["generations"],
        output_path or paths["diagnostics"],
    )


def aggregate_for_notebook(
    project_dir: Path,
    *,
    metric_config_path: Path | None = None,
    reference_metrics_path: Path | None = None,
    deepeval_metrics_path: Path | None = None,
    diagnostics_path: Path | None = None,
    output_directory: Path | None = None,
) -> dict[str, Path]:
    paths = default_paths(project_dir)
    experiment = ExperimentConfig.model_validate(
        json.loads((metric_config_path or paths["metric_config"]).read_text(encoding="utf-8"))
    )
    write_analysis(
        reference_observations_path=reference_metrics_path or paths["reference_metrics"],
        deepeval_observations_path=deepeval_metrics_path or paths["deepeval_metrics"],
        diagnostics_path=diagnostics_path or paths["diagnostics"],
        output_directory=output_directory or paths["analysis"],
        baseline_variant=experiment.baseline_variant,
        bootstrap_resamples=experiment.bootstrap_resamples,
        confidence_level=experiment.confidence_level,
        seed=experiment.random_seed,
    )
    analysis_dir = output_directory or paths["analysis"]
    return {
        "all_metric_scores": analysis_dir / "all_metric_scores.csv",
        "dataset_variant_summary": analysis_dir / "dataset_variant_summary.csv",
        "macro_summary": analysis_dir / "macro_summary.csv",
        "paired_bootstrap_comparisons": analysis_dir / "paired_bootstrap_comparisons.csv",
        "metric_correlation_matrix": analysis_dir / "metric_correlation_matrix.csv",
        "metric_correlations_long": analysis_dir / "metric_correlations_long.csv",
        "cost_summary": analysis_dir / "cost_summary.csv",
    }


def read_jsonl_as_frame(path: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return pd.DataFrame(rows)
