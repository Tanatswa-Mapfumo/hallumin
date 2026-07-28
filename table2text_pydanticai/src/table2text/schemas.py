from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AnalysisRoute(str, Enum):
    DESCRIPTIVE = "descriptive"
    ASSOCIATION_COMPARISON = "association_comparison"
    PREDICTIVE = "predictive"
    FORECASTING = "forecasting"
    CAUSAL_FEASIBILITY = "causal_feasibility"


class ClaimPermission(str, Enum):
    DESCRIPTIVE = "descriptive_claims_allowed"
    COMPARATIVE = "comparative_claims_allowed"
    ASSOCIATIONAL = "associational_claims_allowed"
    PREDICTIVE = "predictive_claims_allowed_after_validation"
    FORECAST = "forecast_claims_allowed_after_validation"
    CAUSAL = "causal_claims_allowed_only_with_verified_design"
    INSUFFICIENCY = "insufficiency_claims_allowed"
    METHODOLOGICAL = "methodological_interpretation_allowed"


class InterpretationLevel(str, Enum):
    FINDING = "finding"
    BOUNDED_INSIGHT = "bounded_insight"
    HYPOTHESIS = "hypothesis"


class ReportGenre(str, Enum):
    DATA_SCIENCE_REPORT = "data_science_report"
    DATASET_OVERVIEW = "dataset_overview"
    EVENT_REPORT = "event_report"
    # Retained for compatibility with existing notebook artifacts.
    SPORTS_GAME_REPORT = "sports_game_report"


class ReportPerspective(str, Enum):
    NEUTRAL = "neutral"
    SUBJECT_CENTRED = "subject_centred"


class ReportSelectionSource(str, Enum):
    EXPLICIT_USER_REQUEST = "explicit_user_request"
    EXPERIMENT_CONFIGURATION = "experiment_configuration"
    STRUCTURED_INFERENCE = "structured_inference"
    FALLBACK = "fallback"


class InputShape(str, Enum):
    FLAT_TABLE = "flat_table"
    NESTED_RECORD = "nested_record"
    ENTITY_COLLECTION = "entity_collection"
    EVENT_RECORD = "event_record"
    TIME_SERIES = "time_series"
    INPUT_REFERENCE_PAIRS = "input_reference_pairs"
    AMBIGUOUS = "ambiguous"


class SemanticRole(str, Enum):
    IDENTIFIER = "identifier"
    CONTEXT = "context"
    TIME = "time"
    LOCATION = "location"
    STATUS = "status"
    PARTICIPANT_IDENTIFIER = "participant_identifier"
    ENTITY_IDENTIFIER = "entity_identifier"
    OUTCOME_MEASURE = "outcome_measure"
    PERFORMANCE_MEASURE = "performance_measure"
    MEASURE = "measure"
    CATEGORY = "category"
    METADATA = "metadata"


class AnalyticalFunction(str, Enum):
    OUTCOME = "outcome"
    OUTCOME_COMPONENT = "outcome_component"
    PERFORMANCE = "performance"
    PARTICIPATION = "participation"
    CONTEXT = "context"


class SemanticLevel(str, Enum):
    DATASET = "dataset"
    EVENT = "event"
    PARTICIPANT = "participant"
    ENTITY = "entity"
    OBSERVATION = "observation"


class EvidenceOperation(str, Enum):
    RETRIEVE = "retrieve"
    COMPARE = "compare"
    RANK = "rank"


class InputRepresentationStatus(str, Enum):
    VALID = "valid"
    VALID_WITH_WARNINGS = "valid_with_warnings"
    AMBIGUOUS = "ambiguous"
    INVALID = "invalid"


class EvidenceCapability(str, Enum):
    DATASET_PROFILE = "dataset_profile"
    MISSINGNESS = "missingness"
    DUPLICATES = "duplicates"
    DISTRIBUTION_SUMMARY = "distribution_summary"
    ASSOCIATION = "association"
    GROUP_COMPARISON = "group_comparison"
    RANKING = "ranking"
    EXTREMA = "extrema"
    TEMPORAL_CHANGE = "temporal_change"
    EVENT_OUTCOME = "event_outcome"
    ENTITY_PERFORMANCE = "entity_performance"
    ANOMALY_DETECTION = "anomaly_detection"


