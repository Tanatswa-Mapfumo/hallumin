# Table2Text PydanticAI Codebase Snapshot

Updated: 2026-08-08  
Branch: `main`  
Current commit at snapshot time: `166d752`  
Snapshot purpose: dissertation-facing technical overview and file-by-file commentary.

This document describes the current `table2text_pydanticai` project as an implemented research system, not just as a collection of scripts. It is intended to help write the dissertation by explaining what each major file contributes, why it exists, and how the pieces fit together.

The codebase is currently in active experimental development. Several source and test files have local modifications, and many generated evaluation artifacts are untracked. That is expected for the project stage: the core system, evaluation harness, human annotation materials, and experiment outputs are being iterated together.

## One-Sentence System Description

`table2text_pydanticai` is an evidence-led, multi-agent data-to-text system that loads structured data, profiles and interprets its shape, plans supported analysis, computes evidence deterministically, verifies facts and bounded insights, and writes a grounded report with factual and genre-quality audit gates.

## Research Motivation

The project investigates whether a multi-agent architecture with deterministic evidence generation and explicit factual gates can reduce unsupported claims in table-to-text generation compared with raw single-LLM baselines.

The system does not claim to eliminate hallucination. The central research claim is narrower and testable:

- LLMs should not calculate statistics directly.
- LLMs should not invent analytical permissions.
- Reports should be constrained by verified evidence, facts, and bounded insights.
- Evaluation should compare generated reports with human references and with source-grounded factuality checks.
- Human review should be used to examine qualities that automatic metrics cannot reliably capture.

## Current Architectural Shape

The implemented workflow can be described as:

```text
Raw input files
    -> deterministic loading and benchmark field policy
    -> input structure profiling
    -> data profiling
    -> data understanding agent or fallback
    -> report contract and genre resolution
    -> orchestrator plan or deterministic event plan
    -> capability-aware analytical execution
    -> evidence ledger
    -> fact candidate generation
    -> fact verification
    -> fact ledger
    -> bounded insight synthesis and verification
    -> writer evidence pack
    -> narrative planning for event reports
    -> LLM writer or deterministic fallback writer
    -> writer support map validation
    -> factual audit
    -> genre and task-quality audit
    -> repair/revision when allowed
    -> final report and run artifacts
```

The most important design separation is:

```text
Data and analytics code:
    computes values and prepares evidence.

Agents:
    interpret, plan, verify, synthesize, and write.

Schemas:
    define the contracts between stages.

Auditors:
    decide whether prose is supported and whether it fulfils the task.

Evaluation subsystem:
    compares the system against baselines, references, source-grounded metrics,
    and human judgement packets.
```

## Main Contributions Implemented

1. Evidence-led report generation  
   The Writer receives a `WriterEvidencePack`, not free access to the raw world. It is asked to express supported facts and insights, with support IDs attached to sentences.

2. Strict typed artifacts  
   Pydantic models define data profiles, report specifications, investigation plans, evidence items, facts, insights, writer drafts, audit reports, run manifests, benchmark examples, metric observations, and human evaluation packets.

3. Genre-aware and structure-aware behavior  
   The system distinguishes data-science reports, dataset overviews, event reports, reference recaps, attribute verbalisation, focused table descriptions, and structured record verbalisation.

4. Generic event capabilities  
   Event reporting is not implemented as a basketball-only path. The system now has generic mechanisms for event outcomes, participant rankings, score progression, entity performance, team contrasts, and event sequence highlights.

5. Support-map validation and factual audit  
   Writer sentences must map to facts and insights. Numeric and entity support are checked. Unsupported causal, predictive, chronological, and genre-inappropriate claims are flagged.

6. Reference and source-grounded evaluation  
   The evaluation subsystem supports reference metrics such as BLEU, chrF, ROUGE, METEOR, BERTScore and PARENT, plus local/source-grounded factuality metrics such as HHEM and AlignScore where configured.

7. Raw baseline comparison  
   The system can run raw single-agent DeepSeek baselines against the same benchmark examples for comparison.

8. Human annotation materials  
   The project includes optimized human evaluation packets, blinded outputs, and paper-style factual error categories for volunteer annotation.

## Directory Overview

```text
table2text_pydanticai/
    README.md
    pyproject.toml
    .env.example
    CODEBASE_SNAPSHOT.md
    inputs/
    src/table2text/
    src/table2text/evaluation/
    scripts/
    tests/
    evaluation/config/
    evaluation/prepared/
    evaluation/generations/
    evaluation/results/
    evaluation/human/
    runs/
    runs_notebook/
```

The most important source code lives under `src/table2text`. The evaluation framework lives under `src/table2text/evaluation`. Experiment outputs live under `evaluation/results`, `evaluation/generations`, and `runs_notebook`.

## Root-Level Files

| File | Role | Dissertation comment |
| --- | --- | --- |
| `README.md` | Project introduction and installation notes. | This gives the high-level claim: a PydanticAI multi-agent Table2Text system designed to reduce hallucinations by separating deterministic analytics from LLM interpretation and writing. It is useful as a concise project abstract. |
| `pyproject.toml` | Python package metadata, dependencies, optional evaluation extras, CLI entry points, pytest and Ruff configuration. | This file shows the engineering packaging story. The core system depends on Pydantic, PydanticAI, pandas, numpy, scikit-learn, pyarrow and OpenPyXL. Evaluation tools are optional extras so the main workflow remains lighter than the full research evaluation stack. |
| `.env.example` | Environment template for model routing, token budgets, writer length controls, insight settings, DeepSeek, Ollama, DeepEval and raw baseline configuration. | This is central to reproducibility. It documents how the same code can be run locally with Ollama models or remotely with DeepSeek models, and how evaluation settings can be adjusted without editing code. |
| `.env` | Local private environment file. | This normally contains real API keys, active model choices and local experiment overrides. It should not be committed or included in dissertation appendices. When writing the methodology, cite `.env.example` instead of `.env`. |
| `.DS_Store` | macOS Finder metadata. | This has no research or runtime meaning and should be ignored. It is mentioned here only because it is physically present at the project root. |
| `apply_report_coverage_fix.py` | One-off helper script from an earlier coverage-recovery patch. | This is historical project scaffolding rather than a core runtime entry point. It reflects a previous maintenance step where report coverage recovery was applied or inspected. |
| `evaluation_manifest.json` | Evaluation manifest file. | This stores evaluation-level metadata for generated experiments. It is part of the reproducibility trail and helps connect runs, configs and result documents. |
| `CODEBASE_SNAPSHOT.md` | This snapshot document. | This file is the dissertation-facing architectural commentary. It should be updated whenever the project structure or research story changes substantially. |

