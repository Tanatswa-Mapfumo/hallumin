# Table2Text PydanticAI Multi-Agent System

This project investigates whether an evidence-generating, claim-verifying,
multi-agent workflow can reduce hallucinations in Table2Text generation.

It does not claim to eliminate hallucinations.

## Six-agent architecture

1. Data Understanding Agent
2. Orchestrator and Investigation Planner
3. Evidence Analyst Agent
4. Claim Verification Agent
5. Writer Agent
6. Factual Accuracy Auditor Agent

## Workflow

Input tables
→ deterministic loading and profiling
→ Data Understanding Agent
→ Orchestrator creates a frozen investigation plan
→ deterministic analytical execution
→ Evidence Analyst creates claim candidates
→ Claim Verification Agent
→ deterministic claim-ledger gate
→ Writer Agent
→ Factual Accuracy Auditor
→ pass, revise, or block

## Why deterministic analytics remain

The LLM agents do not calculate statistics directly.

Python performs:

- table loading;
- profiling;
- missing-value analysis;
- descriptive statistics;
- correlations and group comparisons;
- predictive train/test validation;
- forecast backtesting;
- causal-feasibility checks;
- evidence and claim identifier validation;
- number-support checks;
- audit gates.

The LLM agents perform:

- semantic data understanding;
- investigation planning;
- evidence synthesis;
- claim review;
- natural-language writing;
- semantic factual-accuracy annotation.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"