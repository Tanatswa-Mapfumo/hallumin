from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from table2text.evaluation.models import BenchmarkExample, VariantConfig

from .workflow import LLMOnlyWorkflow, write_result_artifact


def _environment_value(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def llm_only_multi_agent(
    *,
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
) -> dict[str, Any]:
    """Run the LLM-only workflow through the main evaluator's callable interface."""
    settings = dict(variant.settings_overrides)
    workflow = LLMOnlyWorkflow.from_settings(settings)
    result = workflow.run(example)

    artifact_dir = Path(
        str(
            settings.get("llm_only_artifact_dir")
            or _environment_value("T2T_LLM_ONLY_ARTIFACT_DIR")
            or "artifacts/runs"
        )
    )
    result = write_result_artifact(
        result=result,
        example=example,
        variant_id=variant.variant_id,
        repetition=repetition,
        seed=seed,
        artifact_dir=artifact_dir,
    )

    prompt_tokens = sum(trace.usage.prompt_tokens or 0 for trace in result.traces)
    completion_tokens = sum(
        trace.usage.completion_tokens or 0 for trace in result.traces
    )
    total_tokens = sum(trace.usage.total_tokens or 0 for trace in result.traces)
    return {
        "generated_text": result.generated_text,
        "baseline_type": "llm_only_multi_agent",
        "agent_count": len(result.traces),
        "artifact_path": result.artifact_path,
        "candidate_claim_count": len(result.candidate_claims.claims),
        "accepted_claim_count": len(result.adjudicated_claims.accepted_claims),
        "rejected_claim_count": len(result.adjudicated_claims.rejected_claims),
        "audit_decision": result.final_audit.decision,
        "audit_support_rate": result.final_audit.support_rate,
        "repair_attempted": result.repaired_draft is not None,
        "model": workflow.client.config.model,
        "base_url": workflow.client.config.base_url,
        "prompt_tokens": prompt_tokens or None,
        "completion_tokens": completion_tokens or None,
        "total_tokens": total_tokens or None,
    }
