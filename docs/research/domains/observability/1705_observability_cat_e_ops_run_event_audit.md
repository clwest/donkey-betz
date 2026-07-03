---
title: "Group 1700 Cat E — OpsRun + OpsRunEvent Child Audit"
authority: child-audit
category: child_audit
session: 1705
child_slot: P5
domain_slug: observability
research_group: 1700
status: active
generated: 2026-07-03
verifier_loop: [pre-explore-verified, post-explore-verified, sign-cycle-1-folds-landed]
sibling_children: [1701_observability_cat_a_celery_task_event_audit.md, 1702_observability_cat_b_llm_call_event_audit.md, 1703_observability_cat_c_agent_execution_audit.md, 1704_observability_cat_d_tool_call_record_audit.md]
parent_scoping: 1700_observability_domain_scoping.md
canonical_summary: 1799_observability_canonical_summary.md (pending)
---

# Group 1700 Cat E — OpsRun + OpsRunEvent Child Audit

> **Fifth child audit under Group 1700 (Observability arc).** Applies
> playbook §11.2 20-section child audit template + §13 6-parallel-Explore
> sweep + §14 verifier-loop discipline (pre-Explore + post-Explore). Cat E
> is the Ops / Mission orchestration telemetry layer — OpsRun (parent
> run row, ops-domain or mission-domain via `domain` column added S1250
> PR3) + OpsRunEvent (child timeline event rows) + MissionRunner
> (Employee OS reusable orchestrator introduced S1256 PR 1.1) + Ops
> Autopilot consumer surface. Feeds xx99 D74 axis posture evidence
> continuing from S1704 F9 (Option A [incomplete-not-broken] vs Option B
> [broken-not-blocked] distinction).

---

## 1. Executive Summary

Cat E owns telemetry at the Ops / Mission orchestration boundary — one
`OpsRun` row per orchestrated run (ops-domain smoke tests, deploy
verifies, control loops OR mission-domain Employee OS daily jobs) plus
one `OpsRunEvent` row per timeline event within that run (step start,
step pass, step fail, info, heartbeat). The models are `OpsRun` +
`OpsRunEvent` (`core/models_ops_runs.py:11-117`). The primary writers
are MissionRunner (`core/employees/mission_runner.py:778` for the run,
`:812-816` for events via `get_or_create` per I3 idempotency), the
generic Ops Run Tracker (`core/tools/ops_run_tracker.py:34`), the Rigby
event intake path (`core/services/rigby_event_intake.py:416` for the
intake mission, plus lifecycle events at `:434,:450,:508,:522`), and the
Rigby delegation lifecycle signal handler at
`core/signals/rigby_delegation_signals.py:79-84` (Session 1250 PR 8;
flag-gated by `settings.RIGBY_DELEGATION_ENABLED`, default `False`).
The terminal-verdict writer is the `mission_verdict` PA tool at
`core/services/td_handlers_employee.py:434` which routes to
`emit_mission_verdict` (`core/employees/mission_verdict.py`).

**Coverage at HEAD.** 36 OpsRun rows accumulated 2026-06-13 → 2026-07-03
(~20 days, ~1.8 rows/day; ORM-verified 2026-07-03). Domain split:
19 `ops` + 17 `mission`. All 17 mission-domain rows have `mission_id`
populated (100%) and `run_kind` populated (100%); ops-domain rows use
the default blank `run_kind` and null `mission_id` per S1250 PR3
schema intent. Mission `run_kind` distribution: `docs_cascade` (7),
`bug_triage_daily` (4), `morning_brief` (4), `platform_audit` (2) — a
4-employee footprint consistent with the runtime registry at HEAD
(see F3 below re: CLAUDE.md/inventory drift). All 17 mission rows are
`triggered_by='beat'`; all 19 ops rows are `triggered_by='pa_tool'`
(smoke_test run_type). Status: 35 `passed` + 1 `failed` (~2.8% fail
rate). Event count: 224 OpsRunEvent rows (97 step_pass + 86 step_start
+ 39 info + 2 step_fail).

**Nine load-bearing findings emerge from the pre-Explore + post-Explore
verifier passes (see §1.1):** F1 (HIGH) 0/224 OpsRunEvent rows carry
cross-cat correlation IDs in detail JSON at HEAD (`execution_id`,
`trace_id`, `task_id`, `tool_call_id`, `agent_execution_id`,
`llm_call_id`, `celery_task_id` all 0 — ORM-verified) despite a
DESIGN-INTENT writer path that would populate `execution_id`;
F2 (HIGH) OpsRun + OpsRunEvent schema has NO cross-cat correlation
columns — mission_id (indexed) is the only correlation surface,
mission-domain only; F3 (MEDIUM, verifier-loop-corrected) CLAUDE.md
and PLATFORM_INVENTORY autoblock claim "3 Employees" but registry
has **4** (`bug_triage_specialist` added S1267 PR 4.1); F4 (POSITIVE
differentiator vs S1704 F4) CTO/COO/Trend Analysis daily diagnostic
pipelines EXIST and ARE beat-wired at 7:15/7:30/7:45 Denver via
`scheduled_diagnostic_runner` primitive — NOT WRITE-ONLY-FORGOTTEN;
F5 (MEDIUM) but those three daily aggregations do NOT consume
OpsRunEvent — resolves parent §5.E producer-vs-consumer question:
OpsRunEvent is **PRODUCER-ONLY** primary source, zero downstream
aggregation consumer; F6 (MEDIUM) no date-based retention for
OpsRun/OpsRunEvent (Cat A precedent absent, Cat B F4 gap resurfaces,
S1704 F5 resurfaces); F7 (MEDIUM) `evidence_for_mission` join at
`docs/topics/employee-os.md:64-65` is EMPIRICALLY BROKEN for
ToolCallRecord — two orthogonal write-gap paths (trace_id NULL per
S1704 F1, ops_run_id-in-parameters not threaded by Cat D dispatcher);
F8 (POSITIVE) MissionRunner nine invariants I1-I9 all VERIFIED at HEAD
via source read + contract test at
`test_mission_runner.MissionRunnerImportContractTests`;
F9 (D74 axis contribution) Cat E provides **LATENT-VIABLE-BUT-FLAG-GATED
evidence** for spine correlation posture — distinct axis cell from
Cat D's actively-broken (F1 trace_id runtime failure) and Cat C's
coverage-gap posture (F4 PA path).

**Maturity STABLE for writer mechanism (all writer paths honor I1-I9,
transaction-atomic escalation) + PARTIAL for coverage (4/4 employees
producing daily rows; ops-domain covered by 19 smoke tests but no
beat-wired ops-loop writer; retention absent) + NAMED-BUT-BROKEN for
cross-cat correlation contract (F7 evidence_for_mission ToolCallRecord
join is dead-on-arrival; F1 execution_id thread flag-gated off) +
STRONG for downstream orthogonal (daily diagnostics beat-wired) but
EMPTY for OpsRunEvent-consuming pipelines (F5 producer-only role).**
Risk **MEDIUM** — mission-domain lifecycle is production-solid; the
cross-cat correlation gap is design-intent-latent, not runtime-broken;
retention is unaudited but growth is small-cadence bounded (~657
OpsRun/year + ~4,088 OpsRunEvent/year projected).

### 1.1 Nine load-bearing findings (locked)

- **F1 (HIGH, §17)** — 0/224 OpsRunEvent rows carry cross-cat
  correlation IDs in `detail` JSON at HEAD (ORM-verified 2026-07-03:
  execution_id=0, trace_id=0, task_id=0, tool_call_id=0,
  agent_execution_id=0, llm_call_id=0, celery_task_id=0). The
  DESIGN-INTENT writer at `core/signals/rigby_delegation_signals.py:79-84`
  (Session 1250 PR 8) IS built to populate `execution_id` in
  `detail` on AgentExecution post-save for delegated executions
  (`parent_object_type='RigbyWorkItem'`), but the handler is gated
  by `settings.RIGBY_DELEGATION_ENABLED` (default `False` per
  `rigby_delegation_signals.py:22-25`) — when OFF the handler
  short-circuits even for delegated executions. Empirically at HEAD
  the flag is OFF and 0 delegated executions have fired; the detail-JSON
  spine surface is DESIGN-INTENT-LATENT. **Distinct from S1704 F1**
  (Cat D's `trace_id` is 100% NULL as a schema+runtime failure —
  column exists + indexed + always-hardcoded-None at three writer
  sites); Cat E is intentionally-flag-gated (design-intent-viable,
  runtime-empty because the switch is off). Kills S1703 F9 Option B
  runtime credibility at Cat E only when flag is ON; today, blocks
  any Option B evaluation at Cat E because there is no runtime evidence.
- **F2 (HIGH, §17)** — Cat E schema has NO cross-cat correlation
  columns. `OpsRun` has `id`, `title`, `run_type`, `status`,
  `triggered_by`, `started_at`, `finished_at`, `summary` (JSON),
  `event_count`, `fail_count`, `domain`, `run_kind`, `mission_id`
  (`core/models_ops_runs.py:11-89`). `OpsRunEvent` has `id`,
  `run` FK, `event_type`, `label`, `detail` (JSON), `created_at`
  (`:91-117`). Neither has `execution_id`, `trace_id`, `tool_call_id`,
  `celery_task_id`, `task_id`, `agent_execution_id`, `llm_call_id`,
  or `conversation_id`. Only `mission_id` (indexed, mission-domain
  only) plus the `run` FK (implicit index) are correlation surfaces.
  Parallel to S1704 F2 (HIGH) at Cat D. Column-add would enable
  Option A posture; detail-JSON write-time hook (via
  RIGBY_DELEGATION_ENABLED=True + Cat A/B/C/D populate correlation IDs)
  enables Option B posture — but the second requires resolving
  F1 first.
