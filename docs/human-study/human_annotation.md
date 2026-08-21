# Human Annotation Results

This file consolidates five volunteer annotation bundles. It also records a
separate researcher adjudication across the project's most-tested examples
and experimental configurations.

The provenance groups must remain separate in analysis:

- Bundles 1-5 are volunteer responses.
- The cross-configuration section is a project-researcher adjudication and is
  not an additional participant or an LLM-as-a-judge result.



## Bundle Coverage

| Bundle | Source | SportSett | E2E | ToTTo | WebNLG | DART |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | volunteer_csv_1 | 4934 | e2e_nlg-test-178 | totto-validation-217 | web_nlg_en-test-51 | dart-test-204 |
| 2 | volunteer_csv_2 | 4972 | e2e_nlg-test-51 | totto-validation-204 | web_nlg_en-test-178 | dart-test-217 |
| 3 | volunteer_csv_3 | 4975 | e2e_nlg-test-54 | totto-validation-244 | web_nlg_en-test-54 | dart-test-244 |
| 4 | volunteer_csv_4 | 4982 | e2e_nlg-test-61 | totto-validation-260 | web_nlg_en-test-61 | dart-test-260 |
| 5 | volunteer_csv_5 | 4986 | e2e_nlg-test-65 | totto-validation-712 | web_nlg_en-test-65 | dart-test-53 |

## Consolidated Annotation Table

`Output A` is the workflow/full-system output. `Output B` is the raw-generic baseline output.

| Bundle | Dataset/example | Output A annotation | Output B annotation |
| --- | --- | --- | --- |
| 1 | SportSett 4934 | `"third place in their conference" / "sixth" \| NOT CHECKABLE \| Conference standings were not supplied in the source representation used by the annotator.` | `"in a 20,500-capacity arena" \| NOT CHECKABLE \| The annotator judged arena capacity unavailable from the supplied source packet.` |
| 1 | E2E 178 | Blank response. | Blank response. |
| 1 | ToTTo 217 | `none` | `[OMISSION: Jan Koukal] \| OMISSION \| Jan Koukal and his office dates are omitted. Additional claims about the full Prague mayor table were marked as fabrication/not checkable by the volunteer.` |
| 1 | WebNLG 51 | Blank response. | Blank response. |
| 1 | DART 204 | `none` | `none` |
| 2 | SportSett 4972 | `[offensive rebounds] \| NOT CHECKABLE \| The annotator judged the offensive-rebound statement unsupported by the supplied table view.` | `None` |
| 2 | E2E 51 | Blank response. | `None` |
| 2 | ToTTo 204 | Blank response. | `[further results] \| NOT CHECKABLE \| The annotator marked part of the broader election-summary claim as not checkable from the supplied focused table view.` |
| 2 | WebNLG 178 | Blank response. | `None` |
| 2 | DART 217 | `CONTEXT ERROR` | `None` |
| 3 | SportSett 4975 | `"line-score family" \| OTHER \| The phrase does not exist in the supplied table/source.` | `"16,500 in a 17,500-capacity arena" \| NOT CHECKABLE \| The annotator judged the capacity claim unavailable from the supplied source packet.` |
| 3 | E2E 54 | Blank response. | Blank response. |
| 3 | ToTTo 244 | `[OMISSION: City or Town/District] \| OMISSION \| Everett was not mentioned. [OMISSION: Electoral history] \| OMISSION \| The output does not mention that George Keverian retired to run for state treasurer.` | Several broad party/history claims marked `NOT CHECKABLE` by the volunteer. |
| 3 | WebNLG 54 | `None` | Blank response. |
| 3 | DART 244 | Blank response. | Blank response. |
| 4 | SportSett 4982 | `"Milwaukee entered the matchup with a 27-10 record ... Atlanta entered at 11-27" \| CONTEXT \| These records appear to be post-game records because they total the listed game numbers and include this result; pre-game records would be 26-10 and 11-26.` | `"The Bucks entered the game with a 27-10 record ... the Hawks were 11-27" \| CONTEXT \| These are post-game records, not clearly pre-game records. The output is also presented as a heading plus bullet list rather than a multi-paragraph report. |
| 4 | E2E 61 | `None` | `None` |
| 4 | ToTTo 260 | `None` | `"reflecting additional taxes beyond the federal rate" \| NOT CHECKABLE/CONTEXT \| The table shows corporate and combined rates but does not explain the Swiss difference as additional taxes beyond a federal rate. [OMISSION: France 34.43%] \| OMISSION \| The output states that France and Switzerland are highlighted but does not verbalise France's highlighted 34.43% rate. The output also violates the one-sentence focus by giving a multi-bullet table summary.` |
| 4 | WebNLG 61 | `None` | `None` |
| 4 | DART 260 | `None` | `None` |
| 5 | SportSett 4986 | `"Milwaukee entered with a 34-12 record and Dallas with a 20-26 mark" \| CONTEXT \| These records total 46 games and appear to include this game result; pre-game records would be 33-12 and 20-25. The output is also not clearly realised as a multi-paragraph report in the evaluated serialization.` | `TASK/FORMAT \| The output is a hyphen-separated bullet list rather than a multi-paragraph game report. No clear factual error was identified from the supplied source values.` |
| 5 | E2E 65 | `None` | `None` |
| 5 | ToTTo 712 | `None` | `TASK/FORMAT \| The requested output is one sentence focused on the highlighted row, but the response gives three sentences and includes broader tour-summary context before the highlighted date.` |
| 5 | WebNLG 65 | `None` | `None` |
| 5 | DART 53 | `None` | `None` |

