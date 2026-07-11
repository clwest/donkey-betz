# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2756 CLOSED — I-0303 PHASE 3 REPORT-ONLY SUBSTRATE + REG-RISK WIRING RATIFIED

**Refreshed 2026-07-11 (SESSION 2756 CLOSED — Chris D-verdict "approved, ship it" on I-0303 Phase 3 REPORT-ONLY substrate widening + 3 REG-RISK exemplar wiring. Phase 3 stage 2 BATCH-FIX authorized to open at S2757.).**

**S2756 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1; first stage of PLAYBOOK-7.5.1 three-PR staged codification):**

- Substrate widening (`core/security/task_enforcement.py`, +~150 lines): `warn_only` kwarg + `lookup_field` kwarg + `apply_async_with_actor` helper + `_emit_warn_only_envelope` parallel emission path + local shim predicate `can_read_agent_task_execution` (loudly TEMPORARY per Phase 1 §4.4)
- REG-RISK exemplar wiring (3 tasks, all `warn_only=True`): `execute_agent` (`tasks_agents.py:493` — AgentTaskExecution / execution_id), `process_pa_chat_task` (`tasks.py:11947` — ChatConversation / conversation_id), `summarize_conversation_task` (`tasks.py:13107` — ChatConversation / conversation_id)
- Test suite: +14 new tests (32/32 passing, 193s local runtime; 18 Phase 2 tests preserved)
- Ratification envelope: `RATIFICATION_2026-07-11_i0303_phase3_report_only.md`
- Session-open pin rotation on `tools/pa_local.sh:539` (S2756 protocol)
- Handoff + docs cascade + close bookmark

**Workspace deliverables created this session:**

| Deliverable | UUID | Workspace |
|---|---|---|
| `RATIFICATION_20260711_i0303_phase3_report_only` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |
| `I-0303 — Phase 3 REPORT-ONLY Substrate + REG-RISK Wiring (mirror)` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |

---

## P0 — I-0303 PHASE 3 STAGE 2 — BATCH-FIX PR

**Authorized to open at S2756 stage-1 ratification.** Target: 1-2 sessions per PLAYBOOK-7.5.1 elasticity (depends on report-only observation-window findings + AgentExecution/AgentTaskExecution canonical decision scope).

**Scope per I-0303 scoping §8 + PLAYBOOK-7.5.1 stage 2 + Phase 3 stage-1 ratification §5:**

1. **Read the REPORT-ONLY report first.** Query `OpsRunEvent` for rows with `label='tenant_boundary_violation'` since S2756 merge. Group by `task_context.task_name` + `task_context.failure_kind`. Enumerate: (a) rows where `failure_kind=predicate_rejected` (legit cross-tenant), (b) rows where `failure_kind=row_not_found` (natural-key lookup miss — validates lookup_field widening), (c) rows where `failure_kind=missing_acting_identity` (dispatch site missing header attachment).
2. **HTTP dispatch site conversion.** For every caller of `execute_agent`, `process_pa_chat_task`, `summarize_conversation_task`: convert to `apply_async_with_actor(task, user, ...)`. Preserves correlation headers; attaches `x-acting-user-id` from Django `request.user`.
3. **Payload `user_id` stripping.** Remove `user_id=None` param from `summarize_conversation_task` + `process_pa_chat_task` signatures (Phase 1 §5.1 Q1 explicit violation targets). Re-derive from `ChatConversation.user_id` inside impl. Update all callers.
4. **AgentExecution vs AgentTaskExecution canonical decision.** Phase 1 §4.4 duplicate-class caveat. Chris D-verdict required on which class to canonicalize. Retire the sibling. Shim predicate retirement (or promotion to `object_authz.py`) follows.
5. **Extend warn-only wiring** to remaining HIGH-RISK task files per Phase 1 §3 bucketing: `tasks_initiatives.py`, `tasks_content.py`, `tasks_media.py`, `tasks_misc.py`. Same `warn_only=True` posture; batch as findings accumulate.
6. **Rigby SIGN** at each stage (report read + fix batch + payload strip + canonical decision + wiring extension). PLAYBOOK-7.6.1 watchpoint-attestation shape.
7. **Chris D-verdict** on each stage.

**Stage 3 authorization does NOT extend to ENFORCEMENT-FLIP.** Stage 3 (flip warn-only → hard-gate + Phase 3 conformance static check) requires separate Rigby SIGN + Chris ratification.

---

## P0.5 — COST-THRESHOLD ADVANCE-TO-FREEZE ROUTING (still owed since S2753)

