---
session: 1261
status: closed
date: 2026-06-30
arc: Employee OS Foundation Hardening — delete per-job confidence/dedupe/workspace duplication that was already covered by MissionRunnerConfig defaults; centralize workspace name; corrected the S1260 audit's wrong-fix recommendation
prs_merged: [2750]
prs_open: []
companions:
  - docs/handoffs/SESSION_1259_FIRST_FIRE_VERIFICATION.md
  - docs/handoffs/SESSION_1260_EMPLOYEE_OS_PHASE_2_PLANNING_AND_DISCOVERABILITY.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
---

# Session 1261 — Employee OS Foundation Hardening

## TL;DR

The S1260 Architecture Planning doc proposed expanding `JobContract` with 4 new fields to absorb hardcoded per-employee constants. **Independent verification this session showed that was wrong.** The constants already exist as `MissionRunnerConfig` field defaults at `mission_runner.py:255-258` + `:497-502`. Three jobs declared module-level constants that exactly matched the defaults, then passed them as explicit kwargs that exactly matched the defaults again. Pure dead duplication. PR #2750 deletes the redundancy without expanding `JobContract` or touching `MissionRunner`. Discovery → Phase 1 SIGN → implementation → tests → Phase 4 SIGN → admin-merge all clean in one session.

## What shipped — PR #2750 (admin-merged 2026-06-30, merge SHA `918bbbe5`)

**Deleted across all 3 jobs (4 constants + 5 kwargs each):**

```python
# In docs_cascade.py, platform_audit.py, morning_brief.py — DELETED:
CONFIDENCE_SUCCESS_FULL = 0.95         # matches mission_runner.DEFAULT_CONFIDENCE_SUCCESS_FULL
CONFIDENCE_SUCCESS_DEGRADED = 0.6      # matches DEFAULT
CONFIDENCE_FAILURE = 0.0               # matches DEFAULT
DEDUPE_WINDOW_HOURS = 24               # matches DEFAULT
DONKEY_BETZ_WORKSPACE_NAME = "Donkey Betz"   # → centralized
# Plus 5 matching kwargs in build_*_runner() → MissionRunnerConfig(...)
```

**Added in `core/employees/jobs.py`:**

```python
EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME: str = "Donkey Betz"
```

Single canonical, Employee OS-scoped per Rigby's Phase 1 guardrail. Imported by all 3 job modules.

**Tests updated (3 files):** new imports point at `DEFAULT_*` from `mission_runner` + `EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME` from `jobs`. Literal-value AND named-reference assertions retained — drift in either surface fails loud.

| File | Change |
|---|---|
| `core/employees/jobs.py` | +16 (new constant + module docstring) |
| `core/jobs/docs_cascade.py` | -20 / +14 (net -6) |
| `core/jobs/morning_brief.py` | -20 / +14 (net -6) |
| `core/jobs/platform_audit.py` | -22 / +16 (net -6) |
| `core/tests/test_docs_manager_migration.py` | +44 / -10 |
| `core/tests/test_chief_of_staff_routine.py` | +14 / -2 |
| `core/tests/test_platform_audit_routine.py` | +14 / -2 |

**Diff summary:** 7 files, +131 / -77 (positive total because of added test docstrings + new test assertions for the new workspace-via-spec contract; the 4 SOURCE files net -20 LOC of duplication).

## Why the `workspace_name` kwarg was safe to remove

Each job's `escalation_deliverable_spec_factory` already sets `EscalationDeliverableSpec.workspace_name = "Donkey Betz"`, and `MissionRunner._resolve_workspace_for_spec` (`mission_runner.py:1408`) gives the spec precedence over the config-level legacy fallback. **The fallback path is unreachable when a spec factory is wired.** Verified via grep + code trace + tests that assert `runner.config.workspace_name is None` AND `spec.workspace_name == "Donkey Betz"`.

## Hard constraints satisfied

