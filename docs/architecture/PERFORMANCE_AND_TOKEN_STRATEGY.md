# Table2Text performance and token strategy

Prepared 5 September 2026. This is a design and investigation report, not an implemented optimization or a measured claim of future gains.

## 1. Recommendation

Keep the deterministic evidence engine and traceable claims, but replace the largely fixed sequence of broad model reviews with an adaptive pipeline that sends small, complete evidence packets to the model that needs them. Make the output contract determine the work budget. Perform semantic reasoning where it changes the report, and perform copying, arithmetic, provenance bookkeeping, and exact validation in Python.

There are two useful objectives:

1. **Efficiency:** comparable factuality, coverage, and writing quality with substantially fewer tokens and shorter report latency.
2. **Quality at a fixed budget:** fewer semantic mistakes and omissions, better selection and prose, without increasing total tokens. Reinvest some savings in an independent, targeted semantic review or a stronger model for difficult cases.

The same foundational changes support both objectives. My preferred end state has a one-call short-form path, a two- or three-call familiar-event path, and a three- or four-call unfamiliar/analytical path. These are normal-path design targets, not limits that override necessary coverage or an explicit complex request. Local deterministic steps remain between calls.

Do not start by rewriting the framework, adding more agents, or switching every role to a larger model. The largest evidenced opportunities are payload design, task routing, reasoning control, verification scope, and retry behavior.

## 2. Evidence and scope

I inspected the current runtime, schemas, configuration, evaluation runner, separate LLM-only experiment, historical ablation report, and the saved 25-example protected-holdout run. I reconstructed writer payloads from saved artifacts and ran two local deterministic CPU profiles. No live paid model calls were made for this investigation. The runtime was not changed.

Historical behavior must not be confused with the rebuilt environment: the holdout used DeepSeek V4 Flash for all roles, prompted structured output, up to eight requests per invocation, and a **300,000-token limit per invocation**. The newly installed dependency versions are not identical to that historical environment. The current `workflow.py` and `agents.py` differ from their frozen copies only by added module docstrings, so their relevant control-flow findings apply directly; provider behavior still needs contemporary verification.

### Recorded baseline

| Cohort | Examples | Recorded total tokens | Mean tokens/report | Median latency | Recorded requests |
|---|---:|---:|---:|---:|---:|
| Event reports, SportSett | 5 | 3,135,401 | 627,080 | 952.5 seconds | 65 |
| Short-form tasks | 20 | 164,564 | 8,228 | 10.7 seconds | 24 |
| Combined | 25 | 3,299,965 | — | — | 89 |

Five event reports account for approximately **95% of recorded tokens and elapsed generation time**. They contain 219–330 final words, but consume 514,250–813,172 recorded tokens each. The total recorded elapsed time is 5,413.9 seconds. This is one saved cohort, not an estimate for every future workload.

### Where recorded tokens went

| Stage group | Total tokens | Share of recorded total |
|---|---:|---:|
| Initial and post-repair audits | 729,466 | 22.1% |
| Initial insight verification | 437,883 | 13.3% |
| Fact verification | 357,841 | 10.8% |
| Individual insight verification retries | 352,088 | 10.7% |
| Fact enrichment/evidence synthesis | 332,031 | 10.1% |
| Data understanding | 303,611 | 9.2% |
| Insight synthesis | 271,765 | 8.2% |
| Natural writer, including short tasks | 266,675 | 8.1% |
| Writer quality revision | 248,605 | 7.5% |

Verification and audit together consume **56.9%** of the recorded total. The opportunity is to change how these checks work, not to infer that checking is unnecessary.

Of 657,830 recorded output tokens, **494,545 were reported as reasoning tokens: 75.2% of output and 15.0% of all recorded tokens**. Reasoning is already included in output tokens; it must not be added again. Input tokens total 2,642,135, of which 414,976 were recorded cache reads, approximately 15.7%. Cache reads are already part of input tokens.

### The baseline understates consumption

For event `6127`, the trace records an audit failure with `total_tokens=312719`, but that failed invocation is absent from `stage_token_usage.csv`. Adding just that known omission raises the trace-supported total to at least **3,612,684 tokens**. Three event writer attempts also ended in a provider HTTP 400 with no usage logged at the workflow boundary; their actual consumed tokens cannot be reconstructed from the summary.

Do not equate generation success with successful execution of all review stages. All 25 outputs completed, but model failures and deterministic fallbacks occurred within them.

