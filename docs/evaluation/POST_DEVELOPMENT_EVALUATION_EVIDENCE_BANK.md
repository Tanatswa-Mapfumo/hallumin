# Evaluation of the Evidence-Led Multi-Agent Table-to-Text System

## 1. Evaluation purpose and scope

This chapter evaluates whether the proposed evidence-led, multi-agent Table2Text system produces more accurate, task-appropriate and reference-aligned text than a direct large language model baseline. The evaluation is deliberately broader than a single automatic score. Table-to-text quality has several distinct dimensions: the generated text must select the right facts, express them fluently, respect the requested genre and output length, remain grounded in the source, and avoid adding interpretations that the source cannot support. A system can perform well on one of these dimensions while performing poorly on another. For example, a short output can receive a favourable edit-distance score while omitting important content, and a detailed source-faithful report can receive a lower lexical-overlap score when the human reference uses unsupported narrative details.

The quantitative boundary for this chapter is the five-dataset, five-examples-per-dataset experiment carried out on 4-5 August 2026. This experiment contains 25 examples and 50 outputs: one output from the complete workflow and one from a raw generic DeepSeek V4 Flash baseline for every example. Tests and results produced before this boundary are excluded from the quantitative argument. Later experiments are included when they answer a distinct evaluation question, such as the effect of model strength, the effect of removing a workflow stage, or the behaviour of an LLM-only multi-agent system. Development smoke tests, interrupted model calls and repeated debugging runs are not combined with completed experiments.

The main evaluation addresses five research questions:

1. Does the complete workflow improve output quality relative to a direct, generic-prompt LLM baseline across heterogeneous table-to-text tasks?

2. Does the workflow reduce hallucinated or unsupported claims by grounding report content in extracted evidence, verified facts and source-aware audit checks?

3. Which kinds of task benefit most from the architecture, and which tasks can already be handled effectively by a direct model call?

4. Which workflow stages appear to contribute most to factual grounding, content coverage, hallucination control and narrative quality?

5. Are the observed improvements attributable mainly to the architecture, or can they be reproduced simply by replacing the underlying model with a stronger one?

The chapter also considers a fifth exploratory question: can an LLM-only multi-agent design reduce hallucination risk without the deterministic evidence and verification infrastructure of the main system? This final question is based on a separate experimental clone and one detailed SportSett example, so it is interpreted as a case study rather than a general benchmark result.

The hypotheses discussed below are explanatory hypotheses developed from the observed experiments. They were not preregistered and should not be presented as confirmatory statistical hypotheses. The principal hypotheses are:

- H1: architectural benefits will be largest when the input requires structural interpretation, focused evidence selection or genre inference;
- H2: direct LLM generation will remain competitive on simple attribute and triple verbalisation tasks;
- H3: insight synthesis will improve relational coverage and narrative breadth more than basic factual correctness;
- H4: stronger models will improve the raw baseline more consistently than the complete workflow, because the workflow already constrains and scaffolds weaker models;
- H5: reference similarity and source-grounded factuality will sometimes disagree, especially when references contain details that cannot be recovered from the supplied source;
- H6: LLM-as-a-judge results will reveal task and context errors that overlap metrics do not identify.

## 2. System evaluated

The evaluated system is a six-role workflow supported by deterministic data, structure, capability, evidence and audit infrastructure. The six LLM roles are Data Understanding, Orchestrator, Evidence Analyst, Fact Verifier, Writer and Auditor. These roles do not operate as six independent writers. Each has a constrained responsibility within an evidence flow.

The current implementation first loads CSV or JSON data and preserves structured benchmark representations where possible. It then constructs an input structure profile and structural catalogue, including nested paths, probable row semantics, event-like structures and potential reference fields. Reference-like text is excluded from generation and retained only for evaluation. The system builds a semantic map and resolves which generic evidence capabilities are available. Those capabilities include dataset profiling, focused-table analysis, structured-record verbalisation, association, group comparison, ranking, event outcome, event context, score progression, entity performance and event sequence.

The Orchestrator receives the request, structure profile, semantic map and available capabilities. It produces a frozen execution plan rather than inventing arbitrary analytical operations after seeing results. Deterministic capability executors then create evidence items. Candidate facts are generated and verified against this evidence, producing a fact ledger with explicit evidence identifiers and permissions. A second-pass insight stage may propose bounded relationships between verified facts. These insights are separately verified and retain their source fact and evidence identifiers.

The Writer does not receive an unrestricted invitation to inspect the raw source and improvise. It receives a curated evidence pack containing the report contract, verified facts, verified bounded insights, limitations and prohibited claim types. For event reports, the narrative module groups supported content into result, context, score progression, event sequence, leading performance, participant contrast, secondary detail and closing-scope slots. A quality revision pass can improve coverage and organisation before the factual audit. The Auditor checks sentence-level support, entities, numbers, evidence identifiers, causal language and genre fulfilment. Repair rounds can revise a report without authorising new facts.

This architecture matters for interpreting the evaluation. The comparison is not simply between a long prompt and a short prompt. It is between a system that explicitly interprets structure, selects capabilities, constructs evidence, verifies claims, plans a narrative and audits support, and a baseline that asks one model to infer all of these operations in a single call.

The system has also evolved to support different communication contracts. A focused ToTTo description is constrained to a focused table region and one sentence. E2E receives an attribute-verbalisation contract. WebNLG and DART receive triple-verbalisation contracts. SportSett receives an event-report contract with result-first organisation, leading performances, participant contrasts and bounded scope. This genre and output-form separation is central to the main findings.

## 3. Experimental design

### 3.1 Datasets and task diversity

The 25-example evaluation contains five examples from each of five datasets:

| Dataset | Task family | Output form | Primary challenge |
| --- | --- | --- | --- |
| SportSett Basketball | Event report | Multi-paragraph report | Select and relate salient facts from a large nested game record |
| E2E NLG | Attribute verbalisation | Short text | Express all supplied attributes fluently and concisely |
| ToTTo | Highlighted-table description | One sentence | Resolve highlighted cells to the correct subject and relation |
| WebNLG | Triple verbalisation | Short text | Preserve entities, predicates, values and units while producing fluent text |
| DART | Triple verbalisation | Short text | Verbalise heterogeneous relation triples without unsupported additions |

The experiment therefore combines long-form selection and narration with tightly bounded short-form realisation. This is more informative than treating every dataset as an ordinary flat table. It tests whether the same architecture can infer and fulfil different communication contracts without a separate end-to-end pipeline for every domain.

The complete workflow received the benchmark task request. For SportSett the request asked for a coherent game report that led with the result and selected important performances and contrasts. ToTTo requested exactly one sentence about highlighted cells. E2E requested one or two fluent sentences containing all supplied attributes. WebNLG and DART requested short coherent verbalisation of all supplied triples.

The final raw baseline used a stricter generic prompt: `Understand the supplied data and report its strongest supported findings.` It was not given the dataset identifier, task family, expected output form or language hint by the baseline prompt builder. This design tests whether a direct model can infer the task from the source alone. It gives the architecture an advantage in task interpretation, but that advantage is part of the system being evaluated: the workflow itself constructs the task and report contracts. The comparison should therefore be described as a complete task-aware architecture against a minimally scaffolded real-world baseline, not as a controlled prompt-only comparison.

### 3.2 Model configuration

All six roles in the main 25-example workflow used `deepseek:deepseek-v4-flash`. The raw baseline used a single `deepseek-v4-flash` call. Each variant used one recorded repetition with seed 42. The workflow used prompted structured output and stored intermediate artifacts for input structure, understanding, plan, evidence, facts, insights, writer support and audit.

Later model-strength experiments used four configurations:

| Variant | Configuration |
| --- | --- |
| Full Flash | All six workflow roles on DeepSeek V4 Flash |
| Raw Generic Flash | One generic-prompt DeepSeek V4 Flash call |
| Full Pro | All six workflow roles on DeepSeek V4 Pro |
| Raw Generic Pro | One generic-prompt DeepSeek V4 Pro call |

A later allocation experiment retained DeepSeek V4 Flash for understanding, orchestration, evidence, verification and audit but replaced only the Writer with `openai:gpt-5.5`. This tests whether surface realisation, rather than upstream reasoning, was the principal model bottleneck.

### 3.3 Output completion and internal support

The main paired experiment completed all 50 outputs with no empty generations and no recorded generation errors. Of the 25 workflow outputs, 23 used the LLM writer, one SportSett report was repaired by the auditor, and one SportSett report used deterministic fallback. Three workflow outputs were released as approved and 22 as approved with warnings. Every workflow output recorded an audit support rate of 1.0. Across the five SportSett reports, 77 supported sentences were mapped and all 77 had valid support mappings. The short-form datasets generally produced one support-mapped sentence per example.

The warnings must not be equated with factual failure. In many short-form cases the warning reflects generic report-coverage thresholds that are not naturally meaningful for a one-sentence task. Conversely, approval by the native auditor is not proof of perfect correctness. The later GPT-5.6 judge identified a repeated chronology error in SportSett reports that the native audit did not reject. Internal support therefore measures traceability to the system's own fact ledger, while independent judges test whether those facts and their interpretation are themselves correct.

## 4. Evaluation framework

### 4.1 Why multiple metric families are necessary

No single automatic metric measures the full quality of a table-to-text output. The evaluation therefore separates the following dimensions.

| Dimension | Metrics or evidence | Interpretation |
| --- | --- | --- |
| Lexical overlap | BLEU, ROUGE-1, ROUGE-2, ROUGE-L | Similarity to reference wording and content sequence |
| Character overlap | chrF | Robust overlap for names, numbers, morphology and short text |
| Edit distance | TER | Editing required to reach the reference; lower is better |
| Semantic similarity | BERTScore F1 | Similarity in contextual representation despite paraphrase |
| Flexible content overlap | METEOR | Alignment allowing more variation than exact n-gram metrics |
| Table-aware fidelity | PARENT | Intended to combine reference and table support, where available |
| Local source support | HHEM | Sentence-level support estimates against supplied context |
| Source alignment | AlignScore | Alignment between generated claims and source context |
| LLM judgement | DeepEval faithfulness and G-Eval criteria | Independent semantic assessment with written reasons |
| Structured error analysis | GPT-5.6 Sol taxonomy | Counts and categories of concrete output errors |
| Native grounding | Support rate and valid fact/evidence IDs | Whether released sentences map to verified internal support |

BLEU and ROUGE remain useful for comparability, but they are not treated as factuality metrics. BERTScore and chrF are emphasised because the output may express the same supported proposition in different wording. METEOR and ROUGE-L provide complementary signals for content selection and ordering. TER is interpreted cautiously because very short outputs can require fewer edits while omitting important content.

HHEM and AlignScore are diagnostic rather than decisive. Their input representation matters. Large nested SportSett sources are serialized into long contexts, and the local models may not associate a report sentence with distant evidence. HHEM also splits text into sentences, which can mishandle abbreviations such as `J.J.`. The source-grounded results are therefore triangulated with the native support map and LLM judges.

PARENT did not produce usable scores in the main experiment. Across its three outputs, 20 records per metric were skipped because the adapter did not expose a PARENT-compatible table and 30 were unavailable because the optional KaijuML PARENT package was not installed. These missing values are reported rather than imputed.

### 4.2 LLM-as-a-judge configurations

Two judge families were used after the evaluation boundary.

DeepEval used `deepseek:deepseek-v4-pro` as the judge. The saved main-batch artifacts contain five criteria: faithfulness, factual correctness, task relevance, coherence and usefulness. Some later SportSett runs also contain summarization and reference adequacy. The judge received the output and evaluation context and returned a score, threshold decision and written reason.