class InsightType(str, Enum):
    DOMINANT_PATTERN = "dominant_pattern"
    CONTRAST = "contrast"
    REDUNDANCY = "redundancy"
    ANOMALY = "anomaly"
    OUTCOME_ASSOCIATION = "outcome_association"
    TRADE_OFF = "trade_off"
    DATA_QUALITY_IMPLICATION = "data_quality_implication"
    NARRATIVE_SUMMARY = "narrative_summary"


class InsightContribution(str, Enum):
    ANALYTICAL_IMPLICATION = "analytical_implication"
    EVENT_SYNTHESIS = "event_synthesis"
    DESCRIPTIVE_SYNTHESIS = "descriptive_synthesis"


class InsightVerificationStatus(str, Enum):
    VERIFIED = "verified"
    VERIFIED_WITH_CAVEAT = "verified_with_caveat"
    HYPOTHESIS_ONLY = "hypothesis_only"
    REJECTED = "rejected"


class AuditMode(str, Enum):
    INTERNAL = "internal_evidence_fidelity"
    EXTERNAL = "external_truth_mode"
    ANNOTATION_ONLY = "annotation_only"


class AuditDecision(str, Enum):
    PASS = "pass"
    REVISE = "revise"
    BLOCK = "block"


class ReleaseStatus(str, Enum):
    APPROVED = "approved"
    APPROVED_WITH_WARNINGS = "approved_with_warnings"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class ReviewDecision(str, Enum):
    APPROVE = "approve"
    CAUTION = "caution"
    REJECT = "reject"


class VerificationMethod(str, Enum):
    LLM_VERIFIED = "llm_verified"
    DETERMINISTIC_EVIDENCE_RECOVERY = (
        "deterministic_evidence_recovery"
    )


class ErrorType(str, Enum):
    INCORRECT_NAMED_ENTITY = "incorrect_named_entity"
    INCORRECT_NUMBER = "incorrect_number"
    INCORRECT_WORD = "incorrect_word"
    CONTEXT_ERROR = "context_error"
    SUPPORT_MAPPING_ERROR = "support_mapping_error"
    NOT_CHECKABLE = "not_checkable"
    OTHER = "other"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendedUse(str, Enum):
    HEADLINE = "headline"
    MAIN_FINDING = "main_finding"
    SUPPORTING_DETAIL = "supporting_detail"
    LIMITATION = "limitation"
    OMIT_UNLESS_REQUESTED = "omit_unless_requested"


class ZeroRisk(str, Enum):
    NONE = "none"
    LIKELY_VALID = "likely_valid_zero"
    CONTEXT_DEPENDENT = "context_dependent_zero"
    UNUSUAL = "unusual_zero"
    POSSIBLE_SENTINEL = "possible_sentinel_zero"


class ReportComponent(str, Enum):
    DATASET_OVERVIEW = "dataset_overview"
    DATA_QUALITY = "data_quality"
    STRONGEST_RELATIONSHIPS = "strongest_relationships"
    MODELLING_VALIDATION = "modelling_validation"
    LIMITATIONS_NEXT_STEPS = "limitations_next_steps"


class TargetStatus(str, Enum):
    USER_SELECTED = "user_selected"
    METADATA_CONFIRMED = "metadata_confirmed"
    EXPERIMENTAL_CANDIDATE = "experimental_candidate"
    UNCONFIRMED = "unconfirmed"


class ValidationStrategy(str, Enum):
    NONE = "none"
    RANDOM_HOLDOUT = "random_holdout"
    STRATIFIED_HOLDOUT = "stratified_holdout"
    CHRONOLOGICAL_HOLDOUT = "chronological_holdout"
    ROLLING_ORIGIN = "rolling_origin"


class SupportType(str, Enum):
    DIRECT = "direct"
    PARAPHRASE = "paraphrase"
    MULTI_FACT_SYNTHESIS = "multi_fact_synthesis"
    NON_FACTUAL = "non_factual_transition"


class RepairStrategy(str, Enum):
    MINIMAL_CORRECTION = "minimal_correction"
    EVIDENCE_REWRITE = "evidence_constrained_rewrite"
    HEDGED_REWRITE = "hedged_rewrite"
    DELETE = "delete_sentence"


class QualityStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    REVISE = "revise"


class QualityIssueType(str, Enum):
    MISSING_REQUIRED_COMPONENT = "missing_required_component"
    LEDGER_STYLE_RENDERING = "ledger_style_rendering"
    REPETITIVE_CAVEAT = "repetitive_caveat"
    GENERIC_OPENING = "generic_opening"
    WEAK_FINDING_SELECTION = "weak_finding_selection"
    ROUTE_DOMINANCE = "route_dominance"
    UNSUPPORTED_METHOD_INTERPRETATION = "unsupported_method_interpretation"


class EvaluationFieldPolicy(StrictModel):
    operational_input_paths: list[str] = Field(default_factory=list)
    held_out_reference_paths: list[str] = Field(default_factory=list)
    metadata_paths: list[str] = Field(default_factory=list)


class InputStructureProfile(StrictModel):
    shape: InputShape
    representation_status: InputRepresentationStatus

    source_paths: list[str] = Field(default_factory=list)
    row_semantics: str | None = None
    entity_levels: list[str] = Field(default_factory=list)
    nested_paths: list[str] = Field(default_factory=list)

    probable_input_fields: list[str] = Field(default_factory=list)
    probable_reference_fields: list[str] = Field(default_factory=list)
    probable_metadata_fields: list[str] = Field(default_factory=list)

    heterogeneous_rows_detected: bool = False
    sparse_flattening_detected: bool = False
    ambiguity_notes: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)


class StructuralField(StrictModel):
    table_name: str
    path_pattern: str
    value_types: list[str] = Field(default_factory=list)
    sample_values: list[str] = Field(default_factory=list)
    occurrence_count: int = Field(default=1, ge=1)


class SemanticBinding(StrictModel):
    binding_id: str
    table_name: str
    label: str
    role: SemanticRole
    level: SemanticLevel
    path_pattern: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_basis: str
    unit: str | None = None
    analytical_function: AnalyticalFunction | None = None


class InputSemanticMap(StrictModel):
    input_shape: InputShape
    record_description: str
    bindings: list[SemanticBinding] = Field(default_factory=list)
    recommended_report_genre: ReportGenre | None = None
    report_rationale: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    unresolved_ambiguities: list[str] = Field(default_factory=list)


class CapabilityDefinition(StrictModel):
    capability: EvidenceCapability
    supported_input_shapes: list[InputShape]

    requires_numeric_fields: bool = False
    requires_time_field: bool = False
    requires_entity_fields: bool = False
    requires_event_participants: bool = False
    requires_outcome_field: bool = False

    minimum_observations: int | None = None
    output_evidence_types: list[str] = Field(default_factory=list)


class GenreQualityAssessment(StrictModel):
    status: QualityStatus
    genre: ReportGenre

    required_slots: list[str] = Field(default_factory=list)
    supported_slots: list[str] = Field(default_factory=list)
    covered_slots: list[str] = Field(default_factory=list)
    missing_supported_slots: list[str] = Field(default_factory=list)

    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ColumnProfile(StrictModel):
    name: str
    dtype: str
    semantic_type: str

    missing_count: int
    missing_rate: float
    unique_count: int

    sample_values: list[str] = Field(default_factory=list)
    numeric_summary: dict[str, float | int] = Field(default_factory=dict)

    datetime_parse_rate: float = 0.0
    candidate_key: bool = False
    structured_values: bool = False

    constant: bool = False
    near_constant: bool = False
    dominant_value_rate: float = 0.0

    suspicious_zero_values: bool = False
    possible_sentinel_values: bool = False
    zero_risk: ZeroRisk = ZeroRisk.NONE
    zero_risk_reason: str | None = None

    quality_warnings: list[str] = Field(default_factory=list)


class TableProfile(StrictModel):
    table_name: str
    source_path: str

    row_count: int
    column_count: int
    duplicate_row_count: int

    candidate_keys: list[str] = Field(default_factory=list)
    columns: list[ColumnProfile] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DataProfile(StrictModel):
    fingerprint: str
    source_paths: list[str]
    tables: list[TableProfile]


