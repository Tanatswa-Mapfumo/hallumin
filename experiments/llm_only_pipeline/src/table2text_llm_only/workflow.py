from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from table2text.evaluation.models import BenchmarkExample, OutputMode, TaskFamily

from .client import LLMOnlyClient, LLMOnlyClientConfig
from .schemas import (
    AdjudicatedClaims,
    ClaimCritique,
    ClaimSet,
    LLMClaim,
    LLMOnlyResult,
    OutputAudit,
    RepairedDraft,
    RejectedClaim,
    SourceInterpretation,
    WriterSentence,
    WriterDraft,
)


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)


def _truncate(text: str, max_characters: int) -> str:
    if len(text) <= max_characters:
        return text
    return text[:max_characters] + "\n\n[Source truncated by LLM-only configuration.]"


def _final_text(draft: WriterDraft | RepairedDraft) -> str:
    return " ".join(
        sentence.text.strip()
        for sentence in draft.sentences
        if sentence.text.strip()
    ).strip()


def _claim_payload(claims: list[LLMClaim]) -> list[dict[str, Any]]:
    return [claim.model_dump(mode="json") for claim in claims]


SYSTEM_BASE = (
    "You are part of an LLM-only multi-agent Table2Text experiment. "
    "Use only the supplied source data and intermediate artifacts. "
    "Human references, targets, summaries and evaluation answers are held out "
    "and are not available to you. Return only valid JSON matching the requested "
    "shape. Do not include markdown fences. Keep string values concise and keep "
    "arrays short unless the requested schema explicitly asks for more."
)


