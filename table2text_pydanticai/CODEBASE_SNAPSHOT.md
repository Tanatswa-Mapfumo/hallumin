# Codebase Snapshot

- Project: `table2text_pydanticai`
- Updated: `2026-08-02T19:25:01Z`
- Branch: `main`
- Commit at snapshot time: `40b4a4b`
- Purpose: a PydanticAI multi-agent table-to-text system for producing grounded natural-language reports from tabular, semi-structured, and event-style inputs.

This file is a maintained architectural snapshot, not a full source dump. It describes the current system shape, evaluation tooling, recent event-report upgrades, and known issues.

## Current Working State

The worktree has active uncommitted changes in source, tests, evaluation config, and generated notebook/evaluation files. The main changed areas are:

```text
table2text_pydanticai/.env.example
table2text_pydanticai/evaluation/config/metrics_sportsett_basketball_1.json
table2text_pydanticai/src/table2text/agents.py
table2text_pydanticai/src/table2text/audit.py
table2text_pydanticai/src/table2text/evaluation/generation.py
table2text_pydanticai/src/table2text/evaluation/reference_metrics.py
table2text_pydanticai/src/table2text/workflow.py
table2text_pydanticai/tests/test_reference_evaluation.py
table2text_pydanticai/tests/test_semantic_event_pipeline.py
table2text_pydanticai/tests/test_smoke.py
```

New local evaluation configs include:

```text
table2text_pydanticai/evaluation/config/variants_raw_deepseek_v4_flash.json
table2text_pydanticai/evaluation/config/variants_sportsett_basketball_4934.json
```

## Package Layout

```text
table2text_pydanticai/
  pyproject.toml
  README.md
  CODEBASE_SNAPSHOT.md
  .env.example
  inputs/
  runs_notebook/
  evaluation/
    config/
    prepared/
    generations/
    results/
    human/
  src/table2text/
    __init__.py
    __main__.py
    agents.py
    analytics.py
    audit.py
    capabilities.py
    cli.py
    config.py
    data.py
    evaluation_backends.py
    schemas.py
    structure.py
    workflow.py
    evaluation/
      __init__.py
      alignscore_client.py
      cli.py
      datasets.py
      deepeval_metrics.py
      diagnostics.py
      external_factuality.py
      generation.py
      human_evaluation.py
      models.py
      notebook.py
      reference_metrics.py
      statistics.py
  tests/
    test_reference_evaluation.py
    test_semantic_event_pipeline.py
    test_smoke.py
```

## Dependencies

Core runtime dependencies:

```text
pydantic
pydantic-ai-slim[openai]
pandas
numpy
scikit-learn
openpyxl
pyarrow
```

Evaluation extras include:

```text
datasets
huggingface-hub
sacrebleu
rouge-score
nltk
bert-score
transformers
torch
sentencepiece
scipy
tabulate
deepeval
spacy
```

The package exposes:

```text
table2text
table2text-evaluate
```

## Configuration

Runtime configuration is centered on `Settings` in `src/table2text/config.py`.

Common `.env.example` controls include:

```text
T2T_USE_LLM
T2T_OUTPUT_DIR
T2T_MAX_REVISION_ROUNDS
T2T_MAX_AGENT_REQUESTS
T2T_MAX_TOTAL_TOKENS
T2T_RANDOM_SEED
T2T_MAX_ANALYSIS_ROWS
T2T_STRUCTURED_OUTPUT_MODE

T2T_FULL_DATA_CORRELATION_LIMIT
T2T_MIN_ABS_CORRELATION
T2T_MAX_CORRELATION_FINDINGS
T2T_MAX_GROUP_FINDINGS

T2T_WRITER_TARGET_WORDS
T2T_WRITER_MAX_WORDS
T2T_REPAIR_CANDIDATES_PER_SENTENCE

T2T_ENABLE_INSIGHT_SYNTHESIS
T2T_MIN_INSIGHT_CONFIDENCE
T2T_MIN_INSIGHT_SALIENCE
T2T_MIN_FACTS_PER_BOUNDED_INSIGHT
T2T_ALLOW_HYPOTHESES_IN_REPORT

T2T_WRITER_QUALITY_REVISION_ROUNDS
T2T_MINIMUM_REPORT_WORD_RATIO
T2T_MINIMUM_REPORT_WORD_FLOOR
T2T_MAXIMUM_REPEATED_CAVEAT_MENTIONS

T2T_MODEL_DATA_UNDERSTANDING
T2T_MODEL_ORCHESTRATOR
T2T_MODEL_EVIDENCE
T2T_MODEL_VERIFIER
T2T_MODEL_WRITER
T2T_MODEL_AUDITOR
```

