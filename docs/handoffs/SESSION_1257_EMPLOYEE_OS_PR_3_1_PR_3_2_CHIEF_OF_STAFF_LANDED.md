---
session: 1257
status: closed
date: 2026-06-29
arc: Employee OS — Chief of Staff (Employee #3) registration + Morning Brief task runner
prs_merged: [2744, 2745]
prs_open: []
companions:
  - docs/handoffs/SESSION_1254_EMPLOYEE_OS_FOUNDATION.md
  - docs/MORNING_BRIEF_SPEC.md
deliverables:
  - 2983377c-08e3-44e6-aeef-cfcf742ae4cd (discovery, Rigby SIGN-WITH-EDITS)
  - a4fe1a58-a5bd-453e-a1ed-8e5099edf59a (verification request — superseded by local re-verification)
  - 5523e4ca-5ad8-4455-827a-7c395463a997 (local verification, Rigby SIGN)
---

# Session 1257 — Employee OS: PR 3.1 + PR 3.2 (Chief of Staff Morning Brief)

## TL;DR

Shipped the third AI employee, Chief of Staff, end-to-end through MissionRunner:

- **PR #2744 (PR 3.1)** — registers Chief of Staff as Employee #3 + `MORNING_BRIEF_JOB` contract (registry-only; no task runner).
- **PR #2745 (PR 3.2)** — Chief of Staff Morning Brief task runner via MissionRunner using the wrap-as-single-step pattern. **MissionRunner production caller count: 2 → 3.**

The existing morning_brief workflow (`WorkflowOrchestrationAgent.execute(workflow='morning_brief')`) is unchanged. PR 3.2 wraps it in one `step_brief_workflow` MissionRunner step that:
- writes scalar-only summary fields (no envelope persistence)
- derives `brief_chars` postflight via single ORM read of the brief `Deliverable.content`
- re-raises `RuntimeError` on `result.ok=False` (CoS-specific fail-loud, differs from Platform Auditor's wrapper)

Surfaced an Employee OS UX/infrastructure gap during Rigby's verification handshake: `claude_code_tool` dispatch returns a "task_id" but if the dispatched engineer task lacks repo access and/or fails to post back, nobody sees it. Filed as future work in `00-START-NEXT-SESSION.md`.

## What landed

### PR #2744 — `feat(session-1257-pr-3-1): register Chief of Staff as Employee #3`

- Merged: `2026-06-29T19:39:33Z` (commit `dc534924`)
- Adds `CHIEF_OF_STAFF` AIEmployee + `MORNING_BRIEF_JOB` JobContract in `core/employees/jobs.py:646-945`.
- Registry-only: no task runner, no beat schedule, no Celery task.
- Authority profile: 6 OBSERVE (read-only lane data), 5 EXECUTE (rotation slot resolve / synthesis / Deliverable persist / mission certify), 2 RECOMMEND, **13 PROHIBITED** (Chris's explicit directive list — no emails, no external messages, no schedule changes, no decision approvals, no business actions, no public posts, no financial record edits, no user/account creation, no platform settings changes, no PR opening, no scope decisions).
- 41 tests across 7 test classes including `ChiefOfStaffAuthorityBoundaryTests` (12 Chris-directive prohibitions explicitly verified).

### PR #2745 — `feat(session-1257-pr-3-2): Chief of Staff Morning Brief task runner via MissionRunner`

- Merged: `2026-06-29T22:03:58Z` (commit `0c8c66a4`)
- 6 files, 2011 insertions / 30 deletions.
- **NEW** `core/jobs/morning_brief.py` (524 LOC) — `build_chief_of_staff_runner()` + `step_brief_workflow` wrapper + scalar extraction (`_extract_scalars`) + postflight `brief_chars` derivation (`_compute_brief_chars` — single ORM read) + CoS-flavored escalation body formatter + `EscalationDeliverableSpec(workspace_name='Donkey Betz')`.
- **NEW** `core/tasks_chief_of_staff.py` (113 LOC) — `@shared_task chief_of_staff_morning_brief_run`; re-raises `RuntimeError` on `result.ok=False` (fail-loud).
- **NEW** `core/tests/test_chief_of_staff_routine.py` (1228 LOC, 31 tests across 12 TestCase classes) — covers all 16 PR 3.2 contract points.
- `core/celery.py` — adds `core.tasks_chief_of_staff` to `app.conf.imports` + the `_eager_import_session1115_modules` set (S1253 hotfix lesson).
- `core/services/td_handlers_employee.py` — adds `('chief_of_staff', 'morning_brief')` to `_RUN_NOW_TASKS` registry; size now exactly 3.
- `core/tests/test_employees_chief_of_staff.py` — flips the PR 3.1 guardrail tests in `ProductionCallerCountUnchangedTests` to the new ground truth (caller count = 3; factory + task exist).

### Architectural decision: wrap-as-single-step

The morning_brief workflow's 8 internal steps run unchanged inside one MissionRunner step (`step_brief_workflow`). From MissionRunner's perspective: atomic unit, either passed (workflow `success=True`) or failed. From the workflow's perspective: nothing changed.

Failure granularity is preserved via `StepResult.extra['inner_failed_step']` which surfaces the workflow's own failed-step name into the OpsRunEvent.detail JSON, the escalation Deliverable body, and the mission summary. Error-signature hash still varies by inner-step error tail content even though the outer step name is constant — dedupe semantics are intact.

This is the same approach used by docs cascade (where `_run_call_command_step` wraps a multi-stage management command) and Platform Auditor (where each agent tool method becomes one step). Morning Brief follows.

## Rigby SIGN-WITH-EDITS locks (both applied)

From discovery deliverable `2983377c-…`:

1. **Lock #1 — no workflow internal touches.** `brief_chars` derived postflight via single ORM read of `Deliverable.content` length, NOT via a workflow return-dict addition. `core/services/workflow_orchestration_agent.py` is NOT in the PR 3.2 diff. Asserted by `NoWorkflowInternalsModifiedTests` (12 load-bearing workflow internal symbols still present).
2. **Lock #2 — scalar-only `OpsRun.summary`.** `_extract_scalars` returns 9 scalar fields; the full workflow envelope is never persisted to `mission.summary`. Asserted by `test_12_summary_does_not_include_full_workflow_envelope` (forbids 12 envelope keys + asserts no dict-of-dicts).

Both locks confirmed satisfied with file:line evidence in local verification deliverable `5523e4ca-…`. Rigby SIGN'd.

## Production caller count: 2 → 3

AST scan of `core/**/*.py` (excluding tests + the runner itself):
- `core/jobs/docs_cascade.py` + `core/tasks_documentation_manager.py` → **docs_manager**
- `core/jobs/platform_audit.py` + `core/tasks_platform_audit.py` → **platform_audit**
- `core/jobs/morning_brief.py` + `core/tasks_chief_of_staff.py` → **morning_brief** *(NEW)*

6 production caller files in 3 jobs. Asserted by `ThreeProductionCallersTests` (in `test_chief_of_staff_routine.py`) and the mirror in `test_employees_chief_of_staff.ProductionCallerCountUnchangedTests`.

## Test evidence

- **PR #2744 (PR 3.1):** 241/241 focused gauntlet pass.
- **PR #2745 (PR 3.2):** 336/336 gauntlet pass in 33.131s across:
  - `test_chief_of_staff_routine` — 31 tests, all 16 contract points
  - `test_employees_chief_of_staff` — PR 3.1 guardrails flipped to PR 3.2 ground truth
  - `test_employees_jobs` — registry shape (3 employees + 3 jobs)
  - `test_platform_audit_routine`, `test_documentation_manager_routine`, `test_documentation_manager_escalation` — no regression
  - `test_employee_tool_describe`, `test_employee_tool_status`, `test_employee_tool_run_now` — no regression
  - `test_mission_runner` — no public-contract changes
- **Post-merge live-check on `main`:** `chief_of_staff_morning_brief_run` registered in `app.tasks`; `employee_tool action=describe employee=chief_of_staff` returns `ok=True handle=chief_of_staff job_count=1 jobs[0].key=morning_brief run_kind=morning_brief`.

## Out of scope (deferred to PR 3.3 or later)

- **Beat schedule flip.** The legacy `generate-morning-brief-daily` beat row in `core/celery.py:473-477` continues to fire `core.tasks.generate_morning_brief_daily` at 07:00 Denver. PR 3.3 flips the `task` field to `chief_of_staff_morning_brief_run` and removes the legacy task module.
- **Legacy task removal.** `core.tasks.generate_morning_brief_daily` remains live; both tasks coexist until PR 3.3.
- **Beat queue parity audit.** PR 3.3 must verify Procfile + Makefile parity for the post-flip beat row to avoid the queue-routes silent-failure trap (`feedback_procfile_makefile_queue_parity.md`).

## Discovery / verification flow

1. **Discovery deliverable** `2983377c-…` — 12-section, 391-line read-only discovery written by Claude. Rigby returned **SIGN-WITH-EDITS** with two locks (#1 + #2). Both edits incorporated before any code was written.
2. **PR 3.2 implementation** — wrap-as-single-step, scalar-only summary, postflight `brief_chars`, fail-loud Celery wrapper. 336/336 tests pass.
3. **Verification request deliverable** `a4fe1a58-…` — Claude's PR 3.2 evidence + 9-point checklist asks for Rigby.
4. **Rigby's `claude_code_tool` dispatch** — task `068ee853-…` ran on `code_jobs` queue. Completed SUCCESS in 40.7s but the engineer ran in a sandboxed worker without repo access (`fatal: not a git repository`, file-not-found, "no matches found" on every search). Engineer marked all 8 checks FAIL from sandbox blindness, NOT from PR defects. Plus the result was never posted back to PA conversation `pa-e8999a1793f04e23` (`_post_to_conversation` silently no-op'd — likely because `conversation_id=None` threaded across the queue boundary).
5. **Local re-verification** — Claude executed all 9 checks locally with file:line evidence. All 8 checks PASS. Both locks confirmed satisfied. Local verification deliverable `5523e4ca-…` persisted.
6. **Rigby SIGN** — single-word verdict on `5523e4ca-…`: "SIGN" with all 5 PASS confirmations.
7. **Merge** — PR #2745 admin-squashed at `2026-06-29T22:03:58Z` (commit `0c8c66a4`). Post-merge gauntlet 240/240 PASS. Live-check task name + `employee_tool` describe on `main` confirmed.

## Employee OS UX gap surfaced — future fix

The `claude_code_tool` → `claude_code_engineer_task` → `code_jobs` queue chain has three connected gaps:

1. **No `AgentExecution` row written** by `claude_code_engineer_task` — so Rigby's `schedule_followup` (which keys off `AgentExecution.celery_task_id`) can't bind to it, and the UI has nothing to surface.
2. **Silent post-back failure.** `_post_to_conversation` skips silently when `conversation_id` is None or the queue boundary drops it. There's no fail-loud signal back to Rigby or the dispatcher.
3. **No task receipt in Chat UI.** Rigby's "dispatched, task_id=..." ack looks identical to "in flight" and "stuck." Chris can't distinguish queued / running / completed / failed / posted-back without ORM digging.

Plus the related sandboxing issue: the `code_jobs` worker that ran the engineer task lacks repo access (`fatal: not a git repository`), making any repo-level verification impossible from that surface. Either expose the repo to the worker OR refuse the dispatch with a clear error.

Saved as memory `project_employee_os_ux_gap_task_receipts.md` and as the headline future-fix entry in `00-START-NEXT-SESSION.md`.

## Live counts (post-merge)

| Component | Count | Notes |
|---|---|---|
| AI employees | 3 | Rigby (PA / Docs Manager), Platform Auditor, Chief of Staff |
| Job contracts | 3 | docs_manager, platform_audit, morning_brief |
| MissionRunner production callers | 3 | docs_manager + platform_audit + morning_brief (was 2 pre-S1257) |
| `_RUN_NOW_TASKS` registry size | 3 | (rigby, docs_manager) + (platform_auditor, platform_audit) + (chief_of_staff, morning_brief) |
| Mission run_kinds | 3 | docs_cascade, platform_audit, morning_brief |
| Beat schedule for new task | 0 | PR 3.3 scope |

## Next session entry point

**PR 3.3 — Morning Brief beat migration.** Pure task-name flip on the existing `generate-morning-brief-daily` `PeriodicTask` row, from `core.tasks.generate_morning_brief_daily` to `chief_of_staff_morning_brief_run`. Remove the legacy task module from `core/tasks.py:5788-5938`. Verify Procfile + Makefile queue parity. No other scope.

The discovery work for PR 3.3 is already inside the discovery deliverable `2983377c-…` § 9 (Beat schedule) and § 10 (Required code movement / PR 3.3 split) — no separate discovery PR needed.

## Memories saved this session

- `project_employee_os_ux_gap_task_receipts.md` — the claude_code_tool task receipt/post-back UX gap.

---

**Session 1257 closed. Two PRs merged. No follow-up open.**
