"""Infer bounded communication contracts from requests and structured inputs."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .schemas import (
    CommunicationTask,
    InputSemanticMap,
    InputShape,
    InputStructureProfile,
    OutputForm,
    ReportGenre,
    ReportSelectionSource,
    TaskContractDecision,
    TaskFamilyHint,
)


INFERENCE_CONFIDENCE_THRESHOLD = 0.75


def _normalise_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).casefold()).strip("_")


def _source_payloads(structured_inputs: Mapping[str, Any]) -> list[Any]:
    payloads: list[Any] = []
    for payload in structured_inputs.values():
        if (
            isinstance(payload, Mapping)
            and payload.get("__table2text_benchmark_example__")
            and "source_payload" in payload
        ):
            payloads.append(payload.get("source_payload"))
        else:
            payloads.append(payload)
    return payloads


def _walk_mappings(value: Any, *, depth: int = 0):
    if depth > 8:
        return
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child, depth=depth + 1)
    elif isinstance(value, list):
        for child in value[:50]:
            yield from _walk_mappings(child, depth=depth + 1)


def _contains_nonempty_field(payloads: list[Any], field_name: str) -> bool:
    target = _normalise_key(field_name)
    return any(
        _normalise_key(key) == target
        and value is not None
        and value != ""
        and value != []
        and value != {}
        for payload in payloads
        for mapping in _walk_mappings(payload)
        for key, value in mapping.items()
    )


def _has_table(payloads: list[Any]) -> bool:
    return any(
        _normalise_key(key) in {"table", "table_array"}
        and isinstance(value, list)
        and bool(value)
        for payload in payloads
        for mapping in _walk_mappings(payload)
        for key, value in mapping.items()
    )


def _has_highlighted_region(payloads: list[Any]) -> bool:
    has_highlights = any(
        _normalise_key(key) in {"highlighted_cells", "highlighted_cell_ids"}
        and isinstance(value, list)
        and bool(value)
        for payload in payloads
        for mapping in _walk_mappings(payload)
        for key, value in mapping.items()
    )
    return has_highlights and _has_table(payloads)


def _has_attribute_record(payloads: list[Any]) -> bool:
    if _contains_nonempty_field(payloads, "meaning_representation"):
        return True
    return any(
        {"attribute_name", "attribute_value"}.issubset(
            {_normalise_key(key) for key in mapping}
        )
        for payload in payloads
        for mapping in _walk_mappings(payload)
    )


def _has_triple_record(payloads: list[Any]) -> bool:
    if _contains_nonempty_field(payloads, "triples") or _contains_nonempty_field(
        payloads, "tripleset"
    ):
        return True
    triple_key_sets = (
        {"subject", "relation", "object"},
        {"subject", "predicate", "object"},
        {"head", "relation", "tail"},
    )
    return any(
        any(required.issubset({_normalise_key(key) for key in mapping}) for required in triple_key_sets)
        for payload in payloads
        for mapping in _walk_mappings(payload)
    )


def _has_table_question(payloads: list[Any]) -> bool:
    return _has_table(payloads) and _contains_nonempty_field(payloads, "question")


def _requested_output_form(request: str) -> OutputForm | None:
    if re.search(r"\b(exactly|only) one (?:concise )?sentence\b", request, re.I):
        return OutputForm.ONE_SENTENCE
    if re.search(r"\bone sentence\b", request, re.I):
        return OutputForm.ONE_SENTENCE
    if re.search(r"\b(direct answer|answer (?:the )?question)\b", request, re.I):
        return OutputForm.DIRECT_ANSWER
    if re.search(r"\bone or two (?:fluent )?sentences\b|\bshort text\b", request, re.I):
        return OutputForm.SHORT_TEXT
    if re.search(r"\b(?:single )?paragraph\b", request, re.I):
        return OutputForm.PARAGRAPH
    if re.search(r"\b(multi[- ]paragraph|detailed report|full report)\b", request, re.I):
        return OutputForm.MULTI_PARAGRAPH_REPORT
    return None


def _explicit_task(request: str) -> CommunicationTask | None:
    if re.search(r"\b(highlighted|selected|focused) (?:table )?(?:cell|cells|region)\b", request, re.I):
        return CommunicationTask.FOCUSED_TABLE_DESCRIPTION
    if re.search(r"\b(attributes?|meaning representation)\b", request, re.I):
        return CommunicationTask.ATTRIBUTE_VERBALISATION
    if re.search(r"\b(triples?|subject[- ]predicate[- ]object)\b", request, re.I):
        return CommunicationTask.TRIPLE_VERBALISATION
    if re.search(r"\b(event|game|match) (?:report|recap|summary)\b", request, re.I):
        return CommunicationTask.EVENT_REPORT
    if re.search(r"\b(question answering|answer (?:the )?question)\b", request, re.I):
        return CommunicationTask.TABLE_QUESTION_ANSWERING
    if re.search(r"\b(table entailment|entailed by the table)\b", request, re.I):
        return CommunicationTask.TABLE_ENTAILMENT
    if re.search(r"\bdataset overview\b", request, re.I):
        return CommunicationTask.DATASET_OVERVIEW
    if re.search(r"\b(data[- ]science report|statistical analysis)\b", request, re.I):
        return CommunicationTask.DATA_SCIENCE_REPORT
    return None


def _task_family(communication_task: CommunicationTask) -> TaskFamilyHint:
    mapping = {
        CommunicationTask.DATA_SCIENCE_REPORT: TaskFamilyHint.DATA_SCIENCE_REPORT,
        CommunicationTask.DATASET_OVERVIEW: TaskFamilyHint.DATASET_OVERVIEW,
        CommunicationTask.EVENT_REPORT: TaskFamilyHint.EVENT_REPORT,
        CommunicationTask.FOCUSED_TABLE_DESCRIPTION: (
            TaskFamilyHint.HIGHLIGHTED_TABLE_DESCRIPTION
        ),
        CommunicationTask.TABLE_ENTAILMENT: TaskFamilyHint.LOGICAL_TABLE_STATEMENT,
        CommunicationTask.TABLE_QUESTION_ANSWERING: (
            TaskFamilyHint.TABLE_QUESTION_ANSWERING
        ),
        CommunicationTask.ATTRIBUTE_VERBALISATION: (
            TaskFamilyHint.ATTRIBUTE_VERBALISATION
        ),
        CommunicationTask.TRIPLE_VERBALISATION: (
            TaskFamilyHint.TRIPLE_VERBALISATION
        ),
    }
    return mapping.get(communication_task, TaskFamilyHint.CUSTOM)


def _defaults_for_task(
    communication_task: CommunicationTask,
) -> tuple[ReportGenre, OutputForm, str | None]:
    if communication_task == CommunicationTask.EVENT_REPORT:
        return (
            ReportGenre.EVENT_REPORT,
            OutputForm.MULTI_PARAGRAPH_REPORT,
            "event_recap",
        )
    if communication_task == CommunicationTask.FOCUSED_TABLE_DESCRIPTION:
        return (
            ReportGenre.DATASET_OVERVIEW,
            OutputForm.ONE_SENTENCE,
            "highlighted_cells",
        )
    if communication_task in {
        CommunicationTask.ATTRIBUTE_VERBALISATION,
        CommunicationTask.TRIPLE_VERBALISATION,
    }:
        return ReportGenre.DATASET_OVERVIEW, OutputForm.SHORT_TEXT, None
    if communication_task == CommunicationTask.TABLE_QUESTION_ANSWERING:
        return ReportGenre.DATASET_OVERVIEW, OutputForm.DIRECT_ANSWER, None
    if communication_task == CommunicationTask.TABLE_ENTAILMENT:
        return ReportGenre.DATASET_OVERVIEW, OutputForm.ONE_SENTENCE, None
    if communication_task == CommunicationTask.DATASET_OVERVIEW:
        return (
            ReportGenre.DATASET_OVERVIEW,
            OutputForm.MULTI_PARAGRAPH_REPORT,
            None,
        )
    return (
        ReportGenre.DATA_SCIENCE_REPORT,
        OutputForm.MULTI_PARAGRAPH_REPORT,
        None,
    )


def infer_task_contract(
    *,
    request: str,
    structured_inputs: Mapping[str, Any],
    input_structure: InputStructureProfile | None,
    semantic_map: InputSemanticMap | None = None,
) -> TaskContractDecision:
    """Infer a communication contract without dataset IDs or reference text."""

    payloads = _source_payloads(structured_inputs)
    explicit_task = _explicit_task(request)
    evidence: list[str] = []
    ambiguities: list[str] = []

    if explicit_task is not None:
        communication_task = explicit_task
        selection_source = ReportSelectionSource.EXPLICIT_USER_REQUEST
        confidence = 1.0
        evidence.append("The user request explicitly names the communication task.")
    elif _has_highlighted_region(payloads):
        communication_task = CommunicationTask.FOCUSED_TABLE_DESCRIPTION
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
        confidence = 0.98
        evidence.append("The operational source contains a table and a non-empty highlighted region.")
    elif _has_attribute_record(payloads):
        communication_task = CommunicationTask.ATTRIBUTE_VERBALISATION
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
        confidence = 0.97
        evidence.append("The operational source contains an attribute-oriented meaning representation.")
    elif _has_triple_record(payloads):
        communication_task = CommunicationTask.TRIPLE_VERBALISATION
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
        confidence = 0.97
        evidence.append("The operational source contains subject-relation-object records.")
    elif _has_table_question(payloads):
        communication_task = CommunicationTask.TABLE_QUESTION_ANSWERING
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
        confidence = 0.95
        evidence.append("The operational source pairs a table with a question.")
    elif (
        input_structure is not None
        and input_structure.shape == InputShape.EVENT_RECORD
        and input_structure.confidence >= 0.7
    ):
        communication_task = CommunicationTask.EVENT_REPORT
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
        confidence = input_structure.confidence
        evidence.append("The input-structure profile identifies one bounded event record.")
    elif (
        semantic_map is not None
        and semantic_map.confidence >= 0.7
        and semantic_map.recommended_communication_task is not None
    ):
        communication_task = semantic_map.recommended_communication_task
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
        confidence = semantic_map.confidence
        evidence.append("The validated semantic map recommends the communication task.")
    elif re.search(
        r"\b(understand|explore|strongest findings|key findings|report (?:its |the )?findings)\b",
        request,
        re.I,
    ):
        communication_task = CommunicationTask.DATA_SCIENCE_REPORT
        selection_source = ReportSelectionSource.FALLBACK
        confidence = 0.8
        evidence.append("The generic request asks for analytical findings.")
    else:
        communication_task = CommunicationTask.DATASET_OVERVIEW
        selection_source = ReportSelectionSource.FALLBACK
        confidence = 0.65
        evidence.append("No specialised communication task was established.")
        ambiguities.append("The intended communication task is not explicit in the request or structure.")

    report_genre, default_output, focus_scope = _defaults_for_task(
        communication_task
    )
    if (
        semantic_map is not None
        and semantic_map.confidence >= INFERENCE_CONFIDENCE_THRESHOLD
    ):
        if semantic_map.recommended_report_genre is not None:
            report_genre = semantic_map.recommended_report_genre
        if semantic_map.recommended_output_form is not None:
            default_output = semantic_map.recommended_output_form
        if semantic_map.recommended_focus_scope is not None:
            focus_scope = semantic_map.recommended_focus_scope

    requested_output = _requested_output_form(request)
    output_form = requested_output or default_output
    if requested_output is not None:
        evidence.append("The user request explicitly constrains the output form.")

    if (
        communication_task == CommunicationTask.FOCUSED_TABLE_DESCRIPTION
        and not _has_highlighted_region(payloads)
    ):
        ambiguities.append("A focused-table description was requested, but no highlighted region was detected.")
        confidence = min(confidence, 0.6)
    if (
        communication_task == CommunicationTask.EVENT_REPORT
        and (input_structure is None or input_structure.shape != InputShape.EVENT_RECORD)
    ):
        ambiguities.append("An event report was requested, but the structure was not confidently classified as an event.")
        confidence = min(confidence, 0.7)

    return TaskContractDecision(
        task_family=_task_family(communication_task),
        report_genre=report_genre,
        communication_task=communication_task,
        output_form=output_form,
        focus_scope=focus_scope,
        selection_source=selection_source,
        confidence=confidence,
        evidence=evidence,
        unresolved_ambiguities=ambiguities,
    )


def resolve_task_contract(
    *,
    inferred: TaskContractDecision,
    selected_genre: ReportGenre,
    genre_source: ReportSelectionSource,
    genre_confidence: float,
    configured_communication_task: CommunicationTask | None,
    configured_output_form: OutputForm | None,
    configured_focus_scope: str | None,
) -> TaskContractDecision:
    """Merge explicit/configured fields over a validated inferred contract."""

    communication_task = (
        configured_communication_task or inferred.communication_task
    )
    _, default_output, default_focus = _defaults_for_task(communication_task)
    output_form = configured_output_form or (
        inferred.output_form
        if configured_communication_task is None
        else default_output
    )
    focus_scope = configured_focus_scope
    if focus_scope is None:
        if configured_communication_task is None:
            focus_scope = inferred.focus_scope
        elif communication_task == CommunicationTask.EVENT_REPORT:
            focus_scope = default_focus

    configured = any(
        value is not None
        for value in (
            configured_communication_task,
            configured_output_form,
            configured_focus_scope,
        )
    )
    source = (
        ReportSelectionSource.EXPERIMENT_CONFIGURATION
        if configured and genre_source != ReportSelectionSource.EXPLICIT_USER_REQUEST
        else genre_source
    )
    confidence = (
        1.0
        if configured_communication_task is not None
        and configured_output_form is not None
        else min(inferred.confidence, genre_confidence)
    )
    evidence = list(inferred.evidence)
    if configured:
        evidence.append("Configured task-contract fields take precedence over inferred values.")

    return TaskContractDecision(
        task_family=_task_family(communication_task),
        report_genre=selected_genre,
        communication_task=communication_task,
        output_form=output_form,
        focus_scope=focus_scope,
        selection_source=source,
        confidence=confidence,
        evidence=list(dict.fromkeys(evidence)),
        unresolved_ambiguities=inferred.unresolved_ambiguities,
    )


def task_contract_agreement(
    inferred: TaskContractDecision,
    resolved: TaskContractDecision,
) -> dict[str, Any]:
    fields = {
        "task_family": inferred.task_family == resolved.task_family,
        "report_genre": inferred.report_genre == resolved.report_genre,
        "communication_task": (
            inferred.communication_task == resolved.communication_task
        ),
        "output_form": inferred.output_form == resolved.output_form,
        "focus_scope": inferred.focus_scope == resolved.focus_scope,
    }
    return {
        "fields": fields,
        "exact_match": all(fields.values()),
        "inferred_confidence": inferred.confidence,
        "inferred_source": inferred.selection_source.value,
        "resolved_source": resolved.selection_source.value,
    }
