# Final Human Annotation Questions

## Study Title

Human Evaluation of Evidence-Grounded Data-to-Text Generation

## What The Participant Sees

For each task, the participant sees:

1. Dataset name.
2. Example ID.
3. Requested task.
4. Structured source data.
5. Human reference output.
6. Output A.
7. Output B.

Output A and Output B must be randomly ordered. Do not reveal which output was produced by the workflow system or by the raw LLM baseline.

## Participant Instructions

Please judge the two outputs using only the supplied source data and reference output. Do not use outside knowledge.

The best output should:

- be factually correct;
- be supported by the supplied data;
- include the important information for the task;
- avoid unsupported or invented claims;
- match the requested output type;
- be fluent and easy to read;
- use an appropriate level of detail.

It is fine to choose `Tie` if both outputs are similarly good or similarly poor. Choose `Cannot tell` only when the source data is too unclear for you to make a judgement.

## Required Questions

### Q1. Factual Correctness

Which output is more factually correct according to the supplied source data?

- Output A
- Output B
- Tie
- Cannot tell

### Q2. Source Support

Which output is better supported by the supplied source data?

Choose the output whose claims can be traced more clearly to the input.

- Output A
- Output B
- Tie
- Cannot tell

### Q3. Main Information Coverage

Which output includes more of the important information needed to answer the task?

- Output A
- Output B
- Tie
- Cannot tell

### Q4. Task Fit

Which output better matches the requested task type?

For example, a game report should read like a game report, while a highlighted-table task should focus on the highlighted or focused table content.

- Output A
- Output B
- Tie
- Cannot tell

### Q5. Focus and Relevance

Which output stays more focused on the relevant source information?

- Output A
- Output B
- Tie
- Cannot tell

### Q6. Appropriate Level of Detail

Which output has the better level of detail?

Choose the output that is neither too thin nor unnecessarily bloated for the task.

- Output A
- Output B
- Tie
- Cannot tell

### Q7. Coherence and Organisation

Which output is better organised and easier to follow?

- Output A
- Output B
- Tie
- Cannot tell

### Q8. Fluency and Readability

Which output is more fluent, natural and readable?

- Output A
- Output B
- Tie
- Cannot tell

### Q9. Overall Usefulness

Overall, which output would you prefer to use?

- Output A
- Output B
- Tie
- Cannot tell

### Q10. Confidence

How confident are you in your overall preference?

- Very confident
- Somewhat confident
- Not very confident

## Error Tagging

### Q11. Problems In Output A

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
- Poor organisation or narrative flow
- Wrong task style or genre
- Overstates causation, explanation or significance
- Awkward wording
- Hard to understand
- Other

### Q12. Problems In Output B

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
- Poor organisation or narrative flow
- Wrong task style or genre
- Overstates causation, explanation or significance
- Awkward wording
- Hard to understand
- Other

### Q13. Main Reason For Your Preference

In one or two sentences, explain the main reason for your overall preference.

Free-text answer.

## Dataset-Specific Questions

Show only the question set that applies to the current dataset.

## SportSett Basketball / Event Report

### S1. Event Result

Does the output clearly state the game result, including winner and score?

- Yes
- Partly
- No
- Not applicable

### S2. Key Performances

Does the output identify the most important player or team performances from the supplied data?

- Yes
- Partly
- No
- Not applicable

### S3. Event-Report Style

Does the output read like a coherent game report rather than a generic dataset summary?

- Yes
- Partly
- No
- Not applicable

### S4. Unsupported Narrative

Does the output avoid unsupported claims about causation, momentum, dominance, comeback, motivation or wider season significance?

- Yes
- Partly
- No
- Not applicable

## ToTTo / Highlighted Table Description

### T1. Focused Cell Or Region

Does the output focus on the highlighted cell or focused table region?

- Yes
- Partly
- No
- Not applicable

### T2. Correct Subject

Does the output attach the highlighted value to the correct subject, row or entity?

- Yes
- Partly
- No
- Not applicable

### T3. Concision

Is the output concise enough for a focused table description?

- Yes
- Partly
- No
- Not applicable

### T4. No Broad Table Summary

Does the output avoid turning the task into a broad summary of unrelated table content?

- Yes
- Partly
- No
- Not applicable

## E2E NLG / Attribute Verbalisation

### E1. Attribute Coverage

Does the output express all supplied attributes?

- Yes
- Partly
- No
- Not applicable

### E2. No Added Attributes

Does the output avoid adding unsupported attributes?

- Yes
- Partly
- No
- Not applicable

### E3. Natural Sentence

Does the output combine the attributes into a natural sentence or short text?

- Yes
- Partly
- No
- Not applicable

## WebNLG And DART / Triple Verbalisation

### R1. Relation Preservation

Does the output preserve the supplied subject-relation-object facts?

- Yes
- Partly
- No
- Not applicable

### R2. Entity And Value Preservation

Does the output preserve important names, numbers, units and identifiers?

- Yes
- Partly
- No
- Not applicable

### R3. No Unsupported Additions

Does the output avoid adding facts not present in the triples?

- Yes
- Partly
- No
- Not applicable

### R4. Natural Verbalisation

Does the output verbalise the triples naturally rather than listing them mechanically?

- Yes
- Partly
- No
- Not applicable

## Optional Expert Questions

Use these only for expert reviewers or a smaller diagnostic study.

### X1. Unsupported Span Marking

Highlight any phrase in either output that is not supported by the supplied source data.

Free-text or span-highlight answer.

### X2. Missing Important Content

List up to three important source facts that the weaker output should have included.

Free-text answer.

### X3. Minimal Correction

What is the smallest edit needed to make the weaker output acceptable?

Free-text answer.

### X4. Error Severity

If you found an error, how serious is the most important error?

- No error
- Minor: does not change the main meaning
- Major: affects an important claim
- Critical: makes the output misleading or unusable

## Recommended Short Volunteer Version

If the study needs to be shorter, use only:

1. Q1 Factual Correctness.
2. Q3 Main Information Coverage.
3. Q4 Task Fit.
4. Q6 Appropriate Level of Detail.
5. Q7 Coherence and Organisation.
6. Q9 Overall Usefulness.
7. Q10 Confidence.
8. Q11 Problems in Output A.
9. Q12 Problems in Output B.
10. Q13 Main Reason for Preference.

Then add only the relevant dataset-specific questions.

## Recommended Expert Version

For expert reviewers, use:

1. All required questions.
2. All relevant dataset-specific questions.
3. X1 Unsupported Span Marking.
4. X2 Missing Important Content.
5. X3 Minimal Correction.
6. X4 Error Severity.

## Why These Questions Are The Best Fit For This Project

These questions align with the system's actual research claims:

- Q1 and Q2 test factuality and source grounding.
- Q3 tests content selection.
- Q4 and the dataset-specific questions test task awareness.
- Q5 and Q6 test whether outputs are focused rather than bloated or generic.
- Q7 tests narrative structure, especially for event reports.
- Q8 checks fluency without letting fluency dominate the study.
- Q9 captures overall usefulness.
- Q11 and Q12 reveal the failure modes behind the preferences.
- Q13 gives qualitative evidence for the dissertation discussion.

This combination is stronger than asking only for overall preference because it separates:

- factual correctness;
- coverage;
- task fit;
- narrative quality;
- readability;
- error type.

