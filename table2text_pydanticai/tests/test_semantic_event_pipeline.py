from __future__ import annotations

import json

import pandas as pd
import pytest

from table2text.agents import validate_insight_candidates
from table2text.analytics import execute_plan
from table2text.audit import (
    assess_genre_quality,
    augment_fact_ledger_for_report_coverage,
    build_writer_content_requirements,
    content_requirement_errors,
    deterministic_audit,
    deterministic_fact_candidate_scaffold,
    event_scope_limitation_present,
    fact_support_numbers,
    extract_number_tokens,
    fallback_fact_candidates,
    flatten_numbers,
    event_fact_slot,
    merge_fact_candidate_scaffold,
    numbers_supported,
    repair_spurious_missing_evidence_rejections,
    scope_fact_ledger_for_genre,
    select_event_priority_facts,
    split_markdown_sentences,
    validate_fact_candidates,
    validate_writer_output,
)
from table2text.capabilities import (
    available_capabilities,
    build_event_evidence_queries,
    event_capability_evidence,
    normalise_event_evidence_queries,
    normalise_semantic_map,
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
    FactReview,
    InputRepresentationStatus,
    InputSemanticMap,
    InputShape,
    InputStructureProfile,
    InsightCandidate,
    InsightCandidateSet,
    InsightLedger,
    InsightType,
    InterpretationLevel,
    InvestigationTask,
    QualityStatus,
    RecommendedUse,
    ReportGenre,
    ReportSelectionSource,
    ReportSpecification,
    ReviewDecision,
    SemanticBinding,
    SemanticLevel,
    SemanticRole,
    SentenceSupport,
    StructuralField,
    SupportType,
    VerificationResult,
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
        require_entity_measure_coverage=True,
    )

    assert any(
        "reserve substantive entity-performance bindings"
        in error
        for error in errors
    )


def paired_line_event() -> dict:
    return {
        "left_line": {
            "result": "win",
            "team_runs": "7",
            "team_hits": "11",
            "team_errors": "1",
            "team_name": "Mets",
        },
        "right_line": {
            "result": "loss",
            "team_runs": "2",
            "team_hits": "7",
            "team_errors": "1",
            "team_name": "D-backs",
        },
        "box_score": [
            {
                "full_name": "Jose Reyes",
                "team": "Mets",
                "h": "4",
                "r": "3",
                "rbi": "0",
                "hr": "0",
            },
            {
                "full_name": "Ryan Church",
                "team": "Mets",
                "h": "2",
                "r": "2",
                "rbi": "3",
                "hr": "1",
            },
            {
                "full_name": "John Maine",
                "team": "Mets",
                "p_so": "6",
                "p_r": "2",
            },
            {
                "full_name": "Chris Young",
                "team": "D-backs",
                "h": "1",
                "r": "0",
                "rbi": "1",
            },
        ],
        "day": "05_02_08",
    }


def test_paired_participant_line_records_enable_event_capabilities(
    tmp_path,
):
    path = tmp_path / "paired_event.json"
    path.write_text(json.dumps(paired_line_event()), encoding="utf-8")
    bundle = load_data([path])
    capabilities = available_capabilities(bundle)

    assert bundle.input_structure.shape == InputShape.EVENT_RECORD
    assert EvidenceCapability.EVENT_OUTCOME in capabilities
    assert EvidenceCapability.RANKING in capabilities
    assert EvidenceCapability.GROUP_COMPARISON in capabilities

    evidence = event_capability_evidence(paired_line_event())
    outcome = next(
        item
        for item in evidence
        if item.evidence_type == "event_outcome"
    )
    rankings = [
        item
        for item in evidence
        if item.evidence_type == "entity_ranking"
    ]
    contrasts = [
        item
        for item in evidence
        if item.evidence_type == "participant_comparison"
    ]

    assert outcome.metrics["winner"] == "Mets"
    assert outcome.metrics["loser"] == "D-backs"
    assert outcome.metrics["winner_score"] == 7
    assert any(
        item.metrics["metric"] == "hits"
        and item.metrics["ranking"][0]["entity"] == "Jose Reyes"
        and item.metrics["ranking"][0]["value"] == 4
        for item in rankings
    )
    assert any(item.metrics["metric"] == "hits" for item in contrasts)


def test_event_sequence_evidence_is_extracted_from_ordered_nested_records():
    payload = {
        "left_line": {
            "result": "win",
            "team_points": "9",
            "team_name": "North",
        },
        "right_line": {
            "result": "loss",
            "team_points": "4",
            "team_name": "South",
        },
        "timeline": [
            {
                "period": 1,
                "actions": [
                    {
                        "actor": "North",
                        "action": "score",
                        "north_score": 2,
                        "south_score": 0,
                    },
                    {
                        "actor": "South",
                        "action": "score",
                        "north_score": 2,
                        "south_score": 1,
                    },
                ],
            },
            {
                "period": 2,
                "actions": [
                    {
                        "actor": "North",
                        "action": "score",
                        "north_score": 9,
                        "south_score": 4,
                    }
                ],
            },
        ],
    }

    evidence = event_capability_evidence(payload)
    sequence = next(
        item
        for item in evidence
        if item.evidence_type == "event_sequence"
    )

    assert sequence.metrics["step_count"] == 3
    assert sequence.metrics["score_state_step_count"] == 3
    assert "ordered event sequence" in sequence.finding
    assert "score-state fields" in sequence.finding


