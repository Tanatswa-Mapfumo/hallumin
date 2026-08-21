"""Build a dissertation-ready GPT-5.6 Sol annotation figure."""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[3]
RESULTS_DIR = PROJECT_DIR / "evaluation/results"
FIGURE_DIR = RESULTS_DIR / "figures"
ANNOTATIONS_PATH = RESULTS_DIR / "openai_structured_error_annotations.jsonl"


VARIANT_LABELS = {
    "full_system": "Full System",
    "raw_generic_flash": "Raw Generic Flash",
}

VARIANT_COLORS = {
    "full_system": "#0072B2",
    "raw_generic_flash": "#D55E00",
}

CATEGORY_COLORS = {
    "TASK/FORMAT": "#CC79A7",
    "CONTEXT": "#E69F00",
    "OMISSION": "#009E73",
    "NUMBER": "#D55E00",
    "NAME": "#56B4E9",
    "WORD": "#7C3AED",
    "NOT CHECKABLE": "#6B7280",
    "OTHER": "#374151",
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def category_counts(rows: list[dict]) -> dict[str, Counter]:
    counts: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        variant_id = row.get("variant_id")
        if variant_id not in VARIANT_LABELS:
            continue
        for error in row.get("errors") or []:
            category = (error.get("category") or "OTHER").upper()
            counts[variant_id][category] += 1
    return counts


def main() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / ".matplotlib"))

    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    rows = [
        row
        for row in read_jsonl(ANNOTATIONS_PATH)
        if row.get("status") == "scored"
        and row.get("judge_model") == "gpt-5.6-sol"
        and row.get("variant_id") in VARIANT_LABELS
    ]
    if not rows:
        raise RuntimeError(f"No scored GPT-5.6 Sol annotations found in {ANNOTATIONS_PATH}")

    by_variant: dict[str, list[dict]] = {
        variant: [row for row in rows if row.get("variant_id") == variant]
        for variant in VARIANT_LABELS
    }
    totals = {
        variant: sum(int(row.get("error_count") or 0) for row in variant_rows)
        for variant, variant_rows in by_variant.items()
    }
    outputs = {variant: len(variant_rows) for variant, variant_rows in by_variant.items()}
    outputs_with_errors = {
        variant: sum(1 for row in variant_rows if int(row.get("error_count") or 0) > 0)
        for variant, variant_rows in by_variant.items()
    }
    means = {
        variant: (totals[variant] / outputs[variant]) if outputs[variant] else 0
        for variant in VARIANT_LABELS
    }
    category_by_variant = category_counts(rows)
    category_order = [
        category
        for category in CATEGORY_COLORS
        if any(category_by_variant[variant][category] for variant in VARIANT_LABELS)
    ]

    raw_total = totals.get("raw_generic_flash", 0)
    full_total = totals.get("full_system", 0)
    reduction = ((raw_total - full_total) / raw_total * 100) if raw_total else 0.0

    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D1D5DB",
            "axes.labelcolor": "#172033",
            "xtick.color": "#172033",
            "ytick.color": "#172033",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.grid": True,
            "grid.color": "#EEF2F7",
            "grid.linewidth": 0.8,
            "legend.frameon": False,
        }
    )

    fig = plt.figure(figsize=(14.8, 8.4))
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[0.95, 1.25],
        height_ratios=[0.35, 0.65],
        hspace=0.30,
        wspace=0.22,
    )

    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis("off")
    ax_title.text(
        0.0,
        1.00,
        "GPT-5.6 Sol Structured Error Annotations",
        ha="left",
        va="top",
        fontsize=21,
        fontweight="bold",
        color="#172033",
    )
    ax_title.text(
        0.0,
        0.66,
        (
            "Cross-family judge: one output at a time, source data and task metadata only; "
            "no references, competing outputs, automatic scores, or system identity."
        ),
        ha="left",
        va="top",
        fontsize=10.7,
        color="#556070",
    )

    def card(x: float, title: str, value: str, note: str, color: str) -> None:
        rect = FancyBboxPatch(
            (x, 0.06),
            0.225,
            0.38,
            boxstyle="round,pad=0.014,rounding_size=0.025",
            linewidth=1.4,
            edgecolor=color,
            facecolor="#FFFFFF",
            transform=ax_title.transAxes,
        )
        ax_title.add_patch(rect)
        ax_title.text(
            x + 0.018,
            0.36,
            title,
            transform=ax_title.transAxes,
            fontsize=9.5,
            fontweight="bold",
            color="#556070",
            va="top",
        )
        ax_title.text(
            x + 0.018,
            0.235,
            value,
            transform=ax_title.transAxes,
            fontsize=22,
            fontweight="bold",
            color=color,
            va="top",
        )
        ax_title.text(
            x + 0.018,
            0.10,
            note,
            transform=ax_title.transAxes,
            fontsize=8.9,
            color="#556070",
            va="bottom",
        )

    card(
        0.00,
        "Scored outputs",
        str(sum(outputs.values())),
        f"{outputs['full_system']} workflow + {outputs['raw_generic_flash']} raw",
        "#374151",
    )
    card(
        0.255,
        "Total errors",
        f"{full_total} vs {raw_total}",
        "workflow vs raw generic",
        "#7C3AED",
    )
    card(
        0.51,
        "Error reduction",
        f"{reduction:.0f}%",
        "relative to raw generic",
        "#009E73",
    )
    card(
        0.765,
        "Workflow gap",
        "1 missing",
        "SportSett 4975 annotation absent",
        "#D55E00",
    )

    ax_bars = fig.add_subplot(gs[1, 0])
    variants = list(VARIANT_LABELS)
    x = range(len(variants))
    bar_width = 0.34
    ax_bars.bar(
        [i - bar_width / 2 for i in x],
        [totals[variant] for variant in variants],
        width=bar_width,
        color=[VARIANT_COLORS[variant] for variant in variants],
        label="Total errors",
    )
    ax_bars.bar(
        [i + bar_width / 2 for i in x],
        [outputs_with_errors[variant] for variant in variants],
        width=bar_width,
        color=["#9CC9E8", "#F4A582"],
        label="Outputs with errors",
    )
    ax_bars.set_title("Judge-Detected Errors by Variant")
    ax_bars.set_ylabel("Count")
    ax_bars.set_xticks(list(x))
    ax_bars.set_xticklabels([VARIANT_LABELS[variant] for variant in variants])
    ax_bars.set_ylim(0, max(raw_total, full_total) + 4)
    ax_bars.legend(loc="upper left")
    ax_bars.spines[["top", "right"]].set_visible(False)
    for i, variant in enumerate(variants):
        ax_bars.text(
            i - bar_width / 2,
            totals[variant] + 0.35,
            str(totals[variant]),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=VARIANT_COLORS[variant],
        )
        ax_bars.text(
            i + bar_width / 2,
            outputs_with_errors[variant] + 0.35,
            str(outputs_with_errors[variant]),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#556070",
        )
        ax_bars.text(
            i,
            -2.15,
            f"mean {means[variant]:.3f}/output",
            ha="center",
            va="top",
            fontsize=9,
            color="#556070",
            clip_on=False,
        )

    ax_stack = fig.add_subplot(gs[1, 1])
    y_positions = [1, 0]
    lefts = [0, 0]
    for category in category_order:
        values = [category_by_variant[variant][category] for variant in variants]
        ax_stack.barh(
            y_positions,
            values,
            left=lefts,
            height=0.42,
            color=CATEGORY_COLORS[category],
            label=category,
        )
        for idx, value in enumerate(values):
            if value:
                ax_stack.text(
                    lefts[idx] + value / 2,
                    y_positions[idx],
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=9.5,
                    fontweight="bold",
                    color="white" if category != "OMISSION" else "#172033",
                )
        lefts = [lefts[idx] + values[idx] for idx in range(len(values))]

    ax_stack.set_title("Error Category Profile")
    ax_stack.set_xlabel("Structured error count")
    ax_stack.set_yticks(y_positions)
    ax_stack.set_yticklabels([VARIANT_LABELS[variant] for variant in variants])
    ax_stack.set_xlim(0, max(raw_total, full_total) + 2)
    ax_stack.spines[["top", "right"]].set_visible(False)
    ax_stack.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=4,
        fontsize=9,
    )
    ax_stack.text(
        0,
        -0.68,
        (
            "Reading: the workflow removed GPT-5.6-detected NUMBER and OMISSION errors in this "
            "annotated sample; its remaining errors are concentrated in SportSett temporal context "
            "and output-format realization."
        ),
        ha="left",
        va="top",
        fontsize=9.2,
        color="#556070",
        wrap=True,
        transform=ax_stack.transData,
    )

    for suffix in ("png", "svg"):
        output_path = FIGURE_DIR / f"11_gpt56_sol_structured_errors.{suffix}"
        fig.savefig(output_path, dpi=240, bbox_inches="tight")
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