class ColumnMeaning(StrictModel):
    table_name: str
    column_name: str
    inferred_role: str
    interpretation: str
    evidence_basis: str
    confidence: float = Field(ge=0.0, le=1.0)
    caveat: str | None = None


class ColumnRisk(StrictModel):
    table_name: str
    column_name: str
    risk_type: str
    explanation: str
    analytical_consequence: str
    confidence: float = Field(ge=0.0, le=1.0)


class TableUnderstanding(StrictModel):
    table_name: str
    unit_of_observation: str
    summary: str

    likely_keys: list[str] = Field(default_factory=list)
    column_meanings: list[ColumnMeaning] = Field(default_factory=list)
    column_risks: list[ColumnRisk] = Field(default_factory=list)

    quality_findings: list[str] = Field(default_factory=list)
    usability_notes: list[str] = Field(default_factory=list)


class DataUnderstanding(StrictModel):
    profile_fingerprint: str
    dataset_summary: str
    tables: list[TableUnderstanding]

    cross_table_notes: list[str] = Field(default_factory=list)
    supported_routes: list[AnalysisRoute] = Field(default_factory=list)
    uncertain_routes: list[str] = Field(default_factory=list)
    global_caveats: list[str] = Field(default_factory=list)
    semantic_map: InputSemanticMap | None = None


class ReportSpecification(StrictModel):
    intended_audience: str = "A reader seeking a data-science interpretation."
    report_purpose: str

    genre: ReportGenre = ReportGenre.DATA_SCIENCE_REPORT
    audience: str = "general analytical reader"
    perspective: ReportPerspective = ReportPerspective.NEUTRAL
    communication_goal: str = (
        "Summarise the strongest supported findings."
    )

    target_length_words: int = Field(ge=150, le=2_500)
    maximum_length_words: int | None = Field(
        default=None,
        ge=150,
        le=2_500,
    )
    maximum_main_findings: int | None = Field(default=None, ge=2)
    maximum_supporting_facts: int | None = Field(default=None, ge=2)

    preferred_sections: list[str] = Field(default_factory=list)
    required_components: list[ReportComponent] = Field(default_factory=list)
    required_content_slots: list[str] = Field(default_factory=list)
    optional_content_slots: list[str] = Field(default_factory=list)
    prohibited_claim_types: list[str] = Field(default_factory=list)

    selection_source: ReportSelectionSource = ReportSelectionSource.FALLBACK
    selection_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    unresolved_ambiguities: list[str] = Field(default_factory=list)

    include_negative_findings: bool = True
    include_methodological_details: bool = True

    prioritisation_rule: str


class InvestigationTask(StrictModel):
    task_id: str
    question: str

    route: AnalysisRoute
    priority: int = Field(ge=1, le=5)

    table_name: str
    columns: list[str] = Field(default_factory=list)
    capability: EvidenceCapability | None = None
    input_fields: list[str] = Field(default_factory=list)
    entity_scope: list[str] = Field(default_factory=list)
    expected_evidence_types: list[str] = Field(default_factory=list)

    target_column: str | None = None
    target_status: TargetStatus = TargetStatus.UNCONFIRMED
    prediction_definition: str | None = None

    time_column: str | None = None
    validation_strategy: ValidationStrategy = ValidationStrategy.NONE

    exposure_column: str | None = None
    outcome_column: str | None = None
    confounder_columns: list[str] = Field(default_factory=list)

    required_evidence: list[str] = Field(default_factory=list)
    claim_permissions: list[ClaimPermission]
    answerability_note: str


class InsightObjective(StrictModel):
    objective_id: str
    question: str
    preferred_insight_types: list[InsightType] = Field(
        default_factory=list
    )
    relevant_task_ids: list[str] = Field(default_factory=list)
    priority: str = "main"


