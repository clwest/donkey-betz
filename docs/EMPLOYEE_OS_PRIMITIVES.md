---
title: "Employee OS — Canonical Primitives + Anti-Duplication Rules"
status: active
session: 1253
last_updated: 2026-06-29
companion_docs:
  - PLATFORM_INVENTORY.md
  - handoffs/SESSION_1252_AI_EMPLOYEE_V0_PR1_PR2_LANDED.md
owner: claude (structure) + rigby (verbatim primitives + reuse rules)
---

# Employee OS — Canonical Primitives

> **TL;DR.** The platform already has every primitive an AI Employee
> needs: identity, job contract, scheduled execution, audit, verdict,
> escalation, inbox messaging, approval funnel, status read, autonomy
> control. Documentation Manager is **proof #1** that the primitives
> compose — it is **not** the whole architecture. Adding new employees
> or new jobs means **registering JobContracts and writing thin
> job-specific config**, not building new models, queues, or surfaces.

## §1 — Canonical primitives

Each row below is either a Django model, a frozen dataclass, a PA
tool, or a Celery surface that exists today and has at least one
production caller. Counts mirror `PLATFORM_INVENTORY.md` where
applicable; the inventory file is the authoritative count source.

| # | Primitive | Surface | Where it lives | What it does |
|---|---|---|---|---|
| 1 | **`AIEmployee`** | Frozen dataclass | `core/employees/jobs.py` | Identity: handle, display_name, runs_as_username, primary_chat_id, notes |
| 2 | **`JobContract`** | Frozen dataclass | `core/employees/jobs.py` | Policy: mission, responsibilities, triggers, daily_routine, authority, prohibited_actions, escalation_rules, dedupe_rule, evidence contract |
| 3 | **`OpsRun(domain='mission')`** | Django model | `core/models_ops_runs.py` | One row per execution of a job. The "MissionRun" without a separate model — `domain` + `run_kind` distinguish ops vs. mission rows |
| 4 | **`OpsRunEvent`** | Django model | `core/models_ops_runs.py` | One row per step boundary / verdict / escalation; FK to OpsRun |
| 5 | **`emit_mission_verdict()`** | Pure helper | `core/employees/mission_verdict.py` | Writes the terminal `verdict_issued:<certified\|rejected\|deferred>` event + flips OpsRun.status; idempotent on (mission, verdict) |
| 6 | **`@shared_task` Celery jobs** | Celery surface | `core/tasks_*.py` modules | Scheduled execution path. New job modules MUST be added to `app.conf.imports` in `core/celery.py` (Session 1253 hotfix) |
| 7 | **`PeriodicTask`** (`django_celery_beat`) | Django model | DB | Beat schedule rows; daily job triggers (e.g. `rigby_documentation_manager_daily`) |
| 8 | **`Deliverable(publish_intent='publish_candidate')`** | Django model | `core/models_deliverables.py` | Escalation surface on failure; visible to Chris via cockpit inbox |
| 9 | **`DeliverableEvent(event_type='status_transition', source='<Employee>')`** | Django model | `core/models_deliverables.py` | Auditable transition (incl. `ctx.ops_run_id`, `ctx.error_signature`) — survives status field mutation |
| 10 | **`MessageThread` + `DirectMessage` + `ThreadParticipant`** | Django models | `core/models_messaging.py` | Persistent inbox threads; per-user read cursor; metadata-keyed thread lookup |
| 11 | **`post_shift_report(employee, job, mission, …)`** | Pure helper | `core/employees/comms.py` | Generic: posts one DM per terminal mission into the persistent `(employee, job)` thread. Idempotent. Bounded metadata |
| 12 | **`post_docs_manager_shift_report(mission)`** | Thin wrapper | `core/employees/comms_docs_manager.py` | Docs-cascade-specific subject + body formatter + extra metadata keys; calls #11 |
| 13 | **`HumanAttentionItem`** | Django model | `core/models_human_interface.py` | Approval / decision funnel for items needing human action; auto-approve lifecycle for low-risk |
| 14 | **`HumanFeedbackRecord`** | Django model | `core/models_human_interface.py` | Decision + ML-agreement tracking; feeds back into ML training |
| 15 | **`HumanPreference`** | Django model | `core/models_human_interface.py` | Channels, quiet hours, auto-approve thresholds |
| 16 | **`OrchestrationApprovalGate`** | Django model | `core/models_orchestration.py` | Per-step approval gate when an orchestration needs human sign-off — bridges to `HumanAttentionItem` |
| 17 | **`GovernanceState` + `KillSwitch`** | Django models | `core/models_governance.py` | Autonomy control plane (normal/throttle/freeze/safe_mode); emergency blocks with TTL |
| 18 | **`employee_tool`** | PA tool | `core/services/td_handlers_employee.py` | LLM surface: `describe / run_now / status / evidence_for_mission` |
| 19 | **`mission_verdict`** | PA tool | `core/services/td_handlers_employee.py` | LLM surface: Rigby-gated `certify / reject / defer` |
| 20 | **`messaging_tool`** (read-only v0) | PA tool | `core/services/td_handlers_core.py` | LLM surface: `list_threads / get_thread / unread_count`. `send_message` removed from enum + gated by `settings.MESSAGING_TOOL_ALLOW_SEND` |
| 21 | **`/api/inbox/threads/` HTTP** | Django view | `core/views_inbox.py` | Web Inbox page (`/inbox`); 15s poll; thread / messages / mark-read |
| 22 | **`/ws/system-events/` WebSocket** | Daphne consumer | `core/consumers*.py` | 9 typed real-time events (agent_execution_complete, gate_became_critical, etc.) — does NOT yet carry "DM arrived" event for shift reports (v0 design choice) |
| 23 | **`LLMCallEvent`** | Django model | `core/models_llm_telemetry.py` | Per-LLM-call audit row; `metadata.ops_run_id` correlates to mission |
| 24 | **`ToolCallRecord`** | Django model | `core/models_tool_calls.py` | Per-tool-call audit row; correlates by `trace_id` / `parameters` |
| 25 | **`CeleryTaskEvent`** | Django model | `core/models.py` | Per-task lifecycle telemetry; populated by Session-983 task-event signals |

