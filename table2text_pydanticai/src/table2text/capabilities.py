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
    SemanticBinding,
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
    EvidenceCapability.FOCUSED_TABLE_REGION: CapabilityDefinition(
        capability=EvidenceCapability.FOCUSED_TABLE_REGION,
        supported_input_shapes=[
            InputShape.FLAT_TABLE,
            InputShape.NESTED_RECORD,
            InputShape.ENTITY_COLLECTION,
            InputShape.INPUT_REFERENCE_PAIRS,
            InputShape.AMBIGUOUS,
        ],
        output_evidence_types=[
            "focused_table_region",
            "focused_cell_context",
        ],
    ),
    EvidenceCapability.STRUCTURED_RECORD_VERBALISATION: CapabilityDefinition(
        capability=EvidenceCapability.STRUCTURED_RECORD_VERBALISATION,
        supported_input_shapes=[
            InputShape.FLAT_TABLE,
            InputShape.NESTED_RECORD,
            InputShape.ENTITY_COLLECTION,
            InputShape.INPUT_REFERENCE_PAIRS,
            InputShape.AMBIGUOUS,
        ],
        output_evidence_types=[
            "attribute_record",
            "triple_record",
            "structured_record",
        ],
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
        output_evidence_types=[
            "event_outcome",
            "event_status",
            "event_sequence",
            "participant_record_context",
            "score_progression",
        ],
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
    EvidenceCapability.FOCUSED_TABLE_REGION: {
        "focused_table_region",
        "focused_cell_context",
    },
    EvidenceCapability.STRUCTURED_RECORD_VERBALISATION: {
        "attribute_record",
        "triple_record",
        "structured_record",
    },
    EvidenceCapability.EVENT_OUTCOME: {
        "event_outcome",
        "event_context",
        "event_status",
        "event_sequence",
    },
    EvidenceCapability.ENTITY_PERFORMANCE: {"entity_performance"},
    EvidenceCapability.RANKING: {"entity_ranking"},
    EvidenceCapability.GROUP_COMPARISON: {
        "participant_comparison",
        "event_contrast",
    },
}

QUERY_OPERATIONS: dict[str, EvidenceOperation] = {
    "focused_table_region": EvidenceOperation.RETRIEVE,
    "focused_cell_context": EvidenceOperation.RETRIEVE,
    "attribute_record": EvidenceOperation.RETRIEVE,
    "triple_record": EvidenceOperation.RETRIEVE,
    "structured_record": EvidenceOperation.RETRIEVE,
    "event_outcome": EvidenceOperation.COMPARE,
    "event_context": EvidenceOperation.RETRIEVE,
    "event_status": EvidenceOperation.RETRIEVE,
    "event_sequence": EvidenceOperation.RETRIEVE,
    "entity_performance": EvidenceOperation.RETRIEVE,
    "entity_ranking": EvidenceOperation.RANK,
    "participant_comparison": EvidenceOperation.COMPARE,
    "event_contrast": EvidenceOperation.COMPARE,
}


def _parse_pipe_triple(value: Any) -> tuple[str, str, str] | None:
    if not isinstance(value, str) or "|" not in value:
        return None
    parts = [part.strip() for part in value.split("|")]
    if len(parts) != 3 or not all(parts):
        return None
    return parts[0], parts[1], parts[2]


def _value_contains_serialized_triple(value: Any) -> bool:
    if _parse_pipe_triple(value) is not None:
        return True
    if isinstance(value, Mapping):
        triples = value.get("triples")
        if isinstance(triples, list) and any(
            _value_contains_serialized_triple(item)
            or (
                isinstance(item, (list, tuple))
                and len(item) == 3
                and all(str(part).strip() for part in item)
            )
            for item in triples
        ):
            return True
        return any(_value_contains_serialized_triple(item) for item in value.values())
    if isinstance(value, list):
        return any(_value_contains_serialized_triple(item) for item in value)
    return False


def _bundle_contains_serialized_triples(bundle: Any) -> bool:
    structured_inputs = getattr(bundle, "structured_inputs", {}) or {}
    if any(_value_contains_serialized_triple(value) for value in structured_inputs.values()):
        return True

    for frame in getattr(bundle, "tables", {}).values():
        columns = set(getattr(frame, "columns", []))
        candidate_columns = columns & {"source_payload", "source_text", "triples"}
        for column in candidate_columns:
            try:
                values = frame[column].tolist()
            except Exception:
                continue
            if any(_value_contains_serialized_triple(value) for value in values):
                return True
    return False


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


IDENTIFIER_ROLES = {
    SemanticRole.PARTICIPANT_IDENTIFIER,
    SemanticRole.ENTITY_IDENTIFIER,
    SemanticRole.IDENTIFIER,
}


def _path_parent(path_pattern: str) -> str:
    return path_pattern.rsplit(".", 1)[0] if "." in path_pattern else ""


def _repeated_parent(path_pattern: str) -> str | None:
    parent = _path_parent(path_pattern)
    if "*" not in parent and "[]" not in parent:
        return None
    return parent


def _binding_label_text(binding: SemanticBinding) -> str:
    return " ".join(
        part
        for part in [
            binding.label,
            binding.path_pattern,
            binding.description,
            binding.unit or "",
        ]
        if part
    ).lower()


def _identity_score(binding: SemanticBinding) -> float:
    text = _binding_label_text(binding)
    key = normalise_key(binding.path_pattern.rsplit(".", 1)[-1])
    score = 0.0
    if key in NAME_FIELD_NAMES:
        score += 8.0
    if any(
        term in text
        for term in [
            "name",
            "label",
            "actor",
            "entity",
            "member",
            "person",
            "performer",
            "player",
            "subject",
        ]
    ):
        score += 4.0
    if any(
        term in text
        for term in [
            "team",
            "side",
            "group",
            "participant",
            "affiliation",
        ]
    ):
        score -= 3.0
    if any(term in text for term in ["id", "code"]):
        score -= 4.0
    return score


def _affiliation_score(binding: SemanticBinding) -> float:
    text = _binding_label_text(binding)
    key = normalise_key(binding.path_pattern.rsplit(".", 1)[-1])
    score = 0.0
    if key in AFFILIATION_FIELD_NAMES:
        score += 6.0
    if any(
        term in text
        for term in [
            "team",
            "side",
            "group",
            "participant",
            "affiliation",
        ]
    ):
        score += 4.0
    if any(term in text for term in ["name", "label"]):
        score += 1.0
    return score


def _is_affiliation_binding(binding: SemanticBinding) -> bool:
    if binding.role in IDENTIFIER_ROLES:
        return True

    if binding.role not in {
        SemanticRole.CONTEXT,
        SemanticRole.METADATA,
        SemanticRole.LOCATION,
    }:
        return False

    return _affiliation_score(binding) > 0


def _measure_bindings_for_repeated_parents(
    bindings: list[SemanticBinding],
) -> dict[str, list[SemanticBinding]]:
    grouped: dict[str, list[SemanticBinding]] = {}
    for binding in bindings:
        parent = _repeated_parent(binding.path_pattern)
        if parent is None:
            continue
        if binding.role not in {
            SemanticRole.PERFORMANCE_MEASURE,
            SemanticRole.MEASURE,
            SemanticRole.OUTCOME_MEASURE,
        }:
            continue
        grouped.setdefault(parent, []).append(binding)
    return grouped


def _identifier_bindings_for_repeated_parents(
    bindings: list[SemanticBinding],
) -> dict[str, list[SemanticBinding]]:
    grouped: dict[str, list[SemanticBinding]] = {}
    for binding in bindings:
        parent = _repeated_parent(binding.path_pattern)
        if parent is None or binding.role not in IDENTIFIER_ROLES:
            continue
        grouped.setdefault(parent, []).append(binding)
    return grouped


def _repeated_entity_binding_ids(
    bindings: list[SemanticBinding],
) -> set[str]:
    measure_groups = _measure_bindings_for_repeated_parents(bindings)
    identifier_groups = _identifier_bindings_for_repeated_parents(bindings)
    repeated_parents = set(measure_groups) | set(identifier_groups)
    selected: set[str] = set()

    for parent, measures in measure_groups.items():
        if any(
            candidate != parent and candidate.startswith(f"{parent}.")
            for candidate in repeated_parents
        ):
            continue
        identifiers = identifier_groups.get(parent, [])
        if not identifiers or not measures:
            continue

        scored = sorted(
            identifiers,
            key=_identity_score,
            reverse=True,
        )
        best = scored[0]
        if _identity_score(best) <= 0 and len(scored) > 1:
            continue

        selected.add(best.binding_id)
        selected.update(binding.binding_id for binding in measures)

    return selected


def _local_entity_identifier(
    measure_binding: SemanticBinding,
    bindings: list[SemanticBinding],
) -> SemanticBinding | None:
    parent = _repeated_parent(measure_binding.path_pattern)
    candidates = [
        binding
        for binding in bindings
        if parent is not None
        and _repeated_parent(binding.path_pattern) == parent
        and binding.role == SemanticRole.ENTITY_IDENTIFIER
        and binding.level == SemanticLevel.ENTITY
    ]
    if not candidates and parent is None:
        candidates = [
            binding
            for binding in bindings
            if binding.role == SemanticRole.ENTITY_IDENTIFIER
            and binding.level == SemanticLevel.ENTITY
        ]
    if not candidates:
        return None
    return max(candidates, key=_identity_score)


def _global_entity_identifier(
    bindings: list[SemanticBinding],
) -> SemanticBinding | None:
    candidates = [
        binding
        for binding in bindings
        if binding.role == SemanticRole.ENTITY_IDENTIFIER
        and binding.level == SemanticLevel.ENTITY
    ]
    if not candidates:
        return None
    return max(candidates, key=_identity_score)


def _local_group_identifier(
    measure_binding: SemanticBinding,
    entity_binding: SemanticBinding | None,
    bindings: list[SemanticBinding],
    fallback_participant: SemanticBinding | None,
) -> SemanticBinding | None:
    parent = _repeated_parent(measure_binding.path_pattern)
    candidates = [
        binding
        for binding in bindings
        if parent is not None
        and _repeated_parent(binding.path_pattern) == parent
        and binding.binding_id != (
            entity_binding.binding_id if entity_binding else None
        )
        and _is_affiliation_binding(binding)
    ]
    if candidates:
        return max(candidates, key=_affiliation_score)
    return fallback_participant


