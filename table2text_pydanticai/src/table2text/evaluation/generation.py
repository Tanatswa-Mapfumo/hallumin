from __future__ import annotations

import importlib
import json
import os
import subprocess
import tempfile
import time
from dataclasses import fields, replace
from pathlib import Path
from typing import Any, Callable

from .datasets import write_jsonl
from .models import (
    BenchmarkExample,
    GenerationBackend,
    GenerationRecord,
    OutputMode,
    TaskFamily,
    VariantConfig,
)


def load_variants(path: Path) -> list[VariantConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("variants", payload)
    if not isinstance(payload, list):
        raise ValueError("The variant configuration must be a list.")
    return [VariantConfig.model_validate(item) for item in payload]


def plain_generation_id(
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
) -> str:
    return (
        f"{example.dataset_id}__{example.example_id}__"
        f"{variant.variant_id}__r{repetition}__s{seed}"
    )


def materialise_input(example: BenchmarkExample, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{example.dataset_id}__{example.example_id}.json"
    if example.task_family in {
        TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
        TaskFamily.ATTRIBUTE_VERBALISATION,
        TaskFamily.TRIPLE_VERBALISATION,
    }:
        payload = {
            "__table2text_benchmark_example__": True,
            "dataset_id": example.dataset_id,
            "example_id": example.example_id,
            "task_family": example.task_family.value,
            "output_mode": example.output_mode.value,
            "request": example.request,
            "source_text": example.source_text,
            "source_payload": example.source_payload,
            "parent_table": example.parent_table,
            "metadata": example.metadata,
        }
    else:
        payload = example.source_payload
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def report_genre_for_task(task_family: TaskFamily) -> Any:
    from table2text.schemas import ReportGenre

    if task_family in {TaskFamily.EVENT_REPORT, TaskFamily.CROSS_LINGUAL_EVENT_REPORT}:
        return ReportGenre.EVENT_REPORT
    if task_family in {TaskFamily.LONG_FORM_TABLE_REPORT, TaskFamily.ANALYTICAL_EXPLANATION}:
        return ReportGenre.DATA_SCIENCE_REPORT
    return ReportGenre.DATASET_OVERVIEW


def communication_task_for_task(task_family: TaskFamily) -> Any:
    from table2text.schemas import CommunicationTask

    mapping = {
        TaskFamily.EVENT_REPORT: CommunicationTask.EVENT_REPORT,
        TaskFamily.CROSS_LINGUAL_EVENT_REPORT: CommunicationTask.EVENT_REPORT,
        TaskFamily.LONG_FORM_TABLE_REPORT: CommunicationTask.DATA_SCIENCE_REPORT,
        TaskFamily.ANALYTICAL_EXPLANATION: CommunicationTask.DATA_SCIENCE_REPORT,
        TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION: (
            CommunicationTask.FOCUSED_TABLE_DESCRIPTION
        ),
        TaskFamily.LOGICAL_TABLE_STATEMENT: CommunicationTask.TABLE_ENTAILMENT,
        TaskFamily.TABLE_QUESTION_ANSWERING: (
            CommunicationTask.TABLE_QUESTION_ANSWERING
        ),
        TaskFamily.ATTRIBUTE_VERBALISATION: (
            CommunicationTask.ATTRIBUTE_VERBALISATION
        ),
        TaskFamily.TRIPLE_VERBALISATION: (
            CommunicationTask.TRIPLE_VERBALISATION
        ),
    }
    return mapping.get(task_family, CommunicationTask.CUSTOM)


def output_form_for_mode(output_mode: Any) -> Any:
    from table2text.schemas import OutputForm

    mapping = {
        OutputMode.ONE_SENTENCE: OutputForm.ONE_SENTENCE,
        OutputMode.DIRECT_ANSWER: OutputForm.DIRECT_ANSWER,
        OutputMode.SHORT_TEXT: OutputForm.SHORT_TEXT,
        OutputMode.PARAGRAPH: OutputForm.PARAGRAPH,
        OutputMode.MULTI_PARAGRAPH_REPORT: (
            OutputForm.MULTI_PARAGRAPH_REPORT
        ),
    }
    return mapping.get(output_mode, OutputForm.MULTI_PARAGRAPH_REPORT)


def focus_scope_for_task(task_family: TaskFamily) -> str | None:
    if task_family in {
        TaskFamily.EVENT_REPORT,
        TaskFamily.CROSS_LINGUAL_EVENT_REPORT,
    }:
        return "reference_recap"
    if task_family == TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION:
        return "highlighted_cells"
    return None


def valid_setting_names() -> set[str]:
    from table2text.config import Settings

    return {field.name for field in fields(Settings)}


def _base_generation_record(
    *,
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
    generated_text: str,
    backend: GenerationBackend,
    elapsed_seconds: float | None = None,
    metadata: dict[str, Any] | None = None,
    error: str | None = None,
) -> GenerationRecord:
    return GenerationRecord(
        generation_id=plain_generation_id(example, variant, repetition, seed),
        dataset_id=example.dataset_id,
        example_id=example.example_id,
        variant_id=variant.variant_id,
        repetition=repetition,
        seed=seed,
        task_family=example.task_family,
        output_mode=example.output_mode,
        language=example.language,
        source_text=example.source_text,
        references=example.references,
        parent_table=example.parent_table,
        request=example.request,
        generated_text=generated_text,
        backend=backend,
        elapsed_seconds=elapsed_seconds,
        metadata=metadata or {},
        error=error,
    )


def table2text_generate(
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
    run_root: Path,
) -> GenerationRecord:
    from table2text import Settings, Table2TextWorkflow
    from table2text.schemas import AuditMode, EvaluationFieldPolicy

    started = time.perf_counter()
    try:
        settings = Settings.from_env()
        overrides = {
            **variant.settings_overrides,
            "random_seed": seed,
            "output_dir": run_root / variant.variant_id / example.dataset_id,
        }
        unknown = set(overrides) - valid_setting_names()
        if unknown:
            raise ValueError(
                f"Variant `{variant.variant_id}` contains unknown Settings fields: "
                f"{sorted(unknown)}."
            )
        settings = replace(settings, **overrides)
        input_path = materialise_input(example, run_root / "_inputs")
        workflow = Table2TextWorkflow(settings)
        result = workflow.run_sync(
            inputs=[input_path],
            request=example.request,
            audit_mode=AuditMode.INTERNAL,
            evaluation_field_policy=EvaluationFieldPolicy(
                operational_input_paths=["$"],
                held_out_reference_paths=[],
                metadata_paths=[],
            ),
            report_genre=report_genre_for_task(example.task_family),
            communication_task=communication_task_for_task(
                example.task_family
            ),
            output_form=output_form_for_mode(example.output_mode),
            focus_scope=focus_scope_for_task(example.task_family),
        )
        output = result.final_writer_output
        pipeline_result_path = settings.output_dir / result.run_id / "pipeline_result.json"
        pipeline_result_path.parent.mkdir(parents=True, exist_ok=True)
        pipeline_result_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

        fact_ids = {fact.fact_id for fact in result.fact_ledger.writer_ready_facts}
        evidence_ids = {item.evidence_id for item in result.evidence_ledger.items}
        referenced_fact_ids = [
            fact_id for support in output.sentence_support for fact_id in support.fact_ids
        ]
        referenced_evidence_ids = [
            evidence_id
            for support in output.sentence_support
            for evidence_id in support.evidence_ids
        ]
        mapped_support_count = sum(
            bool(
                support.fact_ids
                or support.evidence_ids
                or support.profile_support_ids
                or support.insight_ids
            )
            for support in output.sentence_support
        )
        base = _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text=output.markdown,
            backend=GenerationBackend.TABLE2TEXT,
            elapsed_seconds=time.perf_counter() - started,
        )
        return base.model_copy(
            update={
                "run_id": result.run_id,
                "pipeline_result_path": pipeline_result_path,
                "writer_mode": output.writer_mode,
                "release_status": result.release_status.value,
                "approved_for_release": result.approved_for_release,
                "primary_evaluation_eligible": (
                    result.primary_evaluation_eligible
                    and output.eligible_for_primary_evaluation
                ),
                "primary_evaluation_reason": result.primary_evaluation_reason,
                "repair_rounds_used": result.repair_rounds_used,
                "audit_support_rate": result.final_audit.support_rate,
                "support_sentence_count": len(output.sentence_support),
                "mapped_support_sentence_count": mapped_support_count,
                "fact_id_reference_count": len(referenced_fact_ids),
                "evidence_id_reference_count": len(referenced_evidence_ids),
                "invalid_fact_id_count": sum(
                    fact_id not in fact_ids for fact_id in referenced_fact_ids
                ),
                "invalid_evidence_id_count": sum(
                    evidence_id not in evidence_ids
                    for evidence_id in referenced_evidence_ids
                ),
                "metadata": {
                    "title": output.title,
                    "selected_fact_count": len(output.selected_fact_ids),
                    "omitted_fact_count": len(output.omitted_fact_ids),
                    "quality_revision_round": output.quality_revision_round,
                },
            }
        )
    except Exception as exc:
        return _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text="",
            backend=GenerationBackend.TABLE2TEXT,
            elapsed_seconds=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


async def table2text_generate_async(
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
    run_root: Path,
) -> GenerationRecord:
    from table2text import Settings, Table2TextWorkflow
    from table2text.schemas import AuditMode, EvaluationFieldPolicy

    started = time.perf_counter()
    try:
        settings = Settings.from_env()
        overrides = {
            **variant.settings_overrides,
            "random_seed": seed,
            "output_dir": run_root / variant.variant_id / example.dataset_id,
        }
        unknown = set(overrides) - valid_setting_names()
        if unknown:
            raise ValueError(
                f"Variant `{variant.variant_id}` contains unknown Settings fields: "
                f"{sorted(unknown)}."
            )
        settings = replace(settings, **overrides)
        input_path = materialise_input(example, run_root / "_inputs")
        workflow = Table2TextWorkflow(settings)
        result = await workflow.run(
            inputs=[input_path],
            request=example.request,
            audit_mode=AuditMode.INTERNAL,
            evaluation_field_policy=EvaluationFieldPolicy(
                operational_input_paths=["$"],
                held_out_reference_paths=[],
                metadata_paths=[],
            ),
            report_genre=report_genre_for_task(example.task_family),
            communication_task=communication_task_for_task(
                example.task_family
            ),
            output_form=output_form_for_mode(example.output_mode),
            focus_scope=focus_scope_for_task(example.task_family),
        )
        output = result.final_writer_output
        pipeline_result_path = settings.output_dir / result.run_id / "pipeline_result.json"
        pipeline_result_path.parent.mkdir(parents=True, exist_ok=True)
        pipeline_result_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

        fact_ids = {fact.fact_id for fact in result.fact_ledger.writer_ready_facts}
        evidence_ids = {item.evidence_id for item in result.evidence_ledger.items}
        referenced_fact_ids = [
            fact_id for support in output.sentence_support for fact_id in support.fact_ids
        ]
        referenced_evidence_ids = [
            evidence_id
            for support in output.sentence_support
            for evidence_id in support.evidence_ids
        ]
        mapped_support_count = sum(
            bool(
                support.fact_ids
                or support.evidence_ids
                or support.profile_support_ids
                or support.insight_ids
            )
            for support in output.sentence_support
        )
        base = _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text=output.markdown,
            backend=GenerationBackend.TABLE2TEXT,
            elapsed_seconds=time.perf_counter() - started,
        )
        return base.model_copy(
            update={
                "run_id": result.run_id,
                "pipeline_result_path": pipeline_result_path,
                "writer_mode": output.writer_mode,
                "release_status": result.release_status.value,
                "approved_for_release": result.approved_for_release,
                "primary_evaluation_eligible": (
                    result.primary_evaluation_eligible
                    and output.eligible_for_primary_evaluation
                ),
                "primary_evaluation_reason": result.primary_evaluation_reason,
                "repair_rounds_used": result.repair_rounds_used,
                "audit_support_rate": result.final_audit.support_rate,
                "support_sentence_count": len(output.sentence_support),
                "mapped_support_sentence_count": mapped_support_count,
                "fact_id_reference_count": len(referenced_fact_ids),
                "evidence_id_reference_count": len(referenced_evidence_ids),
                "invalid_fact_id_count": sum(
                    fact_id not in fact_ids for fact_id in referenced_fact_ids
                ),
                "invalid_evidence_id_count": sum(
                    evidence_id not in evidence_ids
                    for evidence_id in referenced_evidence_ids
                ),
                "metadata": {
                    "title": output.title,
                    "selected_fact_count": len(output.selected_fact_ids),
                    "omitted_fact_count": len(output.omitted_fact_ids),
                    "quality_revision_round": output.quality_revision_round,
                },
            }
        )
    except Exception as exc:
        return _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text="",
            backend=GenerationBackend.TABLE2TEXT,
            elapsed_seconds=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def resolve_callable(dotted_path: str) -> Callable[..., Any]:
    module_name, separator, attribute_name = dotted_path.rpartition(".")
    if not separator:
        raise ValueError("callable_path must be formatted as `package.module.function`.")
    module = importlib.import_module(module_name)
    value = getattr(module, attribute_name)
    if not callable(value):
        raise TypeError(f"{dotted_path} is not callable.")
    return value


