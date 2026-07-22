# `scheduled_tasks_tool` — Validation Report (S2893)

**Tool:** `scheduled_tasks_tool`
**Schema:** `core/services/pa_tool_schemas.py:807`
**Handler:** `core/services/td_handlers_ops.py:6350` (`_handle_scheduled_tasks`)
**Register site:** `core/services/tool_dispatcher.py:483`
**Session:** S2893 (Path B systematic sweep — Slice 1 batch 2 of `td_handlers_ops`)
**HEAD at validation:** `387ac953e`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live, including a full net-zero canary on mutating actions).
**Rigby SIGN:** S2893 T1 SIGN AGREE-clean.

---

## 1. Purpose / when-to-use

Beat-schedule surface for Rigby. View and control `PeriodicTask` rows: list, search, paginate, enable, disable. Use when asked "what runs automatically?", "is the daily X job on?", or "disable Y until we're done debugging."

Distinct from `celery_tool` / raw celery-worker introspection — this reads `django-celery-beat` `PeriodicTask` rows only, not the running-workers or task-queue state.

## Covered actions

- `list` — **in scope this ship** — verified live twice: default params (`total_enabled=94, showing=50`) and expanded (`show_disabled=true, limit=100` → `filtered=99, showing=99`). Returns per-row `name, task, schedule (cron string), queue, enabled, last_run, total_runs`.
- `enable` — **in scope this ship** — verified live with net-zero canary on `backfill-spider-embeddings`. Flipped OFF → ON successfully.
- `disable` — **in scope this ship** — verified live with net-zero canary on the same row. Flipped ON → OFF successfully. Post-state verified via `.list` filter (`enabled=false` restored). See §6.1 finding.

## 3. Schema notes

- **Required:** none (schema declares `required: []`, defaults to `action=list`).
- **Optional:** `action` (enum: `list, enable, disable`), `name`, `task_id`, `search`, `show_disabled`, `limit` (default 50, max 100), `offset`.
- **Enable/disable identifier semantics:** accepts either `name` (canonical PeriodicTask name string) or `task_id` (numeric row ID or exact name). Exercised via `name` this ship.
- **Schema description lint:** clean — explicit that `enable/disable` requires the row identifier.

## 4. Golden-path examples

**Default listing (enabled tasks, first page):**

```
scheduled_tasks_tool  action=list
```

**Full listing including disabled rows:**

```
scheduled_tasks_tool  action=list  show_disabled=true  limit=100
```

**Substring search:**

```
scheduled_tasks_tool  action=list  search=spider
```

**Enable then disable back (net-zero canary):**

```
scheduled_tasks_tool  action=list  search=<name>  show_disabled=true   # verify starting state
scheduled_tasks_tool  action=enable  name=<name>
scheduled_tasks_tool  action=disable  name=<name>
scheduled_tasks_tool  action=list  search=<name>  show_disabled=true   # verify enabled=false
```

## 5. Failure / empty-state / pagination notes

- **Pagination via `limit` + `offset`** — response includes `total_enabled`, `filtered`, `showing`, `offset`. Advance `offset += limit` until `showing < limit` (no explicit `has_more` flag in this tool).
- **`show_disabled=true` widens the result set** — observed `filtered=99` vs default `filtered=94` (5 disabled rows exist at HEAD `387ac953e`).
- **`enable`/`disable` are idempotent at the row level** — flipping an already-enabled row to enabled returns `success=true` without changing state. Confirmed acceptable by design.
- **`last_run=null`** on some enabled rows is normal (row exists but has not fired yet, or was manually reset).
- **No latency outliers** — all actions <50ms observed.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** `enable`, `disable`.
- **Containment protocol applied this ship:**
  1. Pre-check: `.list` with `show_disabled=true` to identify a genuinely-disabled row (`backfill-spider-embeddings`, `enabled=false`, `last_run=null`).
  2. Timebox: enable + immediate disable in the same session (mutation window <1 second).
  3. Post-check: `.list` filtered to the target row verified `enabled=false` restored.
  4. Row selection rationale: `backfill-spider-embeddings` is operator-gated (episodic maintenance, `total_runs=644` historical but currently off) — brief enablement cannot race a beat-tick that would enqueue expensive work.
