# Protected Holdout 25: Complete Results Evidence Bank

> Purpose: a result- and output-focused information bank from which a full dissertation evaluation chapter can be written. It preserves the protected experimental design, every measured score, every generated output, every reference, the normalized source supplied for each case, and all GPT-5.6 Sol structured annotations. It is not itself a polished chapter.

## 1. Evidence status

| Component | Status | Count | Evidence |
| --- | --- | --- | --- |
| Protected examples | Complete | 25 | 5 datasets x 5 examples |
| Full System outputs | Complete | 25 | One released output per example |
| Baseline outputs | Complete | 25 | One direct generic-call output per example |
| Paired outputs | Complete | 50 | 25 matched Full System/Baseline pairs |
| Reference metrics | Complete except PARENT | 630 | All configured observations retained, including unavailable statuses |
| Source-grounded metrics | Complete | 200 | AlignScore and three HHEM diagnostics for all 50 outputs |
| GPT-5.6 Sol structured annotations | Complete | 50 | One independent annotation per output |
| Human annotations on this protected set | Not collected | 0 | Do not describe GPT annotations as human gold labels |

### Core artifact paths

- [Protected selection](table2text_pydanticai/evaluation/protected_holdout_full_system/prepared/protected_selection_manifest.json)
- [Full System batch manifest](table2text_pydanticai/evaluation/protected_holdout_full_system/results/protected_batch_manifest.json)
- [Full System run summary](table2text_pydanticai/evaluation/protected_holdout_full_system/results/protected_generation_summary.csv)
- [Sealed paired generations](table2text_pydanticai/evaluation/protected_holdout_baseline/comparison/full_system_and_baseline_sealed.jsonl)
- [Reference-unsealed metrics copy](table2text_pydanticai/evaluation/protected_holdout_baseline/comparison/full_system_and_baseline_for_metrics.jsonl)
- [Reference metric observations](table2text_pydanticai/evaluation/protected_holdout_baseline/results/reference_alignment_metrics.jsonl)
- [Source-grounded metric observations](table2text_pydanticai/evaluation/protected_holdout_baseline/results/source_grounded_metrics.jsonl)
- [GPT-5.6 Sol annotations](table2text_pydanticai/evaluation/protected_holdout_baseline/gpt56_judge/results/gpt56_structured_annotations.jsonl)

## 2. Headline evidence

- Full System has the better direction-adjusted macro mean on all 13 scored per-example automatic metrics.
- Full System wins all 13 per-example metric families on DART and ToTTo.
- Baseline wins 10 of 13 per-example metric families on E2E; both conditions receive zero GPT-reported errors there.
- SportSett splits six metric families to each condition with one tie.
- GPT-5.6 Sol reports 16 errors for each condition; 18 Full System outputs and 14 Baseline outputs have zero reported errors.
- Full System native support rate is 1.0 for all 25 released outputs.
- PARENT produced no numerical scores and is not evidence for either condition.

## 3. Experimental design and isolation

| Property | Recorded value |
| --- | --- |
| Experiment | Protected Holdout Validation |
| Selection timestamp | 2026-08-21T00:28:22.944030+00:00 |
| Protected/unseen | Yes |
| Examples | 25 |
| Dataset allocation | {"dart": 5, "e2e_nlg": 5, "sportsett_basketball": 5, "totto": 5, "web_nlg": 5} |
| Historical overlap at selection | 0 |
| Frozen Git commit | 4a333a76702e6c056d8364dc212ce360d3fb1b92 |
| Frozen implementation SHA-256 | f525ca0c932819f533eab9229752a055a8e9c1acef8dea420bfa7e1e8b6b91fb |
| Full System configuration SHA-256 | 1fe2242bf777f26ada83114301c7c1fc11b6c25f613fa9d42e0b9484e4555d85 |
| Generation seed | 42 |
| Provider seed forwarded | No |
| Human references available during generation | No |
| Generations per condition per example | 1 |

### Conditions

| Condition | Model | Input request | Architecture | Reference access |
| --- | --- | --- | --- | --- |
| Full System | DeepSeek V4 Flash for all six roles | Benchmark task-specific request and explicit task contract | Six-role workflow with evidence, verification, Writer, support mapping, and audit | None during generation |
| Baseline | DeepSeek V4 Flash | Understand the supplied data and report its strongest supported findings. | One direct model call; no supplied task family or output-form metadata | None during generation |

The comparison deliberately tests whether the workflow can infer and enforce the appropriate communication task better than a direct generic call using the same model family. It does not isolate architecture from prompt specificity. Any dissertation claim must describe the treatment as the complete task-aware workflow, not as a pure agent-count ablation.

### Full System model-role configuration

| Role | Model |
| --- | --- |
| data_understanding | deepseek:deepseek-v4-flash |
| orchestrator | deepseek:deepseek-v4-flash |
| evidence | deepseek:deepseek-v4-flash |
| verifier | deepseek:deepseek-v4-flash |
| writer | deepseek:deepseek-v4-flash |
| auditor | deepseek:deepseek-v4-flash |

| Role | Temperature | Maximum tokens | Builder |
| --- | --- | --- | --- |
| data_understanding | 0.0000 | 7000 | build_data_understanding_agent |
| orchestrator | 0.1000 | 8000 | build_orchestrator_agent |
| evidence | 0.0000 | 9000 | build_evidence_agent |
| verifier | 0.0000 | 8000 | build_verifier_agent |
| evidence | 0.0000 | 8000 | build_insight_synthesis_agent |
| verifier | 0.0000 | 8000 | build_insight_verifier_agent |
| writer | 0.1500 | 11000 | build_writer_agent |
| auditor | 0.1000 | 12000 | build_auditor_agent |

### GPT-5.6 Sol annotation protocol

| Setting | Value |
| --- | --- |
| Judge | gpt-5.6-sol |
| Reasoning effort | high |
| Calls | 50 independent single-output calls |
| Human references supplied | No |
| Other condition output supplied | No |
| Condition identity supplied | No |
| Metric scores supplied | No |
| Common benchmark task context supplied | Yes |
| Taxonomy | NAME, NUMBER, WORD, CONTEXT, NOT CHECKABLE, OTHER, OMISSION, TASK/FORMAT |

## 4. Metric framework

| Class | Metrics | What the class contributes | Main limitation |
| --- | --- | --- | --- |
| Lexical/reference alignment | BLEU, chrF, METEOR, ROUGE, TER | Measures wording and content overlap with human references | Penalises valid paraphrase and different report lengths |
| Semantic reference alignment | BERTScore F1 | Measures contextual semantic similarity to references | High semantic similarity does not guarantee exact factuality |
| Table-aware alignment | PARENT | Intended to combine reference and table entailment | Unavailable in this run; no PARENT score can be claimed |
| Source-grounded diagnostics | AlignScore, HHEM | Tests support against normalized source rather than reference wording | Long structured inputs and model/context limits affect comparability |
| Independent structured review | GPT-5.6 Sol error annotations | Produces span-level categories and explanations | An LLM judgement, not a human gold standard |
| White-box workflow evidence | Support rate, support map, evidence/fact/insight counts, audit | Shows traceability and workflow behaviour | Available only for Full System and not an external quality score |

Recommended chapter emphasis: BERTScore, chrF, METEOR, AlignScore, the HHEM support diagnostics, and GPT-5.6's category-level annotations. BLEU, ROUGE, and TER remain useful secondary evidence. Corpus metrics should be labelled as dataset-level. PARENT must be reported as unavailable.

### Metric availability

| Metric | Status | Observations |
| --- | --- | --- |
| AlignScore (base) | scored | 50 |
| BERTScore F1 | scored | 50 |
| BLEU | scored | 50 |
| chrF | scored | 50 |
| Corpus BLEU | scored | 10 |
| Corpus chrF | scored | 10 |
| Corpus TER | scored | 10 |
| HHEM mean support | scored | 50 |
| HHEM minimum sentence support | scored | 50 |
| HHEM unsupported-sentence rate | scored | 50 |
| METEOR | scored | 50 |
| parent_f1 | skipped | 20 |
| parent_f1 | unavailable | 30 |
| parent_precision | skipped | 20 |
| parent_precision | unavailable | 30 |
| parent_recall | skipped | 20 |
| parent_recall | unavailable | 30 |
| ROUGE-1 | scored | 50 |
| ROUGE-2 | scored | 50 |
| ROUGE-L | scored | 50 |
| ROUGE-Lsum | scored | 50 |
| TER | scored | 50 |

PARENT generated no numerical results: 30 observations were unavailable because the optional KaijuML PARENT package was not installed, and 20 were skipped because the corresponding adapter did not expose a PARENT-compatible table. PARENT is therefore excluded from all comparative claims.

## 5. Overall automatic results

The adjusted difference is defined so that a positive value always favours Full System. For TER and HHEM unsupported-sentence rate, lower is better and the subtraction is reversed. The confidence interval is a descriptive 10,000-resample paired bootstrap over the 25 examples; it should not be treated as a substitute for a larger protected test set.

| Metric | Better direction | Baseline | Full System | Adjusted difference | Paired bootstrap 95% CI | Full/Tie/Base wins | Macro preference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.5819 | 0.7291 | 0.1472 | [0.0672, 0.2417] | 18/1/6 | Full System |
| BERTScore F1 | Higher | 0.9089 | 0.9239 | 0.0150 | [0.0061, 0.0253] | 16/1/8 | Full System |
| BLEU | Higher | 0.2455 | 0.3126 | 0.0671 | [0.0273, 0.1128] | 18/2/5 | Full System |
| chrF | Higher | 0.4931 | 0.5518 | 0.0587 | [0.0206, 0.0971] | 17/1/7 | Full System |
| HHEM mean support | Higher | 0.4953 | 0.5368 | 0.0415 | [-0.0173, 0.1099] | 12/1/12 | Full System |
| HHEM minimum sentence support | Higher | 0.4212 | 0.5261 | 0.1049 | [0.0315, 0.1918] | 14/1/10 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.4000 | 0.3200 | 0.0800 | [-0.0200, 0.2000] | 4/20/1 | Full System |
| METEOR | Higher | 0.4194 | 0.4595 | 0.0401 | [0.0040, 0.0783] | 13/2/10 | Full System |
| ROUGE-1 | Higher | 0.5847 | 0.6648 | 0.0801 | [0.0357, 0.1293] | 17/2/6 | Full System |
| ROUGE-2 | Higher | 0.3697 | 0.4188 | 0.0490 | [0.0107, 0.0895] | 16/1/8 | Full System |
| ROUGE-L | Higher | 0.4606 | 0.4967 | 0.0360 | [-0.0118, 0.0898] | 14/2/9 | Full System |
| ROUGE-Lsum | Higher | 0.4606 | 0.4967 | 0.0360 | [-0.0118, 0.0898] | 14/2/9 | Full System |
| TER | Lower | 1.6357 | 0.7742 | 0.8615 | [0.2333, 1.6437] | 12/6/7 | Full System |

The paired intervals exclude zero for AlignScore, BERTScore, BLEU, chrF, HHEM minimum sentence support, METEOR, ROUGE-1, ROUGE-2, and TER. They cross zero for HHEM mean support, HHEM unsupported-sentence rate, ROUGE-L, and ROUGE-Lsum. This pattern supports an overall alignment improvement while showing that not every grounding or sequence-overlap diagnostic is equally stable across the 25 cases.

### Corpus-level metrics by dataset

| Dataset | Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- | --- |
| dart | Corpus BLEU | Higher | 0.3657 | 0.5040 | 0.1383 | Full System |
| dart | Corpus chrF | Higher | 0.6598 | 0.6846 | 0.0249 | Full System |
| dart | Corpus TER | Lower | 0.8074 | 0.6289 | 0.1785 | Full System |
| e2e_nlg | Corpus BLEU | Higher | 0.2249 | 0.2808 | 0.0559 | Full System |
| e2e_nlg | Corpus chrF | Higher | 0.5070 | 0.4848 | -0.0222 | Baseline |
| e2e_nlg | Corpus TER | Lower | 1.5916 | 1.5288 | 0.0628 | Full System |
| sportsett_basketball | Corpus BLEU | Higher | 0.0626 | 0.0999 | 0.0373 | Full System |
| sportsett_basketball | Corpus chrF | Higher | 0.2997 | 0.4160 | 0.1163 | Full System |
| sportsett_basketball | Corpus TER | Lower | 0.8147 | 0.8598 | -0.0452 | Baseline |
| totto | Corpus BLEU | Higher | 0.0342 | 0.1120 | 0.0778 | Full System |
| totto | Corpus chrF | Higher | 0.2671 | 0.4179 | 0.1508 | Full System |
| totto | Corpus TER | Lower | 6.1727 | 1.5971 | 4.5755 | Full System |
| web_nlg | Corpus BLEU | Higher | 0.5286 | 0.5517 | 0.0231 | Full System |
| web_nlg | Corpus chrF | Higher | 0.6984 | 0.7006 | 0.0022 | Full System |
| web_nlg | Corpus TER | Lower | 0.5083 | 0.5083 | 0.0000 | Tie |

## 6. Results by dataset

### e2e_nlg

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9550 | 0.9694 | 0.0143 | Full System |
| BERTScore F1 | Higher | 0.9382 | 0.9374 | -0.0008 | Baseline |
| BLEU | Higher | 0.2745 | 0.2821 | 0.0076 | Full System |
| chrF | Higher | 0.5381 | 0.5083 | -0.0298 | Baseline |
| HHEM mean support | Higher | 0.5599 | 0.5512 | -0.0087 | Baseline |
| HHEM minimum sentence support | Higher | 0.5557 | 0.5512 | -0.0045 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.2000 | 0.2000 | 0.0000 | Tie |
| METEOR | Higher | 0.4476 | 0.4284 | -0.0191 | Baseline |
| ROUGE-1 | Higher | 0.7060 | 0.6874 | -0.0187 | Baseline |
| ROUGE-2 | Higher | 0.4629 | 0.4588 | -0.0040 | Baseline |
| ROUGE-L | Higher | 0.5051 | 0.4852 | -0.0199 | Baseline |
| ROUGE-Lsum | Higher | 0.5051 | 0.4852 | -0.0199 | Baseline |
| TER | Lower | 0.6318 | 0.6327 | -0.0009 | Baseline |

### web_nlg

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.8854 | 0.9518 | 0.0664 | Full System |
| BERTScore F1 | Higher | 0.9523 | 0.9607 | 0.0083 | Full System |
| BLEU | Higher | 0.4969 | 0.5876 | 0.0907 | Full System |
| chrF | Higher | 0.7044 | 0.7362 | 0.0318 | Full System |
| HHEM mean support | Higher | 0.8116 | 0.7425 | -0.0691 | Baseline |
| HHEM minimum sentence support | Higher | 0.7920 | 0.7425 | -0.0494 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.6339 | 0.6895 | 0.0556 | Full System |
| ROUGE-1 | Higher | 0.7792 | 0.8168 | 0.0376 | Full System |
| ROUGE-2 | Higher | 0.6128 | 0.6543 | 0.0415 | Full System |
| ROUGE-L | Higher | 0.7366 | 0.7152 | -0.0213 | Baseline |
| ROUGE-Lsum | Higher | 0.7366 | 0.7152 | -0.0213 | Baseline |
| TER | Lower | 0.5173 | 0.4313 | 0.0860 | Full System |

### dart

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.6908 | 0.8291 | 0.1382 | Full System |
| BERTScore F1 | Higher | 0.9470 | 0.9560 | 0.0090 | Full System |
| BLEU | Higher | 0.3534 | 0.4714 | 0.1180 | Full System |
| chrF | Higher | 0.6523 | 0.6799 | 0.0276 | Full System |
| HHEM mean support | Higher | 0.6490 | 0.7715 | 0.1225 | Full System |
| HHEM minimum sentence support | Higher | 0.5416 | 0.7452 | 0.2035 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.2000 | 0.0000 | 0.2000 | Full System |
| METEOR | Higher | 0.5591 | 0.6067 | 0.0475 | Full System |
| ROUGE-1 | Higher | 0.7443 | 0.8133 | 0.0691 | Full System |
| ROUGE-2 | Higher | 0.4915 | 0.5730 | 0.0816 | Full System |
| ROUGE-L | Higher | 0.5994 | 0.6200 | 0.0206 | Full System |
| ROUGE-Lsum | Higher | 0.5994 | 0.6200 | 0.0206 | Full System |
| TER | Lower | 0.7869 | 0.5839 | 0.2030 | Full System |

### totto

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.2693 | 0.7752 | 0.5059 | Full System |
| BERTScore F1 | Higher | 0.8679 | 0.9164 | 0.0485 | Full System |
| BLEU | Higher | 0.0414 | 0.1264 | 0.0849 | Full System |
| chrF | Higher | 0.2715 | 0.4195 | 0.1480 | Full System |
| HHEM mean support | Higher | 0.3897 | 0.5830 | 0.1933 | Full System |
| HHEM minimum sentence support | Higher | 0.2055 | 0.5830 | 0.3774 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.6000 | 0.4000 | 0.2000 | Full System |
| METEOR | Higher | 0.2727 | 0.3123 | 0.0396 | Full System |
| ROUGE-1 | Higher | 0.2624 | 0.5183 | 0.2559 | Full System |
| ROUGE-2 | Higher | 0.1149 | 0.2487 | 0.1338 | Full System |
| ROUGE-L | Higher | 0.2221 | 0.4333 | 0.2111 | Full System |
| ROUGE-Lsum | Higher | 0.2221 | 0.4333 | 0.2111 | Full System |
| TER | Lower | 5.4288 | 1.3626 | 4.0662 | Full System |

### sportsett_basketball

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.1091 | 0.1201 | 0.0111 | Full System |
| BERTScore F1 | Higher | 0.8388 | 0.8490 | 0.0101 | Full System |
| BLEU | Higher | 0.0612 | 0.0955 | 0.0343 | Full System |
| chrF | Higher | 0.2993 | 0.4151 | 0.1158 | Full System |
| HHEM mean support | Higher | 0.0661 | 0.0357 | -0.0304 | Baseline |
| HHEM minimum sentence support | Higher | 0.0110 | 0.0085 | -0.0025 | Baseline |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.1838 | 0.2606 | 0.0768 | Full System |
| ROUGE-1 | Higher | 0.4313 | 0.4881 | 0.0568 | Full System |
| ROUGE-2 | Higher | 0.1667 | 0.1590 | -0.0077 | Baseline |
| ROUGE-L | Higher | 0.2400 | 0.2296 | -0.0103 | Baseline |
| ROUGE-Lsum | Higher | 0.2400 | 0.2296 | -0.0103 | Baseline |
| TER | Lower | 0.8139 | 0.8608 | -0.0468 | Baseline |

## 7. GPT-5.6 Sol structured error results

| Condition | Outputs | Reported errors | Mean errors/output | Outputs with zero errors | Judge tokens |
| --- | --- | --- | --- | --- | --- |
| Baseline | 25 | 16 | 0.6400 | 14 | 67428 |
| Full System | 25 | 16 | 0.6400 | 18 | 69838 |

| Dataset | Condition | Outputs | Reported errors | Mean errors/output | Zero-error outputs |
| --- | --- | --- | --- | --- | --- |
| dart | Baseline | 5 | 0 | 0.0000 | 5 |
| dart | Full System | 5 | 0 | 0.0000 | 5 |
| e2e_nlg | Baseline | 5 | 0 | 0.0000 | 5 |
| e2e_nlg | Full System | 5 | 0 | 0.0000 | 5 |
| sportsett_basketball | Baseline | 5 | 7 | 1.4000 | 0 |
| sportsett_basketball | Full System | 5 | 13 | 2.6000 | 0 |
| totto | Baseline | 5 | 8 | 1.6000 | 0 |
| totto | Full System | 5 | 3 | 0.6000 | 3 |
| web_nlg | Baseline | 5 | 1 | 0.2000 | 4 |
| web_nlg | Full System | 5 | 0 | 0.0000 | 5 |

| Error category | Baseline | Full System |
| --- | --- | --- |
| NAME | 0 | 0 |
| NUMBER | 1 | 0 |
| WORD | 1 | 2 |
| CONTEXT | 2 | 6 |
| NOT CHECKABLE | 0 | 0 |
| OTHER | 0 | 0 |
| OMISSION | 1 | 2 |
| TASK/FORMAT | 11 | 6 |

| Paired outcome | Examples |
| --- | --- |
| Full System fewer GPT-reported errors | 5 |
| Equal error count | 15 |
| Full System more GPT-reported errors | 5 |

The taxonomy clarifies the equal totals. Baseline's errors were dominated by TASK/FORMAT violations (11), particularly generic responses that ignored ToTTo's highlighted-cell restriction or SportSett's multi-paragraph form. Full System reduced TASK/FORMAT errors to six but increased CONTEXT errors from two to six, all concentrated in the event-report setting. No NAME, NOT CHECKABLE, or OTHER errors were reported for either condition.

These annotations should be described as GPT-5.6 Sol judgements. They are useful diagnostic evidence but cannot establish human precision or recall until checked against independent human annotations. Some annotations are strict, such as treating omission of a full birth date as a NUMBER error, so category totals should be read with the included explanations.

## 8. Output length and qualitative form

| Dataset | Condition | Mean words | Median | Minimum | Maximum |
| --- | --- | --- | --- | --- | --- |
| dart | Baseline | 33.0000 | 28.0000 | 20 | 61 |
| dart | Full System | 25.4000 | 20.0000 | 14 | 44 |
| e2e_nlg | Baseline | 19.2000 | 19.0000 | 11 | 28 |
| e2e_nlg | Full System | 18.0000 | 19.0000 | 9 | 26 |
| sportsett_basketball | Baseline | 159.4000 | 173.0000 | 120 | 197 |
| sportsett_basketball | Full System | 292.6000 | 299.0000 | 219 | 334 |
| totto | Baseline | 62.4000 | 60.0000 | 30 | 92 |
| totto | Full System | 18.0000 | 17.0000 | 9 | 26 |
| web_nlg | Baseline | 17.2000 | 14.0000 | 6 | 29 |
| web_nlg | Full System | 16.2000 | 14.0000 | 6 | 28 |

Full System was much longer on SportSett (292.6 versus 159.4 mean words) but far shorter on ToTTo (18.0 versus 62.4). This is not a uniform verbosity effect. It reflects genre control: expansion for event reports and compression for highlighted-cell descriptions. The ToTTo change aligns with large metric and judge improvements. The SportSett expansion improves coverage and several reference metrics but creates more opportunities for contextual interpretation errors.

## 9. Full System provenance and execution evidence

| Recorded property | Result |
| --- | --- |
| Successful protected executions | 25 |
| Primary-evaluation eligible | 25 |
| Approved | 5 |
| Approved with warnings | 20 |
| Mean native support rate | 1.0000 |
| Unsupported factual sentences | 0 |
| Normal LLM Writer path | 20 |
| Auditor-repaired path | 2 |
| Deterministic fallback path | 3 |
| Evidence items | 228 |
| Verified facts | 224 |
| Rejected facts | 5 |
| Verified insights | 22 |
| Rejected insights | 21 |

All 25 outputs passed the internal audit with complete mapped support, and no invalid fact or evidence identifiers were recorded. This supports a claim of successful provenance enforcement. It does not support a claim of zero factual error, because the independent judge still found contextual and task-level issues.

### Evidence, facts, and insights by dataset

| Dataset | Evidence items | Fact candidates | Verified facts | Rejected facts | Insight candidates | Verified insights | Rejected insights |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dart | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| e2e_nlg | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| sportsett_basketball | 208 | 209 | 204 | 5 | 43 | 22 | 21 |
| totto | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| web_nlg | 5 | 5 | 5 | 0 | 0 | 0 | 0 |

### Operational footprint (secondary evidence)

| Condition | Provider-reported requests | Provider-reported tokens | Elapsed seconds |
| --- | --- | --- | --- |
| Full System | 89 | 3299965 | 5413.9388 |
| Baseline | 25 | 54558 | 83.7314 |

Runtime and token use are retained for reproducibility, not treated as the main evaluation outcome. The conditions differ by orders of magnitude in computation, particularly on SportSett. This makes it important to present quality gains alongside the operational trade-off, without reducing the dissertation to a cost study.

| Stage | Requests | Input tokens | Output tokens | Total tokens |
| --- | --- | --- | --- | --- |
| initial_audit_and_repair | 5 | 469044 | 56394 | 525438 |
| verifier.insight_verification | 5 | 378114 | 59769 | 437883 |
| fact_verification | 5 | 271806 | 86035 | 357841 |
| evidence_synthesis | 5 | 272155 | 59876 | 332031 |
| data_understanding | 8 | 131494 | 172117 | 303611 |
| evidence.insight_synthesis | 5 | 209997 | 61768 | 271765 |
| natural_writer | 26 | 222889 | 43786 | 266675 |
| writer_quality_revision | 4 | 201524 | 47081 | 248605 |
| post_repair_audit_round_1 | 2 | 186421 | 17607 | 204028 |
| verifier.insight_verification.retry.002 | 6 | 89128 | 14192 | 103320 |
| verifier.insight_verification.retry.003 | 5 | 64918 | 9572 | 74490 |
| verifier.insight_verification.retry.001 | 6 | 58131 | 9620 | 67751 |
| verifier.insight_verification.retry.004 | 3 | 44127 | 10422 | 54549 |
| verifier.insight_verification.retry.007 | 1 | 20229 | 1087 | 21316 |
| verifier.insight_verification.retry.005 | 2 | 10583 | 6602 | 17185 |
| verifier.insight_verification.retry.006 | 1 | 11575 | 1902 | 13477 |

## 10. Evidence-use notes

- Positive adjusted differences favour Full System; TER and unsupported-sentence rate are reversed because lower is better.
- The protected sample contains five examples per dataset and one generation per condition.
- The treatment is the complete task-aware workflow; the comparison does not isolate architecture from prompt specificity.
- GPT-5.6 Sol annotations are model judgements, not human gold labels.
- Native support rate is Full System-only provenance evidence, not a paired quality metric.
- PARENT was unavailable and must not be presented as a scored result.

# Appendix A. Complete case-level evidence

Each case below contains the normalized source presented to both conditions, the task-specific Full System request, the generic Baseline request, all human references (unsealed only after generation), both outputs, per-output metrics, GPT-5.6 Sol annotations, and Full System provenance statistics.

## A1. e2e_nlg / e2e_nlg-test-1330

| Field | Value |
| --- | --- |
| Dataset | e2e_nlg |
| Example ID | e2e_nlg-test-1330 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 9e8fb57080429c1e645ec58eeb3803675a8038d04638e3801c08fece45ea4cfc |
| Reference SHA-256 | bf634ba957a0a8228c44057960a6512c941e7510853f54028f6e436b4c50b29f |
| Full System request | Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
name[The Vaults], eatType[pub], food[Italian], customer rating[3 out of 5], area[city centre], familyFriendly[yes], near[Rainbow Vegetarian Café]
````

### Human reference outputs

**Reference 1**

````text
Near Rainbow Vegetarian Café in the centre of the city is The Vaults. An Italian food pub, it is family-friendly with ratings of 3 out of 5 by the customers and is priced moderate.
````

**Reference 2**

````text
The Vaults, an Italian pub, is rated 3 out of 5 by customers and is kid friendly. It is located neat Rainbow Vegetarian Café in the city centre.
````

### Full System output

````markdown
The Vaults is a family-friendly pub in the city centre serving Italian food, with a customer rating of 3 out of 5, near Rainbow Vegetarian Café.
````

### Baseline output

````markdown
The Vaults is a city-centre pub serving Italian food, with a customer rating of 3 out of 5. It is family friendly and located near Rainbow Vegetarian Café.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9586 | 0.9780 | 0.0195 | Full System |
| BERTScore F1 | Higher | 0.9459 | 0.9451 | -0.0008 | Baseline |
| BLEU | Higher | 0.2275 | 0.2696 | 0.0421 | Full System |
| chrF | Higher | 0.5365 | 0.5419 | 0.0055 | Full System |
| HHEM mean support | Higher | 0.6725 | 0.5715 | -0.1011 | Baseline |
| HHEM minimum sentence support | Higher | 0.6515 | 0.5715 | -0.0800 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.4206 | 0.4618 | 0.0413 | Full System |
| ROUGE-1 | Higher | 0.7813 | 0.7742 | -0.0071 | Baseline |
| ROUGE-2 | Higher | 0.4194 | 0.4333 | 0.0140 | Full System |
| ROUGE-L | Higher | 0.4912 | 0.4000 | -0.0912 | Baseline |
| ROUGE-Lsum | Higher | 0.4912 | 0.4000 | -0.0912 | Baseline |
| TER | Lower | 0.7419 | 0.6774 | 0.0645 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T002823Z_9b23675387 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 26 |
| Baseline words | 28 |
| Full System elapsed seconds | 25.7671 |
| Baseline elapsed seconds | 1.6728 |
| Full System provider-reported tokens | 7778 |
| Baseline provider-reported tokens | 297 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/e2e_nlg__e2e_nlg-test-1330/full_system/e2e_nlg/20260821T002823Z_9b23675387/pipeline_result.json |