def test_semantic_map_normalisation_repairs_obvious_event_function_mismatches():
    catalog = [
        StructuralField(
            table_name="event",
            path_pattern="left.name",
            value_types=["string"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="left.score",
            value_types=["integer"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="event.date",
            value_types=["string"],
        ),
    ]
    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event.",
        confidence=0.9,
        bindings=[
            SemanticBinding(
                binding_id="b_name",
                table_name="event",
                label="Participant name",
                role=SemanticRole.PARTICIPANT_IDENTIFIER,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="left.name",
                description="Participant identity.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
            SemanticBinding(
                binding_id="b_score",
                table_name="event",
                label="Score",
                role=SemanticRole.OUTCOME_MEASURE,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="left.score",
                description="Recorded outcome value.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
            SemanticBinding(
                binding_id="b_date",
                table_name="event",
                label="Date",
                role=SemanticRole.TIME,
                level=SemanticLevel.EVENT,
                path_pattern="event.date",
                description="Event time context.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.OUTCOME_COMPONENT,
            ),
        ],
    )

    assert validate_semantic_map(semantic_map, catalog)

    repaired = normalise_semantic_map(semantic_map)

    assert repaired is not None
    assert not validate_semantic_map(repaired, catalog)
    repaired_by_id = {
        binding.binding_id: binding
        for binding in repaired.bindings
    }
    assert repaired_by_id["b_name"].analytical_function is None
    assert (
        repaired_by_id["b_score"].analytical_function
        == AnalyticalFunction.OUTCOME
    )
    assert repaired_by_id["b_date"].analytical_function is None


def test_event_query_validation_accepts_numeric_like_string_samples():
    catalog = [
        StructuralField(
            table_name="event",
            path_pattern="entities[].name",
            value_types=["string"],
            sample_values=["Alpha", "Beta"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="entities[].metric",
            value_types=["string"],
            sample_values=["N/A", "4", "2"],
        ),
    ]
    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event.",
        confidence=0.9,
        bindings=[
            SemanticBinding(
                binding_id="b_entity",
                table_name="event",
                label="Entity name",
                role=SemanticRole.ENTITY_IDENTIFIER,
                level=SemanticLevel.ENTITY,
                path_pattern="entities[].name",
                description="Entity identity.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="b_metric",
                table_name="event",
                label="Entity metric",
                role=SemanticRole.PERFORMANCE_MEASURE,
                level=SemanticLevel.ENTITY,
                path_pattern="entities[].metric",
                description="Numeric-like metric stored as strings.",
                confidence=0.9,
                evidence_basis="sample values",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
        ],
    )
    query = EvidenceQuery(
        query_id="QUERY_METRIC",
        task_id="TASK_EVENT",
        operation=EvidenceOperation.RANK,
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_label="entity metric",
        question="Which entities have the highest recorded values?",
        semantic_level=SemanticLevel.ENTITY,
        table_name="event",
        value_binding_ids=["b_metric"],
        entity_binding_id="b_entity",
    )

    errors = validate_evidence_queries(
        [query],
        semantic_map,
        catalog,
        task_ids={"TASK_EVENT"},
        available={EvidenceCapability.RANKING},
        task_capabilities={"TASK_EVENT": EvidenceCapability.RANKING},
    )

    assert not any("non-numeric" in error for error in errors)


def test_event_query_completion_recovers_repeated_actor_performance_fields():
    catalog = [
        StructuralField(
            table_name="event",
            path_pattern="actors.*.name",
            value_types=["string"],
            sample_values=["Ada", "Bo"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="actors.*.side",
            value_types=["string"],
            sample_values=["North", "South"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="actors.*.points",
            value_types=["string"],
            sample_values=["9", "4"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="actors.*.assists",
            value_types=["string"],
            sample_values=["3", "7"],
        ),
    ]
    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event with repeated actor records.",
        confidence=0.9,
        bindings=[
            SemanticBinding(
                binding_id="b_actor",
                table_name="event",
                label="Actor name",
                role=SemanticRole.PARTICIPANT_IDENTIFIER,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="actors.*.name",
                description="Actor identity inside a repeated record.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="b_side",
                table_name="event",
                label="Actor side",
                role=SemanticRole.ENTITY_IDENTIFIER,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="actors.*.side",
                description="Actor affiliation inside the repeated record.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="b_points",
                table_name="event",
                label="Points",
                role=SemanticRole.PERFORMANCE_MEASURE,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="actors.*.points",
                description="Actor performance value.",
                confidence=0.9,
                evidence_basis="numeric-like values",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
            SemanticBinding(
                binding_id="b_assists",
                table_name="event",
                label="Assists",
                role=SemanticRole.PERFORMANCE_MEASURE,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="actors.*.assists",
                description="Actor performance value.",
                confidence=0.9,
                evidence_basis="numeric-like values",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
        ],
    )
    tasks = [
        InvestigationTask(
            task_id="TASK_RANKING",
            question="Which actors have the highest recorded performances?",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=4,
            table_name="event",
            capability=EvidenceCapability.RANKING,
            expected_evidence_types=["entity_ranking"],
            required_evidence=["entity_ranking"],
            claim_permissions=[
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
            answerability_note="Answerable from repeated actor records.",
        )
    ]

    repaired = normalise_semantic_map(semantic_map)
    queries = normalise_event_evidence_queries(
        queries=[],
        semantic_map=repaired,
        tasks=tasks,
        available_capabilities={EvidenceCapability.RANKING},
        request="Write an event report.",
    )

    by_value = {
        tuple(query.value_binding_ids): query
        for query in queries
        if query.evidence_type == "entity_ranking"
    }

    assert repaired is not None
    assert next(
        binding
        for binding in repaired.bindings
        if binding.binding_id == "b_actor"
    ).level == SemanticLevel.ENTITY
    assert by_value[("b_points",)].entity_binding_id == "b_actor"
    assert by_value[("b_points",)].group_binding_id == "b_side"
    assert by_value[("b_assists",)].entity_binding_id == "b_actor"
    assert not validate_evidence_queries(
        queries,
        repaired,
        catalog,
        task_ids={"TASK_RANKING"},
        available={EvidenceCapability.RANKING},
        task_capabilities={"TASK_RANKING": EvidenceCapability.RANKING},
    )


def test_event_query_normalisation_prunes_unexecutable_rankings():
    catalog = [
        StructuralField(
            table_name="event",
            path_pattern="teams.*.name",
            value_types=["string"],
            sample_values=["North", "South"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="teams.*.score",
            value_types=["integer"],
            sample_values=["9", "4"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="players.*.name",
            value_types=["string"],
            sample_values=["Ada", "Bo"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="players.*.metric",
            value_types=["string"],
            sample_values=["N/A", "-"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="players.*.points",
            value_types=["string"],
            sample_values=["9", "4"],
        ),
    ]
    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event with team and player records.",
        confidence=0.9,
        bindings=[
            SemanticBinding(
                binding_id="team_name",
                table_name="event",
                label="Team name",
                role=SemanticRole.PARTICIPANT_IDENTIFIER,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="teams.*.name",
                description="Team identity.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="team_score",
                table_name="event",
                label="Team score",
                role=SemanticRole.OUTCOME_MEASURE,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="teams.*.score",
                description="Team score.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.OUTCOME,
            ),
            SemanticBinding(
                binding_id="player_name",
                table_name="event",
                label="Player name",
                role=SemanticRole.ENTITY_IDENTIFIER,
                level=SemanticLevel.ENTITY,
                path_pattern="players.*.name",
                description="Player identity.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="player_metric",
                table_name="event",
                label="Unavailable player metric",
                role=SemanticRole.PERFORMANCE_MEASURE,
                level=SemanticLevel.ENTITY,
                path_pattern="players.*.metric",
                description="A metric with no numeric support.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
            SemanticBinding(
                binding_id="player_points",
                table_name="event",
                label="Player points",
                role=SemanticRole.PERFORMANCE_MEASURE,
                level=SemanticLevel.ENTITY,
                path_pattern="players.*.points",
                description="A numeric player performance value.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
        ],
    )
    tasks = [
        InvestigationTask(
            task_id="TASK_RANKING",
            question="Rank player performances.",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=4,
            table_name="event",
            capability=EvidenceCapability.RANKING,
            expected_evidence_types=["entity_ranking"],
            required_evidence=["entity_ranking"],
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            answerability_note="Only executable if a numeric measure exists.",
        ),
        InvestigationTask(
            task_id="TASK_EVENT",
            question="Report the result.",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=5,
            table_name="event",
            capability=EvidenceCapability.EVENT_OUTCOME,
            expected_evidence_types=["event_outcome"],
            required_evidence=["event_outcome"],
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            answerability_note="Supported by team score.",
        ),
    ]
    bad_queries = [
        EvidenceQuery(
            query_id="BAD_ENTITY_RANKING",
            task_id="TASK_RANKING",
            operation=EvidenceOperation.RANK,
            capability=EvidenceCapability.RANKING,
            evidence_type="entity_ranking",
            semantic_label="player unavailable metric",
            question="Which players rank highest?",
            semantic_level=SemanticLevel.ENTITY,
            table_name="event",
            value_binding_ids=["player_metric"],
            entity_binding_id="player_name",
        ),
        EvidenceQuery(
            query_id="BAD_TEAM_RANKING",
            task_id="TASK_RANKING",
            operation=EvidenceOperation.RANK,
            capability=EvidenceCapability.RANKING,
            evidence_type="entity_ranking",
            semantic_label="team score as entity ranking",
            question="Which entities rank highest?",
            semantic_level=SemanticLevel.ENTITY,
            table_name="event",
            value_binding_ids=["team_score"],
            entity_binding_id="team_name",
        ),
        EvidenceQuery(
            query_id="GOOD_ENTITY_RANKING",
            task_id="TASK_RANKING",
            operation=EvidenceOperation.RANK,
            capability=EvidenceCapability.RANKING,
            evidence_type="entity_ranking",
            semantic_label="player points",
            question="Which players rank highest by points?",
            semantic_level=SemanticLevel.ENTITY,
            table_name="event",
            value_binding_ids=["player_points"],
            entity_binding_id="player_name",
        ),
    ]

    queries = normalise_event_evidence_queries(
        queries=bad_queries,
        semantic_map=semantic_map,
        tasks=tasks,
        available_capabilities={
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.RANKING,
        },
        request="Write an event report.",
        structural_catalog=catalog,
    )

    assert all(
        query.query_id not in {"BAD_ENTITY_RANKING", "BAD_TEAM_RANKING"}
        for query in queries
    )
    assert any(query.query_id == "GOOD_ENTITY_RANKING" for query in queries)
    assert not validate_evidence_queries(
        queries,
        semantic_map,
        catalog,
        task_ids={"TASK_RANKING", "TASK_EVENT"},
        available={
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.RANKING,
        },
        task_capabilities={
            "TASK_RANKING": EvidenceCapability.RANKING,
            "TASK_EVENT": EvidenceCapability.EVENT_OUTCOME,
        },
    )


def test_semantic_rankings_skip_zero_only_performance_leaders():
    payload = {
        "players": [
            {"name": "Ada", "metric": "0"},
            {"name": "Bo", "metric": "0"},
        ]
    }
    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event with player records.",
        confidence=0.9,
        bindings=[
            SemanticBinding(
                binding_id="player_name",
                table_name="event",
                label="Player name",
                role=SemanticRole.ENTITY_IDENTIFIER,
                level=SemanticLevel.ENTITY,
                path_pattern="players.*.name",
                description="Player identity.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="player_metric",
                table_name="event",
                label="Player performance metric",
                role=SemanticRole.PERFORMANCE_MEASURE,
                level=SemanticLevel.ENTITY,
                path_pattern="players.*.metric",
                description="Player performance value.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.PERFORMANCE,
            ),
        ],
    )
    query = EvidenceQuery(
        query_id="QUERY_ZERO_ONLY",
        task_id="TASK_RANKING",
        operation=EvidenceOperation.RANK,
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_label="zero-only performance",
        question="Which players rank highest?",
        semantic_level=SemanticLevel.ENTITY,
        table_name="event",
        value_binding_ids=["player_metric"],
        entity_binding_id="player_name",
    )

    evidence = semantic_query_evidence(
        table_name="event",
        payload=payload,
        semantic_map=semantic_map,
        queries=[query],
    )

    assert evidence == []


def test_semantic_event_outcome_pairs_parallel_participant_fields():
    payload = {
        "home_name": "Astros",
        "vis_name": "Rangers",
        "home_line": {"team_runs": "4"},
        "vis_line": {"team_runs": "3"},
    }
    catalog = [
        StructuralField(
            table_name="event",
            path_pattern="home_name",
            value_types=["string"],
            sample_values=["Astros"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="vis_name",
            value_types=["string"],
            sample_values=["Rangers"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="home_line.team_runs",
            value_types=["string"],
            sample_values=["4"],
        ),
        StructuralField(
            table_name="event",
            path_pattern="vis_line.team_runs",
            value_types=["string"],
            sample_values=["3"],
        ),
    ]
    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event with parallel participant lines.",
        confidence=0.9,
        bindings=[
            SemanticBinding(
                binding_id="home_name",
                table_name="event",
                label="Home team name",
                role=SemanticRole.PARTICIPANT_IDENTIFIER,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="home_name",
                description="Home participant identity.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="vis_name",
                table_name="event",
                label="Visiting team name",
                role=SemanticRole.PARTICIPANT_IDENTIFIER,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="vis_name",
                description="Visiting participant identity.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="home_runs",
                table_name="event",
                label="Home team total runs",
                role=SemanticRole.OUTCOME_MEASURE,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="home_line.team_runs",
                description="Home participant outcome value.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.OUTCOME,
            ),
            SemanticBinding(
                binding_id="vis_runs",
                table_name="event",
                label="Visiting team total runs",
                role=SemanticRole.OUTCOME_MEASURE,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="vis_line.team_runs",
                description="Visiting participant outcome value.",
                confidence=0.9,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.OUTCOME,
            ),
        ],
    )
    tasks = [
        InvestigationTask(
            task_id="TASK_EVENT",
            question="Report the event outcome.",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=5,
            table_name="event",
            capability=EvidenceCapability.EVENT_OUTCOME,
            expected_evidence_types=["event_outcome"],
            required_evidence=["event_outcome"],
            claim_permissions=[
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
            answerability_note="Supported by parallel participant lines.",
        )
    ]

    queries = normalise_event_evidence_queries(
        queries=[],
        semantic_map=semantic_map,
        tasks=tasks,
        available_capabilities={EvidenceCapability.EVENT_OUTCOME},
        request="Write an event report.",
        structural_catalog=catalog,
    )
    outcome_query = next(
        query for query in queries if query.evidence_type == "event_outcome"
    )

    assert set(outcome_query.value_binding_ids) == {
        "home_runs",
        "vis_runs",
    }
    assert outcome_query.group_binding_id is None
    assert not validate_evidence_queries(
        queries,
        semantic_map,
        catalog,
        task_ids={"TASK_EVENT"},
        available={EvidenceCapability.EVENT_OUTCOME},
        task_capabilities={"TASK_EVENT": EvidenceCapability.EVENT_OUTCOME},
    )

    evidence = semantic_query_evidence(
        table_name="event",
        payload=payload,
        semantic_map=semantic_map,
        queries=queries,
    )
    outcome = next(
        item for item in evidence if item.evidence_type == "event_outcome"
    )

    assert outcome.metrics["difference"] == 1
    assert {
        (record["entity"], record["value"])
        for record in outcome.metrics["records"]
    } == {("Astros", 4.0), ("Rangers", 3.0)}


def test_semantic_event_comparisons_prefer_game_totals_over_segments():
    payload = {
        "teams": {
            "home": {
                "name": "Bucks",
                "line_score": {
                    "game": {"PTS": "114"},
                    "Q1": {"PTS": "30"},
                    "Q2": {"PTS": "31"},
                },
            },
            "vis": {
                "name": "Suns",
                "line_score": {
                    "game": {"PTS": "116"},
                    "Q1": {"PTS": "34"},
                    "Q2": {"PTS": "30"},
                },
            },
        }
    }
    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event with game and segment scores.",
        confidence=0.95,
        bindings=[
            SemanticBinding(
                binding_id="team_name",
                table_name="event",
                label="Team name",
                role=SemanticRole.PARTICIPANT_IDENTIFIER,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="teams.*.name",
                description="Participant identity.",
                confidence=0.95,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="team_points",
                table_name="event",
                label="Team points",
                role=SemanticRole.OUTCOME_MEASURE,
                level=SemanticLevel.PARTICIPANT,
                path_pattern="teams.*.line_score.*.PTS",
                description="Participant score values at multiple levels.",
                confidence=0.95,
                evidence_basis="field name",
                analytical_function=AnalyticalFunction.OUTCOME,
            ),
        ],
    )
    query = EvidenceQuery(
        query_id="QUERY_EVENT_OUTCOME",
        task_id="TASK_EVENT",
        operation=EvidenceOperation.COMPARE,
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_label="event outcome",
        question="How do participant scores compare?",
        semantic_level=SemanticLevel.PARTICIPANT,
        table_name="event",
        value_binding_ids=["team_points"],
        entity_binding_id="team_name",
    )

    evidence = semantic_query_evidence(
        table_name="event",
        payload=payload,
        semantic_map=semantic_map,
        queries=[query],
    )
    outcome = next(
        item for item in evidence if item.evidence_type == "event_outcome"
    )

    assert outcome.metrics["record_level_filter"] == "aggregate_event_level"
    assert outcome.metrics["difference"] == 2
    assert {
        (record["entity"], record["value"], record["source_path"])
        for record in outcome.metrics["records"]
    } == {
        ("Bucks", 114.0, "teams.home.line_score.game.PTS"),
        ("Suns", 116.0, "teams.vis.line_score.game.PTS"),
    }


def test_event_capability_evidence_adds_record_context_and_score_progression():
    payload = {
        "teams": {
            "home": {
                "name": "Bucks",
                "place": "Milwaukee",
                "wins": "13",
                "losses": "5",
                "line_score": {
                    "game": {"PTS": "114"},
                    "Q1": {"PTS": "30"},
                    "Q2": {"PTS": "31"},
                    "Q3": {"PTS": "29"},
                    "Q4": {"PTS": "24"},
                },
                "box_score": [
                    {"name": "Home Star", "PTS": "35"},
                ],
            },
            "vis": {
                "name": "Suns",
                "place": "Phoenix",
                "wins": "4",
                "losses": "14",
                "line_score": {
                    "game": {"PTS": "116"},
                    "Q1": {"PTS": "34"},
                    "Q2": {"PTS": "30"},
                    "Q3": {"PTS": "27"},
                    "Q4": {"PTS": "25"},
                },
                "box_score": [
                    {"name": "Vis Star", "PTS": "29"},
                ],
            },
        }
    }

    evidence = event_capability_evidence(payload)
    by_type = {item.evidence_type: item for item in evidence}

    assert "participant_record_context" in by_type
    assert "Milwaukee Bucks entered with 13 wins and 5 losses" in (
        by_type["participant_record_context"].finding
    )
    assert "score_progression" in by_type
    progression = by_type["score_progression"].metrics["segments"]
    after_q2 = next(item for item in progression if item["segment"] == "Q2")
    assert after_q2["cumulative_values"] == {
        "Milwaukee Bucks": 61.0,
        "Phoenix Suns": 64.0,
    }
    assert after_q2["leader"] == "Phoenix Suns"


def test_mixed_side_line_outcome_query_is_split_by_measure_family():
    def binding(
        binding_id: str,
        label: str,
        path: str,
    ) -> SemanticBinding:
        return SemanticBinding(
            binding_id=binding_id,
            table_name="event",
            label=label,
            role=SemanticRole.OUTCOME_MEASURE,
            level=SemanticLevel.ENTITY,
            path_pattern=path,
            description="Side-specific team line field.",
            confidence=0.9,
            evidence_basis="field name",
            analytical_function=AnalyticalFunction.OUTCOME,
        )

    semantic_map = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One event with side-specific line fields.",
        confidence=0.9,
        bindings=[
            SemanticBinding(
                binding_id="home_name",
                table_name="event",
                label="Home team",
                role=SemanticRole.ENTITY_IDENTIFIER,
                level=SemanticLevel.ENTITY,
                path_pattern="home_name",
                description="Home-side participant.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            SemanticBinding(
                binding_id="vis_name",
                table_name="event",
                label="Visiting team",
                role=SemanticRole.ENTITY_IDENTIFIER,
                level=SemanticLevel.ENTITY,
                path_pattern="vis_name",
                description="Visiting-side participant.",
                confidence=0.9,
                evidence_basis="field name",
            ),
            binding("home_runs", "Home team runs", "home_line.team_runs"),
            binding("vis_runs", "Visiting team runs", "vis_line.team_runs"),
            binding("home_hits", "Home team hits", "home_line.team_hits"),
            binding("vis_hits", "Visiting team hits", "vis_line.team_hits"),
            binding("home_errors", "Home team errors", "home_line.team_errors"),
            binding("vis_errors", "Visiting team errors", "vis_line.team_errors"),
        ],
    )
    catalog = [
        StructuralField(
            table_name="event",
            path_pattern=path,
            value_types=["integer"],
            sample_values=["1"],
        )
        for path in [
            "home_line.team_runs",
            "vis_line.team_runs",
            "home_line.team_hits",
            "vis_line.team_hits",
            "home_line.team_errors",
            "vis_line.team_errors",
        ]
    ]
    tasks = [
        InvestigationTask(
            task_id="TASK_EVENT",
            question="Report the event outcome.",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=5,
            table_name="event",
            capability=EvidenceCapability.EVENT_OUTCOME,
            expected_evidence_types=["event_outcome"],
            required_evidence=["event_outcome"],
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            answerability_note="Supported.",
        ),
        InvestigationTask(
            task_id="TASK_CONTRAST",
            question="Compare participant line components.",
            route=AnalysisRoute.DESCRIPTIVE,
            priority=4,
            table_name="event",
            capability=EvidenceCapability.GROUP_COMPARISON,
            expected_evidence_types=["participant_comparison"],
            required_evidence=["participant_comparison"],
            claim_permissions=[ClaimPermission.COMPARATIVE],
            answerability_note="Supported.",
        ),
    ]
    bad_query = EvidenceQuery(
        query_id="BAD_MIXED_OUTCOME",
        task_id="TASK_EVENT",
        operation=EvidenceOperation.COMPARE,
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_label="team outcome line",
        question="How many runs, hits, and errors did each team have?",
        semantic_level=SemanticLevel.PARTICIPANT,
        table_name="event",
        value_binding_ids=[
            "home_runs",
            "vis_runs",
            "home_hits",
            "vis_hits",
            "home_errors",
            "vis_errors",
        ],
        entity_binding_id="home_name",
    )

    queries = normalise_event_evidence_queries(
        queries=[bad_query],
        semantic_map=semantic_map,
        tasks=tasks,
        available_capabilities={
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.GROUP_COMPARISON,
        },
        request="Write a coherent event report.",
        structural_catalog=catalog,
    )

    assert "BAD_MIXED_OUTCOME" not in {query.query_id for query in queries}
    outcome = next(
        query for query in queries if query.evidence_type == "event_outcome"
    )
    contrasts = [
        query
        for query in queries
        if query.evidence_type == "participant_comparison"
    ]

    assert set(outcome.value_binding_ids) == {"home_runs", "vis_runs"}
    assert any(
        set(query.value_binding_ids) == {"home_hits", "vis_hits"}
        for query in contrasts
    )


def test_event_sequence_highlights_score_changing_records():
    payload = {
        "home_name": "North",
        "away_name": "South",
        "timeline": [
            {
                "period": "1",
                "home_score": "0",
                "away_score": "1",
                "points": "1",
                "actor": "Sol",
                "event": "opening score",
            },
            {
                "period": "2",
                "home_score": "2",
                "away_score": "1",
                "points": "2",
                "actor": "Nia",
                "event": "late score",
            },
        ],
    }

    evidence = event_capability_evidence(payload)
    sequence = next(
        item
        for item in evidence
        if item.evidence_type == "event_sequence"
        and item.strength_label == "event_sequence_highlight"
    )

    assert sequence.recommended_use == RecommendedUse.MAIN_FINDING
    assert sequence.metrics["highlight_count"] == 2
    assert "Sol recorded opening score" in sequence.finding
    assert "Nia recorded late score" in sequence.finding
    assert "South led 1-0" in sequence.finding
    assert "North led 2-1" in sequence.finding


def test_event_sequence_metrics_retain_all_score_changing_records():
    timeline = []
    north_score = 0
    south_score = 0
    for index in range(8):
        if index % 2 == 0:
            north_score += 1
            actor = f"North scorer {index}"
            event = "score"
        else:
            south_score += 2
            actor = f"South scorer {index}"
            event = "response"
        timeline.append(
            {
                "period": str(index + 1),
                "home_score": str(north_score),
                "away_score": str(south_score),
                "points": "1" if index % 2 == 0 else "2",
                "actor": actor,
                "event": event,
            }
        )

    evidence = event_capability_evidence(
        {
            "home_name": "North",
            "away_name": "South",
            "timeline": timeline,
        }
    )
    sequence = next(
        item
        for item in evidence
        if item.evidence_type == "event_sequence"
        and item.strength_label == "event_sequence_highlight"
    )

    assert sequence.metrics["highlight_count"] == 8
    assert len(sequence.metrics["highlights"]) == 8
    assert len(sequence.metrics["summary_highlights"]) == 6
    assert sequence.metrics["omitted_highlight_count"] == 2
    assert "2 later score-changing steps are omitted" in sequence.finding


def test_semantic_entity_ranking_uses_row_local_affiliation_context():
    payload = {
        "home_name": "Reds",
        "box_score": [
            {"full_name": "Carlos Delgado", "team": "Mets", "rbi": "4"},
            {"full_name": "Joey Votto", "team": "Reds", "rbi": "3"},
        ],
    }

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
            table_name="game",
            label=label,
            role=role,
            level=level,
            path_pattern=path,
            description=f"Semantic interpretation of {label}.",
            confidence=1.0,
            evidence_basis="Fixture.",
            analytical_function=analytical_function,
        )

    semantic = InputSemanticMap(
        input_shape=InputShape.EVENT_RECORD,
        record_description="One game with player rows.",
        bindings=[
            binding(
                "B_HOME",
                "Home team name",
                SemanticRole.PARTICIPANT_IDENTIFIER,
                SemanticLevel.PARTICIPANT,
                "home_name",
            ),
            binding(
                "B_PLAYER",
                "Player full name",
                SemanticRole.ENTITY_IDENTIFIER,
                SemanticLevel.ENTITY,
                "box_score.*.full_name",
            ),
            binding(
                "B_TEAM",
                "Player team",
                SemanticRole.CONTEXT,
                SemanticLevel.PARTICIPANT,
                "box_score.*.team",
            ),
            binding(
                "B_RBI",
                "Runs batted in",
                SemanticRole.PERFORMANCE_MEASURE,
                SemanticLevel.ENTITY,
                "box_score.*.rbi",
                AnalyticalFunction.PERFORMANCE,
            ),
        ],
        recommended_report_genre=ReportGenre.EVENT_REPORT,
        report_rationale="Fixture.",
        confidence=1.0,
    )

    row_local_query = EvidenceQuery(
        query_id="Q_RBI",
        task_id="TASK_EVENT",
        operation=EvidenceOperation.RANK,
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_label="entity ranking for RBI",
        question="Which players had the most RBI?",
        table_name="game",
        semantic_level=SemanticLevel.ENTITY,
        value_binding_ids=["B_RBI"],
        entity_binding_id="B_PLAYER",
        group_binding_id="B_TEAM",
        recommended_use=RecommendedUse.MAIN_FINDING,
        user_relevance=1.0,
        salience=1.0,
    )
    evidence = semantic_query_evidence(
        table_name="game",
        payload=payload,
        semantic_map=semantic,
        queries=[row_local_query],
    )
    ranking = evidence[0].metrics["ranking"]

    assert ranking[0]["entity"] == "Carlos Delgado"
    assert ranking[0]["group"] == "Mets"
    assert ranking[1]["group"] == "Reds"

    global_group_query = row_local_query.model_copy(
        update={"group_binding_id": "B_HOME"}
    )
    global_group_evidence = semantic_query_evidence(
        table_name="game",
        payload=payload,
        semantic_map=semantic,
        queries=[global_group_query],
    )
    global_ranking = global_group_evidence[0].metrics["ranking"]

    assert global_ranking[0]["group"] is None
    assert global_ranking[1]["group"] is None


def test_segment_rankings_do_not_satisfy_leading_performance_slot():
    segment = evidence_item(
        evidence_id="EVID_SEGMENT",
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_level=SemanticLevel.ENTITY,
        analytical_function=AnalyticalFunction.PERFORMANCE,
    ).model_copy(
        update={
            "metrics": {
                "semantic_label": "period scoring ranking",
                "question": "Which periods had the most scores?",
            },
            "source_paths": ["rounds.1.score"],
        }
    )
    actor = evidence_item(
        evidence_id="EVID_ACTOR",
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_level=SemanticLevel.ENTITY,
        analytical_function=AnalyticalFunction.PERFORMANCE,
    ).model_copy(
        update={
            "metrics": {
                "semantic_label": "actor points ranking",
                "question": "Which actors had the most points?",
            },
            "source_paths": ["actors.0.points"],
        }
    )
    lookup = {
        segment.evidence_id: segment,
        actor.evidence_id: actor,
    }

    assert (
        event_fact_slot(
            verified_fact(fact_id="FACT_SEGMENT", evidence=segment),
            lookup,
        )
        == "event_sequence"
    )
    assert (
        event_fact_slot(
            verified_fact(fact_id="FACT_ACTOR", evidence=actor),
            lookup,
        )
        == "leading_performance"
    )


def test_event_quality_gate_rejects_absent_sequence_claim_when_sequence_supported():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    )
    output = WriterOutput(
        title="Event report",
        markdown=(
            "# Event report\n\n"
            "North defeated South 9-4.\n"
            "The supplied data does not capture event dynamics or scoring progression.\n"
        ),
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text="North defeated South 9-4.",
                fact_ids=["FACT_EVENT"],
                evidence_ids=[event.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    assessment = assess_genre_quality(
        output,
        event_report_specification(),
        EvidenceLedger(fingerprint="fixture", items=[event, sequence]),
    )

    assert assessment.status == QualityStatus.REVISE
    assert any("event-sequence evidence" in finding for finding in assessment.findings)


def test_event_sequence_slot_recovers_writer_ready_fact_when_llm_omits_it():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "finding": (
                "The recorded event sequence includes two score-changing "
                "steps from the supplied play records."
            ),
            "strength_label": "event_sequence_highlight",
        }
    )
    ledger = FactLedger(
        writer_ready_facts=[
            verified_fact(fact_id="FACT_EVENT", evidence=event)
        ]
    )

    recovered = augment_fact_ledger_for_report_coverage(
        fact_ledger=ledger,
        evidence=EvidenceLedger(
            fingerprint="fixture",
            items=[event, sequence],
        ),
        required_components=[],
        required_content_slots=["event_result", "event_sequence"],
        settings=Settings(),
    )

    sequence_facts = [
        fact
        for fact in recovered.writer_ready_facts
        if sequence.evidence_id in fact.evidence_ids
    ]

    assert len(sequence_facts) == 1
    assert sequence_facts[0].fact_summary == sequence.finding
    assert (
        sequence_facts[0].verification_method
        == "deterministic_evidence_recovery"
    )


def test_required_event_contrast_recovers_when_existing_fact_is_omitted():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    contrast = evidence_item(
        evidence_id="EVID_CONTRAST",
        capability=EvidenceCapability.GROUP_COMPARISON,
        evidence_type="participant_comparison",
        semantic_level=SemanticLevel.EVENT,
        analytical_function=AnalyticalFunction.OUTCOME_COMPONENT,
    ).model_copy(
        update={
            "query_id": "QUERY_CONTRAST",
            "finding": (
                "Validated semantic query result for participant contrast."
            ),
            "metrics": {
                "records": [
                    {
                        "entity": "North",
                        "value": 12,
                        "measure": "goals",
                    },
                    {
                        "entity": "South",
                        "value": 9,
                        "measure": "goals",
                    },
                ],
                "difference": 3,
            },
        }
    )
    omitted_contrast_fact = verified_fact(
        fact_id="FACT_BAD_CONTRAST",
        evidence=contrast,
    ).model_copy(
        update={
            "fact_summary": (
                "Semantic query result is incomplete in the provided ledger."
            ),
            "recommended_use": RecommendedUse.OMIT_UNLESS_REQUESTED,
        }
    )
    ledger = FactLedger(
        writer_ready_facts=[
            verified_fact(fact_id="FACT_EVENT", evidence=event),
            omitted_contrast_fact,
        ]
    )

    recovered = augment_fact_ledger_for_report_coverage(
        fact_ledger=ledger,
        evidence=EvidenceLedger(
            fingerprint="fixture",
            items=[event, contrast],
        ),
        required_components=[],
        required_content_slots=["event_result", "main_contrast"],
        settings=Settings(),
    )

    recovered_contrasts = [
        fact
        for fact in recovered.writer_ready_facts
        if (
            contrast.evidence_id in fact.evidence_ids
            and fact.fact_id != omitted_contrast_fact.fact_id
        )
    ]

    assert len(recovered_contrasts) == 1
    assert "North recorded 12" in recovered_contrasts[0].fact_summary
    assert recovered_contrasts[0].recommended_use == contrast.recommended_use


def test_event_scope_caveat_does_not_trigger_causal_overclaim():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    sentence = (
        "This report describes only the supplied game; observed performances "
        "do not explain why the result occurred."
    )
    output = WriterOutput(
        title="Event report",
        markdown=sentence + "\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=[],
                evidence_ids=[],
                support_type=SupportType.NON_FACTUAL,
            )
        ],
    )

    audit = deterministic_audit(
        writer_output=output,
        fact_ledger=FactLedger(writer_ready_facts=[]),
        evidence=EvidenceLedger(fingerprint="fixture", items=[event]),
        mode=AuditMode.INTERNAL,
        external_sources=[],
        revision_round=0,
        report_specification=event_report_specification(),
        settings=Settings(),
    )

    assert not any(
        annotation.subtype == "causal_overclaim"
        for annotation in audit.annotations
    )


def test_event_scope_limitation_accepts_supplied_record_and_causality_caveats():
    output = WriterOutput(
        title="Event report",
        markdown=(
            "Sequence highlights describe recorded score-changing steps only "
            "and do not establish causality or momentum.\n"
            "The result is limited to values present in the supplied record.\n"
        ),
        sentence_support=[],
    )

    assert event_scope_limitation_present(output)


def test_fact_summary_numbers_support_recovered_sequence_sentence():
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "metrics": {
                "highlights": [
                    {
                        "event_text": (
                            "inning 9, segment top: Ramon Vazquez "
                            "recorded Home Run"
                        ),
                        "score_phrase": "Houston led 4-3",
                        "left_value": 4,
                        "right_value": 3,
                    }
                ]
            }
        }
    )
    fact = verified_fact(
        fact_id="FACT_SEQUENCE",
        evidence=sequence,
    ).model_copy(
        update={
            "fact_summary": (
                "The recorded score-changing sequence includes: inning 9, "
                "segment top: Ramon Vazquez recorded Home Run, after which "
                "Houston led 4-3."
            )
        }
    )

    support_numbers = fact_support_numbers(
        fact,
        EvidenceLedger(fingerprint="fixture", items=[sequence]),
    )

    assert numbers_supported(fact.fact_summary, support_numbers)


def test_event_content_requirements_ignore_omit_unless_requested_candidates():
    result = evidence_item(
        evidence_id="EVID_RESULT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    contrast = evidence_item(
        evidence_id="EVID_CONTRAST",
        capability=EvidenceCapability.GROUP_COMPARISON,
        evidence_type="participant_comparison",
        semantic_level=SemanticLevel.EVENT,
        analytical_function=AnalyticalFunction.OUTCOME_COMPONENT,
    )
    omitted = verified_fact(
        fact_id="FACT_OMITTED_CONTRAST",
        evidence=contrast,
    ).model_copy(
        update={"recommended_use": RecommendedUse.OMIT_UNLESS_REQUESTED}
    )
    usable = verified_fact(
        fact_id="FACT_USABLE_CONTRAST",
        evidence=contrast,
    )
    requirements = build_writer_content_requirements(
        report_specification=event_report_specification().model_copy(
            update={
                "required_content_slots": [
                    "event_result",
                    "main_contrast",
                ]
            }
        ),
        fact_ledger=FactLedger(
            writer_ready_facts=[
                verified_fact(fact_id="FACT_RESULT", evidence=result),
                omitted,
                usable,
            ]
        ),
        evidence=EvidenceLedger(
            fingerprint="fixture",
            items=[result, contrast],
        ),
        insight_ledger=InsightLedger(),
        settings=Settings(),
    )
    contrast_unit = next(
        unit
        for unit in requirements["units"]
        if unit["unit_id"] == "main_contrast"
    )

    assert contrast_unit["candidate_fact_ids"] == [usable.fact_id]
    assert contrast_unit["minimum_items"] == 1


def test_writer_validation_counts_title_fact_ids_as_selected():
    title_evidence = evidence_item(
        evidence_id="EVID_TITLE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    sentence_evidence = evidence_item(
        evidence_id="EVID_SENTENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    title_fact = verified_fact(
        fact_id="FACT_TITLE",
        evidence=title_evidence,
    )
    sentence_fact = verified_fact(
        fact_id="FACT_SENTENCE",
        evidence=sentence_evidence,
    )
    output = WriterOutput(
        title="Supported event report",
        title_fact_ids=[title_fact.fact_id],
        markdown="North defeated South 12-9.\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text="North defeated South 12-9.",
                fact_ids=[sentence_fact.fact_id],
                evidence_ids=[sentence_evidence.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
        selected_fact_ids=[
            title_fact.fact_id,
            sentence_fact.fact_id,
        ],
    )

    errors = validate_writer_output(
        output,
        FactLedger(
            writer_ready_facts=[
                title_fact,
                sentence_fact,
            ]
        ),
        allow_hypotheses_in_report=False,
    )

    assert "selected_fact_ids must match" not in "\n".join(errors)


def test_event_score_tie_claim_requires_sequence_score_state_support():
    performance = evidence_item(
        evidence_id="EVID_PERFORMANCE",
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_level=SemanticLevel.ENTITY,
    )
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "metrics": {
                "highlights": [
                    {
                        "event_text": (
                            "inning 9, segment top: Ramon Vazquez "
                            "recorded Home Run"
                        ),
                        "score_phrase": "Houston led 4-3",
                        "left_value": 4,
                        "right_value": 3,
                    }
                ]
            }
        }
    )
    fact = verified_fact(fact_id="FACT_PERFORMANCE", evidence=performance)
    sentence = "Ramon Vazquez hit a game-tying home run."
    output = WriterOutput(
        title="Event report",
        markdown=sentence + "\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=[fact.fact_id],
                evidence_ids=[performance.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    audit = deterministic_audit(
        writer_output=output,
        fact_ledger=FactLedger(writer_ready_facts=[fact]),
        evidence=EvidenceLedger(
            fingerprint="fixture",
            items=[performance, sequence],
        ),
        mode=AuditMode.INTERNAL,
        external_sources=[],
        revision_round=0,
        report_specification=event_report_specification(),
        settings=Settings(),
    )

    assert any(
        annotation.subtype == "unsupported_event_score_state"
        for annotation in audit.annotations
    )


def test_event_score_tie_claim_accepts_matching_sequence_highlight():
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "metrics": {
                "highlights": [
                    {
                        "event_text": (
                            "inning 2, segment bottom: Ty Wigginton "
                            "recorded Single"
                        ),
                        "score_phrase": "the score was level at 1-1",
                        "left_value": 1,
                        "right_value": 1,
                    }
                ]
            }
        }
    )
    fact = verified_fact(fact_id="FACT_SEQUENCE", evidence=sequence)
    sentence = "Ty Wigginton singled to tie the game."
    output = WriterOutput(
        title="Event report",
        markdown=sentence + "\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=[fact.fact_id],
                evidence_ids=[sequence.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    audit = deterministic_audit(
        writer_output=output,
        fact_ledger=FactLedger(writer_ready_facts=[fact]),
        evidence=EvidenceLedger(fingerprint="fixture", items=[sequence]),
        mode=AuditMode.INTERNAL,
        external_sources=[],
        revision_round=0,
        report_specification=event_report_specification(),
        settings=Settings(),
    )

    assert not any(
        annotation.subtype == "unsupported_event_score_state"
        for annotation in audit.annotations
    )


def test_event_score_tie_guardrail_allows_negated_tie_wording():
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "metrics": {
                "highlights": [
                    {
                        "event_text": (
                            "inning 8, segment bottom: Chris Dickerson "
                            "recorded Sac Fly"
                        ),
                        "score_phrase": "NY Mets led 9-7",
                        "left_value": 7,
                        "right_value": 9,
                    }
                ]
            }
        }
    )
    fact = verified_fact(fact_id="FACT_SEQUENCE", evidence=sequence)
    sentence = (
        "The Reds scored late on a Chris Dickerson sacrifice fly, but "
        "could not tie the game."
    )
    output = WriterOutput(
        title="Event report",
        markdown=sentence + "\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=[fact.fact_id],
                evidence_ids=[sequence.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    audit = deterministic_audit(
        writer_output=output,
        fact_ledger=FactLedger(writer_ready_facts=[fact]),
        evidence=EvidenceLedger(fingerprint="fixture", items=[sequence]),
        mode=AuditMode.INTERNAL,
        external_sources=[],
        revision_round=0,
        report_specification=event_report_specification(),
        settings=Settings(),
    )

    assert not any(
        annotation.subtype == "unsupported_event_score_state"
        for annotation in audit.annotations
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
    date_support_numbers = [
        number
        for _, number in extract_number_tokens(
            "Game date is 04_08_09."
        )
    ]

    assert numbers_supported(
        "The event was played on April 8, 2009.",
        date_support_numbers,
    )


def test_number_extraction_ignores_digits_embedded_in_entity_names():
    sentence = (
        "Philadelphia 76ers defeated Memphis Grizzlies 103-95, "
        "a margin of 8."
    )

    assert extract_number_tokens(sentence) == [
        ("103", 103.0),
        ("95", 95.0),
        ("8", 8.0),
    ]
    assert numbers_supported(
        sentence,
        [103.0, 95.0, 8.0],
    )


def test_sentence_splitter_keeps_player_initials_with_name():
    markdown = (
        "J.J. Redick recorded 24 points for Philadelphia 76ers. "
        "Jimmy Butler recorded 21."
    )

    assert split_markdown_sentences(markdown) == [
        "J.J. Redick recorded 24 points for Philadelphia 76ers.",
        "Jimmy Butler recorded 21.",
    ]


def test_sentence_splitter_keeps_versus_abbreviation_with_names():
    markdown = (
        "Starrcade featured Big Van Vader vs. Ric Flair. "
        "The event took place in 1993."
    )

    assert split_markdown_sentences(markdown) == [
        "Starrcade featured Big Van Vader vs. Ric Flair.",
        "The event took place in 1993.",
    ]


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
        required_components=[],
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


def test_event_fallback_evidence_emits_generic_context():
    results = event_capability_evidence(renamed_event())
    by_type = {item.evidence_type: item for item in results}

    assert "event_context" in by_type
    context_values = by_type["event_context"].metrics["values"]
    assert {item["value"] for item in context_values} >= {
        "2026-07-23",
        "Civic Hall",
    }
    assert by_type["event_context"].capability == (
        EvidenceCapability.DATASET_PROFILE
    )
    assert "supplied event context" in by_type["event_context"].finding


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
    assert len(
        {
            evidence_id
            for evidence_id in priority_evidence_ids
            if evidence_id.startswith("EVID_CONTRAST_")
        }
    ) == 3
    assert "EVID_GENERAL_CONTRAST" in priority_evidence_ids
    assert "EVID_PARTICIPATION" not in selected_evidence_ids


def test_event_priority_prefers_actionable_sequence_over_structural_sequence():
    result = evidence_item(
        evidence_id="EVID_RESULT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.PARTICIPANT,
    )
    structural_sequence = evidence_item(
        evidence_id="EVID_STRUCTURAL_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence",
            "metrics": {"step_count": 120},
        }
    )
    actionable_sequence = evidence_item(
        evidence_id="EVID_ACTIONABLE_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence_highlight",
            "metrics": {
                "sequence_type": "score_changing_sequence",
                "highlights": [
                    {
                        "event_text": "period 1: North recorded action A",
                        "score_phrase": "North led 2-0",
                        "score_delta": 2,
                        "left_value": 2,
                        "right_value": 0,
                    },
                    {
                        "event_text": "period 2: South recorded action B",
                        "score_phrase": "South led 3-2",
                        "score_delta": 3,
                        "left_value": 2,
                        "right_value": 3,
                    },
                ],
            },
        }
    )
    ledger = EvidenceLedger(
        fingerprint="fixture",
        items=[result, structural_sequence, actionable_sequence],
    )
    facts = [
        verified_fact(fact_id="FACT_RESULT", evidence=result),
        verified_fact(
            fact_id="FACT_STRUCTURAL_SEQUENCE",
            evidence=structural_sequence,
        ),
        verified_fact(
            fact_id="FACT_ACTIONABLE_SEQUENCE",
            evidence=actionable_sequence,
        ),
    ]

    priority, _ = select_event_priority_facts(
        facts=facts,
        evidence=ledger,
        settings=Settings(),
        request="Write an event report.",
    )

    priority_ids = {fact.fact_id for fact in priority}
    assert "FACT_ACTIONABLE_SEQUENCE" in priority_ids
    assert "FACT_STRUCTURAL_SEQUENCE" not in priority_ids


def test_event_content_requirements_use_actionable_sequence_candidates():
    structural_sequence = evidence_item(
        evidence_id="EVID_STRUCTURAL_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence",
            "metrics": {"step_count": 120},
        }
    )
    actionable_sequence = evidence_item(
        evidence_id="EVID_ACTIONABLE_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence_highlight",
            "metrics": {
                "sequence_type": "score_changing_sequence",
                "highlights": [
                    {
                        "event_text": "period 1: North recorded action A",
                        "score_phrase": "North led 2-0",
                        "score_delta": 2,
                    }
                ],
            },
        }
    )
    second_actionable_sequence = actionable_sequence.model_copy(
        update={
            "evidence_id": "EVID_SECOND_ACTIONABLE_SEQUENCE",
            "metrics": {
                "sequence_type": "score_changing_sequence",
                "highlights": [
                    {
                        "event_text": "period 2: South recorded action B",
                        "score_phrase": "South led 3-2",
                        "score_delta": 3,
                    }
                ],
            },
        }
    )
    spec = event_report_specification().model_copy(
        update={
            "required_content_slots": ["event_sequence"],
            "optional_content_slots": [],
        }
    )
    ledger = EvidenceLedger(
        fingerprint="fixture",
        items=[
            structural_sequence,
            actionable_sequence,
            second_actionable_sequence,
        ],
    )
    facts = [
        verified_fact(
            fact_id="FACT_STRUCTURAL_SEQUENCE",
            evidence=structural_sequence,
        ),
        verified_fact(
            fact_id="FACT_ACTIONABLE_SEQUENCE",
            evidence=actionable_sequence,
        ),
        verified_fact(
            fact_id="FACT_SECOND_ACTIONABLE_SEQUENCE",
            evidence=second_actionable_sequence,
        ),
    ]

    requirements = build_writer_content_requirements(
        report_specification=spec,
        fact_ledger=FactLedger(writer_ready_facts=facts),
        evidence=ledger,
        insight_ledger=InsightLedger(synthesis_enabled=False),
        settings=Settings(),
    )

    sequence_unit = next(
        unit
        for unit in requirements["units"]
        if unit["unit_id"] == "event_sequence"
    )
    assert sequence_unit["candidate_fact_ids"] == [
        "FACT_ACTIONABLE_SEQUENCE",
        "FACT_SECOND_ACTIONABLE_SEQUENCE",
    ]
    assert sequence_unit["minimum_items"] == 1


def test_event_content_requirements_prioritise_performance_before_sequence():
    result = evidence_item(
        evidence_id="EVID_RESULT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence_highlight",
            "metrics": {
                "sequence_type": "score_changing_sequence",
                "highlights": [
                    {
                        "event_text": "period 1: North recorded action A",
                        "score_phrase": "North led 2-0",
                        "score_delta": 2,
                    }
                ],
            },
        }
    )
    ranking = evidence_item(
        evidence_id="EVID_RANKING",
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_level=SemanticLevel.ENTITY,
        analytical_function=AnalyticalFunction.PERFORMANCE,
    )
    contrast = evidence_item(
        evidence_id="EVID_CONTRAST",
        capability=EvidenceCapability.GROUP_COMPARISON,
        evidence_type="event_contrast",
        semantic_level=SemanticLevel.PARTICIPANT,
        analytical_function=AnalyticalFunction.OUTCOME_COMPONENT,
    )
    spec = event_report_specification().model_copy(
        update={
            "required_content_slots": [
                "event_result",
                "event_sequence",
                "leading_performance",
                "main_contrast",
            ],
            "optional_content_slots": [],
        }
    )

    requirements = build_writer_content_requirements(
        report_specification=spec,
        fact_ledger=FactLedger(
            writer_ready_facts=[
                verified_fact(fact_id="FACT_RESULT", evidence=result),
                verified_fact(fact_id="FACT_SEQUENCE", evidence=sequence),
                verified_fact(fact_id="FACT_RANKING", evidence=ranking),
                verified_fact(fact_id="FACT_CONTRAST", evidence=contrast),
            ]
        ),
        evidence=EvidenceLedger(
            fingerprint="fixture",
            items=[result, sequence, ranking, contrast],
        ),
        insight_ledger=InsightLedger(synthesis_enabled=False),
        settings=Settings(),
    )

    unit_ids = [unit["unit_id"] for unit in requirements["units"]]

    assert unit_ids == [
        "event_result",
        "leading_performance",
        "main_contrast",
        "event_sequence",
    ]


def test_content_requirement_counts_insight_source_fact_coverage():
    requirements = {
        "units": [
            {
                "unit_id": "event_sequence",
                "description": "Use sequence facts.",
                "minimum_items": 2,
                "candidate_fact_ids": ["FACT_A", "FACT_B"],
                "candidate_insight_ids": ["INS_SEQUENCE"],
                "candidate_insight_fact_ids": {
                    "INS_SEQUENCE": ["FACT_A", "FACT_B"]
                },
            }
        ]
    }

    errors = content_requirement_errors(
        used_fact_ids=set(),
        used_insight_ids={"INS_SEQUENCE"},
        word_count=120,
        requirements=requirements,
    )

    assert errors == []


def test_event_quality_gate_requires_actionable_sequence_coverage():
    structural_sequence = evidence_item(
        evidence_id="EVID_STRUCTURAL_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence",
            "metrics": {"step_count": 120},
        }
    )
    actionable_sequence = evidence_item(
        evidence_id="EVID_ACTIONABLE_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence_highlight",
            "metrics": {
                "sequence_type": "score_changing_sequence",
                "highlights": [
                    {
                        "event_text": "period 1: North recorded action A",
                        "score_phrase": "North led 2-0",
                        "score_delta": 2,
                    }
                ],
            },
        }
    )
    spec = event_report_specification().model_copy(
        update={
            "required_content_slots": ["event_sequence"],
            "optional_content_slots": [],
        }
    )
    output = WriterOutput(
        title="Event report",
        markdown=(
            "# Event report\n\n"
            "The event structure includes an ordered sequence, but detailed "
            "chronology was not analyzed in this report.\n"
        ),
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=(
                    "The event structure includes an ordered sequence, but "
                    "detailed chronology was not analyzed in this report."
                ),
                fact_ids=["FACT_STRUCTURAL_SEQUENCE"],
                evidence_ids=[structural_sequence.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
    )

    assessment = assess_genre_quality(
        output,
        spec,
        EvidenceLedger(
            fingerprint="fixture",
            items=[structural_sequence, actionable_sequence],
        ),
    )

    assert assessment.status == QualityStatus.REVISE
    assert "event_sequence" in assessment.missing_supported_slots
    assert any(
        "omits or disclaims event-sequence narration" in finding
        for finding in assessment.findings
    )


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


def test_factual_title_numbers_can_be_supported_by_fact_summary():
    event = evidence_item(
        evidence_id="EVID_EVENT",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.EVENT,
    )
    score_fact = verified_fact(
        fact_id="FACT_SCORE",
        evidence=event,
    ).model_copy(
        update={
            "fact_summary": (
                "Mets recorded 9 for visiting runs, while Reds recorded 7 "
                "for home runs."
            ),
            "structured_values": {},
            "entities": ["Mets", "Reds"],
        }
    )
    output = WriterOutput(
        title="Mets Defeat Reds 9-7",
        title_fact_ids=["FACT_SCORE"],
        markdown=(
            "# Mets Defeat Reds 9-7\n\n"
            "Mets recorded 9 runs while Reds recorded 7.\n"
        ),
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=(
                    "Mets recorded 9 runs while Reds recorded 7."
                ),
                fact_ids=["FACT_SCORE"],
                evidence_ids=[event.evidence_id],
                support_type=SupportType.DIRECT,
            )
        ],
        selected_fact_ids=["FACT_SCORE"],
    )

    assert not validate_writer_output(
        output,
        FactLedger(writer_ready_facts=[score_fact]),
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


def test_deterministic_fact_fallback_recovers_semantic_query_evidence():
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

    assert len(candidates.candidates) == 1
    assert candidates.candidates[0].evidence_ids == ["EVID_QUERY"]


def test_deterministic_fact_fallback_summarises_event_outcome_records():
    query_evidence = evidence_item(
        evidence_id="EVID_OUTCOME",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.PARTICIPANT,
        analytical_function=AnalyticalFunction.OUTCOME,
    ).model_copy(
        update={
            "query_id": "QUERY_OUTCOME",
            "metrics": {
                "records": [
                    {
                        "entity": "Astros",
                        "value": 4.0,
                        "measure": "Home team total runs",
                    },
                    {
                        "entity": "Rangers",
                        "value": 3.0,
                        "measure": "Visiting team total runs",
                    },
                ]
            },
        }
    )

    candidates = fallback_fact_candidates(
        EvidenceLedger(fingerprint="fixture", items=[query_evidence]),
        maximum_facts=10,
    )

    assert len(candidates.candidates) == 1
    assert "Astros recorded 4" in candidates.candidates[0].fact_summary
    assert "Rangers recorded 3" in candidates.candidates[0].fact_summary


def test_fact_candidate_scaffold_merge_preserves_unenriched_evidence():
    first = evidence_item(
        evidence_id="EVID_FIRST",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_outcome",
        semantic_level=SemanticLevel.PARTICIPANT,
    ).model_copy(update={"finding": "First supported fact."})
    second = evidence_item(
        evidence_id="EVID_SECOND",
        capability=EvidenceCapability.RANKING,
        evidence_type="entity_ranking",
        semantic_level=SemanticLevel.ENTITY,
        analytical_function=AnalyticalFunction.PERFORMANCE,
    ).model_copy(update={"finding": "Second supported fact."})
    ledger = EvidenceLedger(fingerprint="fixture", items=[first, second])
    scaffold = deterministic_fact_candidate_scaffold(
        ledger,
        maximum_facts=None,
    )
    enrichment = FactCandidateSet(
        candidates=[
            FactCandidate(
                candidate_id="CAN_ENRICHED",
                fact_summary="First supported fact.",
                evidence_ids=["EVID_FIRST"],
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.MAIN_FINDING,
            )
        ],
        synthesis_notes=["LLM enriched one candidate."],
    )

    merged = merge_fact_candidate_scaffold(
        scaffold=scaffold,
        enrichment=enrichment,
        evidence=ledger,
    )
    covered = {
        evidence_id
        for candidate in merged.candidates
        for evidence_id in candidate.evidence_ids
    }

    assert covered == {"EVID_FIRST", "EVID_SECOND"}
    assert [candidate.candidate_id for candidate in merged.candidates] == [
        "CAN_0001",
        "CAN_0002",
    ]


def test_fact_candidate_scaffold_expands_event_sequence_highlights():
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence_highlight",
            "metrics": {
                "sequence_type": "score_changing_sequence",
                "highlights": [
                    {
                        "event_text": "period 1: North recorded action A",
                        "score_phrase": "North led 2-0",
                        "score_delta": 2,
                        "left_value": 2,
                        "right_value": 0,
                        "sequence_roles": ["opening_score"],
                    },
                    {
                        "event_text": "period 2: South recorded action B",
                        "score_phrase": "South led 3-2",
                        "score_delta": 3,
                        "left_value": 2,
                        "right_value": 3,
                        "sequence_roles": [
                            "lead_change",
                            "largest_score_change",
                        ],
                    },
                ],
            },
        }
    )

    scaffold = deterministic_fact_candidate_scaffold(
        EvidenceLedger(fingerprint="fixture", items=[sequence]),
        maximum_facts=None,
    )

    assert len(scaffold.candidates) == 2
    summaries = [candidate.fact_summary for candidate in scaffold.candidates]
    assert "period 1: North recorded action A" in summaries[0]
    assert "period 2: South recorded action B" in summaries[1]
    assert "lead change" not in summaries[1]


