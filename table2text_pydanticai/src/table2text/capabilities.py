from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .schemas import (
    CapabilityDefinition,
    ClaimPermission,
    EvidenceCapability,
    InputShape,
    RecommendedUse,
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


def available_capabilities(bundle: Any) -> list[EvidenceCapability]:
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
