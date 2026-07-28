from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .models import DeepEvalObservation, MetricObservation, MetricStatus


def read_metric_observations(path: Path) -> list[MetricObservation]:
    return [
        MetricObservation.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_deepeval_observations(path: Path) -> list[DeepEvalObservation]:
    return [
        DeepEvalObservation.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def observations_to_frame(
    observations: Iterable[MetricObservation | DeepEvalObservation],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in observations:
        if item.status != MetricStatus.SCORED:
            continue
        rows.append(
            {
                "generation_id": item.generation_id,
                "dataset_id": item.dataset_id,
                "example_id": item.example_id,
                "variant_id": item.variant_id,
                "repetition": item.repetition,
                "metric_name": item.metric_name,
                "score": item.score,
                "duration_seconds": item.duration_seconds,
            }
        )
    return pd.DataFrame(rows)


def collapse_judge_repetitions(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    return (
        frame.groupby(
            [
                "generation_id",
                "dataset_id",
                "example_id",
                "variant_id",
                "repetition",
                "metric_name",
            ],
            as_index=False,
        )
        .agg(
            score=("score", "mean"),
            judge_score_std=("score", "std"),
            duration_seconds=("duration_seconds", "sum"),
        )
    )


def descriptive_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    return (
        frame.groupby(["dataset_id", "variant_id", "metric_name"], as_index=False)
        .agg(
            count=("score", "count"),
            mean=("score", "mean"),
            standard_deviation=("score", "std"),
            median=("score", "median"),
            minimum=("score", "min"),
            maximum=("score", "max"),
        )
    )


def macro_dataset_summary(dataset_summary: pd.DataFrame) -> pd.DataFrame:
    if dataset_summary.empty:
        return pd.DataFrame()
    return (
        dataset_summary.groupby(["variant_id", "metric_name"], as_index=False)
        .agg(
            dataset_count=("dataset_id", "nunique"),
            macro_mean=("mean", "mean"),
            macro_standard_deviation=("mean", "std"),
        )
    )


def percentile_interval(values: np.ndarray, confidence_level: float) -> tuple[float, float]:
    alpha = 1.0 - confidence_level
    return (
        float(np.quantile(values, alpha / 2)),
        float(np.quantile(values, 1 - alpha / 2)),
    )


def paired_bootstrap(
    baseline: np.ndarray,
    candidate: np.ndarray,
    *,
    resamples: int,
    confidence_level: float,
    seed: int,
) -> dict[str, float]:
    if len(baseline) != len(candidate):
        raise ValueError("Paired arrays must have equal lengths.")
    if len(baseline) == 0:
        raise ValueError("Paired arrays must not be empty.")
    random_generator = np.random.default_rng(seed)
    indexes = random_generator.integers(0, len(baseline), size=(resamples, len(baseline)))
    differences = candidate[indexes].mean(axis=1) - baseline[indexes].mean(axis=1)
    lower, upper = percentile_interval(differences, confidence_level)
    observed = float(candidate.mean() - baseline.mean())
    probability_candidate_better = float(np.mean(differences > 0))
    return {
        "mean_difference": observed,
        "confidence_lower": lower,
        "confidence_upper": upper,
        "probability_candidate_better": probability_candidate_better,
    }


def paired_variant_comparisons(
    frame: pd.DataFrame,
    *,
    baseline_variant: str,
    resamples: int,
    confidence_level: float,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if frame.empty:
        return pd.DataFrame()
    for (dataset_id, metric_name), group in frame.groupby(["dataset_id", "metric_name"]):
        baseline = group[group["variant_id"] == baseline_variant][
            ["example_id", "repetition", "score"]
        ].rename(columns={"score": "baseline_score"})
        if baseline.empty:
            continue
        for variant_id in sorted(set(group["variant_id"]) - {baseline_variant}):
            candidate = group[group["variant_id"] == variant_id][
                ["example_id", "repetition", "score"]
            ].rename(columns={"score": "candidate_score"})
            paired = baseline.merge(candidate, on=["example_id", "repetition"], how="inner").dropna()
            if paired.empty:
                continue
            result = paired_bootstrap(
                paired["baseline_score"].to_numpy(dtype=float),
                paired["candidate_score"].to_numpy(dtype=float),
                resamples=resamples,
                confidence_level=confidence_level,
                seed=seed,
            )
            rows.append(
                {
                    "dataset_id": dataset_id,
                    "metric_name": metric_name,
                    "baseline_variant": baseline_variant,
                    "candidate_variant": variant_id,
                    "paired_count": len(paired),
                    **result,
                }
            )
    return pd.DataFrame(rows)


def metric_correlation_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    pivot = frame.pivot_table(
        index="generation_id",
        columns="metric_name",
        values="score",
        aggfunc="mean",
    )
    if pivot.shape[1] < 2:
        return pd.DataFrame()
    return pivot.corr(method="spearman")


def pairwise_metric_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    try:
        from scipy.stats import spearmanr
    except ImportError:
        spearmanr = None
    pivot = frame.pivot_table(
        index="generation_id",
        columns="metric_name",
        values="score",
        aggfunc="mean",
    )
    rows: list[dict[str, Any]] = []
    columns = list(pivot.columns)
    for first_index, first in enumerate(columns):
        for second in columns[first_index + 1 :]:
            paired = pivot[[first, second]].dropna()
            if len(paired) < 3 or spearmanr is None:
                coefficient = None
                p_value = None
            else:
                result = spearmanr(paired[first], paired[second])
                coefficient = float(result.statistic)
                p_value = float(result.pvalue)
            rows.append(
                {
                    "metric_a": first,
                    "metric_b": second,
                    "paired_count": len(paired),
                    "spearman_r": coefficient,
                    "p_value": p_value,
                }
            )
    return pd.DataFrame(rows)


def cost_summary(
    metric_frame: pd.DataFrame,
    diagnostics: pd.DataFrame | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not metric_frame.empty:
        for metric_name, group in metric_frame.groupby("metric_name"):
            rows.append(
                {
                    "category": "metric",
                    "name": metric_name,
                    "count": len(group),
                    "total_duration_seconds": group["duration_seconds"].fillna(0).sum(),
                    "mean_duration_seconds": group["duration_seconds"].mean(),
                    "total_cost_gbp": None,
                }
            )
    if diagnostics is not None and not diagnostics.empty:
        for variant_id, group in diagnostics.groupby("variant_id"):
            rows.append(
                {
                    "category": "generation",
                    "name": variant_id,
                    "count": len(group),
                    "total_duration_seconds": group["elapsed_seconds"].fillna(0).sum(),
                    "mean_duration_seconds": group["elapsed_seconds"].mean(),
                    "total_cost_gbp": group["estimated_cost_gbp"].fillna(0).sum(),
                }
            )
    return pd.DataFrame(rows)


def write_analysis(
    *,
    reference_observations_path: Path,
    deepeval_observations_path: Path | None,
    diagnostics_path: Path | None,
    output_directory: Path,
    baseline_variant: str,
    bootstrap_resamples: int,
    confidence_level: float,
    seed: int,
) -> None:
    reference = observations_to_frame(read_metric_observations(reference_observations_path))
    frames = [reference]
    if deepeval_observations_path is not None and deepeval_observations_path.exists():
        judge = observations_to_frame(read_deepeval_observations(deepeval_observations_path))
        frames.append(collapse_judge_repetitions(judge))
    combined = pd.concat(frames, ignore_index=True)
    output_directory.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_directory / "all_metric_scores.csv", index=False)
    dataset_summary = descriptive_summary(combined)
    dataset_summary.to_csv(output_directory / "dataset_variant_summary.csv", index=False)
    macro = macro_dataset_summary(dataset_summary)
    macro.to_csv(output_directory / "macro_summary.csv", index=False)
    comparisons = paired_variant_comparisons(
        combined,
        baseline_variant=baseline_variant,
        resamples=bootstrap_resamples,
        confidence_level=confidence_level,
        seed=seed,
    )
    comparisons.to_csv(output_directory / "paired_bootstrap_comparisons.csv", index=False)
    metric_correlation_matrix(combined).to_csv(output_directory / "metric_correlation_matrix.csv")
    pairwise_metric_correlations(combined).to_csv(
        output_directory / "metric_correlations_long.csv",
        index=False,
    )
    diagnostics = (
        pd.read_csv(diagnostics_path)
        if diagnostics_path is not None and diagnostics_path.exists()
        else None
    )
    cost_summary(combined, diagnostics).to_csv(output_directory / "cost_summary.csv", index=False)