- **F3 (MEDIUM, verifier-loop-corrected, §14+§17)** — Employee count
  drift discovered via ORM. CLAUDE.md at :150-172 and
  PLATFORM_INVENTORY.md autoblock claim "3 Employees (Documentation
  Manager + Platform Auditor + Chief of Staff)". Runtime registry
  `_EMPLOYEES_BY_HANDLE` at `core/employees/jobs.py` has **4** handles:
  (1) `rigby` (`docs_manager` job), (2) `platform_auditor`
  (`platform_audit` job), (3) `chief_of_staff` (`morning_brief` job),
  (4) `bug_triage_specialist` (`triage_daily` job — added S1267 PR
  4.1 per `docs/handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md`).
  Drift is on-count-only; runtime works correctly (4 `run_kind`
  values in OpsRun-domain=mission match the 4 employees:
  `docs_cascade`, `bug_triage_daily`, `morning_brief`,
  `platform_audit`). Owed to xx99 anchor-update (CLAUDE.md autoblock
  regen + PLATFORM_INVENTORY regen).
- **F4 (POSITIVE differentiator vs S1704 F4, §7+§9)** — CTO/COO/Trend
  Analysis daily diagnostic pipelines EXIST at
  `core/services/diagnostics/cto_daily.py`, `.../coo_daily.py`,
  and `core/services/scheduled_diagnostic_runner.py`, AND ARE
  beat-wired at `core/celery.py:306-329`:
  - `cto-daily-diagnostic` @ 07:15 Denver → `core.tasks.run_cto_daily_diagnostic` (queue: long_running, expires: 7200)
  - `coo-daily-diagnostic` @ 07:30 Denver → `core.tasks.run_coo_daily_diagnostic` (queue: long_running, expires: 7200)
  - `trend-daily-diagnostic` @ 07:45 Denver → `core.tasks.run_trend_daily_diagnostic` (queue: long_running, expires: 7200)

  **Material Cat E vs Cat D difference:** S1704 F4 (MEDIUM) found
  `analyze_pa_tool_patterns` + `aggregate_tool_call_stats` beat-orphan
  (defined + queue-routed but neither in beat schedule nor in
  PeriodicTask table; PAToolInsight=0 + ToolCallAggregate=0
  consequence). Cat E has three fully-wired daily aggregations — NOT
  WRITE-ONLY-FORGOTTEN. The `scheduled_diagnostic_runner` primitive
  (introduced S1094) is the shared entry point across all three
  diagnostics; posting is gated independently per diagnostic by
  `CTO_DIAGNOSTIC_POSTING_ENABLED` / `COO_DIAGNOSTIC_POSTING_ENABLED`
  (governance separation of scheduling from posting is intentional).
- **F5 (MEDIUM, §9+§17)** — But those three daily aggregations do NOT
  consume OpsRunEvent. Per Explore Agent 2 evidence (source-read
  confirmed): CTO daily @ `core/services/diagnostics/cto_daily.py`
  reads CeleryTaskEvent + AgentExecution; COO daily @ `.../coo_daily.py`
  reads Deliverable + ActionItem + Initiative backlog; Trend Analysis
  daily reads LegacySpiderData + SignalCluster. **OpsRunEvent has ZERO
  downstream aggregation consumer.** Resolves parent §5.E
  producer-vs-consumer question: **OpsRunEvent is a PRODUCER-ONLY
  primary source of mission telemetry**, not a consumer/aggregator
  of prior-layer events. The three daily diagnostics operate at Cat
  A/B/C layers, orthogonal to Cat E. Consequence for §9 D74: any
  spine posture at Cat E must be write-time via caller-side hooks
  (MissionRunner threading or `rigby_delegation` flag ON), not
  read-time via aggregation. **Canonical verdict at HEAD:
  OpsRunEvent is producer-only. This could evolve to "producer +
  consumer" only if future work introduces cross-table correlation
  IDs at Cat E schema (F2 lift) and an explicit aggregation pipeline
  reads OpsRunEvent detail JSON — but that is post-arc T-slot work,
  not a v0 concern** (Rigby SIGN cycle 1 Q3(d) fold).
- **F6 (MEDIUM, §15)** — No date-based retention for OpsRun/OpsRunEvent.
  No `OPS_RUN_RETENTION_DAYS` setting (grep zero matches), no
  `ops_run_cleanup` task, no watchdog, no archival mechanism. Cat A
  precedent (`CELERY_TASK_EVENT_RETENTION_DAYS` at `core/tasks.py`,
  30-day default) exists; Cat B has watchdog cleanup but no retention
  (S1702 F4 HIGH); Cat D has neither (S1704 F5 MEDIUM); Cat E has
  neither. 36 OpsRun over 20 days extrapolates to ~657/year;
  224 OpsRunEvent over 20 days → ~4,088/year. Bounded but not
  measured for unusual bursts (e.g., an ops-domain smoke-test
  campaign could 10x the ops-domain writer volume without triggering
  any retention signal). Growth is small-cadence today; risk is
  unaudited-headroom, not immediate-blowout.
- **F7 (MEDIUM, §9+§17)** — `evidence_for_mission` join at
  `docs/topics/employee-os.md:64-65` (topic doc) is EMPIRICALLY
  BROKEN for the ToolCallRecord join surface. Implementation at
  `core/employees/status.py` joins by:
    - `OpsRunEvent.filter(run__mission_id=mission_id)` — **WORKS**
    - `LLMCallEvent.filter(metadata__ops_run_id=str(run.id))` — **WORKS** (`emit_mission_verdict` at `core/employees/mission_verdict.py:117-150` populates `metadata.ops_run_id`)
    - `ToolCallRecord.filter(parameters__ops_run_id=str(run.id))` at `status.py:475-483` — **EMPTY** (Cat D dispatcher does NOT thread `ops_run_id` into `parameters` JSON at write time; MissionRunner does not provide it via any context)
    - `ToolCallRecord.filter(trace_id=execution.trace_id)` from `core/services/deliverable_provenance.py:105` (separate consumer) — **EMPTY** per S1704 F1 (100% NULL trace_id)

  Named-but-broken integration. Two orthogonal write-gap paths (trace_id NULL + ops_run_id-in-parameters not threaded) both prevent the semantic join. Both are upstream Cat D-side and Cat E-caller-side write-time responsibilities. Cat E model itself is fine; the join contract straddles a boundary that neither side owns end-to-end.
- **F8 (POSITIVE, §7+§13)** — MissionRunner nine invariants I1-I9
  all VERIFIED at HEAD via source read + contract test at
  `test_mission_runner.MissionRunnerImportContractTests` @
  `core/tests/test_mission_runner.py:181-250`:
    - **I1** (daily idempotency): `_existing_mission_for_today()` @ `mission_runner.py:759-772` queries `OpsRun(domain, run_kind, started_at__date=today)`
    - **I2** (in-progress safety): implicit in I1 query — status='running' returns cached envelope
    - **I3** (event idempotency): `OpsRunEvent.objects.get_or_create(run=mission, label=..., defaults={event_type, detail})` @ `:812-816`
    - **I4** (verdict idempotency): via `emit_mission_verdict` framework helper (separate module)
    - **I5** (step ordering): step loop @ `:1030-1053` with break-on-first-failure + `<name>_skipped` events for remaining
    - **I6** (escalation atomicity): `with transaction.atomic():` @ `:1209` wraps Deliverable create-or-append + status flip + `escalation_emitted` event (either all three or none)
    - **I7** (dedupe key `(failed_step, error_signature)` with `dedupe_window_hours`): `_find_prior_escalation_run` @ `:1250-1275`
    - **I8** (hook containment): try-except around preflight/postflight/shift_report/pa_post hooks — mission outcome preserved on hook exception
    - **I9** (no employee-specific imports): contract-tested at `test_mission_runner.py:181-250` (`MissionRunnerImportContractTests`); grep confirms zero imports from `core.tasks_documentation_manager`, `core.employees.comms_docs_manager`, or specific employee constants (`RIGBY`, `DOCUMENTATION_MANAGER`)

  Cat E writer-mechanism maturity **STABLE**. This is Cat E's positive-differentiator finding vs S1703/S1704 which had structural coverage/correlation gaps at their writer paths.
- **F9 (D74 axis contribution, §9)** — Cat E provides
  **LATENT-VIABLE-BUT-FLAG-GATED evidence** for spine correlation
  posture. Distinct axis cell from Cat D (S1704 F9:
  actively-broken-for-Option-B + incomplete-not-broken-for-Option-A)
  and Cat C (S1703 F4: PA path coverage gap CRITICAL):
    - Cat E is **NOT actively-broken** like Cat D — writer path exists at `rigby_delegation_signals.py:79-84` and honors detail-JSON schema when the gate opens
    - Cat E is **NOT schema-broken** — `mission_id` (indexed) works; `execution_id` can be threaded via `detail` JSON when the flag flips ON without a schema change
    - Cat E's **producer-only role** (F5) means it cannot consume prior-layer IDs at read time; correlation must be threaded at write-time
    - **Option A** (execution_id column on OpsRunEvent) requires Cat E schema change + write-time thread from MissionRunner (which does not currently thread trace_id/execution_id/task_id — F2 gap)
    - **Option B** (trace_id spine) requires Cat A/B/C/D populate + Cat E write-time consume via detail JSON hook + `RIGBY_DELEGATION_ENABLED=True` (F1 flag)
    - **Options C/D** inherit same prerequisite as S1704 F9
    - Cat E contributes a **fourth axis cell**: (Cat A: task_id populated; Cat B: execution_id populated conditional; Cat C: F4 PA coverage gap; Cat D: F1 100% NULL trace_id + F2 schema-empty; Cat E: F1 flag-gated latent + F2 schema-empty). D74 posture decision must reconcile Cat E's design-intent-but-latent state with Cat D's actively-broken state.

  **This is the load-bearing Cat E evidence for the xx99 posture
  decision.** Cat E is the "cheapest to unblock" of the five layers
  for Option B — flip the flag ON, then Cat D F1 + Cat C F4 become
  the gating repairs. But Cat E cannot single-handedly resolve any
  posture; requires upstream populate for the join to close.
  **Rigby SIGN cycle 1 Q3(b) fold nuance:** Flipping the Cat E flag
  DOES yield **partial usefulness inside Cat E even if Cat D remains
  broken** — the delegated-execution lifecycle path would begin
  writing `execution_id` into OpsRunEvent.detail, strengthening the
  Cat E → Cat C join potential once Cat C PA-coverage exists
  (S1703 F4). The Cat D ToolCallRecord join (F7) remains blocking
  irrespective of the Cat E flag state. So "resolves nothing" is too
  strong for Option B posture writ large; the more precise framing is
  "resolves nothing for the ToolCallRecord join, but unlocks the
  execution_id spine cell in the Cat E → Cat C axis."

