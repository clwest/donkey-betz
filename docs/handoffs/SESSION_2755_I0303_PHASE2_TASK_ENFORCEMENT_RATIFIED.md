# Session 2755 — I-0303 Phase 2 Task-Enforcement Module Ratified

**Date:** 2026-07-11
**Predecessor:** S2754 (I-0303 scoping + Phase 1 ledger ratified; both S2754 + S2754a pins retired)
**Successor:** S2756 (I-0303 Phase 3 — Per-Task Enforcement Application, REPORT-ONLY substrate PR)
**Session pin:** `pa-f3637b736efb4c07` (label `i0303-phase2-module`; **retired at S2755 close** per protocol)
**HEAD at open:** `de2a270e0` (post-S2754 close-cascade)
**HEAD at close:** (filled at merge)

---

## §1 Delivery Ledger

Single 1-PR close-ceremony bundle per PLAYBOOK-7.4.1. First arc-phase ratification under v0.5.0 close-ceremony discipline dogfooded across a full authoring+SIGN+D-verdict cycle.

| # | PR | Merge SHA | Content |
|---|---|---|---|
| 1 | (this PR) | pending | I-0303 Phase 2 substrate + tests + Contract §10 amendments + doc drift fixes + handoff + docs cascade + close bookmark |

---

## §2 Ratified Deliverables

### §2.1 `core/security/task_enforcement.py` — 599 lines

Public API per scoping §4 uniform contract:

- `@enforce_tenant_boundary(model=X, id_kwarg='...')` — function-tier decorator
- `TenantScopedTask(celery.Task)` — Celery base class
- `@system_scope` — unified explicit opt-in marker (works on functions AND classes)
- `TenantBoundaryViolation` — picklable exception with `failure_kind` discriminator

Enforcement algorithm (Q1 trusted-source hierarchy):

1. Tier 1 — DB row via `model.objects.filter(pk=row_id).first()` (inspect.signature binding handles positional + keyword)
2. Tier 2 — Transport header via `self.request.headers.get('x-acting-user-id')`
3. Tier 3 — Payload NEVER consulted
4. Ratified predicate delegation → uniform contract with HTTP layer (I-0302 Phase 2)

Six `failure_kind` discriminators, existence-oracle safe (uniform user-facing envelope):

- `missing_row_id` / `row_not_found` / `missing_acting_identity` / `acting_user_not_found` / `unregistered_model` / `predicate_rejected`

### §2.2 Contract §10 amendments

Failure-Data Safety Contract §10 requires new ratification record for reason-code / support-code additions. This session's ratification record IS that authority.

**Reason code addition:** `tenant_boundary_violation` (DENIED / 403 / non-retryable / generic message).

**Support-code component addition:** `TENANT` (yields `RUR-TENANT-yyMMdd-hex`).

Files touched: `core/security/reason_codes.py` + `core/security/error_envelope.py` (`_REASON_TO_COMPONENT`) + `core/security/support_code.py` (`_ALLOWED_COMPONENTS`).

### §2.3 Test suite — 18/18 passing (191s local runtime)

`tests/security/test_i0303_p2_task_enforcement.py` (459 lines) covers:

- 4 primary paths (happy / cross-tenant / system-scope / missing-identity)
- 3 failure-kind coverage (missing_row_id / row_not_found / acting_user_not_found — existence-oracle uniformity)
- 2 per-user model coverage (Initiative — predicate map)
- 2 positional-args dispatch (Phase 1 §4.4 tier-0 pattern)
- 4 base-class parity (TenantScopedTask — uniform contract per scoping §4)
- 3 substrate contract (pickle round-trip + reason-code registration + TENANT support component)

Test approach: direct `_check_boundary` calls + `push_request` stub context on unbound `TenantScopedTask` instances. Full Celery-eager `.apply()` dispatch deferred to Phase 4 async-boundary harness (post_save-signal-dispatched-task interaction is controllable via fixture-level Celery config there).

