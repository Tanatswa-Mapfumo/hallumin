from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None else int(value)


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None else float(value)


@dataclass(frozen=True)
class Settings:
    use_llm: bool = True
    output_dir: Path = Path("runs")

    max_revision_rounds: int = 2
    max_agent_requests: int = 4
    max_total_tokens: int = 24_000

    random_seed: int = 42
    max_analysis_rows: int = 50_000
    structured_output_mode: str = "native"

    full_data_correlation_limit: int = 250_000
    min_abs_correlation: float = 0.20
    max_correlation_findings: int = 6
    max_group_findings: int = 8

    target_proxy_correlation: float = 0.98
    allow_experimental_targets: bool = False

    forecast_folds: int = 3
    max_forecast_test_points: int = 2_000

    writer_target_words: int = 650
    writer_max_main_findings: int = 8
    repair_candidates_per_sentence: int = 3

    ollama_base_url: str = "http://localhost:11434/v1"

    data_understanding_model: str = "ollama:gemma3:4b"
    orchestrator_model: str = "ollama:gemma3:12b"
    evidence_model: str = "ollama:gemma3:12b"
    verifier_model: str = "ollama:gemma3:12b"
    writer_model: str = "ollama:gemma3:12b"
    auditor_model: str = "ollama:gemma3:12b"

    @classmethod
    def from_env(cls) -> "Settings":
        output_mode = os.getenv(
            "T2T_STRUCTURED_OUTPUT_MODE",
            "native",
        ).strip().lower()

        if output_mode not in {"native", "prompted"}:
            raise ValueError(
                "T2T_STRUCTURED_OUTPUT_MODE must be 'native' or 'prompted'."
            )

        return cls(
            use_llm=env_bool("T2T_USE_LLM", True),
            output_dir=Path(os.getenv("T2T_OUTPUT_DIR", "runs")),
            max_revision_rounds=env_int("T2T_MAX_REVISION_ROUNDS", 2),
            max_agent_requests=env_int("T2T_MAX_AGENT_REQUESTS", 4),
            max_total_tokens=env_int("T2T_MAX_TOTAL_TOKENS", 24_000),
            random_seed=env_int("T2T_RANDOM_SEED", 42),
            max_analysis_rows=env_int("T2T_MAX_ANALYSIS_ROWS", 50_000),
            structured_output_mode=output_mode,
            full_data_correlation_limit=env_int(
                "T2T_FULL_DATA_CORRELATION_LIMIT",
                250_000,
            ),
            min_abs_correlation=env_float(
                "T2T_MIN_ABS_CORRELATION",
                0.20,
            ),
            max_correlation_findings=env_int(
                "T2T_MAX_CORRELATION_FINDINGS",
                6,
            ),
            max_group_findings=env_int(
                "T2T_MAX_GROUP_FINDINGS",
                8,
            ),
            target_proxy_correlation=env_float(
                "T2T_TARGET_PROXY_CORRELATION",
                0.98,
            ),
            allow_experimental_targets=env_bool(
                "T2T_ALLOW_EXPERIMENTAL_TARGETS",
                False,
            ),
            forecast_folds=env_int("T2T_FORECAST_FOLDS", 3),
            max_forecast_test_points=env_int(
                "T2T_MAX_FORECAST_TEST_POINTS",
                2_000,
            ),
            writer_target_words=env_int(
                "T2T_WRITER_TARGET_WORDS",
                650,
            ),
            writer_max_main_findings=env_int(
                "T2T_WRITER_MAX_MAIN_FINDINGS",
                8,
            ),
            repair_candidates_per_sentence=env_int(
                "T2T_REPAIR_CANDIDATES_PER_SENTENCE",
                3,
            ),
            ollama_base_url=os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434/v1",
            ),
            data_understanding_model=os.getenv(
                "T2T_MODEL_DATA_UNDERSTANDING",
                "ollama:gemma3:4b",
            ),
            orchestrator_model=os.getenv(
                "T2T_MODEL_ORCHESTRATOR",
                "ollama:gemma3:12b",
            ),
            evidence_model=os.getenv(
                "T2T_MODEL_EVIDENCE",
                "ollama:gemma3:12b",
            ),
            verifier_model=os.getenv(
                "T2T_MODEL_VERIFIER",
                "ollama:gemma3:12b",
            ),
            writer_model=os.getenv(
                "T2T_MODEL_WRITER",
                "ollama:gemma3:12b",
            ),
            auditor_model=os.getenv(
                "T2T_MODEL_AUDITOR",
                "ollama:gemma3:12b",
            ),
        )

    def model_for(self, role: str) -> str:
        mapping = {
            "data_understanding": self.data_understanding_model,
            "orchestrator": self.orchestrator_model,
            "evidence": self.evidence_model,
            "verifier": self.verifier_model,
            "writer": self.writer_model,
            "auditor": self.auditor_model,
        }

        try:
            return mapping[role]
        except KeyError as error:
            raise ValueError(f"Unknown model role: {role}") from error