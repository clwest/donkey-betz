# Session 2754 — I-0303 Scoping + Phase 1 Task Boundary Audit Ledger Ratified

**Date:** 2026-07-11
**Predecessor:** S2753 (Playbook v0.5.0 ratified; pin `pa-44541f01cbb14b46` retired at S2753 close)
**Successor:** S2755 (I-0303 Phase 2 — Decorator + Base-Class Implementation authoring)
**Session pin:** `pa-2659dfa28e124f02` (label `i0303-scoping`; **retired at S2754 close per Chris directive** — `updated_count=6 previously_active=true retired=true`; wrapper `tools/pa_local.sh:539` still points at retired pin as intended failure mode forcing S2755 first-action fresh mint)
**HEAD at open:** `ebf69e966` (before S2753 v0.5.0 ratification bundle)
**HEAD at close:** `fe1cf38e` (post-Phase 1 placeholder-fills merge #3140)

---

## §1 Delivery Ledger

Five PRs merged this session. Two full ratifications (scoping + Phase 1) with placeholder-fills follow-ups per each. Dogfooded PLAYBOOK-7.4.1 close-ceremony 1-PR bundle across both ratifications.

| # | PR | Merge SHA | Content |
|---|---|---|---|
| 1 | #3137 | `47cc13dd` | I-0303 scoping ratified — scoping doc + envelope + pa_local.sh pin update |
| 2 | #3138 | `a957e225` | Scoping placeholder fills + start-here refresh for Phase 1 |
| 3 | #3139 | `543ab9ad` | I-0303 Phase 1 Task Boundary Audit Ledger ratified — ledger + envelope |
| 4 | #3140 | `fe1cf38e` | Phase 1 placeholder fills + start-here refresh for Phase 2 |
| 5 | (this PR) | pending | S2754 close bookmark — pin retire + handoff + cascade |

---

## §2 Two Ratifications, One Session

### §2.1 I-0303 Scoping Ratified

- **Scoping doc:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (322 lines post-Rigby-edits)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`
- **Workspace deliverable:** `18194cab-b737-42bf-b747-1263af5771ae` in `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (RUR-C1 Tenant Boundary Lockdown)
- **Rigby SIGN turn 1:** SCOPING RATIFY WITH EDITS — 4 axis edits + Q6 addition, applied inline
- **Chris D-verdict:** `"agree all"` on Q1..Q6

**Six ratified D-verdicts (Q1..Q6):**

| Q | Topic | Verdict |
|---|---|---|
| Q1 | Trusted-source hierarchy | MANDATE (DB-row first; signed header second; payload NEVER) |
| Q2 | System-task marker | EXPLICIT OPT-IN `@system_scope` (fail-safe) |
| Q3 | `AsyncBoundaryProbe` shape | NEW PROBE CLASS |
| Q4 | Coverage-gap threshold | I-0302 PRECEDENT (per-exemption SIGN + ratify) |
| Q5 | RUR-C1 close SIGN scope | ONE PARENT-CLOSE EVENT |
| Q6 | Canonical row reference | ROW-ID DISPATCH ONLY for user-owned-model tasks |

### §2.2 I-0303 Phase 1 Task Boundary Audit Ledger Ratified

- **Ledger doc:** `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md` (~380 lines post-Rigby-edits)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md`
- **Workspace deliverable:** `2020bc4f-ef7d-42e8-9ee5-38be928ba483` in same RUR-C1 workspace
- **Rigby SIGN turn 1:** LEDGER RATIFY WITH EDITS — 2 axis edits, applied inline (§3 traffic note + Phase-3-first list; §7.3 system-scope justification test)
- **Chris D-verdict:** `"agree all"`

**Phase 1 substantive findings:**

- **407 Celery task registrations** at HEAD `47cc13dd` across 19 `core/tasks*.py` files
- **Two-tier task layer:** `core/tasks.py` facade (370 registrations) delegates to domain `_impl_*`; `tasks_agents.py` is Tier-0 direct-registered (7 tasks)
- **2 confirmed REG RISK at HEAD:**
  - `execute_agent(execution_id)` at `tasks_agents.py:493-538` — no acting-user re-verification against `AgentTaskExecution.user_id` (Q1 spirit violation)
  - `summarize_conversation_task(conversation_id, user_id=None)` at `tasks_conversations.py:3463` — payload-supplied `user_id` (Q1 explicit violation)
- **1 traffic-informed Phase-3-first target:** `process_pa_chat_task` (924 runs/7d — highest non-system-loop volume per Rigby `ops_tool.top_consumers`)
- **4 confirmed system-scope files:** `tasks_beat_health`, `tasks_body_systems`, `tasks_cost_protection`, `tasks_spiders`
- **7 HIGH-RISK task files** bucketed for Phase 3 wiring priority

---

## §3 New Workflow Rules Exercised

### §3.1 Claude+Rigby-agree-first (S2753 directive)

Both ratifications this session followed the agree-first pattern:

- Claude drafted → Rigby SIGN turn 1 → Rigby edits applied inline → joint recommendation to Chris → Chris `"agree all"`

Chris was never presented with an unresolved decision menu. Six ratification decisions (Q1..Q6 scoping + Phase 1 ledger + 2 sets of Rigby edits) all landed as joint recommendations for binary yes/no.

**First-trigger evidence recorded** at scoping ratification envelope §2.3. Second trigger this same session (Phase 1 ledger). Pattern is holding under real use.

### §3.2 Twin-pointer docs card (S2754 directive)

Chris directive at S2754 open: at any context/session boundary, surface a card naming EXACTLY where current-arc artifacts live in BOTH the repo `/docs/` tree AND the workspace UI `/workspaces` surface.

**First-trigger applied** during this session's context load + at session close (this handoff §7). Twin-pointer discipline is now a first-class deliverable at every boundary.

### §3.3 Rigby workspace deliverable discipline

Post-create ORM cleanup pattern per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` applied to both workspace deliverables. Diagnostic markers cleared; titles cleaned of "Rigby:" prefix; bodies mirrored (16309 chars scoping envelope; 10947 chars Phase 1 envelope).

---

## §4 PA Pin Rotation Discipline

- **S2753 close:** pin `pa-44541f01cbb14b46` retired.
- **S2754 open:** pin `pa-2659dfa28e124f02` minted via `python manage.py session_lifecycle open --label i0303-scoping` (atomic mint + wrapper rewrite).
- **S2754 close:** pin `pa-2659dfa28e124f02` retired per Chris directive. `session_tool.retire` returned `updated_count=6 previously_active=true retired=true`.

Wrapper `tools/pa_local.sh:539` intentionally left pointing at the retired pin as the intended failure mode — forces S2755's first action to be a fresh mint + wrapper re-point before any other PA dispatch.

**S2755 open sequence:**

```
python manage.py session_lifecycle open --label i0303-phase2-module
# Automatically mints fresh pin + rewrites wrapper line 539 atomically
```

---

## §5 Phase 2 Charter (P0 for S2755)

Per Phase 1 ratification §4:

- Author `core/tenant_boundary_lockdown/task_enforcement.py`:
  - `@enforce_tenant_boundary(model=X, id_kwarg='...')` decorator (facade-tier tasks)
  - `TenantScopedTask` Celery base class (new task classes)
  - `@system_scope` marker decorator (per Q2 explicit opt-in)
- Import I-0302 predicate module (`core/tenant_boundary_lockdown/predicates.py`); leaf-module layering verified
- Uniform failure envelope (identical `reason_code='tenant_boundary_violation'` + `human_message` per I-0301 safety contract) regardless of mechanism
- Uniform trusted-source resolution contract (DB-row-derived first; signed header second; payload NEVER) regardless of mechanism
- Unit tests (4 primary paths): happy / cross-tenant / system-scope-passthrough / missing-identity-rejection
- Rigby SIGN + Chris ratification before Phase 3 opens
- Target: 1 session (S2755)

**Phase 3 (which Phase 2 authorizes downstream) will dogfood PLAYBOOK-7.5.1 three-PR staged codification.** Phase 3 wiring priority per Phase 1 ledger §3:

1. `execute_agent(execution_id)` — Q1 spirit REG RISK
2. `summarize_conversation_task(conversation_id, user_id=None)` — Q1 explicit REG RISK
3. `process_pa_chat_task` — highest traffic (Phase 2 classification target)
4. `execute_agent_task` — dispatch path adjacent to `execute_agent`

---

## §6 Open Runtime Items Carrying to S2755

1. **I-0303 Phase 2 module authoring** — P0; authorized to open.
2. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no. 24.88h clean observation window from S2753.
3. **P0.75 CI billing status** — still blocked at S2754 close; `--admin` merge continues.
4. **PA celery worker bounce** — Rigby stall fix #3119 still not activated.
5. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed); not opened at S2754.
6. **AgentExecution/AgentTaskExecution canonical class Phase 2 pick** — Phase 1 §4.4 flagged duplicate-class caveat; Phase 2 must pick canonical.

