from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .cli import write_default_metrics, write_default_variants
from .datasets import (
    load_dataset_configs,
    prepare_datasets,
    read_examples,
    save_default_dataset_configs,
)
from .diagnostics import write_diagnostics
from .generation import generate_all_async, load_variants, read_generations
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
        "diagnostics": project_dir / "evaluation/results/diagnostics.csv",
        "analysis": project_dir / "evaluation/results/analysis",
    }


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
