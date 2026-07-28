from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from .datasets import write_jsonl
from .models import DeepEvalConfig, DeepEvalObservation, GenerationRecord, MetricStatus
from .reference_metrics import plain_text


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


def reference_for_judge(record: GenerationRecord) -> str | None:
    if not record.references:
        return None
    return "\n\n--- ALTERNATIVE REFERENCE ---\n\n".join(record.references)


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
        from deepeval.metrics import GEval, SummarizationMetric
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

    source = source_for_judge(record, config)
    generated = plain_text(record.generated_text)
    expected = reference_for_judge(record)
    test_case = LLMTestCase(input=source, actual_output=generated, expected_output=expected)
    factories: list[tuple[str, Callable[[], Any]]] = []

    if config.run_summarization:
        factories.append(
            (
                "deepeval_summarization",
                lambda: SummarizationMetric(
                    threshold=config.threshold,
                    model=config.judge_model,
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
                    model=config.judge_model,
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
                    model=config.judge_model,
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
                    model=config.judge_model,
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
                    model=config.judge_model,
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
                    model=config.judge_model,
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
