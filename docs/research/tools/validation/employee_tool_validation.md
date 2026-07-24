# `employee_tool` — Validation Report (S2940)

**Tool:** `employee_tool`
**Schema:** `core/services/pa_tool_schemas.py:5780` (4-action enum + employee/job/window/mission_id/wait/verbose params)
**Handler:** `core/services/td_handlers_employee.py:100` (`_handle_employee_tool`; per-action helpers `_handle_employee_run_now` :212 / `_handle_employee_status` :326 / `_handle_employee_evidence_for_mission` :405)
**Register site:** `core/services/tool_dispatcher.py:642`
**Session:** S2940 (Slice 7 Batch 2b — trio with `code_job_tool` + `railway_tool`)
**HEAD at validation:** `adba317b0` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Bifurcated verification scope** (per S2939 Chris D-verdict guardrail carried forward): §6 LIVE-VERIFIES the 3 read actions (`describe` / `status` / `evidence_for_mission`); §5a covers `run_now` mutation ANALYZED-NOT-EXECUTED with signal-chain evidence + Appendix A async-fanout.
**Category upgrade target:** `untested` → `validated_full` (read actions LIVE-VERIFIED; mutation action analyzed with §5a mutation-tier + §5b Appendix A async-fanout + Rigby-gate proof)
**Rigby SIGN:** S2940 T0 SIGN AGREE (bifurcated Option C shape ratified; `run_now` analyzed-only per Rigby-gated dispatch surface).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`employee_tool` is the **AI Employee registry inspection + Rigby-gated dispatch** surface — read-only lookup of registered `AIEmployee` + `JobContract` rows (Rigby, Platform Auditor, Chief of Staff, Bug Triage Specialist at v0), an on-demand dispatch entrypoint for the assigned Celery task per employee/job pair, a daily-read status surface (trust ratio + timing + drift), and a per-mission evidence join across the 5+ evidence tables (`OpsRun` + `OpsRunEvent` + `Deliverable` + `DeliverableEvent` + `LLMCallEvent` + `ToolCallRecord`). Use `describe` for contract questions ("what jobs does Rigby own?"); `run_now` to kick off the docs cascade or platform audit on demand; `status` for the morning health check ("is the docs cascade healthy?"); `evidence_for_mission` for postmortem on a specific `mission_id`.

Distinct from `mission_verdict` (that certifies/rejects/defers a MissionRun after evidence review; **shared handler file** with `employee_tool` at `td_handlers_employee.py` — see §5c.3 cross-link) — `mission_verdict` writes the verdict OpsRunEvent, `employee_tool` reads the evidence to reach it. Distinct from `agent_control_tool` (that manages the AGENT_MAP agent-orchestration surface — separate from the Employee OS registry). Distinct from `governance_tool` (that operates on ADR/ratification ledger, not employee missions). This is the **Employee OS reflection interface** — how Rigby reads her own registry and dispatches assigned work.

## Covered actions

Enumerating every action in the schema `action` enum. **3 read actions + 1 mutation action declared in schema.** Read actions LIVE-VERIFIED this ship; `run_now` mutation ANALYZED-NOT-EXECUTED per bifurcated Option C.

