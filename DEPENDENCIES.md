# Dependencies and Verified Versions

## Supported environment

The package requires Python `>=3.11`. The submitted wheel was built and tested
with Python 3.11.15 on macOS. It is a pure-Python wheel and is not tied to
macOS; native numerical and evaluation dependencies are resolved by `pip` for
the target platform.

## Runtime dependencies

| Dependency | Supported range | Verified version | Purpose |
| --- | --- | --- | --- |
| Pydantic | `>=2.10,<3.0` | 2.13.4 | Strict schemas and validation |
| PydanticAI Slim (OpenAI extra) | `>=1.0,<2.0` | 1.107.1 | Model-provider integration |
| pandas | `>=2.2,<3.0` | 2.3.3 | Tabular loading and analysis |
| NumPy | `>=1.26,<3.0` | 2.4.6 | Numerical computation |
| scikit-learn | `>=1.5,<2.0` | 1.9.0 | Analytical and modelling utilities |
| openpyxl | `>=3.1,<4.0` | 3.1.5 | Excel input |
| PyArrow | `>=16.0` | 25.0.0 | Parquet and Arrow input |

## Development and test dependencies

| Dependency | Supported range | Verified version |
| --- | --- | --- |
| pytest | `>=8.0,<9.0` | 8.4.2 |
| pytest-asyncio | `>=0.24,<1.0` | 0.26.0 |
| Ruff | `>=0.8,<1.0` | 0.15.21 |

## Core evaluation dependencies

| Dependency | Supported range | Verified version |
| --- | --- | --- |
| datasets | `>=3.2,<4.0` | 3.6.0 |
| huggingface-hub | `>=0.27,<1.0` | 0.36.2 |
| sacrebleu | `>=2.4,<3.0` | 2.6.0 |
| rouge-score | `>=0.1.2,<0.2` | 0.1.2 |
| NLTK | `>=3.9,<4.0` | 3.10.0 |
| BERTScore | `>=0.3.13,<0.4` | 0.3.13 |
| Transformers | `>=4.46,<5.0` | 4.57.6 |
| PyTorch | `>=2.3,<3.0` | 2.13.0 |
| SentencePiece | `>=0.2,<0.3` | 0.2.2 |
| SciPy | `>=1.13,<2.0` | 1.17.1 |
| tabulate | `>=0.9,<1.0` | 0.9.0 |

Optional metric integrations are declared as separate extras in
`source/MScProject/table2text_pydanticai/pyproject.toml`; they are not required
to run the generation workflow. The verified environment additionally used
DeepEval 3.9.9 for selected judge-based experiments and ReportLab 5.0.0 to
produce submission documentation.

## External services and models

LLM-backed execution requires either a compatible Ollama server or a supported
API provider. Model identifiers and credentials are runtime configuration, not
Python dependencies. The supplied `.env.example` records the tested routing
patterns. No credentials or local model weights are included in the archive.

`requirements-tested.txt` records the exact direct dependency versions used to
verify this submission. The supported ranges in `pyproject.toml` remain the
authoritative installation contract.
