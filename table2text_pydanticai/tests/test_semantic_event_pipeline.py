from __future__ import annotations

import json

import pandas as pd
import pytest

from table2text.agents import validate_insight_candidates
from table2text.analytics import execute_plan
from table2text.audit import (
    assess_genre_quality,
    extract_number_tokens,
    fallback_fact_candidates,
    flatten_numbers,
    numbers_supported,
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