---

## 2. Domain Purpose

**Q1 — What is Cat E telemetry accountable for?** Ops / Mission
orchestration audit trail. Every orchestrated multi-step run
(ops-domain: smoke tests, deploy verifies, ops control loops OR
mission-domain: Employee OS daily jobs) writes one `OpsRun` header
row plus one `OpsRunEvent` per timeline event (step start, step
pass, step fail, info, heartbeat). The audit trail supports:
(a) mission verdict issuance (Rigby via `mission_verdict` PA tool
inspects OpsRunEvent evidence + issues certify/reject/defer verdict);
(b) escalation Deliverable dedupe (`_find_prior_escalation_run` at
`mission_runner.py:1250-1275` queries prior failed OpsRun rows by
`(failed_step, error_signature)`); (c) daily idempotency
(`_existing_mission_for_today` at `:759-772` prevents duplicate
daily runs); (d) Employee OS `evidence_for_mission` PA tool
(`core/services/td_handlers_employee.py`) surfaces mission timeline
to Rigby for post-hoc review.

**Q2 — Where does Cat E end?** Cat E DOES NOT own the business
logic of what a step does (that's the caller's step functions — the
Employee OS job modules at `core/jobs/docs_cascade.py`,
`core/jobs/bug_triage.py`, etc.), DOES NOT own agent dispatch or LLM
execution (Cat C/B scope), DOES NOT own tool schemas or tool-registry
concerns (Cat D scope + PA tool surface concern), DOES NOT own
BodyCoordinator integration or authority enforcement or scheduling
(all Employee OS scope). Cat E owns the **orchestration timeline
persistence primitive** — the `OpsRun`/`OpsRunEvent` write contract
+ MissionRunner lifecycle policy — and stops there. Rigby v0 event
intake activation is post-arc T-slot per parent §6.2 parked candidate;
this audit does NOT design that activation.

---

## 3. Canonical Entry Points

Writer surface (five sites, all cross-referenced against parent §5.E boundary):

| Writer | File:Line | Domain | Method | Notes |
|---|---|---|---|---|
| MissionRunner run creation | `core/employees/mission_runner.py:778` | mission | `OpsRun.objects.create(...)` | Employee OS lifecycle engine; I1 idempotency guaranteed |
| MissionRunner event emission | `core/employees/mission_runner.py:812-816` | mission | `OpsRunEvent.objects.get_or_create(run, label, defaults={event_type, detail})` | I3 event idempotency |
| Generic Ops Run Tracker | `core/tools/ops_run_tracker.py:34` | ops | `OpsRun.objects.create(...)` | Ops-domain multi-step ops (smoke tests, deploy verifies) |
| Rigby event intake mission | `core/services/rigby_event_intake.py:416` | mission | `OpsRun.objects.get_or_create(mission_id=uuid.UUID(event_id))` | run_kind='intake'; PA-tool-triggered |
| Rigby event intake lifecycle events | `core/services/rigby_event_intake.py:434,:450,:508,:522` | mission | `OpsRunEvent.objects.get_or_create(...)` | intake_started → impact_assessed → decision_made → finalize |
| Rigby delegation lifecycle handler | `core/signals/rigby_delegation_signals.py:79-84` | mission (delegated executions only) | `OpsRunEvent.objects.create(run, event_type, label, detail={'execution_id': ..., 'agent_name': ..., ...})` | **FLAG-GATED by `settings.RIGBY_DELEGATION_ENABLED` (default False)**; F1 finding |
| Mission verdict PA tool | `core/services/td_handlers_employee.py:434` → `core/employees/mission_verdict.py` | mission | Emits `verdict_issued:{certified\|rejected\|deferred}` OpsRunEvent + flips OpsRun.status to terminal | Called by Rigby only (auth-gated) |

Reader surface (consumers):

| Reader | File:Line | Purpose |
|---|---|---|
| Employee OS status derive | `core/employees/status.py:53-251` | Reads OpsRun(domain='mission', run_kind) with date window → trust_ratio + latest_mission summary |
| Employee OS evidence_for_mission | `core/employees/status.py:347-508` | Joins OpsRun + OpsRunEvent + LLMCallEvent + ToolCallRecord (F7 broken for ToolCallRecord) |
| Focus Cockpit ops overview | `core/views_diagnostics.py:1511-1610` | Reads failed OpsRuns + error signatures for last N hours |
| Cockpit ops-runs list/detail | `core/views_diagnostics.py:4034-4115` | REST endpoints for OpsRun timeline browse (IsStaff auth) |
| Employee API mission detail | `core/views_employee_api.py:211-281` | REST endpoints for mission timeline + evidence (IsAdminUser auth) |
| Rigby delegation signal idempotency check | `core/signals/rigby_delegation_signals.py:60-71` | `_has_event()` queries OpsRunEvent by (run, label, detail__execution_id) |
| Escalation dedupe | `core/employees/mission_runner.py:1250-1275` | `_find_prior_escalation_run` queries prior failed OpsRuns by (failed_step, error_signature) within window |

---

## 4. Major Models

### `OpsRun` (`core/models_ops_runs.py:11-89`)

Fields:

| Field | Type | Indexes | Default | Purpose |
|---|---|---|---|---|
| `id` | UUIDField(PK) | PK | uuid.uuid4 | — |
| `title` | CharField(200) | — | — | Human-readable summary |
| `run_type` | CharField(40, choices) | — | — | Enum: `ops_loop`, `smoke_test`, `deploy_verify`, `manual`, `llm_routing` (5) |
| `status` | CharField(20, choices) | — | 'running' | Enum: `running`, `passed`, `failed`, `partial` (4) |
| `triggered_by` | CharField(100, choices) | — | 'manual' | Enum: `beat`, `pa_tool`, `management_cmd`, `manual` (4) |
| `started_at` | DateTimeField | — | auto_now_add | — |
| `finished_at` | DateTimeField | — | null | Set on terminal transition |
| `summary` | JSONField | — | dict() | Free-form decision/event metadata (F1 candidate for detail-JSON threading) |
| `event_count` | PositiveIntegerField | — | 0 | Child OpsRunEvent count |
| `fail_count` | PositiveIntegerField | — | 0 | Count of failed step events |
| `domain` | CharField(20, choices) | **db_index** | 'ops' | S1250 PR3: ops vs mission scope separator; enum: `ops`, `mission` |
| `run_kind` | CharField(40) | — | '' | S1250 PR3: sub-classification within domain; blank for ops-domain |
| `mission_id` | UUIDField | **db_index** | null | S1250 PR3: mission identity; null for ops-domain rows |

**Correlation columns:** ONLY `mission_id` (mission-domain only) and the implicit PK `id`. NO `execution_id`, NO `trace_id`, NO `tool_call_id`, NO `task_id`, NO `agent_execution_id`, NO `llm_call_id`, NO `celery_task_id`, NO `conversation_id`. See F2.

**No `unique_together`, no composite indexes.** Meta declares `ordering = ['-started_at']` only. Common query pattern `filter(domain='mission', mission_id=uuid)` uses the single-field `domain` index then filters `mission_id` in a second pass. Acceptable at v0 volumes; risks O(n) at scale.

### `OpsRunEvent` (`core/models_ops_runs.py:91-117`)

Fields:

| Field | Type | Indexes | Default | Purpose |
|---|---|---|---|---|
| `id` | UUIDField(PK) | PK | uuid.uuid4 | — |
| `run` | FK → OpsRun (CASCADE, related_name='events') | implicit | — | Parent run |
| `event_type` | CharField(20, choices) | — | — | Enum: `step_start`, `step_pass`, `step_fail`, `info`, `heartbeat` (5) |
| `label` | CharField(200) | — | — | Event-specific label (idempotency key with `run` per I3) |
| `detail` | JSONField | — | dict() | Free-form event metadata (F1 candidate for cross-cat correlation IDs) |
| `created_at` | DateTimeField | — | auto_now_add | — |

**Correlation columns:** NONE except the parent `run` FK. F2 gap.

**No composite index.** Meta declares `ordering = ['created_at']`. Common query pattern `run.events.all()` uses the FK index but scales linearly with events-per-run.

### Migrations lineage

- `0277_ops_runs.py` (2026-03-02): Initial CreateModel for OpsRun (10 fields) + OpsRunEvent (5 fields with FK).
- `0370_session_1250_opsrun_mission_fields.py` (2026-06-28): AddField `domain`, `run_kind`, `mission_id` to OpsRun. Additive-only, no backfill, no behavior change per migration docstring (S1250 PR3).
- No subsequent schema changes at HEAD.

---

## 5. Major Services

### MissionRunner (`core/employees/mission_runner.py`, 1758 lines)

Session 1256 PR 1.1 introduction. Reusable Employee OS mission lifecycle engine. Extraction goal: mission lifecycle policy separate from Employee/Job-specific implementation. I9 (no employee-specific imports) is contract-tested.

Nine invariants I1-I9 (see F8 for verification detail).

Public API:
- `MissionRunner(config: MissionRunnerConfig, steps: Sequence[Step], **hooks).run() -> MissionRunResult`
- `run_for_existing(mission)` secondary entry point for tests + PA `run_now` path

### Ops Run Tracker (`core/tools/ops_run_tracker.py`)

Generic ops-domain run tracker. Direct `OpsRun.objects.create()` at line 34 (no idempotency; caller-owned dedupe). Used for smoke tests, deploy verifies, ad-hoc ops-loop runs.

### Rigby event intake (`core/services/rigby_event_intake.py`)

PA-tool-triggered mission intake path. Uses `get_or_create(mission_id=uuid.UUID(event_id))` at line 416 for idempotency. Lifecycle events at `:434,:450,:508,:522` (intake_started → impact_assessed → decision_made → finalize).

### Rigby delegation lifecycle handler (`core/signals/rigby_delegation_signals.py`)

