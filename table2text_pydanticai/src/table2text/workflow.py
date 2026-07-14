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
    apply_repair_proposal,
    assess_report_components,
    build_writer_evidence_pack,
    compact_json,
    deterministic_audit,
    fallback_audit_proposal,
    fallback_fact_candidates,
    fallback_verification,
    fallback_writer,
    finalise_fact_ledger,
    json_safe,
    merge_audit_proposal,
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
    ReportComponent,
    ReleaseStatus,
    RunManifest,
    VerificationResult,
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


def build_writer_quality_revision_prompt(
    writer_pack: WriterEvidencePack,
    current_output: WriterOutput,
    missing_components: list[ReportComponent],
) -> str:
    return (
        "Revise the report to cover required report components while "
        "preserving all currently supported factual statements.\n\n"
        "Do not invent calculations or facts.\n"
        "Do not expose internal control fields.\n"
        "You may reorganise, expand, combine, or omit supported content.\n\n"
        "Missing components:\n"
        + "\n".join(f"- {component.value}" for component in missing_components)
        + "\n\nEvidence pack:\n"
        + compact_json(writer_pack)
        + "\n\nCurrent output:\n"
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
                    )
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
        store.save_json("07_fact_ledger.json", fact_ledger)

        writer_pack = build_writer_evidence_pack(
            request=request,
            understanding=understanding,
            plan=plan,
            evidence=evidence_ledger,
            fact_ledger=fact_ledger,
            settings=self.settings,
        )
        store.save_json("08_writer_evidence_pack.json", writer_pack)

        raw_writer_output = await self.run_agent_or_fallback(
            stage="natural_writer",
            agent=self.writer_agent,
            prompt=(
                "Write the final natural data-science report from this "
                "evidence package.\n\n"
                + compact_json(writer_pack)
            ),
            dependencies=AgentDependencies(
                run_id=run_id,
                payload={
                    "fact_ledger": fact_ledger.model_dump(mode="json")
                },
            ),
            fallback=lambda: fallback_writer(writer_pack),
            store=store,
        )
        raw_writer_output = WriterOutput.model_validate(raw_writer_output)
        component_assessments = assess_report_components(
            raw_writer_output,
            fact_ledger,
            evidence_ledger,
            plan.report_specification.required_components,
        )
        missing_components = [
            assessment.component
            for assessment in component_assessments
            if not assessment.covered
        ]

        if missing_components and raw_writer_output.writer_mode == "llm_writer":
            revised_writer_output = await self.run_agent_or_fallback(
                stage="writer_quality_revision",
                agent=self.writer_agent,
                prompt=build_writer_quality_revision_prompt(
                    writer_pack,
                    raw_writer_output,
                    missing_components,
                ),
                dependencies=AgentDependencies(
                    run_id=run_id,
                    payload={
                        "fact_ledger": fact_ledger.model_dump(mode="json")
                    },
                ),
                fallback=lambda: raw_writer_output,
                store=store,
            )
            raw_writer_output = WriterOutput.model_validate(revised_writer_output)
            component_assessments = assess_report_components(
                raw_writer_output,
                fact_ledger,
                evidence_ledger,
                plan.report_specification.required_components,
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
        store.save_json(
            "09_writer_component_coverage.json",
            component_assessments,
        )

        initial_audit, proposal = await self.audit_once(
            run_id=run_id,
            writer_output=raw_writer_output,
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

        current_output = raw_writer_output
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
                release_status = (
                    ReleaseStatus.HUMAN_REVIEW_REQUIRED
                    if current_audit.annotations
                    else ReleaseStatus.APPROVED_WITH_WARNINGS
                )
                current_audit = current_audit.model_copy(
                    update={
                        "decision": AuditDecision.BLOCK,
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

        if current_audit.decision == AuditDecision.REVISE:
            release_status = (
                ReleaseStatus.HUMAN_REVIEW_REQUIRED
                if current_audit.annotations
                else ReleaseStatus.APPROVED_WITH_WARNINGS
            )
            current_audit = current_audit.model_copy(
                update={
                    "decision": AuditDecision.BLOCK,
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
        release_status = final_audit.release_status

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
