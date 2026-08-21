"""Run DeepEval metrics through the project's configured independent judge."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Callable

from .datasets import write_jsonl
from .models import DeepEvalConfig, DeepEvalObservation, GenerationRecord, MetricStatus
from .reference_metrics import plain_text
from table2text.config import load_env_files


def make_observation(
    record: GenerationRecord,
    *,
    metric_name: str,
    judge_model: str,
    judge_repetition: int,
    status: MetricStatus,
    score: float | None = None,
    reason: str | None = None,
    threshold: float | None = None,
    success: bool | None = None,
    duration: float | None = None,
    error: str | None = None,
) -> DeepEvalObservation:
    return DeepEvalObservation(
        generation_id=record.generation_id,
        dataset_id=record.dataset_id,
        example_id=record.example_id,
        variant_id=record.variant_id,
        repetition=record.repetition,
        metric_name=metric_name,
        judge_model=judge_model,
        judge_repetition=judge_repetition,
        status=status,
        score=score,
        reason=reason,
        threshold=threshold,
        success=success,
        duration_seconds=duration,
        error=error,
    )


def source_for_judge(record: GenerationRecord, config: DeepEvalConfig) -> str:
    source = record.source_text
    if len(source) <= config.max_source_characters:
        return source
    return source[: config.max_source_characters] + "\n\n[Source truncated by evaluation configuration.]"


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value) or "")


def task_guidance_for_judge(record: GenerationRecord) -> str:
    task_family = _enum_value(record.task_family)
    output_mode = _enum_value(record.output_mode)
    guidance = [
        "Judge the actual output against the requested data-to-text task, "
        "not against a generic summarisation task.",
    ]

    if task_family == "highlighted_table_description":
        guidance.extend(
            [
                "This is a focused-table task: identify the concise "
                "table-local proposition expressed by the highlighted cell "
                "or focused table region.",
                "Use page title, section title, row labels, column headers, "
                "highlighted values and source-text context to decide the "
                "correct subject and relation.",
                "Penalise outputs that merely describe cell coordinates or "
                "assign the highlighted value to a row co-entity when the "
                "local table context identifies a different primary subject.",
            ]
        )
    elif task_family in {
        "attribute_verbalisation",
        "triple_verbalisation",
    }:
        guidance.extend(
            [
                "This is a short structured-record verbalisation task: the "
                "answer should express all and only the supplied attributes "
                "or triples.",
                "Prefer concise predicate-preserving wording. Do not reward "
                "unrelated background, extra attributes, changed numbers, "
                "changed units or changed entity identity.",
            ]
        )

    if output_mode in {
        "one_sentence",
        "short_text",
        "direct_answer",
    }:
        guidance.append(
            "The expected output is short; brevity is appropriate when the "
            "essential supported proposition is complete."
        )

    return "\n".join(f"- {item}" for item in guidance)


def input_for_judge(record: GenerationRecord, config: DeepEvalConfig) -> str:
    source = source_for_judge(record, config)
    return (
        f"Dataset ID: {record.dataset_id}\n"
        f"Example ID: {record.example_id}\n"
        f"Task family: {_enum_value(record.task_family)}\n"
        f"Output mode: {_enum_value(record.output_mode)}\n"
        f"Request: {record.request}\n\n"
        "Task-specific evaluation guidance:\n"
        f"{task_guidance_for_judge(record)}\n\n"
        "Structured source:\n"
        f"{source}"
    )


def reference_for_judge(record: GenerationRecord) -> str | None:
    if not record.references:
        return None
    return "\n\n--- ALTERNATIVE REFERENCE ---\n\n".join(record.references)


def source_chunks_for_judge(record: GenerationRecord, config: DeepEvalConfig) -> list[str]:
    source = source_for_judge(record, config)
    chunks = [chunk.strip() for chunk in source.split("\n\n") if chunk.strip()]
    return chunks or ([source] if source.strip() else [])


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def _normalise_deepseek_model_name(model_name: str) -> str:
    if model_name.startswith("deepseek:"):
        return model_name.split(":", 1)[1]
    return model_name


def _normalise_openai_model_name(model_name: str) -> str:
    if model_name.startswith("openai:"):
        return model_name.split(":", 1)[1]
    return model_name


def apply_deepeval_env_overrides(config: DeepEvalConfig) -> DeepEvalConfig:
    updates: dict[str, Any] = {}
    provider = _first_env(
        "T2T_DEEPEVAL_JUDGE_PROVIDER",
        "DEEPEVAL_JUDGE_PROVIDER",
    )
    if provider is not None:
        updates["judge_provider"] = provider.lower()

    model = _first_env(
        "T2T_DEEPEVAL_JUDGE_MODEL",
        "DEEPEVAL_JUDGE_MODEL",
    )
    if model is not None:
        updates["judge_model"] = model

    repetitions = _first_env(
        "T2T_DEEPEVAL_JUDGE_REPETITIONS",
        "DEEPEVAL_JUDGE_REPETITIONS",
    )
    if repetitions is not None:
        updates["judge_repetitions"] = int(repetitions)

    if not updates:
        return config
    return DeepEvalConfig.model_validate(config.model_dump() | updates)


def build_judge_model(config: DeepEvalConfig) -> Any:
    provider = config.judge_provider
    model_name = config.judge_model
    if model_name.startswith("deepseek:"):
        provider = "deepseek"
        model_name = _normalise_deepseek_model_name(model_name)
    elif model_name.startswith("openai:"):
        provider = "openai"
        model_name = _normalise_openai_model_name(model_name)

    if provider == "deepseek":
        api_key = _first_env("DEEPSEEK_API_KEY")
        if api_key is None:
            raise RuntimeError(
                "DeepEval is configured to use DeepSeek, but DEEPSEEK_API_KEY "
                "is not set in the environment or project .env file."
            )
        from deepeval.models import DeepSeekModel

        return DeepSeekModel(
            model=_normalise_deepseek_model_name(model_name),
            api_key=api_key,
        )

    if provider == "openai":
        api_key = _first_env("OPENAI_API_KEY", "T2T_OPENAI_API_KEY")
        if api_key is None:
            raise RuntimeError(
                "DeepEval is configured to use OpenAI, but OPENAI_API_KEY "
                "is not set in the environment or project .env file."
            )
        from deepeval.models import GPTModel

        return GPTModel(
            model=_normalise_openai_model_name(model_name),
            api_key=api_key,
            base_url=_first_env("OPENAI_BASE_URL", "T2T_OPENAI_BASE_URL"),
        )

    return model_name


def run_metric(
    record: GenerationRecord,
    metric_name: str,
    metric_factory: Callable[[], Any],
    test_case: Any,
    config: DeepEvalConfig,
    judge_repetition: int,
) -> DeepEvalObservation:
    started = time.perf_counter()
    try:
        metric = metric_factory()
        metric.measure(test_case)
        score = float(metric.score) if metric.score is not None else None
        return make_observation(
            record,
            metric_name=metric_name,
            judge_model=config.judge_model,
            judge_repetition=judge_repetition,
            status=MetricStatus.SCORED,
            score=score,
            reason=getattr(metric, "reason", None),
            threshold=getattr(metric, "threshold", config.threshold),
            success=getattr(metric, "success", None),
            duration=time.perf_counter() - started,
        )
    except Exception as exc:
        return make_observation(
            record,
            metric_name=metric_name,
            judge_model=config.judge_model,
            judge_repetition=judge_repetition,
            status=MetricStatus.ERROR,
            duration=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def evaluate_record(record: GenerationRecord, config: DeepEvalConfig) -> list[DeepEvalObservation]:
    try:
        from deepeval.metrics import FaithfulnessMetric, GEval, SummarizationMetric
        from deepeval.test_case import LLMTestCase, SingleTurnParams
    except ImportError:
        return [
            make_observation(
                record,
                metric_name="deepeval",
                judge_model=config.judge_model,
                judge_repetition=0,
                status=MetricStatus.UNAVAILABLE,
                error="deepeval is not installed.",
            )
        ]

    try:
        judge_model = build_judge_model(config)
    except Exception as exc:
        return [
            make_observation(
                record,
                metric_name="deepeval_judge_model",
                judge_model=config.judge_model,
                judge_repetition=0,
                status=MetricStatus.ERROR,
                error=f"{type(exc).__name__}: {exc}",
            )
        ]

    source = input_for_judge(record, config)
    source_chunks = source_chunks_for_judge(record, config)
    generated = plain_text(record.generated_text)
    expected = reference_for_judge(record)
    test_case = LLMTestCase(
        input=source,
        actual_output=generated,
        expected_output=expected,
        retrieval_context=source_chunks,
    )
    factories: list[tuple[str, Callable[[], Any]]] = []

    if config.run_summarization:
        factories.append(
            (
                "deepeval_summarization",
                lambda: SummarizationMetric(
                    threshold=config.threshold,
                    model=judge_model,
                    include_reason=True,
                    async_mode=False,
                ),
            )
        )
    if config.run_faithfulness:
        factories.append(
            (
                "deepeval_faithfulness",
                lambda: FaithfulnessMetric(
                    threshold=config.threshold,
                    model=judge_model,
                    include_reason=True,
                    async_mode=False,
                ),
            )
        )
    if config.run_factual_correctness:
        factories.append(
            (
                "geval_factual_correctness",
                lambda: GEval(
                    name="Factual correctness",
                    criteria=(
                        "Determine whether every factual statement in the actual output "
                        "is supported by the structured source in the input. Penalise "
                        "incorrect numbers, entities, rankings, comparisons, chronology "
                        "and unsupported causal claims. Do not require wording to match "
                        "a reference."
                    ),
                    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
                    threshold=config.threshold,
                    model=judge_model,
                    async_mode=False,
                ),
            )
        )
    if config.run_reference_adequacy and expected is not None:
        factories.append(
            (
                "geval_reference_adequacy",
                lambda: GEval(
                    name="Reference adequacy",
                    criteria=(
                        "Determine whether the actual output communicates the same "
                        "important content as one or more expected outputs. Accept valid "
                        "paraphrases and different organisation. Penalise material "
                        "omissions and unrelated content."
                    ),
                    evaluation_params=[
                        SingleTurnParams.ACTUAL_OUTPUT,
                        SingleTurnParams.EXPECTED_OUTPUT,
                    ],
                    threshold=config.threshold,
                    model=judge_model,
                    async_mode=False,
                ),
            )
        )
    if config.run_task_relevance:
        factories.append(
            (
                "geval_task_relevance",
                lambda: GEval(
                    name="Task relevance",
                    criteria=(
                        "Determine whether the actual output follows the requested "
                        "data-to-text task, stays within the expected scope and avoids "
                        "irrelevant analysis."
                    ),
                    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
                    threshold=config.threshold,
                    model=judge_model,
                    async_mode=False,
                ),
            )
        )
    if config.run_coherence:
        factories.append(
            (
                "geval_coherence",
                lambda: GEval(
                    name="Coherence and readability",
                    criteria=(
                        "Evaluate whether the actual output is clear, well organised, "
                        "fluent and non-repetitive for its expected length. Do not judge "
                        "factual correctness in this criterion."
                    ),
                    evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
                    threshold=config.threshold,
                    model=judge_model,
                    async_mode=False,
                ),
            )
        )
    if config.run_usefulness:
        factories.append(
            (
                "geval_usefulness",
                lambda: GEval(
                    name="Analytical usefulness",
                    criteria=(
                        "Evaluate whether the actual output selects and communicates "
                        "useful information for the requested task without "
                        "over-interpreting the source. For simple verbalisation tasks, "
                        "usefulness means concise complete expression of the supplied facts."
                    ),
                    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
                    threshold=config.threshold,
                    model=judge_model,
                    async_mode=False,
                ),
            )
        )

    observations: list[DeepEvalObservation] = []
    for judge_repetition in range(config.judge_repetitions):
        for metric_name, factory in factories:
            observations.append(
                run_metric(record, metric_name, factory, test_case, config, judge_repetition)
            )
    return observations


def evaluate_deepeval(
    records: list[GenerationRecord],
    config: DeepEvalConfig,
    output_path: Path,
    *,
    resume: bool = True,
) -> list[DeepEvalObservation]:
    load_env_files()
    config = apply_deepeval_env_overrides(config)
    if not config.enabled:
        return []
    existing: dict[tuple[str, str, int], DeepEvalObservation] = {}
    if resume and output_path.exists():
        for line in output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = DeepEvalObservation.model_validate_json(line)
            existing[(item.generation_id, item.metric_name, item.judge_repetition)] = item

    observations = dict(existing)
    for record in records:
        if record.error is not None or not record.generated_text.strip():
            continue
        if record.primary_evaluation_eligible is False:
            continue
        for item in evaluate_record(record, config):
            observations[(item.generation_id, item.metric_name, item.judge_repetition)] = item
        write_jsonl(output_path, observations.values())

    ordered = sorted(
        observations.values(),
        key=lambda item: (
            item.dataset_id,
            item.example_id,
            item.variant_id,
            item.repetition,
            item.metric_name,
            item.judge_repetition,
        ),
    )
    write_jsonl(output_path, ordered)
    return ordered