## Core Package Files

### `src/table2text/__init__.py`

Public package exports.

This file exposes the main user-facing API, especially `Settings` and `Table2TextWorkflow`. In notebooks, most runs begin by importing these objects:

```python
from table2text import Settings, Table2TextWorkflow
```

Dissertation comment: this file represents the intended surface of the package. The project is not just a collection of scripts; it has a stable importable API.

### `src/table2text/__main__.py`

Module entry point for `python -m table2text`.

This file delegates to the CLI. It is small but important because it makes the package executable in a standard Python way.

### `src/table2text/config.py`

Settings and environment loading.

Important responsibilities:

- finds candidate `.env` files;
- parses key/value environment lines;
- exposes helper readers such as `env_bool`, `env_int`, `env_float`;
- defines the `Settings` dataclass;
- routes models for each agent;
- controls token budgets, analysis limits, writer limits, insight synthesis, fallback thresholds and report coverage settings.

Dissertation comment: this file is the reproducibility switchboard. It allows experiments to vary model allocation, output lengths, insight behavior and audit settings without changing the algorithmic code. This supports fair ablation and model-routing experiments.

### `src/table2text/schemas.py`

Strict Pydantic schema definitions for the whole workflow.

Major schema groups:

- report and task enums: `ReportGenre`, `CommunicationTask`, `OutputForm`, `ReportPerspective`;
- input semantics: `InputShape`, `SemanticRole`, `AnalyticalFunction`, `SemanticLevel`;
- capability vocabulary: `EvidenceCapability`, `CapabilityDefinition`;
- insight vocabulary: `InsightType`, `InsightContribution`, `InsightVerificationStatus`;
- audit and release enums: `AuditMode`, `AuditDecision`, `ReleaseStatus`, `Severity`;
- data structures: `DataProfile`, `TableProfile`, `ColumnProfile`;
- planning structures: `ReportSpecification`, `InvestigationTask`, `EvidenceQuery`, `ExecutionPlan`;
- evidence and fact structures: `EvidenceItem`, `EvidenceLedger`, `FactCandidate`, `VerifiedFact`, `FactLedger`;
- insight structures: `InsightCandidate`, `VerifiedInsight`, `InsightLedger`;
- writer structures: `WriterEvidencePack`, `WriterSentenceDraft`, `WriterAgentDraft`, `WriterOutput`;
- audit structures: `AuditAnnotation`, `RepairCandidate`, `AuditReport`;
- run structures: `RunManifest`, `PipelineResult`.

Dissertation comment: this is the contract layer. The strict models make each pipeline stage explicit and auditable. The schemas also embody the research design: claims are not just strings; they have permissions, provenance, support IDs, confidence values, and release decisions.

### `src/table2text/data.py`

Data loading, normalization and profiling.

Important responsibilities:

- expands input file paths;
- fingerprints input files for reproducible run IDs;
- loads CSV, Excel, JSON and JSONL-like structures;
- recognises benchmark-style structured records such as meaning representations, triples and highlighted table cells;
- converts nested JSON into usable tabular forms when appropriate;
- profiles columns for missingness, uniqueness, semantic type, numeric diagnostics and suspicious zeros;
- detects datetime-like columns and parse rates;
- creates `DataBundle` and `DataProfile` objects.

Dissertation comment: this file is where raw data becomes analyzable evidence substrate. It is deliberately deterministic because row counts, missingness, numeric summaries and structural conversions should not depend on LLM judgement.

### `src/table2text/structure.py`

Input-shape inspection and field filtering.

Important responsibilities:

- detects whether data is a flat table, nested record, event record, entity collection, input/reference pair or ambiguous structure;
- builds a structural catalog of paths and repeated fields;
- detects nested paths and heterogeneous rows;
- identifies probable input fields, reference fields and metadata fields;
- applies benchmark field policies so held-out references do not leak into operational prompts;
- combines structure profiles across multiple inputs.

Dissertation comment: this file directly addresses the problem discovered with basketball and benchmark examples. The system must understand what the input represents before it can decide whether to write a statistical report, an event recap, or a focused table verbalisation.

### `src/table2text/capabilities.py`

Generic capability registry and event/semantic evidence extraction.

Important responsibilities:

- declares and resolves available evidence capabilities;
- normalises semantic maps produced by agents or deterministic fallbacks;
- validates planned evidence queries against available structures;
- builds event evidence queries from semantic bindings;
- extracts event participants, event context, score progression, sequence highlights and entity performance;
- supports renamed event structures without hard-coded basketball or baseball-specific assumptions;
- executes semantic query evidence for structured records, triples, event records and participant collections.

Dissertation comment: this file is one of the core research upgrades. It moves the system away from domain-specific templates and toward reusable capabilities such as event outcome, ranking, entity performance, participant contrasts and sequence highlights. The goal is generality without allowing the Writer to invent meanings.

### `src/table2text/analytics.py`

Deterministic analytical execution.