class EvidenceQuery(StrictModel):
    query_id: str
    task_id: str
    operation: EvidenceOperation
    capability: EvidenceCapability
    evidence_type: str

    semantic_label: str
    question: str
    table_name: str
    semantic_level: SemanticLevel

    value_binding_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Exact SemanticBinding.binding_id values only; never field paths "
            "or semantic labels."
        ),
    )
    entity_binding_id: str | None = Field(
        default=None,
        description=(
            "One exact SemanticBinding.binding_id for the entity being compared "
            "or ranked; never a field path."
        ),
    )
    group_binding_id: str | None = Field(
        default=None,
        description=(
            "One exact SemanticBinding.binding_id for an optional parent group; "
            "never a field path."
        ),
    )
    context_binding_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Exact SemanticBinding.binding_id values for optional context only; "
            "never field paths."
        ),
    )

    limit: int = Field(default=3, ge=1)
    descending: bool = True

    recommended_use: RecommendedUse = RecommendedUse.MAIN_FINDING
    user_relevance: float = Field(default=0.8, ge=0.0, le=1.0)
    salience: float = Field(default=0.8, ge=0.0, le=1.0)


class ExecutionPlan(StrictModel):
    objective: str
    tasks: list[InvestigationTask]
    route_order: list[AnalysisRoute]

    report_specification: ReportSpecification
    audit_mode: AuditMode

    insight_objectives: list[InsightObjective] = Field(
        default_factory=list
    )
    evidence_queries: list[EvidenceQuery] = Field(default_factory=list)

    available_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )
    selected_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    revision_limit: int = Field(ge=0, le=3)
    maximum_facts: int | None = Field(default=None, ge=1)

    frozen: bool = True
    rationale: str


class AnalyticalRecommendation(StrictModel):
    recommendation_id: str
    action: str
    recommendation_type: Literal[
        "data_cleaning",
        "methodological_check",
        "additional_analysis",
        "validation",
        "reporting",
    ]
    priority: Literal["high", "medium", "low"]
    justification: str
    affected_analyses: list[str] = Field(default_factory=list)
    consequence_if_ignored: str = (
        "The related analysis may be less reliable or harder to interpret."
    )
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)


class EvidenceItem(StrictModel):
    evidence_id: str
    route: AnalysisRoute
    task_ids: list[str]

    capability: EvidenceCapability = EvidenceCapability.DATASET_PROFILE
    evidence_type: str = "generic_finding"
    source_paths: list[str] = Field(default_factory=list)
    entity_scope: list[str] = Field(default_factory=list)
    semantic_level: SemanticLevel = SemanticLevel.DATASET
    semantic_binding_ids: list[str] = Field(default_factory=list)
    analytical_function: AnalyticalFunction | None = None
    query_id: str | None = None

    finding: str
    metrics: dict[str, Any] = Field(default_factory=dict)

    source_tables: list[str] = Field(default_factory=list)
    source_columns: list[str] = Field(default_factory=list)

    method: str
    validation_strategy: ValidationStrategy = ValidationStrategy.NONE

    practical_interpretation: str
    strength_label: str

    limitations: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)
    recommendations: list[AnalyticalRecommendation] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission]

    factual_confidence: float = Field(ge=0.0, le=1.0)
    methodological_strength: float = Field(ge=0.0, le=1.0)
    user_relevance: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    recommended_use: RecommendedUse
    eligible_for_writer: bool = True
    exclusion_reason: str | None = None


class EvidenceLedger(StrictModel):
    fingerprint: str
    items: list[EvidenceItem]
    execution_notes: list[str] = Field(default_factory=list)


class FactCandidate(StrictModel):
    candidate_id: str
    fact_summary: str

    evidence_ids: list[str]
    claim_permissions: list[ClaimPermission]

    allowed_interpretations: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)
    required_caveats: list[str] = Field(default_factory=list)

    factual_confidence: float = Field(ge=0.0, le=1.0)
    methodological_strength: float = Field(ge=0.0, le=1.0)
    user_relevance: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    recommended_use: RecommendedUse
    eligible_for_writer: bool = True


class FactCandidateSet(StrictModel):
    candidates: list[FactCandidate]
    synthesis_notes: list[str] = Field(default_factory=list)


class FactReview(StrictModel):
    candidate_id: str
    decision: ReviewDecision
    rationale: str
    required_caveats: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)


class VerificationResult(StrictModel):
    reviews: list[FactReview]
    overall_notes: list[str] = Field(default_factory=list)


