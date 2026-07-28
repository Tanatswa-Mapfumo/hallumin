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
    "box_score",
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
EVENT_CONTEXT_ROLE_KEYS = {
    "context": {
        "event",
        "game",
        "context",
        "title",
        "name",
    },
    "time": {
        "date",
        "day",
        "dayname",
        "month",
        "monthname",
        "season",
        "time",
        "when",
        "year",
    },
    "location": {
        "arena",
        "city",
        "country",
        "location",
        "place",
        "site",
        "stadium",
        "state",
        "venue",
        "where",
    },
}
EVENT_STATUS_KEYS = {
    "cancelled",
    "completed",
    "extra_period",
    "extra_time",
    "overtime",
    "postponed",
    "status",
    "tied",
}
EVENT_CONTEXT_EXCLUDED_KEYS = {
    "attendance",
    "capacity",
    "game_id",
    "id",
    "next_game_id",
    "previous_game_id",
}


@dataclass(frozen=True)
class NumericLeaf:
    path: str
    key: str
    value: float


def _numeric_value(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", cleaned):
            return float(cleaned)
    return None


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
class EventContextValue:
    label: str
    value: Any
    source_path: str
    role: str


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
        elif (numeric := _numeric_value(current)) is not None:
            key = normalise_key(path.rsplit(".", 1)[-1])
            leaves.append(NumericLeaf(path=path, key=key, value=numeric))

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
            numeric = _numeric_value(child)
            if numeric is not None:
                canonical = _canonical_metric(str(key))
                if canonical:
                    metrics[canonical] = numeric
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
) -> tuple[str, Mapping[str, Any] | list[Any]] | None:
    stack: list[tuple[str, Any, int]] = [(prefix, value, 0)]
    while stack:
        path, current, depth = stack.pop()
        if depth > 6 or not isinstance(current, Mapping):
            continue
        for key, child in current.items():
            child_path = f"{path}.{key}" if path else str(key)
            normalised_key = normalise_key(str(key))
            if (
                normalised_key in ENTITY_CONTAINER_NAMES
                and isinstance(child, Mapping)
                and child
                and all(isinstance(item, Mapping) for item in child.values())
            ):
                return child_path, child
            if (
                normalised_key in ENTITY_CONTAINER_NAMES
                and isinstance(child, list)
                and child
                and all(isinstance(item, Mapping) for item in child)
            ):
                return child_path, child
            if isinstance(child, Mapping):
                stack.append((child_path, child, depth + 1))
    return None


def _entity_items(
    entities: Mapping[str, Any] | list[Any],
) -> list[tuple[str, Mapping[str, Any]]]:
    if isinstance(entities, Mapping):
        return [
            (str(key), value)
            for key, value in entities.items()
            if isinstance(value, Mapping)
        ]
    return [
        (str(index), value)
        for index, value in enumerate(entities)
        if isinstance(value, Mapping)
    ]


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
            for entity_key, raw_entity in _entity_items(entities):
                entity_metrics: dict[str, float] = {}
                entity_metric_paths: dict[str, str] = {}
                for raw_metric, raw_value in raw_entity.items():
                    numeric = _numeric_value(raw_value)
                    if numeric is None:
                        continue
                    canonical = _canonical_metric(str(raw_metric))
                    if canonical:
                        entity_metrics[canonical] = numeric
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


def _event_level_scalar_values(
    payload: Any,
    *,
    excluded_prefixes: list[str],
    max_depth: int = 4,
) -> list[EventContextValue]:
    values: list[EventContextValue] = []

    def visit(current: Any, path: str, depth: int) -> None:
        if depth > max_depth:
            return
        if path and any(
            path == prefix or path.startswith(f"{prefix}.")
            for prefix in excluded_prefixes
        ):
            return
        if isinstance(current, Mapping):
            for key, child in current.items():
                child_path = f"{path}.{key}" if path else str(key)
                visit(child, child_path, depth + 1)
            return
        if isinstance(current, (Mapping, list)) or current is None:
            return

        key = normalise_key(path.rsplit(".", 1)[-1])
        if key in EVENT_CONTEXT_EXCLUDED_KEYS:
            return

        role = next(
            (
                role_name
                for role_name, keys in EVENT_CONTEXT_ROLE_KEYS.items()
                if key in keys
            ),
            None,
        )
        if role is None and key in EVENT_STATUS_KEYS:
            role = "status"
        if role is None:
            return

        values.append(
            EventContextValue(
                label=path.rsplit(".", 1)[-1].replace("_", " "),
                value=current,
                source_path=path,
                role=role,
            )
        )

    visit(payload, "", 0)
    return values


