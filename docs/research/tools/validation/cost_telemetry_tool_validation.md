# `cost_telemetry_tool` — Validation Report (S2905)

**Tool:** `cost_telemetry_tool`
**Schema:** `core/services/pa_tool_schemas.py:710`
**Handler:** `core/services/td_handlers_agents.py:4854` (`_handle_cost_telemetry`)
**Register site:** `core/services/tool_dispatcher.py:416`
**Session:** S2905 (Path B systematic sweep — Slice 2 batch 1 of `td_handlers_agents`, first accelerated batch post-substrate arc close)
**HEAD at validation:** `6188e2d10`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised via T1a harness).
**Rigby SIGN:** S2905 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only spend telemetry sourced from `LLMCallLog`. Answers "how much have we spent, which agents cost the most, what are the recent LLM calls?" Use when the user asks about real API costs, spend by provider/model/task-type, top spenders, or wants raw call debugging.

Distinct from `check_resource_budget` (which is a *gating* check against a planned operation, not historical spend) and from `body_vitals` (which surfaces oxygen-level budget health, not raw dollar amounts). `cost_telemetry_tool` returns real dollar values from LLM call logs.

## Covered actions

- `summary` — **in scope this ship** — verified live via T1a harness (34ms). Returns `{action, period_hours, total_cost_usd, total_calls, total_tokens, avg_latency_ms, failed_calls, by_provider[], by_task_type[], trend, generated_at}`. Provider + task-type breakdowns capped at top 10. Trend compares current period to previous same-length period.
- `top_agents` — **in scope this ship** — verified live via T1a harness (13ms). Returns `{action, period_hours, agents[], generated_at}`; each agent row has `agent_name, spend_usd, calls, tokens, avg_latency_ms, failures`. Bounded by `limit` (default 10, hard cap 50).
- `recent_calls` — **in scope this ship** — verified live via T1a harness (4ms). Returns `{action, period_hours, calls[], generated_at}`; each call row has `agent, provider, model, task_type, tokens, cost_usd, latency_ms, success, error, at`. `error` field truncated at 200 chars. Bounded by `limit` (default 10, hard cap 50).

## 3. Schema notes

- **Required:** `action` (enum: `summary, top_agents, recent_calls`).
- **Optional:** `hours` (default 24 — lookback window), `limit` (default 10, hard cap 50 — enforced by handler `min(payload.get('limit', 10), 50)`).
- **Handler-effective defaults match schema.** No divergence observed.

## 4. Golden-path examples

**"What have we spent in the last 24h?"**

```
cost_telemetry_tool  action=summary
```

**"Who's spending the most?" — top 20 over 48h:**

```
cost_telemetry_tool  action=top_agents  hours=48  limit=20
```

**"Show me the last 25 calls":**

```
cost_telemetry_tool  action=recent_calls  limit=25
```

## 5. Failure / empty-state / pagination notes

- **No pagination cursor** — `top_agents` + `recent_calls` cap at `limit` (max 50); no `has_more/offset`. For deeper history the caller needs to widen `hours`, not paginate.
- **Silent cap on `limit`** — `min(payload.get('limit', 10), 50)` at line 4873 clamps values > 50 without any `limit_capped` signal in the response. Cross-tool consistency gap (mirrors F-RT-2/F-RT-5 pattern in `repo_tool`).
- **`by_provider` + `by_task_type` silent top-10 cap in `summary`** — line 4898/4909 slice at `[:10]`. No `truncated` signal in response.
- **`summary.trend.cost_change_pct` returns `null` when previous period had zero spend** — line 4924-4926. Explicit fallback; caller must handle `null`.
- **`error` field truncation** — `recent_calls` truncates `error_message` at 200 chars silently.
- **Empty-state on `summary`** — returns `total_cost_usd: 0, total_calls: 0, by_provider: [], by_task_type: []` when the period had no LLM calls. Not exercised live (recent calls present in dev DB).
- **Unknown action returns `_handler_error` envelope** — line 5025-5029. Typed via helper (matches convention).
- **No latency outliers** — 4-34ms observed.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Entire tool is read-only aggregate reads over `LLMCallLog`.
- **Containment protocol:** N/A — no state modification possible.
- **Safety metadata:** `cost_telemetry_tool` seeded in `TOOL_DEFAULTS` at S2905 with `default_safety_class='READ_ONLY'`.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`python manage.py pa_tool_validate_harness cost_telemetry_tool` at HEAD `6188e2d10` (2026-07-23):

- **`summary` (34ms):** `response_shape_keys=['action', 'avg_latency_ms', 'by_provider', 'by_task_type', 'failed_calls', 'generated_at', 'period_hours', 'total_calls', 'total_cost_usd', 'total_tokens', 'trend']` — `success`. 11 top-level keys — richest response shape in this batch.
- **`top_agents` (13ms):** `response_shape_keys=['action', 'agents', 'generated_at', 'period_hours']` — `success`.
- **`recent_calls` (4ms):** `response_shape_keys=['action', 'calls', 'generated_at', 'period_hours']` — `success`.

Artifact: `docs/audits/pa_tools/harness_output/cost_telemetry_tool.json`.

### 6.2 Runtime-not-executed — this ship

- **`limit > 50` silent-cap fire** — not exercised. Would confirm the cap-fires-silently behavior.
- **Zero-spend previous-period `null` fallback** — not exercised (previous period had spend in dev DB).
- **Unknown action `_handler_error` envelope** — not exercised. Handler contract at line 5025-5029.

---

## Related

- **Ledger candidate surfaced this ship** — silent `limit` cap at 50 without response signal. Cross-tool consistency gap; same class as F-RT-2 (`repo_tool` tree cap) + F-RT-5 (`repo_tool` search cap) patterns. Deferred pending Rigby SIGN — batch-close observation, not this-ship blocker.
- **Adjacent tools:** `check_resource_budget` (planning gate, not historical), `body_vitals` (oxygen-level surface, not raw dollars), `revenue_tracker_tool` (this batch — revenue side of P&L).
- **Substrate context:** first opt-in to T1b `Template version: v1` — this doc's shape validates the ratchet-and-warn lint transition from `warn` (advisory) to `pass` in the gap map.
- **Batch peers:** `gates_tool`, `pilots_tool`, `revenue_tracker_tool` (Slice 2 batch 1).
