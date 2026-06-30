---
session: 1266
status: closed
date: 2026-06-30
arc: Read-only Employee OS readiness audit + Employee #4 (Bug Triage Specialist) discovery package with Rigby SIGN-clean. No code shipped this session — discovery only per Chris's directive. Next session resumes directly with implementation from this signed package.
prs_merged: []
prs_open: []
companions:
  - docs/handoffs/SESSION_1265_THREE_PR_HYGIENE_AND_API.md
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
deliverables: []
---

# Session 1266 — Employee #4 (Bug Triage Specialist) Discovery + Audit

## TL;DR

Two-phase research-only session per Chris's S1266 directive: (1) comprehensive pre-Employee-#4 readiness audit
across 10 areas, returning **GO** for Employee #4 with **Bug Triage Specialist** as the recommended candidate;
(2) full discovery package for Bug Triage with Rigby **SIGN-clean** after three blocking edits + two
non-blocking recommendations accepted. Implementation held for fresh session per Chris's S1265 close
directive.

No code shipped. No PRs opened. Working tree clean at S1266 close. S1267 begins directly with
implementation from the signed discovery package below.

## Phase 1 — Pre-Employee-#4 Readiness Audit (read-only)

Full evidence-cited report delivered inline this session. Verdict: **GO**.

### Key findings

| Area | Verdict | Evidence |
|---|---|---|
| MissionRunner stability | STABLE since S1264 close | Single commit on `core/employees/mission_runner.py` since 2026-06-30 00:00: just the S1264 ship itself (`0fa1b577`). |
| Employee OS primitives discoverable | YES | CLAUDE.md rows 95, 123-125, 146, 187. `docs/EMPLOYEE_OS_PRIMITIVES.md` 19,873 bytes, §5 has 10-step quick-start. |
| Anti-duplication held | YES | AGENT_MAP entries matching Employee OS handles: `[]`. Only one `MissionRunner` class in `core/employees/mission_runner.py:583`. |
| Three production employees healthy | YES | All registered/runnable/JobContract-driven/MissionRunner-orchestrated. Verified via `employee_status_tool` (window=7d): Rigby (4 missions/3-1-0/trust 0.75), Platform Auditor (2/2-0-0/trust 1.0), Chief of Staff (1/1-0-0/trust 1.0). |
| HTTP API production-verified | YES | S1265 PR #2760 5/5 endpoints returning 200 for staff, 403 for non-staff (post-merge probe). |
| 24h operational health | GREEN | 8/8 SLOs clean. queue_pressure GREEN. memory OK. failure_signatures 0. p0_summary 0 open. |
| 30d operational health | 4/8 BREACHES | celery_success 0.998813 (53 fails); agent_timeout 0.024014 (28/1166); pa_tool_success 0.8614 (565/4076, 534 of which are `intelligence_tool` — NOT Employee OS related); content_publish 0/5. **All bounded historical; 24h is green.** |
| claude_code_tool / receipts | HEALTHY | Canonical `Agent.objects.filter(name__in=['claude-code', 'ClaudeCode']).count() == 1`. 7 `AgentExecution` rows in last 7d, ALL status=completed, output_data populated, 0 failed, 0 orphaned. |
| Authority warn-mode evidence | LIVE but N=1 | Single `OpsRunEvent` with label=`authority_contract_observed` (from S1265 Step A test dispatch at 17:06). Exactly-once contract honored. Accumulation begins with each beat fire starting tomorrow 06:30 Denver (Rigby). |
| Active failure loops | NONE | `cockpit_tool.recent_failures` returns 30 historical `process_core_spider_data` 6/27 cluster rows; no fresh failures since 2026-06-27 23:15. S1265 PR #2758 guard prevents recur. |

### Non-blocking gaps surfaced (NOT prereqs for Employee #4)

| # | Finding | Source |
|---|---|---|
| F1 | `PeriodicTask` row missing for `platform_auditor_run` — Platform Auditor has no scheduled cadence | `PeriodicTask.objects.filter(task__icontains='audit').count() == 0` |
| F2 | `triggered_by` field hardcoded to `'beat'` regardless of dispatch path | `core/employees/mission_runner.py:775` |
| F3 | `pa_tool_success_rate` 30d 0.86 breach concentrated in `intelligence_tool` (534/565 = 95%) | `td_handlers_ops.py:593` + `ToolCallRecord` query |
| F4 | 9 `autopilot_tool drift_scan` warnings still open (S1265 P3 carryover) | Rigby `autopilot_tool.drift_scan` |
| F5 | Authority warn-mode evidence is N=1; needs ≥3 events per employee for cross-mission baseline | `OpsRunEvent.objects.filter(label='authority_contract_observed').count() == 1` |