GPT-5.6 Sol was used as a cross-family structured error annotator. It received one output at a time, the supplied source, task metadata and the error taxonomy. It did not receive the human reference, competing output, system identity or automatic metric scores. It returned zero or more errors with a span, category and correction. The categories were NAME, NUMBER, WORD, CONTEXT, NOT CHECKABLE, OTHER, OMISSION and TASK/FORMAT. This is methodologically stronger than asking for a single impressionistic score because it creates inspectable claims that can later be compared with human annotation.

## 5. Main 25-example results

### 5.1 Overall reference similarity

The complete workflow exceeded the raw generic baseline on every reported macro reference metric. The largest absolute differences occurred in TER, ROUGE-1, chrF, BLEU and ROUGE-L. The semantic BERTScore difference was smaller but consistent with an advantage for the workflow.

| Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | METEOR | BERTScore F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full system | 0.3595 | 0.5972 | 0.7161 | 0.7172 | 0.4641 | 0.5599 | 0.5550 | 0.9246 |
| Raw generic Flash | 0.2383 | 0.4676 | 2.6303 | 0.5694 | 0.3585 | 0.4440 | 0.4495 | 0.8965 |

The corpus-level metrics show the same pattern:

| Variant | Corpus BLEU | Corpus chrF | Corpus TER |
| --- | ---: | ---: | ---: |
| Full system | 0.3482 | 0.5961 | 0.8719 |
| Raw generic Flash | 0.2209 | 0.4601 | 2.8756 |

Paired bootstrap analysis was derived from the 25 saved output pairs using 10,000 resamples. Positive advantage values favour the workflow; the TER sign is reversed so that a positive value still indicates a workflow advantage.

| Metric | Mean advantage | 95% bootstrap interval | Full wins | Ties | Raw wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| BERTScore F1 | 0.0281 | [0.0105, 0.0486] | 18 | 2 | 5 |
| BLEU | 0.1212 | [0.0632, 0.1838] | 21 | 2 | 2 |
| chrF | 0.1295 | [0.0719, 0.1942] | 22 | 2 | 1 |
| METEOR | 0.1055 | [0.0433, 0.1739] | 21 | 2 | 2 |
| ROUGE-1 | 0.1478 | [0.0677, 0.2359] | 19 | 4 | 2 |
| ROUGE-2 | 0.1057 | [0.0307, 0.1792] | 16 | 5 | 4 |
| ROUGE-L | 0.1159 | [0.0272, 0.2116] | 16 | 4 | 5 |
| TER improvement | 1.9143 | [0.4001, 3.8331] | 15 | 3 | 7 |

All intervals exclude zero. This does not convert the convenience sample into a population benchmark, but it shows that the macro result is not caused by one isolated example. The architecture won on 22 of 25 chrF comparisons and 21 of 25 BLEU and METEOR comparisons. BERTScore gains were smaller and five raw outputs scored higher, which is expected where both variants stated the same short proposition with minor phrasing differences.

### 5.2 Dataset-level variation

The architecture advantage is not uniform across tasks.

| Dataset and variant | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DART full | 0.1940 | 0.4918 | 0.8431 | 0.4789 | 0.4600 | 0.9206 |
| DART raw | 0.1580 | 0.4796 | 1.0942 | 0.4916 | 0.4378 | 0.9186 |
| E2E full | 0.6039 | 0.7631 | 0.4354 | 0.7398 | 0.7970 | 0.9635 |
| E2E raw | 0.5478 | 0.7439 | 0.4695 | 0.7364 | 0.8006 | 0.9625 |
| SportSett full | 0.0894 | 0.4143 | 0.9638 | 0.2251 | 0.2537 | 0.8424 |
| SportSett raw | 0.0422 | 0.2558 | 0.8133 | 0.2269 | 0.1703 | 0.8296 |
| ToTTo full | 0.3406 | 0.5674 | 0.8730 | 0.5856 | 0.5652 | 0.9338 |
| ToTTo raw | 0.0413 | 0.2021 | 10.0653 | 0.1311 | 0.2266 | 0.8277 |
| WebNLG full | 0.5696 | 0.7492 | 0.4651 | 0.7703 | 0.6993 | 0.9624 |
| WebNLG raw | 0.4022 | 0.6568 | 0.7094 | 0.6341 | 0.6122 | 0.9440 |

ToTTo is the clearest architecture result. The raw generic model interpreted the large surrounding table as the task and produced long dataset-level findings. The workflow identified that only the highlighted region should be verbalised and produced concise propositions. In example 204, the workflow wrote `Ma Ying-jeou received 58.45% of the vote.` The raw output attributed the figure to the `Vincent Siew ticket`, discussed the losing ticket and total vote count, and violated the one-sentence requirement. The reference was `Ma won the presidency by 58.45% of the vote.` The workflow therefore solved both a subject-linking problem and a content-selection problem.

The same pattern appears throughout ToTTo. For Jan Koukal, the workflow reported the highlighted mayoral term; the raw output summarized the entire history of Prague mayors. For George Keverian, the workflow stated the highlighted speaker and term; the raw output produced a long history of party representation and omitted Keverian. For the Swiss and French tax example, the workflow related the two highlighted rates while the raw output discussed many unhighlighted countries and omitted the highlighted French value. This explains the extreme raw ToTTo TER mean of 10.0653 and the large BERTScore gap of 0.1061.

WebNLG also shows a clear benefit. The workflow preserved relation structure and converted serialized forms into natural names. For example, it produced `The ALCO RS-3 has a four-stroke engine, 12 cylinders, and a length of 17068.8 millimetres.` The raw generic output was factually similar, but retained source-like `ALCO_RS-3` formatting in some runs or added framing such as `The strongest supported findings are`. These differences reduce reference overlap and demonstrate that realisation policy matters even when the underlying facts are simple.

E2E is close to a ceiling. Both systems produced essentially identical outputs for two examples, and the raw output slightly exceeded the workflow on mean METEOR. The task normally exposes a small set of attributes that should all be stated. There is little need for evidence prioritisation, ranking, narrative planning or insight synthesis. The architecture still achieved small gains on most metrics, particularly when the raw model used a bullet list for the more complex Clowns example, but H2 is supported: direct generation is already strong on bounded attribute verbalisation.

DART is similarly mixed. The workflow improved mean BLEU, chrF, METEOR, BERTScore and TER, but raw generic achieved a slightly higher mean ROUGE-L and clearly outperformed the workflow on `dart-test-260`. The workflow wrote `Philippe Jeannol played from 1984 - 1991 and made 219 appearances`, while the raw output more closely matched the reference by writing `Philippe Jeannol recorded 219 appearances during the period 1984-1991.` This is a useful counterexample. The architecture is not guaranteed to choose the most reference-like syntax when all necessary facts are already explicit in a single relation.

SportSett requires the most careful interpretation. The workflow improved BLEU, chrF, METEOR and BERTScore, but raw generic was slightly better on ROUGE-L and TER. Workflow reports averaged approximately 335 words, whereas direct outputs were much shorter. The workflow covered quarter progression, a broader set of player leaders, team contrasts and next-game context. The reference often included play-by-play details such as opening runs and momentum that were unavailable in the supplied box-score representation. Consequently, even a complete source-grounded report could not closely match all reference sequences. TER and ROUGE-L partly reward the shorter baseline's compression, while chrF, METEOR and BERTScore reflect the workflow's greater supported coverage.

### 5.3 Complete per-example principal metrics

The following table preserves the main per-example evidence. FS denotes the full system and RG denotes raw generic Flash.

| Dataset/example | FS BLEU | FS chrF | FS TER | FS ROUGE-L | FS METEOR | FS BERT-F1 | RG BLEU | RG chrF | RG TER | RG ROUGE-L | RG METEOR | RG BERT-F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DART 204 | .355 | .580 | .667 | .714 | .625 | .965 | .138 | .518 | 1.500 | .400 | .564 | .946 |
| DART 217 | .068 | .378 | .857 | .429 | .290 | .869 | .042 | .315 | 1.143 | .353 | .208 | .841 |
| DART 244 | .201 | .505 | .714 | .435 | .417 | .915 | .167 | .464 | .714 | .435 | .359 | .916 |
| DART 260 | .172 | .551 | .727 | .400 | .405 | .937 | .382 | .773 | .364 | .900 | .641 | .987 |
| DART 53 | .174 | .444 | 1.250 | .417 | .563 | .917 | .061 | .327 | 1.750 | .370 | .418 | .901 |
| E2E 178 | .677 | .806 | .338 | .812 | .789 | .980 | .677 | .806 | .338 | .812 | .789 | .980 |
| E2E 51 | .869 | .870 | .353 | .722 | .832 | .970 | .700 | .822 | .176 | .757 | .933 | .973 |
| E2E 54 | .203 | .488 | 1.111 | .409 | .598 | .904 | .163 | .471 | 1.333 | .409 | .526 | .901 |
| E2E 61 | .597 | .829 | .125 | .875 | .865 | .981 | .525 | .797 | .250 | .824 | .854 | .976 |
| E2E 65 | .673 | .823 | .250 | .880 | .900 | .983 | .673 | .823 | .250 | .880 | .900 | .983 |
| SportSett 4934 | .123 | .443 | .844 | .276 | .259 | .867 | .030 | .225 | .811 | .241 | .168 | .814 |
| SportSett 4972 | .122 | .456 | .899 | .236 | .289 | .854 | .039 | .226 | .819 | .203 | .149 | .823 |
| SportSett 4975 | .025 | .334 | 1.337 | .165 | .215 | .795 | .049 | .230 | .832 | .200 | .153 | .825 |
| SportSett 4982 | .082 | .430 | .883 | .218 | .242 | .851 | .045 | .321 | .784 | .256 | .215 | .852 |
| SportSett 4986 | .095 | .409 | .857 | .231 | .264 | .844 | .047 | .277 | .822 | .234 | .166 | .833 |
| ToTTo 204 | .489 | .497 | .400 | .632 | .550 | .911 | .019 | .184 | 4.900 | .135 | .166 | .852 |
| ToTTo 217 | .118 | .529 | 1.161 | .533 | .650 | .928 | .004 | .077 | 19.355 | .052 | .099 | .789 |
| ToTTo 244 | .482 | .755 | .429 | .824 | .640 | .965 | .025 | .192 | 11.411 | .083 | .169 | .791 |
| ToTTo 260 | .034 | .300 | 1.905 | .303 | .174 | .903 | .003 | .125 | 12.190 | .071 | .173 | .818 |
| ToTTo 712 | .580 | .757 | .471 | .636 | .811 | .961 | .155 | .432 | 2.471 | .314 | .527 | .889 |
| WebNLG 178 | .690 | .832 | .321 | .865 | .749 | .967 | .470 | .748 | .696 | .727 | .720 | .933 |
| WebNLG 51 | .662 | .805 | .333 | .865 | .777 | .986 | .406 | .666 | .667 | .718 | .599 | .963 |
| WebNLG 54 | .349 | .629 | .658 | .557 | .459 | .930 | .276 | .572 | .763 | .524 | .448 | .906 |
| WebNLG 61 | .573 | .716 | .324 | .923 | .759 | .982 | .443 | .629 | .486 | .615 | .581 | .974 |
| WebNLG 65 | .574 | .764 | .689 | .642 | .753 | .948 | .417 | .668 | .934 | .586 | .713 | .943 |

## 6. Source-grounded factuality

The source-grounded HHEM and AlignScore results are less decisive than the reference metrics.

