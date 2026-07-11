---
title: "I-0303 Phase 3 BATCH-FIX PR — Payload Strip + Dispatch Conversion Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2757
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design → implementation) + Chris joint-recommend D-verdict
program_id: RUR
parent_arc: I-0303
parent_arc_phase: Phase 3 (Per-Task Enforcement Application — BATCH-FIX PR, stage 2 of 3)
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
parent_phase3_stage1_ratification: docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md
sibling_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md
  - docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md
ratified_documents:
  - core/security/task_enforcement.py (amended — apply_async_with_actor accepts user=None; dual-source docstring note)
  - core/tasks.py (amended — summarize_conversation_task facade payload user_id stripped)
  - core/tasks_conversations.py (amended — _impl_summarize_conversation_task payload user_id stripped; re-derives from ChatConversation.user_id)
  - core/services/td_handlers_core.py (amended — summarize dispatch via apply_async_with_actor; user_id kwarg dropped)
  - core/views_personal_assistant.py (amended — 2× process_pa_chat_task dispatch via apply_async_with_actor)
  - core/views/agents.py (amended — execute_agent dispatch via apply_async_with_actor)
  - tests/security/test_i0303_p2_task_enforcement.py (extended — 4 new tests, 36/36 passing)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
staged_codification_stage: 2_of_3 (BATCH-FIX, non-report-driven first pass)
sign_sessions:
  - S2757 — Rigby design SIGN turn 1 (pre-code): PASS on F1-F6 with clarifications on F1 (prefer ChatConversation.user_id direct), F4 (header = authorization, payload = bootstrap only), F6 (watchpoints: user=None header omission + no new hard-fail + tests assert both behavior + ownership)
  - S2757 — Rigby implementation SIGN turn 1 (post-code): PASS on F1-F6 with non-blocking F4 EDIT (docstring note re: bootstrap-vs-authorization — applied)
supersedes: none (first non-report-driven BATCH-FIX pass; second BATCH-FIX PR will consume observation-window report findings)
frozen: true
arc_state:
  phase_1_task_boundary_audit_ledger: closed (S2754)
  phase_2_task_enforcement_module: closed (S2755)
  phase_3_per_task_enforcement_application:
    stage_1_report_only: closed (S2756)
    stage_2_batch_fix:
      first_pass_non_report_driven: closed (this record)
      second_pass_report_driven: pending
    stage_3_enforcement_flip: pending
  phase_4_async_boundary_regression_harness: pending
  phase_5_arc_close: pending
  arc_status: OPEN (Phase 3 stage 2 first pass CLOSED; observation window in progress; second BATCH-FIX pass authorized to open when findings accumulate)
test_results:
  local_test_count: 36
  local_test_pass_rate: "36/36"
  local_test_runtime_seconds: 192
  s2756_test_delta: "+4 tests (32 → 36); 193s → 192s runtime"
path_c_smoke_validation:
  test_task: core.tasks.summarize_conversation_task
  test_conversation_id: smoke-test-nonexistent-conv-id
  eager_dispatch_state: SUCCESS
  envelope_emitted: true
  ops_run_event_failure_kind: row_not_found
  ops_run_event_model_label: ChatConversation
  ops_run_event_support_code: RUR-TENANT-260711-b2b0
  ops_run_event_reason_code: tenant_boundary_violation
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 CLOSED 2026-07-10; I-0302 CLOSED 2026-07-10; I-0303 Phase 3 stage 2 first pass CLOSED (this record); RUR-C1 remains OPEN pending Phase 3 stage 2 second pass + Phase 3 stage 3 (enforcement flip) + Phase 4 + Phase 5 arc close
---

# I-0303 Phase 3 BATCH-FIX PR — Payload Strip + Dispatch Conversion Ratification Record

Frozen canonical record of Chris's ratification of the I-0303 Phase 3 BATCH-FIX PR (stage 2 of 3, first pass — non-report-driven) on 2026-07-11. Captures the B1 payload stripping on `summarize_conversation_task` + B2 dispatch site conversion (4 sites) + `apply_async_with_actor` widening for anonymous dispatch + expanded test coverage (4 new tests), the Rigby SIGN cycle (pre-code design SIGN + post-code implementation SIGN), Chris's joint-recommend D-verdict, and observation-window opening for the second BATCH-FIX pass. Append-only; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Arc phase:** I-0303 Phase 3 (Per-Task Enforcement Application), Stage 2 of 3 per PLAYBOOK-7.5.1 (REPORT-ONLY → BATCH-FIX → ENFORCEMENT-FLIP). This is the FIRST pass of BATCH-FIX (non-report-driven); a SECOND pass will consume production observation-window findings.
- **Ratifier:** Chris (D-verdict against joint Claude+Rigby recommendation)
- **Sibling status:** I-0301 CLOSED · I-0302 CLOSED · I-0303 scoping/Phase 1/Phase 2/Phase 3 stage 1 all closed 2026-07-11 across sessions S2754-S2756; this record ratifies Phase 3 stage 2 first pass at S2757.

