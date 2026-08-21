from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .schemas import (
    ColumnProfile,
    DataProfile,
    EvaluationFieldPolicy,
    InputRepresentationStatus,
    InputShape,
    InputStructureProfile,
    TableProfile,
    ZeroRisk,
)
from .structure import combine_structure_profiles, inspect_and_filter_payload


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".json",
    ".jsonl",
    ".ndjson",
    ".parquet",
    ".xlsx",
    ".xls",
}

VALID_ZERO_TERMS = {
    "bearing",
    "direction",
    "angle",
    "degree",
    "degrees",
    "count",
    "number",
    "index",
    "flag",
    "binary",
}

CONTEXT_DEPENDENT_ZERO_TERMS = {
    "visibility",
    "speed",
    "precipitation",
    "rain",
    "snow",
    "distance",
}

POSSIBLE_SENTINEL_ZERO_TERMS = {
    "pressure",
    "blood pressure",
}


@dataclass
class DataBundle:
    tables: dict[str, pd.DataFrame]
    source_paths: list[Path]
    fingerprint: str
    structured_inputs: dict[str, Any] = field(default_factory=dict)
    input_structure: InputStructureProfile | None = None
    evaluation_field_policy: EvaluationFieldPolicy = field(
        default_factory=EvaluationFieldPolicy
    )


def safe_hashable(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, (list, dict, tuple, set)):
        return json.dumps(value, sort_keys=True, default=str)

    try:
        if bool(pd.isna(value)):
            return None
    except Exception:
        pass

    return value


def profile_sample_value(value: Any) -> str:
    if isinstance(value, dict):
        return json.dumps(
            {
                "type": "object",
                "keys": [str(key) for key in list(value)[:20]],
            },
            sort_keys=True,
        )
    if isinstance(value, list):
        return json.dumps(
            {
                "type": "array",
                "length": len(value),
                "item_type": (
                    type(value[0]).__name__ if value else "unknown"
                ),
            },
            sort_keys=True,
        )

    text = str(value)
    return text if len(text) <= 240 else text[:237] + "..."


def fingerprint_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()

    for path in sorted(paths, key=lambda item: str(item.resolve())):
        digest.update(str(path.resolve()).encode("utf-8"))

        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)

    return digest.hexdigest()


def expand_inputs(inputs: Iterable[str | Path]) -> list[Path]:
    paths: list[Path] = []

    for raw_path in inputs:
        path = Path(raw_path).expanduser()

        if path.is_dir():
            paths.extend(
                item
                for item in sorted(path.iterdir())
                if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS
            )
        elif path.is_file():
            paths.append(path)
        else:
            raise FileNotFoundError(f"Input path does not exist: {path}")

    if not paths:
        raise ValueError("No supported input files were found.")

    return paths


def unique_table_name(name: str, tables: dict[str, pd.DataFrame]) -> str:
    candidate = name
    counter = 2

    while candidate in tables:
        candidate = f"{name}_{counter}"
        counter += 1

    return candidate


def _columnar_mapping(payload: dict[str, Any]) -> bool:
    values = list(payload.values())
    if not values or not all(isinstance(value, list) for value in values):
        return False
    lengths = {len(value) for value in values}
    return len(lengths) == 1 and not all(
        not value or isinstance(value[0], dict)
        for value in values
    )


def _highlight_pairs(value: Any) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    if not isinstance(value, list):
        return pairs

    for item in value:
        if (
            isinstance(item, list | tuple)
            and len(item) >= 2
            and isinstance(item[0], int)
            and isinstance(item[1], int)
        ):
            pairs.add((item[0], item[1]))

    return pairs


def _meaning_representation_pairs(value: Any) -> list[list[str]]:
    text = str(value or "")
    pattern = re.compile(r"([A-Za-z0-9 _-]+)\[([^\]]*)\]")
    pairs = [
        [key.strip(), item.strip()]
        for key, item in pattern.findall(text)
        if key.strip() and item.strip()
    ]
    return pairs or ([["meaning_representation", text]] if text.strip() else [])


