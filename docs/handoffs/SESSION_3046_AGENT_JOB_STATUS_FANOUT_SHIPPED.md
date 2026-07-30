# Session 3046 — `agent_job_status` fanout visibility SHIPPED + linkage-gap ledger row opened

**Session:** S3046
**Date:** 2026-07-30
**HEAD at close:** `86ed83cca` (PR #3800 merged)
**Wrapper pin bump commit:** follows (post-close)
**Cycle 1A streak:** 32nd consecutive verify-before-build session
**Playbook:** v0.11.0 (no amendment this session)

---

## What shipped

**PR #3800** — `feat(s3046): agent_job_status fanout visibility — discharge coordinator-provenance-fanout Option B`

Extends the `agent_job_status` PA tool response with 7 new lineage + fanout fields computed from `AgentExecution.parent_execution_id` + `root_execution_id` (migration 0336, already shipped). No schema change; pure PA tool-surface expansion.

### New response fields (on branches with resolved AgentExecution row)

| Field | Type | Semantics |
|---|---|---|
| `parent_execution_id` | str UUID or None | The execution that dispatched this run |
| `root_execution_id` | str UUID or None | Top-of-chain ancestor |
| `child_count` | int | Direct children (`parent_execution_id == this.id`) |
| `subtree_count` | int | All descendants sharing `root_execution_id` (falls back to `self.id` for legacy pre-0336 rows), excluding self |
| `children` | list, cap 20 | Direct children ordered by `created_at` ASC; each item `{execution_id, agent_name, status, created_at, completed_at, duration_ms}` |
| `children_truncated` | bool | `true` when `child_count > 20` |
| `fanout_available` | bool | Always present; `false` on missing-lookup / unknown-task_id / pending-Celery branches where no `AgentExecution` row exists yet |

### Discipline receipts

- **7 dispatcher-path tests** in `core/tests/test_agent_job_status_fanout.py` via `ToolDispatcher.execute_sync` in `TransactionTestCase` per PLAYBOOK-3.2.3. All PASS in 10.9s.
- **Sibling regression check:** `test_schedule_followup_response_shape` (11 tests) still PASS.
- **`make celery-recycle`** completed post-merge; new response shape live for Rigby.
- **PLAYBOOK-3.2.4 not applicable** — `agent_job_status` is a single-entrypoint tool (no `action` enum, no shared-taxonomy branch); envelope-shape assertions suffice.
- **PLAYBOOK-7.7.5 not fired** — this is net-new capability, not drift/hardening class.

## SIGN cycles (both AGREE, 4 same_pr_mitigatable folds total, all discharged)

### T1 SIGN (Rigby, pre-implementation)

- **D1 (response shape safety):** AGREE — additive fields, no strict-key consumers.
- **D2 (query performance):** `same_pr_mitigatable` → shipped `.values('id', 'agent__name', ...)` projection so children query avoids loading heavy `input_data` / `output_data` JSONB blobs.
- **D3 (NULL semantics for legacy rows):** AGREE — `(execution.root_execution_id or execution.id)` fallback is correct best-effort.
- **D4 (test authoring discipline):** AGREE — dispatcher-path invariant via `TransactionTestCase` per PLAYBOOK-3.2.3.
- **D5 (zoom-out — pending-state asymmetry):** `same_pr_mitigatable` → shipped explicit `fanout_available: false` on every early-return branch (missing-keys, unknown-task_id, pending-Celery); schema doc updated to describe recorded-lineage-only semantics.

### A2 SIGN (Rigby, post-merge, live)

- **D1:** AGREE — live tool calls returned `ok: true` with new keys, no consumer breakage.
- **D2:** `same_pr_mitigatable` (already discharged; projection observed working).
- **D3:** AGREE — legacy null-root executions returned `subtree_count=0` cleanly.
- **D4:** AGREE — 7-test suite shipped correctly.
- **D5 (linkage-gap reality check):** `same_pr_mitigatable` → **confirmed real** via `orm_inspect_tool count_by parent_execution_id` on `AgentExecution` → **1 group only, value=null, count=1785**. Zero recorded lineage across the entire DB lifetime since migration 0336 shipped ages ago. New substrate ledger row opened (see below).

## Substrate ledger changes

### Row flipped `ready → completed`

`3f77850d-3a25-42c0-859f-5cbc397e7a57` — **[S3045] Coordinator-provenance-fanout class — fanout-guard smoke prompt insufficient for stock/market coordinator shape** — Option B (surface fanout in agent_job_status) SHIPPED via PR #3800. Content field annotated with S3046 discharge note.

### Row opened `ready`

`d1182b61-5261-4157-9bfd-a29e5b0e5b08` — **S3046: AgentExecution lineage threading missing in ALL dispatch paths (1785/1785 NULL parent_execution_id)** — Follow-on to the discharged row. Captures the router-side linkage-threading fix that would make the newly-surfaced fanout counts non-zero for coordinator dispatches. Recommended scope (per Rigby A2 SIGN):

1. Audit ALL coordinator→child dispatch entrypoints (`agent_router.py`, `base_agent.py`, and any tasks that call `run_agent` from inside an already-running agent).
2. Every child dispatch call must include `parent_execution_id=<current_execution.id>` (or `context.execution_id` that router resolves) and set/propagate `root_execution_id`.
3. Add integration test: dispatch a known-fanout coordinator, assert at least 1 child `AgentExecution` row exists with `parent_execution_id == parent.id` and `root_execution_id == parent.root_or_self`.
4. Post-fix live verification: re-run coordinator, verify `agent_job_status.child_count > 0` and `children[]` populated.

Priority: **MEDIUM**. Not blocking any active workflow, but blocks the S3046 fanout surface from being *useful* for coordinator dispatches (the tool works; the data feeding it is empty for coordinators).

## Why we closed here instead of continuing

Chris framed the question: *"does continuing into linkage keep us moving toward users for RaaS?"* Honest read: the linkage fix is **observability enablement**, not new user capability. The agents already work together functionally — the router just doesn't record the parent→child relationship. Fixing it would make the surface I just shipped maximally useful, but no user gains a new ability. Per `feedback_engineering_bias_over_audit`, we get more user-facing lean from a net-new capability. Ledger row captures the work so it's not lost.

## Discipline receipts (session-level)

- **32nd consecutive Cycle 1A verify-before-build session** — session opened with `build_pa_tool_audit --gap-only --check` confirming S3045 close state (163 RaaS-validated, 45 `agent_via_run_agent_validated`, 118 `validated_full`, 1 `meta_no_handler`, 0 residue).
- **Ledger flip discipline** — the discharged row (`3f77850d`) was flipped to `completed` and the follow-on gap (`d1182b61`) was opened BEFORE running `session_lifecycle close`. Per `project_ledger_reconciliation_meta_fix_shipped`, the close command now enforces this.
- **Verify-before-build applied twice within-session** — once at open (gap map check); once mid-implementation when Rigby's T1 SIGN caught that `AgentExecution.parent_execution_id` was already shipped in migration 0336, collapsing the scope from "extend model + tool" to "tool-surface only."
- **Rigby-first comms** — all decisions routed through PA chat (T1 SIGN, A2 SIGN, ledger row creation, net-new lean zoom-out).
- **23-session zero-hallucination Rigby SIGN streak** (extends S3036 count by 1).

## Forward-carry / follow-on gaps

- **`d1182b61-…` — AgentExecution lineage threading fix.** MEDIUM priority. Ledger row captures full scope. Not blocking; useful when Chris wants to see fanout counts actually populate.
- **Odds API restoration** (from S3045 carry) — Chris directive: back burner; no API key.
- **Skiplist re-validation** (5 media/audio tools) — deferred; requires dedicated media-batch scope.
- **`agent_router.py:2131-2132` silent fallback** — 1st `future_trigger` (S3043), unchanged.
- **T1 Fold future_trigger (`typing.Literal[actor]`)** — 1st trigger (S3036), unchanged.
- **A2 Fold future_trigger (actor-taxonomy vs frontend-palette drift)** — 1st trigger (S3036), unchanged.
- **S3042 arc Q3/Q4** — Spine Contract v1 §§1+3 (frontend event instrumentation + Workspace UI redo Arc C) unchanged.
- **All other S3045 carry** (S3033 Fold B / S3030 prod deploy / S3032 Fold E / S3031 Fold B / S3034 A2 Folds / stem-matcher lint / `chris-personal` orphan cleanup / `/docs/` restructuring / T2 silent fallback spec) — status preserved from S3045 close.

## Files changed (PR #3800)

- `core/services/td_handlers_agents.py` — `_handle_agent_job_status` extended with lineage + fanout computation
- `core/services/pa_tool_schemas.py` — `agent_job_status` description updated with new fields
- `docs/research/tools/validation/agent_job_status_validation.md` — new `## 7. Fanout visibility (S3046)` section
- `core/tests/test_agent_job_status_fanout.py` — 7 dispatcher-path tests (new file)

**Diff:** 305 insertions, 1 deletion, 4 files.
