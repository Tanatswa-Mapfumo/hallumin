# %% [markdown]
# # Protected 25-Example Full-System Evaluation
#
# This notebook creates and runs a frozen, previously unused holdout batch:
#
# - five examples from each of E2E, WebNLG, DART, ToTTo, and SportSett;
# - one Full-System generation per example;
# - DeepSeek V4 Flash for all six workflow roles;
# - exact task contracts from the prepared benchmark records;
# - held-out references physically replaced by a sentinel during generation;
# - per-example checkpoints, heartbeat logging, and resumable execution;
# - exact source/config/code hashes and complete workflow-artifact indexes;
# - sentence support, evidence/fact/insight, retry, audit, and token summaries.
#
# The selection is written once and never silently recomputed. The notebook
# also verifies the frozen implementation fingerprint before every generation.
# Reference-based scoring is a separate, disabled-by-default final phase that
# cannot run until all 25 generations have completed successfully.

# %%
import ast
import asyncio
import copy
import hashlib
import importlib.metadata
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from IPython.display import Markdown, display

from table2text.config import Settings
from table2text.evaluation import (
    default_paths,
    generate_reports_for_notebook,
    load_project_env,
    score_reference_metrics_for_notebook,
)
from table2text.evaluation.datasets import read_examples
from table2text.evaluation.generation import (
    materialise_input,
    read_generations,
)


# =========================
# User configuration
# =========================

PROJECT_DIR = Path("/Users/realgobs/Documents/MScproject/table2text_pydanticai")
EXPERIMENT_ID = "protected_holdout_full_system_flash_25"

DATASETS = [
    "e2e_nlg",
    "web_nlg",
    "dart",
    "totto",
    "sportsett_basketball",
]
EXAMPLES_PER_DATASET = 5
SELECTION_SEED = 20260820
GENERATION_SEED = 42
MODEL = "deepseek:deepseek-v4-flash"

# Leave as None to run all unfinished examples. Set to 5, for example, to
# process one interleaved block and resume later without changing selection.
MAX_CASES_THIS_SESSION = None

HEARTBEAT_SECONDS = 20
MAX_TOP_LEVEL_ATTEMPTS_PER_EXAMPLE = 2
CONTINUE_AFTER_FAILURE = True
PRINT_FINAL_OUTPUTS = True

# These declarations are copied into the protected-set manifest. Keep them
# True only if they are factually correct at the moment this notebook is run.
RESEARCHER_CONFIRMS_NO_PRIOR_MANUAL_INSPECTION = True
RESEARCHER_CONFIRMS_NO_DEVELOPMENT_CHANGES_AFTER_SELECTION = True

# References are unsealed only after all 25 generations succeed. These metric
# phases are deliberately opt-in and do not alter any workflow output.
RUN_POST_GENERATION_REFERENCE_METRICS = False
RUN_POST_GENERATION_SOURCE_METRICS = False


# =========================
# Paths
# =========================

PATHS = default_paths(PROJECT_DIR)
ARTIFACT_DIR = PROJECT_DIR / "evaluation" / "protected_holdout_full_system"
CONFIG_DIR = ARTIFACT_DIR / "config"
PREPARED_DIR = ARTIFACT_DIR / "prepared"
GENERATION_DIR = ARTIFACT_DIR / "generations"
SHARD_DIR = GENERATION_DIR / "shards"
ATTEMPT_RECORD_DIR = GENERATION_DIR / "attempt_records"
RUN_ROOT = GENERATION_DIR / "runs"
RESULT_DIR = ARTIFACT_DIR / "results"
SNAPSHOT_DIR = ARTIFACT_DIR / "frozen_code_snapshot"
MODEL_INPUT_AUDIT_DIR = ARTIFACT_DIR / "model_input_audit"

for directory in (
    CONFIG_DIR,
    PREPARED_DIR,
    GENERATION_DIR,
    SHARD_DIR,
    ATTEMPT_RECORD_DIR,
    RUN_ROOT,
    RESULT_DIR,
    SNAPSHOT_DIR,
    MODEL_INPUT_AUDIT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

VARIANT_PATH = CONFIG_DIR / "protected_full_system_flash.json"
FREEZE_MANIFEST_PATH = SNAPSHOT_DIR / "freeze_manifest.json"
SELECTION_MANIFEST_PATH = PREPARED_DIR / "protected_selection_manifest.json"
OPERATIONAL_EXAMPLES_PATH = PREPARED_DIR / "protected_operational_examples.jsonl"
EXCLUSION_MANIFEST_PATH = PREPARED_DIR / "historical_exclusions.json"
BATCH_MANIFEST_PATH = RESULT_DIR / "protected_batch_manifest.json"
PROGRESS_LOG_PATH = RESULT_DIR / "protected_progress.log"
ATTEMPT_LOG_PATH = RESULT_DIR / "generation_attempts.jsonl"
SEALED_GENERATIONS_PATH = GENERATION_DIR / "protected_full_system_generations_sealed.jsonl"
UNSEALED_GENERATIONS_PATH = GENERATION_DIR / "protected_full_system_generations_post_generation.jsonl"
SUMMARY_JSONL_PATH = RESULT_DIR / "protected_generation_summary.jsonl"
SUMMARY_CSV_PATH = RESULT_DIR / "protected_generation_summary.csv"
STAGE_USAGE_CSV_PATH = RESULT_DIR / "stage_token_usage.csv"
SUPPORT_MAP_JSONL_PATH = RESULT_DIR / "sentence_support_mappings.jsonl"
ARTIFACT_INDEX_PATH = RESULT_DIR / "run_artifact_indexes.jsonl"
EXECUTION_REPORT_PATH = RESULT_DIR / "PROTECTED_HOLDOUT_EXECUTION_REPORT.md"


# %% [markdown]
# ## Helpers
#
# Progress messages are written both to the cell output and to a persistent
# log. Atomic JSON writes prevent an interrupted kernel from leaving a partial
# manifest. Long generations emit a heartbeat every 20 seconds.

# %%
def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
    print(line, flush=True)
    with PROGRESS_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def json_default(value):
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "value"):
        return value.value
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def write_json_atomic(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=json_default,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def write_jsonl_atomic(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for record in records:
            if hasattr(record, "model_dump"):
                record = record.model_dump(mode="json")
            handle.write(
                json.dumps(record, ensure_ascii=False, default=json_default)
                + "\n"
            )
    temporary.replace(path)


def append_jsonl(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(record, ensure_ascii=False, default=json_default) + "\n"
        )


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl_objects(path):
    path = Path(path)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def canonical_sha256(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=json_default,
    )
    return sha256_bytes(payload.encode("utf-8"))


def safe_name(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value))


def relative_path(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(PROJECT_DIR.resolve()))
    except ValueError:
        return str(path)


def git_output(*arguments):
    completed = subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_DIR,
        check=False,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


async def with_heartbeat(awaitable, label, interval=HEARTBEAT_SECONDS):
    started = time.perf_counter()
    task = asyncio.create_task(awaitable)
    while True:
        try:
            result = await asyncio.wait_for(asyncio.shield(task), timeout=interval)
            elapsed = time.perf_counter() - started
            log(f"{label}: completed after {elapsed:.1f}s")
            return result
        except asyncio.TimeoutError:
            elapsed = time.perf_counter() - started
            log(f"{label}: still running ({elapsed:.1f}s elapsed)")


def markdown_word_count(text):
    without_markup = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    without_markup = re.sub(r"^#{1,6}\s+", "", without_markup, flags=re.MULTILINE)
    return len(re.findall(r"\b[\w'-]+\b", without_markup, flags=re.UNICODE))


def prose_sentence_count(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "<!--"))
    ]
    prose = " ".join(lines)
    return len(
        [part for part in re.split(r"(?<=[.!?])\s+", prose) if part.strip()]
    )


