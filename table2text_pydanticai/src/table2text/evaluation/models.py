from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class TaskFamily(str, Enum):
    EVENT_REPORT = "event_report"
    LONG_FORM_TABLE_REPORT = "long_form_table_report"
    HIGHLIGHTED_TABLE_DESCRIPTION = "highlighted_table_description"
    LOGICAL_TABLE_STATEMENT = "logical_table_statement"
    TABLE_QUESTION_ANSWERING = "table_question_answering"
    ATTRIBUTE_VERBALISATION = "attribute_verbalisation"
    TRIPLE_VERBALISATION = "triple_verbalisation"
    BIOGRAPHY = "biography"
    WEATHER_RESPONSE = "weather_response"
    CROSS_LINGUAL_EVENT_REPORT = "cross_lingual_event_report"
    ANALYTICAL_EXPLANATION = "analytical_explanation"


class OutputMode(str, Enum):
    ONE_SENTENCE = "one_sentence"
    SHORT_TEXT = "short_text"
    PARAGRAPH = "paragraph"
    MULTI_PARAGRAPH_REPORT = "multi_paragraph_report"
    DIRECT_ANSWER = "direct_answer"


class DatasetSource(str, Enum):
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class GenerationBackend(str, Enum):
    TABLE2TEXT = "table2text"
    PRECOMPUTED = "precomputed"
    CALLABLE = "callable"
    COMMAND = "command"


class MetricStatus(str, Enum):
    SCORED = "scored"
    SKIPPED = "skipped"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class DatasetConfig(StrictModel):
    dataset_id: str
    enabled: bool = True
    source: DatasetSource = DatasetSource.HUGGINGFACE
    hub_id: str | None = None
    config_name: str | None = None
    revision: str | None = None
    split: str = "test"
    trust_remote_code: bool = False
    local_path: Path | None = None
    normalizer: str = "generic"
    task_family: TaskFamily
    output_mode: OutputMode
    language: str = "en"
    sample_size: int | None = 30
    seed: int = 42
    source_fields: list[str] = Field(default_factory=list)
    reference_fields: list[str] = Field(
        default_factory=lambda: ["references", "target", "reference", "ref"]
    )
    id_fields: list[str] = Field(
        default_factory=lambda: ["gem_parent_id", "gem_id", "example_id", "id"]
    )
    group_fields: list[str] = Field(default_factory=list)
    metadata_fields: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_source(self) -> "DatasetConfig":
        if self.source == DatasetSource.HUGGINGFACE and not self.hub_id:
            raise ValueError(
                f"{self.dataset_id}: hub_id is required for a Hugging Face source."
            )
        if self.source == DatasetSource.LOCAL and self.local_path is None:
            raise ValueError(f"{self.dataset_id}: local_path is required for a local source.")
        if self.sample_size is not None and self.sample_size <= 0:
            raise ValueError("sample_size must be positive or null.")
        return self


class BenchmarkExample(StrictModel):
    dataset_id: str
    example_id: str
    task_family: TaskFamily
    output_mode: OutputMode
    language: str
    source_payload: Any
    source_text: str
    references: list[str]
    request: str
    parent_table: list[list[str]] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_sha256: str
    reference_sha256: str

    @model_validator(mode="after")
    def validate_references(self) -> "BenchmarkExample":
        cleaned = [
            reference.strip()
            for reference in self.references
            if isinstance(reference, str) and reference.strip()
        ]
        object.__setattr__(self, "references", list(dict.fromkeys(cleaned)))
        if not self.references:
            raise ValueError(f"{self.dataset_id}/{self.example_id} has no usable reference output.")
        return self


class DatasetPreparationStatus(StrictModel):
    dataset_id: str
    status: MetricStatus
    requested_split: str
    example_count: int = 0
    output_path: Path | None = None
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None


class VariantConfig(StrictModel):
    variant_id: str
    enabled: bool = True
    backend: GenerationBackend = GenerationBackend.TABLE2TEXT
    description: str = ""
    settings_overrides: dict[str, Any] = Field(default_factory=dict)
    callable_path: str | None = None
    command: list[str] = Field(default_factory=list)
    precomputed_path: Path | None = None
    repetitions: int = Field(default=1, ge=1)
    seeds: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_backend(self) -> "VariantConfig":
        if self.backend == GenerationBackend.CALLABLE and not self.callable_path:
            raise ValueError(f"{self.variant_id}: callable_path is required.")
        if self.backend == GenerationBackend.COMMAND and not self.command:
            raise ValueError(f"{self.variant_id}: command is required.")
        if self.backend == GenerationBackend.PRECOMPUTED and self.precomputed_path is None:
            raise ValueError(f"{self.variant_id}: precomputed_path is required.")
        return self