Model strings support local and remote style prefixes, for example:

```text
ollama:gemma3:12b
deepseek:deepseek-chat
deepseek:deepseek-v4-pro
deepseek:deepseek-v4-flash
```

Secrets are not stored in this snapshot.

## High-Level Pipeline

The current system is best understood as:

```text
raw input
  -> load and normalize input
  -> interpret input shape and field roles
  -> separate source fields from reference/evaluation fields
  -> infer or apply report contract
  -> resolve available evidence capabilities
  -> freeze execution plan
  -> compute deterministic evidence
  -> synthesize and verify fact candidates
  -> recover coverage-critical facts when needed
  -> synthesize and verify bounded insights
  -> assemble writer evidence pack and content requirements
  -> LLM writer or deterministic fallback writer
  -> support-map validation and materialisation
  -> factual audit and possible repair
  -> genre/task quality checks
  -> final report and pipeline artifacts
```

The pipeline is intentionally evidence-led: the Writer can phrase, order, compress, and narrate, but claims should be traceable to verified facts, verified insights, or structured evidence.

## Core Source Modules

### `config.py`

Defines `Settings`, model configuration, analytical thresholds, writer settings, insight settings, and safety/fallback controls.

Important current direction:

- `writer_max_words` can be unset to avoid a hard cap.
- writer target words can guide length without forcing an exact length.
- model choices can be varied per stage, so cheaper/local models can remain on low-risk stages while DeepSeek is used for harder generation or judging.

### `schemas.py`

Defines the main typed contracts used across the pipeline.

Key enums and schema groups:

```text
ReportGenre
CommunicationTask
OutputForm
InputShape
SemanticRole
AnalyticalFunction
SemanticLevel
EvidenceCapability
InsightType
InsightContribution
InsightVerificationStatus
AuditMode
AuditDecision
ReleaseStatus
```

Important report genres and tasks:

```text
data_science_report
dataset_overview
event_report
focused_table_description
table_entailment
table_question_answering
attribute_verbalisation
triple_verbalisation
custom
```

Important input shapes:

```text
flat_table
nested_record
entity_collection
event_record
time_series
input_reference_pairs
ambiguous
```

Important evidence capabilities:

```text
dataset_profile
focused_table_region
structured_record_verbalisation
missingness
duplicates
distribution_summary
association
group_comparison
ranking
extrema
temporal_change
event_outcome
entity_performance
anomaly_detection
```

### `data.py`

Loads and normalizes local inputs.

Current responsibilities:

- CSV loading.
- JSON loading.
- flattening and preserving structured records.
- dataset/table naming.
- basic table-profile construction.
- handling benchmark-style wrapped inputs.

### `structure.py`

Contains deterministic structure interpretation support.

Current responsibilities:

- classify input shape.
- detect nested records and event records.
- detect heterogeneous rows.
- detect sparse flattening risks.
- identify probable input, reference, and metadata fields.
- support benchmark cases where target/reference text must be held out.

### `capabilities.py`

Defines capability registry and availability resolution.

The registry answers: "What can be safely computed from this input?"

The Orchestrator answers: "Which supported operations answer the request?"

Capabilities are generic rather than domain-specific. For example, basketball and baseball are treated as event/entity structures rather than separate hard-coded sports pipelines.

