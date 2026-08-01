# Evaluation Overview: SportSett Basketball Example 4934

Created: 2026-07-31
Updated: 2026-08-01 with the latest full-system run. Raw baseline metrics are unchanged.

This document summarises one SportSett Basketball evaluation example by placing the generated report, the human reference, the structured source data, and the available metric results in one reviewable packet.

## 1. Evaluation Context

| Field | Value |
| --- | --- |
| Dataset | `sportsett_basketball` |
| Example ID | `4934` |
| Variant | `full_system` |
| Generation ID | `sportsett_basketball__4934__full_system__r0__s42` |
| Run ID | `20260801T115628Z_48b57739d3` |
| Task family | `event_report` |
| Output mode | `multi_paragraph_report` |
| Writer mode | `llm_writer` |
| Release status | `approved` |
| Primary evaluation eligible | `true` |
| Audit support rate | `1.0` |
| Supported sentences | `10 / 10` |
| Repair rounds used | `0` |
| Runtime | `1235.75` seconds |

Request supplied to the system:

```text
Write a coherent game report from the supplied structured game data. Lead with the result, select the most important performances and contrasts, and do not invent information.
```

## 2. Evaluation Setup

The evaluation is split into two complementary views.

| Evaluation view | Candidate text | Support/comparison text | Main question |
| --- | --- | --- | --- |
| Source-grounded factuality | Full-system report, raw DeepSeek baseline, and human references | Full structured source text | Is each text supported by the provided data? |
| Reference similarity | Full-system report and raw DeepSeek baseline | Human references | Which system better matches the reference wording and content selection? |

This split matters because a generated report can be factually supported by the source while still differing from the reference. Conversely, a reference can contain narrative details that are natural for a game recap but absent from the structured source currently provided to the evaluator.

## 3. Structured Source Data

### 3.1 Game Metadata

| Field | Value |
| --- | --- |
| Game ID | `4934` |
| Date | Sunday, December 2, 2018 |
| Season | `2018` |
| Venue | Wells Fargo Center |
| City | Philadelphia |
| State | Pennsylvania |
| Attendance | `20,300` |
| Capacity | `20,500` |

### 3.2 Team Context

| Side | Team | Place | Conference | Conference standing | Record entering/listed in source | Game number | Next game |
| --- | --- | --- | --- | ---: | --- | ---: | --- |
| Home | 76ers | Philadelphia | Eastern Conference | 3 | 17-8 | 25 | At Toronto Raptors, Wednesday December 5, 2018, Scotiabank Arena |
| Visitor | Grizzlies | Memphis | Western Conference | 6 | 13-9 | 22 | Home vs Los Angeles Clippers, Wednesday December 5, 2018, FedExForum |

### 3.3 Score By Period

| Team | Q1 | Q2 | Q3 | Q4 | OT | Final |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 76ers | 26 | 28 | 24 | 25 | 0 | 103 |
| Grizzlies | 25 | 19 | 24 | 27 | 0 | 95 |

### 3.4 Cumulative Score Progression

| Point in game | 76ers | Grizzlies | Leader |
| --- | ---: | ---: | --- |
| End Q1 | 26 | 25 | 76ers by 1 |
| Halftime | 54 | 44 | 76ers by 10 |
| End Q3 | 78 | 68 | 76ers by 10 |
| Final | 103 | 95 | 76ers by 8 |

### 3.5 Team Totals

| Metric | 76ers | Grizzlies |
| --- | ---: | ---: |
| Points | 103 | 95 |
| Field goals | 36-74 | 33-79 |
| Field-goal percentage | 49 | 42 |
| Three-pointers | 8-22 | 11-28 |
| Three-point percentage | 36 | 39 |
| Free throws | 23-30 | 18-23 |
| Free-throw percentage | 77 | 78 |
| Offensive rebounds | 3 | 3 |
| Defensive rebounds | 41 | 32 |
| Total rebounds | 44 | 35 |
| Assists | 22 | 19 |
| Steals | 5 | 7 |
| Blocks | 2 | 7 |
| Turnovers | 16 | 14 |
| Personal fouls | 20 | 24 |

### 3.6 76ers Player Box Score

Zero-minute players are omitted from this table.

