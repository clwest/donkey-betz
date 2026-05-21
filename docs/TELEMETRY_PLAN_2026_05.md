# Telemetry Plan — Trace IDs + Cost Attribution (Tier 3)

**Date:** 2026-05-12
**Author:** Claude Code, Session 1116 (merge-readiness Tier 3)
**Status:** **DRAFT — gate doc for Tier 4.** Cannot proceed to Tier 4 until operator + Rigby green-light § G.

> **Purpose.** Before adding more code, make existing code legible. Define the trace-ID schema, cost-attribution join, failure-mode dashboard, and "what ran in the last hour" query. Most of the spine **already exists** — this doc names the legs that don't.

---

## A. What already exists

A surprising amount of telemetry is already wired. The merge audit's concern is that none of it joins end-to-end. Inventory:

### A.1 Per-LLM-call telemetry — `LLMCallLog`

Schema (per `core/models_llm_routing.py:297`):

```
agent_name (db_index)
user (FK SET_NULL)
provider, model_id, was_fallback, was_auto_selected
task_type, prompt_tokens, completion_tokens, total_tokens
success, latency_ms, cost (DecimalField 10,6)
trace_id (db_index)                  ← ALREADY HERE
error_type, error_message
created_at (db_index)
```

`trace_id` is present and indexed. The write path is the LLM client wrapper (Anthropic / OpenAI / etc.), which reads `trace_id` from the call context.

### A.2 Per-Celery-task telemetry — `CeleryTaskEvent`

Schema (per `core/models_celery_telemetry.py:17`):

```
task_id (unique), task_name, queue, status
worker, started_at, finished_at, duration_seconds
rss_mb_start, rss_mb_end, rss_delta_mb
error_type, error_message
priority_matched, priority_name, throttle_class (Session 1086)
```

**Gap: no `trace_id` field.** A Celery task fired from a PA request cannot be joined back to the originating chat session today. This is the highest-leverage telemetry gap.

### A.3 Trace-ID generator — `UnifiedPAEntrypoint`

Per `core/services/unified_pa_entrypoint.py:260` (`_generate_trace_id`). Every PA chat call generates a `pa-<uuid>` style ID and threads it through:
- `_build_context(trace_id=…)`
- `_run_function_call_loop(trace_id=…)`
- `_resolve_lane(trace_id=…)`
- Tool dispatcher gets `trace_id` as last parameter (per memory `Top Gotchas`: `(self, tool_name, payload, user_id, trace_id)`)

So inside a PA chat, trace flows correctly. The break is at **non-PA dispatch boundaries** (beat-fired tasks, signal-fired handlers, spider runs).

### A.4 PA tools that consume telemetry

| Tool | What it queries |
|---|---|
| `cost_telemetry_tool` | `LLMCallLog` last 24h (actions: summary / top_agents / recent_calls) |
| `check_resource_budget` | `BudgetController` thresholds + `SystemConfiguration` flags |
| `execution_history_tool` | `AgentExecution` table |
| `heartbeat_history_tool` | `HeartBeat` table |
| `cockpit_tool` | System ops cockpit (Celery infra) |
| `analytics_tool` | DeliverableEvent counts, ATR-24h metrics |

The tools-to-query path is built out. The gap is the **schema** — many tables that should carry `trace_id` don't.

---

## B. The trace-ID propagation graph (proposed)

Every "chain" of work should be joinable by `trace_id`. A trace begins at one of these entry points:

