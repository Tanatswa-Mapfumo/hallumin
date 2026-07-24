from __future__ import annotations

import math
import re
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .capabilities import event_capability_evidence, semantic_query_evidence
from .config import Settings
from .data import DataBundle, classify_zero_risk, safe_hashable
from .schemas import (
    AnalyticalFunction,
    AnalysisRoute,
    AnalyticalRecommendation,
    ClaimPermission,
    EvidenceCapability,
    EvidenceItem,
    EvidenceLedger,
    ExecutionPlan,
    InputSemanticMap,
    InputShape,
    InvestigationTask,
    RecommendedUse,
    ReportGenre,
    SemanticLevel,
    TargetStatus,
    ValidationStrategy,
    ZeroRisk,
)


def infer_evidence_capability(
    route: AnalysisRoute,
    metrics: dict[str, Any],
) -> EvidenceCapability:
    if route == AnalysisRoute.ASSOCIATION_COMPARISON:
        if any(
            key in metrics
            for key in {"pearson_r", "spearman_r", "correlation"}
        ):
            return EvidenceCapability.ASSOCIATION
        return EvidenceCapability.GROUP_COMPARISON

    if route == AnalysisRoute.DESCRIPTIVE:
        if "duplicate_row_count" in metrics:
            return EvidenceCapability.DUPLICATES
        if "missing_count" in metrics or "missing_rate" in metrics:
            return EvidenceCapability.MISSINGNESS
        if "row_count" in metrics and "column_count" in metrics:
            return EvidenceCapability.DATASET_PROFILE
        return EvidenceCapability.DISTRIBUTION_SUMMARY

    return EvidenceCapability.DATASET_PROFILE


class EvidenceBuilder:
    def __init__(self, fingerprint: str):
        self.fingerprint = fingerprint
        self.items: list[EvidenceItem] = []
        self.execution_notes: list[str] = []

    def add(
        self,
        *,
        route: AnalysisRoute,
        task_ids: list[str],
        finding: str,
        metrics: dict[str, Any],
        source_tables: list[str],
        source_columns: list[str],
        method: str,
        practical_interpretation: str,
        strength_label: str,
        claim_permissions: list[ClaimPermission],
        factual_confidence: float,
        methodological_strength: float,
        user_relevance: float,
        salience: float,
        recommended_use: RecommendedUse,
        validation_strategy: ValidationStrategy = ValidationStrategy.NONE,
        limitations: list[str] | None = None,
        prohibited_interpretations: list[str] | None = None,
        recommendations: list[AnalyticalRecommendation] | None = None,
        eligible_for_writer: bool = True,
        exclusion_reason: str | None = None,
        capability: EvidenceCapability | None = None,
        evidence_type: str | None = None,
        source_paths: list[str] | None = None,
        entity_scope: list[str] | None = None,
        semantic_level: SemanticLevel = SemanticLevel.DATASET,
        semantic_binding_ids: list[str] | None = None,
        analytical_function: AnalyticalFunction | None = None,
        query_id: str | None = None,
    ) -> None:
        evidence_id = f"EVD_{len(self.items) + 1:04d}"

        item = EvidenceItem(
            evidence_id=evidence_id,
            route=route,
            task_ids=task_ids,
            capability=(
                capability
                or infer_evidence_capability(route, metrics)
            ),
            evidence_type=evidence_type or strength_label,
            source_paths=source_paths or [],
            entity_scope=entity_scope or [],
            semantic_level=semantic_level,
            semantic_binding_ids=semantic_binding_ids or [],
            analytical_function=analytical_function,
            query_id=query_id,
            finding=finding,
            metrics=metrics,
            source_tables=source_tables,
            source_columns=source_columns,
            method=method,
            validation_strategy=validation_strategy,
            practical_interpretation=practical_interpretation,
            strength_label=strength_label,
            limitations=limitations or [],
            prohibited_interpretations=prohibited_interpretations or [],
            recommendations=recommendations or [],
            claim_permissions=claim_permissions,
            factual_confidence=factual_confidence,
            methodological_strength=methodological_strength,
            user_relevance=user_relevance,
            salience=salience,
            recommended_use=recommended_use,
            eligible_for_writer=eligible_for_writer,
            exclusion_reason=exclusion_reason,
        )
        item.metrics["priority_score"] = evidence_priority_score(item)
        self.items.append(item)

    def build(self) -> EvidenceLedger:
        return EvidenceLedger(
            fingerprint=self.fingerprint,
            items=self.items,
            execution_notes=self.execution_notes,
        )


def tasks_for_route(
    plan: ExecutionPlan,
    route: AnalysisRoute,
) -> list[InvestigationTask]:
    return [task for task in plan.tasks if task.route == route]


def event_analysis(
    bundle: DataBundle,
    plan: ExecutionPlan,
    builder: EvidenceBuilder,
    semantic_map: InputSemanticMap | None = None,
) -> None:
    selected = set(plan.selected_capabilities)
    event_capabilities = {
        EvidenceCapability.EVENT_OUTCOME,
        EvidenceCapability.ENTITY_PERFORMANCE,
        EvidenceCapability.RANKING,
        EvidenceCapability.GROUP_COMPARISON,
    }
    if not selected & event_capabilities:
        return

    event_tasks = [
        task
        for task in plan.tasks
        if task.capability in event_capabilities
    ]
    fallback_task_ids = [task.task_id for task in event_tasks]

    semantic_map_available = bool(semantic_map is not None and semantic_map.bindings)
    semantic_query_mode = bool(semantic_map_available and plan.evidence_queries)

    if semantic_map_available and not plan.evidence_queries:
        builder.execution_notes.append(
            "The semantic event map was available, but the frozen plan "
            "contained no validated evidence queries. Legacy field-alias "
            "extraction was not used."
        )
        return

    for table_name, payload in bundle.structured_inputs.items():
        records = (
            semantic_query_evidence(
                table_name=table_name,
                payload=payload,
                semantic_map=semantic_map,
                queries=plan.evidence_queries,
            )
            if semantic_query_mode and semantic_map is not None
            else event_capability_evidence(payload)
        )
        if not records:
            continue

        builder.add(
            route=AnalysisRoute.DESCRIPTIVE,
            task_ids=fallback_task_ids,
            capability=EvidenceCapability.DATASET_PROFILE,
            evidence_type="event_record_overview",
            finding=(
                f"`{table_name}` contains one structured event record with "
                "nested participant and entity information."
            ),
            metrics={
                "event_count": 1,
                "input_shape": InputShape.EVENT_RECORD.value,
            },
            source_tables=[table_name],
            source_columns=list(bundle.tables[table_name].columns),
            source_paths=[],
            entity_scope=[],
            semantic_level=SemanticLevel.EVENT,
            method="Validated input-structure inspection.",
            practical_interpretation=(
                "The source is one event, not a flat sample of independent rows."
            ),
            strength_label="event_record_overview",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.9,
            salience=0.85,
            recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            eligible_for_writer=not semantic_query_mode,
            exclusion_reason=(
                "Container-level profile evidence is excluded from the semantic event Writer path."
                if semantic_query_mode
                else None
            ),
        )

        for record in records:
            if record.capability not in selected:
                continue
            task_ids = [
                task.task_id
                for task in event_tasks
                if task.capability == record.capability
            ] or fallback_task_ids
            builder.add(
                route=(
                    AnalysisRoute.ASSOCIATION_COMPARISON
                    if record.capability == EvidenceCapability.GROUP_COMPARISON
                    else AnalysisRoute.DESCRIPTIVE
                ),
                task_ids=task_ids,
                capability=record.capability,
                evidence_type=record.evidence_type,
                finding=record.finding,
                metrics=record.metrics,
                source_tables=[table_name],
                source_columns=list(
                    dict.fromkeys(path.split(".", 1)[0] for path in record.source_paths)
                ),
                source_paths=record.source_paths,
                entity_scope=record.entity_scope,
                method=(
                    "Validated generic semantic-query execution."
                    if semantic_query_mode
                    else "Legacy structured-event extraction fallback."
                ),
                practical_interpretation=record.practical_interpretation,
                strength_label=record.strength_label,
                claim_permissions=record.claim_permissions,
                factual_confidence=record.factual_confidence,
                methodological_strength=record.methodological_strength,
                user_relevance=record.user_relevance,
                salience=record.salience,
                recommended_use=record.recommended_use,
                limitations=record.limitations,
                prohibited_interpretations=record.prohibited_interpretations,
                semantic_level=record.semantic_level,
                semantic_binding_ids=record.semantic_binding_ids,
                analytical_function=record.analytical_function,
                query_id=record.query_id,
            )


