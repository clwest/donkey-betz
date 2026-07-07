# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0100 STAGE 4 IN FLIGHT; P2 SHIPPED + P4 CODE-MERGED-FLAG-BLOCKED; P3 NEXT

**Refreshed 2026-07-06 per IOS §15.15.**

### Phase

**`implementation`.** IOS `active v1.5` on `main`. Research paused per §15.3.

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`

### Current stage

- **Stage:** `2` (Stage 2 architecture complete; Stage 3 pre-flight running per-PR; runtime PRs shipping)
- **`stage_state`:** `active`

### Runtime discharge progress

| Intake | ADR | PR | Merged | Status | Flag |
|--------|-----|-----|--------|--------|------|
| **IB-1799-T1-01** (P2) | SPEC_COMPLETE (F3) | #2954 | 2026-07-06 | **SHIPPED** | `TOOL_CALL_TRACE_ID_ENFORCED=false` (default; flag-flip is operator decision) |
| **IB-1799-T1-02** (P4) | ADR-0002 | #2955 | 2026-07-06 | **IN_ARC — code-merged, flag-flip-blocked** | `PA_AGENT_EXECUTION_WRITE_ENABLED=false` (3 STOP CONDITIONS block flip) |
| **IB-1799-T1-03** (P3) | ADR-0003 | (not opened) | — | pending Stage 3 pre-flight assumption-lock gate | `RIGBY_DELEGATION_ENABLED=false` |
| **IB-1799-T0-01** (ADR-C track, F1 fold) | ADR-0004 (not authored) | — | — | admitted architecture-only | N/A |
| **IB-1799-T0-02** (retention input to ADR-C, F2 fold) | ADR-0004 (not authored) | — | — | conditional admit | N/A |

### P4 stop conditions (block flag flip to True — DO NOT set flag=true until all three discharged)

1. **~150-site `AgentExecution` consumer sweep.** Each site classified as (a) source-scoped correctly with `.exclude(input_data__source='pa')` OR (b) intentionally cross-source. Categorization pattern sampled in #2955 PR body.
2. **Early-return path finalization decision.** Chris directive OR Claude analysis on whether injection-blocked (line 721) and triage-mode (line 746) paths should also create AgentExecution rows.
3. **`LLMCallEvent.execution_id` end-to-end join verification.** Post-flag-flip Stage 5 verification confirms the correlation contract populates `execution_id` for PA-driven LLM calls per ADR-0002 §3.3.

Row IB-1799-T1-02 flips `IN_ARC → SHIPPED` only when Chris ratifies all three discharge + directs the flag flip.

### Next executable action

**Open P3 Stage 3 pre-flight** for IB-1799-T1-03 per Chris sequencing directive. Requires ADR-0003 §3.3.a 6-row assumption-lock table to pass:

1. `DELEGATION_ROUTING` cardinality == 1 (single-agent `monitor` → `TrendAnalysisAgent`).
2. Delegable-work-item daily cadence `< 10/day`.
3. Handler code (`rigby_delegation_signals.on_delegation_lifecycle`) unchanged since 2026-07-06.
4. `RIGBY_DELEGATION_ENABLED` remains sole runtime gate (no `MISSION_RUNNER_ENABLED` code references).
5. MissionRunner class contract unchanged (nine invariants I1-I9 per S1705 F1).
6. Existing 3-employee OpsRun/OpsRunEvent write path unaffected.

If all 6 pass: author P3 PR (`manage.py delegation_lifecycle_smoke_test` command + Phase 1 exercise + Phase 2 flag-flip trigger + auto-disable trigger implementation).

If any assumption fails: snap back to design-prep Option 2b full-3-phase per ADR-0003 §3.3 reversibility.

**Alternative next actions** (Chris sequencing dependent):

- **(a) Address a subset of P4 stop conditions.** Consumer sweep sampling / classification for a batch of the 150 sites; OR early-return path decision; OR LLMCallEvent wrapper contextvar work.
- **(b) Author ADR-0004 (ADR-C, optional per F4).** D74 six-axis correlation-spine posture. Architecture-only per F1 fold; requires standalone design-prep per IOS v1.5.
- **(c) Stage 6 arc-close preparation.** After all runtime discharges complete (SHIPPED), draft the arc canonical close doc.

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be` (label `ios-arc-open-I-0100`). No rotation. Retirement due at Stage 6 close.
- **Paused-research pin preserved:** `pa-44a6eb70d8814e34`.

