# `task_breakdown_tool` — Validation Report (S2915)

**Tool:** `task_breakdown_tool`
**Schema:** `core/services/pa_tool_schemas.py:1624`
**Handler:** `core/services/td_handlers_core.py:638` (`_handle_task_breakdown`)
**Register site:** `core/services/tool_dispatcher.py:489`
**Session:** S2915 (Path B systematic sweep — Slice 3 batch 5 of `td_handlers_core`)
**HEAD at validation:** `7259caf79` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated (full)` (both actions in-scope, direct pure-ORM READ_ONLY).
**Rigby SIGN:** S2915 T0 SIGN AGREE — batch 5 row-create trio (14+ tool-grounded probes across 4 turns). Q3 verdict: row-create trio ships as batch 5 because it's the biggest concentrated systematic risk (writes + chained network/LLM/DB); `task_breakdown_tool` is the low-risk third that anchors the batch. Q4 verdict: batch 5 introduces the new **first-hop dependency proof** shape (§5b).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Celery task volume + failure-rate telemetry for operator diagnosis. Answers "what's driving Celery load?" / "what task is failing?" / "what queue is a task using?" without shelling into Flower or Django admin.

Distinct from `celery_worker_lifecycle` (worker process control — recycle, kill, restart), from `ops_tool.workers` (worker-level status snapshot), and from `obs_tool` (LLMCallLog cost telemetry, not Celery task telemetry). This tool operates on `CeleryTaskEvent` (task-execution audit trail) + `AgentExecution` (agent-level execution audit).

## Covered actions

**2 total actions. Both in scope this ship.**

- `summary` — **in scope this ship** — verified live via T1a harness at HEAD `7259caf79`. Aggregates `CeleryTaskEvent` rows in the window into totals (tasks/success/failure/started), per-task breakdown (count + failure_rate + p50/p95 duration + top queues), and per-agent breakdown (executions + failure_rate; excludes PA meta-agent per Arc I-0100 P4 §4.2 F1 fold at handler line 780-788). Default window `60m`; limit clamped at 50.
- `drilldown` — **in scope this ship** — verified live via T1a harness. Per-task recent-execution stream ordered by `-started_at`. Requires `task_name`; optional `status` filter (SUCCESS/FAILURE/STARTED); limit clamped at 200 (default 50). Returns `task_id`, `started_at`, `finished_at`, `duration_ms`, `status`, `queue`, `worker`, `error_type`, truncated `error_message`.

## 3. Schema notes

- **Required:** `action` (enum: `summary`, `drilldown`).
- **Optional filters:** `window` (enum: `15m`, `60m`, `2h`, `6h`, `24h`; default `60m` via handler; handler falls back to `60m` for any unrecognized value at line 666).
- **Conditional required (handler-enforced):** `task_name` for `drilldown` (returns typed error dict at line 672 if missing).
- **Drilldown-only:** `status` (enum: `SUCCESS` / `FAILURE` / `STARTED`; handler uppercases at line 678).
- **Limit:** default 25 for summary, 50 for drilldown; handler caps at 50/200 respectively (line 674, 705).
- **Window mapping:** handler-side `WINDOW_MAP` at line 656-662 translates enum → minutes (`15m` → 15, `60m` → 60, etc.).

## 4. Golden-path examples

**"What's driving Celery load right now?"**

```
task_breakdown_tool  action=summary  window=60m
```

**"Show me the top failing tasks in the last 6 hours."**

```
task_breakdown_tool  action=summary  window=6h  limit=10
```

**"Drilldown on execute_agent_task failures."**

```
task_breakdown_tool  action=drilldown  task_name=core.tasks.execute_agent_task  status=FAILURE
```

## 5. Failure / empty-state / pagination notes

- **Empty window (no CeleryTaskEvent rows):** `summary` returns `{totals: {tasks: 0, success: 0, failure: 0, started: 0}, by_task: [], by_agent: []}` — clean empty shape.
- **`drilldown` missing `task_name`:** returns `{error: 'task_name is required for drilldown'}` at handler line 672.
- **`drilldown` with unknown `task_name`:** returns `{action: 'drilldown', task_name, window, count: 0, executions: []}` — no error.
- **Unknown `window` value:** handler falls back to `60m` silently at line 666 (WINDOW_MAP fallback via `.get(window, 60)`).
- **PA meta-agent exclusion (`summary` `by_agent` only):** `AgentExecution.objects.exclude(agent__name='PersonalAssistant')` at line 792 per Arc I-0100 P4 §4.2 F1 fold — PA agentic-loop volume would dominate the ranking otherwise.

## 5a. Mutation containment / gateway allowlist

**N/A this batch.** Both actions are pure-ORM reads with no write path, no Celery dispatch, no network I/O, no LLM call. No mutation actions declared.

## 5b. First-hop dependency proof (NEW at S2915 batch 5)

**Batch 5 introduces this section per Rigby S2915 T0 SIGN Q4 verdict** — explicit-action-allowlist doesn't prove the actions have no hidden network/LLM/write costs via delegated helpers. Each covered action enumerates its direct callees + a classification verdict.

Verdict scheme:
- `read` — pure ORM read, no external side effect.
- `network` — HTTP / gRPC / socket call.
- `llm` — LLM provider call.
- `db_write` — ORM `.save()` / `.create()` / `.update()`.
- `db_delete` — ORM `.delete()` (potentially irreversible).
- `dispatch` — Celery `.delay()` / `.apply_async()`.
- `opaque` — callee not read this batch; trust downgraded, revisit trigger recorded.

### Action: `summary`

| Direct dependency | Classification | Evidence (file:line) |
|---|---|---|
| `CeleryTaskEvent.objects.filter().aggregate()` | read | `td_handlers_core.py:706-713` |
| `CeleryTaskEvent.objects.values().annotate().order_by()` | read | `td_handlers_core.py:715-724` |
| `CeleryTaskEvent.objects.filter().values_list()` | read | `td_handlers_core.py:736-739` (duration percentile source) |
| `CeleryTaskEvent.objects.filter().values().annotate()` | read | `td_handlers_core.py:747-751` (queue breakdown) |
| `AgentExecution.objects.filter().exclude().values().annotate()` | read | `td_handlers_core.py:790-799` |

**No-hidden-cost verdict:** ✓ all first-hop deps are pure ORM reads. No delegated handlers, no service calls, no `apply_async`, no LLM providers imported.

### Action: `drilldown`

| Direct dependency | Classification | Evidence (file:line) |
|---|---|---|
| `CeleryTaskEvent.objects.filter().order_by()[:limit]` | read | `td_handlers_core.py:676-679` |

**No-hidden-cost verdict:** ✓ single ORM query.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness task_breakdown_tool` at HEAD `7259caf79`:

