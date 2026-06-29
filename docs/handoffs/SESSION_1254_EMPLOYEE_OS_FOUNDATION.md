---
title: "Session 1254 — Employee OS Foundation"
status: active
session: 1254
generated: 2026-06-29
companion_docs:
  - EMPLOYEE_OS_PRIMITIVES.md
  - SESSION_1252_AI_EMPLOYEE_V0_PR1_PR2_LANDED.md
  - PLATFORM_INVENTORY.md
owner: chris (framing + architectural conclusion) + claude (PR mechanics + verification)
---

# Session 1254 — Employee OS Foundation

**Mode:** Build + extract. Open-PR cadence with admin-merge given the
Anthropic billing CI gap.
**Framing:** "The platform already contains the majority of the
Employee Operating System. Documentation Manager is proof #1, not the
architecture."

> **Numbering note.** Today's commit subjects are tagged
> `session-1253` (matches the start-here entry-point heading that
> primed this session) but Chris's session-close handoff numbers it
> `1254`. The handoff number wins for forward-looking refs;
> commit/branch history is immutable and uses `session-1253`. Future
> sessions referencing this work should treat the two tags as
> equivalent.

---

## §0 TL;DR

- **5 PRs shipped and merged today.** Documentation Manager went from
  "registration-broken first beat fire" at session open to
  "registered + read API + shift-report DM + generalized comms +
  canonical Employee OS primitives doc" at session close.
