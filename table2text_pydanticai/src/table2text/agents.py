"""Build and configure the six PydanticAI agents used by the workflow."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, ModelRetry, ModelSettings, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.output import NativeOutput, PromptedOutput
from pydantic_ai.providers.ollama import OllamaProvider

from .audit import (
    CAUSAL_PATTERN,
    EXPLANATORY_HYPOTHESIS_PATTERN,
    FACTUAL_TITLE_PATTERN,
    FIELD_LABEL_PATTERN,
    FORECAST_PATTERN,
    INTERNAL_CONTROL_PATTERN,
    PREDICTIVE_PATTERN,
    build_evidence_lookup,
    content_requirement_errors,
    extract_number_tokens,
    fact_support_numbers,
    flatten_numbers,
    numbers_supported,
    sentence_support_narrative_stats,
    unsupported_backtick_entities,
    validate_fact_candidates,
    validate_repair_candidate,
)
from .config import Settings
from .capabilities import (
    normalise_semantic_map,
    normalise_event_evidence_queries,
    validate_event_query_priorities,
    validate_evidence_queries,
    validate_semantic_map,
)
from .schemas import (
    AnalysisRoute,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    ClaimPermission,
    ColumnMeaning,
    ColumnRisk,
    DataProfile,
    DataUnderstanding,
    EvidenceCapability,
    ExecutionPlan,
    FactCandidate,
    FactCandidateSet,
    FactLedger,
    InsightCandidate,
    InsightCandidateSet,
    InsightContribution,
    InsightLedger,
    InsightObjective,
    InsightRejection,
    InsightType,
    InsightVerificationFailure,
    InsightVerificationResult,
    InsightVerificationStatus,
    InvestigationTask,
    InputSemanticMap,
    InputShape,
    InterpretationLevel,
    InputStructureProfile,
    ReportComponent,
    ReportGenre,
    ReportPerspective,
    ReportSelectionSource,
    ReportSpecification,
    SemanticRole,
    Severity,
    StructuralField,
    SupportType,
    TableUnderstanding,
    TargetStatus,
    ValidationStrategy,
    VerificationResult,
    VerifiedFact,
    VerifiedInsight,
    WriterAgentDraft,
    WriterSectionDraft,
    WriterSentenceDraft,
)

REPORT_QUALITY_DEFECT_PATTERN = re.compile(
    r"\b("
    r"report|sentence|section|wording|phrasing|selection|structure|"
    r"coherence|redundan|repetit|overstat|understat|omit|unclear|"
    r"unsupported|imprecise|paragraph|insight|genre|hypothesis|game report"
    r")\b",
    re.IGNORECASE,
)


def valid_quality_finding(
    finding: str,
) -> bool:
    return bool(
        REPORT_QUALITY_DEFECT_PATTERN.search(
            finding
        )
    )


@dataclass
class AgentDependencies:
    run_id: str
    payload: dict[str, Any] = field(default_factory=dict)


def build_model(model_specification: str, settings: Settings) -> Any:
    if model_specification.startswith("ollama:"):
        model_name = model_specification.split(":", 1)[1]

        return OllamaModel(
            model_name,
            provider=OllamaProvider(
                base_url=settings.ollama_base_url
            ),
        )

    return model_specification


def _uses_openai_gpt5_defaults(model_specification: str) -> bool:
    provider = ""
    model_name = model_specification
    if ":" in model_specification:
        provider, model_name = model_specification.split(":", 1)

    return (
        provider == "openai"
        or not provider
    ) and model_name.startswith("gpt-5")


def agent_model_settings(
    settings: Settings,
    role: str,
    *,
    temperature: float,
    max_tokens: int,
) -> ModelSettings:
    model_specification = settings.model_for(role)
    kwargs: dict[str, Any] = {"max_tokens": max_tokens}
    if not _uses_openai_gpt5_defaults(model_specification):
        kwargs["temperature"] = temperature
    return ModelSettings(**kwargs)


def output_schema(output_type: type, settings: Settings) -> Any:
    if settings.structured_output_mode == "native":
        return NativeOutput(output_type)

    return PromptedOutput(output_type)


DATA_UNDERSTANDING_INSTRUCTIONS = """
You are the Data Understanding Agent in a Table2Text data-science system.

Combine:
- unit-of-observation reasoning;
- provisional data dictionary interpretation;
- quality and usability assessment;
- identification of methodological risks.

Use only the supplied deterministic profile, input-structure description and
sanitized structural field catalog. The catalog contains operational input
only; held-out reference text has already been removed.

Identify:
- constant and near-constant columns;
- suspicious zero or possible sentinel values;
- candidate identifiers;
- candidate time columns;
- possible target-proxy risks;
- fields that should not be used analytically.

Do not invent provenance, collection locations, units, scientific meanings,
diagnoses, interventions, or source metadata.

Preserve exact table and column names.

For structured input, create an `InputSemanticMap` that explains what the
record and its fields represent. Use only the broad controlled semantic roles
provided by the schema. Keep domain labels such as scoring, votes, revenue or
assists in the free-text `label` and `description`; do not invent a new role.

The semantic map is a broad analytical index for the supplied structure. Include
every event, participant and entity binding that may support a faithful report,
especially every aggregate participant-level measure and every substantive
nested-entity measure. Copy every `path_pattern` verbatim from the structural
catalog, including any `*` wildcards. A wildcard pattern binds the repeated
field family once: never expand it into concrete participant, entity, period or
record keys, and never bind the same catalog path twice.
Label wildcard bindings collectively, such as "Participant name" or "Entity
points"; never label a wildcard as one particular member such as home,
visitor, first or second.

For every event measure, assign `analytical_function` as a semantic judgement:
- `outcome` is the aggregate measure that determines the recorded event result;
- `outcome_component` is a substantive participant or entity measure that
  contributes to comparison but is not itself the aggregate result;
- `performance` is a substantive recorded achievement or output;
- `participation` is duration, exposure or presence rather than
  substantive performance;
- `context` is a measure whose purpose is descriptive context.
Do not treat playing time, duration or exposure as performance. This
classification interprets field meaning; it does not calculate a result.

Prioritise bindings in this order:
- event context, time, location and status;
- participant and nested-entity identifiers;
- participant-level event outcome measures;
- all participant-level outcome components, then other participant-level
  measures that can support contrasts;
- all substantive entity-level measures, then participation measures.

For an event record, include report-critical roles before optional
administrative fields: human-readable participant identifiers, human-readable
nested entity identifiers when present, the aggregate outcome, event status,
participant measures and entity measures. Include enough date and location
fields to reconstruct the supplied context. Prefer human-readable names over
technical IDs or codes. Do not omit report-critical performance measures in
order to include technical record IDs, redundant name components, pre-event
records, nested status flags or administrative fields.

For event records, do not cap participant contrast measures or entity measures.
When a nested entity collection has numeric measures, bind each substantive
performance or outcome-component measure before optional participation
measures.

Omit low-value administrative fields and exhaustive period/component
measures. For a nested single-event record, top-level constancy is expected:
describe its scope once rather than creating a separate constant-column risk
for every event-context or container field.

Every semantic binding must use an exact table name and exact path pattern from
the supplied structural catalog. Bind the fields needed to identify context,
participants, nested entities, outcome measures and other salient measures.
When the same measure appears at aggregate and segment/sub-event levels, bind
the event outcome to the participant-level aggregate and keep the semantic
levels distinct. Do not substitute a period, phase or component value for an
event total.
Do not encode an analytical conclusion in a binding. Recommend `event_report`
when the sanitized structure represents one event with participants or
entities, even when the later reporting request may be generic.

Also recommend a complete communication contract in the semantic map when the
request and operational structure support it:
- one bounded event with participants and outcomes: `event_report`,
  `multi_paragraph_report`, and `event_recap`;
- a table with an explicit highlighted region: `focused_table_description`,
  `one_sentence`, and `highlighted_cells`;
- an attribute-oriented meaning representation: `attribute_verbalisation` and
  `short_text`;
- subject-relation-object records: `triple_verbalisation` and `short_text`.
Use `dataset_overview` or `data_science_report` when no specialised
communication task is supported. Infer from field structure and the user
request, never from dataset IDs, benchmark labels or held-out references.
Leave a recommendation unset when it is genuinely ambiguous.

Semantic interpretation is not factual evidence. Do not write event results,
rankings or report prose in the semantic map.
Return structured output only.
"""


def build_data_understanding_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("data_understanding"),
            settings,
        ),
        name="data_understanding_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            DataUnderstanding,
            settings,
        ),
        instructions=DATA_UNDERSTANDING_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "data_understanding",
            temperature=0.0,
            max_tokens=7_000,
        ),
        retries={"output": 2},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: DataUnderstanding,
    ) -> DataUnderstanding:
        valid_tables = set(
            context.deps.payload["table_names"]
        )
        valid_columns = {
            table_name: set(columns)
            for table_name, columns in context.deps.payload["columns"].items()
        }

        if (
            output.profile_fingerprint
            != context.deps.payload["fingerprint"]
        ):
            raise ModelRetry(
                "Use the exact supplied profile_fingerprint."
            )

        for table in output.tables:
            if table.table_name not in valid_tables:
                raise ModelRetry(
                    f"Unknown table: {table.table_name}"
                )

            for meaning in table.column_meanings:
                if meaning.column_name not in valid_columns[table.table_name]:
                    raise ModelRetry(
                        f"Unknown column: {meaning.column_name}"
                    )

            for risk in table.column_risks:
                if risk.column_name not in valid_columns[table.table_name]:
                    raise ModelRetry(
                        f"Unknown risk column: {risk.column_name}"
                    )

        catalog = [
            StructuralField.model_validate(item)
            for item in context.deps.payload.get(
                "structural_catalog",
                [],
            )
        ]
        semantic_errors = validate_semantic_map(
            normalise_semantic_map(output.semantic_map),
            catalog,
        )
        if semantic_errors:
            raise ModelRetry(
                "Semantic-map validation failed:\n- " + "\n- ".join(semantic_errors[:12])
            )
        output = output.model_copy(
            update={
                "semantic_map": normalise_semantic_map(output.semantic_map)
            }
        )
        if context.deps.payload.get("semantic_map_required") and (
            output.semantic_map is None or not output.semantic_map.bindings
        ):
            raise ModelRetry(
                "Structured operational input requires a non-empty semantic "
                "map using exact catalog paths."
            )

        return output

    return agent


ORCHESTRATOR_INSTRUCTIONS = """
You are the Orchestrator and Investigation Planner.

Create a frozen analytical plan before analytical results are observed.
Define bounded-insight objectives as questions before results are observed.
Objectives may use the request, report specification, table and column
structure, and planned tasks, but must not contain result values or predicted
conclusions.

The user wants a useful data-science report, not a dump of every statistic.

Rules:
- Use exact table and column names.
- Choose analyses relevant to the user's request.
- Normally create 2 to 8 tasks.
- Do not run prediction merely because a numeric column exists.
- A predictive target must be user-selected, metadata-confirmed, or explicitly
  marked as an experimental candidate.
- Do not mark a target as user-selected unless the request names it.
- Use chronological validation when a usable time field exists.
- Forecasting requires a target, reliable time ordering, rolling evaluation,
  and naive baselines.
- Causal work is feasibility-first.
- Include a report specification with a target length and word ceiling. Leave
  finding and supporting-fact count limits unset; relevance, support,
  non-duplication and the word ceiling govern report selection.
- Use only evidence capabilities listed as available in the supplied input.
- Never plan an event result, entity ranking, temporal change, milestone, or
  comparison capability that is not available.
- Do not let one analytical route dominate a general dataset-understanding
  report.
- Do not let one evidence subtype dominate a general dataset-understanding
  report.
- For requests asking to understand a dataset, require dataset overview,
  data quality, strongest relationships, limitations, and next steps.
- For general requests to report findings, cover overview, data quality, the
  strongest relationships, and limitations/next steps unless the user narrowed
  the scope.
- Prediction and forecasting remain optional and must not be added unless the
  request or confirmed metadata supports them.
- Do not rewrite or replace the user's objective with a different objective.
- Negative and insufficiency findings are valid.
- For a generic request, honour the controller-selected genre derived from the
  sanitized semantic map. A high-confidence single event should remain an
  event report; do not turn it into a flat-table data-science report. Explicit
  user instructions and experiment configuration still take priority. Genre
  controls communication, never factual permission.
- Use neutral perspective by default. Subject-centred perspective may
  prioritise verified facts about an explicitly named subject, but it must not
  change numbers, claim permissions, or evaluative strength.
- A generic report may ask which findings jointly describe the strongest
  structure, which contrast is strongest and non-redundant, whether variables
  overlap substantially, which quality issue matters most, and what the reader
  should remember.
- A sports report may ask which verified facts describe the result, salient
  performances, team contrasts, and supported conventional milestones.
- An event report must request event_result, event_context,
  participant_record_context, score_progression, event_sequence,
  leading_performance, main_contrast and scope_limitations content slots only
  when their required evidence or safety constraints are available. It must not
  treat reference text as operational evidence, and sequence evidence must not
  be inflated into unsupported causality, momentum or turning-point claims.
- When a semantic map is supplied, create generic evidence queries using only
  semantic binding IDs. Use `retrieve` for context, `compare` for participant
  measures, and `rank` for entity measures. Do not hard-code field aliases or
  domain-specific extraction rules.
- Every field whose name ends in `_binding_id` or `_binding_ids` must contain
  only exact `binding_id` strings from the supplied ID-only semantic binding
  catalogue. Never put a path pattern, label or column name in those fields.
- Follow these generic query shapes:
  * `event_context`: retrieve one or more event-level context/time/location
    value IDs; no entity ID is required.
  * `event_status`: retrieve one or more event-level status value IDs.
  * `event_outcome`: compare exactly one participant-level outcome value ID and
    set `entity_binding_id` to a participant-identifier ID.
  * `entity_ranking`: rank exactly one entity-level measure value ID, set
    `entity_binding_id` to an entity-identifier ID and optionally set
    `group_binding_id` to a participant-identifier ID.
  * `participant_comparison` or `event_contrast`: compare exactly one
    participant-level measure value ID and set `entity_binding_id` to a
    participant-identifier ID.
- Query only measures present in the semantic binding catalogue. The broader
  structural catalog is not permission to reference an unbound measure.
- Query questions are pre-result analytical questions. Do not place observed
  values, winners, rankings or conclusions in a query.
- For a supported event report, query event context, event status, the outcome
  measure, all available substantive entity rankings, and all participant
  contrasts that can support a faithful report.
- Treat the semantic binding's `analytical_function` as the content-priority
  contract. Prefer `performance` and `outcome_component` for entity rankings.
  Do not rank `participation` when substantive entity measures are available
  unless the user's request explicitly asks about duration, exposure or
  participation.
- For participant contrasts, prefer distinct `outcome_component` measures
  before general performance or context measures. Relate components as
  descriptive contrasts only; do not imply that they caused the result.
- Do not query the same measure/entity combination twice under different names
  or repeat event context as a data-quality query.
- Use these evidence types exactly: event_outcome for outcome comparison;
  event_context or event_status for context retrieval; entity_ranking for ranking;
  entity_performance for entity performance; and participant_comparison or
  event_contrast for participant comparisons.
- Do not place a result, statistic, double-double, hat-trick, dominance claim,
  or other predicted conclusion in an insight objective.
