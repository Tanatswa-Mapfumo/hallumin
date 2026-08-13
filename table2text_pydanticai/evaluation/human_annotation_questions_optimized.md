# Optimized Human Annotation Questions

## Study Title

Human Evaluation of Factual Accuracy and Usefulness in Source-Grounded Data-to-Text Generation

## Methodological Basis

These questions are based on the factual-accuracy evaluation approach described by Thomson, Reiter and Sundararajan in *Evaluating factual accuracy in complex data-to-text*.

The key idea is to separate two things:

1. factual accuracy: whether the output contains claims that are wrong, unsupported, misleading or not checkable from the source;
2. task quality: whether the output selects useful content, fits the requested genre and reads well.

This separation matters for our project because a report can be factually accurate but omit useful information, or fluent and detailed but contain unsupported claims.

## Participant Instructions

You will compare two outputs for the same source data. The outputs are labelled only as Output A and Output B. Please do not try to guess which system produced which output.

Use the supplied source data as the main authority. The human reference output is provided as an example of the intended task, but it may not contain every valid detail and it may phrase the same facts differently. Do not penalise an output simply because it says the same supported facts in different words.

When judging factual accuracy, look for specific words, numbers, phrases or sentences that are wrong, unsupported, misleading or not checkable from the source.

When judging task quality, consider whether the output includes the important source-supported information and presents it in a useful way.

Choose `Tie` when both outputs are similarly good or similarly poor. Choose `Cannot tell` only when the source data is too unclear to judge.

## Factual Error Categories

Use these categories when marking errors.

| Category | Use when |
| --- | --- |
| Incorrect number | A number, score, date, percentage, count, rank or measurement is wrong. |
| Incorrect named entity | A person, team, place, organisation, title or subject is wrong. |
| Incorrect word or relation | A word or relation changes the meaning, such as wrong verb, wrong role, wrong direction, wrong comparison or wrong attribute. |
| Context or misleading claim | The words may be partly true, but the claim is misleading, over-interpreted or unsupported in context. |
| Not checkable | The claim cannot be verified from the supplied source data. |
| Other factual error | A factual problem is present but does not fit the categories above. |

## Common Questions

### Q1. Factual Accuracy Preference

Which output has fewer factual accuracy errors?

```text
Output A
Output B
Tie
Cannot tell
```

### Q2. Output A Error Annotation

List any factual errors in Output A.

For each error, give:

```text
sentence or phrase:
error category:
brief correction or explanation:
```

If you find no factual errors, write:

```text
No factual errors found.
```

### Q3. Output B Error Annotation

List any factual errors in Output B using the same format as Q2.

### Q4. Unsupported Or Not-Checkable Claims

Which output contains fewer claims that are unsupported or not checkable from the supplied source data?

```text
Output A
Output B
Tie
Cannot tell
```

### Q5. Context And Misleading Claims

Which output better avoids misleading context, unsupported explanations, causal wording or over-interpretation?

```text
Output A
Output B
Tie
Cannot tell
```

### Q6. Important Information Coverage

Which output includes more of the important source-supported information needed for the task?

```text
Output A
Output B
Tie
Cannot tell
```

### Q7. Focus And Relevance

Which output better avoids irrelevant or distracting information?

```text
Output A
Output B
Tie
Cannot tell
```

### Q8. Task Or Genre Fit

Which output better matches the requested task type or genre?

```text
Output A
Output B
Tie
Cannot tell
```

### Q9. Appropriate Detail

Which output has the better level of detail for this task?

```text
Output A
Output B
Tie
Cannot tell
```

### Q10. Organisation And Readability

Which output is better organised and easier to read?

```text
Output A
Output B
Tie
Cannot tell
```

### Q11. Reference Alignment

Which output is closer to the human reference without contradicting the source data?

```text
Output A
Output B
Tie
Cannot tell
```

### Q12. Overall Preference

Overall, which output would you prefer to use?

```text
Output A
Output B
Tie
Cannot tell
```

### Q13. Confidence

How confident are you in your overall preference?

```text
Very confident
Somewhat confident
Not very confident
Cannot tell
```

### Q14. Main Reason For Preference

In one or two sentences, explain the main reason for your overall preference.

## Dataset-Specific Questions

Show only the relevant dataset-specific question group for each packet.

## SportSett Basketball / Event Reports

### S1. Result Accuracy

Does the output correctly state the winner, loser and final score?

```text
Yes
Partly
No
Cannot tell
```

### S2. Statistics Attribution

Are player and team statistics attributed to the correct players, teams and periods?

```text
Yes
Partly
No
Cannot tell
```

### S3. Event Narrative Support

Does the output use available score-period and box-score evidence to form a coherent game report?

```text
Yes
Partly
No
Cannot tell
```

### S4. Unsupported Narrative

Does the output avoid unsupported claims about causation, momentum, dominance, comeback, motivation or wider season significance?

```text
Yes
Partly
No
Cannot tell
```

### S5. Most Important Missing Detail

Name the most important game detail the output missed, if any.

## ToTTo / Highlighted Table Text

### T1. Focused Region

Does the output focus on the highlighted cell or focused table region?

```text
Yes
Partly
No
Cannot tell
```

### T2. Entity And Header Grounding

Does the output correctly connect the highlighted value to the right row entity and column/header meaning?

```text
Yes
Partly
No
Cannot tell
```

### T3. Table Scope

Does the output avoid broad table summaries that go beyond the focused proposition?

```text
Yes
Partly
No
Cannot tell
```

## E2E NLG / Meaning Representation

### E1. Slot Coverage

Does the output preserve all supplied meaning-representation attributes?

```text
Yes
Partly
No
Cannot tell
```

### E2. No Added Attributes

Does the output avoid adding attributes that are not in the source?

```text
Yes
Partly
No
Cannot tell
```

### E3. Natural Realisation

Does the output realise the attributes in a natural sentence rather than a mechanical list?

```text
Yes
Partly
No
Cannot tell
```

## WebNLG / Source Triples

### W1. Triple Coverage

Does the output verbalise all supplied triples?

```text
Yes
Partly
No
Cannot tell
```

### W2. Relation Direction

Does the output preserve relation direction, entity identity and values?

```text
Yes
Partly
No
Cannot tell
```

### W3. No Added Facts

Does the output avoid adding outside facts?

```text
Yes
Partly
No
Cannot tell
```

## DART / Source Triples

### D1. Triple Coverage

Does the output verbalise all supplied triples?

```text
Yes
Partly
No
Cannot tell
```

### D2. Relation Direction

Does the output preserve relation direction, entity identity and values?

```text
Yes
Partly
No
Cannot tell
```

### D3. Concision

Does the output stay concise while still expressing the full source content?

```text
Yes
Partly
No
Cannot tell
```
