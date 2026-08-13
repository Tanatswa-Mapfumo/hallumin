from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic_ai import UsageLimits

from .agents import (
    AgentDependencies,
    build_auditor_agent,
    build_data_understanding_agent,
    build_evidence_agent,
    build_insight_synthesis_agent,
    build_insight_verifier_agent,
    build_orchestrator_agent,
    build_verifier_agent,
    build_writer_agent,
    empty_insight_ledger,
    event_report_requested,
    fallback_execution_plan,
    fallback_understanding,
    materialise_insight_ledger,
    validate_insight_verification,
)
from .analytics import execute_plan
from .capabilities import (
    available_capabilities,
    normalise_event_evidence_queries,
)
from .audit import (
    accept_writer_quality_revision,
    apply_repair_proposal,
    apply_support_map_patches,
    assess_report_component_coverage,
    assess_genre_quality,
    augment_fact_ledger_for_report_coverage,
    assess_report_components,
    build_profile_support_registry,
    build_writer_content_requirements,
    build_writer_evidence_pack,
    compact_json,
    decide_release_status,
    deterministic_audit,
    deterministic_fact_candidate_scaffold,
    empty_fact_candidate_enrichment,
    fallback_audit_proposal,
    fallback_fact_candidates,
    fallback_verification,
    fallback_writer,
    finalise_fact_ledger,
    json_safe,
    materialise_writer_output,
    merge_fact_candidate_scaffold,
    merge_audit_proposal,
    normalise_strength_label,
    repair_spurious_missing_evidence_rejections,
    scope_fact_ledger_for_genre,
    validate_writer_output,
)
from .config import Settings
from .data import load_data, profile_data
from .narrative import build_event_narrative_plan
from .structure import build_structural_catalog
from .schemas import (
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    AnalysisRoute,
    ClaimPermission,
    CommunicationTask,
    DataUnderstanding,
    EvaluationFieldPolicy,
    EvidenceCapability,
    ExecutionPlan,
    ExternalTruthSource,
    FactCandidateSet,
    FactLedger,
    InputSemanticMap,
    InsightCandidateSet,
    InsightLedger,
    InsightObjective,
    InsightType,
    InsightVerificationResult,
    InvestigationTask,
    NarrativePlan,
    PipelineResult,
    ProfileSupportRecord,
    QualityStatus,
    ReportComponent,
    ReportGenre,
    ReportSelectionSource,
    RealisationPolicy,
    InputShape,
    InputRepresentationStatus,
    OutputForm,
    ReleaseStatus,
    RunManifest,
    VerificationResult,
    VerifiedFact,
    WriterAgentDraft,
    WriterEvidencePack,
    WriterOutput,
)


def infer_required_report_components(
    request: str,
) -> list[ReportComponent]:
    normalised = request.lower()
    general_understanding_request = bool(
        re.search(
            r"\b("
            r"understand|"
            r"overview|"
            r"summarise|summarize|"
            r"report findings|"
            r"strongest findings|"
            r"key findings|"
            r"explore"
            r")\b",
            normalised,
        )
    )

    if general_understanding_request:
        return [
            ReportComponent.DATASET_OVERVIEW,
            ReportComponent.DATA_QUALITY,
            ReportComponent.STRONGEST_RELATIONSHIPS,
            ReportComponent.LIMITATIONS_NEXT_STEPS,
        ]

    return []


EVENT_GENRES = {
    ReportGenre.EVENT_REPORT,
    ReportGenre.SPORTS_GAME_REPORT,
}
EVENT_CAPABILITIES = {
    EvidenceCapability.EVENT_OUTCOME,
    EvidenceCapability.ENTITY_PERFORMANCE,
    EvidenceCapability.RANKING,
    EvidenceCapability.GROUP_COMPARISON,
}


def build_orchestrator_prompt_context(
    *,
    understanding: DataUnderstanding,
    input_structure: Any | None,
    structural_catalog: list[Any],
) -> dict[str, Any]:
    """Expose semantic IDs to the planner without competing raw paths."""

    understanding_payload = understanding.model_dump(mode="json")
    semantic_map = understanding.semantic_map
    if semantic_map is None:
        return {
            "understanding": understanding_payload,
            "input_structure": input_structure,
            "structural_catalog": structural_catalog,
            "semantic_binding_catalog": [],
        }

    understanding_payload.pop("semantic_map", None)
    structure_payload = (
        input_structure.model_dump(mode="json")
        if hasattr(input_structure, "model_dump")
        else input_structure
    )
    if isinstance(structure_payload, dict):
        structure_payload = {
            **structure_payload,
            "nested_paths": [],
        }

    return {
        "understanding": understanding_payload,
        "input_structure": structure_payload,
        "structural_catalog": [],
        "semantic_binding_catalog": [
            {
                "binding_id": binding.binding_id,
                "table_name": binding.table_name,
                "label": binding.label,
                "role": binding.role.value,
                "level": binding.level.value,
                "analytical_function": (
                    binding.analytical_function.value
                    if binding.analytical_function is not None
                    else None
                ),
                "unit": binding.unit,
            }
            for binding in semantic_map.bindings
        ],
    }


def resolve_report_genre(
    *,
    request: str,
    planned_genre: ReportGenre,
    configured_genre: ReportGenre | None,
    input_structure: Any | None = None,
    semantic_map: InputSemanticMap | None = None,
) -> tuple[ReportGenre, ReportSelectionSource, float]:
    if event_report_requested(request):
        return (
            ReportGenre.EVENT_REPORT,
            ReportSelectionSource.EXPLICIT_USER_REQUEST,
            1.0,
        )
    if re.search(r"\bdata[- ]science report\b", request, re.IGNORECASE):
        return (
            ReportGenre.DATA_SCIENCE_REPORT,
            ReportSelectionSource.EXPLICIT_USER_REQUEST,
            1.0,
        )
    if re.search(r"\bdataset overview\b", request, re.IGNORECASE):
        return (
            ReportGenre.DATASET_OVERVIEW,
            ReportSelectionSource.EXPLICIT_USER_REQUEST,
            1.0,
        )
    if configured_genre is not None:
        return (
            configured_genre,
            ReportSelectionSource.EXPERIMENT_CONFIGURATION,
            1.0,
        )

    semantic_event = bool(
        semantic_map is not None
        and semantic_map.confidence >= 0.7
        and (
            semantic_map.input_shape == InputShape.EVENT_RECORD
            or semantic_map.recommended_report_genre in EVENT_GENRES
        )
    )
    structural_event = bool(
        input_structure is not None
        and input_structure.shape == InputShape.EVENT_RECORD
        and input_structure.confidence >= 0.7
    )
    if semantic_event or structural_event:
        return (
            ReportGenre.EVENT_REPORT,
            ReportSelectionSource.STRUCTURED_INFERENCE,
            (
                semantic_map.confidence
                if semantic_event and semantic_map is not None
                else input_structure.confidence
            ),
        )

    if re.search(
        r"\b(understand|explore|strongest findings|key findings|"
        r"report (?:its |the )?findings)\b",
        request,
        re.IGNORECASE,
    ):
        return (
            ReportGenre.DATA_SCIENCE_REPORT,
            ReportSelectionSource.FALLBACK,
            0.8,
        )

    if planned_genre in EVENT_GENRES:
        return (
            ReportGenre.EVENT_REPORT,
            ReportSelectionSource.STRUCTURED_INFERENCE,
            0.85,
        )
    return (
        planned_genre,
        ReportSelectionSource.STRUCTURED_INFERENCE,
        0.85,
    )


def report_contract_fields(
    genre: ReportGenre,
) -> dict[str, Any]:
    if genre in EVENT_GENRES:
        return {
            "communication_goal": (
                "Communicate the verified event result, leading performances "
                "major participant contrasts and any supplied event-context "
                "or score-progression evidence."
            ),
            "preferred_sections": [
                "Event overview",
                "Score progression",
                "Key performances",
                "Participant contrasts",
                "Scope limitations",
            ],
            "required_components": [],
            "required_content_slots": [
                "event_result",
                "event_context",
                "participant_record_context",
                "event_status",
                "score_progression",
                "event_sequence",
                "leading_performance",
                "main_contrast",
                "scope_limitations",
            ],
            "optional_content_slots": [
                "secondary_performance",
            ],
            "prohibited_claim_types": [
                "unsupported_chronology",
                "unsupported_milestone",
                "unsupported_historical_significance",
                "unsupported_causality",
            ],
            "include_negative_findings": False,
            "include_methodological_details": False,
        }

    if genre == ReportGenre.DATASET_OVERVIEW:
        return {
            "required_content_slots": ["dataset_scope"],
            "optional_content_slots": ["material_data_quality_issue"],
            "prohibited_claim_types": ["unsupported_causality"],
        }

    return {
        "required_content_slots": [
            "dataset_scope",
            "material_data_quality_issue",
            "strongest_analytical_finding",
            "limitation",
        ],
        "optional_content_slots": [],
        "prohibited_claim_types": ["unsupported_causality"],
    }


def task_contract_fields(
    *,
    genre: ReportGenre,
    communication_task: CommunicationTask | None,
    output_form: OutputForm | None,
    focus_scope: str | None,
) -> dict[str, Any]:
    if communication_task is None:
        if genre in EVENT_GENRES:
            communication_task = CommunicationTask.EVENT_REPORT
        elif genre == ReportGenre.DATASET_OVERVIEW:
            communication_task = CommunicationTask.DATASET_OVERVIEW
        else:
            communication_task = CommunicationTask.DATA_SCIENCE_REPORT

    if output_form is None:
        output_form = OutputForm.MULTI_PARAGRAPH_REPORT

    if communication_task == CommunicationTask.FOCUSED_TABLE_DESCRIPTION:
        return {
            "communication_task": communication_task,
            "output_form": output_form,
            "focus_scope": focus_scope or "focused_table_region",
            "allow_headings": False,
            "max_sentences": 1
            if output_form == OutputForm.ONE_SENTENCE
            else None,
            "max_paragraphs": 1,
            "require_complete_sentence": True,
            "realisation_policy": RealisationPolicy.CONCISE_TABLE_PROPOSITION,
            "communication_goal": (
                "Express the concise table-local relation conveyed by the "
                "selected cell or focused table region, using conservative "
                "cell-context wording only when the relation is ambiguous."
            ),
            "target_length_words": 40,
            "maximum_length_words": 80,
            "preferred_sections": [],
            "required_components": [],
            "required_content_slots": [
                "focused_table_region",
            ],
            "optional_content_slots": [
                "focused_table_relation",
                "focused_cell_context",
            ],
            "prohibited_claim_types": [
                "dataset_overview",
                "data_quality",
                "missingness",
                "correlation",
                "modelling",
                "unrelated_table_cells",
                "markdown_headings",
            ],
            "include_negative_findings": False,
            "include_methodological_details": False,
            "prioritisation_rule": (
                "Prefer a verified focused-table relation insight when the "
                "supplied page, section, row, header and source-text context "
                "support it. When multiple highlighted numeric values share "
                "the same header, prefer a scoped lower/higher contrast "
                "among the highlighted values over a table-wide rank claim; "
                "when a highlighted group label is paired with a highlighted "
                "record-like summary value, prefer the natural record "
                "proposition over a mechanical cell description; when a "
                "highlighted text cell appears under a meaningful column in "
                "a list page, prefer the natural list-page proposition over "
                "unrelated row details; when highlighted record groups are "
                "supplied, preserve all grouped highlighted records that "
                "contribute to the focused proposition; "
                "otherwise give the narrow selected-cell description."
            ),
        }

    if communication_task in {
        CommunicationTask.ATTRIBUTE_VERBALISATION,
        CommunicationTask.TRIPLE_VERBALISATION,
    }:
        task_label = (
            "attributes"
            if communication_task == CommunicationTask.ATTRIBUTE_VERBALISATION
            else "triples"
        )
        return {
            "communication_task": communication_task,
            "output_form": output_form,
            "focus_scope": focus_scope or "structured_record",
            "allow_headings": False,
            "max_sentences": 1
            if output_form == OutputForm.ONE_SENTENCE
            else 2,
            "max_paragraphs": 1,
            "require_complete_sentence": True,
            "realisation_policy": RealisationPolicy.NATURAL_REFERENCE_STYLE,
            "communication_goal": (
                f"Express all and only the supplied {task_label} as concise, "
                "fluent natural language without adding unsupported details."
            ),
            "target_length_words": 35,
            "maximum_length_words": 90,
            "preferred_sections": [],
            "required_components": [],
            "required_content_slots": [
                "structured_record_verbalisation",
            ],
            "optional_content_slots": [],
            "prohibited_claim_types": [
                "dataset_overview",
                "data_quality",
                "missingness",
                "correlation",
                "modelling",
                "unsupported_attribute",
                "unsupported_entity",
                "markdown_headings",
            ],
            "include_negative_findings": False,
            "include_methodological_details": False,
            "prioritisation_rule": (
                "Use every supplied attribute or triple that contributes to "
                "the requested short verbalisation. Prefer natural phrasing "
                "over mechanical key/value listing, but do not introduce "
                "facts absent from the structured record. For triple "
                "verbalisation, preserve the source relation order where "
                "natural and use compact predicate-preserving wording; do "
                "not add interpretive paraphrases or formatting changes that "
                "are not required by grammar. Preserve source digits, "
                "decimals and units exactly."
            ),
        }

    if (
        communication_task == CommunicationTask.EVENT_REPORT
        and focus_scope in {"event_recap", "reference_recap"}
    ):
        reference_recap_style = focus_scope == "reference_recap"
        return {
            "communication_task": communication_task,
            "output_form": output_form,
            "focus_scope": focus_scope,
            "allow_headings": not reference_recap_style,
            "max_sentences": None,
            "max_paragraphs": None,
            "require_complete_sentence": True,
            "realisation_policy": RealisationPolicy.EVENT_RECAP_STYLE,
            "communication_goal": (
                (
                    "Write a reference-style event recap from verified source "
                    "evidence: lead with the result, then integrate supplied "
                    "context, score progression, leading performances, major "
                    "participant contrasts and follow-up context when verified."
                )
                if reference_recap_style
                else (
                    "Write a coherent event recap from verified source "
                    "evidence: lead with the result, then integrate supplied "
                    "context, score progression, leading performances and "
                    "major participant contrasts. Keep the report event-first, "
                    "not a dataset profile."
                )
            ),
            "preferred_sections": []
            if reference_recap_style
            else [
                "Event overview",
                "Score progression",
                "Key performances",
                "Participant contrasts",
            ],
            "required_components": [],
            "required_content_slots": [
                "event_result",
                "event_context",
                "participant_record_context",
                "event_status",
                "score_progression",
                "event_sequence",
                "leading_performance",
                "main_contrast",
            ],
            "optional_content_slots": [
                "secondary_performance",
            ],
            "prohibited_claim_types": [
                "markdown_headings",
                "dataset_overview",
                "data_quality",
                "missingness",
                "correlation",
                "modelling",
                "unsupported_chronology",
                "unsupported_milestone",
                "unsupported_historical_significance",
                "unsupported_causality",
            ],
            "include_negative_findings": False,
            "include_methodological_details": False,
            "prioritisation_rule": (
                (
                    "Optimise for a fluent event recap: include the most "
                    "salient verified result, context, progression, "
                    "performances and contrasts. Keep factual caveats "
                    "internal unless needed to avoid a misleading claim. Do "
                    "not add a generic limitations section for reference-style "
                    "event recaps."
                )
                if reference_recap_style
                else (
                    "Optimise for a fluent event recap: include the most "
                    "salient verified result, context, progression, "
                    "performances and contrasts before secondary rankings. "
                    "Keep any visible caveat concise and event-scoped."
                )
            ),
        }

    return {
        "communication_task": communication_task,
        "output_form": output_form,
        "focus_scope": focus_scope,
        "realisation_policy": RealisationPolicy.STRICT_SOURCE_SURFACE,
    }


