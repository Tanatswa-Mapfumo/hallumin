# Program Listings PDF

This directory adapts the University of Aberdeen `abdn-code` LaTeX template to
the MScProject repository.

The generated PDF clearly separates:

- maintained production and evaluation programs (`P` listings);
- automated test programs (`T` listings);
- reproducibility configuration (`C` listings);
- all 25 protected-holdout source examples (`D` listings);
- all paired Full System/Baseline outputs and principal result tables (`R` listings).

Notebook source is represented by the maintained Python companion files rather
than unreadable `.ipynb` JSON. Secrets, local environments, downloaded source
datasets, caches, transient runs, and duplicated frozen source snapshots are
excluded.

## Build

From the repository root:

```bash
python3 submission/program_listings/build_program_listings.py
```

The build requires `xelatex`. It writes temporary files under `build/` and the
submission artifact to:

```text
submission/program_listings/Tanatswa Mapfumo Project Code Printout.pdf
```