- `describe` — **READ — verified live at S2940 §6.1 (Rigby) + §6.2 (Platform Auditor).** Returns `{ok, action, employee: {handle, display_name, runs_as_username, primary_chat_id, notes}, job_count, jobs: [{key, contract: {...}}]}`. No DB writes, no signal fan-out. Registry read via `get_employee(handle)` + `list_jobs_with_keys(handle)` / `get_job(handle, key)`.
- `run_now` — **MUTATION `external` — ANALYZED-NOT-EXECUTED — Rigby-gated dispatch.** See §5a + §5b Appendix A. Fires `task_callable.delay()` on the resolved Celery task for the (employee, job) pair (`_RUN_NOW_TASKS` registry at `td_handlers_employee.py:569`). v0 supports 4 pairs: `(rigby, docs_manager) → rigby_documentation_manager_daily` on `docs_cascade` kind; `(platform_auditor, platform_audit) → platform_auditor_run` on `platform_audit` kind; `(chief_of_staff, morning_brief) → chief_of_staff_morning_brief_run` on `morning_brief` kind; `(bug_triage_specialist, triage_daily) → bug_triage_daily_run` on `bug_triage_daily` kind.
- `status` — **READ — verified live at S2940 §6.3.** Read-only daily-read surface. Derives trust ratio + timing + drift over a 7d/30d/90d window via `core.employees.status.derive_status(...)`. Returns `{ok, action, employee, employee_display_name, job, job_display_name, window_days, window_start/end, as_of, missions: {total, certified, rejected, deferred, in_progress}, trust: {ratio, status, current_streak, current_streak_kind}, timing: {last_mission_at, last_certified_at, last_escalation_at, avg_wall_time_ms, p95_wall_time_ms}, drift: {last_drift_count, avg_drift_count, degraded_evidence_count}, latest_mission: {...}}`. No writes.
- `evidence_for_mission` — **READ — analyzed at §6.4.** Per-mission join across the 5+ evidence tables via `core.employees.status.evidence_for_mission(mission_id=..., verbose=...)`. `verbose=False` (default) returns `error_tail_preview` (last 30 lines) + `has_full_error_tail` flag instead of the full tail — per Rigby SIGN-WITH-EDITS amendment 2. No writes.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_employee.py:117`). Defaults to `describe` per `(payload.get("action") or "describe").lower()`.
- **invalid action** — verified via handler code inspection (line 132-146). Returns `{ok: False, error: "Unknown employee_tool action <x>; v0 supports 'describe', 'run_now', 'status', 'evidence_for_mission'.", valid_actions: [...]}`. Non-raising in-envelope error with `ok: False` + explicit `valid_actions` array. Same divergence-class pattern as most Slice 7 handlers.

## 3. Schema notes

- **Required:** `action` (enum: `describe` | `run_now` | `status` | `evidence_for_mission`), `employee` (string — lowercase handle).
- **Optional (describe/status/run_now):** `job` (string — lowercase key). For `describe`, scopes response to one job when provided (else returns all jobs for the employee). For `status`, required to select which job to derive status for. For `run_now`, required together with `employee` to resolve the `_RUN_NOW_TASKS` dispatch entry.
- **Optional (run_now-only):** `wait_for_result` (bool; default false — when true, polls up to 90s in 2s intervals for a terminal MissionRun via `_wait_for_terminal_mission`; runs the mission-poller at line 512-544 filtered by `run_kind`).
- **Optional (status-only):** `window` (enum: `7d` | `30d` | `90d`; default `7d` per `_parse_window` at line 614-623). Unknown windows return refusal envelope (line 379-387). Note: `trust_status='under_review'` threshold ALWAYS uses last 7 days regardless of caller `window` — schema description flags this explicitly ("trip-wire, not a lens").
- **Optional (evidence_for_mission-only):** `mission_id` (UUID — required for this action per line 417-422), `verbose` (bool; default false — when false returns preview + flag; when true returns full error_tail).
- **Optional (status-only):** `mission_id` hint — when supplied, the status response carries a `requested_mission_pointer` redirecting to `evidence_for_mission` (status does NOT inline evidence — Rigby SIGN-WITH-EDITS amendment 1). Reference at line 389.
- **Auth gate (run_now only):** `_verify_rigby_caller(user_id)` at line 237. v0 gate: caller's `user_id` must resolve to `username == RIGBY.runs_as_username` (`'chris'`). Failures return `{ok: False, error: ..., error_code: "TOOL_PERMISSION_DENIED", auth_gate: <describe>}`. v0 limitation documented at module docstring lines 15-25 — this is a *channel* gate (both Rigby-as-LLM and Chris-typing-in-PA share the same authenticated user_id), NOT a *speaker* gate. Plumbing `agent_name` through the dispatcher is deferred to a future PR.
- **No flag gate:** unlike `rigby_work_item`'s `RIGBY_WORK_QUEUE_REVIEW_ENABLED` gate, `employee_tool` has no Django settings toggle. Rigby-gate on `run_now` is the safety guardrail; read actions are open (bounded by PA tool-surface exposure).
- **No `dry_run` affordance:** `run_now` always writes an `OpsRun` row and dispatches a Celery task when validation passes. Ledger #38 substrate blocker for LIVE-VERIFY of `run_now`.
- **Registry-driven action set:** `_RUN_NOW_TASKS` dict at line 569-601 controls which (employee, job) pairs are dispatchable. Adding a new employee/job requires a new dict entry — action set grows without schema changes.

## 4. Golden-path examples

**Example 1 — Describe Rigby (READ, verified live):**
```json
{"action": "describe", "employee": "rigby"}
```
→ `{"ok": true, "action": "describe", "employee": {"handle": "rigby", "display_name": "Rigby", "runs_as_username": "chris", "primary_chat_id": "pa-3901b70e61934df7", "notes": "Personal Assistant + first AI employee. Operates the PA tool surface..."}, "job_count": 1, "jobs": [{"key": "docs_manager", "contract": {"title": "Documentation Manager", ...}}]}` (verified §6.1).

**Example 2 — Describe Platform Auditor (READ, verified live):**
```json
{"action": "describe", "employee": "platform_auditor"}
```
→ Returns Platform Auditor's contract with `job_count: 1`, `jobs[0].key = "platform_audit"` (verified §6.2).

**Example 3 — Status snapshot for Rigby's docs_manager job (READ, verified live):**
```json
{"action": "status", "employee": "rigby", "job": "docs_manager", "window": "7d"}
```
→ Returns rich status envelope with `trust.ratio`, `trust.status`, `trust.current_streak`, `missions.certified`, `timing.avg_wall_time_ms`, `drift.last_drift_count`, `latest_mission.{mission_id, status, verdict, verdict_confidence}`. Verified §6.3 (Rigby is `trust_status="healthy"`, `current_streak=5 certified`).

**Example 4 — Evidence for a specific mission (READ):**
```json
{"action": "evidence_for_mission", "mission_id": "<opsrun-uuid>", "verbose": false}
```
→ Would return `{ok, mission_id, ops_run_meta, ops_run_events: [...], deliverables: [...], deliverable_events: [...], llm_call_events: [...], tool_call_records: [...], error_tail_preview: "<last 30 lines>", has_full_error_tail: true|false}`. Full-verbose variant returns `error_tail` in place of `preview`.

**Example 5 — Dispatch Rigby's docs cascade (MUTATION `external` — analyzed only this ship):**
```json
{"action": "run_now", "employee": "rigby", "job": "docs_manager", "wait_for_result": false}
```
→ Would pass through `_verify_rigby_caller(user_id)` gate → resolve `_RUN_NOW_TASKS[('rigby', 'docs_manager')]` = `rigby_documentation_manager_daily` → call `task_callable.delay()` → return `{"ok": true, "action": "run_now", "employee": "rigby", "job": "docs_manager", "task_id": "<celery-uuid>", "dispatch_status": "queued", "wait_for_result": false, "note": "Mission dispatched. Poll via employee_tool action=status..."}`.

**Example 6 — Dispatch with wait_for_result=true (MUTATION):**
```json
{"action": "run_now", "employee": "platform_auditor", "job": "platform_audit", "wait_for_result": true}
```
→ Would dispatch + poll `OpsRun.objects.filter(domain="mission", run_kind="platform_audit").order_by("-started_at").first()` in 2s intervals up to 90s (line 528-544). On terminal: `{"ok": true, "action": "run_now", ..., "mission_id": "<uuid>", "status": "<passed|failed|partial>", "summary": {...}}`. On timeout: `{"ok": true, ..., "wait_timeout": true, "note": "Mission still running after 90s wait cap."}`.

## 5. Failure / empty-state / pagination notes

- **`describe` missing `employee`:** `{"ok": false, "error": "Missing required arg 'employee'. Try: action=describe employee=rigby", "known_employees": ["rigby", "platform_auditor", "chief_of_staff", "bug_triage_specialist"]}` (line 149-159). Non-raising envelope with recovery hint (`known_employees` array via `list_employees()`).
- **`describe` unknown `employee`:** `{"ok": false, "error": "Unknown employee '<x>'.", "known_employees": [...]}` (line 162-169).
- **`describe` `job` not on employee:** `{"ok": false, "error": "Employee '<x>' has no job keyed '<y>'.", "known_jobs": [...]}` (line 176-188). Uses `list_job_keys_for_employee(handle)` to generalize per employee — no hardcoded 'docs_manager' fallback (S1257 PR 2.1 fix).
- **`describe` employee with 0 jobs:** would return `{"ok": true, "action": "describe", "employee": {...}, "job_count": 0, "jobs": []}`. Not currently reachable at v0 registry (every registered employee has at least 1 job).
- **`run_now` auth gate FAIL (caller not Rigby):** `{"ok": false, "error": "<gate rejection reason>", "error_code": "TOOL_PERMISSION_DENIED", "auth_gate": "v0 gate: caller user_id must resolve to username='chris'. Plumbing of caller agent_name into handlers is a future PR."}` (line 239-244). The `auth_gate` field is surfaced explicitly per module docstring intent — keeps the v0 gate transparent about its limitation rather than opaque `denied`.
- **`run_now` unknown (employee, job) pair:** `{"ok": false, "error": "v0 run_now does not support (employee='<x>', job='<y>').", "supported_pairs": [{"employee": ..., "job": ...}, ...]}` (line 252-263). `supported_pairs` derived from `sorted(_RUN_NOW_TASKS.keys())`.
- **`run_now` with `wait_for_result=true` and 90s timeout:** `{"ok": true, "action": "run_now", ..., "task_id": ..., "dispatch_status": "queued", "wait_for_result": true, "wait_timeout": true, "note": "Mission still running after 90s wait cap. Check status later via employee_tool action=status."}` (line 297-310).
- **`status` unknown `employee`:** `{"ok": false, "error": "Unknown employee '<x>'; status surface requires a registered employee.", "known_employees": [...]}` (line 352-362).
- **`status` `job` not on employee:** `{"ok": false, "error": "Employee '<x>' has no job keyed '<y>'.", "known_jobs": [...]}` (line 366-376).
- **`status` unrecognized `window`:** `{"ok": false, "error": "Unrecognized window. v0 supports '7d', '30d', or '90d'.", "valid_windows": ["7d", "30d", "90d"]}` (line 380-387). `_parse_window(None)` defaults to `7d`; empty string also maps to `7d` (line 620-621).
- **`evidence_for_mission` missing `mission_id`:** `{"ok": false, "error": "Missing required arg 'mission_id'."}` (line 419-422).
- **`evidence_for_mission` unknown `mission_id`:** delegated to `evidence_for_mission()` service — refusal envelope shape defined there (out-of-scope for this handler-boundary doc).
- **Invalid action:** `{"ok": false, "error": "Unknown employee_tool action '<x>'; v0 supports 'describe', 'run_now', 'status', 'evidence_for_mission'.", "valid_actions": ["describe", "run_now", "status", "evidence_for_mission"]}` (line 132-146). Non-raising with `ok: False` + explicit `valid_actions`. Consistent with the majority of Slice 7 handlers — not a Ledger #5 divergence hit.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 1 mutation action declared in `## Covered actions` (`run_now`). ANALYZED-NOT-EXECUTED at this ship per bifurcated Option C shape.**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `run_now` | `external` | `td_handlers_employee.py:212-322` (handler) → `_RUN_NOW_TASKS[<pair>].resolve_task().delay()` at line 269-270 | none direct at the handler layer — the Celery task itself writes `OpsRun` + `OpsRunEvent` rows via `MissionRunner.run(...)` in the worker process | `OpsRun.post_save` receivers fire when the worker writes the mission row; `OpsRunEvent.post_save` receivers fire on lifecycle events | **Celery `<task_callable>.delay()`** on the resolved (module, attr) pair — leaves the handler process. Downstream: LLM calls (per-mission cascade), Deliverable writes (on escalation), potential dispatcher re-entry via sub-tool calls in the mission task |