- Set frozen=true.
"""


def build_orchestrator_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("orchestrator"),
            settings,
        ),
        name="orchestrator_and_investigation_planner",
        deps_type=AgentDependencies,
        output_type=output_schema(
            ExecutionPlan,
            settings,
        ),
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "orchestrator",
            temperature=0.1,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: ExecutionPlan,
    ) -> ExecutionPlan:
        valid_tables = set(
            context.deps.payload["table_names"]
        )
        valid_columns = {
            table_name: set(columns)
            for table_name, columns in context.deps.payload["columns"].items()
        }
        allow_experimental = context.deps.payload["allow_experimental_targets"]
        selected_report_genre = context.deps.payload.get("selected_report_genre")

        if not output.frozen:
            raise ModelRetry("Set frozen=true.")

        user_request = context.deps.payload.get("user_request")
        if user_request and output.objective.strip() != user_request.strip():
            raise ModelRetry(
                "Use the exact supplied user objective; do not substitute a new purpose."
            )

        if not output.tasks:
            raise ModelRetry(
                "Create at least one investigation task."
            )

        if (
            selected_report_genre
            and output.report_specification.genre.value != selected_report_genre
        ):
            raise ModelRetry(
                f"Use the controller-selected report genre exactly: {selected_report_genre}."
            )

        seen: set[str] = set()
        available_capabilities = {
            EvidenceCapability(value)
            for value in context.deps.payload.get(
                "available_capabilities",
                [],
            )
        }

        for task in output.tasks:
            if task.task_id in seen:
                raise ModelRetry(
                    f"Duplicate task ID: {task.task_id}"
                )
            seen.add(task.task_id)

            if (
                task.capability is not None
                and task.capability not in available_capabilities
            ):
                raise ModelRetry(
                    f"Task {task.task_id} selects unavailable capability "
                    f"{task.capability.value}."
                )

            if task.table_name not in valid_tables:
                raise ModelRetry(
                    f"Unknown table: {task.table_name}"
                )

            referenced = [
                *task.columns,
                task.target_column,
                task.time_column,
                task.exposure_column,
                task.outcome_column,
                *task.confounder_columns,
            ]

            for column in [value for value in referenced if value]:
                if column not in valid_columns[task.table_name]:
                    raise ModelRetry(
                        f"Unknown column `{column}` in `{task.table_name}`."
                    )

            if (
                task.target_status == TargetStatus.EXPERIMENTAL_CANDIDATE
                and not allow_experimental
            ):
                raise ModelRetry(
                    "Experimental targets are disabled by configuration."
                )

            if (
                task.route
                in {
                    AnalysisRoute.PREDICTIVE,
                    AnalysisRoute.FORECASTING,
                }
                and not task.target_column
            ):
                raise ModelRetry(
                    f"{task.task_id} requires a target column."
                )

        used_routes = {
            task.route
            for task in output.tasks
        }

        if not used_routes.issubset(
            set(output.route_order)
        ):
            raise ModelRetry(
                "route_order must include every route used by the tasks."
            )

        if settings.enable_insight_synthesis and not output.insight_objectives:
            raise ModelRetry(
                "Create a small set of frozen insight objectives as questions."
            )

        objective_ids: set[str] = set()
        for objective in output.insight_objectives:
            if not objective.objective_id.strip():
                raise ModelRetry("Insight objective IDs must not be empty.")

            if objective.objective_id in objective_ids:
                raise ModelRetry(
                    f"Duplicate insight objective ID: {objective.objective_id}"
                )
            objective_ids.add(objective.objective_id)

            if not objective.question.strip().endswith("?"):
                raise ModelRetry(
                    "Insight objectives must be questions, not conclusions."
                )

            if re.search(r"(?<!\w)\d+(?:[.,]\d+)?%?", objective.question):
                raise ModelRetry(
                    "Insight objectives must not contain result values."
                )

            unknown_task_ids = (
                set(objective.relevant_task_ids) - seen
            )
            if unknown_task_ids:
                raise ModelRetry(
                    "Insight objectives reference unknown task IDs: "
                    f"{sorted(unknown_task_ids)}"
                )

        if (
            output.report_specification.genre
            in {
                ReportGenre.EVENT_REPORT,
                ReportGenre.SPORTS_GAME_REPORT,
            }
            and not context.deps.payload.get(
                "event_genre_allowed",
                False,
            )
        ):
            raise ModelRetry(
                "event_report requires an explicit request or experiment "
                "configuration."
            )

        if (
            user_request
            and output.report_specification.genre
            not in {
                ReportGenre.EVENT_REPORT,
                ReportGenre.SPORTS_GAME_REPORT,
            }
            and re.search(
                r"\b(understand|overview|summari[sz]e|describe|report findings|strongest findings)\b",
                user_request,
                re.IGNORECASE,
            )
        ):
            required = set(output.report_specification.required_components)
            expected = {
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            }
            if not expected.issubset(required):
                raise ModelRetry(
                    "General dataset-understanding reports must require overview, "
                    "data quality, strongest relationships, and limitations/next steps."
                )

        semantic_map_payload = context.deps.payload.get("semantic_map")
        semantic_map = (
            InputSemanticMap.model_validate(semantic_map_payload) if semantic_map_payload else None
        )
        structural_catalog = [
            StructuralField.model_validate(item)
            for item in context.deps.payload.get(
                "structural_catalog",
                [],
            )
        ]
        if (
            selected_report_genre
            in {
                ReportGenre.EVENT_REPORT.value,
                ReportGenre.SPORTS_GAME_REPORT.value,
            }
            and semantic_map is not None
            and semantic_map.bindings
        ):
            output = output.model_copy(
                update={
                    "evidence_queries": normalise_event_evidence_queries(
                        queries=output.evidence_queries,
                        semantic_map=semantic_map,
                        tasks=output.tasks,
                        available_capabilities=available_capabilities,
                        request=user_request or "",
                        structural_catalog=structural_catalog,
                    )
                }
            )
        query_errors = validate_evidence_queries(
            output.evidence_queries,
            semantic_map,
            structural_catalog,
            task_ids={task.task_id for task in output.tasks},
            available=available_capabilities,
            task_capabilities={
                task.task_id: task.capability
                for task in output.tasks
            },
        )
        if selected_report_genre in {
            ReportGenre.EVENT_REPORT.value,
            ReportGenre.SPORTS_GAME_REPORT.value,
        }:
            query_errors.extend(
                validate_event_query_priorities(
                    output.evidence_queries,
                    semantic_map,
                    user_request or "",
                )
            )
        if query_errors:
            binding_guide = (
                ", ".join(
                    f"{binding.binding_id}={binding.label} "
                    f"({binding.role.value}/{binding.level.value}/"
                    f"{binding.analytical_function.value if binding.analytical_function else 'none'})"
                    for binding in semantic_map.bindings
                )
                if semantic_map is not None
                else "none"
            )
            raise ModelRetry(
                "Evidence-query validation failed:\n- "
                + "\n- ".join(query_errors[:12])
                + "\nUse only these exact binding IDs: "
                + binding_guide
            )
        if (
            output.maximum_facts is not None
            and len(output.evidence_queries) > output.maximum_facts
        ):
            raise ModelRetry(
                "The number of evidence queries must not exceed the fact "
                "budget because each query requires verifier review."
            )

        if (
            selected_report_genre
            in {
                ReportGenre.EVENT_REPORT.value,
                ReportGenre.SPORTS_GAME_REPORT.value,
            }
            and semantic_map is not None
            and semantic_map.bindings
        ):
            query_signatures: set[
                tuple[str, tuple[str, ...], str | None, str | None]
            ] = set()
            duplicate_query_ids: list[str] = []
            for query in output.evidence_queries:
                signature = (
                    query.operation.value,
                    tuple(query.value_binding_ids),
                    query.entity_binding_id,
                    query.group_binding_id,
                )
                if signature in query_signatures:
                    duplicate_query_ids.append(query.query_id)
                query_signatures.add(signature)
            if duplicate_query_ids:
                raise ModelRetry(
                    "Remove duplicate semantic queries for the same operation, "
                    "measure and entity bindings: "
                    + ", ".join(duplicate_query_ids)
                )

            binding_roles = {binding.role for binding in semantic_map.bindings}
            query_evidence_types = {query.evidence_type for query in output.evidence_queries}
            required_evidence_types: set[str] = set()
            if (
                SemanticRole.OUTCOME_MEASURE in binding_roles
                and EvidenceCapability.EVENT_OUTCOME in available_capabilities
            ):
                required_evidence_types.add("event_outcome")
            if binding_roles & {
                SemanticRole.CONTEXT,
                SemanticRole.TIME,
                SemanticRole.LOCATION,
            }:
                required_evidence_types.add("event_context")
            if SemanticRole.STATUS in binding_roles:
                required_evidence_types.add("event_status")

            missing_evidence_types = required_evidence_types - query_evidence_types
            if missing_evidence_types:
                raise ModelRetry(
                    "The event plan is missing supported semantic evidence "
                    "types: " + ", ".join(sorted(missing_evidence_types))
                )

        return output

    return agent


EVIDENCE_INSTRUCTIONS = """
You are the Evidence Analyst Agent.

The analytical engine has already produced a rich Evidence Ledger containing
calculated values, practical interpretations, methodological limitations,
salience, and prohibited interpretations.

Create atomic verified-fact candidates for the verifier.

Rules:
- Every candidate must cite exact evidence IDs.
- Preserve calculated values exactly.
- Preserve negative and insufficiency findings.
- Do not convert the evidence into a final report.
- Do not create new statistics or domain explanations.
- Carry forward prohibited interpretations and material caveats.
- Exclude evidence marked eligible_for_writer=false.
- Do not make every candidate a headline; preserve recommended_use.
- Do not select facts only from the final evidence items or a single route.
- Preserve dataset overview facts, important quality facts, strong or moderate
  relationships, negative modelling findings, and limitations.
- Do not promote small or weak effects to main findings when stronger unused
  evidence is available.
- Do not copy internal prohibited interpretations into fact_summary.
- For generic semantic-query evidence, use the query's semantic label,
  operation and structured metrics to propose the directly supported fact.
  The executor intentionally does not author winner, ranking or comparison
  sentences. Do not merely repeat "validated semantic query result".
- A compare result may be described only in the direction shown by its ordered
  records. A rank result must preserve the supplied order, values and tie
  annotations. Compose identities only from the supplied entity, group and
  context values.
- For focused-table evidence, preserve direct highlighted role/value pairs,
  supplied highlighted record groups, supplied highlighted-set contrasts, and
  supplied focused record-style relations or list-page relations as
  writer-eligible fact candidates. If the evidence supplies a highlighted
  record-group summary, preserve it as a first-class candidate instead of
  dropping later highlighted rows for brevity. Keep lower/higher contrast
  wording scoped to the highlighted cells unless a cited table-wide rank fact
  explicitly supports a broader claim.
"""


def build_evidence_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("evidence"),
            settings,
        ),
        name="evidence_analyst_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            FactCandidateSet,
            settings,
        ),
        instructions=EVIDENCE_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "evidence",
            temperature=0.0,
            max_tokens=9_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: FactCandidateSet,
    ) -> FactCandidateSet:
        from .schemas import EvidenceLedger

        ledger = EvidenceLedger.model_validate(
            context.deps.payload["evidence_ledger"]
        )

        errors = validate_fact_candidates(
            output,
            ledger,
        )
        valid_candidates: list[FactCandidate] = []
        dropped_notes: list[str] = []
        seen_candidate_ids: set[str] = set()
        for candidate in output.candidates:
            if candidate.candidate_id in seen_candidate_ids:
                dropped_notes.append(
                    f"Dropped duplicate fact candidate {candidate.candidate_id}."
                )
                continue
            seen_candidate_ids.add(candidate.candidate_id)
            candidate_errors = validate_fact_candidates(
                FactCandidateSet(candidates=[candidate]),
                ledger,
            )
            if candidate_errors:
                dropped_notes.append(
                    f"Dropped invalid fact candidate {candidate.candidate_id}: "
                    + "; ".join(candidate_errors)
                )
                continue
            valid_candidates.append(candidate)

        if dropped_notes and valid_candidates:
            output = output.model_copy(
                update={
                    "candidates": valid_candidates,
                    "synthesis_notes": [
                        *output.synthesis_notes,
                        *dropped_notes,
                    ],
                }
            )
            errors = validate_fact_candidates(
                output,
                ledger,
            )

        if errors:
            raise ModelRetry(
                "Fact candidate validation failed:\n- "
                + "\n- ".join(errors[:10])
            )

        return output

    return agent


VERIFIER_INSTRUCTIONS = """
You are the Fact Verification Agent.

Verify each candidate against the cited evidence.

Review every candidate exactly once.

Reject:
- unsupported numbers;
- unsupported entities;
- direction or polarity changes;
- permissions absent from the evidence;
- facts derived from excluded evidence;
- predictive or forecast interpretations without validation;
- causal wording without a verified causal design.
- reversed ordering, winner/loser labels, ranking positions or comparison
  direction relative to semantic-query metrics;
- event meanings not licensed by the query's semantic label and capability.

Judge every candidate independently.

A direct deterministic fact such as a row count, column count,
missing-value count, constant-field finding, correlation, or validated
group comparison can be fully valid even when it is simple or less
narratively interesting than another candidate.

Do not reject overview or data-quality facts merely to keep the ledger
concise. Reject them only when they are unsupported, numerically
inconsistent, semantically escalated, or methodologically invalid.

Do not rewrite candidates into final report prose.
"""


def build_verifier_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("verifier"),
            settings,
        ),
        name="fact_verification_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            VerificationResult,
            settings,
        ),
        instructions=VERIFIER_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "verifier",
            temperature=0.0,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: VerificationResult,
    ) -> VerificationResult:
        candidates = FactCandidateSet.model_validate(
            context.deps.payload["fact_candidates"]
        )

        expected = {
            candidate.candidate_id
            for candidate in candidates.candidates
        }
        received = [
            review.candidate_id
            for review in output.reviews
        ]

        if len(received) != len(set(received)):
            raise ModelRetry(
                "Duplicate fact reviews are not allowed."
            )

        if set(received) != expected:
            raise ModelRetry(
                "Review every candidate exactly once. "
                f"Missing={sorted(expected - set(received))}; "
                f"extra={sorted(set(received) - expected)}"
            )

        return output

    return agent


INSIGHT_SYNTHESIS_INSTRUCTIONS = """
You are the Evidence Analyst performing a second bounded synthesis pass.

The first pass identified evidence-grounded facts. This pass relates verified
facts into distinct, useful, evidence-constrained interpretations.

Definitions:
- Finding: a directly supported observation.
- Bounded insight: an interpretation formed by relating verified findings.
- Analytical implication: why the related findings matter for interpretation
  or analysis, without proposing why the observed pattern exists.
- Event synthesis: a supported relationship among an event outcome, context,
  rankings, performances or participant contrasts. It can be useful narrative
  synthesis without a deeper data-science implication.
- Hypothesis: a plausible explanation requiring additional testing.

Rules:
1. Use only supplied writer-ready verified facts and their referenced
   deterministic evidence.
2. Never calculate a statistic.
3. Never introduce a number absent from supplied support.
4. Never introduce an entity absent from supplied support.
5. Every candidate must cite source fact IDs.
6. Every cited fact ID must contribute materially to the statement.
7. A bounded insight normally requires at least the configured minimum number
   of source facts in analytical reports.
8. Single-fact exceptions are permitted for anomaly, data-quality
   implication, a direct narrative summary supported by one compound fact, or
   event-report evidence that is already a structured outcome, context,
   status, ranking, performance, or participant contrast.
   Focused-table descriptions are also a single-fact exception when the
   highlighted cell evidence plus supplied table context expresses the
   requested relation.
   Structured-record verbalisation tasks are also a single-fact exception
   when the supplied attributes or triples contain the complete meaning
   representation to express.
9. Do not merely paraphrase one fact, or several facts that repeat the same
   result, and label the restatement an insight.
10. Do not turn correlation into causation.
    Use outcome_association, never outcome_driver, for descriptive evidence.
11. Do not use drives, causes, explains, leads to, results in, or equivalent
    causal wording without explicit causal permission.
12. Do not add domain knowledge from memory.
13. Do not infer collection location, frequency, provenance, or measurement
    process.
14. Do not claim that a variable is useless or universally redundant.
15. Describe overlap as containing highly overlapping information in this
    dataset.
16. Set `contribution` to `analytical_implication` for analytical reports,
   `event_synthesis` for event reports, and `descriptive_synthesis` for a
   concise dataset overview, focused table description, direct answer, or
   other short grounded verbalisation task.
17. For `analytical_implication`, `why_it_matters` must add a concrete,
   evidence-bounded consequence for interpretation or analysis; it must not
   restate coefficients, effect labels, or the candidate statement.
18. For `event_synthesis`, `why_it_matters` may be omitted. Relating supported
   rankings, performances, outcomes or participant contrasts is sufficient
   when it contributes to the event report and remains event-scoped.
