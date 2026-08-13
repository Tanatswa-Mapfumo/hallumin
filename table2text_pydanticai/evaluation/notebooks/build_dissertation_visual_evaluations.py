"""Build the dissertation visual-evaluation notebook.

This script writes a reproducible Jupyter notebook that turns the saved
evaluation artifacts into dissertation-ready figures. The focus is output
quality, factual support, reference alignment, model-strength comparisons,
and ablation evidence. Runtime and cost are intentionally not foregrounded.
"""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = PROJECT_DIR / "evaluation/notebooks/dissertation_visual_evaluations.ipynb"


def markdown(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip() + "\n",
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip() + "\n",
    }


SETUP_CODE = r'''
from pathlib import Path
import json
import math
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Markdown, display

project_dir = Path("/Users/realgobs/Documents/MScproject/table2text_pydanticai")
fig_dir = project_dir / "evaluation/results/figures"
fig_dir.mkdir(parents=True, exist_ok=True)

main_generations_path = project_dir / "evaluation/generations/five_dataset_five_each_raw_generic_flash_20260805_181001_combined_generations.jsonl"
main_reference_metrics_path = project_dir / "evaluation/results/five_dataset_five_each_raw_generic_flash_20260805_181001_reference_metrics.jsonl"
main_source_metrics_path = project_dir / "evaluation/results/five_dataset_five_each_raw_generic_flash_20260805_181001_source_grounded_metrics.jsonl"

ablation_generations_path = project_dir / "evaluation/generations/ablation_sportsett_4934_20260805_021058_combined_generations.jsonl"
ablation_reference_metrics_path = project_dir / "evaluation/results/ablation_sportsett_4934_20260805_021058_reference_metrics.jsonl"

pro_generations_path = project_dir / "evaluation/generations/four_dataset_pro_comparison_20260812_215239_combined_generations.jsonl"
pro_reference_metrics_path = project_dir / "evaluation/results/four_dataset_pro_comparison_20260812_215239_reference_metrics_combined.jsonl"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.color": "#e8e8e8",
    "grid.linewidth": 0.8,
    "legend.frameon": False,
})

variant_labels = {
    "full_system": "Full System",
    "raw_generic_flash": "Raw Flash",
    "raw_deepseek_v4_flash": "Raw Flash",
    "full_system_pro": "Full System Pro",
    "raw_generic_pro": "Raw Pro",
    "no_insight_synthesis": "No Insight Synthesis",
    "no_writer_quality_revision": "No Writer Quality",
    "no_audit_repair_rounds": "No Audit Repair",
}

variant_colors = {
    "full_system": "#2563eb",
    "raw_generic_flash": "#f97316",
    "raw_deepseek_v4_flash": "#f97316",
    "full_system_pro": "#0f766e",
    "raw_generic_pro": "#9333ea",
    "no_insight_synthesis": "#db2777",
    "no_writer_quality_revision": "#7c3aed",
    "no_audit_repair_rounds": "#64748b",
}

metric_labels = {
    "bleu": "BLEU",
    "chrf": "chrF",
    "rougeL": "ROUGE-L",
    "meteor": "METEOR",
    "bertscore_f1": "BERTScore F1",
    "ter": "TER",
    "alignscore_base": "AlignScore",
    "hhem_2_1_open_mean_support": "HHEM mean support",
    "hhem_2_1_open_min_sentence_support": "HHEM min sentence",
    "hhem_2_1_open_unsupported_sentence_rate": "Unsupported sentence rate",
}

core_reference_metrics = ["bleu", "chrf", "rougeL", "meteor", "bertscore_f1"]
semantic_content_metrics = ["chrf", "rougeL", "meteor", "bertscore_f1"]
source_metrics = [
    "alignscore_base",
    "hhem_2_1_open_mean_support",
    "hhem_2_1_open_min_sentence_support",
    "hhem_2_1_open_unsupported_sentence_rate",
]

def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        print(f"Missing artifact: {path}")
        return pd.DataFrame()
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return pd.DataFrame(rows)

def scored(frame, metrics=None):
    if frame.empty:
        return frame.copy()
    out = frame[frame["status"].eq("scored")].copy()
    if metrics is not None:
        out = out[out["metric_name"].isin(metrics)]
    return out

def metric_macro(frame, metrics=None, variants=None):
    data = scored(frame, metrics)
    if data.empty:
        return pd.DataFrame()
    macro = (
        data.groupby(["variant_id", "metric_name"], as_index=False)
        .agg(score=("score", "mean"), higher_is_better=("higher_is_better", "first"))
    )
    if variants is not None:
        macro = macro[macro["variant_id"].isin(variants)]
    return macro

def metric_pivot(frame, metrics=None):
    data = scored(frame, metrics)
    if data.empty:
        return pd.DataFrame()
    return data.pivot_table(
        index=["dataset_id", "example_id", "metric_name"],
        columns="variant_id",
        values="score",
        aggfunc="mean",
    ).reset_index()

def direction_for_metric(frame, metric_name):
    subset = frame[frame["metric_name"].eq(metric_name)]
    if subset.empty:
        return 1
    return 1 if bool(subset["higher_is_better"].iloc[0]) else -1

def directional_gain(full_score, raw_score, higher_is_better=True):
    if pd.isna(full_score) or pd.isna(raw_score):
        return np.nan
    return (full_score - raw_score) if higher_is_better else (raw_score - full_score)

def oriented_score(score, higher_is_better=True):
    if pd.isna(score):
        return np.nan
    if higher_is_better:
        return score
    return 1 / (1 + max(score, 0))

def savefig(name):
    path = fig_dir / name
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.show()
    print(f"Saved: {path}")

def word_count(text):
    return len((text or "").split())

def reference_word_count(refs):
    if isinstance(refs, list) and refs:
        return float(np.mean([word_count(ref) for ref in refs]))
    return np.nan

main_generations = read_jsonl(main_generations_path)
main_reference_metrics = read_jsonl(main_reference_metrics_path)
main_source_metrics = read_jsonl(main_source_metrics_path)
ablation_generations = read_jsonl(ablation_generations_path)
ablation_reference_metrics = read_jsonl(ablation_reference_metrics_path)
pro_generations = read_jsonl(pro_generations_path)
pro_reference_metrics = read_jsonl(pro_reference_metrics_path)

summary = pd.DataFrame([
    {"artifact": "main_generations", "rows": len(main_generations)},
    {"artifact": "main_reference_metrics", "rows": len(main_reference_metrics)},
    {"artifact": "main_source_metrics", "rows": len(main_source_metrics)},
    {"artifact": "ablation_generations", "rows": len(ablation_generations)},
    {"artifact": "ablation_reference_metrics", "rows": len(ablation_reference_metrics)},
    {"artifact": "pro_generations", "rows": len(pro_generations)},
    {"artifact": "pro_reference_metrics", "rows": len(pro_reference_metrics)},
])
display(summary)
'''