### Pending PRs

| # | Title | State |
|---|-------|-------|
| **#TBD** (this housekeeping PR) | Arc I-0100 P4 merge annotations + BACKLOG update | `OPEN` (awaiting Chris review) |

Once #TBD merges, no other pending Arc I-0100 PRs until P3 Stage 3 pre-flight opens.

---

## Read as background (Level C step C.4–C.6 loads for P3 Stage 3 pre-flight opening)

- `docs/adr/ADR-0003-mission-runner-staged-enable-posture.md` §3.3.a assumption-lock table + §3.2 Phase 1 shadow-audit-synthetic command sketch.
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_a_mission_runner_staged_enable.md` (design-prep for full option analysis).
- `docs/research/implementation/BACKLOG.md` IB-1799-T1-03 row (`adr_ref: ADR-0003`; `pr_refs: pending P3`).
- Arc I-0100 scoping doc §5 P3 rollout + §7.3 R2/R3 risks + §8 F8-iii pattern.
- 1799 xx99 §1 point 3 + §8.2 T1 item 3 (Cat E OpsRun/OpsRunEvent design-intent-latent).
- `core/signals/rigby_delegation_signals.py` (handler; R3 dormancy target).
- `core/services/rigby_mission_delegation.py` (`delegate_work_item` + `DELEGATION_ROUTING`).
- `core/settings.py:138-140` (`RIGBY_DELEGATION_ENABLED` flag).
- IOS v1.5 §4.3 Stage 3 pre-flight + §5.1 pre-code gates.
- MEMORY rules (as usual).
- MEMORY project entry: `project_ios_v15_design_prep_first_class_codification_candidate` (SHIPPED).

---

## Session ready check (before P3 Stage 3 pre-flight opening)

1. **First tool call:** `context-kit orient`.
2. Verify housekeeping PR merged: `git log --oneline -5` includes this file's refresh.
3. Verify all Arc I-0100 accepted ADRs on main: `grep '^status: accepted' docs/adr/ADR-000{1,2,3}*.md` returns 3 matches.
4. Verify BACKLOG IB-1799-T1-01 SHIPPED, T1-02 IN_ARC-flag-blocked, T1-03 IN_ARC pending.
5. Verify both runtime flags OFF: `grep -E 'TOOL_CALL_TRACE_ID_ENFORCED|PA_AGENT_EXECUTION_WRITE_ENABLED' core/settings.py` — both env-driven, defaults `false`.
6. `tools/pa_local.sh "platform_config_tool action=overview"` — verify local context on arc pin.
7. Read ADR-0003 §3.3.a assumption-lock table in full + §3.2 smoke-test sketch.
8. Read IOS §4.3 Stage 3 pre-flight in full + §5.1 pre-code gates 1-10.
9. Run assumption-lock verification queries (all 6 read-only; no code changes yet):
   - `python -c "from core.services.rigby_mission_delegation import DELEGATION_ROUTING; print(len(DELEGATION_ROUTING), DELEGATION_ROUTING)"`
   - `python manage.py shell -c "from core.models_rigby_work_items import RigbyWorkItem; from django.utils import timezone; from datetime import timedelta; c = RigbyWorkItem.objects.filter(created_at__gte=timezone.now()-timedelta(days=30)).count(); print(f'30d cadence: {c/30:.2f}/day')"`
   - `git log --since=2026-07-06 -- core/signals/rigby_delegation_signals.py` — expect zero commits.
   - `grep -rn "MISSION_RUNNER_ENABLED" core/ agents/ | grep -v test_ | grep -v .md:` — expect zero code matches.
   - Run `test_mission_runner.MissionRunnerImportContractTests` — expect pass.
   - Baseline `OpsRun.objects.filter(created_at__gte=<30d>, ops_run_kind='mission').count()` — record for post-flag-flip comparison.
10. If all 6 assumption-lock gates pass: author P3 PR per ADR-0003 §3.1 Option 5 hybrid.
11. If any fail: STOP + report + snap back to design-prep Option 2b full-3-phase.