## A2. web_nlg / web_nlg_en-test-1209

| Field | Value |
| --- | --- |
| Dataset | web_nlg |
| Example ID | web_nlg_en-test-1209 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | a413a081e355b67874e04f93ab59ee7b33bd20c885e0574a724090f7fe1a163b |
| Reference SHA-256 | 2c8538c423f63fce8e472bfb22f4b2c28bc8595bb9c2016f9d0728cde2b8995e |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Piotr_Hallmann | birthPlace | Gdynia,_Poland
Gdynia,_Poland | timeZone | Central_European_Time
Gdynia,_Poland | timeZone | Central_European_Summer_Time
Piotr_Hallmann | height | 175.26
````

### Human reference outputs

**Reference 1**

````text
Piotr Hallmann was born in Gdynia, Poland, which is in Central European summer time. He is 175.26 cm. tall.
````

**Reference 2**

````text
175.26 cm tall Piotr Hallmann is from the town of Gdynia in Poland. This town follows the Central European Summertime timezone.
````

**Reference 3**

````text
Piotr Hallmann was born in Gdynia, Poland, whose time zone is Central European Summer Time. Hallmann’s height is 175.26 cm.
````

### Full System output

````markdown
Piotr Hallmann was born in Gdynia, Poland, which uses Central European Time and Central European Summer Time, and has a height of 175.26.
````

### Baseline output

````markdown
Piotr Hallmann was born in Gdynia, Poland. Gdynia uses Central European Time and Central European Summer Time. Piotr Hallmann's height is listed as 175.26.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9094 | 0.9670 | 0.0576 | Full System |
| BERTScore F1 | Higher | 0.9494 | 0.9555 | 0.0061 | Full System |
| BLEU | Higher | 0.4162 | 0.4501 | 0.0339 | Full System |
| chrF | Higher | 0.6811 | 0.6457 | -0.0353 | Baseline |
| HHEM mean support | Higher | 0.8467 | 0.6631 | -0.1836 | Baseline |
| HHEM minimum sentence support | Higher | 0.7485 | 0.6631 | -0.0853 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.6191 | 0.5802 | -0.0389 | Baseline |
| ROUGE-1 | Higher | 0.7500 | 0.6522 | -0.0978 | Baseline |
| ROUGE-2 | Higher | 0.5652 | 0.5238 | -0.0414 | Baseline |
| ROUGE-L | Higher | 0.7500 | 0.6522 | -0.0978 | Baseline |
| ROUGE-Lsum | Higher | 0.7500 | 0.6522 | -0.0978 | Baseline |
| TER | Lower | 0.6000 | 0.6000 | 0.0000 | Tie |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T002848Z_b1ed943cf4 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 23 |
| Baseline words | 24 |
| Full System elapsed seconds | 12.7095 |
| Baseline elapsed seconds | 1.8024 |
| Full System provider-reported tokens | 6806 |
| Baseline provider-reported tokens | 360 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/web_nlg__web_nlg_en-test-1209/full_system/web_nlg/20260821T002848Z_b1ed943cf4/pipeline_result.json |

## A3. dart / dart-test-1791

| Field | Value |
| --- | --- |
| Dataset | dart |
| Example ID | dart-test-1791 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 20a5eccd67eb73bbf6f37ec51941e57ad416c4faa691d2cc277daf07d08e88d4 |
| Reference SHA-256 | af602b3a77c5ee0df21a0b25b33a21eac28b98a21cd8922ee4fd59c0c260ee96 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Elliot See | ALMA_MATER | University of Texas at Austin
Elliot See | DEATH_PLACE | St. Louis
Elliot See | WAS_SELECTED_BY_NASA | 1962
````

### Human reference outputs

**Reference 1**

````text
Elliot See, who graduated from the University of Texas at Austin and was chosen by NASA in 1962, died in St. Louis.
````

**Reference 2**

````text
Elliot See who was selected by NASA in 1962, attended the University of Texas at Austin and died in St Louis.
````

**Reference 3**

````text
Elliot See, who graduated from the University of Texas in Austin and was chosen by NASA in 1962, has died in St Louis.
````

### Full System output

````markdown
Elliot See attended the University of Texas at Austin, died in St.
Louis, and was selected by NASA in 1962.
````

### Baseline output

````markdown
Elliot See attended the University of Texas at Austin, was selected by NASA in 1962, and died in St. Louis.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9581 | 0.9824 | 0.0243 | Full System |
| BERTScore F1 | Higher | 0.9716 | 0.9679 | -0.0037 | Baseline |
| BLEU | Higher | 0.7532 | 0.6850 | -0.0682 | Baseline |
| chrF | Higher | 0.8592 | 0.8043 | -0.0549 | Baseline |
| HHEM mean support | Higher | 0.4858 | 0.6566 | 0.1708 | Full System |
| HHEM minimum sentence support | Higher | 0.3632 | 0.6548 | 0.2917 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.5000 | 0.0000 | 0.5000 | Full System |
| METEOR | Higher | 0.8520 | 0.7335 | -0.1185 | Baseline |
| ROUGE-1 | Higher | 0.9756 | 0.9756 | 0.0000 | Tie |
| ROUGE-2 | Higher | 0.8205 | 0.7692 | -0.0513 | Baseline |
| ROUGE-L | Higher | 0.8095 | 0.6667 | -0.1429 | Baseline |
| ROUGE-Lsum | Higher | 0.8095 | 0.6667 | -0.1429 | Baseline |
| TER | Lower | 0.1818 | 0.3636 | -0.1818 | Baseline |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T002901Z_5a8c24f4e7 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 20 |
| Baseline words | 20 |
| Full System elapsed seconds | 9.7589 |
| Baseline elapsed seconds | 1.7031 |
| Full System provider-reported tokens | 6290 |
| Baseline provider-reported tokens | 298 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/dart__dart-test-1791/full_system/dart/20260821T002901Z_5a8c24f4e7/pipeline_result.json |

## A4. totto / totto-validation-1828

| Field | Value |
| --- | --- |
| Dataset | totto |
| Example ID | totto-validation-1828 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source SHA-256 | 4f01b0f2d1a2e944dc9c88cbc4ea7035f7f57569055cd98fd963a9f717fd3a40 |
| Reference SHA-256 | 13f4d6ba14f2d8846ae5d47990ba0abea068972dc688c623d49d9dd967b01b34 |
| Full System request | Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Page: Lasse Staw
Section: Career statistics
Table:
Club | Season | Division | League | Cup | Total
Apps | Goals | Apps | Goals | Apps | Goals
2004 | Fredrikstad | Tippeligaen | 1 | 0 | 0 | 0 | 1 | 0
2005 | 0 | 0 | 0 | 0 | 0 | 0
2006 | 4 | 0 | 0 | 0 | 3 | 0
2007 | 4 | 0 | 1 | 0 | 5 | 0
2008 | 11 | 0 | 1 | 0 | 12 | 0
2009 | 15 | 0 | 2 | 0 | 17 | 0
2010 | Adeccoligaen | 18 | 0 | 2 | 0 | 20 | 0
2011 | Tippeligaen | 22 | 0 | 1 | 0 | 23 | 0
*2012* | *Syrianska* | *Allsvenskan* | 8 | 0 | 0 | 0 | 8 | 0
2012 | Lillestrøm | Tippeligaen | 2 | 0 | 0 | 0 | 2 | 0
2013 | Aalesund | 0 | 0 | 2 | 0 | 2 | 0
2014 | Bodø/Glimt | 14 | 0 | 4 | 0 | 18 | 0
2015 | 9 | 0 | 1 | 0 | 10 | 0
Career Total | 108 | 0 | 14 | 0 | 122 | 0
Cells surrounded by * are highlighted.
````

### Human reference outputs

**Reference 1**

````text
In 2012, Staw had signed with Allsvenskan club Syrianska.
````

**Reference 2**

````text
In 2012, Lasse Staw moved to Allsvenskan club Syrianska FC.
````

**Reference 3**

````text
In 2012, Staw signed with Allsvenskan club Syrianska FC.
````

### Full System output

````markdown
The selected table value is 2012, Syrianska, Allsvenskan under the Career Total header in the row containing 8 and 0, within Career statistics / Lasse Staw.
````

### Baseline output

````markdown
Lasse Staw’s career statistics show that he never scored a goal in any recorded competition: across all clubs and seasons he made 108 league appearances, 14 cup appearances, and 122 total appearances, all with 0 goals. His most productive season by appearances was 2011 with Fredrikstad in Tippeligaen (22 league apps, 1 cup app, 23 total). He played for Fredrikstad (2004–2011), Syrianska (2012), Lillestrøm (2012), Aalesund (2013), and Bodø/Glimt (2014–2015). His highest league-appearance totals were 22 in 2011 and 18 in 2010.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.4371 | 0.7334 | 0.2963 | Full System |
| BERTScore F1 | Higher | 0.8213 | 0.8787 | 0.0575 | Full System |
| BLEU | Higher | 0.0051 | 0.0404 | 0.0353 | Full System |
| chrF | Higher | 0.1498 | 0.3862 | 0.2364 | Full System |
| HHEM mean support | Higher | 0.2123 | 0.7993 | 0.5870 | Full System |
| HHEM minimum sentence support | Higher | 0.0581 | 0.7993 | 0.7412 | Full System |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 0.0000 | 1.0000 | Full System |
| METEOR | Higher | 0.1227 | 0.1724 | 0.0497 | Full System |
| ROUGE-1 | Higher | 0.1237 | 0.3429 | 0.2191 | Full System |
| ROUGE-2 | Higher | 0.0208 | 0.0606 | 0.0398 | Full System |
| ROUGE-L | Higher | 0.0816 | 0.1714 | 0.0898 | Full System |
| ROUGE-Lsum | Higher | 0.0816 | 0.1714 | 0.0898 | Full System |
| TER | Lower | 8.4643 | 2.6786 | 5.7857 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

1. **WORD**
   - Error span: under the Career Total header
   - Correction or explanation: The highlighted 2012, Syrianska, and Allsvenskan cells are not under a Career Total header; Career Total is a separate row label.
2. **TASK/FORMAT**
   - Error span: in the row containing 8 and 0, within Career statistics / Lasse Staw
   - Correction or explanation: The task asks only for a concise description of the highlighted cells, so references to unhighlighted values and surrounding page/section metadata are outside the requested scope.

**Baseline**

1. **TASK/FORMAT**
   - Error span: The generated output consists of four sentences.
   - Correction or explanation: The request requires exactly one concise sentence.
2. **TASK/FORMAT**
   - Error span: Lasse Staw’s career statistics show that he never scored... His highest league-appearance totals were 22 in 2011 and 18 in 2010.
   - Correction or explanation: Most of the output discusses unhighlighted career totals, seasons, clubs, and appearance figures; it should describe only the highlighted cells.
3. **OMISSION**
   - Error span: Allsvenskan
   - Correction or explanation: The highlighted division, Allsvenskan, is omitted; the highlighted cells indicate 2012, Syrianska, and Allsvenskan.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T002911Z_531f6f3190 |
| Execution outcome | success |
| Final generation path | deterministic_fallback |
| Final Writer mode | deterministic_short_form_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 26 |
| Baseline words | 82 |
| Full System elapsed seconds | 23.1703 |
| Baseline elapsed seconds | 3.1390 |
| Full System provider-reported tokens | 8801 |
| Baseline provider-reported tokens | 843 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/totto__totto-validation-1828/full_system/totto/20260821T002911Z_531f6f3190/pipeline_result.json |

## A5. sportsett_basketball / 5130

| Field | Value |
| --- | --- |
| Dataset | sportsett_basketball |
| Example ID | 5130 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source SHA-256 | 432bc48818396a9345adffd433b22b1710c709c30e18a4f6935c3464b65c8e2f |
| Reference SHA-256 | 2c74673beb1cb0b6c4b079762408b342913c08ad6f7271c4c7229717fcc6eb27 |
| Full System request | Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````json
{
  "game": {
    "attendance": "16600",
    "capacity": "19000",
    "city": "Los Angeles",
    "day": "5",
    "dayname": "Monday",
    "game_id": "5130",
    "month": "November",
    "season": "2018",
    "stadium": "Staples Center",
    "state": "California",
    "year": "2018"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "7",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "10",
          "FGM": "4",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "38",
          "OREB": "2",
          "PF": "5",
          "PTS": "10",
          "STL": "0",
          "TOV": "0",
          "TREB": "6",
          "first_name": "Patrick",
          "last_name": "Beverley",
          "name": "Patrick Beverley",
          "starter": "True"
        },
        {
          "+/-": "7",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "9",
          "FG3A": "7",
          "FG3M": "4",
          "FG3_PCT": "57",
          "FGA": "16",
          "FGM": "8",
          "FG_PCT": "50",
          "FTA": "3",
          "FTM": "2",
          "FT_PCT": "67",
          "MIN": "34",
          "OREB": "1",
          "PF": "2",
          "PTS": "22",
          "STL": "1",
          "TOV": "1",
          "TREB": "10",
          "first_name": "Tobias",
          "last_name": "Harris",
          "name": "Tobias Harris",
          "starter": "True"
        },
        {
          "+/-": "0",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "16",
          "FGM": "7",
          "FG_PCT": "44",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "31",
          "OREB": "0",
          "PF": "5",
          "PTS": "22",
          "STL": "0",
          "TOV": "2",
          "TREB": "4",
          "first_name": "Danilo",
          "last_name": "Gallinari",
          "name": "Danilo Gallinari",
          "starter": "True"
        },
        {
          "+/-": "7",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "6",
          "FGM": "2",
          "FG_PCT": "33",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "24",
          "OREB": "2",
          "PF": "2",
          "PTS": "6",
          "STL": "1",
          "TOV": "2",
          "TREB": "3",
          "first_name": "Shai",
          "last_name": "Gilgeous-Alexander",
          "name": "Shai Gilgeous-Alexander",
          "starter": "True"
        },
        {
          "+/-": "2",
          "AST": "2",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "3",
          "FG_PCT": "38",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "17",
          "OREB": "4",
          "PF": "3",
          "PTS": "10",
          "STL": "0",
          "TOV": "1",
          "TREB": "9",
          "first_name": "Boban",
          "last_name": "Marjanović",
          "name": "Boban Marjanović",
          "starter": "True"
        },
        {
          "+/-": "9",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "7",
          "FGM": "6",
          "FG_PCT": "86",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "30",
          "OREB": "4",
          "PF": "1",
          "PTS": "13",
          "STL": "3",
          "TOV": "4",
          "TREB": "7",
          "first_name": "Montrezl",
          "last_name": "Harrell",
          "name": "Montrezl Harrell",
          "starter": "False"
        },
        {
          "+/-": "8",
          "AST": "6",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "17",
          "FGM": "7",
          "FG_PCT": "41",
          "FTA": "5",
          "FTM": "5",
          "FT_PCT": "100",
          "MIN": "27",
          "OREB": "0",
          "PF": "1",
          "PTS": "20",
          "STL": "0",
          "TOV": "1",
          "TREB": "0",
          "first_name": "Lou",
          "last_name": "Williams",
          "name": "Lou Williams",
          "starter": "False"
        },
        {
          "+/-": "11",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "4",
          "FGM": "3",
          "FG_PCT": "75",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "16",
          "OREB": "0",
          "PF": "3",
          "PTS": "8",
          "STL": "0",
          "TOV": "0",
          "TREB": "4",
          "first_name": "Mike",
          "last_name": "Scott",
          "name": "Mike Scott",
          "starter": "False"
        },
        {
          "+/-": "3",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "1",
          "FG3M": "1",
          "FG3_PCT": "100",
          "FGA": "1",
          "FGM": "1",
          "FG_PCT": "100",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "11",
          "OREB": "0",
          "PF": "3",
          "PTS": "3",
          "STL": "0",
          "TOV": "1",
          "TREB": "0",
          "first_name": "Miloš",
          "last_name": "Teodosić",
          "name": "Miloš Teodosić",
          "starter": "False"
        },
        {
          "+/-": "1",
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
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "6",
          "OREB": "0",
          "PF": "2",
          "PTS": "6",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Jerome",
          "last_name": "Robinson",
          "name": "Jerome Robinson",
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
          "first_name": "Marcin",
          "last_name": "Gortat",
          "name": "Marcin Gortat",
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
          "first_name": "Sindarius",
          "last_name": "Thornwell",
          "name": "Sindarius Thornwell",
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
          "first_name": "Tyrone",
          "last_name": "Wallace",
          "name": "Tyrone Wallace",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 5,
      "division": "Pacific",
      "game_number": "10",
      "line_score": {
        "H1": {
          "AST": "109",
          "BLK": "20",
          "DREB": "69",
          "FG3A": "711",
          "FG3M": "45",
          "FG3_PCT": "6",
          "FGA": "2423",
          "FGM": "1212",
          "FG_PCT": "50",
          "FTA": "34",
          "FTM": "33",
          "FT_PCT": "97",
          "MIN": "6060",
          "OREB": "24",
          "PTS": "3132",
          "STL": "01",
          "TOV": "05",
          "TREB": "93"
        },
        "H2": {
          "AST": "56",
          "BLK": "20",
          "DREB": "87",
          "FG3A": "67",
          "FG3M": "32",
          "FG3_PCT": "48",
          "FGA": "1923",
          "FGM": "910",
          "FG_PCT": "47",
          "FTA": "87",
          "FTM": "86",
          "FT_PCT": "99",
          "MIN": "6060",
          "OREB": "34",
          "PTS": "2928",
          "STL": "04",
          "TOV": "43",
          "TREB": "121"
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
          "BLK": "2",
          "DREB": "6",
          "FG3A": "7",
          "FG3M": "4",
          "FG3_PCT": "57",
          "FGA": "24",
          "FGM": "12",
          "FG_PCT": "50",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "2",
          "PTS": "31",
          "STL": "0",
          "TOV": "0",
          "TREB": "8"
        },
        "Q2": {
          "AST": "9",
          "BLK": "0",
          "DREB": "9",
          "FG3A": "11",
          "FG3M": "5",
          "FG3_PCT": "45",
          "FGA": "23",
          "FGM": "12",
          "FG_PCT": "52",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "4",
          "PTS": "32",
          "STL": "1",
          "TOV": "5",
          "TREB": "13"
        },
        "Q3": {
          "AST": "5",
          "BLK": "2",
          "DREB": "8",
          "FG3A": "6",
          "FG3M": "3",
          "FG3_PCT": "50",
          "FGA": "19",
          "FGM": "9",
          "FG_PCT": "47",
          "FTA": "8",
          "FTM": "8",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "3",
          "PTS": "29",
          "STL": "0",
          "TOV": "4",
          "TREB": "11"
        },
        "Q4": {
          "AST": "6",
          "BLK": "0",
          "DREB": "7",
          "FG3A": "7",
          "FG3M": "2",
          "FG3_PCT": "29",
          "FGA": "23",
          "FGM": "10",
          "FG_PCT": "43",
          "FTA": "7",
          "FTM": "6",
          "FT_PCT": "86",
          "MIN": "60",
          "OREB": "4",
          "PTS": "28",
          "STL": "4",
          "TOV": "3",
          "TREB": "11"
        },
        "game": {
          "AST": "30",
          "BLK": "4",
          "DREB": "30",
          "FG3A": "31",
          "FG3M": "14",
          "FG3_PCT": "45",
          "FGA": "88",
          "FGM": "43",
          "FG_PCT": "49",
          "FTA": "22",
          "FTM": "20",
          "FT_PCT": "91",
          "MIN": "4",
          "OREB": "13",
          "PF": "27",
          "PTS": "120",
          "STL": "5",
          "TOV": "12",
          "TREB": "43"
        }
      },
      "losses": "4",
      "name": "Clippers",
      "next_game": {
        "city": "Portland",
        "day": "8",
        "dayname": "Thursday",
        "is_home": "False",
        "month": "November",
        "opponent_name": "Trail Blazers",
        "opponent_place": "Portland",
        "stadium": "Moda Center",
        "year": "2018"
      },
      "next_game_id": "6035",
      "place": "Los Angeles",
      "previous_game_id": "5499",
      "wins": "6"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "-11",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "13",
          "FGM": "6",
          "FG_PCT": "46",
          "FTA": "11",
          "FTM": "8",
          "FT_PCT": "73",
          "MIN": "39",
          "OREB": "0",
          "PF": "4",
          "PTS": "20",
          "STL": "1",
          "TOV": "2",
          "TREB": "4",
          "first_name": "Jimmy",
          "last_name": "Butler",
          "name": "Jimmy Butler",
          "starter": "True"
        },
        {
          "+/-": "-5",
          "AST": "2",
          "BLK": "4",
          "DOUBLE": "double",
          "DREB": "9",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "13",
          "FGM": "8",
          "FG_PCT": "62",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "35",
          "OREB": "3",
          "PF": "3",
          "PTS": "20",
          "STL": "3",
          "TOV": "3",
          "TREB": "12",
          "first_name": "Karl-Anthony",
          "last_name": "Towns",
          "name": "Karl-Anthony Towns",
          "starter": "True"
        },
        {
          "+/-": "-8",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "20",
          "FGM": "8",
          "FG_PCT": "40",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "34",
          "OREB": "1",
          "PF": "2",
          "PTS": "21",
          "STL": "0",
          "TOV": "2",
          "TREB": "3",
          "first_name": "Derrick",
          "last_name": "Rose",
          "name": "Derrick Rose",
          "starter": "True"
        },
        {
          "+/-": "-8",
          "AST": "2",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "7",
          "FG3M": "2",
          "FG3_PCT": "29",
          "FGA": "16",
          "FGM": "4",
          "FG_PCT": "25",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "34",
          "OREB": "0",
          "PF": "3",
          "PTS": "13",
          "STL": "1",
          "TOV": "2",
          "TREB": "6",
          "first_name": "Andrew",
          "last_name": "Wiggins",
          "name": "Andrew Wiggins",
          "starter": "True"
        },
        {
          "+/-": "-7",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "9",
          "FGM": "6",
          "FG_PCT": "67",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "32",
          "OREB": "3",
          "PF": "6",
          "PTS": "15",
          "STL": "2",
          "TOV": "0",
          "TREB": "9",
          "first_name": "Taj",
          "last_name": "Gibson",
          "name": "Taj Gibson",
          "starter": "True"
        },
        {
          "+/-": "-1",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "6",
          "FGM": "3",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "19",
          "OREB": "0",
          "PF": "4",
          "PTS": "7",
          "STL": "0",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Josh",
          "last_name": "Okogie",
          "name": "Josh Okogie",
          "starter": "False"
        },
        {
          "+/-": "-4",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "0",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "15",
          "OREB": "0",
          "PF": "1",
          "PTS": "1",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Anthony",
          "last_name": "Tolliver",
          "name": "Anthony Tolliver",
          "starter": "False"
        },
        {
          "+/-": "-5",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "5",
          "FGM": "2",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "15",
          "OREB": "0",
          "PF": "0",
          "PTS": "4",
          "STL": "1",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Tyus",
          "last_name": "Jones",
          "name": "Tyus Jones",
          "starter": "False"
        },
        {
          "+/-": "-6",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "3",
          "FGM": "3",
          "FG_PCT": "100",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "12",
          "OREB": "1",
          "PF": "0",
          "PTS": "8",
          "STL": "1",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Gorgui",
          "last_name": "Dieng",
          "name": "Gorgui Dieng",
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
          "first_name": "Luol",
          "last_name": "Deng",
          "name": "Luol Deng",
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
          "first_name": "Keita",
          "last_name": "Bates-Diop",
          "name": "Keita Bates-Diop",
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
          "first_name": "C.J.",
          "last_name": "Williams",
          "name": "C.J. Williams",
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
          "first_name": "James",
          "last_name": "Nunnally",
          "name": "James Nunnally",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 13,
      "division": "Northwest",
      "game_number": "11",
      "line_score": {
        "H1": {
          "AST": "58",
          "BLK": "23",
          "DREB": "107",
          "FG3A": "65",
          "FG3M": "21",
          "FG3_PCT": "32",
          "FGA": "2520",
          "FGM": "1310",
          "FG_PCT": "52",
          "FTA": "65",
          "FTM": "55",
          "FT_PCT": "85",
          "MIN": "6060",
          "OREB": "41",
          "PTS": "3326",
          "STL": "03",
          "TOV": "03",
          "TREB": "148"
        },
        "H2": {
          "AST": "52",
          "BLK": "30",
          "DREB": "67",
          "FG3A": "46",
          "FG3M": "20",
          "FG3_PCT": "43",
          "FGA": "2317",
          "FGM": "107",
          "FG_PCT": "5",
          "FTA": "415",
          "FTM": "311",
          "FT_PCT": "75",
          "MIN": "6060",
          "OREB": "30",
          "PTS": "2525",
          "STL": "42",
          "TOV": "35",
          "TREB": "97"
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
          "BLK": "2",
          "DREB": "10",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "25",
          "FGM": "13",
          "FG_PCT": "52",
          "FTA": "6",
          "FTM": "5",
          "FT_PCT": "83",
          "MIN": "60",
          "OREB": "4",
          "PTS": "33",
          "STL": "0",
          "TOV": "0",
          "TREB": "14"
        },
        "Q2": {
          "AST": "8",
          "BLK": "3",
          "DREB": "7",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "20",
          "FGM": "10",
          "FG_PCT": "50",
          "FTA": "5",
          "FTM": "5",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "1",
          "PTS": "26",
          "STL": "3",
          "TOV": "3",
          "TREB": "8"
        },
        "Q3": {
          "AST": "5",
          "BLK": "3",
          "DREB": "6",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "23",
          "FGM": "10",
          "FG_PCT": "43",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "3",
          "PTS": "25",
          "STL": "4",
          "TOV": "3",
          "TREB": "9"
        },
        "Q4": {
          "AST": "2",
          "BLK": "0",
          "DREB": "7",
          "FG3A": "6",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "17",
          "FGM": "7",
          "FG_PCT": "41",
          "FTA": "15",
          "FTM": "11",
          "FT_PCT": "73",
          "MIN": "60",
          "OREB": "0",
          "PTS": "25",
          "STL": "2",
          "TOV": "5",
          "TREB": "7"
        },
        "game": {
          "AST": "20",
          "BLK": "8",
          "DREB": "30",
          "FG3A": "21",
          "FG3M": "5",
          "FG3_PCT": "24",
          "FGA": "85",
          "FGM": "40",
          "FG_PCT": "47",
          "FTA": "30",
          "FTM": "24",
          "FT_PCT": "80",
          "MIN": "4",
          "OREB": "8",
          "PF": "23",
          "PTS": "109",
          "STL": "9",
          "TOV": "11",
          "TREB": "38"
        }
      },
      "losses": "7",
      "name": "Timberwolves",
      "next_game": {
        "city": "Los Angeles",
        "day": "7",
        "dayname": "Wednesday",
        "is_home": "False",
        "month": "November",
        "opponent_name": "Lakers",
        "opponent_place": "Los Angeles",
        "stadium": "Staples Center",
        "year": "2018"
      },
      "next_game_id": "5459",
      "place": "Minnesota",
      "previous_game_id": "6033",
      "wins": "4"
    }
  }
}
````

### Human reference outputs

**Reference 1**

````text
The Los Angeles Clippers defeated the visiting Minnesota Timberwolves, 120 - 109, at Staples Center on Monday evening. Minnesota (4 - 7) has been in a rough patch recently, and the Clippers (6 - 4) made sure to capitalize. Los Angeles held its opponent to just 5 - of - 22 shooting from three - point range, allowing it to take a lead thanks to its own stellar 14 - of - 31 night from deep. The Clippers also outperformed Minnesota on the boards, grabbing 12 offensive rebounds while holding the Wolves to only eight. The loss for Minnesota was the team's third straight, and it comes at an inopportune time for the team, as rumors continue to swirl around All-Star Jimmy Butler's trade demand. Three Clippers scored at least 20 points in the team's win. Forwards Tobias Harris and Danilo Gallinari scored 22 apiece to lead the team, while star guard Lou Williams delivered 20 points and six assists. Big man Boban Marjanovic scored 10 points and had eight rebounds in only 17 minutes on the floor. Minnesota, meanwhile, saw 20 points from Butler in the loss. All-Star big man Karl-Anthony Towns scored another 20 and also blocked four shots. Veteran point guard Derrick Rose led the Wolves with 21 points, coming a week after he delivered a career - high 50 point performance. Rose shot 8 - of - 20 from the field and dished out four assists in Monday's loss. The Timberwolves will attempt to snap their losing streak with a visit to the Los Angeles Lakers on Wednesday. The Clippers, meanwhile, travel to Portland to face the Trail Blazers on Thurdsay.
````

