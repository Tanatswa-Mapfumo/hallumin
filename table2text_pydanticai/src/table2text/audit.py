"""Validate, materialise, repair, and audit evidence-grounded writer output."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from collections import Counter, defaultdict
from typing import Any

import numpy as np
import pandas as pd

from .capabilities import participation_measure_requested
from .schemas import (
    AnalyticalFunction,
    AnalysisRoute,
    AuditAnnotation,
    AuditDecision,
    AuditMode,
    AuditRepairProposal,
    AuditReport,
    ClaimPermission,
    ColumnProfile,
    CommunicationTask,
    DataProfile,
    ErrorType,
    EvidenceCapability,
    EvidenceItem,
    EvidenceLedger,
    ExternalTruthSource,
    FactCandidate,
    FactCandidateSet,
    FactLedger,
    FactReview,
    GenreQualityAssessment,
    InsightContribution,
    InsightLedger,
    InsightType,
    InsightVerificationStatus,
    InputStructureProfile,
    InterpretationLevel,
    OutputForm,
    QualityStatus,
    ProfileSupportRecord,
    RecommendedUse,
    RejectedFact,
    ReleaseStatus,
    RepairCandidate,
    RepairStrategy,
    ReportComponent,
    ReportComponentAssessment,
    ReportGenre,
    ReportPatch,
    ReportQualityAssessment,
    RealisationPolicy,
    ReviewDecision,
    SentenceSupport,
    Severity,
    SupportMapPatch,
    SupportType,
    VerificationMethod,
    VerificationResult,
    VerifiedFact,
    VerifiedInsight,
    WriterAgentDraft,
    WriterEvidencePack,
    WriterOutput,
)
from .config import Settings


NUMBER_PATTERN = re.compile(
    r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?(?!\w|\.(?=\d))"
)
DATE_LIKE_TOKEN_PATTERN = re.compile(
    r"(?<!\w)(\d{1,4})[_/-](\d{1,2})[_/-](\d{1,4})(?!\w)"
)

ABBREVIATION_DOT_PLACEHOLDER = "__T2T_ABBR_DOT__"
INITIALISM_PATTERN = re.compile(r"\b(?:[A-Z]\.){2,}")
SINGLE_INITIAL_PATTERN = re.compile(r"\b([A-Z])\.(?=\s+[A-Z][a-z])")
COMMON_SENTENCE_ABBREVIATION_PATTERN = re.compile(
    r"\b(?:vs|v|etc|e\.g|i\.e)\.",
    re.IGNORECASE,
)

CAUSAL_PATTERN = re.compile(
    r"\b(caused|causes|causing|drives?(?!\s+in\s+\d)|"
    r"drove(?!\s+in\s+\d)|driven by|led to|effect of|"
    r"responsible for|result(?:s|ed|ing)? in|"
    r"contribut(?:e|es|ed|ing) to|because of|due to|explains?)\b",
    re.IGNORECASE,
)

FACTUAL_TITLE_PATTERN = re.compile(
    r"\b(defeats?|defeated|beats?|beat|wins?|won|loses?|lost|"
    r"edges?|edged|outscores?|outscored|leads?|led|draws?|drew|"
    r"ties?|tied|versus|vs\.?)\b",
    re.IGNORECASE,
)

PREDICTIVE_PATTERN = re.compile(
    r"\b(predicts?|predictive|classifier|regressor|out-of-sample|"
    r"deployment|generalises?)\b",
    re.IGNORECASE,
)

FORECAST_PATTERN = re.compile(
    r"\b(forecasts?|forecasted|future values?|will increase|"
    r"will decrease|future performance)\b",
    re.IGNORECASE,
)

APPROXIMATE_PATTERN = re.compile(
    r"\b(about|approximately|around|roughly|nearly|close to|"
    r"more than|over|less than|under)\b",
    re.IGNORECASE,
)

INTERNAL_CONTROL_PATTERN = re.compile(
    r"(?i)\b("
    r"global prohibited interpretations|"
    r"prohibited interpretations|"
    r"interpretation notes|"
    r"recommended use|"
    r"methodological strength|"
    r"user relevance|"
    r"do not say|"
    r"do not describe"
    r")\b"
)

FIELD_LABEL_PATTERN = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?\*{0,2}"
    r"(Finding|Strength|Important Note|Interpretation Notes|"
    r"Recommended Use|Methodological Strength|User Relevance|"
    r"Salience|Global Prohibited Interpretations)"
    r"\*{0,2}\s*:"
)

GENERIC_OPENING_PATTERNS = [
    re.compile(r"\bthis document summarizes\b", re.IGNORECASE),
    re.compile(r"\bthis report provides\b", re.IGNORECASE),
    re.compile(r"\bhere'?s a breakdown\b", re.IGNORECASE),
    re.compile(r"\bthe goal is to provide\b", re.IGNORECASE),
]

CAVEAT_PATTERNS = [
    re.compile(r"does not imply causation", re.IGNORECASE),
    re.compile(r"does not establish causation", re.IGNORECASE),
    re.compile(r"\bunadjusted\b", re.IGNORECASE),
    re.compile(r"\bconfound(?:er|ers|ing)\b", re.IGNORECASE),
]

IMBALANCE_BIAS_PATTERN = re.compile(
    r"\b("
    r"imbalanc\w*[^.!?]{0,80}bias\w*|"
    r"bias\w*[^.!?]{0,80}imbalanc\w*"
    r")\b",
    re.IGNORECASE,
)

UNSANCTIONED_UNIT_TERMS = {
    "event",
    "events",
    "experiment",
    "experiments",
    "subject",
    "subjects",
}

HOURLY_CADENCE_PATTERN = re.compile(
    r"\b(hourly observations?|hourly measurements?|every hour|"
    r"one-hour intervals?)\b",
    re.IGNORECASE,
)

LOCATION_METADATA_PATTERN = re.compile(
    r"\b(specific location|weather station|recorded at a location)\b",
    re.IGNORECASE,
)

CONSTANT_OVERSTATEMENT_PATTERN = re.compile(
    r"\b(no analytical value|useless|worthless|has no value)\b",
    re.IGNORECASE,
)

ZERO_OVERCONFIDENCE_PATTERN = re.compile(
    r"\b(likely represents encoded missingness|definitely represents|"
    r"is measurement failure|must be erroneous)\b",
    re.IGNORECASE,
)

MISSINGNESS_HARMLESS_PATTERN = re.compile(
    r"\b(unlikely to cause major issues|can be safely ignored|"
    r"will not affect the analysis|has no material effect)\b",
    re.IGNORECASE,
)

DUPLICATE_REMOVAL_PATTERN = re.compile(
    r"\b(duplicates?(?: rows?)? should be removed|"
    r"duplicates?(?: rows?)? should likely be removed|"
    r"likely removed|must be removed|automatically deduplicate)\b",
    re.IGNORECASE,
)

PEARSON_IMPRECISE_PATTERN = re.compile(
    r"\bpearson correlation\b[^.!?]{0,100}\b"
    r"(?:is|may be)?\s*influenced by non-linear patterns\b",
    re.IGNORECASE,
)

FUTURE_ANALYSIS_PATTERN = re.compile(
    r"\b(future work should|next analyses should|could model|"
    r"multivariate model|explore temporal trends|"
    r"investigate the relationship)\b",
    re.IGNORECASE,
)

DATASET_GENERALISATION_PATTERN = re.compile(
    r"\b(always|in general|universally|proves that|demonstrates that all)\b",
    re.IGNORECASE,
)

UNSUPPORTED_SPORTS_NARRATIVE_PATTERN = re.compile(
    r"\b(dominated throughout|single-handedly|comeback|turning point|"
    r"all-time classic|historic victory|upset|cruised to victory)\b",
    re.IGNORECASE,
)

SCORE_STATE_TIE_CLAIM_PATTERN = re.compile(
    r"\b(?:game[- ]tying|tie[ds]?\s+(?:the\s+)?game|"
    r"tying\s+(?:the\s+)?game|level(?:led)?\s+(?:the\s+)?score|"
    r"score\s+was\s+level|equali[sz](?:ed|er))\b",
    re.IGNORECASE,
)
NEGATED_SCORE_STATE_TIE_PATTERN = re.compile(
    r"\b(?:could|can|did|does|would|will|was|were|is|are)?\s*"
    r"(?:not|n't|never|failed\s+to|unable\s+to|without)\s+"
    r"(?:tie[ds]?\s+(?:the\s+)?game|tying\s+(?:the\s+)?game|"
    r"level(?:led)?\s+(?:the\s+)?score|"
    r"equali[sz](?:e|ed))\b",
    re.IGNORECASE,
)

INSIGHT_OVERSTATEMENT_PATTERN = re.compile(
    r"\b(completely redundant|universally redundant|should always be removed|"
    r"must always be removed|proves that)\b",
    re.IGNORECASE,
)

HYPOTHESIS_WORDING_PATTERN = re.compile(
    r"\b(hypothesis|hypothesise|hypothesize|question for further "
    r"investigation)\b",
    re.IGNORECASE,
)

UNLABELLED_HYPOTHESIS_PATTERN = re.compile(
    r"\b(may|might|could|likely)\b[^.!?]{0,100}\b"
    r"(because|reflects?|indicates?|explains?|due to)\b",
    re.IGNORECASE,
)

EXPLANATORY_HYPOTHESIS_PATTERN = re.compile(
    r"(?:"
    r"\b(?:may|might|could|possibly|potentially|whether)\b"
    r"[^.!?]{0,180}\b(?:"
    r"reflect(?:s|ed|ing)?|"
    r"result(?:s|ed|ing)?\s+from|"
    r"stems?|stemmed|stemming|"
    r"arises?|arose|arisen|"
    r"be\s+due\s+to|"
    r"be\s+explained\s+by"
    r")\b|"
    r"\b(?:possible|plausible|potential)\s+"
    r"(?:explanation|reason)\b"
    r")",
    re.IGNORECASE,
)

ASSOCIATION_STRENGTH_PATTERN = re.compile(
    r"\b(?P<label>very strong|strong|moderate|weak|negligible)\b"
    r"(?:\s+(?:positive|negative))?"
    r"(?:\s+(?:pearson|spearman|rank-based|linear))?"
    r"\s+(?:correlations?|associations?|relationships?)\b",
    re.IGNORECASE,
)

GROUP_STRENGTH_PATTERN = re.compile(
    r"\b(?P<label>large|moderate|small|negligible)\b"
    r"(?:\s+standard(?:ised|ized))?"
    r"\s+(?:group\s+)?(?:differences?|effect sizes?)\b",
    re.IGNORECASE,
)

INTERPRETIVE_SYNTHESIS_PATTERN = re.compile(
    r"\b(overlapping information|taken together|together suggest|"
    r"combined with|overall pattern|this indicates|this suggests|therefore)\b",
    re.IGNORECASE,
)


def materially_same_report_text(
    left: str,
    right: str,
) -> bool:
    left_normalised = re.sub(
        r"[^a-z0-9]+",
        " ",
        left.lower(),
    ).strip()
    right_normalised = re.sub(
        r"[^a-z0-9]+",
        " ",
        right.lower(),
    ).strip()

    if left_normalised == right_normalised:
        return True

    left_tokens = {
        token
        for token in left_normalised.split()
        if len(token) > 2
    }
    right_tokens = {
        token
        for token in right_normalised.split()
        if len(token) > 2
    }
    if not left_tokens or not right_tokens:
        return False

    return (
        len(left_tokens & right_tokens)
        / len(left_tokens | right_tokens)
        >= 0.8
    )

PROFILE_FACT_KIND_TERMS = {
    "table_dimensions": re.compile(
        r"\b(rows?|columns?|observations?|records?)\b",
        re.IGNORECASE,
    ),
    "duplicate_rows": re.compile(
        r"\b(duplicate|duplicates|duplicate rows?)\b",
        re.IGNORECASE,
    ),
    "column_missingness": re.compile(
        r"\b(missing|missingness)\b",
        re.IGNORECASE,
    ),
    "constant_column": re.compile(
        r"\b(constant|all zeros?|no observed variation)\b",
        re.IGNORECASE,
    ),
    "near_constant_column": re.compile(
        r"\b(near-constant|near constant|dominant value)\b",
        re.IGNORECASE,
    ),
    "numeric_summary": re.compile(
        r"\b(mean|median|minimum|maximum|standard deviation)\b",
        re.IGNORECASE,
    ),
    "zero_diagnostic": re.compile(
        r"\b(zero|zeros|sentinel)\b",
        re.IGNORECASE,
    ),
    "datetime_presence": re.compile(
        r"\b(date|datetime|timestamp|time column)\b",
        re.IGNORECASE,
    ),
    "candidate_key": re.compile(
        r"\b(candidate key|unique identifier)\b",
        re.IGNORECASE,
    ),
}

QUALITY_STATUS_ORDER = {
    QualityStatus.PASS: 0,
    QualityStatus.WARNING: 1,
    QualityStatus.REVISE: 2,
}


def count_caveat_mentions(markdown: str) -> int:
    return sum(len(pattern.findall(markdown)) for pattern in CAVEAT_PATTERNS)


def minimum_useful_report_words(
    *,
    target_words: int,
    required_component_count: int,
    settings: Settings,
) -> int:
    """
    Return a diagnostic minimum that never exceeds the planned target.
    """

    bounded_target = max(1, target_words)

    ratio_floor = int(
        bounded_target
        * settings.minimum_report_word_ratio
    )

    component_floor = (
        required_component_count * 45
    )

    desired_minimum = max(
        settings.minimum_report_word_floor,
        ratio_floor,
        component_floor,
    )

    return min(
        bounded_target,
        desired_minimum,
    )

def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value

    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        number = float(value)
        return None if math.isnan(number) or math.isinf(number) else number

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]

    if hasattr(value, "model_dump"):
        return json_safe(value.model_dump(mode="json"))

    return str(value)


def compact_json(value: Any) -> str:
    """Serialize complete model context without whitespace or invalid truncation."""
    return json.dumps(
        json_safe(value),
        ensure_ascii=False,
        separators=(",", ":"),
    )


def flatten_numbers(value: Any) -> list[float]:
    numbers: list[float] = []

    if isinstance(value, bool) or value is None:
        return numbers

    if isinstance(value, (int, float, np.integer, np.floating)):
        number = float(value)
        if math.isfinite(number):
            numbers.append(number)
        return numbers

    if isinstance(value, str):
        token = value.strip()
        if NUMBER_PATTERN.fullmatch(token):
            percentage = token.endswith("%")
            number = float(token.rstrip("%").replace(",", ""))
            if percentage:
                number /= 100.0
            if math.isfinite(number):
                numbers.append(number)
        return numbers

    if isinstance(value, dict):
        for item in value.values():
            numbers.extend(flatten_numbers(item))
        return numbers

    if isinstance(value, (list, tuple, set)):
        for item in value:
            numbers.extend(flatten_numbers(item))

    return numbers


def extract_number_tokens(text: str) -> list[tuple[str, float]]:
    tokens: list[tuple[str, float]] = []

    for raw in NUMBER_PATTERN.findall(text or ""):
        percentage = raw.endswith("%")
        cleaned = raw.rstrip("%").replace(",", "")

        try:
            number = float(cleaned)
        except ValueError:
            continue

        if percentage:
            number /= 100.0

        tokens.append((raw, number))

    for match in DATE_LIKE_TOKEN_PATTERN.finditer(text or ""):
        parts = [part for part in match.groups()]
        for part in parts:
            try:
                tokens.append((part, float(part)))
            except ValueError:
                continue
        if len(parts[-1]) == 2 and len(parts[0]) != 4:
            try:
                year = int(parts[-1])
            except ValueError:
                continue
            tokens.append((f"20{year:02d}", float(2000 + year)))

    return tokens


def number_supported(
    raw_token: str,
    number: float,
    support_numbers: list[float],
    sentence: str,
) -> bool:
    """
    Check whether a rendered number is supported.

    The tolerance accounts for ordinary display rounding. This is
    particularly important for percentages, where a deterministic
    value such as 0.005359 may be rendered as 0.54%.
    """

    approximate = bool(
        APPROXIMATE_PATTERN.search(sentence)
    )

    token_without_percent = (
        raw_token.rstrip("%").replace(",", "")
    )

    if "." in token_without_percent:
        decimal_places = len(
            token_without_percent.split(".", 1)[1]
        )
    else:
        decimal_places = 0

    displayed_resolution = 10.0 ** (-decimal_places)

    if raw_token.endswith("%"):
        displayed_resolution /= 100.0

    rounding_tolerance = (
        displayed_resolution / 2.0
    ) + 1e-12

    for candidate in support_numbers:
        relative_tolerance = max(
            1e-6,
            abs(candidate) * 0.001,
        )

        exact_tolerance = max(
            rounding_tolerance,
            relative_tolerance,
        )

        if abs(number - candidate) <= exact_tolerance:
            return True

        if approximate:
            approximate_tolerance = max(
                displayed_resolution,
                0.01,
                abs(candidate) * 0.03,
            )

            if (
                abs(number - candidate)
                <= approximate_tolerance
            ):
                return True

        digits = token_without_percent

        if (
            "." not in digits
            and len(digits) >= 4
            and digits.endswith("000")
        ):
            if abs(number - candidate) <= 500:
                return True

    return False

def numbers_supported(
    text: str,
    support_numbers: list[float],
) -> bool:
    return all(
        number_supported(
            raw_token,
            number,
            support_numbers,
            text,
        )
        for raw_token, number in extract_number_tokens(text)
    )


def protect_sentence_abbreviations(text: str) -> str:
    def replace_initialism(match: re.Match[str]) -> str:
        return match.group(0).replace(
            ".",
            ABBREVIATION_DOT_PLACEHOLDER,
        )

    protected = INITIALISM_PATTERN.sub(
        replace_initialism,
        text,
    )
    protected = COMMON_SENTENCE_ABBREVIATION_PATTERN.sub(
        replace_initialism,
        protected,
    )
    return SINGLE_INITIAL_PATTERN.sub(
        rf"\1{ABBREVIATION_DOT_PLACEHOLDER}",
        protected,
    )


def restore_sentence_abbreviations(text: str) -> str:
    return text.replace(
        ABBREVIATION_DOT_PLACEHOLDER,
        ".",
    )


def split_markdown_sentences(markdown: str) -> list[str]:
    sentences: list[str] = []

    for raw_line in (markdown or "").splitlines():
        line = raw_line.strip()

        if (
            not line
            or line.startswith("#")
            or line.startswith("|")
            or line.startswith("```")
        ):
            continue

        line = re.sub(r"^[-*]\s+", "", line)
        line = protect_sentence_abbreviations(line)

        parts = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9`])",
            line,
        )

        sentences.extend(
            restore_sentence_abbreviations(part.strip())
            for part in parts
            if part.strip()
        )

    return sentences


def looks_factual(sentence: str) -> bool:
    return bool(
        extract_number_tokens(sentence)
        or re.search(
            r"\b(dataset|table|rows?|columns?|mean|median|correlations?|"
            r"associations?|relationships?|"
            r"model|forecast|missing|missingness|temperature|humidity|visibility|"
            r"higher|lower|increase|decrease|associated|observed|"
            r"duplicate|constant|zeros?|sentinel|timestamp|hourly|"
            r"location|station|pearson|future work|next analyses|"
            r"team|player|game|match|won|scored|points?|rebounds?|"
            r"turnovers?|comeback|dominated|historic|upset)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def build_evidence_lookup(
    ledger: EvidenceLedger,
) -> dict[str, EvidenceItem]:
    return {
        item.evidence_id: item
        for item in ledger.items
    }


def evidence_lookup(
    ledger: EvidenceLedger,
) -> dict[str, EvidenceItem]:
    return build_evidence_lookup(ledger)


def evidence_for_fact(
    fact: VerifiedFact,
    lookup: dict[str, EvidenceItem],
) -> list[EvidenceItem]:
    return [
        lookup[evidence_id]
        for evidence_id in fact.evidence_ids
        if evidence_id in lookup
    ]


EVENT_CONTENT_UNIT_DEFINITIONS = {
    "event_result": {
        "description": "State the supported event result or outcome.",
        "evidence_types": {"event_outcome"},
        "minimum": 1,
    },
    "event_context": {
        "description": "Include supplied event-level time or location context.",
        "evidence_types": {"event_context"},
        "minimum": 1,
    },
    "event_status": {
        "description": "Include supplied event status when available.",
        "evidence_types": {"event_status"},
        "minimum": 1,
    },
    "participant_record_context": {
        "description": (
            "Include supplied participant record or standing context when "
            "it helps frame the event."
        ),
        "evidence_types": {"participant_record_context"},
        "minimum": 1,
    },
    "score_progression": {
        "description": (
            "Use supplied segment-level score progression when it is available."
        ),
        "evidence_types": {"score_progression"},
        "minimum": 1,
    },
    "event_sequence": {
        "description": (
            "Use supplied ordered event-sequence or score-changing evidence "
            "when it is available."
        ),
        "evidence_types": {"event_sequence"},
        "minimum": 1,
    },
    "leading_performance": {
        "description": (
            "Use leading entity rankings or entity-performance facts."
        ),
        "evidence_types": {"entity_ranking", "entity_performance"},
        "minimum": 2,
    },
    "main_contrast": {
        "description": "Use participant-level contrasts supported by evidence.",
        "evidence_types": {
            "participant_comparison",
            "event_contrast",
            "group_comparison",
        },
        "minimum": 2,
    },
    "secondary_performance": {
        "description": "Use additional supported entity rankings if available.",
        "evidence_types": {"entity_ranking", "entity_performance"},
        "minimum": 1,
    },
}


EVENT_NARRATIVE_CONNECTOR_PATTERN = re.compile(
    r"\b("
    r"while|whereas|despite|although|however|but|in contrast|compared with|"
    r"compared to|than|more|fewer|less|higher|lower|advantage|margin|"
    r"followed by|also|both|combined|concentrated|balanced"
    r")\b",
    re.IGNORECASE,
)

EVENT_SCOPE_LIMITATION_PATTERN = re.compile(
    r"\b("
    r"describe(?:s|d)? only|supplied event|single event|this event|"
    r"this game|broader performance|broader outcomes|generaliz|"
    r"does not establish why|do not establish why|does not imply|"
    r"do not imply|not evidence of causal|does not establish causality|"
    r"do not establish causality|does not establish causal|"
    r"do not establish causal|limited to values present|"
    r"limited to (?:the )?supplied|scope limitations?|"
    r"rankings? (?:are|is) limited"
    r")\b",
    re.IGNORECASE,
)
EVENT_SEQUENCE_ABSENCE_PATTERN = re.compile(
    r"\b(?:does not|do not|cannot|can't|lacks?|missing|without)\b"
    r"(?:(?!\.).){0,120}"
    r"\b(?:chronolog(?:y|ical)|sequence|timeline|progression|"
    r"event dynamics|game dynamics|score(?:ing)? state|score(?:ing)? "
    r"progression|play[- ]?by[- ]?play)\b",
    re.IGNORECASE,
)
EVENT_SEQUENCE_OMISSION_PATTERN = re.compile(
    r"\b(?:this\s+)?(?:report|summary)\b[^.]{0,120}"
    r"\b(?:does\s+not|did\s+not|not|no)\b[^.]{0,80}"
    r"\b(?:analy[sz]e[ds]?|include[ds]?|report(?:ed)?|cover(?:ed)?)\b|"
    r"\b(?:detailed\s+)?(?:event\s+)?(?:chronology|play[- ]by[- ]play|"
    r"sequence)\b[^.]{0,120}\b(?:not|no)\b[^.]{0,80}"
    r"\b(?:analy[sz]ed|included|reported|covered)\b",
    re.IGNORECASE,
)
EVENT_SEGMENT_RANKING_PATTERN = re.compile(
    r"\b(?:inning|half(?:-|\s)?inning|period|quarter|round|segment|"
    r"phase|frame|set|leg|stage|play|turn|timeline|sequence)\b",
    re.IGNORECASE,
)
EVENT_LOW_PRIORITY_ENTITY_METRIC_PATTERN = re.compile(
    r"\b(?:against|allowed|at\s+bats?|batters?\s+faced|blown|career|"
    r"conceded|earned|errors?|holds?|loss(?:es)?|number\s+of\s+pitches|"
    r"pitch(?:es)?|putouts?|season|strikes?|turnovers?)\b",
    re.IGNORECASE,
)
EVENT_RECAP_CORE_ENTITY_METRIC_PATTERN = re.compile(
    r"\b(?:assists?|blocks?|doubles?|goals?|hits?|home runs?|points?|"
    r"rebounds?|runs(?: batted in)?|saves?|scor(?:e|ed|ing)|steals?|"
    r"strikeouts?|triples?)\b",
    re.IGNORECASE,
)
EVENT_RECAP_LOW_PRIORITY_METRIC_PATTERN = re.compile(
    r"\b(?:attempt(?:ed|s)?|capacity|field[- ]?goal percentage|"
    r"free[- ]?throw percentage|game number|minutes?|personal fouls?|"
    r"shoot(?:ing)? percentage|three[- ]?point percentage|"
    r"turnovers?)\b",
    re.IGNORECASE,
)


def _fact_ids_for_evidence_types(
    *,
    facts: list[VerifiedFact],
    evidence_lookup: dict[str, EvidenceItem],
    evidence_types: set[str],
) -> list[str]:
    return [
        fact.fact_id
        for fact in facts
        if any(
            item.evidence_type in evidence_types
            for item in evidence_for_fact(
                fact,
                evidence_lookup,
            )
        )
    ]


def _insight_ids_for_fact_ids(
    *,
    insights: list[VerifiedInsight],
    fact_ids: set[str],
) -> list[str]:
    return [
        insight.insight_id
        for insight in insights
        if set(insight.source_fact_ids) & fact_ids
    ]


def sentence_support_narrative_stats(
    sentence_support: list[Any],
) -> dict[str, int]:
    stats = {
        "synthesis_sentences": 0,
        "insight_sentences": 0,
        "connective_sentences": 0,
        "scope_limitation_sentences": 0,
    }

    for support in sentence_support:
        text = (
            getattr(support, "sentence_text", None)
            or getattr(support, "text", "")
            or ""
        )
        fact_ids = set(getattr(support, "fact_ids", []))
        evidence_ids = set(getattr(support, "evidence_ids", []))
        insight_ids = set(getattr(support, "insight_ids", []))
        support_type = getattr(support, "support_type", None)
        interpretation_level = getattr(
            support,
            "interpretation_level",
            None,
        )

        support_item_count = len(fact_ids | evidence_ids) + len(insight_ids)
        is_insight_sentence = bool(insight_ids) and (
            interpretation_level == InterpretationLevel.BOUNDED_INSIGHT
        )
        is_synthesis_sentence = (
            support_type == SupportType.MULTI_FACT_SYNTHESIS
            or is_insight_sentence
            or support_item_count >= 2
        )

        if is_synthesis_sentence:
            stats["synthesis_sentences"] += 1
            if EVENT_NARRATIVE_CONNECTOR_PATTERN.search(text):
                stats["connective_sentences"] += 1

        if is_insight_sentence:
            stats["insight_sentences"] += 1

        if EVENT_SCOPE_LIMITATION_PATTERN.search(text):
            stats["scope_limitation_sentences"] += 1

    return stats


def event_scope_limitation_present(
    writer_output: WriterOutput,
) -> bool:
    return bool(
        EVENT_SCOPE_LIMITATION_PATTERN.search(
            writer_output.markdown
        )
    )


def build_writer_content_requirements(
    *,
    report_specification: Any,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    insight_ledger: InsightLedger,
    settings: Settings,
) -> dict[str, Any]:
    minimum_words = minimum_useful_report_words(
        target_words=report_specification.target_length_words,
        required_component_count=len(
            report_specification.required_components
        ),
        settings=settings,
    )

    communication_task = getattr(
        report_specification,
        "communication_task",
        None,
    )
    output_form = getattr(
        report_specification,
        "output_form",
        None,
    )
    realisation_policy = getattr(
        report_specification,
        "realisation_policy",
        RealisationPolicy.STRICT_SOURCE_SURFACE,
    )
    realisation_policy_value = (
        realisation_policy.value
        if isinstance(realisation_policy, RealisationPolicy)
        else str(realisation_policy)
    )
    if communication_task == CommunicationTask.FOCUSED_TABLE_DESCRIPTION:
        lookup = build_evidence_lookup(evidence)
        candidate_fact_ids = _fact_ids_for_evidence_types(
            facts=fact_ledger.writer_ready_facts,
            evidence_lookup=lookup,
            evidence_types={"focused_table_region", "focused_cell_context"},
        )
        candidate_insight_ids = [
            insight.insight_id
            for insight in insight_ledger.verified_insights
            if (
                EvidenceCapability.FOCUSED_TABLE_REGION
                in insight.source_capabilities
            )
        ]
        units = []
        if candidate_fact_ids or candidate_insight_ids:
            units.append(
                {
                    "unit_id": "focused_table_region",
                    "description": (
                        "Express the concise relation conveyed by the "
                        "selected table cell or focused region using its "
                        "supplied row, header, table and source-text context."
                    ),
                    "minimum_items": 1,
                    "candidate_fact_ids": candidate_fact_ids,
                    "candidate_insight_ids": candidate_insight_ids,
                }
            )
        return {
            "minimum_word_count": 1,
            "enforce_minimum_words": False,
            "output_form": (
                output_form.value
                if isinstance(output_form, OutputForm)
                else str(output_form or OutputForm.ONE_SENTENCE.value)
            ),
            "allow_headings": False,
            "max_sentences": getattr(report_specification, "max_sentences", 1) or 1,
            "max_paragraphs": getattr(report_specification, "max_paragraphs", 1) or 1,
            "require_complete_sentence": True,
            "realisation_policy": realisation_policy_value,
            "style_rewrite_permissions": {
                "may_normalise_identifier_separators": False,
                "must_preserve_numbers_exactly": True,
                "must_preserve_percentages_exactly": True,
                "must_not_add_caveats": True,
                "must_not_add_headings": True,
            },
            "short_form_selection_policy": {
                "prefer_highlighted_role_value_pairs": True,
                "prefer_primary_subject_candidate": True,
                "treat_non_highlighted_row_values_as_context": True,
                "omit_secondary_numeric_values_unless_needed": True,
                "avoid_joint_subject_without_combined_entity_evidence": True,
                "use_supplied_highlighted_measure_comparisons": True,
                "use_supplied_highlighted_set_contrasts": True,
                "use_supplied_highlighted_record_groups": True,
                "use_supplied_focused_record_relations": True,
                "use_supplied_focused_list_relations": True,
                "scope_lower_higher_to_highlighted_set": True,
                "preserve_numeric_surface_forms": True,
                "preserve_identifier_surface_forms": True,
                "avoid_spelling_out_numbers": True,
            },
            "units": units,
        }

    if communication_task in {
        CommunicationTask.ATTRIBUTE_VERBALISATION,
        CommunicationTask.TRIPLE_VERBALISATION,
    }:
        lookup = build_evidence_lookup(evidence)
        candidate_fact_ids = _fact_ids_for_evidence_types(
            facts=fact_ledger.writer_ready_facts,
            evidence_lookup=lookup,
            evidence_types={
                "attribute_record",
                "triple_record",
                "structured_record",
            },
        )
        candidate_insight_ids = [
            insight.insight_id
            for insight in insight_ledger.verified_insights
            if (
                EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
                in insight.source_capabilities
            )
        ]
        units = []
        if candidate_fact_ids or candidate_insight_ids:
            units.append(
                {
                    "unit_id": "structured_record_verbalisation",
                    "description": (
                        "Express all and only the supplied attributes or "
                        "triples as concise natural language. Do not add "
                        "dataset-profile, data-quality, correlation or "
                        "modelling discussion."
                    ),
                    "minimum_items": 1,
                    "candidate_fact_ids": candidate_fact_ids,
                    "candidate_insight_ids": candidate_insight_ids,
                }
            )
        return {
            "minimum_word_count": 1,
            "enforce_minimum_words": False,
            "output_form": (
                output_form.value
                if isinstance(output_form, OutputForm)
                else str(output_form or OutputForm.SHORT_TEXT.value)
            ),
            "allow_headings": False,
            "max_sentences": getattr(report_specification, "max_sentences", 2) or 2,
            "max_paragraphs": getattr(report_specification, "max_paragraphs", 1) or 1,
            "require_complete_sentence": True,
            "realisation_policy": realisation_policy_value,
            "style_rewrite_permissions": {
                "may_normalise_identifier_separators": (
                    realisation_policy_value
                    == RealisationPolicy.NATURAL_REFERENCE_STYLE.value
                ),
                "may_humanise_relation_labels": True,
                "must_preserve_numbers_exactly": True,
                "must_preserve_units": True,
                "must_not_add_caveats": True,
                "must_not_add_headings": True,
            },
            "short_form_selection_policy": {
                "use_all_supplied_records": True,
                "prefer_natural_phrasing": True,
                "avoid_key_value_dump_when_relation_is_clear": True,
                "do_not_add_unsupplied_attributes": True,
                "do_not_discuss_dataset_profile": True,
                "preserve_numeric_surface_forms": True,
                "preserve_identifier_surface_forms": True,
                "avoid_spelling_out_numbers": True,
                "preserve_units_compactly": True,
                "prefer_ordinal_rank_phrasing": True,
            },
            "units": units,
        }

    event_report = report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }
    if not event_report:
        return {
            "minimum_word_count": minimum_words,
            "enforce_minimum_words": False,
            "units": [],
        }

    reference_recap_style = (
        getattr(report_specification, "focus_scope", None)
        == "reference_recap"
    )
    event_recap_style = (
        realisation_policy_value
        == RealisationPolicy.EVENT_RECAP_STYLE.value
    )
    lookup = build_evidence_lookup(evidence)
    facts = fact_ledger.writer_ready_facts
    insights = [
        insight
        for insight in insight_ledger.verified_insights
        if insight.verification_status
        in {
            InsightVerificationStatus.VERIFIED,
            InsightVerificationStatus.VERIFIED_WITH_CAVEAT,
        }
    ]

    units: list[dict[str, Any]] = []
    ordered_slots = [
        *report_specification.required_content_slots,
        *report_specification.optional_content_slots,
    ]
    if event_report:
        slot_priority = {
            "event_result": 0,
            "event_context": 1,
            "participant_record_context": 2,
            "event_status": 3,
            "score_progression": 4,
            "leading_performance": 5,
            "main_contrast": 6,
            "event_sequence": 7,
            "secondary_performance": 8,
            "scope_limitations": 9,
        }
        ordered_slots = sorted(
            dict.fromkeys(ordered_slots),
            key=lambda slot: (
                slot_priority.get(slot, 100),
                ordered_slots.index(slot),
            ),
        )
    for slot in dict.fromkeys(ordered_slots):
        definition = EVENT_CONTENT_UNIT_DEFINITIONS.get(slot)
        if definition is None:
            continue

        candidate_fact_ids = [
            fact.fact_id
            for fact in facts
            if (
                fact.recommended_use
                != RecommendedUse.OMIT_UNLESS_REQUESTED
                and event_fact_slot(fact, lookup) == slot
            )
        ]
        if slot == "event_sequence":
            actionable_candidate_fact_ids = [
                fact.fact_id
                for fact in facts
                if (
                    fact.fact_id in candidate_fact_ids
                    and event_sequence_fact_is_actionable(fact, lookup)
                )
            ]
            if actionable_candidate_fact_ids:
                candidate_fact_ids = actionable_candidate_fact_ids
        if not candidate_fact_ids:
            continue

        candidate_insight_ids = _insight_ids_for_fact_ids(
            insights=insights,
            fact_ids=set(candidate_fact_ids),
        )
        minimum_items = min(
            int(definition["minimum"]),
            len(candidate_fact_ids),
        )
        units.append(
            {
                "unit_id": slot,
                "description": definition["description"],
                "minimum_items": minimum_items,
                "candidate_fact_ids": candidate_fact_ids,
                "candidate_insight_ids": candidate_insight_ids,
                "candidate_insight_fact_ids": {
                    insight.insight_id: [
                        fact_id
                        for fact_id in insight.source_fact_ids
                        if fact_id in candidate_fact_ids
                    ]
                    for insight in insights
                    if insight.insight_id in candidate_insight_ids
                },
            }
        )

    substantive_unit_count = sum(
        1
        for unit in units
        if unit["unit_id"]
        in {
            "event_result",
            "event_context",
            "participant_record_context",
            "score_progression",
            "event_sequence",
            "leading_performance",
            "main_contrast",
        }
    )
    main_contrast_available = any(
        unit["unit_id"] == "main_contrast"
        and len(unit.get("candidate_fact_ids", [])) >= 2
        for unit in units
    )
    insight_available = any(
        unit.get("candidate_insight_ids")
        for unit in units
    )
    enforce_narrative = bool(
        substantive_unit_count >= 3
        and len(facts) >= 5
    )

    return {
        "minimum_word_count": minimum_words,
        "word_count_validation": "quality",
        "narrative_validation": "quality",
        "content_unit_validation": "quality",
        "enforce_minimum_words": bool(
            enforce_narrative
        ),
        "realisation_policy": realisation_policy_value,
        "style_rewrite_permissions": {
            "may_normalise_identifier_separators": (
                realisation_policy_value
                in {
                    RealisationPolicy.NATURAL_REFERENCE_STYLE.value,
                    RealisationPolicy.EVENT_RECAP_STYLE.value,
                }
            ),
            "may_compress_caveats": reference_recap_style,
            "may_use_reference_style_event_transitions": (
                realisation_policy_value
                == RealisationPolicy.EVENT_RECAP_STYLE.value
            ),
            "must_preserve_numbers_exactly": True,
            "must_not_add_unsupported_chronology": True,
            "must_not_add_unsupported_causality": True,
        },
        "output_form": (
            output_form.value
            if isinstance(output_form, OutputForm)
            else str(output_form or OutputForm.MULTI_PARAGRAPH_REPORT.value)
        ),
        "allow_headings": False if reference_recap_style else True,
        "reference_recap_style": reference_recap_style,
        "event_recap_style": event_recap_style,
        "narrative_requirements": {
            "enforce": enforce_narrative,
            "minimum_synthesis_sentences": 2,
            "minimum_insight_sentences": 1 if insight_available else 0,
            "minimum_connective_sentences": (
                1 if main_contrast_available else 0
            ),
            "minimum_scope_limitations": (
                0 if reference_recap_style else 1
            ),
        },
        "units": units,
    }


def content_requirement_errors(
    *,
    used_fact_ids: set[str],
    used_insight_ids: set[str],
    word_count: int,
    requirements: dict[str, Any] | None,
    narrative_stats: dict[str, int] | None = None,
    include_word_count: bool = True,
    respect_validation_severity: bool = True,
) -> list[str]:
    if not requirements:
        return []

    errors: list[str] = []
    word_count_validation_is_fatal = (
        not respect_validation_severity
        or requirements.get("word_count_validation", "fatal") == "fatal"
    )
    narrative_validation_is_fatal = (
        not respect_validation_severity
        or requirements.get("narrative_validation", "fatal") == "fatal"
    )
    content_unit_validation_is_fatal = (
        not respect_validation_severity
        or requirements.get("content_unit_validation", "fatal") == "fatal"
    )
    minimum_words = requirements.get("minimum_word_count")
    if (
        include_word_count
        and word_count_validation_is_fatal
        and requirements.get("enforce_minimum_words")
        and minimum_words is not None
        and word_count < int(minimum_words)
    ):
        errors.append(
            f"The draft contains {word_count} words; at least "
            f"{minimum_words} words are required while supported content "
            "remains available."
            )

    narrative = requirements.get("narrative_requirements") or {}
    if (
        narrative_validation_is_fatal
        and narrative.get("enforce")
        and narrative_stats is not None
    ):
        for field, stat_key, label in [
            (
                "minimum_synthesis_sentences",
                "synthesis_sentences",
                "multi-fact or insight-backed narrative sentences",
            ),
            (
                "minimum_insight_sentences",
                "insight_sentences",
                "verified insight-backed narrative sentences",
            ),
            (
                "minimum_connective_sentences",
                "connective_sentences",
                "contrastive or connective narrative sentences",
            ),
            (
                "minimum_scope_limitations",
                "scope_limitation_sentences",
                "event-scoped limitation sentences",
            ),
        ]:
            minimum = int(narrative.get(field, 0) or 0)
            if minimum <= 0:
                continue
            observed = int(
                narrative_stats.get(
                    stat_key,
                    0,
                )
            )
            if observed < minimum:
                errors.append(
                    f"The event draft uses {observed} {label}, but "
                    f"{minimum} are required when supported event material "
                    "is available."
                )

    if not content_unit_validation_is_fatal:
        return errors

    for unit in requirements.get("units", []):
        candidate_fact_ids = set(unit.get("candidate_fact_ids", []))
        candidate_insight_ids = set(unit.get("candidate_insight_ids", []))
        if not candidate_fact_ids and not candidate_insight_ids:
            continue
        covered_fact_ids = candidate_fact_ids & used_fact_ids
        insight_fact_coverage = unit.get("candidate_insight_fact_ids") or {}
        for insight_id in candidate_insight_ids & used_insight_ids:
            covered_fact_ids.update(
                fact_id
                for fact_id in insight_fact_coverage.get(insight_id, [])
                if fact_id in candidate_fact_ids
            )
        covered_insight_ids = {
            insight_id
            for insight_id in candidate_insight_ids & used_insight_ids
            if not insight_fact_coverage.get(insight_id)
        }
        covered_items = covered_fact_ids | covered_insight_ids
        minimum_items = int(unit.get("minimum_items", 1))
        if len(covered_items) < minimum_items:
            errors.append(
                f"Content unit `{unit.get('unit_id')}` uses "
                f"{len(covered_items)} supported item(s), but "
                f"{minimum_items} are required: "
                f"{unit.get('description')}"
            )

    return errors


def writer_output_content_requirement_errors(
    *,
    writer_output: WriterOutput,
    requirements: dict[str, Any] | None,
    include_word_count: bool = False,
    respect_validation_severity: bool = True,
) -> list[str]:
    requirements = requirements or {}
    used_fact_ids = {
        *writer_output.title_fact_ids,
        *[
            fact_id
            for support in writer_output.sentence_support
            for fact_id in support.fact_ids
        ],
    }
    used_insight_ids = {
        insight_id
        for support in writer_output.sentence_support
            for insight_id in support.insight_ids
    }
    errors = content_requirement_errors(
        used_fact_ids=used_fact_ids,
        used_insight_ids=used_insight_ids,
        word_count=writer_output_word_count(writer_output),
        requirements=requirements,
        narrative_stats=sentence_support_narrative_stats(
            writer_output.sentence_support
        ),
        include_word_count=include_word_count,
        respect_validation_severity=respect_validation_severity,
    )
    if requirements.get("allow_headings") is False and re.search(
        r"(?m)^#{1,6}\s+",
        writer_output.markdown,
    ):
        errors.append("The output must not contain Markdown headings.")

    max_sentences = requirements.get("max_sentences")
    if max_sentences is not None:
        sentence_count = len(
            split_markdown_sentences(writer_output.markdown)
        )
        if sentence_count > int(max_sentences):
            errors.append(
                f"The output contains {sentence_count} sentences; at most "
                f"{max_sentences} are allowed for this output form."
            )

    max_paragraphs = requirements.get("max_paragraphs")
    if max_paragraphs is not None:
        paragraphs = [
            paragraph
            for paragraph in re.split(
                r"\n\s*\n",
                writer_output.markdown.strip(),
            )
            if paragraph.strip()
        ]
        if len(paragraphs) > int(max_paragraphs):
            errors.append(
                f"The output contains {len(paragraphs)} paragraphs; at most "
                f"{max_paragraphs} are allowed for this output form."
            )

    if requirements.get("require_complete_sentence"):
        text = writer_output.markdown.strip()
        if text and text[-1] not in ".!?":
            errors.append("The output must be a complete sentence.")

    return errors


def fact_support_numbers(
    fact: VerifiedFact,
    evidence: EvidenceLedger,
) -> list[float]:
    lookup = evidence_lookup(evidence)
    numbers = [
        number
        for _, number in extract_number_tokens(fact.fact_summary)
    ]
    numbers.extend(flatten_numbers(fact.structured_values))

    for evidence_id in fact.evidence_ids:
        item = lookup.get(evidence_id)
        if item is not None:
            numbers.extend(flatten_numbers(item.metrics))

    return numbers


def fact_support_text(
    fact: VerifiedFact,
    evidence: EvidenceLedger,
) -> str:
    lookup = evidence_lookup(evidence)

    parts = [
        fact.fact_summary,
        " ".join(fact.allowed_interpretations),
        " ".join(fact.required_caveats),
    ]

    for evidence_id in fact.evidence_ids:
        item = lookup.get(evidence_id)

        if item is None:
            continue

        parts.extend(
            [
                item.finding,
                item.practical_interpretation,
                json.dumps(json_safe(item.metrics), sort_keys=True),
                " ".join(item.source_columns),
            ]
        )

    return " ".join(parts)


def _normalise_entity_text(value: str) -> str:
    text = value.replace("_", " ")
    text = re.sub(
        r"(?<=[A-Za-z])(?=[A-Z][a-z])",
        " ",
        text,
    )
    return re.sub(
        r"\s+",
        " ",
        text.replace("`", "").strip().casefold(),
    )


def unsupported_backtick_entities(
    text: str,
    supported_entities: set[str],
) -> list[str]:
    normalised_supported = {
        _normalise_entity_text(entity)
        for entity in supported_entities
        if _normalise_entity_text(entity)
    }

    return list(
        dict.fromkeys(
            entity
            for entity in re.findall(r"`([^`]+)`", text)
            if _normalise_entity_text(entity)
            not in normalised_supported
        )
    )


def _entity_in_sentence(
    entity: str,
    sentence: str,
) -> bool:
    entity_text = _normalise_entity_text(entity)
    sentence_text = _normalise_entity_text(sentence)

    return bool(
        entity_text
        and re.search(
            rf"(?<!\w){re.escape(entity_text)}(?!\w)",
            sentence_text,
        )
    )


def _profile_support_id(
    *parts: str,
) -> str:
    return "PROFILE::" + "::".join(parts)


def _profile_record(
    *,
    support_id: str,
    fact_kind: str,
    table_name: str,
    column_name: str | None,
    statement: str,
    structured_values: dict[str, Any],
    entities: list[str],
    provenance: str,
    claim_permissions: list[ClaimPermission] | None = None,
) -> ProfileSupportRecord:
    return ProfileSupportRecord(
        support_id=support_id,
        fact_kind=fact_kind,
        table_name=table_name,
        column_name=column_name,
        statement=statement,
        structured_values=structured_values,
        entities=list(dict.fromkeys(entities)),
        claim_permissions=(
            claim_permissions
            or [ClaimPermission.DESCRIPTIVE]
        ),
        provenance=provenance,
    )


def _column_numeric_summary_values(
    column: ColumnProfile,
) -> dict[str, Any]:
    return {
        key: value
        for key, value in column.numeric_summary.items()
        if isinstance(value, (int, float, np.integer, np.floating))
        and math.isfinite(float(value))
    }


def build_profile_support_registry(
    profile: DataProfile,
) -> list[ProfileSupportRecord]:
    records: list[ProfileSupportRecord] = []

    for table in profile.tables:
        records.append(
            _profile_record(
                support_id=_profile_support_id(
                    table.table_name,
                    "dimensions",
                ),
                fact_kind="table_dimensions",
                table_name=table.table_name,
                column_name=None,
                statement=(
                    f"Table `{table.table_name}` contains "
                    f"{table.row_count:,} rows and "
                    f"{table.column_count:,} columns."
                ),
                structured_values={
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                },
                entities=[table.table_name],
                provenance="deterministic_data_profile",
            )
        )

        duplicate_rate = (
            table.duplicate_row_count
            / max(table.row_count, 1)
        )
        records.append(
            _profile_record(
                support_id=_profile_support_id(
                    table.table_name,
                    "duplicates",
                ),
                fact_kind="duplicate_rows",
                table_name=table.table_name,
                column_name=None,
                statement=(
                    f"Table `{table.table_name}` contains "
                    f"{table.duplicate_row_count:,} exact duplicate rows "
                    f"({duplicate_rate:.2%} of rows)."
                ),
                structured_values={
                    "duplicate_row_count": table.duplicate_row_count,
                    "duplicate_row_rate": duplicate_rate,
                    "row_count": table.row_count,
                },
                entities=[table.table_name],
                claim_permissions=[
                    ClaimPermission.DESCRIPTIVE,
                    ClaimPermission.METHODOLOGICAL,
                ],
                provenance="deterministic_data_profile",
            )
        )

        for column in table.columns:
            entities = [
                table.table_name,
                column.name,
            ]
            records.append(
                _profile_record(
                    support_id=_profile_support_id(
                        table.table_name,
                        column.name,
                        "missingness",
                    ),
                    fact_kind="column_missingness",
                    table_name=table.table_name,
                    column_name=column.name,
                    statement=(
                        f"`{column.name}` has {column.missing_count:,} "
                        f"missing values ({column.missing_rate:.2%} "
                        "of rows)."
                    ),
                    structured_values={
                        "missing_count": column.missing_count,
                        "missing_rate": column.missing_rate,
                        "row_count": table.row_count,
                    },
                    entities=entities,
                    provenance="deterministic_data_profile",
                )
            )

            if column.constant:
                values = {
                    "constant": True,
                    "unique_count": column.unique_count,
                    "sample_values": column.sample_values,
                    **_column_numeric_summary_values(column),
                }
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "constant",
                        ),
                        fact_kind="constant_column",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` contains no observed "
                            "variation in the profiled data."
                        ),
                        structured_values=values,
                        entities=entities,
                        claim_permissions=[
                            ClaimPermission.DESCRIPTIVE,
                            ClaimPermission.METHODOLOGICAL,
                        ],
                        provenance="deterministic_data_profile",
                    )
                )

            if column.near_constant:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "near_constant",
                        ),
                        fact_kind="near_constant_column",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` is near-constant with a "
                            "dominant observed value."
                        ),
                        structured_values={
                            "near_constant": True,
                            "dominant_value_rate": (
                                column.dominant_value_rate
                            ),
                            "unique_count": column.unique_count,
                        },
                        entities=entities,
                        claim_permissions=[
                            ClaimPermission.DESCRIPTIVE,
                            ClaimPermission.METHODOLOGICAL,
                        ],
                        provenance="deterministic_data_profile",
                    )
                )

            if column.numeric_summary:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "numeric_summary",
                        ),
                        fact_kind="numeric_summary",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` has deterministic numeric "
                            "summary statistics in the profile."
                        ),
                        structured_values=_column_numeric_summary_values(
                            column
                        ),
                        entities=entities,
                        provenance="deterministic_data_profile",
                    )
                )

            if (
                column.suspicious_zero_values
                or column.possible_sentinel_values
                or column.zero_risk.value != "none"
            ):
                zero_values = {
                    **_column_numeric_summary_values(column),
                    "zero_risk": column.zero_risk.value,
                    "zero_risk_reason": column.zero_risk_reason,
                    "suspicious_zero_values": (
                        column.suspicious_zero_values
                    ),
                    "possible_sentinel_values": (
                        column.possible_sentinel_values
                    ),
                }
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "zero_diagnostic",
                        ),
                        fact_kind="zero_diagnostic",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` has deterministic zero-value "
                            "diagnostics in the profile."
                        ),
                        structured_values=zero_values,
                        entities=entities,
                        claim_permissions=[
                            ClaimPermission.DESCRIPTIVE,
                            ClaimPermission.METHODOLOGICAL,
                        ],
                        provenance="deterministic_data_profile",
                    )
                )

            if column.datetime_parse_rate > 0:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "datetime_presence",
                        ),
                        fact_kind="datetime_presence",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` is date/time-like with "
                            f"parse rate {column.datetime_parse_rate:.2%}."
                        ),
                        structured_values={
                            "datetime_parse_rate": (
                                column.datetime_parse_rate
                            ),
                            "row_count": table.row_count,
                        },
                        entities=entities,
                        provenance="deterministic_data_profile",
                    )
                )

            if column.candidate_key:
                records.append(
                    _profile_record(
                        support_id=_profile_support_id(
                            table.table_name,
                            column.name,
                            "candidate_key",
                        ),
                        fact_kind="candidate_key",
                        table_name=table.table_name,
                        column_name=column.name,
                        statement=(
                            f"`{column.name}` is a deterministic candidate "
                            "key in the profile."
                        ),
                        structured_values={
                            "candidate_key": True,
                            "unique_count": column.unique_count,
                            "row_count": table.row_count,
                        },
                        entities=entities,
                        provenance="deterministic_data_profile",
                    )
                )

    return records


def profile_record_numbers(
    record: ProfileSupportRecord,
) -> list[float]:
    return flatten_numbers(record.structured_values)


def _profile_entity_aligned(
    sentence: str,
    record: ProfileSupportRecord,
    records: list[ProfileSupportRecord],
) -> bool:
    if record.column_name is not None:
        return _entity_in_sentence(
            record.column_name,
            sentence,
        )

    if _entity_in_sentence(record.table_name, sentence):
        return True

    table_count = len(
        {
            candidate.table_name
            for candidate in records
        }
    )

    return (
        table_count == 1
        and re.search(
            r"\b(dataset|table|rows?|records?|observations?)\b",
            sentence,
            re.IGNORECASE,
        )
        is not None
    )


def _profile_fact_kind_aligned(
    sentence: str,
    record: ProfileSupportRecord,
) -> bool:
    pattern = PROFILE_FACT_KIND_TERMS.get(
        record.fact_kind
    )

    return bool(pattern and pattern.search(sentence))


def _profile_semantic_escalation(
    sentence: str,
) -> bool:
    return bool(
        HOURLY_CADENCE_PATTERN.search(sentence)
        or LOCATION_METADATA_PATTERN.search(sentence)
        or CONSTANT_OVERSTATEMENT_PATTERN.search(sentence)
        or ZERO_OVERCONFIDENCE_PATTERN.search(sentence)
        or MISSINGNESS_HARMLESS_PATTERN.search(sentence)
        or DUPLICATE_REMOVAL_PATTERN.search(sentence)
        or PEARSON_IMPRECISE_PATTERN.search(sentence)
    )


def matching_profile_support_records(
    *,
    sentence: str,
    records: list[ProfileSupportRecord],
) -> list[ProfileSupportRecord]:
    if _profile_semantic_escalation(sentence):
        return []

    matches: list[ProfileSupportRecord] = []

    for record in records:
        if not _profile_entity_aligned(
            sentence,
            record,
            records,
        ):
            continue

        if not _profile_fact_kind_aligned(
            sentence,
            record,
        ):
            continue

        if not numbers_supported(
            sentence,
            profile_record_numbers(record),
        ):
            continue

        matches.append(record)

    return matches


def _profile_records_support_sentence(
    *,
    sentence: str,
    support_ids: list[str],
    records_by_id: dict[str, ProfileSupportRecord],
) -> bool:
    selected = [
        records_by_id[support_id]
        for support_id in support_ids
        if support_id in records_by_id
    ]
    if not selected:
        return False

    return bool(
        matching_profile_support_records(
            sentence=sentence,
            records=selected,
        )
    )


def _focused_role_value_text(pair: dict[str, Any]) -> str | None:
    headers = [
        str(header)
        for header in pair.get("headers", [])
        if str(header).strip()
    ]
    value = str(pair.get("value", "")).strip()
    if not value:
        return None

    header_text = " / ".join(headers) if headers else "value"
    return f"{header_text} = {value}"


def _focused_table_fact_summary(item: EvidenceItem) -> str:
    metrics = item.metrics
    record_relation = metrics.get("focused_record_relation")
    record_summary = (
        str(record_relation.get("relation_summary") or "").strip()
        if isinstance(record_relation, dict)
        else ""
    )
    list_relation = metrics.get("focused_list_relation")
    list_summary = (
        str(list_relation.get("relation_summary") or "").strip()
        if isinstance(list_relation, dict)
        else ""
    )
    record_group_summary = str(
        metrics.get("highlighted_record_group_summary") or ""
    ).strip()
    pair_texts = [
        text
        for pair in metrics.get("highlighted_role_value_pairs", [])
        if isinstance(pair, dict)
        and (text := _focused_role_value_text(pair))
    ]

    if record_summary:
        summary = record_summary
    elif list_summary:
        summary = list_summary
    elif record_group_summary:
        summary = record_group_summary
    elif pair_texts:
        summary = "Highlighted table values: " + "; ".join(pair_texts) + "."
    else:
        highlighted_values = [
            str(value)
            for value in metrics.get("highlighted_values", [])
            if str(value).strip()
        ]
        if highlighted_values:
            summary = (
                "Highlighted table value"
                + ("s" if len(highlighted_values) != 1 else "")
                + ": "
                + ", ".join(highlighted_values)
                + "."
            )
        else:
            proposition = str(
                metrics.get("description_proposition") or ""
            ).strip()
            summary = proposition or item.finding

    primary_subjects = [
        str(subject)
        for subject in (
            (metrics.get("concise_output_focus") or {})
            .get("primary_subject_candidates", [])
        )
        if str(subject).strip()
    ]
    if primary_subjects:
        summary += (
            " Structurally supported primary subject candidate"
            + ("s" if len(primary_subjects) != 1 else "")
            + ": "
            + ", ".join(primary_subjects)
            + "."
        )

    highlighted_set_contrasts = [
        str(contrast.get("contrast_summary") or "").strip()
        for contrast in metrics.get("highlighted_set_contrasts", [])
        if isinstance(contrast, dict)
        and str(contrast.get("contrast_summary") or "").strip()
    ]
    if highlighted_set_contrasts:
        summary += (
            " Highlighted-set contrast scoped only to selected cells: "
            + "; ".join(highlighted_set_contrasts)
        )

    record_group_summary = str(
        metrics.get("highlighted_record_group_summary") or ""
    ).strip()
    if record_group_summary and record_group_summary not in summary:
        summary += " Highlighted record-group summary: "
        summary += record_group_summary

    context_parts = [
        str(metrics.get("section_title") or "").strip(),
        str(metrics.get("page_title") or "").strip(),
    ]
    context = " / ".join(
        part
        for part in context_parts
        if part and not extract_number_tokens(part)
    )
    if context:
        summary += f" Context: {context}."

    comparisons = metrics.get("highlighted_measure_comparisons") or []
    comparison_notes = []
    for comparison in comparisons:
        if not isinstance(comparison, dict):
            continue
        value = str(comparison.get("highlighted_value") or "").strip()
        if not value:
            continue
        note_parts = [value]
        if comparison.get("is_highest_comparable_value"):
            note_parts.append("is the highest comparable highlighted measure")
        if comparison.get("is_majority_percentage"):
            note_parts.append("is above half")
        if len(note_parts) > 1:
            comparison_notes.append(" ".join(note_parts))
    if comparison_notes:
        summary += " Highlighted measure context: "
        summary += "; ".join(comparison_notes) + "."

    return summary


def _focused_table_local_contrast_summary(
    metrics: dict[str, Any],
) -> str | None:
    contrasts = metrics.get("highlighted_set_contrasts") or []
    for contrast in contrasts:
        if not isinstance(contrast, dict):
            continue
        summary = str(contrast.get("contrast_summary") or "").strip()
        if summary:
            return summary
    return None


def _structured_record_fact_summary(item: EvidenceItem) -> str:
    records = [
        record
        for record in item.metrics.get("records", [])
        if isinstance(record, dict)
    ]
    triples = [
        record
        for record in records
        if str(record.get("record_kind") or "") == "triple"
    ]
    attributes = [
        record
        for record in records
        if str(record.get("record_kind") or "") != "triple"
    ]

    if triples and not attributes:
        parts = [
            (
                f"{record.get('subject')} | {record.get('relation')} | "
                f"{record.get('object')}"
            )
            for record in triples
            if record.get("subject")
            and record.get("relation")
            and record.get("object")
        ]
        if parts:
            return "Supplied triples: " + "; ".join(parts) + "."

    parts = [
        f"{record.get('attribute_name')} = {record.get('attribute_value')}"
        for record in attributes
        if record.get("attribute_name") and record.get("attribute_value")
    ]
    if parts:
        return "Supplied attributes: " + "; ".join(parts) + "."

    return item.finding


def _semantic_event_fact_summary(item: EvidenceItem) -> str:
    if item.evidence_type in {"event_context", "event_status"}:
        values = [
            value
            for value in item.metrics.get("values", [])
            if isinstance(value, dict)
            and value.get("label") is not None
            and value.get("value") is not None
        ]
        if values:
            parts = [
                f"{value['label']} is {value['value']}"
                for value in values[:4]
            ]
            return "Event context includes " + ", ".join(parts) + "."

    if item.evidence_type in {"entity_ranking", "entity_performance"}:
        ranking = [
            record
            for record in item.metrics.get("ranking", [])
            if isinstance(record, dict)
            and record.get("entity") is not None
            and record.get("value") is not None
        ]
        if ranking:
            measure = str(
                item.metrics.get("semantic_label")
                or ranking[0].get("measure")
                or "recorded value"
            )
            measure = re.sub(
                r"^entity ranking for\s+",
                "",
                measure,
                flags=re.IGNORECASE,
            )

            def entity_name(record: dict[str, Any]) -> str:
                entity = str(record["entity"])
                group = record.get("group")
                if group and str(group) not in entity:
                    return f"{entity} ({group})"
                return entity

            leaders = [
                record
                for record in ranking
                if record.get("rank") == 1
            ]
            if len(leaders) > 1:
                names = ", ".join(entity_name(record) for record in leaders[:4])
                return (
                    f"In the ranking for {measure}, {names} tied for the lead "
                    f"with {float(leaders[0]['value']):g} each."
                )

            leader = ranking[0]
            summary = (
                f"In the ranking for {measure}, {entity_name(leader)} led "
                f"with {float(leader['value']):g}"
            )
            followers = [
                record
                for record in ranking[1:4]
                if record.get("value") is not None
            ]
            if followers:
                summary += ", followed by " + ", ".join(
                    f"{entity_name(record)} ({float(record['value']):g})"
                    for record in followers
                )
            return summary + "."

    if item.evidence_type not in {
        "event_outcome",
        "participant_comparison",
        "event_contrast",
    }:
        return item.finding

    records = [
        record
        for record in item.metrics.get("records", [])
        if isinstance(record, dict)
        and record.get("entity") is not None
        and record.get("value") is not None
    ]
    if len(records) < 2:
        return item.finding

    ordered = sorted(
        records,
        key=lambda record: float(record["value"]),
        reverse=True,
    )
    high = ordered[0]
    low = ordered[-1]
    high_entity = str(high["entity"])
    low_entity = str(low["entity"])
    high_value = float(high["value"])
    low_value = float(low["value"])
    high_measure = str(high.get("measure") or "outcome value")
    low_measure = str(low.get("measure") or high_measure)
    difference = abs(high_value - low_value)

    if high_value == low_value:
        return (
            f"{high_entity} and {low_entity} both recorded "
            f"{high_value:g} for the supplied outcome measure."
        )

    return (
        f"{high_entity} recorded {high_value:g} for {high_measure}, "
        f"while {low_entity} recorded {low_value:g} for {low_measure}; "
        f"the difference is {difference:g}."
    )


def event_sequence_evidence_is_actionable(item: EvidenceItem) -> bool:
    if item.evidence_type != "event_sequence":
        return False

    if normalise_strength_label(item.strength_label) == (
        "event_sequence_highlight"
    ):
        return True

    metrics = item.metrics
    if metrics.get("sequence_type") == "score_changing_sequence":
        return True

    return any(
        isinstance(highlight, dict)
        and str(highlight.get("event_text") or "").strip()
        and str(highlight.get("score_phrase") or "").strip()
        for highlight in metrics.get("highlights", [])
    )


def event_sequence_fact_is_actionable(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> bool:
    return any(
        event_sequence_evidence_is_actionable(item)
        for item in evidence_for_fact(fact, evidence_lookup)
    )


def _event_sequence_highlight_summary(
    highlight: dict[str, Any],
) -> str | None:
    event_text = str(highlight.get("event_text") or "").strip()
    score_phrase = str(highlight.get("score_phrase") or "").strip()
    if not event_text or not score_phrase:
        return None

    return f"{event_text}, after which {score_phrase}."


def _event_sequence_highlight_salience(
    *,
    item: EvidenceItem,
    highlight: dict[str, Any],
) -> float:
    roles = {
        str(role)
        for role in highlight.get("sequence_roles", [])
    }
    bonus = 0.0
    if roles & {"lead_change", "tie", "largest_score_change"}:
        bonus += 0.04
    if roles & {"late_score_change", "final_score_change", "late_narrowing"}:
        bonus += 0.03
    if roles & {"opening_score"}:
        bonus += 0.02
    return min(1.0, item.salience + bonus)


def deterministic_fact_candidates_from_evidence(
    *,
    item: EvidenceItem,
    start_ordinal: int,
) -> list[FactCandidate]:
    highlights = [
        highlight
        for highlight in item.metrics.get("highlights", [])
        if isinstance(highlight, dict)
    ]
    if event_sequence_evidence_is_actionable(item) and highlights:
        candidates: list[FactCandidate] = []
        for offset, highlight in enumerate(highlights):
            summary = _event_sequence_highlight_summary(highlight)
            if summary is None:
                continue
            candidates.append(
                FactCandidate(
                    candidate_id=f"CAN_{start_ordinal + offset:04d}",
                    fact_summary=summary,
                    evidence_ids=[item.evidence_id],
                    claim_permissions=item.claim_permissions,
                    allowed_interpretations=(
                        [item.practical_interpretation]
                        if item.practical_interpretation
                        else []
                    ),
                    prohibited_interpretations=item.prohibited_interpretations,
                    required_caveats=item.limitations,
                    factual_confidence=item.factual_confidence,
                    methodological_strength=item.methodological_strength,
                    user_relevance=item.user_relevance,
                    salience=_event_sequence_highlight_salience(
                        item=item,
                        highlight=highlight,
                    ),
                    recommended_use=RecommendedUse.MAIN_FINDING,
                    eligible_for_writer=True,
                )
            )
        if candidates:
            return candidates

    return [
        deterministic_fact_candidate_from_evidence(
            item=item,
            ordinal=start_ordinal,
        )
    ]


def candidate_support(
    candidate: FactCandidate,
    evidence: EvidenceLedger,
) -> tuple[str, list[float], set[ClaimPermission]]:
    lookup = evidence_lookup(evidence)
    text_parts: list[str] = []
    numbers: list[float] = []
    permissions: set[ClaimPermission] = set()

    for evidence_id in candidate.evidence_ids:
        item = lookup.get(evidence_id)

        if item is None:
            continue

        text_parts.extend(
            [
                item.finding,
                item.practical_interpretation,
                json.dumps(json_safe(item.metrics), sort_keys=True),
            ]
        )
        numbers.extend(flatten_numbers(item.metrics))
        permissions.update(item.claim_permissions)

    return " ".join(text_parts), numbers, permissions


def validate_fact_candidates(
    candidate_set: FactCandidateSet,
    evidence: EvidenceLedger,
) -> list[str]:
    errors: list[str] = []
    lookup = evidence_lookup(evidence)
    seen: set[str] = set()

    for candidate in candidate_set.candidates:
        if candidate.candidate_id in seen:
            errors.append(
                f"Duplicate candidate ID: {candidate.candidate_id}"
            )

        seen.add(candidate.candidate_id)

        if not candidate.evidence_ids:
            errors.append(
                f"{candidate.candidate_id} has no evidence IDs."
            )
            continue

        unknown = [
            evidence_id
            for evidence_id in candidate.evidence_ids
            if evidence_id not in lookup
        ]

        if unknown:
            errors.append(
                f"{candidate.candidate_id} cites unknown evidence IDs: {unknown}"
            )
            continue

        _, support_numbers, permissions = candidate_support(
            candidate,
            evidence,
        )

        if not numbers_supported(
            candidate.fact_summary,
            support_numbers,
        ):
            errors.append(
                f"{candidate.candidate_id} contains unsupported numbers."
            )

        if not set(candidate.claim_permissions).issubset(permissions):
            errors.append(
                f"{candidate.candidate_id} requests unsupported permissions."
            )

        if (
            CAUSAL_PATTERN.search(candidate.fact_summary)
            and ClaimPermission.CAUSAL not in permissions
        ):
            errors.append(f"{candidate.candidate_id} introduces unsupported causal wording.")

        if candidate.eligible_for_writer and not all(
            lookup[evidence_id].eligible_for_writer
            for evidence_id in candidate.evidence_ids
        ):
            errors.append(
                f"{candidate.candidate_id} is writer-eligible but cites excluded evidence."
            )

    return errors


def collect_entity_strings(value: Any) -> set[str]:
    entities: set[str] = set()

    if isinstance(value, str):
        entities.add(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            entities.add(str(key))
            entities.update(collect_entity_strings(item))
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            entities.update(collect_entity_strings(item))

    return entities


def deterministic_fact_candidate_from_evidence(
    *,
    item: EvidenceItem,
    ordinal: int,
) -> FactCandidate:
    return FactCandidate(
        candidate_id=f"CAN_{ordinal:04d}",
        fact_summary=deterministic_fact_summary_from_evidence(item),
        evidence_ids=[item.evidence_id],
        claim_permissions=item.claim_permissions,
        allowed_interpretations=(
            [item.practical_interpretation]
            if item.practical_interpretation
            else []
        ),
        prohibited_interpretations=item.prohibited_interpretations,
        required_caveats=item.limitations,
        factual_confidence=item.factual_confidence,
        methodological_strength=item.methodological_strength,
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
        eligible_for_writer=True,
    )


def deterministic_fact_candidate_scaffold(
    evidence: EvidenceLedger,
    maximum_facts: int | None,
    *,
    synthesis_note: str = (
        "Deterministic evidence-to-fact scaffold was created before "
        "LLM enrichment."
    ),
) -> FactCandidateSet:
    eligible_items = [
        item
        for item in evidence.items
        if item.eligible_for_writer
    ]

    ranked = sorted(
        eligible_items,
        key=lambda item: (
            item.salience
            + item.user_relevance
            + item.methodological_strength
        ),
        reverse=True,
    )

    selected_items = (
        ranked
        if maximum_facts is None
        else ranked[:maximum_facts]
    )
    candidates: list[FactCandidate] = []
    next_ordinal = 1
    for item in selected_items:
        item_candidates = deterministic_fact_candidates_from_evidence(
            item=item,
            start_ordinal=next_ordinal,
        )
        candidates.extend(item_candidates)
        next_ordinal += len(item_candidates)

    return FactCandidateSet(
        candidates=candidates,
        synthesis_notes=[synthesis_note],
    )


def fallback_fact_candidates(
    evidence: EvidenceLedger,
    maximum_facts: int | None,
) -> FactCandidateSet:
    return deterministic_fact_candidate_scaffold(
        evidence,
        maximum_facts,
        synthesis_note="Deterministic evidence-to-fact fallback was used.",
    )


def empty_fact_candidate_enrichment() -> FactCandidateSet:
    return FactCandidateSet(
        candidates=[],
        synthesis_notes=[
            "LLM fact-candidate enrichment was unavailable; "
            "the deterministic scaffold was retained."
        ],
    )


def merge_fact_candidate_scaffold(
    *,
    scaffold: FactCandidateSet,
    enrichment: FactCandidateSet,
    evidence: EvidenceLedger,
) -> FactCandidateSet:
    """Preserve deterministic coverage while accepting valid LLM enrichment."""

    valid_enrichment: list[FactCandidate] = []
    dropped_notes: list[str] = []
    seen_enrichment_ids: set[str] = set()

    for candidate in enrichment.candidates:
        if candidate.candidate_id in seen_enrichment_ids:
            dropped_notes.append(
                f"Dropped duplicate enriched candidate {candidate.candidate_id}."
            )
            continue
        seen_enrichment_ids.add(candidate.candidate_id)

        errors = validate_fact_candidates(
            FactCandidateSet(candidates=[candidate]),
            evidence,
        )
        if errors:
            dropped_notes.append(
                f"Dropped invalid enriched candidate {candidate.candidate_id}: "
                + "; ".join(errors)
            )
            continue
        valid_enrichment.append(candidate)

    lookup = evidence_lookup(evidence)
    merged: list[FactCandidate] = list(scaffold.candidates)
    scaffold_indices_by_evidence_id: dict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(merged):
        if len(candidate.evidence_ids) == 1:
            scaffold_indices_by_evidence_id[candidate.evidence_ids[0]].append(
                index
            )

    replaced_count = 0
    added_count = 0
    seen_signatures: set[tuple[tuple[str, ...], str]] = {
        (
            tuple(candidate.evidence_ids),
            candidate.fact_summary.strip().lower(),
        )
        for candidate in merged
    }

    for candidate in valid_enrichment:
        signature = (
            tuple(candidate.evidence_ids),
            candidate.fact_summary.strip().lower(),
        )
        if signature in seen_signatures:
            continue

        if (
            len(candidate.evidence_ids) == 1
            and len(
                scaffold_indices_by_evidence_id.get(
                    candidate.evidence_ids[0],
                    [],
                )
            )
            == 1
            and not event_sequence_evidence_is_actionable(
                lookup[candidate.evidence_ids[0]]
            )
        ):
            index = scaffold_indices_by_evidence_id[
                candidate.evidence_ids[0]
            ][0]
            seen_signatures.discard(
                (
                    tuple(merged[index].evidence_ids),
                    merged[index].fact_summary.strip().lower(),
                )
            )
            merged[index] = candidate
            seen_signatures.add(signature)
            replaced_count += 1
            continue

        merged.append(candidate)
        seen_signatures.add(signature)
        added_count += 1

    renumbered = [
        candidate.model_copy(
            update={"candidate_id": f"CAN_{index:04d}"}
        )
        for index, candidate in enumerate(merged, start=1)
    ]

    return FactCandidateSet(
        candidates=renumbered,
        synthesis_notes=[
            *scaffold.synthesis_notes,
            *enrichment.synthesis_notes,
            (
                "Merged fact candidates by retaining deterministic "
                f"coverage, replacing {replaced_count} scaffold "
                f"candidate(s), and appending {added_count} enriched "
                "synthesis candidate(s)."
            ),
            *dropped_notes,
        ],
    )


def fallback_verification(
    candidate_set: FactCandidateSet,
) -> VerificationResult:
    return VerificationResult(
        reviews=[
            FactReview(
                candidate_id=candidate.candidate_id,
                decision=(
                    ReviewDecision.CAUTION
                    if candidate.required_caveats
                    else ReviewDecision.APPROVE
                ),
                rationale=(
                    "The candidate is directly grounded in validated evidence."
                ),
                required_caveats=candidate.required_caveats,
                prohibited_interpretations=(
                    candidate.prohibited_interpretations
                ),
            )
            for candidate in candidate_set.candidates
        ],
        overall_notes=[
            "Deterministic verification fallback was used."
        ],
    )


MISSING_EVIDENCE_REJECTION_PATTERN = re.compile(
    r"\b(?:cited\s+)?evidence\b.*\b(?:not present|not found|unknown|missing)\b|"
    r"\b(?:not present|not found|unknown|missing)\b.*\bevidence\b",
    re.IGNORECASE,
)


def repair_spurious_missing_evidence_rejections(
    *,
    candidate_set: FactCandidateSet,
    verification: VerificationResult,
    evidence: EvidenceLedger,
) -> VerificationResult:
    """Keep local evidence-ID validation authoritative over verifier slips."""

    candidates = {
        candidate.candidate_id: candidate
        for candidate in candidate_set.candidates
    }
    repaired_reviews: list[FactReview] = []
    repair_notes: list[str] = []

    for review in verification.reviews:
        candidate = candidates.get(review.candidate_id)
        if (
            candidate is not None
            and review.decision == ReviewDecision.REJECT
            and MISSING_EVIDENCE_REJECTION_PATTERN.search(
                review.rationale
            )
            and not validate_fact_candidates(
                FactCandidateSet(candidates=[candidate]),
                evidence,
            )
        ):
            repaired_reviews.append(
                FactReview(
                    candidate_id=review.candidate_id,
                    decision=(
                        ReviewDecision.CAUTION
                        if candidate.required_caveats
                        else ReviewDecision.APPROVE
                    ),
                    rationale=(
                        "Local deterministic validation confirmed the cited "
                        "evidence IDs exist and support this candidate; "
                        "overrode a spurious missing-evidence rejection."
                    ),
                    required_caveats=[
                        *candidate.required_caveats,
                        *review.required_caveats,
                    ],
                    prohibited_interpretations=[
                        *candidate.prohibited_interpretations,
                        *review.prohibited_interpretations,
                    ],
                )
            )
            repair_notes.append(
                f"Repaired spurious missing-evidence rejection for "
                f"{review.candidate_id}."
            )
            continue

        repaired_reviews.append(review)

    if not repair_notes:
        return verification

    return verification.model_copy(
        update={
            "reviews": repaired_reviews,
            "overall_notes": [
                *verification.overall_notes,
                *repair_notes,
            ],
        }
    )


def finalise_fact_ledger(
    candidate_set: FactCandidateSet,
    verification: VerificationResult,
    evidence: EvidenceLedger,
) -> FactLedger:
    errors = validate_fact_candidates(candidate_set, evidence)
    reviews = {
        review.candidate_id: review
        for review in verification.reviews
    }
    lookup = evidence_lookup(evidence)

    facts: list[VerifiedFact] = []
    rejected: list[RejectedFact] = []

    for candidate in candidate_set.candidates:
        candidate_errors = [
            error
            for error in errors
            if candidate.candidate_id in error
        ]

        review = reviews.get(candidate.candidate_id)

        if candidate_errors:
            rejected.append(
                RejectedFact(
                    source_candidate_id=candidate.candidate_id,
                    fact_summary=candidate.fact_summary,
                    reason=" ".join(candidate_errors),
                )
            )
            continue

        if review is None or review.decision == ReviewDecision.REJECT:
            rejected.append(
                RejectedFact(
                    source_candidate_id=candidate.candidate_id,
                    fact_summary=candidate.fact_summary,
                    reason=(
                        review.rationale
                        if review
                        else "The verifier did not review this candidate."
                    ),
                )
            )
            continue

        structured_values: dict[str, Any] = {}
        entities: set[str] = set()
        source_capabilities = []

        for evidence_id in candidate.evidence_ids:
            item = lookup[evidence_id]
            structured_values[evidence_id] = item.metrics
            entities.update(item.source_tables)
            entities.update(item.source_columns)
            entities.update(item.entity_scope)
            source_capabilities.append(item.capability)

            entities.update(collect_entity_strings(item.metrics))

        facts.append(
            VerifiedFact(
                fact_id=f"FACT_{len(facts) + 1:04d}",
                source_candidate_id=candidate.candidate_id,
                fact_summary=candidate.fact_summary,
                evidence_ids=candidate.evidence_ids,
                source_capabilities=list(
                    dict.fromkeys(source_capabilities)
                ),
                structured_values=structured_values,
                entities=sorted(entities),
                claim_permissions=candidate.claim_permissions,
                allowed_interpretations=candidate.allowed_interpretations,
                prohibited_interpretations=list(
                    dict.fromkeys(
                        candidate.prohibited_interpretations
                        + review.prohibited_interpretations
                    )
                ),
                required_caveats=list(
                    dict.fromkeys(
                        candidate.required_caveats
                        + review.required_caveats
                    )
                ),
                factual_confidence=candidate.factual_confidence,
                methodological_strength=candidate.methodological_strength,
                user_relevance=candidate.user_relevance,
                salience=candidate.salience,
                recommended_use=candidate.recommended_use,
            )
        )

    return FactLedger(
        writer_ready_facts=facts,
        rejected_facts=rejected,
        verifier_notes=verification.overall_notes,
    )



def normalise_strength_label(
    label: str,
) -> str:
    mapping = {
        "very_strong": "very_strong_association",
        "strong": "strong_association",
        "moderate": "moderate_association",
        "weak": "weak_but_reportable_association",
        "weak_but_reportable": (
            "weak_but_reportable_association"
        ),
        "large": "large_group_difference",
        "small": "small_group_difference",
        "negligible": "negligible_group_difference",
    }

    return mapping.get(label, label)


ASSOCIATION_STRENGTH_TERMS = {
    "very strong": "very_strong_association",
    "strong": "strong_association",
    "moderate": "moderate_association",
    "weak": "weak_but_reportable_association",
    "negligible": "negligible_association",
}

GROUP_STRENGTH_TERMS = {
    "large": "large_group_difference",
    "moderate": "moderate_group_difference",
    "small": "small_group_difference",
    "negligible": "negligible_group_difference",
}


def qualitative_strength_conflicts(
    sentence: str,
    evidence_items: list[EvidenceItem],
) -> list[str]:
    normalised_labels = {
        normalise_strength_label(item.strength_label)
        for item in evidence_items
    }
    association_labels = normalised_labels & set(
        ASSOCIATION_STRENGTH_TERMS.values()
    )
    group_labels = normalised_labels & set(
        GROUP_STRENGTH_TERMS.values()
    )
    conflicts: list[str] = []

    for match in ASSOCIATION_STRENGTH_PATTERN.finditer(sentence):
        visible_label = match.group("label").lower()
        expected_label = ASSOCIATION_STRENGTH_TERMS[visible_label]
        if association_labels and expected_label not in association_labels:
            conflicts.append(
                f"{visible_label} association conflicts with "
                f"{sorted(association_labels)}"
            )

    for match in GROUP_STRENGTH_PATTERN.finditer(sentence):
        visible_label = match.group("label").lower()
        expected_label = GROUP_STRENGTH_TERMS[visible_label]
        if group_labels and expected_label not in group_labels:
            conflicts.append(
                f"{visible_label} group difference conflicts with "
                f"{sorted(group_labels)}"
            )

    return list(dict.fromkeys(conflicts))

LOW_PRIORITY_STRENGTH_LABELS = {
    "negligible",
    "negligible_association",
    "negligible_group_difference",
    "weak_but_reportable_association",
    "small_group_difference",
}

RECOVERABLE_CORRELATION_LABELS = {
    "very_strong_association",
    "strong_association",
    "moderate_association",
}

RECOVERABLE_GROUP_LABELS = {
    "large_group_difference",
    "moderate_group_difference",
}

RECOVERABLE_MODELLING_LABELS = {
    "validated_internal_prediction",
    "model_not_better_than_baseline",
    "validated_forecast",
    "forecast_not_better_than_baseline",
    "predictive_insufficiency",
    "forecast_insufficiency",
}

RECOVERABLE_DATA_QUALITY_LABELS = {
    "constant_column",
    "duplicate_rows",
    "possible_sentinel_zero",
    "possible_data_quality_issue",
    "material_missingness",
    "low_missingness",
}


def evidence_subtype(
    item: EvidenceItem,
) -> str:
    metrics = item.metrics
    label = normalise_strength_label(
        item.strength_label
    )

    if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION:
        return "focused_table_region"

    if (
        item.capability
        == EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
    ):
        return "structured_record_verbalisation"

    if item.evidence_type == "event_context":
        return "event_context"

    if item.evidence_type == "event_status":
        return "event_status"

    if item.evidence_type == "participant_record_context":
        return "participant_record_context"

    if item.evidence_type == "score_progression":
        return "score_progression"

    if item.evidence_type == "event_sequence":
        return "event_sequence"

    if item.capability == EvidenceCapability.EVENT_OUTCOME:
        return "event_outcome"

    if item.capability in {
        EvidenceCapability.ENTITY_PERFORMANCE,
        EvidenceCapability.RANKING,
    }:
        return "entity_performance"

    if (
        item.capability == EvidenceCapability.GROUP_COMPARISON
        and item.evidence_type == "participant_comparison"
    ):
        return "group_comparison"

    if item.route == AnalysisRoute.DESCRIPTIVE:
        if (
            "row_count" in metrics
            and "column_count" in metrics
        ):
            return "dataset_overview"

        if (
            metrics.get("constant") is True
            or "missing_count" in metrics
            or "missing_rate" in metrics
            or "duplicate_row_count" in metrics
            or label
            in {
                "constant_column",
                "duplicate_rows",
                "possible_sentinel_zero",
                "possible_data_quality_issue",
                "material_missingness",
                "low_missingness",
            }
        ):
            return "data_quality"

        return "descriptive_detail"

    if (
        item.route
        == AnalysisRoute.ASSOCIATION_COMPARISON
    ):
        if (
            "pearson_r" in metrics
            or "spearman_r" in metrics
            or "correlation" in metrics
        ):
            return "correlation"

        if (
            "highest_group" in metrics
            or "lowest_group" in metrics
            or "group_counts" in metrics
            or "standardised_difference"
            in metrics
            or "standardized_difference"
            in metrics
        ):
            return "group_comparison"

        return "association_other"

    if item.route == AnalysisRoute.PREDICTIVE:
        return "predictive_validation"

    if item.route == AnalysisRoute.FORECASTING:
        return "forecast_validation"

    if (
        item.route
        == AnalysisRoute.CAUSAL_FEASIBILITY
    ):
        return "causal_feasibility"

    return "other"

def fact_priority_score(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> float:
    evidence_items = evidence_for_fact(
        fact,
        evidence_lookup,
    )

    use_bonus = {
        RecommendedUse.HEADLINE: 0.25,
        RecommendedUse.MAIN_FINDING: 0.15,
        RecommendedUse.SUPPORTING_DETAIL: 0.0,
        RecommendedUse.LIMITATION: 0.10,
        RecommendedUse.OMIT_UNLESS_REQUESTED: -0.30,
    }.get(
        fact.recommended_use,
        0.0,
    )

    bonus_by_label = {
        "dataset_overview": 0.18,
        "constant_column": 0.15,
        "possible_sentinel_zero": 0.15,
        "possible_data_quality_issue": 0.12,
        "material_missingness": 0.12,
        "low_missingness": 0.03,
        "very_strong_association": 0.22,
        "strong_association": 0.17,
        "moderate_association": 0.10,
        "weak_but_reportable_association": -0.08,
        "large_group_difference": 0.18,
        "moderate_group_difference": 0.10,
        "small_group_difference": -0.15,
        "negligible_group_difference": -0.35,
        "validated_internal_prediction": 0.15,
        "model_not_better_than_baseline": 0.12,
        "validated_forecast": 0.15,
        "forecast_not_better_than_baseline": 0.12,
    }

    strength_bonuses = [
        bonus_by_label.get(
            normalise_strength_label(
                item.strength_label
            ),
            0.0,
        )
        for item in evidence_items
    ]

    strength_bonus = (
        max(strength_bonuses)
        if strength_bonuses
        else 0.0
    )

    return (
        0.30 * fact.salience
        + 0.25 * fact.user_relevance
        + 0.20 * fact.methodological_strength
        + 0.15 * fact.factual_confidence
        + use_bonus
        + strength_bonus
    )

def evidence_priority_score_for_fact(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> float:
    return fact_priority_score(fact, evidence_lookup)


def classify_fact_component(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> ReportComponent:
    items = evidence_for_fact(fact, evidence_lookup)
    subtypes = {evidence_subtype(item) for item in items}
    permissions = set(fact.claim_permissions)

    if "dataset_overview" in subtypes:
        return ReportComponent.DATASET_OVERVIEW

    if "data_quality" in subtypes:
        return ReportComponent.DATA_QUALITY

    if subtypes & {
        "event_outcome",
        "entity_performance",
        "event_sequence",
        "participant_record_context",
        "score_progression",
    }:
        return ReportComponent.DATASET_OVERVIEW

    if (
        "predictive_validation" in subtypes
        or "forecast_validation" in subtypes
    ):
        return ReportComponent.MODELLING_VALIDATION

    if (
        "correlation" in subtypes
        or "group_comparison" in subtypes
        or "association_other" in subtypes
    ):
        return ReportComponent.STRONGEST_RELATIONSHIPS

    if (
        ClaimPermission.INSUFFICIENCY in permissions
        or fact.recommended_use == RecommendedUse.LIMITATION
        or fact.required_caveats
    ):
        return ReportComponent.LIMITATIONS_NEXT_STEPS

    return ReportComponent.DATASET_OVERVIEW


def eligible_fact_as_priority(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> bool:
    if fact.recommended_use not in {
        RecommendedUse.HEADLINE,
        RecommendedUse.MAIN_FINDING,
        RecommendedUse.LIMITATION,
    }:
        return False

    strength_labels = {
        normalise_strength_label(
            item.strength_label
        )
        for item
        in evidence_for_fact(
            fact,
            evidence_lookup,
        )
    }

    if (
        strength_labels
        & LOW_PRIORITY_STRENGTH_LABELS
    ):
        return False

    return (
        fact.factual_confidence >= 0.90
        and fact.methodological_strength
        >= 0.70
        and fact.user_relevance >= 0.60
    )

def evidence_priority_score(
    item: EvidenceItem,
) -> float:
    temporary_fact = VerifiedFact(
        fact_id="FACT_SCORE_ONLY",
        source_candidate_id=(
            f"SCORE_{item.evidence_id}"
        ),
        verification_method=(
            VerificationMethod
            .DETERMINISTIC_EVIDENCE_RECOVERY
        ),
        fact_summary=item.finding,
        evidence_ids=[item.evidence_id],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=[
            *item.source_tables,
            *item.source_columns,
        ],
        claim_permissions=(
            item.claim_permissions
        ),
        allowed_interpretations=[
            item.practical_interpretation
        ],
        prohibited_interpretations=(
            item.prohibited_interpretations
        ),
        required_caveats=item.limitations,
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )

    return fact_priority_score(
        temporary_fact,
        {
            item.evidence_id: item,
        },
    )


def eligible_for_deterministic_fact_recovery(
    item: EvidenceItem,
    *,
    allow_query_evidence: bool = False,
) -> bool:
    if item.query_id is not None and not allow_query_evidence:
        return False

    if not item.eligible_for_writer:
        return False

    if item.factual_confidence < 0.90:
        return False

    if item.methodological_strength < 0.65:
        return False

    subtype = evidence_subtype(item)
    label = normalise_strength_label(
        item.strength_label
    )

    if subtype == "dataset_overview":
        return True

    if subtype == "focused_table_region":
        return True

    if subtype in {
        "event_context",
        "event_status",
        "participant_record_context",
        "score_progression",
        "event_outcome",
        "entity_performance",
        "event_sequence",
    }:
        return True

    if subtype == "data_quality":
        return (
            label
            in RECOVERABLE_DATA_QUALITY_LABELS
        )

    if subtype == "correlation":
        return (
            label
            in RECOVERABLE_CORRELATION_LABELS
        )

    if subtype == "group_comparison":
        if item.capability == EvidenceCapability.GROUP_COMPARISON:
            return True
        return (
            label in RECOVERABLE_GROUP_LABELS
        )

    if subtype in {
        "predictive_validation",
        "forecast_validation",
    }:
        return (
            label
            in RECOVERABLE_MODELLING_LABELS
            or ClaimPermission.INSUFFICIENCY
            in item.claim_permissions
        )

    if subtype == "causal_feasibility":
        return (
            ClaimPermission.INSUFFICIENCY
            in item.claim_permissions
        )

    return False


def deterministic_fact_summary_from_evidence(
    item: EvidenceItem,
) -> str:
    if item.capability == EvidenceCapability.FOCUSED_TABLE_REGION:
        return _focused_table_fact_summary(item)

    if (
        item.capability
        == EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
    ):
        return _structured_record_fact_summary(item)

    if (
        item.capability
        in {
            EvidenceCapability.EVENT_OUTCOME,
            EvidenceCapability.ENTITY_PERFORMANCE,
            EvidenceCapability.RANKING,
            EvidenceCapability.GROUP_COMPARISON,
        }
        or evidence_subtype(item)
        in {
            "event_context",
            "event_status",
            "participant_record_context",
            "score_progression",
            "event_outcome",
            "entity_performance",
            "event_sequence",
            "group_comparison",
        }
    ):
        return _semantic_event_fact_summary(item)

    return item.finding


def deterministic_fact_from_evidence(
    *,
    item: EvidenceItem,
    ordinal: int,
) -> VerifiedFact:
    entities = set(
        [
            *item.source_tables,
            *item.source_columns,
        ]
    )

    entities.update(
        collect_entity_strings(item.metrics)
    )
    entities.update(item.entity_scope)

    return VerifiedFact(
        fact_id=f"FACT_REC_{ordinal:04d}",
        source_candidate_id=(
            f"RECOVERY_{item.evidence_id}"
        ),
        verification_method=(
            VerificationMethod
            .DETERMINISTIC_EVIDENCE_RECOVERY
        ),
        fact_summary=deterministic_fact_summary_from_evidence(item),
        evidence_ids=[item.evidence_id],
        source_capabilities=[item.capability],
        structured_values={
            item.evidence_id: item.metrics
        },
        entities=sorted(entities),
        claim_permissions=(
            item.claim_permissions
        ),
        allowed_interpretations=(
            [item.practical_interpretation]
            if item.practical_interpretation
            else []
        ),
        prohibited_interpretations=(
            item.prohibited_interpretations
        ),
        required_caveats=item.limitations,
        factual_confidence=(
            item.factual_confidence
        ),
        methodological_strength=(
            item.methodological_strength
        ),
        user_relevance=item.user_relevance,
        salience=item.salience,
        recommended_use=item.recommended_use,
    )


def fact_subtype_counts(
    *,
    facts: list[VerifiedFact],
    evidence_lookup: dict[str, EvidenceItem],
) -> Counter[str]:
    counts: Counter[str] = Counter()

    for fact in facts:
        represented_subtypes = {
            evidence_subtype(
                evidence_lookup[evidence_id]
            )
            for evidence_id in fact.evidence_ids
            if evidence_id in evidence_lookup
        }

        for subtype in represented_subtypes:
            counts[subtype] += 1

    return counts


def augment_fact_ledger_for_report_coverage(
    *,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    required_content_slots: list[str] | None = None,
    settings: Settings,
) -> FactLedger:
    """
    Augment a thin fact ledger using exact, trusted deterministic
    evidence statements.

    This does not create new calculations or LLM interpretations.
    """

    lookup = build_evidence_lookup(evidence)

    represented_evidence_ids = {
        evidence_id
        for fact
        in fact_ledger.writer_ready_facts
        for evidence_id in fact.evidence_ids
    }

    existing_counts = fact_subtype_counts(
        facts=fact_ledger.writer_ready_facts,
        evidence_lookup=lookup,
    )

    candidates = sorted(
        [
            item
            for item in evidence.items
            if (
                item.evidence_id
                not in represented_evidence_ids
                and eligible_for_deterministic_fact_recovery(item)
            )
        ],
        key=evidence_priority_score,
        reverse=True,
    )

    subtype_limits = {
        "dataset_overview": (
            settings
            .maximum_recovered_overview_facts
        ),
        "data_quality": (
            settings
            .maximum_recovered_data_quality_facts
        ),
        "correlation": (
            settings
            .maximum_recovered_correlation_facts
        ),
        "group_comparison": (
            settings
            .maximum_recovered_group_comparison_facts
        ),
        "predictive_validation": (
            settings
            .maximum_recovered_modelling_facts
        ),
        "forecast_validation": (
            settings
            .maximum_recovered_modelling_facts
        ),
        "causal_feasibility": 1,
        "event_context": 2,
        "event_status": 2,
        "participant_record_context": 2,
        "score_progression": 2,
        "event_outcome": 2,
        "entity_performance": 4,
        "event_sequence": 2,
    }

    recovered: list[VerifiedFact] = []
    recovered_counts: Counter[str] = Counter()
    recovery_notes: list[str] = []
    recovered_evidence_ids: set[str] = set()

    existing_fact_ids = {
        fact.fact_id
        for fact
        in fact_ledger.writer_ready_facts
    }

    next_ordinal = 1

    def next_fact_id_ordinal() -> int:
        nonlocal next_ordinal

        while (
            f"FACT_REC_{next_ordinal:04d}"
            in existing_fact_ids
        ):
            next_ordinal += 1

        value = next_ordinal
        next_ordinal += 1

        return value

    def recover(item: EvidenceItem) -> bool:
        subtype = evidence_subtype(item)

        if (
            item.evidence_id
            in recovered_evidence_ids
        ):
            return False

        maximum = subtype_limits.get(
            subtype,
            0,
        )

        if (
            recovered_counts[subtype]
            >= maximum
        ):
            return False

        fact = deterministic_fact_from_evidence(
            item=item,
            ordinal=next_fact_id_ordinal(),
        )

        recovered.append(fact)
        recovered_counts[subtype] += 1
        recovered_evidence_ids.add(
            item.evidence_id
        )

        recovery_notes.append(
            "Recovered writer-ready fact "
            f"`{fact.fact_id}` from deterministic "
            f"evidence `{item.evidence_id}` for "
            f"subtype `{subtype}`."
        )

        return True

    def recover_best(
        subtype: str,
        *,
        allow_query_evidence: bool = False,
        allow_represented_evidence: bool = False,
    ) -> bool:
        source_items = candidates
        if allow_query_evidence or allow_represented_evidence:
            source_items = sorted(
                [
                    item
                    for item in evidence.items
                    if (
                        (
                            allow_represented_evidence
                            or item.evidence_id
                            not in represented_evidence_ids
                        )
                        and eligible_for_deterministic_fact_recovery(
                            item,
                            allow_query_evidence=allow_query_evidence,
                        )
                    )
                ],
                key=evidence_priority_score,
                reverse=True,
            )

        for item in source_items:
            if (
                evidence_subtype(item)
                == subtype
                and item.evidence_id
                not in recovered_evidence_ids
            ):
                if recover(item):
                    return True

        return False

    slot_subtypes = {
        "event_context": "event_context",
        "event_status": "event_status",
        "participant_record_context": "participant_record_context",
        "score_progression": "score_progression",
        "event_sequence": "event_sequence",
        "event_result": "event_outcome",
        "leading_performance": "entity_performance",
        "main_contrast": "group_comparison",
        "secondary_performance": "entity_performance",
    }

    def existing_required_slot_fact_count(
        subtype: str,
    ) -> int:
        return sum(
            1
            for fact in fact_ledger.writer_ready_facts
            if (
                fact.recommended_use
                != RecommendedUse.OMIT_UNLESS_REQUESTED
                and any(
                    evidence_id in lookup
                    and evidence_subtype(lookup[evidence_id])
                    == subtype
                    for evidence_id in fact.evidence_ids
                )
            )
        )

    for slot in required_content_slots or []:
        subtype = slot_subtypes.get(slot)
        if subtype is None:
            continue
        if (
            existing_required_slot_fact_count(subtype)
            + recovered_counts[subtype]
            == 0
        ):
            recover_best(
                subtype,
                allow_query_evidence=True,
                allow_represented_evidence=True,
            )

    if (
        ReportComponent.DATASET_OVERVIEW
        in required_components
    ):
        while (
            existing_counts["dataset_overview"]
            + recovered_counts[
                "dataset_overview"
            ]
            < settings.minimum_overview_fact_count
        ):
            if not recover_best(
                "dataset_overview"
            ):
                break

    if (
        ReportComponent.DATA_QUALITY
        in required_components
    ):
        while (
            existing_counts["data_quality"]
            + recovered_counts["data_quality"]
            < settings.minimum_data_quality_fact_count
        ):
            if not recover_best("data_quality"):
                break

    if (
        ReportComponent.STRONGEST_RELATIONSHIPS
        in required_components
    ):
        # Prefer subtype diversity when both forms are available.
        if (
            existing_counts["correlation"] == 0
            and any(
                evidence_subtype(item)
                == "correlation"
                for item in candidates
            )
        ):
            recover_best("correlation")

        if (
            existing_counts["group_comparison"]
            == 0
            and any(
                evidence_subtype(item)
                == "group_comparison"
                for item in candidates
            )
        ):
            recover_best("group_comparison")

        def relationship_count() -> int:
            return sum(
                existing_counts[subtype]
                + recovered_counts[subtype]
                for subtype in {
                    "correlation",
                    "group_comparison",
                    "association_other",
                }
            )

        while (
            relationship_count()
            < settings.minimum_relationship_fact_count
        ):
            recovered_one = (
                recover_best("correlation")
                or recover_best(
                    "group_comparison"
                )
            )

            if not recovered_one:
                break

    # Fill a thin ledger only with remaining eligible evidence.
    for item in candidates:
        if (
            len(
                fact_ledger.writer_ready_facts
            )
            + len(recovered)
            >= settings.minimum_writer_ready_fact_count
        ):
            break

        recover(item)

    if not recovered:
        return fact_ledger

    return fact_ledger.model_copy(
        update={
            "writer_ready_facts": [
                *fact_ledger.writer_ready_facts,
                *recovered,
            ],
            "deterministically_recovered_fact_ids": [
                *fact_ledger
                .deterministically_recovered_fact_ids,
                *[
                    fact.fact_id
                    for fact in recovered
                ],
            ],
            "coverage_recovery_notes": [
                *fact_ledger.coverage_recovery_notes,
                *recovery_notes,
            ],
        }
    )

def select_balanced_priority_facts(
    *,
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    settings: Settings,
) -> list[VerifiedFact]:
    """
    Select facts by coverage and analytical strength.

    There is deliberately no unrestricted final fill stage. Weak or
    small facts remain available in supporting_facts but are not
    promoted simply because unused capacity remains.
    """

    lookup = build_evidence_lookup(evidence)

    ranked = sorted(
        facts,
        key=lambda fact: fact_priority_score(
            fact,
            lookup,
        ),
        reverse=True,
    )

    selected: list[VerifiedFact] = []
    selected_ids: set[str] = set()
    subtype_counts: Counter[str] = Counter()

    def primary_subtype(
        fact: VerifiedFact,
    ) -> str:
        subtypes = [
            evidence_subtype(item)
            for item
            in evidence_for_fact(
                fact,
                lookup,
            )
        ]

        return (
            subtypes[0]
            if subtypes
            else "other"
        )

    def priority_eligible(
        fact: VerifiedFact,
    ) -> bool:
        return (
            eligible_fact_as_priority(
                fact,
                lookup,
            )
            and fact_priority_score(
                fact,
                lookup,
            )
            >= settings.minimum_main_finding_score
        )

    def add_fact(
        fact: VerifiedFact,
        *,
        require_priority_eligibility: bool,
    ) -> bool:
        if fact.fact_id in selected_ids:
            return False

        subtype = primary_subtype(fact)

        if (
            require_priority_eligibility
            and not priority_eligible(fact)
        ):
            return False

        selected.append(fact)
        selected_ids.add(fact.fact_id)
        subtype_counts[subtype] += 1

        return True

    def add_best_for_subtype(
        subtype: str,
        *,
        require_priority_eligibility: bool,
    ) -> bool:
        for fact in ranked:
            if primary_subtype(fact) != subtype:
                continue

            if add_fact(
                fact,
                require_priority_eligibility=(
                    require_priority_eligibility
                ),
            ):
                return True

        return False

    add_best_for_subtype(
        "event_outcome",
        require_priority_eligibility=False,
    )
    add_best_for_subtype(
        "entity_performance",
        require_priority_eligibility=False,
    )

    if (
        ReportComponent.DATASET_OVERVIEW
        in required_components
    ):
        add_best_for_subtype(
            "dataset_overview",
            require_priority_eligibility=False,
        )

    if (
        ReportComponent.DATA_QUALITY
        in required_components
    ):
        add_best_for_subtype(
            "data_quality",
            require_priority_eligibility=False,
        )

    if (
        ReportComponent.STRONGEST_RELATIONSHIPS
        in required_components
    ):
        # Prefer one strong correlation and one strong group comparison.
        add_best_for_subtype(
            "correlation",
            require_priority_eligibility=True,
        )

        event_facts_present = any(
            EvidenceCapability.EVENT_OUTCOME
            in fact.source_capabilities
            for fact in facts
        )

        add_best_for_subtype(
            "group_comparison",
            require_priority_eligibility=(
                not event_facts_present
            ),
        )

        def selected_relationship_count() -> int:
            return sum(
                subtype_counts[subtype]
                for subtype in {
                    "correlation",
                    "group_comparison",
                    "association_other",
                }
            )

        for fact in ranked:
            if (
                selected_relationship_count()
                >= settings.minimum_relationship_fact_count
            ):
                break

            if primary_subtype(fact) not in {
                "correlation",
                "group_comparison",
                "association_other",
            }:
                continue

            add_fact(
                fact,
                require_priority_eligibility=True,
            )

    if (
        ReportComponent.MODELLING_VALIDATION
        in required_components
    ):
        add_best_for_subtype(
            "predictive_validation",
            require_priority_eligibility=False,
        )

        if not any(
            primary_subtype(fact)
            in {
                "predictive_validation",
                "forecast_validation",
            }
            for fact in selected
        ):
            add_best_for_subtype(
                "forecast_validation",
                require_priority_eligibility=False,
            )

    if (
        ReportComponent.LIMITATIONS_NEXT_STEPS
        in required_components
    ):
        for fact in ranked:
            if (
                fact.recommended_use
                == RecommendedUse.LIMITATION
                or ClaimPermission.INSUFFICIENCY
                in fact.claim_permissions
            ):
                if add_fact(
                    fact,
                    require_priority_eligibility=False,
                ):
                    break

    # Add only high-quality eligible facts. Do not fill with weak facts.
    for fact in ranked:
        if (
            settings.writer_priority_fact_limit is not None
            and len(selected)
            >= settings.writer_priority_fact_limit
        ):
            break
        add_fact(
            fact,
            require_priority_eligibility=True,
        )

    return selected

def select_priority_facts(
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
    settings: Settings,
) -> list[VerifiedFact]:
    return select_balanced_priority_facts(
        facts=facts,
        evidence=evidence,
        required_components=required_components,
        settings=settings,
    )


def reader_facing_caveat(text: str) -> str | None:
    lowered = text.strip().lower()

    if not text.strip():
        return None

    if lowered.startswith(("do not", "never", "prohibited", "internal")):
        if "caus" in lowered:
            return (
                "These are unadjusted descriptive comparisons and should not "
                "be interpreted as causal effects."
            )
        if "confounding" in lowered or "adjusted" in lowered:
            return "The comparisons are unadjusted and do not control for confounding."
        if "predict" in lowered:
            return (
                "Predictive wording should be limited to validated modelling "
                "results and not inferred from descriptive evidence."
            )
        return None

    return text.strip()


def build_reader_facing_limitations(
    facts: list[VerifiedFact],
) -> list[str]:
    limitations: list[str] = []
    has_group_comparison = any(
        ClaimPermission.COMPARATIVE in fact.claim_permissions
        for fact in facts
    )
    has_association = any(
        ClaimPermission.ASSOCIATIONAL in fact.claim_permissions
        for fact in facts
    )
    has_predictive = any(
        ClaimPermission.PREDICTIVE in fact.claim_permissions
        for fact in facts
    )
    has_forecast = any(
        ClaimPermission.FORECAST in fact.claim_permissions
        for fact in facts
    )

    if has_group_comparison or has_association:
        limitations.append(
            "Observed associations and group comparisons are descriptive. "
            "They are not evidence of causal effects."
        )

    if has_group_comparison:
        limitations.append(
            "Group comparisons are unadjusted unless the evidence explicitly "
            "states otherwise. Unequal group sizes may lead to different "
            "levels of precision and stability."
        )

    if has_predictive:
        limitations.append(
            "Predictive results describe internal validation under the tested "
            "setup and do not establish deployment readiness."
        )

    if has_forecast:
        limitations.append(
            "Forecast results are internal backtests and do not guarantee "
            "future performance."
        )

    return list(dict.fromkeys(limitations))


def select_priority_verified_insights(
    *,
    insight_ledger: InsightLedger,
    maximum: int | None,
) -> tuple[list[VerifiedInsight], list[VerifiedInsight]]:
    eligible = [
        insight
        for insight in insight_ledger.verified_insights
        if insight.verification_status
        in {
            InsightVerificationStatus.VERIFIED,
            InsightVerificationStatus.VERIFIED_WITH_CAVEAT,
        }
        and insight.interpretation_level
        == InterpretationLevel.BOUNDED_INSIGHT
    ]
    ranked = sorted(
        enumerate(eligible),
        key=lambda item: (
            -item[1].salience,
            -item[1].confidence,
            item[0],
        ),
    )

    priority: list[VerifiedInsight] = []
    selected_ids: set[str] = set()
    selected_types: set[InsightType] = set()

    priority_limit = maximum or len(ranked)

    for _, insight in ranked:
        if len(priority) >= priority_limit:
            break
        if insight.insight_type in selected_types:
            continue
        priority.append(insight)
        selected_ids.add(insight.insight_id)
        selected_types.add(insight.insight_type)

    for _, insight in ranked:
        if len(priority) >= priority_limit:
            break
        if insight.insight_id in selected_ids:
            continue
        priority.append(insight)
        selected_ids.add(insight.insight_id)

    supporting = [
        insight
        for _, insight in ranked
        if insight.insight_id not in selected_ids
    ]

    return priority, supporting


def fact_is_relevant_to_genre(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
    genre: ReportGenre,
) -> bool:
    if genre not in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }:
        return True

    items = [
        evidence_lookup[evidence_id]
        for evidence_id in fact.evidence_ids
        if evidence_id in evidence_lookup
    ]
    if not items:
        return False

    event_evidence_types = {
        "event_outcome",
        "event_context",
        "event_status",
        "participant_record_context",
        "score_progression",
        "entity_ranking",
        "entity_performance",
        "event_sequence",
        "participant_comparison",
        "event_contrast",
    }
    return any(
        item.eligible_for_writer
        and item.evidence_type in event_evidence_types
        for item in items
    )


def evidence_analytical_function(
    item: EvidenceItem,
) -> AnalyticalFunction | None:
    if item.analytical_function is not None:
        return item.analytical_function

    value = item.metrics.get("analytical_function")
    if not isinstance(value, str):
        return None

    try:
        return AnalyticalFunction(value)
    except ValueError:
        return None


def event_evidence_is_segment_ranking(
    item: EvidenceItem,
) -> bool:
    if item.evidence_type not in {
        "entity_ranking",
        "entity_performance",
    }:
        return False

    text_parts = [
        item.finding,
        item.strength_label,
        item.metrics.get("semantic_label"),
        item.metrics.get("question"),
        item.metrics.get("measure"),
        *item.source_paths,
    ]
    text = " ".join(str(part) for part in text_parts if part)
    return bool(EVENT_SEGMENT_RANKING_PATTERN.search(text))


def event_fact_has_low_priority_entity_metric(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> bool:
    for item in evidence_for_fact(fact, evidence_lookup):
        if item.evidence_type not in {
            "entity_ranking",
            "entity_performance",
        }:
            continue
        text_parts = [
            item.finding,
            item.strength_label,
            item.metrics.get("semantic_label"),
            item.metrics.get("question"),
            item.metrics.get("measure"),
            fact.fact_summary,
            *item.source_paths,
        ]
        text = " ".join(str(part) for part in text_parts if part)
        if (
            item.evidence_type == "entity_performance"
            and EVENT_RECAP_CORE_ENTITY_METRIC_PATTERN.search(text)
        ):
            continue
        if EVENT_LOW_PRIORITY_ENTITY_METRIC_PATTERN.search(text):
            return True
    return False


def event_fact_is_low_priority_for_recap(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> bool:
    slot = event_fact_slot(fact, evidence_lookup)
    items = evidence_for_fact(fact, evidence_lookup)
    text = " ".join(
        str(part)
        for item in items
        for part in [
            item.finding,
            item.strength_label,
            item.metrics.get("metric"),
            item.metrics.get("semantic_label"),
            item.metrics.get("question"),
            item.metrics.get("measure"),
            fact.fact_summary,
        ]
        if part
    )
    if slot == "leading_performance":
        if event_fact_has_low_priority_entity_metric(fact, evidence_lookup):
            return True
        if (
            any(item.evidence_type == "entity_performance" for item in items)
            and EVENT_RECAP_CORE_ENTITY_METRIC_PATTERN.search(text)
        ):
            return False
        if (
            any(item.evidence_type == "entity_ranking" for item in items)
            and not EVENT_RECAP_CORE_ENTITY_METRIC_PATTERN.search(text)
        ):
            return True
    if slot == "main_contrast":
        if EVENT_RECAP_LOW_PRIORITY_METRIC_PATTERN.search(text):
            return True
        if re.search(r"\bpoints?\b", text, re.IGNORECASE):
            return True
    if slot == "participant_record_context":
        return False
    return bool(EVENT_RECAP_LOW_PRIORITY_METRIC_PATTERN.search(text))


def event_fact_slot(
    fact: VerifiedFact,
    evidence_lookup: dict[str, EvidenceItem],
) -> str | None:
    items = evidence_for_fact(fact, evidence_lookup)
    evidence_types = {
        item.evidence_type
        for item in items
    }

    if "event_outcome" in evidence_types:
        return "event_result"

    if "event_status" in evidence_types:
        return "event_status"

    if "participant_record_context" in evidence_types:
        return "participant_record_context"

    if "score_progression" in evidence_types:
        return "score_progression"

    if "event_sequence" in evidence_types:
        return "event_sequence"

    if "event_context" in evidence_types:
        return "event_context"

    if evidence_types & {"entity_ranking", "entity_performance"}:
        if any(
            evidence_analytical_function(item)
            == AnalyticalFunction.PARTICIPATION
            for item in items
        ):
            return "participation"

        if any(event_evidence_is_segment_ranking(item) for item in items):
            return "event_sequence"

        return "leading_performance"

    if evidence_types & {
        "participant_comparison",
        "event_contrast",
    }:
        return "main_contrast"

    return None


def select_event_priority_facts(
    *,
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    settings: Settings,
    request: str,
    report_specification: Any | None = None,
) -> tuple[list[VerifiedFact], list[VerifiedFact]]:
    evidence_lookup = build_evidence_lookup(evidence)
    realisation_policy = getattr(
        report_specification,
        "realisation_policy",
        None,
    )
    realisation_policy_value = (
        realisation_policy.value
        if isinstance(realisation_policy, RealisationPolicy)
        else str(realisation_policy)
    )
    reference_recap_style = bool(
        report_specification is not None
        and (
            getattr(report_specification, "focus_scope", None)
            == "reference_recap"
            or realisation_policy_value
            == RealisationPolicy.EVENT_RECAP_STYLE.value
        )
    )

    def event_priority_score(
        fact: VerifiedFact,
    ) -> float:
        slot = event_fact_slot(fact, evidence_lookup)
        analytical_functions = {
            evidence_analytical_function(item)
            for item in evidence_for_fact(
                fact,
                evidence_lookup,
            )
        }
        component_bonus = (
            0.20
            if (
                slot == "main_contrast"
                and AnalyticalFunction.OUTCOME_COMPONENT
                in analytical_functions
            )
            else 0.0
        )
        sequence_bonus = 0.0
        if slot == "event_sequence":
            sequence_bonus = (
                0.35
                if event_sequence_fact_is_actionable(
                    fact,
                    evidence_lookup,
                )
                else -0.25
            )

        return (
            evidence_priority_score_for_fact(
                fact,
                evidence_lookup,
            )
            + component_bonus
            + sequence_bonus
        )

    ranked = sorted(
        facts,
        key=event_priority_score,
        reverse=True,
    )
    explicit_detail_requested = bool(
        re.search(
            r"\b(all|complete|detailed|every|exhaustive|full)\b",
            request,
            re.IGNORECASE,
        )
    )
    priority_limit = settings.writer_priority_fact_limit
    supporting_limit = (
        settings.writer_supporting_fact_limit
        if settings.writer_supporting_fact_limit is not None
        else None
    )
    uncapped_event_selection = (
        priority_limit is None
        and settings.writer_max_words is None
    )
    actionable_sequence_available = any(
        event_fact_slot(fact, evidence_lookup) == "event_sequence"
        and event_sequence_fact_is_actionable(fact, evidence_lookup)
        for fact in facts
    )

    selected: list[VerifiedFact] = []
    selected_ids: set[str] = set()
    slot_counts: dict[str, int] = {}
    if uncapped_event_selection:
        slot_limits: dict[str, int | None] = {
            "event_result": None,
            "event_context": None,
            "event_status": None,
            "participant_record_context": None,
            "score_progression": None,
            "event_sequence": None,
            "main_contrast": None,
            "leading_performance": None,
            "participation": None if explicit_detail_requested else 0,
        }
    else:
        slot_limits = {
            "event_result": 2,
            "event_context": 1,
            "event_status": 1,
            "participant_record_context": 1,
            "score_progression": 1,
            "event_sequence": None,
            "main_contrast": 2,
            "leading_performance": None,
            "participation": None if explicit_detail_requested else 0,
        }
    if reference_recap_style and not explicit_detail_requested:
        slot_limits.update(
            {
                "event_result": 2,
                "event_context": 1,
                "event_status": 1,
                "participant_record_context": 3,
                "score_progression": 1,
                "main_contrast": 3,
                "leading_performance": 10,
                "participation": 0,
            }
        )

    def can_use_fact(
        fact: VerifiedFact,
        *,
        as_supporting: bool = False,
    ) -> bool:
        if fact.fact_id in selected_ids and not as_supporting:
            return False
        if (
            fact.recommended_use == RecommendedUse.OMIT_UNLESS_REQUESTED
            and not explicit_detail_requested
        ):
            return False
        if (
            reference_recap_style
            and not explicit_detail_requested
            and event_fact_is_low_priority_for_recap(
                fact,
                evidence_lookup,
            )
        ):
            return False
        slot = event_fact_slot(fact, evidence_lookup)
        if slot == "participation" and not explicit_detail_requested:
            return False
        if (
            slot == "event_sequence"
            and actionable_sequence_available
            and not event_sequence_fact_is_actionable(
                fact,
                evidence_lookup,
            )
        ):
            return False
        if (
            slot == "leading_performance"
            and event_fact_has_low_priority_entity_metric(
                fact,
                evidence_lookup,
            )
            and not explicit_detail_requested
        ):
            return False
        return True

    for slot in (
        "event_result",
        "event_context",
        "participant_record_context",
        "event_status",
        "score_progression",
        "leading_performance",
        "main_contrast",
        "event_sequence",
        "participation",
    ):
        if priority_limit is not None and len(selected) >= priority_limit:
            break
        limit = slot_limits.get(slot)
        if limit == 0:
            continue
        for fact in ranked:
            if priority_limit is not None and len(selected) >= priority_limit:
                break
            if event_fact_slot(fact, evidence_lookup) != slot:
                continue
            if not can_use_fact(fact):
                continue
            if (
                limit is not None
                and slot_counts.get(slot, 0) >= limit
            ):
                break

            selected.append(fact)
            selected_ids.add(fact.fact_id)
            slot_counts[slot] = slot_counts.get(slot, 0) + 1

    supporting: list[VerifiedFact] = []
    for fact in ranked:
        if fact.fact_id in selected_ids:
            continue
        if not can_use_fact(fact, as_supporting=True):
            continue
        supporting.append(fact)
        if (
            supporting_limit is not None
            and len(supporting) >= supporting_limit
        ):
            break

    return selected, supporting


EVENT_PROFILE_INSIGHT_PATTERN = re.compile(
    r"\b(missing(?:ness| data| values?)|duplicates?|rows?|columns?|"
    r"constant columns?|correlations?|regressions?|"
    r"statistical (?:modelling|modeling|power)|"
    r"predictive (?:modelling|modeling)|feature sets?)\b",
    re.IGNORECASE,
)


def event_insight_is_relevant(
    insight: VerifiedInsight,
    request: str,
) -> bool:
    text = f"{insight.statement} {insight.why_it_matters}"
    if not EVENT_PROFILE_INSIGHT_PATTERN.search(text):
        return True

    return bool(EVENT_PROFILE_INSIGHT_PATTERN.search(request))


def scope_fact_ledger_for_genre(
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    genre: ReportGenre,
) -> FactLedger:
    evidence_lookup = {item.evidence_id: item for item in evidence.items}
    scoped_facts = [
        fact
        for fact in fact_ledger.writer_ready_facts
        if fact_is_relevant_to_genre(
            fact,
            evidence_lookup,
            genre,
        )
    ]
    return fact_ledger.model_copy(update={"writer_ready_facts": scoped_facts})


def build_writer_evidence_pack(
    request: str,
    understanding: Any,
    plan: Any,
    evidence: EvidenceLedger,
    fact_ledger: FactLedger,
    settings: Settings,
    insight_ledger: InsightLedger | None = None,
    input_structure: InputStructureProfile | None = None,
    available_capabilities: list[EvidenceCapability] | None = None,
) -> WriterEvidencePack:
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False,
        fallback_reason="No Insight Ledger was supplied.",
    )
    evidence_lookup = {item.evidence_id: item for item in evidence.items}
    scoped_fact_ledger = scope_fact_ledger_for_genre(
        fact_ledger,
        evidence,
        plan.report_specification.genre,
    )
    facts = scoped_fact_ledger.writer_ready_facts

    event_genre = plan.report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }
    focused_table_task = (
        getattr(plan.report_specification, "communication_task", None)
        == CommunicationTask.FOCUSED_TABLE_DESCRIPTION
    )

    if focused_table_task:
        focused_facts = [
            fact
            for fact in facts
            if EvidenceCapability.FOCUSED_TABLE_REGION
            in fact.source_capabilities
            or any(
                evidence_lookup[evidence_id].capability
                == EvidenceCapability.FOCUSED_TABLE_REGION
                for evidence_id in fact.evidence_ids
                if evidence_id in evidence_lookup
            )
        ]
        priority = sorted(
            focused_facts,
            key=lambda fact: evidence_priority_score_for_fact(
                fact,
                evidence_lookup,
            ),
            reverse=True,
        )
        supporting = []
    elif event_genre:
        priority, supporting = select_event_priority_facts(
            facts=facts,
            evidence=evidence,
            settings=settings,
            request=request,
            report_specification=plan.report_specification,
        )
    else:
        priority = select_balanced_priority_facts(
            facts=facts,
            evidence=evidence,
            required_components=(
                plan.report_specification.required_components
            ),
            settings=settings,
        )
        priority_ids = {
            fact.fact_id
            for fact in priority
        }
        ranked_facts = sorted(
            facts,
            key=lambda fact: evidence_priority_score_for_fact(
                fact,
                evidence_lookup,
            ),
            reverse=True,
        )
        supporting = [
            fact
            for fact in ranked_facts
            if fact.fact_id not in priority_ids
            and fact.recommended_use
            != RecommendedUse.OMIT_UNLESS_REQUESTED
        ]
        if settings.writer_supporting_fact_limit is not None:
            supporting = supporting[
                : settings.writer_supporting_fact_limit
            ]

    limitations = sorted(
        [
            fact
            for fact in facts
            if (
                fact.recommended_use == RecommendedUse.LIMITATION
                or ClaimPermission.INSUFFICIENCY in fact.claim_permissions
                or (fact.required_caveats and not event_genre)
            )
        ],
        key=lambda fact: evidence_priority_score_for_fact(fact, evidence_lookup),
        reverse=True,
    )

    recommendations = sorted(
        [
        recommendation
        for item in evidence.items
        for recommendation in item.recommendations
        if recommendation.priority in {"high", "medium"}
        ],
        key=lambda item: (
            {"high": 2, "medium": 1, "low": 0}.get(item.priority, 0),
            getattr(item, "confidence", 0.5),
        ),
        reverse=True,
    )

    prohibited = list(
        dict.fromkeys(
            interpretation
            for fact in facts
            for interpretation in fact.prohibited_interpretations
        )
    )
    scoped_fact_ids = {fact.fact_id for fact in facts}
    scoped_insight_ledger = insight_ledger.model_copy(
        update={
            "verified_insights": [
                insight
                for insight in insight_ledger.verified_insights
                if insight.source_fact_ids
                and set(insight.source_fact_ids).issubset(scoped_fact_ids)
                and (
                    not event_genre
                    or event_insight_is_relevant(insight, request)
                )
            ],
            "hypothesis_only_insights": [
                insight
                for insight in insight_ledger.hypothesis_only_insights
                if insight.source_fact_ids
                and set(insight.source_fact_ids).issubset(scoped_fact_ids)
                and (
                    not event_genre
                    or event_insight_is_relevant(insight, request)
                )
            ],
        }
    )
    priority_insights, supporting_insights = select_priority_verified_insights(
        insight_ledger=scoped_insight_ledger,
        maximum=settings.max_verified_main_insights,
    )

    return WriterEvidencePack(
        user_request=request,
        report_specification=plan.report_specification,
        dataset_understanding=understanding,
        input_structure=input_structure,
        available_capabilities=available_capabilities or [],
        priority_facts=priority,
        supporting_facts=supporting,
        limitation_facts=limitations,
        evidence_ledger=evidence,
        insight_ledger=scoped_insight_ledger,
        priority_verified_insights=priority_insights,
        supporting_verified_insights=supporting_insights,
        analytical_recommendations=recommendations,
        reader_facing_limitations=build_reader_facing_limitations(
            priority + limitations
        ),
        internal_prohibited_interpretations=prohibited,
    )


def _sentence_section_headings(
    markdown: str,
) -> dict[str, str]:
    headings: dict[str, str] = {}
    current_heading = ""

    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        if line.startswith("## "):
            current_heading = line[3:].strip()
            continue

        for sentence in split_markdown_sentences(line):
            headings[sentence] = current_heading

    return headings


def validate_writer_output(
    output: WriterOutput,
    fact_ledger: FactLedger,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
) -> list[str]:
    errors: list[str] = []
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    valid_fact_ids = {
        fact.fact_id
        for fact in fact_ledger.writer_ready_facts
    }
    fact_lookup = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insight_ids = {
        *verified_insights,
        *hypothesis_insights,
    }
    section_headings = _sentence_section_headings(output.markdown)

    unknown_title_fact_ids = set(output.title_fact_ids) - valid_fact_ids
    if unknown_title_fact_ids:
        errors.append(f"The title cites unknown fact IDs: {sorted(unknown_title_fact_ids)}")
    title_facts = [
        fact_lookup[fact_id] for fact_id in output.title_fact_ids if fact_id in fact_lookup
    ]
    all_title_entities = {
        entity
        for fact in fact_ledger.writer_ready_facts
        for entity in fact.entities
        if len(entity.strip()) >= 3
        and entity.casefold() in output.title.casefold()
    }
    title_requires_support = bool(
        extract_number_tokens(output.title)
        or (
            all_title_entities
            and FACTUAL_TITLE_PATTERN.search(output.title)
        )
    )
    if title_requires_support and not output.title_fact_ids:
        errors.append("A factual title must cite supporting fact IDs.")
    supported_title_entities = {
        entity
        for fact in title_facts
        for entity in fact.entities
    }
    unsupported_title_entities = (
        all_title_entities - supported_title_entities
    )
    if title_requires_support and unsupported_title_entities:
        errors.append(
            "The title contains entities unsupported by its facts: "
            f"{sorted(unsupported_title_entities)}"
        )
    title_support_numbers = [
        number
        for fact in title_facts
        for number in [
            *[
                value
                for _, value in extract_number_tokens(
                    fact.fact_summary
                )
            ],
            *flatten_numbers(fact.structured_values),
        ]
    ]
    if title_facts and not numbers_supported(
        output.title,
        title_support_numbers,
    ):
        errors.append("The title contains a number unsupported by its facts.")
    if CAUSAL_PATTERN.search(output.title) and not any(
        ClaimPermission.CAUSAL in fact.claim_permissions for fact in title_facts
    ):
        errors.append("The title introduces unsupported causal wording.")

    if re.search(r"\[(?:CLM|FACT)_\d+", output.markdown):
        errors.append(
            "Internal fact or claim IDs must not appear in the visible report."
        )

    if INTERNAL_CONTROL_PATTERN.search(output.markdown):
        errors.append(
            "The visible report exposes an internal writer or auditor control."
        )

    if FIELD_LABEL_PATTERN.search(output.markdown):
        errors.append(
            "The visible report renders internal evidence fields such as "
            "`Finding`, `Strength`, or `Important Note` rather than natural "
            "data-science prose."
        )

    seen_sentence_ids: set[str] = set()
    mapped_sentences = {
        support.sentence_text
        for support in output.sentence_support
    }
    factual_sentences = [
        sentence
        for sentence in split_markdown_sentences(output.markdown)
        if looks_factual(sentence)
    ]
    missing_mappings = [
        sentence
        for sentence in factual_sentences
        if sentence not in mapped_sentences
    ]
    if missing_mappings:
        errors.append(
            "Every factual sentence must appear exactly in the hidden sentence support map."
        )

    for support in output.sentence_support:
        if support.sentence_id in seen_sentence_ids:
            errors.append(
                f"Duplicate sentence ID: {support.sentence_id}"
            )
        seen_sentence_ids.add(support.sentence_id)

        if support.sentence_text not in output.markdown:
            errors.append(
                f"{support.sentence_id} text does not appear in the report."
            )

        unknown = set(support.fact_ids) - valid_fact_ids
        if unknown:
            errors.append(
                f"{support.sentence_id} cites unknown fact IDs: {sorted(unknown)}"
            )

        unknown_insights = (
            set(support.insight_ids)
            - all_insight_ids
        )
        if unknown_insights:
            errors.append(
                f"{support.sentence_id} cites unknown insight IDs: "
                f"{sorted(unknown_insights)}"
            )

        if (
            EXPLANATORY_HYPOTHESIS_PATTERN.search(
                support.sentence_text
            )
            and support.interpretation_level
            != InterpretationLevel.HYPOTHESIS
        ):
            errors.append(
                f"{support.sentence_id} presents a possible explanation "
                "without classifying it as a hypothesis."
            )

        if (
            support.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
        ):
            if not support.insight_ids:
                errors.append(
                    f"{support.sentence_id} is a bounded insight but has no "
                    "insight ID."
                )
            elif not set(support.insight_ids).issubset(
                set(verified_insights)
            ):
                errors.append(
                    f"{support.sentence_id} cites an insight that is not a "
                    "verified main insight."
                )
            else:
                required_fact_ids = {
                    fact_id
                    for insight_id in support.insight_ids
                    for fact_id in verified_insights[
                        insight_id
                    ].source_fact_ids
                }
                required_evidence_ids = {
                    evidence_id
                    for insight_id in support.insight_ids
                    for evidence_id in verified_insights[
                        insight_id
                    ].source_evidence_ids
                }
                if not required_fact_ids.issubset(
                    set(support.fact_ids)
                ):
                    errors.append(
                        f"{support.sentence_id} omits source facts for its "
                        "verified insight."
                    )
                if not required_evidence_ids.issubset(
                    set(support.evidence_ids)
                ):
                    errors.append(
                        f"{support.sentence_id} omits source evidence for its "
                        "verified insight."
                    )

        if (
            support.interpretation_level
            == InterpretationLevel.HYPOTHESIS
        ):
            if not allow_hypotheses_in_report:
                errors.append(
                    f"{support.sentence_id} is a hypothesis while hypotheses "
                    "are disabled."
                )
            if not support.insight_ids or not set(
                support.insight_ids
            ).issubset(set(hypothesis_insights)):
                errors.append(
                    f"{support.sentence_id} lacks valid hypothesis-only "
                    "provenance."
                )
            if section_headings.get(support.sentence_text, "").lower() != (
                "questions for further investigation"
            ):
                errors.append(
                    f"{support.sentence_id} places a hypothesis outside the "
                    "allowed section."
                )
            if (
                not HYPOTHESIS_WORDING_PATTERN.search(
                    support.sentence_text
                )
                and not support.sentence_text.strip().endswith("?")
            ):
                errors.append(
                    f"{support.sentence_id} does not explicitly label the "
                    "hypothesis or frame it as a question."
                )

        if (
            support.interpretation_level
            == InterpretationLevel.FINDING
            and support.insight_ids
        ):
            errors.append(
                f"{support.sentence_id} is a finding but cites insight IDs."
            )

        if (
            support.support_type != SupportType.NON_FACTUAL
            and not support.fact_ids
            and not support.profile_support_ids
            and not support.insight_ids
        ):
            errors.append(
                f"{support.sentence_id} is factual but has no supporting "
                "provenance."
            )

        supporting_facts = [
            fact_lookup[fact_id]
            for fact_id in support.fact_ids
            if fact_id in fact_lookup
        ]
        support_numbers = [
            number
            for fact in supporting_facts
            for number in [
                *[
                    value
                    for _, value in extract_number_tokens(
                        fact.fact_summary
                    )
                ],
                *flatten_numbers(fact.structured_values),
            ]
        ]
        if (
            supporting_facts
            and not numbers_supported(
                support.sentence_text,
                support_numbers,
            )
        ):
            errors.append(
                f"{support.sentence_id} contains a number unsupported by its "
                "mapped facts."
            )

        known_entities = {
            entity
            for fact in supporting_facts
            for entity in fact.entities
        }
        unsupported_entities = unsupported_backtick_entities(
            support.sentence_text,
            known_entities,
        )
        if supporting_facts and unsupported_entities:
            errors.append(
                f"{support.sentence_id} contains unsupported entities "
                f"{unsupported_entities}; mapped fact IDs: "
                f"{support.fact_ids}."
            )

    declared = set(output.selected_fact_ids)
    used = set(output.title_fact_ids)
    used.update(
        fact_id
        for support in output.sentence_support
        for fact_id in support.fact_ids
    )

    if declared != used:
        errors.append(
            "selected_fact_ids must match the facts used in sentence_support."
        )

    return errors


def apply_support_map_patches(
    writer_output: WriterOutput,
    patches: list[SupportMapPatch],
    valid_profile_support_ids: set[str],
) -> WriterOutput:
    original_markdown = writer_output.markdown
    support_map = [
        support.model_copy()
        for support in writer_output.sentence_support
    ]
    support_by_id = {
        support.sentence_id: support
        for support in support_map
    }

    for patch in patches:
        unknown = [
            support_id
            for support_id in patch.added_profile_support_ids
            if support_id not in valid_profile_support_ids
        ]

        if unknown:
            raise ValueError(
                "Support-map patch references unknown profile support "
                f"IDs: {unknown}"
            )

        support = support_by_id.get(patch.sentence_id)

        if support is None:
            raise ValueError(
                "Support-map patch references unknown sentence ID: "
                f"{patch.sentence_id}"
            )

        if support.sentence_text != patch.sentence_text:
            raise ValueError(
                "Support-map patch sentence text does not exactly match "
                "the hidden support entry."
            )

        merged_profile_ids = list(
            dict.fromkeys(
                [
                    *support.profile_support_ids,
                    *patch.added_profile_support_ids,
                ]
            )
        )

        replacement = support.model_copy(
            update={
                "profile_support_ids": merged_profile_ids
            }
        )
        support_index = support_map.index(support)
        support_map[support_index] = replacement
        support_by_id[patch.sentence_id] = replacement

    patched = writer_output.model_copy(
        update={
            "sentence_support": support_map
        }
    )

    assert patched.markdown == original_markdown
    return patched


def materialise_writer_output(
    draft: WriterAgentDraft,
    fact_ledger: FactLedger,
    *,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
    content_requirements: dict[str, Any] | None = None,
    writer_mode: str = "llm_writer",
    eligible_for_primary_evaluation: bool = True,
    quality_revision_round: int = 0,
    quality_revision_summary: str | None = None,
) -> WriterOutput:
    content_requirements = content_requirements or {}
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    fact_lookup = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insight_lookup = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insight_lookup = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insight_lookup = {
        **verified_insight_lookup,
        **hypothesis_insight_lookup,
    }
    output_form = content_requirements.get("output_form")
    short_form_without_headings = bool(
        content_requirements.get("allow_headings") is False
        or output_form
        in {
            OutputForm.ONE_SENTENCE.value,
            OutputForm.DIRECT_ANSWER.value,
            OutputForm.SHORT_TEXT.value,
        }
    )
    unknown_title_fact_ids = [
        fact_id for fact_id in draft.title_fact_ids if fact_id not in fact_lookup
    ]
    if unknown_title_fact_ids and not short_form_without_headings:
        raise ValueError(f"Writer draft title contains unknown fact IDs: {unknown_title_fact_ids}")

    lines: list[str] = (
        []
        if short_form_without_headings
        else [
            f"# {draft.title.strip()}",
            "",
        ]
    )
    max_rendered_sentences = (
        int(content_requirements["max_sentences"])
        if short_form_without_headings
        and content_requirements.get("max_sentences") is not None
        else None
    )

    sentence_support: list[SentenceSupport] = []
    selected_fact_ids: list[str] = (
        []
        if short_form_without_headings
        else list(dict.fromkeys(draft.title_fact_ids))
    )
    sentence_number = 1

    for section in draft.sections:
        heading = section.heading.strip()
        heading = re.sub(
            r"^#+\s*",
            "",
            heading,
        )

        if not heading:
            continue

        if (
            short_form_without_headings
            and max_rendered_sentences is not None
            and sentence_number > max_rendered_sentences
        ):
            break

        if not short_form_without_headings:
            lines.extend(
                [
                    f"## {heading}",
                    "",
                ]
            )

        for sentence_draft in section.sentences:
            if (
                short_form_without_headings
                and max_rendered_sentences is not None
                and sentence_number > max_rendered_sentences
            ):
                break

            sentence_text = re.sub(
                r"\s+",
                " ",
                sentence_draft.text,
            ).strip()

            if not sentence_text:
                continue

            if sentence_text[-1] not in ".!?":
                sentence_text += "."

            unknown_fact_ids = [
                fact_id
                for fact_id in sentence_draft.fact_ids
                if fact_id not in fact_lookup
            ]

            if unknown_fact_ids:
                raise ValueError(
                    "Writer draft contains unknown "
                    f"fact IDs: {unknown_fact_ids}"
                )

            unknown_insight_ids = [
                insight_id
                for insight_id in sentence_draft.insight_ids
                if insight_id not in all_insight_lookup
            ]
            if unknown_insight_ids:
                raise ValueError(
                    "Writer draft contains unknown insight IDs: "
                    f"{unknown_insight_ids}"
                )

            if (
                sentence_draft.interpretation_level
                == InterpretationLevel.BOUNDED_INSIGHT
            ):
                if not sentence_draft.insight_ids:
                    raise ValueError(
                        "A bounded-insight Writer sentence has no verified "
                        "insight ID."
                    )
                if not set(sentence_draft.insight_ids).issubset(
                    set(verified_insight_lookup)
                ):
                    raise ValueError(
                        "A bounded-insight Writer sentence cites an insight "
                        "that is not verified for the main report."
                    )

            if (
                sentence_draft.interpretation_level
                == InterpretationLevel.HYPOTHESIS
            ):
                if not allow_hypotheses_in_report:
                    raise ValueError(
                        "Writer hypotheses are disabled by configuration."
                    )
                if not sentence_draft.insight_ids or not set(
                    sentence_draft.insight_ids
                ).issubset(set(hypothesis_insight_lookup)):
                    raise ValueError(
                        "A hypothesis Writer sentence must cite a valid "
                        "hypothesis-only insight."
                    )

            if (
                sentence_draft.interpretation_level
                == InterpretationLevel.FINDING
                and sentence_draft.insight_ids
            ):
                raise ValueError(
                    "A direct Writer finding must not cite insight IDs."
                )

            expanded_fact_ids = list(
                dict.fromkeys(
                    [
                        *sentence_draft.fact_ids,
                        *[
                            fact_id
                            for insight_id in sentence_draft.insight_ids
                            for fact_id in all_insight_lookup[
                                insight_id
                            ].source_fact_ids
                            if fact_id in fact_lookup
                        ],
                    ]
                )
            )

            if (
                sentence_draft.support_type
                != SupportType.NON_FACTUAL
                and not expanded_fact_ids
            ):
                raise ValueError(
                    "A factual Writer sentence has no "
                    "supporting fact IDs."
                )

            evidence_ids = list(
                dict.fromkeys(
                    [
                        *[
                            evidence_id
                            for fact_id in expanded_fact_ids
                            for evidence_id in fact_lookup[
                                fact_id
                            ].evidence_ids
                        ],
                        *[
                            evidence_id
                            for insight_id in sentence_draft.insight_ids
                            for evidence_id in all_insight_lookup[
                                insight_id
                            ].source_evidence_ids
                        ],
                    ]
                )
            )

            rendered_sentences = (
                split_markdown_sentences(sentence_text)
                or [sentence_text]
            )

            for rendered_sentence in rendered_sentences:
                if (
                    short_form_without_headings
                    and max_rendered_sentences is not None
                    and sentence_number > max_rendered_sentences
                ):
                    break

                lines.append(rendered_sentence)

                sentence_support.append(
                    SentenceSupport(
                        sentence_id=(
                            f"SENT_{sentence_number:04d}"
                        ),
                        sentence_text=rendered_sentence,
                        fact_ids=expanded_fact_ids,
                        evidence_ids=evidence_ids,
                        insight_ids=list(
                            dict.fromkeys(
                                sentence_draft.insight_ids
                            )
                        ),
                        interpretation_level=(
                            sentence_draft.interpretation_level
                        ),
                        support_type=(
                            sentence_draft.support_type
                        ),
                    )
                )

                selected_fact_ids.extend(
                    expanded_fact_ids
                )

                sentence_number += 1

        if not short_form_without_headings:
            lines.append("")

    selected_fact_ids = list(
        dict.fromkeys(selected_fact_ids)
    )

    all_fact_ids = [
        fact.fact_id
        for fact in fact_ledger.writer_ready_facts
    ]

    output = WriterOutput(
        title=(
            "Focused table description"
            if short_form_without_headings
            else draft.title.strip()
        ),
        title_fact_ids=(
            []
            if short_form_without_headings
            else list(dict.fromkeys(draft.title_fact_ids))
        ),
        markdown=(
            "\n".join(lines).strip()
            + "\n"
        ),
        sentence_support=sentence_support,
        selected_fact_ids=selected_fact_ids,
        omitted_fact_ids=[
            fact_id
            for fact_id in all_fact_ids
            if fact_id not in selected_fact_ids
        ],
        writer_notes=draft.writer_notes,
        writer_mode=writer_mode,
        eligible_for_primary_evaluation=(
            eligible_for_primary_evaluation
        ),
        quality_revision_round=(
            quality_revision_round
        ),
        quality_revision_summary=(
            quality_revision_summary
        ),
    )

    errors = validate_writer_output(
        output,
        fact_ledger,
        insight_ledger,
        allow_hypotheses_in_report,
    )
    errors.extend(
        writer_output_content_requirement_errors(
            writer_output=output,
            requirements=content_requirements,
            include_word_count=True,
        )
    )

    if errors:
        raise ValueError(
            "Controller-generated WriterOutput "
            "failed validation:\n- "
            + "\n- ".join(errors)
        )

    return output



def writer_output_word_count(
    output: WriterOutput,
) -> int:
    return len(
        re.findall(
            r"\b[\w'-]+\b",
            output.markdown,
        )
    )


def accept_writer_quality_revision(
    *,
    before: WriterOutput,
    after: WriterOutput,
    before_audit: AuditReport,
    after_audit: AuditReport,
    validation_errors: list[str],
    report_specification: Any,
    settings: Settings,
) -> tuple[bool, list[str]]:
    """
    Accept a whole-report quality revision only when it is valid and
    measurably improves the incomplete draft.
    """

    reasons: list[str] = list(
        validation_errors
    )

    before_missing = sum(
        not assessment.covered
        for assessment
        in before_audit.component_assessments
    )

    after_missing = sum(
        not assessment.covered
        for assessment
        in after_audit.component_assessments
    )

    before_words = writer_output_word_count(
        before
    )
    after_words = writer_output_word_count(
        after
    )

    minimum_words = minimum_useful_report_words(
        target_words=(
            report_specification
            .target_length_words
        ),
        required_component_count=len(
            report_specification
            .required_components
        ),
        settings=settings,
    )
    maximum_words = report_specification.maximum_length_words

    if maximum_words is not None and after_words > maximum_words:
        reasons.append(
            "The revision exceeds the configured report word ceiling."
        )

    if (
        before_missing > 0
        and after_missing >= before_missing
    ):
        reasons.append(
            "The revision did not reduce the number "
            "of missing required components."
        )

    if (
        before_words < minimum_words
        and after_words <= before_words
    ):
        reasons.append(
            "The revision did not improve the "
            "under-length report."
        )

    if (
        before_missing > 0
        and len(after.sentence_support)
        < len(before.sentence_support)
    ):
        reasons.append(
            "The revision reduced supported sentence "
            "coverage while the report was incomplete."
        )

    serious_after = {
        (
            annotation.sentence,
            annotation.subtype,
        )
        for annotation
        in after_audit.annotations
        if annotation.severity
        in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
    }

    serious_before = {
        (
            annotation.sentence,
            annotation.subtype,
        )
        for annotation
        in before_audit.annotations
        if annotation.severity
        in {
            Severity.HIGH,
            Severity.CRITICAL,
        }
    }

    introduced_serious = (
        serious_after - serious_before
    )

    if introduced_serious:
        reasons.append(
            "The revision introduced a new serious "
            "factual or contextual annotation."
        )

    return (
        not reasons,
        list(dict.fromkeys(reasons)),
    )


def _focused_table_fallback_writer(
    pack: WriterEvidencePack,
    evidence_by_id: dict[str, EvidenceItem],
) -> WriterOutput | None:
    available_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                pack.priority_facts
                + pack.supporting_facts
                + pack.limitation_facts
            )
        }.values()
    )
    fact_lookup = {
        fact.fact_id: fact
        for fact in available_facts
    }
    focused_insight = next(
        (
            insight
            for insight in [
                *pack.priority_verified_insights,
                *pack.supporting_verified_insights,
            ]
            if any(
                evidence_by_id[evidence_id].capability
                == EvidenceCapability.FOCUSED_TABLE_REGION
                for evidence_id in insight.source_evidence_ids
                if evidence_id in evidence_by_id
            )
        ),
        None,
    )
    if focused_insight is not None:
        sentence = re.sub(
            r"\s+",
            " ",
            focused_insight.statement,
        ).strip()
        if sentence and sentence[-1] not in ".!?":
            sentence += "."
        fact_ids = [
            fact_id
            for fact_id in focused_insight.source_fact_ids
            if fact_id in fact_lookup
        ]
        evidence_ids = list(focused_insight.source_evidence_ids)
        support = SentenceSupport(
            sentence_id="SENT_0001",
            sentence_text=sentence,
            fact_ids=fact_ids,
            evidence_ids=evidence_ids,
            insight_ids=[focused_insight.insight_id],
            interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
            support_type=SupportType.MULTI_FACT_SYNTHESIS,
        )
        return WriterOutput(
            title="Focused table description",
            markdown=sentence + "\n",
            sentence_support=[support],
            selected_fact_ids=fact_ids,
            omitted_fact_ids=[
                fact.fact_id
                for fact in available_facts
                if fact.fact_id not in set(fact_ids)
            ],
            writer_notes=[
                "Deterministic short-form writer used a verified "
                "focused-table insight.",
                "This requested short-form verbalisation is eligible for "
                "primary evaluation because it is directly support-mapped.",
            ],
            writer_mode="deterministic_short_form_writer",
            eligible_for_primary_evaluation=True,
        )

    focused_fact = next(
        (
            fact
            for fact in available_facts
            if any(
                evidence_by_id[evidence_id].capability
                == EvidenceCapability.FOCUSED_TABLE_REGION
                for evidence_id in fact.evidence_ids
                if evidence_id in evidence_by_id
            )
        ),
        None,
    )
    if focused_fact is None:
        return None

    evidence_item = next(
        (
            evidence_by_id[evidence_id]
            for evidence_id in focused_fact.evidence_ids
            if evidence_id in evidence_by_id
            and evidence_by_id[evidence_id].capability
            == EvidenceCapability.FOCUSED_TABLE_REGION
        ),
        None,
    )
    metrics = evidence_item.metrics if evidence_item is not None else {}

    values = [
        str(value).strip()
        for value in metrics.get("highlighted_values", [])
        if str(value).strip()
    ]
    row_context = [
        str(value).strip()
        for value in metrics.get("row_context", [])
        if str(value).strip()
    ]
    header_context = [
        str(value).strip()
        for value in metrics.get("header_context", [])
        if str(value).strip()
    ]
    page_title = str(metrics.get("page_title") or "").strip()
    section_title = str(metrics.get("section_title") or "").strip()
    proposition = str(metrics.get("description_proposition") or "").strip()
    local_contrast = _focused_table_local_contrast_summary(metrics)
    record_relation = metrics.get("focused_record_relation")
    record_summary = (
        str(record_relation.get("relation_summary") or "").strip()
        if isinstance(record_relation, dict)
        else ""
    )
    list_relation = metrics.get("focused_list_relation")
    list_summary = (
        str(list_relation.get("relation_summary") or "").strip()
        if isinstance(list_relation, dict)
        else ""
    )
    record_group_summary = str(
        metrics.get("highlighted_record_group_summary") or ""
    ).strip()

    value_text = ", ".join(values)
    sentence = focused_fact.fact_summary
    if local_contrast:
        sentence = local_contrast
    elif record_summary:
        sentence = record_summary
    elif list_summary:
        sentence = list_summary
    elif record_group_summary:
        sentence = record_group_summary
    elif proposition:
        sentence = proposition
    elif value_text:
        if row_context and header_context:
            sentence = (
                f"The selected table value is {value_text} under the "
                f"{header_context[0]} header in the row containing "
                f"{row_context[0]}"
            )
        elif row_context:
            sentence = (
                f"The selected table value is {value_text} in the row "
                f"containing {row_context[0]}"
            )
        else:
            sentence = f"The selected table cell value is {value_text}"

        context_parts = [
            part
            for part in [section_title, page_title]
            if part
        ]
        if context_parts:
            sentence += " in " + " / ".join(context_parts)

    sentence = re.sub(r"\s+", " ", sentence).strip()
    if sentence and sentence[-1] not in ".!?":
        sentence += "."

    support = SentenceSupport(
        sentence_id="SENT_0001",
        sentence_text=sentence,
        fact_ids=[focused_fact.fact_id],
        evidence_ids=list(focused_fact.evidence_ids),
        support_type=SupportType.DIRECT,
    )

    return WriterOutput(
        title="Focused table description",
        markdown=sentence + "\n",
        sentence_support=[support],
        selected_fact_ids=[focused_fact.fact_id],
        omitted_fact_ids=[
            fact.fact_id
            for fact in available_facts
            if fact.fact_id != focused_fact.fact_id
        ],
        writer_notes=[
            "Deterministic short-form writer used verified focused-table "
            "evidence.",
            "This requested short-form verbalisation is eligible for "
            "primary evaluation because it is directly support-mapped.",
        ],
        writer_mode="deterministic_short_form_writer",
        eligible_for_primary_evaluation=True,
    )


def _humanise_record_key(value: str) -> str:
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    text = text.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def _compact_record_value(value: Any) -> str:
    text = str(value or "").strip()
    text = text.replace("_", " ")
    text = re.sub(r"\(([^)]+)\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def _record_subject_text(
    value: Any,
    *,
    realisation_policy: RealisationPolicy,
) -> str:
    text = str(value or "").strip()
    if realisation_policy == RealisationPolicy.NATURAL_REFERENCE_STYLE:
        text = text.replace("_", " ")
    return re.sub(r"\s+", " ", text).strip()


def _ordinal_text(value: Any) -> str:
    text = str(value or "").strip()
    try:
        number = int(float(text))
    except ValueError:
        return text
    suffix = "th"
    if number % 100 not in {11, 12, 13}:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def _attribute_sentence(
    records: list[dict[str, Any]],
) -> str:
    attributes = [
        (
            _humanise_record_key(str(record.get("attribute_name") or "")),
            str(record.get("attribute_value") or "").strip(),
        )
        for record in records
        if str(record.get("record_kind") or "") != "triple"
        and str(record.get("attribute_name") or "").strip()
        and str(record.get("attribute_value") or "").strip()
    ]
    if not attributes:
        return ""

    by_key = {
        re.sub(r"[^a-z0-9]+", "", key.casefold()): (key, value)
        for key, value in attributes
    }
    subject = next(
        (
            value
            for key in ["name", "title", "label"]
            if key in by_key
            for _, value in [by_key[key]]
        ),
        None,
    )
    if subject is None:
        subject = attributes[0][1]

    used_keys: set[str] = set()
    clauses: list[str] = []
    type_value = next(
        (
            value
            for key in ["eattype", "type", "category"]
            if key in by_key
            for _, value in [by_key[key]]
        ),
        None,
    )
    if type_value:
        article = "an" if type_value[:1].casefold() in {"a", "e", "i", "o", "u"} else "a"
        clauses.append(f"is {article} {type_value}")
        used_keys.update({"eattype", "type", "category"})

    relation_clauses: list[str] = []
    for normalised_key, (key, value) in by_key.items():
        if normalised_key in used_keys or normalised_key in {"name", "title", "label"}:
            continue
        if normalised_key == "near":
            relation_clauses.append(f"near {value}")
        elif normalised_key == "area":
            relation_clauses.append(f"in the {value} area")
        elif normalised_key == "food":
            relation_clauses.append(f"serves {value} food")
        elif normalised_key in {"customerrating", "rating"}:
            relation_clauses.append(f"has a {key} of {value}")
        elif normalised_key == "pricerange":
            relation_clauses.append(f"has a {key} of {value}")
        elif normalised_key == "rank":
            relation_clauses.append(f"ranks {_ordinal_text(value)}")
        elif normalised_key == "total":
            relation_clauses.append(f"has a total of {value}")
        elif normalised_key == "familyfriendly":
            if value.casefold() in {"yes", "true", "1"}:
                relation_clauses.append("is family friendly")
            elif value.casefold() in {"no", "false", "0"}:
                relation_clauses.append("is not family friendly")
            else:
                relation_clauses.append(f"has {key} {value}")
        else:
            relation_clauses.append(f"has {key} {value}")

    if clauses:
        sentence = f"{subject} " + " and ".join(clauses)
        if relation_clauses:
            prepositional = [
                clause
                for clause in relation_clauses
                if clause.startswith(("near ", "in ", "at ", "on "))
            ]
            predicates = [
                clause
                for clause in relation_clauses
                if clause not in prepositional
            ]
            if prepositional:
                sentence += " " + " and ".join(prepositional)
            if predicates:
                sentence += " and " + " and ".join(predicates)
    else:
        details = [
            f"{key} {value}"
            for key, value in attributes
            if value != subject
        ]
        sentence = (
            f"{subject} has " + ", ".join(details)
            if details
            else str(subject)
        )

    return sentence.strip()


def _triple_relation_clause(relation: str, obj: str) -> str:
    normalised = re.sub(r"[^a-z0-9]+", "", relation.casefold())
    value = _compact_record_value(obj)
    if normalised in {"engine", "enginetype"}:
        if (
            value
            and not value.isupper()
            and not re.search(r"\b[A-Z]{2,}\b", value)
        ):
            value = value[:1].lower() + value[1:]
        if value.casefold().endswith("engine"):
            return f"has a {value}"
        article = "an" if value[:1].casefold() in {"a", "e", "i", "o", "u"} else "a"
        return f"has {article} {value} engine"
    if normalised in {"cylindercount", "cylinders", "numberofcylinders"}:
        return f"has {value} cylinders"
    if normalised in {"length", "height", "width", "diameter"}:
        return f"has a {relation} of {value}"
    if normalised == "rank":
        return f"ranks {_ordinal_text(value)}"
    if normalised == "total":
        return f"has a total of {value}"
    return f"has {_humanise_record_key(relation)} {value}"


def _triple_sentence(
    records: list[dict[str, Any]],
    *,
    realisation_policy: RealisationPolicy = (
        RealisationPolicy.STRICT_SOURCE_SURFACE
    ),
) -> str:
    triples = [
        (
            _record_subject_text(
                record.get("subject"),
                realisation_policy=realisation_policy,
            ),
            _humanise_record_key(str(record.get("relation") or "")),
            str(record.get("object") or "").strip(),
        )
        for record in records
        if str(record.get("record_kind") or "") == "triple"
        and str(record.get("subject") or "").strip()
        and str(record.get("relation") or "").strip()
        and str(record.get("object") or "").strip()
    ]
    if not triples:
        return ""

    grouped: dict[str, list[tuple[str, str]]] = {}
    for subject, relation, obj in triples:
        grouped.setdefault(subject, []).append((relation, obj))

    sentences: list[str] = []
    for subject, relations in grouped.items():
        relation_text = ", ".join(
            _triple_relation_clause(relation, obj)
            for relation, obj in relations
        )
        if len(relations) > 1 and "," in relation_text:
            head, _, tail = relation_text.rpartition(", ")
            relation_text = f"{head}, and {tail}"
        sentences.append(f"{subject} {relation_text}")
    return "; ".join(sentences)


def _structured_record_fallback_writer(
    pack: WriterEvidencePack,
    evidence_by_id: dict[str, EvidenceItem],
) -> WriterOutput | None:
    realisation_policy = getattr(
        pack.report_specification,
        "realisation_policy",
        RealisationPolicy.STRICT_SOURCE_SURFACE,
    )
    if not isinstance(realisation_policy, RealisationPolicy):
        try:
            realisation_policy = RealisationPolicy(str(realisation_policy))
        except ValueError:
            realisation_policy = RealisationPolicy.STRICT_SOURCE_SURFACE
    available_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                pack.priority_facts
                + pack.supporting_facts
                + pack.limitation_facts
            )
        }.values()
    )
    fact_lookup = {
        fact.fact_id: fact
        for fact in available_facts
    }
    structured_insight = next(
        (
            insight
            for insight in [
                *pack.priority_verified_insights,
                *pack.supporting_verified_insights,
            ]
            if any(
                evidence_by_id[evidence_id].capability
                == EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
                for evidence_id in insight.source_evidence_ids
                if evidence_id in evidence_by_id
            )
        ),
        None,
    )
    if structured_insight is not None:
        sentence = re.sub(r"\s+", " ", structured_insight.statement).strip()
        if sentence and sentence[-1] not in ".!?":
            sentence += "."
        fact_ids = [
            fact_id
            for fact_id in structured_insight.source_fact_ids
            if fact_id in fact_lookup
        ]
        evidence_ids = list(structured_insight.source_evidence_ids)
        return WriterOutput(
            title="Structured record verbalisation",
            markdown=sentence + "\n",
            sentence_support=[
                SentenceSupport(
                    sentence_id="SENT_0001",
                    sentence_text=sentence,
                    fact_ids=fact_ids,
                    evidence_ids=evidence_ids,
                    insight_ids=[structured_insight.insight_id],
                    interpretation_level=InterpretationLevel.BOUNDED_INSIGHT,
                    support_type=SupportType.MULTI_FACT_SYNTHESIS,
                )
            ],
            selected_fact_ids=fact_ids,
            omitted_fact_ids=[
                fact.fact_id
                for fact in available_facts
                if fact.fact_id not in set(fact_ids)
            ],
            writer_notes=[
                "Deterministic short-form writer used a verified "
                "structured-record insight.",
                "This requested short-form verbalisation is eligible for "
                "primary evaluation because it is directly support-mapped.",
            ],
            writer_mode="deterministic_short_form_writer",
            eligible_for_primary_evaluation=True,
        )

    structured_fact = next(
        (
            fact
            for fact in available_facts
            if any(
                evidence_by_id[evidence_id].capability
                == EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
                for evidence_id in fact.evidence_ids
                if evidence_id in evidence_by_id
            )
        ),
        None,
    )
    if structured_fact is None:
        return None

    evidence_item = next(
        (
            evidence_by_id[evidence_id]
            for evidence_id in structured_fact.evidence_ids
            if evidence_id in evidence_by_id
            and evidence_by_id[evidence_id].capability
            == EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
        ),
        None,
    )
    metrics = evidence_item.metrics if evidence_item is not None else {}
    records = [
        record
        for record in metrics.get("records", [])
        if isinstance(record, dict)
    ]
    sentence = _triple_sentence(
        records,
        realisation_policy=realisation_policy,
    ) or _attribute_sentence(records)
    sentence = sentence or structured_fact.fact_summary
    sentence = re.sub(r"\s+", " ", sentence).strip()
    if sentence and sentence[-1] not in ".!?":
        sentence += "."

    return WriterOutput(
        title="Structured record verbalisation",
        markdown=sentence + "\n",
        sentence_support=[
            SentenceSupport(
                sentence_id="SENT_0001",
                sentence_text=sentence,
                fact_ids=[structured_fact.fact_id],
                evidence_ids=list(structured_fact.evidence_ids),
                support_type=SupportType.DIRECT,
            )
        ],
        selected_fact_ids=[structured_fact.fact_id],
        omitted_fact_ids=[
            fact.fact_id
            for fact in available_facts
            if fact.fact_id != structured_fact.fact_id
        ],
        writer_notes=[
            "Deterministic short-form writer used verified structured-record "
            "evidence.",
            "This requested short-form verbalisation is eligible for primary "
            "evaluation because it is directly support-mapped.",
        ],
        writer_mode="deterministic_short_form_writer",
        eligible_for_primary_evaluation=True,
    )


def fallback_writer(
    pack: WriterEvidencePack,
) -> WriterOutput:
    """
    Safe deterministic fallback.

    It is deliberately richer than a two-sentence renderer, but remains
    ineligible for primary evaluation because it is not the natural LLM
    Writer.
    """

    event_report = (
        pack.report_specification.genre
        in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }
    )
    reference_recap_style = (
        event_report
        and pack.report_specification.focus_scope == "reference_recap"
    )
    evidence_by_id = build_evidence_lookup(
        pack.evidence_ledger
    )
    if (
        pack.report_specification.communication_task
        == CommunicationTask.FOCUSED_TABLE_DESCRIPTION
    ):
        focused_output = _focused_table_fallback_writer(
            pack,
            evidence_by_id,
        )
        if focused_output is not None:
            return focused_output
    if pack.report_specification.communication_task in {
        CommunicationTask.ATTRIBUTE_VERBALISATION,
        CommunicationTask.TRIPLE_VERBALISATION,
    }:
        structured_output = _structured_record_fallback_writer(
            pack,
            evidence_by_id,
        )
        if structured_output is not None:
            return structured_output

    priority_facts = pack.priority_facts
    if pack.report_specification.maximum_main_findings is not None:
        priority_facts = priority_facts[
            : pack.report_specification.maximum_main_findings
        ]

    selected = list(
        {
            fact.fact_id: fact
            for fact in (
                priority_facts
                + pack.limitation_facts
            )
        }.values()
    )

    sections: dict[
        ReportComponent,
        list[VerifiedFact],
    ] = {
        ReportComponent.DATASET_OVERVIEW: [],
        ReportComponent.DATA_QUALITY: [],
        ReportComponent.STRONGEST_RELATIONSHIPS: [],
        ReportComponent.MODELLING_VALIDATION: [],
        ReportComponent.LIMITATIONS_NEXT_STEPS: [],
    }

    for fact in selected:
        component = classify_fact_component(
            fact,
            evidence_by_id,
        )

        sections.setdefault(
            component,
            [],
        ).append(fact)

    headings = (
        {
            ReportComponent.DATASET_OVERVIEW: (
                "Result and leading performances"
            ),
            ReportComponent.DATA_QUALITY: (
                "Record quality"
            ),
            ReportComponent.STRONGEST_RELATIONSHIPS: (
                "Main participant contrasts"
            ),
            ReportComponent.MODELLING_VALIDATION: (
                "Supporting analysis"
            ),
            ReportComponent.LIMITATIONS_NEXT_STEPS: (
                "Limitations"
            ),
        }
        if event_report
        else {
            ReportComponent.DATASET_OVERVIEW: (
                "Dataset overview"
            ),
            ReportComponent.DATA_QUALITY: (
                "Data quality"
            ),
            ReportComponent.STRONGEST_RELATIONSHIPS: (
                "Strongest observed relationships"
            ),
            ReportComponent.MODELLING_VALIDATION: (
                "Modelling and validation"
            ),
            ReportComponent.LIMITATIONS_NEXT_STEPS: (
                "Limitations and next steps"
            ),
        }
    )

    report_title = (
        "Evidence-grounded event report"
        if event_report
        else "Evidence-grounded data-science report"
    )

    lines = (
        []
        if reference_recap_style
        else [
            f"# {report_title}",
            "",
        ]
    )

    support_map: list[SentenceSupport] = []
    sentence_counter = 1
    rendered_recommendations: set[str] = set()

    def add_supported_sentence(
        sentence: str,
        facts: list[VerifiedFact],
        support_type: SupportType,
    ) -> None:
        nonlocal sentence_counter

        cleaned = sentence.strip()

        if not cleaned:
            return

        if cleaned[-1] not in ".!?":
            cleaned += "."

        lines.append(cleaned)

        fact_ids = list(
            dict.fromkeys(
                fact.fact_id
                for fact in facts
            )
        )

        evidence_ids = list(
            dict.fromkeys(
                evidence_id
                for fact in facts
                for evidence_id in fact.evidence_ids
            )
        )

        rendered_sentences = (
            split_markdown_sentences(cleaned)
            or [cleaned]
        )
        for rendered_sentence in rendered_sentences:
            support_map.append(
                SentenceSupport(
                    sentence_id=(
                        f"SENT_{sentence_counter:04d}"
                    ),
                    sentence_text=rendered_sentence,
                    fact_ids=fact_ids,
                    evidence_ids=evidence_ids,
                    support_type=support_type,
                )
            )

            sentence_counter += 1

    for component in [
        ReportComponent.DATASET_OVERVIEW,
        ReportComponent.DATA_QUALITY,
        ReportComponent.STRONGEST_RELATIONSHIPS,
        ReportComponent.MODELLING_VALIDATION,
    ]:
        component_facts = sections.get(
            component,
            [],
        )

        if not component_facts:
            continue

        if not reference_recap_style:
            lines.extend(
                [
                    f"## {headings[component]}",
                    "",
                ]
            )

        for fact in component_facts:
            sentence = (
                reader_facing_caveat(
                    fact.fact_summary
                )
                or fact.fact_summary
            )

            add_supported_sentence(
                sentence,
                [fact],
                SupportType.DIRECT,
            )

            if (
                component
                == ReportComponent.DATA_QUALITY
            ):
                for evidence_id in fact.evidence_ids:
                    item = evidence_by_id.get(
                        evidence_id
                    )

                    if item is None:
                        continue

                    for recommendation in (
                        item.recommendations
                    ):
                        if (
                            recommendation.priority
                            not in {"high", "medium"}
                        ):
                            continue

                        action = (
                            recommendation.action.strip()
                        )

                        if (
                            action
                            in rendered_recommendations
                        ):
                            continue

                        rendered_recommendations.add(
                            action
                        )

                        add_supported_sentence(
                            action,
                            [fact],
                            SupportType.PARAPHRASE,
                        )

        if not reference_recap_style:
            lines.append("")

    limitation_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                sections.get(
                    ReportComponent
                    .LIMITATIONS_NEXT_STEPS,
                    [],
                )
                + [
                    fact
                    for fact in selected
                    if (
                        fact.required_caveats
                        or ClaimPermission.COMPARATIVE
                        in fact.claim_permissions
                        or ClaimPermission.ASSOCIATIONAL
                        in fact.claim_permissions
                    )
                ]
            )
        }.values()
    )
    event_limitations = list(
        dict.fromkeys(
            caveat
            for fact in selected
            for caveat in fact.required_caveats
        )
    )

    if (
        not reference_recap_style
        and (
            (
                event_limitations
                if event_report
                else pack.reader_facing_limitations
            )
            or limitation_facts
            or rendered_recommendations
        )
    ):
        lines.extend(
            [
                "## "
                + headings[
                    ReportComponent.LIMITATIONS_NEXT_STEPS
                ],
                "",
            ]
        )

        for fact in sections.get(
            ReportComponent
            .LIMITATIONS_NEXT_STEPS,
            [],
        ):
            add_supported_sentence(
                fact.fact_summary,
                [fact],
                SupportType.DIRECT,
            )

        if event_report:
            for limitation in event_limitations:
                supporting = [
                    fact
                    for fact in selected
                    if limitation in fact.required_caveats
                ]
                if supporting:
                    add_supported_sentence(
                        limitation,
                        supporting,
                        SupportType.PARAPHRASE,
                    )
        else:
            relationship_facts = [
                fact
                for fact in selected
                if (
                    ClaimPermission.COMPARATIVE
                    in fact.claim_permissions
                    or ClaimPermission.ASSOCIATIONAL
                    in fact.claim_permissions
                )
            ]

            for limitation in (
                pack.reader_facing_limitations
            ):
                supporting = (
                    relationship_facts
                    or limitation_facts
                )

                if supporting:
                    add_supported_sentence(
                        limitation,
                        supporting,
                        SupportType.MULTI_FACT_SYNTHESIS,
                    )

        lines.append("")

    used_fact_ids = list(
        dict.fromkeys(
            fact_id
            for support in support_map
            for fact_id in support.fact_ids
        )
    )

    available_facts = list(
        {
            fact.fact_id: fact
            for fact in (
                pack.priority_facts
                + pack.supporting_facts
                + pack.limitation_facts
            )
        }.values()
    )

    return WriterOutput(
        title=report_title,
        markdown=(
            "\n".join(lines).strip()
            + "\n"
        ),
        sentence_support=support_map,
        selected_fact_ids=used_fact_ids,
        omitted_fact_ids=[
            fact.fact_id
            for fact in available_facts
            if fact.fact_id
            not in set(used_fact_ids)
        ],
        writer_notes=[
            "Deterministic writer fallback was used.",
            "This output is preserved for debugging "
            "and is not eligible for primary evaluation.",
        ],
        writer_mode=(
            "deterministic_fallback"
        ),
        eligible_for_primary_evaluation=False,
    )

def default_quality_assessment() -> ReportQualityAssessment:
    return ReportQualityAssessment(
        status=QualityStatus.PASS,
        request_responsiveness=1.0,
        finding_selection=1.0,
        coherence=1.0,
        concision=1.0,
        caveat_integration=1.0,
        data_science_interpretation=1.0,
        findings=[],
        recommendations=[],
    )


def assess_report_component_coverage(
    *,
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
) -> list[ReportComponentAssessment]:
    """
    Assess coverage using the sentence support map.

    Limitations and next steps may be supported by the same verified
    relationship or quality fact used elsewhere, so they are not
    restricted to facts whose primary component is LIMITATIONS.
    """

    fact_lookup = {
        fact.fact_id: fact
        for fact
        in fact_ledger.writer_ready_facts
    }

    evidence_by_id = build_evidence_lookup(
        evidence
    )

    support_by_component: defaultdict[
        ReportComponent,
        list[str],
    ] = defaultdict(list)
    component_covered_without_facts: set[ReportComponent] = set()

    for component in required_components:
        support_by_component[component]

    limitation_language = re.compile(
        r"\b("
        r"limitation|"
        r"unadjusted|"
        r"causal|causation|"
        r"confound|"
        r"precision|stability|"
        r"validate|verify|inspect|investigate|"
        r"remove|exclude|check|"
        r"next step|further analysis|"
        r"deployment|backtest"
        r")\b",
        re.IGNORECASE,
    )

    for support in writer_output.sentence_support:
        supported_facts = [
            fact_lookup[fact_id]
            for fact_id in support.fact_ids
            if fact_id in fact_lookup
        ]

        for fact in supported_facts:
            component = classify_fact_component(
                fact,
                evidence_by_id,
            )

            if (
                component
                in required_components
            ):
                support_by_component[
                    component
                ].append(fact.fact_id)

        if (
            ReportComponent
            .LIMITATIONS_NEXT_STEPS
            in required_components
            and limitation_language.search(
                support.sentence_text
            )
        ):
            if supported_facts:
                support_by_component[
                    ReportComponent
                    .LIMITATIONS_NEXT_STEPS
                ].extend(
                    fact.fact_id
                    for fact in supported_facts
                )
            else:
                component_covered_without_facts.add(
                    ReportComponent.LIMITATIONS_NEXT_STEPS
                )

    assessments: list[
        ReportComponentAssessment
    ] = []

    for component in required_components:
        fact_ids = list(
            dict.fromkeys(
                support_by_component[component]
            )
        )
        covered = (
            bool(fact_ids)
            or component in component_covered_without_facts
        )

        assessments.append(
            ReportComponentAssessment(
                component=component,
                covered=covered,
                supporting_fact_ids=fact_ids,
                explanation=(
                    "At least one report sentence is "
                    "mapped to verified support for "
                    "this component."
                    if fact_ids
                    else (
                        "A scoped non-factual caveat clearly covers "
                        "this component."
                        if covered
                        else (
                            "No supported report sentence "
                            "clearly covers this required "
                            "component."
                        )
                    )
                ),
            )
        )

    return assessments

def assess_report_components(
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    required_components: list[ReportComponent],
) -> list[ReportComponentAssessment]:
    return assess_report_component_coverage(
        writer_output=writer_output,
        fact_ledger=fact_ledger,
        evidence=evidence,
        required_components=required_components,
    )


def assess_genre_quality(
    writer_output: WriterOutput,
    report_specification: Any,
    evidence: EvidenceLedger,
) -> GenreQualityAssessment:
    event_report = report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }
    realisation_policy = getattr(
        report_specification,
        "realisation_policy",
        None,
    )
    realisation_policy_value = (
        realisation_policy.value
        if isinstance(realisation_policy, RealisationPolicy)
        else str(realisation_policy)
    )
    reference_recap_style = bool(
        event_report
        and (
            getattr(report_specification, "focus_scope", None)
            == "reference_recap"
            or realisation_policy_value
            == RealisationPolicy.EVENT_RECAP_STYLE.value
        )
    )
    evidence_lookup = {
        item.evidence_id: item
        for item in evidence.items
        if item.eligible_for_writer
    }
    actionable_sequence_evidence_ids = {
        evidence_id
        for evidence_id, item in evidence_lookup.items()
        if event_sequence_evidence_is_actionable(item)
    }
    used_evidence_ids = {
        evidence_id
        for support in writer_output.sentence_support
        for evidence_id in support.evidence_ids
    }

    def matching_evidence(slot: str) -> set[str]:
        matches: set[str] = set()
        for evidence_id, item in evidence_lookup.items():
            if (
                slot in {"focused_table_region", "focused_cell_context"}
                and item.capability == EvidenceCapability.FOCUSED_TABLE_REGION
            ):
                matches.add(evidence_id)
            elif (
                slot == "structured_record_verbalisation"
                and item.capability
                == EvidenceCapability.STRUCTURED_RECORD_VERBALISATION
            ):
                matches.add(evidence_id)
            elif slot == "event_result" and item.evidence_type == "event_outcome":
                matches.add(evidence_id)
            elif slot == "leading_performance" and item.capability in {
                EvidenceCapability.ENTITY_PERFORMANCE,
                EvidenceCapability.RANKING,
            } and evidence_analytical_function(item) != (
                AnalyticalFunction.PARTICIPATION
            ) and not event_evidence_is_segment_ranking(item):
                matches.add(evidence_id)
            elif slot == "main_contrast" and item.evidence_type in {
                "participant_comparison",
                "event_contrast",
                "group_comparison",
            }:
                matches.add(evidence_id)
            elif slot == "event_context" and item.evidence_type == ("event_context"):
                matches.add(evidence_id)
            elif slot == "event_status" and item.evidence_type == "event_status":
                matches.add(evidence_id)
            elif (
                slot == "participant_record_context"
                and item.evidence_type == "participant_record_context"
            ):
                matches.add(evidence_id)
            elif (
                slot == "score_progression"
                and item.evidence_type == "score_progression"
            ):
                matches.add(evidence_id)
            elif (
                slot == "event_sequence"
                and item.evidence_type == "event_sequence"
            ):
                if (
                    actionable_sequence_evidence_ids
                    and evidence_id not in actionable_sequence_evidence_ids
                ):
                    continue
                matches.add(evidence_id)
            elif slot == "secondary_performance" and item.capability == (
                EvidenceCapability.RANKING
            ) and not event_evidence_is_segment_ranking(item):
                matches.add(evidence_id)
            elif slot == "dataset_scope" and item.evidence_type in {
                "dataset_overview",
                "event_record_overview",
            }:
                matches.add(evidence_id)
            elif slot == "material_data_quality_issue" and evidence_subtype(item) == (
                "data_quality"
            ):
                matches.add(evidence_id)
            elif slot == "strongest_analytical_finding" and item.capability in {
                EvidenceCapability.ASSOCIATION,
                EvidenceCapability.GROUP_COMPARISON,
                EvidenceCapability.EVENT_OUTCOME,
            }:
                matches.add(evidence_id)
        return matches

    required_slots = list(report_specification.required_content_slots)
    supported_slots: list[str] = []
    covered_slots: list[str] = []

    for slot in [
        *required_slots,
        *report_specification.optional_content_slots,
    ]:
        matching = matching_evidence(slot)
        if matching:
            supported_slots.append(slot)
        if matching & used_evidence_ids:
            covered_slots.append(slot)

    if "limitation" in required_slots:
        supported_slots.append("limitation")
        if re.search(
            r"\b(limitations?|caveats?|does not|cannot|uncertain|missing)\b",
            writer_output.markdown,
            re.IGNORECASE,
        ):
            covered_slots.append("limitation")

    supported_slot_set = set(supported_slots)
    event_material_available = event_report and {
        "event_result",
        "leading_performance",
        "main_contrast",
    }.issubset(supported_slot_set)

    visible_scope_limitation_required = (
        event_material_available
        and not reference_recap_style
    )

    if visible_scope_limitation_required:
        supported_slots.append("scope_limitations")
        if event_scope_limitation_present(writer_output):
            covered_slots.append("scope_limitations")

    missing = [
        slot
        for slot in required_slots
        if slot in supported_slots and slot not in covered_slots
    ]
    findings = [
        f"Required supported content slot `{slot}` is missing from the report."
        for slot in missing
    ]
    recommendations = [
        "Use the available verified evidence to cover each missing content slot."
    ] if missing else []

    if event_report and re.search(
        r"\b(rows?|columns?|constant columns?|missingness|schema|"
        r"correlations?|regressions?|statistical modelling|statistical modeling|"
        r"predictive modelling|predictive modeling|statistical power|"
        r"feature sets?|observed associations?|"
        r"group comparisons? (?:are|is) unadjusted)\b",
        writer_output.markdown,
        re.IGNORECASE,
    ):
        findings.append(
            "The event report includes flat-table profiling or modelling "
            "discussion that displaces the supported event narrative."
        )
        recommendations.append(
            "Remove wrapper-level profiling and modelling discussion; use the "
            "supported event context, performances and participant contrasts."
        )

    if (
        event_report
        and (
            actionable_sequence_evidence_ids
            or any(
                item.evidence_type == "event_sequence"
                for item in evidence_lookup.values()
            )
        )
        and (
            EVENT_SEQUENCE_ABSENCE_PATTERN.search(writer_output.markdown)
            or EVENT_SEQUENCE_OMISSION_PATTERN.search(writer_output.markdown)
        )
    ):
        findings.append(
            "The event report omits or disclaims event-sequence narration "
            "even though supported event-sequence evidence is available."
        )
        recommendations.append(
            "Use the supported event-sequence evidence without inferring "
            "unsupported causes, momentum or turning points."
        )

    if event_material_available:
        narrative_stats = sentence_support_narrative_stats(
            writer_output.sentence_support
        )
        if narrative_stats["synthesis_sentences"] < 2:
            findings.append(
                "The event report lists supported facts without enough "
                "multi-fact or insight-backed narrative synthesis."
            )
            recommendations.append(
                "Relate the supported result, performances and participant "
                "contrasts in connected event prose."
            )
        if narrative_stats["connective_sentences"] < 1:
            findings.append(
                "The event report does not clearly connect supported "
                "participant contrasts into a narrative comparison."
            )
            recommendations.append(
                "Use bounded connective wording such as while, compared with "
                "or despite when the verified facts support a contrast."
            )
        if (
            visible_scope_limitation_required
            and narrative_stats["scope_limitation_sentences"] < 1
        ):
            findings.append(
                "The event report omits an event-scoped limitation."
            )
            recommendations.append(
                "Add a short caveat that the comparisons describe only the "
                "supplied event and do not explain why the result occurred."
            )

    if event_report and not participation_measure_requested(
        " ".join(
            [
                report_specification.report_purpose,
                report_specification.communication_goal,
            ]
        )
    ):
        available_substantive = {
            evidence_id
            for evidence_id, item in evidence_lookup.items()
            if item.evidence_type
            in {
                "entity_ranking",
                "entity_performance",
            }
            and evidence_analytical_function(item)
            != AnalyticalFunction.PARTICIPATION
            and not event_evidence_is_segment_ranking(item)
        }
        used_participation = {
            evidence_id
            for evidence_id, item in evidence_lookup.items()
            if evidence_id in used_evidence_ids
            and item.evidence_type
            in {
                "entity_ranking",
                "entity_performance",
            }
            and evidence_analytical_function(item)
            == AnalyticalFunction.PARTICIPATION
        }
        omitted_substantive = (
            available_substantive - used_evidence_ids
        )

        if used_participation and omitted_substantive:
            findings.append(
                "The event report uses participation evidence while available "
                "substantive entity-performance evidence is omitted."
            )
            recommendations.append(
                "Prioritise distinct substantive performances over duration or "
                "exposure unless participation was explicitly requested."
            )

    return GenreQualityAssessment(
        status=(QualityStatus.REVISE if findings else QualityStatus.PASS),
        genre=report_specification.genre,
        required_slots=required_slots,
        supported_slots=list(dict.fromkeys(supported_slots)),
        covered_slots=list(dict.fromkeys(covered_slots)),
        missing_supported_slots=missing,
        findings=findings,
        recommendations=recommendations,
    )


REPAIR_DRIVING_ERROR_TYPES = {
    ErrorType.INCORRECT_NAMED_ENTITY,
    ErrorType.INCORRECT_NUMBER,
    ErrorType.INCORRECT_WORD,
    ErrorType.CONTEXT_ERROR,
    ErrorType.SUPPORT_MAPPING_ERROR,
}


def annotation_requires_repair(
    annotation: AuditAnnotation,
) -> bool:
    return (
        annotation.error_type in REPAIR_DRIVING_ERROR_TYPES
        and annotation.severity
        in {
            Severity.MEDIUM,
            Severity.HIGH,
            Severity.CRITICAL,
        }
        and annotation.confidence >= 0.80
        and bool(annotation.correction_goal.strip())
    )


def decide_release_status(
    *,
    annotations: list[AuditAnnotation],
    quality: ReportQualityAssessment,
    methodological_warnings: list[str],
    repair_budget_exhausted: bool,
    audit_mode: AuditMode,
) -> ReleaseStatus:
    if audit_mode == AuditMode.ANNOTATION_ONLY:
        if (
            annotations
            or methodological_warnings
            or quality.status != QualityStatus.PASS
        ):
            return ReleaseStatus.APPROVED_WITH_WARNINGS

        return ReleaseStatus.APPROVED

    unresolved_critical = any(
        annotation.severity == Severity.CRITICAL
        and annotation.confidence >= 0.80
        for annotation in annotations
    )
    unresolved_high = any(
        annotation.severity == Severity.HIGH
        and annotation.confidence >= 0.80
        for annotation in annotations
    )
    unresolved_repairable = any(
        annotation_requires_repair(annotation)
        for annotation in annotations
    )

    if unresolved_critical:
        return ReleaseStatus.HUMAN_REVIEW_REQUIRED

    if (
        repair_budget_exhausted
        and (unresolved_high or unresolved_repairable)
    ):
        return ReleaseStatus.HUMAN_REVIEW_REQUIRED

    if (
        annotations
        or methodological_warnings
        or quality.status != QualityStatus.PASS
    ):
        return ReleaseStatus.APPROVED_WITH_WARNINGS

    return ReleaseStatus.APPROVED


def add_annotation(
    annotations: list[AuditAnnotation],
    *,
    sentence: str,
    text_span: str,
    error_type: ErrorType,
    subtype: str,
    severity: Severity,
    explanation: str,
    correction_goal: str,
    fact_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    profile_support_ids: list[str] | None = None,
    insight_ids: list[str] | None = None,
    confidence: float = 1.0,
) -> None:
    key = (
        sentence,
        text_span,
        error_type.value,
        subtype,
    )

    if any(
        (
            annotation.sentence,
            annotation.text_span,
            annotation.error_type.value,
            annotation.subtype,
        )
        == key
        for annotation in annotations
    ):
        return

    annotations.append(
        AuditAnnotation(
            annotation_id=f"ANN_{len(annotations) + 1:04d}",
            sentence=sentence,
            text_span=text_span,
            error_type=error_type,
            subtype=subtype,
            severity=severity,
            explanation=explanation,
            correction_goal=correction_goal,
            fact_ids=fact_ids or [],
            evidence_ids=evidence_ids or [],
            profile_support_ids=profile_support_ids or [],
            insight_ids=insight_ids or [],
            confidence=confidence,
        )
    )


def negative_causal(sentence: str) -> bool:
    return bool(
        re.search(
            r"\b(no causal|not causal|does not establish causation|"
            r"causality is not established|causal conclusion is not|"
            r"do(?:es)? not explain why|cannot explain why|"
            r"do(?:es)? not establish why|"
            r"without explaining why)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def _normalised_text_contains(
    haystack: str,
    needle: Any,
) -> bool:
    needle_text = str(needle or "").strip()
    if not needle_text:
        return False

    return needle_text.casefold() in haystack.casefold()


def _highlight_describes_tied_score(
    highlight: Mapping[str, Any],
) -> bool:
    left_value = highlight.get("left_value")
    right_value = highlight.get("right_value")
    if isinstance(left_value, (int, float)) and isinstance(
        right_value,
        (int, float),
    ):
        return float(left_value) == float(right_value)

    score_phrase = str(highlight.get("score_phrase") or "")
    return bool(
        re.search(
            r"\b(?:level|tie[sd]?)\b",
            score_phrase,
            re.IGNORECASE,
        )
    )


def _highlight_referenced_by_sentence(
    sentence: str,
    highlight: Mapping[str, Any],
) -> bool:
    event_text = str(highlight.get("event_text") or "")
    actor = event_text.split(" recorded ", 1)[0]
    actor = re.sub(
        r"^.*?:\s*",
        "",
        actor,
    ).strip()
    score_phrase = str(highlight.get("score_phrase") or "")

    return any(
        _normalised_text_contains(sentence, value)
        for value in [
            actor,
            score_phrase,
            f"{highlight.get('left_value'):g}-{highlight.get('right_value'):g}"
            if isinstance(highlight.get("left_value"), (int, float))
            and isinstance(highlight.get("right_value"), (int, float))
            else None,
        ]
    )


def score_state_tie_claim_supported(
    sentence: str,
    evidence_items: Sequence[EvidenceItem],
) -> bool:
    if not SCORE_STATE_TIE_CLAIM_PATTERN.search(sentence):
        return True
    if NEGATED_SCORE_STATE_TIE_PATTERN.search(sentence):
        return True

    sequence_items = [
        item
        for item in evidence_items
        if item.evidence_type == "event_sequence"
    ]
    if not sequence_items:
        return False

    for item in sequence_items:
        highlights = item.metrics.get("highlights", [])
        if not isinstance(highlights, list):
            continue

        for highlight in highlights:
            if not isinstance(highlight, Mapping):
                continue
            if not _highlight_describes_tied_score(highlight):
                continue
            if _highlight_referenced_by_sentence(sentence, highlight):
                return True

    return False


def negative_predictive(sentence: str) -> bool:
    return bool(
        re.search(
            r"\b(not validated|did not improve|no predictive|"
            r"cannot support prediction|not deployment ready)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def negative_forecast(sentence: str) -> bool:
    return bool(
        re.search(
            r"\b(not validated|did not improve|no forecast|"
            r"did not outperform|not a live future forecast)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def _support_text_for_facts(
    facts: list[VerifiedFact],
    evidence: EvidenceLedger,
) -> str:
    return " ".join(
        fact_support_text(fact, evidence)
        for fact in facts
    ).lower()


def _mapped_facts_semantically_support_profile_match(
    *,
    support_text: str,
    matches: list[ProfileSupportRecord],
) -> bool:
    for record in matches:
        pattern = PROFILE_FACT_KIND_TERMS.get(
            record.fact_kind
        )
        if (
            pattern is not None
            and pattern.search(support_text)
        ):
            return True

    return False


def _recommendation_supported_by_evidence(
    sentence: str,
    facts: list[VerifiedFact],
    evidence_lookup_by_id: dict[str, EvidenceItem],
) -> bool:
    sentence_text = sentence.lower()

    for fact in facts:
        for item in evidence_for_fact(
            fact,
            evidence_lookup_by_id,
        ):
            for recommendation in item.recommendations:
                action = recommendation.action.lower()
                if action and (
                    action in sentence_text
                    or sentence_text in action
                ):
                    return True

    return False


def add_wording_guardrail_annotations(
    *,
    annotations: list[AuditAnnotation],
    sentence: str,
    support: SentenceSupport,
    supporting_facts: list[VerifiedFact],
    evidence: EvidenceLedger,
    report_specification: Any,
) -> None:
    support_text = _support_text_for_facts(
        supporting_facts,
        evidence,
    )
    evidence_lookup_by_id = build_evidence_lookup(evidence)
    request_text = (
        getattr(
            report_specification,
            "report_purpose",
            "",
        )
        or ""
    ).lower()

    hourly_match = HOURLY_CADENCE_PATTERN.search(sentence)
    if hourly_match and not HOURLY_CADENCE_PATTERN.search(support_text):
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=hourly_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_temporal_cadence",
            severity=Severity.HIGH,
            explanation=(
                "A date/time-like field or parse rate does not establish "
                "regular hourly spacing."
            ),
            correction_goal=(
                "Use neutral wording such as timestamped weather observations."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    location_match = LOCATION_METADATA_PATTERN.search(sentence)
    if location_match and not LOCATION_METADATA_PATTERN.search(support_text):
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=location_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_location_metadata",
            severity=Severity.HIGH,
            explanation=(
                "The supplied facts do not establish collection at a "
                "specific location or weather station."
            ),
            correction_goal="Remove unsupported location metadata.",
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    constant_match = CONSTANT_OVERSTATEMENT_PATTERN.search(sentence)
    if constant_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=constant_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="overbroad_constant_interpretation",
            severity=Severity.HIGH,
            explanation=(
                "A constant field should not be described as universally "
                "worthless or valueless."
            ),
            correction_goal=(
                "Say it contains no observed variation for analyses that "
                "depend on variation."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    zero_match = ZERO_OVERCONFIDENCE_PATTERN.search(sentence)
    if zero_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=zero_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="overconfident_zero_interpretation",
            severity=Severity.HIGH,
            explanation=(
                "Suspicious zero diagnostics do not establish what the zero "
                "values actually mean."
            ),
            correction_goal=(
                "Use cautious wording such as may represent encoded "
                "missingness or measurement failure and should be validated."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    missingness_match = MISSINGNESS_HARMLESS_PATTERN.search(sentence)
    if missingness_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=missingness_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_missingness_impact",
            severity=Severity.HIGH,
            explanation=(
                "A missingness rate alone does not establish that the "
                "missingness is harmless."
            ),
            correction_goal=(
                "Report the rate and recommend examining the missingness "
                "pattern."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    duplicate_match = DUPLICATE_REMOVAL_PATTERN.search(sentence)
    if duplicate_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=duplicate_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="unsupported_duplicate_removal",
            severity=Severity.HIGH,
            explanation=(
                "Exact duplicate rows may be valid repeated observations or "
                "unintended duplicates."
            ),
            correction_goal=(
                "Say duplicate rows should be reviewed before any decision "
                "to remove them."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
        )

    pearson_match = PEARSON_IMPRECISE_PATTERN.search(sentence)
    if pearson_match:
        add_annotation(
            annotations,
            sentence=sentence,
            text_span=pearson_match.group(0),
            error_type=ErrorType.CONTEXT_ERROR,
            subtype="imprecise_pearson_limitation",
            severity=Severity.MEDIUM,
            explanation=(
                "Pearson correlation may not capture non-linear relationships; "
                "it is not literally influenced by a pattern it does not measure."
            ),
            correction_goal=(
                "Say Pearson correlation may not capture non-linear "
                "relationships and can be sensitive to influential observations."
            ),
            fact_ids=support.fact_ids,
            evidence_ids=support.evidence_ids,
            profile_support_ids=support.profile_support_ids,
            confidence=0.9,
        )

    future_match = FUTURE_ANALYSIS_PATTERN.search(sentence)
    if future_match:
        requested = bool(
            re.search(
                r"\b(model|modelling|modeling|temporal|trend|future|"
                r"relationship|multivariate)\b",
                request_text,
            )
        )
        supported_recommendation = (
            _recommendation_supported_by_evidence(
                sentence,
                supporting_facts,
                evidence_lookup_by_id,
            )
        )

        if not requested and not supported_recommendation:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=future_match.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="unsupported_analytical_recommendation",
                severity=Severity.MEDIUM,
                explanation=(
                    "Reader-facing next steps must come from supplied "
                    "recommendations, verified methodological facts, or the "
                    "explicit user request."
                ),
                correction_goal=(
                    "Remove the unsupported recommendation or ground it in a "
                    "supplied analytical recommendation."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                profile_support_ids=support.profile_support_ids,
                confidence=0.9,
            )


def deterministic_audit(
    writer_output: WriterOutput,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    mode: AuditMode,
    external_sources: list[ExternalTruthSource],
    revision_round: int,
    report_specification: Any,
    settings: Settings | None = None,
    profile_support_records: list[
        ProfileSupportRecord
    ] | None = None,
    insight_ledger: InsightLedger | None = None,
) -> AuditReport:
    settings = settings or Settings()
    profile_support_records = profile_support_records or []
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    profile_records_by_id = {
        record.support_id: record
        for record in profile_support_records
    }
    facts = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insight_ids = {
        *verified_insights,
        *hypothesis_insights,
    }

    support_by_sentence = {
        support.sentence_text: support
        for support in writer_output.sentence_support
    }

    annotations: list[AuditAnnotation] = []
    support_map_patches: list[SupportMapPatch] = []
    sentences = split_markdown_sentences(writer_output.markdown)
    section_headings = _sentence_section_headings(
        writer_output.markdown
    )
    evidence_lookup_by_id = build_evidence_lookup(evidence)

    factual_count = 0
    supported_count = 0

    for sentence in sentences:
        support = support_by_sentence.get(sentence)

        if (
            not looks_factual(sentence)
            and not (
                support is not None
                and support.interpretation_level
                != InterpretationLevel.FINDING
            )
        ):
            continue

        factual_count += 1

        if support is None:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="missing_support_map_entry",
                severity=Severity.HIGH,
                explanation=(
                    "The sentence appears factual but is absent from the hidden "
                    "sentence support map."
                ),
                correction_goal=(
                    "Attach relevant verified facts or remove unsupported factual content."
                ),
            )
            continue

        unknown_fact_ids = [
            fact_id
            for fact_id in support.fact_ids
            if fact_id not in facts
        ]

        if unknown_fact_ids:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="unknown_fact_id",
                severity=Severity.HIGH,
                explanation=(
                    "The support map references facts not present in the verified ledger."
                ),
                correction_goal="Use valid verified facts.",
                fact_ids=unknown_fact_ids,
            )
            continue

        supporting_facts = [
            facts[fact_id]
            for fact_id in support.fact_ids
        ]

        supporting_evidence_ids = {
            *support.evidence_ids,
            *[
                evidence_id
                for fact in supporting_facts
                for evidence_id in fact.evidence_ids
            ],
        }
        supporting_evidence_items = [
            evidence_lookup_by_id[evidence_id]
            for evidence_id in supporting_evidence_ids
            if evidence_id in evidence_lookup_by_id
        ]
        if not score_state_tie_claim_supported(
            sentence,
            supporting_evidence_items,
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="unsupported_event_score_state",
                severity=Severity.HIGH,
                explanation=(
                    "The sentence uses tying or score-level wording without "
                    "mapped event-sequence evidence showing that the referenced "
                    "event left the score tied."
                ),
                correction_goal=(
                    "Remove the tying wording or map the sentence to exact "
                    "event-sequence evidence whose score state supports it."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=sorted(supporting_evidence_ids),
                insight_ids=support.insight_ids,
                confidence=0.95,
            )

        for conflict in qualitative_strength_conflicts(
            sentence,
            supporting_evidence_items,
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="inconsistent_strength_label",
                severity=Severity.HIGH,
                explanation=(
                    "The qualitative relationship strength conflicts with "
                    f"the mapped deterministic evidence: {conflict}."
                ),
                correction_goal=(
                    "Use the qualitative strength classification recorded in "
                    "the mapped evidence."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=sorted(supporting_evidence_ids),
                insight_ids=support.insight_ids,
            )

        explanatory_hypothesis = (
            EXPLANATORY_HYPOTHESIS_PATTERN.search(sentence)
            or UNLABELLED_HYPOTHESIS_PATTERN.search(sentence)
        )
        if (
            explanatory_hypothesis
            and support.interpretation_level
            != InterpretationLevel.HYPOTHESIS
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=explanatory_hypothesis.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="unlabelled_hypothesis",
                severity=Severity.HIGH,
                explanation=(
                    "The sentence proposes a possible explanation without "
                    "verified hypothesis provenance."
                ),
                correction_goal=(
                    "Remove the explanation or present it as an explicitly "
                    "labelled hypothesis in the permitted section when enabled."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        unknown_insight_ids = [
            insight_id
            for insight_id in support.insight_ids
            if insight_id not in all_insight_ids
        ]
        if unknown_insight_ids:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="unsupported_insight",
                severity=Severity.HIGH,
                explanation=(
                    "The support map references insight IDs that are absent "
                    "from the verified Insight Ledger."
                ),
                correction_goal=(
                    "Remove the unsupported interpretation or map it to an "
                    "existing verified insight."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=unknown_insight_ids,
            )

        mapped_verified_insights = [
            verified_insights[insight_id]
            for insight_id in support.insight_ids
            if insight_id in verified_insights
        ]
        mapped_hypotheses = [
            hypothesis_insights[insight_id]
            for insight_id in support.insight_ids
            if insight_id in hypothesis_insights
        ]

        if (
            support.interpretation_level
            == InterpretationLevel.BOUNDED_INSIGHT
        ):
            if not support.insight_ids:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.NOT_CHECKABLE,
                    subtype="unsupported_insight",
                    severity=Severity.HIGH,
                    explanation=(
                        "The sentence presents a bounded interpretation but "
                        "has no verified insight provenance."
                    ),
                    correction_goal=(
                        "Map the sentence to an exact verified insight or "
                        "rewrite it as directly supported findings."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                )
            elif len(mapped_verified_insights) != len(
                support.insight_ids
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="unsupported_insight",
                    severity=Severity.HIGH,
                    explanation=(
                        "A bounded-insight sentence may cite only insights "
                        "verified for the main report."
                    ),
                    correction_goal=(
                        "Use a verified main insight or remove the "
                        "interpretive claim."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

            required_fact_ids = {
                fact_id
                for insight in mapped_verified_insights
                for fact_id in insight.source_fact_ids
            }
            required_evidence_ids = {
                evidence_id
                for insight in mapped_verified_insights
                for evidence_id in insight.source_evidence_ids
            }
            if (
                mapped_verified_insights
                and (
                    not required_fact_ids.issubset(
                        set(support.fact_ids)
                    )
                    or not required_evidence_ids.issubset(
                        set(support.evidence_ids)
                    )
                )
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                    subtype="insight_missing_source_support",
                    severity=Severity.HIGH,
                    explanation=(
                        "The bounded insight is mapped without all of its "
                        "verified source facts and evidence."
                    ),
                    correction_goal=(
                        "Restore the verified insight's source fact and "
                        "evidence provenance in the hidden support map."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

            overstatement = INSIGHT_OVERSTATEMENT_PATTERN.search(sentence)
            if overstatement:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=overstatement.group(0),
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="insight_exceeds_verified_wording",
                    severity=Severity.HIGH,
                    explanation=(
                        "The report wording is stronger than the bounded "
                        "interpretation authorised by the Insight Ledger."
                    ),
                    correction_goal=(
                        "Use the verified dataset-scoped insight wording."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

        if (
            support.interpretation_level
            == InterpretationLevel.HYPOTHESIS
        ):
            if not settings.allow_hypotheses_in_report:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="hypothesis_presented_as_conclusion",
                    severity=Severity.HIGH,
                    explanation=(
                        "Hypotheses are disabled for this report."
                    ),
                    correction_goal="Remove the hypothesis from the report.",
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
            if not mapped_hypotheses or len(mapped_hypotheses) != len(
                support.insight_ids
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.NOT_CHECKABLE,
                    subtype="unlabelled_hypothesis",
                    severity=Severity.HIGH,
                    explanation=(
                        "The sentence lacks valid hypothesis-only provenance."
                    ),
                    correction_goal=(
                        "Map it to a hypothesis-only ledger entry or remove it."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
            if (
                not HYPOTHESIS_WORDING_PATTERN.search(sentence)
                and not sentence.strip().endswith("?")
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="unlabelled_hypothesis",
                    severity=Severity.HIGH,
                    explanation=(
                        "A hypothesis must be explicitly labelled rather than "
                        "presented as established knowledge."
                    ),
                    correction_goal="Label the statement explicitly as a hypothesis.",
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
            if section_headings.get(sentence, "").lower() != (
                "questions for further investigation"
            ):
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="hypothesis_presented_as_conclusion",
                    severity=Severity.HIGH,
                    explanation=(
                        "Hypotheses may appear only in the separate Questions "
                        "for Further Investigation section."
                    ),
                    correction_goal=(
                        "Move the labelled hypothesis to the permitted section."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )

        if (
            support.interpretation_level
            == InterpretationLevel.FINDING
        ):
            if support.insight_ids:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                    subtype="single_fact_relabelled_as_insight",
                    severity=Severity.MEDIUM,
                    explanation=(
                        "A direct finding is incorrectly mapped as an insight."
                    ),
                    correction_goal=(
                        "Remove the insight mapping or mark a genuinely "
                        "verified bounded interpretation."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    insight_ids=support.insight_ids,
                )
        unknown_profile_ids = [
            support_id
            for support_id in support.profile_support_ids
            if support_id not in profile_records_by_id
        ]

        if unknown_profile_ids:
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.NOT_CHECKABLE,
                subtype="unknown_profile_support_id",
                severity=Severity.HIGH,
                explanation=(
                    "The support map references deterministic profile support "
                    "not present in the profile registry."
                ),
                correction_goal="Use valid deterministic profile support IDs.",
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                profile_support_ids=unknown_profile_ids,
            )
            continue

        attached_profile_supports = _profile_records_support_sentence(
            sentence=sentence,
            support_ids=support.profile_support_ids,
            records_by_id=profile_records_by_id,
        )

        fact_numbers = [
            number
            for fact in supporting_facts
            for number in fact_support_numbers(fact, evidence)
        ]

        attached_profile_numbers = [
            number
            for support_id in support.profile_support_ids
            if support_id in profile_records_by_id
            for number in profile_record_numbers(
                profile_records_by_id[support_id]
            )
        ]

        combined_numbers = [
            *fact_numbers,
            *(
                attached_profile_numbers
                if attached_profile_supports
                else []
            ),
        ]

        profile_matches = matching_profile_support_records(
            sentence=sentence,
            records=profile_support_records,
        )

        if not numbers_supported(sentence, combined_numbers):
            if profile_matches:
                matched_ids = [
                    record.support_id
                    for record in profile_matches
                ]
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                    subtype=(
                        "deterministic_profile_support_missing_from_map"
                    ),
                    severity=Severity.MEDIUM,
                    explanation=(
                        "The visible statement is supported by deterministic "
                        "profile data, but that support is missing from the "
                        "hidden sentence support map."
                    ),
                    correction_goal=(
                        "Attach the relevant deterministic profile support "
                        "IDs to the hidden sentence support map."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    profile_support_ids=matched_ids,
                    confidence=1.0,
                )
                support_map_patches.append(
                    SupportMapPatch(
                        sentence_id=support.sentence_id,
                        sentence_text=support.sentence_text,
                        added_profile_support_ids=matched_ids,
                        reason=(
                            "Deterministic profile data exactly supports "
                            "the visible structural statement."
                        ),
                    )
                )
            else:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.INCORRECT_NUMBER,
                    subtype="unsupported_number",
                    severity=Severity.HIGH,
                    explanation=(
                        "One or more numbers are not supported by the mapped "
                        "verified facts or deterministic profile support."
                    ),
                    correction_goal=(
                        "Use a supported exact or appropriately qualified "
                        "rounded value."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    profile_support_ids=support.profile_support_ids,
                )
        elif (
            profile_matches
            and not attached_profile_supports
            and not _mapped_facts_semantically_support_profile_match(
                support_text=_support_text_for_facts(
                    supporting_facts,
                    evidence,
                ),
                matches=profile_matches,
            )
        ):
            matched_ids = [
                record.support_id
                for record in profile_matches
            ]
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.SUPPORT_MAPPING_ERROR,
                subtype="deterministic_profile_support_missing_from_map",
                severity=Severity.MEDIUM,
                explanation=(
                    "The visible structural statement is supported by "
                    "deterministic profile data, but the mapped verified facts "
                    "do not provide that provenance."
                ),
                correction_goal=(
                    "Attach the relevant deterministic profile support IDs "
                    "to the hidden sentence support map."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                profile_support_ids=matched_ids,
                confidence=1.0,
            )
            support_map_patches.append(
                SupportMapPatch(
                    sentence_id=support.sentence_id,
                    sentence_text=support.sentence_text,
                    added_profile_support_ids=matched_ids,
                    reason=(
                        "Deterministic profile data exactly supports the "
                        "visible structural statement."
                    ),
                )
            )

        permissions = {
            permission
            for fact in supporting_facts
            for permission in fact.claim_permissions
        }
        mapped_interpretations = [
            *mapped_verified_insights,
            *mapped_hypotheses,
        ]
        mapped_insight_text = " ".join(
            insight.statement
            for insight in mapped_interpretations
        )

        if IMBALANCE_BIAS_PATTERN.search(sentence):
            support_text = " ".join(
                [
                    sentence,
                    *[fact.fact_summary for fact in supporting_facts],
                    *[
                        item.practical_interpretation
                        for fact in supporting_facts
                        for item in evidence_for_fact(
                            fact,
                            evidence_lookup_by_id,
                        )
                    ],
                    *[
                        limitation
                        for fact in supporting_facts
                        for item in evidence_for_fact(
                            fact,
                            evidence_lookup_by_id,
                        )
                        for limitation in getattr(item, "limitations", [])
                    ],
                ]
            ).lower()

            if "sampling bias" not in support_text and "selection bias" not in support_text:
                add_annotation(
                    annotations,
                    sentence=sentence,
                    text_span=sentence,
                    error_type=ErrorType.CONTEXT_ERROR,
                    subtype="unsupported_methodological_interpretation",
                    severity=Severity.MEDIUM,
                    explanation=(
                        "The evidence can support noting that unequal group sizes "
                        "may affect precision, stability, or representation, but it "
                        "does not establish that the reported means are biased."
                    ),
                    correction_goal=(
                        "Replace bias wording with a precision, stability, or "
                        "representation caveat grounded in the evidence."
                    ),
                    fact_ids=support.fact_ids,
                    evidence_ids=support.evidence_ids,
                    confidence=0.85,
                )

        if (
            CAUSAL_PATTERN.search(sentence)
            and not negative_causal(sentence)
            and (
                ClaimPermission.CAUSAL not in permissions
                or (
                    support.interpretation_level
                    != InterpretationLevel.FINDING
                    and not CAUSAL_PATTERN.search(
                        mapped_insight_text
                    )
                )
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype=(
                    "unsupported_causal_interpretation"
                    if support.interpretation_level
                    != InterpretationLevel.FINDING
                    else "causal_overclaim"
                ),
                severity=Severity.CRITICAL,
                explanation=(
                    "The sentence uses causal language without verified causal permission."
                ),
                correction_goal=(
                    "Rewrite as association or explicitly state that causality "
                    "was not established."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        if (
            PREDICTIVE_PATTERN.search(sentence)
            and not negative_predictive(sentence)
            and (
                ClaimPermission.PREDICTIVE not in permissions
                or (
                    support.interpretation_level
                    != InterpretationLevel.FINDING
                    and not PREDICTIVE_PATTERN.search(
                        mapped_insight_text
                    )
                )
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="predictive_overclaim",
                severity=Severity.HIGH,
                explanation=(
                    "Predictive wording is used without validated predictive permission."
                ),
                correction_goal=(
                    "Describe the feasibility limitation or validated internal result accurately."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        if (
            FORECAST_PATTERN.search(sentence)
            and not negative_forecast(sentence)
            and (
                ClaimPermission.FORECAST not in permissions
                or (
                    support.interpretation_level
                    != InterpretationLevel.FINDING
                    and not FORECAST_PATTERN.search(
                        mapped_insight_text
                    )
                )
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sentence,
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="forecast_overclaim",
                severity=Severity.HIGH,
                explanation=(
                    "Forecast wording is used without validated forecast permission."
                ),
                correction_goal=(
                    "Describe the backtest or insufficiency finding without "
                    "claiming unsupported future performance."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        generalisation_match = DATASET_GENERALISATION_PATTERN.search(
            sentence
        )
        if (
            generalisation_match
            and not DATASET_GENERALISATION_PATTERN.search(
                mapped_insight_text
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=generalisation_match.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="insight_exceeds_verified_wording",
                severity=Severity.HIGH,
                explanation=(
                    "The sentence generalises a dataset-scoped finding or "
                    "insight beyond the analysed data."
                ),
                correction_goal=(
                    "Scope the statement to this dataset and the verified "
                    "interpretation."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        sports_narrative_match = (
            UNSUPPORTED_SPORTS_NARRATIVE_PATTERN.search(
                sentence
            )
        )
        support_text_for_narrative = (
            _support_text_for_facts(
                supporting_facts,
                evidence,
            )
            + " "
            + mapped_insight_text.lower()
        )
        if (
            sports_narrative_match
            and not UNSUPPORTED_SPORTS_NARRATIVE_PATTERN.search(
                support_text_for_narrative
            )
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=sports_narrative_match.group(0),
                error_type=ErrorType.CONTEXT_ERROR,
                subtype="unsupported_sports_narrative",
                severity=Severity.HIGH,
                explanation=(
                    "The sports narrative introduces chronology, evaluation, "
                    "or historical significance absent from verified support."
                ),
                correction_goal=(
                    "Use only the supported result, performances and team "
                    "contrasts without invented narrative context."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
                insight_ids=support.insight_ids,
            )

        add_wording_guardrail_annotations(
            annotations=annotations,
            sentence=sentence,
            support=support,
            supporting_facts=supporting_facts,
            evidence=evidence,
            report_specification=report_specification,
        )

        known_entities = {
            entity
            for fact in supporting_facts
            for entity in fact.entities
        }
        known_entities.update(
            entity
            for support_id in support.profile_support_ids
            if support_id in profile_records_by_id
            for entity in profile_records_by_id[
                support_id
            ].entities
        )

        for backtick_entity in unsupported_backtick_entities(
            sentence,
            known_entities,
        ):
            add_annotation(
                annotations,
                sentence=sentence,
                text_span=backtick_entity,
                error_type=ErrorType.INCORRECT_NAMED_ENTITY,
                subtype="unsupported_backtick_entity",
                severity=Severity.HIGH,
                explanation=(
                    "The named entity is not present in the mapped facts."
                ),
                correction_goal=(
                    "Use an entity present in the verified facts or remove it."
                ),
                fact_ids=support.fact_ids,
                evidence_ids=support.evidence_ids,
            )

        if not any(
            annotation.sentence == sentence
            for annotation in annotations
        ):
            supported_count += 1

    word_count = len(
        re.findall(r"\b[\w'-]+\b", writer_output.markdown)
    )

    quality_findings: list[str] = []
    quality_recommendations: list[str] = []
    methodological_warnings: list[str] = []

    if INTERNAL_CONTROL_PATTERN.search(writer_output.markdown) or FIELD_LABEL_PATTERN.search(
        writer_output.markdown
    ):
        quality_findings.append(
            "The report exposes internal writer or auditor guardrails."
        )
        quality_recommendations.append(
            "Convert internal constraints into concise reader-facing caveats."
        )

    if any(pattern.search(writer_output.markdown) for pattern in GENERIC_OPENING_PATTERNS):
        quality_findings.append(
            "The report opens with generic report boilerplate instead of dataset-specific substance."
        )
        quality_recommendations.append(
            "Start with a concrete dataset overview or leading supported finding."
        )

    maximum_words = report_specification.maximum_length_words
    if maximum_words is not None and word_count > maximum_words:
        quality_findings.append(
            f"The report contains {word_count} words and exceeds the "
            f"{maximum_words}-word ceiling."
        )
        quality_recommendations.append(
            "Remove low-priority detail and consolidate methodological caveats."
        )

    minimum_words = minimum_useful_report_words(
        target_words=report_specification.target_length_words,
        required_component_count=len(report_specification.required_components),
        settings=settings,
    )
    if word_count < minimum_words:
        quality_findings.append(
            f"The report contains {word_count} words, below the minimum useful "
            f"coverage threshold of {minimum_words}."
        )
        if report_specification.genre in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }:
            coverage_target = (
                "the supported event result, context, leading performances, "
                "participant contrasts, and scope caveats"
            )
        else:
            coverage_target = (
                "the required dataset overview, quality, relationship, and "
                "limitation components"
            )
        quality_recommendations.append(
            f"Expand the report using verified facts covering {coverage_target}."
        )

    content_requirements = build_writer_content_requirements(
        report_specification=report_specification,
        fact_ledger=fact_ledger,
        evidence=evidence,
        insight_ledger=insight_ledger,
        settings=settings,
    )
    for content_error in writer_output_content_requirement_errors(
        writer_output=writer_output,
        requirements=content_requirements,
        include_word_count=False,
        respect_validation_severity=False,
    ):
        quality_findings.append(content_error)
        quality_recommendations.append(
            "Use the controller-enforced content requirements to include "
            "the supported event material before adding lower-priority prose."
        )

    configured_fact_limits = [
        limit
        for limit in {
            report_specification.maximum_main_findings,
            report_specification.maximum_supporting_facts,
        }
        if limit is not None
    ]
    if (
        configured_fact_limits
        and len(writer_output.selected_fact_ids)
        > max(configured_fact_limits)
    ):
        quality_findings.append(
            "The report uses more facts than the configured report budget."
        )
        quality_recommendations.append(
            "Prioritise headline findings and omit weaker supporting detail."
        )

    used_verified_insight_ids = {
        insight_id
        for support in writer_output.sentence_support
        if support.interpretation_level
        == InterpretationLevel.BOUNDED_INSIGHT
        for insight_id in support.insight_ids
        if insight_id in verified_insights
    }
    if verified_insights and not used_verified_insight_ids:
        quality_findings.append(
            "The report lists findings without relating them through an "
            "available verified insight."
        )
        quality_recommendations.append(
            "Use at least one salient verified bounded insight in a main "
            "analytical paragraph."
        )

    insights_without_implication = []
    for insight_id in used_verified_insight_ids:
        insight = verified_insights[insight_id]
        if (
            report_specification.genre
            in {
                ReportGenre.EVENT_REPORT,
                ReportGenre.SPORTS_GAME_REPORT,
            }
            or
            insight.contribution
            != InsightContribution.ANALYTICAL_IMPLICATION
        ):
            continue
        mapped_sentences = [
            support.sentence_text
            for support in writer_output.sentence_support
            if insight_id in support.insight_ids
        ]
        direct_source_texts = [
            insight.statement,
            *[
                facts[fact_id].fact_summary
                for fact_id in insight.source_fact_ids
                if fact_id in facts
            ],
        ]
        if mapped_sentences and all(
            any(
                materially_same_report_text(
                    sentence,
                    source_text,
                )
                for source_text in direct_source_texts
            )
            for sentence in mapped_sentences
        ):
            insights_without_implication.append(insight_id)

    if insights_without_implication:
        quality_findings.append(
            "The report states a verified insight but does not explain its "
            "supported analytical implication."
        )
        quality_recommendations.append(
            "Use the verified `why_it_matters` content to explain why the "
            "combined findings matter instead of restating them."
        )

    if verified_insights:
        most_salient_insight = max(
            verified_insights.values(),
            key=lambda insight: (
                insight.salience,
                insight.confidence,
            ),
        )
        if (
            most_salient_insight.insight_id
            not in used_verified_insight_ids
        ):
            quality_findings.append(
                "The report omits the most salient verified insight."
            )
            quality_recommendations.append(
                "Prioritise the most salient verified insight or explain the "
                "selection through stronger supported content."
            )

    if (
        report_specification.genre
        in {
            ReportGenre.EVENT_REPORT,
            ReportGenre.SPORTS_GAME_REPORT,
        }
    ):
        sports_text = writer_output.markdown.lower()
        game_content = re.search(
            r"\b(won|winner|score|points?|rebounds?|turnovers?|team|player)\b",
            sports_text,
        )
        profile_dominant = bool(
            re.search(
                r"\b(columns?|schema|missingness|dtype|data type)\b",
                sports_text,
            )
            and not game_content
        )
        if not game_content or profile_dominant:
            quality_findings.append(
                "The event report reads like a dataset profile rather than "
                "communicating the supported result and performances."
            )
            quality_recommendations.append(
                "Prioritise the supported result, salient performances and "
                "team-level contrasts required by the selected genre."
            )

    if any(
        annotation.subtype
        in {
            "unlabelled_hypothesis",
            "hypothesis_presented_as_conclusion",
        }
        for annotation in annotations
    ):
        quality_findings.append(
            "The report uses a hypothesis as a conclusion."
        )
        quality_recommendations.append(
            "Remove the hypothesis or label it in the permitted further-"
            "investigation section."
        )

    repeated_caveat_count = count_caveat_mentions(writer_output.markdown)

    if repeated_caveat_count > settings.maximum_repeated_caveat_mentions:
        quality_findings.append(
            "The same causal caveat is repeated several times."
        )
        quality_recommendations.append(
            "Consolidate recurring caveats at section level."
        )

    component_assessments = assess_report_component_coverage(
        writer_output=writer_output,
        fact_ledger=fact_ledger,
        evidence=evidence,
        required_components=report_specification.required_components,
    )
    missing_required_components = False
    for assessment in component_assessments:
        if not assessment.covered:
            missing_required_components = True
            quality_findings.append(
                f"Required report component `{assessment.component.value}` is not clearly covered."
            )
            quality_recommendations.append(
                "Revise the report to cover the required component using verified facts."
            )

    fact_text = " ".join(
        fact.fact_summary.lower()
        + " "
        + " ".join(entity.lower() for entity in fact.entities)
        for fact in fact_ledger.writer_ready_facts
    )
    allowed_unit_terms = set()
    if report_specification.genre in {
        ReportGenre.EVENT_REPORT,
        ReportGenre.SPORTS_GAME_REPORT,
    }:
        allowed_unit_terms.update({"event", "events"})

    unsupported_unit_terms = [
        term
        for term in UNSANCTIONED_UNIT_TERMS
        if term not in allowed_unit_terms
        if re.search(rf"\b{re.escape(term)}\b", writer_output.markdown, re.IGNORECASE)
        and term not in fact_text
    ]
    if unsupported_unit_terms:
        quality_findings.append(
            "The report may substitute an unsupported unit of observation: "
            + ", ".join(sorted(set(unsupported_unit_terms)))
            + "."
        )
        quality_recommendations.append(
            "Use neutral unit wording unless verified facts or deterministic "
            "profile support establish a more specific unit."
        )

    for annotation in annotations:
        if annotation.subtype == "unsupported_methodological_interpretation":
            methodological_warnings.append(annotation.explanation)

    quality = ReportQualityAssessment(
        status=(
            QualityStatus.REVISE
            if missing_required_components
            else (
                QualityStatus.WARNING
                if quality_findings
                else QualityStatus.PASS
            )
        ),
        request_responsiveness=0.8 if quality_findings else 1.0,
        finding_selection=0.7 if quality_findings else 1.0,
        coherence=0.9,
        concision=0.7 if quality_findings else 1.0,
        caveat_integration=(
            0.6
            if repeated_caveat_count > settings.maximum_repeated_caveat_mentions
            else 1.0
        ),
        data_science_interpretation=0.9,
        findings=quality_findings,
        recommendations=quality_recommendations,
    )

    serious = any(
        annotation_requires_repair(annotation)
        for annotation in annotations
    )

    if mode == AuditMode.ANNOTATION_ONLY:
        decision = AuditDecision.PASS
    elif serious:
        decision = AuditDecision.REVISE
    else:
        decision = AuditDecision.PASS

    release_status = decide_release_status(
        annotations=annotations,
        quality=quality,
        methodological_warnings=methodological_warnings,
        repair_budget_exhausted=False,
        audit_mode=mode,
    )

    return AuditReport(
        mode=mode,
        decision=decision,
        release_status=release_status,
        annotations=annotations,
        applied_patches=[],
        support_map_patches=support_map_patches,
        factual_sentence_count=factual_count,
        supported_sentence_count=supported_count,
        support_rate=(
            supported_count / factual_count
            if factual_count
            else 1.0
        ),
        residual_risk=(
            "High-confidence factual issues require repair."
            if serious
            else (
                "No high-confidence factual error was detected; "
                "residual writer and auditor error remain possible."
            )
        ),
        revision_instructions=list(
            dict.fromkeys(
                annotation.correction_goal
                for annotation in annotations
            )
        ),
        quality_assessment=quality,
        revision_round=revision_round,
        component_assessments=component_assessments,
        methodological_warnings=methodological_warnings,
    )


def _ordered_dedupe(
    values: list[str],
) -> list[str]:
    return list(
        dict.fromkeys(
            value
            for value in values
            if value
        )
    )


def merge_quality_assessments(
    deterministic: ReportQualityAssessment,
    semantic: ReportQualityAssessment,
) -> ReportQualityAssessment:
    status = max(
        [deterministic.status, semantic.status],
        key=lambda item: QUALITY_STATUS_ORDER[item],
    )

    return ReportQualityAssessment(
        status=status,
        request_responsiveness=min(
            deterministic.request_responsiveness,
            semantic.request_responsiveness,
        ),
        finding_selection=min(
            deterministic.finding_selection,
            semantic.finding_selection,
        ),
        coherence=min(
            deterministic.coherence,
            semantic.coherence,
        ),
        concision=min(
            deterministic.concision,
            semantic.concision,
        ),
        caveat_integration=min(
            deterministic.caveat_integration,
            semantic.caveat_integration,
        ),
        data_science_interpretation=min(
            deterministic.data_science_interpretation,
            semantic.data_science_interpretation,
        ),
        findings=_ordered_dedupe(
            deterministic.findings
            + semantic.findings
        ),
        recommendations=_ordered_dedupe(
            deterministic.recommendations
            + semantic.recommendations
        ),
    )


def merge_audit_proposal(
    deterministic: AuditReport,
    proposal: AuditRepairProposal,
) -> AuditReport:
    annotations = list(deterministic.annotations)

    for proposed in proposal.annotations:
        duplicate = any(
            existing.sentence == proposed.sentence
            and existing.text_span == proposed.text_span
            and existing.subtype == proposed.subtype
            for existing in annotations
        )

        if duplicate:
            continue

        annotations.append(
            proposed.model_copy(
                update={
                    "annotation_id": f"ANN_{len(annotations) + 1:04d}"
                }
            )
        )

    merged_quality = merge_quality_assessments(
        deterministic.quality_assessment,
        proposal.quality_assessment,
    )

    serious = any(
        annotation_requires_repair(annotation)
        for annotation in annotations
    )

    if deterministic.mode == AuditMode.ANNOTATION_ONLY:
        decision = AuditDecision.PASS
    elif serious:
        decision = AuditDecision.REVISE
    else:
        decision = AuditDecision.PASS

    release_status = decide_release_status(
        annotations=annotations,
        quality=merged_quality,
        methodological_warnings=deterministic.methodological_warnings,
        repair_budget_exhausted=False,
        audit_mode=deterministic.mode,
    )


    return deterministic.model_copy(
        update={
            "annotations": annotations,
            "decision": decision,
            "release_status": release_status,
            "residual_risk": " ".join(
                _ordered_dedupe(
                    [
                        deterministic.residual_risk,
                        proposal.residual_risk,
                    ]
                )
            ),
            "revision_instructions": _ordered_dedupe(
                deterministic.revision_instructions
                + proposal.revision_instructions
            ),
            "quality_assessment": merged_quality,
            "methodological_warnings": deterministic.methodological_warnings,
            "component_assessments": deterministic.component_assessments,
            "support_map_patches": deterministic.support_map_patches,
        }
    )


def fallback_audit_proposal(
    deterministic: AuditReport,
) -> AuditRepairProposal:
    return AuditRepairProposal(
        annotations=[],
        repairs=[],
        recommended_decision=deterministic.decision,
        residual_risk=(
            "Semantic auditing was unavailable. "
            + deterministic.residual_risk
        ),
        quality_assessment=deterministic.quality_assessment,
        revision_instructions=deterministic.revision_instructions,
    )


def repair_score(candidate: RepairCandidate) -> float:
    return (
        0.45 * candidate.factual_support_score
        + 0.25 * candidate.meaning_preservation_score
        + 0.20 * candidate.readability_score
        - 0.10 * candidate.residual_hallucination_risk
    )


def validate_repair_candidate(
    candidate: RepairCandidate,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
    original_text: str | None = None,
) -> list[str]:
    errors: list[str] = []
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    facts = {
        fact.fact_id: fact
        for fact in fact_ledger.writer_ready_facts
    }
    verified_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.verified_insights
    }
    hypothesis_insights = {
        insight.insight_id: insight
        for insight in insight_ledger.hypothesis_only_insights
    }
    all_insights = {
        **verified_insights,
        **hypothesis_insights,
    }

    unknown_insights = [
        insight_id
        for insight_id in candidate.supporting_insight_ids
        if insight_id not in all_insights
    ]
    if unknown_insights:
        errors.append(
            f"Unknown repair insight IDs: {unknown_insights}"
        )
        return errors

    if (
        set(candidate.supporting_insight_ids)
        & set(hypothesis_insights)
        and not allow_hypotheses_in_report
    ):
        errors.append(
            "The replacement introduces a hypothesis while hypotheses are "
            "disabled."
        )

    expanded_fact_ids = list(
        dict.fromkeys(
            [
                *candidate.supporting_fact_ids,
                *[
                    fact_id
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                    for fact_id in all_insights[
                        insight_id
                    ].source_fact_ids
                ],
            ]
        )
    )

    unknown = [
        fact_id
        for fact_id in expanded_fact_ids
        if fact_id not in facts
    ]

    if unknown:
        errors.append(f"Unknown repair fact IDs: {unknown}")
        return errors

    if candidate.strategy == RepairStrategy.DELETE:
        if candidate.replacement_text.strip():
            errors.append(
                "Delete repairs must use an empty replacement_text."
            )
        return errors

    if not candidate.replacement_text.strip():
        errors.append("Non-delete repairs require replacement text.")
        return errors

    if (
        original_text is not None
        and " ".join(candidate.replacement_text.split())
        == " ".join(original_text.split())
    ):
        errors.append(
            "The replacement is identical to the original sentence."
        )
        return errors

    supporting_facts = [
        facts[fact_id]
        for fact_id in expanded_fact_ids
    ]

    replacement_hypothesis = EXPLANATORY_HYPOTHESIS_PATTERN.search(
        candidate.replacement_text
    )
    supporting_hypothesis_ids = set(
        candidate.supporting_insight_ids
    ) & set(hypothesis_insights)
    if replacement_hypothesis:
        if (
            not allow_hypotheses_in_report
            or not supporting_hypothesis_ids
        ):
            errors.append(
                "The replacement introduces an explanatory hypothesis "
                "without permitted hypothesis-only provenance."
            )
        elif (
            not HYPOTHESIS_WORDING_PATTERN.search(
                candidate.replacement_text
            )
            and not candidate.replacement_text.strip().endswith("?")
        ):
            errors.append(
                "The replacement does not explicitly label its hypothesis."
            )

    supporting_evidence_ids = {
        evidence_id
        for fact in supporting_facts
        for evidence_id in fact.evidence_ids
    }
    evidence_lookup = build_evidence_lookup(evidence)
    strength_conflicts = qualitative_strength_conflicts(
        candidate.replacement_text,
        [
            evidence_lookup[evidence_id]
            for evidence_id in supporting_evidence_ids
            if evidence_id in evidence_lookup
        ],
    )
    if strength_conflicts:
        errors.append(
            "The replacement uses a qualitative strength label that conflicts "
            "with its mapped evidence: "
            + "; ".join(strength_conflicts)
        )

    if (
        INTERPRETIVE_SYNTHESIS_PATTERN.search(
            candidate.replacement_text
        )
        and not candidate.supporting_insight_ids
    ):
        replacement_normalised = re.sub(
            r"\W+",
            " ",
            candidate.replacement_text.lower(),
        ).strip()
        exact_fact_wording = {
            re.sub(r"\W+", " ", text.lower()).strip()
            for fact in supporting_facts
            for text in [
                fact.fact_summary,
                *fact.allowed_interpretations,
            ]
        }
        if replacement_normalised not in exact_fact_wording:
            errors.append(
                "The replacement introduces an interpretive synthesis "
                "without a verified insight ID."
            )

    support_numbers = [
        number
        for fact in supporting_facts
        for number in fact_support_numbers(fact, evidence)
    ]

    if not numbers_supported(
        candidate.replacement_text,
        support_numbers,
    ):
        errors.append(
            "The replacement introduces unsupported numbers."
        )

    permissions = {
        permission
        for fact in supporting_facts
        for permission in fact.claim_permissions
    }

    if (
        CAUSAL_PATTERN.search(candidate.replacement_text)
        and not negative_causal(candidate.replacement_text)
        and (
            ClaimPermission.CAUSAL not in permissions
            or (
                candidate.supporting_insight_ids
                and not any(
                    CAUSAL_PATTERN.search(
                        all_insights[insight_id].statement
                    )
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                )
            )
        )
    ):
        errors.append(
            "The replacement introduces unsupported causal language."
        )

    if (
        PREDICTIVE_PATTERN.search(candidate.replacement_text)
        and not negative_predictive(candidate.replacement_text)
        and (
            ClaimPermission.PREDICTIVE not in permissions
            or (
                candidate.supporting_insight_ids
                and not any(
                    PREDICTIVE_PATTERN.search(
                        all_insights[insight_id].statement
                    )
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                )
            )
        )
    ):
        errors.append(
            "The replacement introduces unsupported predictive language."
        )

    if (
        FORECAST_PATTERN.search(candidate.replacement_text)
        and not negative_forecast(candidate.replacement_text)
        and (
            ClaimPermission.FORECAST not in permissions
            or (
                candidate.supporting_insight_ids
                and not any(
                    FORECAST_PATTERN.search(
                        all_insights[insight_id].statement
                    )
                    for insight_id in candidate.supporting_insight_ids
                    if insight_id in all_insights
                )
            )
        )
    ):
        errors.append(
            "The replacement introduces unsupported forecast language."
        )

    if (
        DATASET_GENERALISATION_PATTERN.search(
            candidate.replacement_text
        )
        and not any(
            DATASET_GENERALISATION_PATTERN.search(
                all_insights[insight_id].statement
            )
            for insight_id in candidate.supporting_insight_ids
            if insight_id in all_insights
        )
    ):
        errors.append(
            "The replacement generalises beyond its verified support."
        )

    if (
        INSIGHT_OVERSTATEMENT_PATTERN.search(
            candidate.replacement_text
        )
        and not any(
            INSIGHT_OVERSTATEMENT_PATTERN.search(
                all_insights[insight_id].statement
            )
            for insight_id in candidate.supporting_insight_ids
            if insight_id in all_insights
        )
    ):
        errors.append(
            "The replacement is stronger than its verified insight wording."
        )

    known_entities = {
        entity
        for fact in supporting_facts
        for entity in fact.entities
    }

    unsupported_entities = unsupported_backtick_entities(
        candidate.replacement_text,
        known_entities,
    )
    if unsupported_entities:
        errors.append(
            "Unsupported named entities in replacement: "
            f"{unsupported_entities}"
        )

    return errors


def apply_repair_proposal(
    writer_output: WriterOutput,
    proposal: AuditRepairProposal,
    fact_ledger: FactLedger,
    evidence: EvidenceLedger,
    insight_ledger: InsightLedger | None = None,
    allow_hypotheses_in_report: bool = False,
) -> tuple[WriterOutput, list[ReportPatch]]:
    insight_ledger = insight_ledger or InsightLedger(
        synthesis_enabled=False
    )
    markdown = writer_output.markdown
    support_map = list(writer_output.sentence_support)
    patches: list[ReportPatch] = []

    support_by_sentence = {
        support.sentence_text: support
        for support in support_map
    }
    flagged_sentences = {
        repair.original_sentence
        for repair in proposal.repairs
    }
    original_unflagged_sentences = {
        support.sentence_text
        for support in writer_output.sentence_support
        if support.sentence_text not in flagged_sentences
    }

    for repair in proposal.repairs:
        original = repair.original_sentence

        if original not in markdown:
            continue

        ranked_candidates = sorted(
            repair.candidates,
            key=repair_score,
            reverse=True,
        )

        selected: RepairCandidate | None = None

        if repair.preferred_repair_id:
            preferred = next(
                (
                    candidate
                    for candidate in ranked_candidates
                    if candidate.repair_id == repair.preferred_repair_id
                ),
                None,
            )

            if preferred is not None:
                ranked_candidates = [
                    preferred,
                    *[
                        candidate
                        for candidate in ranked_candidates
                        if candidate.repair_id != preferred.repair_id
                    ],
                ]

        for candidate in ranked_candidates:
            if not validate_repair_candidate(
                candidate,
                fact_ledger,
                evidence,
                insight_ledger,
                allow_hypotheses_in_report,
                original_text=original,
            ):
                selected = candidate
                break

        if selected is None:
            continue

        replacement = selected.replacement_text
        operation = (
            "delete"
            if selected.strategy == RepairStrategy.DELETE
            else "replace"
        )

        markdown = markdown.replace(
            original,
            replacement,
            1,
        )

        existing_support = support_by_sentence.get(original)

        if existing_support is not None:
            support_map.remove(existing_support)
            support_by_sentence.pop(original, None)

        if replacement.strip():
            supporting_facts = {
                fact.fact_id: fact
                for fact in fact_ledger.writer_ready_facts
            }
            main_insights = {
                insight.insight_id: insight
                for insight in insight_ledger.verified_insights
            }
            hypothesis_insights = {
                insight.insight_id: insight
                for insight in insight_ledger.hypothesis_only_insights
            }
            all_insights = {
                **main_insights,
                **hypothesis_insights,
            }
            replacement_fact_ids = list(
                dict.fromkeys(
                    [
                        *selected.supporting_fact_ids,
                        *[
                            fact_id
                            for insight_id in selected.supporting_insight_ids
                            if insight_id in all_insights
                            for fact_id in all_insights[
                                insight_id
                            ].source_fact_ids
                        ],
                    ]
                )
            )

            replacement_evidence = list(
                dict.fromkeys(
                    [
                        *[
                            evidence_id
                            for fact_id in replacement_fact_ids
                            if fact_id in supporting_facts
                            for evidence_id in supporting_facts[
                                fact_id
                            ].evidence_ids
                        ],
                        *[
                            evidence_id
                            for insight_id in selected.supporting_insight_ids
                            if insight_id in all_insights
                            for evidence_id in all_insights[
                                insight_id
                            ].source_evidence_ids
                        ],
                    ]
                )
            )
            replacement_level = InterpretationLevel.FINDING
            if set(selected.supporting_insight_ids) & set(
                hypothesis_insights
            ):
                replacement_level = InterpretationLevel.HYPOTHESIS
            elif set(selected.supporting_insight_ids) & set(
                main_insights
            ):
                replacement_level = InterpretationLevel.BOUNDED_INSIGHT

            replacement_sentences = (
                split_markdown_sentences(replacement)
                or [replacement]
            )
            used_sentence_ids = {
                support.sentence_id
                for support in support_map
            }
            numeric_sentence_ids = [
                int(match.group(1))
                for support in support_map
                if (
                    match := re.fullmatch(
                        r"SENT_(\d+)",
                        support.sentence_id,
                    )
                )
            ]
            next_sentence_number = max(
                numeric_sentence_ids,
                default=0,
            ) + 1

            for index, replacement_sentence in enumerate(
                replacement_sentences
            ):
                sentence_id = repair.sentence_id
                if index > 0 or sentence_id in used_sentence_ids:
                    while (
                        f"SENT_{next_sentence_number:04d}"
                        in used_sentence_ids
                    ):
                        next_sentence_number += 1
                    sentence_id = (
                        f"SENT_{next_sentence_number:04d}"
                    )
                    next_sentence_number += 1

                new_support = SentenceSupport(
                    sentence_id=sentence_id,
                    sentence_text=replacement_sentence,
                    fact_ids=replacement_fact_ids,
                    evidence_ids=replacement_evidence,
                    insight_ids=selected.supporting_insight_ids,
                    interpretation_level=replacement_level,
                    support_type=(
                        SupportType.MULTI_FACT_SYNTHESIS
                        if replacement_level
                        != InterpretationLevel.FINDING
                        else SupportType.PARAPHRASE
                    ),
                )

                support_map.append(new_support)
                support_by_sentence[
                    replacement_sentence
                ] = new_support
                used_sentence_ids.add(sentence_id)

        patches.append(
            ReportPatch(
                sentence_id=repair.sentence_id,
                original_text=original,
                replacement_text=replacement,
                operation=operation,
                selected_repair_id=selected.repair_id,
            )
        )

    selected_fact_ids = list(
        dict.fromkeys(
            fact_id
            for support in support_map
            for fact_id in support.fact_ids
        )
    )

    all_fact_ids = [
        fact.fact_id
        for fact in fact_ledger.writer_ready_facts
    ]

    for sentence in original_unflagged_sentences:
        if sentence and sentence not in markdown:
            raise ValueError(
                "A targeted repair modified or removed unflagged report content."
            )

    return (
        writer_output.model_copy(
            update={
                "markdown": markdown,
                "sentence_support": support_map,
                "selected_fact_ids": selected_fact_ids,
                "omitted_fact_ids": [
                    fact_id
                    for fact_id in all_fact_ids
                    if fact_id not in selected_fact_ids
                ],
                "writer_mode": "auditor_repaired",
            }
        ),
        patches,
    )
