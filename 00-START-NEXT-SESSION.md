# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2754 CLOSED — I-0303 SCOPING + PHASE 1 LEDGER RATIFIED; PHASE 2 AUTHORIZED

**Refreshed 2026-07-11 (SESSION 2754 CLOSED — two Chris D-verdicts: I-0303 scoping Q1..Q6 + Phase 1 audit ledger. Phase 2 authorized to open at S2755).**

**S2754 shipped (5 PRs total):**

- #3137 (`47cc13dd`) — I-0303 scoping ratified
- #3138 (`a957e225`) — I-0303 scoping placeholder fills + start-here refresh
- #3139 (`543ab9ad`) — **I-0303 Phase 1 Task Boundary Audit Ledger ratified**
- #3140 (this session's next PR) — Phase 1 placeholder fills + start-here refresh for S2755 Phase 2 (this file)
- Pin rotated at S2754 open: `pa-44541f01cbb14b46` (retired S2753) → `pa-2659dfa28e124f02` (label `i0303-scoping`; carries into S2755)

**Workspace deliverables created this session:**

| Deliverable | UUID | Workspace |
|---|---|---|
| `RATIFICATION_20260711_i0303_scoping` | `18194cab-b737-42bf-b747-1263af5771ae` | RUR-C1 Tenant Boundary Lockdown |
| `RATIFICATION_20260711_i0303_phase1_ledger` | `2020bc4f-ef7d-42e8-9ee5-38be928ba483` | RUR-C1 Tenant Boundary Lockdown |

---

## P0 — I-0303 PHASE 2 — DECORATOR + BASE-CLASS IMPLEMENTATION

**Authorized to open at S2754 Phase 1 ratification (PR #3139).** Target: 1 session (S2755).

**Scope per I-0303 scoping §8 Phase 2 + Phase 1 ledger §9 entry criteria:**

1. **Author `core/tenant_boundary_lockdown/task_enforcement.py`** with three components:
   - `@enforce_tenant_boundary(model=X, id_kwarg='...')` decorator for facade-tier tasks
   - `TenantScopedTask` Celery base class for new task classes
   - `@system_scope` marker decorator (per Q2 explicit opt-in)
2. **Import I-0302 predicate module** (`core/tenant_boundary_lockdown/predicates.py`) — leaf-module layering verified during scoping §3.5
3. **Uniform failure envelope** (per scoping §4 mandate): identical `reason_code='tenant_boundary_violation'`, identical `human_message` shape per I-0301 safety contract — regardless of decorator vs base-class choice
4. **Uniform trusted-source resolution contract** (per Q1 mandate): DB-row-derived identity first; signed dispatch header second; payload-supplied identity NEVER — enforced identically by both mechanisms
5. **Unit tests** (4 primary paths):
   - Happy path — task with `@enforce_tenant_boundary` succeeds when acting user owns the row
   - User-A attempts user-B row — task rejects fail-loud with `reason_code='tenant_boundary_violation'`; no mutation; no existence-oracle in `human_message`
   - System-task passthrough — `@system_scope`-marked task succeeds regardless of acting identity
   - Missing-identity rejection — task naming a user-owned model but with no resolvable acting user rejects fail-loud
6. **Rigby SIGN** on the enforcement module before Phase 3 opens
7. **Chris D-verdict** to open Phase 3

**Phase 2 authorization does NOT extend to Phase 3.** Phase 3 wiring requires separate Rigby SIGN + Chris ratification. Phase 3 dogfoods PLAYBOOK-7.5.1 three-PR staged codification.

---

## P0.5 — COST-THRESHOLD ADVANCE-TO-FREEZE ROUTING (still owed since S2753)

Not blocking Phase 2. Route joint Claude+Rigby recommendation on `--set-mode freeze` (shadow) to Chris for yes/no. 24.88h clean observation window at $6.66/$500 (1.333%) recorded S2753. Do NOT flip without D-verdict.

---

## P0.75 — CI BILLING STATUS CHECK (still owed)

Not blocking Phase 2. Latest S2753/S2754 check: run #885 all jobs failed with 2-sec no-step signature = billing block unchanged. `--admin` merge posture continues.

---

## SESSION PIN — CARRIES INTO S2755

**Pin `pa-2659dfa28e124f02`** (label `i0303-scoping`) minted S2754 open, carries through Phase 2 unless Chris directs a Phase-2-specific rotation. Consider re-labeling at S2755 open if scope shifts: `python manage.py session_lifecycle close --label i0303-phase2-module`.

Wrapper `tools/pa_local.sh:539` currently points at `pa-2659dfa28e124f02`.

---

## OPEN RUNTIME ITEMS (from S2754 close)

1. **I-0303 Phase 2 module authoring** — P0 above; authorized to open.
2. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no.
3. **P0.75 CI billing** — status check.
4. **PA celery worker bounce** — Rigby stall fix #3119 still not activated.
5. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed).
6. **AgentExecution/AgentTaskExecution canonical class Phase 2 pick** — Phase 1 §4.4 flagged duplicate-class caveat; Phase 2 must pick canonical.

