from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
MAIN_PROJECT = PROJECT_ROOT / "table2text_pydanticai"
EXPERIMENT = PROJECT_ROOT / "experiments/llm_only_pipeline"
BUILD_DIR = SCRIPT_DIR / "build"
GENERATED_DIR = BUILD_DIR / "generated"
OUTPUT_PDF = SCRIPT_DIR / "MScProject_Program_Listings.pdf"


DATA_SHARDS = [
    MAIN_PROJECT
    / "evaluation/protected_holdout_full_system/prepared/shards"
    / filename
    for filename in (
        "e2e_nlg__e2e_nlg-test-1330.jsonl",
        "e2e_nlg__e2e_nlg-test-209.jsonl",
        "e2e_nlg__e2e_nlg-test-447.jsonl",
        "e2e_nlg__e2e_nlg-test-476.jsonl",
        "e2e_nlg__e2e_nlg-test-864.jsonl",
        "totto__totto-validation-1828.jsonl",
        "totto__totto-validation-4467.jsonl",
        "totto__totto-validation-6067.jsonl",
        "totto__totto-validation-839.jsonl",
        "totto__totto-validation-912.jsonl",
        "web_nlg__web_nlg_en-test-1209.jsonl",
        "web_nlg__web_nlg_en-test-1330.jsonl",
        "web_nlg__web_nlg_en-test-1466.jsonl",
        "web_nlg__web_nlg_en-test-859.jsonl",
        "web_nlg__web_nlg_en-test-864.jsonl",
        "dart__dart-test-1791.jsonl",
        "dart__dart-test-1805.jsonl",
        "dart__dart-test-1828.jsonl",
        "dart__dart-test-2278.jsonl",
        "dart__dart-test-4597.jsonl",
        "sportsett_basketball__5130.jsonl",
        "sportsett_basketball__5372.jsonl",
        "sportsett_basketball__5786.jsonl",
        "sportsett_basketball__5955.jsonl",
        "sportsett_basketball__6127.jsonl",
    )
]


RESULT_FILES = [
    MAIN_PROJECT
    / "evaluation/protected_holdout_full_system/results/protected_generation_summary.csv",
    MAIN_PROJECT
    / "evaluation/protected_holdout_baseline/results/automatic_metrics_overall.csv",
    MAIN_PROJECT
    / "evaluation/protected_holdout_baseline/results/automatic_metrics_by_dataset.csv",
    MAIN_PROJECT
    / "evaluation/protected_holdout_baseline/gpt56_judge/results/gpt56_annotation_summary.csv",
    MAIN_PROJECT
    / "evaluation/protected_holdout_baseline/gpt56_judge/results/gpt56_category_counts.csv",
]


CONFIG_FILES = [
    MAIN_PROJECT / "pyproject.toml",
    MAIN_PROJECT / ".env.example",
    MAIN_PROJECT / "evaluation/config/datasets.json",
    MAIN_PROJECT / "evaluation/config/metrics.json",
    MAIN_PROJECT / "evaluation/config/metrics_reference_similarity.json",
    MAIN_PROJECT / "evaluation/config/metrics_source_grounded.json",
    MAIN_PROJECT / "evaluation/config/variants.json",
    MAIN_PROJECT / "evaluation/config/variants_ablation.json",
    MAIN_PROJECT / "evaluation/config/variants_raw_deepseek_v4_flash.json",
    MAIN_PROJECT / "evaluation/config/variants_raw_deepseek_v4_pro.json",
    MAIN_PROJECT
    / "evaluation/protected_holdout_full_system/config/protected_full_system_flash.json",
    EXPERIMENT / "pyproject.toml",
    EXPERIMENT / ".env.example",
    EXPERIMENT / "config/variants.json",
]


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    return sorted(set(paths), key=lambda path: path.relative_to(PROJECT_ROOT).as_posix())


def program_files() -> list[Path]:
    paths: list[Path] = []
    paths.extend((MAIN_PROJECT / "src").rglob("*.py"))
    paths.extend((MAIN_PROJECT / "evaluation/scripts").rglob("*.py"))
    paths.extend((MAIN_PROJECT / "evaluation/notebooks").glob("*.py"))
    paths.extend((EXPERIMENT / "src").rglob("*.py"))
    paths.append(Path(__file__).resolve())
    return unique_paths(paths)