Important responsibilities:

- executes planned analytical routes;
- creates evidence for dataset profile, missingness, duplicates and distribution summaries;
- computes correlations and group comparisons;
- handles predictive, forecasting and causal-feasibility analyses when explicitly supported;
- performs focused table analysis for ToTTo-like highlighted cells;
- verbalises structured records and triples for WebNLG, DART and E2E-style tasks;
- delegates event-specific extraction to generic capability evidence where appropriate;
- prioritises evidence for report-worthiness.

Dissertation comment: this file is the calculation engine. It is intentionally deterministic because the project argues that statistics and factual support should be computed by code, not improvised by language models. It is also where benchmark-specific input forms are converted into evidence without exposing references.

### `src/table2text/agents.py`

PydanticAI agent builders, prompts, validators and fallback logic.

The six main roles are implemented here:

1. Data Understanding Agent
2. Orchestrator Agent
3. Evidence Analyst Agent
4. Fact Verifier Agent
5. Writer Agent
6. Auditor Agent

Additional insight roles are also defined:

- Insight Synthesis Agent
- Insight Verifier Agent

Important responsibilities:

- builds model objects from model specifications such as `ollama:gemma3:12b` or `deepseek:deepseek-v4-flash`;
- configures structured output mode;
- defines agent prompts;
- validates LLM outputs before they enter later stages;
- rejects unsupported insight candidates;
- enforces safe causal, predictive and analytical permissions;
- recovers or materialises insight ledgers;
- validates writer grounding and support IDs;
- builds deterministic fallbacks for understanding, planning, fact candidates and audits.

Dissertation comment: this file contains the language-model behavior of the system. It is large because it holds both prompts and validation logic. Methodologically, it demonstrates that LLMs are used for interpretation and realisation, while typed validators and deterministic fallbacks prevent many unsupported outputs from moving forward.

### `src/table2text/audit.py`

Factual validation, report materialisation, fallback writing, repair and release decisions.

Important responsibilities:

- splits generated Markdown into factual sentences;
- checks numeric support against evidence and facts;
- checks entity support and mapped fact IDs;
- builds profile support records from deterministic data profiles;
- creates deterministic fact candidates from evidence when LLM stages are thin;
- finalises fact ledgers;
- selects priority facts and insights for the Writer;
- builds writer evidence packs;
- validates Writer output and support maps;
- provides deterministic fallback writers for focused table, structured record, event and generic reports;
- assesses report component coverage and genre quality;
- flags causal overclaims, unsupported chronology, unsupported predictions, misleading statements and guardrail leakage;
- merges audit proposals;
- applies safe repair proposals;
- decides final release status.

Dissertation comment: this is the main safety and accountability layer. It is also the largest file because many guardrails live here. The dissertation can describe it as the controller and audit layer that turns evidence into permissioned report content and prevents unsupported prose from being released as approved.

### `src/table2text/narrative.py`

Event narrative planning.

Important responsibilities:

- maps event facts and insights into narrative slots;
- distinguishes result, context, sequence, leading performances, participant contrasts and limitations;
- down-prioritises low-value event facts;
- builds a `NarrativePlan` for event reports before writing;
- helps the Writer produce a coherent event recap rather than a flat list of rankings.

Dissertation comment: this file addresses the key qualitative gap found during SportSett and MLB testing: a report can be factually grounded but still read like a data dump. The narrative layer provides structure without hard-coding a specific sport or forcing deterministic prose.

### `src/table2text/workflow.py`

End-to-end pipeline orchestration.

Important responsibilities:

- resolves report genre and task contract from user request, experiment config and structure profile;
- builds compact prompt payloads;
- decides when a deterministic event plan is safer than a generic LLM plan;
- runs each agent stage in order;
- stores every artifact in a run directory;
- handles async and sync workflow execution;
- builds and saves evidence ledgers, fact ledgers, insight ledgers, writer drafts, audit reports and final outputs;
- applies writer quality revision and final audit decisions;
- returns a `PipelineResult`.

Dissertation comment: this is the executable embodiment of the architecture. It is useful for explaining the pipeline as an empirical system: every run produces artifacts that can be inspected, compared and audited.

### `src/table2text/cli.py`

Command-line interface for running the main workflow.

Important responsibilities:

- parses input paths, request text and output directory;
- builds `Settings`;
- runs the workflow;
- prints run ID, release status and report path.

Dissertation comment: this file shows that the system is usable outside notebooks. It provides a reproducible command-line route for running experiments.

### `src/table2text/evaluation_backends.py`

Evaluation-time generation backends, especially raw single-LLM baselines.

Important responsibilities:

- builds a prompt for raw DeepSeek baseline generation;
- supports generic and task-aware raw baseline styles;
- reads model and prompt settings from variant config or environment;
- calls DeepSeek-compatible APIs;
- returns generated text to the evaluation harness as a benchmark `GenerationRecord`.

Dissertation comment: this file matters for fair comparison. It allows the dissertation to compare the multi-agent system with a raw LLM baseline using the same source data and references.

## Evaluation Package Files

### `src/table2text/evaluation/__init__.py`

Public exports for notebook and script evaluation.

Dissertation comment: this file makes evaluation helpers easy to import in notebooks, which became the main experiment interface during development.

### `src/table2text/evaluation/models.py`

Typed models for benchmark evaluation.

Important structures:

- `DatasetConfig`;
- `BenchmarkExample`;
- `VariantConfig`;
- `GenerationRecord`;
- `MetricObservation`;
- `DeepEvalObservation`;
- `HumanEvaluationPair`;
- `HumanJudgement`;
- `ReferenceMetricConfig`;
- `DeepEvalConfig`;
- `ExperimentConfig`.

Dissertation comment: this file mirrors the core system's typed-artifact approach in the evaluation layer. It makes datasets, generations, metrics and human judgements reproducible records rather than ad hoc notebook variables.