| Player | Starter | MIN | PTS | REB | AST | STL | BLK | FG | 3P | FT | +/- | Double |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |
| Joel Embiid | True | 37 | 15 | 14 | 3 | 1 | 1 | 4-13 | 0-2 | 7-8 | 13 | double |
| Ben Simmons | True | 37 | 19 | 12 | 6 | 2 | 0 | 8-10 | 0-0 | 3-8 | 5 | double |
| Jimmy Butler | True | 32 | 21 | 3 | 2 | 0 | 1 | 7-17 | 0-4 | 7-8 | 7 | none |
| J.J. Redick | True | 30 | 24 | 3 | 0 | 0 | 0 | 9-17 | 3-6 | 3-3 | 9 | none |
| Mike Muscala | True | 27 | 8 | 7 | 5 | 0 | 0 | 2-4 | 2-3 | 2-2 | -5 | none |
| T.J. McConnell | False | 31 | 6 | 3 | 3 | 0 | 0 | 3-4 | 0-0 | 0-0 | 16 | none |
| Landry Shamet | False | 17 | 4 | 0 | 0 | 0 | 0 | 1-4 | 1-4 | 1-1 | -1 | none |
| Furkan Korkmaz | False | 15 | 6 | 1 | 2 | 2 | 0 | 2-4 | 2-3 | 0-0 | 1 | none |
| Amir Johnson | False | 10 | 0 | 1 | 1 | 0 | 0 | 0-1 | 0-0 | 0-0 | -5 | none |

Omitted zero-minute 76ers players: Demetrius Jackson, Shake Milton.

### 3.7 Grizzlies Player Box Score

Zero-minute players are omitted from this table.

| Player | Starter | MIN | PTS | REB | AST | STL | BLK | FG | 3P | FT | +/- | Double |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |
| Marc Gasol | True | 38 | 12 | 4 | 3 | 1 | 2 | 4-14 | 2-5 | 2-3 | -12 | none |
| Mike Conley | True | 33 | 21 | 2 | 5 | 1 | 1 | 6-17 | 3-6 | 6-7 | -7 | none |
| Garrett Temple | True | 31 | 12 | 4 | 1 | 0 | 0 | 4-9 | 3-6 | 1-2 | -9 | none |
| Kyle Anderson | True | 27 | 5 | 3 | 5 | 0 | 1 | 2-2 | 0-0 | 1-1 | -6 | none |
| Jaren Jackson | True | 23 | 17 | 3 | 0 | 1 | 3 | 5-10 | 1-4 | 6-6 | -6 | none |
| JaMychal Green | False | 25 | 14 | 7 | 0 | 4 | 0 | 6-10 | 2-4 | 0-2 | 6 | none |
| MarShon Brooks | False | 20 | 12 | 2 | 0 | 0 | 0 | 5-10 | 0-0 | 2-2 | 4 | none |
| Shelvin Mack | False | 20 | 2 | 1 | 4 | 0 | 0 | 1-5 | 0-2 | 0-0 | -13 | none |
| Omri Casspi | False | 14 | 0 | 8 | 0 | 0 | 0 | 0-2 | 0-1 | 0-0 | 2 | none |
| Ivan Rabb | False | 4 | 0 | 1 | 1 | 0 | 0 | 0-0 | 0-0 | 0-0 | 1 | none |

Omitted zero-minute Grizzlies players: Jevon Carter, Wayne Selden, D.J. Stephens.

---

## 4. Primary Human Reference

#### Result And Venue

The Philadelphia 76ers defeated the visiting Memphis Grizzlies, 103 - 95, at Wells Fargo Center on Sunday evening.

#### Game Flow

The Sixers got out to a quick, 10 - 3, lead but the Grizzlies stuck with it, leading to a, 26 - 25, advantage for the home team, after one quarter.

The 76ers stayed on top in the second, where they outscored the Grizzlies, 28 - 19, to take a, 54 - 44, lead by halftime.

Things tightened up again in the second half, as both teams matched each other for 24 points in the third quarter, leaving the Sixers ahead by 10 heading into the fourth.

The Grizzlies started the fourth quarter with a quick 9 - 1 run, to make it a two - point game.

However, the 76ers answered right back, pushing their lead back to nine, with five minutes left.

The Grizzlies cut it as close as a four - point deficit, but could not do better than that, as the 76ers held on to earn their fourth straight win.

#### Player Performances

J.J. Redick led Philly with 24 points on 9 - of - 17 shooting, in 30 minutes.

Jimmy Butler tallied 21 points, three rebounds, two assists and a block.

Ben Simmons finished with 19 points, 12 rebounds, six assists and two steals, while Joel Embiid added 15 points, 14 rebounds, three assists, one steal and one block.

