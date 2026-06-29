---
session: 1258
status: closed
date: 2026-06-29
arc: Employee OS — Chief of Staff Morning Brief beat migration (PR 3.3 closes the docs_manager + platform_audit + morning_brief Employee OS trilogy through-the-runner)
prs_merged: [2747]
prs_open: []
companions:
  - docs/handoffs/SESSION_1257_EMPLOYEE_OS_PR_3_1_PR_3_2_CHIEF_OF_STAFF_LANDED.md
  - docs/MORNING_BRIEF_SPEC.md
deliverables:
  - cc4c0641-c361-4c19-a1db-a6ccfa92b281 (discovery, Rigby SIGN)
  - 96cb6656-26d9-485b-ace7-94d5978a0482 (verification, Rigby SIGN — clean after §13.5 closure)
---

# Session 1258 — Employee OS: PR 3.3 (Chief of Staff Morning Brief beat migration)

## TL;DR

The daily 07:00 Denver Morning Brief now executes through the MissionRunner-backed Chief of Staff job. Beat row `generate-morning-brief-daily` retains its name + cadence + queue; its `task` field flipped from the legacy `core.tasks.generate_morning_brief_daily` to `chief_of_staff_morning_brief_run`. Legacy task body deleted (151 lines). Discovery → implementation → verification → merge → post-merge local verification all clean in one session. **All three Employee OS jobs now run through MissionRunner end-to-end.**

## What shipped

**PR #2747 (admin-merged at 2026-06-29T23:08:25Z, merge SHA `eef22ed5`):**
- `core/celery.py` — beat schedule entry `generate-morning-brief-daily` task field flipped to `chief_of_staff_morning_brief_run` + tombstone comment for the migration.
- `core/tasks.py` — legacy `generate_morning_brief_daily` `@shared_task` body deleted (151 lines: original Session 1233 Sub-step C dispatch + Session 1234 D1 fail-loud raise + D2 telemetry extraction).
- `core/migrations/0373_session_1258_flip_morning_brief_beat_task.py` — **NEW** Django migration that flips the existing PeriodicTask row's `task` field BEFORE `sync_celery_beat` runs in the Railway release sequence. Critical because `sync_celery_beat`'s orphan handler does `pt.save()` without `update_fields` on a stale Python instance, which would otherwise revert the flip + disable the row. Verified locally: post-migration `sync_celery_beat` dry-run shows the row as `✓ in_sync`, `0 to_create`, `0 to_update`.
- `core/employees/jobs.py` — `MORNING_BRIEF_JOB.responsibilities` + `.triggers` rewritten past-tense; file:line citation updated from the deleted `core/tasks.py:5805-5807` to the live `core/celery.py:463-481`.
- `core/tasks_chief_of_staff.py` — module docstring + fail-loud comment updated to remove "legacy" framing now that this IS the production beat target.
- `core/tests/test_morning_brief_sub_step_c.py` — deleted `GenerateMorningBriefDailyTaskTests` (5 tests) + `MorningBriefBeatTaskTelemetryTests` (2 tests); inverted `MorningBriefBeatScheduleRegistrationTests` to assert the new task name + crontab/queue/expires preserved; added 3 regression tests (`test_legacy_generate_morning_brief_daily_symbol_removed`, `test_periodic_task_row_targets_chief_of_staff_runner`, `test_beat_row_targets_chief_of_staff_runner`).
- `core/tests/test_chief_of_staff_routine.py` — renamed `NoBeatScheduleTests` → `PostMigrationBeatScheduleTests`; inverted assertions to the PR 3.3 ground truth (`PeriodicTask` row task field == `chief_of_staff_morning_brief_run`; source-of-truth `app.conf.beat_schedule` entry matches).
- `scripts/verify/verify_morning_brief_2026_06_27.py` — `check_beat_fire` accepts both legacy + new task names via `Q()` so the script works for historical 06-27 verification AND post-migration fires.

Diff summary: **8 files, +327 / -516 lines.**

## Hard constraints satisfied

- ✅ **NO MissionRunner files modified** — `core/employees/mission_runner.py` untouched in diff. Single `+MissionRunner.` reference in the diff is a docstring sentence end.
- ✅ **NO `WorkflowOrchestrationAgent` changes** — workflow internals (the 8-step morning_brief workflow) unchanged.
- ✅ **NO `JobContract` field changes** — only `MORNING_BRIEF_JOB.responsibilities` + `.triggers` doc strings updated.
- ✅ **Production cadence preserved** — `crontab(0 7 * * *)` Denver, queue `default`, expires 3600, row name `generate-morning-brief-daily`. `total_run_count=5` preserved on the row.
- ✅ **MissionRunner production caller count remains 3** — AST scan in `test_chief_of_staff_routine.ThreeProductionCallersTests` + `test_employees_chief_of_staff.ProductionCallerCountUnchangedTests` both pass.

