# Protected Holdout Execution Report

- Experiment: `protected_holdout_full_system_flash_25`
- Selection timestamp: `2026-08-21T00:28:22.944030+00:00`
- Frozen implementation: `f525ca0c932819f533eab9229752a055a8e9c1acef8dea420bfa7e1e8b6b91fb`
- Git commit: `4a333a76702e6c056d8364dc212ce360d3fb1b92`
- Configuration: `evaluation/protected_holdout_full_system/config/protected_full_system_flash.json`
- Configuration SHA-256: `1fe2242bf777f26ada83114301c7c1fc11b6c25f613fa9d42e0b9484e4555d85`
- Model for all six roles: `deepseek:deepseek-v4-flash`
- Status: `complete`
- Completion: `{'successful': 25, 'failed': 0, 'not_started': 0}`
- References available during generation: `No`

## Run Summary

| Dataset | Example | Outcome | Path | Release | Support | Words | Tokens | Seconds |
|---|---|---|---|---|---:|---:|---:|---:|
| e2e_nlg | e2e_nlg-test-1330 | success | normal_llm_writer | approved_with_warnings | 1.0 | 26 | 7778 | 25.8 |
| web_nlg | web_nlg_en-test-1209 | success | normal_llm_writer | approved_with_warnings | 1.0 | 24 | 6806 | 12.7 |
| dart | dart-test-1791 | success | normal_llm_writer | approved_with_warnings | 1.0 | 20 | 6290 | 9.8 |
| totto | totto-validation-1828 | success | deterministic_fallback | approved_with_warnings | 1.0 | 25 | 8801 | 23.2 |
| sportsett_basketball | 5130 | success | deterministic_fallback | approved | 1.0 | 299 | 514250 | 763.1 |
| e2e_nlg | e2e_nlg-test-209 | success | normal_llm_writer | approved_with_warnings | 1.0 | 10 | 6071 | 6.0 |
| web_nlg | web_nlg_en-test-1330 | success | normal_llm_writer | approved_with_warnings | 1.0 | 28 | 12413 | 9.3 |
| dart | dart-test-1805 | success | normal_llm_writer | approved_with_warnings | 1.0 | 14 | 6855 | 12.4 |
| totto | totto-validation-4467 | success | normal_llm_writer | approved_with_warnings | 1.0 | 18 | 14915 | 11.0 |
| sportsett_basketball | 5372 | success | auditor_repaired | approved | 1.0 | 330 | 813172 | 1398.0 |
| e2e_nlg | e2e_nlg-test-447 | success | normal_llm_writer | approved_with_warnings | 1.0 | 19 | 6506 | 10.4 |
| web_nlg | web_nlg_en-test-1466 | success | normal_llm_writer | approved_with_warnings | 1.0 | 10 | 5945 | 6.7 |
| dart | dart-test-1828 | success | normal_llm_writer | approved_with_warnings | 1.0 | 20 | 6637 | 9.9 |
| totto | totto-validation-6067 | success | normal_llm_writer | approved_with_warnings | 1.0 | 10 | 6949 | 7.6 |
| sportsett_basketball | 5786 | success | deterministic_fallback | approved | 1.0 | 298 | 514434 | 840.3 |
| e2e_nlg | e2e_nlg-test-476 | success | normal_llm_writer | approved_with_warnings | 1.0 | 26 | 6226 | 6.5 |
| web_nlg | web_nlg_en-test-859 | success | normal_llm_writer | approved_with_warnings | 1.0 | 6 | 12420 | 17.5 |
| dart | dart-test-2278 | success | normal_llm_writer | approved | 1.0 | 44 | 7197 | 14.0 |
| totto | totto-validation-839 | success | normal_llm_writer | approved_with_warnings | 1.0 | 18 | 8013 | 15.4 |
| sportsett_basketball | 5955 | success | auditor_repaired | approved_with_warnings | 1.0 | 219 | 684034 | 952.5 |
| e2e_nlg | e2e_nlg-test-864 | success | normal_llm_writer | approved_with_warnings | 1.0 | 9 | 13469 | 28.0 |
| web_nlg | web_nlg_en-test-864 | success | normal_llm_writer | approved_with_warnings | 1.0 | 14 | 6415 | 9.6 |
| dart | dart-test-4597 | success | normal_llm_writer | approved_with_warnings | 1.0 | 31 | 7155 | 11.4 |
| totto | totto-validation-912 | success | normal_llm_writer | approved_with_warnings | 1.0 | 22 | 7703 | 9.3 |
| sportsett_basketball | 6127 | success | normal_llm_writer | approved | 1.0 | 313 | 609511 | 1203.4 |

## Provider-Reported Usage by Stage

| Stage | Input tokens | Output tokens | Total tokens | Requests |
|---|---:|---:|---:|---:|
| initial_audit_and_repair | 469044 | 56394 | 525438 | 5 |
| verifier.insight_verification | 378114 | 59769 | 437883 | 5 |
| fact_verification | 271806 | 86035 | 357841 | 5 |
| evidence_synthesis | 272155 | 59876 | 332031 | 5 |
| data_understanding | 131494 | 172117 | 303611 | 8 |
| evidence.insight_synthesis | 209997 | 61768 | 271765 | 5 |
| natural_writer | 222889 | 43786 | 266675 | 26 |
| writer_quality_revision | 201524 | 47081 | 248605 | 4 |
| post_repair_audit_round_1 | 186421 | 17607 | 204028 | 2 |
| verifier.insight_verification.retry.002 | 89128 | 14192 | 103320 | 6 |
| verifier.insight_verification.retry.003 | 64918 | 9572 | 74490 | 5 |
| verifier.insight_verification.retry.001 | 58131 | 9620 | 67751 | 6 |
| verifier.insight_verification.retry.004 | 44127 | 10422 | 54549 | 3 |
| verifier.insight_verification.retry.007 | 20229 | 1087 | 21316 | 1 |
| verifier.insight_verification.retry.005 | 10583 | 6602 | 17185 | 2 |
| verifier.insight_verification.retry.006 | 11575 | 1902 | 13477 | 1 |

## Artifact Locations

- Batch manifest: `evaluation/protected_holdout_full_system/results/protected_batch_manifest.json`
- Exact outputs and run summaries: `evaluation/protected_holdout_full_system/results/protected_generation_summary.jsonl`
- Sentence support: `evaluation/protected_holdout_full_system/results/sentence_support_mappings.jsonl`
- Stage usage: `evaluation/protected_holdout_full_system/results/stage_token_usage.csv`
- Run checksums: `evaluation/protected_holdout_full_system/results/run_artifact_indexes.jsonl`
- Progress log: `evaluation/protected_holdout_full_system/results/protected_progress.log`