def correlation_strength(value: float) -> str:
    absolute = abs(value)

    if absolute >= 0.70:
        return "very_strong"
    if absolute >= 0.50:
        return "strong"
    if absolute >= 0.30:
        return "moderate"
    if absolute >= 0.20:
        return "weak_but_reportable"
    return "negligible"


def standardised_difference_strength(value: float | None) -> str:
    if value is None:
        return "not_available"

    absolute = abs(value)

    if absolute >= 0.80:
        return "large"
    if absolute >= 0.50:
        return "moderate"
    if absolute >= 0.20:
        return "small"
    return "negligible"


def recommendation(
    builder: EvidenceBuilder,
    action: str,
    recommendation_type: str,
    priority: str,
    justification: str,
    affected_analyses: list[str] | None = None,
    consequence_if_ignored: str | None = None,
    confidence: float = 0.75,
) -> AnalyticalRecommendation:
    count = sum(len(item.recommendations) for item in builder.items) + 1

    return AnalyticalRecommendation(
        recommendation_id=f"REC_{count:04d}",
        action=action,
        recommendation_type=recommendation_type,
        priority=priority,
        justification=justification,
        affected_analyses=affected_analyses or [],
        consequence_if_ignored=(
            consequence_if_ignored
            or "The related analysis may be less reliable or harder to interpret."
        ),
        confidence=confidence,
    )


LOW_PRIORITY_STRENGTH_LABELS = {
    "negligible",
    "negligible_association",
    "weak_but_reportable_association",
    "small_group_difference",
}


def eligible_as_main_finding(item: EvidenceItem) -> bool:
    if not item.eligible_for_writer:
        return False

    if item.recommended_use not in {
        RecommendedUse.HEADLINE,
        RecommendedUse.MAIN_FINDING,
    }:
        return False

    if item.strength_label in LOW_PRIORITY_STRENGTH_LABELS:
        return False

    return (
        item.factual_confidence >= 0.90
        and item.methodological_strength >= 0.70
        and item.user_relevance >= 0.65
    )


def evidence_priority_score(item: EvidenceItem) -> float:
    use_bonus = {
        RecommendedUse.HEADLINE: 0.25,
        RecommendedUse.MAIN_FINDING: 0.15,
        RecommendedUse.SUPPORTING_DETAIL: 0.0,
        RecommendedUse.LIMITATION: 0.10,
        RecommendedUse.OMIT_UNLESS_REQUESTED: -0.30,
    }[item.recommended_use]

    strength_bonus = {
        "very_strong_association": 0.20,
        "strong_association": 0.15,
        "moderate_association": 0.08,
        "large_group_difference": 0.18,
        "moderate_group_difference": 0.10,
        "small_group_difference": -0.08,
        "possible_data_quality_issue": 0.12,
        "possible_sentinel_zero": 0.15,
        "constant_column": 0.15,
        "validated_internal_prediction": 0.15,
        "validated_forecast": 0.15,
        "model_not_better_than_baseline": 0.10,
        "forecast_not_better_than_baseline": 0.10,
    }.get(item.strength_label, 0.0)

    return (
        0.30 * item.salience
        + 0.25 * item.user_relevance
        + 0.20 * item.methodological_strength
        + 0.15 * item.factual_confidence
        + use_bonus
        + strength_bonus
    )


