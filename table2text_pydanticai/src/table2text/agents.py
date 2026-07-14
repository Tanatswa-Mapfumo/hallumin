from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, ModelRetry, ModelSettings, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.output import NativeOutput, PromptedOutput
from pydantic_ai.providers.ollama import OllamaProvider

from .audit import (
    validate_fact_candidates,
    validate_writer_output,
)
from .config import Settings
from .schemas import (
    AnalysisRoute,
    AuditMode,
    AuditRepairProposal,
    ClaimPermission,
    ColumnMeaning,
    ColumnRisk,
    DataProfile,
    DataUnderstanding,
    ExecutionPlan,
    FactCandidateSet,
    FactLedger,
    InvestigationTask,
    ReportComponent,
    ReportSpecification,
    TableUnderstanding,
    TargetStatus,
    ValidationStrategy,
    VerificationResult,
    WriterOutput,
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

Use only the supplied deterministic profile.

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
        model_settings=ModelSettings(
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

        return output

    return agent


ORCHESTRATOR_INSTRUCTIONS = """
You are the Orchestrator and Investigation Planner.

Create a frozen analytical plan before analytical results are observed.

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
- Include a report specification with a finding budget and target length.
- Do not let one analytical route dominate a general dataset-understanding
  report.
- For requests asking to understand a dataset, require dataset overview,
  data quality, strongest relationships, limitations, and next steps.
- Prediction and forecasting remain optional and must not be added unless the
  request or confirmed metadata supports them.
- Do not rewrite or replace the user's objective with a different objective.
- Negative and insufficiency findings are valid.
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
        model_settings=ModelSettings(
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
        allow_experimental = context.deps.payload[
            "allow_experimental_targets"
        ]

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

        seen: set[str] = set()

        for task in output.tasks:
            if task.task_id in seen:
                raise ModelRetry(
                    f"Duplicate task ID: {task.task_id}"
                )
            seen.add(task.task_id)

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

        if user_request and re.search(
            r"\b(understand|overview|summari[sz]e|describe|strongest findings)\b",
            user_request,
            re.IGNORECASE,
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
        model_settings=ModelSettings(
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
        model_settings=ModelSettings(
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


WRITER_INSTRUCTIONS = """
You are an expert data scientist and natural report writer.

Use the supplied verified evidence to produce a selective, coherent,
reader-facing data-science report.

You have freedom over:
- wording;
- structure;
- selection;
- synthesis;
- paragraph organisation;
- explanation;
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
- Strength:
- Interpretation Notes:
- Recommended Use:
- Methodological Strength:
- User Relevance:
- Salience:
- Global Prohibited Interpretations

Translate effect labels and metrics into natural prose.

For example, do not write:

"Strength: Large group difference; Standardized Difference: 1.00"

Write naturally:

"The groups differ substantially; the standardised mean difference is
approximately 1.0."

Use the unit of observation supplied by the Data Understanding Agent.
Do not replace "observations", "records", "rows", "patients", "recipes",
or other identified units with "events", "cases", "experiments", or
"subjects" unless that terminology is explicitly supported.

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

Every factual sentence must be represented in the hidden sentence support
map.

Return:
1. natural Markdown;
2. a hidden sentence support map;
3. selected and omitted fact IDs.

Every factual sentence must occur verbatim in sentence_support.
Non-factual transitions may be marked non_factual_transition.
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
            WriterOutput,
            settings,
        ),
        instructions=WRITER_INSTRUCTIONS,
        model_settings=ModelSettings(
            temperature=0.35,
            max_tokens=11_000,
        ),
        retries={"output": 3},
    )

    @agent.output_validator
    def validate_output(
        context: RunContext[AgentDependencies],
        output: WriterOutput,
    ) -> WriterOutput:
        ledger = FactLedger.model_validate(
            context.deps.payload["fact_ledger"]
        )

        errors = validate_writer_output(
            output,
            ledger,
        )

        if errors:
            raise ModelRetry(
                "Writer output validation failed:\n- "
                + "\n- ".join(errors)
            )

        return output.model_copy(
            update={
                "writer_mode": "llm_writer",
                "eligible_for_primary_evaluation": True,
            }
        )

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
- deterministic audit findings;
- methodological limitations;
- optional trusted external facts.

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

Internal-control leakage is a report-quality problem.

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
        model_settings=ModelSettings(
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

        annotation_ids = {
            annotation.annotation_id
            for annotation in output.annotations
        }

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

        for repair in output.repairs:
            if repair.original_sentence not in report_text:
                raise ModelRetry(
                    "Every repair original_sentence must occur in the report."
                )

            unknown_annotations = (
                set(repair.annotation_ids) - annotation_ids
            )

            if unknown_annotations:
                raise ModelRetry(
                    "Repair references unknown annotation IDs."
                )

            for candidate in repair.candidates:
                unknown = (
                    set(candidate.supporting_fact_ids)
                    - valid_fact_ids
                )

                if unknown:
                    raise ModelRetry(
                        f"Unknown repair fact IDs: {sorted(unknown)}"
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


def fallback_execution_plan(
    request: str,
    profile: DataProfile,
    audit_mode: AuditMode,
    settings: Settings,
) -> ExecutionPlan:
    tasks: list[InvestigationTask] = []

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
            target_length_words=settings.writer_target_words,
            maximum_main_findings=settings.writer_max_main_findings,
            preferred_sections=[
                "Overview and data quality",
                "Strongest observed relationships",
                "Modelling and validation",
                "Limitations and next steps",
            ],
            required_components=[
                ReportComponent.DATASET_OVERVIEW,
                ReportComponent.DATA_QUALITY,
                ReportComponent.STRONGEST_RELATIONSHIPS,
                ReportComponent.LIMITATIONS_NEXT_STEPS,
            ],
            include_negative_findings=True,
            include_methodological_details=True,
            prioritisation_rule=(
                "Prefer high-confidence, methodologically strong, user-relevant "
                "findings. Omit negligible effects and repetitive metadata."
            ),
        ),
        audit_mode=audit_mode,
        revision_limit=settings.max_revision_rounds,
        maximum_facts=80,
        frozen=True,
        rationale=(
            "The deterministic fallback plans descriptive and meaningful "
            "association work by default. Prediction, forecasting, and causal "
            "routes are added only when requested and sufficiently specified."
        ),
    )
