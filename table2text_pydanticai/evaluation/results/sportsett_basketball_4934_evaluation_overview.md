# Evaluation Overview: SportSett Basketball Example 4934

Created: 2026-07-31

This document summarises one SportSett Basketball evaluation example by placing the generated report, the human reference, the structured source data, and the available metric results in one reviewable packet.

## 1. Evaluation Context

| Field | Value |
| --- | --- |
| Dataset | `sportsett_basketball` |
| Example ID | `4934` |
| Variant | `full_system` |
| Generation ID | `sportsett_basketball__4934__full_system__r0__s42` |
| Run ID | `20260731T112346Z_48b57739d3` |
| Task family | `event_report` |
| Output mode | `multi_paragraph_report` |
| Writer mode | `llm_writer` |
| Release status | `approved_with_warnings` |
| Primary evaluation eligible | `true` |
| Audit support rate | `1.0` |
| Supported sentences | `18 / 18` |
| Repair rounds used | `0` |
| Runtime | `1352.93` seconds |

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

76ers Defeat Grizzlies 103-95 as Redick Scores 24

#### Event Overview

The Philadelphia 76ers defeated the Memphis Grizzlies 103-95 at Wells Fargo Center on Sunday, December 2, 2018.

Philadelphia entered the game with a 17-8 record in third place in its conference, while Memphis arrived at 13-9 in sixth place; it was the 25th game of the season for the 76ers and the 22nd for the Grizzlies.

#### Score Progression

The 76ers led after every quarter, from 26-25 after the first, to 54-44 at halftime, to 78-68 after the third, before finishing 103-95; Memphis outscored Philadelphia 27-25 in the fourth quarter, but the 76ers preserved the lead.

Philadelphia's largest quarter margin came in the second, where it outscored Memphis 28-19, while the third quarter was even at 24-24.

The recorded final totals of 103 and 95 match the cumulative scores through the four quarters.

#### Key Performances

J.J. Redick led all scorers with 24 points and tied for the game high with three three-pointers made on six attempts.

Jimmy Butler and Memphis's Mike Conley tied for second with 21 points apiece, and Ben Simmons added 19.

Joel Embiid contributed 15 points and led all players with 14 total rebounds and 14 defensive rebounds.

Ben Simmons added 12 rebounds and a game-high 6 assists while shooting 80 percent from the field.

Embiid and Butler each converted 7 free throws, the game high, and T.J. McConnell posted the game's best plus/minus at +16.

For Memphis, JaMychal Green recorded a game-high 4 steals and Jaren Jackson blocked a game-high 3 shots.

Mike Muscala and Furkan Korkmaz each shot 67 percent from three-point range, the best marks in the game.

#### Participant Contrasts

Memphis attempted more field goals (79 to 74) and more three-pointers (28 to 22) and made more threes (11 to 8), but Philadelphia made more field goals overall (36 to 33) and more free throws (23 to 18), offsetting that extra volume.

Philadelphia shot 49 percent from the field to Memphis's 42 percent, while Memphis held the edge from three-point range at 39 percent to 36 percent.

The 76ers also controlled the boards, leading total rebounds 44-35 and defensive rebounds 41-32, with offensive rebounds tied at 3-3.

Philadelphia led team assists 22-19, with Ben Simmons contributing a game-high 6, while the 76ers also committed more turnovers than Memphis, 16 to 14.

Memphis, meanwhile, recorded more steals (7-5) and blocks (7-2), while Philadelphia took more free throws (30-23).

#### Scope Limitations

These comparisons describe only the supplied game record: they show how the teams' box-score totals differed, but they do not establish why the 76ers won and do not support claims about broader team performance.

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
| Full-system report | 0.0143 | 0.0049 | 1.0000 | 0.2451 |
| Raw DeepSeek Flash baseline | 0.0122 | 0.0037 | 1.0000 | 0.2696 |
| Human reference 1 | 0.0101 | 0.0048 | 1.0000 | 0.2121 |
| Human reference 2 | 0.0101 | 0.0045 | 1.0000 | 0.1857 |

Interpretation: HHEM and AlignScore are very low for all candidates when the support context is the full structured JSON. The raw Flash baseline scores lower than the full-system report on HHEM mean support but slightly higher on AlignScore. The absolute values show that these local factuality tools are currently struggling with this source representation. They should be treated as diagnostic, not decisive, for this dataset until the structured source is transformed into cleaner sentence-like evidence.

### 7.2 Source-Grounded DeepEval Metrics

These metrics score each candidate text against the structured source using a DeepSeek V4-Pro judge with one repetition. The full-system faithfulness call timed out, so that cell is recorded as an error rather than a score.

| Candidate | Faithfulness | Factual correctness | Task relevance | Coherence | Usefulness |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full-system report | Error | 1.0000 | 0.7000 | 1.0000 | 1.0000 |
| Raw DeepSeek Flash baseline | 1.0000 | 1.0000 | 0.8000 | 1.0000 | 0.7000 |

Interpretation: DeepEval judged both system outputs as factually correct in this pass. It rated the full-system report higher on usefulness and the raw Flash baseline higher on task relevance. The raw baseline was penalised for adding `Jr.` to `Jaren Jackson` and for interpretive phrases such as "balanced all-around performance." The full-system faithfulness metric timed out after repeated retries, so the available DeepEval comparison is incomplete.

### 7.3 Reference-Similarity Metrics

These metrics compare each system output with the available human references.

| Metric | Higher is better? | Full-system report | Raw DeepSeek Flash baseline | Reading |
| --- | --- | ---: | ---: | --- |
| BLEU | Yes | 0.0883 | 0.1173 | Raw baseline has higher exact n-gram overlap. |
| chrF | Yes | 0.4210 | 0.3743 | Full-system report is closer at character level. |
| TER | No | 1.1922 | 0.8288 | Raw baseline requires fewer edits to match the reference. |
| ROUGE-1 | Yes | 0.4517 | 0.4844 | Raw baseline overlaps more on unigram content. |
| ROUGE-2 | Yes | 0.1387 | 0.2157 | Raw baseline overlaps more on phrase-level content. |
| ROUGE-L | Yes | 0.2167 | 0.2656 | Raw baseline is closer in sequence structure. |
| ROUGE-Lsum | Yes | 0.2167 | 0.2656 | Raw baseline is closer in summary sequence structure. |
| METEOR | Yes | 0.2829 | 0.2443 | Full-system report is higher on lexical-semantic alignment. |
| BERTScore F1 | Yes | 0.8466 | 0.8475 | Both are semantically related to the reference; raw baseline is only slightly higher. |
| PARENT precision | Yes | Skipped | Skipped | No PARENT-compatible table was available from the adapter for this record. |
| PARENT recall | Yes | Skipped | Skipped | No PARENT-compatible table was available from the adapter for this record. |
| PARENT F1 | Yes | Skipped | Skipped | No PARENT-compatible table was available from the adapter for this record. |

Interpretation: the raw Flash baseline is closer to the human reference on BLEU, TER, ROUGE and BERTScore, while the full-system report is better on chrF and METEOR. The baseline is therefore more reference-like on sequence and phrase overlap, but the advantage is smaller than it was with the earlier V4-Pro baseline.

### 7.4 Operational Comparison

| Variant | Runtime | Words | Output status | Main behaviour |
| --- | ---: | ---: | --- | --- |
| Full-system report | 1352.93s | 444 | `approved_with_warnings` | Slower, source-controlled, more analytical and support-mapped. |
| Raw DeepSeek Flash baseline | 32.36s | 197 | No pipeline audit | Faster, more compact recap style, but no evidence ledger or factual audit. |