---

## §7 Twin-Pointer Card (session close)

📁 **Repo `/docs/` — S2754 canonical artifacts:**

- I-0303 arc scoping: `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`
- I-0303 Phase 1 audit ledger: `docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`
- Scoping ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`
- Phase 1 ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md`
- This handoff: `docs/handoffs/SESSION_2754_I0303_SCOPING_AND_PHASE1_CLOSED.md`
- Next-session priorities: `00-START-NEXT-SESSION.md` (Phase 2 charter)
- Playbook v0.5.0: `docs/ENGINEERING_PLAYBOOK.md` (§7.5.1 for Phase 3; §7.6.1 for phase-SIGN; §7.4.x for arc close)
- Predicate module (Phase 2 imports): `core/tenant_boundary_lockdown/predicates.py`
- Regression harness (Phase 4 extends): `tests/security/`

🖥️ **Workspace UI `/workspaces` — S2754 canonical deliverables:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — PRIMARY workspace for I-0303
  - `RATIFICATION_20260711_i0303_scoping` (`18194cab-b737-42bf-b747-1263af5771ae`)
  - `RATIFICATION_20260711_i0303_phase1_ledger` (`2020bc4f-ef7d-42e8-9ee5-38be928ba483`)
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance
  - `RATIFICATION_20260711_PLAYBOOK_v0_5_0` (`4c322f48-3d0b-4e32-8a30-15a08400f887`)
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program

