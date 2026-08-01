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