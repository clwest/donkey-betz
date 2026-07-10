---
title: "I-0302 Phase 1 Model Audit Ledger Ratification Record (2026-07-10)"
status: active
authority: ratification-record
session_added: 2742
ratification_date: 2026-07-10
ratifier: chris
routing: rigby-pa-chat SIGN + Chris direct in-session ratification
program_id: RUR
parent_arc: I-0302
parent_arc_phase: Phase 1 (Model Audit Ledger)
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
sibling_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md (I-0301 arc close — sibling arc closed)
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md (I-0302 scoping ratified)
ratified_document: docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md
ratified_document_head_at_ratification: 8150d9cd
sign_sessions:
  - S2742 — Rigby ledger SIGN initial: SIGN-WITH-EDITS (F1 material + F3 material + F6 material + F2/F4 minor + F5 informational); all edits applied
  - S2742 — Rigby ledger SIGN post-edit: SIGN-PASS
  - S2742 — Rigby joint SIGN on Chris Option C reframe: agreed with two guardrails (canonical-primary-user lookup + provenance note); applied
supersedes: none (first I-0302 Phase 1 ratification)
superseded_by: (open; not expected — Phase 1 ledgers are frozen historical records)
frozen: true
arc_state:
  phase_1_model_audit_ledger: closed (this record)
  phase_2_predicate_module: authorized_to_open
  phase_3_enforcement_application: pending
  phase_4_regression_harness: pending
  phase_5_arc_close: pending
  arc_status: OPEN (Phase 1 CLOSED; Phase 2 authorized to open)
chris_d_verdicts_resolved:
  - Initiative null-owner transitional policy — OPTION C APPROVED: backfill all 62 null-owner rows to primary user via one-shot migration; migrate `owner` to NOT NULL; skip transitional predicate. Rationale: single-user pre-prod operating context (memory recorded 2026-07-10). Guardrails: canonical primary-user lookup (first superuser / configured primary user), NOT hardcoded "chris" string (per Rigby SIGN F3 guardrail preserved).
new_operating_context_captured:
  - Donkey Betz single-user pre-prod operating context — Chris directive 2026-07-10 during I-0302 Phase 1 close. Memory saved as `project_single_user_pre_prod_operating_context.md`. Applies to all future data-to-user connection decisions until Chris signals Phase 0 multi-tenant opening.
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 CLOSED 2026-07-10; I-0302 Phase 1 CLOSED (this record); I-0303 NOT YET OPENED; RUR-C1 remains OPEN
---

# I-0302 Phase 1 Model Audit Ledger Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0302 Phase 1 Model Audit Ledger on 2026-07-10. It captures the ratified ledger, the Rigby SIGN cycle (SIGN-WITH-EDITS → SIGN-PASS post-edit → joint SIGN on Option C reframe), Chris's Option C D-verdict on Initiative null-owner transitional policy, the new single-user pre-prod operating context captured, and the Phase 2 opening authorization. It is append-only history; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-10 (America/Denver operator timezone)
- **Arc phase:** I-0302 Phase 1 (Model Audit Ledger)
- **Ratified document:** `docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md` (~435 lines, 10 sections)
- **HEAD at ratification:** `8150d9cd`
- **Ratifier:** Chris ("Approved!" on Option C joint proposal, plus explicit "remember I am the only user for right now" durable operating context directive)
- **Sibling status:** I-0301 CLOSED 2026-07-10; I-0302 scoping ratified 2026-07-10; I-0302 Phase 2 authorized to open via this record; I-0303 NOT YET OPENED.

---

## §2. Rigby SIGN Cycle (SIGN-WITH-EDITS → SIGN-PASS → joint Option C SIGN)

### §2.1 Initial SIGN (SIGN-WITH-EDITS)

Routed via `tools/pa_local.sh` on conversation `pa-73f0e2e210574d6d` at S2742 with 6-area SIGN prompt on §4 (row counts), §5 (caller classification), §6 (Q7 boundary), §7 (nullable-owner policy), §8 (Phase 2 entry criteria), §9 (retirement targets).

### §2.2 Findings + dispositions

