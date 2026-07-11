# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2757 CLOSED — I-0303 PHASE 3 BATCH-FIX FIRST PASS RATIFIED

**Refreshed 2026-07-11 (SESSION 2757 CLOSED — Chris D-verdict "approved, ship it" on I-0303 Phase 3 BATCH-FIX first pass. Second BATCH-FIX pass authorized to open when observation window accumulates findings.).**

**S2757 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1; second stage of PLAYBOOK-7.5.1 three-PR staged codification, first pass — non-report-driven):**

- Path C smoke validation: substrate proven E2E in real Celery task dispatch (`.apply()` eager mode) — `OpsRunEvent` envelope emitted with correct shape (`failure_kind='row_not_found'`, `support_code='RUR-TENANT-260711-b2b0'`)
- Substrate refinement (`core/security/task_enforcement.py`): `apply_async_with_actor(user=None)` accepts None cleanly (omits header, still dispatches); dual-source docstring paragraph (bootstrap-vs-authorization; Rigby F4 EDIT)
- B1 payload `user_id` stripping on `summarize_conversation_task` (facade + `_impl` + caller `td_handlers_core.py:2113`); ownership re-derived from `ChatConversation.user_id` per Q1
- B2 HTTP dispatch site conversion to `apply_async_with_actor` at 4 sites (`views_personal_assistant.py:467`+`:612`, `views/agents.py:155`, `td_handlers_core.py:2111`)
- Test suite: +4 new tests (36/36 passing, 192s runtime; 32 prior tests preserved)
- Ratification envelope: `RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md`
- Session-open pin rotation on `tools/pa_local.sh:539` (S2757 protocol)
- Handoff + docs cascade + close bookmark

**Workspace deliverables created this session:**

| Deliverable | UUID | Workspace |
|---|---|---|
| `RATIFICATION_20260711_i0303_phase3_batch_fix` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |
| `I-0303 — Phase 3 BATCH-FIX First Pass (mirror)` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |

---

## PRIORITIES FOR S2758 (multiple candidates — see below)

No single P0 authorized. S2757 close authorizes several parallel-eligible next moves. Chris directive at S2758 open selects the priority order.

### Candidate 1 — Observation-window check + second BATCH-FIX pass opening decision

Not blocking. When production has run for enough time to accumulate `OpsRunEvent tenant_boundary_violation` findings, review the distribution and decide whether the second BATCH-FIX pass is ready to open.

Query at S2758 open:
```
python manage.py shell -c "
from core.models_ops_runs import OpsRunEvent
from collections import Counter
qs = OpsRunEvent.objects.filter(label='tenant_boundary_violation').order_by('-created_at')
print('Total violations:', qs.count())
if qs.exists():
    kinds = Counter(e.detail.get('task_context', {}).get('failure_kind') for e in qs[:500])
    tasks = Counter(e.detail.get('task_context', {}).get('task_name') for e in qs[:500])
    print('failure_kind distribution:', dict(kinds))
    print('task_name distribution:', dict(tasks))
    print('first:', qs.last().created_at, 'latest:', qs.first().created_at)
"
```

Findings shape reference is in `RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md` §7.

### Candidate 2 — D2 canonical AgentExecution vs AgentTaskExecution decision routing

