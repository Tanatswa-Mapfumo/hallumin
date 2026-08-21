# GPT-5.6 Sol Structured Error Annotation Results

## Scope and provenance

- Judge label: `gpt-5.6-sol`
- Existing API-authenticated rows retained unchanged: **49**
- Interactive task-aware rows added: **25**
- Interactive canonical-gap rows added: **1**
- Three-condition analysis rows: **75**
- The interactive rows were produced without an OpenAI API call. Their model label follows the active model selection reported for the session, but that identity and the reasoning setting were not returned by an API response.
- Consequently, interactive rows must be reported separately from API-authenticated rows or accompanied by the execution-mode provenance field. They are not a silent replacement for a controlled API run.
- Judgements used the project taxonomy: NAME, NUMBER, WORD, CONTEXT, NOT CHECKABLE, OTHER, OMISSION and TASK/FORMAT.
- The intended basis was source data + task request + one generated output. Human references and automatic metric scores were not used as correctness criteria. Unlike the API runner, the surrounding interactive session was not a formally blinded environment.

## Three-condition totals

| Variant | Outputs | Outputs flagged | Errors |
|---|---:|---:|---:|
| `full_system` | 25 | 5 | 10 |
| `raw_generic_flash` | 25 | 11 | 19 |
| `task_aware_direct_flash` | 25 | 5 | 13 |

## Error categories across all 75 rows

| Category | Count |
|---|---:|
| CONTEXT | 18 |
| NOT CHECKABLE | 2 |
| NUMBER | 3 |
| OMISSION | 3 |
| TASK/FORMAT | 16 |

## Interactive coverage table

| Dataset | Example | Variant | Error count | Categories |
|---|---|---|---:|---|
| `dart` | `dart-test-204` | `task_aware_direct_flash` | 0 | None |
| `dart` | `dart-test-217` | `task_aware_direct_flash` | 0 | None |
| `dart` | `dart-test-244` | `task_aware_direct_flash` | 0 | None |
| `dart` | `dart-test-260` | `task_aware_direct_flash` | 0 | None |
| `dart` | `dart-test-53` | `task_aware_direct_flash` | 0 | None |
| `e2e_nlg` | `e2e_nlg-test-178` | `task_aware_direct_flash` | 0 | None |
| `e2e_nlg` | `e2e_nlg-test-51` | `task_aware_direct_flash` | 0 | None |
| `e2e_nlg` | `e2e_nlg-test-54` | `task_aware_direct_flash` | 0 | None |
| `e2e_nlg` | `e2e_nlg-test-61` | `task_aware_direct_flash` | 0 | None |
| `e2e_nlg` | `e2e_nlg-test-65` | `task_aware_direct_flash` | 0 | None |
| `sportsett_basketball` | `4934` | `task_aware_direct_flash` | 0 | None |
| `sportsett_basketball` | `4972` | `task_aware_direct_flash` | 2 | CONTEXT, CONTEXT |
| `sportsett_basketball` | `4975` | `full_system` | 2 | CONTEXT, TASK/FORMAT |
| `sportsett_basketball` | `4975` | `task_aware_direct_flash` | 4 | CONTEXT, CONTEXT, NUMBER, CONTEXT |
| `sportsett_basketball` | `4982` | `task_aware_direct_flash` | 5 | NOT CHECKABLE, CONTEXT, CONTEXT, CONTEXT, CONTEXT |
| `sportsett_basketball` | `4986` | `task_aware_direct_flash` | 1 | NOT CHECKABLE |
| `totto` | `totto-validation-204` | `task_aware_direct_flash` | 0 | None |
| `totto` | `totto-validation-217` | `task_aware_direct_flash` | 0 | None |
| `totto` | `totto-validation-244` | `task_aware_direct_flash` | 1 | TASK/FORMAT |
| `totto` | `totto-validation-260` | `task_aware_direct_flash` | 0 | None |
| `totto` | `totto-validation-712` | `task_aware_direct_flash` | 0 | None |
| `web_nlg` | `web_nlg_en-test-178` | `task_aware_direct_flash` | 0 | None |
| `web_nlg` | `web_nlg_en-test-51` | `task_aware_direct_flash` | 0 | None |
| `web_nlg` | `web_nlg_en-test-54` | `task_aware_direct_flash` | 0 | None |
| `web_nlg` | `web_nlg_en-test-61` | `task_aware_direct_flash` | 0 | None |
| `web_nlg` | `web_nlg_en-test-65` | `task_aware_direct_flash` | 0 | None |

## Interactive annotations

Rows not listed below were reviewed and assigned an empty error list.

### `sportsett_basketball` / `4972` / `task_aware_direct_flash`

