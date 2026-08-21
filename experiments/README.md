# Experiments

This directory contains isolated research implementations that are not part of
the production `table2text` runtime.

| Experiment | Purpose |
| --- | --- |
| [`llm_only_pipeline`](llm_only_pipeline/) | Tests hallucination control through LLM role decomposition without deterministic analytics or verification. |

Each experiment owns only its implementation, reproducible configuration,
focused tests, and evidence required by the dissertation. Shared benchmark
loading and metric code remain in the main package.
