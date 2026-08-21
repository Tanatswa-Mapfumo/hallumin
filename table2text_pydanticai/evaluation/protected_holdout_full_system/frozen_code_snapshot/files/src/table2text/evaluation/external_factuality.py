from __future__ import annotations

import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from statistics import mean
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExternalFactualityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric_name: str
    status: str

    overall_score: float | None = None
    sentence_scores: list[float] = Field(default_factory=list)
    minimum_sentence_score: float | None = None
    unsupported_sentence_rate: float | None = None

    threshold: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
_TOKEN = re.compile(r"[A-Za-z0-9]+")


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


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [
        sentence.strip()
        for sentence in _SENTENCE_BOUNDARY.split(cleaned)
        if sentence.strip()
    ]


def summarise_sentence_scores(
    *,
    metric_name: str,
    scores: list[float],
    threshold: float,
    details: dict[str, Any] | None = None,
) -> ExternalFactualityResult:
    if not scores:
        return ExternalFactualityResult(
            metric_name=metric_name,
            status="skipped",
            threshold=threshold,
            details={"reason": "No factual sentences were supplied."},
        )

    unsupported_count = sum(score < threshold for score in scores)

    return ExternalFactualityResult(
        metric_name=metric_name,
        status="scored",
        overall_score=mean(scores),
        sentence_scores=scores,
        minimum_sentence_score=min(scores),
        unsupported_sentence_rate=unsupported_count / len(scores),
        threshold=threshold,
        details=details or {},
    )


def _token_set(text: str) -> set[str]:
    return {token.casefold() for token in _TOKEN.findall(text)}


def compact_support_context(
    *,
    context: str,
    claim: str,
    max_characters: int,
) -> str:
    context = re.sub(r"\s+", " ", context).strip()
    if len(context) <= max_characters:
        return context

    claim_tokens = _token_set(claim)
    units = split_sentences(context) or [context]
    ranked: list[tuple[int, int, str]] = []
    for index, unit in enumerate(units):
        overlap = len(claim_tokens & _token_set(unit))
        ranked.append((overlap, index, unit))

    selected: list[tuple[int, str]] = []
    used = 0
    for overlap, index, unit in sorted(
        ranked,
        key=lambda item: (item[0], -item[1]),
        reverse=True,
    ):
        if overlap == 0 and selected:
            continue
        next_length = len(unit) + (1 if selected else 0)
        if used + next_length > max_characters and selected:
            continue
        selected.append((index, unit[:max_characters]))
        used += min(next_length, max_characters)
        if used >= max_characters:
            break

    if not selected:
        return context[:max_characters].strip()

    ordered = [unit for _, unit in sorted(selected, key=lambda item: item[0])]
    compacted = " ".join(ordered).strip()
    return compacted[:max_characters].strip()


class HHEMEvaluator:
    def __init__(
        self,
        *,
        model_name: str = "vectara/hallucination_evaluation_model",
        foundation_model_name: str = "google/flan-t5-base",
        threshold: float = 0.5,
        batch_size: int = 16,
        device: str | None = None,
        local_files_only: bool = True,
        max_context_characters: int = 1_000,
    ) -> None:
        self.model_name = model_name
        self.foundation_model_name = foundation_model_name
        self.threshold = threshold
        self.batch_size = batch_size
        self.device = device
        self.local_files_only = local_files_only
        self.max_context_characters = max_context_characters
        self._model: Any | None = None

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        from huggingface_hub import snapshot_download

        model_path = self.model_name
        foundation_path = self.foundation_model_name
        if self.local_files_only:
            model_path = snapshot_download(
                repo_id=self.model_name,
                local_files_only=True,
            )
            foundation_path = snapshot_download(
                repo_id=self.foundation_model_name,
                local_files_only=True,
            )

        with huggingface_offline(self.local_files_only):
            from transformers import AutoConfig, AutoModelForSequenceClassification

            model_config = AutoConfig.from_pretrained(
                model_path,
                trust_remote_code=True,
                local_files_only=self.local_files_only,
            )
            model_config.foundation = foundation_path

            kwargs: dict[str, Any] = {
                "pretrained_model_name_or_path": model_path,
                "config": model_config,
                "trust_remote_code": True,
                "local_files_only": self.local_files_only,
            }
            if self.device and self.device != "cpu":
                kwargs["device_map"] = self.device
            self._model = AutoModelForSequenceClassification.from_pretrained(**kwargs)
        self._model.eval()
        return self._model

    def evaluate(
        self,
        *,
        context: str,
        generated_text: str,
    ) -> ExternalFactualityResult:
        sentences = split_sentences(generated_text)
        metric_name = "hhem_2_1_open"

        if not context.strip():
            return ExternalFactualityResult(
                metric_name=metric_name,
                status="skipped",
                threshold=self.threshold,
                details={"reason": "The factuality context is empty."},
            )
        if not sentences:
            return ExternalFactualityResult(
                metric_name=metric_name,
                status="skipped",
                threshold=self.threshold,
                details={"reason": "The generated output is empty."},
            )

        try:
            import torch
        except ImportError as exc:
            return ExternalFactualityResult(
                metric_name=metric_name,
                status="unavailable",
                threshold=self.threshold,
                error=f"torch is not installed: {exc}",
            )

        try:
            model = self._load_model()
            if not hasattr(model, "predict"):
                return ExternalFactualityResult(
                    metric_name=metric_name,
                    status="error",
                    threshold=self.threshold,
                    error="The loaded HHEM model does not expose a predict method.",
                )

            scores: list[float] = []
            with torch.inference_mode():
                for start in range(0, len(sentences), self.batch_size):
                    batch = sentences[start : start + self.batch_size]
                    pairs = [
                        (
                            compact_support_context(
                                context=context,
                                claim=sentence,
                                max_characters=self.max_context_characters,
                            ),
                            sentence,
                        )
                        for sentence in batch
                    ]
                    with huggingface_offline(self.local_files_only):
                        batch_scores = model.predict(pairs)
                    if hasattr(batch_scores, "detach"):
                        batch_scores = batch_scores.detach().cpu().tolist()
                    elif hasattr(batch_scores, "tolist"):
                        batch_scores = batch_scores.tolist()
                    for score in batch_scores:
                        if isinstance(score, (list, tuple)):
                            score = score[0]
                        scores.append(float(score))

            return summarise_sentence_scores(
                metric_name=metric_name,
                scores=scores,
                threshold=self.threshold,
                details={
                    "model_name": self.model_name,
                    "foundation_model_name": self.foundation_model_name,
                    "sentence_count": len(sentences),
                    "sentences": sentences,
                },
            )
        except ImportError as exc:
            return ExternalFactualityResult(
                metric_name=metric_name,
                status="unavailable",
                threshold=self.threshold,
                error=f"transformers is not installed: {exc}",
            )
        except Exception as exc:
            return ExternalFactualityResult(
                metric_name=metric_name,
                status="error",
                threshold=self.threshold,
                error=f"{type(exc).__name__}: {exc}",
            )