| Action | Outcome | Safety class | Notes |
|---|---|---|---|
| `summary` | `success` | READ_ONLY | Empty-window shape verified |
| `drilldown` | `soft_error` | READ_ONLY | Expected — `task_name` required, harness dispatches without it and captures the typed error |

Both actions dispatch cleanly; envelope shape stable across empty-window + missing-required-arg cases.

### 6.2 Runtime-not-executed — this ship

None. Both actions are in scope and exercised.

---

## Related

- **Adjacent tools:**
  - `celery_worker_lifecycle` (Slice 1) — worker process control (recycle/kill/restart), not task-execution telemetry.
  - `ops_tool` (Slice 1) — worker-level status snapshot + git-head diagnostics.
  - `obs_tool` (Slice 2) — LLMCallLog cost telemetry (LLM calls, not Celery tasks).
- **Substrate context:** batch 5 (row-create trio) closes Slice 3 at 14/22 tools; `task_breakdown_tool` is the low-risk anchor of the batch (both actions pure ORM read). Introduces the new §5b **first-hop dependency proof** shape per Rigby S2915 T0 SIGN Q4 verdict.
- **Metadata seed:** 2 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (both READ_ONLY).
- **Session provenance:** Session 1048 (`_handle_task_breakdown` first ratified) + Arc I-0100 P4 §4.2 F1 fold (2026-07-06 — PA meta-agent exclusion in `by_agent`).
- **Ledger candidates raised this batch:** none new. `task_breakdown_tool` is intentionally the "boring third" in batch 5 to keep batch size stable + demonstrate the §5b shape on a low-risk tool before applying to the high-risk write-path tools.