**Reference 2**

````text
The Los Angeles Clippers defeated the visiting Minnesota Timberwolves , 120 - 109 , at Staples Center on Monday evening . Minnesota ( 4 - 7 ) has been in a rough patch recently , and the Clippers ( 6 - 4 ) made sure to capitalize . Los Angeles held its opponent to just 5 - of - 22 shooting from three - point range , allowing it to take a lead thanks to its own stellar 14 - of - 31 night from deep . The Clippers also outperformed Minnesota on the boards , grabbing 12 offensive rebounds while holding the Wolves to only eight . The loss for Minnesota was the team 's third straight , and it comes at an inopportune time for the team , as rumors continue to swirl around All-Star Jimmy Butler 's trade demand . Three Clippers scored at least 20 points in the team 's win . Forwards Tobias Harris and Danilo Gallinari scored 22 apiece to lead the team , while star guard Lou Williams delivered 20 points and six assists . Big man Boban Marjanovic scored 10 points and had eight rebounds in only 17 minutes on the floor . Minnesota , meanwhile , saw 20 points from Butler in the loss . All-Star big man Karl-Anthony Towns scored another 20 and also blocked four shots . Veteran point guard Derrick Rose led the Wolves with 21 points , coming a week after he delivered a career - high 50 point performance . Rose shot 8 - of - 20 from the field and dished out four assists in Monday 's loss . The Timberwolves will attempt to snap their losing streak with a visit to the Los Angeles Lakers on Wednesday . The Clippers , meanwhile , travel to Portland to face the Trail Blazers on Thurdsay .
````

### Full System output

````markdown
The Los Angeles Clippers defeated the Minnesota Timberwolves 120-109 on Monday, November 5, 2018, at Staples Center.
Los Angeles entered with 6 wins and 4 losses, while Minnesota entered with 4 wins and 7 losses.
Both teams were next scheduled away from home: Los Angeles at the Trail Blazers on Thursday, November 8, and Minnesota at the Lakers on Wednesday, November 7.
Following a 33-31 Timberwolves lead after the first quarter, the Clippers led 63-59 after the second quarter and 92-84 after the third before closing out the 120-109 victory.
Los Angeles outscored Minnesota 32-26 in the second quarter, 29-25 in the third and 28-25 in the fourth.
Tobias Harris and Danilo Gallinari each scored a game-high 22 points, while Derrick Rose led Minnesota with 21 and Lou Williams, Jimmy Butler and Karl-Anthony Towns each had 20.
Harris tied for the game lead with 8 field goals and collected 10 rebounds; he and Towns each pulled down a game-high 9 defensive rebounds.
Towns added a game-high 12 rebounds, a game-high 4 blocks and 3 steals alongside his 20 points.
Boban Marjanović and Montrezl Harrell each grabbed a game-high 4 offensive rebounds, with Marjanović also recording 2 blocks.
Taj Gibson added 15 points and 9 rebounds for Minnesota.
The Clippers also controlled playmaking, finishing with 30 team assists to Minnesota's 20; Lou Williams led all players with 6 assists, while Shai Gilgeous-Alexander and Jimmy Butler each had 5.
Los Angeles won the rebounding comparison 43-38, including a 13-8 edge on the offensive glass, while the teams matched at 30 defensive rebounds each.
The Clippers made 14 three-pointers to Minnesota's 5, while the Timberwolves held a 24-20 advantage at the free-throw line.
Los Angeles finished with 43 field goals to Minnesota's 40, while Minnesota recorded more steals (9-5) and blocks (8-4).
````

### Baseline output

````markdown
The Los Angeles Clippers defeated the Minnesota Timberwolves 120–109 at Staples Center on November 5, 2018, in front of 16,600 fans. The Clippers shot 49% from the field, 45% on three-pointers (14 makes), and 91% on free throws, while the Timberwolves shot 47% from the field, 24% on three-pointers (5 makes), and 80% on free throws. Tobias Harris and Danilo Gallinari each scored 22 points for the Clippers, with Harris adding a double-double (10 rebounds), and Lou Williams added 20 points off the bench. For the Timberwolves, Derrick Rose scored 21 points, while Jimmy Butler and Karl-Anthony Towns each scored 20 points, with Towns posting a double-double (12 rebounds). The Clippers improved to 6–4, while the Timberwolves fell to 4–7.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.0908 | 0.0975 | 0.0067 | Full System |
| BERTScore F1 | Higher | 0.8408 | 0.8401 | -0.0007 | Baseline |
| BLEU | Higher | 0.0551 | 0.0938 | 0.0387 | Full System |
| chrF | Higher | 0.2874 | 0.4380 | 0.1506 | Full System |
| HHEM mean support | Higher | 0.1102 | 0.0352 | -0.0750 | Baseline |
| HHEM minimum sentence support | Higher | 0.0136 | 0.0103 | -0.0032 | Baseline |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.1765 | 0.2604 | 0.0839 | Full System |
| ROUGE-1 | Higher | 0.4450 | 0.4874 | 0.0424 | Full System |
| ROUGE-2 | Higher | 0.1709 | 0.1450 | -0.0258 | Baseline |
| ROUGE-L | Higher | 0.2600 | 0.2185 | -0.0415 | Baseline |
| ROUGE-Lsum | Higher | 0.2600 | 0.2185 | -0.0415 | Baseline |
| TER | Lower | 0.8000 | 0.9128 | -0.1128 | Baseline |

### GPT-5.6 Sol structured annotations

**Full System**

1. **CONTEXT**
   - Error span: Los Angeles entered with 6 wins and 4 losses, while Minnesota entered with 4 wins and 7 losses.
   - Correction or explanation: The listed records include this result: the Clippers' 6-4 record totals their 10 games, and the Timberwolves' 4-7 record totals their 11 games. They therefore finished the game at those records rather than entered with them; their pregame records were 5-4 and 4-6, respectively.
2. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode is a multi-paragraph report, so the report should be divided into at least two coherent paragraphs.

**Baseline**

1. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode is a multi-paragraph report. The content should be divided into at least two coherent paragraphs.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T002934Z_9f590b408d |
| Execution outcome | success |
| Final generation path | deterministic_fallback |
| Final Writer mode | llm_writer |
| Release status | approved |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 14 |
| Supported sentences | 14 |
| Evidence items | 41 |
| Verified facts | 41 |
| Rejected facts | 0 |
| Verified insights | 5 |
| Rejected insights | 3 |
| Full System words | 299 |
| Baseline words | 120 |
| Full System elapsed seconds | 763.1489 |
| Baseline elapsed seconds | 4.9363 |
| Full System provider-reported tokens | 514250 |
| Baseline provider-reported tokens | 9237 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/sportsett_basketball__5130/full_system/sportsett_basketball/20260821T002934Z_9f590b408d/pipeline_result.json |

## A6. e2e_nlg / e2e_nlg-test-209

| Field | Value |
| --- | --- |
| Dataset | e2e_nlg |
| Example ID | e2e_nlg-test-209 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 7de0ca441f2fb833ff0197f110c66c54c545fc71f7264a1a1c4dfb337b21c277 |
| Reference SHA-256 | f5b104892617f5bd1d9bf95d2252a6ff0fea0dd279e574255231c301381504c4 |
| Full System request | Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
name[The Cricketers], eatType[coffee shop], familyFriendly[yes], near[Café Sicilia]
````

### Human reference outputs

**Reference 1**

````text
The Cricketers is a children friendly coffee shop near Café Sicilia
````

**Reference 2**

````text
The Cricketers is a family friendly coffee shop located near Café Sicilia.
````

**Reference 3**

````text
Known as 'average' and 'Family Friendly' , The Cricketers offers coffee shop food near the Café Sicilia
````

**Reference 4**

````text
A exceptional coffee shop where kids are welcome and is minutes from Café Sicilia is named The Cricketers.
````

### Full System output

````markdown
The Cricketers is a family-friendly coffee shop near Café Sicilia.
````

### Baseline output

````markdown
The Cricketers is a family-friendly coffee shop located near Café Sicilia.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9716 | 0.9627 | -0.0089 | Baseline |
| BERTScore F1 | Higher | 0.9946 | 0.9887 | -0.0059 | Baseline |
| BLEU | Higher | 0.7349 | 0.7017 | -0.0332 | Baseline |
| chrF | Higher | 0.9190 | 0.8010 | -0.1180 | Baseline |
| HHEM mean support | Higher | 0.5307 | 0.5135 | -0.0173 | Baseline |
| HHEM minimum sentence support | Higher | 0.5307 | 0.5135 | -0.0173 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.8370 | 0.7486 | -0.0884 | Baseline |
| ROUGE-1 | Higher | 1.0000 | 0.9565 | -0.0435 | Baseline |
| ROUGE-2 | Higher | 1.0000 | 0.8571 | -0.1429 | Baseline |
| ROUGE-L | Higher | 1.0000 | 0.9565 | -0.0435 | Baseline |
| ROUGE-Lsum | Higher | 1.0000 | 0.9565 | -0.0435 | Baseline |
| TER | Lower | 0.1379 | 0.2069 | -0.0690 | Baseline |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T004218Z_ffab5b6ba8 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 0 |
| Supported sentences | 0 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 10 |
| Baseline words | 11 |
| Full System elapsed seconds | 5.9558 |
| Baseline elapsed seconds | 1.3115 |
| Full System provider-reported tokens | 6071 |
| Baseline provider-reported tokens | 262 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/e2e_nlg__e2e_nlg-test-209/full_system/e2e_nlg/20260821T004218Z_ffab5b6ba8/pipeline_result.json |

## A7. web_nlg / web_nlg_en-test-1330

| Field | Value |
| --- | --- |
| Dataset | web_nlg |
| Example ID | web_nlg_en-test-1330 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 0dc9960da718f111cf6eb450519a016a22ee640015ee8bec715c72ba8d05a6b8 |
| Reference SHA-256 | df9c74f2b730dd5fa43fcdd32b773b9f320e7a007f1424599601776a78857ab8 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Brandon_Carter | doctoralAdvisor | Dennis_William_Sciama
Brandon_Carter | birthPlace | England
Brandon_Carter | birthDate | 1942-01-01
Brandon_Carter | almaMater | University_of_Cambridge
Brandon_Carter | knownFor | Doomsday_argument
````

### Human reference outputs

**Reference 1**

````text
Brandon Carter, whose alma mater is the University of Cambridge with Dennis William Sciama as his doctoral advisor, was born in England on January 1, 1942 and is known for the Doomsday argument.
````

**Reference 2**

````text
Brandon Carter was born in England on January 1, 1942. He is best known for his work with the Doomsday argument. Brandon Carter studied at the University of Cambridge where his doctoral advisor was Dennis William Sciama.
````

**Reference 3**

````text
Brandon Carter was born in England on January 1st, 1942. He graduated from the University of Cambridge, where Dennis William Sciama was his doctoral advisor. Carter is known for his Doomsday argument.
````

### Full System output

````markdown
Brandon Carter's doctoral advisor was Dennis William Sciama; he was born in England on 1942-01-01, studied at the University of Cambridge, and is known for the Doomsday argument.
````

### Baseline output

````markdown
Brandon Carter was born in England in 1942, studied at the University of Cambridge, had Dennis William Sciama as his doctoral advisor, and is known for the Doomsday argument.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9690 | 0.9320 | -0.0370 | Baseline |
| BERTScore F1 | Higher | 0.9493 | 0.9336 | -0.0157 | Baseline |
| BLEU | Higher | 0.6454 | 0.5648 | -0.0806 | Baseline |
| chrF | Higher | 0.7387 | 0.6856 | -0.0531 | Baseline |
| HHEM mean support | Higher | 0.6967 | 0.6373 | -0.0594 | Baseline |
| HHEM minimum sentence support | Higher | 0.6967 | 0.6373 | -0.0594 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.6640 | 0.5803 | -0.0837 | Baseline |
| ROUGE-1 | Higher | 0.8065 | 0.7941 | -0.0123 | Baseline |
| ROUGE-2 | Higher | 0.6333 | 0.5806 | -0.0527 | Baseline |
| ROUGE-L | Higher | 0.7213 | 0.5625 | -0.1588 | Baseline |
| ROUGE-Lsum | Higher | 0.7213 | 0.5625 | -0.1588 | Baseline |
| TER | Lower | 0.3529 | 0.5000 | -0.1471 | Baseline |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

1. **NUMBER**
   - Error span: born in England in 1942
   - Correction or explanation: The source gives the full birth date as 1942-01-01, but the output states only the year, omitting January 1.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T004224Z_ac74aa80e2 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 28 |
| Baseline words | 29 |
| Full System elapsed seconds | 9.3086 |
| Baseline elapsed seconds | 1.8712 |
| Full System provider-reported tokens | 12413 |
| Baseline provider-reported tokens | 356 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/web_nlg__web_nlg_en-test-1330/full_system/web_nlg/20260821T004224Z_ac74aa80e2/pipeline_result.json |

## A8. dart / dart-test-1805

| Field | Value |
| --- | --- |
| Dataset | dart |
| Example ID | dart-test-1805 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 6b2447749b4569aa9ccd293353536c1e5de45907abab23a3d17be3202be8f9f9 |
| Reference SHA-256 | 3a25a85473ab0357b86dd5806e5dce9a5073145299aceb30558b56d66fa6dfe6 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
A Severed Wasp | NUMBER_OF_PAGES | "388"
A Severed Wasp | OCLC_NUMBER | 8805735
A Severed Wasp | MEDIA_TYPE | Hardcover
````

### Human reference outputs

**Reference 1**

````text
The hardback book, A Severed Wasp, has 388 pages and the OCLC number 8805735.
````

**Reference 2**

````text
A Severed Wasp is a hardcover book that has 388 pages and has the OCLC number 8805735.
````

**Reference 3**

````text
A Severed Wasp, with 388 pages, was published in hardcover. Its OCLC number is 8805735.
````

### Full System output

````markdown
A Severed Wasp has 388 pages, OCLC number 8805735, and a hardcover media type.
````

### Baseline output

````markdown
The supplied data supports three factual findings about the book *A Severed Wasp*: it has 388 pages, its OCLC number is 8805735, and its media type is hardcover.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.7002 | 0.9030 | 0.2028 | Full System |
| BERTScore F1 | Higher | 0.9309 | 0.9600 | 0.0291 | Full System |
| BLEU | Higher | 0.1750 | 0.2546 | 0.0796 | Full System |
| chrF | Higher | 0.5515 | 0.6147 | 0.0632 | Full System |
| HHEM mean support | Higher | 0.7567 | 0.9082 | 0.1514 | Full System |
| HHEM minimum sentence support | Higher | 0.7567 | 0.9082 | 0.1514 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.4978 | 0.5341 | 0.0363 | Full System |
| ROUGE-1 | Higher | 0.6222 | 0.7742 | 0.1520 | Full System |
| ROUGE-2 | Higher | 0.3415 | 0.5385 | 0.1970 | Full System |
| ROUGE-L | Higher | 0.5238 | 0.6429 | 0.1190 | Full System |
| ROUGE-Lsum | Higher | 0.5238 | 0.6429 | 0.1190 | Full System |
| TER | Lower | 1.3696 | 0.6522 | 0.7174 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T004233Z_19351712cf |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 14 |
| Baseline words | 28 |
| Full System elapsed seconds | 12.3898 |
| Baseline elapsed seconds | 1.5499 |
| Full System provider-reported tokens | 6855 |
| Baseline provider-reported tokens | 303 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/dart__dart-test-1805/full_system/dart/20260821T004233Z_19351712cf/pipeline_result.json |

## A9. totto / totto-validation-4467

| Field | Value |
| --- | --- |
| Dataset | totto |
| Example ID | totto-validation-4467 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source SHA-256 | aa436856c0ebc8aea944693e765472828cbdc6aafb670970a5c15a03f8df6d1d |
| Reference SHA-256 | b41d8e37a0c759b92fd4173207ba1c235bdd583b30f969d564167dfe6e23b13d |
| Full System request | Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Page: 2015 World Championships in Athletics – Women's long jump
Section: Records
Table:
World record | Galina Chistyakova (URS) | 7.52 | Leningrad, Soviet Union | 11 June 1988
Championship record | Jackie Joyner-Kersee (USA) | 7.36 | Rome, Italy | 3 September 1987
World leading | Tianna Bartoletta (USA) | 7.12 | Eugene, United States | 27 June 2015
African record | Chioma Ajunwa (NGR) | 7.12 | Atlanta, GA, United States | 2 August 1996
Asian record | Yao Weili (CHN) | 7.01 | Jinan, People's Republic of China | 5 June 1993
North, Central American and Caribbean record | Jackie Joyner-Kersee (USA) | 7.49 | New York City, United States | 22 May 1994
Sestriere, Italy | 31 July 1994
South American record | Maurren Higa Maggi (BRA) | 7.26A | Bogotá, Colombia | 26 June 1999
European record | Galina Chistyakova (URS) | 7.52 | Leningrad, Soviet Union | 11 June 1988
Oceanian record | Bronwyn Thompson (AUS) | 7.00 | Melbourne, Australia | 7 March 2002
The following records were established during the competition:
*World Leading* | *Tianna Bartoletta (USA)* | *7.14* | Beijing, China | 28 August 2015
Cells surrounded by * are highlighted.
````

### Human reference outputs

**Reference 1**

````text
Bartoletta leaped a world leading 7.14.
````

**Reference 2**

````text
Bartoletta leaped a world-leading 7.14 to take the lead.
````

**Reference 3**

````text
Bartoletta leaped to a world leading mark of 7.14.
````

### Full System output

````markdown
During the competition, Tianna Bartoletta (USA) set a world-leading mark of 7.14 in the women's long jump.
````

### Baseline output

````markdown
Based on the supplied data, the strongest supported finding is that Tianna Bartoletta (USA) established a new world leading mark of 7.14 meters in the women's long jump at the 2015 World Championships in Beijing, China, on 28 August 2015. This improved upon her previous world leading mark of 7.12 meters set on 27 June 2015 in Eugene, United States.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.1616 | 0.6925 | 0.5310 | Full System |
| BERTScore F1 | Higher | 0.8741 | 0.9031 | 0.0290 | Full System |
| BLEU | Higher | 0.0577 | 0.0956 | 0.0379 | Full System |
| chrF | Higher | 0.3182 | 0.4945 | 0.1763 | Full System |
| HHEM mean support | Higher | 0.4160 | 0.2572 | -0.1588 | Baseline |
| HHEM minimum sentence support | Higher | 0.0556 | 0.2572 | 0.2016 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.5000 | 1.0000 | -0.5000 | Baseline |
| METEOR | Higher | 0.4501 | 0.3796 | -0.0705 | Baseline |
| ROUGE-1 | Higher | 0.2192 | 0.5333 | 0.3142 | Full System |
| ROUGE-2 | Higher | 0.1408 | 0.4286 | 0.2877 | Full System |
| ROUGE-L | Higher | 0.2192 | 0.5333 | 0.3142 | Full System |
| ROUGE-Lsum | Higher | 0.2192 | 0.5333 | 0.3142 | Full System |
| TER | Lower | 6.7500 | 1.6250 | 5.1250 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

1. **TASK/FORMAT**
   - Error span: in Beijing, China, on 28 August 2015. This improved upon her previous world leading mark of 7.12 meters set on 27 June 2015 in Eugene, United States.
   - Correction or explanation: The response uses two sentences and discusses non-highlighted location, date, and prior-mark cells, contrary to the requirement for exactly one concise sentence describing only the highlighted cells. It should state only that Tianna Bartoletta (USA) established a world-leading mark of 7.14.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T004246Z_3312e5d979 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 17 |
| Baseline words | 60 |
| Full System elapsed seconds | 10.9657 |
| Baseline elapsed seconds | 4.6787 |
| Full System provider-reported tokens | 14915 |
| Baseline provider-reported tokens | 1057 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/totto__totto-validation-4467/full_system/totto/20260821T004246Z_3312e5d979/pipeline_result.json |

## A10. sportsett_basketball / 5372

| Field | Value |
| --- | --- |
| Dataset | sportsett_basketball |
| Example ID | 5372 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source SHA-256 | d0793e0e6623f60983f0cc365fa6269099446399d87b82f687382512d9bde29a |
| Reference SHA-256 | 087382c8eb93adfbe153771f92bcac63ce11fe957c30e23620526c9e93103113 |
| Full System request | Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````json
{
  "game": {
    "attendance": "17600",
    "capacity": "17600",
    "city": "Sacramento",
    "day": "17",
    "dayname": "Wednesday",
    "game_id": "5372",
    "month": "October",
    "season": "2018",
    "stadium": "Golden 1 Center",
    "state": "California",
    "year": "2018"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "16",
          "AST": "4",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "15",
          "FGM": "10",
          "FG_PCT": "67",
          "FTA": "6",
          "FTM": "3",
          "FT_PCT": "50",
          "MIN": "38",
          "OREB": "2",
          "PF": "2",
          "PTS": "23",
          "STL": "1",
          "TOV": "0",
          "TREB": "7",
          "first_name": "Willie",
          "last_name": "Cauley-Stein",
          "name": "Willie Cauley-Stein",
          "starter": "True"
        },
        {
          "+/-": "19",
          "AST": "7",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "16",
          "FGM": "8",
          "FG_PCT": "50",
          "FTA": "7",
          "FTM": "5",
          "FT_PCT": "71",
          "MIN": "37",
          "OREB": "0",
          "PF": "5",
          "PTS": "21",
          "STL": "3",
          "TOV": "3",
          "TREB": "4",
          "first_name": "De'Aaron",
          "last_name": "Fox",
          "name": "De'Aaron Fox",
          "starter": "True"
        },
        {
          "+/-": "9",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "18",
          "FGM": "9",
          "FG_PCT": "50",
          "FTA": "1",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "31",
          "OREB": "1",
          "PF": "6",
          "PTS": "19",
          "STL": "1",
          "TOV": "4",
          "TREB": "6",
          "first_name": "Buddy",
          "last_name": "Hield",
          "name": "Buddy Hield",
          "starter": "True"
        },
        {
          "+/-": "10",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "7",
          "FGM": "3",
          "FG_PCT": "43",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "30",
          "OREB": "0",
          "PF": "2",
          "PTS": "12",
          "STL": "0",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Yogi",
          "last_name": "Ferrell",
          "name": "Yogi Ferrell",
          "starter": "True"
        },
        {
          "+/-": "12",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "7",
          "FG3A": "2",
          "FG3M": "2",
          "FG3_PCT": "100",
          "FGA": "12",
          "FGM": "8",
          "FG_PCT": "67",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "27",
          "OREB": "1",
          "PF": "2",
          "PTS": "18",
          "STL": "1",
          "TOV": "0",
          "TREB": "8",
          "first_name": "Nemanja",
          "last_name": "Bjelica",
          "name": "Nemanja Bjelica",
          "starter": "True"
        },
        {
          "+/-": "-19",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "10",
          "FGM": "4",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "30",
          "OREB": "0",
          "PF": "2",
          "PTS": "8",
          "STL": "2",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Justin",
          "last_name": "Jackson",
          "name": "Justin Jackson",
          "starter": "False"
        },
        {
          "+/-": "-29",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "7",
          "FGM": "2",
          "FG_PCT": "29",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "17",
          "OREB": "0",
          "PF": "2",
          "PTS": "5",
          "STL": "0",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Iman",
          "last_name": "Shumpert",
          "name": "Iman Shumpert",
          "starter": "False"
        },
        {
          "+/-": "-14",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "6",
          "FGM": "3",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "12",
          "OREB": "1",
          "PF": "2",
          "PTS": "6",
          "STL": "0",
          "TOV": "0",
          "TREB": "5",
          "first_name": "Marvin",
          "last_name": "Bagley",
          "name": "Marvin Bagley",
          "starter": "False"
        },
        {
          "+/-": "-22",
          "AST": "1",
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
          "MIN": "9",
          "OREB": "0",
          "PF": "4",
          "PTS": "2",
          "STL": "0",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Harry",
          "last_name": "Giles",
          "name": "Harry Giles",
          "starter": "False"
        },
        {
          "+/-": "-12",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "1",
          "FG3M": "1",
          "FG3_PCT": "100",
          "FGA": "2",
          "FGM": "1",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "4",
          "OREB": "0",
          "PF": "0",
          "PTS": "3",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Frank",
          "last_name": "Mason",
          "name": "Frank Mason",
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
          "first_name": "Ben",
          "last_name": "McLemore",
          "name": "Ben McLemore",
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
          "first_name": "Skal",
          "last_name": "Labissière",
          "name": "Skal Labissière",
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
          "first_name": "Wenyen",
          "last_name": "Gabriel",
          "name": "Wenyen Gabriel",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 13,
      "division": "Pacific",
      "game_number": "1",
      "line_score": {
        "H1": {
          "AST": "42",
          "BLK": "00",
          "DREB": "810",
          "FG3A": "34",
          "FG3M": "30",
          "FG3_PCT": "88",
          "FGA": "2423",
          "FGM": "159",
          "FG_PCT": "7",
          "FTA": "34",
          "FTM": "13",
          "FT_PCT": "38",
          "MIN": "6060",
          "OREB": "10",
          "PTS": "3421",
          "STL": "21",
          "TOV": "23",
          "TREB": "820"
        },
        "H2": {
          "AST": "74",
          "BLK": "21",
          "DREB": "68",
          "FG3A": "75",
          "FG3M": "31",
          "FG3_PCT": "41",
          "FGA": "2127",
          "FGM": "1312",
          "FG_PCT": "62",
          "FTA": "56",
          "FTM": "35",
          "FT_PCT": "62",
          "MIN": "6060",
          "OREB": "13",
          "PTS": "3230",
          "STL": "14",
          "TOV": "22",
          "TREB": "81"
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
          "BLK": "0",
          "DREB": "8",
          "FG3A": "3",
          "FG3M": "3",
          "FG3_PCT": "100",
          "FGA": "24",
          "FGM": "15",
          "FG_PCT": "62",
          "FTA": "3",
          "FTM": "1",
          "FT_PCT": "33",
          "MIN": "60",
          "OREB": "1",
          "PTS": "34",
          "STL": "2",
          "TOV": "2",
          "TREB": "9"
        },
        "Q2": {
          "AST": "2",
          "BLK": "0",
          "DREB": "10",
          "FG3A": "4",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "23",
          "FGM": "9",
          "FG_PCT": "39",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "0",
          "PTS": "21",
          "STL": "1",
          "TOV": "3",
          "TREB": "10"
        },
        "Q3": {
          "AST": "7",
          "BLK": "2",
          "DREB": "6",
          "FG3A": "7",
          "FG3M": "3",
          "FG3_PCT": "43",
          "FGA": "21",
          "FGM": "13",
          "FG_PCT": "62",
          "FTA": "5",
          "FTM": "3",
          "FT_PCT": "60",
          "MIN": "60",
          "OREB": "1",
          "PTS": "32",
          "STL": "1",
          "TOV": "2",
          "TREB": "7"
        },
        "Q4": {
          "AST": "4",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "27",
          "FGM": "12",
          "FG_PCT": "44",
          "FTA": "6",
          "FTM": "5",
          "FT_PCT": "83",
          "MIN": "60",
          "OREB": "3",
          "PTS": "30",
          "STL": "4",
          "TOV": "2",
          "TREB": "11"
        },
        "game": {
          "AST": "17",
          "BLK": "3",
          "DREB": "32",
          "FG3A": "19",
          "FG3M": "7",
          "FG3_PCT": "37",
          "FGA": "95",
          "FGM": "49",
          "FG_PCT": "52",
          "FTA": "18",
          "FTM": "12",
          "FT_PCT": "67",
          "MIN": "4",
          "OREB": "5",
          "PF": "27",
          "PTS": "117",
          "STL": "8",
          "TOV": "9",
          "TREB": "37"
        }
      },
      "losses": "1",
      "name": "Kings",
      "next_game": {
        "city": "New Orleans",
        "day": "19",
        "dayname": "Friday",
        "is_home": "False",
        "month": "October",
        "opponent_name": "Pelicans",
        "opponent_place": "New Orleans",
        "stadium": "Smoothie King Center",
        "year": "2018"
      },
      "next_game_id": "5700",
      "place": "Sacramento",
      "previous_game_id": "null",
      "wins": "0"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "-9",
          "AST": "0",
          "BLK": "3",
          "DOUBLE": "double",
          "DREB": "12",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "9",
          "FGM": "7",
          "FG_PCT": "78",
          "FTA": "5",
          "FTM": "5",
          "FT_PCT": "100",
          "MIN": "37",
          "OREB": "3",
          "PF": "3",
          "PTS": "19",
          "STL": "0",
          "TOV": "2",
          "TREB": "15",
          "first_name": "Rudy",
          "last_name": "Gobert",
          "name": "Rudy Gobert",
          "starter": "True"
        },
        {
          "+/-": "-12",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "10",
          "FG3M": "3",
          "FG3_PCT": "30",
          "FGA": "21",
          "FGM": "8",
          "FG_PCT": "38",
          "FTA": "6",
          "FTM": "5",
          "FT_PCT": "83",
          "MIN": "36",
          "OREB": "0",
          "PF": "5",
          "PTS": "24",
          "STL": "2",
          "TOV": "4",
          "TREB": "3",
          "first_name": "Donovan",
          "last_name": "Mitchell",
          "name": "Donovan Mitchell",
          "starter": "True"
        },
        {
          "+/-": "-7",
          "AST": "6",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "6",
          "FG3M": "4",
          "FG3_PCT": "67",
          "FGA": "12",
          "FGM": "9",
          "FG_PCT": "75",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "35",
          "OREB": "0",
          "PF": "3",
          "PTS": "22",
          "STL": "4",
          "TOV": "5",
          "TREB": "1",
          "first_name": "Joe",
          "last_name": "Ingles",
          "name": "Joe Ingles",
          "starter": "True"
        },
        {
          "+/-": "7",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "8",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "7",
          "FG_PCT": "88",
          "FTA": "8",
          "FTM": "4",
          "FT_PCT": "50",
          "MIN": "23",
          "OREB": "1",
          "PF": "1",
          "PTS": "18",
          "STL": "0",
          "TOV": "2",
          "TREB": "9",
          "first_name": "Derrick",
          "last_name": "Favors",
          "name": "Derrick Favors",
          "starter": "True"
        },
        {
          "+/-": "-17",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "21",
          "OREB": "0",
          "PF": "3",
          "PTS": "1",
          "STL": "1",
          "TOV": "2",
          "TREB": "2",
          "first_name": "Ricky",
          "last_name": "Rubio",
          "name": "Ricky Rubio",
          "starter": "True"
        },
        {
          "+/-": "17",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "5",
          "FGM": "2",
          "FG_PCT": "40",
          "FTA": "9",
          "FTM": "7",
          "FT_PCT": "78",
          "MIN": "33",
          "OREB": "0",
          "PF": "2",
          "PTS": "13",
          "STL": "0",
          "TOV": "0",
          "TREB": "5",
          "first_name": "Jae",
          "last_name": "Crowder",
          "name": "Jae Crowder",
          "starter": "False"
        },
        {
          "+/-": "22",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "9",
          "FGM": "4",
          "FG_PCT": "44",
          "FTA": "7",
          "FTM": "4",
          "FT_PCT": "57",
          "MIN": "26",
          "OREB": "1",
          "PF": "1",
          "PTS": "13",
          "STL": "0",
          "TOV": "1",
          "TREB": "4",
          "first_name": "Dante",
          "last_name": "Exum",
          "name": "Dante Exum",
          "starter": "False"
        },
        {
          "+/-": "25",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "3",
          "FG3M": "3",
          "FG3_PCT": "100",
          "FGA": "7",
          "FGM": "4",
          "FG_PCT": "57",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "17",
          "OREB": "0",
          "PF": "1",
          "PTS": "13",
          "STL": "1",
          "TOV": "1",
          "TREB": "3",
          "first_name": "Alec",
          "last_name": "Burks",
          "name": "Alec Burks",
          "starter": "False"
        },
        {
          "+/-": "6",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "4",
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
          "TREB": "2",
          "first_name": "Royce",
          "last_name": "O'Neale",
          "name": "Royce O'Neale",
          "starter": "False"
        },
        {
          "+/-": "-2",
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
          "MIN": "1",
          "OREB": "0",
          "PF": "0",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "0",
          "first_name": "Georges",
          "last_name": "Niang",
          "name": "Georges Niang",
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
          "first_name": "Ekpe",
          "last_name": "Udoh",
          "name": "Ekpe Udoh",
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
          "first_name": "Thabo",
          "last_name": "Sefolosha",
          "name": "Thabo Sefolosha",
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
          "first_name": "Grayson",
          "last_name": "Allen",
          "name": "Grayson Allen",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 6,
      "division": "Northwest",
      "game_number": "1",
      "line_score": {
        "H1": {
          "AST": "55",
          "BLK": "21",
          "DREB": "914",
          "FG3A": "610",
          "FG3M": "45",
          "FG3_PCT": "7",
          "FGA": "1926",
          "FGM": "1013",
          "FG_PCT": "53",
          "FTA": "88",
          "FTM": "67",
          "FT_PCT": "76",
          "MIN": "6060",
          "OREB": "11",
          "PTS": "3038",
          "STL": "22",
          "TOV": "51",
          "TREB": "925"
        },
        "H2": {
          "AST": "56",
          "BLK": "01",
          "DREB": "79",
          "FG3A": "29",
          "FG3M": "13",
          "FG3_PCT": "45",
          "FGA": "1618",
          "FGM": "99",
          "FG_PCT": "6",
          "FTA": "1012",
          "FTM": "69",
          "FT_PCT": "7",
          "MIN": "6060",
          "OREB": "21",
          "PTS": "2530",
          "STL": "22",
          "TOV": "56",
          "TREB": "100"
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
          "BLK": "2",
          "DREB": "9",
          "FG3A": "6",
          "FG3M": "4",
          "FG3_PCT": "67",
          "FGA": "19",
          "FGM": "10",
          "FG_PCT": "53",
          "FTA": "8",
          "FTM": "6",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "1",
          "PTS": "30",
          "STL": "2",
          "TOV": "5",
          "TREB": "10"
        },
        "Q2": {
          "AST": "5",
          "BLK": "1",
          "DREB": "14",
          "FG3A": "10",
          "FG3M": "5",
          "FG3_PCT": "50",
          "FGA": "26",
          "FGM": "13",
          "FG_PCT": "50",
          "FTA": "8",
          "FTM": "7",
          "FT_PCT": "88",
          "MIN": "60",
          "OREB": "1",
          "PTS": "38",
          "STL": "2",
          "TOV": "1",
          "TREB": "15"
        },
        "Q3": {
          "AST": "5",
          "BLK": "0",
          "DREB": "7",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "16",
          "FGM": "9",
          "FG_PCT": "56",
          "FTA": "10",
          "FTM": "6",
          "FT_PCT": "60",
          "MIN": "60",
          "OREB": "2",
          "PTS": "25",
          "STL": "2",
          "TOV": "5",
          "TREB": "9"
        },
        "Q4": {
          "AST": "6",
          "BLK": "1",
          "DREB": "9",
          "FG3A": "9",
          "FG3M": "3",
          "FG3_PCT": "33",
          "FGA": "18",
          "FGM": "9",
          "FG_PCT": "50",
          "FTA": "12",
          "FTM": "9",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "1",
          "PTS": "30",
          "STL": "2",
          "TOV": "6",
          "TREB": "10"
        },
        "game": {
          "AST": "21",
          "BLK": "4",
          "DREB": "39",
          "FG3A": "27",
          "FG3M": "13",
          "FG3_PCT": "48",
          "FGA": "79",
          "FGM": "41",
          "FG_PCT": "52",
          "FTA": "38",
          "FTM": "28",
          "FT_PCT": "74",
          "MIN": "4",
          "OREB": "5",
          "PF": "19",
          "PTS": "123",
          "STL": "8",
          "TOV": "17",
          "TREB": "44"
        }
      },
      "losses": "0",
      "name": "Jazz",
      "next_game": {
        "city": "Salt Lake City",
        "day": "19",
        "dayname": "Friday",
        "is_home": "True",
        "month": "October",
        "opponent_name": "Warriors",
        "opponent_place": "Golden State",
        "stadium": "Vivint Smart Home Arena",
        "year": "2018"
      },
      "next_game_id": "5331",
      "place": "Utah",
      "previous_game_id": "null",
      "wins": "1"
    }
  }
}
````