## The critical bug the discovery missed

The discovery deliverable §7 analyzed `sync_celery_beat` and concluded the Railway release would flip the row cleanly via the `to_create → get_or_create(name) → if not created → update task field` path. **That analysis was wrong.**

`sync_celery_beat`'s **orphan handler** (lines 137-140 in `core/management/commands/sync_celery_beat.py`) does `pt.save()` with no `update_fields` on a Python instance whose `pt.task` still holds the OLD value (because the mutation in `create_task` happens on a SEPARATE Python instance returned by `get_or_create`). Django's default `.save()` writes ALL fields back to the DB, which would silently REVERT the task field AND set `enabled=False`. Beat would stop firing.

**Caught during local implementation verification:** I ran `sync_celery_beat` dry-run after editing celery.py and noticed the row showed up in BOTH the "to_create" section AND the "orphan" section. Pre-existing discovery analysis assumed the orphan check's `pt.task` would reflect the mutated value because Python doesn't auto-snapshot via dict iteration. Wrong assumption — the orphan check uses the pt from `db_tasks.values()` which is the Python instance from the initial `PeriodicTask.objects.all()` query, while `create_task` issues a fresh `get_or_create` query that returns a different Python instance. The two instances diverge once `create_task` mutates its copy.

**Fix:** new Django migration `0373_session_1258_flip_morning_brief_beat_task.py` that flips the row task field BEFORE `sync_celery_beat` runs in the Procfile release sequence (`migrate` runs first). By the time `sync_celery_beat` reads the DB, the row is already in-sync — it skips both the `to_create` branch (task path matches celery.py) AND the orphan check (task path now in `celery_task_paths`). Verified locally: post-migration `sync_celery_beat` dry-run shows `0 to_create`, `0 to_update`, and the row appears in the `✓ in_sync` section.

**Lesson worth saving:** when a discovery analyzes a multi-step process that mutates state across Python instances vs DB state, the only safe verification is to actually run the sequence end-to-end on a real DB. Code reading + reasoning isn't sufficient.

## Process flow

| Step | Status | Notes |
|---|---|---|
| Discovery deliverable | ✅ SIGNED | `cc4c0641-c361-4c19-a1db-a6ccfa92b281` — 13,208 chars, 8 sections + §9 SIGN-WITH-EDITS closure |
| Implementation | ✅ committed `ce1e6932` | 8 files, applied all 8 changes from the discovery PR scope |
| Local test gauntlet | ✅ 100/100 focused | `test_morning_brief_sub_step_c` + `test_chief_of_staff_routine` + `test_employees_chief_of_staff` + `test_local_safe_beat_filter` (2 conditional skips on fresh DB) |
| Broader test sweep | ✅ 224/225 | 1 PRE-EXISTING `test_every_route_pattern_matches_a_registered_task` failure for orphan `content.*` route — S1257 carryover, severity=low, unrelated |
| PR opened | ✅ #2747 | https://github.com/clwest/donkey-betz-platform/pull/2747 |
| Verification deliverable | ✅ SIGN clean | `96cb6656-26d9-485b-ace7-94d5978a0482` — 14,323 chars, 13 sections, all 14 verification requirements green-lit (12 by tool, 2 N/A pending first fire) |
| Admin merge | ✅ `eef22ed5` | 2026-06-29T23:08:25Z |
| Post-merge worker restart | ✅ | `pkill -9 -f celery; rm -f .celery*.pid; make celery` — 5 workers + beat back up |
| Post-merge probe 2 (direct CLI) | ✅ | `.venv/bin/celery -A core inspect registered` → `chief_of_staff_morning_brief_run` registered in 5/5 worker processes; legacy task absent |
| Post-merge probe 3-4 (employee_tool) | ✅ via Rigby | `describe` returns updated past-tense triggers + correct file:line citations; `status` returns clean shape (missions.total=0 pre-first-fire) |
| Post-merge probe 5 (evidence_for_mission) | N/A | No mission yet; tool requires explicit mission_id (gap not in PR 3.3 scope) |
| Live first-fire verification | ⏳ TUE 2026-06-30 07:00 MDT | next session priority |