def descriptive_analysis(
    bundle: DataBundle,
    tasks: list[InvestigationTask],
    builder: EvidenceBuilder,
) -> None:
    tasks_by_table: dict[str, list[InvestigationTask]] = {}

    for task in tasks:
        tasks_by_table.setdefault(task.table_name, []).append(task)

    for table_name, table_tasks in tasks_by_table.items():
        if table_name not in bundle.tables:
            continue

        frame = bundle.tables[table_name]
        task_ids = [task.task_id for task in table_tasks]

        builder.add(
            route=AnalysisRoute.DESCRIPTIVE,
            task_ids=task_ids,
            finding=(
                f"Table `{table_name}` contains {len(frame):,} rows "
                f"and {len(frame.columns):,} columns."
            ),
            metrics={
                "row_count": len(frame),
                "column_count": len(frame.columns),
            },
            source_tables=[table_name],
            source_columns=list(frame.columns),
            method="Direct inspection of loaded table dimensions.",
            practical_interpretation=(
                "This establishes the size and dimensionality of the available data."
            ),
            strength_label="dataset_overview",
            claim_permissions=[ClaimPermission.DESCRIPTIVE],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.95,
            salience=0.95,
            recommended_use=RecommendedUse.HEADLINE,
        )

        hashable_frame = frame.copy()

        for column_name in hashable_frame.columns:
            hashable_frame[column_name] = (
                hashable_frame[column_name].map(
                    safe_hashable
                )
            )

        duplicate_row_count = int(
            hashable_frame.duplicated().sum()
        )

        if duplicate_row_count > 0:
            duplicate_row_rate = duplicate_row_count / max(
                len(frame),
                1,
            )

            builder.add(
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=task_ids,
                finding=(
                    f"Table `{table_name}` contains "
                    f"{duplicate_row_count:,} exact duplicate rows "
                    f"({duplicate_row_rate:.2%} of rows)."
                ),
                metrics={
                    "duplicate_row_count": duplicate_row_count,
                    "duplicate_row_rate": duplicate_row_rate,
                    "row_count": len(frame),
                },
                source_tables=[table_name],
                source_columns=list(frame.columns),
                method="Exact row duplicate inspection.",
                practical_interpretation=(
                    "Exactly repeated rows are present, but the available "
                    "data do not establish whether they are invalid."
                ),
                strength_label="duplicate_rows",
                limitations=[
                    "Exact duplicate rows may be genuine repeated observations "
                    "or unintended duplicates."
                ],
                prohibited_interpretations=[
                    "Do not call duplicate rows erroneous without record-level "
                    "validation.",
                    "Do not automatically recommend deduplication.",
                ],
                recommendations=[
                    AnalyticalRecommendation(
                        recommendation_id="REC_DUPLICATE_ROWS",
                        action=(
                            "Review the exact duplicate rows before deciding "
                            "whether to remove them."
                        ),
                        recommendation_type="data_cleaning",
                        priority="medium",
                        justification=(
                            "Exactly repeated rows can either be valid repeated "
                            "observations or unintended duplicates."
                        ),
                        affected_analyses=[
                            "descriptive analysis",
                            "correlation analysis",
                            "group comparison",
                            "predictive modelling",
                        ],
                        consequence_if_ignored=(
                            "Repeated rows may influence summaries or models if "
                            "they are unintended duplicates."
                        ),
                        confidence=1.0,
                    )
                ],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.METHODOLOGICAL,
                ],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.75,
                salience=0.65,
                recommended_use=RecommendedUse.SUPPORTING_DETAIL,
            )

        missing_counts = frame.isna().sum().sort_values(ascending=False)

        for column_name, count in missing_counts.items():
            count = int(count)

            if count == 0:
                continue

            rate = count / max(len(frame), 1)

            builder.add(
                route=AnalysisRoute.DESCRIPTIVE,
                task_ids=task_ids,
                finding=(
                    f"`{column_name}` has {count:,} missing values "
                    f"({rate:.2%} of rows)."
                ),
                metrics={
                    "missing_count": count,
                    "missing_rate": rate,
                },
                source_tables=[table_name],
                source_columns=[column_name],
                method="Direct missing-value count.",
                practical_interpretation=(
                    "The field is largely complete."
                    if rate < 0.01
                    else "Missingness may materially affect analysis using this field."
                ),
                strength_label=(
                    "low_missingness"
                    if rate < 0.01
                    else "material_missingness"
                ),
                claim_permissions=[ClaimPermission.DESCRIPTIVE],
                factual_confidence=1.0,
                methodological_strength=1.0,
                user_relevance=0.75 if rate >= 0.01 else 0.55,
                salience=0.75 if rate >= 0.01 else 0.50,
                recommended_use=(
                    RecommendedUse.MAIN_FINDING
                    if rate >= 0.05
                    else RecommendedUse.SUPPORTING_DETAIL
                ),
            )

        for column_name in frame.columns:
            series = frame[column_name]
            safe_series = series.map(safe_hashable)
            non_missing = safe_series.dropna()

            if non_missing.empty:
                continue

            unique_count = int(non_missing.nunique())

            if unique_count == 1:
                value = str(non_missing.iloc[0])

                builder.add(
                    route=AnalysisRoute.DESCRIPTIVE,
                    task_ids=task_ids,
                    finding=(
                        f"`{column_name}` is constant at `{value}` "
                        f"across all {len(non_missing):,} non-missing rows."
                    ),
                    metrics={
                        "constant": True,
                        "constant_value": value,
                        "non_missing_count": len(non_missing),
                    },
                    source_tables=[table_name],
                    source_columns=[column_name],
                    method="Unique-value and frequency inspection.",
                    practical_interpretation=(
                        "The column contains no observed variation and should not "
                        "be used for correlation, comparison, prediction, or forecasting."
                    ),
                    strength_label="constant_column",
                    claim_permissions=[
                        ClaimPermission.DESCRIPTIVE,
                        ClaimPermission.METHODOLOGICAL,
                    ],
                    factual_confidence=1.0,
                    methodological_strength=1.0,
                    user_relevance=0.90,
                    salience=0.90,
                    recommended_use=RecommendedUse.MAIN_FINDING,
                    recommendations=[
                        recommendation(
                            builder,
                            action=(
                                f"Remove `{column_name}` from correlation, comparison, "
                                "and predictive feature sets unless its constant value "
                                "has a documented interpretation."
                            ),
                            recommendation_type="data_cleaning",
                            priority="high",
                            justification=(
                                "The variable contains no observed variation and therefore "
                                "cannot distinguish observations or explain differences."
                            ),
                            affected_analyses=[
                                "correlation analysis",
                                "group comparison",
                                "predictive modelling",
                            ],
                            consequence_if_ignored=(
                                "The field will add no analytical information and may "
                                "create unnecessary processing or numerical issues in "
                                "methods that expect varying predictors."
                            ),
                            confidence=1.0,
                        )
                    ],
                    prohibited_interpretations=[
                        "Do not compare groups using this column as an outcome.",
                        "Do not describe the column as predictive.",
                    ],
                )
                continue

            if pd.api.types.is_numeric_dtype(series):
                values = pd.to_numeric(series, errors="coerce").dropna()

                if values.empty:
                    continue

                q01 = float(values.quantile(0.01))
                q05 = float(values.quantile(0.05))
                q25 = float(values.quantile(0.25))
                q75 = float(values.quantile(0.75))
                q99 = float(values.quantile(0.99))
                mean = float(values.mean())
                median = float(values.median())
                std = float(values.std(ddof=1)) if len(values) > 1 else 0.0
                zero_count = int((values == 0).sum())
                zero_rate = zero_count / len(values)
                zero_risk, zero_risk_reason = classify_zero_risk(
                    column_name=column_name,
                    zero_count=zero_count,
                    zero_rate=zero_rate,
                    median=median,
                    q05=q05,
                )

                metrics = {
                    "count": int(values.count()),
                    "mean": mean,
                    "median": median,
                    "standard_deviation": std,
                    "minimum": float(values.min()),
                    "q01": q01,
                    "q05": q05,
                    "q25": q25,
                    "q75": q75,
                    "q99": q99,
                    "maximum": float(values.max()),
                    "zero_count": zero_count,
                    "zero_rate": zero_rate,
                    "zero_risk": zero_risk.value,
                    "zero_risk_reason": zero_risk_reason,
                    "negative_count": int((values < 0).sum()),
                    "skewness": (
                        float(values.skew())
                        if len(values) > 2
                        else 0.0
                    ),
                }

                centre_difference = abs(mean - median)
                centre_close = std == 0 or centre_difference <= 0.10 * std

                if centre_close:
                    interpretation = (
                        "The mean and median are close relative to the observed spread, "
                        "so the centre is not strongly separated by this diagnostic."
                    )
                else:
                    interpretation = (
                        "The mean and median differ relative to the observed spread, "
                        "which may indicate skewness or influential values."
                    )

                suspicious_zero = zero_risk in {
                    ZeroRisk.UNUSUAL,
                    ZeroRisk.POSSIBLE_SENTINEL,
                }

                limitations = [
                    "Distribution summaries do not establish a trend, prediction, "
                    "or causal relationship."
                ]

                recommendations: list[AnalyticalRecommendation] = []

                if zero_risk == ZeroRisk.CONTEXT_DEPENDENT:
                    limitations.append(zero_risk_reason)

                if suspicious_zero:
                    limitations.append(zero_risk_reason)

                    if zero_risk == ZeroRisk.POSSIBLE_SENTINEL:
                        priority = "high"
                        recommendation_use = RecommendedUse.MAIN_FINDING
                        strength_label = "possible_sentinel_zero"
                        consequence = (
                            "Treating encoded missing values as genuine measurements "
                            "could distort means, associations, and fitted model "
                            "relationships."
                        )
                        confidence = 0.85
                    else:
                        priority = "medium"
                        recommendation_use = RecommendedUse.SUPPORTING_DETAIL
                        strength_label = "possible_data_quality_issue"
                        consequence = (
                            "If the zeros are invalid records, summaries and "
                            "relationships involving this field may be distorted."
                        )
                        confidence = 0.70

                    recommendations.append(
                        recommendation(
                            builder,
                            action=(
                                f"Validate zero values in `{column_name}` against "
                                "source records or metadata before relying on analyses "
                                "involving this field."
                            ),
                            recommendation_type="data_cleaning",
                            priority=priority,
                            justification=zero_risk_reason,
                            affected_analyses=[
                                "descriptive statistics",
                                "correlation analysis",
                                "predictive modelling",
                            ],
                            consequence_if_ignored=consequence,
                            confidence=confidence,
                        )
                    )
                else:
                    recommendation_use = (
                        RecommendedUse.OMIT_UNLESS_REQUESTED
                        if zero_risk == ZeroRisk.CONTEXT_DEPENDENT
                        else RecommendedUse.SUPPORTING_DETAIL
                    )
                    strength_label = "distribution_summary"

                builder.add(
                    route=AnalysisRoute.DESCRIPTIVE,
                    task_ids=task_ids,
                    finding=(
                        f"`{column_name}` has mean {mean:.4g}, median {median:.4g}, "
                        f"minimum {metrics['minimum']:.4g}, and maximum "
                        f"{metrics['maximum']:.4g} across {len(values):,} "
                        "non-missing observations."
                    ),
                    metrics=metrics,
                    source_tables=[table_name],
                    source_columns=[column_name],
                    method=(
                        "Direct descriptive statistics with quantiles and "
                        "distribution diagnostics."
                    ),
                    practical_interpretation=interpretation,
                    strength_label=(
                        strength_label
                    ),
                    claim_permissions=[
                        ClaimPermission.DESCRIPTIVE,
                        ClaimPermission.METHODOLOGICAL,
                    ],
                    factual_confidence=0.99,
                    methodological_strength=0.98,
                    user_relevance=0.85 if suspicious_zero else 0.55,
                    salience=0.90 if suspicious_zero else 0.50,
                    recommended_use=recommendation_use,
                    limitations=limitations,
                    recommendations=recommendations,
                    prohibited_interpretations=[
                        "Do not infer temporal change from the distribution alone.",
                        "Do not treat a suspicious value as definitively erroneous "
                        "without source validation.",
                    ],
                )

            elif unique_count <= 20:
                counts = non_missing.astype(str).value_counts().head(10)
                top_values = {
                    str(key): int(value)
                    for key, value in counts.items()
                }

                builder.add(
                    route=AnalysisRoute.DESCRIPTIVE,
                    task_ids=task_ids,
                    finding=(
                        f"The most frequent observed values of `{column_name}` are "
                        + ", ".join(
                            f"`{key}` ({value:,})"
                            for key, value in list(top_values.items())[:5]
                        )
                        + "."
                    ),
                    metrics={
                        "value_counts": top_values,
                        "unique_count": unique_count,
                    },
                    source_tables=[table_name],
                    source_columns=[column_name],
                    method="Frequency counts after safe conversion of structured values.",
                    practical_interpretation=(
                        "The counts describe the observed category composition and "
                        "can reveal imbalance between groups."
                    ),
                    strength_label="category_composition",
                    claim_permissions=[ClaimPermission.DESCRIPTIVE],
                    factual_confidence=0.99,
                    methodological_strength=0.98,
                    user_relevance=0.65,
                    salience=0.60,
                    recommended_use=RecommendedUse.SUPPORTING_DETAIL,
                    limitations=[
                        "Counts describe the observed dataset and do not establish "
                        "population prevalence."
                    ],
                )


