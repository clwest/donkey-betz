# Session 2756 — I-0303 Phase 3 REPORT-ONLY Substrate + REG-RISK Wiring Ratified

**Date:** 2026-07-11
**Predecessor:** S2755 (I-0303 Phase 2 substrate ratified; pin `pa-f3637b736efb4c07` retired)
**Successor:** S2757 (I-0303 Phase 3 stage 2 — BATCH-FIX PR authoring)
**Session pin:** `pa-84d8a5a8987c439f` (label `i0303-phase3-report-only`; **retired at S2756 close** per protocol)
**HEAD at open:** `387b73ad1` (post-S2755 Phase 2 merge)
**HEAD at close:** (filled at merge)

---

## §1 Delivery Ledger

Single 1-PR close-ceremony bundle per PLAYBOOK-7.4.1. Second arc-phase ratification under v0.5.0 close-ceremony discipline; first stage of PLAYBOOK-7.5.1 three-PR staged codification (REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP).

| # | PR | Merge SHA | Content |
|---|---|---|---|
| 1 | (this PR) | pending | I-0303 Phase 3 REPORT-ONLY substrate widening + 3 REG-RISK exemplar wiring + 14 new tests + ratification envelope + handoff + docs cascade + pin-retire commentary |

---

## §2 Ratified Deliverables

### §2.1 `core/security/task_enforcement.py` — substrate widening (~+150 lines)

Four additions layered on Phase 2:

- **`warn_only=False` kwarg** on `@enforce_tenant_boundary` + class attr on `TenantScopedTask`. Catches ONLY `TenantBoundaryViolation`; other exceptions propagate (Rigby GUARDRAIL-1). Same envelope shape as enforcement mode via parallel emission path `_emit_warn_only_envelope`.
- **`lookup_field='pk'` kwarg** on both. `_check_boundary` uses `model.objects.filter(**{lookup_field: row_id})`. Default `'pk'` preserves Phase 2 backwards-compat.
- **`apply_async_with_actor(task, user, *, args=(), kwargs=None, headers=None, **options)` helper.** `setdefault` merge — correlation headers preserved; caller wins on explicit `x-acting-user-id` collision.
- **Local shim predicate `can_read_agent_task_execution`** in `_get_predicate_for_model` — loudly TEMPORARY per Phase 1 §4.4 (Q2 register-both). Fail-safe on `row.user_id is None`.

### §2.2 REG-RISK exemplar wiring (3 tasks, `warn_only=True`)

Decorator placement is BELOW `@shared_task` (Celery wraps outermost). `lookup_field` is required because task IDs are natural-key CharFields, not PKs.

- **`execute_agent`** (`core/tasks_agents.py:493`) — `model=AgentTaskExecution, id_kwarg='execution_id', lookup_field='execution_id'`
- **`process_pa_chat_task`** (`core/tasks.py:11947`) — `model=ChatConversation, id_kwarg='conversation_id', lookup_field='conversation_id'` (highest-traffic 924 runs/7d per Phase 1 §3)
- **`summarize_conversation_task`** (`core/tasks.py:13107`) — same as process_pa_chat_task

### §2.3 Test suite — +14 tests, 32/32 passing (193s runtime)

`tests/security/test_i0303_p2_task_enforcement.py` extended. New coverage: warn-only mode axes (C1/C2/C4 + baseclass parity), `apply_async_with_actor` axes (C3/C3b/C3c), `lookup_field` widening axes (natural-key happy + cross-tenant + backwards-compat), AgentTaskExecution shim predicate axes (registered + matches + rejects + null-user-fail-safe).

Backwards-compat verified: all 18 Phase 2 tests still pass unchanged. +2s runtime for +14 tests.

### §2.4 Ratification envelope

`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md` (~370 lines) — frozen canonical record with three Rigby SIGN turn logs + Chris D-verdict (three ratification points) + Phase 3 stage 2 opening authorization + Phase 3 stage 1 limitations documentation.

---

## §3 Rigby SIGN Cycle — three turns, all PASS

### §3.1 Design SIGN turn 1 (pre-code)

F1–F6 all PASS. Q leans agreed: Q1 one PR · Q2 register both AgentExecution + AgentTaskExecution · Q3 reuse operator envelope · Q4 ship helper in REPORT-ONLY · Q5 extend Phase 2 test file.

Two accepted edits:

- **F2 EDIT-1:** `apply_async_with_actor` merges caller headers (not overwrite); caller wins on `x-acting-user-id` collision.
- **GUARDRAIL-1:** warn-only wrapper catches ONLY `TenantBoundaryViolation`; other exceptions propagate.

### §3.2 Substrate-amendment SIGN (post-code-gap discovery)

Discovered pre-code during read of the 3 REG-RISK target bodies: all use non-PK CharField natural keys. Phase 2 substrate cannot reach these rows.

QA/QB/QC/QD all PASS. One accepted edit:

- **QB EDIT-2:** local shim predicate comment must be loudly TEMPORARY. Applied as inline `# TODO(I-0303 BATCH-FIX): ...` at the shim definition.

### §3.3 Implementation SIGN turn 1 (post-code)

F1–F6 all PASS. One micro-EDIT (PR-body clarity — no code change): explain decorator-below-@shared_task placement + why `lookup_field` is required (natural-key IDs).

---

## §4 Chris D-Verdict — three ratification points