class VerifiedFact(StrictModel):
    fact_id: str
    source_candidate_id: str

    verification_method: VerificationMethod = (
        VerificationMethod.LLM_VERIFIED
    )

    fact_summary: str
    evidence_ids: list[str]
    source_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    structured_values: dict[str, Any] = Field(default_factory=dict)
    entities: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission]
    allowed_interpretations: list[str] = Field(default_factory=list)
    prohibited_interpretations: list[str] = Field(default_factory=list)
    required_caveats: list[str] = Field(default_factory=list)

    factual_confidence: float = Field(ge=0.0, le=1.0)
    methodological_strength: float = Field(ge=0.0, le=1.0)
    user_relevance: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    recommended_use: RecommendedUse


class RejectedFact(StrictModel):
    source_candidate_id: str
    fact_summary: str
    reason: str


class FactLedger(StrictModel):
    writer_ready_facts: list[VerifiedFact]
    rejected_facts: list[RejectedFact] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)

    deterministically_recovered_fact_ids: list[str] = Field(
        default_factory=list
    )
    coverage_recovery_notes: list[str] = Field(
        default_factory=list
    )


class InsightCandidate(StrictModel):
    insight_id: str

    statement: str
    insight_type: InsightType
    interpretation_level: InterpretationLevel
    contribution: InsightContribution = (
        InsightContribution.ANALYTICAL_IMPLICATION
    )

    source_fact_ids: list[str] = Field(default_factory=list)
    source_evidence_ids: list[str] = Field(default_factory=list)

    why_it_matters: str | None = Field(
        default=None,
        description=(
            "For analytical reports, the evidence-bounded implication. For "
            "event and descriptive synthesis this may be omitted because the "
            "supported relationship itself can provide the reader value."
        ),
    )
    supporting_summary: str

    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    suitable_for_main_report: bool = True


class InsightCandidateSet(StrictModel):
    candidates: list[InsightCandidate] = Field(default_factory=list)
    synthesis_notes: list[str] = Field(default_factory=list)


class InsightVerificationRecord(StrictModel):
    insight_id: str
    status: InsightVerificationStatus

    verified_statement: str | None = None

    verified_source_fact_ids: list[str] = Field(default_factory=list)
    verified_source_evidence_ids: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    adds_bounded_synthesis: bool
    analytical_implication_supported: bool
    contains_hypothesis: bool

    limitations: list[str] = Field(default_factory=list)
    verification_notes: list[str] = Field(default_factory=list)


class InsightVerificationResult(StrictModel):
    records: list[InsightVerificationRecord] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)


class VerifiedInsight(StrictModel):
    insight_id: str

    statement: str
    insight_type: InsightType
    interpretation_level: InterpretationLevel
    contribution: InsightContribution = (
        InsightContribution.ANALYTICAL_IMPLICATION
    )

    source_fact_ids: list[str] = Field(default_factory=list)
    source_evidence_ids: list[str] = Field(default_factory=list)
    source_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    why_it_matters: str | None = Field(
        default=None,
        description=(
            "The verified analytical implication when the contribution "
            "requires one; event and descriptive synthesis may omit it."
        ),
    )
    limitations: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)

    verification_status: InsightVerificationStatus


class InsightRejection(StrictModel):
    insight_id: str
    candidate: InsightCandidate
    reasons: list[str] = Field(default_factory=list)


class InsightVerificationFailure(StrictModel):
    insight_id: str
    candidate: InsightCandidate
    reasons: list[str] = Field(default_factory=list)


class InsightLedger(StrictModel):
    verified_insights: list[VerifiedInsight] = Field(default_factory=list)
    hypothesis_only_insights: list[VerifiedInsight] = Field(
        default_factory=list
    )
    rejected_insights: list[InsightRejection] = Field(default_factory=list)
    unverified_insights: list[InsightVerificationFailure] = Field(
        default_factory=list
    )
    verifier_notes: list[str] = Field(default_factory=list)
    synthesis_enabled: bool = True
    fallback_reason: str | None = None


