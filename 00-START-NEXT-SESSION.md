# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2758 CLOSED — `ops_tool.tenant_boundary_violations` PA TOOL RATIFIED

**Refreshed 2026-07-11 (SESSION 2758 CLOSED — Chris D-verdict "Approved" on new `ops_tool.tenant_boundary_violations` PA tool. First non-boundary-lockdown net-new engineering item since S2754.).**

**S2758 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- Schema (`core/services/pa_tool_schemas.py`): `tenant_boundary_violations` added to `ops_tool` action enum (23rd action); new `failure_kind` param with 6-kind Phase 2 enum; extended `task_name` description
- Handler (`core/services/td_handlers_ops.py`): new elif branch + `_ops_tenant_boundary_violations` method (~130 lines) — window/task_name/failure_kind/limit filters; aggregates by task_name + failure_kind + composite; sample_events with discriminator preserved; empty-state diagnostic note; `MAX_AGG_SCAN=5000` defensive cap
- Test suite: 10 new tests (10/10 passing, 189s runtime)
- **E2E verified via live Rigby dispatch** (`make celery-recycle` + real query)
- **Real finding surfaced during verification:** Rigby's own PA loop dispatches `process_pa_chat_task` without acting-user header — outside the 4 S2757-converted sites. Legitimate second-BATCH-FIX-pass candidate.
- Ratification envelope: `RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md`
- Session-open pin rotation on `tools/pa_local.sh:539` (S2758 protocol)
- Handoff + docs cascade + close bookmark

**Workspace deliverables created this session:**

| Deliverable | UUID | Workspace |
|---|---|---|
| `RATIFICATION_20260711_ops_tool_tenant_boundary_violations` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |
| `ops_tool.tenant_boundary_violations PA Tool (mirror)` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |

---

## CHRIS S2758 DIRECTIVE — LOCAL-TRUTH RULE (memory-update candidate)

**"We are working locally so if it passes locally its working — no production right now."** (Chris, S2758 close 2026-07-11)

Reinforces `project_single_user_pre_prod_operating_context.md`. Applies to all future close-ceremonies:

- Local test pass = shipped. No "production observation window" fantasy.
- No "pending production Railway deploy" language in envelopes.
- `make celery-recycle` (or equivalent local worker bounce) is the "deploy" step.
- L1-style "live E2E deferred" limitations are wrong for local-only work; if code passes locally + Rigby can dispatch it locally, it ships.

Envelope §3 + §5 corrected mid-session to remove production framing.

---

## S2759 CANDIDATES (Chris selects at open)

### Candidate 1 — Rigby-side dispatch-path conversion (fresh S2758 finding)

**Real finding surfaced by S2758 tool E2E verification:** Rigby's own PA loop dispatched `process_pa_chat_task` at conversation_id `pa-5fe224e5757f42c0` (S2758 pin) and hit `missing_acting_identity` — meaning the acting-user header was NOT attached at that dispatch path. Dispatch site is OUTSIDE the 4 S2757-converted sites.

**Scope for S2759:**
- Locate the exact Rigby-side dispatch (likely `core/services/unified_pa_entrypoint.py` or `views_assistant_bypass.py`)
- Convert to `apply_async_with_actor(process_pa_chat_task, request.user, kwargs=...)`
- Add regression test
- 1-PR close-ceremony bundle

**Value:** Fast turnaround; concrete finding-driven fix; validates that the S2758 tool actually feeds BATCH-FIX iteration.

### Candidate 2 — D2 canonical AgentExecution vs AgentTaskExecution decision routing

Three approaches (a/b/c) require Chris directive. Design SIGN + Rigby SIGN + Chris ratification.

### Candidate 3 — D4 HIGH-RISK task file wiring extension

Follow-up REPORT-ONLY PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`. Same discipline as S2756 REPORT-ONLY.

### Candidate 4 — Net-new engineering item

Per S2745 engineering-bias directive. Examples:
- New Command Center tile: tenant_boundary_violations dashboard tile
- Beat task: weekly REPORT-ONLY findings summary Deliverable
- New spider / UI page / capability

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2758 RETIRED (fresh mint required at S2759 open)

**Pin history (S2758 arc):**

- `pa-5fe224e5757f42c0` (label `s2758-recent-tenant-violations-tool`) minted S2758 open; **retired at S2758 close** (`updated_count=<n> previously_active=true retired=true`)

**Wrapper `tools/pa_local.sh:539` still points at `pa-5fe224e5757f42c0` (retired)** — intended failure mode forces S2759 first-action fresh mint before any other PA dispatch.

**S2759 open sequence (fresh terminal or continued session):**

```
context-kit orient

# Read this file end-to-end

# Try the S2758 tool first — verify it still surfaces expected findings
bash tools/pa_local.sh "Show me tenant_boundary_violations in the last 24h"

