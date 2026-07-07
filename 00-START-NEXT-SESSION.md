# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0100 STAGE 4 COMPLETE; P4 ASYNC-WRITE FIX MERGED (#2970); LOCAL CANARY PASSED; ARC PREPARING FOR CLOSE

**Refreshed 2026-07-07 post PR #2970 merge.**

### Session summary (2026-07-07 local canary loop)

Local canary of P4 (PR #2955) with `PA_AGENT_EXECUTION_WRITE_ENABLED=true`
surfaced a sync-in-async ORM defect: `_maybe_create_pa_turn_execution` /
`_maybe_finalize_pa_turn_execution` were pure sync but `process_message`
is `async def`. Every PA turn silently emitted
`[PA_AGENT_EXECUTION_WRITE_DEGRADED]` and wrote zero rows. Because
`_pa_wrapped_enforce_real_ai` bypasses the LLM span when
`pa_execution is None`, the ADR-0002 §3.3 join key also never populated —
initially read as a separate Finding 2, actually a downstream symptom.

- **PR #2970** merged 2026-07-07 (`f7c283c3`) via `--admin --squash`.
- Async wrappers hop ORM to worker thread via `sync_to_async`.
- 3 new tests in `AsyncContextRegressionTests(TransactionTestCase)`
  cover the async path from a real `asyncio.run(...)` loop.
- Local canary (flag ON) — 3 turns → 3 `AgentExecution` rows
  `completed`, 3 `LLMCallEvent` rows joined 1:1 via `execution_id`,
  zero DEGRADED lines, zero orphans. **§3.3 join now demonstrably
  works end-to-end.**
- Rollback drill (flag OFF) — zero writes, zero events, zero warnings.
  Guard short-circuits before the write path.
- A1 verified LOCAL only (migration 0377 applied on
  `localhost:5432/unified_donkey_betz` + canonical row present with
  `agent_type='meta'` + `specialization='personal_assistant'` after
  local UPDATE).
- **Prod untouched** — no Railway CLI, no prod URL, no prod DB, no
  prod flag change.
- `PA_AGENT_EXECUTION_WRITE_ENABLED` remains `false` by default
  (`core/settings.py:173-175` unchanged; PA worker env verified via
  `ps -E`).

### Phase

**`implementation`.** IOS `active v1.5` on `main`. Research paused per §15.3.

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`

### Current stage

- **Stage:** `2` (Stage 2 architecture + Stage 4 runtime PRs complete; Stage 5 verification per-PR done; Stage 6 close prep next)
- **`stage_state`:** `active`

### Runtime discharge — all 3 T1 PRs merged 2026-07-06; P4 async-write fix merged 2026-07-07

| Intake | ADR | PR(s) | Status | Flag |
|--------|-----|-----|--------|------|
| **IB-1799-T1-01** (P2) | SPEC_COMPLETE (F3) | #2954 | **SHIPPED** | `TOOL_CALL_TRACE_ID_ENFORCED=false` (Chris operator decision only) |
| **IB-1799-T1-02** (P4) | ADR-0002 | #2955 + **#2970** (async-write fix) | **IN_ARC** — code-merged + async-safe, flag-flip-blocked | `PA_AGENT_EXECUTION_WRITE_ENABLED=false` (3 STOP CONDITIONS locally-verified) |
| **IB-1799-T1-03** (P3) | ADR-0003 | #2957 | **IN_ARC** — code-merged, flag-flip-blocked | `RIGBY_DELEGATION_ENABLED=false` (4 STOP CONDITIONS) |

**Housekeeping PR #TBD** (this file's refresh) is the associated post-merge housekeeping for P3 + P4 canary.

### Deployment-state observation (memory-only per Chris directive)

Both P3 and P4 required an implicit intermediate state between "code merged" and "runtime activated" — a "code-merged, runtime intentionally blocked by deployment gates" state. IOS §2.2 status enum has no name for this. **Per Chris 2026-07-06 directive: four-trigger threshold applies. Do NOT propose IOS v1.6 until pattern surfaces in 2+ more independent arcs.** See memory entry `project_deployment_state_between_merged_and_active.md`.

### Stop conditions summary

**IB-1799-T1-02 (P4) — 3 stop conditions before `PA_AGENT_EXECUTION_WRITE_ENABLED=True`:**
1. ~150-site `AgentExecution` consumer sweep + classification. **Assumed complete per handoff carry-over.**
2. Early-return path finalization decision (injection blocked, triage mode). **Locally-verified after PR #2970**: 3 canary rows all landed `completed`, zero pending orphans.
3. `LLMCallEvent.execution_id` end-to-end join verification post-flag-flip. **Locally-verified after PR #2970**: 3 LLMCallEvent rows joined 1:1 to 3 canary AgentExecution rows.

_Note: All three are LOCAL-verified only. Prod A1 verification (migration 0377 applied on prod DB) still pending — prod URL was unreachable this session._

**IB-1799-T1-03 (P3) — 4 stop conditions before `RIGBY_DELEGATION_ENABLED=True`:**
1. Monitoring surface integration (`MONITORING_SURFACE_INTEGRATED=True` in `core/services/delegation_auto_disable.py`).
2. Phase 2 evidence bundle Chris review per ADR-0003 §3.1 F1.
3. Re-verification of A1-A6 assumption-lock gates at flag-flip time.
4. Ratified §3.1 F1 entry gate.

**IB-1799-T1-01 (P2)** — no stop conditions; SHIPPED under flag OFF.

### Next executable action

**Chris sequencing directive determines next action.** Candidate paths:

- **(a) Verify A1 on production DB.** Confirm migration 0377 applied on prod + canonical `PersonalAssistant` Agent row exists prod-side. Blocked this session because the Railway URL in `tools/pa_chat.py` returned 404 on every probe (`Server: railway-hikari`; `{"code":404,"message":"Application not found"}`) and no other prod entrypoint was available. Needs your action: either point me at the current prod URL, run `railway login && railway link && railway run python manage.py showmigrations core | grep 0377` yourself, or hand me an authenticated prod PA token + URL.
- **(b) P4 canary on prod after A1 verified.** Mirror the local canary once A1 is confirmed prod-side. Needs your explicit go-ahead on flag flip.
- **(c) Address P3 stop condition #1** (monitoring surface integration). Identify which monitoring/ops surface consumes `delegation_auto_disable` constants + wire actual flag-flip-to-False action on threshold breach.
- **(d) Author ADR-0004 (ADR-C, optional per F4).** D74 six-axis correlation-spine posture. Architecture-only per F1 fold; requires standalone design-prep per IOS v1.5. Ratifies with retention as INPUT per F2 fold.
- **(e) Stage 6 arc-close preparation.** Draft the arc canonical close doc `I-010099_observability_spine_implementation_close.md` per IOS §4.3 Stage 6. Note: Arc I-0100 close criteria per §4.5 requires every intake `SHIPPED/RETRACTED/DEFERRED/BLOCKED_ON_RESEARCH`. Currently 1 SHIPPED + 2 IN_ARC-flag-blocked. Close is blocked pending stop-condition discharge OR reclassification.

**My read:** P4 stop conditions #2 + #3 are locally-verified after PR #2970; the last local gate is discharge #1 acceptance (assumed complete per handoff). The natural next-executable action is **(a) prod A1 verification** — without that, no prod canary can start and P4 stays IN_ARC. Once A1 is confirmed prod-side, (b) becomes the operator-driven flag flip. ADR-C and Stage 6 close remain blocked on stop-condition discharge.

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be` (label `ios-arc-open-I-0100`). No rotation. Retirement due at Stage 6 close.
- **Paused-research pin preserved:** `pa-44a6eb70d8814e34`.

### Pending PRs

| # | Title | State |
|---|-------|-------|
| **#TBD** (this housekeeping PR) | Arc I-0100 post-P4-async-fix handoff refresh | `OPEN` (awaiting Chris review) |

No other Arc I-0100 PRs pending. Next PR opens on Chris sequencing directive (candidate: `feat(observability): Arc I-0100 P4 prod A1 verification` or the prod canary flip PR — flip is an operator action, not a code PR).

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
