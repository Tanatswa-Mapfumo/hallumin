# Dissertation Notes: SportSett 4934 Full Workflow vs Raw DeepSeek v4-pro

## Context

This note records the August 11, 2026 SportSett Basketball example `4934`
comparison between the full Table2Text workflow and a raw single-call DeepSeek
v4-pro baseline.

Dataset and example:

| Field | Value |
|---|---|
| Dataset | `sportsett_basketball` |
| Example ID | `4934` |
| Task family | `event_report` |
| Output mode | `multi_paragraph_report` |
| Event | Philadelphia 76ers vs Memphis Grizzlies |
| Final score | Philadelphia 76ers 103, Memphis Grizzlies 95 |

Artifacts:

| Artifact | Path |
|---|---|
| Generations | `evaluation/generations/sportsett_basketball_4934_fast_compare_generations.jsonl` |
| Metrics | `evaluation/results/sportsett_basketball_4934_fast_reference_metrics_fixed.jsonl` |
| Full workflow run | `evaluation/generations/sportsett_basketball_4934_fast_compare_runs/full_system_fast/sportsett_basketball/20260811T202300Z_6fbc97c364/pipeline_result.json` |

## Model Configuration

Although the variant is named `full_system_fast`, the saved manifest shows that
all six workflow roles used DeepSeek v4-pro in this run.

| Component | Model |
|---|---|
| Data Understanding | `deepseek:deepseek-v4-pro` |
| Orchestrator | `deepseek:deepseek-v4-pro` |
| Evidence Analyst | `deepseek:deepseek-v4-pro` |
| Fact Verifier | `deepseek:deepseek-v4-pro` |
| Writer | `deepseek:deepseek-v4-pro` |
| Auditor | `deepseek:deepseek-v4-pro` |
| Raw baseline | `deepseek-v4-pro` |

This means the comparison is best interpreted as:

```text
full architecture using v4-pro
vs
raw single-call v4-pro
```

It is therefore an architecture comparison with the same model family and
capability level, not a cheap-model workflow against a stronger raw baseline.

## Workflow Status

| Field | Value |
|---|---|
| Run ID | `20260811T202300Z_6fbc97c364` |
| Release status | `approved_with_warnings` |
| Final audit decision | `pass` |
| Writer mode | `llm_writer` |
| Report genre | `event_report` |
| Communication task | `event_report` |
| Output form | `multi_paragraph_report` |
| Focus scope | `reference_recap` |
| Verified insights | 3 |
| Repair rounds used | 0 |
| Native support rate | 1.0 |
| Supported factual sentences | 10 / 10 |

The workflow output passed factual audit with full native sentence support. The
remaining warning was quality-oriented rather than a detected factual error: the
report was slightly below the internal minimum useful coverage threshold.

## Reference Metrics

| Metric | Higher is better? | Full workflow v4-pro | Raw v4-pro | Better output |
|---|---:|---:|---:|---|
| BLEU | Yes | 0.1337 | 0.1175 | Full workflow |
| chrF | Yes | 0.4683 | 0.4305 | Full workflow |
| TER | No | 0.7958 | 0.8168 | Full workflow |
| ROUGE-1 | Yes | 0.5700 | 0.5371 | Full workflow |
| ROUGE-2 | Yes | 0.2192 | 0.2234 | Raw v4-pro, very small margin |
| ROUGE-L | Yes | 0.3413 | 0.2898 | Full workflow |
| ROUGE-Lsum | Yes | 0.3413 | 0.2898 | Full workflow |
| METEOR | Yes | 0.2970 | 0.2586 | Full workflow |
| BERTScore F1 | Yes | 0.8839 | 0.8574 | Full workflow |

The full workflow wins eight out of the nine listed metrics. The only raw
baseline win is ROUGE-2, and the margin is small:

```text
raw v4-pro ROUGE-2:       0.2234
full workflow ROUGE-2:    0.2192
difference:               0.0042
```

This is a useful result because previous raw baselines were often competitive on
reference-overlap metrics. Here, when both sides use v4-pro, the full workflow is
closer to the human reference on most lexical, edit-distance and semantic
metrics.

## Runtime

| Variant | Runtime |
|---|---:|
| Full workflow v4-pro | 1082.6 seconds |
| Raw v4-pro | 21.6 seconds |

The full workflow is much slower. The result supports the claim that the
architecture can improve reference similarity and auditability, but it also
confirms that efficiency is a major trade-off.

## Output Comparison Notes

The full workflow report:

- states the final result immediately;
- reports the venue and date;
- describes quarter-by-quarter score progression;
- identifies leading scorers and contributors;
- includes both teams' records and next-game context;
- passed factual audit with every factual sentence supported.

The raw v4-pro baseline is fluent and compact, but it includes at least one
phrase that appears stronger than the supplied evidence:

```text
"sold-out Wells Fargo Center"
```

The structured source records attendance as `20,300` and capacity as `20,500`.
That is very close to full capacity, but it is not exactly sold out. The raw
baseline's wording is therefore a small overstatement. This is a useful example
for the dissertation because it illustrates the difference between fluent
single-call generation and evidence-audited generation.

The raw output also includes more natural sports-report phrasing, but the full
workflow provides a traceable path through input interpretation, evidence
extraction, verification, writing and audit.

## Dissertation Interpretation

This run supports the following dissertation claim:

```text
When the same strong LLM is used in both settings, the structured workflow can
outperform a raw single-call baseline on most reference-similarity metrics while
also providing auditable support for each factual sentence.
```

The result should not be overclaimed. It is one SportSett example, not a full
benchmark conclusion. It is strongest as a case study showing that the workflow
can outperform a strong raw model when the task requires event interpretation,
content selection and factual control.

Suggested dissertation wording:

```text
In SportSett example 4934, both the complete workflow and the raw baseline used
DeepSeek v4-pro. The workflow achieved higher BLEU, chrF, ROUGE-1, ROUGE-L,
METEOR and BERTScore F1, and lower TER. The raw baseline only led on ROUGE-2 by
a very small margin. The workflow also passed the internal factual audit with a
1.0 support rate across ten factual sentences. This suggests that the
architecture can improve both reference similarity and traceable factual control,
although at a substantial runtime cost.
```

## How To Use This In The Evaluation Chapter

This finding is useful for three parts of the dissertation:

1. Main results:

   Show that the workflow can beat a raw single-call LLM even when the raw
   baseline uses the same pro model.

2. Error analysis:

   Use the raw baseline's "sold-out" phrase as a small but concrete example of
   fluent overstatement.

3. Limitations:

   Acknowledge the runtime cost clearly. The architecture improves traceability
   and often improves output quality, but it is much slower than raw generation.

## Caution

If the intended experiment is specifically:

```text
full workflow using v4-flash
vs
raw baseline using v4-pro
```

then the full-system side must be rerun after resetting the workflow model
environment variables to `deepseek-v4-flash`. The saved manifest for this run
shows that the full workflow used `deepseek-v4-pro` for every role.
