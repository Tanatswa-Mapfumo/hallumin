from __future__ import annotations

import ast
import json
import re
from pathlib import Path


SOURCE_PATH = Path(__file__).with_name(
    "protected_holdout_full_system_evaluation.py"
)
TARGET_PATH = SOURCE_PATH.with_suffix(".ipynb")


def markdown_source(body: str) -> list[str]:
    lines: list[str] = []
    for line in body.splitlines(keepends=True):
        if line.startswith("# "):
            lines.append(line[2:])
        elif line.startswith("#"):
            lines.append(line[1:])
        else:
            lines.append(line)
    return "".join(lines).splitlines(keepends=True)


def main() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^# %%([^\n]*)\n", source)
    cells: list[dict[str, object]] = []

    for cell_number, index in enumerate(range(1, len(parts), 2), start=1):
        marker = parts[index].strip()
        body = parts[index + 1]
        if "[markdown]" in marker:
            cells.append(
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": markdown_source(body),
                }
            )
            continue

        compile(
            body,
            f"{SOURCE_PATH}:cell-{cell_number}",
            "exec",
            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )
        cells.append(
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": body.splitlines(keepends=True),
            }
        )

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11",
                "mimetype": "text/x-python",
                "codemirror_mode": {"name": "ipython", "version": 3},
                "pygments_lexer": "ipython3",
                "nbconvert_exporter": "python",
                "file_extension": ".py",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    TARGET_PATH.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {TARGET_PATH} with {len(cells)} cells.")


if __name__ == "__main__":
    main()