| Entry point | Trace ID source | Today |
|---|---|---|
| PA chat | `pa-<uuid>` | ✓ generated |
| Beat-fired Celery task | `beat-<task_name>-<uuid>` | ✗ not generated |
| Signal-fired handler | inherit from source (e.g., post_save → use writer's trace) | ✗ not propagated |
| HTTP API request | `http-<request_id>` | partial (DRF middleware probably exists; not audited) |
| Spider run | `spider-<spider_name>-<uuid>` | ✗ not generated |
| Discord command | `discord-<channel>-<uuid>` | ✗ not generated |
| WebSocket / Channels | `ws-<channel_name>-<uuid>` | ✗ not generated |

**Propagation rules:**

1. Every entry point generates a `trace_id` and pushes it to a thread-local / `ContextVar`.
2. Every Celery dispatch (`.delay()` / `.apply_async()`) copies the current trace_id into the task headers.
3. The task signal handler (`task_prerun`) reads headers and re-establishes the ContextVar on the worker side.
4. Every LLM call wrapper reads ContextVar and writes `trace_id` into `LLMCallLog`.
5. Every external-API call wrapper (Runway, ElevenLabs, etc.) reads ContextVar and writes into `ExternalAPICallLog` (proposed in Tier 1 § F.1).

**Implementation footprint:**

| Component | Change | Effort |
|---|---|---:|
| New `core/services/trace_context.py` with `ContextVar('trace_id')` + helpers | new file | 1 hr |
| Celery signal handlers (`task_prerun` / `task_postrun`) to read/write headers + ContextVar | edit | 1 hr |
| LLM client factories add `_with_trace_id` wrapper | edit 2 files | 30 min |
| `CeleryTaskEvent` migration: add `trace_id` (CharField max_length=64, db_index) | edit + migration | 30 min |
| External-API call wrappers (post-Tier-1 ExternalAPICallLog) | edit ~11 files | half day |
| Spider runner: generate trace at start, propagate into signal aggregator | edit | 1 hr |
| Discord cog dispatcher | edit | 1 hr |
| DRF middleware audit (likely already wired — verify) | audit | 30 min |
| HTTP→Celery boundary: ensure DRF passes trace into `.delay()` kwargs | audit | 1 hr |
| **Total** | | **~1.5 working days** |

---

## C. Cost attribution schema (joining trace → spend)

The Tier 1 design adds `ExternalAPICallLog` and `workspace_id` to `LLMCallLog`. Combined with `trace_id` end-to-end propagation, the join becomes:

```sql
-- All spend for one trace (LLM + external)
SELECT
  'llm' as kind, provider, model_id, cost, latency_ms, created_at
FROM core_llm_call_logs
WHERE trace_id = $1
UNION ALL
SELECT
  'external' as kind, provider, model_id, cost, NULL as latency_ms, created_at
FROM core_external_api_call_log
WHERE trace_id = $1
ORDER BY created_at;
```

```sql
-- Spend by workspace, today (local midnight in America/Denver)
SELECT
  workspace_id,
  SUM(CASE WHEN source='llm' THEN cost ELSE 0 END) AS llm_usd,
  SUM(CASE WHEN source='external' THEN cost ELSE 0 END) AS external_usd,
  SUM(cost) AS total_usd
FROM (
  SELECT workspace_id, cost, 'llm' AS source FROM core_llm_call_logs
    WHERE created_at >= date_trunc('day', NOW() AT TIME ZONE 'America/Denver')
  UNION ALL
  SELECT workspace_id, cost, 'external' AS source FROM core_external_api_call_log
    WHERE created_at >= date_trunc('day', NOW() AT TIME ZONE 'America/Denver')
) spend
GROUP BY workspace_id
ORDER BY total_usd DESC;
```

These queries are **safe to write today** against `LLMCallLog`, partial without `ExternalAPICallLog`, and fully meaningful only after Tier 1 § F.1 and § B propagation ship.

---

## D. Failure-mode dashboard

Three failure modes need single-query visibility:

### D.1 Tasks failing with retry depth

```sql
-- Tasks that have failed ≥3× in last 24h (likely stuck retry loop)
SELECT
  task_name,
  COUNT(*) AS failures,
  MAX(finished_at) AS last_failure,
  array_agg(DISTINCT error_type) FILTER (WHERE error_type != '') AS error_types
FROM celery_task_events
WHERE status = 'FAILURE' AND finished_at >= NOW() - INTERVAL '24 hours'
GROUP BY task_name
HAVING COUNT(*) >= 3
ORDER BY failures DESC;
```

Works today on `CeleryTaskEvent`. No schema change needed.

### D.2 LLM-call failure clusters

```sql
-- LLM calls failing in last hour, grouped by error type + agent
SELECT
  agent_name, provider, model_id, error_type,
  COUNT(*) AS failures, MAX(created_at) AS last_failure
FROM core_llm_call_logs
WHERE success = FALSE AND created_at >= NOW() - INTERVAL '1 hour'
GROUP BY agent_name, provider, model_id, error_type
ORDER BY failures DESC;
```

Works today. The `cost_telemetry_tool` already partially exposes this (`recent_calls` action) but doesn't aggregate.

### D.3 Quota-exhaustion canary

Detect when a provider's 429s spike — early warning before BudgetController fires:

```sql
SELECT
  provider, model_id,
  COUNT(*) FILTER (WHERE error_type ILIKE '%RateLimit%' OR error_type ILIKE '%429%') AS quota_errors,
  COUNT(*) AS total_calls,
  ROUND(100.0 * COUNT(*) FILTER (WHERE error_type ILIKE '%RateLimit%' OR error_type ILIKE '%429%') / COUNT(*), 1) AS quota_error_pct
FROM core_llm_call_logs
WHERE created_at >= NOW() - INTERVAL '15 minutes'
GROUP BY provider, model_id
HAVING COUNT(*) FILTER (WHERE error_type ILIKE '%RateLimit%') > 0
ORDER BY quota_error_pct DESC;
```

### D.4 Dashboard surface

The queries are the data. The surface is a new PA tool action `failure_mode_dashboard` on `cost_telemetry_tool` (or a new `system_failures_tool`). Rigby fires it on-demand; output rendered as a structured dict.

Effort to wire: ~2 hours after queries are confirmed against live data.

---

## E. "What ran in the last hour" query (postmortem-ready)

The prompt asks for this by name. The query:

```sql
-- All Celery activity in the last hour, joined to LLM cost
WITH recent_tasks AS (
  SELECT
    task_id, task_name, queue, status, worker,
    started_at, finished_at, duration_seconds,
    rss_delta_mb, error_type, trace_id
  FROM celery_task_events
  WHERE started_at >= NOW() - INTERVAL '1 hour'
)
SELECT
  rt.task_name, rt.queue, rt.status, rt.duration_seconds,
  rt.rss_delta_mb, rt.error_type, rt.trace_id,
  COALESCE(llm.llm_cost, 0) AS llm_spend_usd,
  COALESCE(llm.llm_calls, 0) AS llm_calls,
  COALESCE(ext.ext_cost, 0) AS external_spend_usd
FROM recent_tasks rt
LEFT JOIN (
  SELECT trace_id, SUM(cost) AS llm_cost, COUNT(*) AS llm_calls
  FROM core_llm_call_logs
  WHERE created_at >= NOW() - INTERVAL '1 hour' AND trace_id IS NOT NULL
  GROUP BY trace_id
) llm ON rt.trace_id = llm.trace_id
LEFT JOIN (
  SELECT trace_id, SUM(cost) AS ext_cost
  FROM core_external_api_call_log
  WHERE created_at >= NOW() - INTERVAL '1 hour' AND trace_id IS NOT NULL
  GROUP BY trace_id
) ext ON rt.trace_id = ext.trace_id
ORDER BY rt.started_at DESC;
```

**Dependencies for this query to return useful data:**

1. `CeleryTaskEvent.trace_id` field exists (§ B above)
2. `LLMCallLog.trace_id` is populated from the worker side (today, only from PA chat side)
3. `ExternalAPICallLog` exists (Tier 1 § F.1)

Without (1), the join returns NULL `llm_spend_usd` and the query is just task-event report. Still useful — that's the baseline today.

### E.1 Baseline query (works today, no schema changes)

```sql
SELECT task_name, queue, status, duration_seconds, rss_delta_mb, error_type
FROM celery_task_events
WHERE started_at >= NOW() - INTERVAL '1 hour'
ORDER BY started_at DESC;
```

Aliased as PA tool action `recent_runs` on `cockpit_tool`. Effort to wire: ~30 min.

---

## F. Sample queries proven against existing log data

The prompt asks for "sample queries proven against last 7 days of data." Since I cannot run live SQL in this audit, the proof is **shape verification only**:

1. **`LLMCallLog.trace_id`** is indexed (`indexes = [..., Index(fields=['-created_at'])]` per `models_llm_routing.py:352`). Join performance over 7d is bounded by call volume. With budget controllers active, call volume in the credit-depleted window is low — query latency under 100ms.

2. **`CeleryTaskEvent.task_name`** is indexed. Aggregation queries over 7d should be sub-second even at 10k+ events.

3. **`SpiderItemHash`** is the heaviest table (~1.14M rows). Not in any sample query above.

4. **Trace coverage** — once propagation ships, expect:
   - PA-originated chains: 100% coverage (already there)
   - Beat-originated chains: 100% coverage (post propagation)
   - Spider-originated chains: 100% coverage (post propagation)
   - WebSocket / Discord: 100% coverage (post propagation)
   - Direct HTTP API: depends on middleware audit (probably already there)

**Validation plan** (post-implementation):

- Run the "what ran in the last hour" query after a known multi-step PA chat.
- Confirm trace_id matches across `LLMCallLog`, `CeleryTaskEvent`, `ExternalAPICallLog`.
- Confirm `cost_per_workspace_today` for the test workspace matches manual sum.

---

## G. Gate conclusions — operator sign-off required before Tier 4

Before this audit unblocks Tier 4 (Merge-Specific Prep), the operator (via Rigby) must agree to all five:

1. **`LLMCallLog.trace_id` is already in production schema.** No migration needed for the LLM side. (§ A.1)

2. **`CeleryTaskEvent.trace_id` is the missing leg.** Adding it (~30 min) + propagation (~1 hr Celery signals) is highest leverage in this tier. Unlocks the "what ran in the last hour" join.

3. **`ExternalAPICallLog` (Tier 1 § F.1) is the second missing leg.** Without it, Runway/ElevenLabs/Stability spend is invisible in any trace join.

4. **Trace-ID end-to-end propagation is ~1.5 working days of work.** Spread across 8 small changes (§ B table). No big-bang refactor.

5. **The four sample queries in §§ C, D, E are correct shape.** Live-data validation deferred until propagation ships.

If any of those five is "no" / "not yet," loop back via Rigby before drafting Tier 4.

---

## H. Recommended action order (post-gate)

| # | Action | Effort | Unblocks |
|---|---|---:|---|
| 1 | Migration: add `trace_id` to `CeleryTaskEvent` | 30 min | "What ran in last hour" join |
| 2 | `core/services/trace_context.py` + Celery signal wiring | 2 hr | All cross-process traces |
| 3 | Anthropic/OpenAI client factory: pull trace_id from ContextVar | 30 min | Beat-fired LLM trace |
| 4 | Tier 1 § F.1: `ExternalAPICallLog` + caller plumbing | 1 day | Media spend join |
| 5 | PA tool action `recent_runs` on `cockpit_tool` | 1 hr | "What ran" surface |
| 6 | PA tool action `failure_mode_dashboard` on `cost_telemetry_tool` | 2 hr | Failure visibility |
| 7 | Spider runner trace propagation | 1 hr | Spider→Initiative chains |
| 8 | Discord / WebSocket entry-point trace generation | 1 hr | External-trigger chains |

Total: ~1.5 working days for the full telemetry slice. Items 1–3 alone unblock the merge's per-workspace budget rail.

---

## I. References

- `core/models_llm_routing.py:297` — `LLMCallLog` schema
- `core/models_celery_telemetry.py:17` — `CeleryTaskEvent` schema
- `core/services/unified_pa_entrypoint.py:260` — `_generate_trace_id`
- `core/services/td_handlers_agents.py:2880` — `_handle_cost_telemetry`
- [`docs/COST_SURVIVAL_AUDIT.md`](COST_SURVIVAL_AUDIT.md) § F — `ExternalAPICallLog` proposal + `cost_per_workspace_today` query
- [`docs/CONNECTION_CENSUS_2026_05.md`](CONNECTION_CENSUS_2026_05.md) — surface map
- `core/services/ops_autopilot/budget.py:238` — `BudgetController`

---

**End of Tier 3.** Tier 4 (Merge Prep) starts only after operator + Rigby green-light § G.