### `src/table2text/evaluation/datasets.py`

Dataset preparation and normalization.

Important responsibilities:

- defines default benchmark dataset configurations;
- loads local and Hugging Face datasets where available;
- normalizes E2E, ToTTo, WebNLG, DART, SportSett, MLB and other examples into `BenchmarkExample`;
- extracts references without leaking them into source payloads;
- builds source text and PARENT tables;
- writes and reads prepared JSONL examples;
- deterministically samples examples.

Dissertation comment: this file is central to methodology. It ensures that different benchmark datasets can be fed into the same pipeline while preserving source/reference separation.

### `src/table2text/evaluation/generation.py`

Generation runner for evaluation experiments.

Important responsibilities:

- loads generation variants;
- materialises benchmark inputs into temporary files;
- maps benchmark task families to workflow report genres;
- runs the Table2Text workflow;
- runs callable baselines and command baselines;
- supports async notebook execution;
- supports resume behavior;
- writes JSONL generation records.

Dissertation comment: this file is the experimental runner. It lets the project compare variants such as full system, raw DeepSeek baseline, ablated systems and precomputed outputs under a common interface.

### `src/table2text/evaluation/reference_metrics.py`

Reference and source-grounded metric registry.

Important responsibilities:

- computes lexical/reference metrics such as BLEU, chrF, TER, ROUGE and METEOR;
- computes semantic metrics such as BERTScore where dependencies are available;
- computes PARENT for source-table faithfulness;
- supports HHEM sentence-level hallucination/factuality scoring;
- supports AlignScore through a worker process;
- normalizes event source context for source-grounded factuality metrics;
- writes metric observations to JSONL.

Dissertation comment: this file supports the quantitative part of the dissertation. It also encodes the metric story: lexical metrics are useful but limited, while semantic and source-grounded metrics better reflect the project's factuality goals.

### `src/table2text/evaluation/external_factuality.py`

Local factuality model helpers.

Important responsibilities:

- splits generated reports into sentences;
- compacts source context for factuality models;
- wraps HHEM evaluation;
- summarizes sentence-level support scores.

Dissertation comment: this file allows local factuality checks without depending only on API-based judges. It helps separate factual support from surface similarity to references.

### `src/table2text/evaluation/alignscore_client.py`

Client wrapper for AlignScore scoring.

Important responsibilities:

- launches or calls the AlignScore worker;
- sends source and generated text;
- receives scalar factuality/alignment scores.

Dissertation comment: AlignScore gives another source-grounded signal. It should be treated as supplementary because setup and model availability can vary.

### `src/table2text/evaluation/deepeval_metrics.py`

DeepEval judge integration.

Important responsibilities:

- builds judge inputs from source, generated output and optional references;
- configures DeepSeek/OpenAI-compatible judges through environment variables;
- runs faithfulness, summarization and reference-adequacy style metrics where enabled;
- supports timeout and retry configuration;
- writes `DeepEvalObservation` records.

Dissertation comment: this file supports LLM-as-judge evaluation. In the dissertation, DeepEval results should be framed as expert-like automated judgements, not objective ground truth.

### `src/table2text/evaluation/diagnostics.py`

Lightweight generation diagnostics.

Important responsibilities:

- counts sentences;
- extracts numbers;
- computes simple ratios and warning signals;
- writes diagnostic tables.

Dissertation comment: this file helps explain outputs before metric scoring. It is useful for spotting empty reports, missing numbers or suspiciously short outputs.

### `src/table2text/evaluation/human_evaluation.py`

Human evaluation packet generation and analysis.

Important responsibilities:

- creates blinded output pairs;
- exports reviewer packets;
- loads human judgements;
- decodes scores;
- computes inter-rater agreement summaries.

Dissertation comment: this file operationalises human participation. It supports evaluating factuality, usefulness, conciseness and preference in ways automatic metrics cannot fully capture.

### `src/table2text/evaluation/statistics.py`

Metric aggregation and statistical comparison.

Important responsibilities:

- reads metric observations;
- collapses judge repetitions;
- computes descriptive summaries;
- computes macro dataset summaries;
- runs paired bootstrap comparisons;
- computes metric correlations;
- summarizes runtime and cost signals.

Dissertation comment: this file is the analysis layer for evaluation results. It helps turn many JSONL metric records into tables that support a defensible experimental story.

### `src/table2text/evaluation/notebook.py`

Notebook-friendly wrappers.

Important responsibilities:

- exposes `default_paths`;
- initializes evaluation folders;
- prepares examples;
- generates reports;
- scores reference metrics;
- scores DeepEval metrics;
- loads diagnostics and aggregate tables into pandas DataFrames.

Dissertation comment: this file exists because most experiments were run interactively in notebooks. It provides a controlled notebook API rather than copying evaluation logic into notebook cells.

### `src/table2text/evaluation/cli.py`

Command-line interface for the evaluation subsystem.

Important responsibilities:

- writes default dataset, variant and metric configs;
- prepares datasets;
- generates outputs;
- scores reference metrics;
- scores DeepEval metrics;
- writes diagnostics;
- exports and analyses human packets;
- aggregates results.

Dissertation comment: this file makes the evaluation reproducible outside notebooks. It is useful for describing how experiments could be rerun by another researcher.

## Scripts

### `scripts/alignscore_worker.py`

Worker process for AlignScore.

Important responsibilities:

- loads AlignScore model dependencies;
- accepts source/output pairs;
- returns alignment scores;
- supports local/offline Hugging Face behavior.

Dissertation comment: this script keeps optional heavyweight AlignScore dependencies outside the core runtime. It also makes failures easier to isolate.

## Test Suite

### `tests/test_smoke.py`

Broad regression and safety tests for the main workflow.