19. For focused-table evidence, a useful descriptive synthesis may infer the
   table relation expressed by the highlighted cell using only page/section
   titles, headers, row context, highlighted-cell markers and supplied source
   text. It may rewrite cell-context evidence into a natural proposition, but
   it must not use held-out references or outside knowledge. Set
   `interpretation_level` to `bounded_insight`, `contribution` to
   `descriptive_synthesis`, and `insight_type` to `narrative_summary` for this
   kind of candidate; do not label it as a direct `finding`.
20. For focused-table tasks, row co-entities, headings and source text help
   identify the table relation. They are not automatically the grammatical
   subject of the output. Prefer the concise proposition conveyed by the
   highlighted cell when the local context supports it; use a conservative
   selected-cell description only when the relation remains ambiguous.
21. When focused-table evidence includes span-aware logical row context,
   highlighted role/value pairs, placeholder roles, or page-title subject
   candidates, treat those structured fields as higher priority than raw
   adjacent-cell context. A page-title subject candidate may fill a missing
   role only when the supplied logical-row evidence and table context support
   that reading.
22. For one-sentence focused-table tasks, centre the candidate on the
   highlighted role/value pair and the most specific supported primary subject
   candidate. Treat non-highlighted same-row values as context; include them
   only when they are needed to identify the highlighted relation. Do not
   combine a page-title subject candidate with row co-entities into a joint
   subject unless the supplied evidence explicitly represents a combined
   entity. Use supplied highlighted-measure comparisons when they support a
   concise outcome-like relation, but do not calculate new comparisons.
   When supplied highlighted-set contrasts relate multiple highlighted values
   under the same header, prefer scoped wording such as "among the highlighted
   rows/entities" and lower/higher language over table-wide highest/lowest
   wording unless a table-wide rank fact is explicitly cited.
   When supplied highlighted record groups preserve multiple highlighted rows,
   keep all grouped records that contribute to the focused proposition; do not
   drop later highlighted records simply to shorten the sentence.
   When supplied focused record-style relations pair a highlighted group or
   section label with a highlighted record-like value, prefer that natural
   proposition over wording about cell coordinates, headers, or "Total" rows.
   When supplied focused list-page relations connect a highlighted cell to a
   list page title, section, and column header, prefer that proposition over
   unrelated same-row details.
23. For structured-record verbalisation tasks, infer only the natural
   sentence-level relation licensed by the supplied attributes or triples.
   Preserve every supplied entity, relation and value needed by the task, but
   do not introduce dataset profiling, data-quality, correlation, modelling or
   outside/domain facts.
24. A possible reason why a pattern exists is a hypothesis, including claims
   that a pattern may reflect a dependency, data artifact, collection process,
   or unmeasured mechanism. Do not hide a hypothesis in `why_it_matters`, a
   limitation, or a recommendation.
25. A hypothesis must be explicitly labelled as a hypothesis.
26. A hypothesis must not be suitable for the main report unless hypotheses
   are explicitly allowed.
27. Preserve deterministic qualitative strength labels. Do not relabel a
   strong association as moderate, or vice versa.
28. For missingness, prefer the directly supported scope of the complete-case
   subset over an assumed bias mechanism. For duplicates, describe a possible
   influence only as a bounded methodological risk, never as a measured effect.
29. Do not claim that data are complete, contain no missing values, or contain
   no duplicates unless the cited facts reference evidence that measured that
   exact data-quality property.
30. Include limitations or alternative explanations where needed, but keep
   unverified explanations in explicitly labelled hypothesis candidates.
31. Generate every distinct, report-relevant insight supported by the supplied
   facts. Do not target a fixed number. Stop when additional candidates would
   only duplicate existing synthesis or add weak, irrelevant material.

Return structured output only.
"""


INSIGHT_VERIFIER_INSTRUCTIONS = """
You are the Fact Verifier reviewing bounded insight candidates.

A candidate can contain correct individual facts while still making an
unsupported interpretation. Review each candidate against only the supplied
verified facts and deterministic evidence.

For each candidate decide verified, verified_with_caveat, hypothesis_only, or
rejected.

For every record explicitly set:
- `adds_bounded_synthesis`: true only when the statement relates findings and
  adds more than a direct finding restatement;
- `analytical_implication_supported`: true only when `why_it_matters` is a
  concrete, evidence-bounded analytical implication rather than a paraphrase;
- `contains_hypothesis`: true whenever the statement or analytical implication
  proposes a possible explanation that requires further testing.

A record may be verified or verified_with_caveat only when
`adds_bounded_synthesis` is true and `contains_hypothesis` is false. For a
data-science report, `analytical_implication_supported` must also be true. For
an event report, a supported event synthesis does not require a separate
analytical implication: rankings, performances, outcomes and participant
contrasts can provide bounded narrative synthesis. In an event report, a
single structured outcome, context, status, ranking, performance, or
participant contrast can be report-worthy event synthesis when it fills the
selected report contract. For focused-table evidence, a statement that relates
the highlighted value to supplied page/section title, row context, headers and
source text may be verified as descriptive synthesis even without a separate
analytical implication. It is acceptable for this relation to be supported by
one compound focused-table fact when that fact carries the highlighted value
and its local table context. If the evidence contains span-aware logical
role/value pairs or page-title subject candidates, evaluate the statement
against those structured fields before raw adjacent-cell context. If the
evidence contains a concise output focus, highlighted-measure comparison,
highlighted-set contrast, focused record-style relation, or focused list-page
relation, prefer the shortest supported statement centred on highlighted
values and required subject context. A lower/higher contrast must remain
scoped to the highlighted set unless a cited table-wide rank fact supports a
broader highest/lowest claim. Do not require unhighlighted numeric row context
in the final wording unless it is needed for disambiguation.
For structured-record verbalisation evidence, a concise sentence expressing
the supplied attributes or triples may be verified as descriptive synthesis
when it preserves the supplied entities, relations and values and adds no
outside information.
Outside those event, focused-table and structured-record cases, a
direct-finding restatement must be rejected. A candidate containing a possible
explanation must be
hypothesis_only or rejected.

Check that every cited fact exists and genuinely contributes; every number,
table, column, group and entity is supported; the facts jointly support the
statement; and the wording adds useful synthesis rather than renaming one
fact. Match wording strength to evidence strength. Do not introduce causality,
outside domain explanations, collection metadata, or generalisations beyond
the analysed dataset. Preserve needed limitations and identify hypotheses
explicitly. Exclude hypotheses from the main report unless explicitly allowed.
Treat explanations involving possible dependencies, artifacts, collection
processes, or unmeasured mechanisms as hypotheses, even when phrased as a next
step. Do not call a deterministically strong relationship moderate.
Assess salience against the request and selected report genre.

