# Evaluation workspace

The evaluation framework code is installed from `src/table2text/evaluation/`.
This directory stores configuration, notebooks, scripts, and research
artifacts.

| Path | Purpose |
| --- | --- |
| `config/` | Canonical configuration plus archived experiment-specific snapshots. |
| `notebooks/` | Reproducible protected-holdout, baseline, and visualisation notebooks. |
| `scripts/` | Report, annotation, and figure artifact builders. |
| `protected_holdout_full_system/` | Immutable full-system holdout record. |
| `protected_holdout_baseline/` | Immutable paired baseline and metric record. |
| `task_aware_direct_baseline/` | Three-condition prompt-asymmetry experiment. |
| `prepared/`, `generations/`, `results/` | Local generated artifacts; ignored by default. |

Do not move or rewrite the protected-holdout directories: their manifests
record internal paths and file hashes.