def infer_event_focus_scope(
    *,
    selected_genre: ReportGenre,
    selection_source: ReportSelectionSource,
    configured_communication_task: CommunicationTask | None,
    configured_output_form: OutputForm | None,
    configured_focus_scope: str | None,
    input_structure: Any | None,
    semantic_map: InputSemanticMap | None,
) -> str | None:
    if configured_focus_scope is not None:
        return configured_focus_scope
    if selected_genre not in EVENT_GENRES:
        return None
    if configured_communication_task is not None or configured_output_form is not None:
        return None
    if selection_source != ReportSelectionSource.STRUCTURED_INFERENCE:
        return None

    semantic_event = bool(
        semantic_map is not None
        and semantic_map.confidence >= 0.7
        and (
            semantic_map.input_shape == InputShape.EVENT_RECORD
            or semantic_map.recommended_report_genre in EVENT_GENRES
        )
    )
    structural_event = bool(
        input_structure is not None
        and input_structure.shape == InputShape.EVENT_RECORD
        and input_structure.confidence >= 0.7
    )
    if semantic_event or structural_event:
        return "event_recap"
    return None


SHORT_FORM_COMMUNICATION_TASKS = {
    CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
    CommunicationTask.ATTRIBUTE_VERBALISATION,
    CommunicationTask.TRIPLE_VERBALISATION,
}


def is_short_form_realisation_task(
    communication_task: CommunicationTask | None,
    output_form: OutputForm | None,
) -> bool:
    return bool(
        communication_task in SHORT_FORM_COMMUNICATION_TASKS
        or output_form
        in {
            OutputForm.ONE_SENTENCE,
            OutputForm.SHORT_TEXT,
            OutputForm.DIRECT_ANSWER,
        }
        and communication_task
        in SHORT_FORM_COMMUNICATION_TASKS
    )