def callable_generate(
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
) -> GenerationRecord:
    assert variant.callable_path is not None
    started = time.perf_counter()
    try:
        function = resolve_callable(variant.callable_path)
        result = function(example=example, variant=variant, repetition=repetition, seed=seed)
        if isinstance(result, str):
            text = result
            metadata: dict[str, Any] = {}
        elif isinstance(result, dict):
            text = str(result.get("generated_text", ""))
            metadata = {key: value for key, value in result.items() if key != "generated_text"}
        else:
            raise TypeError("A generation callable must return a string or dictionary.")
        return _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text=text,
            backend=GenerationBackend.CALLABLE,
            elapsed_seconds=time.perf_counter() - started,
            metadata=metadata,
        )
    except Exception as exc:
        return _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text="",
            backend=GenerationBackend.CALLABLE,
            elapsed_seconds=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def command_generate(
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
) -> GenerationRecord:
    started = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = root / "request.json"
            response_path = root / "response.json"
            request_path.write_text(
                json.dumps(
                    {
                        "example": example.model_dump(mode="json"),
                        "variant": variant.model_dump(mode="json"),
                        "repetition": repetition,
                        "seed": seed,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            replacements = {
                "{request_json}": str(request_path),
                "{response_json}": str(response_path),
                "{seed}": str(seed),
            }
            command = []
            for part in variant.command:
                rendered = part
                for old, new in replacements.items():
                    rendered = rendered.replace(old, new)
                command.append(rendered)
            completed = subprocess.run(
                command,
                check=False,
                text=True,
                capture_output=True,
                env={**os.environ, "TABLE2TEXT_EVALUATION_SEED": str(seed)},
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"Command exited with {completed.returncode}: {completed.stderr.strip()}"
                )
            if response_path.exists():
                response = json.loads(response_path.read_text(encoding="utf-8"))
                text = str(response.get("generated_text", ""))
                metadata = {key: value for key, value in response.items() if key != "generated_text"}
            else:
                text = completed.stdout.strip()
                metadata = {"stderr": completed.stderr}
        return _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text=text,
            backend=GenerationBackend.COMMAND,
            elapsed_seconds=time.perf_counter() - started,
            metadata=metadata,
        )
    except Exception as exc:
        return _base_generation_record(
            example=example,
            variant=variant,
            repetition=repetition,
            seed=seed,
            generated_text="",
            backend=GenerationBackend.COMMAND,
            elapsed_seconds=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def load_precomputed(path: Path) -> dict[tuple[str, str, int], GenerationRecord]:
    result: dict[tuple[str, str, int], GenerationRecord] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = GenerationRecord.model_validate(json.loads(line))
        result[(record.dataset_id, record.example_id, record.repetition)] = record
    return result


def seeds_for_variant(variant: VariantConfig) -> list[int]:
    if variant.seeds:
        if len(variant.seeds) < variant.repetitions:
            raise ValueError(f"{variant.variant_id}: not enough seeds for the requested repetitions.")
        return variant.seeds[: variant.repetitions]
    return [42 + repetition for repetition in range(variant.repetitions)]


def generate_all(
    examples: list[BenchmarkExample],
    variants: list[VariantConfig],
    output_path: Path,
    run_root: Path,
    *,
    resume: bool = True,
) -> list[GenerationRecord]:
    existing: dict[str, GenerationRecord] = {}
    if resume and output_path.exists():
        for line in output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = GenerationRecord.model_validate(json.loads(line))
            existing[record.generation_id] = record
    records = dict(existing)
    for variant in variants:
        if not variant.enabled:
            continue
        precomputed = (
            load_precomputed(variant.precomputed_path)
            if variant.backend == GenerationBackend.PRECOMPUTED
            and variant.precomputed_path is not None
            and variant.precomputed_path.exists()
            else {}
        )
        for example in examples:
            for repetition, seed in enumerate(seeds_for_variant(variant)):
                generation_id = plain_generation_id(example, variant, repetition, seed)
                if generation_id in records:
                    continue
                if variant.backend == GenerationBackend.TABLE2TEXT:
                    record = table2text_generate(example, variant, repetition, seed, run_root)
                elif variant.backend == GenerationBackend.CALLABLE:
                    record = callable_generate(example, variant, repetition, seed)
                elif variant.backend == GenerationBackend.COMMAND:
                    record = command_generate(example, variant, repetition, seed)
                elif variant.backend == GenerationBackend.PRECOMPUTED:
                    key = (example.dataset_id, example.example_id, repetition)
                    if key in precomputed:
                        record = precomputed[key].model_copy(
                            update={
                                "generation_id": generation_id,
                                "variant_id": variant.variant_id,
                                "seed": seed,
                            }
                        )
                    else:
                        record = _base_generation_record(
                            example=example,
                            variant=variant,
                            repetition=repetition,
                            seed=seed,
                            generated_text="",
                            backend=GenerationBackend.PRECOMPUTED,
                            error="No matching precomputed generation was found.",
                        )
                else:
                    raise ValueError(f"Unsupported backend: {variant.backend}")
                records[generation_id] = record
                write_jsonl(output_path, records.values())

    ordered = sorted(
        records.values(),
        key=lambda item: (item.dataset_id, item.example_id, item.variant_id, item.repetition),
    )
    write_jsonl(output_path, ordered)
    return ordered


async def generate_all_async(
    examples: list[BenchmarkExample],
    variants: list[VariantConfig],
    output_path: Path,
    run_root: Path,
    *,
    resume: bool = True,
) -> list[GenerationRecord]:
    existing: dict[str, GenerationRecord] = {}
    if resume and output_path.exists():
        for line in output_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = GenerationRecord.model_validate(json.loads(line))
            existing[record.generation_id] = record
    records = dict(existing)
    for variant in variants:
        if not variant.enabled:
            continue
        precomputed = (
            load_precomputed(variant.precomputed_path)
            if variant.backend == GenerationBackend.PRECOMPUTED
            and variant.precomputed_path is not None
            and variant.precomputed_path.exists()
            else {}
        )
        for example in examples:
            for repetition, seed in enumerate(seeds_for_variant(variant)):
                generation_id = plain_generation_id(example, variant, repetition, seed)
                if generation_id in records:
                    continue
                if variant.backend == GenerationBackend.TABLE2TEXT:
                    record = await table2text_generate_async(
                        example,
                        variant,
                        repetition,
                        seed,
                        run_root,
                    )
                elif variant.backend == GenerationBackend.CALLABLE:
                    record = callable_generate(example, variant, repetition, seed)
                elif variant.backend == GenerationBackend.COMMAND:
                    record = command_generate(example, variant, repetition, seed)
                elif variant.backend == GenerationBackend.PRECOMPUTED:
                    key = (example.dataset_id, example.example_id, repetition)
                    if key in precomputed:
                        record = precomputed[key].model_copy(
                            update={
                                "generation_id": generation_id,
                                "variant_id": variant.variant_id,
                                "seed": seed,
                            }
                        )
                    else:
                        record = _base_generation_record(
                            example=example,
                            variant=variant,
                            repetition=repetition,
                            seed=seed,
                            generated_text="",
                            backend=GenerationBackend.PRECOMPUTED,
                            error="No matching precomputed generation was found.",
                        )
                else:
                    raise ValueError(f"Unsupported backend: {variant.backend}")
                records[generation_id] = record
                write_jsonl(output_path, records.values())

    ordered = sorted(
        records.values(),
        key=lambda item: (item.dataset_id, item.example_id, item.variant_id, item.repetition),
    )
    write_jsonl(output_path, ordered)
    return ordered


def read_generations(path: Path) -> list[GenerationRecord]:
    return [
        GenerationRecord.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
