---
title: "S1702 Group 1700 Cat B — LLM Call Telemetry (LLMCallEvent) Child Audit"
status: active (Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-03 on arc pin pa-e7fbacc996b34b44 [S1600/S1700/S1701 parent-scoping precedent: arc pin doubles as SIGN pin; fresh SIGN isolation pin pa-c3927ab78c52479a minted per playbook §15 was routed-around by tools/pa_local.sh:128 wrapper hard-code — retired at S1702 close per §16]; F1-F3 folds landed pre-commit; Chris ratified P2 kickoff via "Start research group 1702" short command per playbook §21 short-command intent — interpreted as S1702 child under Group 1700 per parent D72 P2 slot)
authority: child-audit for Category B per parent §5 D72 sequence + SECOND child under Group 1700; applies D48 preemptive stability-probe gate 19th arm on arc pin per playbook §15 stage-table child row
category: child_audit
session: 1702
child_slot: P2
domain_slug: observability
research_group: 1700
date: 2026-07-03
head_commit: 2bb196e8
parent_scoping: 1700_observability_domain_scoping.md (§3.B Cat B lines 429-471)
sibling_prior: 1701_observability_cat_a_celery_task_event_audit.md (Cat A CeleryTaskEvent; SIGN-with-edits at High confidence 2026-07-03)
delegates_to: []  # child audits do not delegate; xx99 resolves posture
promotes_to: 1799_observability_canonical_summary.md (D74 axis evidence contribution; F5 correlation-primitives box execution_id row)
---

# S1702 Group 1700 Cat B — LLMCallEvent Child Audit

> **Second child audit under Group 1700 (Observability arc).** Playbook §11.2 20-section template SECOND application under Group 1700 arc (first was S1701 Cat A). 6-parallel-Explore sweep + parent-Claude verifier-loop applied pre-Explore and post-Explore. Rigby SIGN cycle 1 pending on fresh SIGN pin `pa-c3927ab78c52479a` (routed-around by wrapper; arc pin `pa-e7fbacc996b34b44` receives the SIGN traffic per S1600/S1700/S1701 precedent).

---

## 1. Executive Summary

**Cat B (LLM Call Telemetry) owns the LLMCallEvent model at `core/models_llm_telemetry.py:30-115` and the S1098 `llm_call_wrapper` at `core/services/llm_call_wrapper.py` (public API: `llm_call_span` sync ctx-mgr + `llm_call_async` async wrapper).** Per parent §3.B boundary rule, Cat B stops at the wrapper's post-call hook and does NOT own tool-call telemetry (Cat D) or agent-outcome telemetry (Cat C).

**Nine load-bearing findings drive this audit's §14/§15/§17/§19 sections and the D74 axis contribution to xx99:**

- **F1 (CRITICAL, §17) — Multi-model LLM telemetry duplication.** `LLMCallEvent` (S1098, `core/models_llm_telemetry.py:30-115`, 16 fields, NO `cost`/`total_tokens`/`latency_ms`) coexists at HEAD with `LLMCallLog` (S697, `core/models_llm_routing.py:297-362`, HAS `cost` [line 335], `total_tokens` [line 331], `latency_ms` [line 332]) AND a **third store `CostTracking` at `core/models_unified_system.py:6665`** (surfaced by Rigby SIGN cycle 1 F1 fold; full overlap not yet triangulated). Multiple actively-written LLM-cost surfaces; different consumers. This is the largest single dedup candidate for Cat B and reframes parent scoping §3.B's field-list drift.
- **F2 (CRITICAL, §14) — PA agentic loop uncovered.** `core/services/unified_pa_entrypoint.py` + `core/llm_enforcer.py` both import **zero** wrapper symbols (verified grep). PA GPT-5.2 function-calling agentic loop generates 1–20 LLM calls per user message and writes **zero LLMCallEvent rows**. This is the largest single coverage gap in Cat B's telemetry surface.
- **F3 (MEDIUM, §14, latent) — `_extract_usage` provider-shape gap.** Wrapper's `_extract_usage` at `llm_call_wrapper.py:126-159` handles OpenAI (`prompt_tokens`/`completion_tokens`) + Anthropic (`input_tokens`/`output_tokens`) + generic dict shape. Gemini uses `prompt_token_count`/`candidates_token_count` (`llm_provider_registry.py:847-848`); Ollama uses `prompt_eval_count`/`eval_count` (`llm_provider_registry.py:969-970`). LATENT because **all 23 production wrapper call sites at HEAD use `provider='openai'` or `provider='anthropic'`**; drift becomes CRITICAL if any Gemini/Ollama caller adopts the wrapper.
- **F4 (HIGH, §15) — No date-based retention for LLMCallEvent.** `_impl_cleanup_stale_llm_calls` at `core/tasks_agents.py:1659-` sweeps stuck STARTED rows on a 10-minute cadence (S1221 P2 Tier 2 watchdog). No analog to Cat A's 30-day `CELERY_TASK_EVENT_RETENTION_DAYS` retention exists. LLMCallEvent rows accumulate unbounded; LLMCallLog (F1 sibling) does have 30-day retention via `cleanup_llm_call_logs` at `core/tasks.py:4408`. Row-count monitoring absent.
- **F5 (MODERATE, §13) — Wrapper adoption is 23 production sites across 8 files.** Verified inventory: content_writer_agent (3), code_review_agent (5), devops_agent (5), tasks_initiatives (5), market_intelligence_agent (2), campaign_orchestrator_agent (1), thinking_agent (1 async), curated_action_card_generator (1). BaseAgent + agent_router import only `LLMCallCancelled` exception (catch blocks; no wrapper span usage). PA path uncovered (F2). Adoption is **partial** — not universal — and skewed toward writer/reviewer agents.
- **F6 (MEDIUM, §14) — Parent scoping §3.B field list is drift.** Parent claims `model, prompt_tokens, completion_tokens, total_tokens, latency_ms, cost, execution_id, success, error`. Runtime LLMCallEvent has `call_id, execution_id, agent_name, provider, model, status (enum), started_at, finished_at, duration_ms, tokens_in, tokens_out, retry_count, error_type, error_message, cancelled, metadata`. The parent's claimed field names actually match **LLMCallLog** (F1 sibling model) — the drift is definitional confusion between the two models. §7.4 anchor-update owed by xx99.
- **F7 (MEDIUM, §15) — PR #3 cancel is PARTIAL.** Wrapper docstring at `llm_call_wrapper.py:18-21` explicitly notes "provider adapters do not yet abort in-flight sockets." Entry-point cancel check (`_check_cancel` at `llm_call_wrapper.py:227-270`) works via CancelToken + `cancel_registry.is_execution_cancelled`; in-flight LLM socket abort NOT implemented. Cancel signal races with httpx read timeout.
- **F8 (LOW, §15) — PR #4 nested dispatch budget NOT SHIPPED.** Module docstring at `llm_call_wrapper.py:14` promises "Nested dispatch budget (parent token propagates to children)". Zero code exists at HEAD. Documented deferred scope; not a surprise regression.
- **F9 (D74 axis contribution, §9) — execution_id is agent-execution-span, non-FK'd, coverage-gapped.** `LLMCallEvent.execution_id` is UUIDField(null=True, db_index=True) at `models_llm_telemetry.py:54-60`. Docstring at :56-60 explicitly states no FK "so telemetry survives AgentExecution row deletion" and "NULL for detached calls (tests, scripts, PA flows with no execution record)." **Cat B contribution to D74 axis**: `call_id` is Cat B's PK singleton primitive at the LLM-call level; `execution_id` is a Cat C-owned spine primitive that Cat B tags onto its own rows. **Cat B does NOT own a cross-model spine analog to Cat A's `task_id` — no downstream model carries `llm_call_id` or `llm_execution_id` as scalar reference (verified grep, 0 hits).** Cross-cat correlation to Cat A goes via 3-hop chain: `execution_id → AgentExecution.id → AgentExecution.input_data['celery_task_id'] → CeleryTaskEvent.task_id` (JSON-path, unindexed per S1701 §9).

**Coverage-completeness posture.** For the 23 production wrapper call sites, LLMCallEvent coverage is complete (best-effort save at `llm_call_wrapper.py:162-176` swallows DB errors but writes row on the happy path). For the **PA path**, LLMCallEvent coverage is **zero** (F2). For BaseAgent's `_call_openai` synchronous path (S1219 P1 Tier 1 total-request bound at `base_agent.py:58-124`), wrapper adoption status is UNKNOWN — grep shows only `LLMCallCancelled` import at `base_agent.py:4723`, not span usage. For the 6 registered providers, wrapper adoption is skewed to OpenAI + Anthropic; Gemini/Ollama shapes latent-broken (F3).

**Boundary posture (§16).** Six boundary-violation candidates all classified LEGITIMATE — no cross-cat writes from wrapper, no direct `LLMCallEvent.objects.create` outside wrapper (`_create_event_safe`), no cross-cat reads inside wrapper. Cancel-registry integration is a clean cross-cutting service dependency (not a Cat A/C/D/E model read). No Cat B analog to S1219 P1 `on_agent_task_failure_bridge` cross-cat exception exists.