## Compact Error-Count Summary

Blank volunteer responses are kept distinct from explicit `None` responses. The counts below therefore only count explicit annotations.

| Bundle | Source | Output A explicit issue count | Output B explicit issue count | Main pattern |
| --- | --- | ---: | ---: | --- |
| 1 | volunteer_csv_1 | 2 | 1 | Workflow issue: unchecked standings wording; raw issue: capacity claim. Raw ToTTo also omitted the focused proposition. |
| 2 | volunteer_csv_2 | 2 | 1 | Workflow issue: SportSett/source-view support and one DART context mark; raw mostly accepted except ToTTo focused-table concern. |
| 3 | volunteer_csv_3 | 3 | 2+ | Workflow issues: SportSett wording and ToTTo omissions; raw issues: capacity and broad unsupported ToTTo claims. |
| 4 | volunteer_csv_4 | 1 | 3 | Main raw weakness is ToTTo over-generation plus unsupported explanation; both SportSett outputs misframe post-game records as entry records. |
| 5 | volunteer_csv_5 | 1 | 2 | Workflow issue is SportSett post-game-record wording; raw issues are mostly format/focus rather than factual numbers. |

## Data Used For The Annotations

### Evidence hierarchy

The annotations were based on the following evidence, in this order:

1. The complete prepared `source_text` for each example in
   `table2text_pydanticai/evaluation/prepared/all_examples.jsonl`.
2. The task request, task family, output mode, and dataset metadata stored with
   the prepared example and generation record.
3. The exact saved `generated_text` for each evaluated variant.
4. Human reference texts, used as secondary evidence for expected content and
   genre, but not allowed to override the structured source.
5. Saved GPT-5.6 judge annotations, consulted only when comparing the
   researcher's judgement with the automated judge. They were not treated as
   factual ground truth.

No external web information was used. Automatic metric scores were not used to
decide whether a statement was factually correct. Volunteer responses were
kept separate and were not treated as the authority for the researcher
adjudication.

### Volunteer bundle inputs

| Volunteer bundle | Examples inspected | Full/raw outputs used |
| --- | --- | --- |
| `volunteer_csv_4` | SportSett `4982`; E2E `e2e_nlg-test-61`; ToTTo `totto-validation-260`; WebNLG `web_nlg_en-test-61`; DART `dart-test-260` | Matching `full_system` and `raw_generic_flash` records from the 25-example paired evaluation and the rendered human-annotation packet. |
| `volunteer_csv_5` | SportSett `4986`; E2E `e2e_nlg-test-65`; ToTTo `totto-validation-712`; WebNLG `web_nlg_en-test-65`; DART `dart-test-53` | Matching `full_system` and `raw_generic_flash` records from the 25-example paired evaluation and the rendered human-annotation packet. |

### Cross-configuration source examples

The workflow received the task-specific requests shown below. The main
raw-generic baseline instead received the same generic request for every
dataset: `Understand the supplied data and report its strongest supported
findings.` Consequently, prompt adherence and benchmark-task fulfilment were
recorded separately when they led to different judgements.