Major themes:

- data profiling behavior;
- zero-value and constant-column handling;
- generic dataset report requirements;
- writer support-map validation;
- report coverage recovery;
- insight synthesis and verification rules;
- causal and predictive overclaim rejection;
- deterministic fallback behavior;
- event reference quarantine;
- nested event handling;
- writer payload construction;
- quality gates and release status behavior.

Dissertation comment: this file demonstrates that the system's safety claims are backed by regression tests, not only by prompts. It is especially important for showing that factuality constraints are implemented as software checks.

### `tests/test_semantic_event_pipeline.py`

Regression tests for generic event understanding and reporting.

Major themes:

- semantic map validation;
- event capability extraction;
- participant rankings;
- score progression;
- event sequence highlights;
- event report content requirements;
- rejection of flat modelling discussion for event reports;
- prevention of unsupported chronology and participation substitution;
- narrative slot ordering;
- renamed event structures;
- reference isolation.

Dissertation comment: this file is the strongest evidence that the event-reporting upgrade is not simply basketball hard-coding. It tests generic event structures and renamed fields.

### `tests/test_reference_evaluation.py`

Regression tests for benchmark preparation and evaluation.

Major themes:

- E2E/WebNLG/DART normalization;
- raw baseline prompt reference exclusion;
- generic prompt behavior;
- SportSett event source context;
- ToTTo highlighted table materialisation;
- focused table one-sentence contracts;
- PARENT/reference metric scoring;
- HHEM and AlignScore availability behavior;
- human pair ordering;
- notebook helper execution.

Dissertation comment: this file supports the validity of the evaluation setup. It is especially important because reference leakage would invalidate comparisons against raw baselines.

## Input Data Files

| File | Description/comment |
| --- | --- |
| `inputs/weatherHistory.csv` | Weather observations used for tabular descriptive, correlation and group-comparison reports. It is useful for testing classic data-science reporting on a large flat CSV. |
| `inputs/full_format_recipes.json` | Nested recipe dataset used to test missingness, duplicates, nutritional correlations and JSON loading. It exposes how the system handles nested but primarily analytical data. |
| `inputs/heart_disease_uci.csv` | Medical-style tabular dataset used for careful descriptive reporting and limitation language. This kind of input is useful for testing conservative wording in higher-risk domains. |
| `inputs/basketball_data.json` | Local basketball event example used during event-report development. It exposed the need to distinguish single-event reporting from generic dataset-quality reporting. |
| `inputs/dftRoadSafety_Accidents_2016.csv` | UK road-safety accident table used for broader tabular evaluation ideas. |
| `inputs/Cas.csv` | Road-safety casualty table intended to be paired with accident and vehicle files in multi-file road-safety experiments. |
| `inputs/Veh.csv` | Road-safety vehicle table intended for multi-file road-safety experiments. |
| `inputs/MakeModel2016.csv` | Vehicle make/model reference table for road-safety experiments. |

## Evaluation Configuration Files

Stable configuration files:

| File | Description/comment |
| --- | --- |
| `evaluation/config/datasets.json` | Dataset registry for benchmark preparation. It defines which datasets can be prepared, where fields come from, how references are extracted, and what task family each dataset belongs to. |
| `evaluation/config/variants.json` | Default generation variants. It normally includes the full system and baseline definitions. Variants can override settings or call an external baseline backend. |
| `evaluation/config/variants_ablation.json` | Ablation-specific generation variant definitions. Used to test the contribution of system components. |
| `evaluation/config/metrics.json` | Default metric configuration. Defines enabled reference metrics, factuality metrics, source-grounded context behavior and DeepEval settings. |
| `evaluation/config/metrics_reference_similarity.json` | Metric profile focused on similarity to human references. Useful when comparing generated text to benchmark references. |
| `evaluation/config/metrics_source_grounded.json` | Metric profile focused on source-grounded factuality rather than reference similarity. |
| `evaluation/config/metrics_ablation_sportsett_4934.json` | Metric configuration for the SportSett example 4934 ablation study. |

Generated experiment configuration files:

The directory also contains many timestamped `metrics_*` and `variants_*` files. These were produced during notebook experiments, smoke tests, five-dataset runs, raw generic baseline runs, ToTTo/WebNLG fixes, SportSett runs and ablation runs.

Dissertation comment: these files are experiment provenance. They show exactly which variants and metric profiles were used for specific runs. They should not be treated as core source files, but they are useful for audit trails and for reconstructing evaluation tables.

Important generated configuration families:

- `metrics_four_dataset_logged_comparison_*`
- `variants_four_dataset_logged_comparison_*`
- `metrics_five_dataset_five_each_comparison_*`
- `variants_five_dataset_five_each_comparison_*`
- `metrics_five_dataset_five_each_raw_generic_flash_*`
- `variants_five_dataset_five_each_raw_generic_flash_*`
- `metrics_generic_only_sportsett_basketball_4934_*`
- `variants_sportsett_basketball_4934_*`
- `variants_totto_*`
- `variants_e2e_nlg_*`
- `variants_raw_deepseek_v4_flash.json`
- `variants_raw_deepseek_v4_pro.json`

## Evaluation Prepared, Generation and Result Artifacts

The project contains generated artifacts under:

```text
evaluation/prepared/
evaluation/generations/
evaluation/results/
runs/
runs_notebook/
```

These are not source code. They are experiment outputs.

Typical run artifacts include:

- materialised benchmark input files;
- `pipeline_result.json`;
- `final_report.md`;
- `run_manifest.json`;
- `01_data_profile.json`;
- `02_data_understanding.json`;
- `03_evidence_queries.json`;
- `06_evidence_ledger.json`;
- `07_fact_ledger.json`;
- `08_writer_evidence_pack.json`;
- `09_writer_raw_report.md`;
- `09_writer_support_map.json`;
- `10_writer_quality_revision_candidate.md`;
- `final_audit.json`;
- generation JSONL files;
- metric JSONL files.

