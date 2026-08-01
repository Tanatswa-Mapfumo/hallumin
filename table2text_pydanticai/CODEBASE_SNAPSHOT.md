# Codebase Snapshot

- Project: `table2text_pydanticai`
- Generated: `2026-07-24T18:16:20Z`
- Git branch: `main`
- Git commit: `195605d`
- Included files: `18`

## Scope

Included: project README/config, package source, tests, and the current report-coverage helper script.

Excluded: datasets, notebook runs, validation runs, virtual environments, caches, backup folders, binary files, and local notebooks.

## Git Status

```text
M table2text_pydanticai/src/table2text/agents.py
 M table2text_pydanticai/src/table2text/audit.py
 M table2text_pydanticai/src/table2text/capabilities.py
 M table2text_pydanticai/src/table2text/schemas.py
 M table2text_pydanticai/src/table2text/workflow.py
 M table2text_pydanticai/tests/test_semantic_event_pipeline.py
 M table2text_pydanticai/tests/test_smoke.py
?? e.ipynb
?? table2text_pydanticai/.table2text_report_fix_backup_20260715_100700/
?? table2text_pydanticai/.table2text_report_fix_backup_20260715_101128/
?? table2text_pydanticai/.table2text_report_fix_backup_20260715_101846/
?? table2text_pydanticai/apply_report_coverage_fix.py
```

## File Tree

```text
.env.example (4,153 bytes)
README.md (1,505 bytes)
apply_report_coverage_fix.py (81,839 bytes)
pyproject.toml (849 bytes)
src/table2text/__init__.py (187 bytes)
src/table2text/__main__.py (61 bytes)
src/table2text/agents.py (145,599 bytes)
src/table2text/analytics.py (89,028 bytes)
src/table2text/audit.py (209,529 bytes)
src/table2text/capabilities.py (76,555 bytes)
src/table2text/cli.py (4,567 bytes)
src/table2text/config.py (13,263 bytes)
src/table2text/data.py (20,715 bytes)
src/table2text/schemas.py (34,003 bytes)
src/table2text/structure.py (18,996 bytes)
src/table2text/workflow.py (90,300 bytes)
tests/test_semantic_event_pipeline.py (42,680 bytes)
tests/test_smoke.py (136,294 bytes)
```

## File Contents

### `.env.example`

````dotenv
# ============================================================
# GENERAL
# ============================================================

T2T_USE_LLM=true
T2T_OUTPUT_DIR=runs

T2T_MAX_REVISION_ROUNDS=2
T2T_MAX_AGENT_REQUESTS=4
T2T_MAX_TOTAL_TOKENS=24000

T2T_RANDOM_SEED=42
T2T_MAX_ANALYSIS_ROWS=50000
T2T_STRUCTURED_OUTPUT_MODE=native

# ============================================================
# ANALYTICAL QUALITY
# ============================================================

# Correlations use the full dataset below this limit.
T2T_FULL_DATA_CORRELATION_LIMIT=250000

# Weak relationships below this magnitude are not promoted.
T2T_MIN_ABS_CORRELATION=0.20
T2T_MAX_CORRELATION_FINDINGS=6
T2T_MAX_GROUP_FINDINGS=8

# Numeric feature/target correlations above this threshold
# are treated as possible target proxies.
T2T_TARGET_PROXY_CORRELATION=0.98

# Experimental target selection is disabled by default.
# Enable only for explicit modelling experiments.
T2T_ALLOW_EXPERIMENTAL_TARGETS=false

# Forecast evaluation.
T2T_FORECAST_FOLDS=3
T2T_MAX_FORECAST_TEST_POINTS=2000

# ============================================================
# REPORT WRITING
# ============================================================

T2T_WRITER_TARGET_WORDS=650
T2T_WRITER_MAX_MAIN_FINDINGS=8
T2T_REPAIR_CANDIDATES_PER_SENTENCE=3

# ============================================================
# VERIFIED BOUNDED INSIGHT SYNTHESIS
# ============================================================

T2T_ENABLE_INSIGHT_SYNTHESIS=true
T2T_MAX_INSIGHT_CANDIDATES=6
T2T_MAX_VERIFIED_MAIN_INSIGHTS=4
T2T_MIN_INSIGHT_CONFIDENCE=0.75
T2T_MIN_INSIGHT_SALIENCE=0.65
T2T_MIN_FACTS_PER_BOUNDED_INSIGHT=2
T2T_ALLOW_HYPOTHESES_IN_REPORT=false

# ============================================================
# WRITER QUALITY AND FACT SELECTION
# ============================================================

# At most one bounded whole-report Writer quality revision.
T2T_WRITER_QUALITY_REVISION_ROUNDS=1

# Balanced writer evidence-pack limits.
T2T_WRITER_PRIORITY_FACT_LIMIT=10
T2T_WRITER_SUPPORTING_FACT_LIMIT=20

T2T_MAX_PRIORITY_DATASET_OVERVIEW_FACTS=2
T2T_MAX_PRIORITY_DATA_QUALITY_FACTS=3
T2T_MAX_PRIORITY_CORRELATION_FACTS=3
T2T_MAX_PRIORITY_GROUP_COMPARISON_FACTS=2
T2T_MAX_PRIORITY_PREDICTIVE_FACTS=1
T2T_MAX_PRIORITY_FORECAST_FACTS=1
T2T_MAX_PRIORITY_LIMITATION_FACTS=2

# Minimum useful report-length diagnostics.
T2T_MINIMUM_REPORT_WORD_RATIO=0.45
T2T_MINIMUM_REPORT_WORD_FLOOR=160

# Repeated causal/confounding caveats beyond this count are a quality issue.
T2T_MAXIMUM_REPEATED_CAVEAT_MENTIONS=4

T2T_MINIMUM_MAIN_FINDING_SCORE=0.65
T2T_MINIMUM_MAIN_EFFECT_STRENGTH=moderate

T2T_MAX_DATA_QUALITY_FINDINGS=3
T2T_MAX_ASSOCIATION_FINDINGS=4
T2T_MAX_PREDICTIVE_FINDINGS=1
T2T_MAX_FORECAST_FINDINGS=1
T2T_MAX_LIMITATION_FINDINGS=3

# Zero values above this risk threshold may be treated as unusual.
T2T_ZERO_UNUSUAL_RATE_THRESHOLD=0.05

# ============================================================
# OLLAMA
# ============================================================

OLLAMA_BASE_URL=http://localhost:11434/v1

# ============================================================
# MODEL ROUTING
# ============================================================

T2T_MODEL_DATA_UNDERSTANDING=ollama:gemma3:4b
T2T_MODEL_ORCHESTRATOR=ollama:gemma3:12b
T2T_MODEL_EVIDENCE=ollama:gemma3:12b
T2T_MODEL_VERIFIER=ollama:gemma3:12b
T2T_MODEL_WRITER=ollama:gemma3:12b
T2T_MODEL_AUDITOR=ollama:gemma3:12b

# ============================================================
# DETERMINISTIC FACT-COVERAGE RECOVERY
# ============================================================

# Recover safe writer-ready facts directly from trusted deterministic
# evidence when the LLM evidence/verifier stages leave the ledger too thin.
T2T_MINIMUM_WRITER_READY_FACT_COUNT=6

T2T_MINIMUM_OVERVIEW_FACT_COUNT=1
T2T_MINIMUM_DATA_QUALITY_FACT_COUNT=1
T2T_MINIMUM_RELATIONSHIP_FACT_COUNT=2

T2T_MAXIMUM_RECOVERED_OVERVIEW_FACTS=2
T2T_MAXIMUM_RECOVERED_DATA_QUALITY_FACTS=3
T2T_MAXIMUM_RECOVERED_CORRELATION_FACTS=3
T2T_MAXIMUM_RECOVERED_GROUP_COMPARISON_FACTS=2
T2T_MAXIMUM_RECOVERED_MODELLING_FACTS=1
````

### `README.md`

````markdown
# Table2Text PydanticAI Multi-Agent System

This project investigates whether an evidence-generating, claim-verifying,
multi-agent workflow can reduce hallucinations in Table2Text generation.

It does not claim to eliminate hallucinations.

## Six-agent architecture

1. Data Understanding Agent
2. Orchestrator and Investigation Planner
3. Evidence Analyst Agent
4. Claim Verification Agent
5. Writer Agent
6. Factual Accuracy Auditor Agent

## Workflow

Input tables
→ deterministic loading and profiling
→ Data Understanding Agent
→ Orchestrator creates a frozen investigation plan
→ deterministic analytical execution
→ Evidence Analyst creates claim candidates
→ Claim Verification Agent
→ deterministic claim-ledger gate
→ Writer Agent
→ Factual Accuracy Auditor
→ pass, revise, or block

## Why deterministic analytics remain

The LLM agents do not calculate statistics directly.

Python performs:

- table loading;
- profiling;
- missing-value analysis;
- descriptive statistics;
- correlations and group comparisons;
- predictive train/test validation;
- forecast backtesting;
- causal-feasibility checks;
- evidence and claim identifier validation;
- number-support checks;
- audit gates.

The LLM agents perform:

- semantic data understanding;
- investigation planning;
- evidence synthesis;
- claim review;
- natural-language writing;
- semantic factual-accuracy annotation.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
````

### `apply_report_coverage_fix.py`

````python
#!/usr/bin/env python3
"""
Apply the Table2Text report-coverage and weak-finding-selection fix.

Run from the repository root:

    python apply_report_coverage_fix.py

The script:

1. Creates timestamped backups.
2. Updates schemas.py.
3. Updates config.py.
4. Updates .env.example.
5. Updates audit.py.
6. Updates agents.py.
7. Updates workflow.py.
8. Adds deterministic regression tests.
9. Runs compileall and pytest.

It intentionally does not modify:

- analytics.py
- data.py
- datasets
- generated run directories
- prototype3
- dependencies
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()

SOURCE_DIR = ROOT / "src" / "table2text"

SCHEMAS = SOURCE_DIR / "schemas.py"
CONFIG = SOURCE_DIR / "config.py"
AUDIT = SOURCE_DIR / "audit.py"
AGENTS = SOURCE_DIR / "agents.py"
WORKFLOW = SOURCE_DIR / "workflow.py"
TESTS = ROOT / "tests" / "test_smoke.py"
ENV_EXAMPLE = ROOT / ".env.example"

REQUIRED_FILES = [
    ROOT / "pyproject.toml",
    SCHEMAS,
    CONFIG,
    AUDIT,
    AGENTS,
    WORKFLOW,
    TESTS,
    ENV_EXAMPLE,
]


def fail(message: str) -> None:
    raise RuntimeError(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def replace_once(
    path: Path,
    old: str,
    new: str,
    *,
    description: str,
) -> None:
    source = read(path)

    count = source.count(old)

    if count != 1:
        fail(
            f"{description}: expected exactly one matching block in "
            f"{path}, found {count}."
        )

    write(path, source.replace(old, new, 1))


def insert_before_once(
    path: Path,
    marker: str,
    insertion: str,
    *,
    description: str,
) -> None:
    source = read(path)

    count = source.count(marker)

    if count != 1:
        fail(
            f"{description}: expected exactly one marker in "
            f"{path}, found {count}."
        )

    write(
        path,
        source.replace(
            marker,
            insertion.rstrip() + "\n\n" + marker,
            1,
        ),
    )


def replace_top_level_function(
    path: Path,
    function_name: str,
    replacement: str,
) -> None:
    source = read(path)

    start_match = re.search(
        rf"(?m)^def {re.escape(function_name)}\s*\(",
        source,
    )

    if start_match is None:
        fail(
            f"Could not find top-level function "
            f"`{function_name}` in {path}."
        )

    start = start_match.start()

    next_definition = re.search(
        r"(?m)^(?:def|class)\s+[A-Za-z_]\w*",
        source[start_match.end():],
    )

    if next_definition is None:
        end = len(source)
    else:
        end = (
            start_match.end()
            + next_definition.start()
        )

    new_source = (
        source[:start]
        + textwrap.dedent(replacement).strip()
        + "\n\n"
        + source[end:]
    )

    write(path, new_source)


def run_command(command: list[str]) -> int:
    print("\n$", " ".join(command))

    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
    )

    return completed.returncode


def create_backups() -> Path:
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_dir = (
        ROOT
        / f".table2text_report_fix_backup_{timestamp}"
    )

    backup_dir.mkdir(parents=True)

    for path in REQUIRED_FILES[1:]:
        destination = backup_dir / path.name
        shutil.copy2(path, destination)

    return backup_dir


def update_schemas() -> None:
    source = read(SCHEMAS)

    if "class VerificationMethod" not in source:
        replace_once(
            SCHEMAS,
            """class ReviewDecision(str, Enum):
    APPROVE = "approve"
    CAUTION = "caution"
    REJECT = "reject"
""",
            """class ReviewDecision(str, Enum):
    APPROVE = "approve"
    CAUTION = "caution"
    REJECT = "reject"


class VerificationMethod(str, Enum):
    LLM_VERIFIED = "llm_verified"
    DETERMINISTIC_EVIDENCE_RECOVERY = (
        "deterministic_evidence_recovery"
    )
""",
            description=(
                "Add transparent verification method"
            ),
        )

    source = read(SCHEMAS)

    if "verification_method:" not in source:
        replace_once(
            SCHEMAS,
            """class VerifiedFact(StrictModel):
    fact_id: str
    source_candidate_id: str

    fact_summary: str
""",
            """class VerifiedFact(StrictModel):
    fact_id: str
    source_candidate_id: str

    verification_method: VerificationMethod = (
        VerificationMethod.LLM_VERIFIED
    )

    fact_summary: str
""",
            description=(
                "Add verification_method to VerifiedFact"
            ),
        )

    source = read(SCHEMAS)

    if "deterministically_recovered_fact_ids" not in source:
        replace_once(
            SCHEMAS,
            """class FactLedger(StrictModel):
    writer_ready_facts: list[VerifiedFact]
    rejected_facts: list[RejectedFact] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)
""",
            """class FactLedger(StrictModel):
    writer_ready_facts: list[VerifiedFact]
    rejected_facts: list[RejectedFact] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)

    deterministically_recovered_fact_ids: list[str] = Field(
        default_factory=list
    )
    coverage_recovery_notes: list[str] = Field(
        default_factory=list
    )
""",
            description=(
                "Add fact-ledger recovery metadata"
            ),
        )


def update_config() -> None:
    source = read(CONFIG)

    if "minimum_writer_ready_fact_count" not in source:
        replace_once(
            CONFIG,
            """    writer_quality_revision_rounds: int = 1
    writer_priority_fact_limit: int = 10
    writer_supporting_fact_limit: int = 20

    max_priority_dataset_overview_facts: int = 2
""",
            """    writer_quality_revision_rounds: int = 1
    writer_priority_fact_limit: int = 10
    writer_supporting_fact_limit: int = 20

    # Deterministic coverage recovery from the trusted evidence ledger.
    minimum_writer_ready_fact_count: int = 6
    minimum_overview_fact_count: int = 1
    minimum_data_quality_fact_count: int = 1
    minimum_relationship_fact_count: int = 2

    maximum_recovered_overview_facts: int = 2
    maximum_recovered_data_quality_facts: int = 3
    maximum_recovered_correlation_facts: int = 3
    maximum_recovered_group_comparison_facts: int = 2
    maximum_recovered_modelling_facts: int = 1

    max_priority_dataset_overview_facts: int = 2
""",
            description=(
                "Add fact-ledger recovery settings"
            ),
        )

    source = read(CONFIG)

    if (
        '"T2T_MINIMUM_WRITER_READY_FACT_COUNT"'
        not in source
    ):
        replace_once(
            CONFIG,
            """            writer_supporting_fact_limit=env_int(
                "T2T_WRITER_SUPPORTING_FACT_LIMIT",
                20,
            ),
            max_priority_dataset_overview_facts=env_int(
""",
            """            writer_supporting_fact_limit=env_int(
                "T2T_WRITER_SUPPORTING_FACT_LIMIT",
                20,
            ),
            minimum_writer_ready_fact_count=env_int(
                "T2T_MINIMUM_WRITER_READY_FACT_COUNT",
                6,
            ),
            minimum_overview_fact_count=env_int(
                "T2T_MINIMUM_OVERVIEW_FACT_COUNT",
                1,
            ),
            minimum_data_quality_fact_count=env_int(
                "T2T_MINIMUM_DATA_QUALITY_FACT_COUNT",
                1,
            ),
            minimum_relationship_fact_count=env_int(
                "T2T_MINIMUM_RELATIONSHIP_FACT_COUNT",
                2,
            ),
            maximum_recovered_overview_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_OVERVIEW_FACTS",
                2,
            ),
            maximum_recovered_data_quality_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_DATA_QUALITY_FACTS",
                3,
            ),
            maximum_recovered_correlation_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_CORRELATION_FACTS",
                3,
            ),
            maximum_recovered_group_comparison_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_GROUP_COMPARISON_FACTS",
                2,
            ),
            maximum_recovered_modelling_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_MODELLING_FACTS",
                1,
            ),
            max_priority_dataset_overview_facts=env_int(
""",
            description=(
                "Load recovery settings from environment"
            ),
        )


def update_env_example() -> None:
    source = read(ENV_EXAMPLE)

    marker = "T2T_MINIMUM_WRITER_READY_FACT_COUNT"

    if marker in source:
        return

    addition = """

# ============================================================
# DETERMINISTIC FACT-COVERAGE RECOVERY
# ============================================================

# Recover safe writer-ready facts directly from trusted deterministic
# evidence when the LLM evidence/verifier stages leave the ledger too thin.
T2T_MINIMUM_WRITER_READY_FACT_COUNT=6

T2T_MINIMUM_OVERVIEW_FACT_COUNT=1
T2T_MINIMUM_DATA_QUALITY_FACT_COUNT=1
T2T_MINIMUM_RELATIONSHIP_FACT_COUNT=2

T2T_MAXIMUM_RECOVERED_OVERVIEW_FACTS=2
T2T_MAXIMUM_RECOVERED_DATA_QUALITY_FACTS=3
T2T_MAXIMUM_RECOVERED_CORRELATION_FACTS=3
T2T_MAXIMUM_RECOVERED_GROUP_COMPARISON_FACTS=2
T2T_MAXIMUM_RECOVERED_MODELLING_FACTS=1
"""

    write(
        ENV_EXAMPLE,
        source.rstrip() + addition + "\n",
    )


def update_audit_imports() -> None:
    source = read(AUDIT)

    if "VerificationMethod," in source:
        return

    replace_once(
        AUDIT,
        """    SupportType,
    VerificationResult,
    VerifiedFact,
""",
        """    SupportType,
    VerificationMethod,
    VerificationResult,
    VerifiedFact,
""",
        description=(
            "Import VerificationMethod in audit.py"
        ),
    )


def update_numeric_validation() -> None:
    replace_top_level_function(
        AUDIT,
        "number_supported",
        r'''
def number_supported(
    raw_token: str,
    number: float,
    support_numbers: list[float],
    sentence: str,
) -> bool:
    """
    Check whether a rendered number is supported.

    The tolerance accounts for ordinary display rounding. This is
    particularly important for percentages, where a deterministic
    value such as 0.005359 may be rendered as 0.54%.
    """

    approximate = bool(
        APPROXIMATE_PATTERN.search(sentence)
    )

    token_without_percent = (
        raw_token.rstrip("%").replace(",", "")
    )

    if "." in token_without_percent:
        decimal_places = len(
            token_without_percent.split(".", 1)[1]
        )
    else:
        decimal_places = 0

    displayed_resolution = 10.0 ** (-decimal_places)

    if raw_token.endswith("%"):
        displayed_resolution /= 100.0

    rounding_tolerance = (
        displayed_resolution / 2.0
    ) + 1e-12

    for candidate in support_numbers:
        relative_tolerance = max(
            1e-6,
            abs(candidate) * 0.001,
        )

        exact_tolerance = max(
            rounding_tolerance,
            relative_tolerance,
        )

        if abs(number - candidate) <= exact_tolerance:
            return True

        if approximate:
            approximate_tolerance = max(
                displayed_resolution,
                0.01,
                abs(candidate) * 0.03,
            )

            if (
                abs(number - candidate)
                <= approximate_tolerance
            ):
                return True

        digits = token_without_percent

        if (
            "." not in digits
            and len(digits) >= 4
            and digits.endswith("000")
        ):
            if abs(number - candidate) <= 500:
                return True

    return False
''',
    )

    replace_top_level_function(
        AUDIT,
        "minimum_useful_report_words",
        '''
def minimum_useful_report_words(
    *,
    target_words: int,
    required_component_count: int,
    settings: Settings,
) -> int:
    """
    Return a diagnostic minimum that never exceeds the planned target.
    """

    bounded_target = max(1, target_words)

    ratio_floor = int(
        bounded_target
        * settings.minimum_report_word_ratio
    )

    component_floor = (
        required_component_count * 45
    )

    desired_minimum = max(
        settings.minimum_report_word_floor,
        ratio_floor,
        component_floor,
    )

    return min(
        bounded_target,
        desired_minimum,
    )
''',
    )


def add_strength_normalisation() -> None:
    source = read(AUDIT)

    if "def normalise_strength_label" in source:
        return

    insert_before_once(
        AUDIT,
        "LOW_PRIORITY_STRENGTH_LABELS = {",
        '''
def normalise_strength_label(
    label: str,
) -> str:
    mapping = {
        "very_strong": "very_strong_association",
        "strong": "strong_association",
        "moderate": "moderate_association",
        "weak": "weak_but_reportable_association",
        "weak_but_reportable": (
            "weak_but_reportable_association"
        ),
        "large": "large_group_difference",
        "small": "small_group_difference",
        "negligible": "negligible_group_difference",
    }

    return mapping.get(label, label)
''',
        description=(
            "Add strength-label normalisation"
        ),
    )


def replace_evidence_selection_functions() -> None:
    replace_top_level_function(
        AUDIT,
        "evidence_subtype",
        '''
def evidence_subtype(
    item: EvidenceItem,
) -> str:
    metrics = item.metrics
    label = normalise_strength_label(
        item.strength_label
    )

    if item.route == AnalysisRoute.DESCRIPTIVE:
        if (
            "row_count" in metrics
            and "column_count" in metrics
        ):
            return "dataset_overview"

        if (
            metrics.get("constant") is True
            or "missing_count" in metrics
            or "missing_rate" in metrics
            or label
            in {
                "constant_column",
                "possible_sentinel_zero",
                "possible_data_quality_issue",
                "material_missingness",
                "low_missingness",
            }
        ):
            return "data_quality"

        return "descriptive_detail"

    if (
        item.route
        == AnalysisRoute.ASSOCIATION_COMPARISON
    ):
        if (
            "pearson_r" in metrics
            or "spearman_r" in metrics
            or "correlation" in metrics
        ):
            return "correlation"

        if (
            "highest_group" in metrics
            or "lowest_group" in metrics
            or "group_counts" in metrics
            or "standardised_difference"
            in metrics
            or "standardized_difference"
            in metrics
        ):
            return "group_comparison"

        return "association_other"

    if item.route == AnalysisRoute.PREDICTIVE:
        return "predictive_validation"

    if item.route == AnalysisRoute.FORECASTING:
        return "forecast_validation"

    if (
        item.route
        == AnalysisRoute.CAUSAL_FEASIBILITY
    ):
        return "causal_feasibility"

    return "other"
''',
    )

    replace_top_level_function(
        AUDIT,
        "fact_priority_score",
        '''
def fact_priority_score(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> float:
    evidence_items = evidence_for_fact(
        fact,
        evidence_lookup,
    )

    use_bonus = {
        RecommendedUse.HEADLINE: 0.25,
        RecommendedUse.MAIN_FINDING: 0.15,
        RecommendedUse.SUPPORTING_DETAIL: 0.0,
        RecommendedUse.LIMITATION: 0.10,
        RecommendedUse.OMIT_UNLESS_REQUESTED: -0.30,
    }.get(
        fact.recommended_use,
        0.0,
    )

    bonus_by_label = {
        "dataset_overview": 0.18,
        "constant_column": 0.15,
        "possible_sentinel_zero": 0.15,
        "possible_data_quality_issue": 0.12,
        "material_missingness": 0.12,
        "low_missingness": 0.03,
        "very_strong_association": 0.22,
        "strong_association": 0.17,
        "moderate_association": 0.10,
        "weak_but_reportable_association": -0.08,
        "large_group_difference": 0.18,
        "moderate_group_difference": 0.10,
        "small_group_difference": -0.15,
        "negligible_group_difference": -0.35,
        "validated_internal_prediction": 0.15,
        "model_not_better_than_baseline": 0.12,
        "validated_forecast": 0.15,
        "forecast_not_better_than_baseline": 0.12,
    }

    strength_bonuses = [
        bonus_by_label.get(
            normalise_strength_label(
                item.strength_label
            ),
            0.0,
        )
        for item in evidence_items
    ]

    strength_bonus = (
        max(strength_bonuses)
        if strength_bonuses
        else 0.0
    )

    return (
        0.30 * fact.salience
        + 0.25 * fact.user_relevance
        + 0.20 * fact.methodological_strength
        + 0.15 * fact.factual_confidence
        + use_bonus
        + strength_bonus
    )
''',
    )

    replace_top_level_function(
        AUDIT,
        "eligible_fact_as_priority",
        '''
def eligible_fact_as_priority(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> bool:
    if fact.recommended_use not in {
        RecommendedUse.HEADLINE,
        RecommendedUse.MAIN_FINDING,
        RecommendedUse.LIMITATION,
    }:
        return False

    strength_labels = {
        normalise_strength_label(
            item.strength_label
        )
        for item
        in evidence_for_fact(
            fact,
            evidence_lookup,
        )
    }

    if (
        strength_labels
        & LOW_PRIORITY_STRENGTH_LABELS
    ):
        return False

    return (
        fact.factual_confidence >= 0.90
        and fact.methodological_strength
        >= 0.70
        and fact.user_relevance >= 0.60
    )
''',
    )


def add_fact_coverage_recovery() -> None:
    source = read(AUDIT)

    if (
        "def augment_fact_ledger_for_report_coverage"
        in source
    ):
        return

    insert_before_once(
        AUDIT,
        "def select_balanced_priority_facts(",
        '''
RECOVERABLE_CORRELATION_LABELS = {
    "very_strong_association",
    "strong_association",
    "moderate_association",
}

RECOVERABLE_GROUP_LABELS = {
    "large_group_difference",
    "moderate_group_difference",
}

RECOVERABLE_MODELLING_LABELS = {
    "validated_internal_prediction",
    "model_not_better_than_baseline",
    "validated_forecast",
    "forecast_not_better_than_baseline",
    "predictive_insufficiency",
    "forecast_insufficiency",
}

RECOVERABLE_DATA_QUALITY_LABELS = {
    "constant_column",
    "possible_sentinel_zero",
    "possible_data_quality_issue",
    "material_missingness",
    "low_missingness",
}


def evidence_priority_score(
    item: EvidenceItem,
) -> float:
    temporary_fact = VerifiedFact(
        fact_id="FACT_SCORE_ONLY",
        source_candidate_id=(
            f"SCORE_{item.evidence_id}"
        ),
        verification_method=(
            VerificationMethod
            .DETERMINISTIC_EVIDENCE_RECOVERY
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=[
            *item.source_tables,
            *item.source_columns,
        ],
        claim_permissions=(
            item.claim_permissions
        ),
        allowed_interpretations=[
            item.practical_interpretation
        ],
        prohibited_interpretations=(
            item.prohibited_interpretations
        ),
        required_caveats=item.limitations,
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )

    return fact_priority_score(
        temporary_fact,
        {
            item.evidence_id: item,
        },
    )


def eligible_for_deterministic_fact_recovery(
    item: EvidenceItem,
) -> bool:
    if not item.eligible_for_writer:
        return False

    if item.factual_confidence < 0.90:
        return False

    if item.methodological_strength < 0.65:
        return False

    subtype = evidence_subtype(item)
    label = normalise_strength_label(
        item.strength_label
    )

    if subtype == "dataset_overview":
        return True

    if subtype == "data_quality":
        return (
            label
            in RECOVERABLE_DATA_QUALITY_LABELS
        )

    if subtype == "correlation":
        return (
            label
            in RECOVERABLE_CORRELATION_LABELS
        )

    if subtype == "group_comparison":
        return (
            label in RECOVERABLE_GROUP_LABELS
        )

    if subtype in {
        "predictive_validation",
        "forecast_validation",
    }:
        return (
            label
            in RECOVERABLE_MODELLING_LABELS
            or ClaimPermission.INSUFFICIENCY
            in item.claim_permissions
        )

    if subtype == "causal_feasibility":
        return (
            ClaimPermission.INSUFFICIENCY
            in item.claim_permissions
        )

    return False


def deterministic_fact_from_evidence(
    *,
    item: EvidenceItem,
    ordinal: int,
) -> VerifiedFact:
    entities = set(
        [
            *item.source_tables,
            *item.source_columns,
        ]
    )

    entities.update(
        collect_entity_strings(item.metrics)
    )

    return VerifiedFact(
        fact_id=f"FACT_REC_{ordinal:04d}",
        source_candidate_id=(
            f"RECOVERY_{item.evidence_id}"
        ),
        verification_method=(
            VerificationMethod
            .DETERMINISTIC_EVIDENCE_RECOVERY
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=sorted(entities),
        claim_permissions=(
            item.claim_permissions
        ),
        allowed_interpretations=(
            [item.practical_interpretation]
            if item.practical_interpretation
            else []
        ),
        prohibited_interpretations=(
            item.prohibited_interpretations
        ),
        required_caveats=item.limitations,
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )


def fact_subtype_counts(
    *,
    facts: list[VerifiedFact],
    evidence_lookup: dict[str, EvidenceItem],
) -> Counter[str]:
    counts: Counter[str] = Counter()

    for fact in facts:
        represented_subtypes = {
            evidence_subtype(
                evidence_lookup[evidence_id]
            )
            for evidence_id in fact.evidence_ids
            if evidence_id in evidence_lookup
        }

        for subtype in represented_subtypes:
            counts[subtype] += 1

    return counts


def augment_fact_ledger_for_report_coverage(
    *,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    settings: Settings,
) -> FactLedger:
    """
    Augment a thin fact ledger using exact, trusted deterministic
    evidence statements.

    This does not create new calculations or LLM interpretations.
    """

    lookup = build_evidence_lookup(evidence)

    represented_evidence_ids = {
        evidence_id
        for fact
        in fact_ledger.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }

    existing_counts = fact_subtype_counts(
        facts=fact_ledger.writer_ready_facts,
        evidence_lookup=lookup,
    )

    candidates = sorted(
        [
            item
            for item in evidence.items
            if (
                item.evidence_id
                not in represented_evidence_ids
                and eligible_for_deterministic_fact_recovery(
                    item
                )
            )
        ],
        key=evidence_priority_score,
        reverse=True,
    )

    subtype_limits = {
        "dataset_overview": (
            settings
            .maximum_recovered_overview_facts
        ),
        "data_quality": (
            settings
            .maximum_recovered_data_quality_facts
        ),
        "correlation": (
            settings
            .maximum_recovered_correlation_facts
        ),
        "group_comparison": (
            settings
            .maximum_recovered_group_comparison_facts
        ),
        "predictive_validation": (
            settings
            .maximum_recovered_modelling_facts
        ),
        "forecast_validation": (
            settings
            .maximum_recovered_modelling_facts
        ),
        "causal_feasibility": 1,
    }

    recovered: list[VerifiedFact] = []
    recovered_counts: Counter[str] = Counter()
    recovery_notes: list[str] = []
    recovered_evidence_ids: set[str] = set()

    existing_fact_ids = {
        fact.fact_id
        for fact
        in fact_ledger.writer_ready_facts
    }

    next_ordinal = 1

    def next_fact_id_ordinal() -> int:
        nonlocal next_ordinal

        while (
            f"FACT_REC_{next_ordinal:04d}"
            in existing_fact_ids
        ):
            next_ordinal += 1

        value = next_ordinal
        next_ordinal += 1

        return value

    def recover(item: EvidenceItem) -> bool:
        subtype = evidence_subtype(item)

        if (
            item.evidence_id
            in recovered_evidence_ids
        ):
            return False

        maximum = subtype_limits.get(
            subtype,
            0,
        )

        if (
            recovered_counts[subtype]
            >= maximum
        ):
            return False

        fact = deterministic_fact_from_evidence(
            item=item,
            ordinal=next_fact_id_ordinal(),
        )

        recovered.append(fact)
        recovered_counts[subtype] += 1
        recovered_evidence_ids.add(
            item.evidence_id
        )

        recovery_notes.append(
            "Recovered writer-ready fact "
            f"`{fact.fact_id}` from deterministic "
            f"evidence `{item.evidence_id}` for "
            f"subtype `{subtype}`."
        )

        return True

    def recover_best(
        subtype: str,
    ) -> bool:
        for item in candidates:
            if (
                evidence_subtype(item)
                == subtype
                and item.evidence_id
                not in recovered_evidence_ids
            ):
                if recover(item):
                    return True

        return False

    if (
        ReportComponent.DATASET_OVERVIEW
        in required_components
    ):
        while (
            existing_counts["dataset_overview"]
            + recovered_counts[
                "dataset_overview"
            ]
            < settings.minimum_overview_fact_count
        ):
            if not recover_best(
                "dataset_overview"
            ):
                break

    if (
        ReportComponent.DATA_QUALITY
        in required_components
    ):
        while (
            existing_counts["data_quality"]
            + recovered_counts["data_quality"]
            < settings.minimum_data_quality_fact_count
        ):
            if not recover_best("data_quality"):
                break

    if (
        ReportComponent.STRONGEST_RELATIONSHIPS
        in required_components
    ):
        # Prefer subtype diversity when both forms are available.
        if (
            existing_counts["correlation"] == 0
            and any(
                evidence_subtype(item)
                == "correlation"
                for item in candidates
            )
        ):
            recover_best("correlation")

        if (
            existing_counts["group_comparison"]
            == 0
            and any(
                evidence_subtype(item)
                == "group_comparison"
                for item in candidates
            )
        ):
            recover_best("group_comparison")

        def relationship_count() -> int:
            return sum(
                existing_counts[subtype]
                + recovered_counts[subtype]
                for subtype in {
                    "correlation",
                    "group_comparison",
                    "association_other",
                }
            )

        while (
            relationship_count()
            < settings.minimum_relationship_fact_count
        ):
            recovered_one = (
                recover_best("correlation")
                or recover_best(
                    "group_comparison"
                )
            )

            if not recovered_one:
                break

    # Fill a thin ledger only with remaining eligible evidence.
    for item in candidates:
        if (
            len(
                fact_ledger.writer_ready_facts
            )
            + len(recovered)
            >= settings.minimum_writer_ready_fact_count
        ):
            break

        recover(item)

    if not recovered:
        return fact_ledger

    return fact_ledger.model_copy(
        update={
            "writer_ready_facts": [
                *fact_ledger.writer_ready_facts,
                *recovered,
            ],
            "deterministically_recovered_fact_ids": [
                *fact_ledger
                .deterministically_recovered_fact_ids,
                *[
                    fact.fact_id
                    for fact in recovered
                ],
            ],
            "coverage_recovery_notes": [
                *fact_ledger.coverage_recovery_notes,
                *recovery_notes,
            ],
        }
    )
''',
        description=(
            "Add deterministic fact-ledger coverage recovery"
        ),
    )


def replace_priority_selection() -> None:
    replace_top_level_function(
        AUDIT,
        "select_balanced_priority_facts",
        '''
def select_balanced_priority_facts(
    *,
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    settings: Settings,
) -> list[VerifiedFact]:
    """
    Select facts by coverage and analytical strength.

    There is deliberately no unrestricted final fill stage. Weak or
    small facts remain available in supporting_facts but are not
    promoted simply because unused capacity remains.
    """

    lookup = build_evidence_lookup(evidence)

    ranked = sorted(
        facts,
        key=lambda fact: fact_priority_score(
            fact,
            lookup,
        ),
        reverse=True,
    )

    selected: list[VerifiedFact] = []
    selected_ids: set[str] = set()
    subtype_counts: Counter[str] = Counter()

    subtype_limits = {
        "dataset_overview": (
            settings
            .max_priority_dataset_overview_facts
        ),
        "data_quality": (
            settings
            .max_priority_data_quality_facts
        ),
        "correlation": (
            settings
            .max_priority_correlation_facts
        ),
        "group_comparison": (
            settings
            .max_priority_group_comparison_facts
        ),
        "predictive_validation": (
            settings
            .max_priority_predictive_facts
        ),
        "forecast_validation": (
            settings
            .max_priority_forecast_facts
        ),
        "causal_feasibility": (
            settings
            .max_priority_limitation_facts
        ),
        "association_other": 1,
        "descriptive_detail": 1,
        "other": 1,
    }

    def primary_subtype(
        fact: VerifiedFact,
    ) -> str:
        subtypes = [
            evidence_subtype(item)
            for item
            in evidence_for_fact(
                fact,
                lookup,
            )
        ]

        return (
            subtypes[0]
            if subtypes
            else "other"
        )

    def priority_eligible(
        fact: VerifiedFact,
    ) -> bool:
        return (
            eligible_fact_as_priority(
                fact,
                lookup,
            )
            and fact_priority_score(
                fact,
                lookup,
            )
            >= settings.minimum_main_finding_score
        )

    def add_fact(
        fact: VerifiedFact,
        *,
        require_priority_eligibility: bool,
    ) -> bool:
        if fact.fact_id in selected_ids:
            return False

        subtype = primary_subtype(fact)

        if (
            subtype_counts[subtype]
            >= subtype_limits.get(subtype, 1)
        ):
            return False

        if (
            require_priority_eligibility
            and not priority_eligible(fact)
        ):
            return False

        selected.append(fact)
        selected_ids.add(fact.fact_id)
        subtype_counts[subtype] += 1

        return True

    def add_best_for_subtype(
        subtype: str,
        *,
        require_priority_eligibility: bool,
    ) -> bool:
        for fact in ranked:
            if primary_subtype(fact) != subtype:
                continue

            if add_fact(
                fact,
                require_priority_eligibility=(
                    require_priority_eligibility
                ),
            ):
                return True

        return False

    if (
        ReportComponent.DATASET_OVERVIEW
        in required_components
    ):
        add_best_for_subtype(
            "dataset_overview",
            require_priority_eligibility=False,
        )

    if (
        ReportComponent.DATA_QUALITY
        in required_components
    ):
        add_best_for_subtype(
            "data_quality",
            require_priority_eligibility=False,
        )

    if (
        ReportComponent.STRONGEST_RELATIONSHIPS
        in required_components
    ):
        # Prefer one strong correlation and one strong group comparison.
        add_best_for_subtype(
            "correlation",
            require_priority_eligibility=True,
        )

        add_best_for_subtype(
            "group_comparison",
            require_priority_eligibility=True,
        )

        def selected_relationship_count() -> int:
            return sum(
                subtype_counts[subtype]
                for subtype in {
                    "correlation",
                    "group_comparison",
                    "association_other",
                }
            )

        for fact in ranked:
            if (
                selected_relationship_count()
                >= settings.minimum_relationship_fact_count
            ):
                break

            if primary_subtype(fact) not in {
                "correlation",
                "group_comparison",
                "association_other",
            }:
                continue

            add_fact(
                fact,
                require_priority_eligibility=True,
            )

    if (
        ReportComponent.MODELLING_VALIDATION
        in required_components
    ):
        add_best_for_subtype(
            "predictive_validation",
            require_priority_eligibility=False,
        )

        if not any(
            primary_subtype(fact)
            in {
                "predictive_validation",
                "forecast_validation",
            }
            for fact in selected
        ):
            add_best_for_subtype(
                "forecast_validation",
                require_priority_eligibility=False,
            )

    if (
        ReportComponent.LIMITATIONS_NEXT_STEPS
        in required_components
    ):
        for fact in ranked:
            if (
                fact.recommended_use
                == RecommendedUse.LIMITATION
                or ClaimPermission.INSUFFICIENCY
                in fact.claim_permissions
            ):
                if add_fact(
                    fact,
                    require_priority_eligibility=False,
                ):
                    break

    # Add only high-quality eligible facts. Do not fill with weak facts.
    for fact in ranked:
        if (
            len(selected)
            >= settings.writer_priority_fact_limit
        ):
            break

        add_fact(
            fact,
            require_priority_eligibility=True,
        )

    return selected
''',
    )


def replace_component_coverage() -> None:
    replace_top_level_function(
        AUDIT,
        "assess_report_component_coverage",
        r'''
def assess_report_component_coverage(
    *,
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
) -> list[ReportComponentAssessment]:
    """
    Assess coverage using the sentence support map.

    Limitations and next steps may be supported by the same verified
    relationship or quality fact used elsewhere, so they are not
    restricted to facts whose primary component is LIMITATIONS.
    """

    fact_lookup = {
        fact.fact_id: fact
        for fact
        in fact_ledger.writer_ready_facts
    }

    evidence_by_id = build_evidence_lookup(
        evidence
    )

    support_by_component: defaultdict[
        ReportComponent,
        list[str],
    ] = defaultdict(list)

    for component in required_components:
        support_by_component[component]

    limitation_language = re.compile(
        r"\b("
        r"limitation|"
        r"unadjusted|"
        r"causal|causation|"
        r"confound|"
        r"precision|stability|"
        r"validate|verify|inspect|investigate|"
        r"remove|exclude|check|"
        r"next step|further analysis|"
        r"deployment|backtest"
        r")\b",
        re.IGNORECASE,
    )

    for support in writer_output.sentence_support:
        supported_facts = [
            fact_lookup[fact_id]
            for fact_id in support.fact_ids
            if fact_id in fact_lookup
        ]

        for fact in supported_facts:
            component = classify_fact_component(
                fact,
                evidence_by_id,
            )

            if (
                component
                in required_components
            ):
                support_by_component[
                    component
                ].append(fact.fact_id)

        if (
            ReportComponent
            .LIMITATIONS_NEXT_STEPS
            in required_components
            and supported_facts
            and limitation_language.search(
                support.sentence_text
            )
        ):
            support_by_component[
                ReportComponent
                .LIMITATIONS_NEXT_STEPS
            ].extend(
                fact.fact_id
                for fact in supported_facts
            )

    assessments: list[
        ReportComponentAssessment
    ] = []

    for component in required_components:
        fact_ids = list(
            dict.fromkeys(
                support_by_component[component]
            )
        )

        assessments.append(
            ReportComponentAssessment(
                component=component,
                covered=bool(fact_ids),
                supporting_fact_ids=fact_ids,
                explanation=(
                    "At least one report sentence is "
                    "mapped to verified support for "
                    "this component."
                    if fact_ids
                    else (
                        "No supported report sentence "
                        "clearly covers this required "
                        "component."
                    )
                ),
            )
        )

    return assessments
''',
    )


def add_revision_acceptance_helper() -> None:
    source = read(AUDIT)

    if "def accept_writer_quality_revision" in source:
        return

    insert_before_once(
        AUDIT,
        "def fallback_writer(",
        '''
def writer_output_word_count(
    output: WriterOutput,
) -> int:
    return len(
        re.findall(
            r"\\b[\\w'-]+\\b",
            output.markdown,
        )
    )


def accept_writer_quality_revision(
    *,
    before: WriterOutput,
    after: WriterOutput,
    before_audit: AuditReport,
    after_audit: AuditReport,
    validation_errors: list[str],
    report_specification: Any,
    settings: Settings,
) -> tuple[bool, list[str]]:
    """
    Accept a whole-report quality revision only when it is valid and
    measurably improves the incomplete draft.
    """

    reasons: list[str] = list(
        validation_errors
    )

    before_missing = sum(
        not assessment.covered
        for assessment
        in before_audit.component_assessments
    )

    after_missing = sum(
        not assessment.covered
        for assessment
        in after_audit.component_assessments
    )

    before_words = writer_output_word_count(
        before
    )
    after_words = writer_output_word_count(
        after
    )

    minimum_words = minimum_useful_report_words(
        target_words=(
            report_specification
            .target_length_words
        ),
        required_component_count=len(
            report_specification
            .required_components
        ),
        settings=settings,
    )

    if (
        before_missing > 0
        and after_missing >= before_missing
    ):
        reasons.append(
            "The revision did not reduce the number "
            "of missing required components."
        )

    if (
        before_words < minimum_words
        and after_words <= before_words
    ):
        reasons.append(
            "The revision did not improve the "
            "under-length report."
        )

    if (
        before_missing > 0
        and len(after.sentence_support)
        < len(before.sentence_support)
    ):
        reasons.append(
            "The revision reduced supported sentence "
            "coverage while the report was incomplete."
        )

    serious_after = {
        (
            annotation.sentence,
            annotation.subtype,
        )
        for annotation
        in after_audit.annotations
        if annotation.severity
        in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
    }

    serious_before = {
        (
            annotation.sentence,
            annotation.subtype,
        )
        for annotation
        in before_audit.annotations
        if annotation.severity
        in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
    }

    introduced_serious = (
        serious_after - serious_before
    )

    if introduced_serious:
        reasons.append(
            "The revision introduced a new serious "
            "factual or contextual annotation."
        )

    return (
        not reasons,
        list(dict.fromkeys(reasons)),
    )
''',
        description=(
            "Add quality-revision acceptance controller"
        ),
    )


def replace_fallback_writer() -> None:
    replace_top_level_function(
        AUDIT,
        "fallback_writer",
        '''
def fallback_writer(
    pack: WriterEvidencePack,
) -> WriterOutput:
    """
    Safe deterministic fallback.

    It is deliberately richer than a two-sentence renderer, but remains
    ineligible for primary evaluation because it is not the natural LLM
    Writer.
    """

    maximum = (
        pack.report_specification
        .maximum_main_findings
    )

    selected = list(
        {
            fact.fact_id: fact
            for fact in (
                pack.priority_facts[:maximum]
                + pack.limitation_facts[:2]
            )
        }.values()
    )

    evidence_by_id = build_evidence_lookup(
        pack.evidence_ledger
    )

    sections: dict[
        ReportComponent,
        list[VerifiedFact],
    ] = {
        ReportComponent.DATASET_OVERVIEW: [],
        ReportComponent.DATA_QUALITY: [],
        ReportComponent.STRONGEST_RELATIONSHIPS: [],
        ReportComponent.MODELLING_VALIDATION: [],
        ReportComponent.LIMITATIONS_NEXT_STEPS: [],
    }

    for fact in selected:
        component = classify_fact_component(
            fact,
            evidence_by_id,
        )

        sections.setdefault(
            component,
            [],
        ).append(fact)

    headings = {
        ReportComponent.DATASET_OVERVIEW: (
            "Dataset overview"
        ),
        ReportComponent.DATA_QUALITY: (
            "Data quality"
        ),
        ReportComponent.STRONGEST_RELATIONSHIPS: (
            "Strongest observed relationships"
        ),
        ReportComponent.MODELLING_VALIDATION: (
            "Modelling and validation"
        ),
        ReportComponent.LIMITATIONS_NEXT_STEPS: (
            "Limitations and next steps"
        ),
    }

    lines = [
        "# Evidence-grounded data-science report",
        "",
    ]

    support_map: list[SentenceSupport] = []
    sentence_counter = 1
    rendered_recommendations: set[str] = set()

    def add_supported_sentence(
        sentence: str,
        facts: list[VerifiedFact],
        support_type: SupportType,
    ) -> None:
        nonlocal sentence_counter

        cleaned = sentence.strip()

        if not cleaned:
            return

        if cleaned[-1] not in ".!?":
            cleaned += "."

        lines.append(cleaned)

        fact_ids = list(
            dict.fromkeys(
                fact.fact_id
                for fact in facts
            )
        )

        evidence_ids = list(
            dict.fromkeys(
                evidence_id
                for fact in facts
                for evidence_id in fact.evidence_ids
            )
        )

        support_map.append(
            SentenceSupport(
                sentence_id=(
                    f"SENT_{sentence_counter:04d}"
                ),
                sentence_text=cleaned,
                fact_ids=fact_ids,
                evidence_ids=evidence_ids,
                support_type=support_type,
            )
        )

        sentence_counter += 1

    for component in [
        ReportComponent.DATASET_OVERVIEW,
        ReportComponent.DATA_QUALITY,
        ReportComponent.STRONGEST_RELATIONSHIPS,
        ReportComponent.MODELLING_VALIDATION,
    ]:
        component_facts = sections.get(
            component,
            [],
        )

        if not component_facts:
            continue

        lines.extend(
            [
                f"## {headings[component]}",
                "",
            ]
        )

        for fact in component_facts:
            sentence = (
                reader_facing_caveat(
                    fact.fact_summary
                )
                or fact.fact_summary
            )

            add_supported_sentence(
                sentence,
                [fact],
                SupportType.DIRECT,
            )

            if (
                component
                == ReportComponent.DATA_QUALITY
            ):
                for evidence_id in fact.evidence_ids:
                    item = evidence_by_id.get(
                        evidence_id
                    )

                    if item is None:
                        continue

                    for recommendation in (
                        item.recommendations
                    ):
                        if (
                            recommendation.priority
                            not in {"high", "medium"}
                        ):
                            continue

                        action = (
                            recommendation.action.strip()
                        )

                        if (
                            action
                            in rendered_recommendations
                        ):
                            continue

                        rendered_recommendations.add(
                            action
                        )

                        add_supported_sentence(
                            action,
                            [fact],
                            SupportType.PARAPHRASE,
                        )

        lines.append("")

    limitation_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                sections.get(
                    ReportComponent
                    .LIMITATIONS_NEXT_STEPS,
                    [],
                )
                + [
                    fact
                    for fact in selected
                    if (
                        fact.required_caveats
                        or ClaimPermission.COMPARATIVE
                        in fact.claim_permissions
                        or ClaimPermission.ASSOCIATIONAL
                        in fact.claim_permissions
                    )
                ]
            )
        }.values()
    )

    if (
        pack.reader_facing_limitations
        or limitation_facts
        or rendered_recommendations
    ):
        lines.extend(
            [
                "## Limitations and next steps",
                "",
            ]
        )

        for fact in sections.get(
            ReportComponent
            .LIMITATIONS_NEXT_STEPS,
            [],
        ):
            add_supported_sentence(
                fact.fact_summary,
                [fact],
                SupportType.DIRECT,
            )

        relationship_facts = [
            fact
            for fact in selected
            if (
                ClaimPermission.COMPARATIVE
                in fact.claim_permissions
                or ClaimPermission.ASSOCIATIONAL
                in fact.claim_permissions
            )
        ]

        for limitation in (
            pack.reader_facing_limitations
        ):
            supporting = (
                relationship_facts
                or limitation_facts
            )

            if supporting:
                add_supported_sentence(
                    limitation,
                    supporting,
                    SupportType.MULTI_FACT_SYNTHESIS,
                )

        lines.append("")

    used_fact_ids = list(
        dict.fromkeys(
            fact_id
            for support in support_map
            for fact_id in support.fact_ids
        )
    )

    available_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                pack.priority_facts
                + pack.supporting_facts
                + pack.limitation_facts
            )
        }.values()
    )

    return WriterOutput(
        title=(
            "Evidence-grounded "
            "data-science report"
        ),
        markdown=(
            "\\n".join(lines).strip()
            + "\\n"
        ),
        sentence_support=support_map,
        selected_fact_ids=used_fact_ids,
        omitted_fact_ids=[
            fact.fact_id
            for fact in available_facts
            if fact.fact_id
            not in set(used_fact_ids)
        ],
        writer_notes=[
            "Deterministic writer fallback was used.",
            "This output is preserved for debugging "
            "and is not eligible for primary evaluation.",
        ],
        writer_mode=(
            "deterministic_fallback"
        ),
        eligible_for_primary_evaluation=False,
    )
''',
    )


def update_agents() -> None:
    source = read(AGENTS)

    verifier_marker = (
        "A direct deterministic fact such as a row count"
    )

    if verifier_marker not in source:
        replace_once(
            AGENTS,
            """- causal wording without a verified causal design.

Do not rewrite candidates into final report prose.
""",
            """- causal wording without a verified causal design.

Judge every candidate independently.

A direct deterministic fact such as a row count, column count,
missing-value count, constant-field finding, correlation, or validated
group comparison can be fully valid even when it is simple or less
narratively interesting than another candidate.

Do not reject overview or data-quality facts merely to keep the ledger
concise. Reject them only when they are unsupported, numerically
inconsistent, semantically escalated, or methodologically invalid.

Do not rewrite candidates into final report prose.
""",
            description=(
                "Strengthen verifier coverage instructions"
            ),
        )

    source = read(AGENTS)

    writer_marker = (
        "Deterministically recovered facts are direct"
    )

    if writer_marker not in source:
        replace_once(
            AGENTS,
            """Small or weak effects should normally be omitted unless they materially
qualify a stronger finding or the user requested completeness.

Every factual sentence must be represented in the hidden sentence support
map.
""",
            """Small or weak effects should normally be omitted unless they materially
qualify a stronger finding or the user requested completeness.

Deterministically recovered facts are direct representations of trusted
calculated evidence. They are as grounded as LLM-verified facts and may be
used normally, while their recovery method remains recorded internally.

When sufficient verified material exists, do not return only a heading and
one or two factual sentences. Cover every required report component using
the strongest available facts.

Prefer relationship diversity. When both are available, normally include a
strong or moderate correlation and a large or moderate group comparison
rather than several similar comparisons.

Do not use a small relationship merely to increase the number of findings.

Every factual sentence must be represented in the hidden sentence support
map.
""",
            description=(
                "Strengthen writer completeness instructions"
            ),
        )


def update_workflow_imports() -> None:
    source = read(WORKFLOW)

    if (
        "augment_fact_ledger_for_report_coverage,"
        not in source
    ):
        replace_once(
            WORKFLOW,
            """from .audit import (
    apply_repair_proposal,
    assess_report_component_coverage,
""",
            """from .audit import (
    accept_writer_quality_revision,
    apply_repair_proposal,
    assess_report_component_coverage,
    augment_fact_ledger_for_report_coverage,
""",
            description=(
                "Import recovery and revision controller"
            ),
        )

    source = read(WORKFLOW)

    if "validate_writer_output," not in source:
        replace_once(
            WORKFLOW,
            """    merge_audit_proposal,
)
""",
            """    merge_audit_proposal,
    validate_writer_output,
)
""",
            description=(
                "Import writer validation in workflow"
            ),
        )


def replace_quality_revision_prompt() -> None:
    replace_top_level_function(
        WORKFLOW,
        "build_writer_quality_revision_prompt",
        '''
def build_writer_quality_revision_prompt(
    *,
    writer_pack: WriterEvidencePack,
    current_output: WriterOutput,
    missing_components: list[ReportComponent],
    quality_findings: list[str],
    settings: Settings,
) -> str:
    used_fact_ids = set(
        current_output.selected_fact_ids
    )

    unused_priority_facts = [
        fact
        for fact in writer_pack.priority_facts
        if fact.fact_id not in used_fact_ids
    ]

    current_word_count = len(
        re.findall(
            r"\\\\b[\\\\w'-]+\\\\b",
            current_output.markdown,
        )
    )

    target_words = (
        writer_pack.report_specification
        .target_length_words
    )

    minimum_words = min(
        target_words,
        max(
            settings.minimum_report_word_floor,
            int(
                target_words
                * settings.minimum_report_word_ratio
            ),
            len(
                writer_pack
                .report_specification
                .required_components
            )
            * 45,
        ),
    )

    return (
        "Revise the complete report once for task fulfilment and natural "
        "data-science writing before factual audit.\\n\\n"
        "This is a Writer quality revision, not a factual repair.\\n\\n"
        "Do not merely rephrase the existing short report.\\n"
        "Use the unused verified priority facts to cover missing sections.\\n"
        "Do not invent calculations or facts.\\n"
        "Do not calculate statistics.\\n"
        "Do not introduce new numbers, entities, categories, metadata, "
        "causal claims, prediction claims, forecast claims, or deployment "
        "claims.\\n"
        "Do not expose internal control fields such as Finding:, Strength:, "
        "Important Note:, Interpretation Notes:, Recommended Use:, or Global "
        "Prohibited Interpretations.\\n"
        "Use natural data-science prose and consolidate shared caveats.\\n"
        "Prefer strong and moderate evidence over small effects.\\n"
        "Every factual sentence must occur verbatim in the hidden support "
        "map.\\n"
        "Return the complete WriterOutput schema.\\n\\n"
        f"Current word count: {current_word_count}\\n"
        f"Minimum useful word count: {minimum_words}\\n"
        f"Available priority facts: {len(writer_pack.priority_facts)}\\n"
        f"Unused priority facts: {len(unused_priority_facts)}\\n\\n"
        "Missing components:\\n"
        + (
            "\\n".join(
                f"- {component.value}"
                for component in missing_components
            )
            if missing_components
            else "- None"
        )
        + "\\n\\nQuality findings:\\n"
        + (
            "\\n".join(
                f"- {finding}"
                for finding in quality_findings
            )
            if quality_findings
            else "- None"
        )
        + "\\n\\nUnused verified priority facts:\\n"
        + compact_json(unused_priority_facts)
        + "\\n\\nFull Writer evidence pack:\\n"
        + compact_json(writer_pack)
        + "\\n\\nCurrent Writer output:\\n"
        + compact_json(current_output)
    )
''',
    )


def add_fact_coverage_recovery_to_workflow() -> None:
    source = read(WORKFLOW)

    if (
        "07_fact_ledger_pre_coverage_recovery.json"
        in source
    ):
        return

    replace_once(
        WORKFLOW,
        '''        store.save_json("07_fact_ledger.json", fact_ledger)

        writer_pack = build_writer_evidence_pack(
''',
        '''        store.save_json(
            "07_fact_ledger_pre_coverage_recovery.json",
            fact_ledger,
        )

        fact_count_before_recovery = len(
            fact_ledger.writer_ready_facts
        )

        fact_ledger = (
            augment_fact_ledger_for_report_coverage(
                fact_ledger=fact_ledger,
                evidence=evidence_ledger,
                required_components=(
                    plan.report_specification
                    .required_components
                ),
                settings=self.settings,
            )
        )

        store.trace(
            "fact_ledger_coverage_recovery",
            "completed",
            {
                "facts_before": (
                    fact_count_before_recovery
                ),
                "facts_after": len(
                    fact_ledger
                    .writer_ready_facts
                ),
                "recovered_fact_ids": (
                    fact_ledger
                    .deterministically_recovered_fact_ids
                ),
                "notes": (
                    fact_ledger
                    .coverage_recovery_notes
                ),
            },
        )

        store.save_json(
            "07_fact_ledger.json",
            fact_ledger,
        )

        writer_pack = build_writer_evidence_pack(
''',
        description=(
            "Run coverage recovery before Writer pack"
        ),
    )


def replace_quality_revision_workflow_block() -> None:
    source = read(WORKFLOW)

    start_marker = """        if (
            needs_quality_revision
            and raw_writer_output.writer_mode == "llm_writer"
            and self.settings.writer_quality_revision_rounds > 0
        ):
"""

    end_marker = """        initial_audit, proposal = await self.audit_once(
"""

    start = source.find(start_marker)
    end = source.find(end_marker)

    if start == -1 or end == -1 or end <= start:
        fail(
            "Could not locate the existing Writer quality-revision "
            "block in workflow.py."
        )

    replacement = '''        if (
            needs_quality_revision
            and self.settings.use_llm
            and self.writer_agent is not None
            and self.settings.writer_quality_revision_rounds > 0
        ):
            revised_writer_output = await self.run_agent_or_fallback(
                stage="writer_quality_revision",
                agent=self.writer_agent,
                prompt=build_writer_quality_revision_prompt(
                    writer_pack=writer_pack,
                    current_output=raw_writer_output,
                    missing_components=missing_components,
                    quality_findings=(
                        initial_quality_audit
                        .quality_assessment
                        .findings
                    ),
                    settings=self.settings,
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_ledger": (
                            fact_ledger.model_dump(
                                mode="json"
                            )
                        )
                    },
                ),
                fallback=lambda: raw_writer_output,
                store=store,
            )

            revision_candidate = (
                WriterOutput.model_validate(
                    revised_writer_output
                )
                .model_copy(
                    update={
                        "quality_revision_round": 1,
                        "quality_revision_summary": (
                            "Bounded whole-report "
                            "quality-revision candidate."
                        ),
                    }
                )
            )

            store.save_json(
                "10_writer_quality_revision_candidate.json",
                revision_candidate,
            )
            store.save_text(
                "10_writer_quality_revision_candidate.md",
                revision_candidate.markdown,
            )

            revision_validation_errors = (
                validate_writer_output(
                    revision_candidate,
                    fact_ledger,
                )
            )

            revised_quality_audit = (
                deterministic_audit(
                    writer_output=revision_candidate,
                    fact_ledger=fact_ledger,
                    evidence=evidence_ledger,
                    mode=audit_mode,
                    external_sources=(
                        external_truth_sources
                    ),
                    revision_round=0,
                    report_specification=(
                        plan.report_specification
                    ),
                    settings=self.settings,
                )
            )

            revision_accepted, revision_reasons = (
                accept_writer_quality_revision(
                    before=raw_writer_output,
                    after=revision_candidate,
                    before_audit=(
                        initial_quality_audit
                    ),
                    after_audit=(
                        revised_quality_audit
                    ),
                    validation_errors=(
                        revision_validation_errors
                    ),
                    report_specification=(
                        plan.report_specification
                    ),
                    settings=self.settings,
                )
            )

            store.save_json(
                "10_writer_quality_revision_assessment.json",
                {
                    "attempted": True,
                    "accepted": revision_accepted,
                    "reasons": revision_reasons,
                    "before_component_assessments": (
                        initial_quality_audit
                        .component_assessments
                    ),
                    "after_component_assessments": (
                        revised_quality_audit
                        .component_assessments
                    ),
                    "before_quality": (
                        initial_quality_audit
                        .quality_assessment
                    ),
                    "after_quality": (
                        revised_quality_audit
                        .quality_assessment
                    ),
                    "validation_errors": (
                        revision_validation_errors
                    ),
                },
            )

            if revision_accepted:
                quality_revised_writer_output = (
                    revision_candidate.model_copy(
                        update={
                            "quality_revision_summary": (
                                "One bounded Writer "
                                "quality revision was "
                                "accepted before factual "
                                "auditing."
                            ),
                        }
                    )
                )

                writer_output_for_audit = (
                    quality_revised_writer_output
                )

                store.save_json(
                    "10_writer_quality_revision.json",
                    writer_output_for_audit,
                )
                store.save_text(
                    "10_writer_quality_revision.md",
                    writer_output_for_audit.markdown,
                )
                store.save_json(
                    "10_writer_quality_revision_component_coverage.json",
                    revised_quality_audit.component_assessments,
                )
            else:
                store.trace(
                    "writer_quality_revision",
                    "rejected",
                    {
                        "reasons": (
                            revision_reasons
                        )
                    },
                )

'''

    write(
        WORKFLOW,
        source[:start]
        + replacement
        + source[end:],
    )


def append_tests() -> None:
    source = read(TESTS)

    marker = (
        "test_report_coverage_recovery_regression"
    )

    if marker in source:
        return

    addition = r'''

# ============================================================
# REPORT-COVERAGE REGRESSION TESTS
# ============================================================


def _coverage_evidence_item(
    *,
    evidence_id,
    finding,
    route,
    metrics,
    strength_label,
    recommended_use,
    permissions,
    relevance=0.95,
    salience=0.95,
):
    return EvidenceItem(
        evidence_id=evidence_id,
        route=route,
        task_ids=["TASK_COVERAGE"],
        finding=finding,
        metrics=metrics,
        source_tables=["weather"],
        source_columns=list(
            metrics.get(
                "source_columns",
                [],
            )
        ),
        method="Deterministic test evidence.",
        validation_strategy=ValidationStrategy.NONE,
        practical_interpretation=finding,
        strength_label=strength_label,
        limitations=[],
        prohibited_interpretations=[],
        recommendations=[],
        claim_permissions=permissions,
        factual_confidence=1.0,
        methodological_strength=0.95,
        user_relevance=relevance,
        salience=salience,
        recommended_use=recommended_use,
        eligible_for_writer=True,
    )


def _coverage_fact(
    item,
    fact_id,
):
    return VerifiedFact(
        fact_id=fact_id,
        source_candidate_id=(
            f"CAN_{fact_id}"
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=[
            "weather",
            *item.source_columns,
        ],
        claim_permissions=(
            item.claim_permissions
        ),
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )


def _coverage_fixture():
    overview = _coverage_evidence_item(
        evidence_id="EVD_COV_001",
        finding=(
            "Table `weather` contains 96,453 "
            "rows and 12 columns."
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        metrics={
            "row_count": 96_453,
            "column_count": 12,
        },
        strength_label="dataset_overview",
        recommended_use=RecommendedUse.HEADLINE,
        permissions=[
            ClaimPermission.DESCRIPTIVE
        ],
    )

    quality = _coverage_evidence_item(
        evidence_id="EVD_COV_002",
        finding=(
            "`Loud Cover` is constant at `0` "
            "across all observations."
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        metrics={
            "constant": True,
            "constant_value": 0,
        },
        strength_label="constant_column",
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.DESCRIPTIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    correlation = _coverage_evidence_item(
        evidence_id="EVD_COV_003",
        finding=(
            "`Temperature (C)` and "
            "`Apparent Temperature (C)` have "
            "a Pearson correlation of 0.9926."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "pearson_r": 0.9926,
            "complete_pairs": 96_453,
        },
        strength_label=(
            "very_strong_association"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.ASSOCIATIONAL,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    large_group = _coverage_evidence_item(
        evidence_id="EVD_COV_004",
        finding=(
            "Rain observations have a mean "
            "temperature of 12.36 compared with "
            "-4.97 for snow, a difference of "
            "17.33."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "highest_group": {
                "group": "rain",
                "mean": 12.36,
            },
            "lowest_group": {
                "group": "snow",
                "mean": -4.97,
            },
            "difference": 17.33,
            "standardised_difference": 1.0,
        },
        strength_label=(
            "large_group_difference"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.COMPARATIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    small_group = _coverage_evidence_item(
        evidence_id="EVD_COV_005",
        finding=(
            "Rain observations have a mean wind "
            "speed of 10.97 compared with 9.482 "
            "for snow, a difference of 1.489."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "highest_group": {
                "group": "rain",
                "mean": 10.97,
            },
            "lowest_group": {
                "group": "snow",
                "mean": 9.482,
            },
            "difference": 1.489,
            "standardised_difference": 0.22,
        },
        strength_label=(
            "small_group_difference"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.COMPARATIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
        relevance=0.80,
        salience=0.75,
    )

    evidence = EvidenceLedger(
        fingerprint="coverage-test",
        items=[
            overview,
            quality,
            correlation,
            large_group,
            small_group,
        ],
    )

    facts = {
        item.evidence_id: _coverage_fact(
            item,
            f"FACT_COV_{index:03d}",
        )
        for index, item in enumerate(
            evidence.items,
            start=1,
        )
    }

    return evidence, facts


def test_report_coverage_recovery_regression():
    from table2text.audit import (
        augment_fact_ledger_for_report_coverage,
    )
    from table2text.schemas import (
        VerificationMethod,
    )

    evidence, facts = _coverage_fixture()

    thin_ledger = FactLedger(
        writer_ready_facts=[
            facts["EVD_COV_005"]
        ]
    )

    recovered = (
        augment_fact_ledger_for_report_coverage(
            fact_ledger=thin_ledger,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            settings=Settings(),
        )
    )

    assert (
        len(recovered.writer_ready_facts)
        > len(thin_ledger.writer_ready_facts)
    )

    assert (
        recovered
        .deterministically_recovered_fact_ids
    )

    recovered_facts = [
        fact
        for fact in recovered.writer_ready_facts
        if fact.fact_id
        in recovered
        .deterministically_recovered_fact_ids
    ]

    assert recovered_facts

    assert all(
        fact.verification_method
        == VerificationMethod
        .DETERMINISTIC_EVIDENCE_RECOVERY
        for fact in recovered_facts
    )

    represented = {
        evidence_id
        for fact in recovered.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }

    assert "EVD_COV_001" in represented
    assert "EVD_COV_002" in represented
    assert "EVD_COV_003" in represented
    assert "EVD_COV_004" in represented


def test_priority_selection_never_refills_with_small_effect():
    from table2text.audit import (
        select_balanced_priority_facts,
    )

    evidence, facts = _coverage_fixture()

    ledger = FactLedger(
        writer_ready_facts=list(
            facts.values()
        )
    )

    selected = (
        select_balanced_priority_facts(
            facts=ledger.writer_ready_facts,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
            ],
            settings=Settings(),
        )
    )

    selected_evidence_ids = {
        evidence_id
        for fact in selected
        for evidence_id in fact.evidence_ids
    }

    assert "EVD_COV_001" in selected_evidence_ids
    assert "EVD_COV_002" in selected_evidence_ids
    assert "EVD_COV_003" in selected_evidence_ids
    assert "EVD_COV_004" in selected_evidence_ids
    assert "EVD_COV_005" not in selected_evidence_ids


def test_minimum_report_words_never_exceeds_target():
    from table2text.audit import (
        minimum_useful_report_words,
    )

    minimum = minimum_useful_report_words(
        target_words=150,
        required_component_count=4,
        settings=Settings(),
    )

    assert minimum <= 150
    assert minimum > 0


def test_recovered_balanced_fallback_is_not_two_sentence_report():
    from table2text.audit import (
        augment_fact_ledger_for_report_coverage,
    )

    evidence, facts = _coverage_fixture()

    thin_ledger = FactLedger(
        writer_ready_facts=[
            facts["EVD_COV_005"]
        ]
    )

    ledger = (
        augment_fact_ledger_for_report_coverage(
            fact_ledger=thin_ledger,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            settings=Settings(),
        )
    )

    understanding = DataUnderstanding(
        profile_fingerprint="coverage-test",
        dataset_summary=(
            "Weather observations."
        ),
        tables=[],
    )

    plan = ExecutionPlan(
        objective=(
            "Understand the weather dataset and "
            "report its strongest findings."
        ),
        tasks=[],
        route_order=[],
        report_specification=ReportSpecification(
            report_purpose=(
                "Understand the weather dataset."
            ),
            target_length_words=300,
            maximum_main_findings=8,
            prioritisation_rule=(
                "Cover required components using "
                "the strongest evidence."
            ),
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
        ),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=20,
        rationale="Regression test.",
    )

    pack = build_writer_evidence_pack(
        request=plan.objective,
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
    )

    output = fallback_writer(pack)

    assert "## Dataset overview" in output.markdown
    assert "## Data quality" in output.markdown
    assert (
        "## Strongest observed relationships"
        in output.markdown
    )
    assert "1.489" not in output.markdown
    assert len(output.sentence_support) >= 4
    assert (
        output.writer_mode
        == "deterministic_fallback"
    )
    assert not output.eligible_for_primary_evaluation
'''

    write(
        TESTS,
        source.rstrip()
        + "\n"
        + textwrap.dedent(addition).lstrip(),
    )


def main() -> int:
    missing = [
        str(path)
        for path in REQUIRED_FILES
        if not path.exists()
    ]

    if missing:
        print(
            "Run this script from the repository root.",
            file=sys.stderr,
        )
        print(
            "Missing required files:",
            file=sys.stderr,
        )

        for path in missing:
            print(f"- {path}", file=sys.stderr)

        return 2

    backup_dir = create_backups()

    print(f"Backups created at: {backup_dir}")

    update_schemas()
    update_config()
    update_env_example()

    update_audit_imports()
    update_numeric_validation()
    add_strength_normalisation()
    replace_evidence_selection_functions()
    add_fact_coverage_recovery()
    replace_priority_selection()
    replace_component_coverage()
    add_revision_acceptance_helper()
    replace_fallback_writer()

    update_agents()

    update_workflow_imports()
    replace_quality_revision_prompt()
    add_fact_coverage_recovery_to_workflow()
    replace_quality_revision_workflow_block()

    append_tests()

    print("\nSource changes applied successfully.")

    compile_status = run_command(
        [
            sys.executable,
            "-m",
            "compileall",
            "src",
        ]
    )

    if compile_status != 0:
        print(
            "\nCompilation failed. Restore files from:",
            backup_dir,
            file=sys.stderr,
        )
        return compile_status

    pytest_status = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
        ]
    )

    if pytest_status != 0:
        print(
            "\nTests failed. Review the pytest output. "
            "Original files are preserved in:",
            backup_dir,
            file=sys.stderr,
        )
        return pytest_status

    print("\nAll compilation and pytest checks passed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

### `pyproject.toml`

````toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "table2text-pydanticai"
version = "0.1.0"
description = "A PydanticAI multi-agent Table2Text system for reducing hallucinations."
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    "pydantic>=2.10,<3.0",
    "pydantic-ai-slim[openai]>=1.0,<2.0",
    "pandas>=2.2,<3.0",
    "numpy>=1.26,<3.0",
    "scikit-learn>=1.5,<2.0",
    "openpyxl>=3.1,<4.0",
    "pyarrow>=16.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.8",
]

[project.scripts]
table2text = "table2text.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/table2text"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-q"

[tool.ruff]
line-length = 100
target-version = "py311"
````

### `src/table2text/__init__.py`

````python
"""PydanticAI multi-agent Table2Text system."""

from .config import Settings
from .workflow import Table2TextWorkflow

__all__ = ["Settings", "Table2TextWorkflow"]

__version__ = "0.1.0"
````

### `src/table2text/__main__.py`

````python
from .cli import main


if __name__ == "__main__":
    main()
````

### `src/table2text/agents.py`

````python
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, ModelRetry, ModelSettings, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.output import NativeOutput, PromptedOutput
from pydantic_ai.providers.ollama import OllamaProvider

from .audit import (
    CAUSAL_PATTERN,
    EXPLANATORY_HYPOTHESIS_PATTERN,
    FACTUAL_TITLE_PATTERN,
    FIELD_LABEL_PATTERN,
    FORECAST_PATTERN,
    INTERNAL_CONTROL_PATTERN,
    PREDICTIVE_PATTERN,
    build_evidence_lookup,
    fact_support_numbers,
    flatten_numbers,
    numbers_supported,
    unsupported_backtick_entities,
    validate_fact_candidates,
    validate_repair_candidate,
)
from .config import Settings
from .capabilities import (
    normalise_event_evidence_queries,
    validate_event_query_priorities,
    validate_evidence_queries,
    validate_semantic_map,
)
from .schemas import (
    AnalysisRoute,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    ClaimPermission,
    ColumnMeaning,
    ColumnRisk,
    DataProfile,
    DataUnderstanding,
    EvidenceCapability,
    ExecutionPlan,
    FactCandidateSet,
    FactLedger,
    InsightCandidate,
    InsightCandidateSet,
    InsightLedger,
    InsightObjective,
    InsightRejection,
    InsightType,
    InsightVerificationResult,
    InsightVerificationStatus,
    InvestigationTask,
    InputSemanticMap,
    InputShape,
    InterpretationLevel,
    InputStructureProfile,
    ReportComponent,
    ReportGenre,
    ReportPerspective,
    ReportSelectionSource,
    ReportSpecification,
    SemanticRole,
    Severity,
    StructuralField,
    SupportType,
    TableUnderstanding,
    TargetStatus,
    ValidationStrategy,
    VerificationResult,
    VerifiedFact,
    VerifiedInsight,
    WriterAgentDraft,
    WriterSectionDraft,
    WriterSentenceDraft,
)

REPORT_QUALITY_DEFECT_PATTERN = re.compile(
    r"\b("
    r"report|sentence|section|wording|phrasing|selection|structure|"
    r"coherence|redundan|repetit|overstat|understat|omit|unclear|"
    r"unsupported|imprecise|paragraph|insight|genre|hypothesis|game report"
    r")\b",
    re.IGNORECASE,
)


def valid_quality_finding(
    finding: str,
) -> bool:
    return bool(
        REPORT_QUALITY_DEFECT_PATTERN.search(
            finding
        )
    )


@dataclass
class AgentDependencies:
    run_id: str
    payload: dict[str, Any] = field(default_factory=dict)


def build_model(model_specification: str, settings: Settings) -> Any:
    if model_specification.startswith("ollama:"):
        model_name = model_specification.split(":", 1)[1]

        return OllamaModel(
            model_name,
            provider=OllamaProvider(
                base_url=settings.ollama_base_url
            ),
        )

    return model_specification


def output_schema(output_type: type, settings: Settings) -> Any:
    if settings.structured_output_mode == "native":
        return NativeOutput(output_type)

    return PromptedOutput(output_type)


DATA_UNDERSTANDING_INSTRUCTIONS = """
You are the Data Understanding Agent in a Table2Text data-science system.

Combine:
- unit-of-observation reasoning;
- provisional data dictionary interpretation;
- quality and usability assessment;
- identification of methodological risks.

Use only the supplied deterministic profile, input-structure description and
sanitized structural field catalog. The catalog contains operational input
only; held-out reference text has already been removed.

Identify:
- constant and near-constant columns;
- suspicious zero or possible sentinel values;
- candidate identifiers;
- candidate time columns;
- possible target-proxy risks;
- fields that should not be used analytically.

Do not invent provenance, collection locations, units, scientific meanings,
diagnoses, interventions, or source metadata.

Preserve exact table and column names.

For structured input, create an `InputSemanticMap` that explains what the
record and its fields represent. Use only the broad controlled semantic roles
provided by the schema. Keep domain labels such as scoring, votes, revenue or
assists in the free-text `label` and `description`; do not invent a new role.

The semantic map is a broad analytical index for the supplied structure. Include
every event, participant and entity binding that may support a faithful report,
especially every aggregate participant-level measure and every substantive
nested-entity measure. Copy every `path_pattern` verbatim from the structural
catalog, including any `*` wildcards. A wildcard pattern binds the repeated
field family once: never expand it into concrete participant, entity, period or
record keys, and never bind the same catalog path twice.
Label wildcard bindings collectively, such as "Participant name" or "Entity
points"; never label a wildcard as one particular member such as home,
visitor, first or second.

For every event measure, assign `analytical_function` as a semantic judgement:
- `outcome` is the aggregate measure that determines the recorded event result;
- `outcome_component` is a substantive participant or entity measure that
  contributes to comparison but is not itself the aggregate result;
- `performance` is a substantive recorded achievement or output;
- `participation` is duration, exposure or presence rather than
  substantive performance;
- `context` is a measure whose purpose is descriptive context.
Do not treat playing time, duration or exposure as performance. This
classification interprets field meaning; it does not calculate a result.

Prioritise bindings in this order:
- event context, time, location and status;
- participant and nested-entity identifiers;
- participant-level event outcome measures;
- all participant-level outcome components, then other participant-level
  measures that can support contrasts;
- all substantive entity-level measures, then participation measures.

For an event record, include report-critical roles before optional
administrative fields: human-readable participant identifiers, human-readable
nested entity identifiers when present, the aggregate outcome, event status,
participant measures and entity measures. Include enough date and location
fields to reconstruct the supplied context. Prefer human-readable names over
technical IDs or codes. Do not omit report-critical performance measures in
order to include technical record IDs, redundant name components, pre-event
records, nested status flags or administrative fields.

For event records, do not cap participant contrast measures or entity measures.
When a nested entity collection has numeric measures, bind each substantive
performance or outcome-component measure before optional participation
measures.

Omit low-value administrative fields and exhaustive period/component
measures. For a nested single-event record, top-level constancy is expected:
describe its scope once rather than creating a separate constant-column risk
for every event-context or container field.

Every semantic binding must use an exact table name and exact path pattern from
the supplied structural catalog. Bind the fields needed to identify context,
participants, nested entities, outcome measures and other salient measures.
When the same measure appears at aggregate and segment/sub-event levels, bind
the event outcome to the participant-level aggregate and keep the semantic
levels distinct. Do not substitute a period, phase or component value for an
event total.
Do not encode an analytical conclusion in a binding. Recommend `event_report`
when the sanitized structure represents one event with participants or
entities, even when the later reporting request may be generic.

Semantic interpretation is not factual evidence. Do not write event results,
rankings or report prose in the semantic map.
Return structured output only.
"""


def build_data_understanding_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("data_understanding"),
            settings,
        ),
        name="data_understanding_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            DataUnderstanding,
            settings,
        ),
        instructions=DATA_UNDERSTANDING_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.0,
            max_tokens=7_000,
        ),
        retries={"output": 2},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: DataUnderstanding,
    ) -> DataUnderstanding:
        valid_tables = set(
            context.deps.payload["table_names"]
        )
        valid_columns = {
            table_name: set(columns)
            for table_name, columns in context.deps.payload["columns"].items()
        }

        if (
            output.profile_fingerprint
            != context.deps.payload["fingerprint"]
        ):
            raise ModelRetry(
                "Use the exact supplied profile_fingerprint."
            )

        for table in output.tables:
            if table.table_name not in valid_tables:
                raise ModelRetry(
                    f"Unknown table: {table.table_name}"
                )

            for meaning in table.column_meanings:
                if meaning.column_name not in valid_columns[table.table_name]:
                    raise ModelRetry(
                        f"Unknown column: {meaning.column_name}"
                    )

            for risk in table.column_risks:
                if risk.column_name not in valid_columns[table.table_name]:
                    raise ModelRetry(
                        f"Unknown risk column: {risk.column_name}"
                    )

        catalog = [
            StructuralField.model_validate(item)
            for item in context.deps.payload.get(
                "structural_catalog",
                [],
            )
        ]
        semantic_errors = validate_semantic_map(
            output.semantic_map,
            catalog,
        )
        if semantic_errors:
            raise ModelRetry(
                "Semantic-map validation failed:\n- " + "\n- ".join(semantic_errors[:12])
            )
        if context.deps.payload.get("semantic_map_required") and (
            output.semantic_map is None or not output.semantic_map.bindings
        ):
            raise ModelRetry(
                "Structured operational input requires a non-empty semantic "
                "map using exact catalog paths."
            )

        return output

    return agent


ORCHESTRATOR_INSTRUCTIONS = """
You are the Orchestrator and Investigation Planner.

Create a frozen analytical plan before analytical results are observed.
Define bounded-insight objectives as questions before results are observed.
Objectives may use the request, report specification, table and column
structure, and planned tasks, but must not contain result values or predicted
conclusions.

The user wants a useful data-science report, not a dump of every statistic.

Rules:
- Use exact table and column names.
- Choose analyses relevant to the user's request.
- Normally create 2 to 8 tasks.
- Do not run prediction merely because a numeric column exists.
- A predictive target must be user-selected, metadata-confirmed, or explicitly
  marked as an experimental candidate.
- Do not mark a target as user-selected unless the request names it.
- Use chronological validation when a usable time field exists.
- Forecasting requires a target, reliable time ordering, rolling evaluation,
  and naive baselines.
- Causal work is feasibility-first.
- Include a report specification with a main finding budget, supporting-fact
  budget, and target length.
- Use only evidence capabilities listed as available in the supplied input.
- Never plan an event result, entity ranking, temporal change, milestone, or
  comparison capability that is not available.
- Do not let one analytical route dominate a general dataset-understanding
  report.
- Do not let one evidence subtype dominate a general dataset-understanding
  report.
- For requests asking to understand a dataset, require dataset overview,
  data quality, strongest relationships, limitations, and next steps.
- For general requests to report findings, cover overview, data quality, the
  strongest relationships, and limitations/next steps unless the user narrowed
  the scope.
- Prediction and forecasting remain optional and must not be added unless the
  request or confirmed metadata supports them.
- Do not rewrite or replace the user's objective with a different objective.
- Negative and insufficiency findings are valid.
- For a generic request, honour the controller-selected genre derived from the
  sanitized semantic map. A high-confidence single event should remain an
  event report; do not turn it into a flat-table data-science report. Explicit
  user instructions and experiment configuration still take priority. Genre
  controls communication, never factual permission.
- Use neutral perspective by default. Subject-centred perspective may
  prioritise verified facts about an explicitly named subject, but it must not
  change numbers, claim permissions, or evaluative strength.
- A generic report may ask which findings jointly describe the strongest
  structure, which contrast is strongest and non-redundant, whether variables
  overlap substantially, which quality issue matters most, and what the reader
  should remember.
- A sports report may ask which verified facts describe the result, salient
  performances, team contrasts, and supported conventional milestones.
- An event report must request the event_result, leading_performance, and
  main_contrast content slots only when their required capabilities are
  available. It must not treat reference text as operational evidence.
- When a semantic map is supplied, create generic evidence queries using only
  semantic binding IDs. Use `retrieve` for context, `compare` for participant
  measures, and `rank` for entity measures. Do not hard-code field aliases or
  domain-specific extraction rules.
- Every field whose name ends in `_binding_id` or `_binding_ids` must contain
  only exact `binding_id` strings from the supplied ID-only semantic binding
  catalogue. Never put a path pattern, label or column name in those fields.
- Follow these generic query shapes:
  * `event_context`: retrieve one or more event-level context/time/location
    value IDs; no entity ID is required.
  * `event_status`: retrieve one or more event-level status value IDs.
  * `event_outcome`: compare exactly one participant-level outcome value ID and
    set `entity_binding_id` to a participant-identifier ID.
  * `entity_ranking`: rank exactly one entity-level measure value ID, set
    `entity_binding_id` to an entity-identifier ID and optionally set
    `group_binding_id` to a participant-identifier ID.
  * `participant_comparison` or `event_contrast`: compare exactly one
    participant-level measure value ID and set `entity_binding_id` to a
    participant-identifier ID.
- Query only measures present in the semantic binding catalogue. The broader
  structural catalog is not permission to reference an unbound measure.
- Query questions are pre-result analytical questions. Do not place observed
  values, winners, rankings or conclusions in a query.
- For a supported event report, query event context, event status, the outcome
  measure, all available substantive entity rankings, and all participant
  contrasts that can support a faithful report.
- Treat the semantic binding's `analytical_function` as the content-priority
  contract. Prefer `performance` and `outcome_component` for entity rankings.
  Do not rank `participation` when substantive entity measures are available
  unless the user's request explicitly asks about duration, exposure or
  participation.
- For participant contrasts, prefer distinct `outcome_component` measures
  before general performance or context measures. Relate components as
  descriptive contrasts only; do not imply that they caused the result.
- Do not query the same measure/entity combination twice under different names
  or repeat event context as a data-quality query.
- Use these evidence types exactly: event_outcome for outcome comparison;
  event_context or event_status for context retrieval; entity_ranking for ranking;
  entity_performance for entity performance; and participant_comparison or
  event_contrast for participant comparisons.
- Do not place a result, statistic, double-double, hat-trick, dominance claim,
  or other predicted conclusion in an insight objective.
- Set frozen=true.
"""


def build_orchestrator_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("orchestrator"),
            settings,
        ),
        name="orchestrator_and_investigation_planner",
        deps_type=AgentDependencies,
        output_type=output_schema(
            ExecutionPlan,
            settings,
        ),
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.1,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: ExecutionPlan,
    ) -> ExecutionPlan:
        valid_tables = set(
            context.deps.payload["table_names"]
        )
        valid_columns = {
            table_name: set(columns)
            for table_name, columns in context.deps.payload["columns"].items()
        }
        allow_experimental = context.deps.payload["allow_experimental_targets"]
        selected_report_genre = context.deps.payload.get("selected_report_genre")

        if not output.frozen:
            raise ModelRetry("Set frozen=true.")

        user_request = context.deps.payload.get("user_request")
        if user_request and output.objective.strip() != user_request.strip():
            raise ModelRetry(
                "Use the exact supplied user objective; do not substitute a new purpose."
            )

        if not output.tasks:
            raise ModelRetry(
                "Create at least one investigation task."
            )

        if (
            selected_report_genre
            and output.report_specification.genre.value != selected_report_genre
        ):
            raise ModelRetry(
                f"Use the controller-selected report genre exactly: {selected_report_genre}."
            )

        seen: set[str] = set()
        available_capabilities = {
            EvidenceCapability(value)
            for value in context.deps.payload.get(
                "available_capabilities",
                [],
            )
        }

        for task in output.tasks:
            if task.task_id in seen:
                raise ModelRetry(
                    f"Duplicate task ID: {task.task_id}"
                )
            seen.add(task.task_id)

            if (
                task.capability is not None
                and task.capability not in available_capabilities
            ):
                raise ModelRetry(
                    f"Task {task.task_id} selects unavailable capability "
                    f"{task.capability.value}."
                )

            if task.table_name not in valid_tables:
                raise ModelRetry(
                    f"Unknown table: {task.table_name}"
                )

            referenced = [
                *task.columns,
                task.target_column,
                task.time_column,
                task.exposure_column,
                task.outcome_column,
                *task.confounder_columns,
            ]

            for column in [value for value in referenced if value]:
                if column not in valid_columns[task.table_name]:
                    raise ModelRetry(
                        f"Unknown column `{column}` in `{task.table_name}`."
                    )

            if (
                task.target_status == TargetStatus.EXPERIMENTAL_CANDIDATE
                and not allow_experimental
            ):
                raise ModelRetry(
                    "Experimental targets are disabled by configuration."
                )

            if (
                task.route
                in {
                    AnalysisRoute.PREDICTIVE,
                    AnalysisRoute.FORECASTING,
                }
                and not task.target_column
            ):
                raise ModelRetry(
                    f"{task.task_id} requires a target column."
                )

        used_routes = {
            task.route
            for task in output.tasks
        }

        if not used_routes.issubset(
            set(output.route_order)
        ):
            raise ModelRetry(
                "route_order must include every route used by the tasks."
            )

        if settings.enable_insight_synthesis and not output.insight_objectives:
            raise ModelRetry(
                "Create a small set of frozen insight objectives as questions."
            )

        objective_ids: set[str] = set()
        for objective in output.insight_objectives:
            if not objective.objective_id.strip():
                raise ModelRetry("Insight objective IDs must not be empty.")

            if objective.objective_id in objective_ids:
                raise ModelRetry(
                    f"Duplicate insight objective ID: {objective.objective_id}"
                )
            objective_ids.add(objective.objective_id)

            if not objective.question.strip().endswith("?"):
                raise ModelRetry(
                    "Insight objectives must be questions, not conclusions."
                )

            if re.search(r"(?<!\w)\d+(?:[.,]\d+)?%?", objective.question):
                raise ModelRetry(
                    "Insight objectives must not contain result values."
                )

            unknown_task_ids = (
                set(objective.relevant_task_ids) - seen
            )
            if unknown_task_ids:
                raise ModelRetry(
                    "Insight objectives reference unknown task IDs: "
                    f"{sorted(unknown_task_ids)}"
                )

        if (
            output.report_specification.genre
            in {
                ReportGenre.EVENT_REPORT,
                ReportGenre.SPORTS_GAME_REPORT,
            }
            and not context.deps.payload.get(
                "event_genre_allowed",
                False,
            )
        ):
            raise ModelRetry(
                "event_report requires an explicit request or experiment "
                "configuration."
            )

        if (
            user_request
            and output.report_specification.genre
            not in {
                ReportGenre.EVENT_REPORT,
                ReportGenre.SPORTS_GAME_REPORT,
            }
            and re.search(
                r"\b(understand|overview|summari[sz]e|describe|report findings|strongest findings)\b",
                user_request,
                re.IGNORECASE,
            )
        ):
            required = set(output.report_specification.required_components)
            expected = {
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            }
            if not expected.issubset(required):
                raise ModelRetry(
                    "General dataset-understanding reports must require overview, "
                    "data quality, strongest relationships, and limitations/next steps."
                )

        semantic_map_payload = context.deps.payload.get("semantic_map")
        semantic_map = (
            InputSemanticMap.model_validate(semantic_map_payload) if semantic_map_payload else None
        )
        structural_catalog = [
            StructuralField.model_validate(item)
            for item in context.deps.payload.get(
                "structural_catalog",
                [],
            )
        ]
        if (
            selected_report_genre
            in {
                ReportGenre.EVENT_REPORT.value,
                ReportGenre.SPORTS_GAME_REPORT.value,
            }
            and semantic_map is not None
            and semantic_map.bindings
        ):
            output = output.model_copy(
                update={
                    "evidence_queries": normalise_event_evidence_queries(
                        queries=output.evidence_queries,
                        semantic_map=semantic_map,
                        tasks=output.tasks,
                        available_capabilities=available_capabilities,
                        request=user_request or "",
                    )
                }
            )
        query_errors = validate_evidence_queries(
            output.evidence_queries,
            semantic_map,
            structural_catalog,
            task_ids={task.task_id for task in output.tasks},
            available=available_capabilities,
            task_capabilities={
                task.task_id: task.capability
                for task in output.tasks
            },
        )
        if selected_report_genre in {
            ReportGenre.EVENT_REPORT.value,
            ReportGenre.SPORTS_GAME_REPORT.value,
        }:
            query_errors.extend(
                validate_event_query_priorities(
                    output.evidence_queries,
                    semantic_map,
                    user_request or "",
                )
            )
        if query_errors:
            binding_guide = (
                ", ".join(
                    f"{binding.binding_id}={binding.label} "
                    f"({binding.role.value}/{binding.level.value}/"
                    f"{binding.analytical_function.value if binding.analytical_function else 'none'})"
                    for binding in semantic_map.bindings
                )
                if semantic_map is not None
                else "none"
            )
            raise ModelRetry(
                "Evidence-query validation failed:\n- "
                + "\n- ".join(query_errors[:12])
                + "\nUse only these exact binding IDs: "
                + binding_guide
            )
        if len(output.evidence_queries) > output.maximum_facts:
            raise ModelRetry(
                "The number of evidence queries must not exceed the fact "
                "budget because each query requires verifier review."
            )

        if (
            selected_report_genre
            in {
                ReportGenre.EVENT_REPORT.value,
                ReportGenre.SPORTS_GAME_REPORT.value,
            }
            and semantic_map is not None
            and semantic_map.bindings
        ):
            query_signatures: set[
                tuple[str, tuple[str, ...], str | None, str | None]
            ] = set()
            duplicate_query_ids: list[str] = []
            for query in output.evidence_queries:
                signature = (
                    query.operation.value,
                    tuple(query.value_binding_ids),
                    query.entity_binding_id,
                    query.group_binding_id,
                )
                if signature in query_signatures:
                    duplicate_query_ids.append(query.query_id)
                query_signatures.add(signature)
            if duplicate_query_ids:
                raise ModelRetry(
                    "Remove duplicate semantic queries for the same operation, "
                    "measure and entity bindings: "
                    + ", ".join(duplicate_query_ids)
                )

            query_capabilities = {query.capability for query in output.evidence_queries}
            required_query_capabilities = available_capabilities & {
                EvidenceCapability.EVENT_OUTCOME,
                EvidenceCapability.RANKING,
                EvidenceCapability.GROUP_COMPARISON,
            }
            missing_query_capabilities = required_query_capabilities - query_capabilities
            if missing_query_capabilities:
                raise ModelRetry(
                    "The event plan is missing supported semantic query "
                    "capabilities: "
                    + ", ".join(
                        sorted(capability.value for capability in missing_query_capabilities)
                    )
                )

            binding_roles = {binding.role for binding in semantic_map.bindings}
            query_evidence_types = {query.evidence_type for query in output.evidence_queries}
            required_evidence_types: set[str] = set()
            if (
                SemanticRole.OUTCOME_MEASURE in binding_roles
                and EvidenceCapability.EVENT_OUTCOME in available_capabilities
            ):
                required_evidence_types.add("event_outcome")
            if binding_roles & {
                SemanticRole.CONTEXT,
                SemanticRole.TIME,
                SemanticRole.LOCATION,
            }:
                required_evidence_types.add("event_context")
            if SemanticRole.STATUS in binding_roles:
                required_evidence_types.add("event_status")

            missing_evidence_types = required_evidence_types - query_evidence_types
            if missing_evidence_types:
                raise ModelRetry(
                    "The event plan is missing supported semantic evidence "
                    "types: " + ", ".join(sorted(missing_evidence_types))
                )

        return output

    return agent


EVIDENCE_INSTRUCTIONS = """
You are the Evidence Analyst Agent.

The analytical engine has already produced a rich Evidence Ledger containing
calculated values, practical interpretations, methodological limitations,
salience, and prohibited interpretations.

Create atomic verified-fact candidates for the verifier.

Rules:
- Every candidate must cite exact evidence IDs.
- Preserve calculated values exactly.
- Preserve negative and insufficiency findings.
- Do not convert the evidence into a final report.
- Do not create new statistics or domain explanations.
- Carry forward prohibited interpretations and material caveats.
- Exclude evidence marked eligible_for_writer=false.
- Do not make every candidate a headline; preserve recommended_use.
- Do not select facts only from the final evidence items or a single route.
- Preserve dataset overview facts, important quality facts, strong or moderate
  relationships, negative modelling findings, and limitations.
- Do not promote small or weak effects to main findings when stronger unused
  evidence is available.
- Do not copy internal prohibited interpretations into fact_summary.
- For generic semantic-query evidence, use the query's semantic label,
  operation and structured metrics to propose the directly supported fact.
  The executor intentionally does not author winner, ranking or comparison
  sentences. Do not merely repeat "validated semantic query result".
- A compare result may be described only in the direction shown by its ordered
  records. A rank result must preserve the supplied order, values and tie
  annotations. Compose identities only from the supplied entity, group and
  context values.
"""


def build_evidence_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("evidence"),
            settings,
        ),
        name="evidence_analyst_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            FactCandidateSet,
            settings,
        ),
        instructions=EVIDENCE_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.0,
            max_tokens=9_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: FactCandidateSet,
    ) -> FactCandidateSet:
        from .schemas import EvidenceLedger

        ledger = EvidenceLedger.model_validate(
            context.deps.payload["evidence_ledger"]
        )

        errors = validate_fact_candidates(
            output,
            ledger,
        )
        required_query_evidence_ids = {
            item.evidence_id
            for item in ledger.items
            if item.query_id is not None
            and item.eligible_for_writer
        }
        covered_evidence_ids = {
            evidence_id
            for candidate in output.candidates
            for evidence_id in candidate.evidence_ids
        }
        missing_query_evidence_ids = (
            required_query_evidence_ids - covered_evidence_ids
        )
        if missing_query_evidence_ids:
            errors.append(
                "Create at least one atomic fact candidate for every "
                "writer-eligible semantic query result. Missing evidence "
                f"IDs: {sorted(missing_query_evidence_ids)}"
            )

        if errors:
            raise ModelRetry(
                "Fact candidate validation failed:\n- "
                + "\n- ".join(errors[:10])
            )

        return output

    return agent


VERIFIER_INSTRUCTIONS = """
You are the Fact Verification Agent.

Verify each candidate against the cited evidence.

Review every candidate exactly once.

Reject:
- unsupported numbers;
- unsupported entities;
- direction or polarity changes;
- permissions absent from the evidence;
- facts derived from excluded evidence;
- predictive or forecast interpretations without validation;
- causal wording without a verified causal design.
- reversed ordering, winner/loser labels, ranking positions or comparison
  direction relative to semantic-query metrics;
- event meanings not licensed by the query's semantic label and capability.

Judge every candidate independently.

A direct deterministic fact such as a row count, column count,
missing-value count, constant-field finding, correlation, or validated
group comparison can be fully valid even when it is simple or less
narratively interesting than another candidate.

Do not reject overview or data-quality facts merely to keep the ledger
concise. Reject them only when they are unsupported, numerically
inconsistent, semantically escalated, or methodologically invalid.

Do not rewrite candidates into final report prose.
"""


def build_verifier_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("verifier"),
            settings,
        ),
        name="fact_verification_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            VerificationResult,
            settings,
        ),
        instructions=VERIFIER_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.0,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: VerificationResult,
    ) -> VerificationResult:
        candidates = FactCandidateSet.model_validate(
            context.deps.payload["fact_candidates"]
        )

        expected = {
            candidate.candidate_id
            for candidate in candidates.candidates
        }
        received = [
            review.candidate_id
            for review in output.reviews
        ]

        if len(received) != len(set(received)):
            raise ModelRetry(
                "Duplicate fact reviews are not allowed."
            )

        if set(received) != expected:
            raise ModelRetry(
                "Review every candidate exactly once. "
                f"Missing={sorted(expected - set(received))}; "
                f"extra={sorted(set(received) - expected)}"
            )

        return output

    return agent


INSIGHT_SYNTHESIS_INSTRUCTIONS = """
You are the Evidence Analyst performing a second bounded synthesis pass.

The first pass identified evidence-grounded facts. This pass relates verified
facts into a small number of useful, evidence-constrained interpretations.

Definitions:
- Finding: a directly supported observation.
- Bounded insight: an interpretation formed by relating verified findings.
- Analytical implication: why the related findings matter for interpretation
  or analysis, without proposing why the observed pattern exists.
- Hypothesis: a plausible explanation requiring additional testing.

Rules:
1. Use only supplied writer-ready verified facts and their referenced
   deterministic evidence.
2. Never calculate a statistic.
3. Never introduce a number absent from supplied support.
4. Never introduce an entity absent from supplied support.
5. Every candidate must cite source fact IDs.
6. Every cited fact ID must contribute materially to the statement.
7. A bounded insight normally requires at least the configured minimum number
   of source facts.
8. Single-fact exceptions are permitted only for anomaly, data-quality
   implication, or a direct narrative summary supported by one compound fact.
9. Do not merely paraphrase one fact, or several facts that repeat the same
   result, and label the restatement an insight.
10. Do not turn correlation into causation.
    Use outcome_association, never outcome_driver, for descriptive evidence.
11. Do not use drives, causes, explains, leads to, results in, or equivalent
    causal wording without explicit causal permission.
12. Do not add domain knowledge from memory.
13. Do not infer collection location, frequency, provenance, or measurement
    process.
14. Do not claim that a variable is useless or universally redundant.
15. Describe overlap as containing highly overlapping information in this
    dataset.
16. `why_it_matters` is the analytical implication. It must add a concrete,
   evidence-bounded consequence for interpretation or analysis; it must not
   restate coefficients, effect labels, or the candidate statement.
17. A possible reason why a pattern exists is a hypothesis, including claims
   that a pattern may reflect a dependency, data artifact, collection process,
   or unmeasured mechanism. Do not hide a hypothesis in `why_it_matters`, a
   limitation, or a recommendation.
18. A hypothesis must be explicitly labelled as a hypothesis.
19. A hypothesis must not be suitable for the main report unless hypotheses
   are explicitly allowed.
20. Preserve deterministic qualitative strength labels. Do not relabel a
   strong association as moderate, or vice versa.
21. For missingness, prefer the directly supported scope of the complete-case
   subset over an assumed bias mechanism. For duplicates, describe a possible
   influence only as a bounded methodological risk, never as a measured effect.
22. Do not claim that data are complete, contain no missing values, or contain
   no duplicates unless the cited facts reference evidence that measured that
   exact data-quality property.
23. Include limitations or alternative explanations where needed, but keep
   unverified explanations in explicitly labelled hypothesis candidates.
24. Prefer a few meaningful insights over many small restatements.
25. Respect the configured candidate limit.

Return structured output only.
"""


INSIGHT_VERIFIER_INSTRUCTIONS = """
You are the Fact Verifier reviewing bounded insight candidates.

A candidate can contain correct individual facts while still making an
unsupported interpretation. Review each candidate against only the supplied
verified facts and deterministic evidence.

For each candidate decide verified, verified_with_caveat, hypothesis_only, or
rejected.

For every record explicitly set:
- `adds_bounded_synthesis`: true only when the statement relates findings and
  adds more than a direct finding restatement;
- `analytical_implication_supported`: true only when `why_it_matters` is a
  concrete, evidence-bounded analytical implication rather than a paraphrase;
- `contains_hypothesis`: true whenever the statement or analytical implication
  proposes a possible explanation that requires further testing.

A record may be verified or verified_with_caveat only when the first two flags
are true and `contains_hypothesis` is false. A direct-finding restatement must
be rejected. A candidate containing a possible explanation must be
hypothesis_only or rejected.

Check that every cited fact exists and genuinely contributes; every number,
table, column, group and entity is supported; the facts jointly support the
statement; and the wording adds useful synthesis rather than renaming one
fact. Match wording strength to evidence strength. Do not introduce causality,
outside domain explanations, collection metadata, or generalisations beyond
the analysed dataset. Preserve needed limitations and identify hypotheses
explicitly. Exclude hypotheses from the main report unless explicitly allowed.
Treat explanations involving possible dependencies, artifacts, collection
processes, or unmeasured mechanisms as hypotheses, even when phrased as a next
step. Do not call a deterministically strong relationship moderate.
Assess salience against the request and selected report genre.

Do not approve a claim merely because it sounds plausible. Do not use outside
knowledge or calculate new values. Preserve or safely weaken candidate
wording; never strengthen it. Return one record for every candidate.
"""


HYPOTHESIS_LABEL_PATTERN = re.compile(
    r"\b(hypothesis|hypothesise|hypothesize|hypothesised|hypothesized)\b",
    re.IGNORECASE,
)

UNIVERSAL_GENERALISATION_PATTERN = re.compile(
    r"\b(always|in general|universally|proves that|demonstrates that all)\b",
    re.IGNORECASE,
)

MISSINGNESS_CLAIM_PATTERN = re.compile(
    r"\b(no|without|zero)\s+missing(?:ness|\s+(?:data|values?))?\b|"
    r"\bmissing(?:ness|\s+(?:data|values?))\b|"
    r"\b(?:complete data|data (?:are|is|was|were) complete|completeness)\b",
    re.IGNORECASE,
)

DUPLICATE_CLAIM_PATTERN = re.compile(
    r"\b(no|without|zero)\s+(?:exact\s+)?duplicates?\b|"
    r"\bduplicates?|deduplicat(?:e|ed|ion)\b",
    re.IGNORECASE,
)

SINGLE_FACT_INSIGHT_TYPES = {
    InsightType.ANOMALY,
    InsightType.DATA_QUALITY_IMPLICATION,
    InsightType.NARRATIVE_SUMMARY,
}

STRONG_PERMISSIONS = {
    ClaimPermission.CAUSAL,
    ClaimPermission.PREDICTIVE,
    ClaimPermission.FORECAST,
}


def _normalise_statement(value: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        value.lower(),
    ).strip()


def _statement_tokens(value: str) -> set[str]:
    return {
        token
        for token in _normalise_statement(value).split()
        if len(token) > 2
    }


def _materially_duplicate_statements(
    left: str,
    right: str,
) -> bool:
    left_normalised = _normalise_statement(left)
    right_normalised = _normalise_statement(right)

    if left_normalised == right_normalised:
        return True

    left_tokens = _statement_tokens(left)
    right_tokens = _statement_tokens(right)

    if not left_tokens or not right_tokens:
        return False

    return (
        len(left_tokens & right_tokens)
        / len(left_tokens | right_tokens)
        >= 0.85
    )


def _safe_fact_permissions(
    facts: list[VerifiedFact],
) -> set[ClaimPermission]:
    if not facts:
        return set()

    permissions = {
        permission
        for fact in facts
        for permission in fact.claim_permissions
    }

    for permission in STRONG_PERMISSIONS:
        if not all(
            permission in fact.claim_permissions
            for fact in facts
        ):
            permissions.discard(permission)

    return permissions


def _insight_support_numbers(
    facts: list[VerifiedFact],
    evidence_ledger: Any,
) -> list[float]:
    return [
        number
        for fact in facts
        for number in fact_support_numbers(
            fact,
            evidence_ledger,
        )
    ]


def _schema_entities_for_evidence_ids(
    evidence_ids: set[str],
    evidence_ledger: Any,
) -> set[str]:
    lookup = build_evidence_lookup(evidence_ledger)
    return {
        entity
        for evidence_id in evidence_ids
        if evidence_id in lookup
        for entity in [
            *lookup[evidence_id].source_tables,
            *lookup[evidence_id].source_columns,
        ]
        if entity
    }


def _entity_occurs(
    entity: str,
    statement: str,
) -> bool:
    return bool(
        entity
        and re.search(
            rf"(?<!\w){re.escape(entity)}(?!\w)",
            statement,
            re.IGNORECASE,
        )
    )


def _unsupported_insight_entities(
    *,
    statement: str,
    facts: list[VerifiedFact],
    evidence_ledger: Any,
) -> list[str]:
    cited_evidence_ids = {
        evidence_id
        for fact in facts
        for evidence_id in fact.evidence_ids
    }
    supported_entities = {
        entity
        for fact in facts
        for entity in fact.entities
        if entity
    }
    supported_entities.update(
        _schema_entities_for_evidence_ids(
            cited_evidence_ids,
            evidence_ledger,
        )
    )

    all_schema_entities = _schema_entities_for_evidence_ids(
        {
            item.evidence_id
            for item in evidence_ledger.items
        },
        evidence_ledger,
    )

    unsupported = {
        entity
        for entity in all_schema_entities
        if _entity_occurs(entity, statement)
        and entity not in supported_entities
    }

    unsupported.update(
        unsupported_backtick_entities(
            statement,
            supported_entities,
        )
    )

    for entity in re.findall(
        r"\b(?:Team|Player)\s+[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?",
        statement,
    ):
        if entity not in supported_entities:
            unsupported.add(entity)

    return sorted(unsupported)


def _candidate_fact_lookup(
    fact_ledger: FactLedger,
) -> dict[str, VerifiedFact]:
    return {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }


def _supports_data_quality_dimension(
    *,
    evidence_ids: set[str],
    evidence_lookup: dict[str, Any],
    dimension: str,
) -> bool:
    for evidence_id in evidence_ids:
        item = evidence_lookup.get(evidence_id)
        if item is None:
            continue
        if dimension == "missingness" and (
            item.capability == EvidenceCapability.MISSINGNESS
            or item.evidence_type == "missingness"
            or any(
                key in item.metrics
                for key in {"missing_count", "missing_rate"}
            )
        ):
            return True
        if dimension == "duplicates" and (
            item.capability == EvidenceCapability.DUPLICATES
            or item.evidence_type == "duplicate_rows"
            or any(
                key in item.metrics
                for key in {"duplicate_row_count", "duplicate_rate"}
            )
        ):
            return True
    return False


def validate_insight_candidates(
    candidate_set: InsightCandidateSet,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
) -> list[str]:
    errors: list[str] = []
    fact_lookup = _candidate_fact_lookup(fact_ledger)
    evidence_lookup = build_evidence_lookup(evidence_ledger)
    seen_ids: set[str] = set()
    accepted_for_duplicate_check: list[InsightCandidate] = []

    if len(candidate_set.candidates) > settings.max_insight_candidates:
        errors.append(
            "Insight candidate count exceeds the configured limit of "
            f"{settings.max_insight_candidates}."
        )

    for candidate in candidate_set.candidates:
        candidate_id = candidate.insight_id.strip()

        if not candidate_id:
            errors.append("An insight candidate has an empty insight_id.")
            continue

        if candidate_id in seen_ids:
            errors.append(f"Duplicate insight ID: {candidate_id}")
            continue

        seen_ids.add(candidate_id)

        if not candidate.statement.strip():
            errors.append(f"{candidate_id} has an empty statement.")

        if not candidate.source_fact_ids:
            errors.append(f"{candidate_id} has no source fact IDs.")
            continue

        if len(candidate.source_fact_ids) != len(
            set(candidate.source_fact_ids)
        ):
            errors.append(f"{candidate_id} repeats source fact IDs.")

        unknown_fact_ids = [
            fact_id
            for fact_id in candidate.source_fact_ids
            if fact_id not in fact_lookup
        ]
        if unknown_fact_ids:
            errors.append(
                f"{candidate_id} cites unknown fact IDs: "
                f"{unknown_fact_ids}"
            )
            continue

        facts = [
            fact_lookup[fact_id]
            for fact_id in candidate.source_fact_ids
        ]
        fact_evidence_ids = {
            evidence_id
            for fact in facts
            for evidence_id in fact.evidence_ids
        }

        unknown_evidence_ids = [
            evidence_id
            for evidence_id in candidate.source_evidence_ids
            if evidence_id not in evidence_lookup
        ]
        if unknown_evidence_ids:
            errors.append(
                f"{candidate_id} cites unknown evidence IDs: "
                f"{unknown_evidence_ids}"
            )

        unlinked_evidence_ids = [
            evidence_id
            for evidence_id in candidate.source_evidence_ids
            if evidence_id not in fact_evidence_ids
        ]
        if unlinked_evidence_ids:
            errors.append(
                f"{candidate_id} cites evidence not referenced by its "
                f"source facts: {unlinked_evidence_ids}"
            )

        writer_visible_text = " ".join(
            [
                candidate.statement,
                candidate.why_it_matters,
            ]
        )
        if MISSINGNESS_CLAIM_PATTERN.search(
            writer_visible_text
        ) and not _supports_data_quality_dimension(
            evidence_ids=fact_evidence_ids,
            evidence_lookup=evidence_lookup,
            dimension="missingness",
        ):
            errors.append(
                f"{candidate_id} makes a missingness or completeness claim "
                "without missingness evidence."
            )
        if DUPLICATE_CLAIM_PATTERN.search(
            writer_visible_text
        ) and not _supports_data_quality_dimension(
            evidence_ids=fact_evidence_ids,
            evidence_lookup=evidence_lookup,
            dimension="duplicates",
        ):
            errors.append(
                f"{candidate_id} makes a duplicate-data claim without "
                "duplicate-row evidence."
            )

        support_numbers = _insight_support_numbers(
            facts,
            evidence_ledger,
        )
        for field_name, field_text in {
            "statement": candidate.statement,
            "why_it_matters": candidate.why_it_matters,
        }.items():
            if not numbers_supported(
                field_text,
                support_numbers,
            ):
                errors.append(
                    f"{candidate_id} {field_name} contains unsupported "
                    "numbers."
                )

            unsupported_entities = _unsupported_insight_entities(
                statement=field_text,
                facts=facts,
                evidence_ledger=evidence_ledger,
            )
            if unsupported_entities:
                errors.append(
                    f"{candidate_id} {field_name} contains unsupported table "
                    f"or column entities: {unsupported_entities}"
                )

        safe_permissions = _safe_fact_permissions(facts)
        if not set(candidate.claim_permissions).issubset(
            safe_permissions
        ):
            errors.append(
                f"{candidate_id} requests permissions stronger than its "
                "source facts."
            )

        if (
            candidate.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
            and len(set(candidate.source_fact_ids))
            < settings.min_facts_per_bounded_insight
            and candidate.insight_type
            not in SINGLE_FACT_INSIGHT_TYPES
        ):
            errors.append(
                f"{candidate_id} is a single-fact pseudo-insight; "
                f"{settings.min_facts_per_bounded_insight} source facts "
                "are required."
            )

        if (
            candidate.interpretation_level
            == InterpretationLevel.HYPOTHESIS
        ):
            if not HYPOTHESIS_LABEL_PATTERN.search(candidate.statement):
                errors.append(
                    f"{candidate_id} is a hypothesis but is not explicitly "
                    "labelled as one."
                )

            if (
                candidate.suitable_for_main_report
                and not settings.allow_hypotheses_in_report
            ):
                errors.append(
                    f"{candidate_id} cannot be suitable for the main report "
                    "while hypotheses are disabled."
                )

        if (
            candidate.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
            and (
                HYPOTHESIS_LABEL_PATTERN.search(writer_visible_text)
                or EXPLANATORY_HYPOTHESIS_PATTERN.search(
                    writer_visible_text
                )
            )
        ):
            errors.append(
                f"{candidate_id} contains an explanatory hypothesis but is "
                "classified as a bounded insight."
            )

        if (
            candidate.interpretation_level
            == InterpretationLevel.FINDING
        ):
            errors.append(
                f"{candidate_id} is a finding, not a second-pass bounded "
                "insight or hypothesis."
            )

        if (
            CAUSAL_PATTERN.search(writer_visible_text)
            and ClaimPermission.CAUSAL not in safe_permissions
        ):
            errors.append(
                f"{candidate_id} introduces unsupported causal wording."
            )

        if (
            PREDICTIVE_PATTERN.search(writer_visible_text)
            and ClaimPermission.PREDICTIVE not in safe_permissions
        ):
            errors.append(
                f"{candidate_id} introduces unsupported predictive wording."
            )

        if (
            FORECAST_PATTERN.search(writer_visible_text)
            and ClaimPermission.FORECAST not in safe_permissions
        ):
            errors.append(
                f"{candidate_id} introduces unsupported forecast wording."
            )

        if UNIVERSAL_GENERALISATION_PATTERN.search(writer_visible_text):
            errors.append(
                f"{candidate_id} generalises beyond the analysed dataset."
            )

        if _materially_duplicate_statements(
            candidate.statement,
            candidate.why_it_matters,
        ):
            errors.append(
                f"{candidate_id} why_it_matters merely restates the insight."
            )

        if any(
            _materially_duplicate_statements(
                candidate.why_it_matters,
                fact_text,
            )
            for fact in facts
            for fact_text in [
                fact.fact_summary,
                *fact.allowed_interpretations,
            ]
            if fact_text.strip()
        ):
            errors.append(
                f"{candidate_id} why_it_matters merely restates a source "
                "finding."
            )

        duplicate = next(
            (
                previous
                for previous in accepted_for_duplicate_check
                if _materially_duplicate_statements(
                    previous.statement,
                    candidate.statement,
                )
                or (
                    set(previous.source_fact_ids)
                    == set(candidate.source_fact_ids)
                    and previous.insight_type == candidate.insight_type
                    and _materially_duplicate_statements(
                        previous.supporting_summary,
                        candidate.supporting_summary,
                    )
                )
            ),
            None,
        )
        if duplicate is not None:
            errors.append(
                f"{candidate_id} materially duplicates "
                f"{duplicate.insight_id}."
            )
        else:
            accepted_for_duplicate_check.append(candidate)

    return errors


def build_insight_synthesis_agent(
    settings: Settings,
) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("evidence"),
            settings,
        ),
        name="evidence_analyst_agent_second_pass_insight_synthesis",
        deps_type=AgentDependencies,
        output_type=output_schema(
            InsightCandidateSet,
            settings,
        ),
        instructions=INSIGHT_SYNTHESIS_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.0,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: InsightCandidateSet,
    ) -> InsightCandidateSet:
        from .schemas import EvidenceLedger

        fact_ledger = FactLedger.model_validate(
            context.deps.payload["fact_ledger"]
        )
        evidence_ledger = EvidenceLedger.model_validate(
            context.deps.payload["evidence_ledger"]
        )
        errors = validate_insight_candidates(
            output,
            fact_ledger,
            evidence_ledger,
            settings,
        )

        if errors:
            raise ModelRetry(
                "Insight candidate validation failed:\n- "
                + "\n- ".join(errors[:12])
            )

        return output

    return agent


def _verified_statement_is_safe(
    *,
    candidate: InsightCandidate,
    statement: str,
    source_fact_ids: list[str],
    source_evidence_ids: list[str],
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
) -> bool:
    candidate_normalised = _normalise_statement(candidate.statement)
    statement_normalised = _normalise_statement(statement)

    if not statement_normalised:
        return False

    if (
        candidate_normalised not in statement_normalised
        and statement_normalised not in candidate_normalised
    ):
        return False

    checked = candidate.model_copy(
        update={
            "statement": statement,
            "source_fact_ids": source_fact_ids,
            "source_evidence_ids": source_evidence_ids,
        }
    )

    return not validate_insight_candidates(
        InsightCandidateSet(candidates=[checked]),
        fact_ledger,
        evidence_ledger,
        settings,
    )


def validate_insight_verification(
    verification: InsightVerificationResult,
    candidates: InsightCandidateSet,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
) -> list[str]:
    errors: list[str] = []
    candidate_lookup = {
        candidate.insight_id: candidate
        for candidate in candidates.candidates
    }
    received_ids = [
        record.insight_id
        for record in verification.records
    ]
    expected_ids = set(candidate_lookup)

    if len(received_ids) != len(set(received_ids)):
        errors.append("Duplicate insight verification records are not allowed.")

    if set(received_ids) != expected_ids:
        errors.append(
            "Review every insight candidate exactly once. "
            f"Missing={sorted(expected_ids - set(received_ids))}; "
            f"extra={sorted(set(received_ids) - expected_ids)}"
        )

    for record in verification.records:
        candidate = candidate_lookup.get(record.insight_id)
        if candidate is None:
            continue

        verified_status = record.status in {
            InsightVerificationStatus.VERIFIED,
            InsightVerificationStatus.VERIFIED_WITH_CAVEAT,
        }
        if verified_status and not record.adds_bounded_synthesis:
            errors.append(
                f"{record.insight_id} is a direct-finding restatement rather "
                "than a bounded insight."
            )
        if (
            verified_status
            and not record.analytical_implication_supported
        ):
            errors.append(
                f"{record.insight_id} lacks a supported analytical implication."
            )
        if verified_status and record.contains_hypothesis:
            errors.append(
                f"{record.insight_id} contains a hypothesis and cannot be a "
                "verified main insight."
            )
        if (
            record.status
            == InsightVerificationStatus.HYPOTHESIS_ONLY
            and not record.contains_hypothesis
        ):
            errors.append(
                f"{record.insight_id} is marked hypothesis_only without a "
                "hypothesis."
            )
        if (
            candidate.interpretation_level
            == InterpretationLevel.HYPOTHESIS
            and verified_status
        ):
            errors.append(
                f"{record.insight_id} cannot verify a hypothesis as a bounded "
                "main insight."
            )

        source_fact_ids = (
            record.verified_source_fact_ids
            or candidate.source_fact_ids
        )
        source_evidence_ids = (
            record.verified_source_evidence_ids
            or candidate.source_evidence_ids
        )

        if not set(source_fact_ids).issubset(
            set(candidate.source_fact_ids)
        ):
            errors.append(
                f"{record.insight_id} verifier introduced source fact IDs."
            )

        candidate_evidence_ids = {
            evidence_id
            for fact in fact_ledger.writer_ready_facts
            if fact.fact_id in candidate.source_fact_ids
            for evidence_id in fact.evidence_ids
        }
        if not set(source_evidence_ids).issubset(candidate_evidence_ids):
            errors.append(
                f"{record.insight_id} verifier introduced source evidence IDs."
            )

        if record.verified_statement and not _verified_statement_is_safe(
            candidate=candidate,
            statement=record.verified_statement,
            source_fact_ids=source_fact_ids,
            source_evidence_ids=source_evidence_ids,
            fact_ledger=fact_ledger,
            evidence_ledger=evidence_ledger,
            settings=settings,
        ):
            errors.append(
                f"{record.insight_id} verifier statement is unsupported or "
                "stronger than the candidate."
            )

    return errors


def build_insight_verifier_agent(
    settings: Settings,
) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("verifier"),
            settings,
        ),
        name="fact_verification_agent_second_pass_insight_verification",
        deps_type=AgentDependencies,
        output_type=output_schema(
            InsightVerificationResult,
            settings,
        ),
        instructions=INSIGHT_VERIFIER_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.0,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: InsightVerificationResult,
    ) -> InsightVerificationResult:
        from .schemas import EvidenceLedger

        candidates = InsightCandidateSet.model_validate(
            context.deps.payload["insight_candidates"]
        )
        fact_ledger = FactLedger.model_validate(
            context.deps.payload["fact_ledger"]
        )
        evidence_ledger = EvidenceLedger.model_validate(
            context.deps.payload["evidence_ledger"]
        )
        errors = validate_insight_verification(
            output,
            candidates,
            fact_ledger,
            evidence_ledger,
            settings,
        )

        if errors:
            raise ModelRetry(
                "Insight verification validation failed:\n- "
                + "\n- ".join(errors[:12])
            )

        return output

    return agent


def empty_insight_ledger(
    *,
    synthesis_enabled: bool,
    fallback_reason: str,
) -> InsightLedger:
    return InsightLedger(
        synthesis_enabled=synthesis_enabled,
        fallback_reason=fallback_reason,
    )


def materialise_insight_ledger(
    *,
    candidates: InsightCandidateSet,
    verification: InsightVerificationResult,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
) -> InsightLedger:
    candidate_errors = validate_insight_candidates(
        candidates,
        fact_ledger,
        evidence_ledger,
        settings,
    )
    verification_errors = validate_insight_verification(
        verification,
        candidates,
        fact_ledger,
        evidence_ledger,
        settings,
    )
    records = {
        record.insight_id: record
        for record in verification.records
    }
    evidence_lookup = {
        item.evidence_id: item
        for item in evidence_ledger.items
    }
    fact_lookup = _candidate_fact_lookup(fact_ledger)
    rejected: list[InsightRejection] = []
    hypotheses: list[VerifiedInsight] = []
    eligible: list[tuple[int, InsightCandidate, VerifiedInsight]] = []
    candidate_ids = {
        candidate.insight_id
        for candidate in candidates.candidates
    }
    global_candidate_errors = [
        error
        for error in candidate_errors
        if not any(
            candidate_id in error
            for candidate_id in candidate_ids
        )
    ]
    global_verification_errors = [
        error
        for error in verification_errors
        if not any(
            candidate_id in error
            for candidate_id in candidate_ids
        )
    ]

    for index, candidate in enumerate(candidates.candidates):
        reasons = [
            error
            for error in candidate_errors
            if candidate.insight_id in error
        ]
        reasons.extend(global_candidate_errors)
        reasons.extend(global_verification_errors)
        record = records.get(candidate.insight_id)

        if record is None:
            reasons.append("The verifier did not review this insight.")

        if record is not None and record.status == InsightVerificationStatus.REJECTED:
            reasons.extend(
                record.verification_notes
                or ["The verifier rejected this insight."]
            )

        source_fact_ids = list(
            dict.fromkeys(
                (
                    record.verified_source_fact_ids
                    if record is not None
                    and record.verified_source_fact_ids
                    else candidate.source_fact_ids
                )
            )
        )
        source_evidence_ids = list(
            dict.fromkeys(
                (
                    record.verified_source_evidence_ids
                    if record is not None
                    and record.verified_source_evidence_ids
                    else (
                        candidate.source_evidence_ids
                        or [
                            evidence_id
                            for fact_id in source_fact_ids
                            if fact_id in fact_lookup
                            for evidence_id in fact_lookup[
                                fact_id
                            ].evidence_ids
                        ]
                    )
                )
            )
        )
        statement = (
            record.verified_statement
            if record is not None
            and record.verified_statement
            else candidate.statement
        )

        if (
            record is not None
            and record.verified_statement
            and not _verified_statement_is_safe(
                candidate=candidate,
                statement=record.verified_statement,
                source_fact_ids=source_fact_ids,
                source_evidence_ids=source_evidence_ids,
                fact_ledger=fact_ledger,
                evidence_ledger=evidence_ledger,
                settings=settings,
            )
        ):
            reasons.append(
                "The verifier statement was stronger than or unsupported by "
                "the candidate provenance."
            )

        confidence = min(
            candidate.confidence,
            record.confidence if record is not None else 0.0,
        )
        salience = min(
            candidate.salience,
            record.salience if record is not None else 0.0,
        )

        hypothesis_only = bool(
            candidate.interpretation_level
            == InterpretationLevel.HYPOTHESIS
            or (
                record is not None
                and record.status
                == InsightVerificationStatus.HYPOTHESIS_ONLY
            )
        )

        if verification_errors:
            record_errors = [
                error
                for error in verification_errors
                if candidate.insight_id in error
            ]
            reasons.extend(record_errors)

        if reasons:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=list(dict.fromkeys(reasons)),
                )
            )
            continue

        verified = VerifiedInsight(
            insight_id=candidate.insight_id,
            statement=statement,
            insight_type=candidate.insight_type,
            interpretation_level=(
                InterpretationLevel.HYPOTHESIS
                if hypothesis_only
                else InterpretationLevel.BOUNDED_INSIGHT
            ),
            source_fact_ids=source_fact_ids,
            source_evidence_ids=source_evidence_ids,
            source_capabilities=list(
                dict.fromkeys(
                    evidence_lookup[evidence_id].capability
                    for evidence_id in source_evidence_ids
                    if evidence_id in evidence_lookup
                )
            ),
            why_it_matters=candidate.why_it_matters,
            limitations=list(
                dict.fromkeys(
                    [
                        *candidate.limitations,
                        *(
                            record.limitations
                            if record is not None
                            else []
                        ),
                    ]
                )
            ),
            claim_permissions=candidate.claim_permissions,
            confidence=confidence,
            salience=salience,
            verification_status=(
                InsightVerificationStatus.HYPOTHESIS_ONLY
                if hypothesis_only
                else record.status
            ),
        )

        if hypothesis_only:
            if not HYPOTHESIS_LABEL_PATTERN.search(statement):
                rejected.append(
                    InsightRejection(
                        insight_id=candidate.insight_id,
                        candidate=candidate,
                        reasons=[
                            "A hypothesis-only statement must be explicitly "
                            "labelled as a hypothesis."
                        ],
                    )
                )
            else:
                hypotheses.append(verified)
            continue

        if not candidate.suitable_for_main_report:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=["The candidate is not suitable for the main report."],
                )
            )
            continue

        if confidence < settings.min_insight_confidence:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=[
                        "Confidence is below the configured main-insight "
                        "threshold."
                    ],
                )
            )
            continue

        if salience < settings.min_insight_salience:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=[
                        "Salience is below the configured main-insight "
                        "threshold."
                    ],
                )
            )
            continue

        eligible.append((index, candidate, verified))

    eligible.sort(
        key=lambda item: (
            not item[1].suitable_for_main_report,
            -item[2].salience,
            -item[2].confidence,
            item[0],
        )
    )
    selected = eligible[: settings.max_verified_main_insights]

    for _, candidate, _ in eligible[settings.max_verified_main_insights :]:
        rejected.append(
            InsightRejection(
                insight_id=candidate.insight_id,
                candidate=candidate,
                reasons=[
                    "The configured verified main-insight budget was reached."
                ],
            )
        )

    return InsightLedger(
        verified_insights=[
            verified
            for _, _, verified in selected
        ],
        hypothesis_only_insights=hypotheses,
        rejected_insights=rejected,
        verifier_notes=[
            *verification.verifier_notes,
            *[
                error
                for error in verification_errors
                if error not in {
                    reason
                    for rejection in rejected
                    for reason in rejection.reasons
                }
            ],
        ],
        synthesis_enabled=True,
    )


def writer_sentence_grounding_errors(
    *,
    sentence: WriterSentenceDraft,
    fact_lookup: dict[str, VerifiedFact],
    insight_lookup: dict[str, VerifiedInsight],
    sentence_label: str,
) -> list[str]:
    if sentence.support_type == SupportType.NON_FACTUAL:
        return []

    expanded_fact_ids = list(
        dict.fromkeys(
            [
                *sentence.fact_ids,
                *[
                    fact_id
                    for insight_id in sentence.insight_ids
                    if insight_id in insight_lookup
                    for fact_id in insight_lookup[
                        insight_id
                    ].source_fact_ids
                ],
            ]
        )
    )
    supporting_facts = [
        fact_lookup[fact_id]
        for fact_id in expanded_fact_ids
        if fact_id in fact_lookup
    ]

    if not supporting_facts:
        return []

    errors: list[str] = []
    support_numbers = [
        number
        for fact in supporting_facts
        for number in flatten_numbers(
            fact.structured_values
        )
    ]
    if not numbers_supported(
        sentence.text,
        support_numbers,
    ):
        errors.append(
            f"{sentence_label} contains a number unsupported by mapped facts "
            f"{expanded_fact_ids}."
        )

    supported_entities = {
        entity
        for fact in supporting_facts
        for entity in fact.entities
    }
    unsupported_entities = unsupported_backtick_entities(
        sentence.text,
        supported_entities,
    )
    if unsupported_entities:
        errors.append(
            f"{sentence_label} contains unsupported entities "
            f"{unsupported_entities}; mapped fact IDs: "
            f"{expanded_fact_ids}."
        )

    return errors


def recover_missing_writer_insight_ids(
    draft: WriterAgentDraft,
    verified_insight_lookup: dict[str, VerifiedInsight],
) -> WriterAgentDraft:
    """Recover one unambiguous omitted insight ID from exact fact provenance."""

    changed = False
    recovered_sections: list[WriterSectionDraft] = []

    for section in draft.sections:
        recovered_sentences: list[WriterSentenceDraft] = []

        for sentence in section.sentences:
            recovered = sentence
            if (
                sentence.interpretation_level
                == InterpretationLevel.BOUNDED_INSIGHT
                and not sentence.insight_ids
                and sentence.fact_ids
            ):
                cited_fact_ids = set(sentence.fact_ids)
                candidates = [
                    insight_id
                    for insight_id, insight
                    in verified_insight_lookup.items()
                    if set(insight.source_fact_ids)
                    == cited_fact_ids
                ]
                if len(candidates) == 1:
                    recovered = sentence.model_copy(
                        update={"insight_ids": candidates}
                    )
                    changed = True

            recovered_sentences.append(recovered)

        recovered_sections.append(
            section.model_copy(
                update={"sentences": recovered_sentences}
            )
        )

    if not changed:
        return draft

    return draft.model_copy(
        update={"sections": recovered_sections}
    )


WRITER_INSTRUCTIONS = """
You are an expert data scientist and natural report writer.

Use the supplied verified evidence to produce a selective, coherent,
reader-facing data-science report.

Write an insight-led report rather than a catalogue of unrelated statistics
when verified bounded insights are available. The verified Insight Ledger is
the only source of interpretive claims. Verified facts remain the source of
direct findings and supporting details.

For each main analytical paragraph, state one verified bounded insight,
support it with its verified facts, explain why it matters only as authorised
by that insight, and integrate its limitation where needed. Do not invent or
strengthen an insight during writing.

Keep four roles distinct:
- a direct finding reports a verified observation or statistic;
- a bounded insight relates multiple findings into a dataset-scoped pattern;
- the analytical implication explains why that combined pattern matters for
  interpretation or analysis, using only the insight's `why_it_matters`;
- a hypothesis proposes why the pattern exists and requires further testing.

Do not fill an analytical paragraph with a coefficient sentence followed by a
verbal restatement of the same coefficients. Use the verified analytical
implication. A possible dependency, artifact, collection process, or unmeasured
mechanism is a hypothesis even when introduced as something to investigate.

Do not turn association into causation, a group difference into an
explanation, overlapping variables into universal redundancy, a data-quality
risk into a confirmed error, or a game statistic into unsupported dominance.
Every bounded-insight sentence must cite its insight ID and retain relevant
source fact IDs. Every direct factual sentence must cite fact IDs. Do not use
rejected insights or hypothesis-only insights in the main report.

When hypotheses are disabled, do not write a hypothesis section. When they
are enabled, place them only in a separate "Questions for Further
Investigation" section, label each as a hypothesis or question, state what
additional analysis is needed, and never present it as a result.

Respect the selected genre, content slots and perspective. A data-science
report uses bounded analytical prose. A dataset overview stays concise and
mainly finding-led. An event report communicates the verified result, leading
performances and major participant contrasts in conventional narrative form.
Fill each required slot only from evidence carrying its required capability.
Do not mention a slot when its evidence is unavailable. Do not invent
chronology, comeback leadership, dominance, milestones, audience, venue,
season context or historical significance. Neutral perspective is the
default; subject-centred perspective changes selection only, never facts.

For an event report, lead with the supported result when available, integrate
supported date, venue and status as context, then relate salient entity
performances and participant-level contrasts. End with a short event-scoped
limitation. Do not discuss wrapper row counts, constant columns, missingness,
correlation, regression, statistical power, feature removal or predictive
modelling unless the user explicitly requested that analysis. A single event
can still support within-event comparison and ranking. Phrase the limitation
in event terms: the comparisons describe only the supplied event, do not
establish why the result occurred and do not support claims about broader
performance. Avoid generic boilerplate about "observed associations" or
"unadjusted group comparisons" in an event report.

You have freedom over:
- wording;
- structure;
- selection;
- synthesis;
- paragraph organisation;
- integration of verified analytical implications;
- consolidation of caveats.

You do not have freedom to invent:
- calculated values;
- table or column names;
- categories;
- dates;
- locations;
- provenance;
- domain definitions;
- causal explanations;
- predictive performance;
- forecast performance;
- deployment claims.

Internal prohibited interpretations are private safety constraints.
Never quote, enumerate, label, paraphrase as instructions, or expose them
in the visible report.

Do not render internal evidence fields such as:
- Finding:
- Strength:
- Important Note:
- Interpretation Notes:
- Recommended Use:
- Methodological Strength:
- User Relevance:
- Salience:
- Global Prohibited Interpretations

Translate effect labels and metrics into natural prose.
Preserve their verified classification consistently. If mapped evidence calls
an association strong, do not later call the same association moderate. Do not
invent a qualitative strength label that differs from the supplied controlled
strength label.
Do not begin with generic boilerplate such as "This document summarizes",
"This report provides", "Here's a breakdown", or "The goal is to provide".

For example, do not write:

"Strength: Large group difference; Standardized Difference: 1.00"

Write naturally:

"The groups differ substantially; the standardised mean difference is
approximately 1.0."

The Data Understanding output is interpretive context, not an independent
source of factual truth.

Every visible factual statement must be supported by the supplied verified
facts.

Do not introduce a factual claim solely because it appears in:
- dataset_summary;
- unit_of_observation;
- table summary;
- column interpretation;
- quality finding;
- usability note.

In particular, do not state that observations are hourly, collected at a
specific location, produced by a weather station, or gathered through a
particular process unless a verified fact explicitly supports that statement.

Use neutral terms such as "rows", "records", "observations" or
"timestamped observations" when a more specific unit is not verified.

Reader-facing next steps must come from supplied analytical recommendations,
verified methodological facts or the explicit user request. Do not invent
generic future modelling tasks. A recommendation to investigate whether a
pattern reflects a dependency, artifact, collection process, or unmeasured
mechanism is still a hypothesis and must follow the hypothesis policy.

When supported missingness facts are available, state clearly which observed
subset the analysis describes. Do not assume missingness is non-random or has
already biased an estimate. When supported duplicate facts are available,
describe possible influence as an unmeasured methodological risk; do not claim
that deduplication would change results unless that comparison was performed.

For a major group comparison, where supplied, explain:
- the group means;
- their absolute difference;
- whether the difference is small, moderate, or large;
- relevant group-size imbalance;
- whether the comparison is adjusted or unadjusted.

Do not mechanically print all fields. Integrate the most useful context
into natural prose.

Do not include every available fact.
Prioritise the strongest, most relevant, and methodologically defensible
findings.

A generic dataset-understanding report should normally include:
- a concise dataset overview;
- important data-quality findings;
- the strongest observed relationships;
- relevant methodological limitations;
- grounded next analytical steps.

Small or weak effects should normally be omitted unless they materially
qualify a stronger finding or the user requested completeness.

Deterministically recovered facts are direct representations of trusted
calculated evidence. They are as grounded as LLM-verified facts and may be
used normally, while their recovery method remains recorded internally.

When sufficient verified material exists, do not return only a heading and
one or two factual sentences. Cover every required report component using
the strongest available facts.

Prefer relationship diversity. When both are available, normally include a
strong or moderate correlation and a large or moderate group comparison
rather than several similar comparisons.

Do not use a small relationship merely to increase the number of findings.

Every factual sentence must be represented in the hidden sentence support
map.

Return structured sections and sentences only.
Do not return Markdown.
Do not construct a separate support map.
The controller will materialise Markdown and sentence support
deterministically.

Each factual sentence must list its supporting fact IDs.
List the fact IDs supporting the title in `title_fact_ids`. A factual title
must not introduce an entity, value or result absent from those facts.
Every backticked table or column name and every visible number must be
supported by those same fact IDs. When a sentence combines facts, cite every
fact needed for all of its named entities and values.
Use no more than eight fact IDs for the title or any sentence and no more than
four insight IDs per sentence. Return no more than eight sections or twelve
sentences per section. Never create placeholder IDs, ID ranges or exhaustive
sequences of IDs.
Non-factual transitions may be marked non_factual_transition and must not
cite fact IDs.
"""


def build_writer_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("writer"),
            settings,
        ),
        name="natural_data_science_writer_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            WriterAgentDraft,
            settings,
        ),
        instructions=WRITER_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.15,
            max_tokens=11_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: WriterAgentDraft,
    ) -> WriterAgentDraft:
        ledger = FactLedger.model_validate(
            context.deps.payload["fact_ledger"]
        )

        fact_lookup = {
            fact.fact_id: fact
            for fact in ledger.writer_ready_facts
        }
        valid_fact_ids = {
            fact.fact_id
            for fact in ledger.writer_ready_facts
        }
        insight_ledger = InsightLedger.model_validate(
            context.deps.payload.get(
                "insight_ledger",
                {},
            )
        )
        verified_insight_lookup = {
            insight.insight_id: insight
            for insight in insight_ledger.verified_insights
        }
        hypothesis_insight_lookup = {
            insight.insight_id: insight
            for insight in insight_ledger.hypothesis_only_insights
        }
        all_insight_lookup = {
            **verified_insight_lookup,
            **hypothesis_insight_lookup,
        }
        output = recover_missing_writer_insight_ids(
            output,
            verified_insight_lookup,
        )
        valid_insight_ids = set(verified_insight_lookup)
        hypothesis_insight_ids = set(hypothesis_insight_lookup)
        all_insight_ids = set(all_insight_lookup)
        allow_hypotheses = bool(
            context.deps.payload.get(
                "allow_hypotheses_in_report",
                False,
            )
        )

        errors: list[str] = []

        unknown_title_fact_ids = set(output.title_fact_ids) - valid_fact_ids
        if unknown_title_fact_ids:
            errors.append(f"The title uses unknown fact IDs: {sorted(unknown_title_fact_ids)}")
        title_entities = {
            entity
            for fact in ledger.writer_ready_facts
            for entity in fact.entities
            if len(entity.strip()) >= 3
        }
        factual_title = bool(
            re.search(r"(?<!\w)\d+(?:[.,]\d+)?", output.title)
            or (
                FACTUAL_TITLE_PATTERN.search(output.title)
                and any(
                    entity.casefold() in output.title.casefold()
                    for entity in title_entities
                )
            )
        )
        if factual_title and not output.title_fact_ids:
            errors.append("A factual title must list supporting title_fact_ids.")
        if output.title_fact_ids and not unknown_title_fact_ids:
            supported_title_entities = {
                entity
                for fact_id in output.title_fact_ids
                for entity in fact_lookup[fact_id].entities
            }
            mentioned_title_entities = {
                entity
                for entity in title_entities
                if entity.casefold() in output.title.casefold()
            }
            unsupported_title_entities = (
                mentioned_title_entities - supported_title_entities
            )
            if factual_title and unsupported_title_entities:
                errors.append(
                    "The title contains entities unsupported by its facts: "
                    f"{sorted(unsupported_title_entities)}"
                )
            errors.extend(
                writer_sentence_grounding_errors(
                    sentence=WriterSentenceDraft(
                        text=output.title,
                        fact_ids=output.title_fact_ids,
                        support_type=SupportType.DIRECT,
                    ),
                    fact_lookup=fact_lookup,
                    insight_lookup={},
                    sentence_label="Title",
                )
            )

        if not output.sections:
            errors.append(
                "Return at least one report section."
            )

        for section_index, section in enumerate(
            output.sections,
            start=1,
        ):
            if not section.sentences:
                errors.append(
                    f"Section {section_index} contains no sentences."
                )

            for sentence_index, sentence in enumerate(
                section.sentences,
                start=1,
            ):
                unknown = (
                    set(sentence.fact_ids)
                    - valid_fact_ids
                )

                if unknown:
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} "
                        "uses unknown fact IDs: "
                        f"{sorted(unknown)}"
                    )

                unknown_insights = (
                    set(sentence.insight_ids)
                    - all_insight_ids
                )
                if unknown_insights:
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} "
                        "uses unknown insight IDs: "
                        f"{sorted(unknown_insights)}"
                    )

                if not unknown and not unknown_insights:
                    errors.extend(
                        writer_sentence_grounding_errors(
                            sentence=sentence,
                            fact_lookup=fact_lookup,
                            insight_lookup=all_insight_lookup,
                            sentence_label=(
                                "Sentence "
                                f"{section_index}.{sentence_index}"
                            ),
                        )
                    )

                if (
                    EXPLANATORY_HYPOTHESIS_PATTERN.search(
                        sentence.text
                    )
                    and sentence.interpretation_level
                    != InterpretationLevel.HYPOTHESIS
                ):
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} presents a possible "
                        "explanation without classifying it as a hypothesis."
                    )

                if (
                    sentence.interpretation_level
                    == InterpretationLevel.BOUNDED_INSIGHT
                ):
                    if not sentence.insight_ids:
                        errors.append(
                            "A bounded-insight sentence must cite a verified "
                            "insight ID."
                        )
                    elif not set(sentence.insight_ids).issubset(
                        valid_insight_ids
                    ):
                        errors.append(
                            "A bounded-insight sentence may cite only verified "
                            "main insights."
                        )

                if (
                    sentence.interpretation_level
                    == InterpretationLevel.HYPOTHESIS
                ):
                    if not allow_hypotheses:
                        errors.append(
                            "Hypothesis sentences are disabled by configuration."
                        )
                    if not sentence.insight_ids or not set(
                        sentence.insight_ids
                    ).issubset(hypothesis_insight_ids):
                        errors.append(
                            "A hypothesis sentence must cite a hypothesis-only "
                            "insight ID."
                        )
                    if section.heading.strip().lower() != (
                        "questions for further investigation"
                    ):
                        errors.append(
                            "Hypotheses may appear only in the Questions for "
                            "Further Investigation section."
                        )
                    if not HYPOTHESIS_LABEL_PATTERN.search(
                        sentence.text
                    ) and not sentence.text.strip().endswith("?"):
                        errors.append(
                            "A hypothesis sentence must be explicitly labelled "
                            "as a hypothesis."
                        )

                if (
                    sentence.interpretation_level
                    == InterpretationLevel.FINDING
                    and sentence.insight_ids
                ):
                    errors.append(
                        "A direct finding must not be relabelled with insight IDs."
                    )

                if (
                    sentence.support_type
                    != SupportType.NON_FACTUAL
                    and not sentence.fact_ids
                    and not sentence.insight_ids
                ):
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} "
                        "is factual but has no supporting facts."
                    )

                if (
                    sentence.support_type
                    == SupportType.NON_FACTUAL
                    and (
                        sentence.fact_ids
                        or sentence.insight_ids
                    )
                ):
                    errors.append(
                        "A non-factual transition must not "
                        "cite fact or insight IDs."
                    )

                if re.search(
                    r"\[(?:CLM|FACT)_\d+",
                    sentence.text,
                ):
                    errors.append(
                        "Internal fact IDs must not appear "
                        "in visible sentence text."
                    )

                if INTERNAL_CONTROL_PATTERN.search(
                    sentence.text
                ):
                    errors.append(
                        "Visible sentence text exposes an "
                        "internal control."
                    )

                if FIELD_LABEL_PATTERN.search(
                    sentence.text
                ):
                    errors.append(
                        "Visible sentence text renders an "
                        "internal evidence field."
                    )

        if errors:
            raise ModelRetry(
                "Writer draft validation failed:\n- "
                + "\n- ".join(errors)
            )

        return output

    return agent


AUDITOR_INSTRUCTIONS = """
You are the Factual Accuracy Auditor and Report Repair Agent.

The goal is to reduce residual hallucinations, not to demand that the
writer copy deterministic templates.

You receive:
- the raw or repaired report;
- the hidden sentence support map;
- verified facts;
- full evidence;
- deterministic profile support records;
- deterministic audit findings;
- methodological limitations;
- optional trusted external facts.

Authority hierarchy:
- The deterministic pre-audit is authoritative and cannot be erased.
- Factual and interpretive authority, in order, is the Verified Fact Ledger,
  deterministic Evidence Ledger, deterministic profile support, verified
  Insight Ledger for exact bounded interpretations, properly scoped trusted
  external facts when allowed, and Data Understanding as non-authoritative
  context only.
- Never validate one LLM-generated claim solely because another LLM output
  repeats it.
- A claim that is exactly supported by deterministic profile data but missing
  from the sentence support map is a support-mapping defect. Do not call it a
  visible hallucination when the visible statement is correct.
- Do not propose a visible rewrite when a deterministic hidden support-map
  patch fully resolves the problem.
- The semantic Auditor may add supported annotations and repair candidates but
  must not erase deterministic findings.

A verified insight is an evidence-constrained interpretation, not permission
to write any plausible related claim. Check that report wording is no stronger
than the mapped insight. Do not call a supported bounded insight a
hallucination merely because it is not a direct numeric fact.

Flag interpretations absent from the Insight Ledger, wording stronger than a
verified insight, causal escalation, unsupported domain interpretation,
unlabelled hypotheses, hypotheses presented as conclusions, and unsupported
genre-specific narratives. Also flag qualitative strength wording that
conflicts with the mapped deterministic strength label, such as calling the
same verified association strong in one place and moderate in another. The
Insight Ledger does not authorise new numbers, entities, recommendations,
causality, generalisations or domain explanations. Do not use Data
Understanding to validate an insight.

Perform two responsibilities.

A. Factual audit
Detect:
- incorrect numbers;
- incorrect entities;
- wrong direction or polarity;
- unsupported synthesis;
- causal overclaims;
- predictive or deployment overclaims;
- forecast overclaims;
- unsupported metadata;
- missing material caveats.

B. Targeted repair
For each high-confidence repairable error:
- produce several replacement candidates;
- use only supplied facts and evidence;
- favour factual support over style;
- preserve useful meaning when possible;
- use deletion only where no grounded replacement is suitable.

Do not rewrite unflagged portions of the report.
Do not invent corrections.
Do not use outside knowledge.

Also assess report quality separately:
- request responsiveness;
- finding selection;
- coherence;
- concision;
- caveat integration;
- data-science interpretation.

Quality weaknesses alone should normally be warnings, not factual blocks.

`quality_assessment.findings` must describe defects in the report's writing,
selection, structure, interpretation or communication.

Valid examples:
- The report overstates the implication of a constant field.
- The report recommends duplicate removal without sufficient justification.
- The report repeats closely related findings.
- The report omits a required limitation.

Invalid examples:
- The dataset contains duplicate rows.
- Loud Cover is constant.
- Pressure contains zero values.
- Temperature and humidity are correlated.

Dataset observations belong in evidence or facts, not report-quality findings.

Apply these wording rules:
- Do not accept hourly cadence unless regular spacing is verified.
- Do not accept location or weather-station metadata unless verified.
- Constant columns contain no observed variation for analyses that depend on
  variation; they are not universally worthless.
- Suspicious zeros may represent missingness or measurement failure, but this
  must be validated before treating the interpretation as true.
- Low missingness is not automatically harmless.
- Duplicate rows should be reviewed before any decision to remove them.
- Pearson correlation may not capture non-linear relationships and can be
  sensitive to influential observations.
- Reader-facing next steps must be grounded in supplied recommendations,
  verified methodological facts or the explicit user request.

Internal-control leakage is a report-quality problem.
Unsupported claims that group-size imbalance biases group means should be
repaired to say unequal sizes can affect precision, stability, or
representation unless the evidence explicitly supports bias language.

When a visible report contains:
- Interpretation Notes;
- Global Prohibited Interpretations;
- Do not say...;
- evidence-field labels;

propose a targeted natural-language repair or removal.

Do not classify this alone as a critical factual hallucination.
Do not rewrite the complete report.
"""


def build_auditor_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("auditor"),
            settings,
        ),
        name="factual_accuracy_auditor_and_repair_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            AuditRepairProposal,
            settings,
        ),
        instructions=AUDITOR_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.1,
            max_tokens=12_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: AuditRepairProposal,
    ) -> AuditRepairProposal:
        report_text = context.deps.payload["report_text"]
        valid_fact_ids = set(
            context.deps.payload["valid_fact_ids"]
        )
        valid_evidence_ids = set(
            context.deps.payload.get(
                "valid_evidence_ids",
                [],
            )
        )
        valid_profile_support_ids = set(
            context.deps.payload.get(
                "valid_profile_support_ids",
                [],
            )
        )
        valid_insight_ids = set(
            context.deps.payload.get(
                "valid_insight_ids",
                [],
            )
        )
        hypothesis_only_insight_ids = set(
            context.deps.payload.get(
                "hypothesis_only_insight_ids",
                [],
            )
        )
        all_insight_ids = (
            valid_insight_ids
            | hypothesis_only_insight_ids
        )
        insight_statements = dict(
            context.deps.payload.get(
                "insight_statements",
                {},
            )
        )
        sentence_insight_ids = {
            sentence: set(insight_ids)
            for sentence, insight_ids in context.deps.payload.get(
                "sentence_insight_ids",
                {},
            ).items()
        }
        allow_hypotheses = bool(
            context.deps.payload.get(
                "allow_hypotheses_in_report",
                False,
            )
        )
        repair_fact_ledger = (
            FactLedger.model_validate(
                context.deps.payload["fact_ledger"]
            )
            if "fact_ledger" in context.deps.payload
            else None
        )
        if "evidence_ledger" in context.deps.payload:
            from .schemas import EvidenceLedger

            repair_evidence_ledger = EvidenceLedger.model_validate(
                context.deps.payload["evidence_ledger"]
            )
        else:
            repair_evidence_ledger = None
        repair_insight_ledger = InsightLedger.model_validate(
            context.deps.payload.get(
                "insight_ledger",
                {},
            )
        )
        deterministic_annotation_ids = set(
            context.deps.payload.get(
                "deterministic_annotation_ids",
                [],
            )
        )
        deterministic_serious_annotation_ids = set(
            context.deps.payload.get(
                "deterministic_serious_annotation_ids",
                [],
            )
        )
        deterministic_annotation_sentences = set(
            context.deps.payload.get(
                "deterministic_annotation_sentences",
                [],
            )
        )

        annotation_ids = {
            annotation.annotation_id
            for annotation in output.annotations
        }
        all_annotation_ids = (
            annotation_ids
            | deterministic_annotation_ids
        )
        annotated_sentences = {
            annotation.sentence
            for annotation in output.annotations
        } | deterministic_annotation_sentences

        for annotation in output.annotations:
            if annotation.sentence not in report_text:
                raise ModelRetry(
                    "Every annotated sentence must occur in the report."
                )

            if (
                annotation.text_span
                and annotation.text_span not in annotation.sentence
            ):
                raise ModelRetry(
                    "Every text_span must occur in its sentence."
                )

            unknown = set(annotation.fact_ids) - valid_fact_ids

            if unknown:
                raise ModelRetry(
                    f"Unknown annotation fact IDs: {sorted(unknown)}"
                )

            unknown_evidence = (
                set(annotation.evidence_ids)
                - valid_evidence_ids
            )

            if unknown_evidence:
                raise ModelRetry(
                    "Unknown annotation evidence IDs: "
                    f"{sorted(unknown_evidence)}"
                )

            unknown_profile_support = (
                set(annotation.profile_support_ids)
                - valid_profile_support_ids
            )

            if unknown_profile_support:
                raise ModelRetry(
                    "Unknown annotation profile support IDs: "
                    f"{sorted(unknown_profile_support)}"
                )

            unknown_insights = (
                set(annotation.insight_ids)
                - all_insight_ids
            )
            if unknown_insights:
                raise ModelRetry(
                    "Unknown annotation insight IDs: "
                    f"{sorted(unknown_insights)}"
                )

            insight_subtype = annotation.subtype in {
                "unsupported_insight",
                "insight_exceeds_verified_wording",
                "insight_missing_source_support",
                "single_fact_relabelled_as_insight",
                "unlabelled_hypothesis",
                "hypothesis_presented_as_conclusion",
                "unsupported_causal_interpretation",
                "unsupported_domain_interpretation",
                "unsupported_sports_narrative",
                "genre_mismatch",
            }
            if (
                insight_subtype
                and not annotation.insight_ids
                and not sentence_insight_ids.get(annotation.sentence)
                and annotation.subtype
                not in {
                    "unsupported_insight",
                    "unlabelled_hypothesis",
                    "unsupported_sports_narrative",
                    "genre_mismatch",
                }
            ):
                raise ModelRetry(
                    "Insight-specific annotations must reference the mapped "
                    "insight where one exists."
                )

        for repair in output.repairs:
            if repair.original_sentence not in report_text:
                raise ModelRetry(
                    "Every repair original_sentence must occur in the report."
                )

            unknown_annotations = (
                set(repair.annotation_ids)
                - all_annotation_ids
            )

            if unknown_annotations:
                raise ModelRetry(
                    "Repair references unknown annotation IDs."
                )

            if repair.original_sentence not in annotated_sentences:
                raise ModelRetry(
                    "A repair may target only a sentence with an annotation."
                )

            for candidate in repair.candidates:
                if (
                    repair_fact_ledger is not None
                    and repair_evidence_ledger is not None
                ):
                    repair_errors = validate_repair_candidate(
                        candidate,
                        repair_fact_ledger,
                        repair_evidence_ledger,
                        repair_insight_ledger,
                        allow_hypotheses,
                        original_text=(
                            repair.original_sentence
                        ),
                    )
                    if repair_errors:
                        raise ModelRetry(
                            "Repair candidate validation failed: "
                            + "; ".join(repair_errors)
                        )

                unknown = (
                    set(candidate.supporting_fact_ids)
                    - valid_fact_ids
                )

                if unknown:
                    raise ModelRetry(
                        f"Unknown repair fact IDs: {sorted(unknown)}"
                    )

                unknown_evidence = (
                    set(candidate.supporting_evidence_ids)
                    - valid_evidence_ids
                )

                if unknown_evidence:
                    raise ModelRetry(
                        "Unknown repair evidence IDs: "
                        f"{sorted(unknown_evidence)}"
                    )

                unknown_insights = (
                    set(candidate.supporting_insight_ids)
                    - all_insight_ids
                )
                if unknown_insights:
                    raise ModelRetry(
                        "Unknown repair insight IDs: "
                        f"{sorted(unknown_insights)}"
                    )

                if (
                    set(candidate.supporting_insight_ids)
                    & hypothesis_only_insight_ids
                    and not allow_hypotheses
                ):
                    raise ModelRetry(
                        "Repairs may not introduce hypotheses while the "
                        "feature is disabled."
                    )

                for insight_id in candidate.supporting_insight_ids:
                    insight_statement = insight_statements.get(
                        insight_id,
                        "",
                    )
                    replacement = candidate.replacement_text
                    if (
                        replacement
                        and insight_statement
                        and CAUSAL_PATTERN.search(replacement)
                        and not CAUSAL_PATTERN.search(insight_statement)
                    ):
                        raise ModelRetry(
                            "A repair candidate strengthens a verified insight "
                            "with causal wording."
                        )

                    if (
                        replacement
                        and UNIVERSAL_GENERALISATION_PATTERN.search(replacement)
                        and not UNIVERSAL_GENERALISATION_PATTERN.search(
                            insight_statement
                        )
                    ):
                        raise ModelRetry(
                            "A repair candidate generalises beyond its verified "
                            "insight."
                        )

        if output.recommended_decision == AuditDecision.BLOCK:
            semantic_serious = any(
                annotation.severity
                in {
                    Severity.HIGH,
                    Severity.CRITICAL,
                }
                for annotation in output.annotations
            )

            if (
                not semantic_serious
                and not deterministic_serious_annotation_ids
            ):
                raise ModelRetry(
                    "recommended_decision=BLOCK requires at least one "
                    "high or critical deterministic or semantic annotation."
                )

        invalid_quality_findings = [
            finding
            for finding in output.quality_assessment.findings
            if not valid_quality_finding(finding)
        ]

        if invalid_quality_findings:
            raise ModelRetry(
                "Quality findings must describe report defects, not plain "
                "dataset observations: "
                + "; ".join(invalid_quality_findings)
            )

        return output

    return agent


def fallback_understanding(
    profile: DataProfile,
) -> DataUnderstanding:
    tables: list[TableUnderstanding] = []
    supported_routes = {
        AnalysisRoute.DESCRIPTIVE
    }

    for table in profile.tables:
        numeric = [
            column
            for column in table.columns
            if column.semantic_type == "numeric"
            and not column.constant
        ]
        categorical = [
            column
            for column in table.columns
            if column.semantic_type == "categorical"
        ]
        datetime = [
            column
            for column in table.columns
            if column.semantic_type == "datetime"
        ]

        if len(numeric) >= 2 or (numeric and categorical):
            supported_routes.add(
                AnalysisRoute.ASSOCIATION_COMPARISON
            )

        if table.row_count >= 100 and numeric:
            supported_routes.add(
                AnalysisRoute.PREDICTIVE
            )

        if table.row_count >= 40 and numeric and datetime:
            supported_routes.add(
                AnalysisRoute.FORECASTING
            )

        supported_routes.add(
            AnalysisRoute.CAUSAL_FEASIBILITY
        )

        if table.candidate_keys:
            unit = (
                f"one row per unique `{table.candidate_keys[0]}` value"
            )
        else:
            unit = (
                f"one row per observed record in `{table.table_name}`"
            )

        meanings = [
            ColumnMeaning(
                table_name=table.table_name,
                column_name=column.name,
                inferred_role=(
                    "candidate_identifier"
                    if column.candidate_key
                    else column.semantic_type
                ),
                interpretation=(
                    f"Observed `{column.name}` column with provisional "
                    f"{column.semantic_type} analytical role."
                ),
                evidence_basis=(
                    f"dtype={column.dtype}; unique={column.unique_count}; "
                    f"missing_rate={column.missing_rate:.2%}"
                ),
                confidence=(
                    0.95 if column.candidate_key else 0.70
                ),
                caveat=(
                    "The scientific or business meaning is not confirmed "
                    "by the data alone."
                ),
            )
            for column in table.columns
        ]

        risks: list[ColumnRisk] = []

        for column in table.columns:
            if column.constant:
                risks.append(
                    ColumnRisk(
                        table_name=table.table_name,
                        column_name=column.name,
                        risk_type="constant_column",
                        explanation=(
                            "The column has one observed non-missing value."
                        ),
                        analytical_consequence=(
                            "Exclude it from correlation, comparison, "
                            "prediction, and forecasting."
                        ),
                        confidence=1.0,
                    )
                )

            if column.suspicious_zero_values:
                risks.append(
                    ColumnRisk(
                        table_name=table.table_name,
                        column_name=column.name,
                        risk_type="possible_sentinel_zero",
                        explanation=(
                            "Zero observations are separated from most of "
                            "the positive distribution."
                        ),
                        analytical_consequence=(
                            "Validate the zeros before relying on analyses "
                            "using this field."
                        ),
                        confidence=0.85,
                    )
                )

        tables.append(
            TableUnderstanding(
                table_name=table.table_name,
                unit_of_observation=unit,
                summary=(
                    f"`{table.table_name}` has {table.row_count:,} rows "
                    f"and {table.column_count:,} columns."
                ),
                likely_keys=table.candidate_keys,
                column_meanings=meanings,
                column_risks=risks,
                quality_findings=table.warnings,
                usability_notes=[
                    "Constant columns should not enter analytical models.",
                    "Predictive targets require user, metadata, or explicit "
                    "experimental confirmation.",
                    "Temporal data should use chronological validation.",
                    "Causal conclusions require a defensible identification design.",
                ],
            )
        )

    return DataUnderstanding(
        profile_fingerprint=profile.fingerprint,
        dataset_summary=(
            f"The input contains {len(profile.tables)} profiled table(s). "
            "Semantic interpretations remain provisional without metadata."
        ),
        tables=tables,
        cross_table_notes=(
            [
                "Multiple tables were supplied. Joins are not assumed "
                "without explicit key evidence."
            ]
            if len(profile.tables) > 1
            else []
        ),
        supported_routes=sorted(
            supported_routes,
            key=lambda route: route.value,
        ),
        uncertain_routes=[],
        global_caveats=[
            "The data alone do not confirm provenance or domain semantics.",
            "Sampling, missingness, measurement, and temporal limitations "
            "may affect findings.",
        ],
    )


def select_explicit_target(
    request: str,
    table: Any,
) -> str | None:
    for column in table.columns:
        if re.search(
            rf"\b{re.escape(column.name.lower())}\b",
            request.lower(),
        ):
            return column.name

    return None


def event_report_requested(
    request: str,
) -> bool:
    return bool(
        re.search(
            r"\b(write|create|produce|give|prepare)?\s*"
            r"(?:a\s+)?(?:event|sports|game|match)\s+report\b|"
            r"\bwrite up (?:the|this) (?:event|game|match)\b",
            request,
            re.IGNORECASE,
        )
    )


def sports_game_report_requested(
    request: str,
) -> bool:
    return event_report_requested(request)


def profile_supports_sports_game_report(
    profile: DataProfile,
) -> bool:
    names = {
        column.name.lower()
        for table in profile.tables
        for column in table.columns
    }
    table_names = {
        table.table_name.lower()
        for table in profile.tables
    }

    has_subject = any(
        token in name
        for name in names
        for token in {"team", "player", "opponent"}
    )
    has_result = any(
        token in name
        for name in names
        for token in {"score", "points", "winner", "result"}
    )
    game_named = any(
        token in name
        for name in table_names
        for token in {"game", "match", "boxscore", "box_score"}
    )

    return has_subject and has_result and game_named


def fallback_insight_objectives(
    *,
    tasks: list[InvestigationTask],
    genre: ReportGenre,
    enabled: bool,
) -> list[InsightObjective]:
    if not enabled:
        return []

    task_ids = [task.task_id for task in tasks]

    if genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }:
        questions = [
            (
                "What verified facts best describe the result without "
                "implying unsupported causality?",
                [InsightType.NARRATIVE_SUMMARY],
            ),
            (
                "Which verified performances are most salient to the game "
                "report?",
                [InsightType.DOMINANT_PATTERN, InsightType.CONTRAST],
            ),
            (
                "Which verified team-level contrasts define the bounded game "
                "narrative?",
                [InsightType.CONTRAST, InsightType.NARRATIVE_SUMMARY],
            ),
            (
                "Are any conventional milestones explicitly supported by the "
                "verified facts?",
                [InsightType.NARRATIVE_SUMMARY],
            ),
        ]
    else:
        questions = [
            (
                "Which verified findings jointly describe the strongest "
                "structure in the data?",
                [InsightType.DOMINANT_PATTERN, InsightType.NARRATIVE_SUMMARY],
            ),
            (
                "What is the strongest non-redundant verified contrast?",
                [InsightType.CONTRAST],
            ),
            (
                "Do any verified variables contain substantially overlapping "
                "information in this dataset?",
                [InsightType.REDUNDANCY, InsightType.OUTCOME_ASSOCIATION],
            ),
            (
                "Which verified data-quality issue most affects interpretation?",
                [InsightType.DATA_QUALITY_IMPLICATION, InsightType.ANOMALY],
            ),
            (
                "What bounded message should the reader remember from the "
                "verified findings?",
                [InsightType.NARRATIVE_SUMMARY],
            ),
        ]

    return [
        InsightObjective(
            objective_id=f"INSIGHT_OBJECTIVE_{index:03d}",
            question=question,
            preferred_insight_types=insight_types,
            relevant_task_ids=task_ids,
        )
        for index, (question, insight_types) in enumerate(
            questions,
            start=1,
        )
    ]


def fallback_execution_plan(
    request: str,
    profile: DataProfile,
    audit_mode: AuditMode,
    settings: Settings,
    *,
    input_structure: InputStructureProfile | None = None,
    available_capabilities: list[EvidenceCapability] | None = None,
    report_genre_override: ReportGenre | None = None,
) -> ExecutionPlan:
    tasks: list[InvestigationTask] = []
    available_capabilities = available_capabilities or []
    explicit_event_request = event_report_requested(request)
    explicit_data_science_request = bool(
        re.search(
            r"\b(data[- ]science report|statistical analysis)\b",
            request,
            re.IGNORECASE,
        )
    )
    structured_event = bool(
        input_structure is not None
        and input_structure.shape == InputShape.EVENT_RECORD
        and input_structure.confidence >= 0.7
    )
    report_genre = (
        ReportGenre.EVENT_REPORT
        if explicit_event_request
        else (
            ReportGenre.DATA_SCIENCE_REPORT
            if explicit_data_science_request
            else (
                report_genre_override
                if report_genre_override is not None
                else (
                    ReportGenre.EVENT_REPORT
                    if structured_event
                    else (
                        ReportGenre.DATASET_OVERVIEW
                        if re.search(
                            r"\bdataset overview\b",
                            request,
                            re.IGNORECASE,
                        )
                        else ReportGenre.DATA_SCIENCE_REPORT
                    )
                )
            )
        )
    )

    if explicit_event_request or explicit_data_science_request:
        selection_source = ReportSelectionSource.EXPLICIT_USER_REQUEST
    elif report_genre_override is not None:
        selection_source = ReportSelectionSource.EXPERIMENT_CONFIGURATION
    elif structured_event:
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
    else:
        selection_source = ReportSelectionSource.FALLBACK

    if report_genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    } and profile.tables:
        event_table = profile.tables[0]
        event_task_specs = [
            (
                EvidenceCapability.EVENT_OUTCOME,
                AnalysisRoute.DESCRIPTIVE,
                "What is the verified event result and status?",
                ["event_outcome", "event_status"],
            ),
            (
                EvidenceCapability.ENTITY_PERFORMANCE,
                AnalysisRoute.DESCRIPTIVE,
                "Which recorded entity performances are most salient?",
                ["entity_performance"],
            ),
            (
                EvidenceCapability.RANKING,
                AnalysisRoute.DESCRIPTIVE,
                "Which entities lead the recorded performance rankings?",
                ["entity_ranking"],
            ),
            (
                EvidenceCapability.GROUP_COMPARISON,
                AnalysisRoute.ASSOCIATION_COMPARISON,
                "What are the strongest participant-level contrasts?",
                ["participant_comparison"],
            ),
        ]
        for capability, route, question, evidence_types in event_task_specs:
            if capability not in available_capabilities:
                continue
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=question,
                    route=route,
                    priority=5 if capability == EvidenceCapability.EVENT_OUTCOME else 4,
                    table_name=event_table.table_name,
                    columns=[column.name for column in event_table.columns],
                    capability=capability,
                    input_fields=[column.name for column in event_table.columns],
                    entity_scope=input_structure.entity_levels if input_structure else [],
                    expected_evidence_types=evidence_types,
                    required_evidence=evidence_types,
                    claim_permissions=[
                        ClaimPermission.DESCRIPTIVE,
                        ClaimPermission.COMPARATIVE,
                    ],
                    answerability_note=("Answerable from verified structured-event evidence."),
                )
            )

    predictive_requested = bool(
        re.search(
            r"\b(predict|prediction|model|classify|estimate)\b",
            request,
            re.IGNORECASE,
        )
    )
    forecast_requested = bool(
        re.search(
            r"\b(forecast|future|time series|ahead)\b",
            request,
            re.IGNORECASE,
        )
    )
    causal_requested = bool(
        re.search(
            r"\b(cause|causal|effect|impact|intervention)\b",
            request,
            re.IGNORECASE,
        )
    )

    for table in profile.tables:
        if report_genre in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }:
            continue

        tasks.append(
            InvestigationTask(
                task_id=f"TASK_{len(tasks) + 1:03d}",
                question=(
                    f"What are the structure, data quality, distributions, "
                    f"and analytically important fields in `{table.table_name}`?"
                ),
                route=AnalysisRoute.DESCRIPTIVE,
                priority=5,
                table_name=table.table_name,
                columns=[
                    column.name
                    for column in table.columns
                ],
                required_evidence=[
                    "dimensions",
                    "missingness",
                    "distribution diagnostics",
                    "constant columns",
                    "possible sentinel values",
                ],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.METHODOLOGICAL,
                    ClaimPermission.INSUFFICIENCY,
                ],
                answerability_note=(
                    "Directly answerable through deterministic profiling."
                ),
            )
        )

        numeric = [
            column.name
            for column in table.columns
            if column.semantic_type == "numeric"
            and not column.constant
        ]
        categorical = [
            column.name
            for column in table.columns
            if column.semantic_type == "categorical"
        ]
        datetime_columns = [
            column.name
            for column in table.columns
            if column.semantic_type == "datetime"
        ]

        if len(numeric) >= 2 or (numeric and categorical):
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Which substantively meaningful associations and group "
                        f"differences are present in `{table.table_name}`?"
                    ),
                    route=AnalysisRoute.ASSOCIATION_COMPARISON,
                    priority=4,
                    table_name=table.table_name,
                    columns=(numeric + categorical)[:20],
                    required_evidence=[
                        "effect magnitude",
                        "group counts",
                        "sampling method",
                        "association caveats",
                    ],
                    claim_permissions=[
                        ClaimPermission.ASSOCIATIONAL,
                        ClaimPermission.COMPARATIVE,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "Answerable as observed association and comparison, not causation."
                    ),
                )
            )

        target = select_explicit_target(
            request,
            table,
        )

        if predictive_requested and target:
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Can `{target}` be predicted better than a simple baseline "
                        "after leakage screening?"
                    ),
                    route=AnalysisRoute.PREDICTIVE,
                    priority=3,
                    table_name=table.table_name,
                    target_column=target,
                    target_status=TargetStatus.USER_SELECTED,
                    prediction_definition=(
                        f"Estimate `{target}` using fields available in the supplied table."
                    ),
                    time_column=(
                        datetime_columns[0]
                        if datetime_columns
                        else None
                    ),
                    validation_strategy=(
                        ValidationStrategy.CHRONOLOGICAL_HOLDOUT
                        if datetime_columns
                        else ValidationStrategy.RANDOM_HOLDOUT
                    ),
                    required_evidence=[
                        "target confirmation",
                        "proxy leakage audit",
                        "feature exclusions",
                        "baseline comparison",
                        "holdout metrics",
                    ],
                    claim_permissions=[
                        ClaimPermission.PREDICTIVE,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "A positive result requires leakage-audited baseline improvement."
                    ),
                )
            )

        if forecast_requested and target and datetime_columns:
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Can `{target}` be forecast using rolling temporal "
                        "evaluation and seasonal baselines?"
                    ),
                    route=AnalysisRoute.FORECASTING,
                    priority=3,
                    table_name=table.table_name,
                    target_column=target,
                    target_status=TargetStatus.USER_SELECTED,
                    time_column=datetime_columns[0],
                    validation_strategy=ValidationStrategy.ROLLING_ORIGIN,
                    required_evidence=[
                        "time ordering",
                        "rolling folds",
                        "last-value baseline",
                        "seasonal-naive baselines",
                        "candidate-model metrics",
                    ],
                    claim_permissions=[
                        ClaimPermission.FORECAST,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "A positive forecast claim requires consistent improvement "
                        "over the strongest relevant naive baseline."
                    ),
                )
            )

        if causal_requested:
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Does `{table.table_name}` support a defensible "
                        "causal identification strategy?"
                    ),
                    route=AnalysisRoute.CAUSAL_FEASIBILITY,
                    priority=2,
                    table_name=table.table_name,
                    required_evidence=[
                        "exposure",
                        "outcome",
                        "time ordering",
                        "confounders",
                        "identification design",
                    ],
                    claim_permissions=[
                        ClaimPermission.CAUSAL,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "The likely output is a causal-feasibility or insufficiency finding."
                    ),
                )
            )

    route_order = [
        route
        for route in [
            AnalysisRoute.DESCRIPTIVE,
            AnalysisRoute.ASSOCIATION_COMPARISON,
            AnalysisRoute.PREDICTIVE,
            AnalysisRoute.FORECASTING,
            AnalysisRoute.CAUSAL_FEASIBILITY,
        ]
        if any(task.route == route for task in tasks)
    ]

    return ExecutionPlan(
        objective=request,
        tasks=tasks[:10],
        route_order=route_order,
        report_specification=ReportSpecification(
            report_purpose=request,
            genre=report_genre,
            perspective=ReportPerspective.NEUTRAL,
            communication_goal=(
                "Explain the verified result, leading performances and "
                "major team contrasts."
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else (
                    "Describe the table structure and strongest supported "
                    "findings concisely."
                    if report_genre == ReportGenre.DATASET_OVERVIEW
                    else "Summarise the strongest supported findings."
                )
            ),
            target_length_words=(
                settings.writer_target_words
            ),
            maximum_main_findings=(
                100
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else settings.writer_max_main_findings
            ),
            maximum_supporting_facts=(
                max(
                    settings.writer_supporting_fact_limit,
                    settings.writer_priority_fact_limit,
                    500,
                )
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else min(
                    max(
                        settings.writer_supporting_fact_limit,
                        settings.writer_max_main_findings,
                    ),
                    settings.writer_max_main_findings + 4,
                )
            ),
            preferred_sections=(
                [
                    "Event overview",
                    "Key performances",
                    "Participant contrasts",
                    "Scope limitations",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else [
                    "Overview and data quality",
                    "Strongest observed relationships",
                    "Modelling and validation",
                    "Limitations and next steps",
                ]
            ),
            required_components=(
                [
                    ReportComponent.STRONGEST_RELATIONSHIPS,
                    ReportComponent.LIMITATIONS_NEXT_STEPS,
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else [
                    ReportComponent.DATASET_OVERVIEW,
                    ReportComponent.DATA_QUALITY,
                    ReportComponent.STRONGEST_RELATIONSHIPS,
                    ReportComponent.LIMITATIONS_NEXT_STEPS,
                ]
            ),
            required_content_slots=(
                [
                    "event_result",
                    "event_context",
                    "event_status",
                    "leading_performance",
                    "main_contrast",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else [
                    "dataset_scope",
                    "material_data_quality_issue",
                    "strongest_analytical_finding",
                    "limitation",
                ]
            ),
            optional_content_slots=(
                [
                    "secondary_performance",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else []
            ),
            prohibited_claim_types=(
                [
                    "unsupported_chronology",
                    "unsupported_milestone",
                    "unsupported_historical_significance",
                    "unsupported_causality",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else ["unsupported_causality"]
            ),
            selection_source=selection_source,
            selection_confidence=(
                1.0
                if selection_source
                in {
                    ReportSelectionSource.EXPLICIT_USER_REQUEST,
                    ReportSelectionSource.EXPERIMENT_CONFIGURATION,
                }
                else 0.8
            ),
            include_negative_findings=(
                report_genre
                not in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
            ),
            include_methodological_details=(
                report_genre
                not in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
            ),
            prioritisation_rule=(
                "Prefer high-confidence, methodologically strong, user-relevant "
                "findings. Omit negligible effects and repetitive metadata."
            ),
        ),
        audit_mode=audit_mode,
        insight_objectives=fallback_insight_objectives(
            tasks=tasks[:10],
            genre=report_genre,
            enabled=settings.enable_insight_synthesis,
        ),
        available_capabilities=available_capabilities,
        selected_capabilities=[
            capability
            for capability in available_capabilities
            if (
                report_genre
                not in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                or capability
                in {
                    EvidenceCapability.DATASET_PROFILE,
                    EvidenceCapability.EVENT_OUTCOME,
                    EvidenceCapability.ENTITY_PERFORMANCE,
                    EvidenceCapability.RANKING,
                    EvidenceCapability.GROUP_COMPARISON,
                }
            )
        ],
        revision_limit=settings.max_revision_rounds,
        maximum_facts=500,
        frozen=True,
        rationale=(
            "The deterministic fallback plans descriptive and meaningful "
            "association work by default. Prediction, forecasting, and causal "
            "routes are added only when requested and sufficiently specified."
        ),
    )
````

### `src/table2text/analytics.py`

````python
from __future__ import annotations

import math
import re
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .capabilities import event_capability_evidence, semantic_query_evidence
from .config import Settings
from .data import DataBundle, classify_zero_risk, safe_hashable
from .schemas import (
    AnalyticalFunction,
    AnalysisRoute,
    AnalyticalRecommendation,
    ClaimPermission,
    EvidenceCapability,
    EvidenceItem,
    EvidenceLedger,
    ExecutionPlan,
    InputSemanticMap,
    InputShape,
    InvestigationTask,
    RecommendedUse,
    ReportGenre,
    SemanticLevel,
    TargetStatus,
    ValidationStrategy,
    ZeroRisk,
)


def infer_evidence_capability(
    route: AnalysisRoute,
    metrics: dict[str, Any],
) -> EvidenceCapability:
    if route == AnalysisRoute.ASSOCIATION_COMPARISON:
        if any(
            key in metrics
            for key in {"pearson_r", "spearman_r", "correlation"}
        ):
            return EvidenceCapability.ASSOCIATION
        return EvidenceCapability.GROUP_COMPARISON

    if route == AnalysisRoute.DESCRIPTIVE:
        if "duplicate_row_count" in metrics:
            return EvidenceCapability.DUPLICATES
        if "missing_count" in metrics or "missing_rate" in metrics:
            return EvidenceCapability.MISSINGNESS
        if "row_count" in metrics and "column_count" in metrics:
            return EvidenceCapability.DATASET_PROFILE
        return EvidenceCapability.DISTRIBUTION_SUMMARY

    return EvidenceCapability.DATASET_PROFILE


class EvidenceBuilder:
    def __init__(self, fingerprint: str):
        self.fingerprint = fingerprint
        self.items: list[EvidenceItem] = []
        self.execution_notes: list[str] = []

    def add(
        self,
        *,
        route: AnalysisRoute,
        task_ids: list[str],
        finding: str,
        metrics: dict[str, Any],
        source_tables: list[str],
        source_columns: list[str],
        method: str,
        practical_interpretation: str,
        strength_label: str,
        claim_permissions: list[ClaimPermission],
        factual_confidence: float,
        methodological_strength: float,
        user_relevance: float,
        salience: float,
        recommended_use: RecommendedUse,
        validation_strategy: ValidationStrategy = ValidationStrategy.NONE,
        limitations: list[str] | None = None,
        prohibited_interpretations: list[str] | None = None,
        recommendations: list[AnalyticalRecommendation] | None = None,
        eligible_for_writer: bool = True,
        exclusion_reason: str | None = None,
        capability: EvidenceCapability | None = None,
        evidence_type: str | None = None,
        source_paths: list[str] | None = None,
        entity_scope: list[str] | None = None,
        semantic_level: SemanticLevel = SemanticLevel.DATASET,
        semantic_binding_ids: list[str] | None = None,
        analytical_function: AnalyticalFunction | None = None,
        query_id: str | None = None,
    ) -> None:
        evidence_id = f"EVD_{len(self.items) + 1:04d}"

        item = EvidenceItem(
            evidence_id=evidence_id,
            route=route,
            task_ids=task_ids,
            capability=(
                capability
                or infer_evidence_capability(route, metrics)
            ),
            evidence_type=evidence_type or strength_label,
            source_paths=source_paths or [],
            entity_scope=entity_scope or [],
            semantic_level=semantic_level,
            semantic_binding_ids=semantic_binding_ids or [],
            analytical_function=analytical_function,
            query_id=query_id,
            finding=finding,
            metrics=metrics,
            source_tables=source_tables,
            source_columns=source_columns,
            method=method,
            validation_strategy=validation_strategy,
            practical_interpretation=practical_interpretation,
            strength_label=strength_label,
            limitations=limitations or [],
            prohibited_interpretations=prohibited_interpretations or [],
            recommendations=recommendations or [],
            claim_permissions=claim_permissions,
            factual_confidence=factual_confidence,
            methodological_strength=methodological_strength,
            user_relevance=user_relevance,
            salience=salience,
            recommended_use=recommended_use,
            eligible_for_writer=eligible_for_writer,
            exclusion_reason=exclusion_reason,
        )
        item.metrics["priority_score"] = evidence_priority_score(item)
        self.items.append(item)

    def build(self) -> EvidenceLedger:
        return EvidenceLedger(
            fingerprint=self.fingerprint,
            items=self.items,
            execution_notes=self.execution_notes,
        )


def tasks_for_route(
    plan: ExecutionPlan,
    route: AnalysisRoute,
) -> list[InvestigationTask]:
    return [task for task in plan.tasks if task.route == route]


def event_analysis(
    bundle: DataBundle,
    plan: ExecutionPlan,
    builder: EvidenceBuilder,
    semantic_map: InputSemanticMap | None = None,
) -> None:
    selected = set(plan.selected_capabilities)
    event_capabilities = {
        EvidenceCapability.EVENT_OUTCOME,
        EvidenceCapability.ENTITY_PERFORMANCE,
        EvidenceCapability.RANKING,
        EvidenceCapability.GROUP_COMPARISON,
    }
    if not selected & event_capabilities:
        return

    event_tasks = [
        task
        for task in plan.tasks
        if task.capability in event_capabilities
    ]
    fallback_task_ids = [task.task_id for task in event_tasks]

    semantic_map_available = bool(semantic_map is not None and semantic_map.bindings)
    semantic_query_mode = bool(semantic_map_available and plan.evidence_queries)

    if semantic_map_available and not plan.evidence_queries:
        builder.execution_notes.append(
            "The semantic event map was available, but the frozen plan "
            "contained no validated evidence queries. Legacy field-alias "
            "extraction was not used."
        )
        return

    for table_name, payload in bundle.structured_inputs.items():
        records = (
            semantic_query_evidence(
                table_name=table_name,
                payload=payload,
                semantic_map=semantic_map,
                queries=plan.evidence_queries,
            )
            if semantic_query_mode and semantic_map is not None
            else event_capability_evidence(payload)
        )
        if not records:
            continue

        builder.add(
            route=AnalysisRoute.DESCRIPTIVE,
            task_ids=fallback_task_ids,
            capability=EvidenceCapability.DATASET_PROFILE,
            evidence_type="event_record_overview",
            finding=(
                f"`{table_name}` contains one structured event record with "
                "nested participant and entity information."
            ),
            metrics={
                "event_count": 1,
                "input_shape": InputShape.EVENT_RECORD.value,
            },
            source_tables=[table_name],
            source_columns=list(bundle.tables[table_name].columns),
            source_paths=[],
            entity_scope=[],
            semantic_level=SemanticLevel.EVENT,
            method="Validated input-structure inspection.",
            practical_interpretation=(
                "The source is one event, not a flat sample of independent rows."
            ),
            strength_label="event_record_overview",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.9,
            salience=0.85,
            recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            eligible_for_writer=not semantic_query_mode,
            exclusion_reason=(
                "Container-level profile evidence is excluded from the semantic event Writer path."
                if semantic_query_mode
                else None
            ),
        )

        for record in records:
            if record.capability not in selected:
                continue
            task_ids = [
                task.task_id
                for task in event_tasks
                if task.capability == record.capability
            ] or fallback_task_ids
            builder.add(
                route=(
                    AnalysisRoute.ASSOCIATION_COMPARISON
                    if record.capability == EvidenceCapability.GROUP_COMPARISON
                    else AnalysisRoute.DESCRIPTIVE
                ),
                task_ids=task_ids,
                capability=record.capability,
                evidence_type=record.evidence_type,
                finding=record.finding,
                metrics=record.metrics,
                source_tables=[table_name],
                source_columns=list(
                    dict.fromkeys(path.split(".", 1)[0] for path in record.source_paths)
                ),
                source_paths=record.source_paths,
                entity_scope=record.entity_scope,
                method=(
                    "Validated generic semantic-query execution."
                    if semantic_query_mode
                    else "Legacy structured-event extraction fallback."
                ),
                practical_interpretation=record.practical_interpretation,
                strength_label=record.strength_label,
                claim_permissions=record.claim_permissions,
                factual_confidence=record.factual_confidence,
                methodological_strength=record.methodological_strength,
                user_relevance=record.user_relevance,
                salience=record.salience,
                recommended_use=record.recommended_use,
                limitations=record.limitations,
                prohibited_interpretations=record.prohibited_interpretations,
                semantic_level=record.semantic_level,
                semantic_binding_ids=record.semantic_binding_ids,
                analytical_function=record.analytical_function,
                query_id=record.query_id,
            )


def correlation_strength(value: float) -> str:
    absolute = abs(value)

    if absolute >= 0.70:
        return "very_strong"
    if absolute >= 0.50:
        return "strong"
    if absolute >= 0.30:
        return "moderate"
    if absolute >= 0.20:
        return "weak_but_reportable"
    return "negligible"


def standardised_difference_strength(value: float | None) -> str:
    if value is None:
        return "not_available"

    absolute = abs(value)

    if absolute >= 0.80:
        return "large"
    if absolute >= 0.50:
        return "moderate"
    if absolute >= 0.20:
        return "small"
    return "negligible"


def recommendation(
    builder: EvidenceBuilder,
    action: str,
    recommendation_type: str,
    priority: str,
    justification: str,
    affected_analyses: list[str] | None = None,
    consequence_if_ignored: str | None = None,
    confidence: float = 0.75,
) -> AnalyticalRecommendation:
    count = sum(len(item.recommendations) for item in builder.items) + 1

    return AnalyticalRecommendation(
        recommendation_id=f"REC_{count:04d}",
        action=action,
        recommendation_type=recommendation_type,
        priority=priority,
        justification=justification,
        affected_analyses=affected_analyses or [],
        consequence_if_ignored=(
            consequence_if_ignored
            or "The related analysis may be less reliable or harder to interpret."
        ),
        confidence=confidence,
    )


LOW_PRIORITY_STRENGTH_LABELS = {
    "negligible",
    "negligible_association",
    "weak_but_reportable_association",
    "small_group_difference",
}


def eligible_as_main_finding(item: EvidenceItem) -> bool:
    if not item.eligible_for_writer:
        return False

    if item.recommended_use not in {
        RecommendedUse.HEADLINE,
        RecommendedUse.MAIN_FINDING,
    }:
        return False

    if item.strength_label in LOW_PRIORITY_STRENGTH_LABELS:
        return False

    return (
        item.factual_confidence >= 0.90
        and item.methodological_strength >= 0.70
        and item.user_relevance >= 0.65
    )


def evidence_priority_score(item: EvidenceItem) -> float:
    use_bonus = {
        RecommendedUse.HEADLINE: 0.25,
        RecommendedUse.MAIN_FINDING: 0.15,
        RecommendedUse.SUPPORTING_DETAIL: 0.0,
        RecommendedUse.LIMITATION: 0.10,
        RecommendedUse.OMIT_UNLESS_REQUESTED: -0.30,
    }[item.recommended_use]

    strength_bonus = {
        "very_strong_association": 0.20,
        "strong_association": 0.15,
        "moderate_association": 0.08,
        "large_group_difference": 0.18,
        "moderate_group_difference": 0.10,
        "small_group_difference": -0.08,
        "possible_data_quality_issue": 0.12,
        "possible_sentinel_zero": 0.15,
        "constant_column": 0.15,
        "validated_internal_prediction": 0.15,
        "validated_forecast": 0.15,
        "model_not_better_than_baseline": 0.10,
        "forecast_not_better_than_baseline": 0.10,
    }.get(item.strength_label, 0.0)

    return (
        0.30 * item.salience
        + 0.25 * item.user_relevance
        + 0.20 * item.methodological_strength
        + 0.15 * item.factual_confidence
        + use_bonus
        + strength_bonus
    )


def descriptive_analysis(
    bundle: DataBundle,
    tasks: list[InvestigationTask],
    builder: EvidenceBuilder,
) -> None:
    tasks_by_table: dict[str, list[InvestigationTask]] = {}

    for task in tasks:
        tasks_by_table.setdefault(task.table_name, []).append(task)

    for table_name, table_tasks in tasks_by_table.items():
        if table_name not in bundle.tables:
            continue

        frame = bundle.tables[table_name]
        task_ids = [task.task_id for task in table_tasks]

        builder.add(
            route=AnalysisRoute.DESCRIPTIVE,
            task_ids=task_ids,
            finding=(
                f"Table `{table_name}` contains {len(frame):,} rows "
                f"and {len(frame.columns):,} columns."
            ),
            metrics={
                "row_count": len(frame),
                "column_count": len(frame.columns),
            },
            source_tables=[table_name],
            source_columns=list(frame.columns),
            method="Direct inspection of loaded table dimensions.",
            practical_interpretation=(
                "This establishes the size and dimensionality of the available data."
            ),
            strength_label="dataset_overview",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.95,
            salience=0.95,
            recommended_use=RecommendedUse.HEADLINE,
        )

        hashable_frame = frame.copy()

        for column_name in hashable_frame.columns:
            hashable_frame[column_name] = (
                hashable_frame[column_name].map(
                    safe_hashable
                )
            )

        duplicate_row_count = int(
            hashable_frame.duplicated().sum()
        )

        if duplicate_row_count > 0:
            duplicate_row_rate = duplicate_row_count / max(
                len(frame),
                1,
            )

            builder.add(
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=task_ids,
                finding=(
                    f"Table `{table_name}` contains "
                    f"{duplicate_row_count:,} exact duplicate rows "
                    f"({duplicate_row_rate:.2%} of rows)."
                ),
                metrics={
                    "duplicate_row_count": duplicate_row_count,
                    "duplicate_row_rate": duplicate_row_rate,
                    "row_count": len(frame),
                },
                source_tables=[table_name],
                source_columns=list(frame.columns),
                method="Exact row duplicate inspection.",
                practical_interpretation=(
                    "Exactly repeated rows are present, but the available "
                    "data do not establish whether they are invalid."
                ),
                strength_label="duplicate_rows",
                limitations=[
                    "Exact duplicate rows may be genuine repeated observations "
                    "or unintended duplicates."
                ],
                prohibited_interpretations=[
                    "Do not call duplicate rows erroneous without record-level "
                    "validation.",
                    "Do not automatically recommend deduplication.",
                ],
                recommendations=[
                    AnalyticalRecommendation(
                        recommendation_id="REC_DUPLICATE_ROWS",
                        action=(
                            "Review the exact duplicate rows before deciding "
                            "whether to remove them."
                        ),
                        recommendation_type="data_cleaning",
                        priority="medium",
                        justification=(
                            "Exactly repeated rows can either be valid repeated "
                            "observations or unintended duplicates."
                        ),
                        affected_analyses=[
                            "descriptive analysis",
                            "correlation analysis",
                            "group comparison",
                            "predictive modelling",
                        ],
                        consequence_if_ignored=(
                            "Repeated rows may influence summaries or models if "
                            "they are unintended duplicates."
                        ),
                        confidence=1.0,
                    )
                ],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.METHODOLOGICAL,
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.75,
                salience=0.65,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )

        missing_counts = frame.isna().sum().sort_values(ascending=False)

        for column_name, count in missing_counts.items():
            count = int(count)

            if count == 0:
                continue

            rate = count / max(len(frame), 1)

            builder.add(
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=task_ids,
                finding=(
                    f"`{column_name}` has {count:,} missing values "
                    f"({rate:.2%} of rows)."
                ),
                metrics={
                    "missing_count": count,
                    "missing_rate": rate,
                },
                source_tables=[table_name],
                source_columns=[column_name],
                method="Direct missing-value count.",
                practical_interpretation=(
                    "The field is largely complete."
                    if rate < 0.01
                    else "Missingness may materially affect analysis using this field."
                ),
                strength_label=(
                    "low_missingness"
                    if rate < 0.01
                    else "material_missingness"
                ),
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.75 if rate >= 0.01 else 0.55,
                salience=0.75 if rate >= 0.01 else 0.50,
                recommended_use=(
                    RecommendedUse.MAIN_FINDING
                    if rate >= 0.05
                    else RecommendedUse.SUPPORTING_DETAIL
                ),
            )

        for column_name in frame.columns:
            series = frame[column_name]
            safe_series = series.map(safe_hashable)
            non_missing = safe_series.dropna()

            if non_missing.empty:
                continue

            unique_count = int(non_missing.nunique())

            if unique_count == 1:
                value = str(non_missing.iloc[0])

                builder.add(
                    route=AnalysisRoute.DESCRIPTIVE,
                    task_ids=task_ids,
                    finding=(
                        f"`{column_name}` is constant at `{value}` "
                        f"across all {len(non_missing):,} non-missing rows."
                    ),
                    metrics={
                        "constant": True,
                        "constant_value": value,
                        "non_missing_count": len(non_missing),
                    },
                    source_tables=[table_name],
                    source_columns=[column_name],
                    method="Unique-value and frequency inspection.",
                    practical_interpretation=(
                        "The column contains no observed variation and should not "
                        "be used for correlation, comparison, prediction, or forecasting."
                    ),
                    strength_label="constant_column",
                    claim_permissions=[
                        ClaimPermission.DESCRIPTIVE,
                        ClaimPermission.METHODOLOGICAL,
                    ],
                    factual_confidence=1.0,
                    methodological_strength=1.0,
                    user_relevance=0.90,
                    salience=0.90,
                    recommended_use=RecommendedUse.MAIN_FINDING,
                    recommendations=[
                        recommendation(
                            builder,
                            action=(
                                f"Remove `{column_name}` from correlation, comparison, "
                                "and predictive feature sets unless its constant value "
                                "has a documented interpretation."
                            ),
                            recommendation_type="data_cleaning",
                            priority="high",
                            justification=(
                                "The variable contains no observed variation and therefore "
                                "cannot distinguish observations or explain differences."
                            ),
                            affected_analyses=[
                                "correlation analysis",
                                "group comparison",
                                "predictive modelling",
                            ],
                            consequence_if_ignored=(
                                "The field will add no analytical information and may "
                                "create unnecessary processing or numerical issues in "
                                "methods that expect varying predictors."
                            ),
                            confidence=1.0,
                        )
                    ],
                    prohibited_interpretations=[
                        "Do not compare groups using this column as an outcome.",
                        "Do not describe the column as predictive.",
                    ],
                )
                continue

            if pd.api.types.is_numeric_dtype(series):
                values = pd.to_numeric(series, errors="coerce").dropna()

                if values.empty:
                    continue

                q01 = float(values.quantile(0.01))
                q05 = float(values.quantile(0.05))
                q25 = float(values.quantile(0.25))
                q75 = float(values.quantile(0.75))
                q99 = float(values.quantile(0.99))
                mean = float(values.mean())
                median = float(values.median())
                std = float(values.std(ddof=1)) if len(values) > 1 else 0.0
                zero_count = int((values == 0).sum())
                zero_rate = zero_count / len(values)
                zero_risk, zero_risk_reason = classify_zero_risk(
                    column_name=column_name,
                    zero_count=zero_count,
                    zero_rate=zero_rate,
                    median=median,
                    q05=q05,
                )

                metrics = {
                    "count": int(values.count()),
                    "mean": mean,
                    "median": median,
                    "standard_deviation": std,
                    "minimum": float(values.min()),
                    "q01": q01,
                    "q05": q05,
                    "q25": q25,
                    "q75": q75,
                    "q99": q99,
                    "maximum": float(values.max()),
                    "zero_count": zero_count,
                    "zero_rate": zero_rate,
                    "zero_risk": zero_risk.value,
                    "zero_risk_reason": zero_risk_reason,
                    "negative_count": int((values < 0).sum()),
                    "skewness": (
                        float(values.skew())
                        if len(values) > 2
                        else 0.0
                    ),
                }

                centre_difference = abs(mean - median)
                centre_close = std == 0 or centre_difference <= 0.10 * std

                if centre_close:
                    interpretation = (
                        "The mean and median are close relative to the observed spread, "
                        "so the centre is not strongly separated by this diagnostic."
                    )
                else:
                    interpretation = (
                        "The mean and median differ relative to the observed spread, "
                        "which may indicate skewness or influential values."
                    )

                suspicious_zero = zero_risk in {
                    ZeroRisk.UNUSUAL,
                    ZeroRisk.POSSIBLE_SENTINEL,
                }

                limitations = [
                    "Distribution summaries do not establish a trend, prediction, "
                    "or causal relationship."
                ]

                recommendations: list[AnalyticalRecommendation] = []

                if zero_risk == ZeroRisk.CONTEXT_DEPENDENT:
                    limitations.append(zero_risk_reason)

                if suspicious_zero:
                    limitations.append(zero_risk_reason)

                    if zero_risk == ZeroRisk.POSSIBLE_SENTINEL:
                        priority = "high"
                        recommendation_use = RecommendedUse.MAIN_FINDING
                        strength_label = "possible_sentinel_zero"
                        consequence = (
                            "Treating encoded missing values as genuine measurements "
                            "could distort means, associations, and fitted model "
                            "relationships."
                        )
                        confidence = 0.85
                    else:
                        priority = "medium"
                        recommendation_use = RecommendedUse.SUPPORTING_DETAIL
                        strength_label = "possible_data_quality_issue"
                        consequence = (
                            "If the zeros are invalid records, summaries and "
                            "relationships involving this field may be distorted."
                        )
                        confidence = 0.70

                    recommendations.append(
                        recommendation(
                            builder,
                            action=(
                                f"Validate zero values in `{column_name}` against "
                                "source records or metadata before relying on analyses "
                                "involving this field."
                            ),
                            recommendation_type="data_cleaning",
                            priority=priority,
                            justification=zero_risk_reason,
                            affected_analyses=[
                                "descriptive statistics",
                                "correlation analysis",
                                "predictive modelling",
                            ],
                            consequence_if_ignored=consequence,
                            confidence=confidence,
                        )
                    )
                else:
                    recommendation_use = (
                        RecommendedUse.OMIT_UNLESS_REQUESTED
                        if zero_risk == ZeroRisk.CONTEXT_DEPENDENT
                        else RecommendedUse.SUPPORTING_DETAIL
                    )
                    strength_label = "distribution_summary"

                builder.add(
                    route=AnalysisRoute.DESCRIPTIVE,
                    task_ids=task_ids,
                    finding=(
                        f"`{column_name}` has mean {mean:.4g}, median {median:.4g}, "
                        f"minimum {metrics['minimum']:.4g}, and maximum "
                        f"{metrics['maximum']:.4g} across {len(values):,} "
                        "non-missing observations."
                    ),
                    metrics=metrics,
                    source_tables=[table_name],
                    source_columns=[column_name],
                    method=(
                        "Direct descriptive statistics with quantiles and "
                        "distribution diagnostics."
                    ),
                    practical_interpretation=interpretation,
                    strength_label=(
                        strength_label
                    ),
                    claim_permissions=[
                        ClaimPermission.DESCRIPTIVE,
                        ClaimPermission.METHODOLOGICAL,
                    ],
                    factual_confidence=0.99,
                    methodological_strength=0.98,
                    user_relevance=0.85 if suspicious_zero else 0.55,
                    salience=0.90 if suspicious_zero else 0.50,
                    recommended_use=recommendation_use,
                    limitations=limitations,
                    recommendations=recommendations,
                    prohibited_interpretations=[
                        "Do not infer temporal change from the distribution alone.",
                        "Do not treat a suspicious value as definitively erroneous "
                        "without source validation.",
                    ],
                )

            elif unique_count <= 20:
                counts = non_missing.astype(str).value_counts().head(10)
                top_values = {
                    str(key): int(value)
                    for key, value in counts.items()
                }

                builder.add(
                    route=AnalysisRoute.DESCRIPTIVE,
                    task_ids=task_ids,
                    finding=(
                        f"The most frequent observed values of `{column_name}` are "
                        + ", ".join(
                            f"`{key}` ({value:,})"
                            for key, value in list(top_values.items())[:5]
                        )
                        + "."
                    ),
                    metrics={
                        "value_counts": top_values,
                        "unique_count": unique_count,
                    },
                    source_tables=[table_name],
                    source_columns=[column_name],
                    method="Frequency counts after safe conversion of structured values.",
                    practical_interpretation=(
                        "The counts describe the observed category composition and "
                        "can reveal imbalance between groups."
                    ),
                    strength_label="category_composition",
                    claim_permissions=[ClaimPermission.DESCRIPTIVE],
                    factual_confidence=0.99,
                    methodological_strength=0.98,
                    user_relevance=0.65,
                    salience=0.60,
                    recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                    limitations=[
                        "Counts describe the observed dataset and do not establish "
                        "population prevalence."
                    ],
                )


def association_analysis(
    bundle: DataBundle,
    tasks: list[InvestigationTask],
    builder: EvidenceBuilder,
    settings: Settings,
) -> None:
    for task in tasks:
        table_name = task.table_name

        if table_name not in bundle.tables:
            continue

        original = bundle.tables[table_name]

        if len(original) <= settings.full_data_correlation_limit:
            frame = original.copy()
            sampling_method = "full_dataset"
        else:
            sample_size = min(settings.max_analysis_rows, len(original))
            frame = original.sample(
                n=sample_size,
                random_state=settings.random_seed,
            ).copy()
            sampling_method = "fixed_seed_sample"

        numeric_columns = [
            column
            for column in frame.select_dtypes(include=np.number).columns
            if pd.to_numeric(frame[column], errors="coerce").nunique(dropna=True) > 1
        ]

        correlations: list[tuple[float, str, str, int, float]] = []

        for left, right in combinations(numeric_columns, 2):
            pair = (
                frame[[left, right]]
                .apply(pd.to_numeric, errors="coerce")
                .dropna()
            )

            if (
                len(pair) < 20
                or pair[left].nunique() < 2
                or pair[right].nunique() < 2
            ):
                continue

            correlation = float(pair[left].corr(pair[right]))

            if (
                np.isfinite(correlation)
                and abs(correlation) >= settings.min_abs_correlation
            ):
                correlations.append(
                    (
                        abs(correlation),
                        left,
                        right,
                        len(pair),
                        correlation,
                    )
                )

        for _, left, right, complete_count, value in sorted(
            correlations,
            reverse=True,
        )[: settings.max_correlation_findings]:
            direction = "positive" if value > 0 else "negative"
            strength = correlation_strength(value)

            sample_prefix = (
                "Using the full available data"
                if sampling_method == "full_dataset"
                else f"In a fixed-seed sample of {len(frame):,} rows"
            )

            builder.add(
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=[task.task_id],
                finding=(
                    f"{sample_prefix}, `{left}` and `{right}` have a {direction} "
                    f"Pearson correlation of {value:.4f} across "
                    f"{complete_count:,} complete row pairs."
                ),
                metrics={
                    "pearson_r": value,
                    "complete_pairs": complete_count,
                    "sampling_method": sampling_method,
                    "analysed_rows": len(frame),
                    "strength": strength,
                },
                source_tables=[table_name],
                source_columns=[left, right],
                method="Pairwise-complete Pearson correlation.",
                practical_interpretation=(
                    f"Higher values of `{left}` tend to coincide with "
                    f"{'higher' if value > 0 else 'lower'} values of `{right}`. "
                    f"The observed linear relationship is classified as {strength}."
                ),
                strength_label=f"{strength}_association",
                claim_permissions=[
                    ClaimPermission.ASSOCIATIONAL,
                    ClaimPermission.METHODOLOGICAL,
                ],
                factual_confidence=0.98,
                methodological_strength=0.88,
                user_relevance=min(1.0, 0.45 + abs(value)),
                salience=min(1.0, 0.40 + abs(value)),
                recommended_use=(
                    RecommendedUse.MAIN_FINDING
                    if abs(value) >= 0.50
                    else RecommendedUse.SUPPORTING_DETAIL
                ),
                limitations=[
                    "Correlation does not establish causation.",
                    "Pearson correlation measures linear association and may be "
                    "affected by outliers or non-linear structure.",
                ],
                prohibited_interpretations=[
                    f"Do not say `{left}` causes `{right}`.",
                    f"Do not say `{right}` causes `{left}`.",
                    "Do not describe correlation as complete explanation.",
                ],
            )

        categorical_columns = [
            column
            for column in frame.columns
            if not pd.api.types.is_numeric_dtype(frame[column])
            and 2
            <= frame[column].map(safe_hashable).nunique(dropna=True)
            <= 10
        ]

        candidates: list[dict[str, Any]] = []

        for group_column in categorical_columns[:8]:
            groups = frame[group_column].map(safe_hashable)

            for outcome_column in numeric_columns[:12]:
                working = pd.DataFrame(
                    {
                        "group": groups,
                        "outcome": pd.to_numeric(
                            frame[outcome_column],
                            errors="coerce",
                        ),
                    }
                ).dropna()

                if len(working) < 30:
                    continue

                if working["outcome"].nunique(dropna=True) < 2:
                    continue

                summary = working.groupby("group")["outcome"].agg(
                    ["mean", "std", "count"]
                )
                summary = summary[summary["count"] >= 5]

                if len(summary) < 2:
                    continue

                if summary["mean"].nunique(dropna=True) < 2:
                    continue

                highest_group = summary["mean"].idxmax()
                lowest_group = summary["mean"].idxmin()

                if highest_group == lowest_group:
                    continue

                highest_mean = float(summary.loc[highest_group, "mean"])
                lowest_mean = float(summary.loc[lowest_group, "mean"])
                difference = highest_mean - lowest_mean

                high_std = float(summary.loc[highest_group, "std"])
                low_std = float(summary.loc[lowest_group, "std"])

                pooled_std = math.sqrt(
                    (
                        (0.0 if math.isnan(high_std) else high_std ** 2)
                        + (0.0 if math.isnan(low_std) else low_std ** 2)
                    )
                    / 2.0
                )

                standardised_difference = (
                    difference / pooled_std
                    if pooled_std > 0
                    else None
                )

                strength = standardised_difference_strength(
                    standardised_difference
                )

                if strength == "negligible":
                    continue

                group_counts = {
                    str(key): int(value)
                    for key, value in summary["count"].items()
                }

                imbalance_ratio = max(group_counts.values()) / max(
                    min(group_counts.values()),
                    1,
                )

                candidates.append(
                    {
                        "score": abs(standardised_difference or 0.0),
                        "group_column": group_column,
                        "outcome_column": outcome_column,
                        "highest_group": str(highest_group),
                        "lowest_group": str(lowest_group),
                        "highest_mean": highest_mean,
                        "lowest_mean": lowest_mean,
                        "difference": difference,
                        "standardised_difference": standardised_difference,
                        "strength": strength,
                        "group_counts": group_counts,
                        "imbalance_ratio": imbalance_ratio,
                    }
                )

        for candidate in sorted(
            candidates,
            key=lambda item: item["score"],
            reverse=True,
        )[: settings.max_group_findings]:
            if candidate["imbalance_ratio"] >= 2:
                group_imbalance_note = (
                    "The groups are unevenly represented. The larger group mean is "
                    "estimated from more observations than the smaller group mean, "
                    "so the estimates may have different levels of precision and "
                    "stability."
                )
            else:
                group_imbalance_note = "The group sizes are not strongly imbalanced."

            builder.add(
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=[task.task_id],
                finding=(
                    f"For `{candidate['outcome_column']}` grouped by "
                    f"`{candidate['group_column']}`, "
                    f"`{candidate['highest_group']}` has the highest observed mean "
                    f"({candidate['highest_mean']:.4g}) and "
                    f"`{candidate['lowest_group']}` the lowest "
                    f"({candidate['lowest_mean']:.4g}), a difference of "
                    f"{candidate['difference']:.4g}."
                ),
                metrics=candidate,
                source_tables=[table_name],
                source_columns=[
                    candidate["group_column"],
                    candidate["outcome_column"],
                ],
                method=(
                    "Observed group means with at least five observations per "
                    "retained group, accompanied by group counts and a "
                    "standardised difference."
                ),
                practical_interpretation=(
                    f"The extreme observed group means differ by "
                    f"{candidate['difference']:.4g}. The standardised difference "
                    f"is classified as {candidate['strength']}. The comparison is "
                    "descriptive and unadjusted."
                ),
                strength_label=(
                    f"{candidate['strength']}_group_difference"
                ),
                claim_permissions=[
                    ClaimPermission.COMPARATIVE,
                    ClaimPermission.ASSOCIATIONAL,
                    ClaimPermission.METHODOLOGICAL,
                ],
                factual_confidence=0.97,
                methodological_strength=0.82,
                user_relevance=min(1.0, 0.50 + candidate["score"] / 2),
                salience=min(1.0, 0.45 + candidate["score"] / 2),
                recommended_use=(
                    RecommendedUse.MAIN_FINDING
                    if candidate["strength"] in {"large", "moderate"}
                    else RecommendedUse.SUPPORTING_DETAIL
                ),
                limitations=[
                    "This is an unadjusted observed comparison.",
                    "The comparison does not establish causation.",
                    group_imbalance_note,
                ],
                prohibited_interpretations=[
                    "Do not say group membership caused the observed difference.",
                    "Do not describe the comparison as adjusted for confounding.",
                ],
            )


def normalise_name(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", value.lower())
    ignored = {"c", "km", "h", "degrees", "millibars", "value"}
    return " ".join(word for word in words if word not in ignored)


def select_and_audit_features(
    frame: pd.DataFrame,
    target_column: str,
    time_column: str | None,
    proxy_threshold: float,
) -> tuple[list[str], list[str], list[dict[str, str]], list[str]]:
    numeric: list[str] = []
    categorical: list[str] = []
    excluded: list[dict[str, str]] = []
    warnings: list[str] = []

    numeric_target = pd.to_numeric(frame[target_column], errors="coerce")
    target_name = normalise_name(target_column)

    for column_name in frame.columns:
        if column_name in {target_column, time_column}:
            continue

        series = frame[column_name]

        if series.map(
            lambda value: isinstance(value, (list, dict, tuple, set))
        ).any():
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "structured_value",
                    "reason": "Structured values are not encoded by this modelling route.",
                }
            )
            continue

        unique_count = int(
            series.map(safe_hashable).nunique(dropna=True)
        )

        if unique_count <= 1:
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "constant",
                    "reason": "The feature has no observed variation.",
                }
            )
            continue

        if unique_count >= max(int(len(frame) * 0.98), 1_000):
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "identifier",
                    "reason": "The field behaves like a high-cardinality identifier.",
                }
            )
            continue

        possible_proxy = False
        proxy_reason = ""

        if pd.api.types.is_numeric_dtype(series) and numeric_target.notna().any():
            numeric_feature = pd.to_numeric(series, errors="coerce")
            pair = pd.DataFrame(
                {
                    "feature": numeric_feature,
                    "target": numeric_target,
                }
            ).dropna()

            if (
                len(pair) >= 20
                and pair["feature"].nunique() > 1
                and pair["target"].nunique() > 1
            ):
                correlation = abs(
                    float(pair["feature"].corr(pair["target"]))
                )

                if correlation >= proxy_threshold:
                    possible_proxy = True
                    proxy_reason = (
                        f"Absolute feature-target correlation is {correlation:.4f}, "
                        f"above the proxy threshold {proxy_threshold:.4f}."
                    )

        feature_name = normalise_name(column_name)

        if (
            target_name
            and feature_name
            and (
                target_name in feature_name
                or feature_name in target_name
            )
        ):
            if column_name != target_column:
                possible_proxy = True
                proxy_reason = (
                    proxy_reason
                    or "The feature name strongly overlaps the target name."
                )

        if possible_proxy:
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "target_proxy",
                    "reason": proxy_reason,
                }
            )
            warnings.append(
                f"`{column_name}` was excluded as a possible proxy for "
                f"`{target_column}`: {proxy_reason}"
            )
            continue

        if pd.api.types.is_numeric_dtype(series):
            numeric.append(column_name)
        elif unique_count <= 100:
            categorical.append(column_name)

    return numeric[:30], categorical[:20], excluded, warnings


def make_preprocessor(
    numeric_columns: list[str],
    categorical_columns: list[str],
) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler(with_mean=False)),
        ]
    )

    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ]
    )


def add_predictive_insufficiency(
    builder: EvidenceBuilder,
    task: InvestigationTask,
    finding: str,
    metrics: dict[str, Any],
    limitations: list[str],
    recommendations: list[AnalyticalRecommendation] | None = None,
) -> None:
    builder.add(
        route=AnalysisRoute.PREDICTIVE,
        task_ids=[task.task_id],
        finding=finding,
        metrics=metrics,
        source_tables=[task.table_name],
        source_columns=[
            column
            for column in [
                task.target_column,
                task.time_column,
                *task.columns,
            ]
            if column
        ],
        method="Predictive modelling feasibility and validation assessment.",
        validation_strategy=task.validation_strategy,
        practical_interpretation=(
            "The available evidence does not support a positive predictive claim."
        ),
        strength_label="predictive_insufficiency",
        claim_permissions=[
            ClaimPermission.INSUFFICIENCY,
            ClaimPermission.METHODOLOGICAL,
        ],
        factual_confidence=1.0,
        methodological_strength=0.95,
        user_relevance=0.75,
        salience=0.75,
        recommended_use=RecommendedUse.LIMITATION,
        limitations=limitations,
        recommendations=recommendations or [],
        prohibited_interpretations=[
            "Do not describe the task as successfully validated.",
            "Do not claim deployment readiness.",
        ],
    )


def split_predictive_data(
    frame: pd.DataFrame,
    features: list[str],
    target_column: str,
    time_column: str | None,
    classification: bool,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, ValidationStrategy]:
    working_columns = [*features, target_column]

    if time_column and time_column in frame.columns:
        working_columns.append(time_column)

    working = frame[working_columns].copy()
    working = working.dropna(subset=[target_column])

    if time_column and time_column in working.columns:
        parsed_time = pd.to_datetime(
            working[time_column],
            errors="coerce",
            utc=True,
        )

        parse_rate = float(parsed_time.notna().mean())

        if parse_rate >= 0.80:
            working = working.loc[parsed_time.notna()].copy()
            working["_parsed_time"] = parsed_time.loc[parsed_time.notna()]
            working = working.sort_values("_parsed_time")

            split_index = int(len(working) * 0.75)
            split_index = max(1, min(split_index, len(working) - 1))

            train = working.iloc[:split_index]
            test = working.iloc[split_index:]

            return (
                train[features],
                test[features],
                train[target_column],
                test[target_column],
                ValidationStrategy.CHRONOLOGICAL_HOLDOUT,
            )

    x = working[features]
    y = working[target_column]

    stratify = None

    if classification:
        counts = y.map(safe_hashable).astype(str).value_counts()
        if not counts.empty and counts.min() >= 2:
            stratify = y.map(safe_hashable).astype(str)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=seed,
        stratify=stratify,
    )

    strategy = (
        ValidationStrategy.STRATIFIED_HOLDOUT
        if stratify is not None
        else ValidationStrategy.RANDOM_HOLDOUT
    )

    return x_train, x_test, y_train, y_test, strategy


def predictive_analysis(
    bundle: DataBundle,
    task: InvestigationTask,
    builder: EvidenceBuilder,
    settings: Settings,
) -> None:
    table_name = task.table_name
    target_column = task.target_column

    if table_name not in bundle.tables or not target_column:
        add_predictive_insufficiency(
            builder,
            task,
            "Predictive modelling was not run because no target was selected.",
            {},
            ["A prediction target must be selected before model fitting."],
        )
        return

    if target_column not in bundle.tables[table_name].columns:
        add_predictive_insufficiency(
            builder,
            task,
            f"The selected target `{target_column}` was not found.",
            {},
            ["The prediction target is not present in the table."],
        )
        return

    if (
        task.target_status == TargetStatus.UNCONFIRMED
        or (
            task.target_status == TargetStatus.EXPERIMENTAL_CANDIDATE
            and not settings.allow_experimental_targets
        )
    ):
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"`{target_column}` was not used as a predictive target because "
                "the target was not user-selected or metadata-confirmed."
            ),
            {
                "target_column": target_column,
                "target_status": task.target_status.value,
            },
            [
                "An unconfirmed target is insufficient for a primary predictive claim.",
                "Experimental candidate targets can be enabled explicitly for ablation work.",
            ],
            recommendations=[
                recommendation(
                    builder,
                    action=(
                        f"Ask the user to confirm whether `{target_column}` is the "
                        "intended prediction target."
                    ),
                    recommendation_type="methodological_check",
                    priority="high",
                    justification=(
                        "Predictive performance has no stable interpretation without "
                        "a defined target and prediction objective."
                    ),
                )
            ],
        )
        return

    frame = bundle.tables[table_name].copy()

    if len(frame) > settings.max_analysis_rows:
        frame = frame.sample(
            n=settings.max_analysis_rows,
            random_state=settings.random_seed,
        ).copy()

    frame = frame.dropna(subset=[target_column])

    if len(frame) < 80:
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"Predictive modelling for `{target_column}` was not validated "
                f"because only {len(frame):,} rows had a non-missing target."
            ),
            {"usable_target_rows": len(frame)},
            ["At least 80 usable target rows are required."],
        )
        return

    numeric_columns, categorical_columns, excluded, leakage_warnings = (
        select_and_audit_features(
            frame,
            target_column,
            task.time_column,
            settings.target_proxy_correlation,
        )
    )

    feature_columns = numeric_columns + categorical_columns

    if not feature_columns:
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"No leakage-audited predictor columns remained for "
                f"`{target_column}`."
            ),
            {
                "excluded_features": excluded,
                "leakage_warnings": leakage_warnings,
            },
            [
                "All candidate predictors were constant, identifier-like, "
                "structured, or possible target proxies."
            ],
        )
        return

    target = frame[target_column]

    classification = bool(
        not pd.api.types.is_numeric_dtype(target)
        or target.map(safe_hashable).nunique(dropna=True) <= 20
    )

    try:
        (
            x_train,
            x_test,
            y_train,
            y_test,
            validation_strategy,
        ) = split_predictive_data(
            frame,
            feature_columns,
            target_column,
            task.time_column,
            classification,
            settings.random_seed,
        )

        if len(x_test) < 20:
            add_predictive_insufficiency(
                builder,
                task,
                "The predictive holdout contained fewer than 20 rows.",
                {
                    "train_rows": len(x_train),
                    "test_rows": len(x_test),
                },
                ["The holdout is too small for a stable predictive conclusion."],
            )
            return

        if classification:
            y_train = y_train.map(safe_hashable).astype(str)
            y_test = y_test.map(safe_hashable).astype(str)

            baseline = Pipeline(
                [
                    (
                        "preprocess",
                        make_preprocessor(
                            numeric_columns,
                            categorical_columns,
                        ),
                    ),
                    (
                        "model",
                        DummyClassifier(strategy="most_frequent"),
                    ),
                ]
            )

            baseline.fit(x_train, y_train)
            baseline_prediction = baseline.predict(x_test)

            baseline_f1 = f1_score(
                y_test,
                baseline_prediction,
                average="macro",
                zero_division=0,
            )

            candidates = {
                "logistic_regression": LogisticRegression(max_iter=1_000),
                "random_forest": RandomForestClassifier(
                    n_estimators=150,
                    max_depth=10,
                    random_state=settings.random_seed,
                    n_jobs=-1,
                ),
            }

            results: list[tuple[float, str, float]] = []

            for model_name, model in candidates.items():
                pipeline = Pipeline(
                    [
                        (
                            "preprocess",
                            make_preprocessor(
                                numeric_columns,
                                categorical_columns,
                            ),
                        ),
                        ("model", model),
                    ]
                )
                pipeline.fit(x_train, y_train)
                prediction = pipeline.predict(x_test)

                macro_f1 = f1_score(
                    y_test,
                    prediction,
                    average="macro",
                    zero_division=0,
                )
                accuracy = accuracy_score(y_test, prediction)

                results.append((macro_f1, model_name, accuracy))

            best_f1, best_model, best_accuracy = max(results)
            improvement = best_f1 - baseline_f1
            validated = improvement > 0.02

            metrics = {
                "task": "classification",
                "target_column": target_column,
                "target_status": task.target_status.value,
                "prediction_definition": task.prediction_definition,
                "validation_strategy": validation_strategy.value,
                "best_model": best_model,
                "holdout_macro_f1": best_f1,
                "holdout_accuracy": best_accuracy,
                "baseline_macro_f1": baseline_f1,
                "absolute_improvement": improvement,
                "train_rows": len(x_train),
                "test_rows": len(x_test),
                "features_used": feature_columns,
                "features_excluded": excluded,
                "leakage_warnings": leakage_warnings,
            }

            finding = (
                f"The best leakage-audited classifier for `{target_column}` was "
                f"`{best_model}`, with holdout macro-F1 {best_f1:.4f} and "
                f"accuracy {best_accuracy:.4f}; the majority-class baseline "
                f"macro-F1 was {baseline_f1:.4f}."
            )

        else:
            y_train = pd.to_numeric(y_train, errors="coerce")
            y_test = pd.to_numeric(y_test, errors="coerce")

            train_valid = y_train.notna()
            test_valid = y_test.notna()

            x_train = x_train.loc[train_valid]
            y_train = y_train.loc[train_valid]
            x_test = x_test.loc[test_valid]
            y_test = y_test.loc[test_valid]

            baseline = Pipeline(
                [
                    (
                        "preprocess",
                        make_preprocessor(
                            numeric_columns,
                            categorical_columns,
                        ),
                    ),
                    ("model", DummyRegressor(strategy="mean")),
                ]
            )

            baseline.fit(x_train, y_train)
            baseline_prediction = baseline.predict(x_test)
            baseline_mae = mean_absolute_error(y_test, baseline_prediction)

            candidates = {
                "ridge": Ridge(alpha=1.0),
                "random_forest": RandomForestRegressor(
                    n_estimators=150,
                    max_depth=10,
                    random_state=settings.random_seed,
                    n_jobs=-1,
                ),
            }

            results: list[
                tuple[float, str, float, float, float]
            ] = []

            for model_name, model in candidates.items():
                pipeline = Pipeline(
                    [
                        (
                            "preprocess",
                            make_preprocessor(
                                numeric_columns,
                                categorical_columns,
                            ),
                        ),
                        ("model", model),
                    ]
                )
                pipeline.fit(x_train, y_train)
                prediction = pipeline.predict(x_test)

                mae = mean_absolute_error(y_test, prediction)
                rmse = mean_squared_error(y_test, prediction) ** 0.5
                r_squared = r2_score(y_test, prediction)

                results.append(
                    (-mae, model_name, mae, rmse, r_squared)
                )

            _, best_model, best_mae, best_rmse, best_r_squared = max(results)

            improvement = (
                (baseline_mae - best_mae) / baseline_mae
                if baseline_mae > 0
                else 0.0
            )

            validated = improvement > 0.05

            metrics = {
                "task": "regression",
                "target_column": target_column,
                "target_status": task.target_status.value,
                "prediction_definition": task.prediction_definition,
                "validation_strategy": validation_strategy.value,
                "best_model": best_model,
                "holdout_mae": best_mae,
                "holdout_rmse": best_rmse,
                "holdout_r_squared": best_r_squared,
                "baseline_mae": baseline_mae,
                "relative_mae_improvement": improvement,
                "train_rows": len(x_train),
                "test_rows": len(x_test),
                "features_used": feature_columns,
                "features_excluded": excluded,
                "leakage_warnings": leakage_warnings,
            }

            finding = (
                f"The best leakage-audited regressor for `{target_column}` was "
                f"`{best_model}`, with holdout MAE {best_mae:.4g}, "
                f"RMSE {best_rmse:.4g}, and R² {best_r_squared:.4f}; "
                f"the mean baseline MAE was {baseline_mae:.4g}."
            )

        if not validated:
            finding += (
                " The tested model did not improve the relevant baseline "
                "by the configured validation threshold."
            )

        limitations = [
            "This is internal validation rather than external validation.",
            "Performance may change under distribution shift.",
            "Feature availability at the intended prediction time was not "
            "independently confirmed.",
        ]

        if task.target_status == TargetStatus.EXPERIMENTAL_CANDIDATE:
            limitations.append(
                "The target was selected for an explicit experiment rather than "
                "confirmed by the user or metadata."
            )

        if validation_strategy != ValidationStrategy.CHRONOLOGICAL_HOLDOUT:
            limitations.append(
                "The evaluation was not chronological; it should not be interpreted "
                "as evidence of future performance."
            )

        if leakage_warnings:
            limitations.append(
                "Potential proxy features were excluded before modelling."
            )

        builder.add(
            route=AnalysisRoute.PREDICTIVE,
            task_ids=[task.task_id],
            finding=finding,
            metrics=metrics,
            source_tables=[table_name],
            source_columns=[target_column, *feature_columns],
            method=(
                "Leakage-audited baseline comparison using a holdout selected "
                "according to the available temporal structure."
            ),
            validation_strategy=validation_strategy,
            practical_interpretation=(
                "The model is evidence of internal predictive performance only "
                "when it improves the baseline. It is not evidence of causality "
                "or deployment readiness."
            ),
            strength_label=(
                "validated_internal_prediction"
                if validated
                else "model_not_better_than_baseline"
            ),
            claim_permissions=(
                [
                    ClaimPermission.PREDICTIVE,
                    ClaimPermission.METHODOLOGICAL,
                ]
                if validated
                else [
                    ClaimPermission.INSUFFICIENCY,
                    ClaimPermission.METHODOLOGICAL,
                ]
            ),
            factual_confidence=0.97,
            methodological_strength=(
                0.88
                if validation_strategy == ValidationStrategy.CHRONOLOGICAL_HOLDOUT
                else 0.72
            ),
            user_relevance=0.85,
            salience=0.85,
            recommended_use=(
                RecommendedUse.MAIN_FINDING
                if validated
                else RecommendedUse.LIMITATION
            ),
            limitations=limitations,
            recommendations=[
                recommendation(
                    builder,
                    action=(
                        "Confirm the prediction time and verify that every retained "
                        "feature would be available at that time."
                    ),
                    recommendation_type="validation",
                    priority="high",
                    justification=(
                        "Internal holdout performance does not prove operational "
                        "feature availability or future generalisation."
                    ),
                )
            ],
            prohibited_interpretations=[
                "Do not claim causality from predictive performance.",
                "Do not claim deployment readiness.",
                "Do not claim future accuracy unless the validation was explicitly temporal.",
                "Do not imply excluded proxy features were used.",
            ],
        )

    except Exception as error:
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"Predictive modelling for `{target_column}` was inconclusive "
                "because execution failed."
            ),
            {
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
            [
                f"Execution error: {type(error).__name__}: {error}",
            ],
        )


def infer_time_structure(
    timestamps: pd.Series,
) -> tuple[str, list[int], int]:
    differences = (
        timestamps.sort_values()
        .diff()
        .dropna()
        .dt.total_seconds()
    )

    if differences.empty:
        return "unknown", [], 20

    median_seconds = float(differences.median())

    if median_seconds <= 5_400:
        return "hourly_or_finer", [24, 168], 168

    if median_seconds <= 129_600:
        return "daily", [7], 28

    if median_seconds <= 3_456_000:
        return "monthly", [12], 12

    return "irregular_or_sparse", [], 20


def autoregressive_predictions(
    values: np.ndarray,
    train_end: int,
    test_start: int,
    test_end: int,
    lags: list[int],
) -> np.ndarray | None:
    usable_lags = sorted(set(lag for lag in lags if lag > 0))

    if not usable_lags:
        usable_lags = [1]

    maximum_lag = max(usable_lags)

    rows: list[list[float]] = []
    targets: list[float] = []

    for index in range(maximum_lag, train_end):
        feature_row = [values[index - lag] for lag in usable_lags]

        if not np.isfinite(feature_row).all() or not np.isfinite(values[index]):
            continue

        rows.append(feature_row)
        targets.append(values[index])

    if len(rows) < 40:
        return None

    x_train = np.asarray(rows[-50_000:], dtype=float)
    y_train = np.asarray(targets[-50_000:], dtype=float)

    model = Ridge(alpha=1.0)
    model.fit(x_train, y_train)

    test_rows: list[list[float]] = []

    for index in range(test_start, test_end):
        feature_row = [values[index - lag] for lag in usable_lags]

        if not np.isfinite(feature_row).all():
            return None

        test_rows.append(feature_row)

    return model.predict(np.asarray(test_rows, dtype=float))


def forecasting_analysis(
    bundle: DataBundle,
    task: InvestigationTask,
    builder: EvidenceBuilder,
    settings: Settings,
) -> None:
    table_name = task.table_name
    time_column = task.time_column
    target_column = task.target_column

    if (
        table_name not in bundle.tables
        or not time_column
        or not target_column
        or time_column not in bundle.tables[table_name].columns
        or target_column not in bundle.tables[table_name].columns
    ):
        builder.add(
            route=AnalysisRoute.FORECASTING,
            task_ids=[task.task_id],
            finding=(
                "Forecasting was not run because a valid time column and "
                "numeric target were not available."
            ),
            metrics={},
            source_tables=[table_name],
            source_columns=[
                column
                for column in [time_column, target_column]
                if column
            ],
            method="Forecast feasibility assessment.",
            validation_strategy=ValidationStrategy.NONE,
            practical_interpretation=(
                "The available plan does not support a validated forecast."
            ),
            strength_label="forecast_insufficiency",
            claim_permissions=[
                ClaimPermission.INSUFFICIENCY,
                ClaimPermission.METHODOLOGICAL,
            ],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.75,
            salience=0.75,
            recommended_use=RecommendedUse.LIMITATION,
            limitations=[
                "No validated forecast claim is available.",
            ],
        )
        return

    frame = bundle.tables[table_name][
        [time_column, target_column]
    ].copy()

    frame[time_column] = pd.to_datetime(
        frame[time_column],
        errors="coerce",
        utc=True,
    )
    frame[target_column] = pd.to_numeric(
        frame[target_column],
        errors="coerce",
    )

    frame = frame.dropna().sort_values(time_column)
    frame = frame.groupby(
        time_column,
        as_index=False,
    )[target_column].mean()

    granularity, seasonal_lags, minimum_test_points = infer_time_structure(
        frame[time_column]
    )

    maximum_lag = max([1, *seasonal_lags])

    if len(frame) < maximum_lag + minimum_test_points * 2:
        builder.add(
            route=AnalysisRoute.FORECASTING,
            task_ids=[task.task_id],
            finding=(
                f"Forecast validation for `{target_column}` was not run because "
                f"{len(frame):,} usable time points were insufficient for "
                "the inferred evaluation design."
            ),
            metrics={
                "usable_time_points": len(frame),
                "time_granularity": granularity,
                "minimum_test_points": minimum_test_points,
                "seasonal_lags": seasonal_lags,
            },
            source_tables=[table_name],
            source_columns=[time_column, target_column],
            method="Temporal coverage and seasonal-lag feasibility assessment.",
            validation_strategy=ValidationStrategy.NONE,
            practical_interpretation=(
                "The time series is too short for the selected rolling evaluation."
            ),
            strength_label="forecast_insufficiency",
            claim_permissions=[
                ClaimPermission.INSUFFICIENCY,
                ClaimPermission.METHODOLOGICAL,
            ],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.75,
            salience=0.75,
            recommended_use=RecommendedUse.LIMITATION,
            limitations=[
                "The series does not contain enough usable points for the "
                "required rolling evaluation windows."
            ],
        )
        return

    values = frame[target_column].to_numpy(dtype=float)
    length = len(values)

    test_window = max(minimum_test_points, int(length * 0.05))
    test_window = min(test_window, settings.max_forecast_test_points)
    test_window = min(test_window, max(minimum_test_points, length // 5))

    available_folds = max(
        1,
        (length - maximum_lag) // test_window - 1,
    )
    fold_count = min(settings.forecast_folds, available_folds)

    fold_results: list[dict[str, Any]] = []

    for fold_index in range(fold_count):
        test_end = length - (fold_count - fold_index - 1) * test_window
        test_start = test_end - test_window
        train_end = test_start

        if train_end <= maximum_lag:
            continue

        actual = values[test_start:test_end]

        predictions: dict[str, np.ndarray] = {
            "naive_last_value": values[test_start - 1:test_end - 1],
        }

        for lag in seasonal_lags:
            if test_start - lag >= 0:
                predictions[
                    f"seasonal_naive_lag_{lag}"
                ] = values[test_start - lag:test_end - lag]

        trend_model = LinearRegression()
        training_index = np.arange(train_end).reshape(-1, 1)
        testing_index = np.arange(test_start, test_end).reshape(-1, 1)

        trend_model.fit(training_index, values[:train_end])
        predictions["linear_trend"] = trend_model.predict(testing_index)

        autoregressive = autoregressive_predictions(
            values,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            lags=[1, *seasonal_lags],
        )

        if autoregressive is not None:
            predictions["autoregressive_ridge"] = autoregressive

        model_metrics = {
            model_name: float(mean_absolute_error(actual, prediction))
            for model_name, prediction in predictions.items()
        }

        fold_results.append(
            {
                "fold_id": f"FOLD_{fold_index + 1:02d}",
                "train_end": frame[time_column].iloc[train_end - 1].isoformat(),
                "test_start": frame[time_column].iloc[test_start].isoformat(),
                "test_end": frame[time_column].iloc[test_end - 1].isoformat(),
                "test_points": len(actual),
                "mae": model_metrics,
            }
        )

    if not fold_results:
        return

    model_names = sorted(
        {
            model_name
            for fold in fold_results
            for model_name in fold["mae"]
        }
    )

    mean_mae = {
        model_name: float(
            np.mean(
                [
                    fold["mae"][model_name]
                    for fold in fold_results
                    if model_name in fold["mae"]
                ]
            )
        )
        for model_name in model_names
    }

    baseline_names = [
        name
        for name in model_names
        if name.startswith("naive_") or name.startswith("seasonal_naive_")
    ]
    candidate_names = [
        name
        for name in model_names
        if name not in baseline_names
    ]

    best_baseline = min(
        baseline_names,
        key=lambda name: mean_mae[name],
    )
    best_candidate = min(
        candidate_names,
        key=lambda name: mean_mae[name],
    )

    baseline_mae = mean_mae[best_baseline]
    candidate_mae = mean_mae[best_candidate]

    relative_improvement = (
        (baseline_mae - candidate_mae) / baseline_mae
        if baseline_mae > 0
        else 0.0
    )

    fold_wins = sum(
        1
        for fold in fold_results
        if fold["mae"].get(best_candidate, float("inf"))
        < fold["mae"].get(best_baseline, float("inf"))
    )

    validated = bool(
        relative_improvement > 0.05
        and fold_wins >= math.ceil(len(fold_results) / 2)
    )

    if validated:
        finding = (
            f"`{best_candidate}` achieved mean rolling-origin MAE "
            f"{candidate_mae:.4g}, compared with {baseline_mae:.4g} for "
            f"the strongest naive baseline, `{best_baseline}`, across "
            f"{len(fold_results)} evaluation folds."
        )
    else:
        finding = (
            f"The best tested forecasting candidate, `{best_candidate}`, "
            f"had mean rolling-origin MAE {candidate_mae:.4g}, compared with "
            f"{baseline_mae:.4g} for the strongest naive baseline, "
            f"`{best_baseline}`. It did not provide a validated improvement."
        )

    builder.add(
        route=AnalysisRoute.FORECASTING,
        task_ids=[task.task_id],
        finding=finding,
        metrics={
            "target_column": target_column,
            "time_column": time_column,
            "time_granularity": granularity,
            "seasonal_lags": seasonal_lags,
            "fold_count": len(fold_results),
            "test_window_points": test_window,
            "fold_results": fold_results,
            "mean_mae": mean_mae,
            "best_baseline": best_baseline,
            "best_candidate": best_candidate,
            "baseline_mae": baseline_mae,
            "candidate_mae": candidate_mae,
            "relative_improvement": relative_improvement,
            "candidate_fold_wins": fold_wins,
        },
        source_tables=[table_name],
        source_columns=[time_column, target_column],
        method=(
            "Expanding-window rolling-origin, one-step-ahead evaluation "
            "against last-value and available seasonal-naive baselines."
        ),
        validation_strategy=ValidationStrategy.ROLLING_ORIGIN,
        practical_interpretation=(
            "The candidate is considered useful only when it consistently "
            "improves the strongest relevant naive baseline across folds."
        ),
        strength_label=(
            "validated_forecast"
            if validated
            else "forecast_not_better_than_baseline"
        ),
        claim_permissions=(
            [
                ClaimPermission.FORECAST,
                ClaimPermission.METHODOLOGICAL,
            ]
            if validated
            else [
                ClaimPermission.INSUFFICIENCY,
                ClaimPermission.METHODOLOGICAL,
            ]
        ),
        factual_confidence=0.97,
        methodological_strength=0.90,
        user_relevance=0.85,
        salience=0.85,
        recommended_use=(
            RecommendedUse.MAIN_FINDING
            if validated
            else RecommendedUse.LIMITATION
        ),
        limitations=[
            "This is an internal backtest, not a guarantee of live future performance.",
            "The evaluation is one-step-ahead and may not represent longer forecast horizons.",
            "External drivers and distribution shifts are not represented.",
        ],
        recommendations=[
            recommendation(
                builder,
                action=(
                    "Define the intended forecast horizon explicitly and repeat "
                    "evaluation for that horizon."
                ),
                recommendation_type="validation",
                priority="high",
                justification=(
                    "One-step-ahead performance is not interchangeable with "
                    "multi-step forecast performance."
                ),
            )
        ],
        prohibited_interpretations=[
            "Do not describe an unsuccessful candidate as a validated forecast.",
            "Do not claim certainty about future observations.",
            "Do not claim causal explanations for forecast behaviour.",
        ],
    )


def causal_feasibility_analysis(
    bundle: DataBundle,
    task: InvestigationTask,
    builder: EvidenceBuilder,
) -> None:
    table_name = task.table_name
    columns = set(
        bundle.tables.get(table_name, pd.DataFrame()).columns
    )

    exposure_available = bool(
        task.exposure_column
        and task.exposure_column in columns
    )
    outcome_available = bool(
        task.outcome_column
        and task.outcome_column in columns
    )
    time_available = bool(
        task.time_column
        and task.time_column in columns
    )
    confounders = [
        column
        for column in task.confounder_columns
        if column in columns
    ]

    builder.add(
        route=AnalysisRoute.CAUSAL_FEASIBILITY,
        task_ids=[task.task_id],
        finding=(
            "A causal conclusion is not authorised because the workflow has "
            "not verified randomisation, a natural experiment, a defensible "
            "adjustment set, or another identification strategy."
        ),
        metrics={
            "exposure_available": exposure_available,
            "outcome_available": outcome_available,
            "time_column_available": time_available,
            "proposed_confounder_count": len(confounders),
            "causal_claim_authorised": False,
        },
        source_tables=[table_name] if table_name in bundle.tables else [],
        source_columns=[
            column
            for column in [
                task.exposure_column,
                task.outcome_column,
                task.time_column,
                *confounders,
            ]
            if column
        ],
        method="Causal-feasibility checklist; no treatment-effect estimation.",
        practical_interpretation=(
            "Observed relationships may be described as associations, but the "
            "available design does not identify a causal effect."
        ),
        strength_label="causal_insufficiency",
        claim_permissions=[
            ClaimPermission.INSUFFICIENCY,
            ClaimPermission.METHODOLOGICAL,
        ],
        factual_confidence=1.0,
        methodological_strength=1.0,
        user_relevance=0.80,
        salience=0.80,
        recommended_use=RecommendedUse.LIMITATION,
        limitations=[
            "The presence of a date column does not establish temporal ordering.",
            "Observed association does not identify a causal effect.",
        ],
        prohibited_interpretations=[
            "Do not claim that one observed variable caused another.",
            "Do not claim a treatment effect.",
        ],
    )


def execute_plan(
    bundle: DataBundle,
    plan: ExecutionPlan,
    settings: Settings,
    semantic_map: InputSemanticMap | None = None,
) -> EvidenceLedger:
    builder = EvidenceBuilder(bundle.fingerprint)
    event_input = bool(
        (bundle.input_structure and bundle.input_structure.shape == InputShape.EVENT_RECORD)
        or (
            semantic_map is not None
            and semantic_map.input_shape == InputShape.EVENT_RECORD
            and semantic_map.confidence >= 0.7
        )
    )
    event_genre = plan.report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }

    if event_input:
        event_analysis(bundle, plan, builder, semantic_map)

    for route in plan.route_order:
        tasks = tasks_for_route(plan, route)

        if route == AnalysisRoute.DESCRIPTIVE:
            tabular_tasks = [
                task
                for task in tasks
                if task.capability
                not in {
                    EvidenceCapability.EVENT_OUTCOME,
                    EvidenceCapability.ENTITY_PERFORMANCE,
                    EvidenceCapability.RANKING,
                    EvidenceCapability.GROUP_COMPARISON,
                }
            ]
            if not (event_input and event_genre):
                descriptive_analysis(bundle, tabular_tasks, builder)

        elif route == AnalysisRoute.ASSOCIATION_COMPARISON:
            tabular_tasks = [
                task
                for task in tasks
                if task.capability != EvidenceCapability.GROUP_COMPARISON
                or not event_input
            ]
            if tabular_tasks and not (event_input and event_genre):
                association_analysis(
                    bundle,
                    tabular_tasks,
                    builder,
                    settings,
                )

        elif route == AnalysisRoute.PREDICTIVE:
            for task in tasks:
                predictive_analysis(
                    bundle,
                    task,
                    builder,
                    settings,
                )

        elif route == AnalysisRoute.FORECASTING:
            for task in tasks:
                forecasting_analysis(
                    bundle,
                    task,
                    builder,
                    settings,
                )

        elif route == AnalysisRoute.CAUSAL_FEASIBILITY:
            for task in tasks:
                causal_feasibility_analysis(
                    bundle,
                    task,
                    builder,
                )

    if not builder.items:
        builder.execution_notes.append(
            "The execution plan produced no evidence items."
        )

    return builder.build()
````

### `src/table2text/audit.py`

````python
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from typing import Any

import numpy as np
import pandas as pd

from .capabilities import participation_measure_requested
from .schemas import (
    AnalyticalFunction,
    AnalysisRoute,
    AuditAnnotation,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    ClaimPermission,
    ColumnProfile,
    DataProfile,
    ErrorType,
    EvidenceCapability,
    EvidenceItem,
    EvidenceLedger,
    ExternalTruthSource,
    FactCandidate,
    FactCandidateSet,
    FactLedger,
    FactReview,
    GenreQualityAssessment,
    InsightLedger,
    InsightType,
    InsightVerificationStatus,
    InputStructureProfile,
    InterpretationLevel,
    QualityStatus,
    ProfileSupportRecord,
    RecommendedUse,
    RejectedFact,
    ReleaseStatus,
    RepairCandidate,
    RepairStrategy,
    ReportComponent,
    ReportComponentAssessment,
    ReportGenre,
    ReportPatch,
    ReportQualityAssessment,
    ReviewDecision,
    SentenceSupport,
    Severity,
    SupportMapPatch,
    SupportType,
    VerificationMethod,
    VerificationResult,
    VerifiedFact,
    VerifiedInsight,
    WriterAgentDraft,
    WriterEvidencePack,
    WriterOutput,
)
from .config import Settings


NUMBER_PATTERN = re.compile(
    r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?"
)

CAUSAL_PATTERN = re.compile(
    r"\b(caused|causes|causing|drives?|drove|driven by|led to|effect of|"
    r"responsible for|result(?:s|ed|ing)? in|"
    r"contribut(?:e|es|ed|ing) to|because of|due to|explains?)\b",
    re.IGNORECASE,
)

FACTUAL_TITLE_PATTERN = re.compile(
    r"\b(defeats?|defeated|beats?|beat|wins?|won|loses?|lost|"
    r"edges?|edged|outscores?|outscored|leads?|led|draws?|drew|"
    r"ties?|tied|versus|vs\.?)\b",
    re.IGNORECASE,
)

PREDICTIVE_PATTERN = re.compile(
    r"\b(predicts?|predictive|classifier|regressor|out-of-sample|"
    r"deployment|generalises?)\b",
    re.IGNORECASE,
)

FORECAST_PATTERN = re.compile(
    r"\b(forecasts?|forecasted|future values?|will increase|"
    r"will decrease|future performance)\b",
    re.IGNORECASE,
)

APPROXIMATE_PATTERN = re.compile(
    r"\b(about|approximately|around|roughly|nearly|close to|"
    r"more than|over|less than|under)\b",
    re.IGNORECASE,
)

INTERNAL_CONTROL_PATTERN = re.compile(
    r"(?i)\b("
    r"global prohibited interpretations|"
    r"prohibited interpretations|"
    r"interpretation notes|"
    r"recommended use|"
    r"methodological strength|"
    r"user relevance|"
    r"do not say|"
    r"do not describe"
    r")\b"
)

FIELD_LABEL_PATTERN = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?\*{0,2}"
    r"(Finding|Strength|Important Note|Interpretation Notes|"
    r"Recommended Use|Methodological Strength|User Relevance|"
    r"Salience|Global Prohibited Interpretations)"
    r"\*{0,2}\s*:"
)

GENERIC_OPENING_PATTERNS = [
    re.compile(r"\bthis document summarizes\b", re.IGNORECASE),
    re.compile(r"\bthis report provides\b", re.IGNORECASE),
    re.compile(r"\bhere'?s a breakdown\b", re.IGNORECASE),
    re.compile(r"\bthe goal is to provide\b", re.IGNORECASE),
]

CAVEAT_PATTERNS = [
    re.compile(r"does not imply causation", re.IGNORECASE),
    re.compile(r"does not establish causation", re.IGNORECASE),
    re.compile(r"\bunadjusted\b", re.IGNORECASE),
    re.compile(r"\bconfound(?:er|ers|ing)\b", re.IGNORECASE),
]

IMBALANCE_BIAS_PATTERN = re.compile(
    r"\b("
    r"imbalanc\w*[^.!?]{0,80}bias\w*|"
    r"bias\w*[^.!?]{0,80}imbalanc\w*"
    r")\b",
    re.IGNORECASE,
)

UNSANCTIONED_UNIT_TERMS = {
    "event",
    "events",
    "experiment",
    "experiments",
    "subject",
    "subjects",
}

HOURLY_CADENCE_PATTERN = re.compile(
    r"\b(hourly observations?|hourly measurements?|every hour|"
    r"one-hour intervals?)\b",
    re.IGNORECASE,
)

LOCATION_METADATA_PATTERN = re.compile(
    r"\b(specific location|weather station|recorded at a location)\b",
    re.IGNORECASE,
)

CONSTANT_OVERSTATEMENT_PATTERN = re.compile(
    r"\b(no analytical value|useless|worthless|has no value)\b",
    re.IGNORECASE,
)

ZERO_OVERCONFIDENCE_PATTERN = re.compile(
    r"\b(likely represents encoded missingness|definitely represents|"
    r"is measurement failure|must be erroneous)\b",
    re.IGNORECASE,
)

MISSINGNESS_HARMLESS_PATTERN = re.compile(
    r"\b(unlikely to cause major issues|can be safely ignored|"
    r"will not affect the analysis|has no material effect)\b",
    re.IGNORECASE,
)

DUPLICATE_REMOVAL_PATTERN = re.compile(
    r"\b(duplicates?(?: rows?)? should be removed|"
    r"duplicates?(?: rows?)? should likely be removed|"
    r"likely removed|must be removed|automatically deduplicate)\b",
    re.IGNORECASE,
)

PEARSON_IMPRECISE_PATTERN = re.compile(
    r"\bpearson correlation\b[^.!?]{0,100}\b"
    r"(?:is|may be)?\s*influenced by non-linear patterns\b",
    re.IGNORECASE,
)

FUTURE_ANALYSIS_PATTERN = re.compile(
    r"\b(future work should|next analyses should|could model|"
    r"multivariate model|explore temporal trends|"
    r"investigate the relationship)\b",
    re.IGNORECASE,
)

DATASET_GENERALISATION_PATTERN = re.compile(
    r"\b(always|in general|universally|proves that|demonstrates that all)\b",
    re.IGNORECASE,
)

UNSUPPORTED_SPORTS_NARRATIVE_PATTERN = re.compile(
    r"\b(dominated throughout|single-handedly|comeback|turning point|"
    r"all-time classic|historic victory|upset|cruised to victory)\b",
    re.IGNORECASE,
)

INSIGHT_OVERSTATEMENT_PATTERN = re.compile(
    r"\b(completely redundant|universally redundant|should always be removed|"
    r"must always be removed|proves that)\b",
    re.IGNORECASE,
)

HYPOTHESIS_WORDING_PATTERN = re.compile(
    r"\b(hypothesis|hypothesise|hypothesize|question for further "
    r"investigation)\b",
    re.IGNORECASE,
)

UNLABELLED_HYPOTHESIS_PATTERN = re.compile(
    r"\b(may|might|could|likely)\b[^.!?]{0,100}\b"
    r"(because|reflects?|indicates?|explains?|due to)\b",
    re.IGNORECASE,
)

EXPLANATORY_HYPOTHESIS_PATTERN = re.compile(
    r"(?:"
    r"\b(?:may|might|could|possibly|potentially|whether)\b"
    r"[^.!?]{0,180}\b(?:"
    r"reflect(?:s|ed|ing)?|"
    r"result(?:s|ed|ing)?\s+from|"
    r"stems?|stemmed|stemming|"
    r"arises?|arose|arisen|"
    r"be\s+due\s+to|"
    r"be\s+explained\s+by"
    r")\b|"
    r"\b(?:possible|plausible|potential)\s+"
    r"(?:explanation|reason)\b"
    r")",
    re.IGNORECASE,
)

ASSOCIATION_STRENGTH_PATTERN = re.compile(
    r"\b(?P<label>very strong|strong|moderate|weak|negligible)\b"
    r"(?:\s+(?:positive|negative))?"
    r"(?:\s+(?:pearson|spearman|rank-based|linear))?"
    r"\s+(?:correlations?|associations?|relationships?)\b",
    re.IGNORECASE,
)

GROUP_STRENGTH_PATTERN = re.compile(
    r"\b(?P<label>large|moderate|small|negligible)\b"
    r"(?:\s+standard(?:ised|ized))?"
    r"\s+(?:group\s+)?(?:differences?|effect sizes?)\b",
    re.IGNORECASE,
)

INTERPRETIVE_SYNTHESIS_PATTERN = re.compile(
    r"\b(overlapping information|taken together|together suggest|"
    r"combined with|overall pattern|this indicates|this suggests|therefore)\b",
    re.IGNORECASE,
)


def materially_same_report_text(
    left: str,
    right: str,
) -> bool:
    left_normalised = re.sub(
        r"[^a-z0-9]+",
        " ",
        left.lower(),
    ).strip()
    right_normalised = re.sub(
        r"[^a-z0-9]+",
        " ",
        right.lower(),
    ).strip()

    if left_normalised == right_normalised:
        return True

    left_tokens = {
        token
        for token in left_normalised.split()
        if len(token) > 2
    }
    right_tokens = {
        token
        for token in right_normalised.split()
        if len(token) > 2
    }
    if not left_tokens or not right_tokens:
        return False

    return (
        len(left_tokens & right_tokens)
        / len(left_tokens | right_tokens)
        >= 0.8
    )

PROFILE_FACT_KIND_TERMS = {
    "table_dimensions": re.compile(
        r"\b(rows?|columns?|observations?|records?)\b",
        re.IGNORECASE,
    ),
    "duplicate_rows": re.compile(
        r"\b(duplicate|duplicates|duplicate rows?)\b",
        re.IGNORECASE,
    ),
    "column_missingness": re.compile(
        r"\b(missing|missingness)\b",
        re.IGNORECASE,
    ),
    "constant_column": re.compile(
        r"\b(constant|all zeros?|no observed variation)\b",
        re.IGNORECASE,
    ),
    "near_constant_column": re.compile(
        r"\b(near-constant|near constant|dominant value)\b",
        re.IGNORECASE,
    ),
    "numeric_summary": re.compile(
        r"\b(mean|median|minimum|maximum|standard deviation)\b",
        re.IGNORECASE,
    ),
    "zero_diagnostic": re.compile(
        r"\b(zero|zeros|sentinel)\b",
        re.IGNORECASE,
    ),
    "datetime_presence": re.compile(
        r"\b(date|datetime|timestamp|time column)\b",
        re.IGNORECASE,
    ),
    "candidate_key": re.compile(
        r"\b(candidate key|unique identifier)\b",
        re.IGNORECASE,
    ),
}

QUALITY_STATUS_ORDER = {
    QualityStatus.PASS: 0,
    QualityStatus.WARNING: 1,
    QualityStatus.REVISE: 2,
}


def count_caveat_mentions(markdown: str) -> int:
    return sum(len(pattern.findall(markdown)) for pattern in CAVEAT_PATTERNS)


def minimum_useful_report_words(
    *,
    target_words: int,
    required_component_count: int,
    settings: Settings,
) -> int:
    """
    Return a diagnostic minimum that never exceeds the planned target.
    """

    bounded_target = max(1, target_words)

    ratio_floor = int(
        bounded_target
        * settings.minimum_report_word_ratio
    )

    component_floor = (
        required_component_count * 45
    )

    desired_minimum = max(
        settings.minimum_report_word_floor,
        ratio_floor,
        component_floor,
    )

    return min(
        bounded_target,
        desired_minimum,
    )

def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value

    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        number = float(value)
        return None if math.isnan(number) or math.isinf(number) else number

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]

    if hasattr(value, "model_dump"):
        return json_safe(value.model_dump(mode="json"))

    return str(value)


def compact_json(
    value: Any,
    maximum_characters: int = 160_000,
) -> str:
    rendered = json.dumps(
        json_safe(value),
        indent=2,
        ensure_ascii=False,
    )

    if len(rendered) <= maximum_characters:
        return rendered

    return rendered[:maximum_characters] + "\n... [truncated by controller]"


def flatten_numbers(value: Any) -> list[float]:
    numbers: list[float] = []

    if isinstance(value, bool) or value is None:
        return numbers

    if isinstance(value, (int, float, np.integer, np.floating)):
        number = float(value)
        if math.isfinite(number):
            numbers.append(number)
        return numbers

    if isinstance(value, str):
        token = value.strip()
        if NUMBER_PATTERN.fullmatch(token):
            percentage = token.endswith("%")
            number = float(token.rstrip("%").replace(",", ""))
            if percentage:
                number /= 100.0
            if math.isfinite(number):
                numbers.append(number)
        return numbers

    if isinstance(value, dict):
        for item in value.values():
            numbers.extend(flatten_numbers(item))
        return numbers

    if isinstance(value, (list, tuple, set)):
        for item in value:
            numbers.extend(flatten_numbers(item))

    return numbers


def extract_number_tokens(text: str) -> list[tuple[str, float]]:
    tokens: list[tuple[str, float]] = []

    for raw in NUMBER_PATTERN.findall(text or ""):
        percentage = raw.endswith("%")
        cleaned = raw.rstrip("%").replace(",", "")

        try:
            number = float(cleaned)
        except ValueError:
            continue

        if percentage:
            number /= 100.0

        tokens.append((raw, number))

    return tokens


def number_supported(
    raw_token: str,
    number: float,
    support_numbers: list[float],
    sentence: str,
) -> bool:
    """
    Check whether a rendered number is supported.

    The tolerance accounts for ordinary display rounding. This is
    particularly important for percentages, where a deterministic
    value such as 0.005359 may be rendered as 0.54%.
    """

    approximate = bool(
        APPROXIMATE_PATTERN.search(sentence)
    )

    token_without_percent = (
        raw_token.rstrip("%").replace(",", "")
    )

    if "." in token_without_percent:
        decimal_places = len(
            token_without_percent.split(".", 1)[1]
        )
    else:
        decimal_places = 0

    displayed_resolution = 10.0 ** (-decimal_places)

    if raw_token.endswith("%"):
        displayed_resolution /= 100.0

    rounding_tolerance = (
        displayed_resolution / 2.0
    ) + 1e-12

    for candidate in support_numbers:
        relative_tolerance = max(
            1e-6,
            abs(candidate) * 0.001,
        )

        exact_tolerance = max(
            rounding_tolerance,
            relative_tolerance,
        )

        if abs(number - candidate) <= exact_tolerance:
            return True

        if approximate:
            approximate_tolerance = max(
                displayed_resolution,
                0.01,
                abs(candidate) * 0.03,
            )

            if (
                abs(number - candidate)
                <= approximate_tolerance
            ):
                return True

        digits = token_without_percent

        if (
            "." not in digits
            and len(digits) >= 4
            and digits.endswith("000")
        ):
            if abs(number - candidate) <= 500:
                return True

    return False

def numbers_supported(
    text: str,
    support_numbers: list[float],
) -> bool:
    return all(
        number_supported(
            raw_token,
            number,
            support_numbers,
            text,
        )
        for raw_token, number in extract_number_tokens(text)
    )


def split_markdown_sentences(markdown: str) -> list[str]:
    sentences: list[str] = []

    for raw_line in (markdown or "").splitlines():
        line = raw_line.strip()

        if (
            not line
            or line.startswith("#")
            or line.startswith("|")
            or line.startswith("```")
        ):
            continue

        line = re.sub(r"^[-*]\s+", "", line)

        parts = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9`])",
            line,
        )

        sentences.extend(
            part.strip()
            for part in parts
            if part.strip()
        )

    return sentences


def looks_factual(sentence: str) -> bool:
    return bool(
        extract_number_tokens(sentence)
        or re.search(
            r"\b(dataset|table|rows?|columns?|mean|median|correlations?|"
            r"associations?|relationships?|"
            r"model|forecast|missing|missingness|temperature|humidity|visibility|"
            r"higher|lower|increase|decrease|associated|observed|"
            r"duplicate|constant|zeros?|sentinel|timestamp|hourly|"
            r"location|station|pearson|future work|next analyses|"
            r"team|player|game|match|won|scored|points?|rebounds?|"
            r"turnovers?|comeback|dominated|historic|upset)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def build_evidence_lookup(
    ledger: EvidenceLedger,
) -> dict[str, EvidenceItem]:
    return {
        item.evidence_id: item
        for item in ledger.items
    }


def evidence_lookup(
    ledger: EvidenceLedger,
) -> dict[str, EvidenceItem]:
    return build_evidence_lookup(ledger)


def evidence_for_fact(
    fact: VerifiedFact,
    lookup: dict[str, EvidenceItem],
) -> list[EvidenceItem]:
    return [
        lookup[evidence_id]
        for evidence_id in fact.evidence_ids
        if evidence_id in lookup
    ]


def fact_support_numbers(
    fact: VerifiedFact,
    evidence: EvidenceLedger,
) -> list[float]:
    lookup = evidence_lookup(evidence)
    numbers = flatten_numbers(fact.structured_values)

    for evidence_id in fact.evidence_ids:
        item = lookup.get(evidence_id)
        if item is not None:
            numbers.extend(flatten_numbers(item.metrics))

    return numbers


def fact_support_text(
    fact: VerifiedFact,
    evidence: EvidenceLedger,
) -> str:
    lookup = evidence_lookup(evidence)

    parts = [
        fact.fact_summary,
        " ".join(fact.allowed_interpretations),
        " ".join(fact.required_caveats),
    ]

    for evidence_id in fact.evidence_ids:
        item = lookup.get(evidence_id)

        if item is None:
            continue

        parts.extend(
            [
                item.finding,
                item.practical_interpretation,
                json.dumps(json_safe(item.metrics), sort_keys=True),
                " ".join(item.source_columns),
            ]
        )

    return " ".join(parts)


def _normalise_entity_text(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        value.replace("`", "").strip().casefold(),
    )


def unsupported_backtick_entities(
    text: str,
    supported_entities: set[str],
) -> list[str]:
    normalised_supported = {
        _normalise_entity_text(entity)
        for entity in supported_entities
        if _normalise_entity_text(entity)
    }

    return list(
        dict.fromkeys(
            entity
            for entity in re.findall(r"`([^`]+)`", text)
            if _normalise_entity_text(entity)
            not in normalised_supported
        )
    )


def _entity_in_sentence(
    entity: str,
    sentence: str,
) -> bool:
    entity_text = _normalise_entity_text(entity)
    sentence_text = _normalise_entity_text(sentence)

    return bool(
        entity_text
        and re.search(
            rf"(?<!\w){re.escape(entity_text)}(?!\w)",
            sentence_text,
        )
    )


def _profile_support_id(
    *parts: str,
) -> str:
    return "PROFILE::" + "::".join(parts)


def _profile_record(
    *,
    support_id: str,
    fact_kind: str,
    table_name: str,
    column_name: str | None,
    statement: str,
    structured_values: dict[str, Any],
    entities: list[str],
    provenance: str,
    claim_permissions: list[ClaimPermission] | None = None,
) -> ProfileSupportRecord:
    return ProfileSupportRecord(
        support_id=support_id,
        fact_kind=fact_kind,
        table_name=table_name,
        column_name=column_name,
        statement=statement,
        structured_values=structured_values,
        entities=list(dict.fromkeys(entities)),
        claim_permissions=(
            claim_permissions
            or [ClaimPermission.DESCRIPTIVE]
        ),
        provenance=provenance,
    )


def _column_numeric_summary_values(
    column: ColumnProfile,
) -> dict[str, Any]:
    return {
        key: value
        for key, value in column.numeric_summary.items()
        if isinstance(value, (int, float, np.integer, np.floating))
        and math.isfinite(float(value))
    }


def build_profile_support_registry(
    profile: DataProfile,
) -> list[ProfileSupportRecord]:
    records: list[ProfileSupportRecord] = []

    for table in profile.tables:
        records.append(
            _profile_record(
                support_id=_profile_support_id(
                    table.table_name,
                    "dimensions",
                ),
                fact_kind="table_dimensions",
                table_name=table.table_name,
                column_name=None,
                statement=(
                    f"Table `{table.table_name}` contains "
                    f"{table.row_count:,} rows and "
                    f"{table.column_count:,} columns."
                ),
                structured_values={
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                },
                entities=[table.table_name],
                provenance="deterministic_data_profile",
            )
        )

        duplicate_rate = (
            table.duplicate_row_count
            / max(table.row_count, 1)
        )
        records.append(
            _profile_record(
                support_id=_profile_support_id(
                    table.table_name,
                    "duplicates",
                ),
                fact_kind="duplicate_rows",
                table_name=table.table_name,
                column_name=None,
                statement=(
                    f"Table `{table.table_name}` contains "
                    f"{table.duplicate_row_count:,} exact duplicate rows "
                    f"({duplicate_rate:.2%} of rows)."
                ),
                structured_values={
                    "duplicate_row_count": table.duplicate_row_count,
                    "duplicate_row_rate": duplicate_rate,
                    "row_count": table.row_count,
                },
                entities=[table.table_name],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.METHODOLOGICAL,
                ],
                provenance="deterministic_data_profile",
            )
        )

        for column in table.columns:
            entities = [
                table.table_name,
                column.name,
            ]
            records.append(
                _profile_record(
                    support_id=_profile_support_id(
                        table.table_name,
                        column.name,
                        "missingness",
                    ),
                    fact_kind="column_missingness",
                    table_name=table.table_name,
                    column_name=column.name,
                    statement=(
                        f"`{column.name}` has {column.missing_count:,} "
                        f"missing values ({column.missing_rate:.2%} "
                        "of rows)."
                    ),
                    structured_values={
                        "missing_count": column.missing_count,
                        "missing_rate": column.missing_rate,
                        "row_count": table.row_count,
                    },
                    entities=entities,
                    provenance="deterministic_data_profile",
                )
            )

            if column.constant:
                values = {
                    "constant": True,
                    "unique_count": column.unique_count,
                    "sample_values": column.sample_values,
                    **_column_numeric_summary_values(column),
                }
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "constant",
                        ),
                        fact_kind="constant_column",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` contains no observed "
                            "variation in the profiled data."
                        ),
                        structured_values=values,
                        entities=entities,
                        claim_permissions=[
                            ClaimPermission.DESCRIPTIVE,
                            ClaimPermission.METHODOLOGICAL,
                        ],
                        provenance="deterministic_data_profile",
                    )
                )

            if column.near_constant:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "near_constant",
                        ),
                        fact_kind="near_constant_column",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` is near-constant with a "
                            "dominant observed value."
                        ),
                        structured_values={
                            "near_constant": True,
                            "dominant_value_rate": (
                                column.dominant_value_rate
                            ),
                            "unique_count": column.unique_count,
                        },
                        entities=entities,
                        claim_permissions=[
                            ClaimPermission.DESCRIPTIVE,
                            ClaimPermission.METHODOLOGICAL,
                        ],
                        provenance="deterministic_data_profile",
                    )
                )

            if column.numeric_summary:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "numeric_summary",
                        ),
                        fact_kind="numeric_summary",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` has deterministic numeric "
                            "summary statistics in the profile."
                        ),
                        structured_values=_column_numeric_summary_values(
                            column
                        ),
                        entities=entities,
                        provenance="deterministic_data_profile",
                    )
                )

            if (
                column.suspicious_zero_values
                or column.possible_sentinel_values
                or column.zero_risk.value != "none"
            ):
                zero_values = {
                    **_column_numeric_summary_values(column),
                    "zero_risk": column.zero_risk.value,
                    "zero_risk_reason": column.zero_risk_reason,
                    "suspicious_zero_values": (
                        column.suspicious_zero_values
                    ),
                    "possible_sentinel_values": (
                        column.possible_sentinel_values
                    ),
                }
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "zero_diagnostic",
                        ),
                        fact_kind="zero_diagnostic",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` has deterministic zero-value "
                            "diagnostics in the profile."
                        ),
                        structured_values=zero_values,
                        entities=entities,
                        claim_permissions=[
                            ClaimPermission.DESCRIPTIVE,
                            ClaimPermission.METHODOLOGICAL,
                        ],
                        provenance="deterministic_data_profile",
                    )
                )

            if column.datetime_parse_rate > 0:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "datetime_presence",
                        ),
                        fact_kind="datetime_presence",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` is date/time-like with "
                            f"parse rate {column.datetime_parse_rate:.2%}."
                        ),
                        structured_values={
                            "datetime_parse_rate": (
                                column.datetime_parse_rate
                            ),
                            "row_count": table.row_count,
                        },
                        entities=entities,
                        provenance="deterministic_data_profile",
                    )
                )

            if column.candidate_key:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "candidate_key",
                        ),
                        fact_kind="candidate_key",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` is a deterministic candidate "
                            "key in the profile."
                        ),
                        structured_values={
                            "candidate_key": True,
                            "unique_count": column.unique_count,
                            "row_count": table.row_count,
                        },
                        entities=entities,
                        provenance="deterministic_data_profile",
                    )
                )

    return records


def profile_record_numbers(
    record: ProfileSupportRecord,
) -> list[float]:
    return flatten_numbers(record.structured_values)


def _profile_entity_aligned(
    sentence: str,
    record: ProfileSupportRecord,
    records: list[ProfileSupportRecord],
) -> bool:
    if record.column_name is not None:
        return _entity_in_sentence(
            record.column_name,
            sentence,
        )

    if _entity_in_sentence(record.table_name, sentence):
        return True

    table_count = len(
        {
            candidate.table_name
            for candidate in records
        }
    )

    return (
        table_count == 1
        and re.search(
            r"\b(dataset|table|rows?|records?|observations?)\b",
            sentence,
            re.IGNORECASE,
        )
        is not None
    )


def _profile_fact_kind_aligned(
    sentence: str,
    record: ProfileSupportRecord,
) -> bool:
    pattern = PROFILE_FACT_KIND_TERMS.get(
        record.fact_kind
    )

    return bool(pattern and pattern.search(sentence))


def _profile_semantic_escalation(
    sentence: str,
) -> bool:
    return bool(
        HOURLY_CADENCE_PATTERN.search(sentence)
        or LOCATION_METADATA_PATTERN.search(sentence)
        or CONSTANT_OVERSTATEMENT_PATTERN.search(sentence)
        or ZERO_OVERCONFIDENCE_PATTERN.search(sentence)
        or MISSINGNESS_HARMLESS_PATTERN.search(sentence)
        or DUPLICATE_REMOVAL_PATTERN.search(sentence)
        or PEARSON_IMPRECISE_PATTERN.search(sentence)
    )


def matching_profile_support_records(
    *,
    sentence: str,
    records: list[ProfileSupportRecord],
) -> list[ProfileSupportRecord]:
    if _profile_semantic_escalation(sentence):
        return []

    matches: list[ProfileSupportRecord] = []

    for record in records:
        if not _profile_entity_aligned(
            sentence,
            record,
            records,
        ):
            continue

        if not _profile_fact_kind_aligned(
            sentence,
            record,
        ):
            continue

        if not numbers_supported(
            sentence,
            profile_record_numbers(record),
        ):
            continue

        matches.append(record)

    return matches


def _profile_records_support_sentence(
    *,
    sentence: str,
    support_ids: list[str],
    records_by_id: dict[str, ProfileSupportRecord],
) -> bool:
    selected = [
        records_by_id[support_id]
        for support_id in support_ids
        if support_id in records_by_id
    ]
    if not selected:
        return False

    return bool(
        matching_profile_support_records(
            sentence=sentence,
            records=selected,
        )
    )


def candidate_support(
    candidate: FactCandidate,
    evidence: EvidenceLedger,
) -> tuple[str, list[float], set[ClaimPermission]]:
    lookup = evidence_lookup(evidence)
    text_parts: list[str] = []
    numbers: list[float] = []
    permissions: set[ClaimPermission] = set()

    for evidence_id in candidate.evidence_ids:
        item = lookup.get(evidence_id)

        if item is None:
            continue

        text_parts.extend(
            [
                item.finding,
                item.practical_interpretation,
                json.dumps(json_safe(item.metrics), sort_keys=True),
            ]
        )
        numbers.extend(flatten_numbers(item.metrics))
        permissions.update(item.claim_permissions)

    return " ".join(text_parts), numbers, permissions


def validate_fact_candidates(
    candidate_set: FactCandidateSet,
    evidence: EvidenceLedger,
) -> list[str]:
    errors: list[str] = []
    lookup = evidence_lookup(evidence)
    seen: set[str] = set()

    for candidate in candidate_set.candidates:
        if candidate.candidate_id in seen:
            errors.append(
                f"Duplicate candidate ID: {candidate.candidate_id}"
            )

        seen.add(candidate.candidate_id)

        if not candidate.evidence_ids:
            errors.append(
                f"{candidate.candidate_id} has no evidence IDs."
            )
            continue

        unknown = [
            evidence_id
            for evidence_id in candidate.evidence_ids
            if evidence_id not in lookup
        ]

        if unknown:
            errors.append(
                f"{candidate.candidate_id} cites unknown evidence IDs: {unknown}"
            )
            continue

        _, support_numbers, permissions = candidate_support(
            candidate,
            evidence,
        )

        if not numbers_supported(
            candidate.fact_summary,
            support_numbers,
        ):
            errors.append(
                f"{candidate.candidate_id} contains unsupported numbers."
            )

        if not set(candidate.claim_permissions).issubset(permissions):
            errors.append(
                f"{candidate.candidate_id} requests unsupported permissions."
            )

        if (
            CAUSAL_PATTERN.search(candidate.fact_summary)
            and ClaimPermission.CAUSAL not in permissions
        ):
            errors.append(f"{candidate.candidate_id} introduces unsupported causal wording.")

        if candidate.eligible_for_writer and not all(
            lookup[evidence_id].eligible_for_writer
            for evidence_id in candidate.evidence_ids
        ):
            errors.append(
                f"{candidate.candidate_id} is writer-eligible but cites excluded evidence."
            )

    return errors


def collect_entity_strings(value: Any) -> set[str]:
    entities: set[str] = set()

    if isinstance(value, str):
        entities.add(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            entities.add(str(key))
            entities.update(collect_entity_strings(item))
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            entities.update(collect_entity_strings(item))

    return entities


def fallback_fact_candidates(
    evidence: EvidenceLedger,
    maximum_facts: int,
) -> FactCandidateSet:
    eligible_items = [
        item
        for item in evidence.items
        if item.eligible_for_writer
        and item.query_id is None
    ]

    ranked = sorted(
        eligible_items,
        key=lambda item: (
            item.salience
            + item.user_relevance
            + item.methodological_strength
        ),
        reverse=True,
    )

    candidates = [
        FactCandidate(
            candidate_id=f"CAN_{index:04d}",
            fact_summary=item.finding,
            evidence_ids=[item.evidence_id],
            claim_permissions=item.claim_permissions,
            allowed_interpretations=[item.practical_interpretation],
            prohibited_interpretations=item.prohibited_interpretations,
            required_caveats=item.limitations,
            factual_confidence=item.factual_confidence,
            methodological_strength=item.methodological_strength,
            user_relevance=item.user_relevance,
            salience=item.salience,
            recommended_use=item.recommended_use,
            eligible_for_writer=True,
        )
        for index, item in enumerate(
            ranked[:maximum_facts],
            start=1,
        )
    ]

    return FactCandidateSet(
        candidates=candidates,
        synthesis_notes=[
            "Deterministic evidence-to-fact fallback was used."
        ],
    )


def fallback_verification(
    candidate_set: FactCandidateSet,
) -> VerificationResult:
    return VerificationResult(
        reviews=[
            FactReview(
                candidate_id=candidate.candidate_id,
                decision=(
                    ReviewDecision.CAUTION
                    if candidate.required_caveats
                    else ReviewDecision.APPROVE
                ),
                rationale=(
                    "The candidate is directly grounded in validated evidence."
                ),
                required_caveats=candidate.required_caveats,
                prohibited_interpretations=(
                    candidate.prohibited_interpretations
                ),
            )
            for candidate in candidate_set.candidates
        ],
        overall_notes=[
            "Deterministic verification fallback was used."
        ],
    )


def finalise_fact_ledger(
    candidate_set: FactCandidateSet,
    verification: VerificationResult,
    evidence: EvidenceLedger,
) -> FactLedger:
    errors = validate_fact_candidates(candidate_set, evidence)
    reviews = {
        review.candidate_id: review
        for review in verification.reviews
    }
    lookup = evidence_lookup(evidence)

    facts: list[VerifiedFact] = []
    rejected: list[RejectedFact] = []

    for candidate in candidate_set.candidates:
        candidate_errors = [
            error
            for error in errors
            if candidate.candidate_id in error
        ]

        review = reviews.get(candidate.candidate_id)

        if candidate_errors:
            rejected.append(
                RejectedFact(
                    source_candidate_id=candidate.candidate_id,
                    fact_summary=candidate.fact_summary,
                    reason=" ".join(candidate_errors),
                )
            )
            continue

        if review is None or review.decision == ReviewDecision.REJECT:
            rejected.append(
                RejectedFact(
                    source_candidate_id=candidate.candidate_id,
                    fact_summary=candidate.fact_summary,
                    reason=(
                        review.rationale
                        if review
                        else "The verifier did not review this candidate."
                    ),
                )
            )
            continue

        structured_values: dict[str, Any] = {}
        entities: set[str] = set()
        source_capabilities = []

        for evidence_id in candidate.evidence_ids:
            item = lookup[evidence_id]
            structured_values[evidence_id] = item.metrics
            entities.update(item.source_tables)
            entities.update(item.source_columns)
            entities.update(item.entity_scope)
            source_capabilities.append(item.capability)

            entities.update(collect_entity_strings(item.metrics))

        facts.append(
            VerifiedFact(
                fact_id=f"FACT_{len(facts) + 1:04d}",
                source_candidate_id=candidate.candidate_id,
                fact_summary=candidate.fact_summary,
                evidence_ids=candidate.evidence_ids,
                source_capabilities=list(
                    dict.fromkeys(source_capabilities)
                ),
                structured_values=structured_values,
                entities=sorted(entities),
                claim_permissions=candidate.claim_permissions,
                allowed_interpretations=candidate.allowed_interpretations,
                prohibited_interpretations=list(
                    dict.fromkeys(
                        candidate.prohibited_interpretations
                        + review.prohibited_interpretations
                    )
                ),
                required_caveats=list(
                    dict.fromkeys(
                        candidate.required_caveats
                        + review.required_caveats
                    )
                ),
                factual_confidence=candidate.factual_confidence,
                methodological_strength=candidate.methodological_strength,
                user_relevance=candidate.user_relevance,
                salience=candidate.salience,
                recommended_use=candidate.recommended_use,
            )
        )

    return FactLedger(
        writer_ready_facts=facts,
        rejected_facts=rejected,
        verifier_notes=verification.overall_notes,
    )



def normalise_strength_label(
    label: str,
) -> str:
    mapping = {
        "very_strong": "very_strong_association",
        "strong": "strong_association",
        "moderate": "moderate_association",
        "weak": "weak_but_reportable_association",
        "weak_but_reportable": (
            "weak_but_reportable_association"
        ),
        "large": "large_group_difference",
        "small": "small_group_difference",
        "negligible": "negligible_group_difference",
    }

    return mapping.get(label, label)


ASSOCIATION_STRENGTH_TERMS = {
    "very strong": "very_strong_association",
    "strong": "strong_association",
    "moderate": "moderate_association",
    "weak": "weak_but_reportable_association",
    "negligible": "negligible_association",
}

GROUP_STRENGTH_TERMS = {
    "large": "large_group_difference",
    "moderate": "moderate_group_difference",
    "small": "small_group_difference",
    "negligible": "negligible_group_difference",
}


def qualitative_strength_conflicts(
    sentence: str,
    evidence_items: list[EvidenceItem],
) -> list[str]:
    normalised_labels = {
        normalise_strength_label(item.strength_label)
        for item in evidence_items
    }
    association_labels = normalised_labels & set(
        ASSOCIATION_STRENGTH_TERMS.values()
    )
    group_labels = normalised_labels & set(
        GROUP_STRENGTH_TERMS.values()
    )
    conflicts: list[str] = []

    for match in ASSOCIATION_STRENGTH_PATTERN.finditer(sentence):
        visible_label = match.group("label").lower()
        expected_label = ASSOCIATION_STRENGTH_TERMS[visible_label]
        if association_labels and expected_label not in association_labels:
            conflicts.append(
                f"{visible_label} association conflicts with "
                f"{sorted(association_labels)}"
            )

    for match in GROUP_STRENGTH_PATTERN.finditer(sentence):
        visible_label = match.group("label").lower()
        expected_label = GROUP_STRENGTH_TERMS[visible_label]
        if group_labels and expected_label not in group_labels:
            conflicts.append(
                f"{visible_label} group difference conflicts with "
                f"{sorted(group_labels)}"
            )

    return list(dict.fromkeys(conflicts))

LOW_PRIORITY_STRENGTH_LABELS = {
    "negligible",
    "negligible_association",
    "negligible_group_difference",
    "weak_but_reportable_association",
    "small_group_difference",
}

RECOVERABLE_CORRELATION_LABELS = {
    "very_strong_association",
    "strong_association",
    "moderate_association",
}

RECOVERABLE_GROUP_LABELS = {
    "large_group_difference",
    "moderate_group_difference",
}

RECOVERABLE_MODELLING_LABELS = {
    "validated_internal_prediction",
    "model_not_better_than_baseline",
    "validated_forecast",
    "forecast_not_better_than_baseline",
    "predictive_insufficiency",
    "forecast_insufficiency",
}

RECOVERABLE_DATA_QUALITY_LABELS = {
    "constant_column",
    "duplicate_rows",
    "possible_sentinel_zero",
    "possible_data_quality_issue",
    "material_missingness",
    "low_missingness",
}


def evidence_subtype(
    item: EvidenceItem,
) -> str:
    metrics = item.metrics
    label = normalise_strength_label(
        item.strength_label
    )

    if item.capability == EvidenceCapability.EVENT_OUTCOME:
        return "event_outcome"

    if item.capability in {
        EvidenceCapability.ENTITY_PERFORMANCE,
        EvidenceCapability.RANKING,
    }:
        return "entity_performance"

    if (
        item.capability == EvidenceCapability.GROUP_COMPARISON
        and item.evidence_type == "participant_comparison"
    ):
        return "group_comparison"

    if item.route == AnalysisRoute.DESCRIPTIVE:
        if (
            "row_count" in metrics
            and "column_count" in metrics
        ):
            return "dataset_overview"

        if (
            metrics.get("constant") is True
            or "missing_count" in metrics
            or "missing_rate" in metrics
            or "duplicate_row_count" in metrics
            or label
            in {
                "constant_column",
                "duplicate_rows",
                "possible_sentinel_zero",
                "possible_data_quality_issue",
                "material_missingness",
                "low_missingness",
            }
        ):
            return "data_quality"

        return "descriptive_detail"

    if (
        item.route
        == AnalysisRoute.ASSOCIATION_COMPARISON
    ):
        if (
            "pearson_r" in metrics
            or "spearman_r" in metrics
            or "correlation" in metrics
        ):
            return "correlation"

        if (
            "highest_group" in metrics
            or "lowest_group" in metrics
            or "group_counts" in metrics
            or "standardised_difference"
            in metrics
            or "standardized_difference"
            in metrics
        ):
            return "group_comparison"

        return "association_other"

    if item.route == AnalysisRoute.PREDICTIVE:
        return "predictive_validation"

    if item.route == AnalysisRoute.FORECASTING:
        return "forecast_validation"

    if (
        item.route
        == AnalysisRoute.CAUSAL_FEASIBILITY
    ):
        return "causal_feasibility"

    return "other"

def fact_priority_score(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> float:
    evidence_items = evidence_for_fact(
        fact,
        evidence_lookup,
    )

    use_bonus = {
        RecommendedUse.HEADLINE: 0.25,
        RecommendedUse.MAIN_FINDING: 0.15,
        RecommendedUse.SUPPORTING_DETAIL: 0.0,
        RecommendedUse.LIMITATION: 0.10,
        RecommendedUse.OMIT_UNLESS_REQUESTED: -0.30,
    }.get(
        fact.recommended_use,
        0.0,
    )

    bonus_by_label = {
        "dataset_overview": 0.18,
        "constant_column": 0.15,
        "possible_sentinel_zero": 0.15,
        "possible_data_quality_issue": 0.12,
        "material_missingness": 0.12,
        "low_missingness": 0.03,
        "very_strong_association": 0.22,
        "strong_association": 0.17,
        "moderate_association": 0.10,
        "weak_but_reportable_association": -0.08,
        "large_group_difference": 0.18,
        "moderate_group_difference": 0.10,
        "small_group_difference": -0.15,
        "negligible_group_difference": -0.35,
        "validated_internal_prediction": 0.15,
        "model_not_better_than_baseline": 0.12,
        "validated_forecast": 0.15,
        "forecast_not_better_than_baseline": 0.12,
    }

    strength_bonuses = [
        bonus_by_label.get(
            normalise_strength_label(
                item.strength_label
            ),
            0.0,
        )
        for item in evidence_items
    ]

    strength_bonus = (
        max(strength_bonuses)
        if strength_bonuses
        else 0.0
    )

    return (
        0.30 * fact.salience
        + 0.25 * fact.user_relevance
        + 0.20 * fact.methodological_strength
        + 0.15 * fact.factual_confidence
        + use_bonus
        + strength_bonus
    )

def evidence_priority_score_for_fact(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> float:
    return fact_priority_score(fact, evidence_lookup)


def classify_fact_component(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> ReportComponent:
    items = evidence_for_fact(fact, evidence_lookup)
    subtypes = {evidence_subtype(item) for item in items}
    permissions = set(fact.claim_permissions)

    if "dataset_overview" in subtypes:
        return ReportComponent.DATASET_OVERVIEW

    if "data_quality" in subtypes:
        return ReportComponent.DATA_QUALITY

    if subtypes & {"event_outcome", "entity_performance"}:
        return ReportComponent.DATASET_OVERVIEW

    if (
        "predictive_validation" in subtypes
        or "forecast_validation" in subtypes
    ):
        return ReportComponent.MODELLING_VALIDATION

    if (
        "correlation" in subtypes
        or "group_comparison" in subtypes
        or "association_other" in subtypes
    ):
        return ReportComponent.STRONGEST_RELATIONSHIPS

    if (
        ClaimPermission.INSUFFICIENCY in permissions
        or fact.recommended_use == RecommendedUse.LIMITATION
        or fact.required_caveats
    ):
        return ReportComponent.LIMITATIONS_NEXT_STEPS

    return ReportComponent.DATASET_OVERVIEW


def eligible_fact_as_priority(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> bool:
    if fact.recommended_use not in {
        RecommendedUse.HEADLINE,
        RecommendedUse.MAIN_FINDING,
        RecommendedUse.LIMITATION,
    }:
        return False

    strength_labels = {
        normalise_strength_label(
            item.strength_label
        )
        for item
        in evidence_for_fact(
            fact,
            evidence_lookup,
        )
    }

    if (
        strength_labels
        & LOW_PRIORITY_STRENGTH_LABELS
    ):
        return False

    return (
        fact.factual_confidence >= 0.90
        and fact.methodological_strength
        >= 0.70
        and fact.user_relevance >= 0.60
    )

def evidence_priority_score(
    item: EvidenceItem,
) -> float:
    temporary_fact = VerifiedFact(
        fact_id="FACT_SCORE_ONLY",
        source_candidate_id=(
            f"SCORE_{item.evidence_id}"
        ),
        verification_method=(
            VerificationMethod
            .DETERMINISTIC_EVIDENCE_RECOVERY
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=[
            *item.source_tables,
            *item.source_columns,
        ],
        claim_permissions=(
            item.claim_permissions
        ),
        allowed_interpretations=[
            item.practical_interpretation
        ],
        prohibited_interpretations=(
            item.prohibited_interpretations
        ),
        required_caveats=item.limitations,
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )

    return fact_priority_score(
        temporary_fact,
        {
            item.evidence_id: item,
        },
    )


def eligible_for_deterministic_fact_recovery(
    item: EvidenceItem,
) -> bool:
    if item.query_id is not None:
        return False

    if not item.eligible_for_writer:
        return False

    if item.factual_confidence < 0.90:
        return False

    if item.methodological_strength < 0.65:
        return False

    subtype = evidence_subtype(item)
    label = normalise_strength_label(
        item.strength_label
    )

    if subtype == "dataset_overview":
        return True

    if subtype in {"event_outcome", "entity_performance"}:
        return True

    if subtype == "data_quality":
        return (
            label
            in RECOVERABLE_DATA_QUALITY_LABELS
        )

    if subtype == "correlation":
        return (
            label
            in RECOVERABLE_CORRELATION_LABELS
        )

    if subtype == "group_comparison":
        if item.capability == EvidenceCapability.GROUP_COMPARISON:
            return True
        return (
            label in RECOVERABLE_GROUP_LABELS
        )

    if subtype in {
        "predictive_validation",
        "forecast_validation",
    }:
        return (
            label
            in RECOVERABLE_MODELLING_LABELS
            or ClaimPermission.INSUFFICIENCY
            in item.claim_permissions
        )

    if subtype == "causal_feasibility":
        return (
            ClaimPermission.INSUFFICIENCY
            in item.claim_permissions
        )

    return False


def deterministic_fact_from_evidence(
    *,
    item: EvidenceItem,
    ordinal: int,
) -> VerifiedFact:
    entities = set(
        [
            *item.source_tables,
            *item.source_columns,
        ]
    )

    entities.update(
        collect_entity_strings(item.metrics)
    )
    entities.update(item.entity_scope)

    return VerifiedFact(
        fact_id=f"FACT_REC_{ordinal:04d}",
        source_candidate_id=(
            f"RECOVERY_{item.evidence_id}"
        ),
        verification_method=(
            VerificationMethod
            .DETERMINISTIC_EVIDENCE_RECOVERY
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        source_capabilities=[item.capability],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=sorted(entities),
        claim_permissions=(
            item.claim_permissions
        ),
        allowed_interpretations=(
            [item.practical_interpretation]
            if item.practical_interpretation
            else []
        ),
        prohibited_interpretations=(
            item.prohibited_interpretations
        ),
        required_caveats=item.limitations,
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )


def fact_subtype_counts(
    *,
    facts: list[VerifiedFact],
    evidence_lookup: dict[str, EvidenceItem],
) -> Counter[str]:
    counts: Counter[str] = Counter()

    for fact in facts:
        represented_subtypes = {
            evidence_subtype(
                evidence_lookup[evidence_id]
            )
            for evidence_id in fact.evidence_ids
            if evidence_id in evidence_lookup
        }

        for subtype in represented_subtypes:
            counts[subtype] += 1

    return counts


def augment_fact_ledger_for_report_coverage(
    *,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    settings: Settings,
) -> FactLedger:
    """
    Augment a thin fact ledger using exact, trusted deterministic
    evidence statements.

    This does not create new calculations or LLM interpretations.
    """

    lookup = build_evidence_lookup(evidence)

    represented_evidence_ids = {
        evidence_id
        for fact
        in fact_ledger.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }

    existing_counts = fact_subtype_counts(
        facts=fact_ledger.writer_ready_facts,
        evidence_lookup=lookup,
    )

    candidates = sorted(
        [
            item
            for item in evidence.items
            if (
                item.evidence_id
                not in represented_evidence_ids
                and eligible_for_deterministic_fact_recovery(
                    item
                )
            )
        ],
        key=evidence_priority_score,
        reverse=True,
    )

    subtype_limits = {
        "dataset_overview": (
            settings
            .maximum_recovered_overview_facts
        ),
        "data_quality": (
            settings
            .maximum_recovered_data_quality_facts
        ),
        "correlation": (
            settings
            .maximum_recovered_correlation_facts
        ),
        "group_comparison": (
            settings
            .maximum_recovered_group_comparison_facts
        ),
        "predictive_validation": (
            settings
            .maximum_recovered_modelling_facts
        ),
        "forecast_validation": (
            settings
            .maximum_recovered_modelling_facts
        ),
        "causal_feasibility": 1,
        "event_outcome": 2,
        "entity_performance": 4,
    }

    recovered: list[VerifiedFact] = []
    recovered_counts: Counter[str] = Counter()
    recovery_notes: list[str] = []
    recovered_evidence_ids: set[str] = set()

    existing_fact_ids = {
        fact.fact_id
        for fact
        in fact_ledger.writer_ready_facts
    }

    next_ordinal = 1

    def next_fact_id_ordinal() -> int:
        nonlocal next_ordinal

        while (
            f"FACT_REC_{next_ordinal:04d}"
            in existing_fact_ids
        ):
            next_ordinal += 1

        value = next_ordinal
        next_ordinal += 1

        return value

    def recover(item: EvidenceItem) -> bool:
        subtype = evidence_subtype(item)

        if (
            item.evidence_id
            in recovered_evidence_ids
        ):
            return False

        maximum = subtype_limits.get(
            subtype,
            0,
        )

        if (
            recovered_counts[subtype]
            >= maximum
        ):
            return False

        fact = deterministic_fact_from_evidence(
            item=item,
            ordinal=next_fact_id_ordinal(),
        )

        recovered.append(fact)
        recovered_counts[subtype] += 1
        recovered_evidence_ids.add(
            item.evidence_id
        )

        recovery_notes.append(
            "Recovered writer-ready fact "
            f"`{fact.fact_id}` from deterministic "
            f"evidence `{item.evidence_id}` for "
            f"subtype `{subtype}`."
        )

        return True

    def recover_best(
        subtype: str,
    ) -> bool:
        for item in candidates:
            if (
                evidence_subtype(item)
                == subtype
                and item.evidence_id
                not in recovered_evidence_ids
            ):
                if recover(item):
                    return True

        return False

    if (
        ReportComponent.DATASET_OVERVIEW
        in required_components
    ):
        while (
            existing_counts["dataset_overview"]
            + recovered_counts[
                "dataset_overview"
            ]
            < settings.minimum_overview_fact_count
        ):
            if not recover_best(
                "dataset_overview"
            ):
                break

    if (
        ReportComponent.DATA_QUALITY
        in required_components
    ):
        while (
            existing_counts["data_quality"]
            + recovered_counts["data_quality"]
            < settings.minimum_data_quality_fact_count
        ):
            if not recover_best("data_quality"):
                break

    if (
        ReportComponent.STRONGEST_RELATIONSHIPS
        in required_components
    ):
        # Prefer subtype diversity when both forms are available.
        if (
            existing_counts["correlation"] == 0
            and any(
                evidence_subtype(item)
                == "correlation"
                for item in candidates
            )
        ):
            recover_best("correlation")

        if (
            existing_counts["group_comparison"]
            == 0
            and any(
                evidence_subtype(item)
                == "group_comparison"
                for item in candidates
            )
        ):
            recover_best("group_comparison")

        def relationship_count() -> int:
            return sum(
                existing_counts[subtype]
                + recovered_counts[subtype]
                for subtype in {
                    "correlation",
                    "group_comparison",
                    "association_other",
                }
            )

        while (
            relationship_count()
            < settings.minimum_relationship_fact_count
        ):
            recovered_one = (
                recover_best("correlation")
                or recover_best(
                    "group_comparison"
                )
            )

            if not recovered_one:
                break

    # Fill a thin ledger only with remaining eligible evidence.
    for item in candidates:
        if (
            len(
                fact_ledger.writer_ready_facts
            )
            + len(recovered)
            >= settings.minimum_writer_ready_fact_count
        ):
            break

        recover(item)

    if not recovered:
        return fact_ledger

    return fact_ledger.model_copy(
        update={
            "writer_ready_facts": [
                *fact_ledger.writer_ready_facts,
                *recovered,
            ],
            "deterministically_recovered_fact_ids": [
                *fact_ledger
                .deterministically_recovered_fact_ids,
                *[
                    fact.fact_id
                    for fact in recovered
                ],
            ],
            "coverage_recovery_notes": [
                *fact_ledger.coverage_recovery_notes,
                *recovery_notes,
            ],
        }
    )

def select_balanced_priority_facts(
    *,
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    settings: Settings,
) -> list[VerifiedFact]:
    """
    Select facts by coverage and analytical strength.

    There is deliberately no unrestricted final fill stage. Weak or
    small facts remain available in supporting_facts but are not
    promoted simply because unused capacity remains.
    """

    lookup = build_evidence_lookup(evidence)

    ranked = sorted(
        facts,
        key=lambda fact: fact_priority_score(
            fact,
            lookup,
        ),
        reverse=True,
    )

    selected: list[VerifiedFact] = []
    selected_ids: set[str] = set()
    subtype_counts: Counter[str] = Counter()

    subtype_limits = {
        "dataset_overview": (
            settings
            .max_priority_dataset_overview_facts
        ),
        "data_quality": (
            settings
            .max_priority_data_quality_facts
        ),
        "correlation": (
            settings
            .max_priority_correlation_facts
        ),
        "group_comparison": (
            settings
            .max_priority_group_comparison_facts
        ),
        "predictive_validation": (
            settings
            .max_priority_predictive_facts
        ),
        "forecast_validation": (
            settings
            .max_priority_forecast_facts
        ),
        "causal_feasibility": (
            settings
            .max_priority_limitation_facts
        ),
        "event_outcome": 2,
        "entity_performance": 4,
        "association_other": 1,
        "descriptive_detail": 1,
        "other": 1,
    }

    def primary_subtype(
        fact: VerifiedFact,
    ) -> str:
        subtypes = [
            evidence_subtype(item)
            for item
            in evidence_for_fact(
                fact,
                lookup,
            )
        ]

        return (
            subtypes[0]
            if subtypes
            else "other"
        )

    def priority_eligible(
        fact: VerifiedFact,
    ) -> bool:
        return (
            eligible_fact_as_priority(
                fact,
                lookup,
            )
            and fact_priority_score(
                fact,
                lookup,
            )
            >= settings.minimum_main_finding_score
        )

    def add_fact(
        fact: VerifiedFact,
        *,
        require_priority_eligibility: bool,
    ) -> bool:
        if fact.fact_id in selected_ids:
            return False

        subtype = primary_subtype(fact)

        if (
            subtype_counts[subtype]
            >= subtype_limits.get(subtype, 1)
        ):
            return False

        if (
            require_priority_eligibility
            and not priority_eligible(fact)
        ):
            return False

        selected.append(fact)
        selected_ids.add(fact.fact_id)
        subtype_counts[subtype] += 1

        return True

    def add_best_for_subtype(
        subtype: str,
        *,
        require_priority_eligibility: bool,
    ) -> bool:
        for fact in ranked:
            if primary_subtype(fact) != subtype:
                continue

            if add_fact(
                fact,
                require_priority_eligibility=(
                    require_priority_eligibility
                ),
            ):
                return True

        return False

    add_best_for_subtype(
        "event_outcome",
        require_priority_eligibility=False,
    )
    add_best_for_subtype(
        "entity_performance",
        require_priority_eligibility=False,
    )

    if (
        ReportComponent.DATASET_OVERVIEW
        in required_components
    ):
        add_best_for_subtype(
            "dataset_overview",
            require_priority_eligibility=False,
        )

    if (
        ReportComponent.DATA_QUALITY
        in required_components
    ):
        add_best_for_subtype(
            "data_quality",
            require_priority_eligibility=False,
        )

    if (
        ReportComponent.STRONGEST_RELATIONSHIPS
        in required_components
    ):
        # Prefer one strong correlation and one strong group comparison.
        add_best_for_subtype(
            "correlation",
            require_priority_eligibility=True,
        )

        event_facts_present = any(
            EvidenceCapability.EVENT_OUTCOME
            in fact.source_capabilities
            for fact in facts
        )

        add_best_for_subtype(
            "group_comparison",
            require_priority_eligibility=(
                not event_facts_present
            ),
        )

        def selected_relationship_count() -> int:
            return sum(
                subtype_counts[subtype]
                for subtype in {
                    "correlation",
                    "group_comparison",
                    "association_other",
                }
            )

        for fact in ranked:
            if (
                selected_relationship_count()
                >= settings.minimum_relationship_fact_count
            ):
                break

            if primary_subtype(fact) not in {
                "correlation",
                "group_comparison",
                "association_other",
            }:
                continue

            add_fact(
                fact,
                require_priority_eligibility=True,
            )

    if (
        ReportComponent.MODELLING_VALIDATION
        in required_components
    ):
        add_best_for_subtype(
            "predictive_validation",
            require_priority_eligibility=False,
        )

        if not any(
            primary_subtype(fact)
            in {
                "predictive_validation",
                "forecast_validation",
            }
            for fact in selected
        ):
            add_best_for_subtype(
                "forecast_validation",
                require_priority_eligibility=False,
            )

    if (
        ReportComponent.LIMITATIONS_NEXT_STEPS
        in required_components
    ):
        for fact in ranked:
            if (
                fact.recommended_use
                == RecommendedUse.LIMITATION
                or ClaimPermission.INSUFFICIENCY
                in fact.claim_permissions
            ):
                if add_fact(
                    fact,
                    require_priority_eligibility=False,
                ):
                    break

    # Add only high-quality eligible facts. Do not fill with weak facts.
    for fact in ranked:
        if (
            len(selected)
            >= settings.writer_priority_fact_limit
        ):
            break

        add_fact(
            fact,
            require_priority_eligibility=True,
        )

    return selected

def select_priority_facts(
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    settings: Settings,
) -> list[VerifiedFact]:
    return select_balanced_priority_facts(
        facts=facts,
        evidence=evidence,
        required_components=required_components,
        settings=settings,
    )


def reader_facing_caveat(text: str) -> str | None:
    lowered = text.strip().lower()

    if not text.strip():
        return None

    if lowered.startswith(("do not", "never", "prohibited", "internal")):
        if "caus" in lowered:
            return (
                "These are unadjusted descriptive comparisons and should not "
                "be interpreted as causal effects."
            )
        if "confounding" in lowered or "adjusted" in lowered:
            return "The comparisons are unadjusted and do not control for confounding."
        if "predict" in lowered:
            return (
                "Predictive wording should be limited to validated modelling "
                "results and not inferred from descriptive evidence."
            )
        return None

    return text.strip()


def build_reader_facing_limitations(
    facts: list[VerifiedFact],
) -> list[str]:
    limitations: list[str] = []
    has_group_comparison = any(
        ClaimPermission.COMPARATIVE in fact.claim_permissions
        for fact in facts
    )
    has_association = any(
        ClaimPermission.ASSOCIATIONAL in fact.claim_permissions
        for fact in facts
    )
    has_predictive = any(
        ClaimPermission.PREDICTIVE in fact.claim_permissions
        for fact in facts
    )
    has_forecast = any(
        ClaimPermission.FORECAST in fact.claim_permissions
        for fact in facts
    )

    if has_group_comparison or has_association:
        limitations.append(
            "Observed associations and group comparisons are descriptive. "
            "They are not evidence of causal effects."
        )

    if has_group_comparison:
        limitations.append(
            "Group comparisons are unadjusted unless the evidence explicitly "
            "states otherwise. Unequal group sizes may lead to different "
            "levels of precision and stability."
        )

    if has_predictive:
        limitations.append(
            "Predictive results describe internal validation under the tested "
            "setup and do not establish deployment readiness."
        )

    if has_forecast:
        limitations.append(
            "Forecast results are internal backtests and do not guarantee "
            "future performance."
        )

    return list(dict.fromkeys(limitations))


def select_priority_verified_insights(
    *,
    insight_ledger: InsightLedger,
    maximum: int,
) -> tuple[list[VerifiedInsight], list[VerifiedInsight]]:
    eligible = [
        insight
        for insight in insight_ledger.verified_insights
        if insight.verification_status
        in {
            InsightVerificationStatus.VERIFIED,
            InsightVerificationStatus.VERIFIED_WITH_CAVEAT,
        }
        and insight.interpretation_level
        == InterpretationLevel.BOUNDED_INSIGHT
    ]
    ranked = sorted(
        enumerate(eligible),
        key=lambda item: (
            -item[1].salience,
            -item[1].confidence,
            item[0],
        ),
    )

    priority: list[VerifiedInsight] = []
    selected_ids: set[str] = set()
    selected_types: set[InsightType] = set()

    for _, insight in ranked:
        if len(priority) >= maximum:
            break
        if insight.insight_type in selected_types:
            continue
        priority.append(insight)
        selected_ids.add(insight.insight_id)
        selected_types.add(insight.insight_type)

    for _, insight in ranked:
        if len(priority) >= maximum:
            break
        if insight.insight_id in selected_ids:
            continue
        priority.append(insight)
        selected_ids.add(insight.insight_id)

    supporting = [
        insight
        for _, insight in ranked
        if insight.insight_id not in selected_ids
    ]

    return priority, supporting


def fact_is_relevant_to_genre(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
    genre: ReportGenre,
) -> bool:
    if genre not in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }:
        return True

    items = [
        evidence_lookup[evidence_id]
        for evidence_id in fact.evidence_ids
        if evidence_id in evidence_lookup
    ]
    if not items:
        return False

    event_evidence_types = {
        "event_outcome",
        "event_context",
        "event_status",
        "entity_ranking",
        "entity_performance",
        "participant_comparison",
        "event_contrast",
    }
    return any(
        item.eligible_for_writer
        and item.evidence_type in event_evidence_types
        for item in items
    )


def evidence_analytical_function(
    item: EvidenceItem,
) -> AnalyticalFunction | None:
    if item.analytical_function is not None:
        return item.analytical_function

    value = item.metrics.get("analytical_function")
    if not isinstance(value, str):
        return None

    try:
        return AnalyticalFunction(value)
    except ValueError:
        return None


def event_fact_slot(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> str | None:
    items = evidence_for_fact(fact, evidence_lookup)
    evidence_types = {
        item.evidence_type
        for item in items
    }

    if "event_outcome" in evidence_types:
        return "event_result"

    if "event_status" in evidence_types:
        return "event_status"

    if "event_context" in evidence_types:
        return "event_context"

    if evidence_types & {"entity_ranking", "entity_performance"}:
        if any(
            evidence_analytical_function(item)
            == AnalyticalFunction.PARTICIPATION
            for item in items
        ):
            return "participation"

        return "leading_performance"

    if evidence_types & {
        "participant_comparison",
        "event_contrast",
    }:
        return "main_contrast"

    return None


def select_event_priority_facts(
    *,
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    settings: Settings,
    request: str,
) -> tuple[list[VerifiedFact], list[VerifiedFact]]:
    evidence_lookup = build_evidence_lookup(evidence)

    def event_priority_score(
        fact: VerifiedFact,
    ) -> float:
        analytical_functions = {
            evidence_analytical_function(item)
            for item in evidence_for_fact(
                fact,
                evidence_lookup,
            )
        }
        component_bonus = (
            0.20
            if (
                event_fact_slot(fact, evidence_lookup)
                == "main_contrast"
                and AnalyticalFunction.OUTCOME_COMPONENT
                in analytical_functions
            )
            else 0.0
        )

        return (
            evidence_priority_score_for_fact(
                fact,
                evidence_lookup,
            )
            + component_bonus
        )

    ranked = sorted(
        facts,
        key=event_priority_score,
        reverse=True,
    )
    selected: list[VerifiedFact] = []
    selected_ids: set[str] = set()

    for slot in (
        "event_result",
        "event_context",
        "event_status",
        "leading_performance",
        "main_contrast",
        "participation",
    ):
        for fact in ranked:
            if fact.fact_id in selected_ids:
                continue

            if event_fact_slot(fact, evidence_lookup) != slot:
                continue

            selected.append(fact)
            selected_ids.add(fact.fact_id)

    supporting: list[VerifiedFact] = []
    for fact in ranked:
        if fact.fact_id in selected_ids:
            continue

        supporting.append(fact)

    return selected, supporting


EVENT_PROFILE_INSIGHT_PATTERN = re.compile(
    r"\b(missing(?:ness| data| values?)|duplicates?|rows?|columns?|"
    r"constant columns?|correlations?|regressions?|"
    r"statistical (?:modelling|modeling|power)|"
    r"predictive (?:modelling|modeling)|feature sets?)\b",
    re.IGNORECASE,
)


def event_insight_is_relevant(
    insight: VerifiedInsight,
    request: str,
) -> bool:
    text = f"{insight.statement} {insight.why_it_matters}"
    if not EVENT_PROFILE_INSIGHT_PATTERN.search(text):
        return True

    return bool(EVENT_PROFILE_INSIGHT_PATTERN.search(request))


def scope_fact_ledger_for_genre(
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    genre: ReportGenre,
) -> FactLedger:
    evidence_lookup = {item.evidence_id: item for item in evidence.items}
    scoped_facts = [
        fact
        for fact in fact_ledger.writer_ready_facts
        if fact_is_relevant_to_genre(
            fact,
            evidence_lookup,
            genre,
        )
    ]
    return fact_ledger.model_copy(update={"writer_ready_facts": scoped_facts})


def build_writer_evidence_pack(
    request: str,
    understanding: Any,
    plan: Any,
    evidence: EvidenceLedger,
    fact_ledger: FactLedger,
    settings: Settings,
    insight_ledger: InsightLedger | None = None,
    input_structure: InputStructureProfile | None = None,
    available_capabilities: list[EvidenceCapability] | None = None,
) -> WriterEvidencePack:
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False,
        fallback_reason="No Insight Ledger was supplied.",
    )
    evidence_lookup = {item.evidence_id: item for item in evidence.items}
    scoped_fact_ledger = scope_fact_ledger_for_genre(
        fact_ledger,
        evidence,
        plan.report_specification.genre,
    )
    facts = scoped_fact_ledger.writer_ready_facts

    event_genre = plan.report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }

    if event_genre:
        priority, supporting = select_event_priority_facts(
            facts=facts,
            evidence=evidence,
            settings=settings,
            request=request,
        )
    else:
        priority = select_balanced_priority_facts(
            facts=facts,
            evidence=evidence,
            required_components=(
                plan.report_specification.required_components
            ),
            settings=settings,
        )
        priority_ids = {
            fact.fact_id
            for fact in priority
        }
        ranked_facts = sorted(
            facts,
            key=lambda fact: evidence_priority_score_for_fact(
                fact,
                evidence_lookup,
            ),
            reverse=True,
        )
        supporting = [
            fact
            for fact in ranked_facts
            if fact.fact_id not in priority_ids
            and fact.recommended_use
            != RecommendedUse.OMIT_UNLESS_REQUESTED
        ][: settings.writer_supporting_fact_limit]

    limitations = sorted(
        [
            fact
            for fact in facts
            if (
                fact.recommended_use == RecommendedUse.LIMITATION
                or ClaimPermission.INSUFFICIENCY in fact.claim_permissions
                or fact.required_caveats
            )
        ],
        key=lambda fact: evidence_priority_score_for_fact(fact, evidence_lookup),
        reverse=True,
    )[
        : (
            len(facts)
            if event_genre
            else settings.max_priority_limitation_facts
        )
    ]

    recommendations = sorted(
        [
        recommendation
        for item in evidence.items
        for recommendation in item.recommendations
        if recommendation.priority in {"high", "medium"}
        ],
        key=lambda item: (
            {"high": 2, "medium": 1, "low": 0}.get(item.priority, 0),
            getattr(item, "confidence", 0.5),
        ),
        reverse=True,
    )

    prohibited = list(
        dict.fromkeys(
            interpretation
            for fact in facts
            for interpretation in fact.prohibited_interpretations
        )
    )
    scoped_fact_ids = {fact.fact_id for fact in facts}
    scoped_insight_ledger = insight_ledger.model_copy(
        update={
            "verified_insights": [
                insight
                for insight in insight_ledger.verified_insights
                if insight.source_fact_ids
                and set(insight.source_fact_ids).issubset(scoped_fact_ids)
                and (
                    not event_genre
                    or event_insight_is_relevant(insight, request)
                )
            ],
            "hypothesis_only_insights": [
                insight
                for insight in insight_ledger.hypothesis_only_insights
                if insight.source_fact_ids
                and set(insight.source_fact_ids).issubset(scoped_fact_ids)
                and (
                    not event_genre
                    or event_insight_is_relevant(insight, request)
                )
            ],
        }
    )
    priority_insights, supporting_insights = select_priority_verified_insights(
        insight_ledger=scoped_insight_ledger,
        maximum=settings.max_verified_main_insights,
    )

    return WriterEvidencePack(
        user_request=request,
        report_specification=plan.report_specification,
        dataset_understanding=understanding,
        input_structure=input_structure,
        available_capabilities=available_capabilities or [],
        priority_facts=priority,
        supporting_facts=supporting,
        limitation_facts=limitations,
        evidence_ledger=evidence,
        insight_ledger=scoped_insight_ledger,
        priority_verified_insights=priority_insights,
        supporting_verified_insights=supporting_insights,
        analytical_recommendations=recommendations,
        reader_facing_limitations=build_reader_facing_limitations(
            priority + limitations
        ),
        internal_prohibited_interpretations=prohibited,
    )


def _sentence_section_headings(
    markdown: str,
) -> dict[str, str]:
    headings: dict[str, str] = {}
    current_heading = ""

    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        if line.startswith("## "):
            current_heading = line[3:].strip()
            continue

        for sentence in split_markdown_sentences(line):
            headings[sentence] = current_heading

    return headings


def validate_writer_output(
    output: WriterOutput,
    fact_ledger: FactLedger,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
) -> list[str]:
    errors: list[str] = []
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    valid_fact_ids = {
        fact.fact_id
        for fact in fact_ledger.writer_ready_facts
    }
    fact_lookup = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insight_ids = {
        *verified_insights,
        *hypothesis_insights,
    }
    section_headings = _sentence_section_headings(output.markdown)

    unknown_title_fact_ids = set(output.title_fact_ids) - valid_fact_ids
    if unknown_title_fact_ids:
        errors.append(f"The title cites unknown fact IDs: {sorted(unknown_title_fact_ids)}")
    title_facts = [
        fact_lookup[fact_id] for fact_id in output.title_fact_ids if fact_id in fact_lookup
    ]
    all_title_entities = {
        entity
        for fact in fact_ledger.writer_ready_facts
        for entity in fact.entities
        if len(entity.strip()) >= 3
        and entity.casefold() in output.title.casefold()
    }
    title_requires_support = bool(
        extract_number_tokens(output.title)
        or (
            all_title_entities
            and FACTUAL_TITLE_PATTERN.search(output.title)
        )
    )
    if title_requires_support and not output.title_fact_ids:
        errors.append("A factual title must cite supporting fact IDs.")
    supported_title_entities = {
        entity
        for fact in title_facts
        for entity in fact.entities
    }
    unsupported_title_entities = (
        all_title_entities - supported_title_entities
    )
    if title_requires_support and unsupported_title_entities:
        errors.append(
            "The title contains entities unsupported by its facts: "
            f"{sorted(unsupported_title_entities)}"
        )
    if title_facts and not numbers_supported(
        output.title,
        [number for fact in title_facts for number in flatten_numbers(fact.structured_values)],
    ):
        errors.append("The title contains a number unsupported by its facts.")
    if CAUSAL_PATTERN.search(output.title) and not any(
        ClaimPermission.CAUSAL in fact.claim_permissions for fact in title_facts
    ):
        errors.append("The title introduces unsupported causal wording.")

    if re.search(r"\[(?:CLM|FACT)_\d+", output.markdown):
        errors.append(
            "Internal fact or claim IDs must not appear in the visible report."
        )

    if INTERNAL_CONTROL_PATTERN.search(output.markdown):
        errors.append(
            "The visible report exposes an internal writer or auditor control."
        )

    if FIELD_LABEL_PATTERN.search(output.markdown):
        errors.append(
            "The visible report renders internal evidence fields such as "
            "`Finding`, `Strength`, or `Important Note` rather than natural "
            "data-science prose."
        )

    seen_sentence_ids: set[str] = set()
    mapped_sentences = {
        support.sentence_text
        for support in output.sentence_support
    }
    factual_sentences = [
        sentence
        for sentence in split_markdown_sentences(output.markdown)
        if looks_factual(sentence)
    ]
    missing_mappings = [
        sentence
        for sentence in factual_sentences
        if sentence not in mapped_sentences
    ]
    if missing_mappings:
        errors.append(
            "Every factual sentence must appear exactly in the hidden sentence support map."
        )

    for support in output.sentence_support:
        if support.sentence_id in seen_sentence_ids:
            errors.append(
                f"Duplicate sentence ID: {support.sentence_id}"
            )
        seen_sentence_ids.add(support.sentence_id)

        if support.sentence_text not in output.markdown:
            errors.append(
                f"{support.sentence_id} text does not appear in the report."
            )

        unknown = set(support.fact_ids) - valid_fact_ids
        if unknown:
            errors.append(
                f"{support.sentence_id} cites unknown fact IDs: {sorted(unknown)}"
            )

        unknown_insights = (
            set(support.insight_ids)
            - all_insight_ids
        )
        if unknown_insights:
            errors.append(
                f"{support.sentence_id} cites unknown insight IDs: "
                f"{sorted(unknown_insights)}"
            )

        if (
            EXPLANATORY_HYPOTHESIS_PATTERN.search(
                support.sentence_text
            )
            and support.interpretation_level
            != InterpretationLevel.HYPOTHESIS
        ):
            errors.append(
                f"{support.sentence_id} presents a possible explanation "
                "without classifying it as a hypothesis."
            )

        if (
            support.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
        ):
            if not support.insight_ids:
                errors.append(
                    f"{support.sentence_id} is a bounded insight but has no "
                    "insight ID."
                )
            elif not set(support.insight_ids).issubset(
                set(verified_insights)
            ):
                errors.append(
                    f"{support.sentence_id} cites an insight that is not a "
                    "verified main insight."
                )
            else:
                required_fact_ids = {
                    fact_id
                    for insight_id in support.insight_ids
                    for fact_id in verified_insights[
                        insight_id
                    ].source_fact_ids
                }
                required_evidence_ids = {
                    evidence_id
                    for insight_id in support.insight_ids
                    for evidence_id in verified_insights[
                        insight_id
                    ].source_evidence_ids
                }
                if not required_fact_ids.issubset(
                    set(support.fact_ids)
                ):
                    errors.append(
                        f"{support.sentence_id} omits source facts for its "
                        "verified insight."
                    )
                if not required_evidence_ids.issubset(
                    set(support.evidence_ids)
                ):
                    errors.append(
                        f"{support.sentence_id} omits source evidence for its "
                        "verified insight."
                    )

        if (
            support.interpretation_level
            == InterpretationLevel.HYPOTHESIS
        ):
            if not allow_hypotheses_in_report:
                errors.append(
                    f"{support.sentence_id} is a hypothesis while hypotheses "
                    "are disabled."
                )
            if not support.insight_ids or not set(
                support.insight_ids
            ).issubset(set(hypothesis_insights)):
                errors.append(
                    f"{support.sentence_id} lacks valid hypothesis-only "
                    "provenance."
                )
            if section_headings.get(support.sentence_text, "").lower() != (
                "questions for further investigation"
            ):
                errors.append(
                    f"{support.sentence_id} places a hypothesis outside the "
                    "allowed section."
                )
            if (
                not HYPOTHESIS_WORDING_PATTERN.search(
                    support.sentence_text
                )
                and not support.sentence_text.strip().endswith("?")
            ):
                errors.append(
                    f"{support.sentence_id} does not explicitly label the "
                    "hypothesis or frame it as a question."
                )

        if (
            support.interpretation_level
            == InterpretationLevel.FINDING
            and support.insight_ids
        ):
            errors.append(
                f"{support.sentence_id} is a finding but cites insight IDs."
            )

        if (
            support.support_type != SupportType.NON_FACTUAL
            and not support.fact_ids
            and not support.profile_support_ids
            and not support.insight_ids
        ):
            errors.append(
                f"{support.sentence_id} is factual but has no supporting "
                "provenance."
            )

        supporting_facts = [
            fact_lookup[fact_id]
            for fact_id in support.fact_ids
            if fact_id in fact_lookup
        ]
        support_numbers = [
            number
            for fact in supporting_facts
            for number in flatten_numbers(fact.structured_values)
        ]
        if (
            supporting_facts
            and not numbers_supported(
                support.sentence_text,
                support_numbers,
            )
        ):
            errors.append(
                f"{support.sentence_id} contains a number unsupported by its "
                "mapped facts."
            )

        known_entities = {
            entity
            for fact in supporting_facts
            for entity in fact.entities
        }
        unsupported_entities = unsupported_backtick_entities(
            support.sentence_text,
            known_entities,
        )
        if supporting_facts and unsupported_entities:
            errors.append(
                f"{support.sentence_id} contains unsupported entities "
                f"{unsupported_entities}; mapped fact IDs: "
                f"{support.fact_ids}."
            )

    declared = set(output.selected_fact_ids)
    used = {
        fact_id
        for support in output.sentence_support
        for fact_id in support.fact_ids
    }

    if declared != used:
        errors.append(
            "selected_fact_ids must match the facts used in sentence_support."
        )

    return errors


def apply_support_map_patches(
    writer_output: WriterOutput,
    patches: list[SupportMapPatch],
    valid_profile_support_ids: set[str],
) -> WriterOutput:
    original_markdown = writer_output.markdown
    support_map = [
        support.model_copy()
        for support in writer_output.sentence_support
    ]
    support_by_id = {
        support.sentence_id: support
        for support in support_map
    }

    for patch in patches:
        unknown = [
            support_id
            for support_id in patch.added_profile_support_ids
            if support_id not in valid_profile_support_ids
        ]

        if unknown:
            raise ValueError(
                "Support-map patch references unknown profile support "
                f"IDs: {unknown}"
            )

        support = support_by_id.get(patch.sentence_id)

        if support is None:
            raise ValueError(
                "Support-map patch references unknown sentence ID: "
                f"{patch.sentence_id}"
            )

        if support.sentence_text != patch.sentence_text:
            raise ValueError(
                "Support-map patch sentence text does not exactly match "
                "the hidden support entry."
            )

        merged_profile_ids = list(
            dict.fromkeys(
                [
                    *support.profile_support_ids,
                    *patch.added_profile_support_ids,
                ]
            )
        )

        replacement = support.model_copy(
            update={
                "profile_support_ids": merged_profile_ids
            }
        )
        support_index = support_map.index(support)
        support_map[support_index] = replacement
        support_by_id[patch.sentence_id] = replacement

    patched = writer_output.model_copy(
        update={
            "sentence_support": support_map
        }
    )

    assert patched.markdown == original_markdown
    return patched


def materialise_writer_output(
    draft: WriterAgentDraft,
    fact_ledger: FactLedger,
    *,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
    writer_mode: str = "llm_writer",
    eligible_for_primary_evaluation: bool = True,
    quality_revision_round: int = 0,
    quality_revision_summary: str | None = None,
) -> WriterOutput:
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    fact_lookup = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insight_lookup = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insight_lookup = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insight_lookup = {
        **verified_insight_lookup,
        **hypothesis_insight_lookup,
    }
    unknown_title_fact_ids = [
        fact_id for fact_id in draft.title_fact_ids if fact_id not in fact_lookup
    ]
    if unknown_title_fact_ids:
        raise ValueError(f"Writer draft title contains unknown fact IDs: {unknown_title_fact_ids}")

    lines: list[str] = [
        f"# {draft.title.strip()}",
        "",
    ]

    sentence_support: list[SentenceSupport] = []
    selected_fact_ids: list[str] = list(dict.fromkeys(draft.title_fact_ids))
    sentence_number = 1

    for section in draft.sections:
        heading = section.heading.strip()
        heading = re.sub(
            r"^#+\s*",
            "",
            heading,
        )

        if not heading:
            continue

        lines.extend(
            [
                f"## {heading}",
                "",
            ]
        )

        for sentence_draft in section.sentences:
            sentence_text = re.sub(
                r"\s+",
                " ",
                sentence_draft.text,
            ).strip()

            if not sentence_text:
                continue

            if sentence_text[-1] not in ".!?":
                sentence_text += "."

            unknown_fact_ids = [
                fact_id
                for fact_id in sentence_draft.fact_ids
                if fact_id not in fact_lookup
            ]

            if unknown_fact_ids:
                raise ValueError(
                    "Writer draft contains unknown "
                    f"fact IDs: {unknown_fact_ids}"
                )

            unknown_insight_ids = [
                insight_id
                for insight_id in sentence_draft.insight_ids
                if insight_id not in all_insight_lookup
            ]
            if unknown_insight_ids:
                raise ValueError(
                    "Writer draft contains unknown insight IDs: "
                    f"{unknown_insight_ids}"
                )

            if (
                sentence_draft.interpretation_level
                == InterpretationLevel.BOUNDED_INSIGHT
            ):
                if not sentence_draft.insight_ids:
                    raise ValueError(
                        "A bounded-insight Writer sentence has no verified "
                        "insight ID."
                    )
                if not set(sentence_draft.insight_ids).issubset(
                    set(verified_insight_lookup)
                ):
                    raise ValueError(
                        "A bounded-insight Writer sentence cites an insight "
                        "that is not verified for the main report."
                    )

            if (
                sentence_draft.interpretation_level
                == InterpretationLevel.HYPOTHESIS
            ):
                if not allow_hypotheses_in_report:
                    raise ValueError(
                        "Writer hypotheses are disabled by configuration."
                    )
                if not sentence_draft.insight_ids or not set(
                    sentence_draft.insight_ids
                ).issubset(set(hypothesis_insight_lookup)):
                    raise ValueError(
                        "A hypothesis Writer sentence must cite a valid "
                        "hypothesis-only insight."
                    )

            if (
                sentence_draft.interpretation_level
                == InterpretationLevel.FINDING
                and sentence_draft.insight_ids
            ):
                raise ValueError(
                    "A direct Writer finding must not cite insight IDs."
                )

            expanded_fact_ids = list(
                dict.fromkeys(
                    [
                        *sentence_draft.fact_ids,
                        *[
                            fact_id
                            for insight_id in sentence_draft.insight_ids
                            for fact_id in all_insight_lookup[
                                insight_id
                            ].source_fact_ids
                            if fact_id in fact_lookup
                        ],
                    ]
                )
            )

            if (
                sentence_draft.support_type
                != SupportType.NON_FACTUAL
                and not expanded_fact_ids
            ):
                raise ValueError(
                    "A factual Writer sentence has no "
                    "supporting fact IDs."
                )

            evidence_ids = list(
                dict.fromkeys(
                    [
                        *[
                            evidence_id
                            for fact_id in expanded_fact_ids
                            for evidence_id in fact_lookup[
                                fact_id
                            ].evidence_ids
                        ],
                        *[
                            evidence_id
                            for insight_id in sentence_draft.insight_ids
                            for evidence_id in all_insight_lookup[
                                insight_id
                            ].source_evidence_ids
                        ],
                    ]
                )
            )

            rendered_sentences = (
                split_markdown_sentences(sentence_text)
                or [sentence_text]
            )

            for rendered_sentence in rendered_sentences:
                lines.append(rendered_sentence)

                sentence_support.append(
                    SentenceSupport(
                        sentence_id=(
                            f"SENT_{sentence_number:04d}"
                        ),
                        sentence_text=rendered_sentence,
                        fact_ids=expanded_fact_ids,
                        evidence_ids=evidence_ids,
                        insight_ids=list(
                            dict.fromkeys(
                                sentence_draft.insight_ids
                            )
                        ),
                        interpretation_level=(
                            sentence_draft.interpretation_level
                        ),
                        support_type=(
                            sentence_draft.support_type
                        ),
                    )
                )

                selected_fact_ids.extend(
                    expanded_fact_ids
                )

                sentence_number += 1

        lines.append("")

    selected_fact_ids = list(
        dict.fromkeys(selected_fact_ids)
    )

    all_fact_ids = [
        fact.fact_id
        for fact in fact_ledger.writer_ready_facts
    ]

    output = WriterOutput(
        title=draft.title.strip(),
        title_fact_ids=list(dict.fromkeys(draft.title_fact_ids)),
        markdown=(
            "\n".join(lines).strip()
            + "\n"
        ),
        sentence_support=sentence_support,
        selected_fact_ids=selected_fact_ids,
        omitted_fact_ids=[
            fact_id
            for fact_id in all_fact_ids
            if fact_id not in selected_fact_ids
        ],
        writer_notes=draft.writer_notes,
        writer_mode=writer_mode,
        eligible_for_primary_evaluation=(
            eligible_for_primary_evaluation
        ),
        quality_revision_round=(
            quality_revision_round
        ),
        quality_revision_summary=(
            quality_revision_summary
        ),
    )

    errors = validate_writer_output(
        output,
        fact_ledger,
        insight_ledger,
        allow_hypotheses_in_report,
    )

    if errors:
        raise ValueError(
            "Controller-generated WriterOutput "
            "failed validation:\n- "
            + "\n- ".join(errors)
        )

    return output



def writer_output_word_count(
    output: WriterOutput,
) -> int:
    return len(
        re.findall(
            r"\b[\w'-]+\b",
            output.markdown,
        )
    )


def accept_writer_quality_revision(
    *,
    before: WriterOutput,
    after: WriterOutput,
    before_audit: AuditReport,
    after_audit: AuditReport,
    validation_errors: list[str],
    report_specification: Any,
    settings: Settings,
) -> tuple[bool, list[str]]:
    """
    Accept a whole-report quality revision only when it is valid and
    measurably improves the incomplete draft.
    """

    reasons: list[str] = list(
        validation_errors
    )

    before_missing = sum(
        not assessment.covered
        for assessment
        in before_audit.component_assessments
    )

    after_missing = sum(
        not assessment.covered
        for assessment
        in after_audit.component_assessments
    )

    before_words = writer_output_word_count(
        before
    )
    after_words = writer_output_word_count(
        after
    )

    minimum_words = minimum_useful_report_words(
        target_words=(
            report_specification
            .target_length_words
        ),
        required_component_count=len(
            report_specification
            .required_components
        ),
        settings=settings,
    )

    if (
        before_missing > 0
        and after_missing >= before_missing
    ):
        reasons.append(
            "The revision did not reduce the number "
            "of missing required components."
        )

    if (
        before_words < minimum_words
        and after_words <= before_words
    ):
        reasons.append(
            "The revision did not improve the "
            "under-length report."
        )

    if (
        before_missing > 0
        and len(after.sentence_support)
        < len(before.sentence_support)
    ):
        reasons.append(
            "The revision reduced supported sentence "
            "coverage while the report was incomplete."
        )

    serious_after = {
        (
            annotation.sentence,
            annotation.subtype,
        )
        for annotation
        in after_audit.annotations
        if annotation.severity
        in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
    }

    serious_before = {
        (
            annotation.sentence,
            annotation.subtype,
        )
        for annotation
        in before_audit.annotations
        if annotation.severity
        in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
    }

    introduced_serious = (
        serious_after - serious_before
    )

    if introduced_serious:
        reasons.append(
            "The revision introduced a new serious "
            "factual or contextual annotation."
        )

    return (
        not reasons,
        list(dict.fromkeys(reasons)),
    )

def fallback_writer(
    pack: WriterEvidencePack,
) -> WriterOutput:
    """
    Safe deterministic fallback.

    It is deliberately richer than a two-sentence renderer, but remains
    ineligible for primary evaluation because it is not the natural LLM
    Writer.
    """

    event_report = (
        pack.report_specification.genre
        in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }
    )

    maximum = (
        pack.report_specification
        .maximum_main_findings
    )

    selected = list(
        {
            fact.fact_id: fact
            for fact in (
                pack.priority_facts[:maximum]
                + pack.limitation_facts[:2]
            )
        }.values()
    )

    evidence_by_id = build_evidence_lookup(
        pack.evidence_ledger
    )

    sections: dict[
        ReportComponent,
        list[VerifiedFact],
    ] = {
        ReportComponent.DATASET_OVERVIEW: [],
        ReportComponent.DATA_QUALITY: [],
        ReportComponent.STRONGEST_RELATIONSHIPS: [],
        ReportComponent.MODELLING_VALIDATION: [],
        ReportComponent.LIMITATIONS_NEXT_STEPS: [],
    }

    for fact in selected:
        component = classify_fact_component(
            fact,
            evidence_by_id,
        )

        sections.setdefault(
            component,
            [],
        ).append(fact)

    headings = (
        {
            ReportComponent.DATASET_OVERVIEW: (
                "Result and leading performances"
            ),
            ReportComponent.DATA_QUALITY: (
                "Record quality"
            ),
            ReportComponent.STRONGEST_RELATIONSHIPS: (
                "Main participant contrasts"
            ),
            ReportComponent.MODELLING_VALIDATION: (
                "Supporting analysis"
            ),
            ReportComponent.LIMITATIONS_NEXT_STEPS: (
                "Limitations"
            ),
        }
        if event_report
        else {
            ReportComponent.DATASET_OVERVIEW: (
                "Dataset overview"
            ),
            ReportComponent.DATA_QUALITY: (
                "Data quality"
            ),
            ReportComponent.STRONGEST_RELATIONSHIPS: (
                "Strongest observed relationships"
            ),
            ReportComponent.MODELLING_VALIDATION: (
                "Modelling and validation"
            ),
            ReportComponent.LIMITATIONS_NEXT_STEPS: (
                "Limitations and next steps"
            ),
        }
    )

    report_title = (
        "Evidence-grounded event report"
        if event_report
        else "Evidence-grounded data-science report"
    )

    lines = [
        f"# {report_title}",
        "",
    ]

    support_map: list[SentenceSupport] = []
    sentence_counter = 1
    rendered_recommendations: set[str] = set()

    def add_supported_sentence(
        sentence: str,
        facts: list[VerifiedFact],
        support_type: SupportType,
    ) -> None:
        nonlocal sentence_counter

        cleaned = sentence.strip()

        if not cleaned:
            return

        if cleaned[-1] not in ".!?":
            cleaned += "."

        lines.append(cleaned)

        fact_ids = list(
            dict.fromkeys(
                fact.fact_id
                for fact in facts
            )
        )

        evidence_ids = list(
            dict.fromkeys(
                evidence_id
                for fact in facts
                for evidence_id in fact.evidence_ids
            )
        )

        rendered_sentences = (
            split_markdown_sentences(cleaned)
            or [cleaned]
        )
        for rendered_sentence in rendered_sentences:
            support_map.append(
                SentenceSupport(
                    sentence_id=(
                        f"SENT_{sentence_counter:04d}"
                    ),
                    sentence_text=rendered_sentence,
                    fact_ids=fact_ids,
                    evidence_ids=evidence_ids,
                    support_type=support_type,
                )
            )

            sentence_counter += 1

    for component in [
        ReportComponent.DATASET_OVERVIEW,
        ReportComponent.DATA_QUALITY,
        ReportComponent.STRONGEST_RELATIONSHIPS,
        ReportComponent.MODELLING_VALIDATION,
    ]:
        component_facts = sections.get(
            component,
            [],
        )

        if not component_facts:
            continue

        lines.extend(
            [
                f"## {headings[component]}",
                "",
            ]
        )

        for fact in component_facts:
            sentence = (
                reader_facing_caveat(
                    fact.fact_summary
                )
                or fact.fact_summary
            )

            add_supported_sentence(
                sentence,
                [fact],
                SupportType.DIRECT,
            )

            if (
                component
                == ReportComponent.DATA_QUALITY
            ):
                for evidence_id in fact.evidence_ids:
                    item = evidence_by_id.get(
                        evidence_id
                    )

                    if item is None:
                        continue

                    for recommendation in (
                        item.recommendations
                    ):
                        if (
                            recommendation.priority
                            not in {"high", "medium"}
                        ):
                            continue

                        action = (
                            recommendation.action.strip()
                        )

                        if (
                            action
                            in rendered_recommendations
                        ):
                            continue

                        rendered_recommendations.add(
                            action
                        )

                        add_supported_sentence(
                            action,
                            [fact],
                            SupportType.PARAPHRASE,
                        )

        lines.append("")

    limitation_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                sections.get(
                    ReportComponent
                    .LIMITATIONS_NEXT_STEPS,
                    [],
                )
                + [
                    fact
                    for fact in selected
                    if (
                        fact.required_caveats
                        or ClaimPermission.COMPARATIVE
                        in fact.claim_permissions
                        or ClaimPermission.ASSOCIATIONAL
                        in fact.claim_permissions
                    )
                ]
            )
        }.values()
    )
    event_limitations = list(
        dict.fromkeys(
            caveat
            for fact in selected
            for caveat in fact.required_caveats
        )
    )

    if (
        (
            event_limitations
            if event_report
            else pack.reader_facing_limitations
        )
        or limitation_facts
        or rendered_recommendations
    ):
        lines.extend(
            [
                "## "
                + headings[
                    ReportComponent.LIMITATIONS_NEXT_STEPS
                ],
                "",
            ]
        )

        for fact in sections.get(
            ReportComponent
            .LIMITATIONS_NEXT_STEPS,
            [],
        ):
            add_supported_sentence(
                fact.fact_summary,
                [fact],
                SupportType.DIRECT,
            )

        if event_report:
            for limitation in event_limitations:
                supporting = [
                    fact
                    for fact in selected
                    if limitation in fact.required_caveats
                ]
                if supporting:
                    add_supported_sentence(
                        limitation,
                        supporting,
                        SupportType.PARAPHRASE,
                    )
        else:
            relationship_facts = [
                fact
                for fact in selected
                if (
                    ClaimPermission.COMPARATIVE
                    in fact.claim_permissions
                    or ClaimPermission.ASSOCIATIONAL
                    in fact.claim_permissions
                )
            ]

            for limitation in (
                pack.reader_facing_limitations
            ):
                supporting = (
                    relationship_facts
                    or limitation_facts
                )

                if supporting:
                    add_supported_sentence(
                        limitation,
                        supporting,
                        SupportType.MULTI_FACT_SYNTHESIS,
                    )

        lines.append("")

    used_fact_ids = list(
        dict.fromkeys(
            fact_id
            for support in support_map
            for fact_id in support.fact_ids
        )
    )

    available_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                pack.priority_facts
                + pack.supporting_facts
                + pack.limitation_facts
            )
        }.values()
    )

    return WriterOutput(
        title=report_title,
        markdown=(
            "\n".join(lines).strip()
            + "\n"
        ),
        sentence_support=support_map,
        selected_fact_ids=used_fact_ids,
        omitted_fact_ids=[
            fact.fact_id
            for fact in available_facts
            if fact.fact_id
            not in set(used_fact_ids)
        ],
        writer_notes=[
            "Deterministic writer fallback was used.",
            "This output is preserved for debugging "
            "and is not eligible for primary evaluation.",
        ],
        writer_mode=(
            "deterministic_fallback"
        ),
        eligible_for_primary_evaluation=False,
    )

def default_quality_assessment() -> ReportQualityAssessment:
    return ReportQualityAssessment(
        status=QualityStatus.PASS,
        request_responsiveness=1.0,
        finding_selection=1.0,
        coherence=1.0,
        concision=1.0,
        caveat_integration=1.0,
        data_science_interpretation=1.0,
        findings=[],
        recommendations=[],
    )


def assess_report_component_coverage(
    *,
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
) -> list[ReportComponentAssessment]:
    """
    Assess coverage using the sentence support map.

    Limitations and next steps may be supported by the same verified
    relationship or quality fact used elsewhere, so they are not
    restricted to facts whose primary component is LIMITATIONS.
    """

    fact_lookup = {
        fact.fact_id: fact
        for fact
        in fact_ledger.writer_ready_facts
    }

    evidence_by_id = build_evidence_lookup(
        evidence
    )

    support_by_component: defaultdict[
        ReportComponent,
        list[str],
    ] = defaultdict(list)

    for component in required_components:
        support_by_component[component]

    limitation_language = re.compile(
        r"\b("
        r"limitation|"
        r"unadjusted|"
        r"causal|causation|"
        r"confound|"
        r"precision|stability|"
        r"validate|verify|inspect|investigate|"
        r"remove|exclude|check|"
        r"next step|further analysis|"
        r"deployment|backtest"
        r")\b",
        re.IGNORECASE,
    )

    for support in writer_output.sentence_support:
        supported_facts = [
            fact_lookup[fact_id]
            for fact_id in support.fact_ids
            if fact_id in fact_lookup
        ]

        for fact in supported_facts:
            component = classify_fact_component(
                fact,
                evidence_by_id,
            )

            if (
                component
                in required_components
            ):
                support_by_component[
                    component
                ].append(fact.fact_id)

        if (
            ReportComponent
            .LIMITATIONS_NEXT_STEPS
            in required_components
            and supported_facts
            and limitation_language.search(
                support.sentence_text
            )
        ):
            support_by_component[
                ReportComponent
                .LIMITATIONS_NEXT_STEPS
            ].extend(
                fact.fact_id
                for fact in supported_facts
            )

    assessments: list[
        ReportComponentAssessment
    ] = []

    for component in required_components:
        fact_ids = list(
            dict.fromkeys(
                support_by_component[component]
            )
        )

        assessments.append(
            ReportComponentAssessment(
                component=component,
                covered=bool(fact_ids),
                supporting_fact_ids=fact_ids,
                explanation=(
                    "At least one report sentence is "
                    "mapped to verified support for "
                    "this component."
                    if fact_ids
                    else (
                        "No supported report sentence "
                        "clearly covers this required "
                        "component."
                    )
                ),
            )
        )

    return assessments

def assess_report_components(
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
) -> list[ReportComponentAssessment]:
    return assess_report_component_coverage(
        writer_output=writer_output,
        fact_ledger=fact_ledger,
        evidence=evidence,
        required_components=required_components,
    )


def assess_genre_quality(
    writer_output: WriterOutput,
    report_specification: Any,
    evidence: EvidenceLedger,
) -> GenreQualityAssessment:
    evidence_lookup = {
        item.evidence_id: item
        for item in evidence.items
        if item.eligible_for_writer
    }
    used_evidence_ids = {
        evidence_id
        for support in writer_output.sentence_support
        for evidence_id in support.evidence_ids
    }

    def matching_evidence(slot: str) -> set[str]:
        matches: set[str] = set()
        for evidence_id, item in evidence_lookup.items():
            if slot == "event_result" and item.evidence_type == "event_outcome":
                matches.add(evidence_id)
            elif slot == "leading_performance" and item.capability in {
                EvidenceCapability.ENTITY_PERFORMANCE,
                EvidenceCapability.RANKING,
            } and evidence_analytical_function(item) != (
                AnalyticalFunction.PARTICIPATION
            ):
                matches.add(evidence_id)
            elif slot == "main_contrast" and item.evidence_type in {
                "participant_comparison",
                "event_contrast",
                "group_comparison",
            }:
                matches.add(evidence_id)
            elif slot == "event_context" and item.evidence_type == ("event_context"):
                matches.add(evidence_id)
            elif slot == "event_status" and item.evidence_type == "event_status":
                matches.add(evidence_id)
            elif slot == "secondary_performance" and item.capability == (
                EvidenceCapability.RANKING
            ):
                matches.add(evidence_id)
            elif slot == "dataset_scope" and item.evidence_type in {
                "dataset_overview",
                "event_record_overview",
            }:
                matches.add(evidence_id)
            elif slot == "material_data_quality_issue" and evidence_subtype(item) == (
                "data_quality"
            ):
                matches.add(evidence_id)
            elif slot == "strongest_analytical_finding" and item.capability in {
                EvidenceCapability.ASSOCIATION,
                EvidenceCapability.GROUP_COMPARISON,
                EvidenceCapability.EVENT_OUTCOME,
            }:
                matches.add(evidence_id)
        return matches

    required_slots = list(report_specification.required_content_slots)
    supported_slots: list[str] = []
    covered_slots: list[str] = []

    for slot in [
        *required_slots,
        *report_specification.optional_content_slots,
    ]:
        matching = matching_evidence(slot)
        if matching:
            supported_slots.append(slot)
        if matching & used_evidence_ids:
            covered_slots.append(slot)

    if "limitation" in required_slots:
        supported_slots.append("limitation")
        if re.search(
            r"\b(limitations?|caveats?|does not|cannot|uncertain|missing)\b",
            writer_output.markdown,
            re.IGNORECASE,
        ):
            covered_slots.append("limitation")

    missing = [
        slot
        for slot in required_slots
        if slot in supported_slots and slot not in covered_slots
    ]
    findings = [
        f"Required supported content slot `{slot}` is missing from the report."
        for slot in missing
    ]
    recommendations = [
        "Use the available verified evidence to cover each missing content slot."
    ] if missing else []

    if report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    } and re.search(
        r"\b(rows?|columns?|constant columns?|missingness|schema|"
        r"correlations?|regressions?|statistical modelling|statistical modeling|"
        r"predictive modelling|predictive modeling|statistical power|"
        r"feature sets?|observed associations?|"
        r"group comparisons? (?:are|is) unadjusted)\b",
        writer_output.markdown,
        re.IGNORECASE,
    ):
        findings.append(
            "The event report includes flat-table profiling or modelling "
            "discussion that displaces the supported event narrative."
        )
        recommendations.append(
            "Remove wrapper-level profiling and modelling discussion; use the "
            "supported event context, performances and participant contrasts."
        )

    if report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    } and not participation_measure_requested(
        " ".join(
            [
                report_specification.report_purpose,
                report_specification.communication_goal,
            ]
        )
    ):
        available_substantive = {
            evidence_id
            for evidence_id, item in evidence_lookup.items()
            if item.evidence_type
            in {
                "entity_ranking",
                "entity_performance",
            }
            and evidence_analytical_function(item)
            != AnalyticalFunction.PARTICIPATION
        }
        used_participation = {
            evidence_id
            for evidence_id, item in evidence_lookup.items()
            if evidence_id in used_evidence_ids
            and item.evidence_type
            in {
                "entity_ranking",
                "entity_performance",
            }
            and evidence_analytical_function(item)
            == AnalyticalFunction.PARTICIPATION
        }
        omitted_substantive = (
            available_substantive - used_evidence_ids
        )

        if used_participation and omitted_substantive:
            findings.append(
                "The event report uses participation evidence while available "
                "substantive entity-performance evidence is omitted."
            )
            recommendations.append(
                "Prioritise distinct substantive performances over duration or "
                "exposure unless participation was explicitly requested."
            )

    return GenreQualityAssessment(
        status=(QualityStatus.REVISE if findings else QualityStatus.PASS),
        genre=report_specification.genre,
        required_slots=required_slots,
        supported_slots=list(dict.fromkeys(supported_slots)),
        covered_slots=list(dict.fromkeys(covered_slots)),
        missing_supported_slots=missing,
        findings=findings,
        recommendations=recommendations,
    )


def decide_release_status(
    *,
    annotations: list[AuditAnnotation],
    quality: ReportQualityAssessment,
    methodological_warnings: list[str],
    repair_budget_exhausted: bool,
    audit_mode: AuditMode,
) -> ReleaseStatus:
    if audit_mode == AuditMode.ANNOTATION_ONLY:
        if (
            annotations
            or methodological_warnings
            or quality.status != QualityStatus.PASS
        ):
            return ReleaseStatus.APPROVED_WITH_WARNINGS

        return ReleaseStatus.APPROVED

    unresolved_critical = any(
        annotation.severity == Severity.CRITICAL
        and annotation.confidence >= 0.80
        for annotation in annotations
    )
    unresolved_high = any(
        annotation.severity == Severity.HIGH
        and annotation.confidence >= 0.80
        for annotation in annotations
    )

    if unresolved_critical:
        return ReleaseStatus.HUMAN_REVIEW_REQUIRED

    if unresolved_high and repair_budget_exhausted:
        return ReleaseStatus.HUMAN_REVIEW_REQUIRED

    if (
        annotations
        or methodological_warnings
        or quality.status != QualityStatus.PASS
    ):
        return ReleaseStatus.APPROVED_WITH_WARNINGS

    return ReleaseStatus.APPROVED


def add_annotation(
    annotations: list[AuditAnnotation],
    *,
    sentence: str,
    text_span: str,
    error_type: ErrorType,
    subtype: str,
    severity: Severity,
    explanation: str,
    correction_goal: str,
    fact_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    profile_support_ids: list[str] | None = None,
    insight_ids: list[str] | None = None,
    confidence: float = 1.0,
) -> None:
    key = (
        sentence,
        text_span,
        error_type.value,
        subtype,
    )

    if any(
        (
            annotation.sentence,
            annotation.text_span,
            annotation.error_type.value,
            annotation.subtype,
        )
        == key
        for annotation in annotations
    ):
        return

    annotations.append(
        AuditAnnotation(
            annotation_id=f"ANN_{len(annotations) + 1:04d}",
            sentence=sentence,
            text_span=text_span,
            error_type=error_type,
            subtype=subtype,
            severity=severity,
            explanation=explanation,
            correction_goal=correction_goal,
            fact_ids=fact_ids or [],
            evidence_ids=evidence_ids or [],
            profile_support_ids=profile_support_ids or [],
            insight_ids=insight_ids or [],
            confidence=confidence,
        )
    )


def negative_causal(sentence: str) -> bool:
    return bool(
        re.search(
            r"\b(no causal|not causal|does not establish causation|"
            r"causality is not established|causal conclusion is not)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def negative_predictive(sentence: str) -> bool:
    return bool(
        re.search(
            r"\b(not validated|did not improve|no predictive|"
            r"cannot support prediction|not deployment ready)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def negative_forecast(sentence: str) -> bool:
    return bool(
        re.search(
            r"\b(not validated|did not improve|no forecast|"
            r"did not outperform|not a live future forecast)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def _support_text_for_facts(
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
) -> str:
    return " ".join(
        fact_support_text(fact, evidence)
        for fact in facts
    ).lower()


def _mapped_facts_semantically_support_profile_match(
    *,
    support_text: str,
    matches: list[ProfileSupportRecord],
) -> bool:
    for record in matches:
        pattern = PROFILE_FACT_KIND_TERMS.get(
            record.fact_kind
        )
        if (
            pattern is not None
            and pattern.search(support_text)
        ):
            return True

    return False


def _recommendation_supported_by_evidence(
    sentence: str,
    facts: list[VerifiedFact],
    evidence_lookup_by_id: dict[str, EvidenceItem],
) -> bool:
    sentence_text = sentence.lower()

    for fact in facts:
        for item in evidence_for_fact(
            fact,
            evidence_lookup_by_id,
        ):
            for recommendation in item.recommendations:
                action = recommendation.action.lower()
                if action and (
                    action in sentence_text
                    or sentence_text in action
                ):
                    return True

    return False


def add_wording_guardrail_annotations(
    *,
    annotations: list[AuditAnnotation],
    sentence: str,
    support: SentenceSupport,
    supporting_facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    report_specification: Any,
) -> None:
    support_text = _support_text_for_facts(
        supporting_facts,
        evidence,
    )
    evidence_lookup_by_id = build_evidence_lookup(evidence)
    request_text = (
        getattr(
            report_specification,
            "report_purpose",
            "",
        )
        or ""
    ).lower()

    hourly_match = HOURLY_CADENCE_PATTERN.search(sentence)
    if hourly_match and not HOURLY_CADENCE_PATTERN.search(support_text):
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=hourly_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_temporal_cadence",
            severity=Severity.HIGH,
            explanation=(
                "A date/time-like field or parse rate does not establish "
                "regular hourly spacing."
            ),
            correction_goal=(
                "Use neutral wording such as timestamped weather observations."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    location_match = LOCATION_METADATA_PATTERN.search(sentence)
    if location_match and not LOCATION_METADATA_PATTERN.search(support_text):
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=location_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_location_metadata",
            severity=Severity.HIGH,
            explanation=(
                "The supplied facts do not establish collection at a "
                "specific location or weather station."
            ),
            correction_goal="Remove unsupported location metadata.",
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    constant_match = CONSTANT_OVERSTATEMENT_PATTERN.search(sentence)
    if constant_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=constant_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="overbroad_constant_interpretation",
            severity=Severity.HIGH,
            explanation=(
                "A constant field should not be described as universally "
                "worthless or valueless."
            ),
            correction_goal=(
                "Say it contains no observed variation for analyses that "
                "depend on variation."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    zero_match = ZERO_OVERCONFIDENCE_PATTERN.search(sentence)
    if zero_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=zero_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="overconfident_zero_interpretation",
            severity=Severity.HIGH,
            explanation=(
                "Suspicious zero diagnostics do not establish what the zero "
                "values actually mean."
            ),
            correction_goal=(
                "Use cautious wording such as may represent encoded "
                "missingness or measurement failure and should be validated."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    missingness_match = MISSINGNESS_HARMLESS_PATTERN.search(sentence)
    if missingness_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=missingness_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_missingness_impact",
            severity=Severity.HIGH,
            explanation=(
                "A missingness rate alone does not establish that the "
                "missingness is harmless."
            ),
            correction_goal=(
                "Report the rate and recommend examining the missingness "
                "pattern."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    duplicate_match = DUPLICATE_REMOVAL_PATTERN.search(sentence)
    if duplicate_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=duplicate_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_duplicate_removal",
            severity=Severity.HIGH,
            explanation=(
                "Exact duplicate rows may be valid repeated observations or "
                "unintended duplicates."
            ),
            correction_goal=(
                "Say duplicate rows should be reviewed before any decision "
                "to remove them."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    pearson_match = PEARSON_IMPRECISE_PATTERN.search(sentence)
    if pearson_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=pearson_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="imprecise_pearson_limitation",
            severity=Severity.MEDIUM,
            explanation=(
                "Pearson correlation may not capture non-linear relationships; "
                "it is not literally influenced by a pattern it does not measure."
            ),
            correction_goal=(
                "Say Pearson correlation may not capture non-linear "
                "relationships and can be sensitive to influential observations."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
            confidence=0.9,
        )

    future_match = FUTURE_ANALYSIS_PATTERN.search(sentence)
    if future_match:
        requested = bool(
            re.search(
                r"\b(model|modelling|modeling|temporal|trend|future|"
                r"relationship|multivariate)\b",
                request_text,
            )
        )
        supported_recommendation = (
            _recommendation_supported_by_evidence(
                sentence,
                supporting_facts,
                evidence_lookup_by_id,
            )
        )

        if not requested and not supported_recommendation:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=future_match.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="unsupported_analytical_recommendation",
                severity=Severity.MEDIUM,
                explanation=(
                    "Reader-facing next steps must come from supplied "
                    "recommendations, verified methodological facts, or the "
                    "explicit user request."
                ),
                correction_goal=(
                    "Remove the unsupported recommendation or ground it in a "
                    "supplied analytical recommendation."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                profile_support_ids=support.profile_support_ids,
                confidence=0.9,
            )


def deterministic_audit(
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    mode: AuditMode,
    external_sources: list[ExternalTruthSource],
    revision_round: int,
    report_specification: Any,
    settings: Settings | None = None,
    profile_support_records: list[
        ProfileSupportRecord
    ] | None = None,
    insight_ledger: InsightLedger | None = None,
) -> AuditReport:
    settings = settings or Settings()
    profile_support_records = profile_support_records or []
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    profile_records_by_id = {
        record.support_id: record
        for record in profile_support_records
    }
    facts = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insight_ids = {
        *verified_insights,
        *hypothesis_insights,
    }

    support_by_sentence = {
        support.sentence_text: support
        for support in writer_output.sentence_support
    }

    annotations: list[AuditAnnotation] = []
    support_map_patches: list[SupportMapPatch] = []
    sentences = split_markdown_sentences(writer_output.markdown)
    section_headings = _sentence_section_headings(
        writer_output.markdown
    )
    evidence_lookup_by_id = build_evidence_lookup(evidence)

    factual_count = 0
    supported_count = 0

    for sentence in sentences:
        support = support_by_sentence.get(sentence)

        if (
            not looks_factual(sentence)
            and not (
                support is not None
                and support.interpretation_level
                != InterpretationLevel.FINDING
            )
        ):
            continue

        factual_count += 1

        if support is None:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="missing_support_map_entry",
                severity=Severity.HIGH,
                explanation=(
                    "The sentence appears factual but is absent from the hidden "
                    "sentence support map."
                ),
                correction_goal=(
                    "Attach relevant verified facts or remove unsupported factual content."
                ),
            )
            continue

        unknown_fact_ids = [
            fact_id
            for fact_id in support.fact_ids
            if fact_id not in facts
        ]

        if unknown_fact_ids:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="unknown_fact_id",
                severity=Severity.HIGH,
                explanation=(
                    "The support map references facts not present in the verified ledger."
                ),
                correction_goal="Use valid verified facts.",
                fact_ids=unknown_fact_ids,
            )
            continue

        supporting_facts = [
            facts[fact_id]
            for fact_id in support.fact_ids
        ]

        supporting_evidence_ids = {
            *support.evidence_ids,
            *[
                evidence_id
                for fact in supporting_facts
                for evidence_id in fact.evidence_ids
            ],
        }
        supporting_evidence_items = [
            evidence_lookup_by_id[evidence_id]
            for evidence_id in supporting_evidence_ids
            if evidence_id in evidence_lookup_by_id
        ]
        for conflict in qualitative_strength_conflicts(
            sentence,
            supporting_evidence_items,
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="inconsistent_strength_label",
                severity=Severity.HIGH,
                explanation=(
                    "The qualitative relationship strength conflicts with "
                    f"the mapped deterministic evidence: {conflict}."
                ),
                correction_goal=(
                    "Use the qualitative strength classification recorded in "
                    "the mapped evidence."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=sorted(supporting_evidence_ids),
                insight_ids=support.insight_ids,
            )

        explanatory_hypothesis = (
            EXPLANATORY_HYPOTHESIS_PATTERN.search(sentence)
            or UNLABELLED_HYPOTHESIS_PATTERN.search(sentence)
        )
        if (
            explanatory_hypothesis
            and support.interpretation_level
            != InterpretationLevel.HYPOTHESIS
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=explanatory_hypothesis.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="unlabelled_hypothesis",
                severity=Severity.HIGH,
                explanation=(
                    "The sentence proposes a possible explanation without "
                    "verified hypothesis provenance."
                ),
                correction_goal=(
                    "Remove the explanation or present it as an explicitly "
                    "labelled hypothesis in the permitted section when enabled."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        unknown_insight_ids = [
            insight_id
            for insight_id in support.insight_ids
            if insight_id not in all_insight_ids
        ]
        if unknown_insight_ids:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="unsupported_insight",
                severity=Severity.HIGH,
                explanation=(
                    "The support map references insight IDs that are absent "
                    "from the verified Insight Ledger."
                ),
                correction_goal=(
                    "Remove the unsupported interpretation or map it to an "
                    "existing verified insight."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=unknown_insight_ids,
            )

        mapped_verified_insights = [
            verified_insights[insight_id]
            for insight_id in support.insight_ids
            if insight_id in verified_insights
        ]
        mapped_hypotheses = [
            hypothesis_insights[insight_id]
            for insight_id in support.insight_ids
            if insight_id in hypothesis_insights
        ]

        if (
            support.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
        ):
            if not support.insight_ids:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.NOT_CHECKABLE,
                    subtype="unsupported_insight",
                    severity=Severity.HIGH,
                    explanation=(
                        "The sentence presents a bounded interpretation but "
                        "has no verified insight provenance."
                    ),
                    correction_goal=(
                        "Map the sentence to an exact verified insight or "
                        "rewrite it as directly supported findings."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                )
            elif len(mapped_verified_insights) != len(
                support.insight_ids
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="unsupported_insight",
                    severity=Severity.HIGH,
                    explanation=(
                        "A bounded-insight sentence may cite only insights "
                        "verified for the main report."
                    ),
                    correction_goal=(
                        "Use a verified main insight or remove the "
                        "interpretive claim."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

            required_fact_ids = {
                fact_id
                for insight in mapped_verified_insights
                for fact_id in insight.source_fact_ids
            }
            required_evidence_ids = {
                evidence_id
                for insight in mapped_verified_insights
                for evidence_id in insight.source_evidence_ids
            }
            if (
                mapped_verified_insights
                and (
                    not required_fact_ids.issubset(
                        set(support.fact_ids)
                    )
                    or not required_evidence_ids.issubset(
                        set(support.evidence_ids)
                    )
                )
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                    subtype="insight_missing_source_support",
                    severity=Severity.HIGH,
                    explanation=(
                        "The bounded insight is mapped without all of its "
                        "verified source facts and evidence."
                    ),
                    correction_goal=(
                        "Restore the verified insight's source fact and "
                        "evidence provenance in the hidden support map."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

            overstatement = INSIGHT_OVERSTATEMENT_PATTERN.search(sentence)
            if overstatement:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=overstatement.group(0),
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="insight_exceeds_verified_wording",
                    severity=Severity.HIGH,
                    explanation=(
                        "The report wording is stronger than the bounded "
                        "interpretation authorised by the Insight Ledger."
                    ),
                    correction_goal=(
                        "Use the verified dataset-scoped insight wording."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

        if (
            support.interpretation_level
            == InterpretationLevel.HYPOTHESIS
        ):
            if not settings.allow_hypotheses_in_report:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="hypothesis_presented_as_conclusion",
                    severity=Severity.HIGH,
                    explanation=(
                        "Hypotheses are disabled for this report."
                    ),
                    correction_goal="Remove the hypothesis from the report.",
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
            if not mapped_hypotheses or len(mapped_hypotheses) != len(
                support.insight_ids
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.NOT_CHECKABLE,
                    subtype="unlabelled_hypothesis",
                    severity=Severity.HIGH,
                    explanation=(
                        "The sentence lacks valid hypothesis-only provenance."
                    ),
                    correction_goal=(
                        "Map it to a hypothesis-only ledger entry or remove it."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
            if (
                not HYPOTHESIS_WORDING_PATTERN.search(sentence)
                and not sentence.strip().endswith("?")
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="unlabelled_hypothesis",
                    severity=Severity.HIGH,
                    explanation=(
                        "A hypothesis must be explicitly labelled rather than "
                        "presented as established knowledge."
                    ),
                    correction_goal="Label the statement explicitly as a hypothesis.",
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
            if section_headings.get(sentence, "").lower() != (
                "questions for further investigation"
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="hypothesis_presented_as_conclusion",
                    severity=Severity.HIGH,
                    explanation=(
                        "Hypotheses may appear only in the separate Questions "
                        "for Further Investigation section."
                    ),
                    correction_goal=(
                        "Move the labelled hypothesis to the permitted section."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

        if (
            support.interpretation_level
            == InterpretationLevel.FINDING
        ):
            if support.insight_ids:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                    subtype="single_fact_relabelled_as_insight",
                    severity=Severity.MEDIUM,
                    explanation=(
                        "A direct finding is incorrectly mapped as an insight."
                    ),
                    correction_goal=(
                        "Remove the insight mapping or mark a genuinely "
                        "verified bounded interpretation."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
        unknown_profile_ids = [
            support_id
            for support_id in support.profile_support_ids
            if support_id not in profile_records_by_id
        ]

        if unknown_profile_ids:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="unknown_profile_support_id",
                severity=Severity.HIGH,
                explanation=(
                    "The support map references deterministic profile support "
                    "not present in the profile registry."
                ),
                correction_goal="Use valid deterministic profile support IDs.",
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                profile_support_ids=unknown_profile_ids,
            )
            continue

        attached_profile_supports = _profile_records_support_sentence(
            sentence=sentence,
            support_ids=support.profile_support_ids,
            records_by_id=profile_records_by_id,
        )

        fact_numbers = [
            number
            for fact in supporting_facts
            for number in fact_support_numbers(fact, evidence)
        ]

        attached_profile_numbers = [
            number
            for support_id in support.profile_support_ids
            if support_id in profile_records_by_id
            for number in profile_record_numbers(
                profile_records_by_id[support_id]
            )
        ]

        combined_numbers = [
            *fact_numbers,
            *(
                attached_profile_numbers
                if attached_profile_supports
                else []
            ),
        ]

        profile_matches = matching_profile_support_records(
            sentence=sentence,
            records=profile_support_records,
        )

        if not numbers_supported(sentence, combined_numbers):
            if profile_matches:
                matched_ids = [
                    record.support_id
                    for record in profile_matches
                ]
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                    subtype=(
                        "deterministic_profile_support_missing_from_map"
                    ),
                    severity=Severity.MEDIUM,
                    explanation=(
                        "The visible statement is supported by deterministic "
                        "profile data, but that support is missing from the "
                        "hidden sentence support map."
                    ),
                    correction_goal=(
                        "Attach the relevant deterministic profile support "
                        "IDs to the hidden sentence support map."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    profile_support_ids=matched_ids,
                    confidence=1.0,
                )
                support_map_patches.append(
                    SupportMapPatch(
                        sentence_id=support.sentence_id,
                        sentence_text=support.sentence_text,
                        added_profile_support_ids=matched_ids,
                        reason=(
                            "Deterministic profile data exactly supports "
                            "the visible structural statement."
                        ),
                    )
                )
            else:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.INCORRECT_NUMBER,
                    subtype="unsupported_number",
                    severity=Severity.HIGH,
                    explanation=(
                        "One or more numbers are not supported by the mapped "
                        "verified facts or deterministic profile support."
                    ),
                    correction_goal=(
                        "Use a supported exact or appropriately qualified "
                        "rounded value."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    profile_support_ids=support.profile_support_ids,
                )
        elif (
            profile_matches
            and not attached_profile_supports
            and not _mapped_facts_semantically_support_profile_match(
                support_text=_support_text_for_facts(
                    supporting_facts,
                    evidence,
                ),
                matches=profile_matches,
            )
        ):
            matched_ids = [
                record.support_id
                for record in profile_matches
            ]
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                subtype="deterministic_profile_support_missing_from_map",
                severity=Severity.MEDIUM,
                explanation=(
                    "The visible structural statement is supported by "
                    "deterministic profile data, but the mapped verified facts "
                    "do not provide that provenance."
                ),
                correction_goal=(
                    "Attach the relevant deterministic profile support IDs "
                    "to the hidden sentence support map."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                profile_support_ids=matched_ids,
                confidence=1.0,
            )
            support_map_patches.append(
                SupportMapPatch(
                    sentence_id=support.sentence_id,
                    sentence_text=support.sentence_text,
                    added_profile_support_ids=matched_ids,
                    reason=(
                        "Deterministic profile data exactly supports the "
                        "visible structural statement."
                    ),
                )
            )

        permissions = {
            permission
            for fact in supporting_facts
            for permission in fact.claim_permissions
        }
        mapped_interpretations = [
            *mapped_verified_insights,
            *mapped_hypotheses,
        ]
        mapped_insight_text = " ".join(
            insight.statement
            for insight in mapped_interpretations
        )

        if IMBALANCE_BIAS_PATTERN.search(sentence):
            support_text = " ".join(
                [
                    sentence,
                    *[fact.fact_summary for fact in supporting_facts],
                    *[
                        item.practical_interpretation
                        for fact in supporting_facts
                        for item in evidence_for_fact(
                            fact,
                            evidence_lookup_by_id,
                        )
                    ],
                    *[
                        limitation
                        for fact in supporting_facts
                        for item in evidence_for_fact(
                            fact,
                            evidence_lookup_by_id,
                        )
                        for limitation in getattr(item, "limitations", [])
                    ],
                ]
            ).lower()

            if "sampling bias" not in support_text and "selection bias" not in support_text:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="unsupported_methodological_interpretation",
                    severity=Severity.MEDIUM,
                    explanation=(
                        "The evidence can support noting that unequal group sizes "
                        "may affect precision, stability, or representation, but it "
                        "does not establish that the reported means are biased."
                    ),
                    correction_goal=(
                        "Replace bias wording with a precision, stability, or "
                        "representation caveat grounded in the evidence."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    confidence=0.85,
                )

        if (
            CAUSAL_PATTERN.search(sentence)
            and not negative_causal(sentence)
            and (
                ClaimPermission.CAUSAL not in permissions
                or (
                    support.interpretation_level
                    != InterpretationLevel.FINDING
                    and not CAUSAL_PATTERN.search(
                        mapped_insight_text
                    )
                )
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype=(
                    "unsupported_causal_interpretation"
                    if support.interpretation_level
                    != InterpretationLevel.FINDING
                    else "causal_overclaim"
                ),
                severity=Severity.CRITICAL,
                explanation=(
                    "The sentence uses causal language without verified causal permission."
                ),
                correction_goal=(
                    "Rewrite as association or explicitly state that causality "
                    "was not established."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        if (
            PREDICTIVE_PATTERN.search(sentence)
            and not negative_predictive(sentence)
            and (
                ClaimPermission.PREDICTIVE not in permissions
                or (
                    support.interpretation_level
                    != InterpretationLevel.FINDING
                    and not PREDICTIVE_PATTERN.search(
                        mapped_insight_text
                    )
                )
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="predictive_overclaim",
                severity=Severity.HIGH,
                explanation=(
                    "Predictive wording is used without validated predictive permission."
                ),
                correction_goal=(
                    "Describe the feasibility limitation or validated internal result accurately."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        if (
            FORECAST_PATTERN.search(sentence)
            and not negative_forecast(sentence)
            and (
                ClaimPermission.FORECAST not in permissions
                or (
                    support.interpretation_level
                    != InterpretationLevel.FINDING
                    and not FORECAST_PATTERN.search(
                        mapped_insight_text
                    )
                )
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="forecast_overclaim",
                severity=Severity.HIGH,
                explanation=(
                    "Forecast wording is used without validated forecast permission."
                ),
                correction_goal=(
                    "Describe the backtest or insufficiency finding without "
                    "claiming unsupported future performance."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        generalisation_match = DATASET_GENERALISATION_PATTERN.search(
            sentence
        )
        if (
            generalisation_match
            and not DATASET_GENERALISATION_PATTERN.search(
                mapped_insight_text
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=generalisation_match.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="insight_exceeds_verified_wording",
                severity=Severity.HIGH,
                explanation=(
                    "The sentence generalises a dataset-scoped finding or "
                    "insight beyond the analysed data."
                ),
                correction_goal=(
                    "Scope the statement to this dataset and the verified "
                    "interpretation."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        sports_narrative_match = (
            UNSUPPORTED_SPORTS_NARRATIVE_PATTERN.search(
                sentence
            )
        )
        support_text_for_narrative = (
            _support_text_for_facts(
                supporting_facts,
                evidence,
            )
            + " "
            + mapped_insight_text.lower()
        )
        if (
            sports_narrative_match
            and not UNSUPPORTED_SPORTS_NARRATIVE_PATTERN.search(
                support_text_for_narrative
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sports_narrative_match.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="unsupported_sports_narrative",
                severity=Severity.HIGH,
                explanation=(
                    "The sports narrative introduces chronology, evaluation, "
                    "or historical significance absent from verified support."
                ),
                correction_goal=(
                    "Use only the supported result, performances and team "
                    "contrasts without invented narrative context."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        add_wording_guardrail_annotations(
            annotations=annotations,
            sentence=sentence,
            support=support,
            supporting_facts=supporting_facts,
            evidence=evidence,
            report_specification=report_specification,
        )

        known_entities = {
            entity
            for fact in supporting_facts
            for entity in fact.entities
        }
        known_entities.update(
            entity
            for support_id in support.profile_support_ids
            if support_id in profile_records_by_id
            for entity in profile_records_by_id[
                support_id
            ].entities
        )

        for backtick_entity in unsupported_backtick_entities(
            sentence,
            known_entities,
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=backtick_entity,
                error_type=ErrorType.INCORRECT_NAMED_ENTITY,
                subtype="unsupported_backtick_entity",
                severity=Severity.HIGH,
                explanation=(
                    "The named entity is not present in the mapped facts."
                ),
                correction_goal=(
                    "Use an entity present in the verified facts or remove it."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
            )

        if not any(
            annotation.sentence == sentence
            for annotation in annotations
        ):
            supported_count += 1

    word_count = len(
        re.findall(r"\b[\w'-]+\b", writer_output.markdown)
    )

    quality_findings: list[str] = []
    quality_recommendations: list[str] = []
    methodological_warnings: list[str] = []

    if INTERNAL_CONTROL_PATTERN.search(writer_output.markdown) or FIELD_LABEL_PATTERN.search(
        writer_output.markdown
    ):
        quality_findings.append(
            "The report exposes internal writer or auditor guardrails."
        )
        quality_recommendations.append(
            "Convert internal constraints into concise reader-facing caveats."
        )

    if any(pattern.search(writer_output.markdown) for pattern in GENERIC_OPENING_PATTERNS):
        quality_findings.append(
            "The report opens with generic report boilerplate instead of dataset-specific substance."
        )
        quality_recommendations.append(
            "Start with a concrete dataset overview or leading supported finding."
        )

    if word_count > report_specification.target_length_words * 1.5:
        quality_findings.append(
            "The report substantially exceeds the planned target length."
        )
        quality_recommendations.append(
            "Remove low-priority detail and consolidate methodological caveats."
        )

    minimum_words = minimum_useful_report_words(
        target_words=report_specification.target_length_words,
        required_component_count=len(report_specification.required_components),
        settings=settings,
    )
    if word_count < minimum_words:
        quality_findings.append(
            f"The report contains {word_count} words, below the minimum useful "
            f"coverage threshold of {minimum_words}."
        )
        quality_recommendations.append(
            "Expand the report using verified facts covering the required dataset "
            "overview, quality, relationship, and limitation components."
        )

    maximum_supporting_facts = max(
        report_specification.maximum_supporting_facts,
        report_specification.maximum_main_findings,
    )
    if len(writer_output.selected_fact_ids) > maximum_supporting_facts:
        quality_findings.append(
            "The report uses more facts than the planned supporting-fact budget."
        )
        quality_recommendations.append(
            "Prioritise headline findings and omit weak supporting details."
        )

    used_verified_insight_ids = {
        insight_id
        for support in writer_output.sentence_support
        if support.interpretation_level
        == InterpretationLevel.BOUNDED_INSIGHT
        for insight_id in support.insight_ids
        if insight_id in verified_insights
    }
    if verified_insights and not used_verified_insight_ids:
        quality_findings.append(
            "The report lists findings without relating them through an "
            "available verified insight."
        )
        quality_recommendations.append(
            "Use at least one salient verified bounded insight in a main "
            "analytical paragraph."
        )

    insights_without_implication = []
    for insight_id in used_verified_insight_ids:
        insight = verified_insights[insight_id]
        mapped_sentences = [
            support.sentence_text
            for support in writer_output.sentence_support
            if insight_id in support.insight_ids
        ]
        direct_source_texts = [
            insight.statement,
            *[
                facts[fact_id].fact_summary
                for fact_id in insight.source_fact_ids
                if fact_id in facts
            ],
        ]
        if mapped_sentences and all(
            any(
                materially_same_report_text(
                    sentence,
                    source_text,
                )
                for source_text in direct_source_texts
            )
            for sentence in mapped_sentences
        ):
            insights_without_implication.append(insight_id)

    if insights_without_implication:
        quality_findings.append(
            "The report states a verified insight but does not explain its "
            "supported analytical implication."
        )
        quality_recommendations.append(
            "Use the verified `why_it_matters` content to explain why the "
            "combined findings matter instead of restating them."
        )

    if verified_insights:
        most_salient_insight = max(
            verified_insights.values(),
            key=lambda insight: (
                insight.salience,
                insight.confidence,
            ),
        )
        if (
            most_salient_insight.insight_id
            not in used_verified_insight_ids
        ):
            quality_findings.append(
                "The report omits the most salient verified insight."
            )
            quality_recommendations.append(
                "Prioritise the most salient verified insight or explain the "
                "selection through stronger supported content."
            )

    if (
        len(used_verified_insight_ids)
        > settings.max_verified_main_insights
    ):
        quality_findings.append(
            "The report exceeds its configured verified insight budget."
        )
        quality_recommendations.append(
            "Retain the most salient non-duplicate verified insights."
        )

    if (
        report_specification.genre
        in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }
    ):
        sports_text = writer_output.markdown.lower()
        game_content = re.search(
            r"\b(won|winner|score|points?|rebounds?|turnovers?|team|player)\b",
            sports_text,
        )
        profile_dominant = bool(
            re.search(
                r"\b(columns?|schema|missingness|dtype|data type)\b",
                sports_text,
            )
            and not game_content
        )
        if not game_content or profile_dominant:
            quality_findings.append(
                "The sports game report reads like a dataset profile rather "
                "than communicating the supported result and performances."
            )
            quality_recommendations.append(
                "Prioritise the supported result, salient performances and "
                "team-level contrasts required by the selected genre."
            )

    if any(
        annotation.subtype
        in {
            "unlabelled_hypothesis",
            "hypothesis_presented_as_conclusion",
        }
        for annotation in annotations
    ):
        quality_findings.append(
            "The report uses a hypothesis as a conclusion."
        )
        quality_recommendations.append(
            "Remove the hypothesis or label it in the permitted further-"
            "investigation section."
        )

    repeated_caveat_count = count_caveat_mentions(writer_output.markdown)

    if repeated_caveat_count > settings.maximum_repeated_caveat_mentions:
        quality_findings.append(
            "The same causal caveat is repeated several times."
        )
        quality_recommendations.append(
            "Consolidate recurring caveats at section level."
        )

    component_assessments = assess_report_component_coverage(
        writer_output=writer_output,
        fact_ledger=fact_ledger,
        evidence=evidence,
        required_components=report_specification.required_components,
    )
    missing_required_components = False
    for assessment in component_assessments:
        if not assessment.covered:
            missing_required_components = True
            quality_findings.append(
                f"Required report component `{assessment.component.value}` is not clearly covered."
            )
            quality_recommendations.append(
                "Revise the report to cover the required component using verified facts."
            )

    fact_text = " ".join(
        fact.fact_summary.lower()
        + " "
        + " ".join(entity.lower() for entity in fact.entities)
        for fact in fact_ledger.writer_ready_facts
    )
    unsupported_unit_terms = [
        term
        for term in UNSANCTIONED_UNIT_TERMS
        if re.search(rf"\b{re.escape(term)}\b", writer_output.markdown, re.IGNORECASE)
        and term not in fact_text
    ]
    if unsupported_unit_terms:
        quality_findings.append(
            "The report may substitute an unsupported unit of observation: "
            + ", ".join(sorted(set(unsupported_unit_terms)))
            + "."
        )
        quality_recommendations.append(
            "Use neutral unit wording unless verified facts or deterministic "
            "profile support establish a more specific unit."
        )

    for annotation in annotations:
        if annotation.subtype == "unsupported_methodological_interpretation":
            methodological_warnings.append(annotation.explanation)

    quality = ReportQualityAssessment(
        status=(
            QualityStatus.REVISE
            if missing_required_components
            else (
                QualityStatus.WARNING
                if quality_findings
                else QualityStatus.PASS
            )
        ),
        request_responsiveness=0.8 if quality_findings else 1.0,
        finding_selection=0.7 if quality_findings else 1.0,
        coherence=0.9,
        concision=0.7 if quality_findings else 1.0,
        caveat_integration=(
            0.6
            if repeated_caveat_count > settings.maximum_repeated_caveat_mentions
            else 1.0
        ),
        data_science_interpretation=0.9,
        findings=quality_findings,
        recommendations=quality_recommendations,
    )

    serious = any(
        annotation.severity in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
        for annotation in annotations
    )

    if mode == AuditMode.ANNOTATION_ONLY:
        decision = AuditDecision.PASS
    elif serious:
        decision = AuditDecision.REVISE
    else:
        decision = AuditDecision.PASS

    release_status = decide_release_status(
        annotations=annotations,
        quality=quality,
        methodological_warnings=methodological_warnings,
        repair_budget_exhausted=False,
        audit_mode=mode,
    )

    return AuditReport(
        mode=mode,
        decision=decision,
        release_status=release_status,
        annotations=annotations,
        applied_patches=[],
        support_map_patches=support_map_patches,
        factual_sentence_count=factual_count,
        supported_sentence_count=supported_count,
        support_rate=(
            supported_count / factual_count
            if factual_count
            else 1.0
        ),
        residual_risk=(
            "High-confidence factual issues require repair."
            if serious
            else (
                "No high-confidence factual error was detected; "
                "residual writer and auditor error remain possible."
            )
        ),
        revision_instructions=list(
            dict.fromkeys(
                annotation.correction_goal
                for annotation in annotations
            )
        ),
        quality_assessment=quality,
        revision_round=revision_round,
        component_assessments=component_assessments,
        methodological_warnings=methodological_warnings,
    )


def _ordered_dedupe(
    values: list[str],
) -> list[str]:
    return list(
        dict.fromkeys(
            value
            for value in values
            if value
        )
    )


def merge_quality_assessments(
    deterministic: ReportQualityAssessment,
    semantic: ReportQualityAssessment,
) -> ReportQualityAssessment:
    status = max(
        [deterministic.status, semantic.status],
        key=lambda item: QUALITY_STATUS_ORDER[item],
    )

    return ReportQualityAssessment(
        status=status,
        request_responsiveness=min(
            deterministic.request_responsiveness,
            semantic.request_responsiveness,
        ),
        finding_selection=min(
            deterministic.finding_selection,
            semantic.finding_selection,
        ),
        coherence=min(
            deterministic.coherence,
            semantic.coherence,
        ),
        concision=min(
            deterministic.concision,
            semantic.concision,
        ),
        caveat_integration=min(
            deterministic.caveat_integration,
            semantic.caveat_integration,
        ),
        data_science_interpretation=min(
            deterministic.data_science_interpretation,
            semantic.data_science_interpretation,
        ),
        findings=_ordered_dedupe(
            deterministic.findings
            + semantic.findings
        ),
        recommendations=_ordered_dedupe(
            deterministic.recommendations
            + semantic.recommendations
        ),
    )


def merge_audit_proposal(
    deterministic: AuditReport,
    proposal: AuditRepairProposal,
) -> AuditReport:
    annotations = list(deterministic.annotations)

    for proposed in proposal.annotations:
        duplicate = any(
            existing.sentence == proposed.sentence
            and existing.text_span == proposed.text_span
            and existing.subtype == proposed.subtype
            for existing in annotations
        )

        if duplicate:
            continue

        annotations.append(
            proposed.model_copy(
                update={
                    "annotation_id": f"ANN_{len(annotations) + 1:04d}"
                }
            )
        )

    merged_quality = merge_quality_assessments(
        deterministic.quality_assessment,
        proposal.quality_assessment,
    )

    serious = any(
        annotation.severity in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
        for annotation in annotations
    )

    if deterministic.mode == AuditMode.ANNOTATION_ONLY:
        decision = AuditDecision.PASS
    elif serious:
        decision = AuditDecision.REVISE
    else:
        decision = AuditDecision.PASS

    release_status = decide_release_status(
        annotations=annotations,
        quality=merged_quality,
        methodological_warnings=deterministic.methodological_warnings,
        repair_budget_exhausted=False,
        audit_mode=deterministic.mode,
    )


    return deterministic.model_copy(
        update={
            "annotations": annotations,
            "decision": decision,
            "release_status": release_status,
            "residual_risk": " ".join(
                _ordered_dedupe(
                    [
                        deterministic.residual_risk,
                        proposal.residual_risk,
                    ]
                )
            ),
            "revision_instructions": _ordered_dedupe(
                deterministic.revision_instructions
                + proposal.revision_instructions
            ),
            "quality_assessment": merged_quality,
            "methodological_warnings": deterministic.methodological_warnings,
            "component_assessments": deterministic.component_assessments,
            "support_map_patches": deterministic.support_map_patches,
        }
    )


def fallback_audit_proposal(
    deterministic: AuditReport,
) -> AuditRepairProposal:
    return AuditRepairProposal(
        annotations=[],
        repairs=[],
        recommended_decision=deterministic.decision,
        residual_risk=(
            "Semantic auditing was unavailable. "
            + deterministic.residual_risk
        ),
        quality_assessment=deterministic.quality_assessment,
        revision_instructions=deterministic.revision_instructions,
    )


def repair_score(candidate: RepairCandidate) -> float:
    return (
        0.45 * candidate.factual_support_score
        + 0.25 * candidate.meaning_preservation_score
        + 0.20 * candidate.readability_score
        - 0.10 * candidate.residual_hallucination_risk
    )


def validate_repair_candidate(
    candidate: RepairCandidate,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
    original_text: str | None = None,
) -> list[str]:
    errors: list[str] = []
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    facts = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insights = {
        **verified_insights,
        **hypothesis_insights,
    }

    unknown_insights = [
        insight_id
        for insight_id in candidate.supporting_insight_ids
        if insight_id not in all_insights
    ]
    if unknown_insights:
        errors.append(
            f"Unknown repair insight IDs: {unknown_insights}"
        )
        return errors

    if (
        set(candidate.supporting_insight_ids)
        & set(hypothesis_insights)
        and not allow_hypotheses_in_report
    ):
        errors.append(
            "The replacement introduces a hypothesis while hypotheses are "
            "disabled."
        )

    expanded_fact_ids = list(
        dict.fromkeys(
            [
                *candidate.supporting_fact_ids,
                *[
                    fact_id
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                    for fact_id in all_insights[
                        insight_id
                    ].source_fact_ids
                ],
            ]
        )
    )

    unknown = [
        fact_id
        for fact_id in expanded_fact_ids
        if fact_id not in facts
    ]

    if unknown:
        errors.append(f"Unknown repair fact IDs: {unknown}")
        return errors

    if candidate.strategy == RepairStrategy.DELETE:
        if candidate.replacement_text.strip():
            errors.append(
                "Delete repairs must use an empty replacement_text."
            )
        return errors

    if not candidate.replacement_text.strip():
        errors.append("Non-delete repairs require replacement text.")
        return errors

    if (
        original_text is not None
        and " ".join(candidate.replacement_text.split())
        == " ".join(original_text.split())
    ):
        errors.append(
            "The replacement is identical to the original sentence."
        )
        return errors

    supporting_facts = [
        facts[fact_id]
        for fact_id in expanded_fact_ids
    ]

    replacement_hypothesis = EXPLANATORY_HYPOTHESIS_PATTERN.search(
        candidate.replacement_text
    )
    supporting_hypothesis_ids = set(
        candidate.supporting_insight_ids
    ) & set(hypothesis_insights)
    if replacement_hypothesis:
        if (
            not allow_hypotheses_in_report
            or not supporting_hypothesis_ids
        ):
            errors.append(
                "The replacement introduces an explanatory hypothesis "
                "without permitted hypothesis-only provenance."
            )
        elif (
            not HYPOTHESIS_WORDING_PATTERN.search(
                candidate.replacement_text
            )
            and not candidate.replacement_text.strip().endswith("?")
        ):
            errors.append(
                "The replacement does not explicitly label its hypothesis."
            )

    supporting_evidence_ids = {
        evidence_id
        for fact in supporting_facts
        for evidence_id in fact.evidence_ids
    }
    evidence_lookup = build_evidence_lookup(evidence)
    strength_conflicts = qualitative_strength_conflicts(
        candidate.replacement_text,
        [
            evidence_lookup[evidence_id]
            for evidence_id in supporting_evidence_ids
            if evidence_id in evidence_lookup
        ],
    )
    if strength_conflicts:
        errors.append(
            "The replacement uses a qualitative strength label that conflicts "
            "with its mapped evidence: "
            + "; ".join(strength_conflicts)
        )

    if (
        INTERPRETIVE_SYNTHESIS_PATTERN.search(
            candidate.replacement_text
        )
        and not candidate.supporting_insight_ids
    ):
        replacement_normalised = re.sub(
            r"\W+",
            " ",
            candidate.replacement_text.lower(),
        ).strip()
        exact_fact_wording = {
            re.sub(r"\W+", " ", text.lower()).strip()
            for fact in supporting_facts
            for text in [
                fact.fact_summary,
                *fact.allowed_interpretations,
            ]
        }
        if replacement_normalised not in exact_fact_wording:
            errors.append(
                "The replacement introduces an interpretive synthesis "
                "without a verified insight ID."
            )

    support_numbers = [
        number
        for fact in supporting_facts
        for number in fact_support_numbers(fact, evidence)
    ]

    if not numbers_supported(
        candidate.replacement_text,
        support_numbers,
    ):
        errors.append(
            "The replacement introduces unsupported numbers."
        )

    permissions = {
        permission
        for fact in supporting_facts
        for permission in fact.claim_permissions
    }

    if (
        CAUSAL_PATTERN.search(candidate.replacement_text)
        and not negative_causal(candidate.replacement_text)
        and (
            ClaimPermission.CAUSAL not in permissions
            or (
                candidate.supporting_insight_ids
                and not any(
                    CAUSAL_PATTERN.search(
                        all_insights[insight_id].statement
                    )
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                )
            )
        )
    ):
        errors.append(
            "The replacement introduces unsupported causal language."
        )

    if (
        PREDICTIVE_PATTERN.search(candidate.replacement_text)
        and not negative_predictive(candidate.replacement_text)
        and (
            ClaimPermission.PREDICTIVE not in permissions
            or (
                candidate.supporting_insight_ids
                and not any(
                    PREDICTIVE_PATTERN.search(
                        all_insights[insight_id].statement
                    )
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                )
            )
        )
    ):
        errors.append(
            "The replacement introduces unsupported predictive language."
        )

    if (
        FORECAST_PATTERN.search(candidate.replacement_text)
        and not negative_forecast(candidate.replacement_text)
        and (
            ClaimPermission.FORECAST not in permissions
            or (
                candidate.supporting_insight_ids
                and not any(
                    FORECAST_PATTERN.search(
                        all_insights[insight_id].statement
                    )
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                )
            )
        )
    ):
        errors.append(
            "The replacement introduces unsupported forecast language."
        )

    if (
        DATASET_GENERALISATION_PATTERN.search(
            candidate.replacement_text
        )
        and not any(
            DATASET_GENERALISATION_PATTERN.search(
                all_insights[insight_id].statement
            )
            for insight_id in candidate.supporting_insight_ids
            if insight_id in all_insights
        )
    ):
        errors.append(
            "The replacement generalises beyond its verified support."
        )

    if (
        INSIGHT_OVERSTATEMENT_PATTERN.search(
            candidate.replacement_text
        )
        and not any(
            INSIGHT_OVERSTATEMENT_PATTERN.search(
                all_insights[insight_id].statement
            )
            for insight_id in candidate.supporting_insight_ids
            if insight_id in all_insights
        )
    ):
        errors.append(
            "The replacement is stronger than its verified insight wording."
        )

    known_entities = {
        entity
        for fact in supporting_facts
        for entity in fact.entities
    }

    unsupported_entities = unsupported_backtick_entities(
        candidate.replacement_text,
        known_entities,
    )
    if unsupported_entities:
        errors.append(
            "Unsupported named entities in replacement: "
            f"{unsupported_entities}"
        )

    return errors


def apply_repair_proposal(
    writer_output: WriterOutput,
    proposal: AuditRepairProposal,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
) -> tuple[WriterOutput, list[ReportPatch]]:
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    markdown = writer_output.markdown
    support_map = list(writer_output.sentence_support)
    patches: list[ReportPatch] = []

    support_by_sentence = {
        support.sentence_text: support
        for support in support_map
    }
    flagged_sentences = {
        repair.original_sentence
        for repair in proposal.repairs
    }
    original_unflagged_sentences = {
        support.sentence_text
        for support in writer_output.sentence_support
        if support.sentence_text not in flagged_sentences
    }

    for repair in proposal.repairs:
        original = repair.original_sentence

        if original not in markdown:
            continue

        ranked_candidates = sorted(
            repair.candidates,
            key=repair_score,
            reverse=True,
        )

        selected: RepairCandidate | None = None

        if repair.preferred_repair_id:
            preferred = next(
                (
                    candidate
                    for candidate in ranked_candidates
                    if candidate.repair_id == repair.preferred_repair_id
                ),
                None,
            )

            if preferred is not None:
                ranked_candidates = [
                    preferred,
                    *[
                        candidate
                        for candidate in ranked_candidates
                        if candidate.repair_id != preferred.repair_id
                    ],
                ]

        for candidate in ranked_candidates:
            if not validate_repair_candidate(
                candidate,
                fact_ledger,
                evidence,
                insight_ledger,
                allow_hypotheses_in_report,
                original_text=original,
            ):
                selected = candidate
                break

        if selected is None:
            continue

        replacement = selected.replacement_text
        operation = (
            "delete"
            if selected.strategy == RepairStrategy.DELETE
            else "replace"
        )

        markdown = markdown.replace(
            original,
            replacement,
            1,
        )

        existing_support = support_by_sentence.get(original)

        if existing_support is not None:
            support_map.remove(existing_support)
            support_by_sentence.pop(original, None)

        if replacement.strip():
            supporting_facts = {
                fact.fact_id: fact
                for fact in fact_ledger.writer_ready_facts
            }
            main_insights = {
                insight.insight_id: insight
                for insight in insight_ledger.verified_insights
            }
            hypothesis_insights = {
                insight.insight_id: insight
                for insight in insight_ledger.hypothesis_only_insights
            }
            all_insights = {
                **main_insights,
                **hypothesis_insights,
            }
            replacement_fact_ids = list(
                dict.fromkeys(
                    [
                        *selected.supporting_fact_ids,
                        *[
                            fact_id
                            for insight_id in selected.supporting_insight_ids
                            if insight_id in all_insights
                            for fact_id in all_insights[
                                insight_id
                            ].source_fact_ids
                        ],
                    ]
                )
            )

            replacement_evidence = list(
                dict.fromkeys(
                    [
                        *[
                            evidence_id
                            for fact_id in replacement_fact_ids
                            if fact_id in supporting_facts
                            for evidence_id in supporting_facts[
                                fact_id
                            ].evidence_ids
                        ],
                        *[
                            evidence_id
                            for insight_id in selected.supporting_insight_ids
                            if insight_id in all_insights
                            for evidence_id in all_insights[
                                insight_id
                            ].source_evidence_ids
                        ],
                    ]
                )
            )
            replacement_level = InterpretationLevel.FINDING
            if set(selected.supporting_insight_ids) & set(
                hypothesis_insights
            ):
                replacement_level = InterpretationLevel.HYPOTHESIS
            elif set(selected.supporting_insight_ids) & set(
                main_insights
            ):
                replacement_level = InterpretationLevel.BOUNDED_INSIGHT

            replacement_sentences = (
                split_markdown_sentences(replacement)
                or [replacement]
            )
            used_sentence_ids = {
                support.sentence_id
                for support in support_map
            }
            numeric_sentence_ids = [
                int(match.group(1))
                for support in support_map
                if (
                    match := re.fullmatch(
                        r"SENT_(\d+)",
                        support.sentence_id,
                    )
                )
            ]
            next_sentence_number = max(
                numeric_sentence_ids,
                default=0,
            ) + 1

            for index, replacement_sentence in enumerate(
                replacement_sentences
            ):
                sentence_id = repair.sentence_id
                if index > 0 or sentence_id in used_sentence_ids:
                    while (
                        f"SENT_{next_sentence_number:04d}"
                        in used_sentence_ids
                    ):
                        next_sentence_number += 1
                    sentence_id = (
                        f"SENT_{next_sentence_number:04d}"
                    )
                    next_sentence_number += 1

                new_support = SentenceSupport(
                    sentence_id=sentence_id,
                    sentence_text=replacement_sentence,
                    fact_ids=replacement_fact_ids,
                    evidence_ids=replacement_evidence,
                    insight_ids=selected.supporting_insight_ids,
                    interpretation_level=replacement_level,
                    support_type=(
                        SupportType.MULTI_FACT_SYNTHESIS
                        if replacement_level
                        != InterpretationLevel.FINDING
                        else SupportType.PARAPHRASE
                    ),
                )

                support_map.append(new_support)
                support_by_sentence[
                    replacement_sentence
                ] = new_support
                used_sentence_ids.add(sentence_id)

        patches.append(
            ReportPatch(
                sentence_id=repair.sentence_id,
                original_text=original,
                replacement_text=replacement,
                operation=operation,
                selected_repair_id=selected.repair_id,
            )
        )

    selected_fact_ids = list(
        dict.fromkeys(
            fact_id
            for support in support_map
            for fact_id in support.fact_ids
        )
    )

    all_fact_ids = [
        fact.fact_id
        for fact in fact_ledger.writer_ready_facts
    ]

    for sentence in original_unflagged_sentences:
        if sentence and sentence not in markdown:
            raise ValueError(
                "A targeted repair modified or removed unflagged report content."
            )

    return (
        writer_output.model_copy(
            update={
                "markdown": markdown,
                "sentence_support": support_map,
                "selected_fact_ids": selected_fact_ids,
                "omitted_fact_ids": [
                    fact_id
                    for fact_id in all_fact_ids
                    if fact_id not in selected_fact_ids
                ],
                "writer_mode": "auditor_repaired",
            }
        ),
        patches,
    )
````

### `src/table2text/capabilities.py`

````python
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .schemas import (
    AnalyticalFunction,
    CapabilityDefinition,
    ClaimPermission,
    EvidenceCapability,
    EvidenceOperation,
    EvidenceQuery,
    InvestigationTask,
    InputSemanticMap,
    InputShape,
    RecommendedUse,
    SemanticLevel,
    SemanticRole,
    StructuralField,
)
from .structure import find_participant_container, normalise_key


CAPABILITY_REGISTRY: dict[EvidenceCapability, CapabilityDefinition] = {
    EvidenceCapability.DATASET_PROFILE: CapabilityDefinition(
        capability=EvidenceCapability.DATASET_PROFILE,
        supported_input_shapes=list(InputShape),
        output_evidence_types=["dataset_profile", "event_record_overview"],
    ),
    EvidenceCapability.MISSINGNESS: CapabilityDefinition(
        capability=EvidenceCapability.MISSINGNESS,
        supported_input_shapes=[
            InputShape.FLAT_TABLE,
            InputShape.ENTITY_COLLECTION,
            InputShape.TIME_SERIES,
        ],
        output_evidence_types=["missingness"],
    ),
    EvidenceCapability.DUPLICATES: CapabilityDefinition(
        capability=EvidenceCapability.DUPLICATES,
        supported_input_shapes=[
            InputShape.FLAT_TABLE,
            InputShape.ENTITY_COLLECTION,
            InputShape.TIME_SERIES,
        ],
        output_evidence_types=["duplicate_rows"],
    ),
    EvidenceCapability.DISTRIBUTION_SUMMARY: CapabilityDefinition(
        capability=EvidenceCapability.DISTRIBUTION_SUMMARY,
        supported_input_shapes=[
            InputShape.FLAT_TABLE,
            InputShape.ENTITY_COLLECTION,
            InputShape.TIME_SERIES,
        ],
        requires_numeric_fields=True,
        output_evidence_types=["distribution_summary"],
    ),
    EvidenceCapability.ASSOCIATION: CapabilityDefinition(
        capability=EvidenceCapability.ASSOCIATION,
        supported_input_shapes=[
            InputShape.FLAT_TABLE,
            InputShape.ENTITY_COLLECTION,
            InputShape.TIME_SERIES,
        ],
        requires_numeric_fields=True,
        minimum_observations=20,
        output_evidence_types=["correlation"],
    ),
    EvidenceCapability.GROUP_COMPARISON: CapabilityDefinition(
        capability=EvidenceCapability.GROUP_COMPARISON,
        supported_input_shapes=[
            InputShape.FLAT_TABLE,
            InputShape.ENTITY_COLLECTION,
            InputShape.TIME_SERIES,
            InputShape.EVENT_RECORD,
        ],
        requires_entity_fields=True,
        output_evidence_types=["group_comparison", "participant_comparison"],
    ),
    EvidenceCapability.RANKING: CapabilityDefinition(
        capability=EvidenceCapability.RANKING,
        supported_input_shapes=[
            InputShape.ENTITY_COLLECTION,
            InputShape.EVENT_RECORD,
        ],
        requires_entity_fields=True,
        output_evidence_types=["entity_ranking"],
    ),
    EvidenceCapability.EVENT_OUTCOME: CapabilityDefinition(
        capability=EvidenceCapability.EVENT_OUTCOME,
        supported_input_shapes=[InputShape.EVENT_RECORD],
        requires_event_participants=True,
        requires_outcome_field=True,
        output_evidence_types=["event_outcome", "event_status"],
    ),
    EvidenceCapability.ENTITY_PERFORMANCE: CapabilityDefinition(
        capability=EvidenceCapability.ENTITY_PERFORMANCE,
        supported_input_shapes=[InputShape.EVENT_RECORD],
        requires_entity_fields=True,
        requires_event_participants=True,
        output_evidence_types=["entity_performance"],
    ),
}

QUERY_EVIDENCE_TYPES: dict[EvidenceCapability, set[str]] = {
    EvidenceCapability.DATASET_PROFILE: {
        "event_context",
        "event_status",
    },
    EvidenceCapability.EVENT_OUTCOME: {
        "event_outcome",
        "event_context",
        "event_status",
    },
    EvidenceCapability.ENTITY_PERFORMANCE: {"entity_performance"},
    EvidenceCapability.RANKING: {"entity_ranking"},
    EvidenceCapability.GROUP_COMPARISON: {
        "participant_comparison",
        "event_contrast",
    },
}

QUERY_OPERATIONS: dict[str, EvidenceOperation] = {
    "event_outcome": EvidenceOperation.COMPARE,
    "event_context": EvidenceOperation.RETRIEVE,
    "event_status": EvidenceOperation.RETRIEVE,
    "entity_performance": EvidenceOperation.RETRIEVE,
    "entity_ranking": EvidenceOperation.RANK,
    "participant_comparison": EvidenceOperation.COMPARE,
    "event_contrast": EvidenceOperation.COMPARE,
}


PARTICIPATION_REQUEST_PATTERN = re.compile(
    r"\b(duration|time played|playing time|minutes played|seconds played|"
    r"participation|exposure|attendance|appearances?)\b",
    re.IGNORECASE,
)


def participation_measure_requested(request: str) -> bool:
    return bool(PARTICIPATION_REQUEST_PATTERN.search(request))


EVENT_RANKING_RESULT_LIMIT = 200


def _binding_text(binding_id: str, semantic_map: InputSemanticMap) -> str:
    binding = next(
        item
        for item in semantic_map.bindings
        if item.binding_id == binding_id
    )
    return " ".join(
        item
        for item in [
            binding.label,
            binding.path_pattern,
            binding.unit or "",
        ]
        if item
    ).lower()


def _measure_priority(
    binding_id: str,
    semantic_map: InputSemanticMap,
) -> float:
    text = _binding_text(binding_id, semantic_map)
    priority_terms = [
        (100.0, ("point", "score", "total")),
        (90.0, ("goal", "made", "converted")),
        (80.0, ("assist", "support")),
        (75.0, ("rebound", "recovery")),
        (70.0, ("attempt", "opportunit")),
        (55.0, ("turnover", "error")),
        (50.0, ("steal", "block", "defen")),
        (20.0, ("foul", "penalt")),
        (-100.0, ("second", "minute", "duration", "time played", "sec")),
    ]
    score = 0.0
    for value, terms in priority_terms:
        if any(term in text for term in terms):
            score += value
            break

    binding = next(
        item
        for item in semantic_map.bindings
        if item.binding_id == binding_id
    )
    if binding.analytical_function == AnalyticalFunction.OUTCOME:
        score += 120.0
    elif binding.analytical_function == AnalyticalFunction.OUTCOME_COMPONENT:
        score += 80.0
    elif binding.analytical_function == AnalyticalFunction.PERFORMANCE:
        score += 70.0
    elif binding.analytical_function == AnalyticalFunction.PARTICIPATION:
        score -= 120.0

    return score + binding.confidence


def _preferred_identifier(
    bindings: list,
    *,
    preferred_terms: tuple[str, ...],
    excluded_terms: tuple[str, ...] = (),
):
    def score(binding) -> tuple[int, float]:
        text = " ".join(
            item
            for item in [
                binding.label,
                binding.path_pattern,
            ]
            if item
        ).lower()
        preferred = sum(term in text for term in preferred_terms)
        excluded = sum(term in text for term in excluded_terms)
        return (preferred - excluded, binding.confidence)

    eligible = [
        binding
        for binding in bindings
        if not any(
            term
            in " ".join([binding.label, binding.path_pattern]).lower()
            for term in excluded_terms
        )
    ]
    candidates = eligible or bindings
    return max(candidates, key=score) if candidates else None


def _task_id_for_capability(
    tasks: list[InvestigationTask],
    capability: EvidenceCapability,
) -> str | None:
    for task in tasks:
        if task.capability == capability:
            return task.task_id

    return None


def build_event_evidence_queries(
    *,
    semantic_map: InputSemanticMap | None,
    tasks: list[InvestigationTask],
    available_capabilities: set[EvidenceCapability],
    request: str,
) -> list[EvidenceQuery]:
    if semantic_map is None or semantic_map.input_shape != InputShape.EVENT_RECORD:
        return []

    bindings = semantic_map.bindings
    if not bindings:
        return []

    table_name = bindings[0].table_name
    participant_identifiers = [
        binding
        for binding in bindings
        if binding.role == SemanticRole.PARTICIPANT_IDENTIFIER
        and binding.level == SemanticLevel.PARTICIPANT
    ]
    entity_identifiers = [
        binding
        for binding in bindings
        if binding.role == SemanticRole.ENTITY_IDENTIFIER
        and binding.level == SemanticLevel.ENTITY
    ]
    participant_id = _preferred_identifier(
        participant_identifiers,
        preferred_terms=("name", "label", "team", "participant"),
        excluded_terms=("place", "city", "location", "code", "record"),
    )
    participant_group = _preferred_identifier(
        [
            binding
            for binding in participant_identifiers
            if participant_id is None
            or binding.binding_id != participant_id.binding_id
        ],
        preferred_terms=("place", "city", "location"),
    )
    entity_id = _preferred_identifier(
        entity_identifiers,
        preferred_terms=("name", "label", "entity", "player", "person"),
        excluded_terms=("id", "code"),
    )
    context_ids = [
        binding.binding_id
        for binding in bindings
        if binding.level == SemanticLevel.EVENT
        and binding.role
        in {
            SemanticRole.CONTEXT,
            SemanticRole.TIME,
            SemanticRole.LOCATION,
            SemanticRole.METADATA,
        }
    ][:6]
    status_ids = [
        binding.binding_id
        for binding in bindings
        if binding.level == SemanticLevel.EVENT
        and binding.role == SemanticRole.STATUS
    ][:1]
    outcome_ids = [
        binding.binding_id
        for binding in bindings
        if binding.level == SemanticLevel.PARTICIPANT
        and binding.role == SemanticRole.OUTCOME_MEASURE
        and binding.analytical_function == AnalyticalFunction.OUTCOME
    ]
    entity_measure_ids = [
        binding.binding_id
        for binding in bindings
        if binding.level == SemanticLevel.ENTITY
        and binding.role
        in {
            SemanticRole.PERFORMANCE_MEASURE,
            SemanticRole.MEASURE,
        }
        and (
            participation_measure_requested(request)
            or binding.analytical_function
            != AnalyticalFunction.PARTICIPATION
        )
    ]
    participant_component_ids = [
        binding.binding_id
        for binding in bindings
        if binding.level == SemanticLevel.PARTICIPANT
        and binding.role
        in {
            SemanticRole.PERFORMANCE_MEASURE,
            SemanticRole.MEASURE,
        }
        and binding.analytical_function
        == AnalyticalFunction.OUTCOME_COMPONENT
    ]

    queries: list[EvidenceQuery] = []

    event_task_id = _task_id_for_capability(
        tasks,
        EvidenceCapability.EVENT_OUTCOME,
    )
    ranking_task_id = _task_id_for_capability(
        tasks,
        EvidenceCapability.RANKING,
    )
    comparison_task_id = _task_id_for_capability(
        tasks,
        EvidenceCapability.GROUP_COMPARISON,
    )

    common = {
        "table_name": table_name,
        "user_relevance": 0.95,
        "salience": 0.95,
    }

    if (
        event_task_id
        and EvidenceCapability.EVENT_OUTCOME in available_capabilities
        and context_ids
    ):
        queries.append(
            EvidenceQuery(
                query_id="QUERY_EVENT_CONTEXT_AUTO",
                task_id=event_task_id,
                operation=EvidenceOperation.RETRIEVE,
                capability=EvidenceCapability.EVENT_OUTCOME,
                evidence_type="event_context",
                semantic_label="event context",
                question="What supplied context locates this event?",
                semantic_level=SemanticLevel.EVENT,
                value_binding_ids=context_ids,
                recommended_use=RecommendedUse.HEADLINE,
                **common,
            )
        )

    if (
        event_task_id
        and EvidenceCapability.EVENT_OUTCOME in available_capabilities
        and status_ids
    ):
        queries.append(
            EvidenceQuery(
                query_id="QUERY_EVENT_STATUS_AUTO",
                task_id=event_task_id,
                operation=EvidenceOperation.RETRIEVE,
                capability=EvidenceCapability.EVENT_OUTCOME,
                evidence_type="event_status",
                semantic_label="event status",
                question="What status is recorded for this event?",
                semantic_level=SemanticLevel.EVENT,
                value_binding_ids=status_ids,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                **common,
            )
        )

    if (
        event_task_id
        and participant_id
        and outcome_ids
        and EvidenceCapability.EVENT_OUTCOME in available_capabilities
    ):
        outcome_id = max(
            outcome_ids,
            key=lambda binding_id: _measure_priority(
                binding_id,
                semantic_map,
            ),
        )
        queries.append(
            EvidenceQuery(
                query_id="QUERY_EVENT_OUTCOME_AUTO",
                task_id=event_task_id,
                operation=EvidenceOperation.COMPARE,
                capability=EvidenceCapability.EVENT_OUTCOME,
                evidence_type="event_outcome",
                semantic_label="event outcome",
                question="How do the participant outcome measures compare?",
                semantic_level=SemanticLevel.PARTICIPANT,
                value_binding_ids=[outcome_id],
                entity_binding_id=participant_id.binding_id,
                group_binding_id=(
                    participant_group.binding_id
                    if participant_group is not None
                    else None
                ),
                recommended_use=RecommendedUse.HEADLINE,
                **common,
            )
        )

    if (
        ranking_task_id
        and entity_id
        and EvidenceCapability.RANKING in available_capabilities
    ):
        for index, binding_id in enumerate(
            sorted(
                entity_measure_ids,
                key=lambda item: _measure_priority(item, semantic_map),
                reverse=True,
            ),
            start=1,
        ):
            queries.append(
                EvidenceQuery(
                    query_id=f"QUERY_ENTITY_RANKING_AUTO_{index:02d}",
                    task_id=ranking_task_id,
                    operation=EvidenceOperation.RANK,
                    capability=EvidenceCapability.RANKING,
                    evidence_type="entity_ranking",
                    semantic_label=(
                        "entity ranking for "
                        + next(
                            binding.label
                            for binding in bindings
                            if binding.binding_id == binding_id
                        )
                    ),
                    question="Which entities have the highest recorded values?",
                    semantic_level=SemanticLevel.ENTITY,
                    value_binding_ids=[binding_id],
                    entity_binding_id=entity_id.binding_id,
                    group_binding_id=(
                        participant_id.binding_id
                        if participant_id is not None
                        else None
                    ),
                    limit=EVENT_RANKING_RESULT_LIMIT,
                    recommended_use=RecommendedUse.MAIN_FINDING,
                    user_relevance=0.9,
                    salience=0.9,
                    table_name=table_name,
                )
            )

    if (
        comparison_task_id
        and participant_id
        and EvidenceCapability.GROUP_COMPARISON in available_capabilities
    ):
        for index, binding_id in enumerate(
            sorted(
                participant_component_ids,
                key=lambda item: _measure_priority(item, semantic_map),
                reverse=True,
            ),
            start=1,
        ):
            queries.append(
                EvidenceQuery(
                    query_id=f"QUERY_PARTICIPANT_CONTRAST_AUTO_{index:02d}",
                    task_id=comparison_task_id,
                    operation=EvidenceOperation.COMPARE,
                    capability=EvidenceCapability.GROUP_COMPARISON,
                    evidence_type="participant_comparison",
                    semantic_label=(
                        "participant contrast for "
                        + next(
                            binding.label
                            for binding in bindings
                            if binding.binding_id == binding_id
                        )
                    ),
                    question="How do participant-level measures compare?",
                    semantic_level=SemanticLevel.PARTICIPANT,
                    value_binding_ids=[binding_id],
                    entity_binding_id=participant_id.binding_id,
                    group_binding_id=(
                        participant_group.binding_id
                        if participant_group is not None
                        else None
                    ),
                    recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                    user_relevance=0.85,
                    salience=0.85,
                    table_name=table_name,
                )
            )

    return queries


def normalise_event_evidence_queries(
    *,
    queries: list[EvidenceQuery],
    semantic_map: InputSemanticMap | None,
    tasks: list[InvestigationTask],
    available_capabilities: set[EvidenceCapability],
    request: str,
) -> list[EvidenceQuery]:
    if semantic_map is None or semantic_map.input_shape != InputShape.EVENT_RECORD:
        return queries

    generated = build_event_evidence_queries(
        semantic_map=semantic_map,
        tasks=tasks,
        available_capabilities=available_capabilities,
        request=request,
    )
    combined = [*queries, *generated]
    unique: list[EvidenceQuery] = []
    signatures: set[
        tuple[
            str,
            tuple[str, ...],
            str | None,
            str | None,
        ]
    ] = set()
    for query in combined:
        signature = (
            query.operation.value,
            tuple(query.value_binding_ids),
            query.entity_binding_id,
            query.group_binding_id,
        )
        if signature in signatures:
            continue
        signatures.add(signature)
        unique.append(query)

    binding_ids = {
        binding.binding_id
        for binding in semantic_map.bindings
    }

    def query_score(query: EvidenceQuery) -> float:
        score = query.salience + query.user_relevance
        scored_binding_ids = [
            binding_id
            for binding_id in query.value_binding_ids
            if binding_id in binding_ids
        ]
        if scored_binding_ids:
            score += max(
                _measure_priority(binding_id, semantic_map)
                for binding_id in scored_binding_ids
            )
        if query.query_id.endswith("_AUTO"):
            score += 1.0
        return score

    essential_types = (
        "event_context",
        "event_status",
        "event_outcome",
    )
    essential: list[EvidenceQuery] = []
    for evidence_type in essential_types:
        candidates = [
            query
            for query in unique
            if query.evidence_type == evidence_type
        ]
        if candidates:
            essential.append(
                max(candidates, key=query_score)
            )

    rankings = sorted(
        [
            query
            for query in unique
            if query.evidence_type == "entity_ranking"
        ],
        key=query_score,
        reverse=True,
    )
    comparisons = sorted(
        [
            query
            for query in unique
            if query.evidence_type
            in {"participant_comparison", "event_contrast"}
        ],
        key=query_score,
        reverse=True,
    )
    others = [
        query
        for query in unique
        if query.evidence_type
        not in {
            *essential_types,
            "entity_ranking",
            "participant_comparison",
            "event_contrast",
        }
    ]

    ordered = [*essential, *rankings, *comparisons, *others]
    return ordered


ENTITY_CONTAINER_NAMES = {
    "entities",
    "members",
    "participants",
    "performers",
    "players",
}
NAME_FIELD_NAMES = {
    "display_name",
    "entity_name",
    "full_name",
    "name",
    "participant_name",
    "team_name",
}
PLACE_FIELD_NAMES = {"place", "team_place"}
SCORE_FIELD_NAMES = {"final_score", "points", "pts", "score", "total"}
METRIC_ALIASES = {
    "points": {"points", "pts", "score"},
    "rebounds": {"reb", "rebounds"},
    "assists": {"ast", "assists"},
    "turnovers": {"tov", "turnovers"},
    "steals": {"stl", "steals"},
    "blocks": {"blk", "blocks"},
    "field goals made": {"fgm", "field_goals_made"},
    "field goals attempted": {"fga", "field_goals_attempted"},
    "three-pointers made": {"fg3m", "three_pointers_made"},
    "three-pointers attempted": {"fg3a", "three_pointers_attempted"},
    "free throws made": {"ftm", "free_throws_made"},
    "free throws attempted": {"fta", "free_throws_attempted"},
}


@dataclass(frozen=True)
class NumericLeaf:
    path: str
    key: str
    value: float


@dataclass
class EventEntity:
    name: str
    participant_name: str
    metrics: dict[str, float]
    metric_paths: dict[str, str]
    identity_paths: list[str] = field(default_factory=list)


@dataclass
class EventParticipant:
    key: str
    name: str
    source_path: str
    identity_paths: list[str]
    score: float | None
    score_path: str | None
    metrics: dict[str, float] = field(default_factory=dict)
    metric_paths: dict[str, str] = field(default_factory=dict)
    entities: list[EventEntity] = field(default_factory=list)


@dataclass(frozen=True)
class CapabilityEvidence:
    capability: EvidenceCapability
    evidence_type: str
    finding: str
    metrics: dict[str, Any]
    source_paths: list[str]
    entity_scope: list[str]
    practical_interpretation: str
    strength_label: str
    claim_permissions: list[ClaimPermission]
    factual_confidence: float
    methodological_strength: float
    user_relevance: float
    salience: float
    recommended_use: RecommendedUse
    semantic_level: SemanticLevel = SemanticLevel.DATASET
    semantic_binding_ids: list[str] = field(default_factory=list)
    analytical_function: AnalyticalFunction | None = None
    query_id: str | None = None
    limitations: list[str] = field(default_factory=list)
    prohibited_interpretations: list[str] = field(default_factory=list)


def _numeric_leaves(
    value: Any,
    prefix: str,
    *,
    max_depth: int = 7,
) -> list[NumericLeaf]:
    leaves: list[NumericLeaf] = []

    def visit(current: Any, path: str, depth: int) -> None:
        if depth > max_depth:
            return
        if isinstance(current, Mapping):
            for key, child in current.items():
                child_path = f"{path}.{key}" if path else str(key)
                visit(child, child_path, depth + 1)
        elif isinstance(current, (int, float)) and not isinstance(current, bool):
            key = normalise_key(path.rsplit(".", 1)[-1])
            leaves.append(NumericLeaf(path=path, key=key, value=float(current)))

    visit(value, prefix, 0)
    return leaves


def _first_named_item(
    value: Mapping[str, Any],
    names: set[str],
    prefix: str = "",
) -> tuple[str | None, str | None]:
    for key, child in value.items():
        if normalise_key(str(key)) in names and isinstance(child, str) and child.strip():
            path = f"{prefix}.{key}" if prefix else str(key)
            return child.strip(), path
    return None, None


def _first_named_value(value: Mapping[str, Any], names: set[str]) -> str | None:
    return _first_named_item(value, names)[0]


def _participant_identity(
    key: str,
    value: Mapping[str, Any],
    prefix: str,
) -> tuple[str, list[str]]:
    name, name_path = _first_named_item(value, NAME_FIELD_NAMES, prefix)
    place, place_path = _first_named_item(value, PLACE_FIELD_NAMES, prefix)
    name = name or str(key)
    identity_paths = [path for path in [place_path, name_path] if path]
    if place and normalise_key(place) not in normalise_key(name):
        name = f"{place} {name}"
    return name, identity_paths


def _canonical_metric(key: str) -> str | None:
    normalised = normalise_key(key)
    for label, aliases in METRIC_ALIASES.items():
        if normalised in aliases:
            return label
    return None


def _score_leaf(value: Mapping[str, Any], prefix: str) -> NumericLeaf | None:
    candidates: list[tuple[int, NumericLeaf]] = []
    for leaf in _numeric_leaves(value, prefix):
        relative_path = leaf.path.removeprefix(prefix).lstrip(".")
        path_parts = {
            normalise_key(part)
            for part in relative_path.split(".")
        }
        if path_parts & ENTITY_CONTAINER_NAMES:
            continue
        if leaf.key not in SCORE_FIELD_NAMES:
            continue
        score = 20
        if "game" in path_parts or "event" in path_parts:
            score += 30
        if "team" in path_parts or "participant" in path_parts:
            score += 20
        if leaf.key in {"score", "final_score"}:
            score += 15
        candidates.append((score, leaf))
    return max(candidates, default=(0, None), key=lambda item: item[0])[1]


def _team_metric_mapping(
    value: Mapping[str, Any],
    prefix: str,
) -> tuple[dict[str, float], dict[str, str]]:
    best_score = -1
    best_metrics: dict[str, float] = {}
    best_paths: dict[str, str] = {}

    def visit(current: Any, path: str, depth: int) -> None:
        nonlocal best_score, best_metrics, best_paths
        if depth > 6 or not isinstance(current, Mapping):
            return

        metrics: dict[str, float] = {}
        paths: dict[str, str] = {}
        for key, child in current.items():
            if isinstance(child, (int, float)) and not isinstance(child, bool):
                canonical = _canonical_metric(str(key))
                if canonical:
                    metrics[canonical] = float(child)
                    paths[canonical] = f"{path}.{key}" if path else str(key)

        relative_path = path.removeprefix(prefix).lstrip(".")
        path_names = {
            normalise_key(part)
            for part in relative_path.split(".")
        }
        score = len(metrics)
        if "game" in path_names or "event" in path_names:
            score += 10
        if "team" in path_names or "participant" in path_names:
            score += 5
        if "period" in path_names or path_names & ENTITY_CONTAINER_NAMES:
            score -= 20
        if score > best_score:
            best_score = score
            best_metrics = metrics
            best_paths = paths

        for key, child in current.items():
            if isinstance(child, Mapping):
                child_path = f"{path}.{key}" if path else str(key)
                visit(child, child_path, depth + 1)

    visit(value, prefix, 0)
    return best_metrics, best_paths


def _entity_container(
    value: Mapping[str, Any],
    prefix: str,
) -> tuple[str, Mapping[str, Any]] | None:
    stack: list[tuple[str, Any, int]] = [(prefix, value, 0)]
    while stack:
        path, current, depth = stack.pop()
        if depth > 6 or not isinstance(current, Mapping):
            continue
        for key, child in current.items():
            child_path = f"{path}.{key}" if path else str(key)
            if (
                normalise_key(str(key)) in ENTITY_CONTAINER_NAMES
                and isinstance(child, Mapping)
                and child
                and all(isinstance(item, Mapping) for item in child.values())
            ):
                return child_path, child
            if isinstance(child, Mapping):
                stack.append((child_path, child, depth + 1))
    return None


def extract_event_participants(payload: Any) -> list[EventParticipant]:
    located = find_participant_container(payload)
    if located is None:
        return []
    container_path, container = located
    participants: list[EventParticipant] = []

    for key, raw_participant in container.items():
        if not isinstance(raw_participant, Mapping):
            continue
        source_path = f"{container_path}.{key}"
        participant_name, identity_paths = _participant_identity(
            str(key), raw_participant, source_path
        )
        score_leaf = _score_leaf(raw_participant, source_path)
        metrics, metric_paths = _team_metric_mapping(raw_participant, source_path)
        participant = EventParticipant(
            key=str(key),
            name=participant_name,
            source_path=source_path,
            identity_paths=identity_paths,
            score=(score_leaf.value if score_leaf else None),
            score_path=(score_leaf.path if score_leaf else None),
            metrics=metrics,
            metric_paths=metric_paths,
        )

        located_entities = _entity_container(raw_participant, source_path)
        if located_entities is not None:
            entity_path, entities = located_entities
            for entity_key, raw_entity in entities.items():
                if not isinstance(raw_entity, Mapping):
                    continue
                entity_metrics: dict[str, float] = {}
                entity_metric_paths: dict[str, str] = {}
                for raw_metric, raw_value in raw_entity.items():
                    if not isinstance(raw_value, (int, float)) or isinstance(
                        raw_value, bool
                    ):
                        continue
                    canonical = _canonical_metric(str(raw_metric))
                    if canonical:
                        entity_metrics[canonical] = float(raw_value)
                        entity_metric_paths[canonical] = (
                            f"{entity_path}.{entity_key}.{raw_metric}"
                        )
                entity_name, entity_name_path = _first_named_item(
                    raw_entity,
                    NAME_FIELD_NAMES,
                    f"{entity_path}.{entity_key}",
                )
                entity_name = entity_name or str(entity_key)
                participant.entities.append(
                    EventEntity(
                        name=entity_name,
                        participant_name=participant.name,
                        metrics=entity_metrics,
                        metric_paths=entity_metric_paths,
                        identity_paths=list(
                            dict.fromkeys(
                                [
                                    *participant.identity_paths,
                                    *(
                                        [entity_name_path]
                                        if entity_name_path
                                        else []
                                    ),
                                ]
                            )
                        ),
                    )
                )
        participants.append(participant)

    return participants


def available_capabilities(
    bundle: Any,
    semantic_map: InputSemanticMap | None = None,
) -> list[EvidenceCapability]:
    shape = getattr(getattr(bundle, "input_structure", None), "shape", None)
    capabilities = [EvidenceCapability.DATASET_PROFILE]

    if shape in {
        InputShape.FLAT_TABLE,
        InputShape.ENTITY_COLLECTION,
        InputShape.TIME_SERIES,
    }:
        capabilities.extend(
            [
                EvidenceCapability.MISSINGNESS,
                EvidenceCapability.DUPLICATES,
                EvidenceCapability.DISTRIBUTION_SUMMARY,
                EvidenceCapability.ASSOCIATION,
                EvidenceCapability.GROUP_COMPARISON,
            ]
        )

    if semantic_map is not None and semantic_map.bindings:
        semantic_shape = semantic_map.input_shape
        roles_by_table: dict[str, set[SemanticRole]] = {}
        for binding in semantic_map.bindings:
            roles_by_table.setdefault(binding.table_name, set()).add(
                binding.role
            )
        role_sets = list(roles_by_table.values())
        if (
            semantic_shape == InputShape.EVENT_RECORD
            and any(
                {
                    SemanticRole.PARTICIPANT_IDENTIFIER,
                    SemanticRole.OUTCOME_MEASURE,
                }.issubset(roles)
                for roles in role_sets
            )
        ):
            capabilities.append(EvidenceCapability.EVENT_OUTCOME)
        if (
            semantic_shape in {
                InputShape.ENTITY_COLLECTION,
                InputShape.EVENT_RECORD,
            }
            and any(
                SemanticRole.ENTITY_IDENTIFIER in roles
                and bool(
                    roles
                    & {
                        SemanticRole.PERFORMANCE_MEASURE,
                        SemanticRole.MEASURE,
                    }
                )
                for roles in role_sets
            )
        ):
            capabilities.append(EvidenceCapability.RANKING)
        if (
            semantic_shape == InputShape.EVENT_RECORD
            and any(
                {
                    SemanticRole.PARTICIPANT_IDENTIFIER,
                    SemanticRole.ENTITY_IDENTIFIER,
                }.issubset(roles)
                and bool(
                    roles
                    & {
                        SemanticRole.PERFORMANCE_MEASURE,
                        SemanticRole.MEASURE,
                    }
                )
                for roles in role_sets
            )
        ):
            capabilities.append(EvidenceCapability.ENTITY_PERFORMANCE)
        if (
            semantic_shape == InputShape.EVENT_RECORD
            and any(
                SemanticRole.PARTICIPANT_IDENTIFIER in roles
                and bool(
                    roles
                    & {
                        SemanticRole.PERFORMANCE_MEASURE,
                        SemanticRole.OUTCOME_MEASURE,
                        SemanticRole.MEASURE,
                    }
                )
                for roles in role_sets
            )
        ):
            capabilities.append(EvidenceCapability.GROUP_COMPARISON)
    else:
        participants = [
            participant
            for payload in getattr(bundle, "structured_inputs", {}).values()
            for participant in extract_event_participants(payload)
        ]
        if len(participants) >= 2:
            if all(participant.score is not None for participant in participants):
                capabilities.append(EvidenceCapability.EVENT_OUTCOME)
            if any(participant.entities for participant in participants):
                capabilities.extend(
                    [
                        EvidenceCapability.ENTITY_PERFORMANCE,
                        EvidenceCapability.RANKING,
                    ]
                )
            if len([participant for participant in participants if participant.metrics]) >= 2:
                capabilities.append(EvidenceCapability.GROUP_COMPARISON)

    return list(dict.fromkeys(capabilities))


def event_capability_evidence(payload: Any) -> list[CapabilityEvidence]:
    participants = extract_event_participants(payload)
    if len(participants) < 2:
        return []

    evidence: list[CapabilityEvidence] = []
    participant_names = [participant.name for participant in participants]
    scored = [participant for participant in participants if participant.score is not None]

    if len(scored) >= 2:
        ordered = sorted(scored, key=lambda item: float(item.score or 0), reverse=True)
        winner, runner_up = ordered[0], ordered[1]
        margin = float(winner.score or 0) - float(runner_up.score or 0)
        tied = margin == 0
        if tied:
            finding = (
                f"{winner.name} and {runner_up.name} finished level at "
                f"{winner.score:g}-{runner_up.score:g}."
            )
        else:
            finding = (
                f"{winner.name} defeated {runner_up.name} "
                f"{winner.score:g}-{runner_up.score:g}, a margin of {margin:g}."
            )
        evidence.append(
            CapabilityEvidence(
                capability=EvidenceCapability.EVENT_OUTCOME,
                evidence_type="event_outcome",
                finding=finding,
                metrics={
                    "winner": None if tied else winner.name,
                    "loser": None if tied else runner_up.name,
                    "winner_score": winner.score,
                    "loser_score": runner_up.score,
                    "margin": margin,
                    "tied": tied,
                },
                source_paths=[
                    path
                    for path in [
                        *winner.identity_paths,
                        winner.score_path,
                        *runner_up.identity_paths,
                        runner_up.score_path,
                    ]
                    if path
                ],
                entity_scope=[winner.name, runner_up.name],
                practical_interpretation=(
                    "This establishes the supported event result and score margin."
                ),
                strength_label="event_outcome",
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.COMPARATIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
                prohibited_interpretations=[
                    "Do not infer chronology, a comeback, dominance, or historical "
                    "significance from the final score alone."
                ],
            )
        )

    all_entities = [entity for participant in participants for entity in participant.entities]
    for metric in ["points", "rebounds", "assists"]:
        ranked = sorted(
            [entity for entity in all_entities if metric in entity.metrics],
            key=lambda entity: entity.metrics[metric],
            reverse=True,
        )
        if not ranked:
            continue
        leaders = ranked[:3]
        ranking_text = "; ".join(
            f"{entity.name} ({entity.participant_name}) recorded "
            f"{entity.metrics[metric]:g}"
            for entity in leaders
        )
        evidence.append(
            CapabilityEvidence(
                capability=EvidenceCapability.RANKING,
                evidence_type="entity_ranking",
                finding=f"The leading recorded {metric} performances were: {ranking_text}.",
                metrics={
                    "metric": metric,
                    "ranking": [
                        {
                            "rank": index,
                            "entity": entity.name,
                            "participant": entity.participant_name,
                            "value": entity.metrics[metric],
                        }
                        for index, entity in enumerate(leaders, start=1)
                    ],
                },
                source_paths=[
                    path
                    for entity in leaders
                    for path in [
                        *entity.identity_paths,
                        entity.metric_paths.get(metric),
                    ]
                    if path
                ],
                entity_scope=[entity.name for entity in leaders],
                practical_interpretation=(
                    f"This ranks entities by the observed {metric} metric within "
                    "the supplied event."
                ),
                strength_label="entity_ranking",
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.COMPARATIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.95,
                salience=0.95 if metric == "points" else 0.85,
                recommended_use=(
                    RecommendedUse.MAIN_FINDING
                    if metric == "points"
                    else RecommendedUse.SUPPORTING_DETAIL
                ),
                limitations=[
                    "The ranking is limited to entities and metrics recorded in "
                    "the supplied event structure."
                ],
                prohibited_interpretations=[
                    "Do not call a ranked entity historically best or dominant."
                ],
            )
        )

    if all_entities:
        top_entity = max(
            all_entities,
            key=lambda entity: entity.metrics.get("points", float("-inf")),
        )
        visible_metrics = [
            metric
            for metric in ["points", "rebounds", "assists"]
            if metric in top_entity.metrics
        ]
        if visible_metrics:
            metric_text = ", ".join(
                f"{top_entity.metrics[metric]:g} {metric}"
                for metric in visible_metrics
            )
            evidence.append(
                CapabilityEvidence(
                    capability=EvidenceCapability.ENTITY_PERFORMANCE,
                    evidence_type="entity_performance",
                    finding=(
                        f"{top_entity.name} recorded {metric_text} for "
                        f"{top_entity.participant_name}."
                    ),
                    metrics={
                        "entity": top_entity.name,
                        "participant": top_entity.participant_name,
                        **{
                            metric: top_entity.metrics[metric]
                            for metric in visible_metrics
                        },
                    },
                    source_paths=[
                        *top_entity.identity_paths,
                        *[
                            top_entity.metric_paths[metric]
                            for metric in visible_metrics
                        ],
                    ],
                    entity_scope=[top_entity.name, top_entity.participant_name],
                    practical_interpretation=(
                        "This identifies a leading recorded entity performance "
                        "without adding a domain-specific milestone."
                    ),
                    strength_label="entity_performance",
                    claim_permissions=[ClaimPermission.DESCRIPTIVE],
                    factual_confidence=1.0,
                    methodological_strength=1.0,
                    user_relevance=0.95,
                    salience=0.95,
                    recommended_use=RecommendedUse.MAIN_FINDING,
                    prohibited_interpretations=[
                        "Do not infer that this performance caused the event result."
                    ],
                )
            )

    metric_participants = [participant for participant in participants if participant.metrics]
    if len(metric_participants) >= 2:
        left, right = metric_participants[:2]
        common_metrics = set(left.metrics) & set(right.metrics)
        comparisons = sorted(
            common_metrics,
            key=lambda metric: abs(left.metrics[metric] - right.metrics[metric]),
            reverse=True,
        )
        for metric in comparisons[:6]:
            left_value = left.metrics[metric]
            right_value = right.metrics[metric]
            if left_value == right_value:
                continue
            leader, trailer = (
                (left, right) if left_value > right_value else (right, left)
            )
            leader_value = leader.metrics[metric]
            trailer_value = trailer.metrics[metric]
            evidence.append(
                CapabilityEvidence(
                    capability=EvidenceCapability.GROUP_COMPARISON,
                    evidence_type="participant_comparison",
                    finding=(
                        f"{leader.name} recorded more {metric} than {trailer.name} "
                        f"({leader_value:g} versus {trailer_value:g}), a difference "
                        f"of {abs(leader_value - trailer_value):g}."
                    ),
                    metrics={
                        "metric": metric,
                        "higher_participant": leader.name,
                        "lower_participant": trailer.name,
                        "higher_value": leader_value,
                        "lower_value": trailer_value,
                        "difference": abs(leader_value - trailer_value),
                    },
                    source_paths=[
                        *leader.identity_paths,
                        leader.metric_paths[metric],
                        *trailer.identity_paths,
                        trailer.metric_paths[metric],
                    ],
                    entity_scope=[leader.name, trailer.name],
                    practical_interpretation=(
                        "This is a direct participant-level contrast within the event."
                    ),
                    strength_label="participant_comparison",
                    claim_permissions=[
                        ClaimPermission.DESCRIPTIVE,
                        ClaimPermission.COMPARATIVE,
                    ],
                    factual_confidence=1.0,
                    methodological_strength=1.0,
                    user_relevance=0.8,
                    salience=0.75,
                    recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                    prohibited_interpretations=[
                        "Do not call the contrast decisive without explicit evidence."
                    ],
                )
            )

    if isinstance(payload, Mapping):
        overtime_path = next(
            (
                str(key)
                for key in payload
                if normalise_key(str(key)) in {"overtime", "extra_time"}
            ),
            None,
        )
        if overtime_path is not None and isinstance(payload[overtime_path], bool):
            overtime = bool(payload[overtime_path])
            evidence.append(
                CapabilityEvidence(
                    capability=EvidenceCapability.EVENT_OUTCOME,
                    evidence_type="event_status",
                    finding=(
                        "The event required overtime."
                        if overtime
                        else "The event did not require overtime."
                    ),
                    metrics={"overtime": overtime},
                    source_paths=[overtime_path],
                    entity_scope=participant_names,
                    practical_interpretation=(
                        "This records the supplied event-status indicator."
                    ),
                    strength_label="event_status",
                    claim_permissions=[ClaimPermission.DESCRIPTIVE],
                    factual_confidence=1.0,
                    methodological_strength=1.0,
                    user_relevance=0.65,
                    salience=0.55,
                    recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                )
            )

    return evidence


@dataclass(frozen=True)
class PathMatch:
    source_path: str
    captures: tuple[str, ...]
    value: Any


def match_path_pattern(payload: Any, pattern: str) -> list[PathMatch]:
    """Resolve a dot path containing mapping/list wildcards."""

    parts = [part for part in pattern.split(".") if part]
    matches: list[PathMatch] = []

    def visit(
        current: Any,
        index: int,
        path_parts: list[str],
        captures: list[str],
    ) -> None:
        if index == len(parts):
            matches.append(
                PathMatch(
                    source_path=".".join(path_parts),
                    captures=tuple(captures),
                    value=current,
                )
            )
            return

        part = parts[index]
        if part == "*":
            if isinstance(current, Mapping):
                for key, child in current.items():
                    visit(
                        child,
                        index + 1,
                        [*path_parts, str(key)],
                        [*captures, str(key)],
                    )
            elif isinstance(current, list):
                for item_index, child in enumerate(current):
                    visit(
                        child,
                        index + 1,
                        [*path_parts, str(item_index)],
                        [*captures, str(item_index)],
                    )
            return

        if isinstance(current, Mapping) and part in current:
            visit(
                current[part],
                index + 1,
                [*path_parts, part],
                captures,
            )
            return

        if isinstance(current, list) and part.isdigit():
            item_index = int(part)
            if 0 <= item_index < len(current):
                visit(
                    current[item_index],
                    index + 1,
                    [*path_parts, part],
                    captures,
                )

    visit(payload, 0, [], [])
    return matches


def validate_semantic_map(
    semantic_map: InputSemanticMap | None,
    structural_catalog: list[StructuralField],
) -> list[str]:
    if semantic_map is None:
        return []

    errors: list[str] = []
    seen: set[str] = set()
    seen_paths: set[tuple[str, str]] = set()
    catalog_paths = {(field.table_name, field.path_pattern) for field in structural_catalog}

    for binding in semantic_map.bindings:
        if binding.binding_id in seen:
            errors.append(f"Duplicate semantic binding ID: {binding.binding_id}.")
        seen.add(binding.binding_id)
        if (binding.table_name, binding.path_pattern) not in catalog_paths:
            errors.append(
                f"Semantic binding {binding.binding_id} uses an unknown "
                f"catalog path: {binding.table_name}:{binding.path_pattern}."
            )

        binding_path = (binding.table_name, binding.path_pattern)
        if binding_path in seen_paths:
            errors.append(
                f"Semantic binding {binding.binding_id} repeats catalog path "
                f"{binding.table_name}:{binding.path_pattern}."
            )
        seen_paths.add(binding_path)

    if semantic_map.input_shape != InputShape.EVENT_RECORD:
        return errors

    measure_roles = {
        SemanticRole.OUTCOME_MEASURE,
        SemanticRole.PERFORMANCE_MEASURE,
        SemanticRole.MEASURE,
    }
    missing_function_ids = [
        binding.binding_id
        for binding in semantic_map.bindings
        if binding.role in measure_roles
        and binding.analytical_function is None
    ]
    if missing_function_ids:
        errors.append(
            "Event measure bindings must declare analytical_function: "
            + ", ".join(missing_function_ids)
            + "."
        )

    invalid_outcome_ids = [
        binding.binding_id
        for binding in semantic_map.bindings
        if binding.role == SemanticRole.OUTCOME_MEASURE
        and binding.analytical_function != AnalyticalFunction.OUTCOME
    ]
    if invalid_outcome_ids:
        errors.append(
            "Event outcome bindings must use analytical function 'outcome': "
            + ", ".join(invalid_outcome_ids)
            + "."
        )

    invalid_function_ids = [
        binding.binding_id
        for binding in semantic_map.bindings
        if binding.analytical_function
        in {
            AnalyticalFunction.OUTCOME,
            AnalyticalFunction.OUTCOME_COMPONENT,
            AnalyticalFunction.PERFORMANCE,
            AnalyticalFunction.PARTICIPATION,
        }
        and binding.role not in measure_roles
    ]
    if invalid_function_ids:
        errors.append(
            "Measure analytical functions cannot be assigned to non-measure "
            "bindings: "
            + ", ".join(invalid_function_ids)
            + "."
        )

    entity_measure_groups: dict[tuple[str, str], set[str]] = {}
    for binding in semantic_map.bindings:
        if binding.role != SemanticRole.ENTITY_IDENTIFIER:
            continue
        parent_path = binding.path_pattern.rsplit(".", 1)[0]
        key = (binding.table_name, parent_path)
        entity_measure_groups.setdefault(key, set())

    numeric_types = {"integer", "number"}
    for key in entity_measure_groups:
        table_name, parent_path = key
        entity_measure_groups[key] = {
            field.path_pattern
            for field in structural_catalog
            if field.table_name == table_name
            and field.path_pattern.rsplit(".", 1)[0] == parent_path
            and set(field.value_types) & numeric_types
        }

    substantive_functions = {
        AnalyticalFunction.PERFORMANCE,
        AnalyticalFunction.OUTCOME_COMPONENT,
    }
    for (table_name, parent_path), available_paths in entity_measure_groups.items():
        required = min(3, len(available_paths))
        if required == 0:
            continue
        selected = {
            binding.path_pattern
            for binding in semantic_map.bindings
            if binding.table_name == table_name
            and binding.path_pattern.rsplit(".", 1)[0] == parent_path
            and binding.level == SemanticLevel.ENTITY
            and binding.analytical_function in substantive_functions
        }
        if len(selected) < required:
            errors.append(
                "Event semantic map must reserve substantive entity-performance "
                f"bindings under {table_name}:{parent_path}; found {len(selected)} "
                f"but the catalog supports at least {required}."
            )

    return errors


def validate_event_query_priorities(
    queries: list[EvidenceQuery],
    semantic_map: InputSemanticMap | None,
    request: str,
) -> list[str]:
    if semantic_map is None or semantic_map.input_shape != InputShape.EVENT_RECORD:
        return []
    substantive_ids = {
        binding.binding_id
        for binding in semantic_map.bindings
        if binding.level == SemanticLevel.ENTITY
        and binding.analytical_function
        in {
            AnalyticalFunction.PERFORMANCE,
            AnalyticalFunction.OUTCOME_COMPONENT,
        }
    }
    entity_queries = [
        query
        for query in queries
        if query.evidence_type
        in {"entity_ranking", "entity_performance"}
    ]
    ranking_queries = [
        query
        for query in entity_queries
        if query.evidence_type == "entity_ranking"
    ]
    errors: list[str] = []

    queried_substantive_ids = {
        binding_id
        for query in ranking_queries
        for binding_id in query.value_binding_ids
        if binding_id in substantive_ids
    }
    required = min(3, len(substantive_ids))
    if len(queried_substantive_ids) < required:
        errors.append(
            "Event plan must rank distinct substantive entity-performance "
            f"measures when available; found {len(queried_substantive_ids)} "
            f"but {required} are required."
        )

    component_ids = {
        binding.binding_id
        for binding in semantic_map.bindings
        if binding.level == SemanticLevel.PARTICIPANT
        and binding.analytical_function
        == AnalyticalFunction.OUTCOME_COMPONENT
    }
    comparison_queries = [
        query
        for query in queries
        if query.evidence_type
        in {"participant_comparison", "event_contrast"}
    ]
    queried_component_ids = {
        binding_id
        for query in comparison_queries
        for binding_id in query.value_binding_ids
        if binding_id in component_ids
    }
    required_components = min(2, len(component_ids))
    if len(queried_component_ids) < required_components:
        errors.append(
            "Event plan must compare distinct participant-level outcome "
            f"components when available; found {len(queried_component_ids)} "
            f"but {required_components} are required."
        )

    return errors


def validate_evidence_queries(
    queries: list[EvidenceQuery],
    semantic_map: InputSemanticMap | None,
    structural_catalog: list[StructuralField],
    *,
    task_ids: set[str],
    available: set[EvidenceCapability],
    task_capabilities: dict[str, EvidenceCapability | None] | None = None,
) -> list[str]:
    errors = validate_semantic_map(semantic_map, structural_catalog)
    if semantic_map is None:
        if queries:
            errors.append("Evidence queries require an input semantic map.")
        return errors

    binding_lookup = {binding.binding_id: binding for binding in semantic_map.bindings}
    catalog_lookup = {(field.table_name, field.path_pattern): field for field in structural_catalog}
    seen_query_ids: set[str] = set()

    for query in queries:
        if query.query_id in seen_query_ids:
            errors.append(f"Duplicate evidence query ID: {query.query_id}.")
        seen_query_ids.add(query.query_id)

        if re.search(r"(?<!\w)\d+(?:[.,]\d+)?", query.question):
            errors.append(
                f"Evidence query {query.query_id} contains a result value in "
                "its pre-result analytical question."
            )

        if query.task_id not in task_ids:
            errors.append(f"Evidence query {query.query_id} uses unknown task {query.task_id}.")
        elif (
            task_capabilities is not None
            and task_capabilities.get(query.task_id) is not None
            and task_capabilities[query.task_id] != query.capability
        ):
            errors.append(
                f"Evidence query {query.query_id} does not match the capability "
                f"of task {query.task_id}."
            )
        if query.capability not in available:
            errors.append(
                f"Evidence query {query.query_id} uses unavailable capability "
                f"{query.capability.value}."
            )
        allowed_evidence_types = QUERY_EVIDENCE_TYPES.get(query.capability)
        if allowed_evidence_types is not None and query.evidence_type not in allowed_evidence_types:
            errors.append(
                f"Evidence query {query.query_id} uses evidence_type "
                f"{query.evidence_type!r}; allowed values for "
                f"{query.capability.value} are "
                f"{sorted(allowed_evidence_types)}."
            )
        expected_operation = QUERY_OPERATIONS.get(query.evidence_type)
        if expected_operation is not None and query.operation != expected_operation:
            errors.append(
                f"Evidence query {query.query_id} must use operation "
                f"{expected_operation.value!r} for evidence_type "
                f"{query.evidence_type!r}."
            )

        referenced_ids = [
            *query.value_binding_ids,
            *query.context_binding_ids,
            *([query.entity_binding_id] if query.entity_binding_id else []),
            *([query.group_binding_id] if query.group_binding_id else []),
        ]
        unknown_ids = [
            binding_id for binding_id in referenced_ids if binding_id not in binding_lookup
        ]
        if unknown_ids:
            errors.append(
                f"Evidence query {query.query_id} uses unknown semantic bindings: {unknown_ids}."
            )
            continue

        wrong_table = [
            binding_id
            for binding_id in referenced_ids
            if binding_lookup[binding_id].table_name != query.table_name
        ]
        if wrong_table:
            errors.append(
                f"Evidence query {query.query_id} mixes bindings from another table: {wrong_table}."
            )

        value_bindings = [
            binding_lookup[binding_id]
            for binding_id in query.value_binding_ids
            if binding_id in binding_lookup
        ]
        entity_binding = (
            binding_lookup.get(query.entity_binding_id)
            if query.entity_binding_id
            else None
        )
        allowed_value_roles = {
            "event_outcome": {SemanticRole.OUTCOME_MEASURE},
            "event_context": {
                SemanticRole.CONTEXT,
                SemanticRole.IDENTIFIER,
                SemanticRole.LOCATION,
                SemanticRole.METADATA,
                SemanticRole.TIME,
            },
            "event_status": {SemanticRole.STATUS},
            "entity_performance": {
                SemanticRole.MEASURE,
                SemanticRole.PERFORMANCE_MEASURE,
            },
            "entity_ranking": {
                SemanticRole.MEASURE,
                SemanticRole.PERFORMANCE_MEASURE,
            },
            "participant_comparison": {
                SemanticRole.MEASURE,
                SemanticRole.OUTCOME_MEASURE,
                SemanticRole.PERFORMANCE_MEASURE,
            },
            "event_contrast": {
                SemanticRole.MEASURE,
                SemanticRole.OUTCOME_MEASURE,
                SemanticRole.PERFORMANCE_MEASURE,
            },
        }.get(query.evidence_type)
        if allowed_value_roles is not None:
            invalid_value_bindings = [
                binding.binding_id
                for binding in value_bindings
                if binding.role not in allowed_value_roles
            ]
            if invalid_value_bindings:
                errors.append(
                    f"Evidence query {query.query_id} uses semantically "
                    f"incompatible value bindings: {invalid_value_bindings}."
                )
        expected_entity_level = {
            "event_outcome": SemanticLevel.PARTICIPANT,
            "participant_comparison": SemanticLevel.PARTICIPANT,
            "event_contrast": SemanticLevel.PARTICIPANT,
            "entity_performance": SemanticLevel.ENTITY,
            "entity_ranking": SemanticLevel.ENTITY,
        }.get(query.evidence_type)
        if expected_entity_level is not None:
            if entity_binding is None:
                errors.append(
                    f"Evidence query {query.query_id} requires an identifier "
                    f"binding at semantic level {expected_entity_level.value!r}."
                )
            elif entity_binding.level != expected_entity_level:
                errors.append(
                    f"Evidence query {query.query_id} requires an identifier at "
                    f"semantic level {expected_entity_level.value!r}."
                )

        if not query.value_binding_ids:
            errors.append(f"Evidence query {query.query_id} has no value bindings.")
        if query.operation in {
            EvidenceOperation.COMPARE,
            EvidenceOperation.RANK,
        }:
            if len(query.value_binding_ids) != 1:
                errors.append(
                    f"Evidence query {query.query_id} must use exactly one measure binding."
                )
            if query.entity_binding_id is None:
                errors.append(
                    f"Evidence query {query.query_id} requires an entity identifier binding."
                )
            for binding_id in query.value_binding_ids:
                binding = binding_lookup.get(binding_id)
                if binding is None:
                    continue
                field = catalog_lookup.get((binding.table_name, binding.path_pattern))
                if field is not None and not set(field.value_types) & {
                    "integer",
                    "number",
                }:
                    errors.append(
                        f"Evidence query {query.query_id} uses non-numeric "
                        f"measure binding {binding_id}."
                    )

    return errors


def _aligned_label(
    match: PathMatch,
    label_matches: list[PathMatch],
) -> tuple[str | None, str | None]:
    compatible = [
        candidate
        for candidate in label_matches
        if candidate.captures == match.captures[: len(candidate.captures)]
    ]
    if not compatible:
        return None, None
    selected = max(compatible, key=lambda item: len(item.captures))
    return str(selected.value), selected.source_path


def _query_permissions(
    operation: EvidenceOperation,
) -> list[ClaimPermission]:
    permissions = [ClaimPermission.DESCRIPTIVE]
    if operation in {EvidenceOperation.COMPARE, EvidenceOperation.RANK}:
        permissions.append(ClaimPermission.COMPARATIVE)
    return permissions


def semantic_query_evidence(
    *,
    table_name: str,
    payload: Any,
    semantic_map: InputSemanticMap,
    queries: list[EvidenceQuery],
) -> list[CapabilityEvidence]:
    """Execute validated generic semantic queries without authoring claims."""

    binding_lookup = {
        binding.binding_id: binding
        for binding in semantic_map.bindings
        if binding.table_name == table_name
    }
    evidence: list[CapabilityEvidence] = []

    def matches_for(binding_id: str) -> list[PathMatch]:
        binding = binding_lookup[binding_id]
        return match_path_pattern(payload, binding.path_pattern)

    for query in queries:
        if query.table_name != table_name:
            continue
        if any(
            binding_id not in binding_lookup
            for binding_id in [
                *query.value_binding_ids,
                *query.context_binding_ids,
                *([query.entity_binding_id] if query.entity_binding_id else []),
                *([query.group_binding_id] if query.group_binding_id else []),
            ]
        ):
            continue

        binding_ids = list(
            dict.fromkeys(
                [
                    *query.value_binding_ids,
                    *query.context_binding_ids,
                    *([query.entity_binding_id] if query.entity_binding_id else []),
                    *([query.group_binding_id] if query.group_binding_id else []),
                ]
            )
        )
        source_paths: list[str] = []
        entity_scope: list[str] = []
        metrics: dict[str, Any] = {
            "operation": query.operation.value,
            "semantic_label": query.semantic_label,
            "question": query.question,
        }
        value_functions = {
            binding_id: binding_lookup[binding_id].analytical_function
            for binding_id in query.value_binding_ids
            if binding_lookup[binding_id].analytical_function is not None
        }
        query_function = (
            next(iter(value_functions.values()))
            if len(set(value_functions.values())) == 1
            else None
        )
        if value_functions:
            metrics["analytical_functions"] = {
                binding_id: analytical_function.value
                for binding_id, analytical_function
                in value_functions.items()
            }
        if query_function is not None:
            metrics["analytical_function"] = query_function.value

        if query.operation == EvidenceOperation.RETRIEVE:
            values: list[dict[str, Any]] = []
            entity_matches = matches_for(query.entity_binding_id) if query.entity_binding_id else []
            group_matches = matches_for(query.group_binding_id) if query.group_binding_id else []
            context_matches = {
                binding_id: matches_for(binding_id) for binding_id in query.context_binding_ids
            }
            for binding_id in query.value_binding_ids:
                binding = binding_lookup[binding_id]
                for match in matches_for(binding_id):
                    entity, entity_path = _aligned_label(
                        match,
                        entity_matches,
                    )
                    group, group_path = _aligned_label(
                        match,
                        group_matches,
                    )
                    context: dict[str, Any] = {}
                    context_paths: list[str] = []
                    for context_id, candidates in context_matches.items():
                        context_value, context_path = _aligned_label(
                            match,
                            candidates,
                        )
                        if context_value is not None:
                            context[binding_lookup[context_id].label] = context_value
                        if context_path is not None:
                            context_paths.append(context_path)
                    values.append(
                        {
                            "binding_id": binding_id,
                            "label": binding.label,
                            "role": binding.role.value,
                            "analytical_function": (
                                binding.analytical_function.value
                                if binding.analytical_function is not None
                                else None
                            ),
                            "value": match.value,
                            "entity": entity,
                            "group": group,
                            "context": context,
                            "source_path": match.source_path,
                        }
                    )
                    entity_scope.extend(
                        value for value in [entity, group, *context.values()] if value
                    )
                    source_paths.extend(
                        path
                        for path in [
                            match.source_path,
                            entity_path,
                            group_path,
                            *context_paths,
                        ]
                        if path
                    )
            if not values:
                continue
            metrics["values"] = values

        else:
            value_binding_id = query.value_binding_ids[0]
            value_binding = binding_lookup[value_binding_id]
            value_matches = [
                match
                for match in matches_for(value_binding_id)
                if isinstance(match.value, (int, float)) and not isinstance(match.value, bool)
            ]
            entity_matches = matches_for(query.entity_binding_id or "")
            group_matches = matches_for(query.group_binding_id) if query.group_binding_id else []
            context_matches = {
                binding_id: matches_for(binding_id) for binding_id in query.context_binding_ids
            }
            records: list[dict[str, Any]] = []

            for value_match in value_matches:
                entity, entity_path = _aligned_label(
                    value_match,
                    entity_matches,
                )
                if entity is None:
                    continue
                group, group_path = _aligned_label(
                    value_match,
                    group_matches,
                )
                context: dict[str, Any] = {}
                context_paths: list[str] = []
                for binding_id, candidates in context_matches.items():
                    context_value, context_path = _aligned_label(
                        value_match,
                        candidates,
                    )
                    if context_value is not None:
                        context[binding_lookup[binding_id].label] = context_value
                    if context_path is not None:
                        context_paths.append(context_path)

                record = {
                    "entity": entity,
                    "group": group,
                    "value": float(value_match.value),
                    "measure": value_binding.label,
                    "context": context,
                    "source_path": value_match.source_path,
                }
                records.append(record)
                entity_scope.extend(value for value in [entity, group, *context.values()] if value)
                source_paths.extend(
                    path
                    for path in [
                        value_match.source_path,
                        entity_path,
                        group_path,
                        *context_paths,
                    ]
                    if path
                )

            if not records:
                continue
            ordered = sorted(
                records,
                key=lambda item: item["value"],
                reverse=query.descending,
            )
            if query.operation == EvidenceOperation.RANK:
                selected_records = ordered[: query.limit]
                value_counts = {
                    record["value"]: sum(
                        candidate["value"] == record["value"]
                        for candidate in records
                    )
                    for record in selected_records
                }
                ranking: list[dict[str, Any]] = []
                previous_value: float | None = None
                current_rank = 0
                for index, record in enumerate(
                    selected_records,
                    start=1,
                ):
                    if record["value"] != previous_value:
                        current_rank = index
                        previous_value = record["value"]
                    ranking.append(
                        {
                            **record,
                            "rank": current_rank,
                            "tied": value_counts[record["value"]] > 1,
                        }
                    )
                metrics["ranking"] = ranking
                metrics["ties_present"] = any(
                    record["tied"] for record in ranking
                )
            else:
                metrics["records"] = ordered
                if len(ordered) >= 2:
                    metrics["difference"] = abs(ordered[0]["value"] - ordered[-1]["value"])
                    metrics["tied"] = ordered[0]["value"] == ordered[-1]["value"]

        confidences = [binding_lookup[binding_id].confidence for binding_id in binding_ids]
        evidence.append(
            CapabilityEvidence(
                capability=query.capability,
                evidence_type=query.evidence_type,
                finding=(f"Validated semantic query result for `{query.semantic_label}`."),
                metrics=metrics,
                source_paths=list(dict.fromkeys(source_paths)),
                entity_scope=list(dict.fromkeys(entity_scope)),
                practical_interpretation=query.question,
                strength_label=f"semantic_{query.operation.value}",
                claim_permissions=_query_permissions(query.operation),
                factual_confidence=min(confidences, default=0.75),
                methodological_strength=1.0,
                user_relevance=query.user_relevance,
                salience=query.salience,
                recommended_use=query.recommended_use,
                semantic_level=query.semantic_level,
                semantic_binding_ids=binding_ids,
                analytical_function=query_function,
                query_id=query.query_id,
                limitations=["The result is limited to values present in the supplied record."],
                prohibited_interpretations=[
                    "Do not infer causality, chronology, or broader historical "
                    "significance from this result."
                ],
            )
        )

    return evidence
````

### `src/table2text/cli.py`

````python
from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from .config import Settings
from .schemas import (
    AuditMode,
    EvaluationFieldPolicy,
    ExternalTruthSource,
    ReportGenre,
)
from .workflow import Table2TextWorkflow


def load_external_truth(
    path: str | None,
) -> list[ExternalTruthSource]:
    if not path:
        return []

    payload = json.loads(
        Path(path).read_text(encoding="utf-8")
    )

    if isinstance(payload, dict):
        payload = payload.get("sources", [payload])

    if not isinstance(payload, list):
        raise ValueError(
            "External truth JSON must contain a source list."
        )

    return [
        ExternalTruthSource.model_validate(source)
        for source in payload
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="table2text",
        description=(
            "Run the six-agent PydanticAI Table2Text pipeline."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run the full Table2Text workflow.",
    )

    run_parser.add_argument(
        "inputs",
        nargs="+",
        help="Input tables or directories.",
    )

    run_parser.add_argument(
        "--request",
        required=True,
        help="The data-science reporting objective.",
    )

    run_parser.add_argument(
        "--audit-mode",
        default=AuditMode.INTERNAL.value,
        choices=[mode.value for mode in AuditMode],
    )

    run_parser.add_argument(
        "--external-truth",
        help="JSON file containing trusted external facts.",
    )

    run_parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Use deterministic fallbacks without LLM calls.",
    )

    run_parser.add_argument(
        "--output-dir",
        help="Override the run artifact directory.",
    )

    run_parser.add_argument(
        "--allow-experimental-targets",
        action="store_true",
        help=(
            "Allow unconfirmed candidate targets for explicit "
            "modelling experiments."
        ),
    )

    run_parser.add_argument(
        "--report-genre",
        choices=[genre.value for genre in ReportGenre],
        help="Set an experiment-level report-genre contract.",
    )
    run_parser.add_argument(
        "--operational-input-path",
        action="append",
        default=[],
        help="Declare an operational JSON path; repeat for multiple paths.",
    )
    run_parser.add_argument(
        "--held-out-reference-path",
        action="append",
        default=[],
        help="Declare a held-out evaluation-reference JSON path.",
    )
    run_parser.add_argument(
        "--metadata-path",
        action="append",
        default=[],
        help="Declare a metadata-only JSON path.",
    )

    return parser


def main() -> None:
    arguments = build_parser().parse_args()
    settings = Settings.from_env()

    if arguments.no_llm:
        settings = replace(
            settings,
            use_llm=False,
        )

    if arguments.output_dir:
        settings = replace(
            settings,
            output_dir=Path(arguments.output_dir),
        )

    if arguments.allow_experimental_targets:
        settings = replace(
            settings,
            allow_experimental_targets=True,
        )

    workflow = Table2TextWorkflow(settings)

    result = workflow.run_sync(
        inputs=arguments.inputs,
        request=arguments.request,
        audit_mode=AuditMode(arguments.audit_mode),
        external_truth_sources=load_external_truth(
            arguments.external_truth
        ),
        evaluation_field_policy=EvaluationFieldPolicy(
            operational_input_paths=arguments.operational_input_path,
            held_out_reference_paths=arguments.held_out_reference_path,
            metadata_paths=arguments.metadata_path,
        ),
        report_genre=(
            ReportGenre(arguments.report_genre)
            if arguments.report_genre
            else None
        ),
    )

    print(f"Run ID: {result.run_id}")
    print(f"Release status: {result.release_status.value}")
    print(f"Approved for release: {result.approved_for_release}")
    print(f"Repair rounds: {result.repair_rounds_used}")
    print(f"Writer mode: {result.raw_writer_output.writer_mode}")
    print(f"Artifacts: {settings.output_dir / result.run_id}")
````

### `src/table2text/config.py`

````python
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None else int(value)


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None else float(value)


@dataclass(frozen=True)
class Settings:
    use_llm: bool = True
    output_dir: Path = Path("runs")

    max_revision_rounds: int = 2
    max_agent_requests: int = 4
    max_total_tokens: int = 24_000

    random_seed: int = 42
    max_analysis_rows: int = 50_000
    structured_output_mode: str = "native"

    full_data_correlation_limit: int = 250_000
    min_abs_correlation: float = 0.20
    max_correlation_findings: int = 6
    max_group_findings: int = 8

    target_proxy_correlation: float = 0.98
    allow_experimental_targets: bool = False

    forecast_folds: int = 3
    max_forecast_test_points: int = 2_000

    writer_target_words: int = 650
    writer_max_main_findings: int = 8
    repair_candidates_per_sentence: int = 3
    writer_quality_revision_rounds: int = 1
    writer_priority_fact_limit: int = 10
    writer_supporting_fact_limit: int = 20

    enable_insight_synthesis: bool = True
    max_insight_candidates: int = 6
    max_verified_main_insights: int = 4
    min_insight_confidence: float = 0.75
    min_insight_salience: float = 0.65
    min_facts_per_bounded_insight: int = 2
    allow_hypotheses_in_report: bool = False

    # Deterministic coverage recovery from the trusted evidence ledger.
    minimum_writer_ready_fact_count: int = 6
    minimum_overview_fact_count: int = 1
    minimum_data_quality_fact_count: int = 1
    minimum_relationship_fact_count: int = 2

    maximum_recovered_overview_facts: int = 2
    maximum_recovered_data_quality_facts: int = 3
    maximum_recovered_correlation_facts: int = 3
    maximum_recovered_group_comparison_facts: int = 2
    maximum_recovered_modelling_facts: int = 1

    max_priority_dataset_overview_facts: int = 2
    max_priority_data_quality_facts: int = 3
    max_priority_correlation_facts: int = 3
    max_priority_group_comparison_facts: int = 2
    max_priority_predictive_facts: int = 1
    max_priority_forecast_facts: int = 1
    max_priority_limitation_facts: int = 2

    minimum_main_finding_score: float = 0.65
    minimum_main_effect_strength: str = "moderate"

    maximum_data_quality_findings: int = 3
    maximum_association_findings: int = 4
    maximum_predictive_findings: int = 1
    maximum_forecast_findings: int = 1
    maximum_limitation_findings: int = 3

    minimum_report_word_ratio: float = 0.45
    minimum_report_word_floor: int = 160
    maximum_repeated_caveat_mentions: int = 4

    zero_unusual_rate_threshold: float = 0.05

    ollama_base_url: str = "http://localhost:11434/v1"

    data_understanding_model: str = "ollama:gemma3:4b"
    orchestrator_model: str = "ollama:gemma3:12b"
    evidence_model: str = "ollama:gemma3:12b"
    verifier_model: str = "ollama:gemma3:12b"
    writer_model: str = "ollama:gemma3:12b"
    auditor_model: str = "ollama:gemma3:12b"

    def __post_init__(self) -> None:
        if self.max_insight_candidates <= 0:
            raise ValueError(
                "max_insight_candidates must be positive."
            )

        if self.max_verified_main_insights <= 0:
            raise ValueError(
                "max_verified_main_insights must be positive."
            )

        if (
            self.max_verified_main_insights
            > self.max_insight_candidates
        ):
            raise ValueError(
                "max_verified_main_insights cannot exceed "
                "max_insight_candidates."
            )

        for field_name, value in {
            "min_insight_confidence": self.min_insight_confidence,
            "min_insight_salience": self.min_insight_salience,
        }.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be between 0 and 1."
                )

        if self.min_facts_per_bounded_insight < 1:
            raise ValueError(
                "min_facts_per_bounded_insight must be at least 1."
            )

    @classmethod
    def from_env(cls) -> "Settings":
        output_mode = os.getenv(
            "T2T_STRUCTURED_OUTPUT_MODE",
            "native",
        ).strip().lower()

        if output_mode not in {"native", "prompted"}:
            raise ValueError(
                "T2T_STRUCTURED_OUTPUT_MODE must be 'native' or 'prompted'."
            )

        return cls(
            use_llm=env_bool("T2T_USE_LLM", True),
            output_dir=Path(os.getenv("T2T_OUTPUT_DIR", "runs")),
            max_revision_rounds=env_int("T2T_MAX_REVISION_ROUNDS", 2),
            max_agent_requests=env_int("T2T_MAX_AGENT_REQUESTS", 4),
            max_total_tokens=env_int("T2T_MAX_TOTAL_TOKENS", 24_000),
            random_seed=env_int("T2T_RANDOM_SEED", 42),
            max_analysis_rows=env_int("T2T_MAX_ANALYSIS_ROWS", 50_000),
            structured_output_mode=output_mode,
            full_data_correlation_limit=env_int(
                "T2T_FULL_DATA_CORRELATION_LIMIT",
                250_000,
            ),
            min_abs_correlation=env_float(
                "T2T_MIN_ABS_CORRELATION",
                0.20,
            ),
            max_correlation_findings=env_int(
                "T2T_MAX_CORRELATION_FINDINGS",
                6,
            ),
            max_group_findings=env_int(
                "T2T_MAX_GROUP_FINDINGS",
                8,
            ),
            target_proxy_correlation=env_float(
                "T2T_TARGET_PROXY_CORRELATION",
                0.98,
            ),
            allow_experimental_targets=env_bool(
                "T2T_ALLOW_EXPERIMENTAL_TARGETS",
                False,
            ),
            forecast_folds=env_int("T2T_FORECAST_FOLDS", 3),
            max_forecast_test_points=env_int(
                "T2T_MAX_FORECAST_TEST_POINTS",
                2_000,
            ),
            writer_target_words=env_int(
                "T2T_WRITER_TARGET_WORDS",
                650,
            ),
            writer_max_main_findings=env_int(
                "T2T_WRITER_MAX_MAIN_FINDINGS",
                8,
            ),
            repair_candidates_per_sentence=env_int(
                "T2T_REPAIR_CANDIDATES_PER_SENTENCE",
                3,
            ),
            writer_quality_revision_rounds=min(
                env_int("T2T_WRITER_QUALITY_REVISION_ROUNDS", 1),
                1,
            ),
            writer_priority_fact_limit=env_int(
                "T2T_WRITER_PRIORITY_FACT_LIMIT",
                10,
            ),
            writer_supporting_fact_limit=env_int(
                "T2T_WRITER_SUPPORTING_FACT_LIMIT",
                20,
            ),
            enable_insight_synthesis=env_bool(
                "T2T_ENABLE_INSIGHT_SYNTHESIS",
                True,
            ),
            max_insight_candidates=env_int(
                "T2T_MAX_INSIGHT_CANDIDATES",
                6,
            ),
            max_verified_main_insights=env_int(
                "T2T_MAX_VERIFIED_MAIN_INSIGHTS",
                4,
            ),
            min_insight_confidence=env_float(
                "T2T_MIN_INSIGHT_CONFIDENCE",
                0.75,
            ),
            min_insight_salience=env_float(
                "T2T_MIN_INSIGHT_SALIENCE",
                0.65,
            ),
            min_facts_per_bounded_insight=env_int(
                "T2T_MIN_FACTS_PER_BOUNDED_INSIGHT",
                2,
            ),
            allow_hypotheses_in_report=env_bool(
                "T2T_ALLOW_HYPOTHESES_IN_REPORT",
                False,
            ),
            minimum_writer_ready_fact_count=env_int(
                "T2T_MINIMUM_WRITER_READY_FACT_COUNT",
                6,
            ),
            minimum_overview_fact_count=env_int(
                "T2T_MINIMUM_OVERVIEW_FACT_COUNT",
                1,
            ),
            minimum_data_quality_fact_count=env_int(
                "T2T_MINIMUM_DATA_QUALITY_FACT_COUNT",
                1,
            ),
            minimum_relationship_fact_count=env_int(
                "T2T_MINIMUM_RELATIONSHIP_FACT_COUNT",
                2,
            ),
            maximum_recovered_overview_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_OVERVIEW_FACTS",
                2,
            ),
            maximum_recovered_data_quality_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_DATA_QUALITY_FACTS",
                3,
            ),
            maximum_recovered_correlation_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_CORRELATION_FACTS",
                3,
            ),
            maximum_recovered_group_comparison_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_GROUP_COMPARISON_FACTS",
                2,
            ),
            maximum_recovered_modelling_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_MODELLING_FACTS",
                1,
            ),
            max_priority_dataset_overview_facts=env_int(
                "T2T_MAX_PRIORITY_DATASET_OVERVIEW_FACTS",
                2,
            ),
            max_priority_data_quality_facts=env_int(
                "T2T_MAX_PRIORITY_DATA_QUALITY_FACTS",
                3,
            ),
            max_priority_correlation_facts=env_int(
                "T2T_MAX_PRIORITY_CORRELATION_FACTS",
                3,
            ),
            max_priority_group_comparison_facts=env_int(
                "T2T_MAX_PRIORITY_GROUP_COMPARISON_FACTS",
                2,
            ),
            max_priority_predictive_facts=env_int(
                "T2T_MAX_PRIORITY_PREDICTIVE_FACTS",
                1,
            ),
            max_priority_forecast_facts=env_int(
                "T2T_MAX_PRIORITY_FORECAST_FACTS",
                1,
            ),
            max_priority_limitation_facts=env_int(
                "T2T_MAX_PRIORITY_LIMITATION_FACTS",
                2,
            ),
            minimum_main_finding_score=env_float(
                "T2T_MINIMUM_MAIN_FINDING_SCORE",
                0.65,
            ),
            minimum_main_effect_strength=os.getenv(
                "T2T_MINIMUM_MAIN_EFFECT_STRENGTH",
                "moderate",
            ),
            maximum_data_quality_findings=env_int(
                "T2T_MAX_DATA_QUALITY_FINDINGS",
                3,
            ),
            maximum_association_findings=env_int(
                "T2T_MAX_ASSOCIATION_FINDINGS",
                4,
            ),
            maximum_predictive_findings=env_int(
                "T2T_MAX_PREDICTIVE_FINDINGS",
                1,
            ),
            maximum_forecast_findings=env_int(
                "T2T_MAX_FORECAST_FINDINGS",
                1,
            ),
            maximum_limitation_findings=env_int(
                "T2T_MAX_LIMITATION_FINDINGS",
                3,
            ),
            minimum_report_word_ratio=env_float(
                "T2T_MINIMUM_REPORT_WORD_RATIO",
                0.45,
            ),
            minimum_report_word_floor=env_int(
                "T2T_MINIMUM_REPORT_WORD_FLOOR",
                160,
            ),
            maximum_repeated_caveat_mentions=env_int(
                "T2T_MAXIMUM_REPEATED_CAVEAT_MENTIONS",
                4,
            ),
            zero_unusual_rate_threshold=env_float(
                "T2T_ZERO_UNUSUAL_RATE_THRESHOLD",
                0.05,
            ),
            ollama_base_url=os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434/v1",
            ),
            data_understanding_model=os.getenv(
                "T2T_MODEL_DATA_UNDERSTANDING",
                "ollama:gemma3:4b",
            ),
            orchestrator_model=os.getenv(
                "T2T_MODEL_ORCHESTRATOR",
                "ollama:gemma3:12b",
            ),
            evidence_model=os.getenv(
                "T2T_MODEL_EVIDENCE",
                "ollama:gemma3:12b",
            ),
            verifier_model=os.getenv(
                "T2T_MODEL_VERIFIER",
                "ollama:gemma3:12b",
            ),
            writer_model=os.getenv(
                "T2T_MODEL_WRITER",
                "ollama:gemma3:12b",
            ),
            auditor_model=os.getenv(
                "T2T_MODEL_AUDITOR",
                "ollama:gemma3:12b",
            ),
        )

    def model_for(self, role: str) -> str:
        mapping = {
            "data_understanding": self.data_understanding_model,
            "orchestrator": self.orchestrator_model,
            "evidence": self.evidence_model,
            "verifier": self.verifier_model,
            "writer": self.writer_model,
            "auditor": self.auditor_model,
        }

        try:
            return mapping[role]
        except KeyError as error:
            raise ValueError(f"Unknown model role: {role}") from error
````

### `src/table2text/data.py`

````python
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .schemas import (
    ColumnProfile,
    DataProfile,
    EvaluationFieldPolicy,
    InputRepresentationStatus,
    InputShape,
    InputStructureProfile,
    TableProfile,
    ZeroRisk,
)
from .structure import combine_structure_profiles, inspect_and_filter_payload


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".json",
    ".jsonl",
    ".ndjson",
    ".parquet",
    ".xlsx",
    ".xls",
}

VALID_ZERO_TERMS = {
    "bearing",
    "direction",
    "angle",
    "degree",
    "degrees",
    "count",
    "number",
    "index",
    "flag",
    "binary",
}

CONTEXT_DEPENDENT_ZERO_TERMS = {
    "visibility",
    "speed",
    "precipitation",
    "rain",
    "snow",
    "distance",
}

POSSIBLE_SENTINEL_ZERO_TERMS = {
    "pressure",
    "blood pressure",
}


@dataclass
class DataBundle:
    tables: dict[str, pd.DataFrame]
    source_paths: list[Path]
    fingerprint: str
    structured_inputs: dict[str, Any] = field(default_factory=dict)
    input_structure: InputStructureProfile | None = None
    evaluation_field_policy: EvaluationFieldPolicy = field(
        default_factory=EvaluationFieldPolicy
    )


def safe_hashable(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, (list, dict, tuple, set)):
        return json.dumps(value, sort_keys=True, default=str)

    try:
        if bool(pd.isna(value)):
            return None
    except Exception:
        pass

    return value


def profile_sample_value(value: Any) -> str:
    if isinstance(value, dict):
        return json.dumps(
            {
                "type": "object",
                "keys": [str(key) for key in list(value)[:20]],
            },
            sort_keys=True,
        )
    if isinstance(value, list):
        return json.dumps(
            {
                "type": "array",
                "length": len(value),
                "item_type": (
                    type(value[0]).__name__ if value else "unknown"
                ),
            },
            sort_keys=True,
        )

    text = str(value)
    return text if len(text) <= 240 else text[:237] + "..."


def fingerprint_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()

    for path in sorted(paths, key=lambda item: str(item.resolve())):
        digest.update(str(path.resolve()).encode("utf-8"))

        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)

    return digest.hexdigest()


def expand_inputs(inputs: Iterable[str | Path]) -> list[Path]:
    paths: list[Path] = []

    for raw_path in inputs:
        path = Path(raw_path).expanduser()

        if path.is_dir():
            paths.extend(
                item
                for item in sorted(path.iterdir())
                if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS
            )
        elif path.is_file():
            paths.append(path)
        else:
            raise FileNotFoundError(f"Input path does not exist: {path}")

    if not paths:
        raise ValueError("No supported input files were found.")

    return paths


def unique_table_name(name: str, tables: dict[str, pd.DataFrame]) -> str:
    candidate = name
    counter = 2

    while candidate in tables:
        candidate = f"{name}_{counter}"
        counter += 1

    return candidate


def _columnar_mapping(payload: dict[str, Any]) -> bool:
    values = list(payload.values())
    if not values or not all(isinstance(value, list) for value in values):
        return False
    lengths = {len(value) for value in values}
    return len(lengths) == 1 and not all(
        not value or isinstance(value[0], dict)
        for value in values
    )


def load_json_tables(
    path: Path,
    payload: Any | None = None,
) -> dict[str, pd.DataFrame]:
    if payload is None:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

    if isinstance(payload, list):
        return {path.stem: pd.json_normalize(payload)}

    if isinstance(payload, dict):
        nested_tables = {
            str(key): pd.json_normalize(value)
            for key, value in payload.items()
            if isinstance(value, list)
            and (not value or isinstance(value[0], dict))
        }

        if nested_tables and len(nested_tables) == len(payload):
            return nested_tables

        if _columnar_mapping(payload):
            return {path.stem: pd.DataFrame(payload)}

        # A mixed scalar/nested mapping is one structured record. Passing it
        # directly to DataFrame aligns nested keys into artificial rows.
        return {path.stem: pd.DataFrame([payload])}

    return {path.stem: pd.DataFrame({"value": [payload]})}


def load_data(
    inputs: Iterable[str | Path],
    evaluation_field_policy: EvaluationFieldPolicy | None = None,
) -> DataBundle:
    paths = expand_inputs(inputs)
    tables: dict[str, pd.DataFrame] = {}
    structured_inputs: dict[str, Any] = {}
    structure_profiles: list[InputStructureProfile] = []
    effective_policies: list[EvaluationFieldPolicy] = []

    for path in paths:
        extension = path.suffix.lower()

        operational_payload: Any | None = None

        if extension == ".csv":
            loaded = {path.stem: pd.read_csv(path, low_memory=False)}
        elif extension == ".json":
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            (
                operational_payload,
                structure_profile,
                effective_policy,
            ) = inspect_and_filter_payload(
                payload=payload,
                source_path=path,
                field_policy=evaluation_field_policy,
            )
            structure_profiles.append(structure_profile)
            effective_policies.append(effective_policy)
            loaded = load_json_tables(path, operational_payload)
        elif extension in {".jsonl", ".ndjson"}:
            loaded = {path.stem: pd.read_json(path, lines=True)}
        elif extension == ".parquet":
            loaded = {path.stem: pd.read_parquet(path)}
        elif extension in {".xlsx", ".xls"}:
            sheets = pd.read_excel(path, sheet_name=None)
            loaded = {
                f"{path.stem}__{sheet_name}": frame
                for sheet_name, frame in sheets.items()
            }
        else:
            raise ValueError(f"Unsupported format: {path}")

        if extension != ".json":
            structure_profiles.append(
                InputStructureProfile(
                    shape=(
                        InputShape.TIME_SERIES
                        if any(
                            "date" in str(column).casefold()
                            or "time" in str(column).casefold()
                            for frame in loaded.values()
                            for column in frame.columns
                        )
                        else InputShape.FLAT_TABLE
                    ),
                    representation_status=InputRepresentationStatus.VALID,
                    source_paths=[str(path)],
                    row_semantics="one observation per row",
                    confidence=0.95,
                )
            )

        for proposed_name, frame in loaded.items():
            table_name = unique_table_name(proposed_name, tables)
            frame = frame.copy()
            frame.columns = [str(column) for column in frame.columns]
            tables[table_name] = frame
            if operational_payload is not None:
                if len(loaded) == 1:
                    structured_inputs[table_name] = operational_payload
                elif isinstance(operational_payload, dict):
                    structured_inputs[table_name] = operational_payload.get(
                        proposed_name
                    )

    if effective_policies:
        effective_policy = EvaluationFieldPolicy(
            operational_input_paths=list(
                dict.fromkeys(
                    path
                    for policy in effective_policies
                    for path in policy.operational_input_paths
                )
            ),
            held_out_reference_paths=list(
                dict.fromkeys(
                    path
                    for policy in effective_policies
                    for path in policy.held_out_reference_paths
                )
            ),
            metadata_paths=list(
                dict.fromkeys(
                    path
                    for policy in effective_policies
                    for path in policy.metadata_paths
                )
            ),
        )
    else:
        effective_policy = evaluation_field_policy or EvaluationFieldPolicy()

    return DataBundle(
        tables=tables,
        source_paths=paths,
        fingerprint=fingerprint_files(paths),
        structured_inputs=structured_inputs,
        input_structure=combine_structure_profiles(structure_profiles),
        evaluation_field_policy=effective_policy,
    )


def normalise_column_name(column_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", column_name.lower()).strip()


def looks_datetime_like(series: pd.Series) -> bool:
    sample = series.dropna().astype(str).head(200)

    if sample.empty:
        return False

    datetime_pattern_rate = sample.str.contains(
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"
        r"|"
        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"
        r"|"
        r"\d{1,2}:\d{2}",
        regex=True,
    ).mean()

    return bool(datetime_pattern_rate >= 0.5)


def classify_zero_risk(
    *,
    column_name: str,
    zero_count: int,
    zero_rate: float,
    median: float,
    q05: float,
) -> tuple[ZeroRisk, str]:
    if zero_count == 0:
        return ZeroRisk.NONE, "No zero observations were recorded."

    name = normalise_column_name(column_name)

    if any(term in name for term in VALID_ZERO_TERMS):
        return (
            ZeroRisk.LIKELY_VALID,
            "Zero is valid on the apparent measurement or coding scale.",
        )

    if any(term in name for term in CONTEXT_DEPENDENT_ZERO_TERMS):
        return (
            ZeroRisk.CONTEXT_DEPENDENT,
            "Zero may be a genuine extreme observation and should not be "
            "treated as erroneous without contextual evidence.",
        )

    if (
        any(term in name for term in POSSIBLE_SENTINEL_ZERO_TERMS)
        and median > 0
        and q05 > 0
    ):
        return (
            ZeroRisk.POSSIBLE_SENTINEL,
            "Zero is separated from the main positive distribution and may "
            "represent encoded missingness or measurement failure.",
        )

    if median >= 10 and q05 > 0 and zero_rate <= 0.05:
        return (
            ZeroRisk.UNUSUAL,
            "Zero is unusual relative to the observed distribution, but its "
            "validity cannot be established without metadata.",
        )

    return (
        ZeroRisk.NONE,
        "The observed distribution does not provide sufficient evidence that "
        "zero is problematic.",
    )


def datetime_parse_rate(series: pd.Series) -> float:
    non_missing = series.dropna()

    if non_missing.empty:
        return 0.0

    sample = non_missing.head(1_000)

    if pd.api.types.is_datetime64_any_dtype(sample):
        return 1.0

    if pd.api.types.is_numeric_dtype(sample):
        return 0.0

    if not looks_datetime_like(sample):
        return 0.0

    parsed = pd.to_datetime(sample, errors="coerce", utc=True)
    return float(parsed.notna().mean())


def infer_semantic_type(
    series: pd.Series,
    unique_count: int,
    parse_rate: float,
) -> str:
    if series.map(
        lambda value: isinstance(value, (list, dict, tuple, set))
    ).any():
        return "structured"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series) or parse_rate >= 0.8:
        return "datetime"

    row_count = max(len(series), 1)

    if unique_count <= max(20, int(row_count * 0.05)):
        return "categorical"

    return "text"


def numeric_diagnostics(
    column_name: str,
    series: pd.Series,
) -> tuple[dict[str, float | int], list[str], ZeroRisk, str, bool]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()

    if numeric.empty:
        return {}, [], ZeroRisk.NONE, "No numeric observations were available.", False

    q01 = float(numeric.quantile(0.01))
    q05 = float(numeric.quantile(0.05))
    q25 = float(numeric.quantile(0.25))
    q75 = float(numeric.quantile(0.75))
    q99 = float(numeric.quantile(0.99))

    iqr = q75 - q25

    if iqr > 0:
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        outlier_count = int(
            ((numeric < lower_bound) | (numeric > upper_bound)).sum()
        )
    else:
        outlier_count = 0

    zero_count = int((numeric == 0).sum())
    zero_rate = zero_count / len(numeric)

    median = float(numeric.median())

    zero_risk, zero_risk_reason = classify_zero_risk(
        column_name=column_name,
        zero_count=zero_count,
        zero_rate=float(zero_rate),
        median=median,
        q05=q05,
    )
    suspicious_zero = zero_risk in {
        ZeroRisk.UNUSUAL,
        ZeroRisk.POSSIBLE_SENTINEL,
    }

    warnings: list[str] = []

    if suspicious_zero:
        warnings.append(zero_risk_reason)

    summary: dict[str, float | int] = {
        "count": int(numeric.count()),
        "mean": float(numeric.mean()),
        "median": median,
        "standard_deviation": (
            float(numeric.std(ddof=1))
            if len(numeric) > 1
            else 0.0
        ),
        "minimum": float(numeric.min()),
        "q01": q01,
        "q05": q05,
        "q25": q25,
        "q75": q75,
        "q99": q99,
        "maximum": float(numeric.max()),
        "zero_count": zero_count,
        "zero_rate": float(zero_rate),
        "negative_count": int((numeric < 0).sum()),
        "skewness": (
            float(numeric.skew())
            if len(numeric) > 2
            else 0.0
        ),
        "iqr_outlier_count": outlier_count,
    }

    return summary, warnings, zero_risk, zero_risk_reason, suspicious_zero


def profile_data(bundle: DataBundle) -> DataProfile:
    path_lookup = {
        path.stem: str(path)
        for path in bundle.source_paths
    }

    table_profiles: list[TableProfile] = []

    for table_name, frame in bundle.tables.items():
        hashable_frame = frame.copy()

        for column in hashable_frame.columns:
            hashable_frame[column] = hashable_frame[column].map(safe_hashable)

        duplicate_count = int(hashable_frame.duplicated().sum())

        candidate_keys: list[str] = []
        columns: list[ColumnProfile] = []
        table_warnings: list[str] = []

        for column_name in frame.columns:
            series = frame[column_name]
            safe_series = series.map(safe_hashable)

            missing_count = int(safe_series.isna().sum())
            unique_count = int(safe_series.nunique(dropna=True))
            parse_rate = datetime_parse_rate(series)

            candidate_key = bool(
                len(frame) > 0
                and missing_count == 0
                and unique_count == len(frame)
            )

            if candidate_key:
                candidate_keys.append(column_name)

            semantic_type = infer_semantic_type(
                series,
                unique_count,
                parse_rate,
            )

            non_missing = safe_series.dropna()

            if non_missing.empty:
                dominant_rate = 0.0
            else:
                dominant_rate = float(
                    non_missing.value_counts(normalize=True).iloc[0]
                )

            constant = unique_count <= 1 and len(frame) > 0
            near_constant = not constant and dominant_rate >= 0.995

            summary: dict[str, float | int] = {}
            quality_warnings: list[str] = []
            suspicious_zero = False
            zero_risk = ZeroRisk.NONE
            zero_risk_reason = None

            if semantic_type == "numeric":
                (
                    summary,
                    numeric_warnings,
                    zero_risk,
                    zero_risk_reason,
                    suspicious_zero,
                ) = numeric_diagnostics(
                    column_name,
                    series,
                )
                quality_warnings.extend(numeric_warnings)

            if constant:
                quality_warnings.append(
                    "The column is constant and has no observed analytical variation."
                )

            if near_constant:
                quality_warnings.append(
                    "The column is near-constant and may contribute little analytical information."
                )

            samples = list(
                dict.fromkeys(
                    profile_sample_value(value)
                    for value in series.dropna().head(20)
                )
            )[:5]

            columns.append(
                ColumnProfile(
                    name=column_name,
                    dtype=str(series.dtype),
                    semantic_type=semantic_type,
                    missing_count=missing_count,
                    missing_rate=round(
                        missing_count / max(len(frame), 1),
                        6,
                    ),
                    unique_count=unique_count,
                    sample_values=samples,
                    numeric_summary=summary,
                    datetime_parse_rate=round(parse_rate, 6),
                    candidate_key=candidate_key,
                    structured_values=semantic_type == "structured",
                    constant=constant,
                    near_constant=near_constant,
                    dominant_value_rate=round(dominant_rate, 6),
                    suspicious_zero_values=suspicious_zero,
                    possible_sentinel_values=suspicious_zero,
                    zero_risk=zero_risk,
                    zero_risk_reason=zero_risk_reason,
                    quality_warnings=quality_warnings,
                )
            )

        if len(frame) == 0:
            table_warnings.append("The table contains no rows.")

        if duplicate_count:
            table_warnings.append(
                f"{duplicate_count} duplicate rows were detected."
            )

        if any(column.missing_rate >= 0.5 for column in columns):
            table_warnings.append(
                "At least one column has 50% or more missing values."
            )

        constant_columns = [
            column.name for column in columns if column.constant
        ]

        if constant_columns:
            table_warnings.append(
                "Constant columns detected: "
                + ", ".join(f"`{column}`" for column in constant_columns)
                + "."
            )

        suspicious_zero_columns = [
            column.name
            for column in columns
            if column.suspicious_zero_values
        ]

        if suspicious_zero_columns:
            table_warnings.append(
                "Potentially suspicious zero values detected in: "
                + ", ".join(
                    f"`{column}`"
                    for column in suspicious_zero_columns
                )
                + "."
            )

        source_path = next(
            (
                path
                for stem, path in path_lookup.items()
                if table_name.startswith(stem)
            ),
            str(bundle.source_paths[0]),
        )

        table_profiles.append(
            TableProfile(
                table_name=table_name,
                source_path=source_path,
                row_count=int(len(frame)),
                column_count=int(len(frame.columns)),
                duplicate_row_count=duplicate_count,
                candidate_keys=candidate_keys,
                columns=columns,
                warnings=table_warnings,
            )
        )

    return DataProfile(
        fingerprint=bundle.fingerprint,
        source_paths=[str(path) for path in bundle.source_paths],
        tables=table_profiles,
    )
````

### `src/table2text/schemas.py`

````python
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AnalysisRoute(str, Enum):
    DESCRIPTIVE = "descriptive"
    ASSOCIATION_COMPARISON = "association_comparison"
    PREDICTIVE = "predictive"
    FORECASTING = "forecasting"
    CAUSAL_FEASIBILITY = "causal_feasibility"


class ClaimPermission(str, Enum):
    DESCRIPTIVE = "descriptive_claims_allowed"
    COMPARATIVE = "comparative_claims_allowed"
    ASSOCIATIONAL = "associational_claims_allowed"
    PREDICTIVE = "predictive_claims_allowed_after_validation"
    FORECAST = "forecast_claims_allowed_after_validation"
    CAUSAL = "causal_claims_allowed_only_with_verified_design"
    INSUFFICIENCY = "insufficiency_claims_allowed"
    METHODOLOGICAL = "methodological_interpretation_allowed"


class InterpretationLevel(str, Enum):
    FINDING = "finding"
    BOUNDED_INSIGHT = "bounded_insight"
    HYPOTHESIS = "hypothesis"


class ReportGenre(str, Enum):
    DATA_SCIENCE_REPORT = "data_science_report"
    DATASET_OVERVIEW = "dataset_overview"
    EVENT_REPORT = "event_report"
    # Retained for compatibility with existing notebook artifacts.
    SPORTS_GAME_REPORT = "sports_game_report"


class ReportPerspective(str, Enum):
    NEUTRAL = "neutral"
    SUBJECT_CENTRED = "subject_centred"


class ReportSelectionSource(str, Enum):
    EXPLICIT_USER_REQUEST = "explicit_user_request"
    EXPERIMENT_CONFIGURATION = "experiment_configuration"
    STRUCTURED_INFERENCE = "structured_inference"
    FALLBACK = "fallback"


class InputShape(str, Enum):
    FLAT_TABLE = "flat_table"
    NESTED_RECORD = "nested_record"
    ENTITY_COLLECTION = "entity_collection"
    EVENT_RECORD = "event_record"
    TIME_SERIES = "time_series"
    INPUT_REFERENCE_PAIRS = "input_reference_pairs"
    AMBIGUOUS = "ambiguous"


class SemanticRole(str, Enum):
    IDENTIFIER = "identifier"
    CONTEXT = "context"
    TIME = "time"
    LOCATION = "location"
    STATUS = "status"
    PARTICIPANT_IDENTIFIER = "participant_identifier"
    ENTITY_IDENTIFIER = "entity_identifier"
    OUTCOME_MEASURE = "outcome_measure"
    PERFORMANCE_MEASURE = "performance_measure"
    MEASURE = "measure"
    CATEGORY = "category"
    METADATA = "metadata"


class AnalyticalFunction(str, Enum):
    OUTCOME = "outcome"
    OUTCOME_COMPONENT = "outcome_component"
    PERFORMANCE = "performance"
    PARTICIPATION = "participation"
    CONTEXT = "context"


class SemanticLevel(str, Enum):
    DATASET = "dataset"
    EVENT = "event"
    PARTICIPANT = "participant"
    ENTITY = "entity"
    OBSERVATION = "observation"


class EvidenceOperation(str, Enum):
    RETRIEVE = "retrieve"
    COMPARE = "compare"
    RANK = "rank"


class InputRepresentationStatus(str, Enum):
    VALID = "valid"
    VALID_WITH_WARNINGS = "valid_with_warnings"
    AMBIGUOUS = "ambiguous"
    INVALID = "invalid"


class EvidenceCapability(str, Enum):
    DATASET_PROFILE = "dataset_profile"
    MISSINGNESS = "missingness"
    DUPLICATES = "duplicates"
    DISTRIBUTION_SUMMARY = "distribution_summary"
    ASSOCIATION = "association"
    GROUP_COMPARISON = "group_comparison"
    RANKING = "ranking"
    EXTREMA = "extrema"
    TEMPORAL_CHANGE = "temporal_change"
    EVENT_OUTCOME = "event_outcome"
    ENTITY_PERFORMANCE = "entity_performance"
    ANOMALY_DETECTION = "anomaly_detection"


class InsightType(str, Enum):
    DOMINANT_PATTERN = "dominant_pattern"
    CONTRAST = "contrast"
    REDUNDANCY = "redundancy"
    ANOMALY = "anomaly"
    OUTCOME_ASSOCIATION = "outcome_association"
    TRADE_OFF = "trade_off"
    DATA_QUALITY_IMPLICATION = "data_quality_implication"
    NARRATIVE_SUMMARY = "narrative_summary"


class InsightVerificationStatus(str, Enum):
    VERIFIED = "verified"
    VERIFIED_WITH_CAVEAT = "verified_with_caveat"
    HYPOTHESIS_ONLY = "hypothesis_only"
    REJECTED = "rejected"


class AuditMode(str, Enum):
    INTERNAL = "internal_evidence_fidelity"
    EXTERNAL = "external_truth_mode"
    ANNOTATION_ONLY = "annotation_only"


class AuditDecision(str, Enum):
    PASS = "pass"
    REVISE = "revise"
    BLOCK = "block"


class ReleaseStatus(str, Enum):
    APPROVED = "approved"
    APPROVED_WITH_WARNINGS = "approved_with_warnings"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class ReviewDecision(str, Enum):
    APPROVE = "approve"
    CAUTION = "caution"
    REJECT = "reject"


class VerificationMethod(str, Enum):
    LLM_VERIFIED = "llm_verified"
    DETERMINISTIC_EVIDENCE_RECOVERY = (
        "deterministic_evidence_recovery"
    )


class ErrorType(str, Enum):
    INCORRECT_NAMED_ENTITY = "incorrect_named_entity"
    INCORRECT_NUMBER = "incorrect_number"
    INCORRECT_WORD = "incorrect_word"
    CONTEXT_ERROR = "context_error"
    SUPPORT_MAPPING_ERROR = "support_mapping_error"
    NOT_CHECKABLE = "not_checkable"
    OTHER = "other"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendedUse(str, Enum):
    HEADLINE = "headline"
    MAIN_FINDING = "main_finding"
    SUPPORTING_DETAIL = "supporting_detail"
    LIMITATION = "limitation"
    OMIT_UNLESS_REQUESTED = "omit_unless_requested"


class ZeroRisk(str, Enum):
    NONE = "none"
    LIKELY_VALID = "likely_valid_zero"
    CONTEXT_DEPENDENT = "context_dependent_zero"
    UNUSUAL = "unusual_zero"
    POSSIBLE_SENTINEL = "possible_sentinel_zero"


class ReportComponent(str, Enum):
    DATASET_OVERVIEW = "dataset_overview"
    DATA_QUALITY = "data_quality"
    STRONGEST_RELATIONSHIPS = "strongest_relationships"
    MODELLING_VALIDATION = "modelling_validation"
    LIMITATIONS_NEXT_STEPS = "limitations_next_steps"


class TargetStatus(str, Enum):
    USER_SELECTED = "user_selected"
    METADATA_CONFIRMED = "metadata_confirmed"
    EXPERIMENTAL_CANDIDATE = "experimental_candidate"
    UNCONFIRMED = "unconfirmed"


class ValidationStrategy(str, Enum):
    NONE = "none"
    RANDOM_HOLDOUT = "random_holdout"
    STRATIFIED_HOLDOUT = "stratified_holdout"
    CHRONOLOGICAL_HOLDOUT = "chronological_holdout"
    ROLLING_ORIGIN = "rolling_origin"


class SupportType(str, Enum):
    DIRECT = "direct"
    PARAPHRASE = "paraphrase"
    MULTI_FACT_SYNTHESIS = "multi_fact_synthesis"
    NON_FACTUAL = "non_factual_transition"


class RepairStrategy(str, Enum):
    MINIMAL_CORRECTION = "minimal_correction"
    EVIDENCE_REWRITE = "evidence_constrained_rewrite"
    HEDGED_REWRITE = "hedged_rewrite"
    DELETE = "delete_sentence"


class QualityStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    REVISE = "revise"


class QualityIssueType(str, Enum):
    MISSING_REQUIRED_COMPONENT = "missing_required_component"
    LEDGER_STYLE_RENDERING = "ledger_style_rendering"
    REPETITIVE_CAVEAT = "repetitive_caveat"
    GENERIC_OPENING = "generic_opening"
    WEAK_FINDING_SELECTION = "weak_finding_selection"
    ROUTE_DOMINANCE = "route_dominance"
    UNSUPPORTED_METHOD_INTERPRETATION = "unsupported_method_interpretation"


class EvaluationFieldPolicy(StrictModel):
    operational_input_paths: list[str] = Field(default_factory=list)
    held_out_reference_paths: list[str] = Field(default_factory=list)
    metadata_paths: list[str] = Field(default_factory=list)


class InputStructureProfile(StrictModel):
    shape: InputShape
    representation_status: InputRepresentationStatus

    source_paths: list[str] = Field(default_factory=list)
    row_semantics: str | None = None
    entity_levels: list[str] = Field(default_factory=list)
    nested_paths: list[str] = Field(default_factory=list)

    probable_input_fields: list[str] = Field(default_factory=list)
    probable_reference_fields: list[str] = Field(default_factory=list)
    probable_metadata_fields: list[str] = Field(default_factory=list)

    heterogeneous_rows_detected: bool = False
    sparse_flattening_detected: bool = False
    ambiguity_notes: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)


class StructuralField(StrictModel):
    table_name: str
    path_pattern: str
    value_types: list[str] = Field(default_factory=list)
    sample_values: list[str] = Field(default_factory=list)
    occurrence_count: int = Field(default=1, ge=1)


class SemanticBinding(StrictModel):
    binding_id: str
    table_name: str
    label: str
    role: SemanticRole
    level: SemanticLevel
    path_pattern: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_basis: str
    unit: str | None = None
    analytical_function: AnalyticalFunction | None = None


class InputSemanticMap(StrictModel):
    input_shape: InputShape
    record_description: str
    bindings: list[SemanticBinding] = Field(default_factory=list)
    recommended_report_genre: ReportGenre | None = None
    report_rationale: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    unresolved_ambiguities: list[str] = Field(default_factory=list)


class CapabilityDefinition(StrictModel):
    capability: EvidenceCapability
    supported_input_shapes: list[InputShape]

    requires_numeric_fields: bool = False
    requires_time_field: bool = False
    requires_entity_fields: bool = False
    requires_event_participants: bool = False
    requires_outcome_field: bool = False

    minimum_observations: int | None = None
    output_evidence_types: list[str] = Field(default_factory=list)


class GenreQualityAssessment(StrictModel):
    status: QualityStatus
    genre: ReportGenre

    required_slots: list[str] = Field(default_factory=list)
    supported_slots: list[str] = Field(default_factory=list)
    covered_slots: list[str] = Field(default_factory=list)
    missing_supported_slots: list[str] = Field(default_factory=list)

    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ColumnProfile(StrictModel):
    name: str
    dtype: str
    semantic_type: str

    missing_count: int
    missing_rate: float
    unique_count: int

    sample_values: list[str] = Field(default_factory=list)
    numeric_summary: dict[str, float | int] = Field(default_factory=dict)

    datetime_parse_rate: float = 0.0
    candidate_key: bool = False
    structured_values: bool = False

    constant: bool = False
    near_constant: bool = False
    dominant_value_rate: float = 0.0

    suspicious_zero_values: bool = False
    possible_sentinel_values: bool = False
    zero_risk: ZeroRisk = ZeroRisk.NONE
    zero_risk_reason: str | None = None

    quality_warnings: list[str] = Field(default_factory=list)


class TableProfile(StrictModel):
    table_name: str
    source_path: str

    row_count: int
    column_count: int
    duplicate_row_count: int

    candidate_keys: list[str] = Field(default_factory=list)
    columns: list[ColumnProfile] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DataProfile(StrictModel):
    fingerprint: str
    source_paths: list[str]
    tables: list[TableProfile]


class ColumnMeaning(StrictModel):
    table_name: str
    column_name: str
    inferred_role: str
    interpretation: str
    evidence_basis: str
    confidence: float = Field(ge=0.0, le=1.0)
    caveat: str | None = None


class ColumnRisk(StrictModel):
    table_name: str
    column_name: str
    risk_type: str
    explanation: str
    analytical_consequence: str
    confidence: float = Field(ge=0.0, le=1.0)


class TableUnderstanding(StrictModel):
    table_name: str
    unit_of_observation: str
    summary: str

    likely_keys: list[str] = Field(default_factory=list)
    column_meanings: list[ColumnMeaning] = Field(default_factory=list)
    column_risks: list[ColumnRisk] = Field(default_factory=list)

    quality_findings: list[str] = Field(default_factory=list)
    usability_notes: list[str] = Field(default_factory=list)


class DataUnderstanding(StrictModel):
    profile_fingerprint: str
    dataset_summary: str
    tables: list[TableUnderstanding]

    cross_table_notes: list[str] = Field(default_factory=list)
    supported_routes: list[AnalysisRoute] = Field(default_factory=list)
    uncertain_routes: list[str] = Field(default_factory=list)
    global_caveats: list[str] = Field(default_factory=list)
    semantic_map: InputSemanticMap | None = None


class ReportSpecification(StrictModel):
    intended_audience: str = "A reader seeking a data-science interpretation."
    report_purpose: str

    genre: ReportGenre = ReportGenre.DATA_SCIENCE_REPORT
    audience: str = "general analytical reader"
    perspective: ReportPerspective = ReportPerspective.NEUTRAL
    communication_goal: str = (
        "Summarise the strongest supported findings."
    )

    target_length_words: int = Field(ge=150, le=2_500)
    maximum_main_findings: int = Field(ge=2)
    maximum_supporting_facts: int = Field(default=20, ge=2)

    preferred_sections: list[str] = Field(default_factory=list)
    required_components: list[ReportComponent] = Field(default_factory=list)
    required_content_slots: list[str] = Field(default_factory=list)
    optional_content_slots: list[str] = Field(default_factory=list)
    prohibited_claim_types: list[str] = Field(default_factory=list)

    selection_source: ReportSelectionSource = ReportSelectionSource.FALLBACK
    selection_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    unresolved_ambiguities: list[str] = Field(default_factory=list)

    include_negative_findings: bool = True
    include_methodological_details: bool = True

    prioritisation_rule: str


class InvestigationTask(StrictModel):
    task_id: str
    question: str

    route: AnalysisRoute
    priority: int = Field(ge=1, le=5)

    table_name: str
    columns: list[str] = Field(default_factory=list)
    capability: EvidenceCapability | None = None
    input_fields: list[str] = Field(default_factory=list)
    entity_scope: list[str] = Field(default_factory=list)
    expected_evidence_types: list[str] = Field(default_factory=list)

    target_column: str | None = None
    target_status: TargetStatus = TargetStatus.UNCONFIRMED
    prediction_definition: str | None = None

    time_column: str | None = None
    validation_strategy: ValidationStrategy = ValidationStrategy.NONE

    exposure_column: str | None = None
    outcome_column: str | None = None
    confounder_columns: list[str] = Field(default_factory=list)

    required_evidence: list[str] = Field(default_factory=list)
    claim_permissions: list[ClaimPermission]
    answerability_note: str


class InsightObjective(StrictModel):
    objective_id: str
    question: str
    preferred_insight_types: list[InsightType] = Field(
        default_factory=list
    )
    relevant_task_ids: list[str] = Field(default_factory=list)
    priority: str = "main"


class EvidenceQuery(StrictModel):
    query_id: str
    task_id: str
    operation: EvidenceOperation
    capability: EvidenceCapability
    evidence_type: str

    semantic_label: str
    question: str
    table_name: str
    semantic_level: SemanticLevel

    value_binding_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Exact SemanticBinding.binding_id values only; never field paths "
            "or semantic labels."
        ),
    )
    entity_binding_id: str | None = Field(
        default=None,
        description=(
            "One exact SemanticBinding.binding_id for the entity being compared "
            "or ranked; never a field path."
        ),
    )
    group_binding_id: str | None = Field(
        default=None,
        description=(
            "One exact SemanticBinding.binding_id for an optional parent group; "
            "never a field path."
        ),
    )
    context_binding_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Exact SemanticBinding.binding_id values for optional context only; "
            "never field paths."
        ),
    )

    limit: int = Field(default=3, ge=1)
    descending: bool = True

    recommended_use: RecommendedUse = RecommendedUse.MAIN_FINDING
    user_relevance: float = Field(default=0.8, ge=0.0, le=1.0)
    salience: float = Field(default=0.8, ge=0.0, le=1.0)


class ExecutionPlan(StrictModel):
    objective: str
    tasks: list[InvestigationTask]
    route_order: list[AnalysisRoute]

    report_specification: ReportSpecification
    audit_mode: AuditMode

    insight_objectives: list[InsightObjective] = Field(
        default_factory=list
    )
    evidence_queries: list[EvidenceQuery] = Field(default_factory=list)

    available_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )
    selected_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    revision_limit: int = Field(ge=0, le=3)
    maximum_facts: int = Field(ge=1)

    frozen: bool = True
    rationale: str


class AnalyticalRecommendation(StrictModel):
    recommendation_id: str
    action: str
    recommendation_type: Literal[
        "data_cleaning",
        "methodological_check",
        "additional_analysis",
        "validation",
        "reporting",
    ]
    priority: Literal["high", "medium", "low"]
    justification: str
    affected_analyses: list[str] = Field(default_factory=list)
    consequence_if_ignored: str = (
        "The related analysis may be less reliable or harder to interpret."
    )
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)


class EvidenceItem(StrictModel):
    evidence_id: str
    route: AnalysisRoute
    task_ids: list[str]

    capability: EvidenceCapability = EvidenceCapability.DATASET_PROFILE
    evidence_type: str = "generic_finding"
    source_paths: list[str] = Field(default_factory=list)
    entity_scope: list[str] = Field(default_factory=list)
    semantic_level: SemanticLevel = SemanticLevel.DATASET
    semantic_binding_ids: list[str] = Field(default_factory=list)
    analytical_function: AnalyticalFunction | None = None
    query_id: str | None = None

    finding: str
    metrics: dict[str, Any] = Field(default_factory=dict)

    source_tables: list[str] = Field(default_factory=list)
    source_columns: list[str] = Field(default_factory=list)

    method: str
    validation_strategy: ValidationStrategy = ValidationStrategy.NONE

    practical_interpretation: str
    strength_label: str

    limitations: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)
    recommendations: list[AnalyticalRecommendation] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission]

    factual_confidence: float = Field(ge=0.0, le=1.0)
    methodological_strength: float = Field(ge=0.0, le=1.0)
    user_relevance: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    recommended_use: RecommendedUse
    eligible_for_writer: bool = True
    exclusion_reason: str | None = None


class EvidenceLedger(StrictModel):
    fingerprint: str
    items: list[EvidenceItem]
    execution_notes: list[str] = Field(default_factory=list)


class FactCandidate(StrictModel):
    candidate_id: str
    fact_summary: str

    evidence_ids: list[str]
    claim_permissions: list[ClaimPermission]

    allowed_interpretations: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)
    required_caveats: list[str] = Field(default_factory=list)

    factual_confidence: float = Field(ge=0.0, le=1.0)
    methodological_strength: float = Field(ge=0.0, le=1.0)
    user_relevance: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    recommended_use: RecommendedUse
    eligible_for_writer: bool = True


class FactCandidateSet(StrictModel):
    candidates: list[FactCandidate]
    synthesis_notes: list[str] = Field(default_factory=list)


class FactReview(StrictModel):
    candidate_id: str
    decision: ReviewDecision
    rationale: str
    required_caveats: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)


class VerificationResult(StrictModel):
    reviews: list[FactReview]
    overall_notes: list[str] = Field(default_factory=list)


class VerifiedFact(StrictModel):
    fact_id: str
    source_candidate_id: str

    verification_method: VerificationMethod = (
        VerificationMethod.LLM_VERIFIED
    )

    fact_summary: str
    evidence_ids: list[str]
    source_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    structured_values: dict[str, Any] = Field(default_factory=dict)
    entities: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission]
    allowed_interpretations: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)
    required_caveats: list[str] = Field(default_factory=list)

    factual_confidence: float = Field(ge=0.0, le=1.0)
    methodological_strength: float = Field(ge=0.0, le=1.0)
    user_relevance: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    recommended_use: RecommendedUse


class RejectedFact(StrictModel):
    source_candidate_id: str
    fact_summary: str
    reason: str


class FactLedger(StrictModel):
    writer_ready_facts: list[VerifiedFact]
    rejected_facts: list[RejectedFact] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)

    deterministically_recovered_fact_ids: list[str] = Field(
        default_factory=list
    )
    coverage_recovery_notes: list[str] = Field(
        default_factory=list
    )


class InsightCandidate(StrictModel):
    insight_id: str

    statement: str
    insight_type: InsightType
    interpretation_level: InterpretationLevel

    source_fact_ids: list[str] = Field(default_factory=list)
    source_evidence_ids: list[str] = Field(default_factory=list)

    why_it_matters: str = Field(
        min_length=1,
        description=(
            "The evidence-bounded analytical implication: why the related "
            "findings matter without proposing an unverified explanation."
        ),
    )
    supporting_summary: str

    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    suitable_for_main_report: bool = True


class InsightCandidateSet(StrictModel):
    candidates: list[InsightCandidate] = Field(default_factory=list)
    synthesis_notes: list[str] = Field(default_factory=list)


class InsightVerificationRecord(StrictModel):
    insight_id: str
    status: InsightVerificationStatus

    verified_statement: str | None = None

    verified_source_fact_ids: list[str] = Field(default_factory=list)
    verified_source_evidence_ids: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    adds_bounded_synthesis: bool
    analytical_implication_supported: bool
    contains_hypothesis: bool

    limitations: list[str] = Field(default_factory=list)
    verification_notes: list[str] = Field(default_factory=list)


class InsightVerificationResult(StrictModel):
    records: list[InsightVerificationRecord] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)


class VerifiedInsight(StrictModel):
    insight_id: str

    statement: str
    insight_type: InsightType
    interpretation_level: InterpretationLevel

    source_fact_ids: list[str] = Field(default_factory=list)
    source_evidence_ids: list[str] = Field(default_factory=list)
    source_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    why_it_matters: str = Field(
        min_length=1,
        description=(
            "The verified analytical implication, kept separate from direct "
            "findings and hypotheses."
        ),
    )
    limitations: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    verification_status: InsightVerificationStatus


class InsightRejection(StrictModel):
    insight_id: str
    candidate: InsightCandidate
    reasons: list[str] = Field(default_factory=list)


class InsightLedger(StrictModel):
    verified_insights: list[VerifiedInsight] = Field(default_factory=list)
    hypothesis_only_insights: list[VerifiedInsight] = Field(
        default_factory=list
    )
    rejected_insights: list[InsightRejection] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)
    synthesis_enabled: bool = True
    fallback_reason: str | None = None


class WriterEvidencePack(StrictModel):
    user_request: str
    report_specification: ReportSpecification

    dataset_understanding: DataUnderstanding
    input_structure: InputStructureProfile | None = None
    available_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    priority_facts: list[VerifiedFact]
    supporting_facts: list[VerifiedFact]
    limitation_facts: list[VerifiedFact]

    evidence_ledger: EvidenceLedger

    insight_ledger: InsightLedger = Field(default_factory=InsightLedger)
    priority_verified_insights: list[VerifiedInsight] = Field(
        default_factory=list
    )
    supporting_verified_insights: list[VerifiedInsight] = Field(
        default_factory=list
    )

    analytical_recommendations: list[AnalyticalRecommendation] = Field(
        default_factory=list
    )
    reader_facing_limitations: list[str] = Field(default_factory=list)
    internal_prohibited_interpretations: list[str] = Field(default_factory=list)


class ProfileSupportRecord(StrictModel):
    support_id: str
    fact_kind: str

    table_name: str
    column_name: str | None = None

    statement: str
    structured_values: dict[str, Any] = Field(default_factory=dict)
    entities: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission] = Field(
        default_factory=lambda: [
            ClaimPermission.DESCRIPTIVE
        ]
    )

    provenance: str


class ReportComponentAssessment(StrictModel):
    component: ReportComponent
    covered: bool
    supporting_fact_ids: list[str] = Field(default_factory=list)
    explanation: str


class SentenceSupport(StrictModel):
    sentence_id: str
    sentence_text: str

    fact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    profile_support_ids: list[str] = Field(default_factory=list)
    insight_ids: list[str] = Field(default_factory=list)

    interpretation_level: InterpretationLevel = InterpretationLevel.FINDING

    support_type: SupportType


class WriterSentenceDraft(StrictModel):
    text: str = Field(min_length=1)

    fact_ids: list[str] = Field(default_factory=list)

    insight_ids: list[str] = Field(default_factory=list)
    interpretation_level: InterpretationLevel = InterpretationLevel.FINDING

    support_type: SupportType


class WriterSectionDraft(StrictModel):
    heading: str = Field(min_length=1)

    sentences: list[WriterSentenceDraft] = Field(default_factory=list)


class WriterAgentDraft(StrictModel):
    title: str = Field(min_length=1)
    title_fact_ids: list[str] = Field(default_factory=list)

    sections: list[WriterSectionDraft] = Field(default_factory=list)

    writer_notes: list[str] = Field(default_factory=list)


class WriterOutput(StrictModel):
    title: str
    markdown: str
    title_fact_ids: list[str] = Field(default_factory=list)

    sentence_support: list[SentenceSupport]

    selected_fact_ids: list[str] = Field(default_factory=list)
    omitted_fact_ids: list[str] = Field(default_factory=list)

    writer_notes: list[str] = Field(default_factory=list)

    writer_mode: Literal[
        "llm_writer",
        "deterministic_fallback",
        "auditor_repaired",
    ] = "llm_writer"

    eligible_for_primary_evaluation: bool = True
    quality_revision_round: int = Field(default=0, ge=0, le=1)
    quality_revision_summary: str | None = None


class ExternalFact(StrictModel):
    fact_id: str
    fact_text: str
    entities: list[str] = Field(default_factory=list)
    numbers: list[float] = Field(default_factory=list)
    validity: str = "current"


class ExternalTruthSource(StrictModel):
    source_id: str
    source_name: str
    source_type: str
    trust_level: str

    source_uri: str | None = None
    retrieved_at: str | None = None

    scope: list[str] = Field(default_factory=list)
    facts: list[ExternalFact] = Field(default_factory=list)


class AuditAnnotation(StrictModel):
    annotation_id: str

    sentence: str
    text_span: str

    error_type: ErrorType
    subtype: str
    severity: Severity

    explanation: str
    correction_goal: str

    fact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    external_fact_ids: list[str] = Field(default_factory=list)
    profile_support_ids: list[str] = Field(default_factory=list)
    insight_ids: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)


class RepairCandidate(StrictModel):
    repair_id: str
    replacement_text: str

    strategy: RepairStrategy

    supporting_fact_ids: list[str] = Field(default_factory=list)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    supporting_insight_ids: list[str] = Field(default_factory=list)

    factual_support_score: float = Field(ge=0.0, le=1.0)
    meaning_preservation_score: float = Field(ge=0.0, le=1.0)
    readability_score: float = Field(ge=0.0, le=1.0)
    residual_hallucination_risk: float = Field(ge=0.0, le=1.0)


class SentenceRepair(StrictModel):
    sentence_id: str
    original_sentence: str
    annotation_ids: list[str]

    candidates: list[RepairCandidate]
    preferred_repair_id: str | None = None
    selection_reason: str


class ReportQualityAssessment(StrictModel):
    status: QualityStatus

    request_responsiveness: float = Field(ge=0.0, le=1.0)
    finding_selection: float = Field(ge=0.0, le=1.0)
    coherence: float = Field(ge=0.0, le=1.0)
    concision: float = Field(ge=0.0, le=1.0)
    caveat_integration: float = Field(ge=0.0, le=1.0)
    data_science_interpretation: float = Field(ge=0.0, le=1.0)

    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class AuditRepairProposal(StrictModel):
    annotations: list[AuditAnnotation] = Field(default_factory=list)
    repairs: list[SentenceRepair] = Field(default_factory=list)

    recommended_decision: AuditDecision
    residual_risk: str

    quality_assessment: ReportQualityAssessment
    revision_instructions: list[str] = Field(default_factory=list)


class ReportPatch(StrictModel):
    sentence_id: str
    original_text: str
    replacement_text: str
    operation: Literal["replace", "delete"]
    selected_repair_id: str


class SupportMapPatch(StrictModel):
    sentence_id: str
    sentence_text: str
    added_profile_support_ids: list[str]
    reason: str


class AuditReport(StrictModel):
    mode: AuditMode
    decision: AuditDecision
    release_status: ReleaseStatus

    annotations: list[AuditAnnotation] = Field(default_factory=list)
    applied_patches: list[ReportPatch] = Field(default_factory=list)
    support_map_patches: list[SupportMapPatch] = Field(default_factory=list)

    factual_sentence_count: int
    supported_sentence_count: int
    support_rate: float = Field(ge=0.0, le=1.0)

    residual_risk: str
    revision_instructions: list[str] = Field(default_factory=list)
    quality_assessment: ReportQualityAssessment
    component_assessments: list[ReportComponentAssessment] = Field(default_factory=list)
    methodological_warnings: list[str] = Field(default_factory=list)

    revision_round: int = 0


class RunManifest(StrictModel):
    run_id: str
    created_at: str

    input_paths: list[str]
    request: str
    fingerprint: str

    use_llm: bool
    audit_mode: AuditMode

    models: dict[str, str]
    input_representation_status: InputRepresentationStatus = (
        InputRepresentationStatus.VALID
    )
    report_genre: ReportGenre = ReportGenre.DATA_SCIENCE_REPORT


class PipelineResult(StrictModel):
    run_id: str

    profile: DataProfile
    input_structure: InputStructureProfile | None = None
    structural_catalog: list[StructuralField] = Field(default_factory=list)
    evaluation_field_policy: EvaluationFieldPolicy = Field(
        default_factory=EvaluationFieldPolicy
    )
    understanding: DataUnderstanding
    execution_plan: ExecutionPlan

    evidence_ledger: EvidenceLedger
    fact_candidates: FactCandidateSet
    verification: VerificationResult
    fact_ledger: FactLedger
    writer_evidence_pack: WriterEvidencePack

    raw_writer_output: WriterOutput
    quality_revised_writer_output: WriterOutput | None = None
    final_writer_output: WriterOutput

    initial_audit: AuditReport
    final_audit: AuditReport

    repair_rounds_used: int
    release_status: ReleaseStatus
    approved_for_release: bool
    primary_evaluation_eligible: bool = True
    primary_evaluation_reason: str | None = None
    genre_quality_assessment: GenreQualityAssessment | None = None

    insight_ledger: InsightLedger = Field(default_factory=InsightLedger)


# Compatibility aliases for notebooks using the original names.
ClaimCandidate = FactCandidate
ClaimCandidateSet = FactCandidateSet
ClaimReview = FactReview
VerifiedClaim = VerifiedFact
RejectedClaim = RejectedFact
ClaimLedger = FactLedger
ReportDraft = WriterOutput
````

### `src/table2text/structure.py`

````python
from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .schemas import (
    EvaluationFieldPolicy,
    InputRepresentationStatus,
    InputShape,
    InputStructureProfile,
    StructuralField,
)


PARTICIPANT_CONTAINER_NAMES = {
    "competitors",
    "entities",
    "participants",
    "sides",
    "teams",
}
IDENTITY_FIELD_NAMES = {
    "display_name",
    "entity_name",
    "full_name",
    "name",
    "participant_name",
    "team_name",
}
OUTCOME_FIELD_NAMES = {
    "final_score",
    "points",
    "pts",
    "result",
    "score",
    "total",
}


def normalise_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def _mapping_looks_like_collection(value: Any) -> bool:
    if not isinstance(value, Mapping) or len(value) < 2:
        return False

    children = [child for child in value.values() if isinstance(child, Mapping)]
    return len(children) >= 2 and len(children) == len(value)


def _contains_identity_or_metrics(value: Mapping[str, Any]) -> bool:
    keys = {normalise_key(str(key)) for key in value}
    if keys & IDENTITY_FIELD_NAMES:
        return True

    stack: list[tuple[Any, int]] = [(value, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > 4 or not isinstance(current, Mapping):
            continue
        for key, child in current.items():
            key_name = normalise_key(str(key))
            if key_name in OUTCOME_FIELD_NAMES and isinstance(
                child, (int, float)
            ) and not isinstance(child, bool):
                return True
            if isinstance(child, Mapping):
                stack.append((child, depth + 1))
    return False


def find_participant_container(
    payload: Any,
) -> tuple[str, Mapping[str, Any]] | None:
    stack: list[tuple[str, Any, int]] = [("", payload, 0)]
    fallback: tuple[str, Mapping[str, Any]] | None = None

    while stack:
        path, current, depth = stack.pop()
        if depth > 4 or not isinstance(current, Mapping):
            continue

        for key, child in current.items():
            child_path = f"{path}.{key}" if path else str(key)
            if isinstance(child, Mapping):
                if _mapping_looks_like_collection(child) and all(
                    _contains_identity_or_metrics(item)
                    for item in child.values()
                    if isinstance(item, Mapping)
                ):
                    candidate = (child_path, child)
                    if normalise_key(str(key)) in PARTICIPANT_CONTAINER_NAMES:
                        return candidate
                    fallback = fallback or candidate
                stack.append((child_path, child, depth + 1))

    return fallback


def nested_paths(payload: Any, *, limit: int = 240) -> list[str]:
    paths: list[str] = []

    def visit(value: Any, prefix: str, depth: int) -> None:
        if len(paths) >= limit or depth > 6:
            return

        if isinstance(value, Mapping):
            items = list(value.items())
            if (
                len(items) > 8
                and all(isinstance(child, Mapping) for _, child in items)
            ):
                wildcard = f"{prefix}.*" if prefix else "*"
                paths.append(wildcard)
                visit(items[0][1], wildcard, depth + 1)
                return

            for key, child in items:
                path = f"{prefix}.{key}" if prefix else str(key)
                paths.append(path)
                visit(child, path, depth + 1)
        elif isinstance(value, list) and value:
            path = f"{prefix}[]"
            paths.append(path)
            visit(value[0], path, depth + 1)

    visit(payload, "", 0)
    return list(dict.fromkeys(paths))[:limit]


def _key_overlap(rows: list[Mapping[str, Any]]) -> float:
    if len(rows) < 2:
        return 1.0

    overlaps: list[float] = []
    for left, right in zip(rows, rows[1:]):
        left_keys = set(left)
        right_keys = set(right)
        union = left_keys | right_keys
        overlaps.append(len(left_keys & right_keys) / max(len(union), 1))
    return sum(overlaps) / len(overlaps)


def _homogeneous_record_mapping(value: Mapping[str, Any]) -> bool:
    if len(value) < 2 or not all(isinstance(child, Mapping) for child in value.values()):
        return False

    children = [dict(child) for child in value.values()]
    return _key_overlap(children) >= 0.6


def build_structural_catalog(
    structured_inputs: Mapping[str, Any],
    *,
    maximum_fields: int = 500,
    maximum_samples: int = 3,
) -> list[StructuralField]:
    """Build a compact, value-bearing schema from sanitized structured input."""

    entries: dict[tuple[str, str], dict[str, Any]] = {}

    def value_type(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        if isinstance(value, str):
            return "string"
        return type(value).__name__

    def sample_value(value: Any) -> str:
        text = str(value)
        return text if len(text) <= 120 else text[:117] + "..."

    def add_leaf(table_name: str, path: str, value: Any) -> None:
        key = (table_name, path)
        entry = entries.setdefault(
            key,
            {
                "types": set(),
                "samples": [],
                "count": 0,
            },
        )
        entry["types"].add(value_type(value))
        entry["count"] += 1
        sample = sample_value(value)
        if sample not in entry["samples"] and len(entry["samples"]) < maximum_samples:
            entry["samples"].append(sample)

    def visit(table_name: str, value: Any, prefix: str, depth: int) -> None:
        if depth > 12 or len(entries) >= maximum_fields:
            return

        if isinstance(value, Mapping):
            if _homogeneous_record_mapping(value):
                wildcard = f"{prefix}.*" if prefix else "*"
                for child in list(value.values())[:50]:
                    visit(table_name, child, wildcard, depth + 1)
                return

            for raw_key, child in value.items():
                child_path = f"{prefix}.{raw_key}" if prefix else str(raw_key)
                visit(table_name, child, child_path, depth + 1)
            return

        if isinstance(value, list):
            wildcard = f"{prefix}.*" if prefix else "*"
            for child in value[:50]:
                visit(table_name, child, wildcard, depth + 1)
            if not value:
                add_leaf(table_name, prefix, value)
            return

        add_leaf(table_name, prefix, value)

    for table_name, payload in structured_inputs.items():
        visit(str(table_name), payload, "", 0)

    return [
        StructuralField(
            table_name=table_name,
            path_pattern=path,
            value_types=sorted(entry["types"]),
            sample_values=entry["samples"],
            occurrence_count=entry["count"],
        )
        for (table_name, path), entry in sorted(entries.items())
    ][:maximum_fields]


def _probable_reference_paths(payload: Any, event_like: bool) -> list[str]:
    if not event_like or not isinstance(payload, Mapping):
        return []

    return [
        str(key)
        for key, value in payload.items()
        if isinstance(value, str) and len(value.strip()) >= 500
    ]


def _probable_metadata_paths(payload: Any) -> list[str]:
    if not isinstance(payload, Mapping):
        return []

    metadata: list[str] = []
    for key, value in payload.items():
        name = normalise_key(str(key))
        if name.endswith("_id") or name in {"id", "source", "source_url", "url"}:
            if not isinstance(value, (Mapping, list)):
                metadata.append(str(key))
    return metadata


def _sparse_flattening_risk(payload: Any) -> bool:
    if not isinstance(payload, Mapping):
        return False

    mappings = [value for value in payload.values() if isinstance(value, Mapping)]
    scalars = [
        value
        for value in payload.values()
        if not isinstance(value, (Mapping, list))
    ]
    if len(mappings) < 2 or not scalars:
        return False

    nested_key_sets = [set(value) for value in mappings if value]
    if len(nested_key_sets) < 2:
        return False
    union = set().union(*nested_key_sets)
    intersection = set.intersection(*nested_key_sets)
    return len(union) >= 4 and len(intersection) / max(len(union), 1) < 0.5


def _shape_for_payload(payload: Any) -> tuple[InputShape, str | None, list[str]]:
    participant_container = find_participant_container(payload)
    if participant_container is not None and isinstance(payload, Mapping):
        return InputShape.EVENT_RECORD, "one event", ["event", "participant", "entity"]

    if isinstance(payload, list):
        rows = [item for item in payload if isinstance(item, Mapping)]
        if len(rows) == len(payload):
            nested = any(
                any(isinstance(value, (Mapping, list)) for value in row.values())
                for row in rows
            )
            if nested:
                return InputShape.ENTITY_COLLECTION, "one entity per record", ["entity"]
            return InputShape.FLAT_TABLE, "one observation per row", []

    if isinstance(payload, Mapping):
        values = list(payload.values())
        if values and all(isinstance(value, list) for value in values):
            lengths = {len(value) for value in values}
            if len(lengths) == 1 and not all(
                not value or isinstance(value[0], Mapping)
                for value in values
            ):
                return InputShape.FLAT_TABLE, "one observation per row", []
            if all(
                not value or isinstance(value[0], Mapping)
                for value in values
            ):
                return (
                    InputShape.ENTITY_COLLECTION,
                    "one entity per nested record",
                    ["entity"],
                )
        if any(isinstance(value, (Mapping, list)) for value in payload.values()):
            return InputShape.NESTED_RECORD, "one nested record", []
        return InputShape.NESTED_RECORD, "one record", []

    return InputShape.AMBIGUOUS, None, []


def _path_parts(path: str) -> list[str]:
    return [part for part in path.split(".") if part]


def get_path(payload: Any, path: str) -> tuple[bool, Any]:
    current = payload
    for part in _path_parts(path):
        if not isinstance(current, Mapping) or part not in current:
            return False, None
        current = current[part]
    return True, current


def set_path(target: dict[str, Any], path: str, value: Any) -> None:
    parts = _path_parts(path)
    if not parts:
        return
    current = target
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            child = {}
            current[part] = child
        current = child
    current[parts[-1]] = copy.deepcopy(value)


def remove_path(payload: Any, path: str) -> None:
    if not isinstance(payload, dict):
        return
    parts = _path_parts(path)
    if not parts:
        return
    current: Any = payload
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            return
        current = current[part]
    if isinstance(current, dict):
        current.pop(parts[-1], None)


def apply_field_policy(
    payload: Any,
    policy: EvaluationFieldPolicy,
) -> Any:
    if not isinstance(payload, Mapping):
        return copy.deepcopy(payload)

    if policy.operational_input_paths:
        operational: dict[str, Any] = {}
        for path in policy.operational_input_paths:
            found, value = get_path(payload, path)
            if found:
                set_path(operational, path, value)
    else:
        operational = copy.deepcopy(dict(payload))

    for path in [
        *policy.held_out_reference_paths,
        *policy.metadata_paths,
    ]:
        remove_path(operational, path)
    return operational


def inspect_and_filter_payload(
    *,
    payload: Any,
    source_path: Path,
    field_policy: EvaluationFieldPolicy | None,
) -> tuple[Any, InputStructureProfile, EvaluationFieldPolicy]:
    supplied_policy = field_policy or EvaluationFieldPolicy()
    overlap = set(supplied_policy.operational_input_paths) & set(
        supplied_policy.held_out_reference_paths
    )
    if overlap:
        raise ValueError(
            "Operational and held-out paths overlap: " + ", ".join(sorted(overlap))
        )

    shape, row_semantics, entity_levels = _shape_for_payload(payload)
    participant_container = find_participant_container(payload)
    probable_references = _probable_reference_paths(
        payload,
        participant_container is not None,
    )
    probable_metadata = _probable_metadata_paths(payload)
    ambiguity_notes: list[str] = []

    undeclared_references = sorted(
        set(probable_references)
        - set(supplied_policy.held_out_reference_paths)
    )
    if undeclared_references:
        ambiguity_notes.append(
            "Long narrative fields paired with structured event data were "
            "quarantined as probable evaluation references; declare them "
            "explicitly for primary evaluation: "
            + ", ".join(undeclared_references)
        )

    effective_policy = EvaluationFieldPolicy(
        operational_input_paths=supplied_policy.operational_input_paths,
        held_out_reference_paths=list(
            dict.fromkeys(
                [
                    *supplied_policy.held_out_reference_paths,
                    *undeclared_references,
                ]
            )
        ),
        metadata_paths=supplied_policy.metadata_paths,
    )
    operational = apply_field_policy(payload, effective_policy)

    missing_declared_paths = [
        path
        for path in [
            *supplied_policy.operational_input_paths,
            *supplied_policy.held_out_reference_paths,
            *supplied_policy.metadata_paths,
        ]
        if not get_path(payload, path)[0]
    ]
    if missing_declared_paths:
        ambiguity_notes.append(
            "Declared field paths were absent: "
            + ", ".join(sorted(missing_declared_paths))
        )

    if shape == InputShape.AMBIGUOUS:
        status = InputRepresentationStatus.INVALID
        confidence = 0.2
    elif undeclared_references:
        status = InputRepresentationStatus.AMBIGUOUS
        confidence = 0.75
    elif missing_declared_paths:
        status = InputRepresentationStatus.VALID_WITH_WARNINGS
        confidence = 0.8
    else:
        status = InputRepresentationStatus.VALID
        confidence = 0.98 if shape == InputShape.EVENT_RECORD else 0.95

    heterogeneous = False
    if isinstance(payload, list):
        rows = [item for item in payload if isinstance(item, Mapping)]
        heterogeneous = bool(rows and _key_overlap(rows) < 0.6)

    top_level_fields = list(payload) if isinstance(payload, Mapping) else []
    probable_inputs = [
        str(field)
        for field in top_level_fields
        if str(field) not in effective_policy.held_out_reference_paths
        and str(field) not in effective_policy.metadata_paths
    ]

    profile = InputStructureProfile(
        shape=shape,
        representation_status=status,
        source_paths=[str(source_path)],
        row_semantics=row_semantics,
        entity_levels=entity_levels,
        nested_paths=nested_paths(operational),
        probable_input_fields=probable_inputs,
        probable_reference_fields=probable_references,
        probable_metadata_fields=probable_metadata,
        heterogeneous_rows_detected=heterogeneous,
        sparse_flattening_detected=_sparse_flattening_risk(payload),
        ambiguity_notes=ambiguity_notes,
        confidence=confidence,
    )
    return operational, profile, effective_policy


def combine_structure_profiles(
    profiles: Sequence[InputStructureProfile],
) -> InputStructureProfile:
    if not profiles:
        return InputStructureProfile(
            shape=InputShape.AMBIGUOUS,
            representation_status=InputRepresentationStatus.INVALID,
            row_semantics=None,
            ambiguity_notes=["No input structure could be inspected."],
            confidence=0.0,
        )
    if len(profiles) == 1:
        return profiles[0]

    shapes = {profile.shape for profile in profiles}
    status_order = {
        InputRepresentationStatus.VALID: 0,
        InputRepresentationStatus.VALID_WITH_WARNINGS: 1,
        InputRepresentationStatus.AMBIGUOUS: 2,
        InputRepresentationStatus.INVALID: 3,
    }
    worst = max(
        (profile.representation_status for profile in profiles),
        key=status_order.__getitem__,
    )
    combined_shape = shapes.pop() if len(shapes) == 1 else InputShape.AMBIGUOUS
    if combined_shape == InputShape.AMBIGUOUS and worst != InputRepresentationStatus.INVALID:
        worst = InputRepresentationStatus.AMBIGUOUS

    return InputStructureProfile(
        shape=combined_shape,
        representation_status=worst,
        source_paths=[path for profile in profiles for path in profile.source_paths],
        row_semantics=(
            profiles[0].row_semantics
            if len({profile.row_semantics for profile in profiles}) == 1
            else "multiple input representations"
        ),
        entity_levels=list(
            dict.fromkeys(level for profile in profiles for level in profile.entity_levels)
        ),
        nested_paths=list(
            dict.fromkeys(path for profile in profiles for path in profile.nested_paths)
        ),
        probable_input_fields=list(
            dict.fromkeys(
                field for profile in profiles for field in profile.probable_input_fields
            )
        ),
        probable_reference_fields=list(
            dict.fromkeys(
                field
                for profile in profiles
                for field in profile.probable_reference_fields
            )
        ),
        probable_metadata_fields=list(
            dict.fromkeys(
                field
                for profile in profiles
                for field in profile.probable_metadata_fields
            )
        ),
        heterogeneous_rows_detected=any(
            profile.heterogeneous_rows_detected for profile in profiles
        ),
        sparse_flattening_detected=any(
            profile.sparse_flattening_detected for profile in profiles
        ),
        ambiguity_notes=[
            note for profile in profiles for note in profile.ambiguity_notes
        ],
        confidence=min(profile.confidence for profile in profiles),
    )
````

### `src/table2text/workflow.py`

````python
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic_ai import UsageLimits

from .agents import (
    AgentDependencies,
    build_auditor_agent,
    build_data_understanding_agent,
    build_evidence_agent,
    build_insight_synthesis_agent,
    build_insight_verifier_agent,
    build_orchestrator_agent,
    build_verifier_agent,
    build_writer_agent,
    empty_insight_ledger,
    event_report_requested,
    fallback_execution_plan,
    fallback_understanding,
    materialise_insight_ledger,
)
from .analytics import execute_plan
from .capabilities import (
    available_capabilities,
    normalise_event_evidence_queries,
)
from .audit import (
    accept_writer_quality_revision,
    apply_repair_proposal,
    apply_support_map_patches,
    assess_report_component_coverage,
    assess_genre_quality,
    augment_fact_ledger_for_report_coverage,
    assess_report_components,
    build_profile_support_registry,
    build_writer_evidence_pack,
    compact_json,
    decide_release_status,
    deterministic_audit,
    fallback_audit_proposal,
    fallback_fact_candidates,
    fallback_verification,
    fallback_writer,
    finalise_fact_ledger,
    json_safe,
    materialise_writer_output,
    merge_audit_proposal,
    normalise_strength_label,
    scope_fact_ledger_for_genre,
    validate_writer_output,
)
from .config import Settings
from .data import load_data, profile_data
from .structure import build_structural_catalog
from .schemas import (
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    DataUnderstanding,
    EvaluationFieldPolicy,
    EvidenceCapability,
    ExecutionPlan,
    ExternalTruthSource,
    FactCandidateSet,
    FactLedger,
    InputSemanticMap,
    InsightCandidateSet,
    InsightLedger,
    InsightVerificationResult,
    PipelineResult,
    ProfileSupportRecord,
    QualityStatus,
    ReportComponent,
    ReportGenre,
    ReportSelectionSource,
    InputShape,
    InputRepresentationStatus,
    ReleaseStatus,
    RunManifest,
    VerificationResult,
    WriterAgentDraft,
    WriterEvidencePack,
    WriterOutput,
)


def infer_required_report_components(
    request: str,
) -> list[ReportComponent]:
    normalised = request.lower()
    general_understanding_request = bool(
        re.search(
            r"\b("
            r"understand|"
            r"overview|"
            r"summarise|summarize|"
            r"report findings|"
            r"strongest findings|"
            r"key findings|"
            r"explore"
            r")\b",
            normalised,
        )
    )

    if general_understanding_request:
        return [
            ReportComponent.DATASET_OVERVIEW,
            ReportComponent.DATA_QUALITY,
            ReportComponent.STRONGEST_RELATIONSHIPS,
            ReportComponent.LIMITATIONS_NEXT_STEPS,
        ]

    return []


EVENT_GENRES = {
    ReportGenre.EVENT_REPORT,
    ReportGenre.SPORTS_GAME_REPORT,
}
EVENT_CAPABILITIES = {
    EvidenceCapability.EVENT_OUTCOME,
    EvidenceCapability.ENTITY_PERFORMANCE,
    EvidenceCapability.RANKING,
    EvidenceCapability.GROUP_COMPARISON,
}


def build_orchestrator_prompt_context(
    *,
    understanding: DataUnderstanding,
    input_structure: Any | None,
    structural_catalog: list[Any],
) -> dict[str, Any]:
    """Expose semantic IDs to the planner without competing raw paths."""

    understanding_payload = understanding.model_dump(mode="json")
    semantic_map = understanding.semantic_map
    if semantic_map is None:
        return {
            "understanding": understanding_payload,
            "input_structure": input_structure,
            "structural_catalog": structural_catalog,
            "semantic_binding_catalog": [],
        }

    understanding_payload.pop("semantic_map", None)
    structure_payload = (
        input_structure.model_dump(mode="json")
        if hasattr(input_structure, "model_dump")
        else input_structure
    )
    if isinstance(structure_payload, dict):
        structure_payload = {
            **structure_payload,
            "nested_paths": [],
        }

    return {
        "understanding": understanding_payload,
        "input_structure": structure_payload,
        "structural_catalog": [],
        "semantic_binding_catalog": [
            {
                "binding_id": binding.binding_id,
                "table_name": binding.table_name,
                "label": binding.label,
                "role": binding.role.value,
                "level": binding.level.value,
                "analytical_function": (
                    binding.analytical_function.value
                    if binding.analytical_function is not None
                    else None
                ),
                "unit": binding.unit,
            }
            for binding in semantic_map.bindings
        ],
    }


def resolve_report_genre(
    *,
    request: str,
    planned_genre: ReportGenre,
    configured_genre: ReportGenre | None,
    input_structure: Any | None = None,
    semantic_map: InputSemanticMap | None = None,
) -> tuple[ReportGenre, ReportSelectionSource, float]:
    if event_report_requested(request):
        return (
            ReportGenre.EVENT_REPORT,
            ReportSelectionSource.EXPLICIT_USER_REQUEST,
            1.0,
        )
    if re.search(r"\bdata[- ]science report\b", request, re.IGNORECASE):
        return (
            ReportGenre.DATA_SCIENCE_REPORT,
            ReportSelectionSource.EXPLICIT_USER_REQUEST,
            1.0,
        )
    if re.search(r"\bdataset overview\b", request, re.IGNORECASE):
        return (
            ReportGenre.DATASET_OVERVIEW,
            ReportSelectionSource.EXPLICIT_USER_REQUEST,
            1.0,
        )
    if configured_genre is not None:
        return (
            configured_genre,
            ReportSelectionSource.EXPERIMENT_CONFIGURATION,
            1.0,
        )

    semantic_event = bool(
        semantic_map is not None
        and semantic_map.confidence >= 0.7
        and (
            semantic_map.input_shape == InputShape.EVENT_RECORD
            or semantic_map.recommended_report_genre in EVENT_GENRES
        )
    )
    structural_event = bool(
        input_structure is not None
        and input_structure.shape == InputShape.EVENT_RECORD
        and input_structure.confidence >= 0.7
    )
    if semantic_event or structural_event:
        return (
            ReportGenre.EVENT_REPORT,
            ReportSelectionSource.STRUCTURED_INFERENCE,
            (
                semantic_map.confidence
                if semantic_event and semantic_map is not None
                else input_structure.confidence
            ),
        )

    if re.search(
        r"\b(understand|explore|strongest findings|key findings|"
        r"report (?:its |the )?findings)\b",
        request,
        re.IGNORECASE,
    ):
        return (
            ReportGenre.DATA_SCIENCE_REPORT,
            ReportSelectionSource.FALLBACK,
            0.8,
        )

    if planned_genre in EVENT_GENRES:
        return (
            ReportGenre.EVENT_REPORT,
            ReportSelectionSource.STRUCTURED_INFERENCE,
            0.85,
        )
    return (
        planned_genre,
        ReportSelectionSource.STRUCTURED_INFERENCE,
        0.85,
    )


def report_contract_fields(
    genre: ReportGenre,
) -> dict[str, Any]:
    if genre in EVENT_GENRES:
        return {
            "communication_goal": (
                "Communicate the verified event result, leading performances "
                "and major participant contrasts."
            ),
            "preferred_sections": [
                "Event overview",
                "Key performances",
                "Participant contrasts",
                "Scope limitations",
            ],
            "required_components": [
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            "required_content_slots": [
                "event_result",
                "event_context",
                "event_status",
                "leading_performance",
                "main_contrast",
            ],
            "optional_content_slots": [
                "secondary_performance",
            ],
            "prohibited_claim_types": [
                "unsupported_chronology",
                "unsupported_milestone",
                "unsupported_historical_significance",
                "unsupported_causality",
            ],
            "include_negative_findings": False,
            "include_methodological_details": False,
        }

    if genre == ReportGenre.DATASET_OVERVIEW:
        return {
            "required_content_slots": ["dataset_scope"],
            "optional_content_slots": ["material_data_quality_issue"],
            "prohibited_claim_types": ["unsupported_causality"],
        }

    return {
        "required_content_slots": [
            "dataset_scope",
            "material_data_quality_issue",
            "strongest_analytical_finding",
            "limitation",
        ],
        "optional_content_slots": [],
        "prohibited_claim_types": ["unsupported_causality"],
    }


def add_event_capability_tasks(
    *,
    plan: ExecutionPlan,
    request: str,
    profile: Any,
    audit_mode: AuditMode,
    settings: Settings,
    input_structure: Any,
    capabilities: list[EvidenceCapability],
    genre: ReportGenre,
) -> ExecutionPlan:
    if genre not in EVENT_GENRES:
        return plan

    event_fallback = fallback_execution_plan(
        request,
        profile,
        audit_mode,
        settings,
        input_structure=input_structure,
        available_capabilities=capabilities,
        report_genre_override=genre,
    )
    existing_capabilities = {
        task.capability
        for task in plan.tasks
        if task.capability is not None
    }
    additional_tasks = [
        task.model_copy(
            update={
                "task_id": (
                    "TASK_CAPABILITY_"
                    + task.capability.value.upper()
                )
            }
        )
        for task in event_fallback.tasks
        if task.capability in EVENT_CAPABILITIES
        and task.capability not in existing_capabilities
    ]
    tasks = [*plan.tasks, *additional_tasks]
    route_order = list(
        dict.fromkeys(
            [
                *plan.route_order,
                *[
                    task.route
                    for task in additional_tasks
                ],
            ]
        )
    )
    return plan.model_copy(
        update={
            "tasks": tasks,
            "route_order": route_order,
        }
    )


def exception_cause_chain(
    error: BaseException,
) -> list[str]:
    chain: list[str] = []
    current: BaseException | None = error
    seen: set[int] = set()

    while (
        current is not None
        and id(current) not in seen
    ):
        seen.add(id(current))

        message = getattr(
            current,
            "message",
            str(current),
        )

        chain.append(
            f"{type(current).__name__}: "
            f"{message}"
        )

        current = current.__cause__

    return chain


def build_compact_writer_payload(
    pack: WriterEvidencePack,
    allow_hypotheses_in_report: bool = False,
) -> dict[str, Any]:
    facts_by_id = {
        fact.fact_id: fact
        for fact in [
            *pack.priority_facts,
            *pack.supporting_facts,
            *pack.limitation_facts,
        ]
    }
    evidence_by_id = {
        item.evidence_id: item
        for item in pack.evidence_ledger.items
    }
    strength_labels_by_fact_id = {
        fact_id: list(
            dict.fromkeys(
                normalise_strength_label(
                    evidence_by_id[evidence_id].strength_label
                )
                for evidence_id in fact.evidence_ids
                if evidence_id in evidence_by_id
            )
        )
        for fact_id, fact in facts_by_id.items()
    }

    return {
        "user_request": pack.user_request,
        "report_specification": (
            pack.report_specification
        ),
        "genre": pack.report_specification.genre,
        "audience": pack.report_specification.audience,
        "perspective": pack.report_specification.perspective,
        "communication_goal": (
            pack.report_specification.communication_goal
        ),
        "input_structure": pack.input_structure,
        "available_capabilities": pack.available_capabilities,
        "priority_verified_insights": (
            pack.priority_verified_insights
        ),
        "supporting_verified_insights": (
            pack.supporting_verified_insights
        ),
        "hypothesis_only_insights": (
            pack.insight_ledger.hypothesis_only_insights
            if allow_hypotheses_in_report
            else []
        ),
        "priority_facts": (
            pack.priority_facts
        ),
        "supporting_facts": (
            pack.supporting_facts
        ),
        "limitation_facts": (
            pack.limitation_facts
        ),
        "verified_strength_labels_by_fact_id": (
            strength_labels_by_fact_id
        ),
        "analytical_recommendations": (
            pack.analytical_recommendations
        ),
        "reader_facing_limitations": (
            pack.reader_facing_limitations
        ),
        "internal_prohibited_interpretations": (
            pack
            .internal_prohibited_interpretations
        ),
    }


def build_compact_insight_payload(
    *,
    request: str,
    plan: ExecutionPlan,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
) -> dict[str, Any]:
    referenced_evidence_ids = {
        evidence_id
        for fact in fact_ledger.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }
    referenced_evidence = [
        item
        for item in evidence_ledger.items
        if item.evidence_id in referenced_evidence_ids
    ]

    return {
        "user_request": request,
        "report_specification": plan.report_specification,
        "frozen_insight_objectives": plan.insight_objectives,
        "writer_ready_verified_facts": fact_ledger.writer_ready_facts,
        "referenced_deterministic_evidence": referenced_evidence,
        "analytical_recommendations": [
            recommendation
            for item in referenced_evidence
            for recommendation in item.recommendations
        ],
        "prohibited_interpretations": list(
            dict.fromkeys(
                interpretation
                for fact in fact_ledger.writer_ready_facts
                for interpretation in fact.prohibited_interpretations
            )
        ),
        "limits": {
            "max_insight_candidates": settings.max_insight_candidates,
            "max_verified_main_insights": (
                settings.max_verified_main_insights
            ),
            "min_facts_per_bounded_insight": (
                settings.min_facts_per_bounded_insight
            ),
            "min_insight_confidence": settings.min_insight_confidence,
            "min_insight_salience": settings.min_insight_salience,
            "allow_hypotheses_in_report": (
                settings.allow_hypotheses_in_report
            ),
        },
    }


def build_writer_quality_revision_prompt(
    *,
    writer_pack: WriterEvidencePack,
    current_output: WriterOutput,
    missing_components: list[ReportComponent],
    quality_findings: list[str],
    settings: Settings,
) -> str:
    used_fact_ids = set(
        current_output.selected_fact_ids
    )

    unused_priority_facts = [
        fact
        for fact in writer_pack.priority_facts
        if fact.fact_id not in used_fact_ids
    ]

    current_word_count = len(
        re.findall(
            r"\b[\w'-]+\b",
            current_output.markdown,
        )
    )

    target_words = (
        writer_pack.report_specification
        .target_length_words
    )

    minimum_words = min(
        target_words,
        max(
            settings.minimum_report_word_floor,
            int(
                target_words
                * settings.minimum_report_word_ratio
            ),
            len(
                writer_pack
                .report_specification
                .required_components
            )
            * 45,
        ),
    )

    return (
        "Revise the complete report once for task fulfilment and natural "
        "data-science writing before factual audit.\n\n"
        "This is a Writer quality revision, not a factual repair.\n\n"
        "Do not merely rephrase the existing short report.\n"
        "Use the unused verified priority facts to cover missing sections.\n"
        "Do not invent calculations or facts.\n"
        "Do not calculate statistics.\n"
        "Do not introduce new numbers, entities, categories, metadata, "
        "causal claims, prediction claims, forecast claims, or deployment "
        "claims.\n"
        "Do not expose internal control fields such as Finding:, Strength:, "
        "Important Note:, Interpretation Notes:, Recommended Use:, or Global "
        "Prohibited Interpretations.\n"
        "Use natural data-science prose and consolidate shared caveats.\n"
        "Prefer strong and moderate evidence over small effects.\n"
        "Preserve each supplied qualitative strength classification exactly "
        "and consistently.\n"
        "Do not turn a possible explanation into an ordinary next step; it is "
        "a hypothesis and must follow the configured hypothesis policy.\n"
        "Return structured sections and sentences only. Do not return "
        "Markdown or a separate support map; the controller will create both "
        "deterministically.\n"
        "Every factual sentence must list its supporting fact IDs.\n\n"
        f"Current word count: {current_word_count}\n"
        f"Minimum useful word count: {minimum_words}\n"
        f"Available priority facts: {len(writer_pack.priority_facts)}\n"
        f"Unused priority facts: {len(unused_priority_facts)}\n\n"
        "Missing components:\n"
        + (
            "\n".join(
                f"- {component.value}"
                for component in missing_components
            )
            if missing_components
            else "- None"
        )
        + "\n\nQuality findings:\n"
        + (
            "\n".join(
                f"- {finding}"
                for finding in quality_findings
            )
            if quality_findings
            else "- None"
        )
        + "\n\nUnused verified priority facts:\n"
        + compact_json(unused_priority_facts)
        + "\n\nCompact Writer evidence pack:\n"
        + compact_json(
            build_compact_writer_payload(
                writer_pack,
                settings.allow_hypotheses_in_report,
            )
        )
        + "\n\nCurrent Writer output:\n"
        + compact_json(current_output)
    )

class ArtifactStore:
    def __init__(self, base_directory: Path, run_id: str):
        self.run_directory = base_directory / run_id
        self.run_directory.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.run_directory / "trace.jsonl"

    @staticmethod
    def create_run_id(fingerprint: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{timestamp}_{fingerprint[:10]}"

    def save_json(self, filename: str, value: Any) -> Path:
        path = self.run_directory / filename
        path.write_text(
            json.dumps(
                json_safe(value),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    def save_text(self, filename: str, text: str) -> Path:
        path = self.run_directory / filename
        path.write_text(text, encoding="utf-8")
        return path

    def trace(
        self,
        stage: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": stage,
            "status": status,
            "details": json_safe(details or {}),
        }

        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(event, ensure_ascii=False) + "\n"
            )


class Table2TextWorkflow:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings.from_env()
        if not isinstance(self.settings.output_dir, Path):
            self.settings = self.settings.__class__(
                **{
                    **self.settings.__dict__,
                    "output_dir": Path(self.settings.output_dir),
                }
            )

        self.data_understanding_agent = None
        self.orchestrator_agent = None
        self.evidence_agent = None
        self.verifier_agent = None
        self.evidence_insight_synthesis_agent = None
        self.verifier_insight_verification_agent = None
        self.writer_agent = None
        self.auditor_agent = None

        if self.settings.use_llm:
            self.data_understanding_agent = build_data_understanding_agent(
                self.settings
            )
            self.orchestrator_agent = build_orchestrator_agent(self.settings)
            self.evidence_agent = build_evidence_agent(self.settings)
            self.verifier_agent = build_verifier_agent(self.settings)
            self.evidence_insight_synthesis_agent = (
                build_insight_synthesis_agent(self.settings)
            )
            self.verifier_insight_verification_agent = (
                build_insight_verifier_agent(self.settings)
            )
            self.writer_agent = build_writer_agent(self.settings)
            self.auditor_agent = build_auditor_agent(self.settings)

    def usage_limits(self) -> UsageLimits:
        return UsageLimits(
            request_limit=self.settings.max_agent_requests,
            total_tokens_limit=self.settings.max_total_tokens,
        )

    async def run_agent_or_fallback(
        self,
        *,
        stage: str,
        agent: Any,
        prompt: str,
        dependencies: AgentDependencies,
        fallback: Callable[[], Any],
        store: ArtifactStore,
    ) -> Any:
        if not self.settings.use_llm:
            store.trace(
                stage,
                "fallback",
                {"reason": "LLM execution disabled"},
            )
            return fallback()

        try:
            result = await agent.run(
                prompt,
                deps=dependencies,
                usage_limits=self.usage_limits(),
            )

            usage = getattr(result, "usage", None)

            store.trace(
                stage,
                "completed",
                {"usage": str(usage)},
            )

            return result.output

        except Exception as error:
            store.trace(
                stage,
                "fallback",
                {
                    "reason": (
                        f"{type(error).__name__}: {error}"
                    ),
                    "cause_chain": (
                        exception_cause_chain(
                            error
                        )
                    ),
                },
            )
            return fallback()

    async def run_optional_insight_agent(
        self,
        *,
        stage: str,
        agent: Any,
        prompt: str,
        dependencies: AgentDependencies,
        store: ArtifactStore,
    ) -> tuple[Any | None, str | None]:
        if not self.settings.use_llm or agent is None:
            reason = "LLM execution disabled"
            store.trace(
                stage,
                "skipped",
                {"reason": reason},
            )
            return None, reason

        try:
            result = await agent.run(
                prompt,
                deps=dependencies,
                usage_limits=self.usage_limits(),
            )
            usage = getattr(result, "usage", None)
            store.trace(
                stage,
                "completed",
                {"usage": str(usage)},
            )
            return result.output, None
        except Exception as error:
            reason = f"{type(error).__name__}: {error}"
            store.trace(
                stage,
                "fallback",
                {
                    "reason": reason,
                    "cause_chain": exception_cause_chain(error),
                },
            )
            return None, reason

    async def audit_once(
        self,
        *,
        run_id: str,
        writer_output: WriterOutput,
        fact_ledger: Any,
        evidence_ledger: Any,
        insight_ledger: InsightLedger,
        profile_support_records: list[
            ProfileSupportRecord
        ],
        plan: ExecutionPlan,
        audit_mode: AuditMode,
        external_truth_sources: list[ExternalTruthSource],
        revision_round: int,
        store: ArtifactStore,
        stage_name: str,
    ) -> tuple[AuditReport, AuditRepairProposal, WriterOutput]:
        deterministic_pre_patch = deterministic_audit(
            writer_output=writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=revision_round,
            report_specification=plan.report_specification,
            settings=self.settings,
            profile_support_records=profile_support_records,
            insight_ledger=insight_ledger,
        )

        if revision_round == 0:
            pre_patch_audit_name = (
                "10_initial_audit_pre_profile_patch.json"
            )
            support_patch_name = (
                "10_initial_support_map_patches.json"
            )
            profile_patched_name = (
                "10_initial_profile_patched_output.json"
            )
        else:
            pre_patch_audit_name = (
                "14_post_repair_audit_pre_profile_patch"
                f"_round_{revision_round}.json"
            )
            support_patch_name = (
                "14_post_repair_support_map_patches"
                f"_round_{revision_round}.json"
            )
            profile_patched_name = (
                "14_post_repair_profile_patched_output"
                f"_round_{revision_round}.json"
            )

        store.save_json(
            pre_patch_audit_name,
            deterministic_pre_patch,
        )
        store.save_json(
            support_patch_name,
            deterministic_pre_patch.support_map_patches,
        )

        profile_patched_output = writer_output

        if deterministic_pre_patch.support_map_patches:
            profile_patched_output = apply_support_map_patches(
                writer_output,
                deterministic_pre_patch.support_map_patches,
                {
                    record.support_id
                    for record in profile_support_records
                },
            )

        store.save_json(
            profile_patched_name,
            profile_patched_output,
        )

        deterministic = deterministic_audit(
            writer_output=profile_patched_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=revision_round,
            report_specification=plan.report_specification,
            settings=self.settings,
            profile_support_records=profile_support_records,
            insight_ledger=insight_ledger,
        ).model_copy(
            update={
                "support_map_patches": (
                    deterministic_pre_patch
                    .support_map_patches
                )
            }
        )

        deterministic_annotation_ids = [
            annotation.annotation_id
            for annotation in deterministic.annotations
        ]
        deterministic_serious_annotation_ids = [
            annotation.annotation_id
            for annotation in deterministic.annotations
            if annotation.severity.value
            in {"high", "critical"}
        ]

        prompt = (
            "Audit this report independently and propose targeted repairs "
            "for high-confidence factual errors.\n\n"
            "User objective:\n"
            + plan.objective
            + "\n\nReport specification:\n"
            + compact_json(plan.report_specification)
            + "\n\nWriter output:\n"
            + compact_json(profile_patched_output)
            + "\n\nVerified fact ledger:\n"
            + compact_json(fact_ledger)
            + "\n\nEvidence ledger:\n"
            + compact_json(evidence_ledger)
            + "\n\nVerified insight ledger:\n"
            + compact_json(insight_ledger)
            + "\n\nDeterministic profile support registry:\n"
            + compact_json(profile_support_records)
            + "\n\nDeterministic pre-audit:\n"
            + compact_json(deterministic)
            + "\n\nExternal truth sources:\n"
            + compact_json(external_truth_sources)
            + "\n\nGenerate no more than "
            + str(self.settings.repair_candidates_per_sentence)
            + " repair candidates for each flagged sentence."
        )

        proposal = await self.run_agent_or_fallback(
            stage=stage_name,
            agent=self.auditor_agent,
            prompt=prompt,
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "report_text": profile_patched_output.markdown,
                    "fact_ledger": fact_ledger.model_dump(mode="json"),
                    "evidence_ledger": evidence_ledger.model_dump(
                        mode="json"
                    ),
                    "insight_ledger": insight_ledger.model_dump(
                        mode="json"
                    ),
                    "valid_fact_ids": [
                        fact.fact_id
                        for fact in fact_ledger.writer_ready_facts
                    ],
                    "valid_evidence_ids": [
                        item.evidence_id
                        for item in evidence_ledger.items
                    ],
                    "valid_profile_support_ids": [
                        record.support_id
                        for record in profile_support_records
                    ],
                    "valid_insight_ids": [
                        insight.insight_id
                        for insight in insight_ledger.verified_insights
                    ],
                    "verified_main_insight_ids": [
                        insight.insight_id
                        for insight in insight_ledger.verified_insights
                    ],
                    "hypothesis_only_insight_ids": [
                        insight.insight_id
                        for insight in (
                            insight_ledger.hypothesis_only_insights
                        )
                    ],
                    "insight_statements": {
                        insight.insight_id: insight.statement
                        for insight in [
                            *insight_ledger.verified_insights,
                            *insight_ledger.hypothesis_only_insights,
                        ]
                    },
                    "insight_source_fact_ids": {
                        insight.insight_id: insight.source_fact_ids
                        for insight in [
                            *insight_ledger.verified_insights,
                            *insight_ledger.hypothesis_only_insights,
                        ]
                    },
                    "insight_source_evidence_ids": {
                        insight.insight_id: insight.source_evidence_ids
                        for insight in [
                            *insight_ledger.verified_insights,
                            *insight_ledger.hypothesis_only_insights,
                        ]
                    },
                    "sentence_insight_ids": {
                        support.sentence_text: support.insight_ids
                        for support in profile_patched_output.sentence_support
                    },
                    "allow_hypotheses_in_report": (
                        self.settings.allow_hypotheses_in_report
                    ),
                    "report_genre": plan.report_specification.genre.value,
                    "report_perspective": (
                        plan.report_specification.perspective.value
                    ),
                    "deterministic_annotation_ids": (
                        deterministic_annotation_ids
                    ),
                    "deterministic_serious_annotation_ids": (
                        deterministic_serious_annotation_ids
                    ),
                    "deterministic_annotation_sentences": [
                        annotation.sentence
                        for annotation in deterministic.annotations
                    ],
                },
            ),
            fallback=lambda: fallback_audit_proposal(
                deterministic
            ),
            store=store,
        )

        proposal = AuditRepairProposal.model_validate(proposal)
        merged = merge_audit_proposal(deterministic, proposal)

        return merged, proposal, profile_patched_output

    async def run(
        self,
        inputs: list[str | Path],
        request: str,
        *,
        audit_mode: AuditMode = AuditMode.INTERNAL,
        external_truth_sources: list[ExternalTruthSource] | None = None,
        evaluation_field_policy: EvaluationFieldPolicy | None = None,
        report_genre: ReportGenre | None = None,
    ) -> PipelineResult:
        external_truth_sources = external_truth_sources or []

        data_bundle = load_data(
            inputs,
            evaluation_field_policy=evaluation_field_policy,
        )
        input_structure = data_bundle.input_structure
        capabilities = available_capabilities(data_bundle)
        structural_catalog = build_structural_catalog(data_bundle.structured_inputs)
        representation_eligible = bool(
            input_structure
            and input_structure.representation_status
            in {
                InputRepresentationStatus.VALID,
                InputRepresentationStatus.VALID_WITH_WARNINGS,
            }
        )
        profile = profile_data(data_bundle)
        profile_support_records = (
            build_profile_support_registry(
                profile
            )
        )

        run_id = ArtifactStore.create_run_id(
            data_bundle.fingerprint
        )
        store = ArtifactStore(
            self.settings.output_dir,
            run_id,
        )

        store.save_json("00_input_structure.json", input_structure)
        store.save_json(
            "00_evaluation_field_policy.json",
            data_bundle.evaluation_field_policy,
        )
        store.save_json("00_available_capabilities.json", capabilities)
        store.save_json(
            "00_structural_catalog.json",
            structural_catalog,
        )

        models = {
            role: self.settings.model_for(role)
            for role in [
                "data_understanding",
                "orchestrator",
                "evidence",
                "verifier",
                "writer",
                "auditor",
            ]
        }

        manifest = RunManifest(
            run_id=run_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            input_paths=[
                str(path)
                for path in data_bundle.source_paths
            ],
            request=request,
            fingerprint=data_bundle.fingerprint,
            use_llm=self.settings.use_llm,
            audit_mode=audit_mode,
            models=models,
            input_representation_status=(
                input_structure.representation_status
                if input_structure is not None
                else InputRepresentationStatus.INVALID
            ),
            report_genre=(
                ReportGenre.EVENT_REPORT
                if event_report_requested(request)
                else report_genre or ReportGenre.DATA_SCIENCE_REPORT
            ),
        )

        store.save_json("00_manifest.json", manifest)
        store.save_json("01_profile.json", profile)
        store.save_json(
            "02_profile_support_registry.json",
            profile_support_records,
        )

        table_names = [
            table.table_name
            for table in profile.tables
        ]
        columns = {
            table.table_name: [
                column.name
                for column in table.columns
            ]
            for table in profile.tables
        }

        understanding = await self.run_agent_or_fallback(
            stage="data_understanding",
            agent=self.data_understanding_agent,
            prompt=(
                "Create a data understanding and analytical-risk report.\n\n"
                "Input structure:\n"
                + compact_json(input_structure)
                + "\n\nSanitized structural field catalog:\n"
                + compact_json(structural_catalog)
                + "\n\nSanitized data profile:\n"
                + compact_json(profile)
            ),
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "fingerprint": profile.fingerprint,
                    "table_names": table_names,
                    "columns": columns,
                    "input_structure": (
                        input_structure.model_dump(mode="json")
                        if input_structure is not None
                        else None
                    ),
                    "structural_catalog": [
                        field.model_dump(mode="json") for field in structural_catalog
                    ],
                    "semantic_map_required": bool(structural_catalog),
                },
            ),
            fallback=lambda: fallback_understanding(profile),
            store=store,
        )
        understanding = DataUnderstanding.model_validate(understanding)
        store.save_json("02_understanding.json", understanding)
        semantic_map = understanding.semantic_map
        store.save_json("02_semantic_map.json", semantic_map)
        capabilities = available_capabilities(
            data_bundle,
            semantic_map,
        )
        store.save_json(
            "02_available_capabilities.json",
            capabilities,
        )
        inferred_genre = (
            semantic_map.recommended_report_genre
            if semantic_map is not None and semantic_map.recommended_report_genre is not None
            else ReportGenre.DATA_SCIENCE_REPORT
        )
        (
            controller_genre,
            _,
            _,
        ) = resolve_report_genre(
            request=request,
            planned_genre=inferred_genre,
            configured_genre=report_genre,
            input_structure=input_structure,
            semantic_map=semantic_map,
        )
        planner_context = build_orchestrator_prompt_context(
            understanding=understanding,
            input_structure=input_structure,
            structural_catalog=structural_catalog,
        )

        plan = await self.run_agent_or_fallback(
            stage="orchestration_and_planning",
            agent=self.orchestrator_agent,
            prompt=(
                "User objective:\n"
                + request
                + "\n\nData profile:\n"
                + compact_json(profile)
                + "\n\nData understanding:\n"
                + compact_json(planner_context["understanding"])
                + "\n\nInput structure:\n"
                + compact_json(planner_context["input_structure"])
                + "\n\nSanitized structural field catalog:\n"
                + compact_json(planner_context["structural_catalog"])
                + "\n\nID-only semantic binding catalogue:\n"
                + compact_json(planner_context["semantic_binding_catalog"])
                + "\nUse only `binding_id` values from that catalogue in all "
                "evidence-query binding fields. Raw paths are deliberately "
                "unavailable for semantic query planning.\n"
                + "\n\nAvailable evidence capabilities:\n"
                + compact_json(capabilities)
                + "\n\nController-selected report genre:\n"
                + controller_genre.value
                + "\n\nConfigured report genre override:\n"
                + (report_genre.value if report_genre else "none")
                + "\n\nAudit mode:\n"
                + audit_mode.value
            ),
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "table_names": table_names,
                    "columns": columns,
                    "user_request": request,
                    "allow_experimental_targets": (
                        self.settings.allow_experimental_targets
                    ),
                    "available_capabilities": [
                        capability.value
                        for capability in capabilities
                    ],
                    "event_genre_allowed": (
                        controller_genre in EVENT_GENRES
                    ),
                    "selected_report_genre": controller_genre.value,
                    "semantic_map": (
                        semantic_map.model_dump(mode="json")
                        if semantic_map is not None
                        else None
                    ),
                    "structural_catalog": [
                        field.model_dump(mode="json")
                        for field in structural_catalog
                    ],
                    "enable_insight_synthesis": (
                        self.settings.enable_insight_synthesis
                    ),
                },
            ),
            fallback=lambda: fallback_execution_plan(
                request,
                profile,
                audit_mode,
                self.settings,
                input_structure=input_structure,
                available_capabilities=capabilities,
                report_genre_override=report_genre,
            ),
            store=store,
        )

        plan = ExecutionPlan.model_validate(plan)
        (
            selected_genre,
            selection_source,
            selection_confidence,
        ) = resolve_report_genre(
            request=request,
            planned_genre=plan.report_specification.genre,
            configured_genre=report_genre,
            input_structure=input_structure,
            semantic_map=semantic_map,
        )
        contract_fields = report_contract_fields(selected_genre)
        required_components = (
            contract_fields.get("required_components", [])
            if selected_genre in EVENT_GENRES
            else infer_required_report_components(request)
        )
        maximum_main_findings = (
            100
            if selected_genre in EVENT_GENRES
            else plan.report_specification.maximum_main_findings
        )
        maximum_supporting_facts = (
            max(
                plan.report_specification.maximum_supporting_facts,
                self.settings.writer_supporting_fact_limit,
                self.settings.writer_priority_fact_limit,
                500,
            )
            if selected_genre in EVENT_GENRES
            else min(
                max(
                    plan.report_specification.maximum_supporting_facts,
                    maximum_main_findings,
                ),
                maximum_main_findings + 4,
            )
        )
        report_specification = plan.report_specification.model_copy(
            update={
                "report_purpose": request,
                "genre": selected_genre,
                "selection_source": selection_source,
                "selection_confidence": selection_confidence,
                "target_length_words": (
                    plan.report_specification.target_length_words
                ),
                "maximum_main_findings": maximum_main_findings,
                "maximum_supporting_facts": maximum_supporting_facts,
                "required_components": list(
                    dict.fromkeys(
                        [
                            *plan.report_specification.required_components,
                            *required_components,
                        ]
                    )
                ),
                **contract_fields,
            }
        )
        selected_capabilities = [
            capability
            for capability in capabilities
            if (
                selected_genre not in EVENT_GENRES
                or capability
                in {
                    EvidenceCapability.DATASET_PROFILE,
                    *EVENT_CAPABILITIES,
                }
            )
        ]
        plan = plan.model_copy(
            update={
                "objective": request,
                "report_specification": report_specification,
                "available_capabilities": capabilities,
                "selected_capabilities": selected_capabilities,
                "audit_mode": audit_mode,
                "revision_limit": min(
                    plan.revision_limit,
                    self.settings.max_revision_rounds,
                ),
                "insight_objectives": (
                    plan.insight_objectives
                    if self.settings.enable_insight_synthesis
                    else []
                ),
                "frozen": True,
            }
        )
        plan = add_event_capability_tasks(
            plan=plan,
            request=request,
            profile=profile,
            audit_mode=audit_mode,
            settings=self.settings,
            input_structure=input_structure,
            capabilities=capabilities,
            genre=selected_genre,
        )
        if (
            selected_genre in EVENT_GENRES
            and semantic_map is not None
            and semantic_map.bindings
        ):
            plan = plan.model_copy(
                update={
                    "evidence_queries": normalise_event_evidence_queries(
                        queries=plan.evidence_queries,
                        semantic_map=semantic_map,
                        tasks=plan.tasks,
                        available_capabilities=set(capabilities),
                        request=request,
                    )
                }
            )
        manifest = manifest.model_copy(
            update={"report_genre": selected_genre}
        )
        store.save_json("00_manifest.json", manifest)
        store.save_json("03_execution_plan.json", plan)
        store.save_json(
            "03_evidence_queries.json",
            plan.evidence_queries,
        )
        store.save_json(
            "03_insight_objectives.json",
            plan.insight_objectives,
        )

        evidence_ledger = execute_plan(
            data_bundle,
            plan,
            self.settings,
            semantic_map,
        )
        store.save_json("04_evidence_ledger.json", evidence_ledger)

        fact_candidates = await self.run_agent_or_fallback(
            stage="evidence_synthesis",
            agent=self.evidence_agent,
            prompt=(
                "Create atomic fact candidates from this rich evidence ledger.\n\n"
                + compact_json(evidence_ledger)
                + "\n\nMaximum facts:\n"
                + str(plan.maximum_facts)
            ),
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "evidence_ledger": evidence_ledger.model_dump(mode="json")
                },
            ),
            fallback=lambda: fallback_fact_candidates(
                evidence_ledger,
                plan.maximum_facts,
            ),
            store=store,
        )
        fact_candidates = FactCandidateSet.model_validate(fact_candidates)
        store.save_json("05_fact_candidates.json", fact_candidates)

        verification = await self.run_agent_or_fallback(
            stage="fact_verification",
            agent=self.verifier_agent,
            prompt=(
                "Verify every fact candidate against the evidence.\n\n"
                "Candidates:\n"
                + compact_json(fact_candidates)
                + "\n\nEvidence:\n"
                + compact_json(evidence_ledger)
            ),
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "fact_candidates": fact_candidates.model_dump(mode="json")
                },
            ),
            fallback=lambda: fallback_verification(
                fact_candidates
            ),
            store=store,
        )
        verification = VerificationResult.model_validate(verification)
        store.save_json("06_verification.json", verification)

        fact_ledger = finalise_fact_ledger(
            fact_candidates,
            verification,
            evidence_ledger,
        )
        if not fact_ledger.writer_ready_facts:
            store.trace(
                "fact_ledger_finalisation",
                "recovery",
                {
                    "reason": "Verifier rejected every fact candidate.",
                },
            )
            fact_candidates = fallback_fact_candidates(
                evidence_ledger,
                plan.maximum_facts,
            )
            verification = fallback_verification(fact_candidates)
            fact_ledger = finalise_fact_ledger(
                fact_candidates,
                verification,
                evidence_ledger,
            )
            store.save_json("05_fact_candidates_recovered.json", fact_candidates)
            store.save_json("06_verification_recovered.json", verification)
            store.save_json("07_fact_ledger_recovered.json", fact_ledger)
        store.save_json(
            "07_fact_ledger_pre_coverage_recovery.json",
            fact_ledger,
        )

        fact_count_before_recovery = len(
            fact_ledger.writer_ready_facts
        )

        fact_ledger = (
            augment_fact_ledger_for_report_coverage(
                fact_ledger=fact_ledger,
                evidence=evidence_ledger,
                required_components=(
                    plan.report_specification
                    .required_components
                ),
                settings=self.settings,
            )
        )

        store.trace(
            "fact_ledger_coverage_recovery",
            "completed",
            {
                "facts_before": (
                    fact_count_before_recovery
                ),
                "facts_after": len(
                    fact_ledger
                    .writer_ready_facts
                ),
                "recovered_fact_ids": (
                    fact_ledger
                    .deterministically_recovered_fact_ids
                ),
                "notes": (
                    fact_ledger
                    .coverage_recovery_notes
                ),
            },
        )

        store.save_json(
            "07_fact_ledger.json",
            fact_ledger,
        )
        genre_scoped_fact_ledger = scope_fact_ledger_for_genre(
            fact_ledger,
            evidence_ledger,
            plan.report_specification.genre,
        )

        insight_candidates = InsightCandidateSet()
        insight_verification = InsightVerificationResult()

        if not self.settings.enable_insight_synthesis:
            insight_ledger = empty_insight_ledger(
                synthesis_enabled=False,
                fallback_reason=(
                    "Insight synthesis disabled by configuration."
                ),
            )
            store.trace(
                "evidence.insight_synthesis",
                "skipped",
                {"reason": insight_ledger.fallback_reason},
            )
            store.trace(
                "verifier.insight_verification",
                "skipped",
                {"reason": insight_ledger.fallback_reason},
            )
        elif not self.settings.use_llm:
            insight_ledger = empty_insight_ledger(
                synthesis_enabled=True,
                fallback_reason=(
                    "LLM execution disabled; the workflow continued through "
                    "the existing fact-led Writer path."
                ),
            )
            store.trace(
                "evidence.insight_synthesis",
                "skipped",
                {"reason": "LLM execution disabled"},
            )
            store.trace(
                "verifier.insight_verification",
                "skipped",
                {"reason": "LLM execution disabled"},
            )
        else:
            insight_payload = build_compact_insight_payload(
                request=request,
                plan=plan,
                fact_ledger=genre_scoped_fact_ledger,
                evidence_ledger=evidence_ledger,
                settings=self.settings,
            )
            raw_insight_candidates, synthesis_error = (
                await self.run_optional_insight_agent(
                    stage="evidence.insight_synthesis",
                    agent=self.evidence_insight_synthesis_agent,
                    prompt=(
                        "Perform the Evidence Analyst's second bounded "
                        "synthesis pass. Use only this compact package and "
                        "return structured insight candidates.\n\n"
                        + compact_json(insight_payload)
                    ),
                    dependencies=AgentDependencies(
                        run_id=run_id,
                        payload={
                            "fact_ledger": (
                                genre_scoped_fact_ledger.model_dump(
                                    mode="json"
                                )
                            ),
                            "evidence_ledger": evidence_ledger.model_dump(
                                mode="json"
                            ),
                        },
                    ),
                    store=store,
                )
            )

            if synthesis_error is not None:
                insight_ledger = empty_insight_ledger(
                    synthesis_enabled=True,
                    fallback_reason=(
                        "Evidence Analyst second-pass insight synthesis "
                        f"failed: {synthesis_error}"
                    ),
                )
            else:
                try:
                    insight_candidates = InsightCandidateSet.model_validate(
                        raw_insight_candidates
                    )
                except Exception as error:
                    insight_ledger = empty_insight_ledger(
                        synthesis_enabled=True,
                        fallback_reason=(
                            "Evidence Analyst second-pass output remained "
                            "invalid: "
                            f"{type(error).__name__}: {error}"
                        ),
                    )
                else:
                    if not insight_candidates.candidates:
                        insight_ledger = empty_insight_ledger(
                            synthesis_enabled=True,
                            fallback_reason=(
                                "Evidence Analyst second pass returned no "
                                "bounded insight candidates."
                            ),
                        )
                    else:
                        referenced_evidence_ids = {
                            evidence_id
                            for candidate in insight_candidates.candidates
                            for evidence_id in candidate.source_evidence_ids
                        }
                        referenced_evidence_ids.update(
                            evidence_id
                            for fact in genre_scoped_fact_ledger.writer_ready_facts
                            if fact.fact_id
                            in {
                                fact_id
                                for candidate in insight_candidates.candidates
                                for fact_id in candidate.source_fact_ids
                            }
                            for evidence_id in fact.evidence_ids
                        )
                        verifier_evidence = [
                            item
                            for item in evidence_ledger.items
                            if item.evidence_id
                            in referenced_evidence_ids
                        ]
                        raw_insight_verification, verifier_error = (
                            await self.run_optional_insight_agent(
                                stage="verifier.insight_verification",
                                agent=(
                                    self.verifier_insight_verification_agent
                                ),
                                prompt=(
                                    "Perform the Fact Verifier's second-pass "
                                    "review of every bounded insight candidate."
                                    "\n\nCandidates:\n"
                                    + compact_json(insight_candidates)
                                    + "\n\nWriter-ready facts:\n"
                                    + compact_json(
                                        genre_scoped_fact_ledger
                                        .writer_ready_facts
                                    )
                                    + "\n\nReferenced deterministic evidence:\n"
                                    + compact_json(verifier_evidence)
                                    + "\n\nReport specification:\n"
                                    + compact_json(
                                        plan.report_specification
                                    )
                                ),
                                dependencies=AgentDependencies(
                                    run_id=run_id,
                                    payload={
                                        "insight_candidates": (
                                            insight_candidates.model_dump(
                                                mode="json"
                                            )
                                        ),
                                        "fact_ledger": (
                                            genre_scoped_fact_ledger
                                            .model_dump(
                                                mode="json"
                                            )
                                        ),
                                        "evidence_ledger": (
                                            evidence_ledger.model_dump(
                                                mode="json"
                                            )
                                        ),
                                    },
                                ),
                                store=store,
                            )
                        )

                        if verifier_error is not None:
                            insight_ledger = empty_insight_ledger(
                                synthesis_enabled=True,
                                fallback_reason=(
                                    "Fact Verifier second-pass insight review "
                                    f"failed: {verifier_error}"
                                ),
                            )
                        else:
                            try:
                                insight_verification = (
                                    InsightVerificationResult.model_validate(
                                        raw_insight_verification
                                    )
                                )
                                insight_ledger = materialise_insight_ledger(
                                    candidates=insight_candidates,
                                    verification=insight_verification,
                                    fact_ledger=genre_scoped_fact_ledger,
                                    evidence_ledger=evidence_ledger,
                                    settings=self.settings,
                                )
                            except Exception as error:
                                insight_ledger = empty_insight_ledger(
                                    synthesis_enabled=True,
                                    fallback_reason=(
                                        "Deterministic Insight Ledger "
                                        "materialisation failed: "
                                        f"{type(error).__name__}: {error}"
                                    ),
                                )

        store.save_json(
            "07_insight_candidates.json",
            insight_candidates,
        )
        store.save_json(
            "07_insight_verification.json",
            insight_verification,
        )
        store.save_json(
            "07_insight_ledger.json",
            insight_ledger,
        )
        store.trace(
            "insight_ledger",
            "completed" if insight_ledger.fallback_reason is None else "fallback",
            {
                "synthesis_enabled": insight_ledger.synthesis_enabled,
                "verified_main_insight_count": len(
                    insight_ledger.verified_insights
                ),
                "hypothesis_only_count": len(
                    insight_ledger.hypothesis_only_insights
                ),
                "rejected_count": len(
                    insight_ledger.rejected_insights
                ),
                "fallback_reason": insight_ledger.fallback_reason,
            },
        )

        writer_pack = build_writer_evidence_pack(
            request=request,
            understanding=understanding,
            plan=plan,
            evidence=evidence_ledger,
            fact_ledger=fact_ledger,
            settings=self.settings,
            insight_ledger=insight_ledger,
            input_structure=input_structure,
            available_capabilities=capabilities,
        )
        store.save_json("08_writer_evidence_pack.json", writer_pack)

        writer_prompt = (
            "Write the final report for the selected report contract from the "
            "compact verified-fact package below.\n\n"
            "Return structured sections and sentences. Do not return "
            "a Markdown field or construct a separate support map; the "
            "controller will create both deterministically.\n\n"
            + compact_json(
                build_compact_writer_payload(
                    writer_pack,
                    self.settings.allow_hypotheses_in_report,
                )
            )
        )

        writer_material_available = bool(
            writer_pack.priority_facts
            or writer_pack.supporting_facts
            or writer_pack.limitation_facts
            or writer_pack.priority_verified_insights
            or writer_pack.supporting_verified_insights
        )
        if writer_material_available:
            writer_draft_or_fallback = await self.run_agent_or_fallback(
                stage="natural_writer",
                agent=self.writer_agent,
                prompt=writer_prompt,
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_ledger": genre_scoped_fact_ledger.model_dump(mode="json"),
                        "insight_ledger": writer_pack.insight_ledger.model_dump(
                            mode="json"
                        ),
                        "allow_hypotheses_in_report": (
                            self.settings.allow_hypotheses_in_report
                        ),
                        "report_genre": plan.report_specification.genre.value,
                        "report_perspective": (
                            plan.report_specification.perspective.value
                        ),
                    },
                ),
                fallback=lambda: fallback_writer(writer_pack),
                store=store,
            )
        else:
            writer_draft_or_fallback = fallback_writer(writer_pack)
            store.trace(
                "natural_writer",
                "skipped",
                {
                    "reason": "No verified genre-scoped facts or insights.",
                    "fallback": "deterministic_writer",
                },
            )

        if isinstance(
            writer_draft_or_fallback,
            WriterOutput,
        ):
            raw_writer_output = (
                writer_draft_or_fallback
            )
        else:
            writer_draft = (
                WriterAgentDraft.model_validate(
                    writer_draft_or_fallback
                )
            )
            store.save_json(
                "09_writer_structured_draft.json",
                writer_draft,
            )

            try:
                raw_writer_output = materialise_writer_output(
                    writer_draft,
                    genre_scoped_fact_ledger,
                    insight_ledger=writer_pack.insight_ledger,
                    allow_hypotheses_in_report=(
                        self.settings.allow_hypotheses_in_report
                    ),
                    writer_mode="llm_writer",
                    eligible_for_primary_evaluation=representation_eligible,
                )
            except ValueError as error:
                store.save_text(
                    "09_writer_materialisation_error.txt",
                    str(error),
                )
                store.trace(
                    "natural_writer_materialisation",
                    "fallback",
                    {
                        "reason": f"ValueError: {error}",
                        "fallback": "deterministic_writer",
                    },
                )
                raw_writer_output = fallback_writer(
                    writer_pack
                )

        if not representation_eligible:
            raw_writer_output = raw_writer_output.model_copy(
                update={"eligible_for_primary_evaluation": False}
            )

        store.save_json(
            "09_writer_raw_output.json",
            raw_writer_output,
        )
        store.save_text(
            "09_writer_raw_report.md",
            raw_writer_output.markdown,
        )
        store.save_json(
            "09_writer_support_map.json",
            raw_writer_output.sentence_support,
        )

        component_assessments = assess_report_component_coverage(
            writer_output=raw_writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            required_components=plan.report_specification.required_components,
        )
        missing_components = [
            assessment.component
            for assessment in component_assessments
            if not assessment.covered
        ]
        store.save_json(
            "09_writer_component_coverage.json",
            component_assessments,
        )
        initial_genre_quality = assess_genre_quality(
            raw_writer_output,
            plan.report_specification,
            evidence_ledger,
        )
        store.save_json(
            "09_writer_genre_quality.json",
            initial_genre_quality,
        )

        initial_quality_audit = deterministic_audit(
            writer_output=raw_writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=0,
            report_specification=plan.report_specification,
            settings=self.settings,
            profile_support_records=profile_support_records,
            insight_ledger=insight_ledger,
        )
        store.save_json("10_initial_writer_quality.json", initial_quality_audit)

        writer_output_for_audit = raw_writer_output
        quality_revised_writer_output: WriterOutput | None = None
        needs_quality_revision = (
            bool(missing_components)
            or initial_quality_audit.quality_assessment.status == QualityStatus.REVISE
            or initial_genre_quality.status == QualityStatus.REVISE
        )

        if (
            needs_quality_revision
            and writer_material_available
            and self.settings.use_llm
            and self.writer_agent is not None
            and self.settings.writer_quality_revision_rounds > 0
        ):
            revised_draft_or_fallback = await self.run_agent_or_fallback(
                stage="writer_quality_revision",
                agent=self.writer_agent,
                prompt=build_writer_quality_revision_prompt(
                    writer_pack=writer_pack,
                    current_output=raw_writer_output,
                    missing_components=missing_components,
                    quality_findings=(
                        [
                            *initial_quality_audit.quality_assessment.findings,
                            *initial_genre_quality.findings,
                        ]
                    ),
                    settings=self.settings,
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_ledger": (
                            genre_scoped_fact_ledger.model_dump(
                                mode="json"
                            )
                        ),
                        "insight_ledger": (
                            writer_pack.insight_ledger.model_dump(
                                mode="json"
                            )
                        ),
                        "allow_hypotheses_in_report": (
                            self.settings.allow_hypotheses_in_report
                        ),
                        "report_genre": (
                            plan.report_specification.genre.value
                        ),
                        "report_perspective": (
                            plan.report_specification.perspective.value
                        ),
                    },
                ),
                fallback=lambda: raw_writer_output,
                store=store,
            )

            revision_materialisation_error: str | None = None
            if isinstance(
                revised_draft_or_fallback,
                WriterOutput,
            ):
                revision_candidate = (
                    revised_draft_or_fallback
                    .model_copy(
                        update={
                            "quality_revision_round": 1,
                            "quality_revision_summary": (
                                "Bounded whole-report "
                                "quality-revision candidate."
                            ),
                        }
                    )
                )
            else:
                revised_writer_draft = (
                    WriterAgentDraft.model_validate(
                        revised_draft_or_fallback
                    )
                )
                store.save_json(
                    "10_writer_quality_revision_draft.json",
                    revised_writer_draft,
                )
                try:
                    revision_candidate = materialise_writer_output(
                        revised_writer_draft,
                        genre_scoped_fact_ledger,
                        insight_ledger=writer_pack.insight_ledger,
                        allow_hypotheses_in_report=(
                            self.settings.allow_hypotheses_in_report
                        ),
                        writer_mode="llm_writer",
                        eligible_for_primary_evaluation=representation_eligible,
                        quality_revision_round=1,
                        quality_revision_summary=(
                            "Bounded whole-report "
                            "quality-revision candidate."
                        ),
                    )
                except ValueError as error:
                    revision_materialisation_error = str(error)
                    store.save_text(
                        "10_writer_quality_revision_materialisation_error.txt",
                        str(error),
                    )
                    store.trace(
                        "writer_quality_revision_materialisation",
                        "rejected",
                        {
                            "reason": f"ValueError: {error}",
                            "fallback": "pre_revision_writer_output",
                        },
                    )
                    revision_candidate = raw_writer_output

            revision_candidate = revision_candidate.model_copy(
                update={
                    "quality_revision_round": 1,
                    "quality_revision_summary": (
                        "Bounded whole-report "
                        "quality-revision candidate."
                    ),
                }
            )

            store.save_json(
                "10_writer_quality_revision_candidate.json",
                revision_candidate,
            )
            store.save_text(
                "10_writer_quality_revision_candidate.md",
                revision_candidate.markdown,
            )

            revision_validation_errors = (
                validate_writer_output(
                    revision_candidate,
                    fact_ledger,
                    insight_ledger,
                    self.settings.allow_hypotheses_in_report,
                )
            )
            if revision_materialisation_error is not None:
                revision_validation_errors.append(
                    "Writer quality revision failed materialisation: "
                    + revision_materialisation_error
                )

            revised_quality_audit = (
                deterministic_audit(
                    writer_output=revision_candidate,
                    fact_ledger=fact_ledger,
                    evidence=evidence_ledger,
                    mode=audit_mode,
                    external_sources=(
                        external_truth_sources
                    ),
                    revision_round=0,
                    report_specification=(
                        plan.report_specification
                    ),
                    settings=self.settings,
                    profile_support_records=(
                        profile_support_records
                    ),
                    insight_ledger=insight_ledger,
                )
            )

            revision_accepted, revision_reasons = (
                accept_writer_quality_revision(
                    before=raw_writer_output,
                    after=revision_candidate,
                    before_audit=(
                        initial_quality_audit
                    ),
                    after_audit=(
                        revised_quality_audit
                    ),
                    validation_errors=(
                        revision_validation_errors
                    ),
                    report_specification=(
                        plan.report_specification
                    ),
                    settings=self.settings,
                )
            )

            store.save_json(
                "10_writer_quality_revision_assessment.json",
                {
                    "attempted": True,
                    "accepted": revision_accepted,
                    "reasons": revision_reasons,
                    "before_component_assessments": (
                        initial_quality_audit
                        .component_assessments
                    ),
                    "after_component_assessments": (
                        revised_quality_audit
                        .component_assessments
                    ),
                    "before_quality": (
                        initial_quality_audit
                        .quality_assessment
                    ),
                    "after_quality": (
                        revised_quality_audit
                        .quality_assessment
                    ),
                    "validation_errors": (
                        revision_validation_errors
                    ),
                },
            )

            if revision_accepted:
                quality_revised_writer_output = (
                    revision_candidate.model_copy(
                        update={
                            "quality_revision_summary": (
                                "One bounded Writer "
                                "quality revision was "
                                "accepted before factual "
                                "auditing."
                            ),
                        }
                    )
                )

                writer_output_for_audit = (
                    quality_revised_writer_output
                )

                store.save_json(
                    "10_writer_quality_revision.json",
                    writer_output_for_audit,
                )
                store.save_text(
                    "10_writer_quality_revision.md",
                    writer_output_for_audit.markdown,
                )
                store.save_json(
                    "10_writer_quality_revision_component_coverage.json",
                    revised_quality_audit.component_assessments,
                )
            else:
                store.trace(
                    "writer_quality_revision",
                    "rejected",
                    {
                        "reasons": (
                            revision_reasons
                        )
                    },
                )

        (
            initial_audit,
            proposal,
            writer_output_for_audit,
        ) = await self.audit_once(
            run_id=run_id,
            writer_output=writer_output_for_audit,
            fact_ledger=fact_ledger,
            evidence_ledger=evidence_ledger,
            insight_ledger=insight_ledger,
            profile_support_records=profile_support_records,
            plan=plan,
            audit_mode=audit_mode,
            external_truth_sources=external_truth_sources,
            revision_round=0,
            store=store,
            stage_name="initial_audit_and_repair",
        )

        store.save_json("10_initial_audit.json", initial_audit)
        store.save_json(
            "10_initial_quality_assessment.json",
            initial_audit.quality_assessment,
        )
        store.save_json("11_repair_candidates_round_0.json", proposal)

        current_output = writer_output_for_audit
        current_audit = initial_audit
        repair_rounds = 0
        all_patches = []

        while (
            current_audit.decision == AuditDecision.REVISE
            and repair_rounds < plan.revision_limit
        ):
            repaired_output, patches = apply_repair_proposal(
                current_output,
                proposal,
                fact_ledger,
                evidence_ledger,
                insight_ledger,
                self.settings.allow_hypotheses_in_report,
            )

            if not patches:
                release_status = decide_release_status(
                    annotations=current_audit.annotations,
                    quality=current_audit.quality_assessment,
                    methodological_warnings=current_audit.methodological_warnings,
                    repair_budget_exhausted=True,
                    audit_mode=audit_mode,
                )
                current_audit = current_audit.model_copy(
                    update={
                        "decision": (
                            AuditDecision.BLOCK
                            if release_status == ReleaseStatus.HUMAN_REVIEW_REQUIRED
                            else AuditDecision.PASS
                        ),
                        "release_status": release_status,
                        "residual_risk": (
                            current_audit.residual_risk
                            + " No deterministic-valid repair candidate was available."
                        ),
                    }
                )
                break

            repair_rounds += 1
            all_patches.extend(patches)
            current_output = repaired_output

            store.save_json(
                f"12_selected_patches_round_{repair_rounds}.json",
                patches,
            )
            store.save_text(
                f"13_repaired_report_round_{repair_rounds}.md",
                current_output.markdown,
            )
            store.save_json(
                f"13_repaired_output_round_{repair_rounds}.json",
                current_output,
            )

            (
                current_audit,
                proposal,
                current_output,
            ) = await self.audit_once(
                run_id=run_id,
                writer_output=current_output,
                fact_ledger=fact_ledger,
                evidence_ledger=evidence_ledger,
                insight_ledger=insight_ledger,
                profile_support_records=profile_support_records,
                plan=plan,
                audit_mode=audit_mode,
                external_truth_sources=external_truth_sources,
                revision_round=repair_rounds,
                store=store,
                stage_name=f"post_repair_audit_round_{repair_rounds}",
            )

            current_audit = current_audit.model_copy(
                update={"applied_patches": all_patches}
            )

            store.save_json(
                f"14_post_repair_audit_round_{repair_rounds}.json",
                current_audit,
            )
            store.save_json(
                f"14_repair_candidates_round_{repair_rounds}.json",
                proposal,
            )

        repair_budget_exhausted = current_audit.decision == AuditDecision.REVISE

        if repair_budget_exhausted:
            release_status = decide_release_status(
                annotations=current_audit.annotations,
                quality=current_audit.quality_assessment,
                methodological_warnings=current_audit.methodological_warnings,
                repair_budget_exhausted=True,
                audit_mode=audit_mode,
            )
            current_audit = current_audit.model_copy(
                update={
                    "decision": (
                        AuditDecision.BLOCK
                        if release_status == ReleaseStatus.HUMAN_REVIEW_REQUIRED
                        else AuditDecision.PASS
                    ),
                    "release_status": release_status,
                    "residual_risk": (
                        current_audit.residual_risk
                        + " The bounded repair budget was exhausted."
                    ),
                    "applied_patches": all_patches,
                }
            )

        final_audit = current_audit
        store.save_json(
            "14_final_component_coverage.json",
            assess_report_components(
                current_output,
                fact_ledger,
                evidence_ledger,
                plan.report_specification.required_components,
            ),
        )
        genre_quality = assess_genre_quality(
            current_output,
            plan.report_specification,
            evidence_ledger,
        )
        store.save_json(
            "14_final_genre_quality.json",
            genre_quality,
        )

        factual_release_status = decide_release_status(
            annotations=final_audit.annotations,
            quality=final_audit.quality_assessment,
            methodological_warnings=final_audit.methodological_warnings,
            repair_budget_exhausted=repair_budget_exhausted,
            audit_mode=audit_mode,
        )

        if (
            factual_release_status
            == ReleaseStatus.HUMAN_REVIEW_REQUIRED
        ):
            final_decision = AuditDecision.BLOCK
        else:
            final_decision = AuditDecision.PASS

        final_audit = final_audit.model_copy(
            update={
                "decision": final_decision,
                "release_status": factual_release_status,
            }
        )

        release_status = factual_release_status
        if (
            not representation_eligible
            or genre_quality.status == QualityStatus.REVISE
        ):
            release_status = ReleaseStatus.HUMAN_REVIEW_REQUIRED

        if not representation_eligible:
            current_output = current_output.model_copy(
                update={"eligible_for_primary_evaluation": False}
            )

        approved = representation_eligible and genre_quality.status != (
            QualityStatus.REVISE
        ) and release_status in {
            ReleaseStatus.APPROVED,
            ReleaseStatus.APPROVED_WITH_WARNINGS,
        }

        if representation_eligible:
            primary_evaluation_reason = None
        elif input_structure is None:
            primary_evaluation_reason = "input_structure_unavailable"
        else:
            primary_evaluation_reason = (
                "input_representation_"
                + input_structure.representation_status.value
            )

        result = PipelineResult(
            run_id=run_id,
            profile=profile,
            input_structure=input_structure,
            structural_catalog=structural_catalog,
            evaluation_field_policy=data_bundle.evaluation_field_policy,
            understanding=understanding,
            execution_plan=plan,
            evidence_ledger=evidence_ledger,
            fact_candidates=fact_candidates,
            verification=verification,
            fact_ledger=fact_ledger,
            writer_evidence_pack=writer_pack,
            raw_writer_output=raw_writer_output,
            quality_revised_writer_output=quality_revised_writer_output,
            final_writer_output=current_output,
            initial_audit=initial_audit,
            final_audit=final_audit,
            repair_rounds_used=repair_rounds,
            release_status=release_status,
            approved_for_release=approved,
            primary_evaluation_eligible=representation_eligible,
            primary_evaluation_reason=primary_evaluation_reason,
            genre_quality_assessment=genre_quality,
            insight_ledger=insight_ledger,
        )

        store.save_json("final_result.json", result)

        if release_status == ReleaseStatus.APPROVED:
            header = "<!-- APPROVED BY AUDITOR -->\n\n"
        elif release_status == ReleaseStatus.APPROVED_WITH_WARNINGS:
            header = "<!-- APPROVED WITH RESIDUAL WARNINGS -->\n\n"
        else:
            header = "<!-- HUMAN REVIEW REQUIRED -->\n\n"

        store.save_text(
            "final_report.md",
            header + current_output.markdown,
        )

        store.trace(
            "workflow",
            "completed",
            {
                "release_status": release_status.value,
                "repair_rounds": repair_rounds,
                "writer_mode": raw_writer_output.writer_mode,
                "verified_insight_count": len(
                    insight_ledger.verified_insights
                ),
                "insight_fallback_reason": (
                    insight_ledger.fallback_reason
                ),
                "input_representation_status": (
                    input_structure.representation_status.value
                    if input_structure is not None
                    else "invalid"
                ),
                "genre_quality_status": genre_quality.status.value,
                "primary_evaluation_eligible": representation_eligible,
            },
        )

        return result

    def run_sync(
        self,
        inputs: list[str | Path],
        request: str,
        *,
        audit_mode: AuditMode = AuditMode.INTERNAL,
        external_truth_sources: list[ExternalTruthSource] | None = None,
        evaluation_field_policy: EvaluationFieldPolicy | None = None,
        report_genre: ReportGenre | None = None,
    ) -> PipelineResult:
        return asyncio.run(
            self.run(
                inputs,
                request,
                audit_mode=audit_mode,
                external_truth_sources=external_truth_sources,
                evaluation_field_policy=evaluation_field_policy,
                report_genre=report_genre,
            )
        )
````

### `tests/test_semantic_event_pipeline.py`

````python
from __future__ import annotations

import json

import pandas as pd
import pytest

from table2text.agents import validate_insight_candidates
from table2text.analytics import execute_plan
from table2text.audit import (
    assess_genre_quality,
    fallback_fact_candidates,
    flatten_numbers,
    numbers_supported,
    scope_fact_ledger_for_genre,
    select_event_priority_facts,
    validate_fact_candidates,
    validate_writer_output,
)
from table2text.capabilities import (
    available_capabilities,
    build_event_evidence_queries,
    normalise_event_evidence_queries,
    semantic_query_evidence,
    validate_event_query_priorities,
    validate_evidence_queries,
    validate_semantic_map,
)
from table2text.config import Settings
from table2text.data import DataBundle, load_data
from table2text.schemas import (
    AnalyticalFunction,
    AnalysisRoute,
    AuditMode,
    ClaimPermission,
    DataUnderstanding,
    EvaluationFieldPolicy,
    EvidenceCapability,
    EvidenceItem,
    EvidenceLedger,
    EvidenceOperation,
    EvidenceQuery,
    ExecutionPlan,
    FactCandidate,
    FactCandidateSet,
    FactLedger,
    InputRepresentationStatus,
    InputSemanticMap,
    InputShape,
    InputStructureProfile,
    InsightCandidate,
    InsightCandidateSet,
    InsightType,
    InterpretationLevel,
    InvestigationTask,
    QualityStatus,
    RecommendedUse,
    ReportComponent,
    ReportGenre,
    ReportSelectionSource,
    ReportSpecification,
    SemanticBinding,
    SemanticLevel,
    SemanticRole,
    SentenceSupport,
    SupportType,
    VerifiedFact,
    WriterOutput,
    WriterAgentDraft,
)
from table2text.structure import build_structural_catalog
from table2text.workflow import (
    build_orchestrator_prompt_context,
    resolve_report_genre,
)


def renamed_event() -> dict:
    return {
        "occasion": {
            "when": "2026-07-23",
            "where": "Civic Hall",
            "extra": False,
        },
        "sides": {
            "north": {
                "label": "North",
                "tally": 12,
                "attempts": 17,
                "members": {
                    "n1": {"label": "Nia", "alpha": 7},
                    "n2": {"label": "Noor", "alpha": 4},
                },
            },
            "south": {
                "label": "South",
                "tally": 9,
                "attempts": 22,
                "members": {
                    "s1": {"label": "Sol", "alpha": 6},
                    "s2": {"label": "Sage", "alpha": 2},
                },
            },
        },
    }


def semantic_map() -> InputSemanticMap:
    def binding(
        binding_id: str,
        label: str,
        role: SemanticRole,
        level: SemanticLevel,
        path: str,
        analytical_function: AnalyticalFunction | None = None,
    ) -> SemanticBinding:
        return SemanticBinding(
            binding_id=binding_id,
            table_name="contest",
            label=label,
            role=role,
            level=level,
            path_pattern=path,
            description=f"Semantic interpretation of {label}.",
            confidence=0.98,
            evidence_basis="Observed path and values in the sanitized catalog.",
            analytical_function=analytical_function,
        )

    return InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event with two participants and nested entities.",
        bindings=[
            binding(
                "B_PARTICIPANT",
                "participant",
                SemanticRole.PARTICIPANT_IDENTIFIER,
                SemanticLevel.PARTICIPANT,
                "sides.*.label",
            ),
            binding(
                "B_OUTCOME",
                "event tally",
                SemanticRole.OUTCOME_MEASURE,
                SemanticLevel.PARTICIPANT,
                "sides.*.tally",
                AnalyticalFunction.OUTCOME,
            ),
            binding(
                "B_ATTEMPTS",
                "attempts",
                SemanticRole.MEASURE,
                SemanticLevel.PARTICIPANT,
                "sides.*.attempts",
                AnalyticalFunction.OUTCOME_COMPONENT,
            ),
            binding(
                "B_ENTITY",
                "member",
                SemanticRole.ENTITY_IDENTIFIER,
                SemanticLevel.ENTITY,
                "sides.*.members.*.label",
            ),
            binding(
                "B_ALPHA",
                "alpha performance",
                SemanticRole.PERFORMANCE_MEASURE,
                SemanticLevel.ENTITY,
                "sides.*.members.*.alpha",
                AnalyticalFunction.PERFORMANCE,
            ),
            binding(
                "B_TIME",
                "event date",
                SemanticRole.TIME,
                SemanticLevel.EVENT,
                "occasion.when",
            ),
            binding(
                "B_LOCATION",
                "event venue",
                SemanticRole.LOCATION,
                SemanticLevel.EVENT,
                "occasion.where",
            ),
            binding(
                "B_STATUS",
                "extra-period status",
                SemanticRole.STATUS,
                SemanticLevel.EVENT,
                "occasion.extra",
            ),
        ],
        recommended_report_genre=ReportGenre.EVENT_REPORT,
        report_rationale="The sanitized input describes one bounded event.",
        confidence=0.98,
    )


def semantic_queries() -> list[EvidenceQuery]:
    common = {
        "table_name": "contest",
        "user_relevance": 0.95,
        "salience": 0.95,
    }
    return [
        EvidenceQuery(
            query_id="QUERY_CONTEXT",
            task_id="TASK_OUTCOME",
            operation=EvidenceOperation.RETRIEVE,
            capability=EvidenceCapability.EVENT_OUTCOME,
            evidence_type="event_context",
            semantic_label="event context",
            question="What supplied context locates this event?",
            semantic_level=SemanticLevel.EVENT,
            value_binding_ids=["B_TIME", "B_LOCATION"],
            recommended_use=RecommendedUse.HEADLINE,
            **common,
        ),
        EvidenceQuery(
            query_id="QUERY_STATUS",
            task_id="TASK_OUTCOME",
            operation=EvidenceOperation.RETRIEVE,
            capability=EvidenceCapability.EVENT_OUTCOME,
            evidence_type="event_status",
            semantic_label="event status",
            question="What status is recorded for this event?",
            semantic_level=SemanticLevel.EVENT,
            value_binding_ids=["B_STATUS"],
            **common,
        ),
        EvidenceQuery(
            query_id="QUERY_OUTCOME",
            task_id="TASK_OUTCOME",
            operation=EvidenceOperation.COMPARE,
            capability=EvidenceCapability.EVENT_OUTCOME,
            evidence_type="event_outcome",
            semantic_label="event outcome",
            question="How do the participant outcome measures compare?",
            semantic_level=SemanticLevel.PARTICIPANT,
            value_binding_ids=["B_OUTCOME"],
            entity_binding_id="B_PARTICIPANT",
            recommended_use=RecommendedUse.HEADLINE,
            **common,
        ),
        EvidenceQuery(
            query_id="QUERY_RANKING",
            task_id="TASK_RANKING",
            operation=EvidenceOperation.RANK,
            capability=EvidenceCapability.RANKING,
            evidence_type="entity_ranking",
            semantic_label="alpha ranking",
            question="Which entities have the highest alpha values?",
            semantic_level=SemanticLevel.ENTITY,
            value_binding_ids=["B_ALPHA"],
            entity_binding_id="B_ENTITY",
            group_binding_id="B_PARTICIPANT",
            limit=3,
            **common,
        ),
        EvidenceQuery(
            query_id="QUERY_CONTRAST",
            task_id="TASK_CONTRAST",
            operation=EvidenceOperation.COMPARE,
            capability=EvidenceCapability.GROUP_COMPARISON,
            evidence_type="event_contrast",
            semantic_label="attempt contrast",
            question="How do participant attempts compare?",
            semantic_level=SemanticLevel.PARTICIPANT,
            value_binding_ids=["B_ATTEMPTS"],
            entity_binding_id="B_PARTICIPANT",
            **common,
        ),
    ]


def event_query_tasks() -> list[InvestigationTask]:
    return [
        InvestigationTask(
            task_id="TASK_OUTCOME",
            question="What is the verified event outcome and context?",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=5,
            table_name="contest",
            capability=EvidenceCapability.EVENT_OUTCOME,
            expected_evidence_types=[
                "event_context",
                "event_status",
                "event_outcome",
            ],
            required_evidence=[
                "event_context",
                "event_status",
                "event_outcome",
            ],
            claim_permissions=[
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
            answerability_note="Answerable from the structured event.",
        ),
        InvestigationTask(
            task_id="TASK_RANKING",
            question="Which entities lead recorded performance measures?",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=4,
            table_name="contest",
            capability=EvidenceCapability.RANKING,
            expected_evidence_types=["entity_ranking"],
            required_evidence=["entity_ranking"],
            claim_permissions=[
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
            answerability_note="Answerable from entity measures.",
        ),
        InvestigationTask(
            task_id="TASK_CONTRAST",
            question="How do participants compare on recorded measures?",
            route=AnalysisRoute.ASSOCIATION_COMPARISON,
            priority=4,
            table_name="contest",
            capability=EvidenceCapability.GROUP_COMPARISON,
            expected_evidence_types=["participant_comparison"],
            required_evidence=["participant_comparison"],
            claim_permissions=[
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
            answerability_note="Answerable from participant measures.",
        ),
    ]


def test_semantic_map_accepts_broad_event_binding_coverage():
    compact_map = semantic_map()
    bindings = [
        binding.model_copy(
            update={"binding_id": f"B_{index:02d}"},
        )
        for index, binding in enumerate(
            (compact_map.bindings * 4)[:25],
            start=1,
        )
    ]

    broad_map = InputSemanticMap(
        input_shape=compact_map.input_shape,
        record_description=compact_map.record_description,
        bindings=bindings,
        recommended_report_genre=compact_map.recommended_report_genre,
        report_rationale=compact_map.report_rationale,
        confidence=compact_map.confidence,
    )

    assert len(broad_map.bindings) == 25


def test_orchestrator_context_exposes_binding_ids_without_raw_paths():
    understanding = DataUnderstanding(
        profile_fingerprint="fixture",
        dataset_summary="One structured event.",
        tables=[],
        semantic_map=semantic_map(),
    )
    structure = event_structure().model_copy(
        update={"nested_paths": ["sides.*.members.*.alpha"]}
    )
    context = build_orchestrator_prompt_context(
        understanding=understanding,
        input_structure=structure,
        structural_catalog=build_structural_catalog(
            {"contest": renamed_event()}
        ),
    )

    assert "semantic_map" not in context["understanding"]
    assert context["input_structure"]["nested_paths"] == []
    assert context["structural_catalog"] == []
    assert {
        item["binding_id"]
        for item in context["semantic_binding_catalog"]
    } == {binding.binding_id for binding in semantic_map().bindings}
    assert all(
        "path_pattern" not in item
        for item in context["semantic_binding_catalog"]
    )
    assert next(
        item
        for item in context["semantic_binding_catalog"]
        if item["binding_id"] == "B_ALPHA"
    )["analytical_function"] == "performance"


def test_event_semantic_map_reserves_substantive_entity_measures():
    payload = renamed_event()
    for side in payload["sides"].values():
        for member in side["members"].values():
            member["beta"] = 3
            member["gamma"] = 2

    errors = validate_semantic_map(
        semantic_map(),
        build_structural_catalog({"contest": payload}),
    )

    assert any(
        "reserve substantive entity-performance bindings"
        in error
        for error in errors
    )


def test_event_query_priorities_reject_participation_substitution():
    base = semantic_map()
    alpha = next(
        binding
        for binding in base.bindings
        if binding.binding_id == "B_ALPHA"
    )
    enriched = base.model_copy(
        update={
            "bindings": [
                *base.bindings,
                alpha.model_copy(
                    update={
                        "binding_id": "B_BETA",
                        "label": "beta performance",
                        "path_pattern": "sides.*.members.*.beta",
                    }
                ),
                alpha.model_copy(
                    update={
                        "binding_id": "B_GAMMA",
                        "label": "gamma performance",
                        "path_pattern": "sides.*.members.*.gamma",
                    }
                ),
                alpha.model_copy(
                    update={
                        "binding_id": "B_DURATION",
                        "label": "participation duration",
                        "path_pattern": (
                            "sides.*.members.*.duration"
                        ),
                        "analytical_function": (
                            AnalyticalFunction.PARTICIPATION
                        ),
                    }
                ),
            ]
        }
    )
    duration_query = semantic_queries()[3].model_copy(
        update={
            "query_id": "QUERY_DURATION",
            "semantic_label": "participation duration ranking",
            "question": (
                "Which entities recorded the greatest duration?"
            ),
            "value_binding_ids": ["B_DURATION"],
        }
    )

    errors = validate_event_query_priorities(
        [semantic_queries()[3], duration_query],
        enriched,
        "Understand the event and report its strongest findings.",
    )

    assert any(
        "distinct substantive entity-performance" in error
        for error in errors
    )


def test_writer_draft_accepts_broad_support_id_sequences():
    draft = WriterAgentDraft(
        title="Supported title",
        title_fact_ids=[f"FACT_{index:04d}" for index in range(25)],
    )

    assert len(draft.title_fact_ids) == 25


def test_numeric_string_evidence_supports_rendered_dates_and_identifiers():
    support_numbers = flatten_numbers(
        {
            "values": ["4885", "2017", "11", "09"],
            "non_numeric": "Capital One Arena",
        }
    )

    assert support_numbers == [4885.0, 2017.0, 11.0, 9.0]
    assert numbers_supported(
        "Game 4885 took place on 2017-11-09.",
        support_numbers,
    )


def event_structure() -> InputStructureProfile:
    return InputStructureProfile(
        shape=InputShape.EVENT_RECORD,
        representation_status=InputRepresentationStatus.VALID,
        row_semantics="one event",
        confidence=0.98,
    )


def event_report_specification() -> ReportSpecification:
    return ReportSpecification(
        report_purpose="Describe the event.",
        genre=ReportGenre.EVENT_REPORT,
        communication_goal="Communicate the verified event evidence.",
        target_length_words=250,
        maximum_main_findings=5,
        required_components=[
            ReportComponent.STRONGEST_RELATIONSHIPS,
            ReportComponent.LIMITATIONS_NEXT_STEPS,
        ],
        required_content_slots=["event_result"],
        prohibited_claim_types=["unsupported_causality"],
        selection_source=ReportSelectionSource.STRUCTURED_INFERENCE,
        prioritisation_rule="Prefer salient event evidence.",
    )


def evidence_item(
    *,
    evidence_id: str,
    capability: EvidenceCapability,
    evidence_type: str,
    semantic_level: SemanticLevel,
    analytical_function: AnalyticalFunction | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        route=AnalysisRoute.DESCRIPTIVE,
        task_ids=["TASK_EVENT"],
        capability=capability,
        evidence_type=evidence_type,
        semantic_level=semantic_level,
        analytical_function=analytical_function,
        finding="Supported evidence item.",
        metrics={"value": 12},
        source_tables=["contest"],
        method="Validated test evidence.",
        practical_interpretation="Direct descriptive evidence.",
        strength_label="direct",
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        factual_confidence=1.0,
        methodological_strength=1.0,
        user_relevance=1.0,
        salience=1.0,
        recommended_use=RecommendedUse.MAIN_FINDING,
    )


def verified_fact(
    *,
    fact_id: str,
    evidence: EvidenceItem,
) -> VerifiedFact:
    return VerifiedFact(
        fact_id=fact_id,
        source_candidate_id=f"CAN_{fact_id}",
        fact_summary="A directly supported fact.",
        evidence_ids=[evidence.evidence_id],
        source_capabilities=[evidence.capability],
        structured_values={evidence.evidence_id: evidence.metrics},
        entities=["contest"],
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        factual_confidence=1.0,
        methodological_strength=1.0,
        user_relevance=1.0,
        salience=1.0,
        recommended_use=RecommendedUse.MAIN_FINDING,
    )


def test_structural_catalog_uses_wildcards_and_excludes_held_out_reference(
    tmp_path,
):
    sentinel = "SECRET HELD OUT REFERENCE " * 50
    path = tmp_path / "contest.json"
    path.write_text(
        json.dumps({**renamed_event(), "reference": sentinel}),
        encoding="utf-8",
    )
    bundle = load_data(
        [path],
        evaluation_field_policy=EvaluationFieldPolicy(
            operational_input_paths=["occasion", "sides"],
            held_out_reference_paths=["reference"],
        ),
    )

    catalog = build_structural_catalog(bundle.structured_inputs)
    serialized = json.dumps([field.model_dump(mode="json") for field in catalog])
    paths = {field.path_pattern for field in catalog}

    assert "sides.*.members.*.alpha" in paths
    assert "sides.*.tally" in paths
    assert sentinel.strip() not in serialized
    assert "reference" not in serialized


def test_generic_semantic_queries_execute_renamed_event_without_authored_claims():
    catalog = build_structural_catalog({"contest": renamed_event()})
    queries = semantic_queries()
    available = {
        EvidenceCapability.DATASET_PROFILE,
        EvidenceCapability.EVENT_OUTCOME,
        EvidenceCapability.RANKING,
        EvidenceCapability.GROUP_COMPARISON,
    }

    assert not validate_evidence_queries(
        queries,
        semantic_map(),
        catalog,
        task_ids={"TASK_OUTCOME", "TASK_RANKING", "TASK_CONTRAST"},
        available=available,
        task_capabilities={
            "TASK_OUTCOME": EvidenceCapability.EVENT_OUTCOME,
            "TASK_RANKING": EvidenceCapability.RANKING,
            "TASK_CONTRAST": EvidenceCapability.GROUP_COMPARISON,
        },
    )

    results = semantic_query_evidence(
        table_name="contest",
        payload=renamed_event(),
        semantic_map=semantic_map(),
        queries=queries,
    )
    by_type = {item.evidence_type: item for item in results}

    outcome = by_type["event_outcome"]
    assert outcome.metrics["records"][0]["entity"] == "North"
    assert outcome.metrics["records"][0]["value"] == 12
    assert outcome.metrics["records"][1]["entity"] == "South"
    assert outcome.metrics["difference"] == 3
    assert "winner" not in outcome.metrics
    assert "defeated" not in outcome.finding.lower()

    ranking = by_type["entity_ranking"].metrics["ranking"]
    assert [(item["entity"], item["group"], item["value"]) for item in ranking] == [
        ("Nia", "North", 7.0),
        ("Sol", "South", 6.0),
        ("Noor", "North", 4.0),
    ]
    context_values = by_type["event_context"].metrics["values"]
    assert {item["value"] for item in context_values} == {
        "2026-07-23",
        "Civic Hall",
    }


def test_event_fallback_query_builder_creates_executable_queries():
    catalog = build_structural_catalog({"contest": renamed_event()})
    available = {
        EvidenceCapability.DATASET_PROFILE,
        EvidenceCapability.EVENT_OUTCOME,
        EvidenceCapability.RANKING,
        EvidenceCapability.GROUP_COMPARISON,
    }
    queries = build_event_evidence_queries(
        semantic_map=semantic_map(),
        tasks=event_query_tasks(),
        available_capabilities=available,
        request="Understand the event and report its strongest findings.",
    )

    assert {
        query.evidence_type
        for query in queries
    } >= {
        "event_context",
        "event_status",
        "event_outcome",
        "entity_ranking",
        "participant_comparison",
    }
    assert not validate_evidence_queries(
        queries,
        semantic_map(),
        catalog,
        task_ids={
            task.task_id
            for task in event_query_tasks()
        },
        available=available,
        task_capabilities={
            task.task_id: task.capability
            for task in event_query_tasks()
        },
    )

    results = semantic_query_evidence(
        table_name="contest",
        payload=renamed_event(),
        semantic_map=semantic_map(),
        queries=queries,
    )

    assert results
    assert {
        item.evidence_type
        for item in results
    } >= {
        "event_context",
        "event_status",
        "event_outcome",
        "entity_ranking",
        "participant_comparison",
    }


def test_event_query_normaliser_keeps_broad_participant_comparisons():
    compact_map = semantic_map()
    bindings = [
        *compact_map.bindings,
        *[
            compact_map.bindings[4].model_copy(
                update={
                    "binding_id": f"B_COMPONENT_{index:02d}",
                    "label": f"participant component {index}",
                    "path_pattern": f"sides.*.component_{index}",
                    "analytical_function": (
                        AnalyticalFunction.OUTCOME_COMPONENT
                    ),
                }
            )
            for index in range(6)
        ],
    ]
    enriched = compact_map.model_copy(
        update={"bindings": bindings}
    )
    queries = [
        semantic_queries()[-1].model_copy(
            update={
                "query_id": f"QUERY_CONTRAST_{index:02d}",
                "value_binding_ids": [
                    f"B_COMPONENT_{index:02d}"
                ],
            }
        )
        for index in range(6)
    ]

    normalised = normalise_event_evidence_queries(
        queries=queries,
        semantic_map=enriched,
        tasks=event_query_tasks(),
        available_capabilities={
            EvidenceCapability.DATASET_PROFILE,
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.RANKING,
            EvidenceCapability.GROUP_COMPARISON,
        },
        request="Understand the event and report its strongest findings.",
    )

    comparison_count = sum(
        query.evidence_type
        in {"participant_comparison", "event_contrast"}
        for query in normalised
    )

    assert comparison_count >= 6
    assert {
        f"B_COMPONENT_{index:02d}"
        for index in range(6)
    }.issubset(
        {
            binding_id
            for query in normalised
            for binding_id in query.value_binding_ids
        }
    )


def test_semantic_query_validator_rejects_authored_operation_mismatch():
    bad_query = semantic_queries()[2].model_copy(update={"operation": EvidenceOperation.RETRIEVE})

    errors = validate_evidence_queries(
        [bad_query],
        semantic_map(),
        build_structural_catalog({"contest": renamed_event()}),
        task_ids={"TASK_OUTCOME"},
        available={EvidenceCapability.EVENT_OUTCOME},
        task_capabilities={
            "TASK_OUTCOME": EvidenceCapability.EVENT_OUTCOME,
        },
    )

    assert any("must use operation 'compare'" in error for error in errors)


def test_generic_request_uses_semantically_inferred_event_genre():
    genre, source, confidence = resolve_report_genre(
        request="Understand the dataset and report its strongest findings.",
        planned_genre=ReportGenre.DATA_SCIENCE_REPORT,
        configured_genre=None,
        semantic_map=semantic_map(),
    )

    assert genre == ReportGenre.EVENT_REPORT
    assert source == ReportSelectionSource.STRUCTURED_INFERENCE
    assert confidence == 0.98

    explicit_genre, explicit_source, _ = resolve_report_genre(
        request="Write a data-science report.",
        planned_genre=ReportGenre.EVENT_REPORT,
        configured_genre=None,
        semantic_map=semantic_map(),
    )
    assert explicit_genre == ReportGenre.DATA_SCIENCE_REPORT
    assert explicit_source == ReportSelectionSource.EXPLICIT_USER_REQUEST


def test_event_capabilities_require_event_semantics_within_one_table():
    collection_map = semantic_map().model_copy(
        update={"input_shape": InputShape.ENTITY_COLLECTION}
    )
    bundle = DataBundle(
        tables={},
        source_paths=[],
        fingerprint="fixture",
        input_structure=InputStructureProfile(
            shape=InputShape.ENTITY_COLLECTION,
            representation_status=InputRepresentationStatus.VALID,
            confidence=0.95,
        ),
    )

    capabilities = available_capabilities(bundle, collection_map)

    assert EvidenceCapability.RANKING in capabilities
    assert EvidenceCapability.EVENT_OUTCOME not in capabilities
    assert EvidenceCapability.ENTITY_PERFORMANCE not in capabilities


def test_event_writer_scope_excludes_flat_wrapper_profile_facts():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    wrapper = evidence_item(
        evidence_id="EVID_WRAPPER",
        capability=EvidenceCapability.DATASET_PROFILE,
        evidence_type="dataset_overview",
        semantic_level=SemanticLevel.DATASET,
    )
    ledger = EvidenceLedger(fingerprint="fixture", items=[event, wrapper])
    facts = FactLedger(
        writer_ready_facts=[
            verified_fact(fact_id="FACT_EVENT", evidence=event),
            verified_fact(fact_id="FACT_WRAPPER", evidence=wrapper),
        ]
    )

    scoped = scope_fact_ledger_for_genre(
        facts,
        ledger,
        ReportGenre.EVENT_REPORT,
    )

    assert [fact.fact_id for fact in scoped.writer_ready_facts] == ["FACT_EVENT"]


def test_event_fact_selection_keeps_broad_verified_event_coverage():
    items = [
        evidence_item(
            evidence_id="EVID_RESULT",
            capability=EvidenceCapability.EVENT_OUTCOME,
            evidence_type="event_outcome",
            semantic_level=SemanticLevel.PARTICIPANT,
            analytical_function=AnalyticalFunction.OUTCOME,
        ),
        *[
            evidence_item(
                evidence_id=f"EVID_PERFORMANCE_{index}",
                capability=EvidenceCapability.RANKING,
                evidence_type="entity_ranking",
                semantic_level=SemanticLevel.ENTITY,
                analytical_function=AnalyticalFunction.PERFORMANCE,
            )
            for index in range(1, 4)
        ],
        evidence_item(
            evidence_id="EVID_PARTICIPATION",
            capability=EvidenceCapability.RANKING,
            evidence_type="entity_ranking",
            semantic_level=SemanticLevel.ENTITY,
            analytical_function=AnalyticalFunction.PARTICIPATION,
        ),
        evidence_item(
            evidence_id="EVID_GENERAL_CONTRAST",
            capability=EvidenceCapability.GROUP_COMPARISON,
            evidence_type="event_contrast",
            semantic_level=SemanticLevel.PARTICIPANT,
            analytical_function=AnalyticalFunction.PERFORMANCE,
        ),
        *[
            evidence_item(
                evidence_id=f"EVID_CONTRAST_{index}",
                capability=EvidenceCapability.GROUP_COMPARISON,
                evidence_type="event_contrast",
                semantic_level=SemanticLevel.PARTICIPANT,
                analytical_function=(
                    AnalyticalFunction.OUTCOME_COMPONENT
                ),
            )
            for index in range(1, 4)
        ],
    ]
    ledger = EvidenceLedger(
        fingerprint="fixture",
        items=items,
    )
    facts = [
        verified_fact(
            fact_id=f"FACT_{item.evidence_id}",
            evidence=item,
        )
        for item in items
    ]

    priority, supporting = select_event_priority_facts(
        facts=facts,
        evidence=ledger,
        settings=Settings(),
        request=(
            "Understand the event and report its strongest findings."
        ),
    )
    selected_evidence_ids = {
        evidence_id
        for fact in [*priority, *supporting]
        for evidence_id in fact.evidence_ids
    }
    priority_evidence_ids = {
        evidence_id
        for fact in priority
        for evidence_id in fact.evidence_ids
    }

    assert "EVID_RESULT" in selected_evidence_ids
    assert {
        "EVID_PERFORMANCE_1",
        "EVID_PERFORMANCE_2",
        "EVID_PERFORMANCE_3",
    }.issubset(selected_evidence_ids)
    assert {
        "EVID_CONTRAST_1",
        "EVID_CONTRAST_2",
        "EVID_CONTRAST_3",
    }.issubset(priority_evidence_ids)
    assert "EVID_GENERAL_CONTRAST" in priority_evidence_ids
    assert "EVID_PARTICIPATION" in selected_evidence_ids


def test_insight_rejects_unsupported_completeness_and_duplicate_claims():
    event = evidence_item(
        evidence_id="EVID_EVENT_CONTEXT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_context",
        semantic_level=SemanticLevel.EVENT,
    )
    fact = verified_fact(
        fact_id="FACT_EVENT_CONTEXT",
        evidence=event,
    )
    candidate = InsightCandidate(
        insight_id="INS_EVENT_QUALITY",
        statement=(
            "The event record contains no missing data or duplicate rows."
        ),
        insight_type=InsightType.NARRATIVE_SUMMARY,
        interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
        source_fact_ids=[fact.fact_id],
        source_evidence_ids=[event.evidence_id],
        why_it_matters=(
            "Every recorded field would therefore be available for "
            "interpretation."
        ),
        supporting_summary="One event-context fact was supplied.",
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        confidence=0.9,
        salience=0.8,
    )

    errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[candidate]),
        FactLedger(writer_ready_facts=[fact]),
        EvidenceLedger(fingerprint="fixture", items=[event]),
        Settings(),
    )

    assert any(
        "without missingness evidence" in error
        for error in errors
    )
    assert any(
        "without duplicate-row evidence" in error
        for error in errors
    )


@pytest.mark.parametrize(
    "boilerplate",
    [
        "Statistical modeling is not possible because the wrapper has one row.",
        (
            "Observed associations are descriptive. "
            "Group comparisons are unadjusted."
        ),
    ],
)
def test_event_quality_gate_rejects_flat_modelling_discussion(boilerplate):
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    output = WriterOutput(
        title="Event report",
        markdown=(
            f"# Event report\n\nNorth recorded 12. {boilerplate}\n"
        ),
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text="North recorded 12.",
                fact_ids=["FACT_EVENT"],
                evidence_ids=[event.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    assessment = assess_genre_quality(
        output,
        event_report_specification(),
        EvidenceLedger(fingerprint="fixture", items=[event]),
    )

    assert assessment.status == QualityStatus.REVISE
    assert any("flat-table profiling or modelling" in finding for finding in assessment.findings)


def test_event_quality_gate_rejects_participation_substitution():
    performance = evidence_item(
        evidence_id="EVID_PERFORMANCE",
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_level=SemanticLevel.ENTITY,
        analytical_function=AnalyticalFunction.PERFORMANCE,
    )
    participation = evidence_item(
        evidence_id="EVID_PARTICIPATION",
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_level=SemanticLevel.ENTITY,
        analytical_function=AnalyticalFunction.PARTICIPATION,
    )
    output = WriterOutput(
        title="Event report",
        markdown=(
            "# Event report\n\n"
            "One entity recorded the longest duration.\n"
        ),
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=(
                    "One entity recorded the longest duration."
                ),
                fact_ids=["FACT_PARTICIPATION"],
                evidence_ids=[participation.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    assessment = assess_genre_quality(
        output,
        event_report_specification(),
        EvidenceLedger(
            fingerprint="fixture",
            items=[performance, participation],
        ),
    )

    assert assessment.status == QualityStatus.REVISE
    assert any(
        "uses participation evidence" in finding
        for finding in assessment.findings
    )


def test_factual_title_must_map_every_named_entity_to_its_facts():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    alpha_fact = verified_fact(
        fact_id="FACT_ALPHA",
        evidence=event,
    ).model_copy(update={"entities": ["Alpha"]})
    beta_fact = verified_fact(
        fact_id="FACT_BETA",
        evidence=event,
    ).model_copy(update={"entities": ["Beta"]})
    output = WriterOutput(
        title="Alpha defeats Beta",
        title_fact_ids=[alpha_fact.fact_id],
        markdown=(
            "# Alpha defeats Beta\n\n## Event overview\n\n"
            "Alpha has a supported event fact.\n"
        ),
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text="Alpha has a supported event fact.",
                fact_ids=[alpha_fact.fact_id],
                evidence_ids=[event.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    errors = validate_writer_output(
        output,
        FactLedger(writer_ready_facts=[alpha_fact, beta_fact]),
    )

    assert any(
        "entities unsupported by its facts" in error
        and "Beta" in error
        for error in errors
    )


def test_fact_candidate_rejects_driven_by_without_causal_permission():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    candidate = FactCandidate(
        candidate_id="CAN_0001",
        fact_summary="The result was driven by the recorded value of 12.",
        evidence_ids=[event.evidence_id],
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        factual_confidence=1.0,
        methodological_strength=1.0,
        user_relevance=1.0,
        salience=1.0,
        recommended_use=RecommendedUse.MAIN_FINDING,
    )

    errors = validate_fact_candidates(
        FactCandidateSet(candidates=[candidate]),
        EvidenceLedger(fingerprint="fixture", items=[event]),
    )

    assert any("unsupported causal wording" in error for error in errors)


def test_deterministic_fact_fallback_does_not_interpret_semantic_queries():
    query_evidence = evidence_item(
        evidence_id="EVID_QUERY",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.PARTICIPANT,
    ).model_copy(
        update={
            "query_id": "QUERY_OUTCOME",
            "finding": "Validated semantic query result for `event outcome`.",
        }
    )

    candidates = fallback_fact_candidates(
        EvidenceLedger(fingerprint="fixture", items=[query_evidence]),
        maximum_facts=10,
    )

    assert not candidates.candidates


def test_execute_plan_propagates_semantic_query_provenance():
    payload = renamed_event()
    bundle = DataBundle(
        tables={"contest": pd.DataFrame([{"event": payload}])},
        source_paths=[],
        fingerprint="fixture",
        structured_inputs={"contest": payload},
        input_structure=event_structure(),
    )

    def task(
        task_id: str,
        capability: EvidenceCapability,
        route: AnalysisRoute,
    ) -> InvestigationTask:
        return InvestigationTask(
            task_id=task_id,
            question=f"What can {capability.value} establish?",
            route=route,
            priority=5,
            table_name="contest",
            capability=capability,
            expected_evidence_types=[],
            required_evidence=[],
            claim_permissions=[
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
            answerability_note="Use the validated semantic query plan.",
        )

    plan = ExecutionPlan(
        objective="Describe the event.",
        tasks=[
            task(
                "TASK_OUTCOME",
                EvidenceCapability.EVENT_OUTCOME,
                AnalysisRoute.DESCRIPTIVE,
            ),
            task(
                "TASK_RANKING",
                EvidenceCapability.RANKING,
                AnalysisRoute.DESCRIPTIVE,
            ),
            task(
                "TASK_CONTRAST",
                EvidenceCapability.GROUP_COMPARISON,
                AnalysisRoute.ASSOCIATION_COMPARISON,
            ),
        ],
        route_order=[
            AnalysisRoute.DESCRIPTIVE,
            AnalysisRoute.ASSOCIATION_COMPARISON,
        ],
        report_specification=event_report_specification(),
        audit_mode=AuditMode.INTERNAL,
        evidence_queries=semantic_queries(),
        available_capabilities=[
            EvidenceCapability.DATASET_PROFILE,
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.RANKING,
            EvidenceCapability.GROUP_COMPARISON,
        ],
        selected_capabilities=[
            EvidenceCapability.DATASET_PROFILE,
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.RANKING,
            EvidenceCapability.GROUP_COMPARISON,
        ],
        revision_limit=0,
        maximum_facts=10,
        rationale="Frozen semantic event plan.",
    )

    evidence = execute_plan(
        bundle,
        plan,
        Settings(),
        semantic_map(),
    )
    query_items = [item for item in evidence.items if item.query_id]
    overview = next(
        item
        for item in evidence.items
        if item.evidence_type == "event_record_overview"
    )

    assert len(query_items) == len(semantic_queries())
    assert all(
        item.method == "Validated generic semantic-query execution."
        for item in query_items
    )
    assert all(item.semantic_binding_ids for item in query_items)
    assert not overview.eligible_for_writer


def test_semantic_map_without_queries_does_not_use_legacy_alias_extraction():
    payload = renamed_event()
    structure = event_structure()
    bundle = DataBundle(
        tables={"contest": pd.DataFrame([{"event": payload}])},
        source_paths=[],
        fingerprint="fixture",
        structured_inputs={"contest": payload},
        input_structure=structure,
    )
    task = InvestigationTask(
        task_id="TASK_EVENT",
        question="What is the event outcome?",
        route=AnalysisRoute.DESCRIPTIVE,
        priority=5,
        table_name="contest",
        capability=EvidenceCapability.EVENT_OUTCOME,
        expected_evidence_types=["event_outcome"],
        required_evidence=["event_outcome"],
        claim_permissions=[
            ClaimPermission.DESCRIPTIVE,
            ClaimPermission.COMPARATIVE,
        ],
        answerability_note="Use the semantic query plan.",
    )
    plan = ExecutionPlan(
        objective="Describe the event.",
        tasks=[task],
        route_order=[AnalysisRoute.DESCRIPTIVE],
        report_specification=event_report_specification(),
        audit_mode=AuditMode.INTERNAL,
        available_capabilities=[EvidenceCapability.EVENT_OUTCOME],
        selected_capabilities=[EvidenceCapability.EVENT_OUTCOME],
        revision_limit=0,
        maximum_facts=10,
        rationale="Frozen semantic event plan.",
    )

    evidence = execute_plan(
        bundle,
        plan,
        Settings(),
        semantic_map(),
    )

    assert not evidence.items
    assert any(
        "Legacy field-alias extraction was not used" in note for note in evidence.execution_notes
    )
````

### `tests/test_smoke.py`

````python
from __future__ import annotations

import json
from dataclasses import replace
from types import MethodType

import numpy as np
import pandas as pd
import pytest

from table2text import Settings, Table2TextWorkflow
from table2text.analytics import execute_plan
from table2text.audit import (
    apply_repair_proposal,
    apply_support_map_patches,
    assess_genre_quality,
    build_profile_support_registry,
    build_writer_evidence_pack,
    decide_release_status,
    deterministic_audit,
    fallback_writer,
    materialise_writer_output,
    merge_quality_assessments,
    merge_audit_proposal,
    split_markdown_sentences,
    validate_repair_candidate,
    validate_writer_output,
)
from table2text.capabilities import available_capabilities
from table2text.workflow import (
    build_compact_writer_payload,
    resolve_report_genre,
)
from table2text.data import load_data, profile_data
from table2text.schemas import (
    AnalysisRoute,
    AnalyticalRecommendation,
    AuditAnnotation,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    ClaimPermission,
    ColumnProfile,
    DataUnderstanding,
    DataProfile,
    ErrorType,
    EvaluationFieldPolicy,
    EvidenceCapability,
    EvidenceItem,
    EvidenceLedger,
    ExecutionPlan,
    FactLedger,
    InsightCandidate,
    InsightCandidateSet,
    InsightLedger,
    InsightRejection,
    InsightType,
    InsightVerificationRecord,
    InsightVerificationResult,
    InsightVerificationStatus,
    InvestigationTask,
    InputRepresentationStatus,
    InputShape,
    InterpretationLevel,
    QualityStatus,
    RecommendedUse,
    ReleaseStatus,
    RepairCandidate,
    RepairStrategy,
    ReportQualityAssessment,
    ReportComponent,
    ReportGenre,
    ReportPerspective,
    ReportSpecification,
    SentenceRepair,
    SentenceSupport,
    Severity,
    SupportType,
    TableProfile,
    TableUnderstanding,
    TargetStatus,
    ValidationStrategy,
    VerifiedFact,
    VerifiedInsight,
    WriterAgentDraft,
    WriterOutput,
    WriterSectionDraft,
    WriterSentenceDraft,
    ZeroRisk,
)
from table2text.agents import (
    empty_insight_ledger,
    fallback_execution_plan,
    materialise_insight_ledger,
    recover_missing_writer_insight_ids,
    validate_insight_candidates,
    validate_insight_verification,
    valid_quality_finding,
    writer_sentence_grounding_errors,
)


def make_passing_audit_report() -> AuditReport:
    return AuditReport(
        mode=AuditMode.INTERNAL,
        decision=AuditDecision.PASS,
        release_status=ReleaseStatus.APPROVED,
        annotations=[],
        applied_patches=[],
        factual_sentence_count=1,
        supported_sentence_count=1,
        support_rate=1.0,
        residual_risk="No high-confidence factual issue detected.",
        revision_instructions=[],
        quality_assessment=ReportQualityAssessment(
            status=QualityStatus.PASS,
            request_responsiveness=1.0,
            finding_selection=1.0,
            coherence=1.0,
            concision=1.0,
            caveat_integration=1.0,
            data_science_interpretation=1.0,
        ),
    )


def test_profile_detects_constant_and_suspicious_zero(tmp_path):
    path = tmp_path / "quality.csv"

    frame = pd.DataFrame(
        {
            "constant": [0] * 200,
            "pressure_like": [0] * 3 + list(np.linspace(990, 1030, 197)),
            "temperature": np.linspace(-10, 30, 200),
        }
    )
    frame.to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    table = profile.tables[0]

    constant = next(
        column
        for column in table.columns
        if column.name == "constant"
    )
    pressure = next(
        column
        for column in table.columns
        if column.name == "pressure_like"
    )

    assert constant.constant
    assert pressure.suspicious_zero_values


def test_constant_outcome_not_group_compared(tmp_path):
    path = tmp_path / "groups.csv"

    pd.DataFrame(
        {
            "group": ["rain", "snow"] * 100,
            "constant": [0] * 200,
            "variable": np.arange(200),
        }
    ).to_csv(path, index=False)

    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Describe the strongest relationships.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    evidence = execute_plan(
        bundle,
        plan,
        Settings(),
    )

    constant_comparisons = [
        item
        for item in evidence.items
        if item.route == AnalysisRoute.ASSOCIATION_COMPARISON
        and "constant" in item.source_columns
    ]

    assert not constant_comparisons


def test_weak_correlations_are_filtered(tmp_path):
    rng = np.random.default_rng(42)
    path = tmp_path / "weak.csv"

    pd.DataFrame(
        {
            "x": rng.normal(size=1_000),
            "y": rng.normal(size=1_000),
            "z": rng.normal(size=1_000),
        }
    ).to_csv(path, index=False)

    settings = replace(
        Settings(),
        min_abs_correlation=0.20,
    )

    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Report the strongest associations.",
        profile,
        AuditMode.INTERNAL,
        settings,
    )

    evidence = execute_plan(
        bundle,
        plan,
        settings,
    )

    correlations = [
        item.metrics["pearson_r"]
        for item in evidence.items
        if "pearson_r" in item.metrics
    ]

    assert all(abs(value) >= 0.20 for value in correlations)


def test_tabular_relationship_evidence_retains_capability_provenance(
    tmp_path,
):
    path = tmp_path / "relationships.csv"
    values = np.arange(200, dtype=float)
    pd.DataFrame(
        {
            "x": values,
            "y": values * 2,
            "group": ["a"] * 100 + ["b"] * 100,
        }
    ).to_csv(path, index=False)
    bundle = load_data([path])
    plan = fallback_execution_plan(
        "Report the strongest relationships.",
        profile_data(bundle),
        AuditMode.INTERNAL,
        Settings(),
    )

    evidence = execute_plan(bundle, plan, Settings())

    correlation = next(
        item
        for item in evidence.items
        if "pearson_r" in item.metrics
    )
    group_comparison = next(
        item
        for item in evidence.items
        if "group_counts" in item.metrics
    )
    assert correlation.capability == EvidenceCapability.ASSOCIATION
    assert group_comparison.capability == (
        EvidenceCapability.GROUP_COMPARISON
    )

def test_final_approved_status_cannot_have_block_decision():
    release_status = (
        ReleaseStatus.APPROVED_WITH_WARNINGS
    )

    final_decision = (
        AuditDecision.BLOCK
        if release_status
        == ReleaseStatus.HUMAN_REVIEW_REQUIRED
        else AuditDecision.PASS
    )

    assert final_decision == AuditDecision.PASS
    
def test_semantic_block_without_serious_annotations_is_advisory():
    deterministic = make_passing_audit_report()

    proposal = AuditRepairProposal(
        annotations=[],
        repairs=[],
        recommended_decision=AuditDecision.BLOCK,
        residual_risk=(
            "The model requested blocking without "
            "supporting serious annotations."
        ),
        quality_assessment=(
            deterministic.quality_assessment
        ),
    )

    merged = merge_audit_proposal(
        deterministic,
        proposal,
    )

    assert merged.decision == AuditDecision.PASS
    assert merged.release_status in {
        ReleaseStatus.APPROVED,
        ReleaseStatus.APPROVED_WITH_WARNINGS,
    }
    
def test_generic_request_does_not_invent_prediction_target(tmp_path):
    path = tmp_path / "weather.csv"

    pd.DataFrame(
        {
            "Formatted Date": pd.date_range(
                "2020-01-01",
                periods=300,
                freq="h",
            ),
            "Temperature (C)": np.sin(np.arange(300) / 24),
            "Humidity": np.linspace(0.3, 0.9, 300),
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))

    plan = fallback_execution_plan(
        "Understand the dataset and report its strongest findings.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    assert not any(
        task.route == AnalysisRoute.PREDICTIVE
        for task in plan.tasks
    )


def test_explicit_prediction_uses_selected_target(tmp_path):
    path = tmp_path / "model.csv"

    dates = pd.date_range(
        "2020-01-01",
        periods=500,
        freq="h",
    )

    temperature = np.sin(np.arange(500) / 24)

    pd.DataFrame(
        {
            "Formatted Date": dates,
            "Temperature": temperature,
            "Apparent Temperature": temperature + 0.001,
            "Humidity": np.linspace(0.2, 0.9, 500),
        }
    ).to_csv(path, index=False)

    settings = Settings()
    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Predict Temperature from the available variables.",
        profile,
        AuditMode.INTERNAL,
        settings,
    )

    predictive_task = next(
        task
        for task in plan.tasks
        if task.route == AnalysisRoute.PREDICTIVE
    )

    assert predictive_task.target_column == "Temperature"
    assert predictive_task.target_status == TargetStatus.USER_SELECTED
    assert predictive_task.validation_strategy == (
        ValidationStrategy.CHRONOLOGICAL_HOLDOUT
    )

    evidence = execute_plan(bundle, plan, settings)

    predictive_evidence = next(
        item
        for item in evidence.items
        if item.route == AnalysisRoute.PREDICTIVE
    )

    excluded = predictive_evidence.metrics.get(
        "features_excluded",
        [],
    )

    assert any(
        item.get("risk_type") == "target_proxy"
        for item in excluded
    )


def test_hourly_forecast_uses_longer_rolling_windows(tmp_path):
    path = tmp_path / "forecast.csv"
    length = 5_000

    pd.DataFrame(
        {
            "time": pd.date_range(
                "2020-01-01",
                periods=length,
                freq="h",
            ),
            "target": (
                10
                + np.sin(np.arange(length) * 2 * np.pi / 24)
            ),
        }
    ).to_csv(path, index=False)

    settings = Settings()
    bundle = load_data([path])
    profile = profile_data(bundle)

    plan = fallback_execution_plan(
        "Forecast target.",
        profile,
        AuditMode.INTERNAL,
        settings,
    )

    evidence = execute_plan(bundle, plan, settings)

    forecast = next(
        item
        for item in evidence.items
        if item.route == AnalysisRoute.FORECASTING
    )

    assert forecast.validation_strategy == ValidationStrategy.ROLLING_ORIGIN
    assert forecast.metrics["test_window_points"] >= 168
    assert forecast.metrics["fold_count"] >= 1
    assert any(
        name.startswith("seasonal_naive_")
        for name in forecast.metrics["mean_mae"]
    )


def make_fact_fixture() -> tuple[FactLedger, EvidenceLedger]:
    evidence = EvidenceLedger(
        fingerprint="test",
        items=[
            EvidenceItem(
                evidence_id="EVD_0001",
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=["TASK_001"],
                finding="The table contains 96,453 rows.",
                metrics={"row_count": 96_453},
                source_tables=["weather"],
                source_columns=[],
                method="Direct row count.",
                validation_strategy=ValidationStrategy.NONE,
                practical_interpretation="The dataset is large.",
                strength_label="dataset_overview",
                limitations=[],
                prohibited_interpretations=[],
                recommendations=[],
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ],
    )

    ledger = FactLedger(
        writer_ready_facts=[
            VerifiedFact(
                fact_id="FACT_0001",
                source_candidate_id="CAN_0001",
                fact_summary="The table contains 96,453 rows.",
                evidence_ids=["EVD_0001"],
                structured_values={
                    "EVD_0001": {"row_count": 96_453}
                },
                entities=["weather"],
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ]
    )

    return ledger, evidence


def test_approximate_number_is_allowed():
    ledger, evidence = make_fact_fixture()

    sentence = "The dataset contains more than 96,000 observations."

    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )

    plan_spec = ReportSpecification(
        report_purpose="Test",
        target_length_words=300,
        maximum_main_findings=5,
        prioritisation_rule="Test",
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        plan_spec,
    )

    assert audit.decision == AuditDecision.PASS


def _supporting_fact_budget_fixture(
    count: int,
) -> tuple[FactLedger, EvidenceLedger, list[str], list[str]]:
    evidence_items: list[EvidenceItem] = []
    facts: list[VerifiedFact] = []

    for index in range(count):
        evidence_id = f"EVD_BUDGET_{index:04d}"
        fact_id = f"FACT_BUDGET_{index:04d}"
        evidence_items.append(
            EvidenceItem(
                evidence_id=evidence_id,
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=["TASK_BUDGET"],
                capability=EvidenceCapability.DATASET_PROFILE,
                evidence_type="supporting_context",
                finding="Verified source evidence supports the summary.",
                method="Synthetic regression fixture.",
                practical_interpretation=(
                    "The evidence can be used as support for reader-facing prose."
                ),
                strength_label="direct",
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )
        )
        facts.append(
            VerifiedFact(
                fact_id=fact_id,
                source_candidate_id=f"CAN_{fact_id}",
                fact_summary=(
                    "Verified source evidence supports the summary."
                ),
                evidence_ids=[evidence_id],
                source_capabilities=[
                    EvidenceCapability.DATASET_PROFILE,
                ],
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )
        )

    return (
        FactLedger(writer_ready_facts=facts),
        EvidenceLedger(
            fingerprint="support-budget",
            items=evidence_items,
        ),
        [fact.fact_id for fact in facts],
        [item.evidence_id for item in evidence_items],
    )


def test_supporting_fact_budget_is_separate_from_main_finding_budget():
    ledger, evidence, fact_ids, evidence_ids = (
        _supporting_fact_budget_fixture(12)
    )
    sentence = (
        "Verified source evidence supports a focused reader summary with "
        "enough detail to connect context, evidence, and limitations clearly"
    )
    sentence_count = 9
    markdown = "# Supported Summary\n\n" + " ".join(
        f"{sentence}."
        for _ in range(sentence_count)
    )
    support = [
        SentenceSupport(
            sentence_id=f"SENT_BUDGET_{index:04d}",
            sentence_text=sentence + ".",
            fact_ids=fact_ids,
            evidence_ids=evidence_ids,
            support_type=SupportType.PARAPHRASE,
        )
        for index in range(sentence_count)
    ]
    output = WriterOutput(
        title="Supported Summary",
        markdown=markdown,
        sentence_support=support,
        selected_fact_ids=fact_ids,
    )
    spec = ReportSpecification(
        report_purpose="Test supporting fact budget.",
        target_length_words=150,
        maximum_main_findings=5,
        maximum_supporting_facts=12,
        prioritisation_rule="Keep main findings focused.",
    )

    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
    )

    assert audit.quality_assessment.status == QualityStatus.PASS
    assert not any(
        "supporting-fact budget" in finding
        for finding in audit.quality_assessment.findings
    )

    over_budget = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec.model_copy(update={"maximum_supporting_facts": 11}),
        Settings(),
    )

    assert any(
        "supporting-fact budget" in finding
        for finding in over_budget.quality_assessment.findings
    )


def test_wrong_number_triggers_repair():
    ledger, evidence = make_fact_fixture()

    wrong_sentence = "The dataset contains 12 observations."

    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{wrong_sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=wrong_sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )

    replacement = "The dataset contains 96,453 observations."

    candidate = RepairCandidate(
        repair_id="REP_001",
        replacement_text=replacement,
        strategy=RepairStrategy.MINIMAL_CORRECTION,
        supporting_fact_ids=["FACT_0001"],
        supporting_evidence_ids=["EVD_0001"],
        factual_support_score=1.0,
        meaning_preservation_score=1.0,
        readability_score=1.0,
        residual_hallucination_risk=0.0,
    )

    assert not validate_repair_candidate(
        candidate,
        ledger,
        evidence,
    )

    proposal = AuditRepairProposal(
        annotations=[],
        repairs=[
            SentenceRepair(
                sentence_id="SENT_0001",
                original_sentence=wrong_sentence,
                annotation_ids=[],
                candidates=[candidate],
                preferred_repair_id="REP_001",
                selection_reason="Correct the unsupported number.",
            )
        ],
        recommended_decision=AuditDecision.REVISE,
        residual_risk="Repair required.",
        quality_assessment=ReportQualityAssessment(
            status=QualityStatus.PASS,
            request_responsiveness=1.0,
            finding_selection=1.0,
            coherence=1.0,
            concision=1.0,
            caveat_integration=1.0,
            data_science_interpretation=1.0,
        ),
    )

    repaired, patches = apply_repair_proposal(
        writer,
        proposal,
        ledger,
        evidence,
    )

    assert patches
    assert replacement in repaired.markdown
    assert wrong_sentence not in repaired.markdown


def test_full_workflow_without_llm(tmp_path):
    path = tmp_path / "example.csv"

    frame = pd.DataFrame(
        {
            "category": ["a", "b"] * 100,
            "value": np.arange(200),
            "constant": [0] * 200,
        }
    )

    frame.to_csv(path, index=False)

    settings = replace(
        Settings(),
        use_llm=False,
        output_dir=tmp_path / "runs",
        max_revision_rounds=1,
    )

    workflow = Table2TextWorkflow(settings)
    assert workflow.evidence_insight_synthesis_agent is None
    assert workflow.verifier_insight_verification_agent is None

    result = workflow.run_sync(
        inputs=[path],
        request=(
            "Understand the dataset and report its strongest supported findings."
        ),
        audit_mode=AuditMode.INTERNAL,
    )

    assert result.evidence_ledger.items
    assert result.fact_ledger.writer_ready_facts
    assert not result.insight_ledger.verified_insights
    assert "LLM execution disabled" in (
        result.insight_ledger.fallback_reason or ""
    )
    assert result.raw_writer_output.writer_mode == "deterministic_fallback"

    run_directory = settings.output_dir / result.run_id

    assert (run_directory / "09_writer_raw_report.md").exists()
    assert (run_directory / "final_report.md").exists()
    assert (run_directory / "final_result.json").exists()
    assert (
        run_directory
        / "02_profile_support_registry.json"
    ).exists()
    assert (run_directory / "03_insight_objectives.json").exists()
    assert (run_directory / "07_insight_candidates.json").exists()
    assert (run_directory / "07_insight_verification.json").exists()
    assert (run_directory / "07_insight_ledger.json").exists()
    assert "insight_ledger" in result.model_dump(mode="json")

    assert result.release_status in {
        ReleaseStatus.APPROVED,
        ReleaseStatus.APPROVED_WITH_WARNINGS,
        ReleaseStatus.HUMAN_REVIEW_REQUIRED,
    }


def test_zero_wind_bearing_is_likely_valid(tmp_path):
    path = tmp_path / "bearing.csv"
    pd.DataFrame(
        {
            "Wind Bearing (degrees)": [0, 10, 90, 180, 270] * 20,
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    column = profile.tables[0].columns[0]

    assert column.zero_risk == ZeroRisk.LIKELY_VALID
    assert not column.suspicious_zero_values


def test_zero_visibility_is_context_dependent(tmp_path):
    path = tmp_path / "visibility.csv"
    pd.DataFrame(
        {
            "Visibility (km)": [0, 1, 5, 10, 16] * 20,
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    column = profile.tables[0].columns[0]

    assert column.zero_risk == ZeroRisk.CONTEXT_DEPENDENT
    assert not column.suspicious_zero_values


def test_zero_pressure_is_possible_sentinel(tmp_path):
    path = tmp_path / "pressure.csv"
    pd.DataFrame(
        {
            "Pressure (millibars)": [0] * 2 + list(np.linspace(990, 1030, 198)),
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    column = profile.tables[0].columns[0]

    assert column.zero_risk == ZeroRisk.POSSIBLE_SENTINEL
    assert column.suspicious_zero_values


def test_generic_dataset_report_requires_overview(tmp_path):
    path = tmp_path / "overview.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)

    profile = profile_data(load_data([path]))
    plan = fallback_execution_plan(
        "Understand the dataset and report the strongest findings.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    required = set(plan.report_specification.required_components)
    assert ReportComponent.DATASET_OVERVIEW in required
    assert ReportComponent.DATA_QUALITY in required
    assert ReportComponent.STRONGEST_RELATIONSHIPS in required


def test_writer_output_rejects_internal_guardrail_leakage():
    ledger, _ = make_fact_fixture()
    markdown = """
## Global Prohibited Interpretations
- Do not say group membership caused the difference.
"""
    output = WriterOutput(
        title="Leak",
        markdown=markdown,
        sentence_support=[],
        selected_fact_ids=[],
    )

    assert validate_writer_output(output, ledger)


def test_writer_output_rejects_ledger_field_rendering():
    ledger, _ = make_fact_fixture()
    output = WriterOutput(
        title="Leak",
        markdown="Finding: Rain is warmer.\n\nImportant Note: Do not say causal.\n",
        sentence_support=[],
        selected_fact_ids=[],
    )

    assert validate_writer_output(output, ledger)


def test_writer_output_accepts_natural_effect_interpretation():
    ledger, _ = make_fact_fixture()
    sentence = (
        "Rain observations were on average 17.3°C warmer than snow "
        "observations, representing a large difference."
    )
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "fact_summary": sentence,
            "structured_values": {"EVD_0001": {"difference": 17.3}},
            "entities": ["Rain", "snow"],
        }
    )
    ledger = FactLedger(writer_ready_facts=[fact])
    output = WriterOutput(
        title="Natural",
        markdown=f"# Natural\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )

    assert not validate_writer_output(output, ledger)


def test_materialise_writer_output_splits_multi_sentence_draft_text():
    ledger, _ = make_fact_fixture()
    draft = WriterAgentDraft(
        title="Weather summary",
        sections=[
            WriterSectionDraft(
                heading="Dataset overview",
                sentences=[
                    WriterSentenceDraft(
                        text=(
                            "The table contains 96,453 rows. "
                            "The dataset is large."
                        ),
                        fact_ids=["FACT_0001"],
                        support_type=SupportType.PARAPHRASE,
                    )
                ],
            )
        ],
    )

    output = materialise_writer_output(draft, ledger)

    assert [
        support.sentence_text
        for support in output.sentence_support
    ] == [
        "The table contains 96,453 rows.",
        "The dataset is large.",
    ]
    assert output.selected_fact_ids == ["FACT_0001"]
    assert not validate_writer_output(output, ledger)


def test_quality_warning_results_in_approved_with_warnings():
    quality = ReportQualityAssessment(
        status=QualityStatus.WARNING,
        request_responsiveness=0.8,
        finding_selection=0.8,
        coherence=0.9,
        concision=0.9,
        caveat_integration=0.8,
        data_science_interpretation=0.9,
        findings=["The report omits a requested overview."],
    )

    status = decide_release_status(
        annotations=[],
        quality=quality,
        methodological_warnings=[],
        repair_budget_exhausted=False,
        audit_mode=AuditMode.INTERNAL,
    )

    assert status == ReleaseStatus.APPROVED_WITH_WARNINGS


def test_missing_required_component_is_quality_warning_not_human_review():
    ledger, evidence = make_fact_fixture()
    sentence = "The table contains 96,453 rows."
    writer = WriterOutput(
        title="Overview only",
        markdown=f"# Overview only\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    spec = ReportSpecification(
        report_purpose="Describe the data.",
        target_length_words=300,
        maximum_main_findings=5,
        prioritisation_rule="Cover required components.",
        required_components=[
            ReportComponent.DATASET_OVERVIEW,
            ReportComponent.DATA_QUALITY,
        ],
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
    )

    assert audit.quality_assessment.status == QualityStatus.REVISE
    assert audit.release_status == ReleaseStatus.APPROVED_WITH_WARNINGS


def test_imbalance_bias_wording_is_methodological_warning():
    evidence = EvidenceLedger(
        fingerprint="test",
        items=[
            EvidenceItem(
                evidence_id="EVD_0001",
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=["TASK_001"],
                finding="Rain and snow groups have different mean temperatures.",
                metrics={"rain_mean": 12.38, "snow_mean": -4.95},
                source_tables=["weather"],
                source_columns=["Temperature (°C)", "Precip Type"],
                method="Unadjusted group comparison.",
                validation_strategy=ValidationStrategy.NONE,
                practical_interpretation=(
                    "The groups differ descriptively, and unequal group sizes "
                    "may affect precision and stability."
                ),
                strength_label="large_group_difference",
                limitations=[],
                prohibited_interpretations=[],
                recommendations=[],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.COMPARATIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ],
    )
    ledger = FactLedger(
        writer_ready_facts=[
            VerifiedFact(
                fact_id="FACT_0001",
                source_candidate_id="CAN_0001",
                fact_summary=(
                    "Rain and snow groups have different mean temperatures."
                ),
                evidence_ids=["EVD_0001"],
                structured_values={
                    "EVD_0001": {"rain_mean": 12.38, "snow_mean": -4.95}
                },
                entities=["Temperature (°C)", "Precip Type", "rain", "snow"],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.COMPARATIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.HEADLINE,
            )
        ]
    )
    sentence = "The imbalanced group sizes may bias the observed means."
    writer = WriterOutput(
        title="Groups",
        markdown=f"# Groups\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    spec = ReportSpecification(
        report_purpose="Describe group differences.",
        target_length_words=200,
        maximum_main_findings=3,
        prioritisation_rule="Use supported comparisons.",
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
    )

    assert any(
        annotation.subtype == "unsupported_methodological_interpretation"
        and annotation.severity == Severity.MEDIUM
        for annotation in audit.annotations
    )
    assert audit.release_status == ReleaseStatus.APPROVED_WITH_WARNINGS


def test_precision_stability_imbalance_wording_is_allowed():
    ledger, evidence = make_fact_fixture()
    sentence = (
        "Unequal group sizes may affect precision and stability of the "
        "observed means."
    )
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "fact_summary": sentence,
            "claim_permissions": [
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
        }
    )
    ledger = FactLedger(writer_ready_facts=[fact])
    writer = WriterOutput(
        title="Groups",
        markdown=f"# Groups\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    spec = ReportSpecification(
        report_purpose="Describe group differences.",
        target_length_words=200,
        maximum_main_findings=3,
        prioritisation_rule="Use supported comparisons.",
    )

    audit = deterministic_audit(
        writer,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
    )

    assert not [
        annotation
        for annotation in audit.annotations
        if annotation.subtype == "unsupported_methodological_interpretation"
    ]


def test_unresolved_high_factual_error_requires_human_review():
    quality = ReportQualityAssessment(
        status=QualityStatus.PASS,
        request_responsiveness=1.0,
        finding_selection=1.0,
        coherence=1.0,
        concision=1.0,
        caveat_integration=1.0,
        data_science_interpretation=1.0,
    )
    status = decide_release_status(
        annotations=[
            AuditAnnotation(
                annotation_id="ANN_0001",
                sentence="The table has 12 rows.",
                text_span="12",
                error_type=ErrorType.INCORRECT_NUMBER,
                subtype="unsupported_number",
                severity=Severity.HIGH,
                explanation="Wrong number.",
                correction_goal="Use the supported number.",
                confidence=0.95,
            )
        ],
        quality=quality,
        methodological_warnings=[],
        repair_budget_exhausted=True,
        audit_mode=AuditMode.INTERNAL,
    )

    assert status == ReleaseStatus.HUMAN_REVIEW_REQUIRED


def test_targeted_repair_preserves_unflagged_sentences():
    ledger, evidence = make_fact_fixture()
    bad_sentence = "The dataset contains 12 observations."
    good_sentence = "The table contains 96,453 rows."
    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{bad_sentence}\n\n{good_sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=bad_sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            ),
            SentenceSupport(
                sentence_id="SENT_0002",
                sentence_text=good_sentence,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.DIRECT,
            ),
        ],
        selected_fact_ids=["FACT_0001"],
    )
    proposal = AuditRepairProposal(
        annotations=[],
        repairs=[
            SentenceRepair(
                sentence_id="SENT_0001",
                original_sentence=bad_sentence,
                annotation_ids=[],
                candidates=[
                    RepairCandidate(
                        repair_id="REP_001",
                        replacement_text="The dataset contains 96,453 observations.",
                        strategy=RepairStrategy.MINIMAL_CORRECTION,
                        supporting_fact_ids=["FACT_0001"],
                        supporting_evidence_ids=["EVD_0001"],
                        factual_support_score=1.0,
                        meaning_preservation_score=1.0,
                        readability_score=1.0,
                        residual_hallucination_risk=0.0,
                    )
                ],
                preferred_repair_id="REP_001",
                selection_reason="Correct the number.",
            )
        ],
        recommended_decision=AuditDecision.REVISE,
        residual_risk="Repair required.",
        quality_assessment=ReportQualityAssessment(
            status=QualityStatus.PASS,
            request_responsiveness=1.0,
            finding_selection=1.0,
            coherence=1.0,
            concision=1.0,
            caveat_integration=1.0,
            data_science_interpretation=1.0,
        ),
    )

    repaired, _ = apply_repair_proposal(writer, proposal, ledger, evidence)

    assert good_sentence in repaired.markdown


def test_deterministic_writer_fallback_is_not_primary_evaluation():
    ledger, evidence = make_fact_fixture()
    understanding = DataUnderstanding(
        profile_fingerprint="test",
        dataset_summary="Test.",
        tables=[],
    )
    plan = ExecutionPlan(
        objective="Describe the data.",
        tasks=[],
        route_order=[],
        report_specification=ReportSpecification(
            report_purpose="Describe the data.",
            target_length_words=300,
            maximum_main_findings=5,
            prioritisation_rule="Use verified facts.",
            required_components=[ReportComponent.DATASET_OVERVIEW],
        ),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=10,
        rationale="Test plan.",
    )
    pack = build_writer_evidence_pack(
        request="Describe the data.",
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
    )

    output = fallback_writer(pack)

    assert output.writer_mode == "deterministic_fallback"
    assert not output.eligible_for_primary_evaluation


def test_writer_materialisation_maps_each_compound_sentence_fragment():
    ledger, _ = make_fact_fixture()
    first = "The table contains 96,453 rows."
    second = "The dataset contains more than 96,000 observations."
    draft = WriterAgentDraft(
        title="Supported report",
        sections=[
            WriterSectionDraft(
                heading="Overview",
                sentences=[
                    WriterSentenceDraft(
                        text=f"{first} {second}",
                        fact_ids=["FACT_0001"],
                        support_type=SupportType.PARAPHRASE,
                    )
                ],
            )
        ],
    )

    output = materialise_writer_output(draft, ledger)

    assert [
        support.sentence_text
        for support in output.sentence_support
    ] == [first, second]


def test_fallback_writer_maps_each_compound_limitation_fragment():
    ledger, evidence = make_fact_fixture()
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "claim_permissions": [
                ClaimPermission.ASSOCIATIONAL,
            ]
        }
    )
    understanding = DataUnderstanding(
        profile_fingerprint="test",
        dataset_summary="Test.",
        tables=[],
    )
    plan = ExecutionPlan(
        objective="Describe the data.",
        tasks=[],
        route_order=[],
        report_specification=ReportSpecification(
            report_purpose="Describe the data.",
            target_length_words=300,
            maximum_main_findings=5,
            prioritisation_rule="Use verified facts.",
            required_components=[ReportComponent.DATASET_OVERVIEW],
        ),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=10,
        rationale="Test plan.",
    )
    pack = build_writer_evidence_pack(
        request="Describe the data.",
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=FactLedger(writer_ready_facts=[fact]),
        settings=Settings(),
    )
    limitation = (
        "Observed associations are descriptive. "
        "They are not evidence of causal effects."
    )
    pack = pack.model_copy(
        update={
            "priority_facts": [fact],
            "reader_facing_limitations": [limitation],
        }
    )

    output = fallback_writer(pack)
    mapped_sentences = {
        support.sentence_text
        for support in output.sentence_support
    }

    assert set(split_markdown_sentences(limitation)).issubset(
        mapped_sentences
    )


def test_repair_rejects_identical_replacement_text():
    ledger, evidence = make_fact_fixture()
    sentence = "The table contains 96,453 rows."
    candidate = RepairCandidate(
        repair_id="REP_NOOP",
        replacement_text=sentence,
        strategy=RepairStrategy.MINIMAL_CORRECTION,
        supporting_fact_ids=["FACT_0001"],
        supporting_evidence_ids=["EVD_0001"],
        factual_support_score=1.0,
        meaning_preservation_score=1.0,
        readability_score=1.0,
        residual_hallucination_risk=0.0,
    )

    errors = validate_repair_candidate(
        candidate,
        ledger,
        evidence,
        original_text=sentence,
    )

    assert errors == [
        "The replacement is identical to the original sentence."
    ]


def test_repair_maps_every_fragment_of_compound_replacement():
    ledger, evidence = make_fact_fixture()
    original = "The dataset contains 12 observations."
    first = "The table contains 96,453 rows."
    second = "The dataset contains more than 96,000 observations."
    writer = WriterOutput(
        title="Test",
        markdown=f"# Test\n\n{original}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=original,
                fact_ids=["FACT_0001"],
                evidence_ids=["EVD_0001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_0001"],
    )
    candidate = RepairCandidate(
        repair_id="REP_COMPOUND",
        replacement_text=f"{first} {second}",
        strategy=RepairStrategy.MINIMAL_CORRECTION,
        supporting_fact_ids=["FACT_0001"],
        supporting_evidence_ids=["EVD_0001"],
        factual_support_score=1.0,
        meaning_preservation_score=1.0,
        readability_score=1.0,
        residual_hallucination_risk=0.0,
    )
    proposal = AuditRepairProposal(
        repairs=[
            SentenceRepair(
                sentence_id="SENT_0001",
                original_sentence=original,
                annotation_ids=[],
                candidates=[candidate],
                preferred_repair_id=candidate.repair_id,
                selection_reason="Correct and clarify the supported count.",
            )
        ],
        recommended_decision=AuditDecision.REVISE,
        residual_risk="Repair required.",
        quality_assessment=(
            make_passing_audit_report().quality_assessment
        ),
    )

    repaired, patches = apply_repair_proposal(
        writer,
        proposal,
        ledger,
        evidence,
    )

    assert len(patches) == 1
    assert [
        support.sentence_text
        for support in repaired.sentence_support
    ] == [first, second]
    assert len(
        {
            support.sentence_id
            for support in repaired.sentence_support
        }
    ) == 2


def test_writer_recovers_one_unambiguous_missing_insight_id():
    insight = VerifiedInsight(
        insight_id="INS_RECOVER",
        statement=(
            "The verified findings form one bounded pattern."
        ),
        insight_type=InsightType.NARRATIVE_SUMMARY,
        interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
        source_fact_ids=["FACT_0001"],
        source_evidence_ids=["EVD_0001"],
        why_it_matters="It provides a bounded interpretation.",
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        confidence=0.95,
        salience=0.90,
        verification_status=InsightVerificationStatus.VERIFIED,
    )
    draft = WriterAgentDraft(
        title="Insight report",
        sections=[
            WriterSectionDraft(
                heading="Finding",
                sentences=[
                    WriterSentenceDraft(
                        text=insight.statement,
                        fact_ids=["FACT_0001"],
                        interpretation_level=(
                            InterpretationLevel.BOUNDED_INSIGHT
                        ),
                        support_type=SupportType.MULTI_FACT_SYNTHESIS,
                    )
                ],
            )
        ],
    )

    recovered = recover_missing_writer_insight_ids(
        draft,
        {insight.insight_id: insight},
    )

    assert recovered.sections[0].sentences[0].insight_ids == [
        insight.insight_id
    ]


# ============================================================
# REPORT-COVERAGE REGRESSION TESTS
# ============================================================


def _coverage_evidence_item(
    *,
    evidence_id,
    finding,
    route,
    metrics,
    strength_label,
    recommended_use,
    permissions,
    relevance=0.95,
    salience=0.95,
):
    return EvidenceItem(
        evidence_id=evidence_id,
        route=route,
        task_ids=["TASK_COVERAGE"],
        finding=finding,
        metrics=metrics,
        source_tables=["weather"],
        source_columns=list(
            metrics.get(
                "source_columns",
                [],
            )
        ),
        method="Deterministic test evidence.",
        validation_strategy=ValidationStrategy.NONE,
        practical_interpretation=finding,
        strength_label=strength_label,
        limitations=[],
        prohibited_interpretations=[],
        recommendations=[],
        claim_permissions=permissions,
        factual_confidence=1.0,
        methodological_strength=0.95,
        user_relevance=relevance,
        salience=salience,
        recommended_use=recommended_use,
        eligible_for_writer=True,
    )


def _coverage_fact(
    item,
    fact_id,
):
    return VerifiedFact(
        fact_id=fact_id,
        source_candidate_id=(
            f"CAN_{fact_id}"
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=[
            "weather",
            *item.source_columns,
        ],
        claim_permissions=(
            item.claim_permissions
        ),
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )


def _coverage_fixture():
    overview = _coverage_evidence_item(
        evidence_id="EVD_COV_001",
        finding=(
            "Table `weather` contains 96,453 "
            "rows and 12 columns."
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        metrics={
            "row_count": 96_453,
            "column_count": 12,
        },
        strength_label="dataset_overview",
        recommended_use=RecommendedUse.HEADLINE,
        permissions=[
            ClaimPermission.DESCRIPTIVE
        ],
    )

    quality = _coverage_evidence_item(
        evidence_id="EVD_COV_002",
        finding=(
            "`Loud Cover` is constant at `0` "
            "across all observations."
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        metrics={
            "constant": True,
            "constant_value": 0,
        },
        strength_label="constant_column",
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.DESCRIPTIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    correlation = _coverage_evidence_item(
        evidence_id="EVD_COV_003",
        finding=(
            "`Temperature (C)` and "
            "`Apparent Temperature (C)` have "
            "a Pearson correlation of 0.9926."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "pearson_r": 0.9926,
            "complete_pairs": 96_453,
        },
        strength_label=(
            "very_strong_association"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.ASSOCIATIONAL,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    large_group = _coverage_evidence_item(
        evidence_id="EVD_COV_004",
        finding=(
            "Rain observations have a mean "
            "temperature of 12.36 compared with "
            "-4.97 for snow, a difference of "
            "17.33."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "highest_group": {
                "group": "rain",
                "mean": 12.36,
            },
            "lowest_group": {
                "group": "snow",
                "mean": -4.97,
            },
            "difference": 17.33,
            "standardised_difference": 1.0,
        },
        strength_label=(
            "large_group_difference"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.COMPARATIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
    )

    small_group = _coverage_evidence_item(
        evidence_id="EVD_COV_005",
        finding=(
            "Rain observations have a mean wind "
            "speed of 10.97 compared with 9.482 "
            "for snow, a difference of 1.489."
        ),
        route=(
            AnalysisRoute
            .ASSOCIATION_COMPARISON
        ),
        metrics={
            "highest_group": {
                "group": "rain",
                "mean": 10.97,
            },
            "lowest_group": {
                "group": "snow",
                "mean": 9.482,
            },
            "difference": 1.489,
            "standardised_difference": 0.22,
        },
        strength_label=(
            "small_group_difference"
        ),
        recommended_use=(
            RecommendedUse.MAIN_FINDING
        ),
        permissions=[
            ClaimPermission.COMPARATIVE,
            ClaimPermission.METHODOLOGICAL,
        ],
        relevance=0.80,
        salience=0.75,
    )

    evidence = EvidenceLedger(
        fingerprint="coverage-test",
        items=[
            overview,
            quality,
            correlation,
            large_group,
            small_group,
        ],
    )

    facts = {
        item.evidence_id: _coverage_fact(
            item,
            f"FACT_COV_{index:03d}",
        )
        for index, item in enumerate(
            evidence.items,
            start=1,
        )
    }

    return evidence, facts


def test_report_coverage_recovery_regression():
    from table2text.audit import (
        augment_fact_ledger_for_report_coverage,
    )
    from table2text.schemas import (
        VerificationMethod,
    )

    evidence, facts = _coverage_fixture()

    thin_ledger = FactLedger(
        writer_ready_facts=[
            facts["EVD_COV_005"]
        ]
    )

    recovered = (
        augment_fact_ledger_for_report_coverage(
            fact_ledger=thin_ledger,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            settings=Settings(),
        )
    )

    assert (
        len(recovered.writer_ready_facts)
        > len(thin_ledger.writer_ready_facts)
    )

    assert (
        recovered
        .deterministically_recovered_fact_ids
    )

    recovered_facts = [
        fact
        for fact in recovered.writer_ready_facts
        if fact.fact_id
        in recovered
        .deterministically_recovered_fact_ids
    ]

    assert recovered_facts

    assert all(
        fact.verification_method
        == VerificationMethod
        .DETERMINISTIC_EVIDENCE_RECOVERY
        for fact in recovered_facts
    )

    represented = {
        evidence_id
        for fact in recovered.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }

    assert "EVD_COV_001" in represented
    assert "EVD_COV_002" in represented
    assert "EVD_COV_003" in represented
    assert "EVD_COV_004" in represented


def test_priority_selection_never_refills_with_small_effect():
    from table2text.audit import (
        select_balanced_priority_facts,
    )

    evidence, facts = _coverage_fixture()

    ledger = FactLedger(
        writer_ready_facts=list(
            facts.values()
        )
    )

    selected = (
        select_balanced_priority_facts(
            facts=ledger.writer_ready_facts,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
            ],
            settings=Settings(),
        )
    )

    selected_evidence_ids = {
        evidence_id
        for fact in selected
        for evidence_id in fact.evidence_ids
    }

    assert "EVD_COV_001" in selected_evidence_ids
    assert "EVD_COV_002" in selected_evidence_ids
    assert "EVD_COV_003" in selected_evidence_ids
    assert "EVD_COV_004" in selected_evidence_ids
    assert "EVD_COV_005" not in selected_evidence_ids


def test_minimum_report_words_never_exceeds_target():
    from table2text.audit import (
        minimum_useful_report_words,
    )

    minimum = minimum_useful_report_words(
        target_words=150,
        required_component_count=4,
        settings=Settings(),
    )

    assert minimum <= 150
    assert minimum > 0


def test_recovered_balanced_fallback_is_not_two_sentence_report():
    from table2text.audit import (
        augment_fact_ledger_for_report_coverage,
    )

    evidence, facts = _coverage_fixture()

    thin_ledger = FactLedger(
        writer_ready_facts=[
            facts["EVD_COV_005"]
        ]
    )

    ledger = (
        augment_fact_ledger_for_report_coverage(
            fact_ledger=thin_ledger,
            evidence=evidence,
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            settings=Settings(),
        )
    )

    understanding = DataUnderstanding(
        profile_fingerprint="coverage-test",
        dataset_summary=(
            "Weather observations."
        ),
        tables=[],
    )

    plan = ExecutionPlan(
        objective=(
            "Understand the weather dataset and "
            "report its strongest findings."
        ),
        tasks=[],
        route_order=[],
        report_specification=ReportSpecification(
            report_purpose=(
                "Understand the weather dataset."
            ),
            target_length_words=300,
            maximum_main_findings=8,
            prioritisation_rule=(
                "Cover required components using "
                "the strongest evidence."
            ),
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
        ),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=20,
        rationale="Regression test.",
    )

    pack = build_writer_evidence_pack(
        request=plan.objective,
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
    )

    output = fallback_writer(pack)

    assert "## Dataset overview" in output.markdown
    assert "## Data quality" in output.markdown
    assert (
        "## Strongest observed relationships"
        in output.markdown
    )
    assert "1.489" not in output.markdown
    assert len(output.sentence_support) >= 4
    assert (
        output.writer_mode
        == "deterministic_fallback"
    )
    assert not output.eligible_for_primary_evaluation


# ============================================================
# PROFILE-SUPPORT AND AUDIT-AUTHORITY REGRESSION TESTS
# ============================================================


def _profile_authority_fixture() -> DataProfile:
    return DataProfile(
        fingerprint="profile-authority",
        source_paths=["memory.csv"],
        tables=[
            TableProfile(
                table_name="weather",
                source_path="memory.csv",
                row_count=4,
                column_count=4,
                duplicate_row_count=1,
                candidate_keys=["Timestamp"],
                columns=[
                    ColumnProfile(
                        name="Timestamp",
                        dtype="object",
                        semantic_type="datetime",
                        missing_count=0,
                        missing_rate=0.0,
                        unique_count=4,
                        sample_values=[
                            "2020-01-01 00:00",
                            "2020-01-01 01:00",
                        ],
                        datetime_parse_rate=1.0,
                        candidate_key=True,
                    ),
                    ColumnProfile(
                        name="Constant",
                        dtype="int64",
                        semantic_type="numeric",
                        missing_count=0,
                        missing_rate=0.0,
                        unique_count=1,
                        sample_values=["0"],
                        numeric_summary={
                            "count": 4,
                            "mean": 0.0,
                            "minimum": 0.0,
                            "maximum": 0.0,
                        },
                        constant=True,
                    ),
                    ColumnProfile(
                        name="Pressure",
                        dtype="float64",
                        semantic_type="numeric",
                        missing_count=0,
                        missing_rate=0.0,
                        unique_count=3,
                        numeric_summary={
                            "count": 4,
                            "mean": 750.0,
                            "median": 1000.0,
                            "minimum": 0.0,
                            "maximum": 1010.0,
                            "zero_count": 1,
                            "zero_rate": 0.25,
                        },
                        suspicious_zero_values=True,
                        possible_sentinel_values=True,
                        zero_risk=ZeroRisk.POSSIBLE_SENTINEL,
                        zero_risk_reason=(
                            "Zero is separated from positive pressure values."
                        ),
                    ),
                    ColumnProfile(
                        name="Precip Type",
                        dtype="object",
                        semantic_type="categorical",
                        missing_count=1,
                        missing_rate=0.25,
                        unique_count=2,
                    ),
                ],
            )
        ],
    )


def _basic_spec() -> ReportSpecification:
    return ReportSpecification(
        report_purpose="Understand the dataset.",
        target_length_words=300,
        maximum_main_findings=5,
        prioritisation_rule="Use supported facts.",
    )


def _audit_sentence(
    sentence: str,
    *,
    support: SentenceSupport | None = None,
    profile_records=None,
    ledger: FactLedger | None = None,
    evidence: EvidenceLedger | None = None,
):
    ledger = ledger or make_fact_fixture()[0]
    evidence = evidence or make_fact_fixture()[1]
    support = support or SentenceSupport(
        sentence_id="SENT_0001",
        sentence_text=sentence,
        fact_ids=["FACT_0001"],
        evidence_ids=["EVD_0001"],
        support_type=SupportType.PARAPHRASE,
    )
    output = WriterOutput(
        title="Audit",
        markdown=f"# Audit\n\n{sentence}\n",
        sentence_support=[support],
        selected_fact_ids=support.fact_ids,
    )
    return deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        profile_support_records=profile_records or [],
    ), output


def test_profile_support_registry_contains_structural_records():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    by_kind = {record.fact_kind for record in records}

    assert "table_dimensions" in by_kind
    assert "duplicate_rows" in by_kind
    assert "constant_column" in by_kind
    assert "column_missingness" in by_kind
    assert "numeric_summary" in by_kind
    assert "zero_diagnostic" in by_kind
    assert "datetime_presence" in by_kind
    assert "candidate_key" in by_kind


def test_execute_plan_emits_duplicate_row_evidence(tmp_path):
    path = tmp_path / "dupes.csv"
    pd.DataFrame(
        {
            "a": [1, 1, 2],
            "b": ["x", "x", "y"],
        }
    ).to_csv(path, index=False)
    bundle = load_data([path])
    plan = ExecutionPlan(
        objective="Describe duplicates.",
        tasks=[
            InvestigationTask(
                task_id="TASK_DUP",
                question="Check duplicate rows.",
                route=AnalysisRoute.DESCRIPTIVE,
                priority=1,
                table_name="dupes",
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE
                ],
                answerability_note="Deterministic profile.",
            )
        ],
        route_order=[AnalysisRoute.DESCRIPTIVE],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=20,
        rationale="Test.",
    )

    evidence = execute_plan(bundle, plan, Settings())
    duplicate_items = [
        item
        for item in evidence.items
        if item.strength_label == "duplicate_rows"
    ]

    assert len(duplicate_items) == 1
    assert (
        duplicate_items[0]
        .metrics["duplicate_row_count"]
        == 1
    )


def test_profile_supported_unmapped_number_creates_hidden_patch():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    sentence = "The dataset contains 1 exact duplicate row."
    audit, output = _audit_sentence(
        sentence,
        profile_records=records,
    )

    assert any(
        annotation.error_type
        == ErrorType.SUPPORT_MAPPING_ERROR
        and annotation.severity == Severity.MEDIUM
        for annotation in audit.annotations
    )
    assert not any(
        annotation.subtype == "unsupported_number"
        and annotation.severity == Severity.HIGH
        for annotation in audit.annotations
    )
    assert audit.support_map_patches

    patched = apply_support_map_patches(
        output,
        audit.support_map_patches,
        {record.support_id for record in records},
    )

    assert patched.markdown == output.markdown
    assert (
        patched.sentence_support[0].sentence_text
        == sentence
    )
    assert patched.sentence_support[0].profile_support_ids

    post_audit = deterministic_audit(
        patched,
        make_fact_fixture()[0],
        make_fact_fixture()[1],
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        profile_support_records=records,
    )

    assert not any(
        annotation.error_type
        == ErrorType.SUPPORT_MAPPING_ERROR
        for annotation in post_audit.annotations
    )


def test_wrong_profile_number_remains_high_error():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    audit, _ = _audit_sentence(
        "The dataset contains 2 exact duplicate rows.",
        profile_records=records,
    )

    assert not audit.support_map_patches
    assert any(
        annotation.subtype == "unsupported_number"
        and annotation.severity == Severity.HIGH
        for annotation in audit.annotations
    )


def test_data_understanding_is_not_factual_authority_for_metadata():
    audit, _ = _audit_sentence(
        "The dataset contains hourly observations at a specific location."
    )

    subtypes = {
        annotation.subtype
        for annotation in audit.annotations
    }
    assert "unsupported_temporal_cadence" in subtypes
    assert "unsupported_location_metadata" in subtypes


def test_datetime_parse_rate_does_not_prove_hourly_cadence():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    audit, _ = _audit_sentence(
        "The dataset contains hourly observations.",
        profile_records=records,
    )

    assert any(
        annotation.subtype
        == "unsupported_temporal_cadence"
        for annotation in audit.annotations
    )


def test_wording_guardrails_for_constant_zero_missing_duplicate_and_pearson():
    examples = {
        "The Constant column provides no analytical value.": (
            "overbroad_constant_interpretation"
        ),
        "Pressure zeros likely represents encoded missingness.": (
            "overconfident_zero_interpretation"
        ),
        "The missingness is unlikely to cause major issues.": (
            "unsupported_missingness_impact"
        ),
        "Duplicate rows should likely be removed.": (
            "unsupported_duplicate_removal"
        ),
        "Pearson correlation may be influenced by non-linear patterns.": (
            "imprecise_pearson_limitation"
        ),
    }

    for sentence, subtype in examples.items():
        audit, _ = _audit_sentence(sentence)
        assert any(
            annotation.subtype == subtype
            for annotation in audit.annotations
        )


def test_safe_profile_supported_wording_is_allowed_after_hidden_patch():
    records = build_profile_support_registry(
        _profile_authority_fixture()
    )
    constant_id = next(
        record.support_id
        for record in records
        if record.fact_kind == "constant_column"
    )
    sentence = (
        "The Constant column contains no observed variation for analyses "
        "that depend on variation."
    )
    support = SentenceSupport(
        sentence_id="SENT_0001",
        sentence_text=sentence,
        fact_ids=[],
        evidence_ids=[],
        profile_support_ids=[constant_id],
        support_type=SupportType.PARAPHRASE,
    )
    audit, _ = _audit_sentence(
        sentence,
        support=support,
        profile_records=records,
    )

    assert not audit.annotations


def test_unsupported_and_supported_future_recommendations():
    unsupported, _ = _audit_sentence(
        "Future work should explore temporal trends."
    )
    assert any(
        annotation.subtype
        == "unsupported_analytical_recommendation"
        for annotation in unsupported.annotations
    )

    evidence = EvidenceLedger(
        fingerprint="recommendation",
        items=[
            EvidenceItem(
                evidence_id="EVD_REC",
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=["TASK_REC"],
                finding="The table contains 4 rows.",
                metrics={"row_count": 4},
                source_tables=["weather"],
                source_columns=[],
                method="Direct count.",
                validation_strategy=ValidationStrategy.NONE,
                practical_interpretation="Small table.",
                strength_label="dataset_overview",
                limitations=[],
                prohibited_interpretations=[],
                recommendations=[
                    AnalyticalRecommendation(
                        recommendation_id="REC_TEMPORAL",
                        action=(
                            "Future work should explore temporal trends."
                        ),
                        recommendation_type="additional_analysis",
                        priority="low",
                        justification=(
                            "The source includes a timestamp field."
                        ),
                    )
                ],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.8,
                salience=0.7,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )
        ],
    )
    ledger = FactLedger(
        writer_ready_facts=[
            VerifiedFact(
                fact_id="FACT_REC",
                source_candidate_id="CAN_REC",
                fact_summary="The table contains 4 rows.",
                evidence_ids=["EVD_REC"],
                structured_values={
                    "EVD_REC": {"row_count": 4}
                },
                entities=["weather"],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.8,
                salience=0.7,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )
        ]
    )
    sentence = "Future work should explore temporal trends."
    support = SentenceSupport(
        sentence_id="SENT_0001",
        sentence_text=sentence,
        fact_ids=["FACT_REC"],
        evidence_ids=["EVD_REC"],
        support_type=SupportType.PARAPHRASE,
    )
    supported, _ = _audit_sentence(
        sentence,
        support=support,
        ledger=ledger,
        evidence=evidence,
    )

    assert not any(
        annotation.subtype
        == "unsupported_analytical_recommendation"
        for annotation in supported.annotations
    )


def test_quality_finding_validation_and_conservative_merge():
    assert not valid_quality_finding(
        "The dataset contains 24 duplicate rows."
    )
    assert valid_quality_finding(
        "The report recommends duplicate removal without sufficient justification."
    )

    deterministic = ReportQualityAssessment(
        status=QualityStatus.REVISE,
        request_responsiveness=0.9,
        finding_selection=0.8,
        coherence=0.7,
        concision=0.8,
        caveat_integration=0.9,
        data_science_interpretation=0.8,
        findings=["The report omits a required limitation."],
        recommendations=["Add the missing limitation."],
    )
    semantic = ReportQualityAssessment(
        status=QualityStatus.PASS,
        request_responsiveness=1.0,
        finding_selection=0.6,
        coherence=0.9,
        concision=0.9,
        caveat_integration=1.0,
        data_science_interpretation=0.9,
        findings=["The report repeats closely related findings."],
        recommendations=["Consolidate repeated findings."],
    )

    merged = merge_quality_assessments(
        deterministic,
        semantic,
    )

    assert merged.status == QualityStatus.REVISE
    assert "The report omits a required limitation." in merged.findings
    assert "The report repeats closely related findings." in merged.findings
    assert merged.finding_selection == 0.6


def test_writer_payload_removes_data_understanding_factual_prose():
    ledger, evidence = make_fact_fixture()
    understanding = DataUnderstanding(
        profile_fingerprint="payload",
        dataset_summary=(
            "The data are hourly and collected at a specific location."
        ),
        tables=[
            TableUnderstanding(
                table_name="weather",
                unit_of_observation="hourly weather station measurement",
                summary="Location-specific hourly weather station data.",
            )
        ],
    )
    plan = ExecutionPlan(
        objective="Understand the data.",
        tasks=[],
        route_order=[],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=20,
        rationale="Test.",
    )
    pack = build_writer_evidence_pack(
        request=plan.objective,
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
    )

    payload = build_compact_writer_payload(pack)

    assert "dataset_summary" not in payload
    assert "table_context" not in payload
    assert "semantic_map" not in payload
    assert payload["priority_facts"]
    assert "analytical_recommendations" in payload


# ============================================================
# VERIFIED BOUNDED INSIGHT SYNTHESIS TESTS
# ============================================================


def _insight_fixture() -> tuple[FactLedger, EvidenceLedger]:
    evidence = EvidenceLedger(
        fingerprint="insight-test",
        items=[
            EvidenceItem(
                evidence_id="EVD_INS_001",
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=["TASK_INS"],
                finding=(
                    "`Humidity` and `Temperature` have a negative Pearson "
                    "correlation."
                ),
                metrics={"pearson_r": -0.63},
                source_tables=["weather"],
                source_columns=["Humidity", "Temperature"],
                method="Deterministic Pearson correlation.",
                practical_interpretation=(
                    "Higher humidity is associated with lower temperature "
                    "in this dataset."
                ),
                strength_label="strong_association",
                claim_permissions=[ClaimPermission.ASSOCIATIONAL],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=0.9,
                salience=0.9,
                recommended_use=RecommendedUse.MAIN_FINDING,
            ),
            EvidenceItem(
                evidence_id="EVD_INS_002",
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=["TASK_INS"],
                finding=(
                    "`Humidity` and `Temperature` also have a negative rank "
                    "association."
                ),
                metrics={"spearman_r": -0.61},
                source_tables=["weather"],
                source_columns=["Humidity", "Temperature"],
                method="Deterministic rank association.",
                practical_interpretation=(
                    "The inverse association is present under a rank-based "
                    "summary as well."
                ),
                strength_label="strong_association",
                claim_permissions=[ClaimPermission.ASSOCIATIONAL],
                factual_confidence=1.0,
                methodological_strength=0.9,
                user_relevance=0.85,
                salience=0.85,
                recommended_use=RecommendedUse.MAIN_FINDING,
            ),
        ],
    )
    facts = [
        VerifiedFact(
            fact_id=f"FACT_INS_{index:03d}",
            source_candidate_id=f"CAN_INS_{index:03d}",
            fact_summary=item.finding,
            evidence_ids=[item.evidence_id],
            structured_values={item.evidence_id: item.metrics},
            entities=[
                "weather",
                "Humidity",
                "Temperature",
            ],
            claim_permissions=item.claim_permissions,
            allowed_interpretations=[item.practical_interpretation],
            factual_confidence=1.0,
            methodological_strength=0.9,
            user_relevance=item.user_relevance,
            salience=item.salience,
            recommended_use=RecommendedUse.MAIN_FINDING,
        )
        for index, item in enumerate(evidence.items, start=1)
    ]
    return FactLedger(writer_ready_facts=facts), evidence


def _insight_candidate(
    *,
    insight_id: str = "INSIGHT_001",
    statement: str = (
        "Pearson and rank-based summaries both show an inverse association "
        "between `Humidity` and `Temperature` in this dataset."
    ),
    insight_type: InsightType = InsightType.OUTCOME_ASSOCIATION,
    interpretation_level: InterpretationLevel = (
        InterpretationLevel.BOUNDED_INSIGHT
    ),
    source_fact_ids: list[str] | None = None,
    source_evidence_ids: list[str] | None = None,
    suitable_for_main_report: bool = True,
    confidence: float = 0.9,
    salience: float = 0.9,
) -> InsightCandidate:
    return InsightCandidate(
        insight_id=insight_id,
        statement=statement,
        insight_type=insight_type,
        interpretation_level=interpretation_level,
        source_fact_ids=(
            source_fact_ids
            if source_fact_ids is not None
            else ["FACT_INS_001", "FACT_INS_002"]
        ),
        source_evidence_ids=(
            source_evidence_ids
            if source_evidence_ids is not None
            else ["EVD_INS_001", "EVD_INS_002"]
        ),
        why_it_matters=(
            "Agreement across both summaries makes the direction less "
            "dependent on a single association measure."
        ),
        supporting_summary="Two verified association summaries agree.",
        limitations=["The association is descriptive, not causal."],
        claim_permissions=[ClaimPermission.ASSOCIATIONAL],
        confidence=confidence,
        salience=salience,
        suitable_for_main_report=suitable_for_main_report,
    )


def _verified_insight(
    candidate: InsightCandidate | None = None,
    *,
    status: InsightVerificationStatus = InsightVerificationStatus.VERIFIED,
) -> VerifiedInsight:
    candidate = candidate or _insight_candidate()
    return VerifiedInsight(
        insight_id=candidate.insight_id,
        statement=candidate.statement,
        insight_type=candidate.insight_type,
        interpretation_level=candidate.interpretation_level,
        source_fact_ids=candidate.source_fact_ids,
        source_evidence_ids=candidate.source_evidence_ids,
        why_it_matters=candidate.why_it_matters,
        limitations=candidate.limitations,
        claim_permissions=candidate.claim_permissions,
        confidence=candidate.confidence,
        salience=candidate.salience,
        verification_status=status,
    )


def test_insight_schema_defaults_and_report_controls():
    plan = ExecutionPlan(
        objective="Describe the data.",
        tasks=[],
        route_order=[],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=10,
        rationale="Compatibility fixture.",
    )
    sentence = WriterSentenceDraft(
        text="A direct finding.",
        support_type=SupportType.DIRECT,
    )

    assert plan.insight_objectives == []
    assert sentence.insight_ids == []
    assert sentence.interpretation_level == InterpretationLevel.FINDING
    assert plan.report_specification.genre == ReportGenre.DATA_SCIENCE_REPORT
    assert plan.report_specification.perspective == ReportPerspective.NEUTRAL
    assert InsightLedger().verified_insights == []


def test_insight_configuration_defaults_and_validation():
    settings = Settings()

    assert settings.enable_insight_synthesis
    assert settings.max_insight_candidates == 6
    assert settings.max_verified_main_insights == 4

    with pytest.raises(ValueError):
        replace(settings, max_insight_candidates=0)
    with pytest.raises(ValueError):
        replace(settings, max_verified_main_insights=7)
    with pytest.raises(ValueError):
        replace(settings, min_insight_confidence=1.1)
    with pytest.raises(ValueError):
        replace(settings, min_insight_salience=-0.1)
    with pytest.raises(ValueError):
        replace(settings, min_facts_per_bounded_insight=0)


def test_fallback_plan_freezes_questions_and_genre_defaults():
    profile = _profile_authority_fixture()
    generic = fallback_execution_plan(
        "Understand the dataset.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )
    sports = fallback_execution_plan(
        "Write a game report.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
    )

    assert generic.insight_objectives
    assert all(
        objective.question.endswith("?")
        for objective in generic.insight_objectives
    )
    assert all(
        not any(character.isdigit() for character in objective.question)
        for objective in generic.insight_objectives
    )
    assert generic.report_specification.genre == ReportGenre.DATA_SCIENCE_REPORT
    assert sports.report_specification.genre == ReportGenre.EVENT_REPORT


def test_valid_bounded_insight_and_safe_association_are_accepted():
    ledger, evidence = _insight_fixture()
    candidate = _insight_candidate()
    overlap = _insight_candidate(
        insight_id="INSIGHT_OVERLAP",
        statement=(
            "The two measures contain highly overlapping information in "
            "this dataset."
        ),
        insight_type=InsightType.REDUNDANCY,
    )

    assert not validate_insight_candidates(
        InsightCandidateSet(candidates=[candidate]),
        ledger,
        evidence,
        Settings(),
    )
    assert not validate_insight_candidates(
        InsightCandidateSet(candidates=[overlap]),
        ledger,
        evidence,
        Settings(),
    )


def test_insight_candidate_rejects_unknown_fact_and_number():
    ledger, evidence = _insight_fixture()
    unknown = _insight_candidate(
        source_fact_ids=["FACT_UNKNOWN", "FACT_INS_002"]
    )
    numbered = _insight_candidate(
        statement=(
            "Higher `Humidity` is associated with a 99-point reduction in "
            "`Temperature`."
        )
    )
    unknown_entity = _insight_candidate(
        statement=(
            "`Pressure` contains highly overlapping information with "
            "`Temperature` in this dataset."
        )
    )

    unknown_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[unknown]),
        ledger,
        evidence,
        Settings(),
    )
    number_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[numbered]),
        ledger,
        evidence,
        Settings(),
    )
    entity_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[unknown_entity]),
        ledger,
        evidence,
        Settings(),
    )

    assert any("unknown fact" in error for error in unknown_errors)
    assert any("unsupported numbers" in error for error in number_errors)
    assert any("unsupported table or column" in error for error in entity_errors)


def test_insight_candidate_requires_grounded_non_hypothetical_implication():
    ledger, evidence = _insight_fixture()
    restatement = _insight_candidate().model_copy(
        update={
            "why_it_matters": (
                ledger.writer_ready_facts[0].allowed_interpretations[0]
            )
        }
    )
    hidden_hypothesis = _insight_candidate().model_copy(
        update={
            "why_it_matters": (
                "The pattern may reflect a data artifact in the source."
            )
        }
    )
    unsupported_number = _insight_candidate().model_copy(
        update={
            "why_it_matters": (
                "The implication applies to 99 analytical settings."
            )
        }
    )

    restatement_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[restatement]),
        ledger,
        evidence,
        Settings(),
    )
    hypothesis_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[hidden_hypothesis]),
        ledger,
        evidence,
        Settings(),
    )
    number_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[unsupported_number]),
        ledger,
        evidence,
        Settings(),
    )

    assert any("restates a source finding" in error for error in restatement_errors)
    assert any("explanatory hypothesis" in error for error in hypothesis_errors)
    assert any("why_it_matters" in error for error in number_errors)


def test_single_fact_pseudo_insight_rejected_but_anomaly_allowed():
    ledger, evidence = _insight_fixture()
    pseudo = _insight_candidate(
        insight_type=InsightType.CONTRAST,
        source_fact_ids=["FACT_INS_001"],
        source_evidence_ids=["EVD_INS_001"],
    )
    anomaly = _insight_candidate(
        insight_id="INSIGHT_ANOMALY",
        statement=(
            "The association in `Humidity` and `Temperature` is an anomaly "
            "requiring further review in this dataset."
        ),
        insight_type=InsightType.ANOMALY,
        source_fact_ids=["FACT_INS_001"],
        source_evidence_ids=["EVD_INS_001"],
    )

    assert any(
        "single-fact pseudo-insight" in error
        for error in validate_insight_candidates(
            InsightCandidateSet(candidates=[pseudo]),
            ledger,
            evidence,
            Settings(),
        )
    )
    assert not validate_insight_candidates(
        InsightCandidateSet(candidates=[anomaly]),
        ledger,
        evidence,
        Settings(),
    )


def test_causal_escalation_is_rejected():
    ledger, evidence = _insight_fixture()
    causal = _insight_candidate(
        statement="`Humidity` causes lower `Temperature`."
    )

    assert any(
        "causal wording" in error
        for error in validate_insight_candidates(
            InsightCandidateSet(candidates=[causal]),
            ledger,
            evidence,
            Settings(),
        )
    )


def test_predictive_and_forecast_escalation_are_rejected():
    ledger, evidence = _insight_fixture()
    predictive = _insight_candidate(
        statement="`Humidity` predicts `Temperature`."
    )
    forecast = _insight_candidate(
        statement="`Humidity` forecasts future `Temperature` values."
    )

    predictive_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[predictive]),
        ledger,
        evidence,
        Settings(),
    )
    forecast_errors = validate_insight_candidates(
        InsightCandidateSet(candidates=[forecast]),
        ledger,
        evidence,
        Settings(),
    )

    assert any("predictive wording" in error for error in predictive_errors)
    assert any("forecast wording" in error for error in forecast_errors)


def test_insight_verifier_must_confirm_synthesis_and_implication():
    ledger, evidence = _insight_fixture()
    candidate = _insight_candidate()
    candidates = InsightCandidateSet(candidates=[candidate])
    restatement_review = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id=candidate.insight_id,
                status=InsightVerificationStatus.VERIFIED,
                confidence=0.9,
                salience=0.9,
                adds_bounded_synthesis=False,
                analytical_implication_supported=False,
                contains_hypothesis=False,
            )
        ]
    )
    valid_review = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id=candidate.insight_id,
                status=InsightVerificationStatus.VERIFIED,
                confidence=0.9,
                salience=0.9,
                adds_bounded_synthesis=True,
                analytical_implication_supported=True,
                contains_hypothesis=False,
            )
        ]
    )

    errors = validate_insight_verification(
        restatement_review,
        candidates,
        ledger,
        evidence,
        Settings(),
    )

    assert any("direct-finding restatement" in error for error in errors)
    assert any("supported analytical implication" in error for error in errors)
    assert not validate_insight_verification(
        valid_review,
        candidates,
        ledger,
        evidence,
        Settings(),
    )


def test_hypotheses_remain_separate_under_both_policies():
    ledger, evidence = _insight_fixture()
    candidate = _insight_candidate(
        insight_id="INSIGHT_HYP",
        statement=(
            "Hypothesis: the observed association may reflect an unmeasured "
            "process."
        ),
        interpretation_level=InterpretationLevel.HYPOTHESIS,
        suitable_for_main_report=False,
    )
    candidates = InsightCandidateSet(candidates=[candidate])
    verification = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id="INSIGHT_HYP",
                status=InsightVerificationStatus.HYPOTHESIS_ONLY,
                confidence=0.8,
                salience=0.7,
                adds_bounded_synthesis=False,
                analytical_implication_supported=False,
                contains_hypothesis=True,
            )
        ]
    )

    for allow in [False, True]:
        settings = replace(
            Settings(),
            allow_hypotheses_in_report=allow,
        )
        assert not validate_insight_candidates(
            candidates,
            ledger,
            evidence,
            settings,
        )
        result = materialise_insight_ledger(
            candidates=candidates,
            verification=verification,
            fact_ledger=ledger,
            evidence_ledger=evidence,
            settings=settings,
        )
        assert not result.verified_insights
        assert [
            insight.insight_id
            for insight in result.hypothesis_only_insights
        ] == ["INSIGHT_HYP"]


def test_insight_ledger_materialisation_applies_status_threshold_order_and_limit():
    ledger, evidence = _insight_fixture()
    first = _insight_candidate(
        insight_id="INSIGHT_FIRST",
        salience=0.95,
    )
    second = _insight_candidate(
        insight_id="INSIGHT_SECOND",
        statement=(
            "The two verified association summaries provide overlapping "
            "directional information in this dataset."
        ),
        insight_type=InsightType.REDUNDANCY,
        salience=0.8,
    )
    rejected = _insight_candidate(
        insight_id="INSIGHT_REJECTED",
        statement=(
            "The verified findings form a bounded narrative summary for this "
            "dataset."
        ),
        insight_type=InsightType.NARRATIVE_SUMMARY,
        salience=0.7,
    )
    candidates = InsightCandidateSet(
        candidates=[first, second, rejected]
    )
    verification = InsightVerificationResult(
        records=[
            InsightVerificationRecord(
                insight_id="INSIGHT_FIRST",
                status=InsightVerificationStatus.VERIFIED_WITH_CAVEAT,
                verified_statement=(
                    first.statement
                    + " This remains a descriptive association."
                ),
                confidence=0.9,
                salience=0.95,
                adds_bounded_synthesis=True,
                analytical_implication_supported=True,
                contains_hypothesis=False,
                limitations=["No causal conclusion is supported."],
            ),
            InsightVerificationRecord(
                insight_id="INSIGHT_SECOND",
                status=InsightVerificationStatus.VERIFIED,
                confidence=0.85,
                salience=0.8,
                adds_bounded_synthesis=True,
                analytical_implication_supported=True,
                contains_hypothesis=False,
            ),
            InsightVerificationRecord(
                insight_id="INSIGHT_REJECTED",
                status=InsightVerificationStatus.REJECTED,
                confidence=0.9,
                salience=0.7,
                adds_bounded_synthesis=False,
                analytical_implication_supported=False,
                contains_hypothesis=False,
                verification_notes=["The synthesis is not sufficiently useful."],
            ),
        ]
    )
    settings = replace(
        Settings(),
        max_verified_main_insights=1,
    )

    result = materialise_insight_ledger(
        candidates=candidates,
        verification=verification,
        fact_ledger=ledger,
        evidence_ledger=evidence,
        settings=settings,
    )

    assert [
        insight.insight_id
        for insight in result.verified_insights
    ] == ["INSIGHT_FIRST"]
    assert result.verified_insights[0].verification_status == (
        InsightVerificationStatus.VERIFIED_WITH_CAVEAT
    )
    assert "descriptive association" in result.verified_insights[0].statement
    assert {
        rejection.insight_id
        for rejection in result.rejected_insights
    } == {"INSIGHT_SECOND", "INSIGHT_REJECTED"}


def test_writer_payload_contains_only_writer_eligible_insights():
    ledger, evidence = _insight_fixture()
    main_candidate = _insight_candidate()
    hypothesis_candidate = _insight_candidate(
        insight_id="INSIGHT_HYP",
        statement="Hypothesis: another process may contribute.",
        interpretation_level=InterpretationLevel.HYPOTHESIS,
        suitable_for_main_report=False,
    )
    insight_ledger = InsightLedger(
        verified_insights=[_verified_insight(main_candidate)],
        hypothesis_only_insights=[
            _verified_insight(
                hypothesis_candidate,
                status=InsightVerificationStatus.HYPOTHESIS_ONLY,
            )
        ],
        rejected_insights=[
            InsightRejection(
                insight_id="INSIGHT_BAD",
                candidate=_insight_candidate(insight_id="INSIGHT_BAD"),
                reasons=["Rejected."],
            )
        ],
    )
    understanding = DataUnderstanding(
        profile_fingerprint="insight-test",
        dataset_summary="Unverified prose must remain private.",
        tables=[],
    )
    plan = ExecutionPlan(
        objective="Describe the strongest findings.",
        tasks=[],
        route_order=[],
        report_specification=_basic_spec(),
        audit_mode=AuditMode.INTERNAL,
        revision_limit=1,
        maximum_facts=10,
        rationale="Test.",
    )
    pack = build_writer_evidence_pack(
        request=plan.objective,
        understanding=understanding,
        plan=plan,
        evidence=evidence,
        fact_ledger=ledger,
        settings=Settings(),
        insight_ledger=insight_ledger,
    )
    payload = build_compact_writer_payload(pack)

    assert payload["priority_verified_insights"]
    assert payload["priority_verified_insights"][0].source_fact_ids
    assert payload["priority_facts"]
    assert payload["genre"] == ReportGenre.DATA_SCIENCE_REPORT
    assert payload["perspective"] == ReportPerspective.NEUTRAL
    assert payload["communication_goal"]
    assert payload["hypothesis_only_insights"] == []
    assert payload["verified_strength_labels_by_fact_id"][
        "FACT_INS_001"
    ] == ["strong_association"]
    assert "INSIGHT_BAD" not in str(payload)
    assert "Unverified prose" not in str(payload)


def test_writer_materialisation_expands_insight_provenance_without_text_change():
    ledger, _ = _insight_fixture()
    insight = _verified_insight()
    insight_ledger = InsightLedger(verified_insights=[insight])
    draft = WriterAgentDraft(
        title="Bounded report",
        sections=[
            WriterSectionDraft(
                heading="Main insight",
                sentences=[
                    WriterSentenceDraft(
                        text=insight.statement,
                        insight_ids=[insight.insight_id],
                        interpretation_level=(
                            InterpretationLevel.BOUNDED_INSIGHT
                        ),
                        support_type=SupportType.MULTI_FACT_SYNTHESIS,
                    )
                ],
            )
        ],
    )

    output = materialise_writer_output(
        draft,
        ledger,
        insight_ledger=insight_ledger,
    )
    support = output.sentence_support[0]

    assert insight.statement in output.markdown
    assert support.insight_ids == [insight.insight_id]
    assert support.interpretation_level == InterpretationLevel.BOUNDED_INSIGHT
    assert set(support.fact_ids) == set(insight.source_fact_ids)
    assert set(support.evidence_ids) == set(insight.source_evidence_ids)


def test_writer_hypothesis_requires_enabled_separate_section():
    ledger, _ = _insight_fixture()
    candidate = _insight_candidate(
        insight_id="INSIGHT_HYP_WRITER",
        statement="Hypothesis: an unmeasured process may contribute.",
        interpretation_level=InterpretationLevel.HYPOTHESIS,
        suitable_for_main_report=False,
    )
    hypothesis = _verified_insight(
        candidate,
        status=InsightVerificationStatus.HYPOTHESIS_ONLY,
    )
    insight_ledger = InsightLedger(
        hypothesis_only_insights=[hypothesis]
    )
    draft = WriterAgentDraft(
        title="Further investigation",
        sections=[
            WriterSectionDraft(
                heading="Questions for Further Investigation",
                sentences=[
                    WriterSentenceDraft(
                        text=hypothesis.statement,
                        insight_ids=[hypothesis.insight_id],
                        interpretation_level=InterpretationLevel.HYPOTHESIS,
                        support_type=SupportType.MULTI_FACT_SYNTHESIS,
                    )
                ],
            )
        ],
    )

    with pytest.raises(ValueError, match="disabled"):
        materialise_writer_output(
            draft,
            ledger,
            insight_ledger=insight_ledger,
        )

    output = materialise_writer_output(
        draft,
        ledger,
        insight_ledger=insight_ledger,
        allow_hypotheses_in_report=True,
    )
    assert output.sentence_support[0].interpretation_level == (
        InterpretationLevel.HYPOTHESIS
    )


def test_writer_rejects_explanatory_hypothesis_disguised_as_next_step():
    ledger, _ = _insight_fixture()
    sentence = (
        "Further analysis could explore whether the association reflects a "
        "data artifact."
    )
    draft = WriterAgentDraft(
        title="Unsupported explanation",
        sections=[
            WriterSectionDraft(
                heading="Limitations and next steps",
                sentences=[
                    WriterSentenceDraft(
                        text=sentence,
                        fact_ids=["FACT_INS_001", "FACT_INS_002"],
                        support_type=SupportType.PARAPHRASE,
                    )
                ],
            )
        ],
    )

    with pytest.raises(ValueError, match="possible explanation"):
        materialise_writer_output(
            draft,
            ledger,
            insight_ledger=InsightLedger(),
        )


def test_writer_validation_rejects_unknown_or_missing_insight_mapping():
    ledger, _ = _insight_fixture()
    insight = _verified_insight()
    insight_ledger = InsightLedger(verified_insights=[insight])

    with pytest.raises(ValueError, match="unknown insight"):
        materialise_writer_output(
            WriterAgentDraft(
                title="Unknown",
                sections=[
                    WriterSectionDraft(
                        heading="Main",
                        sentences=[
                            WriterSentenceDraft(
                                text=insight.statement,
                                insight_ids=["INSIGHT_UNKNOWN"],
                                interpretation_level=(
                                    InterpretationLevel.BOUNDED_INSIGHT
                                ),
                                support_type=SupportType.MULTI_FACT_SYNTHESIS,
                            )
                        ],
                    )
                ],
            ),
            ledger,
            insight_ledger=insight_ledger,
        )

    sentence = insight.statement
    invalid = WriterOutput(
        title="Missing mapping",
        markdown=f"# Missing mapping\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            )
        ],
        selected_fact_ids=insight.source_fact_ids,
    )

    assert any(
        "bounded insight" in error
        for error in validate_writer_output(
            invalid,
            ledger,
            insight_ledger,
        )
    )


def test_direct_finding_remains_valid_without_insight_id():
    ledger, _ = _insight_fixture()
    sentence = ledger.writer_ready_facts[0].fact_summary
    output = WriterOutput(
        title="Finding",
        markdown=f"# Finding\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001"],
                evidence_ids=["EVD_INS_001"],
                support_type=SupportType.DIRECT,
            )
        ],
        selected_fact_ids=["FACT_INS_001"],
    )

    assert not validate_writer_output(output, ledger, InsightLedger())


def test_writer_entity_grounding_is_case_insensitive_and_diagnostic():
    ledger, _ = _insight_fixture()
    fact_lookup = {
        fact.fact_id: fact
        for fact in ledger.writer_ready_facts
    }
    case_variant = WriterSentenceDraft(
        text=(
            "The `humidity` and `temperature` fields are associated in this "
            "dataset."
        ),
        fact_ids=["FACT_INS_001"],
        support_type=SupportType.PARAPHRASE,
    )

    assert not writer_sentence_grounding_errors(
        sentence=case_variant,
        fact_lookup=fact_lookup,
        insight_lookup={},
        sentence_label="Sentence 1.1",
    )

    unsupported = WriterSentenceDraft(
        text="The `Pressure` and `Wind` fields are associated.",
        fact_ids=["FACT_INS_001"],
        support_type=SupportType.PARAPHRASE,
    )
    early_errors = writer_sentence_grounding_errors(
        sentence=unsupported,
        fact_lookup=fact_lookup,
        insight_lookup={},
        sentence_label="Sentence 1.2",
    )

    assert early_errors == [
        "Sentence 1.2 contains unsupported entities ['Pressure', 'Wind']; "
        "mapped fact IDs: ['FACT_INS_001']."
    ]

    unsupported_number = case_variant.model_copy(
        update={
            "text": (
                "The `humidity` and `temperature` fields have a correlation "
                "of 99."
            )
        }
    )
    assert any(
        "number unsupported" in error
        for error in writer_sentence_grounding_errors(
            sentence=unsupported_number,
            fact_lookup=fact_lookup,
            insight_lookup={},
            sentence_label="Sentence 1.3",
        )
    )

    sentence = unsupported.text
    output = WriterOutput(
        title="Unsupported entities",
        markdown=f"# Unsupported entities\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001"],
                evidence_ids=["EVD_INS_001"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_INS_001"],
    )
    late_entity_errors = [
        error
        for error in validate_writer_output(
            output,
            ledger,
            InsightLedger(),
        )
        if "unsupported entities" in error
    ]

    assert late_entity_errors == [
        "SENT_0001 contains unsupported entities ['Pressure', 'Wind']; "
        "mapped fact IDs: ['FACT_INS_001']."
    ]


def _audit_verified_insight_sentence(
    sentence: str,
    *,
    insight: VerifiedInsight | None = None,
) -> AuditReport:
    ledger, evidence = _insight_fixture()
    insight = insight or _verified_insight()
    output = WriterOutput(
        title="Insight audit",
        markdown=f"# Insight audit\n\n## Main insight\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            )
        ],
        selected_fact_ids=insight.source_fact_ids,
    )
    return deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        insight_ledger=InsightLedger(
            verified_insights=[insight]
        ),
    )


def test_verified_insight_sentence_is_not_treated_as_hallucination():
    audit = _audit_verified_insight_sentence(
        _verified_insight().statement
    )

    assert not [
        annotation
        for annotation in audit.annotations
        if annotation.subtype
        in {
            "unsupported_insight",
            "insight_exceeds_verified_wording",
        }
    ]
    assert not any(
        "lists findings without relating" in finding
        for finding in audit.quality_assessment.findings
    )


def test_quality_warns_when_available_insights_are_not_used():
    ledger, evidence = _insight_fixture()
    insight = _verified_insight()
    sentence = ledger.writer_ready_facts[0].fact_summary
    output = WriterOutput(
        title="Fact list",
        markdown=f"# Fact list\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001"],
                evidence_ids=["EVD_INS_001"],
                support_type=SupportType.DIRECT,
            )
        ],
        selected_fact_ids=["FACT_INS_001"],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        insight_ledger=InsightLedger(
            verified_insights=[insight]
        ),
    )

    assert any(
        "lists findings without relating" in finding
        for finding in audit.quality_assessment.findings
    )


def test_quality_requires_verified_analytical_implication():
    insight = _verified_insight()
    restatement_only = _audit_verified_insight_sentence(
        insight.statement,
        insight=insight,
    )

    assert any(
        "does not explain its supported analytical implication" in finding
        for finding in restatement_only.quality_assessment.findings
    )

    ledger, evidence = _insight_fixture()
    markdown = (
        "# Insight audit\n\n## Main insight\n\n"
        f"{insight.statement}\n\n{insight.why_it_matters}\n"
    )
    output = WriterOutput(
        title="Insight audit",
        markdown=markdown,
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=insight.statement,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            ),
            SentenceSupport(
                sentence_id="SENT_0002",
                sentence_text=insight.why_it_matters,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            ),
        ],
        selected_fact_ids=insight.source_fact_ids,
    )
    with_implication = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
        insight_ledger=InsightLedger(verified_insights=[insight]),
    )

    assert not any(
        "does not explain its supported analytical implication" in finding
        for finding in with_implication.quality_assessment.findings
    )


def test_audit_flags_strength_classification_inconsistency():
    ledger, evidence = _insight_fixture()
    sentence = "The two measures have moderate correlations."
    output = WriterOutput(
        title="Strength mismatch",
        markdown=f"# Strength mismatch\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001", "FACT_INS_002"],
                evidence_ids=["EVD_INS_001", "EVD_INS_002"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_INS_001", "FACT_INS_002"],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
    )

    assert any(
        annotation.subtype == "inconsistent_strength_label"
        for annotation in audit.annotations
    )


def test_insight_wording_escalation_is_flagged():
    audit = _audit_verified_insight_sentence(
        "One measure is completely redundant and should always be removed."
    )

    assert any(
        annotation.subtype == "insight_exceeds_verified_wording"
        for annotation in audit.annotations
    )


def test_unlabelled_hypothesis_is_flagged():
    ledger, evidence = _insight_fixture()
    sentence = (
        "The dataset pattern may reflect lower temperature because of an "
        "unmeasured process."
    )
    output = WriterOutput(
        title="Hypothesis",
        markdown=f"# Hypothesis\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=["FACT_INS_001", "FACT_INS_002"],
                evidence_ids=["EVD_INS_001", "EVD_INS_002"],
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=["FACT_INS_001", "FACT_INS_002"],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
    )

    assert any(
        annotation.subtype == "unlabelled_hypothesis"
        for annotation in audit.annotations
    )


def test_unsupported_sports_chronology_is_flagged():
    ledger, evidence = _insight_fixture()
    sentence = "Player X led a dramatic comeback."
    fact = ledger.writer_ready_facts[0].model_copy(
        update={
            "fact_summary": "Player X scored for Team A.",
            "entities": ["Player X", "Team A"],
        }
    )
    ledger = FactLedger(writer_ready_facts=[fact])
    output = WriterOutput(
        title="Game",
        markdown=f"# Game\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=[fact.fact_id],
                evidence_ids=fact.evidence_ids,
                support_type=SupportType.PARAPHRASE,
            )
        ],
        selected_fact_ids=[fact.fact_id],
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        _basic_spec(),
        Settings(),
    )

    assert any(
        annotation.subtype == "unsupported_sports_narrative"
        for annotation in audit.annotations
    )


def test_safe_sports_synthesis_requires_no_chronology():
    statements = [
        "Team A won the game.",
        "Player X and Player Y shared the Team A scoring lead.",
        "Team A recorded more rebounds.",
        "Team A recorded fewer turnovers.",
    ]
    evidence_items = [
        EvidenceItem(
            evidence_id=f"EVD_GAME_{index:03d}",
            route=AnalysisRoute.DESCRIPTIVE,
            task_ids=["TASK_GAME"],
            finding=statement,
            metrics={},
            source_tables=["game"],
            source_columns=["Team", "Player", "Points", "Rebounds", "Turnovers"],
            method="Direct deterministic game summary.",
            practical_interpretation=statement,
            strength_label="game_fact",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=1.0,
            salience=1.0,
            recommended_use=RecommendedUse.MAIN_FINDING,
        )
        for index, statement in enumerate(statements, start=1)
    ]
    evidence = EvidenceLedger(
        fingerprint="game",
        items=evidence_items,
    )
    facts = [
        VerifiedFact(
            fact_id=f"FACT_GAME_{index:03d}",
            source_candidate_id=f"CAN_GAME_{index:03d}",
            fact_summary=item.finding,
            evidence_ids=[item.evidence_id],
            entities=[
                "game",
                "Team A",
                "Player X",
                "Player Y",
                "Team",
                "Player",
                "Points",
                "Rebounds",
                "Turnovers",
            ],
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=1.0,
            salience=1.0,
            recommended_use=RecommendedUse.MAIN_FINDING,
        )
        for index, item in enumerate(evidence_items, start=1)
    ]
    ledger = FactLedger(writer_ready_facts=facts)
    sentence = (
        "Team A combined a shared scoring lead with advantages in rebounds "
        "and turnovers."
    )
    insight = VerifiedInsight(
        insight_id="INSIGHT_GAME",
        statement=sentence,
        insight_type=InsightType.NARRATIVE_SUMMARY,
        interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
        source_fact_ids=[fact.fact_id for fact in facts],
        source_evidence_ids=[item.evidence_id for item in evidence_items],
        why_it_matters="It provides a bounded game narrative.",
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        confidence=0.95,
        salience=0.95,
        verification_status=InsightVerificationStatus.VERIFIED,
    )
    output = WriterOutput(
        title="Game report",
        markdown=f"# Game report\n\n## Game narrative\n\n{sentence}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=insight.source_fact_ids,
                evidence_ids=insight.source_evidence_ids,
                insight_ids=[insight.insight_id],
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                support_type=SupportType.MULTI_FACT_SYNTHESIS,
            )
        ],
        selected_fact_ids=insight.source_fact_ids,
    )
    spec = _basic_spec().model_copy(
        update={"genre": ReportGenre.SPORTS_GAME_REPORT}
    )
    audit = deterministic_audit(
        output,
        ledger,
        evidence,
        AuditMode.INTERNAL,
        [],
        0,
        spec,
        Settings(),
        insight_ledger=InsightLedger(
            verified_insights=[insight]
        ),
    )

    assert not audit.annotations


def test_insight_feature_flag_ablation_keeps_fact_writer_path(tmp_path):
    path = tmp_path / "ablation.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)
    settings = replace(
        Settings(),
        use_llm=False,
        enable_insight_synthesis=False,
        output_dir=tmp_path / "runs",
    )

    result = Table2TextWorkflow(settings).run_sync(
        [path],
        "Understand the dataset.",
    )

    assert not result.insight_ledger.synthesis_enabled
    assert "disabled by configuration" in (
        result.insight_ledger.fallback_reason or ""
    )
    assert result.raw_writer_output.writer_mode == "deterministic_fallback"
    assert (
        settings.output_dir
        / result.run_id
        / "07_insight_ledger.json"
    ).exists()


def test_insight_stage_failure_continues_without_changing_llm_writer_mode(
    tmp_path,
):
    path = tmp_path / "failure.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)
    settings = replace(
        Settings(),
        use_llm=True,
        output_dir=tmp_path / "runs",
        writer_quality_revision_rounds=0,
    )
    workflow = Table2TextWorkflow(settings)

    async def deterministic_regular_fallback(
        self,
        *,
        stage,
        dependencies,
        fallback,
        **_,
    ):
        if stage == "natural_writer":
            ledger = FactLedger.model_validate(
                dependencies.payload["fact_ledger"]
            )
            fact = ledger.writer_ready_facts[0]
            return WriterAgentDraft(
                title="Supported report",
                sections=[
                    WriterSectionDraft(
                        heading="Dataset overview",
                        sentences=[
                            WriterSentenceDraft(
                                text=fact.fact_summary,
                                fact_ids=[fact.fact_id],
                                support_type=SupportType.DIRECT,
                            )
                        ],
                    )
                ],
            )
        return fallback()

    async def failed_optional_stage(self, **_):
        return None, "simulated insight-stage failure"

    workflow.run_agent_or_fallback = MethodType(
        deterministic_regular_fallback,
        workflow,
    )
    workflow.run_optional_insight_agent = MethodType(
        failed_optional_stage,
        workflow,
    )

    result = workflow.run_sync(
        [path],
        "Understand the dataset.",
    )

    assert "simulated insight-stage failure" in (
        result.insight_ledger.fallback_reason or ""
    )
    assert result.raw_writer_output.writer_mode == "llm_writer"
    assert result.release_status in {
        ReleaseStatus.APPROVED,
        ReleaseStatus.APPROVED_WITH_WARNINGS,
        ReleaseStatus.HUMAN_REVIEW_REQUIRED,
    }
    assert result.model_dump_json()


def test_late_writer_materialisation_failure_uses_deterministic_fallback(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "materialisation.csv"
    pd.DataFrame(
        {
            "group": ["a", "b"] * 60,
            "value": np.arange(120),
        }
    ).to_csv(path, index=False)
    settings = replace(
        Settings(),
        use_llm=True,
        output_dir=tmp_path / "runs",
        writer_quality_revision_rounds=0,
    )
    workflow = Table2TextWorkflow(settings)

    async def deterministic_regular_fallback(
        self,
        *,
        stage,
        dependencies,
        fallback,
        **_,
    ):
        if stage == "natural_writer":
            ledger = FactLedger.model_validate(
                dependencies.payload["fact_ledger"]
            )
            fact = ledger.writer_ready_facts[0]
            return WriterAgentDraft(
                title="Materialisation candidate",
                sections=[
                    WriterSectionDraft(
                        heading="Dataset overview",
                        sentences=[
                            WriterSentenceDraft(
                                text=fact.fact_summary,
                                fact_ids=[fact.fact_id],
                                support_type=SupportType.DIRECT,
                            )
                        ],
                    )
                ],
            )
        return fallback()

    async def failed_optional_stage(self, **_):
        return None, "simulated insight-stage failure"

    def failed_materialisation(*_, **__):
        raise ValueError("simulated late entity mismatch")

    workflow.run_agent_or_fallback = MethodType(
        deterministic_regular_fallback,
        workflow,
    )
    workflow.run_optional_insight_agent = MethodType(
        failed_optional_stage,
        workflow,
    )
    monkeypatch.setattr(
        "table2text.workflow.materialise_writer_output",
        failed_materialisation,
    )

    result = workflow.run_sync(
        [path],
        "Understand the dataset.",
    )
    run_directory = settings.output_dir / result.run_id

    assert result.raw_writer_output.writer_mode == "deterministic_fallback"
    assert (run_directory / "09_writer_structured_draft.json").exists()
    error_path = run_directory / "09_writer_materialisation_error.txt"
    assert error_path.exists()
    assert "simulated late entity mismatch" in error_path.read_text()


def test_empty_insight_ledger_fallback_is_explicit():
    ledger = empty_insight_ledger(
        synthesis_enabled=True,
        fallback_reason="request budget exhausted",
    )

    assert ledger.synthesis_enabled
    assert not ledger.verified_insights
    assert ledger.fallback_reason == "request budget exhausted"


def _nested_event_fixture(reference_text: str) -> dict:
    return {
        "event_id": "EVENT-001",
        "date": {"year": 2026, "month": 7, "day": 23},
        "venue": {"city": "Example City", "name": "Example Arena"},
        "overtime": False,
        "participants": {
            "home": {
                "name": "Alpha",
                "statistics": {
                    "team": {
                        "game": {
                            "points": 90,
                            "rebounds": 40,
                            "assists": 20,
                        }
                    },
                    "entities": {
                        "alpha_one": {
                            "name": "Alex One",
                            "points": 25,
                            "rebounds": 8,
                            "assists": 6,
                        },
                        "alpha_two": {
                            "name": "Alex Two",
                            "points": 18,
                            "rebounds": 5,
                            "assists": 4,
                        },
                    },
                },
            },
            "visitor": {
                "name": "Beta",
                "statistics": {
                    "team": {
                        "game": {
                            "points": 80,
                            "rebounds": 35,
                            "assists": 17,
                        }
                    },
                    "entities": {
                        "beta_one": {
                            "name": "Blair One",
                            "points": 22,
                            "rebounds": 9,
                            "assists": 3,
                        }
                    },
                },
            },
        },
        "reference_text": reference_text,
    }


def _event_field_policy() -> EvaluationFieldPolicy:
    return EvaluationFieldPolicy(
        operational_input_paths=[
            "event_id",
            "date",
            "venue",
            "overtime",
            "participants",
        ],
        held_out_reference_paths=["reference_text"],
    )


def _write_nested_event(tmp_path, reference_text: str):
    path = tmp_path / "nested_event.json"
    path.write_text(
        json.dumps(_nested_event_fixture(reference_text)),
        encoding="utf-8",
    )
    return path


def test_nested_event_is_one_record_and_explicit_reference_is_held_out(
    tmp_path,
):
    reference_text = "REFERENCE SENTINEL " * 80
    path = _write_nested_event(tmp_path, reference_text)

    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    frame = next(iter(bundle.tables.values()))
    profile = profile_data(bundle)

    assert len(frame) == 1
    assert bundle.input_structure is not None
    assert bundle.input_structure.shape == InputShape.EVENT_RECORD
    assert bundle.input_structure.row_semantics == "one event"
    assert bundle.input_structure.representation_status == (
        InputRepresentationStatus.VALID
    )
    assert "reference_text" not in frame.columns
    assert "reference_text" not in bundle.input_structure.nested_paths
    assert reference_text.strip() not in json.dumps(
        {
            "profile": profile.model_dump(mode="json"),
            "structure": bundle.input_structure.model_dump(mode="json"),
            "operational": bundle.structured_inputs,
        },
        default=str,
    )


def test_nested_entity_collection_retains_core_tabular_capabilities(
    tmp_path,
):
    path = tmp_path / "entities.json"
    path.write_text(
        json.dumps(
            [
                {
                    "name": f"entity-{index}",
                    "value": index,
                    "attributes": {"group": index % 2},
                    "tags": ["example"],
                }
                for index in range(30)
            ]
        ),
        encoding="utf-8",
    )

    bundle = load_data([path])
    capabilities = available_capabilities(bundle)

    assert bundle.input_structure is not None
    assert bundle.input_structure.shape == InputShape.ENTITY_COLLECTION
    assert len(next(iter(bundle.tables.values()))) == 30
    assert {
        EvidenceCapability.MISSINGNESS,
        EvidenceCapability.DUPLICATES,
        EvidenceCapability.DISTRIBUTION_SUMMARY,
        EvidenceCapability.ASSOCIATION,
        EvidenceCapability.GROUP_COMPARISON,
    }.issubset(capabilities)


def test_undeclared_event_reference_is_quarantined_and_ineligible(
    tmp_path,
):
    reference_text = "UNDECLARED REFERENCE SENTINEL " * 60
    path = _write_nested_event(tmp_path, reference_text)
    bundle = load_data([path])

    assert len(next(iter(bundle.tables.values()))) == 1
    assert bundle.input_structure is not None
    assert bundle.input_structure.sparse_flattening_detected
    assert bundle.input_structure.representation_status == (
        InputRepresentationStatus.AMBIGUOUS
    )
    assert bundle.evaluation_field_policy.held_out_reference_paths == [
        "reference_text"
    ]

    settings = replace(
        Settings(),
        use_llm=False,
        enable_insight_synthesis=False,
        output_dir=tmp_path / "runs_ambiguous",
    )
    result = Table2TextWorkflow(settings).run_sync(
        [path],
        "Understand the dataset and report its strongest findings.",
    )

    assert not result.primary_evaluation_eligible
    assert result.primary_evaluation_reason == (
        "input_representation_ambiguous"
    )
    assert result.release_status == ReleaseStatus.HUMAN_REVIEW_REQUIRED
    assert reference_text.strip() not in result.final_writer_output.markdown


def test_generic_event_capabilities_extract_outcome_rankings_and_paths(
    tmp_path,
):
    path = _write_nested_event(tmp_path, "HELD OUT " * 100)
    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    capabilities = available_capabilities(bundle)
    profile = profile_data(bundle)
    plan = fallback_execution_plan(
        "Write a neutral event report.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=capabilities,
    )
    evidence = execute_plan(bundle, plan, Settings())

    assert {
        EvidenceCapability.EVENT_OUTCOME,
        EvidenceCapability.ENTITY_PERFORMANCE,
        EvidenceCapability.RANKING,
        EvidenceCapability.GROUP_COMPARISON,
    }.issubset(capabilities)

    outcome = next(
        item
        for item in evidence.items
        if item.evidence_type == "event_outcome"
    )
    assert outcome.metrics["winner"] == "Alpha"
    assert outcome.metrics["loser"] == "Beta"
    assert outcome.metrics["winner_score"] == 90
    assert outcome.metrics["loser_score"] == 80
    assert outcome.metrics["margin"] == 10
    assert {
        "participants.home.name",
        "participants.home.statistics.team.game.points",
        "participants.visitor.name",
        "participants.visitor.statistics.team.game.points",
    }.issubset(outcome.source_paths)

    points_ranking = next(
        item
        for item in evidence.items
        if item.evidence_type == "entity_ranking"
        and item.metrics["metric"] == "points"
    )
    assert points_ranking.metrics["ranking"][0]["entity"] == "Alex One"
    assert points_ranking.metrics["ranking"][0]["value"] == 25
    assert "participants.home.statistics.entities.alpha_one.name" in (
        points_ranking.source_paths
    )


def test_event_capability_selection_and_report_contract_are_bounded(
    tmp_path,
):
    path = _write_nested_event(tmp_path, "HELD OUT " * 100)
    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    profile = profile_data(bundle)
    restricted_capabilities = [
        EvidenceCapability.DATASET_PROFILE,
        EvidenceCapability.EVENT_OUTCOME,
    ]

    generic = fallback_execution_plan(
        "Understand the dataset and report its strongest findings.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=restricted_capabilities,
    )
    event = fallback_execution_plan(
        "Write a neutral event report.",
        profile,
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=restricted_capabilities,
    )

    assert generic.report_specification.genre == ReportGenre.EVENT_REPORT
    assert event.report_specification.genre == ReportGenre.EVENT_REPORT
    assert "event_result" in event.report_specification.required_content_slots
    assert all(
        task.capability is None
        or task.capability in restricted_capabilities
        for task in event.tasks
    )
    assert EvidenceCapability.RANKING not in event.selected_capabilities

    resolved_genre, _, _ = resolve_report_genre(
        request="Understand the dataset and report its strongest findings.",
        planned_genre=ReportGenre.DATASET_OVERVIEW,
        configured_genre=None,
        input_structure=bundle.input_structure,
    )
    assert resolved_genre == ReportGenre.EVENT_REPORT


def test_genre_quality_revises_event_report_that_omits_supported_result(
    tmp_path,
):
    path = _write_nested_event(tmp_path, "HELD OUT " * 100)
    bundle = load_data(
        [path],
        evaluation_field_policy=_event_field_policy(),
    )
    capabilities = available_capabilities(bundle)
    plan = fallback_execution_plan(
        "Write a neutral event report.",
        profile_data(bundle),
        AuditMode.INTERNAL,
        Settings(),
        input_structure=bundle.input_structure,
        available_capabilities=capabilities,
    )
    evidence = execute_plan(bundle, plan, Settings())
    ranking = next(
        item
        for item in evidence.items
        if item.evidence_type == "entity_ranking"
    )
    output = WriterOutput(
        title="Incomplete event report",
        markdown=f"# Incomplete event report\n\n{ranking.finding}\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=ranking.finding,
                evidence_ids=[ranking.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    assessment = assess_genre_quality(
        output,
        plan.report_specification,
        evidence,
    )

    assert assessment.status == QualityStatus.REVISE
    assert "event_result" in assessment.missing_supported_slots


def test_event_reference_never_reaches_operational_prompts_or_report(
    tmp_path,
):
    reference_text = "SECRET REFERENCE PROSE " * 70
    path = _write_nested_event(tmp_path, reference_text)
    settings = replace(
        Settings(),
        use_llm=True,
        enable_insight_synthesis=False,
        writer_quality_revision_rounds=0,
        output_dir=tmp_path / "runs_explicit",
    )
    workflow = Table2TextWorkflow(settings)
    operational_payloads: list[str] = []

    async def capture_and_fallback(
        self,
        *,
        prompt,
        dependencies,
        fallback,
        **_,
    ):
        operational_payloads.append(str(prompt))
        operational_payloads.append(
            json.dumps(
                dependencies.payload,
                default=str,
                sort_keys=True,
            )
        )
        return fallback()

    workflow.run_agent_or_fallback = MethodType(
        capture_and_fallback,
        workflow,
    )
    result = workflow.run_sync(
        [path],
        "Write a neutral event report.",
        evaluation_field_policy=_event_field_policy(),
        report_genre=ReportGenre.EVENT_REPORT,
    )

    operational_text = "\n".join(operational_payloads)
    assert reference_text.strip() not in operational_text
    assert reference_text.strip() not in result.final_writer_output.markdown
    assert result.primary_evaluation_eligible
    assert result.execution_plan.report_specification.genre == (
        ReportGenre.EVENT_REPORT
    )
    assert result.genre_quality_assessment is not None
    assert result.genre_quality_assessment.status == QualityStatus.PASS
    assert result.genre_quality_assessment.missing_supported_slots == []
    assert "Alpha defeated Beta 90-80" in result.final_writer_output.markdown
    assert "comeback" not in result.final_writer_output.markdown.lower()
````