| Dataset/example | Task supplied to the workflow | Structured source facts used in annotation | References |
| --- | --- | --- | ---: |
| SportSett Basketball `4934` | Write a coherent game report, lead with the result, select important performances and contrasts, and do not invent information. | Full game object, both team records and game numbers, conference standings, quarter and final scores, team totals, all player box scores, venue, attendance/capacity, and next-game metadata. | 2 near-duplicate reports |
| ToTTo `totto-validation-204` | Write exactly one concise sentence describing only the highlighted table cells. | Page `Ma Ying-jeou`; section `Inauguration`; highlighted percentage `58.45%`; associated total `7,659,014`; candidate hierarchy and surrounding non-highlighted row. | 2 |
| E2E `e2e_nlg-test-51` | Express all and only the supplied attributes in one or two fluent sentences. | `name[Clowns]`, `eatType[pub]`, `customer rating[5 out of 5]`, and `near[Crowne Plaza Hotel]`. | 9 |
| WebNLG `web_nlg_en-test-51` | Express all and only the supplied triples as short, coherent natural language. | `ALCO_RS-3 | engine | Four-stroke_engine`; `ALCO_RS-3 | cylinderCount | 12`; `ALCO_RS-3 | length | 17068.8 (millimetres)`. | 3 |
| DART `dart-test-53` | Express all and only the supplied triples as short, coherent natural language. | `University of Makati UM Pep Squad | TOTAL | 211.5`; `University of Makati UM Pep Squad | RANK | 11`. | 1 |

### SportSett 4934 facts used for checking claims

| Evidence group | Values used |
| --- | --- |
| Event | Sunday 2 December 2018; Wells Fargo Center, Philadelphia, Pennsylvania; attendance 20,300; capacity 20,500. |
| Result | Philadelphia 76ers 103, Memphis Grizzlies 95; margin 8. |
| Records and game counts | Philadelphia 17-8 in game 25; Memphis 13-9 in game 22. Because each record total equals the listed game number, the values include this result and are post-game records. |
| Conference context | Philadelphia third in the Eastern Conference; Memphis sixth in the Western Conference. |
| Quarter scores | Philadelphia: 26, 28, 24, 25. Memphis: 25, 19, 24, 27. Cumulative checkpoints: 26-25, 54-44, 78-68, 103-95. |
| Team contrasts | FGM 36-33; 3PM 8-11; FTM 23-18; rebounds 44-35; assists 22-19; steals 5-7; blocks 2-7; turnovers 16-14. |
| Philadelphia leaders | J.J. Redick 24 points; Jimmy Butler 21; Ben Simmons 19 points, 12 rebounds and 6 assists; Joel Embiid 15 points and 14 rebounds. |
| Memphis leaders | Mike Conley 21 points and 5 assists; Jaren Jackson 17 points and 3 blocks; JaMychal Green 14 points, 7 rebounds and 4 steals. |
| Next games | Both source records specify Wednesday 5 December 2018: Philadelphia at Toronto and Memphis home to the Clippers. |

### Saved generation and evaluation artifacts inspected

| Experiment | Artifact |
| --- | --- |
| Main 25-example Full versus raw-generic Flash comparison | `table2text_pydanticai/evaluation/generations/five_dataset_five_each_raw_generic_flash_20260805_181001_combined_generations.jsonl` |
| Four short-form Pro comparisons | `table2text_pydanticai/evaluation/generations/four_dataset_pro_comparison_20260812_215239_combined_generations.jsonl` |
| SportSett Pro comparisons | `table2text_pydanticai/evaluation/generations/five_dataset_pro_comparison_for_openai_judge_generations.jsonl` and `table2text_pydanticai/evaluation/generations/sportsett_raw_deepseek_v4_pro_generations.jsonl` |
| Flash pipeline with GPT writer | `table2text_pydanticai/evaluation/generations/five_dataset_flash_pipeline_gpt55_writer_generations.jsonl` |
| All-agent GPT exploratory run | `table2text_pydanticai/evaluation/generations/five_dataset_full_system_openai_gpt55_same_as_pro_generations.jsonl` |
| SportSett ablation | `table2text_pydanticai/evaluation/generations/ablation_sportsett_4934_20260805_021058_combined_generations.jsonl` |
| Generic-request experiment | `table2text_pydanticai/evaluation/generations/generic_only_sportsett_basketball_4934_20260805_131536_generations.jsonl` and `table2text_pydanticai/evaluation/generations/generic_only_sportsett_basketball_4934_20260805_162215_generations.jsonl`. |
| Inferred-contract experiment | `table2text_pydanticai/evaluation/generations/sportsett_4934_inferred_contract_20260813_200558_generations.jsonl` and `table2text_pydanticai/evaluation/generations/sportsett_basketball_4934_inferred_contract_deepseek-v4-flash_20260813_203625_generations.jsonl`. |
| LLM-only Flash and Pro | `experiments/llm_only_pipeline/artifacts/sportsett_4934/flash/result.json` and `experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/result.json`. |
| GPT-5.6 structured error annotations | `table2text_pydanticai/evaluation/results/openai_structured_error_annotations.jsonl` and `sportsett_basketball_4934_full_system_openai_judge_annotations.jsonl`. |