- **All architectural decisions routed through Rigby before code
  landed** on the four substantive PRs (#2734, #2735, #2736). PR #2733
  was a same-day hotfix dictated by the morning verification.
- **Net production change**: Rigby's Documentation Manager now
  registers at worker boot, posts a shift-report DM into Chris's
  `/inbox` after every terminal mission, exposes a read-only
  `employee_tool action=status` + `evidence_for_mission`, and the
  underlying comms helper is generic enough to host a second employee
  without a refactor.
- **Architectural conclusion (Chris):** the largest remaining gap is
  no longer communications — it is extracting the reusable employee
  lifecycle (PR-B: MissionRunner) and proving it with Employee #2.

---

## §1 PRs shipped

| PR | Type | Scope | Merge SHA | Tests added |
|---|---|---|---|---|
| [#2733](https://github.com/clwest/donkey-betz-platform/pull/2733) | fix | Register `rigby_documentation_manager_daily` for worker boot (`app.conf.imports`) | `475bbe5f` | 2 |
| [#2734](https://github.com/clwest/donkey-betz-platform/pull/2734) | feat | `employee_tool action=status` + `evidence_for_mission` (read-only) | `7e5209b5` | 27 |
| [#2735](https://github.com/clwest/donkey-betz-platform/pull/2735) | feat | Documentation Manager shift-report DM into the persistent `/inbox` thread | `771023df` | 22 |
| [#2736](https://github.com/clwest/donkey-betz-platform/pull/2736) | feat | Generalize shift-report helper + `EMPLOYEE_OS_PRIMITIVES.md` | `4b941a68` | 8 |

All four admin-merged (Anthropic billing CI gap pattern, S1249+).

### PR #2733 — Celery registration hotfix

**Discovered live at Priority 0 verification.** The Monday 06:30 MDT
first beat fire dispatched correctly but the default worker rejected
the task message:

```
ERROR 2026-06-29 06:30:00,098 consumer ... Received unregistered task
  of type 'rigby_documentation_manager_daily'.
KeyError: 'rigby_documentation_manager_daily'
```

Root cause: PR #2730 added `core/tasks_documentation_manager.py` (a
non-standard `tasks_*.py` module name) but never added it to
`app.conf.imports` in `core/celery.py`. S1252 cutover verification
used the management command path (in-process import) and never
exercised the Celery worker dispatch path. PeriodicTask
`last_run_at` advanced anyway, so beat-side observability looked
green while the worker silently dropped the task.

Fix: add `'core.tasks_documentation_manager'` to both the
`app.conf.imports` tuple AND the `_eager_import_session1115_modules`
hook. New `DocsManagerTaskRegistrationTests` in
`core/tests/test_celery_queue_parity.py` lock in both mechanisms —
module-in-imports AND task-name-in-registry — so any future refactor
that drops either side fails CI loudly.

### PR #2734 — `employee_tool action=status` + `evidence_for_mission`

Read-only daily-status surface + per-mission evidence join. Built per
Rigby's SIGN-WITH-EDITS amendments:

- `evidence_for_mission` is a separate action; `status` returns a
  `requested_mission_pointer` when called with `mission_id` rather
  than inlining evidence
- `verbose=false` default on evidence → `error_tail_preview` (last
  30 lines) + `has_full_error_tail` flag; `verbose=true` → full tail
- Deferred verdicts neutral for trust math:
  `trust_ratio = certified / (certified + rejected)`
- `trust_status='under_review'` fires at 3 rejections in **last 7
  days regardless of caller-requested window** (fixed trip-wire)
- Stale-pin evidence exposed on `latest_mission.pa_post` (`conversation_id`,
  `settings_primary_pin`, `pin_matches_settings`) — surfaces the
  S1252 cutover scenario live
- No new model, no migration, trust ratio derived per-call

### PR #2735 — Documentation Manager shift-report DM

First Employee Communications PR. After every terminal docs_manager
mission, Rigby posts exactly one `DirectMessage` into the persistent
inbox thread "Rigby — Documentation Manager", visible to Chris in
the existing `/inbox` web UI.

- Thread lookup keyed by `metadata.employee + metadata.job` (subject
  typo-proof)
- Idempotent on `(thread, mission_id)`
- Bounded metadata (9 keys, never `error_tail`)
- Additive to existing escalation Deliverable + PA chat post
- `messaging_tool` schema trimmed to read-only enum
  `[list_threads, get_thread, unread_count]`; defense-in-depth
  handler guard refuses `send_message` unless
  `settings.MESSAGING_TOOL_ALLOW_SEND=True`

### PR #2736 — Generalize shift-report comms + Employee OS primitives

Refactored `post_shift_report` from Rigby/docs_manager-hardcoded to
`post_shift_report(*, employee, job, mission, body_formatter=None,
extra_metadata_keys=(), thread_subject=None, sender_type='system')`.

Docs-specific config moved into `core/employees/comms_docs_manager.py`
with a thin `post_docs_manager_shift_report(mission)` wrapper that
calls the generic helper with the docs config baked in. Docs cascade
behavior preserved exactly — same thread, same DM body, same
metadata shape, same idempotency. All 22 PR 4 tests pass verbatim
against the wrapper.

New `docs/EMPLOYEE_OS_PRIMITIVES.md` codifies:

- 25-row canonical primitives table (AIEmployee + JobContract +
  OpsRun(domain='mission') + emit_mission_verdict + Deliverable +
  MessageThread + HumanAttentionItem + employee_tool +
  messaging_tool + LLMCallEvent + ToolCallRecord, etc.)
- 12-row anti-duplication matrix naming each "do not build" model
  with its canonical primitive substitute
- 9-stage standard employee lifecycle with file-ownership map
- 7 explicit warnings citing the sessions that surfaced them
- Quick-start for adding a new employee

---

## §2 Verification trail

### Live tool exercises (Rigby PA chat path)

| Surface | Result |
|---|---|
| `employee_tool action=status employee=rigby job=docs_manager window=7d` | `latest_mission.mission_id=02480a34-…`, `triggered_by=beat`, `certified` 0.95, trust_ratio 0.6667 from 2/(2+1), trust_status `healthy`, current_streak 1 certified |
| `employee_tool action=evidence_for_mission 02480a34-…` | 11 events, no escalation block, llm_calls=[], tool_calls=[], `error_tail` absent from summary |
| `employee_tool action=evidence_for_mission eab1accc-…` | 9 events, escalation deliverable `0af7bfe5-…`, deliverable_event with `source=DocsManager` + `ctx.ops_run_id` + `ctx.error_signature`, pa_post `pk=1565 conversation_id=pa-3901b70e61934df7` (stale-pin surface proved live) |
| `messaging_tool action=list_threads` | 5 threads; shift-report thread at top with `unread_count=2` |
| `messaging_tool action=get_thread d24e5e7a-…` | Both DMs returned, `sender_type='rigby'` on both, bodies match templates exactly |
| `messaging_tool action=unread_count` | 2 |
| `GET /api/inbox/threads/` (HTTP — what the web Inbox polls) | Shift-report thread `d24e5e7a-…` at top with `unread_count=2`, `last_message.sender='rigby'` |

### Post-merge handler invocations

| Invocation | Result |
|---|---|
| `post_docs_manager_shift_report(02480a34-…)` (existing DM) | `created=False, skipped_reason='duplicate'`, same `message_id` returned, DM count unchanged at 1 |
| `post_shift_report(employee=_FakeEmployee, job='pra_verify_job', mission=transient)` | `created=True`, new non-docs thread `67683d69-…`, subject `'PR-A Verify Bot — pra_verify_job'`, sender_type `'system'`, body `"Mission … reached terminal verdict 'certified' (wall 1.2s)."` — zero docs-cascade vocabulary leak, metadata exactly `BASE_METADATA_KEYS` |

### Test inventory

| Suite | Count | Result |
|---|---|---|
| docs-manager comms (`test_employees_comms`) | 22 | green |
| generic comms (`test_employees_comms_generic`) | 8 | green |
| employee tool describe / run_now / status | 47 | green |
| mission_verdict | 15 | green |
| documentation_manager routine + escalation | 53 | green |
| employees_jobs | 37 | green |
| docs-manager Celery registration | 2 | green |
| **Total across the employee suite** | **190** | **190 / 190 in 3.9–4.6s on real PostgreSQL** |

### Production state at session close

| Item | Value |
|---|---|
| `PeriodicTask(rigby_documentation_manager_daily).enabled` | `True` |
| Schedule | `30 6 * * 1,2,3,4,5 America/Denver` (Mon–Fri 06:30 local) |
| Default worker | PID 11924 — task registered, `RIGBY_PRIMARY_PA_PIN=pa-c7263e7061a0` in env |
| PA worker | PID 15879 — read-only `messaging_tool` enum loaded |
| Inbox thread | `d24e5e7a-e77e-4251-93e3-4b4fac3f5d9b` "Rigby — Documentation Manager" |
| Existing DMs in thread | 2 (passed `02480a34-…`, rejected `eab1accc-…`) |
| Next scheduled beat fire | Tue 2026-06-30 06:30 MDT = 12:30 UTC — first untouched beat-driven run |

---

## §3 Architectural conclusion (verbatim from Chris)

> This session confirmed an important architectural finding: **the
> platform already contains the majority of the Employee Operating
> System. Documentation Manager is proof #1, not the architecture.**

> Most required primitives already existed:

- OpsRun
- OpsRunEvent
- Mission verdicts
- Trust derivation
- HumanAttentionItem
- DirectMessage
- MessageThread
- GovernanceState
- Heartbeat / BodyCoordinator
- Push infrastructure
- Inbox infrastructure
- Employee tooling

> The largest remaining architectural gap is no longer
> communications. It is extracting the reusable employee lifecycle.

### Current Employee OS maturity

**Completed:**

- Generic employee communications
- Generic employee evidence
- Generic employee status
- Generic mission verdicts
- Generic trust calculation
- Generic employee tool surface
- Canonical Employee OS documentation

**Remaining architectural work:**

1. **MissionRunner extraction** (PR-B)
2. **Employee #2 proof implementation**
3. **Authority enforcement**
4. **Notification channel abstraction**

Everything after those items is primarily feature work.

---

## §4 Recommended next architectural milestone — PR-B (MissionRunner)

**Goal:** extract the reusable employee lifecycle from
`tasks_documentation_manager.py`.

**MissionRunner should own:**

- Mission creation (`OpsRun(domain='mission', run_kind=<job>)`)
- OpsRun lifecycle (status transitions, finished_at)
- Step event emission (`OpsRunEvent` per step)
- Summary accumulation (the running `summary_acc` dict)
- Verdict emission (`emit_mission_verdict` call site)
- Idempotency (one mission per day per (employee, job))
- Escalation hooks (the `_handle_failure_escalation` shape)
- Shift report dispatch (`post_shift_report` call site)

**MissionRunner should NOT own:**

- LLM execution
- Step semantics
- Business logic

Those remain job-specific. The job module provides the **steps** —
MissionRunner orchestrates them and writes the audit trail.

**Concrete shape (working sketch — Rigby sign-off required before code):**

```python
class MissionRunner:
    def __init__(self, *, employee, job_contract, shift_report_fn):
        ...

    def run(self, *, step_fns: Sequence[Callable]) -> MissionRunResult:
        """
        Execute steps in order, recording OpsRunEvent boundaries.
        On step failure, halt + emit rejected verdict + call shift_report_fn.
        On all-steps-pass, emit certified verdict + call shift_report_fn.
        Returns a normalized result; never raises.
        """
```

The Documentation Manager becomes the first MissionRunner
implementation. Employee #2 becomes the second — and that's the
proof the extraction is correct.

**Hard rules carrying over from EMPLOYEE_OS_PRIMITIVES.md §4:**

- No new `MissionRun` model. `OpsRun(domain='mission')` is the
  MissionRun.
- No new `EmployeeAuditLog`. Reuse OpsRunEvent + DeliverableEvent +
  LLMCallEvent + ToolCallRecord.
- No new PA tool. `employee_tool` already covers status / evidence /
  run_now / describe.
- Idempotency stays in MissionRunner — not in each job module.

---

## §5 Employee #2

**Do not invent a new employee architecture.** Reuse the Employee OS
primitives from §1 of `docs/EMPLOYEE_OS_PRIMITIVES.md`.

**Candidate employees:**

- StockAuditCoordinator
- COOAgent

**Goal:** prove that a second employee can reuse the same lifecycle
with only:

1. A new `AIEmployee` + `JobContract` in `core/employees/jobs.py`
2. A new `core/tasks_<job>.py` module (registered in
   `app.conf.imports` per the S1253 hotfix lesson)
3. Job-specific step functions
4. (Optionally) a thin `core/employees/comms_<job>.py` for a tuned
   body template — if the generic default is fine, skip this

If implementing Employee #2 requires *any* new model, PA tool, queue,
or admin UI, **stop and re-read EMPLOYEE_OS_PRIMITIVES.md §2 + §4**.
That's the canary.

---

## §6 Architectural guardrails (carrying forward)

Per `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 + §4, **do not introduce new
models for**:

- `EmployeeMessage`
- `ApprovalQueue`
- `TrustScore`
- `MissionRun`
- `EmployeeNotification`
- `EmployeeHistory`
- `EmployeeStatus`

Reuse the canonical primitives.

---

## §7 Open items / carryover into Session 1255

| Item | Severity | Source |
|---|---|---|
| PR-B MissionRunner extraction | architectural | §4 above |
| Employee #2 implementation | architectural | §5 above |
| Authority enforcement (JobContract.authority is policy, not enforced today) | medium | EMPLOYEE_OS_PRIMITIVES.md §1 row 2 |
| Notification channel abstraction (push + WebSocket "DM arrived" event) | low | PR #2735 §"What's NOT in this PR" |
| Mobile messaging screen | low | PR-4 discovery report |
| `RIGBY.primary_chat_id` contract constant still pointing at the stale `pa-3901b70e61934df7` (env override active; cosmetic) | low | S1252 carryover |
| `auto-archive-stale-deliverables` interaction with new `publish_candidate` escalation deliverables (window may eat them prematurely) | low | S1252 carryover |
| Pre-existing failing test `test_every_route_pattern_matches_a_registered_task` (orphan `content.*` route) | low | confirmed pre-PR; out of scope of S1253 |
| `Deliverable.create` defaults-to-completed upstream fix (PR 2 works around; root cause outside docs-manager scope) | low | S1252 carryover |

---

## §8 Session retrospective

**What worked:**

- The Priority 0 verification catching the registration bug before
  any downstream work. Cost: ~30 min hotfix. Counterfactual cost
  (catching it Tuesday after a silent failure): much more.
- The Rigby-in-the-loop SIGN-WITH-EDITS pattern. Three substantive
  PRs (#2734, #2735, #2736) all reviewed and amended before code
  landed; zero post-merge corrections required.
- Honest reporting of the cached-mission case during PR #2735
  post-merge verification: `run_now` short-circuited via the daily
  idempotency gate and the shift-report helper was bypassed — that
  *real behavior* surfaced cleanly rather than being hidden by a
  test-only fixture.
- The PR-A refactor preserved all 22 existing tests verbatim by
  flipping imports only — no test-body changes, low review surface.

**What hurt:**

- S1252 cutover declared the docs cascade "verified" but had only
  exercised the management-command path. The Celery worker path was
  never tested. Cost: one extra session-open hotfix PR. Lesson: the
  worker dispatch path must be in every cutover checklist for new
  `@shared_task` jobs.
- One initial test-suite write hit Pyright warnings on Django
  dynamic types — pre-existing pattern, but distracting. Filed as
  ignorable noise.

**Net hours:** ~7 hours from session open through close. 5 PRs
shipped, 4 admin-merged. 59 new tests across the suite. The
Documentation Manager went from "broken first beat fire" to
"foundation of an Employee Operating System."

---

*End of Session 1254.*