def association_analysis(
    bundle: DataBundle,
    tasks: list[InvestigationTask],
    builder: EvidenceBuilder,
    settings: Settings,
) -> None:
    for task in tasks:
        table_name = task.table_name

        if table_name not in bundle.tables:
            continue

        original = bundle.tables[table_name]

        if len(original) <= settings.full_data_correlation_limit:
            frame = original.copy()
            sampling_method = "full_dataset"
        else:
            sample_size = min(settings.max_analysis_rows, len(original))
            frame = original.sample(
                n=sample_size,
                random_state=settings.random_seed,
            ).copy()
            sampling_method = "fixed_seed_sample"

        numeric_columns = [
            column
            for column in frame.select_dtypes(include=np.number).columns
            if pd.to_numeric(frame[column], errors="coerce").nunique(dropna=True) > 1
        ]

        correlations: list[tuple[float, str, str, int, float]] = []

        for left, right in combinations(numeric_columns, 2):
            pair = (
                frame[[left, right]]
                .apply(pd.to_numeric, errors="coerce")
                .dropna()
            )

            if (
                len(pair) < 20
                or pair[left].nunique() < 2
                or pair[right].nunique() < 2
            ):
                continue

            correlation = float(pair[left].corr(pair[right]))

            if (
                np.isfinite(correlation)
                and abs(correlation) >= settings.min_abs_correlation
            ):
                correlations.append(
                    (
                        abs(correlation),
                        left,
                        right,
                        len(pair),
                        correlation,
                    )
                )

        for _, left, right, complete_count, value in sorted(
            correlations,
            reverse=True,
        )[: settings.max_correlation_findings]:
            direction = "positive" if value > 0 else "negative"
            strength = correlation_strength(value)

            sample_prefix = (
                "Using the full available data"
                if sampling_method == "full_dataset"
                else f"In a fixed-seed sample of {len(frame):,} rows"
            )

            builder.add(
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=[task.task_id],
                finding=(
                    f"{sample_prefix}, `{left}` and `{right}` have a {direction} "
                    f"Pearson correlation of {value:.4f} across "
                    f"{complete_count:,} complete row pairs."
                ),
                metrics={
                    "pearson_r": value,
                    "complete_pairs": complete_count,
                    "sampling_method": sampling_method,
                    "analysed_rows": len(frame),
                    "strength": strength,
                },
                source_tables=[table_name],
                source_columns=[left, right],
                method="Pairwise-complete Pearson correlation.",
                practical_interpretation=(
                    f"Higher values of `{left}` tend to coincide with "
                    f"{'higher' if value > 0 else 'lower'} values of `{right}`. "
                    f"The observed linear relationship is classified as {strength}."
                ),
                strength_label=f"{strength}_association",
                claim_permissions=[
                    ClaimPermission.ASSOCIATIONAL,
                    ClaimPermission.METHODOLOGICAL,
                ],
                factual_confidence=0.98,
                methodological_strength=0.88,
                user_relevance=min(1.0, 0.45 + abs(value)),
                salience=min(1.0, 0.40 + abs(value)),
                recommended_use=(
                    RecommendedUse.MAIN_FINDING
                    if abs(value) >= 0.50
                    else RecommendedUse.SUPPORTING_DETAIL
                ),
                limitations=[
                    "Correlation does not establish causation.",
                    "Pearson correlation measures linear association and may be "
                    "affected by outliers or non-linear structure.",
                ],
                prohibited_interpretations=[
                    f"Do not say `{left}` causes `{right}`.",
                    f"Do not say `{right}` causes `{left}`.",
                    "Do not describe correlation as complete explanation.",
                ],
            )

        categorical_columns = [
            column
            for column in frame.columns
            if not pd.api.types.is_numeric_dtype(frame[column])
            and 2
            <= frame[column].map(safe_hashable).nunique(dropna=True)
            <= 10
        ]

        candidates: list[dict[str, Any]] = []

        for group_column in categorical_columns[:8]:
            groups = frame[group_column].map(safe_hashable)

            for outcome_column in numeric_columns[:12]:
                working = pd.DataFrame(
                    {
                        "group": groups,
                        "outcome": pd.to_numeric(
                            frame[outcome_column],
                            errors="coerce",
                        ),
                    }
                ).dropna()

                if len(working) < 30:
                    continue

                if working["outcome"].nunique(dropna=True) < 2:
                    continue

                summary = working.groupby("group")["outcome"].agg(
                    ["mean", "std", "count"]
                )
                summary = summary[summary["count"] >= 5]

                if len(summary) < 2:
                    continue

                if summary["mean"].nunique(dropna=True) < 2:
                    continue

                highest_group = summary["mean"].idxmax()
                lowest_group = summary["mean"].idxmin()

                if highest_group == lowest_group:
                    continue

                highest_mean = float(summary.loc[highest_group, "mean"])
                lowest_mean = float(summary.loc[lowest_group, "mean"])
                difference = highest_mean - lowest_mean

                high_std = float(summary.loc[highest_group, "std"])
                low_std = float(summary.loc[lowest_group, "std"])

                pooled_std = math.sqrt(
                    (
                        (0.0 if math.isnan(high_std) else high_std ** 2)
                        + (0.0 if math.isnan(low_std) else low_std ** 2)
                    )
                    / 2.0
                )

                standardised_difference = (
                    difference / pooled_std
                    if pooled_std > 0
                    else None
                )

                strength = standardised_difference_strength(
                    standardised_difference
                )

                if strength == "negligible":
                    continue

                group_counts = {
                    str(key): int(value)
                    for key, value in summary["count"].items()
                }

                imbalance_ratio = max(group_counts.values()) / max(
                    min(group_counts.values()),
                    1,
                )

                candidates.append(
                    {
                        "score": abs(standardised_difference or 0.0),
                        "group_column": group_column,
                        "outcome_column": outcome_column,
                        "highest_group": str(highest_group),
                        "lowest_group": str(lowest_group),
                        "highest_mean": highest_mean,
                        "lowest_mean": lowest_mean,
                        "difference": difference,
                        "standardised_difference": standardised_difference,
                        "strength": strength,
                        "group_counts": group_counts,
                        "imbalance_ratio": imbalance_ratio,
                    }
                )

        for candidate in sorted(
            candidates,
            key=lambda item: item["score"],
            reverse=True,
        )[: settings.max_group_findings]:
            if candidate["imbalance_ratio"] >= 2:
                group_imbalance_note = (
                    "The groups are unevenly represented. The larger group mean is "
                    "estimated from more observations than the smaller group mean, "
                    "so the estimates may have different levels of precision and "
                    "stability."
                )
            else:
                group_imbalance_note = "The group sizes are not strongly imbalanced."

            builder.add(
                route=AnalysisRoute.ASSOCIATION_COMPARISON,
                task_ids=[task.task_id],
                finding=(
                    f"For `{candidate['outcome_column']}` grouped by "
                    f"`{candidate['group_column']}`, "
                    f"`{candidate['highest_group']}` has the highest observed mean "
                    f"({candidate['highest_mean']:.4g}) and "
                    f"`{candidate['lowest_group']}` the lowest "
                    f"({candidate['lowest_mean']:.4g}), a difference of "
                    f"{candidate['difference']:.4g}."
                ),
                metrics=candidate,
                source_tables=[table_name],
                source_columns=[
                    candidate["group_column"],
                    candidate["outcome_column"],
                ],
                method=(
                    "Observed group means with at least five observations per "
                    "retained group, accompanied by group counts and a "
                    "standardised difference."
                ),
                practical_interpretation=(
                    f"The extreme observed group means differ by "
                    f"{candidate['difference']:.4g}. The standardised difference "
                    f"is classified as {candidate['strength']}. The comparison is "
                    "descriptive and unadjusted."
                ),
                strength_label=(
                    f"{candidate['strength']}_group_difference"
                ),
                claim_permissions=[
                    ClaimPermission.COMPARATIVE,
                    ClaimPermission.ASSOCIATIONAL,
                    ClaimPermission.METHODOLOGICAL,
                ],
                factual_confidence=0.97,
                methodological_strength=0.82,
                user_relevance=min(1.0, 0.50 + candidate["score"] / 2),
                salience=min(1.0, 0.45 + candidate["score"] / 2),
                recommended_use=(
                    RecommendedUse.MAIN_FINDING
                    if candidate["strength"] in {"large", "moderate"}
                    else RecommendedUse.SUPPORTING_DETAIL
                ),
                limitations=[
                    "This is an unadjusted observed comparison.",
                    "The comparison does not establish causation.",
                    group_imbalance_note,
                ],
                prohibited_interpretations=[
                    "Do not say group membership caused the observed difference.",
                    "Do not describe the comparison as adjusted for confounding.",
                ],
            )