Do not approve a claim merely because it sounds plausible. Do not use outside
knowledge or calculate new values. Preserve or safely weaken candidate
wording; never strengthen it. Return one record for every candidate.
"""


HYPOTHESIS_LABEL_PATTERN = re.compile(
    r"\b(hypothesis|hypothesise|hypothesize|hypothesised|hypothesized)\b",
    re.IGNORECASE,
)

UNIVERSAL_GENERALISATION_PATTERN = re.compile(
    r"\b(always|in general|universally|proves that|demonstrates that all)\b",
    re.IGNORECASE,
)

MISSINGNESS_CLAIM_PATTERN = re.compile(
    r"\b(no|without|zero)\s+missing(?:ness|\s+(?:data|values?))?\b|"
    r"\bmissing(?:ness|\s+(?:data|values?))\b|"
    r"\b(?:complete data|data (?:are|is|was|were) complete|completeness)\b",
    re.IGNORECASE,
)

DUPLICATE_CLAIM_PATTERN = re.compile(
    r"\b(no|without|zero)\s+(?:exact\s+)?duplicates?\b|"
    r"\bduplicates?|deduplicat(?:e|ed|ion)\b",
    re.IGNORECASE,
)

EVENT_REPORT_META_OMISSION_PATTERN = re.compile(
    r"\b(?:this\s+)?(?:report|summary)\b[^.]{0,120}"
    r"\b(?:does\s+not|did\s+not|not|no)\b[^.]{0,80}"
    r"\b(?:analy[sz]e[ds]?|include[ds]?|report(?:ed)?|cover(?:ed)?)\b|"
    r"\b(?:detailed\s+)?(?:event\s+)?(?:chronology|play[- ]by[- ]play|sequence)\b"
    r"[^.]{0,120}\b(?:not|no)\b[^.]{0,80}"
    r"\b(?:analy[sz]ed|included|reported|covered)\b",
    re.IGNORECASE,
)

SINGLE_FACT_INSIGHT_TYPES = {
    InsightType.ANOMALY,
    InsightType.DATA_QUALITY_IMPLICATION,
    InsightType.NARRATIVE_SUMMARY,
}

EVENT_INSIGHT_GENRES = {
    ReportGenre.EVENT_REPORT,
    ReportGenre.SPORTS_GAME_REPORT,
}

STRONG_PERMISSIONS = {
    ClaimPermission.CAUSAL,
    ClaimPermission.PREDICTIVE,
    ClaimPermission.FORECAST,
}


def _normalise_statement(value: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        value.lower(),
    ).strip()


def _statement_tokens(value: str) -> set[str]:
    return {
        token
        for token in _normalise_statement(value).split()
        if len(token) > 2
    }


def _materially_duplicate_statements(
    left: str,
    right: str,
) -> bool:
    left_normalised = _normalise_statement(left)
    right_normalised = _normalise_statement(right)

    if left_normalised == right_normalised:
        return True

    left_tokens = _statement_tokens(left)
    right_tokens = _statement_tokens(right)

    if not left_tokens or not right_tokens:
        return False

    return (
        len(left_tokens & right_tokens)
        / len(left_tokens | right_tokens)
        >= 0.85
    )


def _safe_fact_permissions(
    facts: list[VerifiedFact],
) -> set[ClaimPermission]:
    if not facts:
        return set()

    permissions = {
        permission
        for fact in facts
        for permission in fact.claim_permissions
    }

    for permission in STRONG_PERMISSIONS:
        if not all(
            permission in fact.claim_permissions
            for fact in facts
        ):
            permissions.discard(permission)

    return permissions


def _insight_support_numbers(
    facts: list[VerifiedFact],
    evidence_ledger: Any,
) -> list[float]:
    return [
        number
        for fact in facts
        for number in fact_support_numbers(
            fact,
            evidence_ledger,
        )
    ]


def _schema_entities_for_evidence_ids(
    evidence_ids: set[str],
    evidence_ledger: Any,
) -> set[str]:
    lookup = build_evidence_lookup(evidence_ledger)
    return {
        entity
        for evidence_id in evidence_ids
        if evidence_id in lookup
        for entity in [
            *lookup[evidence_id].source_tables,
            *lookup[evidence_id].source_columns,
        ]
        if entity
    }


def _entity_occurs(
    entity: str,
    statement: str,
) -> bool:
    return bool(
        entity
        and re.search(
            rf"(?<!\w){re.escape(entity)}(?!\w)",
            statement,
            re.IGNORECASE,
        )
    )


def _unsupported_insight_entities(
    *,
    statement: str,
    facts: list[VerifiedFact],
    evidence_ledger: Any,
) -> list[str]:
    cited_evidence_ids = {
        evidence_id
        for fact in facts
        for evidence_id in fact.evidence_ids
    }
    supported_entities = {
        entity
        for fact in facts
        for entity in fact.entities
        if entity
    }
    supported_entities.update(
        _schema_entities_for_evidence_ids(
            cited_evidence_ids,
            evidence_ledger,
        )
    )

    all_schema_entities = _schema_entities_for_evidence_ids(
        {
            item.evidence_id
            for item in evidence_ledger.items
        },
        evidence_ledger,
    )

    unsupported = {
        entity
        for entity in all_schema_entities
        if _entity_occurs(entity, statement)
        and entity not in supported_entities
    }

    unsupported.update(
        unsupported_backtick_entities(
            statement,
            supported_entities,
        )
    )

    for entity in re.findall(
        r"\b(?:Team|Player)\s+[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?",
        statement,
    ):
        if entity not in supported_entities:
            unsupported.add(entity)

    return sorted(unsupported)


def _candidate_fact_lookup(
    fact_ledger: FactLedger,
) -> dict[str, VerifiedFact]:
    return {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }


def _supports_data_quality_dimension(
    *,
    evidence_ids: set[str],
    evidence_lookup: dict[str, Any],
    dimension: str,
) -> bool:
    for evidence_id in evidence_ids:
        item = evidence_lookup.get(evidence_id)
        if item is None:
            continue
        if dimension == "missingness" and (
            item.capability == EvidenceCapability.MISSINGNESS
            or item.evidence_type == "missingness"
            or any(
                key in item.metrics
                for key in {"missing_count", "missing_rate"}
            )
        ):
            return True
        if dimension == "duplicates" and (
            item.capability == EvidenceCapability.DUPLICATES
            or item.evidence_type == "duplicate_rows"
            or any(
                key in item.metrics
                for key in {"duplicate_row_count", "duplicate_rate"}
            )
        ):
            return True
    return False


def _candidate_has_reportworthy_evidence(
    *,
    candidate: InsightCandidate,
    fact_lookup: dict[str, VerifiedFact],
    evidence_lookup: dict[str, Any],
    report_genre: ReportGenre,
) -> bool:
    fact_evidence_ids = {
        evidence_id
        for fact_id in candidate.source_fact_ids
        if fact_id in fact_lookup
        for evidence_id in fact_lookup[fact_id].evidence_ids
    }
    fact_evidence_ids.update(candidate.source_evidence_ids)
    evidence_types = {
        evidence_lookup[evidence_id].evidence_type
        for evidence_id in fact_evidence_ids
        if evidence_id in evidence_lookup
    }
    capabilities = {
        evidence_lookup[evidence_id].capability
        for evidence_id in fact_evidence_ids
        if evidence_id in evidence_lookup
    }

    if (
        EvidenceCapability.FOCUSED_TABLE_REGION in capabilities
        or "focused_table_region" in evidence_types
        or "focused_cell_context" in evidence_types
    ):
        return True

    if report_genre not in EVENT_INSIGHT_GENRES:
        return False

    return bool(
        evidence_types
        & {
            "event_context",
            "event_status",
            "participant_record_context",
            "score_progression",
            "event_outcome",
            "entity_ranking",
            "entity_performance",
            "event_sequence",
            "participant_comparison",
            "event_contrast",
        }
        or capabilities
        & {
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.ENTITY_PERFORMANCE,
            EvidenceCapability.RANKING,
            EvidenceCapability.GROUP_COMPARISON,
        }
    )


def _event_candidate_has_reportworthy_evidence(
    *,
    candidate: InsightCandidate,
    fact_lookup: dict[str, VerifiedFact],
    evidence_lookup: dict[str, Any],
    report_genre: ReportGenre,
) -> bool:
    return (
        report_genre in EVENT_INSIGHT_GENRES
        and _candidate_has_reportworthy_evidence(
            candidate=candidate,
            fact_lookup=fact_lookup,
            evidence_lookup=evidence_lookup,
            report_genre=report_genre,
        )
    )


def validate_insight_candidates(
    candidate_set: InsightCandidateSet,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
    report_genre: ReportGenre = ReportGenre.DATA_SCIENCE_REPORT,
) -> list[str]:
    errors: list[str] = []
    fact_lookup = _candidate_fact_lookup(fact_ledger)
    evidence_lookup = build_evidence_lookup(evidence_ledger)
    seen_ids: set[str] = set()
    accepted_for_duplicate_check: list[InsightCandidate] = []

    if (
        settings.max_insight_candidates is not None
        and len(candidate_set.candidates)
        > settings.max_insight_candidates
    ):
        errors.append(
            "Insight candidate count exceeds the configured limit of "
            f"{settings.max_insight_candidates}."
        )

    for candidate in candidate_set.candidates:
        candidate_id = candidate.insight_id.strip()

        if not candidate_id:
            errors.append("An insight candidate has an empty insight_id.")
            continue

        if candidate_id in seen_ids:
            errors.append(f"Duplicate insight ID: {candidate_id}")
            continue

        seen_ids.add(candidate_id)

        if not candidate.statement.strip():
            errors.append(f"{candidate_id} has an empty statement.")

        if not candidate.source_fact_ids:
            errors.append(f"{candidate_id} has no source fact IDs.")
            continue

        if len(candidate.source_fact_ids) != len(
            set(candidate.source_fact_ids)
        ):
            errors.append(f"{candidate_id} repeats source fact IDs.")

        unknown_fact_ids = [
            fact_id
            for fact_id in candidate.source_fact_ids
            if fact_id not in fact_lookup
        ]
        if unknown_fact_ids:
            errors.append(
                f"{candidate_id} cites unknown fact IDs: "
                f"{unknown_fact_ids}"
            )
            continue

        facts = [
            fact_lookup[fact_id]
            for fact_id in candidate.source_fact_ids
        ]
        fact_evidence_ids = {
            evidence_id
            for fact in facts
            for evidence_id in fact.evidence_ids
        }

        unknown_evidence_ids = [
            evidence_id
            for evidence_id in candidate.source_evidence_ids
            if evidence_id not in evidence_lookup
        ]
        if unknown_evidence_ids:
            errors.append(
                f"{candidate_id} cites unknown evidence IDs: "
                f"{unknown_evidence_ids}"
            )

        unlinked_evidence_ids = [
            evidence_id
            for evidence_id in candidate.source_evidence_ids
            if evidence_id not in fact_evidence_ids
        ]
        if unlinked_evidence_ids:
            errors.append(
                f"{candidate_id} cites evidence not referenced by its "
                f"source facts: {unlinked_evidence_ids}"
            )

        analytical_why = (
            candidate.why_it_matters
            if report_genre == ReportGenre.DATA_SCIENCE_REPORT
            else None
        )
        writer_visible_text = " ".join(
            filter(
                None,
                [
                    candidate.statement,
                    analytical_why,
                ],
            )
        )
        if (
            report_genre in EVENT_INSIGHT_GENRES
            and EVENT_REPORT_META_OMISSION_PATTERN.search(
                writer_visible_text
            )
        ):
            errors.append(
                f"{candidate_id} describes report omissions rather than "
                "supported event content."
            )
        if (
            report_genre == ReportGenre.DATA_SCIENCE_REPORT
            and candidate.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
            and not candidate.why_it_matters
        ):
            errors.append(
                f"{candidate_id} lacks an analytical implication required "
                "for a data-science report."
            )
        if MISSINGNESS_CLAIM_PATTERN.search(
            writer_visible_text
        ) and not _supports_data_quality_dimension(
            evidence_ids=fact_evidence_ids,
            evidence_lookup=evidence_lookup,
            dimension="missingness",
        ):
            errors.append(
                f"{candidate_id} makes a missingness or completeness claim "
                "without missingness evidence."
            )
        if DUPLICATE_CLAIM_PATTERN.search(
            writer_visible_text
        ) and not _supports_data_quality_dimension(
            evidence_ids=fact_evidence_ids,
            evidence_lookup=evidence_lookup,
            dimension="duplicates",
        ):
            errors.append(
                f"{candidate_id} makes a duplicate-data claim without "
                "duplicate-row evidence."
            )

        support_numbers = _insight_support_numbers(
            facts,
            evidence_ledger,
        )
        for field_name, field_text in {
            "statement": candidate.statement,
            "why_it_matters": analytical_why,
        }.items():
            if not field_text:
                continue
            if not numbers_supported(
                field_text,
                support_numbers,
            ):
                errors.append(
                    f"{candidate_id} {field_name} contains unsupported "
                    "numbers."
                )

            unsupported_entities = _unsupported_insight_entities(
                statement=field_text,
                facts=facts,
                evidence_ledger=evidence_ledger,
            )
            if unsupported_entities:
                errors.append(
                    f"{candidate_id} {field_name} contains unsupported table "
                    f"or column entities: {unsupported_entities}"
                )

        safe_permissions = _safe_fact_permissions(facts)
        if not set(candidate.claim_permissions).issubset(
            safe_permissions
        ):
            errors.append(
                f"{candidate_id} requests permissions stronger than its "
                "source facts."
            )

        reportworthy_single_fact_synthesis = (
            _candidate_has_reportworthy_evidence(
                candidate=candidate,
                fact_lookup=fact_lookup,
                evidence_lookup=evidence_lookup,
                report_genre=report_genre,
            )
        )

        if (
            candidate.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
            and len(set(candidate.source_fact_ids))
            < settings.min_facts_per_bounded_insight
            and candidate.insight_type
            not in SINGLE_FACT_INSIGHT_TYPES
            and not reportworthy_single_fact_synthesis
        ):
            errors.append(
                f"{candidate_id} is a single-fact pseudo-insight; "
                f"{settings.min_facts_per_bounded_insight} source facts "
                "are required."
            )

        if (
            candidate.interpretation_level
            == InterpretationLevel.HYPOTHESIS
        ):
            if not HYPOTHESIS_LABEL_PATTERN.search(candidate.statement):
                errors.append(
                    f"{candidate_id} is a hypothesis but is not explicitly "
                    "labelled as one."
                )

            if (
                candidate.suitable_for_main_report
                and not settings.allow_hypotheses_in_report
            ):
                errors.append(
                    f"{candidate_id} cannot be suitable for the main report "
                    "while hypotheses are disabled."
                )

        if (
            candidate.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
            and (
                HYPOTHESIS_LABEL_PATTERN.search(writer_visible_text)
                or EXPLANATORY_HYPOTHESIS_PATTERN.search(
                    writer_visible_text
                )
            )
        ):
            errors.append(
                f"{candidate_id} contains an explanatory hypothesis but is "
                "classified as a bounded insight."
            )

        finding_label_allowed_for_reportworthy_synthesis = (
            reportworthy_single_fact_synthesis
            and candidate.contribution
            in {
                InsightContribution.DESCRIPTIVE_SYNTHESIS,
                InsightContribution.EVENT_SYNTHESIS,
            }
        )
        if (
            candidate.interpretation_level
            == InterpretationLevel.FINDING
            and not finding_label_allowed_for_reportworthy_synthesis
        ):
            errors.append(
                f"{candidate_id} is a finding, not a second-pass bounded "
                "insight or hypothesis."
            )

        if (
            CAUSAL_PATTERN.search(writer_visible_text)
            and ClaimPermission.CAUSAL not in safe_permissions
        ):
            errors.append(
                f"{candidate_id} introduces unsupported causal wording."
            )

        if (
            PREDICTIVE_PATTERN.search(writer_visible_text)
            and ClaimPermission.PREDICTIVE not in safe_permissions
        ):
            errors.append(
                f"{candidate_id} introduces unsupported predictive wording."
            )

        if (
            FORECAST_PATTERN.search(writer_visible_text)
            and ClaimPermission.FORECAST not in safe_permissions
        ):
            errors.append(
                f"{candidate_id} introduces unsupported forecast wording."
            )

        if UNIVERSAL_GENERALISATION_PATTERN.search(writer_visible_text):
            errors.append(
                f"{candidate_id} generalises beyond the analysed dataset."
            )

        if (
            analytical_why
            and _materially_duplicate_statements(
                candidate.statement,
                analytical_why,
            )
        ):
            errors.append(
                f"{candidate_id} why_it_matters merely restates the insight."
            )

        if analytical_why and any(
            _materially_duplicate_statements(
                analytical_why,
                fact_text,
            )
            for fact in facts
            for fact_text in [
                fact.fact_summary,
                *fact.allowed_interpretations,
            ]
            if fact_text.strip()
        ):
            errors.append(
                f"{candidate_id} why_it_matters merely restates a source "
                "finding."
            )

        duplicate = next(
            (
                previous
                for previous in accepted_for_duplicate_check
                if _materially_duplicate_statements(
                    previous.statement,
                    candidate.statement,
                )
                or (
                    set(previous.source_fact_ids)
                    == set(candidate.source_fact_ids)
                    and previous.insight_type == candidate.insight_type
                    and _materially_duplicate_statements(
                        previous.supporting_summary,
                        candidate.supporting_summary,
                    )
                )
            ),
            None,
        )
        if duplicate is not None:
            errors.append(
                f"{candidate_id} materially duplicates "
                f"{duplicate.insight_id}."
            )
        else:
            accepted_for_duplicate_check.append(candidate)

    return errors


def build_insight_synthesis_agent(
    settings: Settings,
) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("evidence"),
            settings,
        ),
        name="evidence_analyst_agent_second_pass_insight_synthesis",
        deps_type=AgentDependencies,
        output_type=output_schema(
            InsightCandidateSet,
            settings,
        ),
        instructions=INSIGHT_SYNTHESIS_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "evidence",
            temperature=0.0,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    return agent


def _verified_statement_is_safe(
    *,
    candidate: InsightCandidate,
    statement: str,
    source_fact_ids: list[str],
    source_evidence_ids: list[str],
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
    report_genre: ReportGenre,
) -> bool:
    candidate_normalised = _normalise_statement(candidate.statement)
    statement_normalised = _normalise_statement(statement)

    if not statement_normalised:
        return False

    if (
        candidate_normalised not in statement_normalised
        and statement_normalised not in candidate_normalised
    ):
        return False

    checked = candidate.model_copy(
        update={
            "statement": statement,
            "source_fact_ids": source_fact_ids,
            "source_evidence_ids": source_evidence_ids,
        }
    )

    return not validate_insight_candidates(
        InsightCandidateSet(candidates=[checked]),
        fact_ledger,
        evidence_ledger,
        settings,
        report_genre,
    )


def validate_insight_verification(
    verification: InsightVerificationResult,
    candidates: InsightCandidateSet,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
    report_genre: ReportGenre = ReportGenre.DATA_SCIENCE_REPORT,
) -> list[str]:
    errors: list[str] = []
    candidate_lookup = {
        candidate.insight_id: candidate
        for candidate in candidates.candidates
    }
    received_ids = [
        record.insight_id
        for record in verification.records
    ]
    expected_ids = set(candidate_lookup)

    duplicate_ids = {
        insight_id
        for insight_id in received_ids
        if received_ids.count(insight_id) > 1
    }
    for insight_id in sorted(duplicate_ids):
        errors.append(
            f"{insight_id} has duplicate insight verification records."
        )

    for insight_id in sorted(expected_ids - set(received_ids)):
        errors.append(
            f"{insight_id} was not reviewed by the insight verifier."
        )
    for insight_id in sorted(set(received_ids) - expected_ids):
        errors.append(
            f"Unexpected insight verification record: {insight_id}."
        )

    for record in verification.records:
        candidate = candidate_lookup.get(record.insight_id)
        if candidate is None:
            continue

        verified_status = record.status in {
            InsightVerificationStatus.VERIFIED,
            InsightVerificationStatus.VERIFIED_WITH_CAVEAT,
        }
        reportworthy = _candidate_has_reportworthy_evidence(
            candidate=candidate,
            fact_lookup=_candidate_fact_lookup(fact_ledger),
            evidence_lookup=build_evidence_lookup(evidence_ledger),
            report_genre=report_genre,
        )
        if (
            verified_status
            and not record.adds_bounded_synthesis
            and not reportworthy
        ):
            errors.append(
                f"{record.insight_id} is a direct-finding restatement rather "
                "than a bounded insight."
            )
        if (
            verified_status
            and report_genre == ReportGenre.DATA_SCIENCE_REPORT
            and not record.analytical_implication_supported
        ):
            errors.append(
                f"{record.insight_id} lacks a supported analytical implication."
            )
        if verified_status and record.contains_hypothesis:
            errors.append(
                f"{record.insight_id} contains a hypothesis and cannot be a "
                "verified main insight."
            )
        if (
            record.status
            == InsightVerificationStatus.HYPOTHESIS_ONLY
            and not record.contains_hypothesis
        ):
            errors.append(
                f"{record.insight_id} is marked hypothesis_only without a "
                "hypothesis."
            )
        if (
            candidate.interpretation_level
            == InterpretationLevel.HYPOTHESIS
            and verified_status
        ):
            errors.append(
                f"{record.insight_id} cannot verify a hypothesis as a bounded "
                "main insight."
            )

        source_fact_ids = (
            record.verified_source_fact_ids
            or candidate.source_fact_ids
        )
        source_evidence_ids = (
            record.verified_source_evidence_ids
            or candidate.source_evidence_ids
        )

        if not set(source_fact_ids).issubset(
            set(candidate.source_fact_ids)
        ):
            errors.append(
                f"{record.insight_id} verifier introduced source fact IDs."
            )

        candidate_evidence_ids = {
            evidence_id
            for fact in fact_ledger.writer_ready_facts
            if fact.fact_id in candidate.source_fact_ids
            for evidence_id in fact.evidence_ids
        }
        if not set(source_evidence_ids).issubset(candidate_evidence_ids):
            errors.append(
                f"{record.insight_id} verifier introduced source evidence IDs."
            )

        if record.verified_statement and not _verified_statement_is_safe(
            candidate=candidate,
            statement=record.verified_statement,
            source_fact_ids=source_fact_ids,
            source_evidence_ids=source_evidence_ids,
            fact_ledger=fact_ledger,
            evidence_ledger=evidence_ledger,
            settings=settings,
            report_genre=report_genre,
        ):
            errors.append(
                f"{record.insight_id} verifier statement is unsupported or "
                "stronger than the candidate."
            )

    return errors


def build_insight_verifier_agent(
    settings: Settings,
) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("verifier"),
            settings,
        ),
        name="fact_verification_agent_second_pass_insight_verification",
        deps_type=AgentDependencies,
        output_type=output_schema(
            InsightVerificationResult,
            settings,
        ),
        instructions=INSIGHT_VERIFIER_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "verifier",
            temperature=0.0,
            max_tokens=8_000,
        ),
        retries={"output": 3},
    )

    return agent


def empty_insight_ledger(
    *,
    synthesis_enabled: bool,
    fallback_reason: str,
) -> InsightLedger:
    return InsightLedger(
        synthesis_enabled=synthesis_enabled,
        fallback_reason=fallback_reason,
    )


def materialise_insight_ledger(
    *,
    candidates: InsightCandidateSet,
    verification: InsightVerificationResult,
    fact_ledger: FactLedger,
    evidence_ledger: Any,
    settings: Settings,
    report_genre: ReportGenre = ReportGenre.DATA_SCIENCE_REPORT,
) -> InsightLedger:
    candidate_errors = validate_insight_candidates(
        candidates,
        fact_ledger,
        evidence_ledger,
        settings,
        report_genre,
    )
    verification_errors = validate_insight_verification(
        verification,
        candidates,
        fact_ledger,
        evidence_ledger,
        settings,
        report_genre,
    )
    records = {
        record.insight_id: record
        for record in verification.records
    }
    evidence_lookup = {
        item.evidence_id: item
        for item in evidence_ledger.items
    }
    fact_lookup = _candidate_fact_lookup(fact_ledger)
    rejected: list[InsightRejection] = []
    unverified: list[InsightVerificationFailure] = []
    hypotheses: list[VerifiedInsight] = []
    eligible: list[tuple[int, InsightCandidate, VerifiedInsight]] = []
    candidate_ids = {
        candidate.insight_id
        for candidate in candidates.candidates
    }
    global_candidate_errors = [
        error
        for error in candidate_errors
        if not any(
            candidate_id in error
            for candidate_id in candidate_ids
        )
    ]
    for index, candidate in enumerate(candidates.candidates):
        candidate_reasons = [
            error
            for error in candidate_errors
            if candidate.insight_id in error
        ]
        candidate_reasons.extend(global_candidate_errors)
        record = records.get(candidate.insight_id)

        if candidate_reasons:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=list(dict.fromkeys(candidate_reasons)),
                )
            )
            continue

        if record is None:
            unverified.append(
                InsightVerificationFailure(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=[
                        "The verifier did not return a usable review for this "
                        "insight."
                    ],
                )
            )
            continue

        if record.status == InsightVerificationStatus.REJECTED:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=record.verification_notes
                    or ["The verifier rejected this insight."],
                )
            )
            continue

        verification_reasons = [
            error
            for error in verification_errors
            if candidate.insight_id in error
        ]

        source_fact_ids = list(
            dict.fromkeys(
                (
                    record.verified_source_fact_ids
                    if record.verified_source_fact_ids
                    else candidate.source_fact_ids
                )
            )
        )
        source_evidence_ids = list(
            dict.fromkeys(
                (
                    record.verified_source_evidence_ids
                    if record.verified_source_evidence_ids
                    else (
                        candidate.source_evidence_ids
                        or [
                            evidence_id
                            for fact_id in source_fact_ids
                            if fact_id in fact_lookup
                            for evidence_id in fact_lookup[
                                fact_id
                            ].evidence_ids
                        ]
                    )
                )
            )
        )
        statement = (
            record.verified_statement
            if record.verified_statement
            else candidate.statement
        )

        if (
            record.verified_statement
            and not _verified_statement_is_safe(
                candidate=candidate,
                statement=record.verified_statement,
                source_fact_ids=source_fact_ids,
                source_evidence_ids=source_evidence_ids,
                fact_ledger=fact_ledger,
                evidence_ledger=evidence_ledger,
                settings=settings,
                report_genre=report_genre,
            )
        ):
            verification_reasons.append(
                "The verifier statement was stronger than or unsupported by "
                "the candidate provenance."
            )

        confidence = min(
            candidate.confidence,
            record.confidence,
        )
        salience = min(
            candidate.salience,
            record.salience,
        )

        hypothesis_only = bool(
            candidate.interpretation_level
            == InterpretationLevel.HYPOTHESIS
            or record.status
            == InsightVerificationStatus.HYPOTHESIS_ONLY
        )

        if verification_reasons:
            unverified.append(
                InsightVerificationFailure(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=list(dict.fromkeys(verification_reasons)),
                )
            )
            continue

        contribution = (
            InsightContribution.EVENT_SYNTHESIS
            if report_genre in EVENT_INSIGHT_GENRES
            else (
                InsightContribution.DESCRIPTIVE_SYNTHESIS
                if report_genre == ReportGenre.DATASET_OVERVIEW
                else InsightContribution.ANALYTICAL_IMPLICATION
            )
        )
        verified = VerifiedInsight(
            insight_id=candidate.insight_id,
            statement=statement,
            insight_type=candidate.insight_type,
            interpretation_level=(
                InterpretationLevel.HYPOTHESIS
                if hypothesis_only
                else InterpretationLevel.BOUNDED_INSIGHT
            ),
            contribution=contribution,
            source_fact_ids=source_fact_ids,
            source_evidence_ids=source_evidence_ids,
            source_capabilities=list(
                dict.fromkeys(
                    evidence_lookup[evidence_id].capability
                    for evidence_id in source_evidence_ids
                    if evidence_id in evidence_lookup
                )
            ),
            why_it_matters=(
                candidate.why_it_matters
                if contribution
                == InsightContribution.ANALYTICAL_IMPLICATION
                else None
            ),
            limitations=list(
                dict.fromkeys(
                    [
                        *candidate.limitations,
                        *record.limitations,
                    ]
                )
            ),
            claim_permissions=candidate.claim_permissions,
            confidence=confidence,
            salience=salience,
            verification_status=(
                InsightVerificationStatus.HYPOTHESIS_ONLY
                if hypothesis_only
                else record.status
            ),
        )

        if hypothesis_only:
            if not HYPOTHESIS_LABEL_PATTERN.search(statement):
                rejected.append(
                    InsightRejection(
                        insight_id=candidate.insight_id,
                        candidate=candidate,
                        reasons=[
                            "A hypothesis-only statement must be explicitly "
                            "labelled as a hypothesis."
                        ],
                    )
                )
            else:
                hypotheses.append(verified)
            continue

        if not candidate.suitable_for_main_report:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=["The candidate is not suitable for the main report."],
                )
            )
            continue

        if confidence < settings.min_insight_confidence:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=[
                        "Confidence is below the configured main-insight "
                        "threshold."
                    ],
                )
            )
            continue

        if salience < settings.min_insight_salience:
            rejected.append(
                InsightRejection(
                    insight_id=candidate.insight_id,
                    candidate=candidate,
                    reasons=[
                        "Salience is below the configured main-insight "
                        "threshold."
                    ],
                )
            )
            continue

        eligible.append((index, candidate, verified))

    eligible.sort(
        key=lambda item: (
            not item[1].suitable_for_main_report,
            -item[2].salience,
            -item[2].confidence,
            item[0],
        )
    )
    return InsightLedger(
        verified_insights=[
            verified
            for _, _, verified in eligible
        ],
        hypothesis_only_insights=hypotheses,
        rejected_insights=rejected,
        unverified_insights=unverified,
        verifier_notes=[
            *verification.verifier_notes,
            *[
                error
                for error in verification_errors
                if error not in {
                    reason
                    for rejection in rejected
                    for reason in rejection.reasons
                }
            ],
        ],
        synthesis_enabled=True,
    )


def writer_sentence_grounding_errors(
    *,
    sentence: WriterSentenceDraft,
    fact_lookup: dict[str, VerifiedFact],
    insight_lookup: dict[str, VerifiedInsight],
    sentence_label: str,
) -> list[str]:
    if sentence.support_type == SupportType.NON_FACTUAL:
        return []

    expanded_fact_ids = list(
        dict.fromkeys(
            [
                *sentence.fact_ids,
                *[
                    fact_id
                    for insight_id in sentence.insight_ids
                    if insight_id in insight_lookup
                    for fact_id in insight_lookup[
                        insight_id
                    ].source_fact_ids
                ],
            ]
        )
    )
    supporting_facts = [
        fact_lookup[fact_id]
        for fact_id in expanded_fact_ids
        if fact_id in fact_lookup
    ]

    if not supporting_facts:
        return []

    errors: list[str] = []
    support_numbers = [
        number
        for fact in supporting_facts
        for number in flatten_numbers(
            fact.structured_values
        )
    ]
    support_numbers.extend(
        number
        for fact in supporting_facts
        for _, number in extract_number_tokens(
            fact.fact_summary
        )
    )
    for insight_id in sentence.insight_ids:
        insight = insight_lookup.get(insight_id)
        if insight is None:
            continue
        support_numbers.extend(
            number
            for _, number in extract_number_tokens(
                insight.statement
            )
        )
    if not numbers_supported(
        sentence.text,
        support_numbers,
    ):
        errors.append(
            f"{sentence_label} contains a number unsupported by mapped facts "
            f"{expanded_fact_ids}."
        )

    supported_entities = {
        entity
        for fact in supporting_facts
        for entity in fact.entities
    }
    unsupported_entities = unsupported_backtick_entities(
        sentence.text,
        supported_entities,
    )
    if unsupported_entities:
        errors.append(
            f"{sentence_label} contains unsupported entities "
            f"{unsupported_entities}; mapped fact IDs: "
            f"{expanded_fact_ids}."
        )

    return errors


def recover_missing_writer_insight_ids(
    draft: WriterAgentDraft,
    verified_insight_lookup: dict[str, VerifiedInsight],
) -> WriterAgentDraft:
    """Recover one unambiguous omitted insight ID from exact fact provenance."""

    changed = False
    recovered_sections: list[WriterSectionDraft] = []

    for section in draft.sections:
        recovered_sentences: list[WriterSentenceDraft] = []

        for sentence in section.sentences:
            recovered = sentence
            if (
                sentence.interpretation_level
                == InterpretationLevel.BOUNDED_INSIGHT
                and not sentence.insight_ids
                and sentence.fact_ids
            ):
                cited_fact_ids = set(sentence.fact_ids)
                candidates = [
                    insight_id
                    for insight_id, insight
                    in verified_insight_lookup.items()
                    if set(insight.source_fact_ids)
                    == cited_fact_ids
                ]
                if len(candidates) == 1:
                    recovered = sentence.model_copy(
                        update={"insight_ids": candidates}
                    )
                    changed = True

            recovered_sentences.append(recovered)

        recovered_sections.append(
            section.model_copy(
                update={"sentences": recovered_sentences}
            )
        )

    if not changed:
        return draft

    return draft.model_copy(
        update={"sections": recovered_sections}
    )


WRITER_INSTRUCTIONS = """
You are an expert data scientist and natural report writer.

