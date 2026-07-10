---
title: "I-0302 Object-Level Authorization Scoping Ratification Record (2026-07-10)"
status: active
authority: ratification-record
session_added: 2742
ratification_date: 2026-07-10
ratifier: chris
routing: rigby-pa-chat SIGN + Chris direct in-session ratification
program_id: RUR
parent_arc: I-0302
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
sibling_arc_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
ratified_document: docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md
ratified_document_head_at_ratification: 8150d9cd
sign_sessions:
  - S2742 — Rigby scope SIGN: SIGN-WITH-EDITS (F1 material + F3 material + F2/F4/F5 minor + F6 informational + governance-critical §9 Q7 add); all edits APPLIED; post-edit SIGN-CLEAN
supersedes: none (first I-0302 arc-scoping ratification)
superseded_by: (open; not expected — scoping ratifications are frozen historical records)
frozen: true
arc_state:
  phase_1_model_audit_ledger: authorized_to_open
  phase_2_predicate_module: pending
  phase_3_enforcement_application: pending
  phase_4_regression_harness: pending
  phase_5_arc_close: pending
  arc_status: OPEN (scoping ratified; Phase 1 authorized to open)
d_verdicts_captured:
  - Q7 (tenant boundary — governance-critical, Rigby F6 add): APPROVED — hybrid per-model boundary. Workspace-scoped: Deliverable, ChatConversation. Per-user: Initiative, AgentExecution, Document. Phase 1 audit locks the per-model choice.
  - Q2 (AgentExecution triple-class in-scope vs follow-on): APPROVED lean — I-0302 picks the canonical class + scopes it; duplicate retirement is follow-on scope.
  - Q3 (nullable-owner policy per model): APPROVED lean — defer to Phase 1 audit; escalate to Chris only if row counts are large.
  - Q6 (reuse not_found vs add object_authz_denied reason_code): APPROVED lean — reuse `not_found` per existence-oracle avoidance (matches Rigby S2742 Stage 2b SIGN Q6).
d_verdicts_deferred:
  - Q1 (Bucket-A/B/C model-classification lean flip): informational; Phase 1 may flip AgentExecution to view-level scoping if canonical class settles favorably.
  - Q4 (`core/security/object_authz.py` location): my lean confirmed by Rigby F4 leaf-module constraint; no deferral.
  - Q5 (regression harness in `tests/security/`): informational confirmation.
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 arc CLOSED 2026-07-10; RUR-C1 remains OPEN
---

# I-0302 Object-Level Authorization Scoping Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0302 arc scoping on 2026-07-10. It captures the ratified scoping doc, the Rigby SIGN cycle (SIGN-WITH-EDITS → post-edit SIGN-CLEAN), the applied amendments, Chris's D-verdicts on §9 open questions (including the governance-critical Q7 tenant boundary), and the Phase 1 open authorization. It is append-only history; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-10 (America/Denver operator timezone)
- **Arc:** I-0302 (Object-Level Authorization on 5 User-Owned Models)
- **Ratified document:** `docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md` (298 lines pre-amendment, ~360 lines post-amendment; 11 sections)
- **HEAD at ratification:** `8150d9cd`
- **Ratifier:** Chris ("approve all")
- **Sibling status:** I-0301 CLOSED 2026-07-10 (safety contract ratified, arc close ratified). I-0303 NOT YET OPENED (Chris will authorize post-I-0302-substrate).

---

## §2. Rigby SIGN Cycle (SIGN-WITH-EDITS → SIGN-CLEAN)

### §2.1 SIGN focus areas (6)

Routed via `tools/pa_local.sh` on conversation `pa-73f0e2e210574d6d` at S2742 with 6-area SIGN prompt targeting model audit correctness, enforcement rubric, harness design, async-boundary contract, scope boundaries, and open scope questions.

### §2.2 Findings + dispositions

| Finding | Severity | Rigby verdict | Disposition |
|---|---|---|---|
| **F1** — Model audit: Initiative.owner FK type not locked; Document.owner clarification; AgentTaskExecution "user-facing" assumption too strong | material | SIGN-WITH-EDITS | APPLIED — §3.1 AgentTaskExecution assumption softened; §3.2 Initiative FK locked to `core.UnifiedUser` nullable SET_NULL; §3.2 Document FK locked to User NOT NULL (defined on Document, NOT UnifiedBaseModel) |
| **F2** — §4 Meta.permissions bullet overstates ORM-caller coverage | minor | SIGN-WITH-EDITS | APPLIED — reframed to "one canonical predicate" shared by DRF + non-DRF callers |
| **F3** — §5 harness: ownership vs nonexistent probes conflated; list-endpoint semantics; response-body safety-contract probes | material | SIGN-WITH-EDITS | APPLIED — §5.1 now distinguishes ownership vs nonexistent probes, list vs detail semantics (200 + filter check), JSON/non-JSON response-body probes, authentication precondition |
| **F4** — §6 `object_authz.py` import-cycle risk + predicate signature under-specified | minor | SIGN-WITH-EDITS | APPLIED — §6.1 leaf-module constraint added; §6.2 predicate signatures + purity rule frozen |
| **F5** — §7 scope-creep line + NULL-owner interim policy explicit non-policy | minor | SIGN-WITH-EDITS | APPLIED — §7.4 bullet added (no Celery/trace/task-routing creep); §7.5 nullable-owner interim policy added with explicit non-policy on silent-NULL-as-public |
| **F6** — §9 missing governance-critical tenant-boundary question (user vs workspace/tenant) | informational + governance-critical add | SIGN-WITH-EDITS | APPLIED — §9 Q7 added; flagged as pre-Phase-1 Chris D-verdict gate |