Session 1250 PR 8. Post-save signal receiver on `AgentExecution`. Appends OpsRunEvent rows to the parent MissionRun for delegated executions (`parent_object_type='RigbyWorkItem'`). Labels: `agent_assigned`, `agent_completed`, `verification_started`, `verification_completed`, `mission_closed`.

**Gated by `settings.RIGBY_DELEGATION_ENABLED` (default False)** at `:22-25`. When OFF, the handler short-circuits even for delegated executions. Empirically at HEAD the flag is OFF and 0 rows have been written by this path (F1 evidence).

### Ops Autopilot (`core/services/ops_autopilot/`, 24000 lines across 12 modules)

Consumer surface. Three god-service modules (`core.py` 2905, `intelligence.py` 2790, `governance.py` 2568). Independent of Cat E — does NOT write OpsRun/OpsRunEvent and does NOT read OpsRunEvent. Not in scope per parent §5.E boundary but catalogued for maturity assessment (F5 orthogonal position).

### Scheduled Diagnostic Runner (`core/services/scheduled_diagnostic_runner.py`)

Shared primitive used by CTO/COO/Trend Analysis daily diagnostics. Introduced S1094. Beat-wired at `core/celery.py:306-329` (F4 evidence). Reads Cat A/B/C data (CeleryTaskEvent + AgentExecution + Deliverable + spider data), NOT OpsRunEvent (F5 evidence).

### `tasks_ops.py` (`core/tasks_ops.py`, 3878 lines)

Auto-generated by `tools/do_extract.py` — extracted `_impl_<name>` functions for `@shared_task` implementations in `core/tasks.py`. Extraction is INCOMPLETE (imports private helpers from `core.tasks` at line 23, and further lazy imports inside method bodies at line 1992). This is a known design artifact per file header.

---

## 6. Major APIs and Interfaces

### REST endpoints

Employee OS surface (`core/views_employee_api.py`):

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `GET /api/employees/` | GET | IsAdminUser | List registered AI Employees |
| `GET /api/employees/<handle>/` | GET | IsAdminUser | Employee detail + assigned JobContracts |
| `GET /api/employees/<handle>/jobs/<job_key>/status/` | GET | IsAdminUser | Daily-read status surface (window=7d/30d/90d); wraps `derive_status` |
| `GET /api/missions/<mission_id>/` | GET | IsAdminUser | Minimal OpsRun detail (8 fields) |
| `GET /api/missions/<mission_id>/evidence/` | GET | IsAdminUser | Full OpsRunEvent evidence join |

Diagnostics surface (`core/views_diagnostics.py`):

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `GET /api/cockpit/ops/overview/` | GET | Authenticated | Focus Cockpit: health checks + failing agents + error signatures + failed runs |
| `GET /api/cockpit/ops-runs/` | GET | IsStaff | List recent OpsRuns (filters: run_type, status, hours, limit) |
| `GET /api/cockpit/ops-runs/<uuid>/` | GET | IsStaff | OpsRun detail + all events |

All read-only; no write endpoints. Writes flow via PA tools + beat schedule + signals (§3).

### PA tools

| Tool | Handler File:Line | Actions | Read/Write | OpsRun Writer? |
|---|---|---|---|---|
| `ops_tool` | `core/services/td_handlers_ops.py:160` | 17 actions incl. `celery_task_history` (reads Cat A), execution_detail, execution_search, memory_pressure, ... | Read-only | No |
| `employee_tool` | `core/services/td_handlers_employee.py:100` | describe, run_now (dispatches Celery task), status, evidence_for_mission | Read-only (run_now dispatches; does not write OpsRun directly) | No — dispatch only |
| `mission_verdict` | `core/services/td_handlers_employee.py:434` | certify, reject, defer | **Write** | **Yes** — emits `verdict_issued:<verdict>` OpsRunEvent + mutates OpsRun.status |

`mission_verdict` is the sole PA tool that writes Cat E state. Auth-gated to Rigby-only (`_verify_rigby_caller` per S1252 PR 2 pattern).

### WebSocket consumers

None. Grep confirmed no `class *Consumer(...)` references OpsRun/OpsRunEvent.

### Management commands

- `core/management/commands/ops_verify.py:14-100+`: on-demand ops verification (deploy_verify, pa_tools_smoke, DB health, error summary 24h). Admin-only manual trigger.

---

## 7. Runtime Flows

### MissionRunner mission run (mission-domain)

```
Caller (beat task / PA run_now / test)
  └─ MissionRunner(config, steps, **hooks).run()
     ├─ Preflight: _existing_mission_for_today() [I1]
     │  └─ If found + status='running' → cached envelope [I2]
     │  └─ If found + status terminal → cached envelope, no re-run [I1]
     │  └─ Else → proceed
     ├─ CREATE OpsRun row [mission_runner.py:778]
     │  └─ OpsRun.objects.create(domain='mission', run_kind, mission_id=uuid4(), triggered_by='beat', status='running')
     ├─ EMIT 'run_started' info event [I3, get_or_create]
     ├─ EMIT 'authority_contract_observed' info event (if config.job_contract)
     ├─ preflight_fn(summary_acc) [I8 contained]
     ├─ STEP LOOP [I5]
     │  For each step:
     │  ├─ EMIT '{step}_started' step_start event [I3]
     │  ├─ EXECUTE step.fn(mission) → StepResult(passed, output, duration_ms, extra)
     │  ├─ EMIT '{step}_passed' | '{step}_failed' event [I3]
     │  └─ If failed → break, emit '<remaining>_skipped' info events with reason='prior_failure'
     ├─ postflight_fn (I8 contained, signature-detected)
     ├─ ESCALATION on failure [I6 atomic + I7 dedupe]
     │  └─ transaction.atomic():
     │     ├─ _find_prior_escalation_run(failed_step, error_signature, window)
     │     ├─ create-new OR append-to-prior Deliverable
     │     ├─ status flip if new
     │     └─ EMIT 'escalation_emitted' info event [I6 inside txn]
     ├─ VERDICT emission [I4]
     │  └─ auto_emit_verdict? emit_mission_verdict(certified|rejected|partial) : status flip only
     ├─ shift_report_fn(mission) [I8 contained]
     └─ RETURN MissionRunResult
```

### Rigby event intake (mission-domain)

```
PA tool caller (Rigby)
  └─ rigby_event_intake.run(event) [rigby_event_intake.py:416]
     ├─ get_or_create OpsRun(mission_id=uuid.UUID(event_id), run_kind='intake', triggered_by='pa_tool')
     ├─ EMIT 'intake_started' event [:434]
     ├─ EMIT 'impact_assessed' event [:450]
     ├─ EMIT 'decision_made' event [:508]
     └─ EMIT 'finalize' event [:522]
```

### Rigby delegation lifecycle (mission-domain, FLAG-GATED)

```
AgentExecution.save (post-save signal)
  └─ rigby_delegation_signal_handler [rigby_delegation_signals.py]
     ├─ IF settings.RIGBY_DELEGATION_ENABLED is False → short-circuit ← EMPIRICAL STATE AT HEAD (F1)
     ├─ IF parent_object_type != 'RigbyWorkItem' → short-circuit
     ├─ On creation → EMIT 'agent_assigned' event with detail={'execution_id': ...}
     ├─ On terminal status → EMIT 'agent_completed' event
     ├─ Deterministic verification (no LLM):
     │  └─ EMIT 'verification_completed' event with verdict ∈ {verified, failed_agent_error, failed_no_llm_calls}
     └─ EMIT 'mission_closed' event
```

### Ops-domain generic run (ops smoke test / deploy verify)

```
Caller (management command / PA tool)
  └─ OpsRunTracker.create(title, run_type, triggered_by='pa_tool')
     └─ OpsRun.objects.create(domain='ops', run_kind='', mission_id=null, run_type='smoke_test', ...)
  └─ For each step:
     └─ OpsRunEvent.objects.create(run, event_type='step_pass', label, detail={...})
```

### Reader flow: `evidence_for_mission` join (F7 broken)

```
Rigby PA tool 'evidence_for_mission'
  └─ core/services/td_handlers_employee.py:handler
     └─ core/employees/status.py:evidence_for_mission(mission_id, verbose)
        ├─ QUERY OpsRun.objects.get(mission_id) [WORKS]
        ├─ QUERY OpsRunEvent.filter(run__mission_id=mission_id) [WORKS]
        ├─ QUERY LLMCallEvent.filter(metadata__ops_run_id=str(run.id)) [WORKS — mission_verdict.py:117-150 populates]
        ├─ QUERY ToolCallRecord.filter(parameters__ops_run_id=str(run.id)) [EMPTY — Cat D dispatcher never threads]
        └─ QUERY ToolCallRecord.filter(trace_id=execution.trace_id) [EMPTY — S1704 F1 100% NULL]
```

---

## 8. Data Ownership and Lifecycle

**Ownership.** MissionRunner owns the mission-domain lifecycle policy;
`OpsRunTracker` owns the ops-domain generic writer. `mission_verdict`
PA tool owns terminal-verdict-issuance; `rigby_delegation_signals`
owns lifecycle-event append for delegated executions (flag-gated).
`rigby_event_intake` owns intake-mission-lifecycle. Employee OS
`status` module owns read-time aggregation (derive_status +
evidence_for_mission).

**Lifecycle.**

- **Create:** `MissionRunner._create_mission_row()` → `OpsRun.objects.create(status='running', started_at=now)`.
- **Progress:** `MissionRunner._emit_event()` → `OpsRunEvent.objects.get_or_create(...)` per step.
- **Terminate:** `emit_mission_verdict()` at `mission_verdict.py` → set `OpsRun.status='passed'|'failed'|'partial'` + `finished_at=now` + emit `verdict_issued:<verdict>` event.
- **Escalate:** `_handle_failure_escalation()` at `mission_runner.py:1194-1248` inside `transaction.atomic()` → Deliverable create-or-append + `escalation_emitted` event.
- **Retention:** **NONE** at HEAD (F6). No cleanup task, no watchdog, no archival.

---

## 9. Integrations With Other Domains

### Cross-domain integration matrix