### `analytics.py`

Implements deterministic analysis and evidence production.

Main capability families:

- dataset profile.
- missingness.
- duplicate detection.
- distribution summaries.
- correlations.
- group comparisons.
- rankings.
- extrema.
- event outcome evidence.
- entity performance evidence.
- team/participant contrasts.
- event sequence highlights when ordered sequence evidence exists.

### `agents.py`

Defines the LLM-facing agents and prompt contracts.

Current agent roles:

```text
Data Understanding
Orchestrator / Planner
Evidence Analyst
Verifier
Insight Synthesizer
Writer
Auditor
```

Recent Writer behavior:

- event reports should use event facts as the center of the report.
- reference-recap benchmark outputs should be prose-first and avoid visible Markdown headings.
- the Writer may narrate and combine supported facts, but must not invent unsupported chronology, causality, milestones, or external context.
- scope caveats should be internal or minimal for reference-style benchmark outputs unless the contract requires visible limitations.

### `audit.py`

Large validation and safety module.

Major responsibilities:

- convert facts and insights into writer-ready evidence packs.
- build writer content requirements.
- select priority facts.
- validate Writer output against support maps.
- materialise `WriterOutput`.
- provide deterministic fallback writer.
- perform factual audit.
- repair unsupported claims.
- detect unsupported entities/numbers.
- enforce prohibited claim types.
- enforce report-contract and genre-quality requirements.

Important recent behavior:

- event priority selection can be uncapped when `writer_max_words` is unset.
- reference-recap style suppresses deterministic headings and generic limitations in fallback output.
- event content slots distinguish factual errors from genre-quality omissions.

### `workflow.py`

Coordinates the full pipeline.

Important responsibilities:

- create run directories.
- call every stage.
- persist artifacts.
- handle LLM fallback behavior.
- apply report contract and structure profile.
- choose deterministic event plan when structure/capability evidence is high-confidence.
- run verification, insights, writer, audit, and repair loops.
- return `PipelineResult`.

Important helper:

```text
should_use_deterministic_event_plan()
```

This avoids expensive or brittle planning calls for high-confidence event records while still allowing the Writer to remain generative.

### `evaluation_backends.py`

Supports generation backends and model integration used by evaluation variants.

### `cli.py` and `__main__.py`

Provide command-line entry points for running the system.

## Main Pipeline Artifacts

Typical run artifacts in `runs_notebook/<run_id>/` include:

```text
01_inputs.json
02_data_understanding.json
03_evidence_queries.json
04_evidence_ledger.json
05_fact_candidates.json
06_verification.json
07_fact_ledger.json
07_fact_ledger_pre_coverage_recovery.json
08_writer_evidence_pack.json
09_writer_raw_output.json
09_writer_raw_report.md
09_writer_support_map.json
10_writer_quality_revision_candidate.md
final_result.json
final_report.md
pipeline_result.json
```

Not every run has every intermediate file. Files depend on fallback path, revision rounds, and whether optional stages were invoked.

## Report Contracts

The system now separates "what kind of output is wanted" from "what the input contains."

The decision priority is:

```text
1. explicit user request
2. experiment configuration
3. structured inference
4. deterministic fallback
```

Examples:

```text
"Write a neutral basketball game report" -> event_report
"Report the strongest statistical findings" -> data_science_report
"Summarise this for senior management" -> executive/custom summary behavior
"Understand the dataset and report its strongest findings" -> usually data_science_report unless benchmark/task metadata says otherwise
```

For benchmark event tasks, `evaluation/generation.py` maps the task family to:

```text
focus_scope = reference_recap
```

That tells the system to favor reference-style event recap over a generic dataset-quality report.

## Event Reporting Design

The current event-report architecture is deliberately generic.

It should work for:

```text
basketball games
baseball games
competitions
elections
awards
incidents
transactions
other single-event records
```

It should not require new code for every sport or domain.

Current event content slots include:

```text
event_result
event_context
participant_record_context
event_status
score_progression
event_sequence
leading_performance
main_contrast
secondary_performance
scope_limitations
```