---

## Twin-pointer card (per memory rule feedback_twin_pointer_docs_at_boundaries)

📁 **Repo `/docs/` — I-0303 arc + related artifacts:**

- **I-0303 arc scoping (RATIFIED S2754):** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`
- **I-0303 Phase 1 audit ledger (RATIFIED S2754):** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`
- **Ratification envelopes (both S2754):**
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`
  - `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md`
- **Predicate module (I-0302 Phase 2, will be imported by Phase 2 of I-0303):** `core/tenant_boundary_lockdown/predicates.py`
- **Regression harness (I-0302 Phase 4, will be extended in Phase 4 of I-0303):** `tests/security/`
- **Sibling I-0301 (CLOSED 2026-07-10):** `docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md` + `I-030199_...close.md`
- **Sibling I-0302 (CLOSED 2026-07-10):** `I-0302_scoping.md` + `I-030201_model_audit_ledger.md` (Phase 1 template) + `I-030299_i0302_arc_close.md`
- **Parent CAMPAIGN:** `docs/research/implementation/real_user_readiness/CAMPAIGN.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md` (§7.5.1 for Phase 3; §7.6.1 for every phase-SIGN; §7.4.x for arc close)
- **Prior ratification envelope (v0.5.0):** `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md`
- **Prior handoff:** `docs/handoffs/SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **PRIMARY** for I-0303 execution + phase ratifications
  - `RATIFICATION_20260711_i0303_scoping` (`18194cab-b737-42bf-b747-1263af5771ae`) — scoping envelope
  - `RATIFICATION_20260711_i0303_phase1_ledger` (`2020bc4f-ef7d-42e8-9ee5-38be928ba483`) — Phase 1 envelope
  - Phase 2 module ratification will land here as new deliverable
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
  - `RATIFICATION_20260711_PLAYBOOK_v0_5_0` (`4c322f48-3d0b-4e32-8a30-15a08400f887`)
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program workspace
- URL template: `/workspace?workspace_id=<uuid>&tab=work&sub=deliverables`

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `543ab9ad` (post-S2754 Phase 1 ratification merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · **I-0303 scoping RATIFIED (S2754); Phase 1 CLOSED (S2754); Phase 2 authorized** · RUR-C1 parent OPEN |
| Session pin | `pa-2659dfa28e124f02` (label i0303-scoping; carries into S2755) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-2659dfa28e124f02` |
| Live infra state | Cost threshold monitor mode $500/mo; PA celery worker pre-#3119; CI billing-blocked (`--admin` on merges) |
| RUR-C1 close-gate | Blocked until I-0303 arc closes AND all three arcs pass shared cross-tenant regression |
| I-0303 next phase | **Phase 2 (Decorator + Base-Class Implementation) — authorized to open** |

---

## Recommended session-open protocol (S2755)

1. `context-kit orient`
2. Read this file end-to-end
3. Read Phase 1 ledger `I-030301_task_boundary_audit_ledger.md` §9 (Phase 2 entry criteria) + §11 (handoff summary)
4. Read scoping doc §4 (enforcement mechanism framework) + §8 Phase 2 charter
5. Read I-0302 Phase 2 predicate module `core/tenant_boundary_lockdown/predicates.py` — Phase 2 of I-0303 imports it
6. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at `pa-2659dfa28e124f02`
7. **P0.5** — cost-threshold advance-to-freeze routing (Claude+Rigby agree first → Chris yes/no) — optional, can defer if Phase 2 substantive
8. **P0.75** — CI billing status check
9. **P0** — Phase 2 module authoring:
   - Draft `core/tenant_boundary_lockdown/task_enforcement.py` skeleton
   - Import predicate module + verify layering
   - Draft 4 unit tests (happy / cross-tenant / system-scope / missing-identity)
   - Claude+Rigby joint agreement on module shape → Chris yes/no
   - Ship as substrate PR (dogfooding PLAYBOOK-7.5.1 REPORT-ONLY? — actually Phase 2 is enforcement-module authoring, not staged codification of enforcement flip; Phase 3 is where the three-PR pattern applies)

---

## Reference documents

Ordered by frequency of use at S2755 Phase 2:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md) — Phase 1 ratified ledger (§9 entry criteria + §11 handoff)
3. [`docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`](docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md) — scoping (§4 enforcement framework + §8 Phase 2 charter)
4. `core/tenant_boundary_lockdown/predicates.py` — I-0302 Phase 2 predicate module (Phase 2 of I-0303 imports)
5. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md) — Phase 1 ratification envelope
6. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md) — scoping ratification envelope (Q1..Q6 D-verdicts)
7. [`docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md`](docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md) — I-0302 Phase 2 design (template for I-0303 Phase 2)
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0 body