### Signal-chain evidence (Chris D-verdict guardrail — file/line cited)

- **`OpsRun.post_save` receivers:** `OpsRun` is defined at `core/models_ops_runs.py`. Receivers subscribed to `OpsRun.post_save` fire when the worker writes the mission row (during `MissionRunner.run(...)`) — NOT during the handler dispatch. The handler itself does not write `OpsRun`; it only calls `task_callable.delay()`.
- **`OpsRunEvent.post_save` receivers:** the same 2 receivers documented for `mission_verdict` (`broadcast_mission_verdict` at `core/signals/mission_verdict_signals.py:56` + `escalate_mission_verdict_to_hai` at `core/signals/mission_verdict_attention_signals.py:68`) subscribe to `OpsRunEvent.post_save`. They gate on `label.startswith('verdict_issued:')` — so lifecycle-only labels (`step_start`, `step_pass`, `step_fail`, etc.) written during the mission run do NOT trigger those receivers. Only the final `verdict_issued:*` write (via `mission_verdict_tool` post-cascade) does.
- **`run_now` is external:** the dispatch step is a Celery `.delay()` — leaves the handler process into the worker pool. Even if the downstream `OpsRun`/`OpsRunEvent` writes fire in-process on the worker side, the handler's first-hop is the Celery boundary, which classifies as `external`.
- **`_wait_for_terminal_mission` polling (wait_for_result=true):** `time.sleep(poll_interval_seconds)` + DB read loop at line 528-544. Read-only from the polling side — no writes. The mission row it queries is being written by the worker; polling here does not compete for the row.