| Variant | AlignScore | HHEM mean support | HHEM minimum support | HHEM unsupported sentence rate |
| --- | ---: | ---: | ---: | ---: |
| Full system | 0.6784 | 0.5530 | 0.5396 | 0.3504 |
| Raw generic Flash | 0.6121 | 0.5437 | 0.4665 | 0.3460 |

The workflow has higher mean AlignScore, HHEM mean support and minimum sentence support. The unsupported sentence rate is effectively tied and slightly favours raw generic. Paired bootstrap intervals reinforce this cautious interpretation.

| Metric | Full advantage | 95% bootstrap interval | Full wins | Ties | Raw wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| AlignScore | 0.0663 | [-0.0407, 0.1926] | 11 | 2 | 12 |
| HHEM mean support | 0.0093 | [-0.0642, 0.0721] | 16 | 2 | 7 |
| HHEM minimum support | 0.0730 | [0.0159, 0.1388] | 13 | 2 | 10 |
| HHEM unsupported-rate improvement | -0.0044 | [-0.1187, 0.1163] | 5 | 17 | 3 |

Only minimum sentence support has an interval that excludes zero. The mixed win counts show substantial dataset dependence. AlignScore is higher on average for the workflow but raw generic wins 12 individual comparisons against 11 workflow wins.

The per-dataset source scores reveal the representation problem:

| Dataset/variant | AlignScore | HHEM mean | HHEM minimum | Unsupported rate |
| --- | ---: | ---: | ---: | ---: |
| DART full | .977 | .877 | .877 | .000 |
| DART raw | .844 | .769 | .769 | .000 |
| E2E full | .978 | .673 | .673 | .000 |
| E2E raw | .967 | .711 | .711 | .000 |
| SportSett full | .128 | .069 | .010 | .952 |
| SportSett raw | .194 | .094 | .024 | .933 |
| ToTTo full | .351 | .449 | .449 | .600 |
| ToTTo raw | .461 | .537 | .225 | .397 |
| WebNLG full | .957 | .698 | .690 | .200 |
| WebNLG raw | .595 | .607 | .603 | .400 |

SportSett's near-zero support values conflict with the workflow's complete internal mapping and with the LLM judge's high factual-correctness scores. This is unlikely to mean that 95% of workflow sentences are hallucinated. The nested source is large, repeated and serialized, and the external factuality models see a truncated or difficult context. ToTTo also shows disagreement because the focused proposition may depend on page and header context rather than a locally obvious source sentence. These findings support H5: source-grounded metrics are informative, but their scores depend strongly on how structured data is converted into text for the metric.

## 7. LLM-as-a-judge results

### 7.1 DeepSeek V4 Pro judge

The main saved DeepEval batches contain 140 judge records. Of these, 137 were scored and three failed because the judge returned invalid JSON. Every record used `deepseek:deepseek-v4-pro`. Coverage was incomplete: the judge scored 20 full-system examples and eight earlier `raw_deepseek_v4_flash` baseline examples, not all 25 raw-generic outputs. The raw rows therefore must not be treated as the same baseline as the final generic-prompt experiment.

| Variant | Faithfulness | Coherence | Factual correctness | Task relevance | Usefulness |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full system | 0.9973 | 0.9800 | 1.0000 | 1.0000 | 0.9900 |
| Earlier raw Flash subset | 0.9590 | 0.9714 | 0.9875 | 0.9250 | 0.9750 |

The DeepSeek judge favours the workflow on every criterion. The largest difference is task relevance, consistent with the workflow's explicit output contracts. However, the scores show a strong ceiling effect. Almost every value is between 0.9 and 1.0, which limits discrimination. The same model family generated and judged many outputs, creating a potential family-preference concern. The results are therefore supporting evidence rather than the primary result.

Coverage by dataset was uneven. The workflow judge means were:

| Dataset | Faithfulness | Coherence | Factual correctness | Task relevance | Usefulness |
| --- | ---: | ---: | ---: | ---: | ---: |
| DART | 1.0000 | 0.9800 | 1.0000 | 1.0000 | 1.0000 |
| E2E | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| SportSett | 0.9837 | 0.9250 | 1.0000 | 1.0000 | 0.9500 |
| ToTTo | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| WebNLG | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

Three metric calls failed: DART 260 workflow faithfulness, SportSett 4934 workflow faithfulness, and SportSett 4975 raw coherence. These are evaluation failures, not zero scores.

A later SportSett 4934 post-fix comparison included all seven configured judge metrics:

| Variant | Faithfulness | Summarization | Coherence | Factual correctness | Reference adequacy | Task relevance | Usefulness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full system | 1.0000 | 0.8000 | 0.9000 | 1.0000 | 0.6000 | 1.0000 | 1.0000 |
| Raw Flash | 1.0000 | 0.3214 | 1.0000 | 0.9000 | 0.5000 | 1.0000 | 1.0000 |

This judge saw the workflow as substantially more adequate as a summary, slightly more factually correct and slightly more reference-adequate, while the raw output was marginally more coherent. This is plausible given the workflow's greater coverage and the raw output's brevity.

Other saved SportSett judge runs illustrate judge variance. One full-system run received faithfulness 1.0, summarization 0.5333, coherence 0.9, factual correctness 0.9, reference adequacy 0.4, task relevance 0.9 and usefulness 0.5. Another received faithfulness 0.9667, factual correctness 1.0, task relevance 0.8, coherence 0.8 and usefulness 0.7. The generated text and evaluation context differed across these runs, but the variation also warns against treating one LLM judgement as a precise measurement.

### 7.2 GPT-5.6 Sol structured error annotations

The cross-family GPT-5.6 Sol run successfully annotated 49 main-experiment outputs: 24 workflow outputs and all 25 raw-generic outputs. One workflow output, SportSett 4975, was absent. GPT-5.6 reported 8 errors in the 24 workflow outputs and 19 errors in the 25 raw outputs.

| Variant | Outputs | Outputs with errors | Total errors | Mean errors/output | Median | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Full system | 24 | 4 | 8 | 0.333 | 0 | 2 |
| Raw generic Flash | 25 | 11 | 19 | 0.760 | 0 | 4 |

On the 24 paired examples, the workflow averaged 0.333 errors and raw generic averaged 0.750. The workflow had fewer errors in six pairs, the outputs tied in 16, and raw had fewer in two. The large number of ties reflects perfect or near-perfect short-form outputs in DART and E2E.

| Error category | Full system | Raw generic Flash |
| --- | ---: | ---: |
| CONTEXT | 4 | 4 |
| NUMBER | 0 | 2 |
| OMISSION | 0 | 3 |
| TASK/FORMAT | 4 | 10 |
| NAME | 0 | 0 |
| WORD | 0 | 0 |
| NOT CHECKABLE | 0 | 0 |
| OTHER | 0 | 0 |

This is one of the most informative evaluation results. The workflow eliminated all GPT-detected numeric errors and omissions in the annotated sample. Its remaining errors were concentrated in SportSett chronology and paragraph format. The raw baseline's largest weakness was task fulfilment: all five ToTTo outputs violated the requested one-sentence focus, and all five SportSett outputs used a single inline list or paragraph instead of a multi-paragraph report.

Dataset-level counts reinforce the architecture hypothesis:

| Dataset/variant | Annotated outputs | Outputs with errors | Total errors |
| --- | ---: | ---: | ---: |
| DART full | 5 | 0 | 0 |
| DART raw | 5 | 0 | 0 |
| E2E full | 5 | 0 | 0 |
| E2E raw | 5 | 0 | 0 |
| SportSett full | 4 | 4 | 8 |
| SportSett raw | 5 | 5 | 7 |
| ToTTo full | 5 | 0 | 0 |
| ToTTo raw | 5 | 5 | 11 |
| WebNLG full | 5 | 0 | 0 |
| WebNLG raw | 5 | 1 | 1 |

The full system's repeated SportSett context error was the statement that teams `entered` with the records supplied in the source. The records summed to the game number and included the observed result, so they were post-game records. GPT-5.6 correctly advised `improved to` and `fell to`. This exposes an important distinction between numerical support and temporal interpretation: every number can be copied correctly while the sentence remains contextually wrong. The current fact and audit infrastructure traced the values but did not infer whether record fields were pre-game or post-game.

The format error reflects an artifact-level representation issue. The generation text displayed line breaks, but the structured judge saw the report as a single paragraph in the evaluated serialization. Regardless of whether this arose during generation or serialization, it matters because output form is part of task fulfilment.

The raw ToTTo errors are more severe. GPT-5.6 detected an incorrect claim that the Prague table contained 24 mayors rather than 24 officeholding entries, a false uninterrupted Communist sequence, omission of Jan Koukal, omission of George Keverian, omission of France's highlighted tax value, unsupported explanation of Swiss tax structure, and repeated one-sentence violations. These findings align with the reference metrics and demonstrate that the ToTTo advantage is structural rather than cosmetic.

In WebNLG 178, the raw model added `(minutes)` to a source value that did not explicitly specify its unit in the supplied representation. The reference itself used minutes, so reference overlap can reward a detail that a strict source-only judge rejects. This is a concrete example of H5 and illustrates why reference and source evaluations must remain separate.

A separate successful GPT-5.6 annotation of SportSett 4934 reproduced the same two workflow errors: post-game records framed as entry records and failure to deliver a multi-paragraph report. This replication increases confidence that these are genuine weaknesses rather than a one-off judge response.

An attempted GPT-5.6 annotation of the five GPT-5.5-writer outputs failed for all five items because the OpenAI account had no remaining API credits. Those records have status `error` and contain no annotations. They are not interpreted as zero-error outputs.

## 8. Prompt robustness and task inference

SportSett 4934 was rerun with the generic request on both the complete workflow and the raw model. The first workflow attempt fell back to deterministic writing and performed poorly: BERTScore 0.8054, BLEU 0.0202, chrF 0.2961, METEOR 0.2215 and ROUGE-L 0.1186. Raw generic was stronger on most metrics. After the structure and task-inference fixes, the workflow used the LLM writer and produced a coherent event report from the same generic request.

| Variant | BERTScore F1 | BLEU | chrF | METEOR | ROUGE-L | TER |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Full generic after fix | 0.8506 | 0.1110 | 0.4507 | 0.3054 | 0.2385 | 0.9550 |
| Raw generic | 0.8414 | 0.0755 | 0.2994 | 0.1974 | 0.2772 | 0.8198 |

The post-fix workflow won BERTScore, BLEU, chrF and METEOR, while the shorter raw output retained better ROUGE-L and TER. More importantly, the workflow inferred an event-report genre and produced result, progression, performances and contrasts rather than treating the nested record as a dataset profile. This experiment supports H1: the system can construct task structure from the input, but only if structure recognition, report-contract resolution and writer routing all succeed.

A later exploratory task-contract upgrade was tested on the same SportSett 4934 example. This version added an explicit inferred-contract variant that attempted to infer task family, report genre, communication task, output form and focus scope from operational source structure. The inference itself succeeded: the system selected an event report, multi-paragraph output and event-recap focus with high confidence. However, the resulting report did not improve over the selected workflow. With DeepSeek V4 Flash, the inferred-contract variant scored below the saved full-system run on BLEU, chrF, METEOR, ROUGE, BERTScore, AlignScore and HHEM mean support. It was also slow, taking approximately 946 seconds for one example, and still used contextually risky wording around team records. This result is treated as a useful negative finding: task-contract inference is promising as lightweight routing, but the tested heavyweight inferred-contract path is not adopted as the final system.

### 8.1 Additional exploratory findings from development runs

