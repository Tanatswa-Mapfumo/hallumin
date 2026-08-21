# Optimized Human Participation Plan

## Purpose

This human participation study is designed to evaluate whether the workflow system produces outputs that are more useful than a raw generic LLM baseline when both are judged against the supplied source data.

The study is based on the factual-accuracy annotation logic in Thomson, Reiter and Sundararajan's *Evaluating factual accuracy in complex data-to-text*. The key adaptation is that annotators first identify factual errors, then separately judge task quality. This avoids treating content selection, fluency and factual correctness as one blurred score.

The study is not primarily a reference-matching exercise. The automatic metrics already show that reference overlap can be misleading, especially for event reports where there are many valid ways to write the same game. Human judgement should therefore focus on source-grounded factuality, important information coverage, task fit and narrative quality.

## Paper-Based Accuracy Protocol

The factual accuracy component uses six error categories inspired by the paper:

| Error category | Meaning in this project |
| --- | --- |
| Incorrect number | Wrong score, date, percentage, count, rank, statistic or measurement. |
| Incorrect named entity | Wrong person, team, place, organisation, title or subject. |
| Incorrect word or relation | Wrong verb, role, relation direction, comparison, attribute or table-header meaning. |
| Context or misleading claim | A claim that may sound plausible but is misleading, over-interpreted or unsupported in context. |
| Not checkable | A claim that cannot be checked against the supplied source data. |
| Other factual error | Any other factual problem. |

Annotators are asked to list the sentence or phrase containing an error, assign one category and provide a short correction or explanation. This is a practical form-friendly version of span-level annotation.

## What Is Kept Separate From Accuracy

Following the paper's distinction, omissions are not automatically counted as factual errors. In complex data-to-text, no short report can include every source fact. Instead:

- wrong or unsupported claims are factual accuracy errors;
- missing important information is a content-selection issue;
- weak event narrative or poor table focus is a task-quality issue;
- awkward phrasing is a readability issue.

This separation lets the dissertation report both factual reliability and usefulness without pretending they are the same thing.

## Main Comparison

The primary blinded comparison is:

```text
full_system vs raw_generic_flash
```

The raw baseline receives a generic instruction and the same source data. The workflow output comes from the full system run. Annotators do not see which output came from which system.

## Optimized Dataset Selection

The old broad 25-example packet set was useful for coverage, but it was not ideal for the human study because it included examples that do not support a clean story. This optimized version uses 12 examples selected for interpretability and diagnostic value.

The selection emphasises:

- examples where the source data is readable enough for volunteers to judge;
- outputs where the workflow used an LLM writer path rather than a deterministic fallback;
- datasets where factual exactness and content selection can be evaluated directly;
- a small number of challenge cases where automatic metrics are mixed or favour the raw baseline.

## Included Datasets

| Dataset | Included examples | Reason for inclusion |
| --- | ---: | --- |
| SportSett Basketball | 2 | Tests event-report narration, result extraction, player-performance selection and bounded interpretation. Only `llm_writer` examples are used. |
| ToTTo | 3 | Tests focused highlighted-table propositions, entity/header grounding and avoiding broad irrelevant summaries. |
| WebNLG | 2 | Tests structured triple verbalisation, relation direction and concise semantic coverage. |
| DART | 3 | Tests short triple-to-text generation, including one raw-baseline counterexample. |
| E2E NLG | 2 | Tests meaning-representation slot coverage and natural realisation. |

## Exclusion Rules

SportSett examples are excluded from the primary human study if the workflow output used `deterministic_fallback`. This avoids using outputs that are less representative of the LLM-led workflow.

The excluded SportSett examples from the 25-example run are:

- `4975`: excluded because `full_system_writer_mode = deterministic_fallback`.
- `4972`: excluded from the clean primary comparison because it used `auditor_repaired`; it can be used later in a repair-quality appendix.
- `4982`: retained as a reserve, but not needed in the 12-packet primary set.

## Selected Primary Packets

| Dataset | Example | Role |
| --- | --- | --- |
| SportSett Basketball | `4934` | Event narrative showcase |
| SportSett Basketball | `4986` | Event narrative challenge |
| ToTTo | `totto-validation-712` | Focused table strong case |
| ToTTo | `totto-validation-244` | Focused table precision case |
| ToTTo | `totto-validation-204` | Subject-relation grounding case |
| WebNLG | `web_nlg_en-test-178` | Triple realisation strong case |
| WebNLG | `web_nlg_en-test-61` | Triple source-support case |
| DART | `dart-test-204` | Short triple workflow win |
| DART | `dart-test-217` | Short triple source-support case |
| DART | `dart-test-260` | Raw metric win counterexample |
| E2E NLG | `e2e_nlg-test-51` | Mixed metric slot-realisation case |
| E2E NLG | `e2e_nlg-test-61` | Clean slot-realisation case |

## Good And Bad Output Strategy

The study should not cherry-pick only workflow wins. Instead, it should deliberately include:

- clear workflow wins, where source-grounded structure appears to help;
- close cases, where both outputs are plausible;
- challenge cases, where the raw baseline has stronger reference overlap or fluency;
- event-report cases, where reference metrics are less reliable and human judgement matters most.

This makes the human study more defensible: it can show where the workflow helps, where it does not, and which failure modes matter.

## Annotation Method

Each packet should be judged by at least three annotators where possible. Annotators should not know which output is the workflow output.

For each packet, annotators see:

1. requested task;
2. structured source data;
3. human reference output;
4. Output A;
5. Output B;
6. common pairwise questions;
7. dataset-specific questions.

Annotators should use the source data as the main authority. The human reference is useful as a target style and content clue, but it should not override the source data.

## Analysis Plan

Report results in four groups:

| Category | Questions | What it shows |
| --- | --- | --- |
| Category | Questions | What it shows |
| --- | --- | --- |
| Factual accuracy | Q1, Q2, Q3 | Which output has fewer concrete factual errors and what types of errors appear. |
| Unsupported and misleading claims | Q4, Q5 | Whether claims are checkable and properly bounded by the source. |
| Content selection | Q6, Q7 plus free-text comments | Whether outputs include useful source-supported information without distraction. |
| Task and genre fit | Q8 plus dataset-specific questions | Whether the report type matches the requested task. |
| Readability | Q9, Q10 | Whether the output is appropriately detailed, organised and readable. |
| Reference relation | Q11 | How close the output is to the reference when the source remains authoritative. |
| Overall preference | Q12, Q13, Q14 | Which output humans would actually use and why. |

In the dissertation, compare human preference against automatic metrics. This is especially important for SportSett, where reference overlap is only a partial indicator of quality.

## Output Files

The optimized human-study files are:

```text
evaluation/human/optimized/optimized_human_annotation_packets_preview.md
evaluation/human/optimized/optimized_human_annotation_packets_blinded.jsonl
evaluation/human/optimized/optimized_human_annotation_packets_for_forms.csv
evaluation/human/optimized/optimized_human_annotation_answer_key_private.jsonl
evaluation/human/optimized/optimized_selection_manifest.md
```