Sources: [holdout execution report](../../table2text_pydanticai/evaluation/protected_holdout_full_system/results/PROTECTED_HOLDOUT_EXECUTION_REPORT.md), [per-stage usage](../../table2text_pydanticai/evaluation/protected_holdout_full_system/results/stage_token_usage.csv), [per-report summaries](../../table2text_pydanticai/evaluation/protected_holdout_full_system/results/protected_generation_summary.jsonl), and each summary's `run_directory/trace.jsonl`.

## 3. Highest-impact findings and changes

### P0 — Fix budget enforcement and accounting first

`Table2TextWorkflow.usage_limits()` creates limits for each `agent.run()` call. Neither runner passes a shared usage accumulator. Individual insight retries therefore start another invocation budget. `max_total_tokens` is not a report-wide maximum, and `max_agent_requests` is not a report-wide request count.

Create a report-level budget controller with stage allocations, a reserved audit/repair allowance, and a wall-clock deadline. Record every provider attempt, including responses later rejected by parsing, validation, or a token limit. Keep request-level usage as structured fields, with stage totals derived from those records. Avoid parsing `str(RunUsage(...))` as the permanent telemetry format.

For sequential handoffs, PydanticAI supports sharing usage across calls; its own multi-agent examples demonstrate this pattern. For concurrent calls, use atomic reservations and reconcile actual usage, rather than letting multiple calls independently spend the same remaining allocation. [PydanticAI multi-agent documentation](https://github.com/pydantic/pydantic-ai/blob/main/docs/multi-agent-applications.md).

Preflight complete prompt size and reserve output before sending. The installed PydanticAI 1.107.5 checks reported token usage after responses and documents pre-request counting only for certain providers; do not assume DeepSeek's OpenAI-compatible endpoint supports that facility. Use an appropriate tokenizer/estimator with a safety margin plus provider output limits, and label estimates separately from reported usage. A threshold checked after payment is not a hard spending guarantee.

Minimum telemetry: report/stage/attempt IDs; model and dependency versions; prompt/schema/config hashes; input, cached input, output, reasoning, requests; retries by reason; request duration; fallback; selected/rejected/unused claim counts; review coverage; and billable cost when actual rates and usage are available. Keep token savings, monetary savings, and latency savings separate.

### P0 — Stop cutting structured context in the middle

`audit.py:compact_json()` uses `indent=2` and cuts the serialized string at 160,000 characters. This is neither compact serialization nor a token-aware context budget. Separate calls to this function can each contribute up to 160,000 characters to one prompt.

All five saved event evidence ledgers are roughly 228–236 KB; their fact ledgers are roughly 213–249 KB. Passing them through the current serializer cuts off valid records. The insight package combines facts with referenced evidence and can also exceed this boundary.

Reconstructing the actual writer payload for event `6127` gives **175,409 characters**. Its tail is cut before all later fields can be sent. `content_requirements`, event guidance, and `narrative_plan` occur after the large fact arrays. The model can therefore be penalized by validators for requirements it did not fully receive. This is an observed payload defect; its precise contribution to individual retries has not been causally measured.

Implement one prompt compiler that:

- serializes valid JSON with compact separators;
- includes contract and hard constraints before optional evidence;
- selects complete records within a token budget;
- retains every evidence dependency of each selected claim;
- reports which optional records were omitted and why;
- fails or routes to a larger/segmented task when mandatory coverage cannot fit;
- asserts that every ID required by a validator was visible to the model, unless it is explicitly controller-owned metadata.

Minification alone changes that writer payload from 175,409 to 111,790 characters, a **36.3% character reduction**, while preserving fields. This is not a measured 36.3% token reduction. More importantly, the structural redesign below should make the original oversized payload unnecessary.

### P0 — Make reasoning and provider limits explicit

`agent_model_settings()` currently supplies only `max_tokens` and, usually, temperature. There is no per-role reasoning policy. Builder output ceilings range up to 12,000 tokens, including 11,000 for the same writer used for one-sentence output.

DeepSeek's current documentation says thinking defaults to enabled with high effort, and sampling settings such as temperature have no effect in thinking mode. It documents a separate thinking toggle and effort control. Explicitly configure low/off thinking for extraction, ID selection, straightforward verbalization, and exact checks; reserve higher effort for ambiguous interpretation or a difficult semantic review. Benchmark each choice rather than turning thinking off everywhere. [DeepSeek thinking mode](https://api-docs.deepseek.com/guides/thinking_mode/).

Historical single requests sometimes reported output above the configured builder ceiling. Capture the actual outbound request fields and provider response metadata in an adapter test. Verify the effective completion/reasoning cap for the selected API mode; do not assume a field accepted by an SDK is enforced as intended by the endpoint.

The three saved writer HTTP 400 errors have the message `Invalid assistant message: content or tool_calls must be set`. Reproduce with sanitized request fixtures and identify whether empty output, history serialization, or a retry sequence is responsible. The logs alone do not establish the underlying cause. DeepSeek also documents occasional empty JSON-mode content, but that is a relevant hypothesis, not proof of this failure's cause. [DeepSeek JSON output](https://api-docs.deepseek.com/guides/json_mode/).

### P1 — Normalize evidence once; send projections, not ledgers

`finalise_fact_ledger()` copies each referenced evidence item's `metrics` into `VerifiedFact.structured_values` and collects metric strings/keys as entities. Later prompts contain both these expanded facts and the original evidence ledger. Writer packs include full ledgers plus selected collections, while audit prompts include facts, evidence, insights, profile registry, writer output, and pre-audit output together.

Store one canonical evidence record. A claim should reference it and identify its exact relevant operands. Use separate small models for LLM input/output and rich models for persisted research artifacts. A rich Pydantic artifact is useful; sending its entire serialization to every role is not required.

For example, a model-visible claim can have this form:

```json
{"id":"c17","subject":"team_a","relation":"scored_more_than","object":"team_b","values":{"a":103,"b":95,"margin":8},"unit":"points","scope":"full_game","evidence":["e4"],"allowed":"descriptive"}
```

The real system must preserve original source strings and stable provenance; this example is illustrative. A controller can supply short local aliases for IDs and expand them in artifacts. Models should not regenerate fingerprints, repeated permission lists, method descriptions, full rankings, or evidence dictionaries already owned by Python.

Use a single schema-and-source-aware index for evidence IDs, facts, entities, units, and scope. Prompt projections must preserve entity/value binding, denominators, comparison direction, ties, and necessary caveats. A lossy summary of all evidence is not an adequate replacement.

### P1 — Merge the two overlapping synthesis passes

The first Evidence Analyst call already requests improvements, combinations, and prioritization of a deterministic scaffold. The second asks for bounded insight synthesis. Both reason about largely the same evidence and can create overlapping report material.

Retain deterministic atomic facts. Replace those two LLM passes with one bounded **content selection and synthesis** call that returns:

- selected existing claim IDs and ordering;
- a small number of proposed derived claims with exact support references;
- essential caveats and mandatory coverage decisions;
- no rewritten copy of every atomic fact.

Move routine comparisons, ranking, deltas, percentages, and supported conjunctions into typed deterministic operators. Preserve the distinction between a descriptive contrast and a causal explanation. A model may propose an operation; Python executes and validates it.

For familiar small event inputs, test merging selection and writing into a single draft call followed by an independent critic. For complex analytical narratives, retain a separate selector when experiments show it improves coverage or synthesis. This gives a two-call efficiency variant and a three-call quality variant, rather than one universal fixed architecture.

Do not delete insights wholesale. The existing one-example ablation retained basic factuality without insights but reduced supported relational content and output breadth. It is useful directional evidence, not a clean population-level causal result. [Saved ablation analysis](../../table2text_pydanticai/evaluation/results/sportsett_4934_ablation_story.md).

### P1 — Verify the risky transformation, not every copy of a fact

The current Fact Verifier reviews every candidate, including deterministic scaffold facts. Later, the insight verifier reviews derived claims; finally the auditor rereads all ledgers. These checks have overlapping concerns, but are not fully interchangeable.

Introduce three claim classes:

| Claim origin | Required verification |
|---|---|
| Direct extraction or deterministic calculation | Typed operand/source validation, units/scope/permissions, provenance |
| LLM interpretation or derived assertion | Deterministic validation plus targeted semantic review |
| Final natural-language sentence | Verify its meaning against exact supporting claims; check coverage and unsupported additions |

A correct number somewhere in the support packet does not prove a sentence is correct. `writer_sentence_grounding_errors()` pools numbers from mapped facts and separately checks certain entity forms. It cannot, by that numeric membership test alone, distinguish “Alice scored 10, Bob scored 20” from the reversed assignment when both values are present. Other audit functions add checks, but the numeric helper is not a general entailment proof.

Strengthen this boundary with atomic relation-bearing claims and sentence-to-claim alignment. Prefer deterministic rendering for high-risk numbers/units/comparison phrases where practical, while leaving grammar and narrative integration to the writer. Retain targeted independent semantic review for natural-language relationships that cannot be proven deterministically.

Do not label a default approval as semantic verification. `fallback_verification()` assigns approve/caution based on the candidate and caveats; it does not itself compare the assertion with source evidence. Subsequent finalization performs deterministic checks, but these should be recorded honestly. `VerifiedFact.verification_method` defaults to `llm_verified`, and the saved short-form E2E fact has that label despite the trace showing skipped LLM fact verification. Carry the actual verification method explicitly through finalization and recovery.

### P1 — Replace broad audits with sentence evidence packets

For each final sentence, construct a small packet containing its proposed claims, exact supporting source values, units/scope, and applicable prohibitions. Include all factual sentences in a batched final review for the quality path, not only sentences flagged by existing regex checks. That avoids assuming current local detectors catch every semantic error.

Give the critic the full short draft for coherence and cross-sentence contradictions, but only compact relevant evidence. Include competing facts needed to test rankings or winner claims; citation-only retrieval must not hide contradicting source evidence. Perform required-content coverage separately against a deterministic checklist.

Ask for a compact verdict and, when necessary, one targeted patch. Do not ask for lengthy rationales for every correct fact or up to three alternatives per sentence by default. Permit an explanation or another candidate only when needed to resolve ambiguity.

After a patch, rerun deterministic checks on affected claims and report-level constraints. Semantically review changed sentences and dependencies; avoid rereading all unchanged evidence. If a change alters the report's global meaning, expand the review scope explicitly.

### P1 — Bound retries and reuse valid work

There are two retry layers: PydanticAI output retries, and the workflow's per-insight repair loop. The holdout's individual insight retries consumed 352,088 recorded tokens and 24 requests. The loop already narrows facts/evidence for one candidate and retains valid reviews; build on that behavior instead of replacing it with another full-batch retry.

Separate malformed JSON, missing IDs, unsupported semantics, transport errors, and exhausted budgets. Only retry errors a new call can plausibly resolve. Use typed errors keyed by candidate ID instead of matching IDs inside error strings. Batch the unresolved subset into a bounded repair request when it fits. Skip optional unresolved insights when budget is exhausted; escalate a missing mandatory fact instead of silently dropping it.

Fix deterministic metadata locally when the source of truth is unambiguous. Do not ask a model to repeat a complete interpretation because it copied the wrong fingerprint. Do not repair a substantive claim by silently changing its meaning.

Checkpoint expensive stage outputs with versioned content hashes. Resuming a failed writer should reuse valid interpretation, evidence, and selection results. Retry policy needs a report-wide deadline and request cap in addition to per-stage controls.

### P1 — Specialize short-form prompts and schemas

The short-form path is already implemented: it skips LLM understanding, enrichment, fact verification, insight synthesis, and usually the semantic auditor when deterministic audit passes. In the saved cohort, these tasks use 24 recorded writer requests for 20 outputs. Do not claim another six-to-one agent reduction here.

However, they still use `WRITER_INSTRUCTIONS`, a **17,530-character** instruction block covering many genres, and `WriterAgentDraft` with title, sections, notes, and sentence support machinery. The short E2E example's additional payload is 6,209 pretty-printed characters for a 26-word result.

Create a short-form writer with only its task-specific rules and a minimal sentence/claim-ID schema. Use controller-provided defaults for headings, metadata, and provenance. Maintain task semantics: an “all supplied attributes/triples” request cannot be optimized by dropping facts to meet an arbitrary cap. For templates with exact safe realization, allow a zero-model path; use LLM realization when fluency or relation interpretation needs it.

Use native schema enforcement only for provider/model/API combinations confirmed to support the needed schema. Otherwise use a small prompted/tool schema and strict local validation. Changing `structured_output_mode` globally without a compatibility test could increase failures.

### P1 — Make configuration limits coherent

`build_compact_insight_payload()` advertises `candidate_count: uncapped` and `verified_insight_count: uncapped` even though settings expose candidate and verified-insight limits. Elsewhere validation can reject too many candidates. The plan and scaffold also deliberately set `maximum_facts=None`. Writer fact caps act later, after upstream work has already been paid for. The `force_llm_short_form_writer` setting also affects the upstream short-form routing predicate, so it is not merely a writer switch.

Derive selection, prompt instructions, output schema limits, validation rules, and budget reservations from one resolved task policy. Cap optional candidates before synthesis and verification, not only before writing. Preserve required coverage first, then allocate remaining budget by relevance, novelty, and evidence strength. Require explicit abstention or task segmentation when mandatory coverage exceeds the budget.

## 4. Proposed execution structure

```text
Input + user request
    -> sanitize references/metadata; parse source once
    -> resolve task contract and uncertainty
    -> reuse validated schema mapping OR compact interpretation/plan call
    -> deterministic evidence and atomic claim store
    -> contract-aware selection under a token budget
        short records:              compact writer
        familiar event, fast:       select-and-write
        event/analysis, quality:     bounded selector -> writer
    -> deterministic semantic/structural checks
    -> compact independent critic where required
    -> optional targeted patch + affected-claim recheck
    -> release with actual review status and usage
```

The planner should choose from executable capabilities and receive only the schema slice it needs. Reuse the existing deterministic event planner; it is already skipped as an LLM stage in the saved event runs. When unfamiliar semantics require a model, combine understanding and planning into one constrained mapping/query specification if validation shows that is reliable.

Do not introduce an autonomous supervisor that asks agents what to do next on every step. A small explicit state machine can choose the path from task type, ambiguity, evidence completeness, error category, and remaining budget.

### Role decisions

| Current role/component | Proposed treatment |
|---|---|
| Data Understanding | Conditional; reusable schema mapping and deterministic metadata, one compact call for unresolved semantics |
| Orchestrator | Deterministic for familiar capabilities; merge with interpretation for ambiguous inputs where appropriate |
| Evidence Analyst, first pass | Replace with deterministic claims plus the shared selection/synthesis stage |
| Fact Verifier | Deterministic for typed atomic facts; semantic review for model-authored transformations |
| Insight Analyst, second pass | Merge into selection/synthesis; retain only useful bounded synthesis |
| Insight Verifier | Review selected derived claims in compact batches; reuse evidence needed by final review |
| Writer | Genre-specific prompt/schema; optionally combine with selection on simple event tasks |
| Factual Auditor | Retain independent semantic responsibility with sentence-level evidence and targeted patches |
| Whole-report quality revision | Conditional; first fix coverage/selection upfront; prefer local edits when the defect is local |
| Deterministic narrative planner | Retain; reuse its slots for both selection and coverage validation |
| Deterministic evidence/permission/provenance checks | Retain and strengthen entity–relation–value checks |

There are six conceptual roles but eight constructed Agent objects because synthesis and verification have second-pass agents. All eight are created eagerly when LLM use is enabled, including on short-form requests. Lazy initialization helps startup and service efficiency, though merely constructing an agent is not a billed model call.

## 5. Better quality without more tokens

The most promising quality improvements spend fewer tokens on irrelevant material and more attention on the right distinctions:

1. **Restore complete constraints.** Eliminate payload cuts and the prompt/validator mismatch. Put mandatory coverage into a small, shared task contract.
2. **Improve source meaning once.** Validate entity identity, metric meaning, units, temporal scope, and relation direction before prose. Reuse a mapping only after confirming the new input still satisfies its schema and semantic assumptions.
3. **Select for coverage and novelty.** Choose a result-first narrative with supported contrasts and relevant exceptions. Use mandatory slots plus diversity across subjects and finding types. Do not let long ranking lists crowd out the result or the weaker side of a comparison.
4. **Make numerical claims exact.** Evaluate declarative comparisons and calculations in Python. A richer reasoning model should not be paid to recompute arithmetic already available deterministically.
5. **Use a stronger model selectively.** Compare models for the bounded selector, writer, or independent critic, not by upgrading every role. Equal tokens do not imply equal money or latency; impose separate cost and latency constraints.
6. **Separate style from factual correction.** A semantic critic can identify unsupported implications; a small targeted writer edit can repair wording without regenerating every valid sentence.
7. **Route uncertainty explicitly.** Escalate ambiguous schemas, contradictory records, missing operands, unsupported causal phrasing, and unresolved reviewer disagreements. Do not use a model's self-reported confidence as the sole routing signal.
8. **Use spare budget only when useful.** In a quality policy, permit one focused second opinion for a contested high-impact claim or a second draft when the first fails coverage/coherence. Do not add universal self-consistency sampling, debate, or repeated judges.
9. **Improve the evaluator's evidence representation.** Evaluate a sentence against relevant canonical source relations as a new diagnostic, alongside existing frozen metrics. The dossier already reports unreliable-looking HHEM/AlignScore behavior on long nested SportSett inputs. Changing scoring context changes the metric protocol and must be reported as such.

Research on long-context use supports testing focused context, but does not establish the improvement for this model or application. The project's own payload truncation is stronger direct evidence for this particular redesign. [Lost in the Middle](https://arxiv.org/abs/2307.03172).

### Candidate budget policies to test

These are experimental targets, not achieved measurements or guaranteed service-level objectives.

| Policy | Typical shape | Initial total-token target |
|---|---|---:|
| Short-form efficient | Deterministic extraction + minimal writer; critic only when needed | 1,000–3,000 for small records |
| Familiar-event efficient | Deterministic claims + select/write + compact critic | 15,000–30,000 |
| Event quality | Bounded selector + writer + independent critic + repair reserve | 30,000–60,000 |
| Ambiguous/analytical quality | Interpretation/plan + deterministic analysis + selection/write/review | 40,000–100,000 initially |

Moving from the recorded event mean of 627,080 to 30,000–60,000 would mean approximately **90–95% fewer tokens**. That is a reasonable ambitious design target given the repeated payloads, but it must be earned by evaluation. It does not imply the same percentage latency reduction. The short-task target is roughly 64–88% below the historical 8,228-token mean; the main gain must come from prompt/reasoning reduction because that path already uses few calls.

An illustrative 30,000-token event envelope could allocate 6,000 to selection/synthesis, 8,000 to writing, 8,000 to semantic review, and 8,000 to contingencies. Each allocation includes input plus output and any reasoning. Unknown-schema interpretation must fit the contingency or cause explicit routing to the larger policy. Do not spend the entire contingency by default.

## 6. Caching, tools, and throughput

### Application caches

Cache parsed/sanitized input, profile/structural catalog, validated semantic mapping, deterministic query results, and final projections separately. Use keys that include normalized source content, field-isolation policy, schema/version, query operands, sampling seed, and analytical settings. Mapping caches need schema and semantic validation; identical field names alone are insufficient.

Keep request-specific selection and prose separate from source-derived evidence. Changed audience or wording should not require reloading a 16 MB CSV and recomputing its statistics. Changed source values must invalidate evidence even if its schema is unchanged.

### Provider prompt caching

DeepSeek uses shared prefixes for context-cache reuse. Place stable role instructions and stable schema first, reusable source context next where appropriate, and variable request/repair content last. Do not put timestamps or run fingerprints before a reusable prefix unless necessary. Confirm hits using returned usage rather than assuming caching occurred. [DeepSeek context caching](https://api-docs.deepseek.com/guides/kv_cache/).

Provider caching reduces repeated input processing and can reduce billed input cost; it does not remove those tokens from the logical context. Application caching can avoid a model call entirely. Measure both separately. Do not pad prompts to get a higher cache-hit percentage.

### Tool design

The runtime agents currently expose no registered function tools in `agents.py`; evidence execution is controller-driven. Adding tools indiscriminately would add schemas and request turns.

For broad unfamiliar datasets, consider a small bounded interface such as `get_claims(ids)`, `get_source_fields(paths)`, or `execute_query(typed_spec)`. Most familiar tasks should receive their needed projection directly. Batch retrieval requests, bound result size, validate query capabilities, and prevent arbitrary unsupported calculation or reference access. A vector database is not needed to resolve exact evidence IDs; use keyed lookup first. Introduce semantic retrieval only if schema matching or open-ended evidence discovery demonstrates a need.

### Concurrency

`generate_all_async()` currently awaits each example/variant/repetition in nested loops, so it is asynchronous in interface but sequential in scheduling. It also invokes synchronous callable/command backends directly. Add bounded cross-report concurrency with request/token-rate controls, retries with backoff for transient provider errors, and thread/process offloading for blocking backends where appropriate.

Parallelize independent analytical tasks and compact claim-review batches only after dependencies are known. A writer still depends on its selected evidence; starting speculative writers or multiple full reviewers can spend more tokens. Concurrency improves throughput and sometimes latency, not token count by itself.

Use unique run/attempt IDs before enabling concurrent same-input runs. Current IDs are a timestamp to second precision plus a source fingerprint prefix, so identical input launched in the same second and output root can collide. Centralize result writes or use per-run shards and deterministic aggregation.

## 7. Python performance and structural cleanup

Two local deterministic profiles, excluding imports and model calls, took approximately 0.186 seconds for the 20-row weather demo and 0.297 seconds for `inputs/basketball_data.json`. These are diagnostic samples with profiling overhead, not production benchmarks. The weather result was approved with warnings; the event input required human review. Therefore the fast deterministic event run is **not** evidence of equivalent report quality.

Both runs made three calls to `deterministic_audit()` and 49 `save_json()` calls. JSON serialization/artifact saving and repeated auditing were prominent locally. In the historical event cohort, model work still dominates the minutes-long end-to-end time.

| Area | Concrete opportunity | Priority/qualification |
|---|---|---|
| `workflow.py:audit_once` | Reuse the pre-patch deterministic audit when no support-map patch was applied; invalidate on actual content/support changes | Useful local optimization; preserve differences in revision metadata |
| `workflow.py` quality and final checks | Reuse coverage/genre/number/entity results for identical report versions | Cache by content, evidence, contract, and validator version |
| `audit.py`, `agents.py` validators | Build fact/evidence indexes and flattened numeric/entity data once per immutable ledger | Avoid rebuilding lookups inside record loops and revalidating dictionaries repeatedly |
| `agents.py:build_evidence_agent` | Avoid full-set, per-candidate, then full-set validation of the same data when one structured validation pass can return per-item results | Preserve partial valid-output recovery |
| `data.py:profile_data` | Reuse normalized/hashable series; avoid mapping `safe_hashable` twice and repeated duplicate-count preparation | More relevant for large tabular inputs |
| `analytics.py:descriptive_analysis` | Reuse profile statistics/duplicate results with the same scope | Do not reuse full-data counts for sampled analysis accidentally |
| `analytics.py:association_analysis` | Convert numeric columns once and reuse pairwise computation; bound candidates by task relevance | Preserve pairwise missing-value handling, sample counts, thresholds, and stable tie order |
| `analytics.py` predictive/forecast paths | Lazy-import heavy estimators; avoid unnecessary analysis routes; parallelize independent fits if worthwhile | Benchmark wide/large tables separately; prevent CPU oversubscription |
| `data.py:load_data` | Avoid unnecessary whole-frame copies; selective column/sheet loading for an explicitly scoped task | Keep exact results and data ownership semantics |
| `ArtifactStore` | Production trace mode with canonical artifacts and references/deltas; full research mode when requested | Saving less JSON will not itself reduce model tokens |
| Evaluation generation | Unify duplicated sync/async result materialization and append/shard results instead of rewriting all accumulated records after every run | Improves maintenance and batch I/O scaling |
| Evaluation models | Reuse existing HHEM lazy loading and persistent AlignScore worker; batch compatible scoring requests | These reuse mechanisms already exist; do not claim they are absent |
| Initialization | Lazy-build only agents needed by the route; reuse compatible clients in a service | Small versus model-call savings; useful for repeated short tasks |

The core package has about 34,000 lines; `audit.py` alone has 9,892. File size is a maintainability issue, not a direct token bill. Split orchestration, evidence indexing, claim checking, genre policy, repair, and persistence along their actual responsibilities. Extract shared normalization and relation rules so prompt instructions, validators, and deterministic renderers derive from one policy instead of accumulating independent exceptions.

`sports_game_report_requested()` and `profile_supports_sports_game_report()` have definitions but no other references in the scanned runtime/tests. Treat them as cleanup candidates after checking notebooks, external callers, and API compatibility. Deleting dormant functions produces negligible runtime/token savings; prioritize active paths. The separate `experiments/llm_only_pipeline` is not invoked by the production workflow, so deleting it would not speed generation. Preserve experimental records and learn from its compact serialization and explicit claim bounds.

Do not equate Ruff cleanup with performance optimization. Do not remove protected artifacts, evaluation modules, numerical validation, or provenance simply because they make the repository large.

## 8. Implementation sequence

Each phase should be a reviewable change with its own measured contribution. Avoid a simultaneous framework/model/prompt/schema rewrite that makes failures impossible to attribute.

| Phase | Deliverables | Exit evidence |
|---|---|---|
| 0: trustworthy baseline | Structured request usage; failed-attempt accounting; prompt/response size and review coverage; pinned environment/config snapshots; unique attempt IDs | Per-request totals reconcile with provider records where available; no silent missing failure usage |
| 1: remove obvious waste | Valid compact prompt compiler; complete constraints; role-specific reasoning/output policy; provider adapter fixtures; prompt/validator budget consistency | No cut JSON; no invisible required IDs; token reduction and retry outcomes measured on development cases |
| 2: efficient short route | Dedicated minimal writer prompt/schema; exact extraction and surface-form checks | Required attributes/triples retained; fluency and semantic fidelity meet acceptance margins |
| 3: bounded evidence architecture | Canonical claim/evidence store; projection compiler; one selection/synthesis pass; typed derived operations | Same evidence and source isolation; fewer repeated tokens; no loss of mandatory coverage |
| 4: focused verification | Claim-origin policy; compact independent critic; typed retry errors; targeted patching; honest verification labels | Critical swapped-entity/unit/direction errors caught; no correctness gain manufactured by default approval |
| 5: quality reinvestment | Selective stronger model/effort; routing calibration; optional second opinion within reserved budget | Better independently judged quality at equal or lower total token budget |
| 6: service/batch performance | Content/version caches; bounded concurrency; selective profiling/import improvements; resumable stage execution | Warm/cold latency, p95 latency, throughput, memory, and error-rate improvements measured separately |

Start with phases 0–2. They have the strongest direct evidence, relatively limited architectural risk, and make later comparisons reliable. Phases 3–5 are the larger redesign that can produce the drastic gain.

## 9. Evaluation that can prove the improvement

The existing 212 passing tests are useful regressions, but they do not establish live-provider factuality, token efficiency, or prose quality. The one-example ablation contains provider failures and changed content lengths, so it cannot decide which roles should be deleted universally.

Use a development set across short records, highlighted tables, familiar and renamed/nested events, statistical reports, wide tables, and large inputs. Include ambiguous units, ties, missing data, conflicting fields, excluded references, irrelevant metadata, and explicit all-facts coverage. The 25 historic holdout cases inspected here are now historical diagnostic evidence; do not tune against them and later describe them as a new untouched test. Freeze a new evaluation set after design selection.

### Controlled experiments

Compare the following incremental variants with the same input contracts and coverage requirements:

- Current architecture with corrected telemetry.
- Compact valid payloads only.
- Role-specific reasoning and output limits only.
- Short-form specialization.
- One bounded selection/synthesis stage.
- Targeted semantic verification and delta repair.
- Combined efficient route.
- Combined quality route with selective stronger model/effort.

Use at least three repetitions initially to expose provider variability, then size the final evaluation for the desired detectable quality difference. Three repeats do not by themselves make a small corpus statistically conclusive. Pair comparisons by input and report dataset/task strata; use item-level or hierarchical bootstrap intervals rather than treating repeated generations as unrelated examples.

Compare both fixed-token budgets and the full quality/latency/cost trade-off across budgets. Count failed attempts in consumption and reliability, even if a repeat eventually succeeds. Avoid judging quality only on successfully released outputs: report abstentions, blocked reports, missing content, and fallbacks alongside release precision.

### Measures

| Dimension | Measures |
|---|---|
| Factuality | Independently source-checked error rate; severity; swapped subject/value, unit, scope, chronology, relation, and causal errors |
| Coverage | Required-slot recall; supported distinct claims; entity/team balance; omissions of mandatory source attributes |
| Writing | Blinded coherence, relevance, concision, repetition, task fulfillment, and usefulness judgments |
| Grounding | Provenance validity, exact operand validity, semantic review coverage, unsupported additions, truthful verification method |
| Tokens/cost | Total input/output including reasoning and failures; cached/uncached input; tokens per accepted supported claim; actual price-weighted cost |
| Performance | p50/p95 end-to-end latency, time by stage, time to first draft, reports/minute under controlled load, memory |
| Reliability | Schema/transport errors, retry counts, fallback rate, review exhaustion, successful complete reports, correct abstentions |

Reference overlap metrics remain secondary diagnostics: a shorter report can look cheaper while omitting useful content, and a fluent report can score well while getting a relation wrong. Preserve existing scoring for comparability; version any new source-context representation or judge protocol.

Proposed promotion gates: zero violations of source isolation or provenance validity; no increase in serious factual errors within an agreed statistical margin; mandatory coverage non-inferiority; writing-quality non-inferiority for the efficiency route or improvement for the quality route; and a predeclared token/latency reduction target. A practical first milestone is a 50% reduction in event tokens without quality regression; treat 80–95% as the subsequent architecture goal. Set the final numerical quality margins before evaluating the new holdout.

## 10. Decisions to defer

Model distillation or fine-tuning may become useful once compact task contracts and enough high-quality examples exist. It is premature while prompts are being truncated and verification behavior is unstable. A complete migration away from PydanticAI is similarly unproven: keep the typed contracts and replace adapters only where measurements identify a specific issue.

A universal agent debate, more tool turns, a vector store for exact IDs, speculative parallel writers, or a large model for every role can increase cost without addressing the observed defects. Test them only against the compact baseline and a concrete residual failure class.

The central design commitment is to keep complete, exact evidence in the system while making each model request small and purpose-specific. That is the strongest route to both substantially lower consumption and better performance within the same budget.