- ✅ **NO MissionRunner file modified** — `core/employees/mission_runner.py` untouched
- ✅ **NO `JobContract` field changes** — only a new module-level constant added in `core/employees/jobs.py`
- ✅ **Production cadence + behavior preserved** — runtime probe confirms `confidence=0.95`, `dedupe=24`, escalation workspace targeting via spec unchanged
- ✅ **No new architectural primitives** — no new dataclass, no new base class, no new registry
- ✅ **Tests preserved** — same behavior assertions, updated canonical-source imports

## Phase flow

| Step | Status | Notes |
|---|---|---|
| Phase 1 discovery | ✅ Rigby SIGN (with 3 guardrails — all verified) | grep + code trace confirmed `MissionRunnerConfig` already has defaults |
| Phase 2 implementation | ✅ committed `b9fa545e` | 7 files, applied all changes |
| Phase 3 targeted tests | ✅ 304/304 pass | test_docs_manager_migration + test_mission_runner + test_platform_audit_routine + test_chief_of_staff_routine + test_employees_chief_of_staff + test_employees_platform_auditor + test_documentation_manager_routine + test_documentation_manager_escalation |
| Phase 3 broader sweep | ✅ Employee OS-specific queue parity tests pass; 1 unrelated pre-existing `content.*` orphan-route failure (not in any touched file) | |
| Phase 3 runtime probe | ✅ all 3 factories build clean | `confidence=0.95 dedupe=24 workspace_name=None` (correctly using runner defaults; spec wins for workspace targeting) |
| PR opened | ✅ [#2750](https://github.com/clwest/donkey-betz-platform/pull/2750) | |
| Phase 4 verification | ✅ Rigby SIGN clean, no edits | "tomorrow's beats will produce the same OpsRun/OpsRunEvent/verdict/deliverable shapes they produced today" |
| Admin merge | ✅ `918bbbe5` | 2026-06-30 |

## The verifier-loop pattern caught the wrong audit fix

S1260 audit was the work of 5 parallel Explore agents + Rigby's runtime evidence. The proposed JobContract expansion was directionally reasonable but missed that `MissionRunnerConfig` already had the defaults wired. Verifying independently THIS session (grep + cross-file trace + reading the runner config) corrected it before any code was written. **Saved a useless contract expansion.** The S1260 doc remains a useful reference for Phase 2 priorities — only the P3 specific recommendation was wrong.

## Tech debt status after this session

| Item | Status |
|---|---|
| Critical: hardcoded confidence dup | ✅ fixed |
| Important: workspace name hardcoded | ✅ fixed (centralized) |
| Important: dedupe window hardcoded | ✅ fixed (uses runner default) |
| Important: user resolution patterns inconsistent | ⏸️ deferred (1/3 jobs uses helper; N=1 doesn't justify generalization) |
| Better before Employee #5: `_persist_to_summary` 2/3 dup | ⏸️ deferred (abstraction cost ≈ duplication cost at N=2) |
| Pre-existing: `content.*` orphan route in `CELERY_TASK_ROUTES` | ⏸️ separate hygiene PR |
| Pre-existing: `sync_celery_beat` orphan-handler revert trap | ⏸️ documented in migration `0373`, code fix deferred |

## Observation worth keeping

**`claude_code_tool` recursive dispatch hits the S1257 receipts gap.** When Rigby dispatched a `claude_code_tool` to verify my work this session, the task_id was returned but the post-back wouldn't have arrived. Worked around by sending her the receipts directly. Reinforces the S1257 P1 priority — task receipt UX gap is real and surfaces during Rigby-led verification flows.

## What's next (Session 1262 entry point)

Foundation is stronger. **Employee #4 is ready when Chris is.** Per the S1260 Architecture Planning doc Stop #1, the recommended foundation block (P1 docs discoverability + P2 topic file + P3 centralize constants) is now landed. The next stopping point before Employee #5 would be:
- P4 MissionRunner `authority_check_fn` preflight hook (warn-mode)
- P5 Read-only `/api/employees/` + `/api/missions/` HTTP API
- Investigation of the 2 pre-existing SLO breaches (`agent_timeout_rate` 12× over; `celery_task_success_rate` marginally under)

None of these are blockers for adding Employee #4 itself.