**Inventory authority.** Counts (agent count, spider count, beat
periodicity, etc.) come from `PLATFORM_INVENTORY.md` regenerated via
`python manage.py generate_platform_inventory`. Do **not** invent or
hand-edit counts in this doc.

## §2 — Anti-duplication matrix

The wrong instinct when adding a new AI employee or capability is to
build a "fresh, clean" abstraction for it. **Reuse the table below.**
Each "do not build" entry has burned at least one operator hour in
prior sessions and is named here so it stays burned.

| Do **NOT** build | Use this instead |
|---|---|
| `EmployeeMessage` | `DirectMessage` + `MessageThread` with `metadata.employee + metadata.job` |
| `ApprovalQueue` | `HumanAttentionItem` + `HumanAttentionLifecycleService` (auto-expire / auto-approve low-risk / aging escalation) |
| `TrustScore` (persisted) | `OpsRun.summary.verdict` counts; trust ratio derived on read by `employee_tool action=status` (PR 3) — never persisted |
| `MissionRun` (separate model) | `OpsRun(domain='mission', run_kind=<job-key>)` — the MissionRun-compatibility fields (`domain`, `run_kind`, `mission_id`) were added in Session 1250 PR 3 specifically to avoid this |
| `EmployeeNotification` | Choose: (a) `DirectMessage` shift report (proactive, no decision needed) or (b) `HumanAttentionItem` (decision needed — approve/reject) |
| `EmployeeJob` admin UI | Frozen `JobContract` dataclass in `core/employees/jobs.py`. PR-reviewable, git-versioned. No admin form, no migration, no fixtures |
| `ShiftReport` model | `DirectMessage` with bounded `metadata` (`mission_id`, `verdict`, etc.) |
| `EmployeeKillSwitch` | `GovernanceState` (set `mode='freeze'` scoped to the relevant `agent` or `desk`) + `KillSwitch` (emergency, TTL-required) |
| `EmployeeAuditLog` | `OpsRunEvent` for step-level + `DeliverableEvent` for status transitions + `LLMCallEvent` for LLM calls + `ToolCallRecord` for tool calls. Already 4 audit surfaces — adding a 5th is a sign you haven't read them |
| New PA tool per employee (`rigby_tool`, `auditor_tool`, …) | `employee_tool` with `employee` param + new actions on the same tool |
| New beat queue per employee | `default` queue + standard `@shared_task` |
| `EmployeeContract` (persisted) | Frozen `JobContract` dataclass — see #6 in §1 |
| Inline shift-report code in each task | `post_shift_report(employee, job, mission, …)` from `core.employees.comms` |
| Per-employee escalation Deliverable category/type | Existing `Deliverable` with `publish_intent='publish_candidate'` and `metadata`/`raw_output.ops_run_id` |

**Spotting a duplication candidate.** If you find yourself writing
`class <Anything>Mission`, `class <Anything>Approval`, or
`class <Anything>Notification`, stop and re-read this table.

## §3 — Standard employee lifecycle

The lifecycle below is implemented end-to-end for **Rigby /
Documentation Manager** as of Session 1253. New employees follow the
same path; deviations require explicit justification.