None block Employee #4 implementation. They form the natural next hygiene queue.

## Phase 2 — Bug Triage Specialist Discovery Package (Rigby SIGN-clean)

### Why Bug Triage as Employee #4

Selected over Spider Network Auditor, Code Reviewer, Doc Search Curator, Cost Reporter because it would be
the **first downstream employee** — consumes outputs that the existing three employees produce + the broader
`CeleryTaskEvent` / `AgentExecution` failure surface. This validates the "primitives compose for inter-employee
data flow" claim from `docs/EMPLOYEE_OS_PRIMITIVES.md` §1 which has not been tested yet.

Zero new infrastructure (no new models, no new external APIs, no new PA tools, no new admin UIs).
Authority contract exercises every level cleanly. Low ops risk + high revert-ability.

### AIEmployee constant (Rigby-approved)

```python
BUG_TRIAGE_SPECIALIST = AIEmployee(
    handle='bug_triage_specialist',
    display_name='Bug Triage Specialist',
    runs_as_username='chris',          # matches RIGBY/PA/CoS per v0 auth honesty
    primary_chat_id=None,              # no pinned conversation (matches PA + CoS)
    notes=(
        'Read-only failure-pattern reporter. Consumes CeleryTaskEvent, '
        'AgentExecution, OpsRun, OpsRunEvent. Produces one daily triage '
        'Deliverable. No write access except deliverable creation. v0 does '
        'not auto-certify — certification left to Rigby/human review of the '
        'daily Deliverable.'
    ),
)
```

### JobContract draft (Rigby SIGN-clean after corrections)

