# Complete Three-Condition Table-to-Text Evaluation Dossier

Generated from persisted artifacts on 2026-08-20T12:52:09.502343+00:00.

This document is a self-contained results bank for the 25-example, five-dataset experiment comparing the complete multi-agent workflow, a one-call raw-generic baseline and a one-call task-aware baseline. It includes every selected source input, every condition-specific request, held-out human reference, exact generated output, automatic metric score and structured error annotation.

## 1. Experimental population

| Property | Value |
|---|---|
| Datasets | DART, E2E NLG, SportSett Basketball, ToTTo, WebNLG |
| Examples | 25 total; five per dataset |
| Conditions | 3 |
| Generated outputs | 75 |
| Seed | 42 |
| Reference isolation | Human references were held out from every generator |
| Request control | Full and Task-aware Direct used the task-specific request; Raw Generic used one generic request |
| Reference metric records | 495 |
| Source-grounded metric records | 300 |
| Structured judge records | 75 |

### 1.1 Dataset and task distribution

| Dataset | Cases |
|---|---|
| dart | 5 |
| e2e_nlg | 5 |
| sportsett_basketball | 5 |
| totto | 5 |
| web_nlg | 5 |

| Task family | Cases |
|---|---|
| attribute_verbalisation | 5 |
| event_report | 5 |
| highlighted_table_description | 5 |
| triple_verbalisation | 10 |

| Output mode | Cases |
|---|---|
| multi_paragraph_report | 5 |
| one_sentence | 5 |
| short_text | 15 |

### 1.2 Conditions

| Variant ID | Description | Model configuration | Generation path |
|---|---|---|---|
| `full_system` | Six-role multi-agent workflow with deterministic evidence infrastructure, verification, Writer and Auditor. | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash | Source + request + prepared task contract pass through the complete workflow. |
| `raw_generic_flash` | One direct DeepSeek call receiving a generic strongest-findings request and the source, without task-family/output-form metadata. | deepseek-v4-flash; temperature 0.2; maximum output 3,000 tokens | Generic direct prompt |
| `task_aware_direct_flash` | One direct DeepSeek call receiving the same source and request plus task family, output form and language. | deepseek-v4-flash; temperature 0.2; maximum output 3,000 tokens | Structured direct prompt |

## 2. Generator inputs and prompt contracts

### 2.1 Shared direct-baseline system prompt

```text
You are a raw single-LLM data-to-text baseline. Generate the requested output directly from the supplied source data. Use only the source data and the user request. Do not use outside knowledge. Do not invent numbers, entities, chronology, causal explanations, or background. Do not mention hidden references, evaluation, prompts, or uncertainty unless the source itself makes the requested output impossible.
```

### 2.2 Raw-generic user-prompt template

```text
Request:
Understand the supplied data and report its strongest supported findings.

Source data:
{source}

Write the final answer only.
```

### 2.3 Task-aware direct user-prompt template

```text
Task type: {task_family}
Expected form: {output_mode}
Language: {language}

Request:
{example.request}

Source data:
{source}

Write the final answer only.
```

### 2.4 Full-System operational input

The Full System received the same source data and task-specific request as Task-aware Direct together with the prepared benchmark task metadata. It did not receive the human references. Unlike the direct conditions, this is a workflow input rather than one monolithic LLM prompt: source interpretation, planning, evidence, verification, writing and auditing are separate stages.

The Raw-vs-Task-aware comparison changes the complete communication contract: the request itself becomes task-specific and the prompt adds task family, expected form and language. It should therefore be interpreted as a task-contract ablation, not as an isolated test of metadata labels alone.

## 3. Evaluation measures

| Metric | Family | Orientation | What is compared |
|---|---|---|---|
| BLEU / Corpus BLEU | Lexical overlap | Higher is better | Output against held-out reference text |
| chrF / Corpus chrF | Character overlap | Higher is better | Output against held-out reference text |
| TER / Corpus TER | Edit distance | Lower is better | Output against held-out reference text |
| ROUGE-L | Sequence overlap | Higher is better | Output against held-out reference text |
| METEOR | Lexical-semantic alignment | Higher is better | Output against held-out reference text |
| BERTScore F1 | Embedding similarity | Higher is better | Output against held-out reference text |
| AlignScore | Source-grounded alignment | Higher is better | Output against full structured source |
| HHEM mean support | Source-grounded support | Higher is better | Sentence support against full source |
| HHEM minimum support | Weakest-sentence support | Higher is better | Minimum sentence support against full source |
| HHEM unsupported-sentence rate | Unsupported-content diagnostic | Lower is better | Proportion below the HHEM support threshold |
| GPT-5.6 Sol taxonomy | Structured error annotation | Fewer errors is better | Source + task + one output; no human reference as correctness criterion |

Corpus BLEU, corpus chrF and corpus TER are computed once per dataset-condition group of five examples. They therefore appear in aggregate tables, not as independent per-example scores.

## 4. Generation outcomes

| Condition | Outputs | Generation errors | Total elapsed seconds | Median output words | Writer modes | Release statuses |
|---|---:|---:|---:|---:|---|---|
| Full multi-agent system | 25 | 0 | 5451.529 | 18 | auditor_repaired: 1, deterministic_fallback: 1, llm_writer: 23 | approved: 3, approved_with_warnings: 22 |
| Raw-generic direct Flash | 25 | 0 | 131.983 | 26 | Not applicable | Not applicable |
| Task-aware direct Flash | 25 | 0 | 109.729 | 18 | Not applicable | Not applicable |

All 75 generation records contain non-empty outputs and no generation-level error. Full-System release and Writer-mode fields do not apply to the two direct baselines.

## 5. Aggregate reference-alignment metrics

| metric_name | full_system | raw_generic_flash | task_aware_direct_flash |
|---|---|---|---|
| bertscore_f1 | 0.924556961 | 0.896492805 | 0.922681706 |
| bleu | 0.359519658 | 0.23831319 | 0.30910482 |
| chrf | 0.597166836 | 0.4676202 | 0.548803193 |
| corpus_bleu | 0.348185259 | 0.220898337 | 0.294510853 |
| corpus_chrf | 0.596111273 | 0.460135878 | 0.539737023 |
| corpus_ter | 0.871923021 | 2.875585978 | 0.896159274 |
| meteor | 0.555026325 | 0.449514292 | 0.506067028 |
| rougeL | 0.559918077 | 0.444022787 | 0.537541881 |
| ter | 0.716080166 | 2.630348227 | 0.735125538 |

## 6. Aggregate source-grounded metrics

| metric_name | full_system | raw_generic_flash | task_aware_direct_flash |
|---|---|---|---|
| alignscore_base | 0.67837122 | 0.612100539 | 0.635583142 |
| hhem_2_1_open_mean_support | 0.553033755 | 0.543720499 | 0.585651486 |
| hhem_2_1_open_min_sentence_support | 0.539562534 | 0.466515104 | 0.573314445 |
| hhem_2_1_open_unsupported_sentence_rate | 0.350388889 | 0.346 | 0.233333333 |

## 7. Direction-adjusted same-item metric wins

For TER and HHEM unsupported-sentence rate, lower values are treated as wins; all other included metrics use higher values.

| comparison | paired_metric_cases | left_wins | ties | right_wins |
|---|---|---|---|---|
| Full vs Task-aware Direct | 265 | 110 | 77 | 78 |
| Task-aware Direct vs Raw Generic | 265 | 172 | 47 | 46 |
| Full vs Raw Generic | 265 | 171 | 38 | 56 |

## 8. Structured error annotations

| Condition | Outputs | Flagged outputs | Errors | Categories | Execution provenance |
|---|---|---|---|---|---|
| Full multi-agent system | 25 | 5 | 10 | CONTEXT: 5, TASK/FORMAT: 5 | interactive_session: 1, openai_responses_api: 24 |
| Raw-generic direct Flash | 25 | 11 | 19 | CONTEXT: 4, NUMBER: 2, OMISSION: 3, TASK/FORMAT: 10 | openai_responses_api: 25 |
| Task-aware direct Flash | 25 | 5 | 13 | CONTEXT: 9, NOT CHECKABLE: 2, NUMBER: 1, TASK/FORMAT: 1 | interactive_session: 25 |

The judge label is `gpt-5.6-sol`. The Full and raw-generic conditions contain 49 API-authenticated records plus one interactive completion for the previously skipped Full-System SportSett 4975 output. All 25 task-aware records were produced interactively without an API call. The combined artifact retains `execution_mode` and `api_authenticated` fields so this split cannot be mistaken for a uniform API run.

### 8.1 Category totals

| Category | Count |
|---|---|
| CONTEXT | 18 |
| NOT CHECKABLE | 2 |
| NUMBER | 3 |
| OMISSION | 3 |
| TASK/FORMAT | 16 |

## 9. Reference metrics by dataset

| dataset_id | metric_name | full_system | raw_generic_flash | task_aware_direct_flash |
|---|---|---|---|---|
| dart | bertscore_f1 | 0.920560491 | 0.918590617 | 0.917348838 |
| dart | bleu | 0.193985081 | 0.158001689 | 0.177479619 |
| dart | chrf | 0.491787546 | 0.479559369 | 0.483320782 |
| dart | corpus_bleu | 0.219679029 | 0.165853634 | 0.189296905 |
| dart | corpus_chrf | 0.500590229 | 0.50433438 | 0.491175272 |
| dart | corpus_ter | 0.826086957 | 0.97826087 | 0.891304348 |
| dart | meteor | 0.459953396 | 0.437811063 | 0.455615719 |
| dart | rougeL | 0.478861284 | 0.491618831 | 0.489492809 |
| dart | ter | 0.843073593 | 1.094155844 | 0.91482684 |
| e2e_nlg | bertscore_f1 | 0.963549459 | 0.962500226 | 0.964344001 |
| e2e_nlg | bleu | 0.603940762 | 0.547822922 | 0.570746157 |
| e2e_nlg | chrf | 0.763079003 | 0.743903536 | 0.753719966 |
| e2e_nlg | corpus_bleu | 0.56937711 | 0.48719558 | 0.519409132 |
| e2e_nlg | corpus_chrf | 0.743422919 | 0.723361157 | 0.731698063 |
| e2e_nlg | corpus_ter | 1.188679245 | 1.256603774 | 1.086792453 |
| e2e_nlg | meteor | 0.796960435 | 0.800582767 | 0.812850287 |
| e2e_nlg | rougeL | 0.739762626 | 0.736375416 | 0.749055556 |
| e2e_nlg | ter | 0.435378025 | 0.469528352 | 0.400083907 |
| sportsett_basketball | bertscore_f1 | 0.842422521 | 0.829608798 | 0.862284458 |
| sportsett_basketball | bleu | 0.08944279 | 0.042220238 | 0.108498579 |
| sportsett_basketball | chrf | 0.414339212 | 0.255759564 | 0.395912119 |
| sportsett_basketball | corpus_bleu | 0.083005233 | 0.043987144 | 0.114884905 |
| sportsett_basketball | corpus_chrf | 0.412680646 | 0.257087916 | 0.397103403 |
| sportsett_basketball | corpus_ter | 0.955768636 | 0.812867306 | 0.821527993 |
| sportsett_basketball | meteor | 0.253678706 | 0.170333535 | 0.266808461 |
| sportsett_basketball | rougeL | 0.225143724 | 0.226877546 | 0.270643043 |
| sportsett_basketball | ter | 0.963805723 | 0.813300287 | 0.822113357 |
| totto | bertscore_f1 | 0.93381685 | 0.827738595 | 0.906550431 |
| totto | bleu | 0.340589807 | 0.041280285 | 0.155648367 |
| totto | chrf | 0.567410023 | 0.202104306 | 0.397392357 |
| totto | corpus_bleu | 0.33715821 | 0.023683594 | 0.147157429 |
| totto | corpus_chrf | 0.600846551 | 0.176383276 | 0.395128507 |
| totto | corpus_ter | 0.87150838 | 10.592178771 | 1.173184358 |
| totto | meteor | 0.565198533 | 0.226614778 | 0.324165422 |
| totto | rougeL | 0.585567126 | 0.131117646 | 0.421058019 |
| totto | ter | 0.873042378 | 10.065323484 | 1.075268365 |
| web_nlg | bertscore_f1 | 0.962435484 | 0.944025791 | 0.962880802 |
| web_nlg | bleu | 0.569639851 | 0.402240817 | 0.533151376 |
| web_nlg | chrf | 0.749218394 | 0.656774226 | 0.713670739 |
| web_nlg | corpus_bleu | 0.531706716 | 0.383771732 | 0.501805893 |
| web_nlg | corpus_chrf | 0.723016021 | 0.63951266 | 0.683579869 |
| web_nlg | corpus_ter | 0.517571885 | 0.738019169 | 0.50798722 |
| web_nlg | meteor | 0.699340557 | 0.612229319 | 0.670895248 |
| web_nlg | rougeL | 0.770255622 | 0.634124496 | 0.757459977 |
| web_nlg | ter | 0.465101111 | 0.70943317 | 0.463335221 |

## 10. Source-grounded metrics by dataset

| dataset_id | metric_name | full_system | raw_generic_flash | task_aware_direct_flash |
|---|---|---|---|---|
| dart | alignscore_base | 0.977376366 | 0.843651712 | 0.863333881 |
| dart | hhem_2_1_open_mean_support | 0.876600122 | 0.768950367 | 0.825728691 |
| dart | hhem_2_1_open_min_sentence_support | 0.876600122 | 0.768950367 | 0.825728691 |
| dart | hhem_2_1_open_unsupported_sentence_rate | 0 | 0 | 0 |
| e2e_nlg | alignscore_base | 0.978235114 | 0.966581857 | 0.978417695 |
| e2e_nlg | hhem_2_1_open_mean_support | 0.673254359 | 0.711226702 | 0.688891423 |
| e2e_nlg | hhem_2_1_open_min_sentence_support | 0.673254359 | 0.711226702 | 0.688891423 |
| e2e_nlg | hhem_2_1_open_unsupported_sentence_rate | 0 | 0 | 0 |
| sportsett_basketball | alignscore_base | 0.128457081 | 0.19428148 | 0.178423068 |
| sportsett_basketball | hhem_2_1_open_mean_support | 0.068618534 | 0.093643892 | 0.058961998 |
| sportsett_basketball | hhem_2_1_open_min_sentence_support | 0.009588013 | 0.023847265 | 0.00830538 |
| sportsett_basketball | hhem_2_1_open_unsupported_sentence_rate | 0.951944444 | 0.933333333 | 0.966666667 |
| totto | alignscore_base | 0.350862062 | 0.461192754 | 0.328416198 |
| totto | hhem_2_1_open_mean_support | 0.448542912 | 0.537304018 | 0.664293636 |
| totto | hhem_2_1_open_min_sentence_support | 0.448542912 | 0.225302413 | 0.664293636 |
| totto | hhem_2_1_open_unsupported_sentence_rate | 0.6 | 0.396666667 | 0.2 |
| web_nlg | alignscore_base | 0.956925476 | 0.594794892 | 0.829324871 |
| web_nlg | hhem_2_1_open_mean_support | 0.698152846 | 0.607477516 | 0.690381682 |
| web_nlg | hhem_2_1_open_min_sentence_support | 0.689827263 | 0.603248775 | 0.679353094 |
| web_nlg | hhem_2_1_open_unsupported_sentence_rate | 0.2 | 0.4 | 0 |

## 11. Selected five-case source-grounded extraction

This is the notebook's dedicated exact-case extract for the five preselected diagnostic cases.

| dataset_id | example_id | variant_id | alignscore_base | hhem_2_1_open_mean_support | hhem_2_1_open_min_sentence_support | hhem_2_1_open_unsupported_sentence_rate |
|---|---|---|---|---|---|---|
| dart | dart-test-53 | full_system | 0.984827399 | 0.766979694 | 0.766979694 | 0 |
| dart | dart-test-53 | raw_generic_flash | 0.835419893 | 0.717174292 | 0.717174292 | 0 |
| dart | dart-test-53 | task_aware_direct_flash | 0.99002701 | 0.73588568 | 0.73588568 | 0 |
| e2e_nlg | e2e_nlg-test-51 | full_system | 0.98525846 | 0.656192243 | 0.656192243 | 0 |
| e2e_nlg | e2e_nlg-test-51 | raw_generic_flash | 0.986562431 | 0.642529547 | 0.642529547 | 0 |
| e2e_nlg | e2e_nlg-test-51 | task_aware_direct_flash | 0.987490237 | 0.673285127 | 0.673285127 | 0 |
| sportsett_basketball | 4934 | full_system | 0.161951184 | 0.109063067 | 0.007973887 | 0.888888889 |
| sportsett_basketball | 4934 | raw_generic_flash | 0.198321849 | 0.033393375 | 0.010957376 | 1 |
| sportsett_basketball | 4934 | task_aware_direct_flash | 0.191163212 | 0.140728037 | 0.013212758 | 0.833333333 |
| totto | totto-validation-204 | full_system | 0.229820535 | 0.831519663 | 0.831519663 | 0 |
| totto | totto-validation-204 | raw_generic_flash | 0.667195082 | 0.794786423 | 0.589485765 | 0 |
| totto | totto-validation-204 | task_aware_direct_flash | 0.637972236 | 0.90948987 | 0.90948987 | 0 |
| web_nlg | web_nlg_en-test-51 | full_system | 0.950594425 | 0.720226645 | 0.720226645 | 0 |
| web_nlg | web_nlg_en-test-51 | raw_generic_flash | 0.983758807 | 0.742143214 | 0.742143214 | 0 |
| web_nlg | web_nlg_en-test-51 | task_aware_direct_flash | 0.959383786 | 0.699708045 | 0.699708045 | 0 |

## 12. Aggregate observations

1. The Full System has the strongest overall reference-alignment macro scores: BLEU 0.3595, chrF 0.5972, METEOR 0.5550, ROUGE-L 0.5599 and BERTScore F1 0.9246. Its macro TER is also lowest at 0.7161.
2. Supplying the complete task contract to the direct model substantially improves over the raw-generic direct baseline: Task-aware Direct wins 172 of 265 paired metric cases, loses 46 and ties 47. This contrast combines a task-specific request with task-family, output-form and language metadata.
3. The Full System still leads the task-aware direct condition in the paired analysis, with 110 wins, 78 losses and 77 ties, but the gap is much smaller than Full versus raw generic.
4. SportSett is the principal exception in reference alignment: task-aware direct has the highest SportSett BERTScore, BLEU, METEOR and ROUGE-L. This indicates that explicit event-report metadata gives a strong one-call model a major advantage on long-form game reports.
5. ToTTo shows the largest architecture benefit. Full System materially exceeds both direct conditions because highlighted-cell selection is a content-selection problem, not merely a fluency problem.
6. Source-grounded metrics disagree with each other. Full System has the highest macro AlignScore (0.6784), while task-aware direct has the best HHEM mean support (0.5857), minimum support (0.5733) and unsupported-sentence rate (0.2333). These models should be interpreted as separate diagnostics rather than combined into one factuality score.
7. All three conditions receive extremely low HHEM/AlignScore values on SportSett despite mostly plausible reports and source-checked judge findings. The long nested JSON source is a difficult input representation for these local factuality models, so SportSett source scores should not be treated as direct hallucination rates.
8. Structured error annotations flag 10 Full-System errors, 19 raw-generic errors and 13 task-aware-direct errors. Full System therefore retains the lowest annotation count, while task metadata removes a substantial share of the raw baseline's task/format failures.
9. CONTEXT and TASK/FORMAT dominate the annotation taxonomy. Straightforward short-form datasets are largely accurate; remaining weaknesses concentrate in chronology, causal narration, ranking language and scope compliance.

## 13. Complete per-example records

Each record below contains the complete source, condition-specific requests, all three exact outputs, all item-level metrics and all corresponding structured annotations. References are displayed for evaluation transparency but were not supplied to any generator or used by the structured judge as its correctness criterion.