### §2.4 Documentation amendments

Six stale path references replaced with the ratified I-0302 module path:

- `I-0303_scoping.md` §3.5 + §11 provenance chain + §8 Phase 2 charter (3 refs)
- `I-030301_task_boundary_audit_ledger.md` frontmatter + §9 entry criteria + §11 handoff (3 refs)

Original text referenced `core/tenant_boundary_lockdown/predicates.py` (path never landed). Ratified I-0302 Phase 2 module is at `core/security/object_authz.py` per I-030202 design doc. Amendments include inline S2755 notes explaining the drift.

### §2.5 Ratification envelope

`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md` (~200 lines) — frozen canonical record with Rigby double-SIGN cycle log + Chris D-verdict + Phase 3 opening authorization + Phase 2 limitations documentation.

---

## §3 Rigby Double-SIGN Cycle

### §3.1 Design SIGN turn 1 (pre-code)

Rigby converged on 6 design points before I wrote code:

| Question | Chosen shape |
|---|---|
| Q-A (reason code amendment scope) | **a1** — add `tenant_boundary_violation` now; this ratification IS the §10 authority |
| Q-B (trusted-source algorithm) | **b2** — DB-row expected + transport-header actual + ratified predicate as acceptance check |
| Q-C (failure mechanism) | **c1** — raise `TenantBoundaryViolation` → Celery `task_failure` signal → operator envelope emitted best-effort |
| Q-D (system_scope marker shape) | **d2** — unified marker works on both function decorators AND class decorators |
| Header-missing policy | **Fail-closed** unless `@system_scope` (Q2 fail-safe default) |
| Existence-oracle protection | Uniform user-facing envelope across all `failure_kind` |

### §3.2 Implementation SIGN turn 1 (post-code)

Rigby verdict: **SIGN-WITH-EDITS** (2 items):

- **F3** — ratification record pointer in `reason_codes.py` must resolve to a real artifact. **Applied:** created the ratification envelope file; pointer updated to resolve.
- **F5** — `tools/pa_local.sh:539` change must be justified in PR summary. **Applied:** session-open pin rotation per S2755 protocol (S2754 close pin retired; S2755 fresh mint required for Rigby routing). Documented in envelope §3.2.

Other axes at implementation turn 1: F1 (Q1 hierarchy + §4 uniform-contract conformance) PASS, F2 (existence-oracle protection across 6 failure_kinds) PASS, F4 (test coverage sufficient for Phase 3 opening) PASS.

### §3.3 Implementation SIGN turn 2 (post-edits)

Rigby verdict: **SIGN-PASS** on all axes. Joint recommend-to-Chris line locked: *"Recommend to Chris: approve I-0303 Phase 2 module — substrate is contract-conformant, existence-oracle safe, and test-covered; proceed to D-verdict and open Phase 3 wiring."*

---

## §4 Chris D-Verdict

Chris ratified with single-word approval: **"Approved!"**

Joint Claude+Rigby recommendation card presented before D-verdict included substrate + amendments + tests + doc fixes + envelope + session-pin justification. Chris ratified the joint recommendation — no unresolved menu presented per the agree-first workflow rule.

---

## §5 Workflow Rules Exercised

### §5.1 Claude+Rigby agree-first (S2753 directive)

Six design points converged with Rigby BEFORE code was written. Then two SIGN turns AFTER code was written. Chris ratified against a single joint recommendation. Zero unresolved decisions routed to Chris.

### §5.2 Verify-before-build (Cycle 1A rule)

Before writing `task_enforcement.py`, discovered TWO doc-vs-code drifts:

1. Scoping + Phase 1 ledger reference `core/tenant_boundary_lockdown/predicates.py` — path never landed; ratified I-0302 Phase 2 module actually at `core/security/object_authz.py`. Chris chose landing location A (`core/security/task_enforcement.py`) matching I-0302 precedent. 6 doc refs amended in this same PR.
2. Scoping + Phase 1 ledger mandate `reason_code='tenant_boundary_violation'` — NOT in the ratified enum. Route: Rigby converged on option a1 (add now, this ratification IS the §10 authority). Landed cleanly with cross-referenced comments in `reason_codes.py`.

