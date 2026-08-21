"""Prepare heterogeneous benchmark datasets as canonical evaluation examples."""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .models import (
    BenchmarkExample,
    DatasetConfig,
    DatasetPreparationStatus,
    DatasetSource,
    MetricStatus,
    OutputMode,
    TaskFamily,
)


REFERENCE_FIELD_NAMES = {
    "answer",
    "answers",
    "article",
    "description",
    "descriptions",
    "gold",
    "news_article",
    "ref",
    "reference",
    "references",
    "summary",
    "summaries",
    "summary_de",
    "summary_en",
    "target",
    "targets",
    "text",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def compact_json(value: Any) -> str:
    return json.dumps(
        json_safe(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def pretty_json(value: Any) -> str:
    return json.dumps(json_safe(value), ensure_ascii=False, sort_keys=True, indent=2)


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, dict):
        results: list[str] = []
        for candidate in (
            "text",
            "target",
            "reference",
            "final_sentence",
            "answer",
            "summary",
            "news_article",
        ):
            if candidate in value:
                results.extend(as_string_list(value[candidate]))
        return results
    if isinstance(value, list | tuple):
        results: list[str] = []
        for item in value:
            results.extend(as_string_list(item))
        return results
    return [str(value)]


def deduplicate_strings(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = re.sub(r"\s+", " ", value).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def value_at_path(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def references_from_row(row: dict[str, Any], config: DatasetConfig) -> list[str]:
    values: list[str] = []
    for field in config.reference_fields:
        candidate = value_at_path(row, field)
        if candidate is not None:
            values.extend(as_string_list(candidate))

    if config.normalizer == "sportsett":
        values.extend(as_string_list(row.get("summaries")))
    if config.normalizer == "totto":
        for annotation in row.get("sentence_annotations", []) or []:
            if isinstance(annotation, dict):
                values.extend(as_string_list(annotation.get("final_sentence")))
    if config.normalizer == "rotowire_en_de":
        if config.language.casefold().startswith("de"):
            values.extend(as_string_list(row.get("summary_de")))
        else:
            values.extend(as_string_list(row.get("summary_en")))
    if config.normalizer == "turku_hockey":
        values.extend(as_string_list(row.get("news_article")))

    return deduplicate_strings(values)


def example_id_from_row(row: dict[str, Any], config: DatasetConfig, index: int) -> str:
    for field in [*config.group_fields, *config.id_fields]:
        candidate = value_at_path(row, field)
        if candidate not in (None, ""):
            return str(candidate)
    source_key = compact_json(source_payload_from_row(row, config))
    return f"{config.dataset_id}-{sha256_text(source_key)[:16]}-{index}"


def parse_meaning_representation(value: str) -> list[list[str]]:
    pattern = re.compile(r"([A-Za-z0-9 _-]+)\[([^\]]*)\]")
    pairs = [[key.strip(), item.strip()] for key, item in pattern.findall(value)]
    return pairs or [["meaning_representation", value]]


def triples_to_parent_table(value: Any) -> list[list[str]] | None:
    if not isinstance(value, list):
        return None
    rows: list[list[str]] = []
    for item in value:
        if isinstance(item, list | tuple):
            if len(item) >= 3:
                rows.append([str(item[0]), str(item[1]), str(item[2])])
            elif item:
                rows.append([str(part) for part in item])
        elif isinstance(item, dict):
            subject = item.get("subject") or item.get("head") or item.get("s")
            relation = (
                item.get("relation")
                or item.get("predicate")
                or item.get("property")
                or item.get("r")
            )
            obj = item.get("object") or item.get("tail") or item.get("value") or item.get("o")
            if subject is not None and relation is not None and obj is not None:
                rows.append([str(subject), str(relation), str(obj)])
    return rows or None


def totto_parent_table(row: dict[str, Any]) -> list[list[str]] | None:
    table = row.get("table")
    if not isinstance(table, list):
        return None
    result: list[list[str]] = []
    for table_row in table:
        if not isinstance(table_row, list):
            continue
        values = [
            str(cell.get("value", "")) if isinstance(cell, dict) else str(cell)
            for cell in table_row
        ]
        result.append(values)
    return result or None


def flat_parent_table(payload: Any) -> list[list[str]] | None:
    if not isinstance(payload, dict):
        return None
    rows = [
        [str(key), str(value)]
        for key, value in payload.items()
        if isinstance(value, str | int | float | bool)
    ]
    return rows or None


def source_payload_from_row(row: dict[str, Any], config: DatasetConfig) -> Any:
    normalizer = config.normalizer
    if normalizer == "sportsett":
        return {"game": json_safe(row.get("game")), "teams": json_safe(row.get("teams"))}
    if normalizer == "mlb":
        excluded = {*config.reference_fields, "summary", "summary_eval", "target", "references"}
        return {key: json_safe(value) for key, value in row.items() if key not in excluded}
    if normalizer == "totto":
        return {
            "table_page_title": row.get("table_page_title"),
            "table_section_title": row.get("table_section_title"),
            "table_section_text": row.get("table_section_text"),
            "table": json_safe(row.get("table")),
            "highlighted_cells": json_safe(row.get("highlighted_cells")),
        }
    if normalizer in {"e2e", "viggo"}:
        field = "meaning_representation" if "meaning_representation" in row else "mr"
        return {"meaning_representation": row.get(field)}
    if normalizer in {"webnlg", "dart"}:
        triples = row.get("input") if normalizer == "webnlg" else row.get("tripleset")
        return {"triples": json_safe(triples), "category": row.get("category")}
    if normalizer == "logicnlg":
        return {
            "title": row.get("title"),
            "table": json_safe(row.get("table")),
            "linked_columns": json_safe(row.get("linked_columns")),
            "template": row.get("template"),
        }
    if normalizer == "fetaqa":
        table = row.get("table_array") or row.get("table")
        return {
            "page_title": row.get("table_page_title") or row.get("page_title"),
            "table_title": row.get("table_section_title")
            or row.get("table_title")
            or row.get("title"),
            "table": json_safe(table),
            "highlighted_cell_ids": json_safe(row.get("highlighted_cell_ids")),
            "question": row.get("question"),
        }
    if normalizer == "rotowire_en_de":
        return {
            "home_line": json_safe(row.get("home_line")),
            "vis_line": json_safe(row.get("vis_line")),
            "box_score": json_safe(row.get("box_score")),
            "home_name": row.get("home_name"),
            "vis_name": row.get("vis_name"),
            "day": row.get("day"),
        }
    if normalizer == "turku_hockey":
        excluded = {*config.reference_fields, "news_article", "target", "references"}
        return {key: json_safe(value) for key, value in row.items() if key not in excluded}

    if config.source_fields:
        selected: dict[str, Any] = {}
        for field in config.source_fields:
            candidate = value_at_path(row, field)
            if candidate is not None:
                selected[field] = json_safe(candidate)
        if selected:
            return selected

    excluded_fields = {*config.reference_fields, *config.id_fields, *REFERENCE_FIELD_NAMES}
    return {key: json_safe(value) for key, value in row.items() if key not in excluded_fields}


def source_text_from_payload(payload: Any, row: dict[str, Any], config: DatasetConfig) -> str:
    if config.normalizer == "totto":
        lines: list[str] = []
        if payload.get("table_page_title"):
            lines.append(f"Page: {payload['table_page_title']}")
        if payload.get("table_section_title"):
            lines.append(f"Section: {payload['table_section_title']}")
        highlights = {
            tuple(item)
            for item in (payload.get("highlighted_cells") or [])
            if isinstance(item, list) and len(item) == 2
        }
        lines.append("Table:")
        for row_index, table_row in enumerate(payload.get("table") or []):
            cells: list[str] = []
            for column_index, cell in enumerate(table_row):
                value = str(cell.get("value", "")) if isinstance(cell, dict) else str(cell)
                marker = "*" if (row_index, column_index) in highlights else ""
                cells.append(f"{marker}{value}{marker}")
            lines.append(" | ".join(cells))
        lines.append("Cells surrounded by * are highlighted.")
        return "\n".join(lines)

    if config.normalizer == "fetaqa":
        lines: list[str] = []
        if payload.get("page_title"):
            lines.append(f"Page: {payload['page_title']}")
        if payload.get("table_title"):
            lines.append(f"Table: {payload['table_title']}")
        lines.append(pretty_json(payload.get("table")))
        if payload.get("question"):
            lines.append(f"Question: {payload['question']}")
        return "\n".join(lines)

    if config.normalizer in {"e2e", "viggo"}:
        return str(payload.get("meaning_representation", ""))
    if config.normalizer in {"webnlg", "dart"}:
        return "\n".join(
            " | ".join(map(str, item)) if isinstance(item, list) else str(item)
            for item in (payload.get("triples") or [])
        )
    if config.normalizer == "logicnlg":
        lines = []
        if payload.get("title"):
            lines.append(f"Title: {payload['title']}")
        lines.append(str(payload.get("table", "")))
        return "\n".join(lines)
    return pretty_json(payload)


def parent_table_from_row(
    row: dict[str, Any],
    payload: Any,
    config: DatasetConfig,
) -> list[list[str]] | None:
    if config.normalizer == "totto":
        return totto_parent_table(row)
    if config.normalizer == "webnlg":
        return triples_to_parent_table(row.get("input"))
    if config.normalizer == "dart":
        return triples_to_parent_table(row.get("tripleset"))
    if config.normalizer in {"e2e", "viggo"}:
        return parse_meaning_representation(str(payload.get("meaning_representation", "")))
    if config.normalizer in {"fetaqa", "logicnlg"}:
        table = payload.get("table")
        if isinstance(table, list):
            return [
                [str(cell) for cell in table_row]
                for table_row in table
                if isinstance(table_row, list)
            ] or None
    return flat_parent_table(payload)


def request_for_config(config: DatasetConfig, payload: Any) -> str:
    language_name = {
        "de": "German",
        "fi": "Finnish",
        "en": "English",
    }.get(config.language.split("-")[0].casefold(), config.language)

    match config.task_family:
        case TaskFamily.EVENT_REPORT:
            return (
                "Write a coherent game report from the supplied structured game data. "
                "Lead with the result, select the most important performances and "
                "contrasts, and do not invent information."
            )
        case TaskFamily.LONG_FORM_TABLE_REPORT:
            return (
                "Write a coherent factual report from the supplied structured data. "
                "Select the most important information, organise it clearly, and "
                "avoid unsupported claims."
            )
        case TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION:
            return (
                "Write exactly one concise sentence describing the highlighted table "
                "cells. Do not discuss unrelated cells and do not add headings."
            )
        case TaskFamily.LOGICAL_TABLE_STATEMENT:
            return (
                "Write one concise statement that is logically entailed by the supplied "
                "table. Do not introduce outside knowledge."
            )
        case TaskFamily.TABLE_QUESTION_ANSWERING:
            question = payload.get("question") if isinstance(payload, dict) else None
            return (
                "Answer the supplied question directly using only the table. Give a "
                "concise free-form answer."
                + (f"\nQuestion: {question}" if question else "")
            )
        case TaskFamily.ATTRIBUTE_VERBALISATION:
            return (
                "Express all and only the supplied attributes in one or two fluent "
                "sentences. Do not add headings or unsupported details."
            )
        case TaskFamily.TRIPLE_VERBALISATION:
            return (
                "Express all and only the supplied triples as short, coherent natural "
                "language. Do not add unsupported facts."
            )
        case TaskFamily.BIOGRAPHY:
            return (
                "Write one concise biographical opening sentence using only the "
                "supplied infobox information."
            )
        case TaskFamily.WEATHER_RESPONSE:
            return "Write a concise weather response using only the supplied weather attributes."
        case TaskFamily.CROSS_LINGUAL_EVENT_REPORT:
            return f"Write a coherent game report in {language_name}. Use only the supplied structured game data."
        case TaskFamily.ANALYTICAL_EXPLANATION:
            return (
                "Write a concise analytical explanation of the supplied "
                "model-performance table. Compare the reported metrics accurately "
                "and do not invent causal explanations."
            )

    raise ValueError(f"Unsupported task family: {config.task_family}")


def normalise_row(row: dict[str, Any], config: DatasetConfig, index: int) -> BenchmarkExample:
    payload = source_payload_from_row(row, config)
    references = references_from_row(row, config)
    example_id = example_id_from_row(row, config, index)
    source_text = source_text_from_payload(payload, row, config)
    parent_table = parent_table_from_row(row, payload, config)
    metadata = {
        field: json_safe(value_at_path(row, field))
        for field in config.metadata_fields
        if value_at_path(row, field) is not None
    }
    metadata.update(
        {
            "normalizer": config.normalizer,
            "requested_split": config.split,
            "hub_id": config.hub_id,
            "config_name": config.config_name,
        }
    )
    return BenchmarkExample(
        dataset_id=config.dataset_id,
        example_id=example_id,
        task_family=config.task_family,
        output_mode=config.output_mode,
        language=config.language,
        source_payload=payload,
        source_text=source_text,
        references=references,
        request=request_for_config(config, payload),
        parent_table=parent_table,
        metadata=metadata,
        source_sha256=sha256_text(compact_json(payload)),
        reference_sha256=sha256_text(compact_json(references)),
    )


def load_json_rows(path: Path, split: str, root_field: str | None) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if root_field:
        payload = value_at_path(payload, root_field)
    elif isinstance(payload, dict):
        if split in payload:
            payload = payload[split]
        elif "data" in payload:
            payload = payload["data"]
        elif "examples" in payload:
            payload = payload["examples"]
    if isinstance(payload, dict):
        return [
            {"_mapping_key": key, **value}
            if isinstance(value, dict)
            else {"_mapping_key": key, "value": value}
            for key, value in payload.items()
        ]
    if not isinstance(payload, list):
        raise ValueError(f"Expected a list or mapping in {path}.")
    return [dict(item) for item in payload if isinstance(item, dict)]


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not an object.")
            rows.append(value)
    return rows


def resolve_local_file(path: Path, split: str) -> Path:
    if path.is_file():
        return path
    for candidate in (
        path / f"{split}.jsonl",
        path / f"{split}.json",
        path / f"{split}.parquet",
        path / f"{split}.csv",
        path / f"{split}.tsv",
    ):
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No file for split `{split}` was found in {path}.")


def load_local_rows(config: DatasetConfig) -> list[dict[str, Any]]:
    assert config.local_path is not None
    path = resolve_local_file(config.local_path, config.split)
    suffix = path.suffix.casefold()
    if suffix == ".jsonl":
        return load_jsonl_rows(path)
    if suffix == ".json":
        return load_json_rows(path, config.split, config.options.get("root_field"))
    if suffix == ".parquet":
        return pd.read_parquet(path).to_dict(orient="records")
    if suffix in {".csv", ".tsv"}:
        separator = "\t" if suffix == ".tsv" else config.options.get("separator", ",")
        return pd.read_csv(path, sep=separator, low_memory=False).to_dict(orient="records")
    raise ValueError(f"Unsupported local dataset format: {path}")


def load_huggingface_rows(config: DatasetConfig) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install the evaluation dependencies first.") from exc

    kwargs: dict[str, Any] = {"path": config.hub_id, "split": config.split}
    if config.config_name:
        kwargs["name"] = config.config_name
    if config.revision:
        kwargs["revision"] = config.revision
    if config.trust_remote_code:
        kwargs["trust_remote_code"] = True
    try:
        dataset = load_dataset(**kwargs)
    except RuntimeError as exc:
        if "Dataset scripts are no longer supported" in str(exc):
            raise RuntimeError(
                "This benchmark dataset still uses a Hugging Face loading script. "
                "Install the evaluation extra with datasets<4.0, then restart the notebook kernel."
            ) from exc
        raise
    except TypeError:
        kwargs.pop("trust_remote_code", None)
        dataset = load_dataset(**kwargs)
    return [dict(row) for row in dataset]


def merge_examples(examples: list[BenchmarkExample]) -> list[BenchmarkExample]:
    grouped: dict[tuple[str, str], list[BenchmarkExample]] = defaultdict(list)
    for example in examples:
        grouped[(example.dataset_id, example.example_id)].append(example)

    merged: list[BenchmarkExample] = []
    for group in grouped.values():
        first = group[0]
        references = deduplicate_strings(
            reference for example in group for reference in example.references
        )
        merged.append(
            first.model_copy(
                update={
                    "references": references,
                    "reference_sha256": sha256_text(compact_json(references)),
                }
            )
        )
    return merged


def deterministic_sample(
    examples: list[BenchmarkExample],
    sample_size: int | None,
    seed: int,
) -> list[BenchmarkExample]:
    if sample_size is None or sample_size >= len(examples):
        return examples
    random_generator = random.Random(seed)
    selected_indexes = sorted(random_generator.sample(range(len(examples)), sample_size))
    return [examples[index] for index in selected_indexes]


def load_and_normalise_dataset(config: DatasetConfig) -> list[BenchmarkExample]:
    rows = load_huggingface_rows(config) if config.source == DatasetSource.HUGGINGFACE else load_local_rows(config)
    examples: list[BenchmarkExample] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        try:
            examples.append(normalise_row(json_safe(row), config, index))
        except Exception as exc:
            errors.append(f"row {index}: {type(exc).__name__}: {exc}")
    examples = deterministic_sample(merge_examples(examples), config.sample_size, config.seed)
    if not examples:
        details = "\n".join(errors[:10])
        raise RuntimeError(
            f"{config.dataset_id} produced no usable examples."
            + (f"\nFirst errors:\n{details}" if details else "")
        )
    return examples


def write_jsonl(path: Path, values: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            payload = value.model_dump(mode="json") if hasattr(value, "model_dump") else json_safe(value)
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_examples(path: Path) -> list[BenchmarkExample]:
    return [
        BenchmarkExample.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def prepare_datasets(
    configs: list[DatasetConfig],
    output_directory: Path,
    *,
    skip_unavailable: bool = False,
) -> list[DatasetPreparationStatus]:
    output_directory.mkdir(parents=True, exist_ok=True)
    statuses: list[DatasetPreparationStatus] = []
    all_examples: list[BenchmarkExample] = []

    for config in configs:
        if not config.enabled:
            continue
        try:
            examples = load_and_normalise_dataset(config)
            dataset_path = output_directory / f"{config.dataset_id}.jsonl"
            write_jsonl(dataset_path, examples)
            all_examples.extend(examples)
            statuses.append(
                DatasetPreparationStatus(
                    dataset_id=config.dataset_id,
                    status=MetricStatus.SCORED,
                    requested_split=config.split,
                    example_count=len(examples),
                    output_path=dataset_path,
                )
            )
        except Exception as exc:
            status = DatasetPreparationStatus(
                dataset_id=config.dataset_id,
                status=MetricStatus.UNAVAILABLE,
                requested_split=config.split,
                error=f"{type(exc).__name__}: {exc}",
            )
            statuses.append(status)
            if not skip_unavailable:
                write_jsonl(output_directory / "preparation_status.jsonl", statuses)
                raise

    write_jsonl(output_directory / "all_examples.jsonl", all_examples)
    write_jsonl(output_directory / "preparation_status.jsonl", statuses)
    return statuses


def default_dataset_configs() -> list[DatasetConfig]:
    configs = [
        DatasetConfig(
            dataset_id="sportsett_basketball",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/sportsett_basketball",
            split="test",
            normalizer="sportsett",
            task_family=TaskFamily.EVENT_REPORT,
            output_mode=OutputMode.MULTI_PARAGRAPH_REPORT,
            sample_size=30,
            reference_fields=["references", "target", "summaries"],
            id_fields=["sportsett_id", "gem_parent_id", "gem_id"],
            metadata_fields=["sportsett_id"],
        ),
        DatasetConfig(
            dataset_id="totto",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/totto",
            split="validation",
            normalizer="totto",
            task_family=TaskFamily.HIGHLIGHTED_TABLE_DESCRIPTION,
            output_mode=OutputMode.ONE_SENTENCE,
            sample_size=30,
            reference_fields=["references", "target"],
            metadata_fields=["overlap_subset", "table_page_title", "table_section_title"],
        ),
        DatasetConfig(
            dataset_id="e2e_nlg",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/e2e_nlg",
            split="test",
            normalizer="e2e",
            task_family=TaskFamily.ATTRIBUTE_VERBALISATION,
            output_mode=OutputMode.SHORT_TEXT,
            sample_size=30,
            reference_fields=["references", "target"],
        ),
        DatasetConfig(
            dataset_id="web_nlg",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/web_nlg",
            config_name="en",
            split="test",
            normalizer="webnlg",
            task_family=TaskFamily.TRIPLE_VERBALISATION,
            output_mode=OutputMode.SHORT_TEXT,
            sample_size=30,
            reference_fields=["references", "target"],
            metadata_fields=["category"],
        ),
        DatasetConfig(
            dataset_id="dart",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/dart",
            split="test",
            normalizer="dart",
            task_family=TaskFamily.TRIPLE_VERBALISATION,
            output_mode=OutputMode.SHORT_TEXT,
            sample_size=30,
            reference_fields=["references", "target"],
            metadata_fields=["target_sources", "subtree_was_extended"],
        ),
        DatasetConfig(
            dataset_id="logicnlg",
            source=DatasetSource.HUGGINGFACE,
            hub_id="kasnerz/logicnlg",
            split="test",
            normalizer="logicnlg",
            task_family=TaskFamily.LOGICAL_TABLE_STATEMENT,
            output_mode=OutputMode.ONE_SENTENCE,
            sample_size=30,
            reference_fields=["ref", "references", "target"],
            id_fields=["table_id", "id"],
            metadata_fields=["title", "template"],
        ),
        DatasetConfig(
            dataset_id="fetaqa",
            source=DatasetSource.HUGGINGFACE,
            hub_id="table-benchmark/fetaqa",
            split="test",
            normalizer="fetaqa",
            task_family=TaskFamily.TABLE_QUESTION_ANSWERING,
            output_mode=OutputMode.DIRECT_ANSWER,
            sample_size=30,
            reference_fields=["answer", "references", "target"],
            id_fields=["feta_id", "id"],
            metadata_fields=["table_page_title", "table_section_title"],
        ),
        DatasetConfig(
            dataset_id="viggo",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/viggo",
            split="test",
            normalizer="viggo",
            task_family=TaskFamily.ATTRIBUTE_VERBALISATION,
            output_mode=OutputMode.SHORT_TEXT,
            sample_size=30,
            reference_fields=["references", "target"],
        ),
        DatasetConfig(
            dataset_id="mlb_data_to_text",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/mlb_data_to_text",
            split="test",
            trust_remote_code=True,
            normalizer="mlb",
            task_family=TaskFamily.EVENT_REPORT,
            output_mode=OutputMode.MULTI_PARAGRAPH_REPORT,
            sample_size=20,
            reference_fields=["references", "target", "summary_eval", "summary"],
            id_fields=["gem_parent_id", "gem_id", "game_id", "id"],
        ),
        DatasetConfig(
            dataset_id="conversational_weather",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/conversational_weather",
            split="test",
            trust_remote_code=True,
            normalizer="generic",
            task_family=TaskFamily.WEATHER_RESPONSE,
            output_mode=OutputMode.SHORT_TEXT,
            sample_size=30,
            source_fields=["dialogue_act", "weather_data", "input", "linearized_input"],
            reference_fields=["references", "target", "response"],
        ),
        DatasetConfig(
            dataset_id="turku_hockey",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/turku_hockey_data2text",
            split="test",
            trust_remote_code=True,
            normalizer="turku_hockey",
            task_family=TaskFamily.EVENT_REPORT,
            output_mode=OutputMode.PARAGRAPH,
            language="fi",
            sample_size=20,
            reference_fields=["references", "target", "news_article"],
        ),
        DatasetConfig(
            dataset_id="rotowire_english_german",
            source=DatasetSource.HUGGINGFACE,
            hub_id="GEM/RotoWire_English-German",
            split="test",
            trust_remote_code=True,
            normalizer="rotowire_en_de",
            task_family=TaskFamily.CROSS_LINGUAL_EVENT_REPORT,
            output_mode=OutputMode.MULTI_PARAGRAPH_REPORT,
            language="de",
            sample_size=20,
            reference_fields=["references", "target", "summary_de"],
        ),
    ]

    local_configs = [
        ("rotowire_fg", TaskFamily.EVENT_REPORT, OutputMode.MULTI_PARAGRAPH_REPORT),
        ("rotowire_original", TaskFamily.EVENT_REPORT, OutputMode.MULTI_PARAGRAPH_REPORT),
        ("wikitablet", TaskFamily.LONG_FORM_TABLE_REPORT, OutputMode.PARAGRAPH),
        ("takg", TaskFamily.LONG_FORM_TABLE_REPORT, OutputMode.PARAGRAPH),
        ("ml_performance_explanations", TaskFamily.ANALYTICAL_EXPLANATION, OutputMode.PARAGRAPH),
    ]
    for dataset_id, task_family, output_mode in local_configs:
        configs.append(
            DatasetConfig(
                dataset_id=dataset_id,
                enabled=False,
                source=DatasetSource.LOCAL,
                local_path=Path("evaluation/local_datasets") / dataset_id,
                split="test",
                normalizer="generic",
                task_family=task_family,
                output_mode=output_mode,
                sample_size=30,
                source_fields=["table", "metadata", "input", "box_score", "line_score"],
                reference_fields=["summary", "reference", "references", "target", "explanation"],
                id_fields=["game_id", "id", "table_id"],
            )
        )
    return configs


def load_dataset_configs(path: Path) -> list[DatasetConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("datasets", payload)
    if not isinstance(payload, list):
        raise ValueError("The dataset config must contain a list.")
    return [DatasetConfig.model_validate(item) for item in payload]


def save_default_dataset_configs(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"datasets": [item.model_dump(mode="json") for item in default_dataset_configs()]},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