def normalise_name(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", value.lower())
    ignored = {"c", "km", "h", "degrees", "millibars", "value"}
    return " ".join(word for word in words if word not in ignored)


def select_and_audit_features(
    frame: pd.DataFrame,
    target_column: str,
    time_column: str | None,
    proxy_threshold: float,
) -> tuple[list[str], list[str], list[dict[str, str]], list[str]]:
    numeric: list[str] = []
    categorical: list[str] = []
    excluded: list[dict[str, str]] = []
    warnings: list[str] = []

    numeric_target = pd.to_numeric(frame[target_column], errors="coerce")
    target_name = normalise_name(target_column)

    for column_name in frame.columns:
        if column_name in {target_column, time_column}:
            continue

        series = frame[column_name]

        if series.map(
            lambda value: isinstance(value, (list, dict, tuple, set))
        ).any():
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "structured_value",
                    "reason": "Structured values are not encoded by this modelling route.",
                }
            )
            continue

        unique_count = int(
            series.map(safe_hashable).nunique(dropna=True)
        )

        if unique_count <= 1:
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "constant",
                    "reason": "The feature has no observed variation.",
                }
            )
            continue

        if unique_count >= max(int(len(frame) * 0.98), 1_000):
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "identifier",
                    "reason": "The field behaves like a high-cardinality identifier.",
                }
            )
            continue

        possible_proxy = False
        proxy_reason = ""

        if pd.api.types.is_numeric_dtype(series) and numeric_target.notna().any():
            numeric_feature = pd.to_numeric(series, errors="coerce")
            pair = pd.DataFrame(
                {
                    "feature": numeric_feature,
                    "target": numeric_target,
                }
            ).dropna()

            if (
                len(pair) >= 20
                and pair["feature"].nunique() > 1
                and pair["target"].nunique() > 1
            ):
                correlation = abs(
                    float(pair["feature"].corr(pair["target"]))
                )

                if correlation >= proxy_threshold:
                    possible_proxy = True
                    proxy_reason = (
                        f"Absolute feature-target correlation is {correlation:.4f}, "
                        f"above the proxy threshold {proxy_threshold:.4f}."
                    )

        feature_name = normalise_name(column_name)

        if (
            target_name
            and feature_name
            and (
                target_name in feature_name
                or feature_name in target_name
            )
        ):
            if column_name != target_column:
                possible_proxy = True
                proxy_reason = (
                    proxy_reason
                    or "The feature name strongly overlaps the target name."
                )

        if possible_proxy:
            excluded.append(
                {
                    "feature": column_name,
                    "risk_type": "target_proxy",
                    "reason": proxy_reason,
                }
            )
            warnings.append(
                f"`{column_name}` was excluded as a possible proxy for "
                f"`{target_column}`: {proxy_reason}"
            )
            continue

        if pd.api.types.is_numeric_dtype(series):
            numeric.append(column_name)
        elif unique_count <= 100:
            categorical.append(column_name)

    return numeric[:30], categorical[:20], excluded, warnings


def make_preprocessor(
    numeric_columns: list[str],
    categorical_columns: list[str],
) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler(with_mean=False)),
        ]
    )

    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ]
    )


def add_predictive_insufficiency(
    builder: EvidenceBuilder,
    task: InvestigationTask,
    finding: str,
    metrics: dict[str, Any],
    limitations: list[str],
    recommendations: list[AnalyticalRecommendation] | None = None,
) -> None:
    builder.add(
        route=AnalysisRoute.PREDICTIVE,
        task_ids=[task.task_id],
        finding=finding,
        metrics=metrics,
        source_tables=[task.table_name],
        source_columns=[
            column
            for column in [
                task.target_column,
                task.time_column,
                *task.columns,
            ]
            if column
        ],
        method="Predictive modelling feasibility and validation assessment.",
        validation_strategy=task.validation_strategy,
        practical_interpretation=(
            "The available evidence does not support a positive predictive claim."
        ),
        strength_label="predictive_insufficiency",
        claim_permissions=[
            ClaimPermission.INSUFFICIENCY,
            ClaimPermission.METHODOLOGICAL,
        ],
        factual_confidence=1.0,
        methodological_strength=0.95,
        user_relevance=0.75,
        salience=0.75,
        recommended_use=RecommendedUse.LIMITATION,
        limitations=limitations,
        recommendations=recommendations or [],
        prohibited_interpretations=[
            "Do not describe the task as successfully validated.",
            "Do not claim deployment readiness.",
        ],
    )


def split_predictive_data(
    frame: pd.DataFrame,
    features: list[str],
    target_column: str,
    time_column: str | None,
    classification: bool,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, ValidationStrategy]:
    working_columns = [*features, target_column]

    if time_column and time_column in frame.columns:
        working_columns.append(time_column)

    working = frame[working_columns].copy()
    working = working.dropna(subset=[target_column])

    if time_column and time_column in working.columns:
        parsed_time = pd.to_datetime(
            working[time_column],
            errors="coerce",
            utc=True,
        )

        parse_rate = float(parsed_time.notna().mean())

        if parse_rate >= 0.80:
            working = working.loc[parsed_time.notna()].copy()
            working["_parsed_time"] = parsed_time.loc[parsed_time.notna()]
            working = working.sort_values("_parsed_time")

            split_index = int(len(working) * 0.75)
            split_index = max(1, min(split_index, len(working) - 1))

            train = working.iloc[:split_index]
            test = working.iloc[split_index:]

            return (
                train[features],
                test[features],
                train[target_column],
                test[target_column],
                ValidationStrategy.CHRONOLOGICAL_HOLDOUT,
            )

    x = working[features]
    y = working[target_column]

    stratify = None

    if classification:
        counts = y.map(safe_hashable).astype(str).value_counts()
        if not counts.empty and counts.min() >= 2:
            stratify = y.map(safe_hashable).astype(str)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=seed,
        stratify=stratify,
    )

    strategy = (
        ValidationStrategy.STRATIFIED_HOLDOUT
        if stratify is not None
        else ValidationStrategy.RANDOM_HOLDOUT
    )

    return x_train, x_test, y_train, y_test, strategy


