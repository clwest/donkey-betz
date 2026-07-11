---
title: "I-0303 Async Tenant-Boundary Enforcement Scoping Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2754
ratification_date: 2026-07-11
ratifier: chris
ratifier_verdict: "agree all"
routing: rigby-pa-chat SIGN + Chris direct in-session ratification (per new Claude+Rigby-agree-first workflow rule S2753)
program_id: RUR
parent_arc: I-0303
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
sibling_arc_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md
ratified_document: docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md
ratified_document_head_at_ratification: f7e40ddb
sign_sessions:
  - S2754 turn 1 — Rigby scope SIGN via watchpoint-anchor axes 1-8 (agree-first joint agreement per S2753 workflow rule): SCOPING RATIFY WITH EDITS — 4 axis edits (§1 read/return + DB-row-derived default; §4 uniform contract; §8 Phase 3 elasticity; §8 Phase 4 per-cluster sentinel) + Q6 addition (canonical row reference); all edits APPLIED inline pre-Chris-ratification; Q1..Q6 leans Claude+Rigby converged; joint recommendation SCOPING RATIFY. Pin: `pa-2659dfa28e124f02`.
supersedes: none (first I-0303 arc-scoping ratification)
superseded_by: (open; not expected — scoping ratifications are frozen historical records)
frozen: true
arc_state:
  phase_1_task_boundary_audit_ledger: authorized_to_open
  phase_2_decorator_and_base_class: pending
  phase_3_per_task_enforcement: pending
  phase_4_async_boundary_regression_harness: pending
  phase_5_arc_close: pending
  arc_status: OPEN (scoping ratified; Phase 1 authorized to open)
d_verdicts_captured:
  - Q1 trusted-source hierarchy — APPROVED MANDATE (DB-row-derived identity first; signed dispatch header second only when DB-row unresolvable; payload-supplied identity NEVER)
  - Q2 system-task marker discipline — APPROVED EXPLICIT OPT-IN `@system_scope` (fail-safe by default; task lacking any marker MUST fail Phase 3 enforcement flip)
  - Q3 AsyncBoundaryProbe shape — APPROVED NEW PROBE CLASS (task-dispatch semantics distinct from HTTP endpoint probes; shared matrix + shared coverage-gap tolerance retained)
  - Q4 coverage-gap threshold — APPROVED I-0302 PRECEDENT (per-exemption enumeration + Rigby SIGN + Chris ratification at Phase 4 close; no numerical aggregate threshold)
  - Q5 RUR-C1 close SIGN scope — APPROVED ONE PARENT-CLOSE EVENT (single Chris D-verdict at RUR-C1 parent close ratifying all three arcs pass shared harness)
  - Q6 canonical row reference — APPROVED ROW-ID DISPATCH ONLY for user-owned-model tasks (filters/queries either refactor in Phase 3 OR receive explicit exemption per Q4)
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 arc CLOSED 2026-07-10; I-0302 arc CLOSED 2026-07-10; I-0303 arc OPENED at scoping ratification (this record); RUR-C1 remains OPEN pending I-0303 close
depends_on_ratified_artifacts:
  - Engineering Playbook v0.5.0 (ratified 2026-07-11 S2753) — close-ceremony discipline §7.4; staged codification §7.5.1 (Phase 3 dogfood); watchpoint SIGN §7.6.1 (every phase/arc-close SIGN dogfood)
  - I-0301 Failure-Data Safety Contract (ratified 2026-07-10)
  - I-0302 predicate module + shared cross-tenant regression harness (ratified 2026-07-10)
workspace_ratification_deliverable_id: 18194cab-b737-42bf-b747-1263af5771ae
workspace_content_mirror_deliverable_id: f8af6aad-05ae-4d9f-b61b-3a81d6604b57  # S2754a backfill per twin-deliverable rule
close_pr: "#3137 (merged 47cc13dd)"
---

