# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2754 CLOSED (partial) — I-0303 SCOPING RATIFIED; PHASE 1 AUDIT LEDGER AUTHORIZED

**Refreshed 2026-07-11 (SESSION 2754 — Chris D-verdict `"agree all"` on I-0303 scoping Q1..Q6; Phase 1 authorized to open).**

**S2754 shipped:**

- **I-0303 scoping RATIFIED** — third and final RUR-C1 child arc opens. `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (322 lines post-Rigby-edits). Ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`. Workspace deliverable: `18194cab-b737-42bf-b747-1263af5771ae` in `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (RUR-C1 Tenant Boundary Lockdown).
- **First arc ratification under Claude+Rigby-agree-first workflow rule** (Chris S2753 directive). Rigby SIGN edits applied inline BEFORE routing joint recommendation. Chris presented with one joint proposal, not a decision menu. Recorded in envelope §2.3 as first-trigger evidence of the workflow rule.
- **First arc opened under Playbook v0.5.0** — will dogfood PLAYBOOK-7.5.1 (three-PR staged codification) at Phase 3; PLAYBOOK-7.6.1 (watchpoint SIGN) at every phase/arc close; PLAYBOOK-7.4.1/7.4.2/7.4.3 (close-ceremony delivery) at arc close.
- **PA pin rotation** — `pa-44541f01cbb14b46` (retired S2753 close) → `pa-2659dfa28e124f02` (label `i0303-scoping`; minted S2754 open via `session_lifecycle open`).
- **Close-bundle PR** #3137 merged (47cc13dd).

**Six Chris D-verdicts (Q1..Q6):**

| Q | Topic | Verdict |
|---|---|---|
| Q1 | Trusted-source hierarchy | MANDATE (DB-row first; signed header second; payload NEVER) |
| Q2 | System-task marker | EXPLICIT OPT-IN `@system_scope` (fail-safe) |
| Q3 | `AsyncBoundaryProbe` shape | NEW PROBE CLASS |
| Q4 | Coverage-gap threshold | I-0302 PRECEDENT (per-exemption SIGN + ratify) |
| Q5 | RUR-C1 close SIGN scope | ONE PARENT-CLOSE EVENT |
| Q6 | Canonical row reference | ROW-ID DISPATCH ONLY for user-owned-model tasks |

---

## P0 — I-0303 PHASE 1 TASK BOUNDARY AUDIT LEDGER

**Authorized to open at S2754 scoping ratification.** Target: 1 session (S2755 fresh, or S2754 continuation if context permits).

**Scope:**

- Materialize per-task boundary audit ledger as workspace deliverable under RUR-C1 workspace `fcd7e683-3bfe-4d35-9704-0e54dd587ea1`
- Per task touching user-owned model (Deliverable, Initiative, ChatConversation, AgentExecution, Document):
  - Classify **acting-identity source**: session-derived / payload-supplied / mixed / none
  - Classify **existing verification**: present / absent / partial
  - Classify **row reference shape**: row-ID / filter / query (Q6-driven; filter/query rows need Phase 3 refactor or explicit exemption)
- **System-task classification**: which tasks are legitimately system-scope (`@system_scope` opt-in per Q2)
- **Preliminary evidence at HEAD `47cc13dd`:** 19 `core/tasks*.py` files; 415 total Celery tasks per PLATFORM_INVENTORY; 6 highest-signal files (agents/content/conversations/initiatives/tasks.py/executor)
- **Deliverable:** audit ledger + Rigby SIGN before Phase 2 opens

**Phase 2 (Decorator + Base-Class Implementation)** is the next phase after Phase 1 close. Do NOT begin Phase 2 substrate work under Phase 1 authorization.

---

## P0.5 — COST-THRESHOLD ADVANCE-TO-FREEZE ROUTING (owed since S2753)

**Do this in parallel or before Phase 1 substrate work.** Not blocking Phase 1.

S2753 P0.5 check-in: 24.88h clean observation window ($6.66 / $500 = 1.333%; no anomalies). Route joint Claude+Rigby recommendation on `--set-mode freeze` (shadow) to Chris for yes/no. Do NOT flip without D-verdict.

---

## P0.75 — CI BILLING STATUS CHECK (still owed)

Latest S2753/S2754 check: run #885 all jobs failed with 2-sec no-step signature = billing block unchanged. `--admin` merge posture continues. Report at S2755 open whether billing has cleared.

---

## SESSION PIN — CARRIES INTO S2755

**Pin `pa-2659dfa28e124f02`** (label `i0303-scoping`) minted S2754 open, carries through Phase 1 unless Chris directs a scope-level rotation for a different label (e.g., `i0303-phase1-audit`).

Wrapper `tools/pa_local.sh:539` currently points at `pa-2659dfa28e124f02`. If S2755 opens Phase 1 with a scope-specific pin, run `python manage.py session_lifecycle close` (retire current + mint fresh + rewrite wrapper atomically) with `--label i0303-phase1-audit`.

---

## OPEN RUNTIME ITEMS (from S2754 close)

1. **I-0303 Phase 1 audit ledger** — P0 above; authorized to open.
2. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no.
3. **P0.75 CI billing** — status check; unblocks lint-enforcement flips + recovery gates.
4. **PA celery worker bounce** — Rigby stall fix #3119 still not activated. Deferred to Chris.
5. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed). Not opened at S2754; opens per Chris directive when I-0303 substrate needs parallel work.

---

## Twin-pointer card (per memory rule feedback_twin_pointer_docs_at_boundaries)

📁 **Repo `/docs/` — current-arc + related artifacts:**

- **I-0303 arc scoping (RATIFIED S2754):** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`
- **I-0303 scoping ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`
- **Sibling I-0301 (CLOSED 2026-07-10):** `docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md` + `I-030199_tenant_boundary_lockdown_implementation_close.md`
- **Sibling I-0302 (CLOSED 2026-07-10):** `I-0302_scoping.md` through `I-030299_i0302_arc_close.md` in same dir
- **Parent CAMPAIGN:** `docs/research/implementation/real_user_readiness/CAMPAIGN.md` (§4 arc slot; §5 dependency graph)
- **Playbook v0.5.0 (governing close-ceremony discipline):** `docs/ENGINEERING_PLAYBOOK.md`
- **Prior ratification envelopes:** `docs/research/implementation/RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md`, `RATIFICATION_2026-07-10_i0302_arc_close.md`
- **Handoffs:** `docs/handoffs/SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md` (prior); S2754 handoff to be created if session properly closes (partial close so far — I-0303 scoping ratified but Phase 1 pending)

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **PRIMARY** for I-0303 execution
  - `RATIFICATION_20260711_i0303_scoping` (`18194cab-b737-42bf-b747-1263af5771ae`) — this session's ratification envelope
  - Phase 1 audit ledger will land here as a new deliverable
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
  - `RATIFICATION_20260711_PLAYBOOK_v0_5_0` (`4c322f48-3d0b-4e32-8a30-15a08400f887`) — v0.5.0 amendment
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program workspace
- URL template: `/workspace?workspace_id=<uuid>&tab=work&sub=deliverables`

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `47cc13dd` (S2754 I-0303 scoping ratification merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · **I-0303 OPENED at scoping (S2754)** — Phase 1 authorized · RUR-C1 parent OPEN |
| Session pin | `pa-2659dfa28e124f02` (label i0303-scoping; carries into S2755) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-2659dfa28e124f02` |
| Live infra state | Cost threshold monitor mode $500/mo; PA celery worker running pre-#3119 code; CI billing-blocked (`--admin` on merges) |
| RUR-C1 close-gate | Blocked until I-0303 closes AND all three arcs pass shared cross-tenant regression |
| I-0303 next phase | **Phase 1 (Task Boundary Audit Ledger) — authorized to open** |