| Finding | Severity | Rigby verdict | Disposition |
|---|---|---|---|
| **F1** — Row counts LOCAL-only framing + missing confidence column + no related-tables informational section | material | SIGN-WITH-EDITS | APPLIED — §4 LOCAL-DB banner + confidence column (local_verified/prod_pending) + §4.2 related-tables subsection (DeliverableExport, DeliverableCollection, ContentPacket, Initiative sub-tables) with explicit scope-carve-out |
| **F2** — §9 titles need tightening: framing as "import hygiene + dead-code retirement" not scope creep | minor | SIGN-WITH-EDITS | APPLIED — SHADOWED file reframed as "import hygiene + audit correctness"; ZOMBIE class reframed as "migration integrity issue, prefer removal over adding migration" |
| **F3** — Initiative "attribute to chris fallback" is high-risk silent cross-tenant visibility; need transitional predicate with staff-only carve-out; ChatConversation deny-by-default | material | SIGN-WITH-EDITS | APPLIED (initial) — Initiative Option A vs Option B + transitional predicate; ChatConversation deny-by-default rewrite. **SUPERSEDED by Chris Option C D-verdict** (see §3) |
| **F4** — §5 sampling depth acceptable IF "unscoped" reserved for user-visible yield paths + aggregate-leakage rule + reproducibility footnote | minor | SIGN-WITH-EDITS | APPLIED — §5.0 preface + §5.0.1 grep-strategy footnote + aggregate-leakage rule for AgentExecution/Document dashboards |
| **F5** — §6 workspace-scoped semantics need explicit "membership check, NOT row.user==request.user" clarification + Phase 2 TODO for canonical `user_can_access_workspace` primitive | informational | SIGN-WITH-EDITS | APPLIED — §6.1 workspace-scoped semantics clarification; §6.2 Phase 2 TODO for canonical membership primitive |
| **F6** — Phase 2 entry criteria missing Chris D-verdict gate on Initiative + migration guardrail + shadowed/zombie retirement note | material | SIGN-WITH-EDITS | APPLIED — §8 entry criteria expanded to 9 items; Chris D-verdict item 6 was RESOLVED via Option C (see §3) |

### §2.3 Post-edit SIGN state

**SIGN-PASS confirmed** after F1..F6 edits applied.

### §2.4 Joint Option C SIGN (post-Chris-reframe)

Chris reframed the Initiative D-verdict question by stating platform is single-user + not in prod. Rigby joint SIGN on the joint Option C proposal:
- **Agreed** with Option C (backfill + NOT NULL, skip transitional predicate) under single-user pre-prod context
- **Two guardrails preserved from F3:** canonical primary-user lookup (NOT hardcoded "chris" string); provenance note in ledger recording this as a "pre-prod single-user normalization step"
- **ChatConversation deny-by-default softened** to minimal future-proofing invariant ("null_user is staff-only if it ever appears") — no code change today
- Post-Option-C SIGN-PASS confirmed on the joint proposal

---

## §3. Chris D-verdict — Initiative Null-Owner Transitional Policy

**RESOLVED — Option C approved 2026-07-10.**

### §3.1 The decision

**Backfill all 62 null-owner Initiative rows to canonical primary user via one-shot migration; migrate `owner` to NOT NULL immediately; enforce `owner=request.user` from Phase 3 day 1; NO transitional predicate layer.**

### §3.2 Guardrails preserved from Rigby SIGN F3

1. **Canonical primary-user lookup, NOT hardcoded "chris" string.** Migration derives the target user via `User.objects.filter(is_superuser=True).order_by('pk').first()` or a configured primary-user setting. This survives DB re-seed + operator handle changes.
2. **Provenance note recorded in ledger §7 Initiative row:** "pre-prod single-user normalization step; revisit when Phase 0 multi-tenant lands."

### §3.3 Rationale

- Platform is single-user + pre-prod (per Chris directive captured in `project_single_user_pre_prod_operating_context.md`).
- Options A (deny-by-default) and B (derive owner deterministically) were designed for a hypothetical multi-tenant world that doesn't exist yet.
- 62 rows + 1 user = trivial migration; NOT NULL flip removes the entire ownership-nullability ambiguity class from future code.
- I-0302's core deliverable — multi-tenant predicate module + regression harness — STILL gets built. Chris D-verdict only simplifies the data-state complexity; the predicate substrate + cross-tenant test harness remain per the ratified scoping doc.