```python
BUG_TRIAGE_JOB = JobContract(
    title='Daily Bug Triage',
    employee_handle='bug_triage_specialist',
    manager='chris',
    mission_run_kind='bug_triage_daily',

    mission=(
        'Bug Triage Specialist owns running a daily failure-pattern scan across '
        'the platform\'s telemetry surface, clustering errors by signature, '
        'ranking patterns by recurrence, and producing one structured triage '
        'Deliverable per day. The triage is strictly read-only: it inspects '
        'CeleryTaskEvent failures, AgentExecution failures, OpsRun verdicts, '
        'and OpsRunEvent rows in a fixed 24h window. The specialist does NOT '
        'modify code, open PRs, restart workers, dispatch other employees\' '
        'missions, or take remediation actions. Findings are persisted as a '
        'structured Deliverable; failures escalate per the standard Employee '
        'OS visibility guarantee.'
    ),

    triggers=(
        'Cron only (v0). Beat schedule lands in PR 4.3 — daily at 08:00 '
        'Denver, after Chief of Staff Morning Brief (07:00 Denver) so triage '
        'incorporates the most recent morning brief OpsRun verdict.',
        'Manual override via employee_tool action=run_now '
        'employee=bug_triage_specialist job=triage_daily.',
    ),

    daily_routine=(
        'Step 1 — collect_celery_failures: query CeleryTaskEvent rows with '
        'status=FAILURE in last 24h.',
        'Step 2 — collect_agent_failures: query AgentExecution rows with '
        'status=failed in last 24h.',
        'Step 3 — collect_mission_verdicts: query OpsRun(domain=mission) rows '
        'in last 24h, group by verdict.',
        'Step 4 — collect_authority_events: query OpsRunEvent(label='
        'authority_contract_observed) in last 24h — supports the S1264 '
        'enforce-mode prereq #2 baseline accumulation.',
        'Step 5 — cluster_by_signature: group failures by (task_name|'
        'agent_name, error_type, first 80 chars of error_message). Rank by '
        'occurrence count.',
        'Step 6 — generate_triage_report: synthesize the findings into one '
        'structured Deliverable (Window Summary / Top Failure Patterns / '
        'Mission Verdicts Today / Authority Telemetry Today / Recommendations '
        '/ Green Checks).',
        'Step 7 — record run summary + mark OpsRun.status=passed/failed. '
        'NO auto-certification in v0 — leave mission_verdict to Rigby/human '
        'review of the daily Deliverable.',
    ),

    weekly_routine=(),  # explicit empty — daily-only v0

    mission_run_kind='bug_triage_daily',

    # ── Authority — 17 entries (4 OBSERVE + 3 EXECUTE + 1 RECOMMEND + 9 PROHIBITED)
    authority={
        # OBSERVE (4)
        'read_celery_task_events': AuthorityLevel.OBSERVE.value,
        'read_agent_executions': AuthorityLevel.OBSERVE.value,
        'read_ops_runs': AuthorityLevel.OBSERVE.value,
        'read_ops_run_events': AuthorityLevel.OBSERVE.value,
        # EXECUTE (3)
        'cluster_failures_by_signature': AuthorityLevel.EXECUTE.value,
        'generate_triage_report': AuthorityLevel.EXECUTE.value,
        'save_triage_to_deliverable': AuthorityLevel.EXECUTE.value,
        # RECOMMEND (1)
        'recommend_remediations': AuthorityLevel.RECOMMEND.value,
        # PROHIBITED (9)
        'modify_any_file': AuthorityLevel.PROHIBITED.value,
        'open_pull_request': AuthorityLevel.PROHIBITED.value,
        'restart_worker': AuthorityLevel.PROHIBITED.value,
        'dispatch_other_employee_mission': AuthorityLevel.PROHIBITED.value,
        'modify_settings': AuthorityLevel.PROHIBITED.value,
        'delete_database_rows': AuthorityLevel.PROHIBITED.value,
        'execute_arbitrary_code': AuthorityLevel.PROHIBITED.value,
        'kill_celery_task': AuthorityLevel.PROHIBITED.value,
        'modify_periodic_task_enabled': AuthorityLevel.PROHIBITED.value,
    },

    prohibited_actions=(
        'Modify any file (config, code, docs).',
        'Open or merge pull requests.',
        'Restart Celery workers or Daphne.',
        'Dispatch a mission run for any other employee.',
        'Kill or cancel running Celery tasks.',
        'Enable or disable PeriodicTask rows.',
        'Execute arbitrary code outside the named triage tools.',
        'Delete or update rows in any database model.',
        'Take direct remediation actions — only recommend in deliverable.',
    ),

    required_summary_keys=(
        # Window shape
        'window_start_iso',                      # ISO 8601, 24h ago
        'window_end_iso',                        # ISO 8601, mission start
        # Failure inventory (steps 1-2)
        'celery_failures_count',                 # int
        'agent_failures_count',                  # int
        # Mission visibility (step 3)
        'missions_today_total',                  # int
        'missions_certified_count',              # int
        'missions_rejected_count',               # int
        'missions_deferred_count',               # int
        'missions_in_progress_count',            # int
        # Authority telemetry (step 4) — supports S1264 enforce-mode baseline
        'authority_events_count',                # int
        'authority_events_by_employee',          # dict[str, int]
        # Clustering (step 5)
        'cluster_count',                         # int — distinct signatures
        'top_cluster_signature',                 # str — highest-occurrence
        'top_cluster_occurrences',               # int
        # Synthesis output (step 6)
        'report_deliverable_id',                 # UUID
        'report_chars',                          # int
        'recommendations_count',                 # int
        # Standard MissionRunner fields (bounded per Rigby Edit 5)
        'wall_time_ms',
        'failed_step',
        'error_tail_preview',                    # last N lines, not full tail
        'has_full_error_tail',                   # bool — full tail lives in OpsRunEvent
        'degraded_evidence',
    ),

    evidence_tables=(
        'OpsRun (domain=mission, run_kind=bug_triage_daily)',
        'OpsRunEvent (one per triage step + verdict_issued + '
        'authority_contract_observed)',
        'CeleryTaskEvent (source-of-truth for celery failure rows read in '
        'step 1)',
        'LLMCallEvent (from gpt-5.2 synthesis in step 6)',
        'ToolCallRecord (from each triage helper tool invocation if any)',
        'Deliverable (triage report — created on every run, not just '
        'on escalation)',
    ),

    drift_count_definition=(
        'Drift for Bug Triage = delta in top_cluster_occurrences vs the prior '
        '24h window. Captured in step 5 metadata for trend tracking. Not used '
        'as a verdict gate in v0 — purely observational telemetry.'
    ),

    embed_step_timeout={},

    # ── Escalation (Rigby SIGN-clean full block) ─────────────────────
    escalation_rules=(
        'First failure of any step → escalate immediately (no '
        'retry-then-escalate; the canonical MissionRunner pattern is '
        'fail-fast).',
        'Subsequent failures with the SAME failure signature within 24h → '
        'append a reference to the prior escalation Deliverable rather than '
        'create a duplicate. Dedupe key: MissionRunner.make_error_signature('
        'failed_step, error_tail).',
        '3 failures of any kind within a 7-day rolling window → mark the job '
        'trust_status=under_review in the status tool derived response. No '
        'state change to the JobContract itself.',
    ),

    escalation_visibility=(
        'Create a Deliverable with publish_intent=publish_candidate titled '
        '"Bug Triage Escalation [YYYY-MM-DD]" in workspace '
        'EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME (Donkey Betz).',
        'Force the Deliverable to a visible state (ready or '
        'attention-required) via the canonical status transition path with '
        'source=BugTriageSpecialist. Required because Deliverable.create '
        'currently defaults new rows to status=completed regardless of '
        'explicit param (S1252 footgun; mirror PA workaround at '
        'core/jobs/platform_audit.py:_persist_audit_deliverable).',
        'No PA chat post for v0 — Bug Triage has no pinned PA conversation. '
        'Findings + escalations visible in the /inbox web UI via the '
        'shift-report DM (post_shift_report at core/employees/comms.py).',
    ),

    dedupe_rule=(
        'Duplicate escalation suppression MUST key off the failure signature '
        'derived from OpsRun.summary.failed_step + a normalized hash of '
        'OpsRun.summary.error_tail (canonical '
        'MissionRunner.make_error_signature). Same signature within 24h → '
        'append to or reference the prior escalation. Different signature → '
        'new Deliverable, even if the prior one is still open. 24h window '
        'matches PA + CoS dedupe conventions.'
    ),

    success_metrics=(
        'All 7 triage steps return without raising.',
        'Triage Deliverable includes the 6 required sections.',
        'Triage Deliverable persisted with deliverable_type=analysis.',
        'Total mission wall time < 3 minutes.',
        'cluster_count + top_cluster_occurrences recorded in summary.',
    ),

    failure_metrics=(
        'Any of the 7 steps raises or returns malformed shape.',
        'Triage Deliverable missing one or more required sections.',
        'Wall time exceeds 10 minutes.',
        '3 failures within 7d rolling → trust_status=under_review.',
    ),

    what_chris_approves=(
        'The contract itself (PR 4.1 review).',
        'Weekly: reads employee_tool action=status '
        'employee=bug_triage_specialist and decides if recommended '
        'remediations warrant a follow-up PR.',
        'Acts on the daily triage Deliverable findings.',
        # NEW vs PA: certification surface
        'Reviews the daily triage Deliverable and issues mission_verdict '
        '(certify/reject/defer) via the PA tool — v0 does not auto-certify.',
    ),

    what_claude_handles=(
        'Writing PRs 4.1 / 4.2 / 4.3 of this rollout.',
        'Fixing bugs surfaced by triage findings (in separate PRs after '
        'Chris reviews the deliverable).',
        'Adding new failure-source tables to the triage scope.',
    ),

    what_rigby_can_do_alone=(
        'Run the daily triage routine.',
        'Read CeleryTaskEvent, AgentExecution, OpsRun, OpsRunEvent.',
        'Cluster failures by signature.',
        'Generate + persist the triage Deliverable.',
        # NEW vs PA: certification stays with Rigby (the PA tool gate honors this)
        'Issue mission_verdict (certify/reject/defer) on Bug Triage missions '
        'after reviewing the daily Deliverable.',
        'Emit escalation artifacts per visibility guarantee.',
        'Answer employee_tool action=status queries.',
    ),
)
```

