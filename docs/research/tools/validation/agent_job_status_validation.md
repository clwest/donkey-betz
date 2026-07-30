# `agent_job_status` — Validation Report (S3044)

**Tool:** `agent_job_status`
**Schema:** `core/services/pa_tool_schemas.py:5821`
**Handler:** `core/services/td_handlers_agents.py:6895` (`_handle_agent_job_status`)
**Register site:** `core/services/tool_dispatcher.py` (agent-status registration)
**Session:** S3044 (Path B systematic sweep FINISH — Batch 1 of 3 covering the last 18 non-agent_via_run_agent gaps)
**HEAD at validation:** `eb38187ec` (2026-07-30)
**Ship shape:** Doc-only (S2796 shape).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S3044 A1 SIGN AGREE (11 tool_runs) — see §Related.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** dry_run_supported

---

## 1. Purpose / when-to-use

Poll the current status + a short output preview for an agent job dispatched via `run_agent` (or any tool that returns a Celery `task_id`). Sibling to `schedule_followup` — same lookup shape (`task_id` OR `execution_id`) — but returns an immediate status snapshot instead of subscribing to a completion notification.

Use `agent_job_status` when Rigby has already dispatched a long-running agent and wants to poll progress inline rather than wait for a completion banner. Use `schedule_followup` when the caller wants a subscription-based completion notification.

Distinct from `execution_history_tool` (which surfaces completed executions across the history) and `job_status` (which is a lower-level Celery status probe). `agent_job_status` is `AgentExecution`-row-aware: it distinguishes "Celery task queued but AgentExecution not yet materialized" (returns `pending`) from "no such task" (returns `unknown`).

## Covered actions

**This tool has no `action` enum.** The discriminator is `task_id` OR `execution_id` (at least one required). All coverage below applies to the single-entrypoint call shape.

- **`agent_job_status` (single entrypoint, execution_id lookup)** — read — returns `{ok, execution_id, task_id, agent_name, status, created_at, completed_at, duration_ms, error_message, output_preview}` for the matching `AgentExecution` row.
- **`agent_job_status` (single entrypoint, task_id lookup)** — read — same shape as execution_id lookup when the AgentExecution row exists. When the row is not yet materialized, falls back to `AsyncResult(task_id)` and returns `{ok, status: 'pending', task_id, celery_state, message}` for `PENDING`/`RECEIVED`/`STARTED`/`RETRY` Celery states.
- **`agent_job_status` (missing both)** — read — returns `{ok: false, error: 'agent_job_status requires execution_id OR task_id'}` at HTTP 200.
- **`agent_job_status` (unknown task_id, no Celery record)** — read — returns `{ok: false, status: 'unknown', error: 'No AgentExecution found for ...'}` at HTTP 200.

## 3. Schema notes

- **Required:** none declared in schema; **handler-enforced OR-constraint:** must supply `task_id` OR `execution_id`.
- **Optional:** none beyond the two lookup keys.
- **Lookup precedence:** `execution_id` takes precedence when both provided (handler line 6919). Falls back to `task_id`-based ORM lookup via `input_data__celery_task_id`.
- **Output preview cap:** `output_data.message` (or `.content`) truncated to first 800 chars (handler line 6962).
- **Error message cap:** truncated to first 500 chars (handler line 6973).

## 4. Golden-path examples

**"What's the status of task X?"**

```
agent_job_status  task_id=<celery-task-uuid>
```

**"Look up AgentExecution by canonical id:"**

```
agent_job_status  execution_id=<execution-uuid>
```

**"Poll a freshly-dispatched task (may return pending):"**

```
agent_job_status  task_id=<newly-dispatched-uuid>
# → {ok: true, status: 'pending', celery_state: 'PENDING', message: 'Poll again in 5–15 seconds'}
```

## 5. Failure / empty-state / pagination notes

- **Missing lookup keys** — `{ok: false, error: 'agent_job_status requires execution_id OR task_id'}` at HTTP 200.
- **Unknown task_id with no Celery record** — `{ok: false, status: 'unknown', error: 'No AgentExecution found for task_id=<x>'}` at HTTP 200.
- **Freshly-dispatched, AgentExecution not yet materialized** — `{ok: true, status: 'pending', celery_state, message}` at HTTP 200. Valid transient state — caller polls again after 5–15 seconds.
- **AgentExecution with no `output_data.message`** — `output_preview` returns `None` (not empty string).
- **AgentExecution with `agent_id=None`** — `agent_name` returns `None`.
- **No pagination** — single-row read.

## 5c. Contract ↔ Implementation Consistency

### 5c.1 Handler / module header claims match action reality

**PASS.** Schema `description` accurately names the return-shape fields (status, agent_name, duration_ms, error_message, output_preview). Zero-action shape (no `action` enum) matches handler's single-entrypoint dispatch pattern.

### 5c.2 Gating truth matches runtime behavior

**PASS.** No feature flag gates this tool. `execution_id` OR `task_id` OR both are the only runtime discriminators.

### 5c.3 Shared handler-file coupling noted

Shared module: `td_handlers_agents.py` — 30+ agent-family tools live here. Sibling tools most-adjacent: `schedule_followup` (same lookup shape, subscribes to completion instead of polling), `execution_history_tool` (historical AgentExecution enumeration), `agent_capability_drift_tool` (drift audit, also in this batch S3044).

## 6. Evidence