### Human reference outputs

**Reference 1**

````text
The visiting Utah Jazz defeated the Sacramento Kings at Golden 1 Center, 123 - 117, on Wednesday evening. Sacramento (0 - 1) started the season opener in dominant fashion, beginning the game on an 18 - 4 run. Utah (10) quickly answered back, though, cutting the deficit to just four points by the end of the first quarter. It soon became Utah's game to lose, as the trio of Donovan Mitchell, Rudy Gobert, and Joe Ingles helped the Jazz rack up 68 points by halftime. Utah's efficiency was a contributing factor in their strong offensive play, as the team shot over 51 percent from the field and 48 percent from three - point range. Mitchell was the game's top scorer, finishing with 24 points on 8 - of - 21 shooting. He did, though, commit five turnovers on the night. Ingles, meanwhile, scored 22 points and shot 9 - of - 12 from the field. He added four steals on the defensive end. Of course, the story of the night on the defensive end was Rudy Gobert. The reigning Defensive Player of the Year finished the game with 15 rebounds and blocked three shots. On Sacramento's side, all eyes were on second overall pick Marvin Bagley, who made his NBA debut in the game. Despite his status as a top pick, Bagley came off the bench and played only 12 minutes in his first appearance. He made the most of those minutes, though, scoring six points and grabbing five rebounds. Center Willie Cauley-Stein scored a team - high 23 points in 38 minutes of play. The former Kentucky star also dished out four assists and blocked two shots. Sophomore point guard De'Aaron Fox added 21 points and dished out seven assists as well. On Friday, the Kings will visit New Orleans while Utah will host the defending champion Golden State Warriors.
````

**Reference 2**

````text
The visiting Utah Jazz defeated the Sacramento Kings at Golden 1 Center , 123 - 117 , on Wednesday evening . Sacramento ( 0 - 1 ) started the season opener in dominant fashion , beginning the game on an 18 - 4 run . Utah ( 10 ) quickly answered back , though , cutting the deficit to just four points by the end of the first quarter . It soon became Utah 's game to lose , as the trio of Donovan Mitchell , Rudy Gobert , and Joe Ingles helped the Jazz rack up 68 points by halftime . Utah 's efficiency was a contributing factor in their strong offensive play , as the team shot over 51 percent from the field and 48 percent from three - point range . Mitchell was the game 's top scorer , finishing with 24 points on 8 - of - 21 shooting . He did , though , commit five turnovers on the night . Ingles , meanwhile , scored 22 points and shot 9 - of - 12 from the field . He added four steals on the defensive end . Of course , the story of the night on the defensive end was Rudy Gobert . The reigning Defensive Player of the Year finished the game with 15 rebounds and blocked three shots . On Sacramento 's side , all eyes were on second overall pick Marvin Bagley , who made his NBA debut in the game . Despite his status as a top pick , Bagley came off the bench and played only 12 minutes in his first appearance . He made the most of those minutes , though , scoring six points and grabbing five rebounds . Center Willie Cauley-Stein scored a team - high 23 points in 38 minutes of play . The former Kentucky star also dished out four assists and blocked two shots . Sophomore point guard De'Aaron Fox added 21 points and dished out seven assists as well . On Friday , the Kings will visit New Orleans while Utah will host the defending champion Golden State Warriors .
````

### Full System output

````markdown
The Utah Jazz defeated the Sacramento Kings 123-117 at Golden 1 Center on Wednesday, October 17, 2018.
The contest was the opening game of the 2018 campaign for both teams — and Sacramento's home opener — with the Jazz improving to 1-0 and the Kings falling to 0-1.
Utah also held the better conference standing, arriving in sixth place compared with the Kings' 13th.
Sacramento jumped out to a 34-30 lead after the first quarter, but Utah answered with a 38-21 second quarter — the Jazz's highest-scoring period — to lead 68-55 at halftime.
The Kings responded with a 32-25 third quarter to trim the advantage to 93-87, and the fourth quarter was level at 30-30 before Utah closed out the 123-117 win.
Donovan Mitchell led all scorers with 24 points, while Joe Ingles added 22 points, six assists and a game-high four steals for the Jazz.
Rudy Gobert anchored the interior with a game-high 15 rebounds (12 defensive), three blocks and 19 points, and Derrick Favors contributed 18 points and nine rebounds.
Sacramento was paced by Willie Cauley-Stein's 23 points on a game-high 10 made field goals, while De'Aaron Fox contributed 21 points, a game-high seven assists and three steals.
Buddy Hield (19 points) and Nemanja Bjelica (18 points and eight rebounds) also reached double figures for the Kings.
Ingles' nine made field goals were tied for the second-most in the game.
The teams produced contrasting shot profiles: while Sacramento out-shot Utah from the field (49 made field goals to 41), the Jazz held a clear edge in three-pointers made (13 to 7) and a 28-to-12 advantage in made free throws.
Utah also held the advantage in total rebounds (44-37), defensive rebounds (39-32), assists (21-17) and blocks (4-3), while the teams finished tied in offensive rebounds (5) and steals (8).
Both teams return to action on Friday, October 19, 2018, when the Jazz host the Warriors at Vivint Smart Home Arena and the Kings visit the New Orleans Pelicans at Smoothie King Center.
````

### Baseline output

````markdown
The visiting Utah Jazz defeated the Sacramento Kings 123–117 on October 17, 2018, at a sold-out Golden 1 Center (attendance 17,600, full capacity). Utah outscored Sacramento in three-point shooting (13 made threes on 48% shooting vs. 7 on 37%), free throws (28/38 vs. 12/18), rebounds (44–37), and assists (21–17). Sacramento committed fewer turnovers (9 vs. 17) and had more field-goal attempts (95 vs. 79), but the Jazz's efficiency from deep and the foul line proved decisive. Donovan Mitchell led all scorers with 24 points, Joe Ingles added 22, Rudy Gobert posted a double-double (19 points, 15 rebounds), and Derrick Favors scored 18. For the Kings, Willie Cauley-Stein scored 23, De'Aaron Fox added 21, Buddy Hield scored 19, and Nemanja Bjelica contributed 18.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.1103 | 0.0986 | -0.0117 | Baseline |
| BERTScore F1 | Higher | 0.8250 | 0.8424 | 0.0173 | Full System |
| BLEU | Higher | 0.0403 | 0.0686 | 0.0283 | Full System |
| chrF | Higher | 0.2453 | 0.4301 | 0.1849 | Full System |
| HHEM mean support | Higher | 0.0493 | 0.0244 | -0.0249 | Baseline |
| HHEM minimum sentence support | Higher | 0.0065 | 0.0041 | -0.0024 | Baseline |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.1184 | 0.2741 | 0.1556 | Full System |
| ROUGE-1 | Higher | 0.3702 | 0.5097 | 0.1395 | Full System |
| ROUGE-2 | Higher | 0.1315 | 0.1414 | 0.0098 | Full System |
| ROUGE-L | Higher | 0.2122 | 0.2279 | 0.0157 | Full System |
| ROUGE-Lsum | Higher | 0.2122 | 0.2279 | 0.0157 | Full System |
| TER | Lower | 0.8490 | 0.8969 | -0.0478 | Baseline |

### GPT-5.6 Sol structured annotations

**Full System**

1. **CONTEXT**
   - Error span: arriving in sixth place compared with the Kings' 13th
   - Correction or explanation: The source lists Utah's conference standing as sixth and Sacramento's as 13th, but does not establish that these were their standings entering the game. Avoid the pregame implication of “arriving.”
2. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode is a multi-paragraph report, so the report should be divided into at least two paragraphs.

**Baseline**

1. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode was a multi-paragraph report. The content should be divided into at least two coherent paragraphs, for example separating the result/team contrasts from the individual performances.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T004257Z_df24b18c95 |
| Execution outcome | success |
| Final generation path | auditor_repaired |
| Final Writer mode | auditor_repaired |
| Release status | approved |
| Audit decision | pass |
| Repair rounds | 1 |
| Native support rate | 1.0000 |
| Factual sentences | 12 |
| Supported sentences | 12 |
| Evidence items | 41 |
| Verified facts | 40 |
| Rejected facts | 0 |
| Verified insights | 3 |
| Rejected insights | 4 |
| Full System words | 334 |
| Baseline words | 122 |
| Full System elapsed seconds | 1398.0258 |
| Baseline elapsed seconds | 7.1140 |
| Full System provider-reported tokens | 813172 |
| Baseline provider-reported tokens | 9347 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/sportsett_basketball__5372/full_system/sportsett_basketball/20260821T004257Z_df24b18c95/pipeline_result.json |

## A11. e2e_nlg / e2e_nlg-test-447

| Field | Value |
| --- | --- |
| Dataset | e2e_nlg |
| Example ID | e2e_nlg-test-447 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | ee20f1488f496eb0fa489b07f5fb0d6f77c740eb5148166dae377bca9b9ff4ca |
| Reference SHA-256 | 94a4d50214686760602a9c1c5c903df9ffc684adbed2fc0b1d14c37cdbb91e06 |
| Full System request | Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
name[The Mill], eatType[pub], food[English], familyFriendly[no], near[Raja Indian Cuisine]
````

### Human reference outputs

**Reference 1**

````text
The Mill is a Luton based adults only pub, sited near Raja Indian Cuisine serving English food in the mid range bracket.
````

### Full System output

````markdown
The Mill is a pub that serves English food, is not family friendly, and is near Raja Indian Cuisine.
````

### Baseline output

````markdown
The Mill is a pub that serves English food, is not family-friendly, and is located near Raja Indian Cuisine.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.8796 | 0.9448 | 0.0651 | Full System |
| BERTScore F1 | Higher | 0.9209 | 0.9206 | -0.0003 | Baseline |
| BLEU | Higher | 0.2317 | 0.2317 | 0.0000 | Tie |
| chrF | Higher | 0.4749 | 0.4532 | -0.0217 | Baseline |
| HHEM mean support | Higher | 0.2092 | 0.2139 | 0.0046 | Full System |
| HHEM minimum sentence support | Higher | 0.2092 | 0.2139 | 0.0046 | Full System |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.3533 | 0.3533 | 0.0000 | Tie |
| ROUGE-1 | Higher | 0.5714 | 0.5854 | 0.0139 | Full System |
| ROUGE-2 | Higher | 0.4000 | 0.4103 | 0.0103 | Full System |
| ROUGE-L | Higher | 0.4286 | 0.4390 | 0.0105 | Full System |
| ROUGE-Lsum | Higher | 0.4286 | 0.4390 | 0.0105 | Full System |
| TER | Lower | 0.7273 | 0.7273 | 0.0000 | Tie |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T010615Z_718ad58c86 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 0 |
| Supported sentences | 0 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 19 |
| Baseline words | 19 |
| Full System elapsed seconds | 10.3916 |
| Baseline elapsed seconds | 1.2711 |
| Full System provider-reported tokens | 6506 |
| Baseline provider-reported tokens | 256 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/e2e_nlg__e2e_nlg-test-447/full_system/e2e_nlg/20260821T010615Z_718ad58c86/pipeline_result.json |

## A12. web_nlg / web_nlg_en-test-1466

| Field | Value |
| --- | --- |
| Dataset | web_nlg |
| Example ID | web_nlg_en-test-1466 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | ceda5e34141ed6d3857c4ea8e2e05f21e7098cf4f2c6fe0eb35471edeeaf60ee |
| Reference SHA-256 | 0944315b3912e63a7949969411805989726f2e28d27211c704460c9fd1606042 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Ciudad_Ayala | timeZone | Pacific_Daylight_Time
````

### Human reference outputs

**Reference 1**

````text
Ciudad Ayala is in the PDT time zone.
````

**Reference 2**

````text
Ciudad Ayala's time zone is Pacific Daylight Time.
````

**Reference 3**

````text
Ciudad Ayala is located in the Pacific Daylight time zone.
````

### Full System output

````markdown
Ciudad Ayala is in the Pacific Daylight Time time zone.
````

### Baseline output

````markdown
The data shows that Ciudad_Ayala is in the Pacific Daylight Time time zone.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.5842 | 0.8963 | 0.3120 | Full System |
| BERTScore F1 | Higher | 0.9425 | 0.9898 | 0.0473 | Full System |
| BLEU | Higher | 0.3943 | 0.7158 | 0.3215 | Full System |
| chrF | Higher | 0.6460 | 0.7652 | 0.1192 | Full System |
| HHEM mean support | Higher | 0.9050 | 0.8480 | -0.0570 | Baseline |
| HHEM minimum sentence support | Higher | 0.9050 | 0.8480 | -0.0570 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.6529 | 0.8833 | 0.2305 | Full System |
| ROUGE-1 | Higher | 0.7500 | 0.9000 | 0.1500 | Full System |
| ROUGE-2 | Higher | 0.6364 | 0.7778 | 0.1414 | Full System |
| ROUGE-L | Higher | 0.7500 | 0.9000 | 0.1500 | Full System |
| ROUGE-Lsum | Higher | 0.7500 | 0.9000 | 0.1500 | Full System |
| TER | Lower | 0.8077 | 0.2308 | 0.5769 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T010626Z_5c736a6ff8 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 0 |
| Supported sentences | 0 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 10 |
| Baseline words | 13 |
| Full System elapsed seconds | 6.7230 |
| Baseline elapsed seconds | 1.5438 |
| Full System provider-reported tokens | 5945 |
| Baseline provider-reported tokens | 264 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/web_nlg__web_nlg_en-test-1466/full_system/web_nlg/20260821T010626Z_5c736a6ff8/pipeline_result.json |

## A13. dart / dart-test-1828

| Field | Value |
| --- | --- |
| Dataset | dart |
| Example ID | dart-test-1828 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 943f0cf7a385a91bb9ae4340fc1c3f852658d553173f9aacb7b19e5c8036e1c0 |
| Reference SHA-256 | 0d539c5af7762ac1859ecb654efbff4c76292ab5629b138b455834c2a2d98c92 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
A.C. Lumezzane | FULL_NAME | "Associazione Calcio Lumezzane SpA"
A.C. Lumezzane | LEAGUE | "Lega Pro/A"
A.C. Lumezzane | NUMBER_OF_MEMBERS | 4150
````

### Human reference outputs

**Reference 1**

````text
The "Associazione Calcio Lumezzane SpA" is the full name of A.C. Lumezzane who play in Lega Pro/A and have 4150 members.
````

**Reference 2**

````text
Associazione Calcio Lumezzane SpA (abbreviated to A.C. Lumezzane) play in the Lega Pro/A and has 4150 members.
````

**Reference 3**

````text
The fullname of A.C. Lumezzane is Associazione Calcio Lumezzane SpA. It is in the Lega Pro/A league and has 4150 members.
````

### Full System output

````markdown
A.C. Lumezzane, whose full name is Associazione Calcio Lumezzane SpA, competes in Lega Pro/A and has 4150 members.
````

### Baseline output

````markdown
The strongest supported findings are that A.C. Lumezzane's full name is "Associazione Calcio Lumezzane SpA," it competes in the "Lega Pro/A" league, and it has 4,150 members.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.0014 | 0.4017 | 0.4003 | Full System |
| BERTScore F1 | Higher | 0.9451 | 0.9586 | 0.0135 | Full System |
| BLEU | Higher | 0.2606 | 0.6421 | 0.3815 | Full System |
| chrF | Higher | 0.5964 | 0.6907 | 0.0943 | Full System |
| HHEM mean support | Higher | 0.5762 | 0.7298 | 0.1535 | Full System |
| HHEM minimum sentence support | Higher | 0.3764 | 0.5998 | 0.2234 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.5000 | 0.0000 | 0.5000 | Full System |
| METEOR | Higher | 0.3948 | 0.6278 | 0.2330 | Full System |
| ROUGE-1 | Higher | 0.7037 | 0.7907 | 0.0870 | Full System |
| ROUGE-2 | Higher | 0.5000 | 0.5946 | 0.0946 | Full System |
| ROUGE-L | Higher | 0.7037 | 0.7442 | 0.0405 | Full System |
| ROUGE-Lsum | Higher | 0.7037 | 0.7442 | 0.0405 | Full System |
| TER | Lower | 0.8136 | 0.5085 | 0.3051 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T010632Z_beec1e5b68 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 18 |
| Baseline words | 27 |
| Full System elapsed seconds | 9.9374 |
| Baseline elapsed seconds | 1.8486 |
| Full System provider-reported tokens | 6637 |
| Baseline provider-reported tokens | 359 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/dart__dart-test-1828/full_system/dart/20260821T010632Z_beec1e5b68/pipeline_result.json |

## A14. totto / totto-validation-6067

| Field | Value |
| --- | --- |
| Dataset | totto |
| Example ID | totto-validation-6067 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source SHA-256 | 93ea1c14d25c908009aadf5d17515d948625a4673384762f1e058b9319db1c05 |
| Reference SHA-256 | bddc524b00580d101af2646170f1309589439cffb40ef1626fc3a61fb14e3f83 |
| Full System request | Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Page: Peruvians in Italy
Section: History
Table:
Year | Peruvian-born population | Other data
2001 |  | 26,831
2006 |  | 66.506
2007 |  | 70.755
2008 |  | 77.629
2009 |  | 87.747
2010 | 225,795 | 98.603
*2011* | *246,908* | 
2012 |  | 
2013 |  | 
Cells surrounded by * are highlighted.
````

### Human reference outputs

**Reference 1**

````text
In 2011, Italy had 246,908 immigrants from Peru.
````

**Reference 2**

````text
In 2011, Italy had 246,908 inhabitants of Peru.
````

### Full System output

````markdown
In 2011, the Peruvian-born population in Italy was 246,908.
````

### Baseline output

````markdown
The strongest supported findings are: (1) the only highlighted figure is the 2011 Peruvian-born population of 246,908, the largest number shown in the table; and (2) the “other data” column rises steadily from 26,831 in 2001 to 98,603 in 2010, with no figures provided for 2012 or 2013.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.0604 | 0.9334 | 0.8730 | Full System |
| BERTScore F1 | Higher | 0.8648 | 0.9438 | 0.0790 | Full System |
| BLEU | Higher | 0.0100 | 0.1659 | 0.1559 | Full System |
| chrF | Higher | 0.1729 | 0.3924 | 0.2195 | Full System |
| HHEM mean support | Higher | 0.6189 | 0.8844 | 0.2655 | Full System |
| HHEM minimum sentence support | Higher | 0.6189 | 0.8844 | 0.2655 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.0833 | 0.1852 | 0.1019 | Full System |
| ROUGE-1 | Higher | 0.1639 | 0.5000 | 0.3361 | Full System |
| ROUGE-2 | Higher | 0.0339 | 0.2222 | 0.1883 | Full System |
| ROUGE-L | Higher | 0.1311 | 0.5000 | 0.3689 | Full System |
| ROUGE-Lsum | Higher | 0.1311 | 0.5000 | 0.3689 | Full System |
| TER | Lower | 5.7500 | 0.8750 | 4.8750 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

1. **TASK/FORMAT**
   - Error span: the largest number shown in the table; and (2) the “other data” column rises steadily from 26,831 in 2001 to 98,603 in 2010, with no figures provided for 2012 or 2013
   - Correction or explanation: This compares the highlighted value with unhighlighted cells and describes the unhighlighted “other data” column, contrary to the instruction not to discuss unrelated cells. The sentence should focus only on the highlighted 2011 Peruvian-born population of 246,908.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T010643Z_3e17181bc2 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 9 |
| Baseline words | 48 |
| Full System elapsed seconds | 7.5640 |
| Baseline elapsed seconds | 4.3832 |
| Full System provider-reported tokens | 6949 |
| Baseline provider-reported tokens | 681 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/totto__totto-validation-6067/full_system/totto/20260821T010643Z_3e17181bc2/pipeline_result.json |

## A15. sportsett_basketball / 5786

