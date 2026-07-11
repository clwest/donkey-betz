# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2755 CLOSED — I-0303 PHASE 2 TASK-ENFORCEMENT MODULE RATIFIED

**Refreshed 2026-07-11 (SESSION 2755 CLOSED — Chris D-verdict "Approved!" on I-0303 Phase 2 module after Rigby double-SIGN cycle. Phase 3 authorized to open at S2756).**

**S2755 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- Substrate code (599 lines): `core/security/task_enforcement.py`
- Contract §10 amendments: `tenant_boundary_violation` reason code + `TENANT` support-code component (`reason_codes.py` + `error_envelope.py` + `support_code.py`)
- Test suite (18/18 passing, 191s local runtime): `tests/security/test_i0303_p2_task_enforcement.py`
- Ratification envelope: `RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- 6 stale doc path amendments in scoping + Phase 1 ledger
- Session-open pin rotation on `tools/pa_local.sh:539` (S2755 protocol)
- Handoff + docs cascade + close bookmark

**Workspace deliverables created this session:**

| Deliverable | UUID | Workspace |
|---|---|---|
| `RATIFICATION_20260711_i0303_phase2_task_enforcement` | `66102e76-1ecd-4407-88b9-97000481d73f` | RUR-C1 Tenant Boundary Lockdown |
| `I-0303 — Phase 2 Task-Enforcement Module (mirror)` | `4fba089a-9743-4f9c-997e-66b1bb5e926f` | RUR-C1 Tenant Boundary Lockdown |

---

## P0 — I-0303 PHASE 3 — PER-TASK ENFORCEMENT APPLICATION

**Authorized to open at S2755 Phase 2 ratification.** Target: 1-3 sessions (Rigby S2754 SIGN elasticity — depends on how many "mixed identity" tasks Phase 1 audit surfaces during application).

**Scope per I-0303 scoping §8 Phase 3 + PLAYBOOK-7.5.1 staged codification:**

1. **REPORT-ONLY substrate PR** — apply `@enforce_tenant_boundary` (or `TenantScopedTask` base) to every user-owned-model-touching task from Phase 1 audit; wire in warn-only mode (log violations, do NOT raise). Coverage: Phase 1 REG-RISK targets first (`execute_agent`, `summarize_conversation_task`, `process_pa_chat_task`), then HIGH-RISK task files (`tasks.py` facade + `tasks_agents.py` + `tasks_initiatives.py` + `tasks_conversations.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`).
2. **BATCH-FIX PR** — resolve all report-only findings from step 1. Every violation classified either (a) legitimate acting-user resolution + header attachment fix at dispatch site, OR (b) Phase 3 substrate task rework (Q6 refactor from filter → row-ID dispatch).
3. **ENFORCEMENT-FLIP PR** — flip warn-only to hard-gate. Any task lacking `@enforce_tenant_boundary` OR `@system_scope` fails registered per Q2 fail-safe default.
4. **Dispatch-site helper** — Phase 3 substrate adds a helper `apply_async_with_actor(task, user, ...)` that always attaches `apply_async(..., headers={'x-acting-user-id': str(user.pk)})` from Django's `request.user`. All HTTP dispatch sites converted.
5. **AgentExecution / AgentTaskExecution duplicate-class resolution** — Phase 1 §4.4 caveat surfaces here. Pick canonical class (I-0302 ratified `AgentExecution`) + convert legacy `AgentTaskExecution` touches at `tasks_agents.py:493-538` etc.
6. **Rigby SIGN** at each stage (REPORT-ONLY, BATCH-FIX, ENFORCEMENT-FLIP). PLAYBOOK-7.6.1 watchpoint-attestation shape.
7. **Chris D-verdict** on each stage.

**Phase 3 authorization does NOT extend to Phase 4.** Phase 4 (async-boundary regression harness) requires separate Rigby SIGN + Chris ratification.

---

## P0.5 — COST-THRESHOLD ADVANCE-TO-FREEZE ROUTING (still owed since S2753)

Not blocking Phase 3. Route joint Claude+Rigby recommendation on `--set-mode freeze` (shadow) to Chris for yes/no. 24.88h clean observation window at $6.66/$500 (1.333%) recorded S2753.

---

## P0.75 — CI BILLING STATUS CHECK (still owed)

Not blocking Phase 3. `--admin` merge posture continues until Chris says billing is fixed.

---

## SESSION PIN — S2755 RETIRED (fresh mint required at S2756 open in fresh terminal)

**Pin history (S2755 arc):**
- `pa-f3637b736efb4c07` (label `i0303-phase2-module`) minted S2755 open; **retired at S2755 close** (`updated_count=<n> previously_active=true retired=true`)

**Wrapper `tools/pa_local.sh:539` still points at `pa-f3637b736efb4c07` (retired)** — intended failure mode forces S2756 first-action fresh mint before any other PA dispatch.

**S2756 open sequence (in fresh terminal):**

```
# Session-open orient (feedback rule)
context-kit orient