## Verification handshake — 14 requirements

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | Production behavior identical | ✅ | Test coverage + post-migration `sync_celery_beat` in-sync |
| 2 | Beat schedule unchanged (cadence + queue) | ✅ | Probe 1 — `cron(0 7 * * *)`, `queue=default`, `expires=3600` preserved |
| 3 | Morning Brief Deliverable unchanged | ✅ | `SuccessPathTests` coverage; workflow internals untouched |
| 4 | Workspace unchanged | ✅ | `workspace_name='Donkey Betz'`, `_resolve_chris_user` preserved |
| 5 | OpsRun created on fire | ✅ | `test_8_run_creates_ops_run_with_morning_brief_kind` |
| 6 | OpsRunEvent timeline created | ✅ | `test_employees_chief_of_staff` coverage |
| 7 | Mission summary populated (scalar-only) | ✅ | PR 3.2 SIGN-WITH-EDITS lock #2 preserved |
| 8 | Mission verdict emitted | ✅ | `mission_verdict` tests |
| 9 | No unexpected escalation | ✅ | Escalation only on `result.ok=False` |
| 10 | `employee_tool describe` works | ✅ | Probe 3 (post-worker-restart) |
| 11 | `employee_tool status` works | ✅ | Probe 4 (post-worker-restart) |
| 12 | `evidence_for_mission` works | N/A | No mission yet; tool requires `mission_id` |
| 13 | MissionRunner production caller count = 3 | ✅ | `ThreeProductionCallersTests` + `ProductionCallerCountUnchangedTests` green |
| 14 | No MissionRunner/workflow/JobContract changes | ✅ | Diff confirmed; only docstring updates to JobContract |

## Rollback playbook

PR 3.3 deletes the legacy task body. **DB-only rollback (hand-flip the `PeriodicTask` row back) is INCOMPLETE** — the row would point at a task name that doesn't exist in the deployed code, and beat fires would error with `Received unregistered task of type 'core.tasks.generate_morning_brief_daily'`.

**Emergency rollback: `git revert <merge_sha> && git push`** — the revert restores the legacy task body AND the migration's `reverse_code` flips the row back to the legacy task name. Both happen in the same release. Estimated impact: at most one missed 07:00 fire while the revert deploys.

## Out-of-scope tool surface gaps (follow-up tickets)

Rigby's verification flagged two PA tool-surface UX gaps that surfaced during PR 3.3 probing. Neither is in PR 3.3 scope; both are independent backlog items:

1. **No `celery_inspect_tool` in PA surface.** Probe 2 (worker task registry inspection) had to be run via direct CLI by Claude. Adding `celery_inspect_tool action=registered filter=…` would close the gap for future Rigby-led verifications.
2. **`employee_tool evidence_for_mission` requires explicit `mission_id`** — no default-to-latest. With no mission yet for CoS, the probe returns `Missing required arg 'mission_id'` rather than an empty result shape. A default-to-latest-mission-for-this-employee+job would be more useful.

## Honest framings worth keeping

- **Discovery analyses that depend on Python identity semantics across DB queries need end-to-end real-DB verification** before the analysis is treated as authoritative. The §7 sync_celery_beat read-the-code analysis was internally consistent but wrong on Python instance behavior.
- **Tool-surface gaps surfaced during verification probes ARE useful product feedback** — they get filed as follow-up tickets rather than swept under "BLOCKED-by-tooling". The two flagged here came from running real verification work, not from speculative audit.
- **Worker `sys.modules` staleness is a routine post-merge hygiene step** — but it ALSO masquerades as registration drift on the first probe attempt. Pattern recognition next time: if a known-registered employee/task/handler is missing from the PA tool's "known X" list right after a PR merge, restart the worker BEFORE investigating a registration bug.

## What's next (Session 1259 entry points)

See `00-START-NEXT-SESSION.md`. Top items:

1. **Live first-fire verification: TUE 2026-06-30 07:00 MDT = 13:00 UTC** — the first beat fire of the post-migration `chief_of_staff_morning_brief_run`. Verify via `CeleryTaskEvent` + `OpsRun(domain='mission', run_kind='morning_brief')` + brief `Deliverable` in `Morning Brief` workspace + mission verdict. If clean, the morning_brief arc closes.
2. **Earlier-same-day: TUE 2026-06-30 06:30 MDT = 12:30 UTC docs-manager first untouched fire** — carried over from S1257. If clean, docs-manager arc also closes.
3. **Carryover backlog** — `claude_code_tool` task receipt/post-back/sandbox UX fix (S1257 incident); JobContract authority enforcement; PA tool surface gaps named above; etc.

**Do not begin Employee #4 work** until both first-fire watches close cleanly.