### Locked decisions (every Rigby SIGN edit applied)

| # | Decision | Origin |
|---|---|---|
| D1 | Step 7 = mark OpsRun.status passed/failed; **NO auto-certification in v0** | Rigby blocking Edit 1 |
| D2 | Authority table = **17 entries** (4 OBSERVE + 3 EXECUTE + 1 RECOMMEND + 9 PROHIBITED) | Rigby blocking Edit 2 (recounted from buggy 16-claim) |
| D3 | Full escalation block (rules + visibility + dedupe_rule) verbatim per JobContract dataclass schema | Rigby blocking Edit 3 |
| D4 | Step events fire even on 0-row queries (consistent shape) | Rigby Edit 4 (non-blocking adopted) |
| D5 | Replace `error_tail` with `error_tail_preview` + `has_full_error_tail` (bounded summary) | Rigby Edit 5 (non-blocking adopted) |
| D6 | LIFT `_persist_to_summary` to shared helper NOW (N=4 = right time, was S1261 deferred) | Rigby §8.6 call |
| D7 | Evidence tables include LLMCallEvent + CeleryTaskEvent reference; no FailureDetection | Rigby §8.7 |
| D8 | Dedupe uses `MissionRunner.make_error_signature` everywhere, 24h window explicit | Rigby §8.8 |
| D9 | Implementation chooses **deliverable_append vs new-deliverable-with-backlink** for "subsequent failure" path — either acceptable | Rigby micro-edit (deferred to implementation) |