class WriterEvidencePack(StrictModel):
    user_request: str
    report_specification: ReportSpecification

    dataset_understanding: DataUnderstanding
    input_structure: InputStructureProfile | None = None
    available_capabilities: list[EvidenceCapability] = Field(
        default_factory=list
    )

    priority_facts: list[VerifiedFact]
    supporting_facts: list[VerifiedFact]
    limitation_facts: list[VerifiedFact]

    evidence_ledger: EvidenceLedger

    insight_ledger: InsightLedger = Field(default_factory=InsightLedger)
    priority_verified_insights: list[VerifiedInsight] = Field(
        default_factory=list
    )
    supporting_verified_insights: list[VerifiedInsight] = Field(
        default_factory=list
    )

    analytical_recommendations: list[AnalyticalRecommendation] = Field(
        default_factory=list
    )
    reader_facing_limitations: list[str] = Field(default_factory=list)
    internal_prohibited_interpretations: list[str] = Field(default_factory=list)


class ProfileSupportRecord(StrictModel):
    support_id: str
    fact_kind: str

    table_name: str
    column_name: str | None = None

    statement: str
    structured_values: dict[str, Any] = Field(default_factory=dict)
    entities: list[str] = Field(default_factory=list)

    claim_permissions: list[ClaimPermission] = Field(
        default_factory=lambda: [
            ClaimPermission.DESCRIPTIVE
        ]
    )

    provenance: str


class ReportComponentAssessment(StrictModel):
    component: ReportComponent
    covered: bool
    supporting_fact_ids: list[str] = Field(default_factory=list)
    explanation: str


class SentenceSupport(StrictModel):
    sentence_id: str
    sentence_text: str

    fact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    profile_support_ids: list[str] = Field(default_factory=list)
    insight_ids: list[str] = Field(default_factory=list)

    interpretation_level: InterpretationLevel = InterpretationLevel.FINDING

    support_type: SupportType


class WriterSentenceDraft(StrictModel):
    text: str = Field(min_length=1)

    fact_ids: list[str] = Field(default_factory=list)

    insight_ids: list[str] = Field(default_factory=list)
    interpretation_level: InterpretationLevel = InterpretationLevel.FINDING

    support_type: SupportType


class WriterSectionDraft(StrictModel):
    heading: str = Field(min_length=1)

    sentences: list[WriterSentenceDraft] = Field(default_factory=list)


class WriterAgentDraft(StrictModel):
    title: str = Field(min_length=1)
    title_fact_ids: list[str] = Field(default_factory=list)

    sections: list[WriterSectionDraft] = Field(default_factory=list)

    writer_notes: list[str] = Field(default_factory=list)


class WriterOutput(StrictModel):
    title: str
    markdown: str
    title_fact_ids: list[str] = Field(default_factory=list)

    sentence_support: list[SentenceSupport]

    selected_fact_ids: list[str] = Field(default_factory=list)
    omitted_fact_ids: list[str] = Field(default_factory=list)

    writer_notes: list[str] = Field(default_factory=list)

    writer_mode: Literal[
        "llm_writer",
        "deterministic_fallback",
        "auditor_repaired",
    ] = "llm_writer"

    eligible_for_primary_evaluation: bool = True
    quality_revision_round: int = Field(default=0, ge=0, le=1)
    quality_revision_summary: str | None = None


class ExternalFact(StrictModel):
    fact_id: str
    fact_text: str
    entities: list[str] = Field(default_factory=list)
    numbers: list[float] = Field(default_factory=list)
    validity: str = "current"


class ExternalTruthSource(StrictModel):
    source_id: str
    source_name: str
    source_type: str
    trust_level: str

    source_uri: str | None = None
    retrieved_at: str | None = None

    scope: list[str] = Field(default_factory=list)
    facts: list[ExternalFact] = Field(default_factory=list)


class AuditAnnotation(StrictModel):
    annotation_id: str

    sentence: str
    text_span: str

    error_type: ErrorType
    subtype: str
    severity: Severity

    explanation: str
    correction_goal: str

    fact_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    external_fact_ids: list[str] = Field(default_factory=list)
    profile_support_ids: list[str] = Field(default_factory=list)
    insight_ids: list[str] = Field(default_factory=list)

    confidence: float = Field(ge=0.0, le=1.0)


class RepairCandidate(StrictModel):
    repair_id: str
    replacement_text: str

    strategy: RepairStrategy

    supporting_fact_ids: list[str] = Field(default_factory=list)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    supporting_insight_ids: list[str] = Field(default_factory=list)

    factual_support_score: float = Field(ge=0.0, le=1.0)
    meaning_preservation_score: float = Field(ge=0.0, le=1.0)
    readability_score: float = Field(ge=0.0, le=1.0)
    residual_hallucination_risk: float = Field(ge=0.0, le=1.0)


