---
title: "Employee OS"
status: active
session: 1260
last_updated: 2026-06-30
companion_docs:
  - EMPLOYEE_OS_PRIMITIVES.md
  - PLATFORM_INVENTORY.md
  - PLATFORM_WHAT_IT_IS.md
owner: claude (orientation pointer) — canonical content lives in EMPLOYEE_OS_PRIMITIVES.md
---

# Employee OS

> **Canonical primitives + anti-duplication rules live in [`docs/EMPLOYEE_OS_PRIMITIVES.md`](../EMPLOYEE_OS_PRIMITIVES.md).**
> This topic file is an orientation pointer. Read the primitives doc before adding employees, jobs, or new audit surfaces.

## What it is

**Employee OS is a primitive-reuse pattern, not a new subsystem.** It turns the platform's existing primitives — `AIEmployee` (frozen dataclass), `JobContract` (frozen dataclass), `MissionRunner` (orchestrator), `OpsRun` / `OpsRunEvent` (audit), `emit_mission_verdict()` (terminal verdict), `Deliverable` (escalation), `DirectMessage` (shift report), `employee_tool` (PA read surface) — into deterministic, audit-trail-emitting AI workers.

**Documentation Manager is proof #1 that the primitives compose; it is not the architecture.** Adding a new employee means registering JobContracts and writing a thin job-specific config — *not* new models, queues, or admin UIs. [`EMPLOYEE_OS_PRIMITIVES.md` §2](../EMPLOYEE_OS_PRIMITIVES.md#2--anti-duplication-matrix) names the wrong instincts that would create parallel systems.

## Production employees

As of Session 1258 close, **3 employees** run through MissionRunner with full evidence trail (`OpsRun(domain='mission')` + `OpsRunEvent` step boundaries + `emit_mission_verdict` terminal event):

| Employee | Job key | Cadence | Code |
|---|---|---|---|
| Rigby (Documentation Manager) | `docs_manager` | Daily 06:30 MDT (Mon-Fri) | `core/tasks_documentation_manager.py`, `core/jobs/docs_cascade.py` |
| Platform Auditor | `platform_audit` | On-demand via `employee_tool action=run_now` | `core/tasks_platform_audit.py`, `core/jobs/platform_audit.py` |
| Chief of Staff | `morning_brief` | Daily 07:00 MDT | `core/tasks_chief_of_staff.py`, `core/jobs/morning_brief.py` |

First-fires verified Session 1259 (2026-06-30): both scheduled beats fired clean — `OpsRun.status=passed`, `verdict=certified`, zero escalations, zero degraded evidence.

## What MissionRunner owns

`core/employees/mission_runner.py` is the orchestrator. It owns **lifecycle policy** — preflight → ordered steps → postflight → verdict emission → escalation policy with dedupe. It does **not** own domain logic; that lives in the job module's step functions. Lifecycle hooks (`preflight_fn`, `postflight_fn`, `escalation_body_formatter`, `shift_report_fn`) compose; jobs supply the job-specific behavior.

The runner is stable infrastructure as of Session 1258. New employees compose against the existing contract; they do not modify it.

## What primitives must be reused

See [`EMPLOYEE_OS_PRIMITIVES.md` §1](../EMPLOYEE_OS_PRIMITIVES.md#1--canonical-primitives) for the full 25-row matrix. Short list:

- **Identity + policy**: `AIEmployee` + `JobContract` (no model, no admin UI, no migration)
- **Audit**: `OpsRun(domain='mission')` + `OpsRunEvent` — *never* invent `MissionRun`
- **Verdict**: `emit_mission_verdict()` — *never* persist `TrustScore`; trust ratio is derived on read
- **Escalation**: `Deliverable(publish_intent='publish_candidate')` + `DeliverableEvent`
- **Shift report**: `post_shift_report()` via `MessageThread` + `DirectMessage` with bounded metadata
- **Read surface**: `employee_tool` PA tool (`describe / run_now / status / evidence_for_mission`) — *never* invent `<employee>_tool`

## Anti-duplication rules (DO NOT violate)

Each row in [`EMPLOYEE_OS_PRIMITIVES.md` §2](../EMPLOYEE_OS_PRIMITIVES.md#2--anti-duplication-matrix) has cost at least one operator hour. If you find yourself writing `class <Anything>Mission`, `<Anything>Approval`, `<Anything>Notification`, `<Anything>TrustScore`, `<Anything>AuditLog`, or a per-employee PA tool — **stop and re-read the matrix**.

The seven explicit warnings in [`EMPLOYEE_OS_PRIMITIVES.md` §4](../EMPLOYEE_OS_PRIMITIVES.md#4--explicit-warnings) cover the recurring traps: don't build new core models, don't invent per-employee PA tools, don't persist trust math, don't dump unbounded error tails into DM metadata, don't forget `app.conf.imports` registration for new task modules, don't enable free-form LLM outbound messaging.

## Why Employee #4 should not introduce parallel abstractions

The current N=3 employees follow an identical structural pattern: frozen `AIEmployee` + `JobContract` registry entry in `core/employees/jobs.py`, `core/tasks_<job>.py` `@shared_task` facade, `build_*_runner()` factory wiring `MissionRunner`, escalation body formatter, shift report formatter. Adding Employee #4 means following the [§5 quick-start](../EMPLOYEE_OS_PRIMITIVES.md#5--quick-start-for-adding-a-new-employee), not inventing a new framework. With N=3 patterns visible, abstraction candidates (BaseJobRunner, declarative beat schedule, YAML JobContract schema) do not yet have load-bearing evidence — premature abstraction is a documented anti-pattern.

## Runtime read surface (no LLM required)

- **`employee_tool` PA actions** (`core/services/td_handlers_employee.py`): `describe` (employee + job list), `run_now` (Rigby-gated dispatch), `status` (trust ratio over window), `evidence_for_mission` (postmortem join across OpsRun + OpsRunEvent + LLMCallEvent + ToolCallRecord)
- **HTTP**: `GET /api/cockpit/ops-runs/<run_id>/` exposes OpsRun detail today; employee-centric `/api/employees/` endpoints are Phase 2 work (deferred)
- **Beat**: `scheduled_tasks_tool action=list` shows current cadence + last_run for every Employee OS beat row

## See also

- [`docs/EMPLOYEE_OS_PRIMITIVES.md`](../EMPLOYEE_OS_PRIMITIVES.md) — **canonical** primitives + anti-duplication + lifecycle + warnings + quick-start. Always start here.
- [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md) "Layer 3.5 — Employee OS" — narrative anchor entry
- [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) — runtime anchor (regenerable via `python manage.py generate_platform_inventory`)
- [`docs/handoffs/SESSION_1258_EMPLOYEE_OS_PR_3_3_MORNING_BRIEF_BEAT_MIGRATION.md`](../handoffs/SESSION_1258_EMPLOYEE_OS_PR_3_3_MORNING_BRIEF_BEAT_MIGRATION.md) — latest production state at PR #2747 ship