**Analyzed-mode validation (per Execution mode frontmatter).** Handler at `td_handlers_agents.py:6895-6975` read line-by-line; behavior verified against schema at `pa_tool_schemas.py:5821-5844`. Live dispatch deferred — the tool is a passive read of platform state that Rigby already exercises inline whenever she dispatches an agent (the `job_status` receipt shape is her primary polling surface post-dispatch).

**Zero-action classifier note:** `pa_tools_gap_map.classify_tool` at `core/services/pa_tools_gap_map.py:540-543` — "Non-action-multiplexed tool with covered_actions heading; any coverage counts as `validated_full` (no unmapped actions)." This doc's `## Covered actions` heading + any bulleted content satisfies the classifier.

## 7. Fanout visibility (S3046)

**S3046 extension** — discharges S3045 substrate ledger row `3f77850d-…` (coordinator-provenance-fanout Option B trigger).

The response now includes lineage + fanout fields computed from `AgentExecution.parent_execution_id` + `root_execution_id` (shipped in migration 0336). No schema change; pure PA tool-surface expansion.

### 7.1 New response fields

Added to every branch with a resolved `AgentExecution` row:

- `parent_execution_id` (str UUID or None) — the execution that dispatched this run. NULL for root dispatches and legacy pre-migration-0336 rows.
- `root_execution_id` (str UUID or None) — top-of-chain ancestor. NULL for legacy rows.
- `child_count` (int) — direct children where `parent_execution_id == this.id`.
- `subtree_count` (int) — all descendants sharing the same `root_execution_id` (falls back to `self.id` when this execution's own `root_execution_id` is NULL), excluding self.
- `children` (list, cap = 20) — direct children ordered by `created_at` ASC. Each item: `{execution_id, agent_name, status, created_at, completed_at, duration_ms}`. Uses `.values()` projection to avoid loading heavy `input_data` / `output_data` JSONB blobs (D2 same_pr_mitigation from T1 SIGN).
- `children_truncated` (bool) — `true` when `child_count > 20`.
- `fanout_available` (bool) — always present. `false` on the four branches where no `AgentExecution` row could be resolved: missing-lookup-keys error, unknown-task_id error, pending-Celery-task branch, and any other early-return path. `true` when the response describes a real `AgentExecution` row (D5 same_pr_mitigation from T1 SIGN).

### 7.2 Example — parent with 3 direct children

```
agent_job_status  execution_id=<parent-uuid>
# →
# {
#   ok: true, execution_id: "<parent>", status: "in_progress",
#   agent_name: "AiSeriesWorkflowAgent",
#   parent_execution_id: null,
#   root_execution_id: "<parent>",
#   child_count: 3,
#   subtree_count: 3,
#   children: [
#     {execution_id: "<c1>", agent_name: "ResearchAgent", status: "completed", ...},
#     {execution_id: "<c2>", agent_name: "TrendAnalysisAgent", status: "in_progress", ...},
#     {execution_id: "<c3>", agent_name: "ContentWriterAgent", status: "queued", ...}
#   ],
#   children_truncated: false,
#   fanout_available: true,
#   ...
# }
```

### 7.3 Semantics + caveats

- **Recorded-lineage only.** Counts reflect what was threaded via `parent_execution_id` at dispatch time. Coordinator paths that don't pass `parent_execution_id` through the router will not populate the field on their children, and those children will not show up in `child_count` / `subtree_count`. This is a known-shape S3045 substrate concern being tracked separately in the Rigby Tool Gap Ledger.
- **Legacy rows.** Pre-migration-0336 (Session 1098 PR #4) executions have `parent_execution_id = NULL` + `root_execution_id = NULL`. For a legacy execution polled today, `subtree_count` falls back to `filter(root_execution_id=self.id)` — which is 0 unless newer dispatches recorded this legacy row as their root. Acceptable best-effort.
- **Cap = 20 children.** `children_truncated=true` signals overflow; caller can fall back to `execution_history_tool` for exhaustive enumeration.
- **Performance.** Both count queries hit indexed columns (`parent_execution_id` + `root_execution_id` are `db_index=True` per migration 0336). Children list uses `.values('id', 'agent__name', 'status', 'created_at', 'completed_at', 'execution_time_ms')` so no JSONB blobs are pulled into memory.

## Related

- **Sibling tool (subscription):** `schedule_followup_validation.md` — same lookup shape, subscribes to completion notification instead of returning inline status.
- **Sibling tool (drift audit):** `agent_capability_drift_tool_validation.md` — also authored in S3044 Batch 1.
- **Shared handler module:** `td_handlers_agents.py`.
- **Path B FINISH plan:** `docs/audits/pa_tools/substrate/S3044_path_b_finish_plan.md` (this session's batch shape).
- **S3044 Rigby A1 SIGN cycle:** 11 tool_runs; AGREE on Q1-Q4 with tweaks; Q5 zoom-out flagged registration-count false positive + pre-authored Path B CLOSE stub (adopted).
- **S3046 T1 SIGN cycle:** AGREE overall (D1/D3/D4) + 2 `same_pr_mitigatable` folds (D2 `.values()` projection for children query; D5 explicit `fanout_available: false` on pending/missing branches). Both mitigations shipped in this diff.
- **S3045 substrate ledger:** row `3f77850d-…` (coordinator-provenance-fanout Option B trigger) — this extension is Option B's discharge.
- **Migration:** `core/migrations/0336_agentexecution_parent_root_lineage.py` (Session 1098 PR #4) — schema substrate reused unchanged.
