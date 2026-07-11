---
title: "I-0303 Phase 2 Task-Enforcement Module Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2755
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design → implementation) + Chris joint-recommend D-verdict
program_id: RUR
parent_arc: I-0303
parent_arc_phase: Phase 2 (Decorator + Base-Class Implementation)
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
parent_scoping_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md
parent_phase1_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md
sibling_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_safety_contract.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md
ratified_documents:
  - core/security/task_enforcement.py
  - core/security/reason_codes.py (amended — tenant_boundary_violation added)
  - core/security/error_envelope.py (amended — _REASON_TO_COMPONENT extension)
  - core/security/support_code.py (amended — TENANT component allowlist extension)
  - core/security/__init__.py (unchanged — future extension deferred to Phase 3 wiring)
  - tests/security/test_i0303_p2_task_enforcement.py (18 tests, 191s runtime)
  - docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md (amended — 4 stale path refs)
  - docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md (amended — 2 stale path refs)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
contract_10_amendments:
  - reason_code addition: tenant_boundary_violation (per Failure-Data Safety Contract §10)
  - support_code component addition: TENANT (per Failure-Data Safety Contract §10)
sign_sessions:
  - S2755 — Rigby design SIGN turn 1 (pre-code): converged on 6 design points (Q-A a1 / Q-B b2 / Q-C c1 / Q-D d2 + fail-closed header policy + predicate-delegation)
  - S2755 — Rigby implementation SIGN turn 1 (post-code): SIGN-WITH-EDITS (F3 + F5)
  - S2755 — Rigby implementation SIGN turn 2 (post-edits): SIGN-PASS on all axes (F1..F5)
supersedes: none (first I-0303 Phase 2 ratification)
frozen: true
arc_state:
  phase_1_task_boundary_audit_ledger: closed (S2754)
  phase_2_task_enforcement_module: closed (this record)
  phase_3_per_task_enforcement_application: authorized_to_open
  phase_4_async_boundary_regression_harness: pending
  phase_5_arc_close: pending
  arc_status: OPEN (Phase 2 CLOSED; Phase 3 authorized to open)
test_results:
  local_test_count: 18
  local_test_pass_rate: "18/18"
  local_test_runtime_seconds: 191
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 CLOSED 2026-07-10; I-0302 CLOSED 2026-07-10; I-0303 Phase 2 CLOSED (this record); RUR-C1 remains OPEN pending I-0303 arc close
---

# I-0303 Phase 2 Task-Enforcement Module Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0303 Phase 2 Task-Enforcement Module on 2026-07-11. It captures the ratified module + amendments to the Failure-Data Safety Contract (§10 additions), the shipped code + tests, the Rigby double-SIGN cycle (design SIGN turn 1 → implementation SIGN turn 1 → turn 2 post-edits), Chris's joint-recommend D-verdict, and Phase 3 opening authorization. It is append-only history; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Arc phase:** I-0303 Phase 2 (Decorator + Base-Class Implementation)
- **Ratifier:** Chris (D-verdict against joint Claude+Rigby recommendation)
- **Sibling status:** I-0301 CLOSED 2026-07-10; I-0302 CLOSED 2026-07-10; I-0303 scoping RATIFIED S2754; I-0303 Phase 1 audit ledger RATIFIED S2754; Phase 2 module ratified via this record; Phase 3 authorized to open.

---

## §2. Ratified Deliverables

### §2.1 `core/security/task_enforcement.py` — enforcement substrate (599 lines)

Public API (per scoping §4 uniform contract):

- `@enforce_tenant_boundary(model=X, id_kwarg='...')` — function-tier decorator for `@shared_task` bodies. Signature-cached binding handles positional AND keyword dispatch (Phase 1 §4.4 tier-0 caveat).
- `TenantScopedTask(celery.Task)` — Celery base class for new task classes. Declares `tenant_model` + `tenant_id_kwarg` class attributes. `__call__` override runs enforcement before body via `super().__call__`.
- `@system_scope` — unified explicit opt-in marker (Q2 D-verdict fail-safe default). Works on both function-decorated tasks AND `Task` subclasses. Sets `__rur_system_scope__ = True`.
- `TenantBoundaryViolation` — exception raised on any enforcement failure. Picklable via `__reduce__` (Celery `EagerResult` / `AsyncResult` isinstance-safe).

Enforcement algorithm (Q1 trusted-source hierarchy):

1. **Tier 1 — DB row.** Load `model.objects.filter(pk=row_id).first()` from `kwargs[id_kwarg]` via `inspect.signature` binding.
2. **Tier 2 — Transport header.** Extract `x-acting-user-id` from `self.request.headers` (Celery task headers set at `apply_async` time by trusted server code, NOT payload).
3. **Tier 3 — Payload.** NEVER consulted (Q1 mandate).
4. **Ratified predicate.** `PREDICATE_MAP[model]` → one of `can_read_deliverable` / `can_read_chat_conversation` / `can_read_initiative` / `can_read_agent_execution` / `can_read_document` from `core.security.object_authz` (I-0302 Phase 2 ratified). Uniform contract with HTTP layer.

