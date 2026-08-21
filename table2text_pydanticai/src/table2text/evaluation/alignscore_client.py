"""Invoke an isolated AlignScore worker and normalise its factuality scores."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path

from .external_factuality import ExternalFactualityResult


class AlignScoreClient:
    def __init__(
        self,
        *,
        python_executable: Path,
        worker_path: Path,
        model_size: str = "base",
        device: str = "cpu",
        batch_size: int = 8,
        threshold: float = 0.5,
        local_files_only: bool = True,
    ) -> None:
        self.threshold = threshold
        self.model_size = model_size

        command = [
            str(python_executable),
            str(worker_path),
            "--model-size",
            model_size,
            "--device",
            device,
            "--batch-size",
            str(batch_size),
        ]
        environment = os.environ.copy()
        if local_files_only:
            command.append("--local-files-only")
            environment["HF_HUB_OFFLINE"] = "1"
            environment["TRANSFORMERS_OFFLINE"] = "1"
        environment.setdefault(
            "HF_MODULES_CACHE",
            str(Path(tempfile.gettempdir()) / "table2text_hf_modules"),
        )

        self._process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=environment,
        )

    @property
    def metric_name(self) -> str:
        return f"alignscore_{self.model_size}"

    def evaluate(
        self,
        *,
        context: str,
        generated_text: str,
    ) -> ExternalFactualityResult:
        if not context.strip():
            return ExternalFactualityResult(
                metric_name=self.metric_name,
                status="skipped",
                threshold=self.threshold,
                details={"reason": "The factuality context is empty."},
            )
        if not generated_text.strip():
            return ExternalFactualityResult(
                metric_name=self.metric_name,
                status="skipped",
                threshold=self.threshold,
                details={"reason": "The generated output is empty."},
            )
        if self._process.stdin is None or self._process.stdout is None:
            return ExternalFactualityResult(
                metric_name=self.metric_name,
                status="error",
                threshold=self.threshold,
                error="AlignScore worker pipes are unavailable.",
            )

        request_id = uuid.uuid4().hex
        request = {
            "request_id": request_id,
            "context": context,
            "claim": generated_text,
        }

        self._process.stdin.write(json.dumps(request) + "\n")
        self._process.stdin.flush()

        response_line = self._process.stdout.readline()
        if not response_line:
            stderr = self._process.stderr.read() if self._process.stderr else ""
            return ExternalFactualityResult(
                metric_name=self.metric_name,
                status="error",
                threshold=self.threshold,
                error=f"AlignScore worker terminated. stderr={stderr}",
            )

        response = json.loads(response_line)
        if response.get("request_id") != request_id:
            return ExternalFactualityResult(
                metric_name=self.metric_name,
                status="error",
                threshold=self.threshold,
                error="AlignScore response ID mismatch.",
            )
        if response.get("status") != "scored":
            return ExternalFactualityResult(
                metric_name=self.metric_name,
                status="error",
                threshold=self.threshold,
                error=response.get("error"),
            )

        return ExternalFactualityResult(
            metric_name=self.metric_name,
            status="scored",
            overall_score=float(response["score"]),
            threshold=self.threshold,
            details={
                "evaluation_mode": "nli_sp",
                "model_size": self.model_size,
            },
        )

    def close(self) -> None:
        if self._process.stdin:
            self._process.stdin.close()
        self._process.terminate()
        try:
            self._process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=10)
