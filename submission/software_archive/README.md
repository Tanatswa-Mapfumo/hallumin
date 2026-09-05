# Software Submission Builder

This directory builds the compressed MScProject software submission. The
resulting archive contains:

- a one-page program description in PDF and Markdown;
- installation, build, execution, and test instructions;
- supported dependency ranges and the exact versions used for verification;
- maintained source code, tests, notebooks, configuration, and curated results;
- a Python wheel exposing the `table2text` and `table2text-evaluate` commands;
- a deterministic sample input and runnable demonstration;
- SHA-256 checksums for every archived file.

Credentials, `.env` files, virtual environments, caches, transient run
directories, and the duplicate protected-holdout source snapshot are excluded.

## Build

From the repository root, using the project virtual environment:

```bash
table2text_pydanticai/.venv/bin/python \
  submission/software_archive/build_software_submission.py
```

The builder requires `reportlab` to generate the one-page PDF and a functioning
Python packaging toolchain to build the wheel. Temporary files are written to
`submission/software_archive/build/`.

The final artifact is:

```text
submission/software_archive/Tanatswa_Mapfumo Source_Code.zip
```