### Three "must NOT do" proofs (audited)

| # | Constraint | Proof |
|---|---|---|
| P1 | Does not modify code, open PRs, restart workers, or dispatch employees | All 4 declared PROHIBITED in `authority` dict + listed in `prohibited_actions` tuple. No step in `daily_routine` performs these. v0 implementation = ORM read + one Deliverable write. |
| P2 | No MissionRunner / JobContract dataclass changes | `BUG_TRIAGE_JOB` uses existing JobContract fields ONLY (verified against `core/employees/jobs.py:94-163`). `mission_run_kind='bug_triage_daily'` is a new VALUE; no schema change. Inherits `summary_field_for_error_signature='error_signature'` default. |
| P3 | Uses existing primitives only | See "Primitive reuse audit" below — every primitive cited has been in production since at least S1264. Adheres to `EMPLOYEE_OS_PRIMITIVES.md` §5 quick-start checklist. |

### Primitive reuse audit (zero new primitives)

| Primitive | Location | Bug Triage usage |
|---|---|---|
| `AIEmployee` dataclass | `core/employees/jobs.py:73` | `BUG_TRIAGE_SPECIALIST` constant |
| `JobContract` dataclass | `core/employees/jobs.py:94` | `BUG_TRIAGE_JOB` constant |
| `AuthorityLevel` enum | `core/employees/jobs.py:41` | authority dict values |
| `_EMPLOYEES_BY_HANDLE` registry | `core/employees/jobs.py:971` | register handle → AIEmployee |
| `_JOBS_BY_EMPLOYEE` registry | `core/employees/jobs.py:977` | register handle → {job_key: JobContract} |
| `MissionRunner` | `core/employees/mission_runner.py:583` | orchestrate 7 steps + verdict + escalation |
| `MissionRunnerConfig.job_contract` | `core/employees/mission_runner.py` (S1264) | pass `BUG_TRIAGE_JOB` for warn-mode emission |
| `MissionRunner.make_error_signature` | `core/employees/mission_runner.py` | dedupe escalations (24h) |
| `emit_mission_verdict` | `core/employees/mission_verdict.py` | **NOT called by Bug Triage v0** — left to Rigby PA tool path |
| `OpsRun` model | `core/models_ops_runs.py` | mission record, `run_kind=bug_triage_daily` |
| `OpsRunEvent` model | `core/models_ops_runs.py` | one event per step + verdict + `authority_contract_observed` |
| `Deliverable` model | `core/models_deliverables.py` | triage report via existing factory |
| `post_shift_report` | `core/employees/comms.py` | DM shift report |
| `build_*_runner` factory pattern | `core/jobs/docs_cascade.py:699` / `platform_audit.py:916` / `morning_brief.py` | `build_bug_triage_runner()` |
| `_persist_to_summary` | `core/jobs/platform_audit.py:118` | **LIFT to shared helper** (Rigby D6) |
| `@shared_task` wrapper | `core/tasks_platform_audit.py` pattern | `core/tasks_bug_triage.py` NEW |
| HTTP API (5 endpoints) | `core/views_employee_api.py` (S1265) | auto-surfaces via `list_employees()` |

### De-duplication delta vs Platform Auditor