# Read this file end-to-end

# Mint fresh pin scoped to Phase 3 REPORT-ONLY work
python manage.py session_lifecycle open --label i0303-phase3-report-only

# Confirm wrapper repoint
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until the wrapper is repointed to the new pin.

---

## OPEN RUNTIME ITEMS (from S2755 close)

1. **I-0303 Phase 3 REPORT-ONLY substrate authoring** — P0 above; authorized to open.
2. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no.
3. **P0.75 CI billing** — status check.
4. **PA celery worker bounce** — Rigby stall fix #3119 still not activated.
5. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed).
6. **AgentExecution/AgentTaskExecution canonical class Phase 3 selection** — Phase 1 §4.4 flagged; Phase 3 REPORT-ONLY forces the pick.
7. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation; RUR-C2 / follow-on backlog.

---

## Twin-pointer card (per memory rule feedback_twin_pointer_docs_at_boundaries)

📁 **Repo `/docs/` + `/core/` — I-0303 Phase 2 artifacts:**

- **Phase 2 substrate module:** `core/security/task_enforcement.py`
- **Predicate module dependency (I-0302 Phase 2):** `core/security/object_authz.py`
- **Contract §10 amendments:** `core/security/reason_codes.py` (tenant_boundary_violation) + `core/security/error_envelope.py` (_REASON_TO_COMPONENT) + `core/security/support_code.py` (_ALLOWED_COMPONENTS)
- **Test suite:** `tests/security/test_i0303_p2_task_enforcement.py`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`
- **Phase 1 ledger (ratified S2754):** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`
- **Scoping (ratified S2754):** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`
- **Sibling I-0301 (CLOSED 2026-07-10):** `docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md` + `I-030199_...close.md`
- **Sibling I-0302 (CLOSED 2026-07-10):** `I-0302_scoping.md` + `I-030201_model_audit_ledger.md` + `I-030299_i0302_arc_close.md`
- **Parent CAMPAIGN:** `docs/research/implementation/real_user_readiness/CAMPAIGN.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (§7.5.1 for Phase 3 staged codification; §7.6.1 for every phase SIGN; §7.4.x for arc close)
- **Prior handoff:** `docs/handoffs/SESSION_2754_I0303_SCOPING_AND_PHASE1_CLOSED.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **PRIMARY** for I-0303 execution + phase ratifications. **11 deliverables total** after S2755 close (9 pre-existing + 2 new).
  - Governance-truth (ratification envelopes):
    - `RATIFICATION_20260711_i0303_scoping` (`18194cab-b737-42bf-b747-1263af5771ae`)
    - `RATIFICATION_20260711_i0303_phase1_ledger` (`2020bc4f-ef7d-42e8-9ee5-38be928ba483`)
    - `RATIFICATION_20260711_i0303_phase2_task_enforcement` (`66102e76-1ecd-4407-88b9-97000481d73f`)
  - Engineering-truth (content mirrors):
    - `I-0303 — Scoping (mirror)` — `f8af6aad-05ae-4d9f-b61b-3a81d6604b57`
    - `I-0303 — Audit Ledger (mirror)` — `0462ac90-dc11-4196-a549-150ff271b7e3`
    - `I-0303 — Phase 2 Task-Enforcement Module (mirror)` — `4fba089a-9743-4f9c-997e-66b1bb5e926f`
    - `I-0302 — Scoping (mirror)` — `80c83e8c-d130-4b65-9204-de279fae6b83`
    - `I-030201 — Audit Ledger (mirror)` — `c16e582c-ed09-4747-9d77-a4804a746b99`
    - `I-030202 — Design (mirror)` — `e916cbe9-1bb9-4b17-a54d-daed25725efb`
    - `I-030299 — Arc Close (mirror)` — `5d879edd-d654-4fd3-b955-89f700c8416a`
    - `I-0301 Phase 1 Audit Ledger — HTTP AllowAny Surface Classification` — `1ca36f84-...`
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
  - `RATIFICATION_20260711_PLAYBOOK_v0_5_0` (`4c322f48-3d0b-4e32-8a30-15a08400f887`)
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program workspace
- URL template: `/workspace?workspace_id=<uuid>&tab=work&sub=deliverables`

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2755 Phase 2 ratification merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · **I-0303 scoping+Phase 1+Phase 2 CLOSED; Phase 3 authorized** · RUR-C1 parent OPEN |
| Session pin | `pa-f3637b736efb4c07` (label i0303-phase2-module; retired at S2755 close) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-f3637b736efb4c07` (retired; forces fresh mint at S2756 open) |
| Live infra state | Cost threshold monitor mode $500/mo; PA celery worker pre-#3119; CI billing-blocked (`--admin` on merges) |
| RUR-C1 close-gate | Blocked until I-0303 arc closes AND all three arcs pass shared cross-tenant regression |
| I-0303 next phase | **Phase 3 (Per-Task Enforcement Application) — authorized to open** |