### §2.3 Post-edit SIGN state

**SIGN-CLEAN** pending Chris D-verdict on §9 open questions.

---

## §3. Chris D-Verdicts on §9 Open Scope Questions

Chris responded "approve all" during in-session ratification. Verdicts captured:

### §3.1 Q7 — Tenant boundary definition (governance-critical, pre-Phase-1 gate)

**APPROVED — hybrid per-model boundary:**
- **Workspace-scoped:** `Deliverable`, `ChatConversation` (both have workspace FKs; existing PA tool paths already scope by workspace)
- **Per-user:** `Initiative`, `AgentExecution`, `Document` (no workspace FK on canonical class OR workspace FK is orthogonal to ownership)

**Phase 1 lock:** Phase 1 audit resolves the per-model choice against HEAD; any deviation from the above list requires Rigby re-SIGN + Chris re-ratification of a §9 Q7 amendment.

### §3.2 Q2 — AgentExecution triple-class

**APPROVED lean:** I-0302 picks the canonical class + scopes it. Duplicate class retirement is follow-on scope (recorded in the arc close doc §7.3 carve-out already).

### §3.3 Q3 — Nullable-owner policy per model

**APPROVED lean:** defer to Phase 1 audit. Escalate to Chris only if row counts are large (Phase 1 §7.5 policy application will surface volumes).

### §3.4 Q6 — `not_found` vs `object_authz_denied`

**APPROVED lean:** reuse existing `not_found` reason_code per existence-oracle avoidance. Matches Rigby S2742 Stage 2b SIGN Q6 outcome for I-0301.

### §3.5 Q1, Q4, Q5 — Informational / auto-resolved

- Q1 (Bucket A/B/C model-classification flip): informational; Phase 1 may adjust.
- Q4 (`core/security/object_authz.py` location): my lean confirmed by Rigby F4 leaf-module constraint (co-locate with security substrate).
- Q5 (regression harness in `tests/security/`): informational confirmation of I-0301 precedent.

---

## §4. Downstream Unlocks

Ratification of this scoping doc authorizes:

- **Phase 1 (Model Audit Ledger)** to open under this arc.
- Frontmatter transition of the scoping doc from `status: draft` → `status: active`.
- Use of the scoping doc as the constitutional reference for every Phase 1-5 sub-artifact.

Ratification does NOT authorize:
- Any Phase 2+ activity (predicate module, enforcement application, harness) — those open only after each prior Phase Rigby SIGN.
- Any modification to the ratified failure-data safety contract (I-0301 constitutional artifact).
- Any modification to the RUR-C1 parent close condition (needs all three arcs).
- Any I-0303 work — I-0303 remains OPEN authorization pending.

---

## §5. Constitutional Anchors

This scoping ratification is anchored under:

- **Engineering Playbook v0.4.1** (ratified S2742) — arc scoping + SIGN-then-ratify cadence per §4.3, §14.2.
- **Real User Readiness CAMPAIGN** (parent program, ratified S2742) — RUR-C1 close-gate invariant per §4.
- **Failure-Data Safety Contract** (ratified S2742 as I-0301 Phase 2 constitutional artifact) — §5 harness safety-contract probes anchor to the contract.
- **I-0301 Arc Close** (ratified S2742) — sibling arc; §5 harness follows I-0301 test-file precedent.

---

## §6. Handoff to Phase 1

Phase 1 (Model Audit Ledger) is authorized to open. Concrete Phase 1 opening moves:

1. Materialize the 5-model audit ledger as a workspace deliverable under `fcd7e683` (RUR-C1 Tenant Boundary Lockdown workspace).
2. Per-model: resolve `AgentExecution` canonical class; enumerate ownership FKs; count nullable-owner rows; catalogue all views/services/tasks/management-commands touching the model; classify each as scoped / unscoped / ambiguous.
3. Apply Chris §3.1 Q7 D-verdict per-model: verify `Deliverable` + `ChatConversation` map to workspace-scope predicate; verify `Initiative` + `AgentExecution` + `Document` map to per-user predicate.
4. Nullable-owner policy decision per model (§7.5).
5. Rigby SIGN on the ledger before Phase 2 opens.

---

**End of I-0302 Scoping Ratification Record. Frozen 2026-07-10.**