| Peer domain | Direction | Strength | Evidence | Note |
|---|---|---|---|---|
| Employee OS (MissionRunner primitives + Jobs) | ↕️ (Cat E provides the persistence primitive) | **STRONG** | `mission_runner.py:778,:812`; contract-tested via `MissionRunnerImportContractTests` | Cat E is Employee OS's audit trail; boundary held via I9 |
| Deliverable (Escalation) | Cat E → Deliverable | **STRONG** | `mission_runner.py:1209` atomic transaction | I6 atomicity verified |
| PA tool surface (Rigby) | ↕️ | **STRONG** | `mission_verdict` writes; `employee_tool.run_now` dispatches; `evidence_for_mission` reads | 3 read tools + 1 write tool |
| Cat A (CeleryTaskEvent) | Cat A → Cat E via beat | **STRONG (trigger)** / **MISSING (correlation)** | Beat fires MissionRunner runs; but no `celery_task_id` correlation column at Cat E (F2) | Correlation debt inherits S1704 F2 pattern |
| Cat B (LLMCallEvent) | Cat E → Cat B via metadata JSON | **STRONG (write)** / **STRONG (read)** | `emit_mission_verdict` at `mission_verdict.py:117-150` populates `LLMCallEvent.metadata.ops_run_id`; `evidence_for_mission` reads via `metadata__ops_run_id` | Only Cat E → Cat X correlation that works today |
| Cat C (AgentExecution) | Cat E → Cat C via Rigby delegation signal (FLAG-GATED) | **LATENT** | `rigby_delegation_signals.py:70` uses `detail__execution_id` for idempotency check; empirically flag OFF | Would be STRONG if flag flipped ON |
| Cat D (ToolCallRecord) | Cat E → Cat D via `parameters.ops_run_id` intended surface | **BROKEN** | `status.py:475-483` queries `parameters__ops_run_id` but Cat D dispatcher never threads it (F7); `deliverable_provenance.py:105` queries `trace_id` but S1704 F1 100% NULL | Two orthogonal write-gap paths |
| Chief of Staff daily brief | Cat E → chat | **PARTIAL** | 2 of 4 employees wire `shift_report_fn`; docs_cascade wires `pa_post_fn`; platform_audit + bug_triage_specialist do not | Optional hooks pattern |
| Discord | Cat E → Discord | **MISSING** | No `ops_tool` action surfaces OpsRun/mission status to Discord | Not a v0 concern |
| Human Attention / Boardroom | Cat E → HAI | **MISSING** | No MissionRunner escalation path writes HumanAttentionItem rows | Deliverable escalation subsumes for now |

### D74 axis contribution (F9)

Cat E adds a fourth cell to the cross-cat correlation axis matrix:

| Layer | trace_id column | execution_id column | mission_id column | Runtime population | Posture |
|---|---|---|---|---|---|
| Cat A CeleryTaskEvent | ❌ | ❌ | ❌ | task_id (unique) populated | Populate baseline |
| Cat B LLMCallEvent | ❌ (metadata JSON only) | ✅ (FK) | metadata JSON | execution_id via FK; ops_run_id via metadata JSON | Semi-populated |
| Cat C AgentExecution | ✅ | (self) | ❌ | trace_id populated by S1703 F9 F1 fold | S1703 F4 CRITICAL: PA path coverage gap |
| Cat D ToolCallRecord | ✅ (indexed) | ❌ | ❌ | trace_id 100% NULL empirically | S1704 F1 CRITICAL: runtime failure |
| Cat E OpsRunEvent | ❌ | ❌ (would live in detail JSON) | ↕️ (via `run` FK to OpsRun.mission_id) | detail JSON 0/224 rows with execution_id | **S1705 F1 LATENT: flag-gated design-intent** |

Cat E is the cheapest to unblock for Option B via `RIGBY_DELEGATION_ENABLED=True`, but by itself resolves nothing — Cat D F1 + Cat C F4 remain gating repairs regardless of Cat E's flag state.

### Cross-domain audit §14 alignment

Read `docs/research/platform/cross_domain_integration_audit.md` §14 v3 refresh (line 1977+). §14.7 explicitly reserves §14.8 for Group 1700 xx99 close consumption. Current §14.1-§14.6 rows (Memory / Revenue / Sports / Content arc closes + CX-P1..CX-P6 patterns) do NOT directly reference Cat E territory.

CX-P applicability to Cat E:

- **CX-P1 (Runtime-owner MISSING):** TANGENTIAL. MissionRunner is infrastructure primitive, not employee-owned. Applies at employee-instantiation level (S1499 D55 scope), not at Cat E.
- **CX-P2 (single-arc scope-honest):** NOT APPLICABLE. Cat E is a persistence primitive scoped within Group 1700 Observability arc.
- **CX-P6 (Parallel-schema drift):** NOT APPLICABLE. `OpsRun(domain='mission')` IS the canonical mission representation. No parallel MissionExecution table or intelligence-plane analog identified. RigbyWorkItem references OpsRun via FK, not parallels it.

---

## 10. Event Flows

### Event vocabulary (labels observed at HEAD)

48 distinct labels across 224 OpsRunEvent rows. Top 25 by count:

| Label | Count | Owner |
|---|---|---|
| `default` | 22 | Generic ops writer (OpsRunTracker) |
| `run_started` | 17 | MissionRunner (all 17 mission-domain runs) |
| `pa_tools_smoke` | 14 | ops_verify management command |
| `verdict_issued:certified` | 12 | mission_verdict PA tool |
| `authority_contract_observed` | 11 | MissionRunner (missions with `job_contract` configured) |
| `step_1_index_started` | 7 | docs_cascade job |
| `step_2_corpus_started/passed` | 6/6 | docs_cascade job |
| `step_3_sync_started/passed` | 6/6 | docs_cascade job |
| `step_4_embed_started/passed` | 6/6 | docs_cascade job |
| `step_5_drift_observed` | 6 | docs_cascade job |
| `step_brief_workflow_started/passed` | 4/4 | morning_brief job (Chief of Staff) |
| `step_1_collect_celery_failures_started/passed` | 4/4 | bug_triage_daily job |
| `step_2_collect_agent_failures_started/passed` | 4/4 | bug_triage_daily job |
| `step_3_collect_mission_verdicts_passed` | 4 | bug_triage_daily job |
| `step_4_collect_authority_events_started` | 4 | bug_triage_daily job |
| `step_5_cluster_by_signature_passed` | 4 | bug_triage_daily job |
| `step_6_generate_triage_report_started` | 4 | bug_triage_daily job |
| `step_7_record_run_summary_started` | 4 | bug_triage_daily job |

### Sample `detail` JSON keys

- Step events: `{'step': 'step_5_cluster_by_signature', 'duration_ms': ..., 'cluster_count': ..., 'top_cluster_occurrences': ...}` — step-specific metrics
- Triage report: `{'step': ..., 'duration_ms': ..., 'report_chars': ..., 'deliverable_id': ..., 'recommendations_count': ...}` — deliverable ID referenced (7 rows carry `deliverable_id` key)
- Run summary: `{'step': ..., 'duration_ms': ..., 'cluster_count': ..., 'agent_failures_count': ..., 'missions_today_total': ..., 'celery_failures_count': ...}` — aggregate metrics

**0/224 rows** carry `execution_id`, `trace_id`, `task_id`, `tool_call_id`, `agent_execution_id`, `llm_call_id`, `celery_task_id`, `mission_id`, `conversation_id`, or `agent_name` in the detail JSON. Only `ops_run_id` (1 row — likely escalation_emitted) and `deliverable_id` (7 rows) appear as cross-object references. See F1.

### Escalation event (I6 atomicity)

The `escalation_emitted` event's `detail` includes `deliverable_id`, `ops_run_id`, `error_signature`, `deduped`, `prior_ops_run_id`, `pa_post_id`. Written inside `transaction.atomic()` at `mission_runner.py:1209`, coupled with Deliverable create-or-append + status flip. Verified I6 contract.

---

## 11. Existing Documentation

| Doc | Session/date | Cat E coverage | Freshness |
|---|---|---|---|
| `docs/topics/employee-os.md` | S1260 refresh 2026-06-30 | Employee OS orientation; :64-65 names `evidence_for_mission` join surface (F7 target) | CURRENT |
| `docs/EMPLOYEE_OS_PRIMITIVES.md` | S1253 finalized | 25-row primitives inventory incl. `AIEmployee`, `JobContract`, `OpsRun`, `OpsRunEvent`, MissionRunner; anti-duplication rules | CURRENT + LOCKED |
| `docs/PLATFORM_WHAT_IT_IS.md` | S1223 refresh 2026-05-24 (Layer 3.5) | Employee OS narrative; 3-employee count (drift per F3) | PARTIAL DRIFT (F3) |
| `docs/PLATFORM_INVENTORY.md` | Auto-regen 2026-07-02 | Employees autoblock = 3 rows (drift per F3) | PARTIAL DRIFT (F3) |
| `CLAUDE.md` §Detailed Breakdown row Employees | 2026-06-30 S1260 PR-γ | 3 employees (drift per F3) | PARTIAL DRIFT (F3) |
| `docs/topics/celery-workers.md` | S1167 last touch | No Cat E cross-reference | NO COVERAGE (not scope) |
| `docs/topics/agent-system.md` | S1115 last touch | No MissionRunner cross-reference; Cat C/D territory | NO COVERAGE (not scope) |
| `docs/handoffs/SESSION_1250_*.md` | 2026-06-18 | OpsRun.domain/run_kind/mission_id fields introduced | Historical |
| `docs/handoffs/SESSION_1252_*.md` | 2026-06-28 | First production Employee (Rigby v0); mission_verdict PA tool; escalation | Historical |
| `docs/handoffs/SESSION_1256_*.md` | 2026-06-22 | MissionRunner PR 1.1 design + orchestrator lifecycle | Historical |
| `docs/handoffs/SESSION_1258_*.md` | 2026-06-30 | Morning Brief beat migration (Chief of Staff) | Historical |
| `docs/handoffs/SESSION_1259_*.md` | 2026-06-30 | First-fire verification (both beats fired certified) | Historical |
| `docs/handoffs/SESSION_1267_*.md` | ~2026-06-30 | Bug Triage Specialist 4th employee ship (F3 evidence) | Historical |
| `docs/research/employee_os_communication_substrate_audit.md` | S1268 | 4-substrate inventory (DEEP research, not authoritative) | RESEARCH-ONLY |
| `docs/research/employee_os_communication_protocol_sketch.md` | S1268 | Inter-employee comms v0 one-way sketch | RESEARCH-ONLY, PARKED |