| Field | Value |
| --- | --- |
| Dataset | sportsett_basketball |
| Example ID | 5786 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source SHA-256 | 2d380f4702e071a20f97f90c6d2771c5357144f5f890c974fe06cab042aaf70d |
| Reference SHA-256 | bb95fec76d8be49f9311a03c0fbf3396fdab22b489d16729eec104139375f72e |
| Full System request | Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````json
{
  "game": {
    "attendance": "19800",
    "capacity": "19800",
    "city": "Toronto",
    "day": "26",
    "dayname": "Friday",
    "game_id": "5786",
    "month": "October",
    "season": "2018",
    "stadium": "Scotiabank Arena",
    "state": "Ontario",
    "year": "2018"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "11",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "4",
          "FG_PCT": "50",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "37",
          "OREB": "1",
          "PF": "3",
          "PTS": "10",
          "STL": "1",
          "TOV": "3",
          "TREB": "7",
          "first_name": "Pascal",
          "last_name": "Siakam",
          "name": "Pascal Siakam",
          "starter": "True"
        },
        {
          "+/-": "6",
          "AST": "12",
          "BLK": "1",
          "DOUBLE": "double",
          "DREB": "4",
          "FG3A": "6",
          "FG3M": "3",
          "FG3_PCT": "50",
          "FGA": "14",
          "FGM": "8",
          "FG_PCT": "57",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "35",
          "OREB": "0",
          "PF": "2",
          "PTS": "20",
          "STL": "0",
          "TOV": "0",
          "TREB": "4",
          "first_name": "Kyle",
          "last_name": "Lowry",
          "name": "Kyle Lowry",
          "starter": "True"
        },
        {
          "+/-": "5",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "8",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "16",
          "FGM": "7",
          "FG_PCT": "44",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "34",
          "OREB": "1",
          "PF": "0",
          "PTS": "21",
          "STL": "3",
          "TOV": "0",
          "TREB": "9",
          "first_name": "Kawhi",
          "last_name": "Leonard",
          "name": "Kawhi Leonard",
          "starter": "True"
        },
        {
          "+/-": "4",
          "AST": "0",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "7",
          "FG3M": "4",
          "FG3_PCT": "57",
          "FGA": "8",
          "FGM": "4",
          "FG_PCT": "50",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "30",
          "OREB": "2",
          "PF": "3",
          "PTS": "15",
          "STL": "1",
          "TOV": "0",
          "TREB": "8",
          "first_name": "Danny",
          "last_name": "Green",
          "name": "Danny Green",
          "starter": "True"
        },
        {
          "+/-": "12",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "16",
          "FGM": "7",
          "FG_PCT": "44",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "22",
          "OREB": "5",
          "PF": "4",
          "PTS": "17",
          "STL": "1",
          "TOV": "1",
          "TREB": "8",
          "first_name": "Jonas",
          "last_name": "Valančiūnas",
          "name": "Jonas Valančiūnas",
          "starter": "True"
        },
        {
          "+/-": "-3",
          "AST": "1",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "13",
          "FGM": "5",
          "FG_PCT": "38",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "25",
          "OREB": "2",
          "PF": "2",
          "PTS": "11",
          "STL": "0",
          "TOV": "5",
          "TREB": "8",
          "first_name": "Serge",
          "last_name": "Ibaka",
          "name": "Serge Ibaka",
          "starter": "False"
        },
        {
          "+/-": "8",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "1",
          "FGM": "1",
          "FG_PCT": "100",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "19",
          "OREB": "0",
          "PF": "1",
          "PTS": "2",
          "STL": "1",
          "TOV": "1",
          "TREB": "2",
          "first_name": "Norman",
          "last_name": "Powell",
          "name": "Norman Powell",
          "starter": "False"
        },
        {
          "+/-": "5",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "8",
          "FGM": "4",
          "FG_PCT": "50",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "15",
          "OREB": "0",
          "PF": "2",
          "PTS": "9",
          "STL": "2",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Lorenzo",
          "last_name": "Brown",
          "name": "Lorenzo Brown",
          "starter": "False"
        },
        {
          "+/-": "-5",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "2",
          "FG3M": "2",
          "FG3_PCT": "100",
          "FGA": "6",
          "FGM": "4",
          "FG_PCT": "67",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "11",
          "OREB": "0",
          "PF": "4",
          "PTS": "10",
          "STL": "1",
          "TOV": "1",
          "TREB": "2",
          "first_name": "C.J.",
          "last_name": "Miles",
          "name": "C.J. Miles",
          "starter": "False"
        },
        {
          "+/-": "2",
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
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "8",
          "OREB": "1",
          "PF": "1",
          "PTS": "1",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Malachi",
          "last_name": "Richardson",
          "name": "Malachi Richardson",
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
          "first_name": "Greg",
          "last_name": "Monroe",
          "name": "Greg Monroe",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 1,
      "division": "Atlantic",
      "game_number": "6",
      "line_score": {
        "H1": {
          "AST": "106",
          "BLK": "21",
          "DREB": "127",
          "FG3A": "116",
          "FG3M": "44",
          "FG3_PCT": "38",
          "FGA": "2423",
          "FGM": "1312",
          "FG_PCT": "54",
          "FTA": "102",
          "FTM": "92",
          "FT_PCT": "90",
          "MIN": "6060",
          "OREB": "42",
          "PTS": "3930",
          "STL": "22",
          "TOV": "23",
          "TREB": "169"
        },
        "H2": {
          "AST": "25",
          "BLK": "11",
          "DREB": "811",
          "FG3A": "37",
          "FG3M": "21",
          "FG3_PCT": "57",
          "FGA": "1925",
          "FGM": "910",
          "FG_PCT": "47",
          "FTA": "44",
          "FTM": "33",
          "FT_PCT": "75",
          "MIN": "6060",
          "OREB": "15",
          "PTS": "2324",
          "STL": "06",
          "TOV": "43",
          "TREB": "826"
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
          "BLK": "2",
          "DREB": "12",
          "FG3A": "11",
          "FG3M": "4",
          "FG3_PCT": "36",
          "FGA": "24",
          "FGM": "13",
          "FG_PCT": "54",
          "FTA": "10",
          "FTM": "9",
          "FT_PCT": "90",
          "MIN": "60",
          "OREB": "4",
          "PTS": "39",
          "STL": "2",
          "TOV": "2",
          "TREB": "16"
        },
        "Q2": {
          "AST": "6",
          "BLK": "1",
          "DREB": "7",
          "FG3A": "6",
          "FG3M": "4",
          "FG3_PCT": "67",
          "FGA": "23",
          "FGM": "12",
          "FG_PCT": "52",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "2",
          "PTS": "30",
          "STL": "2",
          "TOV": "3",
          "TREB": "9"
        },
        "Q3": {
          "AST": "2",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "19",
          "FGM": "9",
          "FG_PCT": "47",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "1",
          "PTS": "23",
          "STL": "0",
          "TOV": "4",
          "TREB": "9"
        },
        "Q4": {
          "AST": "5",
          "BLK": "1",
          "DREB": "11",
          "FG3A": "7",
          "FG3M": "1",
          "FG3_PCT": "14",
          "FGA": "25",
          "FGM": "10",
          "FG_PCT": "40",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "60",
          "OREB": "5",
          "PTS": "24",
          "STL": "6",
          "TOV": "3",
          "TREB": "16"
        },
        "game": {
          "AST": "23",
          "BLK": "5",
          "DREB": "38",
          "FG3A": "27",
          "FG3M": "11",
          "FG3_PCT": "41",
          "FGA": "91",
          "FGM": "44",
          "FG_PCT": "48",
          "FTA": "20",
          "FTM": "17",
          "FT_PCT": "85",
          "MIN": "4",
          "OREB": "12",
          "PF": "22",
          "PTS": "116",
          "STL": "10",
          "TOV": "12",
          "TREB": "50"
        }
      },
      "losses": "0",
      "name": "Raptors",
      "next_game": {
        "city": "Milwaukee",
        "day": "29",
        "dayname": "Monday",
        "is_home": "False",
        "month": "October",
        "opponent_name": "Bucks",
        "opponent_place": "Milwaukee",
        "stadium": "Fiserv Forum",
        "year": "2018"
      },
      "next_game_id": "4966",
      "place": "Toronto",
      "previous_game_id": "5785",
      "wins": "6"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "0",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "6",
          "FG3M": "4",
          "FG3_PCT": "67",
          "FGA": "14",
          "FGM": "7",
          "FG_PCT": "50",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "35",
          "OREB": "1",
          "PF": "1",
          "PTS": "22",
          "STL": "0",
          "TOV": "3",
          "TREB": "5",
          "first_name": "Luka",
          "last_name": "Dončić",
          "name": "Luka Dončić",
          "starter": "True"
        },
        {
          "+/-": "0",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "double",
          "DREB": "10",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "10",
          "FGM": "5",
          "FG_PCT": "50",
          "FTA": "9",
          "FTM": "8",
          "FT_PCT": "89",
          "MIN": "33",
          "OREB": "5",
          "PF": "1",
          "PTS": "18",
          "STL": "0",
          "TOV": "2",
          "TREB": "15",
          "first_name": "DeAndre",
          "last_name": "Jordan",
          "name": "DeAndre Jordan",
          "starter": "True"
        },
        {
          "+/-": "-8",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "8",
          "FG3M": "3",
          "FG3_PCT": "38",
          "FGA": "15",
          "FGM": "9",
          "FG_PCT": "60",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "32",
          "OREB": "0",
          "PF": "4",
          "PTS": "21",
          "STL": "0",
          "TOV": "2",
          "TREB": "0",
          "first_name": "Wesley",
          "last_name": "Matthews",
          "name": "Wesley Matthews",
          "starter": "True"
        },
        {
          "+/-": "-3",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "4",
          "FG3M": "2",
          "FG3_PCT": "50",
          "FGA": "11",
          "FGM": "3",
          "FG_PCT": "27",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "29",
          "OREB": "0",
          "PF": "2",
          "PTS": "8",
          "STL": "1",
          "TOV": "2",
          "TREB": "3",
          "first_name": "Jalen",
          "last_name": "Brunson",
          "name": "Jalen Brunson",
          "starter": "True"
        },
        {
          "+/-": "-24",
          "AST": "3",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "17",
          "FGM": "5",
          "FG_PCT": "29",
          "FTA": "5",
          "FTM": "3",
          "FT_PCT": "60",
          "MIN": "28",
          "OREB": "1",
          "PF": "2",
          "PTS": "14",
          "STL": "0",
          "TOV": "1",
          "TREB": "6",
          "first_name": "Harrison",
          "last_name": "Barnes",
          "name": "Harrison Barnes",
          "starter": "True"
        },
        {
          "+/-": "-1",
          "AST": "1",
          "BLK": "4",
          "DOUBLE": "none",
          "DREB": "7",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "6",
          "FGM": "2",
          "FG_PCT": "33",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "30",
          "OREB": "1",
          "PF": "0",
          "PTS": "8",
          "STL": "2",
          "TOV": "0",
          "TREB": "8",
          "first_name": "Maxi",
          "last_name": "Kleber",
          "name": "Maxi Kleber",
          "starter": "False"
        },
        {
          "+/-": "2",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "6",
          "FGM": "2",
          "FG_PCT": "33",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "19",
          "OREB": "1",
          "PF": "4",
          "PTS": "5",
          "STL": "1",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Dorian",
          "last_name": "Finney-Smith",
          "name": "Dorian Finney-Smith",
          "starter": "False"
        },
        {
          "+/-": "-5",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "11",
          "FGM": "3",
          "FG_PCT": "27",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "15",
          "OREB": "1",
          "PF": "0",
          "PTS": "7",
          "STL": "0",
          "TOV": "2",
          "TREB": "2",
          "first_name": "J.J.",
          "last_name": "Barea",
          "name": "J.J. Barea",
          "starter": "False"
        },
        {
          "+/-": "-9",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "2",
          "FG_PCT": "100",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "14",
          "OREB": "0",
          "PF": "3",
          "PTS": "4",
          "STL": "2",
          "TOV": "2",
          "TREB": "2",
          "first_name": "Dwight",
          "last_name": "Powell",
          "name": "Dwight Powell",
          "starter": "False"
        },
        {
          "+/-": "3",
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
          "first_name": "Dennis",
          "last_name": "Smith",
          "name": "Dennis Smith",
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
          "first_name": "Salah",
          "last_name": "Mejri",
          "name": "Salah Mejri",
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
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 10,
      "division": "Southwest",
      "game_number": "5",
      "line_score": {
        "H1": {
          "AST": "39",
          "BLK": "03",
          "DREB": "88",
          "FG3A": "97",
          "FG3M": "24",
          "FG3_PCT": "25",
          "FGA": "2323",
          "FGM": "913",
          "FG_PCT": "39",
          "FTA": "74",
          "FTM": "64",
          "FT_PCT": "86",
          "MIN": "6060",
          "OREB": "02",
          "PTS": "2634",
          "STL": "12",
          "TOV": "23",
          "TREB": "90"
        },
        "H2": {
          "AST": "55",
          "BLK": "21",
          "DREB": "99",
          "FG3A": "86",
          "FG3M": "42",
          "FG3_PCT": "49",
          "FGA": "2224",
          "FGM": "97",
          "FG_PCT": "4",
          "FTA": "103",
          "FTM": "72",
          "FT_PCT": "70",
          "MIN": "6060",
          "OREB": "35",
          "PTS": "2918",
          "STL": "12",
          "TOV": "27",
          "TREB": "134"
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
          "BLK": "0",
          "DREB": "8",
          "FG3A": "9",
          "FG3M": "2",
          "FG3_PCT": "22",
          "FGA": "23",
          "FGM": "9",
          "FG_PCT": "39",
          "FTA": "7",
          "FTM": "6",
          "FT_PCT": "86",
          "MIN": "60",
          "OREB": "0",
          "PTS": "26",
          "STL": "1",
          "TOV": "2",
          "TREB": "8"
        },
        "Q2": {
          "AST": "9",
          "BLK": "3",
          "DREB": "8",
          "FG3A": "7",
          "FG3M": "4",
          "FG3_PCT": "57",
          "FGA": "23",
          "FGM": "13",
          "FG_PCT": "57",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "2",
          "PTS": "34",
          "STL": "2",
          "TOV": "3",
          "TREB": "10"
        },
        "Q3": {
          "AST": "5",
          "BLK": "2",
          "DREB": "9",
          "FG3A": "8",
          "FG3M": "4",
          "FG3_PCT": "50",
          "FGA": "22",
          "FGM": "9",
          "FG_PCT": "41",
          "FTA": "10",
          "FTM": "7",
          "FT_PCT": "70",
          "MIN": "60",
          "OREB": "3",
          "PTS": "29",
          "STL": "1",
          "TOV": "2",
          "TREB": "12"
        },
        "Q4": {
          "AST": "5",
          "BLK": "1",
          "DREB": "9",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "24",
          "FGM": "7",
          "FG_PCT": "29",
          "FTA": "3",
          "FTM": "2",
          "FT_PCT": "67",
          "MIN": "60",
          "OREB": "5",
          "PTS": "18",
          "STL": "2",
          "TOV": "7",
          "TREB": "14"
        },
        "game": {
          "AST": "22",
          "BLK": "6",
          "DREB": "34",
          "FG3A": "30",
          "FG3M": "12",
          "FG3_PCT": "40",
          "FGA": "92",
          "FGM": "38",
          "FG_PCT": "41",
          "FTA": "24",
          "FTM": "19",
          "FT_PCT": "79",
          "MIN": "4",
          "OREB": "10",
          "PF": "17",
          "PTS": "107",
          "STL": "6",
          "TOV": "14",
          "TREB": "44"
        }
      },
      "losses": "3",
      "name": "Mavericks",
      "next_game": {
        "city": "Dallas",
        "day": "28",
        "dayname": "Sunday",
        "is_home": "True",
        "month": "October",
        "opponent_name": "Jazz",
        "opponent_place": "Utah",
        "stadium": "American Airlines Center",
        "year": "2018"
      },
      "next_game_id": "5538",
      "place": "Dallas",
      "previous_game_id": "5208",
      "wins": "2"
    }
  }
}
````

### Human reference outputs

**Reference 1**

````text
The Toronto Raptors defeated the Dallas Mavericks, 116 - 107, at Scotiabank Arena on Friday evening. The Raptors (60) had proven invincible at home coming into Friday's contest, and their level of play in the first quarter was a good example of why. Toronto jumped on the Mavericks (2 - 3) early, establishing a 39 - 26 lead. While Dallas managed to bring their deficit down to a slim three points entering the final period, the home squad stepped up, outscoring the visitors by a 24 - 18 margin. Both shooting and rebounding were keys to victory, as the Raptors enjoyed a 48 percent - 41 percent advantage from the field and a 50 - 44 edge on the boards. Luka Doncic paced the Mavericks with 22 points, which he complemented with five rebounds and four assists. Wesley Matthews supplied 21 points and dished out one assist. DeAndre Jordan generated an 18 - point, 15 - rebound double - double that also included five assists and one block. Harrison Barnes turned in 14 points, six rebounds, three assists and one block. Jalen Brunson, who started for Dennis Smith, Jr. (ankle), and Maxi Kleber both generated eight - point deficits. Kawhi Leonard paced the Raptors with 21 points, nine rebounds, five assists, three steals and one block. Kyle Lowry posted a 20 - point, 12 - assist double - double that also included four rebounds and a block. Jonas Valanciunas started and managed 17 points, eight rebounds, one assist and one steal. Danny Green poured in 15 points and added eight rebounds, one steal and one block. Serge Ibaka pitched in a bench - leading 11 points along with eight rebounds, an assist and two blocks. The Mavericks heads back home and take on the Utah Jazz on Sunday evening, while the Raptors pay a visit to the Milwaukee Bucks on Monday night.
````

**Reference 2**

````text
The Toronto Raptors defeated the Dallas Mavericks , 116 - 107 , at Scotiabank Arena on Friday evening . The Raptors ( 60 ) had proven invincible at home coming into Friday 's contest , and their level of play in the first quarter was a good example of why . Toronto jumped on the Mavericks ( 2 - 3 ) early , establishing a 39 - 26 lead . While Dallas managed to bring their deficit down to a slim three points entering the final period , the home squad stepped up , outscoring the visitors by a 24 - 18 margin . Both shooting and rebounding were keys to victory , as the Raptors enjoyed a 48 percent - 41 percent advantage from the field and a 50 - 44 edge on the boards . Luka Doncic paced the Mavericks with 22 points , which he complemented with five rebounds and four assists . Wesley Matthews supplied 21 points and dished out one assist . DeAndre Jordan generated an 18 - point , 15 - rebound double - double that also included five assists and one block . Harrison Barnes turned in 14 points , six rebounds , three assists and one block . Jalen Brunson , who started for Dennis Smith , Jr. ( ankle ) , and Maxi Kleber both generated eight - point deficits . Kawhi Leonard paced the Raptors with 21 points , nine rebounds , five assists , three steals and one block . Kyle Lowry posted a 20 - point , 12 - assist double - double that also included four rebounds and a block . Jonas Valanciunas started and managed 17 points , eight rebounds , one assist and one steal . Danny Green poured in 15 points and added eight rebounds , one steal and one block . Serge Ibaka pitched in a bench - leading 11 points along with eight rebounds , an assist and two blocks . The Mavericks heads back home and take on the Utah Jazz on Sunday evening , while the Raptors pay a visit to the Milwaukee Bucks on Monday night .
````

### Full System output

````markdown
The Toronto Raptors defeated the Dallas Mavericks 116-107 on Friday, October 26, 2018, at Scotiabank Arena in the 2018 season.
Toronto entered with a 6-0 record and first place in its conference standings, while Dallas arrived at 2-3.
It was Toronto's sixth game of the season and Dallas's fifth.
Toronto led after every quarter: 39-26 after the first, 69-60 at halftime, 92-89 after the third, and 116-107 at the end.
Dallas outscored Toronto in the middle quarters (34-30 in the second and 29-23 in the third), but the Raptors' 39-26 start and 24-18 finish kept them in front.
Luka Dončić led all scorers with 22 points, while Kawhi Leonard and Wesley Matthews tied for second with 21 apiece.
Leonard complemented his scoring with 9 rebounds, 5 assists, 3 steals and a block, while Kyle Lowry added 20 points and a game-high 12 assists.
DeAndre Jordan paced Dallas with 15 rebounds, including 10 defensive rebounds, and added 18 points and 5 assists; he and Jonas Valančiūnas each collected 5 offensive rebounds.
Wesley Matthews made a game-high 9 field goals, Maxi Kleber led all players with 4 blocks, and Serge Ibaka added 11 points and 8 rebounds for Toronto.
The Raptors held the shooting and rebounding edges, making more field goals (44-38) and grabbing more total rebounds (50-44), although the Mavericks attempted more field goals (92-91).
Dallas had the edge from three-point range, making 12 three-pointers to Toronto's 11, with Dončić and Danny Green each hitting 4.
Toronto also recorded more defensive rebounds (38-34), offensive rebounds (12-10), steals (10-6) and assists (23-22), while Dallas led in blocks (6-5) and free throws made (19-17).
Both teams had immediate follow-up fixtures: Toronto travelled to Milwaukee to face the Bucks on Monday, October 29, while Dallas hosted the Jazz on Sunday, October 28.
````

### Baseline output

````markdown
- The Toronto Raptors defeated the Dallas Mavericks 116–107 at Scotiabank Arena on October 26, 2018, in front of a sold-out crowd of 19,800.
- The Raptors improved to 6–0 and held the No. 1 spot in the Eastern Conference; the Mavericks fell to 2–3 and stood 10th in the Western Conference.
- Toronto shot 48% from the field, 41% on three-pointers, and 85% on free throws; Dallas shot 41% from the field, 40% on threes, and 79% on free throws.
- The Raptors had seven players score in double figures, led by Kawhi Leonard (21 points, 9 rebounds, 5 assists, 3 steals), Kyle Lowry (20 points, 12 assists, double-double), and Jonas Valančiūnas (17 points, 8 rebounds).
- The Mavericks were led by Luka Dončić (22 points, 5 rebounds, 4 assists) and Wesley Matthews (21 points); DeAndre Jordan posted a double-double with 18 points and 15 rebounds.
- Toronto won the first and fourth quarters, while Dallas won the second and third quarters, but Toronto’s 13-point first-quarter margin helped secure the 9-point victory.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.0708 | 0.1005 | 0.0297 | Full System |
| BERTScore F1 | Higher | 0.8482 | 0.8558 | 0.0077 | Full System |
| BLEU | Higher | 0.0593 | 0.0893 | 0.0300 | Full System |
| chrF | Higher | 0.3126 | 0.4300 | 0.1174 | Full System |
| HHEM mean support | Higher | 0.0238 | 0.0335 | 0.0096 | Full System |
| HHEM minimum sentence support | Higher | 0.0127 | 0.0121 | -0.0006 | Baseline |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.2029 | 0.2793 | 0.0764 | Full System |
| ROUGE-1 | Higher | 0.4699 | 0.4928 | 0.0230 | Full System |
| ROUGE-2 | Higher | 0.1754 | 0.1722 | -0.0031 | Baseline |
| ROUGE-L | Higher | 0.2661 | 0.2289 | -0.0372 | Baseline |
| ROUGE-Lsum | Higher | 0.2661 | 0.2289 | -0.0372 | Baseline |
| TER | Lower | 0.7881 | 0.8507 | -0.0627 | Baseline |

### GPT-5.6 Sol structured annotations

**Full System**

1. **CONTEXT**
   - Error span: Toronto entered with a 6-0 record and first place in its conference standings, while Dallas arrived at 2-3.
   - Correction or explanation: The listed records are postgame records: Toronto improved to 6-0 and Dallas fell to 2-3. They did not enter the game with those records.
2. **TASK/FORMAT**
   - Error span: The entire report is presented as one paragraph.
   - Correction or explanation: The requested output mode was a multi-paragraph report, but the generated report contains only one paragraph.

**Baseline**

1. **TASK/FORMAT**
   - Error span: The entire generated output is presented as a six-item bullet list rather than a multi-paragraph report.
   - Correction or explanation: The request specifies a coherent multi-paragraph game report. The accurate points should be rewritten as connected prose across multiple paragraphs.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T010650Z_c25deef725 |
| Execution outcome | success |
| Final generation path | deterministic_fallback |
| Final Writer mode | llm_writer |
| Release status | approved |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 13 |
| Supported sentences | 13 |
| Evidence items | 42 |
| Verified facts | 42 |
| Rejected facts | 1 |
| Verified insights | 5 |
| Rejected insights | 3 |
| Full System words | 298 |
| Baseline words | 173 |
| Full System elapsed seconds | 840.3415 |
| Baseline elapsed seconds | 7.7733 |
| Full System provider-reported tokens | 514434 |
| Baseline provider-reported tokens | 9022 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/sportsett_basketball__5786/full_system/sportsett_basketball/20260821T010650Z_c25deef725/pipeline_result.json |

## A16. e2e_nlg / e2e_nlg-test-476

| Field | Value |
| --- | --- |
| Dataset | e2e_nlg |
| Example ID | e2e_nlg-test-476 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | dc16cc8d4dfa17c95af826014892da10e7adc35b3dfec6455e3e14a60dd75116 |
| Reference SHA-256 | 6d7229dffa4ca4a672bc73b14e4bd031d67f9a879f4a2cfeee3dddadb677541b |
| Full System request | Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
name[The Mill], eatType[pub], food[Fast food], customer rating[3 out of 5], area[riverside], familyFriendly[yes], near[Café Rouge]
````

### Human reference outputs

**Reference 1**

````text
Located in Riverside near Café Rouge there is a pub known as 'The Mill'. Has a good customer rating, is child friendly and has a good price range for fast food.
````

### Full System output

````markdown
The Mill is a riverside pub that serves fast food, has a customer rating of 3 out of 5, is family-friendly, and is near Café Rouge.
````

### Baseline output

````markdown
The Mill is a riverside pub that serves fast food, has a customer rating of 3 out of 5, is family-friendly, and is located near Café Rouge.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9834 | 0.9828 | -0.0006 | Baseline |
| BERTScore F1 | Higher | 0.9085 | 0.9081 | -0.0004 | Baseline |
| BLEU | Higher | 0.0842 | 0.0841 | -0.0002 | Baseline |
| chrF | Higher | 0.4261 | 0.4112 | -0.0149 | Baseline |
| HHEM mean support | Higher | 0.6271 | 0.6343 | 0.0072 | Full System |
| HHEM minimum sentence support | Higher | 0.6271 | 0.6343 | 0.0072 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.2961 | 0.2796 | -0.0165 | Baseline |
| ROUGE-1 | Higher | 0.6441 | 0.6207 | -0.0234 | Baseline |
| ROUGE-2 | Higher | 0.2807 | 0.2857 | 0.0050 | Full System |
| ROUGE-L | Higher | 0.3390 | 0.3448 | 0.0058 | Full System |
| ROUGE-Lsum | Higher | 0.3390 | 0.3448 | 0.0058 | Full System |
| TER | Lower | 0.7742 | 0.7742 | 0.0000 | Tie |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T012051Z_0fe9ddab53 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 26 |
| Baseline words | 27 |
| Full System elapsed seconds | 6.5065 |
| Baseline elapsed seconds | 1.9383 |
| Full System provider-reported tokens | 6226 |
| Baseline provider-reported tokens | 335 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/e2e_nlg__e2e_nlg-test-476/full_system/e2e_nlg/20260821T012051Z_0fe9ddab53/pipeline_result.json |

## A17. web_nlg / web_nlg_en-test-859

| Field | Value |
| --- | --- |
| Dataset | web_nlg |
| Example ID | web_nlg_en-test-859 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 850b090ceaacbc5f7faf4782b25926cf343176e102230332065c2f88daff7e34 |
| Reference SHA-256 | 8d32ebce4aaf2ab161d1495559f07b3f74fa982abc751bf28c8bb264c8d0c9aa |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Pontiac_Rageous | assembly | Detroit
````

### Human reference outputs

**Reference 1**

````text
The Pontiac Rageous assembly line is in Detroit.
````

**Reference 2**

````text
The Pontiac Rageous was assembled in Detroit.
````

### Full System output

````markdown
Pontiac Rageous was assembled in Detroit.
````

### Baseline output

````markdown
Pontiac Rageous was assembled in Detroit.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9696 | 0.9696 | 0.0000 | Tie |
| BERTScore F1 | Higher | 0.9688 | 0.9688 | 0.0000 | Tie |
| BLEU | Higher | 0.8669 | 0.8669 | 0.0000 | Tie |
| chrF | Higher | 0.9223 | 0.9223 | 0.0000 | Tie |
| HHEM mean support | Higher | 0.8579 | 0.8579 | 0.0000 | Tie |
| HHEM minimum sentence support | Higher | 0.8579 | 0.8579 | 0.0000 | Tie |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.8676 | 0.8676 | 0.0000 | Tie |
| ROUGE-1 | Higher | 0.9231 | 0.9231 | 0.0000 | Tie |
| ROUGE-2 | Higher | 0.9091 | 0.9091 | 0.0000 | Tie |
| ROUGE-L | Higher | 0.9231 | 0.9231 | 0.0000 | Tie |
| ROUGE-Lsum | Higher | 0.9231 | 0.9231 | 0.0000 | Tie |
| TER | Lower | 0.1333 | 0.1333 | 0.0000 | Tie |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T012058Z_5d63e851c3 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 0 |
| Supported sentences | 0 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 6 |
| Baseline words | 6 |
| Full System elapsed seconds | 17.5028 |
| Baseline elapsed seconds | 1.6266 |
| Full System provider-reported tokens | 12420 |
| Baseline provider-reported tokens | 257 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/web_nlg__web_nlg_en-test-859/full_system/web_nlg/20260821T012058Z_5d63e851c3/pipeline_result.json |

## A18. dart / dart-test-2278