Several useful findings emerged during development runs that were not treated as primary benchmark evidence because they were produced before the protected 25-example comparison, used changing code, or were single-case diagnostics. They are nevertheless useful for interpreting the final architecture.

First, single-event inputs should not be treated as ordinary flat datasets. Early basketball and baseball experiments showed that a generic data-quality template could correctly identify constant fields while missing the communicative task: describing what happened in the event. This motivated the later distinction between dataset reports, focused verbalisation tasks and event reports.

Second, narrative ordering matters as much as fact extraction. In MLB development runs the system could extract many correct rankings, score changes and player statistics, but early outputs read like exhaustive stat dumps. More useful reports began with the result, then selected a small number of game sequence events, key performances and participant contrasts. This supports the claim that data-to-text generation requires salience and discourse planning, not only fact recovery.

Third, more evidence is not automatically better. Removing hard caps on findings and insights increased coverage, but it also made some outputs less reference-like because they included additional correct but non-reference details. This explains why reference metrics sometimes penalise richer reports and why human evaluation is needed for completeness and usefulness.

Fourth, short-form datasets require stricter focus than event reports. ToTTo, E2E, WebNLG and DART examples showed that one-sentence and short-text tasks reward precise selection and restraint. The same architecture that helps SportSett through event structure can hurt short-form tasks if it expands a focused proposition into a mini report.

Fifth, ToTTo exposed a highlighted-region salience problem. The Ma Ying-jeou, Switzerland-France tax and Jan Koukal development examples showed that the system needed to privilege highlighted cells and their local row/header context over globally interesting table facts. This finding helped motivate the focused-table-description route used in the final evaluation.

Sixth, direct raw LLM outputs often score well because they are compact and stylistically close to references. This is not the same as being more controllable or more source-faithful. The final evaluation therefore separates reference-overlap metrics from source-grounded checks and structured LLM-as-judge annotations.

Seventh, model upgrades alone were not sufficient. DeepSeek Pro and GPT-5.5 experiments improved some individual outputs, but did not consistently solve task interpretation, salience or source-grounded discourse structure. The strongest results came from combining capable models with task routing, evidence selection, writer constraints and auditing.

Eighth, LLM-as-judge and automatic metrics exposed different risks. DeepEval-style judgement was useful for coherence and adequacy, but showed ceiling effects. GPT-5.6 structured annotation was more useful for named error categories, while HHEM and AlignScore were more sensitive to the choice of reference context versus source context. These findings support the multi-perspective evaluation design rather than reliance on a single score.

## 9. Ablation study

The stage ablation used SportSett example 4934. It compared the complete workflow with no insight synthesis, no writer quality revision and no audit repair rounds. The original raw row in the ablation artifact used an earlier raw Flash baseline; the later narrative analysis refreshed that baseline with raw generic Flash. The cleanest architectural comparisons are among the workflow variants.

| Variant | chrF | TER | ROUGE-L | METEOR | BERTScore F1 | Words | Support rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full system | 0.443 | 0.844 | 0.276 | 0.259 | 0.867 | 300 | 1.0 |
| Raw generic Flash | 0.225 | 0.811 | 0.241 | 0.168 | 0.814 | 116 | n/a |
| No insight synthesis | 0.362 | 0.781 | 0.288 | 0.247 | 0.862 | 168 | 1.0 |
| No writer quality revision | 0.414 | 0.838 | 0.258 | 0.269 | 0.854 | 292 | 1.0 |
| No audit repair rounds | 0.329 | 1.450 | 0.144 | 0.238 | 0.808 | 521 | 1.0 |

The complete workflow achieved the strongest chrF and BERTScore. Removing insight synthesis reduced the report from 300 to 168 words while preserving basic correctness and a 1.0 support rate. Result, date, venue, quarter scores and leading players remained, but relational content narrowed. The full report connected a wider set of defensive leaders, shot contrasts and team-level patterns. This supports H3: insight synthesis primarily contributes breadth and cross-fact synthesis, not the ability to copy a final score.

The no-insight output's good TER and ROUGE-L show why no single metric should define the ablation conclusion. It was shorter and closer to some reference sequences, yet covered fewer supported relationships. A human completeness or salience judgement is needed to validate whether the additional workflow content is useful.

Removing writer quality revision retained 292 words and most facts. The qualitative difference was repetition: it stated that Philadelphia led at each break and then repeated the same period-by-period scores. The revision stage appears to improve compression and flow more than factual coverage. METEOR happened to be highest without revision, demonstrating that overlap metrics do not reliably measure narrative economy.

The no-audit-repair variant is not a clean causal ablation. Its writer encountered an external model-response error and the final report was a 521-word recovery output. Similarly, the no-insight run used structural recovery after a data-understanding API error, and the no-writer-revision run reached the total-token limit during audit. These operational events mean the ablation cannot prove isolated causal effects. Its strongest defensible result is the observed reduction in synthesis and coverage when insights were disabled. Claims about audit repair and revision remain provisional.

## 10. Model-strength comparisons

### 10.1 DeepSeek Flash versus Pro

Four shared short-form examples were run through full and raw configurations using both DeepSeek V4 Flash and V4 Pro. The examples were E2E 51, ToTTo 204, WebNLG 51 and DART 53.

| Variant | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Full Flash | 0.5485 | 0.6540 | 0.5841 | 0.6588 | 0.6806 | 0.9461 |
| Raw generic Flash | 0.2964 | 0.5000 | 1.8733 | 0.4951 | 0.5289 | 0.9225 |
| Full Pro | 0.4623 | 0.6449 | 0.5752 | 0.6926 | 0.6629 | 0.9420 |
| Raw generic Pro | 0.3920 | 0.6334 | 0.7545 | 0.5804 | 0.6394 | 0.9380 |

The architecture beat the corresponding raw baseline under both model strengths on all six macro metrics. Raw Pro improved substantially over raw Flash, including BLEU from 0.2964 to 0.3920, chrF from 0.5000 to 0.6334, METEOR from 0.5289 to 0.6394 and TER from 1.8733 to 0.7545. This confirms that model strength matters and that the raw baseline is not intentionally weak.

Full Pro did not uniformly improve on Full Flash. Pro improved TER and ROUGE-L, while Flash retained higher BLEU, chrF, METEOR and BERTScore. WebNLG explains much of this pattern. The Pro workflow preserved source formatting such as `ALCO_RS-3`, capitalised `Four-stroke`, and placed the unit in parentheses, whereas Flash produced a more natural reference-like sentence. A more capable model can choose a less benchmark-aligned surface form even when its semantic content is correct.

ToTTo 204 is again the clearest architecture result. Raw generic Pro still attributed 58.45% to Vincent Siew, while both workflow configurations linked the value to Ma Ying-jeou. Increasing model strength did not remove the need for structure interpretation.

### 10.2 SportSett Pro case study

SportSett 4934 was also run with V4 Pro in all six roles and compared with a raw V4 Pro baseline. The workflow passed factual audit, used the LLM writer, recorded three verified insights and achieved a 1.0 native support rate across ten factual sentences.

| Metric | Full V4 Pro | Raw V4 Pro | Better |
| --- | ---: | ---: | --- |
| BLEU | 0.1337 | 0.1175 | Full |
| chrF | 0.4683 | 0.4305 | Full |
| TER | 0.7958 | 0.8168 | Full |
| ROUGE-1 | 0.5700 | 0.5371 | Full |
| ROUGE-2 | 0.2192 | 0.2234 | Raw by 0.0042 |
| ROUGE-L | 0.3413 | 0.2898 | Full |
| METEOR | 0.2970 | 0.2586 | Full |
| BERTScore F1 | 0.8839 | 0.8574 | Full |

The workflow won eight of nine listed metrics. The raw output was fluent, but described the 20,300 attendance in a 20,500-capacity arena as `sold-out`, which overstates the supplied values. This case supports the argument that evidence-led generation can outperform a strong direct model while avoiding a small but meaningful unsupported flourish. It remains a single example and should not be generalized to all SportSett games.

### 10.3 GPT-5.5 writer allocation

Five matching examples were run with DeepSeek V4 Flash for understanding, orchestration, evidence, verification and audit, and OpenAI GPT-5.5 only for writing.

| Dataset | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DART 53 | .1956 | .5662 | 1.2500 | .4167 | .5628 | .9264 |
| E2E 51 | .7938 | .8483 | .1765 | .8000 | .8909 | .9778 |
| SportSett 4934 | .0874 | .3993 | .9129 | .2285 | .2306 | .8418 |
| ToTTo 204 | .4888 | .4966 | .4000 | .6316 | .5500 | .9115 |
| WebNLG 51 | .0979 | .4939 | .8000 | .6154 | .3035 | .9294 |
| Macro mean | .3327 | .5609 | .7079 | .5384 | .5076 | .9174 |

All five outputs completed with the LLM writer and no generation errors. The allocation was not a general improvement. WebNLG deteriorated because GPT-5.5 preserved source-like forms: `ALCO_RS-3's engine is Four-stroke_engine`. The output was factually recoverable but much less reference-like than the Flash workflow sentence. SportSett also remained weak on overlap metrics. E2E performed strongly, while ToTTo and DART were similar to Pro outputs.

The important inference is that the Writer model was not the sole bottleneck. Surface-form quality depends on the payload, realisation policy and task contract as well as model intelligence. Simply assigning a frontier model to writing can introduce stylistic variation that hurts controlled verbalisation.

A separate all-agent GPT-5.5 generation file contains only one completed SportSett row, even though an associated metric file contains five dataset rows. This provenance mismatch makes the five-row all-agent metric aggregate unsuitable as a completed experiment. The one completed generation can be discussed as an exploratory artifact, but the aggregate is not used for a model-effect claim.

## 11. LLM-only multi-agent experiment

The LLM-only experiment was implemented in a separate clone to isolate multi-agent decomposition from deterministic analytics. It did not call the main `Table2TextWorkflow`, deterministic plan executor, deterministic fact scaffold or deterministic audit. Its stages were Source Interpreter, Claim Analyst, Claim Critic, Claim Adjudicator, Writer, Output Auditor and Repair. The Writer could use only accepted claims, and later iterations required accepted claims to carry explicit source references and copied values.

The experiment used SportSett 4934 with references held out. The final Flash run proposed and accepted seven claims, passed audit with support rate 1.0 and produced an 85-word report. The Pro run accepted nine claims, passed with support rate 1.0 and produced 106 words. Both achieved generated-number source precision of 1.0.

| Context/metric | Full system | Raw Flash | LLM-only Flash | LLM-only Pro |
| --- | ---: | ---: | ---: | ---: |
| Reference BERTScore F1 | .8517 | .8504 | .8318 | .8548 |
| Reference BLEU | .1071 | .1357 | .0363 | .0525 |
| Reference chrF | .4166 | .3860 | .1835 | .2580 |
| Reference METEOR | .2580 | .2534 | .1111 | .1584 |
| Reference ROUGE-L | .2311 | .3214 | .2341 | .3058 |
| Source HHEM mean support | .2065 | .1662 | .2200 | .1808 |
| Source HHEM unsupported rate | .7895 | .7692 | .7143 | .7500 |

LLM-only Flash achieved the best HHEM mean support and lowest unsupported-sentence rate in this one example. Compared with raw Flash, mean support increased from 0.1662 to 0.2200 and unsupported rate fell from 0.7692 to 0.7143. This supports the exploratory hypothesis that role separation and claim gating can improve factual discipline without deterministic analytics.