Use the supplied verified evidence to produce a selective, coherent,
reader-facing data-science report.

Write an insight-led report rather than a catalogue of unrelated statistics
when verified bounded insights are available. The verified Insight Ledger is
the only source of interpretive claims. Verified facts remain the source of
direct findings and supporting details.

For each main analytical paragraph, state one verified bounded insight,
support it with its verified facts, explain why it matters only when the
verified insight carries an analytical implication, and integrate its
limitation where needed. Event and descriptive synthesis can provide value by
coherently relating supported facts without adding a deeper implication. Do
not invent or strengthen an insight during writing.

Keep four roles distinct:
- a direct finding reports a verified observation or statistic;
- a bounded insight relates multiple findings into a dataset-scoped pattern;
- the analytical implication explains why that combined pattern matters for
  interpretation or analysis, using only the insight's `why_it_matters`;
- a hypothesis proposes why the pattern exists and requires further testing.

Do not fill an analytical paragraph with a coefficient sentence followed by a
verbal restatement of the same coefficients. Use the verified analytical
implication. A possible dependency, artifact, collection process, or unmeasured
mechanism is a hypothesis even when introduced as something to investigate.

Do not turn association into causation, a group difference into an
explanation, overlapping variables into universal redundancy, a data-quality
risk into a confirmed error, or a game statistic into unsupported dominance.
Every bounded-insight sentence must cite its insight ID and retain relevant
source fact IDs. Every direct factual sentence must cite fact IDs. Do not use
rejected insights or hypothesis-only insights in the main report.

When hypotheses are disabled, do not write a hypothesis section. When they
are enabled, place them only in a separate "Questions for Further
Investigation" section, label each as a hypothesis or question, state what
additional analysis is needed, and never present it as a result.

Respect the selected genre, content slots and perspective. Respect a maximum
word count only when `maximum_length_words` is provided; otherwise treat
`target_length_words` as guidance rather than a hard ceiling.
A data-science
report uses bounded analytical prose. A dataset overview stays concise and
mainly finding-led. An event report communicates the verified result, leading
performances and major participant contrasts in conventional narrative form.
Fill each required slot only from evidence carrying its required capability.
Do not mention a slot when its evidence is unavailable. Do not invent
chronology, comeback leadership, dominance, milestones, audience, venue,
season context or historical significance. Neutral perspective is the
default; subject-centred perspective changes selection only, never facts.

For an event report, lead with the supported result when available, integrate
supported date, venue, participant record context, segment score progression
and status as context, then relate salient entity performances and
participant-level contrasts. For structured event reports, end with a short
event-scoped limitation. For reference-style event recaps, keep caveats
internal unless they are needed to avoid a misleading unsupported inference.
Do not discuss wrapper row counts, constant columns, missingness, correlation,
regression, statistical power, feature removal or predictive modelling unless
the user explicitly requested that analysis. A single event can still support
within-event comparison and ranking. When a visible limitation is required,
phrase it in event terms: the comparisons describe only the supplied event,
do not establish why the result occurred and do not support claims about
broader performance. Avoid generic boilerplate about "observed associations"
or "unadjusted group comparisons" in an event report.
If event-sequence evidence is present, you may mention that recorded sequence
or score-state information exists, but prefer concrete supported
score-changing facts over generic availability statements. Do not infer
unverified chronology, momentum or turning points. If actionable sequence
facts are present in `content_requirements`, do not satisfy that slot by
saying sequence detail was not analysed; use the supported sequence facts or
omit unsupported commentary.

There is no fixed findings or insights quota. Cover required content first,
then use as many additional distinct, relevant verified facts and insights as
improve the report. If `maximum_length_words` is provided, stay within it; if
it is not provided, keep the report concise but do not omit strong supported
material merely to hit the target length. Do not pad the report, repeat
findings, or omit a stronger supported item merely to reach a particular
count.

When the Writer payload contains `content_requirements`, treat it as a
controller-enforced coverage checklist. Use enough supported facts or verified
insights from each listed content unit to satisfy `minimum_items`. If
`enforce_minimum_words` is true, write at least `minimum_word_count` useful
words. If an explicit `maximum_length_words` is provided, stay below it.
Expand by adding supported event context, secondary performances, participant
contrasts, and scoped limitations; do not expand by adding unsupported
explanation or filler.
For one-sentence, direct-answer and short-text verbalisation tasks, preserve
source surface forms that benchmark references are likely to depend on: keep
digits as digits, keep percentages and decimals unchanged, preserve compact
units, and do not spell out alphanumeric or hyphenated identifiers. For
example, keep `ALCO_RS-3`, `12`, `17068.8` and `58.45%` rather than rewriting
them as words. Convert relation labels into concise natural predicates when
clear, such as `RANK = 11` -> `ranks 11th`, `TOTAL = 211.5` -> `total of
211.5`, and `cylinderCount = 12` -> `12 cylinders`.
When `realisation_policy` is `natural_reference_style`, you may make harmless
surface normalisations that improve benchmark-style prose while preserving the
same supported entity or value, such as changing underscores between words to
spaces in an identifier. Never change digits, percentages, decimals, units,
entity identity, or relation meaning. When `realisation_policy` is
`strict_source_surface`, keep source spelling and separators exactly.
When `realisation_policy` is `concise_table_proposition`, produce the shortest
complete proposition supported by the focused cell or region; do not add
headings, caveats, row-counts, or unrelated table context.
When the Writer payload contains `event_report_writing_guidance`, use it as
the event style contract. Start from the result, then build a readable recap
from supported context, sequence/progression, leading performances and major
participant contrasts. Select and combine the strongest distinct details
instead of listing every ranking mechanically. Do not add dataset-quality,
correlation, modelling or feature-selection discussion to an event report
unless the user explicitly asks for that analysis.
When `event_report_writing_guidance.realisation_policy` is
`event_recap_style`, prioritise reference-style event narration: concise
opening result, natural progression, key performances, and compact team
contrasts. Use only supported sequence/progression facts for chronology; avoid
visible methodological caveats unless they prevent a misleading unsupported
inference.
If the guidance or content requirements indicate `reference_recap_style`,
write flowing reference-style event prose: do not use visible Markdown
headings, do not add a generic scope/limitations paragraph, and keep caveats
internal unless they are needed to avoid an unsupported inference. Use hidden
sections only to organise the structured draft; the controller will render the
visible text without headings.
For event-sequence units, prefer verified sequence insights for coherent
narration, then cite additional sequence fact IDs only for score-changing
steps not already covered by the insight. Do not expose internal role labels
such as `lead_change` or `late_score_change`; express the supplied scores and
events naturally.
When `narrative_requirements` are present, satisfy them with connected event
prose: use verified insights or multi-fact synthesis, contrastive connectors
such as "while" or "despite" where the support allows them, and an
event-scoped caveat only when required by the supplied narrative
requirements. Do not satisfy narration by inventing chronology, momentum or
causes.
When the Writer payload contains `narrative_plan`, follow its slot order and
paragraph hints as the visible story plan. Cover higher-priority slots before
secondary details, combine related facts into natural sentences, and use
`low_priority_fact_ids` only when they add distinct value after the result,
sequence, leading performances and participant contrasts are covered.

For focused-table, structured-record verbalisation, direct-answer,
one-sentence or short-text tasks, the report contract overrides normal report
structure. Write only the requested answer form from the focused or supplied
record facts and verified insights. If headings are not allowed, use the title
and section fields only as hidden structure; they will not be rendered. Do not
add dataset overview, data quality, missingness, correlation, modelling,
generic limitations, or unrelated table facts unless the user explicitly asks
for them.
When a verified focused-table descriptive insight is available, prefer its
natural table relation over a mechanical description of the highlighted cell
coordinates. Keep the sentence within the requested output form and cite the
insight plus its source facts.
When structured-record evidence is available for an attribute or triple
verbalisation task, express all and only those supplied records as fluent
natural language. Prefer natural wording over a mechanical key/value dump, but
do not add unsupported attributes, entities, relations or background facts.
For triple verbalisation, treat the supplied triples as the sentence schema:
keep the source subject as the grammatical subject when natural, render each
relation once, preserve relation order where possible, and use compact direct
predicates. Do not add explanatory verbs, alternate measurements or
background framing not present in the supplied triples. Preserve numeric
punctuation exactly.
If the focused evidence or content requirements include a short-form selection
policy, centre the sentence on highlighted role/value pairs and the most
specific supported primary subject candidate. Treat non-highlighted same-row
values as context. Omit them unless they are needed to identify the subject or
relation. Do not combine that primary subject with row co-entities into a
joint subject unless the supplied evidence explicitly represents a combined
entity. Use supplied highlighted-measure comparisons for concise
outcome-like wording when the table context supports it; do not calculate new
comparisons. If the evidence supplies a highlighted-set contrast, prefer it
for one-sentence lower/higher wording, and keep the wording scoped to the
highlighted cells unless a cited table-wide rank fact supports a broader
highest/lowest claim. If the evidence supplies highlighted record groups,
preserve all grouped highlighted records that contribute to the focused
answer, including repeated same-pattern rows. If the evidence supplies a focused record-style
relation, prefer that relation over a mechanical description of highlighted
cell labels, headers, or summary rows. If the evidence supplies a focused
list-page relation, prefer it over venue, location, opponent, or other
same-row details unless the user explicitly asks for those details.

