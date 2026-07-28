from __future__ import annotations

import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .datasets import write_jsonl
from .models import GenerationRecord, MetricObservation, MetricStatus, ReferenceMetricConfig


MARKDOWN_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MARKDOWN_DECORATION = re.compile(r"[*_`~]")
WHITESPACE = re.compile(r"\s+")


def plain_text(value: str) -> str:
    value = MARKDOWN_LINK.sub(r"\1", value)
    value = MARKDOWN_HEADING.sub("", value)
    value = MARKDOWN_DECORATION.sub("", value)
    return WHITESPACE.sub(" ", value).strip()


def valid_generation(
    record: GenerationRecord,
    *,
    include_ineligible: bool = False,
) -> bool:
    return (
        record.error is None
        and bool(record.generated_text.strip())
        and bool(record.references)
        and (
            include_ineligible
            or record.primary_evaluation_eligible is not False
        )
    )


def ineligible_generation_reason(
    record: GenerationRecord,
    *,
    include_ineligible: bool = False,
) -> str | None:
    if record.error is not None:
        return f"Generation failed: {record.error}"
    if not record.generated_text.strip():
        return "Generated text is empty."
    if not record.references:
        return "No reference outputs are available."
    if record.primary_evaluation_eligible is False and not include_ineligible:
        return (
            record.primary_evaluation_reason
            or "The generation was marked ineligible for primary evaluation."
        )
    return None


def observation(
    record: GenerationRecord,
    *,
    family: str,
    name: str,
    status: MetricStatus,
    score: float | None = None,
    higher_is_better: bool = True,
    duration: float | None = None,
    details: dict[str, Any] | None = None,
    error: str | None = None,
) -> MetricObservation:
    return MetricObservation(
        generation_id=record.generation_id,
        dataset_id=record.dataset_id,
        example_id=record.example_id,
        variant_id=record.variant_id,
        repetition=record.repetition,
        metric_family=family,
        metric_name=name,
        status=status,
        score=score,
        higher_is_better=higher_is_better,
        duration_seconds=duration,
        details=details or {},
        error=error,
    )


def score_over_references(
    candidate: str,
    references: list[str],
    function: Callable[[str, str], float],
) -> tuple[float, int]:
    scores = [float(function(candidate, reference)) for reference in references]
    best_index = int(np.argmax(scores))
    return scores[best_index], best_index


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold())