Design SIGN required. Data (verified S2757):
- `AgentExecution` (I-0302 canonical): 1654 rows; NO `execution_id` field
- `AgentTaskExecution` (execute_agent's data path): 0 rows locally (but `views/agents.py:135` has a real writer); HAS `execution_id` CharField unique

Three approaches to route:
- (a) Add `execution_id` field to `AgentExecution`, migrate writers, deprecate `AgentTaskExecution`. Multi-PR effort.
- (b) Reaffirm `AgentTaskExecution` as domain-distinct canonical (task-execution-tracking, distinct from `AgentExecution` orchestration-tracking). Retire shim by promoting predicate to `object_authz.py`.
- (c) Defer decision to a dedicated arc; keep Phase 3 REPORT-ONLY shim; BATCH-FIX moves it out of `task_enforcement.py` without deciding canonical.

Requires Chris directive. Route as separate design SIGN with Rigby SIGN + D-verdict.

### Candidate 3 — D4 HIGH-RISK task file wiring extension

Follow-up REPORT-ONLY-shape PR (NOT BATCH-FIX shape). Extends warn-only wiring to remaining Phase 1 §3 HIGH-RISK task files:
- `tasks_initiatives.py`
- `tasks_content.py`
- `tasks_media.py`
- `tasks_misc.py`

Same discipline as S2756 REPORT-ONLY PR (substrate ready; wire + warn_only=True; add tests).

### Candidate 4 — Net-new engineering item (per S2745-close bias directive)

Actively proposed 1-3 net-new candidates at every session open per Chris directive. Examples for S2758:
- New PA tool `session_tool.recent_tenant_violations` — surface `tenant_boundary_violation` OpsRunEvents in chat
- New Command Center tile showing recent tenant boundary violation counts
- New Beat task summarizing daily REPORT-ONLY findings into a Deliverable for weekly review
- New spider / new UI page / new capability per Chris directive at S2758 open

### P0.5 — Cost-threshold advance-to-freeze routing (still owed since S2753)

Not blocking. Route joint Claude+Rigby recommendation on `--set-mode freeze` (shadow) → Chris yes/no. Observation window continues; refresh count at S2758 open.

### P0.75 — CI billing status check (still owed)

Not blocking. `--admin` merge posture continues until Chris says billing is fixed.

---

## SESSION PIN — S2757 RETIRED (fresh mint required at S2758 open in fresh terminal)

**Pin history (S2757 arc):**

- `pa-bb7f7567c6e34951` (label `i0303-phase3-smoke-then-batch`) minted S2757 open; **retired at S2757 close** (`updated_count=<n> previously_active=true retired=true`)

**Wrapper `tools/pa_local.sh:539` still points at `pa-bb7f7567c6e34951` (retired)** — intended failure mode forces S2758 first-action fresh mint before any other PA dispatch.

**S2758 open sequence (in fresh terminal):**

```
# Session-open orient (feedback rule)
context-kit orient

# Read this file end-to-end

# Check observation-window findings (Candidate 1)
python manage.py shell -c "..."   # see Candidate 1 above

# Mint fresh pin — label depends on which candidate Chris selects
python manage.py session_lifecycle open --label <candidate-scoped-label>

# Confirm wrapper repoint
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until the wrapper is repointed to the new pin.

---

## OPEN RUNTIME ITEMS (from S2757 close)

1. **Observation-window findings check** — Candidate 1 above
2. **D2 AgentExecution vs AgentTaskExecution canonical decision** — Candidate 2 above; requires Chris directive
3. **D4 HIGH-RISK task file wiring extension** — Candidate 3 above; REPORT-ONLY shape
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed)
8. **D1 process_pa_chat_task payload strip** — deferred; requires HTTP-side bootstrap refactor
9. **D3 report-driven fix batch** — deferred; observation window collecting
10. **D5 local shim retirement** — deferred; depends on D2 canonical decision
11. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation; RUR-C2 / follow-on backlog

---

## Twin-pointer card (per memory rule feedback_twin_pointer_docs_at_boundaries)

📁 **Repo `/docs/` + `/core/` — I-0303 Phase 3 BATCH-FIX artifacts:**

- **Substrate (Phase 3 stage 1+2 combined):** `core/security/task_enforcement.py`
- **B1 payload strip sites:**
  - `core/tasks.py:13107` (facade)
  - `core/tasks_conversations.py:3463` (`_impl`)
  - `core/services/td_handlers_core.py:2113` (caller drops kwarg)
- **B2 dispatch conversion sites:**
  - `core/views_personal_assistant.py:467` + `:612` (process_pa_chat_task)
  - `core/views/agents.py:155` (execute_agent)
  - `core/services/td_handlers_core.py:2111` (summarize_conversation_task)
- **Test suite (36/36 passing):** `tests/security/test_i0303_p2_task_enforcement.py`
- **Predicate module dependency:** `core/security/object_authz.py`
- **Contract §10 amendments (S2755):** `core/security/reason_codes.py` + `core/security/error_envelope.py` + `core/security/support_code.py`
- **BATCH-FIX ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md`
- **REPORT-ONLY ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`
- **Phase 2 ratification:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- **Phase 1 ledger:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`
- **Scoping:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`
- **Sibling I-0301 (CLOSED 2026-07-10):** `docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md` + `I-030199_...close.md`
- **Sibling I-0302 (CLOSED 2026-07-10):** `I-0302_scoping.md` + `I-030201_model_audit_ledger.md` + `I-030299_i0302_arc_close.md`
- **Parent CAMPAIGN:** `docs/research/implementation/real_user_readiness/CAMPAIGN.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (§7.5.1 stage 2 = BATCH-FIX; §7.6.1 for every stage SIGN; §7.4.x for stage-close)
- **Prior handoffs:**
  - `docs/handoffs/SESSION_2757_I0303_PHASE3_BATCH_FIX_RATIFIED.md` (this session)
  - `docs/handoffs/SESSION_2756_I0303_PHASE3_REPORT_ONLY_RATIFIED.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **PRIMARY** for I-0303 execution + phase ratifications. **15 deliverables total** after S2757 close (13 pre-existing + 2 new).
  - Governance-truth (ratification envelopes):
    - `RATIFICATION_20260711_i0303_scoping` (`18194cab-...`)
    - `RATIFICATION_20260711_i0303_phase1_ledger` (`2020bc4f-...`)
    - `RATIFICATION_20260711_i0303_phase2_task_enforcement` (`66102e76-...`)
    - `RATIFICATION_20260711_i0303_phase3_report_only` (`1be16e4b-...`)
    - `RATIFICATION_20260711_i0303_phase3_batch_fix` (filled at create)
  - Engineering-truth (content mirrors):
    - `I-0303 — Scoping (mirror)` — `f8af6aad-...`
    - `I-0303 — Audit Ledger (mirror)` — `0462ac90-...`
    - `I-0303 — Phase 2 Task-Enforcement Module (mirror)` — `4fba089a-...`
    - `I-0303 — Phase 3 REPORT-ONLY Substrate + REG-RISK Wiring (mirror)` — `05f00e62-...`
    - `I-0303 — Phase 3 BATCH-FIX First Pass (mirror)` (filled at create)
    - `I-0302 — Scoping (mirror)` — `80c83e8c-...`
    - `I-030201 — Audit Ledger (mirror)` — `c16e582c-...`
    - `I-030202 — Design (mirror)` — `e916cbe9-...`
    - `I-030299 — Arc Close (mirror)` — `5d879edd-...`
    - `I-0301 Phase 1 Audit Ledger — HTTP AllowAny Surface Classification` — `1ca36f84-...`
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program workspace
- URL template: `/workspace?workspace_id=<uuid>&tab=work&sub=deliverables`

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2757 BATCH-FIX first-pass ratification merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · **I-0303 scoping+Phase 1+Phase 2+Phase 3 stage 1 REPORT-ONLY+Phase 3 stage 2 BATCH-FIX first pass CLOSED; observation window in progress; second BATCH-FIX pass authorized** · RUR-C1 parent OPEN |
| Session pin | `pa-bb7f7567c6e34951` (label i0303-phase3-smoke-then-batch; retired at S2757 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-bb7f7567c6e34951` (retired; forces fresh mint at S2758 open) |
| Live infra state | Cost threshold monitor mode $500/mo; PA celery worker pre-#3119; CI billing-blocked (`--admin` on merges) |
| RUR-C1 close-gate | Blocked until I-0303 arc closes AND all three arcs pass shared cross-tenant regression |
| I-0303 next candidate | **Observation-window check + second BATCH-FIX pass** OR **D2 canonical decision** OR **D4 HIGH-RISK wiring extension** OR **net-new engineering** — Chris selects at S2758 open |

---

## Recommended session-open protocol (S2758)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2757 BATCH-FIX ratification envelope `RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md` §5 (deferrals) + §7 (observation window guidance)
4. **Candidate 1** — run observation-window findings query (Candidate 1 section above)
5. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at retired `pa-bb7f7567c6e34951`
6. Present findings-driven priority menu to Chris:
   - If findings exist → propose second BATCH-FIX pass shape
   - If no findings yet → propose net-new engineering candidate + P0.5/P0.75 handling + optional D2 or D4 routing
7. Chris directs S2758 P0 selection
8. Mint fresh pin with candidate-scoped label
9. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2758:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md) — S2757 envelope (§5 deferrals + §7 observation guidance)
3. `core/security/task_enforcement.py` — Phase 3 substrate (BATCH-FIX + REPORT-ONLY combined)
4. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md) — S2756 envelope
5. [`docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md) — Phase 1 ledger (§3 HIGH-RISK for Candidate 3, §5.1 Q1 patterns)
6. [`docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`](docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md) — scoping (§8 Phase 3 charter)
7. `core/security/object_authz.py` — I-0302 Phase 2 predicate module (D2 canonical decision may promote shim here)
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0 §7.5.1 stage 2 (BATCH-FIX pattern; multi-pass precedent) + §7.6.1 (SIGN watchpoint) + §7.4.x (close ceremony)