You have freedom over:
- wording;
- structure;
- selection;
- synthesis;
- paragraph organisation;
- integration of verified analytical implications;
- consolidation of caveats.

You do not have freedom to invent:
- calculated values;
- table or column names;
- categories;
- dates;
- locations;
- provenance;
- domain definitions;
- causal explanations;
- predictive performance;
- forecast performance;
- deployment claims.

Internal prohibited interpretations are private safety constraints.
Never quote, enumerate, label, paraphrase as instructions, or expose them
in the visible report.

Do not render internal evidence fields such as:
- Finding:
- Strength:
- Important Note:
- Interpretation Notes:
- Recommended Use:
- Methodological Strength:
- User Relevance:
- Salience:
- Global Prohibited Interpretations

Translate effect labels and metrics into natural prose.
Preserve their verified classification consistently. If mapped evidence calls
an association strong, do not later call the same association moderate. Do not
invent a qualitative strength label that differs from the supplied controlled
strength label.
Do not begin with generic boilerplate such as "This document summarizes",
"This report provides", "Here's a breakdown", or "The goal is to provide".

For example, do not write:

"Strength: Large group difference; Standardized Difference: 1.00"

Write naturally:

"The groups differ substantially; the standardised mean difference is
approximately 1.0."

The Data Understanding output is interpretive context, not an independent
source of factual truth.

Every visible factual statement must be supported by the supplied verified
facts.

Do not introduce a factual claim solely because it appears in:
- dataset_summary;
- unit_of_observation;
- table summary;
- column interpretation;
- quality finding;
- usability note.

In particular, do not state that observations are hourly, collected at a
specific location, produced by a weather station, or gathered through a
particular process unless a verified fact explicitly supports that statement.

Use neutral terms such as "rows", "records", "observations" or
"timestamped observations" when a more specific unit is not verified.

Reader-facing next steps must come from supplied analytical recommendations,
verified methodological facts or the explicit user request. Do not invent
generic future modelling tasks. A recommendation to investigate whether a
pattern reflects a dependency, artifact, collection process, or unmeasured
mechanism is still a hypothesis and must follow the hypothesis policy.

When supported missingness facts are available, state clearly which observed
subset the analysis describes. Do not assume missingness is non-random or has
already biased an estimate. When supported duplicate facts are available,
describe possible influence as an unmeasured methodological risk; do not claim
that deduplication would change results unless that comparison was performed.

For a major group comparison, where supplied, explain:
- the group means;
- their absolute difference;
- whether the difference is small, moderate, or large;
- relevant group-size imbalance;
- whether the comparison is adjusted or unadjusted.

Do not mechanically print all fields. Integrate the most useful context
into natural prose.

Do not include every available fact.
Prioritise the strongest, most relevant, and methodologically defensible
findings.

A generic dataset-understanding report should normally include:
- a concise dataset overview;
- important data-quality findings;
- the strongest observed relationships;
- relevant methodological limitations;
- grounded next analytical steps.

Small or weak effects should normally be omitted unless they materially
qualify a stronger finding or the user requested completeness.

Deterministically recovered facts are direct representations of trusted
calculated evidence. They are as grounded as LLM-verified facts and may be
used normally, while their recovery method remains recorded internally.

When sufficient verified material exists, do not return only a heading and
one or two factual sentences. Cover every required report component using
the strongest available facts.

Prefer relationship diversity. When both are available, normally include a
strong or moderate correlation and a large or moderate group comparison
rather than several similar comparisons.

Do not use a small relationship merely to increase the number of findings.

Every factual sentence must be represented in the hidden sentence support
map.

Return structured sections and sentences only.
Do not return Markdown.
Do not construct a separate support map.
The controller will materialise Markdown and sentence support
deterministically.

Each factual sentence must list its supporting fact IDs.
List the fact IDs supporting the title in `title_fact_ids`. A factual title
must not introduce an entity, value or result absent from those facts.
Every backticked table or column name and every visible number must be
supported by those same fact IDs. When a sentence combines facts, cite every
fact needed for all of its named entities and values.
Cite every fact and insight ID genuinely needed to support the title or
sentence. Keep sections, sentences and support lists coherent within the report
word ceiling. Never create placeholder IDs, ID ranges or exhaustive sequences
of IDs.
Non-factual transitions may be marked non_factual_transition and must not
cite fact IDs.
"""


def build_writer_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("writer"),
            settings,
        ),
        name="natural_data_science_writer_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            WriterAgentDraft,
            settings,
        ),
        instructions=WRITER_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "writer",
            temperature=0.15,
            max_tokens=11_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: WriterAgentDraft,
    ) -> WriterAgentDraft:
        ledger = FactLedger.model_validate(
            context.deps.payload["fact_ledger"]
        )

        fact_lookup = {
            fact.fact_id: fact
            for fact in ledger.writer_ready_facts
        }
        valid_fact_ids = {
            fact.fact_id
            for fact in ledger.writer_ready_facts
        }
        insight_ledger = InsightLedger.model_validate(
            context.deps.payload.get(
                "insight_ledger",
                {},
            )
        )
        verified_insight_lookup = {
            insight.insight_id: insight
            for insight in insight_ledger.verified_insights
        }
        hypothesis_insight_lookup = {
            insight.insight_id: insight
            for insight in insight_ledger.hypothesis_only_insights
        }
        all_insight_lookup = {
            **verified_insight_lookup,
            **hypothesis_insight_lookup,
        }
        output = recover_missing_writer_insight_ids(
            output,
            verified_insight_lookup,
        )
        valid_insight_ids = set(verified_insight_lookup)
        hypothesis_insight_ids = set(hypothesis_insight_lookup)
        all_insight_ids = set(all_insight_lookup)
        allow_hypotheses = bool(
            context.deps.payload.get(
                "allow_hypotheses_in_report",
                False,
            )
        )
        maximum_length_words = context.deps.payload.get(
            "maximum_length_words"
        )
        content_requirements = context.deps.payload.get(
            "writer_content_requirements"
        )
        short_form_without_headings = bool(
            isinstance(content_requirements, dict)
            and (
                content_requirements.get("allow_headings") is False
                or content_requirements.get("output_form")
                in {"one_sentence", "direct_answer", "short_text"}
            )
        )

        errors: list[str] = []

        draft_text_parts = (
            [
                sentence.text
                for section in output.sections
                for sentence in section.sentences
            ]
            if short_form_without_headings
            else [
                output.title,
                *[
                    part
                    for section in output.sections
                    for part in [
                        section.heading,
                        *[
                            sentence.text
                            for sentence in section.sentences
                        ],
                    ]
                ],
            ]
        )
        draft_word_count = len(
            re.findall(
                r"\b[\w'-]+\b",
                " ".join(draft_text_parts),
            )
        )
        if maximum_length_words is not None:
            if draft_word_count > int(maximum_length_words):
                errors.append(
                    f"The draft contains {draft_word_count} words and exceeds "
                    f"the {maximum_length_words}-word ceiling."
                )

        unknown_title_fact_ids = set(output.title_fact_ids) - valid_fact_ids
        if unknown_title_fact_ids and not short_form_without_headings:
            errors.append(f"The title uses unknown fact IDs: {sorted(unknown_title_fact_ids)}")
        title_entities = {
            entity
            for fact in ledger.writer_ready_facts
            for entity in fact.entities
            if len(entity.strip()) >= 3
        }
        factual_title = bool(
            re.search(r"(?<!\w)\d+(?:[.,]\d+)?", output.title)
            or (
                FACTUAL_TITLE_PATTERN.search(output.title)
                and any(
                    entity.casefold() in output.title.casefold()
                    for entity in title_entities
                )
            )
        )
        if (
            factual_title
            and not output.title_fact_ids
            and not short_form_without_headings
        ):
            errors.append("A factual title must list supporting title_fact_ids.")
        if output.title_fact_ids and not unknown_title_fact_ids:
            supported_title_entities = {
                entity
                for fact_id in output.title_fact_ids
                for entity in fact_lookup[fact_id].entities
            }
            mentioned_title_entities = {
                entity
                for entity in title_entities
                if entity.casefold() in output.title.casefold()
            }
            unsupported_title_entities = (
                mentioned_title_entities - supported_title_entities
            )
            if (
                factual_title
                and unsupported_title_entities
                and not short_form_without_headings
            ):
                errors.append(
                    "The title contains entities unsupported by its facts: "
                    f"{sorted(unsupported_title_entities)}"
                )
            errors.extend(
                writer_sentence_grounding_errors(
                    sentence=WriterSentenceDraft(
                        text=output.title,
                        fact_ids=output.title_fact_ids,
                        support_type=SupportType.DIRECT,
                    ),
                    fact_lookup=fact_lookup,
                    insight_lookup={},
                    sentence_label="Title",
                )
            )

        if not output.sections:
            errors.append(
                "Return at least one report section."
            )

        if short_form_without_headings and isinstance(content_requirements, dict):
            sentence_texts = [
                sentence.text
                for section in output.sections
                for sentence in section.sentences
                if sentence.text.strip()
            ]
            if (
                content_requirements.get("require_complete_sentence")
                and sentence_texts
                and sentence_texts[-1].strip()[-1] not in ".!?"
            ):
                errors.append(
                    "The draft must provide a complete sentence for this "
                    "output form."
                )

        for section_index, section in enumerate(
            output.sections,
            start=1,
        ):
            if not section.sentences:
                errors.append(
                    f"Section {section_index} contains no sentences."
                )

            for sentence_index, sentence in enumerate(
                section.sentences,
                start=1,
            ):
                unknown = (
                    set(sentence.fact_ids)
                    - valid_fact_ids
                )

                if unknown:
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} "
                        "uses unknown fact IDs: "
                        f"{sorted(unknown)}"
                    )

                unknown_insights = (
                    set(sentence.insight_ids)
                    - all_insight_ids
                )
                if unknown_insights:
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} "
                        "uses unknown insight IDs: "
                        f"{sorted(unknown_insights)}"
                    )

                if not unknown and not unknown_insights:
                    errors.extend(
                        writer_sentence_grounding_errors(
                            sentence=sentence,
                            fact_lookup=fact_lookup,
                            insight_lookup=all_insight_lookup,
                            sentence_label=(
                                "Sentence "
                                f"{section_index}.{sentence_index}"
                            ),
                        )
                    )

                if (
                    EXPLANATORY_HYPOTHESIS_PATTERN.search(
                        sentence.text
                    )
                    and sentence.interpretation_level
                    != InterpretationLevel.HYPOTHESIS
                ):
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} presents a possible "
                        "explanation without classifying it as a hypothesis."
                    )

                if (
                    sentence.interpretation_level
                    == InterpretationLevel.BOUNDED_INSIGHT
                ):
                    if not sentence.insight_ids:
                        errors.append(
                            "A bounded-insight sentence must cite a verified "
                            "insight ID."
                        )
                    elif not set(sentence.insight_ids).issubset(
                        valid_insight_ids
                    ):
                        errors.append(
                            "A bounded-insight sentence may cite only verified "
                            "main insights."
                        )

                if (
                    sentence.interpretation_level
                    == InterpretationLevel.HYPOTHESIS
                ):
                    if not allow_hypotheses:
                        errors.append(
                            "Hypothesis sentences are disabled by configuration."
                        )
                    if not sentence.insight_ids or not set(
                        sentence.insight_ids
                    ).issubset(hypothesis_insight_ids):
                        errors.append(
                            "A hypothesis sentence must cite a hypothesis-only "
                            "insight ID."
                        )
                    if section.heading.strip().lower() != (
                        "questions for further investigation"
                    ):
                        errors.append(
                            "Hypotheses may appear only in the Questions for "
                            "Further Investigation section."
                        )
                    if not HYPOTHESIS_LABEL_PATTERN.search(
                        sentence.text
                    ) and not sentence.text.strip().endswith("?"):
                        errors.append(
                            "A hypothesis sentence must be explicitly labelled "
                            "as a hypothesis."
                        )

                if (
                    sentence.interpretation_level
                    == InterpretationLevel.FINDING
                    and sentence.insight_ids
                ):
                    errors.append(
                        "A direct finding must not be relabelled with insight IDs."
                    )

                if (
                    sentence.support_type
                    != SupportType.NON_FACTUAL
                    and not sentence.fact_ids
                    and not sentence.insight_ids
                ):
                    errors.append(
                        "Sentence "
                        f"{section_index}.{sentence_index} "
                        "is factual but has no supporting facts."
                    )

                if (
                    sentence.support_type
                    == SupportType.NON_FACTUAL
                    and (
                        sentence.fact_ids
                        or sentence.insight_ids
                    )
                ):
                    errors.append(
                        "A non-factual transition must not "
                        "cite fact or insight IDs."
                    )

                if re.search(
                    r"\[(?:CLM|FACT)_\d+",
                    sentence.text,
                ):
                    errors.append(
                        "Internal fact IDs must not appear "
                        "in visible sentence text."
                    )

                if INTERNAL_CONTROL_PATTERN.search(
                    sentence.text
                ):
                    errors.append(
                        "Visible sentence text exposes an "
                        "internal control."
                    )

                if FIELD_LABEL_PATTERN.search(
                    sentence.text
                ):
                    errors.append(
                        "Visible sentence text renders an "
                        "internal evidence field."
                    )

        used_fact_ids = {
            *output.title_fact_ids,
            *[
                fact_id
                for section in output.sections
                for sentence in section.sentences
                for fact_id in sentence.fact_ids
            ],
        }
        used_insight_ids = {
            insight_id
            for section in output.sections
            for sentence in section.sentences
            for insight_id in sentence.insight_ids
        }
        errors.extend(
            content_requirement_errors(
                used_fact_ids=used_fact_ids,
                used_insight_ids=used_insight_ids,
                word_count=draft_word_count,
                requirements=content_requirements,
                narrative_stats=sentence_support_narrative_stats(
                    [
                        sentence
                        for section in output.sections
                        for sentence in section.sentences
                    ]
                ),
                include_word_count=True,
            )
        )

        if errors:
            raise ModelRetry(
                "Writer draft validation failed:\n- "
                + "\n- ".join(errors)
            )

        return output

    return agent


AUDITOR_INSTRUCTIONS = """
You are the Factual Accuracy Auditor and Report Repair Agent.

The goal is to reduce residual hallucinations, not to demand that the
writer copy deterministic templates.

You receive:
- the raw or repaired report;
- the hidden sentence support map;
- verified facts;
- full evidence;
- deterministic profile support records;
- deterministic audit findings;
- methodological limitations;
- optional trusted external facts.

Authority hierarchy:
- The deterministic pre-audit is authoritative and cannot be erased.
- Factual and interpretive authority, in order, is the Verified Fact Ledger,
  deterministic Evidence Ledger, deterministic profile support, verified
  Insight Ledger for exact bounded interpretations, properly scoped trusted
  external facts when allowed, and Data Understanding as non-authoritative
  context only.
- Never validate one LLM-generated claim solely because another LLM output
  repeats it.
- A claim that is exactly supported by deterministic profile data but missing
  from the sentence support map is a support-mapping defect. Do not call it a
  visible hallucination when the visible statement is correct.
- Do not propose a visible rewrite when a deterministic hidden support-map
  patch fully resolves the problem.