def test_scaffold_merge_preserves_multiple_candidates_for_one_sequence_evidence():
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={
            "strength_label": "event_sequence_highlight",
            "metrics": {
                "sequence_type": "score_changing_sequence",
                "highlights": [
                    {
                        "event_text": "period 1: North recorded action A",
                        "score_phrase": "North led 2-0",
                        "score_delta": 2,
                        "left_value": 2,
                        "right_value": 0,
                    },
                    {
                        "event_text": "period 2: South recorded action B",
                        "score_phrase": "South led 3-2",
                        "score_delta": 3,
                        "left_value": 2,
                        "right_value": 3,
                    },
                ],
            },
        }
    )
    ledger = EvidenceLedger(fingerprint="fixture", items=[sequence])
    scaffold = deterministic_fact_candidate_scaffold(
        ledger,
        maximum_facts=None,
    )
    enrichment = FactCandidateSet(
        candidates=[
            FactCandidate(
                candidate_id="CAN_ENRICHED",
                fact_summary=(
                    "The supplied sequence contains supported score-changing "
                    "steps."
                ),
                evidence_ids=["EVID_SEQUENCE"],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=1.0,
                salience=1.0,
                recommended_use=RecommendedUse.MAIN_FINDING,
            )
        ],
        synthesis_notes=["LLM enriched one sequence candidate."],
    )

    merged = merge_fact_candidate_scaffold(
        scaffold=scaffold,
        enrichment=enrichment,
        evidence=ledger,
    )

    assert len(merged.candidates) == 3
    assert any(
        "period 1: North recorded action A" in candidate.fact_summary
        for candidate in merged.candidates
    )
    assert any(
        "period 2: South recorded action B" in candidate.fact_summary
        for candidate in merged.candidates
    )
    assert any(
        "supported score-changing steps" in candidate.fact_summary
        for candidate in merged.candidates
    )