Six `failure_kind` discriminators (existence-oracle safe — identical user-facing envelope across all):

- `missing_row_id`
- `row_not_found`
- `missing_acting_identity`
- `acting_user_not_found`
- `unregistered_model`
- `predicate_rejected`

Failure emission: `TenantBoundaryViolation` raised → Celery `task_failure` signal fires → `_emit_operator_envelope_best_effort` writes `OpsRunEvent` with `task_context` (task_name, task_id, model_label, failure_kind, row_id, acting_user_id, trace_id). User-facing envelope = `reason_code=tenant_boundary_violation` + `support_code` (RUR-TENANT-yyMMdd-hex) only.

### §2.2 Contract §10 amendments

Two entries added per Failure-Data Safety Contract §10 (additions require a ratification record; this record IS that ratification):

**Amendment 1 — `tenant_boundary_violation` reason_code** (added to `core/security/reason_codes.py`):

- Terminal state: `DENIED`
- Typical HTTP status: `403`
- Retryable: `False`
- Default message: `"You do not have access to that resource."` (existence-oracle safe — no row_id, no discriminator, no "not found" phrasing)

**Amendment 2 — `TENANT` support_code component** (added to `core/security/support_code.py`):

- Component name: `TENANT`
- Support code shape: `RUR-TENANT-yyMMdd-hex`
- Also added to `core/security/error_envelope.py` `_REASON_TO_COMPONENT` mapping so DRF error handler resolves component from reason_code correctly.

Both amendments are cross-referenced in module docstrings pointing to this ratification record.

### §2.3 `tests/security/test_i0303_p2_task_enforcement.py` — 18 tests, 191s local runtime

Coverage per Phase 2 charter §5.1-§5.4 + additional axis coverage:

- 4 primary paths (happy / cross-tenant / system-scope / missing-identity) via `_check_boundary` direct + decorator + base-class variants
- 3 failure-kind coverage (missing_row_id / row_not_found / acting_user_not_found — proves existence-oracle uniformity)
- 2 per-user model coverage (Initiative happy + cross-tenant — proves predicate map covers per-user models)
- 2 positional-args dispatch (Phase 1 §4.4 tier-0 pattern — signature binding proven)
- 4 base-class parity (TenantScopedTask happy + cross-tenant + missing-identity + system-scope bypass — uniform contract per scoping §4)
- 3 substrate contract (pickle round-trip + reason-code enum registration + TENANT support component registration)

Test approach: direct `_check_boundary` calls + `push_request` stub context on unbound `TenantScopedTask` instances. Full Celery-eager `.apply()` dispatch is deferred to Phase 4 async-boundary harness where post_save-signal-dispatched-task interaction is controllable via fixture-level Celery config.

### §2.4 Documentation amendments

Six stale path references replaced with the ratified I-0302 path:

- `I-0303_scoping.md` §3.5 (predicate module path) + §11 provenance chain (path in bullet list) + §8 Phase 2 charter (module output path)
- `I-030301_task_boundary_audit_ledger.md` frontmatter `predicate_module_dependency` + §9 entry criteria #8 + §11 handoff bullet
- All amendments include an inline S2755 note explaining the drift (originally referenced `core/tenant_boundary_lockdown/predicates.py` — path never landed; ratified I-0302 Phase 2 module is at `core/security/object_authz.py` per I-030202 design doc §2)

---

## §3. Rigby SIGN Cycle

### §3.1 Design SIGN turn 1 (pre-code)

Rigby converged on 6 design points before coding began:

| Question | Chosen shape |
|---|---|
| Q-A (reason code amendment scope) | **a1** — add `tenant_boundary_violation` in this PR; treat Phase 2 ratification record as contract §10 amendment |
| Q-B (trusted-source algorithm) | **b2** — DB-row-derived expected + transport-header actual + ratified predicate as acceptance check |
| Q-C (failure mechanism) | **c1** — raise `TenantBoundaryViolation` → Celery `task_failure` signal hook → operator envelope emitted best-effort |
| Q-D (system_scope marker shape) | **d2** — unified marker usable on both function decorators AND class decorators |
| Header-missing policy | **Fail-closed** — missing `x-acting-user-id` always rejects unless `@system_scope` |
| Existence-oracle protection | Unified user-facing envelope across all `failure_kind`; discriminator in operator envelope only |

### §3.2 Implementation SIGN turn 1 (post-code)

Rigby verdict: **SIGN-WITH-EDITS** (2 items):

- **F3 (Contract §10 amendment discipline):** ratification record pointer in `reason_codes.py` header comment (`per RATIFICATION_<date>_i0303_phase2_task_enforcement.md`) must resolve to a real artifact.
  - **Applied:** this file (`RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`) IS that artifact. Pointer resolves.