---

## Recommended session-open protocol (S2756)

1. `context-kit orient`
2. Read this file end-to-end
3. Read Phase 2 ratification envelope `RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md` §2 (ratified deliverables) + §5 (Phase 3 opening authorization)
4. Read Phase 1 ledger §3 (task file inventory), §4 (per-model exemplars), §5 (REG-RISK exemplars), §7 (system-scope candidates)
5. Read Phase 2 module `core/security/task_enforcement.py` — start with docstring, then §Public API section
6. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at retired `pa-f3637b736efb4c07`
7. **P0.5** — cost-threshold advance-to-freeze routing (Claude+Rigby agree first → Chris yes/no) — optional
8. **P0.75** — CI billing status check
9. **P0** — Phase 3 REPORT-ONLY substrate authoring:
   - Mint fresh pin: `python manage.py session_lifecycle open --label i0303-phase3-report-only`
   - Draft Phase 3 REPORT-ONLY PR shape via joint agreement Claude+Rigby before touching code
   - Wire warn-only mode on top of `@enforce_tenant_boundary` module (per PLAYBOOK-7.5.1)
   - REG-RISK targets first: `execute_agent` + `summarize_conversation_task` + `process_pa_chat_task`
   - Then HIGH-RISK task files per Phase 1 §3 bucketing

---

## Reference documents

Ordered by frequency of use at S2756 Phase 3 REPORT-ONLY:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md) — Phase 2 envelope (§5 Phase 3 authorization + §2 module contract)
3. `core/security/task_enforcement.py` — Phase 2 module (Phase 3 applies it)
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md) — Phase 1 ledger (§3 task files, §4 REG-RISK, §5 acting-identity, §7 system-scope)
5. [`docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`](docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md) — scoping (§8 Phase 3 charter)
6. `core/security/object_authz.py` — I-0302 Phase 2 predicate module (Phase 2 imports; Phase 3 depends transitively)
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0 §7.5.1 (three-PR staged codification) + §7.6.1 (SIGN watchpoint-attestation) + §7.4.x (close ceremony)
