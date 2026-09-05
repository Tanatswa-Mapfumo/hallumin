"""Build the examiner-facing MScProject software submission archive."""

from __future__ import annotations

import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
PACKAGE_DIR = PROJECT_ROOT / "table2text_pydanticai"
BUILD_DIR = SCRIPT_DIR / "build"
STAGE_PARENT = BUILD_DIR / "stage"
ARCHIVE_ROOT_NAME = "Tanatswa_Mapfumo_MScProject_Software_Submission"
STAGE_ROOT = STAGE_PARENT / ARCHIVE_ROOT_NAME
OUTPUT_ARCHIVE = SCRIPT_DIR / "Tanatswa_Mapfumo Source_Code.zip"
OUTPUT_CHECKSUM = SCRIPT_DIR / f"{OUTPUT_ARCHIVE.name}.sha256"

SOURCE_EXCLUDED_PREFIXES = (
    "submission/",
    "table2text_pydanticai/evaluation/protected_holdout_full_system/"
    "frozen_code_snapshot/",
)

SUBMISSION_DOCUMENTS = {
    "ARCHIVE_README.md": "README.md",
    "PROGRAM_DESCRIPTION.md": "PROGRAM_DESCRIPTION.md",
    "INSTALLATION_AND_BUILD.md": "INSTALLATION_AND_BUILD.md",
    "DEPENDENCIES.md": "DEPENDENCIES.md",
    "VERIFICATION.md": "VERIFICATION.md",
    "requirements-tested.txt": "requirements-tested.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def tracked_source_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    relative_paths = [
        Path(item.decode("utf-8"))
        for item in completed.stdout.split(b"\0")
        if item
    ]
    selected: list[Path] = []
    for relative in relative_paths:
        relative_text = relative.as_posix()
        if relative_text == ".gitignore":
            continue
        if relative_text.startswith(SOURCE_EXCLUDED_PREFIXES):
            continue
        source = PROJECT_ROOT / relative
        if source.is_file():
            selected.append(relative)
    return sorted(selected)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def build_wheel() -> Path:
    wheel_dir = BUILD_DIR / "wheel"
    wheel_dir.mkdir(parents=True, exist_ok=True)
    for existing in wheel_dir.glob("*.whl"):
        existing.unlink()
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--wheel-dir",
            str(wheel_dir),
            str(PACKAGE_DIR),
        ],
        cwd=PROJECT_ROOT,
    )
    wheels = sorted(wheel_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected one wheel, found {len(wheels)}")
    return wheels[0]


def markdown_inline(text: str) -> str:
    from xml.sax.saxutils import escape

    escaped = escape(text.strip())
    escaped = re.sub(
        r"`([^`]+)`",
        r"<font name='Courier'>\1</font>",
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    return escaped


def build_program_description_pdf(output_path: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    lines = (SCRIPT_DIR / "PROGRAM_DESCRIPTION.md").read_text(
        encoding="utf-8"
    ).splitlines()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SubmissionTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17324D"),
        spaceAfter=5,
    )
    heading_style = ParagraphStyle(
        "SubmissionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=14,
        textColor=colors.HexColor("#17324D"),
        spaceBefore=4,
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "SubmissionBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=12.3,
        textColor=colors.HexColor("#202A33"),
        spaceAfter=3,
    )

    story = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(
                Paragraph(markdown_inline(" ".join(paragraph)), body_style)
            )
            paragraph.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
        elif stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(markdown_inline(stripped[2:]), title_style))
        elif stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(markdown_inline(stripped[3:]), heading_style))
        elif stripped.endswith("  "):
            paragraph.append(stripped[:-2] + "<br/>")
        else:
            paragraph.append(stripped)
    flush_paragraph()
    story.append(Spacer(1, 1 * mm))

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm,
        title="MScProject Program Description",
        author="Tanatswa Mapfumo",
        subject="Evidence-grounded table-to-text generation software",
    )
    document.build(story)


