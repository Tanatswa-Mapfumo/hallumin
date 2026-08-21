# %% [markdown]
# # Task-Aware Direct Baseline Evaluation
#
# This notebook closes the main prompt-asymmetry threat in the 25-example
# evaluation. It compares three conditions on exactly the same stored cases:
#
# 1. `raw_generic_flash`: one DeepSeek V4 Flash call with a generic request;
# 2. `task_aware_direct_flash`: one DeepSeek V4 Flash call with the original
#    task request, task family, expected output form, language, and source;
# 3. `full_system`: the stored multi-agent workflow output.
#
# The notebook does **not** rerun Full or Raw Generic. Generation and judging
# are sharded by example, resumable, and accompanied by timestamped heartbeat
# messages. References are held out during generation.

# %%
import asyncio
import copy
import hashlib
import json
import os
import random
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
from IPython.display import Markdown, display

from table2text.evaluation import (
    annotate_with_openai_judge_for_notebook,
    default_paths,
    generate_reports_for_notebook,
    load_project_env,
    score_reference_metrics_for_notebook,
)
from table2text.evaluation.datasets import read_examples, write_jsonl
from table2text.evaluation.generation import read_generations
from table2text.evaluation_backends import build_single_agent_prompt


# =========================
# User configuration
# =========================

PROJECT_DIR = Path("/Users/realgobs/Documents/MScproject/table2text_pydanticai")
EXPERIMENT_ID = "task_aware_direct_flash_25"

# None runs the canonical 25. Set to 1 or 5 only for a smoke test.
MAX_EXAMPLES = None

DEEPSEEK_MODEL = "deepseek-v4-flash"
MAX_SOURCE_CHARACTERS = 100_000
MAX_OUTPUT_TOKENS = 3_000
TEMPERATURE = 0.2
SEED = 42

RUN_TASK_AWARE_GENERATION = True
RUN_REFERENCE_METRICS = True
RUN_SOURCE_GROUNDED_METRICS = True

# These are opt-in because they consume API budget or create study materials.
RUN_GPT56_STRUCTURED_JUDGE = False
BUILD_BLINDED_HUMAN_PACKETS = False
RUN_STABILITY_EXPERIMENT = False

# When GPT judging is enabled, also fill the canonical 4975/full_system gap.
# The source/output stay unchanged; only the evaluator eligibility skip is
# bypassed, and that intervention is recorded in a sidecar note.
COMPLETE_MISSING_CANONICAL_GPT56 = True

GPT56_MODEL = "gpt-5.6-sol"
GPT56_REASONING_EFFORT = "high"

RESUME_GENERATION = True
RETRY_FAILED_GENERATIONS = True
GENERATION_ATTEMPTS = 2
RESUME_METRICS = True
RETRY_FAILED_JUDGE_ROWS = True

HEARTBEAT_SECONDS = 15
PRINT_GENERATED_OUTPUTS = True
INCLUDE_INELIGIBLE_STORED_OUTPUTS = True

# Optional stability study: one selected case per dataset, three runs/condition.
STABILITY_REPETITIONS = 3
STABILITY_SEEDS = [42, 43, 44]
STABILITY_INCLUDE_FULL_SYSTEM = True


# =========================
# Canonical stored artifacts
# =========================

PATHS = default_paths(PROJECT_DIR)
CANONICAL_GENERATIONS = (
    PROJECT_DIR
    / "evaluation/generations/"
    "five_dataset_five_each_raw_generic_flash_20260805_181001_combined_generations.jsonl"
)
CANONICAL_REFERENCE_CONFIG = (
    PROJECT_DIR
    / "evaluation/config/"
    "metrics_five_dataset_five_each_raw_generic_flash_20260805_181001_reference.json"
)
CANONICAL_SOURCE_CONFIG = (
    PROJECT_DIR
    / "evaluation/config/"
    "metrics_five_dataset_five_each_raw_generic_flash_20260805_181001_source_grounded.json"
)
CANONICAL_SOURCE_METRICS = (
    PROJECT_DIR
    / "evaluation/results/"
    "five_dataset_five_each_raw_generic_flash_20260805_181001_source_grounded_metrics.jsonl"
)
CANONICAL_GPT56_ANNOTATIONS = (
    PROJECT_DIR / "evaluation/results/openai_structured_error_annotations.jsonl"
)

ARTIFACT_DIR = PROJECT_DIR / "evaluation" / "task_aware_direct_baseline"
CONFIG_DIR = ARTIFACT_DIR / "config"
PREPARED_DIR = ARTIFACT_DIR / "prepared"
GENERATION_DIR = ARTIFACT_DIR / "generations"
RESULT_DIR = ARTIFACT_DIR / "results"
JUDGE_DIR = RESULT_DIR / "judge_shards"
TASK_AWARE_JUDGE_DIR = JUDGE_DIR / "task_aware"
CANONICAL_GAP_JUDGE_DIR = JUDGE_DIR / "canonical_gap"
STABILITY_DIR = ARTIFACT_DIR / "stability"

for directory in (
    CONFIG_DIR,
    PREPARED_DIR,
    GENERATION_DIR,
    RESULT_DIR,
    JUDGE_DIR,
    TASK_AWARE_JUDGE_DIR,
    CANONICAL_GAP_JUDGE_DIR,
    STABILITY_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

PROGRESS_LOG = RESULT_DIR / f"{EXPERIMENT_ID}_progress.log"

# %% [markdown]
# ## Progress and persistence helpers
#
# Blocking model and metric calls run in a worker thread. The notebook event
# loop remains free to print a heartbeat every `HEARTBEAT_SECONDS`.

# %%
def log(message):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
    print(line, flush=True)
    with PROGRESS_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def read_jsonl_objects(path):
    path = Path(path)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def safe_name(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value))


