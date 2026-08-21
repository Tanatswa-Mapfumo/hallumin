"""Isolated LLM-only multi-agent Table2Text experiment."""

from .backend import llm_only_multi_agent
from .workflow import LLMOnlyWorkflow

__all__ = ["LLMOnlyWorkflow", "llm_only_multi_agent"]
