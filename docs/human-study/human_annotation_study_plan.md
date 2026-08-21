# Human Participation and Annotation Study Plan

## Purpose

The human study should answer a question that automatic metrics cannot fully resolve:

> When people inspect the source data, references and generated outputs, which system output is more factual, complete, task-appropriate and useful?

The study should not simply ask volunteers which output "sounds better." The system is designed to produce evidence-grounded data-to-text reports, so human annotation should focus on:

- factual correctness;
- support from the supplied source;
- important content coverage;
- task or genre fulfilment;
- readability and narrative quality;
- appropriate level of detail;
- overall usefulness.

The outputs must be blinded. Annotators should see `Output A` and `Output B`, not system names.

## Best Selection Strategy

Use a two-layer design.

### Layer 1: Representative Main Evaluation

Use all 25 examples from the current five-dataset evaluation:

- 5 SportSett Basketball examples;
- 5 E2E NLG examples;
- 5 ToTTo examples;
- 5 WebNLG examples;
- 5 DART examples.

For each example, compare:

```text
full_system vs raw_generic_flash
```

This is the cleanest primary study because it avoids cherry-picking. It supports dataset-level and overall conclusions.

Recommended minimum:

```text
25 output pairs × 3 annotators = 75 pair judgements
```

If volunteer time is limited:

```text
15 output pairs × 3 annotators = 45 pair judgements
```

The 15-pair version should still be stratified by dataset.

### Layer 2: Diagnostic Challenge Set

Add a smaller set of deliberately chosen cases to explain *why* outputs succeed or fail. These are not the main average result; they are qualitative evidence for the dissertation story.

The challenge set should include:

| Case type | Why include it | Example candidates |
| --- | --- | --- |
| Clear workflow wins | Shows the value of task understanding and evidence-led content selection. | ToTTo `217`, ToTTo `244`, ToTTo `204`, WebNLG `61`, SportSett `4972` |
| Hard ties | Shows where a raw LLM is already strong and the workflow has less room to improve. | E2E `65`, E2E `178`, DART `244` |
| Raw baseline wins or near-wins | Prevents the study from looking biased. It also shows limits of the current system. | DART `260`, E2E `51`, SportSett `4975` |
| Long-form event reports | Tests narrative quality, coverage and whether the report feels like an event report rather than a data dump. | SportSett `4934`, `4972`, `4986` |
| Focused table failures | Tests whether the system describes highlighted/focused table content instead of summarising the whole table. | ToTTo `217`, `244`, `260` |

This gives a balanced story:

- the workflow wins where structure and focus matter;
- raw LLMs can be competitive on simple verbalisation;
- metrics sometimes disagree with human judgement;
- the workflow's main value is not just fluency, but grounded selection and task control.

## How To Select Good and Bad Outputs

Do not manufacture bad outputs unless you are creating a separate calibration task. Use naturally generated outputs from saved runs.

### Internally Label Output Quality

The labels below are for experiment design only. Annotators should never see them.

#### A good output

Select as a "good" output when most of these hold:

- no generation error;
- no empty output;
- no obvious unsupported claim on eye inspection;
- high or acceptable BERTScore F1;
- strong chrF or METEOR relative to the comparison output;
- good task fit;
- for workflow outputs, strong native sentence support;
- includes important content without bloating.

#### A bad output

Select as a "bad" output when one or more of these hold:

- wrong entity, number, winner, highlighted-cell subject or relation;
- broad generic summary when the task asks for a focused proposition;
- missing the main result or central fact;
- unsupported information not present in the source;
- wrong genre, such as dataset analysis instead of event report;
- very low chrF/METEOR/BERTScore against reference;
- very high TER;
- empty output or operational failure.

Use empty outputs and operational failures only in an expert diagnostic appendix, not the main volunteer comparison, unless the aim is to measure reliability.

### Avoid Cherry-Picking

The main evaluation should be selected before reading the final outputs whenever possible. For the current project, the safest framing is:

```text
Primary study:
    all 25 examples from the five-dataset run

Diagnostic study:
    stratified examples selected by metric disagreement and observed failure type
```

The diagnostic set can be "clever"; the main set should be representative.

## Recommended Annotation Interface

For each task, show:

1. Dataset name.
2. Example ID.
3. Requested task.
4. Structured input data.
5. Human reference output.
6. Output A.
7. Output B.

Randomise whether the workflow or raw baseline appears as Output A.

Do not show:

- metric scores;
- system names;
- run IDs;
- audit decisions;
- which output is expected to be better.

## Mandatory Annotation Questions

### 1. Factual Correctness

Which output is more factually correct according to the supplied source data?

- Output A
- Output B
- Tie
- Cannot tell

### 2. Source Support

Which output is better supported by the supplied source data?

- Output A
- Output B
- Tie
- Cannot tell

### 3. Important Content Coverage

Which output includes more of the important information needed for the task?

- Output A
- Output B
- Tie
- Cannot tell

### 4. Task or Genre Fit

Which output better matches the requested task?

Examples:

- a game report should read like a game report;
- a highlighted-table description should focus on highlighted/focused cells;
- an attribute verbalisation should express the supplied attributes;
- a triple verbalisation should express the supplied triples.

Options:

- Output A
- Output B
- Tie
- Cannot tell

### 5. Appropriate Detail

Which output has the better level of detail?

- Output A
- Output B
- Tie
- Cannot tell

### 6. Fluency and Readability

Which output is easier to read and more naturally written?

- Output A
- Output B
- Tie
- Cannot tell

### 7. Narrative or Explanation Quality

