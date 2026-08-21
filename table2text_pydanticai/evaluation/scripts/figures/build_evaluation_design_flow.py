"""Build the dissertation evaluation-design flow diagram."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[3]
FIGURE_DIR = PROJECT_DIR / "evaluation/results/figures"


def main() -> None:
    os.environ.setdefault(
        "MPLCONFIGDIR",
        str(PROJECT_DIR / ".matplotlib"),
    )

    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    colors = {
        "ink": "#172033",
        "muted": "#556070",
        "line": "#768195",
        "band": "#F7F8FA",
        "source": "#EAF4FF",
        "source_edge": "#2F6FDB",
        "reference": "#ECFEFF",
        "reference_edge": "#0891B2",
        "workflow": "#E2F3EF",
        "workflow_edge": "#009E73",
        "raw": "#FFF2E8",
        "raw_edge": "#D55E00",
        "outputs": "#F1EDFF",
        "outputs_edge": "#7C3AED",
        "grounded": "#ECFDF5",
        "grounded_edge": "#009E73",
        "judge": "#FDF2F8",
        "judge_edge": "#CC79A7",
        "audit": "#FFFFFF",
        "audit_edge": "#374151",
    }

    fig, ax = plt.subplots(figsize=(15.8, 8.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def stage_label(x: float, text: str) -> None:
        ax.text(
            x,
            0.855,
            text,
            ha="center",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color=colors["muted"],
        )

    def box(
        xy: tuple[float, float],
        width: float,
        height: float,
        text: str,
        *,
        face: str,
        edge: str,
        size: int = 11,
        weight: str = "normal",
        radius: float = 0.015,
    ) -> tuple[float, float, float, float]:
        patch = FancyBboxPatch(
            xy,
            width,
            height,
            boxstyle=f"round,pad=0.012,rounding_size={radius}",
            linewidth=1.8,
            edgecolor=edge,
            facecolor=face,
        )
        ax.add_patch(patch)
        ax.text(
            xy[0] + width / 2,
            xy[1] + height / 2,
            text,
            ha="center",
            va="center",
            fontsize=size,
            fontweight=weight,
            color=colors["ink"],
            linespacing=1.35,
        )
        return (xy[0], xy[1], width, height)

    def right(rect: tuple[float, float, float, float], y_frac: float = 0.5) -> tuple[float, float]:
        return (rect[0] + rect[2], rect[1] + rect[3] * y_frac)

    def left(rect: tuple[float, float, float, float], y_frac: float = 0.5) -> tuple[float, float]:
        return (rect[0], rect[1] + rect[3] * y_frac)

    def top(rect: tuple[float, float, float, float], x_frac: float = 0.5) -> tuple[float, float]:
        return (rect[0] + rect[2] * x_frac, rect[1] + rect[3])

    def bottom(rect: tuple[float, float, float, float], x_frac: float = 0.5) -> tuple[float, float]:
        return (rect[0] + rect[2] * x_frac, rect[1])

    def arrow(
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        connectionstyle: str = "arc3,rad=0",
        lw: float = 1.6,
    ) -> None:
        patch = FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=lw,
            color=colors["line"],
            connectionstyle=connectionstyle,
            shrinkA=6,
            shrinkB=6,
        )
        ax.add_patch(patch)

    def metric_tile(
        xy: tuple[float, float],
        width: float,
        height: float,
        title: str,
        items: str,
        *,
        face: str,
        edge: str,
    ) -> tuple[float, float, float, float]:
        rect = box(xy, width, height, "", face=face, edge=edge)
        ax.text(
            xy[0] + width / 2,
            xy[1] + height * 0.73,
            title,
            ha="center",
            va="center",
            fontsize=8.8,
            fontweight="bold",
            color=colors["ink"],
            linespacing=1.1,
        )
        ax.text(
            xy[0] + width / 2,
            xy[1] + height * 0.30,
            items,
            ha="center",
            va="center",
            fontsize=8.1,
            color=colors["muted"],
            linespacing=1.18,
        )
        return rect

    ax.text(
        0.5,
        0.975,
        "Evaluation Design: Workflow vs Raw Generic Baseline",
        ha="center",
        va="top",
        fontsize=18.5,
        fontweight="bold",
        color=colors["ink"],
    )

    ax.text(
        0.5,
        0.925,
        "Human references are isolated from generation, then reused only for evaluation.",
        ha="center",
        va="top",
        fontsize=10.5,
        color=colors["muted"],
    )

    for x0, width in [(0.04, 0.21), (0.29, 0.32), (0.64, 0.15), (0.82, 0.16)]:
        ax.add_patch(
            Rectangle(
                (x0, 0.12),
                width,
                0.71,
                facecolor=colors["band"],
                edgecolor="#E5E7EB",
                linewidth=1.0,
                zorder=0,
            )
        )

    stage_label(0.145, "Dataset setup")
    stage_label(0.45, "Generation arms")
    stage_label(0.72, "Pairing")
    stage_label(0.895, "Evaluation")

    source = box(
        (0.07, 0.615),
        0.15,
        0.13,
        "25 source\nexamples\n5 datasets x 5 cases",
        face=colors["source"],
        edge=colors["source_edge"],
        size=11.5,
        weight="bold",
    )
    box(
        (0.07, 0.365),
        0.15,
        0.12,
        "Reference\nisolation",
        face=colors["reference"],
        edge=colors["reference_edge"],
        size=11.5,
        weight="bold",
    )
    ax.text(
        0.145,
        0.315,
        "Reference text is withheld from\nboth generation prompts.",
        ha="center",
        va="top",
        fontsize=8.8,
        color=colors["muted"],
        linespacing=1.25,
    )
    arrow((0.145, 0.615), (0.145, 0.485))

    workflow = box(
        (0.31, 0.60),
        0.26,
        0.15,
        "Full multi-agent system\nDeepSeek V4 Flash\nsix-role workflow",
        face=colors["workflow"],
        edge=colors["workflow_edge"],
        size=11,
        weight="bold",
    )
    audit = box(
        (0.34, 0.465),
        0.20,
        0.08,
        "Internal provenance,\nfact support and audit",
        face=colors["audit"],
        edge=colors["audit_edge"],
        size=8.8,
        weight="bold",
        radius=0.012,
    )
    raw = box(
        (0.31, 0.255),
        0.26,
        0.15,
        "Raw generic baseline\nDeepSeek V4 Flash\nsingle LLM call",
        face=colors["raw"],
        edge=colors["raw_edge"],
        size=11,
        weight="bold",
    )
    arrow(right(source, 0.7), left(workflow, 0.55))
    arrow(right(source, 0.3), left(raw, 0.55))
    arrow((0.44, 0.60), top(audit, 0.5), connectionstyle="arc3,rad=0")

    paired = box(
        (0.655, 0.44),
        0.12,
        0.14,
        "50 paired\noutputs",
        face=colors["outputs"],
        edge=colors["outputs_edge"],
        size=12,
        weight="bold",
    )
    arrow(right(workflow), left(paired, 0.72))
    arrow(right(raw), left(paired, 0.28))

    ref_eval = metric_tile(
        (0.835, 0.64),
        0.13,
        0.13,
        "Reference\nalignment",
        "BERTScore\nchrF\nMETEOR",
        face=colors["reference"],
        edge=colors["reference_edge"],
    )
    source_eval = metric_tile(
        (0.835, 0.455),
        0.13,
        0.13,
        "Source-grounded\ndiagnostics",
        "AlignScore\nHHEM",
        face=colors["grounded"],
        edge=colors["grounded_edge"],
    )
    judge_eval = metric_tile(
        (0.835, 0.27),
        0.13,
        0.13,
        "Independent\njudgement",
        "GPT-5.6 Sol\nHuman study",
        face=colors["judge"],
        edge=colors["judge_edge"],
    )
    arrow(right(paired, 0.75), left(ref_eval))
    arrow(right(paired, 0.50), left(source_eval))
    arrow(right(paired, 0.25), left(judge_eval))

    synthesis = box(
        (0.835, 0.13),
        0.13,
        0.085,
        "Synthesis\nsimilarity + grounding\n+ judgement",
        face="#FFFFFF",
        edge=colors["line"],
        size=8.4,
        weight="bold",
    )
    bus_x = 0.975
    metric_centers = [right(ref_eval), right(source_eval), right(judge_eval)]
    for x, y in metric_centers:
        ax.plot([x, bus_x], [y, y], color=colors["line"], lw=1.2)
    ax.plot(
        [bus_x, bus_x],
        [right(ref_eval)[1], top(synthesis)[1] + 0.015],
        color=colors["line"],
        lw=1.2,
    )
    arrow((bus_x, top(synthesis)[1] + 0.015), right(synthesis, 0.72), lw=1.2)

    for suffix in ["png", "svg"]:
        output_path = FIGURE_DIR / f"00_evaluation_design_flow.{suffix}"
        fig.savefig(output_path, dpi=240, bbox_inches="tight")
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