Not blocking BATCH-FIX. Route joint Claude+Rigby recommendation on `--set-mode freeze` (shadow) to Chris for yes/no. Cost observation window continues — refresh count at S2757 open.

---

## P0.75 — CI BILLING STATUS CHECK (still owed)

Not blocking BATCH-FIX. `--admin` merge posture continues until Chris says billing is fixed.

---

## SESSION PIN — S2756 RETIRED (fresh mint required at S2757 open in fresh terminal)

**Pin history (S2756 arc):**

- `pa-84d8a5a8987c439f` (label `i0303-phase3-report-only`) minted S2756 open; **retired at S2756 close** (`updated_count=<n> previously_active=true retired=true`)

**Wrapper `tools/pa_local.sh:539` still points at `pa-84d8a5a8987c439f` (retired)** — intended failure mode forces S2757 first-action fresh mint before any other PA dispatch.

**S2757 open sequence (in fresh terminal):**

```
# Session-open orient (feedback rule)
context-kit orient

# Read this file end-to-end

# Read REPORT-ONLY findings first (BATCH-FIX P0 step 1)
python manage.py shell -c "
from core.models_ops_runs import OpsRunEvent
from collections import Counter
qs = OpsRunEvent.objects.filter(label='tenant_boundary_violation').order_by('-created_at')
print('Total violations:', qs.count())
kinds = Counter(e.detail.get('task_context', {}).get('failure_kind') for e in qs[:500])
print('failure_kind distribution (last 500):', dict(kinds))
tasks = Counter(e.detail.get('task_context', {}).get('task_name') for e in qs[:500])
print('task_name distribution (last 500):', dict(tasks))
"

# Mint fresh pin scoped to BATCH-FIX work
python manage.py session_lifecycle open --label i0303-phase3-batch-fix

# Confirm wrapper repoint
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until the wrapper is repointed to the new pin.

---

## OPEN RUNTIME ITEMS (from S2756 close)

1. **I-0303 Phase 3 stage 2 BATCH-FIX PR authoring** — P0 above; authorized to open
2. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
3. **P0.75 CI billing** — status check
4. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
5. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed)
6. **AgentExecution / AgentTaskExecution canonical class selection** — Phase 1 §4.4 + Phase 3 REPORT-ONLY shim predicate retirement; BATCH-FIX gates
7. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation; RUR-C2 / follow-on backlog

---

## Twin-pointer card (per memory rule feedback_twin_pointer_docs_at_boundaries)

📁 **Repo `/docs/` + `/core/` — I-0303 Phase 3 REPORT-ONLY artifacts:**

- **Phase 3 substrate widening:** `core/security/task_enforcement.py` (warn_only + lookup_field + apply_async_with_actor + shim predicate)
- **Phase 3 wired REG-RISK exemplars:**
  - `core/tasks_agents.py:493` (`execute_agent`)
  - `core/tasks.py:11947` (`process_pa_chat_task` facade)
  - `core/tasks.py:13107` (`summarize_conversation_task` facade)
  - `core/tasks_misc.py:4672` (`_impl_process_pa_chat_task` — decorated via facade only)
  - `core/tasks_conversations.py:3463` (`_impl_summarize_conversation_task` — decorated via facade only)
- **Test suite (32/32 passing):** `tests/security/test_i0303_p2_task_enforcement.py`
- **Predicate module dependency:** `core/security/object_authz.py`
- **Contract §10 amendments (S2755):** `core/security/reason_codes.py` + `core/security/error_envelope.py` + `core/security/support_code.py`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`
- **Phase 2 ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`
- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`
- **Sibling I-0301 (CLOSED 2026-07-10):** `docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md` + `I-030199_...close.md`
- **Sibling I-0302 (CLOSED 2026-07-10):** `I-0302_scoping.md` + `I-030201_model_audit_ledger.md` + `I-030299_i0302_arc_close.md`
- **Parent CAMPAIGN:** `docs/research/implementation/real_user_readiness/CAMPAIGN.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (§7.5.1 stage 2 = BATCH-FIX; §7.6.1 for every stage SIGN; §7.4.x for stage-close)
- **Prior handoff:** `docs/handoffs/SESSION_2756_I0303_PHASE3_REPORT_ONLY_RATIFIED.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **PRIMARY** for I-0303 execution + phase ratifications. **13 deliverables total** after S2756 close (11 pre-existing + 2 new).
  - Governance-truth (ratification envelopes):
    - `RATIFICATION_20260711_i0303_scoping` (`18194cab-b737-42bf-b747-1263af5771ae`)
    - `RATIFICATION_20260711_i0303_phase1_ledger` (`2020bc4f-ef7d-42e8-9ee5-38be928ba483`)
    - `RATIFICATION_20260711_i0303_phase2_task_enforcement` (`66102e76-1ecd-4407-88b9-97000481d73f`)
    - `RATIFICATION_20260711_i0303_phase3_report_only` (filled at create)
  - Engineering-truth (content mirrors):
    - `I-0303 — Scoping (mirror)` — `f8af6aad-05ae-4d9f-b61b-3a81d6604b57`
    - `I-0303 — Audit Ledger (mirror)` — `0462ac90-dc11-4196-a549-150ff271b7e3`
    - `I-0303 — Phase 2 Task-Enforcement Module (mirror)` — `4fba089a-9743-4f9c-997e-66b1bb5e926f`
    - `I-0303 — Phase 3 REPORT-ONLY Substrate + REG-RISK Wiring (mirror)` (filled at create)
    - `I-0302 — Scoping (mirror)` — `80c83e8c-d130-4b65-9204-de279fae6b83`
    - `I-030201 — Audit Ledger (mirror)` — `c16e582c-ed09-4747-9d77-a4804a746b99`
    - `I-030202 — Design (mirror)` — `e916cbe9-1bb9-4b17-a54d-daed25725efb`
    - `I-030299 — Arc Close (mirror)` — `5d879edd-d654-4fd3-b955-89f700c8416a`
    - `I-0301 Phase 1 Audit Ledger — HTTP AllowAny Surface Classification` — `1ca36f84-...`
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program workspace
- URL template: `/workspace?workspace_id=<uuid>&tab=work&sub=deliverables`

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2756 Phase 3 REPORT-ONLY ratification merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · **I-0303 scoping+Phase 1+Phase 2+Phase 3 stage 1 REPORT-ONLY CLOSED; Phase 3 stage 2 BATCH-FIX authorized** · RUR-C1 parent OPEN |
| Session pin | `pa-84d8a5a8987c439f` (label i0303-phase3-report-only; retired at S2756 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-84d8a5a8987c439f` (retired; forces fresh mint at S2757 open) |
| Live infra state | Cost threshold monitor mode $500/mo; PA celery worker pre-#3119; CI billing-blocked (`--admin` on merges) |
| RUR-C1 close-gate | Blocked until I-0303 arc closes AND all three arcs pass shared cross-tenant regression |
| I-0303 next stage | **Phase 3 stage 2 (BATCH-FIX) — authorized to open at S2757** |

---

## Recommended session-open protocol (S2757)

1. `context-kit orient`
2. Read this file end-to-end
3. Read Phase 3 REPORT-ONLY ratification envelope `RATIFICATION_2026-07-11_i0303_phase3_report_only.md` §2 (ratified deliverables) + §5 (stage 2 opening authorization) + §6 (stage 1 limitations)
4. **P0 step 1** — read REPORT-ONLY findings from `OpsRunEvent` (bash snippet in §SESSION PIN above)
5. Read Phase 1 ledger §3 (HIGH-RISK task files for stage 2 wiring extension), §5.1 (Q1-violation exemplars for payload stripping)
6. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at retired `pa-84d8a5a8987c439f`
7. **P0.5** — cost-threshold advance-to-freeze routing (Claude+Rigby agree first → Chris yes/no) — optional
8. **P0.75** — CI billing status check
9. **P0** — Phase 3 stage 2 BATCH-FIX PR authoring:
   - Mint fresh pin: `python manage.py session_lifecycle open --label i0303-phase3-batch-fix`
   - Draft BATCH-FIX PR shape via joint agreement Claude+Rigby before touching code
   - Route findings-driven fix batch through Rigby SIGN → Chris D-verdict
   - HTTP dispatch site conversion + payload user_id stripping + canonical class decision + HIGH-RISK task file wiring extension

---

## Reference documents

Ordered by frequency of use at S2757 Phase 3 BATCH-FIX:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md) — Phase 3 stage 1 envelope (§5 stage 2 authorization + §2 substrate contract)
3. `core/security/task_enforcement.py` — Phase 3 substrate (BATCH-FIX consumes `apply_async_with_actor`)
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md) — Phase 1 ledger (§3 HIGH-RISK for stage 2 wiring, §5.1 Q1 payload violations)
5. [`docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`](docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md) — scoping (§8 Phase 3 charter)
6. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md) — Phase 2 envelope (module contract + failure_kind reference)
7. `core/security/object_authz.py` — I-0302 Phase 2 predicate module (BATCH-FIX may promote shim predicate here)
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0 §7.5.1 stage 2 (BATCH-FIX pattern) + §7.6.1 (SIGN watchpoint-attestation) + §7.4.x (close ceremony)
