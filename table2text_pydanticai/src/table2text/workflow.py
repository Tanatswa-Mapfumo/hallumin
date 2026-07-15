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
    build_orchestrator_agent,
    build_verifier_agent,
    build_writer_agent,
    fallback_execution_plan,
    fallback_understanding,
)
from .analytics import execute_plan
from .audit import (
    accept_writer_quality_revision,
    apply_repair_proposal,
    assess_report_component_coverage,
    augment_fact_ledger_for_report_coverage,
    assess_report_components,
    build_writer_evidence_pack,
    compact_json,
    decide_release_status,
    deterministic_audit,
    fallback_audit_proposal,
    fallback_fact_candidates,
    fallback_verification,
    fallback_writer,
    finalise_fact_ledger,
    json_safe,
    materialise_writer_output,
    merge_audit_proposal,
    validate_writer_output,
)
from .config import Settings
from .data import load_data, profile_data
from .schemas import (
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    DataUnderstanding,
    ExecutionPlan,
    ExternalTruthSource,
    FactCandidateSet,
    PipelineResult,
    QualityStatus,
    ReportComponent,
    ReleaseStatus,
    RunManifest,
    VerificationResult,
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


def build_compact_writer_payload(
    pack: WriterEvidencePack,
) -> dict[str, Any]:
    tables = [
        {
            "table_name": table.table_name,
            "unit_of_observation": (
                table.unit_of_observation
            ),
            "summary": table.summary,
        }
        for table
        in pack.dataset_understanding.tables
    ]

    return {
        "user_request": pack.user_request,
        "report_specification": (
            pack.report_specification
        ),
        "dataset_summary": (
            pack.dataset_understanding
            .dataset_summary
        ),
        "table_context": tables,
        "priority_facts": (
            pack.priority_facts
        ),
        "supporting_facts": (
            pack.supporting_facts
        ),
        "limitation_facts": (
            pack.limitation_facts
        ),
        "analytical_recommendations": (
            pack.analytical_recommendations
        ),
        "reader_facing_limitations": (
            pack.reader_facing_limitations
        ),
        "internal_prohibited_interpretations": (
            pack
            .internal_prohibited_interpretations
        ),
    }


def build_writer_quality_revision_prompt(
    *,
    writer_pack: WriterEvidencePack,
    current_output: WriterOutput,
    missing_components: list[ReportComponent],
    quality_findings: list[str],
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

    current_word_count = len(
        re.findall(
            r"\\b[\\w'-]+\\b",
            current_output.markdown,
        )
    )

    target_words = (
        writer_pack.report_specification
        .target_length_words
    )

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

    return (
        "Revise the complete report once for task fulfilment and natural "
        "data-science writing before factual audit.\n\n"
        "This is a Writer quality revision, not a factual repair.\n\n"
        "Do not merely rephrase the existing short report.\n"
        "Use the unused verified priority facts to cover missing sections.\n"
        "Do not invent calculations or facts.\n"
        "Do not calculate statistics.\n"
        "Do not introduce new numbers, entities, categories, metadata, "
        "causal claims, prediction claims, forecast claims, or deployment "
        "claims.\n"
        "Do not expose internal control fields such as Finding:, Strength:, "
        "Important Note:, Interpretation Notes:, Recommended Use:, or Global "
        "Prohibited Interpretations.\n"
        "Use natural data-science prose and consolidate shared caveats.\n"
        "Prefer strong and moderate evidence over small effects.\n"
        "Return structured sections and sentences only. Do not return "
        "Markdown or a separate support map; the controller will create both "
        "deterministically.\n"
        "Every factual sentence must list its supporting fact IDs.\n\n"
        f"Current word count: {current_word_count}\n"
        f"Minimum useful word count: {minimum_words}\n"
        f"Available priority facts: {len(writer_pack.priority_facts)}\n"
        f"Unused priority facts: {len(unused_priority_facts)}\n\n"
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
        + compact_json(unused_priority_facts)
        + "\n\nCompact Writer evidence pack:\n"
        + compact_json(
            build_compact_writer_payload(
                writer_pack
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
        self.writer_agent = None
        self.auditor_agent = None

        if self.settings.use_llm:
            self.data_understanding_agent = build_data_understanding_agent(
                self.settings
            )
            self.orchestrator_agent = build_orchestrator_agent(self.settings)
            self.evidence_agent = build_evidence_agent(self.settings)
            self.verifier_agent = build_verifier_agent(self.settings)
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

    async def audit_once(
        self,
        *,
        run_id: str,
        writer_output: WriterOutput,
        fact_ledger: Any,
        evidence_ledger: Any,
        plan: ExecutionPlan,
        audit_mode: AuditMode,
        external_truth_sources: list[ExternalTruthSource],
        revision_round: int,
        store: ArtifactStore,
        stage_name: str,
    ) -> tuple[AuditReport, AuditRepairProposal]:
        deterministic = deterministic_audit(
            writer_output=writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=revision_round,
            report_specification=plan.report_specification,
            settings=self.settings,
        )

        prompt = (
            "Audit this report independently and propose targeted repairs "
            "for high-confidence factual errors.\n\n"
            "User objective:\n"
            + plan.objective
            + "\n\nReport specification:\n"
            + compact_json(plan.report_specification)
            + "\n\nWriter output:\n"
            + compact_json(writer_output)
            + "\n\nVerified fact ledger:\n"
            + compact_json(fact_ledger)
            + "\n\nEvidence ledger:\n"
            + compact_json(evidence_ledger)
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
                    "report_text": writer_output.markdown,
                    "valid_fact_ids": [
                        fact.fact_id
                        for fact in fact_ledger.writer_ready_facts
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

        return merged, proposal

    async def run(
        self,
        inputs: list[str | Path],
        request: str,
        *,
        audit_mode: AuditMode = AuditMode.INTERNAL,
        external_truth_sources: list[ExternalTruthSource] | None = None,
    ) -> PipelineResult:
        external_truth_sources = external_truth_sources or []

        data_bundle = load_data(inputs)
        profile = profile_data(data_bundle)

        run_id = ArtifactStore.create_run_id(
            data_bundle.fingerprint
        )
        store = ArtifactStore(
            self.settings.output_dir,
            run_id,
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
        )

        store.save_json("00_manifest.json", manifest)
        store.save_json("01_profile.json", profile)

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

        understanding = await self.run_agent_or_fallback(
            stage="data_understanding",
            agent=self.data_understanding_agent,
            prompt=(
                "Create a data understanding and analytical-risk report.\n\n"
                + compact_json(profile)
            ),
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "fingerprint": profile.fingerprint,
                    "table_names": table_names,
                    "columns": columns,
                },
            ),
            fallback=lambda: fallback_understanding(profile),
            store=store,
        )
        understanding = DataUnderstanding.model_validate(understanding)
        store.save_json("02_understanding.json", understanding)

        plan = await self.run_agent_or_fallback(
            stage="orchestration_and_planning",
            agent=self.orchestrator_agent,
            prompt=(
                "User objective:\n"
                + request
                + "\n\nData profile:\n"
                + compact_json(profile)
                + "\n\nData understanding:\n"
                + compact_json(understanding)
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
                },
            ),
            fallback=lambda: fallback_execution_plan(
                request,
                profile,
                audit_mode,
                self.settings,
            ),
            store=store,
        )

        plan = ExecutionPlan.model_validate(plan)
        required_components = infer_required_report_components(request)
        report_specification = plan.report_specification.model_copy(
            update={
                "report_purpose": request,
                "required_components": list(
                    dict.fromkeys(
                        [
                            *plan.report_specification.required_components,
                            *required_components,
                        ]
                    )
                )
            }
        )
        plan = plan.model_copy(
            update={
                "objective": request,
                "report_specification": report_specification,
                "audit_mode": audit_mode,
                "revision_limit": min(
                    plan.revision_limit,
                    self.settings.max_revision_rounds,
                ),
                "frozen": True,
            }
        )
        store.save_json("03_execution_plan.json", plan)

        evidence_ledger = execute_plan(
            data_bundle,
            plan,
            self.settings,
        )
        store.save_json("04_evidence_ledger.json", evidence_ledger)

        fact_candidates = await self.run_agent_or_fallback(
            stage="evidence_synthesis",
            agent=self.evidence_agent,
            prompt=(
                "Create atomic fact candidates from this rich evidence ledger.\n\n"
                + compact_json(evidence_ledger)
                + "\n\nMaximum facts:\n"
                + str(plan.maximum_facts)
            ),
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "evidence_ledger": evidence_ledger.model_dump(mode="json")
                },
            ),
            fallback=lambda: fallback_fact_candidates(
                evidence_ledger,
                plan.maximum_facts,
            ),
            store=store,
        )
        fact_candidates = FactCandidateSet.model_validate(fact_candidates)
        store.save_json("05_fact_candidates.json", fact_candidates)

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

        writer_pack = build_writer_evidence_pack(
            request=request,
            understanding=understanding,
            plan=plan,
            evidence=evidence_ledger,
            fact_ledger=fact_ledger,
            settings=self.settings,
        )
        store.save_json("08_writer_evidence_pack.json", writer_pack)

        writer_prompt = (
            "Write the final natural data-science report from the "
            "compact verified-fact package below.\n\n"
            "Return structured sections and sentences. Do not return "
            "a Markdown field or construct a separate support map; the "
            "controller will create both deterministically.\n\n"
            + compact_json(
                build_compact_writer_payload(
                    writer_pack
                )
            )
        )

        writer_draft_or_fallback = await self.run_agent_or_fallback(
            stage="natural_writer",
            agent=self.writer_agent,
            prompt=writer_prompt,
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "fact_ledger": fact_ledger.model_dump(mode="json")
                },
            ),
            fallback=lambda: fallback_writer(writer_pack),
            store=store,
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

            raw_writer_output = (
                materialise_writer_output(
                    writer_draft,
                    fact_ledger,
                    writer_mode="llm_writer",
                    eligible_for_primary_evaluation=True,
                )
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

        initial_quality_audit = deterministic_audit(
            writer_output=raw_writer_output,
            fact_ledger=fact_ledger,
            evidence=evidence_ledger,
            mode=audit_mode,
            external_sources=external_truth_sources,
            revision_round=0,
            report_specification=plan.report_specification,
            settings=self.settings,
        )
        store.save_json("10_initial_writer_quality.json", initial_quality_audit)

        writer_output_for_audit = raw_writer_output
        quality_revised_writer_output: WriterOutput | None = None
        needs_quality_revision = (
            bool(missing_components)
            or initial_quality_audit.quality_assessment.status == QualityStatus.REVISE
        )

        if (
            needs_quality_revision
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
                        initial_quality_audit
                        .quality_assessment
                        .findings
                    ),
                    settings=self.settings,
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_ledger": (
                            fact_ledger.model_dump(
                                mode="json"
                            )
                        )
                    },
                ),
                fallback=lambda: raw_writer_output,
                store=store,
            )

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
                revision_candidate = materialise_writer_output(
                    revised_writer_draft,
                    fact_ledger,
                    writer_mode="llm_writer",
                    eligible_for_primary_evaluation=True,
                    quality_revision_round=1,
                    quality_revision_summary=(
                        "Bounded whole-report "
                        "quality-revision candidate."
                    ),
                )

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
                )
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

        initial_audit, proposal = await self.audit_once(
            run_id=run_id,
            writer_output=writer_output_for_audit,
            fact_ledger=fact_ledger,
            evidence_ledger=evidence_ledger,
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

            current_audit, proposal = await self.audit_once(
                run_id=run_id,
                writer_output=current_output,
                fact_ledger=fact_ledger,
                evidence_ledger=evidence_ledger,
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
        release_status = decide_release_status(
            annotations=final_audit.annotations,
            quality=final_audit.quality_assessment,
            methodological_warnings=final_audit.methodological_warnings,
            repair_budget_exhausted=repair_budget_exhausted,
            audit_mode=audit_mode,
        )

        if (
            release_status
            == ReleaseStatus.HUMAN_REVIEW_REQUIRED
        ):
            final_decision = AuditDecision.BLOCK
        else:
            final_decision = AuditDecision.PASS

        final_audit = final_audit.model_copy(
            update={
                "decision": final_decision,
                "release_status": release_status,
            }
        )

        approved = release_status in {
            ReleaseStatus.APPROVED,
            ReleaseStatus.APPROVED_WITH_WARNINGS,
        }

        result = PipelineResult(
            run_id=run_id,
            profile=profile,
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
                "writer_mode": raw_writer_output.writer_mode,
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
    ) -> PipelineResult:
        return asyncio.run(
            self.run(
                inputs,
                request,
                audit_mode=audit_mode,
                external_truth_sources=external_truth_sources,
            )
        )