The cost was coverage. LLM-only Flash had much lower BLEU, chrF and METEOR than the full system and raw baseline because it produced a cautious 85-word report. Pro improved every reported reference-similarity measure over LLM-only Flash and produced a richer game recap, but its HHEM score was lower. The result exposes a recurring coverage-grounding tension: the more claims a model realises, the more opportunities exist for unsupported or weakly aligned sentences.

The engineering failures are as informative as the scores. Agents often returned plausible content in invalid schemas, used categorical strings where numeric confidence was expected, or returned empty claim ledgers. Early versions blocked output when uncertainty was detected. Recovery analysis, tolerant schema normalization, fallback adjudication and evidence-gated writing were required to make the pipeline fail soft. The experiment therefore shows that adding agents creates control points and additional failure points. The strongest hallucination-control mechanism was not merely having a Critic; it was preventing the Writer from using claims that lacked accepted evidence metadata.

This experiment should not be treated as proof that LLM-only multi-agent systems are more factual in general. It uses one primary example and HHEM has known representation problems. The existing Pro artifact also predates the final evidence gate. Its appropriate dissertation role is an explanatory case study: decomposition alone can improve factual discipline, but deterministic evidence infrastructure improves robustness, coverage and inspectability.

## 12. Cross-experiment interpretation

### 12.1 Architecture is most valuable for semantic selection

The strongest result across metrics, judge annotations and qualitative inspection is not that the architecture rewrites sentences more elegantly. It is that it decides what the output is supposed to be about. In ToTTo, the main challenge is identifying the highlighted proposition within a large table. In SportSett, it is recognising one event and prioritising outcome, progression and performances rather than profiling columns. In WebNLG, it is preserving relation structure while normalising source formatting. These are semantic-selection problems.

The raw generic baseline performs well when selection is trivial. It matched the workflow exactly on two E2E examples and had no GPT-5.6 errors on E2E or DART. The system's overhead is therefore not justified by every input equally. A practical deployment could route simple bounded realisation tasks through a shorter evidence path while retaining the full architecture for ambiguous, nested or high-risk inputs. This is not evidence for removing verification; it is evidence for capability-aware computational depth.

### 12.2 The system is auditable but not infallible

Every main workflow sentence mapped to internal support, yet GPT-5.6 found four context errors. The system correctly copied the team records but incorrectly labelled them as pre-game. This shows that provenance and correctness are related but distinct. A claim may be supported by a field and still misinterpret the field's temporal semantics.

A robust improvement would represent temporal status explicitly in the semantic map or evidence item: pre-event record, post-event record, unknown timing, or context-dependent. The verifier and auditor could then prohibit `entered with` unless pre-event status is established. This is a generic fix applicable to sports standings, financial balances, election totals and other event records.

### 12.3 Stronger models do not remove architectural needs

Raw Pro improved substantially over raw Flash, but still made the ToTTo subject-linking error. Full Pro continued to outperform raw Pro on the four-example macro comparison and the SportSett case. This supports H4 in a nuanced form: model strength improves direct generation, while architecture contributes a separate source of value through task interpretation and evidence control.

The fact that Full Flash sometimes exceeded Full Pro also matters. A stronger model can paraphrase more freely, preserve awkward source forms or choose a different degree of compression. Reference metrics reward alignment with a particular human style, not latent reasoning capability. Model selection should therefore be role-specific and empirically evaluated. The evidence does not justify assigning the most expensive model to every agent.

### 12.4 Insight synthesis is useful but expensive and fragile

The ablation and run traces suggest that insight synthesis and verification increase relational coverage. Removing them produced a shorter but still factual SportSett recap. The current code verifies a batch and then retries unresolved insight candidates individually, which prevents one malformed item from discarding the entire ledger. This is methodologically appropriate but increases requests and repeated context.

The likely improvement is not a new hard cap on insights. It is salience-aware verification: generate atomic evidence deterministically, prioritize candidates relevant to the report contract, verify each high-priority candidate with the smallest necessary evidence packet, and let the Writer use all verified insights that fit the output contract. This would retain the uncapped design while reducing repeated large prompts.

### 12.5 Narrative quality needs direct evaluation

Reference metrics only partly captured the benefit of narrative planning and writer revision. The no-revision report repeated quarter information but remained strong on METEOR. The raw SportSett baseline was concise and received better TER, but it was a bullet-list summary rather than a multi-paragraph game narrative. DeepEval coherence gave raw outputs high scores, while GPT-5.6 classified their format as wrong.

Human evaluation should therefore ask separate questions about factual accuracy, important-content coverage, organisation, genre fulfilment and readability. A single preference question would conceal why an annotator preferred one output. The prepared human annotation study already follows this direction by asking annotators to label concrete errors and assess task quality.

## 13. Threats to validity

### 13.1 Sample size and selection

The main comparison contains 25 examples, only five per dataset. This is enough to reveal consistent paired patterns but not enough to claim benchmark-wide state of the art. Examples were selected for manageable evaluation and include cases used repeatedly during development. Familiarity with specific examples may have influenced later improvements. A protected test set would provide stronger evidence of generalisation.

The ablation, SportSett Pro comparison and LLM-only experiment are primarily single-example studies. They explain mechanisms but cannot estimate population effects. Provider errors also contaminate several ablation variants.

### 13.2 Baseline fairness

The final raw baseline intentionally received a generic request and no task metadata. This resembles a user supplying structured data without specifying the target genre, while the workflow constructs structure and report contracts internally. It is a meaningful system-level comparison but not a pure architecture ablation. The benchmark-aware raw baseline used in some DeepEval files is a different condition and is reported separately.

A complete future evaluation should include both raw conditions: generic prompt and task-matched prompt. The difference between them would estimate the value of task-contract inference separately from evidence construction and auditing.

### 13.3 Reference limitations

Human references are not guaranteed to be fully supported by the supplied source representation. SportSett references include momentum, opening runs and other play-by-play details that may not be present in the prepared box score. WebNLG references may supply a unit not explicit in the serialized source. Reference similarity can therefore penalise cautious source-faithful text and reward unsupported imitation.

This is why the chapter does not use BLEU or ROUGE as factuality evidence. The strongest claims require agreement among source checks, independent judges, native provenance and qualitative inspection.

### 13.4 Metric limitations

The main DeepEval judge used the same model family as the generator and displayed ceiling effects. GPT-5.6 provides cross-family evidence but only one judge repetition and one output was missing. It is itself an LLM and may make errors. The structured annotation run should ultimately be evaluated against human annotations using category-level precision, recall and F1.

HHEM and AlignScore struggled on nested SportSett input. PARENT was unavailable. BERTScore can award high similarity to text with the wrong task format. TER can favour brevity. Bootstrap intervals describe uncertainty within the selected pairs but do not correct selection bias.

### 13.5 Reproducibility and model APIs

The experiments recorded seed 42, but hosted LLM APIs are not guaranteed to reproduce identical outputs. Model aliases may change. Intermediate schemas, fallbacks and retries can also cause two nominally identical configurations to follow different execution paths. Saved manifests and complete artifacts are therefore more authoritative than variant names. The SportSett `full_system_fast` run, for example, actually used V4 Pro for all roles according to its manifest.

The all-agent GPT-5.5 metric mismatch and failed GPT-5.6 credit-limited run demonstrate the need for artifact validation. Every dissertation table should be generated from files whose generation rows, model manifests and metric generation identifiers match.

## 14. Answers to the research questions

**RQ1: Does the workflow improve over a raw generic model?** Yes, within the selected 25 examples. The workflow improved all macro reference metrics, won 22 of 25 chrF comparisons, and reduced GPT-5.6 error annotations from 19 to 8 despite one missing workflow annotation. The result is strongest for task relevance, focused content selection and omission avoidance.

**RQ2: Which tasks benefit most?** ToTTo benefits most because highlighted-cell interpretation and subject linking are not solved reliably by a generic request. WebNLG also benefits from relation-aware realisation. SportSett benefits in semantic coverage and narrative structure but remains difficult for overlap and external factuality metrics. E2E and DART often permit strong direct generation because their inputs are already close to the target proposition.

**RQ3: Which stages contribute?** Deterministic evidence and fact verification provide a factual backbone. Insight synthesis appears to add breadth and relational content. Writer quality revision reduces repetition and improves organisation. The audit layer provides traceability and repair, although its independent effect was not cleanly isolated in the ablation. Report-contract and structure inference are major contributors to ToTTo and SportSett success.

**RQ4: Is model strength sufficient?** No. Raw Pro is stronger than raw Flash, but the workflow still improves most metrics under Pro and corrects a ToTTo subject-linking error that Pro alone does not solve. Full Pro does not consistently beat Full Flash, and GPT-5.5 writing does not consistently improve the output. Architecture and model capability are complementary rather than interchangeable.

**Exploratory RQ5: Can LLM-only decomposition reduce hallucination risk?** On SportSett 4934, the LLM-only Flash system improved HHEM support over raw Flash and achieved perfect numeric source precision. It was substantially shorter and less reference-like, and required extensive schema tolerance and recovery logic. This suggests that claim decomposition and writer gating are useful controls, while deterministic evidence remains valuable for coverage and robustness.

## 15. Evaluation conclusion

The evaluation supports the central dissertation argument: an evidence-led multi-agent architecture can improve heterogeneous table-to-text generation beyond what is achieved by a direct generic LLM call. The improvement is most convincing where the system must understand the source's semantic structure and select a bounded communication target. The 25-example workflow achieved higher macro reference scores, substantially improved ToTTo outputs, reduced independent GPT-5.6 error counts, eliminated annotated omissions and numeric errors, and maintained complete internal support mapping.

The results do not support a claim of universal superiority. Direct models are highly competitive on simple attribute verbalisation, and stronger raw models narrow the gap. The workflow is slower and more operationally complex. It can trace a contextually incorrect claim to a valid number, and external factuality metrics can disagree sharply with internal provenance. Some benefits, especially narrative revision, are more visible to human inspection than to automatic overlap metrics.

The most defensible conclusion is therefore conditional. The architecture adds value through task inference, evidence selection, claim permissions, bounded insight synthesis and auditability. Its value grows with ambiguity and structural complexity. The next evaluation step should validate the GPT-5.6 taxonomy against human annotations, repeat clean ablations across multiple task families, and evaluate generic and task-matched baselines side by side. These additions would test whether the observed architecture advantage generalises beyond the selected examples and whether its factual controls align with human judgement.

## Appendix A. Complete main-experiment metric availability

| Metric | Records | Status |
| --- | ---: | --- |
| BLEU | 50 | Scored |
| chrF | 50 | Scored |
| TER | 50 | Scored |
| ROUGE-1 | 50 | Scored |
| ROUGE-2 | 50 | Scored |
| ROUGE-L | 50 | Scored |
| ROUGE-Lsum | 50 | Scored |
| METEOR | 50 | Scored |
| BERTScore F1 | 50 | Scored |
| Reference-context HHEM mean | 50 | Scored |
| Reference-context HHEM minimum | 50 | Scored |
| Reference-context HHEM unsupported rate | 50 | Scored |
| Reference-context AlignScore | 50 | Scored |
| Source-context HHEM mean | 50 | Scored |
| Source-context HHEM minimum | 50 | Scored |
| Source-context HHEM unsupported rate | 50 | Scored |
| Source-context AlignScore | 50 | Scored |
| PARENT precision | 20 skipped, 30 unavailable | Not usable |
| PARENT recall | 20 skipped, 30 unavailable | Not usable |
| PARENT F1 | 20 skipped, 30 unavailable | Not usable |
| Corpus BLEU | 10 | Scored by dataset and variant |
| Corpus chrF | 10 | Scored by dataset and variant |
| Corpus TER | 10 | Scored by dataset and variant |

