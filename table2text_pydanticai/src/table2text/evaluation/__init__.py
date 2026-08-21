"""Public API for dataset preparation, generation, metrics, and human studies."""

from __future__ import annotations

from .models import (
    BenchmarkExample,
    DatasetConfig,
    DeepEvalObservation,
    ExperimentConfig,
    GenerationRecord,
    LLMJudgeAnnotationRecord,
    LLMJudgeErrorAnnotation,
    MetricObservation,
    VariantConfig,
)
from .alignscore_client import AlignScoreClient
from .external_factuality import ExternalFactualityResult, HHEMEvaluator
from .notebook import (
    aggregate_for_notebook,
    annotate_with_openai_judge_for_notebook,
    default_paths,
    diagnostics_for_notebook,
    generate_reports_for_notebook,
    init_notebook_evaluation,
    load_project_env,
    prepare_examples_for_notebook,
    read_jsonl_as_frame,
    score_deepeval_for_notebook,
    score_openai_judge_for_notebook,
    score_reference_metrics_for_notebook,
)

__all__ = [
    "aggregate_for_notebook",
    "annotate_with_openai_judge_for_notebook",
    "AlignScoreClient",
    "BenchmarkExample",
    "DatasetConfig",
    "default_paths",
    "DeepEvalObservation",
    "diagnostics_for_notebook",
    "ExternalFactualityResult",
    "ExperimentConfig",
    "generate_reports_for_notebook",
    "GenerationRecord",
    "HHEMEvaluator",
    "init_notebook_evaluation",
    "load_project_env",
    "LLMJudgeAnnotationRecord",
    "LLMJudgeErrorAnnotation",
    "MetricObservation",
    "prepare_examples_for_notebook",
    "read_jsonl_as_frame",
    "score_deepeval_for_notebook",
    "score_openai_judge_for_notebook",
    "score_reference_metrics_for_notebook",
    "VariantConfig",
]

__version__ = "2.0.0"