- **F5 (Unrelated changes):** `tools/pa_local.sh:539` modified in working set.
  - **Justified:** session-open pin rotation per S2755 protocol (S2754 close pin `pa-8663e11a0db64131` retired; S2755 fresh mint `pa-f3637b736efb4c07` required for Rigby routing during Phase 2 authoring). Not Phase 2 substrate but a necessary session-scope side effect. Included in the same PR bundle per PLAYBOOK-7.4.1 close-ceremony 1-PR discipline.

Other SIGN axes at implementation turn 1:

- **F1 (Algorithm conformance to Q1 hierarchy + §4 uniform contract):** PASS
- **F2 (Existence-oracle protection across all 6 failure_kinds):** PASS
- **F4 (Test coverage sufficient for Phase 3 opening):** PASS

### §3.3 Implementation SIGN turn 2 (post-edits) — SIGN-PASS

Rigby verdict: **SIGN-PASS** on all axes.

- **F3 (contract §10 amendment discipline):** PASS. Ratification record now exists at `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`, and the pointer in `core/security/reason_codes.py` resolves to a real, auditable artifact.
- **F5 (latent gaps / pre–D-verdict):** PASS. `tools/pa_local.sh` change is justified as a session protocol pin-rotation per `00-START-NEXT-SESSION.md §63-84`, and the rationale is documented in this envelope §3.2. Acceptable to keep in the 1-PR close-ceremony bundle.
- **F1, F2, F4 axes** (unchanged from turn 1): PASS.

Joint recommend-to-Chris (final): *"Recommend to Chris: approve I-0303 Phase 2 module — substrate is contract-conformant, existence-oracle safe, and test-covered; proceed to D-verdict and open Phase 3 wiring."*

---

## §4. Chris D-Verdict

**Verdict:** **APPROVED** ("Approved!" — S2755, 2026-07-11)

Joint Claude+Rigby recommendation presented to Chris after Rigby SIGN-PASS turn 2. Chris ratified with single-word approval on the joint recommendation card that included:

- 599-line `core/security/task_enforcement.py` substrate
- Contract §10 amendments (reason_code `tenant_boundary_violation` + support_code component `TENANT`)
- 18-test suite (18/18 passing, 191s local runtime)
- 6 doc path amendments across scoping + Phase 1 ledger
- Session-open pin rotation on `tools/pa_local.sh:539` (S2755 protocol)
- This ratification record itself as the contract §10 amendment authority

**Effect:** Phase 2 CLOSED. Phase 3 (Per-Task Enforcement Application) authorized to open. Phase 3 dogfoods PLAYBOOK-7.5.1 three-PR staged codification (REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP). Phase 3 opening requires separate Rigby SIGN + Chris ratification per per-phase discipline.

---

## §5. Phase 3 Opening Authorization

Phase 2 close authorizes Phase 3 (Per-Task Enforcement Application) to open. Phase 3 charter per scoping §8:

- Apply decorator or base-class to every user-owned-model-touching task from Phase 1 audit
- Follow PLAYBOOK-7.5.1 staged codification: REPORT-ONLY substrate PR → BATCH-FIX PR → ENFORCEMENT-FLIP PR
- Track per-task application in ledger; incrementally close rows
- Session-count elasticity: 2-3 sessions if Phase 1 audit surfaces many mixed/none identity tasks (Rigby S2754 SIGN edit)

Phase 3 dispatch guidance (informative; not ratified here):

- Every user-owned-model-touching task wires either (a) `@enforce_tenant_boundary(model=X, id_kwarg='...')` on `@shared_task(bind=True)` OR (b) `@shared_task(base=MyScopedTask, bind=True)` where `MyScopedTask(TenantScopedTask)` sets `tenant_model` + `tenant_id_kwarg` class attrs OR (c) `@system_scope` explicit opt-out
- Callers dispatch via `apply_async(..., headers={'x-acting-user-id': str(user.pk)})` — Phase 3 substrate adds a helper that always attaches the header from Django's `request.user`

---

## §6. Phase 2 Limitations

- **HMAC signing of `x-acting-user-id` header deferred.** Current implementation accepts the header unsigned. HMAC-signed headers land on the RUR-C2 / follow-on backlog. Rationale: Celery task headers are transport metadata set by trusted server code at dispatch time (not payload strings forgeable by LLM prompt-injection); HMAC signing is defense-in-depth, not a Phase 2 blocker.
- **Duplicate AgentExecution / AgentTaskExecution class caveat inherited from Phase 1 §4.4.** Phase 3 wiring selects canonical class per-task; predicate map currently registers only `AgentExecution` (I-0302 ratified canonical). Legacy `AgentTaskExecution` touches at `tasks_agents.py:493-538` will need Phase 3 conversion.

---

## §7. Provenance Chain

- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (ratified S2754)
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md` (ratified S2754)
- **Predicate module dependency:** `core/security/object_authz.py` (I-0302 Phase 2 ratified 2026-07-10)
- **Failure-Data Safety Contract:** `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` (ratified I-0301)
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` — §7.4.x (close-ceremony discipline), §7.5.1 (Phase 3 staged codification pattern), §7.6.1 (Phase 4 SIGN watchpoint-attestation)
