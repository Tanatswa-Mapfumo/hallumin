from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .schemas import ColumnProfile, DataProfile, TableProfile


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".json",
    ".jsonl",
    ".ndjson",
    ".parquet",
    ".xlsx",
    ".xls",
}


@dataclass
class DataBundle:
    tables: dict[str, pd.DataFrame]
    source_paths: list[Path]
    fingerprint: str


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


def load_json_tables(path: Path) -> dict[str, pd.DataFrame]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

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

        try:
            return {path.stem: pd.DataFrame(payload)}
        except ValueError:
            return {path.stem: pd.json_normalize(payload)}

    return {path.stem: pd.DataFrame({"value": [payload]})}


def load_data(inputs: Iterable[str | Path]) -> DataBundle:
    paths = expand_inputs(inputs)
    tables: dict[str, pd.DataFrame] = {}

    for path in paths:
        extension = path.suffix.lower()

        if extension == ".csv":
            loaded = {path.stem: pd.read_csv(path, low_memory=False)}
        elif extension == ".json":
            loaded = load_json_tables(path)
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

        for proposed_name, frame in loaded.items():
            table_name = unique_table_name(proposed_name, tables)
            frame = frame.copy()
            frame.columns = [str(column) for column in frame.columns]
            tables[table_name] = frame

    return DataBundle(
        tables=tables,
        source_paths=paths,
        fingerprint=fingerprint_files(paths),
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
    series: pd.Series,
) -> tuple[dict[str, float | int], list[str], bool]:
    numeric = pd.to_numeric(series, errors="coerce").dropna()

    if numeric.empty:
        return {}, [], False

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

    suspicious_zero = bool(
        zero_count > 0
        and median >= 10
        and q05 > 0
        and zero_rate < 0.20
    )

    warnings: list[str] = []

    if suspicious_zero:
        warnings.append(
            "Zero values are separated from most of the positive distribution "
            "and may require validation as possible sentinel or measurement values."
        )

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

    return summary, warnings, suspicious_zero


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

            if semantic_type == "numeric":
                summary, numeric_warnings, suspicious_zero = numeric_diagnostics(
                    series
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

            samples = (
                non_missing.astype(str)
                .drop_duplicates()
                .head(5)
                .tolist()
            )

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