def _stringify_context_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def _context_metric_map(
    values: list[EventContextValue],
) -> dict[str, EventContextValue]:
    mapped: dict[str, EventContextValue] = {}
    for value in values:
        key = normalise_key(value.label)
        mapped.setdefault(key, value)
    return mapped


def _event_context_finding(
    values: list[EventContextValue],
) -> str:
    by_key = _context_metric_map(values)
    date_parts = [
        by_key[key]
        for key in [
            "day",
            "monthname" if "monthname" in by_key else "month",
            "year",
        ]
        if key in by_key
    ]
    location_parts = [
        by_key[key]
        for key in ["venue", "stadium", "arena", "site", "city", "state", "country"]
        if key in by_key
    ]

    clauses: list[str] = []
    if date_parts:
        clauses.append(
            "on "
            + " ".join(_stringify_context_value(item.value) for item in date_parts)
        )
    if location_parts:
        first_location = _stringify_context_value(location_parts[0].value)
        remaining_location = ", ".join(
            _stringify_context_value(item.value)
            for item in location_parts[1:]
        )
        clauses.append(
            f"at {first_location}"
            if not remaining_location
            else f"at {first_location} in {remaining_location}"
        )

    if clauses:
        return (
            "The supplied event context records the event "
            + " ".join(clauses)
            + "."
        )

    fallback_values = "; ".join(
        f"{item.label}: {_stringify_context_value(item.value)}"
        for item in values[:8]
    )
    return f"The supplied event context records {fallback_values}."


def _event_context_evidence(payload: Any) -> list[CapabilityEvidence]:
    if not isinstance(payload, Mapping):
        return []

    located = find_participant_container(payload)
    excluded_prefixes = [located[0]] if located is not None else []
    values = _event_level_scalar_values(
        payload,
        excluded_prefixes=excluded_prefixes,
    )
    context_values = [
        item
        for item in values
        if item.role in {"context", "time", "location"}
    ]
    status_values = [
        item
        for item in values
        if item.role == "status"
    ]

    evidence: list[CapabilityEvidence] = []
    if context_values:
        evidence.append(
            CapabilityEvidence(
                capability=EvidenceCapability.DATASET_PROFILE,
                evidence_type="event_context",
                finding=_event_context_finding(context_values),
                metrics={
                    "values": [
                        {
                            "label": item.label,
                            "value": item.value,
                            "role": item.role,
                            "source_path": item.source_path,
                        }
                        for item in context_values
                    ],
                },
                source_paths=[item.source_path for item in context_values],
                entity_scope=[
                    _stringify_context_value(item.value)
                    for item in context_values
                    if item.role in {"location", "context"}
                ],
                practical_interpretation=(
                    "This records supplied event-level context without "
                    "using participant or entity statistics."
                ),
                strength_label="event_context",
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.75,
                salience=0.70,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                semantic_level=SemanticLevel.EVENT,
            )
        )

    for item in status_values:
        value_text = _stringify_context_value(item.value)
        normalised_label = normalise_key(item.label)
        if isinstance(item.value, bool) and normalised_label in {
            "extra_period",
            "extra_time",
            "overtime",
        }:
            status_finding = (
                f"The event required {item.label.replace('_', ' ')}."
                if item.value
                else f"The event did not require {item.label.replace('_', ' ')}."
            )
        else:
            status_finding = (
                f"The supplied event status records {item.label}: {value_text}."
            )
        evidence.append(
            CapabilityEvidence(
                capability=EvidenceCapability.EVENT_OUTCOME,
                evidence_type="event_status",
                finding=status_finding,
                metrics={
                    "label": item.label,
                    "value": item.value,
                    "source_path": item.source_path,
                },
                source_paths=[item.source_path],
                entity_scope=[],
                practical_interpretation=(
                    "This records a supplied event-status field."
                ),
                strength_label="event_status",
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.65,
                salience=0.55,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                semantic_level=SemanticLevel.EVENT,
            )
        )

    return evidence


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
    evidence: list[CapabilityEvidence] = _event_context_evidence(payload)
    if len(participants) < 2:
        return evidence

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
                if _numeric_value(match.value) is not None
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
                    "value": _numeric_value(value_match.value),
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
