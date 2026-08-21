from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


def _string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list | tuple | set):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _string_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list | tuple | set):
        return "; ".join(str(item) for item in value if item is not None)
    return str(value)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    raw = str(value).strip()
    if not raw or raw.casefold() in {"none", "null", "all", "n/a", "na"}:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


class UsageSummary(StrictModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AgentCallTrace(StrictModel):
    stage: str
    model: str
    elapsed_seconds: float
    usage: UsageSummary = Field(default_factory=UsageSummary)


class SourceInterpretation(StrictModel):
    task_understanding: str
    source_units: str
    important_entities: list[str] = Field(default_factory=list)
    important_fields: list[str] = Field(default_factory=list)
    allowed_claim_types: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    @field_validator("task_understanding", "source_units", mode="before")
    @classmethod
    def normalise_text(cls, value: object) -> str:
        return _string_value(value)

    @field_validator(
        "important_entities",
        "important_fields",
        "allowed_claim_types",
        "risks",
        mode="before",
    )
    @classmethod
    def normalise_lists(cls, value: object) -> list[str]:
        return _string_list(value)


class LLMClaim(StrictModel):
    claim_id: str
    claim: str
    claim_type: str = "source_fact"
    source_refs: list[str] = Field(default_factory=list)
    copied_values: list[str] = Field(default_factory=list)
    calculation_or_reasoning: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator("calculation_or_reasoning", mode="before")
    @classmethod
    def normalise_reasoning(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value)

    @field_validator("source_refs", "copied_values", mode="before")
    @classmethod
    def normalise_lists(cls, value: object) -> list[str]:
        return _string_list(value)

    @field_validator("confidence", mode="before")
    @classmethod
    def normalise_confidence(cls, value: object) -> float:
        if value is None:
            return 0.5
        if isinstance(value, int | float):
            raw = float(value)
            return raw / 100.0 if raw > 1.0 else raw
        label = str(value).strip().casefold()
        labels = {
            "very high": 0.95,
            "high": 0.9,
            "medium": 0.65,
            "moderate": 0.65,
            "low": 0.35,
            "very low": 0.2,
        }
        if label in labels:
            return labels[label]
        try:
            raw = float(label.rstrip("%"))
        except ValueError:
            return 0.5
        return raw / 100.0 if raw > 1.0 else raw


class ClaimSet(StrictModel):
    claims: list[LLMClaim] = Field(default_factory=list)
    analysis_notes: list[str] = Field(default_factory=list)

    @field_validator("analysis_notes", mode="before")
    @classmethod
    def normalise_notes(cls, value: object) -> list[str]:
        return _string_list(value)


class ClaimReview(StrictModel):
    claim_id: str
    status: Literal[
        "supported",
        "unsupported",
        "overstated",
        "wrong_number",
        "wrong_entity",
        "wrong_relation",
        "needs_caveat",
    ]
    reason: str
    corrected_claim: str | None = None


class ClaimCritique(StrictModel):
    reviews: list[ClaimReview] = Field(default_factory=list)
    global_warnings: list[str] = Field(default_factory=list)

    @field_validator("global_warnings", mode="before")
    @classmethod
    def normalise_warnings(cls, value: object) -> list[str]:
        return _string_list(value)


class RejectedClaim(StrictModel):
    claim_id: str
    claim: str
    reason: str


class AdjudicatedClaims(StrictModel):
    accepted_claims: list[LLMClaim] = Field(default_factory=list)
    rejected_claims: list[RejectedClaim] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("warnings", mode="before")
    @classmethod
    def normalise_warnings(cls, value: object) -> list[str]:
        return _string_list(value)


class WriterSentence(StrictModel):
    text: str
    claim_ids: list[str] = Field(default_factory=list)

    @field_validator("claim_ids", mode="before")
    @classmethod
    def normalise_claim_ids(cls, value: object) -> list[str]:
        return _string_list(value)


class WriterDraft(StrictModel):
    title: str | None = None
    sentences: list[WriterSentence] = Field(default_factory=list)


class AuditFinding(StrictModel):
    sentence_index: int | None = None
    severity: Literal["minor", "major", "critical"]
    issue: str
    suggested_action: Literal["delete", "weaken", "replace"]

    @field_validator("sentence_index", mode="before")
    @classmethod
    def normalise_sentence_index(cls, value: object) -> int | None:
        return _optional_int(value)

    @field_validator("severity", mode="before")
    @classmethod
    def normalise_severity(cls, value: object) -> str:
        raw = _string_value(value).strip().casefold()
        if raw in {"blocking", "block", "blocked", "fatal", "severe", "critical"}:
            return "critical"
        if raw in {"major", "high", "serious"}:
            return "major"
        return "minor"

    @field_validator("suggested_action", mode="before")
    @classmethod
    def normalise_suggested_action(cls, value: object) -> str:
        raw = _string_value(value).strip().casefold()
        if raw in {"delete", "remove", "drop"} or any(
            phrase in raw for phrase in ("delete", "remove", "drop")
        ):
            return "delete"
        if raw in {"weaken", "qualify", "caveat"} or any(
            phrase in raw for phrase in ("weaken", "qualify", "caveat")
        ):
            return "weaken"
        return "replace"


class OutputAudit(StrictModel):
    decision: Literal["pass", "revise"]
    support_rate: float = Field(ge=0.0, le=1.0)
    findings: list[AuditFinding] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @field_validator("decision", mode="before")
    @classmethod
    def normalise_decision(cls, value: object) -> str:
        raw = _string_value(value).strip().casefold()
        return "pass" if raw == "pass" else "revise"

    @field_validator("notes", mode="before")
    @classmethod
    def normalise_notes(cls, value: object) -> list[str]:
        return _string_list(value)


class RepairedDraft(StrictModel):
    sentences: list[WriterSentence] = Field(default_factory=list)
    repair_notes: list[str] = Field(default_factory=list)

    @field_validator("repair_notes", mode="before")
    @classmethod
    def normalise_repair_notes(cls, value: object) -> list[str]:
        return _string_list(value)


class LLMOnlyResult(StrictModel):
    generated_text: str
    interpretation: SourceInterpretation
    candidate_claims: ClaimSet
    critique: ClaimCritique
    adjudicated_claims: AdjudicatedClaims
    writer_draft: WriterDraft
    final_audit: OutputAudit
    repaired_draft: RepairedDraft | None = None
    traces: list[AgentCallTrace] = Field(default_factory=list)
    artifact_path: str | None = None
