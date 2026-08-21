# LLM-Only Multi-Agent Table-to-Text Experimentation Document

## Purpose

This document records the design, implementation, failures, fixes, and empirical findings from an experimental LLM-only multi-agent table-to-text system. The experiment was originally developed in a clone of the main project so that the behaviour of the existing system would not overly influence the new design. Its retained implementation and evidence have since been extracted into a focused experiment package.

The central research question was:

> Can a multi-agent LLM workflow reduce the likelihood of hallucination compared with a bare single-prompt LLM baseline, without relying on the deterministic analytics and verification layers used by the current Table2Text system?

The experiment should be treated as separate from the main operational system. It reuses benchmark loading and evaluation tooling only, so that outputs are comparable against existing runs.

## Repository Context

The isolated experiment package is:

```text
experiments/llm_only_pipeline/
```

The main project remains:

```text
table2text_pydanticai/
```

The LLM-only workflow lives in:

```text
experiments/llm_only_pipeline/src/table2text_llm_only/
```

The callable evaluation backend is:

```text
table2text_llm_only.backend.llm_only_multi_agent
```

The experiment deliberately does not call the main system's:

```text
Table2TextWorkflow
execute_plan()
deterministic_fact_candidate_scaffold()
deterministic_audit()
```

This boundary matters because the experiment is not testing the full current system. It is testing whether a multi-agent LLM-only structure, by itself, can reduce hallucination risk.

## Data Used

The main worked example was the prepared SportSett basketball example:

```text
experiments/llm_only_pipeline/data/sportsett_basketball_4934.jsonl
```

Dataset and example:

```text
dataset_id: sportsett_basketball
example_id: 4934
task_family: event_report
output_mode: multi_paragraph_report
language: en
```

The source contains structured NBA game data for Philadelphia 76ers vs Memphis Grizzlies, including:

- game metadata: date, venue, city, attendance, capacity
- team records and standings
- quarter-by-quarter line scores
- full-game team totals
- player box scores
- next-game metadata

Human references were held out from the generation agents and used only for evaluation metrics.

## Reference Policy

A strict held-out reference policy was used.

Generation agents received:

```text
request
task_family
output_mode
language
source_text
source_payload
parent_table
metadata
```

Generation agents did not receive:

```text
references
targets
summaries
gold outputs
evaluation answers
```

This was important because the aim was hallucination reduction from source grounding, not imitation of reference text.

## Initial LLM-Only Multi-Agent Design

The first LLM-only workflow decomposed generation into the following agents:

```text
Source Interpreter
LLM Analysis
Claim Critic
Claim Adjudicator
Writer
Output Auditor
Repair Agent
```

The intended information flow was:

```text
source packet
-> source interpretation
-> candidate claims
-> claim critique
-> accepted/rejected claim ledger
-> draft text from accepted claims only
-> output audit
-> repair if needed
-> final text
```

The design principle was that each agent should have a narrower role than a single end-to-end LLM prompt:

- The Source Interpreter identifies task type, important entities, fields, allowed claim types, and risks.
- The LLM Analysis Agent proposes candidate claims from the source.
- The Claim Critic checks each claim against the source.
- The Claim Adjudicator creates a final accepted claim ledger.
- The Writer generates text only from accepted claims.
- The Output Auditor checks whether the draft is supported.
- The Repair Agent revises unsupported or incomplete output using accepted claims only.

The writer was intentionally not allowed to add facts directly from the raw source. It was supposed to write only from accepted claims. This made hallucination less likely but also made the system brittle when upstream agents failed to produce a usable claim ledger.

## Rationale For LLM-Only Rather Than Deterministic Analytics

The original full system uses deterministic analytics and structured verification to build and check facts. For this experiment, those mechanisms were intentionally removed.

The reason was methodological: we wanted to test whether the multi-agent structure alone improves factual grounding compared with a bare LLM prompt. If deterministic analytics were included, any improvement could be attributed to deterministic computation rather than multi-agent decomposition.

The LLM-only design therefore tested a more constrained hypothesis:

> Even without deterministic analytics, can a role-separated LLM pipeline improve factual discipline by forcing claims to be proposed, critiqued, adjudicated, written from, and audited?