### §3.4 What this does NOT change

- Phase 2 predicate module still ships `initiative_owned_by(user, initiative) := initiative.owner == user` — the multi-tenant enforcement primitive.
- Phase 4 regression harness still tests user-A vs user-B synthetically per scoping §5.
- Cross-tenant leakage detection still gates arc close.
- I-0303 async task-boundary enforcement still uses shared predicate module.

---

## §4. New Operating Context Captured (Memory)

Chris directive 2026-07-10: **"Remember I am the only user for right now going forward in case we hit other areas about connecting data to a user."**

Recorded as durable operating context in `project_single_user_pre_prod_operating_context.md`. Applies across sessions and across all future arcs where data-to-user connection decisions arise.

**Default assumption going forward:** single-tenant reasoning applies until Chris explicitly signals Phase 0 multi-tenant opening (or adds a second user to the DB, or wires up Discord/system integrations for real).

**Anti-pattern reminder:** don't hardcode operator handles by string; use canonical primary-user lookups so migrations survive DB re-seed events.

---

## §5. Downstream Unlocks

Ratification of this ledger authorizes:

- **Phase 2 (Predicate Module)** to open under I-0302.
- Phase 2 ships `core/security/object_authz.py` with 5 per-model predicate functions (per §6 Q7 boundary):
  - `deliverable_in_scope(user, deliverable)` — workspace-scoped via `user_can_access_workspace(user, deliverable.workspace_id)`
  - `chat_conversation_in_scope(user, conv)` — workspace-scoped
  - `initiative_owned_by(user, initiative)` — per-user
  - `agent_execution_owned_by(user, execution)` — per-user + staff carve-out for `user=NULL` Celery runs (Phase 2 SIGN target)
  - `document_owned_by(user, doc)` — per-user
- Phase 2 also identifies canonical `user_can_access_workspace(user, workspace_id)` source-of-truth (per §6.2 TODO).
- Phase 3 pre-flight: Initiative backfill migration to canonical primary user + NOT NULL flip. (Phase 3 opens after Phase 2 predicate SIGN.)

Ratification does NOT authorize:
- Phase 3 enforcement application without Phase 2 predicate SIGN.
- Any Phase 4 (regression harness) work without Phase 3 close.
- Any Phase 5 (arc close) work without full arc completion.
- Any I-0303 (async boundary) work — I-0303 remains OPEN authorization pending.
- Any modification to the ratified failure-data safety contract or the I-0302 scoping doc.

---

## §6. Constitutional Anchors

This ratification is anchored under:

- **Engineering Playbook v0.4.1** (ratified S2742) — Phase 1 SIGN-then-ratify cadence per §4.3.
- **Real User Readiness CAMPAIGN** (parent program, ratified S2742) — RUR-C1 close-gate invariant per §4.
- **I-0302 Scoping** (ratified S2742) — Chris Q7 hybrid boundary D-verdict + Rigby scope SIGN.
- **I-0301 Arc Close** (ratified S2742) — sibling arc precedent for Phase-by-Phase ratification cadence.
- **Failure-Data Safety Contract** (ratified S2742 as I-0301 Phase 2 constitutional artifact) — §5 regression harness safety-contract probes.

---

## §7. Handoff to Phase 2

Phase 2 (Predicate Module) is authorized to open. Concrete Phase 2 opening moves:

1. Create `core/security/object_authz.py` leaf module (per scoping §6.1 leaf-module constraint).
2. Ship 5 per-model predicates (per §6 Q7 boundary):
   - Workspace-scoped: Deliverable, ChatConversation
   - Per-user: Initiative, AgentExecution, Document
3. Identify + wire canonical `user_can_access_workspace(user, workspace_id)` primitive (per §6.2 TODO).
4. AgentExecution staff carve-out predicate: `agent_execution_owned_by(user, execution) := (execution.user == user) OR (execution.user IS NULL AND user.is_staff)` — Rigby SIGN target on the carve-out shape.
5. Test suite: `tests/security/test_object_authz_predicates.py` proving each predicate correctly scopes to owner + membership.
6. Rigby SIGN on the Phase 2 predicate module before Phase 3 opens.

---

**End of I-0302 Phase 1 Model Audit Ledger Ratification Record. Frozen 2026-07-10.**
