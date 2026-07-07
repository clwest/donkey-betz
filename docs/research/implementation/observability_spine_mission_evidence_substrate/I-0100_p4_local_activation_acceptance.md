---
title: "Arc I-0100 P4 — Local Activation Acceptance"
status: local-accepted
authority: arc-implementation-acceptance
arc_id: I-0100
arc_slug: observability_spine_mission_evidence_substrate
intake: IB-1799-T1-02
adr: ADR-0002
runtime_pr: 2955
async_fix_pr: 2970
handoff_refresh_pr: 2971
local_only_reality_pr: 2972
acceptance_pr: TBD
operating_model: local-only
ratifier: chris
ratification_mechanism: pr-merge
date_authored: 2026-07-07
scope: single-intake (P4 only; P3 IB-1799-T1-03 out of scope)
---

# Arc I-0100 P4 — Local Activation Acceptance

## 1. Executive Summary

Under the LOCAL-ONLY operating model formalized in PR #2972, Arc I-0100 P4 (intake `IB-1799-T1-02`; runtime PR #2955 with async-safe follow-up PR #2970) is **COMPLETE for local operation**.

"Complete" in this context means:

- Every runtime code change required to satisfy ADR-0002 has landed on `main` and is exercised by regression tests that reproduce the failure modes that produced them.
- Every stop condition for `PA_AGENT_EXECUTION_WRITE_ENABLED=True` has been locally verified.
- The default runtime posture (`PA_AGENT_EXECUTION_WRITE_ENABLED=false`) is deliberately unchanged and remains authoritative for the local platform.
- No production verification is applicable because no production deployment currently exists to verify against; per PR #2972's guardrail, future sessions must not attempt production verification unless Chris explicitly provides a live prod access path.
- No further engineering work is required for local operation.

"Complete" **does not** mean:

- The `PA_AGENT_EXECUTION_WRITE_ENABLED` flag has been flipped to `true` on any environment (local or otherwise).
- Production activation has been performed or attempted.
- The full Arc I-0100 (P2 + P3 + P4) is closed; this document scopes only P4. Arc I-0100 Stage 6 close remains blocked on P3 (`IB-1799-T1-03`) and is out of scope of this document.

## 2. Evidence Summary

### Stop Condition #1 — ~150-site `AgentExecution` consumer sweep + classification

- **Status:** discharge accepted per handoff carry-over.
- **Location of evidence:** Arc I-0100 scoping doc §5; Category-C consumer review at `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_p4_stop_condition_1_category_c_review.md`; direct-callsite sweep round 2 (excluding PA) merged as PR #2967.
- **Evidence type:** consumer classification bundle (Category A/B/C review) plus merged code sweep.

### Stop Condition #2 — Early-return path finalization decision

- **Status:** locally-verified after PR #2970.
- **Concrete evidence:** during the local canary (flag ON), 3 canary rows all landed `completed`; zero pending orphans observed.
- **Design source:** ADR-0002 §3.3 early-return finalize; runtime discharge PR #2968.

### Stop Condition #3 — `LLMCallEvent.execution_id` end-to-end join verification

- **Status:** locally-verified after PR #2970.
- **Concrete evidence:** during the local canary (flag ON), 3 `LLMCallEvent` rows joined 1:1 to 3 canary `AgentExecution` rows via `execution_id`.
- **Design source:** ADR-0002 §3.3 PA↔LLMCallEvent wiring (Option 1); runtime discharge PR #2969.

### Async write fix (PR #2970)

- **Root cause:** `_maybe_create_pa_turn_execution` / `_maybe_finalize_pa_turn_execution` were sync callables invoked from `async def process_message`, silently emitting `[PA_AGENT_EXECUTION_WRITE_DEGRADED]` on every PA turn and writing zero rows. Because `_pa_wrapped_enforce_real_ai` bypasses the LLM span when `pa_execution is None`, the ADR-0002 §3.3 join key also never populated — initially misread as a separate finding, actually a downstream symptom of the same defect.
- **Fix:** async wrappers hop the ORM writes to a worker thread via `sync_to_async`.
- **Commit on `main`:** `f7c283c3` (merged 2026-07-07 via `--admin --squash`).

### Local canary

- **Configuration:** `PA_AGENT_EXECUTION_WRITE_ENABLED=true` in the PA worker environment on `localhost:5432/unified_donkey_betz`.
- **Result:** 3 PA turns → 3 `AgentExecution` rows persisted `completed`; 3 `LLMCallEvent` rows joined 1:1 to those rows via `execution_id`; zero `[PA_AGENT_EXECUTION_WRITE_DEGRADED]` log lines; zero orphan rows. **ADR-0002 §3.3 join now demonstrably works end-to-end locally.**

### Rollback drill

- **Configuration:** `PA_AGENT_EXECUTION_WRITE_ENABLED=false` (default).
- **Result:** zero writes, zero events, zero warnings. Guard short-circuits before the write path, as designed. Rollback semantics are runtime-safe.

### Regression coverage