Dissertation comment: these artifacts are a major strength of the project. They make the pipeline inspectable. When a report is weak, the failure can be traced to a specific stage: input interpretation, evidence extraction, fact verification, insight synthesis, writer selection, audit, or repair.

## Major Evaluation Result Documents

| File | Description/comment |
| --- | --- |
| `evaluation/results/five_dataset_results_appendix.md` | Full evaluation appendix covering five datasets, with structured source data, references, system outputs, raw baseline outputs and metric tables. This is one of the main dissertation evidence documents. |
| `evaluation/results/five_dataset_results_appendix.html` | HTML rendering of the full evaluation appendix. |
| `evaluation/results/five_dataset_results_appendix.pdf` | PDF version of the evaluation appendix. |
| `evaluation/results/five_dataset_results_appendix_designed.pdf` | Designed/styled PDF version for readability. |
| `evaluation/results/five_dataset_results_appendix_full_content.pdf` | Full-content PDF designed to preserve detailed structured source sections. |
| `evaluation/results/five_dataset_five_each_raw_generic_flash_20260805_181001_summary.md` | Summary for five datasets with five examples each and raw generic Flash baseline comparison. |
| `evaluation/results/sportsett_4934_ablation_story.md` | Narrative write-up of the SportSett 4934 ablation study. |
| `evaluation/ABLATION_STUDY_SPORTSETT_4934.md` | Main ablation-study document for SportSett example 4934. |
| `evaluation/results/four_dataset_logged_comparison_20260803_013629_evaluation_overview.md` | Earlier four-dataset evaluation overview. Useful as historical context. |
| `evaluation/results/four_dataset_logged_comparison_20260803_013629_deep_dive_findings.md` | Deep-dive notes from earlier evaluation runs. Useful for explaining the evolution of fixes. |
| `evaluation/results/sportsett_basketball_4934_evaluation_overview.md` | Focused evaluation overview for SportSett basketball example 4934. |

## Human Evaluation Materials

| File | Description/comment |
| --- | --- |
| `evaluation/human_annotation_questionnaire.md` | General questionnaire draft for human participation. |
| `evaluation/human_annotation_questions_final.md` | Final question set for human annotation. |
| `evaluation/human_annotation_questions_optimized.md` | Optimized question set after refining dataset selection and annotation goals. |
| `evaluation/human_annotation_study_plan.md` | Study plan explaining how volunteers should be used and what judgements they provide. |
| `evaluation/human_participation_optimized_plan.md` | Optimized plan for selecting good and bad outputs, avoiding unsuitable deterministic fallback examples, and collecting useful human judgements. |
| `evaluation/human/human_annotation_packets_preview.md` | Preview of annotation packets. |
| `evaluation/human/human_annotation_packets_blinded.jsonl` | Blinded pair data for annotation. |
| `evaluation/human/human_annotation_packets_for_forms.csv` | Form-friendly export of human annotation packets. |
| `evaluation/human/human_annotation_answer_key_private.jsonl` | Private answer key mapping blinded outputs to systems. This should not be shown to annotators. |
| `evaluation/human/human_annotation_diagnostic_subset_preview.md` | Preview for a smaller diagnostic subset. |
| `evaluation/human/human_annotation_diagnostic_subset_blinded.jsonl` | Blinded diagnostic subset. |

There is also an optimized human annotation packet set under `evaluation/human/optimized/`. It includes a preview Markdown file and PDF packet designed for discussion with the supervisor.

Optimized human annotation files:

| File | Description/comment |
| --- | --- |
| `evaluation/human/optimized/optimized_human_annotation_packets_preview.md` | Human-readable preview of the optimized annotation packets. |
| `evaluation/human/optimized/optimized_human_annotation_packets_preview.pdf` | PDF rendering of the optimized packet preview for sharing with the supervisor or reviewers. |
| `evaluation/human/optimized/optimized_human_annotation_packets_blinded.jsonl` | Blinded machine-readable packet data. |
| `evaluation/human/optimized/optimized_human_annotation_packets_for_forms.csv` | Form-friendly export for volunteer annotation tools. |
| `evaluation/human/optimized/optimized_human_annotation_answer_key_private.jsonl` | Private key connecting blinded outputs to system identity. It should not be shown to annotators. |
| `evaluation/human/optimized/optimized_selection_manifest.md` | Selection rationale for the optimized packet set, including why certain examples were chosen or excluded. |

Dissertation comment: the human evaluation materials are important because automatic metrics do not fully measure whether an output is useful, well-structured, faithful, concise or preferable to a baseline. The optimized packet design supports targeted annotation instead of asking volunteers vague questions.

## Evaluation Metrics Shortlist

The project uses many metrics, but the dissertation story should focus on a smaller set.

Most useful metrics:

| Metric | Class | Why it matters |
| --- | --- | --- |
| BERTScore F1 | Semantic similarity | Captures semantic overlap with references better than exact n-gram matching. |
| chrF | Character-level lexical similarity | Useful for short references and morphology-sensitive overlap. |
| ROUGE-L | Sequence/summary overlap | Measures longest common subsequence similarity and is familiar in NLG evaluation. |
| METEOR | Alignment-aware lexical/semantic overlap | More forgiving than BLEU and useful for paraphrased outputs. |
| PARENT F1 | Table-to-text source faithfulness | Important because the task is structured-data-to-text, not generic summarization. |
| HHEM unsupported sentence rate | Source-grounded factuality | Helps identify sentences that appear unsupported by source context. |
| HHEM mean support | Source-grounded factuality | Gives a continuous support signal for generated sentences. |
| AlignScore | Source-output alignment | Provides an additional local factuality/alignment signal when available. |
| DeepEval faithfulness/reference adequacy | LLM-as-judge | Useful as a qualitative automated judge, especially when source and reference context are rich. |