## Difference From The Current Full System

The current full system and the LLM-only experiment differ in several important ways.

| Dimension | Current full system | LLM-only experiment |
|---|---|---|
| Source analysis | Uses structured workflow and deterministic stages | Uses LLM interpretation |
| Fact extraction | Uses deterministic and structured fact machinery | Uses LLM-generated candidate claims |
| Verification | Uses verifier/auditor mechanisms plus structured support | Uses LLM critic, adjudicator, auditor |
| Writer input | Writer receives system-curated facts/evidence | Writer receives accepted LLM claims only |
| Hallucination control | Deterministic grounding plus LLM audit | LLM role separation and evidence-gated claims |
| Failure mode | Can be verbose or reference-like, but has stronger scaffolding | Can collapse if an agent returns malformed or empty JSON |
| Experimental role | Main operational baseline | Isolated research prototype |

The LLM-only system should not be interpreted as replacing the current system. It is a controlled comparison to understand what multi-agent decomposition contributes when deterministic analytics are removed.

## Implementation Summary

Key files retained in the isolated experiment package:

```text
src/table2text_llm_only/client.py
src/table2text_llm_only/schemas.py
src/table2text_llm_only/workflow.py
src/table2text_llm_only/backend.py
config/variants.json
notebooks/llm_only_smoke_test.ipynb
README.md
```

The client uses an OpenAI-compatible chat completions API. The default endpoint is DeepSeek:

```text
base_url: https://api.deepseek.com
api key env var: DEEPSEEK_API_KEY
```

The model can be configured with:

```text
llm_only_model
T2T_LLM_ONLY_MODEL
```

The two main models tested were:

```text
deepseek-v4-flash
deepseek-v4-pro
```

## Workflow Evolution During The Experiment

The system changed substantially during testing. These changes are part of the experimental findings because they reveal where LLM-only multi-agent systems are fragile.

### 1. Schema Tolerance Was Required

Early runs failed because LLM outputs were semantically reasonable but did not exactly match the Pydantic schemas.

Examples included:

- `confidence` returned as `"high"` rather than a float.
- `notes` returned as a string rather than a list.
- `source_units` returned as a list rather than a string.
- `severity` returned as `"block"` rather than `"blocking"` or `"critical"`.
- `suggested_action` returned as a free-text instruction rather than an enum.
- `claim_type` missing from one candidate claim.

The schemas were therefore made more tolerant at the system boundary:

- string labels such as `"high"` are converted to numeric confidence values
- string fields can absorb list-like responses
- list fields can absorb string responses
- free-text audit actions are normalised
- missing `claim_type` defaults to `source_fact`

Finding:

> A practical LLM-only multi-agent system needs tolerant structured parsing. Strict schemas are useful internally, but raw model outputs require normalisation before validation.

### 2. The System Initially Blocked Or Refused

At one point, the system produced:

```text
No verified game data was available for this report.
Audit: block 0.0
```

This happened even though the SportSett source clearly contained game data. The problem was not hallucination. The problem was over-cautious collapse.

The LLM Analysis Agent returned zero claims, leaving downstream agents with nothing to write from. The writer then refused rather than inventing.

This was a useful but undesirable behaviour. The user clarified the design goal:

> The system should not block anything. It should reduce the likelihood of hallucination.

The system was changed so that `block` is not a final state. The audit decision schema now permits:

```text
pass
revise
```

Any model-emitted `block` is converted to:

```text
revise
```

The internal high-risk severity label was also changed from `blocking` to:

```text
critical
```

Finding:

> Hallucination reduction should not be implemented as refusal for this task. A better behaviour is to produce the safest supported output available and mark risk as a repair signal.

### 3. A Recovery Analyst Was Needed

The first major live failure was:

```text
candidate_claim_count: 0
accepted_claim_count: 0
audit_decision: block
generated_text: No verified game data was available for this report.
```

The source interpreter had correctly understood the SportSett source, but the LLM Analysis Agent returned an empty claim list after a long completion.

A recovery pass was added:

```text
llm_analysis_recovery
```

This agent triggers only when:

```text
claims == []
source is non-empty
```

It asks for a conservative claim ledger using directly visible source values.

Finding:

> Multi-agent systems need recovery paths for silent agent collapse. A failed intermediate agent should not force the entire pipeline into refusal or empty output.

### 4. Empty Adjudication Was A Second Collapse Point

After the recovery analyst was added, the system produced candidate claims successfully, but another failure appeared:

```text
candidate_claim_count: 14
accepted_claim_count: 0
rejected_claim_count: 0
generated_text: ""
audit_decision: revise
```

The adjudicator returned neither accepted nor rejected claims. This is worse than rejecting claims because it erased the ledger without explanation.

A guarded fallback adjudication was added:

- If candidate claims exist
- and accepted claims are empty
- and rejected claims are empty
- then high-confidence cited candidate claims are promoted into the accepted ledger

This fallback still does not perform deterministic analytics. It only carries forward LLM-generated claims that already include explicit evidence fields.

Finding:

> LLM-only pipelines need safeguards against "empty ledger" failures. Otherwise, one weak agent can erase valid work from earlier agents.

### 5. Empty Writer Output Was Also Guarded

Another guard was added:

- If accepted claims exist
- but the writer returns no sentences
- then the workflow creates a fallback draft directly from accepted claim text

This prevents the writer from causing an empty final output when a valid accepted claim ledger exists.

Finding:

> The writer should be allowed to be cautious, but not to silently return nothing when evidence-backed accepted claims are available.

### 6. Evidence Gate Was Added

During Pro testing, one accepted claim had no `source_refs` and no `copied_values`:

```text
Ben Simmons dished out a game-high 6 assists.
```

The claim was probably correct, and the critic said it was supported, but it violated the experiment's evidence principle. The writer should not use claims that lack explicit evidence fields.

An evidence gate was added:

```text
enforce_accepted_claim_evidence(...)
```

It runs after adjudication and before writing.

Any accepted claim without both:

```text
source_refs
copied_values
```

is moved to:

```text
rejected_claims
```

Finding:

> In an LLM-only system, verbal assertion by a critic is not enough. Accepted claims must carry explicit evidence metadata so the writer can remain constrained.

## Current Final Behaviour

The intended current behaviour is:

```text
Never block final output.
Never let the writer use claims without explicit evidence.
Repair or revise when risk is detected.
Return the safest supported output available.
```

Audit semantics are:

| Audit field | Meaning |
|---|---|
| `pass` | Output appears supported by accepted evidence-backed claims |
| `revise` | Output has risk or missing coverage and should be repaired |
| `critical` | High hallucination risk finding, not a refusal |

## Flash Run Result

The latest Flash artifact was:

```text
experiments/llm_only_pipeline/artifacts/sportsett_4934/flash/result.json
```

Summary:

```text
model: deepseek-v4-flash
agent_count: 6
candidate_claim_count: 7
accepted_claim_count: 7
rejected_claim_count: 0
audit_decision: pass
audit_support_rate: 1.0
repair_attempted: false
prompt_tokens: 61,372
completion_tokens: 20,039
total_tokens: 81,411
```

Generated text:

```text
On December 2, 2018, the Philadelphia 76ers defeated the Memphis Grizzlies 103-95 at Wells Fargo Center in Philadelphia before a near-capacity crowd of 20,300. The win improved Philadelphia to 17-8; Memphis fell to 13-9. Quarter scoring went 26-25 Philadelphia, 28-19 Philadelphia, 24-24, and 27-25 Memphis. Philadelphia seized control with a 28-19 second quarter and led 54-44 at halftime. J.J. Redick led all scorers with 24 points on 9-of-17 shooting. Jimmy Butler (21), Ben Simmons (19), and Joel Embiid (15) also reached double figures for Philadelphia.
```

Diagnostic summary:

```text
word_count: 85
sentence_count: 7
generated_number_count: 28
generated_number_source_precision: 1.0
generated_number_reference_precision: 0.8571
```

Interpretation:

The Flash model produced a cautious and compact report. It had perfect generated-number precision against the source and the best source-grounded HHEM score among the compared systems. It was less similar to the human reference because it omitted unsupported play-by-play detail and was much shorter.