def _token_f1(candidate: str, reference: str) -> float:
    candidate_tokens = _tokens(candidate)
    reference_tokens = _tokens(reference)
    if not candidate_tokens and not reference_tokens:
        return 1.0
    if not candidate_tokens or not reference_tokens:
        return 0.0
    overlap = 0
    reference_counts: dict[str, int] = defaultdict(int)
    for token in reference_tokens:
        reference_counts[token] += 1
    for token in candidate_tokens:
        if reference_counts[token] > 0:
            overlap += 1
            reference_counts[token] -= 1
    precision = overlap / len(candidate_tokens)
    recall = overlap / len(reference_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _fallback_overlap(candidate: str, references: list[str]) -> tuple[float, int]:
    return score_over_references(candidate, references, _token_f1)


def score_lexical_record(
    record: GenerationRecord,
    config: ReferenceMetricConfig,
) -> list[MetricObservation]:
    results: list[MetricObservation] = []
    candidate = plain_text(record.generated_text)
    references = [plain_text(reference) for reference in record.references]
    if config.lowercase:
        candidate = candidate.casefold()
        references = [reference.casefold() for reference in references]
    enabled = set(config.enabled_metrics)

    try:
        import sacrebleu
    except ImportError:
        sacrebleu = None

    for name in ("bleu", "chrf", "ter"):
        if name not in enabled:
            continue
        started = time.perf_counter()
        if sacrebleu is None:
            fallback, best_index = _fallback_overlap(candidate, references)
            score = (1.0 - fallback) if name == "ter" else fallback
            results.append(
                observation(
                    record,
                    family="lexical",
                    name=name,
                    status=MetricStatus.SCORED,
                    score=score,
                    higher_is_better=(name != "ter"),
                    duration=time.perf_counter() - started,
                    details={
                        "fallback": "token_f1",
                        "selected_reference_index": best_index,
                    },
                )
            )
            continue
        try:
            if name == "bleu":
                result = sacrebleu.sentence_bleu(
                    candidate,
                    references,
                    lowercase=config.lowercase,
                    smooth_method="exp",
                )
            elif name == "chrf":
                result = sacrebleu.sentence_chrf(candidate, references, word_order=2)
            else:
                result = sacrebleu.sentence_ter(candidate, references)
            results.append(
                observation(
                    record,
                    family="lexical",
                    name=name,
                    status=MetricStatus.SCORED,
                    score=result.score / 100.0,
                    higher_is_better=(name != "ter"),
                    duration=time.perf_counter() - started,
                    details={"reference_count": len(references), "raw_percent": result.score},
                )
            )
        except Exception as exc:
            results.append(
                observation(
                    record,
                    family="lexical",
                    name=name,
                    status=MetricStatus.ERROR,
                    higher_is_better=(name != "ter"),
                    duration=time.perf_counter() - started,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

    rouge_names = {"rouge1", "rouge2", "rougeL", "rougeLsum"} & enabled
    if rouge_names:
        started = time.perf_counter()
        try:
            from rouge_score import rouge_scorer

            scorer = rouge_scorer.RougeScorer(sorted(rouge_names), use_stemmer=True)
            for name in sorted(rouge_names):
                score, best_index = score_over_references(
                    candidate,
                    references,
                    lambda prediction, reference: scorer.score(reference, prediction)[name].fmeasure,
                )
                results.append(
                    observation(
                        record,
                        family="lexical",
                        name=name,
                        status=MetricStatus.SCORED,
                        score=score,
                        duration=time.perf_counter() - started,
                        details={
                            "reference_count": len(references),
                            "selected_reference_index": best_index,
                            "aggregation": "maximum_over_references",
                        },
                    )
                )
        except ImportError:
            for name in sorted(rouge_names):
                score, best_index = _fallback_overlap(candidate, references)
                results.append(
                    observation(
                        record,
                        family="lexical",
                        name=name,
                        status=MetricStatus.SCORED,
                        score=score,
                        duration=time.perf_counter() - started,
                        details={
                            "fallback": "token_f1",
                            "selected_reference_index": best_index,
                        },
                    )
                )
        except Exception as exc:
            for name in sorted(rouge_names):
                results.append(
                    observation(
                        record,
                        family="lexical",
                        name=name,
                        status=MetricStatus.ERROR,
                        duration=time.perf_counter() - started,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )

    if "meteor" in enabled:
        started = time.perf_counter()
        try:
            import nltk
            from nltk.translate.meteor_score import meteor_score

            try:
                score, best_index = score_over_references(
                    candidate,
                    references,
                    lambda prediction, reference: meteor_score(
                        [reference.split()],
                        prediction.split(),
                    ),
                )
            except LookupError:
                nltk.download("wordnet", quiet=True)
                nltk.download("omw-1.4", quiet=True)
                score, best_index = score_over_references(
                    candidate,
                    references,
                    lambda prediction, reference: meteor_score(
                        [reference.split()],
                        prediction.split(),
                    ),
                )
            results.append(
                observation(
                    record,
                    family="lexical_semantic",
                    name="meteor",
                    status=MetricStatus.SCORED,
                    score=score,
                    duration=time.perf_counter() - started,
                    details={
                        "reference_count": len(references),
                        "selected_reference_index": best_index,
                        "aggregation": "maximum_over_references",
                    },
                )
            )
        except ImportError:
            results.append(
                observation(
                    record,
                    family="lexical_semantic",
                    name="meteor",
                    status=MetricStatus.UNAVAILABLE,
                    error="nltk is not installed.",
                )
            )
        except Exception as exc:
            results.append(
                observation(
                    record,
                    family="lexical_semantic",
                    name="meteor",
                    status=MetricStatus.ERROR,
                    duration=time.perf_counter() - started,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

    return results


def score_bertscore(
    records: list[GenerationRecord],
    config: ReferenceMetricConfig,
) -> list[MetricObservation]:
    if "bertscore" not in config.enabled_metrics:
        return []
    try:
        from bert_score import score as bert_score
    except ImportError:
        return [
            observation(
                record,
                family="semantic",
                name="bertscore_f1",
                status=MetricStatus.UNAVAILABLE,
                error="bert-score is not installed.",
            )
            for record in records
        ]

    observations: list[MetricObservation] = []
    grouped: dict[str, list[GenerationRecord]] = defaultdict(list)
    for record in records:
        grouped[record.language].append(record)

    for language, language_records in grouped.items():
        candidates: list[str] = []
        references: list[str] = []
        ownership: list[tuple[GenerationRecord, int]] = []
        for record in language_records:
            candidate = plain_text(record.generated_text)
            for reference_index, reference in enumerate(record.references):
                candidates.append(candidate)
                references.append(plain_text(reference))
                ownership.append((record, reference_index))
        if not candidates:
            continue
        started = time.perf_counter()
        try:
            kwargs: dict[str, Any] = {
                "cands": candidates,
                "refs": references,
                "batch_size": config.bertscore_batch_size,
                "verbose": False,
            }
            if config.bertscore_model:
                kwargs["model_type"] = config.bertscore_model
                kwargs["rescale_with_baseline"] = False
            else:
                kwargs["lang"] = language.split("-")[0]
                kwargs["rescale_with_baseline"] = config.bertscore_rescale_with_baseline
            if config.bertscore_device:
                kwargs["device"] = config.bertscore_device
            _, _, f1 = bert_score(**kwargs)
            values_by_generation: dict[str, list[tuple[int, float]]] = defaultdict(list)
            for (record, reference_index), value in zip(ownership, f1.tolist(), strict=True):
                values_by_generation[record.generation_id].append((reference_index, float(value)))
            total_duration = time.perf_counter() - started
            duration_each = total_duration / max(len(language_records), 1)
            for record in language_records:
                best_index, best_value = max(
                    values_by_generation[record.generation_id],
                    key=lambda item: item[1],
                )
                observations.append(
                    observation(
                        record,
                        family="semantic",
                        name="bertscore_f1",
                        status=MetricStatus.SCORED,
                        score=best_value,
                        duration=duration_each,
                        details={
                            "language": language,
                            "model": config.bertscore_model or "bert-score default",
                            "selected_reference_index": best_index,
                            "aggregation": "maximum_over_references",
                        },
                    )
                )
        except Exception as exc:
            duration = time.perf_counter() - started
            for record in language_records:
                observations.append(
                    observation(
                        record,
                        family="semantic",
                        name="bertscore_f1",
                        status=MetricStatus.ERROR,
                        duration=duration,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )
    return observations


def score_parent_record(
    record: GenerationRecord,
    config: ReferenceMetricConfig,
) -> list[MetricObservation]:
    if "parent" not in config.enabled_metrics:
        return []
    metric_names = ["parent_precision", "parent_recall", "parent_f1"]
    if record.parent_table is None:
        return [
            observation(
                record,
                family="table_aware",
                name=name,
                status=MetricStatus.SKIPPED,
                details={
                    "reason": "The dataset adapter did not expose a PARENT-compatible table."
                },
            )
            for name in metric_names
        ]
    try:
        from parent import parent
    except ImportError:
        return [
            observation(
                record,
                family="table_aware",
                name=name,
                status=MetricStatus.UNAVAILABLE,
                error="Install the optional KaijuML PARENT package.",
            )
            for name in metric_names
        ]
    candidate = plain_text(record.generated_text).split()
    references = [plain_text(reference).split() for reference in record.references]
    table = [[str(cell) for cell in table_row] for table_row in record.parent_table]
    started = time.perf_counter()
    try:
        precision, recall, f1 = parent(
            [candidate],
            [references],
            [table],
            avg_results=True,
            n_jobs=config.parent_n_jobs,
            use_tqdm=False,
        )
        duration = time.perf_counter() - started
        return [
            observation(
                record,
                family="table_aware",
                name="parent_precision",
                status=MetricStatus.SCORED,
                score=float(precision),
                duration=duration,
            ),
            observation(
                record,
                family="table_aware",
                name="parent_recall",
                status=MetricStatus.SCORED,
                score=float(recall),
                duration=duration,
            ),
            observation(
                record,
                family="table_aware",
                name="parent_f1",
                status=MetricStatus.SCORED,
                score=float(f1),
                duration=duration,
            ),
        ]
    except Exception as exc:
        duration = time.perf_counter() - started
        return [
            observation(
                record,
                family="table_aware",
                name=name,
                status=MetricStatus.ERROR,
                duration=duration,
                error=f"{type(exc).__name__}: {exc}",
            )
            for name in metric_names
        ]


def corpus_sacrebleu_observations(
    records: list[GenerationRecord],
    config: ReferenceMetricConfig,
) -> list[MetricObservation]:
    enabled = set(config.enabled_metrics)
    relevant = {"bleu", "chrf", "ter"} & enabled
    if not relevant or not records:
        return []
    try:
        import sacrebleu
    except ImportError:
        return []

    grouped: dict[tuple[str, str, int], list[GenerationRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.dataset_id, record.variant_id, record.repetition)].append(record)
    results: list[MetricObservation] = []
    for (dataset_id, variant_id, repetition), group in grouped.items():
        ordered = sorted(group, key=lambda item: item.example_id)
        candidates = [plain_text(item.generated_text) for item in ordered]
        maximum_reference_count = max(len(item.references) for item in ordered)
        reference_streams = [
            [
                plain_text(item.references[reference_index])
                if reference_index < len(item.references)
                else ""
                for item in ordered
            ]
            for reference_index in range(maximum_reference_count)
        ]
        representative = ordered[0]
        if "bleu" in relevant:
            result = sacrebleu.corpus_bleu(
                candidates,
                reference_streams,
                lowercase=config.lowercase,
            )
            results.append(
                observation(
                    representative,
                    family="lexical_corpus",
                    name="corpus_bleu",
                    status=MetricStatus.SCORED,
                    score=result.score / 100.0,
                    details={
                        "dataset_id": dataset_id,
                        "variant_id": variant_id,
                        "repetition": repetition,
                        "example_count": len(ordered),
                        "reference_stream_count": maximum_reference_count,
                    },
                )
            )
        if "chrf" in relevant:
            result = sacrebleu.corpus_chrf(candidates, reference_streams, word_order=2)
            results.append(
                observation(
                    representative,
                    family="lexical_corpus",
                    name="corpus_chrf",
                    status=MetricStatus.SCORED,
                    score=result.score / 100.0,
                    details={"example_count": len(ordered)},
                )
            )
        if "ter" in relevant:
            result = sacrebleu.corpus_ter(candidates, reference_streams)
            results.append(
                observation(
                    representative,
                    family="lexical_corpus",
                    name="corpus_ter",
                    status=MetricStatus.SCORED,
                    score=result.score / 100.0,
                    higher_is_better=False,
                    details={"example_count": len(ordered)},
                )
            )
    return results


def evaluate_reference_metrics(
    records: list[GenerationRecord],
    config: ReferenceMetricConfig,
    output_path: Path,
    *,
    include_ineligible: bool = False,
) -> list[MetricObservation]:
    eligible: list[GenerationRecord] = []
    observations: list[MetricObservation] = []
    for record in records:
        reason = ineligible_generation_reason(
            record,
            include_ineligible=include_ineligible,
        )
        if reason is None:
            eligible.append(record)
            continue
        observations.append(
            observation(
                record,
                family="reference",
                name="reference_metrics",
                status=MetricStatus.SKIPPED,
                details={"reason": reason},
                error=reason,
            )
        )
    for record in eligible:
        observations.extend(score_lexical_record(record, config))
        observations.extend(score_parent_record(record, config))
    observations.extend(score_bertscore(eligible, config))
    observations.extend(corpus_sacrebleu_observations(eligible, config))
    write_jsonl(output_path, observations)
    return observations