The human references were held out from every generation condition. They were
examined only during evaluation. Where a human reference conflicted with the
structured source, the structured source determined the factual annotation.

## Researcher Cross-Configuration Adjudication

**Attribution:** project researcher / author adjudication  
**Date recorded:** 19 August 2026  
**Status:** researcher result; do not pool with volunteer-participant responses
or GPT judge annotations.

The adjudication uses the supplied structured source as the factual authority.
Exact duplicate outputs and punctuation-only reruns are collapsed, while every
materially different configuration is retained. Error categories are `NAME`,
`NUMBER`, `WORD`, `CONTEXT`, `NOT CHECKABLE`, `OMISSION`, and `TASK/FORMAT`.

### Most-Tested Main Comparison

| Dataset/example | Full-system annotation | Raw-generic Flash annotation | Researcher judgement |
| --- | --- | --- | --- |
| SportSett `4934` | `CONTEXT`: the 17-8 and 13-9 post-game records are described as entry records. `TASK/FORMAT`: the evaluated serialization is effectively one paragraph. Coverage is otherwise excellent. | No hard factual error. The bullet-list form only partially fulfils the intended game-report genre, although it follows the generic prompt actually supplied to the raw model. | Factuality and source support: raw. Coverage and intended genre: full. Overall: tie. |
| ToTTo `totto-validation-204` | No identified error. Ma Ying-jeou is correctly identified as receiving 58.45% of the vote. | `CONTEXT`: the result is centred on a "Vincent Siew ticket" instead of Ma's presidential result. The output also includes unrelated rows and totals rather than the highlighted proposition. | Full system, decisively. |
| E2E `e2e_nlg-test-51` | No identified error; all supplied attributes are expressed. | No identified error; all supplied attributes are expressed. | Tie. |
| WebNLG `web_nlg_en-test-51` | No identified error; complete and naturally lexicalised. | No factual error. Retaining `ALCO_RS-3` is a minor readability issue. | Full system, slightly. |
| DART `dart-test-53` | No identified error. | No identified error; wording is marginally more natural. | Tie. |

### Main Pairwise Decisions

| Dataset/example | Factuality | Source support | Coverage | Intended task fit | Overall |
| --- | --- | --- | --- | --- | --- |
| SportSett `4934` | Raw | Raw | Full | Full | Tie |
| ToTTo `204` | Full | Full | Full | Full | Full |
| E2E `51` | Tie | Tie | Tie | Tie | Tie |
| WebNLG `51` | Tie | Tie | Tie | Full | Full |
| DART `53` | Tie | Tie | Tie | Tie | Tie |

### Pro And GPT Model Experiments

| Experiment | Researcher annotation |
| --- | --- |
| SportSett all-Pro workflow | `CONTEXT`: post-game records are described as entry records. `CONTEXT/NUMBER`: Conley and Jackson supplied 38 of Memphis's 95 points, so they did not provide "most of their offense." "Anchored the defense" is not directly checkable. |
| SportSett raw Pro, primary run | `CONTEXT/NUMBER`: attendance of 20,300 in a 20,500-capacity arena is not sold out. `NOT CHECKABLE`: "never trailed over the final three periods" and "never seriously threatened" require play-by-play evidence. "Forced 14 turnovers" attributes causation absent from the source. |
| SportSett raw Pro, alternate run | Numerical claims are correct. Minor `CONTEXT`: "could not overcome the 76ers' balanced all-around performance" gives an unsupported explanation for the result. |
| E2E Full Pro / Raw Pro | Both outputs have no identified error. |
| ToTTo Full Pro | No identified error. |
| ToTTo Raw Pro | `CONTEXT`: "Vincent Siew received 58.45%" assigns the presidential vote share to the vice-presidential candidate. |
| WebNLG Full Pro | Factually correct, but source-like capitalization and parentheses reduce realisation quality. |
| WebNLG Raw Pro | No identified error and more natural than Full Pro. |
| DART Full Pro / Raw Pro | Both outputs have no identified error. |
| Flash pipeline plus GPT writer: SportSett | `CONTEXT`: post-game records are presented as entry records. `NOT CHECKABLE`: quarter endpoints do not prove Philadelphia remained ahead continuously. The serialization is effectively one paragraph. |
| Flash pipeline plus GPT writer: WebNLG | Facts are recoverable, but `Four-stroke_engine` is not lexicalised and the sentence contains a comma splice: `WORD/TASK/FORMAT`. |
| Flash pipeline plus GPT writer: E2E, ToTTo and DART | No identified errors. |
| All-agent GPT experiment | Only the SportSett row completed. It repeats the post-game-record chronology error and remains mechanically phrased in one paragraph. The associated five-row metric aggregate is not treated as a completed five-dataset generation experiment. |