### Rigby-gate proof bar (Chris D-verdict guardrail — Rigby-only surface)

- **v0 gate:** `_verify_rigby_caller(user_id)` at line 629-674. Verifies `user_id → username == RIGBY.runs_as_username` (`'chris'` at v0). Failures return `TOOL_PERMISSION_DENIED` + `auth_gate` transparency field.
- **Honest limitation:** module docstring lines 15-25 documents that the gate is a *channel* gate (both Rigby-as-LLM and Chris-typing-in-PA resolve to the same authenticated user_id), NOT a *speaker* gate. Realistic invocation scope is bounded to PA tool-surface exposure — GPT-5.2 function-calling on PA chat path, where Rigby is the LLM.
- **Speaker-gate future work:** plumbing `agent_name` through the dispatcher to handlers is deferred to a future PR (documented at module docstring line 24-25). No Ledger candidate at this ship — behavior matches the documented v0 contract.

### Idempotency proof bar (Chris D-verdict guardrail)

- **`run_now` idempotency:** **NONE** — every valid `run_now` writes a new `OpsRun` mission row. No dedupe key on `(employee, job)`. Re-dispatching the same (employee, job) pair while a mission is running creates a **second concurrent mission row**. The `_wait_for_terminal_mission` poller (when `wait_for_result=true`) queries `OpsRun.objects.filter(domain="mission", run_kind=<kind>).order_by("-started_at").first()` — grabs the latest, which after re-dispatch is the new row, not the still-running previous one. **Potential double-dispatch hazard** — not blocked at the handler layer. Ledger candidate for `run_now` idempotency contract (e.g., refuse if a non-terminal mission of the same `run_kind` exists).
- **`wait_for_result` polling:** idempotent — read-only. Multiple `wait_for_result=true` calls interleave safely because they all read the latest OpsRun.

### Deferral rationale (why not live-fire this ship)

- Live-firing `run_now` would dispatch a real Celery task and write a real `OpsRun` mission row. Not reversible cleanly (row persists; mission state advances through `MissionRunner`).
- Live-firing Rigby's `docs_manager` would fire the full docs cascade (index rebuild → RAG corpus → Document table sync → embedding regen) — takes ~1 minute, generates side effects across the docs corpus.
- Live-firing Platform Auditor's `platform_audit` would run the weekly platform audit — generates a Deliverable row.
- Rigby S2940 T0 mutation-verb scan confirmed `run_now` is the only mutation surface; live-mutation deferral is the standard bifurcated Option C posture.
- Ledger #38 (`dry_run` substrate) would let §6 LIVE-VERIFY cover `run_now` shape without dispatching — same blocker documented for `rigby_work_item` mutations.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `get_employee(handle)` (describe/status/evidence_for_mission) | `read` (in-memory registry) | `td_handlers_employee.py:161, 351` | validated |
| `get_job(handle, key)` (describe/status when `job` scoped) | `read` (in-memory registry) | line 174, 365 | validated |
| `list_employees()` (describe error-response only) | `read` (in-memory registry) | line 157, 167, 359 | validated |
| `list_jobs_with_keys(handle)` (describe — all-jobs branch) | `read` (in-memory registry) | line 197-200 | validated |
| `list_job_keys_for_employee(handle)` (describe/status error-response) | `read` (in-memory registry) | line 185, 372 | validated |
| `derive_status(employee_handle=..., job_key=..., mission_run_kind=..., window_days=..., mission_id_hint=...)` (status) | `read` (delegated to service) | line 391-401 → `core.employees.status.derive_status` | validated |
| `evidence_for_mission(mission_id=..., verbose=...)` (evidence_for_mission) | `read` (delegated to service) | line 426-430 → `core.employees.status.evidence_for_mission` | validated |
| `_verify_rigby_caller(user_id)` (run_now auth gate) | `read` (Django UserModel + settings check) | line 237 → 629-674 (helper); reads `RIGBY.runs_as_username` constant + `UserModel.objects.get(id=...)` | validated |
| `_RUN_NOW_TASKS[<pair>].resolve_task()` (run_now) | `read` (lazy `importlib.import_module` — read-only side effect on module registry) | line 269 → `_RunNowDispatch.resolve_task` at line 562-566 | validated |
| `task_callable.delay()` (run_now) | `dispatch` (Celery fan-out — see Appendix A) | line 270 | validated |
| `_wait_for_terminal_mission(timeout_seconds=90, poll_interval_seconds=2, run_kind=<kind>)` (run_now `wait_for_result=true`) | `read` (poll loop) + `time.sleep` | line 291-295 → 512-544 | validated |
| `OpsRun.objects.filter(domain="mission", run_kind=<kind>).order_by("-started_at").first()` (mission poller) | `read` | line 533-540 | validated |
| `_dataclass_to_jsonable(...)` (describe response marshalling) | `read` (pure fn on dataclass/enum) | line 67-86 | validated |
| `_parse_window(payload.get("window"))` (status window parse) | `read` (pure fn) | line 614-623 | validated |