Meanwhile, Mike Conley led the Grizzlies with 21 points, five assists, two rebounds, one steal and one block.

Jaren Jackson Jr. followed up with 17 points, three rebounds, three blocks and a steal, while JaMychal Green tallied 14 points, seven rebounds and four steals.

#### Next Games

The Grizzlies (13 - 9) will look to bounce back as they play host to the Clippers on Tuesday.

The 76ers (17 - 8) take on the Raptors in Toronto on Wednesday.

A second reference is present in the dataset and is effectively a tokenized version of the same report.

---

## 5. Generated Report

#### Generated Title

Philadelphia 76ers Defeat Memphis Grizzlies 103-95

#### Event Overview

On Sunday, December 2, 2018, the Philadelphia 76ers defeated the Memphis Grizzlies 103-95 at Wells Fargo Center, holding the lead after each quarter.

The 76ers arrived at 17-8 and the Grizzlies at 13-9; the supplied record lists Philadelphia third and Memphis sixth in conference standing, with the game as the two teams' 25th and 22nd games of the season respectively.

#### Score Progression

Quarter by quarter, Philadelphia led 26-25 after the first, 54-44 after the second, 78-68 after the third and 103-95 at the end.

The teams each scored 24 in the third quarter, while Memphis outscored Philadelphia 27-25 in the fourth.

#### Key Performances

J.J. Redick led all scorers with 24 points, while Jimmy Butler and Mike Conley tied at 21 and Ben Simmons added 19.

Joel Embiid recorded a game-high 14 rebounds and Ben Simmons added 12, while the 76ers finished with a 44-35 team rebounding advantage over the Grizzlies.

Ben Simmons also dished out a game-high six assists, with Mike Muscala, Mike Conley and Kyle Anderson each recording five.

On the defensive end, Memphis's Jaren Jackson had a game-high three blocks and JaMychal Green recorded four steals, while T.J. McConnell posted the best plus/minus of the game at +16.

#### Participant Contrasts

Across the supplied team statistics, Philadelphia held the edge in total rebounds (44-35), defensive rebounds (41-32), assists (22-19), field goals made (36-33), free throws made (23-18) and free-throw attempts (30-23), while Memphis attempted more field goals (79-74) and three-pointers (28-22) and made more three-pointers (11-8); offensive rebounds were tied at 3.

#### Scope Limitations

These comparisons are limited to the supplied game record and describe only this event; they do not establish why the result occurred and do not support claims about broader performance.

---

## 6. Raw DeepSeek Flash Baseline Report

This baseline sends the benchmark request and structured source text directly to DeepSeek Flash. It bypasses the project pipeline, including input interpretation, evidence extraction, fact verification, insight synthesis, writer support maps and final audit. The stored variant tag is still `raw_deepseek_v4_pro`, but the run metadata confirms that the model used for this run was `deepseek-v4-flash`.

| Field | Value |
| --- | --- |
| Variant | `raw_deepseek_v4_pro` |
| Backend | `callable` |
| Model | `deepseek-v4-flash` |
| Prompt tokens | `8328` |
| Completion tokens | `2941` |
| Total tokens | `11269` |
| Runtime | `32.36` seconds |
| Max output tokens | `3000` |
| Temperature | `0.2` |

#### Raw Baseline Text

J.J. Redick scored a game-high 24 points, and Ben Simmons and Joel Embiid each posted double-doubles as the Philadelphia 76ers defeated the Memphis Grizzlies 103-95 on Sunday, December 2, 2018, at Wells Fargo Center. Philadelphia improved to 17-8 with the win, while Memphis fell to 13-9.

Redick led the 76ers with efficient shooting, going 9-of-17 from the field and 3-of-6 from three-point range. Jimmy Butler added 21 points, Ben Simmons finished with 19 points, 12 rebounds, and 6 assists, and Joel Embiid contributed 15 points and 14 rebounds. Philadelphia built a 54-44 halftime lead and maintained control despite being outscored 27-25 in the fourth quarter.

Memphis was led by Mike Conley's 21 points and 5 assists, though he shot 6-of-17 from the field. Jaren Jackson Jr. added 17 points and 3 blocks, while JaMychal Green scored 14 points off the bench. Marc Gasol chipped in 12 points for the Grizzlies.

Philadelphia shot 49 percent from the field and held a 44-35 rebounding advantage. The 76ers also made 23 of 30 free throws, while Memphis hit 11 three-pointers to Philadelphia's eight but could not overcome the 76ers' balanced all-around performance in front of 20,300 at Wells Fargo Center.