class LLMOnlyWorkflow:
    def __init__(
        self,
        *,
        client: LLMOnlyClient,
        max_source_characters: int = 100_000,
        max_source_payload_characters: int = 5_000,
        max_claims: int = 16,
        repair_rounds: int = 1,
    ):
        self.client = client
        self.max_source_characters = max_source_characters
        self.max_source_payload_characters = max_source_payload_characters
        self.max_claims = max_claims
        self.repair_rounds = repair_rounds

    @classmethod
    def from_settings(cls, values: dict[str, Any]) -> "LLMOnlyWorkflow":
        config = LLMOnlyClientConfig.from_mapping(values)
        return cls(
            client=LLMOnlyClient(config),
            max_source_characters=int(
                values.get("llm_only_max_source_characters", 100_000)
            ),
            max_source_payload_characters=int(
                values.get("llm_only_max_source_payload_characters", 5_000)
            ),
            max_claims=int(values.get("llm_only_max_claims", 16)),
            repair_rounds=int(values.get("llm_only_repair_rounds", 1)),
        )

    def _source_packet(self, example: BenchmarkExample) -> dict[str, Any]:
        source_text = example.source_text.strip() or _pretty_json(example.source_payload)
        source_payload = self._source_payload_for_packet(
            example.source_payload,
            source_text,
        )
        return {
            "dataset_id": example.dataset_id,
            "example_id": example.example_id,
            "task_family": example.task_family.value,
            "output_mode": example.output_mode.value,
            "language": example.language,
            "request": example.request,
            "source_text": _truncate(source_text, self.max_source_characters),
            "source_payload": source_payload,
            "parent_table": example.parent_table,
            "metadata": example.metadata,
        }

    def _source_payload_for_packet(self, source_payload: Any, source_text: str) -> Any:
        payload_text = _compact_json(source_payload)
        if len(payload_text) <= self.max_source_payload_characters:
            return source_payload
        if source_text.strip():
            return {
                "omitted_from_prompt": True,
                "reason": (
                    "source_payload was omitted to avoid duplicating the full "
                    "source_text in every LLM-only agent prompt"
                ),
                "payload_characters": len(payload_text),
            }
        return {
            "truncated_payload_json": payload_text[
                : self.max_source_payload_characters
            ],
            "payload_characters": len(payload_text),
        }

    def interpret_source(self, packet: dict[str, Any]) -> tuple[SourceInterpretation, Any]:
        payload, trace = self.client.json_call(
            stage="source_interpreter",
            system=SYSTEM_BASE
            + " You are the Source Interpreter Agent. Describe what the source "
            "contains, what claims are allowed, and what risks could cause "
            "hallucination. Do not produce final report claims. This is a compact "
            "orientation artifact, not a field-by-field dump.",
            user=(
                "Return JSON with keys: task_understanding, source_units, "
                "important_entities, important_fields, allowed_claim_types, risks. "
                "Limits: important_entities <= 12, important_fields <= 20, "
                "allowed_claim_types <= 10, risks <= 8. Each string should be "
                "under 160 characters.\n\n"
                "Source packet:\n"
                + _pretty_json(packet)
            ),
        )
        return SourceInterpretation.model_validate(payload), trace

    def analyse_claims(
        self,
        packet: dict[str, Any],
        interpretation: SourceInterpretation,
    ) -> tuple[ClaimSet, Any]:
        payload, trace = self.client.json_call(
            stage="llm_analysis",
            system=SYSTEM_BASE
            + " You are the LLM Analysis Agent. Produce candidate claims directly "
            "from the source. Every claim must cite source_refs and copied_values. "
            "If arithmetic or comparison is needed, do it yourself and show it in "
            "calculation_or_reasoning. Keep each claim concise.",
            user=(
                "Return JSON with keys: claims, analysis_notes. "
                "claims must contain objects with claim_id, claim, claim_type, "
                "source_refs, copied_values, calculation_or_reasoning, confidence. "
                "source_refs and copied_values must be flat arrays of short "
                "strings, never nested objects. Each claim should be one sentence. "
                "confidence must be a number from 0.0 to 1.0, never a word such "
                "as high or low. If no calculation is needed, set "
                "calculation_or_reasoning to a short source-grounding note. "
                f"Return at most {self.max_claims} claims. Prefer claims needed "
                "for the requested output. Keep analysis_notes <= 5. Do not "
                "return an empty claims list when the source contains visible "
                "game, team, player, score, or table values.\n\n"
                + self._claim_slot_instruction(packet)
                + "\n\n"
                "Task and source:\n"
                + _pretty_json(packet)
                + "\n\nSource interpretation:\n"
                + interpretation.model_dump_json(indent=2)
            ),
        )
        return ClaimSet.model_validate(payload), trace

    def recover_claims(
        self,
        packet: dict[str, Any],
        interpretation: SourceInterpretation,
    ) -> tuple[ClaimSet, Any]:
        payload, trace = self.client.json_call(
            stage="llm_analysis_recovery",
            system=SYSTEM_BASE
            + " You are the Recovery Claim Analyst Agent. A previous analyst "
            "returned zero claims from a non-empty source. Build a conservative "
            "claim ledger from directly visible source values. This is still "
            "LLM-only: do not use outside knowledge, references, or hidden "
            "answers. Prefer simple copied facts over clever narrative.",
            user=(
                "Return JSON with keys: claims, analysis_notes. claims must "
                "contain objects with claim_id, claim, claim_type, source_refs, "
                "copied_values, calculation_or_reasoning, confidence. "
                "source_refs and copied_values must be flat arrays of short "
                "strings, never nested objects. Each claim should be one sentence. "
                "When the source contains game/team/player fields, return at "
                f"least 8 and at most {self.max_claims} claims. Only return zero "
                "claims if the source is genuinely empty or unreadable.\n\n"
                "For structured event sources, prefer directly checkable facts "
                "when present: outcome, context, participant records, period or "
                "stage progression, leading performances, participant totals, "
                "contrasts, and subsequent-event context. Adapt these categories "
                "to the source vocabulary instead of assuming a domain. "
                "Avoid unsupported play-by-play runs or momentum claims.\n\n"
                + self._claim_slot_instruction(packet)
                + "\n\nTask and source:\n"
                + _pretty_json(packet)
                + "\n\nSource interpretation:\n"
                + interpretation.model_dump_json(indent=2)
            ),
        )
        return ClaimSet.model_validate(payload), trace

    def critique_claims(
        self,
        packet: dict[str, Any],
        claims: ClaimSet,
    ) -> tuple[ClaimCritique, Any]:
        payload, trace = self.client.json_call(
            stage="claim_critic",
            system=SYSTEM_BASE
            + " You are the Claim Critic Agent. Independently check each claim "
            "against the source. Be stricter with numbers, entities, highlighted "
            "cells, triples, attributes, chronology and causal language.",
            user=(
                "Return JSON with keys: reviews, global_warnings. Each review "
                "must contain claim_id, status, reason, corrected_claim. Use status "
                "supported, unsupported, overstated, wrong_number, wrong_entity, "
                "wrong_relation, or needs_caveat. Keep each reason to one concise "
                "sentence.\n\nSource packet:\n"
                + _pretty_json(packet)
                + "\n\nCandidate claims:\n"
                + claims.model_dump_json(indent=2)
            ),
        )
        return ClaimCritique.model_validate(payload), trace

    def adjudicate_claims(
        self,
        packet: dict[str, Any],
        claims: ClaimSet,
        critique: ClaimCritique,
    ) -> tuple[AdjudicatedClaims, Any]:
        payload, trace = self.client.json_call(
            stage="claim_adjudicator",
            system=SYSTEM_BASE
            + " You are the Claim Adjudicator Agent. Create the final accepted "
            "claim ledger. Accept only claims that are supported or can be made "
            "supported by a conservative corrected_claim. Reject uncertain claims, "
            "but do not reject every claim from a non-empty source if some simple "
            "copied-value claims are visibly supported. If critique reviews are "
            "missing or empty, conservatively accept high-confidence claims with "
            "source_refs and copied_values instead of returning an empty ledger.",
            user=(
                "Return JSON with keys: accepted_claims, rejected_claims, warnings. "
                "accepted_claims use the original claim schema. rejected_claims "
                "contain claim_id, claim, reason. Every accepted claim must keep "
                "non-empty source_refs and copied_values; reject claims that lack "
                "evidence even if they look plausible. Do not invent new claims. "
                "Keep warnings <= 8.\n\n"
                "Task and source:\n"
                + _pretty_json(packet)
                + "\n\nCandidate claims:\n"
                + claims.model_dump_json(indent=2)
                + "\n\nCritique:\n"
                + critique.model_dump_json(indent=2)
            ),
        )
        return AdjudicatedClaims.model_validate(payload), trace

    def enforce_accepted_claim_evidence(
        self,
        adjudicated: AdjudicatedClaims,
    ) -> AdjudicatedClaims:
        accepted: list[LLMClaim] = []
        rejected = list(adjudicated.rejected_claims)
        warnings = list(adjudicated.warnings)

        for claim in adjudicated.accepted_claims:
            if claim.source_refs and claim.copied_values:
                accepted.append(claim)
                continue
            rejected.append(
                RejectedClaim(
                    claim_id=claim.claim_id,
                    claim=claim.claim,
                    reason=(
                        "Accepted claim removed because it lacked source_refs "
                        "or copied_values."
                    ),
                )
            )

        if len(accepted) != len(adjudicated.accepted_claims):
            warnings.append(
                "Accepted claims without explicit source_refs and copied_values "
                "were moved to rejected_claims."
            )

        return AdjudicatedClaims(
            accepted_claims=accepted,
            rejected_claims=rejected,
            warnings=warnings,
        )

    def fallback_adjudication(
        self,
        claims: ClaimSet,
        critique: ClaimCritique,
    ) -> AdjudicatedClaims:
        accepted: list[LLMClaim] = []
        rejected: list[RejectedClaim] = []
        review_by_id = {review.claim_id: review for review in critique.reviews}

        for claim in claims.claims:
            review = review_by_id.get(claim.claim_id)
            has_evidence = bool(claim.source_refs and claim.copied_values)
            supported_by_review = (
                review is not None
                and review.status in {"supported", "needs_caveat"}
                and has_evidence
            )
            safe_without_review = review is None and has_evidence and claim.confidence >= 0.8

            if supported_by_review or safe_without_review:
                accepted.append(claim)
            else:
                rejected.append(
                    RejectedClaim(
                        claim_id=claim.claim_id,
                        claim=claim.claim,
                        reason=(
                            "Fallback adjudication did not find enough LLM "
                            "evidence to accept this claim."
                        ),
                    )
                )

        if not accepted:
            candidates = [
                claim
                for claim in claims.claims
                if claim.source_refs and claim.copied_values
            ]
            if candidates:
                best = max(candidates, key=lambda claim: claim.confidence)
                accepted.append(best)
                rejected = [
                    item for item in rejected if item.claim_id != best.claim_id
                ]

        return AdjudicatedClaims(
            accepted_claims=accepted,
            rejected_claims=rejected,
            warnings=[
                "Fallback adjudication used cited candidate claims because the "
                "adjudicator returned an empty ledger."
            ],
        )

    def write_draft(
        self,
        packet: dict[str, Any],
        adjudicated: AdjudicatedClaims,
    ) -> tuple[WriterDraft, Any]:
        payload, trace = self.client.json_call(
            stage="writer",
            system=SYSTEM_BASE
            + " You are the Writer Agent. Write only from accepted_claims. "
            "You do not have permission to add facts from the raw source. "
            "Every sentence must list the claim_ids that support it.",
            user=(
                "Return JSON with keys: title, sentences. sentences must contain "
                "text and claim_ids. The final style must match the task family, "
                "output mode and language. "
                + self._style_instruction(packet)
                + "\n\nTask contract:\n"
                + _pretty_json(
                    {
                        key: packet[key]
                        for key in (
                            "dataset_id",
                            "task_family",
                            "output_mode",
                            "language",
                            "request",
                        )
                    }
                )
                + "\n\nAccepted claims:\n"
                + _pretty_json(_claim_payload(adjudicated.accepted_claims))
                + "\n\nWarnings:\n"
                + _pretty_json(adjudicated.warnings)
            ),
        )
        return WriterDraft.model_validate(payload), trace

    def fallback_draft(
        self,
        packet: dict[str, Any],
        adjudicated: AdjudicatedClaims,
    ) -> WriterDraft:
        sentences = [
            WriterSentence(text=claim.claim.rstrip(".") + ".", claim_ids=[claim.claim_id])
            for claim in adjudicated.accepted_claims[:8]
            if claim.claim.strip()
        ]
        task_family = TaskFamily(packet["task_family"])
        title = (
            "Event Report"
            if task_family
            in {TaskFamily.EVENT_REPORT, TaskFamily.CROSS_LINGUAL_EVENT_REPORT}
            else None
        )
        return WriterDraft(title=title, sentences=sentences)

    def audit_output(
        self,
        packet: dict[str, Any],
        adjudicated: AdjudicatedClaims,
        draft: WriterDraft | RepairedDraft,
    ) -> tuple[OutputAudit, Any]:
        payload, trace = self.client.json_call(
            stage="output_auditor",
            system=SYSTEM_BASE
            + " You are the Output Auditor Agent. Check whether the draft uses "
            "only accepted claims and whether each sentence is properly supported. "
            "Also judge whether the draft covers the minimum required task slots. "
            "This system never blocks output; severe factual problems should be "
            "reported as revise so the repair agent can produce the safest "
            "supported version.",
            user=(
                "Return JSON with keys: decision, support_rate, findings, notes. "
                "findings contain sentence_index, severity, issue, suggested_action. "
                "Use severity minor, major, or critical; critical means high "
                "hallucination risk that should be repaired, not blocked. "
                "Decision must be pass or revise, never block. For unsupported "
                "wording or missing but available coverage, use decision revise "
                "with suggested_action replace, delete, or weaken.\n\n"
                "Required coverage:\n"
                + self._coverage_instruction(packet)
                + "\n\nTask and source:\n"
                + _pretty_json(packet)
                + "\n\nAccepted claims:\n"
                + _pretty_json(_claim_payload(adjudicated.accepted_claims))
                + "\n\nDraft:\n"
                + draft.model_dump_json(indent=2)
            ),
        )
        return OutputAudit.model_validate(payload), trace

    def repair_output(
        self,
        packet: dict[str, Any],
        adjudicated: AdjudicatedClaims,
        draft: WriterDraft | RepairedDraft,
        audit: OutputAudit,
    ) -> tuple[RepairedDraft, Any]:
        payload, trace = self.client.json_call(
            stage="repair",
            system=SYSTEM_BASE
            + " You are the Repair Agent. Only delete, weaken, or replace text "
            "using accepted claims. Do not add new claims from the raw source.",
            user=(
                "Return JSON with keys: sentences, repair_notes. sentences contain "
                "text and claim_ids. You may add a sentence only when it is fully "
                "supported by accepted claim_ids. Keep the output task-appropriate.\n\n"
                "Required coverage:\n"
                + self._coverage_instruction(packet)
                + "\n\n"
                "Task contract:\n"
                + _pretty_json(
                    {
                        key: packet[key]
                        for key in (
                            "dataset_id",
                            "task_family",
                            "output_mode",
                            "language",
                            "request",
                        )
                    }
                )
                + "\n\nAccepted claims:\n"
                + _pretty_json(_claim_payload(adjudicated.accepted_claims))
                + "\n\nCurrent draft:\n"
                + draft.model_dump_json(indent=2)
                + "\n\nAudit:\n"
                + audit.model_dump_json(indent=2)
            ),
        )
        return RepairedDraft.model_validate(payload), trace

    def run(self, example: BenchmarkExample) -> LLMOnlyResult:
        packet = self._source_packet(example)
        traces = []

        interpretation, trace = self.interpret_source(packet)
        traces.append(trace)
        claims, trace = self.analyse_claims(packet, interpretation)
        traces.append(trace)
        if not claims.claims and self._has_visible_source_data(packet):
            claims, trace = self.recover_claims(packet, interpretation)
            traces.append(trace)
        critique, trace = self.critique_claims(packet, claims)
        traces.append(trace)
        adjudicated, trace = self.adjudicate_claims(packet, claims, critique)
        traces.append(trace)
        if (
            claims.claims
            and not adjudicated.accepted_claims
            and not adjudicated.rejected_claims
        ):
            adjudicated = self.fallback_adjudication(claims, critique)
        adjudicated = self.enforce_accepted_claim_evidence(adjudicated)
        draft, trace = self.write_draft(packet, adjudicated)
        traces.append(trace)
        if adjudicated.accepted_claims and not draft.sentences:
            draft = self.fallback_draft(packet, adjudicated)
        audit, trace = self.audit_output(packet, adjudicated, draft)
        traces.append(trace)

        repaired: RepairedDraft | None = None
        final_text = _final_text(draft)
        if audit.decision == "revise" and self.repair_rounds > 0:
            repaired, trace = self.repair_output(packet, adjudicated, draft, audit)
            traces.append(trace)
            audit, trace = self.audit_output(packet, adjudicated, repaired)
            traces.append(trace)
            final_text = _final_text(repaired)

        return LLMOnlyResult(
            generated_text=final_text,
            interpretation=interpretation,
            candidate_claims=claims,
            critique=critique,
            adjudicated_claims=adjudicated,
            writer_draft=draft,
            final_audit=audit,
            repaired_draft=repaired,
            traces=traces,
        )

    def _style_instruction(self, packet: dict[str, Any]) -> str:
        task_family = TaskFamily(packet["task_family"])
        output_mode = OutputMode(packet["output_mode"])
        if output_mode == OutputMode.ONE_SENTENCE:
            return "Write exactly one sentence."
        if output_mode in {OutputMode.SHORT_TEXT, OutputMode.DIRECT_ANSWER}:
            return "Write one or two concise sentences with no heading."
        if task_family in {TaskFamily.EVENT_REPORT, TaskFamily.CROSS_LINGUAL_EVENT_REPORT}:
            return (
                "Write a coherent event recap in 2 to 4 paragraphs. Lead with "
                "the result, then cover score progression, leading performances "
                "and team contrasts when those accepted claims are available."
            )
        return "Write a concise factual report."

    def _has_visible_source_data(self, packet: dict[str, Any]) -> bool:
        source_text = str(packet.get("source_text") or "").strip()
        if source_text and source_text not in {"{}", "[]"}:
            return True
        source_payload = packet.get("source_payload")
        return bool(source_payload)

    def _claim_slot_instruction(self, packet: dict[str, Any]) -> str:
        task_family = TaskFamily(packet["task_family"])
        if task_family not in {
            TaskFamily.EVENT_REPORT,
            TaskFamily.CROSS_LINGUAL_EVENT_REPORT,
        }:
            return (
                "Select claims that fully satisfy the requested task while "
                "avoiding unrelated details."
            )
        return (
            "For this event-report task, cover these claim slots when supported "
            "by the source: event_result, event_context, record_context, "
            "period_score_progression, turning_period_or_key_run, lead_scorer, "
            "secondary_scorers, top_rebounders_or_double_doubles, assist_leaders, "
            "shooting_comparison, three_point_comparison, free_throw_comparison, "
            "rebounding_comparison, defensive_stats, bench_or_supporting "
            "contribution, and scope_note. It is better to include a concise "
            "supported claim for each major slot than to over-focus on only "
            "the final score and top scorer."
        )

    def _coverage_instruction(self, packet: dict[str, Any]) -> str:
        task_family = TaskFamily(packet["task_family"])
        if task_family not in {
            TaskFamily.EVENT_REPORT,
            TaskFamily.CROSS_LINGUAL_EVENT_REPORT,
        }:
            return "Cover the requested task exactly; do not require event-report sections."
        return (
            "A passable event recap should include the supported result, event "
            "context, score progression or period-by-period development, leading "
            "performances, and at least one team-level contrast. If accepted "
            "claims contain these facts but the draft omits them, return revise."
        )


def artifact_id(example: BenchmarkExample, variant_id: str, repetition: int, seed: int) -> str:
    raw = "::".join(
        [
            example.dataset_id,
            example.example_id,
            variant_id,
            str(repetition),
            str(seed),
            example.source_sha256,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def write_result_artifact(
    *,
    result: LLMOnlyResult,
    example: BenchmarkExample,
    variant_id: str,
    repetition: int,
    seed: int,
    artifact_dir: Path,
) -> LLMOnlyResult:
    path = (
        artifact_dir
        / example.dataset_id
        / f"{artifact_id(example, variant_id, repetition, seed)}.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    result = result.model_copy(update={"artifact_path": str(path)})
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result
