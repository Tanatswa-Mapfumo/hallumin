from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from pydantic_ai import RunUsage

from table2text.agents import AgentDependencies
from table2text.config import Settings
from table2text.workflow import ArtifactStore, Table2TextWorkflow


class RecordingAgent:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.usage_objects: list[RunUsage] = []
        self.usage_limits = []

    async def run(self, _prompt, *, deps, usage_limits, usage):
        assert isinstance(deps, AgentDependencies)
        self.usage_objects.append(usage)
        self.usage_limits.append(usage_limits)
        usage.incr(
            RunUsage(
                requests=1,
                input_tokens=11,
                output_tokens=3,
                cache_read_tokens=2,
                details={"reasoning_tokens": 1},
            )
        )
        if self.fail:
            raise RuntimeError("simulated provider failure")
        return SimpleNamespace(output={"ok": True})


def workflow_for_usage_test(tmp_path) -> Table2TextWorkflow:
    workflow = object.__new__(Table2TextWorkflow)
    workflow.settings = Settings(
        use_llm=True,
        output_dir=tmp_path,
        max_agent_requests=2,
        max_total_tokens=30,
    )
    return workflow


def trace_events(store: ArtifactStore) -> list[dict]:
    return [
        json.loads(line)
        for line in store.trace_path.read_text(encoding="utf-8").splitlines()
    ]


@pytest.mark.asyncio
async def test_agent_stages_share_one_report_usage_budget(tmp_path):
    workflow = workflow_for_usage_test(tmp_path)
    store = ArtifactStore(tmp_path, "shared-budget")
    agent = RecordingAgent()
    report_usage = RunUsage()
    dependencies = AgentDependencies(run_id="shared-budget", payload={})

    for stage in ("first", "second"):
        result = await workflow.run_agent_or_fallback(
            stage=stage,
            agent=agent,
            prompt="test",
            dependencies=dependencies,
            fallback=lambda: {"ok": False},
            store=store,
            report_usage=report_usage,
        )
        assert result == {"ok": True}

    assert agent.usage_objects == [report_usage, report_usage]
    assert report_usage.requests == 2
    assert report_usage.total_tokens == 28
    assert all(limit.request_limit == 2 for limit in agent.usage_limits)
    assert all(limit.total_tokens_limit == 30 for limit in agent.usage_limits)

    events = trace_events(store)
    assert [event["details"]["attempt_usage"]["total_tokens"] for event in events] == [
        14,
        14,
    ]
    assert events[-1]["details"]["report_usage"]["total_tokens"] == 28
    assert events[-1]["details"]["report_usage"]["details"] == {
        "reasoning_tokens": 2
    }


@pytest.mark.asyncio
async def test_failed_attempt_usage_is_not_lost(tmp_path):
    workflow = workflow_for_usage_test(tmp_path)
    store = ArtifactStore(tmp_path, "failed-attempt")
    report_usage = RunUsage()

    result = await workflow.run_agent_or_fallback(
        stage="failing-stage",
        agent=RecordingAgent(fail=True),
        prompt="test",
        dependencies=AgentDependencies(run_id="failed-attempt", payload={}),
        fallback=lambda: "fallback",
        store=store,
        report_usage=report_usage,
    )

    assert result == "fallback"
    assert report_usage.total_tokens == 14
    event = trace_events(store)[0]
    assert event["status"] == "fallback"
    assert event["details"]["attempt_usage"]["total_tokens"] == 14
    assert event["details"]["report_usage"]["requests"] == 1