| Dimension | Platform Auditor | Bug Triage Specialist |
|---|---|---|
| Question | "Is the platform CONFIGURED correctly RIGHT NOW?" | "What FAILED in the last 24h?" |
| Time semantics | Point-in-time snapshot | 24h rolling window |
| Tables read | docs files + integration configs + env var names + 8 canonical model row counts | `CeleryTaskEvent` (failures) + `AgentExecution` (failures) + `OpsRun` (verdicts) + `OpsRunEvent` |
| Cadence | Weekly (Mon 06:30 proposed; no beat row exists yet — F1) | Daily (08:00 Denver, after CoS at 07:00) |
| `run_kind` | `platform_audit` | `bug_triage_daily` |
| Deliverable sections | Executive Summary / Integration Health / Configuration Status / Database Health / Top Risks / Green Checks | Window Summary / Top Failure Patterns / Mission Verdicts Today / Authority Telemetry Today / Recommendations / Green Checks |
| Authority entries | 15 (5 EXECUTE + 2 OBSERVE + 1 RECOMMEND + 7 PROHIBITED) | 17 (4 OBSERVE + 3 EXECUTE + 1 RECOMMEND + 9 PROHIBITED) |
| Auto-certifies | Yes (step 6 calls `emit_mission_verdict`) | **No (v0)** — Rigby/human certifies via PA tool |
| Overlap | n/a | NONE — PA inspects config state; Triage inspects failure patterns |

## Implementation footprint (finalized for S1267)

| File | Action | LOC est. |
|---|---|---|
| `core/employees/jobs.py` | modify (+AIEmployee + +JobContract + register in 2 dicts) | +310 |
| `core/employees/_persistence.py` | **NEW** — extracted `_persist_to_summary` shared helper (Rigby D6 LIFT) | ~80 |
| `core/jobs/platform_audit.py` | modify (replace inline `_persist_to_summary` at line 118 with import) | ~3 line delta |
| `core/jobs/docs_cascade.py` | modify (same import swap if it has its own copy) | ~3 line delta |
| `core/jobs/morning_brief.py` | modify (same import swap if it has its own copy) | ~3 line delta |
| `core/jobs/bug_triage.py` | **NEW** — 7 step functions + factory + escalation_spec_factory + shift_report formatter | ~700-800 |
| `core/tasks_bug_triage.py` | **NEW** — `@shared_task` wrapper around `build_bug_triage_runner().run()` | ~100 |
| `core/celery.py` | modify (+import + eager-import set) | +2 |
| `core/migrations/0375_session_xxxx_bug_triage_beat.py` | **NEW** — seed `PeriodicTask(enabled=False)` at 08:00 Denver | ~50 |
| `core/tests/test_employees_bug_triage.py` | **NEW** — mirror `test_employees_platform_auditor.py` shape | ~600 |
| `core/tests/test_celery_queue_parity.py` | modify (+`BugTriageTaskRegistrationTests` class) | +30 |
| **Total** | | ~1,900-2,100 LOC across **9 files modified/created** |

## Verification gates (must pass before merge)

| # | Gate | Verification path |
|---|---|---|
| V1 | `JobContract` registers cleanly | `get_employee('bug_triage_specialist')` returns the constant; `list_jobs_with_keys('bug_triage_specialist')` returns `[('triage_daily', BUG_TRIAGE_JOB)]` |
| V2 | Celery task discoverable | `.venv/bin/celery -A core inspect registered \| grep bug_triage_daily_run` |
| V3 | All 7 steps emit OpsRunEvent rows even on 0-row queries (Rigby D4) | manual run → `OpsRunEvent.objects.filter(run=...).count() >= 7` |
| V4 | Triage Deliverable created with 6 required sections | inspect `Deliverable.objects.filter(workspace__name='Donkey Betz', deliverable_type='analysis').latest('created_at').content` |
| V5 | `error_tail_preview` + `has_full_error_tail` present in summary (Rigby D5) | `OpsRun.objects.latest('started_at').summary` keys check |
| V6 | `authority_contract_observed` emits exactly once (extends N=1 → N=2 evidence) | `OpsRunEvent.objects.filter(label='authority_contract_observed', run=...).count() == 1` |
| V7 | NO `emit_mission_verdict` call from Bug Triage runner (Rigby D1) | grep `core/jobs/bug_triage.py` for `emit_mission_verdict` — should be absent |
| V8 | HTTP API auto-surfaces new employee | `GET /api/employees/` returns count=4 including `bug_triage_specialist` |
| V9 | HTTP API `/api/employees/bug_triage_specialist/jobs/triage_daily/status/?window=7d` returns shape-equivalent payload to existing employees | curl/Client probe |
| V10 | `_persist_to_summary` LIFT verified: PA + CoS + Bug Triage all import from shared helper, behavior unchanged | grep + test runs |
| V11 | Rigby SIGN at pre-PR + pre-merge per verifier-loop pattern | manual SIGN messages |
| V12 | Beat row created `enabled=False` initially | migration applied → `PeriodicTask.objects.get(task='bug_triage_daily_run').enabled == False` |
| V13 | Manual `employee_tool action=run_now employee=bug_triage_specialist job=triage_daily` produces a non-empty Deliverable | dispatch + verify |
| V14 | Flip `enabled=True` only after V13 green for ≥1 manual run | admin action + verify beat fires at next 08:00 Denver |

