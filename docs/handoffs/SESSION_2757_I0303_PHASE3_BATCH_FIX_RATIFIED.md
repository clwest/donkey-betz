# Session 2757 — I-0303 Phase 3 BATCH-FIX PR (First Pass, Non-Report-Driven) Ratified

**Date:** 2026-07-11
**Predecessor:** S2756 (I-0303 Phase 3 REPORT-ONLY substrate + REG-RISK wiring ratified; pin `pa-84d8a5a8987c439f` retired)
**Successor:** S2758 (multiple candidates — observation-window check, D2 canonical decision routing, D4 HIGH-RISK task file wiring extension, or net-new engineering per Chris directive)
**Session pin:** `pa-bb7f7567c6e34951` (label `i0303-phase3-smoke-then-batch`; **retired at S2757 close** per protocol)
**HEAD at open:** `0dd3905ee` (post-S2756 REPORT-ONLY merge)
**HEAD at close:** (filled at merge)

---

## §1 Delivery Ledger

Single 1-PR close-ceremony bundle per PLAYBOOK-7.4.1. Third phase-close under v0.5.0 discipline; second stage of PLAYBOOK-7.5.1 three-PR staged codification (REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP). This is the FIRST pass of BATCH-FIX (non-report-driven); a SECOND pass will consume observation-window findings later.

| # | PR | Merge SHA | Content |
|---|---|---|---|
| 1 | (this PR) | pending | Path C smoke validation + B1 payload strip + B2 dispatch conversion + apply_async_with_actor(user=None) widening + 4 new tests + ratification envelope + handoff + docs cascade + pin retire commentary |

---

## §2 Ratified Deliverables

### §2.1 Path C — Smoke validation of S2756 REPORT-ONLY substrate

Before drafting BATCH-FIX, validated substrate end-to-end in real Celery task dispatch context (`.apply()` eager mode):

- All 3 decorators applied at module load (attribute inspection verified)
- `summarize_conversation_task.apply(kwargs={'conversation_id': 'smoke-test-nonexistent-conv-id'})` → task state SUCCESS + body ran + `OpsRunEvent` envelope emitted with correct shape (`failure_kind='row_not_found'`, `model_label='ChatConversation'`, `support_code='RUR-TENANT-260711-b2b0'`, `reason_code='tenant_boundary_violation'`)
- Substrate works. BATCH-FIX authorized to proceed.

### §2.2 Substrate refinement (`core/security/task_enforcement.py`)

- `apply_async_with_actor(user=None)` now accepts None cleanly — omits `x-acting-user-id` header, still dispatches. Substrate then emits `missing_acting_identity` (correct anon-dispatch report-only outcome). B2 Watchpoint 1 addressed.
- Dual-source identity docstring paragraph (Rigby F4 EDIT) explains that some tasks intentionally keep payload `user_id` as bootstrap input; helper header is AUTHORIZATION identity; future cleanup must not strip payload without refactoring bootstrap flow.

### §2.3 B1 — Payload `user_id` stripping on `summarize_conversation_task`

- Facade signature (`tasks.py:13107`) + `_impl` (`tasks_conversations.py:3463`) — `user_id` kwarg removed
- Ownership re-derived from `ChatConversation.user_id` via `turns_qs.only('user_id', 'session_title').first()` (Q1 DB-row-derived)
- Downstream `create_deliverable(user_id=...)` + `ConversationMemory(user_id=...)` consume re-derived value
- Empty-conversation edge case: `user_id=None` fallback preserved
- Caller (`td_handlers_core.py:2113`) drops `user_id` kwarg

### §2.4 B2 — HTTP dispatch site conversion (4 sites → `apply_async_with_actor`)

- `views_personal_assistant.py:467` — process_pa_chat_task (payload user_id KEPT per bootstrap; header ADDED for authorization)
- `views_personal_assistant.py:612` — same pattern for @rigby-mention path
- `views/agents.py:155` — execute_agent with `execution.user` (may be None; helper handles cleanly)
- `td_handlers_core.py:2111` — summarize_conversation_task with `User.objects.filter(pk=user_id).first()` (None handled cleanly)

### §2.5 Test suite — +4 tests, 36/36 passing (192s runtime)

- `test_apply_async_with_actor_omits_header_when_user_is_none` — B2 Watchpoint 1
- `test_apply_async_with_actor_none_user_preserves_correlation_headers` — B2 Watchpoint 1 continuation
- `test_summarize_conversation_task_derives_user_from_conversation` — B1 unit test (monkey-patches LLM + create_deliverable + EmbeddingService)
- `test_summarize_conversation_task_empty_conversation_yields_no_deliverable` — B1 edge case

Backwards-compat: 32 previous tests (Phase 2 + Phase 3 REPORT-ONLY) all still pass.

### §2.6 Ratification envelope

`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md` — frozen canonical record with two Rigby SIGN turn logs + Chris D-verdict + observation window guidance + 5 explicit deferrals documented.

---

## §3 Rigby SIGN Cycle — two turns, all PASS

### §3.1 Design SIGN turn 1 (pre-code)

F1–F6 all PASS with 3 clarifications: F1 prefer `ChatConversation.user_id` direct; F4 header = authorization + payload = bootstrap only + mismatch warn-only; F6 watchpoints (user=None header omission + no new hard-fail + tests assert both).