def nested_list(payload, *path):
    current = payload
    for key in path:
        if not isinstance(current, dict):
            return []
        current = current.get(key)
    return current if isinstance(current, list) else []


load_project_env(PROJECT_DIR)
log(f"Project: {PROJECT_DIR}")
log(f"Experiment: {EXPERIMENT_ID}")


# %% [markdown]
# ## 1. Freeze the Full-System configuration and implementation
#
# All environment-derived workflow settings are resolved once. The six model
# roles are then fixed to DeepSeek V4 Flash, and the complete settings payload
# is stored in the protected variant. A source-tree snapshot is used even if
# the Git worktree is dirty; the commit and dirty status are both disclosed.
# Every later run must match this fingerprint exactly.

# %%
MODEL_FIELDS = [
    "data_understanding_model",
    "orchestrator_model",
    "evidence_model",
    "verifier_model",
    "writer_model",
    "auditor_model",
]


def build_frozen_variant():
    resolved = asdict(Settings.from_env())
    resolved["use_llm"] = True
    for field_name in MODEL_FIELDS:
        resolved[field_name] = MODEL

    # These two are supplied per generation by the evaluation runner.
    resolved.pop("output_dir", None)
    resolved.pop("random_seed", None)

    return {
        "variants": [
            {
                "variant_id": "full_system",
                "enabled": True,
                "backend": "table2text",
                "description": (
                    "Frozen protected-holdout Full-System run with all six "
                    "roles on DeepSeek V4 Flash."
                ),
                "settings_overrides": resolved,
                "task_contract_mode": "explicit",
                "request_override": None,
                "callable_path": None,
                "command": [],
                "precomputed_path": None,
                "repetitions": 1,
                "seeds": [GENERATION_SEED],
            }
        ]
    }


if not VARIANT_PATH.exists():
    write_json_atomic(VARIANT_PATH, build_frozen_variant())
    log(f"Created frozen variant: {VARIANT_PATH}")
else:
    log(f"Reusing existing frozen variant: {VARIANT_PATH}")

frozen_variant_payload = read_json(VARIANT_PATH)
frozen_variant = frozen_variant_payload["variants"][0]
frozen_overrides = frozen_variant["settings_overrides"]

assert frozen_variant["variant_id"] == "full_system"
assert frozen_variant["task_contract_mode"] == "explicit"
assert frozen_variant["repetitions"] == 1
assert frozen_variant["seeds"] == [GENERATION_SEED]
assert all(frozen_overrides[field] == MODEL for field in MODEL_FIELDS)
assert frozen_overrides["use_llm"] is True


def implementation_files():
    files = sorted((PROJECT_DIR / "src" / "table2text").rglob("*.py"))
    files.extend(
        path
        for path in [
            PROJECT_DIR / "pyproject.toml",
            PROJECT_DIR / "evaluation" / "config" / "datasets.json",
            PROJECT_DIR
            / "evaluation"
            / "notebooks"
            / "protected_holdout_full_system_evaluation.py",
        ]
        if path.exists()
    )
    return sorted(set(path.resolve() for path in files))


