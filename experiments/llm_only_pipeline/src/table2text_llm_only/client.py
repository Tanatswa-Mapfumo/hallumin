from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any

from table2text.config import load_env_files

from .schemas import AgentCallTrace, UsageSummary


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def _as_int(value: Any, default: int) -> int:
    if value is None:
        return default
    return int(str(value).replace("_", ""))


def _as_float(value: Any, default: float) -> float:
    if value is None:
        return default
    return float(str(value))


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.DOTALL)
    return fenced.group(1).strip() if fenced else stripped


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = _strip_json_fence(text)
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("Expected the model to return a JSON object.")
    return value


@dataclass(frozen=True)
class LLMOnlyClientConfig:
    model: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"
    max_output_tokens: int = 6000
    temperature: float = 0.1
    response_format_json: bool = True
    json_repair_attempts: int = 1

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "LLMOnlyClientConfig":
        load_env_files()
        model = str(
            values.get("llm_only_model")
            or _first_env("T2T_LLM_ONLY_MODEL")
            or cls.model
        )
        if model.startswith("deepseek:"):
            model = model.split(":", 1)[1]
        return cls(
            model=model,
            base_url=str(
                values.get("llm_only_base_url")
                or _first_env("T2T_LLM_ONLY_BASE_URL", "DEEPSEEK_BASE_URL")
                or cls.base_url
            ),
            api_key_env=str(
                values.get("llm_only_api_key_env")
                or _first_env("T2T_LLM_ONLY_API_KEY_ENV")
                or cls.api_key_env
            ),
            max_output_tokens=_as_int(
                values.get("llm_only_max_output_tokens")
                or _first_env("T2T_LLM_ONLY_MAX_OUTPUT_TOKENS"),
                cls.max_output_tokens,
            ),
            temperature=_as_float(
                values.get("llm_only_temperature")
                or _first_env("T2T_LLM_ONLY_TEMPERATURE"),
                cls.temperature,
            ),
            response_format_json=str(
                values.get("llm_only_response_format_json")
                or _first_env("T2T_LLM_ONLY_RESPONSE_FORMAT_JSON")
                or "true"
            ).strip().lower()
            in {"1", "true", "yes", "on"},
            json_repair_attempts=_as_int(
                values.get("llm_only_json_repair_attempts")
                or _first_env("T2T_LLM_ONLY_JSON_REPAIR_ATTEMPTS"),
                cls.json_repair_attempts,
            ),
        )


class LLMOnlyClient:
    def __init__(self, config: LLMOnlyClientConfig):
        self.config = config
        api_key = _first_env(config.api_key_env)
        if api_key is None:
            raise RuntimeError(
                f"{config.api_key_env} is required to run the LLM-only workflow."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The openai package is required to run the LLM-only workflow."
            ) from exc
        self._client = OpenAI(api_key=api_key, base_url=config.base_url)

    def json_call(
        self,
        *,
        stage: str,
        system: str,
        user: str,
    ) -> tuple[dict[str, Any], AgentCallTrace]:
        started = time.perf_counter()
        text, usage = self._chat_json_mode(system=system, user=user)
        try:
            parsed = parse_json_object(text)
        except json.JSONDecodeError as error:
            if self.config.json_repair_attempts <= 0:
                raise RuntimeError(
                    f"{stage} returned invalid JSON: {error}. "
                    f"Response excerpt: {text[:1000]}"
                ) from error
            repaired_text, repair_usage = self._chat_json_mode(
                system=(
                    "You repair malformed JSON. Return only one valid JSON "
                    "object. Do not add commentary, markdown fences, or fields "
                    "that were not implied by the malformed JSON."
                ),
                user=(
                    "The previous model response was intended to be JSON but "
                    f"failed with this parser error: {error}\n\n"
                    "Repair it into valid JSON. Preserve all complete content "
                    "that can be safely recovered. If a string or array was "
                    "truncated, close it conservatively rather than inventing "
                    "missing details.\n\nMalformed response:\n"
                    + text[:12000]
                ),
            )
            try:
                parsed = parse_json_object(repaired_text)
            except json.JSONDecodeError as repair_error:
                raise RuntimeError(
                    f"{stage} returned invalid JSON, and repair failed: "
                    f"{repair_error}. Original excerpt: {text[:1000]}"
                ) from repair_error
            usage = UsageSummary(
                prompt_tokens=(usage.prompt_tokens or 0)
                + (repair_usage.prompt_tokens or 0)
                or None,
                completion_tokens=(usage.completion_tokens or 0)
                + (repair_usage.completion_tokens or 0)
                or None,
                total_tokens=(usage.total_tokens or 0)
                + (repair_usage.total_tokens or 0)
                or None,
            )

        trace = AgentCallTrace(
            stage=stage,
            model=self.config.model,
            elapsed_seconds=time.perf_counter() - started,
            usage=usage,
        )
        return parsed, trace

    def _chat_json_mode(
        self,
        *,
        system: str,
        user: str,
    ) -> tuple[str, UsageSummary]:
        kwargs: dict[str, Any] = {}
        if self.config.response_format_json:
            kwargs["response_format"] = {"type": "json_object"}
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            **kwargs,
        )
        text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        return (
            text,
            UsageSummary(
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            ),
        )