---

## What S2754 shipped (this session)

| PR | Content | Notes |
|---|---|---|
| #3137 (47cc13dd) | I-0303 scoping doc + ratification envelope + pa_local.sh pin update | Single close-bundle PR (dogfooding PLAYBOOK-7.4.1); cascade deferred to next session or bundled with next PR |

**Not yet shipped in S2754 close:**
- 4-step docs cascade + build_docs_provenance (feedback_docs_cascade_at_every_close rule) — DEFERRED to Phase 1 open or S2754 explicit close if session continues
- S2754 close handoff (SESSION_2754_*.md) — DEFERRED
- Phase 1 audit ledger open (P0 above)

---

## Recommended session-open protocol (S2755)

1. `context-kit orient`
2. Read this file end-to-end (all sections)
3. Read `RATIFICATION_2026-07-11_i0303_scoping.md` §3 (D-verdicts Q1..Q6) — these are the invariants Phase 1 audit must respect
4. Read `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` §3, §8 Phase 1 — preliminary audit + Phase 1 charter
5. Read `docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md` Phase 1 execution — template for I-0303 Phase 1 shape
6. Verify runtime state: `git log --oneline -5`; confirm `tools/pa_local.sh:539` points at `pa-2659dfa28e124f02`
7. **P0.5** — cost-threshold advance-to-freeze routing (Claude+Rigby agree first → Chris yes/no)
8. **P0.75** — CI billing status check
9. **P0** — Phase 1 audit ledger open (Claude+Rigby joint plan → Chris yes/no on Phase 1 opening scope)

---

## Reference documents

Ordered by frequency of use at S2755:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`](docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md) — ratified scoping (Phase 1 charter §8)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md) — Chris D-verdicts Q1..Q6
4. [`docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md`](docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md) — sibling arc template
5. [`docs/research/implementation/real_user_readiness/CAMPAIGN.md`](docs/research/implementation/real_user_readiness/CAMPAIGN.md) — parent program §4 arc slot; §5 dependency graph
6. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0 ratified body (Phase 3 uses §7.5.1; every SIGN uses §7.6.1)
