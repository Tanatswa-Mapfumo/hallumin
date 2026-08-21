from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from .config import Settings
from .schemas import (
    AuditMode,
    EvaluationFieldPolicy,
    ExternalTruthSource,
    ReportGenre,
)
from .workflow import Table2TextWorkflow


def load_external_truth(
    path: str | None,
) -> list[ExternalTruthSource]:
    if not path:
        return []

    payload = json.loads(
        Path(path).read_text(encoding="utf-8")
    )

    if isinstance(payload, dict):
        payload = payload.get("sources", [payload])

    if not isinstance(payload, list):
        raise ValueError(
            "External truth JSON must contain a source list."
        )

    return [
        ExternalTruthSource.model_validate(source)
        for source in payload
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="table2text",
        description=(
            "Run the six-agent PydanticAI Table2Text pipeline."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run the full Table2Text workflow.",
    )

    run_parser.add_argument(
        "inputs",
        nargs="+",
        help="Input tables or directories.",
    )

    run_parser.add_argument(
        "--request",
        required=True,
        help="The data-science reporting objective.",
    )

    run_parser.add_argument(
        "--audit-mode",
        default=AuditMode.INTERNAL.value,
        choices=[mode.value for mode in AuditMode],
    )

    run_parser.add_argument(
        "--external-truth",
        help="JSON file containing trusted external facts.",
    )

    run_parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Use deterministic fallbacks without LLM calls.",
    )

    run_parser.add_argument(
        "--output-dir",
        help="Override the run artifact directory.",
    )

    run_parser.add_argument(
        "--allow-experimental-targets",
        action="store_true",
        help=(
            "Allow unconfirmed candidate targets for explicit "
            "modelling experiments."
        ),
    )

    run_parser.add_argument(
        "--report-genre",
        choices=[genre.value for genre in ReportGenre],
        help="Set an experiment-level report-genre contract.",
    )
    run_parser.add_argument(
        "--operational-input-path",
        action="append",
        default=[],
        help="Declare an operational JSON path; repeat for multiple paths.",
    )
    run_parser.add_argument(
        "--held-out-reference-path",
        action="append",
        default=[],
        help="Declare a held-out evaluation-reference JSON path.",
    )
    run_parser.add_argument(
        "--metadata-path",
        action="append",
        default=[],
        help="Declare a metadata-only JSON path.",
    )

    return parser


def main() -> None:
    arguments = build_parser().parse_args()
    settings = Settings.from_env()

    if arguments.no_llm:
        settings = replace(
            settings,
            use_llm=False,
        )

    if arguments.output_dir:
        settings = replace(
            settings,
            output_dir=Path(arguments.output_dir),
        )

    if arguments.allow_experimental_targets:
        settings = replace(
            settings,
            allow_experimental_targets=True,
        )

    workflow = Table2TextWorkflow(settings)

    result = workflow.run_sync(
        inputs=arguments.inputs,
        request=arguments.request,
        audit_mode=AuditMode(arguments.audit_mode),
        external_truth_sources=load_external_truth(
            arguments.external_truth
        ),
        evaluation_field_policy=EvaluationFieldPolicy(
            operational_input_paths=arguments.operational_input_path,
            held_out_reference_paths=arguments.held_out_reference_path,
            metadata_paths=arguments.metadata_path,
        ),
        report_genre=(
            ReportGenre(arguments.report_genre)
            if arguments.report_genre
            else None
        ),
    )

    print(f"Run ID: {result.run_id}")
    print(f"Release status: {result.release_status.value}")
    print(f"Approved for release: {result.approved_for_release}")
    print(f"Repair rounds: {result.repair_rounds_used}")
    print(f"Writer mode: {result.raw_writer_output.writer_mode}")
    print(f"Artifacts: {settings.output_dir / result.run_id}")