**No Appendix N (Network-Preflight) needed:** neither handler nor first-hop dependencies leave the process via HTTP at the handler boundary. Registry helpers are in-memory; `derive_status` / `evidence_for_mission` are DB reads only. The Celery task dispatched by `run_now` MAY invoke LLMs (network) downstream — out of scope for this handler-boundary doc.

### Appendix A — Async-Fanout (first-hop = Celery `<task>.delay()` via `run_now` action)

Filling per S2917 batch 7 template extension — `run_now` is the sole mutation action across `employee_tool` whose first-hop is Celery dispatch.

- **A1. Dispatch target type(s):** `direct_task` — resolved lazily via `_RunNowDispatch.resolve_task()` (line 562-566) which `importlib.import_module`s the target module and returns the task callable. v0 registry (`_RUN_NOW_TASKS` at line 569-601) contains 4 (employee, job) → task pairs:
  - `(rigby, docs_manager)` → `core.tasks_documentation_manager.rigby_documentation_manager_daily` (run_kind=`docs_cascade`)
  - `(platform_auditor, platform_audit)` → `core.tasks_platform_audit.platform_auditor_run` (run_kind=`platform_audit`)
  - `(chief_of_staff, morning_brief)` → `core.tasks_chief_of_staff.chief_of_staff_morning_brief_run` (run_kind=`morning_brief`)
  - `(bug_triage_specialist, triage_daily)` → `core.tasks_bug_triage.bug_triage_daily_run` (run_kind=`bug_triage_daily`)

  First-hop opacity: handler SEES the task_id + queued state; the Celery worker actually executes `MissionRunner.run(...)` for the assigned steps.

- **A2. Queue name(s) + priority:** queue is not specified in the `.delay()` call at line 270 — falls through to each task's own `@task(queue=...)` decoration (Celery routing table). Priority not set. Callable-per-callable — the handler doesn't own queue routing; the task decorator does.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery — `getattr(async_result, "id", None)` at line 271) + `mission_id` (when `wait_for_result=true` AND poll succeeds — `str(terminal.id)` at line 319) + always includes `employee` + `job` + `dispatch_status: "queued"` + `wait_for_result` echo. Envelope varies between `wait_for_result=false` (immediate return with task_id + queued note) and `wait_for_result=true` + terminal (returns mission_id + status + summary) and `wait_for_result=true` + timeout (returns wait_timeout: true).
  - (b) **Polling endpoints:** `employee_tool action=status employee=<h> job=<k>` (the daily-read surface — returns latest_mission summary); OR `employee_tool action=evidence_for_mission mission_id=<uuid>` (per-mission deep dive); OR direct ORM query on `OpsRun(domain='mission', run_kind=<kind>)` via `zoom_out_tool` / `orm_inspect_tool`. No `AsyncResult` polling — the domain object (OpsRun) is source of truth. `_wait_for_terminal_mission` at line 512-544 is the built-in poller (90s cap, 2s interval).
  - (c) **Idempotency stance:** `none`. Every `run_now` dispatches a new Celery task + writes a new `OpsRun` mission row (via the worker). No dedupe key. Concurrent re-dispatch of the same (employee, job) creates a second concurrent mission. Explicit declaration per Appendix A discipline; potential double-dispatch hazard flagged as Ledger candidate (see §5a).
- **A4. Downstream side-effect boundary:** each Celery task runs its assigned `MissionRunner` pipeline. Per-task boundaries:
  - `rigby_documentation_manager_daily`: 6-step docs cascade — `build_docs_index`, `build_rag_corpus`, `sync_docs_index_to_documents`, `sync_docs_index_to_documents --embed` (**LLM calls for embeddings**), `verify_doc_claims --only-drift`, emit verdict. Writes `Document` rows (Step 3), `DocumentEmbedding` rows (Step 4), `LLMCallEvent` rows (Step 4), `OpsRun`/`OpsRunEvent` (throughout), `Deliverable` on escalation.
  - `platform_auditor_run`: read-only inspection surface — docs, integrations, env config, model counts. Writes `Deliverable` (audit report) + `OpsRun`/`OpsRunEvent`. No data mutation.
  - `chief_of_staff_morning_brief_run`: wraps morning_brief workflow as a single MissionRunner step — writes `Deliverable` (brief) + `OpsRun`/`OpsRunEvent`.
  - `bug_triage_daily_run`: daily triage — `auto_emit_verdict=False` (line 596-600 comment) — MissionRunner flips OpsRun.status but does NOT write `verdict_issued:*` event. `mission_verdict` tool is the certification surface post-triage-review. Writes `Deliverable` (triage report) + `OpsRun`/`OpsRunEvent`.

  Cite the task files for entrypoints. **Explicit call-out: dispatcher re-entry** possible if any MissionRunner step invokes PA tools (e.g., `deliverable_tool.create` on escalation). Full downstream audit is out-of-scope for this handler-boundary doc — see per-task validation (not authored per Slice 7 scope).

- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** authoritative status = `OpsRun.status` on `domain='mission', run_kind=<kind>`. Best-effort event stream = `OpsRunEvent` rows on the same mission (lifecycle labels: `step_start`, `step_pass`, `step_fail`, `verdict_issued:certified|rejected|deferred`). `Deliverable` rows on escalation. Summary fields per `JobContract.required_summary_keys` (v0 for docs_manager: 12 keys including `wall_time_ms`, `drift_count`, `failed_step`, etc.).
  - (b) **Cancel semantics:** no explicit cancel path at the tool surface. Celery revoke could work at the queue layer but there's no domain-side "mission cancelled" marker. "No cancel" is the honest v0 answer — matches `rigby_work_item.delegate` pattern.
  - (c) **Revisit triggers:** re-audit this Appendix A if (1) `_RUN_NOW_TASKS` grows beyond the current 4 pairs, (2) queue routing changes (any task adds an explicit `queue=<name>` on `delay()`), (3) `_wait_for_terminal_mission` polling contract changes (currently 90s / 2s), (4) idempotency stance changes (e.g., refuse-if-non-terminal check added), (5) new dispatcher re-entry sites emerge in the MissionRunner steps, or (6) the auth gate is promoted to a speaker gate (would change §5a Rigby-gate section).

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PASS — no drift.** The module docstring at `td_handlers_employee.py:1-26` correctly names both tools registered by this mixin: `employee_tool` (4 actions: `describe / run_now / status / evidence_for_mission`) and `mission_verdict` (3 actions: `certify | reject | defer`). Both action lists match the schema enum (`pa_tool_schemas.py:5800-5805` for employee_tool; `pa_tool_schemas.py:5882` for mission_verdict). The auth honesty paragraph at lines 15-25 correctly documents the v0 gate as a *channel* gate with future-PR plumbing for speaker gate. The `_handle_employee_tool` docstring at line 107-116 accurately describes `describe` + `run_now` behaviors (though it predates `status` + `evidence_for_mission` per S1253 PR 3 — the higher-level branch handling at line 124-131 correctly routes those). Ledger #5 lint pre-flight at S2940 open: `employee_tool` returned **0 hits** — no auto-detected drift.

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — Rigby-gated on `run_now` (verified via analysis, §6.1-6.3 exercise read-only path which requires no gate).** `_verify_rigby_caller(user_id)` at line 629-674 enforces the v0 channel-gate: `user_id → username == RIGBY.runs_as_username`. §6 LIVE-VERIFIES the 3 read actions (no gate); §5a documents the gate on `run_now`. Read actions (`describe` / `status` / `evidence_for_mission`) are un-gated at v0 — realistic caller bounded by PA tool-surface exposure. Documented in schema description at `pa_tool_schemas.py:5782-5794` (says "Rigby-only dispatch" for run_now; describes read actions as "read-only") — matches runtime.

### 5c.3 Shared handler-file coupling noted

**Disposition: SHARED — dedicated file BUT with sibling tool.** `td_handlers_employee.py` also hosts `_handle_mission_verdict` (the `mission_verdict` handler) at line 434. Both tools share the same `EmployeeHandlersMixin` class + the same `_verify_rigby_caller` auth helper (at line 629-674) + the same module-level constants (`_ACTION_TO_VERDICT` at line 60-64). Cross-link required for future operators editing this file: **`mission_verdict` is the sibling** — that tool certifies/rejects/defers a MissionRun via `emit_mission_verdict(...)` after the operator (Rigby) has reviewed the evidence. The two tools form the Employee OS **dispatch → observe → certify** loop:

1. `employee_tool action=run_now` — dispatches the assigned job's Celery task (writes OpsRun via MissionRunner).
2. `employee_tool action=status` OR `action=evidence_for_mission` — read the resulting mission's evidence.
3. `mission_verdict action=certify|reject|defer` — write the `verdict_issued:*` OpsRunEvent + flip `OpsRun.status` to terminal.

Any refactor to the shared `_verify_rigby_caller` helper affects BOTH tools' Rigby-gate posture. `mission_verdict` is `validated_full` per `mission_verdict_tool_validation.md` (shipped S2939 Slice 7 Batch 2a).

## 6. Evidence

Live PA-dispatch evidence for the 3 read actions. Captured at S2940 T0 via Rigby dispatch (tool_runs verbose block). Mutation (`run_now`) analyzed-not-executed per §5a.

### 6.1 `action=describe employee=rigby` — LIVE at S2940 T0

Dispatch: `employee_tool action=describe employee=rigby`
Latency: 5ms
Result (top-level; job contract truncated for brevity — full serialization verified live):
```json
{
  "ok": true,
  "action": "describe",
  "employee": {
    "handle": "rigby",
    "display_name": "Rigby",
    "runs_as_username": "chris",
    "primary_chat_id": "pa-3901b70e61934df7",
    "notes": "Personal Assistant + first AI employee. Operates the PA tool surface (110+ schemas / 170+ handlers) and certifies business truth for the platform. v0 acts as the `chris` UnifiedUser server-side; no dedicated service account yet."
  },
  "job_count": 1,
  "jobs": [
    {
      "key": "docs_manager",
      "contract": {
        "title": "Documentation Manager",
        "employee_handle": "rigby",
        "manager": "chris",
        "mission": "Rigby owns running the documentation cascade, recording evidence, certifying successful runs, and escalating failures or drift...",
        "responsibilities": ["Run the 4-step documentation cascade once per weekday morning.", "Run `verify_doc_claims --only-drift` as an observation step...", "..."],
        "success_metrics": [...],
        "failure_metrics": [...],
        "triggers": [...],
        "daily_routine": [...],
        "mission_run_kind": "docs_cascade",
        "authority": {"run_docs_cascade_commands": "execute", ...},
        "prohibited_actions": [...],
        "required_summary_keys": ["docs_indexed_count", "documents_count_before", "documents_count_after", "embeddings_count_before", "embeddings_count_after", "embedding_delta", "drift_count", "drift_items_count", "degraded_evidence", "wall_time_ms", "failed_step", "error_tail"],
        "evidence_tables": ["OpsRun (domain=mission, run_kind=docs_cascade)", "OpsRunEvent (one per step + verdict_issued event)", "LLMCallEvent (from step 4 embedding API)", "ToolCallRecord (if any cascade command emits one)", "Deliverable (publish_candidate, only on escalation)"],
        "drift_count_definition": "..."
      }
    }
  ]
}
```