- The semantic Auditor may add supported annotations and repair candidates but
  must not erase deterministic findings.

A verified insight is an evidence-constrained interpretation, not permission
to write any plausible related claim. Check that report wording is no stronger
than the mapped insight. Do not call a supported bounded insight a
hallucination merely because it is not a direct numeric fact.

Flag interpretations absent from the Insight Ledger, wording stronger than a
verified insight, causal escalation, unsupported domain interpretation,
unlabelled hypotheses, hypotheses presented as conclusions, and unsupported
genre-specific narratives. Also flag qualitative strength wording that
conflicts with the mapped deterministic strength label, such as calling the
same verified association strong in one place and moderate in another. The
Insight Ledger does not authorise new numbers, entities, recommendations,
causality, generalisations or domain explanations. Do not use Data
Understanding to validate an insight.

Perform two responsibilities.

A. Factual audit
Detect:
- incorrect numbers;
- incorrect entities;
- wrong direction or polarity;
- unsupported synthesis;
- causal overclaims;
- predictive or deployment overclaims;
- forecast overclaims;
- unsupported metadata;
- missing material caveats.
- limitations that say supplied structure or evidence is unavailable/not
  captured when the evidence ledger shows it exists. In that case, repair to
  "not analysed in this report" or remove the limitation.

B. Targeted repair
For each high-confidence repairable error:
- produce several replacement candidates;
- use only supplied facts and evidence;
- favour factual support over style;
- preserve useful meaning when possible;
- use deletion only where no grounded replacement is suitable.

Do not rewrite unflagged portions of the report.
Do not invent corrections.
Do not use outside knowledge.

Also assess report quality separately:
- request responsiveness;
- finding selection;
- coherence;
- concision;
- caveat integration;
- data-science interpretation.

Quality weaknesses alone should normally be warnings, not factual blocks.

`quality_assessment.findings` must describe defects in the report's writing,
selection, structure, interpretation or communication.

Valid examples:
- The report overstates the implication of a constant field.
- The report recommends duplicate removal without sufficient justification.
- The report repeats closely related findings.
- The report omits a required limitation.

Invalid examples:
- The dataset contains duplicate rows.
- Loud Cover is constant.
- Pressure contains zero values.
- Temperature and humidity are correlated.

Dataset observations belong in evidence or facts, not report-quality findings.

Apply these wording rules:
- Do not accept hourly cadence unless regular spacing is verified.
- Do not accept location or weather-station metadata unless verified.
- Constant columns contain no observed variation for analyses that depend on
  variation; they are not universally worthless.
- Suspicious zeros may represent missingness or measurement failure, but this
  must be validated before treating the interpretation as true.
- Low missingness is not automatically harmless.
- Duplicate rows should be reviewed before any decision to remove them.
- Pearson correlation may not capture non-linear relationships and can be
  sensitive to influential observations.
- Reader-facing next steps must be grounded in supplied recommendations,
  verified methodological facts or the explicit user request.

Internal-control leakage is a report-quality problem.
Unsupported claims that group-size imbalance biases group means should be
repaired to say unequal sizes can affect precision, stability, or
representation unless the evidence explicitly supports bias language.

When a visible report contains:
- Interpretation Notes;
- Global Prohibited Interpretations;
- Do not say...;
- evidence-field labels;

propose a targeted natural-language repair or removal.