URL template: `/workspace?workspace_id=<uuid>&tab=work&sub=deliverables`

---

## §8 What This Session Taught Us About How to Do Research

Per feedback rule `feedback_xx99_meta_methodology_section`, scoped to S2754 close.

### §8.1 What worked cleanly

- **Two-turn Claude+Rigby-agree-first flow.** Both ratifications this session converged in a single Rigby SIGN turn (with edits applied inline). Chris never had to arbitrate between Claude and Rigby. Second in-wild trigger of the workflow rule (first was v0.5.0 SIGN at S2753); rule is holding under real use.
- **Rigby `ops_tool.top_consumers` traffic anchor.** Phase 1 ledger §3 traffic note came from Rigby's SIGN — Rigby pulled 7-day top-consumer data unprompted and used it to elevate `process_pa_chat_task` from LOW-RISK bucketing to Phase-3-first priority. Traffic-informed prioritization emerged from Rigby's SIGN discipline, not Claude's scoping.
- **Twin-pointer discipline as first-class deliverable.** Chris directive at S2754 open established that documentation pointers at boundaries are a durable pattern, not just tracking friction. Chris explicitly framed the `/docs/` + workspace surfaces as demonstrations of AI collaboration with minimum human interference. Twin-pointer is now a memory rule + a session-close ritual.

### §8.2 What to codify (candidacy)

- **Phase 1 SAMPLED-not-exhaustive discipline** — I-0302 Phase 1 established the sampled-audit pattern (Rigby F4 amendment 2026-07-10); I-0303 Phase 1 inherited it cleanly this session. Two triggers now. Candidate for Playbook v0.6 codification under §7.5 or §7.6 activation (arc-phase audit discipline).
- **Post-Rigby-create ORM diagnostic cleanup** — the `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` memory rule was created in S2753 close-out; this session exercised the workaround twice more (Phase 1 + scoping deliverables). Third trigger this session for the substrate fix candidate (`td_handlers_agents.py:2139` should not flag ratification-scoped deliverables). Candidacy remains at engineering-substrate level, not Playbook level.

### §8.3 Anti-patterns avoided

- **Chris arbitration overload avoided** by agree-first workflow. Prior sessions (pre-S2753) would have presented Chris with "Rigby leans X, Claude leans Y, which do you pick?" for Q1..Q6 + 2 sets of Rigby edits = 8 arbitration prompts. Instead: 2 binary `"agree all"` D-verdicts.

### §8.4 Suggestions for future sessions

- **Session_lifecycle command reduces pin-rotation ceremony to one shell command** — used at S2754 open (`session_lifecycle open --label i0303-scoping`) and worked cleanly. Should be the default going forward; avoids the fragile hand-edit of `tools/pa_local.sh:539` that memory rules keep warning about.
- **Phase-close 1-PR discipline (PLAYBOOK-7.4.1)** worked cleanly in S2754 close cycles. Followed with placeholder-fills follow-up PR pattern (per S2753 v0.5.0 precedent). Cadence is settling into a repeatable 2-PR-per-close shape.

---

## §9 References

- [`docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md`](../research/implementation/tenant_boundary_lockdown/I-0303_scoping.md) — arc scoping (ratified S2754)
- [`docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md`](../research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md) — Phase 1 audit ledger (ratified S2754)
- [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md`](../research/implementation/RATIFICATION_2026-07-11_i0303_scoping.md) — scoping envelope
- [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md`](../research/implementation/RATIFICATION_2026-07-11_i0303_phase1_ledger.md) — Phase 1 envelope
- [`docs/handoffs/SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md`](SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md) — prior session
- [`docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md`](../research/implementation/tenant_boundary_lockdown/I-0302_scoping.md) — sibling arc template
- [`docs/research/implementation/real_user_readiness/CAMPAIGN.md`](../research/implementation/real_user_readiness/CAMPAIGN.md) — parent program
- [`docs/ENGINEERING_PLAYBOOK.md`](../ENGINEERING_PLAYBOOK.md) — v0.5.0 body
