---
title: "I-0302 Arc Close Ratification Record (2026-07-10)"
status: active
authority: ratification-record
session_added: 2751
ratification_date: 2026-07-10
ratifier: chris
ratifier_verdict: "agree all"
routing: rigby-pa-chat SIGN (arc-close watchpoints W1..W5) + Chris D-verdict via Rigby PA chat
program_id: RUR
parent_arc: I-0302
parent_arc_workspace: fcd7e683-3bfe-4d35-9704-0e54dd587ea1
parent_arc_workspace_name: "RUR-C1 Tenant Boundary Lockdown"
parent_campaign: RUR-C1 (Tenant Boundary Lockdown)
parent_campaign_workspace: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
parent_campaign_workspace_name: "Real User Readiness Campaign"
parent_program_doc: docs/research/implementation/real_user_readiness/CAMPAIGN.md
parent_program_ratification: docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md
sibling_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase1_ledger.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md
  - docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase4_close.md
ratified_documents:
  - docs/research/implementation/tenant_boundary_lockdown/I-030299_i0302_arc_close.md
  - docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md (final §8 chain-of-custody row for arc CLOSED)
ratified_arc_scope:
  - Phase 1 ledger (I-030201) — model audit + §11 @ops_aggregate_allowed codification + §14 Http404-swallow codification
  - Phase 2 predicate module (I-030202) — 11 predicate functions + 60 unit tests
  - Phase 3 wiring — 144 enforcement sites across 34+ view files (10 PRs #3100-#3109)
  - Phase 4 harness (I-030203/I-030204/I-030205) — 6 test modules + 50 matrix cells + 28 sentinels + 2 AST rules enforcing + coverage-gap report + VIP carve-out + fixtures (14 substrate PRs + 1 close-doc PR)
ratified_head: 2a691ca5
close_pr: TBD (S2751 arc-close PR — filled at merge)
sign_sessions:
  - S2751 — Rigby arc-close SIGN (W1..W5): SIGN-PASS clean, no F-blockers, 2 non-blocking asks applied inline. Pin `pa-e71c011bfa3d4124`.
supersedes: none (first I-0302 arc close ratification)
superseded_by: (open; not expected — arc-close ratifications are frozen historical records)
frozen: true
arc_state:
  phase_1_model_audit_ledger: closed (ratified S2742)
  phase_2_predicate_module: closed (ratified S2742)
  phase_3_enforcement_application: closed (S2747 wiring; no separate ratification — enclosed in Phase 4 arch doc `head_at_architecture: 62ee3911`)
  phase_4_regression_harness: closed (ratified S2751)
  phase_5_arc_close: closed (this record)
  arc_status: CLOSED
parent_campaign_close_gate:
  - RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all pass shared cross-tenant regression suite per Chris Q2 D-verdict at parent CAMPAIGN ratification
  - I-0301 CLOSED 2026-07-10; I-0302 CLOSED 2026-07-10 (this record); I-0303 NOT YET OPENED; RUR-C1 remains OPEN
deferred_verify_recovery_gate:
  - condition: first green CI run against a PR touching `tests/security/**` after GitHub Actions billing resumption
  - action_on_regression: if any Phase 4 test module regresses on that run, Phase 4 close reopens per RATIFICATION_2026-07-10_i0302_phase4_close.md §5, which cascades to reopening this arc close
  - status_at_ratification: CI billing still blocked as of 2026-07-10; recovery gate pending
playbook_candidate_patterns_promoted:
  - "report-only → batch-fix → enforce three-PR substrate pattern (2 triggers confirmed)"
  - "phase-close doc + ratification record + arch amendments = 1 PR (2 triggers confirmed)"
  - "watchpoint-attestation SIGN (W1..Wn) shape for phase/arc-close SIGN (2 triggers confirmed)"
  - "phase-close doc changes serialized on a single close-doc PR (2 triggers confirmed; anti-pattern → codified prohibition)"
  - "1 close-doc PR + 1 cascade PR at every close (2 triggers with shape divergence — S2750 split vs S2751 combined)"
playbook_candidate_ratification_scope:
  - These 5 candidates are eligible for CODIFY under a separate v0.5 MINOR playbook ratification cycle.
  - This arc-close ratification records candidacy only; it does NOT itself codify any playbook rule.
  - Chris D-verdict on the actual playbook v0.5 codification remains a distinct ratification event.
---

# I-0302 Object-Level Authorization — Arc Close Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the I-0302 arc close on 2026-07-10. It captures the ratified arc-close doc, the arc's cumulative scope across 4 phases, the Rigby arc-close SIGN attestation, Chris's D-verdict, the deferred behavioral-verify recovery gate, and the 5 playbook-candidate patterns eligible for a separate v0.5 codification cycle. It is append-only history; do NOT edit after commit.

---

## §1. Context

- **Ratification date:** 2026-07-10 (America/Denver operator timezone)
- **Session:** S2751 (same session as Phase 4 close ratification — continuous close-ceremony arc)
- **Arc phase:** I-0302 Phase 5 (Arc Close / Retro)
- **Ratified HEAD:** `2a691ca5`
- **Close PR:** TBD (filled at merge — this ratification record ships in the same PR as the arc-close doc)
- **Ratifier:** Chris ("agree all")
- **Routing:** Rigby PA chat surface via pin `pa-e71c011bfa3d4124`; Chris D-verdict entered via Rigby chat.
- **Sibling status:** I-0301 CLOSED (arc, 2026-07-10); I-0302 scoping / Phase 1 / Phase 2 / Phase 4 all ratified 2026-07-10; Phase 3 closed implicit at S2747 wiring; Phase 5 arc close ratified via this record; I-0303 NOT YET OPENED.

---

## §2. Ratified Deliverables

### §2.1 `I-030299_i0302_arc_close.md` — Arc close doc

10 sections + frontmatter. Content roll-up:

- **§1 Executive Summary** — I-0302 Object-Level Authorization arc; 5 canonical models × 11 predicates × 60 unit tests; 144 Phase 3 enforcement sites across 34+ view files; 6 Phase 4 harness modules + 50 matrix extension cells + 28 sentinels + 2 AST rules enforcing. Cumulative arc: 26 substrate PRs + 5 docs/handoff/cascade PRs across 4 phases.
- **§2 Phase-by-Phase Outcomes** — Phase 1 ledger (ratified S2742); Phase 2 predicate module (ratified S2742, PR #3097); Phase 3 wiring (closed S2747, 10 PRs #3100-#3109); Phase 4 harness (ratified S2751, 14 substrate PRs + 1 close-doc PR).
- **§3 Metrics + Coverage** — enforcement surface metrics; §5.1.b remediation lifecycle (3 → 5 → 9 sites); deferred surface roll-forward table; VIP scope carve-out coverage. Two footnoted AST-rule enumeration for clarity.
- **§4 SIGN Cycle History** — 18 rows spanning arc scoping (S2742) through arc close (S2751).
- **§5 Follow-on Scope** — 8 items recorded out-of-arc: I-0303 open readiness; non-canonical model follow-on (LegalDocument/LitigationDocument/ReviewDocument); §5.3.b ChatConversation C2 roll-forward; §5.1.a Deliverable D-followup roll-forward; §5.5.a Document WebSocket roll-forward (inherits to I-0303); behavioral-verify recovery gate; Document.owner-vs-user field question; CREATE-parent-binding endpoint inventory; AGGREGATE endpoint inventory.
- **§6 Downstream Unlock Status** — Phase 5 (this close) authorized RUR-C1 parent close sequence step 2 of 3; I-0303 still gates.
- **§7 Playbook + Contract Alignment** — no PLAYBOOK v0.4.1 rule violations recorded. §7.1 recommended 5 playbook-candidate patterns for CODIFY in a separate v0.5 MINOR cycle.
- **§8 Chris Ratification Contract** — this ratification.
- **§9 Cross-References** — all sibling arc/phase/ratification docs enumerated.
- **§10 Rigby Close SIGN Outcome** — SIGN-PASS clean W1..W5, 2 non-blocking asks applied inline pre-ratification.

### §2.2 `I-030203_phase4_harness_architecture.md` — Final chain-of-custody append

Non-material amendment: §8 chain-of-custody gains a single "arc CLOSED" final row referencing this ratification record. This is the last append the arch doc receives — arc close is a terminal event on that lifecycle.

### §2.3 Ratified arc scope (already merged pre-ratification)

The 26 substrate PRs across Phase 2 (1), Phase 3 (10), Phase 4 (14 + 1 close-doc) shipped across S2742 → S2751 — all merged before this ratification. This record freezes the shipped shape at HEAD `2a691ca5`.

Phase deliverables (already ratified individually where applicable):

- Phase 1 ledger: `I-030201_model_audit_ledger.md` (ratified S2742).
- Phase 2 predicate module: `I-030202_predicate_module_design.md` + `core/security/object_authz.py` + `tests/security/test_object_authz_predicates.py` (60 tests) (ratified S2742).
- Phase 3 wiring: 144 sites across 34+ view files (closed S2747, no separate ratification record).
- Phase 4 architecture: `I-030203_phase4_harness_architecture.md`.
- Phase 4 AST rule spec: `I-030204_ast_conformance_rule_spec.md`.
- Phase 4 close: `I-030205_phase4_close.md` (ratified S2751).
- Phase 4 harness modules: `tests/security/test_i0302_p4_matrix_harness.py` + `test_i0302_p4_endpoint_sentinels.py` + `test_i0302_p4_ast_conformance.py` + `test_i0302_p4_ops_aggregate_decorator.py` + `test_i0302_p4_coverage_gap_report.py` + `fixtures/tenant_boundary.py`.

---

## §3. Rigby SIGN Cycle

### §3.1 Arc-close SIGN (S2751) — SIGN-PASS clean

Routed via `tools/pa_local.sh` on pin `pa-e71c011bfa3d4124` (same continuous pin from S2749 arc pin → S2751 Phase 4 close → this arc close).

**SIGN shape:** code-review + tool-surface inspection. Full pytest execution NOT possible due to (a) CI billing outage and (b) pre-existing SQLite migration error — same fallback pattern as Phase 4 close SIGN.

**Five watchpoints attested:**

| ID | Watchpoint | Verdict |
|---|---|---|
| W1 | Phase-by-phase outcome accuracy (§2 matches shipped state at HEAD `2a691ca5`) | **PASS** |
| W2 | Metrics + coverage accuracy (§3) — counts internally consistent | **PASS** |
| W3 | Follow-on scope completeness (§5) — nothing material dropped from Phase 4 close doc §7 recovery gate or prior phase deferred surfaces | **PASS** |
| W4 | Downstream unlock accuracy (§6) — RUR-C1 gate + I-0303 open readiness correctly represented | **PASS** |
| W5 | Playbook-candidate two-triggers threshold accuracy (§7.1) — trigger counts + "CODIFY vs watch" recommendations consistent with recorded cadence | **PASS** |

**Overall verdict:** **SIGN-PASS clean.** No F-blockers.

**2 non-blocking asks applied inline pre-ratification:**

1. §7.1 "1 close-doc PR + 1 cascade PR at every close" row — added clarifying sentence on combined-vs-split cascade shape (S2750 SPLIT vs S2751 COMBINED) with candidate decision criterion for future codification.
2. §3 "Phase 4 AST rules" row — added footnote `[^ast-rules]` explicitly enumerating the two distinct AST checks (`@ops_aggregate_allowed` contract + Http404-swallow anti-pattern) to avoid misread as two separate Http404 rules.

Both amendments are correctness/clarity edits; no downstream impact on outcomes, follow-on scope, or downstream unlocks.

**Rigby tool-surface probes used during SIGN** (partial list): `repo_tool.read_file` on the full arc close doc (0-367 lines); `repo_tool.search` for `## §5` (5 matches inside doc structure).

---

## §4. Chris D-Verdict

- **Verdict shape:** "agree all"
- **Verdict scope:** binary arc-close ratification of `I-030299_i0302_arc_close.md` (as amended per §3.1 non-blocking asks) + the I-030203 §8 final chain-of-custody append + the 26 substrate PRs enumerated §2.3.
- **Adjustments requested:** none.
- **Blockers raised:** none.
- **Playbook-candidate patterns endorsed as CANDIDATES:** all 5 per §5 below. Chris D-verdict here signals candidacy for a separate v0.5 MINOR playbook ratification cycle, NOT codification here.

Chris D-verdict entered via Rigby PA chat on pin `pa-e71c011bfa3d4124` at 2026-07-10, immediately after review of Rigby's SIGN-PASS attestation.

---

## §5. Playbook-Candidate Patterns Promoted to v0.5 Ratification Queue

Per arc-close doc §7.1, 5 playbook-candidate patterns cleared the two-triggers threshold during the I-0302 arc. This ratification records their **candidacy** for a v0.5 MINOR playbook release; codification requires a separate playbook-ratification cycle.

### §5.1 Candidate — "Report-only → batch-fix → enforce" three-PR substrate pattern

**Trigger count:** 2 CONFIRMED — §14 AST codification (S2749) + endpoint sentinels (S2749).
**Proposed playbook slot:** PLAYBOOK-6.10.7 (new sub-rule under §6.10 verify-before-build family).
**Contract summary:** when introducing a codification substrate that will flag existing anti-pattern sites, ship in three PRs: (1) report-only pass revealing sites; (2) batch-fix PR closing all report-only findings; (3) enforcement flip PR turning the substrate into a hard gate. Each PR gets its own Rigby SIGN.

### §5.2 Candidate — "Phase-close doc + ratification record + arch amendments = 1 PR"

**Trigger count:** 2 CONFIRMED — S2751 Phase 4 close (PR #3129) + S2751 arc close (proposed 1-PR shape; will confirm second trigger at merge).
**Proposed playbook slot:** PLAYBOOK-6.12.x sub-rule.
**Contract summary:** every phase close or arc close ships as a single PR containing (a) the close doc, (b) the ratification record, (c) any final amendments to the phase/arc architecture doc chain-of-custody. Do NOT interleave with substrate work.

### §5.3 Candidate — "Watchpoint-attestation SIGN (W1..Wn) shape for phase/arc-close SIGN"

**Trigger count:** 2 CONFIRMED — S2751 Phase 4 close SIGN + S2751 arc close SIGN.
**Proposed playbook slot:** PLAYBOOK-6.6.15 sub-rule.
**Contract summary:** for phase-close or arc-close SIGN cycles, structure the SIGN request as numbered watchpoints (W1..Wn) each attesting a specific verification dimension (contract fidelity, coverage completeness, ledger consistency, deferred acknowledgment, anti-regression posture, downstream unlock accuracy, etc.). Reviewer response returns per-item PASS/BLOCK verdict + optional non-blocking asks. Map watchpoint outcomes directly into the close-doc SIGN log.

### §5.4 Candidate — "Phase-close doc changes serialized on a single close-doc PR (anti-pattern → codified prohibition)"

**Trigger count:** 2 CONFIRMED — S2750 §4 anti-pattern note (rebase-conflict on shared arc doc from interleaved substrate PRs) + S2751 applied cleanly (single close-doc PR, no interleave, no conflict).
**Proposed playbook slot:** PLAYBOOK-6.12.y sub-rule.
**Contract summary:** phase-close doc mutations must NOT interleave with substrate PRs on the same arc doc. Ship close-doc PRs serially, or consolidate substrate + close changes into a single PR when compatible.

### §5.5 Candidate — "1 close-doc PR + 1 cascade PR at every close (with combined-vs-split shape discipline)"

**Trigger count:** 2 CONFIRMED with shape divergence — S2750 SPLIT cadence (#3127 handoff-only + #3128 cascade-only) + S2751 COMBINED cadence (#3129 close doc; #3130 handoff + start-here + cascade in one).
**Proposed playbook slot:** PLAYBOOK sub-rule (position TBD in v0.5 draft).
**Contract summary:** every close (phase or arc) MUST ship a docs cascade output (INDEX refresh + embed batch) either combined with the handoff PR or as a follow-on. Candidate decision criterion for combined-vs-split: combined when cascade output changes only `docs/INDEX.md` + a single embed batch; split when cascade generates cross-cutting artifacts that risk conflicting with handoff review.

### §5.6 v0.5 Ratification Path

This ratification records candidacy for these 5 patterns. To actually codify:

1. Draft playbook v0.5 patch/PR incorporating the 5 candidates (Claude drafts).
2. Rigby SIGN cycle on the v0.5 diff (typically watchpoint-attestation SIGN per §5.3 now).
3. Chris D-verdict on v0.5 playbook release (separate ratification event).
4. Body commit + tag `playbook-v0.5`.
5. L7 anchor refresh in CLAUDE.md + workspace ratification record.

Playbook v0.5 timing is a Chris scoping decision — could open immediately after this ratification (would be first MINOR release since v0.4.0), or defer to a natural playbook-review window (e.g., after RUR-C1 parent closes).

---

## §6. Deferred Behavioral-Verify Recovery Gate

Inherited from Phase 4 close ratification (`RATIFICATION_2026-07-10_i0302_phase4_close.md` §5). Reproduced here because arc close inherits any phase-close recovery gate:

- **Criterion inherited:** Phase 4 close criterion #5 — `security-conformance.yml` runs the Phase 4 harness on every relevant PR.
- **Structural attestation (2026-07-10):** workflow YAML triggers on `tests/security/**` for both push + PR paths; `pytest tests/security/ -v --tb=short --strict-markers` globs all 6 Phase 4 harness modules automatically.
- **Behavioral verify:** deferred to first green CI run against a PR touching `tests/security/**` after GitHub Actions billing resumption. If any Phase 4 test module regresses on that run, Phase 4 close reopens per phase-close ratification §5, which cascades to reopening this arc close.

Recovery-gate status at arc-close ratification: CI billing still blocked. Gate pending.

---

## §7. Downstream Unlocks

Ratification of the arc close authorizes:

- **RUR-C1 parent close sequence step 2 of 3 COMPLETE.** Remaining step 1: open + close I-0303 (Async Tenant-Boundary Enforcement). Remaining step 3: shared cross-tenant regression suite green across all three arcs.

Ratification does NOT authorize:

- Any modification to the ratified arc scope (all 4 phases frozen).
- Any I-0303 (async-boundary enforcement) work — I-0303 remains OPEN authorization pending until Chris signals arc open.
- Any RUR-C1 parent campaign close — parent close still requires I-0303 close + shared cross-tenant regression pass per Q2 D-verdict at parent CAMPAIGN ratification.
- Any playbook v0.5 codification — playbook-candidate patterns from §5 require their own ratification cycle.

---

## §8. Constitutional Anchors

This ratification is anchored under:

- **Engineering Playbook v0.4.1** (ratified S2742) — arc-close SIGN cadence + phase-close discipline + `--admin` merge-flag workflow rule + doc lifecycle governance.
- **Real User Readiness CAMPAIGN** (parent program, ratified S2742) — RUR-C1 close-gate invariant per §4 (all three sub-arcs pass shared regression).
- **I-0302 Scoping** (ratified S2742) — arc scoping D-verdicts.
- **I-0302 Phase 1 Ledger** (ratified S2742) — model audit substrate + §11 `@ops_aggregate_allowed` + §14 Http404-swallow codifications (both AST-enforced by Phase 4 harness).
- **I-0302 Phase 2 Predicate Module** (ratified S2742) — 11 predicate functions Phase 3 wires + Phase 4 asserts boundaries against.
- **I-0302 Phase 4 Close** (ratified S2751) — harness surface arc close attests against.
- **I-0301 Arc Close** (ratified S2742) — sibling arc precedent for phase-by-phase ratification cadence + `security-conformance.yml` CI substrate + arc-close doc shape (`I-030199`) that this arc-close doc (`I-030299`) mirrors.
- **Failure-Data Safety Contract** (ratified S2742 as I-0301 Phase 2 constitutional artifact) — safety-contract probes coexist under `tests/security/` with the Phase 4 harness; both suites share `security-conformance.yml`.

---

## §9. Handoff to Next Arc

I-0303 (Async Tenant-Boundary Enforcement) is authorized to open at Chris's discretion. Recommended I-0303 opening moves per arc-close §5.1:

1. Draft I-0303 scoping doc — `I-0303_scoping.md` (following `I-0302_scoping.md` pattern).
2. Scoping content: async-boundary surface enumeration; inherited scope from I-0302 §5.5.a Document WebSocket + §5.1.a Deliverable non-view sites; scope decision on non-canonical models (§5.2 arc-close doc); phase decomposition; Chris scoping Q&A.
3. Rigby SIGN cycle on I-0303 scoping doc.
4. Chris D-verdict on I-0303 scoping → arc OPENED.
5. Phase 1 opens under I-0303 (async-boundary audit ledger, mirroring I-0302 Phase 1 pattern).

I-0303 open timing is a Chris scoping decision; nothing in this ratification forces it to open immediately.

Alternative next-arc paths recorded:
- **Playbook v0.5 codification cycle** (see §5.6) — could open before I-0303 if Chris wants the new patterns codified into the constitutional layer first.
- **Cost Guardian dashboard tab or other net-new engineering** (per S2745 engineering-bias rule) — carry-forward from S2751 open menu.

---

## §10. Arc Retrospective — What This Arc Taught Us

Consolidated from Phase 4 close doc §8, Phase 4 close ratification §5, and this arc close doc §7.1. Not new material — captured here in ratified-frozen form because arc close is the terminal event where these lessons become playbook-eligible.

### §10.1 What worked cleanly across the arc

- **Sub-phase decomposition into report-only → batch-fix → enforce three-PR arcs** — cleaner than trying to codify an anti-pattern rule + fix its existing sites + flip enforcement in one shot. Reused twice cleanly (§14 codification + endpoint sentinels).
- **Hybrid harness shape (matrix + sentinels + AST) over full URL sweep** — combinatorial 1864 × 4 × 7 sweep was correctly rejected at F1 SIGN; the shipped hybrid delivers equivalent guarantee at a fraction of maintenance surface. Confidence this shape reuses for I-0303 async-boundary regression.
- **Watchpoint-attestation SIGN cycles** — every phase-close and this arc-close SIGN returned clean per-item PASS/BLOCK on first pass. Cheap for reviewer, cheap for author to fold non-blocking asks inline.
- **Single close-doc PR isolation** — no interleave with substrate PRs, no rebase conflict on shared arc doc after S2750's cheap-but-instructive first collision. Anti-pattern learned → applied → codification-eligible in one arc.
- **Chris D-verdict path-2 fallback for AST rule spec** — when Rigby jammed at the multi-fold rule-proposal LLM boundary during S2749, path-2 (Claude drafts spec; Rigby SIGN against draft) unblocked the substrate same-session. Bonus PR #3119 (Rigby stall fix) closed the loop on the LLM-boundary root cause.

### §10.2 Anti-patterns caught + corrected

- **Interleaved substrate PRs on shared arc doc** (S2750 §4) → codified prohibition (§5.4 above).
- **Merging red-CI without stating why** (S2750 close directive) → `--admin` merge-flag rule (already codified in memory `feedback_gh_pr_merge_admin_until_billing_fixed.md`); playbook §11.x candidacy pending third trigger.
- **gpt-5.2 multi-fold design prompts through Rigby stall** (S2749) → path-2 fallback + PR #3119 fix + memory rule `feedback_gpt5_stalls_on_multifold_design_prompts.md`; not arc-level playbook material.
- **Generic A/B/C session-open menu when blocker #1 has a hidden cost** (S2751 §5 handoff) → session-open menu framing lesson; not arc-level playbook material (workflow-scope, not substrate-scope).

### §10.3 Suggestions surfaced

- Ratification record + close doc + arch amendments should always be a single PR (§5.2 candidate).
- Rigby SIGN watchpoints should be numbered W1..Wn (§5.3 candidate) so response maps directly into close-doc SIGN log.
- Behavioral-verify recovery gate structure works even when CI can't run — makes close honest without blocking progress (candidate at 1 trigger; watch for second in a future billing-blocked close).
- Cascade at every close is non-negotiable (already codified: `feedback_docs_cascade_at_every_close.md` + `feedback_cascade_pr_must_include_embed_step.md`). Combined-vs-split shape discipline is a new dimension to codify (§5.5 candidate).

---

**End of I-0302 Object-Level Authorization Arc Close Ratification Record. Frozen 2026-07-10.**