Do not classify this alone as a critical factual hallucination.
Do not rewrite the complete report.
"""


def build_auditor_agent(settings: Settings) -> Agent:
    agent = Agent(
        build_model(
            settings.model_for("auditor"),
            settings,
        ),
        name="factual_accuracy_auditor_and_repair_agent",
        deps_type=AgentDependencies,
        output_type=output_schema(
            AuditRepairProposal,
            settings,
        ),
        instructions=AUDITOR_INSTRUCTIONS,
        model_settings=agent_model_settings(
            settings,
            "auditor",
            temperature=0.1,
            max_tokens=12_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: AuditRepairProposal,
    ) -> AuditRepairProposal:
        report_text = context.deps.payload["report_text"]
        valid_fact_ids = set(
            context.deps.payload["valid_fact_ids"]
        )
        valid_evidence_ids = set(
            context.deps.payload.get(
                "valid_evidence_ids",
                [],
            )
        )
        valid_profile_support_ids = set(
            context.deps.payload.get(
                "valid_profile_support_ids",
                [],
            )
        )
        valid_insight_ids = set(
            context.deps.payload.get(
                "valid_insight_ids",
                [],
            )
        )
        hypothesis_only_insight_ids = set(
            context.deps.payload.get(
                "hypothesis_only_insight_ids",
                [],
            )
        )
        all_insight_ids = (
            valid_insight_ids
            | hypothesis_only_insight_ids
        )
        insight_statements = dict(
            context.deps.payload.get(
                "insight_statements",
                {},
            )
        )
        sentence_insight_ids = {
            sentence: set(insight_ids)
            for sentence, insight_ids in context.deps.payload.get(
                "sentence_insight_ids",
                {},
            ).items()
        }
        allow_hypotheses = bool(
            context.deps.payload.get(
                "allow_hypotheses_in_report",
                False,
            )
        )
        repair_fact_ledger = (
            FactLedger.model_validate(
                context.deps.payload["fact_ledger"]
            )
            if "fact_ledger" in context.deps.payload
            else None
        )
        if "evidence_ledger" in context.deps.payload:
            from .schemas import EvidenceLedger

            repair_evidence_ledger = EvidenceLedger.model_validate(
                context.deps.payload["evidence_ledger"]
            )
        else:
            repair_evidence_ledger = None
        repair_insight_ledger = InsightLedger.model_validate(
            context.deps.payload.get(
                "insight_ledger",
                {},
            )
        )
        deterministic_annotation_ids = set(
            context.deps.payload.get(
                "deterministic_annotation_ids",
                [],
            )
        )
        deterministic_serious_annotation_ids = set(
            context.deps.payload.get(
                "deterministic_serious_annotation_ids",
                [],
            )
        )
        deterministic_annotation_sentences = set(
            context.deps.payload.get(
                "deterministic_annotation_sentences",
                [],
            )
        )

        annotation_ids = {
            annotation.annotation_id
            for annotation in output.annotations
        }
        all_annotation_ids = (
            annotation_ids
            | deterministic_annotation_ids
        )
        annotated_sentences = {
            annotation.sentence
            for annotation in output.annotations
        } | deterministic_annotation_sentences

        for annotation in output.annotations:
            if annotation.sentence not in report_text:
                raise ModelRetry(
                    "Every annotated sentence must occur in the report."
                )

            if (
                annotation.text_span
                and annotation.text_span not in annotation.sentence
            ):
                raise ModelRetry(
                    "Every text_span must occur in its sentence."
                )

            unknown = set(annotation.fact_ids) - valid_fact_ids

            if unknown:
                raise ModelRetry(
                    f"Unknown annotation fact IDs: {sorted(unknown)}"
                )

            unknown_evidence = (
                set(annotation.evidence_ids)
                - valid_evidence_ids
            )

            if unknown_evidence:
                raise ModelRetry(
                    "Unknown annotation evidence IDs: "
                    f"{sorted(unknown_evidence)}"
                )

            unknown_profile_support = (
                set(annotation.profile_support_ids)
                - valid_profile_support_ids
            )

            if unknown_profile_support:
                raise ModelRetry(
                    "Unknown annotation profile support IDs: "
                    f"{sorted(unknown_profile_support)}"
                )

            unknown_insights = (
                set(annotation.insight_ids)
                - all_insight_ids
            )
            if unknown_insights:
                raise ModelRetry(
                    "Unknown annotation insight IDs: "
                    f"{sorted(unknown_insights)}"
                )

            insight_subtype = annotation.subtype in {
                "unsupported_insight",
                "insight_exceeds_verified_wording",
                "insight_missing_source_support",
                "single_fact_relabelled_as_insight",
                "unlabelled_hypothesis",
                "hypothesis_presented_as_conclusion",
                "unsupported_causal_interpretation",
                "unsupported_domain_interpretation",
                "unsupported_sports_narrative",
                "genre_mismatch",
            }
            if (
                insight_subtype
                and not annotation.insight_ids
                and not sentence_insight_ids.get(annotation.sentence)
                and annotation.subtype
                not in {
                    "unsupported_insight",
                    "unlabelled_hypothesis",
                    "unsupported_sports_narrative",
                    "genre_mismatch",
                }
            ):
                raise ModelRetry(
                    "Insight-specific annotations must reference the mapped "
                    "insight where one exists."
                )

        for repair in output.repairs:
            if repair.original_sentence not in report_text:
                raise ModelRetry(
                    "Every repair original_sentence must occur in the report."
                )

            unknown_annotations = (
                set(repair.annotation_ids)
                - all_annotation_ids
            )

            if unknown_annotations:
                raise ModelRetry(
                    "Repair references unknown annotation IDs."
                )

            if repair.original_sentence not in annotated_sentences:
                raise ModelRetry(
                    "A repair may target only a sentence with an annotation."
                )

            for candidate in repair.candidates:
                if (
                    repair_fact_ledger is not None
                    and repair_evidence_ledger is not None
                ):
                    repair_errors = validate_repair_candidate(
                        candidate,
                        repair_fact_ledger,
                        repair_evidence_ledger,
                        repair_insight_ledger,
                        allow_hypotheses,
                        original_text=(
                            repair.original_sentence
                        ),
                    )
                    if repair_errors:
                        raise ModelRetry(
                            "Repair candidate validation failed: "
                            + "; ".join(repair_errors)
                        )

                unknown = (
                    set(candidate.supporting_fact_ids)
                    - valid_fact_ids
                )

                if unknown:
                    raise ModelRetry(
                        f"Unknown repair fact IDs: {sorted(unknown)}"
                    )

                unknown_evidence = (
                    set(candidate.supporting_evidence_ids)
                    - valid_evidence_ids
                )

                if unknown_evidence:
                    raise ModelRetry(
                        "Unknown repair evidence IDs: "
                        f"{sorted(unknown_evidence)}"
                    )

                unknown_insights = (
                    set(candidate.supporting_insight_ids)
                    - all_insight_ids
                )
                if unknown_insights:
                    raise ModelRetry(
                        "Unknown repair insight IDs: "
                        f"{sorted(unknown_insights)}"
                    )

                if (
                    set(candidate.supporting_insight_ids)
                    & hypothesis_only_insight_ids
                    and not allow_hypotheses
                ):
                    raise ModelRetry(
                        "Repairs may not introduce hypotheses while the "
                        "feature is disabled."
                    )

                for insight_id in candidate.supporting_insight_ids:
                    insight_statement = insight_statements.get(
                        insight_id,
                        "",
                    )
                    replacement = candidate.replacement_text
                    if (
                        replacement
                        and insight_statement
                        and CAUSAL_PATTERN.search(replacement)
                        and not CAUSAL_PATTERN.search(insight_statement)
                    ):
                        raise ModelRetry(
                            "A repair candidate strengthens a verified insight "
                            "with causal wording."
                        )

                    if (
                        replacement
                        and UNIVERSAL_GENERALISATION_PATTERN.search(replacement)
                        and not UNIVERSAL_GENERALISATION_PATTERN.search(
                            insight_statement
                        )
                    ):
                        raise ModelRetry(
                            "A repair candidate generalises beyond its verified "
                            "insight."
                        )

        if output.recommended_decision == AuditDecision.BLOCK:
            semantic_serious = any(
                annotation.severity
                in {
                    Severity.HIGH,
                    Severity.CRITICAL,
                }
                for annotation in output.annotations
            )

            if (
                not semantic_serious
                and not deterministic_serious_annotation_ids
            ):
                raise ModelRetry(
                    "recommended_decision=BLOCK requires at least one "
                    "high or critical deterministic or semantic annotation."
                )

        invalid_quality_findings = [
            finding
            for finding in output.quality_assessment.findings
            if not valid_quality_finding(finding)
        ]

        if invalid_quality_findings:
            raise ModelRetry(
                "Quality findings must describe report defects, not plain "
                "dataset observations: "
                + "; ".join(invalid_quality_findings)
            )

        return output

    return agent


def fallback_understanding(
    profile: DataProfile,
) -> DataUnderstanding:
    tables: list[TableUnderstanding] = []
    supported_routes = {
        AnalysisRoute.DESCRIPTIVE
    }

    for table in profile.tables:
        numeric = [
            column
            for column in table.columns
            if column.semantic_type == "numeric"
            and not column.constant
        ]
        categorical = [
            column
            for column in table.columns
            if column.semantic_type == "categorical"
        ]
        datetime = [
            column
            for column in table.columns
            if column.semantic_type == "datetime"
        ]

        if len(numeric) >= 2 or (numeric and categorical):
            supported_routes.add(
                AnalysisRoute.ASSOCIATION_COMPARISON
            )

        if table.row_count >= 100 and numeric:
            supported_routes.add(
                AnalysisRoute.PREDICTIVE
            )

        if table.row_count >= 40 and numeric and datetime:
            supported_routes.add(
                AnalysisRoute.FORECASTING
            )

        supported_routes.add(
            AnalysisRoute.CAUSAL_FEASIBILITY
        )

        if table.candidate_keys:
            unit = (
                f"one row per unique `{table.candidate_keys[0]}` value"
            )
        else:
            unit = (
                f"one row per observed record in `{table.table_name}`"
            )

        meanings = [
            ColumnMeaning(
                table_name=table.table_name,
                column_name=column.name,
                inferred_role=(
                    "candidate_identifier"
                    if column.candidate_key
                    else column.semantic_type
                ),
                interpretation=(
                    f"Observed `{column.name}` column with provisional "
                    f"{column.semantic_type} analytical role."
                ),
                evidence_basis=(
                    f"dtype={column.dtype}; unique={column.unique_count}; "
                    f"missing_rate={column.missing_rate:.2%}"
                ),
                confidence=(
                    0.95 if column.candidate_key else 0.70
                ),
                caveat=(
                    "The scientific or business meaning is not confirmed "
                    "by the data alone."
                ),
            )
            for column in table.columns
        ]

        risks: list[ColumnRisk] = []

        for column in table.columns:
            if column.constant:
                risks.append(
                    ColumnRisk(
                        table_name=table.table_name,
                        column_name=column.name,
                        risk_type="constant_column",
                        explanation=(
                            "The column has one observed non-missing value."
                        ),
                        analytical_consequence=(
                            "Exclude it from correlation, comparison, "
                            "prediction, and forecasting."
                        ),
                        confidence=1.0,
                    )
                )

            if column.suspicious_zero_values:
                risks.append(
                    ColumnRisk(
                        table_name=table.table_name,
                        column_name=column.name,
                        risk_type="possible_sentinel_zero",
                        explanation=(
                            "Zero observations are separated from most of "
                            "the positive distribution."
                        ),
                        analytical_consequence=(
                            "Validate the zeros before relying on analyses "
                            "using this field."
                        ),
                        confidence=0.85,
                    )
                )

        tables.append(
            TableUnderstanding(
                table_name=table.table_name,
                unit_of_observation=unit,
                summary=(
                    f"`{table.table_name}` has {table.row_count:,} rows "
                    f"and {table.column_count:,} columns."
                ),
                likely_keys=table.candidate_keys,
                column_meanings=meanings,
                column_risks=risks,
                quality_findings=table.warnings,
                usability_notes=[
                    "Constant columns should not enter analytical models.",
                    "Predictive targets require user, metadata, or explicit "
                    "experimental confirmation.",
                    "Temporal data should use chronological validation.",
                    "Causal conclusions require a defensible identification design.",
                ],
            )
        )

    return DataUnderstanding(
        profile_fingerprint=profile.fingerprint,
        dataset_summary=(
            f"The input contains {len(profile.tables)} profiled table(s). "
            "Semantic interpretations remain provisional without metadata."
        ),
        tables=tables,
        cross_table_notes=(
            [
                "Multiple tables were supplied. Joins are not assumed "
                "without explicit key evidence."
            ]
            if len(profile.tables) > 1
            else []
        ),
        supported_routes=sorted(
            supported_routes,
            key=lambda route: route.value,
        ),
        uncertain_routes=[],
        global_caveats=[
            "The data alone do not confirm provenance or domain semantics.",
            "Sampling, missingness, measurement, and temporal limitations "
            "may affect findings.",
        ],
    )


def select_explicit_target(
    request: str,
    table: Any,
) -> str | None:
    for column in table.columns:
        if re.search(
            rf"\b{re.escape(column.name.lower())}\b",
            request.lower(),
        ):
            return column.name

    return None


def event_report_requested(
    request: str,
) -> bool:
    return bool(
        re.search(
            r"\b(write|create|produce|give|prepare)?\s*"
            r"(?:a\s+)?(?:event|sports|game|match)\s+report\b|"
            r"\bwrite up (?:the|this) (?:event|game|match)\b",
            request,
            re.IGNORECASE,
        )
    )


def sports_game_report_requested(
    request: str,
) -> bool:
    return event_report_requested(request)


def profile_supports_sports_game_report(
    profile: DataProfile,
) -> bool:
    names = {
        column.name.lower()
        for table in profile.tables
        for column in table.columns
    }
    table_names = {
        table.table_name.lower()
        for table in profile.tables
    }

    has_subject = any(
        token in name
        for name in names
        for token in {"team", "player", "opponent"}
    )
    has_result = any(
        token in name
        for name in names
        for token in {"score", "points", "winner", "result"}
    )
    game_named = any(
        token in name
        for name in table_names
        for token in {"game", "match", "boxscore", "box_score"}
    )

    return has_subject and has_result and game_named


def fallback_insight_objectives(
    *,
    tasks: list[InvestigationTask],
    genre: ReportGenre,
    enabled: bool,
) -> list[InsightObjective]:
    if not enabled:
        return []

    task_ids = [task.task_id for task in tasks]

    if genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }:
        questions = [
            (
                "What verified facts best describe the result without "
                "implying unsupported causality?",
                [InsightType.NARRATIVE_SUMMARY],
            ),
            (
                "Which verified performances are most salient to the game "
                "report?",
                [InsightType.DOMINANT_PATTERN, InsightType.CONTRAST],
            ),
            (
                "Which verified team-level contrasts define the bounded game "
                "narrative?",
                [InsightType.CONTRAST, InsightType.NARRATIVE_SUMMARY],
            ),
            (
                "Are any conventional milestones explicitly supported by the "
                "verified facts?",
                [InsightType.NARRATIVE_SUMMARY],
            ),
        ]
    else:
        questions = [
            (
                "Which verified findings jointly describe the strongest "
                "structure in the data?",
                [InsightType.DOMINANT_PATTERN, InsightType.NARRATIVE_SUMMARY],
            ),
            (
                "What is the strongest non-redundant verified contrast?",
                [InsightType.CONTRAST],
            ),
            (
                "Do any verified variables contain substantially overlapping "
                "information in this dataset?",
                [InsightType.REDUNDANCY, InsightType.OUTCOME_ASSOCIATION],
            ),
            (
                "Which verified data-quality issue most affects interpretation?",
                [InsightType.DATA_QUALITY_IMPLICATION, InsightType.ANOMALY],
            ),
            (
                "What bounded message should the reader remember from the "
                "verified findings?",
                [InsightType.NARRATIVE_SUMMARY],
            ),
        ]

    return [
        InsightObjective(
            objective_id=f"INSIGHT_OBJECTIVE_{index:03d}",
            question=question,
            preferred_insight_types=insight_types,
            relevant_task_ids=task_ids,
        )
        for index, (question, insight_types) in enumerate(
            questions,
            start=1,
        )
    ]


def fallback_execution_plan(
    request: str,
    profile: DataProfile,
    audit_mode: AuditMode,
    settings: Settings,
    *,
    input_structure: InputStructureProfile | None = None,
    available_capabilities: list[EvidenceCapability] | None = None,
    report_genre_override: ReportGenre | None = None,
) -> ExecutionPlan:
    tasks: list[InvestigationTask] = []
    available_capabilities = available_capabilities or []
    explicit_event_request = event_report_requested(request)
    explicit_data_science_request = bool(
        re.search(
            r"\b(data[- ]science report|statistical analysis)\b",
            request,
            re.IGNORECASE,
        )
    )
    structured_event = bool(
        input_structure is not None
        and input_structure.shape == InputShape.EVENT_RECORD
        and input_structure.confidence >= 0.7
    )
    report_genre = (
        ReportGenre.EVENT_REPORT
        if explicit_event_request
        else (
            ReportGenre.DATA_SCIENCE_REPORT
            if explicit_data_science_request
            else (
                report_genre_override
                if report_genre_override is not None
                else (
                    ReportGenre.EVENT_REPORT
                    if structured_event
                    else (
                        ReportGenre.DATASET_OVERVIEW
                        if re.search(
                            r"\bdataset overview\b",
                            request,
                            re.IGNORECASE,
                        )
                        else ReportGenre.DATA_SCIENCE_REPORT
                    )
                )
            )
        )
    )

    if explicit_event_request or explicit_data_science_request:
        selection_source = ReportSelectionSource.EXPLICIT_USER_REQUEST
    elif report_genre_override is not None:
        selection_source = ReportSelectionSource.EXPERIMENT_CONFIGURATION
    elif structured_event:
        selection_source = ReportSelectionSource.STRUCTURED_INFERENCE
    else:
        selection_source = ReportSelectionSource.FALLBACK

    if report_genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    } and profile.tables:
        event_table = profile.tables[0]
        event_task_specs = [
            (
                EvidenceCapability.EVENT_OUTCOME,
                AnalysisRoute.DESCRIPTIVE,
                "What is the verified event result, context, status and score progression?",
                [
                    "event_outcome",
                    "event_context",
                    "event_status",
                    "participant_record_context",
                    "score_progression",
                ],
            ),
            (
                EvidenceCapability.ENTITY_PERFORMANCE,
                AnalysisRoute.DESCRIPTIVE,
                "Which recorded entity performances are most salient?",
                ["entity_performance"],
            ),
            (
                EvidenceCapability.RANKING,
                AnalysisRoute.DESCRIPTIVE,
                "Which entities lead the recorded performance rankings?",
                ["entity_ranking"],
            ),
            (
                EvidenceCapability.GROUP_COMPARISON,
                AnalysisRoute.ASSOCIATION_COMPARISON,
                "What are the strongest participant-level contrasts?",
                ["participant_comparison"],
            ),
        ]
        for capability, route, question, evidence_types in event_task_specs:
            if capability not in available_capabilities:
                continue
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=question,
                    route=route,
                    priority=5 if capability == EvidenceCapability.EVENT_OUTCOME else 4,
                    table_name=event_table.table_name,
                    columns=[column.name for column in event_table.columns],
                    capability=capability,
                    input_fields=[column.name for column in event_table.columns],
                    entity_scope=input_structure.entity_levels if input_structure else [],
                    expected_evidence_types=evidence_types,
                    required_evidence=evidence_types,
                    claim_permissions=[
                        ClaimPermission.DESCRIPTIVE,
                        ClaimPermission.COMPARATIVE,
                    ],
                    answerability_note=("Answerable from verified structured-event evidence."),
                )
            )

    predictive_requested = bool(
        re.search(
            r"\b(predict|prediction|model|classify|estimate)\b",
            request,
            re.IGNORECASE,
        )
    )
    forecast_requested = bool(
        re.search(
            r"\b(forecast|future|time series|ahead)\b",
            request,
            re.IGNORECASE,
        )
    )
    causal_requested = bool(
        re.search(
            r"\b(cause|causal|effect|impact|intervention)\b",
            request,
            re.IGNORECASE,
        )
    )

    for table in profile.tables:
        if report_genre in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }:
            continue

        tasks.append(
            InvestigationTask(
                task_id=f"TASK_{len(tasks) + 1:03d}",
                question=(
                    f"What are the structure, data quality, distributions, "
                    f"and analytically important fields in `{table.table_name}`?"
                ),
                route=AnalysisRoute.DESCRIPTIVE,
                priority=5,
                table_name=table.table_name,
                columns=[
                    column.name
                    for column in table.columns
                ],
                required_evidence=[
                    "dimensions",
                    "missingness",
                    "distribution diagnostics",
                    "constant columns",
                    "possible sentinel values",
                ],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.METHODOLOGICAL,
                    ClaimPermission.INSUFFICIENCY,
                ],
                answerability_note=(
                    "Directly answerable through deterministic profiling."
                ),
            )
        )

        numeric = [
            column.name
            for column in table.columns
            if column.semantic_type == "numeric"
            and not column.constant
        ]
        categorical = [
            column.name
            for column in table.columns
            if column.semantic_type == "categorical"
        ]
        datetime_columns = [
            column.name
            for column in table.columns
            if column.semantic_type == "datetime"
        ]

        if len(numeric) >= 2 or (numeric and categorical):
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Which substantively meaningful associations and group "
                        f"differences are present in `{table.table_name}`?"
                    ),
                    route=AnalysisRoute.ASSOCIATION_COMPARISON,
                    priority=4,
                    table_name=table.table_name,
                    columns=(numeric + categorical)[:20],
                    required_evidence=[
                        "effect magnitude",
                        "group counts",
                        "sampling method",
                        "association caveats",
                    ],
                    claim_permissions=[
                        ClaimPermission.ASSOCIATIONAL,
                        ClaimPermission.COMPARATIVE,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "Answerable as observed association and comparison, not causation."
                    ),
                )
            )

        target = select_explicit_target(
            request,
            table,
        )

        if predictive_requested and target:
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Can `{target}` be predicted better than a simple baseline "
                        "after leakage screening?"
                    ),
                    route=AnalysisRoute.PREDICTIVE,
                    priority=3,
                    table_name=table.table_name,
                    target_column=target,
                    target_status=TargetStatus.USER_SELECTED,
                    prediction_definition=(
                        f"Estimate `{target}` using fields available in the supplied table."
                    ),
                    time_column=(
                        datetime_columns[0]
                        if datetime_columns
                        else None
                    ),
                    validation_strategy=(
                        ValidationStrategy.CHRONOLOGICAL_HOLDOUT
                        if datetime_columns
                        else ValidationStrategy.RANDOM_HOLDOUT
                    ),
                    required_evidence=[
                        "target confirmation",
                        "proxy leakage audit",
                        "feature exclusions",
                        "baseline comparison",
                        "holdout metrics",
                    ],
                    claim_permissions=[
                        ClaimPermission.PREDICTIVE,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "A positive result requires leakage-audited baseline improvement."
                    ),
                )
            )

        if forecast_requested and target and datetime_columns:
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Can `{target}` be forecast using rolling temporal "
                        "evaluation and seasonal baselines?"
                    ),
                    route=AnalysisRoute.FORECASTING,
                    priority=3,
                    table_name=table.table_name,
                    target_column=target,
                    target_status=TargetStatus.USER_SELECTED,
                    time_column=datetime_columns[0],
                    validation_strategy=ValidationStrategy.ROLLING_ORIGIN,
                    required_evidence=[
                        "time ordering",
                        "rolling folds",
                        "last-value baseline",
                        "seasonal-naive baselines",
                        "candidate-model metrics",
                    ],
                    claim_permissions=[
                        ClaimPermission.FORECAST,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "A positive forecast claim requires consistent improvement "
                        "over the strongest relevant naive baseline."
                    ),
                )
            )

        if causal_requested:
            tasks.append(
                InvestigationTask(
                    task_id=f"TASK_{len(tasks) + 1:03d}",
                    question=(
                        f"Does `{table.table_name}` support a defensible "
                        "causal identification strategy?"
                    ),
                    route=AnalysisRoute.CAUSAL_FEASIBILITY,
                    priority=2,
                    table_name=table.table_name,
                    required_evidence=[
                        "exposure",
                        "outcome",
                        "time ordering",
                        "confounders",
                        "identification design",
                    ],
                    claim_permissions=[
                        ClaimPermission.CAUSAL,
                        ClaimPermission.METHODOLOGICAL,
                        ClaimPermission.INSUFFICIENCY,
                    ],
                    answerability_note=(
                        "The likely output is a causal-feasibility or insufficiency finding."
                    ),
                )
            )

    route_order = [
        route
        for route in [
            AnalysisRoute.DESCRIPTIVE,
            AnalysisRoute.ASSOCIATION_COMPARISON,
            AnalysisRoute.PREDICTIVE,
            AnalysisRoute.FORECASTING,
            AnalysisRoute.CAUSAL_FEASIBILITY,
        ]
        if any(task.route == route for task in tasks)
    ]

    return ExecutionPlan(
        objective=request,
        tasks=tasks[:10],
        route_order=route_order,
        report_specification=ReportSpecification(
            report_purpose=request,
            genre=report_genre,
            perspective=ReportPerspective.NEUTRAL,
            communication_goal=(
                "Explain the verified result, leading performances and "
                "major team contrasts."
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else (
                    "Describe the table structure and strongest supported "
                    "findings concisely."
                    if report_genre == ReportGenre.DATASET_OVERVIEW
                    else "Summarise the strongest supported findings."
                )
            ),
            target_length_words=(
                settings.writer_target_words
            ),
            maximum_length_words=(
                settings.writer_max_words
            ),
            maximum_main_findings=settings.writer_max_main_findings,
            maximum_supporting_facts=(
                settings.writer_supporting_fact_limit
            ),
            preferred_sections=(
                [
                    "Event overview",
                    "Score progression",
                    "Key performances",
                    "Participant contrasts",
                    "Scope limitations",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else [
                    "Overview and data quality",
                    "Strongest observed relationships",
                    "Modelling and validation",
                    "Limitations and next steps",
                ]
            ),
            required_components=(
                []
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else [
                    ReportComponent.DATASET_OVERVIEW,
                    ReportComponent.DATA_QUALITY,
                    ReportComponent.STRONGEST_RELATIONSHIPS,
                    ReportComponent.LIMITATIONS_NEXT_STEPS,
                ]
            ),
            required_content_slots=(
                [
                    "event_result",
                    "event_context",
                    "participant_record_context",
                    "event_status",
                    "score_progression",
                    "event_sequence",
                    "leading_performance",
                    "main_contrast",
                    "scope_limitations",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else [
                    "dataset_scope",
                    "material_data_quality_issue",
                    "strongest_analytical_finding",
                    "limitation",
                ]
            ),
            optional_content_slots=(
                [
                    "secondary_performance",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else []
            ),
            prohibited_claim_types=(
                [
                    "unsupported_chronology",
                    "unsupported_milestone",
                    "unsupported_historical_significance",
                    "unsupported_causality",
                ]
                if report_genre
                in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                else ["unsupported_causality"]
            ),
            selection_source=selection_source,
            selection_confidence=(
                1.0
                if selection_source
                in {
                    ReportSelectionSource.EXPLICIT_USER_REQUEST,
                    ReportSelectionSource.EXPERIMENT_CONFIGURATION,
                }
                else 0.8
            ),
            include_negative_findings=(
                report_genre
                not in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
            ),
            include_methodological_details=(
                report_genre
                not in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
            ),
            prioritisation_rule=(
                "Prefer high-confidence, methodologically strong, user-relevant "
                "findings. Omit negligible effects and repetitive metadata."
            ),
        ),
        audit_mode=audit_mode,
        insight_objectives=fallback_insight_objectives(
            tasks=tasks[:10],
            genre=report_genre,
            enabled=settings.enable_insight_synthesis,
        ),
        available_capabilities=available_capabilities,
        selected_capabilities=[
            capability
            for capability in available_capabilities
            if (
                report_genre
                not in {
                    ReportGenre.EVENT_REPORT,
                    ReportGenre.SPORTS_GAME_REPORT,
                }
                or capability
                in {
                    EvidenceCapability.DATASET_PROFILE,
                    EvidenceCapability.EVENT_OUTCOME,
                    EvidenceCapability.ENTITY_PERFORMANCE,
                    EvidenceCapability.RANKING,
                    EvidenceCapability.GROUP_COMPARISON,
                }
            )
        ],
        revision_limit=settings.max_revision_rounds,
        maximum_facts=None,
        frozen=True,
        rationale=(
            "The deterministic fallback plans descriptive and meaningful "
            "association work by default. Prediction, forecasting, and causal "
            "routes are added only when requested and sufficiently specified."
        ),
    )