def _normalise_record_rows(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []

    rows: list[list[str]] = []
    for item in value:
        if isinstance(item, dict):
            subject = item.get("subject") or item.get("head") or item.get("s")
            relation = (
                item.get("relation")
                or item.get("predicate")
                or item.get("property")
                or item.get("r")
            )
            obj = item.get("object") or item.get("tail") or item.get("value") or item.get("o")
            if subject is not None and relation is not None and obj is not None:
                rows.append([str(subject), str(relation), str(obj)])
            else:
                for key, child in item.items():
                    if not isinstance(child, (dict, list)):
                        rows.append([str(key), str(child)])
        elif isinstance(item, list | tuple):
            values = [str(part) for part in item if str(part).strip()]
            if values:
                rows.append(values)
    return rows


def _structured_record_table(payload: dict[str, Any]) -> pd.DataFrame | None:
    if payload.get("__table2text_benchmark_example__"):
        task_family = str(payload.get("task_family") or "")
        if task_family not in {
            "attribute_verbalisation",
            "triple_verbalisation",
        }:
            return None
        source_payload = payload.get("source_payload")
        parent_table = payload.get("parent_table")
        request = payload.get("request")
        source_text = payload.get("source_text")
        output_mode = payload.get("output_mode")
    else:
        task_family = ""
        source_payload = payload
        parent_table = None
        request = None
        source_text = None
        output_mode = None

    rows = _normalise_record_rows(parent_table)
    if not rows and isinstance(source_payload, dict):
        if "meaning_representation" in source_payload:
            rows = _meaning_representation_pairs(
                source_payload.get("meaning_representation")
            )
            task_family = task_family or "attribute_verbalisation"
            source_text = source_text or str(
                source_payload.get("meaning_representation") or ""
            )
        elif "triples" in source_payload:
            rows = _normalise_record_rows(source_payload.get("triples"))
            task_family = task_family or "triple_verbalisation"

    if not rows:
        return None

    records: list[dict[str, Any]] = []
    record_kind = (
        "triple"
        if task_family == "triple_verbalisation"
        or any(len(row) >= 3 for row in rows)
        else "attribute"
    )
    for row_index, row in enumerate(rows):
        if len(row) >= 3:
            subject, relation, obj = row[0], row[1], row[2]
            records.append(
                {
                    "row_index": row_index,
                    "record_kind": "triple",
                    "subject": subject,
                    "relation": relation,
                    "object": obj,
                    "attribute_name": relation,
                    "attribute_value": obj,
                    "task_family": task_family or "triple_verbalisation",
                    "output_mode": output_mode,
                    "request": request,
                    "source_text": source_text,
                }
            )
        elif len(row) >= 2:
            records.append(
                {
                    "row_index": row_index,
                    "record_kind": record_kind,
                    "subject": None,
                    "relation": row[0],
                    "object": row[1],
                    "attribute_name": row[0],
                    "attribute_value": row[1],
                    "task_family": task_family or "attribute_verbalisation",
                    "output_mode": output_mode,
                    "request": request,
                    "source_text": source_text,
                }
            )

    return pd.DataFrame(records) if records else None


def _benchmark_cell_table(payload: dict[str, Any]) -> pd.DataFrame | None:
    benchmark_wrapper = bool(payload.get("__table2text_benchmark_example__"))
    source_payload = payload.get("source_payload") if benchmark_wrapper else payload
    if not isinstance(source_payload, dict):
        return None

    highlighted_source = (
        source_payload.get("highlighted_cells")
        or source_payload.get("highlighted_cell_ids")
    )
    if not highlighted_source:
        return None

    table = source_payload.get("table")
    if not isinstance(table, list):
        table = payload.get("parent_table") if benchmark_wrapper else None

    if not isinstance(table, list):
        return None

    highlighted = _highlight_pairs(highlighted_source)
    page_title = (
        source_payload.get("table_page_title")
        or source_payload.get("page_title")
    )
    section_title = (
        source_payload.get("table_section_title")
        or source_payload.get("table_title")
    )

    records: list[dict[str, Any]] = []
    occupied_columns_by_row: dict[int, set[int]] = {}
    for row_index, table_row in enumerate(table):
        if not isinstance(table_row, list):
            continue
        expanded_column_index = 0
        for raw_column_index, cell in enumerate(table_row):
            occupied_columns = occupied_columns_by_row.get(row_index, set())
            while expanded_column_index in occupied_columns:
                expanded_column_index += 1

            if isinstance(cell, dict):
                value = cell.get("value", "")
                is_header = bool(cell.get("is_header", False))
                row_span = cell.get("row_span")
                column_span = cell.get("column_span")
            else:
                value = cell
                is_header = False
                row_span = None
                column_span = None

            span_width = (
                column_span
                if isinstance(column_span, int) and column_span > 0
                else 1
            )
            span_height = (
                row_span
                if isinstance(row_span, int) and row_span > 0
                else 1
            )
            column_index = expanded_column_index
            column_end_index = expanded_column_index + span_width - 1
            # Benchmark highlighted-cell coordinates are raw table-cell
            # coordinates. Keep span-expanded columns for structural context,
            # but do not let a preceding colspan absorb a later highlighted
            # raw cell in the same row.
            cell_highlighted = (row_index, raw_column_index) in highlighted

            records.append(
                {
                    "page_title": page_title,
                    "section_title": section_title,
                    "row_index": row_index,
                    "raw_column_index": raw_column_index,
                    "column_index": column_index,
                    "column_end_index": column_end_index,
                    "cell_value": value,
                    "is_header": is_header,
                    "is_highlighted": cell_highlighted,
                    "row_span": row_span,
                    "column_span": column_span,
                    "task_family": payload.get("task_family") if benchmark_wrapper else None,
                    "output_mode": payload.get("output_mode") if benchmark_wrapper else None,
                    "request": payload.get("request") if benchmark_wrapper else None,
                    "source_text": payload.get("source_text") if benchmark_wrapper else None,
                }
            )
            expanded_column_index += span_width
            if span_height > 1:
                spanned_columns = set(
                    range(column_index, column_end_index + 1)
                )
                for spanned_row_index in range(
                    row_index + 1,
                    row_index + span_height,
                ):
                    occupied_columns_by_row.setdefault(
                        spanned_row_index,
                        set(),
                    ).update(spanned_columns)

    if not records:
        return None

    return pd.DataFrame(records)


def load_json_tables(
    path: Path,
    payload: Any | None = None,
) -> dict[str, pd.DataFrame]:
    if payload is None:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

    if isinstance(payload, dict):
        structured_record = _structured_record_table(payload)
        if structured_record is not None:
            return {path.stem: structured_record}

        benchmark_table = _benchmark_cell_table(payload)
        if benchmark_table is not None:
            return {path.stem: benchmark_table}

    if isinstance(payload, list):
        return {path.stem: pd.json_normalize(payload)}

    if isinstance(payload, dict):
        nested_tables = {
            str(key): pd.json_normalize(value)
            for key, value in payload.items()
            if isinstance(value, list)
            and (not value or isinstance(value[0], dict))
        }

        if nested_tables and len(nested_tables) == len(payload):
            return nested_tables

        if _columnar_mapping(payload):
            return {path.stem: pd.DataFrame(payload)}

        # A mixed scalar/nested mapping is one structured record. Passing it
        # directly to DataFrame aligns nested keys into artificial rows.
        return {path.stem: pd.DataFrame([payload])}

    return {path.stem: pd.DataFrame({"value": [payload]})}


def load_data(
    inputs: Iterable[str | Path],
    evaluation_field_policy: EvaluationFieldPolicy | None = None,
) -> DataBundle:
    paths = expand_inputs(inputs)
    tables: dict[str, pd.DataFrame] = {}
    structured_inputs: dict[str, Any] = {}
    structure_profiles: list[InputStructureProfile] = []
    effective_policies: list[EvaluationFieldPolicy] = []

    for path in paths:
        extension = path.suffix.lower()

        operational_payload: Any | None = None

        if extension == ".csv":
            loaded = {path.stem: pd.read_csv(path, low_memory=False)}
        elif extension == ".json":
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            (
                operational_payload,
                structure_profile,
                effective_policy,
            ) = inspect_and_filter_payload(
                payload=payload,
                source_path=path,
                field_policy=evaluation_field_policy,
            )
            structure_profiles.append(structure_profile)
            effective_policies.append(effective_policy)
            loaded = load_json_tables(path, operational_payload)
        elif extension in {".jsonl", ".ndjson"}:
            loaded = {path.stem: pd.read_json(path, lines=True)}
        elif extension == ".parquet":
            loaded = {path.stem: pd.read_parquet(path)}
        elif extension in {".xlsx", ".xls"}:
            sheets = pd.read_excel(path, sheet_name=None)
            loaded = {
                f"{path.stem}__{sheet_name}": frame
                for sheet_name, frame in sheets.items()
            }
        else:
            raise ValueError(f"Unsupported format: {path}")

        if extension != ".json":
            structure_profiles.append(
                InputStructureProfile(
                    shape=(
                        InputShape.TIME_SERIES
                        if any(
                            "date" in str(column).casefold()
                            or "time" in str(column).casefold()
                            for frame in loaded.values()
                            for column in frame.columns
                        )
                        else InputShape.FLAT_TABLE
                    ),
                    representation_status=InputRepresentationStatus.VALID,
                    source_paths=[str(path)],
                    row_semantics="one observation per row",
                    confidence=0.95,
                )
            )

        for proposed_name, frame in loaded.items():
            table_name = unique_table_name(proposed_name, tables)
            frame = frame.copy()
            frame.columns = [str(column) for column in frame.columns]
            tables[table_name] = frame
            if operational_payload is not None:
                if len(loaded) == 1:
                    structured_inputs[table_name] = operational_payload
                elif isinstance(operational_payload, dict):
                    structured_inputs[table_name] = operational_payload.get(
                        proposed_name
                    )

    if effective_policies:
        effective_policy = EvaluationFieldPolicy(
            operational_input_paths=list(
                dict.fromkeys(
                    path
                    for policy in effective_policies
                    for path in policy.operational_input_paths
                )
            ),
            held_out_reference_paths=list(
                dict.fromkeys(
                    path
                    for policy in effective_policies
                    for path in policy.held_out_reference_paths
                )
            ),
            metadata_paths=list(
                dict.fromkeys(
                    path
                    for policy in effective_policies
                    for path in policy.metadata_paths
                )
            ),
        )
    else:
        effective_policy = evaluation_field_policy or EvaluationFieldPolicy()

    return DataBundle(
        tables=tables,
        source_paths=paths,
        fingerprint=fingerprint_files(paths),
        structured_inputs=structured_inputs,
        input_structure=combine_structure_profiles(structure_profiles),
        evaluation_field_policy=effective_policy,
    )


def normalise_column_name(column_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", column_name.lower()).strip()


def looks_datetime_like(series: pd.Series) -> bool:
    sample = series.dropna().astype(str).head(200)

    if sample.empty:
        return False

    datetime_pattern_rate = sample.str.contains(
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"
        r"|"
        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"
        r"|"
        r"\d{1,2}:\d{2}",
        regex=True,
    ).mean()

    return bool(datetime_pattern_rate >= 0.5)


def classify_zero_risk(
    *,
    column_name: str,
    zero_count: int,
    zero_rate: float,
    median: float,
    q05: float,
) -> tuple[ZeroRisk, str]:
    if zero_count == 0:
        return ZeroRisk.NONE, "No zero observations were recorded."

    name = normalise_column_name(column_name)

    if any(term in name for term in VALID_ZERO_TERMS):
        return (
            ZeroRisk.LIKELY_VALID,
            "Zero is valid on the apparent measurement or coding scale.",
        )

    if any(term in name for term in CONTEXT_DEPENDENT_ZERO_TERMS):
        return (
            ZeroRisk.CONTEXT_DEPENDENT,
            "Zero may be a genuine extreme observation and should not be "
            "treated as erroneous without contextual evidence.",
        )

    if (
        any(term in name for term in POSSIBLE_SENTINEL_ZERO_TERMS)
        and median > 0
        and q05 > 0
    ):
        return (
            ZeroRisk.POSSIBLE_SENTINEL,
            "Zero is separated from the main positive distribution and may "
            "represent encoded missingness or measurement failure.",
        )

    if median >= 10 and q05 > 0 and zero_rate <= 0.05:
        return (
            ZeroRisk.UNUSUAL,
            "Zero is unusual relative to the observed distribution, but its "
            "validity cannot be established without metadata.",
        )

    return (
        ZeroRisk.NONE,
        "The observed distribution does not provide sufficient evidence that "
        "zero is problematic.",
    )


def datetime_parse_rate(series: pd.Series) -> float:
    non_missing = series.dropna()

    if non_missing.empty:
        return 0.0

    sample = non_missing.head(1_000)

    if pd.api.types.is_datetime64_any_dtype(sample):
        return 1.0

    if pd.api.types.is_numeric_dtype(sample):
        return 0.0

    if not looks_datetime_like(sample):
        return 0.0

    parsed = pd.to_datetime(sample, errors="coerce", utc=True)
    return float(parsed.notna().mean())


def infer_semantic_type(
    series: pd.Series,
    unique_count: int,
    parse_rate: float,
) -> str:
    if series.map(
        lambda value: isinstance(value, (list, dict, tuple, set))
    ).any():
        return "structured"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series) or parse_rate >= 0.8:
        return "datetime"

    row_count = max(len(series), 1)

    if unique_count <= max(20, int(row_count * 0.05)):
        return "categorical"

    return "text"


def numeric_diagnostics(
    column_name: str,
    series: pd.Series,
) -> tuple[dict[str, float | int], list[str], ZeroRisk, str, bool]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()

    if numeric.empty:
        return {}, [], ZeroRisk.NONE, "No numeric observations were available.", False

    q01 = float(numeric.quantile(0.01))
    q05 = float(numeric.quantile(0.05))
    q25 = float(numeric.quantile(0.25))
    q75 = float(numeric.quantile(0.75))
    q99 = float(numeric.quantile(0.99))

    iqr = q75 - q25

    if iqr > 0:
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        outlier_count = int(
            ((numeric < lower_bound) | (numeric > upper_bound)).sum()
        )
    else:
        outlier_count = 0

    zero_count = int((numeric == 0).sum())
    zero_rate = zero_count / len(numeric)

    median = float(numeric.median())

    zero_risk, zero_risk_reason = classify_zero_risk(
        column_name=column_name,
        zero_count=zero_count,
        zero_rate=float(zero_rate),
        median=median,
        q05=q05,
    )
    suspicious_zero = zero_risk in {
        ZeroRisk.UNUSUAL,
        ZeroRisk.POSSIBLE_SENTINEL,
    }

    warnings: list[str] = []

    if suspicious_zero:
        warnings.append(zero_risk_reason)

    summary: dict[str, float | int] = {
        "count": int(numeric.count()),
        "mean": float(numeric.mean()),
        "median": median,
        "standard_deviation": (
            float(numeric.std(ddof=1))
            if len(numeric) > 1
            else 0.0
        ),
        "minimum": float(numeric.min()),
        "q01": q01,
        "q05": q05,
        "q25": q25,
        "q75": q75,
        "q99": q99,
        "maximum": float(numeric.max()),
        "zero_count": zero_count,
        "zero_rate": float(zero_rate),
        "negative_count": int((numeric < 0).sum()),
        "skewness": (
            float(numeric.skew())
            if len(numeric) > 2
            else 0.0
        ),
        "iqr_outlier_count": outlier_count,
    }

    return summary, warnings, zero_risk, zero_risk_reason, suspicious_zero


def profile_data(bundle: DataBundle) -> DataProfile:
    path_lookup = {
        path.stem: str(path)
        for path in bundle.source_paths
    }

    table_profiles: list[TableProfile] = []

    for table_name, frame in bundle.tables.items():
        hashable_frame = frame.copy()

        for column in hashable_frame.columns:
            hashable_frame[column] = hashable_frame[column].map(safe_hashable)

        duplicate_count = int(hashable_frame.duplicated().sum())

        candidate_keys: list[str] = []
        columns: list[ColumnProfile] = []
        table_warnings: list[str] = []

        for column_name in frame.columns:
            series = frame[column_name]
            safe_series = series.map(safe_hashable)

            missing_count = int(safe_series.isna().sum())
            unique_count = int(safe_series.nunique(dropna=True))
            parse_rate = datetime_parse_rate(series)

            candidate_key = bool(
                len(frame) > 0
                and missing_count == 0
                and unique_count == len(frame)
            )

            if candidate_key:
                candidate_keys.append(column_name)

            semantic_type = infer_semantic_type(
                series,
                unique_count,
                parse_rate,
            )

            non_missing = safe_series.dropna()

            if non_missing.empty:
                dominant_rate = 0.0
            else:
                dominant_rate = float(
                    non_missing.value_counts(normalize=True).iloc[0]
                )

            constant = unique_count <= 1 and len(frame) > 0
            near_constant = not constant and dominant_rate >= 0.995

            summary: dict[str, float | int] = {}
            quality_warnings: list[str] = []
            suspicious_zero = False
            zero_risk = ZeroRisk.NONE
            zero_risk_reason = None

            if semantic_type == "numeric":
                (
                    summary,
                    numeric_warnings,
                    zero_risk,
                    zero_risk_reason,
                    suspicious_zero,
                ) = numeric_diagnostics(
                    column_name,
                    series,
                )
                quality_warnings.extend(numeric_warnings)

            if constant:
                quality_warnings.append(
                    "The column is constant and has no observed analytical variation."
                )

            if near_constant:
                quality_warnings.append(
                    "The column is near-constant and may contribute little analytical information."
                )

            samples = list(
                dict.fromkeys(
                    profile_sample_value(value)
                    for value in series.dropna().head(20)
                )
            )[:5]

            columns.append(
                ColumnProfile(
                    name=column_name,
                    dtype=str(series.dtype),
                    semantic_type=semantic_type,
                    missing_count=missing_count,
                    missing_rate=round(
                        missing_count / max(len(frame), 1),
                        6,
                    ),
                    unique_count=unique_count,
                    sample_values=samples,
                    numeric_summary=summary,
                    datetime_parse_rate=round(parse_rate, 6),
                    candidate_key=candidate_key,
                    structured_values=semantic_type == "structured",
                    constant=constant,
                    near_constant=near_constant,
                    dominant_value_rate=round(dominant_rate, 6),
                    suspicious_zero_values=suspicious_zero,
                    possible_sentinel_values=suspicious_zero,
                    zero_risk=zero_risk,
                    zero_risk_reason=zero_risk_reason,
                    quality_warnings=quality_warnings,
                )
            )

        if len(frame) == 0:
            table_warnings.append("The table contains no rows.")

        if duplicate_count:
            table_warnings.append(
                f"{duplicate_count} duplicate rows were detected."
            )

        if any(column.missing_rate >= 0.5 for column in columns):
            table_warnings.append(
                "At least one column has 50% or more missing values."
            )

        constant_columns = [
            column.name for column in columns if column.constant
        ]

        if constant_columns:
            table_warnings.append(
                "Constant columns detected: "
                + ", ".join(f"`{column}`" for column in constant_columns)
                + "."
            )

        suspicious_zero_columns = [
            column.name
            for column in columns
            if column.suspicious_zero_values
        ]

        if suspicious_zero_columns:
            table_warnings.append(
                "Potentially suspicious zero values detected in: "
                + ", ".join(
                    f"`{column}`"
                    for column in suspicious_zero_columns
                )
                + "."
            )

        source_path = next(
            (
                path
                for stem, path in path_lookup.items()
                if table_name.startswith(stem)
            ),
            str(bundle.source_paths[0]),
        )

        table_profiles.append(
            TableProfile(
                table_name=table_name,
                source_path=source_path,
                row_count=int(len(frame)),
                column_count=int(len(frame.columns)),
                duplicate_row_count=duplicate_count,
                candidate_keys=candidate_keys,
                columns=columns,
                warnings=table_warnings,
            )
        )

    return DataProfile(
        fingerprint=bundle.fingerprint,
        source_paths=[str(path) for path in bundle.source_paths],
        tables=table_profiles,
    )
