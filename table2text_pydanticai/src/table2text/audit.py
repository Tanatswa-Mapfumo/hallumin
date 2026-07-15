from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from typing import Any

import numpy as np
import pandas as pd

from .schemas import (
    AnalysisRoute,
    AuditAnnotation,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    ClaimPermission,
    ErrorType,
    EvidenceItem,
    EvidenceLedger,
    ExternalTruthSource,
    FactCandidate,
    FactCandidateSet,
    FactLedger,
    FactReview,
    QualityStatus,
    RecommendedUse,
    RejectedFact,
    ReleaseStatus,
    RepairCandidate,
    RepairStrategy,
    ReportComponent,
    ReportComponentAssessment,
    ReportPatch,
    ReportQualityAssessment,
    ReviewDecision,
    SentenceSupport,
    Severity,
    SupportType,
    VerificationMethod,
    VerificationResult,
    VerifiedFact,
    WriterAgentDraft,
    WriterEvidencePack,
    WriterOutput,
)
from .config import Settings


NUMBER_PATTERN = re.compile(
    r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?"
)

CAUSAL_PATTERN = re.compile(
    r"\b(caused|causes|causing|led to|effect of|responsible for|"
    r"results? in|because of|due to)\b",
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
            r"\b(dataset|table|rows?|columns?|mean|median|correlation|"
            r"model|forecast|missing|temperature|humidity|visibility|"
            r"higher|lower|increase|decrease|associated|observed)\b",
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

        for evidence_id in candidate.evidence_ids:
            item = lookup[evidence_id]
            structured_values[evidence_id] = item.metrics
            entities.update(item.source_tables)
            entities.update(item.source_columns)

            entities.update(collect_entity_strings(item.metrics))

        facts.append(
            VerifiedFact(
                fact_id=f"FACT_{len(facts) + 1:04d}",
                source_candidate_id=candidate.candidate_id,
                fact_summary=candidate.fact_summary,
                evidence_ids=candidate.evidence_ids,
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


def build_writer_evidence_pack(
    request: str,
    understanding: Any,
    plan: Any,
    evidence: EvidenceLedger,
    fact_ledger: FactLedger,
    settings: Settings,
) -> WriterEvidencePack:
    facts = fact_ledger.writer_ready_facts
    evidence_lookup = {
        item.evidence_id: item
        for item in evidence.items
    }

    priority = select_balanced_priority_facts(
        facts=facts,
        evidence=evidence,
        required_components=plan.report_specification.required_components,
        settings=settings,
    )
    priority_ids = {
        fact.fact_id
        for fact in priority
    }
    ranked_facts = sorted(
        facts,
        key=lambda fact: evidence_priority_score_for_fact(fact, evidence_lookup),
        reverse=True,
    )
    supporting = [
        fact
        for fact in ranked_facts
        if fact.fact_id not in priority_ids
        and fact.recommended_use != RecommendedUse.OMIT_UNLESS_REQUESTED
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
    )[: settings.max_priority_limitation_facts]

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

    return WriterEvidencePack(
        user_request=request,
        report_specification=plan.report_specification,
        dataset_understanding=understanding,
        priority_facts=priority,
        supporting_facts=supporting,
        limitation_facts=limitations,
        evidence_ledger=evidence,
        analytical_recommendations=recommendations,
        reader_facing_limitations=build_reader_facing_limitations(
            priority + limitations
        ),
        internal_prohibited_interpretations=prohibited,
    )


def validate_writer_output(
    output: WriterOutput,
    fact_ledger: FactLedger,
) -> list[str]:
    errors: list[str] = []
    valid_fact_ids = {
        fact.fact_id
        for fact in fact_ledger.writer_ready_facts
    }

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

        if (
            support.support_type != SupportType.NON_FACTUAL
            and not support.fact_ids
        ):
            errors.append(
                f"{support.sentence_id} is factual but has no supporting facts."
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


def materialise_writer_output(
    draft: WriterAgentDraft,
    fact_ledger: FactLedger,
    *,
    writer_mode: str = "llm_writer",
    eligible_for_primary_evaluation: bool = True,
    quality_revision_round: int = 0,
    quality_revision_summary: str | None = None,
) -> WriterOutput:
    fact_lookup = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }

    lines: list[str] = [
        f"# {draft.title.strip()}",
        "",
    ]

    sentence_support: list[SentenceSupport] = []
    selected_fact_ids: list[str] = []
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

            if (
                sentence_draft.support_type
                != SupportType.NON_FACTUAL
                and not sentence_draft.fact_ids
            ):
                raise ValueError(
                    "A factual Writer sentence has no "
                    "supporting fact IDs."
                )

            evidence_ids = list(
                dict.fromkeys(
                    evidence_id
                    for fact_id in sentence_draft.fact_ids
                    for evidence_id in fact_lookup[
                        fact_id
                    ].evidence_ids
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
                        fact_ids=list(
                            dict.fromkeys(
                                sentence_draft.fact_ids
                            )
                        ),
                        evidence_ids=evidence_ids,
                        support_type=(
                            sentence_draft.support_type
                        ),
                    )
                )

                selected_fact_ids.extend(
                    sentence_draft.fact_ids
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


def deterministic_audit(
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    mode: AuditMode,
    external_sources: list[ExternalTruthSource],
    revision_round: int,
    report_specification: Any,
    settings: Settings | None = None,
) -> AuditReport:
    settings = settings or Settings()
    facts = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }

    support_by_sentence = {
        support.sentence_text: support
        for support in writer_output.sentence_support
    }

    annotations: list[AuditAnnotation] = []
    sentences = split_markdown_sentences(writer_output.markdown)
    evidence_lookup_by_id = build_evidence_lookup(evidence)

    factual_count = 0
    supported_count = 0

    for sentence in sentences:
        support = support_by_sentence.get(sentence)

        if not looks_factual(sentence):
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

        support_numbers = [
            number
            for fact in supporting_facts
            for number in fact_support_numbers(fact, evidence)
        ]

        if not numbers_supported(sentence, support_numbers):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.INCORRECT_NUMBER,
                subtype="unsupported_number",
                severity=Severity.HIGH,
                explanation=(
                    "One or more numbers are not supported by the mapped verified facts."
                ),
                correction_goal=(
                    "Use a supported exact or appropriately qualified rounded value."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
            )

        permissions = {
            permission
            for fact in supporting_facts
            for permission in fact.claim_permissions
        }

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
            and ClaimPermission.CAUSAL not in permissions
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="causal_overclaim",
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
            )

        if (
            PREDICTIVE_PATTERN.search(sentence)
            and not negative_predictive(sentence)
            and ClaimPermission.PREDICTIVE not in permissions
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
            )

        if (
            FORECAST_PATTERN.search(sentence)
            and not negative_forecast(sentence)
            and ClaimPermission.FORECAST not in permissions
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
            )

        known_entities = {
            entity
            for fact in supporting_facts
            for entity in fact.entities
        }

        for backtick_entity in re.findall(r"`([^`]+)`", sentence):
            if backtick_entity not in known_entities:
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

    if (
        len(writer_output.selected_fact_ids)
        > report_specification.maximum_main_findings + 4
    ):
        quality_findings.append(
            "The report uses more facts than the planned finding budget."
        )
        quality_recommendations.append(
            "Prioritise headline and main findings and omit weak supporting details."
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
            "Use the unit of observation supplied by dataset understanding or verified facts."
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
        quality=proposal.quality_assessment,
        methodological_warnings=deterministic.methodological_warnings,
        repair_budget_exhausted=False,
        audit_mode=deterministic.mode,
    )


    return deterministic.model_copy(
        update={
            "annotations": annotations,
            "decision": decision,
            "release_status": release_status,
            "residual_risk": proposal.residual_risk,
            "revision_instructions": list(
                dict.fromkeys(
                    deterministic.revision_instructions
                    + proposal.revision_instructions
                )
            ),
            "quality_assessment": proposal.quality_assessment,
            "methodological_warnings": deterministic.methodological_warnings,
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
) -> list[str]:
    errors: list[str] = []
    facts = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }

    unknown = [
        fact_id
        for fact_id in candidate.supporting_fact_ids
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

    supporting_facts = [
        facts[fact_id]
        for fact_id in candidate.supporting_fact_ids
    ]

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
        and ClaimPermission.CAUSAL not in permissions
    ):
        errors.append(
            "The replacement introduces unsupported causal language."
        )

    if (
        PREDICTIVE_PATTERN.search(candidate.replacement_text)
        and not negative_predictive(candidate.replacement_text)
        and ClaimPermission.PREDICTIVE not in permissions
    ):
        errors.append(
            "The replacement introduces unsupported predictive language."
        )

    if (
        FORECAST_PATTERN.search(candidate.replacement_text)
        and not negative_forecast(candidate.replacement_text)
        and ClaimPermission.FORECAST not in permissions
    ):
        errors.append(
            "The replacement introduces unsupported forecast language."
        )

    known_entities = {
        entity
        for fact in supporting_facts
        for entity in fact.entities
    }

    for entity in re.findall(
        r"`([^`]+)`",
        candidate.replacement_text,
    ):
        if entity not in known_entities:
            errors.append(
                f"Unsupported named entity in replacement: {entity}"
            )

    return errors


def apply_repair_proposal(
    writer_output: WriterOutput,
    proposal: AuditRepairProposal,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
) -> tuple[WriterOutput, list[ReportPatch]]:
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

        if replacement.strip():
            supporting_facts = {
                fact.fact_id: fact
                for fact in fact_ledger.writer_ready_facts
            }

            replacement_evidence = list(
                dict.fromkeys(
                    evidence_id
                    for fact_id in selected.supporting_fact_ids
                    if fact_id in supporting_facts
                    for evidence_id in supporting_facts[fact_id].evidence_ids
                )
            )

            new_support = SentenceSupport(
                sentence_id=repair.sentence_id,
                sentence_text=replacement,
                fact_ids=selected.supporting_fact_ids,
                evidence_ids=replacement_evidence,
                support_type=SupportType.PARAPHRASE,
            )

            support_map.append(new_support)
            support_by_sentence[replacement] = new_support

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