def file_manifest(files):
    return [
        {
            "path": relative_path(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in files
    ]


def implementation_fingerprint(files=None):
    manifest = file_manifest(files or implementation_files())
    return canonical_sha256(manifest), manifest


class AgentParameterVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_name = None
        self.records = []

    def visit_FunctionDef(self, node):
        previous = self.function_name
        self.function_name = node.name
        self.generic_visit(node)
        self.function_name = previous

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        function_name = getattr(node.func, "id", None)
        if function_name == "agent_model_settings" and len(node.args) >= 2:
            role_node = node.args[1]
            role = role_node.value if isinstance(role_node, ast.Constant) else None
            values = {"temperature": None, "max_tokens": None}
            for keyword in node.keywords:
                if keyword.arg in values and isinstance(keyword.value, ast.Constant):
                    values[keyword.arg] = keyword.value.value
            self.records.append(
                {
                    "builder": self.function_name,
                    "role": role,
                    "temperature": values["temperature"],
                    "max_tokens": values["max_tokens"],
                    "source_line": node.lineno,
                }
            )
        self.generic_visit(node)


def extract_agent_parameters():
    path = PROJECT_DIR / "src" / "table2text" / "agents.py"
    visitor = AgentParameterVisitor()
    visitor.visit(ast.parse(path.read_text(encoding="utf-8")))
    return visitor.records


current_implementation_sha256, current_file_manifest = implementation_fingerprint()
variant_sha256 = sha256_file(VARIANT_PATH)
prepared_examples_sha256 = sha256_file(PATHS["prepared_examples"])

if not FREEZE_MANIFEST_PATH.exists():
    snapshot_file_root = SNAPSHOT_DIR / "files"
    for item, source in zip(current_file_manifest, implementation_files()):
        destination = snapshot_file_root / item["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    freeze_manifest = {
        "experiment_id": EXPERIMENT_ID,
        "frozen_at": utc_now(),
        "freeze_basis": "exact_source_tree_snapshot",
        "git_commit": git_output("rev-parse", "HEAD"),
        "git_branch": git_output("branch", "--show-current"),
        "git_status_porcelain": (git_output("status", "--porcelain") or "").splitlines(),
        "git_worktree_clean": not bool(git_output("status", "--porcelain")),
        "implementation_sha256": current_implementation_sha256,
        "implementation_files": current_file_manifest,
        "variant_path": relative_path(VARIANT_PATH),
        "variant_sha256": variant_sha256,
        "prepared_examples_path": relative_path(PATHS["prepared_examples"]),
        "prepared_examples_sha256": prepared_examples_sha256,
        "models": {role.removesuffix("_model"): MODEL for role in MODEL_FIELDS},
        "generation_seed": GENERATION_SEED,
        "resolved_settings": frozen_overrides,
        "agent_model_parameters": extract_agent_parameters(),
        "provider_seed_forwarded_to_deepseek": False,
        "deepseek_base_url": os.getenv("DEEPSEEK_BASE_URL", "provider default"),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "table2text_package_source": str(PROJECT_DIR / "src" / "table2text"),
            "pydantic": package_version("pydantic"),
            "pydantic_ai": package_version("pydantic-ai"),
            "openai": package_version("openai"),
            "pandas": package_version("pandas"),
        },
        "secrets_recorded": False,
    }
    write_json_atomic(FREEZE_MANIFEST_PATH, freeze_manifest)
    log(f"Frozen implementation snapshot: {current_implementation_sha256}")
else:
    freeze_manifest = read_json(FREEZE_MANIFEST_PATH)
    log(f"Reusing frozen implementation: {freeze_manifest['implementation_sha256']}")


def assert_frozen_state():
    current_sha256, _ = implementation_fingerprint()
    errors = []
    if current_sha256 != freeze_manifest["implementation_sha256"]:
        errors.append(
            "implementation fingerprint changed after protected selection"
        )
    if sha256_file(VARIANT_PATH) != freeze_manifest["variant_sha256"]:
        errors.append("protected variant configuration changed")
    if sha256_file(PATHS["prepared_examples"]) != freeze_manifest["prepared_examples_sha256"]:
        errors.append("prepared benchmark file changed")
    if errors:
        raise RuntimeError("Protected-run freeze violation: " + "; ".join(errors))
    return current_sha256


assert_frozen_state()

print("Freeze basis:", freeze_manifest["freeze_basis"])
print("Git commit:", freeze_manifest["git_commit"])
print("Git worktree clean:", freeze_manifest["git_worktree_clean"])
print("Implementation SHA-256:", freeze_manifest["implementation_sha256"])
print("Variant SHA-256:", freeze_manifest["variant_sha256"])
print("Models:", sorted(set(freeze_manifest["models"].values())))
display(pd.DataFrame(freeze_manifest["agent_model_parameters"]))


# %% [markdown]
# ## 2. Freeze the unseen 25-example selection
#
# Selection uses only dataset ID and example ID. Every generation record found
# elsewhere under `evaluation/**/generations/**` is excluded. Sources and
# references do not participate in selection. The five datasets are then
# interleaved, so a partial run remains balanced across task families.
#
# The operational examples replace the true references with a fixed sentinel
# before any generator call. True references are recovered only in the final,
# explicitly opt-in post-generation metric phase.

# %%
TARGET_DATASET_SET = set(DATASETS)
HELD_OUT_REFERENCE_SENTINEL = "<HELD_OUT_REFERENCE_NOT_AVAILABLE_DURING_GENERATION>"
REFERENCE_LIKE_METADATA_KEYS = {
    "answer",
    "answers",
    "description",
    "descriptions",
    "gold",
    "news_article",
    "ref",
    "reference",
    "references",
    "summary",
    "summaries",
    "target",
    "targets",
    "text",
}


def historical_generation_inventory():
    identities = defaultdict(set)
    files = []
    evaluation_root = PROJECT_DIR / "evaluation"
    for path in sorted(evaluation_root.rglob("*.jsonl")):
        if path.is_relative_to(ARTIFACT_DIR):
            continue
        if "generations" not in path.parts:
            continue

        matched = 0
        for item in read_jsonl_objects(path):
            if "generated_text" not in item or "variant_id" not in item:
                continue
            dataset_id = str(item.get("dataset_id", ""))
            example_id = item.get("example_id")
            if dataset_id in TARGET_DATASET_SET and example_id is not None:
                identities[dataset_id].add(str(example_id))
                matched += 1
        if matched:
            files.append(
                {
                    "path": relative_path(path),
                    "sha256": sha256_file(path),
                    "matching_generation_rows": matched,
                }
            )
    return identities, files


all_examples = read_examples(PATHS["prepared_examples"])
example_lookup = {
    (str(example.dataset_id), str(example.example_id)): example
    for example in all_examples
}

if not SELECTION_MANIFEST_PATH.exists():
    assert_frozen_state()
    historical_ids, historical_files = historical_generation_inventory()
    selected_by_dataset = {}

    for dataset_id in DATASETS:
        candidates = sorted(
            [
                example
                for example in all_examples
                if example.dataset_id == dataset_id
                and str(example.example_id) not in historical_ids[dataset_id]
            ],
            key=lambda item: str(item.example_id),
        )
        if len(candidates) < EXAMPLES_PER_DATASET:
            raise RuntimeError(
                f"{dataset_id} has only {len(candidates)} previously unused "
                f"prepared examples; {EXAMPLES_PER_DATASET} are required."
            )
        generator = random.Random(f"{SELECTION_SEED}:{dataset_id}")
        selected_by_dataset[dataset_id] = sorted(
            generator.sample(candidates, EXAMPLES_PER_DATASET),
            key=lambda item: str(item.example_id),
        )

    # Round-robin order: one example from each dataset per block.
    selected_examples = [
        selected_by_dataset[dataset_id][position]
        for position in range(EXAMPLES_PER_DATASET)
        for dataset_id in DATASETS
    ]
    selection_timestamp = utc_now()

    exclusion_manifest = {
        "created_at": selection_timestamp,
        "selection_rule": (
            "Exclude every prior GenerationRecord found outside this protected "
            "experiment; sample by identity only."
        ),
        "historical_generation_files": historical_files,
        "excluded_example_ids": {
            dataset_id: sorted(historical_ids[dataset_id])
            for dataset_id in DATASETS
        },
    }
    write_json_atomic(EXCLUSION_MANIFEST_PATH, exclusion_manifest)

    selection_manifest = {
        "experiment_id": EXPERIMENT_ID,
        "selected_at": selection_timestamp,
        "protected": True,
        "selection_seed": SELECTION_SEED,
        "selection_algorithm": (
            "Dataset-stratified random sample after historical-generation "
            "exclusion; source and reference fields were not used."
        ),
        "examples_per_dataset": EXAMPLES_PER_DATASET,
        "dataset_order": DATASETS,
        "run_order": [
            {
                "position": index,
                "dataset_id": example.dataset_id,
                "example_id": str(example.example_id),
                "source_sha256": example.source_sha256,
                "reference_sha256": example.reference_sha256,
                "task_family": example.task_family.value,
                "output_mode": example.output_mode.value,
                "language": example.language,
            }
            for index, example in enumerate(selected_examples, start=1)
        ],
        "historical_overlap_count_at_selection": 0,
        "researcher_declared_no_prior_manual_inspection": (
            RESEARCHER_CONFIRMS_NO_PRIOR_MANUAL_INSPECTION
        ),
        "freeze_manifest_sha256": sha256_file(FREEZE_MANIFEST_PATH),
    }
    write_json_atomic(SELECTION_MANIFEST_PATH, selection_manifest)
    log(f"Protected selection frozen at {selection_timestamp}")
else:
    selection_manifest = read_json(SELECTION_MANIFEST_PATH)
    selected_examples = []
    for item in selection_manifest["run_order"]:
        key = (item["dataset_id"], str(item["example_id"]))
        if key not in example_lookup:
            raise RuntimeError(f"Selected example disappeared from prepared data: {key}")
        example = example_lookup[key]
        if example.source_sha256 != item["source_sha256"]:
            raise RuntimeError(f"Source hash changed for selected example: {key}")
        if example.reference_sha256 != item["reference_sha256"]:
            raise RuntimeError(f"Reference hash changed for selected example: {key}")
        selected_examples.append(example)
    log(f"Reusing protected selection from {selection_manifest['selected_at']}")

expected_total = len(DATASETS) * EXAMPLES_PER_DATASET
assert len(selected_examples) == expected_total
assert Counter(example.dataset_id for example in selected_examples) == Counter(
    {dataset_id: EXAMPLES_PER_DATASET for dataset_id in DATASETS}
)


def sanitize_operational_metadata(metadata):
    return {
        key: value
        for key, value in metadata.items()
        if key.casefold() not in REFERENCE_LIKE_METADATA_KEYS
        and "reference" not in key.casefold()
        and not key.casefold().startswith("target")
    }


operational_examples = [
    example.model_copy(
        update={
            "references": [HELD_OUT_REFERENCE_SENTINEL],
            "metadata": sanitize_operational_metadata(example.metadata),
        }
    )
    for example in selected_examples
]
write_jsonl_atomic(OPERATIONAL_EXAMPLES_PATH, operational_examples)


def audit_materialized_model_input(example):
    path = materialise_input(example, MODEL_INPUT_AUDIT_DIR)
    payload = json.loads(path.read_text(encoding="utf-8"))
    serialized = json.dumps(payload, ensure_ascii=False)
    forbidden_top_level = {
        "references",
        "reference_sha256",
        "target",
        "targets",
        "summary",
        "summaries",
    }
    present = sorted(forbidden_top_level & set(payload)) if isinstance(payload, dict) else []
    if present:
        raise RuntimeError(
            f"Reference-like top-level fields reached model input for "
            f"{example.dataset_id}/{example.example_id}: {present}"
        )
    if HELD_OUT_REFERENCE_SENTINEL in serialized:
        raise RuntimeError(
            f"Held-out reference sentinel reached model input for "
            f"{example.dataset_id}/{example.example_id}."
        )
    return {
        "dataset_id": example.dataset_id,
        "example_id": str(example.example_id),
        "materialized_input_path": relative_path(path),
        "materialized_input_sha256": sha256_file(path),
        "reference_fields_present": present,
        "reference_sentinel_present": False,
    }


model_input_audits = [
    audit_materialized_model_input(example) for example in operational_examples
]
write_json_atomic(
    MODEL_INPUT_AUDIT_DIR / "model_input_isolation_manifest.json",
    {
        "created_at": utc_now(),
        "reference_isolation": "pass",
        "records": model_input_audits,
    },
)

selected_table = pd.DataFrame(selection_manifest["run_order"])
display(
    selected_table[
        [
            "position",
            "dataset_id",
            "example_id",
            "task_family",
            "output_mode",
            "language",
        ]
    ]
)
print("Selected examples:", len(selected_examples))
print("Historical overlap:", selection_manifest["historical_overlap_count_at_selection"])
print("Reference isolation: PASS (sentinel absent from all materialized model inputs)")


# %% [markdown]
# ## 3. Initialize the experiment-level manifest
#
# This manifest is updated after every case. It records the frozen code and
# config, protected selection, model roles, task contracts, reference boundary,
# completion counts, and whether any implementation drift was detected.

# %%
def collect_final_records():
    records = []
    for item in selection_manifest["run_order"]:
        slug = f"{safe_name(item['dataset_id'])}__{safe_name(item['example_id'])}"
        path = SHARD_DIR / f"{slug}.jsonl"
        if not path.exists():
            continue
        rows = read_generations(path)
        if rows:
            records.append(rows[-1])
    write_jsonl_atomic(SEALED_GENERATIONS_PATH, records)
    return records


def update_batch_manifest(status=None):
    records = collect_final_records()
    successful = [record for record in records if not record.error and record.generated_text]
    failed = [record for record in records if record.error or not record.generated_text]
    inferred_status = (
        "complete"
        if len(successful) == expected_total and not failed
        else "running"
        if records
        else "selected"
    )
    prior = read_json(BATCH_MANIFEST_PATH, {})
    payload = {
        **prior,
        "experiment": "Protected Holdout Validation",
        "experiment_id": EXPERIMENT_ID,
        "selection_date": selection_manifest["selected_at"],
        "last_updated": utc_now(),
        "status": status or inferred_status,
        "protected_unseen": True,
        "system_frozen_before_selection": True,
        "freeze_basis": freeze_manifest["freeze_basis"],
        "git_commit": freeze_manifest["git_commit"],
        "git_worktree_clean_at_freeze": freeze_manifest["git_worktree_clean"],
        "implementation_sha256": freeze_manifest["implementation_sha256"],
        "configuration_path": relative_path(VARIANT_PATH),
        "configuration_sha256": freeze_manifest["variant_sha256"],
        "selection_manifest_sha256": sha256_file(SELECTION_MANIFEST_PATH),
        "model_input_isolation_manifest_sha256": sha256_file(
            MODEL_INPUT_AUDIT_DIR / "model_input_isolation_manifest.json"
        ),
        "model": "DeepSeek V4 Flash",
        "models_by_role": freeze_manifest["models"],
        "model_parameters": freeze_manifest["agent_model_parameters"],
        "generation_seed": GENERATION_SEED,
        "provider_seed_forwarded": False,
        "examples": expected_total,
        "datasets": {
            dataset_id: EXAMPLES_PER_DATASET for dataset_id in DATASETS
        },
        "selected_examples": selection_manifest["run_order"],
        "previous_manual_inspection_of_selected_examples": (
            "none_declared"
            if RESEARCHER_CONFIRMS_NO_PRIOR_MANUAL_INSPECTION
            else "not_confirmed"
        ),
        "historical_generation_overlap_count": (
            selection_manifest["historical_overlap_count_at_selection"]
        ),
        "development_changes_after_holdout_selection": (
            "none_verified_by_fingerprint"
            if RESEARCHER_CONFIRMS_NO_DEVELOPMENT_CHANGES_AFTER_SELECTION
            else "not_confirmed"
        ),
        "implementation_drift_detected": False,
        "human_references_available_to_generator": False,
        "reference_isolation_method": (
            "True references replaced by a sentinel in BenchmarkExample before "
            "generation; materialized model inputs contain neither references nor "
            "the sentinel."
        ),
        "released_generations_per_example": 1,
        "generation_configuration": relative_path(VARIANT_PATH),
        "completion": {
            "successful": len(successful),
            "failed": len(failed),
            "not_started": expected_total - len(records),
        },
        "sealed_generations_path": relative_path(SEALED_GENERATIONS_PATH),
        "summary_path": relative_path(SUMMARY_JSONL_PATH),
        "progress_log_path": relative_path(PROGRESS_LOG_PATH),
        "true_references_unsealed_at": prior.get("true_references_unsealed_at"),
    }
    if payload["status"] == "complete" and "generation_completed_at" not in payload:
        payload["generation_completed_at"] = utc_now()
    if records and "generation_started_at" not in payload:
        payload["generation_started_at"] = utc_now()
    write_json_atomic(BATCH_MANIFEST_PATH, payload)
    return payload


batch_manifest = update_batch_manifest()
display(pd.DataFrame([batch_manifest["completion"]]))


# %% [markdown]
# ## 4. Artifact and token extraction
#
# These functions summarize the workflow artifacts themselves. They do not
# infer missing information. Provider-reported token usage is parsed from the
# persisted trace, and monetary cost remains null unless directly returned.

# %%
USAGE_FIELD_PATTERN = {
    "input_tokens": re.compile(r"\binput_tokens=(\d+)"),
    "cache_read_tokens": re.compile(r"\bcache_read_tokens=(\d+)"),
    "output_tokens": re.compile(r"\boutput_tokens=(\d+)"),
    "requests": re.compile(r"\brequests=(\d+)"),
}


def parse_usage_string(value):
    if not isinstance(value, str):
        return None
    result = {}
    for name, pattern in USAGE_FIELD_PATTERN.items():
        match = pattern.search(value)
        result[name] = int(match.group(1)) if match else 0
    if not any(result.values()):
        return None
    result["total_tokens"] = result["input_tokens"] + result["output_tokens"]
    return result


def locate_pipeline_result(record):
    if record.pipeline_result_path:
        path = Path(record.pipeline_result_path)
        if path.exists():
            return path
    if record.run_id:
        matches = list(RUN_ROOT.rglob(f"{record.run_id}/pipeline_result.json"))
        if len(matches) == 1:
            return matches[0]
    return None


def stage_usage_rows(record, run_directory):
    trace_path = run_directory / "trace.jsonl"
    rows = []
    for index, event in enumerate(read_jsonl_objects(trace_path), start=1):
        usage = parse_usage_string(event.get("details", {}).get("usage"))
        if usage is None:
            continue
        rows.append(
            {
                "dataset_id": record.dataset_id,
                "example_id": str(record.example_id),
                "run_id": record.run_id,
                "trace_event": index,
                "timestamp": event.get("timestamp"),
                "stage": event.get("stage"),
                "status": event.get("status"),
                **usage,
            }
        )
    return rows


def run_artifact_index(record, run_directory):
    files = []
    for path in sorted(run_directory.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": relative_path(path),
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                }
            )
    return {
        "dataset_id": record.dataset_id,
        "example_id": str(record.example_id),
        "run_id": record.run_id,
        "run_directory": relative_path(run_directory),
        "artifact_count": len(files),
        "artifacts": files,
        "index_sha256": canonical_sha256(files),
    }