## Appendix B. LLM judge coverage and status

| Judge artifact | Model | Outputs/records | Result |
| --- | --- | ---: | --- |
| Main DeepEval five-dataset batches | DeepSeek V4 Pro | 140 records | 137 scored, 3 invalid-JSON errors |
| SportSett latest seven-metric run | DeepSeek V4 Pro | 7 records | 7 scored |
| SportSett post-fix full-vs-raw run | DeepSeek V4 Pro | 14 records | 14 scored |
| SportSett source-grounded comparison | DeepSeek V4 Pro | 20 records | 15 scored, 5 errors |
| Source-grounded workflow/reference comparison | DeepSeek V4 Pro | 10 records | 10 scored |
| Main structured error annotations | GPT-5.6 Sol | 49 outputs | 49 scored |
| Repeated SportSett 4934 annotation | GPT-5.6 Sol | 1 output | Scored, 2 errors found |
| GPT-5.5-writer annotation attempt | GPT-5.6 Sol | 5 outputs | 5 failed due exhausted credits |

## Appendix C. Canonical artifact provenance

Main 25-example paired comparison:

```text
evaluation/generations/five_dataset_five_each_raw_generic_flash_20260805_181001_combined_generations.jsonl
evaluation/results/five_dataset_five_each_raw_generic_flash_20260805_181001_reference_metrics.jsonl
evaluation/results/five_dataset_five_each_raw_generic_flash_20260805_181001_source_grounded_metrics.jsonl
evaluation/results/five_dataset_five_each_raw_generic_flash_20260805_181001_summary.md
evaluation/results/five_dataset_results_appendix.md
```

Main DeepEval batches:

```text
evaluation/results/five_dataset_five_each_comparison_20260804_205019_sportsett_basketball_deepeval_metrics.jsonl
evaluation/results/five_dataset_five_each_comparison_20260804_230117_e2e_nlg_deepeval_metrics.jsonl
evaluation/results/five_dataset_five_each_comparison_20260804_231315_totto_deepeval_metrics.jsonl
evaluation/results/five_dataset_five_each_comparison_20260804_232653_web_nlg_deepeval_metrics.jsonl
evaluation/results/five_dataset_five_each_comparison_20260804_233348_dart_deepeval_metrics.jsonl
```

OpenAI structured judge:

```text
evaluation/results/openai_structured_error_annotations.jsonl
evaluation/results/sportsett_basketball_4934_full_system_openai_judge_annotations.jsonl
evaluation/results/five_dataset_flash_pipeline_gpt55_writer_openai_judge_annotations.jsonl
```

Ablation and generic-prompt studies:

```text
evaluation/generations/ablation_sportsett_4934_20260805_021058_combined_generations.jsonl
evaluation/results/ablation_sportsett_4934_20260805_021058_reference_metrics.jsonl
evaluation/results/sportsett_4934_ablation_story.md
evaluation/generations/generic_only_sportsett_basketball_4934_20260805_162215_generations.jsonl
evaluation/results/generic_only_sportsett_basketball_4934_20260805_162215_reference_metrics.jsonl
evaluation/generations/sportsett_basketball_4934_inferred_contract_deepseek-v4-flash_20260813_203625_generations.jsonl
evaluation/results/sportsett_basketball_4934_inferred_contract_deepseek-v4-flash_20260813_203625_reference_metrics.jsonl
```

Model comparisons:

```text
evaluation/generations/four_dataset_pro_comparison_20260812_215239_combined_generations.jsonl
evaluation/results/four_dataset_pro_comparison_20260812_215239_reference_metrics_combined.jsonl
evaluation/generations/sportsett_basketball_4934_fast_compare_generations.jsonl
evaluation/results/sportsett_basketball_4934_fast_reference_metrics_fixed.jsonl
evaluation/generations/five_dataset_flash_pipeline_gpt55_writer_generations.jsonl
evaluation/results/five_dataset_flash_pipeline_gpt55_writer_reference_metrics.jsonl
```

LLM-only experiment:

```text
LLM_ONLY_MULTIAGENT_EXPERIMENTATION_DOCUMENT.md
../table2text_pydanticai_experiment/evaluation/llm_only_runs_notebook_dataset/sportsett_basketball/814de3d5c33d2f7f.json
../table2text_pydanticai_experiment/evaluation/llm_only_runs_notebook_dataset_pro/sportsett_basketball/3fb04b6be798d06c.json
../table2text_pydanticai_experiment/evaluation/results/llm_only_pro_existing/sportsett_4934_selected_metric_comparison.csv
../table2text_pydanticai_experiment/evaluation/results/llm_only_pro_existing/sportsett_4934_generation_diagnostics_comparison.csv
```

## Appendix D. Complete main DeepEval score matrix

This appendix reports every score in the post-boundary five-dataset DeepEval batch. `ERR` means the judge call failed and no score was assigned. Blank dataset/variant combinations were not evaluated in this batch. The `raw_deepseek_v4_flash` condition is the earlier benchmark-aware baseline and is not the final `raw_generic_flash` condition used in the principal 25-pair comparison.

| Dataset/example | Variant | Faithfulness | Coherence | Factual correctness | Task relevance | Usefulness |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DART / dart-test-204 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| DART / dart-test-204 | raw_deepseek_v4_flash | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| DART / dart-test-217 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| DART / dart-test-217 | raw_deepseek_v4_flash | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| DART / dart-test-244 | full_system | 1.0000 | 0.9000 | 1.0000 | 1.0000 | 1.0000 |
| DART / dart-test-244 | raw_deepseek_v4_flash | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| DART / dart-test-260 | full_system | ERR | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| DART / dart-test-53 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| E2E / e2e_nlg-test-178 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| E2E / e2e_nlg-test-51 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| E2E / e2e_nlg-test-54 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| E2E / e2e_nlg-test-61 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| E2E / e2e_nlg-test-65 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| SportSett / 4934 | full_system | ERR | 0.9000 | 1.0000 | 1.0000 | 1.0000 |
| SportSett / 4934 | raw_deepseek_v4_flash | 0.8889 | 1.0000 | 0.9000 | 0.6000 | 0.9000 |
| SportSett / 4972 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9000 |
| SportSett / 4972 | raw_deepseek_v4_flash | 0.8947 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| SportSett / 4975 | raw_deepseek_v4_flash | 1.0000 | ERR | 1.0000 | 1.0000 | 1.0000 |
| SportSett / 4982 | full_system | 1.0000 | 0.8000 | 1.0000 | 1.0000 | 0.9000 |
| SportSett / 4982 | raw_deepseek_v4_flash | 0.9600 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| SportSett / 4986 | full_system | 0.9512 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| SportSett / 4986 | raw_deepseek_v4_flash | 0.9286 | 0.8000 | 1.0000 | 0.8000 | 0.9000 |
| ToTTo / totto-validation-204 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ToTTo / totto-validation-217 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ToTTo / totto-validation-244 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ToTTo / totto-validation-260 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| WebNLG / web_nlg_en-test-178 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| WebNLG / web_nlg_en-test-51 | full_system | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

The three `ERR` cells correspond to invalid JSON returned for DART 260 workflow faithfulness, SportSett 4934 workflow faithfulness and SportSett 4975 raw coherence. They are evaluation failures, not low generation scores.

## Appendix E. Complete later SportSett DeepEval score matrices

These tables retain every score from the later SportSett judge files. They are kept separate because the generated reports, contexts and metric configurations differ between runs.

### E.1 Source-grounded workflow/reference comparison

| Example | Variant | Faithfulness | Factual correctness | Task relevance | Coherence | Usefulness |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 4934 | full_system | 0.9091 | 1.0000 | 0.7000 | 1.0000 | 1.0000 |
| 4934 | human_reference_1 | 0.9375 | 0.0000 | 0.6000 | 0.9000 | 0.3000 |

### E.2 Latest seven-metric workflow run

| Example | Variant | Faithfulness | Summarization | Coherence | Factual correctness | Reference adequacy | Task relevance | Usefulness |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4934 | full_system | 1.0000 | 0.5333 | 0.9000 | 0.9000 | 0.4000 | 0.9000 | 0.5000 |

### E.3 Latest five-metric workflow comparison

| Example | Variant | Faithfulness | Factual correctness | Task relevance | Coherence | Usefulness |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 4934 | full_system | 0.9667 | 1.0000 | 0.8000 | 0.8000 | 0.7000 |

### E.4 Source-grounded four-output comparison

| Example | Variant | Faithfulness | Coherence | Factual correctness | Task relevance | Usefulness |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 4934 | full_system | ERR | 1.0000 | 1.0000 | 0.7000 | 1.0000 |
| 4934 | human_reference_1 | 0.9412 | 1.0000 | 0.2000 | 0.0000 | 0.3000 |
| 4934 | human_reference_2 | 0.9500 | ERR | ERR | ERR | ERR |
| 4934 | raw_deepseek_v4_pro | 1.0000 | 1.0000 | 1.0000 | 0.8000 | 0.7000 |

The full-system faithfulness call timed out. Four calls for `human_reference_2` also failed. The very low factual-correctness and task-relevance values assigned to `human_reference_1` illustrate that the reference included content or narrative expectations not recoverable from the source representation supplied to the judge.

### E.5 Post-fix seven-metric full/raw comparison

| Example | Variant | Faithfulness | Summarization | Coherence | Factual correctness | Reference adequacy | Task relevance | Usefulness |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4934 | full_system | 1.0000 | 0.8000 | 0.9000 | 1.0000 | 0.6000 | 1.0000 | 1.0000 |
| 4934 | raw_deepseek_v4_flash | 1.0000 | 0.3214 | 1.0000 | 0.9000 | 0.5000 | 1.0000 | 1.0000 |

## Appendix F. Complete non-zero GPT-5.6 Sol annotations

The main structured-annotation run returned an empty error list for 34 of the 49 scored outputs. The table below includes every non-zero annotation. Wording is retained from the structured judge output with only minor punctuation normalization for Markdown.