def test_spurious_missing_evidence_rejection_is_repaired():
    evidence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    ).model_copy(
        update={"limitations": ["Sequence evidence is descriptive only."]}
    )
    candidate = deterministic_fact_candidate_scaffold(
        EvidenceLedger(fingerprint="fixture", items=[evidence]),
        maximum_facts=None,
    ).candidates[0]
    verification = VerificationResult(
        reviews=[
            FactReview(
                candidate_id=candidate.candidate_id,
                decision=ReviewDecision.REJECT,
                rationale=(
                    "Cited evidence EVID_SEQUENCE not present in the "
                    "evidence list."
                ),
            )
        ]
    )

    repaired = repair_spurious_missing_evidence_rejections(
        candidate_set=FactCandidateSet(candidates=[candidate]),
        verification=verification,
        evidence=EvidenceLedger(fingerprint="fixture", items=[evidence]),
    )

    assert repaired.reviews[0].decision == ReviewDecision.CAUTION
    assert any(
        "Repaired spurious missing-evidence rejection" in note
        for note in repaired.overall_notes
    )


def test_event_insight_rejects_report_omission_meta_commentary():
    sequence = evidence_item(
        evidence_id="EVID_SEQUENCE",
        capability=EvidenceCapability.EVENT_OUTCOME,
        evidence_type="event_sequence",
        semantic_level=SemanticLevel.EVENT,
    )
    fact = verified_fact(fact_id="FACT_SEQUENCE", evidence=sequence)
    candidates = InsightCandidateSet(
        candidates=[
            InsightCandidate(
                insight_id="INS_META",
                statement=(
                    "The game data includes recorded play-by-play, but "
                    "detailed event chronology is not analyzed in this report."
                ),
                insight_type=InsightType.NARRATIVE_SUMMARY,
                interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                source_fact_ids=[fact.fact_id],
                source_evidence_ids=[sequence.evidence_id],
                supporting_summary=(
                    "The source fact says event-sequence evidence exists."
                ),
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                confidence=1.0,
                salience=0.8,
                suitable_for_main_report=True,
            )
        ]
    )

    errors = validate_insight_candidates(
        candidates,
        FactLedger(writer_ready_facts=[fact]),
        EvidenceLedger(fingerprint="fixture", items=[sequence]),
        Settings(),
        report_genre=ReportGenre.EVENT_REPORT,
    )

    assert any(
        "describes report omissions" in error
        for error in errors
    )


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
