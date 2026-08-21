"""Command-line interface for the reproducible evaluation subsystem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .datasets import (
    default_dataset_configs,
    load_dataset_configs,
    prepare_datasets,
    read_examples,
    save_default_dataset_configs,
)
from .deepeval_metrics import evaluate_deepeval
from .diagnostics import write_diagnostics
from .generation import generate_all, load_variants, read_generations
from .human_evaluation import (
    decode_human_scores,
    export_human_packet,
    export_reviewer_packet,
    inter_rater_statistics,
    load_human_judgements,
    make_blinded_pairs,
)
from .models import (
    DeepEvalConfig,
    ExperimentConfig,
    HumanEvaluationPair,
    ReferenceMetricConfig,
    VariantConfig,
)
from .reference_metrics import evaluate_reference_metrics
from .statistics import write_analysis


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_default_variants(path: Path) -> None:
    variants = [
        VariantConfig(
            variant_id="single_agent_baseline",
            enabled=False,
            backend="callable",
            description=(
                "Configure callable_path with a direct single-agent generation function."
            ),
            callable_path="table2text.evaluation_backends.single_agent_baseline",
            repetitions=1,
            seeds=[42],
        ),
        VariantConfig(
            variant_id="full_system",
            enabled=True,
            backend="table2text",
            description="Current full multi-agent system.",
            settings_overrides={},
            repetitions=1,
            seeds=[42],
        ),
        VariantConfig(
            variant_id="insight_synthesis_off",
            enabled=True,
            backend="table2text",
            description="Full system with insight synthesis disabled.",
            settings_overrides={"enable_insight_synthesis": False},
            repetitions=1,
            seeds=[42],
        ),
        VariantConfig(
            variant_id="verifier_off",
            enabled=False,
            backend="precomputed",
            description=(
                "Enable after the operational pipeline exposes a verifier feature "
                "flag, or provide precomputed outputs."
            ),
            precomputed_path=Path("evaluation/generations/verifier_off.jsonl"),
            repetitions=1,
            seeds=[42],
        ),
        VariantConfig(
            variant_id="auditor_off",
            enabled=False,
            backend="precomputed",
            description=(
                "Enable after generating outputs with the final Auditor and repair "
                "stages disabled."
            ),
            precomputed_path=Path("evaluation/generations/auditor_off.jsonl"),
            repetitions=1,
            seeds=[42],
        ),
        VariantConfig(
            variant_id="auditor_detection_only",
            enabled=False,
            backend="precomputed",
            description="Auditor detects issues but does not repair them.",
            precomputed_path=Path("evaluation/generations/auditor_detection_only.jsonl"),
            repetitions=1,
            seeds=[42],
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"variants": [item.model_dump(mode="json") for item in variants]},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def write_default_metrics(path: Path) -> None:
    payload = {
        "experiment_id": "table2text_reference_evaluation_v1",
        "prepared_examples_path": "evaluation/prepared/all_examples.jsonl",
        "generations_path": "evaluation/generations/generations.jsonl",
        "result_directory": "evaluation/results",
        "baseline_variant": "single_agent_baseline",
        "bootstrap_resamples": 5000,
        "confidence_level": 0.95,
        "random_seed": 42,
        "reference_metrics": ReferenceMetricConfig().model_dump(mode="json"),
        "deepeval": DeepEvalConfig().model_dump(mode="json"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def init_config(arguments: argparse.Namespace) -> None:
    root = Path(arguments.directory)
    save_default_dataset_configs(root / "datasets.json")
    write_default_variants(root / "variants.json")
    write_default_metrics(root / "metrics.json")
    print(f"Created evaluation configuration in {root}")


def list_datasets(_: argparse.Namespace) -> None:
    for config in default_dataset_configs():
        location = config.hub_id if config.hub_id else str(config.local_path)
        print(
            f"{config.dataset_id:32s} "
            f"{config.source.value:12s} "
            f"{config.task_family.value:36s} "
            f"{location}"
        )


def prepare(arguments: argparse.Namespace) -> None:
    statuses = prepare_datasets(
        load_dataset_configs(Path(arguments.config)),
        Path(arguments.output_directory),
        skip_unavailable=arguments.skip_unavailable,
    )
    for status in statuses:
        print(
            f"{status.dataset_id}: {status.status.value}; examples={status.example_count}"
            + (f"; error={status.error}" if status.error else "")
        )


def generate(arguments: argparse.Namespace) -> None:
    records = generate_all(
        read_examples(Path(arguments.examples)),
        load_variants(Path(arguments.variants)),
        Path(arguments.output),
        Path(arguments.run_root),
        resume=not arguments.no_resume,
    )
    successful = sum(item.error is None for item in records)
    print(
        f"Generation records: {len(records)}; successful: {successful}; "
        f"errors: {len(records) - successful}"
    )


def reference_metrics(arguments: argparse.Namespace) -> None:
    records = read_generations(Path(arguments.generations))
    experiment = ExperimentConfig.model_validate(load_json(Path(arguments.config)))
    observations = evaluate_reference_metrics(
        records,
        experiment.reference_metrics,
        Path(arguments.output),
        include_ineligible=arguments.include_ineligible,
    )
    scored = sum(item.status.value == "scored" for item in observations)
    print(f"Reference metric observations: {len(observations)}; scored: {scored}")


def deepeval_metrics(arguments: argparse.Namespace) -> None:
    records = read_generations(Path(arguments.generations))
    experiment = ExperimentConfig.model_validate(load_json(Path(arguments.config)))
    observations = evaluate_deepeval(
        records,
        experiment.deepeval,
        Path(arguments.output),
        resume=not arguments.no_resume,
    )
    scored = sum(item.status.value == "scored" for item in observations)
    print(f"DeepEval observations: {len(observations)}; scored: {scored}")


def diagnostics(arguments: argparse.Namespace) -> None:
    frame = write_diagnostics(Path(arguments.generations), Path(arguments.output))
    print(f"Wrote {len(frame)} diagnostic rows.")


def export_human(arguments: argparse.Namespace) -> None:
    pairs = make_blinded_pairs(
        read_generations(Path(arguments.generations)),
        variants=arguments.variant if arguments.variant else None,
        examples_per_dataset=arguments.examples_per_dataset,
        seed=arguments.seed,
    )
    export_human_packet(
        pairs,
        Path(arguments.hidden_packet),
        Path(arguments.response_template),
    )
    export_reviewer_packet(pairs, Path(arguments.reviewer_packet))
    print(f"Created {len(pairs)} blinded comparisons.")


def analyse_human(arguments: argparse.Namespace) -> None:
    pairs = [
        HumanEvaluationPair.model_validate_json(line)
        for line in Path(arguments.hidden_packet).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    judgements = load_human_judgements(Path(arguments.responses))
    decoded = decode_human_scores(pairs, judgements)
    output_directory = Path(arguments.output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    decoded.to_csv(output_directory / "human_scores_decoded.csv", index=False)
    inter_rater_statistics(judgements).to_csv(
        output_directory / "inter_rater_agreement.csv",
        index=False,
    )
    summary = (
        decoded.groupby(["dataset_id", "variant_id"], as_index=False)
        .agg(
            factual_correctness=("factual_correctness", "mean"),
            coverage=("coverage", "mean"),
            coherence=("coherence", "mean"),
            usefulness=("usefulness", "mean"),
            preference_rate=("preferred", "mean"),
            tie_rate=("tie", "mean"),
            rating_count=("pair_id", "count"),
        )
    )
    summary.to_csv(output_directory / "human_summary.csv", index=False)
    print(f"Analysed {len(judgements)} judgements.")


def aggregate(arguments: argparse.Namespace) -> None:
    experiment = ExperimentConfig.model_validate(load_json(Path(arguments.config)))
    write_analysis(
        reference_observations_path=Path(arguments.reference_metrics),
        deepeval_observations_path=(
            Path(arguments.deepeval_metrics) if arguments.deepeval_metrics else None
        ),
        diagnostics_path=Path(arguments.diagnostics) if arguments.diagnostics else None,
        output_directory=Path(arguments.output_directory),
        baseline_variant=experiment.baseline_variant,
        bootstrap_resamples=experiment.bootstrap_resamples,
        confidence_level=experiment.confidence_level,
        seed=experiment.random_seed,
    )
    print(f"Analysis written to {arguments.output_directory}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reference-based Table2Text evaluation system.")
    subparsers = parser.add_subparsers(required=True)

    command = subparsers.add_parser("init-config")
    command.add_argument("--directory", default="evaluation/config")
    command.set_defaults(function=init_config)

    command = subparsers.add_parser("list-datasets")
    command.set_defaults(function=list_datasets)

    command = subparsers.add_parser("prepare")
    command.add_argument("--config", default="evaluation/config/datasets.json")
    command.add_argument("--output-directory", default="evaluation/prepared")
    command.add_argument("--skip-unavailable", action="store_true")
    command.set_defaults(function=prepare)

    command = subparsers.add_parser("generate")
    command.add_argument("--examples", default="evaluation/prepared/all_examples.jsonl")
    command.add_argument("--variants", default="evaluation/config/variants.json")
    command.add_argument("--output", default="evaluation/generations/generations.jsonl")
    command.add_argument("--run-root", default="evaluation/generations/runs")
    command.add_argument("--no-resume", action="store_true")
    command.set_defaults(function=generate)

    command = subparsers.add_parser("reference-metrics")
    command.add_argument("--generations", default="evaluation/generations/generations.jsonl")
    command.add_argument("--config", default="evaluation/config/metrics.json")
    command.add_argument("--output", default="evaluation/results/reference_metrics.jsonl")
    command.add_argument(
        "--include-ineligible",
        action="store_true",
        help=(
            "Score generations marked ineligible for primary evaluation. "
            "Useful for notebook smoke tests; protected evaluation should omit this."
        ),
    )
    command.set_defaults(function=reference_metrics)

    command = subparsers.add_parser("deepeval")
    command.add_argument("--generations", default="evaluation/generations/generations.jsonl")
    command.add_argument("--config", default="evaluation/config/metrics.json")
    command.add_argument("--output", default="evaluation/results/deepeval_metrics.jsonl")
    command.add_argument("--no-resume", action="store_true")
    command.set_defaults(function=deepeval_metrics)

    command = subparsers.add_parser("diagnostics")
    command.add_argument("--generations", default="evaluation/generations/generations.jsonl")
    command.add_argument("--output", default="evaluation/results/diagnostics.csv")
    command.set_defaults(function=diagnostics)

    command = subparsers.add_parser("export-human")
    command.add_argument("--generations", default="evaluation/generations/generations.jsonl")
    command.add_argument("--variant", action="append", default=[])
    command.add_argument("--examples-per-dataset", type=int, default=10)
    command.add_argument("--seed", type=int, default=42)
    command.add_argument("--hidden-packet", default="evaluation/human/hidden_pair_mapping.jsonl")
    command.add_argument("--reviewer-packet", default="evaluation/human/reviewer_packet.jsonl")
    command.add_argument("--response-template", default="evaluation/human/response_template.csv")
    command.set_defaults(function=export_human)

    command = subparsers.add_parser("analyse-human")
    command.add_argument("--hidden-packet", default="evaluation/human/hidden_pair_mapping.jsonl")
    command.add_argument("--responses", required=True)
    command.add_argument("--output-directory", default="evaluation/results/human")
    command.set_defaults(function=analyse_human)

    command = subparsers.add_parser("aggregate")
    command.add_argument("--config", default="evaluation/config/metrics.json")
    command.add_argument("--reference-metrics", default="evaluation/results/reference_metrics.jsonl")
    command.add_argument("--deepeval-metrics", default="evaluation/results/deepeval_metrics.jsonl")
    command.add_argument("--diagnostics", default="evaluation/results/diagnostics.csv")
    command.add_argument("--output-directory", default="evaluation/results/analysis")
    command.set_defaults(function=aggregate)
    return parser


def main(argv: list[str] | None = None) -> None:
    arguments = build_parser().parse_args(argv)
    arguments.function(arguments)


if __name__ == "__main__":
    main()