# Mint fresh pin scoped to selected candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

# Confirm wrapper repoint
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until the wrapper is repointed to the new pin.

---

## OPEN RUNTIME ITEMS (from S2758 close)

1. **Rigby-side dispatch-path conversion** — Candidate 1 above (fresh finding from S2758 tool)
2. **D2 AgentExecution vs AgentTaskExecution canonical decision** — Candidate 2
3. **D4 HIGH-RISK task file wiring extension** — Candidate 3
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed)
8. **D1 process_pa_chat_task payload strip** — deferred; requires HTTP-side bootstrap refactor
9. **D3 report-driven fix batch** — findings now accumulating via S2758 tool; second BATCH-FIX pass opens when signal is strong
10. **D5 local shim retirement** — depends on D2 canonical decision
11. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation; RUR-C2 / follow-on backlog

---

## Twin-pointer card (per memory rule feedback_twin_pointer_docs_at_boundaries)

📁 **Repo `/docs/` + `/core/` — S2758 tool artifacts:**

- **Schema:** `core/services/pa_tool_schemas.py` (ops_tool action enum + failure_kind param)
- **Handler:** `core/services/td_handlers_ops.py` (`_ops_tenant_boundary_violations` method after `_ops_celery_task_history`)
- **Test suite (10/10 passing):** `tests/security/test_ops_tool_tenant_boundary_violations.py`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md`
- **Prior handoff:** `docs/handoffs/SESSION_2758_OPS_TOOL_TENANT_BOUNDARY_VIOLATIONS_RATIFIED.md`
- **Predecessor I-0303 ratifications:**
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md`
- **Substrate that emits events this tool surfaces:** `core/security/task_enforcement.py`
- **Sibling ops_tool actions for adjacency reference:** `_ops_failure_signatures` + `_ops_celery_task_history` + `_ops_execution_search`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (§7.4.x close-ceremony + §7.6.1 SIGN watchpoint)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **PRIMARY**. **17 deliverables total** after S2758 close (15 pre-existing + 2 new).
  - Governance-truth (ratification envelopes):
    - `RATIFICATION_20260711_i0303_scoping`, `..._phase1_ledger`, `..._phase2_task_enforcement`, `..._phase3_report_only`, `..._phase3_batch_fix`
    - `RATIFICATION_20260711_ops_tool_tenant_boundary_violations` (filled at create)
  - Engineering-truth (content mirrors):
    - `I-0303 — Scoping / Audit Ledger / Phase 2 / Phase 3 REPORT-ONLY / Phase 3 BATCH-FIX First Pass` (5 mirrors)
    - `ops_tool.tenant_boundary_violations PA Tool (mirror)` (filled at create)
    - `I-0302 — Scoping / Audit Ledger / Design / Arc Close`
    - `I-0301 Phase 1 Audit Ledger`
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program workspace
- URL template: `/workspace?workspace_id=<uuid>&tab=work&sub=deliverables`

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2758 tool merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 through Phase 3 stage 2 first pass CLOSED · **S2758 tool surfaces findings for second BATCH-FIX pass planning** · RUR-C1 parent OPEN |
| Session pin | `pa-5fe224e5757f42c0` (label s2758-recent-tenant-violations-tool; retired at S2758 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-5fe224e5757f42c0` (retired; forces fresh mint at S2759 open) |
| Live infra state | Local-only per Chris S2758 directive; CI billing-blocked (`--admin` on merges) |
| RUR-C1 close-gate | Blocked until I-0303 arc closes AND all three arcs pass shared cross-tenant regression |
| I-0303 next move | **Rigby-side dispatch-path conversion (Candidate 1)** OR **D2 canonical decision** OR **D4 HIGH-RISK wiring** OR **net-new** — Chris selects at S2759 open |

---

## Recommended session-open protocol (S2759)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2758 tool envelope `RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md` §5 (E2E verification + real-finding discovery)
4. **First move:** exercise the S2758 tool — `bash tools/pa_local.sh "Show me tenant_boundary_violations in the last 24h"` — check for new findings since S2758 close
5. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at retired `pa-5fe224e5757f42c0`
6. Present findings-driven priority menu to Chris (Candidates 1–4 above)
7. Chris directs S2759 P0 selection
8. Mint fresh pin with candidate-scoped label
9. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2759:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md) — S2758 envelope (§5 real findings)
3. `core/services/pa_tool_schemas.py` — ops_tool schema
4. `core/services/td_handlers_ops.py` — ops_tool handler
5. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md) — Phase 3 BATCH-FIX first pass (Candidate 1 predecessor)
6. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_report_only.md) — Phase 3 REPORT-ONLY substrate
7. `core/security/task_enforcement.py` — substrate emitting events S2758 tool surfaces
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0 §7.4.x + §7.6.1
