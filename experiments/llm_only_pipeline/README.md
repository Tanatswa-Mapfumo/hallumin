# LLM-Only Multi-Agent Experiment

This directory contains the isolated LLM-only comparison used by the MSc
Table2Text evaluation. It tests whether role decomposition can improve factual
grounding without the main system's deterministic analytics, evidence ledger,
fact scaffold, or deterministic audit.

The experiment deliberately reuses only the main project's benchmark contracts
and evaluation runner. It does not duplicate the operational codebase.

## Workflow

```text
source packet
  -> source interpreter
  -> claim analyst
  -> claim critic
  -> claim adjudicator
  -> constrained writer
  -> output auditor
  -> repair, when requested
```

The writer receives accepted claims rather than the raw source. Accepted claims
must retain explicit source references and copied values. Human references are
held out during generation and used only by evaluation metrics.

## Contents

```text
src/table2text_llm_only/   experiment runtime and evaluator adapter
config/variants.json      Flash variant and optional Pro comparison
notebooks/                reproducible smoke test and one-example runner
tests/                    offline behavioral tests
data/                     the retained SportSett 4934 case-study input
artifacts/                 retained Flash/Pro outputs and metric evidence
```

The raw one-call baseline is intentionally absent. It belongs to the main
evaluation framework and is not part of this multi-agent implementation.

## Setup

From the repository root:

```bash
python -m pip install -e table2text_pydanticai
python -m pip install -e 'experiments/llm_only_pipeline[dev]'
```

Set `DEEPSEEK_API_KEY` in the project-level `.env`. The remaining supported
settings are documented in [.env.example](.env.example).

## Verify

```bash
python -m pytest experiments/llm_only_pipeline/tests
python -m ruff check experiments/llm_only_pipeline
```

Use
[llm_only_smoke_test.ipynb](notebooks/llm_only_smoke_test.ipynb) for an offline
contract check, a live one-example run, and optional metric scoring.

## Preserved Evidence

The original Flash and Pro artifacts for `sportsett_basketball/4934` are stored
under `artifacts/sportsett_4934/`. These are immutable research outputs; the
paths recorded inside their metadata describe where the artifacts were created
before this repository cleanup.
