# SportSett 4934 Stage Ablation

This ablation follows the project plan's core experimental framing:

- compare a direct/single-agent baseline against the full multi-agent system;
- test a small number of stage-level design choices;
- measure factual reliability, task fulfilment, output quality, and runtime.

The fixed example is:

```text
dataset_id: sportsett_basketball
example_id: 4934
task_family: event_report
output_mode: multi_paragraph_report
```

The existing raw baseline and full-system records are reused from:

```text
evaluation/generations/five_dataset_five_each_comparison_20260804_205019_sportsett_basketball_combined_generations.jsonl
```

Only these ablations need to be generated:

```text
no_insight_synthesis
no_writer_quality_revision
no_audit_repair_rounds
```

## Notebook Cell

```python
import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from IPython.display import display

from table2text.evaluation import (
    default_paths,
    generate_reports_for_notebook,
    score_reference_metrics_for_notebook,
    score_deepeval_for_notebook,
)
from table2text.evaluation.datasets import read_examples, write_jsonl

project_dir = Path("/Users/realgobs/Documents/MScproject/table2text_pydanticai")
paths = default_paths(project_dir)

DATASET_ID = "sportsett_basketball"
EXAMPLE_ID = "4934"

RUN_REFERENCE_METRICS = True
RUN_DEEPEVAL = False  # Run after the first smoke pass; this is slower.

experiment_name = (
    f"ablation_sportsett_{EXAMPLE_ID}_"
    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

existing_generations_path = (
    project_dir
    / "evaluation/generations/"
    / "five_dataset_five_each_comparison_20260804_205019_sportsett_basketball_combined_generations.jsonl"
)

ablation_variant_ids = [
    "no_insight_synthesis",
    "no_writer_quality_revision",
    "no_audit_repair_rounds",
]

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)

def read_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def write_generation_records(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

def compact_metric_table(scores):
    if scores.empty:
        return pd.DataFrame()

    return (
        scores[scores["status"].isin(["scored", "error", "skipped", "unavailable"])]
        .pivot_table(
            index=["dataset_id", "example_id", "metric_name"],
            columns="variant_id",
            values="score",
            aggfunc="first",
        )
        .reset_index()
    )

def delta_vs_full(scores):
    table = compact_metric_table(scores)
    if table.empty or "full_system" not in table.columns:
        return table

    lower_is_better = {"ter", "corpus_ter"}
    variant_cols = [
        c for c in table.columns
        if c not in {"dataset_id", "example_id", "metric_name", "full_system"}
    ]

    rows = []
    for _, row in table.iterrows():
        metric_name = row["metric_name"]
        full_score = row.get("full_system")
        if pd.isna(full_score):
            continue

        for variant_id in variant_cols:
            variant_score = row.get(variant_id)
            if pd.isna(variant_score):
                continue

            if metric_name in lower_is_better:
                advantage_over_full = full_score - variant_score
            else:
                advantage_over_full = variant_score - full_score

            rows.append(
                {
                    "dataset_id": row["dataset_id"],
                    "example_id": row["example_id"],
                    "metric_name": metric_name,
                    "variant_id": variant_id,
                    "variant_score": variant_score,
                    "full_system_score": full_score,
                    "advantage_over_full": advantage_over_full,
                }
            )

    return pd.DataFrame(rows)

def summarise_generations(rows):
    frame = pd.DataFrame(rows)
    cols = [
        "dataset_id",
        "example_id",
        "variant_id",
        "error",
        "release_status",
        "writer_mode",
        "repair_rounds_used",
        "audit_support_rate",
        "elapsed_seconds",
    ]
    return frame[[c for c in cols if c in frame.columns]]

# Select the fixed example.
examples = read_examples(paths["prepared_examples"])
example = next(
    e for e in examples
    if e.dataset_id == DATASET_ID and str(e.example_id) == EXAMPLE_ID
)

examples_path = project_dir / f"evaluation/prepared/{experiment_name}.jsonl"
write_jsonl(examples_path, [example])

log(f"Selected {DATASET_ID}/{EXAMPLE_ID}")
log(f"Reference count: {len(example.references)}")

# Reuse existing raw baseline and full-system records.
existing_rows = read_jsonl(existing_generations_path)
baseline_rows = [
    row for row in existing_rows
    if row["dataset_id"] == DATASET_ID
    and str(row["example_id"]) == EXAMPLE_ID
    and row["variant_id"] in {"raw_deepseek_v4_flash", "full_system"}
]

found_baselines = sorted(row["variant_id"] for row in baseline_rows)
log(f"Loaded existing baseline rows: {found_baselines}")

if set(found_baselines) != {"raw_deepseek_v4_flash", "full_system"}:
    raise RuntimeError(f"Missing baseline rows. Found: {found_baselines}")

# Build ablation-only variants.
variants_payload = json.loads(
    (project_dir / "evaluation/config/variants_ablation.json").read_text(encoding="utf-8")
)
ablation_variants = [
    {**variant, "enabled": variant["variant_id"] in ablation_variant_ids}
    for variant in variants_payload["variants"]
    if variant["variant_id"] in ablation_variant_ids
]

variants_path = project_dir / f"evaluation/config/variants_{experiment_name}.json"
write_json(variants_path, {"variants": ablation_variants})

log(f"Ablation variants: {[variant['variant_id'] for variant in ablation_variants]}")

# Generate the missing ablations.
ablation_generations_path = (
    project_dir / f"evaluation/generations/{experiment_name}_ablation_only_generations.jsonl"
)
run_root = project_dir / f"evaluation/generations/{experiment_name}_runs"

start = time.perf_counter()
ablation_frame = await generate_reports_for_notebook(
    project_dir,
    examples_path=examples_path,
    variants_path=variants_path,
    output_path=ablation_generations_path,
    run_root=run_root,
    resume=False,
)
log(f"Finished ablation generation in {time.perf_counter() - start:.1f}s")

display(
    ablation_frame[
        [
            "dataset_id",
            "example_id",
            "variant_id",
            "error",
            "release_status",
            "writer_mode",
            "repair_rounds_used",
            "audit_support_rate",
            "elapsed_seconds",
        ]
    ]
)

# Combine existing raw/full with newly generated ablations.
combined_rows = baseline_rows + ablation_frame.to_dict("records")
combined_generations_path = (
    project_dir / f"evaluation/generations/{experiment_name}_combined_generations.jsonl"
)
write_generation_records(combined_generations_path, combined_rows)

log(f"Combined generations: {combined_generations_path}")

print("\nGENERATION SUMMARY")
display(summarise_generations(combined_rows))

print("\nOUTPUT PREVIEWS")
for row in combined_rows:
    print("\n" + "=" * 100)
    print(row["variant_id"])
    print("-" * 100)
    print((row.get("generated_text") or "")[:2500])

if RUN_REFERENCE_METRICS:
    reference_scores_path = (
        project_dir / f"evaluation/results/{experiment_name}_reference_metrics.jsonl"
    )
    metrics_path = project_dir / "evaluation/config/metrics_ablation_sportsett_4934.json"

    log("Scoring compact reference metrics")
    reference_scores = score_reference_metrics_for_notebook(
        project_dir,
        generations_path=combined_generations_path,
        metric_config_path=metrics_path,
        output_path=reference_scores_path,
        include_ineligible=True,
    )

    print("\nREFERENCE METRICS")
    display(compact_metric_table(reference_scores))

    print("\nDELTA VS FULL SYSTEM")
    display(
        delta_vs_full(reference_scores)
        .sort_values(["metric_name", "advantage_over_full"])
        .reset_index(drop=True)
    )

if RUN_DEEPEVAL:
    deepeval_scores_path = (
        project_dir / f"evaluation/results/{experiment_name}_deepeval_metrics.jsonl"
    )
    metrics_path = project_dir / "evaluation/config/metrics_ablation_sportsett_4934.json"

    log("Scoring DeepEval metrics")
    deepeval_scores = score_deepeval_for_notebook(
        project_dir,
        generations_path=combined_generations_path,
        metric_config_path=metrics_path,
        output_path=deepeval_scores_path,
        resume=False,
    )

    print("\nDEEPEVAL METRICS")
    display(compact_metric_table(deepeval_scores))

    print("\nDEEPEVAL DELTA VS FULL SYSTEM")
    display(
        delta_vs_full(deepeval_scores)
        .sort_values(["metric_name", "advantage_over_full"])
        .reset_index(drop=True)
    )
```

## Reporting Interpretation

Use this ablation to answer a narrow question:

```text
Which stage-level design choices contribute to factual reliability,
task relevance, narrative quality, and runtime on a complex event-report task?
```

Treat the variants as stage ablations:

| Variant | Interpretation |
| --- | --- |
| `raw_deepseek_v4_flash` | Direct single-agent baseline. |
| `full_system` | Complete multi-agent system. |
| `no_insight_synthesis` | Removes bounded insight synthesis and insight verification. |
| `no_writer_quality_revision` | Removes pre-audit writer quality revision. |
| `no_audit_repair_rounds` | Removes post-audit repair rounds while keeping deterministic audit. |

Do not describe these as full individual-agent removals. The current codebase has clean switches for these stages, not for every individual agent.
