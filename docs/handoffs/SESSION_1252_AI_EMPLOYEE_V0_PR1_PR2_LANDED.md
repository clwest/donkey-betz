---
title: "Session 1252 — AI Employee v0 (PR 1 + PR 2 + cutover landed)"
status: active
session: 1252
generated: 2026-06-28
companion_docs:
  - SESSION_1251_CAPABILITY_AUDIT.md
  - PLATFORM_INVENTORY.md
---

# Session 1252 — AI Employee v0 (PR 1 + PR 2 + cutover landed)

**Mode:** Build, with a Rigby-in-the-loop review at each gate.
**Framing:** "Build a framework for teaching AI systems how to earn
operational responsibility instead of just responding to prompts."
Rigby is employee #1; Documentation Manager is her first job.

---

## §0 TL;DR

- **3 PRs shipped and merged** (#2729, #2730, #2731). Session 1251 audit said
  "stop building, start using"; Session 1252 took that literally — built the
  *smallest possible* employee/job/verdict framework around Phase B of the
  audit (docs cascade owner) and put Rigby in charge of executing it.
- **All architectural decisions routed through Rigby before code landed**:
  v0 contract reviewed and SIGNed with 6 required edits (applied verbatim);
  PR 2 operational requirements answered Q1–Q9 with real tool inspection;
  audit-trail amendment routed back after SIGN-WITH-EDITS and re-SIGNed.
- **Production cutover complete**. `PeriodicTask` for the Documentation
  Manager daily routine is now `enabled=True`. Default worker has
  `RIGBY_PRIMARY_PA_PIN=pa-c7263e7061a0` baked in via `make celery`.
- **Net production change this session**: a recurring 06:30 Mon-Fri job
  Rigby owns end-to-end, with full evidence trail (`OpsRun + OpsRunEvent +
  LLMCallEvent + ToolCallRecord + Deliverable + DeliverableEvent`) and
  auditable escalation surface. First beat fire: **2026-06-29 06:30
  America/Denver** (Monday).

---

## §1 PRs shipped

| PR | Type | Scope | Tests | Merge SHA |
|---|---|---|---|---|
| [#2729](https://github.com/clwest/donkey-betz-platform/pull/2729) | feat | AI Employee v0 contract + verdict surface | 65 | `1fe0bb0f` |
| [#2730](https://github.com/clwest/donkey-betz-platform/pull/2730) | feat | Documentation Manager daily routine + run_now + audit trail | +56 new + 10 audit | `1b5b65c0` |
| [#2731](https://github.com/clwest/donkey-betz-platform/pull/2731) | chore | Makefile env var for active PA pin | — | `67ab1e73` |

All three admin-merged given the Anthropic billing CI gap (matches the
S1249-S1250 pattern).

### PR #2729 — AI Employee v0 contract

**Shipped:**
- `core/employees/jobs.py` — frozen `AIEmployee` + `JobContract` dataclasses,
  `RIGBY` employee constant, `DOCUMENTATION_MANAGER` job constant.
- `core/employees/mission_verdict.py` — `emit_mission_verdict()` helper
  (pure-Python, idempotent per `(mission_id, verdict)`, terminal-status
  preserving).
- `employee_tool action=describe` — read-only PA tool surface for the
  contract.
- `mission_verdict` PA tool — Rigby-only certify / reject / defer (v0 gate
  is a channel gate: caller `user.username` must equal
  `RIGBY.runs_as_username = 'chris'`).

**Rigby applied 6 required contract edits before signing:**
1. Best-effort sync wording (not magical-fix responsibility)
2. 12-key required summary stats schema
3. drift_count definition allows null + degraded_evidence
4. Step 4 timeout precondition (600s warning / 1800s hard fail)
5. Escalation visibility guarantee (publish_candidate + canonical
   status path flip + pinned PA post)
6. Failure-signature dedupe rule (24h, OpsRun-first lookup)

**Honest call-out kept on the table:** `RIGBY.primary_chat_id` hardcoded
to the retired S1247 pin (`pa-3901b70e61934df7`). Surfaced as a contract
drift and explicitly deferred to PR 2 (settings-resolved env override
landed via #2731).

### PR #2730 — Documentation Manager daily routine

**Shipped:**
- `core/tasks_documentation_manager.py` — `@shared_task` cascade runner.
  Subprocess hard-timeout for step 4 (1800s), `threading.Timer` warning
  at 600s, count probes (Document + DocumentEmbedding + docs_indexed_count
  derived from `docs/_index.json` length), drift observation via
  `verify_doc_claims --only-drift --format json` with regex fallback,
  verdict emission via PR 1's helper.
- Escalation flow with 24h dedupe (OpsRun.summary lookup matching
  `failed_step + error_signature`), append-vs-create branching.
- Error signature normalization strips ISO timestamps, bare HH:MM:SS,
  epoch floats, UUIDs.
- `employee_tool action=run_now` for on-demand dispatch (90s wait cap
  on `wait_for_result=true`).
- `core/management/commands/run_docs_manager_daily.py` with `--dry-run`.
- Migration `0372` seeds `PeriodicTask(name='rigby_documentation_manager_daily',
  enabled=False)` (Mon-Fri 06:30 America/Denver).
- `settings.RIGBY_PRIMARY_PA_PIN` env-resolved active pin with contract
  constant fallback.
- 56 new tests in 3 files; 181/181 green after audit amendment.

**Two structural decisions made mid-build:**

1. **`dispatcher.execute_sync` swap.** Original plan was to flip the
   escalation Deliverable's status via the canonical
   `deliverable_tool.set_status` dispatcher path. Real test failure:
   `execute_sync` opens a new asyncio event loop whose cleanup closes
   the Django DB connection mid-task. Fix: mirror the same contract
   via direct ORM mutation with the `_transition_context` stash —
   same observable behavior, no dispatcher round-trip. Documented in
   the function docstring.

2. **Explicit `status='completed'` on create.** Direct ORM
   `Deliverable(...).save()` lands at the model default `'ready'`, not
   `'completed'` (the bug only manifests through the PA dispatcher's
   `deliverable_tool.create` path). Without forcing the initial state
   to `completed`, the subsequent `completed→ready` flip wasn't a
   transition — and no audit row fired. The fix: explicitly create at
   `completed` (matches what the broken dispatcher path would produce)
   and flip to `ready` via the audited transition. Defends against
   future model default changes and gives Rigby the real
   completed→ready audit row she required.

### PR #2730 audit-trail amendment (Rigby SIGN-WITH-EDITS resolution)

Rigby returned SIGN-WITH-EDITS requiring 5 audit guarantees:

1. Deliverable status deterministically `ready`
2. Auditable DeliverableEvent equivalent per transition
3. Audit record includes previous_status, new_status, source='DocsManager',
   ops_run_id, error_signature
4. Audit independent of `Deliverable.status` field
5. Tests proving all of the above + that silent-completed cannot occur

Amendment landed in commit `0915e7bd`:
- Extended `core/signals/deliverable_status_signals.py` whitelist to
  accept `ops_run_id` + `error_signature` (generic — benefits any
  future caller).
- `_force_deliverable_ready()` now requires both as keyword args; raises
  ValueError on empty/null (prevents silent unqueryable audit rows).
- Standardized actor source to `"DocsManager"` (Rigby's preferred
  identifier, indexed on `DeliverableEvent.source`).
- 10 new audit-trail tests in `EscalationAuditTrailTests` (including
  one that tampers with `Deliverable.status` post-escalation and proves
  the audit row is unaffected).

Rigby re-signed clean: *"This satisfies my SIGN-WITH-EDITS conditions.
... I'm comfortable signing and proceeding to merge PR #2730."*

### PR #2731 — Cutover Makefile env var

Adds `RIGBY_PRIMARY_PA_PIN=pa-c7263e7061a0` to the `make celery`
default-worker block so the active pin resolves without per-shell env
exports. Default worker only — `rigby_documentation_manager_daily`
lands on the default queue.

---

## §2 Production state at session close

### Live config

- `PeriodicTask.enabled` for `rigby_documentation_manager_daily`: **True**
- Schedule: `30 6 * * 1,2,3,4,5 America/Denver` (Mon-Fri 06:30 local)
- Next scheduled fire: **2026-06-29 06:30 America/Denver** (Monday)
- Default worker PID 96619 (started 19:48 with env vars confirmed via
  `ps eww`):
  - `PA_USE_FUNCTION_CALLING=true`
  - `RIGBY_PRIMARY_PA_PIN=pa-c7263e7061a0`
- Beat scheduler PID 78073 — alive, dispatching due tasks

### Manual verification performed before flip

| Step | Result |
|---|---|
| `--dry-run` | plan output clean, zero DB writes |
| Real cascade run | passed in 44.4s, mission `39cc4083-…`, certified verdict, all 12 summary keys present |
| Success-path ORM verify | OpsRun domain/run_kind/status correct, full 11-event timeline, zero escalation Deliverables, zero PA posts |
| Failure injection (renamed `build_docs_index.py`) | escalation Deliverable `0af7bfe5-…` final status='ready', `DeliverableEvent(status_transition, source='DocsManager')` with ctx.ops_run_id + ctx.error_signature matching the OpsRun row, pinned PA post at ChatConversation row 1565 |
| File restore | OK |
| Mutated `started_at` restored | OK |

### Test inventory after PR 2

- **181/181 PR 2 + PR 1 + S1250 regression tests green** in 2.9s on real
  PostgreSQL.
- New test files this session: `test_employees_jobs.py` (37),
  `test_employee_tool_describe.py` (13), `test_mission_verdict.py` (15),
  `test_documentation_manager_routine.py` (26),
  `test_documentation_manager_escalation.py` (27),
  `test_employee_tool_run_now.py` (13). Total: 131 new tests.

### Memory rule status

- `feedback_docs_pipeline_4_step_cascade.md` — **not updated yet**.
  Per the PR 1 plan, the memory rule update is the last commit in PR 3
  (after `employee_tool action=status` ships as the daily-read surface).
  Until PR 3 lands, the existing manual rule stays live as a fallback if
  the daily routine ever fails silently.

---

## §3 Architectural decisions worth carrying forward

1. **Frozen-dataclass config beats new DB models for v0 employee
   abstractions.** No migrations, no fixtures, no admin UI surface,
   no end-user CRUD pressure. PR-reviewable, git-versioned. Promote to
   a model only when (a) a second employee exists, (b) non-engineers
   need to edit contracts, or (c) cross-workspace rollups become
   impossible without joins. None of those are true today.

2. **"Plan-as-signed" workflow shape.** Pattern: discovery → 9-question
   operational sign-off → implementation plan (also signed) → build →
   amendment loop if needed → re-sign → merge → cutover. Worked clean
   across PR 1 (1 sign cycle) and PR 2 (2 sign cycles: pre-build plan
   + post-build audit amendment).

3. **Direct ORM > dispatcher round-trip for in-task ops.** The
   `dispatcher.execute_sync` failure mode (asyncio loop cleanup closes
   the Django DB connection mid-task) is sharp enough that any future
   in-task PA-tool-equivalent operation should mirror the handler
   contract via direct ORM, not call back through the dispatcher.

4. **Channel gate vs speaker gate (v0 auth honesty).** The PA
   dispatcher doesn't propagate `agent_name` into handlers — so
   "Rigby-only" tools can only verify caller `user_id` resolves to the
   user Rigby acts as. Documented honestly in module docstrings and
   surfaced in rejection responses. Promote to a true speaker gate
   only when a second AI employee actually needs the distinction.

5. **Explicit `completed` create + audited flip beats trusting model
   defaults.** Defends against future default changes AND gives the
   transition a real audit row to attach to.

---

## §4 What to watch Monday morning

When the first beat fires at 06:30 local Monday (2026-06-29):

1. **Check `OpsRun.objects.filter(run_kind='docs_cascade').latest('started_at')`**
   exists, status=`passed`, `triggered_by='beat'`, full 12 summary keys.
2. **No escalation Deliverable created.** If one IS created, read
   `error_tail` and `failed_step` to triage — the daily routine itself
   is the canary; a Monday-morning escalation is *expected behavior on
   real failure*, not a Documentation Manager bug.
3. **PA post (if escalation):** should land in `pa-c7263e7061a0` (active
   pin via env), not the stale contract constant. If it lands in
   `pa-3901b70e61934df7`, the worker env wasn't loaded — check
   `ps eww <default_worker_pid>`.
4. **Wall time should be ~30-90s on incremental.** First Monday could
   be longer if many docs were edited over the weekend.

---

## §5 What NOT to do tomorrow

- **Don't start PR 3 reflexively.** PR 3 is `employee_tool action=status`
  (the daily-read surface + trust ratio derivation). Wait for Monday's
  first beat to produce a real MissionRun before designing the read
  surface — actual data shapes the API better than theoretical specs.
- **Don't touch `RIGBY.primary_chat_id` in the contract code.** The
  env-override pattern (`settings.RIGBY_PRIMARY_PA_PIN`) closes the
  drift. If you want to update the contract constant to match the
  current active pin (`pa-c7263e7061a0`), that's a separate
  housekeeping PR — not blocking anything.
- **Don't restart all celery workers.** The default worker has the env;
  the others don't need it (`rigby_documentation_manager_daily` doesn't
  route to them). A full restart wouldn't hurt but adds nothing.
- **Don't flip the Session 1250 flags** (`RIGBY_EVENT_INTAKE_ENABLED`
  et al.) yet. The audit's "stop building toward a richer pipeline"
  rule still applies. Documentation Manager is the first job; let it
  burn a week before exercising the intake/queue/delegation stack.
- **Don't `rm -rf` `docs/INDEX.md` if it shows up uncommitted.** It's
  cascade output — regen-on-demand via `build_docs_index`, never
  hand-edited per `feedback_docs_never_delete`.

---

## §6 PR 3 framing (when ready)

Per PR 1 plan §6:

**Scope:** new action `employee_tool action=status employee=rigby
[job=docs_manager] [window=7d|30d|90d]`. Read-only. Returns:

```
{
  job: "Documentation Manager",
  window_days: 7,
  missions_total: N,
  missions_certified: N,
  missions_failed: N,
  trust_ratio: 0.0-1.0,
  trust_status: "healthy" | "under_review",
  last_mission_at: <iso>,
  last_escalation_at: <iso|null>,
  current_streak: N,
  avg_wall_time_ms: N,
  last_drift_count: N,
}
```

Plus `evidence_for_mission(mission_id)` read helper joining the 5
evidence tables (`OpsRun + OpsRunEvent + LLMCallEvent + ToolCallRecord
+ DeliverableEvent`).

**Wait until:** at least one real beat-driven MissionRun exists. The
shape of the response gets sharper once Chris has actually read the
first day's data.

**Acceptance criterion fragments to remember:**
- Trust ratio is **derived on read, never persisted** (per the
  architecture review's "no new model" discipline).
- `trust_status='under_review'` fires at 3 failures in 7d.
- Single integration test against 100 seeded MissionRuns; response
  under 500ms.
- After PR 3 ships, update `feedback_docs_pipeline_4_step_cascade.md`
  memory rule to point at the new daily check.

---

## §7 Open items

| Item | Owner | Notes |
|---|---|---|
| Monday 06:30 first-fire watch | Chris | Read `employee_tool action=describe` or query OpsRun directly until PR 3 lands |
| `RIGBY.primary_chat_id` contract constant update | TBD | Housekeeping; non-blocking thanks to env override |
| PR 3 specification refinement | Next session | Wait for ≥1 real beat-driven MissionRun first |
| `verify_doc_claims --format json` quality | Deferred | Rigby's contract explicitly allows null + degraded_evidence as the fallback path |
| `Deliverable.create` default-completed upstream fix | Deferred | PR 2 works around; upstream fix is outside Documentation Manager scope |
| `auto-archive-stale-deliverables` interaction with Docs Manager escalations | Future audit | New `publish_candidate` deliverables — check the auto-archive window doesn't eat them prematurely |

---

## §8 Session retrospective

**What worked:**
- The Rigby-in-the-loop sign-off pattern caught a real audit gap (the
  `Deliverable.status` field is not a trustworthy substitute for a
  DeliverableEvent transition row).
- Verifying the PA dispatcher mid-task footgun (`execute_sync` →
  asyncio loop → connection close) during PR 2 build, not after merge.
- The architecture review (this session's discovery phase) prevented a
  Capability/Department/Authority model layer that would have shipped
  dormant code and broken the "stop building, start using" discipline.

**What hurt:**
- One initial test-suite write got 23/26 failures from a single Celery
  signal handler that closes DB connections post-task. Burned ~15
  minutes diagnosing. Patch is now well-documented in the test
  helper's docstring; future Celery-task test files can copy it.
- Mid-build had to invert the "model default is `ready`" assumption.
  Explicit `status='completed'` create is the right move but had to
  be discovered through a failing audit test, not designed up front.

**Net hours:** ~6.5 from architecture review through cutover. 3 PRs
admin-merged. 131 new tests. One employee. One job. Live in
production with a Monday 06:30 first fire.

---

*Rigby holds the job. Beat owns the schedule. Chris reads the
evidence Monday morning.*
