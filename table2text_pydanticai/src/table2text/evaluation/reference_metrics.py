from __future__ import annotations

import json
import re
import time
import os
import gc
import tempfile
from contextlib import contextmanager
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from .datasets import write_jsonl
from .alignscore_client import AlignScoreClient
from .external_factuality import ExternalFactualityResult, HHEMEvaluator
from .models import (
    GenerationRecord,
    MetricObservation,
    MetricStatus,
    ReferenceMetricConfig,
    TaskFamily,
)


MARKDOWN_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MARKDOWN_DECORATION = re.compile(r"[*`~]")
MARKDOWN_UNDERSCORE_EMPHASIS = re.compile(
    r"(?<![A-Za-z0-9])_([^_\n]+)_(?![A-Za-z0-9])"
)
WHITESPACE = re.compile(r"\s+")
DEFAULT_ALIGNSCORE_WORKER = Path(__file__).resolve().parents[3] / "scripts/alignscore_worker.py"


def default_alignscore_python_executable() -> Path | None:
    project_root = DEFAULT_ALIGNSCORE_WORKER.parent.parent
    candidates = [
        project_root / ".venv-alignscore/bin/python",
        project_root / ".venv-alignscore/Scripts/python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def plain_text(value: str) -> str:
    value = MARKDOWN_LINK.sub(r"\1", value)
    value = MARKDOWN_HEADING.sub("", value)
    value = MARKDOWN_UNDERSCORE_EMPHASIS.sub(r"\1", value)
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


@contextmanager
def huggingface_offline(enabled: bool):
    keys = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_MODULES_CACHE", "MPLCONFIGDIR")
    previous = {key: os.environ.get(key) for key in keys}
    if enabled:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    if previous["HF_MODULES_CACHE"] is None:
        modules_cache = Path(tempfile.gettempdir()) / "table2text_hf_modules"
        modules_cache.mkdir(parents=True, exist_ok=True)
        os.environ["HF_MODULES_CACHE"] = str(modules_cache)
    if previous["MPLCONFIGDIR"] is None:
        matplotlib_cache = Path(tempfile.gettempdir()) / "table2text_matplotlib"
        matplotlib_cache.mkdir(parents=True, exist_ok=True)
        os.environ["MPLCONFIGDIR"] = str(matplotlib_cache)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def metric_enabled(config: ReferenceMetricConfig, *names: str) -> bool:
    enabled = {name.casefold() for name in config.enabled_metrics}
    return any(name.casefold() in enabled for name in names)


def local_huggingface_snapshot(model_name_or_path: str) -> str:
    path = Path(model_name_or_path)
    if path.exists():
        return str(path)

    from huggingface_hub import snapshot_download

    return snapshot_download(
        repo_id=model_name_or_path,
        local_files_only=True,
    )


def _primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _clean_label(value: str) -> str:
    value = re.sub(r"[_./]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _primitive_items(mapping: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [
        (_clean_label(str(key)), value)
        for key, value in mapping.items()
        if _primitive(value)
        and str(value).strip()
        and str(value).strip().lower() not in {"none", "null"}
    ]


def _format_items(
    items: list[tuple[str, Any]],
    *,
    skip: set[str] | None = None,
    maximum: int = 16,
) -> str:
    skip = {item.casefold() for item in (skip or set())}
    parts = [
        f"{key} {value}"
        for key, value in items
        if key.casefold() not in skip
    ]
    return ", ".join(parts[:maximum])


def _format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else str(value)


def _team_score(payload: Mapping[str, Any]) -> Any | None:
    line_score = payload.get("line_score")
    if not isinstance(line_score, Mapping):
        return None
    game = line_score.get("game")
    if not isinstance(game, Mapping):
        return None
    return game.get("PTS") or game.get("points") or game.get("score")


def _event_participants(payload: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    for key in ("teams", "participants", "sides", "competitors"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            participants = [
                (str(role), record)
                for role, record in value.items()
                if isinstance(record, Mapping)
            ]
            if participants:
                return participants
    return []


def _named_records(value: Any) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    if isinstance(value, Mapping):
        if "name" in value and any(
            isinstance(item, (int, float, str))
            and str(item).strip()
            for key, item in value.items()
            if key != "name"
        ):
            records.append(value)
        for item in value.values():
            records.extend(_named_records(item))
    elif isinstance(value, list):
        for item in value:
            records.extend(_named_records(item))
    return records


def _event_source_context_from_json(payload: Any) -> str | None:
    if not isinstance(payload, Mapping):
        return None

    lines: list[str] = []
    game = payload.get("game")
    if isinstance(game, Mapping):
        context = _format_items(
            _primitive_items(game),
            maximum=20,
        )
        if context:
            lines.append(f"Event context: {context}.")

    participants = _event_participants(payload)
    participant_scores: list[tuple[str, str, float]] = []
    for role, participant in participants:
        name = (
            participant.get("place")
            or participant.get("name")
            or participant.get("team")
            or role
        )
        score = _team_score(participant)
        if score is not None:
            try:
                participant_scores.append((role, str(name), float(score)))
            except (TypeError, ValueError):
                pass
        totals = []
        line_score = participant.get("line_score")
        if isinstance(line_score, Mapping):
            game_totals = line_score.get("game")
            if isinstance(game_totals, Mapping):
                totals = _primitive_items(game_totals)
        if totals:
            lines.append(
                f"{role} participant {name} game totals: "
                f"{_format_items(totals, maximum=18)}."
            )
        for segment_name, segment in (
            line_score.items()
            if isinstance(line_score, Mapping)
            else []
        ):
            if not isinstance(segment, Mapping) or segment_name == "game":
                continue
            points = (
                segment.get("PTS")
                or segment.get("points")
                or segment.get("score")
            )
            if points is not None:
                lines.append(
                    f"{role} participant {name} {segment_name} points {points}."
                )

    if len(participant_scores) >= 2:
        ordered = sorted(
            participant_scores,
            key=lambda item: item[2],
            reverse=True,
        )
        winner = ordered[0]
        loser = ordered[-1]
        margin = winner[2] - loser[2]
        if margin.is_integer():
            margin_text = str(int(margin))
        else:
            margin_text = str(margin)
        lines.insert(
            0,
            (
                f"Event result: {winner[1]} scored {_format_number(winner[2])} "
                f"and {loser[1]} scored {_format_number(loser[2])}; "
                f"the margin was {margin_text}."
            ),
        )

    for record in _named_records(payload):
        name = record.get("name")
        if not name:
            continue
        values = _format_items(
            _primitive_items(record),
            skip={"name", "first name", "last name"},
            maximum=22,
        )
        if values:
            lines.append(f"Record for {name}: {values}.")

    if not lines:
        return None
    return "\n".join(dict.fromkeys(lines))


def normalized_event_source_context(record: GenerationRecord) -> str | None:
    if record.task_family not in {
        TaskFamily.EVENT_REPORT,
        TaskFamily.CROSS_LINGUAL_EVENT_REPORT,
    }:
        return None
    try:
        payload = json.loads(record.source_text)
    except json.JSONDecodeError:
        return None
    return _event_source_context_from_json(payload)


def factuality_context(record: GenerationRecord, config: ReferenceMetricConfig) -> str:
    if config.external_factuality_context == "references" and record.references:
        source = "\n".join(
            reference.strip()
            for reference in record.references
            if reference.strip()
        )
    else:
        source = (
            normalized_event_source_context(record)
            if config.external_factuality_context == "source_text"
            else None
        ) or record.source_text.strip()
    limit = config.external_context_max_characters
    if len(source) <= limit:
        return source
    return source[:limit] + "\n\n[Source truncated by reference metric configuration.]"


def metric_status(value: str) -> MetricStatus:
    try:
        return MetricStatus(value)
    except ValueError:
        return MetricStatus.ERROR


def hhem_observations(
    record: GenerationRecord,
    result: ExternalFactualityResult,
    *,
    duration: float,
) -> list[MetricObservation]:
    status = metric_status(result.status)
    details = result.details | {
        "metric_group": result.metric_name,
        "threshold": result.threshold,
    }
    outputs = [
        (
            f"{result.metric_name}_mean_support",
            result.overall_score,
            True,
        ),
        (
            f"{result.metric_name}_min_sentence_support",
            result.minimum_sentence_score,
            True,
        ),
        (
            f"{result.metric_name}_unsupported_sentence_rate",
            result.unsupported_sentence_rate,
            False,
        ),
    ]
    return [
        observation(
            record,
            family="external_factuality",
            name=name,
            status=status,
            score=score if status == MetricStatus.SCORED else None,
            higher_is_better=higher_is_better,
            duration=duration,
            details=details | {"sentence_scores": result.sentence_scores},
            error=result.error,
        )
        for name, score, higher_is_better in outputs
    ]


def alignscore_observation(
    record: GenerationRecord,
    result: ExternalFactualityResult,
    *,
    duration: float,
) -> MetricObservation:
    return observation(
        record,
        family="external_factuality",
        name=result.metric_name,
        status=metric_status(result.status),
        score=result.overall_score if result.status == "scored" else None,
        higher_is_better=True,
        duration=duration,
        details=result.details | {"threshold": result.threshold},
        error=result.error,
    )


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
        with huggingface_offline(config.hf_local_files_only):
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
                model_name = config.bertscore_model
                model_type = config.bertscore_model
                if config.hf_local_files_only:
                    model_type = local_huggingface_snapshot(model_type)
                kwargs["model_type"] = model_type
                if config.bertscore_num_layers is not None:
                    kwargs["num_layers"] = config.bertscore_num_layers
                elif model_type != model_name:
                    from bert_score.utils import model2layers

                    if model_name in model2layers:
                        kwargs["num_layers"] = model2layers[model_name]
                kwargs["rescale_with_baseline"] = False
            else:
                kwargs["lang"] = language.split("-")[0]
                kwargs["rescale_with_baseline"] = config.bertscore_rescale_with_baseline
            if config.bertscore_device:
                kwargs["device"] = config.bertscore_device
            with huggingface_offline(config.hf_local_files_only):
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


def score_hhem_records(
    records: list[GenerationRecord],
    config: ReferenceMetricConfig,
) -> list[MetricObservation]:
    if not metric_enabled(config, "hhem", "hhem_2_1_open"):
        return []

    evaluator = HHEMEvaluator(
        model_name=config.hhem_model,
        foundation_model_name=config.hhem_foundation_model,
        threshold=config.hhem_threshold,
        batch_size=config.hhem_batch_size,
        device=config.hhem_device,
        local_files_only=config.hf_local_files_only,
        max_context_characters=config.hhem_context_max_characters,
    )
    observations: list[MetricObservation] = []
    for record in records:
        started = time.perf_counter()
        result = evaluator.evaluate(
            context=factuality_context(record, config),
            generated_text=plain_text(record.generated_text),
        )
        observations.extend(
            hhem_observations(
                record,
                result,
                duration=time.perf_counter() - started,
            )
        )
    del evaluator
    gc.collect()
    return observations


def unavailable_alignscore_observation(
    record: GenerationRecord,
    config: ReferenceMetricConfig,
    *,
    reason: str,
) -> MetricObservation:
    return observation(
        record,
        family="external_factuality",
        name=f"alignscore_{config.alignscore_model_size}",
        status=MetricStatus.UNAVAILABLE,
        details={
            "threshold": config.alignscore_threshold,
            "model_size": config.alignscore_model_size,
        },
        error=reason,
    )


def score_alignscore_records(
    records: list[GenerationRecord],
    config: ReferenceMetricConfig,
) -> list[MetricObservation]:
    if not metric_enabled(config, "alignscore"):
        return []
    if not records:
        return []

    if config.alignscore_python_executable is None:
        discovered_executable = default_alignscore_python_executable()
    else:
        discovered_executable = config.alignscore_python_executable

    if discovered_executable is None:
        reason = (
            "AlignScore requires a separate worker Python executable. "
            "Set reference_metrics.alignscore_python_executable in metrics.json "
            "or create .venv-alignscore in the project root."
        )
        return [
            unavailable_alignscore_observation(record, config, reason=reason)
            for record in records
        ]

    worker_path = config.alignscore_worker_path or DEFAULT_ALIGNSCORE_WORKER
    if not worker_path.exists():
        reason = f"AlignScore worker script was not found at {worker_path}."
        return [
            unavailable_alignscore_observation(record, config, reason=reason)
            for record in records
        ]

    try:
        client = AlignScoreClient(
            python_executable=discovered_executable,
            worker_path=worker_path,
            model_size=config.alignscore_model_size,
            device=config.alignscore_device,
            batch_size=config.alignscore_batch_size,
            threshold=config.alignscore_threshold,
            local_files_only=config.hf_local_files_only,
        )
    except Exception as exc:
        reason = f"{type(exc).__name__}: {exc}"
        return [
            unavailable_alignscore_observation(record, config, reason=reason)
            for record in records
        ]

    observations: list[MetricObservation] = []
    try:
        for record in records:
            started = time.perf_counter()
            try:
                result = client.evaluate(
                    context=factuality_context(record, config),
                    generated_text=plain_text(record.generated_text),
                )
            except Exception as exc:
                result = ExternalFactualityResult(
                    metric_name=f"alignscore_{config.alignscore_model_size}",
                    status="error",
                    threshold=config.alignscore_threshold,
                    error=f"{type(exc).__name__}: {exc}",
                )
            observations.append(
                alignscore_observation(
                    record,
                    result,
                    duration=time.perf_counter() - started,
                )
            )
    finally:
        try:
            client.close()
        except Exception:
            pass
    return observations


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
    observations.extend(score_hhem_records(eligible, config))
    observations.extend(score_alignscore_records(eligible, config))
    observations.extend(score_bertscore(eligible, config))
    observations.extend(corpus_sacrebleu_observations(eligible, config))
    write_jsonl(output_path, observations)
    return observations