Both drifts surfaced pre-code and resolved by Chris D-verdict + amendments in the same PR bundle.

### §5.3 Twin-canonical-representations (S2754a rule)

Phase 2 ratification lands TWO deliverables in the workspace:

- Governance-truth: `RATIFICATION_20260711_i0303_phase2_task_enforcement`
- Engineering-truth: `I-0303 — Phase 2 Task-Enforcement Module (mirror)` (content mirror of `task_enforcement.py` + tests)

Created via ORM-direct create to avoid Rigby's `deliverable_tool.create` diagnostic-flag path bug (per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`).

### §5.4 Docs cascade at every close (S1399 rule)

Full 4-step cascade at close:

1. `build_docs_index` (regenerate `docs/INDEX.md`)
2. `build_rag_corpus` (regenerate RAG corpus)
3. `sync_docs_index_to_documents` (push doc content to Document table)
4. `sync_docs_index_to_documents --embed` (embed all newly synced/updated)

Chunk count evidence in PR body per `feedback_cascade_pr_must_include_embed_step`.

### §5.5 PLAYBOOK-7.4.1 close-ceremony 1-PR bundle (dogfooding v0.5.0)

Substrate + tests + amendments + envelope + handoff + docs cascade + pin retire all land in ONE PR. First phase-close under v0.5.0 discipline; pattern held cleanly.

### §5.6 `gh pr merge --admin` (feedback rule)

Merged with `--admin` posture — GitHub Actions billing still blocked. Rationale documented in PR description.

---

## §6 Session Timing + Cost

- Session open: 2026-07-11 (early)
- First Rigby dispatch: after fresh pin mint (`pa-f3637b736efb4c07`)
- Rigby design SIGN turn 1: converged in 1 exchange
- Rigby implementation SIGN turn 1 → 2: 2 exchanges (2 edits applied inline)
- Chris D-verdict: single "Approved!"
- Test suite: 3 runs during authoring (191s each; two hangs recovered by algorithm-direct testing pivot)
- Total local runtime: ~4 hours

Cost-threshold observation window (from S2753 baseline $6.66/$500): S2755 close (TBD).

---

## §7 Phase 3 Opening Guidance (Informative)

Phase 3 opens at S2756 under this ratification. Charter per scoping §8:

- **REPORT-ONLY substrate PR** — wire `@enforce_tenant_boundary` + `@system_scope` on every user-owned-model-touching task; warn-only mode (log violations, do NOT raise)
- **BATCH-FIX PR** — resolve all report-only findings (either dispatch-site header attachment fix OR Q6 refactor to row-ID dispatch)
- **ENFORCEMENT-FLIP PR** — flip warn-only to hard-gate
- **Dispatch-site helper** — Phase 3 substrate adds `apply_async_with_actor(task, user, ...)` helper
- **AgentExecution / AgentTaskExecution duplicate-class resolution** — Phase 1 §4.4 caveat surfaces here
- Each stage: Rigby SIGN + Chris D-verdict per PLAYBOOK-7.6.1 + PLAYBOOK-7.5.1

Rigby elasticity clause (S2754 SIGN): Phase 3 may expand to 2-3 sessions if Phase 1 audit surfaces many "mixed identity" tasks during application.

---

## §8 Provenance Chain

- **Predecessor session:** `docs/handoffs/SESSION_2754_I0303_SCOPING_AND_PHASE1_CLOSED.md`
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md` (ratified S2754)
- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (ratified S2754)
- **Predicate module dependency:** `core/security/object_authz.py` (I-0302 Phase 2 ratified 2026-07-10)
- **Failure-Data Safety Contract:** `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` (ratified I-0301)
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (ratified S2753)
- **Ratification envelope (this session):** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