| Field | Value |
| --- | --- |
| Dataset | dart |
| Example ID | dart-test-2278 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 83a08c4f27a66f1a6306ae6360a6ed977011c4ca6ded4a7b1df2f31b72c49479 |
| Reference SHA-256 | dce109bd22e76fd1ea233f5c335019f0b17608be71f544d9f143331402310cf6 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Al Asad Airbase | OPERATING_ORGANISATION | United States Air Force
United States Air Force | ATTACK_AIRCRAFT | Lockheed AC-130
United States Air Force | TRANSPORT_AIRCRAFT | Boeing C-17 Globemaster III
United States Air Force | AIRCRAFT_FIGHTER | General Dynamics F-16 Fighting Falcon
United States Air Force | BATTLES | 1986 United States bombing of Libya
````

### Human reference outputs

**Reference 1**

````text
The Lockheed AC-130 can be found on USAF aircraft carriers and the Boeing C-17 Globemaster III is a transport aircraft of the United States Air Force. The airforce also has the aircraft fighter the General Dynamics F-16 Fighting Falcon. The 1986 United States bombing of Libya was carried out by the United States Air Force which now operates Al Asad Airbase.
````

**Reference 2**

````text
Al Asad Airbase is operated by the United States Air Force which was involved in the 1986 United States bombing of Libya. Some of the Air Force's aircraft are the Lockheed AC-130 (an attack aircraft), Boeing C-17 Globemaster III (transport aircraft) and the General Dynamics F-16 Fighting Falcon (aircraft fighter).
````

**Reference 3**

````text
Al Asad air base is operated by the United States Air Force who were involved in the 1986 bombing of Libya. They deploy the Lockheed AC-130 on their aircraft carriers, use the Boeing C-17 Globemaster III transport aircraft and the General Dynamics F-16 Fighting Falcon fighter aircraft.
````

### Full System output

````markdown
Al Asad Airbase is operated by the United States Air Force, whose aircraft include the Lockheed AC-130 attack aircraft, Boeing C-17 Globemaster III transport aircraft, and General Dynamics F-16 Fighting Falcon fighter aircraft, and whose battles include the 1986 United States bombing of Libya.
````

### Baseline output

````markdown
Al Asad Airbase is operated by the United States Air Force (USAF). The USAF is associated with specific aircraft types: the Lockheed AC-130 as its attack aircraft, the Boeing C-17 Globemaster III as its transport aircraft, and the General Dynamics F-16 Fighting Falcon as its fighter aircraft. The data also links the USAF to the 1986 United States bombing of Libya.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.8336 | 0.8772 | 0.0436 | Full System |
| BERTScore F1 | Higher | 0.9432 | 0.9548 | 0.0116 | Full System |
| BLEU | Higher | 0.4506 | 0.5966 | 0.1460 | Full System |
| chrF | Higher | 0.6991 | 0.7059 | 0.0068 | Full System |
| HHEM mean support | Higher | 0.7140 | 0.8274 | 0.1134 | Full System |
| HHEM minimum sentence support | Higher | 0.5069 | 0.8274 | 0.3205 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.6412 | 0.6207 | -0.0205 | Baseline |
| ROUGE-1 | Higher | 0.7288 | 0.8119 | 0.0831 | Full System |
| ROUGE-2 | Higher | 0.5690 | 0.6667 | 0.0977 | Full System |
| ROUGE-L | Higher | 0.5965 | 0.6535 | 0.0570 | Full System |
| ROUGE-Lsum | Higher | 0.5965 | 0.6535 | 0.0570 | Full System |
| TER | Lower | 0.5696 | 0.4367 | 0.1329 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T012116Z_5b71a80fdb |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 44 |
| Baseline words | 61 |
| Full System elapsed seconds | 14.0320 |
| Baseline elapsed seconds | 2.8258 |
| Full System provider-reported tokens | 7197 |
| Baseline provider-reported tokens | 558 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/dart__dart-test-2278/full_system/dart/20260821T012116Z_5b71a80fdb/pipeline_result.json |

## A19. totto / totto-validation-839

| Field | Value |
| --- | --- |
| Dataset | totto |
| Example ID | totto-validation-839 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source SHA-256 | 09a9a840e0ecbe6e8cc23300cef1fc925e8577e9d8c77bced996240dff713676 |
| Reference SHA-256 | 4bc3fecf5a648f242388bf1ed91ce31c75f2b90e15263b2e563f0f18efb5cbf1 |
| Full System request | Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Page: Ernest Burton (American football)
Section: Head coaching record
Table:
Year | Team | Overall | Conference | Standing | Bowl/playoffs
*Maine Black Bears (Maine Intercollegiate Athletic Association) (1900)*
1900 | Maine | 4–4 |  |  | 
Maine: | 4–4 |  | 
Total: | *4–4* | 
Cells surrounded by * are highlighted.
````

### Human reference outputs

**Reference 1**

````text
C. Ernest Burton was the head coach of the Maine's football team in 1900 and compiled a 4–4 record.
````

**Reference 2**

````text
C. Ernest Burton was the head coach of Maine's football team in 1900 and compiled a 4–4 record.
````

### Full System output

````markdown
Ernest Burton's head coaching record shows Maine Black Bears in 1900 with an overall record of 4–4.
````

### Baseline output

````markdown
Ernest Burton coached the Maine Black Bears football team in 1900, and the team finished with an overall record of 4–4. No conference record, standing, or bowl/playoff information is provided.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.4556 | 0.9120 | 0.4564 | Full System |
| BERTScore F1 | Higher | 0.9156 | 0.9183 | 0.0027 | Full System |
| BLEU | Higher | 0.0917 | 0.0544 | -0.0373 | Baseline |
| chrF | Higher | 0.4494 | 0.3730 | -0.0764 | Baseline |
| HHEM mean support | Higher | 0.5710 | 0.9084 | 0.3374 | Full System |
| HHEM minimum sentence support | Higher | 0.2765 | 0.9084 | 0.6319 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.5000 | 0.0000 | 0.5000 | Full System |
| METEOR | Higher | 0.3162 | 0.2855 | -0.0306 | Baseline |
| ROUGE-1 | Higher | 0.5660 | 0.6154 | 0.0493 | Full System |
| ROUGE-2 | Higher | 0.2745 | 0.2162 | -0.0583 | Baseline |
| ROUGE-L | Higher | 0.4906 | 0.4615 | -0.0290 | Baseline |
| ROUGE-Lsum | Higher | 0.4906 | 0.4615 | -0.0290 | Baseline |
| TER | Lower | 1.2973 | 0.8108 | 0.4865 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

1. **OMISSION**
   - Error span: Maine Black Bears in 1900
   - Correction or explanation: The highlighted team heading also identifies the Maine Black Bears as members of the Maine Intercollegiate Athletic Association, which the output omits.

**Baseline**

1. **TASK/FORMAT**
   - Error span: No conference record, standing, or bowl/playoff information is provided.
   - Correction or explanation: This second sentence violates the requirement to write exactly one sentence and discusses unhighlighted table cells unrelated to the highlighted content.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T012130Z_163d7186d4 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 17 |
| Baseline words | 30 |
| Full System elapsed seconds | 15.4413 |
| Baseline elapsed seconds | 2.6153 |
| Full System provider-reported tokens | 8013 |
| Baseline provider-reported tokens | 475 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/totto__totto-validation-839/full_system/totto/20260821T012130Z_163d7186d4/pipeline_result.json |

## A20. sportsett_basketball / 5955

| Field | Value |
| --- | --- |
| Dataset | sportsett_basketball |
| Example ID | 5955 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source SHA-256 | 86491264c5dd17cd78b7120bb3f179565618a1c2778e388ea25b41e288ef6199 |
| Reference SHA-256 | 833109f0de34b3c6c88341b8443b6db76e62efa6cd0eacea3e3a9b99a3995d5f |
| Full System request | Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````json
{
  "game": {
    "attendance": "18200",
    "capacity": "18200",
    "city": "Oklahoma City",
    "day": "24",
    "dayname": "Saturday",
    "game_id": "5955",
    "month": "November",
    "season": "2018",
    "stadium": "Chesapeake Energy Arena",
    "state": "Oklahoma",
    "year": "2018"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "-1",
          "AST": "3",
          "BLK": "3",
          "DOUBLE": "double",
          "DREB": "7",
          "FG3A": "6",
          "FG3M": "3",
          "FG3_PCT": "50",
          "FGA": "21",
          "FGM": "8",
          "FG_PCT": "38",
          "FTA": "7",
          "FTM": "5",
          "FT_PCT": "71",
          "MIN": "39",
          "OREB": "4",
          "PF": "5",
          "PTS": "24",
          "STL": "2",
          "TOV": "1",
          "TREB": "11",
          "first_name": "Paul",
          "last_name": "George",
          "name": "Paul George",
          "starter": "True"
        },
        {
          "+/-": "-3",
          "AST": "12",
          "BLK": "0",
          "DOUBLE": "triple",
          "DREB": "7",
          "FG3A": "12",
          "FG3M": "1",
          "FG3_PCT": "8",
          "FGA": "23",
          "FGM": "6",
          "FG_PCT": "26",
          "FTA": "7",
          "FTM": "3",
          "FT_PCT": "43",
          "MIN": "39",
          "OREB": "3",
          "PF": "5",
          "PTS": "16",
          "STL": "1",
          "TOV": "4",
          "TREB": "10",
          "first_name": "Russell",
          "last_name": "Westbrook",
          "name": "Russell Westbrook",
          "starter": "True"
        },
        {
          "+/-": "-5",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "7",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "15",
          "FGM": "6",
          "FG_PCT": "40",
          "FTA": "1",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "37",
          "OREB": "7",
          "PF": "3",
          "PTS": "12",
          "STL": "1",
          "TOV": "2",
          "TREB": "14",
          "first_name": "Steven",
          "last_name": "Adams",
          "name": "Steven Adams",
          "starter": "True"
        },
        {
          "+/-": "2",
          "AST": "2",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "5",
          "FG3M": "2",
          "FG3_PCT": "40",
          "FGA": "11",
          "FGM": "5",
          "FG_PCT": "45",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "31",
          "OREB": "0",
          "PF": "5",
          "PTS": "13",
          "STL": "0",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Jerami",
          "last_name": "Grant",
          "name": "Jerami Grant",
          "starter": "True"
        },
        {
          "+/-": "-10",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "6",
          "FGM": "1",
          "FG_PCT": "17",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "20",
          "OREB": "1",
          "PF": "1",
          "PTS": "3",
          "STL": "1",
          "TOV": "1",
          "TREB": "5",
          "first_name": "Timothé",
          "last_name": "Luwawu-Cabarrot",
          "name": "Timothé Luwawu-Cabarrot",
          "starter": "True"
        },
        {
          "+/-": "4",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "7",
          "FG3M": "2",
          "FG3_PCT": "29",
          "FGA": "14",
          "FGM": "5",
          "FG_PCT": "36",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "29",
          "OREB": "0",
          "PF": "0",
          "PTS": "18",
          "STL": "1",
          "TOV": "2",
          "TREB": "2",
          "first_name": "Dennis",
          "last_name": "Schröder",
          "name": "Dennis Schröder",
          "starter": "False"
        },
        {
          "+/-": "-1",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "6",
          "FGM": "4",
          "FG_PCT": "67",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "13",
          "OREB": "0",
          "PF": "2",
          "PTS": "8",
          "STL": "1",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Deonte",
          "last_name": "Burton",
          "name": "Deonte Burton",
          "starter": "False"
        },
        {
          "+/-": "-2",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "2",
          "FG_PCT": "100",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "10",
          "OREB": "3",
          "PF": "2",
          "PTS": "4",
          "STL": "1",
          "TOV": "0",
          "TREB": "5",
          "first_name": "Nerlens",
          "last_name": "Noel",
          "name": "Nerlens Noel",
          "starter": "False"
        },
        {
          "+/-": "-10",
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
          "MIN": "9",
          "OREB": "1",
          "PF": "0",
          "PTS": "0",
          "STL": "1",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Patrick",
          "last_name": "Patterson",
          "name": "Patrick Patterson",
          "starter": "False"
        },
        {
          "+/-": "-9",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "2",
          "FGM": "0",
          "FG_PCT": "0",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "7",
          "OREB": "0",
          "PF": "1",
          "PTS": "0",
          "STL": "0",
          "TOV": "0",
          "TREB": "1",
          "first_name": "Álex",
          "last_name": "Abrines",
          "name": "Álex Abrines",
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
          "first_name": "Raymond",
          "last_name": "Felton",
          "name": "Raymond Felton",
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
          "first_name": "Abdel",
          "last_name": "Nader",
          "name": "Abdel Nader",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 5,
      "division": "Northwest",
      "game_number": "19",
      "line_score": {
        "H1": {
          "AST": "43",
          "BLK": "02",
          "DREB": "78",
          "FG3A": "136",
          "FG3M": "20",
          "FG3_PCT": "15",
          "FGA": "2523",
          "FGM": "86",
          "FG_PCT": "3",
          "FTA": "79",
          "FTM": "57",
          "FT_PCT": "72",
          "MIN": "6060",
          "OREB": "63",
          "PTS": "2319",
          "STL": "32",
          "TOV": "36",
          "TREB": "141"
        },
        "H2": {
          "AST": "411",
          "BLK": "21",
          "DREB": "1010",
          "FG3A": "812",
          "FG3M": "34",
          "FG3_PCT": "4",
          "FGA": "2827",
          "FGM": "1013",
          "FG_PCT": "36",
          "FTA": "52",
          "FTM": "12",
          "FT_PCT": "23",
          "MIN": "6060",
          "OREB": "73",
          "PTS": "2432",
          "STL": "22",
          "TOV": "10",
          "TREB": "1083"
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
          "BLK": "0",
          "DREB": "7",
          "FG3A": "13",
          "FG3M": "2",
          "FG3_PCT": "15",
          "FGA": "25",
          "FGM": "8",
          "FG_PCT": "32",
          "FTA": "7",
          "FTM": "5",
          "FT_PCT": "71",
          "MIN": "60",
          "OREB": "6",
          "PTS": "23",
          "STL": "3",
          "TOV": "3",
          "TREB": "13"
        },
        "Q2": {
          "AST": "3",
          "BLK": "2",
          "DREB": "8",
          "FG3A": "6",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "23",
          "FGM": "6",
          "FG_PCT": "26",
          "FTA": "9",
          "FTM": "7",
          "FT_PCT": "78",
          "MIN": "60",
          "OREB": "3",
          "PTS": "19",
          "STL": "2",
          "TOV": "6",
          "TREB": "11"
        },
        "Q3": {
          "AST": "4",
          "BLK": "2",
          "DREB": "10",
          "FG3A": "8",
          "FG3M": "3",
          "FG3_PCT": "38",
          "FGA": "28",
          "FGM": "10",
          "FG_PCT": "36",
          "FTA": "5",
          "FTM": "1",
          "FT_PCT": "20",
          "MIN": "60",
          "OREB": "7",
          "PTS": "24",
          "STL": "2",
          "TOV": "1",
          "TREB": "17"
        },
        "Q4": {
          "AST": "11",
          "BLK": "1",
          "DREB": "10",
          "FG3A": "12",
          "FG3M": "4",
          "FG3_PCT": "33",
          "FGA": "27",
          "FGM": "13",
          "FG_PCT": "48",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "3",
          "PTS": "32",
          "STL": "2",
          "TOV": "0",
          "TREB": "13"
        },
        "game": {
          "AST": "22",
          "BLK": "5",
          "DREB": "35",
          "FG3A": "39",
          "FG3M": "9",
          "FG3_PCT": "23",
          "FGA": "103",
          "FGM": "37",
          "FG_PCT": "36",
          "FTA": "23",
          "FTM": "15",
          "FT_PCT": "65",
          "MIN": "4",
          "OREB": "19",
          "PF": "24",
          "PTS": "98",
          "STL": "9",
          "TOV": "10",
          "TREB": "54"
        }
      },
      "losses": "7",
      "name": "Thunder",
      "next_game": {
        "city": "Oklahoma City",
        "day": "28",
        "dayname": "Wednesday",
        "is_home": "True",
        "month": "November",
        "opponent_name": "Cavaliers",
        "opponent_place": "Cleveland",
        "stadium": "Chesapeake Energy Arena",
        "year": "2018"
      },
      "next_game_id": "5956",
      "place": "Oklahoma City",
      "previous_game_id": "5954",
      "wins": "12"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "4",
          "AST": "8",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "23",
          "FGM": "9",
          "FG_PCT": "39",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "39",
          "OREB": "2",
          "PF": "1",
          "PTS": "22",
          "STL": "0",
          "TOV": "3",
          "TREB": "8",
          "first_name": "Jamal",
          "last_name": "Murray",
          "name": "Jamal Murray",
          "starter": "True"
        },
        {
          "+/-": "-2",
          "AST": "1",
          "BLK": "2",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "2",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "4",
          "FG_PCT": "50",
          "FTA": "1",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "36",
          "OREB": "6",
          "PF": "2",
          "PTS": "8",
          "STL": "1",
          "TOV": "2",
          "TREB": "10",
          "first_name": "Torrey",
          "last_name": "Craig",
          "name": "Torrey Craig",
          "starter": "True"
        },
        {
          "+/-": "4",
          "AST": "0",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "7",
          "FG3A": "7",
          "FG3M": "3",
          "FG3_PCT": "43",
          "FGA": "12",
          "FGM": "4",
          "FG_PCT": "33",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "35",
          "OREB": "1",
          "PF": "2",
          "PTS": "15",
          "STL": "2",
          "TOV": "1",
          "TREB": "8",
          "first_name": "Juan",
          "last_name": "Hernangómez",
          "name": "Juan Hernangómez",
          "starter": "True"
        },
        {
          "+/-": "2",
          "AST": "3",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "3",
          "FG3M": "2",
          "FG3_PCT": "67",
          "FGA": "7",
          "FGM": "3",
          "FG_PCT": "43",
          "FTA": "2",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "28",
          "OREB": "0",
          "PF": "3",
          "PTS": "8",
          "STL": "1",
          "TOV": "1",
          "TREB": "6",
          "first_name": "Paul",
          "last_name": "Millsap",
          "name": "Paul Millsap",
          "starter": "True"
        },
        {
          "+/-": "15",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "7",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "20",
          "FGM": "6",
          "FG_PCT": "30",
          "FTA": "5",
          "FTM": "4",
          "FT_PCT": "80",
          "MIN": "27",
          "OREB": "2",
          "PF": "4",
          "PTS": "16",
          "STL": "0",
          "TOV": "4",
          "TREB": "6",
          "first_name": "Nikola",
          "last_name": "Jokić",
          "name": "Nikola Jokić",
          "starter": "True"
        },
        {
          "+/-": "-8",
          "AST": "2",
          "BLK": "4",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "4",
          "FG_PCT": "50",
          "FTA": "6",
          "FTM": "3",
          "FT_PCT": "50",
          "MIN": "20",
          "OREB": "3",
          "PF": "4",
          "PTS": "11",
          "STL": "0",
          "TOV": "2",
          "TREB": "7",
          "first_name": "Mason",
          "last_name": "Plumlee",
          "name": "Mason Plumlee",
          "starter": "False"
        },
        {
          "+/-": "7",
          "AST": "6",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "5",
          "FGM": "1",
          "FG_PCT": "20",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "20",
          "OREB": "0",
          "PF": "1",
          "PTS": "4",
          "STL": "2",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Monte",
          "last_name": "Morris",
          "name": "Monte Morris",
          "starter": "False"
        },
        {
          "+/-": "5",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "2",
          "FG3M": "2",
          "FG3_PCT": "100",
          "FGA": "6",
          "FGM": "6",
          "FG_PCT": "100",
          "FTA": "2",
          "FTM": "2",
          "FT_PCT": "100",
          "MIN": "19",
          "OREB": "1",
          "PF": "1",
          "PTS": "16",
          "STL": "0",
          "TOV": "1",
          "TREB": "4",
          "first_name": "Trey",
          "last_name": "Lyles",
          "name": "Trey Lyles",
          "starter": "False"
        },
        {
          "+/-": "8",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "6",
          "FGM": "2",
          "FG_PCT": "33",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "12",
          "OREB": "0",
          "PF": "2",
          "PTS": "5",
          "STL": "0",
          "TOV": "0",
          "TREB": "3",
          "first_name": "Malik",
          "last_name": "Beasley",
          "name": "Malik Beasley",
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
          "first_name": "DeVaughn",
          "last_name": "Akoon-Purcell",
          "name": "DeVaughn Akoon-Purcell",
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
          "first_name": "Gary",
          "last_name": "Harris",
          "name": "Gary Harris",
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
          "first_name": "Tyler",
          "last_name": "Lydon",
          "name": "Tyler Lydon",
          "starter": "False"
        }
      ],
      "conference": "Western Conference",
      "conference_standing": 4,
      "division": "Northwest",
      "game_number": "20",
      "line_score": {
        "H1": {
          "AST": "97",
          "BLK": "02",
          "DREB": "912",
          "FG3A": "98",
          "FG3M": "52",
          "FG3_PCT": "53",
          "FGA": "2327",
          "FGM": "1312",
          "FG_PCT": "56",
          "FTA": "46",
          "FTM": "24",
          "FT_PCT": "52",
          "MIN": "6060",
          "OREB": "25",
          "PTS": "3330",
          "STL": "24",
          "TOV": "36",
          "TREB": "937"
        },
        "H2": {
          "AST": "55",
          "BLK": "52",
          "DREB": "99",
          "FG3A": "94",
          "FG3M": "21",
          "FG3_PCT": "22",
          "FGA": "2223",
          "FGM": "59",
          "FG_PCT": "3",
          "FTA": "410",
          "FTM": "47",
          "FT_PCT": "11",
          "MIN": "6060",
          "OREB": "44",
          "PTS": "1626",
          "STL": "00",
          "TOV": "32",
          "TREB": "143"
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
          "AST": "9",
          "BLK": "0",
          "DREB": "9",
          "FG3A": "9",
          "FG3M": "5",
          "FG3_PCT": "56",
          "FGA": "23",
          "FGM": "13",
          "FG_PCT": "57",
          "FTA": "4",
          "FTM": "2",
          "FT_PCT": "50",
          "MIN": "60",
          "OREB": "2",
          "PTS": "33",
          "STL": "2",
          "TOV": "3",
          "TREB": "11"
        },
        "Q2": {
          "AST": "7",
          "BLK": "2",
          "DREB": "12",
          "FG3A": "8",
          "FG3M": "2",
          "FG3_PCT": "25",
          "FGA": "27",
          "FGM": "12",
          "FG_PCT": "44",
          "FTA": "6",
          "FTM": "4",
          "FT_PCT": "67",
          "MIN": "60",
          "OREB": "5",
          "PTS": "30",
          "STL": "4",
          "TOV": "6",
          "TREB": "17"
        },
        "Q3": {
          "AST": "5",
          "BLK": "5",
          "DREB": "9",
          "FG3A": "9",
          "FG3M": "2",
          "FG3_PCT": "22",
          "FGA": "22",
          "FGM": "5",
          "FG_PCT": "23",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "4",
          "PTS": "16",
          "STL": "0",
          "TOV": "3",
          "TREB": "13"
        },
        "Q4": {
          "AST": "5",
          "BLK": "2",
          "DREB": "9",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "23",
          "FGM": "9",
          "FG_PCT": "39",
          "FTA": "10",
          "FTM": "7",
          "FT_PCT": "70",
          "MIN": "60",
          "OREB": "4",
          "PTS": "26",
          "STL": "0",
          "TOV": "2",
          "TREB": "13"
        },
        "game": {
          "AST": "26",
          "BLK": "9",
          "DREB": "39",
          "FG3A": "30",
          "FG3M": "10",
          "FG3_PCT": "33",
          "FGA": "95",
          "FGM": "39",
          "FG_PCT": "41",
          "FTA": "24",
          "FTM": "17",
          "FT_PCT": "71",
          "MIN": "4",
          "OREB": "15",
          "PF": "20",
          "PTS": "105",
          "STL": "6",
          "TOV": "14",
          "TREB": "54"
        }
      },
      "losses": "7",
      "name": "Nuggets",
      "next_game": {
        "city": "Denver",
        "day": "27",
        "dayname": "Tuesday",
        "is_home": "True",
        "month": "November",
        "opponent_name": "Lakers",
        "opponent_place": "Los Angeles",
        "stadium": "Pepsi Center",
        "year": "2018"
      },
      "next_game_id": "5629",
      "place": "Denver",
      "previous_game_id": "5628",
      "wins": "13"
    }
  }
}
````

### Human reference outputs

**Reference 1**

````text
The Denver Nuggets defeated the host Oklahoma City Thunder, 105 - 98, at Chesapeake Energy Arena on Saturday evening. The Nuggets got out to a great start on the road, as they outscored the Thunder, 33 - 23, in the first quarter. The Nuggets kept up the intensity in the second and outscored the Thunder 30 - 19 in the quarter, to take a convincing, 63 - 42, lead by halftime. The Thunder picked it up in the third, but could not make a significant dent in the deficit, as they trailed, 79 - 66, entering the fourth. The Thunder continued their push in the fourth, as they cut the deficit to just seven points early in the quarter. The Nuggets did not slip up and maintained their edge. Despite a continued effort from the home team, the Nuggets hung on for their third straight win. Jamal Murray led Denver with 22 points, eight rebounds and eight assists, in 39 minutes. Nikola Jokic followed up with 16 points, five rebounds, five assists and one block, while Juancho Hernangomez tallied 15 points, eight rebounds, two steals and one block. The Nuggets shot 41 percent from the field, including 10 - of - 30 from long range. Meanwhile, Paul George led the Thunder with 24 points, 11 rebounds, three assists, three blocks and two steals, in 39 minutes. Russell Westbrook followed up with 16 points, 12 assists, 10 rebounds and one steal, while Steven Adams tallied 12 points, 14 rebounds and one steal, in 37 minutes. The Thunder shot 36 percent from the field. The Thunder (12 - 7) will look to bounce back as they play host to the Cavs on Wednesday. The Nuggets (13 - 7) play host to the Lakers on Tuesday.
````

**Reference 2**

````text
The Denver Nuggets defeated the host Oklahoma City Thunder , 105 - 98 , at Chesapeake Energy Arena on Saturday evening . The Nuggets got out to a great start on the road , as they outscored the Thunder , 33 - 23 , in the first quarter . The Nuggets kept up the intensity in the second and outscored the Thunder 30 - 19 in the quarter , to take a convincing , 63 - 42 , lead by halftime . The Thunder picked it up in the third , but could not make a significant dent in the deficit , as they trailed , 79 - 66 , entering the fourth . The Thunder continued their push in the fourth , as they cut the deficit to just seven points early in the quarter . The Nuggets did not slip up and maintained their edge . Despite a continued effort from the home team , the Nuggets hung on for their third straight win . Jamal Murray led Denver with 22 points , eight rebounds and eight assists , in 39 minutes . Nikola Jokic followed up with 16 points , five rebounds , five assists and one block , while Juancho Hernangomez tallied 15 points , eight rebounds , two steals and one block . The Nuggets shot 41 percent from the field , including 10 - of - 30 from long range . Meanwhile , Paul George led the Thunder with 24 points , 11 rebounds , three assists , three blocks and two steals , in 39 minutes . Russell Westbrook followed up with 16 points , 12 assists , 10 rebounds and one steal , while Steven Adams tallied 12 points , 14 rebounds and one steal , in 37 minutes . The Thunder shot 36 percent from the field . The Thunder ( 12 - 7 ) will look to bounce back as they play host to the Cavs on Wednesday . The Nuggets ( 13 - 7 ) play host to the Lakers on Tuesday .
````

### Full System output

````markdown
Denver Nuggets defeated Oklahoma City Thunder 105-98 at Chesapeake Energy Arena on Saturday, November 24, 2018.
Denver (13-7) and Oklahoma City (12-7) each entered the game with seven losses, with the Thunder playing at home in their own arena.
Denver led at the end of every quarter (33-23 after the first, 63-42 at halftime, 79-66 after the third) before closing out a 105-98 win.
Oklahoma City outscored Denver 24-16 in the third quarter and 32-26 in the fourth, narrowing the margin without taking the lead at a recorded checkpoint.
Paul George led all scorers with 24 points and added 11 rebounds, two steals and three blocks, while Jamal Murray topped Denver with 22 points and nine made field goals.
Russell Westbrook finished with 16 points and a game-high 12 assists, and Steven Adams grabbed a game-high 14 rebounds with seven offensive boards.
Oklahoma City attempted more field goals and three-pointers than Denver (103 vs 95 field goals; 39 vs 30 three-pointers), yet Denver made more of both (39 vs 37 field goals; 10 vs 9 three-pointers).
Denver also held a 26-22 edge in team assists and a 9-5 advantage in blocks, while Oklahoma City led 19-15 in offensive rebounds and 9-6 in steals.
The result covers only the supplied game record and does not establish why either team won.
````

