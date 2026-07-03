---
session: 1705
status: closed (Group 1700 Cat E OpsRun + OpsRunEvent child audit LANDED — FIFTH child under Group 1700 per parent D72 P5 slot; audit doc landed `status: active` post-fold; Rigby SIGN cycle 1 SIGN-with-edits at Medium/Medium-High confidence on arc pin `pa-e7fbacc996b34b44` — fresh SIGN isolation pin `pa-09c46ee3a0d34069` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code (S1600/S1700/S1701/S1702/S1703/S1704 precedent: arc pin doubles as SIGN pin; fresh SIGN pin retired at S1705 close per §16 with `updated_count=1, retired=true, previously_active=true`); F1-F7 folds landed pre-commit; D48 preemptive stability-probe gate 22nd arm HOLDING CLEAN — 17-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704+S1705 CONFIRMED per single-batch-4-question criterion; ARCHITECTURE_INDEX v47 → v48 with §1.51 S1705 registration + §8 timeline S1705 row + line-6 v48 preamble; OPEN_ARCS Group 1700 In-progress row current-child updated S1704 → S1705; arc pin retained through Group 1700 close at S1799; next session: S1706 Cat F Adjacent/Separation Boundaries per D72 P6 slot — LAST child before S1799 xx99 canonical summary)
date: 2026-07-03
arc: Research Group 1700 (Observability / Telemetry / SLOs) — Cat E OpsRun + OpsRunEvent child audit; FIFTH child session under Group 1700 per D72 P5 slot
category: research (playbook §11.2 child audit template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN cycle 1)
head_commit_before: a991971a (main; post-S1704 close + start-here refresh PR #2845)
head_commit_after: (this commit)
authors: Claude Code (Chris directed via short command "Start research group 1705")
---

# Session 1705 — Group 1700 Cat E OpsRun + OpsRunEvent Child Audit

> **Fifth child audit under Group 1700 (Observability arc).** Playbook §11.2 20-section template FIFTH application under Group 1700 arc (first was S1701 Cat A CeleryTaskEvent; second S1702 Cat B LLMCallEvent; third S1703 Cat C AgentExecution; fourth S1704 Cat D ToolCallRecord). 6-parallel-Explore sweep + parent-Claude verifier-loop applied both pre-Explore and post-Explore. Rigby SIGN cycle 1 delivered SIGN-with-edits at Medium/Medium-High confidence via single-batch 4-question pattern (D48 22nd arm HOLDING CLEAN — 17-consecutive-fully-clean-arms sub-pattern confirmed).

## What shipped

### 1. Audit doc

- **`docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md`** (NEW; 916 lines pre-fold + ~60 lines added by F1-F7 folds)
- `status: active` after Rigby SIGN cycle 1 SIGN-with-edits
- `authority: child-audit`, `category: child_audit`, `session: 1705`, `child_slot: P5`, `domain_slug: observability`, `research_group: 1700`
- Applies playbook §11.2 20-section child audit template + §13 6-parallel-Explore + §14 verifier-loop discipline (both pre-Explore and post-Explore)

### 2. Rigby SIGN cycle 1 folds (F1-F7, all landed pre-commit)

- **F1 (Q2(b) — Medium)** — §14 drift matrix: D4 severity justification block added ("Severity remains HIGH even though the fix is upstream — Chris-facing operator surface `evidence_for_mission` documented join path is non-functional at HEAD")
- **F2 (Q3(b) — Medium-High)** — §1.1 F9: nuance added ("Flipping the Cat E flag DOES yield partial usefulness inside Cat E even if Cat D remains broken — the delegated-execution lifecycle path would begin writing execution_id into OpsRunEvent.detail, strengthening the Cat E → Cat C join potential. Precise Option B framing: resolves nothing for the ToolCallRecord join, but unlocks the execution_id spine cell in the Cat E → Cat C axis.")
- **F3 (Q3(d) — Medium)** — §1.1 F5: canonical verdict block appended ("Canonical verdict at HEAD: OpsRunEvent is producer-only. This could evolve to 'producer + consumer' only if future work introduces cross-table correlation IDs and an explicit aggregation pipeline — post-arc T-slot work, not a v0 concern.")
- **F4 (Q4(a) — Medium)** — §19: R2 sequencing note added ("R2 is the lowest-cost lever to generate Cat E runtime evidence, but should be sequenced after (or explicitly in service of) the R1 D74 posture decision to avoid producing evidence against an obsolete spine choice.")
- **F5 (Q4(b) — Medium)** — §19: R3 cross-cat remediation scope note added ("R3 remains HIGH as an operator-surface contract breach, but remediation is cross-cat: depends on Cat D correlation primitive population (S1704 F1/F2) and Cat C PA coverage (S1703 F4). Not solvable at Cat E alone.")
- **F6 (Q4(c) — Medium)** — §19: R6 scope discipline note added ("Land as a 1-2 sentence canonical note in xx99 §7.4 ('OpsRunEvent is producer-only at HEAD'), with deeper rationale staying in this audit doc + optional pointer from EMPLOYEE_OS_PRIMITIVES §1. Do not inflate R6 into a large workstream.")
- **F7 (Q4(d) — Medium)** — §19: R2 scope discipline block added per playbook §14.5 ("xx99 scope: record the recommended toggle as an evidence-plan decision; do NOT implement/flip flags during arc-close per §14.5 no-implementation rule.")

### 3. ARCHITECTURE_INDEX bump

- **`docs/research/ARCHITECTURE_INDEX.md`** v47 → v48
- §1.51 S1705 registration (S1705 Cat E OpsRun + OpsRunEvent Child Audit)
- §8 timeline S1705 row (below S1704 row, above S1600 row per timeline order)
- Line 6 v48 preamble (S1705 close summary with F1-F9 + folds); prior v47 preamble demoted to "Prior v47 preamble" block

### 4. OPEN_ARCS refresh

- **`docs/research/OPEN_ARCS.md`** Group 1700 In-progress row current-child updated S1704 → S1705
- Arc pin `pa-e7fbacc996b34b44` retained per playbook §16 through Group 1700 close at S1799
- Group 1700 arc progress: 6/8 = 75% (parent S1700 + S1701 + S1702 + S1703 + S1704 + S1705 done; S1706 + S1799 pending)

### 5. Rigby SIGN pin retirement

- Fresh SIGN isolation pin `pa-09c46ee3a0d34069` retired at S1705 close per playbook §16
- ORM result: `retired=true, updated_count=1, previously_active=true, is_current_bound=false`
- Arc pin `pa-e7fbacc996b34b44` continues in service through Group 1700 close at S1799

## 9 load-bearing findings locked in S1705 audit §1.1 Executive Summary

- **F1 (HIGH, §17)** — 0/224 OpsRunEvent rows carry cross-cat correlation IDs in `detail` JSON at HEAD (ORM-verified 2026-07-03: execution_id=0, trace_id=0, task_id=0, tool_call_id=0, agent_execution_id=0, llm_call_id=0, celery_task_id=0). DESIGN-INTENT writer at `core/signals/rigby_delegation_signals.py:79-84` (Session 1250 PR 8) IS built to populate `execution_id` in detail on delegated-execution post-save (`parent_object_type='RigbyWorkItem'`), but the handler is gated by `settings.RIGBY_DELEGATION_ENABLED` (default `False` per `rigby_delegation_signals.py:22-25`). **Distinct from S1704 F1** (Cat D's `trace_id` is 100% NULL as schema+runtime failure — column exists + indexed + always-hardcoded-None at three writer sites). Cat E is intentionally-flag-gated: DESIGN-INTENT-LATENT.
- **F2 (HIGH, §17)** — Cat E schema has NO cross-cat correlation columns. OpsRun has `id`, `title`, `run_type`, `status`, `triggered_by`, `started_at`, `finished_at`, `summary` JSON, `event_count`, `fail_count`, `domain`, `run_kind`, `mission_id`. OpsRunEvent has `id`, `run` FK, `event_type`, `label`, `detail` JSON, `created_at`. Neither has `execution_id`, `trace_id`, `tool_call_id`, `celery_task_id`, `task_id`. Only `mission_id` (indexed, mission-domain only) + implicit `run` FK are correlation surfaces. Parallel to S1704 F2.
- **F3 (MEDIUM, verifier-loop-corrected, §14+§17)** — Employee count drift. CLAUDE.md at :150-172 + PLATFORM_INVENTORY autoblock claim "3 Employees". Runtime registry `_EMPLOYEES_BY_HANDLE` at `core/employees/jobs.py` has **4** handles verified via ORM: rigby (`docs_manager`), platform_auditor (`platform_audit`), chief_of_staff (`morning_brief`), **bug_triage_specialist (`triage_daily` — added S1267 PR 4.1**). Drift is on-count-only; runtime works correctly (4 mission `run_kind` values in OpsRun match 4 employees).
- **F4 (POSITIVE differentiator vs S1704 F4, §7+§9)** — CTO/COO/Trend Analysis daily diagnostic pipelines EXIST at `core/services/diagnostics/{cto_daily,coo_daily}.py` + `core/services/scheduled_diagnostic_runner.py` AND ARE beat-wired at `core/celery.py:306-329`:
  - `cto-daily-diagnostic` @ 07:15 Denver → `run_cto_daily_diagnostic` (queue: long_running, expires: 7200)
  - `coo-daily-diagnostic` @ 07:30 Denver → `run_coo_daily_diagnostic` (queue: long_running, expires: 7200)
  - `trend-daily-diagnostic` @ 07:45 Denver → `run_trend_daily_diagnostic` (queue: long_running, expires: 7200)

  **Material Cat E vs Cat D difference:** S1704 F4 found `analyze_pa_tool_patterns` + `aggregate_tool_call_stats` beat-orphan; Cat E has three fully-wired daily aggregations. NOT WRITE-ONLY-FORGOTTEN.
- **F5 (MEDIUM, §9+§17)** — But those three daily aggregations do NOT consume OpsRunEvent (CTO daily reads CeleryTaskEvent + AgentExecution; COO daily reads Deliverable + ActionItem + Initiative backlog; Trend Analysis daily reads LegacySpiderData + SignalCluster). **OpsRunEvent has ZERO downstream aggregation consumer.** Resolves parent §5.E producer-vs-consumer question: **OpsRunEvent is a PRODUCER-ONLY primary source of mission telemetry**. Canonical verdict at HEAD per Rigby SIGN Q3(d) fold: could evolve if future work introduces cross-table correlation IDs + explicit aggregation pipeline — post-arc T-slot.
- **F6 (MEDIUM, §15)** — No date-based retention for OpsRun/OpsRunEvent. Parallel to S1704 F5 + S1702 F4. 36 OpsRun over 20 days → ~657/year projected; 224 OpsRunEvent → ~4,088/year projected. Small cadence but unaudited-headroom.
- **F7 (MEDIUM, §9+§17)** — `evidence_for_mission` join at `docs/topics/employee-os.md:64-65` EMPIRICALLY BROKEN for ToolCallRecord — two orthogonal write-gap paths:
  - `ToolCallRecord.filter(parameters__ops_run_id=str(run.id))` at `status.py:475-483` — EMPTY (Cat D dispatcher never threads `ops_run_id` into `parameters`)
  - `ToolCallRecord.filter(trace_id=execution.trace_id)` at `deliverable_provenance.py:105` — EMPTY per S1704 F1 (100% NULL)

  LLMCallEvent join by `metadata__ops_run_id` WORKS (`emit_mission_verdict.py:117-150` populates). Named-but-broken integration. D4 HIGH held per Rigby SIGN Q2(b) fold.
- **F8 (POSITIVE, §7+§13)** — MissionRunner nine invariants I1-I9 all VERIFIED at HEAD via source read + contract test at `test_mission_runner.MissionRunnerImportContractTests` @ `core/tests/test_mission_runner.py:181-250`:
  - I1 daily idempotency `_existing_mission_for_today()` @ :759-772
  - I2 in-progress safety (implicit)
  - I3 event idempotency `get_or_create` @ :812-816
  - I4 verdict idempotency via `emit_mission_verdict`
  - I5 step ordering @ :1030-1053
  - I6 escalation atomicity `with transaction.atomic():` @ :1209
  - I7 dedupe `(failed_step, error_signature)` window @ :1250-1275
  - I8 hook containment
  - I9 no employee-specific imports (contract-tested)

  Cat E writer-mechanism maturity STABLE.
- **F9 (D74 axis contribution, §9)** — Cat E provides **LATENT-VIABLE-BUT-FLAG-GATED evidence** for spine correlation posture. Distinct axis cell from Cat D (S1704 F9 actively-broken-for-Option-B + incomplete-not-broken-for-Option-A) and Cat C (S1703 F4 PA path coverage gap CRITICAL). Cat E is NOT actively-broken and NOT schema-broken — writer path exists, mission_id (indexed) works, execution_id can be threaded via detail JSON when flag flips ON. **Cat E is the cheapest to unblock for Option B** via `RIGBY_DELEGATION_ENABLED=True`, but Cat D F1 + Cat C F4 remain gating for the ToolCallRecord join. **Rigby SIGN Q3(b) fold nuance:** flag flip DOES yield partial usefulness on the Cat E → Cat C axis via execution_id detail-JSON thread, even if the ToolCallRecord join (F7) remains blocked.

## §9 D74 axis-contribution matrix (Cat E fourth cell)

| Layer | trace_id col | execution_id col | mission_id col | Runtime population | Posture |
|---|---|---|---|---|---|
| Cat A CeleryTaskEvent | — | — | — | task_id (unique) populated | Populate baseline |
| Cat B LLMCallEvent | metadata JSON | ✅ (FK) | metadata JSON | execution_id via FK; ops_run_id via metadata JSON | Semi-populated |
| Cat C AgentExecution | ✅ | (self) | — | trace_id populated by S1703 F9 F1 fold | S1703 F4 CRITICAL: PA path coverage gap |
| Cat D ToolCallRecord | ✅ (indexed) | — | — | trace_id 100% NULL empirically | S1704 F1 CRITICAL: runtime failure |
| Cat E OpsRunEvent | — | — (detail JSON) | via `run` FK to OpsRun.mission_id | detail JSON 0/224 rows with execution_id | **S1705 F1 LATENT: flag-gated design-intent** |

## §16 Boundary violation matrix: 5 candidates all LEGITIMATE

MissionRunner + OpsRunTracker + rigby_event_intake + rigby_delegation_signals (flag-gated) + mission_verdict PA tool — no unexpected writer sites via grep. BodyCoordinator NOT integrated (I9 boundary held). `tasks_ops.py` cross-imports from `core.tasks` are LEGITIMATE extraction artifact per file header.

## Maturity classification

- Writer mechanism: **STABLE** (F8 I1-I9 verified)
- Coverage: **PARTIAL** (4/4 employees producing daily OpsRun rows; ops-domain smoke_test only; retention absent)
- Cross-cat correlation contract: **NAMED-BUT-BROKEN** (F7 evidence_for_mission ToolCallRecord join empirically empty due to S1704 F1 + Cat D `parameters.ops_run_id` write-gap)
- Downstream orthogonal pipelines: **STRONG** (F4 CTO/COO/Trend Analysis daily fully beat-wired)
- OpsRunEvent-consuming pipelines: **EMPTY** (F5 producer-only)
- Risk: **MEDIUM**

## Verifier-loop corrections (VC1-VC3)

- **VC1 (F3 corrected):** Explore Agent 5 doc-derived "3 Employees" (from topic-doc reading) vs Explore Agent 6 registry-derived "4 Employees". ORM verified 4 handles. Bug Triage Specialist added S1267 PR 4.1.
- **VC2 (F4 vs Agent 6 F2 claim corrected):** Explore Agent 6 claimed "CTO/COO/Trend Analysis daily DOES NOT EXIST" (searched Ops Autopilot module). Post-Explore grep found them at `core/services/diagnostics/{cto_daily,coo_daily}.py` + `core/services/scheduled_diagnostic_runner.py`, beat-wired at `core/celery.py:306-329`. Agent 2 was correct. Fold: F4 documents the POSITIVE differentiator; misconception was searching wrong package.
- **VC3 (F1 vs Agent 1 claim corrected):** Explore Agent 1 claimed `execution_id` IS threaded into OpsRunEvent.detail via `rigby_delegation_signals.py:70`. ORM check showed 0/224 rows with execution_id key. Source read revealed writer path IS built to populate execution_id but is FLAG-GATED off by `settings.RIGBY_DELEGATION_ENABLED=False`. Fold: F1 distinguishes DESIGN-INTENT-LATENT (Cat E) from SCHEMA+RUNTIME-BROKEN (S1704 F1 at Cat D).

## Session close artifacts committed at S1705 close

```
docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md  [new; ~975 lines post-fold; Cat E child audit; F1-F7 folds landed pre-commit; FIFTH child under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                                   [modified — v47 → v48 with §1.51 S1705 registration + §8 timeline S1705 row + line-6 v48 preamble]
docs/research/OPEN_ARCS.md                                                            [modified — Group 1700 In-progress row current-child updated S1704 → S1705]
docs/handoffs/SESSION_1705_OBSERVABILITY_CAT_E_OPS_RUN_EVENT_AUDIT.md                  [new — S1705 handoff]
00-START-NEXT-SESSION.md                                                              [modified — this file; S1705 Cat E CLOSED; next-session priority = S1706 Cat F Adjacent/Separation Boundaries]
```

Handoff: `docs/handoffs/SESSION_1705_OBSERVABILITY_CAT_E_OPS_RUN_EVENT_AUDIT.md`.