## Implementation sequence (recommended for S1267)

Per `EMPLOYEE_OS_PRIMITIVES.md` §5 + Rigby decisions:

1. **Open session with `context-kit orient`** + Rigby conversation health check.
2. **PR 4.0 (prerequisite hygiene): LIFT `_persist_to_summary`** to `core/employees/_persistence.py`. Update PA + CoS imports. Tests + Rigby SIGN-clean before continuing.
3. **PR 4.1: Contract + registry**. Add `BUG_TRIAGE_SPECIALIST` + `BUG_TRIAGE_JOB` to `core/employees/jobs.py`. Register in 2 dicts. Update test_celery_queue_parity. Rigby SIGN.
4. **PR 4.2: Job module + task wrapper**. Write `core/jobs/bug_triage.py` (7 steps) + `core/tasks_bug_triage.py` (shared_task) + `core/celery.py` imports. Migration `0375_…` seeded `enabled=False`. Full test file. Manual run verification per V1-V13. Rigby SIGN.
5. **PR 4.3: Flip beat to enabled=True**. After PR 4.2 is green + at least one clean manual run on production code. Single-line admin migration or direct admin UI flip.

## Memory observations worth keeping

- **The verifier-loop pattern caught 3 design issues this session.** Rigby's blocking edits: (1) mission_verdict speaker-gate conflict — caught the "Bug Triage cannot call mission_verdict like PA/CoS do because the gate is speaker-Rigby not server-side" subtlety; (2) authority math 16/18 inconsistency — recounted to 17; (3) escalation block truncation — full text now in handoff. Without this loop, all three would have shipped in code.
- **"First downstream employee" is a real validation lens.** Bug Triage was selected over Spider Auditor / Code Reviewer / Doc Curator / Cost Reporter explicitly because it CONSUMES other employees' outputs. This tests "primitives compose for inter-employee data flow" with concrete data instead of theory.
- **N=4 triggers the LIFT decision for `_persist_to_summary`.** Rigby flipped §8.6 from "S1261 N=2 deferral" to "centralize NOW" because adding a 4th employee that copies the same pattern is the natural trigger point. EMPLOYEE_OS_PRIMITIVES.md §5 step 7 already mentions "thin `core/employees/comms_<job>.py`" — analogous LIFT precedent.
- **Honest auto-cert conservatism for new employee pattern.** PA + CoS auto-certify via `emit_mission_verdict`; Bug Triage explicitly does NOT in v0. After 14+ days clean Bug Triage data + Rigby review of N≥3 missions, auto-cert can flip on. Matches S1264 enforce-mode prereq pattern.
- **No prerequisite PRs needed.** The 5 audit findings (F1-F5) are NOT blockers; they're the natural next hygiene queue. F4 (Rigby drift-hygiene) was S1265 Candidate B and remains the next-after-Employee-#4 candidate.

## Session metadata

- **Window:** 2026-06-30, continuation of single-day arc started at S1259 open.
- **Rigby conversation:** `pa-3a226cd451494350` carried both the S1266 audit + Employee #4 discovery + SIGN. Created S1265 open; should be evaluated at S1267 open for rotate vs continue.
- **Verifier-loop:** caught 3 blocking design issues + adopted 2 non-blocking recommendations. Same pattern that caught the PR #2760 ToolDispatcher coupling and the D3 auth gate flip in S1265.
- **No code shipped.** Working tree clean at S1266 close. Implementation explicitly held for fresh session per Chris's directive.
