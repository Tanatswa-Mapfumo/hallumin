"""Build transparent interactive GPT-5.6 Sol annotation artifacts.

This script does not call an API. The semantic judgements below were produced in
an interactive model session using the same source-only error taxonomy as the
project's OpenAI judge. Existing API-authenticated annotations are read but never
modified.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from table2text.evaluation.models import GenerationRecord, LLMJudgeAnnotationRecord


PROJECT_DIR = Path(__file__).resolve().parents[2]
EVALUATION_DIR = PROJECT_DIR / "evaluation"
RESULT_DIR = EVALUATION_DIR / "task_aware_direct_baseline" / "results"

TASK_AWARE_GENERATIONS = (
    EVALUATION_DIR
    / "task_aware_direct_baseline"
    / "generations"
    / "task_aware_direct_flash_25_generations.jsonl"
)
CANONICAL_GENERATIONS = (
    EVALUATION_DIR
    / "generations"
    / "five_dataset_five_each_raw_generic_flash_20260805_181001_combined_generations.jsonl"
)
API_ANNOTATIONS = EVALUATION_DIR / "results" / "openai_structured_error_annotations.jsonl"

TASK_AWARE_OUTPUT = RESULT_DIR / "task_aware_direct_flash_25_interactive_gpt56_annotations.jsonl"
CANONICAL_GAP_OUTPUT = RESULT_DIR / "canonical_gap_interactive_gpt56_annotation.jsonl"
COMBINED_OUTPUT = RESULT_DIR / "gpt56_all_75_annotations_with_provenance.jsonl"
SUMMARY_CSV = RESULT_DIR / "gpt56_all_75_annotation_summary.csv"
PROVENANCE_OUTPUT = RESULT_DIR / "interactive_gpt56_annotation_provenance.json"
REPORT_OUTPUT = RESULT_DIR / "interactive_gpt56_annotation_report.md"

JUDGE_MODEL = "gpt-5.6-sol"


def error(span: str, category: str, explanation: str) -> dict[str, str]:
    return {
        "error_span": span,
        "category": category,
        "correction_or_explanation": explanation,
    }


# Empty lists are deliberate scored judgements, not unreviewed records.
TASK_AWARE_ERRORS: dict[str, list[dict[str, str]]] = {
    "dart__dart-test-204__task_aware_direct_flash__r0__s42": [],
    "dart__dart-test-217__task_aware_direct_flash__r0__s42": [],
    "dart__dart-test-244__task_aware_direct_flash__r0__s42": [],
    "dart__dart-test-260__task_aware_direct_flash__r0__s42": [],
    "dart__dart-test-53__task_aware_direct_flash__r0__s42": [],
    "e2e_nlg__e2e_nlg-test-178__task_aware_direct_flash__r0__s42": [],
    "e2e_nlg__e2e_nlg-test-51__task_aware_direct_flash__r0__s42": [],
    "e2e_nlg__e2e_nlg-test-54__task_aware_direct_flash__r0__s42": [],
    "e2e_nlg__e2e_nlg-test-61__task_aware_direct_flash__r0__s42": [],
    "e2e_nlg__e2e_nlg-test-65__task_aware_direct_flash__r0__s42": [],
    "sportsett_basketball__4934__task_aware_direct_flash__r0__s42": [],
    "sportsett_basketball__4972__task_aware_direct_flash__r0__s42": [
        error(
            "but the Bucks could not overcome poor outside shooting.",
            "CONTEXT",
            "The source supports Milwaukee's 10-for-44 three-point shooting, but a box score alone does not establish that this was a causal barrier that produced the loss.",
        ),
        error(
            "then answered every Milwaukee push in the second half.",
            "CONTEXT",
            "The source provides quarter totals but no play-by-play sequence, so it cannot verify every Milwaukee push or a corresponding Phoenix response.",
        ),
    ],
    "sportsett_basketball__4975__task_aware_direct_flash__r0__s42": [
        error(
            "while forcing 20 Pistons turnovers.",
            "CONTEXT",
            "The source records 20 Detroit turnovers and 13 Milwaukee steals, but does not state that Milwaukee forced every turnover.",
        ),
        error(
            "but could not overcome its shooting struggles and turnovers.",
            "CONTEXT",
            "The box score supports the shooting and turnover figures, but it does not establish them as the causal explanation for Detroit's defeat.",
        ),
        error(
            "as only Griffin and Jackson scored in double figures",
            "NUMBER",
            "Andre Drummond also scored in double figures with exactly 10 points, so Griffin and Jackson were not the only Detroit players to do so.",
        ),
        error(
            "Detroit’s miscues proved costly against a Bucks team that converted those turnovers into scoring chances.",
            "CONTEXT",
            "The source contains turnover totals but no points-off-turnovers or possession-level evidence showing that Milwaukee converted those turnovers into scoring chances or that they proved causal.",
        ),
    ],
    "sportsett_basketball__4982__task_aware_direct_flash__r0__s42": [
        error(
            "Friday night",
            "NOT CHECKABLE",
            "The source supplies the date and weekday but no start time or time-of-day information.",
        ),
        error(
            "The Bucks led from the opening tip, building a 43-14 edge after the first quarter and never looking back.",
            "CONTEXT",
            "Quarter-end scores support the 43-14 first-quarter margin, but the source has no play-by-play evidence for the opening tip or for a continuous lead throughout the game.",
        ),
        error(
            "DeAndre' Bembry led all scorers with 19 points",
            "CONTEXT",
            "Bembry tied for the game-high 19 points with Milwaukee's Khris Middleton and Malcolm Brogdon rather than leading alone.",
        ),
        error(
            "Atlanta struggled against Milwaukee's pressure",
            "CONTEXT",
            "The source records 21 Atlanta turnovers but does not identify Milwaukee pressure as their cause.",
        ),
        error(
            "helping Milwaukee maintain its large lead throughout the second half.",
            "CONTEXT",
            "The source does not attribute lead maintenance to those bench performances, and quarter-end totals do not establish the continuous game state throughout the half.",
        ),
    ],
    "sportsett_basketball__4986__task_aware_direct_flash__r0__s42": [
        error(
            "Monday night",
            "NOT CHECKABLE",
            "The source supplies the date and weekday but no start time or time-of-day information.",
        )
    ],
    "totto__totto-validation-204__task_aware_direct_flash__r0__s42": [],
    "totto__totto-validation-217__task_aware_direct_flash__r0__s42": [],
    "totto__totto-validation-244__task_aware_direct_flash__r0__s42": [
        error(
            "represented Everett (39th Middlesex), and retired to run for State Treasurer.",
            "TASK/FORMAT",
            "The city/district and electoral-history details come from unhighlighted cells. The request required exactly one sentence about the highlighted cells and explicitly excluded unrelated cells.",
        )
    ],
    "totto__totto-validation-260__task_aware_direct_flash__r0__s42": [],
    "totto__totto-validation-712__task_aware_direct_flash__r0__s42": [],
    "web_nlg__web_nlg_en-test-178__task_aware_direct_flash__r0__s42": [],
    "web_nlg__web_nlg_en-test-51__task_aware_direct_flash__r0__s42": [],
    "web_nlg__web_nlg_en-test-54__task_aware_direct_flash__r0__s42": [],
    "web_nlg__web_nlg_en-test-61__task_aware_direct_flash__r0__s42": [],
    "web_nlg__web_nlg_en-test-65__task_aware_direct_flash__r0__s42": [],
}

CANONICAL_GAP_ERRORS: dict[str, list[dict[str, str]]] = {
    "sportsett_basketball__4975__full_system__r0__s42": [
        error(
            "Participant context records Milwaukee Bucks entered with 16 wins and 7 losses; Detroit Pistons entered with 13 wins and 9 losses.",
            "CONTEXT",
            "Those records each total the listed game number and therefore include this result. Milwaukee improved to 16-7 and Detroit fell to 13-9; they did not enter with those records.",
        ),
        error(
            "The entire generated output is a sequence of evidence-ledger statements and rankings rather than a coherent multi-paragraph game report.",
            "TASK/FORMAT",
            "The request required a coherent game report that leads with the result and selects the most important performances and contrasts. The output is a mechanical inventory with repeated result statements and no paragraph-level narrative organization.",
        ),
    ]
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def annotation_record(
    generation: GenerationRecord,
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    record = LLMJudgeAnnotationRecord.model_validate(
        {
            "generation_id": generation.generation_id,
            "dataset_id": generation.dataset_id,
            "example_id": generation.example_id,
            "variant_id": generation.variant_id,
            "repetition": generation.repetition,
            "judge_model": JUDGE_MODEL,
            "judge_repetition": 0,
            "status": "scored",
            "errors": errors,
            "error_count": len(errors),
            "duration_seconds": None,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "error": None,
        }
    )
    return record.model_dump(mode="json")


def build_interactive_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    task_generations = [
        GenerationRecord.model_validate(row) for row in read_jsonl(TASK_AWARE_GENERATIONS)
    ]
    task_by_id = {row.generation_id: row for row in task_generations}
    if set(task_by_id) != set(TASK_AWARE_ERRORS):
        missing = sorted(set(task_by_id) - set(TASK_AWARE_ERRORS))
        extra = sorted(set(TASK_AWARE_ERRORS) - set(task_by_id))
        raise RuntimeError(f"Task-aware identity mismatch: missing={missing}; extra={extra}")

    canonical_generations = [
        GenerationRecord.model_validate(row) for row in read_jsonl(CANONICAL_GENERATIONS)
    ]
    canonical_by_id = {row.generation_id: row for row in canonical_generations}
    if not set(CANONICAL_GAP_ERRORS).issubset(canonical_by_id):
        missing = sorted(set(CANONICAL_GAP_ERRORS) - set(canonical_by_id))
        raise RuntimeError(f"Canonical gap generations not found: {missing}")

    task_rows = [
        annotation_record(task_by_id[generation_id], TASK_AWARE_ERRORS[generation_id])
        for generation_id in sorted(TASK_AWARE_ERRORS)
    ]
    gap_rows = [
        annotation_record(canonical_by_id[generation_id], CANONICAL_GAP_ERRORS[generation_id])
        for generation_id in sorted(CANONICAL_GAP_ERRORS)
    ]
    return task_rows, gap_rows


def provenance_row(row: dict[str, Any], execution_mode: str) -> dict[str, Any]:
    return {
        **row,
        "execution_mode": execution_mode,
        "api_authenticated": execution_mode == "openai_responses_api",
    }


def summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["execution_mode"], row["variant_id"], row["dataset_id"])
        item = grouped.setdefault(
            key,
            {
                "execution_mode": key[0],
                "variant_id": key[1],
                "dataset_id": key[2],
                "outputs": 0,
                "outputs_with_errors": 0,
                "errors": 0,
            },
        )
        item["outputs"] += 1
        item["errors"] += row["error_count"]
        item["outputs_with_errors"] += int(row["error_count"] > 0)
    return [grouped[key] for key in sorted(grouped)]


def markdown_report(
    task_rows: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    api_rows: list[dict[str, Any]],
    combined_rows: list[dict[str, Any]],
) -> str:
    category_counts = Counter(
        error_item["category"]
        for row in combined_rows
        for error_item in row.get("errors", [])
    )
    variant_counts = defaultdict(lambda: {"outputs": 0, "flagged": 0, "errors": 0})
    for row in combined_rows:
        item = variant_counts[row["variant_id"]]
        item["outputs"] += 1
        item["flagged"] += int(row["error_count"] > 0)
        item["errors"] += row["error_count"]

    lines = [
        "# GPT-5.6 Sol Structured Error Annotation Results",
        "",
        "## Scope and provenance",
        "",
        f"- Judge label: `{JUDGE_MODEL}`",
        f"- Existing API-authenticated rows retained unchanged: **{len(api_rows)}**",
        f"- Interactive task-aware rows added: **{len(task_rows)}**",
        f"- Interactive canonical-gap rows added: **{len(gap_rows)}**",
        f"- Three-condition analysis rows: **{len(combined_rows)}**",
        "- The interactive rows were produced without an OpenAI API call. Their model label follows the active model selection reported for the session, but that identity and the reasoning setting were not returned by an API response.",
        "- Consequently, interactive rows must be reported separately from API-authenticated rows or accompanied by the execution-mode provenance field. They are not a silent replacement for a controlled API run.",
        "- Judgements used the project taxonomy: NAME, NUMBER, WORD, CONTEXT, NOT CHECKABLE, OTHER, OMISSION and TASK/FORMAT.",
        "- The intended basis was source data + task request + one generated output. Human references and automatic metric scores were not used as correctness criteria. Unlike the API runner, the surrounding interactive session was not a formally blinded environment.",
        "",
        "## Three-condition totals",
        "",
        "| Variant | Outputs | Outputs flagged | Errors |",
        "|---|---:|---:|---:|",
    ]
    for variant_id in sorted(variant_counts):
        item = variant_counts[variant_id]
        lines.append(
            f"| `{variant_id}` | {item['outputs']} | {item['flagged']} | {item['errors']} |"
        )

    lines.extend(
        [
            "",
            "## Error categories across all 75 rows",
            "",
            "| Category | Count |",
            "|---|---:|",
        ]
    )
    for category, count in sorted(category_counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend(
        [
            "",
            "## Interactive coverage table",
            "",
            "| Dataset | Example | Variant | Error count | Categories |",
            "|---|---|---|---:|---|",
        ]
    )
    for row in sorted(
        task_rows + gap_rows,
        key=lambda item: (
            item["dataset_id"],
            item["example_id"],
            item["variant_id"],
        ),
    ):
        categories = ", ".join(item["category"] for item in row["errors"]) or "None"
        lines.append(
            f"| `{row['dataset_id']}` | `{row['example_id']}` | "
            f"`{row['variant_id']}` | {row['error_count']} | {categories} |"
        )

    lines.extend(
        [
            "",
            "## Interactive annotations",
            "",
            "Rows not listed below were reviewed and assigned an empty error list.",
            "",
        ]
    )
    for row in task_rows + gap_rows:
        if not row["errors"]:
            continue
        lines.extend(
            [
                f"### `{row['dataset_id']}` / `{row['example_id']}` / `{row['variant_id']}`",
                "",
            ]
        )
        for index, item in enumerate(row["errors"], start=1):
            lines.extend(
                [
                    f"{index}. **{item['category']}**: “{item['error_span']}”",
                    f"   - {item['correction_or_explanation']}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "The combined file is convenient for descriptive analysis, but it contains mixed execution provenance: 49 API-authenticated annotations and 26 interactive annotations. Any dissertation table using all 75 rows should disclose this split. Confirmatory claims about GPT-5.6 Sol as an API judge should use the 49 API-authenticated rows unless the remaining cases are later rerun through the same controlled API procedure.",
            "",
            "## Artifacts",
            "",
            f"- `{TASK_AWARE_OUTPUT.relative_to(PROJECT_DIR)}`",
            f"- `{CANONICAL_GAP_OUTPUT.relative_to(PROJECT_DIR)}`",
            f"- `{COMBINED_OUTPUT.relative_to(PROJECT_DIR)}`",
            f"- `{SUMMARY_CSV.relative_to(PROJECT_DIR)}`",
            f"- `{PROVENANCE_OUTPUT.relative_to(PROJECT_DIR)}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    print("[1/5] Validating generation identities and interactive judgements...", flush=True)
    task_rows, gap_rows = build_interactive_rows()
    if len(task_rows) != 25 or len(gap_rows) != 1:
        raise RuntimeError(
            f"Expected 25 task-aware rows and one canonical gap; got {len(task_rows)} and {len(gap_rows)}"
        )

    print("[2/5] Writing separate interactive annotation artifacts...", flush=True)
    write_jsonl(TASK_AWARE_OUTPUT, task_rows)
    write_jsonl(CANONICAL_GAP_OUTPUT, gap_rows)

    print("[3/5] Combining with existing API rows without modifying them...", flush=True)
    api_rows = read_jsonl(API_ANNOTATIONS)
    if len(api_rows) != 49:
        raise RuntimeError(f"Expected 49 existing API rows; found {len(api_rows)}")
    combined_rows = [
        provenance_row(row, "openai_responses_api") for row in api_rows
    ] + [
        provenance_row(row, "interactive_session") for row in task_rows + gap_rows
    ]
    combined_rows.sort(
        key=lambda row: (
            row["dataset_id"],
            row["example_id"],
            row["variant_id"],
            row["judge_repetition"],
        )
    )
    identities = [row["generation_id"] for row in combined_rows]
    if len(combined_rows) != 75 or len(set(identities)) != 75:
        raise RuntimeError(
            f"Combined artifact must contain 75 unique generation IDs; got rows={len(combined_rows)}, unique={len(set(identities))}"
        )
    counts = Counter(row["variant_id"] for row in combined_rows)
    expected_counts = {
        "full_system": 25,
        "raw_generic_flash": 25,
        "task_aware_direct_flash": 25,
    }
    if counts != expected_counts:
        raise RuntimeError(f"Unexpected condition counts: {counts}")
    write_jsonl(COMBINED_OUTPUT, combined_rows)

    print("[4/5] Writing summary tables, provenance and report...", flush=True)
    summary = summary_rows(combined_rows)
    with SUMMARY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    provenance = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "judge_model": JUDGE_MODEL,
        "model_identity_basis": "User-reported active model selection; not independently returned by an API response.",
        "reasoning_effort_basis": "High reasoning was reported for the active session; not independently returned by an API response.",
        "execution_mode": "interactive_session",
        "openai_api_call_made": False,
        "api_authenticated": False,
        "taxonomy_source": "src/table2text/evaluation/llm_judge_annotations.py",
        "api_rows_preserved_unchanged": len(api_rows),
        "interactive_task_aware_rows": len(task_rows),
        "interactive_canonical_gap_rows": len(gap_rows),
        "controlled_blinding": False,
        "analysis_restriction": (
            "Do not describe the interactive rows as API-authenticated. Stratify by execution_mode "
            "or disclose the 49 API / 26 interactive split when reporting the combined artifact."
        ),
        "source_files": {
            "task_aware_generations": str(TASK_AWARE_GENERATIONS),
            "canonical_generations": str(CANONICAL_GENERATIONS),
            "existing_api_annotations": str(API_ANNOTATIONS),
        },
    }
    PROVENANCE_OUTPUT.write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REPORT_OUTPUT.write_text(
        markdown_report(task_rows, gap_rows, api_rows, combined_rows),
        encoding="utf-8",
    )

    print("[5/5] Complete.", flush=True)
    print(f"Task-aware annotations: {TASK_AWARE_OUTPUT}")
    print(f"Canonical gap:         {CANONICAL_GAP_OUTPUT}")
    print(f"Combined 75 rows:      {COMBINED_OUTPUT}")
    print(f"Report:                {REPORT_OUTPUT}")
    print(f"Condition counts:      {dict(counts)}")
    print(
        "Interactive error counts: "
        f"task-aware={sum(row['error_count'] for row in task_rows)}, "
        f"canonical-gap={sum(row['error_count'] for row in gap_rows)}"
    )


if __name__ == "__main__":
    main()