CELLS = [
    markdown(
        """
        # Dissertation Visual Evaluations

        This notebook builds ten dissertation-ready evaluation visuals from the saved experiment artifacts.
        It deliberately focuses on output quality rather than time or cost: reference alignment, semantic similarity,
        source-grounded factuality, metric-family behaviour, ablation evidence, narration/coverage, and model-strength effects.

        The figures are saved to `evaluation/results/figures/`.
        """
    ),
    code(SETUP_CODE),
    markdown(
        """
        ## 1. Main 25-Example Macro Reference Metrics

        This line chart shows the headline comparison between the full architecture and the raw generic Flash baseline
        across the shortlisted reference-alignment metrics, excluding TER because TER has the opposite interpretation.
        """
    ),
    code(
        r'''
macro = metric_macro(main_reference_metrics, core_reference_metrics, ["full_system", "raw_generic_flash"])
plot_data = macro.pivot(index="metric_name", columns="variant_id", values="score").reindex(core_reference_metrics)

fig, ax = plt.subplots(figsize=(10.8, 5.8))
x = np.arange(len(plot_data.index))
for variant in ["full_system", "raw_generic_flash"]:
    values = plot_data[variant].values
    ax.plot(
        x,
        values,
        marker="o",
        linewidth=2.8,
        markersize=8,
        label=variant_labels[variant],
        color=variant_colors[variant],
    )
    for xi, value in zip(x, values):
        ax.text(xi, value + 0.012, f"{value:.3f}", ha="center", va="bottom", fontsize=8, color=variant_colors[variant])

ax.set_title("Macro Reference Alignment: Full System vs Raw Flash")
ax.set_ylabel("Mean score, higher is better")
ax.set_xticks(x)
ax.set_xticklabels([metric_labels[m] for m in plot_data.index])
ax.set_ylim(0, max(1.0, np.nanmax(plot_data.values) * 1.15))
ax.margins(x=0.08)
ax.legend(loc="upper left")
savefig("01_main_macro_reference_metrics.png")
display(plot_data.rename(index=metric_labels, columns=variant_labels))
'''
    ),
    markdown(
        """
        ## 2. Main 25-Example TER Comparison

        TER is kept separate because lower is better. The slope format makes the edit-distance reduction easier to read.
        """
    ),
    code(
        r'''
ter_macro = metric_macro(main_reference_metrics, ["ter"], ["full_system", "raw_generic_flash"])
ter_plot = ter_macro.pivot(index="metric_name", columns="variant_id", values="score")

fig, ax = plt.subplots(figsize=(7.5, 5.2))
variants = ["full_system", "raw_generic_flash"]
values = [float(ter_plot.loc["ter", variant]) for variant in variants]
ax.plot(
    [0, 1],
    values,
    color="#334155",
    linewidth=2.5,
    marker="o",
    markersize=9,
)
for xi, variant, value in zip([0, 1], variants, values):
    ax.scatter([xi], [value], s=120, color=variant_colors[variant], zorder=3)
    ax.text(xi, value + max(values) * 0.035, f"{value:.3f}", ha="center", fontsize=9)
if len(values) == 2:
    ax.text(0.5, max(values) * 0.92, f"directional improvement: {values[1] - values[0]:.3f}", ha="center", color="#334155")
ax.set_title("TER: Lower Means Closer Surface Realisation")
ax.set_ylabel("Mean TER, lower is better")
ax.set_xticks([0, 1])
ax.set_xticklabels([variant_labels[v] for v in variants])
ax.set_ylim(0, max(values) * 1.25)
savefig("02_main_macro_ter.png")
display(ter_plot.rename(columns=variant_labels))
'''
    ),
    markdown(
        """
        ## 3. Per-Dataset Architecture-Gain Heatmap

        Positive values mean the full system beat the raw generic baseline after respecting each metric's direction.
        This makes it easy to see where the architecture helps most and where more work is needed.
        """
    ),
    code(
        r'''
heat_metrics = ["bleu", "chrf", "rougeL", "meteor", "bertscore_f1", "ter"]
pivot = metric_pivot(main_reference_metrics, heat_metrics)
gain_rows = []
for _, row in pivot.iterrows():
    metric = row["metric_name"]
    if "full_system" not in row or "raw_generic_flash" not in row:
        continue
    higher = direction_for_metric(main_reference_metrics, metric) == 1
    gain_rows.append({
        "dataset_id": row["dataset_id"],
        "metric_name": metric,
        "directional_gain": directional_gain(row.get("full_system"), row.get("raw_generic_flash"), higher),
    })

gain_df = pd.DataFrame(gain_rows)
heat = gain_df.pivot_table(index="dataset_id", columns="metric_name", values="directional_gain", aggfunc="mean").reindex(columns=heat_metrics)

fig, ax = plt.subplots(figsize=(11, 5.8))
vmax = np.nanmax(np.abs(heat.values))
im = ax.imshow(heat.values, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
ax.set_title("Directional Full-System Gain By Dataset")
ax.set_xticks(np.arange(len(heat.columns)))
ax.set_xticklabels([metric_labels[m] for m in heat.columns], rotation=30, ha="right")
ax.set_yticks(np.arange(len(heat.index)))
ax.set_yticklabels(heat.index)
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        value = heat.iloc[i, j]
        if pd.notna(value):
            ax.text(j, i, f"{value:+.3f}", ha="center", va="center", fontsize=8)
cbar = fig.colorbar(im, ax=ax, shrink=0.85)
cbar.set_label("Directional gain over raw baseline")
savefig("03_architecture_gain_heatmap.png")
display(heat)
'''
    ),
    markdown(
        """
        ## 4. Per-Dataset Semantic And Content Dumbbell Chart

        This chart focuses on chrF and BERTScore F1 because they tell a useful dissertation story:
        chrF captures character-level content overlap, while BERTScore captures semantic similarity.
        """
    ),
    code(
        r'''
dumb_metrics = ["chrf", "bertscore_f1"]
dumb_data = (
    scored(main_reference_metrics, dumb_metrics)
    .groupby(["dataset_id", "metric_name", "variant_id"], as_index=False)["score"].mean()
)

fig, axes = plt.subplots(1, 2, figsize=(13, 5.8), sharey=True)
datasets = sorted(dumb_data["dataset_id"].unique())
for ax, metric in zip(axes, dumb_metrics):
    subset = dumb_data[dumb_data["metric_name"].eq(metric)]
    for yi, dataset in enumerate(datasets):
        vals = subset[subset["dataset_id"].eq(dataset)].set_index("variant_id")["score"]
        raw = vals.get("raw_generic_flash", np.nan)
        full = vals.get("full_system", np.nan)
        ax.plot([raw, full], [yi, yi], color="#94a3b8", linewidth=2)
        ax.scatter(raw, yi, color=variant_colors["raw_generic_flash"], s=80, label=variant_labels["raw_generic_flash"] if yi == 0 else "")
        ax.scatter(full, yi, color=variant_colors["full_system"], s=80, label=variant_labels["full_system"] if yi == 0 else "")
        if pd.notna(raw) and pd.notna(full):
            ax.text(max(raw, full) + 0.004, yi, f"{full-raw:+.3f}", va="center", fontsize=8)
    ax.set_title(metric_labels[metric])
    ax.set_xlabel("Score")
    ax.set_yticks(np.arange(len(datasets)))
    ax.set_yticklabels(datasets)
    ax.set_xlim(max(0, np.nanmin(subset["score"]) - 0.05), min(1.02, np.nanmax(subset["score"]) + 0.06))
axes[0].legend(loc="lower right")
fig.suptitle("Semantic And Content Alignment By Dataset", fontsize=15, fontweight="bold")
savefig("04_semantic_content_dumbbell.png")
display(dumb_data.pivot_table(index=["dataset_id", "metric_name"], columns="variant_id", values="score"))
'''
    ),
    markdown(
        """
        ## 5. Metric-Family Profile

        This line profile groups the metrics into dissertation-friendly families: lexical overlap, sequence/content
        overlap, semantic similarity, and edit efficiency. TER is converted to a higher-is-better complement here only.
        """
    ),
    code(
        r'''
family_map = {
    "bleu": "Lexical overlap",
    "chrf": "Lexical overlap",
    "rougeL": "Sequence/content overlap",
    "meteor": "Sequence/content overlap",
    "bertscore_f1": "Semantic similarity",
    "ter": "Edit efficiency",
}
family_metrics = list(family_map)
family_rows = []
for _, row in scored(main_reference_metrics, family_metrics).iterrows():
    family_rows.append({
        "variant_id": row["variant_id"],
        "metric_family_label": family_map[row["metric_name"]],
        "oriented_score": oriented_score(row["score"], bool(row["higher_is_better"])),
    })
family_df = pd.DataFrame(family_rows)
family_macro = (
    family_df.groupby(["variant_id", "metric_family_label"], as_index=False)["oriented_score"].mean()
)
families = ["Lexical overlap", "Sequence/content overlap", "Semantic similarity", "Edit efficiency"]
plot_data = family_macro.pivot(index="metric_family_label", columns="variant_id", values="oriented_score").reindex(families)

fig, ax = plt.subplots(figsize=(10.8, 5.8))
x = np.arange(len(families))
for variant in ["full_system", "raw_generic_flash"]:
    values = plot_data[variant].values
    ax.plot(
        x,
        values,
        marker="o",
        linewidth=2.8,
        markersize=8,
        label=variant_labels[variant],
        color=variant_colors[variant],
    )
    for xi, value in zip(x, values):
        ax.text(xi, value + 0.012, f"{value:.3f}", ha="center", va="bottom", fontsize=8, color=variant_colors[variant])
ax.set_title("Metric-Family Profile")
ax.set_ylabel("Oriented mean score, higher is better")
ax.set_xticks(x)
ax.set_xticklabels(families, rotation=20, ha="right")
ax.set_ylim(0, max(1.0, np.nanmax(plot_data.values) * 1.15))
ax.margins(x=0.08)
ax.legend(loc="upper left")
savefig("05_metric_family_profile.png")
display(plot_data.rename(columns=variant_labels))
'''
    ),
    markdown(
        """
        ## 6. Full-System Win Rate By Metric

        This line chart asks a simple question: across individual examples, how often did the architecture beat the raw
        generic baseline for each metric?
        """
    ),
    code(
        r'''
win_metrics = ["bleu", "chrf", "rougeL", "meteor", "bertscore_f1", "ter"]
pivot = metric_pivot(main_reference_metrics, win_metrics)
win_rows = []
for metric in win_metrics:
    subset = pivot[pivot["metric_name"].eq(metric)].copy()
    higher = direction_for_metric(main_reference_metrics, metric) == 1
    wins = 0
    ties = 0
    comparable = 0
    for _, row in subset.iterrows():
        full = row.get("full_system")
        raw = row.get("raw_generic_flash")
        if pd.isna(full) or pd.isna(raw):
            continue
        comparable += 1
        diff = full - raw if higher else raw - full
        if abs(diff) < 1e-9:
            ties += 1
        elif diff > 0:
            wins += 1
    win_rows.append({
        "metric_name": metric,
        "win_rate": wins / comparable if comparable else np.nan,
        "tie_rate": ties / comparable if comparable else np.nan,
        "n": comparable,
    })

win_df = pd.DataFrame(win_rows)
fig, ax = plt.subplots(figsize=(10.8, 5.8))
x = np.arange(len(win_df))
ax.plot(
    x,
    win_df["win_rate"],
    color="#2563eb",
    marker="o",
    linewidth=2.8,
    markersize=8,
)
ax.fill_between(x, 0.5, win_df["win_rate"], where=win_df["win_rate"] >= 0.5, color="#bfdbfe", alpha=0.55, interpolate=True)
for xi, value, n in zip(x, win_df["win_rate"], win_df["n"]):
    ax.text(xi, value + 0.035, f"{value:.0%}\n(n={n})", ha="center", fontsize=8)
ax.axhline(0.5, color="#64748b", linestyle="--", linewidth=1.2)
ax.text(len(win_df) - 0.6, 0.52, "50% parity line", color="#64748b", fontsize=9)
ax.set_ylim(0, 1.05)
ax.set_title("How Often The Full System Beats Raw Flash")
ax.set_ylabel("Full-system win rate")
ax.set_xticks(x)
ax.set_xticklabels([metric_labels[m] for m in win_df["metric_name"]], rotation=20, ha="right")
savefig("06_full_system_win_rate_by_metric.png")
display(win_df)
'''
    ),
    markdown(
        """
        ## 7. Source-Grounded Factuality Diagnostics

        This line chart compares outputs against the structured source rather than only the human reference.
        AlignScore and HHEM support are higher-is-better; unsupported sentence rate is lower-is-better.
        """
    ),
    code(
        r'''
source_macro = metric_macro(main_source_metrics, source_metrics, ["full_system", "raw_generic_flash"])
plot_data = source_macro.pivot(index="metric_name", columns="variant_id", values="score").reindex(source_metrics)

fig, ax = plt.subplots(figsize=(11, 5.8))
x = np.arange(len(plot_data.index))
for variant in ["full_system", "raw_generic_flash"]:
    values = plot_data[variant].values
    ax.plot(
        x,
        values,
        marker="o",
        linewidth=2.8,
        markersize=8,
        label=variant_labels[variant],
        color=variant_colors[variant],
    )
    for xi, value in zip(x, values):
        ax.text(xi, value + 0.012, f"{value:.3f}", ha="center", va="bottom", fontsize=8, color=variant_colors[variant])
ax.set_title("Source-Grounded Factuality Diagnostics")
ax.set_ylabel("Mean score")
ax.set_xticks(x)
ax.set_xticklabels([metric_labels[m] for m in plot_data.index], rotation=25, ha="right")
ax.set_ylim(0, max(1.0, np.nanmax(plot_data.values) * 1.15))
ax.margins(x=0.08)
ax.legend(loc="upper left")
savefig("07_source_grounded_diagnostics.png")
display(plot_data.rename(index=metric_labels, columns=variant_labels))
'''
    ),
    markdown(
        """
        ## 8. SportSett 4934 Ablation Metric Impact

        This line chart isolates components of the architecture on the same example. Positive values mean the full
        system scored better than the ablated variant after metric direction is accounted for.
        """
    ),
    code(
        r'''
ab_metrics = ["chrf", "rougeL", "meteor", "bertscore_f1", "ter"]
ab_pivot = metric_pivot(ablation_reference_metrics, ab_metrics)
ab_variants = [
    "raw_deepseek_v4_flash",
    "no_insight_synthesis",
    "no_writer_quality_revision",
    "no_audit_repair_rounds",
]
rows = []
for _, row in ab_pivot.iterrows():
    metric = row["metric_name"]
    higher = direction_for_metric(ablation_reference_metrics, metric) == 1
    full = row.get("full_system")
    for variant in ab_variants:
        if variant in row and pd.notna(row.get(variant)):
            rows.append({
                "variant_id": variant,
                "metric_name": metric,
                "directional_full_gain": directional_gain(full, row.get(variant), higher),
            })
ab_gain = pd.DataFrame(rows)
ab_heat = ab_gain.pivot_table(index="variant_id", columns="metric_name", values="directional_full_gain", aggfunc="mean").reindex(ab_variants)

fig, ax = plt.subplots(figsize=(11.5, 5.8))
x = np.arange(len(ab_heat.columns))
for variant in ab_variants:
    values = ab_heat.loc[variant].values
    ax.plot(
        x,
        values,
        marker="o",
        linewidth=2.3,
        markersize=7,
        label=variant_labels.get(variant, variant),
        color=variant_colors.get(variant),
    )
ax.axhline(0, color="#334155", linewidth=1.2)
ax.set_title("Ablation Impact: Full-System Gain Over Each Variant")
ax.set_ylabel("Directional full-system gain")
ax.set_xticks(x)
ax.set_xticklabels([metric_labels[m] for m in ab_heat.columns], rotation=25, ha="right")
ax.legend(loc="best")
savefig("08_ablation_metric_impact.png")
display(ab_heat.rename(index=variant_labels, columns=metric_labels))
'''
    ),
    markdown(
        """
        ## 9. Output Coverage And Narrative Scope

        This is not a speed chart. It shows, as a line profile, whether each system tends to under-produce, match,
        or over-expand relative to the available human references. It is useful for discussing narration and coverage.
        """
    ),
    code(
        r'''
coverage = main_generations.copy()
coverage["generated_words"] = coverage["generated_text"].map(word_count)
coverage["reference_words"] = coverage["references"].map(reference_word_count)
coverage["output_reference_ratio"] = coverage["generated_words"] / coverage["reference_words"]

coverage_macro = (
    coverage.groupby(["dataset_id", "variant_id"], as_index=False)
    .agg(
        generated_words=("generated_words", "mean"),
        reference_words=("reference_words", "mean"),
        output_reference_ratio=("output_reference_ratio", "mean"),
    )
)

datasets = sorted(coverage_macro["dataset_id"].unique())
fig, axes = plt.subplots(1, 2, figsize=(14, 5.8), sharey=True)
for ax, column, title, x_label in [
    (axes[0], "generated_words", "Mean Generated Length", "Words"),
    (axes[1], "output_reference_ratio", "Output / Reference Length Ratio", "Ratio"),
]:
    x = np.arange(len(datasets))
    for variant in ["full_system", "raw_generic_flash"]:
        vals = (
            coverage_macro[coverage_macro["variant_id"].eq(variant)]
            .set_index("dataset_id")
            .reindex(datasets)[column]
        )
        ax.plot(
            x,
            vals,
            marker="o",
            linewidth=2.6,
            markersize=7,
            label=variant_labels[variant],
            color=variant_colors[variant],
        )
    if column == "output_reference_ratio":
        ax.axhline(1.0, color="#64748b", linestyle="--", linewidth=1.2)
        ax.text(len(datasets) - 1.25, 1.04, "reference length", color="#64748b", fontsize=9)
    ax.set_title(title)
    ax.set_ylabel(x_label)
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, rotation=25, ha="right")
axes[0].legend(loc="lower right")
fig.suptitle("Narrative Scope And Coverage Profile", fontsize=15, fontweight="bold")
savefig("09_output_coverage_profile.png")
display(coverage_macro.pivot_table(index="dataset_id", columns="variant_id", values=["generated_words", "output_reference_ratio"]))
'''
    ),
    markdown(
        """
        ## 10. Model-Strength Comparison And ToTTo Subject-Linking Case

        This line chart combines the Flash and Pro experiments. It separates two ideas: whether a stronger raw model
        narrows the gap, and whether the architecture still protects against table-linking errors that a raw model can make.
        """
    ),
    code(
        r'''
main_4 = scored(main_reference_metrics, ["chrf", "rougeL", "meteor", "bertscore_f1"])
main_4 = main_4[main_4["dataset_id"].isin(["e2e_nlg", "totto", "web_nlg", "dart"])]
main_4 = main_4[main_4["variant_id"].isin(["full_system", "raw_generic_flash"])]
pro_4 = scored(pro_reference_metrics, ["chrf", "rougeL", "meteor", "bertscore_f1"])

combined = pd.concat([main_4, pro_4], ignore_index=True)
macro = (
    combined.groupby(["variant_id", "metric_name"], as_index=False)["score"].mean()
)
plot = macro.pivot(index="metric_name", columns="variant_id", values="score").reindex(["chrf", "rougeL", "meteor", "bertscore_f1"])
variant_order = ["full_system", "raw_generic_flash", "full_system_pro", "raw_generic_pro"]

fig, ax = plt.subplots(figsize=(12.5, 5.8))
x = np.arange(len(plot.index))
for variant in variant_order:
    if variant not in plot:
        continue
    ax.plot(
        x,
        plot[variant].values,
        marker="o",
        linewidth=2.4,
        markersize=7,
        label=variant_labels[variant],
        color=variant_colors[variant],
    )
ax.set_title("Flash/Pro Model Strength Across Four Matched Datasets")
ax.set_ylabel("Mean score, higher is better")
ax.set_xticks(x)
ax.set_xticklabels([metric_labels[m] for m in plot.index])
ax.set_ylim(0, max(1.0, np.nanmax(plot.values) * 1.12))
ax.legend(ncols=2, loc="lower right")
savefig("10_model_strength_comparison.png")
display(plot.rename(index=metric_labels, columns=variant_labels))

totto = scored(combined, ["chrf", "meteor", "bertscore_f1"])
totto = totto[
    (totto["dataset_id"].eq("totto"))
    & (totto["example_id"].astype(str).str.endswith("204"))
]
totto_plot = totto.pivot_table(index="metric_name", columns="variant_id", values="score", aggfunc="mean").reindex(["chrf", "meteor", "bertscore_f1"])

fig, ax = plt.subplots(figsize=(10, 5.4))
x = np.arange(len(totto_plot.index))
for variant in variant_order:
    if variant in totto_plot:
        ax.plot(
            x,
            totto_plot[variant].values,
            marker="o",
            linewidth=2.4,
            markersize=7,
            label=variant_labels[variant],
            color=variant_colors[variant],
        )
ax.set_title("ToTTo 204: Subject-Linking Stress Case")
ax.set_ylabel("Score")
ax.set_xticks(x)
ax.set_xticklabels([metric_labels[m] for m in totto_plot.index])
upper = 1.0 if totto_plot.empty else max(1.0, np.nanmax(totto_plot.values) * 1.12)
ax.set_ylim(0, upper)
ax.legend(ncols=2, loc="lower right")
savefig("10b_totto_subject_linking_case.png")

display(Markdown("""
**Qualitative note:** in this ToTTo example, the architecture links the highlighted percentage to Ma Ying-jeou,
while the raw Pro baseline can still attach the same value to Vincent Siew. This is a useful dissertation caveat:
stronger models improve fluency and sometimes overlap, but they do not remove the need for structure-aware grounding.
"""))
display(totto_plot.rename(index=metric_labels, columns=variant_labels))
'''
    ),
    markdown(
        """
        ## Figure Files

        The notebook saves these dissertation-focused figures:

        1. `01_main_macro_reference_metrics.png`
        2. `02_main_macro_ter.png`
        3. `03_architecture_gain_heatmap.png`
        4. `04_semantic_content_dumbbell.png`
        5. `05_metric_family_profile.png`
        6. `06_full_system_win_rate_by_metric.png`
        7. `07_source_grounded_diagnostics.png`
        8. `08_ablation_metric_impact.png`
        9. `09_output_coverage_profile.png`
        10. `10_model_strength_comparison.png`

        A supporting case-study figure is also saved as `10b_totto_subject_linking_case.png`.
        """
    ),
]


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    notebook = {
        "cells": CELLS,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