def test_files() -> list[Path]:
    return unique_paths(
        [
            *(MAIN_PROJECT / "tests").rglob("*.py"),
            *(EXPERIMENT / "tests").rglob("*.py"),
        ]
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def write_pretty_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_protected_data_listings() -> list[Path]:
    output_paths = []
    for path in DATA_SHARDS:
        for record in read_jsonl(path):
            payload = {
                "dataset_id": record["dataset_id"],
                "example_id": record["example_id"],
                "task_family": record["task_family"],
                "output_mode": record["output_mode"],
                "language": record["language"],
                "request": record["request"],
                "source_payload": record.get("source_payload"),
                "parent_table": record.get("parent_table"),
                "references": record.get("references", []),
                "source_sha256": record.get("source_sha256"),
                "reference_sha256": record.get("reference_sha256"),
            }
            safe_id = str(record["example_id"]).replace("/", "_")
            output = GENERATED_DIR / "data" / f"{record['dataset_id']}__{safe_id}.json"
            write_pretty_json(output, payload)
            output_paths.append(output)
    output_paths = unique_paths(output_paths)
    if len(output_paths) != 25:
        raise RuntimeError(
            f"Expected 25 protected examples, found {len(output_paths)}"
        )
    return output_paths


def build_paired_output_listing() -> Path:
    source = (
        MAIN_PROJECT
        / "evaluation/protected_holdout_baseline/comparison/full_system_and_baseline_sealed.jsonl"
    )
    grouped: dict[tuple[str, str], dict[str, Any]] = defaultdict(dict)
    for record in read_jsonl(source):
        key = (record["dataset_id"], str(record["example_id"]))
        condition = "full_system" if record["variant_id"] == "full_system" else "baseline"
        grouped[key][condition] = {
            "generated_text": record["generated_text"],
            "release_status": record.get("release_status"),
            "writer_mode": record.get("writer_mode"),
            "primary_evaluation_eligible": record.get("primary_evaluation_eligible"),
        }
        grouped[key]["dataset_id"] = record["dataset_id"]
        grouped[key]["example_id"] = str(record["example_id"])
        grouped[key]["task_family"] = record["task_family"]
        grouped[key]["request"] = record["request"]
        grouped[key]["references"] = record.get("references", [])

    records = [grouped[key] for key in sorted(grouped)]
    if len(records) != 25 or any(
        "full_system" not in record or "baseline" not in record for record in records
    ):
        raise RuntimeError("The paired protected output file is incomplete.")
    output = GENERATED_DIR / "protected_holdout_25_paired_outputs.json"
    write_pretty_json(output, records)
    return output


def copy_result_files() -> list[Path]:
    output_paths = []
    for source in RESULT_FILES:
        destination = GENERATED_DIR / "results" / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        output_paths.append(destination)
    return output_paths


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def listing_language(path: Path) -> str:
    return {
        ".py": "Python",
        ".json": "json",
        ".jsonl": "json",
        ".csv": "",
        ".toml": "",
        ".example": "",
    }.get(path.suffix, "")


def listing_command(identifier: str, caption: str, path: Path) -> str:
    relative_path = Path(os.path.relpath(path, BUILD_DIR)).as_posix()
    language = listing_language(path)
    language_option = f"language={language}," if language else ""
    return (
        f"\\lstinputlisting[{language_option}"
        f"caption={{{latex_escape(identifier + ': ' + caption)}}},"
        f"label={{lst:{identifier.lower()}}}]"
        f"{{{relative_path}}}"
    )


def file_caption(path: Path) -> str:
    relative = path.relative_to(PROJECT_ROOT).as_posix()
    return relative


def build_manifest(
    programs: list[Path],
    tests: list[Path],
    configs: list[Path],
    data: list[Path],
    results: list[Path],
) -> Path:
    records = []
    for category, paths in (
        ("program", programs),
        ("test", tests),
        ("configuration", configs),
        ("data", data),
        ("result", results),
    ):
        for path in paths:
            records.append(
                {
                    "category": category,
                    "path": (
                        path.relative_to(PROJECT_ROOT).as_posix()
                        if path.is_relative_to(PROJECT_ROOT)
                        else path.relative_to(SCRIPT_DIR).as_posix()
                    ),
                    "lines": len(path.read_text(encoding="utf-8").splitlines()),
                    "sha256": sha256(path),
                }
            )
    output = GENERATED_DIR / "listing_manifest.json"
    write_pretty_json(output, records)
    return output


def render_tex(
    programs: list[Path],
    tests: list[Path],
    configs: list[Path],
    data: list[Path],
    results: list[Path],
    manifest: Path,
) -> str:
    sections: list[str] = []

    def add_section(title: str, prefix: str, files: list[Path], description: str) -> None:
        sections.extend(
            [
                "\\clearpage",
                f"\\section{{{latex_escape(title)}}}",
                description,
            ]
        )
        for index, path in enumerate(files, start=1):
            identifier = f"{prefix}{index:02d}"
            sections.append(listing_command(identifier, file_caption(path), path))

    add_section(
        "Program Listings",
        "P",
        programs,
        "Maintained runtime, evaluation, notebook-companion and experimental programs.",
    )
    add_section(
        "Test Program Listings",
        "T",
        tests,
        "Automated test programs for the main system and the isolated LLM-only experiment.",
    )
    add_section(
        "Configuration Listings",
        "C",
        configs,
        "Reproducibility configuration. Environment examples contain placeholders only; no secrets are included.",
    )
    add_section(
        "Protected Data Listings",
        "D",
        data,
        "All 25 protected-holdout inputs, grouped across five datasets and "
        "formatted as readable JSON. Where the benchmark stores both a "
        "structured payload and a duplicate serialized source-text field, this "
        "appendix displays the complete structured payload once.",
    )
    add_section(
        "Evaluation Result Listings",
        "R",
        results,
        "Paired Full System/Baseline outputs and the principal protected-holdout result tables.",
    )
    sections.extend(
        [
            "\\clearpage",
            "\\section{Listing Manifest}",
            "This machine-readable manifest records the category, path, line count and SHA-256 digest of every included listing.",
            listing_command("M01", "Program-listing inclusion manifest", manifest),
        ]
    )

    total_source_lines = sum(
        len(path.read_text(encoding="utf-8").splitlines()) for path in programs
    )
    total_test_lines = sum(
        len(path.read_text(encoding="utf-8").splitlines()) for path in tests
    )

    return r"""\documentclass[a4paper,10pt]{article}
\usepackage[top=16mm,bottom=17mm,left=16mm,right=14mm,headheight=14pt]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{microtype}

\setmainfont{Times New Roman}
\setmonofont{Menlo}
\definecolor{codeblue}{HTML}{154A8A}
\definecolor{codegreen}{HTML}{176B3A}
\definecolor{codered}{HTML}{9A2D25}
\definecolor{linegray}{HTML}{707070}
\definecolor{framegray}{HTML}{D5D9DE}
\definecolor{shade}{HTML}{F7F8FA}

\lstdefinelanguage{json}{
  basicstyle=\ttfamily\fontsize{7.1}{8.2}\selectfont,
  string=[s]{\"}{\"},
  stringstyle=\color{codegreen},
  comment=[l]{//},
  commentstyle=\color{linegray},
  morecomment=[s]{/*}{*/},
  literate=
   *{0}{{{\color{codered}0}}}{1}
    {1}{{{\color{codered}1}}}{1}
    {2}{{{\color{codered}2}}}{1}
    {3}{{{\color{codered}3}}}{1}
    {4}{{{\color{codered}4}}}{1}
    {5}{{{\color{codered}5}}}{1}
    {6}{{{\color{codered}6}}}{1}
    {7}{{{\color{codered}7}}}{1}
    {8}{{{\color{codered}8}}}{1}
    {9}{{{\color{codered}9}}}{1}
}

\lstset{
  basicstyle=\ttfamily\fontsize{7.1}{8.2}\selectfont,
  keywordstyle=\bfseries\color{codeblue},
  stringstyle=\color{codegreen},
  commentstyle=\itshape\color{linegray},
  identifierstyle=\color{black},
  numbers=left,
  numberstyle=\ttfamily\fontsize{5.8}{6.5}\selectfont\color{linegray},
  numbersep=7pt,
  frame=single,
  rulecolor=\color{framegray},
  backgroundcolor=\color{shade},
  breaklines=true,
  breakatwhitespace=false,
  showstringspaces=false,
  keepspaces=true,
  columns=fullflexible,
  tabsize=4,
  captionpos=t,
  aboveskip=1.2em,
  belowskip=1.5em,
  inputencoding=utf8,
}

\hypersetup{colorlinks=true,linkcolor=codeblue,urlcolor=codeblue,pdftitle={MScProject Program Listings}}
\pagestyle{fancy}
\fancyhf{}
\lhead{MScProject Program Listings}
\rhead{Evidence-grounded Table-to-Text Generation}
\cfoot{\thepage}
\setcounter{tocdepth}{1}

\title{MScProject\\Program, Test, Data and Result Listings}
\author{Tanatswa}
\date{21 August 2026}

\begin{document}
\maketitle

\section*{Purpose and Scope}
This PDF is the readable program-listing submission for the MScProject on evidence-grounded table-to-text generation. Its source repository is available at \href{https://github.com/tboysavage/MScProject}{github.com/tboysavage/MScProject}. The document includes maintained programs, automated tests, reproducibility configuration, all 25 protected-holdout inputs, all 25 paired system/baseline outputs, and principal evaluation tables. The final manifest supplies file-level SHA-256 digests for the exact listed snapshot.

The listings exclude credentials, local environments, downloaded datasets, caches, transient run directories and duplicated frozen source snapshots. Jupyter notebooks are represented by their maintained Python companion programs because raw notebook JSON is not readable as a program listing.

\begin{center}
\begin{tabular}{lrr}
\toprule
Category & Files & Source lines \\
\midrule
Programs & PROGRAM_COUNT & PROGRAM_LINES \\
Tests & TEST_COUNT & TEST_LINES \\
Configuration & CONFIG_COUNT & -- \\
Protected data & DATA_COUNT & 25 examples \\
Evaluation results & RESULT_COUNT & 25 paired outputs plus tables \\
\bottomrule
\end{tabular}
\end{center}

\section*{Listing Labels}
\begin{description}
\item[P] Program or executable research-support module.
\item[T] Automated test program.
\item[C] Reproducibility configuration.
\item[D] Protected-holdout data.
\item[R] Evaluation result.
\item[M] Machine-readable inclusion manifest.
\end{description}

\tableofcontents
\clearpage
\lstlistoflistings

SECTIONS

\end{document}
""".replace("PROGRAM_COUNT", str(len(programs))).replace(
        "PROGRAM_LINES", f"{total_source_lines:,}"
    ).replace("TEST_COUNT", str(len(tests))).replace(
        "TEST_LINES", f"{total_test_lines:,}"
    ).replace("CONFIG_COUNT", str(len(configs))).replace(
        "DATA_COUNT", str(len(data))
    ).replace("RESULT_COUNT", str(len(results))).replace(
        "SECTIONS", "\n\n".join(sections)
    )


def validate_inputs(paths: Iterable[Path]) -> None:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Required listing inputs are missing:\n{formatted}")


def build_pdf(*, compile_pdf: bool = True) -> Path:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    programs = program_files()
    tests = test_files()
    configs = unique_paths(CONFIG_FILES)
    validate_inputs([*programs, *tests, *configs, *DATA_SHARDS, *RESULT_FILES])

    data_files = build_protected_data_listings()
    paired_outputs = build_paired_output_listing()
    result_files = [paired_outputs, *copy_result_files()]
    manifest = build_manifest(programs, tests, configs, data_files, result_files)

    tex_path = BUILD_DIR / "program_listings.tex"
    tex_path.write_text(
        render_tex(programs, tests, configs, data_files, result_files, manifest),
        encoding="utf-8",
    )
    print(f"Programs: {len(programs)}")
    print(f"Tests: {len(tests)}")
    print("Protected examples: 25")
    print("Paired output examples: 25")
    print(f"LaTeX: {tex_path}")

    if not compile_pdf:
        return tex_path

    log_path = BUILD_DIR / "xelatex.log"
    for pass_number in (1, 2, 3):
        print(f"XeLaTeX pass {pass_number}/3...")
        with log_path.open("a" if pass_number > 1 else "w", encoding="utf-8") as log:
            result = subprocess.run(
                [
                    "xelatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    tex_path.name,
                ],
                cwd=BUILD_DIR,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        if result.returncode:
            tail = "\n".join(log_path.read_text(encoding="utf-8").splitlines()[-30:])
            raise RuntimeError(f"XeLaTeX pass {pass_number} failed:\n{tail}")
    shutil.copy2(BUILD_DIR / "program_listings.pdf", OUTPUT_PDF)
    print(f"PDF: {OUTPUT_PDF}")
    return OUTPUT_PDF


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-compile",
        action="store_true",
        help="Generate staged listings and LaTeX without invoking XeLaTeX.",
    )
    args = parser.parse_args()
    build_pdf(compile_pdf=not args.no_compile)


if __name__ == "__main__":
    main()