Q leans confirmed on 5 axes (QA/QB/QC/QD/QE).

### §3.2 Implementation SIGN turn 1 (post-code)

F1–F6 all PASS with one non-blocking F4 EDIT (docstring bootstrap-vs-authorization note applied).

---

## §4 Chris D-Verdict — three ratification points

1. **Original Path B shape** — "approve"
2. **Post-code shape** — "approved, ship it"
3. **Final ship** — this record

Zero unresolved menus routed. Every decision converged Claude+Rigby first per S2753 agree-first rule.

---

## §5 Workflow Rules Exercised

### §5.1 Claude+Rigby agree-first (S2753 directive)

Two Rigby SIGN turns + three Chris D-verdict points. Zero unresolved menus presented to Chris.

### §5.2 Bias engineering / net-new builds over audit (S2745 close directive)

S2757 Path C (smoke test) validated substrate is real; Path B shipped non-report-driven BATCH-FIX (net-new dispatch site conversion + net-new B1 payload stripping semantics). Not an audit-of-existing session. Waited on P0.5 (freeze-mode routing) + P0.75 (CI billing) as background items — no engineering blocked.

### §5.3 Verify-before-build (Cycle 1A rule)

Before writing BATCH-FIX code, discovered TWO scope-narrowing constraints via read-of-actual-code:
1. `process_pa_chat_task` cannot cleanly strip payload `user_id` (chicken-and-egg with conversation creation) — deferred as D1.
2. AgentExecution has 1654 rows but NO `execution_id` field; AgentTaskExecution HAS the field. Migration is non-trivial — deferred as D2 pending Chris directive.

Both surfaced pre-code + folded into the SIGN cycle before any code was written.

### §5.4 Twin-canonical-representations (S2754a rule)

Phase 3 stage 2 first-pass ratification lands TWO deliverables in RUR-C1 workspace:

- Governance-truth: `RATIFICATION_20260711_i0303_phase3_batch_fix`
- Engineering-truth: `I-0303 — Phase 3 BATCH-FIX First Pass (mirror)`

Created via ORM-direct.

### §5.5 Docs cascade at every close (S1399 rule)

Full 4-step cascade at close: `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded` + `build_docs_provenance`. Chunk count evidence in PR body.

### §5.6 PLAYBOOK-7.4.1 close-ceremony 1-PR bundle

All artifacts land in ONE PR. Third phase-close under v0.5.0 discipline; pattern held cleanly.

### §5.7 PLAYBOOK-7.5.1 staged codification (Phase 3 stage 2 dogfooding)

First BATCH-FIX pass execution — non-report-driven. Second pass (report-driven) authorized to open when observation window accumulates findings. Precedent for splitting a PLAYBOOK-7.5.1 stage into multiple passes when observation window is required — likely codification candidate for a future Playbook amendment.

### §5.8 PLAYBOOK-7.6.1 SIGN watchpoint-attestation

Exercised TWICE this session (pre-code + post-code). All PASS.

### §5.9 `gh pr merge --admin` (feedback rule)

Merged with `--admin` posture — GitHub Actions billing still blocked. Rationale in PR body.

---

## §6 Session Timing + Cost

- Session open: 2026-07-11 (continued conversation post-S2756 close)
- First Rigby dispatch: after fresh pin mint (`pa-bb7f7567c6e34951`)
- Rigby SIGN turns: 2 (pre-code + post-code) — all PASS
- Chris D-verdicts: 3 (original shape / final ship / this record)
- Test suite: 1 run during authoring (192s combined 36/36; ≈ baseline)
- Path C smoke test: 1 run (< 5 seconds)
- Total local runtime: ~2 hours (very efficient — single-turn SIGN convergence)

Cost-threshold observation window (from S2753 baseline $6.66/$500): S2757 close TBD.

---

## §7 Second BATCH-FIX Pass Opening Guidance (Informative)

Second pass opens when production observation window accumulates findings. Charter shape:

- Query `OpsRunEvent.objects.filter(label='tenant_boundary_violation')` for accumulated events
- Group by `task_context.task_name` + `task_context.failure_kind`
- Resolve findings by class:
  - `missing_acting_identity` → dispatch sites we haven't converted (either HIGH-RISK task file targets from D4, or unauthenticated caller paths that should be `@system_scope` per Q2)
  - `predicate_rejected` → legitimate cross-tenant boundary breaches (this is what enforcement mode will hard-gate in stage 3)
  - `row_not_found` → dispatch-path lookup misses (may indicate legit bugs or missing lookup_field configuration)
  - `acting_user_not_found` → header-derived user pk doesn't resolve (stale sessions, dispatch-time race conditions)

Rigby SIGN + Chris D-verdict per stage discipline.

---

## §8 Provenance Chain

- **Predecessor session:** `docs/handoffs/SESSION_2756_I0303_PHASE3_REPORT_ONLY_RATIFIED.md`
- **Phase 3 stage 1 (REPORT-ONLY) ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`
- **Phase 2 substrate:** `core/security/task_enforcement.py` (ratified S2755)
- **Phase 2 ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md` (ratified S2754)
- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (ratified S2754)
- **Predicate module dependency:** `core/security/object_authz.py` (I-0302 Phase 2 ratified 2026-07-10)
- **Failure-Data Safety Contract:** `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` (ratified I-0301)
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (ratified S2753)
- **Ratification envelope (this session):** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md`