### SportSett 4934 Ablation

| Variant | Researcher annotation | Interpretation |
| --- | --- | --- |
| Full system | One `CONTEXT` chronology error. | Best breadth, but paragraph structure is weak. |
| Raw task-aware Flash | No hard factual error. "Provided a spark" and "protected the lead" are mildly interpretive. | Fluent and coherent. |
| No insight synthesis | Same record chronology error. | The factual backbone survives, but synthesis and breadth decline. |
| No writer-quality revision | Same chronology error. | Quarter information is repeated and organisation is less efficient. |
| No audit-repair rounds | Same chronology error plus severe `TASK/FORMAT`: a mechanical evidence inventory rather than a game report. | Operationally confounded by a model-response failure, so it is not a clean audit ablation. |

The defensible ablation finding is that insight synthesis contributes to
content breadth and relational coverage. The audit-repair and writer-revision
effects are not cleanly isolated because those variants experienced unrelated
operational failures.

### Other SportSett 4934 Experiments

| Variant | Researcher annotation |
| --- | --- |
| Full generic, successful LLM writer | Strong structure and coverage. The material error is the post-game record presented as pre-game. |
| Raw generic, clean version | Source-correct but presented as a findings list rather than a narrative report. |
| Raw generic, alternate version | `CONTEXT`: it says Philadelphia led "after each quarter" while using period scores such as Q2 28-19 instead of the cumulative halftime score 54-44. |
| Full generic deterministic fallback | Chronology error; calls cumulative 103-95 a Q4 segment; exposes internal verification language; excessive data-dump format. |
| Inferred-contract deterministic | Chronology error and vague labels such as "ranking for recorded value." Other stated values are supported. |
| Inferred-contract LLM | Chronology error plus `OTHER`: it says the package lacks season standings even though conference standings are supplied. |
| LLM-only Flash | No hard factual error. `OMISSION`: Memphis's leading performances and most team contrasts are absent. "Near-capacity" is supported by 20,300 attendance against 20,500 capacity. |
| LLM-only Pro | Chronology error and limited team-level contrast; otherwise accurate. |
| Earlier full-system smoke report | Avoids the record error but adds `NOT CHECKABLE` interpretations: Redick "focused purely on scoring" and free throws "neutralized" Memphis's advantages. |
| Historical full-system reruns | Eight of nine materially distinct `full_system` texts describe post-game records as entry records, indicating a persistent semantic issue rather than random variation. |

### Short-Form Development Findings

- ToTTo's earliest full-system output centred Vincent Siew and discussed the
  non-highlighted opponent row. Later full-system, Pro, and GPT-writer outputs
  corrected both problems.
- The verbose E2E draft added unsupported temporal wording (`currently`), but
  the selected evaluation outputs are clean.
- One historical WebNLG output changed the entity identifier to `ALCO
  RS-three`, which is classified as a `NAME` error. Later outputs corrected it.
- Every non-empty DART `53` output is factually correct.
- Five empty raw-generic rows, one for each selected dataset, came from API
  connection errors. They are generation-reliability failures rather than
  factuality annotations.

### Researcher Assessment Of GPT-5.6 Judge Annotations

The GPT-5.6 judge repeatedly identified the main SportSett chronology and
formatting problems. The researcher adjudication nevertheless found three
important limitations:

- the judge missed the raw ToTTo entity-role error and reported only the
  sentence-count issue;
- it marked all five GPT-writer outputs clean, overlooking SportSett's record
  chronology and WebNLG's unlexicalised source token;
- it treated raw-generic formatting as a task violation even though the raw
  model's actual generic prompt did not specify the benchmark output form.

GPT-5.6 annotations are therefore supporting evidence, not the human gold
standard.

### Source And Reference Caveats

- The SportSett reference says Memphis's next game was Tuesday, while the
  structured source says Wednesday. It also contains play-by-play details not
  present in the supplied generation source. The structured source takes
  precedence in this adjudication.
- One E2E reference reverses the pub and nearby-hotel relationship. Source
  fidelity therefore takes precedence over agreement with that malformed
  reference.
