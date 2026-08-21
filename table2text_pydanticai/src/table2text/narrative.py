"""Select and order verified content for genre-appropriate narrative plans."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from .schemas import (
    EvidenceCapability,
    EvidenceItem,
    NarrativePlan,
    NarrativeSlot,
    NarrativeSlotPlan,
    RealisationPolicy,
    RecommendedUse,
    ReportGenre,
    VerifiedFact,
    VerifiedInsight,
    WriterEvidencePack,
)


EVENT_GENRES = {
    ReportGenre.EVENT_REPORT,
    ReportGenre.SPORTS_GAME_REPORT,
}

EVENT_SLOT_BY_EVIDENCE_TYPE = {
    "event_outcome": NarrativeSlot.OPENING_RESULT,
    "event_context": NarrativeSlot.EVENT_CONTEXT,
    "event_status": NarrativeSlot.EVENT_CONTEXT,
    "participant_record_context": NarrativeSlot.EVENT_CONTEXT,
    "score_progression": NarrativeSlot.SCORE_PROGRESSION,
    "event_sequence": NarrativeSlot.EVENT_SEQUENCE,
    "entity_ranking": NarrativeSlot.LEADING_PERFORMANCES,
    "entity_performance": NarrativeSlot.LEADING_PERFORMANCES,
    "participant_comparison": NarrativeSlot.PARTICIPANT_CONTRASTS,
    "event_contrast": NarrativeSlot.PARTICIPANT_CONTRASTS,
    "group_comparison": NarrativeSlot.PARTICIPANT_CONTRASTS,
}

SLOT_PURPOSES = {
    NarrativeSlot.OPENING_RESULT: (
        "Open with the supplied event result, score/outcome and margin when "
        "those values are verified."
    ),
    NarrativeSlot.EVENT_CONTEXT: (
        "Attach compact supported context such as date, venue, event status "
        "or participant record context to the opening rather than making a "
        "dataset overview."
    ),
    NarrativeSlot.SCORE_PROGRESSION: (
        "Use supplied segment-level progression to show how the result is "
        "situated across the event."
    ),
    NarrativeSlot.EVENT_SEQUENCE: (
        "Use supported ordered score-changing or event-sequence evidence for "
        "natural chronology without inventing momentum or causes."
    ),
    NarrativeSlot.LEADING_PERFORMANCES: (
        "Select the strongest supported entity performances and rankings, "
        "combining related measures for the same entity where support allows."
    ),
    NarrativeSlot.PARTICIPANT_CONTRASTS: (
        "Relate major participant-level contrasts with bounded connective "
        "language such as while, compared with or despite."
    ),
    NarrativeSlot.SECONDARY_DETAILS: (
        "Use additional supported details only when they add distinct value "
        "after the result, sequence, leading performances and contrasts."
    ),
    NarrativeSlot.CLOSING_SCOPE: (
        "Keep the scope bounded to the supplied event when a visible caveat "
        "is required by the report contract."
    ),
}

LOW_PRIORITY_METRIC_PATTERN = re.compile(
    r"\b("
    r"attempt(?:ed|s)?|minutes?|personal fouls?|turnovers?|"
    r"field[- ]?goal attempts?|field[- ]?goal percentage|"
    r"three[- ]?point attempts?|three[- ]?point percentage|"
    r"free[- ]?throw attempts?|free[- ]?throw percentage|at bats?|"
    r"plate appearances?|batters faced|pitch(?:es)?|strikes?|"
    r"putouts?|walks?|left on base|game number|game score|"
    r"season total|recorded steps?|capacity|attendance"
    r")\b",
    re.IGNORECASE,
)
CORE_ENTITY_METRIC_PATTERN = re.compile(
    r"\b(?:assists?|blocks?|doubles?|goals?|hits?|home runs?|points?|"
    r"rebounds?|runs(?: batted in)?|saves?|scor(?:e|ed|ing)|steals?|"
    r"strikeouts?|triples?)\b",
    re.IGNORECASE,
)


def _evidence_lookup(pack: WriterEvidencePack) -> dict[str, EvidenceItem]:
    return {
        item.evidence_id: item
        for item in pack.evidence_ledger.items
        if item.eligible_for_writer
    }


def _fact_evidence(
    fact: VerifiedFact,
    evidence_by_id: dict[str, EvidenceItem],
) -> list[EvidenceItem]:
    return [
        evidence_by_id[evidence_id]
        for evidence_id in fact.evidence_ids
        if evidence_id in evidence_by_id
    ]


def _slot_for_fact(
    fact: VerifiedFact,
    evidence_by_id: dict[str, EvidenceItem],
) -> NarrativeSlot | None:
    evidence_items = _fact_evidence(fact, evidence_by_id)
    if not evidence_items:
        return None

    ranked_slots = [
        EVENT_SLOT_BY_EVIDENCE_TYPE.get(item.evidence_type)
        for item in evidence_items
    ]
    ranked_slots = [slot for slot in ranked_slots if slot is not None]
    if not ranked_slots:
        if EvidenceCapability.RANKING in fact.source_capabilities:
            return NarrativeSlot.LEADING_PERFORMANCES
        if EvidenceCapability.GROUP_COMPARISON in fact.source_capabilities:
            return NarrativeSlot.PARTICIPANT_CONTRASTS
        return None

    priority = {
        NarrativeSlot.OPENING_RESULT: 0,
        NarrativeSlot.SCORE_PROGRESSION: 1,
        NarrativeSlot.EVENT_SEQUENCE: 2,
        NarrativeSlot.LEADING_PERFORMANCES: 3,
        NarrativeSlot.PARTICIPANT_CONTRASTS: 4,
        NarrativeSlot.EVENT_CONTEXT: 5,
    }
    return min(ranked_slots, key=lambda slot: priority.get(slot, 100))


def _is_low_priority_event_fact(
    fact: VerifiedFact,
    evidence_items: list[EvidenceItem],
) -> bool:
    if fact.recommended_use == RecommendedUse.OMIT_UNLESS_REQUESTED:
        return True
    if fact.recommended_use in {
        RecommendedUse.HEADLINE,
        RecommendedUse.MAIN_FINDING,
    }:
        return False
    if fact.salience < 0.75 or fact.user_relevance < 0.75:
        return True

    text = " ".join(
        [
            fact.fact_summary,
            *[
                item.finding
                for item in evidence_items
            ],
            *[
                item.strength_label
                for item in evidence_items
            ],
        ]
    )
    if (
        any(item.evidence_type == "entity_performance" for item in evidence_items)
        and CORE_ENTITY_METRIC_PATTERN.search(text)
    ):
        return False
    return bool(LOW_PRIORITY_METRIC_PATTERN.search(text))


def _insight_ids_for_facts(
    insights: list[VerifiedInsight],
    fact_ids: set[str],
) -> list[str]:
    return [
        insight.insight_id
        for insight in insights
        if fact_ids.intersection(insight.source_fact_ids)
    ]


def _slot_plan(
    *,
    slot: NarrativeSlot,
    fact_ids: list[str],
    insight_ids: list[str],
    priority: int,
    minimum_items: int,
    paragraph_hint: int,
    connective_hint: str | None = None,
    maximum_items: int | None = None,
    visible_caveat_allowed: bool = True,
) -> NarrativeSlotPlan:
    return NarrativeSlotPlan(
        slot=slot,
        purpose=SLOT_PURPOSES[slot],
        fact_ids=list(dict.fromkeys(fact_ids)),
        insight_ids=list(dict.fromkeys(insight_ids)),
        priority=priority,
        minimum_items=minimum_items,
        maximum_items=maximum_items,
        paragraph_hint=paragraph_hint,
        connective_hint=connective_hint,
        visible_caveat_allowed=visible_caveat_allowed,
    )


def build_event_narrative_plan(
    pack: WriterEvidencePack,
    content_requirements: dict[str, Any] | None = None,
) -> NarrativePlan:
    if pack.report_specification.genre not in EVENT_GENRES:
        return NarrativePlan()

    requirements = content_requirements or {}
    realisation_policy = requirements.get(
        "realisation_policy",
        pack.report_specification.realisation_policy.value,
    )
    event_recap_style = bool(
        realisation_policy == RealisationPolicy.EVENT_RECAP_STYLE.value
    )
    reference_recap_style = bool(
        requirements.get("reference_recap_style")
        or pack.report_specification.focus_scope == "reference_recap"
    )

    evidence_by_id = _evidence_lookup(pack)
    all_facts = [
        *pack.priority_facts,
        *pack.supporting_facts,
        *pack.limitation_facts,
    ]
    all_insights = [
        *pack.priority_verified_insights,
        *pack.supporting_verified_insights,
    ]

    fact_ids_by_slot: dict[NarrativeSlot, list[str]] = defaultdict(list)
    low_priority_fact_ids: list[str] = []

    for fact in all_facts:
        evidence_items = _fact_evidence(fact, evidence_by_id)
        slot = _slot_for_fact(fact, evidence_by_id)
        if slot is None:
            continue
        if _is_low_priority_event_fact(fact, evidence_items):
            low_priority_fact_ids.append(fact.fact_id)
            if slot == NarrativeSlot.LEADING_PERFORMANCES:
                fact_ids_by_slot[NarrativeSlot.SECONDARY_DETAILS].append(
                    fact.fact_id
                )
                continue
        fact_ids_by_slot[slot].append(fact.fact_id)

    planned_slots: list[NarrativeSlotPlan] = []
    slot_order = [
        (
            NarrativeSlot.OPENING_RESULT,
            1,
            1,
            1,
            None,
            None,
        ),
        (
            NarrativeSlot.EVENT_CONTEXT,
            2,
            1,
            1,
            "Attach context to the result sentence or opening paragraph.",
            None,
        ),
        (
            NarrativeSlot.SCORE_PROGRESSION,
            3,
            1,
            2,
            "Use progression as the bridge from result to event story.",
            None,
        ),
        (
            NarrativeSlot.EVENT_SEQUENCE,
            4,
            1,
            2,
            "Narrate only verified score-changing or ordered event steps.",
            None,
        ),
        (
            NarrativeSlot.LEADING_PERFORMANCES,
            5,
            2,
            3,
            "Group related achievements by entity instead of listing metrics.",
            None,
        ),
        (
            NarrativeSlot.PARTICIPANT_CONTRASTS,
            6,
            1,
            4,
            "Use bounded contrastive connectors; avoid causal wording.",
            None,
        ),
        (
            NarrativeSlot.SECONDARY_DETAILS,
            7,
            0,
            4,
            "Use only if it adds distinct report value after higher slots.",
            None,
        ),
    ]

    for slot, priority, minimum, paragraph, connective, maximum in slot_order:
        fact_ids = fact_ids_by_slot.get(slot, [])
        if not fact_ids and minimum > 0:
            continue
        insight_ids = _insight_ids_for_facts(all_insights, set(fact_ids))
        planned_slots.append(
            _slot_plan(
                slot=slot,
                fact_ids=fact_ids,
                insight_ids=insight_ids,
                priority=priority,
                minimum_items=min(minimum, len(fact_ids)),
                maximum_items=maximum,
                paragraph_hint=paragraph,
                connective_hint=connective,
            )
        )

    visible_scope_required = (
        requirements
        .get("narrative_requirements", {})
        .get("minimum_scope_limitations", 1)
    ) > 0
    if visible_scope_required:
        planned_slots.append(
            _slot_plan(
                slot=NarrativeSlot.CLOSING_SCOPE,
                fact_ids=[],
                insight_ids=[],
                priority=8,
                minimum_items=1,
                paragraph_hint=4,
                connective_hint=(
                    "Use one concise event-scoped caveat; do not add a "
                    "generic methodology section."
                ),
            )
        )

    if not planned_slots:
        return NarrativePlan()

    return NarrativePlan(
        applies=True,
        style=(
            "reference_recap"
            if reference_recap_style
            else "event_recap"
            if event_recap_style
            else "structured_event_report"
        ),
        allow_headings=not reference_recap_style,
        target_paragraphs=4 if (reference_recap_style or event_recap_style) else 5,
        slots=planned_slots,
        low_priority_fact_ids=list(dict.fromkeys(low_priority_fact_ids)),
        prohibited_narrative_moves=[
            "Do not add unsupported causes, momentum, dominance, historical "
            "significance, comeback labels or broader trends.",
            "Do not discuss row counts, missingness, constant columns, "
            "correlation, regression, modelling or feature removal unless "
            "the user explicitly requested dataset analysis.",
            "Do not satisfy sequence coverage by saying the sequence was not "
            "analysed when verified sequence evidence is available.",
        ],
        closing_policy=(
            "Reference-style recaps should not add a visible generic "
            "limitations paragraph. Add a final bounded sentence only when "
            "needed to prevent a misleading unsupported inference."
            if reference_recap_style
            else (
                "End with a concise event-scoped limitation that does not "
                "displace the event recap."
            )
        ),
    )