```
┌─────────────────────────────────────────────────────────────────┐
│  1. IDENTITY                                                    │
│     core/employees/jobs.py:                                     │
│       FOO = AIEmployee(handle="foo", display_name="Foo", ...)   │
│                                                                 │
│  2. JOB CONTRACT                                                │
│     core/employees/jobs.py:                                     │
│       FOO_JOB = JobContract(title=..., mission=..., ...)        │
│     Register in _JOBS_BY_EMPLOYEE.                              │
│                                                                 │
│  3. EXECUTION (Celery task)                                     │
│     core/tasks_<job>.py:                                        │
│       @shared_task(name="foo_<job>_daily")                      │
│       def foo_<job>_daily(): ...                                │
│     Add 'core.tasks_<job>' to app.conf.imports in core/celery.py│
│     (Session 1253 #2733 lesson — registration is load-bearing.) │
│                                                                 │
│  4. SCHEDULING                                                  │
│     migrations/NNNN.py: seed PeriodicTask(name=..., enabled=    │
│     False). Flip to enabled=True only after manual run_now and  │
│     a recorded passed MissionRun.                               │
│                                                                 │
│  5. STEP TELEMETRY                                              │
│     Inside the task body:                                       │
│       OpsRun.objects.create(domain='mission', run_kind=<job>)   │
│       OpsRunEvent.objects.create(run=..., label=<step>)         │
│     LLMCallEvent + ToolCallRecord populate automatically if the │
│     task uses the standard LLM caller / dispatcher.             │
│                                                                 │
│  6. VERDICT EMIT                                                │
│     core/employees/mission_verdict.py:                          │
│       emit_mission_verdict(                                     │
│           mission_id=..., verdict='certified' | 'rejected' |    │
│           'deferred', confidence=..., issued_by=FOO.handle)     │
│                                                                 │
│  7. ESCALATION (on rejected only)                               │
│     Create Deliverable(publish_intent='publish_candidate',      │
│       title=<job>-escalation).                                  │
│     Force status to 'ready' via the audited transition path     │
│     (DeliverableEvent with source=<Employee>, ctx.ops_run_id,   │
│     ctx.error_signature).                                       │
│     Post a one-line summary to the employee's primary_chat_id.  │
│     Dedupe by (failed_step + normalized error tail hash) within │
│     24h — append/reference rather than re-create.               │
│                                                                 │
│  8. SHIFT REPORT (every terminal mission, additive)             │
│     core/employees/comms.py: post_shift_report(                 │
│         employee=FOO, job="<job-key>", mission=...,             │
│         body_formatter=foo_format_body,                         │
│         extra_metadata_keys=("foo_specific_key", ...),          │
│         thread_subject="Foo — Job Name",                        │
│         sender_type='system')                                   │
│     OR write a thin wrapper module like comms_docs_manager.py.  │
│                                                                 │
│  9. READ + POSTMORTEM (already shipped — no new code needed)    │
│     employee_tool action=status employee=foo job=<job-key>      │
│     employee_tool action=evidence_for_mission mission_id=...    │
│     messaging_tool action=list_threads (read-only)              │
│     /inbox (web UI)                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Per-step file ownership

| Lifecycle step | File / module pattern |
|---|---|
| 1, 2 | `core/employees/jobs.py` (frozen-dataclass registry) |
| 3 | `core/tasks_<job>.py` + `core/celery.py:app.conf.imports` |
| 4 | New migration adding one PeriodicTask row |
| 5 | Inline within the task; see `tasks_documentation_manager.py` for the canonical pattern |
| 6 | One call to `emit_mission_verdict()` per mission |
| 7 | Inline within the task; mirror `_handle_failure_escalation` in `tasks_documentation_manager.py` |
| 8 | Either generic helper call OR a thin `comms_<job>.py` wrapper |
| 9 | Existing `employee_tool` + `messaging_tool` — no per-employee surface |

## §4 — Explicit warnings

Each warning below is named because the next session that ignores it
will spend hours rediscovering it.

### 4.1 — Do not build new core models for AI Employees
**Don't write:** `EmployeeMessage`, `EmployeeNotification`,
`MissionRun`, `ApprovalQueue`, `TrustScore`, `ShiftReport`,
`EmployeeJob`, `EmployeeAuditLog`, `EmployeeContract`,
`EmployeeKillSwitch`, `EmployeeWorkItem`, `EmployeeAssignment`. Each
of these has a working primitive in §1.

**Why:** every new model requires migration coordination, fixture
seeding, admin UI, serializers, API endpoints, and downstream
verification. The platform already has 584 models; adding model #585
for an employee capability that fits an existing primitive is a tax
that compounds against every future change.

**How to apply:** before writing `class Foo(models.Model):` for
anything employee-related, find the primitive in §1 and the
"do not build" row in §2. If you cannot find a match, raise the
question through Rigby before opening a migration PR.

### 4.2 — Do not invent new PA tools per employee
**Don't write:** `rigby_tool`, `auditor_tool`, `triager_tool`,
`<employee>_tool`.

**Use:** `employee_tool` with `employee` + `action` params. Add new
actions there; the action enum is cheap to extend and the LLM only
needs to learn one tool name per category.

### 4.3 — Documentation Manager is proof #1, not the architecture
The Documentation Manager job exists to **demonstrate that the
primitives compose**. Concretely it proves:

- AIEmployee + JobContract carry policy without a model
- OpsRun(domain='mission') is a usable MissionRun without a new table
- emit_mission_verdict is a usable verdict surface without a new table
- post_shift_report is a usable comms surface without a new table
- employee_tool action=status is a usable read surface without a new table
- HumanAttentionItem + Deliverable + DeliverableEvent are usable
  escalation surfaces without a new table

If a future employee needs something **none** of the primitives in §1
provides, that's the signal to extend a primitive — not to build a
parallel system. Examples that **should** extend an existing
primitive:

- Adding a `mode='audit'` value to `GovernanceState` (extends §17)
- Adding `evidence_for_mission` joins for new evidence tables
  (extends §18)
- Adding a new `OpsRunEvent.label` value for a new step type
  (extends §4)

### 4.4 — Trust math is derived, never persisted
`employee_tool action=status` derives the trust ratio + status on
read, every call, from `OpsRun.summary.verdict` counts. There is no
`TrustScore` row and there must not be one. Persisting trust math
makes it impossible to retroactively adjust the policy (e.g., change
the under-review threshold from 3 failures to 5) without backfilling.

### 4.5 — Shift-report metadata is bounded, never an error tail
`post_shift_report` projects mission summary into a small, JSON-safe
metadata dict (`BASE_METADATA_KEYS` + caller's `extra_metadata_keys`).
Never store `error_tail`, full LLM output, or any unbounded field in
DirectMessage.metadata. The escalation Deliverable carries the full
error tail; the DM carries only the pointer fields needed to find it.

### 4.6 — Adding a job module needs `app.conf.imports`
**Anti-pattern:** add `core/tasks_<new_job>.py` with
`@shared_task`, schedule it via a `PeriodicTask` row, observe
`PeriodicTask.last_run_at` advancing, and conclude the task runs.

**Reality:** unless `'core.tasks_<new_job>'` is in
`app.conf.imports` in `core/celery.py`, the worker rejects the
message with `KeyError: '<task-name>'` while beat's
`last_run_at` updates anyway. Beat-side observability stays green;
no OpsRun, no Deliverable, no PA post.

Session 1253 PR #2733 closed this for the docs cascade; the
`DocsManagerTaskRegistrationTests` lock-in catches the regression
shape. Apply the same pattern to every new job module.

### 4.7 — Free-form LLM outbound messaging is OFF
`messaging_tool` is read-only in v0. The LLM cannot call
`send_message` from chat. Programmatic shift reports go through
`post_shift_report` (direct ORM). If a future capability genuinely
needs LLM-driven outbound DMs, set
`settings.MESSAGING_TOOL_ALLOW_SEND=True` deliberately and document
the use case here.

## §5 — Quick-start for adding a new employee

1. Define `AIEmployee` + `JobContract` in `core/employees/jobs.py`.
2. Register in `_EMPLOYEES_BY_HANDLE` + `_JOBS_BY_EMPLOYEE`.
3. Write `core/tasks_<job>.py` with one `@shared_task`.
4. Add `'core.tasks_<job>'` to `app.conf.imports` in `core/celery.py`
   (and the eager-import set inside `_eager_import_session1115_modules`).
5. Add a registration test in
   `core/tests/test_celery_queue_parity.py` (mirror
   `DocsManagerTaskRegistrationTests`).
6. Seed a `PeriodicTask` (enabled=False) in a new migration.
7. Either call the generic `post_shift_report` directly inside the
   task or write a thin `core/employees/comms_<job>.py` carrying
   job-specific subject + body formatter + extra metadata keys.
8. **Manual run via `employee_tool action=run_now` first.** Verify
   the OpsRun shape, summary keys, verdict, escalation behavior.
9. Flip the PeriodicTask to `enabled=True` only after #8 is green.
10. **No new model. No new PA tool. No new admin UI.** If you find
    yourself wanting any of those, re-read §2 + §4.

## §6 — Doc maintenance

This file is **narrative** — it describes intent and reuse rules.
It is **not** an inventory; the runtime inventory anchor is
`PLATFORM_INVENTORY.md`. When the inventory regenerates and a count
in §1 above drifts, prefer fixing the canonical surface or updating
§1's narrative — never inline a count in §1 that contradicts the
inventory.

When a new primitive lands, add a row to §1 and (if it replaces a
"do not build" instinct) add a row to §2.

When a warning gets re-discovered the hard way, add it to §4 with
the session number.
