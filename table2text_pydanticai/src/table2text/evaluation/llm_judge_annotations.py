"""Produce structured, source-only factual error annotations with an LLM judge."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Literal

from pydantic import Field

from table2text.config import load_env_files

from .datasets import write_jsonl
from .models import (
    GenerationRecord,
    LLMJudgeAnnotationPayload,
    LLMJudgeAnnotationRecord,
    MetricStatus,
    StrictModel,
)
from .reference_metrics import plain_text


class OpenAIJudgeAnnotationConfig(StrictModel):
    judge_model: str = "gpt-5.6-sol"
    judge_repetitions: int = Field(default=1, ge=1)
    reasoning_effort: Literal[
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
        "max",
    ] = "high"
    max_source_characters: int = Field(default=50_000, ge=1_000)
    max_output_tokens: int = Field(default=2_500, ge=200)
    include_references: bool = False
    include_system_identity: bool = False
    include_metric_scores: bool = False


ERROR_TAXONOMY = """\
Use exactly one category per error:
- NAME: wrong, missing, swapped or misattributed named entity.
- NUMBER: wrong, missing, swapped, rounded incorrectly or unsupported number, date, score, rank, unit or quantity.
- WORD: incorrect word choice that changes the factual meaning, including wrong predicate, relation, role or action.
- CONTEXT: unsupported or incorrect broader interpretation, chronology, comparison, causal implication, trend, scope or situation.
- NOT CHECKABLE: claim cannot be verified from the supplied source data alone.
- OTHER: factual error that does not fit the other categories.
- OMISSION: important source-supported content required by the task is absent from the output.
- TASK/FORMAT: output does not follow the requested task, genre, scope, language or format.
"""


SYSTEM_INSTRUCTIONS = f"""\
You are an independent factual-accuracy annotator for structured data-to-text outputs.

You must inspect one generated output at a time. Use only the supplied source data and task request.
Do not use outside knowledge, web search, hidden references, metric scores, or any other system output.

Return structured JSON matching the requested schema. If the output has no errors, return an empty errors list.

Do not reward or punish style unless it creates a TASK/FORMAT error. Do not require wording to match a human
reference. Do not report harmless paraphrases as errors. Do not infer facts that are not in the source.

For OMISSION, only report missing information when it is clearly required by the task or when omitting it changes
the adequacy of the output. Do not report every unused source field as an omission.