---

## §2. Ratified Deliverables

### §2.1 `core/security/task_enforcement.py` — substrate refinement

**`apply_async_with_actor(user=None)` behavior widening.** Prior to S2757, calling the helper with a `None` user would crash on `str(user.pk)`. Post-S2757: `user=None` is accepted; helper OMITS the `x-acting-user-id` header and dispatches with only caller-provided headers. Substrate enforcement then emits `missing_acting_identity` at the task boundary — the correct report-only outcome for anonymous dispatches (S2757 B2 Watchpoint 1).

**Dual-source identity docstring note (Rigby F4 EDIT).** New paragraph in `apply_async_with_actor` docstring explains that some tasks intentionally keep payload `user_id` as bootstrap input (e.g., `process_pa_chat_task` needs it to create the ChatConversation row when `conversation_id` is not materialized yet). The header is the AUTHORIZATION identity; payload is bootstrap. Future cleanup passes MUST NOT strip such payload kwargs without first refactoring the bootstrap flow.

### §2.2 B1 — Payload `user_id` stripping on `summarize_conversation_task`

Phase 1 §5.1 Q1 explicit violation target eliminated.

- **Facade** (`core/tasks.py:13107`) — `user_id` kwarg removed from signature.
- **`_impl_summarize_conversation_task`** (`core/tasks_conversations.py:3463`) — `user_id` kwarg removed. Ownership re-derived via:
  ```python
  first_row = turns_qs.only('user_id', 'session_title').first()
  user_id = first_row.user_id if first_row else None
  ```
- Downstream `create_deliverable(user_id=user_id)` + `ConversationMemory(user_id=user_id)` consume the re-derived value.
- **Caller** (`core/services/td_handlers_core.py:2113`) drops the `user_id` kwarg from the dispatch call.
- Empty-conversation edge case: `user_id=None` fallback preserved (matches prior behavior when payload `user_id` was None).

Rigby F1 SIGN axis attestation: Q1 trusted-source hierarchy preserved (DB row → header → NEVER payload). Existence-oracle protection unchanged.

### §2.3 B2 — HTTP dispatch site conversion (4 sites)

All 4 caller sites of the 3 REG-RISK REPORT-ONLY tasks now dispatch via `apply_async_with_actor`:

| Site | Task | User source | Header semantic |
|---|---|---|---|
| `views_personal_assistant.py:467` | `process_pa_chat_task` | `request.user` | Authorization (payload `user_id` KEPT for bootstrap per F4 dual-source) |
| `views_personal_assistant.py:612` | `process_pa_chat_task` | `request.user` | Same as above (`@rigby` mention path) |
| `views/agents.py:155` | `execute_agent` | `execution.user` (may be None for unauth) | Authorization; None-user omits header cleanly |
| `services/td_handlers_core.py:2111` | `summarize_conversation_task` | `User.objects.filter(pk=user_id).first()` | Authorization; None-user omits header cleanly |

Rigby F3 SIGN axis attestation: `apply_async_with_actor` preserves existing Celery options (queue/routing keys pass through `**options`); correlation headers merged not overwritten (`setdefault` path); caller wins on `x-acting-user-id` collision (C3c invariant preserved).

### §2.4 Test suite — 4 new tests, 36/36 passing (192s runtime)

`tests/security/test_i0303_p2_task_enforcement.py` extended:

- `test_apply_async_with_actor_omits_header_when_user_is_none` — B2 Watchpoint 1: `user=None` omits `x-acting-user-id` and dispatches cleanly.
- `test_apply_async_with_actor_none_user_preserves_correlation_headers` — B2 Watchpoint 1 continuation: correlation headers still preserved when `user=None`.
- `test_summarize_conversation_task_derives_user_from_conversation` — B1 unit test: `_impl_summarize_conversation_task` derives `Deliverable.user_id` from `ChatConversation.user_id`, not from a payload kwarg. Monkey-patches LLM enforcer + `create_deliverable` + `EmbeddingService` to isolate the ownership assertion.
- `test_summarize_conversation_task_empty_conversation_yields_no_deliverable` — B1 edge case: empty-conversation early-return preserved; no `create_deliverable` call.