# I-0303 Async Tenant-Boundary Enforcement — Scoping Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0303 arc scoping on 2026-07-11. It captures the ratified scoping doc, the Rigby scope SIGN cycle (SCOPING RATIFY WITH EDITS applied inline pre-Chris-ratification per the new Claude+Rigby-agree-first workflow rule), Chris's D-verdicts on the six open scope questions (Q1..Q6), and the Phase 1 open authorization. It is append-only history; do NOT edit after commit except to fill the reserved TBD fields.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Session:** S2754 (opened same day as v0.5.0 ratification session S2753)
- **Arc:** I-0303 (Async Tenant-Boundary Enforcement) — third and final RUR-C1 child
- **Ratified document:** `docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md` (322 lines post-Rigby-edits)
- **HEAD at ratification:** `f7e40ddb`
- **Ratifier:** Chris (`"agree all"`)
- **Routing:** Rigby PA chat surface via pin `pa-2659dfa28e124f02` (label `i0303-scoping`, minted S2754 open via `session_lifecycle open`); Chris D-verdict entered directly in-session per workflow choice (feedback_rigby_comms.md permits terminal D-verdict when Chris explicitly directs).
- **Workflow rule exercised:** first arc ratification under the new **Claude+Rigby-agree-first** rule (Chris directive S2753 D-verdict). Rigby's SIGN edits were folded inline BEFORE routing joint recommendation to Chris; Chris ratified the joint proposal, not a decision menu.

**Sibling arc status at scoping ratification:**

- **I-0301 (CLOSED 2026-07-10):** safety contract ratified; consumed by I-0303 for failure-envelope conformance.
- **I-0302 (CLOSED 2026-07-10):** object-level authorization + predicate module + shared regression harness ratified; consumed by I-0303 Phase 2 (predicate import) + Phase 4 (harness extension).
- **I-0303 (OPENED S2754, this record):** scoping ratified; Phase 1 authorized to open.
- **RUR-C1 parent:** remains OPEN. Closes only when I-0303 closes AND all three arcs pass the shared cross-tenant regression suite per parent CAMPAIGN Chris Q2 D-verdict.

---

## §2. Rigby SIGN Cycle (SCOPING RATIFY WITH EDITS)

### §2.1 SIGN dispatch

Routed via `tools/pa_local.sh` on conversation `pa-2659dfa28e124f02` at S2754 turn 1 with an 8-axis SIGN prompt covering: arc objective + deliverable (§1); required scope outcomes (§2); preliminary current-HEAD audit (§3); enforcement mechanism framework (§4); async-boundary probe extension (§5); scope boundaries (§7); phases (§8); open scope questions (§9).

Dispatch used a joint-agreement framing per the new Claude+Rigby-agree-first workflow rule (Chris S2753 D-verdict): SIGN turn 1 aimed to reach converged joint recommendation rather than dispatch a decision menu to Chris.

### §2.2 Findings + dispositions

| Axis | Rigby verdict | Finding | Disposition |
|---|---|---|---|
| **§1 objective + deliverable** | EDIT | Add "read/return user-owned rows" (not just mutate); default trusted source = DB-row-derived identity (not equally signed-header); clamp in-scope models to the 5 named + Phase-1-discovered additions | APPLIED inline: §1 body expanded to name read/return equally; DB-row-derived default explicit; scope clamp added as Rigby-SIGN-edit paragraph |
| **§2 required scope outcomes (Q1..Q10)** | PASS | Complete; mirrors I-0302 template well; import-layering constraint (Q2.8) pinning is correct | No change |
| **§3 preliminary current-HEAD audit** | PASS | Preliminary framing correct; nothing conflicts with Rigby's understanding; ops_tool.celery_task_history not queried in this pass | No change |
| **§4 enforcement mechanism framework** | PASS | Per-task decorator vs base-class choice legitimate | APPLIED addition inline: uniform failure envelope + uniform trusted-source resolution contract MANDATORY regardless of mechanism (§4 body extended with "Uniform contract" paragraph) |
| **§5 async-boundary probe extension** | PASS | New AsyncBoundaryProbe + per-(task, model) matrix + sentinel + CI-block + coverage-gap tolerance shape correct | No change |
| **§7 scope boundaries** | PASS | Deferral list to RUR-C2/RUR-C4/follow-on matches; explicit non-goals crisp | No change |
| **§8 phases (5-phase plan)** | EDIT | Phase 3 may need extra session if Phase 1 audit surfaces many mixed/none identity tasks; Phase 4 sentinel must be per-model AND per-task-domain-cluster (agents/content/conversations/initiatives) | APPLIED inline: Phase 3 elasticity paragraph added; Phase 4 sentinel requirement expanded to name both dimensions with per-cluster minimum |
| **§9 open scope questions (Q1..Q5)** | EDIT | Add Q6 canonical row reference (row-ID dispatch vs filters/queries); Rigby leans recorded on all six | APPLIED inline: Q6 added; joint Claude+Rigby leans folded per Q; framing changed from "leans pending" to "joint leans applied" |