---

## 12. Research Coverage

**Classification: DEEP** per playbook §12.

Cat E territory has been covered by multiple prior arcs:

- **S1250 PR3** (extraction): introduced `domain`/`run_kind`/`mission_id` fields to OpsRun; no separate MissionRun model (design intent locked)
- **S1252** (Rigby v0): first production employee; mission_verdict + escalation + shift-report primitives; full contract review
- **S1253** (Employee OS foundation): primitives locked; anti-duplication rules
- **S1256** (MissionRunner PR 1.1): reusable orchestrator; I1-I9 invariants documented
- **S1257** (Chief of Staff PR 3.1/3.2): second employee
- **S1258** (Morning Brief beat migration): CoS morning_brief on MissionRunner
- **S1259** (first-fire verification): both beats fired certified 2026-06-30; production foundation validated
- **S1260** (Phase 2 planning + discoverability): CLAUDE.md rows added
- **S1264** (authority enforcement warn-mode)
- **S1267** (Bug Triage Specialist PR 4.1): 4th employee ship — MissionRunner arc validates cross-employee reuse
- **S1268** (substrate audit + protocol sketch): research-only inventory + inter-employee comms sketch (parked pending Employee #4 posture decision)

Prior audits DID NOT cover:
- Retention policy (F6)
- Cross-cat correlation posture (this audit F1 + F2 + F9)
- `evidence_for_mission` empirical join reality (F7)
- Ops-domain writer coverage (this audit — ops_verify smoke tests only, no beat-wired ops-loop writer at HEAD)

---

## 13. Architecture Maturity

Multi-axis assessment per playbook §12:

| Axis | Verdict | Evidence |
|---|---|---|
| Writer mechanism | **STABLE** | I1-I9 invariants VERIFIED (F8); tests at `test_mission_runner.py:272-1600` cover idempotency + ordering + escalation + import contract; production first-fire S1259 verified both beats certified |
| Coverage | **PARTIAL** | 4/4 employees producing daily OpsRun(domain='mission') rows via MissionRunner. Ops-domain coverage: 19 smoke_test rows from ops_verify; no beat-wired ops-loop writer at HEAD (`run_ops_autopilot` + `post_ops_digest` intentionally deferred per AUDIT_FINDINGS.md §12). Retention absent (F6). |
| Cross-cat correlation contract | **NAMED-BUT-BROKEN** | evidence_for_mission ToolCallRecord join is EMPIRICALLY EMPTY (F7 — two orthogonal write-gap paths: S1704 F1 trace_id NULL + Cat D never threads `parameters.ops_run_id`); LLMCallEvent join WORKS via metadata JSON; execution_id detail JSON path FLAG-GATED off (F1) |
| Downstream pipeline (orthogonal) | **STRONG** | CTO/COO/Trend Analysis daily diagnostics EXIST + beat-wired at 7:15/7:30/7:45 Denver (F4); NOT WRITE-ONLY-FORGOTTEN like S1704 F4 |
| Downstream pipeline (OpsRunEvent-consuming) | **EMPTY** | Zero pipelines aggregate OpsRunEvent detail JSON; producer-only role resolved (F5) |
| Risk | **MEDIUM** | Mission-domain lifecycle production-solid; cross-cat correlation gap is design-intent-latent not runtime-broken; retention unaudited but growth is small-cadence bounded (~657 OpsRun/year, ~4,088 OpsRunEvent/year); F7 named-but-broken has explicit Cat D-side gating repair |

---

## 14. Known Drift

Discovered via verifier-loop passes (pre-Explore + post-Explore):

| # | Doc | Runtime | Severity | Type | Owed to |
|---|---|---|---|---|---|
| D1 | CLAUDE.md :150-172 "3 Employees" | Registry `_EMPLOYEES_BY_HANDLE` has 4 handles (F3) | MEDIUM | Count drift | xx99 anchor-update PR |
| D2 | PLATFORM_INVENTORY.md Employees autoblock "3" | Same 4-employee registry | MEDIUM | Count drift | Regen via `generate_platform_inventory` |
| D3 | Parent §5.E "CTO daily / COO daily / Trend Analysis daily" (implied consumers of Cat E) | Diagnostics DO EXIST + ARE beat-wired but do NOT consume OpsRunEvent (F4 + F5) | LOW | Boundary clarification | xx99 parent §5.E addendum |
| D4 | `docs/topics/employee-os.md:64-65` `evidence_for_mission` join surface | ToolCallRecord join is EMPIRICALLY BROKEN (F7); topic doc names the surface but does not flag the runtime gap | HIGH | Named-but-broken integration | xx99 §7.4 + topic-doc addendum |
| D5 | Migration 0370 docstring "additive-only, no backfill" | Verified at HEAD (F2 — no additional correlation columns added since) | LOW | Confirmed | — |
| D6 | `tasks_ops.py` header "Auto-generated by tools/do_extract.py — do not edit section markers" | File has no visible section markers at HEAD; extraction is INCOMPLETE (imports private helpers from `core.tasks` at line 23) | LOW | Extraction status ambiguous | Phase 2 or extraction-cleanup PR |
| D7 | Rigby delegation lifecycle handler exists but 0/224 events written at HEAD | Handler is FLAG-GATED off by default (`RIGBY_DELEGATION_ENABLED=False`); design intent latent (F1) | INFORMATIONAL | Flag-state confirmation | Doc: cross-reference from employee-os.md to signal handler + flag |
| D8 | ARCHITECTURE_INDEX §8 timeline table drift | Missing rows for S1605 + S1606 + S1699 (Group 1600); inherited from S1704 §14 | LOW | Existing carry-over | Follow-up docs PR (not this session) |

**D4 severity justification (Rigby SIGN cycle 1 Q2(b) fold):** Severity
remains HIGH even though the fix is upstream (Cat D F1 trace_id write
coverage + Cat D dispatcher-side `parameters.ops_run_id` threading),
because this is a **Chris-facing operator surface** (`evidence_for_mission`
PA tool) whose documented join path is non-functional at HEAD. Doc/feature
contract breaches on Chris-visible surfaces earn HIGH regardless of where
the root-cause repair lives.

Verifier-loop corrections applied in this audit:

- **VC1 (F3 corrected):** Pre-Explore prior "3 Employees" (from Explore Agent 5 topic-doc reading) was DOC-DERIVED; Post-Explore ORM check confirmed 4 handles in `_EMPLOYEES_BY_HANDLE`. Explore Agent 6 correctly flagged the drift. Fold corrected in §1.1 F3.
- **VC2 (F4 vs Agent 6 F2 claim corrected):** Explore Agent 6 claimed "CTO/COO/Trend Analysis daily DOES NOT EXIST" (searched Ops Autopilot module for the strings). Post-Explore grep found them at `core/services/diagnostics/{cto_daily,coo_daily}.py` + `core/services/scheduled_diagnostic_runner.py`, and beat-wired at `core/celery.py:306-329`. Agent 2 was correct. Fold: F4 documents the POSITIVE differentiator; the misconception was searching the wrong package.
- **VC3 (F1 vs Agent 1 claim corrected):** Explore Agent 1 claimed `execution_id` IS threaded into OpsRunEvent.detail via `rigby_delegation_signals.py:70`. Post-Explore ORM check showed 0/224 rows with execution_id key. Reading the source revealed the writer path IS built to populate execution_id but is FLAG-GATED off by `settings.RIGBY_DELEGATION_ENABLED=False`. Fold: F1 distinguishes DESIGN-INTENT-LATENT (Cat E) from SCHEMA+RUNTIME-BROKEN (S1704 F1 at Cat D).

---

## 15. Known Technical Debt

| Item | Severity | Rationale | Owed to |
|---|---|---|---|
| No correlation ID columns on OpsRun/OpsRunEvent (F2) | HIGH | Parallel to S1704 F2 HIGH; blocks Option A posture; blocks Cat E-side spine consumption without detail-JSON hook | xx99 + S1704 R4 |
| No date-based retention policy (F6) | MEDIUM | Parallel to S1704 F5 MEDIUM + S1702 F4 HIGH; growth manageable at current cadence but unbounded | xx99 |
| `evidence_for_mission` ToolCallRecord join broken (F7) | MEDIUM | Named-but-broken integration; requires Cat D-side write-time fix (S1704 R2) + `parameters.ops_run_id` threading from MissionRunner + dispatcher | xx99 + S1704 R2 |
| `tasks_ops.py` extraction incomplete (D6) | LOW-MEDIUM | Imports private helpers from `core.tasks` at line 23; auto-gen contract unclear at HEAD | Phase 2 |
| No composite indexes on `(domain, mission_id)` or `(domain, run_kind)` | LOW | Small volume at HEAD; query patterns work; risk is unbounded growth (F6) | Post-arc |
| No Django admin registration for OpsRun/OpsRunEvent (analog S1704 F8) | LOW | Not blocking any current flow; xx99 dev-triage ergonomics improvement | xx99 |
| Rigby delegation flag OFF at HEAD (F1) | INFORMATIONAL | Design-intent-latent; unblocks Cat E-side Option B when flipped ON (but Cat D F1 remains gating) | xx99 posture decision |
| Ops-domain beat-wired writer absent | LOW | `run_ops_autopilot` + `post_ops_digest` intentionally deferred per AUDIT_FINDINGS.md §12; not a regression | Post-arc governance |

---

## 16. Boundary Violations

Systematic check per parent §5.E boundary rule (audit stops at OpsRun/OpsRunEvent writer boundary; does NOT own business logic, LLM execution, BodyCoordinator integration, or authority enforcement):

| Candidate | File:Line | Verdict | Rationale |
|---|---|---|---|
| MissionRunner writer paths | `mission_runner.py:778,:812` | LEGITIMATE | In scope; owns mission lifecycle policy per S1256 PR 1.1 |
| Ops Run Tracker | `tools/ops_run_tracker.py:34` | LEGITIMATE | In scope; owns generic ops-domain writer |
| Rigby event intake | `services/rigby_event_intake.py:416,:434-522` | LEGITIMATE | In scope; owns intake-mission lifecycle |
| Rigby delegation signal handler | `signals/rigby_delegation_signals.py:79-84` | LEGITIMATE | In scope; owns delegated-execution lifecycle append (flag-gated) |
| Mission verdict PA tool | `services/td_handlers_employee.py:434` + `employees/mission_verdict.py` | LEGITIMATE | In scope; owns terminal-verdict emission |
| BodyCoordinator integration | (grep in `mission_runner.py` for `BodyCoordinator\|body_coordinator`) | 0 matches | I9 boundary held; MissionRunner does NOT integrate BodyCoordinator |
| Employee-specific imports | `mission_runner.py` module-level | 0 matches to `RIGBY`/`DOCUMENTATION_MANAGER`/`core.tasks_*` | I9 contract-tested; boundary held |
| `tasks_ops.py` cross-domain imports | Line 23 imports private helpers from `core.tasks` | LEGITIMATE (extraction artifact) | Auto-generated file; extraction is intentionally partial |

**No boundary violations detected.** All 5 writer sites in scope per parent §5.E.

---

## 17. Duplicate or Overlapping Systems

Cross-reference with S1273 §5 (14+ event-shaped models):

| System | Overlap with OpsRunEvent | Verdict |
|---|---|---|
| CeleryTaskEvent (Cat A) | Task-scoped, unique task_id | NO OVERLAP — different scope |
| LLMCallEvent (Cat B) | Per-call, FK to AgentExecution | NO OVERLAP — different granularity; LLMCallEvent.metadata.ops_run_id is Cat B→Cat E link, not duplication |
| AgentExecution (Cat C) | Per-execution, trace_id populated by S1703 F9 F1 fold | NO OVERLAP — different scope |
| ToolCallRecord (Cat D) | Per-tool-call | NO OVERLAP — different scope |
| DeliverableEvent | Object-lifecycle transitions | NO OVERLAP — clean separation |
| ImpactEvent | Business impact | NO OVERLAP — orthogonal |
| TriggerEvent | Rule evaluation | NO OVERLAP — orthogonal |
| FleetEvent | Cross-app | NO OVERLAP — orthogonal |
| Cockpit*Event (Incident, Autopilot) | Incident/policy audit | NO OVERLAP — deferred per EVENT_SYSTEM_INVENTORY §4 |
| EngagementEvent, ThreatEvent, ABTestEvent, ConversionEvent, BadContextEvent, RelationshipEvent | Domain-specific | NO OVERLAP |
| Legacy `MissionRun` table | Design intent to fold into `OpsRun(domain='mission')` per S1250 PR3 | NO OVERLAP — no separate table (design-decision confirmed via migration lineage) |

**No duplicate systems.** OpsRunEvent is a **clean specialty model** for orchestration timelines. Session 1250 PR3 chose "add domain field to OpsRun" over "create MissionRun table" — anti-duplication contract per EMPLOYEE_OS_PRIMITIVES.md §2 verified.

### F1-F9 findings expanded

(See §1.1 for lock-in table. Section 17 is the canonical location for
overlap classification; F1-F9 findings are cross-referenced from §1.1
to §14 (drift), §15 (debt), and §9 (integrations) per playbook §11.2.)

---

## 18. Ownership Gaps

| Entity | Documented Owner | De Facto Owner | Gap |
|---|---|---|---|
| MissionRunner infrastructure | EMPLOYEE_OS_PRIMITIVES.md §1 primitive; extraction-locked S1256 | Claude Code (S1256 PR 1.1) | None significant — anti-duplication rules enforce |
| OpsRun/OpsRunEvent writers (5 sites) | None single CODEOWNERS entry | Split across mission_runner, mission_verdict, ops_run_tracker, rigby_event_intake, rigby_delegation_signals | LOW — natural functional split |
| Ops Autopilot pipelines (`core/services/ops_autopilot/`) | None documented | Platform infrastructure debt | LOW — outside Cat E scope per boundary |
| Employee OS primitives docs | EMPLOYEE_OS_PRIMITIVES.md owner = "claude (structure) + rigby (verbatim primitives)" | Actively maintained | None |
| PLATFORM_INVENTORY autoblock regen | Auto-derived via `generate_platform_inventory` mgmt command | Auto | LOW — F3 drift persists until next regen |

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows (playbook §11.2 §19 requirement):

| # | Item | Priority | Type | Owed to |
|---|---|---|---|---|
| R1 | F9 D74 axis posture decision — evaluate Option A (schema execution_id) vs Option B (trace_id spine + `RIGBY_DELEGATION_ENABLED=True`) with Cat E-side lift cost accounting | HIGH | xx99 evidence brief | S1799 canonical summary |
| R2 | F1 rigby_delegation flag posture — decide whether to flip `RIGBY_DELEGATION_ENABLED=True` (unblocks execution_id detail-JSON thread on Cat E) or repair Cat D-side first (S1704 R2) | HIGH | xx99 ADR | S1799 |
| R3 | F7 evidence_for_mission join repair — either (a) MissionRunner threads `parameters.ops_run_id` to dispatcher context, dispatcher threads to ToolCallRecord.parameters at write time; or (b) drop ToolCallRecord from the named join surface until Cat D F1 resolves | HIGH | Post-arc T-slot | S1799 |

**R2 sequencing note (Rigby SIGN cycle 1 Q4(a) fold):** R2 is the
lowest-cost lever to generate Cat E runtime evidence, but it should be
sequenced **after** (or explicitly in service of) the R1 D74 posture
decision to avoid producing evidence against an obsolete spine choice.

**R2 scope discipline (Rigby SIGN cycle 1 Q4(d) fold — playbook §14.5):**
xx99 scope records the recommended toggle as an **evidence-plan
decision**; do NOT implement/flip flags during arc-close per §14.5
no-implementation rule.

**R3 cross-cat remediation scope (Rigby SIGN cycle 1 Q4(b) fold):** R3
remains HIGH as an operator-surface contract breach, but remediation is
**cross-cat**: depends on Cat D correlation primitive population
(S1704 F1/F2) and Cat C PA coverage (S1703 F4). Not solvable at Cat E
alone.
| R4 | F2 schema-level correlation columns — audit whether OpsRun/OpsRunEvent should acquire `execution_id`, `trace_id`, `celery_task_id` columns (aligns with S1704 R4) | MEDIUM | Schema ADR | Post-arc |
| R5 | F6 retention policy — unified retention design across Cat A (30d exists) + Cat B (S1702 R3) + Cat D (S1704 R5) + Cat E (this R5) | MEDIUM | Post-arc | S1799 |
| R6 | F5 producer-vs-consumer contract documentation — codify OpsRunEvent-as-producer-only into topic doc + EMPLOYEE_OS_PRIMITIVES.md §1 note | MEDIUM | xx99 §7.4 doc PR | S1799 |

**R6 scope discipline (Rigby SIGN cycle 1 Q4(c) fold):** Land as a **1-2
sentence** canonical note in xx99 §7.4 (e.g., "OpsRunEvent is producer-only
at HEAD"), with deeper rationale staying in this audit doc + optional
pointer from EMPLOYEE_OS_PRIMITIVES §1. Do not inflate R6 into a large
workstream.
| R7 | F3 employee count drift regen — run `generate_platform_inventory` + refresh CLAUDE.md autoblock; add `bug_triage_specialist` to narrative anchor | MEDIUM | Anchor-update PR | S1799 §7 |
| R8 | D6 `tasks_ops.py` extraction status — audit whether extraction should be completed or the auto-gen contract retired | LOW-MEDIUM | Phase 2 | Post-arc |
| R9 | D8 admin registration for OpsRun/OpsRunEvent — analog to S1704 F8; dev-triage ergonomics | LOW | xx99 optional | S1799 |
| R10 | Ops-domain beat-wired writer decision — `run_ops_autopilot` + `post_ops_digest` remain intentionally deferred per AUDIT_FINDINGS.md §12; xx99 should confirm or unblock | LOW | Governance | S1799 |
| R11 | F4 daily diagnostics consume OpsRunEvent decision — should CTO/COO/Trend Analysis add OpsRunEvent as a signal source, or is producer-only correct? | LOW | Post-arc | Ops Autopilot arc if needed |
| R12 | F8 MissionRunner invariant regression prevention — ensure I1-I9 contract test stays green as employees expand (5th+ employee ship) | LOW | Ongoing | Employee OS |

---

## 20. Appendix

### 20.1 Files inspected

- `core/models_ops_runs.py` (117 lines, full)
- `core/employees/mission_runner.py` (1758 lines, first 150 + spot-checks around :778, :812, :1194-1250, :1500-1600)
- `core/tools/ops_run_tracker.py` (writer at :34; spot-checks around emission)
- `core/services/rigby_event_intake.py` (writer at :416, :434, :450, :508, :522)
- `core/signals/rigby_delegation_signals.py` (first 100 lines, full flag-gate verification)
- `core/services/diagnostics/cto_daily.py` (existence + beat wiring)
- `core/services/diagnostics/coo_daily.py` (existence + beat wiring)
- `core/services/scheduled_diagnostic_runner.py` (shared primitive)
- `core/celery.py:306-329` (beat schedule for CTO/COO/Trend Analysis daily)
- `core/services/td_handlers_employee.py:100, :434` (employee_tool + mission_verdict)
- `core/services/td_handlers_ops.py:160` (ops_tool)
- `core/services/td_handlers_core.py` (OpsRun import)
- `core/employees/jobs.py` (`_EMPLOYEES_BY_HANDLE` registry — 4 handles verified)
- `core/employees/mission_verdict.py:117-150` (LLMCallEvent metadata.ops_run_id write)
- `core/employees/status.py:53-508` (derive_status + evidence_for_mission)
- `core/tasks_ops.py:1-150` + line 23 (import shape)
- `core/services/ops_autopilot/` package listing (12 modules, 24000 lines total)
- `core/views_employee_api.py:49-281` (REST endpoints)
- `core/views_diagnostics.py:1511-1610, :4034-4115` (REST endpoints + Focus Cockpit)
- `core/tests/test_mission_runner.py:181-250` (MissionRunnerImportContractTests + invariant coverage)
- `core/tests/test_opsrun_mission_fields.py` (S1250 PR3 field additive-only verification)
- `docs/topics/employee-os.md` (Cat E cross-reference — F7 target)
- `docs/EMPLOYEE_OS_PRIMITIVES.md` (25-row inventory)
- `docs/PLATFORM_INVENTORY.md` (Employees autoblock — F3 drift)
- `CLAUDE.md` (Employees Detailed Breakdown row — F3 drift; Key Files rows for `jobs.py`, `mission_runner.py`, `models_ops_runs.py`)
- `docs/research/domains/observability/1700_observability_domain_scoping.md` (parent §5.E boundary)
- `docs/research/domains/observability/1704_observability_cat_d_tool_call_record_audit.md` (sibling; F1/F2/F4/F5 inheritance)
- `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md` (sibling; F4/F6 inheritance)
- `docs/research/platform/cross_domain_integration_audit.md` §14 v3 refresh (line 1977+)

### 20.2 Grep patterns used

- `OpsRun\.objects\.create|OpsRunEvent\.objects\.create|OpsRun\(|OpsRunEvent\(` — writer sites
- `from core\.models_ops_runs import|import.*OpsRun|import.*OpsRunEvent` — importer files
- `cto_daily|coo_daily|trend_analysis_daily` — diagnostic pipeline existence
- `detail__execution_id|detail\[.execution_id.\]|'execution_id':\s*str\(execution_id\)` — execution_id detail-JSON writer sites
- `BodyCoordinator|body_coordinator` in mission_runner.py — I9 boundary verification
- `RIGBY_DELEGATION_ENABLED|rigby_delegation_signals` — flag-gate verification

### 20.3 ORM verification queries (2026-07-03 HEAD `a991971a`)

- `OpsRun.objects.count()` = 36 (19 ops + 17 mission)
- `OpsRun.objects.filter(domain='mission').count()` = 17
- `OpsRun.objects.filter(mission_id__isnull=False).count()` = 17 (100% of domain='mission')
- `OpsRun.objects.exclude(run_kind='').count()` = 17 (100% of domain='mission')
- `OpsRun.objects.filter(status='failed').count()` = 1 (~2.8% fail rate)
- Mission run_kind distribution: `docs_cascade`(7) + `bug_triage_daily`(4) + `morning_brief`(4) + `platform_audit`(2) = 17 → **4 employees**
- All 17 mission rows `triggered_by='beat'`
- All 19 ops rows `triggered_by='pa_tool'` (all `run_type='smoke_test'`)
- `OpsRunEvent.objects.count()` = 224 (97 step_pass + 86 step_start + 39 info + 2 step_fail)
- `OpsRunEvent.objects.filter(detail__has_key='execution_id').count()` = **0**
- Same for `trace_id`, `task_id`, `tool_call_id`, `agent_execution_id`, `llm_call_id`, `celery_task_id`, `mission_id`, `conversation_id`, `agent_name` = **all 0**
- `OpsRunEvent.objects.filter(detail__has_key='ops_run_id').count()` = 1 (likely escalation_emitted)
- `OpsRunEvent.objects.filter(detail__has_key='deliverable_id').count()` = 7
- `_EMPLOYEES_BY_HANDLE` registry length = **4** (rigby, platform_auditor, chief_of_staff, bug_triage_specialist)
- 48 distinct OpsRunEvent labels observed
- OpsRun span: oldest 2026-06-13 → newest 2026-07-03 (~20 days); 25 in last 7d, 36 in last 30d, 36 in last 90d
- OpsRunEvent volume: 202 in last 7d, 224 in last 30d

### 20.4 Unresolved unknowns

- Whether `RIGBY_DELEGATION_ENABLED` flag is intended to flip ON at any specific milestone (Employee OS Phase 2 posture, S1268 comms sketch adoption, Employee #4 authority-level enforcement). Owed to xx99 R2 ADR.
- Whether ops-domain beat-wired writer (`run_ops_autopilot` + `post_ops_digest`) should be unblocked from AUDIT_FINDINGS.md §12 deferred list. Owed to xx99 R10.
- Whether Ops Autopilot god-services extraction (F5 secondary; not primary Cat E scope) should be prioritized. Owed to post-arc governance.
- Whether the empirical 2.8% fail rate is a representative production signal or artifact of the ~20-day window; awaiting longer observation window.

### 20.5 Conflicts between sources

- **CLAUDE.md/PLATFORM_INVENTORY vs runtime registry:** 3 vs 4 employees (F3). Runtime wins per DOC_LIFECYCLE §2c.
- **Explore Agent 5 (topic-doc reading) vs Explore Agent 6 (jobs.py registry reading):** Agent 5 said "3 employees" from doc; Agent 6 correctly flagged 4. ORM-verified.
- **Explore Agent 6 (F2 claim CTO/COO/Trend Analysis DOES NOT EXIST) vs Explore Agent 2 (found them):** Agent 6 searched Ops Autopilot module; the diagnostics live under `core/services/diagnostics/` in a separate package. Agent 2 was correct. Fold: F4 documents the positive differentiator; VC2 records the misconception.
- **Explore Agent 1 (execution_id IS threaded) vs runtime ORM (0/224 rows):** Agent 1 read the writer source at `rigby_delegation_signals.py:70` (which DOES thread execution_id when the handler runs) but did not verify the flag gate at :22-25. Runtime shows the handler is OFF by default. Fold: F1 distinguishes DESIGN-INTENT-LATENT (Cat E) from SCHEMA+RUNTIME-BROKEN (S1704 F1). VC3 records the correction.

### 20.6 Rigby SIGN cycle 1 fold notes

**Status: SIGN-WITH-EDITS landed pre-commit.** SIGN pin
`pa-09c46ee3a0d34069` minted at session open (D48 22nd arm start);
routing per S1600/S1700/S1701/S1702/S1703/S1704 wrapper-hard-code
precedent landed on arc pin `pa-e7fbacc996b34b44` via
`tools/pa_local.sh:128`. Fresh SIGN pin retired at S1705 close per
playbook §16. Rigby SIGN cycle 1 single-batch 4-question pattern
per S1701-S1704 precedent + D48 preemptive stability-probe gate 22nd
arm HOLDING CLEAN (**17-consecutive-fully-clean-arms sub-pattern
S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+
S1700+S1701+S1702+S1703+S1704+S1705 CONFIRMED**).

**Per-question SIGN cycle 1 verdicts:**

- **Q1 coverage-completeness:** **SIGN-clean at Medium-High**. All
  4 sub-parts (writer sites, readers/consumers, producer-vs-consumer
  resolution via F5, sibling event models overlap) confirmed complete.
  No folds required.
- **Q2 drift-severity calibration:** **SIGN-with-edits at Medium**.
  D1+D2 MEDIUM correct; D3 LOW correct (scope misinterpretation, not
  drift); D7 INFORMATIONAL correct (intentional flag state per module
  docstring); **D4 HIGH held with justification fold landed**.
- **Q3 F9 D74 axis correctness:** **SIGN-with-edits at Medium-High**.
  Q3(a) LATENT-VIABLE-BUT-FLAG-GATED distinct axis cell held; Q3(b)
  nuance fold landed (Cat E flag flip does yield partial usefulness
  via execution_id detail-JSON thread, unblocks Cat E → Cat C axis
  cell even if Cat D remains broken); Q3(c) SIGN-clean; Q3(d)
  canonical verdict fold landed (producer-only at HEAD, could evolve
  post-arc).
- **Q4 R1-R12 follow-on ranking + xx99 scope discipline:**
  **SIGN-with-edits at Medium**. R1 top slot held; R2 sequencing +
  scope-discipline folds landed (evidence-plan not execution during
  xx99); R3 cross-cat remediation fold landed; R6 1-2 sentence xx99
  §7.4 scope-discipline fold landed.

**Fold-edits applied to audit doc pre-commit:**

- **F1 (Q2(b) fold)** — §14 drift matrix: added D4 severity
  justification block explaining HIGH is held because
  `evidence_for_mission` is a Chris-facing operator surface, upstream
  root cause (Cat D F1 + Cat D dispatcher-side threading) does not
  demote the operator-visible breach.
- **F2 (Q3(b) fold)** — §1.1 F9: added Rigby-SIGN-cycle-1-Q3(b)-nuance
  block correcting "resolves nothing" to "resolves nothing for the
  ToolCallRecord join, but unlocks the execution_id spine cell in the
  Cat E → Cat C axis" — more precise Option B posture framing.
- **F3 (Q3(d) fold)** — §1.1 F5: appended canonical verdict block
  ("producer-only at HEAD; could evolve to 'producer + consumer' only
  if future work introduces cross-table correlation IDs + explicit
  aggregation pipeline — post-arc T-slot").
- **F4 (Q4(a) fold)** — §19 R2 area: added sequencing note ("R2 is
  the lowest-cost lever to generate Cat E runtime evidence, but should
  be sequenced after or in service of R1 D74 posture decision to
  avoid producing evidence against an obsolete spine choice").
- **F5 (Q4(b) fold)** — §19 R3 area: added cross-cat remediation
  scope note ("R3 remains HIGH as operator-surface contract breach,
  but remediation is cross-cat: depends on Cat D correlation primitive
  population + Cat C PA coverage — not solvable at Cat E alone").
- **F6 (Q4(c) fold)** — §19 R6 area: added scope-discipline note
  ("Land as 1-2 sentence canonical note in xx99 §7.4 — 'OpsRunEvent
  is producer-only at HEAD' — deeper rationale stays in this audit
  doc + optional EMPLOYEE_OS_PRIMITIVES §1 pointer").
- **F7 (Q4(d) fold)** — §19 R2 area: added scope-discipline block
  per playbook §14.5 no-implementation rule ("xx99 scope records
  recommended toggle as evidence-plan decision; do NOT implement/flip
  flags during arc-close").

**No must-fix outstanding; no severity flips at commit-time. All 7
folds landed pre-commit.**

---

**End of audit doc — S1705 SIGN cycle 1 SIGN-with-edits landed
pre-commit. Next: retire fresh SIGN pin + update INDEX + OPEN_ARCS +
handoff.**