### Baseline output

````markdown
The Denver Nuggets defeated the Oklahoma City Thunder 105–98 on Saturday, November 24, 2018, at Chesapeake Energy Arena in Oklahoma City. The game was a sellout (18,200 attendance).

Strongest supported findings:
- Denver won despite Oklahoma City outscoring them 32–26 in the fourth quarter; the Nuggets led after Q1 (33–23), Q2 (63–42), and Q3 (79–66).
- The Nuggets shot better overall: 41% FG, 33% 3PT, and 71% FT compared to the Thunder’s 36% FG, 23% 3PT, and 65% FT.
- Denver had 9 blocks to Oklahoma City’s 5, and 26 assists to the Thunder’s 22, while both teams totaled 54 rebounds.
- For the Thunder, Paul George scored 24 points, Russell Westbrook recorded a triple-double (16 points, 10 rebounds, 12 assists), and Steven Adams had a double-double (12 points, 14 rebounds).
- For the Nuggets, Jamal Murray scored 22 points, Trey Lyles scored 16 points on 6-of-6 shooting, Nikola Jokić had 16 points and 5 assists, and Juan Hernangómez added 15 points.
- At the time, the Nuggets were 13–7 and the Thunder 12–7, with Denver holding the higher Western Conference standing (4th vs. 5th).
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.1699 | 0.1783 | 0.0085 | Full System |
| BERTScore F1 | Higher | 0.8534 | 0.8572 | 0.0038 | Full System |
| BLEU | Higher | 0.0814 | 0.1268 | 0.0454 | Full System |
| chrF | Higher | 0.3441 | 0.3632 | 0.0191 | Full System |
| HHEM mean support | Higher | 0.0880 | 0.0528 | -0.0352 | Baseline |
| HHEM minimum sentence support | Higher | 0.0082 | 0.0087 | 0.0005 | Full System |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.2110 | 0.2102 | -0.0007 | Baseline |
| ROUGE-1 | Higher | 0.4551 | 0.4760 | 0.0209 | Full System |
| ROUGE-2 | Higher | 0.1971 | 0.1773 | -0.0198 | Baseline |
| ROUGE-L | Higher | 0.2547 | 0.2457 | -0.0090 | Baseline |
| ROUGE-Lsum | Higher | 0.2547 | 0.2457 | -0.0090 | Baseline |
| TER | Lower | 0.8006 | 0.7975 | 0.0031 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

1. **CONTEXT**
   - Error span: Denver (13-7) and Oklahoma City (12-7) each entered the game with seven losses
   - Correction or explanation: Those are the teams' postgame records: Denver's 13 wins include this victory, and Oklahoma City's seventh loss is this defeat. Their entering records were therefore 12-7 and 12-6, respectively.
2. **OMISSION**
   - Error span: Russell Westbrook finished with 16 points and a game-high 12 assists
   - Correction or explanation: The report omits Westbrook's 10 rebounds, which completed a notable 16-point, 10-rebound, 12-assist triple-double.
3. **TASK/FORMAT**
   - Error span: Entire generated output
   - Correction or explanation: The requested output mode was a multi-paragraph report, but the report is presented as a single paragraph.

**Baseline**

1. **TASK/FORMAT**
   - Error span: Strongest supported findings: - Denver won ... - At the time, the Nuggets were 13–7 ...
   - Correction or explanation: The request specifies a coherent multi-paragraph game report, but the output presents nearly all details as a single inline bullet list rather than multi-paragraph report prose.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T012146Z_70aaa903bc |
| Execution outcome | success |
| Final generation path | auditor_repaired |
| Final Writer mode | auditor_repaired |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 1 |
| Native support rate | 1.0000 |
| Factual sentences | 9 |
| Supported sentences | 9 |
| Evidence items | 42 |
| Verified facts | 42 |
| Rejected facts | 0 |
| Verified insights | 3 |
| Rejected insights | 5 |
| Full System words | 219 |
| Baseline words | 185 |
| Full System elapsed seconds | 952.5461 |
| Baseline elapsed seconds | 9.0855 |
| Full System provider-reported tokens | 684034 |
| Baseline provider-reported tokens | 9216 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/sportsett_basketball__5955/full_system/sportsett_basketball/20260821T012146Z_70aaa903bc/pipeline_result.json |

## A21. e2e_nlg / e2e_nlg-test-864

| Field | Value |
| --- | --- |
| Dataset | e2e_nlg |
| Example ID | e2e_nlg-test-864 |
| Task family | attribute_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 772650e2992ed07ecfb68cae7171298479d3d2d9bd6216b563c4fdc4e4f5c712 |
| Reference SHA-256 | 5ef157458d3427cf0014a21463a855d8194f2045332afb43eded6fd3cb096645 |
| Full System request | Express all and only the supplied attributes in one or two fluent sentences. Do not add headings or unsupported details. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
name[The Phoenix], eatType[pub], near[Crowne Plaza Hotel]
````

### Human reference outputs

**Reference 1**

````text
Found near Crowne Plaza Hotel, The Phoenix pub provides mid-priced wine and cheese dining for the whole family.
````

### Full System output

````markdown
The Phoenix is a pub near Crowne Plaza Hotel.
````

### Baseline output

````markdown
The Phoenix is a pub located near the Crowne Plaza Hotel.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9820 | 0.9785 | -0.0035 | Baseline |
| BERTScore F1 | Higher | 0.9213 | 0.9245 | 0.0032 | Full System |
| BLEU | Higher | 0.0943 | 0.1235 | 0.0292 | Full System |
| chrF | Higher | 0.3339 | 0.3341 | 0.0001 | Full System |
| HHEM mean support | Higher | 0.7599 | 0.8229 | 0.0630 | Full System |
| HHEM minimum sentence support | Higher | 0.7599 | 0.8229 | 0.0630 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.3309 | 0.2989 | -0.0320 | Baseline |
| ROUGE-1 | Higher | 0.5333 | 0.5000 | -0.0333 | Baseline |
| ROUGE-2 | Higher | 0.2143 | 0.3077 | 0.0934 | Full System |
| ROUGE-L | Higher | 0.2667 | 0.2857 | 0.0190 | Full System |
| ROUGE-Lsum | Higher | 0.2667 | 0.2857 | 0.0190 | Full System |
| TER | Lower | 0.7778 | 0.7778 | 0.0000 | Tie |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T013739Z_5acf94b523 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 0 |
| Supported sentences | 0 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 9 |
| Baseline words | 11 |
| Full System elapsed seconds | 28.0319 |
| Baseline elapsed seconds | 2.0391 |
| Full System provider-reported tokens | 13469 |
| Baseline provider-reported tokens | 292 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/e2e_nlg__e2e_nlg-test-864/full_system/e2e_nlg/20260821T013739Z_5acf94b523/pipeline_result.json |

## A22. web_nlg / web_nlg_en-test-864

| Field | Value |
| --- | --- |
| Dataset | web_nlg |
| Example ID | web_nlg_en-test-864 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 3d589eb09ad48805c2de71a9c53f355e9c0dd090d7ad7330a531db2dd1163f66 |
| Reference SHA-256 | 94f9b0173d9ce29a5afa00e4d7523b95eb7a3b8e9981398b9cd1b2f0c2a36b74 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Akeem_Ayers | debutTeam | Tennessee_Titans
Akeem_Ayers | activeYearsStartYear | 2011
````

### Human reference outputs

**Reference 1**

````text
Akeem Ayers, who started his career in 2011, debuted for the Tennessee Titans.
````

**Reference 2**

````text
Hakeem Ayers started his career in 2011 when he debuted for the Tennessee Titans.
````

**Reference 3**

````text
Akeem Ayers, part of the Tennessee Titans has been active since 2011.
````

### Full System output

````markdown
Akeem Ayers debuted for the Tennessee Titans, and his active years started in 2011.
````

### Baseline output

````markdown
Akeem Ayers debuted with the Tennessee Titans, and his active years began in 2011.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9948 | 0.9945 | -0.0004 | Baseline |
| BERTScore F1 | Higher | 0.9517 | 0.9557 | 0.0040 | Full System |
| BLEU | Higher | 0.1619 | 0.3406 | 0.1787 | Full System |
| chrF | Higher | 0.5340 | 0.6621 | 0.1281 | Full System |
| HHEM mean support | Higher | 0.7519 | 0.7063 | -0.0456 | Baseline |
| HHEM minimum sentence support | Higher | 0.7519 | 0.7063 | -0.0456 | Baseline |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.3661 | 0.5361 | 0.1700 | Full System |
| ROUGE-1 | Higher | 0.6667 | 0.8148 | 0.1481 | Full System |
| ROUGE-2 | Higher | 0.3200 | 0.4800 | 0.1600 | Full System |
| ROUGE-L | Higher | 0.5385 | 0.5385 | 0.0000 | Tie |
| ROUGE-Lsum | Higher | 0.5385 | 0.5385 | 0.0000 | Tie |
| TER | Lower | 0.6923 | 0.6923 | 0.0000 | Tie |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T013807Z_bf2039a3c8 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 14 |
| Baseline words | 14 |
| Full System elapsed seconds | 9.6025 |
| Baseline elapsed seconds | 1.4120 |
| Full System provider-reported tokens | 6415 |
| Baseline provider-reported tokens | 265 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/web_nlg__web_nlg_en-test-864/full_system/web_nlg/20260821T013807Z_bf2039a3c8/pipeline_result.json |

## A23. dart / dart-test-4597

| Field | Value |
| --- | --- |
| Dataset | dart |
| Example ID | dart-test-4597 |
| Task family | triple_verbalisation |
| Output mode | short_text |
| Language | en |
| Source SHA-256 | 652f9936ba6424bb0f260c603db3501d3047181a928e2fdb4eec3ca81f2829e5 |
| Reference SHA-256 | 4bd00c10ae67936e233cbc1a60c47d4265f1871969876cbfb8a66c8fbcba1669 |
| Full System request | Express all and only the supplied triples as short, coherent natural language. Do not add unsupported facts. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
The Vaults | eatType | pub
The Vaults | food | Italian
The Vaults | priceRange | moderate
The Vaults | customer rating | average
The Vaults | area | riverside
The Vaults | familyFriendly | yes
The Vaults | near | Rainbow Vegetarian Café
````

### Human reference outputs

**Reference 1**

````text
The Vaults, an Italian pub in the riverside area near Rainbow Vegetarian Café is child-friendly with a high price range but an average rating.
````

### Full System output

````markdown
The Vaults is a pub serving Italian food at moderate prices with an average customer rating, is located in the riverside area, is family friendly, and is near Rainbow Vegetarian Café.
````

### Baseline output

````markdown
The Vaults is a family-friendly pub with moderate prices, serving Italian food in a riverside area. It has an average customer rating and is located near Rainbow Vegetarian Café.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.9608 | 0.9809 | 0.0201 | Full System |
| BERTScore F1 | Higher | 0.9443 | 0.9387 | -0.0056 | Baseline |
| BLEU | Higher | 0.1275 | 0.1786 | 0.0512 | Full System |
| chrF | Higher | 0.5551 | 0.5837 | 0.0286 | Full System |
| HHEM mean support | Higher | 0.7125 | 0.7357 | 0.0232 | Full System |
| HHEM minimum sentence support | Higher | 0.7050 | 0.7357 | 0.0307 | Full System |
| HHEM unsupported-sentence rate | Lower | 0.0000 | 0.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.4099 | 0.5173 | 0.1075 | Full System |
| ROUGE-1 | Higher | 0.6909 | 0.7143 | 0.0234 | Full System |
| ROUGE-2 | Higher | 0.2264 | 0.2963 | 0.0699 | Full System |
| ROUGE-L | Higher | 0.3636 | 0.3929 | 0.0292 | Full System |
| ROUGE-Lsum | Higher | 0.3636 | 0.3929 | 0.0292 | Full System |
| TER | Lower | 1.0000 | 0.9583 | 0.0417 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

GPT-5.6 Sol reported no errors.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T013817Z_645510c269 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 0 |
| Supported sentences | 0 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 31 |
| Baseline words | 29 |
| Full System elapsed seconds | 11.4253 |
| Baseline elapsed seconds | 2.1631 |
| Full System provider-reported tokens | 7155 |
| Baseline provider-reported tokens | 369 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/dart__dart-test-4597/full_system/dart/20260821T013817Z_645510c269/pipeline_result.json |

## A24. totto / totto-validation-912

| Field | Value |
| --- | --- |
| Dataset | totto |
| Example ID | totto-validation-912 |
| Task family | highlighted_table_description |
| Output mode | one_sentence |
| Language | en |
| Source SHA-256 | 02076943868e187e53172594cfe40e876163ca4a1385a814147a0a1655d4b5aa |
| Reference SHA-256 | 85e3d857aa14ca068b9257722fc7a85a211536410554c00103c0b93772d8aaae |
| Full System request | Write exactly one concise sentence describing the highlighted table cells. Do not discuss unrelated cells and do not add headings. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````text
Page: Tyrell Sutton
Section: CFL Statistics
Table:
Year | Team | GP | Carries | Yards | TDs | Avg | Long |  | Rec | Yards | TDs
2013 | MTL | 12 | 55 | 342 | 3 | 6.2 | 20 | 14 | 156 | 0
2014 | MTL | 12 | 96 | 500 | 1 | 5.2 | 24 | 15 | 190 | 0
2015 | MTL | 15 | 180 | 1,059 | 5 | 5.9 | 54 | 43 | 334 | 2
*2016* | MTL | *7* | *74* | *412* | 0 | *5.6* | 27 | 27 | 206 | 0
2017 | MTL | 14 | 152 | 843 | 5 | 5.5 | 43 | 44 | 312 | 1
2018 | MTL | 9 | 86 | 417 | 1 | 4.8 | 44 | 30 | 309 | 0
BC | 4 | 55 | 268 | 2 | 4.9 | 31 | 5 | 32 | 0
Total | 73 | 698 | 3,841 | 17 | 5.5 | 54 | 178 | 1,539 | 3
Cells surrounded by * are highlighted.
````

### Human reference outputs

**Reference 1**

````text
Tyrell Sutton played in seven games in 2016, rushing for 412 yards on 74 attempts (5.6 avg).
````

**Reference 2**

````text
In 2016, Tyrell Sutton played seven games and had 412 rushing yards on 74 attempts (5.6 avg).
````

### Full System output

````markdown
In 2016, Tyrell Sutton played 7 games, with 74 carries for 412 yards and an average of 5.6 yards per carry.
````

### Baseline output

````markdown
Tyrell Sutton’s strongest season was 2015: he set career highs in rushing yards (1,059), rushing touchdowns (5), carries (180), receptions (43), and receiving yards (334), while averaging 5.9 yards per carry with a long run of 54 yards. Across his CFL career, he totaled 3,841 rushing yards on 698 carries (5.5 average) with 17 rushing touchdowns, plus 178 receptions for 1,539 yards and 3 receiving touchdowns in 73 games. His 2016 season was highlighted but was shortened to 7 games, producing 412 rushing yards on 74 carries (5.6 average) with 0 touchdowns.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.2319 | 0.6047 | 0.3729 | Full System |
| BERTScore F1 | Higher | 0.8636 | 0.9378 | 0.0742 | Full System |
| BLEU | Higher | 0.0427 | 0.2755 | 0.2328 | Full System |
| chrF | Higher | 0.2672 | 0.4516 | 0.1844 | Full System |
| HHEM mean support | Higher | 0.1301 | 0.0654 | -0.0647 | Baseline |
| HHEM minimum sentence support | Higher | 0.0185 | 0.0654 | 0.0468 | Full System |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.3911 | 0.5388 | 0.1477 | Full System |
| ROUGE-1 | Higher | 0.2393 | 0.6000 | 0.3607 | Full System |
| ROUGE-2 | Higher | 0.1043 | 0.3158 | 0.2114 | Full System |
| ROUGE-L | Higher | 0.1880 | 0.5000 | 0.3120 | Full System |
| ROUGE-Lsum | Higher | 0.1880 | 0.5000 | 0.3120 | Full System |
| TER | Lower | 4.8824 | 0.8235 | 4.0588 | Full System |

### GPT-5.6 Sol structured annotations

**Full System**

GPT-5.6 Sol reported no errors.

**Baseline**

1. **TASK/FORMAT**
   - Error span: Tyrell Sutton’s strongest season was 2015: he set career highs in rushing yards (1,059), rushing touchdowns (5), carries (180), receptions (43), and receiving yards (334), while averaging 5.9 yards per carry with a long run of 54 yards. Across his CFL career, he totaled 3,841 rushing yards on 698 carries (5.5 average) with 17 rushing touchdowns, plus 178 receptions for 1,539 yards and 3 receiving touchdowns in 73 games. His 2016 season was highlighted but was shortened to 7 games, producing 412 rushing yards on 74 carries (5.6 average) with 0 touchdowns.
   - Correction or explanation: The request requires exactly one concise sentence about only the highlighted cells. The output uses three sentences and discusses unrelated 2015 statistics, career totals, and the unhighlighted 2016 touchdown value.
2. **CONTEXT**
   - Error span: was shortened to 7 games
   - Correction or explanation: The table shows that Sutton played 7 games in 2016, but it does not establish that the season was shortened.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T013829Z_1e2ad3ba70 |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved_with_warnings |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 1 |
| Supported sentences | 1 |
| Evidence items | 1 |
| Verified facts | 1 |
| Rejected facts | 0 |
| Verified insights | 0 |
| Rejected insights | 0 |
| Full System words | 21 |
| Baseline words | 92 |
| Full System elapsed seconds | 9.2777 |
| Baseline elapsed seconds | 4.4019 |
| Full System provider-reported tokens | 7703 |
| Baseline provider-reported tokens | 874 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/totto__totto-validation-912/full_system/totto/20260821T013829Z_1e2ad3ba70/pipeline_result.json |

## A25. sportsett_basketball / 6127

| Field | Value |
| --- | --- |
| Dataset | sportsett_basketball |
| Example ID | 6127 |
| Task family | event_report |
| Output mode | multi_paragraph_report |
| Language | en |
| Source SHA-256 | 532b36909f92f9f2d8e8c7faf6b1f5643fde5ecac64a97df32804fc816cd53df |
| Reference SHA-256 | b35653aa64d112e412a5fd2d9f6320a37fe2b9791b2854ce11248a82c31ef183 |
| Full System request | Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information. |
| Baseline request | Understand the supplied data and report its strongest supported findings. |

### Normalized source supplied during generation