def _measure_priority(
    binding_id: str,
    semantic_map: InputSemanticMap,
) -> float:
    binding = next(
        item
        for item in semantic_map.bindings
        if item.binding_id == binding_id
    )
    terminal_key = binding.path_pattern.rsplit(".", 1)[-1]
    text = " ".join(
        part
        for part in [
            binding.label,
            terminal_key,
            binding.unit or "",
        ]
        if part
    ).lower()
    text = re.sub(r"[_*.\-/]+", " ", text)
    score = (
        -90.0
        if re.search(
            r"\b(avg|average|era|loss(?:es)?|obp|ops|pct|percentage|"
            r"rate|record|standing|wins?)\b",
            text,
        )
        else 0.0
    )
    structural_text = re.sub(r"[_*.\-/]+", " ", _binding_label_text(binding))
    if re.search(
        r"\b(?:inning|half(?:-|\s)?inning|period|quarter|round|segment|"
        r"phase|frame|stage|play|turn|timeline|sequence)\b",
        structural_text,
    ):
        score -= 150.0
    if re.search(
        r"\b(?:allowed|against|caught\s+stealing|conceded|earned|error|"
        r"errors|loss|losses)\b",
        text,
    ):
        score -= 130.0
    if (
        re.search(r"\bstrikeout\w*\b", text)
        and not re.search(
            r"\b(?:defensive|pitcher|pitchers|pitching)\b",
            text,
        )
    ):
        score -= 130.0
    priority_terms = [
        (120.0, ("point", "score", "total", "run")),
        (100.0, ("goal", "made", "converted", "hit")),
        (95.0, ("rbi", "assist", "support")),
        (75.0, ("rebound", "recovery")),
        (72.0, ("strikeout",)),
        (71.0, ("double", "triple", "stolen")),
        (70.0, ("attempt", "opportunit")),
        (55.0, ("turnover", "error")),
        (50.0, ("steal", "block", "defen")),
        (20.0, ("foul", "penalt")),
        (-100.0, ("second", "minute", "duration", "time played", "sec")),
    ]
    for value, terms in priority_terms:
        if any(
            re.search(rf"\b{re.escape(term)}\w*\b", text)
            for term in terms
        ):
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
        score += 60.0
    elif binding.analytical_function == AnalyticalFunction.PERFORMANCE:
        score += 45.0
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


PARTICIPANT_SIDE_ALIASES = {
    "home": "home",
    "host": "home",
    "local": "home",
    "away": "away",
    "guest": "away",
    "road": "away",
    "vis": "away",
    "visitor": "away",
    "visiting": "away",
    "left": "left",
    "right": "right",
    "north": "north",
    "south": "south",
    "east": "east",
    "west": "west",
    "first": "first",
    "second": "second",
}


def _participant_side_key(binding: SemanticBinding) -> str | None:
    texts = [
        binding.path_pattern.rsplit(".", 1)[0],
        binding.path_pattern,
        binding.label,
    ]
    for text in texts:
        tokens = [
            token
            for token in normalise_key(text).split("_")
            if token
        ]
        for token in tokens[:3]:
            side = PARTICIPANT_SIDE_ALIASES.get(token)
            if side is not None:
                return side
    return None


def _participant_identifier_for_measure(
    measure_binding: SemanticBinding,
    participant_identifiers: list[SemanticBinding],
) -> SemanticBinding | None:
    side_key = _participant_side_key(measure_binding)
    if side_key is None:
        return None
    candidates = [
        binding
        for binding in participant_identifiers
        if _participant_side_key(binding) == side_key
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda binding: binding.confidence)


def _is_single_participant_side_binding(
    binding: SemanticBinding,
) -> bool:
    return (
        _participant_side_key(binding) is not None
        and _repeated_parent(binding.path_pattern) is None
    )


EVENT_RESULT_MEASURE_TERMS = {
    "points",
    "result",
    "runs",
    "score",
    "scored",
    "seats",
    "tally",
    "total",
    "votes",
}


def _looks_like_event_result_measure(
    binding: SemanticBinding,
) -> bool:
    tokens = set(
        token
        for token in normalise_key(
            " ".join(
                [
                    binding.path_pattern.rsplit(".", 1)[-1],
                    binding.label,
                ]
            )
        ).split("_")
        if token
    )
    return bool(tokens & EVENT_RESULT_MEASURE_TERMS)


PARALLEL_PARTICIPANT_COMPARISON_TYPES = {
    "event_outcome",
    "participant_comparison",
    "event_contrast",
}


def _participant_measure_family_key(
    binding: SemanticBinding,
) -> str:
    leaf = binding.path_pattern.rsplit(".", 1)[-1]
    side_tokens = set(PARTICIPANT_SIDE_ALIASES)
    tokens = [
        token
        for token in normalise_key(f"{leaf} {binding.label}").split("_")
        if token and token not in side_tokens
    ]
    return "_".join(tokens)


def _allows_parallel_participant_value_bindings(
    *,
    evidence_type: str,
    value_bindings: list[SemanticBinding],
) -> bool:
    if evidence_type not in PARALLEL_PARTICIPANT_COMPARISON_TYPES:
        return False
    if len(value_bindings) < 2:
        return False
    side_keys = [
        _participant_side_key(binding)
        for binding in value_bindings
    ]
    family_keys = {
        _participant_measure_family_key(binding)
        for binding in value_bindings
    }
    return (
        all(side_keys)
        and len(set(side_keys)) == len(side_keys)
        and len(family_keys) == 1
    )


def build_event_evidence_queries(
    *,
    semantic_map: InputSemanticMap | None,
    tasks: list[InvestigationTask],
    available_capabilities: set[EvidenceCapability],
    request: str,
) -> list[EvidenceQuery]:
    semantic_map = normalise_semantic_map(semantic_map)
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
    context_bindings = [
        binding
        for binding in bindings
        if binding.level == SemanticLevel.EVENT
        and binding.role
        in {
            SemanticRole.CONTEXT,
            SemanticRole.TIME,
            SemanticRole.LOCATION,
            SemanticRole.METADATA,
        }
    ]
    compact_context_bindings = [
        binding
        for binding in context_bindings
        if _repeated_parent(binding.path_pattern) is None
    ]
    context_ids = [
        binding.binding_id
        for binding in (compact_context_bindings or context_bindings)
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
    entity_performance_task_id = _task_id_for_capability(
        tasks,
        EvidenceCapability.ENTITY_PERFORMANCE,
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
        paired_outcome_ids = [
            binding_id
            for binding_id in sorted(
                outcome_ids,
                key=lambda item: _measure_priority(item, semantic_map),
                reverse=True,
            )
            if _participant_identifier_for_measure(
                next(
                    binding
                    for binding in bindings
                    if binding.binding_id == binding_id
                ),
                participant_identifiers,
            )
            is not None
        ]
        selected_outcome_ids = (
            paired_outcome_ids
            if len(paired_outcome_ids) >= 2
            else [
                max(
                    outcome_ids,
                    key=lambda binding_id: _measure_priority(
                        binding_id,
                        semantic_map,
                    ),
                )
            ]
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
                value_binding_ids=selected_outcome_ids,
                entity_binding_id=participant_id.binding_id,
                group_binding_id=(
                    participant_group.binding_id
                    if participant_group is not None
                    and len(selected_outcome_ids) == 1
                    else None
                ),
                recommended_use=RecommendedUse.HEADLINE,
                **common,
            )
        )

    if (
        ranking_task_id
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
            measure_binding = next(
                binding
                for binding in bindings
                if binding.binding_id == binding_id
            )
            local_entity_id = _local_entity_identifier(
                measure_binding,
                bindings,
            )
            if (
                local_entity_id is None
                and _repeated_parent(measure_binding.path_pattern) is None
            ):
                local_entity_id = entity_id
            if local_entity_id is None:
                continue
            local_group_id = _local_group_identifier(
                measure_binding,
                local_entity_id,
                bindings,
                participant_id,
            )
            priority_score = _measure_priority(binding_id, semantic_map)
            recommended_use = (
                RecommendedUse.MAIN_FINDING
                if priority_score >= 70
                else (
                    RecommendedUse.SUPPORTING_DETAIL
                    if priority_score >= 20
                    else RecommendedUse.OMIT_UNLESS_REQUESTED
                )
            )
            salience = (
                0.9
                if priority_score >= 70
                else (0.65 if priority_score >= 20 else 0.30)
            )
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
                    entity_binding_id=local_entity_id.binding_id,
                    group_binding_id=(
                        local_group_id.binding_id
                        if local_group_id is not None
                        else None
                    ),
                    limit=EVENT_RANKING_RESULT_LIMIT,
                    recommended_use=recommended_use,
                    user_relevance=salience,
                    salience=salience,
                    table_name=table_name,
                )
            )

    if (
        entity_performance_task_id
        and EvidenceCapability.ENTITY_PERFORMANCE in available_capabilities
        and not ranking_task_id
    ):
        ranked_measure_ids = sorted(
            entity_measure_ids,
            key=lambda item: _measure_priority(item, semantic_map),
            reverse=True,
        )
        for index, binding_id in enumerate(ranked_measure_ids, start=1):
            measure_binding = next(
                binding
                for binding in bindings
                if binding.binding_id == binding_id
            )
            local_entity_id = _local_entity_identifier(
                measure_binding,
                bindings,
            )
            if (
                local_entity_id is None
                and _repeated_parent(measure_binding.path_pattern) is None
            ):
                local_entity_id = entity_id
            if local_entity_id is None:
                continue
            local_group_id = _local_group_identifier(
                measure_binding,
                local_entity_id,
                bindings,
                participant_id,
            )
            priority_score = _measure_priority(binding_id, semantic_map)
            recommended_use = (
                RecommendedUse.MAIN_FINDING
                if priority_score >= 70
                else (
                    RecommendedUse.SUPPORTING_DETAIL
                    if priority_score >= 20
                    else RecommendedUse.OMIT_UNLESS_REQUESTED
                )
            )
            salience = (
                0.88
                if priority_score >= 70
                else (0.62 if priority_score >= 20 else 0.25)
            )
            queries.append(
                EvidenceQuery(
                    query_id=f"QUERY_ENTITY_PERFORMANCE_AUTO_{index:02d}",
                    task_id=entity_performance_task_id,
                    operation=EvidenceOperation.RETRIEVE,
                    capability=EvidenceCapability.ENTITY_PERFORMANCE,
                    evidence_type="entity_performance",
                    semantic_label=(
                        "entity performance for "
                        + measure_binding.label
                    ),
                    question="What entity-level performance values are recorded?",
                    semantic_level=SemanticLevel.ENTITY,
                    value_binding_ids=[binding_id],
                    entity_binding_id=local_entity_id.binding_id,
                    group_binding_id=(
                        local_group_id.binding_id
                        if local_group_id is not None
                        else None
                    ),
                    limit=EVENT_RANKING_RESULT_LIMIT,
                    recommended_use=recommended_use,
                    user_relevance=salience,
                    salience=salience,
                    table_name=table_name,
                )
            )

    if (
        comparison_task_id
        and participant_id
        and EvidenceCapability.GROUP_COMPARISON in available_capabilities
    ):
        participant_component_lookup = {
            binding.binding_id: binding
            for binding in bindings
            if binding.binding_id in participant_component_ids
        }
        paired_component_groups: dict[str, list[SemanticBinding]] = {}
        repeated_component_ids: list[str] = []
        for binding_id in sorted(
            participant_component_ids,
            key=lambda item: _measure_priority(item, semantic_map),
            reverse=True,
        ):
            binding = participant_component_lookup[binding_id]
            if _participant_identifier_for_measure(
                binding,
                participant_identifiers,
            ) is None:
                repeated_component_ids.append(binding_id)
                continue
            paired_component_groups.setdefault(
                _participant_measure_family_key(binding),
                [],
            ).append(binding)

        paired_queries: list[list[str]] = []
        used_component_ids: set[str] = set()
        for component_group in paired_component_groups.values():
            side_unique: dict[str, SemanticBinding] = {}
            for binding in component_group:
                side_key = _participant_side_key(binding)
                if side_key is None or side_key in side_unique:
                    continue
                side_unique[side_key] = binding
            if len(side_unique) < 2:
                repeated_component_ids.extend(
                    binding.binding_id
                    for binding in component_group
                    if binding.binding_id not in used_component_ids
                )
                continue
            selected_ids = [
                binding.binding_id
                for binding in sorted(
                    side_unique.values(),
                    key=lambda item: _measure_priority(
                        item.binding_id,
                        semantic_map,
                    ),
                    reverse=True,
                )
            ]
            used_component_ids.update(selected_ids)
            paired_queries.append(selected_ids)

        comparison_value_sets = [
            *paired_queries,
            *[
                [binding_id]
                for binding_id in repeated_component_ids
                if binding_id not in used_component_ids
            ],
        ]

        for index, value_binding_ids in enumerate(
            comparison_value_sets,
            start=1,
        ):
            priority_score = max(
                _measure_priority(binding_id, semantic_map)
                for binding_id in value_binding_ids
            )
            recommended_use = (
                RecommendedUse.SUPPORTING_DETAIL
                if priority_score >= 20
                else RecommendedUse.OMIT_UNLESS_REQUESTED
            )
            salience = 0.85 if priority_score >= 20 else 0.30
            primary_binding_id = value_binding_ids[0]
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
                            if binding.binding_id == primary_binding_id
                        )
                    ),
                    question="How do participant-level measures compare?",
                    semantic_level=SemanticLevel.PARTICIPANT,
                    value_binding_ids=value_binding_ids,
                    entity_binding_id=participant_id.binding_id,
                    group_binding_id=(
                        participant_group.binding_id
                        if participant_group is not None
                        and len(value_binding_ids) == 1
                        else None
                    ),
                    recommended_use=recommended_use,
                    user_relevance=salience,
                    salience=salience,
                    table_name=table_name,
                )
            )

    return queries