def predictive_analysis(
    bundle: DataBundle,
    task: InvestigationTask,
    builder: EvidenceBuilder,
    settings: Settings,
) -> None:
    table_name = task.table_name
    target_column = task.target_column

    if table_name not in bundle.tables or not target_column:
        add_predictive_insufficiency(
            builder,
            task,
            "Predictive modelling was not run because no target was selected.",
            {},
            ["A prediction target must be selected before model fitting."],
        )
        return

    if target_column not in bundle.tables[table_name].columns:
        add_predictive_insufficiency(
            builder,
            task,
            f"The selected target `{target_column}` was not found.",
            {},
            ["The prediction target is not present in the table."],
        )
        return

    if (
        task.target_status == TargetStatus.UNCONFIRMED
        or (
            task.target_status == TargetStatus.EXPERIMENTAL_CANDIDATE
            and not settings.allow_experimental_targets
        )
    ):
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"`{target_column}` was not used as a predictive target because "
                "the target was not user-selected or metadata-confirmed."
            ),
            {
                "target_column": target_column,
                "target_status": task.target_status.value,
            },
            [
                "An unconfirmed target is insufficient for a primary predictive claim.",
                "Experimental candidate targets can be enabled explicitly for ablation work.",
            ],
            recommendations=[
                recommendation(
                    builder,
                    action=(
                        f"Ask the user to confirm whether `{target_column}` is the "
                        "intended prediction target."
                    ),
                    recommendation_type="methodological_check",
                    priority="high",
                    justification=(
                        "Predictive performance has no stable interpretation without "
                        "a defined target and prediction objective."
                    ),
                )
            ],
        )
        return

    frame = bundle.tables[table_name].copy()

    if len(frame) > settings.max_analysis_rows:
        frame = frame.sample(
            n=settings.max_analysis_rows,
            random_state=settings.random_seed,
        ).copy()

    frame = frame.dropna(subset=[target_column])

    if len(frame) < 80:
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"Predictive modelling for `{target_column}` was not validated "
                f"because only {len(frame):,} rows had a non-missing target."
            ),
            {"usable_target_rows": len(frame)},
            ["At least 80 usable target rows are required."],
        )
        return

    numeric_columns, categorical_columns, excluded, leakage_warnings = (
        select_and_audit_features(
            frame,
            target_column,
            task.time_column,
            settings.target_proxy_correlation,
        )
    )

    feature_columns = numeric_columns + categorical_columns

    if not feature_columns:
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"No leakage-audited predictor columns remained for "
                f"`{target_column}`."
            ),
            {
                "excluded_features": excluded,
                "leakage_warnings": leakage_warnings,
            },
            [
                "All candidate predictors were constant, identifier-like, "
                "structured, or possible target proxies."
            ],
        )
        return

    target = frame[target_column]

    classification = bool(
        not pd.api.types.is_numeric_dtype(target)
        or target.map(safe_hashable).nunique(dropna=True) <= 20
    )

    try:
        (
            x_train,
            x_test,
            y_train,
            y_test,
            validation_strategy,
        ) = split_predictive_data(
            frame,
            feature_columns,
            target_column,
            task.time_column,
            classification,
            settings.random_seed,
        )

        if len(x_test) < 20:
            add_predictive_insufficiency(
                builder,
                task,
                "The predictive holdout contained fewer than 20 rows.",
                {
                    "train_rows": len(x_train),
                    "test_rows": len(x_test),
                },
                ["The holdout is too small for a stable predictive conclusion."],
            )
            return

        if classification:
            y_train = y_train.map(safe_hashable).astype(str)
            y_test = y_test.map(safe_hashable).astype(str)

            baseline = Pipeline(
                [
                    (
                        "preprocess",
                        make_preprocessor(
                            numeric_columns,
                            categorical_columns,
                        ),
                    ),
                    (
                        "model",
                        DummyClassifier(strategy="most_frequent"),
                    ),
                ]
            )

            baseline.fit(x_train, y_train)
            baseline_prediction = baseline.predict(x_test)

            baseline_f1 = f1_score(
                y_test,
                baseline_prediction,
                average="macro",
                zero_division=0,
            )

            candidates = {
                "logistic_regression": LogisticRegression(max_iter=1_000),
                "random_forest": RandomForestClassifier(
                    n_estimators=150,
                    max_depth=10,
                    random_state=settings.random_seed,
                    n_jobs=-1,
                ),
            }

            results: list[tuple[float, str, float]] = []

            for model_name, model in candidates.items():
                pipeline = Pipeline(
                    [
                        (
                            "preprocess",
                            make_preprocessor(
                                numeric_columns,
                                categorical_columns,
                            ),
                        ),
                        ("model", model),
                    ]
                )
                pipeline.fit(x_train, y_train)
                prediction = pipeline.predict(x_test)

                macro_f1 = f1_score(
                    y_test,
                    prediction,
                    average="macro",
                    zero_division=0,
                )
                accuracy = accuracy_score(y_test, prediction)

                results.append((macro_f1, model_name, accuracy))

            best_f1, best_model, best_accuracy = max(results)
            improvement = best_f1 - baseline_f1
            validated = improvement > 0.02

            metrics = {
                "task": "classification",
                "target_column": target_column,
                "target_status": task.target_status.value,
                "prediction_definition": task.prediction_definition,
                "validation_strategy": validation_strategy.value,
                "best_model": best_model,
                "holdout_macro_f1": best_f1,
                "holdout_accuracy": best_accuracy,
                "baseline_macro_f1": baseline_f1,
                "absolute_improvement": improvement,
                "train_rows": len(x_train),
                "test_rows": len(x_test),
                "features_used": feature_columns,
                "features_excluded": excluded,
                "leakage_warnings": leakage_warnings,
            }

            finding = (
                f"The best leakage-audited classifier for `{target_column}` was "
                f"`{best_model}`, with holdout macro-F1 {best_f1:.4f} and "
                f"accuracy {best_accuracy:.4f}; the majority-class baseline "
                f"macro-F1 was {baseline_f1:.4f}."
            )

        else:
            y_train = pd.to_numeric(y_train, errors="coerce")
            y_test = pd.to_numeric(y_test, errors="coerce")

            train_valid = y_train.notna()
            test_valid = y_test.notna()

            x_train = x_train.loc[train_valid]
            y_train = y_train.loc[train_valid]
            x_test = x_test.loc[test_valid]
            y_test = y_test.loc[test_valid]

            baseline = Pipeline(
                [
                    (
                        "preprocess",
                        make_preprocessor(
                            numeric_columns,
                            categorical_columns,
                        ),
                    ),
                    ("model", DummyRegressor(strategy="mean")),
                ]
            )

            baseline.fit(x_train, y_train)
            baseline_prediction = baseline.predict(x_test)
            baseline_mae = mean_absolute_error(y_test, baseline_prediction)

            candidates = {
                "ridge": Ridge(alpha=1.0),
                "random_forest": RandomForestRegressor(
                    n_estimators=150,
                    max_depth=10,
                    random_state=settings.random_seed,
                    n_jobs=-1,
                ),
            }

            results: list[
                tuple[float, str, float, float, float]
            ] = []

            for model_name, model in candidates.items():
                pipeline = Pipeline(
                    [
                        (
                            "preprocess",
                            make_preprocessor(
                                numeric_columns,
                                categorical_columns,
                            ),
                        ),
                        ("model", model),
                    ]
                )
                pipeline.fit(x_train, y_train)
                prediction = pipeline.predict(x_test)

                mae = mean_absolute_error(y_test, prediction)
                rmse = mean_squared_error(y_test, prediction) ** 0.5
                r_squared = r2_score(y_test, prediction)

                results.append(
                    (-mae, model_name, mae, rmse, r_squared)
                )

            _, best_model, best_mae, best_rmse, best_r_squared = max(results)

            improvement = (
                (baseline_mae - best_mae) / baseline_mae
                if baseline_mae > 0
                else 0.0
            )

            validated = improvement > 0.05

            metrics = {
                "task": "regression",
                "target_column": target_column,
                "target_status": task.target_status.value,
                "prediction_definition": task.prediction_definition,
                "validation_strategy": validation_strategy.value,
                "best_model": best_model,
                "holdout_mae": best_mae,
                "holdout_rmse": best_rmse,
                "holdout_r_squared": best_r_squared,
                "baseline_mae": baseline_mae,
                "relative_mae_improvement": improvement,
                "train_rows": len(x_train),
                "test_rows": len(x_test),
                "features_used": feature_columns,
                "features_excluded": excluded,
                "leakage_warnings": leakage_warnings,
            }

            finding = (
                f"The best leakage-audited regressor for `{target_column}` was "
                f"`{best_model}`, with holdout MAE {best_mae:.4g}, "
                f"RMSE {best_rmse:.4g}, and R² {best_r_squared:.4f}; "
                f"the mean baseline MAE was {baseline_mae:.4g}."
            )

        if not validated:
            finding += (
                " The tested model did not improve the relevant baseline "
                "by the configured validation threshold."
            )

        limitations = [
            "This is internal validation rather than external validation.",
            "Performance may change under distribution shift.",
            "Feature availability at the intended prediction time was not "
            "independently confirmed.",
        ]

        if task.target_status == TargetStatus.EXPERIMENTAL_CANDIDATE:
            limitations.append(
                "The target was selected for an explicit experiment rather than "
                "confirmed by the user or metadata."
            )

        if validation_strategy != ValidationStrategy.CHRONOLOGICAL_HOLDOUT:
            limitations.append(
                "The evaluation was not chronological; it should not be interpreted "
                "as evidence of future performance."
            )

        if leakage_warnings:
            limitations.append(
                "Potential proxy features were excluded before modelling."
            )

        builder.add(
            route=AnalysisRoute.PREDICTIVE,
            task_ids=[task.task_id],
            finding=finding,
            metrics=metrics,
            source_tables=[table_name],
            source_columns=[target_column, *feature_columns],
            method=(
                "Leakage-audited baseline comparison using a holdout selected "
                "according to the available temporal structure."
            ),
            validation_strategy=validation_strategy,
            practical_interpretation=(
                "The model is evidence of internal predictive performance only "
                "when it improves the baseline. It is not evidence of causality "
                "or deployment readiness."
            ),
            strength_label=(
                "validated_internal_prediction"
                if validated
                else "model_not_better_than_baseline"
            ),
            claim_permissions=(
                [
                    ClaimPermission.PREDICTIVE,
                    ClaimPermission.METHODOLOGICAL,
                ]
                if validated
                else [
                    ClaimPermission.INSUFFICIENCY,
                    ClaimPermission.METHODOLOGICAL,
                ]
            ),
            factual_confidence=0.97,
            methodological_strength=(
                0.88
                if validation_strategy == ValidationStrategy.CHRONOLOGICAL_HOLDOUT
                else 0.72
            ),
            user_relevance=0.85,
            salience=0.85,
            recommended_use=(
                RecommendedUse.MAIN_FINDING
                if validated
                else RecommendedUse.LIMITATION
            ),
            limitations=limitations,
            recommendations=[
                recommendation(
                    builder,
                    action=(
                        "Confirm the prediction time and verify that every retained "
                        "feature would be available at that time."
                    ),
                    recommendation_type="validation",
                    priority="high",
                    justification=(
                        "Internal holdout performance does not prove operational "
                        "feature availability or future generalisation."
                    ),
                )
            ],
            prohibited_interpretations=[
                "Do not claim causality from predictive performance.",
                "Do not claim deployment readiness.",
                "Do not claim future accuracy unless the validation was explicitly temporal.",
                "Do not imply excluded proxy features were used.",
            ],
        )

    except Exception as error:
        add_predictive_insufficiency(
            builder,
            task,
            (
                f"Predictive modelling for `{target_column}` was inconclusive "
                "because execution failed."
            ),
            {
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
            [
                f"Execution error: {type(error).__name__}: {error}",
            ],
        )


def infer_time_structure(
    timestamps: pd.Series,
) -> tuple[str, list[int], int]:
    differences = (
        timestamps.sort_values()
        .diff()
        .dropna()
        .dt.total_seconds()
    )

    if differences.empty:
        return "unknown", [], 20

    median_seconds = float(differences.median())

    if median_seconds <= 5_400:
        return "hourly_or_finer", [24, 168], 168

    if median_seconds <= 129_600:
        return "daily", [7], 28

    if median_seconds <= 3_456_000:
        return "monthly", [12], 12

    return "irregular_or_sparse", [], 20


def autoregressive_predictions(
    values: np.ndarray,
    train_end: int,
    test_start: int,
    test_end: int,
    lags: list[int],
) -> np.ndarray | None:
    usable_lags = sorted(set(lag for lag in lags if lag > 0))

    if not usable_lags:
        usable_lags = [1]

    maximum_lag = max(usable_lags)

    rows: list[list[float]] = []
    targets: list[float] = []

    for index in range(maximum_lag, train_end):
        feature_row = [values[index - lag] for lag in usable_lags]

        if not np.isfinite(feature_row).all() or not np.isfinite(values[index]):
            continue

        rows.append(feature_row)
        targets.append(values[index])

    if len(rows) < 40:
        return None

    x_train = np.asarray(rows[-50_000:], dtype=float)
    y_train = np.asarray(targets[-50_000:], dtype=float)

    model = Ridge(alpha=1.0)
    model.fit(x_train, y_train)

    test_rows: list[list[float]] = []

    for index in range(test_start, test_end):
        feature_row = [values[index - lag] for lag in usable_lags]

        if not np.isfinite(feature_row).all():
            return None

        test_rows.append(feature_row)

    return model.predict(np.asarray(test_rows, dtype=float))


def forecasting_analysis(
    bundle: DataBundle,
    task: InvestigationTask,
    builder: EvidenceBuilder,
    settings: Settings,
) -> None:
    table_name = task.table_name
    time_column = task.time_column
    target_column = task.target_column

    if (
        table_name not in bundle.tables
        or not time_column
        or not target_column
        or time_column not in bundle.tables[table_name].columns
        or target_column not in bundle.tables[table_name].columns
    ):
        builder.add(
            route=AnalysisRoute.FORECASTING,
            task_ids=[task.task_id],
            finding=(
                "Forecasting was not run because a valid time column and "
                "numeric target were not available."
            ),
            metrics={},
            source_tables=[table_name],
            source_columns=[
                column
                for column in [time_column, target_column]
                if column
            ],
            method="Forecast feasibility assessment.",
            validation_strategy=ValidationStrategy.NONE,
            practical_interpretation=(
                "The available plan does not support a validated forecast."
            ),
            strength_label="forecast_insufficiency",
            claim_permissions=[
                ClaimPermission.INSUFFICIENCY,
                ClaimPermission.METHODOLOGICAL,
            ],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.75,
            salience=0.75,
            recommended_use=RecommendedUse.LIMITATION,
            limitations=[
                "No validated forecast claim is available.",
            ],
        )
        return

    frame = bundle.tables[table_name][
        [time_column, target_column]
    ].copy()

    frame[time_column] = pd.to_datetime(
        frame[time_column],
        errors="coerce",
        utc=True,
    )
    frame[target_column] = pd.to_numeric(
        frame[target_column],
        errors="coerce",
    )

    frame = frame.dropna().sort_values(time_column)
    frame = frame.groupby(
        time_column,
        as_index=False,
    )[target_column].mean()

    granularity, seasonal_lags, minimum_test_points = infer_time_structure(
        frame[time_column]
    )

    maximum_lag = max([1, *seasonal_lags])

    if len(frame) < maximum_lag + minimum_test_points * 2:
        builder.add(
            route=AnalysisRoute.FORECASTING,
            task_ids=[task.task_id],
            finding=(
                f"Forecast validation for `{target_column}` was not run because "
                f"{len(frame):,} usable time points were insufficient for "
                "the inferred evaluation design."
            ),
            metrics={
                "usable_time_points": len(frame),
                "time_granularity": granularity,
                "minimum_test_points": minimum_test_points,
                "seasonal_lags": seasonal_lags,
            },
            source_tables=[table_name],
            source_columns=[time_column, target_column],
            method="Temporal coverage and seasonal-lag feasibility assessment.",
            validation_strategy=ValidationStrategy.NONE,
            practical_interpretation=(
                "The time series is too short for the selected rolling evaluation."
            ),
            strength_label="forecast_insufficiency",
            claim_permissions=[
                ClaimPermission.INSUFFICIENCY,
                ClaimPermission.METHODOLOGICAL,
            ],
            factual_confidence=1.0,
            methodological_strength=1.0,
            user_relevance=0.75,
            salience=0.75,
            recommended_use=RecommendedUse.LIMITATION,
            limitations=[
                "The series does not contain enough usable points for the "
                "required rolling evaluation windows."
            ],
        )
        return

    values = frame[target_column].to_numpy(dtype=float)
    length = len(values)

    test_window = max(minimum_test_points, int(length * 0.05))
    test_window = min(test_window, settings.max_forecast_test_points)
    test_window = min(test_window, max(minimum_test_points, length // 5))

    available_folds = max(
        1,
        (length - maximum_lag) // test_window - 1,
    )
    fold_count = min(settings.forecast_folds, available_folds)

    fold_results: list[dict[str, Any]] = []

    for fold_index in range(fold_count):
        test_end = length - (fold_count - fold_index - 1) * test_window
        test_start = test_end - test_window
        train_end = test_start

        if train_end <= maximum_lag:
            continue

        actual = values[test_start:test_end]

        predictions: dict[str, np.ndarray] = {
            "naive_last_value": values[test_start - 1:test_end - 1],
        }

        for lag in seasonal_lags:
            if test_start - lag >= 0:
                predictions[
                    f"seasonal_naive_lag_{lag}"
                ] = values[test_start - lag:test_end - lag]

        trend_model = LinearRegression()
        training_index = np.arange(train_end).reshape(-1, 1)
        testing_index = np.arange(test_start, test_end).reshape(-1, 1)

        trend_model.fit(training_index, values[:train_end])
        predictions["linear_trend"] = trend_model.predict(testing_index)

        autoregressive = autoregressive_predictions(
            values,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            lags=[1, *seasonal_lags],
        )

        if autoregressive is not None:
            predictions["autoregressive_ridge"] = autoregressive

        model_metrics = {
            model_name: float(mean_absolute_error(actual, prediction))
            for model_name, prediction in predictions.items()
        }

        fold_results.append(
            {
                "fold_id": f"FOLD_{fold_index + 1:02d}",
                "train_end": frame[time_column].iloc[train_end - 1].isoformat(),
                "test_start": frame[time_column].iloc[test_start].isoformat(),
                "test_end": frame[time_column].iloc[test_end - 1].isoformat(),
                "test_points": len(actual),
                "mae": model_metrics,
            }
        )

    if not fold_results:
        return

    model_names = sorted(
        {
            model_name
            for fold in fold_results
            for model_name in fold["mae"]
        }
    )

    mean_mae = {
        model_name: float(
            np.mean(
                [
                    fold["mae"][model_name]
                    for fold in fold_results
                    if model_name in fold["mae"]
                ]
            )
        )
        for model_name in model_names
    }

    baseline_names = [
        name
        for name in model_names
        if name.startswith("naive_") or name.startswith("seasonal_naive_")
    ]
    candidate_names = [
        name
        for name in model_names
        if name not in baseline_names
    ]

    best_baseline = min(
        baseline_names,
        key=lambda name: mean_mae[name],
    )
    best_candidate = min(
        candidate_names,
        key=lambda name: mean_mae[name],
    )

    baseline_mae = mean_mae[best_baseline]
    candidate_mae = mean_mae[best_candidate]

    relative_improvement = (
        (baseline_mae - candidate_mae) / baseline_mae
        if baseline_mae > 0
        else 0.0
    )

    fold_wins = sum(
        1
        for fold in fold_results
        if fold["mae"].get(best_candidate, float("inf"))
        < fold["mae"].get(best_baseline, float("inf"))
    )

    validated = bool(
        relative_improvement > 0.05
        and fold_wins >= math.ceil(len(fold_results) / 2)
    )

    if validated:
        finding = (
            f"`{best_candidate}` achieved mean rolling-origin MAE "
            f"{candidate_mae:.4g}, compared with {baseline_mae:.4g} for "
            f"the strongest naive baseline, `{best_baseline}`, across "
            f"{len(fold_results)} evaluation folds."
        )
    else:
        finding = (
            f"The best tested forecasting candidate, `{best_candidate}`, "
            f"had mean rolling-origin MAE {candidate_mae:.4g}, compared with "
            f"{baseline_mae:.4g} for the strongest naive baseline, "
            f"`{best_baseline}`. It did not provide a validated improvement."
        )

    builder.add(
        route=AnalysisRoute.FORECASTING,
        task_ids=[task.task_id],
        finding=finding,
        metrics={
            "target_column": target_column,
            "time_column": time_column,
            "time_granularity": granularity,
            "seasonal_lags": seasonal_lags,
            "fold_count": len(fold_results),
            "test_window_points": test_window,
            "fold_results": fold_results,
            "mean_mae": mean_mae,
            "best_baseline": best_baseline,
            "best_candidate": best_candidate,
            "baseline_mae": baseline_mae,
            "candidate_mae": candidate_mae,
            "relative_improvement": relative_improvement,
            "candidate_fold_wins": fold_wins,
        },
        source_tables=[table_name],
        source_columns=[time_column, target_column],
        method=(
            "Expanding-window rolling-origin, one-step-ahead evaluation "
            "against last-value and available seasonal-naive baselines."
        ),
        validation_strategy=ValidationStrategy.ROLLING_ORIGIN,
        practical_interpretation=(
            "The candidate is considered useful only when it consistently "
            "improves the strongest relevant naive baseline across folds."
        ),
        strength_label=(
            "validated_forecast"
            if validated
            else "forecast_not_better_than_baseline"
        ),
        claim_permissions=(
            [
                ClaimPermission.FORECAST,
                ClaimPermission.METHODOLOGICAL,
            ]
            if validated
            else [
                ClaimPermission.INSUFFICIENCY,
                ClaimPermission.METHODOLOGICAL,
            ]
        ),
        factual_confidence=0.97,
        methodological_strength=0.90,
        user_relevance=0.85,
        salience=0.85,
        recommended_use=(
            RecommendedUse.MAIN_FINDING
            if validated
            else RecommendedUse.LIMITATION
        ),
        limitations=[
            "This is an internal backtest, not a guarantee of live future performance.",
            "The evaluation is one-step-ahead and may not represent longer forecast horizons.",
            "External drivers and distribution shifts are not represented.",
        ],
        recommendations=[
            recommendation(
                builder,
                action=(
                    "Define the intended forecast horizon explicitly and repeat "
                    "evaluation for that horizon."
                ),
                recommendation_type="validation",
                priority="high",
                justification=(
                    "One-step-ahead performance is not interchangeable with "
                    "multi-step forecast performance."
                ),
            )
        ],
        prohibited_interpretations=[
            "Do not describe an unsuccessful candidate as a validated forecast.",
            "Do not claim certainty about future observations.",
            "Do not claim causal explanations for forecast behaviour.",
        ],
    )


def causal_feasibility_analysis(
    bundle: DataBundle,
    task: InvestigationTask,
    builder: EvidenceBuilder,
) -> None:
    table_name = task.table_name
    columns = set(
        bundle.tables.get(table_name, pd.DataFrame()).columns
    )

    exposure_available = bool(
        task.exposure_column
        and task.exposure_column in columns
    )
    outcome_available = bool(
        task.outcome_column
        and task.outcome_column in columns
    )
    time_available = bool(
        task.time_column
        and task.time_column in columns
    )
    confounders = [
        column
        for column in task.confounder_columns
        if column in columns
    ]

    builder.add(
        route=AnalysisRoute.CAUSAL_FEASIBILITY,
        task_ids=[task.task_id],
        finding=(
            "A causal conclusion is not authorised because the workflow has "
            "not verified randomisation, a natural experiment, a defensible "
            "adjustment set, or another identification strategy."
        ),
        metrics={
            "exposure_available": exposure_available,
            "outcome_available": outcome_available,
            "time_column_available": time_available,
            "proposed_confounder_count": len(confounders),
            "causal_claim_authorised": False,
        },
        source_tables=[table_name] if table_name in bundle.tables else [],
        source_columns=[
            column
            for column in [
                task.exposure_column,
                task.outcome_column,
                task.time_column,
                *confounders,
            ]
            if column
        ],
        method="Causal-feasibility checklist; no treatment-effect estimation.",
        practical_interpretation=(
            "Observed relationships may be described as associations, but the "
            "available design does not identify a causal effect."
        ),
        strength_label="causal_insufficiency",
        claim_permissions=[
            ClaimPermission.INSUFFICIENCY,
            ClaimPermission.METHODOLOGICAL,
        ],
        factual_confidence=1.0,
        methodological_strength=1.0,
        user_relevance=0.80,
        salience=0.80,
        recommended_use=RecommendedUse.LIMITATION,
        limitations=[
            "The presence of a date column does not establish temporal ordering.",
            "Observed association does not identify a causal effect.",
        ],
        prohibited_interpretations=[
            "Do not claim that one observed variable caused another.",
            "Do not claim a treatment effect.",
        ],
    )


def execute_plan(
    bundle: DataBundle,
    plan: ExecutionPlan,
    settings: Settings,
    semantic_map: InputSemanticMap | None = None,
) -> EvidenceLedger:
    builder = EvidenceBuilder(bundle.fingerprint)
    event_input = bool(
        (bundle.input_structure and bundle.input_structure.shape == InputShape.EVENT_RECORD)
        or (
            semantic_map is not None
            and semantic_map.input_shape == InputShape.EVENT_RECORD
            and semantic_map.confidence >= 0.7
        )
    )
    event_genre = plan.report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }

    if event_input:
        event_analysis(bundle, plan, builder, semantic_map)

    for route in plan.route_order:
        tasks = tasks_for_route(plan, route)

        if route == AnalysisRoute.DESCRIPTIVE:
            tabular_tasks = [
                task
                for task in tasks
                if task.capability
                not in {
                    EvidenceCapability.EVENT_OUTCOME,
                    EvidenceCapability.ENTITY_PERFORMANCE,
                    EvidenceCapability.RANKING,
                    EvidenceCapability.GROUP_COMPARISON,
                }
            ]
            if not (event_input and event_genre):
                descriptive_analysis(bundle, tabular_tasks, builder)

        elif route == AnalysisRoute.ASSOCIATION_COMPARISON:
            tabular_tasks = [
                task
                for task in tasks
                if task.capability != EvidenceCapability.GROUP_COMPARISON
                or not event_input
            ]
            if tabular_tasks and not (event_input and event_genre):
                association_analysis(
                    bundle,
                    tabular_tasks,
                    builder,
                    settings,
                )

        elif route == AnalysisRoute.PREDICTIVE:
            for task in tasks:
                predictive_analysis(
                    bundle,
                    task,
                    builder,
                    settings,
                )

        elif route == AnalysisRoute.FORECASTING:
            for task in tasks:
                forecasting_analysis(
                    bundle,
                    task,
                    builder,
                    settings,
                )

        elif route == AnalysisRoute.CAUSAL_FEASIBILITY:
            for task in tasks:
                causal_feasibility_analysis(
                    bundle,
                    task,
                    builder,
                )

    if not builder.items:
        builder.execution_notes.append(
            "The execution plan produced no evidence items."
        )

    return builder.build()
