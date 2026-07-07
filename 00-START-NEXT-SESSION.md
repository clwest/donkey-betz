# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0100 STAGE 4 COMPLETE; ALL 3 RUNTIME PRs MERGED; ARC PREPARING FOR CLOSE

**Refreshed 2026-07-06 per IOS §15.15.**

### Phase

**`implementation`.** IOS `active v1.5` on `main`. Research paused per §15.3.

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`

### Current stage

- **Stage:** `2` (Stage 2 architecture + Stage 4 runtime PRs complete; Stage 5 verification per-PR done; Stage 6 close prep next)
- **`stage_state`:** `active`

### Runtime discharge — all 3 T1 PRs merged 2026-07-06

| Intake | ADR | PR | Status | Flag |
|--------|-----|-----|--------|------|
| **IB-1799-T1-01** (P2) | SPEC_COMPLETE (F3) | #2954 | **SHIPPED** | `TOOL_CALL_TRACE_ID_ENFORCED=false` (Chris operator decision only) |
| **IB-1799-T1-02** (P4) | ADR-0002 | #2955 | **IN_ARC** — code-merged, flag-flip-blocked | `PA_AGENT_EXECUTION_WRITE_ENABLED=false` (3 STOP CONDITIONS) |
| **IB-1799-T1-03** (P3) | ADR-0003 | #2957 | **IN_ARC** — code-merged, flag-flip-blocked | `RIGBY_DELEGATION_ENABLED=false` (4 STOP CONDITIONS) |

**Housekeeping PR #TBD** (this file's refresh) is the associated post-merge housekeeping for P3.

### Deployment-state observation (memory-only per Chris directive)

Both P3 and P4 required an implicit intermediate state between "code merged" and "runtime activated" — a "code-merged, runtime intentionally blocked by deployment gates" state. IOS §2.2 status enum has no name for this. **Per Chris 2026-07-06 directive: four-trigger threshold applies. Do NOT propose IOS v1.6 until pattern surfaces in 2+ more independent arcs.** See memory entry `project_deployment_state_between_merged_and_active.md`.

### Stop conditions summary

**IB-1799-T1-02 (P4) — 3 stop conditions before `PA_AGENT_EXECUTION_WRITE_ENABLED=True`:**
1. ~150-site `AgentExecution` consumer sweep + classification.
2. Early-return path finalization decision (injection blocked, triage mode).
3. `LLMCallEvent.execution_id` end-to-end join verification post-flag-flip.

**IB-1799-T1-03 (P3) — 4 stop conditions before `RIGBY_DELEGATION_ENABLED=True`:**
1. Monitoring surface integration (`MONITORING_SURFACE_INTEGRATED=True` in `core/services/delegation_auto_disable.py`).
2. Phase 2 evidence bundle Chris review per ADR-0003 §3.1 F1.
3. Re-verification of A1-A6 assumption-lock gates at flag-flip time.
4. Ratified §3.1 F1 entry gate.

**IB-1799-T1-01 (P2)** — no stop conditions; SHIPPED under flag OFF.

### Next executable action

**Chris sequencing directive determines next action.** Candidate paths:

- **(a) Address P4 stop condition #1** (~150-site consumer sweep). Batchable; low risk. Progresses P4 toward SHIPPED.
- **(b) Address P4 stop condition #2** (early-return path decision). Small — either move create earlier in `process_message` OR add finalize at early-return sites. Progresses P4 toward SHIPPED.
- **(c) Address P3 stop condition #1** (monitoring surface integration). Identify which monitoring/ops surface consumes `delegation_auto_disable` constants + wire actual flag-flip-to-False action on threshold breach.
- **(d) Author ADR-0004 (ADR-C, optional per F4).** D74 six-axis correlation-spine posture. Architecture-only per F1 fold; requires standalone design-prep per IOS v1.5. Ratifies with retention as INPUT per F2 fold.
- **(e) Stage 6 arc-close preparation.** Draft the arc canonical close doc `I-010099_observability_spine_implementation_close.md` per IOS §4.3 Stage 6. Note: Arc I-0100 close criteria per §4.5 requires every intake `SHIPPED/RETRACTED/DEFERRED/BLOCKED_ON_RESEARCH`. Currently 1 SHIPPED + 2 IN_ARC-flag-blocked. Close is blocked pending stop-condition discharge OR reclassification.

**My read:** Chris's sequencing directive is authoritative. P3 + P4 stop conditions are the natural next work — they progress two IN_ARC rows toward SHIPPED. ADR-C is optional and can be deferred to arc close prep. Stage 6 arc close is blocked until stop conditions discharge.

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be` (label `ios-arc-open-I-0100`). No rotation. Retirement due at Stage 6 close.
- **Paused-research pin preserved:** `pa-44a6eb70d8814e34`.