For reference-recap evaluation style:

- visible headings are disabled.
- generic limitations sections are discouraged.
- dataset-quality boilerplate is prohibited.
- correlation, regression, statistical power, missingness, and modelling discussion are prohibited unless directly requested.
- event sequence and participant contrasts are prioritized when evidence exists.

## Important Behavioral Boundaries

Allowed:

- "Team A defeated Team B 116-114."
- "Player X led all players with 35 points."
- "Team A made more field goals, while Team B made more free throws."
- "The score-changing sequence includes a lead change in the fifth inning."
- "The comparison describes only the supplied event."

Not allowed unless explicitly supported:

- causation, for example "field goals caused the win."
- unsupported chronology, for example "dominated throughout" without sequence support.
- unsupported historical meaning, for example "upset" without standings/context support.
- broad generalization from one event.
- outside knowledge not present in source/evidence.
- leaking benchmark reference text into source/evidence.

## Insight System

An insight is a bounded interpretation that relates multiple verified facts or evidence items into a useful statement while staying inside claim permissions.

Examples:

```text
Data-science insight:
Temperature and apparent temperature are almost redundant as linear features because their Pearson correlation is 0.9926.

Event insight:
Washington's top three scorers were all Wizards players, while the assist leader came from the Lakers.

Table-local insight:
Among highlighted countries, Switzerland had the lower corporate tax rate and France had the higher rate.
```

Current insight principles:

- insights must have provenance.
- event insights can be useful rankings, contrasts, or narrative syntheses.
- event insights do not need a deeper data-science implication.
- hypotheses are blocked from reports unless explicitly allowed.
- failing one candidate should not require dropping the whole insight ledger.

## Evaluation Subsystem

The evaluation subsystem is under `src/table2text/evaluation/`.

### Main Files

```text
models.py              Typed benchmark, variant, metric, and experiment configs
datasets.py            Dataset preparation and normalisation
generation.py          Runs variants and records generations
reference_metrics.py   Lexical, semantic, source-grounded, HHEM, AlignScore, PARENT-style metrics
deepeval_metrics.py    DeepEval judge metrics
alignscore_client.py   Local AlignScore worker integration
external_factuality.py External factuality helpers
diagnostics.py         Run/metric diagnostics
statistics.py          Aggregation, correlations, bootstrap comparisons
human_evaluation.py    Human review support
notebook.py            Notebook-friendly wrappers
cli.py                 Evaluation command-line interface
```

### Notebook Helpers

```python
from table2text.evaluation import (
    default_paths,
    generate_reports_for_notebook,
    score_reference_metrics_for_notebook,
    score_deepeval_for_notebook,
    diagnostics_for_notebook,
)
```

### Dataset Preparation

Configured datasets include:

```text
sportsett_basketball
totto
e2e_nlg
web_nlg
dart
logicnlg
fetaqa
viggo
mlb_data_to_text
conversational_weather
turku_hockey
rotowire_english_german
```

Some Hugging Face datasets may be unavailable in the current environment because dataset scripts are no longer supported by the installed `datasets` version. Local prepared JSONL files are therefore important for repeatable notebook experiments.

### Generation Variants

Evaluation variants can use:

```text
table2text full system
precomputed generation files
callable generation functions
command backends
raw LLM baselines
```

Current local variant files include:

```text
variants.json
variants_raw_deepseek_v4_flash.json
variants_raw_deepseek_v4_pro.json
variants_sportsett_basketball_4934.json
variants_totto_full_system.json
variants_e2e_nlg_one.json
variants_mlb_data_to_text_one.json
```

### Metrics

Reference similarity metrics:

```text
BLEU
chrF
TER
ROUGE-1
ROUGE-2
ROUGE-L
ROUGE-Lsum
METEOR
BERTScore
PARENT-style table metrics when parent table data exists
```

Local/source-grounded factuality metrics:

```text
HHEM
AlignScore
```

Judge-based metrics:

```text
DeepEval with a configurable judge model, including DeepSeek through the existing env setup
```

For source-grounded event evaluation, `reference_metrics.py` now builds normalized event source context from structured JSON when possible. This gives HHEM/AlignScore a more readable factual context than raw nested JSON.

## Latest SportSett 4934 Comparison

Most recent compared files:

```text
evaluation/generations/sportsett_basketball_4934_generations.jsonl
evaluation/generations/sportsett_raw_deepseek_v4_flash_generations.jsonl
evaluation/generations/sportsett_4934_new_run_vs_raw_flash_baseline.jsonl
evaluation/results/sportsett_4934_new_run_vs_raw_flash_reference_metrics.jsonl
evaluation/results/sportsett_4934_new_run_vs_raw_flash_source_grounded_reference_metrics.jsonl
```

Latest full-system run:

```text
run_id: 20260801T151226Z_7ccd0b3a42
variant_id: full_system
writer_mode: llm_writer
release_status: approved
elapsed_seconds: about 795.21
generated_words: about 329
```

Raw Flash baseline:

```text
variant_id: raw_deepseek_v4_flash
elapsed_seconds: about 13.43
generated_words: about 216
```

Reference-similarity comparison:

| Metric | Full system | Raw flash | Better |
| --- | ---: | ---: | --- |
| BLEU | 0.107134 | 0.135714 | raw flash |
| chrF | 0.416579 | 0.385963 | full system |
| TER | 0.909910 | 0.813814 | raw flash |
| ROUGE-1 | 0.471495 | 0.514178 | raw flash |
| ROUGE-2 | 0.154560 | 0.189753 | raw flash |
| ROUGE-L | 0.231125 | 0.321361 | raw flash |
| METEOR | 0.257996 | 0.253407 | full system |
| HHEM mean support | 0.268974 | 0.250427 | full system |
| HHEM unsupported rate | 0.736842 | 0.769231 | full system |
| AlignScore base | 0.398620 | 0.307779 | full system |
| BERTScore F1 | 0.851689 | 0.850376 | full system |

Source-grounded comparison:

| Metric | Full system | Raw flash | Better |
| --- | ---: | ---: | --- |
| HHEM mean support | 0.206466 | 0.166208 | full system |
| HHEM min support | 0.008334 | 0.011255 | raw flash |
| HHEM unsupported rate | 0.789474 | 0.769231 | raw flash |
| AlignScore base | 0.190825 | 0.180214 | full system |

Interpretation:

- Raw flash still has stronger lexical overlap on BLEU/ROUGE/TER for this example.
- The full system is stronger on chrF, METEOR, BERTScore, reference-context HHEM mean support, reference-context AlignScore, and source-grounded AlignScore.
- The full system is slower because it runs structure interpretation, capability selection, evidence extraction, verification, insight handling, writing, support validation, audit, and repair.
- The latest reference-recap style is closer to benchmark prose, but visible caveat language can still hurt reference overlap.

## Current Notebook Run Pattern

Single specific example:

```python
import json
from pathlib import Path

from table2text.evaluation import default_paths, generate_reports_for_notebook
from table2text.evaluation.datasets import read_examples, write_jsonl

project_dir = Path("/Users/realgobs/Documents/MScproject/table2text_pydanticai")
paths = default_paths(project_dir)
examples = read_examples(paths["prepared_examples"])

dataset_id = "sportsett_basketball"
example_id = "4934"
one_example = next(
    example
    for example in examples
    if example.dataset_id == dataset_id and example.example_id == example_id
)

examples_path = project_dir / f"evaluation/prepared/{dataset_id}_{example_id}.jsonl"
write_jsonl(examples_path, [one_example])

variants_payload = json.loads(paths["variant_config"].read_text(encoding="utf-8"))
variants = {
    "variants": [
        {**variant, "enabled": variant["variant_id"] == "full_system"}
        for variant in variants_payload["variants"]
    ]
}

variants_path = project_dir / f"evaluation/config/variants_{dataset_id}_{example_id}.json"
variants_path.write_text(json.dumps(variants, indent=2), encoding="utf-8")

generations_path = project_dir / f"evaluation/generations/{dataset_id}_{example_id}_generations.jsonl"
run_root = project_dir / f"evaluation/generations/{dataset_id}_{example_id}_runs"

generations = await generate_reports_for_notebook(
    project_dir,
    examples_path=examples_path,
    variants_path=variants_path,
    output_path=generations_path,
    run_root=run_root,
    resume=False,
)
```

