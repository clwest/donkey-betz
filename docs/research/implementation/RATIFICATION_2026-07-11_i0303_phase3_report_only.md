---
title: "I-0303 Phase 3 REPORT-ONLY Substrate + REG-RISK Wiring Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2756
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design → implementation) + Chris joint-recommend D-verdict
program_id: RUR
parent_arc: I-0303
parent_arc_phase: Phase 3 (Per-Task Enforcement Application — REPORT-ONLY PR #1)
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
parent_scoping_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md
parent_phase1_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md
parent_phase2_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md
sibling_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_safety_contract.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md
ratified_documents:
  - core/security/task_enforcement.py (amended — warn_only + lookup_field + apply_async_with_actor + AgentTaskExecution shim predicate)
  - core/tasks_agents.py (amended — execute_agent decorated + import)
  - core/tasks.py (amended — process_pa_chat_task + summarize_conversation_task decorated + imports)
  - tests/security/test_i0303_p2_task_enforcement.py (extended — 14 new tests, 32/32 passing)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
staged_codification_stage: 1_of_3 (REPORT-ONLY)
sign_sessions:
  - S2756 — Rigby design SIGN turn 1 (pre-code): PASS on F1–F6 with F2 EDIT (merge headers not overwrite) + non-blocking guardrail (warn-only catches ONLY TenantBoundaryViolation)
  - S2756 — Rigby substrate-amendment SIGN (post-code-gap-discovery): PASS on QA/QB/QC/QD (lookup_field kwarg + local shim predicate + test coverage + within-REPORT-ONLY-discipline attestation)
  - S2756 — Rigby implementation SIGN turn 1 (post-code): PASS on F1–F6 with F3 micro-EDIT (PR-body clarity — no code change)
supersedes: none (first I-0303 Phase 3 ratification)
frozen: true
arc_state:
  phase_1_task_boundary_audit_ledger: closed (S2754)
  phase_2_task_enforcement_module: closed (S2755)
  phase_3_per_task_enforcement_application:
    stage_1_report_only: closed (this record)
    stage_2_batch_fix: pending
    stage_3_enforcement_flip: pending
  phase_4_async_boundary_regression_harness: pending
  phase_5_arc_close: pending
  arc_status: OPEN (Phase 3 stage 1 of 3 CLOSED; BATCH-FIX PR authorized to open at S2757)
test_results:
  local_test_count: 32
  local_test_pass_rate: "32/32"
  local_test_runtime_seconds: 193
  phase_2_test_delta: "+14 tests (18 → 32); 191s → 193s runtime"
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 CLOSED 2026-07-10; I-0302 CLOSED 2026-07-10; I-0303 Phase 3 stage 1 (REPORT-ONLY) CLOSED (this record); RUR-C1 remains OPEN pending Phase 3 stages 2+3 + Phase 4 + Phase 5 arc close
---

# I-0303 Phase 3 REPORT-ONLY Substrate + REG-RISK Wiring Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0303 Phase 3 REPORT-ONLY PR #1 on 2026-07-11. It captures the substrate widening (warn-only mode, lookup_field, apply_async_with_actor helper, AgentTaskExecution shim predicate) + REG-RISK exemplar wiring (3 tasks) + expanded test coverage (14 new tests), the Rigby SIGN cycle (pre-code design SIGN + substrate-amendment SIGN + post-code implementation SIGN), Chris's joint-recommend D-verdict, and BATCH-FIX PR opening authorization. Append-only history; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Arc phase:** I-0303 Phase 3 (Per-Task Enforcement Application), Stage 1 of 3 per PLAYBOOK-7.5.1 (REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP)
- **Ratifier:** Chris (D-verdict against joint Claude+Rigby recommendation)
- **Sibling status:** I-0301 CLOSED 2026-07-10; I-0302 CLOSED 2026-07-10; I-0303 scoping / Phase 1 / Phase 2 ratified S2754 / S2754 / S2755; Phase 3 authorized at Phase 2 close; this record ratifies Phase 3 stage 1.

---

## §2. Ratified Deliverables

### §2.1 `core/security/task_enforcement.py` — substrate widening (~+150 lines)

Four substrate additions layered on the Phase 2 module:

**`warn_only=False` kwarg** on `@enforce_tenant_boundary` and matching class attr on `TenantScopedTask`. When True: wrapper catches `TenantBoundaryViolation`, emits the operator envelope via a parallel path (`_emit_warn_only_envelope`), and returns from the wrapper — body runs. Only `TenantBoundaryViolation` is caught; all other exceptions raised inside `_check_boundary` or the body propagate normally (Rigby GUARDRAIL-1).

**`lookup_field='pk'` kwarg** on both decorator and class attr. `_check_boundary` uses `model.objects.filter(**{lookup_field: row_id}).first()` instead of the hardcoded `pk=row_id`. Default `'pk'` preserves all Phase 2 test invariance. Widening was required because all 3 REG-RISK exemplars dispatch on natural-key CharFields (`conversation_id`, `execution_id`), not PKs — Phase 2 substrate could not reach the rows. Discovered pre-code during read-of-target-signatures; ratified as within-REPORT-ONLY discipline (additive, no enforcement change, no Phase 2 behavior change).

**`apply_async_with_actor(task, user, *, args=(), kwargs=None, headers=None, **options)` helper.** Merges caller-provided headers with the acting-user header via `setdefault` — caller-provided correlation headers (`x-request-id`, `x-trace-id`, etc.) preserved; caller wins on explicit `x-acting-user-id` collision. BATCH-FIX PR consumes this helper for HTTP dispatch site conversion.

**Local shim predicate `can_read_agent_task_execution`** in `_get_predicate_for_model`. Marked TEMPORARY per Phase 1 §4.4 duplicate-class caveat — Q2 register-both agreement means both `AgentExecution` (I-0302 canonical) and `AgentTaskExecution` (`execute_agent`'s actual data path) resolve. BATCH-FIX PR canonicalizes the class decision. Fail-safe on `row.user_id is None` (unowned rows rejected per Q2 fail-safe default).

**`_emit_warn_only_envelope(exc)` parallel emission path.** Reuses the Phase 2 `_build_task_operator_envelope` + `_emit_operator_envelope_best_effort` targets. Warn-only and enforcement-mode `OpsRunEvent` rows are byte-identical; distinguished only via `task_context.failure_kind`. Q9 best-effort — emission failures swallowed rather than break the (warn-only) task body.

### §2.2 REG-RISK exemplar wiring (3 tasks, all `warn_only=True`)

Decorator placement: BELOW `@shared_task` (Celery wraps outermost). `lookup_field` is required because task dispatch IDs are natural-key CharFields, not PKs.

**`execute_agent` (`core/tasks_agents.py:493`, Tier-0 direct-registered):**

```python
@shared_task(bind=True, base=AgentExecutionTask, max_retries=3)
@enforce_tenant_boundary(
    model=AgentTaskExecution,
    id_kwarg="execution_id",
    lookup_field="execution_id",
    warn_only=True,
)
def execute_agent(self, execution_id: str, **kwargs):
    ...
```

Applied against `AgentTaskExecution` matching the task body's actual model reference at `tasks_agents.py:504` (per Phase 1 §4.4 spot-check). Canonical decision (AgentExecution vs AgentTaskExecution) deferred to BATCH-FIX.

**`process_pa_chat_task` (`core/tasks.py:11947` facade):**

```python
@shared_task(bind=True, time_limit=300, soft_time_limit=280, acks_late=False)
@enforce_tenant_boundary(
    model=ChatConversation,
    id_kwarg="conversation_id",
    lookup_field="conversation_id",
    warn_only=True,
)
def process_pa_chat_task(self, user_id, message, context=None, ...):
    ...
```

Highest-traffic user-owned-model task per Phase 1 §3 (924 runs/7d). Payload `user_id` NOT stripped in REPORT-ONLY (behavior change deferred to BATCH-FIX).

**`summarize_conversation_task` (`core/tasks.py:13107` facade):**

Same decorator shape as `process_pa_chat_task`. Phase 1 §5.1 confirmed REG-RISK exemplar for payload-supplied `user_id` (Q1 explicit violation) — payload stripping deferred to BATCH-FIX.

### §2.3 Test suite — 14 new tests (32/32 passing, 193s runtime)

`tests/security/test_i0303_p2_task_enforcement.py` extended (+~250 lines):

- **C1** `test_warn_only_violation_emits_envelope_no_raise` — cross-tenant violation emits `OpsRunEvent`, does not raise, body runs
- **C2** `test_warn_only_happy_path_unchanged` — non-violation path idle
- **C4** `test_warn_only_non_boundary_exception_propagates` — GUARDRAIL-1: only `TenantBoundaryViolation` caught
- **C1-baseclass** `test_baseclass_warn_only_violation_emits_envelope_no_raise` — TenantScopedTask parity
- **C3** `test_apply_async_with_actor_attaches_header` — helper injects `x-acting-user-id`
- **C3b** `test_apply_async_with_actor_merges_correlation_headers` — F2 EDIT: correlation preserved
- **C3c** `test_apply_async_with_actor_caller_wins_on_actor_collision` — explicit caller override supported
- `test_lookup_field_conversation_id_reaches_row` — natural-key ChatConversation happy path
- `test_lookup_field_conversation_id_cross_tenant` — natural-key ChatConversation cross-tenant
- `test_lookup_field_defaults_to_pk_for_backwards_compat` — Phase 2 test invariance
- `test_agent_task_execution_shim_predicate_registered` — Q2 register-both fulfilled
- `test_agent_task_execution_shim_predicate_matches_user` — shim positive behavior
- `test_agent_task_execution_shim_predicate_rejects_cross_tenant` — shim negative behavior
- `test_agent_task_execution_shim_predicate_null_user_rejected` — fail-safe on unowned row

Test approach continuity: `_check_boundary` direct calls + `push_request` stub context on unbound `TenantScopedTask` instances + Django `_db` fixture for `OpsRunEvent` count assertions. Full Celery-eager `.apply()` dispatch of the 3 wired tasks deferred to Phase 4 async-boundary harness (same reason as Phase 2 §2.3: `post_save` signals dispatch nested tasks that hang test worker).

---

## §3. Rigby SIGN Cycle

Three SIGN turns across the S2756 authoring cycle.

### §3.1 Design SIGN turn 1 (pre-code)

Rigby SIGN-PASS on F1–F6:

| Axis | Verdict |
|---|---|
| F1 warn-only preserves existence-oracle protection | PASS |
| F2 apply_async_with_actor header shape matches ACTING_USER_HEADER contract | PASS (with EDIT: merge not overwrite; caller wins on collision) |
| F3 3 REG-RISK targets are the right first batch | PASS |
| F4 Q2 answer 2a (register-both) sits well with Phase 3 constraint | PASS |
| F5 PR scope bounded per PLAYBOOK-7.4.1 + 7.5.1 | PASS |
| F6 pre-code SIGN watchpoint attested | PASS |

Q leans agreed: Q1 one PR · Q2 register both AgentExecution + AgentTaskExecution · Q3 reuse operator envelope · Q4 ship helper in REPORT-ONLY · Q5 extend Phase 2 test file.

**Rigby EDIT-1 (F2, accepted as substrate requirement):** `apply_async_with_actor` merges caller headers rather than overwrites; caller wins on explicit `x-acting-user-id` collision.

**Rigby GUARDRAIL-1 (non-blocking, accepted):** warn-only wrapper catches ONLY `TenantBoundaryViolation`. Other exceptions propagate.

### §3.2 Substrate-amendment SIGN (post-code-gap discovery)

Discovered during pre-code read of the 3 REG-RISK task bodies: all use non-PK CharField natural keys (`conversation_id`, `execution_id`). Phase 2's hardcoded `.filter(pk=row_id).first()` cannot reach these rows.

Rigby SIGN-PASS on QA/QB/QC/QD:

| Axis | Verdict |
|---|---|
| QA `lookup_field` kwarg + class attr shape | PASS |
| QB local shim predicate in task_enforcement.py (not object_authz.py) | PASS (with EDIT: loudly TEMPORARY comment) |
| QC test coverage for new lookup_field paths | PASS |
| QD within-REPORT-ONLY-discipline (additive; no enforcement change; no Phase 2 behavior change) | PASS |

**Rigby EDIT-2 (QB, applied as code comment):** `# TODO(I-0303 BATCH-FIX): promote can_read_agent_task_execution to core.security.object_authz and reconcile with can_read_agent_execution per Phase 1 §4.4 duplicate-class caveat. This is a TEMPORARY Phase 3 REPORT-ONLY shim — do NOT rely on this location for the canonical AgentExecution vs AgentTaskExecution decision.` — landed at the shim definition site.

### §3.3 Implementation SIGN turn 1 (post-code)

Rigby SIGN-PASS on F1–F6:

| Axis | Verdict |
|---|---|
| F1 existence-oracle preserved via sanitized envelope reuse | PASS |
| F2 apply_async_with_actor merge behavior + caller-wins semantics | PASS |
| F3 3 REG-RISK targets wired correctly | PASS (with micro-EDIT: PR-body clarify decorator-below-@shared_task + lookup_field rationale) |
| F4 Q2 register-both AgentExecution + AgentTaskExecution fulfilled | PASS |
| F5 scope disciplined per PLAYBOOK-7.4.1 + 7.5.1 | PASS |
| F6 post-code implementation matches signed design shape | PASS |

**Rigby micro-EDIT (F3, applied to PR body, no code change):** call out decorator-below-@shared_task placement + explain why `lookup_field` is required (natural-key IDs).

Joint recommend-to-Chris (final): *"Recommend APPROVE for merge — substrate widening + 3 REG-RISK exemplars + tests all shipped locally; F1–F6 SIGN-PASS; scope disciplined; explicit deferrals documented."*

---

## §4. Chris D-Verdict

**Verdict:** **APPROVED** ("approve to open PR" / "approved" / "approved, ship it" — three ratification points across the S2756 cycle: original PR shape, substrate-amendment delta, final ship instruction)

Joint Claude+Rigby recommendations routed to Chris in three cards:

1. **Original PR shape** — approve to open PR (D-verdict "approve")
2. **Amended delta** — substrate widening for natural-key lookup (D-verdict "approved")
3. **Final ship** — post-code SIGN-PASS + micro-EDIT (D-verdict "approved, ship it")

Zero unresolved menus routed to Chris; every decision converged Claude+Rigby first per S2753 workflow rule.

**Effect:** Phase 3 REPORT-ONLY substrate + 3 REG-RISK exemplar wiring + 14 test additions CLOSED. Phase 3 stage 2 (BATCH-FIX PR) authorized to open at S2757. Stage 2 requires separate Rigby SIGN + Chris ratification per per-stage discipline.

---

## §5. Stage 2 (BATCH-FIX) Opening Authorization

Phase 3 stage 1 close authorizes Phase 3 stage 2 (BATCH-FIX PR) to open. Stage 2 charter per scoping §8 + PLAYBOOK-7.5.1:

- Resolve all REPORT-ONLY findings from stage 1 substrate (observation window TBD by traffic volume)
- Every violation classified either:
  - (a) legitimate acting-user resolution + header attachment fix at HTTP dispatch site (convert to `apply_async_with_actor`)
  - (b) substrate task rework (Q6 refactor from filter → row-ID dispatch)
- **Payload `user_id` stripping** on `summarize_conversation_task` + `process_pa_chat_task` (Phase 1 §5.1 Q1 explicit violation) — remove from signatures, re-derive from `ChatConversation.user_id`
- **AgentExecution vs AgentTaskExecution canonical decision** — Phase 1 §4.4 duplicate-class caveat + Phase 3 REPORT-ONLY shim retirement
- **HTTP dispatch site conversion** — convert callers of `execute_agent`, `process_pa_chat_task`, `summarize_conversation_task` to use `apply_async_with_actor` helper (Phase 3 substrate ready)
- **Extend warn-only wiring** to remaining HIGH-RISK task files per Phase 1 §3 bucketing (`tasks_initiatives.py`, `tasks_content.py`, `tasks_media.py`, `tasks_misc.py`) — informed by stage 1 report data
- Rigby SIGN + Chris D-verdict per per-stage discipline

Stage 3 (ENFORCEMENT-FLIP) authorization does NOT extend from this ratification — separate ratification required after BATCH-FIX closes.

---

## §6. Phase 3 Stage 1 Limitations

- **Phase 4 async-boundary harness deferred.** Full Celery-eager `.apply()` dispatch of the 3 wired tasks against real fixtures is not exercised at Phase 3 (same substrate limitation as Phase 2 §2.3). Phase 4 sibling arc I-030304 (I-0302 completed; I-0303 counterpart pending) is where end-to-end dispatch flows exercise.
- **Payload `user_id` still accepted** on `summarize_conversation_task` + `process_pa_chat_task` — behavior change deferred to BATCH-FIX. REPORT-ONLY discipline forbids payload signature changes at this stage.
- **AgentTaskExecution shim predicate lives in `task_enforcement.py`** rather than `object_authz.py`. Loudly TEMPORARY per Rigby EDIT-2. BATCH-FIX PR promotes or retires.
- **HTTP dispatch sites unconverted.** `apply_async_with_actor` helper is shipped substrate; BATCH-FIX PR consumes it site-by-site.
- **Phase 3 conformance check** (per module docstring: *"Phase 3 conformance check will reject any user-owned-model task lacking exactly one of `@enforce_tenant_boundary` or `@system_scope`"*) not yet implemented as a static check. Runtime enforcement is the substrate; static check lands with ENFORCEMENT-FLIP PR.

---

## §7. Substrate Widening Provenance (S2756 discovery)

Documented as a PLAYBOOK-6.10.3 close-cycle watchpoint hit — a Phase 2 substrate constraint gap that only surfaced at Phase 3 application. Not a Phase 2 defect: Phase 2 tests used pk-shaped fake rows and passed. The gap surfaced when reading real production task signatures at Phase 3 wiring.

**Resolution mechanism:** additive substrate widening within Phase 3 REPORT-ONLY discipline (default `lookup_field='pk'` preserves Phase 2 behavior). No Phase 2 amendment record required per Rigby SIGN QD.

**Watchpoint attestation:** the S2756 authoring cycle exercised PLAYBOOK-7.6.1 pre-code SIGN watchpoint FOUR times — original design, substrate-amendment delta, post-code implementation SIGN, D-verdict routing. Three Rigby SIGN turns; all PASS. Two additive edits (F2 header-merge, QB shim comment) folded in cleanly. This is the second phase-close under v0.5.0 discipline (Phase 2 was first); pattern holding.

---

## §8. Provenance Chain

- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (ratified S2754)
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md` (ratified S2754)
- **Phase 2 substrate:** `core/security/task_enforcement.py` (ratified S2755)
- **Phase 2 ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- **Predicate module dependency:** `core/security/object_authz.py` (I-0302 Phase 2 ratified 2026-07-10)
- **Failure-Data Safety Contract:** `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` (ratified I-0301)
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` — §7.4.x (close-ceremony discipline), §7.5.1 (three-PR staged codification pattern — this is stage 1 of 3), §7.6.1 (SIGN watchpoint-attestation — exercised 3x this session), §6.10.3 (close-cycle watchpoint — substrate-gap discovery documented)
