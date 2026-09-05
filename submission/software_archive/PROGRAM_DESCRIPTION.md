# MScProject: Evidence-Grounded Table-to-Text Generation

**Author:** Tanatswa Mapfumo | **Software:** `table2text-pydanticai` | **Version:** 0.1.0

## Purpose

This software converts structured tabular data into natural-language reports
while reducing unsupported factual claims. It was developed for an MSc project
investigating whether an evidence-grounded multi-agent workflow can improve
table-to-text generation over a direct single-model baseline. The system does
not claim to eliminate hallucinations; it makes evidence provenance, claim
verification, sentence support, and release decisions explicit and auditable.

## Program Operation

The input may be CSV, JSON, spreadsheet, Parquet, or Arrow data together with a
natural-language reporting request. Deterministic code loads and profiles the
data, interprets supported analytical capabilities, executes analyses, and
records evidence identifiers. Six semantic roles then cooperate: Data
Understanding interprets structure and field meaning; the Orchestrator freezes
a capability-aware plan; the Evidence Analyst proposes grounded claims and
bounded insights; the Claim Verifier checks support and permissions; the Writer
realises verified content under a report contract; and the Factual Auditor
checks factual support and task fulfilment. Deterministic validators retain
control of provenance, numerical permissions, support maps, and release gates.

The workflow supports dataset overviews, data-science reports, focused table
descriptions, attribute and triple verbalisation, and event reports. It can run
with configured LLM services or in a deterministic fallback mode that requires
no API key. Each run creates a timestamped artifact directory containing the
interpreted structure, execution plan, evidence and fact ledgers, writer output,
audit records, final report, and machine-readable result.

## Interfaces and Evaluation

The installable wheel exposes `table2text` for generation and
`table2text-evaluate` for dataset preparation, report generation, automatic
metrics, diagnostics, human-study export, and aggregation. A Python API and
research notebooks are also supplied. Automated tests cover loading,
capability selection, semantic event handling, evidence validation, writing,
auditing, and reference-based evaluation.

The included protected evaluation evidence contains 25 unseen examples across
five heterogeneous datasets, paired Full System and Baseline outputs,
reference-alignment and source-grounded metrics, model-input audits, and
structured judge results. Held-out references are isolated from generation.

## Deliverables

The submission contains maintained source and test programs, configuration,
notebooks, curated data/results, full program listings, installation and build
instructions, exact dependency versions, a deterministic demonstration, and a
platform-independent Python wheel. Credentials, downloaded caches, local model
weights, virtual environments, and transient development runs are intentionally
excluded.