{ERROR_TAXONOMY}
"""


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def _normalise_openai_model_name(model_name: str) -> str:
    if model_name.startswith("openai:"):
        return model_name.split(":", 1)[1]
    return model_name


def source_for_annotation_judge(
    record: GenerationRecord,
    config: OpenAIJudgeAnnotationConfig,
) -> str:
    source = record.source_text
    if len(source) <= config.max_source_characters:
        return source
    return source[: config.max_source_characters] + "\n\n[Source truncated by LLM judge configuration.]"


def build_annotation_judge_input(
    record: GenerationRecord,
    config: OpenAIJudgeAnnotationConfig,
) -> str:
    sections = [
        "TASK",
        f"Dataset ID: {record.dataset_id}",
        f"Example ID: {record.example_id}",
        f"Task family: {getattr(record.task_family, 'value', record.task_family)}",
        f"Output mode: {getattr(record.output_mode, 'value', record.output_mode)}",
        f"Language: {record.language}",
        f"Request: {record.request}",
        "",
        "SOURCE DATA",
        source_for_annotation_judge(record, config),
        "",
        "GENERATED OUTPUT",
        plain_text(record.generated_text),
        "",
        "ERROR TAXONOMY",
        ERROR_TAXONOMY,
    ]
    if config.include_references:
        sections.extend(
            [
                "",
                "HUMAN REFERENCES",
                "\n\n--- ALTERNATIVE REFERENCE ---\n\n".join(record.references),
            ]
        )
    if config.include_system_identity:
        sections.extend(
            [
                "",
                "SYSTEM IDENTITY",
                f"Variant ID: {record.variant_id}",
                f"Writer mode: {record.writer_mode}",
                f"Release status: {record.release_status}",
            ]
        )
    if config.include_metric_scores:
        sections.extend(
            [
                "",
                "SYSTEM METADATA",
                f"Audit support rate: {record.audit_support_rate}",
                f"Repair rounds used: {record.repair_rounds_used}",
            ]
        )
    return "\n".join(sections)


def _usage_value(usage: object, name: str) -> int | None:
    value = getattr(usage, name, None)
    return int(value) if value is not None else None


def _parsed_payload(response: object) -> LLMJudgeAnnotationPayload:
    parsed = getattr(response, "output_parsed", None)
    if parsed is not None:
        return LLMJudgeAnnotationPayload.model_validate(parsed)

    for output in getattr(response, "output", []) or []:
        if getattr(output, "type", None) != "message":
            continue
        for item in getattr(output, "content", []) or []:
            parsed = getattr(item, "parsed", None)
            if parsed is not None:
                return LLMJudgeAnnotationPayload.model_validate(parsed)
    raise RuntimeError("OpenAI response did not contain parsed structured output.")


def _make_record(
    record: GenerationRecord,
    config: OpenAIJudgeAnnotationConfig,
    *,
    judge_repetition: int,
    status: MetricStatus,
    payload: LLMJudgeAnnotationPayload | None = None,
    duration: float | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    total_tokens: int | None = None,
    error: str | None = None,
) -> LLMJudgeAnnotationRecord:
    errors = payload.errors if payload is not None else []
    return LLMJudgeAnnotationRecord(
        generation_id=record.generation_id,
        dataset_id=record.dataset_id,
        example_id=record.example_id,
        variant_id=record.variant_id,
        repetition=record.repetition,
        judge_model=config.judge_model,
        judge_repetition=judge_repetition,
        status=status,
        errors=errors,
        error_count=len(errors),
        duration_seconds=duration,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        error=error,
    )


def annotate_record_with_openai_judge(
    record: GenerationRecord,
    config: OpenAIJudgeAnnotationConfig,
    *,
    judge_repetition: int,
) -> LLMJudgeAnnotationRecord:
    started = time.perf_counter()
    try:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The openai package is required to run OpenAI LLM judge annotations."
            ) from exc

        api_key = _first_env("OPENAI_API_KEY", "T2T_OPENAI_API_KEY")
        if api_key is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not set in the environment or project .env file."
            )

        client = OpenAI(
            api_key=api_key,
            base_url=_first_env("OPENAI_BASE_URL", "T2T_OPENAI_BASE_URL"),
        )
        response = client.responses.parse(
            model=_normalise_openai_model_name(config.judge_model),
            instructions=SYSTEM_INSTRUCTIONS,
            input=build_annotation_judge_input(record, config),
            text_format=LLMJudgeAnnotationPayload,
            reasoning={"effort": config.reasoning_effort},
            max_output_tokens=config.max_output_tokens,
            store=False,
        )
        payload = _parsed_payload(response)
        usage = getattr(response, "usage", None)
        return _make_record(
            record,
            config,
            judge_repetition=judge_repetition,
            status=MetricStatus.SCORED,
            payload=payload,
            duration=time.perf_counter() - started,
            input_tokens=_usage_value(usage, "input_tokens") if usage else None,
            output_tokens=_usage_value(usage, "output_tokens") if usage else None,
            total_tokens=_usage_value(usage, "total_tokens") if usage else None,
        )
    except Exception as exc:
        return _make_record(
            record,
            config,
            judge_repetition=judge_repetition,
            status=MetricStatus.ERROR,
            duration=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def annotate_generations_with_openai_judge(
    records: list[GenerationRecord],
    config: OpenAIJudgeAnnotationConfig,
    output_path: Path,
    *,
    resume: bool = True,
) -> list[LLMJudgeAnnotationRecord]:
    load_env_files()
    existing: dict[tuple[str, str, int], LLMJudgeAnnotationRecord] = {}
    if resume and output_path.exists():
        for line in output_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = LLMJudgeAnnotationRecord.model_validate_json(line)
                existing[(item.generation_id, item.judge_model, item.judge_repetition)] = item

    annotations = dict(existing)
    for record in records:
        if record.error is not None or not record.generated_text.strip():
            continue
        if record.primary_evaluation_eligible is False:
            continue
        for judge_repetition in range(config.judge_repetitions):
            key = (record.generation_id, config.judge_model, judge_repetition)
            if resume and key in annotations:
                continue
            annotations[key] = annotate_record_with_openai_judge(
                record,
                config,
                judge_repetition=judge_repetition,
            )
            write_jsonl(output_path, annotations.values())

    ordered = sorted(
        annotations.values(),
        key=lambda item: (
            item.dataset_id,
            item.example_id,
            item.variant_id,
            item.repetition,
            item.judge_model,
            item.judge_repetition,
        ),
    )
    write_jsonl(output_path, ordered)
    return ordered