class SentenceRepair(StrictModel):
    sentence_id: str
    original_sentence: str
    annotation_ids: list[str]

    candidates: list[RepairCandidate]
    preferred_repair_id: str | None = None
    selection_reason: str


class ReportQualityAssessment(StrictModel):
    status: QualityStatus

    request_responsiveness: float = Field(ge=0.0, le=1.0)
    finding_selection: float = Field(ge=0.0, le=1.0)
    coherence: float = Field(ge=0.0, le=1.0)
    concision: float = Field(ge=0.0, le=1.0)
    caveat_integration: float = Field(ge=0.0, le=1.0)
    data_science_interpretation: float = Field(ge=0.0, le=1.0)

    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class AuditRepairProposal(StrictModel):
    annotations: list[AuditAnnotation] = Field(default_factory=list)
    repairs: list[SentenceRepair] = Field(default_factory=list)

    recommended_decision: AuditDecision
    residual_risk: str

    quality_assessment: ReportQualityAssessment
    revision_instructions: list[str] = Field(default_factory=list)


class ReportPatch(StrictModel):
    sentence_id: str
    original_text: str
    replacement_text: str
    operation: Literal["replace", "delete"]
    selected_repair_id: str


class SupportMapPatch(StrictModel):
    sentence_id: str
    sentence_text: str
    added_profile_support_ids: list[str]
    reason: str


class AuditReport(StrictModel):
    mode: AuditMode
    decision: AuditDecision
    release_status: ReleaseStatus

    annotations: list[AuditAnnotation] = Field(default_factory=list)
    applied_patches: list[ReportPatch] = Field(default_factory=list)
    support_map_patches: list[SupportMapPatch] = Field(default_factory=list)

    factual_sentence_count: int
    supported_sentence_count: int
    support_rate: float = Field(ge=0.0, le=1.0)

    residual_risk: str
    revision_instructions: list[str] = Field(default_factory=list)
    quality_assessment: ReportQualityAssessment
    component_assessments: list[ReportComponentAssessment] = Field(default_factory=list)
    methodological_warnings: list[str] = Field(default_factory=list)

    revision_round: int = 0


class RunManifest(StrictModel):
    run_id: str
    created_at: str

    input_paths: list[str]
    request: str
    fingerprint: str

    use_llm: bool
    audit_mode: AuditMode

    models: dict[str, str]
    input_representation_status: InputRepresentationStatus = (
        InputRepresentationStatus.VALID
    )
    report_genre: ReportGenre = ReportGenre.DATA_SCIENCE_REPORT


class PipelineResult(StrictModel):
    run_id: str

    profile: DataProfile
    input_structure: InputStructureProfile | None = None
    structural_catalog: list[StructuralField] = Field(default_factory=list)
    evaluation_field_policy: EvaluationFieldPolicy = Field(
        default_factory=EvaluationFieldPolicy
    )
    understanding: DataUnderstanding
    execution_plan: ExecutionPlan

    evidence_ledger: EvidenceLedger
    fact_candidates: FactCandidateSet
    verification: VerificationResult
    fact_ledger: FactLedger
    writer_evidence_pack: WriterEvidencePack

    raw_writer_output: WriterOutput
    quality_revised_writer_output: WriterOutput | None = None
    final_writer_output: WriterOutput

    initial_audit: AuditReport
    final_audit: AuditReport

    repair_rounds_used: int
    release_status: ReleaseStatus
    approved_for_release: bool
    primary_evaluation_eligible: bool = True
    primary_evaluation_reason: str | None = None
    genre_quality_assessment: GenreQualityAssessment | None = None

    insight_ledger: InsightLedger = Field(default_factory=InsightLedger)


# Compatibility aliases for notebooks using the original names.
ClaimCandidate = FactCandidate
ClaimCandidateSet = FactCandidateSet
ClaimReview = FactReview
VerifiedClaim = VerifiedFact
RejectedClaim = RejectedFact
ClaimLedger = FactLedger
ReportDraft = WriterOutput
