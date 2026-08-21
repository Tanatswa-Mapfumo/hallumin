from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from .datasets import write_jsonl
from .models import GenerationRecord, HumanEvaluationPair, HumanJudgement


def pair_identifier(
    dataset_id: str,
    example_id: str,
    first_variant: str,
    second_variant: str,
) -> str:
    raw = f"{dataset_id}|{example_id}|{first_variant}|{second_variant}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def make_blinded_pairs(
    records: list[GenerationRecord],
    *,
    variants: list[str] | None = None,
    examples_per_dataset: int = 10,
    seed: int = 42,
) -> list[HumanEvaluationPair]:
    eligible = [
        record
        for record in records
        if (
            record.error is None
            and record.generated_text.strip()
            and (variants is None or record.variant_id in variants)
        )
    ]
    grouped: dict[tuple[str, str], dict[str, GenerationRecord]] = defaultdict(dict)
    for record in eligible:
        if record.repetition == 0:
            grouped[(record.dataset_id, record.example_id)][record.variant_id] = record

    by_dataset: dict[str, list[tuple[tuple[str, str], dict[str, GenerationRecord]]]] = (
        defaultdict(list)
    )
    for key, value in grouped.items():
        if len(value) >= 2:
            by_dataset[key[0]].append((key, value))

    random_generator = random.Random(seed)
    pairs: list[HumanEvaluationPair] = []
    for dataset_id, candidates in by_dataset.items():
        candidates = list(candidates)
        random_generator.shuffle(candidates)
        for (_, example_id), variant_records in candidates[:examples_per_dataset]:
            for first_variant, second_variant in combinations(sorted(variant_records), 2):
                first = variant_records[first_variant]
                second = variant_records[second_variant]
                pair_id = pair_identifier(dataset_id, example_id, first_variant, second_variant)
                pair_seed = int(
                    hashlib.sha256(f"{pair_id}|{seed}".encode("utf-8")).hexdigest()[:8],
                    16,
                )
                swap = random.Random(pair_seed).choice([False, True])
                if swap:
                    output_a, output_b = second.generated_text, first.generated_text
                    hidden_a, hidden_b = second_variant, first_variant
                else:
                    output_a, output_b = first.generated_text, second.generated_text
                    hidden_a, hidden_b = first_variant, second_variant
                pairs.append(
                    HumanEvaluationPair(
                        pair_id=pair_id,
                        dataset_id=dataset_id,
                        example_id=example_id,
                        source_text=first.source_text,
                        references=first.references,
                        output_a=output_a,
                        output_b=output_b,
                        hidden_variant_a=hidden_a,
                        hidden_variant_b=hidden_b,
                        order_seed=pair_seed,
                    )
                )
    random_generator.shuffle(pairs)
    return pairs


def export_human_packet(
    pairs: list[HumanEvaluationPair],
    packet_path: Path,
    response_template_path: Path,
) -> None:
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(packet_path, pairs)
    columns = [
        "pair_id",
        "evaluator_id",
        "factual_correctness_a",
        "factual_correctness_b",
        "coverage_a",
        "coverage_b",
        "coherence_a",
        "coherence_b",
        "usefulness_a",
        "usefulness_b",
        "preference",
        "comments",
    ]
    response_template_path.parent.mkdir(parents=True, exist_ok=True)
    with response_template_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for pair in pairs:
            writer.writerow({"pair_id": pair.pair_id, **{column: "" for column in columns[1:]}})


def export_reviewer_packet(pairs: list[HumanEvaluationPair], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for pair in pairs:
            payload = {
                "pair_id": pair.pair_id,
                "dataset_id": pair.dataset_id,
                "example_id": pair.example_id,
                "source_text": pair.source_text,
                "references": pair.references,
                "output_a": pair.output_a,
                "output_b": pair.output_b,
                "rubric": {
                    "factual_correctness": "1 = materially incorrect; 5 = fully supported.",
                    "coverage": "1 = omits most important content; 5 = strong content coverage.",
                    "coherence": "1 = difficult to read; 5 = clear and well organised.",
                    "usefulness": (
                        "1 = not useful for the task; 5 = highly useful and appropriately scoped."
                    ),
                    "preference": "A, B, or tie",
                },
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_human_judgements(path: Path) -> list[HumanJudgement]:
    frame = pd.read_csv(path)
    return [
        HumanJudgement.model_validate(
            {key: "" if pd.isna(value) else value for key, value in row.items()}
        )
        for row in frame.to_dict(orient="records")
    ]


def decode_human_scores(
    pairs: list[HumanEvaluationPair],
    judgements: list[HumanJudgement],
) -> pd.DataFrame:
    pair_lookup = {pair.pair_id: pair for pair in pairs}
    rows: list[dict[str, Any]] = []
    for judgement in judgements:
        pair = pair_lookup.get(judgement.pair_id)
        if pair is None:
            raise ValueError(f"Unknown pair ID: {judgement.pair_id}")
        for label, variant, suffix in (
            ("A", pair.hidden_variant_a, "a"),
            ("B", pair.hidden_variant_b, "b"),
        ):
            rows.append(
                {
                    "pair_id": pair.pair_id,
                    "dataset_id": pair.dataset_id,
                    "example_id": pair.example_id,
                    "evaluator_id": judgement.evaluator_id,
                    "position": label,
                    "variant_id": variant,
                    "factual_correctness": getattr(
                        judgement,
                        f"factual_correctness_{suffix}",
                    ),
                    "coverage": getattr(judgement, f"coverage_{suffix}"),
                    "coherence": getattr(judgement, f"coherence_{suffix}"),
                    "usefulness": getattr(judgement, f"usefulness_{suffix}"),
                    "preferred": judgement.preference == label,
                    "tie": judgement.preference == "tie",
                }
            )
    return pd.DataFrame(rows)


def inter_rater_statistics(judgements: list[HumanJudgement]) -> pd.DataFrame:
    by_pair: dict[str, list[HumanJudgement]] = defaultdict(list)
    for judgement in judgements:
        by_pair[judgement.pair_id].append(judgement)

    metrics = [
        "factual_correctness_a",
        "factual_correctness_b",
        "coverage_a",
        "coverage_b",
        "coherence_a",
        "coherence_b",
        "usefulness_a",
        "usefulness_b",
    ]
    rows: list[dict[str, Any]] = []
    for metric in metrics:
        first_values = []
        second_values = []
        for pair_judgements in by_pair.values():
            if len(pair_judgements) < 2:
                continue
            ordered = sorted(pair_judgements, key=lambda item: item.evaluator_id)
            first_values.append(getattr(ordered[0], metric))
            second_values.append(getattr(ordered[1], metric))
        rows.append(
            {
                "measure": metric,
                "paired_rating_count": len(first_values),
                "quadratic_weighted_kappa": (
                    cohen_kappa_score(first_values, second_values, weights="quadratic")
                    if len(first_values) >= 2
                    else None
                ),
            }
        )

    first_preferences = []
    second_preferences = []
    for pair_judgements in by_pair.values():
        if len(pair_judgements) < 2:
            continue
        ordered = sorted(pair_judgements, key=lambda item: item.evaluator_id)
        first_preferences.append(ordered[0].preference)
        second_preferences.append(ordered[1].preference)
    rows.append(
        {
            "measure": "pairwise_preference",
            "paired_rating_count": len(first_preferences),
            "quadratic_weighted_kappa": (
                cohen_kappa_score(first_preferences, second_preferences)
                if len(first_preferences) >= 2
                else None
            ),
        }
    )
    return pd.DataFrame(rows)