def trace_summary(run_directory):
    events = read_jsonl_objects(run_directory / "trace.jsonl")
    fallbacks = [event for event in events if event.get("status") == "fallback"]
    retries = [event for event in events if ".retry." in str(event.get("stage", ""))]
    non_success = [
        event
        for event in events
        if event.get("status") in {"fallback", "error", "failed"}
    ]
    return events, fallbacks, retries, non_success


def extract_summary(record):
    pipeline_path = locate_pipeline_result(record)
    if pipeline_path is None:
        return {
            "dataset_id": record.dataset_id,
            "example_id": str(record.example_id),
            "run_id": record.run_id,
            "execution_outcome": "failed",
            "error": record.error or "pipeline_result.json not found",
            "exact_final_output": record.generated_text,
        }, [], [], None

    result = read_json(pipeline_path)
    run_directory = pipeline_path.parent
    run_manifest = read_json(run_directory / "00_manifest.json", {})
    events, fallbacks, retries, non_success = trace_summary(run_directory)
    usage_rows = stage_usage_rows(record, run_directory)
    artifact_index = run_artifact_index(record, run_directory)

    fact_candidates = nested_list(result, "fact_candidates", "candidates")
    writer_ready_facts = nested_list(result, "fact_ledger", "writer_ready_facts")
    rejected_facts = nested_list(result, "fact_ledger", "rejected_facts")
    evidence_items = nested_list(result, "evidence_ledger", "items")
    verified_insights = nested_list(result, "insight_ledger", "verified_insights")
    rejected_insights = nested_list(result, "insight_ledger", "rejected_insights")
    unverified_insights = nested_list(result, "insight_ledger", "unverified_insights")
    hypothesis_insights = nested_list(result, "insight_ledger", "hypothesis_only_insights")
    insight_candidate_payload = read_json(run_directory / "07_insight_candidates.json", {})
    insight_candidates = (
        insight_candidate_payload.get("candidates", [])
        if isinstance(insight_candidate_payload, dict)
        else []
    )

    final_output = result.get("final_writer_output", {})
    raw_output = result.get("raw_writer_output", {})
    final_audit = result.get("final_audit", {})
    support = final_output.get("sentence_support", []) or []
    repair_rounds = result.get("repair_rounds_used", 0) or 0
    final_writer_mode = final_output.get("writer_mode") or record.writer_mode
    raw_writer_mode = raw_output.get("writer_mode")
    used_deterministic_fallback = "deterministic" in str(raw_writer_mode).casefold()

    if repair_rounds > 0 or final_audit.get("applied_patches"):
        final_generation_path = "auditor_repaired"
    elif used_deterministic_fallback:
        final_generation_path = "deterministic_fallback"
    else:
        final_generation_path = "normal_llm_writer"

    start_time = run_manifest.get("created_at")
    end_time = events[-1].get("timestamp") if events else None
    total_input_tokens = sum(row["input_tokens"] for row in usage_rows)
    total_output_tokens = sum(row["output_tokens"] for row in usage_rows)
    total_cache_tokens = sum(row["cache_read_tokens"] for row in usage_rows)
    total_requests = sum(row["requests"] for row in usage_rows)

    final_report_path = run_directory / "final_report.md"
    exact_released_report = (
        final_report_path.read_text(encoding="utf-8")
        if final_report_path.exists()
        else record.generated_text
    )
    actual_input_path = None
    input_paths = run_manifest.get("input_paths", [])
    if input_paths:
        candidate = Path(input_paths[0])
        if candidate.exists():
            actual_input_path = candidate
    expected_input_audit = next(
        (
            item
            for item in model_input_audits
            if item["dataset_id"] == record.dataset_id
            and item["example_id"] == str(record.example_id)
        ),
        None,
    )
    actual_input_sha256 = (
        sha256_file(actual_input_path) if actual_input_path is not None else None
    )
    expected_input_sha256 = (
        expected_input_audit["materialized_input_sha256"]
        if expected_input_audit is not None
        else None
    )

    summary = {
        "dataset_id": record.dataset_id,
        "example_id": str(record.example_id),
        "protected_unseen": True,
        "selection_timestamp": selection_manifest["selected_at"],
        "run_id": record.run_id,
        "generation_id": record.generation_id,
        "execution_outcome": "success" if not record.error else "failed",
        "error": record.error,
        "start_time": start_time,
        "end_time": end_time,
        "elapsed_seconds": record.elapsed_seconds,
        "task_family": record.task_family.value,
        "request": record.request,
        "output_mode": record.output_mode.value,
        "language": record.language,
        "task_contract": run_manifest.get("task_contract"),
        "report_genre": run_manifest.get("report_genre"),
        "communication_task": run_manifest.get("communication_task"),
        "focus_scope": run_manifest.get("focus_scope"),
        "models": run_manifest.get("models"),
        "generation_seed": record.seed,
        "configuration_sha256": freeze_manifest["variant_sha256"],
        "implementation_sha256": freeze_manifest["implementation_sha256"],
        "reference_available_to_generator": False,
        "source_sha256": next(
            item["source_sha256"]
            for item in selection_manifest["run_order"]
            if item["dataset_id"] == record.dataset_id
            and item["example_id"] == str(record.example_id)
        ),
        "reference_sha256": next(
            item["reference_sha256"]
            for item in selection_manifest["run_order"]
            if item["dataset_id"] == record.dataset_id
            and item["example_id"] == str(record.example_id)
        ),
        "input_paths": input_paths,
        "materialized_model_input_sha256": actual_input_sha256,
        "model_input_matches_reference_isolation_audit": (
            actual_input_sha256 is not None
            and actual_input_sha256 == expected_input_sha256
        ),
        "pipeline_result_path": relative_path(pipeline_path),
        "run_directory": relative_path(run_directory),
        "final_report_path": relative_path(final_report_path),
        "initial_writer_mode": raw_writer_mode,
        "final_writer_mode": final_writer_mode,
        "used_deterministic_fallback": used_deterministic_fallback,
        "final_generation_path": final_generation_path,
        "repair_rounds_used": repair_rounds,
        "audit_decision": final_audit.get("decision"),
        "release_status": result.get("release_status") or record.release_status,
        "approved_for_release": result.get("approved_for_release"),
        "primary_evaluation_eligible": result.get("primary_evaluation_eligible"),
        "native_support_rate": final_audit.get("support_rate"),
        "factual_sentence_count": final_audit.get("factual_sentence_count"),
        "supported_sentence_count": final_audit.get("supported_sentence_count"),
        "unsupported_factual_sentence_count": (
            (final_audit.get("factual_sentence_count") or 0)
            - (final_audit.get("supported_sentence_count") or 0)
        ),
        "sentence_support_mapping_count": len(support),
        "output_word_count": markdown_word_count(record.generated_text),
        "output_sentence_count": prose_sentence_count(record.generated_text),
        "evidence_item_count": len(evidence_items),
        "fact_candidate_count": len(fact_candidates),
        "verified_fact_count": len(writer_ready_facts),
        "rejected_fact_count": len(rejected_facts),
        "insight_candidate_count": len(insight_candidates),
        "verified_insight_count": len(verified_insights),
        "rejected_insight_count": len(rejected_insights),
        "unverified_insight_count": len(unverified_insights),
        "hypothesis_only_insight_count": len(hypothesis_insights),
        "top_level_attempt_count": sum(
            1
            for item in read_jsonl_objects(ATTEMPT_LOG_PATH)
            if item.get("event") == "started"
            and item.get("dataset_id") == record.dataset_id
            and item.get("example_id") == str(record.example_id)
        ),
        "trace_retry_event_count": len(retries),
        "fallback_event_count": len(fallbacks),
        "non_success_trace_event_count": len(non_success),
        "fallbacks": fallbacks,
        "trace_retries": retries,
        "provider_reported_input_tokens": total_input_tokens,
        "provider_reported_output_tokens": total_output_tokens,
        "provider_reported_total_tokens": total_input_tokens + total_output_tokens,
        "provider_reported_cache_read_tokens": total_cache_tokens,
        "provider_reported_requests": total_requests,
        "monetary_cost": record.estimated_cost_gbp,
        "monetary_cost_source": (
            "provider/evaluation record"
            if record.estimated_cost_gbp is not None
            else "not directly available"
        ),
        "artifact_count": artifact_index["artifact_count"],
        "artifact_index_sha256": artifact_index["index_sha256"],
        "exact_final_output": record.generated_text,
        "exact_released_report": exact_released_report,
    }

    support_rows = [
        {
            "dataset_id": record.dataset_id,
            "example_id": str(record.example_id),
            "run_id": record.run_id,
            **mapping,
        }
        for mapping in support
    ]
    return summary, usage_rows, support_rows, artifact_index