def key_for(item):
    return (str(item.dataset_id), str(item.example_id))


def generation_key(item):
    return (str(item.dataset_id), str(item.example_id), str(item.variant_id))


def file_fingerprint(*paths):
    digest = hashlib.sha256()
    for path in paths:
        path = Path(path)
        digest.update(str(path.resolve()).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


async def with_heartbeat(awaitable, label, interval=HEARTBEAT_SECONDS):
    started = time.perf_counter()
    task = asyncio.create_task(awaitable)
    while True:
        try:
            result = await asyncio.wait_for(asyncio.shield(task), timeout=interval)
            log(f"{label}: complete after {time.perf_counter() - started:.1f}s")
            return result
        except asyncio.TimeoutError:
            log(f"{label}: still running ({time.perf_counter() - started:.1f}s elapsed)")


async def run_blocking(func, *args, label, **kwargs):
    return await with_heartbeat(
        asyncio.to_thread(func, *args, **kwargs),
        label,
    )


def run_generation_blocking(
    project_dir,
    *,
    examples_path,
    variants_path,
    output_path,
    run_root,
    resume,
):
    return asyncio.run(
        generate_reports_for_notebook(
            project_dir,
            examples_path=examples_path,
            variants_path=variants_path,
            output_path=output_path,
            run_root=run_root,
            resume=resume,
        )
    )


def load_metric_frame(path):
    rows = read_jsonl_objects(path)
    return pd.DataFrame(rows)


def score_with_cache(
    *,
    generations_path,
    config_path,
    output_path,
    include_ineligible,
):
    fingerprint_path = output_path.with_suffix(output_path.suffix + ".sha256")
    current = file_fingerprint(generations_path, config_path)
    if (
        RESUME_METRICS
        and output_path.exists()
        and fingerprint_path.exists()
        and fingerprint_path.read_text(encoding="utf-8").strip() == current
    ):
        return load_metric_frame(output_path)

    frame = score_reference_metrics_for_notebook(
        PROJECT_DIR,
        generations_path=generations_path,
        metric_config_path=config_path,
        output_path=output_path,
        include_ineligible=include_ineligible,
    )
    fingerprint_path.write_text(current + "\n", encoding="utf-8")
    return frame


log(f"Notebook initialised. Progress log: {PROGRESS_LOG}")

# %% [markdown]
# ## 1. Preflight and exact 25-example selection

# %%
load_project_env(PROJECT_DIR)

required_paths = [
    PATHS["prepared_examples"],
    CANONICAL_GENERATIONS,
    CANONICAL_REFERENCE_CONFIG,
    CANONICAL_SOURCE_CONFIG,
    CANONICAL_SOURCE_METRICS,
]
missing_paths = [path for path in required_paths if not path.exists()]
if missing_paths:
    raise FileNotFoundError(f"Missing required artifacts: {missing_paths}")

if RUN_TASK_AWARE_GENERATION and not os.getenv("DEEPSEEK_API_KEY"):
    raise RuntimeError("DEEPSEEK_API_KEY is not available from the project environment.")

if RUN_GPT56_STRUCTURED_JUDGE and not (
    os.getenv("OPENAI_API_KEY") or os.getenv("T2T_OPENAI_API_KEY")
):
    raise RuntimeError("OPENAI_API_KEY is required when GPT-5.6 judging is enabled.")

canonical_records = read_generations(CANONICAL_GENERATIONS)
full_records = [row for row in canonical_records if row.variant_id == "full_system"]
raw_records = [row for row in canonical_records if row.variant_id == "raw_generic_flash"]

full_keys = {key_for(row) for row in full_records}
raw_keys = {key_for(row) for row in raw_records}
if len(full_records) != 25 or len(raw_records) != 25 or full_keys != raw_keys:
    raise ValueError(
        "The canonical artifact is not the expected paired 25 Full + 25 Raw experiment."
    )

selected_keys = sorted(full_keys)
if MAX_EXAMPLES is not None:
    selected_keys = selected_keys[: int(MAX_EXAMPLES)]

all_examples = read_examples(PATHS["prepared_examples"])
example_by_key = {key_for(example): example for example in all_examples}
missing_examples = [key for key in selected_keys if key not in example_by_key]
if missing_examples:
    raise ValueError(f"Prepared examples are missing canonical identities: {missing_examples}")

selected_examples = [example_by_key[key] for key in selected_keys]
selected_examples_path = PREPARED_DIR / f"{EXPERIMENT_ID}_examples.jsonl"
write_jsonl(selected_examples_path, selected_examples)

selection_frame = pd.DataFrame(
    [
        {
            "dataset_id": example.dataset_id,
            "example_id": example.example_id,
            "task_family": getattr(example.task_family, "value", example.task_family),
            "output_mode": getattr(example.output_mode, "value", example.output_mode),
            "request": example.request,
            "references": len(example.references),
            "source_characters": len(example.source_text),
        }
        for example in selected_examples
    ]
)

log(
    f"Preflight passed: {len(selected_examples)} exactly matched cases across "
    f"{selection_frame['dataset_id'].nunique()} datasets."
)
print("DeepSeek model:", DEEPSEEK_MODEL)
print("DeepSeek key available:", bool(os.getenv("DEEPSEEK_API_KEY")))
print("OpenAI key available:", bool(os.getenv("OPENAI_API_KEY") or os.getenv("T2T_OPENAI_API_KEY")))
display(selection_frame)

# %% [markdown]
# ## 2. Extract the existing same-item AlignScore/HHEM evidence
#
# This stage requires no model call. It extracts Full and Raw Generic values
# for the five researcher-adjudicated examples from the canonical 200-record
# source-grounded metrics artifact.

# %%
FOCUS_CASES = [
    ("sportsett_basketball", "4934"),
    ("totto", "totto-validation-204"),
    ("e2e_nlg", "e2e_nlg-test-51"),
    ("web_nlg", "web_nlg_en-test-51"),
    ("dart", "dart-test-53"),
]

existing_source_scores = load_metric_frame(CANONICAL_SOURCE_METRICS)
focus_mask = existing_source_scores.apply(
    lambda row: (str(row["dataset_id"]), str(row["example_id"])) in FOCUS_CASES,
    axis=1,
)
focus_source_scores = existing_source_scores[
    focus_mask
    & existing_source_scores["variant_id"].isin(["full_system", "raw_generic_flash"])
    & existing_source_scores["status"].eq("scored")
].copy()

focus_source_table = (
    focus_source_scores.pivot_table(
        index=["dataset_id", "example_id", "variant_id"],
        columns="metric_name",
        values="score",
        aggfunc="first",
    )
    .reset_index()
    .rename_axis(columns=None)
)

expected_focus_rows = len(FOCUS_CASES) * 2
if len(focus_source_table) != expected_focus_rows:
    log(
        f"WARNING: expected {expected_focus_rows} same-item source rows after pivot; "
        f"found {len(focus_source_table)}."
    )

focus_source_csv = RESULT_DIR / "selected_five_existing_full_raw_source_metrics.csv"
focus_source_table.to_csv(focus_source_csv, index=False)
log(f"Extracted existing same-item source metrics: {focus_source_csv}")
display(focus_source_table)

# %% [markdown]
# ## 3. Define and inspect the task-aware direct baseline
#
# `raw_baseline_prompt_style="structured"` uses one LLM call and includes the
# original request, task family, output mode, language, and source. It does not
# invoke any workflow agent, evidence ledger, verifier, writer pack, support
# map, auditor, or repair stage.

# %%
TASK_AWARE_VARIANT_ID = "task_aware_direct_flash"
task_aware_variant = {
    "variant_id": TASK_AWARE_VARIANT_ID,
    "enabled": True,
    "backend": "callable",
    "description": (
        "One-call DeepSeek V4 Flash baseline with the original task and output contract."
    ),
    "settings_overrides": {
        "raw_baseline_model": DEEPSEEK_MODEL,
        "raw_baseline_prompt_style": "structured",
        "raw_baseline_max_source_characters": MAX_SOURCE_CHARACTERS,
        "raw_baseline_max_output_tokens": MAX_OUTPUT_TOKENS,
        "raw_baseline_temperature": TEMPERATURE,
    },
    "callable_path": "table2text.evaluation_backends.single_agent_baseline",
    "command": [],
    "precomputed_path": None,
    "repetitions": 1,
    "seeds": [SEED],
}

task_aware_variants_path = CONFIG_DIR / f"variants_{EXPERIMENT_ID}.json"
write_json(task_aware_variants_path, {"variants": [task_aware_variant]})

preview_messages = build_single_agent_prompt(
    selected_examples[0],
    max_source_characters=MAX_SOURCE_CHARACTERS,
    prompt_style="structured",
)
preview_without_source = preview_messages[1]["content"].split("Source data:", 1)[0]
print("SYSTEM PROMPT\n-------------")
print(preview_messages[0]["content"])
print("\nUSER PROMPT CONTRACT PREVIEW\n----------------------------")
print(preview_without_source + "Source data: [supplied in full, references excluded]")

# %% [markdown]
# ## 4. Generate the 25 task-aware direct outputs
#
# Each example has its own generation shard. Rerunning this cell resumes from
# completed shards. Failed calls can be retried without losing successful work.

# %%
task_aware_generations_path = GENERATION_DIR / f"{EXPERIMENT_ID}_generations.jsonl"
task_aware_run_root = GENERATION_DIR / f"{EXPERIMENT_ID}_runs"


def collect_task_aware_shards():
    records = []
    selected_key_set = set(selected_keys)
    for shard in sorted((GENERATION_DIR / "shards").glob("*.jsonl")):
        for record in read_generations(shard):
            if (
                record.variant_id == TASK_AWARE_VARIANT_ID
                and key_for(record) in selected_key_set
            ):
                records.append(record)
    unique = {record.generation_id: record for record in records}
    ordered = sorted(unique.values(), key=lambda row: (row.dataset_id, row.example_id))
    write_jsonl(task_aware_generations_path, ordered)
    return ordered


if RUN_TASK_AWARE_GENERATION:
    (GENERATION_DIR / "shards").mkdir(parents=True, exist_ok=True)
    for index, example in enumerate(selected_examples, start=1):
        identity = f"{example.dataset_id}/{example.example_id}"
        slug = f"{safe_name(example.dataset_id)}__{safe_name(example.example_id)}"
        example_path = PREPARED_DIR / "shards" / f"{slug}.jsonl"
        output_path = GENERATION_DIR / "shards" / f"{slug}.jsonl"
        run_root = task_aware_run_root / slug
        write_jsonl(example_path, [example])

        log("=" * 76)
        log(f"GENERATION {index}/{len(selected_examples)} starting: {identity}")

        if output_path.exists() and RETRY_FAILED_GENERATIONS:
            previous = read_generations(output_path)
            if previous and any(row.error for row in previous):
                log(f"{identity}: removing failed shard before retry")
                output_path.unlink()

        final_row = None
        for attempt in range(1, GENERATION_ATTEMPTS + 1):
            try:
                frame = await run_blocking(
                    run_generation_blocking,
                    PROJECT_DIR,
                    examples_path=example_path,
                    variants_path=task_aware_variants_path,
                    output_path=output_path,
                    run_root=run_root,
                    resume=RESUME_GENERATION,
                    label=f"{identity} generation attempt {attempt}/{GENERATION_ATTEMPTS}",
                )
                if frame.empty:
                    raise RuntimeError("Generation returned no rows.")
                final_row = frame.iloc[-1]
                if not final_row.get("error"):
                    break
                log(f"{identity}: recorded generation error: {final_row.get('error')}")
            except Exception as exc:
                log(f"{identity}: {type(exc).__name__}: {exc}")

            if attempt < GENERATION_ATTEMPTS:
                if output_path.exists():
                    output_path.unlink()
                log(f"{identity}: retrying after 5 seconds")
                await asyncio.sleep(5)

        collect_task_aware_shards()

        if final_row is None:
            log(f"{identity}: no generation row was produced")
            continue

        log(
            f"GENERATION {index}/{len(selected_examples)} finished: {identity}; "
            f"error={final_row.get('error')}; elapsed={final_row.get('elapsed_seconds')}s"
        )
        if PRINT_GENERATED_OUTPUTS:
            generated = str(final_row.get("generated_text") or "").strip()
            display(Markdown(f"### {identity} / task-aware direct\n\n{generated or '*No text*'}"))
else:
    log("Task-aware generation disabled; loading any existing shards.")

task_aware_records = collect_task_aware_shards()
task_aware_summary = pd.DataFrame(
    [
        {
            "dataset_id": row.dataset_id,
            "example_id": row.example_id,
            "variant_id": row.variant_id,
            "error": row.error,
            "elapsed_seconds": row.elapsed_seconds,
            "generated_characters": len(row.generated_text),
        }
        for row in task_aware_records
    ]
)
display(task_aware_summary)

# %% [markdown]
# ## 5. Validate and construct the three-condition paired artifact

# %%
selected_key_set = set(selected_keys)
task_success = [
    row
    for row in task_aware_records
    if key_for(row) in selected_key_set and row.error is None and row.generated_text.strip()
]

task_success_keys = {key_for(row) for row in task_success}
missing_task_aware = sorted(selected_key_set - task_success_keys)
if missing_task_aware:
    raise RuntimeError(
        "Task-aware generation is incomplete. Rerun the generation cell. "
        f"Missing/failed identities: {missing_task_aware}"
    )

canonical_selected = [
    row
    for row in canonical_records
    if key_for(row) in selected_key_set
    and row.variant_id in {"full_system", "raw_generic_flash"}
]
three_condition_records = canonical_selected + task_success
three_condition_records = sorted(
    three_condition_records,
    key=lambda row: (row.dataset_id, row.example_id, row.variant_id),
)

condition_counts = Counter(row.variant_id for row in three_condition_records)
expected_count = len(selected_keys)
for condition in ("full_system", "raw_generic_flash", TASK_AWARE_VARIANT_ID):
    if condition_counts[condition] != expected_count:
        raise ValueError(
            f"Pairing failed for {condition}: expected {expected_count}, "
            f"found {condition_counts[condition]}."
        )

three_condition_generations_path = (
    GENERATION_DIR / f"{EXPERIMENT_ID}_three_condition_generations.jsonl"
)
write_jsonl(three_condition_generations_path, three_condition_records)

pairing_table = pd.DataFrame(
    [
        {
            "dataset_id": row.dataset_id,
            "example_id": row.example_id,
            "variant_id": row.variant_id,
            "error": row.error,
            "eligible": row.primary_evaluation_eligible,
            "writer_mode": row.writer_mode,
            "elapsed_seconds": row.elapsed_seconds,
        }
        for row in three_condition_records
    ]
)

log(f"Three-condition artifact validated: {condition_counts}")
log(f"Saved: {three_condition_generations_path}")
display(pairing_table)

# %% [markdown]
# ## 6. Build matching reference and source-grounded metric configurations
#
# The focused reference set is BLEU, chrF, TER, ROUGE-L, METEOR and BERTScore
# F1. AlignScore and all three HHEM diagnostics are computed separately against
# the structured source, not against the references.

# %%
reference_config = json.loads(CANONICAL_REFERENCE_CONFIG.read_text(encoding="utf-8"))
reference_config["experiment_id"] = EXPERIMENT_ID
reference_config["prepared_examples_path"] = str(selected_examples_path)
reference_config["generations_path"] = str(three_condition_generations_path)
reference_config["result_directory"] = str(RESULT_DIR)
reference_config["baseline_variant"] = TASK_AWARE_VARIANT_ID
reference_config["reference_metrics"]["enabled_metrics"] = [
    "bleu",
    "chrf",
    "ter",
    "rougeL",
    "meteor",
    "bertscore",
]
reference_config["deepeval"]["enabled"] = False

source_config = json.loads(CANONICAL_SOURCE_CONFIG.read_text(encoding="utf-8"))
source_config["experiment_id"] = f"{EXPERIMENT_ID}_source_grounded"
source_config["prepared_examples_path"] = str(selected_examples_path)
source_config["generations_path"] = str(three_condition_generations_path)
source_config["result_directory"] = str(RESULT_DIR)
source_config["baseline_variant"] = TASK_AWARE_VARIANT_ID
source_config["reference_metrics"]["enabled_metrics"] = ["hhem", "alignscore"]
source_config["reference_metrics"]["external_factuality_context"] = "source_text"
source_config["deepeval"]["enabled"] = False

reference_config_path = CONFIG_DIR / f"metrics_{EXPERIMENT_ID}_reference.json"
source_config_path = CONFIG_DIR / f"metrics_{EXPERIMENT_ID}_source_grounded.json"
write_json(reference_config_path, reference_config)
write_json(source_config_path, source_config)

print("Reference metrics:", reference_config["reference_metrics"]["enabled_metrics"])
print("Source metrics:", source_config["reference_metrics"]["enabled_metrics"])
print("Stored ineligible outputs included:", INCLUDE_INELIGIBLE_STORED_OUTPUTS)

# %% [markdown]
# ## 7. Score reference similarity

# %%
reference_metrics_path = RESULT_DIR / f"{EXPERIMENT_ID}_reference_metrics.jsonl"

if RUN_REFERENCE_METRICS:
    log("Starting reference metrics for all three paired conditions")
    reference_scores = await run_blocking(
        score_with_cache,
        generations_path=three_condition_generations_path,
        config_path=reference_config_path,
        output_path=reference_metrics_path,
        include_ineligible=INCLUDE_INELIGIBLE_STORED_OUTPUTS,
        label="Reference metrics",
    )
else:
    reference_scores = load_metric_frame(reference_metrics_path)

if reference_scores.empty:
    log("No reference metric rows are available.")
else:
    log(f"Reference metric rows: {len(reference_scores)}")
    display(
        reference_scores.groupby(["metric_name", "status"], dropna=False)
        .size()
        .rename("rows")
        .reset_index()
    )

# %% [markdown]
# ## 8. Score source-grounded AlignScore and HHEM

# %%
source_metrics_path = RESULT_DIR / f"{EXPERIMENT_ID}_source_grounded_metrics.jsonl"

if RUN_SOURCE_GROUNDED_METRICS:
    log("Starting source-grounded AlignScore/HHEM for all three paired conditions")
    source_scores = await run_blocking(
        score_with_cache,
        generations_path=three_condition_generations_path,
        config_path=source_config_path,
        output_path=source_metrics_path,
        include_ineligible=INCLUDE_INELIGIBLE_STORED_OUTPUTS,
        label="Source-grounded metrics",
    )
else:
    source_scores = load_metric_frame(source_metrics_path)

if source_scores.empty:
    log("No source-grounded metric rows are available.")
else:
    log(f"Source-grounded metric rows: {len(source_scores)}")
    display(
        source_scores.groupby(["metric_name", "status"], dropna=False)
        .size()
        .rename("rows")
        .reset_index()
    )

# %% [markdown]
# ## 9. Three-condition comparison tables

# %%
def scored_only(frame):
    if frame.empty:
        return frame.copy()
    return frame[frame["status"].eq("scored") & frame["score"].notna()].copy()


def macro_table(frame):
    scored = scored_only(frame)
    if scored.empty:
        return pd.DataFrame()
    return (
        scored.groupby(["variant_id", "metric_name"], as_index=False)["score"]
        .mean()
        .pivot(index="metric_name", columns="variant_id", values="score")
        .reset_index()
        .rename_axis(columns=None)
    )


def dataset_table(frame):
    scored = scored_only(frame)
    if scored.empty:
        return pd.DataFrame()
    return (
        scored.groupby(["dataset_id", "variant_id", "metric_name"], as_index=False)["score"]
        .mean()
        .pivot(
            index=["dataset_id", "metric_name"],
            columns="variant_id",
            values="score",
        )
        .reset_index()
        .rename_axis(columns=None)
    )


reference_macro = macro_table(reference_scores)
source_macro = macro_table(source_scores)
reference_by_dataset = dataset_table(reference_scores)
source_by_dataset = dataset_table(source_scores)

print("REFERENCE METRICS — MACRO MEANS")
display(reference_macro)
print("REFERENCE METRICS — BY DATASET")
display(reference_by_dataset)
print("SOURCE-GROUNDED METRICS — MACRO MEANS")
display(source_macro)
print("SOURCE-GROUNDED METRICS — BY DATASET")
display(source_by_dataset)

reference_macro.to_csv(RESULT_DIR / f"{EXPERIMENT_ID}_reference_macro.csv", index=False)
source_macro.to_csv(RESULT_DIR / f"{EXPERIMENT_ID}_source_macro.csv", index=False)
reference_by_dataset.to_csv(
    RESULT_DIR / f"{EXPERIMENT_ID}_reference_by_dataset.csv", index=False
)
source_by_dataset.to_csv(
    RESULT_DIR / f"{EXPERIMENT_ID}_source_by_dataset.csv", index=False
)

# %%
# Direction-adjusted same-item wins. TER and unsupported-sentence rate are lower-is-better.
all_scores = pd.concat(
    [
        scored_only(reference_scores).assign(evaluation_family="reference"),
        scored_only(source_scores).assign(evaluation_family="source"),
    ],
    ignore_index=True,
)

if not all_scores.empty:
    all_scores["quality_score"] = all_scores.apply(
        lambda row: row["score"] if bool(row["higher_is_better"]) else -row["score"],
        axis=1,
    )
    paired = all_scores.pivot_table(
        index=["evaluation_family", "dataset_id", "example_id", "metric_name"],
        columns="variant_id",
        values="quality_score",
        aggfunc="first",
    ).reset_index()

    comparisons = []
    for left, right, label in [
        ("full_system", TASK_AWARE_VARIANT_ID, "Full vs Task-aware Direct"),
        (TASK_AWARE_VARIANT_ID, "raw_generic_flash", "Task-aware Direct vs Raw Generic"),
        ("full_system", "raw_generic_flash", "Full vs Raw Generic"),
    ]:
        available = paired.dropna(subset=[left, right]).copy()
        delta = available[left] - available[right]
        comparisons.append(
            {
                "comparison": label,
                "paired_metric_cases": len(available),
                "left_wins": int((delta > 1e-12).sum()),
                "ties": int(delta.abs().le(1e-12).sum()),
                "right_wins": int((delta < -1e-12).sum()),
            }
        )
    win_table = pd.DataFrame(comparisons)
    display(win_table)
    win_table.to_csv(RESULT_DIR / f"{EXPERIMENT_ID}_direction_adjusted_wins.csv", index=False)

    if not source_scores.empty:
        selected_three_source = source_scores[
            source_scores.apply(
                lambda row: (str(row["dataset_id"]), str(row["example_id"])) in FOCUS_CASES,
                axis=1,
            )
            & source_scores["status"].eq("scored")
        ].pivot_table(
            index=["dataset_id", "example_id", "variant_id"],
            columns="metric_name",
            values="score",
            aggfunc="first",
        ).reset_index().rename_axis(columns=None)
        selected_three_source.to_csv(
            RESULT_DIR / "selected_five_three_condition_source_metrics.csv", index=False
        )
        print("SELECTED FIVE — ALL THREE CONDITIONS — SOURCE METRICS")
        display(selected_three_source)

# %% [markdown]
# ## 10. Optional GPT-5.6 Sol structured error annotations
#
# This sends only the 25 new task-aware outputs. It supplies source + task + one
# output, excludes references/metrics/system identity, and saves one shard per
# case. Enable `RUN_GPT56_STRUCTURED_JUDGE` in the configuration cell only when
# API credit is available.

# %%
task_aware_judge_path = RESULT_DIR / f"{EXPERIMENT_ID}_gpt56_annotations.jsonl"
canonical_gap_judge_path = RESULT_DIR / "canonical_missing_gpt56_annotations.jsonl"


def collect_judge_shards(shard_directory, combined_path):
    rows = []
    for shard in sorted(Path(shard_directory).glob("*.jsonl")):
        rows.extend(read_jsonl_objects(shard))
    unique = {
        (row["generation_id"], row["judge_model"], row["judge_repetition"]): row
        for row in rows
    }
    ordered = sorted(
        unique.values(),
        key=lambda row: (row["dataset_id"], row["example_id"], row["variant_id"]),
    )
    write_jsonl(combined_path, ordered)
    return ordered


if RUN_GPT56_STRUCTURED_JUDGE:
    for index, record in enumerate(task_success, start=1):
        identity = f"{record.dataset_id}/{record.example_id}"
        slug = f"{safe_name(record.dataset_id)}__{safe_name(record.example_id)}"
        judge_input = PREPARED_DIR / "judge_inputs" / f"{slug}.jsonl"
        judge_output = TASK_AWARE_JUDGE_DIR / f"{slug}.jsonl"
        write_jsonl(judge_input, [record])

        if judge_output.exists() and RETRY_FAILED_JUDGE_ROWS:
            prior = read_jsonl_objects(judge_output)
            if prior and any(row.get("status") == "error" for row in prior):
                log(f"{identity}: removing failed GPT judge shard before retry")
                judge_output.unlink()

        log(f"GPT-5.6 JUDGE {index}/{len(task_success)} starting: {identity}")
        try:
            frame = await run_blocking(
                annotate_with_openai_judge_for_notebook,
                PROJECT_DIR,
                generations_path=judge_input,
                output_path=judge_output,
                judge_model=GPT56_MODEL,
                judge_repetitions=1,
                reasoning_effort=GPT56_REASONING_EFFORT,
                max_source_characters=50_000,
                max_output_tokens=2_500,
                include_references=False,
                include_system_identity=False,
                include_metric_scores=False,
                resume=True,
                label=f"GPT-5.6 judge {identity}",
            )
            if frame.empty:
                log(f"GPT-5.6 JUDGE {identity}: no row returned")
            else:
                row = frame.iloc[-1]
                log(
                    f"GPT-5.6 JUDGE {identity}: status={row.get('status')}; "
                    f"errors={row.get('error_count')}; api_error={row.get('error')}"
                )
        except Exception as exc:
            log(f"GPT-5.6 JUDGE {identity}: {type(exc).__name__}: {exc}")
        collect_judge_shards(TASK_AWARE_JUDGE_DIR, task_aware_judge_path)
else:
    log("GPT-5.6 structured judging disabled.")

task_aware_judge_rows = collect_judge_shards(
    TASK_AWARE_JUDGE_DIR,
    task_aware_judge_path,
)

canonical_judge_rows = read_jsonl_objects(CANONICAL_GPT56_ANNOTATIONS)
canonical_judged_ids = {row["generation_id"] for row in canonical_judge_rows}
missing_canonical_full = [
    row
    for row in full_records
    if key_for(row) in selected_key_set
    and row.generation_id not in canonical_judged_ids
]

if RUN_GPT56_STRUCTURED_JUDGE and COMPLETE_MISSING_CANONICAL_GPT56:
    if missing_canonical_full:
        log(
            "Canonical GPT-5.6 gap detected: "
            + ", ".join(row.generation_id for row in missing_canonical_full)
        )
    for index, original_record in enumerate(missing_canonical_full, start=1):
        # The original generation remains untouched. This evaluation-only copy
        # bypasses the annotation runner's eligibility filter.
        judge_record = original_record.model_copy(
            update={"primary_evaluation_eligible": True}
        )
        identity = f"{judge_record.dataset_id}/{judge_record.example_id}/full_system"
        slug = f"{safe_name(judge_record.dataset_id)}__{safe_name(judge_record.example_id)}"
        judge_input = PREPARED_DIR / "judge_inputs" / f"canonical_gap__{slug}.jsonl"
        judge_output = CANONICAL_GAP_JUDGE_DIR / f"{slug}.jsonl"
        write_jsonl(judge_input, [judge_record])

        if judge_output.exists() and RETRY_FAILED_JUDGE_ROWS:
            prior = read_jsonl_objects(judge_output)
            if prior and any(row.get("status") == "error" for row in prior):
                judge_output.unlink()

        log(
            f"GPT-5.6 CANONICAL GAP {index}/{len(missing_canonical_full)} "
            f"starting: {identity}"
        )
        try:
            frame = await run_blocking(
                annotate_with_openai_judge_for_notebook,
                PROJECT_DIR,
                generations_path=judge_input,
                output_path=judge_output,
                judge_model=GPT56_MODEL,
                judge_repetitions=1,
                reasoning_effort=GPT56_REASONING_EFFORT,
                max_source_characters=50_000,
                max_output_tokens=2_500,
                include_references=False,
                include_system_identity=False,
                include_metric_scores=False,
                resume=True,
                label=f"GPT-5.6 canonical gap {identity}",
            )
            if frame.empty:
                log(f"GPT-5.6 CANONICAL GAP {identity}: no row returned")
            else:
                row = frame.iloc[-1]
                log(
                    f"GPT-5.6 CANONICAL GAP {identity}: status={row.get('status')}; "
                    f"errors={row.get('error_count')}; api_error={row.get('error')}"
                )
        except Exception as exc:
            log(f"GPT-5.6 CANONICAL GAP {identity}: {type(exc).__name__}: {exc}")

    write_json(
        RESULT_DIR / "canonical_gpt56_gap_provenance.json",
        {
            "reason": (
                "The canonical annotation runner skipped generation records marked "
                "primary_evaluation_eligible=false. The unchanged source and output "
                "were judged through an evaluation-only copy with that gate enabled."
            ),
            "generation_ids": [row.generation_id for row in missing_canonical_full],
        },
    )

canonical_gap_judge_rows = collect_judge_shards(
    CANONICAL_GAP_JUDGE_DIR,
    canonical_gap_judge_path,
)

if task_aware_judge_rows:
    judge_frame = pd.DataFrame(task_aware_judge_rows)
    display(
        judge_frame.groupby(["variant_id", "status"], dropna=False)
        .agg(outputs=("generation_id", "count"), errors=("error_count", "sum"))
        .reset_index()
    )

    combined_judge_path = RESULT_DIR / f"{EXPERIMENT_ID}_three_condition_gpt56_annotations.jsonl"
    combined_judge_rows = canonical_judge_rows + canonical_gap_judge_rows + task_aware_judge_rows
    combined_judge_rows = list(
        {
            (row["generation_id"], row["judge_model"], row["judge_repetition"]): row
            for row in combined_judge_rows
        }.values()
    )
    write_jsonl(combined_judge_path, combined_judge_rows)
    log(f"Combined canonical + task-aware GPT annotations: {combined_judge_path}")

# %% [markdown]
# ## 11. Optional blinded independent-adjudication packets
#
# This only prepares materials. Do not recruit or collect new participant data
# unless the work is covered by ethics approval or explicitly cleared by the
# supervisor. System order is randomised and the mapping is stored separately.

# %%
if BUILD_BLINDED_HUMAN_PACKETS:
    record_by_identity = {
        generation_key(row): row
        for row in three_condition_records
    }
    example_lookup = {key_for(example): example for example in selected_examples}

    for comparison_name, condition_pair in {
        "full_vs_raw_generic": ("full_system", "raw_generic_flash"),
        "full_vs_task_aware": ("full_system", TASK_AWARE_VARIANT_ID),
    }.items():
        packet_rows = []
        private_rows = []
        rng = random.Random(SEED)
        for pair_index, case in enumerate(FOCUS_CASES, start=1):
            if case not in selected_key_set:
                continue
            example = example_lookup[case]
            candidates = list(condition_pair)
            rng.shuffle(candidates)
            output_a = record_by_identity[(case[0], case[1], candidates[0])]
            output_b = record_by_identity[(case[0], case[1], candidates[1])]
            pair_id = f"PAIR_{pair_index:02d}"
            packet_rows.append(
                {
                    "pair_id": pair_id,
                    "dataset_id": case[0],
                    "example_id": case[1],
                    "task_request": example.request,
                    "task_family": getattr(example.task_family, "value", example.task_family),
                    "output_mode": getattr(example.output_mode, "value", example.output_mode),
                    "source_text": example.source_text,
                    "output_a": output_a.generated_text,
                    "output_b": output_b.generated_text,
                    "preferred_output_a_b_or_tie": "",
                    "output_a_error_notes": "",
                    "output_b_error_notes": "",
                }
            )
            private_rows.append(
                {
                    "pair_id": pair_id,
                    "output_a_variant": candidates[0],
                    "output_b_variant": candidates[1],
                }
            )

        packet_path = RESULT_DIR / f"blind_packet_{comparison_name}.csv"
        key_path = RESULT_DIR / f"PRIVATE_blind_key_{comparison_name}.json"
        pd.DataFrame(packet_rows).to_csv(packet_path, index=False)
        write_json(key_path, private_rows)
        log(f"Blinded packet: {packet_path}")
        log(f"PRIVATE mapping: {key_path}")
else:
    log("Blinded human packet generation disabled.")

# %% [markdown]
# ## 12. Optional small repeated-generation stability experiment
#
# This is diagnostic, not part of the main 25-case result. It uses one selected
# example per dataset and three seeds. Because it uses the current code and
# current hosted model aliases, report it as a later stability check rather
# than silently merging it with the historical main experiment.

# %%
if RUN_STABILITY_EXPERIMENT:
    stability_cases = [case for case in FOCUS_CASES if case in selected_key_set]
    stability_examples = [example_by_key[case] for case in stability_cases]
    stability_records = []

    stability_variants = [
        {
            **task_aware_variant,
            "variant_id": "stability_task_aware_direct_flash",
        }
    ]
    if STABILITY_INCLUDE_FULL_SYSTEM:
        stability_variants.append(
            {
                "variant_id": "stability_full_system",
                "enabled": True,
                "backend": "table2text",
                "description": "Current Full workflow used only for the stability diagnostic.",
                "settings_overrides": {},
                "callable_path": None,
                "command": [],
                "precomputed_path": None,
                "repetitions": 1,
                "seeds": [SEED],
            }
        )

    total_calls = len(stability_examples) * len(stability_variants) * STABILITY_REPETITIONS
    call_number = 0
    for example in stability_examples:
        for base_variant in stability_variants:
            for repetition_index in range(STABILITY_REPETITIONS):
                call_number += 1
                seed_subset = STABILITY_SEEDS[: repetition_index + 1]
                variant = {
                    **base_variant,
                    "repetitions": repetition_index + 1,
                    "seeds": seed_subset,
                }
                identity = (
                    f"{example.dataset_id}/{example.example_id}/"
                    f"{variant['variant_id']}/seed={seed_subset[-1]}"
                )
                slug = (
                    f"{safe_name(example.dataset_id)}__{safe_name(example.example_id)}__"
                    f"{safe_name(variant['variant_id'])}"
                )
                example_path = STABILITY_DIR / "prepared" / f"{slug}.jsonl"
                variant_path = STABILITY_DIR / "config" / f"{slug}.json"
                output_path = STABILITY_DIR / "generations" / f"{slug}.jsonl"
                run_root = STABILITY_DIR / "runs" / slug
                write_jsonl(example_path, [example])
                write_json(variant_path, {"variants": [variant]})
                log(f"STABILITY {call_number}/{total_calls}: {identity}")
                await run_blocking(
                    run_generation_blocking,
                    PROJECT_DIR,
                    examples_path=example_path,
                    variants_path=variant_path,
                    output_path=output_path,
                    run_root=run_root,
                    resume=True,
                    label=f"Stability {identity}",
                )

    for path in sorted((STABILITY_DIR / "generations").glob("*.jsonl")):
        stability_records.extend(read_generations(path))
    stability_records = list(
        {record.generation_id: record for record in stability_records}.values()
    )
    stability_generations_path = STABILITY_DIR / "stability_generations.jsonl"
    write_jsonl(stability_generations_path, stability_records)
    log(f"Stability generations saved: {stability_generations_path}")
    display(
        pd.DataFrame(
            [
                {
                    "dataset_id": row.dataset_id,
                    "example_id": row.example_id,
                    "variant_id": row.variant_id,
                    "seed": row.seed,
                    "error": row.error,
                    "elapsed_seconds": row.elapsed_seconds,
                }
                for row in stability_records
            ]
        )
    )
else:
    log("Repeated-generation stability experiment disabled.")

# %% [markdown]
# ## 13. Final artifact manifest

# %%
manifest = {
    "experiment_id": EXPERIMENT_ID,
    "created_or_updated_at": datetime.now().isoformat(),
    "model": DEEPSEEK_MODEL,
    "task_aware_prompt_style": "structured",
    "seed": SEED,
    "temperature": TEMPERATURE,
    "selected_examples": len(selected_keys),
    "condition_counts": dict(condition_counts),
    "include_ineligible_stored_outputs": INCLUDE_INELIGIBLE_STORED_OUTPUTS,
    "canonical_generations": str(CANONICAL_GENERATIONS),
    "selected_examples_path": str(selected_examples_path),
    "task_aware_generations": str(task_aware_generations_path),
    "three_condition_generations": str(three_condition_generations_path),
    "reference_metrics": str(reference_metrics_path),
    "source_grounded_metrics": str(source_metrics_path),
    "existing_selected_five_source_metrics": str(focus_source_csv),
    "task_aware_gpt56_annotations": str(task_aware_judge_path),
    "canonical_gap_gpt56_annotations": str(canonical_gap_judge_path),
    "progress_log": str(PROGRESS_LOG),
}
manifest_path = RESULT_DIR / f"{EXPERIMENT_ID}_manifest.json"
write_json(manifest_path, manifest)

log("Evaluation notebook complete.")
print(json.dumps(manifest, indent=2))
