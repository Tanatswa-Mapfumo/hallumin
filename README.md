# MScProject

This repository contains the implementation and evaluation evidence for an MSc
project on evidence-grounded table-to-text generation. The production Python
package is in [`table2text_pydanticai`](table2text_pydanticai/); dissertation
evidence and research notebooks are kept outside the runtime package.

## Repository layout

| Path | Purpose |
| --- | --- |
| `table2text_pydanticai/` | Installable Python package, tests, evaluation framework, and sealed evaluation artifacts. |
| `experiments/` | Isolated research implementations that reuse, but do not duplicate, the main evaluation framework. |
| `docs/` | Architecture notes, evaluation evidence banks, human-study materials, and figures. |
| `notebooks/` | Research-facing workflow, ablation, and LLM-judge notebooks. |

The protected-holdout directories under `table2text_pydanticai/evaluation/`
are immutable research records. Their internal paths and hashes are preserved
deliberately.

## Quick start

```bash
cd table2text_pydanticai
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
pytest -p no:rerunfailures
```

See [`table2text_pydanticai/README.md`](table2text_pydanticai/README.md) for
runtime and evaluation commands, and [`docs/README.md`](docs/README.md) for the
research-document index.