Metrics to de-emphasize:

| Metric | Why it is less central |
| --- | --- |
| BLEU | Too sensitive to wording and weak for single-reference or paraphrased outputs. |
| TER | Useful for edit distance but less aligned with factual usefulness. |
| ROUGE-1 and ROUGE-2 alone | Helpful as supporting evidence but too lexical to carry the main story. |
| Corpus-only aggregates without examples | Can hide dataset-specific behavior and failure modes. |

Dissertation comment: the metric story should not be "one score proves the system is better." It should be that different metric classes reveal different aspects: semantic similarity, reference overlap, source faithfulness, factual support and human preference.

## Current Model and Runtime Configuration Story

The system supports two main model routes:

1. Local Ollama models  
   Useful for development, cheaper runs and local privacy.

2. DeepSeek models  
   Useful for stronger Writer/Auditor behavior and raw baseline comparison.

The `.env.example` currently documents:

- local default routing with Gemma through Ollama;
- DeepSeek model routing for all agents;
- stronger Writer/Auditor routing with `deepseek-v4-pro`;
- DeepEval judge routing through DeepSeek;
- raw baseline settings;
- writer word targets and optional hard ceilings;
- insight synthesis controls;
- deterministic fact coverage recovery thresholds.

Dissertation comment: model routing is part of the experimental design. The project can ask which stages need stronger models and which can remain local or cheaper without major output loss.

## Run Artifact Naming and Interpretation

Notebook runs usually write outputs into:

```text
runs_notebook/<timestamp>_<fingerprint>/
```

Evaluation runs usually write outputs into:

```text
evaluation/generations/<experiment>_runs/<variant>/<dataset>/<run_id>/
```

Each run directory should be read as a trace of the pipeline. For example:

- if `writer_mode` is `llm_writer`, the LLM Writer produced a materialised output that passed validation;
- if `writer_mode` is `deterministic_fallback`, the deterministic fallback writer produced the final text after an upstream or materialisation failure;
- `final_audit.decision` explains factual audit outcome;
- `release_status` explains whether the output was approved, approved with warnings or required human review;
- `insight_fallback_reason` indicates why insight synthesis was empty or degraded.

## Important Design Concepts

### Evidence

Evidence is a deterministic or controlled analytical observation that can support one or more claims. Examples:

- a row count;
- a missingness rate;
- a correlation coefficient;
- a group difference;
- an event result;
- a player ranking;
- a score-changing sequence highlight;
- a highlighted table-cell proposition.

Evidence is not the final report. It is the support substrate.

### Fact

A fact is a verified, reportable statement derived from evidence. It should have:

- a fact ID;
- evidence IDs;
- claim permissions;
- numbers and entities supported by evidence;
- a component or narrative role.

### Insight

An insight is a bounded synthesis across one or more facts. It can relate facts, contrast them, or explain their analytical relevance without creating unsupported causal, predictive or historical claims.

For example:

- Safe insight: "Washington won despite Los Angeles having the free-throw advantage; Washington's larger advantages were in made field goals and made three-pointers."
- Unsafe insight: "Washington won because they shot better." This is causal unless the evidence explicitly supports causation.

### Report Contract

The report contract defines the expected output type:

- data-science report;
- dataset overview;
- event report;
- reference recap;
- focused table answer;
- structured record verbalisation;
- executive summary or custom form.

The contract controls content slots and prohibited claim types.

### Narrative Plan

The narrative plan is used mostly for event reports. It organizes facts into:

- result;
- context;
- score progression or sequence;
- leading performances;
- participant contrasts;
- limitations.

The plan should guide prose structure without forcing deterministic writing.

### Audit

The audit checks factual and quality conditions:

- unsupported numbers;
- unsupported entities;
- unsupported causal wording;
- unsupported chronology;
- missing required supported content;
- genre mismatch;
- low-usefulness output;
- over-repeated caveats;
- unsupported hypotheses.

## Known Strengths

1. The system is highly inspectable.  
   Each stage leaves artifacts, making debugging and dissertation analysis possible.

2. Source/reference separation is explicit.  
   Benchmark references are held out from operational prompts.

3. The event-reporting system is now generic.  
   It has been tested on basketball and MLB-style nested event records.

4. The evaluation layer is richer than simple BLEU scoring.  
   It supports reference metrics, source-grounded factuality, DeepEval and human evaluation.

5. The project has a clear ablation path.  
   Variants can disable or alter stages, allowing component-level analysis.

## Known Limitations and Technical Debt

1. Several files are very large.  
   `audit.py`, `capabilities.py`, `analytics.py`, `agents.py` and `workflow.py` are monolithic. This is acceptable for a research prototype but should be refactored in future work.

2. Generated artifacts are numerous.  
   The evaluation process creates many timestamped configs and results. These are useful for provenance but make the repository visually noisy.

3. Some automatic metrics are imperfect for this task.  
   Human references may omit correct facts, and generated reports may be source-faithful but lexically different. This can depress BLEU/ROUGE even when the report is useful.

4. LLM-as-judge metrics require careful framing.  
   DeepEval can be helpful but depends on judge model, prompt, timeout and repetition settings.

5. Event reports remain sensitive to content prioritisation.  
   The system may produce very factual outputs that still need better narration or salience selection.

6. Deterministic fallback is not inherently bad but must be reported honestly.  
   It can produce safe outputs, but the dissertation should distinguish LLM-written and fallback-written reports.

7. Worktree state is active.  
   At snapshot time, several source and test files are modified and many experiment configs are untracked. Commit boundaries should be used when finalising dissertation experiments.

## Source File Size Snapshot

Approximate line counts from the current source tree:

| File | Lines | Comment |
| --- | ---: | --- |
| `src/table2text/audit.py` | 9890 | Largest controller, validation, fallback and audit file. |
| `src/table2text/capabilities.py` | 5501 | Generic capability and event evidence extraction logic. |
| `src/table2text/analytics.py` | 4975 | Deterministic analytical execution and benchmark verbalisation. |
| `src/table2text/agents.py` | 4661 | Agent builders, prompts, validators and fallback agent logic. |
| `src/table2text/workflow.py` | 4194 | End-to-end pipeline orchestration. |
| `src/table2text/schemas.py` | 1268 | Typed contracts for the system. |
| `src/table2text/data.py` | 960 | Loading and profiling. |
| `src/table2text/structure.py` | 650 | Input-shape inspection and field filtering. |
| `src/table2text/evaluation/reference_metrics.py` | 1133 | Reference/source-grounded metric registry. |
| `src/table2text/evaluation/datasets.py` | 869 | Benchmark preparation and normalization. |
| `src/table2text/evaluation/generation.py` | 718 | Evaluation generation runner. |
| `src/table2text/evaluation/deepeval_metrics.py` | 452 | DeepEval judge integration. |
| `src/table2text/narrative.py` | 401 | Event narrative planning. |
| `src/table2text/config.py` | 425 | Settings and environment management. |
| `src/table2text/evaluation/statistics.py` | 305 | Metric aggregation and comparison. |
| `src/table2text/evaluation/external_factuality.py` | 296 | HHEM/local factuality helpers. |
| `src/table2text/evaluation/human_evaluation.py` | 252 | Human evaluation packet and judgement helpers. |
| `src/table2text/evaluation_backends.py` | 219 | Raw baseline generation backend. |
| `src/table2text/evaluation/notebook.py` | 196 | Notebook helper API. |
| `src/table2text/cli.py` | 178 | Main workflow CLI. |
| `src/table2text/evaluation/cli.py` | 359 | Evaluation CLI. |
| `src/table2text/evaluation/alignscore_client.py` | 145 | AlignScore worker client. |
| `src/table2text/evaluation/diagnostics.py` | 115 | Lightweight diagnostics. |
| `src/table2text/evaluation/__init__.py` | 50 | Evaluation exports. |
| `src/table2text/__init__.py` | 7 | Package exports. |
| `src/table2text/__main__.py` | 4 | Module entry point. |

## Suggested Dissertation Structure Using This Codebase

### Methodology chapter

Use these files:

- `schemas.py` to explain typed artifacts;
- `workflow.py` to explain the pipeline;
- `data.py` and `structure.py` to explain input handling;
- `capabilities.py` and `analytics.py` to explain evidence generation;
- `agents.py` to explain LLM roles;
- `audit.py` to explain factual controls;
- `narrative.py` to explain event-report narration.

### Evaluation chapter

Use these files:

- `evaluation/datasets.py` for benchmark preparation;
- `evaluation/generation.py` for generation variants;
- `evaluation/reference_metrics.py` for metric registry;
- `evaluation/deepeval_metrics.py` for LLM-as-judge evaluation;
- `evaluation/statistics.py` for aggregation;
- `evaluation/human_evaluation.py` for human annotation;
- `evaluation/results/five_dataset_results_appendix.md` for concrete examples.

### Results chapter

Use:

- five-dataset appendix;
- SportSett 4934 ablation story;
- raw generic baseline comparisons;
- DeepEval/source-grounded metrics;
- human annotation packet design.

### Discussion chapter

Emphasize:

- the system improves controllability and auditability;
- automatic metrics do not perfectly reward faithful, differently worded outputs;
- genre and narrative planning are necessary for event reports;
- deterministic evidence is valuable but cannot replace human judgement about communicative quality;
- future work should refactor large modules and expand human evaluation.

## Recommended Future Refactors

These are not required for the dissertation but are useful future engineering improvements:

1. Split `audit.py` into:
   - support checking;
   - writer materialisation;
   - fallback writers;
   - quality assessment;
   - repair logic.

2. Split `capabilities.py` into:
   - registry and availability;
   - semantic map validation;
   - event extraction;
   - sequence extraction;
   - generic query execution.

3. Split `analytics.py` into:
   - tabular analytics;
   - focused table analysis;
   - structured record verbalisation;
   - predictive/forecasting analysis.

4. Move prompt text out of `agents.py` into versioned prompt modules.

5. Add experiment manifests that bundle:
   - variant config;
   - metric config;
   - generation file;
   - result file;
   - model configuration;
   - commit hash.

6. Reduce generated config clutter by storing per-run configs under experiment-specific folders.

## Practical Commands

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Install evaluation extras as needed:

```bash
pip install -e ".[evaluation]"
pip install -e ".[evaluation-deepeval]"
pip install -e ".[evaluation-hhem]"
```

Run tests:

```bash
pytest
```

Run CLI:

```bash
table2text inputs/weatherHistory.csv --request "Understand the dataset and report its strongest findings."
```

Use notebook helpers:

```python
from pathlib import Path
from table2text.evaluation import default_paths, generate_reports_for_notebook

project_dir = Path("/Users/realgobs/Documents/MScproject/table2text_pydanticai")
paths = default_paths(project_dir)
```

## Final Dissertation Framing

This codebase should be presented as a research prototype with a strong emphasis on control, traceability and evaluation. Its novelty is not that it simply prompts a stronger LLM. Its novelty is the layered architecture:

```text
Input interpretation
    + deterministic evidence
    + typed claim permissions
    + verified facts
    + bounded insights
    + genre-aware writing
    + factual audit
    + metric and human evaluation
```

The project is strongest when the dissertation treats the system as an auditable pipeline and uses concrete run artifacts to show where it succeeds, where it fails, and how each design choice affects factuality and usefulness.
