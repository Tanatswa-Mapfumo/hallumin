"""Build the complete three-condition task-aware evaluation dossier.

The generated Markdown is intentionally self-contained: it includes every
selected input, held-out reference, generated output, metric score and
structured error annotation from the completed 25-example experiment.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from table2text.evaluation.models import GenerationRecord


PROJECT_DIR = Path(__file__).resolve().parents[2]
EVALUATION_DIR = PROJECT_DIR / "evaluation"
EXPERIMENT_DIR = EVALUATION_DIR / "task_aware_direct_baseline"
RESULT_DIR = EXPERIMENT_DIR / "results"

GENERATIONS_PATH = (
    EXPERIMENT_DIR
    / "generations"
    / "task_aware_direct_flash_25_three_condition_generations.jsonl"
)
PREPARED_EXAMPLES_PATH = (
    EXPERIMENT_DIR
    / "prepared"
    / "task_aware_direct_flash_25_examples.jsonl"
)
REFERENCE_METRICS_PATH = RESULT_DIR / "task_aware_direct_flash_25_reference_metrics.jsonl"
SOURCE_METRICS_PATH = RESULT_DIR / "task_aware_direct_flash_25_source_grounded_metrics.jsonl"
ANNOTATIONS_PATH = RESULT_DIR / "gpt56_all_75_annotations_with_provenance.jsonl"
REFERENCE_MACRO_PATH = RESULT_DIR / "task_aware_direct_flash_25_reference_macro.csv"
SOURCE_MACRO_PATH = RESULT_DIR / "task_aware_direct_flash_25_source_macro.csv"
REFERENCE_BY_DATASET_PATH = RESULT_DIR / "task_aware_direct_flash_25_reference_by_dataset.csv"
SOURCE_BY_DATASET_PATH = RESULT_DIR / "task_aware_direct_flash_25_source_by_dataset.csv"
WINS_PATH = RESULT_DIR / "task_aware_direct_flash_25_direction_adjusted_wins.csv"
SELECTED_FIVE_PATH = RESULT_DIR / "selected_five_three_condition_source_metrics.csv"
EXPERIMENT_MANIFEST_PATH = RESULT_DIR / "task_aware_direct_flash_25_manifest.json"
ANNOTATION_PROVENANCE_PATH = RESULT_DIR / "interactive_gpt56_annotation_provenance.json"
PROGRESS_LOG_PATH = RESULT_DIR / "task_aware_direct_flash_25_progress.log"
VARIANT_CONFIG_PATH = (
    EXPERIMENT_DIR / "config" / "variants_task_aware_direct_flash_25.json"
)
REFERENCE_CONFIG_PATH = (
    EXPERIMENT_DIR / "config" / "metrics_task_aware_direct_flash_25_reference.json"
)
SOURCE_CONFIG_PATH = (
    EXPERIMENT_DIR / "config" / "metrics_task_aware_direct_flash_25_source_grounded.json"
)
NOTEBOOK_PATH = EVALUATION_DIR / "notebooks" / "task_aware_direct_baseline_evaluation.ipynb"
NOTEBOOK_SOURCE_PATH = EVALUATION_DIR / "notebooks" / "task_aware_direct_baseline_evaluation.py"
ANNOTATION_BUILDER_PATH = (
    EVALUATION_DIR / "notebooks" / "build_interactive_gpt56_annotation_artifacts.py"
)
DOSSIER_BUILDER_PATH = Path(__file__).resolve()

OUTPUT_PATH = EXPERIMENT_DIR / "COMPLETE_THREE_CONDITION_EVALUATION_DOSSIER.md"
OUTPUT_MANIFEST_PATH = RESULT_DIR / "complete_evaluation_dossier_manifest.json"

VARIANT_ORDER = ["full_system", "raw_generic_flash", "task_aware_direct_flash"]
VARIANT_LABELS = {
    "full_system": "Full multi-agent system",
    "raw_generic_flash": "Raw-generic direct Flash",
    "task_aware_direct_flash": "Task-aware direct Flash",
}
DATASET_ORDER = ["dart", "e2e_nlg", "sportsett_basketball", "totto", "web_nlg"]

ITEM_REFERENCE_METRICS = [
    "bleu",
    "chrf",
    "ter",
    "rougeL",
    "meteor",
    "bertscore_f1",
]
SOURCE_METRICS = [
    "alignscore_base",
    "hhem_2_1_open_mean_support",
    "hhem_2_1_open_min_sentence_support",
    "hhem_2_1_open_unsupported_sentence_rate",
]
ALL_ITEM_METRICS = ITEM_REFERENCE_METRICS + SOURCE_METRICS

METRIC_LABELS = {
    "bleu": "BLEU",
    "chrf": "chrF",
    "ter": "TER",
    "rougeL": "ROUGE-L",
    "meteor": "METEOR",
    "bertscore_f1": "BERTScore F1",
    "corpus_bleu": "Corpus BLEU",
    "corpus_chrf": "Corpus chrF",
    "corpus_ter": "Corpus TER",
    "alignscore_base": "AlignScore",
    "hhem_2_1_open_mean_support": "HHEM mean support",
    "hhem_2_1_open_min_sentence_support": "HHEM minimum sentence support",
    "hhem_2_1_open_unsupported_sentence_rate": "HHEM unsupported-sentence rate",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_DIR))


def safe_cell(value: Any) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def md_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(safe_cell(item) for item in row) + " |")
    return lines


def score(value: Any) -> str:
    if value is None or value == "":
        return "—"
    number = float(value)
    return f"{number:.9f}".rstrip("0").rstrip(".")


def seconds(value: Any) -> str:
    if value is None or value == "":
        return "—"
    return f"{float(value):.3f}"


def fenced(text: str, language: str = "text") -> list[str]:
    fence_length = max(3, max((len(match) for match in re.findall(r"`+", text)), default=0) + 1)
    fence = "`" * fence_length
    return [f"{fence}{language}", text.rstrip(), fence]


def formatted_source(source: str) -> tuple[str, str]:
    stripped = source.strip()
    if stripped.startswith(("{", "[")):
        try:
            payload = json.loads(stripped)
            return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False), "json"
        except json.JSONDecodeError:
            pass
    return source, "text"


def csv_table(path: Path, *, score_columns: bool = True) -> list[str]:
    rows = read_csv(path)
    if not rows:
        return ["*No rows.*"]
    headers = list(rows[0])
    values: list[list[str]] = []
    for row in rows:
        rendered: list[str] = []
        for header in headers:
            value = row[header]
            if score_columns and header not in {
                "dataset_id",
                "metric_name",
                "comparison",
                "paired_metric_cases",
                "left_wins",
                "ties",
                "right_wins",
            }:
                try:
                    value = score(value)
                except ValueError:
                    pass
            rendered.append(value)
        values.append(rendered)
    return md_table(headers, values)


def generation_key(row: GenerationRecord) -> tuple[str, str, str]:
    return row.dataset_id, row.example_id, row.variant_id


def case_key(row: GenerationRecord) -> tuple[str, str]:
    return row.dataset_id, row.example_id


def direct_model(row: GenerationRecord) -> str:
    metadata = row.metadata or {}
    return str(metadata.get("model") or "—")


def token_value(row: GenerationRecord, field: str) -> Any:
    metadata = row.metadata or {}
    return metadata.get(field)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+(?:[-’']\w+)*\b", text))


def load_full_models(full_rows: list[GenerationRecord]) -> tuple[Counter[str], list[str]]:
    signatures: Counter[str] = Counter()
    missing: list[str] = []
    for row in full_rows:
        if not row.pipeline_result_path:
            missing.append(row.generation_id)
            continue
        manifest = Path(row.pipeline_result_path).parent / "00_manifest.json"
        if not manifest.exists():
            missing.append(row.generation_id)
            continue
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        signature = json.dumps(payload.get("models", {}), sort_keys=True)
        signatures[signature] += 1
    return signatures, missing


def validate_population(
    generations: list[GenerationRecord],
    prepared_examples: list[dict[str, Any]],
    reference_metrics: list[dict[str, Any]],
    source_metrics: list[dict[str, Any]],
    annotations: list[dict[str, Any]],
) -> None:
    expected_variant_counts = Counter({variant: 25 for variant in VARIANT_ORDER})
    variant_counts = Counter(row.variant_id for row in generations)
    if variant_counts != expected_variant_counts:
        raise RuntimeError(f"Unexpected generation condition counts: {variant_counts}")
    if len({row.generation_id for row in generations}) != 75:
        raise RuntimeError("Generation IDs are not 75 unique values.")
    dataset_counts = Counter(row.dataset_id for row in generations)
    if dataset_counts != Counter({dataset: 15 for dataset in DATASET_ORDER}):
        raise RuntimeError(f"Unexpected dataset counts: {dataset_counts}")

    grouped: dict[tuple[str, str], list[GenerationRecord]] = defaultdict(list)
    for row in generations:
        grouped[case_key(row)].append(row)
    if len(grouped) != 25 or any(len(rows) != 3 for rows in grouped.values()):
        raise RuntimeError("Expected 25 cases with exactly three conditions each.")
    for identity, rows in grouped.items():
        anchor = rows[0]
        for row in rows[1:]:
            fields = [
                "source_text",
                "references",
                "task_family",
                "output_mode",
                "language",
            ]
            mismatched = [field for field in fields if getattr(row, field) != getattr(anchor, field)]
            if mismatched:
                raise RuntimeError(f"Condition inputs differ for {identity}: {mismatched}")

        by_variant = {row.variant_id: row for row in rows}
        if by_variant["full_system"].request != by_variant["task_aware_direct_flash"].request:
            raise RuntimeError(f"Full and task-aware requests differ for {identity}")

    prepared_by_id = {
        (row["dataset_id"], row["example_id"]): row for row in prepared_examples
    }
    if set(prepared_by_id) != set(grouped):
        raise RuntimeError("Prepared-example and generation case identities differ.")
    for identity, rows in grouped.items():
        prepared = prepared_by_id[identity]
        for row in rows:
            if row.source_text != prepared["source_text"]:
                raise RuntimeError(f"Prepared and generated source text differ for {identity}")
            if row.references != prepared["references"]:
                raise RuntimeError(f"Prepared and generated references differ for {identity}")
        by_variant = {row.variant_id: row for row in rows}
        if by_variant["full_system"].request != prepared["request"]:
            raise RuntimeError(f"Prepared and Full-System requests differ for {identity}")

    item_reference = [
        row for row in reference_metrics if row["metric_name"] in ITEM_REFERENCE_METRICS
    ]
    if len(item_reference) != 75 * len(ITEM_REFERENCE_METRICS):
        raise RuntimeError(f"Expected 450 item-level reference metrics; found {len(item_reference)}")
    if len(source_metrics) != 75 * len(SOURCE_METRICS):
        raise RuntimeError(f"Expected 300 source-grounded metrics; found {len(source_metrics)}")
    if len(annotations) != 75:
        raise RuntimeError(f"Expected 75 annotation rows; found {len(annotations)}")
    if {row["generation_id"] for row in annotations} != {
        row.generation_id for row in generations
    }:
        raise RuntimeError("Annotation and generation identity sets differ.")


def metric_lookup(
    reference_metrics: list[dict[str, Any]],
    source_metrics: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in reference_metrics + source_metrics:
        key = (row["generation_id"], row["metric_name"])
        if key in lookup:
            # Corpus rows are dataset aggregates attached to one generation ID;
            # their names do not collide with item-level names.
            raise RuntimeError(f"Duplicate metric key: {key}")
        lookup[key] = row
    return lookup


def generation_summary(generations: list[GenerationRecord]) -> list[str]:
    lines: list[str] = []
    for variant in VARIANT_ORDER:
        rows = [row for row in generations if row.variant_id == variant]
        lines.extend(
            md_table(
                [
                    "Condition",
                    "Outputs",
                    "Generation errors",
                    "Total elapsed seconds",
                    "Median output words",
                    "Writer modes",
                    "Release statuses",
                ],
                [
                    [
                        VARIANT_LABELS[variant],
                        len(rows),
                        sum(row.error is not None for row in rows),
                        seconds(sum(float(row.elapsed_seconds or 0) for row in rows)),
                        sorted(word_count(row.generated_text) for row in rows)[len(rows) // 2],
                        (
                            "Not applicable"
                            if all(row.writer_mode is None for row in rows)
                            else ", ".join(
                                f"{key}: {value}"
                                for key, value in sorted(
                                    Counter(str(row.writer_mode) for row in rows).items()
                                )
                            )
                        ),
                        (
                            "Not applicable"
                            if all(row.release_status is None for row in rows)
                            else ", ".join(
                                f"{key}: {value}"
                                for key, value in sorted(
                                    Counter(str(row.release_status) for row in rows).items()
                                )
                            )
                        ),
                    ]
                ],
            )[2:]
        )
    return [
        "| Condition | Outputs | Generation errors | Total elapsed seconds | Median output words | Writer modes | Release statuses |",
        "|---|---:|---:|---:|---:|---|---|",
        *lines,
    ]


def annotation_aggregate(annotations: list[dict[str, Any]]) -> list[str]:
    rows = []
    for variant in VARIANT_ORDER:
        selected = [row for row in annotations if row["variant_id"] == variant]
        categories = Counter(
            item["category"] for row in selected for item in row.get("errors", [])
        )
        execution = Counter(row["execution_mode"] for row in selected)
        rows.append(
            [
                VARIANT_LABELS[variant],
                len(selected),
                sum(row["error_count"] > 0 for row in selected),
                sum(row["error_count"] for row in selected),
                ", ".join(f"{key}: {value}" for key, value in sorted(categories.items()))
                or "None",
                ", ".join(f"{key}: {value}" for key, value in sorted(execution.items())),
            ]
        )
    return md_table(
        ["Condition", "Outputs", "Flagged outputs", "Errors", "Categories", "Execution provenance"],
        rows,
    )


def per_example_metric_table(
    case_rows: list[GenerationRecord],
    metrics: dict[tuple[str, str], dict[str, Any]],
) -> list[str]:
    headers = ["Condition"] + [METRIC_LABELS[name] for name in ALL_ITEM_METRICS]
    rows: list[list[str]] = []
    by_variant = {row.variant_id: row for row in case_rows}
    for variant in VARIANT_ORDER:
        generation = by_variant[variant]
        values = [VARIANT_LABELS[variant]]
        for metric_name in ALL_ITEM_METRICS:
            metric = metrics.get((generation.generation_id, metric_name))
            values.append(score(metric["score"]) if metric else "—")
        rows.append(values)
    return md_table(headers, rows)


def output_metadata_table(row: GenerationRecord, full_model_label: str) -> list[str]:
    metadata = row.metadata or {}
    model = full_model_label if row.variant_id == "full_system" else direct_model(row)
    return md_table(
        ["Field", "Value"],
        [
            ["Generation ID", f"`{row.generation_id}`"],
            ["Model", model],
            ["Seed", row.seed],
            ["Backend", row.backend],
            ["Prompt style", metadata.get("prompt_style")],
            ["Elapsed seconds", seconds(row.elapsed_seconds)],
            ["Prompt tokens", token_value(row, "prompt_tokens")],
            ["Completion tokens", token_value(row, "completion_tokens")],
            ["Total tokens", token_value(row, "total_tokens")],
            ["Output words", word_count(row.generated_text)],
            ["Writer mode", row.writer_mode],
            ["Release status", row.release_status],
            ["Primary evaluation eligible", row.primary_evaluation_eligible],
            ["Primary evaluation reason", row.primary_evaluation_reason],
            ["Repair rounds", row.repair_rounds_used],
            ["Audit support rate", score(row.audit_support_rate) if row.audit_support_rate is not None else None],
            ["Mapped support sentences", row.mapped_support_sentence_count],
            ["Support sentences", row.support_sentence_count],
            ["Generation error", row.error],
        ],
    )


def annotation_section(annotation: dict[str, Any]) -> list[str]:
    lines = [
        f"- Judge model: `{annotation['judge_model']}`",
        f"- Execution mode: `{annotation['execution_mode']}`",
        f"- API authenticated: `{str(annotation['api_authenticated']).lower()}`",
        f"- Status: `{annotation['status']}`",
        f"- Error count: **{annotation['error_count']}**",
    ]
    if not annotation["errors"]:
        lines.append("- Errors: none recorded.")
        return lines
    lines.append("- Errors:")
    for index, item in enumerate(annotation["errors"], start=1):
        lines.extend(
            [
                f"  {index}. **{item['category']}** — “{item['error_span']}”",
                f"     - {item['correction_or_explanation']}",
            ]
        )
    return lines


def build_document() -> tuple[str, dict[str, Any]]:
    generations = [
        GenerationRecord.model_validate(row) for row in read_jsonl(GENERATIONS_PATH)
    ]
    prepared_examples = read_jsonl(PREPARED_EXAMPLES_PATH)
    reference_metrics = read_jsonl(REFERENCE_METRICS_PATH)
    source_metrics = read_jsonl(SOURCE_METRICS_PATH)
    annotations = read_jsonl(ANNOTATIONS_PATH)
    validate_population(
        generations,
        prepared_examples,
        reference_metrics,
        source_metrics,
        annotations,
    )

    metrics = metric_lookup(reference_metrics, source_metrics)
    annotation_by_id = {row["generation_id"]: row for row in annotations}
    grouped: dict[tuple[str, str], list[GenerationRecord]] = defaultdict(list)
    for row in generations:
        grouped[case_key(row)].append(row)
    prepared_by_id = {
        (row["dataset_id"], row["example_id"]): row for row in prepared_examples
    }

    full_rows = [row for row in generations if row.variant_id == "full_system"]
    full_model_signatures, missing_manifests = load_full_models(full_rows)
    if missing_manifests:
        raise RuntimeError(f"Missing Full-System manifests: {missing_manifests}")
    if len(full_model_signatures) != 1:
        raise RuntimeError(f"Full-System model settings were not constant: {full_model_signatures}")
    full_models = json.loads(next(iter(full_model_signatures)))
    full_model_label = ", ".join(
        f"{role}={model}" for role, model in full_models.items()
    )

    artifact_paths = [
        GENERATIONS_PATH,
        PREPARED_EXAMPLES_PATH,
        REFERENCE_METRICS_PATH,
        SOURCE_METRICS_PATH,
        ANNOTATIONS_PATH,
        REFERENCE_MACRO_PATH,
        SOURCE_MACRO_PATH,
        REFERENCE_BY_DATASET_PATH,
        SOURCE_BY_DATASET_PATH,
        WINS_PATH,
        SELECTED_FIVE_PATH,
        EXPERIMENT_MANIFEST_PATH,
        ANNOTATION_PROVENANCE_PATH,
        PROGRESS_LOG_PATH,
        VARIANT_CONFIG_PATH,
        REFERENCE_CONFIG_PATH,
        SOURCE_CONFIG_PATH,
        NOTEBOOK_PATH,
        NOTEBOOK_SOURCE_PATH,
        ANNOTATION_BUILDER_PATH,
        DOSSIER_BUILDER_PATH,
    ]
    artifact_hashes = {rel(path): sha256(path) for path in artifact_paths}

    lines: list[str] = [
        "# Complete Three-Condition Table-to-Text Evaluation Dossier",
        "",
        f"Generated from persisted artifacts on {datetime.now(timezone.utc).isoformat()}.",
        "",
        "This document is a self-contained results bank for the 25-example, five-dataset experiment comparing the complete multi-agent workflow, a one-call raw-generic baseline and a one-call task-aware baseline. It includes every selected source input, every condition-specific request, held-out human reference, exact generated output, automatic metric score and structured error annotation.",
        "",
        "## 1. Experimental population",
        "",
    ]
    lines.extend(
        md_table(
            ["Property", "Value"],
            [
                ["Datasets", "DART, E2E NLG, SportSett Basketball, ToTTo, WebNLG"],
                ["Examples", "25 total; five per dataset"],
                ["Conditions", "3"],
                ["Generated outputs", "75"],
                ["Seed", "42"],
                ["Reference isolation", "Human references were held out from every generator"],
                ["Request control", "Full and Task-aware Direct used the task-specific request; Raw Generic used one generic request"],
                ["Reference metric records", len(reference_metrics)],
                ["Source-grounded metric records", len(source_metrics)],
                ["Structured judge records", len(annotations)],
            ],
        )
    )

    dataset_case_counts = Counter(dataset for dataset, _ in grouped)
    task_counts = Counter(
        str(rows[0].task_family.value) for rows in grouped.values()
    )
    output_counts = Counter(
        str(rows[0].output_mode.value) for rows in grouped.values()
    )
    lines.extend(
        [
            "",
            "### 1.1 Dataset and task distribution",
            "",
            *md_table(
                ["Dataset", "Cases"],
                [[dataset, dataset_case_counts[dataset]] for dataset in DATASET_ORDER],
            ),
            "",
            *md_table(
                ["Task family", "Cases"],
                [[key, value] for key, value in sorted(task_counts.items())],
            ),
            "",
            *md_table(
                ["Output mode", "Cases"],
                [[key, value] for key, value in sorted(output_counts.items())],
            ),
            "",
            "### 1.2 Conditions",
            "",
            *md_table(
                ["Variant ID", "Description", "Model configuration", "Generation path"],
                [
                    [
                        "`full_system`",
                        "Six-role multi-agent workflow with deterministic evidence infrastructure, verification, Writer and Auditor.",
                        full_model_label,
                        "Source + request + prepared task contract pass through the complete workflow.",
                    ],
                    [
                        "`raw_generic_flash`",
                        "One direct DeepSeek call receiving a generic strongest-findings request and the source, without task-family/output-form metadata.",
                        "deepseek-v4-flash; temperature 0.2; maximum output 3,000 tokens",
                        "Generic direct prompt",
                    ],
                    [
                        "`task_aware_direct_flash`",
                        "One direct DeepSeek call receiving the same source and request plus task family, output form and language.",
                        "deepseek-v4-flash; temperature 0.2; maximum output 3,000 tokens",
                        "Structured direct prompt",
                    ],
                ],
            ),
            "",
            "## 2. Generator inputs and prompt contracts",
            "",
            "### 2.1 Shared direct-baseline system prompt",
            "",
            *fenced(
                "You are a raw single-LLM data-to-text baseline. Generate the requested output directly from the supplied source data. Use only the source data and the user request. Do not use outside knowledge. Do not invent numbers, entities, chronology, causal explanations, or background. Do not mention hidden references, evaluation, prompts, or uncertainty unless the source itself makes the requested output impossible."
            ),
            "",
            "### 2.2 Raw-generic user-prompt template",
            "",
            *fenced(
                "Request:\nUnderstand the supplied data and report its strongest supported findings.\n\nSource data:\n{source}\n\nWrite the final answer only."
            ),
            "",
            "### 2.3 Task-aware direct user-prompt template",
            "",
            *fenced(
                "Task type: {task_family}\nExpected form: {output_mode}\nLanguage: {language}\n\nRequest:\n{example.request}\n\nSource data:\n{source}\n\nWrite the final answer only."
            ),
            "",
            "### 2.4 Full-System operational input",
            "",
            "The Full System received the same source data and task-specific request as Task-aware Direct together with the prepared benchmark task metadata. It did not receive the human references. Unlike the direct conditions, this is a workflow input rather than one monolithic LLM prompt: source interpretation, planning, evidence, verification, writing and auditing are separate stages.",
            "",
            "The Raw-vs-Task-aware comparison changes the complete communication contract: the request itself becomes task-specific and the prompt adds task family, expected form and language. It should therefore be interpreted as a task-contract ablation, not as an isolated test of metadata labels alone.",
            "",
            "## 3. Evaluation measures",
            "",
            *md_table(
                ["Metric", "Family", "Orientation", "What is compared"],
                [
                    ["BLEU / Corpus BLEU", "Lexical overlap", "Higher is better", "Output against held-out reference text"],
                    ["chrF / Corpus chrF", "Character overlap", "Higher is better", "Output against held-out reference text"],
                    ["TER / Corpus TER", "Edit distance", "Lower is better", "Output against held-out reference text"],
                    ["ROUGE-L", "Sequence overlap", "Higher is better", "Output against held-out reference text"],
                    ["METEOR", "Lexical-semantic alignment", "Higher is better", "Output against held-out reference text"],
                    ["BERTScore F1", "Embedding similarity", "Higher is better", "Output against held-out reference text"],
                    ["AlignScore", "Source-grounded alignment", "Higher is better", "Output against full structured source"],
                    ["HHEM mean support", "Source-grounded support", "Higher is better", "Sentence support against full source"],
                    ["HHEM minimum support", "Weakest-sentence support", "Higher is better", "Minimum sentence support against full source"],
                    ["HHEM unsupported-sentence rate", "Unsupported-content diagnostic", "Lower is better", "Proportion below the HHEM support threshold"],
                    ["GPT-5.6 Sol taxonomy", "Structured error annotation", "Fewer errors is better", "Source + task + one output; no human reference as correctness criterion"],
                ],
            ),
            "",
            "Corpus BLEU, corpus chrF and corpus TER are computed once per dataset-condition group of five examples. They therefore appear in aggregate tables, not as independent per-example scores.",
            "",
            "## 4. Generation outcomes",
            "",
            *generation_summary(generations),
            "",
            "All 75 generation records contain non-empty outputs and no generation-level error. Full-System release and Writer-mode fields do not apply to the two direct baselines.",
            "",
            "## 5. Aggregate reference-alignment metrics",
            "",
            *csv_table(REFERENCE_MACRO_PATH),
            "",
            "## 6. Aggregate source-grounded metrics",
            "",
            *csv_table(SOURCE_MACRO_PATH),
            "",
            "## 7. Direction-adjusted same-item metric wins",
            "",
            "For TER and HHEM unsupported-sentence rate, lower values are treated as wins; all other included metrics use higher values.",
            "",
            *csv_table(WINS_PATH, score_columns=False),
            "",
            "## 8. Structured error annotations",
            "",
            *annotation_aggregate(annotations),
            "",
            "The judge label is `gpt-5.6-sol`. The Full and raw-generic conditions contain 49 API-authenticated records plus one interactive completion for the previously skipped Full-System SportSett 4975 output. All 25 task-aware records were produced interactively without an API call. The combined artifact retains `execution_mode` and `api_authenticated` fields so this split cannot be mistaken for a uniform API run.",
            "",
            "### 8.1 Category totals",
            "",
        ]
    )
    category_counts = Counter(
        item["category"] for row in annotations for item in row.get("errors", [])
    )
    lines.extend(
        md_table(
            ["Category", "Count"],
            [[category, count] for category, count in sorted(category_counts.items())],
        )
    )

    lines.extend(
        [
            "",
            "## 9. Reference metrics by dataset",
            "",
            *csv_table(REFERENCE_BY_DATASET_PATH),
            "",
            "## 10. Source-grounded metrics by dataset",
            "",
            *csv_table(SOURCE_BY_DATASET_PATH),
            "",
            "## 11. Selected five-case source-grounded extraction",
            "",
            "This is the notebook's dedicated exact-case extract for the five preselected diagnostic cases.",
            "",
            *csv_table(SELECTED_FIVE_PATH),
            "",
            "## 12. Aggregate observations",
            "",
            "1. The Full System has the strongest overall reference-alignment macro scores: BLEU 0.3595, chrF 0.5972, METEOR 0.5550, ROUGE-L 0.5599 and BERTScore F1 0.9246. Its macro TER is also lowest at 0.7161.",
            "2. Supplying the complete task contract to the direct model substantially improves over the raw-generic direct baseline: Task-aware Direct wins 172 of 265 paired metric cases, loses 46 and ties 47. This contrast combines a task-specific request with task-family, output-form and language metadata.",
            "3. The Full System still leads the task-aware direct condition in the paired analysis, with 110 wins, 78 losses and 77 ties, but the gap is much smaller than Full versus raw generic.",
            "4. SportSett is the principal exception in reference alignment: task-aware direct has the highest SportSett BERTScore, BLEU, METEOR and ROUGE-L. This indicates that explicit event-report metadata gives a strong one-call model a major advantage on long-form game reports.",
            "5. ToTTo shows the largest architecture benefit. Full System materially exceeds both direct conditions because highlighted-cell selection is a content-selection problem, not merely a fluency problem.",
            "6. Source-grounded metrics disagree with each other. Full System has the highest macro AlignScore (0.6784), while task-aware direct has the best HHEM mean support (0.5857), minimum support (0.5733) and unsupported-sentence rate (0.2333). These models should be interpreted as separate diagnostics rather than combined into one factuality score.",
            "7. All three conditions receive extremely low HHEM/AlignScore values on SportSett despite mostly plausible reports and source-checked judge findings. The long nested JSON source is a difficult input representation for these local factuality models, so SportSett source scores should not be treated as direct hallucination rates.",
            "8. Structured error annotations flag 10 Full-System errors, 19 raw-generic errors and 13 task-aware-direct errors. Full System therefore retains the lowest annotation count, while task metadata removes a substantial share of the raw baseline's task/format failures.",
            "9. CONTEXT and TASK/FORMAT dominate the annotation taxonomy. Straightforward short-form datasets are largely accurate; remaining weaknesses concentrate in chronology, causal narration, ranking language and scope compliance.",
            "",
            "## 13. Complete per-example records",
            "",
            "Each record below contains the complete source, condition-specific requests, all three exact outputs, all item-level metrics and all corresponding structured annotations. References are displayed for evaluation transparency but were not supplied to any generator or used by the structured judge as its correctness criterion.",
            "",
        ]
    )

    dataset_rank = {dataset: index for index, dataset in enumerate(DATASET_ORDER)}
    ordered_cases = sorted(grouped, key=lambda key: (dataset_rank[key[0]], key[1]))
    for case_index, identity in enumerate(ordered_cases, start=1):
        dataset_id, example_id = identity
        case_rows = grouped[identity]
        by_variant = {row.variant_id: row for row in case_rows}
        anchor = by_variant["full_system"]
        prepared = prepared_by_id[identity]
        lines.extend(
            [
                f"# Case {case_index}: `{dataset_id}` / `{example_id}`",
                "",
                "## Case metadata",
                "",
                *md_table(
                    ["Field", "Value"],
                    [
                        ["Dataset ID", dataset_id],
                        ["Example ID", example_id],
                        ["Task family", prepared["task_family"]],
                        ["Output mode", prepared["output_mode"]],
                        ["Language", prepared["language"]],
                        ["Source characters", len(prepared["source_text"])],
                        ["Reference count", len(prepared["references"])],
                        ["Source SHA-256", prepared["source_sha256"]],
                        ["Reference SHA-256", prepared["reference_sha256"]],
                    ],
                ),
                "",
                "## Requests supplied by condition",
                "",
                "### Full System and Task-aware Direct",
                "",
                *fenced(by_variant["full_system"].request),
                "",
                "### Raw Generic",
                "",
                *fenced(by_variant["raw_generic_flash"].request),
                "",
                "## Source text supplied to every condition",
                "",
                "JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.",
                "",
            ]
        )
        source_text, source_language = formatted_source(prepared["source_text"])
        lines.extend(fenced(source_text, source_language))

        try:
            parsed_source = json.loads(prepared["source_text"])
        except (json.JSONDecodeError, TypeError):
            parsed_source = None
        if parsed_source != prepared["source_payload"]:
            lines.extend(
                [
                    "",
                    "## Structured source payload",
                    "",
                    *fenced(
                        json.dumps(prepared["source_payload"], ensure_ascii=False, indent=2),
                        "json",
                    ),
                ]
            )
        else:
            lines.extend(
                [
                    "",
                    "The parsed source text and structured source payload are identical for this case.",
                ]
            )

        if prepared["parent_table"] is not None:
            lines.extend(
                [
                    "",
                    "## Parent table representation",
                    "",
                    *fenced(
                        json.dumps(prepared["parent_table"], ensure_ascii=False, indent=2),
                        "json",
                    ),
                ]
            )

        lines.extend(
            [
                "",
                "## Prepared-example metadata",
                "",
                *fenced(
                    json.dumps(prepared["metadata"], ensure_ascii=False, indent=2),
                    "json",
                ),
                "",
                "## Held-out human references",
                "",
            ]
        )
        for reference_index, reference in enumerate(prepared["references"], start=1):
            lines.extend(
                [
                    f"### Reference {reference_index}",
                    "",
                    *fenced(reference),
                    "",
                ]
            )

        lines.extend(["## Generated outputs", ""])
        for variant in VARIANT_ORDER:
            row = by_variant[variant]
            lines.extend(
                [
                    f"### {VARIANT_LABELS[variant]}",
                    "",
                    *output_metadata_table(row, full_model_label),
                    "",
                    "#### Exact generated text",
                    "",
                    *fenced(row.generated_text),
                    "",
                ]
            )

        lines.extend(
            [
                "## Per-output metrics",
                "",
                *per_example_metric_table(case_rows, metrics),
                "",
                "Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.",
                "",
                "## Structured judge annotations",
                "",
            ]
        )
        for variant in VARIANT_ORDER:
            generation = by_variant[variant]
            annotation = annotation_by_id[generation.generation_id]
            lines.extend(
                [
                    f"### {VARIANT_LABELS[variant]}",
                    "",
                    *annotation_section(annotation),
                    "",
                ]
            )

        lines.extend(["---", ""])

    lines.extend(
        [
            "# Artifact provenance",
            "",
            "The following SHA-256 hashes identify every persisted input used to build this dossier.",
            "",
            *md_table(
                ["Artifact", "SHA-256"],
                [[path, digest] for path, digest in sorted(artifact_hashes.items())],
            ),
            "",
            "The complete raw metric JSONL files remain authoritative for metric implementation details such as sentence-level HHEM scores and durations. This document preserves every headline score while avoiding duplication of those low-level diagnostic payloads.",
            "",
        ]
    )

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "output_path": str(OUTPUT_PATH),
        "population": {
            "datasets": 5,
            "examples": 25,
            "conditions": 3,
            "generations": len(generations),
            "reference_metric_records": len(reference_metrics),
            "source_metric_records": len(source_metrics),
            "annotation_records": len(annotations),
        },
        "condition_counts": dict(Counter(row.variant_id for row in generations)),
        "dataset_counts": dict(Counter(row.dataset_id for row in generations)),
        "full_system_models": full_models,
        "artifact_sha256": artifact_hashes,
    }
    return "\n".join(lines), manifest


def main() -> None:
    print("[1/4] Loading and validating generations, metrics and annotations...", flush=True)
    document, manifest = build_document()
    print("[2/4] Writing the self-contained Markdown dossier...", flush=True)
    OUTPUT_PATH.write_text(document, encoding="utf-8")
    print("[3/4] Writing the machine-readable dossier manifest...", flush=True)
    OUTPUT_MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("[4/4] Complete.", flush=True)
    print(f"Document: {OUTPUT_PATH}")
    print(f"Manifest: {OUTPUT_MANIFEST_PATH}")
    print(f"Document bytes: {OUTPUT_PATH.stat().st_size:,}")
    print(f"Document lines: {len(document.splitlines()):,}")


if __name__ == "__main__":
    main()