| Dataset/example | Variant | Count | Categories | Judge findings |
| --- | --- | ---: | --- | --- |
| SportSett / 4934 | full_system | 2 | CONTEXT, TASK/FORMAT | `Philadelphia entered with a 17-8 record...Memphis arrived at 13-9`: the totals match each team's game number, so the values are post-game records; `The entire report is presented as one paragraph`: the requested mode was multi-paragraph. |
| SportSett / 4934 | raw_generic_flash | 1 | TASK/FORMAT | The output is one paragraph with inline dash-separated items rather than the requested multi-paragraph report. |
| SportSett / 4972 | full_system | 2 | CONTEXT, TASK/FORMAT | `Milwaukee entered with a 13-5 record...Phoenix arrived at 4-14`: both totals equal 18 games and are post-game records; the report is serialized as one paragraph. |
| SportSett / 4972 | raw_generic_flash | 2 | CONTEXT, TASK/FORMAT | The 13-5 and 4-14 records are incorrectly presented as entry records; the output is a single inline list rather than multiple paragraphs. |
| SportSett / 4975 | raw_generic_flash | 1 | TASK/FORMAT | The response is an inline list rather than a multi-paragraph report. |
| SportSett / 4982 | full_system | 2 | CONTEXT, TASK/FORMAT | `Milwaukee entered...27-10...Atlanta entered at 11-27`: the records include the reported result and are post-game; the report is one paragraph. |
| SportSett / 4982 | raw_generic_flash | 2 | CONTEXT, TASK/FORMAT | The records and standings are framed as pre-game without support; the output is one paragraph with inline findings. |
| SportSett / 4986 | full_system | 2 | CONTEXT, TASK/FORMAT | `Milwaukee entered with a 34-12 record and Dallas with a 20-26 mark`: both are post-game records; the report is one paragraph. |
| SportSett / 4986 | raw_generic_flash | 1 | TASK/FORMAT | The output is a hyphen-separated list rather than a multi-paragraph report. |
| ToTTo / 204 | raw_generic_flash | 1 | TASK/FORMAT | The output has four sentences although the requested mode is one sentence. |
| ToTTo / 217 | raw_generic_flash | 4 | NUMBER, CONTEXT, OMISSION, TASK/FORMAT | The table has 24 officeholding entries but only 22 distinct mayors; Petr Zenkl interrupts the claimed Communist sequence; the highlighted Jan Koukal term is omitted; the response contains multiple bullet-like sentences rather than one sentence. |
| ToTTo / 244 | raw_generic_flash | 2 | TASK/FORMAT, OMISSION | The multi-bullet response violates the one-sentence mode and omits the highlighted George Keverian proposition. |
| ToTTo / 260 | raw_generic_flash | 3 | CONTEXT, OMISSION, TASK/FORMAT | The claim that the Swiss difference reflects taxes beyond a federal rate is unsupported; France's highlighted 34.43% rate is omitted; the response contains multiple bullet-style sentences. |
| ToTTo / 712 | raw_generic_flash | 1 | TASK/FORMAT | The output contains three sentences rather than one. |
| WebNLG / 178 | raw_generic_flash | 1 | NUMBER | The model adds the unit `minutes` to `230.05`, although the supplied source representation does not specify a unit. |

The separate repeated GPT-5.6 run on SportSett 4934 again returned two workflow errors: incorrect pre-game chronology for post-game records and failure to realize a multi-paragraph report. The five attempted GPT-5.5-writer annotations all failed because the API account had exhausted its credits; those failures provide no error-count evidence.

## Appendix G. Metric definitions, directions and evidential roles

This appendix makes explicit every evaluation measure referenced in the chapter. An ideal endpoint is included to clarify direction, but it is not a universal acceptance threshold. Scores from different metric families should not be averaged because they represent different constructs.

| Metric | Range or form | Ideal direction | What it measures | Evidential role and limitation |
| --- | --- | --- | --- | --- |
| BLEU | Usually 0-1 | Higher | Modified n-gram precision with a brevity penalty | Useful for conventional reference comparison; insensitive to many valid paraphrases and not a factuality measure |
| Corpus BLEU | Usually 0-1 | Higher | BLEU calculated over a dataset-level corpus | More stable than averaging sentence BLEU, but masks example-level failures |
| chrF | 0-1 | Higher | Character n-gram precision and recall | Particularly useful for names, numbers, morphology and short texts; still reference-dependent |
| Corpus chrF | 0-1 | Higher | chrF over all outputs in a dataset/variant | Provides dataset-level character overlap but does not reveal which examples failed |
| TER | 0 upward | Lower | Number of edits needed to transform output into a reference, normalized by reference length | Can exceed 1.0 and strongly penalizes over-generation; can favour an incomplete but short output |
| Corpus TER | 0 upward | Lower | Corpus-level translation edit rate | Useful as an aggregate edit burden, with the same brevity and reference limitations |
| ROUGE-1 | 0-1 | Higher | Unigram overlap with the reference | Indicates broad content-word overlap; does not establish correct relations |
| ROUGE-2 | 0-1 | Higher | Bigram overlap | More sensitive to local phrasing and ordering than ROUGE-1 |
| ROUGE-L | 0-1 | Higher | Longest-common-subsequence similarity | Captures ordering and sentence-level structure; can penalize valid reorganisation |
| ROUGE-Lsum | 0-1 | Higher | Summary-oriented ROUGE-L over sentence boundaries | Equal to ROUGE-L in the saved main runs because outputs and preprocessing did not produce a distinct summary segmentation |
| METEOR | 0-1 | Higher | Token alignment with precision, recall and flexible matching | More tolerant of lexical variation than BLEU, but remains reference-based |
| BERTScore F1 | Approximately 0-1 | Higher | Contextual embedding similarity between generated and reference tokens | Captures semantic paraphrase; may remain high when format, focus or a crucial number is wrong |
| PARENT precision | 0-1 | Higher | Intended precision relative to reference and table records | Not available in the main experiment because compatible table records/package support were missing |
| PARENT recall | 0-1 | Higher | Intended recall of reference/table-supported content | Same availability limitation |
| PARENT F1 | 0-1 | Higher | Harmonic mean of PARENT precision and recall | Same availability limitation; no PARENT values were imputed |
| AlignScore | 0-1 | Higher | Semantic alignment between generated text and an evaluation context | Meaning changes with context: reference-context alignment is not source factuality; long serialized sources can degrade matching |
| HHEM mean support | 0-1 | Higher | Mean local-model support probability across output sentences | Diagnostic sentence support, sensitive to sentence splitting and source serialization |
| HHEM minimum support | 0-1 | Higher | Lowest sentence-level support in an output | Highlights the weakest sentence and was the only source-grounded paired measure whose bootstrap interval excluded zero |
| HHEM unsupported sentence rate | 0-1 | Lower | Proportion of sentences below the configured support threshold | Easy to interpret, but a sentence splitter or inaccessible evidence can inflate it |
| Native audit support rate | 0-1 | Higher | Proportion of released sentences mapped to accepted internal facts/evidence | Measures provenance inside the workflow, not independent truth; a field can be mapped yet contextually misinterpreted |
| DeepEval faithfulness | 0-1 | Higher | LLM judgement of support against supplied evaluation context | Inspectable reason is useful; subject to judge bias, context construction and invalid-JSON failures |
| DeepEval summarization | 0-1 | Higher | LLM judgement of summary coverage and faithfulness | Used only in selected SportSett runs, so it is not a five-dataset aggregate |
| G-Eval coherence | 0-1 | Higher | Clarity, organisation and logical flow | Can reward a fluent output that uses the wrong required format |
| G-Eval factual correctness | 0-1 | Higher | Correctness of concrete statements against supplied context | Depends on whether the judge can locate evidence in the serialized source |
| G-Eval reference adequacy | 0-1 | Higher | Adequacy relative to reference expectations | Used only in later SportSett configurations and remains reference-sensitive |
| G-Eval task relevance | 0-1 | Higher | Fulfilment of the requested task and relevance of included material | Particularly useful for focused ToTTo and event-report format requirements |
| G-Eval usefulness | 0-1 | Higher | Practical informativeness for the intended task | A subjective semantic judgement with observed run-to-run variation |
| GPT-5.6 error count | Non-negative integer | Lower | Number of structured errors identified in one output | More interpretable than one scalar score, but requires human validation and category matching |
| GPT-5.6 error category | Categorical | Fewer substantive errors | NAME, NUMBER, WORD, CONTEXT, NOT CHECKABLE, OTHER, OMISSION or TASK/FORMAT | Reveals failure type; category frequencies should not be treated as equal-severity interval data |
| Generated-number source precision | 0-1 | Higher | Proportion of generated numeric values recoverable from source | Useful in the LLM-only case study, but does not test omitted numbers or incorrect narrative relations |
| Word count | Non-negative integer | Task-dependent | Output length | A diagnostic for coverage/compression, not an intrinsic quality score |
| Accepted claim count | Non-negative integer | Task-dependent | Number of claims admitted by the LLM-only adjudication stage | Helps explain coverage but says nothing alone about claim importance or correctness |

The primary dissertation story should rely on a small, complementary set rather than declaring one universal score: chrF and BERTScore for reference similarity, HHEM/AlignScore for source diagnostics, structured GPT-5.6 errors for concrete independent failures, native support for provenance, and human annotation for the eventual gold-standard assessment. BLEU, ROUGE, METEOR and TER remain useful secondary comparators because they expose precision, ordering and verbosity effects that the primary measures can conceal.

## Appendix H. Complete main-experiment aggregate metrics

### H.1 Reference-based and reference-context metrics

The first four factuality columns in this table use the human references as context, as configured by `external_factuality_context: references`. They measure compatibility with reference text and must not be read as direct source support.

| Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum | METEOR | BERTScore F1 | AlignScore (reference) | HHEM mean (reference) | HHEM minimum (reference) | HHEM unsupported rate (reference) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full system | 0.3595 | 0.5972 | 0.7161 | 0.7172 | 0.4641 | 0.5599 | 0.5599 | 0.5550 | 0.9246 | 0.6778 | 0.5772 | 0.5510 | 0.4578 |
| Raw generic Flash | 0.2383 | 0.4676 | 2.6303 | 0.5694 | 0.3585 | 0.4440 | 0.4440 | 0.4495 | 0.8965 | 0.5089 | 0.5309 | 0.5074 | 0.4667 |

### H.2 Source-context metrics

These values use `external_factuality_context: source_text` and therefore address source support rather than reference similarity.

| Variant | AlignScore (source) | HHEM mean (source) | HHEM minimum (source) | HHEM unsupported rate (source) |
| --- | ---: | ---: | ---: | ---: |
| Full system | 0.6784 | 0.5530 | 0.5396 | 0.3504 |
| Raw generic Flash | 0.6121 | 0.5437 | 0.4665 | 0.3460 |

### H.3 Corpus metrics

| Variant | Corpus BLEU | Corpus chrF | Corpus TER |
| --- | ---: | ---: | ---: |
| Full system | 0.3482 | 0.5961 | 0.8719 |
| Raw generic Flash | 0.2209 | 0.4601 | 2.8756 |

## Appendix I. Complete main metrics by dataset

### I.1 Reference-overlap and semantic metrics

| Dataset | Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum | METEOR | BERTScore F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DART | Full system | 0.1940 | 0.4918 | 0.8431 | 0.7075 | 0.4052 | 0.4789 | 0.4789 | 0.4600 | 0.9206 |
| DART | Raw generic Flash | 0.1580 | 0.4796 | 1.0942 | 0.6421 | 0.3845 | 0.4916 | 0.4916 | 0.4378 | 0.9186 |
| E2E | Full system | 0.6039 | 0.7631 | 0.4354 | 0.8582 | 0.6813 | 0.7398 | 0.7398 | 0.7970 | 0.9635 |
| E2E | Raw generic Flash | 0.5478 | 0.7439 | 0.4695 | 0.8428 | 0.6439 | 0.7364 | 0.7364 | 0.8006 | 0.9625 |
| SportSett | Full system | 0.0894 | 0.4143 | 0.9638 | 0.4688 | 0.1574 | 0.2251 | 0.2251 | 0.2537 | 0.8424 |
| SportSett | Raw generic Flash | 0.0422 | 0.2558 | 0.8133 | 0.3919 | 0.1532 | 0.2269 | 0.2269 | 0.1703 | 0.8296 |
| ToTTo | Full system | 0.3406 | 0.5674 | 0.8730 | 0.6789 | 0.4246 | 0.5856 | 0.5856 | 0.5652 | 0.9338 |
| ToTTo | Raw generic Flash | 0.0413 | 0.2021 | 10.0653 | 0.1835 | 0.0715 | 0.1311 | 0.1311 | 0.2266 | 0.8277 |
| WebNLG | Full system | 0.5696 | 0.7492 | 0.4651 | 0.8727 | 0.6521 | 0.7703 | 0.7703 | 0.6993 | 0.9624 |
| WebNLG | Raw generic Flash | 0.4022 | 0.6568 | 0.7094 | 0.7866 | 0.5393 | 0.6341 | 0.6341 | 0.6122 | 0.9440 |

