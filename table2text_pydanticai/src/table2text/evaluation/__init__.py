from __future__ import annotations

from .models import (
    BenchmarkExample,
    DatasetConfig,
    DeepEvalObservation,
    ExperimentConfig,
    GenerationRecord,
    MetricObservation,
    VariantConfig,
)
from .notebook import (
    aggregate_for_notebook,
    default_paths,
    diagnostics_for_notebook,
    generate_reports_for_notebook,
    init_notebook_evaluation,
    prepare_examples_for_notebook,
    read_jsonl_as_frame,
    score_reference_metrics_for_notebook,
)

__all__ = [
    "aggregate_for_notebook",
    "BenchmarkExample",
    "DatasetConfig",
    "default_paths",
    "DeepEvalObservation",
    "diagnostics_for_notebook",
    "ExperimentConfig",
    "generate_reports_for_notebook",
    "GenerationRecord",
    "init_notebook_evaluation",
    "MetricObservation",
    "prepare_examples_for_notebook",
    "read_jsonl_as_frame",
    "score_reference_metrics_for_notebook",
    "VariantConfig",
]

__version__ = "2.0.0"
