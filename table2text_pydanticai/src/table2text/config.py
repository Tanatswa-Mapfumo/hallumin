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
    writer_quality_revision_rounds: int = 1
    writer_priority_fact_limit: int = 10
    writer_supporting_fact_limit: int = 20

    enable_insight_synthesis: bool = True
    max_insight_candidates: int = 6
    max_verified_main_insights: int = 4
    min_insight_confidence: float = 0.75
    min_insight_salience: float = 0.65
    min_facts_per_bounded_insight: int = 2
    allow_hypotheses_in_report: bool = False

    # Deterministic coverage recovery from the trusted evidence ledger.
    minimum_writer_ready_fact_count: int = 6
    minimum_overview_fact_count: int = 1
    minimum_data_quality_fact_count: int = 1
    minimum_relationship_fact_count: int = 2

    maximum_recovered_overview_facts: int = 2
    maximum_recovered_data_quality_facts: int = 3
    maximum_recovered_correlation_facts: int = 3
    maximum_recovered_group_comparison_facts: int = 2
    maximum_recovered_modelling_facts: int = 1

    max_priority_dataset_overview_facts: int = 2
    max_priority_data_quality_facts: int = 3
    max_priority_correlation_facts: int = 3
    max_priority_group_comparison_facts: int = 2
    max_priority_predictive_facts: int = 1
    max_priority_forecast_facts: int = 1
    max_priority_limitation_facts: int = 2

    minimum_main_finding_score: float = 0.65
    minimum_main_effect_strength: str = "moderate"

    maximum_data_quality_findings: int = 3
    maximum_association_findings: int = 4
    maximum_predictive_findings: int = 1
    maximum_forecast_findings: int = 1
    maximum_limitation_findings: int = 3

    minimum_report_word_ratio: float = 0.45
    minimum_report_word_floor: int = 160
    maximum_repeated_caveat_mentions: int = 4

    zero_unusual_rate_threshold: float = 0.05

    ollama_base_url: str = "http://localhost:11434/v1"

    data_understanding_model: str = "ollama:gemma3:4b"
    orchestrator_model: str = "ollama:gemma3:12b"
    evidence_model: str = "ollama:gemma3:12b"
    verifier_model: str = "ollama:gemma3:12b"
    writer_model: str = "ollama:gemma3:12b"
    auditor_model: str = "ollama:gemma3:12b"

    def __post_init__(self) -> None:
        if self.max_insight_candidates <= 0:
            raise ValueError(
                "max_insight_candidates must be positive."
            )

        if self.max_verified_main_insights <= 0:
            raise ValueError(
                "max_verified_main_insights must be positive."
            )

        if (
            self.max_verified_main_insights
            > self.max_insight_candidates
        ):
            raise ValueError(
                "max_verified_main_insights cannot exceed "
                "max_insight_candidates."
            )

        for field_name, value in {
            "min_insight_confidence": self.min_insight_confidence,
            "min_insight_salience": self.min_insight_salience,
        }.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be between 0 and 1."
                )

        if self.min_facts_per_bounded_insight < 1:
            raise ValueError(
                "min_facts_per_bounded_insight must be at least 1."
            )

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
            writer_quality_revision_rounds=min(
                env_int("T2T_WRITER_QUALITY_REVISION_ROUNDS", 1),
                1,
            ),
            writer_priority_fact_limit=env_int(
                "T2T_WRITER_PRIORITY_FACT_LIMIT",
                10,
            ),
            writer_supporting_fact_limit=env_int(
                "T2T_WRITER_SUPPORTING_FACT_LIMIT",
                20,
            ),
            enable_insight_synthesis=env_bool(
                "T2T_ENABLE_INSIGHT_SYNTHESIS",
                True,
            ),
            max_insight_candidates=env_int(
                "T2T_MAX_INSIGHT_CANDIDATES",
                6,
            ),
            max_verified_main_insights=env_int(
                "T2T_MAX_VERIFIED_MAIN_INSIGHTS",
                4,
            ),
            min_insight_confidence=env_float(
                "T2T_MIN_INSIGHT_CONFIDENCE",
                0.75,
            ),
            min_insight_salience=env_float(
                "T2T_MIN_INSIGHT_SALIENCE",
                0.65,
            ),
            min_facts_per_bounded_insight=env_int(
                "T2T_MIN_FACTS_PER_BOUNDED_INSIGHT",
                2,
            ),
            allow_hypotheses_in_report=env_bool(
                "T2T_ALLOW_HYPOTHESES_IN_REPORT",
                False,
            ),
            minimum_writer_ready_fact_count=env_int(
                "T2T_MINIMUM_WRITER_READY_FACT_COUNT",
                6,
            ),
            minimum_overview_fact_count=env_int(
                "T2T_MINIMUM_OVERVIEW_FACT_COUNT",
                1,
            ),
            minimum_data_quality_fact_count=env_int(
                "T2T_MINIMUM_DATA_QUALITY_FACT_COUNT",
                1,
            ),
            minimum_relationship_fact_count=env_int(
                "T2T_MINIMUM_RELATIONSHIP_FACT_COUNT",
                2,
            ),
            maximum_recovered_overview_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_OVERVIEW_FACTS",
                2,
            ),
            maximum_recovered_data_quality_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_DATA_QUALITY_FACTS",
                3,
            ),
            maximum_recovered_correlation_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_CORRELATION_FACTS",
                3,
            ),
            maximum_recovered_group_comparison_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_GROUP_COMPARISON_FACTS",
                2,
            ),
            maximum_recovered_modelling_facts=env_int(
                "T2T_MAXIMUM_RECOVERED_MODELLING_FACTS",
                1,
            ),
            max_priority_dataset_overview_facts=env_int(
                "T2T_MAX_PRIORITY_DATASET_OVERVIEW_FACTS",
                2,
            ),
            max_priority_data_quality_facts=env_int(
                "T2T_MAX_PRIORITY_DATA_QUALITY_FACTS",
                3,
            ),
            max_priority_correlation_facts=env_int(
                "T2T_MAX_PRIORITY_CORRELATION_FACTS",
                3,
            ),
            max_priority_group_comparison_facts=env_int(
                "T2T_MAX_PRIORITY_GROUP_COMPARISON_FACTS",
                2,
            ),
            max_priority_predictive_facts=env_int(
                "T2T_MAX_PRIORITY_PREDICTIVE_FACTS",
                1,
            ),
            max_priority_forecast_facts=env_int(
                "T2T_MAX_PRIORITY_FORECAST_FACTS",
                1,
            ),
            max_priority_limitation_facts=env_int(
                "T2T_MAX_PRIORITY_LIMITATION_FACTS",
                2,
            ),
            minimum_main_finding_score=env_float(
                "T2T_MINIMUM_MAIN_FINDING_SCORE",
                0.65,
            ),
            minimum_main_effect_strength=os.getenv(
                "T2T_MINIMUM_MAIN_EFFECT_STRENGTH",
                "moderate",
            ),
            maximum_data_quality_findings=env_int(
                "T2T_MAX_DATA_QUALITY_FINDINGS",
                3,
            ),
            maximum_association_findings=env_int(
                "T2T_MAX_ASSOCIATION_FINDINGS",
                4,
            ),
            maximum_predictive_findings=env_int(
                "T2T_MAX_PREDICTIVE_FINDINGS",
                1,
            ),
            maximum_forecast_findings=env_int(
                "T2T_MAX_FORECAST_FINDINGS",
                1,
            ),
            maximum_limitation_findings=env_int(
                "T2T_MAX_LIMITATION_FINDINGS",
                3,
            ),
            minimum_report_word_ratio=env_float(
                "T2T_MINIMUM_REPORT_WORD_RATIO",
                0.45,
            ),
            minimum_report_word_floor=env_int(
                "T2T_MINIMUM_REPORT_WORD_FLOOR",
                160,
            ),
            maximum_repeated_caveat_mentions=env_int(
                "T2T_MAXIMUM_REPEATED_CAVEAT_MENTIONS",
                4,
            ),
            zero_unusual_rate_threshold=env_float(
                "T2T_ZERO_UNUSUAL_RATE_THRESHOLD",
                0.05,
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