**Post-edit SIGN state:** joint recommendation = **SCOPING RATIFY**. No F-BLOCKING remaining. All 4 axis edits + Q6 addition applied inline PRE-Chris-ratification per the agree-first rule. Chris presented with ONE joint proposal, not a menu.

### §2.3 Workflow rule dogfooding

This SIGN cycle is the first ratification exercised under the new Claude+Rigby-agree-first rule (Chris directive at v0.5.0 D-verdict, S2753). Rigby's edits landed in the scoping doc BEFORE Chris ratified; Chris did not have to arbitrate between Claude's and Rigby's positions. Q1..Q6 leans converged during SIGN turn 1 — no Q required a Chris tie-break.

**Provenance note:** the ratification envelope §5.1 of `RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md` records the workflow rule verbatim; this record is the first-trigger evidence of that rule in normal use. Second-trigger threshold for future Playbook codification not yet met (per shape doc §5.1 candidacy paragraph).

---

## §3. Chris D-Verdict (Q1..Q6)

**Verdict:** `"agree all"` on all six joint leans + the scoping doc as-drafted (post-inline-edits).
**Recorded:** 2026-07-11 S2754 (terminal-side D-verdict; routing preference established at S2753 D-verdict).

### §3.1 Q1 — Trusted-source hierarchy — APPROVED MANDATE

DB-row-derived identity first (resolve `acting_user_id` + `acting_workspace_id` from the committed row referenced by dispatch); signed dispatch header second (only when DB-row identity is not resolvable — narrow set of system-initiated dispatches); payload-supplied identity NEVER (payload identity is inherently forgeable by prompt-injection or stale dispatch).

### §3.2 Q2 — System-task marker discipline — APPROVED EXPLICIT OPT-IN

Explicit `@system_scope` decorator required for system-scope tasks. Fail-safe by default: task lacking either `@enforce_tenant_boundary` OR `@system_scope` marker MUST fail CI at Phase 3 enforcement flip. No implicit-by-absence system passthrough.

### §3.3 Q3 — AsyncBoundaryProbe shape — APPROVED NEW PROBE CLASS

Task-dispatch semantics differ from HTTP endpoint semantics (dispatch → queue → execute vs request → response). New `AsyncBoundaryProbe` class in `tests/security/`; shared coverage-gap matrix + coverage-gap tolerance policy reused verbatim from I-0302.

### §3.4 Q4 — Coverage-gap threshold — APPROVED I-0302 PRECEDENT

No numerical aggregate threshold. Discipline is per-exemption sign-off: every exempted task enumerated in the Phase 4 coverage-gap report AND receives Rigby SIGN + Chris ratification at Phase 4 close. Matches I-0302 arc-close doc §7 recorded tolerance.

### §3.5 Q5 — RUR-C1 close SIGN scope — APPROVED ONE PARENT-CLOSE EVENT

After I-0303 arc close ratifies (§Phase 5), RUR-C1 parent close is ONE additional ratification event: a single Chris D-verdict ratifying "all three arcs (I-0301 + I-0302 + I-0303) pass the shared cross-tenant regression suite." Splitting into two events (regression pass + parent-close) would add ceremony without evidence benefit.

### §3.6 Q6 — Canonical row reference — APPROVED ROW-ID DISPATCH ONLY

For Celery tasks touching user-owned models: task dispatch MUST accept a **row ID** (not filters, not queries, not natural keys). Task re-resolves the row from DB at execution start; ownership check runs against the resolved row per Q1's DB-row-derived identity rule. Tasks currently accepting filters/queries MUST either (a) refactor to accept row IDs (Phase 3 substrate) OR (b) receive an explicit exemption enumerated in the Phase 4 coverage-gap report per Q4.