Backwards-compat verified: 32 previous tests (Phase 2 + Phase 3 REPORT-ONLY) still pass unchanged. Runtime 192s vs 193s baseline — no meaningful drift.

### §2.5 Path C smoke validation (from S2757 open)

Before drafting BATCH-FIX, validated the S2756 REPORT-ONLY substrate end-to-end in real Celery task dispatch (`.apply()` eager mode):

- All 3 decorators applied at module load (attribute inspection: `__rur_tenant_model__` / `__rur_tenant_id_kwarg__` / `__rur_tenant_lookup_field__` / `__rur_tenant_warn_only__` set correctly)
- `summarize_conversation_task.apply(kwargs={'conversation_id': 'smoke-test-nonexistent-conv-id'})` → task state SUCCESS (warn-only did not raise) + body ran ("No turns found" log) + `OpsRunEvent` envelope emitted with `failure_kind='row_not_found'`, `model_label='ChatConversation'`, `row_id='smoke-test-nonexistent-conv-id'`, `support_code='RUR-TENANT-260711-b2b0'`, `reason_code='tenant_boundary_violation'`
- Substrate works. BATCH-FIX pass authorized.

---

## §3. Rigby SIGN Cycle

Two SIGN turns across the S2757 authoring cycle.

### §3.1 Design SIGN turn 1 (pre-code)

Rigby SIGN-PASS on F1–F6:

| Axis | Verdict |
|---|---|
| F1 B1 semantic (re-derive from ChatConversation.user_id) | PASS (clarification: prefer `ChatConversation.user_id` direct; only fall back to first turn's user_id if you've seen conversation-without-user-id-carrying-turns cases) |
| F2 B1 caller drops user_id kwarg from td_handlers_core dispatch | PASS |
| F3 B2 dispatch conversion at 4 sites | PASS |
| F4 process_pa_chat_task dual-source (payload=bootstrap, header=authorization; mismatch stays warn-only) | PASS |
| F5 PR scope disciplined | PASS |
| F6 pre-code watchpoints (user=None header omission + no new hard-fail + tests assert both) | PASS |

Q leans confirmed: QA use None for empty-conversation fallback · QB pass None actor for unauth execute_agent · QC lookup User at td_handlers_core (None if missing) · QD 1 unit-ish B1 + 1 integration-ish B2 test · QE one PR unless bootstrap semantics need touching.

### §3.2 Implementation SIGN turn 1 (post-code)

Rigby SIGN-PASS on F1–F6:

| Axis | Verdict |
|---|---|
| F1 B1 semantic implemented correctly | PASS |
| F2 caller update clean | PASS |
| F3 B2 dispatch conversion preserves Celery options + correlation headers | PASS |
| F4 process_pa_chat_task dual-source constraint respected | PASS (with non-blocking EDIT: add explicit bootstrap-vs-authorization comment in helper docstring or call sites) |
| F5 scope stayed locked (no D1/D2/D4/D5 drift) | PASS |
| F6 watchpoints attested; test coverage right shape | PASS |

**Rigby EDIT applied (F4, docstring):** new paragraph in `apply_async_with_actor` docstring explaining bootstrap-vs-authorization intent; guards against future "helpful cleanup" prematurely stripping payload `user_id` from tasks like `process_pa_chat_task`.

Joint recommend-to-Chris (final): *"Recommend APPROVE for merge — B1 + B2 shipped locally with substrate refinement + docstring EDIT; F1–F6 SIGN-PASS; scope disciplined; 5 explicit deferrals preserved."*

---

## §4. Chris D-Verdict

**Verdict:** **APPROVED** (three ratification points across S2757: original Path B scope "approve"; post-code shape "approved, ship it"; final ship — this record.)

Zero unresolved menus routed per S2753 agree-first workflow rule. Every decision converged Claude+Rigby first.

**Effect:** Phase 3 stage 2 FIRST PASS (non-report-driven BATCH-FIX) CLOSED. Second pass (report-driven) authorized to open when production observation window accumulates findings. Stage 3 (ENFORCEMENT-FLIP) requires separate ratification.

---

## §5. Explicit Deferrals (Preserved from Pre-Code SIGN)

