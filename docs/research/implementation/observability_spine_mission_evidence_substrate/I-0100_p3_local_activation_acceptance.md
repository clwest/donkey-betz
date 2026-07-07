---
title: "Arc I-0100 P3 — Local Activation Acceptance"
status: local-accepted
authority: arc-implementation-acceptance
arc_id: I-0100
arc_slug: observability_spine_mission_evidence_substrate
intake: IB-1799-T1-03
adr: ADR-0003
runtime_pr: 2957
stop_condition_1_pr: 2974
handoff_refresh_pr: 2971
local_only_reality_pr: 2972
p4_acceptance_pr: 2973
acceptance_pr: TBD
operating_model: local-only
ratifier: chris
ratification_mechanism: pr-merge
date_authored: 2026-07-07
scope: single-intake (P3 only; P4 IB-1799-T1-02 accepted separately in PR #2973)
---

# Arc I-0100 P3 — Local Activation Acceptance

## 1. Executive Summary

Under the LOCAL-ONLY operating model formalized in PR #2972, Arc I-0100 P3 (intake `IB-1799-T1-03`; runtime PR #2957 with Stop Condition #1 discharge PR #2974) is **COMPLETE for local operation**.

"Complete" in this context means:

- Every runtime code change required to satisfy ADR-0003 has landed on `main` and is exercised by regression tests that reproduce the design's failure modes.
- All four stop conditions for `RIGBY_DELEGATION_ENABLED=True` have been locally discharged: Stop Condition #1 via PR #2974 (monitoring surface integration + kill-switch wire-up), Stop Condition #2 via the smoke-test evidence bundle (§2 below), Stop Condition #3 via the A1–A6 re-verification (§3 below with two documented discrepancies), and Stop Condition #4 via Chris ratification of this acceptance package.
- The default runtime posture (`RIGBY_DELEGATION_ENABLED=false`) is deliberately unchanged and remains authoritative for the local platform.
- No production verification is applicable because no production deployment currently exists to verify against; per PR #2972's guardrail, future sessions must not attempt production verification unless Chris explicitly provides a live prod access path.
- No further engineering work is required for local operation.

"Complete" **does not** mean:

- The `RIGBY_DELEGATION_ENABLED` flag has been flipped to `true` on any environment (local or otherwise).
- Production activation has been performed or attempted.
- The full Arc I-0100 (P2 + P3 + P4) is closed at Stage 6; this document scopes only P3. Stage 6 close criteria (§4.5) now depend only on which terminal-state name is chosen for P3 + P4 in the runtime discharge table.

## 2. Evidence Summary

### Stop Condition #1 — Monitoring surface integration + flag-flip-to-False action

- **Status:** discharged via PR #2974 (merged 2026-07-07, commit `9372efcf`).
- **Consumer surface:** `core.services.delegation_auto_disable_monitor` — `check_thresholds()` reads all four thresholds from `core.services.delegation_auto_disable`; invoked on-demand via `manage.py delegation_auto_disable_check` (`--verbose`, `--dry-run`, `--clear`).
- **Kill-switch action:** `trip()` sets a cache-key sentinel (`KILL_SWITCH_KEY = "rigby_delegation_kill_switch"`) via `django.core.cache`; `delegate_work_item` and `on_delegation_lifecycle` short-circuit on `is_tripped()` after the existing `RIGBY_DELEGATION_ENABLED` guard.
- **`MONITORING_SURFACE_INTEGRATED = True`** on `main` at `core/services/delegation_auto_disable.py:87`.
- **Regression coverage:** 21 targeted tests in `core.tests.test_delegation_auto_disable_monitor` (below/above per threshold; sentinel set/read/clear/idempotent; audit row emission; log line emission; delegation short-circuit; lifecycle-signal short-circuit; flag-off baseline preservation regardless of sentinel state); 55/55 combined delegation-scope regression pass.
- **Local canary evidence** (in PR #2974 body): consumer detected a real breach against dev DB (33/day > 14.955/day threshold), tripped, emitted `[RIGBY_DELEGATION_AUTO_DISABLED]` log line, wrote OpsRun+OpsRunEvent audit row (`OpsRun id=d1c58567-…`, `OpsRunEvent id=6a08982b-…`), and the delegation entry point short-circuited with `kill_switch=True` under a scoped `override_settings(RIGBY_DELEGATION_ENABLED=True)`.
- **Rollback drill evidence** (in PR #2974 body): `--clear` cleared the sentinel, live flag remained `False`, flag-off baseline response was byte-identical to pre-arc behavior, kill-switch guard confirmed to not over-block when sentinel is clear.

### Stop Condition #2 — Phase 2 evidence bundle Chris review (ADR-0003 §3.1 F1)

`python manage.py delegation_lifecycle_smoke_test --verbose` — **PASS**.

Complete evidence bundle (verbatim from stdout, 2026-07-07 second verification pass):

```json
{
  "phase": "1_shadow_audit_synthetic",
  "adr_ref": "ADR-0003",
  "override_settings_applied": [
    "RIGBY_DELEGATION_ENABLED=True",
    "CELERY_TASK_ALWAYS_EAGER=True"
  ],
  "expected_labels_in_order": [
    "agent_assigned",
    "agent_completed",
    "verification_started",
    "verification_completed",
    "mission_closed"
  ],
  "checks": [
    {"name": "resolve_routed_agent",             "detail": "Found TrendAnalysisAgent id=6f785089-f051-4de8-8550-45bea883cb2a", "ok": true},
    {"name": "create_mission_run",               "detail": "OpsRun id=2a561132-4ebf-4802-b822-029917f9ff91 domain=mission",     "ok": true},
    {"name": "create_work_item",                 "detail": "RigbyWorkItem id=4966fea7-3ae5-4d25-bcd5-631357bec2fa decision=monitor", "ok": true},
    {"name": "create_agent_execution_pending",   "detail": "AgentExecution id=ca9d7f1f-78f1-4ae3-aceb-e2a1a7fee7ae status=pending", "ok": true},
    {"name": "verify_agent_assigned_emitted",    "ok": true},
    {"name": "verify_agent_completed_emitted",   "ok": true},
    {"name": "verify_verification_started_emitted",   "ok": true},
    {"name": "verify_verification_completed_emitted", "ok": true},
    {"name": "verify_mission_closed_emitted",    "ok": true},
    {"name": "verify_idempotency",               "pre_count": 5, "post_count": 5, "ok": true},
    {"name": "verify_verdict_is_verified",       "actual_verdict": "verified", "ok": true},
    {"name": "cleanup",                          "detail": "Savepoint rolled back — zero persistent artifacts", "ok": true}
  ],
  "unhandled_exceptions": [],
  "verdict": "PASS"
}
```

Stdout marker: `DELEGATION_LIFECYCLE_SMOKE_TEST_PASS`.

**Ratified by Chris** — the bundle satisfies every ADR-0003 §3.1 F1 fold requirement (zero unhandled exceptions; successful create → event → evidence join with all 5 lifecycle labels in order; same-settings-surface assertion; committable evidence bundle; idempotency verified `pre=5 post=5`; deterministic verdict `verified`; savepoint cleanup with zero persistent artifacts).

### Stop Condition #3 — Re-verification of A1–A6 assumption-lock gates

| # | Assumption | Ratified (2026-07-06) | Current (2026-07-07) | Status |
|---|-----------|-----------------------|----------------------|--------|
| **A1** | `len(DELEGATION_ROUTING) == 1`; `{'monitor':'TrendAnalysisAgent'}` | `1`; `{'monitor':'TrendAnalysisAgent'}` | Same: `1`; `{'monitor':'TrendAnalysisAgent'}` | **VERIFIED** |
| **A2** | Delegable cadence `< 10/day` (0.00/day at ratification) | `RigbyWorkItem.objects.filter(created_at__gte=T-30d, decision__in=DELEGATION_ROUTING.keys()).count() → 0` (rate `0.00/day`) | **VERIFIED** |
| **A3** | Handler unchanged since 2026-07-06; last commit `d5e7824f` (S1250 PR 8) | `git log --since=2026-07-06 -- core/services/rigby_mission_delegation.py core/signals/rigby_delegation_signals.py` → 1 commit: `9372efcf` (PR #2974) | **CHANGED SINCE RATIFICATION** — additive kill-switch guard only; accepted by Chris as non-blocking |
| **A4** | `MISSION_RUNNER_ENABLED` — zero code matches across `core/**/*.py` (excl. tests/docs) | `grep MISSION_RUNNER_ENABLED core/**/*.py` → "No matches found" | **VERIFIED** |
| **A5** | `MissionRunnerImportContractTests` 4/4 pass | `Ran 4 tests in 0.024s OK` (`test_no_celery_imports`, `test_no_docs_manager_imports`, `test_no_employee_specific_symbol_references`, `test_verdict_constants_match_framework`) | **VERIFIED** |
| **A6** | OpsRun 30d: 43 total (24 mission_id-populated); OpsRunEvent 30d: 299 (~9.97/day) | OpsRun 30d: **46** total / **26** mission_id-populated (+3/+2); OpsRunEvent 30d: **315** (~**10.50/day**, +5.3%); last-24h: **34** | **CHANGED SINCE RATIFICATION** — 30-day rate drift minor; last-24h above `OPSRUNEVENT_DAILY_AUTO_DISABLE = 14.955`; accepted by Chris as non-blocking for LOCAL activation |

**A3 discrepancy detail (evidence-grounded):** Exactly one commit touches the handler files since ratification — `9372efcf` (PR #2974). Diff is purely additive: `+7 LOC` to `rigby_mission_delegation.py`, `+4 LOC` to `rigby_delegation_signals.py`, both adding an `is_tripped()` short-circuit **after** the existing `RIGBY_DELEGATION_ENABLED` guard. When the sentinel is clear (baseline state), execution flow through both handlers is byte-identical to the ratified S1250 PR 8 code. Ratified by Chris as compatible with the A3 assumption because the change is the very Stop Condition #1 discharge PR ratified in the same arc.

**A6 discrepancy detail (evidence-grounded):** 30-day rolling averages drifted +5.3% (299→315 OpsRunEvent) over one calendar day — within noise for a system that emits mission/employee cycles daily. Last-24h count is 34 rows, above the current `OPSRUNEVENT_DAILY_AUTO_DISABLE = 14.955` threshold (baseline × 1.5). Ratified by Chris as **non-blocking for LOCAL activation acceptance** because no flag flip is imminent. Recalibration of `BASELINE_OPSRUNEVENT_DAILY` in `core/services/delegation_auto_disable.py:41` is **deferred until any future flag-flip preparation** and is not a P3 arc-close blocker under the current LOCAL-only regime.

### Stop Condition #4 — Ratified §3.1 F1 entry gate

**Ratified by Chris** via merge of this acceptance PR — the composite evidence package satisfying §3.1 F1 for LOCAL activation is: (1) the smoke test evidence bundle above, (2) the A1–A6 verification table above, (3) `MissionRunnerImportContractTests` 4/4 pass, (4) the 21/21 auto-disable monitor test suite from PR #2974, (5) PR #2957 (P3 runtime) + PR #2974 (P3 SC#1 discharge) both on `main`.

### Current default flag state

- `core/settings.py:138-140` — `RIGBY_DELEGATION_ENABLED` is env-driven with default `'false'`.
- `core/settings.py:173-174` — `PA_AGENT_EXECUTION_WRITE_ENABLED` is env-driven with default `'false'`.
- Neither is changed by any PR in this arc or by this acceptance document. **Both remain `false` at the time this acceptance is authored.**

### Regression coverage summary

- **`core.tests.test_delegation_auto_disable_monitor`** — 21/21 pass (from PR #2974).
- **`core.tests.test_delegation_lifecycle_smoke_test`** — 25/25 pass (from PR #2957 + assertion refresh in PR #2974).
- **`core.tests.test_rigby_mission_delegation`** — 9/9 pass (from Session 1250 PR 8 through the current head).
- **`core.tests.test_mission_runner.MissionRunnerImportContractTests`** — 4/4 pass (A5).

## 3. Local Acceptance Decision

**ACCEPTED for LOCAL operation.**

Arc I-0100 P3 implementation is complete, locally validated, and safe to leave in its current shipped state (code on `main`, flag `false` by default, kill sentinel clear on dev). No further engineering action is required to consider P3 discharged under the local-only operating model. Ratification of this decision is the merge of the PR carrying this file.

## 4. Production Status

- **No production deployment currently exists.** The historical Railway URL (`donkey-betz-platform-production.up.railway.app`) returns 404 with `x-railway-fallback: true`; the Railway CLI is unauthenticated with no project link; `.env.production` contains a placeholder `DATABASE_URL`, not a live one. Same posture as PR #2972 + PR #2973.
- **Production activation has not been attempted.** No prod endpoint responded during any session in this arc; no prod DB was written to; no prod flag was flipped.
- **This is not a failure.** The absence of production is a platform-lifecycle state, not a defect of Arc I-0100 P3. All ADR-0003 requirements are met by the local artifacts.
- **Production validation is deferred until a production environment exists.** When production is stood up, activation validation reopens per the trigger in §5. Until then, per PR #2972's guardrail, no session should attempt prod verification unless Chris explicitly provides a live prod access path.

## 5. Future Trigger

Arc I-0100 P3 reopens if and only if:

> **A production deployment is created, or Chris explicitly requests production activation.**

No other event reopens this arc. Specifically:

- New delegation-adjacent consumer sites landing in the codebase do NOT reopen P3. They are covered by the ongoing sweep discipline documented in PR #2967's Category A/B/C review process (P4's SC#1 machinery, applied analogously).
- New auto-disable trip events on dev do NOT reopen P3. They are the intended byproduct of the wired monitor and produce audit rows + log lines as evidence.
- OpsRunEvent baseline drift on dev does NOT reopen P3. Recalibration of `BASELINE_OPSRUNEVENT_DAILY` is future flag-flip preparation, not P3 rework.
- Unrelated Rigby delegation refactors do NOT reopen P3. They operate on the `RIGBY_DELEGATION_ENABLED` + kill-switch substrate P3 already established.
- P4 (`IB-1799-T1-02`) activity does NOT reopen P3. P4 is a separate intake with its own acceptance (PR #2973).

## 6. Remaining Work Classification

Every remaining item related to Arc I-0100 P3 is classified below. **No item is a local implementation blocker.**

| Item | Classification |
|------|----------------|
| Production canary of `RIGBY_DELEGATION_ENABLED=true` (mirror local smoke test with real dispatch traffic once prod exists) | Deferred until production exists |
| Production re-verification of A1–A6 gates at flag-flip time | Deferred until production exists |
| Production rollback drill | Deferred until production exists |
| Recalibration of `BASELINE_OPSRUNEVENT_DAILY` in `core/services/delegation_auto_disable.py:41` (address A6 drift before any future flag flip) | Deferred until production exists (future flag-flip preparation, not a current blocker) |
| Periodic beat task invocation of `check_delegation_auto_disable` (LOCAL-only regime uses on-demand management command; a beat task would only be needed in a multi-worker, flag-on environment) | Future enhancement |
| Emission-side wiring for `handler_exception` label rows, `execution_id`-detail lifecycle rows, and per-signature/per-trace error signature rows so the currently-dormant A6 signals (Stop Condition #1 measurements 2, 3, 4) fire meaningfully in the wild | Future enhancement |
| Optional ADR-0004 (ADR-C; D74 six-axis correlation-spine posture) | Future enhancement (F4 fold third-place; architecture-only, not required for P3 discharge) |
| Handoff phrasing cleanup once prod exists (drop "LOCAL-only" qualifier where appropriate) | Documentation improvement |

**No remaining implementation blockers for LOCAL.**

## 7. Arc Closure Recommendation

**Recommendation:** Move Arc I-0100 P3 from its current `IN_ARC — code-merged, flag-flip-blocked` state to a **`local-validated / production-deferred`** terminal state (mirroring the shape recommended for P4 in PR #2973 §7), and remove it from active engineering work.

Concretely:

- On merge of this acceptance PR, the P3 row in the runtime discharge table in `00-START-NEXT-SESSION.md` transitions from `IN_ARC` to a terminal status (e.g., `LOCAL_ACCEPTED_PROD_DEFERRED`) at the next handoff refresh, matching the shape used for P4.
- With both P3 and P4 in the same terminal state and P2 already `SHIPPED`, Arc I-0100 Stage 6 close criteria per IOS §4.5 ("every intake `SHIPPED / RETRACTED / DEFERRED / BLOCKED_ON_RESEARCH`") are satisfied under a `local-validated / production-deferred` interpretation — Stage 6 arc-close preparation becomes the next executable action, subject to Chris directive.
- Ratification of this recommendation is the merge of the PR carrying this file.

---

**End of Local Activation Acceptance package.**
