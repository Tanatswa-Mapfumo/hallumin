from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

from .schemas import (
    AuditAnnotation,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    ClaimPermission,
    ErrorType,
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
    ReportPatch,
    ReportQualityAssessment,
    ReviewDecision,
    SentenceSupport,
    Severity,
    SupportType,
    VerificationResult,
    VerifiedFact,
    WriterEvidencePack,
    WriterOutput,
)


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
    approximate = bool(APPROXIMATE_PATTERN.search(sentence))

    for candidate in support_numbers:
        exact_tolerance = max(1e-6, abs(number) * 0.001)

        if abs(number - candidate) <= exact_tolerance:
            return True

        if approximate:
            approximate_tolerance = max(
                0.01,
                abs(candidate) * 0.03,
            )

            if abs(number - candidate) <= approximate_tolerance:
                return True

        digits = raw_token.rstrip("%").replace(",", "")

        if "." not in digits and len(digits) >= 4 and digits.endswith("000"):
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


def evidence_lookup(
    ledger: EvidenceLedger,
) -> dict[str, Any]:
    return {
        item.evidence_id: item
        for item in ledger.items
    }


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

            for value in item.metrics.values():
                if isinstance(value, str):
                    entities.add(value)

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


def build_writer_evidence_pack(
    request: str,
    understanding: Any,
    plan: Any,
    evidence: EvidenceLedger,
    fact_ledger: FactLedger,
) -> WriterEvidencePack:
    facts = fact_ledger.writer_ready_facts

    priority = sorted(
        [
            fact
            for fact in facts
            if fact.recommended_use in {
                RecommendedUse.HEADLINE,
                RecommendedUse.MAIN_FINDING,
            }
        ],
        key=lambda fact: (
            fact.salience
            + fact.user_relevance
            + fact.methodological_strength
        ),
        reverse=True,
    )

    supporting = sorted(
        [
            fact
            for fact in facts
            if fact.recommended_use == RecommendedUse.SUPPORTING_DETAIL
        ],
        key=lambda fact: (
            fact.salience
            + fact.user_relevance
        ),
        reverse=True,
    )

    limitations = sorted(
        [
            fact
            for fact in facts
            if fact.recommended_use == RecommendedUse.LIMITATION
        ],
        key=lambda fact: fact.salience,
        reverse=True,
    )

    recommendations = [
        recommendation
        for item in evidence.items
        for recommendation in item.recommendations
    ]

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
        global_prohibited_interpretations=prohibited,
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

    seen_sentence_ids: set[str] = set()

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


def fallback_writer(
    pack: WriterEvidencePack,
) -> WriterOutput:
    maximum = pack.report_specification.maximum_main_findings

    selected = (
        pack.priority_facts[:maximum]
        + pack.limitation_facts[:2]
    )

    sections: dict[str, list[VerifiedFact]] = {
        "Overview and data quality": [],
        "Strongest observed relationships": [],
        "Modelling and validation": [],
        "Limitations and next steps": [],
    }

    for fact in selected:
        permissions = set(fact.claim_permissions)

        if ClaimPermission.PREDICTIVE in permissions or ClaimPermission.FORECAST in permissions:
            sections["Modelling and validation"].append(fact)
        elif ClaimPermission.INSUFFICIENCY in permissions:
            sections["Limitations and next steps"].append(fact)
        elif any(
            phrase in fact.fact_summary.lower()
            for phrase in ["constant", "missing", "zero", "rows", "columns"]
        ):
            sections["Overview and data quality"].append(fact)
        else:
            sections["Strongest observed relationships"].append(fact)

    lines = ["# Evidence-grounded data-science report", ""]
    support_map: list[SentenceSupport] = []

    sentence_counter = 1

    for heading, facts in sections.items():
        if not facts:
            continue

        lines.extend([f"## {heading}", ""])

        for fact in facts:
            sentence = fact.fact_summary
            lines.append(sentence)

            support_map.append(
                SentenceSupport(
                    sentence_id=f"SENT_{sentence_counter:04d}",
                    sentence_text=sentence,
                    fact_ids=[fact.fact_id],
                    evidence_ids=fact.evidence_ids,
                    support_type=SupportType.DIRECT,
                )
            )
            sentence_counter += 1

        lines.append("")

    return WriterOutput(
        title="Evidence-grounded data-science report",
        markdown="\n".join(lines).strip() + "\n",
        sentence_support=support_map,
        selected_fact_ids=[
            fact.fact_id
            for fact in selected
        ],
        omitted_fact_ids=[
            fact.fact_id
            for fact in pack.priority_facts
            + pack.supporting_facts
            + pack.limitation_facts
            if fact.fact_id
            not in {selected_fact.fact_id for selected_fact in selected}
        ],
        writer_notes=[
            "Deterministic writer fallback was used."
        ],
        writer_mode="deterministic_fallback",
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
) -> AuditReport:
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
        re.findall(r"\b\w+\b", writer_output.markdown)
    )

    quality_findings: list[str] = []
    quality_recommendations: list[str] = []

    if word_count > report_specification.target_length_words * 1.5:
        quality_findings.append(
            "The report substantially exceeds the planned target length."
        )
        quality_recommendations.append(
            "Remove low-priority detail and consolidate methodological caveats."
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

    repeated_caveat_count = len(
        re.findall(
            r"does not establish causation",
            writer_output.markdown,
            re.IGNORECASE,
        )
    )

    if repeated_caveat_count > 2:
        quality_findings.append(
            "The same causal caveat is repeated several times."
        )
        quality_recommendations.append(
            "Consolidate recurring caveats at section level."
        )

    quality = ReportQualityAssessment(
        status=(
            QualityStatus.WARNING
            if quality_findings
            else QualityStatus.PASS
        ),
        request_responsiveness=0.8 if quality_findings else 1.0,
        finding_selection=0.7 if quality_findings else 1.0,
        coherence=0.9,
        concision=0.7 if quality_findings else 1.0,
        caveat_integration=(
            0.6 if repeated_caveat_count > 2 else 1.0
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

    if decision == AuditDecision.REVISE:
        release_status = ReleaseStatus.HUMAN_REVIEW_REQUIRED
    elif annotations or quality.status == QualityStatus.WARNING:
        release_status = ReleaseStatus.APPROVED_WITH_WARNINGS
    else:
        release_status = ReleaseStatus.APPROVED

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
    elif proposal.recommended_decision == AuditDecision.BLOCK:
        decision = AuditDecision.BLOCK
    elif serious:
        decision = AuditDecision.REVISE
    else:
        decision = AuditDecision.PASS

    warning_present = bool(
        annotations
        or proposal.quality_assessment.status != QualityStatus.PASS
    )

    if decision in {AuditDecision.REVISE, AuditDecision.BLOCK}:
        release_status = ReleaseStatus.HUMAN_REVIEW_REQUIRED
    elif warning_present:
        release_status = ReleaseStatus.APPROVED_WITH_WARNINGS
    else:
        release_status = ReleaseStatus.APPROVED

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