def _normalise_event_query_priority(
    query: EvidenceQuery,
    semantic_map: InputSemanticMap,
) -> EvidenceQuery:
    if query.evidence_type not in {
        "entity_ranking",
        "entity_performance",
        "participant_comparison",
        "event_contrast",
    }:
        return query

    priority_scores = [
        _measure_priority(binding_id, semantic_map)
        for binding_id in query.value_binding_ids
    ]
    if not priority_scores:
        return query

    priority_score = max(priority_scores)
    if query.evidence_type in {
        "entity_ranking",
        "entity_performance",
    }:
        recommended_use = (
            RecommendedUse.MAIN_FINDING
            if priority_score >= 70
            else (
                RecommendedUse.SUPPORTING_DETAIL
                if priority_score >= 20
                else RecommendedUse.OMIT_UNLESS_REQUESTED
            )
        )
        salience = (
            0.9
            if priority_score >= 70
            else (0.65 if priority_score >= 20 else 0.30)
        )
    else:
        recommended_use = (
            RecommendedUse.SUPPORTING_DETAIL
            if priority_score >= 20
            else RecommendedUse.OMIT_UNLESS_REQUESTED
        )
        salience = 0.85 if priority_score >= 20 else 0.30

    return query.model_copy(
        update={
            "recommended_use": recommended_use,
            "user_relevance": min(query.user_relevance, salience),
            "salience": min(query.salience, salience),
        }
    )


def normalise_event_evidence_queries(
    *,
    queries: list[EvidenceQuery],
    semantic_map: InputSemanticMap | None,
    tasks: list[InvestigationTask],
    available_capabilities: set[EvidenceCapability],
    request: str,
    structural_catalog: list[StructuralField] | None = None,
) -> list[EvidenceQuery]:
    semantic_map = normalise_semantic_map(semantic_map)
    if semantic_map is None or semantic_map.input_shape != InputShape.EVENT_RECORD:
        return queries

    generated = build_event_evidence_queries(
        semantic_map=semantic_map,
        tasks=tasks,
        available_capabilities=available_capabilities,
        request=request,
    )
    combined = [
        _normalise_event_query_priority(query, semantic_map)
        for query in [*queries, *generated]
    ]
    unique: list[EvidenceQuery] = []
    signatures: set[
        tuple[
            str,
            tuple[str, ...],
            str | None,
            str | None,
        ]
    ] = set()
    task_capabilities = {
        task.task_id: task.capability
        for task in tasks
    }
    for query in combined:
        if not _event_query_is_semantically_executable(
            query=query,
            semantic_map=semantic_map,
            structural_catalog=structural_catalog or [],
            available_capabilities=available_capabilities,
            task_capabilities=task_capabilities,
        ):
            continue
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
        if query.evidence_type in PARALLEL_PARTICIPANT_COMPARISON_TYPES:
            score += 2.0 * len(query.value_binding_ids)
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