### Pending PRs

| # | Title | State |
|---|-------|-------|
| **#TBD** (this housekeeping PR) | Arc I-0100 P3 merge annotations | `OPEN` (awaiting Chris review) |

Once #TBD merges, no other Arc I-0100 PRs pending. Next PR opens on Chris sequencing directive.

---

## Arc I-0100 implementation dependency graph (post-merge state)

```
ADR-0001 (accepted) ────┐
ADR-0002 (accepted) ─┐  │
ADR-0003 (accepted) ─┼──┼─── P2 (#2954, SHIPPED) — no stop conditions
                     │  │       │
                     │  │       └── P4 (#2955, IN_ARC-flag-blocked)
                     │  │             └── 3 stop conditions gate `PA_AGENT_EXECUTION_WRITE_ENABLED=True`
                     │  │
                     │  └────── P3 (#2957, IN_ARC-flag-blocked)
                     │                └── 4 stop conditions gate `RIGBY_DELEGATION_ENABLED=True`
                     │
                     └────── ADR-C (not authored; optional per F4; architecture-only track)
```

**Stage 4 exit gate per IOS §4.3:** "Every planned PR merged; every regression test green." — **SATISFIED** (P2 + P4 + P3 all merged; combined 33/33 tests pass).

**Stage 6 arc-close criteria per IOS §4.5:** "Every intake item admitted at Stage 1 has status SHIPPED, RETRACTED, DEFERRED, or BLOCKED_ON_RESEARCH." — **NOT YET SATISFIED**. Two rows remain IN_ARC-flag-blocked.

Path to close:
1. Discharge P3 + P4 stop conditions → row flips to SHIPPED, OR
2. Reclassify P3 + P4 as DEFERRED (with runtime activation as a follow-on arc's discharge), OR
3. Ratify a new arc-close-permitted state (e.g., "code-merged, activation deferred").

Chris sequencing directive determines path.

---

## Read as background

- All 3 accepted ADRs: `docs/adr/ADR-000{1,2,3}*.md`
- All 2 design-prep artifacts: `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_{b,a}_*.md`
- Arc I-0100 scoping doc §5 planned PR sequence + §7.3 risks + §8 F-folds + §9.3 verification interface.
- All 3 runtime PRs merged: #2954 (P2), #2955 (P4), #2957 (P3).
- P4 stop conditions: `#2955 PR body Pre-flag-flip requirements section`.
- P3 stop conditions: `#2957 PR body Pre-flag-flip requirements section` + `core/services/delegation_auto_disable.py`.
- 1799 xx99 §1 verdicts + §2.5 Cat E evidence.
- IOS v1.5 §4.3 Stage 6 close + §4.5 arc graduation criteria + §5.3 post-merge gates.
- MEMORY rules (as usual).
- **MEMORY project entry:** `project_deployment_state_between_merged_and_active.md` (2 triggers so far; four-trigger threshold).

---

## Session ready check (before next action)

1. **First tool call:** `context-kit orient`.
2. Verify housekeeping PR merged: `git log --oneline -5` includes #TBD.
3. Verify all 3 runtime PRs on main via `git log --oneline | head -10`.
4. Verify all 3 runtime flags OFF: `grep -E 'TOOL_CALL_TRACE_ID_ENFORCED|PA_AGENT_EXECUTION_WRITE_ENABLED|RIGBY_DELEGATION_ENABLED' core/settings.py` — all env-driven `false` defaults.
5. Verify combined test suite green: `python manage.py test core.tests.test_tool_call_record_trace_id core.tests.test_pa_agent_execution_write core.tests.test_delegation_lifecycle_smoke_test --keepdb` — expect 33/33 OK.
6. Read Chris sequencing directive from prior session.
7. If directive names one of the 5 candidate next actions above (a-e), execute per that action's Stage 3 pre-flight discipline. If ambiguous, ask.
