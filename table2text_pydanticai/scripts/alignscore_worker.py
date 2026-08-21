"""Isolated command-line worker for local AlignScore inference."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download


@contextmanager
def huggingface_offline(enabled: bool):
    keys = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_MODULES_CACHE")
    previous = {key: os.environ.get(key) for key in keys}
    if enabled:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    if previous["HF_MODULES_CACHE"] is None:
        modules_cache = Path(tempfile.gettempdir()) / "table2text_hf_modules"
        modules_cache.mkdir(parents=True, exist_ok=True)
        os.environ["HF_MODULES_CACHE"] = str(modules_cache)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-size", choices=["base", "large"], default="base")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--local-files-only", action="store_true")
    return parser


def load_scorer(
    *,
    model_size: str,
    device: str,
    batch_size: int,
    local_files_only: bool,
):
    if model_size == "base":
        model_repo = "roberta-base"
        filename = "AlignScore-base.ckpt"
    else:
        model_repo = "roberta-large"
        filename = "AlignScore-large.ckpt"

    checkpoint = hf_hub_download(
        repo_id="yzha/AlignScore",
        filename=filename,
        local_files_only=local_files_only,
    )
    model_name = model_repo
    if local_files_only:
        model_name = snapshot_download(
            repo_id=model_repo,
            local_files_only=True,
        )

    with huggingface_offline(local_files_only):
        from alignscore import AlignScore

        return AlignScore(
            model=model_name,
            batch_size=batch_size,
            device=device,
            ckpt_path=checkpoint,
            evaluation_mode="nli_sp",
        )


def main() -> None:
    arguments = build_parser().parse_args()
    scorer = load_scorer(
        model_size=arguments.model_size,
        device=arguments.device,
        batch_size=arguments.batch_size,
        local_files_only=arguments.local_files_only,
    )

    for line in sys.stdin:
        if not line.strip():
            continue
        request = json.loads(line)
        request_id = str(request["request_id"])
        context = str(request["context"])
        claim = str(request["claim"])

        try:
            scores = scorer.score(contexts=[context], claims=[claim])
            response = {
                "request_id": request_id,
                "status": "scored",
                "score": float(scores[0]),
            }
        except Exception as exc:
            response = {
                "request_id": request_id,
                "status": "error",
                "score": None,
                "error": f"{type(exc).__name__}: {exc}",
            }

        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