## Pro Run Result

The existing Pro artifact was:

```text
experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/result.json
```

Summary:

```text
model: deepseek-v4-pro
agent_count: 6
candidate_claim_count: 9
accepted_claim_count: 9
rejected_claim_count: 0
audit_decision: pass
audit_support_rate: 1.0
repair_attempted: false
prompt_tokens: 61,446
completion_tokens: 19,178
total_tokens: 80,624
```

Generated text:

```text
The Philadelphia 76ers defeated the Memphis Grizzlies 103-95 on Sunday, December 2, 2018 at Wells Fargo Center in Philadelphia. Philadelphia entered the game with a 17-8 record, while Memphis held a 13-9 mark, and the contest drew an attendance of 20,300. The 76ers used a 28-19 second quarter to build a 54-44 halftime lead. J.J. Redick led the charge with 24 points on 9-of-17 shooting. Jimmy Butler added 21 points, while Ben Simmons posted a double-double of 19 points, 12 rebounds and a game-high 6 assists. Joel Embiid also recorded a double-double with 15 points and 14 rebounds. Mike Conley paced the Grizzlies with 21 points.
```

Diagnostic summary:

```text
word_count: 106
sentence_count: 8
generated_number_count: 25
generated_number_source_precision: 1.0
generated_number_reference_precision: 0.84
```

Important caveat:

This Pro artifact was generated before the final evidence-gate patch. One accepted claim in the artifact lacked explicit `source_refs` and `copied_values`. The fact was likely correct, but the final evidence gate was added precisely to prevent such claims being used in future runs.

A fresh evidence-gated Pro rerun was attempted, but it required sending the SportSett source payload to DeepSeek Pro again. The approval layer blocked the run because explicit approval for that data transfer was not present. Therefore, the Pro metrics below are from the existing Pro artifact, not a fresh evidence-gated Pro artifact.

## Metric Results

Metrics were computed using the existing evaluation tooling. The selected comparison table was written to:

```text
experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/metrics/sportsett_4934_selected_metric_comparison.csv
```

### Selected Metric Comparison

| Metric context | Metric | Higher is better | Full system | Raw DeepSeek Flash | LLM-only Flash | LLM-only Pro |
|---|---|---:|---:|---:|---:|---:|
| reference similarity | BERTScore F1 | yes | 0.8517 | 0.8504 | 0.8318 | 0.8548 |
| reference similarity | BLEU | yes | 0.1071 | 0.1357 | 0.0363 | 0.0525 |
| reference similarity | chrF | yes | 0.4166 | 0.3860 | 0.1835 | 0.2580 |
| reference similarity | METEOR | yes | 0.2580 | 0.2534 | 0.1111 | 0.1584 |
| reference similarity | ROUGE-L | yes | 0.2311 | 0.3214 | 0.2341 | 0.3058 |
| source grounded | HHEM mean support | yes | 0.2065 | 0.1662 | 0.2200 | 0.1808 |
| source grounded | HHEM unsupported sentence rate | no | 0.7895 | 0.7692 | 0.7143 | 0.7500 |

AlignScore was unavailable locally for the LLM-only runs because the required separate worker Python executable was not configured.

## Interpretation Of Metrics

### Reference Similarity

The Pro model improved reference similarity compared with LLM-only Flash:

```text
BERTScore F1: 0.8318 -> 0.8548
ROUGE-L:      0.2341 -> 0.3058
chrF:         0.1835 -> 0.2580
METEOR:       0.1111 -> 0.1584
BLEU:         0.0363 -> 0.0525
```

This suggests that Pro generated a more reference-like report. It included more player performance details and sounded more like a conventional game recap.

However, reference similarity is not the same as factual reliability. The human reference contains play-by-play style details, such as runs and momentum, that are not fully available in the structured box score source. A cautious system that avoids unsupported narrative will naturally score lower on some lexical metrics.

### Source-Grounded Factuality

The Flash LLM-only run achieved the strongest source-grounded HHEM result:

```text
Full system:       0.2065
Raw Flash:         0.1662
LLM-only Flash:    0.2200
LLM-only Pro:      0.1808
```

