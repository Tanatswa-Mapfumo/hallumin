"""Build the protected 25-example evidence bank from sealed artifacts."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = REPO_DIR.parent
OUTPUT_PATH = (
    PROJECT_DIR
    / "docs/evaluation/PROTECTED_HOLDOUT_25_COMPLETE_RESULTS_BANK.md"
)

FULL_ROOT = REPO_DIR / "evaluation/protected_holdout_full_system"
BASELINE_ROOT = REPO_DIR / "evaluation/protected_holdout_baseline"

SELECTION_PATH = FULL_ROOT / "prepared/protected_selection_manifest.json"
FULL_MANIFEST_PATH = FULL_ROOT / "results/protected_batch_manifest.json"
FULL_CONFIG_PATH = FULL_ROOT / "config/protected_full_system_flash.json"
FULL_SUMMARY_PATH = FULL_ROOT / "results/protected_generation_summary.csv"
STAGE_USAGE_PATH = FULL_ROOT / "results/stage_token_usage.csv"

SEALED_PAIRED_PATH = (
    BASELINE_ROOT / "comparison/full_system_and_baseline_sealed.jsonl"
)
METRIC_INPUT_PATH = (
    BASELINE_ROOT / "comparison/full_system_and_baseline_for_metrics.jsonl"
)
BASELINE_GENERATIONS_PATH = (
    BASELINE_ROOT / "generations/baseline_generations_sealed.jsonl"
)
REFERENCE_METRICS_PATH = (
    BASELINE_ROOT / "results/reference_alignment_metrics.jsonl"
)
SOURCE_METRICS_PATH = (
    BASELINE_ROOT / "results/source_grounded_metrics.jsonl"
)
JUDGE_ANNOTATIONS_PATH = (
    BASELINE_ROOT / "gpt56_judge/results/gpt56_structured_annotations.jsonl"
)

CONDITION_LABELS = {
    "full_system": "Full System",
    "baseline": "Baseline",
}

LOWER_IS_BETTER = {
    "ter",
    "corpus_ter",
    "hhem_2_1_open_unsupported_sentence_rate",
}

CORPUS_METRICS = {"corpus_bleu", "corpus_chrf", "corpus_ter"}

METRIC_NAMES = {
    "alignscore_base": "AlignScore (base)",
    "bertscore_f1": "BERTScore F1",
    "bleu": "BLEU",
    "chrf": "chrF",
    "corpus_bleu": "Corpus BLEU",
    "corpus_chrf": "Corpus chrF",
    "corpus_ter": "Corpus TER",
    "hhem_2_1_open_mean_support": "HHEM mean support",
    "hhem_2_1_open_min_sentence_support": "HHEM minimum sentence support",
    "hhem_2_1_open_unsupported_sentence_rate": (
        "HHEM unsupported-sentence rate"
    ),
    "meteor": "METEOR",
    "rouge1": "ROUGE-1",
    "rouge2": "ROUGE-2",
    "rougeL": "ROUGE-L",
    "rougeLsum": "ROUGE-Lsum",
    "ter": "TER",
}

PRIMARY_METRICS = {
    "bertscore_f1",
    "chrf",
    "meteor",
    "alignscore_base",
    "hhem_2_1_open_mean_support",
    "hhem_2_1_open_unsupported_sentence_rate",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(PROJECT_DIR.resolve()))


def clean(value: Any) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    if isinstance(value, (bool, np.bool_)):
        return "Yes" if value else "No"
    if isinstance(value, (np.floating, float)):
        return f"{float(value):.4f}"
    if isinstance(value, (np.integer, int)):
        return f"{int(value)}"
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(clean(value) for value in row) + " |"
        for row in rows
    )
    return "\n".join(lines)


def code_block(value: str, language: str = "text") -> str:
    return f"````{language}\n{value.rstrip()}\n````"


def word_count(value: str) -> int:
    return len(re.findall(r"\S+", value))


def direction(metric_name: str) -> str:
    return "Lower" if metric_name in LOWER_IS_BETTER else "Higher"


def adjusted_delta(metric_name: str, full_score: float, baseline_score: float) -> float:
    if metric_name in LOWER_IS_BETTER:
        return baseline_score - full_score
    return full_score - baseline_score


def outcome(delta: float, tolerance: float = 1e-12) -> str:
    if delta > tolerance:
        return "Full System"
    if delta < -tolerance:
        return "Baseline"
    return "Tie"


def bootstrap_interval(values: np.ndarray, seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(10_000, len(values)))
    means = values[indices].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def annotation_text(annotation: dict[str, Any] | None) -> str:
    if annotation is None:
        return "No annotation record was found."
    if not annotation["errors"]:
        return "GPT-5.6 Sol reported no errors."
    lines = []
    for index, error in enumerate(annotation["errors"], start=1):
        lines.extend(
            [
                f"{index}. **{error['category']}**",
                f"   - Error span: {error['error_span']}",
                "   - Correction or explanation: "
                f"{error['correction_or_explanation']}",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    required = [
        SELECTION_PATH,
        FULL_MANIFEST_PATH,
        FULL_CONFIG_PATH,
        FULL_SUMMARY_PATH,
        STAGE_USAGE_PATH,
        SEALED_PAIRED_PATH,
        METRIC_INPUT_PATH,
        BASELINE_GENERATIONS_PATH,
        REFERENCE_METRICS_PATH,
        SOURCE_METRICS_PATH,
        JUDGE_ANNOTATIONS_PATH,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing protected evaluation artifacts:\n" + "\n".join(missing)
        )

    selection = read_json(SELECTION_PATH)
    full_manifest = read_json(FULL_MANIFEST_PATH)
    full_summary = pd.read_csv(FULL_SUMMARY_PATH)
    stage_usage = pd.read_csv(STAGE_USAGE_PATH)
    sealed_records = read_jsonl(SEALED_PAIRED_PATH)
    metric_input_records = read_jsonl(METRIC_INPUT_PATH)
    baseline_records = read_jsonl(BASELINE_GENERATIONS_PATH)
    reference_metrics = pd.DataFrame(read_jsonl(REFERENCE_METRICS_PATH))
    source_metrics = pd.DataFrame(read_jsonl(SOURCE_METRICS_PATH))
    annotations = read_jsonl(JUDGE_ANNOTATIONS_PATH)

    selection_order = [
        (str(item["dataset_id"]), str(item["example_id"]))
        for item in selection["run_order"]
    ]
    selected_keys = set(selection_order)

    sealed_by_key = {
        (row["dataset_id"], str(row["example_id"]), row["variant_id"]): row
        for row in sealed_records
    }
    metric_input_by_key = {
        (row["dataset_id"], str(row["example_id"]), row["variant_id"]): row
        for row in metric_input_records
    }
    annotation_by_key = {
        (row["dataset_id"], str(row["example_id"]), row["variant_id"]): row
        for row in annotations
    }
    summary_by_key = {
        (str(row.dataset_id), str(row.example_id)): row
        for row in full_summary.itertuples(index=False)
    }
    selection_by_key = {
        (str(item["dataset_id"]), str(item["example_id"])): item
        for item in selection["run_order"]
    }

    assert len(selection_order) == 25
    assert len(selected_keys) == 25
    assert len(sealed_records) == 50
    assert len(metric_input_records) == 50
    assert len(baseline_records) == 25
    assert len(annotations) == 50
    assert all((key[0], key[1], "full_system") in sealed_by_key for key in selection_order)
    assert all((key[0], key[1], "baseline") in sealed_by_key for key in selection_order)

    all_metrics = pd.concat([reference_metrics, source_metrics], ignore_index=True)
    scored_metrics = all_metrics[all_metrics["status"] == "scored"].copy()

    individual_metrics = scored_metrics[
        ~scored_metrics["metric_name"].isin(CORPUS_METRICS)
    ].copy()

    paired = (
        individual_metrics.pivot_table(
            index=["dataset_id", "example_id", "metric_name"],
            columns="variant_id",
            values="score",
            aggfunc="first",
        )
        .dropna()
        .reset_index()
    )
    paired["adjusted_delta"] = paired.apply(
        lambda row: adjusted_delta(
            row["metric_name"], row["full_system"], row["baseline"]
        ),
        axis=1,
    )

    macro_rows = []
    for metric_name, group in paired.groupby("metric_name"):
        deltas = group["adjusted_delta"].to_numpy(dtype=float)
        low, high = bootstrap_interval(deltas)
        full_score = float(group["full_system"].mean())
        baseline_score = float(group["baseline"].mean())
        delta = adjusted_delta(metric_name, full_score, baseline_score)
        macro_rows.append(
            {
                "metric_name": metric_name,
                "baseline": baseline_score,
                "full_system": full_score,
                "adjusted_delta": delta,
                "ci_low": low,
                "ci_high": high,
                "full_wins": int((deltas > 1e-12).sum()),
                "ties": int((np.abs(deltas) <= 1e-12).sum()),
                "baseline_wins": int((deltas < -1e-12).sum()),
                "preferred": outcome(delta),
            }
        )
    macro = pd.DataFrame(macro_rows).sort_values("metric_name")

    corpus = scored_metrics[scored_metrics["metric_name"].isin(CORPUS_METRICS)]
    corpus_pivot = (
        corpus.pivot_table(
            index=["dataset_id", "metric_name"],
            columns="variant_id",
            values="score",
            aggfunc="first",
        )
        .dropna()
        .reset_index()
    )
    corpus_pivot["adjusted_delta"] = corpus_pivot.apply(
        lambda row: adjusted_delta(
            row["metric_name"], row["full_system"], row["baseline"]
        ),
        axis=1,
    )

    dataset_means = (
        individual_metrics.groupby(
            ["dataset_id", "metric_name", "variant_id"], as_index=False
        )["score"]
        .mean()
        .pivot(
            index=["dataset_id", "metric_name"],
            columns="variant_id",
            values="score",
        )
        .dropna()
        .reset_index()
    )
    dataset_means["adjusted_delta"] = dataset_means.apply(
        lambda row: adjusted_delta(
            row["metric_name"], row["full_system"], row["baseline"]
        ),
        axis=1,
    )
    dataset_means["preferred"] = dataset_means["adjusted_delta"].map(outcome)

    judge = pd.DataFrame(
        [
            {
                **{key: value for key, value in row.items() if key != "errors"},
                "condition": CONDITION_LABELS[row["variant_id"]],
            }
            for row in annotations
        ]
    )

    judge_pairs = (
        judge.pivot_table(
            index=["dataset_id", "example_id"],
            columns="condition",
            values="error_count",
            aggfunc="first",
        )
        .dropna()
        .reset_index()
    )
    judge_pairs["comparison"] = np.where(
        judge_pairs["Full System"] < judge_pairs["Baseline"],
        "Full System fewer",
        np.where(
            judge_pairs["Full System"] > judge_pairs["Baseline"],
            "Full System more",
            "Equal",
        ),
    )

    category_rows = []
    for row in annotations:
        counts = Counter(error["category"] for error in row["errors"])
        for category in [
            "NAME",
            "NUMBER",
            "WORD",
            "CONTEXT",
            "NOT CHECKABLE",
            "OTHER",
            "OMISSION",
            "TASK/FORMAT",
        ]:
            category_rows.append(
                {
                    "dataset_id": row["dataset_id"],
                    "example_id": str(row["example_id"]),
                    "condition": CONDITION_LABELS[row["variant_id"]],
                    "category": category,
                    "count": counts.get(category, 0),
                }
            )
    categories = pd.DataFrame(category_rows)

    length_rows = []
    for row in sealed_records:
        length_rows.append(
            {
                "dataset_id": row["dataset_id"],
                "example_id": str(row["example_id"]),
                "condition": CONDITION_LABELS[row["variant_id"]],
                "words": word_count(row["generated_text"]),
            }
        )
    lengths = pd.DataFrame(length_rows)

    metric_availability_rows = []
    for (metric_name, status), group in all_metrics.groupby(["metric_name", "status"]):
        metric_availability_rows.append(
            [METRIC_NAMES.get(metric_name, metric_name), status, len(group)]
        )

    lines: list[str] = []
    add = lines.append

    add("# Protected Holdout 25: Complete Results Evidence Bank")
    add("")
    add(
        "> Purpose: a result- and output-focused information bank from which a full "
        "dissertation evaluation chapter can be written. It preserves the protected "
        "experimental design, every measured score, every generated output, every "
        "reference, the normalized source supplied for each case, and all GPT-5.6 Sol "
        "structured annotations. It is not itself a polished chapter."
    )
    add("")
    add("## 1. Evidence status")
    add("")
    add(
        table(
            ["Component", "Status", "Count", "Evidence"],
            [
                ["Protected examples", "Complete", 25, "5 datasets x 5 examples"],
                ["Full System outputs", "Complete", 25, "One released output per example"],
                ["Baseline outputs", "Complete", 25, "One direct generic-call output per example"],
                ["Paired outputs", "Complete", 50, "25 matched Full System/Baseline pairs"],
                [
                    "Reference metrics",
                    "Complete except PARENT",
                    len(reference_metrics),
                    "All configured observations retained, including unavailable statuses",
                ],
                [
                    "Source-grounded metrics",
                    "Complete",
                    len(source_metrics),
                    "AlignScore and three HHEM diagnostics for all 50 outputs",
                ],
                [
                    "GPT-5.6 Sol structured annotations",
                    "Complete",
                    len(annotations),
                    "One independent annotation per output",
                ],
                [
                    "Human annotations on this protected set",
                    "Not collected",
                    0,
                    "Do not describe GPT annotations as human gold labels",
                ],
            ],
        )
    )
    add("")
    add("### Core artifact paths")
    add("")
    for label, path in [
        ("Protected selection", SELECTION_PATH),
        ("Full System batch manifest", FULL_MANIFEST_PATH),
        ("Full System run summary", FULL_SUMMARY_PATH),
        ("Sealed paired generations", SEALED_PAIRED_PATH),
        ("Reference-unsealed metrics copy", METRIC_INPUT_PATH),
        ("Reference metric observations", REFERENCE_METRICS_PATH),
        ("Source-grounded metric observations", SOURCE_METRICS_PATH),
        ("GPT-5.6 Sol annotations", JUDGE_ANNOTATIONS_PATH),
    ]:
        add(f"- [{label}]({rel(path)})")
    add("")

    add("## 2. Headline evidence")
    add("")
    for item in [
        f"Full System has the better direction-adjusted macro mean on all {len(macro)} scored per-example automatic metrics.",
        "Full System wins all 13 per-example metric families on DART and ToTTo.",
        "Baseline wins 10 of 13 per-example metric families on E2E; both conditions receive zero GPT-reported errors there.",
        "SportSett splits six metric families to each condition with one tie.",
        "GPT-5.6 Sol reports 16 errors for each condition; 18 Full System outputs and 14 Baseline outputs have zero reported errors.",
        "Full System native support rate is 1.0 for all 25 released outputs.",
        "PARENT produced no numerical scores and is not evidence for either condition.",
    ]:
        add(f"- {item}")
    add("")

    add("## 3. Experimental design and isolation")
    add("")
    add(
        table(
            ["Property", "Recorded value"],
            [
                ["Experiment", full_manifest.get("experiment")],
                ["Selection timestamp", full_manifest.get("selection_date")],
                ["Protected/unseen", full_manifest.get("protected_unseen")],
                ["Examples", full_manifest.get("examples")],
                ["Dataset allocation", json.dumps(full_manifest.get("datasets"), sort_keys=True)],
                ["Historical overlap at selection", selection.get("historical_overlap_count_at_selection")],
                ["Frozen Git commit", full_manifest.get("git_commit")],
                ["Frozen implementation SHA-256", full_manifest.get("implementation_sha256")],
                ["Full System configuration SHA-256", full_manifest.get("configuration_sha256")],
                ["Generation seed", full_manifest.get("generation_seed")],
                ["Provider seed forwarded", full_manifest.get("provider_seed_forwarded")],
                ["Human references available during generation", "No"],
                ["Generations per condition per example", 1],
            ],
        )
    )
    add("")
    add("### Conditions")
    add("")
    add(
        table(
            ["Condition", "Model", "Input request", "Architecture", "Reference access"],
            [
                [
                    "Full System",
                    "DeepSeek V4 Flash for all six roles",
                    "Benchmark task-specific request and explicit task contract",
                    "Six-role workflow with evidence, verification, Writer, support mapping, and audit",
                    "None during generation",
                ],
                [
                    "Baseline",
                    "DeepSeek V4 Flash",
                    "Understand the supplied data and report its strongest supported findings.",
                    "One direct model call; no supplied task family or output-form metadata",
                    "None during generation",
                ],
            ],
        )
    )
    add("")
    add(
        "The comparison deliberately tests whether the workflow can infer and enforce "
        "the appropriate communication task better than a direct generic call using "
        "the same model family. It does not isolate architecture from prompt "
        "specificity. Any dissertation claim must describe the treatment as the "
        "complete task-aware workflow, not as a pure agent-count ablation."
    )
    add("")
    add("### Full System model-role configuration")
    add("")
    model_rows = []
    for role, model in full_manifest.get("models_by_role", {}).items():
        model_rows.append([role, model])
    add(table(["Role", "Model"], model_rows))
    add("")
    parameter_rows = []
    for item in full_manifest.get("model_parameters", []):
        parameter_rows.append(
            [item["role"], item["temperature"], item["max_tokens"], item["builder"]]
        )
    add(table(["Role", "Temperature", "Maximum tokens", "Builder"], parameter_rows))
    add("")
    add("### GPT-5.6 Sol annotation protocol")
    add("")
    add(
        table(
            ["Setting", "Value"],
            [
                ["Judge", "gpt-5.6-sol"],
                ["Reasoning effort", "high"],
                ["Calls", "50 independent single-output calls"],
                ["Human references supplied", "No"],
                ["Other condition output supplied", "No"],
                ["Condition identity supplied", "No"],
                ["Metric scores supplied", "No"],
                ["Common benchmark task context supplied", "Yes"],
                [
                    "Taxonomy",
                    "NAME, NUMBER, WORD, CONTEXT, NOT CHECKABLE, OTHER, OMISSION, TASK/FORMAT",
                ],
            ],
        )
    )
    add("")

    add("## 4. Metric framework")
    add("")
    add(
        table(
            ["Class", "Metrics", "What the class contributes", "Main limitation"],
            [
                [
                    "Lexical/reference alignment",
                    "BLEU, chrF, METEOR, ROUGE, TER",
                    "Measures wording and content overlap with human references",
                    "Penalises valid paraphrase and different report lengths",
                ],
                [
                    "Semantic reference alignment",
                    "BERTScore F1",
                    "Measures contextual semantic similarity to references",
                    "High semantic similarity does not guarantee exact factuality",
                ],
                [
                    "Table-aware alignment",
                    "PARENT",
                    "Intended to combine reference and table entailment",
                    "Unavailable in this run; no PARENT score can be claimed",
                ],
                [
                    "Source-grounded diagnostics",
                    "AlignScore, HHEM",
                    "Tests support against normalized source rather than reference wording",
                    "Long structured inputs and model/context limits affect comparability",
                ],
                [
                    "Independent structured review",
                    "GPT-5.6 Sol error annotations",
                    "Produces span-level categories and explanations",
                    "An LLM judgement, not a human gold standard",
                ],
                [
                    "White-box workflow evidence",
                    "Support rate, support map, evidence/fact/insight counts, audit",
                    "Shows traceability and workflow behaviour",
                    "Available only for Full System and not an external quality score",
                ],
            ],
        )
    )
    add("")
    add(
        "Recommended chapter emphasis: BERTScore, chrF, METEOR, AlignScore, the HHEM "
        "support diagnostics, and GPT-5.6's category-level annotations. BLEU, ROUGE, "
        "and TER remain useful secondary evidence. Corpus metrics should be labelled "
        "as dataset-level. PARENT must be reported as unavailable."
    )
    add("")
    add("### Metric availability")
    add("")
    add(table(["Metric", "Status", "Observations"], metric_availability_rows))
    add("")
    add(
        "PARENT generated no numerical results: 30 observations were unavailable "
        "because the optional KaijuML PARENT package was not installed, and 20 were "
        "skipped because the corresponding adapter did not expose a PARENT-compatible "
        "table. PARENT is therefore excluded from all comparative claims."
    )
    add("")

    add("## 5. Overall automatic results")
    add("")
    add(
        "The adjusted difference is defined so that a positive value always favours "
        "Full System. For TER and HHEM unsupported-sentence rate, lower is better and "
        "the subtraction is reversed. The confidence interval is a descriptive "
        "10,000-resample paired bootstrap over the 25 examples; it should not be "
        "treated as a substitute for a larger protected test set."
    )
    add("")
    macro_table_rows = []
    for row in macro.itertuples(index=False):
        macro_table_rows.append(
            [
                METRIC_NAMES.get(row.metric_name, row.metric_name),
                direction(row.metric_name),
                row.baseline,
                row.full_system,
                row.adjusted_delta,
                f"[{row.ci_low:.4f}, {row.ci_high:.4f}]",
                f"{row.full_wins}/{row.ties}/{row.baseline_wins}",
                row.preferred,
            ]
        )
    add(
        table(
            [
                "Metric",
                "Better direction",
                "Baseline",
                "Full System",
                "Adjusted difference",
                "Paired bootstrap 95% CI",
                "Full/Tie/Base wins",
                "Macro preference",
            ],
            macro_table_rows,
        )
    )
    add("")
    add(
        "The paired intervals exclude zero for AlignScore, BERTScore, BLEU, chrF, "
        "HHEM minimum sentence support, METEOR, ROUGE-1, ROUGE-2, and TER. They cross "
        "zero for HHEM mean support, HHEM unsupported-sentence rate, ROUGE-L, and "
        "ROUGE-Lsum. This pattern supports an overall alignment improvement while "
        "showing that not every grounding or sequence-overlap diagnostic is equally "
        "stable across the 25 cases."
    )
    add("")
    add("### Corpus-level metrics by dataset")
    add("")
    corpus_rows = []
    for row in corpus_pivot.sort_values(["dataset_id", "metric_name"]).itertuples(index=False):
        corpus_rows.append(
            [
                row.dataset_id,
                METRIC_NAMES[row.metric_name],
                direction(row.metric_name),
                row.baseline,
                row.full_system,
                row.adjusted_delta,
                outcome(row.adjusted_delta),
            ]
        )
    add(
        table(
            [
                "Dataset",
                "Metric",
                "Better direction",
                "Baseline",
                "Full System",
                "Adjusted difference",
                "Preferred",
            ],
            corpus_rows,
        )
    )
    add("")

    add("## 6. Results by dataset")
    add("")
    for dataset_id in [
        "e2e_nlg",
        "web_nlg",
        "dart",
        "totto",
        "sportsett_basketball",
    ]:
        add(f"### {dataset_id}")
        add("")
        rows = []
        subset = dataset_means[dataset_means["dataset_id"] == dataset_id]
        for row in subset.sort_values("metric_name").itertuples(index=False):
            rows.append(
                [
                    METRIC_NAMES.get(row.metric_name, row.metric_name),
                    direction(row.metric_name),
                    row.baseline,
                    row.full_system,
                    row.adjusted_delta,
                    row.preferred,
                ]
            )
        add(
            table(
                [
                    "Metric",
                    "Better direction",
                    "Baseline",
                    "Full System",
                    "Adjusted difference",
                    "Preferred",
                ],
                rows,
            )
        )
        add("")

    add("## 7. GPT-5.6 Sol structured error results")
    add("")
    judge_overall = []
    for condition, group in judge.groupby("condition"):
        judge_overall.append(
            [
                condition,
                len(group),
                int(group["error_count"].sum()),
                float(group["error_count"].mean()),
                int((group["error_count"] == 0).sum()),
                int(group["total_tokens"].fillna(0).sum()),
            ]
        )
    add(
        table(
            [
                "Condition",
                "Outputs",
                "Reported errors",
                "Mean errors/output",
                "Outputs with zero errors",
                "Judge tokens",
            ],
            judge_overall,
        )
    )
    add("")
    judge_dataset_rows = []
    for (dataset_id, condition), group in judge.groupby(["dataset_id", "condition"]):
        judge_dataset_rows.append(
            [
                dataset_id,
                condition,
                len(group),
                int(group["error_count"].sum()),
                float(group["error_count"].mean()),
                int((group["error_count"] == 0).sum()),
            ]
        )
    add(
        table(
            [
                "Dataset",
                "Condition",
                "Outputs",
                "Reported errors",
                "Mean errors/output",
                "Zero-error outputs",
            ],
            judge_dataset_rows,
        )
    )
    add("")
    category_pivot = (
        categories.groupby(["category", "condition"])["count"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    category_table_rows = []
    for row in category_pivot.itertuples(index=False):
        category_table_rows.append(
            [row.category, getattr(row, "Baseline"), getattr(row, "_2", None)]
        )
    # Avoid pandas' tuple-name mangling for the column with a space.
    category_table_rows = [
        [
            category,
            int(categories[(categories["category"] == category) & (categories["condition"] == "Baseline")]["count"].sum()),
            int(categories[(categories["category"] == category) & (categories["condition"] == "Full System")]["count"].sum()),
        ]
        for category in [
            "NAME",
            "NUMBER",
            "WORD",
            "CONTEXT",
            "NOT CHECKABLE",
            "OTHER",
            "OMISSION",
            "TASK/FORMAT",
        ]
    ]
    add(table(["Error category", "Baseline", "Full System"], category_table_rows))
    add("")
    pair_counts = judge_pairs["comparison"].value_counts().to_dict()
    add(
        table(
            ["Paired outcome", "Examples"],
            [
                ["Full System fewer GPT-reported errors", pair_counts.get("Full System fewer", 0)],
                ["Equal error count", pair_counts.get("Equal", 0)],
                ["Full System more GPT-reported errors", pair_counts.get("Full System more", 0)],
            ],
        )
    )
    add("")
    add(
        "The taxonomy clarifies the equal totals. Baseline's errors were dominated by "
        "TASK/FORMAT violations (11), particularly generic responses that ignored "
        "ToTTo's highlighted-cell restriction or SportSett's multi-paragraph form. "
        "Full System reduced TASK/FORMAT errors to six but increased CONTEXT errors "
        "from two to six, all concentrated in the event-report setting. No NAME, NOT "
        "CHECKABLE, or OTHER errors were reported for either condition."
    )
    add("")
    add(
        "These annotations should be described as GPT-5.6 Sol judgements. They are "
        "useful diagnostic evidence but cannot establish human precision or recall "
        "until checked against independent human annotations. Some annotations are "
        "strict, such as treating omission of a full birth date as a NUMBER error, so "
        "category totals should be read with the included explanations."
    )
    add("")

    add("## 8. Output length and qualitative form")
    add("")
    length_table_rows = []
    for (dataset_id, condition), group in lengths.groupby(["dataset_id", "condition"]):
        length_table_rows.append(
            [
                dataset_id,
                condition,
                float(group["words"].mean()),
                float(group["words"].median()),
                int(group["words"].min()),
                int(group["words"].max()),
            ]
        )
    add(
        table(
            ["Dataset", "Condition", "Mean words", "Median", "Minimum", "Maximum"],
            length_table_rows,
        )
    )
    add("")
    add(
        "Full System was much longer on SportSett (292.6 versus 159.4 mean words) but "
        "far shorter on ToTTo (18.0 versus 62.4). This is not a uniform verbosity "
        "effect. It reflects genre control: expansion for event reports and "
        "compression for highlighted-cell descriptions. The ToTTo change aligns with "
        "large metric and judge improvements. The SportSett expansion improves "
        "coverage and several reference metrics but creates more opportunities for "
        "contextual interpretation errors."
    )
    add("")

    add("## 9. Full System provenance and execution evidence")
    add("")
    add(
        table(
            ["Recorded property", "Result"],
            [
                ["Successful protected executions", int((full_summary["execution_outcome"] == "success").sum())],
                ["Primary-evaluation eligible", int(full_summary["primary_evaluation_eligible"].sum())],
                ["Approved", int((full_summary["release_status"] == "approved").sum())],
                [
                    "Approved with warnings",
                    int((full_summary["release_status"] == "approved_with_warnings").sum()),
                ],
                ["Mean native support rate", float(full_summary["native_support_rate"].mean())],
                ["Unsupported factual sentences", int(full_summary["unsupported_factual_sentence_count"].sum())],
                ["Normal LLM Writer path", int((full_summary["final_generation_path"] == "normal_llm_writer").sum())],
                ["Auditor-repaired path", int((full_summary["final_generation_path"] == "auditor_repaired").sum())],
                ["Deterministic fallback path", int((full_summary["final_generation_path"] == "deterministic_fallback").sum())],
                ["Evidence items", int(full_summary["evidence_item_count"].sum())],
                ["Verified facts", int(full_summary["verified_fact_count"].sum())],
                ["Rejected facts", int(full_summary["rejected_fact_count"].sum())],
                ["Verified insights", int(full_summary["verified_insight_count"].sum())],
                ["Rejected insights", int(full_summary["rejected_insight_count"].sum())],
            ],
        )
    )
    add("")
    add(
        "All 25 outputs passed the internal audit with complete mapped support, and no "
        "invalid fact or evidence identifiers were recorded. This supports a claim of "
        "successful provenance enforcement. It does not support a claim of zero "
        "factual error, because the independent judge still found contextual and "
        "task-level issues."
    )
    add("")
    add("### Evidence, facts, and insights by dataset")
    add("")
    workflow_rows = []
    for dataset_id, group in full_summary.groupby("dataset_id"):
        workflow_rows.append(
            [
                dataset_id,
                int(group["evidence_item_count"].sum()),
                int(group["fact_candidate_count"].sum()),
                int(group["verified_fact_count"].sum()),
                int(group["rejected_fact_count"].sum()),
                int(group["insight_candidate_count"].sum()),
                int(group["verified_insight_count"].sum()),
                int(group["rejected_insight_count"].sum()),
            ]
        )
    add(
        table(
            [
                "Dataset",
                "Evidence items",
                "Fact candidates",
                "Verified facts",
                "Rejected facts",
                "Insight candidates",
                "Verified insights",
                "Rejected insights",
            ],
            workflow_rows,
        )
    )
    add("")
    add("### Operational footprint (secondary evidence)")
    add("")
    baseline_tokens = sum(int(row.get("total_tokens") or 0) for row in baseline_records)
    baseline_seconds = sum(float(row.get("elapsed_seconds") or 0) for row in baseline_records)
    add(
        table(
            ["Condition", "Provider-reported requests", "Provider-reported tokens", "Elapsed seconds"],
            [
                [
                    "Full System",
                    int(stage_usage["requests"].sum()),
                    int(stage_usage["total_tokens"].sum()),
                    float(full_summary["elapsed_seconds"].sum()),
                ],
                ["Baseline", 25, baseline_tokens, baseline_seconds],
            ],
        )
    )
    add("")
    add(
        "Runtime and token use are retained for reproducibility, not treated as the "
        "main evaluation outcome. The conditions differ by orders of magnitude in "
        "computation, particularly on SportSett. This makes it important to present "
        "quality gains alongside the operational trade-off, without reducing the "
        "dissertation to a cost study."
    )
    add("")
    stage_rows = []
    for stage, group in stage_usage.groupby("stage"):
        stage_rows.append(
            [
                stage,
                int(group["requests"].sum()),
                int(group["input_tokens"].sum()),
                int(group["output_tokens"].sum()),
                int(group["total_tokens"].sum()),
            ]
        )
    stage_rows.sort(key=lambda row: row[-1], reverse=True)
    add(table(["Stage", "Requests", "Input tokens", "Output tokens", "Total tokens"], stage_rows))
    add("")

    add("## 10. Evidence-use notes")
    add("")
    for item in [
        "Positive adjusted differences favour Full System; TER and unsupported-sentence rate are reversed because lower is better.",
        "The protected sample contains five examples per dataset and one generation per condition.",
        "The treatment is the complete task-aware workflow; the comparison does not isolate architecture from prompt specificity.",
        "GPT-5.6 Sol annotations are model judgements, not human gold labels.",
        "Native support rate is Full System-only provenance evidence, not a paired quality metric.",
        "PARENT was unavailable and must not be presented as a scored result.",
    ]:
        add(f"- {item}")
    add("")

    add("# Appendix A. Complete case-level evidence")
    add("")
    add(
        "Each case below contains the normalized source presented to both conditions, "
        "the task-specific Full System request, the generic Baseline request, all human "
        "references (unsealed only after generation), both outputs, per-output metrics, "
        "GPT-5.6 Sol annotations, and Full System provenance statistics."
    )
    add("")

    for case_number, key in enumerate(selection_order, start=1):
        dataset_id, example_id = key
        full = metric_input_by_key[(dataset_id, example_id, "full_system")]
        baseline = metric_input_by_key[(dataset_id, example_id, "baseline")]
        sealed_full = sealed_by_key[(dataset_id, example_id, "full_system")]
        sealed_baseline = sealed_by_key[(dataset_id, example_id, "baseline")]
        full_annotation = annotation_by_key.get((dataset_id, example_id, "full_system"))
        baseline_annotation = annotation_by_key.get((dataset_id, example_id, "baseline"))
        run = summary_by_key[key]
        selected = selection_by_key[key]

        add(f"## A{case_number}. {dataset_id} / {example_id}")
        add("")
        add(
            table(
                ["Field", "Value"],
                [
                    ["Dataset", dataset_id],
                    ["Example ID", example_id],
                    ["Task family", full["task_family"]],
                    ["Output mode", full["output_mode"]],
                    ["Language", full["language"]],
                    ["Source SHA-256", selected["source_sha256"]],
                    ["Reference SHA-256", selected["reference_sha256"]],
                    ["Full System request", full["request"]],
                    ["Baseline request", sealed_baseline["request"]],
                ],
            )
        )
        add("")
        add("### Normalized source supplied during generation")
        add("")
        source_language = "json" if full["source_text"].lstrip().startswith("{") else "text"
        add(code_block(full["source_text"], source_language))
        add("")
        add("### Human reference outputs")
        add("")
        for reference_number, reference in enumerate(full["references"], start=1):
            add(f"**Reference {reference_number}**")
            add("")
            add(code_block(reference, "text"))
            add("")
        add("### Full System output")
        add("")
        add(code_block(full["generated_text"], "markdown"))
        add("")
        add("### Baseline output")
        add("")
        add(code_block(baseline["generated_text"], "markdown"))
        add("")

        case_metric_rows = []
        case_metrics = paired[
            (paired["dataset_id"] == dataset_id)
            & (paired["example_id"].astype(str) == example_id)
        ]
        for row in case_metrics.sort_values("metric_name").itertuples(index=False):
            case_metric_rows.append(
                [
                    METRIC_NAMES.get(row.metric_name, row.metric_name),
                    direction(row.metric_name),
                    row.baseline,
                    row.full_system,
                    row.adjusted_delta,
                    outcome(row.adjusted_delta),
                ]
            )
        add("### Automatic metrics")
        add("")
        add(
            table(
                [
                    "Metric",
                    "Better direction",
                    "Baseline",
                    "Full System",
                    "Adjusted difference",
                    "Preferred",
                ],
                case_metric_rows,
            )
        )
        add("")
        add("### GPT-5.6 Sol structured annotations")
        add("")
        add("**Full System**")
        add("")
        add(annotation_text(full_annotation))
        add("")
        add("**Baseline**")
        add("")
        add(annotation_text(baseline_annotation))
        add("")
        add("### Full System provenance and execution record")
        add("")
        add(
            table(
                ["Property", "Value"],
                [
                    ["Run ID", run.run_id],
                    ["Execution outcome", run.execution_outcome],
                    ["Final generation path", run.final_generation_path],
                    ["Final Writer mode", run.final_writer_mode],
                    ["Release status", run.release_status],
                    ["Audit decision", run.audit_decision],
                    ["Repair rounds", run.repair_rounds_used],
                    ["Native support rate", run.native_support_rate],
                    ["Factual sentences", run.factual_sentence_count],
                    ["Supported sentences", run.supported_sentence_count],
                    ["Evidence items", run.evidence_item_count],
                    ["Verified facts", run.verified_fact_count],
                    ["Rejected facts", run.rejected_fact_count],
                    ["Verified insights", run.verified_insight_count],
                    ["Rejected insights", run.rejected_insight_count],
                    ["Full System words", word_count(full["generated_text"])],
                    ["Baseline words", word_count(baseline["generated_text"])],
                    ["Full System elapsed seconds", sealed_full.get("elapsed_seconds")],
                    ["Baseline elapsed seconds", sealed_baseline.get("elapsed_seconds")],
                    ["Full System provider-reported tokens", run.provider_reported_total_tokens],
                    ["Baseline provider-reported tokens", sealed_baseline.get("total_tokens")],
                    ["Pipeline result", run.pipeline_result_path],
                ],
            )
        )
        add("")

    add("# Appendix B. Complete GPT-5.6 Sol non-zero annotations")
    add("")
    add(
        "This appendix repeats every non-zero annotation in one place for taxonomy "
        "analysis. Zero-error records remain visible in each case section."
    )
    add("")
    for row in sorted(
        (item for item in annotations if item["error_count"] > 0),
        key=lambda item: (
            item["dataset_id"],
            str(item["example_id"]),
            item["variant_id"],
        ),
    ):
        add(
            f"## {row['dataset_id']} / {row['example_id']} / "
            f"{CONDITION_LABELS[row['variant_id']]}"
        )
        add("")
        add(annotation_text(row))
        add("")

    add("# Appendix C. Reproducibility inventory")
    add("")
    inventory_rows = []
    for label, path in [
        ("Protected selection manifest", SELECTION_PATH),
        ("Full System batch manifest", FULL_MANIFEST_PATH),
        ("Full System configuration", FULL_CONFIG_PATH),
        ("Full System generation summary", FULL_SUMMARY_PATH),
        ("Full System stage usage", STAGE_USAGE_PATH),
        ("Sealed paired outputs", SEALED_PAIRED_PATH),
        ("Metrics input with references", METRIC_INPUT_PATH),
        ("Baseline sealed generations", BASELINE_GENERATIONS_PATH),
        ("Reference metrics", REFERENCE_METRICS_PATH),
        ("Source-grounded metrics", SOURCE_METRICS_PATH),
        ("GPT-5.6 Sol annotations", JUDGE_ANNOTATIONS_PATH),
    ]:
        inventory_rows.append([label, rel(path), path.stat().st_size])
    add(table(["Artifact", "Path", "Bytes"], inventory_rows))
    add("")
    add(
        "End of evidence bank. Numerical claims in a dissertation should be copied "
        "from the direction-aware tables in this document or recomputed from the "
        "linked JSONL artifacts."
    )

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Lines: {len(lines):,}")
    print(f"Bytes: {OUTPUT_PATH.stat().st_size:,}")


if __name__ == "__main__":
    main()