def add_focused_table_capability_task(
    *,
    plan: ExecutionPlan,
    profile: Any,
    capabilities: list[EvidenceCapability],
    enable_insight_synthesis: bool,
) -> ExecutionPlan:
    if (
        plan.report_specification.communication_task
        != CommunicationTask.FOCUSED_TABLE_DESCRIPTION
    ):
        return plan

    if EvidenceCapability.FOCUSED_TABLE_REGION not in capabilities:
        return plan

    table_name = next(
        (
            table.table_name
            for table in profile.tables
            if any(column.name == "is_highlighted" for column in table.columns)
        ),
        profile.tables[0].table_name if profile.tables else "",
    )
    if not table_name:
        return plan

    columns = [
        "cell_value",
        "is_highlighted",
        "row_index",
        "column_index",
        "page_title",
        "section_title",
        "is_header",
    ]
    task = InvestigationTask(
        task_id="TASK_FOCUSED_TABLE_REGION",
        question=(
            "Which selected table cell or focused region should be described, "
            "and what local row, header and table context supports it?"
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        priority=5,
        table_name=table_name,
        columns=columns,
        capability=EvidenceCapability.FOCUSED_TABLE_REGION,
        input_fields=columns,
        expected_evidence_types=[
            "focused_table_region",
            "focused_cell_context",
        ],
        required_evidence=[
            "selected cell value",
            "row context",
            "header or table context when available",
        ],
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        answerability_note=(
            "The output should describe the focused table region only; broad "
            "dataset profiling and unrelated analytical routes are out of scope."
        ),
    )
    insight_objectives = []
    if enable_insight_synthesis:
        insight_objectives = [
            InsightObjective(
                objective_id="INSIGHT_FOCUSED_TABLE_RELATION",
                question=(
                    "What concise table-local proposition is expressed by "
                    "the highlighted cell or focused table region, using "
                    "only supplied page, section, row, header, highlighted "
                    "cell and source-text context, including scoped "
                    "lower/higher contrast among highlighted values when "
                    "supported and record-style propositions when a "
                    "highlighted group label is paired with a highlighted "
                    "record-like value, or list-page propositions when a "
                    "highlighted text cell is selected from a list table?"
                ),
                preferred_insight_types=[
                    InsightType.NARRATIVE_SUMMARY,
                ],
                relevant_task_ids=[
                    task.task_id,
                ],
                priority="main",
            )
        ]

    return plan.model_copy(
        update={
            "tasks": [task],
            "route_order": [AnalysisRoute.DESCRIPTIVE],
            "selected_capabilities": [
                EvidenceCapability.FOCUSED_TABLE_REGION,
            ],
            "evidence_queries": [],
            "insight_objectives": insight_objectives,
            "rationale": (
                "The controller selected a focused-table contract, so the "
                "plan is restricted to selected-cell evidence and local "
                "table-context relation synthesis."
            ),
        }
    )


def add_structured_record_capability_task(
    *,
    plan: ExecutionPlan,
    profile: Any,
    capabilities: list[EvidenceCapability],
    enable_insight_synthesis: bool,
) -> ExecutionPlan:
    if plan.report_specification.communication_task not in {
        CommunicationTask.ATTRIBUTE_VERBALISATION,
        CommunicationTask.TRIPLE_VERBALISATION,
    }:
        return plan

    if (
        EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
        not in capabilities
    ):
        return plan

    table_name = next(
        (
            table.table_name
            for table in profile.tables
            if {
                "attribute_name",
                "attribute_value",
            }.issubset({column.name for column in table.columns})
            or {
                "subject",
                "relation",
                "object",
            }.issubset({column.name for column in table.columns})
        ),
        profile.tables[0].table_name if profile.tables else "",
    )
    if not table_name:
        return plan

    columns = [
        "attribute_name",
        "attribute_value",
        "subject",
        "relation",
        "object",
        "source_text",
    ]
    task = InvestigationTask(
        task_id="TASK_STRUCTURED_RECORD_VERBALISATION",
        question=(
            "Which supplied attributes or triples must be verbalised, and "
            "what exact entities, relations and values do they contain?"
        ),
        route=AnalysisRoute.DESCRIPTIVE,
        priority=5,
        table_name=table_name,
        columns=columns,
        capability=EvidenceCapability.STRUCTURED_RECORD_VERBALISATION,
        input_fields=columns,
        expected_evidence_types=[
            "attribute_record",
            "triple_record",
            "structured_record",
        ],
        required_evidence=[
            "supplied attributes or triples",
            "entity, relation and value strings",
        ],
        claim_permissions=[ClaimPermission.DESCRIPTIVE],
        answerability_note=(
            "The output should verbalise the supplied structured record only; "
            "broad dataset profiling and analytical routes are out of scope."
        ),
    )
    insight_objectives = []
    if enable_insight_synthesis:
        insight_objectives = [
            InsightObjective(
                objective_id="INSIGHT_STRUCTURED_RECORD_VERBALISATION",
                question=(
                    "What concise natural-language proposition is expressed "
                    "by the supplied attributes or triples, using only the "
                    "given entity, relation and value strings?"
                ),
                preferred_insight_types=[
                    InsightType.NARRATIVE_SUMMARY,
                ],
                relevant_task_ids=[
                    task.task_id,
                ],
                priority="main",
            )
        ]

    return plan.model_copy(
        update={
            "tasks": [task],
            "route_order": [AnalysisRoute.DESCRIPTIVE],
            "selected_capabilities": [
                EvidenceCapability.STRUCTURED_RECORD_VERBALISATION,
            ],
            "evidence_queries": [],
            "insight_objectives": insight_objectives,
            "rationale": (
                "The controller selected a structured-record verbalisation "
                "contract, so the plan is restricted to supplied attribute "
                "or triple evidence."
            ),
        }
    )


def add_event_capability_tasks(
    *,
    plan: ExecutionPlan,
    request: str,
    profile: Any,
    audit_mode: AuditMode,
    settings: Settings,
    input_structure: Any,
    capabilities: list[EvidenceCapability],
    genre: ReportGenre,
) -> ExecutionPlan:
    if genre not in EVENT_GENRES:
        return plan

    event_fallback = fallback_execution_plan(
        request,
        profile,
        audit_mode,
        settings,
        input_structure=input_structure,
        available_capabilities=capabilities,
        report_genre_override=genre,
    )
    existing_capabilities = {
        task.capability
        for task in plan.tasks
        if task.capability is not None
    }
    additional_tasks = [
        task.model_copy(
            update={
                "task_id": (
                    "TASK_CAPABILITY_"
                    + task.capability.value.upper()
                )
            }
        )
        for task in event_fallback.tasks
        if task.capability in EVENT_CAPABILITIES
        and task.capability not in existing_capabilities
    ]
    tasks = [*plan.tasks, *additional_tasks]
    route_order = list(
        dict.fromkeys(
            [
                *plan.route_order,
                *[
                    task.route
                    for task in additional_tasks
                ],
            ]
        )
    )
    return plan.model_copy(
        update={
            "tasks": tasks,
            "route_order": route_order,
        }
    )


def should_use_deterministic_event_plan(
    *,
    controller_genre: ReportGenre,
    input_structure: Any,
    semantic_map: InputSemanticMap | None,
    capabilities: list[EvidenceCapability],
) -> bool:
    if controller_genre not in EVENT_GENRES:
        return False
    if input_structure is None:
        return False
    if input_structure.shape != InputShape.EVENT_RECORD:
        return False
    if input_structure.representation_status not in {
        InputRepresentationStatus.VALID,
        InputRepresentationStatus.VALID_WITH_WARNINGS,
    }:
        return False
    if getattr(input_structure, "confidence", 0.0) < 0.7:
        return False
    if semantic_map is None or not semantic_map.bindings:
        return False
    return bool(EVENT_CAPABILITIES & set(capabilities))


def exception_cause_chain(
    error: BaseException,
) -> list[str]:
    chain: list[str] = []
    current: BaseException | None = error
    seen: set[int] = set()

    while (
        current is not None
        and id(current) not in seen
    ):
        seen.add(id(current))

        message = getattr(
            current,
            "message",
            str(current),
        )

        chain.append(
            f"{type(current).__name__}: "
            f"{message}"
        )

        current = current.__cause__

    return chain


def _compact_writer_structured_value(
    value: Any,
    *,
    item_limit: int | None,
) -> Any:
    if isinstance(value, list):
        if item_limit is None:
            return [
                _compact_writer_structured_value(
                    item,
                    item_limit=item_limit,
                )
                for item in value
            ]

        omitted_count = max(0, len(value) - item_limit)
        compacted = [
            _compact_writer_structured_value(
                item,
                item_limit=item_limit,
            )
            for item in value[:item_limit]
        ]
        if omitted_count:
            compacted.append(
                {
                    "omitted_record_count": omitted_count,
                    "omission_reason": (
                        "Writer prompt compaction retained the highest-priority "
                        "records for this report-sized payload."
                    ),
                }
            )
        return compacted

    if isinstance(value, dict):
        return {
            key: _compact_writer_structured_value(
                nested_value,
                item_limit=item_limit,
            )
            for key, nested_value in value.items()
        }

    return value


def _compact_writer_fact(
    fact: VerifiedFact,
    *,
    item_limit: int | None,
) -> dict[str, Any]:
    payload = fact.model_dump(mode="json")
    payload["structured_values"] = _compact_writer_structured_value(
        payload.get("structured_values", {}),
        item_limit=item_limit,
    )
    entities = payload.get("entities")
    if isinstance(entities, list) and item_limit is not None:
        entity_limit = max(8, item_limit * 3)
        omitted_count = max(0, len(entities) - entity_limit)
        payload["entities"] = entities[:entity_limit]
        if omitted_count:
            payload["entities"].append(
                f"... {omitted_count} lower-priority entities omitted "
                "from the writer prompt"
            )
    return payload


def _compact_short_form_structured_values(
    values: Any,
) -> Any:
    if isinstance(values, dict):
        keep_keys = {
            "description_proposition",
            "records",
            "attributes",
            "highlighted_values",
            "header_context",
            "page_title",
            "section_title",
            "focused_record_relation",
            "focused_list_relation",
            "highlighted_role_value_pairs",
        }
        if all(isinstance(item, dict) for item in values.values()):
            return {
                evidence_id: {
                    key: nested_value
                    for key, nested_value in item.items()
                    if key in keep_keys
                    and nested_value not in (None, [], {}, "")
                }
                for evidence_id, item in values.items()
                if isinstance(item, dict)
            }
        return {
            key: _compact_short_form_structured_values(nested_value)
            for key, nested_value in values.items()
            if key in keep_keys
            or key.startswith("EVD_")
        }
    if isinstance(values, list):
        return [
            _compact_short_form_structured_values(item)
            for item in values
        ]
    return values


def _short_form_writer_fact(
    fact: VerifiedFact,
) -> dict[str, Any]:
    payload = fact.model_dump(mode="json")
    return {
        "fact_id": payload.get("fact_id"),
        "fact_summary": payload.get("fact_summary"),
        "evidence_ids": payload.get("evidence_ids", []),
        "source_capabilities": payload.get("source_capabilities", []),
        "structured_values": _compact_short_form_structured_values(
            payload.get("structured_values", {})
        ),
        "entities": payload.get("entities", []),
        "claim_permissions": payload.get("claim_permissions", []),
    }


def _writer_structured_item_limit(
    pack: WriterEvidencePack,
) -> int | None:
    maximum_words = pack.report_specification.maximum_length_words
    if maximum_words is None:
        return None

    event_report = pack.report_specification.genre in EVENT_GENRES
    if event_report:
        return max(12, min(60, maximum_words // 25))

    return max(3, min(10, maximum_words // 100))


def _event_report_writing_guidance(
    content_requirements: dict[str, Any] | None,
) -> dict[str, Any]:
    units = (
        content_requirements or {}
    ).get("units", [])
    supported_slots = [
        unit.get("unit_id")
        for unit in units
        if isinstance(unit, dict)
        and unit.get("candidate_fact_ids")
    ]
    realisation_policy = (
        content_requirements or {}
    ).get("realisation_policy", RealisationPolicy.STRICT_SOURCE_SURFACE.value)
    reference_recap_style = bool(
        (content_requirements or {}).get("reference_recap_style")
    )
    event_recap_style = bool(
        (content_requirements or {}).get("event_recap_style")
    )

    return {
        "realisation_policy": realisation_policy,
        "event_recap_style": event_recap_style,
        "reference_recap_style": reference_recap_style,
        "style": (
            (
                "Write a reference-style event recap from verified evidence "
                "as flowing prose without visible headings."
            )
            if reference_recap_style
            else (
                "Write a coherent event recap from verified evidence, not a "
                "flat-table profile or a mechanical ranking dump."
            )
        ),
        "content_priority_order": [
            "event_result",
            "event_context",
            "participant_record_context",
            "event_status",
            "score_progression",
            "event_sequence",
            "leading_performance",
            "main_contrast",
            "secondary_performance",
            "scope_limitations",
        ],
        "supported_content_slots": supported_slots,
        "opening_policy": (
            "Lead with the supported result or outcome when it exists. Add "
            "date, venue/location, status and participant record context in "
            "the opening only when those facts are verified."
        ),
        "narration_policy": (
            "Use verified sequence and score-progression facts to describe "
            "what happened in natural order. Use connective wording only "
            "for directly supported contrasts. Do not invent causes, "
            "momentum, runs, streaks, dominance, historical significance or "
            "chronology absent from verified facts."
        ),
        "selection_policy": (
            "There is no fixed number of findings. Cover required supported "
            "slots first, then add distinct high-salience verified facts and "
            "insights that improve the recap. Omit low-value mechanical "
            "rankings unless they clarify a stronger event point or the user "
            "requested exhaustive detail."
        ),
        "surface_policy": (
            "For reference-style recaps, do not use Markdown headings or a "
            "generic limitations paragraph. Keep caveats internal unless a "
            "visible caveat is necessary to prevent an unsupported inference."
            if reference_recap_style
            else (
                "Use the requested report structure while keeping event "
                "scope limitations concise and event-specific."
            )
        ),
        "avoid": [
            "wrapper row or column counts",
            "constant-column analysis",
            "missingness discussion",
            "correlation or regression language",
            "statistical-power or predictive-modelling discussion",
            "unsupported explanation of why the result occurred",
        ],
    }


def build_compact_writer_payload(
    pack: WriterEvidencePack,
    allow_hypotheses_in_report: bool = False,
    content_requirements: dict[str, Any] | None = None,
    narrative_plan: NarrativePlan | None = None,
) -> dict[str, Any]:
    facts_by_id = {
        fact.fact_id: fact
        for fact in [
            *pack.priority_facts,
            *pack.supporting_facts,
            *pack.limitation_facts,
        ]
    }
    evidence_by_id = {
        item.evidence_id: item
        for item in pack.evidence_ledger.items
    }
    strength_labels_by_fact_id = {
        fact_id: list(
            dict.fromkeys(
                normalise_strength_label(
                    evidence_by_id[evidence_id].strength_label
                )
                for evidence_id in fact.evidence_ids
                if evidence_id in evidence_by_id
            )
        )
        for fact_id, fact in facts_by_id.items()
    }
    structured_item_limit = _writer_structured_item_limit(pack)
    event_report = pack.report_specification.genre in EVENT_GENRES
    short_form = (
        pack.report_specification.communication_task
        in SHORT_FORM_COMMUNICATION_TASKS
    )

    if short_form:
        requirements = content_requirements or {}
        realisation_policy = requirements.get(
            "realisation_policy",
            pack.report_specification.realisation_policy.value,
        )
        may_normalise_identifiers = bool(
            requirements.get(
                "style_rewrite_permissions",
                {},
            ).get("may_normalise_identifier_separators")
        )
        return {
            "user_request": pack.user_request,
            "report_specification": {
                "genre": pack.report_specification.genre.value,
                "communication_task": (
                    pack.report_specification.communication_task.value
                ),
                "output_form": pack.report_specification.output_form.value,
                "focus_scope": pack.report_specification.focus_scope,
                "realisation_policy": realisation_policy,
                "allow_headings": pack.report_specification.allow_headings,
                "max_sentences": pack.report_specification.max_sentences,
                "max_paragraphs": pack.report_specification.max_paragraphs,
                "require_complete_sentence": (
                    pack.report_specification.require_complete_sentence
                ),
                "communication_goal": (
                    pack.report_specification.communication_goal
                ),
                "prohibited_claim_types": (
                    pack.report_specification.prohibited_claim_types
                ),
                "prioritisation_rule": (
                    pack.report_specification.prioritisation_rule
                ),
            },
            "content_requirements": requirements,
            "priority_facts": [
                _short_form_writer_fact(fact)
                for fact in pack.priority_facts
            ],
            "supporting_facts": [
                _short_form_writer_fact(fact)
                for fact in pack.supporting_facts
            ],
            "priority_verified_insights": pack.priority_verified_insights,
            "supporting_verified_insights": pack.supporting_verified_insights,
            "internal_prohibited_interpretations": (
                pack.internal_prohibited_interpretations
            ),
            "surface_form_policy": (
                "Preserve digits, percentages, decimals and units exactly. "
                "You may normalize harmless identifier separators such as "
                "underscores to spaces when this improves natural reference "
                "style and the entity remains recognisable."
                if may_normalise_identifiers
                else (
                    "Preserve source identifiers, digits, percentages, "
                    "decimals, units and compact alphanumeric forms exactly "
                    "unless only minor grammar is needed."
                )
            ),
        }

    payload = {
        "user_request": pack.user_request,
        "report_specification": (
            pack.report_specification
        ),
        "genre": pack.report_specification.genre,
        "audience": pack.report_specification.audience,
        "perspective": pack.report_specification.perspective,
        "communication_goal": (
            pack.report_specification.communication_goal
        ),
        "input_structure": pack.input_structure,
        "available_capabilities": pack.available_capabilities,
        "priority_verified_insights": (
            pack.priority_verified_insights
        ),
        "supporting_verified_insights": (
            pack.supporting_verified_insights
        ),
        "hypothesis_only_insights": (
            pack.insight_ledger.hypothesis_only_insights
            if allow_hypotheses_in_report
            else []
        ),
        "priority_facts": (
            [
                _compact_writer_fact(
                    fact,
                    item_limit=structured_item_limit,
                )
                for fact in pack.priority_facts
            ]
        ),
        "supporting_facts": (
            [
                _compact_writer_fact(
                    fact,
                    item_limit=structured_item_limit,
                )
                for fact in pack.supporting_facts
            ]
        ),
        "limitation_facts": (
            [
                _compact_writer_fact(
                    fact,
                    item_limit=structured_item_limit,
                )
                for fact in pack.limitation_facts
            ]
        ),
        "verified_strength_labels_by_fact_id": (
            strength_labels_by_fact_id
        ),
        "analytical_recommendations": (
            pack.analytical_recommendations
        ),
        "reader_facing_limitations": (
            pack.reader_facing_limitations
        ),
        "content_requirements": (
            content_requirements or {}
        ),
        "structured_value_compaction": (
            {
                "item_limit": structured_item_limit,
                "policy": (
                    "No list item limit is applied because no maximum word "
                    "ceiling is configured."
                    if structured_item_limit is None
                    else (
                        "Structured list values are compacted to fit the "
                        "configured maximum word ceiling."
                    )
                ),
            }
        ),
        "internal_prohibited_interpretations": (
            pack
            .internal_prohibited_interpretations
        ),
    }
    if event_report:
        payload["event_report_writing_guidance"] = (
            _event_report_writing_guidance(
                content_requirements,
            )
        )
        plan = narrative_plan or build_event_narrative_plan(
            pack,
            content_requirements,
        )
        if plan.applies:
            payload["narrative_plan"] = plan
    return payload


def build_compact_insight_payload(
    *,
    request: str,
    plan: ExecutionPlan,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
) -> dict[str, Any]:
    referenced_evidence_ids = {
        evidence_id
        for fact in fact_ledger.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }
    referenced_evidence = [
        item
        for item in evidence_ledger.items
        if item.evidence_id in referenced_evidence_ids
    ]

    return {
        "user_request": request,
        "report_specification": plan.report_specification,
        "frozen_insight_objectives": plan.insight_objectives,
        "writer_ready_verified_facts": fact_ledger.writer_ready_facts,
        "referenced_deterministic_evidence": referenced_evidence,
        "analytical_recommendations": [
            recommendation
            for item in referenced_evidence
            for recommendation in item.recommendations
        ],
        "prohibited_interpretations": list(
            dict.fromkeys(
                interpretation
                for fact in fact_ledger.writer_ready_facts
                for interpretation in fact.prohibited_interpretations
            )
        ),
        "selection_policy": {
            "candidate_count": "uncapped",
            "verified_insight_count": "uncapped",
            "report_word_ceiling": (
                plan.report_specification.maximum_length_words
            ),
            "min_facts_per_bounded_insight": (
                settings.min_facts_per_bounded_insight
            ),
            "min_insight_confidence": settings.min_insight_confidence,
            "min_insight_salience": settings.min_insight_salience,
            "allow_hypotheses_in_report": (
                settings.allow_hypotheses_in_report
            ),
            "focused_table_semantic_inference": (
                {
                    "expected_interpretation_level": "bounded_insight",
                    "expected_contribution": "descriptive_synthesis",
                    "instruction": (
                        "Infer a concise table-local relation from "
                        "highlighted cells, row context, headers, "
                        "page/section titles and source text only. Prefer the "
                        "relation conveyed by the table context over a "
                        "mechanical cell-location description when support is "
                        "clear. Do not use held-out references or outside "
                        "knowledge."
                    ),
                    "short_form_selection": (
                        "For one-sentence focused-table tasks, centre the "
                        "candidate on highlighted role/value pairs and the "
                        "most specific supported primary subject candidate. "
                        "Treat non-highlighted same-row values as context; "
                        "omit them unless they are required to disambiguate "
                        "the highlighted relation. Do not combine subject "
                        "candidates with co-entities into a joint subject "
                        "unless the supplied evidence explicitly represents "
                        "a combined entity. Use supplied highlighted-measure "
                        "comparisons when they support concise outcome-like "
                        "wording."
                    ),
                    "safe_fallback": (
                        "Use conservative selected-cell description if the "
                        "relation is ambiguous."
                    ),
                }
                if plan.report_specification.communication_task
                == CommunicationTask.FOCUSED_TABLE_DESCRIPTION
                else None
            ),
        },
    }


def build_writer_quality_revision_prompt(
    *,
    writer_pack: WriterEvidencePack,
    current_output: WriterOutput,
    missing_components: list[ReportComponent],
    quality_findings: list[str],
    content_requirements: dict[str, Any],
    settings: Settings,
) -> str:
    used_fact_ids = set(
        current_output.selected_fact_ids
    )

    unused_priority_facts = [
        fact
        for fact in writer_pack.priority_facts
        if fact.fact_id not in used_fact_ids
    ]
    used_insight_ids = {
        insight_id
        for support in current_output.sentence_support
        for insight_id in support.insight_ids
    }
    unused_verified_insights = [
        insight
        for insight in [
            *writer_pack.priority_verified_insights,
            *writer_pack.supporting_verified_insights,
        ]
        if insight.insight_id not in used_insight_ids
    ]

    current_word_count = len(
        re.findall(
            r"\b[\w'-]+\b",
            current_output.markdown,
        )
    )

    target_words = (
        writer_pack.report_specification
        .target_length_words
    )
    maximum_words = writer_pack.report_specification.maximum_length_words

    minimum_words = min(
        target_words,
        max(
            settings.minimum_report_word_floor,
            int(
                target_words
                * settings.minimum_report_word_ratio
            ),
            len(
                writer_pack
                .report_specification
                .required_components
            )
            * 45,
        ),
    )
    event_report = (
        writer_pack.report_specification.genre
        in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }
    )
    writing_goal = (
        "event-report writing"
        if event_report
        else "data-science writing"
    )
    component_guidance = (
        "required event result, context, performance, contrast, and scope slots"
        if event_report
        else "required dataset overview, quality, relationship, and limitation components"
    )

    return (
        "Revise the complete report once for task fulfilment and natural "
        f"{writing_goal} before factual audit.\n\n"
        "This is a Writer quality revision, not a factual repair.\n\n"
        "Do not merely rephrase the existing short report.\n"
        "Use unused verified facts and insights to cover missing sections and "
        "add non-duplicative synthesis.\n"
        + (
            f"Do not exceed {maximum_words} words.\n"
            if maximum_words is not None
            else (
                "No explicit maximum word count is configured; use the "
                "target length as guidance while prioritising supported "
                "coverage and concision.\n"
            )
        )
        + "Do not invent calculations or facts.\n"
        "Do not calculate statistics.\n"
        "Do not introduce new numbers, entities, categories, metadata, "
        "causal claims, prediction claims, forecast claims, or deployment "
        "claims.\n"
        "Do not expose internal control fields such as Finding:, Strength:, "
        "Important Note:, Interpretation Notes:, Recommended Use:, or Global "
        "Prohibited Interpretations.\n"
        f"Use {writing_goal} and consolidate shared caveats.\n"
        "Prefer strong and moderate evidence over small effects.\n"
        "Preserve each supplied qualitative strength classification exactly "
        "and consistently.\n"
        "Do not turn a possible explanation into an ordinary next step; it is "
        "a hypothesis and must follow the configured hypothesis policy.\n"
        "Return structured sections and sentences only. Do not return "
        "Markdown or a separate support map; the controller will create both "
        "deterministically.\n"
        "Every factual sentence must list its supporting fact IDs.\n\n"
        f"Current word count: {current_word_count}\n"
        f"Minimum useful word count: {minimum_words}\n"
        + (
            f"Maximum word count: {maximum_words}\n"
            if maximum_words is not None
            else "Maximum word count: not configured\n"
        )
        + f"Available priority facts: {len(writer_pack.priority_facts)}\n"
        f"Unused priority facts: {len(unused_priority_facts)}\n\n"
        f"Unused verified insights: {len(unused_verified_insights)}\n\n"
        "Controller-enforced content requirements:\n"
        + compact_json(content_requirements)
        + "\n\n"
        "Missing components:\n"
        + (
            "\n".join(
                f"- {component.value}"
                for component in missing_components
            )
            if missing_components
            else "- None"
        )
        + "\n\nQuality findings:\n"
        + (
            "\n".join(
                f"- {finding}"
                for finding in quality_findings
            )
            if quality_findings
            else "- None"
        )
        + "\n\nUnused verified priority facts:\n"
        + f"\nUse verified support to cover the {component_guidance}.\n"
        + compact_json(unused_priority_facts)
        + "\n\nUnused verified insights:\n"
        + compact_json(unused_verified_insights)
        + "\n\nCompact Writer evidence pack:\n"
        + compact_json(
            build_compact_writer_payload(
                writer_pack,
                settings.allow_hypotheses_in_report,
                content_requirements,
            )
        )
        + "\n\nCurrent Writer output:\n"
        + compact_json(current_output)
    )

class ArtifactStore:
    def __init__(self, base_directory: Path, run_id: str):
        self.run_directory = base_directory / run_id
        self.run_directory.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.run_directory / "trace.jsonl"

    @staticmethod
    def create_run_id(fingerprint: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{timestamp}_{fingerprint[:10]}"

    def save_json(self, filename: str, value: Any) -> Path:
        path = self.run_directory / filename
        path.write_text(
            json.dumps(
                json_safe(value),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    def save_text(self, filename: str, text: str) -> Path:
        path = self.run_directory / filename
        path.write_text(text, encoding="utf-8")
        return path

    def trace(
        self,
        stage: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": stage,
            "status": status,
            "details": json_safe(details or {}),
        }

        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(event, ensure_ascii=False) + "\n"
            )


class Table2TextWorkflow:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings.from_env()
        if not isinstance(self.settings.output_dir, Path):
            self.settings = self.settings.__class__(
                **{
                    **self.settings.__dict__,
                    "output_dir": Path(self.settings.output_dir),
                }
            )

        self.data_understanding_agent = None
        self.orchestrator_agent = None
        self.evidence_agent = None
        self.verifier_agent = None
        self.evidence_insight_synthesis_agent = None
        self.verifier_insight_verification_agent = None
        self.writer_agent = None
        self.auditor_agent = None

        if self.settings.use_llm:
            self.data_understanding_agent = build_data_understanding_agent(
                self.settings
            )
            self.orchestrator_agent = build_orchestrator_agent(self.settings)
            self.evidence_agent = build_evidence_agent(self.settings)
            self.verifier_agent = build_verifier_agent(self.settings)
            self.evidence_insight_synthesis_agent = (
                build_insight_synthesis_agent(self.settings)
            )
            self.verifier_insight_verification_agent = (
                build_insight_verifier_agent(self.settings)
            )
            self.writer_agent = build_writer_agent(self.settings)
            self.auditor_agent = build_auditor_agent(self.settings)

    def usage_limits(self) -> UsageLimits:
        return UsageLimits(
            request_limit=self.settings.max_agent_requests,
            total_tokens_limit=self.settings.max_total_tokens,
        )

    async def run_agent_or_fallback(
        self,
        *,
        stage: str,
        agent: Any,
        prompt: str,
        dependencies: AgentDependencies,
        fallback: Callable[[], Any],
        store: ArtifactStore,
    ) -> Any:
        if not self.settings.use_llm:
            store.trace(
                stage,
                "fallback",
                {"reason": "LLM execution disabled"},
            )
            return fallback()

        try:
            result = await agent.run(
                prompt,
                deps=dependencies,
                usage_limits=self.usage_limits(),
            )

            usage = getattr(result, "usage", None)

            store.trace(
                stage,
                "completed",
                {"usage": str(usage)},
            )

            return result.output

        except Exception as error:
            store.trace(
                stage,
                "fallback",
                {
                    "reason": (
                        f"{type(error).__name__}: {error}"
                    ),
                    "cause_chain": (
                        exception_cause_chain(
                            error
                        )
                    ),
                },
            )
            return fallback()

    async def run_optional_insight_agent(
        self,
        *,
        stage: str,
        agent: Any,
        prompt: str,
        dependencies: AgentDependencies,
        store: ArtifactStore,
    ) -> tuple[Any | None, str | None]:
        if not self.settings.use_llm or agent is None:
            reason = "LLM execution disabled"
            store.trace(
                stage,
                "skipped",
                {"reason": reason},
            )
            return None, reason

        try:
            result = await agent.run(
                prompt,
                deps=dependencies,
                usage_limits=self.usage_limits(),
            )
            usage = getattr(result, "usage", None)
            store.trace(
                stage,
                "completed",
                {"usage": str(usage)},
            )
            return result.output, None
        except Exception as error:
            reason = f"{type(error).__name__}: {error}"
            store.trace(
                stage,
                "fallback",
                {
                    "reason": reason,
                    "cause_chain": exception_cause_chain(error),
                },
            )
            return None, reason

    async def audit_once(
        self,
        *,
        run_id: str,
        writer_output: WriterOutput,
        fact_ledger: Any,
        evidence_ledger: Any,
        insight_ledger: InsightLedger,
        profile_support_records: list[
            ProfileSupportRecord
        ],
        plan: ExecutionPlan,
        audit_mode: AuditMode,
        external_truth_sources: list[ExternalTruthSource],
        revision_round: int,
        store: ArtifactStore,
        stage_name: str,
    ) -> tuple[AuditReport, AuditRepairProposal, WriterOutput]:
        deterministic_pre_patch = deterministic_audit(
            writer_output=writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=revision_round,
            report_specification=plan.report_specification,
            settings=self.settings,
            profile_support_records=profile_support_records,
            insight_ledger=insight_ledger,
        )

        if revision_round == 0:
            pre_patch_audit_name = (
                "10_initial_audit_pre_profile_patch.json"
            )
            support_patch_name = (
                "10_initial_support_map_patches.json"
            )
            profile_patched_name = (
                "10_initial_profile_patched_output.json"
            )
        else:
            pre_patch_audit_name = (
                "14_post_repair_audit_pre_profile_patch"
                f"_round_{revision_round}.json"
            )
            support_patch_name = (
                "14_post_repair_support_map_patches"
                f"_round_{revision_round}.json"
            )
            profile_patched_name = (
                "14_post_repair_profile_patched_output"
                f"_round_{revision_round}.json"
            )

        store.save_json(
            pre_patch_audit_name,
            deterministic_pre_patch,
        )
        store.save_json(
            support_patch_name,
            deterministic_pre_patch.support_map_patches,
        )

        profile_patched_output = writer_output

        if deterministic_pre_patch.support_map_patches:
            profile_patched_output = apply_support_map_patches(
                writer_output,
                deterministic_pre_patch.support_map_patches,
                {
                    record.support_id
                    for record in profile_support_records
                },
            )

        store.save_json(
            profile_patched_name,
            profile_patched_output,
        )

        deterministic = deterministic_audit(
            writer_output=profile_patched_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=revision_round,
            report_specification=plan.report_specification,
            settings=self.settings,
            profile_support_records=profile_support_records,
            insight_ledger=insight_ledger,
        ).model_copy(
            update={
                "support_map_patches": (
                    deterministic_pre_patch
                    .support_map_patches
                )
            }
        )

        deterministic_annotation_ids = [
            annotation.annotation_id
            for annotation in deterministic.annotations
        ]
        deterministic_serious_annotation_ids = [
            annotation.annotation_id
            for annotation in deterministic.annotations
            if annotation.severity.value
            in {"high", "critical"}
        ]
        short_form_output = (
            plan.report_specification.communication_task
            in SHORT_FORM_COMMUNICATION_TASKS
        )

        if (
            short_form_output
            and deterministic.decision == AuditDecision.PASS
            and not deterministic_serious_annotation_ids
        ):
            proposal = fallback_audit_proposal(deterministic)
            store.trace(
                stage_name,
                "skipped",
                {
                    "reason": (
                        "Short-form output passed deterministic audit; "
                        "LLM repair audit was skipped to avoid a large "
                        "one-sentence audit prompt."
                    ),
                    "communication_task": (
                        plan.report_specification.communication_task.value
                    ),
                    "deterministic_annotation_count": len(
                        deterministic.annotations
                    ),
                },
            )
            return (
                merge_audit_proposal(deterministic, proposal),
                proposal,
                profile_patched_output,
            )

        prompt = (
            "Audit this report independently and propose targeted repairs "
            "for high-confidence factual errors.\n\n"
            "User objective:\n"
            + plan.objective
            + "\n\nReport specification:\n"
            + compact_json(plan.report_specification)
            + "\n\nWriter output:\n"
            + compact_json(profile_patched_output)
            + "\n\nVerified fact ledger:\n"
            + compact_json(fact_ledger)
            + "\n\nEvidence ledger:\n"
            + compact_json(evidence_ledger)
            + "\n\nVerified insight ledger:\n"
            + compact_json(insight_ledger)
            + "\n\nDeterministic profile support registry:\n"
            + compact_json(profile_support_records)
            + "\n\nDeterministic pre-audit:\n"
            + compact_json(deterministic)
            + "\n\nExternal truth sources:\n"
            + compact_json(external_truth_sources)
            + "\n\nGenerate no more than "
            + str(self.settings.repair_candidates_per_sentence)
            + " repair candidates for each flagged sentence."
        )

        proposal = await self.run_agent_or_fallback(
            stage=stage_name,
            agent=self.auditor_agent,
            prompt=prompt,
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "report_text": profile_patched_output.markdown,
                    "fact_ledger": fact_ledger.model_dump(mode="json"),
                    "evidence_ledger": evidence_ledger.model_dump(
                        mode="json"
                    ),
                    "insight_ledger": insight_ledger.model_dump(
                        mode="json"
                    ),
                    "valid_fact_ids": [
                        fact.fact_id
                        for fact in fact_ledger.writer_ready_facts
                    ],
                    "valid_evidence_ids": [
                        item.evidence_id
                        for item in evidence_ledger.items
                    ],
                    "valid_profile_support_ids": [
                        record.support_id
                        for record in profile_support_records
                    ],
                    "valid_insight_ids": [
                        insight.insight_id
                        for insight in insight_ledger.verified_insights
                    ],
                    "verified_main_insight_ids": [
                        insight.insight_id
                        for insight in insight_ledger.verified_insights
                    ],
                    "hypothesis_only_insight_ids": [
                        insight.insight_id
                        for insight in (
                            insight_ledger.hypothesis_only_insights
                        )
                    ],
                    "insight_statements": {
                        insight.insight_id: insight.statement
                        for insight in [
                            *insight_ledger.verified_insights,
                            *insight_ledger.hypothesis_only_insights,
                        ]
                    },
                    "insight_source_fact_ids": {
                        insight.insight_id: insight.source_fact_ids
                        for insight in [
                            *insight_ledger.verified_insights,
                            *insight_ledger.hypothesis_only_insights,
                        ]
                    },
                    "insight_source_evidence_ids": {
                        insight.insight_id: insight.source_evidence_ids
                        for insight in [
                            *insight_ledger.verified_insights,
                            *insight_ledger.hypothesis_only_insights,
                        ]
                    },
                    "sentence_insight_ids": {
                        support.sentence_text: support.insight_ids
                        for support in profile_patched_output.sentence_support
                    },
                    "allow_hypotheses_in_report": (
                        self.settings.allow_hypotheses_in_report
                    ),
                    "report_genre": plan.report_specification.genre.value,
                    "report_perspective": (
                        plan.report_specification.perspective.value
                    ),
                    "deterministic_annotation_ids": (
                        deterministic_annotation_ids
                    ),
                    "deterministic_serious_annotation_ids": (
                        deterministic_serious_annotation_ids
                    ),
                    "deterministic_annotation_sentences": [
                        annotation.sentence
                        for annotation in deterministic.annotations
                    ],
                },
            ),
            fallback=lambda: fallback_audit_proposal(
                deterministic
            ),
            store=store,
        )

        proposal = AuditRepairProposal.model_validate(proposal)
        merged = merge_audit_proposal(deterministic, proposal)

        return merged, proposal, profile_patched_output

    async def run(
        self,
        inputs: list[str | Path],
        request: str,
        *,
        audit_mode: AuditMode = AuditMode.INTERNAL,
        external_truth_sources: list[ExternalTruthSource] | None = None,
        evaluation_field_policy: EvaluationFieldPolicy | None = None,
        report_genre: ReportGenre | None = None,
        communication_task: CommunicationTask | None = None,
        output_form: OutputForm | None = None,
        focus_scope: str | None = None,
    ) -> PipelineResult:
        external_truth_sources = external_truth_sources or []

        data_bundle = load_data(
            inputs,
            evaluation_field_policy=evaluation_field_policy,
        )
        input_structure = data_bundle.input_structure
        capabilities = available_capabilities(data_bundle)
        structural_catalog = build_structural_catalog(data_bundle.structured_inputs)
        representation_eligible = bool(
            input_structure
            and input_structure.representation_status
            in {
                InputRepresentationStatus.VALID,
                InputRepresentationStatus.VALID_WITH_WARNINGS,
            }
        )
        profile = profile_data(data_bundle)
        profile_support_records = (
            build_profile_support_registry(
                profile
            )
        )

        run_id = ArtifactStore.create_run_id(
            data_bundle.fingerprint
        )
        store = ArtifactStore(
            self.settings.output_dir,
            run_id,
        )

        store.save_json("00_input_structure.json", input_structure)
        store.save_json(
            "00_evaluation_field_policy.json",
            data_bundle.evaluation_field_policy,
        )
        store.save_json("00_available_capabilities.json", capabilities)
        store.save_json(
            "00_structural_catalog.json",
            structural_catalog,
        )

        models = {
            role: self.settings.model_for(role)
            for role in [
                "data_understanding",
                "orchestrator",
                "evidence",
                "verifier",
                "writer",
                "auditor",
            ]
        }

        initial_manifest_genre = (
            ReportGenre.EVENT_REPORT
            if event_report_requested(request)
            else report_genre or ReportGenre.DATA_SCIENCE_REPORT
        )
        initial_manifest_task = (
            communication_task
            or (
                CommunicationTask.EVENT_REPORT
                if initial_manifest_genre in EVENT_GENRES
                else CommunicationTask.DATA_SCIENCE_REPORT
            )
        )
        short_form_realisation_task = is_short_form_realisation_task(
            initial_manifest_task,
            output_form or OutputForm.MULTI_PARAGRAPH_REPORT,
        ) and not self.settings.force_llm_short_form_writer
        manifest = RunManifest(
            run_id=run_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            input_paths=[
                str(path)
                for path in data_bundle.source_paths
            ],
            request=request,
            fingerprint=data_bundle.fingerprint,
            use_llm=self.settings.use_llm,
            audit_mode=audit_mode,
            models=models,
            input_representation_status=(
                input_structure.representation_status
                if input_structure is not None
                else InputRepresentationStatus.INVALID
            ),
            report_genre=initial_manifest_genre,
            communication_task=initial_manifest_task,
            output_form=output_form or OutputForm.MULTI_PARAGRAPH_REPORT,
            focus_scope=focus_scope,
        )

        store.save_json("00_manifest.json", manifest)
        store.save_json("01_profile.json", profile)
        store.save_json(
            "02_profile_support_registry.json",
            profile_support_records,
        )

        table_names = [
            table.table_name
            for table in profile.tables
        ]
        columns = {
            table.table_name: [
                column.name
                for column in table.columns
            ]
            for table in profile.tables
        }

        if short_form_realisation_task:
            store.trace(
                "data_understanding",
                "skipped",
                {
                    "reason": (
                        "Short-form verbalisation uses deterministic input "
                        "structure and capability extraction instead of the "
                        "general analytical Data Understanding agent."
                    ),
                    "communication_task": initial_manifest_task.value,
                },
            )
            understanding = fallback_understanding(profile)
        else:
            understanding = await self.run_agent_or_fallback(
                stage="data_understanding",
                agent=self.data_understanding_agent,
                prompt=(
                    "Create a data understanding and analytical-risk report.\n\n"
                    "Input structure:\n"
                    + compact_json(input_structure)
                    + "\n\nSanitized structural field catalog:\n"
                    + compact_json(structural_catalog)
                    + "\n\nSanitized data profile:\n"
                    + compact_json(profile)
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fingerprint": profile.fingerprint,
                        "table_names": table_names,
                        "columns": columns,
                        "input_structure": (
                            input_structure.model_dump(mode="json")
                            if input_structure is not None
                            else None
                        ),
                        "structural_catalog": [
                            field.model_dump(mode="json") for field in structural_catalog
                        ],
                        "semantic_map_required": bool(structural_catalog),
                    },
                ),
                fallback=lambda: fallback_understanding(profile),
                store=store,
            )
        understanding = DataUnderstanding.model_validate(understanding)
        store.save_json("02_understanding.json", understanding)
        semantic_map = understanding.semantic_map
        store.save_json("02_semantic_map.json", semantic_map)
        capabilities = available_capabilities(
            data_bundle,
            semantic_map,
        )
        store.save_json(
            "02_available_capabilities.json",
            capabilities,
        )
        inferred_genre = (
            semantic_map.recommended_report_genre
            if semantic_map is not None and semantic_map.recommended_report_genre is not None
            else ReportGenre.DATA_SCIENCE_REPORT
        )
        (
            controller_genre,
            _,
            _,
        ) = resolve_report_genre(
            request=request,
            planned_genre=inferred_genre,
            configured_genre=report_genre,
            input_structure=input_structure,
            semantic_map=semantic_map,
        )
        controller_task_contract = task_contract_fields(
            genre=controller_genre,
            communication_task=communication_task,
            output_form=output_form,
            focus_scope=focus_scope,
        )
        planner_context = build_orchestrator_prompt_context(
            understanding=understanding,
            input_structure=input_structure,
            structural_catalog=structural_catalog,
        )

        deterministic_event_plan = should_use_deterministic_event_plan(
            controller_genre=controller_genre,
            input_structure=input_structure,
            semantic_map=semantic_map,
            capabilities=capabilities,
        )
        if short_form_realisation_task:
            store.trace(
                "orchestration_and_planning",
                "skipped",
                {
                    "reason": (
                        "Short-form verbalisation uses the controller "
                        "contract and deterministic capability task instead "
                        "of the general LLM Orchestrator."
                    ),
                    "selected_report_genre": controller_genre.value,
                    "communication_task": initial_manifest_task.value,
                    "available_capabilities": [
                        capability.value for capability in capabilities
                    ],
                },
            )
            plan = fallback_execution_plan(
                request,
                profile,
                audit_mode,
                self.settings,
                input_structure=input_structure,
                available_capabilities=capabilities,
                report_genre_override=controller_genre,
            )
        elif deterministic_event_plan:
            store.trace(
                "orchestration_and_planning",
                "skipped",
                {
                    "reason": (
                        "High-confidence event structure uses the generic "
                        "deterministic capability plan instead of the LLM "
                        "Orchestrator retry path."
                    ),
                    "selected_report_genre": controller_genre.value,
                    "input_shape": input_structure.shape.value,
                    "available_event_capabilities": [
                        capability.value
                        for capability in capabilities
                        if capability in EVENT_CAPABILITIES
                    ],
                },
            )
            plan = fallback_execution_plan(
                request,
                profile,
                audit_mode,
                self.settings,
                input_structure=input_structure,
                available_capabilities=capabilities,
                report_genre_override=controller_genre,
            )
        else:
            plan = await self.run_agent_or_fallback(
                stage="orchestration_and_planning",
                agent=self.orchestrator_agent,
                prompt=(
                    "User objective:\n"
                    + request
                    + "\n\nData profile:\n"
                    + compact_json(profile)
                    + "\n\nData understanding:\n"
                    + compact_json(planner_context["understanding"])
                    + "\n\nInput structure:\n"
                    + compact_json(planner_context["input_structure"])
                    + "\n\nSanitized structural field catalog:\n"
                    + compact_json(planner_context["structural_catalog"])
                    + "\n\nID-only semantic binding catalogue:\n"
                    + compact_json(planner_context["semantic_binding_catalog"])
                    + "\nUse only `binding_id` values from that catalogue in all "
                    "evidence-query binding fields. Raw paths are deliberately "
                    "unavailable for semantic query planning.\n"
                    + "\n\nAvailable evidence capabilities:\n"
                    + compact_json(capabilities)
                    + "\n\nController-selected report genre:\n"
                    + controller_genre.value
                    + "\n\nController-selected task/output contract:\n"
                    + compact_json(controller_task_contract)
                    + "\n\nConfigured report genre override:\n"
                    + (report_genre.value if report_genre else "none")
                    + "\n\nAudit mode:\n"
                    + audit_mode.value
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "table_names": table_names,
                        "columns": columns,
                        "user_request": request,
                        "allow_experimental_targets": (
                            self.settings.allow_experimental_targets
                        ),
                        "available_capabilities": [
                            capability.value
                            for capability in capabilities
                        ],
                        "event_genre_allowed": (
                            controller_genre in EVENT_GENRES
                        ),
                        "selected_report_genre": controller_genre.value,
                        "selected_task_contract": controller_task_contract,
                        "semantic_map": (
                            semantic_map.model_dump(mode="json")
                            if semantic_map is not None
                            else None
                        ),
                        "structural_catalog": [
                            field.model_dump(mode="json")
                            for field in structural_catalog
                        ],
                        "enable_insight_synthesis": (
                            self.settings.enable_insight_synthesis
                        ),
                    },
                ),
                fallback=lambda: fallback_execution_plan(
                    request,
                    profile,
                    audit_mode,
                    self.settings,
                    input_structure=input_structure,
                    available_capabilities=capabilities,
                    report_genre_override=controller_genre,
                ),
                store=store,
            )

        plan = ExecutionPlan.model_validate(plan)
        (
            selected_genre,
            selection_source,
            selection_confidence,
        ) = resolve_report_genre(
            request=request,
            planned_genre=plan.report_specification.genre,
            configured_genre=report_genre,
            input_structure=input_structure,
            semantic_map=semantic_map,
        )
        resolved_focus_scope = infer_event_focus_scope(
            selected_genre=selected_genre,
            selection_source=selection_source,
            configured_communication_task=communication_task,
            configured_output_form=output_form,
            configured_focus_scope=focus_scope,
            input_structure=input_structure,
            semantic_map=semantic_map,
        )
        contract_fields = {
            **report_contract_fields(selected_genre),
            **task_contract_fields(
                genre=selected_genre,
                communication_task=communication_task,
                output_form=output_form,
                focus_scope=resolved_focus_scope,
            ),
        }
        required_components = (
            contract_fields.get("required_components", [])
            if (
                selected_genre in EVENT_GENRES
                or contract_fields.get("communication_task")
                in {
                    CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
                    CommunicationTask.ATTRIBUTE_VERBALISATION,
                    CommunicationTask.TRIPLE_VERBALISATION,
                }
            )
            else infer_required_report_components(request)
        )
        report_specification = plan.report_specification.model_copy(
            update={
                "report_purpose": request,
                "genre": selected_genre,
                "selection_source": selection_source,
                "selection_confidence": selection_confidence,
                "target_length_words": (
                    plan.report_specification.target_length_words
                ),
                "maximum_length_words": (
                    self.settings.writer_max_words
                ),
                "maximum_main_findings": (
                    self.settings.writer_max_main_findings
                ),
                "maximum_supporting_facts": (
                    self.settings.writer_supporting_fact_limit
                ),
                "required_components": list(
                    dict.fromkeys(
                        [
                            *plan.report_specification.required_components,
                            *required_components,
                        ]
                    )
                ),
                **contract_fields,
            }
        )
        selected_capabilities = [
            capability
            for capability in capabilities
            if (
                (
                    report_specification.communication_task
                    == CommunicationTask.FOCUSED_TABLE_DESCRIPTION
                    and capability
                    == EvidenceCapability.FOCUSED_TABLE_REGION
                )
                or (
                    report_specification.communication_task
                    != CommunicationTask.FOCUSED_TABLE_DESCRIPTION
                    and (
                        selected_genre not in EVENT_GENRES
                        or capability
                        in {
                            EvidenceCapability.DATASET_PROFILE,
                            *EVENT_CAPABILITIES,
                        }
                    )
                )
            )
        ]
        plan = plan.model_copy(
            update={
                "objective": request,
                "report_specification": report_specification,
                "available_capabilities": capabilities,
                "selected_capabilities": selected_capabilities,
                "audit_mode": audit_mode,
                "revision_limit": min(
                    plan.revision_limit,
                    self.settings.max_revision_rounds,
                ),
                "maximum_facts": None,
                "insight_objectives": (
                    plan.insight_objectives
                    if self.settings.enable_insight_synthesis
                    else []
                ),
                "frozen": True,
            }
        )
        plan = add_event_capability_tasks(
            plan=plan,
            request=request,
            profile=profile,
            audit_mode=audit_mode,
            settings=self.settings,
            input_structure=input_structure,
            capabilities=capabilities,
            genre=selected_genre,
        )
        plan = add_focused_table_capability_task(
            plan=plan,
            profile=profile,
            capabilities=capabilities,
            enable_insight_synthesis=self.settings.enable_insight_synthesis,
        )
        plan = add_structured_record_capability_task(
            plan=plan,
            profile=profile,
            capabilities=capabilities,
            enable_insight_synthesis=self.settings.enable_insight_synthesis,
        )
        final_manifest = manifest.model_copy(
            update={
                "report_genre": plan.report_specification.genre,
                "communication_task": plan.report_specification.communication_task,
                "output_form": plan.report_specification.output_form,
                "focus_scope": plan.report_specification.focus_scope,
            }
        )
        store.save_json("00_manifest.json", final_manifest)
        if (
            selected_genre in EVENT_GENRES
            and semantic_map is not None
            and semantic_map.bindings
        ):
            plan = plan.model_copy(
                update={
                    "evidence_queries": normalise_event_evidence_queries(
                        queries=plan.evidence_queries,
                        semantic_map=semantic_map,
                        tasks=plan.tasks,
                        available_capabilities=set(capabilities),
                        request=request,
                        structural_catalog=structural_catalog,
                    )
                }
            )
        manifest = manifest.model_copy(
            update={
                "report_genre": selected_genre,
                "communication_task": (
                    plan.report_specification.communication_task
                ),
                "output_form": plan.report_specification.output_form,
                "focus_scope": plan.report_specification.focus_scope,
            }
        )
        store.save_json("00_manifest.json", manifest)
        store.save_json("03_execution_plan.json", plan)
        store.save_json(
            "03_evidence_queries.json",
            plan.evidence_queries,
        )
        store.save_json(
            "03_insight_objectives.json",
            plan.insight_objectives,
        )

        evidence_ledger = execute_plan(
            data_bundle,
            plan,
            self.settings,
            semantic_map,
        )
        store.save_json("04_evidence_ledger.json", evidence_ledger)

        fact_candidate_scaffold = deterministic_fact_candidate_scaffold(
            evidence_ledger,
            maximum_facts=None,
        )
        store.save_json(
            "05_fact_candidates_scaffold.json",
            fact_candidate_scaffold,
        )

        if short_form_realisation_task:
            store.trace(
                "evidence_synthesis",
                "skipped",
                {
                    "reason": (
                        "Short-form verbalisation uses deterministic atomic "
                        "fact candidates from direct evidence extraction."
                    )
                },
            )
            fact_candidate_enrichment = empty_fact_candidate_enrichment()
        else:
            fact_candidate_enrichment = await self.run_agent_or_fallback(
                stage="evidence_synthesis",
                agent=self.evidence_agent,
                prompt=(
                    "Review this deterministic fact-candidate scaffold and "
                    "return only fact candidates that materially improve, "
                    "correct, combine, or prioritise the scaffold while staying "
                    "strictly grounded in the evidence. You do not need to cover "
                    "every evidence item; deterministic scaffold coverage is "
                    "already preserved.\n\nEvidence ledger:\n"
                    + compact_json(evidence_ledger)
                    + "\n\nDeterministic scaffold:\n"
                    + compact_json(fact_candidate_scaffold)
                    + "\n\nEnrichment policy:\n"
                    "Return a concise set of higher-quality candidates only. "
                    "Single-evidence candidates may improve ordinary scaffold "
                    "candidates, but concrete event-sequence scaffold facts are "
                    "preserved. Multi-evidence candidates may add bounded "
                    "synthesis. Do not drop evidence coverage; the controller "
                    "will merge your valid candidates with the deterministic "
                    "scaffold."
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "evidence_ledger": evidence_ledger.model_dump(mode="json")
                    },
                ),
                fallback=empty_fact_candidate_enrichment,
                store=store,
            )
        fact_candidate_enrichment = FactCandidateSet.model_validate(
            fact_candidate_enrichment
        )
        store.save_json(
            "05_fact_candidates_enrichment.json",
            fact_candidate_enrichment,
        )

        fact_candidates = merge_fact_candidate_scaffold(
            scaffold=fact_candidate_scaffold,
            enrichment=fact_candidate_enrichment,
            evidence=evidence_ledger,
        )
        store.save_json("05_fact_candidates.json", fact_candidates)

        if short_form_realisation_task:
            store.trace(
                "fact_verification",
                "skipped",
                {
                    "reason": (
                        "Short-form facts come from deterministic direct "
                        "extraction and are verified by deterministic "
                        "fallback review."
                    )
                },
            )
            verification = fallback_verification(fact_candidates)
        else:
            verification = await self.run_agent_or_fallback(
                stage="fact_verification",
                agent=self.verifier_agent,
                prompt=(
                    "Verify every fact candidate against the evidence.\n\n"
                    "Candidates:\n"
                    + compact_json(fact_candidates)
                    + "\n\nEvidence:\n"
                    + compact_json(evidence_ledger)
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_candidates": fact_candidates.model_dump(mode="json")
                    },
                ),
                fallback=lambda: fallback_verification(
                    fact_candidates
                ),
                store=store,
            )
        verification = VerificationResult.model_validate(verification)
        raw_verification = verification
        verification = repair_spurious_missing_evidence_rejections(
            candidate_set=fact_candidates,
            verification=verification,
            evidence=evidence_ledger,
        )
        if (
            verification.model_dump(mode="json")
            != raw_verification.model_dump(mode="json")
        ):
            store.save_json("06_verification_raw.json", raw_verification)
        store.save_json("06_verification.json", verification)

        fact_ledger = finalise_fact_ledger(
            fact_candidates,
            verification,
            evidence_ledger,
        )
        if not fact_ledger.writer_ready_facts:
            store.trace(
                "fact_ledger_finalisation",
                "recovery",
                {
                    "reason": "Verifier rejected every fact candidate.",
                },
            )
            fact_candidates = fallback_fact_candidates(
                evidence_ledger,
                plan.maximum_facts,
            )
            verification = fallback_verification(fact_candidates)
            fact_ledger = finalise_fact_ledger(
                fact_candidates,
                verification,
                evidence_ledger,
            )
            store.save_json("05_fact_candidates_recovered.json", fact_candidates)
            store.save_json("06_verification_recovered.json", verification)
            store.save_json("07_fact_ledger_recovered.json", fact_ledger)
        store.save_json(
            "07_fact_ledger_pre_coverage_recovery.json",
            fact_ledger,
        )

        fact_count_before_recovery = len(
            fact_ledger.writer_ready_facts
        )

        fact_ledger = (
            augment_fact_ledger_for_report_coverage(
                fact_ledger=fact_ledger,
                evidence=evidence_ledger,
                required_components=(
                    plan.report_specification
                    .required_components
                ),
                required_content_slots=(
                    plan.report_specification
                    .required_content_slots
                ),
                settings=self.settings,
            )
        )

        store.trace(
            "fact_ledger_coverage_recovery",
            "completed",
            {
                "facts_before": (
                    fact_count_before_recovery
                ),
                "facts_after": len(
                    fact_ledger
                    .writer_ready_facts
                ),
                "recovered_fact_ids": (
                    fact_ledger
                    .deterministically_recovered_fact_ids
                ),
                "notes": (
                    fact_ledger
                    .coverage_recovery_notes
                ),
            },
        )

        store.save_json(
            "07_fact_ledger.json",
            fact_ledger,
        )
        genre_scoped_fact_ledger = scope_fact_ledger_for_genre(
            fact_ledger,
            evidence_ledger,
            plan.report_specification.genre,
        )
        if (
            plan.report_specification.communication_task
            in {
                CommunicationTask.FOCUSED_TABLE_DESCRIPTION,
                CommunicationTask.ATTRIBUTE_VERBALISATION,
                CommunicationTask.TRIPLE_VERBALISATION,
            }
        ):
            allowed_capability = (
                EvidenceCapability.FOCUSED_TABLE_REGION
                if (
                    plan.report_specification.communication_task
                    == CommunicationTask.FOCUSED_TABLE_DESCRIPTION
                )
                else EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
            )
            evidence_by_id = {
                item.evidence_id: item
                for item in evidence_ledger.items
            }
            genre_scoped_fact_ledger = (
                genre_scoped_fact_ledger.model_copy(
                    update={
                        "writer_ready_facts": [
                            fact
                            for fact
                            in genre_scoped_fact_ledger.writer_ready_facts
                            if allowed_capability in fact.source_capabilities
                            or any(
                                evidence_by_id[evidence_id].capability
                                == allowed_capability
                                for evidence_id in fact.evidence_ids
                                if evidence_id in evidence_by_id
                            )
                        ]
                    }
                )
            )

        insight_candidates = InsightCandidateSet()
        insight_verification = InsightVerificationResult()

        if short_form_realisation_task:
            insight_ledger = empty_insight_ledger(
                synthesis_enabled=self.settings.enable_insight_synthesis,
                fallback_reason=(
                    "Short-form verbalisation skips bounded insight "
                    "synthesis; direct record evidence is sufficient for "
                    "the requested output form."
                ),
            )
            store.trace(
                "evidence.insight_synthesis",
                "skipped",
                {"reason": insight_ledger.fallback_reason},
            )
            store.trace(
                "verifier.insight_verification",
                "skipped",
                {"reason": insight_ledger.fallback_reason},
            )
        elif not self.settings.enable_insight_synthesis:
            insight_ledger = empty_insight_ledger(
                synthesis_enabled=False,
                fallback_reason=(
                    "Insight synthesis disabled by configuration."
                ),
            )
            store.trace(
                "evidence.insight_synthesis",
                "skipped",
                {"reason": insight_ledger.fallback_reason},
            )
            store.trace(
                "verifier.insight_verification",
                "skipped",
                {"reason": insight_ledger.fallback_reason},
            )
        elif not self.settings.use_llm:
            insight_ledger = empty_insight_ledger(
                synthesis_enabled=True,
                fallback_reason=(
                    "LLM execution disabled; the workflow continued through "
                    "the existing fact-led Writer path."
                ),
            )
            store.trace(
                "evidence.insight_synthesis",
                "skipped",
                {"reason": "LLM execution disabled"},
            )
            store.trace(
                "verifier.insight_verification",
                "skipped",
                {"reason": "LLM execution disabled"},
            )
        else:
            insight_payload = build_compact_insight_payload(
                request=request,
                plan=plan,
                fact_ledger=genre_scoped_fact_ledger,
                evidence_ledger=evidence_ledger,
                settings=self.settings,
            )
            raw_insight_candidates, synthesis_error = (
                await self.run_optional_insight_agent(
                    stage="evidence.insight_synthesis",
                    agent=self.evidence_insight_synthesis_agent,
                    prompt=(
                        "Perform the Evidence Analyst's second bounded "
                        "synthesis pass. Use only this compact package and "
                        "return structured insight candidates.\n\n"
                        + compact_json(insight_payload)
                    ),
                    dependencies=AgentDependencies(
                        run_id=run_id,
                        payload={
                            "fact_ledger": (
                                genre_scoped_fact_ledger.model_dump(
                                    mode="json"
                                )
                            ),
                            "evidence_ledger": evidence_ledger.model_dump(
                                mode="json"
                            ),
                        },
                    ),
                    store=store,
                )
            )

            if synthesis_error is not None:
                insight_ledger = empty_insight_ledger(
                    synthesis_enabled=True,
                    fallback_reason=(
                        "Evidence Analyst second-pass insight synthesis "
                        f"failed: {synthesis_error}"
                    ),
                )
            else:
                try:
                    insight_candidates = InsightCandidateSet.model_validate(
                        raw_insight_candidates
                    )
                except Exception as error:
                    insight_ledger = empty_insight_ledger(
                        synthesis_enabled=True,
                        fallback_reason=(
                            "Evidence Analyst second-pass output remained "
                            "invalid: "
                            f"{type(error).__name__}: {error}"
                        ),
                    )
                else:
                    if not insight_candidates.candidates:
                        insight_ledger = empty_insight_ledger(
                            synthesis_enabled=True,
                            fallback_reason=(
                                "Evidence Analyst second pass returned no "
                                "bounded insight candidates."
                            ),
                        )
                    else:
                        referenced_evidence_ids = {
                            evidence_id
                            for candidate in insight_candidates.candidates
                            for evidence_id in candidate.source_evidence_ids
                        }
                        referenced_evidence_ids.update(
                            evidence_id
                            for fact in genre_scoped_fact_ledger.writer_ready_facts
                            if fact.fact_id
                            in {
                                fact_id
                                for candidate in insight_candidates.candidates
                                for fact_id in candidate.source_fact_ids
                            }
                            for evidence_id in fact.evidence_ids
                        )
                        verifier_evidence = [
                            item
                            for item in evidence_ledger.items
                            if item.evidence_id
                            in referenced_evidence_ids
                        ]
                        raw_insight_verification, verifier_error = (
                            await self.run_optional_insight_agent(
                                stage="verifier.insight_verification",
                                agent=(
                                    self.verifier_insight_verification_agent
                                ),
                                prompt=(
                                    "Perform the Fact Verifier's second-pass "
                                    "review of every bounded insight candidate."
                                    "\n\nCandidates:\n"
                                    + compact_json(insight_candidates)
                                    + "\n\nWriter-ready facts:\n"
                                    + compact_json(
                                        genre_scoped_fact_ledger
                                        .writer_ready_facts
                                    )
                                    + "\n\nReferenced deterministic evidence:\n"
                                    + compact_json(verifier_evidence)
                                    + "\n\nReport specification:\n"
                                    + compact_json(
                                        plan.report_specification
                                    )
                                ),
                                dependencies=AgentDependencies(
                                    run_id=run_id,
                                    payload={
                                        "insight_candidates": (
                                            insight_candidates.model_dump(
                                                mode="json"
                                            )
                                        ),
                                        "fact_ledger": (
                                            genre_scoped_fact_ledger
                                            .model_dump(
                                                mode="json"
                                            )
                                        ),
                                        "evidence_ledger": (
                                            evidence_ledger.model_dump(
                                                mode="json"
                                            )
                                        ),
                                    },
                                ),
                                store=store,
                            )
                        )

                        verification_notes: list[str] = []
                        valid_records = []
                        unresolved_candidates = list(
                            insight_candidates.candidates
                        )

                        if verifier_error is not None:
                            verification_notes.append(
                                "Batch insight verification failed: "
                                + verifier_error
                            )
                        else:
                            try:
                                batch_verification = (
                                    InsightVerificationResult.model_validate(
                                        raw_insight_verification
                                    )
                                )
                            except Exception as error:
                                verification_notes.append(
                                    "Batch insight verification could not be "
                                    "parsed: "
                                    f"{type(error).__name__}: {error}"
                                )
                            else:
                                batch_errors = validate_insight_verification(
                                    batch_verification,
                                    insight_candidates,
                                    genre_scoped_fact_ledger,
                                    evidence_ledger,
                                    self.settings,
                                    plan.report_specification.genre,
                                )
                                verification_notes.extend(batch_errors)
                                unresolved_ids = {
                                    candidate.insight_id
                                    for candidate
                                    in insight_candidates.candidates
                                    if any(
                                        candidate.insight_id in error
                                        for error in batch_errors
                                    )
                                    or sum(
                                        record.insight_id
                                        == candidate.insight_id
                                        for record
                                        in batch_verification.records
                                    )
                                    != 1
                                }
                                valid_records = [
                                    record
                                    for record in batch_verification.records
                                    if record.insight_id
                                    not in unresolved_ids
                                    and record.insight_id
                                    in {
                                        candidate.insight_id
                                        for candidate
                                        in insight_candidates.candidates
                                    }
                                ]
                                unresolved_candidates = [
                                    candidate
                                    for candidate
                                    in insight_candidates.candidates
                                    if candidate.insight_id in unresolved_ids
                                ]
                                verification_notes.extend(
                                    batch_verification.verifier_notes
                                )

                        for retry_index, candidate in enumerate(
                            unresolved_candidates,
                            start=1,
                        ):
                            candidate_set = InsightCandidateSet(
                                candidates=[candidate]
                            )
                            candidate_fact_ids = set(
                                candidate.source_fact_ids
                            )
                            candidate_facts = [
                                fact
                                for fact
                                in genre_scoped_fact_ledger.writer_ready_facts
                                if fact.fact_id in candidate_fact_ids
                            ]
                            candidate_evidence_ids = {
                                evidence_id
                                for fact in candidate_facts
                                for evidence_id in fact.evidence_ids
                            }
                            candidate_evidence_ids.update(
                                candidate.source_evidence_ids
                            )
                            candidate_evidence = [
                                item
                                for item in evidence_ledger.items
                                if item.evidence_id
                                in candidate_evidence_ids
                            ]
                            retry_output, retry_error = (
                                await self.run_optional_insight_agent(
                                    stage=(
                                        "verifier.insight_verification.retry."
                                        f"{retry_index:03d}"
                                    ),
                                    agent=(
                                        self
                                        .verifier_insight_verification_agent
                                    ),
                                    prompt=(
                                        "Review this one bounded insight "
                                        "candidate independently. Return "
                                        "exactly one verification record."
                                        "\n\nCandidate:\n"
                                        + compact_json(candidate_set)
                                        + "\n\nWriter-ready facts:\n"
                                        + compact_json(candidate_facts)
                                        + "\n\nReferenced deterministic "
                                        "evidence:\n"
                                        + compact_json(candidate_evidence)
                                        + "\n\nReport specification:\n"
                                        + compact_json(
                                            plan.report_specification
                                        )
                                    ),
                                    dependencies=AgentDependencies(
                                        run_id=run_id,
                                        payload={
                                            "insight_candidates": (
                                                candidate_set.model_dump(
                                                    mode="json"
                                                )
                                            ),
                                            "fact_ledger": (
                                                genre_scoped_fact_ledger
                                                .model_dump(mode="json")
                                            ),
                                            "evidence_ledger": (
                                                evidence_ledger.model_dump(
                                                    mode="json"
                                                )
                                            ),
                                        },
                                    ),
                                    store=store,
                                )
                            )
                            if retry_error is not None:
                                verification_notes.append(
                                    f"{candidate.insight_id} verification "
                                    f"retry failed: {retry_error}"
                                )
                                continue

                            try:
                                retry_verification = (
                                    InsightVerificationResult.model_validate(
                                        retry_output
                                    )
                                )
                            except Exception as error:
                                verification_notes.append(
                                    f"{candidate.insight_id} verification "
                                    "retry could not be parsed: "
                                    f"{type(error).__name__}: {error}"
                                )
                                continue

                            retry_errors = validate_insight_verification(
                                retry_verification,
                                candidate_set,
                                genre_scoped_fact_ledger,
                                evidence_ledger,
                                self.settings,
                                plan.report_specification.genre,
                            )
                            matching_records = [
                                record
                                for record
                                in retry_verification.records
                                if record.insight_id
                                == candidate.insight_id
                            ]
                            if retry_errors or len(matching_records) != 1:
                                verification_notes.extend(retry_errors)
                                if len(matching_records) != 1:
                                    verification_notes.append(
                                        f"{candidate.insight_id} verification "
                                        "retry did not return exactly one "
                                        "matching record."
                                    )
                                continue

                            valid_records.append(matching_records[0])
                            verification_notes = [
                                note
                                for note in verification_notes
                                if candidate.insight_id not in note
                            ]
                            verification_notes.append(
                                f"{candidate.insight_id} was recovered by "
                                "individual verification."
                            )
                            verification_notes.extend(
                                retry_verification.verifier_notes
                            )

                        if len(valid_records) == len(
                            insight_candidates.candidates
                        ):
                            verification_notes = [
                                note
                                for note in verification_notes
                                if not note.startswith(
                                    "Batch insight verification"
                                )
                            ]

                        insight_verification = InsightVerificationResult(
                            records=valid_records,
                            verifier_notes=list(
                                dict.fromkeys(verification_notes)
                            ),
                        )
                        try:
                            insight_ledger = materialise_insight_ledger(
                                candidates=insight_candidates,
                                verification=insight_verification,
                                fact_ledger=genre_scoped_fact_ledger,
                                evidence_ledger=evidence_ledger,
                                settings=self.settings,
                                report_genre=(
                                    plan.report_specification.genre
                                ),
                            )
                            if (
                                not insight_ledger.verified_insights
                                and insight_ledger.unverified_insights
                                and not insight_ledger.rejected_insights
                            ):
                                insight_ledger = insight_ledger.model_copy(
                                    update={
                                        "fallback_reason": (
                                            "No insight candidate received a "
                                            "usable verifier review; the "
                                            "Writer continued with verified "
                                            "facts."
                                        )
                                    }
                                )
                        except Exception as error:
                            insight_ledger = empty_insight_ledger(
                                synthesis_enabled=True,
                                fallback_reason=(
                                    "Deterministic Insight Ledger "
                                    "materialisation failed: "
                                    f"{type(error).__name__}: {error}"
                                ),
                            )

        store.save_json(
            "07_insight_candidates.json",
            insight_candidates,
        )
        store.save_json(
            "07_insight_verification.json",
            insight_verification,
        )
        store.save_json(
            "07_insight_ledger.json",
            insight_ledger,
        )
        store.trace(
            "insight_ledger",
            "completed" if insight_ledger.fallback_reason is None else "fallback",
            {
                "synthesis_enabled": insight_ledger.synthesis_enabled,
                "verified_insight_count": len(
                    insight_ledger.verified_insights
                ),
                "hypothesis_only_count": len(
                    insight_ledger.hypothesis_only_insights
                ),
                "rejected_count": len(
                    insight_ledger.rejected_insights
                ),
                "unverified_count": len(
                    insight_ledger.unverified_insights
                ),
                "fallback_reason": insight_ledger.fallback_reason,
            },
        )

        writer_pack = build_writer_evidence_pack(
            request=request,
            understanding=understanding,
            plan=plan,
            evidence=evidence_ledger,
            fact_ledger=fact_ledger,
            settings=self.settings,
            insight_ledger=insight_ledger,
            input_structure=input_structure,
            available_capabilities=capabilities,
        )
        store.save_json("08_writer_evidence_pack.json", writer_pack)
        writer_visible_fact_ledger = FactLedger(
            writer_ready_facts=[
                *writer_pack.priority_facts,
                *writer_pack.supporting_facts,
                *writer_pack.limitation_facts,
            ],
            rejected_facts=genre_scoped_fact_ledger.rejected_facts,
            verifier_notes=genre_scoped_fact_ledger.verifier_notes,
            deterministically_recovered_fact_ids=(
                genre_scoped_fact_ledger
                .deterministically_recovered_fact_ids
            ),
            coverage_recovery_notes=(
                genre_scoped_fact_ledger.coverage_recovery_notes
            ),
        )
        writer_content_requirements = build_writer_content_requirements(
            report_specification=plan.report_specification,
            fact_ledger=writer_visible_fact_ledger,
            evidence=evidence_ledger,
            insight_ledger=writer_pack.insight_ledger,
            settings=self.settings,
        )
        store.save_json(
            "08_writer_content_requirements.json",
            writer_content_requirements,
        )
        narrative_plan = build_event_narrative_plan(
            writer_pack,
            writer_content_requirements,
        )
        store.save_json(
            "08_narrative_plan.json",
            narrative_plan,
        )

        writer_prompt = (
            "Write the final report for the selected report contract from the "
            "compact verified-fact package below.\n\n"
            "The `content_requirements` field is a controller-enforced "
            "coverage checklist. Use the required supported items and meet "
            "the minimum useful word count when it is enforced.\n\n"
            "When `event_report_writing_guidance` is present, follow it as "
            "the task style contract: write a coherent event recap, lead with "
            "the supported result, integrate supported sequence/progression "
            "and performances, and avoid flat-table profiling or mechanical "
            "ranking dumps.\n\n"
            "When `narrative_plan` is present, use it to decide ordering, "
            "paragraph grouping and salience. Cover higher-priority narrative "
            "slots first, use low-priority fact IDs only when they add "
            "distinct value, and keep the prose flowing instead of listing "
            "every available ranking.\n\n"
            "When `realisation_policy` or `style_rewrite_permissions` are "
            "present, use them only to improve phrasing, ordering, compression "
            "and harmless surface formatting. They do not authorise new facts, "
            "new numbers, new entities, unsupported chronology, or unsupported "
            "explanations.\n\n"
            "Return structured sections and sentences. Do not return "
            "a Markdown field or construct a separate support map; the "
            "controller will create both deterministically.\n\n"
            + compact_json(
                build_compact_writer_payload(
                    writer_pack,
                    self.settings.allow_hypotheses_in_report,
                    writer_content_requirements,
                    narrative_plan,
                )
            )
        )

        writer_material_available = bool(
            writer_pack.priority_facts
            or writer_pack.supporting_facts
            or writer_pack.limitation_facts
            or writer_pack.priority_verified_insights
            or writer_pack.supporting_verified_insights
        )
        if writer_material_available:
            writer_draft_or_fallback = await self.run_agent_or_fallback(
                stage="natural_writer",
                agent=self.writer_agent,
                prompt=writer_prompt,
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_ledger": genre_scoped_fact_ledger.model_dump(mode="json"),
                        "insight_ledger": writer_pack.insight_ledger.model_dump(
                            mode="json"
                        ),
                        "allow_hypotheses_in_report": (
                            self.settings.allow_hypotheses_in_report
                        ),
                        "report_genre": plan.report_specification.genre.value,
                        "report_perspective": (
                            plan.report_specification.perspective.value
                        ),
                        "maximum_length_words": (
                            plan.report_specification.maximum_length_words
                        ),
                        "writer_content_requirements": (
                            writer_content_requirements
                        ),
                        "narrative_plan": narrative_plan.model_dump(
                            mode="json"
                        ),
                    },
                ),
                fallback=lambda: fallback_writer(writer_pack),
                store=store,
            )
        else:
            writer_draft_or_fallback = fallback_writer(writer_pack)
            store.trace(
                "natural_writer",
                "skipped",
                {
                    "reason": "No verified genre-scoped facts or insights.",
                    "fallback": "deterministic_writer",
                },
            )

        if isinstance(
            writer_draft_or_fallback,
            WriterOutput,
        ):
            raw_writer_output = (
                writer_draft_or_fallback
            )
        else:
            writer_draft = (
                WriterAgentDraft.model_validate(
                    writer_draft_or_fallback
                )
            )
            store.save_json(
                "09_writer_structured_draft.json",
                writer_draft,
            )

            try:
                raw_writer_output = materialise_writer_output(
                    writer_draft,
                    genre_scoped_fact_ledger,
                    insight_ledger=writer_pack.insight_ledger,
                    allow_hypotheses_in_report=(
                        self.settings.allow_hypotheses_in_report
                    ),
                    content_requirements=writer_content_requirements,
                    writer_mode="llm_writer",
                    eligible_for_primary_evaluation=representation_eligible,
                )
            except ValueError as error:
                store.save_text(
                    "09_writer_materialisation_error.txt",
                    str(error),
                )
                store.trace(
                    "natural_writer_materialisation",
                    "fallback",
                    {
                        "reason": f"ValueError: {error}",
                        "fallback": "deterministic_writer",
                    },
                )
                raw_writer_output = fallback_writer(
                    writer_pack
                )

        if not representation_eligible:
            raw_writer_output = raw_writer_output.model_copy(
                update={"eligible_for_primary_evaluation": False}
            )

        store.save_json(
            "09_writer_raw_output.json",
            raw_writer_output,
        )
        store.save_text(
            "09_writer_raw_report.md",
            raw_writer_output.markdown,
        )
        store.save_json(
            "09_writer_support_map.json",
            raw_writer_output.sentence_support,
        )

        component_assessments = assess_report_component_coverage(
            writer_output=raw_writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            required_components=plan.report_specification.required_components,
        )
        missing_components = [
            assessment.component
            for assessment in component_assessments
            if not assessment.covered
        ]
        store.save_json(
            "09_writer_component_coverage.json",
            component_assessments,
        )
        initial_genre_quality = assess_genre_quality(
            raw_writer_output,
            plan.report_specification,
            evidence_ledger,
        )
        store.save_json(
            "09_writer_genre_quality.json",
            initial_genre_quality,
        )

        initial_quality_audit = deterministic_audit(
            writer_output=raw_writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=0,
            report_specification=plan.report_specification,
            settings=self.settings,
            profile_support_records=profile_support_records,
            insight_ledger=insight_ledger,
        )
        store.save_json("10_initial_writer_quality.json", initial_quality_audit)

        writer_output_for_audit = raw_writer_output
        quality_revised_writer_output: WriterOutput | None = None
        short_form_output = (
            plan.report_specification.communication_task
            in SHORT_FORM_COMMUNICATION_TASKS
        )
        needs_quality_revision = (
            not short_form_output
            and (
                bool(missing_components)
                or initial_quality_audit.quality_assessment.status
                != QualityStatus.PASS
                or initial_genre_quality.status == QualityStatus.REVISE
            )
        )

        if (
            needs_quality_revision
            and writer_material_available
            and self.settings.use_llm
            and self.writer_agent is not None
            and self.settings.writer_quality_revision_rounds > 0
        ):
            revised_draft_or_fallback = await self.run_agent_or_fallback(
                stage="writer_quality_revision",
                agent=self.writer_agent,
                prompt=build_writer_quality_revision_prompt(
                    writer_pack=writer_pack,
                    current_output=raw_writer_output,
                    missing_components=missing_components,
                    quality_findings=(
                        [
                            *initial_quality_audit.quality_assessment.findings,
                            *initial_genre_quality.findings,
                        ]
                    ),
                    content_requirements=(
                        writer_content_requirements
                    ),
                    settings=self.settings,
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_ledger": (
                            genre_scoped_fact_ledger.model_dump(
                                mode="json"
                            )
                        ),
                        "insight_ledger": (
                            writer_pack.insight_ledger.model_dump(
                                mode="json"
                            )
                        ),
                        "allow_hypotheses_in_report": (
                            self.settings.allow_hypotheses_in_report
                        ),
                        "report_genre": (
                            plan.report_specification.genre.value
                        ),
                        "report_perspective": (
                            plan.report_specification.perspective.value
                        ),
                        "maximum_length_words": (
                            plan.report_specification.maximum_length_words
                        ),
                        "writer_content_requirements": (
                            writer_content_requirements
                        ),
                    },
                ),
                fallback=lambda: raw_writer_output,
                store=store,
            )

            revision_materialisation_error: str | None = None
            if isinstance(
                revised_draft_or_fallback,
                WriterOutput,
            ):
                revision_candidate = (
                    revised_draft_or_fallback
                    .model_copy(
                        update={
                            "quality_revision_round": 1,
                            "quality_revision_summary": (
                                "Bounded whole-report "
                                "quality-revision candidate."
                            ),
                        }
                    )
                )
            else:
                revised_writer_draft = (
                    WriterAgentDraft.model_validate(
                        revised_draft_or_fallback
                    )
                )
                store.save_json(
                    "10_writer_quality_revision_draft.json",
                    revised_writer_draft,
                )
                try:
                    revision_candidate = materialise_writer_output(
                        revised_writer_draft,
                        genre_scoped_fact_ledger,
                        insight_ledger=writer_pack.insight_ledger,
                        allow_hypotheses_in_report=(
                            self.settings.allow_hypotheses_in_report
                        ),
                        content_requirements=writer_content_requirements,
                        writer_mode="llm_writer",
                        eligible_for_primary_evaluation=representation_eligible,
                        quality_revision_round=1,
                        quality_revision_summary=(
                            "Bounded whole-report "
                            "quality-revision candidate."
                        ),
                    )
                except ValueError as error:
                    revision_materialisation_error = str(error)
                    store.save_text(
                        "10_writer_quality_revision_materialisation_error.txt",
                        str(error),
                    )
                    store.trace(
                        "writer_quality_revision_materialisation",
                        "rejected",
                        {
                            "reason": f"ValueError: {error}",
                            "fallback": "pre_revision_writer_output",
                        },
                    )
                    revision_candidate = raw_writer_output

            revision_candidate = revision_candidate.model_copy(
                update={
                    "quality_revision_round": 1,
                    "quality_revision_summary": (
                        "Bounded whole-report "
                        "quality-revision candidate."
                    ),
                }
            )

            store.save_json(
                "10_writer_quality_revision_candidate.json",
                revision_candidate,
            )
            store.save_text(
                "10_writer_quality_revision_candidate.md",
                revision_candidate.markdown,
            )

            revision_validation_errors = (
                validate_writer_output(
                    revision_candidate,
                    fact_ledger,
                    insight_ledger,
                    self.settings.allow_hypotheses_in_report,
                )
            )
            if revision_materialisation_error is not None:
                revision_validation_errors.append(
                    "Writer quality revision failed materialisation: "
                    + revision_materialisation_error
                )

            revised_quality_audit = (
                deterministic_audit(
                    writer_output=revision_candidate,
                    fact_ledger=fact_ledger,
                    evidence=evidence_ledger,
                    mode=audit_mode,
                    external_sources=(
                        external_truth_sources
                    ),
                    revision_round=0,
                    report_specification=(
                        plan.report_specification
                    ),
                    settings=self.settings,
                    profile_support_records=(
                        profile_support_records
                    ),
                    insight_ledger=insight_ledger,
                )
            )

            revision_accepted, revision_reasons = (
                accept_writer_quality_revision(
                    before=raw_writer_output,
                    after=revision_candidate,
                    before_audit=(
                        initial_quality_audit
                    ),
                    after_audit=(
                        revised_quality_audit
                    ),
                    validation_errors=(
                        revision_validation_errors
                    ),
                    report_specification=(
                        plan.report_specification
                    ),
                    settings=self.settings,
                )
            )

            store.save_json(
                "10_writer_quality_revision_assessment.json",
                {
                    "attempted": True,
                    "accepted": revision_accepted,
                    "reasons": revision_reasons,
                    "before_component_assessments": (
                        initial_quality_audit
                        .component_assessments
                    ),
                    "after_component_assessments": (
                        revised_quality_audit
                        .component_assessments
                    ),
                    "before_quality": (
                        initial_quality_audit
                        .quality_assessment
                    ),
                    "after_quality": (
                        revised_quality_audit
                        .quality_assessment
                    ),
                    "validation_errors": (
                        revision_validation_errors
                    ),
                },
            )

            if revision_accepted:
                quality_revised_writer_output = (
                    revision_candidate.model_copy(
                        update={
                            "quality_revision_summary": (
                                "One bounded Writer "
                                "quality revision was "
                                "accepted before factual "
                                "auditing."
                            ),
                        }
                    )
                )

                writer_output_for_audit = (
                    quality_revised_writer_output
                )

                store.save_json(
                    "10_writer_quality_revision.json",
                    writer_output_for_audit,
                )
                store.save_text(
                    "10_writer_quality_revision.md",
                    writer_output_for_audit.markdown,
                )
                store.save_json(
                    "10_writer_quality_revision_component_coverage.json",
                    revised_quality_audit.component_assessments,
                )
            else:
                store.trace(
                    "writer_quality_revision",
                    "rejected",
                    {
                        "reasons": (
                            revision_reasons
                        )
                    },
                )

        (
            initial_audit,
            proposal,
            writer_output_for_audit,
        ) = await self.audit_once(
            run_id=run_id,
            writer_output=writer_output_for_audit,
            fact_ledger=fact_ledger,
            evidence_ledger=evidence_ledger,
            insight_ledger=insight_ledger,
            profile_support_records=profile_support_records,
            plan=plan,
            audit_mode=audit_mode,
            external_truth_sources=external_truth_sources,
            revision_round=0,
            store=store,
            stage_name="initial_audit_and_repair",
        )

        store.save_json("10_initial_audit.json", initial_audit)
        store.save_json(
            "10_initial_quality_assessment.json",
            initial_audit.quality_assessment,
        )
        store.save_json("11_repair_candidates_round_0.json", proposal)

        current_output = writer_output_for_audit
        current_audit = initial_audit
        repair_rounds = 0
        all_patches = []

        while (
            current_audit.decision == AuditDecision.REVISE
            and repair_rounds < plan.revision_limit
        ):
            repaired_output, patches = apply_repair_proposal(
                current_output,
                proposal,
                fact_ledger,
                evidence_ledger,
                insight_ledger,
                self.settings.allow_hypotheses_in_report,
            )

            if not patches:
                release_status = decide_release_status(
                    annotations=current_audit.annotations,
                    quality=current_audit.quality_assessment,
                    methodological_warnings=current_audit.methodological_warnings,
                    repair_budget_exhausted=True,
                    audit_mode=audit_mode,
                )
                current_audit = current_audit.model_copy(
                    update={
                        "decision": (
                            AuditDecision.BLOCK
                            if release_status == ReleaseStatus.HUMAN_REVIEW_REQUIRED
                            else AuditDecision.PASS
                        ),
                        "release_status": release_status,
                        "residual_risk": (
                            current_audit.residual_risk
                            + " No deterministic-valid repair candidate was available."
                        ),
                    }
                )
                break

            repair_rounds += 1
            all_patches.extend(patches)
            current_output = repaired_output

            store.save_json(
                f"12_selected_patches_round_{repair_rounds}.json",
                patches,
            )
            store.save_text(
                f"13_repaired_report_round_{repair_rounds}.md",
                current_output.markdown,
            )
            store.save_json(
                f"13_repaired_output_round_{repair_rounds}.json",
                current_output,
            )

            (
                current_audit,
                proposal,
                current_output,
            ) = await self.audit_once(
                run_id=run_id,
                writer_output=current_output,
                fact_ledger=fact_ledger,
                evidence_ledger=evidence_ledger,
                insight_ledger=insight_ledger,
                profile_support_records=profile_support_records,
                plan=plan,
                audit_mode=audit_mode,
                external_truth_sources=external_truth_sources,
                revision_round=repair_rounds,
                store=store,
                stage_name=f"post_repair_audit_round_{repair_rounds}",
            )

            current_audit = current_audit.model_copy(
                update={"applied_patches": all_patches}
            )

            store.save_json(
                f"14_post_repair_audit_round_{repair_rounds}.json",
                current_audit,
            )
            store.save_json(
                f"14_repair_candidates_round_{repair_rounds}.json",
                proposal,
            )

        repair_budget_exhausted = current_audit.decision == AuditDecision.REVISE

        if repair_budget_exhausted:
            release_status = decide_release_status(
                annotations=current_audit.annotations,
                quality=current_audit.quality_assessment,
                methodological_warnings=current_audit.methodological_warnings,
                repair_budget_exhausted=True,
                audit_mode=audit_mode,
            )
            current_audit = current_audit.model_copy(
                update={
                    "decision": (
                        AuditDecision.BLOCK
                        if release_status == ReleaseStatus.HUMAN_REVIEW_REQUIRED
                        else AuditDecision.PASS
                    ),
                    "release_status": release_status,
                    "residual_risk": (
                        current_audit.residual_risk
                        + " The bounded repair budget was exhausted."
                    ),
                    "applied_patches": all_patches,
                }
            )

        final_audit = current_audit
        store.save_json(
            "14_final_component_coverage.json",
            assess_report_components(
                current_output,
                fact_ledger,
                evidence_ledger,
                plan.report_specification.required_components,
            ),
        )
        genre_quality = assess_genre_quality(
            current_output,
            plan.report_specification,
            evidence_ledger,
        )
        store.save_json(
            "14_final_genre_quality.json",
            genre_quality,
        )

        factual_release_status = decide_release_status(
            annotations=final_audit.annotations,
            quality=final_audit.quality_assessment,
            methodological_warnings=final_audit.methodological_warnings,
            repair_budget_exhausted=repair_budget_exhausted,
            audit_mode=audit_mode,
        )

        if (
            factual_release_status
            == ReleaseStatus.HUMAN_REVIEW_REQUIRED
        ):
            final_decision = AuditDecision.BLOCK
        else:
            final_decision = AuditDecision.PASS

        final_audit = final_audit.model_copy(
            update={
                "decision": final_decision,
                "release_status": factual_release_status,
            }
        )

        release_status = factual_release_status
        if (
            not representation_eligible
            or genre_quality.status == QualityStatus.REVISE
        ):
            release_status = ReleaseStatus.HUMAN_REVIEW_REQUIRED

        if not representation_eligible:
            current_output = current_output.model_copy(
                update={"eligible_for_primary_evaluation": False}
            )

        approved = representation_eligible and genre_quality.status != (
            QualityStatus.REVISE
        ) and release_status in {
            ReleaseStatus.APPROVED,
            ReleaseStatus.APPROVED_WITH_WARNINGS,
        }

        if representation_eligible:
            primary_evaluation_reason = None
        elif input_structure is None:
            primary_evaluation_reason = "input_structure_unavailable"
        else:
            primary_evaluation_reason = (
                "input_representation_"
                + input_structure.representation_status.value
            )

        result = PipelineResult(
            run_id=run_id,
            profile=profile,
            input_structure=input_structure,
            structural_catalog=structural_catalog,
            evaluation_field_policy=data_bundle.evaluation_field_policy,
            understanding=understanding,
            execution_plan=plan,
            evidence_ledger=evidence_ledger,
            fact_candidates=fact_candidates,
            verification=verification,
            fact_ledger=fact_ledger,
            writer_evidence_pack=writer_pack,
            raw_writer_output=raw_writer_output,
            quality_revised_writer_output=quality_revised_writer_output,
            final_writer_output=current_output,
            initial_audit=initial_audit,
            final_audit=final_audit,
            repair_rounds_used=repair_rounds,
            release_status=release_status,
            approved_for_release=approved,
            primary_evaluation_eligible=representation_eligible,
            primary_evaluation_reason=primary_evaluation_reason,
            genre_quality_assessment=genre_quality,
            insight_ledger=insight_ledger,
        )

        store.save_json("final_result.json", result)

        if release_status == ReleaseStatus.APPROVED:
            header = "<!-- APPROVED BY AUDITOR -->\n\n"
        elif release_status == ReleaseStatus.APPROVED_WITH_WARNINGS:
            header = "<!-- APPROVED WITH RESIDUAL WARNINGS -->\n\n"
        else:
            header = "<!-- HUMAN REVIEW REQUIRED -->\n\n"

        store.save_text(
            "final_report.md",
            header + current_output.markdown,
        )

        store.trace(
            "workflow",
            "completed",
            {
                "release_status": release_status.value,
                "repair_rounds": repair_rounds,
                "writer_mode": current_output.writer_mode,
                "raw_writer_mode": raw_writer_output.writer_mode,
                "verified_insight_count": len(
                    insight_ledger.verified_insights
                ),
                "insight_fallback_reason": (
                    insight_ledger.fallback_reason
                ),
                "input_representation_status": (
                    input_structure.representation_status.value
                    if input_structure is not None
                    else "invalid"
                ),
                "genre_quality_status": genre_quality.status.value,
                "primary_evaluation_eligible": representation_eligible,
            },
        )

        return result

    def run_sync(
        self,
        inputs: list[str | Path],
        request: str,
        *,
        audit_mode: AuditMode = AuditMode.INTERNAL,
        external_truth_sources: list[ExternalTruthSource] | None = None,
        evaluation_field_policy: EvaluationFieldPolicy | None = None,
        report_genre: ReportGenre | None = None,
        communication_task: CommunicationTask | None = None,
        output_form: OutputForm | None = None,
        focus_scope: str | None = None,
    ) -> PipelineResult:
        return asyncio.run(
            self.run(
                inputs,
                request,
                audit_mode=audit_mode,
                external_truth_sources=external_truth_sources,
                evaluation_field_policy=evaluation_field_policy,
                report_genre=report_genre,
                communication_task=communication_task,
                output_form=output_form,
                focus_scope=focus_scope,
            )
        )