For unsupported sentence rate, where lower is better:

```text
Full system:       0.7895
Raw Flash:         0.7692
LLM-only Flash:    0.7143
LLM-only Pro:      0.7500
```

This suggests that the more cautious Flash output was more source-grounded under HHEM, while Pro was more fluent and reference-like but slightly more exposed to unsupported-sentence penalties.

### Numeric Precision

Both LLM-only Flash and Pro achieved:

```text
generated_number_source_precision: 1.0
```

This is an important result. It suggests that the claim-led workflow helped preserve numeric grounding, at least on this SportSett example.

Generated-number reference precision differed slightly:

```text
LLM-only Flash: 0.8571
LLM-only Pro:   0.8400
```

The system is therefore better aligned with the source than with the reference, which is consistent with the experiment's design.

## Comparison With The Bare Raw LLM Baseline

The raw DeepSeek Flash baseline directly sends the benchmark request and source to the model. It bypasses:

- source interpretation
- claim extraction
- claim critique
- claim adjudication
- writer claim constraints
- output audit
- repair
- evidence-gating

Compared with raw Flash, LLM-only Flash improved the source-grounded HHEM score:

```text
Raw Flash:      0.1662
LLM-only Flash: 0.2200
```

It also reduced unsupported sentence rate:

```text
Raw Flash:      0.7692
LLM-only Flash: 0.7143
```

This supports the experimental hypothesis for this example: a multi-agent LLM-only structure can improve source-grounded factuality compared with a bare LLM prompt.

However, the LLM-only Flash output had much lower lexical similarity to the reference:

```text
Raw Flash BLEU:      0.1357
LLM-only Flash BLEU: 0.0363
Raw Flash ROUGE-L:   0.3214
LLM-only ROUGE-L:    0.2341
```

This is not necessarily a failure, because the cautious output intentionally avoided unsupported narrative. But it shows a tradeoff: stricter hallucination reduction can reduce reference-style coverage.

## Comparison With The Current Full System

Compared with the full system, LLM-only Flash achieved better source-grounded HHEM on this example:

```text
Full system:    0.2065
LLM-only Flash: 0.2200
```

It also had a lower unsupported sentence rate:

```text
Full system:    0.7895
LLM-only Flash: 0.7143
```

However, the full system performed better on several reference-similarity metrics:

```text
Full system BLEU:   0.1071
LLM-only Flash:     0.0363

Full system chrF:   0.4166
LLM-only Flash:     0.1835

Full system METEOR: 0.2580
LLM-only Flash:     0.1111
```

Interpretation:

The LLM-only Flash system is more conservative and better source-grounded on this one example, but less complete and less reference-like than the full system. This suggests that the current full system's deterministic and structured stages may help produce richer reports, while the LLM-only claim gate reduces unsupported elaboration.

## Flash vs Pro Findings

Flash and Pro behaved differently.

### Flash

Strengths:

- More cautious
- Better source-grounded HHEM score
- Lower unsupported sentence rate
- Perfect number precision against source
- Faster than Pro in practice

Weaknesses:

- Shorter output
- Lower reference similarity
- Less rich game recap

### Pro

Strengths:

- More fluent output
- More complete player-performance coverage
- Better reference similarity
- Strong BERTScore and ROUGE-L
- Perfect number precision against source

Weaknesses:

- Slower
- More verbose intermediate JSON
- Initially produced truncated JSON during analysis
- Accepted one claim without explicit evidence before the evidence gate was added
- Slightly worse source-grounded HHEM than Flash

Overall:

> Pro is better for report-like fluency and reference similarity, while Flash was better for cautious source-grounded factuality in this experiment.

## Major Failure Modes Observed

### Failure Mode 1: Schema Mismatch

LLMs often returned valid-looking content in invalid shapes. Examples:

```text
confidence: "high"
notes: "All sentences are supported"
source_units: ["game metadata", "team stats"]
severity: "block"
suggested_action: "Regenerate the report..."
```

Resolution:

Schema normalisation was added.

Dissertation implication:

Structured LLM systems require robust parsing and normalisation layers. The schema is not only a validator; it is also part of the control system.

### Failure Mode 2: Over-Cautious Refusal

The system initially blocked output or produced refusal text when claim generation failed.

Resolution:

Final blocking was removed. `block` is now normalised to `revise`, and the workflow attempts recovery or fallback output.

Dissertation implication:

For data-to-text generation, hallucination reduction should not be equivalent to refusal. The desired behaviour is minimal supported generation.

### Failure Mode 3: Empty Claim Ledger

The analysis or adjudication agent sometimes returned empty outputs despite visible source data.

Resolution:

Recovery analysis and fallback adjudication were added.

Dissertation implication:

Multi-agent decomposition creates more control points but also more failure points. Each stage needs fail-soft behaviour.

### Failure Mode 4: Unsupported Evidence Metadata

A claim can be verbally judged supported but still lack explicit evidence pointers.

Resolution:

Evidence gate was added before writing.

Dissertation implication:

For hallucination reduction, it is insufficient for an LLM to say a claim is supported. The claim must carry inspectable evidence metadata.

### Failure Mode 5: Token Cost And Latency

Both Flash and Pro consumed around 80k total tokens for a single SportSett example:

```text
Flash total tokens: 81,411
Pro total tokens:   80,624
```

Pro was noticeably slower in live testing.

Dissertation implication:

LLM-only multi-agent systems may improve factual discipline but can be expensive and slow because multiple agents repeatedly read long source packets.

## Methodological Limitations

This experiment has several limitations.

1. Single primary example

Most detailed results are from one SportSett basketball example. The findings are useful but should not be overgeneralised without broader dataset runs.

2. Metrics are imperfect

HHEM sentence splitting treated `J.J. Redick` as separate sentence fragments:

```text
J.J.
Redick led all scorers...
```

This likely distorted support scores. Therefore, HHEM should be interpreted comparatively, not as an absolute truth measure.

3. References contain unsupported narrative

The human reference includes play-by-play style content that is not fully present in the structured source. A source-faithful output can therefore score worse on reference metrics.

4. Pro result caveat

The reported Pro metrics use the existing Pro artifact generated before the final evidence gate. A fresh Pro run after the evidence gate would require explicit approval to send the SportSett source data to DeepSeek Pro again.

5. No deterministic verification

This is intentional, but it means the LLM-only workflow cannot guarantee correctness. It can only reduce risk through decomposition, evidence constraints, and audit.

## Research Findings

The experiment supports several dissertation-level findings.

### Finding 1: Multi-agent decomposition can reduce hallucination risk compared with a bare prompt

On SportSett 4934, LLM-only Flash improved source-grounded HHEM support compared with raw Flash:

```text
0.1662 -> 0.2200
```

It also reduced unsupported sentence rate:

```text
0.7692 -> 0.7143
```

This suggests that even without deterministic analytics, forcing the model through claim generation, critique, adjudication, writing, and audit can improve factual discipline.

### Finding 2: The strongest hallucination control came from constraining the writer

The writer was only allowed to use accepted claims. This prevented free-form elaboration from the raw source.

However, this also caused early failures when accepted claims were empty. The final design therefore combines writer constraint with recovery and fallback mechanisms.

### Finding 3: Blocking is the wrong objective for this use case

The desired behaviour is not refusal. The desired behaviour is:

```text
produce the safest supported text possible
```

The system therefore changed from blocking to revision and evidence-gated fallback.

### Finding 4: Evidence metadata is essential

The evidence gate became one of the most important design lessons. Without it, an LLM critic can verbally approve a claim without leaving inspectable support.

For dissertation framing:

> The accepted claim ledger should be treated as the factual contract between analysis and generation.

### Finding 5: Richer outputs can reduce factuality scores

Pro produced richer and more reference-like output but scored lower than Flash on source-grounded HHEM. This reflects a common tension in data-to-text:

```text
coverage and fluency vs cautious source faithfulness
```

### Finding 6: LLM-only multi-agent systems are operationally expensive

The workflow consumed around 80k tokens for a single example. This makes it useful as a research prototype, but expensive compared with a simpler single-call baseline.

## Dissertation Use

This experiment can support a dissertation section structured as follows:

1. Motivation

Explain that hallucination in table-to-text generation can arise when LLMs add unsupported facts, misread numeric values, or imitate reference-like narrative not present in source data.

2. Experimental Design

Describe an isolated LLM-only clone with no deterministic analytics, using the same dataset and metrics as the main system.

3. Architecture

Describe the agent chain:

```text
Source Interpreter -> Claim Analyst -> Critic -> Adjudicator -> Writer -> Auditor -> Repair
```

4. Control Mechanisms

Explain:

- writer only sees accepted claims
- claims require source references and copied values
- audit cannot block final output
- repair handles risk
- fallback handles empty intermediate outputs

5. Results

Use the metric table above.

6. Discussion

Discuss the tradeoff:

- LLM-only Flash improved source-grounded factuality
- Pro improved reference similarity
- both remained expensive
- robust schema normalisation was necessary

7. Limitations

Emphasise single-example scope, imperfect factuality metrics, and the lack of deterministic guarantees.

## Suggested Dissertation Paragraph

The following paragraph can be adapted directly:

> To isolate the effect of multi-agent decomposition from deterministic verification, I implemented a separate LLM-only table-to-text pipeline in an experimental clone of the project. This pipeline reused the same benchmark loading and evaluation framework as the main system but did not call the existing deterministic analytics, fact scaffolding, or audit mechanisms. The pipeline decomposed generation into source interpretation, claim analysis, claim critique, claim adjudication, constrained writing, output auditing, and repair. The writer was only allowed to realise accepted claims, and later iterations added an evidence gate requiring accepted claims to carry explicit source references and copied values. On the SportSett basketball example 4934, the LLM-only Flash configuration achieved higher source-grounded HHEM support than both the raw single-LLM baseline and the current full system, although it scored lower on reference-similarity metrics because it produced a shorter and more conservative report. These results suggest that multi-agent decomposition alone can reduce hallucination likelihood compared with a bare LLM prompt, but also that LLM-only systems require robust schema normalisation, recovery from empty intermediate outputs, and explicit evidence gating to avoid collapse or unsupported claim propagation.

## Artifact Index

Important files produced by the experiment:

```text
experiments/llm_only_pipeline/src/table2text_llm_only/client.py
experiments/llm_only_pipeline/src/table2text_llm_only/schemas.py
experiments/llm_only_pipeline/src/table2text_llm_only/workflow.py
experiments/llm_only_pipeline/src/table2text_llm_only/backend.py
experiments/llm_only_pipeline/config/variants.json
experiments/llm_only_pipeline/notebooks/llm_only_smoke_test.ipynb
experiments/llm_only_pipeline/README.md
```

Key output artifacts:

```text
experiments/llm_only_pipeline/artifacts/sportsett_4934/flash/result.json
experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/result.json
```

Key metric files:

```text
experiments/llm_only_pipeline/artifacts/sportsett_4934/flash/metrics/reference_metrics.jsonl
experiments/llm_only_pipeline/artifacts/sportsett_4934/flash/metrics/source_grounded_metrics.jsonl
experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/metrics/reference_metrics.jsonl
experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/metrics/source_grounded_metrics.jsonl
experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/metrics/sportsett_4934_selected_metric_comparison.csv
experiments/llm_only_pipeline/artifacts/sportsett_4934/pro/metrics/sportsett_4934_generation_diagnostics_comparison.csv
```

## Conclusion

The LLM-only multi-agent experiment demonstrated that hallucination likelihood can be reduced through workflow structure alone, even without deterministic analytics. The most important mechanisms were claim decomposition, writer restriction to accepted claims, audit-as-revision rather than blocking, and the final evidence gate. On the SportSett example, the Flash LLM-only system outperformed both the raw LLM baseline and the current full system on source-grounded HHEM support, while Pro produced more fluent and reference-like text.

The experiment also showed that LLM-only multi-agent systems are fragile unless engineered with tolerant schemas, fallback recovery, and explicit evidence requirements. The system's development failures were therefore not incidental: they revealed core design requirements for practical hallucination reduction in LLM-based table-to-text generation.