- **3 new tests** in `AsyncContextRegressionTests(TransactionTestCase)` exercise the async path from a real `asyncio.run(...)` loop, preventing the sync-in-async defect from regressing.
- **Combined suite:** `core.tests.test_tool_call_record_trace_id` + `core.tests.test_pa_agent_execution_write` + `core.tests.test_delegation_lifecycle_smoke_test` — 33/33 OK per SESSION_2699 handoff.

### Current default flag state

- `core/settings.py:173-174` — `PA_AGENT_EXECUTION_WRITE_ENABLED` is env-driven with default `'false'`.
- Unchanged by every PR in this arc; unchanged by PR #2972; unchanged by this acceptance PR. **Remains `false` at the time this acceptance document is authored.**

### Canonical PersonalAssistant row (local A1)

- **Migration:** `0377_arc_i0100_p4_canonical_pa_agent` applied on `localhost:5432/unified_donkey_betz` (`[X]` in `showmigrations core` output).
- **Row:** `id=c37a2f81-41d3-4ac5-bbf3-4c894c0b22c0`, `name='PersonalAssistant'`, `agent_type='meta'`, `specialization='personal_assistant'`, `is_active=True`.
- Re-verified 2026-07-07 (read-only ORM read; no writes).

## 3. Local Acceptance Decision

**ACCEPTED for LOCAL operation.**

Arc I-0100 P4 implementation is complete, locally validated, and safe to leave in its current shipped state (code on `main`, flag `false` by default). No further engineering action is required to consider P4 discharged under the local-only operating model. Ratification of this decision is the merge of the PR carrying this file.

## 4. Production Status

- **No production deployment currently exists.** The historical Railway URL (`donkey-betz-platform-production.up.railway.app`) returns 404 with `x-railway-fallback: true`; the Railway CLI is unauthenticated with no project link; `.env.production` contains a placeholder `DATABASE_URL`, not a live one.
- **Production activation has not been attempted.** No prod endpoint responded during any session in this arc; no prod DB was written to; no prod flag was flipped.
- **This is not a failure.** The absence of production is a platform-lifecycle state, not a defect of Arc I-0100 P4. All ADR-0002 requirements are met by the local artifacts.
- **Production validation is deferred until a production environment exists.** When production is stood up, activation validation reopens per the trigger in §5. Until then, per PR #2972's guardrail, no session should attempt prod verification unless Chris explicitly provides a live prod access path.

## 5. Future Trigger

Arc I-0100 P4 reopens if and only if:

> **A production deployment is created, or Chris explicitly requests production activation.**

No other event reopens this arc. Specifically:

- New PA-adjacent consumer sites landing in the codebase do NOT reopen P4. They are covered by the ongoing sweep discipline documented under Stop Condition #1 above.
- New `[PA_AGENT_EXECUTION_WRITE_DEGRADED]` log lines locally do NOT reopen P4. They are covered by the regression tests documented under Regression Coverage above.
- Unrelated PA rewrites or refactors do NOT reopen P4. They operate on the sync/async substrate P4 already established.
- P3 (`IB-1799-T1-03`) discharge activity does NOT reopen P4. P3 is a separate intake with its own stop-condition set.

## 6. Remaining Work Classification

Every remaining item related to Arc I-0100 P4 is classified below. **No item is a local implementation blocker.**

| Item | Classification |
|------|----------------|
| Production canary of `PA_AGENT_EXECUTION_WRITE_ENABLED=true` (mirror local canary once prod exists) | Deferred until production exists |
| Production A1 verification (migration 0377 applied on prod DB + canonical `PersonalAssistant` row present on prod) | Deferred until production exists |
| Production rollback drill | Deferred until production exists |
| Optional ADR-0004 (ADR-C; D74 six-axis correlation-spine posture) | Future enhancement (F4 fold third-place; architecture-only, not required for P4 discharge) |
| Handoff phrasing cleanup once prod exists (drop "LOCAL-only" qualifier where appropriate) | Documentation improvement |
| Future refactor of `_maybe_create_pa_turn_execution` / `_maybe_finalize_pa_turn_execution` into a shared async-safe helper if the sync-in-async pattern proves common elsewhere in the codebase | Technical debt (only if the pattern generalizes; no reopen trigger for P4 itself) |

**No remaining implementation blockers for LOCAL.**

## 7. Arc Closure Recommendation

**Recommendation:** Move Arc I-0100 P4 from its current `IN_ARC — code-merged + async-safe, flag-flip-blocked` state to a **`local-validated / production-deferred`** terminal state, and remove it from active engineering work.

Concretely:

- On merge of this acceptance PR, the P4 row in the runtime discharge table in `00-START-NEXT-SESSION.md` transitions from `IN_ARC` to a terminal status (e.g., `LOCAL_ACCEPTED_PROD_DEFERRED`) at the next handoff refresh.
- Arc I-0100 Stage 6 close remains **blocked on P3** (`IB-1799-T1-03`), which is out of scope of this document.
- Ratification of this recommendation is the merge of the PR carrying this file.

---

**End of Local Activation Acceptance package.**
