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
    "team_runs",
    "total",
}
PARTICIPANT_LINE_SUFFIXES = {
    "line",
    "record",
    "summary",
}
PARTICIPANT_LINE_METRIC_NAMES = {
    "final_score",
    "points",
    "pts",
    "score",
    "team_runs",
    "team_points",
    "total",
}


def normalise_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def _looks_numeric(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        return bool(
            re.fullmatch(
                r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)",
                value.strip().replace(",", ""),
            )
        )
    return False


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
            if key_name in OUTCOME_FIELD_NAMES and _looks_numeric(child):
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


def _participant_line_records(payload: Any) -> list[tuple[str, Mapping[str, Any]]]:
    if not isinstance(payload, Mapping):
        return []

    records: list[tuple[str, Mapping[str, Any]]] = []
    for key, child in payload.items():
        if not isinstance(child, Mapping):
            continue
        normalised_key = normalise_key(str(key))
        key_parts = normalised_key.split("_")
        if len(key_parts) < 2 or key_parts[-1] not in PARTICIPANT_LINE_SUFFIXES:
            continue
        child_keys = {normalise_key(str(child_key)) for child_key in child}
        has_result = "result" in child_keys
        has_score = bool(child_keys & PARTICIPANT_LINE_METRIC_NAMES)
        has_identity = bool(child_keys & IDENTITY_FIELD_NAMES)
        if has_result and (has_score or has_identity):
            records.append((str(key), child))

    return records


def has_paired_participant_line_records(payload: Any) -> bool:
    records = _participant_line_records(payload)
    if len(records) < 2:
        return False
    prefixes = {
        normalise_key(key).rsplit("_", 1)[0]
        for key, _ in records
        if "_" in normalise_key(key)
    }
    return len(prefixes) >= 2


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

    if has_paired_participant_line_records(payload):
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
    if path.strip() in {"", "$"}:
        return []
    return [part for part in path.split(".") if part]


def get_path(payload: Any, path: str) -> tuple[bool, Any]:
    if path.strip() in {"", "$"}:
        return True, payload
    current = payload
    for part in _path_parts(path):
        if not isinstance(current, Mapping) or part not in current:
            return False, None
        current = current[part]
    return True, current


def set_path(target: dict[str, Any], path: str, value: Any) -> None:
    parts = _path_parts(path)
    if not parts:
        if isinstance(value, Mapping):
            target.clear()
            target.update(copy.deepcopy(dict(value)))
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
        payload.clear()
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
        if any(path.strip() in {"", "$"} for path in policy.operational_input_paths):
            operational = copy.deepcopy(dict(payload))
        else:
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