1. **Original PR shape** — "approve" (open PR authorized)
2. **Amended substrate delta** — "approved" (lookup_field widening + shim predicate + expanded test coverage authorized)
3. **Final ship** — "approved, ship it" (post-code SIGN-PASS + close-ceremony bundle authorized)

Zero unresolved menus routed. Every decision converged Claude+Rigby first per S2753 workflow rule.

---

## §5 Workflow Rules Exercised

### §5.1 Claude+Rigby agree-first (S2753 directive)

Three Rigby SIGN turns + three Chris D-verdict points across the session. Zero unresolved menus presented to Chris; every decision converged Claude+Rigby first.

### §5.2 Verify-before-build (Cycle 1A rule)

Before writing substrate code, discovered a substrate GAP: the 3 REG-RISK exemplars all dispatch on natural-key CharFields, not PKs. Phase 2 substrate couldn't reach the rows. Resolution: `lookup_field` kwarg widening, ratified as within-REPORT-ONLY discipline. Discovered pre-code and routed through Rigby SIGN before any code was written.

### §5.3 Twin-canonical-representations (S2754a rule)

Phase 3 stage 1 ratification lands TWO deliverables in RUR-C1 workspace:

- Governance-truth: `RATIFICATION_20260711_i0303_phase3_report_only`
- Engineering-truth: `I-0303 — Phase 3 REPORT-ONLY Substrate + REG-RISK Wiring (mirror)` (content mirror of substrate + wiring diff + test file)

Created via ORM-direct to avoid `deliverable_tool.create` diagnostic-flag path bug.

### §5.4 Docs cascade at every close (S1399 rule)

Full 4-step cascade at close: `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `sync_docs_index_to_documents --embed` (+ `build_docs_provenance`). Chunk count evidence in PR body per `feedback_cascade_pr_must_include_embed_step`.

### §5.5 PLAYBOOK-7.4.1 close-ceremony 1-PR bundle

Substrate + wiring + tests + envelope + handoff + docs cascade + pin retire all land in ONE PR. Second phase-close under v0.5.0 discipline; pattern held cleanly.

### §5.6 PLAYBOOK-7.5.1 staged codification (Phase 3 dogfooding)

First stage-1 (REPORT-ONLY) execution under the v0.5.0 three-PR staged codification rule. Stage 2 (BATCH-FIX) authorized to open at S2757.

### §5.7 PLAYBOOK-7.6.1 SIGN watchpoint-attestation

Exercised THREE times this session (pre-code + substrate-amendment + post-code). All PASS with additive edits folded cleanly.

### §5.8 PLAYBOOK-6.10.3 close-cycle watchpoint

Substrate-gap discovery documented as a close-cycle watchpoint hit — Phase 2 substrate constraint only visible at Phase 3 application. Not a Phase 2 defect; resolution ratified as within-REPORT-ONLY discipline.

### §5.9 `gh pr merge --admin` (feedback rule)

Merged with `--admin` posture — GitHub Actions billing still blocked. Rationale in PR body.

---

## §6 Session Timing + Cost

- Session open: 2026-07-11 (post-S2755 Phase 2 merge)
- First Rigby dispatch: after fresh pin mint (`pa-84d8a5a8987c439f`)
- Rigby SIGN turns: 3 (design pre-code / substrate-amendment / implementation post-code) — all PASS
- Chris D-verdicts: 3 (original shape / amended delta / final ship)
- Test suite: 2 runs during authoring (191s Phase 2 baseline + 193s Phase 2+3 combined; +2s for +14 tests)
- Total local runtime: ~3 hours (efficient — SIGN convergence single-turn each)

Cost-threshold observation window (from S2753 baseline $6.66/$500): S2756 close TBD.

---

## §7 Phase 3 Stage 2 (BATCH-FIX) Opening Guidance (Informative)

Stage 2 opens at S2757 under this ratification. Charter per scoping §8 + PLAYBOOK-7.5.1:

- **Report-driven fix scope.** Let REPORT-ONLY substrate collect violations from the 3 wired REG-RISK exemplars in production observation window. BATCH-FIX PR resolves every observed violation.
- **Payload `user_id` stripping** on `summarize_conversation_task` + `process_pa_chat_task` — Phase 1 §5.1 Q1 explicit violation targets.
- **AgentExecution vs AgentTaskExecution canonical decision** — Phase 1 §4.4 duplicate-class caveat. Shim predicate retirement follows.
- **HTTP dispatch site conversion** — every caller of the 3 REG-RISK tasks converted to `apply_async_with_actor(task, user, ...)`.
- **Extend warn-only wiring** to remaining HIGH-RISK task files per Phase 1 §3 bucketing (`tasks_initiatives.py`, `tasks_content.py`, `tasks_media.py`, `tasks_misc.py`).
- Rigby SIGN + Chris D-verdict per per-stage discipline.

Stage 3 (ENFORCEMENT-FLIP) requires separate ratification.

---

## §8 Provenance Chain

- **Predecessor session:** `docs/handoffs/SESSION_2755_I0303_PHASE2_TASK_ENFORCEMENT_RATIFIED.md`
- **Phase 2 substrate:** `core/security/task_enforcement.py` (ratified S2755)
- **Phase 2 ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md` (ratified S2754)
- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (ratified S2754)
- **Predicate module dependency:** `core/security/object_authz.py` (I-0302 Phase 2 ratified 2026-07-10)
- **Failure-Data Safety Contract:** `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` (ratified I-0301)
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (ratified S2753)
- **Ratification envelope (this session):** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`
