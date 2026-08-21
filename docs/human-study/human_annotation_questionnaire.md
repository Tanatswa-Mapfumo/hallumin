# Human Evaluation Questionnaire

## Title

Human Evaluation of Structured Data-to-Text Outputs

## Purpose

This questionnaire is designed to compare two anonymous generated outputs for the same structured-data input. The task is to judge which output is more accurate, useful, complete, and appropriate for the requested report type.

The outputs may come from:

- the proposed workflow system;
- a raw LLM baseline;
- another system variant.

Annotators should not be told which system produced which output.

## Annotator Instructions

You will be shown:

- the structured input data;
- the user/requested task;
- one or more human reference outputs;
- Output A;
- Output B.

Judge the outputs only using the supplied input data and reference output. Do not use outside knowledge.

Focus on whether each output:

- is factually supported by the input;
- includes the important information;
- avoids unsupported or invented claims;
- matches the requested task;
- is fluent and easy to read.

## Example Display Template

### Dataset

`[dataset_id]`

### Example ID

`[example_id]`

### Requested Task

```text
[request]
```

### Structured Input Data

```text
[structured_input]
```

### Human Reference Output

```text
[reference_output]
```

### Output A

```text
[output_a]
```

### Output B

```text
[output_b]
```

## Annotation Questions

### 1. Factual Correctness

Which output is more factually correct according to the supplied input data?

- Output A
- Output B
- Tie
- Cannot tell

### 2. Important Content Coverage

Which output includes more of the important information needed for the task?

- Output A
- Output B
- Tie
- Cannot tell

### 3. Task Match

Which output better matches the requested task type?

Examples include one-sentence table description, attribute verbalisation, triple verbalisation, event report, or dataset report.

- Output A
- Output B
- Tie
- Cannot tell

### 4. Fluency and Readability

Which output is more fluent, natural, and easy to read?

- Output A
- Output B
- Tie
- Cannot tell

### 5. Appropriate Detail

Which output has the better level of detail for the task?

- Output A
- Output B
- Tie
- Cannot tell

### 6. Overall Preference

Overall, which output would you prefer to use?

- Output A
- Output B
- Tie
- Cannot tell

### 7. Output A Error Tags

Select all problems that apply to Output A.

- No obvious problem
- Wrong number
- Wrong entity, person, team, or place
- Unsupported fact not present in the input
- Missing important information
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

### 8. Output B Error Tags

Select all problems that apply to Output B.

- No obvious problem
- Wrong number
- Wrong entity, person, team, or place
- Unsupported fact not present in the input
- Missing important information
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

### 9. Dataset-Specific Check

Answer the relevant check for the dataset being shown.

For SportSett or other event reports:

Does the output clearly describe the event result and key performances without turning the task into a generic dataset analysis?

- Yes
- Partly
- No
- Not applicable

For ToTTo highlighted table descriptions:

Does the output describe the highlighted cell or focused table region without relying on unrelated cells?

- Yes
- Partly
- No
- Not applicable

For E2E attribute verbalisation:

Does the output express the supplied attributes without adding unsupported attributes?

- Yes
- Partly
- No
- Not applicable

For WebNLG or DART triple verbalisation:

Does the output express the supplied triples while preserving important numbers, identifiers, and units?

- Yes
- Partly
- No
- Not applicable

### 10. Reason for Preference

In one sentence, what is the main reason for your overall preference?

Free-text answer.

## Optional Scoring Sheet

Use this only if absolute scores are needed in addition to pairwise preference.

Scale:

- 1 = very poor
- 2 = poor
- 3 = acceptable
- 4 = good
- 5 = excellent

| Criterion | Output A Score | Output B Score |
| --- | --- | --- |
| Factual correctness |  |  |
| Coverage of important content |  |  |
| Task relevance |  |  |
| Fluency/readability |  |  |
| Appropriate level of detail |  |  |
| Overall quality |  |  |

## Recommended Use

For volunteer annotators, make Questions 1 to 10 mandatory.

Use the optional scoring sheet only for a smaller expert review or when numerical human ratings are required.