---

## 7. Metric Results

### 7.1 Source-Grounded Local Factuality Metrics

These metrics score each candidate text against the structured source, not against the human reference.

| Candidate | HHEM mean support | HHEM min sentence support | HHEM unsupported sentence rate | AlignScore base |
| --- | ---: | ---: | ---: | ---: |
| Full-system report | 0.1686 | 0.0070 | 0.9167 | 0.2263 |
| Raw DeepSeek Flash baseline | 0.0122 | 0.0037 | 1.0000 | 0.2696 |
| Human reference 1 | 0.0101 | 0.0048 | 1.0000 | 0.2121 |
| Human reference 2 | 0.0101 | 0.0045 | 1.0000 | 0.1857 |

Interpretation: HHEM support improved substantially for the latest full-system run, and the unsupported sentence rate decreased from the earlier full-system score. AlignScore remains lower than the raw Flash baseline. The absolute values still show that these local factuality tools struggle when the support context is raw structured JSON, so they should be treated as diagnostic rather than decisive for this dataset until the source is transformed into cleaner sentence-like evidence.

### 7.2 Source-Grounded DeepEval Metrics

These metrics score each candidate text against the structured source using a DeepSeek V4-Pro judge with one repetition.

| Candidate | Faithfulness | Factual correctness | Task relevance | Coherence | Usefulness | Reference adequacy | Summarization |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full-system report | 0.9512 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4000 | 0.0714 |
| Raw DeepSeek Flash baseline | 1.0000 | 1.0000 | 0.8000 | 1.0000 | 0.7000 | Not run | Not run |

Interpretation: DeepEval judged both outputs as factually correct in the available metric files. The latest full-system run is now scored successfully on faithfulness and is rated higher than the raw Flash baseline on task relevance and usefulness, while the raw baseline retains a slightly higher faithfulness score. Reference adequacy remains moderate for the full-system report, which matches the observation that the system is controlled and factual but still less human-reference-like in narrative selection.

### 7.3 Reference-Similarity Metrics

These metrics compare each system output with the available human references.

| Metric | Higher is better? | Full-system report | Raw DeepSeek Flash baseline | Reading |
| --- | --- | ---: | ---: | --- |
| BLEU | Yes | 0.1081 | 0.1173 | Raw baseline remains slightly higher on exact n-gram overlap. |
| chrF | Yes | 0.4070 | 0.3743 | Full-system report remains closer at character level. |
| TER | No | 0.8589 | 0.8288 | Raw baseline still requires slightly fewer edits, but the gap is much smaller than before. |
| ROUGE-1 | Yes | 0.4513 | 0.4844 | Raw baseline overlaps more on unigram content. |
| ROUGE-2 | Yes | 0.1629 | 0.2157 | Raw baseline overlaps more on phrase-level content. |
| ROUGE-L | Yes | 0.2338 | 0.2656 | Raw baseline is still closer in sequence structure. |
| ROUGE-Lsum | Yes | 0.2338 | 0.2656 | Raw baseline is still closer in summary sequence structure. |
| METEOR | Yes | 0.2453 | 0.2443 | Full-system report is now effectively tied with the raw baseline. |
| BERTScore F1 | Yes | 0.8452 | 0.8475 | Both are semantically related to the reference; raw baseline is only slightly higher. |
| PARENT precision | Yes | Skipped | Skipped | No PARENT-compatible table was available from the adapter for this record. |
| PARENT recall | Yes | Skipped | Skipped | No PARENT-compatible table was available from the adapter for this record. |
| PARENT F1 | Yes | Skipped | Skipped | No PARENT-compatible table was available from the adapter for this record. |

Interpretation: the latest full-system report improved over the previous full-system run on BLEU, TER, ROUGE-2 and ROUGE-L, while METEOR decreased. The raw Flash baseline remains more reference-like on most sequence and phrase-overlap metrics, but the latest system narrowed the TER and BLEU gaps while preserving source-controlled generation and auditability.

### 7.4 Operational Comparison

| Variant | Runtime | Words | Output status | Main behaviour |
| --- | ---: | ---: | --- | --- |
| Full-system report | 1235.75s | 299 | `approved` | Slower, source-controlled, audited and more concise than the previous full-system run. |
| Raw DeepSeek Flash baseline | 32.36s | 197 | No pipeline audit | Faster, more compact recap style, but no evidence ledger or factual audit. |