- **Rollback:** N/A — net-zero achieved by design.
- **Risks NOT tested:** enable-then-crash-before-disable (would leave the row enabled indefinitely); race between enable and a beat-tick firing (window was too short in this session to observe).

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2893 T1 (2026-07-22, HEAD `387ac953e`, pin `pa-7a595cac8cc04bf8`):

**`list` (35ms, defaults):**

```json
{"total_enabled": 94, "filtered": 94, "showing": 50, "offset": 0,
 "filter": "all",
 "tasks": [
   {"name": "aggregate-roi-metrics-daily", "task": "core.tasks.aggregate_roi_metrics_daily",
    "schedule": "cron(0 2 * * *)", "queue": "default", "enabled": true,
    "last_run": "2026-07-22T08:00:00.015607+00:00", "total_runs": 40},
   {"name": "aggregate-spider-signals", "task": "aggregate_spider_signals",
    "schedule": "cron(*/30 * * * *)", "queue": "long_running", "enabled": true,
    "last_run": "2026-07-22T22:30:00.054753+00:00", "total_runs": 1825},
   // ...48 more rows
 ]}
```

**`list` (42ms, `show_disabled=true, limit=100`):**

```json
{"total_enabled": 94, "filtered": 99, "showing": 99, "offset": 0,
 "filter": "all",
 "tasks": [ /* ...99 rows, including 5 disabled */ ]}
```

Reconciles to inventory count: 94 enabled + 5 disabled = 99 PeriodicTask rows (matches `PLATFORM_INVENTORY.md`).

**`enable` (14ms) — canary flip ON:**

```json
{"action": "enable", "name": "backfill-spider-embeddings",
 "enabled": true, "success": true}
```

**`disable` (13ms) — canary flip OFF:**

```json
{"action": "disable", "name": "backfill-spider-embeddings",
 "enabled": false, "success": true}
```

**`list` (10ms) — post-state verify:**

```json
{"total_enabled": 94, "filtered": 1, "showing": 1, "offset": 0,
 "filter": "backfill-spider-embeddings",
 "tasks": [
   {"name": "backfill-spider-embeddings", "task": "core.tasks.backfill_spider_embeddings",
    "schedule": "cron(*/15 * * * *)", "queue": "ml", "enabled": false,
    "last_run": null, "total_runs": 644}
 ]}
```

Post-state confirmed: `enabled=false` restored; `total_enabled` still 94 (net-zero); row's `total_runs=644` unchanged (no fire occurred during the brief enable window).

**Finding — mutation canary succeeded cleanly:** No race observed. `total_runs` remained at 644 across enable/disable, indicating no beat-tick fired the task during the mutation window. The tool surface behaved as designed; `enabled` flag is authoritative.

### 6.2 Runtime-not-executed — this ship

- **`enable` via `task_id`** (numeric ID) — only exercised via `name`. Would confirm both identifier paths work.
- **Search action** (`search=<substring>`) — not exercised as a distinct call; the last `.list` used the filter param but that's the canonical listing path with a name filter, not a semantic-search path.
- **Enable an already-enabled row / disable an already-disabled row** — the idempotency claim in §5 is inferred from handler code shape, not exercised live.
- **`limit=1` / very small pages** — not tested for edge cases in pagination.

---

## Related

- **Ledger candidates surfaced this ship** — none unique to this tool. Behavior matched schema; canary net-zero achieved cleanly. Best-behaved of the 4 tools this batch.
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`.
- **Related tools:** `autopilot_tool` (deferred to Slice 1.5 — includes its own scheduler-report action that reads beat state at a higher level), `governor_tool` (governs whether the tasks that beat entries fire actually dispatch to agents).