**Observations locked at this HEAD:**
- Employee registry contains Rigby with 1 assigned job (`docs_manager`). `runs_as_username=chris` (v0 UnifiedUser channel binding).
- `JobContract` is a large frozen-dataclass (~30 fields including `mission`, `responsibilities`, `success_metrics`, `failure_metrics`, `triggers`, `daily_routine`, `authority`, `prohibited_actions`, `required_summary_keys`, `evidence_tables`). Full serialization via `_dataclass_to_jsonable` (line 67-86) — handles nested dataclasses + `AuthorityLevel` enum coercion.
- Envelope shape stable: `{ok: true, action, employee: {handle, display_name, runs_as_username, primary_chat_id, notes}, job_count, jobs: [{key, contract: {...}}]}`.

### 6.2 `action=describe employee=platform_auditor` — LIVE at S2940 T0

Dispatch: `employee_tool action=describe employee=platform_auditor`
Latency: 4ms
Result (top-level):
```json
{
  "ok": true,
  "action": "describe",
  "employee": {
    "handle": "platform_auditor",
    "display_name": "Platform Auditor",
    "runs_as_username": "chris",
    "primary_chat_id": null,
    "notes": "Second AI employee (Session 1257). Owns the weekly platform audit — read-only inspection of docs, integrations, env config status, and database model counts. Wraps the existing PlatformAuditAgent (core/agents/platform_audit_agent.py). v0 acts as the ``chris`` UnifiedUser server-side; no dedicated service account yet. Beat schedule + task runner land in subsequent PRs (2.2/2.3); PR 2.1 registers the contract only."
  },
  "job_count": 1,
  "jobs": [
    {
      "key": "platform_audit",
      "contract": {
        "title": "Platform Audit",
        "employee_handle": "platform_auditor",
        "manager": "chris",
        "mission": "Platform Auditor owns running the weekly internal platform audit, recording evidence, certifying healthy audits, and escalating drift or anomalies...",
        "responsibilities": ["Run the platform audit once per week...", "Inspect the canonical platform docs...", "Inventory integrations...", "..."],
        ...
      }
    }
  ]
}
```

