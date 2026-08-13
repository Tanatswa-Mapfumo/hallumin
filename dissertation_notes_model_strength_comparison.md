# Dissertation Notes: Model Strength and Architecture Effects

## Purpose

This note records the follow-up pro-model comparison run and explains how it
maps onto the existing flash-model evaluation. It is intended for dissertation
writing and graph preparation rather than as a replacement for the main
25-example evaluation.

The useful question is not simply whether a stronger model improves every
number. The more useful question is:

```text
How much of the result comes from the architecture, and how much comes from
the model used inside or outside the architecture?
```

## Artifacts

| Artifact | Path |
|---|---|
| Four-dataset pro generations | `evaluation/generations/four_dataset_pro_comparison_20260812_215239_combined_generations.jsonl` |
| Four-dataset pro metrics | `evaluation/results/four_dataset_pro_comparison_20260812_215239_reference_metrics_combined.jsonl` |
| Four-dataset pro variant config | `evaluation/config/variants_four_dataset_pro_comparison_20260812_215239.json` |
| Main 25-example flash generations | `evaluation/generations/five_dataset_five_each_raw_generic_flash_20260805_181001_combined_generations.jsonl` |
| Main 25-example flash metrics | `evaluation/results/five_dataset_five_each_raw_generic_flash_20260805_181001_reference_metrics.jsonl` |
| SportSett pro case metrics | `evaluation/results/sportsett_basketball_4934_fast_reference_metrics_fixed.jsonl` |

The four-dataset pro run excludes SportSett because SportSett example `4934`
had already been run separately with pro.

## Compared Variants

| Variant | Meaning |
|---|---|
| `full_system_flash` | Full workflow using DeepSeek v4-flash, taken from the main 25-example run. |
| `raw_generic_flash` | Raw single-call DeepSeek v4-flash with generic request only. |
| `full_system_pro` | Full workflow with all six agent roles on DeepSeek v4-pro. |
| `raw_generic_pro` | Raw single-call DeepSeek v4-pro with generic request only. |

The important methodological detail is that the raw baseline is generic. It does
not receive the dataset ID, task family, expected output mode, or hidden
reference. This makes it a stricter and fairer baseline than the earlier
benchmark-aware raw prompt.

## Example Mapping

The pro run maps cleanly onto examples that already exist in the flash
25-example run.

| Dataset | Example ID | Flash full | Flash raw | Pro full | Pro raw |
|---|---|---|---|---|---|
| `e2e_nlg` | `e2e_nlg-test-51` | yes | yes | yes | yes |
| `totto` | `totto-validation-204` | yes | yes | yes | yes |
| `web_nlg` | `web_nlg_en-test-51` | yes | yes | yes | yes |
| `dart` | `dart-test-53` | yes | yes | yes | yes |

These shared `dataset_id` and `example_id` values allow direct per-example
graphs for:

```text
architecture effect under flash
architecture effect under pro
model upgrade effect inside the workflow
model upgrade effect for the raw baseline
runtime cost of architecture and model strength
```

## Generation Status

All four pro examples completed without generation errors.

| Dataset | Example | Variant | Release status | Writer mode | Runtime seconds |
|---|---|---|---|---|---:|
| `e2e_nlg` | `e2e_nlg-test-51` | `full_system_pro` | `approved_with_warnings` | `llm_writer` | 20.94 |
| `e2e_nlg` | `e2e_nlg-test-51` | `raw_generic_pro` | n/a | n/a | 2.33 |
| `totto` | `totto-validation-204` | `full_system_pro` | `approved_with_warnings` | `llm_writer` | 19.35 |
| `totto` | `totto-validation-204` | `raw_generic_pro` | n/a | n/a | 3.83 |
| `web_nlg` | `web_nlg_en-test-51` | `full_system_pro` | `approved_with_warnings` | `llm_writer` | 31.86 |
| `web_nlg` | `web_nlg_en-test-51` | `raw_generic_pro` | n/a | n/a | 1.90 |
| `dart` | `dart-test-53` | `full_system_pro` | `approved_with_warnings` | `llm_writer` | 14.46 |
| `dart` | `dart-test-53` | `raw_generic_pro` | n/a | n/a | 1.98 |

## Macro Metrics On The Four Shared Examples

Higher is better for BLEU, chrF, ROUGE-L, METEOR and BERTScore F1. Lower is
better for TER.

| Variant | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 |
|---|---:|---:|---:|---:|---:|---:|
| `full_system_flash` | 0.5485 | 0.6540 | 0.5841 | 0.6588 | 0.6806 | 0.9461 |
| `raw_generic_flash` | 0.2964 | 0.5000 | 1.8733 | 0.4951 | 0.5289 | 0.9225 |
| `full_system_pro` | 0.4623 | 0.6449 | 0.5752 | 0.6926 | 0.6629 | 0.9420 |
| `raw_generic_pro` | 0.3920 | 0.6334 | 0.7545 | 0.5804 | 0.6394 | 0.9380 |

## Main Observations

### 1. The architecture helps under both model settings

Under flash, the full workflow beats the raw-generic flash baseline on all six
macro metrics in the four-example subset.

Under pro, the full workflow also beats the raw-generic pro baseline on all six
macro metrics.

This is the strongest dissertation point from this run:

```text
The architecture advantage is visible even when the raw baseline is upgraded
to a stronger model.
```

### 2. Raw pro improves substantially over raw flash

The raw baseline benefits strongly from the model upgrade:

| Metric | Raw flash | Raw pro | Direction |
|---|---:|---:|---|
| BLEU | 0.2964 | 0.3920 | improves |
| chrF | 0.5000 | 0.6334 | improves |
| TER | 1.8733 | 0.7545 | improves |
| ROUGE-L | 0.4951 | 0.5804 | improves |
| METEOR | 0.5289 | 0.6394 | improves |
| BERTScore F1 | 0.9225 | 0.9380 | improves |

This is useful because it shows that model quality matters. The raw baseline is
not weak by construction; when given a stronger model, it becomes much more
competitive.

### 3. Full-system pro is not uniformly better than full-system flash

The full workflow's model upgrade is mixed:

| Metric | Full flash | Full pro | Better |
|---|---:|---:|---|
| BLEU | 0.5485 | 0.4623 | Flash |
| chrF | 0.6540 | 0.6449 | Flash |
| TER | 0.5841 | 0.5752 | Pro |
| ROUGE-L | 0.6588 | 0.6926 | Pro |
| METEOR | 0.6806 | 0.6629 | Flash |
| BERTScore F1 | 0.9461 | 0.9420 | Flash |

This should be stated carefully. A stronger model does not automatically produce
better benchmark fit inside the workflow. The pro model sometimes uses different
wording or preserves source formatting in a way that hurts reference overlap.

This is valuable because it avoids a simplistic "bigger model is always better"
claim.

### 4. ToTTo remains the clearest architecture win

For `totto-validation-204`, the full workflow output was:

```text
Ma Ying-jeou received 58.45% of the vote.
```

The raw-generic pro baseline output was:

```text
The highlighted cell shows that Vincent Siew received 58.45% of the vote.
```

This is the same subject-linking error seen earlier with the raw baseline. It is
especially important because the raw model was upgraded to v4-pro and still made
the mistake. The workflow, both flash and pro, correctly connects the highlighted
percentage to the page/table subject and produces the intended proposition.

Suggested dissertation wording:

```text
The ToTTo example shows a qualitative advantage that is not merely a model-size
effect. Even the raw v4-pro baseline verbalised the highlighted value as
belonging to Vincent Siew, whereas the workflow linked the value to Ma
Ying-jeou, matching the reference proposition. This supports the role of input
structure interpretation and task-aware evidence selection in the architecture.
```

### 5. WebNLG shows that pro can be less reference-like

For `web_nlg_en-test-51`, the flash workflow produced:

```text
The ALCO RS-3 has a four-stroke engine, 12 cylinders, and a length of 17068.8
millimetres.
```

The pro workflow produced:

```text
ALCO_RS-3 has a Four-stroke engine, 12 cylinders, and a length of 17068.8
(millimetres).
```

Both are factually recoverable, but the pro wording is less close to the human
references because it preserves the underscore, capitalises `Four-stroke`, and
places the unit in parentheses. This explains why `full_system_pro` scores lower
than `full_system_flash` on several WebNLG overlap metrics.

This gives a useful caveat for the dissertation:

```text
Model upgrades can change realisation style in ways that improve reasoning but
hurt reference-overlap metrics.
```

## Per-Example Graph Data

This table is suitable for grouped bar charts.

| Dataset | Example | Variant | BLEU | chrF | TER | ROUGE-L | METEOR | BERTScore F1 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `dart` | `dart-test-53` | `full_system_flash` | 0.1740 | 0.4445 | 1.2500 | 0.4167 | 0.5628 | 0.9172 |
| `dart` | `dart-test-53` | `raw_generic_flash` | 0.0605 | 0.3273 | 1.7500 | 0.3704 | 0.4180 | 0.9015 |
| `dart` | `dart-test-53` | `full_system_pro` | 0.1956 | 0.5662 | 1.2500 | 0.4167 | 0.5628 | 0.9264 |
| `dart` | `dart-test-53` | `raw_generic_pro` | 0.1821 | 0.5551 | 1.3750 | 0.4000 | 0.5563 | 0.9151 |
| `e2e_nlg` | `e2e_nlg-test-51` | `full_system_flash` | 0.8690 | 0.8696 | 0.3529 | 0.7222 | 0.8323 | 0.9700 |
| `e2e_nlg` | `e2e_nlg-test-51` | `raw_generic_flash` | 0.7004 | 0.8223 | 0.1765 | 0.7568 | 0.9331 | 0.9730 |
| `e2e_nlg` | `e2e_nlg-test-51` | `full_system_pro` | 0.9071 | 0.8859 | 0.1176 | 0.8889 | 0.9418 | 0.9776 |
| `e2e_nlg` | `e2e_nlg-test-51` | `raw_generic_pro` | 0.7938 | 0.8483 | 0.1765 | 0.8000 | 0.8909 | 0.9778 |
| `totto` | `totto-validation-204` | `full_system_flash` | 0.4888 | 0.4966 | 0.4000 | 0.6316 | 0.5500 | 0.9115 |
| `totto` | `totto-validation-204` | `raw_generic_flash` | 0.0190 | 0.1845 | 4.9000 | 0.1351 | 0.1656 | 0.8519 |
| `totto` | `totto-validation-204` | `full_system_pro` | 0.4888 | 0.4966 | 0.4000 | 0.6316 | 0.5500 | 0.9115 |
| `totto` | `totto-validation-204` | `raw_generic_pro` | 0.3499 | 0.4503 | 0.8000 | 0.5217 | 0.5204 | 0.9079 |
| `web_nlg` | `web_nlg_en-test-51` | `full_system_flash` | 0.6622 | 0.8052 | 0.3333 | 0.8649 | 0.7774 | 0.9858 |
| `web_nlg` | `web_nlg_en-test-51` | `raw_generic_flash` | 0.4056 | 0.6659 | 0.6667 | 0.7179 | 0.5988 | 0.9635 |
| `web_nlg` | `web_nlg_en-test-51` | `full_system_pro` | 0.2576 | 0.6311 | 0.5333 | 0.8333 | 0.5971 | 0.9525 |
| `web_nlg` | `web_nlg_en-test-51` | `raw_generic_pro` | 0.2422 | 0.6796 | 0.6667 | 0.6000 | 0.5900 | 0.9512 |

## Recommended Graphs

1. Architecture effect by model:

   ```text
   full_system_flash - raw_generic_flash
   full_system_pro - raw_generic_pro
   ```

2. Model upgrade effect by architecture:

   ```text
   full_system_pro - full_system_flash
   raw_generic_pro - raw_generic_flash
   ```

3. Runtime comparison:

   ```text
   full_system_flash
   raw_generic_flash
   full_system_pro
   raw_generic_pro
   ```

4. ToTTo qualitative case:

   Show the full workflow output and raw-pro output side by side to demonstrate
   the subject-linking error.

5. WebNLG style caveat:

   Show the flash and pro workflow outputs side by side to demonstrate that a
   stronger model can produce less reference-like surface form.

## Dissertation-Level Conclusion

The pro comparison strengthens the dissertation story in three ways.

First, it shows that the architecture advantage is not limited to weak raw
baselines. On the four shared non-SportSett examples, `full_system_pro` beats
`raw_generic_pro` on the macro metrics.

Second, it shows that raw model strength matters. `raw_generic_pro` is much
stronger than `raw_generic_flash`, so the raw baseline should be treated as a
serious competitor rather than a strawman.

Third, it shows that model strength is not the same as task success. In ToTTo,
raw v4-pro still misassigns the highlighted value to Vincent Siew, while the
workflow resolves the intended subject. In WebNLG, pro changes surface form in a
way that reduces reference overlap. These cases support the argument that
structured interpretation, evidence selection and controlled realisation remain
important even when the underlying language model is strong.

Suggested dissertation wording:

```text
The model-strength comparison separated architecture effects from model effects.
Upgrading the raw baseline from v4-flash to v4-pro substantially improved raw
performance, but the full workflow with v4-pro still outperformed the raw v4-pro
baseline on the four-example macro comparison. At the same time, the full
workflow with v4-pro did not universally outperform the flash workflow, showing
that stronger models can alter realisation style in ways that do not always
improve reference-overlap metrics. The ToTTo case is especially informative:
even raw v4-pro attached the highlighted vote percentage to the wrong entity,
while the workflow preserved the intended subject relation.
```

## Caveats

- This pro comparison contains four non-SportSett examples plus the separate
  SportSett pro case, not a full 25-example pro run.
- Each example was generated once, so the results should be treated as
  descriptive case-study evidence rather than a statistical estimate.
- Reference-overlap metrics can reward surface similarity over factual
  disambiguation. The ToTTo example should therefore be discussed with an eye
  test, not only with automatic scores.
- Runtime comparisons are sensitive to API latency, provider load and retry
  behaviour.