Which output better relates facts into a coherent answer rather than listing isolated facts?

- Output A
- Output B
- Tie
- Cannot tell

This question is especially important for SportSett and other event-report tasks.

### 8. Overall Preference

Overall, which output would you prefer to use?

- Output A
- Output B
- Tie
- Cannot tell

### 9. Error Tags for Output A

Select all that apply.

- No obvious problem
- Wrong number
- Wrong entity, person, team, place or subject
- Unsupported claim not present in the source
- Missing the main fact or result
- Missing important supporting information
- Includes irrelevant information
- Too generic
- Too short
- Too verbose
- Poor narrative flow
- Wrong task style or genre
- Overstates causation or explanation
- Uses awkward wording
- Hard to understand
- Other

### 10. Error Tags for Output B

Use the same list as Question 9.

### 11. Main Reason for Preference

In one or two sentences, explain the main reason for your overall preference.

Free text.

## Dataset-Specific Questions

Show only the relevant dataset-specific question for the current example.

### SportSett Basketball / Event Reports

Does the output clearly describe the event result and key performances without turning the task into generic dataset analysis?

- Yes
- Partly
- No
- Not applicable

Does the output avoid unsupported claims about causation, momentum or chronology?

- Yes
- Partly
- No
- Not applicable

### ToTTo / Highlighted Table Description

Does the output focus on the highlighted cell or focused table region?

- Yes
- Partly
- No
- Not applicable

Does the output attach the highlighted value to the correct subject/entity?

- Yes
- Partly
- No
- Not applicable

### E2E NLG / Attribute Verbalisation

Does the output express all supplied attributes?

- Yes
- Partly
- No
- Not applicable

Does the output avoid adding unsupported attributes?

- Yes
- Partly
- No
- Not applicable

### WebNLG and DART / Triple Verbalisation

Does the output preserve the supplied subject-relation-object facts?

- Yes
- Partly
- No
- Not applicable

Does the output preserve important names, numbers, units and identifiers?

- Yes
- Partly
- No
- Not applicable

## Optional Expert Annotation Tasks

Use these for a smaller expert group, not for every volunteer.

### Unsupported Span Marking

Ask the expert to highlight any phrase in the output that is not supported by the source.

### Missing Content Marking

Ask the expert to list up to three important source facts that the output should have included.

### Minimal Edit Task

Ask the expert:

> What is the smallest edit needed to make this output acceptable?

This is useful for understanding whether failures are minor wording problems or deeper content-selection problems.

### Error Severity

For each tagged error, assign:

- Minor: does not change the main meaning;
- Major: affects an important claim;
- Critical: makes the output misleading or unusable.

## Recommended Study Design

### Volunteer Study

Use pairwise comparison. It is faster and easier than asking volunteers to assign absolute scores.

Recommended:

```text
10 to 12 pairs per volunteer
3 annotators per pair
15 to 20 minutes per volunteer
```

If possible:

```text
25 pairs × 3 annotators = 75 annotations
```

### Expert Review

Use fewer examples but ask deeper questions.

Recommended:

```text
8 to 12 diagnostic pairs
2 expert reviewers
unsupported-span and missing-content tasks enabled
```

## Suggested Diagnostic Pair List

Use these pairs in addition to the 25-example representative evaluation if time allows.

| Dataset | Example | Why it is useful |
| --- | --- | --- |
| ToTTo | `totto-validation-217` | Strong workflow advantage; tests focused table interpretation. |
| ToTTo | `totto-validation-244` | Raw-generic produced a broad table summary; tests whether humans notice task mismatch. |
| ToTTo | `totto-validation-204` | Tests correct highlighted value subject and focused proposition. |
| SportSett | `4972` | Strong event-report case; tests result, key performances and narrative quality. |
| SportSett | `4934` | Good known basketball report; useful dissertation example. |
| WebNLG | `web_nlg_en-test-61` | Strong workflow advantage in triple verbalisation. |
| WebNLG | `web_nlg_en-test-51` | Good concise triple verbalisation example. |
| DART | `dart-test-204` | Strong workflow advantage. |
| E2E | `e2e_nlg-test-65` | Hard tie; tests whether both systems are acceptable. |
| E2E | `e2e_nlg-test-178` | Hard tie; useful control case. |
| DART | `dart-test-260` | Raw-generic appears stronger by metrics; prevents biased selection. |
| SportSett | `4975` | Near raw-generic advantage; useful counterexample. |

## How To Report Human Results

Report:

1. Overall preference rate for the workflow.
2. Preference rate by dataset.
3. Factual correctness preference rate.
4. Coverage preference rate.
5. Task-fit preference rate.
6. Narrative-quality preference rate.
7. Error-tag frequency by system.
8. Inter-annotator agreement.
9. A short qualitative summary of recurring comments.

Recommended agreement measures:

- simple percent agreement for pairwise choices;
- Cohen's kappa if each pair has two annotators;
- Fleiss' kappa if each pair has three or more annotators.

## Best Dissertation Framing

The human study should not claim that the workflow is always more fluent than a raw LLM. The better claim is:

> The workflow is designed to improve grounded content selection, task fulfilment and traceable factuality. Human annotation tests whether those design goals are visible to readers, especially in cases where automatic overlap metrics are incomplete or misleading.

This framing is defensible because the current results show:

- the workflow is strongest on focused table interpretation and structured triple tasks;
- raw-generic is competitive on simple short verbalisation tasks;
- event-report quality requires human judgement because references include narrative details and automatic metrics can reward brevity or penalise grounded omissions;
- native support evidence is central to the workflow but unavailable for raw baselines.