**Observations locked at this HEAD:**
- Platform Auditor exists in the registry with 1 assigned job (`platform_audit`, mission_run_kind=`platform_audit`).
- `primary_chat_id` is `null` (unlike Rigby's `pa-3901b70e61934df7`) — Platform Auditor does not have a dedicated PA chat channel at v0.
- Envelope structure identical to §6.1 — describes generalized correctly across registered employees (S1257 PR 2.1 fix verified).

### 6.3 `action=status employee=rigby job=docs_manager window=7d` — LIVE at S2940 T0

Dispatch: `employee_tool action=status employee=rigby job=docs_manager window=7d`
Latency: 20ms
Result:
```json
{
  "ok": true,
  "action": "status",
  "employee": "rigby",
  "employee_display_name": "Rigby",
  "job": "docs_manager",
  "job_display_name": "Documentation Manager",
  "window_days": 7,
  "window_start": "2026-07-17T19:51:14.175844+00:00",
  "window_end": "2026-07-24T19:51:14.175844+00:00",
  "as_of": "2026-07-24T19:51:14.175844+00:00",
  "missions": {
    "total": 5,
    "certified": 5,
    "rejected": 0,
    "deferred": 0,
    "in_progress": 0
  },
  "trust": {
    "ratio": 1.0,
    "status": "healthy",
    "current_streak": 5,
    "current_streak_kind": "certified"
  },
  "timing": {
    "last_mission_at": "2026-07-24T12:30:01.828148+00:00",
    "last_certified_at": "2026-07-24T12:30:01.828148+00:00",
    "last_escalation_at": null,
    "avg_wall_time_ms": 61033,
    "p95_wall_time_ms": 68773
  },
  "drift": {
    "last_drift_count": 10,
    "avg_drift_count": 10,
    "degraded_evidence_count": 0
  },
  "latest_mission": {
    "mission_id": "b05d5b3d-fa2e-42ab-897b-5392ca55e221",
    "triggered_by": "beat",
    "status": "passed",
    "verdict": "certified",
    "verdict_confidence": 0.95,
    "started_at": "2026-07-24T12:30:01.828148+00:00",
    "finished_at": "2026-07-24T12:31:10.606615+00:00",
    "wall_time_ms": 68773,
    "failed_step": null,
    "error_signature": null,
    "has_escalation": false,
    "escalation_deliverable_id": null,
    "pa_post": null
  }
}
```

**Observations locked at this HEAD:**
- Trust status `healthy` — 5/5 certified, no rejections/deferrals over last 7d. Streak counter at 5 certified consecutive.
- Timing: `avg_wall_time_ms=61033` (~1min avg), `p95_wall_time_ms=68773` (~1.15min p95). Well under the `JobContract.success_metrics` bound of "Total mission wall time < 10 minutes" (600s = 600000ms).
- Drift: 10 documented drift claims (rag_or_narrative anchor per verify_doc_claims) — accumulator (last=avg=10 for the window). `degraded_evidence_count=0` — no drift-observation degradation.
- Latest mission: certified with `verdict_confidence=0.95`, triggered by `beat` (weekday cron), no escalation. `mission_id=b05d5b3d-fa2e-42ab-897b-5392ca55e221` — future `action=evidence_for_mission` probe target.
- Envelope structurally stable — 12 top-level fields (`ok`, `action`, `employee`, `employee_display_name`, `job`, `job_display_name`, `window_days`, `window_start`, `window_end`, `as_of`, `missions`, `trust`, `timing`, `drift`, `latest_mission`).

### 6.4 `action=evidence_for_mission` — ANALYZED

Cannot LIVE-VERIFY without triggering the full evidence-join service. Handler branch at line 405-430 delegates to `core.employees.status.evidence_for_mission(mission_id=..., verbose=...)`. Expected envelope shape (per service documentation + Rigby SIGN-WITH-EDITS amendment 2):
```json
{
  "ok": true,
  "action": "evidence_for_mission",
  "mission_id": "<uuid>",
  "ops_run_meta": {...},
  "ops_run_events": [...],
  "deliverables": [...],
  "deliverable_events": [...],
  "llm_call_events": [...],
  "tool_call_records": [...],
  "error_tail_preview": "<last 30 lines>",
  "has_full_error_tail": true|false,
  "run_kind": "docs_cascade|platform_audit|morning_brief|bug_triage_daily"
}
```
Missing-mission_id envelope (verified via §5 analysis of line 419-422): `{"ok": false, "error": "Missing required arg 'mission_id'."}`.

Verbose variant (`verbose: true`) returns `error_tail: "<full N lines>"` instead of `error_tail_preview` + `has_full_error_tail`. Verified via handler line 424 (`verbose = bool(payload.get("verbose"))`) and service delegation.

### 6.5 Mutation action (`run_now`) — ANALYZED-NOT-EXECUTED

See §5a for per-action write-target inventory + signal-chain evidence + Rigby-gate proof + idempotency proof + §5b Appendix A async-fanout contract + deferral rationale.

### 6.6 Invalid action envelope

Handler lines 132-146: `{"ok": false, "error": "Unknown employee_tool action '<x>'; v0 supports 'describe', 'run_now', 'status', 'evidence_for_mission'.", "valid_actions": ["describe", "run_now", "status", "evidence_for_mission"]}`. Non-raising envelope with `ok: false` + `valid_actions` recovery hint.

## Related

- **Adjacent tools (same Slice 7 Batch 2b):** `code_job_tool` (bifurcated: 4 read + 3 mutation — `submit` external, `cancel` cascading, `add_repo` contained), `railway_tool` (bifurcated: 5 read + 2 external mutations — Railway GraphQL API).
- **Adjacent tools (same handler file — SHARED):** `mission_verdict` (`_handle_mission_verdict` at `td_handlers_employee.py:434`) — sibling in the `EmployeeHandlersMixin` mixin. Shares `_verify_rigby_caller` auth helper (line 629-674) + `_ACTION_TO_VERDICT` constant (line 60-64). The two tools form the Employee OS dispatch → observe → certify loop (§5c.3). `mission_verdict` is `validated_full` per `mission_verdict_tool_validation.md` (shipped S2939 Slice 7 Batch 2a).
- **Adjacent tools (adjacent surface):** `agent_control_tool` (AGENT_MAP orchestration — different registry), `governance_tool` (ADR/ratification ledger — different persistence surface), `deliverable_tool` (the Deliverable-side view of mission escalations + audit reports), `zoom_out_tool` (governance/audit reads — OpsRunEvent aggregation across missions), `execution_history_tool` (read-only cross-tool execution audit).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md`; `core/employees/__init__.py` (registry helpers `get_employee` / `list_employees` / `get_job` / `list_jobs_with_keys` / `list_job_keys_for_employee`); `core/employees/jobs.py` (`AIEmployee` + `JobContract` frozen-dataclasses + `_EMPLOYEES_BY_HANDLE` / `_JOBS_BY_EMPLOYEE` maps); `core/employees/status.py` (`derive_status` + `evidence_for_mission` service functions); `core/employees/mission_verdict.py` (`emit_mission_verdict` + verdict constants — shared with `mission_verdict` tool); `docs/topics/employee-os.md` (Employee OS overview); `docs/EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives + anti-duplication rules — read before adding new employee/job).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2937 T1 Chris ratification (4-batch Slice 7 plan + §5c retro-fold); S2938 Ledger #5 lint substrate; **S2939 Slice 7 Batch 2a** (mission_verdict + newsletter_tool + rigby_work_item) with Chris D-verdict guardrails (§6 read-only scope + §5a mutation proof bar) — carried forward at S2940 T0 Chris D-verdict RATIFIED (Batch 2b = 3-tool ship closes Slice 7); **S1252-S1257 Employee OS build arc** (registry + PRs 1-4 for the 4 registered employees).
- **Lint pre-flight at S2940 open:** `employee_tool` → **0 handler_drift hits** (verified via `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check`). Clean.
- **First-hop dependencies:** see §5b table + Appendix A (`run_now` async fan-out via Celery `.delay()` — 4 dispatch pairs across `core.tasks_documentation_manager` / `core.tasks_platform_audit` / `core.tasks_chief_of_staff` / `core.tasks_bug_triage`).
- **Regression coverage:** `core/tests/test_employee_tool*.py`, `core/tests/test_employee_run_now*.py`, `core/tests/test_employee_status*.py`, `core/tests/test_mission_runner*.py` (adjacent — exercises the downstream MissionRunner used by `run_now`), `core/tests/test_ai_employee_registry.py`.
- **Ledger candidates surfaced this doc:** **`run_now` double-dispatch hazard** — no idempotency check at the handler layer; re-dispatching the same (employee, job) while a mission is running creates a concurrent second mission row. Ledger candidate for a refuse-if-non-terminal-<run_kind>-exists check. Record-only this ship; not fixed. Ledger #38 (`dry_run` substrate) remains a blocker for LIVE-VERIFY on `run_now`.
- **Post-merge live-dispatch verification:** exercise `employee_tool action=describe employee=rigby` + `action=status employee=rigby job=docs_manager window=7d` after `make recycle-all` at merge; confirm envelope shapes match §6.1 + §6.3. `run_now` remains analyzed-only.