## Tests

Primary tests:

```text
tests/test_smoke.py
tests/test_semantic_event_pipeline.py
tests/test_reference_evaluation.py
```

Recent targeted verification command:

```bash
table2text_pydanticai/.venv/bin/python -m pytest -p no:rerunfailures \
  table2text_pydanticai/tests/test_reference_evaluation.py \
  table2text_pydanticai/tests/test_smoke.py \
  table2text_pydanticai/tests/test_semantic_event_pipeline.py \
  -q
```

This targeted suite has been passing after the recent evaluation and event-report fixes.

## Known Issues And Risks

### Runtime

Full-system event runs can be very slow compared with a raw single-call baseline. The latest SportSett 4934 run took about 795 seconds, while raw DeepSeek Flash took about 13 seconds.

Main runtime drivers:

- multi-stage LLM orchestration.
- verification and audit calls.
- insight synthesis and verification.
- large event evidence packs.
- external metric models such as HHEM, AlignScore, BERTScore, and DeepEval.

### Token Use

Token-heavy areas:

- data-understanding payloads for nested JSON.
- evidence synthesis over large event structures.
- verifier batches over many fact candidates.
- Writer evidence packs when uncapped event evidence is preserved.
- audit/repair prompts with full support context.

### Evaluation Ambiguity

Reference metrics measure closeness to the human reference, not pure correctness. A conservative report can score lower if it omits reference wording, and a raw baseline can score higher if it imitates the reference style while being less auditable.

Source-grounded metrics are useful but imperfect:

- raw structured JSON is difficult for HHEM/AlignScore.
- normalized event context improves readability but is still a proxy.
- sentence segmentation affects unsupported-rate metrics.

### Dataset Availability

Some benchmark datasets are unavailable through current Hugging Face dataset-loading paths because dataset scripts are no longer supported. Prepared local JSONL files are the stable path for experiments.

### DeepEval Timeouts

DeepEval calls using remote judges can time out. Disabling per-attempt timeouts entirely can cause notebook cells to hang; increasing the timeout is safer than setting it to an unbounded value.

### Reference-Recap Style

The latest event-recap path is closer to target benchmark outputs, but any visible "scope limitations" sentence in benchmark event reports may still reduce lexical overlap against concise human references.

## Recommended Next Improvements

High-impact improvements that preserve the architecture:

1. Keep evidence extraction broad, but add smarter salience ordering before the Writer.
2. Teach the Writer to compress event evidence into a reference-style recap without visible methodology language.
3. Use the LLM for narrative realization, but keep support-map validation strict.
4. Prefer small-batch fact verification over whole-ledger failure.
5. Keep normalized source context for HHEM/AlignScore and extend it to more task families.
6. Add a report-length policy that is soft and task-specific, not a fixed findings cap.
7. Compare outputs against both references and source-grounded metrics in every benchmark table.

## Current Design Principle

The system should remain generic:

```text
input adapter:
  what does the data structure represent?

capability registry:
  what can be computed safely?

orchestrator:
  which supported operations answer the request?

fact and insight ledgers:
  what claims are permitted?

report contract:
  what content should this output type contain?

writer:
  how should verified content be expressed?

auditors:
  is it factually supported and does it fulfil the task?
```

The target is not to hard-code basketball, baseball, ToTTo, or E2E outputs. The target is a general structure-aware, genre-aware, capability-aware table-to-text system whose reports are useful, auditable, and comparable against benchmark references.