---

## §4. Phase 1 Open Authorization

Ratification of this scoping AUTHORIZES Phase 1 (Task Boundary Audit Ledger) to open. Phase 1 scope per scoping doc §8:

- Materialize per-task boundary audit ledger as a workspace deliverable under `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (RUR-C1 Tenant Boundary Lockdown workspace)
- Per task touching user-owned model: classify acting-identity source (session-derived / payload-supplied / mixed / none); classify existing verification (present / absent / partial)
- System-task classification: which tasks are legitimately system-scope and do not need tenant-boundary enforcement
- Rigby SIGN on the ledger before Phase 2 opens

Phase 1 target: 1 session (S2755 or same-session continuation per Chris directive).

Phase 1 authorization does NOT extend to Phase 2 (decorator + base-class implementation); Phase 2 requires Rigby SIGN on the Phase 1 ledger + Chris ratification. Same amendment discipline through Phase 5.

---

## §5. Downstream Unlocks

Ratification of I-0303 scoping authorizes:

- Immediate Phase 1 open per §4
- I-0303 becomes the first arc opened under Playbook v0.5.0 — Phase 3 will dogfood PLAYBOOK-7.5.1 (three-PR staged codification); every phase/arc-close SIGN will dogfood PLAYBOOK-7.6.1 (watchpoint-attestation shape); arc close will dogfood PLAYBOOK-7.4.1/7.4.2/7.4.3 (close-ceremony delivery discipline)
- Cross-arc close-ceremony precedent for future arcs (I-0400, I-0500, etc. under RUR-C2/C3/C4/C5/C6)
- RUR-C1 parent close-gate remains OPEN until I-0303 closes; scoping ratification does NOT open RUR-C2 (which was already eligible-to-open per Wave 1 staged-overlap Chris Q1 D-verdict)

---

## §6. Provenance Chain

- **Parent CAMPAIGN scoping:** `docs/research/implementation/real_user_readiness/CAMPAIGN.md` (ratified S2742) — §4 I-0303 arc slot; §5 dependency ordering; §11 Div 2 RUR-C1 close-gate
- **Sibling ratifications:** RATIFICATION_2026-07-10_i0301_arc_close.md + RATIFICATION_2026-07-10_i0302_scoping.md + RATIFICATION_2026-07-10_i0302_arc_close.md
- **Deferral chain:** I-0302 §7.2 explicitly deferred to I-0303 (Celery task workspace-scope re-verification + reject unsafe dispatches + user-A → user-B negative tests)
- **Playbook v0.5.0:** RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0.md — §5.1 workflow directive is the parent contract this SIGN cycle exercises (Claude+Rigby-agree-first)
- **Ratified scoping doc:** `tenant_boundary_lockdown/I-0303_scoping.md` at HEAD `f7e40ddb`
- **This ratification envelope:** the workspace-canonical record for Phase 1 authorization

---

## §7. Post-Ratification Bindings (filled at commit + workspace registration)

- `workspace_ratification_deliverable_id`: TBD → workspace deliverable UUID in `fcd7e683-3bfe-4d35-9704-0e54dd587ea1` (RUR-C1 Tenant Boundary Lockdown); title `RATIFICATION_20260711_i0303_scoping`; category `governance`; deliverable_type `ratification_record`; body mirrored from this file; ORM-fix diagnostic-cleanup per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`
- `close_pr`: TBD → S2754 scoping-ratification PR merge SHA (this record + scoping doc + task list updates ship as single close-bundle PR per PLAYBOOK-7.4.1 dogfooding)
- `ratified_document_head_at_ratification`: `f7e40ddb` (recorded at authoring; verified against playbook top-frontmatter merge SHA)

CLAUDE.md L7 anchor NOT updated at scoping ratification (arc-scoping is not a governance-level artifact requiring L7 refresh; L7 anchor tracks Playbook version only). Scoping ratification is discoverable via `docs/research/implementation/RATIFICATION_2026-07-11_*` grep or via the RUR-C1 workspace deliverables UI.