def csv_safe_summary(summary):
    excluded = {
        "task_contract",
        "models",
        "input_paths",
        "fallbacks",
        "trace_retries",
        "exact_final_output",
        "exact_released_report",
    }
    return {key: value for key, value in summary.items() if key not in excluded}


def escape_markdown(value):
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def rebuild_aggregate_artifacts():
    records = collect_final_records()
    summaries = []
    usage_rows = []
    support_rows = []
    artifact_indexes = []
    for record in records:
        summary, usage, support, artifact_index = extract_summary(record)
        summaries.append(summary)
        usage_rows.extend(usage)
        support_rows.extend(support)
        if artifact_index is not None:
            artifact_indexes.append(artifact_index)

    write_jsonl_atomic(SUMMARY_JSONL_PATH, summaries)
    write_jsonl_atomic(SUPPORT_MAP_JSONL_PATH, support_rows)
    write_jsonl_atomic(ARTIFACT_INDEX_PATH, artifact_indexes)
    pd.DataFrame([csv_safe_summary(item) for item in summaries]).to_csv(
        SUMMARY_CSV_PATH,
        index=False,
    )
    pd.DataFrame(usage_rows).to_csv(STAGE_USAGE_CSV_PATH, index=False)

    manifest = update_batch_manifest()
    lines = [
        "# Protected Holdout Execution Report",
        "",
        f"- Experiment: `{EXPERIMENT_ID}`",
        f"- Selection timestamp: `{selection_manifest['selected_at']}`",
        f"- Frozen implementation: `{freeze_manifest['implementation_sha256']}`",
        f"- Git commit: `{freeze_manifest['git_commit']}`",
        f"- Configuration: `{relative_path(VARIANT_PATH)}`",
        f"- Configuration SHA-256: `{freeze_manifest['variant_sha256']}`",
        f"- Model for all six roles: `{MODEL}`",
        f"- Status: `{manifest['status']}`",
        f"- Completion: `{manifest['completion']}`",
        "- References available during generation: `No`",
        "",
        "## Run Summary",
        "",
        "| Dataset | Example | Outcome | Path | Release | Support | Words | Tokens | Seconds |",
        "|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    for item in summaries:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_markdown(item.get("dataset_id")),
                    escape_markdown(item.get("example_id")),
                    escape_markdown(item.get("execution_outcome")),
                    escape_markdown(item.get("final_generation_path")),
                    escape_markdown(item.get("release_status")),
                    escape_markdown(item.get("native_support_rate")),
                    escape_markdown(item.get("output_word_count")),
                    escape_markdown(item.get("provider_reported_total_tokens")),
                    escape_markdown(
                        round(item.get("elapsed_seconds") or 0.0, 1)
                    ),
                ]
            )
            + " |"
        )

    if usage_rows:
        usage_frame = pd.DataFrame(usage_rows)
        stage_totals = (
            usage_frame.groupby("stage", as_index=False)[
                ["input_tokens", "output_tokens", "total_tokens", "requests"]
            ]
            .sum()
            .sort_values("total_tokens", ascending=False)
        )
        lines.extend(
            [
                "",
                "## Provider-Reported Usage by Stage",
                "",
                "| Stage | Input tokens | Output tokens | Total tokens | Requests |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in stage_totals.to_dict(orient="records"):
            lines.append(
                f"| {escape_markdown(row['stage'])} | {row['input_tokens']} | "
                f"{row['output_tokens']} | {row['total_tokens']} | {row['requests']} |"
            )

    lines.extend(
        [
            "",
            "## Artifact Locations",
            "",
            f"- Batch manifest: `{relative_path(BATCH_MANIFEST_PATH)}`",
            f"- Exact outputs and run summaries: `{relative_path(SUMMARY_JSONL_PATH)}`",
            f"- Sentence support: `{relative_path(SUPPORT_MAP_JSONL_PATH)}`",
            f"- Stage usage: `{relative_path(STAGE_USAGE_CSV_PATH)}`",
            f"- Run checksums: `{relative_path(ARTIFACT_INDEX_PATH)}`",
            f"- Progress log: `{relative_path(PROGRESS_LOG_PATH)}`",
            "",
        ]
    )
    EXECUTION_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return pd.DataFrame([csv_safe_summary(item) for item in summaries])


summary_frame = rebuild_aggregate_artifacts()
if not summary_frame.empty:
    display(summary_frame)


# %% [markdown]
# ## 5. Run or resume the protected generation batch
#
# Each example has an independent generation shard. Failed attempts are copied
# to `attempt_records/` before retry; successful outputs are never regenerated.
# The exact implementation/config/input fingerprints are checked immediately
# before every call.

# %%
def operational_example_lookup():
    return {
        (str(example.dataset_id), str(example.example_id)): example
        for example in operational_examples
    }


def attempt_count(dataset_id, example_id):
    return sum(
        1
        for item in read_jsonl_objects(ATTEMPT_LOG_PATH)
        if item.get("event") == "started"
        and item.get("dataset_id") == dataset_id
        and item.get("example_id") == str(example_id)
    )


def existing_success(shard_path):
    if not shard_path.exists():
        return None
    rows = read_generations(shard_path)
    if not rows:
        return None
    row = rows[-1]
    return row if not row.error and bool(row.generated_text.strip()) else None


async def run_protected_batch():
    operational_lookup = operational_example_lookup()
    completed_before = {
        (record.dataset_id, str(record.example_id))
        for record in collect_final_records()
        if not record.error and record.generated_text.strip()
    }
    pending = [
        item
        for item in selection_manifest["run_order"]
        if (item["dataset_id"], str(item["example_id"])) not in completed_before
    ]
    if MAX_CASES_THIS_SESSION is not None:
        pending = pending[:MAX_CASES_THIS_SESSION]

    log("=" * 80)
    log(
        f"Protected batch: {len(completed_before)}/{expected_total} already complete; "
        f"{len(pending)} scheduled this session."
    )
    if pending:
        manifest = read_json(BATCH_MANIFEST_PATH, {})
        if not manifest.get("generation_started_at"):
            manifest["generation_started_at"] = utc_now()
            manifest["status"] = "running"
            manifest["last_updated"] = utc_now()
            write_json_atomic(BATCH_MANIFEST_PATH, manifest)

    for session_index, item in enumerate(pending, start=1):
        dataset_id = item["dataset_id"]
        example_id = str(item["example_id"])
        key = (dataset_id, example_id)
        example = operational_lookup[key]
        slug = f"{safe_name(dataset_id)}__{safe_name(example_id)}"
        example_path = PREPARED_DIR / "shards" / f"{slug}.jsonl"
        shard_path = SHARD_DIR / f"{slug}.jsonl"
        run_root = RUN_ROOT / slug
        example_path.parent.mkdir(parents=True, exist_ok=True)
        write_jsonl_atomic(example_path, [example])

        success = existing_success(shard_path)
        if success is not None:
            log(f"SKIP {dataset_id}/{example_id}: successful shard already exists")
            continue

        prior_attempts = attempt_count(dataset_id, example_id)
        remaining_attempts = max(
            0,
            MAX_TOP_LEVEL_ATTEMPTS_PER_EXAMPLE - prior_attempts,
        )
        if remaining_attempts == 0:
            log(f"EXHAUSTED {dataset_id}/{example_id}: no attempts remain")
            continue

        log("-" * 80)
        log(
            f"CASE {session_index}/{len(pending)} this session; "
            f"protected position {item['position']}/{expected_total}: "
            f"{dataset_id}/{example_id}"
        )

        case_succeeded = False
        for _ in range(remaining_attempts):
            assert_frozen_state()
            attempt_number = attempt_count(dataset_id, example_id) + 1
            attempt_started = utc_now()
            append_jsonl(
                ATTEMPT_LOG_PATH,
                {
                    "event": "started",
                    "timestamp": attempt_started,
                    "dataset_id": dataset_id,
                    "example_id": example_id,
                    "attempt": attempt_number,
                    "implementation_sha256": freeze_manifest["implementation_sha256"],
                    "configuration_sha256": freeze_manifest["variant_sha256"],
                },
            )

            if shard_path.exists():
                archived = ATTEMPT_RECORD_DIR / f"{slug}__before_attempt_{attempt_number}.jsonl"
                shutil.copy2(shard_path, archived)
                shard_path.unlink()

            try:
                frame = await with_heartbeat(
                    generate_reports_for_notebook(
                        PROJECT_DIR,
                        examples_path=example_path,
                        variants_path=VARIANT_PATH,
                        output_path=shard_path,
                        run_root=run_root,
                        resume=False,
                    ),
                    label=(
                        f"{dataset_id}/{example_id} attempt "
                        f"{attempt_number}/{MAX_TOP_LEVEL_ATTEMPTS_PER_EXAMPLE}"
                    ),
                )
                row = frame.iloc[-1].to_dict() if not frame.empty else {}
                error = row.get("error") or None
                generated_text = str(row.get("generated_text") or "")
                success = not error and bool(generated_text.strip())
                append_jsonl(
                    ATTEMPT_LOG_PATH,
                    {
                        "event": "finished",
                        "timestamp": utc_now(),
                        "dataset_id": dataset_id,
                        "example_id": example_id,
                        "attempt": attempt_number,
                        "success": success,
                        "error": error,
                        "run_id": row.get("run_id"),
                        "pipeline_result_path": row.get("pipeline_result_path"),
                        "elapsed_seconds": row.get("elapsed_seconds"),
                    },
                )
                if shard_path.exists():
                    shutil.copy2(
                        shard_path,
                        ATTEMPT_RECORD_DIR / f"{slug}__attempt_{attempt_number}.jsonl",
                    )

                rebuild_aggregate_artifacts()
                manifest = update_batch_manifest("running")
                log(
                    f"{dataset_id}/{example_id}: success={success}, "
                    f"release={row.get('release_status')}, "
                    f"writer={row.get('writer_mode')}, error={error}"
                )
                log(f"Batch completion: {manifest['completion']}")

                if PRINT_FINAL_OUTPUTS and generated_text:
                    display(
                        Markdown(
                            f"### {dataset_id} / {example_id}\n\n{generated_text}"
                        )
                    )
                if success:
                    case_succeeded = True
                    break
            except Exception as exc:
                append_jsonl(
                    ATTEMPT_LOG_PATH,
                    {
                        "event": "exception",
                        "timestamp": utc_now(),
                        "dataset_id": dataset_id,
                        "example_id": example_id,
                        "attempt": attempt_number,
                        "success": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                )
                log(
                    f"{dataset_id}/{example_id} attempt {attempt_number} raised "
                    f"{type(exc).__name__}: {exc}"
                )

        if not case_succeeded and not CONTINUE_AFTER_FAILURE:
            raise RuntimeError(f"Protected generation failed: {dataset_id}/{example_id}")

    final_frame = rebuild_aggregate_artifacts()
    final_manifest = update_batch_manifest()
    assert_frozen_state()
    log("=" * 80)
    log(f"Session complete. Batch status: {final_manifest['status']}")
    log(f"Completion: {final_manifest['completion']}")
    log(f"Execution report: {EXECUTION_REPORT_PATH}")
    return final_frame


protected_results = await run_protected_batch()

if not protected_results.empty:
    display(
        protected_results[
            [
                "dataset_id",
                "example_id",
                "execution_outcome",
                "final_generation_path",
                "release_status",
                "native_support_rate",
                "output_word_count",
                "verified_fact_count",
                "verified_insight_count",
                "fallback_event_count",
                "provider_reported_total_tokens",
                "elapsed_seconds",
            ]
        ]
    )


# %% [markdown]
# ## 6. Batch integrity checks
#
# This cell is safe to rerun at any point. It reports missing, failed, or
# incomplete cases without regenerating anything.

# %%
assert_frozen_state()
records = collect_final_records()
record_by_key = {
    (record.dataset_id, str(record.example_id)): record for record in records
}
integrity_rows = []
for item in selection_manifest["run_order"]:
    key = (item["dataset_id"], str(item["example_id"]))
    record = record_by_key.get(key)
    pipeline_path = locate_pipeline_result(record) if record else None
    integrity_rows.append(
        {
            "position": item["position"],
            "dataset_id": item["dataset_id"],
            "example_id": item["example_id"],
            "record_present": record is not None,
            "generation_success": bool(
                record and not record.error and record.generated_text.strip()
            ),
            "pipeline_result_present": bool(pipeline_path and pipeline_path.exists()),
            "reference_masked_in_record": bool(
                record and record.references == [HELD_OUT_REFERENCE_SENTINEL]
            ),
            "model_input_isolation_hash_match": bool(
                record
                and pipeline_path
                and extract_summary(record)[0].get(
                    "model_input_matches_reference_isolation_audit"
                )
            ),
            "error": record.error if record else None,
        }
    )

integrity_frame = pd.DataFrame(integrity_rows)
display(integrity_frame)
print("Successful:", int(integrity_frame["generation_success"].sum()), "/", expected_total)
print("All references masked:", bool(integrity_frame["reference_masked_in_record"].all()))
print("Implementation fingerprint unchanged: PASS")


# %% [markdown]
# ## 7. Optional post-generation reference and source metrics
#
# This phase is blocked until all 25 protected generations are successful.
# Only here are the true references joined back into a separate copy of the
# GenerationRecords. The sealed generation file and all workflow artifacts are
# left untouched.

# %%
def unseal_generation_records_for_metrics():
    records = collect_final_records()
    successful = [record for record in records if not record.error and record.generated_text]
    if len(successful) != expected_total:
        raise RuntimeError(
            f"Cannot unseal references: {len(successful)}/{expected_total} "
            "protected generations are successful."
        )
    assert_frozen_state()
    true_lookup = {
        (example.dataset_id, str(example.example_id)): example
        for example in selected_examples
    }
    unsealed = [
        record.model_copy(
            update={
                "references": true_lookup[
                    (record.dataset_id, str(record.example_id))
                ].references
            }
        )
        for record in successful
    ]
    write_jsonl_atomic(UNSEALED_GENERATIONS_PATH, unsealed)
    manifest = read_json(BATCH_MANIFEST_PATH, {})
    if not manifest.get("true_references_unsealed_at"):
        manifest["true_references_unsealed_at"] = utc_now()
        manifest["true_references_unsealed_for"] = "post-generation evaluation only"
        manifest["unsealed_generations_path"] = relative_path(UNSEALED_GENERATIONS_PATH)
        write_json_atomic(BATCH_MANIFEST_PATH, manifest)
    return unsealed


def build_metric_config(enabled_metrics, context, filename):
    payload = copy.deepcopy(read_json(PATHS["metric_config"]))
    payload["experiment_id"] = f"{EXPERIMENT_ID}_{context}"
    payload["prepared_examples_path"] = relative_path(OPERATIONAL_EXAMPLES_PATH)
    payload["generations_path"] = relative_path(UNSEALED_GENERATIONS_PATH)
    payload["result_directory"] = relative_path(RESULT_DIR)
    payload["baseline_variant"] = "full_system"
    payload["reference_metrics"]["enabled_metrics"] = enabled_metrics
    payload["reference_metrics"]["external_factuality_context"] = context
    payload["deepeval"]["enabled"] = False
    path = CONFIG_DIR / filename
    write_json_atomic(path, payload)
    return path


reference_scores = pd.DataFrame()
source_scores = pd.DataFrame()

if RUN_POST_GENERATION_REFERENCE_METRICS or RUN_POST_GENERATION_SOURCE_METRICS:
    unseal_generation_records_for_metrics()

if RUN_POST_GENERATION_REFERENCE_METRICS:
    reference_config_path = build_metric_config(
        [
            "bleu",
            "chrf",
            "ter",
            "rouge1",
            "rouge2",
            "rougeL",
            "rougeLsum",
            "meteor",
            "bertscore",
            "parent",
        ],
        "references",
        "metrics_protected_reference.json",
    )
    log("Starting protected post-generation reference metrics")
    reference_scores = score_reference_metrics_for_notebook(
        PROJECT_DIR,
        generations_path=UNSEALED_GENERATIONS_PATH,
        metric_config_path=reference_config_path,
        output_path=RESULT_DIR / "protected_reference_metrics.jsonl",
        include_ineligible=True,
    )
    display(
        reference_scores.pivot_table(
            index="metric_name",
            values="score",
            aggfunc="mean",
        ).sort_index()
    )

if RUN_POST_GENERATION_SOURCE_METRICS:
    source_config_path = build_metric_config(
        ["hhem", "alignscore"],
        "source_text",
        "metrics_protected_source_grounded.json",
    )
    log("Starting protected post-generation source-grounded metrics")
    source_scores = score_reference_metrics_for_notebook(
        PROJECT_DIR,
        generations_path=UNSEALED_GENERATIONS_PATH,
        metric_config_path=source_config_path,
        output_path=RESULT_DIR / "protected_source_grounded_metrics.jsonl",
        include_ineligible=True,
    )
    display(
        source_scores.pivot_table(
            index="metric_name",
            values="score",
            aggfunc="mean",
        ).sort_index()
    )

print("Protected generation artifacts:", ARTIFACT_DIR)
print("Batch manifest:", BATCH_MANIFEST_PATH)
print("Execution report:", EXECUTION_REPORT_PATH)
print("Exact outputs and summaries:", SUMMARY_JSONL_PATH)