class GenerationRecord(StrictModel):
    generation_id: str
    dataset_id: str
    example_id: str
    variant_id: str
    repetition: int
    seed: int
    task_family: TaskFamily
    output_mode: OutputMode
    language: str
    source_text: str
    references: list[str]
    parent_table: list[list[str]] | None = None
    request: str
    generated_text: str
    backend: GenerationBackend
    run_id: str | None = None
    pipeline_result_path: Path | None = None
    writer_mode: str | None = None
    release_status: str | None = None
    approved_for_release: bool | None = None
    primary_evaluation_eligible: bool | None = None
    primary_evaluation_reason: str | None = None
    repair_rounds_used: int | None = None
    audit_support_rate: float | None = None
    support_sentence_count: int | None = None
    mapped_support_sentence_count: int | None = None
    fact_id_reference_count: int | None = None
    evidence_id_reference_count: int | None = None
    invalid_fact_id_count: int | None = None
    invalid_evidence_id_count: int | None = None
    elapsed_seconds: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_gbp: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class MetricObservation(StrictModel):
    generation_id: str
    dataset_id: str
    example_id: str
    variant_id: str
    repetition: int
    metric_family: str
    metric_name: str
    status: MetricStatus
    score: float | None = None
    higher_is_better: bool = True
    duration_seconds: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class DeepEvalObservation(StrictModel):
    generation_id: str
    dataset_id: str
    example_id: str
    variant_id: str
    repetition: int
    metric_name: str
    judge_model: str
    judge_repetition: int
    status: MetricStatus
    score: float | None = None
    reason: str | None = None
    threshold: float | None = None
    success: bool | None = None
    duration_seconds: float | None = None
    estimated_cost_gbp: float | None = None
    error: str | None = None


class HumanEvaluationPair(StrictModel):
    pair_id: str
    dataset_id: str
    example_id: str
    source_text: str
    references: list[str]
    output_a: str
    output_b: str
    hidden_variant_a: str
    hidden_variant_b: str
    order_seed: int


class HumanJudgement(StrictModel):
    pair_id: str
    evaluator_id: str
    factual_correctness_a: int = Field(ge=1, le=5)
    factual_correctness_b: int = Field(ge=1, le=5)
    coverage_a: int = Field(ge=1, le=5)
    coverage_b: int = Field(ge=1, le=5)
    coherence_a: int = Field(ge=1, le=5)
    coherence_b: int = Field(ge=1, le=5)
    usefulness_a: int = Field(ge=1, le=5)
    usefulness_b: int = Field(ge=1, le=5)
    preference: Literal["A", "B", "tie"]
    comments: str = ""


class ReferenceMetricConfig(StrictModel):
    enabled_metrics: list[str] = Field(
        default_factory=lambda: [
            "bleu",
            "chrf",
            "ter",
            "rouge1",
            "rouge2",
            "rougeL",
            "rougeLsum",
            "meteor",
            "bertscore",
            "parent",
        ]
    )
    bertscore_model: str | None = None
    bertscore_batch_size: int = 8
    bertscore_device: str | None = None
    bertscore_rescale_with_baseline: bool = True
    parent_n_jobs: int = 1
    lowercase: bool = False


class DeepEvalConfig(StrictModel):
    enabled: bool = True
    judge_model: str = "gpt-4.1-mini"
    judge_repetitions: int = Field(default=3, ge=1)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    max_source_characters: int = 50_000
    run_summarization: bool = True
    run_factual_correctness: bool = True
    run_reference_adequacy: bool = True
    run_task_relevance: bool = True
    run_coherence: bool = True
    run_usefulness: bool = True


class ExperimentConfig(StrictModel):
    experiment_id: str
    prepared_examples_path: Path
    generations_path: Path
    result_directory: Path = Path("evaluation/results")
    reference_metrics: ReferenceMetricConfig = Field(default_factory=ReferenceMetricConfig)
    deepeval: DeepEvalConfig = Field(default_factory=DeepEvalConfig)
    baseline_variant: str = "single_agent_baseline"
    bootstrap_resamples: int = Field(default=5_000, ge=100)
    confidence_level: float = Field(default=0.95, gt=0.0, lt=1.0)
    random_seed: int = 42