def _event_query_is_semantically_executable(
    *,
    query: EvidenceQuery,
    semantic_map: InputSemanticMap,
    structural_catalog: list[StructuralField],
    available_capabilities: set[EvidenceCapability],
    task_capabilities: dict[str, EvidenceCapability | None],
) -> bool:
    """Return whether an event query can be safely executed.

    This is intentionally a permissive sanitiser for LLM-authored and
    controller-completed queries. The formal validator still reports errors;
    this gate prevents known-bad event queries from poisoning an otherwise
    recoverable plan.
    """

    if query.capability not in available_capabilities:
        return False
    if (
        query.task_id in task_capabilities
        and task_capabilities[query.task_id] is not None
        and task_capabilities[query.task_id] != query.capability
    ):
        return False

    allowed_evidence_types = QUERY_EVIDENCE_TYPES.get(query.capability)
    if (
        allowed_evidence_types is not None
        and query.evidence_type not in allowed_evidence_types
    ):
        return False

    expected_operation = QUERY_OPERATIONS.get(query.evidence_type)
    if expected_operation is not None and query.operation != expected_operation:
        return False

    binding_lookup = {
        binding.binding_id: binding
        for binding in semantic_map.bindings
    }
    referenced_ids = [
        *query.value_binding_ids,
        *query.context_binding_ids,
        *([query.entity_binding_id] if query.entity_binding_id else []),
        *([query.group_binding_id] if query.group_binding_id else []),
    ]
    if any(binding_id not in binding_lookup for binding_id in referenced_ids):
        return False
    if any(
        binding_lookup[binding_id].table_name != query.table_name
        for binding_id in referenced_ids
    ):
        return False

    value_bindings = [
        binding_lookup[binding_id]
        for binding_id in query.value_binding_ids
    ]
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
    if allowed_value_roles is not None and any(
        binding.role not in allowed_value_roles
        for binding in value_bindings
    ):
        return False

    entity_binding = (
        binding_lookup.get(query.entity_binding_id)
        if query.entity_binding_id
        else None
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
            return False
        if entity_binding.level != expected_entity_level:
            return False

    if not query.value_binding_ids:
        return False
    if query.operation in {
        EvidenceOperation.COMPARE,
        EvidenceOperation.RANK,
    }:
        if (
            query.evidence_type not in PARALLEL_PARTICIPANT_COMPARISON_TYPES
            and len(query.value_binding_ids) != 1
        ):
            return False
        if query.evidence_type in PARALLEL_PARTICIPANT_COMPARISON_TYPES:
            if not query.value_binding_ids:
                return False
            if len(query.value_binding_ids) > 1 and not (
                query.operation == EvidenceOperation.COMPARE
                and _allows_parallel_participant_value_bindings(
                    evidence_type=query.evidence_type,
                    value_bindings=value_bindings,
                )
            ):
                return False
        if query.entity_binding_id is None:
            return False

        catalog_lookup = {
            (field.table_name, field.path_pattern): field
            for field in structural_catalog
        }
        for binding in value_bindings:
            field = catalog_lookup.get(
                (binding.table_name, binding.path_pattern)
            )
            if field is not None and not _field_supports_numeric_measure(field):
                return False

    return True


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
AFFILIATION_FIELD_NAMES = {
    "participant",
    "participant_name",
    "side",
    "team",
    "team_name",
}
LINE_RECORD_SUFFIXES = {
    "line",
    "record",
    "summary",
}
SCORE_FIELD_NAMES = {
    "final_score",
    "points",
    "pts",
    "score",
    "team_points",
    "team_runs",
    "total",
}
EVENT_AGGREGATE_LEVEL_TERMS = {
    "event",
    "final",
    "full",
    "game",
    "match",
    "overall",
    "total",
}
EVENT_SEGMENT_LEVEL_TERMS = {
    "half",
    "h1",
    "h2",
    "inning",
    "innings",
    "ot",
    "overtime",
    "period",
    "periods",
    "q1",
    "q2",
    "q3",
    "q4",
    "quarter",
    "quarters",
    "segment",
    "segments",
}
PARTICIPANT_RECORD_CONTEXT_KEYS = {
    "draws",
    "game_number",
    "losses",
    "rank",
    "ranking",
    "record",
    "seed",
    "standing",
    "ties",
    "wins",
}
METRIC_ALIASES = {
    "points": {"points", "pts", "score"},
    "runs": {"r", "runs", "team_runs"},
    "hits": {"h", "hits", "team_hits"},
    "errors": {"e", "errors", "team_errors"},
    "runs batted in": {"rbi", "runs_batted_in"},
    "home runs": {"hr", "home_runs"},
    "triples": {"t", "triples"},
    "doubles": {"d", "doubles"},
    "strikeouts": {"so", "strikeouts"},
    "pitching strikeouts": {"p_so"},
    "walks": {"bb", "walks"},
    "pitching walks": {"p_bb"},
    "earned runs allowed": {"p_er"},
    "runs allowed": {"p_r"},
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

PRIMARY_ENTITY_METRIC_PRIORITY = [
    "points",
    "runs",
    "hits",
    "runs batted in",
    "home runs",
    "pitching strikeouts",
    "strikeouts",
    "assists",
    "rebounds",
    "triples",
    "doubles",
    "walks",
]
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
SEQUENCE_CONTAINER_TERMS = {
    "action",
    "actions",
    "event",
    "events",
    "phase",
    "phases",
    "play",
    "plays",
    "round",
    "rounds",
    "segment",
    "segments",
    "sequence",
    "step",
    "steps",
    "timeline",
    "turn",
    "turns",
}
SEQUENCE_ORDER_KEYS = {
    "frame",
    "half",
    "inning",
    "index",
    "order",
    "period",
    "phase",
    "quarter",
    "round",
    "segment",
    "sequence",
    "step",
    "time",
    "timestamp",
    "turn",
}
SEQUENCE_ACTION_KEYS = {
    "action",
    "description",
    "event",
    "event_type",
    "outcome",
    "result",
    "summary",
    "type",
}
SEQUENCE_PARTICIPANT_KEYS = {
    "actor",
    "batter",
    "competitor",
    "entity",
    "participant",
    "participant_name",
    "performer",
    "pitcher",
    "player",
    "scorer",
    "scorers",
    "side",
    "subject",
    "team",
    "team_name",
}
SEQUENCE_SCORE_KEYS = {
    "goals",
    "score",
    "score_state",
    "scores",
    "points",
    "runs",
    "total",
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
    record_context: dict[str, Any] = field(default_factory=dict)
    record_context_paths: dict[str, str] = field(default_factory=dict)
    segment_scores: dict[str, tuple[float, str]] = field(default_factory=dict)


@dataclass(frozen=True)
class EventContextValue:
    label: str
    value: Any
    source_path: str
    role: str


@dataclass(frozen=True)
class EventSequenceRecord:
    source_path: str
    order_values: dict[str, Any] = field(default_factory=dict)
    action_values: dict[str, Any] = field(default_factory=dict)
    participant_values: dict[str, Any] = field(default_factory=dict)
    score_values: dict[str, Any] = field(default_factory=dict)


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


def _metric_priority(metric: str) -> tuple[int, str]:
    try:
        return (
            -PRIMARY_ENTITY_METRIC_PRIORITY.index(metric),
            metric,
        )
    except ValueError:
        return (-len(PRIMARY_ENTITY_METRIC_PRIORITY), metric)


def _normalised_path_tokens(path: str) -> list[str]:
    return [
        token
        for token in normalise_key(path).split("_")
        if token
    ]


def _event_measure_path_is_aggregate(path: str) -> bool:
    tokens = set(_normalised_path_tokens(path))
    return bool(tokens & EVENT_AGGREGATE_LEVEL_TERMS)


def _event_measure_path_is_segment(path: str) -> bool:
    tokens = set(_normalised_path_tokens(path))
    if tokens & EVENT_SEGMENT_LEVEL_TERMS:
        return True
    return any(
        re.fullmatch(r"(?:q|h|p|period|quarter|inning)\d+", token)
        for token in tokens
    )


def _event_record_identity(record: Mapping[str, Any]) -> tuple[str, str]:
    return (
        str(record.get("entity") or ""),
        str(record.get("group") or ""),
    )


def _event_records_cover_multiple_entities(
    records: list[dict[str, Any]],
) -> bool:
    return len({_event_record_identity(record) for record in records}) >= 2


def _deduplicate_event_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    retained: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        key = (
            *_event_record_identity(record),
            str(record.get("measure") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        retained.append(record)
    return retained


def _comparable_event_records(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str | None]:
    """Prefer event/game totals over segment values for direct comparisons."""

    if len(records) < 3:
        return records, None

    aggregate_records = [
        record
        for record in records
        if _event_measure_path_is_aggregate(str(record.get("source_path") or ""))
    ]
    if _event_records_cover_multiple_entities(aggregate_records):
        return (
            _deduplicate_event_records(aggregate_records),
            "aggregate_event_level",
        )

    non_segment_records = [
        record
        for record in records
        if not _event_measure_path_is_segment(
            str(record.get("source_path") or "")
        )
    ]
    if _event_records_cover_multiple_entities(non_segment_records):
        return (
            _deduplicate_event_records(non_segment_records),
            "non_segment_event_level",
        )

    return records, None


EVENT_MEASURE_ROLES = {
    SemanticRole.OUTCOME_MEASURE,
    SemanticRole.PERFORMANCE_MEASURE,
    SemanticRole.MEASURE,
}
MEASURE_ANALYTICAL_FUNCTIONS = {
    AnalyticalFunction.OUTCOME,
    AnalyticalFunction.OUTCOME_COMPONENT,
    AnalyticalFunction.PERFORMANCE,
    AnalyticalFunction.PARTICIPATION,
}


def _default_event_analytical_function(
    binding: Any,
) -> AnalyticalFunction:
    if binding.role == SemanticRole.OUTCOME_MEASURE:
        return AnalyticalFunction.OUTCOME
    if binding.level == SemanticLevel.PARTICIPANT:
        return AnalyticalFunction.OUTCOME_COMPONENT
    if binding.level == SemanticLevel.ENTITY:
        return AnalyticalFunction.PERFORMANCE
    return AnalyticalFunction.CONTEXT


def normalise_semantic_map(
    semantic_map: InputSemanticMap | None,
) -> InputSemanticMap | None:
    if semantic_map is None or semantic_map.input_shape != InputShape.EVENT_RECORD:
        return semantic_map

    changed = False
    repeated_entity_ids = _repeated_entity_binding_ids(semantic_map.bindings)
    bindings = []
    for binding in semantic_map.bindings:
        analytical_function = binding.analytical_function
        role = binding.role
        level = binding.level

        if _is_single_participant_side_binding(binding):
            if role in IDENTIFIER_ROLES:
                role = SemanticRole.PARTICIPANT_IDENTIFIER
                level = SemanticLevel.PARTICIPANT
            elif role == SemanticRole.OUTCOME_MEASURE:
                level = SemanticLevel.PARTICIPANT
                if _looks_like_event_result_measure(binding):
                    analytical_function = AnalyticalFunction.OUTCOME
                else:
                    role = SemanticRole.MEASURE
                    analytical_function = AnalyticalFunction.OUTCOME_COMPONENT
            elif role in {
                SemanticRole.PERFORMANCE_MEASURE,
                SemanticRole.MEASURE,
            }:
                level = SemanticLevel.PARTICIPANT
                if analytical_function in {
                    None,
                    AnalyticalFunction.PERFORMANCE,
                    AnalyticalFunction.OUTCOME_COMPONENT,
                }:
                    analytical_function = AnalyticalFunction.OUTCOME_COMPONENT
            elif role == SemanticRole.STATUS:
                level = SemanticLevel.PARTICIPANT

        elif binding.binding_id in repeated_entity_ids:
            if role in IDENTIFIER_ROLES:
                role = SemanticRole.ENTITY_IDENTIFIER
                level = SemanticLevel.ENTITY
            elif role in EVENT_MEASURE_ROLES:
                level = SemanticLevel.ENTITY

        if (
            role == SemanticRole.OUTCOME_MEASURE
            and analytical_function != AnalyticalFunction.OUTCOME
        ):
            analytical_function = AnalyticalFunction.OUTCOME
        elif (
            role in EVENT_MEASURE_ROLES
            and analytical_function is None
        ):
            analytical_function = _default_event_analytical_function(
                binding.model_copy(update={"role": role, "level": level})
            )
        elif (
            role not in EVENT_MEASURE_ROLES
            and analytical_function in MEASURE_ANALYTICAL_FUNCTIONS
        ):
            analytical_function = None

        if (
            analytical_function != binding.analytical_function
            or role != binding.role
            or level != binding.level
        ):
            changed = True
            bindings.append(
                binding.model_copy(
                    update={
                        "analytical_function": analytical_function,
                        "role": role,
                        "level": level,
                    }
                )
            )
        else:
            bindings.append(binding)

    if not changed:
        return semantic_map

    return semantic_map.model_copy(update={"bindings": bindings})


def _field_supports_numeric_measure(field: StructuralField) -> bool:
    if set(field.value_types) & {"integer", "number"}:
        return True

    meaningful_samples = [
        str(value).strip()
        for value in field.sample_values
        if str(value).strip().lower()
        not in {"", "n/a", "na", "nan", "none", "null", "-"}
    ]
    if not meaningful_samples:
        return False

    numeric_samples = [
        value
        for value in meaningful_samples
        if _numeric_value(value) is not None
    ]
    return bool(numeric_samples) and (
        len(numeric_samples) == len(meaningful_samples)
        or len(numeric_samples) >= 2
    )


def _participant_line_prefix(key: str) -> str:
    normalised = normalise_key(key)
    parts = normalised.split("_")
    if len(parts) > 1 and parts[-1] in LINE_RECORD_SUFFIXES:
        return "_".join(parts[:-1])
    return normalised


def _participant_line_items(
    payload: Any,
) -> list[tuple[str, Mapping[str, Any], str]]:
    if not isinstance(payload, Mapping):
        return []

    records: list[tuple[str, Mapping[str, Any], str]] = []
    for key, child in payload.items():
        if not isinstance(child, Mapping):
            continue
        prefix = _participant_line_prefix(str(key))
        if prefix == normalise_key(str(key)):
            continue
        child_keys = {normalise_key(str(child_key)) for child_key in child}
        if "result" not in child_keys:
            continue
        if not (
            child_keys & SCORE_FIELD_NAMES
            or child_keys & NAME_FIELD_NAMES
        ):
            continue
        records.append((prefix, child, str(key)))
    return records


def _external_entity_collections(
    payload: Any,
) -> list[tuple[str, Mapping[str, Any] | list[Any]]]:
    if not isinstance(payload, Mapping):
        return []
    collections: list[tuple[str, Mapping[str, Any] | list[Any]]] = []
    for key, child in payload.items():
        if normalise_key(str(key)) not in ENTITY_CONTAINER_NAMES:
            continue
        if isinstance(child, list) and any(isinstance(item, Mapping) for item in child):
            collections.append((str(key), child))
        elif (
            isinstance(child, Mapping)
            and child
            and all(isinstance(item, Mapping) for item in child.values())
        ):
            collections.append((str(key), child))
    return collections


def _entity_affiliation(
    entity: Mapping[str, Any],
) -> tuple[str | None, str | None]:
    return _first_named_item(entity, AFFILIATION_FIELD_NAMES)


def _normalised_text(value: str) -> str:
    return normalise_key(value).replace("_", "")


def _matching_participant(
    participants: list[EventParticipant],
    affiliation: str,
) -> EventParticipant | None:
    target = _normalised_text(affiliation)
    for participant in participants:
        candidates = {
            _normalised_text(participant.key),
            _normalised_text(participant.name),
        }
        if target in candidates or any(
            target in candidate or candidate in target
            for candidate in candidates
        ):
            return participant
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


def _participant_record_context(
    value: Mapping[str, Any],
    prefix: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    context: dict[str, Any] = {}
    paths: dict[str, str] = {}
    for key, child in value.items():
        if isinstance(child, (Mapping, list)) or child is None:
            continue
        normalised = normalise_key(str(key))
        if (
            normalised not in PARTICIPANT_RECORD_CONTEXT_KEYS
            and not normalised.endswith("_standing")
        ):
            continue
        text = str(child).strip()
        if not text:
            continue
        label = str(key).replace("_", " ")
        context[label] = child
        paths[label] = f"{prefix}.{key}" if prefix else str(key)
    return context, paths


def _segment_sort_key(segment: str) -> tuple[int, int, str] | None:
    normalised = normalise_key(segment)
    if normalised in EVENT_AGGREGATE_LEVEL_TERMS:
        return None
    if normalised in {"ot", "overtime", "extra_time", "extra_period"}:
        return (90, 1, normalised)
    match = re.fullmatch(r"q(?:uarter)?_?(\d+)", normalised)
    if match:
        return (10, int(match.group(1)), normalised)
    match = re.fullmatch(r"h(?:alf)?_?(\d+)", normalised)
    if match:
        return (20, int(match.group(1)), normalised)
    match = re.fullmatch(r"(?:p|period)_?(\d+)", normalised)
    if match:
        return (30, int(match.group(1)), normalised)
    match = re.fullmatch(r"(?:inning|frame)_?(\d+)", normalised)
    if match:
        return (40, int(match.group(1)), normalised)
    if normalised.isdigit():
        return (50, int(normalised), normalised)
    if normalised in EVENT_SEGMENT_LEVEL_TERMS:
        return (80, 0, normalised)
    return None


def _segment_family(segment: str) -> str:
    sort_key = _segment_sort_key(segment)
    if sort_key is None:
        return "unknown"
    return {
        10: "quarter",
        20: "half",
        30: "period",
        40: "inning",
        50: "numeric",
        80: "named_segment",
        90: "extra_period",
    }.get(sort_key[0], "unknown")


def _participant_segment_scores(
    value: Mapping[str, Any],
    prefix: str,
) -> dict[str, tuple[float, str]]:
    scores: dict[str, tuple[float, str]] = {}

    def visit(current: Any, path: str, depth: int) -> None:
        if depth > 5 or not isinstance(current, Mapping):
            return
        for key, child in current.items():
            child_path = f"{path}.{key}" if path else str(key)
            segment_key = str(key)
            if isinstance(child, Mapping) and _segment_sort_key(segment_key) is not None:
                score_leaf = _score_leaf(child, child_path)
                if score_leaf is not None:
                    scores[segment_key] = (score_leaf.value, score_leaf.path)
                continue
            if isinstance(child, Mapping):
                visit(child, child_path, depth + 1)

    visit(value, prefix, 0)
    return scores


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
    participants: list[EventParticipant] = []

    if located is not None:
        container_path, container = located
        participant_items = [
            (str(key), raw_participant, f"{container_path}.{key}")
            for key, raw_participant in container.items()
            if isinstance(raw_participant, Mapping)
        ]
    else:
        participant_items = [
            (prefix, raw_participant, source_path)
            for prefix, raw_participant, source_path
            in _participant_line_items(payload)
        ]

    if not participant_items:
        return []

    for key, raw_participant, source_path in participant_items:
        participant_name, identity_paths = _participant_identity(
            str(key), raw_participant, source_path
        )
        score_leaf = _score_leaf(raw_participant, source_path)
        metrics, metric_paths = _team_metric_mapping(raw_participant, source_path)
        record_context, record_context_paths = _participant_record_context(
            raw_participant,
            source_path,
        )
        segment_scores = _participant_segment_scores(
            raw_participant,
            source_path,
        )
        participant = EventParticipant(
            key=str(key),
            name=participant_name,
            source_path=source_path,
            identity_paths=identity_paths,
            score=(score_leaf.value if score_leaf else None),
            score_path=(score_leaf.path if score_leaf else None),
            metrics=metrics,
            metric_paths=metric_paths,
            record_context=record_context,
            record_context_paths=record_context_paths,
            segment_scores=segment_scores,
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

    if located is None and isinstance(payload, Mapping):
        for entity_collection_path, entities in _external_entity_collections(payload):
            for entity_key, raw_entity in _entity_items(entities):
                affiliation, affiliation_path = _entity_affiliation(raw_entity)
                if not affiliation:
                    continue
                participant = _matching_participant(
                    participants,
                    affiliation,
                )
                if participant is None:
                    continue

                entity_path = f"{entity_collection_path}.{entity_key}"
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
                            f"{entity_path}.{raw_metric}"
                        )

                if not entity_metrics:
                    continue

                entity_name, entity_name_path = _first_named_item(
                    raw_entity,
                    NAME_FIELD_NAMES,
                    entity_path,
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
                                        [affiliation_path]
                                        if affiliation_path
                                        else []
                                    ),
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


def _sequence_container_name(key: str) -> bool:
    normalised = normalise_key(key)
    return any(term in normalised.split("_") for term in SEQUENCE_CONTAINER_TERMS)


def _sequence_score_key(key: str) -> bool:
    normalised = normalise_key(key)
    return (
        normalised in SEQUENCE_SCORE_KEYS
        or normalised.endswith("_score")
        or normalised.endswith("_points")
        or normalised.endswith("_total")
        or normalised.endswith("_runs")
    )


def _sequence_signal_count(item: Mapping[str, Any]) -> int:
    signals = 0
    for key, value in item.items():
        if isinstance(value, (Mapping, list)):
            continue
        normalised = normalise_key(str(key))
        if normalised in SEQUENCE_ORDER_KEYS:
            signals += 1
        if normalised in SEQUENCE_ACTION_KEYS:
            signals += 1
        if normalised in SEQUENCE_PARTICIPANT_KEYS:
            signals += 1
        if _sequence_score_key(normalised):
            signals += 1
    return signals


def _sequence_field_values(
    item: Mapping[str, Any],
    *,
    path: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    order_values: dict[str, Any] = {}
    action_values: dict[str, Any] = {}
    participant_values: dict[str, Any] = {}
    score_values: dict[str, Any] = {}

    for key, value in item.items():
        if isinstance(value, Mapping) or value is None:
            continue
        if isinstance(value, list) and any(
            isinstance(child, (Mapping, list))
            for child in value
        ):
            continue
        normalised = normalise_key(str(key))
        source_path = f"{path}.{key}" if path else str(key)
        labelled_value = {
            "label": str(key),
            "value": value,
            "source_path": source_path,
        }
        if normalised in SEQUENCE_ORDER_KEYS:
            order_values[str(key)] = labelled_value
        if normalised in SEQUENCE_ACTION_KEYS:
            action_values[str(key)] = labelled_value
        if normalised in SEQUENCE_PARTICIPANT_KEYS:
            participant_values[str(key)] = labelled_value
        if _sequence_score_key(normalised):
            score_values[str(key)] = labelled_value

    return order_values, action_values, participant_values, score_values


def _sequence_record(
    item: Mapping[str, Any],
    *,
    path: str,
    inherited_order: dict[str, Any] | None = None,
    inherited_participants: dict[str, Any] | None = None,
) -> EventSequenceRecord | None:
    order_values, action_values, participant_values, score_values = (
        _sequence_field_values(item, path=path)
    )
    order_values = {**(inherited_order or {}), **order_values}
    participant_values = {
        **(inherited_participants or {}),
        **participant_values,
    }

    if not (action_values or score_values):
        return None

    return EventSequenceRecord(
        source_path=path,
        order_values=order_values,
        action_values=action_values,
        participant_values=participant_values,
        score_values=score_values,
    )


def _event_sequence_records(payload: Any) -> list[EventSequenceRecord]:
    records: list[EventSequenceRecord] = []

    def visit(current: Any, path: str, depth: int) -> None:
        if depth > 5:
            return
        if isinstance(current, Mapping):
            for key, child in current.items():
                child_path = f"{path}.{key}" if path else str(key)
                if isinstance(child, list):
                    visit_list(str(key), child, child_path, depth + 1)
                elif isinstance(child, Mapping):
                    visit(child, child_path, depth + 1)
            return
        if isinstance(current, list):
            visit_list(path.rsplit(".", 1)[-1], current, path, depth + 1)

    def visit_list(key: str, items: list[Any], path: str, depth: int) -> None:
        mapping_items = [
            (index, item)
            for index, item in enumerate(items)
            if isinstance(item, Mapping)
        ]
        if len(mapping_items) < 2:
            for index, item in mapping_items:
                visit(item, f"{path}[{index}]", depth + 1)
            return

        sequence_like = _sequence_container_name(key) or any(
            _sequence_signal_count(item) >= 2
            for _, item in mapping_items[:5]
        )
        if not sequence_like:
            for index, item in mapping_items:
                visit(item, f"{path}[{index}]", depth + 1)
            return

        for index, item in mapping_items:
            item_path = f"{path}[{index}]"
            parent_order, _, parent_participants, _ = _sequence_field_values(
                item,
                path=item_path,
            )
            record = _sequence_record(item, path=item_path)
            if record is not None:
                records.append(record)

            for child_key, child in item.items():
                if not isinstance(child, list):
                    continue
                child_mappings = [
                    (child_index, child_item)
                    for child_index, child_item in enumerate(child)
                    if isinstance(child_item, Mapping)
                ]
                if not child_mappings:
                    continue
                segment_value = {
                    "label": "segment",
                    "value": child_key,
                    "source_path": f"{item_path}.{child_key}",
                }
                inherited_order = {
                    **parent_order,
                    f"{child_key} segment": segment_value,
                }
                for child_index, child_item in child_mappings:
                    child_path = f"{item_path}.{child_key}[{child_index}]"
                    nested_record = _sequence_record(
                        child_item,
                        path=child_path,
                        inherited_order=inherited_order,
                        inherited_participants=parent_participants,
                    )
                    if nested_record is not None:
                        records.append(nested_record)

    visit(payload, "", 0)
    return records


def _clean_sequence_scalar(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        cleaned_items = [
            item
            for item in (
                _clean_sequence_scalar(child)
                for child in value
            )
            if item
        ]
        return ", ".join(cleaned_items) if cleaned_items else None
    text = str(value).strip()
    if not text or text.upper() in {"N/A", "NA", "NONE", "NULL"}:
        return None
    return text


def _sequence_value_number(labelled_value: Any) -> float | None:
    if not isinstance(labelled_value, Mapping):
        return None
    return _numeric_value(labelled_value.get("value"))


def _side_key_from_text(text: str) -> str | None:
    tokens = [
        token
        for token in normalise_key(text).split("_")
        if token
    ]
    for token in tokens[:4]:
        side = PARTICIPANT_SIDE_ALIASES.get(token)
        if side is not None:
            return side
    return None


def _participant_name_for_side(
    payload: Any,
    side: str,
) -> str:
    side_aliases = {
        alias
        for alias, canonical in PARTICIPANT_SIDE_ALIASES.items()
        if canonical == side
    } | {side}
    name_terms = {"name", "team", "participant", "side", "label"}
    candidates: list[tuple[int, str]] = []

    def visit(current: Any, path: str, depth: int) -> None:
        if depth > 3 or not isinstance(current, Mapping):
            return
        for key, value in current.items():
            key_tokens = set(normalise_key(str(key)).split("_"))
            path_tokens = set(normalise_key(path).split("_"))
            side_match = bool((key_tokens | path_tokens) & side_aliases)
            if isinstance(value, str):
                value_text = _clean_sequence_scalar(value)
                if not value_text:
                    continue
                if side_match and key_tokens & name_terms:
                    candidates.append((3, value_text))
                elif side_match:
                    candidates.append((1, value_text))
            elif isinstance(value, Mapping):
                child_path = f"{path}.{key}" if path else str(key)
                visit(value, child_path, depth + 1)

    visit(payload, "", 0)
    if candidates:
        return sorted(candidates, reverse=True)[0][1]
    return side.title()


def _sequence_order_text(record: EventSequenceRecord) -> str | None:
    parts = []
    for labelled_value in record.order_values.values():
        if not isinstance(labelled_value, Mapping):
            continue
        label = str(labelled_value.get("label") or "").replace("_", " ")
        value = _clean_sequence_scalar(labelled_value.get("value"))
        if label and value:
            parts.append(f"{label} {value}")
    return ", ".join(dict.fromkeys(parts)) or None


def _sequence_action_text(record: EventSequenceRecord) -> str | None:
    preferred = []
    for labelled_value in record.action_values.values():
        if not isinstance(labelled_value, Mapping):
            continue
        value = _clean_sequence_scalar(labelled_value.get("value"))
        if value:
            preferred.append(value)
    return "; ".join(dict.fromkeys(preferred)) or None


def _sequence_actor_text(record: EventSequenceRecord) -> str | None:
    primary_actors = []
    secondary_actors = []
    primary_terms = {
        "actor",
        "batter",
        "competitor",
        "entity",
        "participant",
        "performer",
        "player",
        "subject",
        "team",
        "team_name",
    }
    secondary_terms = {
        "pitcher",
        "scorer",
        "scorers",
    }
    for labelled_value in record.participant_values.values():
        if not isinstance(labelled_value, Mapping):
            continue
        label = normalise_key(str(labelled_value.get("label") or ""))
        value = _clean_sequence_scalar(labelled_value.get("value"))
        if not value:
            continue
        if label in primary_terms:
            primary_actors.append(value)
        elif label in secondary_terms:
            secondary_actors.append(value)
    actors = primary_actors or secondary_actors
    return ", ".join(dict.fromkeys(actors)) or None


def _sequence_score_state(
    record: EventSequenceRecord,
    payload: Any,
) -> dict[str, Any] | None:
    side_values: dict[str, float] = {}
    source_paths: list[str] = []
    for labelled_value in record.score_values.values():
        if not isinstance(labelled_value, Mapping):
            continue
        side = _side_key_from_text(
            " ".join(
                str(labelled_value.get(part) or "")
                for part in ["label", "source_path"]
            )
        )
        if side is None:
            continue
        number = _sequence_value_number(labelled_value)
        if number is None:
            continue
        side_values[side] = number
        source_path = labelled_value.get("source_path")
        if source_path:
            source_paths.append(str(source_path))

    if len(side_values) < 2:
        return None
    sides = list(side_values)[:2]
    left, right = sides[0], sides[1]
    return {
        "left_side": left,
        "right_side": right,
        "left_name": _participant_name_for_side(payload, left),
        "right_name": _participant_name_for_side(payload, right),
        "left_value": side_values[left],
        "right_value": side_values[right],
        "source_paths": source_paths,
    }


def _sequence_score_delta(record: EventSequenceRecord) -> float | None:
    for labelled_value in record.score_values.values():
        if not isinstance(labelled_value, Mapping):
            continue
        text = " ".join(
            str(labelled_value.get(part) or "")
            for part in ["label", "source_path"]
        )
        if _side_key_from_text(text) is not None:
            continue
        number = _sequence_value_number(labelled_value)
        if number is not None and number > 0:
            return number
    return None


def _event_sequence_highlights(
    records: list[EventSequenceRecord],
    payload: Any,
) -> list[dict[str, Any]]:
    highlights: list[dict[str, Any]] = []
    for record in records:
        score_state = _sequence_score_state(record, payload)
        score_delta = _sequence_score_delta(record)
        if score_state is None or score_delta is None:
            continue

        left_value = float(score_state["left_value"])
        right_value = float(score_state["right_value"])
        if left_value == right_value:
            score_phrase = (
                f"the score was level at {left_value:g}-{right_value:g}"
            )
        else:
            leader = (
                score_state["left_name"]
                if left_value > right_value
                else score_state["right_name"]
            )
            score_phrase = (
                f"{leader} led {max(left_value, right_value):g}-"
                f"{min(left_value, right_value):g}"
            )

        action = _sequence_action_text(record)
        actor = _sequence_actor_text(record)
        order_text = _sequence_order_text(record)
        if action and actor:
            event_text = f"{actor} recorded {action}"
        elif action:
            event_text = f"the recorded action was {action}"
        elif actor:
            event_text = f"{actor} was recorded"
        else:
            event_text = "a score-changing step was recorded"
        if order_text:
            event_text = f"{order_text}: {event_text}"

        source_paths = [
            record.source_path,
            *score_state.get("source_paths", []),
            *[
                str(value.get("source_path"))
                for value in [
                    *record.action_values.values(),
                    *record.participant_values.values(),
                ]
                if isinstance(value, Mapping)
                and value.get("source_path")
            ],
        ]
        highlights.append(
            {
                "order": len(highlights) + 1,
                "event_text": event_text,
                "score_phrase": score_phrase,
                "score_delta": score_delta,
                "left_name": score_state["left_name"],
                "right_name": score_state["right_name"],
                "left_value": left_value,
                "right_value": right_value,
                "source_path": record.source_path,
                "source_paths": list(dict.fromkeys(source_paths)),
            }
        )

    if not highlights:
        return highlights

    def leader_after(highlight: dict[str, Any]) -> str | None:
        left_value = float(highlight["left_value"])
        right_value = float(highlight["right_value"])
        if left_value == right_value:
            return None
        return (
            str(highlight["left_name"])
            if left_value > right_value
            else str(highlight["right_name"])
        )

    largest_delta = max(float(item["score_delta"]) for item in highlights)
    previous_leader: str | None = None
    previous_margin: float | None = None
    total_highlights = len(highlights)
    for index, highlight in enumerate(highlights):
        roles: list[str] = []
        current_leader = leader_after(highlight)
        current_margin = abs(
            float(highlight["left_value"]) - float(highlight["right_value"])
        )

        if current_leader is None:
            roles.append("tie")
        elif previous_leader is None and index == 0:
            roles.append("opening_score")
        elif previous_leader is not None and previous_leader != current_leader:
            roles.append("lead_change")
        elif previous_leader is None and index > 0:
            roles.append("tie_broken")

        if float(highlight["score_delta"]) == largest_delta:
            roles.append("largest_score_change")

        sequence_position = (index + 1) / total_highlights
        if sequence_position >= 0.75:
            roles.append("late_score_change")
        if index == total_highlights - 1:
            roles.append("final_score_change")
            if (
                previous_margin is not None
                and current_margin < previous_margin
            ):
                roles.append("late_narrowing")

        highlight["leader_after"] = current_leader
        highlight["margin_after"] = current_margin
        highlight["sequence_position"] = sequence_position
        highlight["sequence_roles"] = roles

        previous_leader = current_leader
        previous_margin = current_margin

    return highlights


def _event_sequence_evidence(payload: Any) -> list[CapabilityEvidence]:
    records = _event_sequence_records(payload)
    if len(records) < 2:
        return []

    action_count = sum(bool(record.action_values) for record in records)
    score_count = sum(bool(record.score_values) for record in records)
    participant_count = sum(bool(record.participant_values) for record in records)
    if not (action_count or score_count):
        return []

    source_roots = list(
        dict.fromkeys(
            record.source_path.split("[", 1)[0]
            for record in records
            if record.source_path
        )
    )
    available_parts = []
    if action_count:
        available_parts.append("action labels")
    if participant_count:
        available_parts.append("participant roles")
    if score_count:
        available_parts.append("score-state fields")

    evidence = [
        CapabilityEvidence(
            capability=EvidenceCapability.EVENT_OUTCOME,
            evidence_type="event_sequence",
            finding=(
                "The supplied event structure includes an ordered event "
                f"sequence with {len(records)} recorded steps"
                + (
                    f" across {', '.join(source_roots[:3])}"
                    if source_roots
                    else ""
                )
                + (
                    f", including {', '.join(available_parts)}."
                    if available_parts
                    else "."
                )
            ),
            metrics={
                "step_count": len(records),
                "action_step_count": action_count,
                "participant_step_count": participant_count,
                "score_state_step_count": score_count,
                "source_roots": source_roots,
            },
            source_paths=[
                path
                for record in records[:12]
                for path in [record.source_path]
                if path
            ],
            entity_scope=[],
            practical_interpretation=(
                "This permits bounded descriptions of recorded event order "
                "and score-state availability without inferring causes."
            ),
            strength_label="event_sequence",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.75,
            salience=0.65,
            recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            semantic_level=SemanticLevel.EVENT,
            limitations=[
                "Sequence evidence supports the supplied recorded order only; "
                "it does not by itself establish momentum, tactics or causes."
            ],
            prohibited_interpretations=[
                "Do not infer a comeback, turning point, dominance or causal "
                "game mechanism unless directly supported."
            ],
        )
    ]
    highlights = _event_sequence_highlights(records, payload)
    if highlights:
        retained = highlights[:6]
        highlight_text = "; ".join(
            f"{item['event_text']}, after which {item['score_phrase']}"
            for item in retained
        )
        if len(highlights) > len(retained):
            highlight_text += (
                f"; {len(highlights) - len(retained)} later score-changing "
                "steps are omitted from this compact evidence item"
            )
        evidence.append(
            CapabilityEvidence(
                capability=EvidenceCapability.EVENT_OUTCOME,
                evidence_type="event_sequence",
                finding=(
                    "The recorded score-changing sequence includes: "
                    + highlight_text
                    + "."
                ),
                metrics={
                    "sequence_type": "score_changing_sequence",
                    "highlight_count": len(highlights),
                    "summary_highlight_count": len(retained),
                    "highlights": highlights,
                    "summary_highlights": retained,
                    "omitted_highlight_count": max(
                        0,
                        len(highlights) - len(retained),
                    ),
                },
                source_paths=list(
                    dict.fromkeys(
                        path
                        for item in highlights
                        for path in item.get("source_paths", [])
                        if path
                    )
                ),
                entity_scope=list(
                    dict.fromkeys(
                        name
                        for item in highlights
                        for name in [
                            item.get("left_name"),
                            item.get("right_name"),
                        ]
                        if name
                    )
                ),
                practical_interpretation=(
                    "This supports a bounded recap of recorded score-changing "
                    "steps and score states, without assigning causes."
                ),
                strength_label="event_sequence_highlight",
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.COMPARATIVE,
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.95,
                salience=0.92,
                recommended_use=RecommendedUse.MAIN_FINDING,
                semantic_level=SemanticLevel.EVENT,
                limitations=[
                    "Sequence highlights describe recorded score-changing "
                    "steps only and do not establish causality or momentum."
                ],
                prohibited_interpretations=[
                    "Do not call a score-changing step a turning point, comeback "
                    "or cause unless explicitly supported by the source."
                ],
            )
        )

    return evidence


def _participant_record_context_finding(
    participants: list[EventParticipant],
) -> str:
    clauses: list[str] = []
    for participant in participants:
        if not participant.record_context:
            continue
        wins_key = next(
            (
                key
                for key in participant.record_context
                if normalise_key(key) == "wins"
            ),
            None,
        )
        losses_key = next(
            (
                key
                for key in participant.record_context
                if normalise_key(key) == "losses"
            ),
            None,
        )
        if wins_key and losses_key:
            clauses.append(
                f"{participant.name} entered with "
                f"{participant.record_context[wins_key]} wins and "
                f"{participant.record_context[losses_key]} losses"
            )
            continue
        values = [
            f"{label} {value}"
            for label, value in list(participant.record_context.items())[:3]
        ]
        if values:
            clauses.append(f"{participant.name} had " + ", ".join(values))

    return (
        "Participant context records "
        + "; ".join(clauses)
        + "."
    )


def _participant_record_context_evidence(
    participants: list[EventParticipant],
) -> list[CapabilityEvidence]:
    participants_with_context = [
        participant
        for participant in participants
        if participant.record_context
    ]
    if len(participants_with_context) < 2:
        return []

    values = [
        {
            "participant": participant.name,
            "values": participant.record_context,
            "source_paths": list(participant.record_context_paths.values()),
        }
        for participant in participants_with_context
    ]
    return [
        CapabilityEvidence(
            capability=EvidenceCapability.EVENT_OUTCOME,
            evidence_type="participant_record_context",
            finding=_participant_record_context_finding(
                participants_with_context
            ),
            metrics={"values": values},
            source_paths=list(
                dict.fromkeys(
                    path
                    for participant in participants_with_context
                    for path in participant.record_context_paths.values()
                )
            ),
            entity_scope=[participant.name for participant in participants_with_context],
            practical_interpretation=(
                "This supplies participant-level record or standing context "
                "without using it as causal evidence."
            ),
            strength_label="participant_record_context",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.80,
            salience=0.82,
            recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            semantic_level=SemanticLevel.PARTICIPANT,
            prohibited_interpretations=[
                "Do not infer motivation, upset status or historical "
                "significance from participant records alone."
            ],
        )
    ]


def _preferred_score_segment_family(
    participants: list[EventParticipant],
) -> str | None:
    family_counts: dict[str, set[str]] = {}
    for participant in participants:
        for segment in participant.segment_scores:
            family = _segment_family(segment)
            if family == "extra_period":
                continue
            family_counts.setdefault(family, set()).add(segment)
    eligible = {
        family: segments
        for family, segments in family_counts.items()
        if family != "unknown" and len(segments) >= 2
    }
    if not eligible:
        return None
    family_priority = {
        "quarter": 0,
        "period": 1,
        "inning": 2,
        "numeric": 3,
        "half": 4,
        "named_segment": 5,
    }
    return min(
        eligible,
        key=lambda family: family_priority.get(family, 99),
    )


def _score_progression_evidence(
    participants: list[EventParticipant],
) -> list[CapabilityEvidence]:
    if len(participants) < 2:
        return []
    family = _preferred_score_segment_family(participants)
    if family is None:
        return []

    segment_names = sorted(
        {
            segment
            for participant in participants
            for segment in participant.segment_scores
            if _segment_family(segment) == family
        },
        key=lambda segment: _segment_sort_key(segment) or (99, 99, segment),
    )
    cumulative: dict[str, float] = {
        participant.name: 0.0
        for participant in participants
    }
    progression: list[dict[str, Any]] = []
    source_paths: list[str] = []
    for segment in segment_names:
        segment_values: dict[str, float] = {}
        segment_paths: list[str] = []
        for participant in participants:
            if segment not in participant.segment_scores:
                continue
            value, path = participant.segment_scores[segment]
            segment_values[participant.name] = value
            segment_paths.append(path)
        if len(segment_values) < 2:
            continue
        if all(value == 0 for value in segment_values.values()):
            continue
        for participant_name, value in segment_values.items():
            cumulative[participant_name] = cumulative.get(participant_name, 0.0) + value
        ordered_cumulative = sorted(
            cumulative.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        leader = ordered_cumulative[0][0]
        tied = (
            len(ordered_cumulative) > 1
            and ordered_cumulative[0][1] == ordered_cumulative[1][1]
        )
        progression.append(
            {
                "segment": segment,
                "segment_values": segment_values,
                "cumulative_values": dict(cumulative),
                "leader": None if tied else leader,
                "tied": tied,
                "source_paths": segment_paths,
            }
        )
        source_paths.extend(segment_paths)

    if len(progression) < 2:
        return []

    highlight_parts: list[str] = []
    for item in progression[:4]:
        ordered_scores = sorted(
            item["cumulative_values"].items(),
            key=lambda score_item: score_item[1],
            reverse=True,
        )
        score_text = "-".join(f"{value:g}" for _, value in ordered_scores[:2])
        if item["tied"]:
            highlight_parts.append(
                f"after {item['segment']}, the cumulative score was level at {score_text}"
            )
        else:
            highlight_parts.append(
                f"after {item['segment']}, {item['leader']} led {score_text}"
            )

    return [
        CapabilityEvidence(
            capability=EvidenceCapability.EVENT_OUTCOME,
            evidence_type="score_progression",
            finding=(
                "The supplied score progression records "
                + "; ".join(highlight_parts)
                + "."
            ),
            metrics={
                "segment_family": family,
                "segments": progression,
            },
            source_paths=list(dict.fromkeys(source_paths)),
            entity_scope=[participant.name for participant in participants],
            practical_interpretation=(
                "This supports bounded narration of recorded score progression "
                "without inferring momentum or causes."
            ),
            strength_label="score_progression",
            claim_permissions=[
                ClaimPermission.DESCRIPTIVE,
                ClaimPermission.COMPARATIVE,
            ],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.88,
            salience=0.88,
            recommended_use=RecommendedUse.MAIN_FINDING,
            semantic_level=SemanticLevel.EVENT,
            limitations=[
                "Score progression describes supplied segment scores only and "
                "does not establish why the result occurred."
            ],
            prohibited_interpretations=[
                "Do not infer momentum, a turning point or a comeback unless "
                "a recorded event sequence directly supports it."
            ],
        )
    ]


def available_capabilities(
    bundle: Any,
    semantic_map: InputSemanticMap | None = None,
) -> list[EvidenceCapability]:
    shape = getattr(getattr(bundle, "input_structure", None), "shape", None)
    capabilities = [EvidenceCapability.DATASET_PROFILE]

    tables = getattr(bundle, "tables", {})
    if any(
        (
            {"attribute_name", "attribute_value"}.issubset(
                set(getattr(frame, "columns", []))
            )
            or {"subject", "relation", "object"}.issubset(
                set(getattr(frame, "columns", []))
            )
        )
        for frame in tables.values()
    ) or _bundle_contains_serialized_triples(bundle):
        capabilities.append(EvidenceCapability.STRUCTURED_RECORD_VERBALISATION)

    if any(
        "is_highlighted" in getattr(frame, "columns", [])
        and bool(frame["is_highlighted"].fillna(False).any())
        for frame in tables.values()
    ):
        capabilities.append(EvidenceCapability.FOCUSED_TABLE_REGION)

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
    evidence: list[CapabilityEvidence] = [
        *_event_context_evidence(payload),
        *_event_sequence_evidence(payload),
    ]
    if len(participants) < 2:
        return evidence

    evidence.extend(
        [
            *_participant_record_context_evidence(participants),
            *_score_progression_evidence(participants),
        ]
    )

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
    entity_metrics = sorted(
        {
            metric
            for entity in all_entities
            for metric in entity.metrics
        },
        key=_metric_priority,
        reverse=True,
    )
    for metric in entity_metrics[:8]:
        ranked = sorted(
            [entity for entity in all_entities if metric in entity.metrics],
            key=lambda entity: entity.metrics[metric],
            reverse=True,
        )
        if not ranked:
            continue
        if ranked[0].metrics[metric] > 0:
            ranked = [
                entity
                for entity in ranked
                if entity.metrics[metric] > 0
            ]
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
                    if metric == entity_metrics[0]
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

    primary_entity_metric = entity_metrics[0] if entity_metrics else None
    if all_entities and primary_entity_metric:
        top_entity = max(
            [
                entity
                for entity in all_entities
                if primary_entity_metric in entity.metrics
            ],
            key=lambda entity: entity.metrics.get(primary_entity_metric, float("-inf")),
        )
        visible_metrics = [
            metric
            for metric in dict.fromkeys(
                [
                    primary_entity_metric,
                    *entity_metrics,
                ]
            )
            if metric in top_entity.metrics
            and (
                top_entity.metrics[metric] > 0
                or metric == primary_entity_metric
            )
        ][:4]
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
    *,
    require_entity_measure_coverage: bool = False,
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

    if require_entity_measure_coverage:
        entity_measure_groups: dict[tuple[str, str], set[str]] = {}
        for binding in semantic_map.bindings:
            if binding.role != SemanticRole.ENTITY_IDENTIFIER:
                continue
            parent_path = binding.path_pattern.rsplit(".", 1)[0]
            key = (binding.table_name, parent_path)
            entity_measure_groups.setdefault(key, set())

        for key in entity_measure_groups:
            table_name, parent_path = key
            entity_measure_groups[key] = {
                field.path_pattern
                for field in structural_catalog
                if field.table_name == table_name
                and field.path_pattern.rsplit(".", 1)[0] == parent_path
                and _field_supports_numeric_measure(field)
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
    semantic_map = normalise_semantic_map(semantic_map)
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
    semantic_map = normalise_semantic_map(semantic_map)
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
            if (
                query.evidence_type not in PARALLEL_PARTICIPANT_COMPARISON_TYPES
                and len(query.value_binding_ids) != 1
            ):
                errors.append(
                    f"Evidence query {query.query_id} must use exactly one measure binding."
                )
            if query.evidence_type in PARALLEL_PARTICIPANT_COMPARISON_TYPES:
                if not query.value_binding_ids:
                    errors.append(
                        f"Evidence query {query.query_id} must use at least one measure binding."
                    )
                elif len(query.value_binding_ids) > 1 and not (
                    query.operation == EvidenceOperation.COMPARE
                    and _allows_parallel_participant_value_bindings(
                        evidence_type=query.evidence_type,
                        value_bindings=value_bindings,
                    )
                ):
                    errors.append(
                        f"Evidence query {query.query_id} can only use "
                        "multiple measure bindings when they are aligned "
                        "side-specific participant values from the same "
                        "measure family."
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
                if field is not None and not _field_supports_numeric_measure(field):
                    errors.append(
                        f"Evidence query {query.query_id} uses non-numeric "
                        f"measure binding {binding_id}."
                    )

    return errors


def _aligned_label_match(
    match: PathMatch,
    label_matches: list[PathMatch],
) -> PathMatch | None:
    compatible = [
        candidate
        for candidate in label_matches
        if candidate.captures == match.captures[: len(candidate.captures)]
    ]
    if not compatible:
        return None
    return max(compatible, key=lambda item: len(item.captures))


def _aligned_label(
    match: PathMatch,
    label_matches: list[PathMatch],
) -> tuple[str | None, str | None]:
    selected = _aligned_label_match(match, label_matches)
    if selected is None:
        return None, None
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

    semantic_map = normalise_semantic_map(semantic_map) or semantic_map
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
            value_binding_ids = query.value_binding_ids
            value_bindings_for_query = [
                binding_lookup[binding_id]
                for binding_id in value_binding_ids
                if binding_id in binding_lookup
            ]
            participant_identifiers = [
                binding
                for binding in binding_lookup.values()
                if binding.role == SemanticRole.PARTICIPANT_IDENTIFIER
                and binding.level == SemanticLevel.PARTICIPANT
            ]
            side_specific_values = _allows_parallel_participant_value_bindings(
                evidence_type=query.evidence_type,
                value_bindings=value_bindings_for_query,
            )
            entity_matches_by_binding: dict[str, list[PathMatch]] = {}
            if side_specific_values:
                participant_binding_ids = [
                    binding.binding_id
                    for binding in participant_identifiers
                ]
                entity_matches_by_binding = {
                    binding_id: matches_for(binding_id)
                    for binding_id in participant_binding_ids
                }
            else:
                entity_matches_by_binding = {
                    query.entity_binding_id or "": matches_for(
                        query.entity_binding_id or ""
                    )
                }
            group_matches = (
                matches_for(query.group_binding_id)
                if query.group_binding_id
                else []
            )
            context_matches = {
                binding_id: matches_for(binding_id)
                for binding_id in query.context_binding_ids
            }
            records: list[dict[str, Any]] = []
            extra_binding_ids: list[str] = []

            for value_binding_id in value_binding_ids:
                current_value_binding = binding_lookup[value_binding_id]
                value_matches = [
                    match
                    for match in matches_for(value_binding_id)
                    if _numeric_value(match.value) is not None
                ]
                current_entity_binding = (
                    _participant_identifier_for_measure(
                        current_value_binding,
                        participant_identifiers,
                    )
                    if side_specific_values
                    else binding_lookup.get(query.entity_binding_id or "")
                )
                current_entity_matches = (
                    entity_matches_by_binding.get(
                        current_entity_binding.binding_id,
                        [],
                    )
                    if current_entity_binding is not None
                    else []
                )
                if current_entity_binding is not None:
                    extra_binding_ids.append(current_entity_binding.binding_id)

                for value_match in value_matches:
                    entity, entity_path = _aligned_label(
                        value_match,
                        current_entity_matches,
                    )
                    if entity is None:
                        continue
                    group_match = _aligned_label_match(
                        value_match,
                        group_matches,
                    )
                    if (
                        group_match is not None
                        and value_match.captures
                        and not group_match.captures
                    ):
                        group_match = None
                    group = (
                        str(group_match.value)
                        if group_match is not None
                        else None
                    )
                    group_path = (
                        group_match.source_path
                        if group_match is not None
                        else None
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
                        "measure": current_value_binding.label,
                        "context": context,
                        "source_path": value_match.source_path,
                    }
                    records.append(record)
                    entity_scope.extend(
                        value
                        for value in [entity, group, *context.values()]
                        if value
                    )
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
                if (
                    query.descending
                    and ordered
                    and ordered[0]["value"] <= 0
                    and query_function
                    in {
                        AnalyticalFunction.OUTCOME_COMPONENT,
                        AnalyticalFunction.PERFORMANCE,
                    }
                ):
                    continue
                ranking_source = ordered
                if (
                    query.descending
                    and ordered
                    and ordered[0]["value"] > 0
                ):
                    ranking_source = [
                        record
                        for record in ordered
                        if record["value"] > 0
                    ]
                selected_records = ranking_source[: query.limit]
                value_counts = {
                    record["value"]: sum(
                        candidate["value"] == record["value"]
                        for candidate in ranking_source
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
                comparable_records, level_filter = _comparable_event_records(
                    ordered
                )
                metrics["records"] = comparable_records
                if level_filter is not None:
                    metrics["record_level_filter"] = level_filter
                    metrics["unfiltered_record_count"] = len(ordered)
                    source_paths = [
                        str(record["source_path"])
                        for record in comparable_records
                        if record.get("source_path")
                    ]
                    entity_scope = [
                        value
                        for record in comparable_records
                        for value in [
                            record.get("entity"),
                            record.get("group"),
                            *record.get("context", {}).values(),
                        ]
                        if value
                    ]
                if len(comparable_records) >= 2:
                    metrics["difference"] = abs(
                        comparable_records[0]["value"]
                        - comparable_records[-1]["value"]
                    )
                    metrics["tied"] = (
                        comparable_records[0]["value"]
                        == comparable_records[-1]["value"]
                    )
                binding_ids = list(dict.fromkeys([*binding_ids, *extra_binding_ids]))

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