1. **CONTEXT**: “but the Bucks could not overcome poor outside shooting.”
   - The source supports Milwaukee's 10-for-44 three-point shooting, but a box score alone does not establish that this was a causal barrier that produced the loss.
2. **CONTEXT**: “then answered every Milwaukee push in the second half.”
   - The source provides quarter totals but no play-by-play sequence, so it cannot verify every Milwaukee push or a corresponding Phoenix response.

### `sportsett_basketball` / `4975` / `task_aware_direct_flash`

1. **CONTEXT**: “while forcing 20 Pistons turnovers.”
   - The source records 20 Detroit turnovers and 13 Milwaukee steals, but does not state that Milwaukee forced every turnover.
2. **CONTEXT**: “but could not overcome its shooting struggles and turnovers.”
   - The box score supports the shooting and turnover figures, but it does not establish them as the causal explanation for Detroit's defeat.
3. **NUMBER**: “as only Griffin and Jackson scored in double figures”
   - Andre Drummond also scored in double figures with exactly 10 points, so Griffin and Jackson were not the only Detroit players to do so.
4. **CONTEXT**: “Detroit’s miscues proved costly against a Bucks team that converted those turnovers into scoring chances.”
   - The source contains turnover totals but no points-off-turnovers or possession-level evidence showing that Milwaukee converted those turnovers into scoring chances or that they proved causal.

### `sportsett_basketball` / `4982` / `task_aware_direct_flash`

1. **NOT CHECKABLE**: “Friday night”
   - The source supplies the date and weekday but no start time or time-of-day information.
2. **CONTEXT**: “The Bucks led from the opening tip, building a 43-14 edge after the first quarter and never looking back.”
   - Quarter-end scores support the 43-14 first-quarter margin, but the source has no play-by-play evidence for the opening tip or for a continuous lead throughout the game.
3. **CONTEXT**: “DeAndre' Bembry led all scorers with 19 points”
   - Bembry tied for the game-high 19 points with Milwaukee's Khris Middleton and Malcolm Brogdon rather than leading alone.
4. **CONTEXT**: “Atlanta struggled against Milwaukee's pressure”
   - The source records 21 Atlanta turnovers but does not identify Milwaukee pressure as their cause.
5. **CONTEXT**: “helping Milwaukee maintain its large lead throughout the second half.”
   - The source does not attribute lead maintenance to those bench performances, and quarter-end totals do not establish the continuous game state throughout the half.

### `sportsett_basketball` / `4986` / `task_aware_direct_flash`

1. **NOT CHECKABLE**: “Monday night”
   - The source supplies the date and weekday but no start time or time-of-day information.

### `totto` / `totto-validation-244` / `task_aware_direct_flash`

1. **TASK/FORMAT**: “represented Everett (39th Middlesex), and retired to run for State Treasurer.”
   - The city/district and electoral-history details come from unhighlighted cells. The request required exactly one sentence about the highlighted cells and explicitly excluded unrelated cells.

### `sportsett_basketball` / `4975` / `full_system`

1. **CONTEXT**: “Participant context records Milwaukee Bucks entered with 16 wins and 7 losses; Detroit Pistons entered with 13 wins and 9 losses.”
   - Those records each total the listed game number and therefore include this result. Milwaukee improved to 16-7 and Detroit fell to 13-9; they did not enter with those records.
2. **TASK/FORMAT**: “The entire generated output is a sequence of evidence-ledger statements and rankings rather than a coherent multi-paragraph game report.”
   - The request required a coherent game report that leads with the result and selects the most important performances and contrasts. The output is a mechanical inventory with repeated result statements and no paragraph-level narrative organization.

## Interpretation boundary

The combined file is convenient for descriptive analysis, but it contains mixed execution provenance: 49 API-authenticated annotations and 26 interactive annotations. Any dissertation table using all 75 rows should disclose this split. Confirmatory claims about GPT-5.6 Sol as an API judge should use the 49 API-authenticated rows unless the remaining cases are later rerun through the same controlled API procedure.

## Artifacts

- `evaluation/task_aware_direct_baseline/results/task_aware_direct_flash_25_interactive_gpt56_annotations.jsonl`
- `evaluation/task_aware_direct_baseline/results/canonical_gap_interactive_gpt56_annotation.jsonl`
- `evaluation/task_aware_direct_baseline/results/gpt56_all_75_annotations_with_provenance.jsonl`
- `evaluation/task_aware_direct_baseline/results/gpt56_all_75_annotation_summary.csv`
- `evaluation/task_aware_direct_baseline/results/interactive_gpt56_annotation_provenance.json`