### I.2 Reference-context AlignScore and HHEM by dataset

| Dataset | Variant | AlignScore | HHEM mean | HHEM minimum | HHEM unsupported rate |
| --- | --- | ---: | ---: | ---: | ---: |
| DART | Full system | 0.8785 | 0.8042 | 0.8042 | 0.2000 |
| DART | Raw generic Flash | 0.7177 | 0.8034 | 0.8034 | 0.2000 |
| E2E | Full system | 0.8352 | 0.8501 | 0.8501 | 0.2000 |
| E2E | Raw generic Flash | 0.9061 | 0.9229 | 0.9229 | 0.0000 |
| SportSett | Full system | 0.2269 | 0.1363 | 0.0067 | 0.8892 |
| SportSett | Raw generic Flash | 0.2583 | 0.0724 | 0.0402 | 1.0000 |
| ToTTo | Full system | 0.4687 | 0.3087 | 0.3087 | 0.8000 |
| ToTTo | Raw generic Flash | 0.0755 | 0.0939 | 0.0111 | 0.9333 |
| WebNLG | Full system | 0.9798 | 0.7868 | 0.7853 | 0.2000 |
| WebNLG | Raw generic Flash | 0.5870 | 0.7619 | 0.7596 | 0.2000 |

The same models behave differently when source text replaces references as context, as shown in Section 6. This confirms that the context choice is part of the metric definition rather than an incidental implementation detail.

## Appendix J. Complete metrics for secondary experiments

### J.1 Generic-request robustness on SportSett 4934

| Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum | METEOR | BERTScore F1 | AlignScore (reference) | HHEM mean | HHEM minimum | HHEM unsupported rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| First full-generic attempt | 0.0202 | 0.2961 | 2.7057 | 0.2619 | 0.0386 | 0.1186 | 0.1186 | 0.2215 | 0.8054 | 0.2860 | 0.0736 | 0.0070 | 0.9804 |
| First raw-generic comparison | 0.0592 | 0.2802 | 0.7958 | 0.3833 | 0.1381 | 0.2583 | 0.2583 | 0.2042 | 0.8376 | 0.2139 | 0.1097 | 0.0130 | 1.0000 |
| Full generic after fix | 0.1110 | 0.4507 | 0.9550 | 0.5246 | 0.1854 | 0.2385 | 0.2385 | 0.3054 | 0.8506 | 0.1774 | 0.0981 | 0.0126 | 1.0000 |
| Raw generic | 0.0755 | 0.2994 | 0.8198 | 0.3966 | 0.1713 | 0.2772 | 0.2772 | 0.1974 | 0.8414 | 0.2999 | 0.1195 | 0.0197 | 1.0000 |
| Saved full system on same example | 0.1232 | 0.4432 | 0.8438 | 0.5186 | 0.2049 | 0.2755 | 0.2755 | 0.2588 | 0.8671 | 0.2873 | 0.1964 | 0.0110 | 0.8333 |
| Saved raw-generic Flash on same example | 0.0302 | 0.2248 | 0.8108 | 0.3566 | 0.1453 | 0.2410 | 0.2410 | 0.1677 | 0.8144 | 0.3898 | 0.1423 | 0.0578 | 1.0000 |
| Exploratory inferred-contract Flash | 0.0754 | 0.3724 | 0.8649 | 0.4038 | 0.1093 | 0.2019 | 0.2019 | 0.2170 | 0.8315 | 0.2485 | 0.1018 | 0.0075 | 1.0000 |

The rows in this table come from several saved SportSett 4934 diagnostic artifacts. They are retained together so a writing model can see the full metric trail, but they should not be averaged into one experiment.

The overlap measures split: the workflow improves BLEU, chrF, ROUGE-1, ROUGE-2, METEOR and BERTScore, while raw generic improves TER, ROUGE-L and the local reference-context support measures. Because this configuration compares sentences with the reference rather than the source, the unsupported rate of 1.0 means that HHEM found neither long event report sufficiently entailed by the much shorter human reference. It is not evidence that every sentence was unsupported by the structured game record.

The exploratory inferred-contract row is not used as a replacement system. It confirms that source-structure task inference can select the correct event-report contract, but the full inferred-contract path was slower and weaker than the already selected full-generic workflow. Its main value is diagnostic: future work should reuse task-contract inference as a lightweight routing signal rather than routing large source-only event records through a heavier inferred-contract pipeline.

### J.2 Four-example DeepSeek model-strength comparison

| Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum | METEOR | BERTScore F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full Flash | 0.5485 | 0.6540 | 0.5841 | 0.7831 | 0.6376 | 0.6588 | 0.6588 | 0.6806 | 0.9461 |
| Raw generic Flash | 0.2964 | 0.5000 | 1.8733 | 0.5986 | 0.4048 | 0.4951 | 0.4951 | 0.5289 | 0.9225 |
| Full Pro | 0.4623 | 0.6449 | 0.5752 | 0.7760 | 0.6136 | 0.6926 | 0.6926 | 0.6629 | 0.9420 |
| Raw generic Pro | 0.3920 | 0.6334 | 0.7545 | 0.6898 | 0.5254 | 0.5804 | 0.5804 | 0.6394 | 0.9380 |

### J.3 SportSett 4934 all-Pro comparison

| Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum | METEOR | BERTScore F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full V4 Pro | 0.1337 | 0.4683 | 0.7958 | 0.5700 | 0.2192 | 0.3413 | 0.3413 | 0.2970 | 0.8839 |
| Raw V4 Pro | 0.1175 | 0.4305 | 0.8168 | 0.5371 | 0.2234 | 0.2898 | 0.2898 | 0.2586 | 0.8574 |

### J.4 Five matching examples with GPT-5.5 allocated only to the Writer

| Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum | METEOR | BERTScore F1 | AlignScore (reference) | HHEM mean | HHEM minimum | HHEM unsupported rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full Flash | 0.4634 | 0.6118 | 0.6360 | 0.7302 | 0.5510 | 0.5822 | 0.5822 | 0.5963 | 0.9303 | 0.7888 | 0.4859 | 0.4489 | 0.5667 |
| Raw generic Flash | 0.2431 | 0.4449 | 1.6608 | 0.5502 | 0.3529 | 0.4442 | 0.4442 | 0.4566 | 0.9008 | 0.6022 | 0.5254 | 0.4995 | 0.6000 |
| Flash pipeline with GPT-5.5 Writer | 0.3327 | 0.5609 | 0.7079 | 0.6729 | 0.4714 | 0.5384 | 0.5384 | 0.5076 | 0.9174 | 0.7248 | 0.4865 | 0.4596 | 0.5714 |

These are matched-example aggregates. The GPT-5.5 Writer condition falls between Full Flash and raw generic Flash on most reference measures, reinforcing the conclusion that replacing only the realisation model does not reproduce the full architectural advantage.

### J.5 SportSett 4934 stage ablation: every available reference metric

| Variant | chrF | TER | ROUGE-L | METEOR | BERTScore F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full system | 0.4432 | 0.8438 | 0.2755 | 0.2588 | 0.8671 |
| No insight synthesis | 0.3619 | 0.7808 | 0.2875 | 0.2470 | 0.8618 |
| No writer quality revision | 0.4145 | 0.8378 | 0.2577 | 0.2688 | 0.8545 |
| No audit repair rounds | 0.3290 | 1.4505 | 0.1442 | 0.2382 | 0.8082 |
| Original raw Flash row | 0.3825 | 0.8048 | 0.3299 | 0.2443 | 0.8489 |

The refreshed raw-generic values used in the narrative ablation table are a different saved output: chrF 0.225, TER 0.811, ROUGE-L 0.241, METEOR 0.168 and BERTScore 0.814. The two raw rows are intentionally not averaged.

### J.6 LLM-only multi-agent case-study diagnostics

#### J.6.1 Complete reference-similarity metrics

| Metric | Full system | Raw Flash | LLM-only Flash | LLM-only Pro |
| --- | ---: | ---: | ---: | ---: |
| AlignScore (reference) | 0.3986 | 0.3078 | n/a | n/a |
| BERTScore F1 | 0.8517 | 0.8504 | 0.8318 | 0.8548 |
| BLEU | 0.1071 | 0.1357 | 0.0363 | 0.0525 |
| chrF | 0.4166 | 0.3860 | 0.1835 | 0.2580 |
| Corpus BLEU | 0.1071 | 0.1357 | 0.0363 | 0.0525 |
| Corpus chrF | 0.4166 | 0.3860 | 0.1835 | 0.2580 |
| Corpus TER | 0.9099 | 0.8138 | 0.8559 | 0.8018 |
| HHEM mean support (reference) | 0.2690 | 0.2504 | n/a | n/a |
| HHEM minimum support (reference) | 0.0045 | 0.0062 | n/a | n/a |
| HHEM unsupported rate (reference) | 0.7368 | 0.7692 | n/a | n/a |
| METEOR | 0.2580 | 0.2534 | 0.1111 | 0.1584 |
| ROUGE-1 | 0.4715 | 0.5142 | 0.3206 | 0.4223 |
| ROUGE-2 | 0.1546 | 0.1898 | 0.1535 | 0.2195 |
| ROUGE-L | 0.2311 | 0.3214 | 0.2341 | 0.3058 |
| ROUGE-Lsum | 0.2311 | 0.3214 | 0.2341 | 0.3058 |
| TER | 0.9099 | 0.8138 | 0.8559 | 0.8018 |

#### J.6.2 Complete source-grounded metrics

| Metric | Full system | Raw Flash | LLM-only Flash | LLM-only Pro |
| --- | ---: | ---: | ---: | ---: |
| AlignScore (source) | 0.1908 | 0.1802 | n/a | n/a |
| HHEM mean support (source) | 0.2065 | 0.1662 | 0.2200 | 0.1808 |
| HHEM minimum support (source) | 0.0083 | 0.0113 | 0.0120 | 0.0083 |
| HHEM unsupported rate (source) | 0.7895 | 0.7692 | 0.7143 | 0.7500 |

#### J.6.3 Generation diagnostics

| Configuration | Accepted claims | Native audit support | Generated-number source precision | Words | Prompt tokens | Completion tokens | Total tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LLM-only Flash | 7 | 1.000 | 1.000 | 85 | 61,372 | 20,039 | 81,411 |
| LLM-only Pro | 9 | 1.000 | 1.000 | 106 | 61,446 | 19,178 | 80,624 |

Token counts are supplied for reproducibility and architectural interpretation, not as a principal dissertation outcome.

### J.7 Provenance-mismatched all-agent GPT-5.5 metric file

The following values are retained because the associated run is discussed in Section 10.3. They should not be used as a completed model-strength result: the generation file contained only one completed SportSett row while the metric file contained five dataset rows.

| Variant | BLEU | chrF | TER | ROUGE-1 | ROUGE-2 | ROUGE-L | ROUGE-Lsum | METEOR | BERTScore F1 | AlignScore (reference) | HHEM mean | HHEM minimum | HHEM unsupported rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Provenance-mismatched all-agent GPT-5.5 metric file | 0.4617 | 0.6219 | 0.6561 | 0.6865 | 0.5039 | 0.5937 | 0.5937 | 0.5814 | 0.9251 | 0.7634 | 0.5036 | 0.4695 | 0.5789 |

The same file also contained five scored rows each for corpus BLEU, corpus chrF and corpus TER, plus six skipped PARENT rows and nine unavailable PARENT rows. These status counts are preserved for provenance only.