**Maturity STABLE for the covered surface + PARTIAL overall + Risk MEDIUM-HIGH.** Wrapper design is coherent (best-effort telemetry, cancel-registry integration, error classification into 7 buckets); tests exist (`test_llm_call_wrapper.py` + `test_cancel_token_e2e.py`); CI lint enforces wrapper adoption for direct SDK calls (PR #2 SHIPPED at `.github/workflows/check-llm-sdk.yml` enforce mode per S1222 P5). PARTIAL because F1 dedup gap + F2 PA coverage gap + F4 retention gap + F5 partial adoption combine to make Cat B **not yet a canonical LLM-call spine**.

**§19 R1 (HIGH) — F2 PA path coverage** and **R2 (HIGH) — F1 dedup posture between LLMCallEvent and LLMCallLog** are the two most consequential follow-ons owed to xx99 (S1799). Both are Cat B-scoped but downstream posture decisions belong to xx99 per D73 posture-framing discipline.

---

## 2. Domain Purpose

**Q1 + Q2 from §9: What is Cat B, and why does it exist?**

Cat B (LLM Call Telemetry) is the observability layer for LLM API invocations. Its purpose is to answer three questions:

1. **What LLM calls happened?** — per-call provenance (call_id, provider, model, agent_name, execution_id, started_at, finished_at, duration_ms, tokens_in, tokens_out, error_type, cancelled). One LLMCallEvent row per invocation.
2. **What did they cost?** — usage counting via tokens_in + tokens_out. Cost dollar value is **not persisted** on LLMCallEvent (F1 + T-1 debt); computed downstream via price-table lookup on tokens.
3. **What went wrong when they didn't complete?** — 4-state lifecycle (STARTED → SUCCESS | FAILED | CANCELLED) + 8-value error_type enum (`''`, `timeout`, `rate_limit`, `auth`, `api_error`, `client_error`, `cancelled`, `unknown`) + `error_message` TextField (2000-char truncated) + `cancelled` BooleanField.

Cat B exists because before S1098, direct provider SDK calls at agent boundaries produced no consistent audit trail — LLM cost, latency, and failure taxonomy were operator lore, not queryable data. S1098 introduced the wrapper pattern (`llm_call_span` sync ctx-mgr + `llm_call_async` async wrapper) that brackets every LLM call with mandatory START row + terminal SUCCESS/FAILED/CANCELLED row. PR #2 of the S1098 4-PR arc introduced CI lint enforcement at `tools/check_direct_llm_calls.py` + `.github/workflows/check-llm-sdk.yml` to forbid direct SDK calls outside the wrapper (promoted from `--warn-only` to enforce mode per S1222 P5 audit).

**What Cat B does NOT own** (parent §3.B boundary rule):

- **Cat D (ToolCallRecord) — tool-call telemetry.** LLM calls made from inside a tool invocation remain Cat B per parent §3.B accounting rule + §3.D F3 fold; Cat D never attempts to own LLM cost or token accounting. Dedup between Cat B and Cat D happens via correlation keys (execution_id + trace_id + tool_call_id), not by redefining ownership.
- **Cat C (AgentExecution) — agent-execution outcome.** Cat C owns `agent.route()` boundary intent + outcome; Cat B owns the LLM calls that happen inside that boundary. `LLMCallEvent.execution_id` correlates to `AgentExecution.id` implicitly (no FK) per F9.
- **Cat A (CeleryTaskEvent) — Celery task lifecycle.** Cat B does not read or write Cat A telemetry. Cross-cat correlation Cat B ↔ Cat A is via 3-hop Cat C intermediary (F9).
- **Provider client factories.** `get_openai_client()` + `get_anthropic_client()` factories at `core/services/openai_client_factory.py` + `core/services/anthropic_client_factory.py` own timeout / retry / kwargs enforcement per memory rules `feedback_openai_client_factory.md` + `feedback_anthropic_client_factory.md`. Wrapper wraps the SDK call; factory constructs the client. Different concerns.
- **Provider registry** at `core/services/llm_provider_registry.py` (1146 lines, 6 providers registered). Registry owns provider adapter shape + routing decisions; Cat B does not.

---

## 3. Canonical Entry Points

**Q3: File:line for the entry points that write / read LLMCallEvent.**

### Writer entry points (in priority order)

| Rank | Entry point | File:Line | Semantics |
|---|---|---|---|
| 1 | `llm_call_span` (sync context manager) | `core/services/llm_call_wrapper.py:272-367` | Primary writer for sync LLM calls. Callers enter ctxmgr → wrapper creates STARTED row → caller invokes SDK inside block → attaches response → wrapper writes terminal row (SUCCESS / FAILED / CANCELLED). 22 of 23 production call sites use this. |
| 2 | `llm_call_async` (async wrapper) | `core/services/llm_call_wrapper.py:370-456` | Async twin. Accepts `fn` callable + args + kwargs; runs fn (sync or async) and wraps with sync_to_async ORM writes. Only production async caller: `thinking_agent.py:670` (`ThinkingAgent._call_llm`). |
| 3 | `_create_event_safe` (internal) | `core/services/llm_call_wrapper.py:179-209` | Lazy-imports `LLMCallEvent` (line 194) inside try-except. Writes STARTED row via `objects.create(status='STARTED', ...)`. Returns None on any exception (best-effort telemetry). Only called from wrapper's two public entry points. |
| 4 | `_save_event_safe` (internal) | `core/services/llm_call_wrapper.py:162-176` | Updates event row with terminal fields. Swallows all exceptions (best-effort). Called from success/failure/cancel branches of both public entry points. |
| 5 | `_impl_cleanup_stale_llm_calls` (writer via `update`) | `core/tasks_agents.py:1659-1720` | 10-minute cadence beat sweeper (S1221 P2 Tier 2 watchdog). Filters `LLMCallEvent.objects.filter(status='STARTED', started_at__lt=now-10min)` and calls `.update(status='FAILED', error_type='timeout', error_message='watchdog_cleanup')`. Cross-cat exception NONE — pure Cat B write. |

### Non-wrapper writers (legitimate exceptions to "wrapper owns writes")

**None found.** Grep for `LLMCallEvent.objects.create` outside `llm_call_wrapper.py` returns zero direct-write sites. Grep for `LLMCallEvent.objects.filter(...).update(...)` returns only the S1221 P2 watchdog at `tasks_agents.py:1721`. Cat B write-boundary discipline is intact.

### Reader entry points

| Reader | File:Line | Cardinality | Purpose |
|---|---|---|---|
| PA `cost_telemetry_tool` handler | `core/services/td_handlers_agents.py:3664-3835` | **⚠ Read of LLMCallLog, NOT LLMCallEvent** — see F1 | PA tool schema at `pa_tool_schemas.py:509-541`; registered at `tool_dispatcher.py:352`. Actions: `summary` / `top_agents` / `recent_calls`. Confirmed via Explore 3 verifier read: imports `from core.models_llm_routing import LLMCallLog` at :3676. |
| `_impl_cleanup_stale_llm_calls` | `core/tasks_agents.py:1697-1701` | Filter + count | Reads LLMCallEvent to find stuck STARTED rows. |
| Test fixtures | `core/tests/test_llm_call_wrapper.py` (10+ read sites) + `core/tests/test_rigby_mission_delegation.py` (fixture reads) | Test-scoped | Not production consumers. |
| `core/employees/status.py` | (grep hit — imports LLMCallEvent) | UNKNOWN read/write intent | Requires additional read to classify. |
| `core/signals/rigby_delegation_signals.py` | (grep hit — imports LLMCallEvent) | UNKNOWN read/write intent | Requires additional read to classify. |

**Reader gap (§18 candidate):** No REST endpoint reads LLMCallEvent directly. No WebSocket consumer reads LLMCallEvent. The primary consumer surface (`cost_telemetry_tool`) reads **LLMCallLog** (F1 sibling model), not LLMCallEvent. Cat B rows are **written but under-consumed** — a write-only-forgotten pattern candidate.

### Retention entry point

`_impl_cleanup_stale_llm_calls` (`core/tasks_agents.py:1659-1720`) is the **only** cleanup task for LLMCallEvent, and it is NOT a retention task — it is a stuck-STARTED-row watchdog (10-min threshold). **No date-based retention exists** (F4 debt).

Sibling model `LLMCallLog` has retention via `cleanup_llm_call_logs` at `core/tasks.py:4405-4417`: `LLMCallLog.objects.filter(created_at__lt=cutoff).delete()` with `LLM_CALL_LOG_RETENTION_DAYS` env default 30 days. Cat B has no analog.

---

## 4. Major Models

**Q4 + Q5 + Q6 + Q7: Models owned, FK graph, retention, overlaps.**

### `LLMCallEvent` — `core/models_llm_telemetry.py:30-115`

Introduced **Session 1098** (migration `core/migrations/0334_llmcallevent.py`; no subsequent LLMCallEvent-specific migrations at HEAD). Session-1098 module docstring cites 4-PR arc plan (PR #1 telemetry SHIPPED, PR #2 CI lint SHIPPED, PR #3 cancel PARTIAL, PR #4 nested budget NOT SHIPPED).

**Full field inventory (16 persistent fields + PK):**

| Field | Line | Type | Nullability | Index | Default | Purpose |
|---|---|---|---|---|---|---|
| `call_id` | :51-53 | UUIDField (PK, editable=False) | N | PK | `uuid.uuid4` | Primary key (per-call singleton). |
| `execution_id` | :54-61 | UUIDField, db_index=True | Y (null=True, blank=True) | Y | NULL | Implicit correlation to `AgentExecution.id`. **Explicitly NOT an FK** per docstring at :56-60 ("so telemetry survives AgentExecution row deletion" + "NULL for detached calls"). |
| `agent_name` | :62-65 | CharField(120), db_index=True | Y (blank='') | Y | `''` | Dashboards filter here (S1169 dimension). |
| `provider` | :66 | CharField(50) | Y (blank='') | N | `''` | LLM provider (`openai`, `anthropic`, `deepseek`, `together`, `gemini`, `ollama`). |
| `model` | :67 | CharField(120) | Y (blank='') | N | `''` | Model identifier (e.g., `gpt-5-mini`, `claude-opus-4-7`). |
| `status` | :69-72 | CharField(20, choices=STATUS_CHOICES), db_index=True | N | Y | `'STARTED'` | 4-state enum: `STARTED`, `SUCCESS`, `FAILED`, `CANCELLED`. |
| `started_at` | :73 | DateTimeField, db_index=True | N | Y | `timezone.now` | Call start; retention key candidate. |
| `finished_at` | :74 | DateTimeField | Y (null=True, blank=True) | N | NULL | Terminal-row timestamp. |
| `duration_ms` | :75 | IntegerField | Y (null=True, blank=True) | N | NULL | `perf_counter()` elapsed × 1000. |
| `tokens_in` | :77 | IntegerField | Y | N | NULL | Prompt/input token count via `_extract_usage` (F3 provider-shape gap). |
| `tokens_out` | :78 | IntegerField | Y | N | NULL | Completion/output token count. |
| `retry_count` | :79 | IntegerField | N | N | `0` | Retry attempts. |
| `error_type` | :81-84 | CharField(50, choices=ERROR_TYPE_CHOICES) | Y (blank='') | N | `''` | 8-value enum: `''`, `timeout`, `rate_limit`, `auth`, `api_error`, `client_error`, `cancelled`, `unknown`. |
| `error_message` | :85 | TextField | Y (blank='') | N | `''` | Truncated at 2000 chars in wrapper (`llm_call_wrapper.py:345, 356, 433, 443`). |
| `cancelled` | :86 | BooleanField, db_index=True | N | Y | `False` | Cancellation flag (redundant with `status='CANCELLED'` but indexed separately). |
| `metadata` | :91 | JSONField | Y (blank={}) | N | `{}` | Freeform caller context (`task_id`, `parent_trace_id`, provider-specific options). |

**Meta (lines 93-109):**
- `app_label='core'`
- `ordering=['-started_at']`
- **3 declared indexes:**
  - `llm_call_exec_time` on `(execution_id, -started_at)` — execution-scoped time-window queries
  - `llm_call_provider_time` on `(provider, -started_at)` — per-provider aggregations
  - `llm_call_time_status` on `(-started_at, status)` — time-window status filters

**No unique constraints beyond PK.** No `unique_together`. No `constraints=[UniqueConstraint(...)]`.

### Migration lineage

- **`core/migrations/0334_llmcallevent.py`** (Session 1098) — CreateModel + AddIndex ×3. Only LLMCallEvent-specific migration at HEAD.
- **`core/migrations/0299_llmcalllog_trace_id.py`** — belongs to `LLMCallLog` (F1 sibling model), not LLMCallEvent. Confirms LLMCallLog predates LLMCallEvent by 35 migration steps.

### FK graph

- **Outbound FKs from LLMCallEvent:** ZERO. `execution_id` is a plain UUIDField, not a ForeignKey (intentional per docstring).
- **Inbound FKs to LLMCallEvent:** ZERO. Grep for FK targets pointing at `LLMCallEvent` or `models_llm_telemetry.LLMCallEvent` returns zero hits.
- **Scalar downstream references (per Cat A §9 analog):** ZERO. No model carries `llm_call_id` or `llm_execution_id` as CharField/UUIDField reference. Verified grep, 0 hits. (Cat A has 8 such references to `celery_task_id`.)
- **Cross-cat correlation via `execution_id`:** `execution_id` implicitly points at `AgentExecution.id`. Which AgentExecution class? Parent §3.C notes 3 classes exist:
  - `intelligence/models/agent_execution.py:11` (ActionPlan-scoped, canonical per S1273 §3.25)
  - `intelligence/models.py:587` (duplicate body, likely re-export)
  - `core/models_unified_system.py:882` (DEPRECATED per docstring, stale docstring points at `agents.models` which is a compatibility shim per S391)
  
  Which class does the router actually instantiate? P3 (Cat C, S1703) resolves. For P2 purposes: `LLMCallEvent.execution_id` **inherits the class ambiguity** — a UUID matches whichever AgentExecution.id was created upstream by `agent_router._create_execution_record` (per Explore 4).

### Overlap flags vs Cat A/C/D/E/F + F1 SIBLING MODEL

**F1 — `LLMCallLog` at `core/models_llm_routing.py:297-362` is a second LLM telemetry model at HEAD.** Verified via direct read (verifier-loop). Selected fields:

| LLMCallLog field | Line | LLMCallEvent equivalent | Note |
|---|---|---|---|
| `total_tokens` (IntegerField) | :331 | *missing* on LLMCallEvent | Explicit sum column. |
| `latency_ms` (IntegerField) | :332 | `duration_ms` on LLMCallEvent | Different name; same semantics. |
| `cost` (DecimalField `max_digits=10, decimal_places=6`) | :335 | *missing* on LLMCallEvent | Persisted cost dollar value. |
| `trace_id` (CharField, db_index=True) | (from S697 + migration 0299) | *missing* on LLMCallEvent | S697 trace correlation. |
| `agent_name` (CharField) | (implicit) | Present on LLMCallEvent | Duplicated column. |
| `provider` / `model` | (implicit) | Present on LLMCallEvent | Duplicated columns. |

**Consequence:** Parent scoping §3.B lines 440-442 field list (`model, prompt_tokens, completion_tokens, total_tokens, latency_ms, cost, execution_id, success, error`) actually describes **LLMCallLog** fields, not LLMCallEvent. The parent scoping author was reading LLMCallLog schema and mislabeled it as LLMCallEvent. This is F6 drift; the root cause is F1 (two models exist).

**Cross-cat overlap:**
- **Cat A (CeleryTaskEvent):** No overlap. Different scope (Cat A = Celery task boundary; Cat B = LLM call boundary). Correlation is 3-hop via Cat C.
- **Cat C (AgentExecution):** Denormalization candidate. Does AgentExecution carry `llm_call_count` or `total_tokens` for the agent's LLM usage? Explore 1 verified: NO `llm_call_count`, NO `total_tokens` on any of the 3 AgentExecution classes. Aggregation, if desired, is per-execution ORM sum over `LLMCallEvent WHERE execution_id = ?`.
- **Cat D (ToolCallRecord):** Correlation via `execution_id + trace_id + tool_call_id` per parent F3 fold. **ToolCallRecord has `trace_id` + `conversation_id` + `agent_name` + `tool_name` but NO `execution_id` or `tool_call_id` field** (Explore 4 verified). Accounting rule cites `tool_call_id` for dedup but schema has no column. Correlation is **incomplete** — LLM calls made from inside tools cannot be linked back to specific tool invocations at schema level.
- **Cat E (OpsRunEvent):** `OpsRun` + `OpsRunEvent` (`core/models_ops_runs.py:11-117`) have `mission_id` but no `execution_id`. MissionRunner (`core/employees/mission_runner.py`) does NOT thread `mission_id` into `llm_call_span` metadata (grep verified). Missions cannot attribute LLM cost.
- **Cat F (Heartbeat):** No interaction. Passive telemetry sinks don't cross.

---

## 5. Major Services

**Q8 + Q9: Services owned, dependency chains.**

### `core/services/llm_call_wrapper.py` (465 lines) — Cat B production surface

Public API:
- `llm_call_span` sync context manager at `:272-367`
- `llm_call_async` async wrapper at `:370-456`
- `LLMCallCancelled` exception at `:49-55`
- `CancelToken` dataclass at `:58-74`

Internal helpers:
- `_coerce_execution_id` at `:83-92` — accepts UUID / str / None, returns UUID or None, never raises
- `_classify_error` at `:95-123` — maps SDK exceptions to 7 buckets (`timeout`, `rate_limit`, `auth`, `client_error`, `api_error`, `cancelled`, `unknown`)
- `_extract_usage` at `:126-159` — best-effort token extraction (OpenAI + Anthropic + generic dict; **F3 latent gap for Gemini/Ollama shapes**)
- `_check_cancel` at `:227-270` — direct token check + registry check (`cancel_registry.is_execution_cancelled`) + `mark_observed` on cancel hit
- `_save_event_safe` at `:162-176` — best-effort ORM save (swallows Exception)
- `_create_event_safe` at `:179-209` — best-effort ORM create (swallows Exception, returns None on failure)
- `_Span` at `:212-221` — handle returned by `llm_call_span`; holds `call_id` + `response`

Key contracts:
- **Best-effort telemetry** (module docstring lines 26-28): "Telemetry is best-effort: a failing LLMCallEvent save must never mask the real LLM response or exception."
- **Model kwarg naming asymmetry** (docstring at :305-308 + :387-392): sync ctx-mgr uses `model=`; async wrapper uses `model_name=` to avoid collision with kwargs forwarded to `fn`.
- **Response attachment pattern** (sync only): caller must call `span.attach_response(response)` inside the block for `_extract_usage` to fire on exit. Async wrapper auto-captures `result`.

Cross-domain imports:
- Top-level: stdlib (`asyncio`, `logging`, `time`, `uuid`, `contextlib`, `dataclasses`, `typing`) + `django.utils.timezone`. Clean.
- **Lazy imports inside functions:**
  - `LLMCallEvent` at `:194` inside `_create_event_safe` (avoid app-loading order issues)
  - `is_execution_cancelled` + `mark_observed` at `:252-253` inside `_check_cancel` (avoid circular + fail-graceful if registry unavailable per `:265-269`)
  - `sync_to_async` at `:394` inside `llm_call_async` (defer asgiref dependency)

God-service check: 465 lines is well under 3000 threshold. No cross-domain imports at top level. Clean encapsulation.

### `core/services/cancel_registry.py` (~398 lines per Explore 2) — Cat B dependency (support service)

Redis-backed execution cancel state + ancestor walk. Wrapper consults at `_check_cancel`. Public API: `request_execution_cancel`, `is_execution_cancelled` (with ancestor walk capped at `_MAX_ANCESTOR_DEPTH = 25`), `mark_observed`, `get_cancel_state`, `clear_execution_cancel`. 24h Redis TTL with in-memory fallback. Idempotent request semantics.

Not owned by Cat B — cross-cutting service. Boundary: registry is agnostic to LLMCallEvent; wrapper is the caller. LEGITIMATE dependency per §16.

### `core/services/llm_provider_registry.py` (~1146 lines per Explore 2) — 6-provider adapter registry

Provider adapters:

| Provider | Class | Factory | Token-shape at registry layer |
|---|---|---|---|
| OpenAI | `OpenAIProvider` at `:122-347` | `get_openai_client(api_key=...)` | `response.usage.prompt_tokens`, `.completion_tokens` |
| Anthropic | `AnthropicProvider` at `:353-522` | `get_anthropic_client(api_key=...)` | `response.usage.input_tokens`, `.output_tokens` |
| DeepSeek | `DeepSeekProvider` at `:528-634` | `get_openai_client(base_url='https://api.deepseek.com')` | OpenAI-compatible shape |
| Together AI | `TogetherProvider` at `:640-755` | `get_openai_client(base_url='https://api.together.xyz/v1')` | OpenAI-compatible shape |
| Gemini | `GeminiProvider` at `:761-891` | `google.genai.Client(api_key=..., http_options=HttpOptions(timeout=90_000))` | `usage.usage_metadata.prompt_token_count`, `.candidates_token_count` at `:847-848` — **NOT OpenAI-compatible; F3 latent gap** |
| Ollama | `OllamaProvider` at `:897-995` | direct `requests.post(f"{base_url}/api/generate", ...)` (120s timeout) | `response.prompt_eval_count`, `.eval_count` at `:969-970` — **NOT OpenAI-compatible; F3 latent gap** |

Not owned by Cat B — separate concern (adapter registry vs telemetry wrapper). But Cat B's `_extract_usage` must know about provider shapes; F3 is Cat B debt.

### `_impl_cleanup_stale_llm_calls` at `core/tasks_agents.py:1659-1720` — 10-min watchdog

S1221 P2 Tier 2 watchdog per docstring at `:1662-1682`. Runs every 10 minutes via beat (see §6). Marks stale STARTED rows as FAILED with `error_type='timeout'` and `error_message='LLM call orphaned in STARTED state for {minutes_threshold}+ minutes — marked failed by watchdog_cleanup'` at `:1721-1728`. Samples up to 10 stale rows per run for operator logs at `:1710-1719`. Session 1220 P2 investigation found rows held open for 96+ hours pre-watchdog.

Cat B-owned. No cross-cat reads/writes. LEGITIMATE.

---

## 6. Major APIs and Interfaces

**Q10 + Q11 + Q12 + Q13: External-facing surface reading / writing LLMCallEvent.**

### REST endpoints reading LLMCallEvent

**None directly.** Two candidate endpoints from Explore 3 both read the F1 sibling model (LLMCallLog), not LLMCallEvent:

| Endpoint | View | LLMCallEvent? | Notes |
|---|---|---|---|
| `GET /api/llm-routing/logs/` | `llm_call_logs_list` at `core/views_llm_routing.py:300-375` | ❌ Reads LLMCallLog | S697-era routing telemetry endpoint |
| `GET /api/cockpit/cost/` | `cockpit_cost_overview` at `core/views_diagnostics.py:2880-2971` | ❌ Reads LLMCallLog | Cost dashboard reads LLMCallLog |

**Consequence for F1:** LLMCallEvent has zero REST readers at HEAD. All cost/usage dashboards flow through LLMCallLog. LLMCallEvent is written but not surfaced.

### PA tool schemas

| Tool | Schema location | Handler | Reads LLMCallEvent? |
|---|---|---|---|
| `cost_telemetry_tool` | `pa_tool_schemas.py:509-541` | `_handle_cost_telemetry` at `td_handlers_agents.py:3664-3835` | ❌ Reads LLMCallLog (import at :3676) |

Actions exposed by `cost_telemetry_tool`: `summary`, `top_agents`, `recent_calls`. 24-hour default lookback. All queries hit LLMCallLog.

**No PA tool reads LLMCallEvent at HEAD.** Zero handlers found via grep.

### WebSocket consumers reading LLMCallEvent

**None.** Grep across `core/consumers*.py` returns zero LLMCallEvent references (Explore 3 verified). Matches S1701 R7 LOW-priority deferred posture — realtime push of LLM-call events not implemented.

### Celery tasks

| Task | Decorator | Signature + line | Beat schedule | Purpose |
|---|---|---|---|---|
| `cleanup_stale_llm_calls` | `@shared_task(bind=True)` + `@singleton_task("cleanup-stale-llm-calls", ttl=600)` | `core/tasks.py:415` (delegates to `_impl_cleanup_stale_llm_calls` at `tasks_agents.py:1659`) | `cleanup-stuck-llm-calls` at `crontab(minute='*/10')` (broadcast queue) | Watchdog: mark stuck STARTED rows FAILED with error_type='timeout'. S1221 P2 Tier 2. |
| `cleanup_llm_call_logs` | `@shared_task` | `core/tasks.py:4408` | `cleanup-llm-call-logs` at `crontab(minute=15, hour=4, day_of_week='sunday')` (default queue) | **Deletes LLMCallLog rows** older than `LLM_CALL_LOG_RETENTION_DAYS` (default 30). NOT LLMCallEvent. |

**Reconciliation:** Cat B has:
- ✅ Stuck-STARTED-row watchdog (10-min, on LLMCallEvent)
- ❌ NO date-based retention (F4)

Cat A has both. F1 sibling model LLMCallLog has both (its own retention). LLMCallEvent proper has neither retention nor row-count monitoring.

### Beat schedule

Two Cat B-related entries confirmed in `core/celery.py` `beat_schedule`:
- `cleanup-stuck-llm-calls` → `core.tasks.cleanup_stale_llm_calls` @ `*/10 min` (broadcast queue)
- `cleanup-llm-call-logs` → `core.tasks.cleanup_llm_call_logs` @ `Sunday 04:15` (default queue) — targets LLMCallLog

No aggregation, cost-rollup, or spike-detection beat entries reference LLMCallEvent. `PLATFORM_INVENTORY.md` autoblock reports 92 enabled + 5 disabled PeriodicTasks; none are LLMCallEvent aggregators.

### Management commands

- `setup_llm_routing` at `core/management/commands/setup_llm_routing.py` — seeds provider/model/routing config; does NOT touch LLMCallEvent.
- `db_health_snapshot` at `core/management/commands/db_health_snapshot.py` — counts LLMCallLog rows (:158-159 per Explore 3); does NOT count LLMCallEvent.

**No management command exists for LLMCallEvent audit / backfill / replay.**

### CI lint enforcement

- `tools/check_direct_llm_calls.py` (305 lines) — AST-based scanner that walks all `.py` files and detects direct provider SDK invocations outside `llm_call_span` / `llm_call_async` blocks.
- `.ci/llm_whitelist.txt` — allowed bypass sites (S1222 P5 whitelist).
- `.github/workflows/check-llm-sdk.yml` — runs the checker on every PR touching `**/*.py`. **Enforce mode** (S1222 P5 promoted from `--warn-only`). Fails PR on any non-whitelisted direct call.

Corresponds to S1098 PR #2. SHIPPED.

### Frontend surfaces

Not verified in detail. Explore 3 defers to frontend-specific deep-dive; assumed cost/usage dashboards consume REST endpoints or PA tools, both of which read LLMCallLog (F1). No direct frontend consumers of LLMCallEvent expected.

### Discord bot

No Discord command surfacing LLMCallEvent found (Explore 3 verified).

### PA `unified_pa_entrypoint`

**F2 CRITICAL** — verified via grep at Task 4 verifier-loop:
- `core/services/unified_pa_entrypoint.py` — 0 imports of `llm_call_span` / `llm_call_async` / `llm_call_wrapper`
- `core/llm_enforcer.py` — 0 imports

PA GPT-5.2 function-calling agentic loop (per CLAUDE.md: 113 tool schemas + 156 handlers + up to 20 iterations per message) generates multiple LLM calls per user message and writes **zero LLMCallEvent rows**. This is the largest uncovered surface in Cat B.

---

## 7. Runtime Flows

### Flow 1: Sync LLM call via `llm_call_span` (22 of 23 production sites)

```
Caller (e.g., content_writer_agent._draft_intro)
  ↓
  from core.services.llm_call_wrapper import llm_call_span
  ↓
  with llm_call_span(
      provider='openai', model='gpt-5-mini',
      execution_id=ctx.get('execution_id'),
      agent_name='ContentWriterAgent',
  ) as span:
      ↓
      wrapper: _coerce_execution_id(execution_id) → UUID | None      [:310]
      ↓
      wrapper: _check_cancel(cancel_token, execution_id, location, ...)  [:312-318]
      ↓ (may raise LLMCallCancelled before any DB write)
      ↓
      wrapper: call_id = uuid.uuid4(); started_at = now(); perf_counter start
      ↓
      wrapper: _create_event_safe(call_id, execution_id, agent_name,
                                  provider, model, started_at, metadata)  [:323-331]
             → LLMCallEvent.objects.create(status='STARTED', ...)          [:194-204]
             → returns event row (or None on DB failure)
      ↓
      wrapper: yield _Span(call_id)                                       [:336]
      ↓
      caller: response = client.chat.completions.create(...)
      caller: span.attach_response(response)  ← REQUIRED for token extraction
  ↓
  wrapper: else block (no exception)                                       [:358-367]
    → _extract_usage(span.response) → {tokens_in, tokens_out}              [:359]
    → _save_event_safe(event, status='SUCCESS', tokens_in, tokens_out,
                       duration_ms, finished_at)                            [:360-367]
  ↓
  caller continues with response
```

**Failure branches:**
- Exception during SDK call → `except Exception` at `:348-357` → `_save_event_safe(status='FAILED', error_type=_classify_error(exc), error_message=str(exc)[:2000], ...)` → re-raise
- CancelToken or registry cancel → `except LLMCallCancelled` at `:337-347` → `_save_event_safe(status='CANCELLED', cancelled=True, error_type='cancelled', ...)` → re-raise
- ORM failure inside `_create_event_safe` or `_save_event_safe` → swallowed (best-effort telemetry; caller sees LLM response normally; telemetry gap silent)

### Flow 2: Async LLM call via `llm_call_async` (1 production site: `thinking_agent.py:670`)

```
async caller (ThinkingAgent._call_llm)
  ↓
  from core.services.llm_call_wrapper import llm_call_async
  ↓
  response = await llm_call_async(
      client.chat.completions.create,  ← callable (may be sync or async)
      model='gpt-5-mini', messages=[...],  ← forwarded kwargs
      provider='openai', model_name='gpt-5-mini',
      execution_id=..., agent_name='ThinkingAgent',
  )
  ↓
  wrapper: _coerce_execution_id + _check_cancel (identical to sync)
  ↓
  wrapper: await sync_to_async(_create_event_safe, thread_sensitive=False)(...)  [:411]
  ↓
  wrapper: result = fn(*args, **kwargs)  [:422]
    → if asyncio.iscoroutine(result): result = await result  [:423-424]
  ↓
  wrapper: else block (no exception)  [:446-456]
    → _extract_usage(result) → {tokens_in, tokens_out}
    → await sync_to_async(_save_event_safe, ...)(event, status='SUCCESS', ...)
  ↓
  wrapper: return result
```

Model kwarg asymmetry: sync uses `model=`; async uses `model_name=` to avoid collision when forwarding kwargs to `fn` (docstring at `:387-392`).

### Flow 3: Cancellation via registry (PR #3 PARTIAL)

```
Orchestration signal (e.g., user hits Cancel button)
  ↓
  cancel_registry.request_execution_cancel(execution_id, reason='user_abort')
    → Redis HSET (with in-memory fallback)  [24h TTL]
  ↓
  ... time passes; LLM call in flight ...
  ↓
  Next `_check_cancel` at wrapper entry (either llm_call_span or llm_call_async):
    → is_execution_cancelled(execution_id) walks ancestor chain
    → returns True on direct hit or ancestor cancel
  ↓
  wrapper: mark_observed(execution_id, location='LLMCallWrapper.span:pre-call:AgentName')
  ↓
  wrapper: raise LLMCallCancelled("LLM call cancelled via registry...")
  ↓
  wrapper: except LLMCallCancelled block writes CANCELLED row + re-raises
```

**F7 partial gap:** Once `client.chat.completions.create(...)` is in flight inside the `with llm_call_span` block, cancel signal does NOT abort the in-flight socket. Only next entry to a wrapper checkpoint (or a subsequent LLM call) observes the cancel. Wrapper docstring at `:18-21` explicitly notes: "provider adapters do not yet abort in-flight sockets." Race condition: LLM completes normally + writes SUCCESS row before next cancel check fires; user sees CANCELLED status only for the *next* call after the signal. Deferred to future PR #3-completion.

### Flow 4: Stuck-STARTED watchdog cleanup (10-min beat)

```
Beat: cleanup-stuck-llm-calls @ */10 min (broadcast queue)
  ↓
  cleanup_stale_llm_calls(minutes_threshold=10)
    → _impl_cleanup_stale_llm_calls at tasks_agents.py:1659
  ↓
  LLMCallEvent.objects.filter(status='STARTED', started_at__lt=now-10min)
  ↓
  If count > 0:
    → log up to 10 sample rows for operator visibility
    → .update(status='FAILED', error_type='timeout',
              error_message='LLM call orphaned in STARTED state for 10+ minutes — marked failed by watchdog_cleanup')
  ↓
  return {'stale_marked': count, ...}
```

Session 1221 P2 (Tier 2) mechanic. Cleans up rows from BaseAgent Tier 1 timeout (60s→180s cap) escaping OR non-BaseAgent code paths with their own LLM call sites.

### Flow 5: Best-effort telemetry silent failure

```
Wrapper attempts _create_event_safe or _save_event_safe
  ↓
  DB down / integrity error / permission denied
  ↓
  except Exception at :173-176 or :205-208
  ↓
  logger.exception("[llm_call_wrapper] LLMCallEvent save failed: %s", ...)
  ↓
  return None (create_event_safe) or return normally (save_event_safe)
  ↓
  Telemetry row NOT persisted; LLM response still returned to caller normally;
  Caller unaware; log-only signal to operators
```

No metric increments a `_save_event_safe_exceptions_total` counter (T-5 debt candidate). Telemetry gaps are silent.

---

## 8. Data Ownership and Lifecycle

### Data owned by Cat B

- `LLMCallEvent` rows (write + retention + drift observability)
- Wrapper's error classification enum (7 buckets)
- Wrapper's provider-shape mapping (`_extract_usage` — OpenAI + Anthropic + generic dict)

### Data consumed by Cat B

- `execution_id` UUID from caller context (Cat C `AgentExecution.id`, non-typed)
- `agent_name` string from caller
- `provider` + `model` strings from caller
- Cancel state from `cancel_registry` (support service)

### Data produced by Cat B (for other domains)

- `LLMCallEvent` rows consumable by:
  - No REST readers at HEAD (F1 — `cost_telemetry_tool` reads LLMCallLog, not LLMCallEvent)
  - Test fixtures
  - Watchdog cleanup task (self-reads to mark stale)
  - Grep hits at `core/employees/status.py` + `core/signals/rigby_delegation_signals.py` — UNKNOWN read/write intent (SPECULATIVE; requires additional read to classify)

### Lifecycle summary

| Phase | Trigger | Writer | State transition |
|---|---|---|---|
| Create (STARTED) | `llm_call_span` / `llm_call_async` entry | `_create_event_safe` | (none → STARTED) |
| Success terminal | `else` branch on wrapper exit | `_save_event_safe` | STARTED → SUCCESS |
| Failure terminal | `except Exception` branch | `_save_event_safe` | STARTED → FAILED |
| Cancel terminal | `except LLMCallCancelled` branch | `_save_event_safe` | STARTED → CANCELLED |
| Stuck-STARTED watchdog | 10-min beat sweep | `_impl_cleanup_stale_llm_calls` | STARTED → FAILED (with `error_type='timeout'`, `error_message='watchdog_cleanup'`) |
| Retention delete | (none) | (**no retention task exists — F4**) | — |

**Coverage gap:** No cleanup, no archival, no aggregation-and-forget for LLMCallEvent. Rows persist indefinitely.

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22: Integrations map + cross-cat.**

### Cross-cat integration map at HEAD (mirror S1701 §9 table shape)

| Integration | Direction | Mechanism | Strength |
|---|---|---|---|
| Cat B ↔ Cat A (CeleryTaskEvent) | none direct | 3-hop via Cat C: `LLMCallEvent.execution_id → AgentExecution.id → AgentExecution.input_data['celery_task_id'] → CeleryTaskEvent.task_id` (JSON-path, unindexed unless GIN-indexed per S1701 §9). No direct schema correlation. | **MISSING (by design)** — S1701 §9 already declared symmetric; verified from Cat B side. |
| Cat B ↔ Cat C (AgentExecution) | Cat B reads from → Cat C | `LLMCallEvent.execution_id` is UUIDField, nullable, indexed, NOT FK. Points at `AgentExecution.id` implicitly. Untyped correlation (3 AgentExecution classes exist per parent §3.C landmine). Caller (agent_router → `_impl_create_execution_record`) instantiates whichever class; `execution_id` inherits the class ambiguity. | **STRONG (scope-spanning, non-FK'd for autonomy)** — value threads through entire agent-LLM sequence; correlation is untyped. |
| Cat B ↔ Cat D (ToolCallRecord) | none declared | Parent §3.B + F3 fold: "LLM calls made from inside a tool invocation remain Cat B; dedup via correlation keys (execution_id + trace_id + tool_call_id)". **BUT** `ToolCallRecord` at `core/models_tool_calls.py:19-132` has `trace_id`, `conversation_id`, `agent_name`, `tool_name` — **NO `execution_id` and NO `tool_call_id` field** (Explore 4 verified). Accounting rule cites schema fields that do not exist. | **MISSING (accounting-rule gap)** — accounting rule is definitional but not enforceable at schema level. §17 dedup candidate. |
| Cat B ↔ Cat E (OpsRun/OpsRunEvent) | none declared | `OpsRun` + `OpsRunEvent` (`core/models_ops_runs.py:11-117`) have `mission_id` (UUIDField, nullable, indexed); no `execution_id`. `MissionRunner` at `core/employees/mission_runner.py` does NOT thread `mission_id` into `llm_call_span` metadata (grep verified). | **MISSING** — missions cannot attribute LLM cost. Would require: (a) thread mission_id into `metadata` kwarg + index metadata['mission_id'] via GIN, OR (b) FK from OpsRun to LLMCallEvent via execution_id chain. |
| Cat B ↔ Cat F.a (HeartBeat) | none | HeartBeat is a separate polling model; no LLMCallEvent reference. | **MISSING** (by design; different concerns). |
| Cat B ↔ EventBus / EventOutbox | none | No outbound publish pattern in wrapper. Zero grep hits. | **MISSING** — Cat B is passive telemetry sink. Same posture as Cat A (S1701 §9). |
| Cat B ↔ RAG pipeline | none | RAG (`core/rag_integration.py`, `core/rag.py`, `build_rag_corpus`) is retrieval-only; no LLM generation. LLM calls by agents *consuming* RAG results flow through agent context. | **MISSING (by design)** — RAG is retrieval, not generation. |

### Correlation primitive posture (parent §5 F5 execution_id row) — D74 axis evidence

**Cat B primitive posture at HEAD:**

- **`call_id`** — LLMCallEvent PK. UUIDField(primary_key=True, default=uuid.uuid4, editable=False). **Singleton primitive at LLM-call level.** Complete coverage (every row has one; not nullable). No downstream models carry `llm_call_id` as scalar reference (0 grep hits). Not a cross-model spine.
- **`execution_id`** — LLMCallEvent UUIDField, nullable, indexed, NOT FK. **Cat C-owned spine primitive tagged onto Cat B rows.** Coverage-gapped by design ("NULL for detached calls"). Untyped correlation (3 AgentExecution classes). No downstream models carry `llm_execution_id`.

**Comparison to Cat A task_id posture** (S1701 §9-10):
- Cat A `task_id`: coverage-complete singleton (all Celery tasks reaching worker); CharField(unique=True, db_index=True); 8 downstream scalar-CharField consumers.
- Cat B `call_id`: coverage-complete singleton (PK non-null); UUIDField; **0 downstream consumers**.
- Cat B `execution_id`: coverage-gapped by design (nullable); UUIDField, non-FK; **0 downstream consumers**.

**Cat B's D74 axis contribution (feeds xx99):**
- `call_id` is Cat B's singleton primitive **at the LLM-call level**, analogous in role but not in scope to Cat A's `task_id` (which is at the Celery-task level). **`call_id` is not a candidate cross-model spine** — no downstream model needs to reference a specific LLM call.
- `execution_id` is a **borrowed spine** — Cat C owns it; Cat B tags it. If xx99 decides the arc-wide spine should be a canonical `execution_id + trace_id` pair spanning task→LLM→agent→tool→ops, Cat B's contribution is: (a) `execution_id` is present + indexed at Cat B; (b) nullability + non-FK are intentional per docstring (survives AgentExecution deletion); (c) if xx99 tightens Cat B to `execution_id NOT NULL + FK`, it forces PA path adoption (F2) as a prerequisite and breaks the "survive AgentExecution deletion" retention model.
- **If xx99 decides layers stay structurally separate**, current Cat B posture is defensible for a passive telemetry sink — no changes required.
- **If xx99 decides task_id → execution_id needs a canonical spine**, the required work is (a) F1 dedup (LLMCallEvent vs LLMCallLog); (b) F2 PA coverage; (c) F3 provider-shape completeness; (d) F4 retention; (e) **option set for execution_id typing** — either (e.i) upgrade `execution_id` to `NOT NULL + FK` (breaks the "telemetry survives AgentExecution deletion" rationale from `models_llm_telemetry.py:56-60` docstring and forces PA-path adoption as prerequisite), OR (e.ii) standardize a shared correlation-view / join contract that preserves current nullability + non-FK autonomy while making the 3-hop chain queryable in one hop. Rigby SIGN cycle 1 F2 fold: NOT-NULL+FK is not universally required — it's one option that conflicts with the survival-of-deletion rationale.

### Import boundaries

**`core/models_llm_telemetry.py` imports (top-of-file):**
- `uuid` (stdlib)
- `from django.db import models`
- `from django.utils import timezone`

Zero cross-domain imports. Clean. (S1701 §9 same posture for Cat A.)

**`core/services/llm_call_wrapper.py` imports (top-of-file):**
- Stdlib: `asyncio`, `logging`, `time`, `uuid`, `contextlib`, `dataclasses`, `typing`
- Django: `django.utils.timezone`

Zero cross-domain imports at top level. Lazy imports inside functions:
- `LLMCallEvent` at `:194` (Cat B self-reference)
- `is_execution_cancelled`, `mark_observed` at `:252-253` (support-service dependency, not a Cat A/C/D/E model)
- `sync_to_async` at `:394` (deferred asgiref)

All lazy imports have documented rationale (app-loading order, circular avoidance, fail-graceful). No boundary violations.

**Reverse (imports of Cat B from other domains):**
- `LLMCallEvent`: 9 files (per Explore 4 grep) — `tasks_agents.py`, `signals/rigby_delegation_signals.py`, tests (multiple), `models/__init__.py`, `llm_call_wrapper.py` itself, `employees/status.py`.
- `llm_call_span` / `llm_call_async` / `LLMCallCancelled`: 23 production wrapper call sites + 2 test files + 1 tool (`check_direct_llm_calls.py` grep hits, but that's a checker, not a caller).

Callers by domain:
- **`core/agents/`**: 7 agents (content_writer, code_review, devops, market_intelligence, campaign_orchestrator, thinking, base_agent [exception import only], agent_router [exception import only])
- **`core/tasks_*.py`**: 1 file (`tasks_initiatives.py`) with 5 sites; 1 file (`tasks_agents.py`) as watchdog implementer
- **`core/services/`**: 1 file (`curated_action_card_generator.py`) with 1 site
- **`core/employees/`**: `mission_runner.py` does NOT import wrapper (F2 analog for missions — missions cannot attribute LLM cost)
- **PA path** (`unified_pa_entrypoint.py` + `llm_enforcer.py`): 0 imports (F2 CRITICAL)

### Cross-arc references

- **Group 1400 Revenue (S1499 canonical):** R.A2 follow-on cites `LLMCallEvent` for scoring-rate telemetry probe. Implies Group 1700 xx99 should verify: does `OpportunityDraftGenerator` (Revenue Cat B agent per S1401) route through `llm_call_span`? SPECULATIVE at S1702 close; verified null-rate query owed to xx99.
- **Group 1600 Content (S1699 canonical):** S1602 Content Reviewers make LLM calls for citation inference (LLM-prompt-only per §7.4 CORRECTION). If they route through wrapper, `agent_name='ContentReviewerAgent'` shows up in LLMCallEvent aggregations. Coverage UNKNOWN.
- **Group 1500 Sports (S1599 canonical):** F.B1 fold: 4 of 5 sports pipeline agents use `.execute()` (bypasses AgentExecution row); LLM calls from those agents (if wrapped) write `LLMCallEvent.execution_id=NULL`. Cost attribution for sports agents is degraded (SPECULATIVE — coverage not verified at S1702 close).

---

## 10. Event Flows

**Q19 + Q20: Events emitted + events that should be emitted.**

### Events emitted by Cat B

Cat B does **NOT emit downstream events** in the domain-event sense (no Django signals `pre_save`/`post_save` publishers, no channel_layer `group_send`, no WebSocket push, no Kafka/RabbitMQ producer). Cat B is a **passive telemetry sink** — data captured, stored, and read by pull-based consumers (SQL queries).

**Side effects at wrapper boundary (not events per se):**
- `mark_observed(execution_id, location=...)` at `_check_cancel:257` — writes to cancel_registry (Redis) with observed_at + location. This is a cross-cutting service write, not a domain event.
- `logger.exception(...)` at `_save_event_safe:174` + `_create_event_safe:206` — best-effort telemetry-failure logs. Consumed by log aggregation, not event bus.

### Events that should be emitted (gaps)

- **`llm_call_completed` domain event** — S1500 F.B3 (Sports) + Group 1400 (Revenue) both would benefit from `llm_call_completed(execution_id, cost, tokens, agent_name)` to drive per-agent cost dashboards without SQL polling. NOT emitted at HEAD. §19 R7 candidate.
- **`llm_call_budget_exhausted` domain event** — S1224 gpt-5 max_completion_tokens floor precedent: silent empty-content returns are not observably distinguishable from normal SUCCESS at Cat B. No `error_type='budget_exhausted'` bucket exists in the 8-value enum. §19 R5 candidate.
- **`llm_call_provider_health_degraded` domain event** — Session 841 provider_health_tracker is referenced in registry but not integrated with LLMCallEvent (Explore 2 SPECULATIVE). If wrapper aggregates FAILED rows by provider over rolling window, health degradation could be emitted. NOT emitted at HEAD.

---

## 11. Existing Documentation

**Q10 + Q11: What docs cover Cat B; where are the gaps.**

### Docs that cover Cat B

- **Parent scoping (S1700):** `docs/research/domains/observability/1700_observability_domain_scoping.md` §3.B (lines 429-472) — CANONICAL for Cat B boundary + scope + load-bearing questions. F6 drift on field list already flagged.
- **Sibling audit (S1701 Cat A):** `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md` §9 — cross-cat integration map row for Cat A ↔ Cat B (MISSING by design). Establishes template.
- **`docs/topics/employee-os.md` (S1260, :65):** Names LLMCallEvent as read surface for `employee_tool` evidence join (`OpsRun + OpsRunEvent + LLMCallEvent + ToolCallRecord`). ACCURATE.
- **`docs/topics/active-module-ownership-map.md` (S1111, :23):** Names `llm_provider_registry.py` + `agent_llm_router.py` as distinct modules. ACCURATE.
- **`docs/topics/agent-system.md`:** References EditorAgent LLM fix (S1033) + LLMProviderRegistry + LLMRequest pattern. Does NOT discuss wrapper, telemetry, or cost fields directly.
- **`PLATFORM_WHAT_IT_IS.md` "OpenAI hardening — Sessions 1214-1216 + 1221" subsection (lines 436-462):** Documents factory adoption (S1214: 8 PRs, 22 timeout footguns eliminated), reasoning-contract fixes (S1215: 3 files, 8 sites), runtime guard + CI lint (S1216: `apply_reasoning_guard` + env-gated `OPENAI_REASONING_GUARD`), Tier 1 + Tier 2 (S1221: total-request bound + cleanup watchdog). Cumulative: ~30 call sites aligned; catalog deliverable `bb775acb-…` tracks provenance. ACCURATE at S1223 refresh.

### Docs that mention Cat B in passing

- **Session handoffs relevant to Cat B:**
  - `SESSION_1098_WRAP_CANARY_GREEN.md` — origin session; content-delivery-canary focus, sparse on architecture.
  - `SESSION_1098_ADDENDUM_CANCEL_AND_LINT.md` — PR #3 cancel + PR #2 CI lint follow-ons.
  - `SESSION_1098_ADDENDUM_2_TIER1_AND_BFULL.md` — Tier 1 bound wiring + full-buffer handling.
  - `SESSION_1214_OPENAI_CALLER_ALIGNMENT_PHASES_A_B.md` — Phase A+B factory adoption (8 PRs). Line 86: "These should migrate to `core/services/llm_call_wrapper.py` per Session 1098 PR #1's pattern."
  - `SESSION_1215_OPENAI_REASONING_CONTRACT_C_D.md` — reasoning contract fixes.
  - `SESSION_1216_OPENAI_REASONING_GUARD.md` — runtime guard.
  - `SESSION_1220_ZOMBIE_MONITOR_PLUS_HTTPX_INVESTIGATION.md` — precursor to Tier 1/2 arc.
  - `SESSION_1221_TIER_1_PLUS_TIER_2_FROM_7AE61CF7.md` — Tier 1 (PR #2519) + Tier 2 (PR #2520) shipping.
  - `SESSION_1223_AUDIT_SWEEP_AND_WATCHDOG_GREEN.md` — 5-check burn-in window; Check #2 verified LLMCallEvent stuck-STARTED count = 0.
  - `SESSION_1224_OUTREACH_PIPELINE_AND_TOKEN_BUDGET_SWEEP.md` — gpt-5 max_completion_tokens floor sweep (11 sites bumped to 4000); memory rule `feedback_gpt5_max_completion_tokens_floor.md`.
  - `SESSION_1222_V2_AUDIT_CLOSE.md` — P5 promoted CI lint to enforce mode.
- **Memory rules relevant to Cat B:**
  - `feedback_openai_client_factory.md` (S1084) — factory required
  - `feedback_anthropic_client_factory.md` (S1084) — factory required
  - `feedback_gpt5_max_completion_tokens_floor.md` (S1224) — 4000-token floor
  - `feedback_llm_autofills_boolean_params_with_false.md` (S1227) — tool-schema pattern, not Cat B direct

### Documentation gaps (input to §14 Known Drift)

- **No dedicated `docs/topics/llm-telemetry.md`** — Cat B has no operator handbook analog to `celery-workers.md` (which S1701 references for Cat A operator ownership). §19 R-item candidate.
- **Parent scoping §3.B field list is drift** (F6) — describes LLMCallLog fields, not LLMCallEvent. Owed to xx99 anchor-update.
- **CLAUDE.md 6-provider claim** — accurate; but no doc discusses per-provider wrapper adoption %. §14 gap.
- **Wrapper adoption count claim** — no doc reports the "23 production sites" number this audit establishes. §14 gap.
- **F1 two-model gap** — no doc explains why LLMCallEvent and LLMCallLog coexist, or what the migration/consolidation plan is. §17 primary finding.

---

## 12. Research Coverage

**Per playbook §12 taxonomy:** NONE / LIGHT / MODERATE / DEEP / CANONICAL.

**Cat B research coverage classification: MODERATE.**

**Evidence:**
- Foundational scoping exists (S1700 §3.B, CANONICAL for boundary).
- Operational history is DEEP: S1098 origin + S1214-1216 OpenAI hardening arc + S1221 watchdog arc + S1223 burn-in + S1224 token floor + S1222 P5 CI enforce promotion. Multiple sessions of grounded operational work.
- Memory rules enforce preconditions (factory adoption, gpt-5 floor). LIGHT — not systematic coverage.
- Topic docs mention Cat B in passing (employee-os.md, agent-system.md, active-module-ownership-map.md) but no dedicated Cat B doc exists.
- S1274 cross-domain baseline named the 5-layer dedup mission but did not audit Cat B specifically.

**Verdict:** MODERATE. Foundational + operational + enforcement coverage exists; systematic completeness audit (this doc) is the FIRST — no prior "wrapper adoption %" or "PA coverage" analysis has been performed at HEAD.

---

## 13. Architecture Maturity

**Per playbook §12 taxonomy:** EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL.

**Cat B maturity verdict: STABLE for the covered surface + PARTIAL overall.**

**Evidence signals:**
- ✅ **Operationally alive.** Rows are being written (23 production wrapper sites; watchdog is finding + cleaning stuck-STARTED rows regularly per S1223 burn-in Check #2).
- ✅ **CI-enforced.** `.github/workflows/check-llm-sdk.yml` in enforce mode (S1222 P5). Prevents new direct-SDK bypasses.
- ✅ **Well-tested.** `core/tests/test_llm_call_wrapper.py` covers sync + async happy path + exception + cancel + edge cases. `core/tests/test_cancel_token_e2e.py` covers PR #3 cancel-registry integration.
- ✅ **Documented at implementation level.** Module docstrings at both `models_llm_telemetry.py` and `llm_call_wrapper.py` are detailed and correct.
- ✅ **Bounded latency + best-effort.** `_save_event_safe` swallows DB errors; wrapper doesn't block LLM response on telemetry failure.
- ❌ **Coverage is partial.** PA path uncovered (F2 CRITICAL). BaseAgent primary path status UNKNOWN. Gemini/Ollama shapes latent-broken (F3 MEDIUM).
- ❌ **F1 dedup unresolved.** Two LLM telemetry models coexist; consumers split between them.
- ❌ **No retention.** LLMCallEvent rows accumulate unbounded (F4).
- ❌ **PR #3 partial.** Cancel signals don't abort in-flight sockets.
- ❌ **PR #4 not shipped.** Nested dispatch budget documented but not implemented.

**Comparison to Cat A (S1701 verdict: STABLE):**
- Cat A has 30-day retention + no F1 sibling model + coverage-complete primitive (task_id) + no PA coverage gap.
- Cat B has stuck-STARTED sweep but no retention + F1 duplication + coverage-partial primitives (call_id complete but under-consumed; execution_id nullable by design) + PA coverage gap.

**Verdict:** Cat B is lower-maturity than Cat A. **STABLE** describes the covered surface (23 production sites, tests, CI enforce); **PARTIAL** describes the overall Cat B posture given F1 + F2 + F4. Playbook §12 does not permit split verdicts — pick one. Given the CRITICAL F1 + F2 findings, **overall verdict is PARTIAL**.

**Risk verdict: MEDIUM-HIGH.**
- F1 dedup risk (write both models silently, consumers pick different sides) → HIGH downstream.
- F2 PA coverage gap → HIGH (PA is likely the dominant LLM caller; zero LLMCallEvent visibility).
- F4 retention → MEDIUM (accumulates but doesn't fail today).
- F3 latent → MEDIUM (fires only if Gemini/Ollama adopt wrapper).
- Overall: **MEDIUM-HIGH** — no acute failure at HEAD, but observability posture is materially degraded.

---

## 14. Known Drift

### D1 (MEDIUM) — Parent scoping §3.B field list drift (F6)

- **Parent claim** (`1700_observability_domain_scoping.md:440-442`): "Fields: model, prompt_tokens, completion_tokens, total_tokens, latency_ms, cost, execution_id (correlation key), success, error"
- **Runtime reality** (`core/models_llm_telemetry.py:30-115`): `call_id, execution_id, agent_name, provider, model, status (enum), started_at, finished_at, duration_ms, tokens_in, tokens_out, retry_count, error_type, error_message, cancelled, metadata`
- **Root cause**: Parent scoping author was reading LLMCallLog fields (F1 sibling model at `models_llm_routing.py:297-362`) and mislabeled as LLMCallEvent. LLMCallLog has `total_tokens`, `latency_ms`, `cost`, plus `agent_name` + `provider` + `model` — parent's list matches LLMCallLog exactly.
- **Severity**: MEDIUM. Not a runtime bug; documentation error causing readers to expect fields that don't exist on LLMCallEvent.
- **Fix owner**: xx99 (S1799) anchor-update PR. Correct parent's Cat B field list AND explicitly disambiguate LLMCallEvent vs LLMCallLog.

### D2 (CRITICAL) — PA agentic loop bypass (F2)

- **Runtime**: `core/services/unified_pa_entrypoint.py` + `core/llm_enforcer.py` both have 0 wrapper imports (verified grep during Task 4 verifier-loop).
- **Impact**: PA GPT-5.2 function-calling loop generates 1-20 LLM calls per user message and writes 0 LLMCallEvent rows. Dominant LLM caller (per usage volume assumption) has zero observability at Cat B layer.
- **Consequence**: All cost/latency/error dashboards that read LLMCallEvent under-count. `cost_telemetry_tool` reads LLMCallLog (F1) so PA cost may be captured there — SPECULATIVE at S1702 close; requires read of `enforce_real_ai` to confirm.
- **Severity**: CRITICAL. Not fixable inside Cat B — requires PA path adoption of wrapper.
- **Fix owner**: §19 R1 (this doc); belongs to PA-integration follow-on, not xx99 anchor-update.

### D3 (MEDIUM, latent) — `_extract_usage` provider-shape gap (F3)

- **Runtime**: `_extract_usage` at `llm_call_wrapper.py:126-159` handles OpenAI `prompt_tokens`/`completion_tokens` + Anthropic `input_tokens`/`output_tokens` + generic dict shape. Does NOT handle Gemini `prompt_token_count`/`candidates_token_count` (per `llm_provider_registry.py:847-848`) or Ollama `prompt_eval_count`/`eval_count` (per `llm_provider_registry.py:969-970`).
- **Impact today**: None. All 23 production wrapper sites use OpenAI/Anthropic (or OpenAI-compatible DeepSeek/Together via `get_openai_client(base_url=...)`).
- **Impact if Gemini/Ollama adopt wrapper**: LLMCallEvent rows would have `tokens_in=NULL, tokens_out=NULL` silently. Cost dashboards would show these providers with 0 tokens.
- **Severity**: MEDIUM (latent). CRITICAL if adoption happens.
- **Fix owner**: §19 R4 (this doc); low-risk P1 code change (add 2 shape branches to `_extract_usage`).

### D4 (HIGH) — No date-based retention for LLMCallEvent (F4)

- **Runtime**: Only cleanup task for LLMCallEvent is `_impl_cleanup_stale_llm_calls` (10-min watchdog for stuck STARTED rows). No date-based retention exists.
- **Sibling has retention**: `cleanup_llm_call_logs` at `core/tasks.py:4408` deletes LLMCallLog rows older than `LLM_CALL_LOG_RETENTION_DAYS` (default 30). LLMCallEvent has no analog.
- **Impact**: Unbounded row accumulation. Query performance degrades over time. Storage cost grows without bound. No row-count monitoring.
- **Severity**: HIGH. Not acute today; will bite at scale.
- **Fix owner**: §19 R2 (this doc); post-arc T-slot per D73 posture-framing (posture: retain-forever, retain-30-day, retain-by-tier).

### D5 (SPECULATIVE) — S1224 budget-exhausted silent failures not observably distinguishable at Cat B

- **Runtime**: `_classify_error` at `:95-123` has 7 error buckets; none is `budget_exhausted`. `finish_reason='length'` + `reasoning_tokens >> output_tokens` scenario (S1224 memory rule) returns SUCCESS with `tokens_out` including reasoning; wrapper cannot distinguish empty-content-due-to-budget from normal completion.
- **Impact**: SPECULATIVE at HEAD — S1224 remediation swept 11 sites to 4000-token floor, so scenario is largely mitigated. But no observability guard exists if a new site regresses.
- **Severity**: MEDIUM. Rare occurrence; hard to detect if it recurs.
- **Fix owner**: §19 R5 (this doc); optional enhancement to `_classify_error` + wrapper to inspect response shape for finish_reason='length' + minimal output. Or add 8th error bucket + caller-supplied hint.

### D6 (MEDIUM) — Parent scoping §3.B model line-range drift

- **Parent claim** (`:438`): "Model: `core/models_llm_telemetry.py:30-100` (`LLMCallEvent`)"
- **Runtime reality**: Class body extends `:30-115` (16 field definitions + Meta + `__str__` method). `_100` is roughly the last field; `_115` is the end of `__str__`.
- **Severity**: MINOR. Line-range drift analog to S1701 F2 fold (S1701 caught the same class of drift for Cat A signal-handler line-range).
- **Fix owner**: xx99 anchor-update PR (bundle with D1).

---

## 15. Known Technical Debt

### T-1 (CRITICAL) — Two-model LLM telemetry duplication (F1)

- LLMCallEvent + LLMCallLog coexist; different schemas; different consumers; different retention.
- Blocks unified cost accounting. Any downstream consumer must choose which model to read.
- **Debt severity: CRITICAL** — architectural ambiguity at the heart of the LLM observability layer.
- Fix belongs to xx99 posture decision (D74 axis contribution).

### T-2 (CRITICAL) — PA agentic loop uncovered (F2)

- Dominant LLM caller writes zero LLMCallEvent rows.
- Cannot be fixed inside Cat B alone; requires PA path integration.
- **Debt severity: CRITICAL** for observability posture.

### T-3 (HIGH) — No date-based retention (F4)

- Unbounded accumulation.
- Fix is simple (add `cleanup_old_llm_call_events` beat task with `LLM_CALL_EVENT_RETENTION_DAYS` env default 30).
- **Debt severity: HIGH** — operational.

### T-4 (MEDIUM) — Provider-shape gap latent (F3)

- Gemini/Ollama silent nulls if adopted.
- Fix is 2 shape branches in `_extract_usage`.
- **Debt severity: MEDIUM latent → CRITICAL if adopted.**

### T-5 (MEDIUM) — PR #3 cancel is entry-point only (F7)

- In-flight LLM sockets don't abort on cancel.
- Fix requires provider-adapter socket-level abort (per-provider work).
- **Debt severity: MEDIUM** — race condition on cancel; usually resolves at next checkpoint.

### T-6 (MEDIUM) — Cat B/Cat D correlation gap (parent §3.B accounting rule vs schema)

- Accounting rule cites `tool_call_id` for Cat B/Cat D dedup; `ToolCallRecord` has no `tool_call_id` field.
- LLM calls from inside tools cannot be linked to specific tool invocations at schema level.
- **Debt severity: MEDIUM** — dedup by convention only.

### T-7 (MEDIUM) — Wrapper adoption partial (F5)

- 23 production sites across 8 files. BaseAgent primary path status UNKNOWN.
- Fix is per-caller migration (S1214-S1216 pattern).
- **Debt severity: MEDIUM** — CI lint prevents new drift; existing partial adoption is stable.

### T-8 (MEDIUM) — MissionRunner LLM-cost attribution gap

- `mission_id` not threaded into `llm_call_span` metadata.
- Missions cannot attribute LLM cost via LLMCallEvent.
- **Debt severity: MEDIUM** — Employee OS observability gap.

### T-9 (LOW) — PR #4 nested dispatch budget not shipped (F8)

- Documented deferred scope.
- No parent-token propagation.
- **Debt severity: LOW** — no active regression; documented promise.

### T-10 (LOW) — Best-effort telemetry silent failures (T-5 candidate from Explore 6)

- `_save_event_safe` swallows Exception; no counter for swallowed failures.
- Fix: add `LLM_CALL_EVENT_SAVE_ERROR_TOTAL` counter + WARN-level log.
- **Debt severity: LOW** — observability of Cat B itself.

### T-11 (LOW) — No LLMCallEvent aggregation beat

- No cost-rollup, spike-detection, or provider-health aggregation task exists.
- Consumers must query LLMCallEvent directly for aggregations (or read F1 sibling LLMCallLog).
- **Debt severity: LOW** — nice-to-have.

### T-12 (LOW) — CI lint scope limited to SDK calls; ORM writes not enforced

- `check_direct_llm_calls.py` forbids direct SDK calls but not direct `LLMCallEvent.objects.create` bypasses.
- No active violations at HEAD (grep verified — only wrapper writes LLMCallEvent).
- **Debt severity: LOW** — asymmetric risk.

---

## 16. Boundary Violations

### Violation candidates evaluated

| # | Candidate | File:Line | Verdict | Rationale |
|---|---|---|---|---|
| 1 | Wrapper writes outside Cat B (e.g., writes AgentExecution or CeleryTaskEvent) | `llm_call_wrapper.py` | LEGITIMATE (no violation) | Wrapper only writes to LLMCallEvent via `_create_event_safe` + `_save_event_safe`. No cross-cat writes. |
| 2 | Non-wrapper services write LLMCallEvent directly | (grep for `LLMCallEvent.objects.create/save/update` outside wrapper) | LEGITIMATE (no violation) | Grep returned only `_impl_cleanup_stale_llm_calls` (`.update`) which is the S1221 P2 Tier 2 watchdog — legitimate Cat B write. No direct-create bypasses found. |
| 3 | Wrapper reads Cat A/C/D/E/F models | `llm_call_wrapper.py` imports | LEGITIMATE (no violation) | Only reads LLMCallEvent (Cat B self) via lazy import at `:194`. cancel_registry is a support service, not a Cat A/C/D/E model. |
| 4 | Non-Cat-B service reads LLMCallEvent directly (bypassing wrapper reader API) | `td_handlers_agents.py`, `tasks_agents.py`, `signals/rigby_delegation_signals.py`, `employees/status.py` | LEGITIMATE (read-only consumer) | Read-only consumers of LLMCallEvent are allowed (no reader API contract yet). Not a violation. |
| 5 | Cross-cat exception analog (S1219 P1 `on_agent_task_failure_bridge`) | (none found) | LEGITIMATE (no Cat B analog needed) | Cat A has cross-cat exception (writes AgentExecution) as fire-alarm circuit-breaker (S1701 §16 F4 fold). Cat B has no analog need — wrapper writes LLMCallEvent only. |
| 6 | Cancel-registry integration boundary | `_check_cancel:227-270` | LEGITIMATE (support-service dependency) | cancel_registry is a cross-cutting cancel-state service, not a Cat A/C/D/E model. Wrapper queries registry by execution_id; registry is agnostic to LLMCallEvent. Clean boundary. |

**Result: ZERO boundary violations at HEAD.** Cat B write-boundary + read-boundary discipline is clean. Matches S1701 Cat A posture — passive telemetry sinks tend not to violate boundaries.

---

## 17. Duplicate or Overlapping Systems

### F1 CRITICAL — LLMCallEvent + LLMCallLog dual model at HEAD

**Two LLM telemetry models exist:**

| Model | File:Line | Session | Fields | Retention | Consumers |
|---|---|---|---|---|---|
| **LLMCallEvent** | `core/models_llm_telemetry.py:30-115` | S1098 | 16 fields; NO cost, NO total_tokens, NO latency_ms; HAS status enum, error_type enum, cancelled, metadata JSONField | 10-min stuck-STARTED sweep only (F4 debt: no date-based retention) | Read by watchdog + tests + `employees/status.py` + `rigby_delegation_signals.py`; NOT read by REST or PA tools |
| **LLMCallLog** | `core/models_llm_routing.py:297-362` | S697 | HAS cost (DecimalField at :335), total_tokens (:331), latency_ms (:332), trace_id (S697 correlation via 0299 migration), agent_name, provider, model | 30-day retention via `cleanup_llm_call_logs` at `tasks.py:4408` | Read by REST endpoints (`llm_call_logs_list`, `cockpit_cost_overview`), PA tool (`cost_telemetry_tool`), `db_health_snapshot` mgmt command |

**Both are actively written** (verified: LLMCallEvent by wrapper's `_create_event_safe`; LLMCallLog by `core/services/agent_llm_router.py:171-173`).

**Consumer split:**
- Cost / usage dashboards → LLMCallLog (has `cost` column; has retention)
- PA tools → LLMCallLog (`cost_telemetry_tool` handler imports LLMCallLog)
- REST APIs → LLMCallLog
- Cat B internal (watchdog, tests) → LLMCallEvent
- Employee OS evidence join (per `docs/topics/employee-os.md:65`) → LLMCallEvent
- Anti-zombie-thread cleanup (Session 1219-1221 Tier 2) → LLMCallEvent

**Root cause hypothesis (SPECULATIVE):** S697 LLMCallLog was originally the LLM-routing decision layer (which provider to use, provider-selection outcome). S1098 introduced LLMCallEvent as the per-invocation execution telemetry with `execution_id` correlation. The two models were meant to serve different scopes but grew overlapping fields (both have provider/model/agent_name/tokens) without an explicit deprecation of LLMCallLog. Confirmation requires reading S697 origin session handoff + S1098 addendum handoffs.

**Consequences:**
- Parent scoping §3.B (F6 drift) was written against LLMCallLog's field shape while pointing at LLMCallEvent's file:line — evidence that even senior authors confuse the two.
- Cost reporting flows through LLMCallLog, so F2 PA coverage gap on LLMCallEvent is **partially masked** — PA cost is likely captured in LLMCallLog (SPECULATIVE; requires reading `enforce_real_ai` to confirm).
- Any future consumer needs an explicit decision: LLMCallEvent for execution-boundary telemetry, LLMCallLog for cost/routing.

**Third LLM-cost store exists (Rigby SIGN cycle 1 F1 fold):** `CostTracking` model at `core/models_unified_system.py:6665` is a third LLM-cost persistence surface (verified via Rigby `repo_tool.search`; class body not read at S1702 close — SPECULATIVE on exact overlap with LLMCallLog + LLMCallEvent). Existence reinforces F1 severity: at least three parallel LLM-cost/telemetry stores coexist without an explicit boundary contract. Full CostTracking↔LLMCallLog↔LLMCallEvent triangulation is xx99 scope; do not resolve here.

**Recommendation to xx99 (D73 posture-framing):**
- Do NOT recommend a specific consolidation posture here (D73 forbids). 
- DO surface as xx99 posture-decision axis: (a) deprecate LLMCallLog + migrate consumers to LLMCallEvent (adds cost column + retention to LLMCallEvent); (b) deprecate LLMCallEvent + migrate S1221 watchdog to LLMCallLog; (c) formalize dual-model contract (LLMCallEvent = execution telemetry, LLMCallLog = cost/routing; ADR defining boundary + preventing further overlap); (d) triangulate all three (LLMCallEvent + LLMCallLog + CostTracking) into a single canonical LLM observability model + retire the other two.

### Other overlap candidates

- **No provider-specific parallel telemetry models** (no OpenAILogEntry, AnthropicUsage, etc.). Explore 1 verified.
- **AgentExecution denormalization** — none of 3 AgentExecution classes carries `llm_call_count` or `total_tokens`. No denormalization to reconcile.
- **CostTracking model at `core/models_unified_system.py:6665`** — third LLM-cost store surfaced by Rigby SIGN cycle 1 F1 fold. Reinforces F1 severity; full triangulation deferred to xx99.

---

## 18. Ownership Gaps

**Q25 (§9): Who owns Cat B?**

### Named owner search

- **`models_llm_telemetry.py` module docstring**: Session 1098 attribution only. No person named.
- **`llm_call_wrapper.py` module docstring**: Session 1098 attribution only. No person named. References "conversation pa-3c7ddc058db1 (Rigby's boardroom-dispatch remediation, PR #1 of 4)" — that identifies the design conversation but not a code owner.
- **`check_direct_llm_calls.py`**: Session 1098 PR #A2 attribution. No person named.
- **`.github/workflows/check-llm-sdk.yml`**: References Session 1222 P5 (enforce promotion). No person named.
- **CODEOWNERS file**: Not verified to exist at repo root (SPECULATIVE — Explore 6 checked; assumed absent).

### Gap #1: No human owner named in any Cat B module

All attribution is by session number or audit tag. No MAINTAINER file. No CODEOWNERS entry. If Cat B design questions arise between sessions, the routing path is "read handoff, then ask Chris" — no direct Cat B owner exists.

### Gap #2: F1 duplication has no owner-of-consolidation

LLMCallEvent (S1098) + LLMCallLog (S697) coexist. Neither module docstring acknowledges the other; no dead-code or deprecation note. Consolidation decision has no explicit owner.

### Gap #3: Cross-cat responsibility for F2 PA path is ambiguous

PA path (unified_pa_entrypoint + llm_enforcer) does not import wrapper. Whose responsibility is it to fix — Cat B author (wrapper design) or PA path author (adoption)? No convention exists.

---

## 19. Recommended Future Research

Ranked by (architectural uncertainty × risk × unblocked flows).

### R1 (HIGH priority) — PA path wrapper adoption (F2)

**Question:** Should `unified_pa_entrypoint._enforce_real_ai` and `llm_enforcer.py` route through `llm_call_span` / `llm_call_async`? If yes, what's the coverage plan for the multi-iteration agentic loop (per-iteration span or one span for the whole `process_message`)?

**Evidence:** F2 CRITICAL — verified 0 imports at Task 4 verifier-loop. Dominant LLM caller has zero LLMCallEvent visibility.

**Blockers:** None identified. LLMCallEvent supports nullable execution_id (PA calls may have no AgentExecution row), so adoption is low-risk.

**Estimated scope:** 1-2 sessions of code work + 1 session of Rigby SIGN (design decision on per-iteration vs per-message span).

**Not xx99 scope** — belongs to PA-integration follow-on, not anchor-update.

### R2 (HIGH priority) — F1 dedup posture (LLMCallEvent vs LLMCallLog)

**Question:** What is the intended split of responsibility between LLMCallEvent (S1098) and LLMCallLog (S697)? Is one deprecated? Are both canonical for different concerns? xx99 (S1799) posture-decision axis.

**Evidence:** F1 CRITICAL — verified both models actively written; consumer split confirmed.

**Blockers:** Requires reading S697 origin + S1098 addendum handoffs to reconstruct design intent. Chris ratification needed for posture (D73 posture-framing).

**Estimated scope:** xx99 scope. Consolidation implementation is post-arc T-slot per D73.

### R3 (HIGH priority) — LLMCallEvent retention posture (F4)

**Question:** Should LLMCallEvent have date-based retention analog to Cat A's 30-day? Or is it meant to be forever-retained for postmortem (per S1098 module docstring "so telemetry survives AgentExecution row deletion")?

**Evidence:** F4 HIGH debt — unbounded accumulation.

**Blockers:** Requires product decision on retention window.

**Estimated scope:** 1 session code work (add `LLM_CALL_EVENT_RETENTION_DAYS` env + beat task) once posture is decided. xx99 candidate for D74 axis if posture ties to F1 dedup decision.

### R4 (MEDIUM priority) — `_extract_usage` provider-shape coverage (F3)

**Question:** Should `_extract_usage` handle Gemini + Ollama shapes even though no production caller uses them today? Or wait until adoption drives the fix?

**Evidence:** F3 latent gap — Gemini/Ollama shapes at `llm_provider_registry.py:847-848` + `:969-970` don't match wrapper's OpenAI/Anthropic-shape extractor.

**Blockers:** None. Low-risk 2-branch addition to `_extract_usage`.

**Estimated scope:** 0.5 session code work + tests. §22 default queue lean: add to xx99 anchor-update bundle (P0 pre-emptive fix).

### R5 (MEDIUM priority) — S1224 budget-exhausted observability (D5)

**Question:** Should Cat B add `error_type='budget_exhausted'` bucket + wrapper-side detection of `finish_reason='length'` + `output_tokens=0`? Or leave budget floor enforcement to caller convention?

**Evidence:** D5 SPECULATIVE — S1224 memory rule documents diagnostic; no observability guard exists.

**Blockers:** Requires wrapper to inspect response shape (adds coupling to provider response format).

**Estimated scope:** 0.5-1 session code work + tests.

### R6 (MEDIUM priority) — Cat B/Cat D correlation gap (T-6)

**Question:** Should ToolCallRecord add `execution_id` + `tool_call_id` fields to enable the parent §3.B accounting rule dedup between Cat B and Cat D?

**Evidence:** T-6 MEDIUM debt — accounting rule cites schema fields that don't exist.

**Blockers:** Cat D scope (S1704). Do not pre-empt.

**Estimated scope:** Cat D audit (S1704) inherits. Post-arc T-slot if it becomes a design-preparation project.

### R7 (MEDIUM priority) — MissionRunner LLM-cost attribution (T-8)

**Question:** Should MissionRunner thread `mission_id` into `llm_call_span` metadata + add GIN index on `LLMCallEvent.metadata->>'mission_id'`? Or should OpsRun aggregate LLM cost differently?

**Evidence:** T-8 MEDIUM debt — missions cannot attribute LLM cost via LLMCallEvent.

**Blockers:** Cat E scope (S1705). Do not pre-empt.

**Estimated scope:** Cat E audit (S1705) inherits.

### R8 (LOW priority) — Best-effort telemetry silent-failure metric (T-10)

**Question:** Add counter `LLM_CALL_EVENT_SAVE_ERROR_TOTAL` + WARN log level for swallowed exceptions in `_save_event_safe` + `_create_event_safe`?

**Evidence:** T-10 LOW debt — observability of Cat B itself is fragile.

**Blockers:** None.

**Estimated scope:** 0.5 session code work.

### R9 (LOW priority) — Realtime WebSocket push of LLMCallEvent (S1701 R7 analog)

**Question:** Should Cat B realtime push mirror Cat A's proposal (S1701 R7 LOW)?

**Evidence:** No consumer demand at HEAD.

**Blockers:** Downstream to any dashboard that wants realtime.

**Estimated scope:** Do not build until consumer demand is real.

### R10 (LOW priority) — Documentation gap — dedicated `docs/topics/llm-telemetry.md`

**Question:** Should Cat B have an operator handbook analog to `celery-workers.md`?

**Evidence:** No such doc exists at HEAD.

**Blockers:** Requires xx99 to decide F1 dedup posture first (documenting current state is misleading if F1 is unresolved).

**Estimated scope:** Post-xx99. 1 session doc work.

---

## 20. Appendix

### 20.1 Files inspected

- `core/models_llm_telemetry.py` (115 lines) — LLMCallEvent model
- `core/services/llm_call_wrapper.py` (465 lines) — wrapper public + internal API
- `core/models_llm_routing.py:297-362` (LLMCallLog fields F1 verifier read)
- `core/tasks.py:415` + `:4408` (cleanup task delegations)
- `core/tasks_agents.py:1659-1720` (_impl_cleanup_stale_llm_calls implementation)
- `docs/research/domains/observability/1700_observability_domain_scoping.md` §3.B + §5 F5 box
- `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md` §9, §14, §16, §17, §20.5 (template inheritance)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop + §15 SIGN cycle 1
- Read-only spot-checks of `unified_pa_entrypoint.py` + `llm_enforcer.py` (0 wrapper-import verification)

### 20.2 Docs inspected

- `PLATFORM_WHAT_IT_IS.md` §OpenAI hardening (lines 436-462)
- `PLATFORM_INVENTORY.md` LLM Providers section
- `docs/topics/employee-os.md:65` (LLMCallEvent as evidence-join source)
- `docs/topics/active-module-ownership-map.md:23`
- `docs/topics/agent-system.md:78-87, 142-145`
- Session handoffs: S1098 + S1214-1216 + S1220-1224 + S1222 P5

### 20.3 Grep patterns used

- `class LLMCallEvent` — model definition
- `from core.services.llm_call_wrapper|llm_call_span|llm_call_async` — wrapper call sites (23 production + 2 test files)
- `LLMCallEvent.objects.create|.save|.update` — direct write attempts (0 outside wrapper)
- `llm_call_id|llm_execution_id` — downstream scalar references (0 hits)
- `class LLMCallLog|cost\s*=\s*models\.|total_tokens\s*=\s*models\.|latency_ms\s*=\s*models\.` — F1 sibling model fields
- `cleanup_stale_llm_calls|cleanup_llm_call_logs|def cleanup.*llm` — cleanup task inventory
- `llm_call_span|llm_call_async|from core\.services\.llm_call_wrapper` in `unified_pa_entrypoint.py` + `llm_enforcer.py` — F2 verifier-loop (0 hits both files)

### 20.4 Unresolved unknowns

- **UNK-1**: BaseAgent primary LLM call path (`_call_openai`) — does it route through `llm_call_span`? Grep shows only `LLMCallCancelled` import at `base_agent.py:4723`. Method exists at `:2597`. Full method body not inspected. **SPECULATIVE**; UNK for §19 R1 inheritance.
- **UNK-2**: `enforce_real_ai` — does it write LLMCallLog (F1 sibling)? If so, PA cost is captured but not correlated to execution_id. Not inspected in detail at S1702 close. **SPECULATIVE**.
- **UNK-3**: `employees/status.py` + `signals/rigby_delegation_signals.py` reads of LLMCallEvent — read intent unclassified. SPECULATIVE.
- **UNK-4**: LLMCallEvent row null-rate on `execution_id` at HEAD. Not queried at S1702 close (would require ORM shell). D74 axis input for xx99.
- **UNK-5**: Are Together AI / DeepSeek callers actually using wrapper today, or does adoption skew even harder to OpenAI/Anthropic? Not verified per-provider at S1702 close.
- **UNK-6**: `_extract_usage` return for Gemini/Ollama when adopted — tested? No dedicated test in `test_llm_call_wrapper.py` (SPECULATIVE — inferred from Explore 6).

### 20.5 Rigby SIGN cycle 1 fold notes

Rigby SIGN cycle 1 completed 2026-07-03 on fresh SIGN isolation pin `pa-c3927ab78c52479a` (minted per playbook §15 discipline; routed-around by `tools/pa_local.sh:128` wrapper hard-code to arc pin `pa-e7fbacc996b34b44` per S1600/S1700/S1701 precedent). D48 preemptive stability-probe gate 19th arm HOLDING CLEAN — Rigby responded substantively on turn 1 to single-batch 4-question pattern per S1701 precedent.

**Verdict: SIGN-with-edits at Medium-High confidence.**

**Q1 CONFIRM (Medium-High) — Coverage-completeness:**
- Rigby verified via `repo_tool.search` that wrapper import file set matches (7 agents + tasks + service + tests + wrapper itself). 23-site count "plausible" but not independently enumerated by Rigby.
- Rigby verified F2 PA path 0 wrapper imports and additionally cross-checked that `llm_enforcer.py` is heavily tied to LLMCallLog (not wrapper).
- **New finding surfaced:** `CostTracking` model exists at `core/models_unified_system.py:6665` — a third LLM-cost store beyond LLMCallEvent + LLMCallLog. Reinforces F1 rather than negates it.

**Q2 CONFIRM (High) — Drift-severity + finding-classification:**
- F1 CRITICAL correct: "two concurrently-written, differently-consumed LLM telemetry models is canonical observability poison."
- F2 CRITICAL correct: "PA being the highest-volume interactive path yet producing 0 Cat B rows is a top-tier coverage failure."
- F3 MEDIUM-latent correct as framed. Would NOT elevate to CRITICAL absent evidence of active Gemini/Ollama wrapper adoption.
- D5 keep as SPECULATIVE/MEDIUM. T-1 through T-12 severities all correct.

**Q3 CONFIRM (Medium-High) — D74 axis contribution:**
- call_id + execution_id posture correct. "Cat B does NOT own a cross-model spine analog to task_id" correct and defensible.
- **F2 fold (MEDIUM):** The "execution_id NOT NULL + FK" step in the D74 work-chain is NOT universally required — it's one option that conflicts with the stated "telemetry survives AgentExecution deletion" rationale. Reframe as option set: NOT NULL + FK OR standardize correlation view / shared join contract. Fold applied to §1 (Executive Summary) + §9 (D74 axis contribution).

**Q4 CONFIRM (Medium-High) — R1-R10 ranking + xx99 scope discipline:**
- Ranking R1 > R2 > R3 > R4 defensible.
- R4 stays MEDIUM per §22 default-queue lean (cheap fix; explicitly latent until wrapper is used with those providers).
- xx99 discipline maintained — R2 correctly kept as evidence-plan-only, not "merge these models now."
- **Suggested addition:** R6 Cat B/Cat D correlation gap could be an explicit R-item beyond §9 integration-gap mention. Verification: **R6 already exists in §19 as MEDIUM priority "Cat B/Cat D correlation gap (T-6)"** — Rigby's suggestion already reflected in the audit.

**Folds landed pre-commit (F1-F3):**
- **F1 (LOW)** — §1 executive summary + §17: added CostTracking as third LLM-cost store (`core/models_unified_system.py:6665`), reinforcing F1 severity; full triangulation deferred to xx99. Added §17 "Other overlap candidates" row + expanded xx99 recommendation option (d) to triangulate all three stores.
- **F2 (MEDIUM)** — §1 executive summary F9 + §9 D74 axis contribution: reframed "upgrade execution_id to NOT NULL + FK" from mandatory step into explicit option set — (e.i) NOT NULL + FK (breaks survival-of-deletion rationale) OR (e.ii) shared correlation-view / join contract preserving current nullability + non-FK autonomy.
- **F3 (LOW, verification)** — §19 R6 already surfaces Cat B/Cat D correlation gap as MEDIUM R-item; Rigby SIGN cycle 1 suggested it as new R-item but verification confirmed it was already present. No additional fold needed; noted here for provenance.

**Response truncation:** Rigby's response body was truncated mid-"F1 fold text" at the transport layer (`(truncated)` marker at end of body). Fold text was inferred from Rigby's Q1 Coverage-completeness narrative + `CostTracking` grep hit. If additional fold text existed after truncation, it can be recovered on the SIGN pin `pa-c3927ab78c52479a` in future.

### 20.6 Verifier-loop corrections landed

- **Pre-Explore verifier-loop:** Direct-read of `core/models_llm_telemetry.py` established that no `cost` column exists on LLMCallEvent, contradicting parent scoping §3.B field claim. Established as F6 drift going into Explores. Explore 6 independently re-verified and confirmed.
- **Post-Explore verifier-loop:** Direct-read of `core/models_llm_routing.py:297-362` established that `LLMCallLog` (F1 sibling) HAS `cost` (line 335) + `total_tokens` (line 331) + `latency_ms` (line 332). This **explains F6 drift as F1 root cause** — parent scoping was describing LLMCallLog fields. Explore 1 had partially caught the F1 finding; verifier-loop upgraded it to load-bearing.
- **Post-Explore verifier-loop:** Direct grep of `unified_pa_entrypoint.py` + `llm_enforcer.py` for wrapper imports returned 0 hits in both files, confirming F2 CRITICAL PA-path bypass.
- **Post-Explore verifier-loop:** Direct grep + read of `_impl_cleanup_stale_llm_calls` at `tasks_agents.py:1659-` confirmed it targets `LLMCallEvent` (line 1685 imports + line 1697 filters). Reconciled Explore 3 vs Explore 6 conflict: LLMCallEvent has stuck-STARTED sweep (Cat B watchdog), LLMCallLog has retention (F1 sibling). Cat B has NO retention analog to Cat A — confirmed F4.
- **Post-Explore verifier-loop:** Direct grep + count of production `llm_call_span` / `llm_call_async` invocations across all files returned **23 production sites across 8 files** (7 agents + 1 task file + 1 service): content_writer_agent (3), code_review_agent (5), devops_agent (5), tasks_initiatives (5), market_intelligence_agent (2), campaign_orchestrator_agent (1), thinking_agent (1 async), curated_action_card_generator (1). base_agent + agent_router import only `LLMCallCancelled` exception (catch blocks; no wrapper span usage). This reconciles Explore 2's overestimate of 28 sites.

---

**End of S1702 Cat B LLMCallEvent Child Audit.**