- **D1 — `process_pa_chat_task` payload strip.** Chicken-and-egg: task creates ChatConversation from `user_id` when `conversation_id` not materialized. Requires HTTP-side conversation-creation refactor. Too large for BATCH-FIX first pass.
- **D2 — AgentExecution vs AgentTaskExecution canonical decision.** Non-trivial: I-0302 canonical `AgentExecution` has 1654 rows but NO `execution_id` field; `execute_agent`'s data path `AgentTaskExecution` HAS `execution_id` as unique CharField. Three approaches (add field + migrate writers; reaffirm AgentTaskExecution as domain-distinct canonical + promote predicate; defer to dedicated arc). Requires Chris directive. Route as separate design SIGN.
- **D3 — Report-driven fix batch.** Zero `OpsRunEvent` findings at S2757 open (S2756 REPORT-ONLY merged ~15 min prior). Production observation window needed; second BATCH-FIX PR consumes findings.
- **D4 — HIGH-RISK task file wiring extension.** Remaining Phase 1 §3 files (`tasks_initiatives.py`, `tasks_content.py`, `tasks_media.py`, `tasks_misc.py`) not wired. Follow-up REPORT-ONLY PR shape more appropriate than absorbing into BATCH-FIX.
- **D5 — Local shim retirement.** `can_read_agent_task_execution` shim in `task_enforcement.py._get_predicate_for_model` still TEMPORARY. Retirement/promotion depends on D2 canonical decision.

---

## §6. Path C Smoke Validation Detail

Distinct from Phase 3 REPORT-ONLY test suite (`_check_boundary` direct + `push_request` stubs). Path C proved:

1. Decorators actually apply at module-load time in the real codebase (attribute inspection on production task registration)
2. The Celery task boundary fires the wrapper BEFORE the body
3. warn-only mode: violation → envelope emission → body still runs → task state SUCCESS
4. `OpsRunEvent.detail` has correct shape (support_code + trace_id + reason_code + task_context with task_name/model_label/row_id/failure_kind + timing)

Path C provides the "does the substrate work under real Celery machinery" evidence that the unit test suite (which uses lightweight stubs to avoid post_save-signal-dispatched-task hangs per Phase 2 §2.3) intentionally does not exercise.

---

## §7. Observation Window + Second BATCH-FIX Pass Opening Guidance

Once this PR merges, the 3 REG-RISK REPORT-ONLY targets begin collecting production findings via `OpsRunEvent`:

- `execute_agent` — dispatched from `views/agents.py:155` (now attaches acting-user header)
- `process_pa_chat_task` — dispatched from `views_personal_assistant.py:467` + `:612` (now attaches acting-user header + retains payload user_id for bootstrap)
- `summarize_conversation_task` — dispatched from `td_handlers_core.py:2111` (now attaches acting-user header + payload user_id removed)

**Query for opening the second BATCH-FIX pass:**

```python
from core.models_ops_runs import OpsRunEvent
from collections import Counter

qs = OpsRunEvent.objects.filter(label='tenant_boundary_violation').order_by('-created_at')
print('Total violations:', qs.count())
kinds = Counter(e.detail.get('task_context', {}).get('failure_kind') for e in qs[:500])
print('failure_kind distribution:', dict(kinds))
tasks = Counter(e.detail.get('task_context', {}).get('task_name') for e in qs[:500])
print('task_name distribution:', dict(tasks))
```

Expected findings shape (guidance, not commitment):

- `missing_acting_identity` → dispatch sites we haven't converted (either HIGH-RISK task file targets from D4, or unauthenticated caller paths that should be `@system_scope` per Q2)
- `predicate_rejected` → legitimate cross-tenant boundary breaches (this is what the enforcement mode will hard-gate in stage 3)
- `row_not_found` → dispatch-path lookup misses (may indicate legit bugs or missing lookup_field configuration)
- `acting_user_not_found` → header-derived user pk doesn't resolve (may indicate stale sessions or dispatch-time race conditions)

Second pass opens when finding volume + patterns provide enough signal to plan concrete fixes.

---

## §8. Provenance Chain

- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (ratified S2754)
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md` (ratified S2754)
- **Phase 2 substrate:** `core/security/task_enforcement.py` (ratified S2755)
- **Phase 2 ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- **Phase 3 stage 1 (REPORT-ONLY) ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`
- **Predicate module dependency:** `core/security/object_authz.py` (I-0302 Phase 2 ratified 2026-07-10)
- **Failure-Data Safety Contract:** `docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md` (ratified I-0301)
- **Engineering Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` — §7.4.x (close-ceremony discipline; second phase-close pattern), §7.5.1 (three-PR staged codification — this is stage 2 first pass), §7.6.1 (SIGN watchpoint-attestation)
