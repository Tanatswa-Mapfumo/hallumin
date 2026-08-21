"""Derive generation diagnostics from workflow artifacts and metric records."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .generation import read_generations
from .reference_metrics import plain_text


NUMBER_PATTERN = re.compile(
    r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?"
)


def extract_numbers(value: str) -> list[str]:
    numbers: list[str] = []
    for token in NUMBER_PATTERN.findall(value):
        cleaned = token.replace(",", "").rstrip("%")
        if cleaned.startswith(("+", "-")):
            cleaned = cleaned[1:]
        if cleaned:
            numbers.append(cleaned)
    return numbers


def sentence_count(value: str) -> int:
    text = plain_text(value)
    return len([item for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()])


def safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def number_diagnostics(
    generated: str,
    source: str,
    references: list[str],
) -> dict[str, float | int | None]:
    generated_numbers = extract_numbers(generated)
    source_numbers = set(extract_numbers(source))
    reference_numbers = {
        number for reference in references for number in extract_numbers(reference)
    }
    source_supported = sum(number in source_numbers for number in generated_numbers)
    reference_supported = sum(number in reference_numbers for number in generated_numbers)
    return {
        "generated_number_count": len(generated_numbers),
        "source_number_count": len(source_numbers),
        "reference_number_count": len(reference_numbers),
        "generated_number_source_precision": safe_ratio(
            source_supported,
            len(generated_numbers),
        ),
        "generated_number_reference_precision": safe_ratio(
            reference_supported,
            len(generated_numbers),
        ),
    }


def generation_diagnostics(records: Iterable[Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in records:
        generated = plain_text(record.generated_text)
        support_count = record.support_sentence_count or 0
        mapped_count = record.mapped_support_sentence_count or 0
        row = {
            "generation_id": record.generation_id,
            "dataset_id": record.dataset_id,
            "example_id": record.example_id,
            "variant_id": record.variant_id,
            "repetition": record.repetition,
            "seed": record.seed,
            "language": record.language,
            "writer_mode": record.writer_mode,
            "release_status": record.release_status,
            "approved_for_release": record.approved_for_release,
            "primary_evaluation_eligible": record.primary_evaluation_eligible,
            "repair_rounds_used": record.repair_rounds_used,
            "audit_support_rate": record.audit_support_rate,
            "elapsed_seconds": record.elapsed_seconds,
            "word_count": len(generated.split()),
            "character_count": len(generated),
            "sentence_count": sentence_count(generated),
            "reference_count": len(record.references),
            "support_sentence_count": support_count,
            "mapped_support_sentence_count": mapped_count,
            "provenance_coverage": safe_ratio(mapped_count, support_count),
            "fact_id_reference_count": record.fact_id_reference_count,
            "evidence_id_reference_count": record.evidence_id_reference_count,
            "invalid_fact_id_count": record.invalid_fact_id_count,
            "invalid_evidence_id_count": record.invalid_evidence_id_count,
            "input_tokens": record.input_tokens,
            "output_tokens": record.output_tokens,
            "total_tokens": record.total_tokens,
            "estimated_cost_gbp": record.estimated_cost_gbp,
            "generation_error": record.error,
        }
        row.update(number_diagnostics(generated, record.source_text, record.references))
        rows.append(row)
    return pd.DataFrame(rows)


def write_diagnostics(generations_path: Path, output_path: Path) -> pd.DataFrame:
    records = read_generations(generations_path)
    frame = generation_diagnostics(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame
