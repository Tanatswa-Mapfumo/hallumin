# Reproducible evaluation notebooks

- `protected_holdout_full_system_evaluation.ipynb` runs the sealed 25-example full-system evaluation.
- `task_aware_direct_baseline_evaluation.ipynb` runs the matched task-aware direct baseline study.
- `dissertation_visual_evaluations.ipynb` recreates dissertation figures from stored metrics.

The matching `.py` files are notebook source files using `# %%` cell markers.
The `build_*_notebook.py` scripts regenerate clean notebook JSON. Existing
executed notebooks are retained as research evidence; regeneration creates an
unexecuted copy from the corresponding source.
