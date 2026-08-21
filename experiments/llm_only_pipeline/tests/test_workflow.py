from __future__ import annotations

from table2text.evaluation.models import BenchmarkExample, OutputMode, TaskFamily

from table2text_llm_only.schemas import AgentCallTrace, UsageSummary
from table2text_llm_only.workflow import LLMOnlyWorkflow


def example() -> BenchmarkExample:
    return BenchmarkExample(
        dataset_id="demo_e2e",
        example_id="demo-1",
        task_family=TaskFamily.ATTRIBUTE_VERBALISATION,
        output_mode=OutputMode.SHORT_TEXT,
        language="en",
        source_payload={"name": "The Eagle", "food": "French", "area": "riverside"},
        source_text="name[The Eagle], food[French], area[riverside]",
        references=["The Eagle is a French riverside restaurant."],
        request="Express all and only the supplied attributes.",
        parent_table=[["name", "The Eagle"], ["food", "French"], ["area", "riverside"]],
        metadata={"normalizer": "e2e"},
        source_sha256="demo-source",
        reference_sha256="demo-reference",
    )


class FakeClient:
    config = type("Config", (), {"model": "fake-llm", "base_url": "offline"})()

    def json_call(self, *, stage: str, system: str, user: str):
        del system, user
        claim = {
            "claim_id": "C1",
            "claim": "The Eagle serves French food in the riverside area.",
            "claim_type": "attribute",
            "source_refs": ["source_payload.name", "source_payload.food", "source_payload.area"],
            "copied_values": ["The Eagle", "French", "riverside"],
            "calculation_or_reasoning": "Direct attribute verbalisation.",
            "confidence": 0.99,
        }
        payloads = {
            "source_interpreter": {
                "task_understanding": "Verbalise the supplied restaurant attributes.",
                "source_units": "One meaning representation.",
                "important_entities": ["The Eagle"],
                "important_fields": ["name", "food", "area"],
                "allowed_claim_types": ["attribute verbalisation"],
                "risks": ["Do not add absent attributes."],
            },
            "llm_analysis": {"claims": [claim], "analysis_notes": []},
            "claim_critic": {
                "reviews": [
                    {
                        "claim_id": "C1",
                        "status": "supported",
                        "reason": "All values occur in the source.",
                        "corrected_claim": None,
                    }
                ],
                "global_warnings": [],
            },
            "claim_adjudicator": {
                "accepted_claims": [claim],
                "rejected_claims": [],
                "warnings": [],
            },
            "writer": {
                "title": None,
                "sentences": [{"text": claim["claim"], "claim_ids": ["C1"]}],
            },
            "output_auditor": {
                "decision": "pass",
                "support_rate": 1.0,
                "findings": [],
                "notes": [],
            },
        }
        trace = AgentCallTrace(
            stage=stage,
            model="fake-llm",
            elapsed_seconds=0.0,
            usage=UsageSummary(),
        )
        return payloads[stage], trace


def test_source_packet_holds_out_references():
    workflow = LLMOnlyWorkflow(client=FakeClient())

    packet = workflow._source_packet(example())

    assert "references" not in packet
    assert "reference_sha256" not in packet
    assert packet["source_payload"]["name"] == "The Eagle"


def test_offline_workflow_preserves_supported_claim_path():
    result = LLMOnlyWorkflow(client=FakeClient()).run(example())

    assert result.generated_text == "The Eagle serves French food in the riverside area."
    assert result.final_audit.decision == "pass"
    assert [trace.stage for trace in result.traces] == [
        "source_interpreter",
        "llm_analysis",
        "claim_critic",
        "claim_adjudicator",
        "writer",
        "output_auditor",
    ]


def test_evidence_gate_rejects_uncited_accepted_claim():
    workflow = LLMOnlyWorkflow(client=FakeClient())
    result = workflow.run(example())
    claim = result.adjudicated_claims.accepted_claims[0].model_copy(
        update={"source_refs": []}
    )
    adjudicated = result.adjudicated_claims.model_copy(
        update={"accepted_claims": [claim]}
    )

    gated = workflow.enforce_accepted_claim_evidence(adjudicated)

    assert gated.accepted_claims == []
    assert gated.rejected_claims[0].claim_id == "C1"