def stage_submission(wheel: Path, description_pdf: Path) -> None:
    if STAGE_PARENT.exists():
        shutil.rmtree(STAGE_PARENT)
    STAGE_ROOT.mkdir(parents=True)

    for source_name, destination_name in SUBMISSION_DOCUMENTS.items():
        copy_file(SCRIPT_DIR / source_name, STAGE_ROOT / destination_name)
    copy_file(description_pdf, STAGE_ROOT / "PROGRAM_DESCRIPTION.pdf")
    copy_file(wheel, STAGE_ROOT / "executable" / wheel.name)

    for relative in tracked_source_files():
        copy_file(
            PROJECT_ROOT / relative,
            STAGE_ROOT / "source" / "MScProject" / relative,
        )

    for example in sorted((SCRIPT_DIR / "examples").iterdir()):
        if example.is_file():
            copy_file(example, STAGE_ROOT / "examples" / example.name)

    listing_candidates = [
        PROJECT_ROOT
        / "submission/program_listings/Tanatswa Mapfumo Project Code Printout.pdf",
        PROJECT_ROOT
        / "submission/program_listings/MScProject_Program_Listings.pdf",
    ]
    listing_pdf = next((path for path in listing_candidates if path.is_file()), None)
    if listing_pdf is not None:
        copy_file(
            listing_pdf,
            STAGE_ROOT / "documentation" / listing_pdf.name,
        )

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    version_text = (
        "MScProject software submission\n"
        "Package: table2text-pydanticai 0.1.0\n"
        f"Git commit: {commit}\n"
        f"Archive build date: {date.today().isoformat()}\n"
        f"Builder Python: {platform.python_version()}\n"
        f"Builder platform: {platform.platform()}\n"
    )
    (STAGE_ROOT / "VERSION.txt").write_text(version_text, encoding="utf-8")


def write_manifests() -> None:
    payload_files = sorted(
        path
        for path in STAGE_ROOT.rglob("*")
        if path.is_file()
        and path.name not in {"SOFTWARE_MANIFEST.json", "CHECKSUMS.sha256"}
    )
    records = [
        {
            "path": path.relative_to(STAGE_ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in payload_files
    ]
    manifest = {
        "archive_root": ARCHIVE_ROOT_NAME,
        "file_count": len(records),
        "total_payload_bytes": sum(record["bytes"] for record in records),
        "files": records,
    }
    (STAGE_ROOT / "SOFTWARE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    checksum_lines = [
        f"{record['sha256']}  {record['path']}" for record in records
    ]
    (STAGE_ROOT / "CHECKSUMS.sha256").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
    )


def build_zip() -> None:
    temporary_archive = BUILD_DIR / OUTPUT_ARCHIVE.name
    if temporary_archive.exists():
        temporary_archive.unlink()
    with zipfile.ZipFile(
        temporary_archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in sorted(STAGE_ROOT.rglob("*")):
            if path.is_file():
                archive.write(
                    path,
                    (Path(ARCHIVE_ROOT_NAME) / path.relative_to(STAGE_ROOT)).as_posix(),
                )
    shutil.copy2(temporary_archive, OUTPUT_ARCHIVE)
    OUTPUT_CHECKSUM.write_text(
        f"{sha256(OUTPUT_ARCHIVE)}  {OUTPUT_ARCHIVE.name}\n",
        encoding="utf-8",
    )


def main() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    generated_dir = BUILD_DIR / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    print("Building Python wheel...", flush=True)
    wheel = build_wheel()

    print("Generating one-page program description...", flush=True)
    description_pdf = generated_dir / "PROGRAM_DESCRIPTION.pdf"
    build_program_description_pdf(description_pdf)

    print("Staging maintained software and evidence...", flush=True)
    stage_submission(wheel, description_pdf)
    write_manifests()

    print("Compressing submission archive...", flush=True)
    build_zip()

    print(f"Archive: {OUTPUT_ARCHIVE}")
    print(f"SHA-256: {sha256(OUTPUT_ARCHIVE)}")
    print(
        "Archived files:",
        len([path for path in STAGE_ROOT.rglob("*") if path.is_file()]),
    )


if __name__ == "__main__":
    main()
