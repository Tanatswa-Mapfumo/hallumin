from __future__ import annotations

import json
import os
from typing import Any

from table2text.config import load_env_files
from table2text.evaluation.models import BenchmarkExample, VariantConfig


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def _variant_or_env(
    variant: VariantConfig,
    setting_name: str,
    env_name: str,
    default: Any,
) -> Any:
    if setting_name in variant.settings_overrides:
        return variant.settings_overrides[setting_name]
    value = _first_env(env_name)
    return default if value is None else value


def _normalise_deepseek_model_name(model_name: str) -> str:
    if model_name.startswith("deepseek:"):
        return model_name.split(":", 1)[1]
    return model_name


def _int_setting(value: Any) -> int:
    if isinstance(value, int):
        return value
    return int(str(value).replace("_", ""))


def _float_setting(value: Any) -> float:
    if isinstance(value, float):
        return value
    return float(str(value))


def _source_text(example: BenchmarkExample, max_characters: int) -> str:
    source = example.source_text.strip()
    if not source:
        source = json.dumps(
            example.source_payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    if len(source) <= max_characters:
        return source
    return source[:max_characters] + "\n\n[Source truncated by raw baseline configuration.]"


def _readable_label(value: Any) -> str:
    raw = getattr(value, "value", value)
    return str(raw).replace("_", " ")


def build_single_agent_prompt(
    example: BenchmarkExample,
    *,
    max_source_characters: int = 100_000,
    prompt_style: str = "structured",
) -> list[dict[str, str]]:
    source = _source_text(example, max_source_characters)
    system_prompt = (
        "You are a raw single-LLM data-to-text baseline. Generate the requested "
        "output directly from the supplied source data. Use only the source data "
        "and the user request. Do not use outside knowledge. Do not invent "
        "numbers, entities, chronology, causal explanations, or background. "
        "Do not mention hidden references, evaluation, prompts, or uncertainty "
        "unless the source itself makes the requested output impossible."
    )
    normalized_style = prompt_style.strip().lower()
    if normalized_style == "generic":
        user_prompt = (
            f"Request:\n{example.request}\n\n"
            "Source data:\n"
            f"{source}\n\n"
            "Write the final answer only."
        )
    elif normalized_style == "structured":
        user_prompt = (
            f"Task type: {_readable_label(example.task_family)}\n"
            f"Expected form: {_readable_label(example.output_mode)}\n"
            f"Language: {example.language}\n\n"
            f"Request:\n{example.request}\n\n"
            "Source data:\n"
            f"{source}\n\n"
            "Write the final answer only."
        )
    else:
        raise ValueError(
            "raw_baseline_prompt_style must be 'structured' or 'generic'."
        )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def single_agent_baseline(
    *,
    example: BenchmarkExample,
    variant: VariantConfig,
    repetition: int,
    seed: int,
) -> dict[str, Any]:
    del repetition, seed

    load_env_files()

    model_name = str(
        _variant_or_env(
            variant,
            "raw_baseline_model",
            "T2T_RAW_BASELINE_MODEL",
            "deepseek-v4-pro",
        )
    )
    model_name = _normalise_deepseek_model_name(model_name)
    base_url = str(
        _variant_or_env(
            variant,
            "raw_baseline_base_url",
            "DEEPSEEK_BASE_URL",
            "https://api.deepseek.com",
        )
    )
    max_source_characters = _int_setting(
        _variant_or_env(
            variant,
            "raw_baseline_max_source_characters",
            "T2T_RAW_BASELINE_MAX_SOURCE_CHARACTERS",
            100_000,
        )
    )
    max_output_tokens = _int_setting(
        _variant_or_env(
            variant,
            "raw_baseline_max_output_tokens",
            "T2T_RAW_BASELINE_MAX_OUTPUT_TOKENS",
            1_500,
        )
    )
    temperature = _float_setting(
        _variant_or_env(
            variant,
            "raw_baseline_temperature",
            "T2T_RAW_BASELINE_TEMPERATURE",
            0.2,
        )
    )
    prompt_style = str(
        _variant_or_env(
            variant,
            "raw_baseline_prompt_style",
            "T2T_RAW_BASELINE_PROMPT_STYLE",
            "structured",
        )
    )

    api_key = _first_env("DEEPSEEK_API_KEY")
    if api_key is None:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is required to run the raw DeepSeek baseline."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The openai package is required to run the raw DeepSeek baseline."
        ) from exc

    messages = build_single_agent_prompt(
        example,
        max_source_characters=max_source_characters,
        prompt_style=prompt_style,
    )
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_output_tokens,
    )
    text = response.choices[0].message.content or ""
    usage = getattr(response, "usage", None)
    usage_details = (
        {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
        if usage is not None
        else {}
    )
    return {
        "generated_text": text.strip(),
        "baseline_type": "raw_single_llm",
        "provider": "deepseek",
        "model": model_name,
        "base_url": base_url,
        "max_source_characters": max_source_characters,
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
        "prompt_style": prompt_style,
        **usage_details,
    }