# Case 1: `dart` / `dart-test-204`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | dart |
| Example ID | dart-test-204 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 36 |
| Reference count | 1 |
| Source SHA-256 | 72e14f2e09e5252b44541ab335c2a12c81a66a62fe6e7f4542de8719d1cfbd90 |
| Reference SHA-256 | e469f0d5f3549dc1cb4afb2de8906e94ce28c510c6bbfda208a2cca366d6583a |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
AC Express | TRAIN_NO. | 22475/22476
```

## Structured source payload

```json
{
  "triples": [
    [
      "AC Express",
      "TRAIN_NO.",
      "22475/22476"
    ]
  ],
  "category": null
}
```

## Parent table representation

```json
[
  [
    "AC Express",
    "TRAIN_NO.",
    "22475/22476"
  ]
]
```

## Prepared-example metadata

```json
{
  "target_sources": [
    "WikiSQL_lily"
  ],
  "subtree_was_extended": false,
  "normalizer": "dart",
  "requested_split": "test",
  "hub_id": "GEM/dart",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The AC Express is numbered 22475/22476.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-204__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 8.243 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 7 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
AC Express has train number 22475/22476.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-204__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 2.423 |
| Prompt tokens | 197 |
| Completion tokens | 137 |
| Total tokens | 334 |
| Output words | 13 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The data indicates that train number 22475/22476 is an AC Express service.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-204__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 2.050 |
| Prompt tokens | 225 |
| Completion tokens | 68 |
| Total tokens | 293 |
| Output words | 7 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
AC Express has train number 22475/22476.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.354948106 | 0.58021324 | 0.666666667 | 0.714285714 | 0.625 | 0.965390563 | 0.984553993 | 0.975843668 | 0.975843668 | 0 |
| Raw-generic direct Flash | 0.138343685 | 0.518253466 | 1.5 | 0.4 | 0.563636364 | 0.946432829 | 0.884801269 | 0.968204379 | 0.968204379 | 0 |
| Task-aware direct Flash | 0.354948106 | 0.58021324 | 0.666666667 | 0.714285714 | 0.625 | 0.965390563 | 0.984553993 | 0.975843668 | 0.975843668 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 2: `dart` / `dart-test-217`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | dart |
| Example ID | dart-test-217 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 36 |
| Reference count | 1 |
| Source SHA-256 | 2fa680e859c8a48aa01b207f20617aa9ec356596606de11af5fcd8e6a7ac03d2 |
| Reference SHA-256 | 9436e2fecaad44cd8d0d66b83e938b3320bc905742f9ee9e92805b3158072476 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Alabama 5 | INCUMBENT | Albert Rains
```

## Structured source payload

```json
{
  "triples": [
    [
      "Alabama 5",
      "INCUMBENT",
      "Albert Rains"
    ]
  ],
  "category": null
}
```

## Parent table representation

```json
[
  [
    "Alabama 5",
    "INCUMBENT",
    "Albert Rains"
  ]
]
```

## Prepared-example metadata

```json
{
  "target_sources": [
    "WikiSQL_decl_sents"
  ],
  "subtree_was_extended": false,
  "normalizer": "dart",
  "requested_split": "test",
  "hub_id": "GEM/dart",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
Incumbent albert is rains from alabama 5.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-217__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 8.822 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 6 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Alabama 5's incumbent is Albert Rains.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-217__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.835 |
| Prompt tokens | 196 |
| Completion tokens | 111 |
| Total tokens | 307 |
| Output words | 9 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Albert Rains was the incumbent in Alabama's 5th district.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-217__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 2.338 |
| Prompt tokens | 224 |
| Completion tokens | 192 |
| Total tokens | 416 |
| Output words | 9 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Albert Rains is the incumbent for Alabama's 5th district.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.067701862 | 0.377910348 | 0.857142857 | 0.428571429 | 0.289855072 | 0.868617773 | 0.952587903 | 0.917543471 | 0.917543471 | 0 |
| Raw-generic direct Flash | 0.041961149 | 0.315184447 | 1.142857143 | 0.352941176 | 0.208333333 | 0.841331124 | 0.531945169 | 0.64457196 | 0.64457196 | 0 |
| Task-aware direct Flash | 0.049900497 | 0.333322456 | 1 | 0.352941176 | 0.277777778 | 0.844684243 | 0.375718713 | 0.625620306 | 0.625620306 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 3: `dart` / `dart-test-244`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | dart |
| Example ID | dart-test-244 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 47 |
| Reference count | 1 |
| Source SHA-256 | 9b3193812dec4b05d9fcf4504fb0e9aa7d428a39ec734675ff35581ad151adec |
| Reference SHA-256 | 47081ead6a9f8e85c315481ef9ba03389d0d1d4b93daa13b207417614c5759da |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
 piece of my heart  | DIRECTED_BY | mark tinker
```

## Structured source payload

```json
{
  "triples": [
    [
      " piece of my heart ",
      "DIRECTED_BY",
      "mark tinker"
    ]
  ],
  "category": null
}
```

## Parent table representation

```json
[
  [
    " piece of my heart ",
    "DIRECTED_BY",
    "mark tinker"
  ]
]
```

## Prepared-example metadata

```json
{
  "target_sources": [
    "WikiSQL_decl_sents"
  ],
  "subtree_was_extended": false,
  "normalizer": "dart",
  "requested_split": "test",
  "hub_id": "GEM/dart",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The title of the episode directed by Mark Tinker is "Piece of my Heart".
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-244__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 18.617 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 9 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Piece of my heart is directed by Mark Tinker.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-244__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.536 |
| Prompt tokens | 197 |
| Completion tokens | 62 |
| Total tokens | 259 |
| Output words | 9 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Piece of My Heart was directed by Mark Tinker.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-244__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.476 |
| Prompt tokens | 225 |
| Completion tokens | 100 |
| Total tokens | 325 |
| Output words | 9 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Piece of My Heart was directed by Mark Tinker.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.200895251 | 0.505054687 | 0.714285714 | 0.434782609 | 0.416666667 | 0.91503489 | 0.990329981 | 0.930508733 | 0.930508733 | 0 |
| Raw-generic direct Flash | 0.16669832 | 0.463603983 | 0.714285714 | 0.434782609 | 0.358518519 | 0.916429639 | 0.990097523 | 0.932230771 | 0.932230771 | 0 |
| Task-aware direct Flash | 0.16669832 | 0.463603983 | 0.714285714 | 0.434782609 | 0.358518519 | 0.916429639 | 0.990097523 | 0.932230771 | 0.932230771 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 4: `dart` / `dart-test-260`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | dart |
| Example ID | dart-test-260 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 77 |
| Reference count | 1 |
| Source SHA-256 | d1b0080bf9ffe396d2f840044373b09f422f0eb8f91792a82cb96b2624d3be8d |
| Reference SHA-256 | fbddbeed8343fa59d3a956d38d1ddc2ac9fd239ee61e8223d97527382ba0a843 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
philippe jeannol | PERIOD | 1984 - 1991
philippe jeannol | APPEARANCES¹ | 219
```

## Structured source payload

```json
{
  "triples": [
    [
      "philippe jeannol",
      "PERIOD",
      "1984 - 1991"
    ],
    [
      "philippe jeannol",
      "APPEARANCES¹",
      "219"
    ]
  ],
  "category": null
}
```

## Parent table representation

```json
[
  [
    "philippe jeannol",
    "PERIOD",
    "1984 - 1991"
  ],
  [
    "philippe jeannol",
    "APPEARANCES¹",
    "219"
  ]
]
```

## Prepared-example metadata

```json
{
  "target_sources": [
    "WikiSQL_decl_sents"
  ],
  "subtree_was_extended": true,
  "normalizer": "dart",
  "requested_split": "test",
  "hub_id": "GEM/dart",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
Philippe Jeannol had 219 appearances during the period 1984 - 1991.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-260__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 12.393 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 10 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Philippe Jeannol played from 1984 - 1991 and made 219 appearances¹.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-260__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 2.101 |
| Prompt tokens | 216 |
| Completion tokens | 104 |
| Total tokens | 320 |
| Output words | 10 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Philippe Jeannol recorded 219 appearances during the period 1984–1991.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-260__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.525 |
| Prompt tokens | 244 |
| Completion tokens | 126 |
| Total tokens | 370 |
| Output words | 12 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Philippe Jeannol had a period from 1984 to 1991, with 219 appearances.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.172422213 | 0.551286978 | 0.727272727 | 0.4 | 0.405454545 | 0.936533093 | 0.974582553 | 0.792125046 | 0.792125046 | 0 |
| Raw-generic direct Flash | 0.382460228 | 0.773497897 | 0.363636364 | 0.9 | 0.640589569 | 0.987292767 | 0.975994706 | 0.582570434 | 0.582570434 | 0 |
| Task-aware direct Flash | 0.153965038 | 0.596197128 | 0.818181818 | 0.545454545 | 0.46046046 | 0.952301025 | 0.976272166 | 0.859063029 | 0.859063029 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 5: `dart` / `dart-test-53`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | dart |
| Example ID | dart-test-53 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 95 |
| Reference count | 1 |
| Source SHA-256 | 8d265c7b0c5f2d309c6412f1c4e19de09e346b664500fb2ef1b2ce1b0f184665 |
| Reference SHA-256 | 3eb817df12fec937c8388415e90082273053f00fb71f166d2ec26adbaee9828b |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
University of Makati UM Pep Squad | TOTAL | 211.5
University of Makati UM Pep Squad | RANK | 11
```

## Structured source payload

```json
{
  "triples": [
    [
      "University of Makati UM Pep Squad",
      "TOTAL",
      "211.5"
    ],
    [
      "University of Makati UM Pep Squad",
      "RANK",
      "11"
    ]
  ],
  "category": null
}
```

## Parent table representation

```json
[
  [
    "University of Makati UM Pep Squad",
    "TOTAL",
    "211.5"
  ],
  [
    "University of Makati UM Pep Squad",
    "RANK",
    "11"
  ]
]
```

## Prepared-example metadata

```json
{
  "target_sources": [
    "WikiSQL_decl_sents"
  ],
  "subtree_was_extended": true,
  "normalizer": "dart",
  "requested_split": "test",
  "hub_id": "GEM/dart",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
It ranks 11th with a total of 211.5
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-53__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 10.102 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 15 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
University of Makati UM Pep Squad recorded a total of 211.5 and ranked 11th.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-53__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 2.236 |
| Prompt tokens | 211 |
| Completion tokens | 92 |
| Total tokens | 303 |
| Output words | 18 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The University of Makati UM Pep Squad earned a total score of 211.5, placing them 11th overall.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `dart__dart-test-53__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.855 |
| Prompt tokens | 239 |
| Completion tokens | 90 |
| Total tokens | 329 |
| Output words | 16 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The University of Makati UM Pep Squad scored a total of 211.5 and ranked 11th.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.173957974 | 0.444472477 | 1.25 | 0.416666667 | 0.562790698 | 0.917226136 | 0.984827399 | 0.766979694 | 0.766979694 | 0 |
| Raw-generic direct Flash | 0.060545065 | 0.327257052 | 1.75 | 0.37037037 | 0.417977528 | 0.901466727 | 0.835419893 | 0.717174292 | 0.717174292 | 0 |
| Task-aware direct Flash | 0.161886136 | 0.443267101 | 1.375 | 0.4 | 0.556321839 | 0.907938719 | 0.99002701 | 0.73588568 | 0.73588568 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 6: `e2e_nlg` / `e2e_nlg-test-178`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | e2e_nlg |
| Example ID | e2e_nlg-test-178 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 86 |
| Reference count | 5 |
| Source SHA-256 | 3a2239c81ecaaee2ee04686540806933518cd062ea19fee6a9820c3cb1fdcbbd |
| Reference SHA-256 | 8ff926771c9081f7ab35609af92903b87646de36f13fc20994cdfbbe5b0d7156 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
name[Strada], eatType[coffee shop], customer rating[low], near[Express by Holiday Inn]
```

## Structured source payload

```json
{
  "meaning_representation": "name[Strada], eatType[coffee shop], customer rating[low], near[Express by Holiday Inn]"
}
```

## Parent table representation

```json
[
  [
    "name",
    "Strada"
  ],
  [
    "eatType",
    "coffee shop"
  ],
  [
    "customer rating",
    "low"
  ],
  [
    "near",
    "Express by Holiday Inn"
  ]
]
```

## Prepared-example metadata

```json
{
  "normalizer": "e2e",
  "requested_split": "test",
  "hub_id": "GEM/e2e_nlg",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
Strada coffee shop has a low customer Rating and is located near Express by Holiday Inn.
```

### Reference 2

```text
Strada coffee shop has a low customer rating and is located near Express by Holiday Inn.
```

### Reference 3

```text
Strada is a one star coffee shop located near Express by Holiday Inn
```

### Reference 4

```text
Strada is a coffee shop, near Express by Holiday Inn. It has a low customer rating.
```

### Reference 5

```text
Strada coffee shop near Express by Holiday Inn has a low customer Rating
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-178__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 12.283 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 16 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Strada is a coffee shop with a low customer rating, located near Express by Holiday Inn.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-178__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.491 |
| Prompt tokens | 206 |
| Completion tokens | 69 |
| Total tokens | 275 |
| Output words | 16 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Strada is a coffee shop with a low customer rating, located near Express by Holiday Inn.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-178__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.260 |
| Prompt tokens | 235 |
| Completion tokens | 82 |
| Total tokens | 317 |
| Output words | 16 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Strada is a coffee shop with a low customer rating, located near Express by Holiday Inn.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.677468975 | 0.806134643 | 0.337837838 | 0.8125 | 0.789386095 | 0.9798491 | 0.981230915 | 0.604754806 | 0.604754806 | 0 |
| Raw-generic direct Flash | 0.677468975 | 0.806134643 | 0.337837838 | 0.8125 | 0.789386095 | 0.9798491 | 0.981230915 | 0.604754806 | 0.604754806 | 0 |
| Task-aware direct Flash | 0.677468975 | 0.806134643 | 0.337837838 | 0.8125 | 0.789386095 | 0.9798491 | 0.981230915 | 0.604754806 | 0.604754806 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 7: `e2e_nlg` / `e2e_nlg-test-51`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | e2e_nlg |
| Example ID | e2e_nlg-test-51 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 81 |
| Reference count | 9 |
| Source SHA-256 | 0962f10b1f2dfc0204014fbac5e985ea6018b201dd00f9e0c2922966e383c2c2 |
| Reference SHA-256 | 35470565cbf70bc2735e5bf36b65d22a6d377090eb50676381175bb2884564d4 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
name[Clowns], eatType[pub], customer rating[5 out of 5], near[Crowne Plaza Hotel]
```

## Structured source payload

```json
{
  "meaning_representation": "name[Clowns], eatType[pub], customer rating[5 out of 5], near[Crowne Plaza Hotel]"
}
```

## Parent table representation

```json
[
  [
    "name",
    "Clowns"
  ],
  [
    "eatType",
    "pub"
  ],
  [
    "customer rating",
    "5 out of 5"
  ],
  [
    "near",
    "Crowne Plaza Hotel"
  ]
]
```

## Prepared-example metadata

```json
{
  "normalizer": "e2e",
  "requested_split": "test",
  "hub_id": "GEM/e2e_nlg",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The pub Clowns that is near Crowne Plaza Hotel has ratings of 5 out of 5.
```

### Reference 2

```text
The pub Clowns is near Crowne Plaza Hotel and has a customer rating of 5 out of 5.
```

### Reference 3

```text
Near Crowne Plaza Hotel is a pub named Clowns that proudly boasts a high customer rating of 5 out of 5.
```

### Reference 4

```text
Found near Crowne Plaza Hotel, Clowns is a pub with a customer rating of 5 out of 5.
```

### Reference 5

```text
Crowne Plaza Hotel is a pub in Clowns with a rating 5 out of 5.
```

### Reference 6

```text
5 out of 5 rated Clowns pub is located near Crowne Plaza Hotel.
```

### Reference 7

```text
Near Crowne Plaza Hotel there is a pub with a 5 out of 5 rating. It's called Clowns.
```

### Reference 8

```text
Located near Crowne Plaza Hotel, The Clowns pub has a customer rating of 5 out of 5.
```

### Reference 9

```text
For a pub with a 5 out of 5 rating, check out Clowns near Crowne Plaza Hotel.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-51__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 14.331 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 18 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Clowns is a pub with a customer rating of 5 out of 5, located near Crowne Plaza Hotel.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-51__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.521 |
| Prompt tokens | 208 |
| Completion tokens | 89 |
| Total tokens | 297 |
| Output words | 19 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Clowns is a pub located near the Crowne Plaza Hotel, with a customer rating of 5 out of 5.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-51__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.540 |
| Prompt tokens | 237 |
| Completion tokens | 89 |
| Total tokens | 326 |
| Output words | 18 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Clowns is a pub near the Crowne Plaza Hotel, with a customer rating of 5 out of 5.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.868964684 | 0.869580897 | 0.352941176 | 0.722222222 | 0.832345679 | 0.970044017 | 0.98525846 | 0.656192243 | 0.656192243 | 0 |
| Raw-generic direct Flash | 0.700365242 | 0.822326525 | 0.176470588 | 0.756756757 | 0.933109025 | 0.972983599 | 0.986562431 | 0.642529547 | 0.642529547 | 0 |
| Task-aware direct Flash | 0.717283595 | 0.826213053 | 0.176470588 | 0.777777778 | 0.938292964 | 0.974251091 | 0.987490237 | 0.673285127 | 0.673285127 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 8: `e2e_nlg` / `e2e_nlg-test-54`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | e2e_nlg |
| Example ID | e2e_nlg-test-54 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 101 |
| Reference count | 1 |
| Source SHA-256 | d0a6692a2db3dcfb1b47a63172c2dcb213ab108c55bc7fc625a2f198d6c6ee41 |
| Reference SHA-256 | d8347083962842732d2755bf25423cf762ca90f5fd1c3aaa56d1bf8e9e24f983 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
name[Clowns], eatType[pub], priceRange[more than £30], customer rating[3 out of 5], near[All Bar One]
```

## Structured source payload

```json
{
  "meaning_representation": "name[Clowns], eatType[pub], priceRange[more than £30], customer rating[3 out of 5], near[All Bar One]"
}
```

## Parent table representation

```json
[
  [
    "name",
    "Clowns"
  ],
  [
    "eatType",
    "pub"
  ],
  [
    "priceRange",
    "more than £30"
  ],
  [
    "customer rating",
    "3 out of 5"
  ],
  [
    "near",
    "All Bar One"
  ]
]
```

## Prepared-example metadata

```json
{
  "normalizer": "e2e",
  "requested_split": "test",
  "hub_id": "GEM/e2e_nlg",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
For a 3 out of 5 star customer rated pub near All Bar One, Clowns is relatively expensive.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-54__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 11.127 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 26 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Clowns is a pub with a price range of more than £30 and a customer rating of 3 out of 5, located near All Bar One.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-54__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.631 |
| Prompt tokens | 215 |
| Completion tokens | 99 |
| Total tokens | 314 |
| Output words | 26 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
- Clowns is a pub.
- Its price range is more than £30.
- Its customer rating is 3 out of 5.
- It is located near All Bar One.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-54__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.272 |
| Prompt tokens | 244 |
| Completion tokens | 84 |
| Total tokens | 328 |
| Output words | 27 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Clowns is a pub with a price range of more than £30, a customer rating of 3 out of 5, and is located near All Bar One.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.203334482 | 0.487717106 | 1.111111111 | 0.409090909 | 0.598404255 | 0.90387094 | 0.975156724 | 0.614630342 | 0.614630342 | 0 |
| Raw-generic direct Flash | 0.162911928 | 0.471113338 | 1.333333333 | 0.409090909 | 0.526429063 | 0.90061456 | 0.913594127 | 0.821508944 | 0.821508944 | 0 |
| Task-aware direct Flash | 0.189042547 | 0.484289769 | 1.111111111 | 0.4 | 0.571906232 | 0.903636575 | 0.973837852 | 0.675722778 | 0.675722778 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 9: `e2e_nlg` / `e2e_nlg-test-61`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | e2e_nlg |
| Example ID | e2e_nlg-test-61 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 53 |
| Reference count | 1 |
| Source SHA-256 | 2762a016684067fd6e885e67880da470fa473ab6a459e634fb6c97607b9e4e84 |
| Reference SHA-256 | 9cfe5aed1199944569cd7fa27d32aac9e0484bfc9bec8c470396ec38ccc64753 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
name[Cocum], eatType[coffee shop], near[The Sorrento]
```

## Structured source payload

```json
{
  "meaning_representation": "name[Cocum], eatType[coffee shop], near[The Sorrento]"
}
```

## Parent table representation

```json
[
  [
    "name",
    "Cocum"
  ],
  [
    "eatType",
    "coffee shop"
  ],
  [
    "near",
    "The Sorrento"
  ]
]
```

## Prepared-example metadata

```json
{
  "normalizer": "e2e",
  "requested_split": "test",
  "hub_id": "GEM/e2e_nlg",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
Cocum is a coffee shop by The Sorrento.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-61__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 12.196 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 8 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Cocum is a coffee shop near The Sorrento.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-61__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.474 |
| Prompt tokens | 201 |
| Completion tokens | 63 |
| Total tokens | 264 |
| Output words | 9 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Cocum is a coffee shop located near The Sorrento.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-61__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.435 |
| Prompt tokens | 230 |
| Completion tokens | 64 |
| Total tokens | 294 |
| Output words | 8 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Cocum is a coffee shop near The Sorrento.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.596949179 | 0.829197825 | 0.125 | 0.875 | 0.864795918 | 0.981256723 | 0.973889053 | 0.83305043 | 0.83305043 | 0 |
| Raw-generic direct Flash | 0.525381979 | 0.797178631 | 0.25 | 0.823529412 | 0.854119426 | 0.97632736 | 0.975881398 | 0.829696238 | 0.829696238 | 0 |
| Task-aware direct Flash | 0.596949179 | 0.829197825 | 0.125 | 0.875 | 0.864795918 | 0.981256723 | 0.973889053 | 0.83305043 | 0.83305043 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 10: `e2e_nlg` / `e2e_nlg-test-65`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | e2e_nlg |
| Example ID | e2e_nlg-test-65 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 67 |
| Reference count | 1 |
| Source SHA-256 | 03fba3cd9ca6f0d0fa250e1b0000ebd4fe4dacc9b308f8f902c8d9a28bb05f27 |
| Reference SHA-256 | 11b991361936d60906b434607d3ef82d7c5996707e9715510a6c52de793f8ba6 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
name[Cocum], eatType[pub], customer rating[low], near[Café Sicilia]
```

## Structured source payload

```json
{
  "meaning_representation": "name[Cocum], eatType[pub], customer rating[low], near[Café Sicilia]"
}
```

## Parent table representation

```json
[
  [
    "name",
    "Cocum"
  ],
  [
    "eatType",
    "pub"
  ],
  [
    "customer rating",
    "low"
  ],
  [
    "near",
    "Café Sicilia"
  ]
]
```

## Prepared-example metadata

```json
{
  "normalizer": "e2e",
  "requested_split": "test",
  "hub_id": "GEM/e2e_nlg",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
Cocum, a pub with a low customer rating, is near Café Sicilia.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-65__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 10.135 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 13 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Cocum is a pub with a low customer rating, located near Café Sicilia.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-65__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.876 |
| Prompt tokens | 204 |
| Completion tokens | 92 |
| Total tokens | 296 |
| Output words | 13 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Cocum is a pub with a low customer rating, located near Café Sicilia.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `e2e_nlg__e2e_nlg-test-65__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.359 |
| Prompt tokens | 233 |
| Completion tokens | 73 |
| Total tokens | 306 |
| Output words | 13 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Cocum is a pub with a low customer rating, located near Café Sicilia.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.672986488 | 0.822764543 | 0.25 | 0.88 | 0.899870227 | 0.982726514 | 0.975640416 | 0.657643974 | 0.657643974 | 0 |
| Raw-generic direct Flash | 0.672986488 | 0.822764543 | 0.25 | 0.88 | 0.899870227 | 0.982726514 | 0.975640416 | 0.657643974 | 0.657643974 | 0 |
| Task-aware direct Flash | 0.672986488 | 0.822764543 | 0.25 | 0.88 | 0.899870227 | 0.982726514 | 0.975640416 | 0.657643974 | 0.657643974 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 11: `sportsett_basketball` / `4934`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | sportsett_basketball |
| Example ID | 4934 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source characters | 24168 |
| Reference count | 2 |
| Source SHA-256 | 9843569b4698cb26d209987be483cd7b92b8442d6b07ab0cec2711154e086fb4 |
| Reference SHA-256 | 8af3970b0ad580a41ed24ee9a588e7fdf7edeb5b2ced52e076bf7309216f64d1 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```json
{
  "game": {
    "attendance": "20300",
    "capacity": "20500",
    "city": "Philadelphia",
    "day": "2",
    "dayname": "Sunday",
    "game_id": "4934",
    "month": "December",
    "season": "2018",
    "stadium": "Wells Fargo Center",
    "state": "Pennsylvania",
    "year": "2018"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "13",
          "AST": "3",
          "BLK": "1",
          "DOUBLE": "double",
          "DREB": "14",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "13",
          "FGM": "4",
          "FG_PCT": "31",
          "FTA": "8",
          "FTM": "7",
          "FT_PCT": "88",
          "MIN": "37",
          "OREB": "0",
          "PF": "3",
          "PTS": "15",
          "STL": "1",
          "TOV": "4",
          "TREB": "14",
          "first_name": "Joel",
          "last_name": "Embiid",
          "name": "Joel Embiid",
          "starter": "True"
        },
        {
          "+/-": "5",
          "AST": "6",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "10",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "10",
          "FGM": "8",
          "FG_PCT": "80",
          "FTA": "8",
          "FTM": "3",
          "FT_PCT": "38",
          "MIN": "37",
          "OREB": "2",
          "PF": "4",
          "PTS": "19",
          "STL": "2",
          "TOV": "3",
          "TREB": "12",
          "first_name": "Ben",
          "last_name": "Simmons",
          "name": "Ben Simmons",
          "starter": "True"
        },
        {
          "+/-": "7",
          "AST": "2",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "4",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "17",
          "FGM": "7",
          "FG_PCT": "41",
          "FTA": "8",
          "FTM": "7",
          "FT_PCT": "88",
          "MIN": "32",
          "OREB": "0",
          "PF": "3",
          "PTS": "21",
          "STL": "0",
          "TOV": "3",
          "TREB": "3",
          "first_name": "Jimmy",
          "last_name": "Butler",
          "name": "Jimmy Butler",
          "starter": "True"
        },
        {
          "+/-": "9",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "6",
          "FG3M": "3",
          "FG3_PCT": "50",
          "FGA": "17",
          "FGM": "9",
          "FG_PCT": "53",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "30",
          "OREB": "0",
          "PF": "5",
          "PTS": "24",
          "STL": "0",
          "TOV": "1",
          "TREB": "3",
          "first_name": "J.J.",
          "last_name": "Redick",
          "name": "J.J. Redick",
          "starter": "True"
        },
        {
          "+/-": "-5",
          "AST": "5",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "4",
          "FGM": "2",
          "FG_PCT": "50",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "27",
          "OREB": "1",
          "PF": "0",
          "PTS": "8",
          "STL": "0",
          "TOV": "0",
          "TREB": "7",
          "first_name": "Mike",
          "last_name": "Muscala",
          "name": "Mike Muscala",
          "starter": "True"
        },
        {
          "+/-": "16",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
          "FGM": "3",
          "FG_PCT": "75",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "31",
          "OREB": "0",
          "PF": "2",
          "PTS": "6",
          "STL": "0",
          "TOV": "1",
          "TREB": "3",
          "first_name": "T.J.",
          "last_name": "McConnell",
          "name": "T.J. McConnell",
          "starter": "False"
        },
        {
          "+/-": "-1",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "4",
          "FGM": "1",
          "FG_PCT": "25",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "17",
          "OREB": "0",
          "PF": "1",
          "PTS": "4",
          "STL": "0",
          "TOV": "3",
          "TREB": "0",
          "first_name": "Landry",
          "last_name": "Shamet",
          "name": "Landry Shamet",
          "starter": "False"
        },
        {
          "+/-": "1",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "4",
          "FGM": "2",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "15",
          "OREB": "0",
          "PF": "0",
          "PTS": "6",
          "STL": "2",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Furkan",
          "last_name": "Korkmaz",
          "name": "Furkan Korkmaz",
          "starter": "False"
        },
        {
          "+/-": "-5",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "1",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "10",
          "OREB": "0",
          "PF": "2",
          "PTS": "0",
          "STL": "0",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Amir",
          "last_name": "Johnson",
          "name": "Amir Johnson",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Demetrius",
          "last_name": "Jackson",
          "name": "Demetrius Jackson",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Shake",
          "last_name": "Milton",
          "name": "Shake Milton",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 3,
      "division": "Atlantic",
      "game_number": "25",
      "line_score": {
        "H1": {
          "AST": "46",
          "BLK": "11",
          "DREB": "1112",
          "FG3A": "46",
          "FG3M": "13",
          "FG3_PCT": "28",
          "FGA": "2019",
          "FGM": "811",
          "FG_PCT": "40",
          "FTA": "123",
          "FTM": "93",
          "FT_PCT": "76",
          "MIN": "6060",
          "OREB": "10",
          "PTS": "2628",
          "STL": "11",
          "TOV": "44",
          "TREB": "1122"
        },
        "H2": {
          "AST": "84",
          "BLK": "00",
          "DREB": "810",
          "FG3A": "93",
          "FG3M": "40",
          "FG3_PCT": "43",
          "FGA": "1916",
          "FGM": "107",
          "FG_PCT": "6",
          "FTA": "015",
          "FTM": "011",
          "FT_PCT": "73",
          "MIN": "6060",
          "OREB": "11",
          "PTS": "2425",
          "STL": "21",
          "TOV": "53",
          "TREB": "821"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "4",
          "BLK": "1",
          "DREB": "11",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "20",
          "FGM": "8",
          "FG_PCT": "40",
          "FTA": "12",
          "FTM": "9",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "1",
          "PTS": "26",
          "STL": "1",
          "TOV": "4",
          "TREB": "12"
        },
        "Q2": {
          "AST": "6",
          "BLK": "1",
          "DREB": "12",
          "FG3A": "6",
          "FG3M": "3",
          "FG3_PCT": "50",
          "FGA": "19",
          "FGM": "11",
          "FG_PCT": "58",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "0",
          "PTS": "28",
          "STL": "1",
          "TOV": "4",
          "TREB": "12"
        },
        "Q3": {
          "AST": "8",
          "BLK": "0",
          "DREB": "8",
          "FG3A": "9",
          "FG3M": "4",
          "FG3_PCT": "44",
          "FGA": "19",
          "FGM": "10",
          "FG_PCT": "53",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "60",
          "OREB": "1",
          "PTS": "24",
          "STL": "2",
          "TOV": "5",
          "TREB": "9"
        },
        "Q4": {
          "AST": "4",
          "BLK": "0",
          "DREB": "10",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "16",
          "FGM": "7",
          "FG_PCT": "44",
          "FTA": "15",
          "FTM": "11",
          "FT_PCT": "73",
          "MIN": "60",
          "OREB": "1",
          "PTS": "25",
          "STL": "1",
          "TOV": "3",
          "TREB": "11"
        },
        "game": {
          "AST": "22",
          "BLK": "2",
          "DREB": "41",
          "FG3A": "22",
          "FG3M": "8",
          "FG3_PCT": "36",
          "FGA": "74",
          "FGM": "36",
          "FG_PCT": "49",
          "FTA": "30",
          "FTM": "23",
          "FT_PCT": "77",
          "MIN": "4",
          "OREB": "3",
          "PF": "20",
          "PTS": "103",
          "STL": "5",
          "TOV": "16",
          "TREB": "44"
        }
      },
      "losses": "8",
      "name": "76ers",
      "next_game": {
        "city": "Toronto",
        "day": "5",
        "dayname": "Wednesday",
        "is_home": "False",
        "month": "December",
        "opponent_name": "Raptors",
        "opponent_place": "Toronto",
        "stadium": "Scotiabank Arena",
        "year": "2018"
      },
      "next_game_id": "5795",
      "place": "Philadelphia",
      "previous_game_id": "4933",
      "wins": "17"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "-12",
          "AST": "3",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "5",
          "FG3M": "2",
          "FG3_PCT": "40",
          "FGA": "14",
          "FGM": "4",
          "FG_PCT": "29",
          "FTA": "3",
          "FTM": "2",
          "FT_PCT": "67",
          "MIN": "38",
          "OREB": "0",
          "PF": "4",
          "PTS": "12",
          "STL": "1",
          "TOV": "4",
          "TREB": "4",
          "first_name": "Marc",
          "last_name": "Gasol",
          "name": "Marc Gasol",
          "starter": "True"
        },
        {
          "+/-": "-7",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "6",
          "FG3M": "3",
          "FG3_PCT": "50",
          "FGA": "17",
          "FGM": "6",
          "FG_PCT": "35",
          "FTA": "7",
          "FTM": "6",
          "FT_PCT": "86",
          "MIN": "33",
          "OREB": "0",
          "PF": "1",
          "PTS": "21",
          "STL": "1",
          "TOV": "1",
          "TREB": "2",
          "first_name": "Mike",
          "last_name": "Conley",
          "name": "Mike Conley",
          "starter": "True"
        },
        {
          "+/-": "-9",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "6",
          "FG3M": "3",
          "FG3_PCT": "50",
          "FGA": "9",
          "FGM": "4",
          "FG_PCT": "44",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "31",
          "OREB": "0",
          "PF": "1",
          "PTS": "12",
          "STL": "0",
          "TOV": "0",
          "TREB": "4",
          "first_name": "Garrett",
          "last_name": "Temple",
          "name": "Garrett Temple",
          "starter": "True"
        },
        {
          "+/-": "-6",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "2",
          "FG_PCT": "100",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "27",
          "OREB": "0",
          "PF": "3",
          "PTS": "5",
          "STL": "0",
          "TOV": "1",
          "TREB": "3",
          "first_name": "Kyle",
          "last_name": "Anderson",
          "name": "Kyle Anderson",
          "starter": "True"
        },
        {
          "+/-": "-6",
          "AST": "0",
          "BLK": "3",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "10",
          "FGM": "5",
          "FG_PCT": "50",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "23",
          "OREB": "1",
          "PF": "5",
          "PTS": "17",
          "STL": "1",
          "TOV": "2",
          "TREB": "3",
          "first_name": "Jaren",
          "last_name": "Jackson",
          "name": "Jaren Jackson",
          "starter": "True"
        },
        {
          "+/-": "6",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "10",
          "FGM": "6",
          "FG_PCT": "60",
          "FTA": "2",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "25",
          "OREB": "2",
          "PF": "4",
          "PTS": "14",
          "STL": "4",
          "TOV": "3",
          "TREB": "7",
          "first_name": "JaMychal",
          "last_name": "Green",
          "name": "JaMychal Green",
          "starter": "False"
        },
        {
          "+/-": "4",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "10",
          "FGM": "5",
          "FG_PCT": "50",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "20",
          "OREB": "0",
          "PF": "1",
          "PTS": "12",
          "STL": "0",
          "TOV": "2",
          "TREB": "2",
          "first_name": "MarShon",
          "last_name": "Brooks",
          "name": "MarShon Brooks",
          "starter": "False"
        },
        {
          "+/-": "-13",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "5",
          "FGM": "1",
          "FG_PCT": "20",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "20",
          "OREB": "0",
          "PF": "2",
          "PTS": "2",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Shelvin",
          "last_name": "Mack",
          "name": "Shelvin Mack",
          "starter": "False"
        },
        {
          "+/-": "2",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "8",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "14",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "1",
          "TREB": "8",
          "first_name": "Omri",
          "last_name": "Casspi",
          "name": "Omri Casspi",
          "starter": "False"
        },
        {
          "+/-": "1",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "4",
          "OREB": "0",
          "PF": "3",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Ivan",
          "last_name": "Rabb",
          "name": "Ivan Rabb",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Jevon",
          "last_name": "Carter",
          "name": "Jevon Carter",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Wayne",
          "last_name": "Selden",
          "name": "Wayne Selden",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "D.J.",
          "last_name": "Stephens",
          "name": "D.J. Stephens",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 6,
      "division": "Southwest",
      "game_number": "22",
      "line_score": {
        "H1": {
          "AST": "74",
          "BLK": "31",
          "DREB": "107",
          "FG3A": "85",
          "FG3M": "31",
          "FG3_PCT": "36",
          "FGA": "2217",
          "FGM": "106",
          "FG_PCT": "5",
          "FTA": "29",
          "FTM": "26",
          "FT_PCT": "90",
          "MIN": "6060",
          "OREB": "00",
          "PTS": "2519",
          "STL": "22",
          "TOV": "53",
          "TREB": "107"
        },
        "H2": {
          "AST": "35",
          "BLK": "21",
          "DREB": "69",
          "FG3A": "96",
          "FG3M": "52",
          "FG3_PCT": "54",
          "FGA": "1525",
          "FGM": "611",
          "FG_PCT": "40",
          "FTA": "84",
          "FTM": "73",
          "FT_PCT": "87",
          "MIN": "6060",
          "OREB": "03",
          "PTS": "2427",
          "STL": "21",
          "TOV": "42",
          "TREB": "72"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "7",
          "BLK": "3",
          "DREB": "10",
          "FG3A": "8",
          "FG3M": "3",
          "FG3_PCT": "38",
          "FGA": "22",
          "FGM": "10",
          "FG_PCT": "45",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "0",
          "PTS": "25",
          "STL": "2",
          "TOV": "5",
          "TREB": "10"
        },
        "Q2": {
          "AST": "4",
          "BLK": "1",
          "DREB": "7",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "17",
          "FGM": "6",
          "FG_PCT": "35",
          "FTA": "9",
          "FTM": "6",
          "FT_PCT": "67",
          "MIN": "60",
          "OREB": "0",
          "PTS": "19",
          "STL": "2",
          "TOV": "3",
          "TREB": "7"
        },
        "Q3": {
          "AST": "3",
          "BLK": "2",
          "DREB": "6",
          "FG3A": "9",
          "FG3M": "5",
          "FG3_PCT": "56",
          "FGA": "15",
          "FGM": "6",
          "FG_PCT": "40",
          "FTA": "8",
          "FTM": "7",
          "FT_PCT": "88",
          "MIN": "60",
          "OREB": "0",
          "PTS": "24",
          "STL": "2",
          "TOV": "4",
          "TREB": "6"
        },
        "Q4": {
          "AST": "5",
          "BLK": "1",
          "DREB": "9",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "25",
          "FGM": "11",
          "FG_PCT": "44",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "3",
          "PTS": "27",
          "STL": "1",
          "TOV": "2",
          "TREB": "12"
        },
        "game": {
          "AST": "19",
          "BLK": "7",
          "DREB": "32",
          "FG3A": "28",
          "FG3M": "11",
          "FG3_PCT": "39",
          "FGA": "79",
          "FGM": "33",
          "FG_PCT": "42",
          "FTA": "23",
          "FTM": "18",
          "FT_PCT": "78",
          "MIN": "4",
          "OREB": "3",
          "PF": "24",
          "PTS": "95",
          "STL": "7",
          "TOV": "14",
          "TREB": "35"
        }
      },
      "losses": "9",
      "name": "Grizzlies",
      "next_game": {
        "city": "Memphis",
        "day": "5",
        "dayname": "Wednesday",
        "is_home": "True",
        "month": "December",
        "opponent_name": "Clippers",
        "opponent_place": "Los Angeles",
        "stadium": "FedExForum",
        "year": "2018"
      },
      "next_game_id": "5177",
      "place": "Memphis",
      "previous_game_id": "5587",
      "wins": "13"
    }
  }
}
```

The parsed source text and structured source payload are identical for this case.

## Prepared-example metadata

```json
{
  "sportsett_id": "4934",
  "normalizer": "sportsett",
  "requested_split": "test",
  "hub_id": "GEM/sportsett_basketball",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The Philadelphia 76ers defeated the visiting Memphis Grizzlies, 103 - 95, at Wells Fargo Center on Sunday evening. The Sixers got out to a quick, 10 - 3, lead but the Grizzlies stuck with it, leading to a, 26 - 25, advantage for the home team, after one quarter. The 76ers stayed on top in the second, where they outscored the Grizzlies, 28 - 19, to take a, 54 - 44, lead by halftime. Things tightened up again in the second half, as both teams matched each other for 24 points in the third quarter, leaving the Sixers ahead by 10 heading into the fourth. The Grizzlies started the fourth quarter with a quick 9 - 1 run, to make it a two - point game. However, the 76ers answered right back, pushing their lead back to nine, with five minutes left. The Grizzlies cut it as close as a four - point deficit, but could not do better than that, as the 76ers held on to earn their fourth straight win. J.J. Redick led Philly with 24 points on 9 - of - 17 shooting, in 30 minutes. Jimmy Butler tallied 21 points, three rebounds, two assists and a block. Ben Simmons finished with 19 points, 12 rebounds, six assists and two steals, while Joel Embiid added 15 points, 14 rebounds, three assists, one steal and one block. Meanwhile, Mike Conley led the Grizzlies with 21 points, five assists, two rebounds, one steal and one block. Jaren Jackson Jr. followed up with 17 points, three rebounds, three blocks and a steal, while JaMychal Green tallied 14 points, seven rebounds and four steals. The Grizzlies (13 - 9) will look to bounce back as they play host to the Clippers on Tuesday. The 76ers (17 - 8) take on the Raptors in Toronto on Wednesday.
```

### Reference 2

```text
The Philadelphia 76ers defeated the visiting Memphis Grizzlies , 103 - 95 , at Wells Fargo Center on Sunday evening . The Sixers got out to a quick , 10 - 3 , lead but the Grizzlies stuck with it , leading to a , 26 - 25 , advantage for the home team , after one quarter . The 76ers stayed on top in the second , where they outscored the Grizzlies , 28 - 19 , to take a , 54 - 44 , lead by halftime . Things tightened up again in the second half , as both teams matched each other for 24 points in the third quarter , leaving the Sixers ahead by 10 heading into the fourth . The Grizzlies started the fourth quarter with a quick 9 - 1 run , to make it a two - point game . However , the 76ers answered right back , pushing their lead back to nine , with five minutes left . The Grizzlies cut it as close as a four - point deficit , but could not do better than that , as the 76ers held on to earn their fourth straight win . J.J. Redick led Philly with 24 points on 9 - of - 17 shooting , in 30 minutes . Jimmy Butler tallied 21 points , three rebounds , two assists and a block . Ben Simmons finished with 19 points , 12 rebounds , six assists and two steals , while Joel Embiid added 15 points , 14 rebounds , three assists , one steal and one block . Meanwhile , Mike Conley led the Grizzlies with 21 points , five assists , two rebounds , one steal and one block . Jaren Jackson Jr. followed up with 17 points , three rebounds , three blocks and a steal , while JaMychal Green tallied 14 points , seven rebounds and four steals . The Grizzlies ( 13 - 9 ) will look to bounce back as they play host to the Clippers on Tuesday . The 76ers ( 17 - 8 ) take on the Raptors in Toronto on Wednesday .
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4934__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 839.862 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 301 |
| Writer mode | llm_writer |
| Release status | approved |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 17 |
| Support sentences | 17 |
| Generation error | — |

#### Exact generated text

```text
The Philadelphia 76ers defeated the Memphis Grizzlies 103-95 on Sunday, December 2, 2018, at Wells Fargo Center.
The 2018-season contest finished with Philadelphia holding an eight-point margin over Memphis.
Philadelphia entered with a 17-8 record and third place in their conference, while Memphis arrived at 13-9 and sixth.
The matchup was the 76ers' 25th game of the season and the Grizzlies' 22nd.
The 76ers led after every quarter: 26-25 after the first, 54-44 at the half, 78-68 after the third and 103-95 after the fourth.
Philadelphia outscored Memphis 28-19 in the second quarter.
The third quarter was even at 24-24, and Memphis outscored the 76ers 27-25 in the fourth, but the final margin remained 103-95.
J.J. Redick led all scorers with 24 points and also topped the game with nine field goals made.
Jimmy Butler and Memphis's Mike Conley each scored 21 points, and Ben Simmons added 19.
Joel Embiid recorded 15 points, a game-high 14 rebounds and 14 defensive rebounds, while Simmons finished with 12 rebounds and a game-high six assists.
Memphis's JaMychal Green contributed 14 points and seven rebounds and led all players with four steals, and Jaren Jackson scored 17 points and led the game with three blocks.
Marc Gasol, Garrett Temple and MarShon Brooks each scored 12 points for Memphis.
Mike Muscala added eight points and seven rebounds for Philadelphia.
Joel Embiid and Jimmy Butler each converted a game-high seven free throws.
Philadelphia controlled the rebounding battle 44-35 and made 36 field goals to Memphis's 33.
Memphis countered from three-point range, making 11 threes to the 76ers' eight, with Redick, Conley and Temple each hitting a game-high three.
Both teams next play on Wednesday, December 5, 2018: the 76ers visit the Toronto Raptors at Scotiabank Arena, and the Grizzlies host the Los Angeles Clippers at FedExForum.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4934__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 7.579 |
| Prompt tokens | 8291 |
| Completion tokens | 626 |
| Total tokens | 8917 |
| Output words | 117 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The Philadelphia 76ers beat the Memphis Grizzlies 103–95 on Sunday, December 2, 2018, at Wells Fargo Center in Philadelphia.

- Philadelphia improved to 17–8; Memphis fell to 13–9.
- J.J. Redick led all scorers with 24 points. Jimmy Butler scored 21, Ben Simmons 19, and Joel Embiid 15.
- Joel Embiid recorded a double-double with 15 points and 14 rebounds; Ben Simmons also had a double-double with 19 points and 12 rebounds.
- Memphis was led by Mike Conley with 21 points; Jaren Jackson added 17.
- Philadelphia out-rebounded Memphis 44–35 and had more assists, 22–19.
- The 76ers shot 49% from the field; the Grizzlies shot 42%.
- Attendance was 20,300 in a 20,500-capacity arena.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4934__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 15.555 |
| Prompt tokens | 8328 |
| Completion tokens | 1584 |
| Total tokens | 9912 |
| Output words | 181 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The Philadelphia 76ers defeated the Memphis Grizzlies 103-95 on Sunday, December 2, 2018, at Wells Fargo Center. Philadelphia built a 54-44 halftime lead, paced by a 28-19 second quarter, and held on down the stretch to finish with the win in front of an announced crowd of 20,300.

J.J. Redick led the 76ers with 24 points on 9-of-17 shooting, including 3-of-6 from three-point range. Jimmy Butler added 21 points, while Ben Simmons recorded a double-double with 19 points and 12 rebounds to go with six assists. Joel Embiid also posted a double-double, finishing with 15 points and 14 rebounds. T.J. McConnell provided a boost off the bench with six points and a team-high plus-minus of plus-16.

Memphis was led by Mike Conley’s 21 points. Jaren Jackson added 17 points, and JaMychal Green supplied 14 points and seven rebounds off the bench. The Grizzlies shot 42 percent from the field and were outrebounded 44-35, while the 76ers shot 49 percent and converted 23 of 30 free throws. With the win, Philadelphia improved to 17-8, while Memphis fell to 13-9.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.123164356 | 0.443245487 | 0.843843844 | 0.275526742 | 0.258794534 | 0.867145121 | 0.161951184 | 0.109063067 | 0.007973887 | 0.888888889 |
| Raw-generic direct Flash | 0.030178491 | 0.224788032 | 0.810810811 | 0.240963855 | 0.167685443 | 0.814384043 | 0.198321849 | 0.033393375 | 0.010957376 | 1 |
| Task-aware direct Flash | 0.096014039 | 0.347515318 | 0.792792793 | 0.321138211 | 0.236620125 | 0.856875002 | 0.191163212 | 0.140728037 | 0.013212758 | 0.833333333 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “Philadelphia entered with a 17-8 record and third place in their conference, while Memphis arrived at 13-9 and sixth.”
     - The records are presented with incorrect pregame chronology. They total 25 and 22 games respectively, matching each team's game number for this contest, so they reflect the postgame records: Philadelphia improved to 17-8 and Memphis fell to 13-9.
  2. **TASK/FORMAT** — “The entire report is presented as one paragraph.”
     - The requested output mode was a multi-paragraph report, but the generated output contains only a single paragraph.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **TASK/FORMAT** — “The entire output is presented as one paragraph with inline dash-separated items.”
     - The requested output mode was a multi-paragraph report. The content should be organized into multiple prose paragraphs rather than a single inline list.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 12: `sportsett_basketball` / `4972`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | sportsett_basketball |
| Example ID | 4972 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source characters | 25481 |
| Reference count | 2 |
| Source SHA-256 | 0cacde0ec6e52b2d848617c50303cfbcf4953108fda6507d1b464c1d7f879c60 |
| Reference SHA-256 | 7b2425723ebb8a8b58771a694a63fc1224a9d256795fd6c293e8fbe98dbddadb |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```json
{
  "game": {
    "attendance": "17900",
    "capacity": "17500",
    "city": "Milwaukee",
    "day": "23",
    "dayname": "Friday",
    "game_id": "4972",
    "month": "November",
    "season": "2018",
    "stadium": "Fiserv Forum",
    "state": "Wisconsin",
    "year": "2018"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "7",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "9",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "16",
          "FGM": "14",
          "FG_PCT": "88",
          "FTA": "12",
          "FTM": "7",
          "FT_PCT": "58",
          "MIN": "36",
          "OREB": "1",
          "PF": "2",
          "PTS": "35",
          "STL": "1",
          "TOV": "4",
          "TREB": "10",
          "first_name": "Giannis",
          "last_name": "Antetokounmpo",
          "name": "Giannis Antetokounmpo",
          "starter": "True"
        },
        {
          "+/-": "-12",
          "AST": "0",
          "BLK": "4",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "12",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "17",
          "FGM": "3",
          "FG_PCT": "18",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "32",
          "OREB": "0",
          "PF": "3",
          "PTS": "7",
          "STL": "0",
          "TOV": "0",
          "TREB": "5",
          "first_name": "Brook",
          "last_name": "Lopez",
          "name": "Brook Lopez",
          "starter": "True"
        },
        {
          "+/-": "-3",
          "AST": "7",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "9",
          "FGM": "4",
          "FG_PCT": "44",
          "FTA": "4",
          "FTM": "2",
          "FT_PCT": "50",
          "MIN": "30",
          "OREB": "0",
          "PF": "3",
          "PTS": "12",
          "STL": "1",
          "TOV": "4",
          "TREB": "3",
          "first_name": "Eric",
          "last_name": "Bledsoe",
          "name": "Eric Bledsoe",
          "starter": "True"
        },
        {
          "+/-": "-14",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "3",
          "FG3M": "3",
          "FG3_PCT": "100",
          "FGA": "10",
          "FGM": "8",
          "FG_PCT": "80",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "30",
          "OREB": "1",
          "PF": "0",
          "PTS": "22",
          "STL": "1",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Malcolm",
          "last_name": "Brogdon",
          "name": "Malcolm Brogdon",
          "starter": "True"
        },
        {
          "+/-": "-7",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "9",
          "FGM": "4",
          "FG_PCT": "44",
          "FTA": "5",
          "FTM": "5",
          "FT_PCT": "100",
          "MIN": "29",
          "OREB": "0",
          "PF": "4",
          "PTS": "15",
          "STL": "1",
          "TOV": "4",
          "TREB": "6",
          "first_name": "Khris",
          "last_name": "Middleton",
          "name": "Khris Middleton",
          "starter": "True"
        },
        {
          "+/-": "14",
          "AST": "2",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "7",
          "FGM": "3",
          "FG_PCT": "43",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "21",
          "OREB": "0",
          "PF": "0",
          "PTS": "8",
          "STL": "2",
          "TOV": "0",
          "TREB": "5",
          "first_name": "Pat",
          "last_name": "Connaughton",
          "name": "Pat Connaughton",
          "starter": "False"
        },
        {
          "+/-": "7",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "4",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "19",
          "OREB": "1",
          "PF": "1",
          "PTS": "2",
          "STL": "0",
          "TOV": "0",
          "TREB": "4",
          "first_name": "Tony",
          "last_name": "Snell",
          "name": "Tony Snell",
          "starter": "False"
        },
        {
          "+/-": "5",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "8",
          "FGM": "4",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "16",
          "OREB": "3",
          "PF": "3",
          "PTS": "9",
          "STL": "0",
          "TOV": "2",
          "TREB": "4",
          "first_name": "Ersan",
          "last_name": "İlyasova",
          "name": "Ersan İlyasova",
          "starter": "False"
        },
        {
          "+/-": "-8",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "3",
          "FGM": "1",
          "FG_PCT": "33",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "8",
          "OREB": "0",
          "PF": "1",
          "PTS": "2",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Sterling",
          "last_name": "Brown",
          "name": "Sterling Brown",
          "starter": "False"
        },
        {
          "+/-": "-5",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
          "FGM": "1",
          "FG_PCT": "25",
          "FTA": "2",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "8",
          "OREB": "1",
          "PF": "0",
          "PTS": "2",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Thon",
          "last_name": "Maker",
          "name": "Thon Maker",
          "starter": "False"
        },
        {
          "+/-": "6",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "6",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Matthew",
          "last_name": "Dellavedova",
          "name": "Matthew Dellavedova",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Jaylen",
          "last_name": "Morris",
          "name": "Jaylen Morris",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Christian",
          "last_name": "Wood",
          "name": "Christian Wood",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 2,
      "division": "Central",
      "game_number": "18",
      "line_score": {
        "H1": {
          "AST": "108",
          "BLK": "02",
          "DREB": "99",
          "FG3A": "1410",
          "FG3M": "32",
          "FG3_PCT": "2",
          "FGA": "2323",
          "FGM": "1111",
          "FG_PCT": "48",
          "FTA": "79",
          "FTM": "57",
          "FT_PCT": "72",
          "MIN": "6060",
          "OREB": "14",
          "PTS": "3031",
          "STL": "31",
          "TOV": "35",
          "TREB": "113"
        },
        "H2": {
          "AST": "57",
          "BLK": "23",
          "DREB": "711",
          "FG3A": "1010",
          "FG3M": "32",
          "FG3_PCT": "3",
          "FGA": "2219",
          "FGM": "128",
          "FG_PCT": "6",
          "FTA": "68",
          "FTM": "26",
          "FT_PCT": "38",
          "MIN": "6060",
          "OREB": "11",
          "PTS": "2924",
          "STL": "11",
          "TOV": "24",
          "TREB": "722"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "10",
          "BLK": "0",
          "DREB": "9",
          "FG3A": "14",
          "FG3M": "3",
          "FG3_PCT": "21",
          "FGA": "23",
          "FGM": "11",
          "FG_PCT": "48",
          "FTA": "7",
          "FTM": "5",
          "FT_PCT": "71",
          "MIN": "60",
          "OREB": "1",
          "PTS": "30",
          "STL": "3",
          "TOV": "3",
          "TREB": "10"
        },
        "Q2": {
          "AST": "8",
          "BLK": "2",
          "DREB": "9",
          "FG3A": "10",
          "FG3M": "2",
          "FG3_PCT": "20",
          "FGA": "23",
          "FGM": "11",
          "FG_PCT": "48",
          "FTA": "9",
          "FTM": "7",
          "FT_PCT": "78",
          "MIN": "60",
          "OREB": "4",
          "PTS": "31",
          "STL": "1",
          "TOV": "5",
          "TREB": "13"
        },
        "Q3": {
          "AST": "5",
          "BLK": "2",
          "DREB": "7",
          "FG3A": "10",
          "FG3M": "3",
          "FG3_PCT": "30",
          "FGA": "22",
          "FGM": "12",
          "FG_PCT": "55",
          "FTA": "6",
          "FTM": "2",
          "FT_PCT": "33",
          "MIN": "60",
          "OREB": "1",
          "PTS": "29",
          "STL": "1",
          "TOV": "2",
          "TREB": "8"
        },
        "Q4": {
          "AST": "7",
          "BLK": "3",
          "DREB": "11",
          "FG3A": "10",
          "FG3M": "2",
          "FG3_PCT": "20",
          "FGA": "19",
          "FGM": "8",
          "FG_PCT": "42",
          "FTA": "8",
          "FTM": "6",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "1",
          "PTS": "24",
          "STL": "1",
          "TOV": "4",
          "TREB": "12"
        },
        "game": {
          "AST": "30",
          "BLK": "7",
          "DREB": "36",
          "FG3A": "44",
          "FG3M": "10",
          "FG3_PCT": "23",
          "FGA": "87",
          "FGM": "42",
          "FG_PCT": "48",
          "FTA": "30",
          "FTM": "20",
          "FT_PCT": "67",
          "MIN": "4",
          "OREB": "7",
          "PF": "17",
          "PTS": "114",
          "STL": "6",
          "TOV": "14",
          "TREB": "43"
        }
      },
      "losses": "5",
      "name": "Bucks",
      "next_game": {
        "city": "Milwaukee",
        "day": "24",
        "dayname": "Saturday",
        "is_home": "True",
        "month": "November",
        "opponent_name": "Spurs",
        "opponent_place": "San Antonio",
        "stadium": "Fiserv Forum",
        "year": "2018"
      },
      "next_game_id": "4973",
      "place": "Milwaukee",
      "previous_game_id": "4971",
      "wins": "13"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "1",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "11",
          "FG3A": "7",
          "FG3M": "3",
          "FG3_PCT": "43",
          "FGA": "10",
          "FGM": "4",
          "FG_PCT": "40",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "40",
          "OREB": "0",
          "PF": "3",
          "PTS": "13",
          "STL": "2",
          "TOV": "2",
          "TREB": "11",
          "first_name": "Trevor",
          "last_name": "Ariza",
          "name": "Trevor Ariza",
          "starter": "True"
        },
        {
          "+/-": "14",
          "AST": "7",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "26",
          "FGM": "13",
          "FG_PCT": "50",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "39",
          "OREB": "0",
          "PF": "4",
          "PTS": "29",
          "STL": "3",
          "TOV": "3",
          "TREB": "4",
          "first_name": "Devin",
          "last_name": "Booker",
          "name": "Devin Booker",
          "starter": "True"
        },
        {
          "+/-": "2",
          "AST": "2",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "13",
          "FGM": "8",
          "FG_PCT": "62",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "31",
          "OREB": "1",
          "PF": "5",
          "PTS": "19",
          "STL": "1",
          "TOV": "0",
          "TREB": "5",
          "first_name": "T.J.",
          "last_name": "Warren",
          "name": "T.J. Warren",
          "starter": "True"
        },
        {
          "+/-": "10",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "13",
          "FGM": "8",
          "FG_PCT": "62",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "30",
          "OREB": "3",
          "PF": "3",
          "PTS": "17",
          "STL": "0",
          "TOV": "1",
          "TREB": "7",
          "first_name": "Deandre",
          "last_name": "Ayton",
          "name": "Deandre Ayton",
          "starter": "True"
        },
        {
          "+/-": "7",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "2",
          "FGM": "1",
          "FG_PCT": "50",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "24",
          "OREB": "0",
          "PF": "2",
          "PTS": "4",
          "STL": "0",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Mikal",
          "last_name": "Bridges",
          "name": "Mikal Bridges",
          "starter": "True"
        },
        {
          "+/-": "-8",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "13",
          "FGM": "5",
          "FG_PCT": "38",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "23",
          "OREB": "0",
          "PF": "2",
          "PTS": "11",
          "STL": "1",
          "TOV": "3",
          "TREB": "3",
          "first_name": "Jamal",
          "last_name": "Crawford",
          "name": "Jamal Crawford",
          "starter": "False"
        },
        {
          "+/-": "-8",
          "AST": "0",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
          "FGM": "4",
          "FG_PCT": "100",
          "FTA": "5",
          "FTM": "4",
          "FT_PCT": "80",
          "MIN": "17",
          "OREB": "2",
          "PF": "2",
          "PTS": "12",
          "STL": "1",
          "TOV": "1",
          "TREB": "4",
          "first_name": "Richaun",
          "last_name": "Holmes",
          "name": "Richaun Holmes",
          "starter": "False"
        },
        {
          "+/-": "-2",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "4",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "5",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "16",
          "OREB": "0",
          "PF": "1",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Isaiah",
          "last_name": "Canaan",
          "name": "Isaiah Canaan",
          "starter": "False"
        },
        {
          "+/-": "-6",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "1",
          "FG3M": "1",
          "FG3_PCT": "100",
          "FGA": "4",
          "FGM": "2",
          "FG_PCT": "50",
          "FTA": "7",
          "FTM": "6",
          "FT_PCT": "86",
          "MIN": "15",
          "OREB": "0",
          "PF": "3",
          "PTS": "11",
          "STL": "0",
          "TOV": "1",
          "TREB": "2",
          "first_name": "Josh",
          "last_name": "Jackson",
          "name": "Josh Jackson",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Elie",
          "last_name": "Okobo",
          "name": "Elie Okobo",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Troy",
          "last_name": "Daniels",
          "name": "Troy Daniels",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Ryan",
          "last_name": "Anderson",
          "name": "Ryan Anderson",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Dragan",
          "last_name": "Bender",
          "name": "Dragan Bender",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 15,
      "division": "Pacific",
      "game_number": "18",
      "line_score": {
        "H1": {
          "AST": "84",
          "BLK": "12",
          "DREB": "87",
          "FG3A": "65",
          "FG3M": "22",
          "FG3_PCT": "34",
          "FGA": "2321",
          "FGM": "1411",
          "FG_PCT": "61",
          "FTA": "411",
          "FTM": "46",
          "FT_PCT": "11",
          "MIN": "6060",
          "OREB": "02",
          "PTS": "3430",
          "STL": "22",
          "TOV": "32",
          "TREB": "89"
        },
        "H2": {
          "AST": "45",
          "BLK": "01",
          "DREB": "118",
          "FG3A": "105",
          "FG3M": "32",
          "FG3_PCT": "30",
          "FGA": "2224",
          "FGM": "911",
          "FG_PCT": "41",
          "FTA": "61",
          "FTM": "61",
          "FT_PCT": "100",
          "MIN": "6060",
          "OREB": "31",
          "PTS": "2725",
          "STL": "13",
          "TOV": "42",
          "TREB": "149"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "8",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "23",
          "FGM": "14",
          "FG_PCT": "61",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "0",
          "PTS": "34",
          "STL": "2",
          "TOV": "3",
          "TREB": "8"
        },
        "Q2": {
          "AST": "4",
          "BLK": "2",
          "DREB": "7",
          "FG3A": "5",
          "FG3M": "2",
          "FG3_PCT": "40",
          "FGA": "21",
          "FGM": "11",
          "FG_PCT": "52",
          "FTA": "11",
          "FTM": "6",
          "FT_PCT": "55",
          "MIN": "60",
          "OREB": "2",
          "PTS": "30",
          "STL": "2",
          "TOV": "2",
          "TREB": "9"
        },
        "Q3": {
          "AST": "4",
          "BLK": "0",
          "DREB": "11",
          "FG3A": "10",
          "FG3M": "3",
          "FG3_PCT": "30",
          "FGA": "22",
          "FGM": "9",
          "FG_PCT": "41",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "3",
          "PTS": "27",
          "STL": "1",
          "TOV": "4",
          "TREB": "14"
        },
        "Q4": {
          "AST": "5",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "5",
          "FG3M": "2",
          "FG3_PCT": "40",
          "FGA": "24",
          "FGM": "11",
          "FG_PCT": "46",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "1",
          "PTS": "25",
          "STL": "3",
          "TOV": "2",
          "TREB": "9"
        },
        "game": {
          "AST": "21",
          "BLK": "4",
          "DREB": "34",
          "FG3A": "26",
          "FG3M": "9",
          "FG3_PCT": "35",
          "FGA": "90",
          "FGM": "45",
          "FG_PCT": "50",
          "FTA": "22",
          "FTM": "17",
          "FT_PCT": "77",
          "MIN": "4",
          "OREB": "6",
          "PF": "25",
          "PTS": "116",
          "STL": "8",
          "TOV": "11",
          "TREB": "40"
        }
      },
      "losses": "14",
      "name": "Suns",
      "next_game": {
        "city": "Detroit",
        "day": "25",
        "dayname": "Sunday",
        "is_home": "False",
        "month": "November",
        "opponent_name": "Pistons",
        "opponent_place": "Detroit",
        "stadium": "Little Caesars Arena",
        "year": "2018"
      },
      "next_game_id": "5749",
      "place": "Phoenix",
      "previous_game_id": "5012",
      "wins": "4"
    }
  }
}
```

The parsed source text and structured source payload are identical for this case.

## Prepared-example metadata

```json
{
  "sportsett_id": "4972",
  "normalizer": "sportsett",
  "requested_split": "test",
  "hub_id": "GEM/sportsett_basketball",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The Phoenix Suns defeated the Milwaukee Bucks, 116 - 114, at Fiserv Forum on Friday evening. The Suns (4 - 14) came into Saturday's contest still seeking their first road win of the season, and facing quite the uphill battle versus a Bucks (13 - 5) squad that had only dropped one home game. However, Phoenix made a statement by taking a 64 - 61 halftime lead, and they proved it wasn't a fluke by essentially hanging with Milwaukee basket for basket in the second half. The game was deadlocked at 114 - 114 when Jamal Crawford drained 17 - foot jumper with 1 seconds remaining to give the Suns an upset win. Devin Booker led the way with 29 points, a total he supplemented with seven assists, four rebounds and three steals. T.J. Warren provided 19 points, five rebounds, two assists, one steal and one block. Deandre Ayton managed 17 points, seven rebounds and three assists. Trevor Ariza totaled 13 points, 11 rebounds, three assists and two steals. Richaun Holmes led the bench with 12 points, Josh Jackson and Crawford each pitched in 11 points. Giannis Antetokounmpo paced the Bucks with 35 points and added 10 rebounds, three assists and one steal. Malcolm Brogdon totaled 22 points, four assists, three rebounds and one steal. Khris Middleton collected 15 points, six rebounds, four assists and one steal. Eric Bledsoe filled out the stat sheet with 12 points, seven assists, three rebounds, one steal and one block. Ersan Ilyasova led the bench with nine points, four rebounds and three assists. The Suns next pay a visit to the Detroit Pistons on Sunday afternoon, while the Bucks remain home and take on the San Antonio Spurs in a Saturday night showdown.
```

### Reference 2

```text
The Phoenix Suns defeated the Milwaukee Bucks , 116 - 114 , at Fiserv Forum on Friday evening . The Suns ( 4 - 14 ) came into Saturday 's contest still seeking their first road win of the season , and facing quite the uphill battle versus a Bucks ( 13 - 5 ) squad that had only dropped one home game . However , Phoenix made a statement by taking a 64 - 61 halftime lead , and they proved it was n't a fluke by essentially hanging with Milwaukee basket for basket in the second half . The game was deadlocked at 114 - 114 when Jamal Crawford drained 17 - foot jumper with 1 seconds remaining to give the Suns an upset win . Devin Booker led the way with 29 points , a total he supplemented with seven assists , four rebounds and three steals . T.J. Warren provided 19 points , five rebounds , two assists , one steal and one block . Deandre Ayton managed 17 points , seven rebounds and three assists . Trevor Ariza totaled 13 points , 11 rebounds , three assists and two steals . Richaun Holmes led the bench with 12 points , Josh Jackson and Crawford each pitched in 11 points . Giannis Antetokounmpo paced the Bucks with 35 points and added 10 rebounds , three assists and one steal . Malcolm Brogdon totaled 22 points , four assists , three rebounds and one steal . Khris Middleton collected 15 points , six rebounds , four assists and one steal . Eric Bledsoe filled out the stat sheet with 12 points , seven assists , three rebounds , one steal and one block . Ersan Ilyasova led the bench with nine points , four rebounds and three assists . The Suns next pay a visit to the Detroit Pistons on Sunday afternoon , while the Bucks remain home and take on the San Antonio Spurs in a Saturday night showdown .
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4972__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 1019.143 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 314 |
| Writer mode | auditor_repaired |
| Release status | approved |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 1 |
| Audit support rate | 1 |
| Mapped support sentences | 15 |
| Support sentences | 15 |
| Generation error | — |

#### Exact generated text

```text
The Phoenix Suns defeated the Milwaukee Bucks 116-114 at Fiserv Forum on Friday, November 23, 2018, a game decided by two points.
The Suns led 34-30 after the first quarter, 64-61 at halftime and 91-90 after three quarters before closing out the win with a 25-24 fourth quarter.
Milwaukee entered with a 13-5 record and a conference standing of 2, while Phoenix arrived at 4-14 with a conference standing of 15; both teams were playing their 18th game.
Giannis Antetokounmpo led all scorers with 35 points, ahead of Devin Booker's 29, Malcolm Brogdon's 22 and T.J. Warren's 19.
Antetokounmpo's total came on 14 made field goals in 16 attempts, while Booker needed 26 attempts for his 13 makes and 29 points.
Deandre Ayton added 17 points for Phoenix and Khris Middleton 15 for Milwaukee, while Eric Bledsoe and Booker each recorded a game-high seven assists.
Antetokounmpo also pulled down 10 rebounds and dished out three assists, while Ayton contributed seven rebounds and three assists.
The Bucks attempted 44 three-pointers to the Suns' 26 but converted only one more, 10 to 9.
Milwaukee also finished with a 30-21 edge in assists and led the rebounding battle 43-40, including 36-34 on the defensive glass.
At the foul line, the Bucks made 20 of 30 free throws, while the Suns made 17 of 22.
Phoenix nevertheless finished with more made field goals, 45 to 42, and more steals, 8 to 6.
The Bucks held a 7-6 edge in offensive rebounds and blocked seven shots to the Suns' four.
Trevor Ariza led all players with 11 rebounds and added 13 points and two steals, while Brook Lopez blocked four shots for Milwaukee.
Malcolm Brogdon and Ariza each made three three-pointers, the game high.
Both teams face quick turnarounds: Milwaukee hosts the Spurs on Saturday, November 24, and Phoenix visits the Pistons in Detroit on Sunday, November 25.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4972__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 9.700 |
| Prompt tokens | 8718 |
| Completion tokens | 757 |
| Total tokens | 9475 |
| Output words | 117 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The strongest supported findings from the supplied data:

- The Phoenix Suns defeated the Milwaukee Bucks 116–114.
- The game was played at Fiserv Forum in Milwaukee, Wisconsin, on Friday, November 23, 2018.
- Reported attendance was 17,900, which exceeded the listed stadium capacity of 17,500.
- Giannis Antetokounmpo led all scorers with 35 points and recorded a double-double with 10 rebounds.
- Devin Booker led the Suns with 29 points.
- The Bucks entered the game with a 13–5 record; the Suns entered with a 4–14 record.
- The Suns shot 50% from the field overall, while the Bucks shot 48%.
- The Suns committed 11 turnovers to the Bucks’ 14 and recorded 8 steals to the Bucks’ 6.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4972__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 13.695 |
| Prompt tokens | 8755 |
| Completion tokens | 1377 |
| Total tokens | 10132 |
| Output words | 195 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The Phoenix Suns defeated the Milwaukee Bucks 116-114 on Friday, November 23, 2018, at Fiserv Forum in Milwaukee. The Suns improved to 4-14 with the win, while the Bucks fell to 13-5. Devin Booker led Phoenix with 29 points, adding 7 assists and 3 steals, and T.J. Warren contributed 19 points for the visiting side.

Milwaukee’s Giannis Antetokounmpo posted a double-double with a game-high 35 points and 10 rebounds, but the Bucks could not overcome poor outside shooting. They went 10-for-44 from three-point range, including an 0-for-12 night for Brook Lopez, who finished with 7 points on 3-of-17 shooting. Malcolm Brogdon was efficient for Milwaukee, scoring 22 points on 8-of-10 shooting.

The Suns were paced by balanced scoring behind Booker, with Deandre Ayton adding 17 points and 7 rebounds and Trevor Ariza registering a double-double with 13 points and 11 rebounds. Phoenix shot 50 percent from the field and committed only 11 turnovers, while the Bucks had 14 turnovers and shot 48 percent. The Suns led 34-30 after the first quarter, held a 64-61 edge at halftime, and then answered every Milwaukee push in the second half. The attendance was reported as 17,900.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.122243808 | 0.456099551 | 0.898876404 | 0.236245955 | 0.289480012 | 0.854462206 | 0.141306967 | 0.067963597 | 0.007717797 | 0.9375 |
| Raw-generic direct Flash | 0.038849609 | 0.225524924 | 0.818619583 | 0.202970297 | 0.149443857 | 0.822810411 | 0.259092748 | 0.014980112 | 0.014980112 | 1 |
| Task-aware direct Flash | 0.123619476 | 0.353431742 | 0.812199037 | 0.256513026 | 0.248356751 | 0.851003826 | 0.196784556 | 0.032350402 | 0.006739938 | 1 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “Milwaukee entered with a 13-5 record and a conference standing of 2, while Phoenix arrived at 4-14 with a conference standing of 15”
     - The 13-5 and 4-14 records total 18 games and therefore cannot be the teams' records entering their 18th game. They should be presented as postgame records (or the unsupported pregame framing should be removed).
  2. **TASK/FORMAT** — “The entire report is presented as a single paragraph.”
     - The requested output mode was a multi-paragraph report, but the generated report contains only one paragraph.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “The Bucks entered the game with a 13–5 record; the Suns entered with a 4–14 record.”
     - The records are associated with each team's 18th game and include this result: Milwaukee finished the game 13–5 after losing, while Phoenix finished 4–14 after winning. Therefore, they were not the teams' entering records.
  2. **TASK/FORMAT** — “The strongest supported findings from the supplied data: - The Phoenix Suns defeated ...”
     - The request specified a multi-paragraph report, but the output is a single inline list rather than multiple report paragraphs.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “but the Bucks could not overcome poor outside shooting.”
     - The source supports Milwaukee's 10-for-44 three-point shooting, but a box score alone does not establish that this was a causal barrier that produced the loss.
  2. **CONTEXT** — “then answered every Milwaukee push in the second half.”
     - The source provides quarter totals but no play-by-play sequence, so it cannot verify every Milwaukee push or a corresponding Phoenix response.

---

# Case 13: `sportsett_basketball` / `4975`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | sportsett_basketball |
| Example ID | 4975 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source characters | 25494 |
| Reference count | 2 |
| Source SHA-256 | b60a1157885c13c3d5467bfd71b333b68bd9c30a7bd539621aa42b60269217f6 |
| Reference SHA-256 | 49f37d9b10914af3a004f6eeec28995b222f8955d4b9b585fbdb00dcb7ed5532 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```json
{
  "game": {
    "attendance": "16500",
    "capacity": "17500",
    "city": "Milwaukee",
    "day": "5",
    "dayname": "Wednesday",
    "game_id": "4975",
    "month": "December",
    "season": "2018",
    "stadium": "Fiserv Forum",
    "state": "Wisconsin",
    "year": "2018"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "22",
          "AST": "1",
          "BLK": "3",
          "DOUBLE": "none",
          "DREB": "8",
          "FG3A": "5",
          "FG3M": "2",
          "FG3_PCT": "40",
          "FGA": "5",
          "FGM": "2",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "26",
          "OREB": "0",
          "PF": "2",
          "PTS": "6",
          "STL": "1",
          "TOV": "0",
          "TREB": "8",
          "first_name": "Brook",
          "last_name": "Lopez",
          "name": "Brook Lopez",
          "starter": "True"
        },
        {
          "+/-": "22",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "12",
          "FGM": "6",
          "FG_PCT": "50",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "26",
          "OREB": "1",
          "PF": "4",
          "PTS": "15",
          "STL": "1",
          "TOV": "5",
          "TREB": "7",
          "first_name": "Giannis",
          "last_name": "Antetokounmpo",
          "name": "Giannis Antetokounmpo",
          "starter": "True"
        },
        {
          "+/-": "14",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "17",
          "FGM": "10",
          "FG_PCT": "59",
          "FTA": "5",
          "FTM": "5",
          "FT_PCT": "100",
          "MIN": "26",
          "OREB": "0",
          "PF": "2",
          "PTS": "27",
          "STL": "3",
          "TOV": "1",
          "TREB": "3",
          "first_name": "Eric",
          "last_name": "Bledsoe",
          "name": "Eric Bledsoe",
          "starter": "True"
        },
        {
          "+/-": "21",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "5",
          "FGM": "2",
          "FG_PCT": "40",
          "FTA": "7",
          "FTM": "7",
          "FT_PCT": "100",
          "MIN": "24",
          "OREB": "1",
          "PF": "1",
          "PTS": "11",
          "STL": "2",
          "TOV": "1",
          "TREB": "7",
          "first_name": "Tony",
          "last_name": "Snell",
          "name": "Tony Snell",
          "starter": "True"
        },
        {
          "+/-": "14",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "10",
          "FGM": "5",
          "FG_PCT": "50",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "21",
          "OREB": "0",
          "PF": "1",
          "PTS": "14",
          "STL": "1",
          "TOV": "2",
          "TREB": "6",
          "first_name": "Malcolm",
          "last_name": "Brogdon",
          "name": "Malcolm Brogdon",
          "starter": "True"
        },
        {
          "+/-": "4",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "8",
          "FGM": "3",
          "FG_PCT": "38",
          "FTA": "6",
          "FTM": "3",
          "FT_PCT": "50",
          "MIN": "21",
          "OREB": "0",
          "PF": "3",
          "PTS": "11",
          "STL": "0",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Thon",
          "last_name": "Maker",
          "name": "Thon Maker",
          "starter": "False"
        },
        {
          "+/-": "11",
          "AST": "6",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "20",
          "OREB": "0",
          "PF": "4",
          "PTS": "2",
          "STL": "0",
          "TOV": "3",
          "TREB": "1",
          "first_name": "Matthew",
          "last_name": "Dellavedova",
          "name": "Matthew Dellavedova",
          "starter": "False"
        },
        {
          "+/-": "4",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "3",
          "FG3_PCT": "75",
          "FGA": "6",
          "FGM": "4",
          "FG_PCT": "67",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "19",
          "OREB": "1",
          "PF": "0",
          "PTS": "11",
          "STL": "1",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Sterling",
          "last_name": "Brown",
          "name": "Sterling Brown",
          "starter": "False"
        },
        {
          "+/-": "6",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "3",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "18",
          "OREB": "0",
          "PF": "1",
          "PTS": "0",
          "STL": "1",
          "TOV": "1",
          "TREB": "2",
          "first_name": "Pat",
          "last_name": "Connaughton",
          "name": "Pat Connaughton",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "5",
          "FGM": "1",
          "FG_PCT": "20",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "16",
          "OREB": "0",
          "PF": "0",
          "PTS": "3",
          "STL": "2",
          "TOV": "2",
          "TREB": "2",
          "first_name": "Donte",
          "last_name": "DiVincenzo",
          "name": "Donte DiVincenzo",
          "starter": "False"
        },
        {
          "+/-": "-3",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "3",
          "FGM": "2",
          "FG_PCT": "67",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "7",
          "OREB": "1",
          "PF": "0",
          "PTS": "6",
          "STL": "0",
          "TOV": "0",
          "TREB": "4",
          "first_name": "Christian",
          "last_name": "Wood",
          "name": "Christian Wood",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "3",
          "FGM": "1",
          "FG_PCT": "33",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "6",
          "OREB": "0",
          "PF": "0",
          "PTS": "2",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Jaylen",
          "last_name": "Morris",
          "name": "Jaylen Morris",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "3",
          "FGM": "2",
          "FG_PCT": "67",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "5",
          "OREB": "0",
          "PF": "3",
          "PTS": "7",
          "STL": "1",
          "TOV": "0",
          "TREB": "0",
          "first_name": "D.J.",
          "last_name": "Wilson",
          "name": "D.J. Wilson",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 2,
      "division": "Central",
      "game_number": "23",
      "line_score": {
        "H1": {
          "AST": "57",
          "BLK": "10",
          "DREB": "118",
          "FG3A": "1110",
          "FG3M": "25",
          "FG3_PCT": "2",
          "FGA": "2420",
          "FGM": "109",
          "FG_PCT": "5",
          "FTA": "84",
          "FTM": "83",
          "FT_PCT": "99",
          "MIN": "6060",
          "OREB": "11",
          "PTS": "3026",
          "STL": "26",
          "TOV": "16",
          "TREB": "129"
        },
        "H2": {
          "AST": "58",
          "BLK": "30",
          "DREB": "149",
          "FG3A": "119",
          "FG3M": "43",
          "FG3_PCT": "36",
          "FGA": "1919",
          "FGM": "109",
          "FG_PCT": "6",
          "FTA": "513",
          "FTM": "410",
          "FT_PCT": "80",
          "MIN": "6060",
          "OREB": "11",
          "PTS": "2831",
          "STL": "23",
          "TOV": "53",
          "TREB": "160"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "5",
          "BLK": "1",
          "DREB": "11",
          "FG3A": "11",
          "FG3M": "2",
          "FG3_PCT": "18",
          "FGA": "24",
          "FGM": "10",
          "FG_PCT": "42",
          "FTA": "8",
          "FTM": "8",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "1",
          "PTS": "30",
          "STL": "2",
          "TOV": "1",
          "TREB": "12"
        },
        "Q2": {
          "AST": "7",
          "BLK": "0",
          "DREB": "8",
          "FG3A": "10",
          "FG3M": "5",
          "FG3_PCT": "50",
          "FGA": "20",
          "FGM": "9",
          "FG_PCT": "45",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "1",
          "PTS": "26",
          "STL": "6",
          "TOV": "6",
          "TREB": "9"
        },
        "Q3": {
          "AST": "5",
          "BLK": "3",
          "DREB": "14",
          "FG3A": "11",
          "FG3M": "4",
          "FG3_PCT": "36",
          "FGA": "19",
          "FGM": "10",
          "FG_PCT": "53",
          "FTA": "5",
          "FTM": "4",
          "FT_PCT": "80",
          "MIN": "60",
          "OREB": "1",
          "PTS": "28",
          "STL": "2",
          "TOV": "5",
          "TREB": "15"
        },
        "Q4": {
          "AST": "8",
          "BLK": "0",
          "DREB": "9",
          "FG3A": "9",
          "FG3M": "3",
          "FG3_PCT": "33",
          "FGA": "19",
          "FGM": "9",
          "FG_PCT": "47",
          "FTA": "13",
          "FTM": "10",
          "FT_PCT": "77",
          "MIN": "60",
          "OREB": "1",
          "PTS": "31",
          "STL": "3",
          "TOV": "3",
          "TREB": "10"
        },
        "game": {
          "AST": "25",
          "BLK": "4",
          "DREB": "42",
          "FG3A": "41",
          "FG3M": "14",
          "FG3_PCT": "34",
          "FGA": "82",
          "FGM": "38",
          "FG_PCT": "46",
          "FTA": "30",
          "FTM": "25",
          "FT_PCT": "83",
          "MIN": "4",
          "OREB": "4",
          "PF": "21",
          "PTS": "115",
          "STL": "13",
          "TOV": "15",
          "TREB": "46"
        }
      },
      "losses": "7",
      "name": "Bucks",
      "next_game": {
        "city": "Milwaukee",
        "day": "7",
        "dayname": "Friday",
        "is_home": "True",
        "month": "December",
        "opponent_name": "Warriors",
        "opponent_place": "Golden State",
        "stadium": "Fiserv Forum",
        "year": "2018"
      },
      "next_game_id": "4976",
      "place": "Milwaukee",
      "previous_game_id": "5422",
      "wins": "16"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "-17",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "10",
          "FGM": "4",
          "FG_PCT": "40",
          "FTA": "4",
          "FTM": "2",
          "FT_PCT": "50",
          "MIN": "30",
          "OREB": "2",
          "PF": "5",
          "PTS": "10",
          "STL": "1",
          "TOV": "3",
          "TREB": "8",
          "first_name": "Andre",
          "last_name": "Drummond",
          "name": "Andre Drummond",
          "starter": "True"
        },
        {
          "+/-": "-17",
          "AST": "4",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "7",
          "FG3A": "11",
          "FG3M": "4",
          "FG3_PCT": "36",
          "FGA": "22",
          "FGM": "11",
          "FG_PCT": "50",
          "FTA": "6",
          "FTM": "5",
          "FT_PCT": "83",
          "MIN": "30",
          "OREB": "0",
          "PF": "2",
          "PTS": "31",
          "STL": "0",
          "TOV": "7",
          "TREB": "7",
          "first_name": "Blake",
          "last_name": "Griffin",
          "name": "Blake Griffin",
          "starter": "True"
        },
        {
          "+/-": "-20",
          "AST": "5",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "15",
          "FGM": "6",
          "FG_PCT": "40",
          "FTA": "3",
          "FTM": "2",
          "FT_PCT": "67",
          "MIN": "24",
          "OREB": "1",
          "PF": "4",
          "PTS": "15",
          "STL": "1",
          "TOV": "1",
          "TREB": "7",
          "first_name": "Reggie",
          "last_name": "Jackson",
          "name": "Reggie Jackson",
          "starter": "True"
        },
        {
          "+/-": "-25",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "5",
          "FGM": "2",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "22",
          "OREB": "1",
          "PF": "1",
          "PTS": "5",
          "STL": "0",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Langston",
          "last_name": "Galloway",
          "name": "Langston Galloway",
          "starter": "True"
        },
        {
          "+/-": "-14",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "1",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "8",
          "OREB": "0",
          "PF": "2",
          "PTS": "2",
          "STL": "1",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Glenn",
          "last_name": "Robinson",
          "name": "Glenn Robinson",
          "starter": "True"
        },
        {
          "+/-": "-13",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "8",
          "FG3M": "1",
          "FG3_PCT": "12",
          "FGA": "16",
          "FGM": "3",
          "FG_PCT": "19",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "26",
          "OREB": "3",
          "PF": "1",
          "PTS": "7",
          "STL": "2",
          "TOV": "4",
          "TREB": "9",
          "first_name": "Stanley",
          "last_name": "Johnson",
          "name": "Stanley Johnson",
          "starter": "False"
        },
        {
          "+/-": "-1",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "2",
          "FGM": "1",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "26",
          "OREB": "2",
          "PF": "5",
          "PTS": "3",
          "STL": "0",
          "TOV": "2",
          "TREB": "5",
          "first_name": "Bruce",
          "last_name": "Brown",
          "name": "Bruce Brown",
          "starter": "False"
        },
        {
          "+/-": "-6",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "3",
          "FGM": "2",
          "FG_PCT": "67",
          "FTA": "6",
          "FTM": "4",
          "FT_PCT": "67",
          "MIN": "17",
          "OREB": "2",
          "PF": "1",
          "PTS": "8",
          "STL": "0",
          "TOV": "0",
          "TREB": "5",
          "first_name": "Zaza",
          "last_name": "Pachulia",
          "name": "Zaza Pachulia",
          "starter": "False"
        },
        {
          "+/-": "-5",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "3",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "14",
          "OREB": "0",
          "PF": "2",
          "PTS": "0",
          "STL": "0",
          "TOV": "2",
          "TREB": "1",
          "first_name": "Ish",
          "last_name": "Smith",
          "name": "Ish Smith",
          "starter": "False"
        },
        {
          "+/-": "3",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "13",
          "OREB": "0",
          "PF": "2",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "José",
          "last_name": "Calderón",
          "name": "José Calderón",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "3",
          "FGM": "1",
          "FG_PCT": "33",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "10",
          "OREB": "0",
          "PF": "0",
          "PTS": "3",
          "STL": "0",
          "TOV": "1",
          "TREB": "3",
          "first_name": "Khyri",
          "last_name": "Thomas",
          "name": "Khyri Thomas",
          "starter": "False"
        },
        {
          "+/-": "3",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
          "FGM": "3",
          "FG_PCT": "75",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "7",
          "OREB": "1",
          "PF": "1",
          "PTS": "6",
          "STL": "0",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Jon",
          "last_name": "Leuer",
          "name": "Jon Leuer",
          "starter": "False"
        },
        {
          "+/-": "-3",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "6",
          "FGM": "1",
          "FG_PCT": "17",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "6",
          "OREB": "0",
          "PF": "0",
          "PTS": "2",
          "STL": "1",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Luke",
          "last_name": "Kennard",
          "name": "Luke Kennard",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 4,
      "division": "Central",
      "game_number": "22",
      "line_score": {
        "H1": {
          "AST": "25",
          "BLK": "00",
          "DREB": "139",
          "FG3A": "99",
          "FG3M": "22",
          "FG3_PCT": "22",
          "FGA": "2425",
          "FGM": "911",
          "FG_PCT": "38",
          "FTA": "20",
          "FTM": "10",
          "FT_PCT": "50",
          "MIN": "6060",
          "OREB": "14",
          "PTS": "2124",
          "STL": "13",
          "TOV": "47",
          "TREB": "153"
        },
        "H2": {
          "AST": "48",
          "BLK": "10",
          "DREB": "710",
          "FG3A": "137",
          "FG3M": "32",
          "FG3_PCT": "23",
          "FGA": "2719",
          "FGM": "510",
          "FG_PCT": "19",
          "FTA": "710",
          "FTM": "66",
          "FT_PCT": "9",
          "MIN": "6060",
          "OREB": "61",
          "PTS": "1928",
          "STL": "11",
          "TOV": "45",
          "TREB": "771"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "2",
          "BLK": "0",
          "DREB": "13",
          "FG3A": "9",
          "FG3M": "2",
          "FG3_PCT": "22",
          "FGA": "24",
          "FGM": "9",
          "FG_PCT": "38",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "60",
          "OREB": "1",
          "PTS": "21",
          "STL": "1",
          "TOV": "4",
          "TREB": "14"
        },
        "Q2": {
          "AST": "5",
          "BLK": "0",
          "DREB": "9",
          "FG3A": "9",
          "FG3M": "2",
          "FG3_PCT": "22",
          "FGA": "25",
          "FGM": "11",
          "FG_PCT": "44",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "60",
          "OREB": "4",
          "PTS": "24",
          "STL": "3",
          "TOV": "7",
          "TREB": "13"
        },
        "Q3": {
          "AST": "4",
          "BLK": "1",
          "DREB": "7",
          "FG3A": "13",
          "FG3M": "3",
          "FG3_PCT": "23",
          "FGA": "27",
          "FGM": "5",
          "FG_PCT": "19",
          "FTA": "7",
          "FTM": "6",
          "FT_PCT": "86",
          "MIN": "60",
          "OREB": "6",
          "PTS": "19",
          "STL": "1",
          "TOV": "4",
          "TREB": "13"
        },
        "Q4": {
          "AST": "8",
          "BLK": "0",
          "DREB": "10",
          "FG3A": "7",
          "FG3M": "2",
          "FG3_PCT": "29",
          "FGA": "19",
          "FGM": "10",
          "FG_PCT": "53",
          "FTA": "10",
          "FTM": "6",
          "FT_PCT": "60",
          "MIN": "60",
          "OREB": "1",
          "PTS": "28",
          "STL": "1",
          "TOV": "5",
          "TREB": "11"
        },
        "game": {
          "AST": "19",
          "BLK": "1",
          "DREB": "39",
          "FG3A": "38",
          "FG3M": "9",
          "FG3_PCT": "24",
          "FGA": "95",
          "FGM": "35",
          "FG_PCT": "37",
          "FTA": "19",
          "FTM": "13",
          "FT_PCT": "68",
          "MIN": "4",
          "OREB": "12",
          "PF": "26",
          "PTS": "92",
          "STL": "6",
          "TOV": "20",
          "TREB": "51"
        }
      },
      "losses": "9",
      "name": "Pistons",
      "next_game": {
        "city": "Detroit",
        "day": "7",
        "dayname": "Friday",
        "is_home": "True",
        "month": "December",
        "opponent_name": "76ers",
        "opponent_place": "Philadelphia",
        "stadium": "Little Caesars Arena",
        "year": "2018"
      },
      "next_game_id": "5754",
      "place": "Detroit",
      "previous_game_id": "5753",
      "wins": "13"
    }
  }
}
```

The parsed source text and structured source payload are identical for this case.

## Prepared-example metadata

```json
{
  "sportsett_id": "4975",
  "normalizer": "sportsett",
  "requested_split": "test",
  "hub_id": "GEM/sportsett_basketball",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The Milwaukee Bucks defeated the Detroit Pistons, 115 - 92, at Fiserv Forum on Wednesday evening. The Bucks (16 - 7) came in well - rested, last having taken the court Saturday. That energy was evident in the first half, as Milwaukee had forged a 56 - 45 lead over the Pistons (13 - 9) by intermission. The home squad would keep the pressure on in the second half, compiling another 59 points while limiting Detroit to 47. The Bucks put on a stellar offensive show, holding the visitors to 36 percent shooting and forcing 20 turnovers. Blake Griffin's 31 points, which he supplemented with seven rebounds, four assists and one block, led the Pistons. Reggie Jackson provided 15 points, seven rebounds, five assists and one steal. Andre Drummond continued a string of quiet games with 10 points, eight boards, one assist and one steal. No other Detroit player hit double digits in the scoring column, with Zaza Pachuilia coming the closest with eight points off the bench. Eric Bledsoe paced the Bucks with 27 points, adding four assists, three rebounds and four steals. Giannis Antetokounmpo managed 15 points, eight rebounds, five assists, one steal and one block. Malcolm Brogdon poured in 14 points and also supplied six rebounds and two assists. Tony Snell drew a start for Khris Middleton (personal) and netted 11 points, seven rebounds, one assist and two steals. Thon Maker and Sterling Brown delivered matching 11 - point tallies off the bench. The Pistons head back home and tangle with the Philadelphia 76ers on Friday night, while the Bucks remain home for a Friday night showdown against the Golden State Warriors.
```

### Reference 2

```text
The Milwaukee Bucks defeated the Detroit Pistons , 115 - 92 , at Fiserv Forum on Wednesday evening . The Bucks ( 16 - 7 ) came in well - rested , last having taken the court Saturday . That energy was evident in the first half , as Milwaukee had forged a 56 - 45 lead over the Pistons ( 13 - 9 ) by intermission . The home squad would keep the pressure on in the second half , compiling another 59 points while limiting Detroit to 47 . The Bucks put on a stellar offensive show , holding the visitors to 36 percent shooting and forcing 20 turnovers . Blake Griffin 's 31 points , which he supplemented with seven rebounds , four assists and one block , led the Pistons . Reggie Jackson provided 15 points , seven rebounds , five assists and one steal . Andre Drummond continued a string of quiet games with 10 points , eight boards , one assist and one steal . No other Detroit player hit double digits in the scoring column , with Zaza Pachuilia coming the closest with eight points off the bench . Eric Bledsoe paced the Bucks with 27 points , adding four assists , three rebounds and four steals . Giannis Antetokounmpo managed 15 points , eight rebounds , five assists , one steal and one block . Malcolm Brogdon poured in 14 points and also supplied six rebounds and two assists . Tony Snell drew a start for Khris Middleton ( personal ) and netted 11 points , seven rebounds , one assist and two steals . Thon Maker and Sterling Brown delivered matching 11 - point tallies off the bench . The Pistons head back home and tangle with the Philadelphia 76ers on Friday night , while the Bucks remain home for a Friday night showdown against the Golden State Warriors .
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4975__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 889.345 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 441 |
| Writer mode | deterministic_fallback |
| Release status | approved_with_warnings |
| Primary evaluation eligible | False |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 15 |
| Support sentences | 15 |
| Generation error | — |

#### Exact generated text

```text
Bucks recorded 115 for Team points (line-score family), while Pistons recorded 92 for Team points (line-score family); the difference is 23.
The recorded event at Fiserv Forum on Wednesday, December 5, 2018 (2018 season) shows the Milwaukee Bucks with 115 team points (line-score family) and the Detroit Pistons with 92 team points (line-score family).
Participant context records Milwaukee Bucks entered with 16 wins and 7 losses; Detroit Pistons entered with 13 wins and 9 losses.
The supplied score progression records after Q1, Milwaukee Bucks led 30-21; after Q2, Milwaukee Bucks led 56-45; after Q3, Milwaukee Bucks led 84-64; after Q4, Milwaukee Bucks led 115-92.
In the ranking for Player points, Blake Griffin (Pistons) ranked first with 31, Eric Bledsoe (Bucks) ranked second with 27, and Giannis Antetokounmpo (Bucks) and Reggie Jackson (Pistons) tied for third with 15.
In the ranking for Player total rebounds, Stanley Johnson (Pistons) ranked first with 9; Brook Lopez (Bucks) and Andre Drummond (Pistons) tied for second with 8; Giannis Antetokounmpo, Tony Snell (Bucks), Blake Griffin and Reggie Jackson (Pistons) tied for fourth with 7.
In the ranking for Player field goals made, Blake Griffin (Pistons) ranked first with 11, Eric Bledsoe (Bucks) ranked second with 10, and Giannis Antetokounmpo (Bucks) and Reggie Jackson (Pistons) tied for third with 6.
In the ranking for Player assists, Matthew Dellavedova (Bucks) ranked first with 6; Giannis Antetokounmpo (Bucks) and Reggie Jackson (Pistons) tied for second with 5; Eric Bledsoe (Bucks) and Blake Griffin (Pistons) tied for fourth with 4.
In the ranking for Player offensive rebounds, Stanley Johnson (Pistons) led with 3, followed by Andre Drummond (Pistons) (2), Bruce Brown (Pistons) (2), Zaza Pachulia (Pistons) (2).
In the ranking for Player defensive rebounds, Brook Lopez (Bucks) ranked first with 8, Blake Griffin (Pistons) ranked second with 7, and Giannis Antetokounmpo, Tony Snell, Malcolm Brogdon (Bucks), Andre Drummond, Reggie Jackson and Stanley Johnson (Pistons) tied for third with 6.
In the ranking for Player steals, Eric Bledsoe (Bucks) led with 3, followed by Tony Snell (Bucks) (2), Donte DiVincenzo (Bucks) (2), Stanley Johnson (Pistons) (2).
In the ranking for Player blocks, Brook Lopez (Bucks) led with 3, followed by Giannis Antetokounmpo (Bucks) (1), Blake Griffin (Pistons) (1).
Bucks recorded 38 for Team field goals made (line-score family), while Pistons recorded 35 for Team field goals made (line-score family); the difference is 3.
Bucks recorded 14 for Team three-pointers made (line-score family), while Pistons recorded 9 for Team three-pointers made (line-score family); the difference is 5.
Bucks recorded 25 for Team free throws made (line-score family), while Pistons recorded 13 for Team free throws made (line-score family); the difference is 12.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4975__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 13.409 |
| Prompt tokens | 8714 |
| Completion tokens | 1165 |
| Total tokens | 9879 |
| Output words | 135 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The strongest supported findings from the data are:

- The Milwaukee Bucks defeated the Detroit Pistons 115–92 on December 5, 2018, at Fiserv Forum in Milwaukee.
- The Bucks won every quarter: Q1 30–21, Q2 26–24, Q3 28–19, Q4 31–28.
- Milwaukee shot more efficiently than Detroit: 46% to 37% from the field, 34% to 24% from three-point range, and 83% to 68% from the free-throw line.
- The Bucks also had more assists (25–19), steals (13–6), and blocks (4–1), and fewer turnovers (15–20).
- Blake Griffin scored a game-high 31 points for the Pistons, but Detroit lost.
- Eric Bledsoe led the Bucks with 27 points.
- The Pistons outrebounded the Bucks 51–46, including 12–4 on offensive rebounds, but still lost.
- Attendance was 16,500 in a 17,500-capacity arena.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4975__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 16.104 |
| Prompt tokens | 8751 |
| Completion tokens | 1524 |
| Total tokens | 10275 |
| Output words | 298 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The Milwaukee Bucks defeated the Detroit Pistons 115-92 on Wednesday, December 5, 2018, at Fiserv Forum in Milwaukee. The Bucks played in front of 16,500 fans and improved to 16-7, while the Pistons dropped to 13-9. Milwaukee built an early lead, winning the first quarter 30-21 and holding a 56-45 advantage at halftime. The Bucks extended their lead in the third quarter, outscoring Detroit 28-19, before closing out the game with a 31-28 fourth quarter.

Milwaukee’s shooting and defensive pressure were key contrasts to Detroit’s performance. The Bucks shot 46 percent from the field and 34 percent from three-point range, while the Pistons shot 37 percent overall and 24 percent from beyond the arc. The Bucks also made 25 of 30 free throws, compared with 13 of 19 for Detroit. Milwaukee finished with 25 assists, 13 steals, and 4 blocks, while forcing 20 Pistons turnovers. Detroit actually outrebounded Milwaukee 51-46, including a 12-4 edge in offensive rebounds, but could not overcome its shooting struggles and turnovers.

Eric Bledsoe led the Bucks with 27 points on 10-of-17 shooting, adding 5 rebounds, 4 assists, and 3 steals. Malcolm Brogdon added 14 points, Tony Snell scored 11, and both Thon Maker and Sterling Brown contributed 11 points off the bench. Giannis Antetokounmpo finished with 15 points, 7 rebounds, and 5 assists but committed 5 turnovers. Brook Lopez chipped in 6 points and 3 blocks.

Blake Griffin was the high scorer for Detroit with 31 points on 11-of-22 shooting, but he also committed 7 turnovers. Reggie Jackson added 15 points, and Andre Drummond posted 10 points and 8 rebounds. The Pistons’ offense never found consistent rhythm, as only Griffin and Jackson scored in double figures, and Detroit’s miscues proved costly against a Bucks team that converted those turnovers into scoring chances.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.02468538 | 0.333515975 | 1.336700337 | 0.165061898 | 0.21465052 | 0.795203507 | 0.111774713 | 0.063436197 | 0.011439787 | 0.933333333 |
| Raw-generic direct Flash | 0.049271101 | 0.230025063 | 0.831649832 | 0.200488998 | 0.153344208 | 0.824968219 | 0.164463058 | 0.056197982 | 0.056197982 | 1 |
| Task-aware direct Flash | 0.134627177 | 0.475722676 | 0.858585859 | 0.256410256 | 0.313838598 | 0.872730196 | 0.108926907 | 0.034323019 | 0.006212678 | 1 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “Participant context records Milwaukee Bucks entered with 16 wins and 7 losses; Detroit Pistons entered with 13 wins and 9 losses.”
     - Those records each total the listed game number and therefore include this result. Milwaukee improved to 16-7 and Detroit fell to 13-9; they did not enter with those records.
  2. **TASK/FORMAT** — “The entire generated output is a sequence of evidence-ledger statements and rankings rather than a coherent multi-paragraph game report.”
     - The request required a coherent game report that leads with the result and selects the most important performances and contrasts. The output is a mechanical inventory with repeated result statements and no paragraph-level narrative organization.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **TASK/FORMAT** — “The strongest supported findings from the data are: - The Milwaukee Bucks defeated ... - Attendance was 16,500 in a 17,500-capacity arena.”
     - The requested output mode was a multi-paragraph report, but the response is presented as a single inline list rather than multiple paragraphs.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **4**
- Errors:
  1. **CONTEXT** — “while forcing 20 Pistons turnovers.”
     - The source records 20 Detroit turnovers and 13 Milwaukee steals, but does not state that Milwaukee forced every turnover.
  2. **CONTEXT** — “but could not overcome its shooting struggles and turnovers.”
     - The box score supports the shooting and turnover figures, but it does not establish them as the causal explanation for Detroit's defeat.
  3. **NUMBER** — “as only Griffin and Jackson scored in double figures”
     - Andre Drummond also scored in double figures with exactly 10 points, so Griffin and Jackson were not the only Detroit players to do so.
  4. **CONTEXT** — “Detroit’s miscues proved costly against a Bucks team that converted those turnovers into scoring chances.”
     - The source contains turnover totals but no points-off-turnovers or possession-level evidence showing that Milwaukee converted those turnovers into scoring chances or that they proved causal.

---

# Case 14: `sportsett_basketball` / `4982`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | sportsett_basketball |
| Example ID | 4982 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source characters | 24850 |
| Reference count | 2 |
| Source SHA-256 | b19ea3f03d213afa0775423a02eac33a2d53f2dd62dfdfd22baf8e192dcd5f9b |
| Reference SHA-256 | 5148551d43ec4d524fe9aa435f3a091caf02a038d027a57e6ad20b63dfddd0cd |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```json
{
  "game": {
    "attendance": "17600",
    "capacity": "17500",
    "city": "Milwaukee",
    "day": "4",
    "dayname": "Friday",
    "game_id": "4982",
    "month": "January",
    "season": "2018",
    "stadium": "Fiserv Forum",
    "state": "Wisconsin",
    "year": "2019"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "29",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "4",
          "FG3M": "4",
          "FG3_PCT": "100",
          "FGA": "8",
          "FGM": "7",
          "FG_PCT": "88",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "22",
          "OREB": "0",
          "PF": "1",
          "PTS": "19",
          "STL": "3",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Khris",
          "last_name": "Middleton",
          "name": "Khris Middleton",
          "starter": "True"
        },
        {
          "+/-": "26",
          "AST": "2",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "13",
          "FGM": "7",
          "FG_PCT": "54",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "22",
          "OREB": "2",
          "PF": "4",
          "PTS": "14",
          "STL": "1",
          "TOV": "2",
          "TREB": "8",
          "first_name": "Eric",
          "last_name": "Bledsoe",
          "name": "Eric Bledsoe",
          "starter": "True"
        },
        {
          "+/-": "17",
          "AST": "0",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "9",
          "FGM": "3",
          "FG_PCT": "33",
          "FTA": "4",
          "FTM": "2",
          "FT_PCT": "50",
          "MIN": "21",
          "OREB": "0",
          "PF": "2",
          "PTS": "10",
          "STL": "1",
          "TOV": "1",
          "TREB": "2",
          "first_name": "Brook",
          "last_name": "Lopez",
          "name": "Brook Lopez",
          "starter": "True"
        },
        {
          "+/-": "10",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "9",
          "FGM": "6",
          "FG_PCT": "67",
          "FTA": "7",
          "FTM": "7",
          "FT_PCT": "100",
          "MIN": "19",
          "OREB": "1",
          "PF": "1",
          "PTS": "19",
          "STL": "0",
          "TOV": "1",
          "TREB": "3",
          "first_name": "Malcolm",
          "last_name": "Brogdon",
          "name": "Malcolm Brogdon",
          "starter": "True"
        },
        {
          "+/-": "21",
          "AST": "10",
          "BLK": "2",
          "DOUBLE": "double",
          "DREB": "7",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "6",
          "FG_PCT": "75",
          "FTA": "6",
          "FTM": "4",
          "FT_PCT": "67",
          "MIN": "19",
          "OREB": "1",
          "PF": "2",
          "PTS": "16",
          "STL": "1",
          "TOV": "0",
          "TREB": "8",
          "first_name": "Giannis",
          "last_name": "Antetokounmpo",
          "name": "Giannis Antetokounmpo",
          "starter": "True"
        },
        {
          "+/-": "15",
          "AST": "7",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "11",
          "FGM": "4",
          "FG_PCT": "36",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "25",
          "OREB": "0",
          "PF": "4",
          "PTS": "9",
          "STL": "0",
          "TOV": "1",
          "TREB": "5",
          "first_name": "Pat",
          "last_name": "Connaughton",
          "name": "Pat Connaughton",
          "starter": "False"
        },
        {
          "+/-": "11",
          "AST": "3",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "9",
          "FGM": "4",
          "FG_PCT": "44",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "22",
          "OREB": "2",
          "PF": "1",
          "PTS": "11",
          "STL": "1",
          "TOV": "2",
          "TREB": "4",
          "first_name": "Tony",
          "last_name": "Snell",
          "name": "Tony Snell",
          "starter": "False"
        },
        {
          "+/-": "17",
          "AST": "5",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "1",
          "FG3M": "1",
          "FG3_PCT": "100",
          "FGA": "4",
          "FGM": "3",
          "FG_PCT": "75",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "21",
          "OREB": "0",
          "PF": "1",
          "PTS": "8",
          "STL": "1",
          "TOV": "0",
          "TREB": "4",
          "first_name": "D.J.",
          "last_name": "Wilson",
          "name": "D.J. Wilson",
          "starter": "False"
        },
        {
          "+/-": "10",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "8",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "5",
          "FG_PCT": "62",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "19",
          "OREB": "3",
          "PF": "5",
          "PTS": "10",
          "STL": "1",
          "TOV": "4",
          "TREB": "11",
          "first_name": "Ersan",
          "last_name": "İlyasova",
          "name": "Ersan İlyasova",
          "starter": "False"
        },
        {
          "+/-": "20",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "7",
          "FGM": "4",
          "FG_PCT": "57",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "16",
          "OREB": "2",
          "PF": "0",
          "PTS": "12",
          "STL": "1",
          "TOV": "0",
          "TREB": "3",
          "first_name": "George",
          "last_name": "Hill",
          "name": "George Hill",
          "starter": "False"
        },
        {
          "+/-": "-8",
          "AST": "0",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "6",
          "FG3M": "1",
          "FG3_PCT": "17",
          "FGA": "10",
          "FGM": "3",
          "FG_PCT": "30",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "14",
          "OREB": "1",
          "PF": "4",
          "PTS": "8",
          "STL": "0",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Thon",
          "last_name": "Maker",
          "name": "Thon Maker",
          "starter": "False"
        },
        {
          "+/-": "-8",
          "AST": "0",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "4",
          "FGM": "3",
          "FG_PCT": "75",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "14",
          "OREB": "0",
          "PF": "1",
          "PTS": "8",
          "STL": "1",
          "TOV": "2",
          "TREB": "2",
          "first_name": "Jason",
          "last_name": "Smith",
          "name": "Jason Smith",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Sterling",
          "last_name": "Brown",
          "name": "Sterling Brown",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 1,
      "division": "Central",
      "game_number": "37",
      "line_score": {
        "H1": {
          "AST": "113",
          "BLK": "14",
          "DREB": "149",
          "FG3A": "148",
          "FG3M": "51",
          "FG3_PCT": "34",
          "FGA": "3026",
          "FGM": "1812",
          "FG_PCT": "60",
          "FTA": "211",
          "FTM": "28",
          "FT_PCT": "13",
          "MIN": "6060",
          "OREB": "24",
          "PTS": "4333",
          "STL": "35",
          "TOV": "21",
          "TREB": "173"
        },
        "H2": {
          "AST": "139",
          "BLK": "12",
          "DREB": "811",
          "FG3A": "711",
          "FG3M": "53",
          "FG3_PCT": "7",
          "FGA": "2024",
          "FGM": "1510",
          "FG_PCT": "75",
          "FTA": "105",
          "FTM": "73",
          "FT_PCT": "70",
          "MIN": "6060",
          "OREB": "24",
          "PTS": "4226",
          "STL": "21",
          "TOV": "56",
          "TREB": "835"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "11",
          "BLK": "1",
          "DREB": "14",
          "FG3A": "14",
          "FG3M": "5",
          "FG3_PCT": "36",
          "FGA": "30",
          "FGM": "18",
          "FG_PCT": "60",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "2",
          "PTS": "43",
          "STL": "3",
          "TOV": "2",
          "TREB": "16"
        },
        "Q2": {
          "AST": "3",
          "BLK": "4",
          "DREB": "9",
          "FG3A": "8",
          "FG3M": "1",
          "FG3_PCT": "12",
          "FGA": "26",
          "FGM": "12",
          "FG_PCT": "46",
          "FTA": "11",
          "FTM": "8",
          "FT_PCT": "73",
          "MIN": "60",
          "OREB": "4",
          "PTS": "33",
          "STL": "5",
          "TOV": "1",
          "TREB": "13"
        },
        "Q3": {
          "AST": "13",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "7",
          "FG3M": "5",
          "FG3_PCT": "71",
          "FGA": "20",
          "FGM": "15",
          "FG_PCT": "75",
          "FTA": "10",
          "FTM": "7",
          "FT_PCT": "70",
          "MIN": "60",
          "OREB": "2",
          "PTS": "42",
          "STL": "2",
          "TOV": "5",
          "TREB": "10"
        },
        "Q4": {
          "AST": "9",
          "BLK": "2",
          "DREB": "11",
          "FG3A": "11",
          "FG3M": "3",
          "FG3_PCT": "27",
          "FGA": "24",
          "FGM": "10",
          "FG_PCT": "42",
          "FTA": "5",
          "FTM": "3",
          "FT_PCT": "60",
          "MIN": "60",
          "OREB": "4",
          "PTS": "26",
          "STL": "1",
          "TOV": "6",
          "TREB": "15"
        },
        "game": {
          "AST": "36",
          "BLK": "8",
          "DREB": "42",
          "FG3A": "40",
          "FG3M": "14",
          "FG3_PCT": "35",
          "FGA": "100",
          "FGM": "55",
          "FG_PCT": "55",
          "FTA": "28",
          "FTM": "20",
          "FT_PCT": "71",
          "MIN": "4",
          "OREB": "12",
          "PF": "26",
          "PTS": "144",
          "STL": "11",
          "TOV": "14",
          "TREB": "54"
        }
      },
      "losses": "10",
      "name": "Bucks",
      "next_game": {
        "city": "Milwaukee",
        "day": "5",
        "dayname": "Saturday",
        "is_home": "True",
        "month": "January",
        "opponent_name": "Raptors",
        "opponent_place": "Toronto",
        "stadium": "Fiserv Forum",
        "year": "2019"
      },
      "next_game_id": "4983",
      "place": "Milwaukee",
      "previous_game_id": "4981",
      "wins": "27"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "-21",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "10",
          "FGM": "4",
          "FG_PCT": "40",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "33",
          "OREB": "0",
          "PF": "1",
          "PTS": "10",
          "STL": "1",
          "TOV": "3",
          "TREB": "2",
          "first_name": "Kevin",
          "last_name": "Huerter",
          "name": "Kevin Huerter",
          "starter": "True"
        },
        {
          "+/-": "-18",
          "AST": "10",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "9",
          "FGM": "3",
          "FG_PCT": "33",
          "FTA": "5",
          "FTM": "5",
          "FT_PCT": "100",
          "MIN": "31",
          "OREB": "0",
          "PF": "2",
          "PTS": "13",
          "STL": "3",
          "TOV": "2",
          "TREB": "2",
          "first_name": "Trae",
          "last_name": "Young",
          "name": "Trae Young",
          "starter": "True"
        },
        {
          "+/-": "-13",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "9",
          "FGM": "4",
          "FG_PCT": "44",
          "FTA": "6",
          "FTM": "4",
          "FT_PCT": "67",
          "MIN": "25",
          "OREB": "2",
          "PF": "4",
          "PTS": "12",
          "STL": "2",
          "TOV": "1",
          "TREB": "7",
          "first_name": "John",
          "last_name": "Collins",
          "name": "John Collins",
          "starter": "True"
        },
        {
          "+/-": "1",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "1",
          "FGM": "1",
          "FG_PCT": "100",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "22",
          "OREB": "1",
          "PF": "1",
          "PTS": "2",
          "STL": "0",
          "TOV": "3",
          "TREB": "4",
          "first_name": "Daniel",
          "last_name": "Hamilton",
          "name": "Daniel Hamilton",
          "starter": "True"
        },
        {
          "+/-": "-21",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "9",
          "FG3M": "4",
          "FG3_PCT": "44",
          "FGA": "11",
          "FGM": "5",
          "FG_PCT": "45",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "21",
          "OREB": "0",
          "PF": "5",
          "PTS": "14",
          "STL": "1",
          "TOV": "5",
          "TREB": "1",
          "first_name": "Dewayne",
          "last_name": "Dedmon",
          "name": "Dewayne Dedmon",
          "starter": "True"
        },
        {
          "+/-": "-16",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "12",
          "FGM": "7",
          "FG_PCT": "58",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "22",
          "OREB": "0",
          "PF": "2",
          "PTS": "19",
          "STL": "1",
          "TOV": "1",
          "TREB": "2",
          "first_name": "DeAndre'",
          "last_name": "Bembry",
          "name": "DeAndre' Bembry",
          "starter": "False"
        },
        {
          "+/-": "-18",
          "AST": "3",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "8",
          "FGM": "4",
          "FG_PCT": "50",
          "FTA": "9",
          "FTM": "3",
          "FT_PCT": "33",
          "MIN": "21",
          "OREB": "2",
          "PF": "1",
          "PTS": "12",
          "STL": "1",
          "TOV": "3",
          "TREB": "8",
          "first_name": "Alex",
          "last_name": "Len",
          "name": "Alex Len",
          "starter": "False"
        },
        {
          "+/-": "-8",
          "AST": "6",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "7",
          "FGM": "3",
          "FG_PCT": "43",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "20",
          "OREB": "0",
          "PF": "3",
          "PTS": "12",
          "STL": "0",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Jeremy",
          "last_name": "Lin",
          "name": "Jeremy Lin",
          "starter": "False"
        },
        {
          "+/-": "-23",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "8",
          "FGM": "1",
          "FG_PCT": "12",
          "FTA": "2",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "16",
          "OREB": "0",
          "PF": "2",
          "PTS": "3",
          "STL": "0",
          "TOV": "1",
          "TREB": "2",
          "first_name": "Justin",
          "last_name": "Anderson",
          "name": "Justin Anderson",
          "starter": "False"
        },
        {
          "+/-": "-6",
          "AST": "0",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "7",
          "FGM": "3",
          "FG_PCT": "43",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "16",
          "OREB": "0",
          "PF": "2",
          "PTS": "9",
          "STL": "2",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Tyler",
          "last_name": "Dorsey",
          "name": "Tyler Dorsey",
          "starter": "False"
        },
        {
          "+/-": "-17",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "3",
          "FGM": "2",
          "FG_PCT": "67",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "8",
          "OREB": "0",
          "PF": "0",
          "PTS": "6",
          "STL": "0",
          "TOV": "1",
          "TREB": "0",
          "first_name": "Vince",
          "last_name": "Carter",
          "name": "Vince Carter",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Miles",
          "last_name": "Plumlee",
          "name": "Miles Plumlee",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 12,
      "division": "Southeast",
      "game_number": "38",
      "line_score": {
        "H1": {
          "AST": "36",
          "BLK": "11",
          "DREB": "78",
          "FG3A": "97",
          "FG3M": "13",
          "FG3_PCT": "13",
          "FGA": "2219",
          "FGM": "69",
          "FG_PCT": "3",
          "FTA": "311",
          "FTM": "18",
          "FT_PCT": "6",
          "MIN": "6060",
          "OREB": "21",
          "PTS": "1429",
          "STL": "21",
          "TOV": "85",
          "TREB": "99"
        },
        "H2": {
          "AST": "98",
          "BLK": "10",
          "DREB": "38",
          "FG3A": "1213",
          "FG3M": "73",
          "FG3_PCT": "6",
          "FGA": "2123",
          "FGM": "1210",
          "FG_PCT": "57",
          "FTA": "912",
          "FTM": "510",
          "FT_PCT": "56",
          "MIN": "6060",
          "OREB": "20",
          "PTS": "3633",
          "STL": "44",
          "TOV": "62",
          "TREB": "58"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "3",
          "BLK": "1",
          "DREB": "7",
          "FG3A": "9",
          "FG3M": "1",
          "FG3_PCT": "11",
          "FGA": "22",
          "FGM": "6",
          "FG_PCT": "27",
          "FTA": "3",
          "FTM": "1",
          "FT_PCT": "33",
          "MIN": "60",
          "OREB": "2",
          "PTS": "14",
          "STL": "2",
          "TOV": "8",
          "TREB": "9"
        },
        "Q2": {
          "AST": "6",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "7",
          "FG3M": "3",
          "FG3_PCT": "43",
          "FGA": "19",
          "FGM": "9",
          "FG_PCT": "47",
          "FTA": "11",
          "FTM": "8",
          "FT_PCT": "73",
          "MIN": "60",
          "OREB": "1",
          "PTS": "29",
          "STL": "1",
          "TOV": "5",
          "TREB": "9"
        },
        "Q3": {
          "AST": "9",
          "BLK": "1",
          "DREB": "3",
          "FG3A": "12",
          "FG3M": "7",
          "FG3_PCT": "58",
          "FGA": "21",
          "FGM": "12",
          "FG_PCT": "57",
          "FTA": "9",
          "FTM": "5",
          "FT_PCT": "56",
          "MIN": "60",
          "OREB": "2",
          "PTS": "36",
          "STL": "4",
          "TOV": "6",
          "TREB": "5"
        },
        "Q4": {
          "AST": "8",
          "BLK": "0",
          "DREB": "8",
          "FG3A": "13",
          "FG3M": "3",
          "FG3_PCT": "23",
          "FGA": "23",
          "FGM": "10",
          "FG_PCT": "43",
          "FTA": "12",
          "FTM": "10",
          "FT_PCT": "83",
          "MIN": "60",
          "OREB": "0",
          "PTS": "33",
          "STL": "4",
          "TOV": "2",
          "TREB": "8"
        },
        "game": {
          "AST": "26",
          "BLK": "3",
          "DREB": "26",
          "FG3A": "41",
          "FG3M": "14",
          "FG3_PCT": "34",
          "FGA": "85",
          "FGM": "37",
          "FG_PCT": "44",
          "FTA": "35",
          "FTM": "24",
          "FT_PCT": "69",
          "MIN": "4",
          "OREB": "5",
          "PF": "23",
          "PTS": "112",
          "STL": "11",
          "TOV": "21",
          "TREB": "31"
        }
      },
      "losses": "27",
      "name": "Hawks",
      "next_game": {
        "city": "Atlanta",
        "day": "6",
        "dayname": "Sunday",
        "is_home": "True",
        "month": "January",
        "opponent_name": "Heat",
        "opponent_place": "Miami",
        "stadium": "State Farm Arena",
        "year": "2019"
      },
      "next_game_id": "5224",
      "place": "Atlanta",
      "previous_game_id": "6127",
      "wins": "11"
    }
  }
}
```

The parsed source text and structured source payload are identical for this case.

## Prepared-example metadata

```json
{
  "sportsett_id": "4982",
  "normalizer": "sportsett",
  "requested_split": "test",
  "hub_id": "GEM/sportsett_basketball",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The Milwaukee Bucks defeated the visiting Atlanta Hawks, 144 - 112, at Fiserv Forum on Friday. Milwaukee came into this matchup as a sizable favorite and this scoreline shows just why. The first quarter really set the tone, as they outscored Atlanta, 43 - 14, en route to a wire - to - wire win. The domination didn't end there though, as they led by 33 points at the half and by 39 points heading into the fourth quarter. The shooting disparity was key, with Milwaukee hitting 55 percent of their shots while holding Atlanta to just 44 percent from the field. The Bucks also outrebounded the Hawks, 53 - 32, while out - assisting them, 36 - 26. Milwaukee also won the points in the paint battle, 74 - 40, while winning the fastbreak points differential, 34 - 19. The Hawks (11 - 27) were led by DeAndre' Bembry, as he provided 19 points and two rebounds off the bench. DeWayne Dedmon led the starters with 14 points and two assists. Trae Young was their best player, as he tallied 13 points, three rebounds, 10 assists and two steals. John Collins finished with 12 points, seven rebounds, two assists and two steals. The Bucks (27 - 10) had all 12 players score at least eight points, as Khris Middleton led the team with 19 points, four assists and three steals. Malcolm Brogdon matched those 19 points, adding three rebounds and two assists to his tally. Giannis Antetokounmpo accumulated 16 points, eight rebounds and 10 assists while Eric Bledsoe totaled 14 points, eight rebounds and two assists. Ersan Ilyasova led the bench with 10 points and 10 boards. On deck for Milwaukee is a home matchup versus the Toronto Raptors on Saturday. As for Atlanta, they return to action on Sunday when they play host to the Miami Heat.
```

### Reference 2

```text
The Milwaukee Bucks defeated the visiting Atlanta Hawks , 144 - 112 , at Fiserv Forum on Friday . Milwaukee came into this matchup as a sizable favorite and this scoreline shows just why . The first quarter really set the tone , as they outscored Atlanta , 43 - 14 , en route to a wire - to - wire win . The domination did n't end there though , as they led by 33 points at the half and by 39 points heading into the fourth quarter . The shooting disparity was key , with Milwaukee hitting 55 percent of their shots while holding Atlanta to just 44 percent from the field . The Bucks also outrebounded the Hawks , 53 - 32 , while out - assisting them , 36 - 26 . Milwaukee also won the points in the paint battle , 74 - 40 , while winning the fastbreak points differential , 34 - 19 . The Hawks ( 11 - 27 ) were led by DeAndre ' Bembry , as he provided 19 points and two rebounds off the bench . DeWayne Dedmon led the starters with 14 points and two assists . Trae Young was their best player , as he tallied 13 points , three rebounds , 10 assists and two steals . John Collins finished with 12 points , seven rebounds , two assists and two steals . The Bucks ( 27 - 10 ) had all 12 players score at least eight points , as Khris Middleton led the team with 19 points , four assists and three steals . Malcolm Brogdon matched those 19 points , adding three rebounds and two assists to his tally . Giannis Antetokounmpo accumulated 16 points , eight rebounds and 10 assists while Eric Bledsoe totaled 14 points , eight rebounds and two assists . Ersan Ilyasova led the bench with 10 points and 10 boards . On deck for Milwaukee is a home matchup versus the Toronto Raptors on Saturday . As for Atlanta , they return to action on Sunday when they play host to the Miami Heat .
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4982__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 1204.110 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 327 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 16 |
| Support sentences | 16 |
| Generation error | — |

#### Exact generated text

```text
The Milwaukee Bucks defeated the Atlanta Hawks 144–112 on Friday, January 4, 2019, at Fiserv Forum, a 32-point margin in the 2018 season.
Milwaukee entered the matchup with a 27–10 record and the top conference standing, while Atlanta entered at 11–27 and 12th.
It was the 37th game of the season for the Bucks and the 38th for the Hawks.
Both teams were at home for their next games, with the Bucks hosting the Toronto Raptors on Saturday, January 5, and the Hawks hosting the Miami Heat on Sunday, January 6.
Milwaukee led after every recorded quarter, posting leads of 43–14, 76–43, and 118–79 through the first three quarters before finishing 144–112.
Atlanta outscored Milwaukee 33–26 in the fourth quarter, the only recorded quarter in which the Hawks held the scoring edge.
Khris Middleton, Malcolm Brogdon, and DeAndre' Bembry shared the scoring lead with 19 points each, while Giannis Antetokounmpo followed with 16.
Middleton, Eric Bledsoe, and Bembry also made the most field goals with 7 each.
Antetokounmpo tied Atlanta's Trae Young for the assists lead with 10 each; Pat Connaughton added 7 and Jeremy Lin 6.
Trae Young added 13 points for the Hawks in addition to his 10 assists.
Ersan İlyasova led all players with 11 total rebounds, including 8 defensive rebounds.
İlyasova also led the game with 3 offensive rebounds, while Eric Bledsoe, Giannis Antetokounmpo, and Alex Len each grabbed 8 boards overall.
Middleton and Young each recorded 3 steals, and Antetokounmpo and Jason Smith shared the blocks lead with 2 apiece.
Milwaukee recorded 54 total rebounds to Atlanta's 31, a 23-rebound team advantage.
The Bucks also led in made field goals (55 to 37) and assists (36 to 26), while the Hawks made more free throws (24 to 20).
Milwaukee held a 12–5 edge in offensive rebounds and a 42–26 edge on the defensive glass, and finished with more blocks (8 to 3).
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4982__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 20.789 |
| Prompt tokens | 8501 |
| Completion tokens | 1744 |
| Total tokens | 10245 |
| Output words | 182 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The Milwaukee Bucks defeated the Atlanta Hawks 144–112 on Friday, January 4, 2019, at Fiserv Forum in Milwaukee. Attendance was 17,600, exceeding the listed stadium capacity of 17,500.

Strongest findings:
- The Bucks won by 32 points and led 43–14 after the first quarter, 76–43 at halftime, and 118–79 after three quarters.
- Milwaukee shot 55% from the field (55/100), outrebounded Atlanta 54–31, and recorded more assists (36–26) and blocks (8–3).
- The Hawks committed 21 turnovers to the Bucks’ 14.
- Giannis Antetokounmpo posted a double-double with 16 points and 10 assists in 19 minutes, adding 8 rebounds and 2 blocks without a turnover.
- Khris Middleton scored 19 points on 7/8 shooting and made all four of his three-point attempts.
- Malcolm Brogdon also scored 19 points and made all seven of his free throws.
- Trae Young recorded a double-double for Atlanta with 13 points and 10 assists.
- The Bucks entered the game with a 27–10 record and the top Eastern Conference standing; the Hawks were 11–27 and 12th in the Eastern Conference.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4982__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 9.169 |
| Prompt tokens | 8538 |
| Completion tokens | 850 |
| Total tokens | 9388 |
| Output words | 209 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The Milwaukee Bucks rolled to a dominant 144-112 victory over the Atlanta Hawks on Friday night at Fiserv Forum. The Bucks led from the opening tip, building a 43-14 edge after the first quarter and never looking back. With the win, Milwaukee improved to 27-10, while Atlanta fell to 11-27.

Giannis Antetokounmpo anchored the Bucks with a double-double of 16 points and 10 assists to go with 8 rebounds. Khris Middleton scored 19 points on a perfect 4-for-4 from three-point range, and Malcolm Brogdon added 19 points, hitting all seven of his free throws. Ersan İlyasova also recorded a double-double with 10 points and 11 rebounds off the bench. Milwaukee shot 55 percent from the field and connected on 14 three-pointers.

For the Hawks, DeAndre' Bembry led all scorers with 19 points, while Trae Young posted a double-double with 13 points and 10 assists. Kevin Huerter and John Collins each scored 10 and 12 points, respectively. Atlanta struggled against Milwaukee's pressure, committing 21 turnovers overall and shooting just 44 percent from the floor.

The Bucks’ bench provided a significant boost, with Tony Snell scoring 11 and George Hill adding 12, helping Milwaukee maintain its large lead throughout the second half. The announced attendance was 17,600 for the game.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.082437256 | 0.430120522 | 0.882882883 | 0.21835443 | 0.241535724 | 0.85110724 | 0.124278724 | 0.066463212 | 0.01274105 | 1 |
| Raw-generic direct Flash | 0.04549699 | 0.321256213 | 0.783783784 | 0.256198347 | 0.215040346 | 0.852450192 | 0.174308315 | 0.343333405 | 0.016786268 | 0.666666667 |
| Task-aware direct Flash | 0.094144702 | 0.389010333 | 0.807807808 | 0.214971209 | 0.264341363 | 0.857804239 | 0.188327894 | 0.066094118 | 0.006752795 | 1 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “Milwaukee entered the matchup with a 27–10 record and the top conference standing, while Atlanta entered at 11–27 and 12th.”
     - The listed records are postgame records: each record sums to the team’s game number (37 for Milwaukee and 38 for Atlanta) and includes this result. Before the game, Milwaukee was 26–10 and Atlanta was 11–26.
  2. **TASK/FORMAT** — “The entire report is presented as a single paragraph.”
     - The requested output mode was a multi-paragraph report, so the report should be divided into multiple paragraphs.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “The Bucks entered the game with a 27–10 record and the top Eastern Conference standing; the Hawks were 11–27 and 12th in the Eastern Conference.”
     - The records are postgame records: 27–10 totals 37 games, matching Milwaukee's game number, and 11–27 totals 38, matching Atlanta's game number. Given the result, the teams entered at 26–10 and 11–26, respectively. The source also does not establish that the listed conference standings are specifically pregame standings.
  2. **TASK/FORMAT** — “The entire output is presented as a single paragraph with inline dash-separated findings.”
     - The requested output mode was a multi-paragraph report, but the response does not contain multiple paragraphs.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **5**
- Errors:
  1. **NOT CHECKABLE** — “Friday night”
     - The source supplies the date and weekday but no start time or time-of-day information.
  2. **CONTEXT** — “The Bucks led from the opening tip, building a 43-14 edge after the first quarter and never looking back.”
     - Quarter-end scores support the 43-14 first-quarter margin, but the source has no play-by-play evidence for the opening tip or for a continuous lead throughout the game.
  3. **CONTEXT** — “DeAndre' Bembry led all scorers with 19 points”
     - Bembry tied for the game-high 19 points with Milwaukee's Khris Middleton and Malcolm Brogdon rather than leading alone.
  4. **CONTEXT** — “Atlanta struggled against Milwaukee's pressure”
     - The source records 21 Atlanta turnovers but does not identify Milwaukee pressure as their cause.
  5. **CONTEXT** — “helping Milwaukee maintain its large lead throughout the second half.”
     - The source does not attribute lead maintenance to those bench performances, and quarter-end totals do not establish the continuous game state throughout the half.

---

# Case 15: `sportsett_basketball` / `4986`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | sportsett_basketball |
| Example ID | 4986 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source characters | 25515 |
| Reference count | 2 |
| Source SHA-256 | 73599b42f26fb49026855411b9096285574c9c4b053bc764d26472af03d3ae7b |
| Reference SHA-256 | aedd70124e65fb16903d0f724fc8578710fffee23a5d28d7b24ebe7e780f88f0 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```json
{
  "game": {
    "attendance": "18000",
    "capacity": "17500",
    "city": "Milwaukee",
    "day": "21",
    "dayname": "Monday",
    "game_id": "4986",
    "month": "January",
    "season": "2018",
    "stadium": "Fiserv Forum",
    "state": "Wisconsin",
    "year": "2019"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "10",
          "AST": "5",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "12",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "20",
          "FGM": "10",
          "FG_PCT": "50",
          "FTA": "12",
          "FTM": "10",
          "FT_PCT": "83",
          "MIN": "35",
          "OREB": "3",
          "PF": "4",
          "PTS": "31",
          "STL": "0",
          "TOV": "5",
          "TREB": "15",
          "first_name": "Giannis",
          "last_name": "Antetokounmpo",
          "name": "Giannis Antetokounmpo",
          "starter": "True"
        },
        {
          "+/-": "14",
          "AST": "0",
          "BLK": "5",
          "DOUBLE": "double",
          "DREB": "10",
          "FG3A": "7",
          "FG3M": "4",
          "FG3_PCT": "57",
          "FGA": "10",
          "FGM": "6",
          "FG_PCT": "60",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "34",
          "OREB": "0",
          "PF": "3",
          "PTS": "16",
          "STL": "0",
          "TOV": "1",
          "TREB": "10",
          "first_name": "Brook",
          "last_name": "Lopez",
          "name": "Brook Lopez",
          "starter": "True"
        },
        {
          "+/-": "8",
          "AST": "3",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "7",
          "FG3M": "1",
          "FG3_PCT": "14",
          "FGA": "18",
          "FGM": "6",
          "FG_PCT": "33",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "33",
          "OREB": "2",
          "PF": "1",
          "PTS": "13",
          "STL": "0",
          "TOV": "3",
          "TREB": "8",
          "first_name": "Khris",
          "last_name": "Middleton",
          "name": "Khris Middleton",
          "starter": "True"
        },
        {
          "+/-": "3",
          "AST": "2",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "14",
          "FGM": "6",
          "FG_PCT": "43",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "32",
          "OREB": "1",
          "PF": "2",
          "PTS": "19",
          "STL": "5",
          "TOV": "2",
          "TREB": "4",
          "first_name": "Malcolm",
          "last_name": "Brogdon",
          "name": "Malcolm Brogdon",
          "starter": "True"
        },
        {
          "+/-": "19",
          "AST": "5",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "7",
          "FG3M": "1",
          "FG3_PCT": "14",
          "FGA": "16",
          "FGM": "8",
          "FG_PCT": "50",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "32",
          "OREB": "1",
          "PF": "3",
          "PTS": "21",
          "STL": "2",
          "TOV": "2",
          "TREB": "4",
          "first_name": "Eric",
          "last_name": "Bledsoe",
          "name": "Eric Bledsoe",
          "starter": "True"
        },
        {
          "+/-": "-2",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "5",
          "FGM": "2",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "21",
          "OREB": "0",
          "PF": "2",
          "PTS": "5",
          "STL": "0",
          "TOV": "0",
          "TREB": "6",
          "first_name": "George",
          "last_name": "Hill",
          "name": "George Hill",
          "starter": "False"
        },
        {
          "+/-": "4",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "3",
          "FG3M": "3",
          "FG3_PCT": "100",
          "FGA": "4",
          "FGM": "4",
          "FG_PCT": "100",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "19",
          "OREB": "1",
          "PF": "2",
          "PTS": "11",
          "STL": "1",
          "TOV": "1",
          "TREB": "2",
          "first_name": "Sterling",
          "last_name": "Brown",
          "name": "Sterling Brown",
          "starter": "False"
        },
        {
          "+/-": "2",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "1",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "14",
          "OREB": "0",
          "PF": "1",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "2",
          "first_name": "D.J.",
          "last_name": "Wilson",
          "name": "D.J. Wilson",
          "starter": "False"
        },
        {
          "+/-": "-2",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "1",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "6",
          "OREB": "0",
          "PF": "1",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Ersan",
          "last_name": "İlyasova",
          "name": "Ersan İlyasova",
          "starter": "False"
        },
        {
          "+/-": "-7",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "6",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "1",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Tony",
          "last_name": "Snell",
          "name": "Tony Snell",
          "starter": "False"
        },
        {
          "+/-": "1",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "4",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Thon",
          "last_name": "Maker",
          "name": "Thon Maker",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Donte",
          "last_name": "DiVincenzo",
          "name": "Donte DiVincenzo",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Pat",
          "last_name": "Connaughton",
          "name": "Pat Connaughton",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 1,
      "division": "Central",
      "game_number": "46",
      "line_score": {
        "H1": {
          "AST": "74",
          "BLK": "30",
          "DREB": "117",
          "FG3A": "96",
          "FG3M": "40",
          "FG3_PCT": "42",
          "FGA": "2625",
          "FGM": "158",
          "FG_PCT": "6",
          "FTA": "17",
          "FTM": "16",
          "FT_PCT": "94",
          "MIN": "6060",
          "OREB": "23",
          "PTS": "3522",
          "STL": "13",
          "TOV": "23",
          "TREB": "140"
        },
        "H2": {
          "AST": "64",
          "BLK": "13",
          "DREB": "1213",
          "FG3A": "107",
          "FG3M": "62",
          "FG3_PCT": "58",
          "FGA": "2317",
          "FGM": "127",
          "FG_PCT": "5",
          "FTA": "68",
          "FTM": "58",
          "FT_PCT": "85",
          "MIN": "6060",
          "OREB": "21",
          "PTS": "3524",
          "STL": "32",
          "TOV": "54",
          "TREB": "1234"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "7",
          "BLK": "3",
          "DREB": "11",
          "FG3A": "9",
          "FG3M": "4",
          "FG3_PCT": "44",
          "FGA": "26",
          "FGM": "15",
          "FG_PCT": "58",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "2",
          "PTS": "35",
          "STL": "1",
          "TOV": "2",
          "TREB": "13"
        },
        "Q2": {
          "AST": "4",
          "BLK": "0",
          "DREB": "7",
          "FG3A": "6",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "25",
          "FGM": "8",
          "FG_PCT": "32",
          "FTA": "7",
          "FTM": "6",
          "FT_PCT": "86",
          "MIN": "60",
          "OREB": "3",
          "PTS": "22",
          "STL": "3",
          "TOV": "3",
          "TREB": "10"
        },
        "Q3": {
          "AST": "6",
          "BLK": "1",
          "DREB": "12",
          "FG3A": "10",
          "FG3M": "6",
          "FG3_PCT": "60",
          "FGA": "23",
          "FGM": "12",
          "FG_PCT": "52",
          "FTA": "6",
          "FTM": "5",
          "FT_PCT": "83",
          "MIN": "60",
          "OREB": "2",
          "PTS": "35",
          "STL": "3",
          "TOV": "5",
          "TREB": "14"
        },
        "Q4": {
          "AST": "4",
          "BLK": "3",
          "DREB": "13",
          "FG3A": "7",
          "FG3M": "2",
          "FG3_PCT": "29",
          "FGA": "17",
          "FGM": "7",
          "FG_PCT": "41",
          "FTA": "8",
          "FTM": "8",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "1",
          "PTS": "24",
          "STL": "2",
          "TOV": "4",
          "TREB": "14"
        },
        "game": {
          "AST": "21",
          "BLK": "7",
          "DREB": "43",
          "FG3A": "32",
          "FG3M": "12",
          "FG3_PCT": "38",
          "FGA": "91",
          "FGM": "42",
          "FG_PCT": "46",
          "FTA": "22",
          "FTM": "20",
          "FT_PCT": "91",
          "MIN": "4",
          "OREB": "8",
          "PF": "19",
          "PTS": "116",
          "STL": "9",
          "TOV": "14",
          "TREB": "51"
        }
      },
      "losses": "12",
      "name": "Bucks",
      "next_game": {
        "city": "Milwaukee",
        "day": "25",
        "dayname": "Friday",
        "is_home": "True",
        "month": "January",
        "opponent_name": "Hornets",
        "opponent_place": "Charlotte",
        "stadium": "Fiserv Forum",
        "year": "2019"
      },
      "next_game_id": "4987",
      "place": "Milwaukee",
      "previous_game_id": "5519",
      "wins": "34"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "-10",
          "AST": "10",
          "BLK": "1",
          "DOUBLE": "triple",
          "DREB": "9",
          "FG3A": "5",
          "FG3M": "2",
          "FG3_PCT": "40",
          "FGA": "17",
          "FGM": "6",
          "FG_PCT": "35",
          "FTA": "5",
          "FTM": "4",
          "FT_PCT": "80",
          "MIN": "32",
          "OREB": "2",
          "PF": "1",
          "PTS": "18",
          "STL": "1",
          "TOV": "3",
          "TREB": "11",
          "first_name": "Luka",
          "last_name": "Dončić",
          "name": "Luka Dončić",
          "starter": "True"
        },
        {
          "+/-": "-7",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "8",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "15",
          "FGM": "4",
          "FG_PCT": "27",
          "FTA": "2",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "31",
          "OREB": "1",
          "PF": "1",
          "PTS": "8",
          "STL": "0",
          "TOV": "2",
          "TREB": "3",
          "first_name": "Harrison",
          "last_name": "Barnes",
          "name": "Harrison Barnes",
          "starter": "True"
        },
        {
          "+/-": "-9",
          "AST": "3",
          "BLK": "4",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "8",
          "FG3M": "3",
          "FG3_PCT": "38",
          "FGA": "14",
          "FGM": "6",
          "FG_PCT": "43",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "31",
          "OREB": "0",
          "PF": "1",
          "PTS": "15",
          "STL": "3",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Wesley",
          "last_name": "Matthews",
          "name": "Wesley Matthews",
          "starter": "True"
        },
        {
          "+/-": "-15",
          "AST": "1",
          "BLK": "2",
          "DOUBLE": "double",
          "DREB": "10",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "11",
          "FGM": "6",
          "FG_PCT": "55",
          "FTA": "6",
          "FTM": "3",
          "FT_PCT": "50",
          "MIN": "31",
          "OREB": "5",
          "PF": "4",
          "PTS": "15",
          "STL": "0",
          "TOV": "3",
          "TREB": "15",
          "first_name": "DeAndre",
          "last_name": "Jordan",
          "name": "DeAndre Jordan",
          "starter": "True"
        },
        {
          "+/-": "-12",
          "AST": "5",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "15",
          "FGM": "6",
          "FG_PCT": "40",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "29",
          "OREB": "0",
          "PF": "3",
          "PTS": "16",
          "STL": "0",
          "TOV": "1",
          "TREB": "3",
          "first_name": "Jalen",
          "last_name": "Brunson",
          "name": "Jalen Brunson",
          "starter": "True"
        },
        {
          "+/-": "7",
          "AST": "2",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "5",
          "FG3M": "3",
          "FG3_PCT": "60",
          "FGA": "8",
          "FGM": "5",
          "FG_PCT": "62",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "33",
          "OREB": "1",
          "PF": "1",
          "PTS": "13",
          "STL": "2",
          "TOV": "1",
          "TREB": "5",
          "first_name": "Dorian",
          "last_name": "Finney-Smith",
          "name": "Dorian Finney-Smith",
          "starter": "False"
        },
        {
          "+/-": "-6",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "6",
          "FGM": "3",
          "FG_PCT": "50",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "17",
          "OREB": "0",
          "PF": "4",
          "PTS": "9",
          "STL": "0",
          "TOV": "1",
          "TREB": "0",
          "first_name": "Devin",
          "last_name": "Harris",
          "name": "Devin Harris",
          "starter": "False"
        },
        {
          "+/-": "-3",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "8",
          "FGM": "3",
          "FG_PCT": "38",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "16",
          "OREB": "2",
          "PF": "3",
          "PTS": "8",
          "STL": "0",
          "TOV": "0",
          "TREB": "6",
          "first_name": "Maxi",
          "last_name": "Kleber",
          "name": "Maxi Kleber",
          "starter": "False"
        },
        {
          "+/-": "5",
          "AST": "1",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "5",
          "FGM": "2",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "16",
          "OREB": "0",
          "PF": "1",
          "PTS": "4",
          "STL": "1",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Dwight",
          "last_name": "Powell",
          "name": "Dwight Powell",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Ryan",
          "last_name": "Broekhoff",
          "name": "Ryan Broekhoff",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Dirk",
          "last_name": "Nowitzki",
          "name": "Dirk Nowitzki",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Daryl",
          "last_name": "Macon",
          "name": "Daryl Macon",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Kostas",
          "last_name": "Antetokounmpo",
          "name": "Kostas Antetokounmpo",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 13,
      "division": "Southwest",
      "game_number": "46",
      "line_score": {
        "H1": {
          "AST": "87",
          "BLK": "14",
          "DREB": "812",
          "FG3A": "910",
          "FG3M": "36",
          "FG3_PCT": "4",
          "FGA": "2720",
          "FGM": "1111",
          "FG_PCT": "41",
          "FTA": "26",
          "FTM": "15",
          "FT_PCT": "58",
          "MIN": "6060",
          "OREB": "31",
          "PTS": "2633",
          "STL": "12",
          "TOV": "24",
          "TREB": "843"
        },
        "H2": {
          "AST": "36",
          "BLK": "51",
          "DREB": "89",
          "FG3A": "1011",
          "FG3M": "32",
          "FG3_PCT": "3",
          "FGA": "2527",
          "FGM": "118",
          "FG_PCT": "5",
          "FTA": "09",
          "FTM": "04",
          "FT_PCT": "44",
          "MIN": "6060",
          "OREB": "16",
          "PTS": "2522",
          "STL": "31",
          "TOV": "32",
          "TREB": "105"
        },
        "OT": {
          "AST": "0",
          "BLK": "0",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "0",
          "OREB": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0"
        },
        "Q1": {
          "AST": "8",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "9",
          "FG3M": "3",
          "FG3_PCT": "33",
          "FGA": "27",
          "FGM": "11",
          "FG_PCT": "41",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "60",
          "OREB": "3",
          "PTS": "26",
          "STL": "1",
          "TOV": "2",
          "TREB": "11"
        },
        "Q2": {
          "AST": "7",
          "BLK": "4",
          "DREB": "12",
          "FG3A": "10",
          "FG3M": "6",
          "FG3_PCT": "60",
          "FGA": "20",
          "FGM": "11",
          "FG_PCT": "55",
          "FTA": "6",
          "FTM": "5",
          "FT_PCT": "83",
          "MIN": "60",
          "OREB": "1",
          "PTS": "33",
          "STL": "2",
          "TOV": "4",
          "TREB": "13"
        },
        "Q3": {
          "AST": "3",
          "BLK": "5",
          "DREB": "8",
          "FG3A": "10",
          "FG3M": "3",
          "FG3_PCT": "30",
          "FGA": "25",
          "FGM": "11",
          "FG_PCT": "44",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "60",
          "OREB": "1",
          "PTS": "25",
          "STL": "3",
          "TOV": "3",
          "TREB": "9"
        },
        "Q4": {
          "AST": "6",
          "BLK": "1",
          "DREB": "9",
          "FG3A": "11",
          "FG3M": "2",
          "FG3_PCT": "18",
          "FGA": "27",
          "FGM": "8",
          "FG_PCT": "30",
          "FTA": "9",
          "FTM": "4",
          "FT_PCT": "44",
          "MIN": "60",
          "OREB": "6",
          "PTS": "22",
          "STL": "1",
          "TOV": "2",
          "TREB": "15"
        },
        "game": {
          "AST": "24",
          "BLK": "11",
          "DREB": "37",
          "FG3A": "40",
          "FG3M": "14",
          "FG3_PCT": "35",
          "FGA": "99",
          "FGM": "41",
          "FG_PCT": "41",
          "FTA": "17",
          "FTM": "10",
          "FT_PCT": "59",
          "MIN": "4",
          "OREB": "11",
          "PF": "19",
          "PTS": "106",
          "STL": "7",
          "TOV": "11",
          "TREB": "48"
        }
      },
      "losses": "26",
      "name": "Mavericks",
      "next_game": {
        "city": "Dallas",
        "day": "22",
        "dayname": "Tuesday",
        "is_home": "True",
        "month": "January",
        "opponent_name": "Clippers",
        "opponent_place": "Los Angeles",
        "stadium": "American Airlines Center",
        "year": "2019"
      },
      "next_game_id": "5558",
      "place": "Dallas",
      "previous_game_id": "5680",
      "wins": "20"
    }
  }
}
```

The parsed source text and structured source payload are identical for this case.

## Prepared-example metadata

```json
{
  "sportsett_id": "4986",
  "normalizer": "sportsett",
  "requested_split": "test",
  "hub_id": "GEM/sportsett_basketball",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The Milwaukee Bucks defeated the Dallas Mavericks, 116 - 106, at Fiserv Forum on Tuesday. After opening up an early nine - point lead, the Bucks (34 - 12) struggled mightily in the second quarter and only put up 22 points. As a result, they entered halftime down two points against one of the NBA's worth road teams. It didn't take long for Milwaukee to regain control of the game, however, as the team went on to win the third quarter by 10 points and managed to hold off the Mavericks (20 - 26) from that point on. Giannis Antetokounmpo had yet another stellar all - around performance in the win, posting 31 points, 15 rebounds and five assists in 36 minutes. Eric Bledsoe struggled from behind the arc, going just 1 - of - 7 from deep, but he was efficient inside and finished with 21 points on 8 - of - 16 shooting from the field. All five Bucks starters ended up reach double figures in points, with Malcolm Brogdon scoring 18 points, Brook Lopez adding 16 and Khris Middleton topping things off with 13 points of his own. The starting unit ended up scoring 100 of the team's 116 points Monday. As for the Mavericks, they failed to put up an efficient enough performance to keep up with the high - powered Bucks. As a team, they shot just 41 percent from the field overall and went just 10 - of - 17 from the free throw line. Rookie Luka Doncic led the way for the team again, posting a triple - double of 18 points, 11 rebounds and 10 assists in 33 minutes, while another rookie, Jalen Brunson, was close behind him with 16 points and five assists in 30 minutes. DeAndre Jordan and Wesley Matthews each added 15 points, while Harrison Barnes struggled mightily, going 5 - of - 14 from the field for just 8 points.
```

### Reference 2

```text
The Milwaukee Bucks defeated the Dallas Mavericks , 116 - 106 , at Fiserv Forum on Tuesday . After opening up an early nine - point lead , the Bucks ( 34 - 12 ) struggled mightily in the second quarter and only put up 22 points . As a result , they entered halftime down two points against one of the NBA 's worth road teams . It did n't take long for Milwaukee to regain control of the game , however , as the team went on to win the third quarter by 10 points and managed to hold off the Mavericks ( 20 - 26 ) from that point on . Giannis Antetokounmpo had yet another stellar all - around performance in the win , posting 31 points , 15 rebounds and five assists in 36 minutes . Eric Bledsoe struggled from behind the arc , going just 1 - of - 7 from deep , but he was efficient inside and finished with 21 points on 8 - of - 16 shooting from the field . All five Bucks starters ended up reach double figures in points , with Malcolm Brogdon scoring 18 points , Brook Lopez adding 16 and Khris Middleton topping things off with 13 points of his own . The starting unit ended up scoring 100 of the team 's 116 points Monday . As for the Mavericks , they failed to put up an efficient enough performance to keep up with the high - powered Bucks . As a team , they shot just 41 percent from the field overall and went just 10 - of - 17 from the free throw line . Rookie Luka Doncic led the way for the team again , posting a triple - double of 18 points , 11 rebounds and 10 assists in 33 minutes , while another rookie , Jalen Brunson , was close behind him with 16 points and five assists in 30 minutes . DeAndre Jordan and Wesley Matthews each added 15 points , while Harrison Barnes struggled mightily , going 5 - of - 14 from the field for just 8 points .
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4986__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 1247.383 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 302 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 14 |
| Support sentences | 14 |
| Generation error | — |

#### Exact generated text

```text
The Milwaukee Bucks defeated the Dallas Mavericks 116-106 at Fiserv Forum on Monday, January 21, 2019.
Both teams were playing their 46th game of the 2018 season when Milwaukee entered with a 34-12 record and Dallas with a 20-26 mark.
The Bucks also held a conference standing of 1, compared with 13 for the Mavericks.
Milwaukee was next scheduled to host the Hornets on Friday, January 25, while Dallas was set to host the Clippers on Tuesday, January 22.
Milwaukee led 35-26 after the first quarter, Dallas moved in front 59-57 at halftime, and the Bucks went back ahead 92-84 after the third quarter before finishing with the 116-106 win.
In the quarter-by-quarter breakdown, Dallas outscored Milwaukee 33-22 in the second period, while the Bucks answered with a 35-25 third quarter and a 24-22 fourth.
Giannis Antetokounmpo led all scorers with 31 points, tied DeAndre Jordan for a game-high 15 rebounds, and grabbed 12 defensive boards.
Antetokounmpo's 31 points included a game-high 10 made field goals, while teammate Eric Bledsoe added 21 points on 8 makes.
Jordan matched the 15-rebound total, added 15 points and led every player with 5 offensive rebounds.
Malcolm Brogdon contributed 19 points and a game-high 5 steals, and Brook Lopez hit 4 three-pointers and blocked 5 shots.
Luka Dončić led the Mavericks with 18 points while posting 11 rebounds and a game-high 10 assists, and Wesley Matthews added 15 points, 4 blocks and 3 steals.
The 10-point margin came with a 20-10 Bucks edge in made free throws, while the teams split made field goals nearly evenly at 42-41 in Milwaukee's favor.
Milwaukee outrebounded Dallas 51-48 overall and 43-37 on the defensive glass, while Dallas held an 11-8 edge in offensive rebounds.
Dallas finished with more assists (24-21) and blocks (11-7), while Milwaukee took more steals (9-7).
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4986__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 14.334 |
| Prompt tokens | 8744 |
| Completion tokens | 1181 |
| Total tokens | 9925 |
| Output words | 146 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
- The Milwaukee Bucks defeated the Dallas Mavericks 116–106 at Fiserv Forum in Milwaukee on Monday, January 21, 2019.
- Attendance was 18,000, which exceeded the listed stadium capacity of 17,500.
- The Bucks had the better team record at 34–12 and were 1st in the Eastern Conference; the Mavericks were 20–26 and 13th in the Western Conference.
- Giannis Antetokounmpo led all scorers with 31 points, adding 15 rebounds, 5 assists, and a double-double.
- Luka Dončić recorded a triple-double for the Mavericks with 18 points, 11 rebounds, and 10 assists.
- DeAndre Jordan also had a double-double with 15 points and 15 rebounds.
- Milwaukee shot 46% from the field, 38% from three-point range, and 91% from the free-throw line; Dallas shot 41%, 35%, and 59%, respectively.
- The Bucks outrebounded the Mavericks 51–48, while the Mavericks had more assists (24–21) and blocks (11–7).
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `sportsett_basketball__4986__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 14.673 |
| Prompt tokens | 8781 |
| Completion tokens | 1476 |
| Total tokens | 10257 |
| Output words | 202 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Giannis Antetokounmpo finished with 31 points and 15 rebounds, and the Milwaukee Bucks defeated the Dallas Mavericks 116-106 on Monday night at Fiserv Forum. Milwaukee led 35-26 after the first quarter, but Dallas answered with a 33-22 second quarter to take a 59-57 halftime lead. The Bucks regained control in the third, outscoring the Mavericks 35-25, and then closed the game with a 24-22 fourth quarter.

Milwaukee’s starters carried the offense. Eric Bledsoe added 21 points, Malcolm Brogdon scored 19 with five steals, and Brook Lopez posted 16 points, 10 rebounds, and five blocked shots. Khris Middleton had 13 points, while Sterling Brown added 11 off the bench. The Bucks shot 46 percent from the field, made 12 of 32 three-pointers, and went 20 of 22 from the free-throw line. They also won the rebounding battle 51-48.

Luka Dončić recorded a triple-double for Dallas with 18 points, 11 rebounds, and 10 assists. DeAndre Jordan contributed 15 points and 15 rebounds, Jalen Brunson scored 16, and Wesley Matthews added 15. The Mavericks shot 41 percent from the field and just 10 of 17 on free throws. The win improved the Bucks to 34-12, while the Mavericks dropped to 20-26. Attendance was 18,000.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.094683151 | 0.408714527 | 0.856725146 | 0.230529595 | 0.263932742 | 0.844194531 | 0.102973819 | 0.036166596 | 0.008067545 | 1 |
| Raw-generic direct Flash | 0.047304998 | 0.27720359 | 0.821637427 | 0.233766234 | 0.16615382 | 0.833431125 | 0.175221428 | 0.020314585 | 0.020314585 | 1 |
| Task-aware direct Flash | 0.094087502 | 0.413880526 | 0.839181287 | 0.30418251 | 0.270885471 | 0.873009026 | 0.206912771 | 0.021314413 | 0.008608733 | 1 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **CONTEXT** — “Milwaukee entered with a 34-12 record and Dallas with a 20-26 mark”
     - Those records each total 46 games, so they represent the teams' records after this 46th game, not their entering records. Given the result, Milwaukee entered 33-12 and Dallas entered 20-25.
  2. **TASK/FORMAT** — “The entire report is presented as one paragraph.”
     - The requested output mode was a multi-paragraph report, so the report should be divided into multiple coherent paragraphs.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **TASK/FORMAT** — “The entire output is presented as a single hyphen-separated list rather than a multi-paragraph report.”
     - Rewrite the supported findings as a report organized into multiple prose paragraphs, as required by the output mode.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **NOT CHECKABLE** — “Monday night”
     - The source supplies the date and weekday but no start time or time-of-day information.

---

# Case 16: `totto` / `totto-validation-204`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | totto |
| Example ID | totto-validation-204 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source characters | 291 |
| Reference count | 2 |
| Source SHA-256 | dddb3ae8aec408cb30f0f2c0551cf61311a2e3e8dcf8afec4e880bc2d433f032 |
| Reference SHA-256 | a89ddb504b865adb192fc492903eb90580701a77fde453fe5fdd628b53f9ebf2 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Page: Ma Ying-jeou
Section: Inauguration
Table:
Party | Candidate | Votes | Percentage
President | Vice president
 | - | - | Vincent Siew | 7,659,014 | *58.45%* | 
 | - | Frank Hsieh | Su Tseng-chang | 5,444,949 | 41.55% | 
Total | 13,103,963 | 100.00%
Cells surrounded by * are highlighted.
```

## Structured source payload

```json
{
  "table_page_title": "Ma Ying-jeou",
  "table_section_title": "Inauguration",
  "table_section_text": "",
  "table": [
    [
      {
        "column_span": 2,
        "is_header": true,
        "row_span": 2,
        "value": "Party"
      },
      {
        "column_span": 2,
        "is_header": true,
        "row_span": 1,
        "value": "Candidate"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 2,
        "value": "Votes"
      },
      {
        "column_span": 2,
        "is_header": true,
        "row_span": 2,
        "value": "Percentage"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "President"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Vice president"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Vincent Siew"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "7,659,014"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "58.45%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Frank Hsieh"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Su Tseng-chang"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "5,444,949"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "41.55%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      }
    ],
    [
      {
        "column_span": 4,
        "is_header": false,
        "row_span": 1,
        "value": "Total"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "13,103,963"
      },
      {
        "column_span": 2,
        "is_header": false,
        "row_span": 1,
        "value": "100.00%"
      }
    ]
  ],
  "highlighted_cells": [
    [
      2,
      5
    ]
  ]
}
```

## Parent table representation

```json
[
  [
    "Party",
    "Candidate",
    "Votes",
    "Percentage"
  ],
  [
    "President",
    "Vice president"
  ],
  [
    "",
    "-",
    "-",
    "Vincent Siew",
    "7,659,014",
    "58.45%",
    ""
  ],
  [
    "",
    "-",
    "Frank Hsieh",
    "Su Tseng-chang",
    "5,444,949",
    "41.55%",
    ""
  ],
  [
    "Total",
    "13,103,963",
    "100.00%"
  ]
]
```

## Prepared-example metadata

```json
{
  "overlap_subset": "True",
  "table_page_title": "Ma Ying-jeou",
  "table_section_title": "Inauguration",
  "normalizer": "totto",
  "requested_split": "validation",
  "hub_id": "GEM/totto",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
Ma won the presidency by 58.45% of the vote.
```

### Reference 2

```text
Ma first won the presidency with 58.45% of the popular vote.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-204__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 4.765 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 8 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Ma Ying-jeou received 58.45% of the vote.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-204__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 7.196 |
| Prompt tokens | 283 |
| Completion tokens | 587 |
| Total tokens | 870 |
| Output words | 62 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
In the inauguration-related election table, the Vincent Siew ticket received 7,659,014 votes, highlighted as 58.45%—the highest vote share. The Frank Hsieh/Su Tseng-chang ticket received 5,444,949 votes (41.55%). The total votes cast were 13,103,963. Thus, the strongest supported finding is that the Vincent Siew ticket won the election with a majority of votes.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-204__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 3.028 |
| Prompt tokens | 311 |
| Completion tokens | 262 |
| Total tokens | 573 |
| Output words | 12 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The highlighted cell shows Vincent Siew receiving 58.45% of the votes.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.488829032 | 0.496635849 | 0.4 | 0.631578947 | 0.55 | 0.911496103 | 0.229820535 | 0.831519663 | 0.831519663 | 0 |
| Raw-generic direct Flash | 0.018991146 | 0.184467683 | 4.9 | 0.135135135 | 0.165562914 | 0.851893783 | 0.667195082 | 0.794786423 | 0.589485765 | 0 |
| Task-aware direct Flash | 0.204480074 | 0.401339373 | 0.8 | 0.545454545 | 0.407608696 | 0.903280854 | 0.637972236 | 0.90948987 | 0.90948987 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **TASK/FORMAT** — “The generated output consists of four sentences.”
     - The requested output mode is one_sentence, so the findings should be combined into a single sentence.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 17: `totto` / `totto-validation-217`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | totto |
| Example ID | totto-validation-217 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source characters | 2429 |
| Reference count | 3 |
| Source SHA-256 | cf0974324109ee43b4bd419533f4d5d29eb0f9a9f62a6327e1f561a113f79ba6 |
| Reference SHA-256 | da51efb8651d23fa30f07395893ec141909c61010136f3d6b1fb23ea3fd7eae2 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Page: List of mayors of Prague
Section: Mayors of the Great Prague (1918–Present)
Table:
# | Portrait | Name | Time of office | Terms | Political Party | Appointer(s)
1 | - | Přemysl Šámal | 13 November 1918 | 15 June 1919 | ​1⁄3 |  | National Democracy | Elected by City Assembly (1919–1948)
2 | - | Karel Baxa | 15 June 1919 | 5 April 1937 | 3 ​1⁄2 |  | National Social
3 | - | Petr Zenkl | 6 April 1937 | 24 February 1939 | ​1⁄2 |  | National Social
4 | - | Otakar Klapka (Died in office) | 24 February 1939 | 9 July 1940 | ​1⁄2 |  | National Social
5 | - | Alois Říha | 17 July 1940 | 5 May 1945 | 1 |  | Nonpartisan (Collaborationist)
6 | - | Václav Vacek | 8 May 1945 | 7 August 1945 | Prov. |  | Communist
7 | - | Petr Zenkl | 27 August 1945 | 1 July 1946 | ​1⁄5 |  | National Social
8 | - | Václav Vacek | 1 July 1946 | 21 May 1954 | 2 |  | Communist | Elected by City Committee of the KSČ (1948–1990)
9 | - | Adolf Svoboda | 21 May 1954 | 29 June 1964 | 1 |  | Communist
10 | - | Ludvík Černý | 29 June 1964 | 10 September 1970 | 1 |  | Communist
11 | - | Zdeněk Zuska | 10 September 1970 | 22 June 1981 | 1 |  | Communist
12 | - | František Štafa | 22 June 1981 | 4 July 1988 | 1 |  | Communist
13 | - | Zdeněk Horčík | 4 July 1988 | 8 December 1989 | 1 |  | Communist
14 | - | Josef Hájek | 8 December 1989 | 23 January 1990 | 1 |  | Communist
15 | - | Jaroslav Kořán | 1 February 1990 | 13 September 1991 | Prov. |  | Civic Forum | Elected by City Assembly (1990–present)
16 | - | Milan Kondr | 28 September 1991 | 13 May 1993 | ​2⁄4 |  | Civic Democratic
17 | - | *Jan Koukal* | *13 May 1993* | *26 November 1998* | 1 ​1⁄4 |  | Civic Democratic
18 | Jan Kasl 2013.JPG | Jan Kasl | 26 November 1998 | 28 May 2002 | ​3⁄4 |  | Civic Democratic
19 | - | Igor Němec | 28 May 2002 | 28 November 2002 | ​1⁄4 |  | Civic Democratic
20 | Pavel Bém s manželkou 2013 (cropped).JPG | Pavel Bém | 28 November 2002 | 30 November 2010 | 2 |  | Civic Democratic
21 | - | Bohuslav Svoboda | 30 November 2010 | 23 May 2013 | ​3⁄4 |  | Civic Democratic
22 | Tomáš Hudeček 2014.JPG | Tomáš Hudeček | 20 June 2013 | 26 November 2014 | ​1⁄4 |  | Tradition Responsibility Prosperity
23 | Adriana Krnáčová Mayor of Prague.JPG | Adriana Krnáčová | 26 November 2014 | 15 November 2018 | 1 |  | Action of Dissatisfied Citizens
24 | - | Zdeněk Hřib | 15 November 2018 | Incumbent |  |  | Czech Pirate Party
Cells surrounded by * are highlighted.
```

## Structured source payload

```json
{
  "table_page_title": "List of mayors of Prague",
  "table_section_title": "Mayors of the Great Prague (1918–Present)",
  "table_section_text": "",
  "table": [
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "#"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Portrait"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Name"
      },
      {
        "column_span": 2,
        "is_header": true,
        "row_span": 1,
        "value": "Time of office"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Terms"
      },
      {
        "column_span": 2,
        "is_header": true,
        "row_span": 1,
        "value": "Political Party"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Appointer(s)"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Přemysl Šámal"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "13 November 1918"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "15 June 1919"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​1⁄3"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Democracy"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 7,
        "value": "Elected by City Assembly (1919–1948)"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "2"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Karel Baxa"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "15 June 1919"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "5 April 1937"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "3 ​1⁄2"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Social"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "3"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Petr Zenkl"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "6 April 1937"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "24 February 1939"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​1⁄2"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Social"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "4"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Otakar Klapka (Died in office)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "24 February 1939"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "9 July 1940"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​1⁄2"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Social"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "5"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Alois Říha"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "17 July 1940"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "5 May 1945"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Nonpartisan (Collaborationist)"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "6"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Václav Vacek"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "8 May 1945"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "7 August 1945"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Prov."
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "7"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Petr Zenkl"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "27 August 1945"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1 July 1946"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​1⁄5"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Social"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "8"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Václav Vacek"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1 July 1946"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "21 May 1954"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "2"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 7,
        "value": "Elected by City Committee of the KSČ (1948–1990)"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "9"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Adolf Svoboda"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "21 May 1954"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "29 June 1964"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "10"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Ludvík Černý"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "29 June 1964"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "10 September 1970"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "11"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Zdeněk Zuska"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "10 September 1970"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22 June 1981"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "12"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "František Štafa"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22 June 1981"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "4 July 1988"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "13"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Zdeněk Horčík"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "4 July 1988"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "8 December 1989"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "14"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Josef Hájek"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "8 December 1989"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "23 January 1990"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Communist"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "15"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Jaroslav Kořán"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1 February 1990"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "13 September 1991"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Prov."
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Civic Forum"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 10,
        "value": "Elected by City Assembly (1990–present)"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "16"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Milan Kondr"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "28 September 1991"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "13 May 1993"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​2⁄4"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Civic Democratic"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "17"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Jan Koukal"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "13 May 1993"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "26 November 1998"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1 ​1⁄4"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Civic Democratic"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "18"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Jan Kasl 2013.JPG"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Jan Kasl"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "26 November 1998"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "28 May 2002"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​3⁄4"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Civic Democratic"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "19"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Igor Němec"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "28 May 2002"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "28 November 2002"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​1⁄4"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Civic Democratic"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "20"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pavel Bém s manželkou 2013 (cropped).JPG"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pavel Bém"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "28 November 2002"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "30 November 2010"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "2"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Civic Democratic"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "21"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Bohuslav Svoboda"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "30 November 2010"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "23 May 2013"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​3⁄4"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Civic Democratic"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "22"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Tomáš Hudeček 2014.JPG"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Tomáš Hudeček"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20 June 2013"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "26 November 2014"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "​1⁄4"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Tradition Responsibility Prosperity"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "23"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Adriana Krnáčová Mayor of Prague.JPG"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Adriana Krnáčová"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "26 November 2014"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "15 November 2018"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Action of Dissatisfied Citizens"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "24"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "-"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Zdeněk Hřib"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "15 November 2018"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Incumbent"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": ""
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Czech Pirate Party"
      }
    ]
  ],
  "highlighted_cells": [
    [
      17,
      2
    ],
    [
      17,
      3
    ],
    [
      17,
      4
    ]
  ]
}
```

## Parent table representation

```json
[
  [
    "#",
    "Portrait",
    "Name",
    "Time of office",
    "Terms",
    "Political Party",
    "Appointer(s)"
  ],
  [
    "1",
    "-",
    "Přemysl Šámal",
    "13 November 1918",
    "15 June 1919",
    "​1⁄3",
    "",
    "National Democracy",
    "Elected by City Assembly (1919–1948)"
  ],
  [
    "2",
    "-",
    "Karel Baxa",
    "15 June 1919",
    "5 April 1937",
    "3 ​1⁄2",
    "",
    "National Social"
  ],
  [
    "3",
    "-",
    "Petr Zenkl",
    "6 April 1937",
    "24 February 1939",
    "​1⁄2",
    "",
    "National Social"
  ],
  [
    "4",
    "-",
    "Otakar Klapka (Died in office)",
    "24 February 1939",
    "9 July 1940",
    "​1⁄2",
    "",
    "National Social"
  ],
  [
    "5",
    "-",
    "Alois Říha",
    "17 July 1940",
    "5 May 1945",
    "1",
    "",
    "Nonpartisan (Collaborationist)"
  ],
  [
    "6",
    "-",
    "Václav Vacek",
    "8 May 1945",
    "7 August 1945",
    "Prov.",
    "",
    "Communist"
  ],
  [
    "7",
    "-",
    "Petr Zenkl",
    "27 August 1945",
    "1 July 1946",
    "​1⁄5",
    "",
    "National Social"
  ],
  [
    "8",
    "-",
    "Václav Vacek",
    "1 July 1946",
    "21 May 1954",
    "2",
    "",
    "Communist",
    "Elected by City Committee of the KSČ (1948–1990)"
  ],
  [
    "9",
    "-",
    "Adolf Svoboda",
    "21 May 1954",
    "29 June 1964",
    "1",
    "",
    "Communist"
  ],
  [
    "10",
    "-",
    "Ludvík Černý",
    "29 June 1964",
    "10 September 1970",
    "1",
    "",
    "Communist"
  ],
  [
    "11",
    "-",
    "Zdeněk Zuska",
    "10 September 1970",
    "22 June 1981",
    "1",
    "",
    "Communist"
  ],
  [
    "12",
    "-",
    "František Štafa",
    "22 June 1981",
    "4 July 1988",
    "1",
    "",
    "Communist"
  ],
  [
    "13",
    "-",
    "Zdeněk Horčík",
    "4 July 1988",
    "8 December 1989",
    "1",
    "",
    "Communist"
  ],
  [
    "14",
    "-",
    "Josef Hájek",
    "8 December 1989",
    "23 January 1990",
    "1",
    "",
    "Communist"
  ],
  [
    "15",
    "-",
    "Jaroslav Kořán",
    "1 February 1990",
    "13 September 1991",
    "Prov.",
    "",
    "Civic Forum",
    "Elected by City Assembly (1990–present)"
  ],
  [
    "16",
    "-",
    "Milan Kondr",
    "28 September 1991",
    "13 May 1993",
    "​2⁄4",
    "",
    "Civic Democratic"
  ],
  [
    "17",
    "-",
    "Jan Koukal",
    "13 May 1993",
    "26 November 1998",
    "1 ​1⁄4",
    "",
    "Civic Democratic"
  ],
  [
    "18",
    "Jan Kasl 2013.JPG",
    "Jan Kasl",
    "26 November 1998",
    "28 May 2002",
    "​3⁄4",
    "",
    "Civic Democratic"
  ],
  [
    "19",
    "-",
    "Igor Němec",
    "28 May 2002",
    "28 November 2002",
    "​1⁄4",
    "",
    "Civic Democratic"
  ],
  [
    "20",
    "Pavel Bém s manželkou 2013 (cropped).JPG",
    "Pavel Bém",
    "28 November 2002",
    "30 November 2010",
    "2",
    "",
    "Civic Democratic"
  ],
  [
    "21",
    "-",
    "Bohuslav Svoboda",
    "30 November 2010",
    "23 May 2013",
    "​3⁄4",
    "",
    "Civic Democratic"
  ],
  [
    "22",
    "Tomáš Hudeček 2014.JPG",
    "Tomáš Hudeček",
    "20 June 2013",
    "26 November 2014",
    "​1⁄4",
    "",
    "Tradition Responsibility Prosperity"
  ],
  [
    "23",
    "Adriana Krnáčová Mayor of Prague.JPG",
    "Adriana Krnáčová",
    "26 November 2014",
    "15 November 2018",
    "1",
    "",
    "Action of Dissatisfied Citizens"
  ],
  [
    "24",
    "-",
    "Zdeněk Hřib",
    "15 November 2018",
    "Incumbent",
    "",
    "",
    "Czech Pirate Party"
  ]
]
```

## Prepared-example metadata

```json
{
  "overlap_subset": "True",
  "table_page_title": "List of mayors of Prague",
  "table_section_title": "Mayors of the Great Prague (1918–Present)",
  "normalizer": "totto",
  "requested_split": "validation",
  "hub_id": "GEM/totto",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
From 1993 to 1998, Jan Koukal was mayor of Prague.
```

### Reference 2

```text
Jan Koukal was the mayor of Prague from 1993 to 1998.
```

### Reference 3

```text
Jan Koukal was mayor of Prague from 1993 to 1998.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-217__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 6.950 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 19 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
In the list of mayors of Prague, Jan Koukal held office from 13 May 1993 to 26 November 1998.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-217__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 12.036 |
| Prompt tokens | 1125 |
| Completion tokens | 1065 |
| Total tokens | 2190 |
| Output words | 210 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The strongest supported findings from the table are:

- The table lists 24 mayors of Prague between 1918 and the present, from Přemysl Šámal (taking office 13 November 1918) to Zdeněk Hřib (incumbent since 15 November 2018).
- Karel Baxa served the longest single continuous mayoral tenure, from 15 June 1919 to 5 April 1937, recorded as 3 1⁄2 terms.
- Petr Zenkl and Václav Vacek each served two non-consecutive periods as mayor: Zenkl in 1937–1939 and 1945–1946; Vacek in 1945 (provisional) and 1946–1954.
- Otakar Klapka is explicitly noted as having died in office while mayor.
- Political party representation is clearly clustered: early mayors were from National Democracy or the National Social party; from Václav Vacek’s 1945 appointment through Josef Hájek’s 1989–1990 term, all listed mayors were Communists; after 1990, most mayors were from the Civic Democratic Party until 2013, with later mayors from other parties.
- Until the 1990s, one wartime mayor is listed as a nonpartisan collaborationist: Alois Říha (1940–1945).
- The method of election or appointment changed over time: rows 1–7 are marked “Elected by City Assembly (1919–1948),” rows 8–14 are marked “Elected by City Committee of the KSČ (1948–1990),” and rows 15–24 are marked “Elected by City Assembly (1990–present).”
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-217__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 4.465 |
| Prompt tokens | 1153 |
| Completion tokens | 429 |
| Total tokens | 1582 |
| Output words | 19 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The highlighted cells indicate that Jan Koukal's time of office was from 13 May 1993 to 26 November 1998.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.117628978 | 0.528558009 | 1.161290323 | 0.533333333 | 0.649717514 | 0.928236008 | 0.290549457 | 0.022479815 | 0.022479815 | 1 |
| Raw-generic direct Flash | 0.004090022 | 0.07667982 | 19.35483871 | 0.052173913 | 0.098684211 | 0.789236844 | 0.445211738 | 0.081028856 | 0.081028856 | 1 |
| Task-aware direct Flash | 0.064399314 | 0.379497791 | 1.258064516 | 0.466666667 | 0.450873941 | 0.899896801 | 0.350539207 | 0.011544947 | 0.011544947 | 1 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **4**
- Errors:
  1. **NUMBER** — “The table lists 24 mayors of Prague”
     - The table has 24 numbered officeholding entries, but only 22 distinct mayors because Petr Zenkl and Václav Vacek each appear twice.
  2. **CONTEXT** — “from Václav Vacek’s 1945 appointment through Josef Hájek’s 1989–1990 term, all listed mayors were Communists”
     - Petr Zenkl, a National Social politician, served between Václav Vacek’s two periods, from 27 August 1945 to 1 July 1946. The uninterrupted sequence of listed Communist officeholders begins with Vacek’s second period in 1946, not his 1945 period.
  3. **OMISSION** — “The strongest supported findings from the table are:”
     - The output omits the highlighted finding: Jan Koukal served from 13 May 1993 to 26 November 1998.
  4. **TASK/FORMAT** — “The strongest supported findings from the table are: - The table lists 24 mayors ... rows 15–24 are marked “Elected by City Assembly (1990–present).””
     - The requested output mode was one sentence, but the response consists of an introduction followed by seven separate bullet-like sentences.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 18: `totto` / `totto-validation-244`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | totto |
| Example ID | totto-validation-244 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source characters | 8415 |
| Reference count | 3 |
| Source SHA-256 | 3cfadaf4cb0c28b5ffb74ad1ff7cf3f3242fd4cd6a6a3af44e59435994106c02 |
| Reference SHA-256 | 67b4d3c06c37c939792d14b073fa6f941938733f4d6779daf3ad7e470faf470e |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Page: List of Speakers of the Massachusetts House of Representatives
Section: House of Representatives under the Massachusetts Constitution
Table:
Speaker | Party | Years ↑ | City or Town (District) | Electoral history
Caleb Davis | None | 1780–1782 | Boston | Resigned
Nathaniel Gorham | None | 1782–1783 | Charlestown | [Data unknown/missing.]
Tristram Dalton | None | 1783–1784 | Newbury | Elected to State Senate
Samuel Allyne Otis | None | 1784–1785 | Barnstable | [Data unknown/missing.]
Nathaniel Gorham | None | 1785–1786 | Charlestown | [Data unknown/missing.]
Artemas Ward | None | 1786–1787 | Shrewsbury | [Data unknown/missing.]
James Warren | None | 1787–1788 | Plymouth | [Data unknown/missing.]
Theodore Sedgwick | Pro-Administration | 1788–1789 | Sheffield | Elected to the U.S. House of Representatives
David Cobb | Pro-Administration | 1789–1793 | Taunton | Elected to the U.S. House of Representatives
Edward Robbins | Democratic-Republican | 1793–1802 | Boston | Elected Lieutenant Governor of Massachusetts
John Coffin Jones | Federalist | 1802–1803 | Boston | [Data unknown/missing.]
Harrison Gray Otis | Federalist | 1803–1805 | Boston | Elected to the State Senate
Timothy Bigelow | Federalist | 1805–1806 | Worcester | Party lost majority
Perez Morton | Democratic-Republican | 1806–1808 | Dorchester | Party lost majority
Timothy Bigelow | Federalist | 1808–1810 | Worcester | Party lost majority
Perez Morton | Democratic-Republican | 1810–1811 | Dorchester | Resigned
Joseph Story | Democratic-Republican | 1811–1812 | Salem | Resigned when appointed Associate Justice of the Supreme Court of the United States
Eleazer Ripley | Democratic-Republican | 1812 | Waterville | Joined United States Army
Timothy Bigelow | Federalist | 1812–1820 | Worcester | [Data unknown/missing.]
Elijah H. Mills | Federalist | 1820–1821 | Northampton | Elected to the U.S. House of Representatives
Josiah Quincy III | Federalist | 1821–1822 | Boston | Resigned to become Judge of Boston Municipal Court
Luther Lawrence | Federalist | 1822 | Lowell | Party lost majority
Levi Lincoln, Jr. | National Republican | 1822–1823 | Worcester | Elected Lieutenant Governor of Massachusetts
William C. Jarvis | National Republican | 1823–1825 | Woburn | Party lost majority
Timothy Fuller | Democratic-Republican | 1825–1826 | Cambridgeport | Party lost majority
William C. Jarvis | National Republican | 1826–1828 | Woburn | [Data unknown/missing.]
William B. Calhoun | National Republican | 1828–1834 | Springfield | Elected to the U.S. House of Representatives
Julius Rockwell | Whig | 1835–1837 | Pittsfield | Resigned when appointed commissioner of the Bank of Massachusetts
Robert Charles Winthrop | Whig | 1838–1840 | Boston | Elected to the U.S. House of Representatives
George Ashmun | Whig | 1841 | Blandford | [Data unknown/missing.]
Thomas H. Kinnicutt | Whig | 1842 | Worcester | [Data unknown/missing.]
Daniel P. King | Whig | 1843 | South Danvers | [Data unknown/missing.]
Thomas H. Kinnicutt | Whig | 1844 | Worcester | Resigned
Samuel H. Walley, Jr. | Whig | 1844–1846 | Boston | [Data unknown/missing.]
Ebenezer Bradbury | Whig | 1847 | Newburyport | [Data unknown/missing.]
Francis Crowninshield | Whig | 1848–1849 | Boston | [Data unknown/missing.]
Ensign H. Kellogg | Whig | 1850 | Pittsfield | [Data unknown/missing.]
Nathaniel Prentice Banks | Democratic/Free Soil Coalition | 1851–1852 | Waltham | Elected to the U.S. House of Representatives
George Bliss | Whig | 1853 | Springfield | [Data unknown/missing.]
Otis P. Lord | Whig | 1854 | Salem | Party lost majority
Daniel C. Eddy | Know Nothing | 1855 | Lowell | [Data unknown/missing.]
Charles A. Phelps | Know Nothing | 1856–1857 | Boston | Elected to the Massachusetts Senate; Party Lost election
Julius Rockwell | Republican | 1858 | Pittsfield | Resigned when appointed to the Massachusetts Superior Court
Charles Hale | Republican | 1859 | Boston | [Data unknown/missing.]
John A. Goodwin | Republican | 1860–1861 | Lowell | [Data unknown/missing.]
Alexander Hamilton Bullock | Republican | 1862–1865 | Worcester | Elected Governor of Massachusetts
James M. Stone | Republican | 1866–1867 | Charlestown | [Data unknown/missing.]
Harvey Jewell | Republican | 1868–1871 | Boston | [Data unknown/missing.]
John E. Sanford | Republican | 1872–1875 | Taunton | [Data unknown/missing.]
John Davis Long | Republican | 1876–1878 | Hingham | Elected Lieutenant Governor of Massachusetts
Levi C. Wade | Republican | 1879 | Newton | [Data unknown/missing.]
Charles J. Noyes | Republican | 1880–1882 | Boston (14th Suffolk) | [Data unknown/missing.]
George Augustus Marden | Republican | 1883–1884 | Lowell | [Data unknown/missing.]
John Q. A. Brackett | Republican | January 7, 1885 – 1886 | Boston (17th Suffolk) | Elected Lieutenant Governor of Massachusetts
Charles J. Noyes | Republican | 1887–1888 | Boston (14th Suffolk) | [Data unknown/missing.]
William Emerson Barrett | Republican | 1889–1893 | Melrose (11th Middlesex) | Elected to the U.S. House of Representatives
George von Lengerke Meyer | Republican | 1894–1896 | Boston (9th Suffolk) | [Data unknown/missing.]
John Lewis Bates | Republican | 1897–1899 | Boston (1st Suffolk) | Elected Lieutenant Governor of Massachusetts
James J. Myers | Republican | 1900–1903 | Cambridge (1st Middlesex) | Retired
Louis A. Frothingham | Republican | 1904–1905 | Boston (11th Suffolk) | Left House to run for governor
John N. Cole | Republican | 1906–1908 | Andover (8th Essex) | Left House to run for Lieutenant Governor
Joseph H. Walker | Republican | 1909–1911 | Brookline (2nd Norfolk) | Left House to run for governor
Grafton D. Cushing | Republican | 1912–1914 | Boston (11th Suffolk) | Elected Lieutenant Governor of Massachusetts
Channing H. Cox | Republican | 1915–1918 | Boston (10th Suffolk) | Elected Lieutenant Governor of Massachusetts
Joseph E. Warner | Republican | 1919–1920 | Taunton (4th Bristol) | Lost primary for Lieutenant Governor of Massachusetts to Alvan Fuller
Benjamin Loring Young | Republican | 1921–1924 | Weston (13th Middlesex) | [Data unknown/missing.]
John C. Hull | Republican | 1925–1929 | Leominster (11th Worcester) | Retired
Leverett Saltonstall | Republican | 1929–1936 | Chestnut Hill (5th Middlesex) | Defeated for election as Lieutenant Governor by Francis E. Kelly
Horace T. Cahill | Republican | 1937–1938 | Braintree (6th Norfolk) | Elected Lieutenant Governor of Massachusetts
Christian Herter | Republican | 1939–1942 | Boston (5th Suffolk) | Elected to the U.S. House of Representatives
Rudolph King | Republican | 1943–1944 | Millis (8th Norfolk) | Resigned to run become Registrar of Motor Vehicles
Frederick Willis | Republican | 1945–1948 | Saugus (10th Essex) | Party lost majority
Thomas P. O'Neill | Democratic | 1949–1952 | Cambridge (3rd Middlesex) | Party lost majority; O'Neill elected to U.S. House of Representatives
Charles Gibbons | Republican | 1953–1954 | Stoneham (22nd Middlesex) | Party lost majority
Michael F. Skerry | Democratic | 1955–1957 | Medford (27th Middlesex) | Resigned when appointed Clerk of the Malden District Court
John F. Thompson | Democratic | 1958–1964 | Ludlow (2nd Hampden) | Resigned after being indicted on charges of conspiracy and bribery
John Davoren | Democratic | 1965–1967 | Milford (9th Worcester) | Resigned when appointed Secretary of the Commonwealth
Robert H. Quinn | Democratic | 1967–1969 | Boston (9th Suffolk) | Elected Massachusetts Attorney General
David M. Bartley | Democratic | 1969–1975 | Holyoke (7th Hampden) | Resigned to become President of Holyoke Community College
Thomas W. McGee | Democratic | 1975–1984 | Lynn (20th Essex) | Defeated by Keverian in leadership challenge
*George Keverian* | *Democratic* | *1985–1990* | Everett (39th Middlesex) | Retired to run for State Treasurer
Charles Flaherty | Democratic | 1991 – April 9, 1996 | Cambridge (27th Middlesex) | Resigned: pleaded guilty to tax evasion
Thomas Finneran | Democratic | April 9, 1996 – September 28, 2004 | Mattapan (12th Suffolk) | Resigned due to allegations of perjury and obstruction of justice
Salvatore DiMasi | Democratic | September 28, 2004 – January 27, 2009 | Boston (3rd Suffolk) | Resigned: convicted of conspiracy, honest services fraud, and extortion
Robert DeLeo | Democratic | January 27, 2009 – present | Winthrop (19th Suffolk) | Current Speaker
Cells surrounded by * are highlighted.
```

## Structured source payload

```json
{
  "table_page_title": "List of Speakers of the Massachusetts House of Representatives",
  "table_section_title": "House of Representatives under the Massachusetts Constitution",
  "table_section_text": "",
  "table": [
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Speaker"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Party"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Years ↑"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "City or Town (District)"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Electoral history"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Caleb Davis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "None"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1780–1782"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Nathaniel Gorham"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "None"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1782–1783"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charlestown"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Tristram Dalton"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "None"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1783–1784"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Newbury"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to State Senate"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Samuel Allyne Otis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "None"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1784–1785"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Barnstable"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Nathaniel Gorham"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "None"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1785–1786"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charlestown"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Artemas Ward"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "None"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1786–1787"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Shrewsbury"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "James Warren"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "None"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1787–1788"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Plymouth"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Theodore Sedgwick"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pro-Administration"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1788–1789"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Sheffield"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "David Cobb"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pro-Administration"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1789–1793"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Taunton"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Edward Robbins"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic-Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1793–1802"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John Coffin Jones"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1802–1803"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Harrison Gray Otis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1803–1805"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the State Senate"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Timothy Bigelow"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1805–1806"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Worcester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Perez Morton"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic-Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1806–1808"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Dorchester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Timothy Bigelow"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1808–1810"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Worcester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Perez Morton"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic-Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1810–1811"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Dorchester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Joseph Story"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic-Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1811–1812"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Salem"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned when appointed Associate Justice of the Supreme Court of the United States"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Eleazer Ripley"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic-Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1812"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Waterville"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Joined United States Army"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Timothy Bigelow"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1812–1820"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Worcester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elijah H. Mills"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1820–1821"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Northampton"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Josiah Quincy III"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1821–1822"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned to become Judge of Boston Municipal Court"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Luther Lawrence"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Federalist"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1822"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Lowell"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Levi Lincoln, Jr."
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1822–1823"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Worcester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "William C. Jarvis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1823–1825"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Woburn"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Timothy Fuller"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic-Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1825–1826"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Cambridgeport"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "William C. Jarvis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1826–1828"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Woburn"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "William B. Calhoun"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "National Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1828–1834"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Springfield"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Julius Rockwell"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1835–1837"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pittsfield"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned when appointed commissioner of the Bank of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Robert Charles Winthrop"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1838–1840"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "George Ashmun"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1841"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Blandford"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Thomas H. Kinnicutt"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1842"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Worcester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Daniel P. King"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1843"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "South Danvers"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Thomas H. Kinnicutt"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1844"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Worcester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Samuel H. Walley, Jr."
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1844–1846"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Ebenezer Bradbury"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1847"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Newburyport"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Francis Crowninshield"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1848–1849"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Ensign H. Kellogg"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1850"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pittsfield"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Nathaniel Prentice Banks"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic/Free Soil Coalition"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1851–1852"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Waltham"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "George Bliss"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1853"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Springfield"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Otis P. Lord"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Whig"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1854"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Salem"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Daniel C. Eddy"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Know Nothing"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1855"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Lowell"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charles A. Phelps"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Know Nothing"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1856–1857"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the Massachusetts Senate; Party Lost election"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Julius Rockwell"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1858"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pittsfield"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned when appointed to the Massachusetts Superior Court"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charles Hale"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1859"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John A. Goodwin"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1860–1861"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Lowell"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Alexander Hamilton Bullock"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1862–1865"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Worcester"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "James M. Stone"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1866–1867"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charlestown"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Harvey Jewell"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1868–1871"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John E. Sanford"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1872–1875"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Taunton"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John Davis Long"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1876–1878"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Hingham"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Levi C. Wade"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1879"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Newton"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charles J. Noyes"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1880–1882"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (14th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "George Augustus Marden"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1883–1884"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Lowell"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John Q. A. Brackett"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "January 7, 1885 – 1886"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (17th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charles J. Noyes"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1887–1888"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (14th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "William Emerson Barrett"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1889–1893"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Melrose (11th Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "George von Lengerke Meyer"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1894–1896"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (9th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John Lewis Bates"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1897–1899"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (1st Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "James J. Myers"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1900–1903"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Cambridge (1st Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Retired"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Louis A. Frothingham"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1904–1905"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (11th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Left House to run for governor"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John N. Cole"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1906–1908"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Andover (8th Essex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Left House to run for Lieutenant Governor"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Joseph H. Walker"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1909–1911"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Brookline (2nd Norfolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Left House to run for governor"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Grafton D. Cushing"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1912–1914"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (11th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Channing H. Cox"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1915–1918"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (10th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Joseph E. Warner"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1919–1920"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Taunton (4th Bristol)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Lost primary for Lieutenant Governor of Massachusetts to Alvan Fuller"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Benjamin Loring Young"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1921–1924"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Weston (13th Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "[Data unknown/missing.]"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John C. Hull"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1925–1929"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Leominster (11th Worcester)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Retired"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Leverett Saltonstall"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1929–1936"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Chestnut Hill (5th Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Defeated for election as Lieutenant Governor by Francis E. Kelly"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Horace T. Cahill"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1937–1938"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Braintree (6th Norfolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Lieutenant Governor of Massachusetts"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Christian Herter"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1939–1942"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (5th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected to the U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Rudolph King"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1943–1944"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Millis (8th Norfolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned to run become Registrar of Motor Vehicles"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Frederick Willis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1945–1948"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Saugus (10th Essex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Thomas P. O'Neill"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1949–1952"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Cambridge (3rd Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority; O'Neill elected to U.S. House of Representatives"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charles Gibbons"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Republican"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1953–1954"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Stoneham (22nd Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Party lost majority"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Michael F. Skerry"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1955–1957"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Medford (27th Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned when appointed Clerk of the Malden District Court"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John F. Thompson"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1958–1964"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Ludlow (2nd Hampden)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned after being indicted on charges of conspiracy and bribery"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "John Davoren"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1965–1967"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Milford (9th Worcester)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned when appointed Secretary of the Commonwealth"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Robert H. Quinn"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1967–1969"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (9th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Elected Massachusetts Attorney General"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "David M. Bartley"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1969–1975"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Holyoke (7th Hampden)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned to become President of Holyoke Community College"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Thomas W. McGee"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1975–1984"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Lynn (20th Essex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Defeated by Keverian in leadership challenge"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "George Keverian"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1985–1990"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Everett (39th Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Retired to run for State Treasurer"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Charles Flaherty"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "1991 – April 9, 1996"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Cambridge (27th Middlesex)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned: pleaded guilty to tax evasion"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Thomas Finneran"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "April 9, 1996 – September 28, 2004"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Mattapan (12th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned due to allegations of perjury and obstruction of justice"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Salvatore DiMasi"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "September 28, 2004 – January 27, 2009"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston (3rd Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Resigned: convicted of conspiracy, honest services fraud, and extortion"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Robert DeLeo"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Democratic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "January 27, 2009 – present"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Winthrop (19th Suffolk)"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Current Speaker"
      }
    ]
  ],
  "highlighted_cells": [
    [
      81,
      0
    ],
    [
      81,
      1
    ],
    [
      81,
      2
    ]
  ]
}
```

## Parent table representation

```json
[
  [
    "Speaker",
    "Party",
    "Years ↑",
    "City or Town (District)",
    "Electoral history"
  ],
  [
    "Caleb Davis",
    "None",
    "1780–1782",
    "Boston",
    "Resigned"
  ],
  [
    "Nathaniel Gorham",
    "None",
    "1782–1783",
    "Charlestown",
    "[Data unknown/missing.]"
  ],
  [
    "Tristram Dalton",
    "None",
    "1783–1784",
    "Newbury",
    "Elected to State Senate"
  ],
  [
    "Samuel Allyne Otis",
    "None",
    "1784–1785",
    "Barnstable",
    "[Data unknown/missing.]"
  ],
  [
    "Nathaniel Gorham",
    "None",
    "1785–1786",
    "Charlestown",
    "[Data unknown/missing.]"
  ],
  [
    "Artemas Ward",
    "None",
    "1786–1787",
    "Shrewsbury",
    "[Data unknown/missing.]"
  ],
  [
    "James Warren",
    "None",
    "1787–1788",
    "Plymouth",
    "[Data unknown/missing.]"
  ],
  [
    "Theodore Sedgwick",
    "Pro-Administration",
    "1788–1789",
    "Sheffield",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "David Cobb",
    "Pro-Administration",
    "1789–1793",
    "Taunton",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "Edward Robbins",
    "Democratic-Republican",
    "1793–1802",
    "Boston",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "John Coffin Jones",
    "Federalist",
    "1802–1803",
    "Boston",
    "[Data unknown/missing.]"
  ],
  [
    "Harrison Gray Otis",
    "Federalist",
    "1803–1805",
    "Boston",
    "Elected to the State Senate"
  ],
  [
    "Timothy Bigelow",
    "Federalist",
    "1805–1806",
    "Worcester",
    "Party lost majority"
  ],
  [
    "Perez Morton",
    "Democratic-Republican",
    "1806–1808",
    "Dorchester",
    "Party lost majority"
  ],
  [
    "Timothy Bigelow",
    "Federalist",
    "1808–1810",
    "Worcester",
    "Party lost majority"
  ],
  [
    "Perez Morton",
    "Democratic-Republican",
    "1810–1811",
    "Dorchester",
    "Resigned"
  ],
  [
    "Joseph Story",
    "Democratic-Republican",
    "1811–1812",
    "Salem",
    "Resigned when appointed Associate Justice of the Supreme Court of the United States"
  ],
  [
    "Eleazer Ripley",
    "Democratic-Republican",
    "1812",
    "Waterville",
    "Joined United States Army"
  ],
  [
    "Timothy Bigelow",
    "Federalist",
    "1812–1820",
    "Worcester",
    "[Data unknown/missing.]"
  ],
  [
    "Elijah H. Mills",
    "Federalist",
    "1820–1821",
    "Northampton",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "Josiah Quincy III",
    "Federalist",
    "1821–1822",
    "Boston",
    "Resigned to become Judge of Boston Municipal Court"
  ],
  [
    "Luther Lawrence",
    "Federalist",
    "1822",
    "Lowell",
    "Party lost majority"
  ],
  [
    "Levi Lincoln, Jr.",
    "National Republican",
    "1822–1823",
    "Worcester",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "William C. Jarvis",
    "National Republican",
    "1823–1825",
    "Woburn",
    "Party lost majority"
  ],
  [
    "Timothy Fuller",
    "Democratic-Republican",
    "1825–1826",
    "Cambridgeport",
    "Party lost majority"
  ],
  [
    "William C. Jarvis",
    "National Republican",
    "1826–1828",
    "Woburn",
    "[Data unknown/missing.]"
  ],
  [
    "William B. Calhoun",
    "National Republican",
    "1828–1834",
    "Springfield",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "Julius Rockwell",
    "Whig",
    "1835–1837",
    "Pittsfield",
    "Resigned when appointed commissioner of the Bank of Massachusetts"
  ],
  [
    "Robert Charles Winthrop",
    "Whig",
    "1838–1840",
    "Boston",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "George Ashmun",
    "Whig",
    "1841",
    "Blandford",
    "[Data unknown/missing.]"
  ],
  [
    "Thomas H. Kinnicutt",
    "Whig",
    "1842",
    "Worcester",
    "[Data unknown/missing.]"
  ],
  [
    "Daniel P. King",
    "Whig",
    "1843",
    "South Danvers",
    "[Data unknown/missing.]"
  ],
  [
    "Thomas H. Kinnicutt",
    "Whig",
    "1844",
    "Worcester",
    "Resigned"
  ],
  [
    "Samuel H. Walley, Jr.",
    "Whig",
    "1844–1846",
    "Boston",
    "[Data unknown/missing.]"
  ],
  [
    "Ebenezer Bradbury",
    "Whig",
    "1847",
    "Newburyport",
    "[Data unknown/missing.]"
  ],
  [
    "Francis Crowninshield",
    "Whig",
    "1848–1849",
    "Boston",
    "[Data unknown/missing.]"
  ],
  [
    "Ensign H. Kellogg",
    "Whig",
    "1850",
    "Pittsfield",
    "[Data unknown/missing.]"
  ],
  [
    "Nathaniel Prentice Banks",
    "Democratic/Free Soil Coalition",
    "1851–1852",
    "Waltham",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "George Bliss",
    "Whig",
    "1853",
    "Springfield",
    "[Data unknown/missing.]"
  ],
  [
    "Otis P. Lord",
    "Whig",
    "1854",
    "Salem",
    "Party lost majority"
  ],
  [
    "Daniel C. Eddy",
    "Know Nothing",
    "1855",
    "Lowell",
    "[Data unknown/missing.]"
  ],
  [
    "Charles A. Phelps",
    "Know Nothing",
    "1856–1857",
    "Boston",
    "Elected to the Massachusetts Senate; Party Lost election"
  ],
  [
    "Julius Rockwell",
    "Republican",
    "1858",
    "Pittsfield",
    "Resigned when appointed to the Massachusetts Superior Court"
  ],
  [
    "Charles Hale",
    "Republican",
    "1859",
    "Boston",
    "[Data unknown/missing.]"
  ],
  [
    "John A. Goodwin",
    "Republican",
    "1860–1861",
    "Lowell",
    "[Data unknown/missing.]"
  ],
  [
    "Alexander Hamilton Bullock",
    "Republican",
    "1862–1865",
    "Worcester",
    "Elected Governor of Massachusetts"
  ],
  [
    "James M. Stone",
    "Republican",
    "1866–1867",
    "Charlestown",
    "[Data unknown/missing.]"
  ],
  [
    "Harvey Jewell",
    "Republican",
    "1868–1871",
    "Boston",
    "[Data unknown/missing.]"
  ],
  [
    "John E. Sanford",
    "Republican",
    "1872–1875",
    "Taunton",
    "[Data unknown/missing.]"
  ],
  [
    "John Davis Long",
    "Republican",
    "1876–1878",
    "Hingham",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "Levi C. Wade",
    "Republican",
    "1879",
    "Newton",
    "[Data unknown/missing.]"
  ],
  [
    "Charles J. Noyes",
    "Republican",
    "1880–1882",
    "Boston (14th Suffolk)",
    "[Data unknown/missing.]"
  ],
  [
    "George Augustus Marden",
    "Republican",
    "1883–1884",
    "Lowell",
    "[Data unknown/missing.]"
  ],
  [
    "John Q. A. Brackett",
    "Republican",
    "January 7, 1885 – 1886",
    "Boston (17th Suffolk)",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "Charles J. Noyes",
    "Republican",
    "1887–1888",
    "Boston (14th Suffolk)",
    "[Data unknown/missing.]"
  ],
  [
    "William Emerson Barrett",
    "Republican",
    "1889–1893",
    "Melrose (11th Middlesex)",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "George von Lengerke Meyer",
    "Republican",
    "1894–1896",
    "Boston (9th Suffolk)",
    "[Data unknown/missing.]"
  ],
  [
    "John Lewis Bates",
    "Republican",
    "1897–1899",
    "Boston (1st Suffolk)",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "James J. Myers",
    "Republican",
    "1900–1903",
    "Cambridge (1st Middlesex)",
    "Retired"
  ],
  [
    "Louis A. Frothingham",
    "Republican",
    "1904–1905",
    "Boston (11th Suffolk)",
    "Left House to run for governor"
  ],
  [
    "John N. Cole",
    "Republican",
    "1906–1908",
    "Andover (8th Essex)",
    "Left House to run for Lieutenant Governor"
  ],
  [
    "Joseph H. Walker",
    "Republican",
    "1909–1911",
    "Brookline (2nd Norfolk)",
    "Left House to run for governor"
  ],
  [
    "Grafton D. Cushing",
    "Republican",
    "1912–1914",
    "Boston (11th Suffolk)",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "Channing H. Cox",
    "Republican",
    "1915–1918",
    "Boston (10th Suffolk)",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "Joseph E. Warner",
    "Republican",
    "1919–1920",
    "Taunton (4th Bristol)",
    "Lost primary for Lieutenant Governor of Massachusetts to Alvan Fuller"
  ],
  [
    "Benjamin Loring Young",
    "Republican",
    "1921–1924",
    "Weston (13th Middlesex)",
    "[Data unknown/missing.]"
  ],
  [
    "John C. Hull",
    "Republican",
    "1925–1929",
    "Leominster (11th Worcester)",
    "Retired"
  ],
  [
    "Leverett Saltonstall",
    "Republican",
    "1929–1936",
    "Chestnut Hill (5th Middlesex)",
    "Defeated for election as Lieutenant Governor by Francis E. Kelly"
  ],
  [
    "Horace T. Cahill",
    "Republican",
    "1937–1938",
    "Braintree (6th Norfolk)",
    "Elected Lieutenant Governor of Massachusetts"
  ],
  [
    "Christian Herter",
    "Republican",
    "1939–1942",
    "Boston (5th Suffolk)",
    "Elected to the U.S. House of Representatives"
  ],
  [
    "Rudolph King",
    "Republican",
    "1943–1944",
    "Millis (8th Norfolk)",
    "Resigned to run become Registrar of Motor Vehicles"
  ],
  [
    "Frederick Willis",
    "Republican",
    "1945–1948",
    "Saugus (10th Essex)",
    "Party lost majority"
  ],
  [
    "Thomas P. O'Neill",
    "Democratic",
    "1949–1952",
    "Cambridge (3rd Middlesex)",
    "Party lost majority; O'Neill elected to U.S. House of Representatives"
  ],
  [
    "Charles Gibbons",
    "Republican",
    "1953–1954",
    "Stoneham (22nd Middlesex)",
    "Party lost majority"
  ],
  [
    "Michael F. Skerry",
    "Democratic",
    "1955–1957",
    "Medford (27th Middlesex)",
    "Resigned when appointed Clerk of the Malden District Court"
  ],
  [
    "John F. Thompson",
    "Democratic",
    "1958–1964",
    "Ludlow (2nd Hampden)",
    "Resigned after being indicted on charges of conspiracy and bribery"
  ],
  [
    "John Davoren",
    "Democratic",
    "1965–1967",
    "Milford (9th Worcester)",
    "Resigned when appointed Secretary of the Commonwealth"
  ],
  [
    "Robert H. Quinn",
    "Democratic",
    "1967–1969",
    "Boston (9th Suffolk)",
    "Elected Massachusetts Attorney General"
  ],
  [
    "David M. Bartley",
    "Democratic",
    "1969–1975",
    "Holyoke (7th Hampden)",
    "Resigned to become President of Holyoke Community College"
  ],
  [
    "Thomas W. McGee",
    "Democratic",
    "1975–1984",
    "Lynn (20th Essex)",
    "Defeated by Keverian in leadership challenge"
  ],
  [
    "George Keverian",
    "Democratic",
    "1985–1990",
    "Everett (39th Middlesex)",
    "Retired to run for State Treasurer"
  ],
  [
    "Charles Flaherty",
    "Democratic",
    "1991 – April 9, 1996",
    "Cambridge (27th Middlesex)",
    "Resigned: pleaded guilty to tax evasion"
  ],
  [
    "Thomas Finneran",
    "Democratic",
    "April 9, 1996 – September 28, 2004",
    "Mattapan (12th Suffolk)",
    "Resigned due to allegations of perjury and obstruction of justice"
  ],
  [
    "Salvatore DiMasi",
    "Democratic",
    "September 28, 2004 – January 27, 2009",
    "Boston (3rd Suffolk)",
    "Resigned: convicted of conspiracy, honest services fraud, and extortion"
  ],
  [
    "Robert DeLeo",
    "Democratic",
    "January 27, 2009 – present",
    "Winthrop (19th Suffolk)",
    "Current Speaker"
  ]
]
```

## Prepared-example metadata

```json
{
  "overlap_subset": "True",
  "table_page_title": "List of Speakers of the Massachusetts House of Representatives",
  "table_section_title": "House of Representatives under the Massachusetts Constitution",
  "normalizer": "totto",
  "requested_split": "validation",
  "hub_id": "GEM/totto",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
George Keverian from Democratic Party served as the Speaker of the Massachusetts House of Representatives from 1985.
```

### Reference 2

```text
George Keverian was a Democratic party politician who served as the speaker of the Massachusetts House of Representatives beginning in 1985.
```

### Reference 3

```text
George Keverian of the Democratic Party served as the Speaker of the Massachusetts House of Representatives in 1985.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-244__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 7.889 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 17 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
George Keverian, a Democrat, served as Speaker of the Massachusetts House of Representatives from 1985 to 1990.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-244__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 10.205 |
| Prompt tokens | 2517 |
| Completion tokens | 688 |
| Total tokens | 3205 |
| Output words | 220 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The strongest supported findings from the data are:

- The table lists Speakers of the Massachusetts House of Representatives from 1780 to the present, with early speakers having no party affiliation and later speakers representing parties including Pro-Administration, Democratic-Republican, Federalist, National Republican, Whig, Know Nothing, Free Soil/Democratic coalition, Republican, and Democratic.
- From 1858 through 1948, every listed Speaker was a Republican.
- From 1958 onward, every listed Speaker is a Democrat.
- Boston is the most frequently listed city or town for Speakers, appearing many times across different eras.
- Many Speakers left office to be elected or appointed to higher positions, including the U.S. House of Representatives, Lieutenant Governor of Massachusetts, Governor of Massachusetts, U.S. Senate-related appointments? No—source mentions "Elected to the U.S. House," "Elected Lieutenant Governor," "Elected Governor," and appointments like "Associate Justice of the Supreme Court."
- Several recent Speakers resigned due to legal or ethical issues, including Charles Flaherty (pleaded guilty to tax evasion), Thomas Finneran (resigned due to allegations of perjury and obstruction of justice), and Salvatore DiMasi (convicted of conspiracy, honest services fraud, and extortion).
- Some Speakers served multiple non-consecutive terms, including Nathaniel Gorham, Timothy Bigelow, Perez Morton, William C. Jarvis, Thomas H. Kinnicutt, Julius Rockwell, and Charles J. Noyes.
- For many Speakers, electoral history data is unknown or missing in the source table.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-244__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.755 |
| Prompt tokens | 2545 |
| Completion tokens | 147 |
| Total tokens | 2692 |
| Output words | 23 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The highlighted cells show George Keverian, a Democrat, served from 1985–1990, represented Everett (39th Middlesex), and retired to run for State Treasurer.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.482457299 | 0.754673089 | 0.428571429 | 0.823529412 | 0.640495868 | 0.96543926 | 0.152571753 | 0.011460356 | 0.011460356 | 1 |
| Raw-generic direct Flash | 0.025473172 | 0.191918827 | 11.410714286 | 0.082987552 | 0.168831169 | 0.790536344 | 0.455479771 | 0.614993441 | 0.016762793 | 0.25 |
| Task-aware direct Flash | 0.033868193 | 0.329890842 | 1.125 | 0.3 | 0.142857143 | 0.879420817 | 0.05897544 | 0.78661567 | 0.78661567 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **2**
- Errors:
  1. **TASK/FORMAT** — “The entire multi-bullet response”
     - The requested output mode is one sentence, but the response contains multiple bullet points and sentences.
  2. **OMISSION** — “No statement about the highlighted George Keverian row”
     - The response omits the highlighted finding: Democrat George Keverian represented Everett (39th Middlesex), served as Speaker from 1985 to 1990, and retired to run for State Treasurer.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **TASK/FORMAT** — “represented Everett (39th Middlesex), and retired to run for State Treasurer.”
     - The city/district and electoral-history details come from unhighlighted cells. The request required exactly one sentence about the highlighted cells and explicitly excluded unrelated cells.

---

# Case 19: `totto` / `totto-validation-260`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | totto |
| Example ID | totto-validation-260 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source characters | 1106 |
| Reference count | 2 |
| Source SHA-256 | 5175d00543d25fd909b2dbcdc620b7151760b060140444203865c8019147f2a0 |
| Reference SHA-256 | f97c32cd89553fe11da1fe18330d078aa125218fc16d32f5f94e19ab693aae43 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Page: Corporate tax
Section: International corporate tax rates
Table:
Country | Corporate income tax rate (2016) | Combined corporate tax rate (2016)
Australia | 30.00% | 30.00%
Austria | 25.00% | 25.00%
Belgium | 33.00% | 33.99%
Canada | 15.00% | 26.80%
Chile | 24.00% | 24.00%
Czech Republic | 19.00% | 19.00%
Denmark | 22.00% | 22.00%
Estonia | 20.00% | 20.00%
Finland | 20.00% | 20.00%
*France* | *34.43%* | 34.43%
Germany | 15.83% | 30.18%
Greece | 29.00% | 29.00%
Hungary | 19.00% | 19.00%
Iceland | 20.00% | 20.00%
Ireland | 12.50% | 12.50%
Israel | 25.00% | 25.00%
Italy | 24.00% | 31.29%
Japan | 23.40% | 29.97%
South Korea | 22.00% | 24.20%
Luxembourg | 22.47% | 29.22%
Mexico | 30.00% | 30.00%
Netherlands | 25.00% | 25.00%
New Zealand | 28.00% | 28.00%
Norway | 25.00% | 25.00%
Poland | 19.00% | 19.00%
Portugal | 21.00% | 22.50%
Slovakia | 22.00% | 22.00%
Slovenia | 17.00% | 17.00%
Spain | 25.00% | 25.00%
Sweden | 22.00% | 22.00%
*Switzerland* | *8.50%* | 21.15%
Turkey | 20.00% | 20.00%
United Kingdom | 19.00% | 19.00%
United States | 35.00% | 38.92%
Cells surrounded by * are highlighted.
```

## Structured source payload

```json
{
  "table_page_title": "Corporate tax",
  "table_section_title": "International corporate tax rates",
  "table_section_text": "",
  "table": [
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Country"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Corporate income tax rate (2016)"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Combined corporate tax rate (2016)"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Australia"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "30.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "30.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Austria"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Belgium"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "33.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "33.99%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Canada"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "15.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "26.80%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Chile"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "24.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "24.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Czech Republic"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Denmark"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Estonia"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Finland"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "France"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "34.43%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "34.43%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Germany"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "15.83%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "30.18%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Greece"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "29.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "29.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Hungary"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Iceland"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Ireland"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "12.50%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "12.50%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Israel"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Italy"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "24.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "31.29%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Japan"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "23.40%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "29.97%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "South Korea"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "24.20%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Luxembourg"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.47%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "29.22%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Mexico"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "30.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "30.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Netherlands"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "New Zealand"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "28.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "28.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Norway"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Poland"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Portugal"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "21.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.50%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Slovakia"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Slovenia"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "17.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "17.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Spain"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "25.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Sweden"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "22.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Switzerland"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "8.50%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "21.15%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Turkey"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "20.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "United Kingdom"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "19.00%"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "United States"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "35.00%"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "38.92%"
      }
    ]
  ],
  "highlighted_cells": [
    [
      10,
      0
    ],
    [
      10,
      1
    ],
    [
      31,
      0
    ],
    [
      31,
      1
    ]
  ]
}
```

## Parent table representation

```json
[
  [
    "Country",
    "Corporate income tax rate (2016)",
    "Combined corporate tax rate (2016)"
  ],
  [
    "Australia",
    "30.00%",
    "30.00%"
  ],
  [
    "Austria",
    "25.00%",
    "25.00%"
  ],
  [
    "Belgium",
    "33.00%",
    "33.99%"
  ],
  [
    "Canada",
    "15.00%",
    "26.80%"
  ],
  [
    "Chile",
    "24.00%",
    "24.00%"
  ],
  [
    "Czech Republic",
    "19.00%",
    "19.00%"
  ],
  [
    "Denmark",
    "22.00%",
    "22.00%"
  ],
  [
    "Estonia",
    "20.00%",
    "20.00%"
  ],
  [
    "Finland",
    "20.00%",
    "20.00%"
  ],
  [
    "France",
    "34.43%",
    "34.43%"
  ],
  [
    "Germany",
    "15.83%",
    "30.18%"
  ],
  [
    "Greece",
    "29.00%",
    "29.00%"
  ],
  [
    "Hungary",
    "19.00%",
    "19.00%"
  ],
  [
    "Iceland",
    "20.00%",
    "20.00%"
  ],
  [
    "Ireland",
    "12.50%",
    "12.50%"
  ],
  [
    "Israel",
    "25.00%",
    "25.00%"
  ],
  [
    "Italy",
    "24.00%",
    "31.29%"
  ],
  [
    "Japan",
    "23.40%",
    "29.97%"
  ],
  [
    "South Korea",
    "22.00%",
    "24.20%"
  ],
  [
    "Luxembourg",
    "22.47%",
    "29.22%"
  ],
  [
    "Mexico",
    "30.00%",
    "30.00%"
  ],
  [
    "Netherlands",
    "25.00%",
    "25.00%"
  ],
  [
    "New Zealand",
    "28.00%",
    "28.00%"
  ],
  [
    "Norway",
    "25.00%",
    "25.00%"
  ],
  [
    "Poland",
    "19.00%",
    "19.00%"
  ],
  [
    "Portugal",
    "21.00%",
    "22.50%"
  ],
  [
    "Slovakia",
    "22.00%",
    "22.00%"
  ],
  [
    "Slovenia",
    "17.00%",
    "17.00%"
  ],
  [
    "Spain",
    "25.00%",
    "25.00%"
  ],
  [
    "Sweden",
    "22.00%",
    "22.00%"
  ],
  [
    "Switzerland",
    "8.50%",
    "21.15%"
  ],
  [
    "Turkey",
    "20.00%",
    "20.00%"
  ],
  [
    "United Kingdom",
    "19.00%",
    "19.00%"
  ],
  [
    "United States",
    "35.00%",
    "38.92%"
  ]
]
```

## Prepared-example metadata

```json
{
  "overlap_subset": "False",
  "table_page_title": "Corporate tax",
  "table_section_title": "International corporate tax rates",
  "normalizer": "totto",
  "requested_split": "validation",
  "hub_id": "GEM/totto",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The low tax was 8.5% in Switzerland and a high of 34.43% in France.
```

### Reference 2

```text
The Corporate tax was 34.43% in France.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-260__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 10.694 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 25 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Among the highlighted countries, Switzerland had the lower corporate income tax rate (2016) at 8.50%, while France had the higher value at 34.43%.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-260__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 6.134 |
| Prompt tokens | 698 |
| Completion tokens | 535 |
| Total tokens | 1233 |
| Output words | 153 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The strongest supported findings are:

- The United States had the highest basic corporate income tax rate (35.00%) and the highest combined corporate tax rate (38.92%) among the listed countries.
- Ireland had the lowest combined corporate tax rate (12.50%) and one of the lowest basic rates (12.50%).
- Switzerland had the lowest basic corporate income tax rate (8.50%), but its combined rate was 21.15%, reflecting additional taxes beyond the federal rate.
- Several countries’ combined rates were higher than their basic rates, including Belgium (33.00% vs. 33.99%), Canada (15.00% vs. 26.80%), Germany (15.83% vs. 30.18%), Italy (24.00% vs. 31.29%), Japan (23.40% vs. 29.97%), South Korea (22.00% vs. 24.20%), Luxembourg (22.47% vs. 29.22%), Portugal (21.00% vs. 22.50%), and Switzerland (8.50% vs. 21.15%).
- France and Switzerland were the only highlighted entries in the table.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-260__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 2.884 |
| Prompt tokens | 726 |
| Completion tokens | 298 |
| Total tokens | 1024 |
| Output words | 21 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The highlighted cells show France's corporate income tax rate of 34.43% and Switzerland's corporate income tax rate of 8.50%.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.033961882 | 0.299911554 | 1.904761905 | 0.303030303 | 0.174418605 | 0.902592659 | 0.326796055 | 0.46781373 | 0.46781373 | 1 |
| Raw-generic direct Flash | 0.003058843 | 0.12546791 | 12.19047619 | 0.071005917 | 0.173076923 | 0.818047404 | 0.141087607 | 0.554092105 | 0.116373576 | 0.4 |
| Task-aware direct Flash | 0.082161073 | 0.376223967 | 1.428571429 | 0.322580645 | 0.243902439 | 0.925865531 | 0.369144142 | 0.801890612 | 0.801890612 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **3**
- Errors:
  1. **CONTEXT** — “reflecting additional taxes beyond the federal rate”
     - The table only shows that Switzerland’s combined rate exceeds its corporate income tax rate; it does not identify the 8.50% figure as a federal rate or explain the difference as additional taxes.
  2. **OMISSION** — “France and Switzerland were the only highlighted entries in the table.”
     - The output does not report France’s highlighted corporate income tax rate of 34.43%, an important highlighted finding.
  3. **TASK/FORMAT** — “The strongest supported findings are: - The United States ... - France and Switzerland were the only highlighted entries in the table.”
     - The requested output mode was one sentence, but the response contains multiple separately punctuated bullet-style sentences.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 20: `totto` / `totto-validation-712`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | totto |
| Example ID | totto-validation-712 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source characters | 1304 |
| Reference count | 3 |
| Source SHA-256 | 1a790c9eab97b067f1e4d6745e58ff2f3fe0ad2746f310a09d67bf93f3448d43 |
| Reference SHA-256 | e47b5b35646c8d4dbb5033654269c43f8104984e6614b6bf847a83dd98df403d |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Page: House of Blues Tour (Mýa 2003 Tour)
Section: Tour dates
Table:
Date | City | Country | Venue
North America
October 11, 2003 | Fresno | United States | Paul Paul Theatre
October 12, 2003 | San Diego | 4th & B
October 13, 2003 | Perris | Coors Arena
October 14, 2003 | Tempe | Marquee Theatre
October 16, 2003 | Dallas | Gypsy Tea Room
October 17, 2003 | Austin | La Zona Rosa
October 18, 2003 | Houston | Health and Physical Education Arena
October 19, 2003 | New Orleans | House of Blues
October 21, 2003 | Atlanta | Variety Playhouse
October 22, 2003 | Lake Buena Vista | House of Blues
October 23, 2003 | North Myrtle Beach
*October 24, 2003* | *Washington, D.C.* | *Dream*
October 25, 2003 | Columbia | Mays Arena
October 26, 2003 | Atlantic City | Borgata Event Center
October 27, 2003 | New York City | B.B. King Blues Club
October 28, 2003 | Boston | Wilbur Theatre
October 29, 2003 | Ledyard | B.B. King Nite Club
October 31, 2003 | Pittsburgh | Club Laga
November 1, 2003 | Chicago | House of Blues
November 2, 2003 | St. Louis | The Pageant
November 3, 2003 | Minneapolis | First Avenue
November 6, 2003 | Seattle | Showbox Comedy and Supper Club
November 9, 2003 | San Francisco | Bimbo's 365 Club
November 10, 2003 | West Hollywood | House of Blues
Cells surrounded by * are highlighted.
```

## Structured source payload

```json
{
  "table_page_title": "House of Blues Tour (Mýa 2003 Tour)",
  "table_section_title": "Tour dates",
  "table_section_text": "Festivals and other miscellaneous performances This concert was a part of \"The Big Fresno Fair\" This concert was a part of the \"Southern California Fair\" This concert was a part of the \"TSU Homecoming Concert\"",
  "table": [
    [
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Date"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "City"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Country"
      },
      {
        "column_span": 1,
        "is_header": true,
        "row_span": 1,
        "value": "Venue"
      }
    ],
    [
      {
        "column_span": 4,
        "is_header": true,
        "row_span": 1,
        "value": "North America"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 11, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Fresno"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 24,
        "value": "United States"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Paul Paul Theatre"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 12, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "San Diego"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "4th & B"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 13, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Perris"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Coors Arena"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 14, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Tempe"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Marquee Theatre"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 16, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Dallas"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Gypsy Tea Room"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 17, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Austin"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "La Zona Rosa"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 18, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Houston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Health and Physical Education Arena"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 19, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "New Orleans"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "House of Blues"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 21, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Atlanta"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Variety Playhouse"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 22, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Lake Buena Vista"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 2,
        "value": "House of Blues"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 23, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "North Myrtle Beach"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 24, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Washington, D.C."
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Dream"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 25, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Columbia"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Mays Arena"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 26, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Atlantic City"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Borgata Event Center"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 27, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "New York City"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "B.B. King Blues Club"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 28, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Boston"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Wilbur Theatre"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 29, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Ledyard"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "B.B. King Nite Club"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "October 31, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Pittsburgh"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Club Laga"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "November 1, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Chicago"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "House of Blues"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "November 2, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "St. Louis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "The Pageant"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "November 3, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Minneapolis"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "First Avenue"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "November 6, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Seattle"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Showbox Comedy and Supper Club"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "November 9, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "San Francisco"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "Bimbo's 365 Club"
      }
    ],
    [
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "November 10, 2003"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "West Hollywood"
      },
      {
        "column_span": 1,
        "is_header": false,
        "row_span": 1,
        "value": "House of Blues"
      }
    ]
  ],
  "highlighted_cells": [
    [
      13,
      0
    ],
    [
      13,
      1
    ],
    [
      13,
      2
    ]
  ]
}
```

## Parent table representation

```json
[
  [
    "Date",
    "City",
    "Country",
    "Venue"
  ],
  [
    "North America"
  ],
  [
    "October 11, 2003",
    "Fresno",
    "United States",
    "Paul Paul Theatre"
  ],
  [
    "October 12, 2003",
    "San Diego",
    "4th & B"
  ],
  [
    "October 13, 2003",
    "Perris",
    "Coors Arena"
  ],
  [
    "October 14, 2003",
    "Tempe",
    "Marquee Theatre"
  ],
  [
    "October 16, 2003",
    "Dallas",
    "Gypsy Tea Room"
  ],
  [
    "October 17, 2003",
    "Austin",
    "La Zona Rosa"
  ],
  [
    "October 18, 2003",
    "Houston",
    "Health and Physical Education Arena"
  ],
  [
    "October 19, 2003",
    "New Orleans",
    "House of Blues"
  ],
  [
    "October 21, 2003",
    "Atlanta",
    "Variety Playhouse"
  ],
  [
    "October 22, 2003",
    "Lake Buena Vista",
    "House of Blues"
  ],
  [
    "October 23, 2003",
    "North Myrtle Beach"
  ],
  [
    "October 24, 2003",
    "Washington, D.C.",
    "Dream"
  ],
  [
    "October 25, 2003",
    "Columbia",
    "Mays Arena"
  ],
  [
    "October 26, 2003",
    "Atlantic City",
    "Borgata Event Center"
  ],
  [
    "October 27, 2003",
    "New York City",
    "B.B. King Blues Club"
  ],
  [
    "October 28, 2003",
    "Boston",
    "Wilbur Theatre"
  ],
  [
    "October 29, 2003",
    "Ledyard",
    "B.B. King Nite Club"
  ],
  [
    "October 31, 2003",
    "Pittsburgh",
    "Club Laga"
  ],
  [
    "November 1, 2003",
    "Chicago",
    "House of Blues"
  ],
  [
    "November 2, 2003",
    "St. Louis",
    "The Pageant"
  ],
  [
    "November 3, 2003",
    "Minneapolis",
    "First Avenue"
  ],
  [
    "November 6, 2003",
    "Seattle",
    "Showbox Comedy and Supper Club"
  ],
  [
    "November 9, 2003",
    "San Francisco",
    "Bimbo's 365 Club"
  ],
  [
    "November 10, 2003",
    "West Hollywood",
    "House of Blues"
  ]
]
```

## Prepared-example metadata

```json
{
  "overlap_subset": "True",
  "table_page_title": "House of Blues Tour (Mýa 2003 Tour)",
  "table_section_title": "Tour dates",
  "normalizer": "totto",
  "requested_split": "validation",
  "hub_id": "GEM/totto",
  "config_name": null
}
```

## Held-out human references

### Reference 1

```text
The House of Blues Tour (Mýa 2003 Tour) was held on October 24, 2003, at Dream in Washington, D.C.
```

### Reference 2

```text
The House of Blues concert was held on October 24, 2003, at Dream in Washington, D.C..
```

### Reference 3

```text
The House of Blues Tour was held on October 24, 2003, at Dream in Washington, D.C..
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-712__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 18.291 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 22 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
On October 24, 2003, the House of Blues Tour (Mýa 2003 Tour) date was in Washington, D.C., at the venue Dream.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-712__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 3.271 |
| Prompt tokens | 604 |
| Completion tokens | 215 |
| Total tokens | 819 |
| Output words | 53 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The tour had North American dates from October 11 to November 10, 2003, with venues primarily in the United States. Multiple shows were held at House of Blues venues (New Orleans, Lake Buena Vista, Chicago, and West Hollywood). One date—October 24, 2003, in Washington, D.C., at the venue Dream—is highlighted.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `totto__totto-validation-712__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 2.134 |
| Prompt tokens | 632 |
| Completion tokens | 165 |
| Total tokens | 797 |
| Output words | 17 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The highlighted cells list the October 24, 2003 concert in Washington, D.C. at the venue Dream.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.580071842 | 0.757271615 | 0.470588235 | 0.636363636 | 0.811360677 | 0.961320221 | 0.754572511 | 0.909440994 | 0.909440994 | 0 |
| Raw-generic direct Flash | 0.15478824 | 0.431987291 | 2.470588235 | 0.314285714 | 0.526918671 | 0.888978601 | 0.596989572 | 0.641619265 | 0.322861075 | 0.333333333 |
| Task-aware direct Flash | 0.39333318 | 0.500009815 | 0.764705882 | 0.470588235 | 0.375584893 | 0.924288154 | 0.225449964 | 0.81192708 | 0.81192708 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **TASK/FORMAT** — “The generated output consists of three sentences.”
     - The requested output mode is one sentence, so the findings should be combined into a single sentence.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 21: `web_nlg` / `web_nlg_en-test-178`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | web_nlg |
| Example ID | web_nlg_en-test-178 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 134 |
| Reference count | 3 |
| Source SHA-256 | 9ae2ac7aed16676c5d94862900d67fac368c8d3d42dcb287970b8be3ffd1d376 |
| Reference SHA-256 | 7c668b36270a56b6028a0350ebae45135c68142861fe4687c9a3d5572cb5573d |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Bootleg_Series_Volume_1:_The_Quine_Tapes | artist | The_Velvet_Underground
Bootleg_Series_Volume_1:_The_Quine_Tapes | runtime | 230.05
```

## Structured source payload

```json
{
  "triples": [
    "Bootleg_Series_Volume_1:_The_Quine_Tapes | artist | The_Velvet_Underground",
    "Bootleg_Series_Volume_1:_The_Quine_Tapes | runtime | 230.05"
  ],
  "category": "MusicalWork"
}
```

## Prepared-example metadata

```json
{
  "category": "MusicalWork",
  "normalizer": "webnlg",
  "requested_split": "test",
  "hub_id": "GEM/web_nlg",
  "config_name": "en"
}
```

## Held-out human references

### Reference 1

```text
Bootleg Series Volume I: The Quine Tapes was created by The Velvet Underground and is 230.05 minutes long.
```

### Reference 2

```text
Music group the Velvet Underground released album Bootleg Series Volume 1: The Quine Tapes, which have a runtime of 230.05 minutes.
```

### Reference 3

```text
Bootleg Series Volume 1: The Quine Tapes by The Velvet Underground, has a run time of 230:05.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-178__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 17.464 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 19 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Bootleg Series Volume 1: The Quine Tapes is by The Velvet Underground and has a runtime of 230.05.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-178__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.945 |
| Prompt tokens | 232 |
| Completion tokens | 122 |
| Total tokens | 354 |
| Output words | 26 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The strongest supported findings are that *Bootleg Series Volume 1: The Quine Tapes* is by The Velvet Underground and has a runtime of 230.05 (minutes).
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-178__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 2.385 |
| Prompt tokens | 260 |
| Completion tokens | 196 |
| Total tokens | 456 |
| Output words | 19 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Bootleg Series Volume 1: The Quine Tapes is by The Velvet Underground and has a runtime of 230.05.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.690279103 | 0.832115302 | 0.321428571 | 0.864864865 | 0.749160871 | 0.966833949 | 0.966809332 | 0.809057534 | 0.809057534 | 0 |
| Raw-generic direct Flash | 0.469596684 | 0.748283983 | 0.696428571 | 0.727272727 | 0.719699488 | 0.933103383 | 0.013481415 | 0.614380896 | 0.614380896 | 0 |
| Task-aware direct Flash | 0.690279103 | 0.832115302 | 0.321428571 | 0.864864865 | 0.749160871 | 0.966833949 | 0.966809332 | 0.809057534 | 0.809057534 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **1**
- Errors:
  1. **NUMBER** — “(minutes)”
     - The source gives the runtime as 230.05 but does not specify a unit, so interpreting it as minutes is unsupported.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 22: `web_nlg` / `web_nlg_en-test-51`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | web_nlg |
| Example ID | web_nlg_en-test-51 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 113 |
| Reference count | 3 |
| Source SHA-256 | 7a9c7d26db8b78333812ec0c07315f74ec94151e57b5fee5c719fd734af16494 |
| Reference SHA-256 | 9f63bc7d6e86f9827bc742967db7a371e4397e26c76480222cdfcf53a94815b2 |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
ALCO_RS-3 | engine | Four-stroke_engine
ALCO_RS-3 | cylinderCount | 12
ALCO_RS-3 | length | 17068.8 (millimetres)
```

## Structured source payload

```json
{
  "triples": [
    "ALCO_RS-3 | engine | Four-stroke_engine",
    "ALCO_RS-3 | cylinderCount | 12",
    "ALCO_RS-3 | length | 17068.8 (millimetres)"
  ],
  "category": "MeanOfTransportation"
}
```

## Prepared-example metadata

```json
{
  "category": "MeanOfTransportation",
  "normalizer": "webnlg",
  "requested_split": "test",
  "hub_id": "GEM/web_nlg",
  "config_name": "en"
}
```

## Held-out human references

### Reference 1

```text
The ALCO RS-3, with a four-stroke engine and 12 cylinders, has a length of 17068.8 millimetres.
```

### Reference 2

```text
The four-stroke 12 cylinder ALCO RS-3 is 17068.8 millimetres long.
```

### Reference 3

```text
The ALCO RS-3 has a four-stroke engine and a cylinder count of 12 which is 17068.8 mm in length.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-51__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 10.937 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 16 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
The ALCO RS-3 has a four-stroke engine, 12 cylinders, and a length of 17068.8 millimetres.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-51__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.503 |
| Prompt tokens | 229 |
| Completion tokens | 80 |
| Total tokens | 309 |
| Output words | 17 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The ALCO_RS-3 is equipped with a four-stroke engine, has 12 cylinders, and is 17068.8 millimetres long.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-51__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.723 |
| Prompt tokens | 257 |
| Completion tokens | 139 |
| Total tokens | 396 |
| Output words | 15 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The ALCO_RS-3 has a four-stroke engine, 12 cylinders, and a length of 17068.8 millimetres.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.662237862 | 0.805209817 | 0.333333333 | 0.864864865 | 0.777418034 | 0.985750318 | 0.950594425 | 0.720226645 | 0.720226645 | 0 |
| Raw-generic direct Flash | 0.405613793 | 0.665860405 | 0.666666667 | 0.717948718 | 0.598767809 | 0.963478208 | 0.983758807 | 0.742143214 | 0.742143214 | 0 |
| Task-aware direct Flash | 0.563209809 | 0.755281328 | 0.4 | 0.864864865 | 0.712025316 | 0.97792232 | 0.959383786 | 0.699708045 | 0.699708045 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 23: `web_nlg` / `web_nlg_en-test-54`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | web_nlg |
| Example ID | web_nlg_en-test-54 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 293 |
| Reference count | 3 |
| Source SHA-256 | dfa48a38c481e06a3aad7732dd24c495fdbfea00df3e7bb86eb319aa95c90330 |
| Reference SHA-256 | 82026296d92ebba9cfc40c569289af8e8c33db34115c56ed87adfbf3389af8eb |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Mermaid_(Train_song) | recordLabel | Sony_Music_Entertainment
Mermaid_(Train_song) | writer | Amund_Bjørklund
Mermaid_(Train_song) | writer | Stargate_(production_team)
Mermaid_(Train_song) | followedBy | Imagine_(John_Lennon_song)
Mermaid_(Train_song) | producer | Espionage_(production_team)
```

## Structured source payload

```json
{
  "triples": [
    "Mermaid_(Train_song) | recordLabel | Sony_Music_Entertainment",
    "Mermaid_(Train_song) | writer | Amund_Bjørklund",
    "Mermaid_(Train_song) | writer | Stargate_(production_team)",
    "Mermaid_(Train_song) | followedBy | Imagine_(John_Lennon_song)",
    "Mermaid_(Train_song) | producer | Espionage_(production_team)"
  ],
  "category": "MusicalWork"
}
```

## Prepared-example metadata

```json
{
  "category": "MusicalWork",
  "normalizer": "webnlg",
  "requested_split": "test",
  "hub_id": "GEM/web_nlg",
  "config_name": "en"
}
```

## Held-out human references

### Reference 1

```text
Train's hit Mermaid was put out by the Sony Music Entertainment record label, was written by Amund Bjørklund with the producer Stargate. Train followed Mermaid with Imagine, a song by John Lennon where Mermaid was produced by the Espionage production team.
```

### Reference 2

```text
The song Mermaid, by Train, is a Sony Music Entertainment release produced by Stargate along with the production team Espionage. Mermaid, written by Amund Bjorklund, is followed by John Lennon's Imagine.
```

### Reference 3

```text
The Train song Mermaid written by Amund Bjørklund and production team Stargate was produced by the production team Espionage and released under the record label Sony Music Entertainment. It was followed by the release of Imagine by John Lennon performed by Train.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-54__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 17.330 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 35 |
| Writer mode | llm_writer |
| Release status | approved |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
The song Mermaid (Train song) has the record label Sony Music Entertainment, was written by Amund Bjørklund and Stargate (production team), was followed by Imagine (John Lennon song), and was produced by Espionage (production team).
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-54__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 2.367 |
| Prompt tokens | 273 |
| Completion tokens | 147 |
| Total tokens | 420 |
| Output words | 40 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The data supports that “Mermaid” (Train song) is associated with Sony Music Entertainment as its record label, was written by Amund Bjørklund and Stargate (production team), was produced by Espionage (production team), and is followed by “Imagine” (John Lennon song).
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-54__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 3.215 |
| Prompt tokens | 301 |
| Completion tokens | 273 |
| Total tokens | 574 |
| Output words | 27 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
"Mermaid" by Train was released on Sony Music Entertainment, written by Amund Bjørklund and Stargate, and produced by Espionage. It was followed by "Imagine" (John Lennon song).
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.348995679 | 0.629100822 | 0.657894737 | 0.556962025 | 0.458535109 | 0.930199146 | 0.986531675 | 0.497825861 | 0.497825861 | 1 |
| Raw-generic direct Flash | 0.276177344 | 0.572242784 | 0.763157895 | 0.523809524 | 0.448319071 | 0.905884206 | 0.969355643 | 0.404211015 | 0.404211015 | 1 |
| Task-aware direct Flash | 0.326441474 | 0.530147881 | 0.631578947 | 0.507042254 | 0.375294963 | 0.932182133 | 0.968267381 | 0.576865196 | 0.562794566 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 24: `web_nlg` / `web_nlg_en-test-61`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | web_nlg |
| Example ID | web_nlg_en-test-61 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 63 |
| Reference count | 3 |
| Source SHA-256 | df67683da7a1dd2d88170456d02c2d5daee07238efaa53a497349d5e45710114 |
| Reference SHA-256 | ebfa624e52c11b5d14af32f7ba4dc5238d7afc23bff614731199cc0f508134cc |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Ciudad_Ayala | utcOffset | −6
Ciudad_Ayala | isPartOf | Morelos
```

## Structured source payload

```json
{
  "triples": [
    "Ciudad_Ayala | utcOffset | −6",
    "Ciudad_Ayala | isPartOf | Morelos"
  ],
  "category": "City"
}
```

## Prepared-example metadata

```json
{
  "category": "City",
  "normalizer": "webnlg",
  "requested_split": "test",
  "hub_id": "GEM/web_nlg",
  "config_name": "en"
}
```

## Held-out human references

### Reference 1

```text
Morelos, in Ciudad Ayala, is in the UTC offset -6 timezone.
```

### Reference 2

```text
Ciudad Ayala, which has a UTC offset of -6, is part of Morelos.
```

### Reference 3

```text
The UTC offset of Ciudad Ayala which is part of Morelos is -6.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-61__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 11.339 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 13 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 1 |
| Support sentences | 1 |
| Generation error | — |

#### Exact generated text

```text
Ciudad Ayala has a UTC offset of −6 and is part of Morelos.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-61__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.616 |
| Prompt tokens | 208 |
| Completion tokens | 71 |
| Total tokens | 279 |
| Output words | 12 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Ciudad_Ayala is part of Morelos and has a UTC offset of −6.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-61__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.127 |
| Prompt tokens | 236 |
| Completion tokens | 53 |
| Total tokens | 289 |
| Output words | 13 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Ciudad Ayala has a UTC offset of −6 and is part of Morelos.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.573122448 | 0.716012579 | 0.324324324 | 0.923076923 | 0.758846154 | 0.981760323 | 0.989338815 | 0.60049969 | 0.60049969 | 0 |
| Raw-generic direct Flash | 0.442850014 | 0.629454082 | 0.486486486 | 0.615384615 | 0.581395349 | 0.974201977 | 0.987160087 | 0.490945905 | 0.490945905 | 1 |
| Task-aware direct Flash | 0.573122448 | 0.716012579 | 0.324324324 | 0.923076923 | 0.758846154 | 0.981760323 | 0.989338815 | 0.60049969 | 0.60049969 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Case 25: `web_nlg` / `web_nlg_en-test-65`

## Case metadata

| Field | Value |
|---|---|
| Dataset ID | web_nlg |
| Example ID | web_nlg_en-test-65 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source characters | 284 |
| Reference count | 3 |
| Source SHA-256 | aacce2dd3771e0f8e77b31f7cc25f27ccf63ae24d1e9d5f470bed95a710e5d93 |
| Reference SHA-256 | 1f26a4ecbe84c8e62f6cc49161af4f1549ff4e4536a05254bee19c6bf8adfc5d |

## Requests supplied by condition

### Full System and Task-aware Direct

```text
Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts.
```

### Raw Generic

```text
Understand the supplied data and report its strongest supported findings.
```

## Source text supplied to every condition

JSON source strings are pretty-printed below for readability; the parsed content is unchanged and its original SHA-256 is recorded above.

```text
Bootleg_Series_Volume_1:_The_Quine_Tapes | producer | The_Velvet_Underground
Bootleg_Series_Volume_1:_The_Quine_Tapes | recordedIn | United_States
Bootleg_Series_Volume_1:_The_Quine_Tapes | recordedIn | St._Louis,_Missouri
Bootleg_Series_Volume_1:_The_Quine_Tapes | genre | Rock_music
```

## Structured source payload

```json
{
  "triples": [
    "Bootleg_Series_Volume_1:_The_Quine_Tapes | producer | The_Velvet_Underground",
    "Bootleg_Series_Volume_1:_The_Quine_Tapes | recordedIn | United_States",
    "Bootleg_Series_Volume_1:_The_Quine_Tapes | recordedIn | St._Louis,_Missouri",
    "Bootleg_Series_Volume_1:_The_Quine_Tapes | genre | Rock_music"
  ],
  "category": "MusicalWork"
}
```

## Prepared-example metadata

```json
{
  "category": "MusicalWork",
  "normalizer": "webnlg",
  "requested_split": "test",
  "hub_id": "GEM/web_nlg",
  "config_name": "en"
}
```

## Held-out human references

### Reference 1

```text
The Quine Tapes was produced by The Velvet Underground in St. Louis, Missouri, United States; its genre is rock.
```

### Reference 2

```text
The rock album Bootleg Series Volume 1: The Quine Tapes was produced and recorded by the Velvet Underground in St. Louis, Missouri, USA.
```

### Reference 3

```text
The Velvet Underground recorded Rock album The Bootleg Series Volume I: The Quine Tapes in St. Louis, Missouri, USA.
```

## Generated outputs

### Full multi-agent system

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-65__full_system__r0__s42` |
| Model | auditor=deepseek:deepseek-v4-flash, data_understanding=deepseek:deepseek-v4-flash, evidence=deepseek:deepseek-v4-flash, orchestrator=deepseek:deepseek-v4-flash, verifier=deepseek:deepseek-v4-flash, writer=deepseek:deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.TABLE2TEXT |
| Prompt style | — |
| Elapsed seconds | 27.779 |
| Prompt tokens | — |
| Completion tokens | — |
| Total tokens | — |
| Output words | 30 |
| Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Primary evaluation eligible | True |
| Primary evaluation reason | — |
| Repair rounds | 0 |
| Audit support rate | 1 |
| Mapped support sentences | 2 |
| Support sentences | 2 |
| Generation error | — |

#### Exact generated text

```text
Bootleg Series Volume 1: The Quine Tapes was produced by The Velvet Underground, recorded in the United States and in St.
Louis, Missouri, and is in the rock music genre.
```

### Raw-generic direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-65__raw_generic_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | generic |
| Elapsed seconds | 1.777 |
| Prompt tokens | 280 |
| Completion tokens | 100 |
| Total tokens | 380 |
| Output words | 35 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
The strongest supported findings are that *Bootleg Series Volume 1: The Quine Tapes* is a rock music release produced by The Velvet Underground and was recorded in the United States, specifically in St. Louis, Missouri.
```

### Task-aware direct Flash

| Field | Value |
|---|---|
| Generation ID | `web_nlg__web_nlg_en-test-65__task_aware_direct_flash__r0__s42` |
| Model | deepseek-v4-flash |
| Seed | 42 |
| Backend | GenerationBackend.CALLABLE |
| Prompt style | structured |
| Elapsed seconds | 1.706 |
| Prompt tokens | 308 |
| Completion tokens | 120 |
| Total tokens | 428 |
| Output words | 28 |
| Writer mode | — |
| Release status | — |
| Primary evaluation eligible | — |
| Primary evaluation reason | — |
| Repair rounds | — |
| Audit support rate | — |
| Mapped support sentences | — |
| Support sentences | — |
| Generation error | — |

#### Exact generated text

```text
Bootleg Series Volume 1: The Quine Tapes is a rock music album produced by The Velvet Underground and recorded in the United States, specifically in St. Louis, Missouri.
```

## Per-output metrics

| Condition | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | AlignScore | HHEM mean support | HHEM minimum sentence support | HHEM unsupported-sentence rate |
|---|---|---|---|---|---|---|---|---|---|---|
| Full multi-agent system | 0.573564162 | 0.763653452 | 0.68852459 | 0.641509434 | 0.752742616 | 0.947633684 | 0.89135313 | 0.863154501 | 0.821526587 | 0 |
| Raw-generic direct Flash | 0.416966249 | 0.668029875 | 0.93442623 | 0.586206897 | 0.712964876 | 0.94346118 | 0.02021851 | 0.78570655 | 0.764562845 | 0 |
| Task-aware direct Flash | 0.512704049 | 0.734796607 | 0.639344262 | 0.62745098 | 0.759148936 | 0.955705285 | 0.262825042 | 0.765777946 | 0.724705637 | 0 |

Metric orientation: TER and HHEM unsupported-sentence rate are lower-is-better; every other column is higher-is-better.

## Structured judge annotations

### Full multi-agent system

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Raw-generic direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `openai_responses_api`
- API authenticated: `true`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

### Task-aware direct Flash

- Judge model: `gpt-5.6-sol`
- Execution mode: `interactive_session`
- API authenticated: `false`
- Status: `scored`
- Error count: **0**
- Errors: none recorded.

---

# Artifact provenance

The following SHA-256 hashes identify every persisted input used to build this dossier.

| Artifact | SHA-256 |
|---|---|
| evaluation/notebooks/build_interactive_gpt56_annotation_artifacts.py | ffcdc7cb94b2fa8289f215ddcd6716b96f922f8fa0cfeac8012bfb5b3cf136a4 |
| evaluation/notebooks/build_task_aware_complete_evaluation_dossier.py | 17505078b60a324b2620a1fa54dda6e541e58d82b951016c8ecb06372331a0e7 |
| evaluation/notebooks/task_aware_direct_baseline_evaluation.ipynb | e58ed6babaec7a30bd34d682e5a2aa72143d0b45895fb1580ad83bc3ddfc8053 |
| evaluation/notebooks/task_aware_direct_baseline_evaluation.py | a7605341fcfd3463b17f22bc8065efa7cab356040dcf5b1d3030294f9262d03e |
| evaluation/task_aware_direct_baseline/config/metrics_task_aware_direct_flash_25_reference.json | 993f52df90cd6402dcf564cc5ee33af8caa4f2817d59a1680b3e4c5a7e3df278 |
| evaluation/task_aware_direct_baseline/config/metrics_task_aware_direct_flash_25_source_grounded.json | 3940a57d4d4bf2e427a9dbaf07691e53a616d725b2be47c2c552043ad55363e2 |
| evaluation/task_aware_direct_baseline/config/variants_task_aware_direct_flash_25.json | 43bb29f21cfca34b5cb23418e17f876c00b148722149b869a2dc67e8bf96eba4 |
| evaluation/task_aware_direct_baseline/generations/task_aware_direct_flash_25_three_condition_generations.jsonl | 257c1882706bbf3a8973fece1fb2fa1b0d8e516bdb16f8cf557c926d83ba718f |
| evaluation/task_aware_direct_baseline/prepared/task_aware_direct_flash_25_examples.jsonl | e835ee853ad4cb0a8f34f3f84963b7859571ca2db7499ea62ceb4c69708a238b |
| evaluation/task_aware_direct_baseline/results/gpt56_all_75_annotations_with_provenance.jsonl | 3f681ae7f0711b62ef3b5854ea9a8e550dd6e277a8f2b8de629433b52379f4dc |
| evaluation/task_aware_direct_baseline/results/interactive_gpt56_annotation_provenance.json | 5056fd45f9f76d7d5198512ea1604abfa7e6aafd6347bd21db82bd41bce60d5a |
| evaluation/task_aware_direct_baseline/results/selected_five_three_condition_source_metrics.csv | 53e332f74a7aeb0e9d29cec89b5044c7781d258ece8db16f2a93bb0d56bb2e58 |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_direction_adjusted_wins.csv | 6d2bd3a137ba4c8f1c9c42d183ce50b355f5d360f3ab3dae30e5736388e6ee24 |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_manifest.json | 6deb1bea431cb69396637446a258d2d8aa8111438a125416da24bcd27399001a |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_progress.log | eddeb00471befe9cc301daf284f7c26c331fe71113a914a43babcffe2cd7eb8a |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_reference_by_dataset.csv | 2476c02f83f964bd01edd8ed5928b48617c1fd3249d7151d0ae6ccd5ea221eab |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_reference_macro.csv | 6f07a8594d45db410d005e24d1ae7495ca25101f2632f0b99c4281282b8dba0c |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_reference_metrics.jsonl | 6500471c7e1d9dda7cfb7fdf45917f6b78c5057573c672355918b203692be2f3 |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_source_by_dataset.csv | 525a9568f3106956015cc39934c1c6f993baeaa9640930b71bd2c6bd26d6640c |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_source_grounded_metrics.jsonl | bb02c524e6c3caa5cca5f99ac87377a71d6a46d8a4faf63f0c82d5c0d935af9f |
| evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_source_macro.csv | 29ad862f023727b90f097190f42ba5d56decfe6c69979bfbe5e1c8ac9ca223aa |

The complete raw metric JSONL files remain authoritative for metric implementation details such as sentence-level HHEM scores and durations. This document preserves every headline score while avoiding duplication of those low-level diagnostic payloads.
