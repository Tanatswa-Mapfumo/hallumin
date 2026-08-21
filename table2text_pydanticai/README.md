# Table2Text PydanticAI

An evidence-grounded, six-role Table2Text workflow designed to reduce factual
errors while preserving natural-language generation. The project investigates
hallucination reduction; it does not claim that hallucinations are eliminated.

## Architecture

1. **Data Understanding** interprets structure and field semantics.
2. **Orchestrator** creates a frozen, capability-aware investigation plan.
3. **Evidence Analyst** synthesises deterministic evidence into candidate claims and insights.
4. **Claim Verifier** checks candidate support and permissions.
5. **Writer** realises verified content under the selected report contract.
6. **Factual Auditor** checks support, factuality, and task fulfilment.

Python handles loading, profiling, analytical execution, evidence identifiers,
support maps, and deterministic validation. LLM roles handle semantic
interpretation, planning, bounded synthesis, natural-language realisation, and
semantic audit.

## Installation

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Install the optional evaluation stack when reproducing benchmark metrics:

```bash
pip install -e ".[dev,evaluation]"
```

API keys and model settings belong in `.env`; the file is ignored by Git.
`.env.example` documents the supported settings.

## Run the workflow

```bash
table2text run inputs/example.csv \
  --request "Understand the dataset and report its strongest supported findings." \
  --output-dir runs
```

For deterministic operation without model calls, add `--no-llm`. Use
`table2text run --help` for report contracts, input-role declarations, and
audit modes.

## Run tests

```bash
pytest -p no:rerunfailures
ruff check src tests scripts
```

The explicit plugin disable keeps `pytest-rerunfailures` from opening a local
status socket in restricted execution environments; ordinary local runs may
use `pytest` directly.

## Evaluation

```bash
table2text-evaluate init-config
table2text-evaluate list-datasets
table2text-evaluate --help
```

Canonical evaluation configuration is in `evaluation/config/`. Reproducible
notebooks are in `evaluation/notebooks/`, while generated development outputs
under `evaluation/prepared/`, `evaluation/generations/`, and
`evaluation/results/` are ignored by default. Sealed dissertation artifacts
are retained in their named experiment directories.

## Package layout

```text
src/table2text/             Runtime workflow and schemas
src/table2text/evaluation/  Evaluation framework
tests/                      Regression and integration tests
scripts/                    External metric workers
evaluation/config/          Canonical and archived experiment configuration
evaluation/notebooks/       Reproducible research notebooks
evaluation/scripts/         Evidence and figure builders
```