````json
{
  "game": {
    "attendance": "15300",
    "capacity": "20400",
    "city": "Washington",
    "day": "2",
    "dayname": "Wednesday",
    "game_id": "6127",
    "month": "January",
    "season": "2018",
    "stadium": "Capital One Arena",
    "state": "Washington",
    "year": "2019"
  },
  "teams": {
    "home": {
      "box_score": [
        {
          "+/-": "20",
          "AST": "1",
          "BLK": "2",
          "DOUBLE": "double",
          "DREB": "14",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "7",
          "FGM": "5",
          "FG_PCT": "71",
          "FTA": "6",
          "FTM": "6",
          "FT_PCT": "100",
          "MIN": "39",
          "OREB": "1",
          "PF": "3",
          "PTS": "16",
          "STL": "2",
          "TOV": "1",
          "TREB": "15",
          "first_name": "Thomas",
          "last_name": "Bryant",
          "name": "Thomas Bryant",
          "starter": "True"
        },
        {
          "+/-": "11",
          "AST": "4",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "5",
          "FG3M": "1",
          "FG3_PCT": "20",
          "FGA": "15",
          "FGM": "5",
          "FG_PCT": "33",
          "FTA": "3",
          "FTM": "1",
          "FT_PCT": "33",
          "MIN": "39",
          "OREB": "1",
          "PF": "1",
          "PTS": "12",
          "STL": "1",
          "TOV": "1",
          "TREB": "5",
          "first_name": "Trevor",
          "last_name": "Ariza",
          "name": "Trevor Ariza",
          "starter": "True"
        },
        {
          "+/-": "13",
          "AST": "7",
          "BLK": "0",
          "DOUBLE": "double",
          "DREB": "7",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "10",
          "FGM": "5",
          "FG_PCT": "50",
          "FTA": "6",
          "FTM": "3",
          "FT_PCT": "50",
          "MIN": "36",
          "OREB": "4",
          "PF": "1",
          "PTS": "14",
          "STL": "2",
          "TOV": "1",
          "TREB": "11",
          "first_name": "Tomáš",
          "last_name": "Satoranský",
          "name": "Tomáš Satoranský",
          "starter": "True"
        },
        {
          "+/-": "15",
          "AST": "6",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "8",
          "FG3M": "4",
          "FG3_PCT": "50",
          "FGA": "13",
          "FGM": "7",
          "FG_PCT": "54",
          "FTA": "4",
          "FTM": "4",
          "FT_PCT": "100",
          "MIN": "36",
          "OREB": "0",
          "PF": "4",
          "PTS": "22",
          "STL": "0",
          "TOV": "1",
          "TREB": "6",
          "first_name": "Jeff",
          "last_name": "Green",
          "name": "Jeff Green",
          "starter": "True"
        },
        {
          "+/-": "22",
          "AST": "6",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "4",
          "FG3A": "7",
          "FG3M": "3",
          "FG3_PCT": "43",
          "FGA": "20",
          "FGM": "9",
          "FG_PCT": "45",
          "FTA": "3",
          "FTM": "3",
          "FT_PCT": "100",
          "MIN": "36",
          "OREB": "0",
          "PF": "5",
          "PTS": "24",
          "STL": "2",
          "TOV": "3",
          "TREB": "4",
          "first_name": "Bradley",
          "last_name": "Beal",
          "name": "Bradley Beal",
          "starter": "True"
        },
        {
          "+/-": "-3",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "6",
          "FGM": "3",
          "FG_PCT": "50",
          "FTA": "1",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "17",
          "OREB": "2",
          "PF": "3",
          "PTS": "7",
          "STL": "3",
          "TOV": "2",
          "TREB": "3",
          "first_name": "Chasson",
          "last_name": "Randle",
          "name": "Chasson Randle",
          "starter": "False"
        },
        {
          "+/-": "-1",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "0",
          "FG3A": "0",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "10",
          "FGM": "4",
          "FG_PCT": "40",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "15",
          "OREB": "2",
          "PF": "2",
          "PTS": "8",
          "STL": "0",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Sam",
          "last_name": "Dekker",
          "name": "Sam Dekker",
          "starter": "False"
        },
        {
          "+/-": "3",
          "AST": "2",
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
          "MIN": "13",
          "OREB": "0",
          "PF": "1",
          "PTS": "9",
          "STL": "0",
          "TOV": "1",
          "TREB": "1",
          "first_name": "Otto",
          "last_name": "Porter",
          "name": "Otto Porter",
          "starter": "False"
        },
        {
          "+/-": "0",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "1",
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
          "first_name": "Troy",
          "last_name": "Brown",
          "name": "Troy Brown",
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
          "first_name": "Ron",
          "last_name": "Baker",
          "name": "Ron Baker",
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
          "first_name": "Ian",
          "last_name": "Mahinmi",
          "name": "Ian Mahinmi",
          "starter": "False"
        }
      ],
      "conference": "Eastern Conference",
      "conference_standing": 11,
      "division": "Southeast",
      "game_number": "38",
      "line_score": {
        "H1": {
          "AST": "88",
          "BLK": "01",
          "DREB": "912",
          "FG3A": "86",
          "FG3M": "41",
          "FG3_PCT": "48",
          "FGA": "2126",
          "FGM": "1212",
          "FG_PCT": "57",
          "FTA": "106",
          "FTM": "74",
          "FT_PCT": "70",
          "MIN": "6060",
          "OREB": "32",
          "PTS": "3529",
          "STL": "23",
          "TOV": "12",
          "TREB": "944"
        },
        "H2": {
          "AST": "67",
          "BLK": "01",
          "DREB": "611",
          "FG3A": "87",
          "FG3M": "33",
          "FG3_PCT": "38",
          "FGA": "2025",
          "FGM": "811",
          "FG_PCT": "40",
          "FTA": "52",
          "FTM": "51",
          "FT_PCT": "98",
          "MIN": "6060",
          "OREB": "23",
          "PTS": "2426",
          "STL": "14",
          "TOV": "61",
          "TREB": "634"
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
          "BLK": "0",
          "DREB": "9",
          "FG3A": "8",
          "FG3M": "4",
          "FG3_PCT": "50",
          "FGA": "21",
          "FGM": "12",
          "FG_PCT": "57",
          "FTA": "10",
          "FTM": "7",
          "FT_PCT": "70",
          "MIN": "60",
          "OREB": "3",
          "PTS": "35",
          "STL": "2",
          "TOV": "1",
          "TREB": "12"
        },
        "Q2": {
          "AST": "8",
          "BLK": "1",
          "DREB": "12",
          "FG3A": "6",
          "FG3M": "1",
          "FG3_PCT": "17",
          "FGA": "26",
          "FGM": "12",
          "FG_PCT": "46",
          "FTA": "6",
          "FTM": "4",
          "FT_PCT": "67",
          "MIN": "60",
          "OREB": "2",
          "PTS": "29",
          "STL": "3",
          "TOV": "2",
          "TREB": "14"
        },
        "Q3": {
          "AST": "6",
          "BLK": "0",
          "DREB": "6",
          "FG3A": "8",
          "FG3M": "3",
          "FG3_PCT": "38",
          "FGA": "20",
          "FGM": "8",
          "FG_PCT": "40",
          "FTA": "5",
          "FTM": "5",
          "FT_PCT": "100",
          "MIN": "60",
          "OREB": "2",
          "PTS": "24",
          "STL": "1",
          "TOV": "6",
          "TREB": "8"
        },
        "Q4": {
          "AST": "7",
          "BLK": "1",
          "DREB": "11",
          "FG3A": "7",
          "FG3M": "3",
          "FG3_PCT": "43",
          "FGA": "25",
          "FGM": "11",
          "FG_PCT": "44",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "60",
          "OREB": "3",
          "PTS": "26",
          "STL": "4",
          "TOV": "1",
          "TREB": "14"
        },
        "game": {
          "AST": "29",
          "BLK": "2",
          "DREB": "38",
          "FG3A": "29",
          "FG3M": "11",
          "FG3_PCT": "38",
          "FGA": "92",
          "FGM": "43",
          "FG_PCT": "47",
          "FTA": "23",
          "FTM": "17",
          "FT_PCT": "74",
          "MIN": "4",
          "OREB": "10",
          "PF": "20",
          "PTS": "114",
          "STL": "10",
          "TOV": "10",
          "TREB": "48"
        }
      },
      "losses": "23",
      "name": "Wizards",
      "next_game": {
        "city": "Miami",
        "day": "4",
        "dayname": "Friday",
        "is_home": "False",
        "month": "January",
        "opponent_name": "Heat",
        "opponent_place": "Miami",
        "stadium": "American Airlines Arena",
        "year": "2019"
      },
      "next_game_id": "5268",
      "place": "Washington",
      "previous_game_id": "6126",
      "wins": "15"
    },
    "vis": {
      "box_score": [
        {
          "+/-": "-11",
          "AST": "5",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "1",
          "FG3A": "7",
          "FG3M": "1",
          "FG3_PCT": "14",
          "FGA": "14",
          "FGM": "5",
          "FG_PCT": "36",
          "FTA": "1",
          "FTM": "1",
          "FT_PCT": "100",
          "MIN": "44",
          "OREB": "0",
          "PF": "2",
          "PTS": "12",
          "STL": "0",
          "TOV": "2",
          "TREB": "1",
          "first_name": "Kevin",
          "last_name": "Huerter",
          "name": "Kevin Huerter",
          "starter": "True"
        },
        {
          "+/-": "-19",
          "AST": "9",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "3",
          "FG3A": "2",
          "FG3M": "1",
          "FG3_PCT": "50",
          "FGA": "8",
          "FGM": "2",
          "FG_PCT": "25",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "27",
          "OREB": "0",
          "PF": "2",
          "PTS": "5",
          "STL": "0",
          "TOV": "4",
          "TREB": "3",
          "first_name": "Trae",
          "last_name": "Young",
          "name": "Trae Young",
          "starter": "True"
        },
        {
          "+/-": "-12",
          "AST": "1",
          "BLK": "1",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "8",
          "FGM": "3",
          "FG_PCT": "38",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "27",
          "OREB": "3",
          "PF": "3",
          "PTS": "6",
          "STL": "1",
          "TOV": "1",
          "TREB": "9",
          "first_name": "Dewayne",
          "last_name": "Dedmon",
          "name": "Dewayne Dedmon",
          "starter": "True"
        },
        {
          "+/-": "-7",
          "AST": "3",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "7",
          "FG3A": "5",
          "FG3M": "4",
          "FG3_PCT": "80",
          "FGA": "14",
          "FGM": "8",
          "FG_PCT": "57",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "26",
          "OREB": "1",
          "PF": "4",
          "PTS": "21",
          "STL": "0",
          "TOV": "2",
          "TREB": "8",
          "first_name": "John",
          "last_name": "Collins",
          "name": "John Collins",
          "starter": "True"
        },
        {
          "+/-": "-8",
          "AST": "1",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "5",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "8",
          "FGM": "3",
          "FG_PCT": "38",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "20",
          "OREB": "2",
          "PF": "1",
          "PTS": "8",
          "STL": "0",
          "TOV": "0",
          "TREB": "7",
          "first_name": "Daniel",
          "last_name": "Hamilton",
          "name": "Daniel Hamilton",
          "starter": "True"
        },
        {
          "+/-": "-6",
          "AST": "0",
          "BLK": "3",
          "DOUBLE": "double",
          "DREB": "5",
          "FG3A": "3",
          "FG3M": "1",
          "FG3_PCT": "33",
          "FGA": "19",
          "FGM": "11",
          "FG_PCT": "58",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "27",
          "OREB": "6",
          "PF": "3",
          "PTS": "24",
          "STL": "0",
          "TOV": "1",
          "TREB": "11",
          "first_name": "Alex",
          "last_name": "Len",
          "name": "Alex Len",
          "starter": "False"
        },
        {
          "+/-": "-8",
          "AST": "0",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "6",
          "FG3A": "1",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "9",
          "FGM": "5",
          "FG_PCT": "56",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "25",
          "OREB": "1",
          "PF": "3",
          "PTS": "11",
          "STL": "1",
          "TOV": "1",
          "TREB": "7",
          "first_name": "DeAndre'",
          "last_name": "Bembry",
          "name": "DeAndre' Bembry",
          "starter": "False"
        },
        {
          "+/-": "5",
          "AST": "5",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "7",
          "FGM": "2",
          "FG_PCT": "29",
          "FTA": "4",
          "FTM": "3",
          "FT_PCT": "75",
          "MIN": "19",
          "OREB": "0",
          "PF": "0",
          "PTS": "8",
          "STL": "3",
          "TOV": "2",
          "TREB": "2",
          "first_name": "Jeremy",
          "last_name": "Lin",
          "name": "Jeremy Lin",
          "starter": "False"
        },
        {
          "+/-": "-5",
          "AST": "2",
          "BLK": "0",
          "DOUBLE": "none",
          "DREB": "2",
          "FG3A": "4",
          "FG3M": "1",
          "FG3_PCT": "25",
          "FGA": "6",
          "FGM": "1",
          "FG_PCT": "17",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "13",
          "OREB": "0",
          "PF": "0",
          "PTS": "3",
          "STL": "0",
          "TOV": "0",
          "TREB": "2",
          "first_name": "Vince",
          "last_name": "Carter",
          "name": "Vince Carter",
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
          "MIN": "5",
          "OREB": "0",
          "PF": "1",
          "PTS": "0",
          "STL": "0",
          "TOV": "1",
          "TREB": "0",
          "first_name": "Justin",
          "last_name": "Anderson",
          "name": "Justin Anderson",
          "starter": "False"
        },
        {
          "+/-": "-2",
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
          "first_name": "Tyler",
          "last_name": "Dorsey",
          "name": "Tyler Dorsey",
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
      "game_number": "37",
      "line_score": {
        "H1": {
          "AST": "98",
          "BLK": "02",
          "DREB": "712",
          "FG3A": "1111",
          "FG3M": "44",
          "FG3_PCT": "4",
          "FGA": "2326",
          "FGM": "1210",
          "FG_PCT": "52",
          "FTA": "20",
          "FTM": "10",
          "FT_PCT": "50",
          "MIN": "6060",
          "OREB": "22",
          "PTS": "2924",
          "STL": "11",
          "TOV": "25",
          "TREB": "734"
        },
        "H2": {
          "AST": "72",
          "BLK": "13",
          "DREB": "810",
          "FG3A": "63",
          "FG3M": "20",
          "FG3_PCT": "32",
          "FGA": "2521",
          "FGM": "126",
          "FG_PCT": "5",
          "FTA": "83",
          "FTM": "52",
          "FT_PCT": "63",
          "MIN": "6060",
          "OREB": "63",
          "PTS": "3114",
          "STL": "30",
          "TOV": "34",
          "TREB": "873"
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
          "AST": "9",
          "BLK": "0",
          "DREB": "7",
          "FG3A": "11",
          "FG3M": "4",
          "FG3_PCT": "36",
          "FGA": "23",
          "FGM": "12",
          "FG_PCT": "52",
          "FTA": "2",
          "FTM": "1",
          "FT_PCT": "50",
          "MIN": "60",
          "OREB": "2",
          "PTS": "29",
          "STL": "1",
          "TOV": "2",
          "TREB": "9"
        },
        "Q2": {
          "AST": "8",
          "BLK": "2",
          "DREB": "12",
          "FG3A": "11",
          "FG3M": "4",
          "FG3_PCT": "36",
          "FGA": "26",
          "FGM": "10",
          "FG_PCT": "38",
          "FTA": "0",
          "FTM": "0",
          "FT_PCT": "0",
          "MIN": "60",
          "OREB": "2",
          "PTS": "24",
          "STL": "1",
          "TOV": "5",
          "TREB": "14"
        },
        "Q3": {
          "AST": "7",
          "BLK": "1",
          "DREB": "8",
          "FG3A": "6",
          "FG3M": "2",
          "FG3_PCT": "33",
          "FGA": "25",
          "FGM": "12",
          "FG_PCT": "48",
          "FTA": "8",
          "FTM": "5",
          "FT_PCT": "62",
          "MIN": "60",
          "OREB": "6",
          "PTS": "31",
          "STL": "3",
          "TOV": "3",
          "TREB": "14"
        },
        "Q4": {
          "AST": "2",
          "BLK": "3",
          "DREB": "10",
          "FG3A": "3",
          "FG3M": "0",
          "FG3_PCT": "0",
          "FGA": "21",
          "FGM": "6",
          "FG_PCT": "29",
          "FTA": "3",
          "FTM": "2",
          "FT_PCT": "67",
          "MIN": "60",
          "OREB": "3",
          "PTS": "14",
          "STL": "0",
          "TOV": "4",
          "TREB": "13"
        },
        "game": {
          "AST": "26",
          "BLK": "6",
          "DREB": "37",
          "FG3A": "31",
          "FG3M": "10",
          "FG3_PCT": "32",
          "FGA": "95",
          "FGM": "40",
          "FG_PCT": "42",
          "FTA": "13",
          "FTM": "8",
          "FT_PCT": "62",
          "MIN": "4",
          "OREB": "13",
          "PF": "19",
          "PTS": "98",
          "STL": "5",
          "TOV": "14",
          "TREB": "50"
        }
      },
      "losses": "26",
      "name": "Hawks",
      "next_game": {
        "city": "Milwaukee",
        "day": "4",
        "dayname": "Friday",
        "is_home": "False",
        "month": "January",
        "opponent_name": "Bucks",
        "opponent_place": "Milwaukee",
        "stadium": "Fiserv Forum",
        "year": "2019"
      },
      "next_game_id": "4982",
      "place": "Atlanta",
      "previous_game_id": "5677",
      "wins": "11"
    }
  }
}
````

### Human reference outputs

**Reference 1**

````text
The Washington Wizards defeated the Atlanta Hawks, 114 - 98, at Capital One Arena on Wednesday evening. The Wizards (15 - 23) had notched 10 of their 14 victories on their home floor coming in, so it wasn't a surprise to see them jump out to a 64 - 53 halftime lead. The Hawks (11 - 26) seemed to wake up at intermission, however, compiling 31 points in the third quarter to slice seven points off their deficit. Atlanta clawed all the way back to knot the game at 94 with 6:44 remaining, before Washington would flash their killer instinct. The home squad would go on to finish the game on an 18 - 4 run to seal the victory, and they saw all five members of their starting five hit double digits in the scoring column. Alex Len paced the Hawks with 24 points in 23 minutes off the bench. He added 11 rebounds and three blocks. John Collins supplied 21 points, eight boards and three assists. Kyle Huerter turned in 12 points, five assists, one rebound and one block. DeAndre' Bembry registered 11 points and seven rebounds. Daniel Hamilton and Jeremy Lin generated eight points apiece, with Hamilton also hauling in seven rebounds. Tre Young mustered just five points but dished out nine assists and recorded one block. Bradley Beal led the Wizards with 24 points and also posted six assists, four rebounds and two steals. Jeff Green managed 22 points, six rebounds and six assists. Thomas Bryant managed a 16 - point, 15 - rebound double - double that also included one assist, two steals and two blocks. Tomas Satoransky delivered 14 points, 11 rebounds, seven assists and two steals. Trevor Ariza collected 12 points, five rebounds, four assists and one steal. Otto Porter, Jr. led the bench with nine points. The Hawks remain on the road and tangle with the Milwaukee Bucks on Friday night, while the Wizards pay a visit to the Miami Heat on Friday evening as well.
````

**Reference 2**

````text
The Washington Wizards defeated the Atlanta Hawks , 114 - 98 , at Capital One Arena on Wednesday evening . The Wizards ( 15 - 23 ) had notched 10 of their 14 victories on their home floor coming in , so it was n't a surprise to see them jump out to a 64 - 53 halftime lead . The Hawks ( 11 - 26 ) seemed to wake up at intermission , however , compiling 31 points in the third quarter to slice seven points off their deficit . Atlanta clawed all the way back to knot the game at 94 with 6:44 remaining , before Washington would flash their killer instinct . The home squad would go on to finish the game on an 18 - 4 run to seal the victory , and they saw all five members of their starting five hit double digits in the scoring column . Alex Len paced the Hawks with 24 points in 23 minutes off the bench . He added 11 rebounds and three blocks . John Collins supplied 21 points , eight boards and three assists . Kyle Huerter turned in 12 points , five assists , one rebound and one block . DeAndre ' Bembry registered 11 points and seven rebounds . Daniel Hamilton and Jeremy Lin generated eight points apiece , with Hamilton also hauling in seven rebounds . Tre Young mustered just five points but dished out nine assists and recorded one block . Bradley Beal led the Wizards with 24 points and also posted six assists , four rebounds and two steals . Jeff Green managed 22 points , six rebounds and six assists . Thomas Bryant managed a 16 - point , 15 - rebound double - double that also included one assist , two steals and two blocks . Tomas Satoransky delivered 14 points , 11 rebounds , seven assists and two steals . Trevor Ariza collected 12 points , five rebounds , four assists and one steal . Otto Porter , Jr. led the bench with nine points . The Hawks remain on the road and tangle with the Milwaukee Bucks on Friday night , while the Wizards pay a visit to the Miami Heat on Friday evening as well .
````

### Full System output

````markdown
The Washington Wizards defeated the Atlanta Hawks 114-98 at Capital One Arena on Wednesday, January 2, 2019, in a 2018-season matchup.
Washington entered with a 15-23 record in its 38th game, while Atlanta arrived at 11-26 in its 37th game.
Washington led at the end of every quarter, ahead 35-29 after the first, 64-53 at halftime, and 88-84 after three.
The Hawks' only quarter-winning margin was a 31-24 third period, while the Wizards closed with a 26-14 fourth quarter to seal the result.
Bradley Beal and Alex Len tied for game-high scoring honours with 24 points each; Jeff Green added 22 for the Wizards, and John Collins paced Atlanta with 21.
Len also led the game with 11 field goals made and 3 blocks, grabbed 11 rebounds and a game-high 6 offensive rebounds, while Thomas Bryant pulled down a game-high 15 rebounds (14 defensive) and Trae Young dished out a game-high 9 assists.
Tomáš Satoranský supported Washington with 11 rebounds and 7 assists, while Kevin Huerter and Jeremy Lin each dished out 5 assists for Atlanta.
Chasson Randle and Jeremy Lin each recorded a game-high 3 steals, and Jeff Green and John Collins each made a game-high 4 three-pointers.
The largest team-level gap in the supplied statistics came at the free-throw line, where the Wizards finished 17 of 23 and the Hawks 8 of 13.
Washington also made more field goals than Atlanta (43-40) despite fewer attempts (92-95), and held a 10-5 edge in steals while committing fewer turnovers (10-14).
Atlanta, meanwhile, controlled the glass, outrebounding Washington 50-48, and blocked more shots (6-2).
Washington held a 38-37 edge in defensive rebounds, while the Hawks led 13-10 on the offensive glass.
The Wizards also recorded a narrow 29-26 advantage in assists.
Both teams return to action on Friday, January 4, 2019, with Washington visiting the Miami Heat and Atlanta travelling to the Milwaukee Bucks.
````

### Baseline output

````markdown
The strongest supported finding is that the Washington Wizards defeated the Atlanta Hawks 114–98 on Wednesday, January 2, 2019, at Capital One Arena in Washington.

- The Wizards led after every quarter except the third, outscoring the Hawks 35–29 in Q1, 29–24 in Q2, and 26–14 in Q4. Atlanta won Q3 31–24, but Washington closed the game strongly.
- Bradley Beal led all scorers with 24 points, and Jeff Green added 22 points. Thomas Bryant (16), Tomáš Satoranský (14), and Trevor Ariza (12) joined them, giving the Wizards five starters in double figures.
- Alex Len led the Hawks with 24 points off the bench, while John Collins scored 21. No other Atlanta player reached 15 points.
- Washington shot better overall: 47% from the field (43/92) vs. Atlanta's 42% (40/95), and 74% from the free-throw line vs. Atlanta's 62%.
- The Wizards committed fewer turnovers (10 vs. 14) and recorded more assists (29 vs. 26) and steals (10 vs. 5). The Hawks had more rebounds (50 vs. 48) and blocks (6 vs. 2).
- Attendance was 15,300, below the arena capacity of 20,400.
- Entering the game, the Wizards were 15–23 and the Hawks were 11–26.
````

### Automatic metrics

| Metric | Better direction | Baseline | Full System | Adjusted difference | Preferred |
| --- | --- | --- | --- | --- | --- |
| AlignScore (base) | Higher | 0.1035 | 0.1258 | 0.0222 | Full System |
| BERTScore F1 | Higher | 0.8268 | 0.8494 | 0.0225 | Full System |
| BLEU | Higher | 0.0701 | 0.0991 | 0.0290 | Full System |
| chrF | Higher | 0.3069 | 0.4141 | 0.1072 | Full System |
| HHEM mean support | Higher | 0.0590 | 0.0327 | -0.0264 | Baseline |
| HHEM minimum sentence support | Higher | 0.0141 | 0.0071 | -0.0070 | Baseline |
| HHEM unsupported-sentence rate | Lower | 1.0000 | 1.0000 | 0.0000 | Tie |
| METEOR | Higher | 0.2102 | 0.2789 | 0.0687 | Full System |
| ROUGE-1 | Higher | 0.4165 | 0.4746 | 0.0581 | Full System |
| ROUGE-2 | Higher | 0.1585 | 0.1589 | 0.0004 | Full System |
| ROUGE-L | Higher | 0.2068 | 0.2272 | 0.0204 | Full System |
| ROUGE-Lsum | Higher | 0.2068 | 0.2272 | 0.0204 | Full System |
| TER | Lower | 0.8319 | 0.8459 | -0.0140 | Baseline |

### GPT-5.6 Sol structured annotations

**Full System**

1. **CONTEXT**
   - Error span: Washington entered with a 15-23 record in its 38th game, while Atlanta arrived at 11-26 in its 37th game.
   - Correction or explanation: Those records sum to the listed game numbers and include this result, so they are postgame records. Before the game, Washington would have been 14-23 and Atlanta 11-25.
2. **WORD**
   - Error span: John Collins paced Atlanta with 21.
   - Correction or explanation: Alex Len led Atlanta with 24 points; Collins scored 21.
3. **CONTEXT**
   - Error span: The largest team-level gap in the supplied statistics came at the free-throw line
   - Correction or explanation: This broad comparison is false as written because the supplied points totals differ by 16, exceeding the free-throw differences of nine makes and 10 attempts.
4. **TASK/FORMAT**
   - Error span: Entire generated output
   - Correction or explanation: The request specified a multi-paragraph report, but the output is presented as a single paragraph.

**Baseline**

1. **WORD**
   - Error span: The Wizards led after every quarter except the third
   - Correction or explanation: Washington led after every quarter, including 88–84 after the third. The Hawks won the third quarter 31–24, but did not take the overall lead.
2. **CONTEXT**
   - Error span: Entering the game, the Wizards were 15–23 and the Hawks were 11–26.
   - Correction or explanation: Those are the postgame records because they total each team's listed game number. Entering the game, Washington was 14–23 and Atlanta was 11–25.
3. **TASK/FORMAT**
   - Error span: The output is presented as one dash-separated paragraph.
   - Correction or explanation: The requested output mode was a multi-paragraph game report, not a single paragraph formatted as an inline list.

### Full System provenance and execution record

| Property | Value |
| --- | --- |
| Run ID | 20260821T013838Z_4f66014f7c |
| Execution outcome | success |
| Final generation path | normal_llm_writer |
| Final Writer mode | llm_writer |
| Release status | approved |
| Audit decision | pass |
| Repair rounds | 0 |
| Native support rate | 1.0000 |
| Factual sentences | 14 |
| Supported sentences | 14 |
| Evidence items | 42 |
| Verified facts | 39 |
| Rejected facts | 4 |
| Verified insights | 6 |
| Rejected insights | 6 |
| Full System words | 313 |
| Baseline words | 197 |
| Full System elapsed seconds | 1203.4145 |
| Baseline elapsed seconds | 9.0249 |
| Full System provider-reported tokens | 609511 |
| Baseline provider-reported tokens | 8975 |
| Pipeline result | evaluation/protected_holdout_full_system/generations/runs/sportsett_basketball__6127/full_system/sportsett_basketball/20260821T013838Z_4f66014f7c/pipeline_result.json |

# Appendix B. Complete GPT-5.6 Sol non-zero annotations

This appendix repeats every non-zero annotation in one place for taxonomy analysis. Zero-error records remain visible in each case section.

## sportsett_basketball / 5130 / Baseline

1. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode is a multi-paragraph report. The content should be divided into at least two coherent paragraphs.

## sportsett_basketball / 5130 / Full System

1. **CONTEXT**
   - Error span: Los Angeles entered with 6 wins and 4 losses, while Minnesota entered with 4 wins and 7 losses.
   - Correction or explanation: The listed records include this result: the Clippers' 6-4 record totals their 10 games, and the Timberwolves' 4-7 record totals their 11 games. They therefore finished the game at those records rather than entered with them; their pregame records were 5-4 and 4-6, respectively.
2. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode is a multi-paragraph report, so the report should be divided into at least two coherent paragraphs.

## sportsett_basketball / 5372 / Baseline

1. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode was a multi-paragraph report. The content should be divided into at least two coherent paragraphs, for example separating the result/team contrasts from the individual performances.

## sportsett_basketball / 5372 / Full System

1. **CONTEXT**
   - Error span: arriving in sixth place compared with the Kings' 13th
   - Correction or explanation: The source lists Utah's conference standing as sixth and Sacramento's as 13th, but does not establish that these were their standings entering the game. Avoid the pregame implication of “arriving.”
2. **TASK/FORMAT**
   - Error span: The entire report is presented as a single paragraph.
   - Correction or explanation: The requested output mode is a multi-paragraph report, so the report should be divided into at least two paragraphs.

## sportsett_basketball / 5786 / Baseline

1. **TASK/FORMAT**
   - Error span: The entire generated output is presented as a six-item bullet list rather than a multi-paragraph report.
   - Correction or explanation: The request specifies a coherent multi-paragraph game report. The accurate points should be rewritten as connected prose across multiple paragraphs.

## sportsett_basketball / 5786 / Full System

1. **CONTEXT**
   - Error span: Toronto entered with a 6-0 record and first place in its conference standings, while Dallas arrived at 2-3.
   - Correction or explanation: The listed records are postgame records: Toronto improved to 6-0 and Dallas fell to 2-3. They did not enter the game with those records.
2. **TASK/FORMAT**
   - Error span: The entire report is presented as one paragraph.
   - Correction or explanation: The requested output mode was a multi-paragraph report, but the generated report contains only one paragraph.

## sportsett_basketball / 5955 / Baseline

1. **TASK/FORMAT**
   - Error span: Strongest supported findings: - Denver won ... - At the time, the Nuggets were 13–7 ...
   - Correction or explanation: The request specifies a coherent multi-paragraph game report, but the output presents nearly all details as a single inline bullet list rather than multi-paragraph report prose.

## sportsett_basketball / 5955 / Full System

1. **CONTEXT**
   - Error span: Denver (13-7) and Oklahoma City (12-7) each entered the game with seven losses
   - Correction or explanation: Those are the teams' postgame records: Denver's 13 wins include this victory, and Oklahoma City's seventh loss is this defeat. Their entering records were therefore 12-7 and 12-6, respectively.
2. **OMISSION**
   - Error span: Russell Westbrook finished with 16 points and a game-high 12 assists
   - Correction or explanation: The report omits Westbrook's 10 rebounds, which completed a notable 16-point, 10-rebound, 12-assist triple-double.
3. **TASK/FORMAT**
   - Error span: Entire generated output
   - Correction or explanation: The requested output mode was a multi-paragraph report, but the report is presented as a single paragraph.

## sportsett_basketball / 6127 / Baseline

1. **WORD**
   - Error span: The Wizards led after every quarter except the third
   - Correction or explanation: Washington led after every quarter, including 88–84 after the third. The Hawks won the third quarter 31–24, but did not take the overall lead.
2. **CONTEXT**
   - Error span: Entering the game, the Wizards were 15–23 and the Hawks were 11–26.
   - Correction or explanation: Those are the postgame records because they total each team's listed game number. Entering the game, Washington was 14–23 and Atlanta was 11–25.
3. **TASK/FORMAT**
   - Error span: The output is presented as one dash-separated paragraph.
   - Correction or explanation: The requested output mode was a multi-paragraph game report, not a single paragraph formatted as an inline list.

## sportsett_basketball / 6127 / Full System

1. **CONTEXT**
   - Error span: Washington entered with a 15-23 record in its 38th game, while Atlanta arrived at 11-26 in its 37th game.
   - Correction or explanation: Those records sum to the listed game numbers and include this result, so they are postgame records. Before the game, Washington would have been 14-23 and Atlanta 11-25.
2. **WORD**
   - Error span: John Collins paced Atlanta with 21.
   - Correction or explanation: Alex Len led Atlanta with 24 points; Collins scored 21.
3. **CONTEXT**
   - Error span: The largest team-level gap in the supplied statistics came at the free-throw line
   - Correction or explanation: This broad comparison is false as written because the supplied points totals differ by 16, exceeding the free-throw differences of nine makes and 10 attempts.
4. **TASK/FORMAT**
   - Error span: Entire generated output
   - Correction or explanation: The request specified a multi-paragraph report, but the output is presented as a single paragraph.

## totto / totto-validation-1828 / Baseline

1. **TASK/FORMAT**
   - Error span: The generated output consists of four sentences.
   - Correction or explanation: The request requires exactly one concise sentence.
2. **TASK/FORMAT**
   - Error span: Lasse Staw’s career statistics show that he never scored... His highest league-appearance totals were 22 in 2011 and 18 in 2010.
   - Correction or explanation: Most of the output discusses unhighlighted career totals, seasons, clubs, and appearance figures; it should describe only the highlighted cells.
3. **OMISSION**
   - Error span: Allsvenskan
   - Correction or explanation: The highlighted division, Allsvenskan, is omitted; the highlighted cells indicate 2012, Syrianska, and Allsvenskan.

## totto / totto-validation-1828 / Full System

1. **WORD**
   - Error span: under the Career Total header
   - Correction or explanation: The highlighted 2012, Syrianska, and Allsvenskan cells are not under a Career Total header; Career Total is a separate row label.
2. **TASK/FORMAT**
   - Error span: in the row containing 8 and 0, within Career statistics / Lasse Staw
   - Correction or explanation: The task asks only for a concise description of the highlighted cells, so references to unhighlighted values and surrounding page/section metadata are outside the requested scope.

## totto / totto-validation-4467 / Baseline

1. **TASK/FORMAT**
   - Error span: in Beijing, China, on 28 August 2015. This improved upon her previous world leading mark of 7.12 meters set on 27 June 2015 in Eugene, United States.
   - Correction or explanation: The response uses two sentences and discusses non-highlighted location, date, and prior-mark cells, contrary to the requirement for exactly one concise sentence describing only the highlighted cells. It should state only that Tianna Bartoletta (USA) established a world-leading mark of 7.14.

## totto / totto-validation-6067 / Baseline

1. **TASK/FORMAT**
   - Error span: the largest number shown in the table; and (2) the “other data” column rises steadily from 26,831 in 2001 to 98,603 in 2010, with no figures provided for 2012 or 2013
   - Correction or explanation: This compares the highlighted value with unhighlighted cells and describes the unhighlighted “other data” column, contrary to the instruction not to discuss unrelated cells. The sentence should focus only on the highlighted 2011 Peruvian-born population of 246,908.

## totto / totto-validation-839 / Baseline

1. **TASK/FORMAT**
   - Error span: No conference record, standing, or bowl/playoff information is provided.
   - Correction or explanation: This second sentence violates the requirement to write exactly one sentence and discusses unhighlighted table cells unrelated to the highlighted content.

## totto / totto-validation-839 / Full System

1. **OMISSION**
   - Error span: Maine Black Bears in 1900
   - Correction or explanation: The highlighted team heading also identifies the Maine Black Bears as members of the Maine Intercollegiate Athletic Association, which the output omits.

## totto / totto-validation-912 / Baseline

1. **TASK/FORMAT**
   - Error span: Tyrell Sutton’s strongest season was 2015: he set career highs in rushing yards (1,059), rushing touchdowns (5), carries (180), receptions (43), and receiving yards (334), while averaging 5.9 yards per carry with a long run of 54 yards. Across his CFL career, he totaled 3,841 rushing yards on 698 carries (5.5 average) with 17 rushing touchdowns, plus 178 receptions for 1,539 yards and 3 receiving touchdowns in 73 games. His 2016 season was highlighted but was shortened to 7 games, producing 412 rushing yards on 74 carries (5.6 average) with 0 touchdowns.
   - Correction or explanation: The request requires exactly one concise sentence about only the highlighted cells. The output uses three sentences and discusses unrelated 2015 statistics, career totals, and the unhighlighted 2016 touchdown value.
2. **CONTEXT**
   - Error span: was shortened to 7 games
   - Correction or explanation: The table shows that Sutton played 7 games in 2016, but it does not establish that the season was shortened.

## web_nlg / web_nlg_en-test-1330 / Baseline

1. **NUMBER**
   - Error span: born in England in 1942
   - Correction or explanation: The source gives the full birth date as 1942-01-01, but the output states only the year, omitting January 1.

# Appendix C. Reproducibility inventory

| Artifact | Path | Bytes |
| --- | --- | --- |
| Protected selection manifest | table2text_pydanticai/evaluation/protected_holdout_full_system/prepared/protected_selection_manifest.json | 10612 |
| Full System batch manifest | table2text_pydanticai/evaluation/protected_holdout_full_system/results/protected_batch_manifest.json | 14030 |
| Full System configuration | table2text_pydanticai/evaluation/protected_holdout_full_system/config/protected_full_system_flash.json | 2744 |
| Full System generation summary | table2text_pydanticai/evaluation/protected_holdout_full_system/results/protected_generation_summary.csv | 38434 |
| Full System stage usage | table2text_pydanticai/evaluation/protected_holdout_full_system/results/stage_token_usage.csv | 11827 |
| Sealed paired outputs | table2text_pydanticai/evaluation/protected_holdout_baseline/comparison/full_system_and_baseline_sealed.jsonl | 441565 |
| Metrics input with references | table2text_pydanticai/evaluation/protected_holdout_baseline/comparison/full_system_and_baseline_for_metrics.jsonl | 485887 |
| Baseline sealed generations | table2text_pydanticai/evaluation/protected_holdout_baseline/generations/baseline_generations_sealed.jsonl | 203962 |
| Reference metrics | table2text_pydanticai/evaluation/protected_holdout_baseline/results/reference_alignment_metrics.jsonl | 278886 |
| Source-grounded metrics | table2text_pydanticai/evaluation/protected_holdout_baseline/results/source_grounded_metrics.jsonl | 186120 |
| GPT-5.6 Sol annotations | table2text_pydanticai/evaluation/protected_holdout_baseline/gpt56_judge/results/gpt56_structured_annotations.jsonl | 31091 |

End of evidence bank. Numerical claims in a dissertation should be copied from the direction-aware tables in this document or recomputed from the linked JSONL artifacts.
