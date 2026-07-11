---
title: "Engineering Playbook v0.5 — Proposal Shape (Stage 1)"
status: shape-ratified
authority: chris-d-verdict-ratified-2026-07-11-S2752
session_added: 2752
last_updated: 2026-07-11
predecessor_version: v0.4.1
proposed_version: v0.5.0
version_bump_class: MINOR
head_at_draft: d5e54777
rigby_sign_state: pre-D-verdict-lean-recorded-Option-B-and-EXTEND
chris_d_verdicts_resolved:
  - Q1 Chapter fit — Option B (Ch 7 §7.4/§7.5/§7.6 activation) — RATIFIED 2026-07-11 S2752
  - Q2 All 5 candidates in v0.5 — RATIFIED 2026-07-11 S2752
  - Q3 Watchpoint SIGN — EXTEND ROS §6.10.3 (SIGN wrapper importing ROS mechanics) — RATIFIED 2026-07-11 S2752
  - Q4 Stage 2 timing — fresh session immediately after shape doc lands — RATIFIED 2026-07-11 S2752
  - Q5 Manifest freeze — bundle under v0.5 SIGN cycle — RATIFIED 2026-07-11 S2752
predecessor_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_arc_close.md §5
---

# Engineering Playbook v0.5 — Proposal Shape (Stage 1)

Playbook §10.2.2 Stage 1 shape proposal for v0.5 MINOR amendment codifying 5 candidate patterns promoted at I-0302 arc close (`RATIFICATION_2026-07-10_i0302_arc_close.md` §5). Stage 2 drafting occurs in a fresh session; this doc locks the shape, slot fit, evidence citations, and version-bump class **before** drafting resources are spent.

## §1 What this doc is

- **A Stage 1 shape.** Not the amendment. Not the ratification record. Locks the design decisions that drive Stage 2 drafting.
- **A slot-fit audit.** Ratification §5 proposed rule slots (6.10.7, 6.6.15, 6.12.x/y). This doc audits those against the chapter dependency discipline of §6 and flags Chapter-fit concerns for D-verdict.
- **A D-verdict menu.** Section §8 enumerates open questions. Each has a Claude lean + one-sentence reason; each awaits D-verdict before Stage 2 drafting begins.

## §2 Version bump analysis

**Class:** MINOR (per PLAYBOOK-10.5.1).

**Rationale:**

- 5 new rules added; 0 existing rules removed, modified, or reclassified. Matches PLAYBOOK-10.5.1 admissible additions (new rules, new sub-sections).
- Backward compatibility preserved per PLAYBOOK-10.5.2 — no existing rule's downstream applicability changes.
- Full SIGN cycle required per PLAYBOOK-10.5.3 — lightweight SIGN not permitted for MINOR.
- v0.5 continues the ancestry chain: v0.1.0 → v0.2.0 → v0.3.0 → v0.4.0 → v0.4.1 (PATCH) → **v0.5.0 (MINOR)**.

**Not MAJOR:** none of the 5 candidates would remove, replace, or reclassify any existing rule; none reorganize chapter structure.

**Not PATCH:** each candidate is substantive new normative content, not a typo fix, link repair, or clarification.

## §3 Chapter-fit audit — 5 candidates vs current chapter map

Ratification §5 proposed slots under §6.6, §6.10, §6.12. Chapter 6's authored scope is **Provenance and Evidence**. Auditing each candidate against Ch 6 scope:

| Candidate | Ratification proposed slot | Actual discipline domain | Chapter-fit verdict |
|---|---|---|---|
| §5.1 Report-only → batch-fix → enforce three-PR pattern | PLAYBOOK-6.10.7 | Delivery discipline (staged codification) | **Marginal fit for §6.10.** §6.10 is verify-before-dispatch; §6.10.6 already extends to verify-before-implementation. Extending further to verify-before-codification-flip is defensible but stretches §6.10's authored scope. |
| §5.2 Phase-close 1-PR (close doc + ratification + arch amendments) | PLAYBOOK-6.12.x | Close-ceremony discipline (delivery bundling) | **Poor fit for §6.12.** §6.12 is Extension Points (informative, MAY-future-extensions). Rules do not belong in §6.12. |
| §5.3 Watchpoint-attestation SIGN (W1..Wn) shape | PLAYBOOK-6.6.15 | SIGN methodology (per-item attestation structure) | **Wrong chapter.** §6.6 is Evidence Admission Standard (per-class evidence thresholds). Per PLAYBOOK-6.10.3 SIGN methodology is inherited from the Research Operating System — the playbook currently does not host SIGN-shape rules. |
| §5.4 Phase-close doc serialization (anti-pattern → prohibition) | PLAYBOOK-6.12.y | Close-ceremony discipline (delivery serialization) | **Same as §5.2 — poor fit for §6.12.** |
| §5.5 1 close-doc PR + 1 cascade PR + combined-vs-split shape | Position TBD | Close-cascade discipline (delivery cadence) | **No slot proposed.** Close-ceremony discipline domain, same as §5.2/§5.4. |

**Structural finding:** 4 of 5 candidates are **arc/phase close-ceremony delivery discipline**. The playbook has no ratified chapter hosting this domain today. Candidate §5.3 is a **SIGN methodology extension**, currently inherited from the ROS.

### §3.1 Chapter placement options

- **Option A — Stretch Ch 6 to host these rules.** Slot as ratification proposed but rename §6.10's authored scope to include "verification-and-delivery discipline" via a v0.5 preamble clarification. Cheapest. Weakens §6's authored coherence.
- **Option B — Activate Chapter 7 (Session Discipline, STUB) partially.** Ch 7 currently STUB with only §7.1/§7.2/§7.3 authored. Ch 7 frontmatter declares scope as "session-open orientation; session-close handoff production; cascade sequencing at session boundaries" — a natural home. Add §7.4 for close-ceremony discipline (candidates §5.2/§5.4/§5.5) and §7.5 for staged-codification discipline (candidate §5.1). Watchpoint SIGN (§5.3) fits under §7.6 as session-close SIGN-cycle discipline.
- **Option C — Open a new "Delivery Discipline" chapter slot.** Cleanest structurally but new chapters typically ride MAJOR bumps. PLAYBOOK-10.5.1 does allow "new chapters into reserved slots" under MINOR, so it's admissible if a slot is reserved.
- **Option D — Defer 4 of 5 to v0.6.** Ship v0.5 with only candidate §5.1 into §6.10.7 as a minimal extension; hold §5.2/§5.3/§5.4/§5.5 for a coordinated close-ceremony chapter authored in v0.6. Slowest but most disciplined.

**Claude lean: Option B.** Activates a STUB chapter within its declared scope. Ch 7's frontmatter already names "session-close handoff production" and "cascade sequencing at session boundaries" — candidates §5.2/§5.4/§5.5 map directly. Watchpoint SIGN (§5.3) fits as close-cycle SIGN discipline. Three-PR staged codification (§5.1) is a stretch for Ch 7 but codification substrates are typically session-scoped delivery — defensible under Ch 7's scope. Cost: forces Stage 2 to author 3 new §7 sub-sections instead of dropping bullets into existing sections. Chris D-verdict required.

## §4 Per-candidate rule shape (Option B slots)

For each candidate: rule intent, proposed statement class, proposed slot under Option B, evidence citations meeting §6.6 thresholds.

### §4.1 Candidate §5.1 — Report-only → batch-fix → enforce three-PR substrate pattern

**Intent:** When introducing a codification substrate that will flag existing anti-pattern sites, the substrate MUST ship in three sequential PRs: (1) report-only harness merged with warning-only outcome; (2) batch-fix PR closing all report-only findings; (3) enforcement flip PR turning the harness into a hard gate. Each PR gets its own SIGN.

**Proposed statement class:** [GR] Governance Rule — governs how codification is dispatched.

**Proposed slot (Option B):** PLAYBOOK-7.5.1 (new sub-section §7.5 "Staged codification of anti-pattern substrates").

**Evidence citations:**

- E3: `docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md` §4 + §5 + §9 (rule spec + report-only + enforcement-flip criteria)
- E6: `docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md` (three-PR sequence executed: #3116 report-only → #3117 batch-fix → #3118 enforcement flip; SHAs `f586a2cf` → `40f2bffc` → `f1cf8950`)
- E6: `docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md` (second trigger via endpoint sentinels)
- E2: `RATIFICATION_2026-07-10_i0302_arc_close.md` §5.1 (candidacy record)

**§6.6 threshold check:** [GR] requires ≥2 sources with at least one E1/E2 + at least one E6. Met: E2 + E6.

### §4.2 Candidate §5.2 — Phase-close 1-PR (close doc + ratification + arch amendments)

**Intent:** Every phase close or arc close MUST ship as a single PR bundling (a) the close doc, (b) the ratification record, (c) any final amendments to the phase/arc architecture doc chain-of-custody. Interleaving with substrate work is prohibited.

**Proposed statement class:** [GR] Governance Rule.

**Proposed slot (Option B):** PLAYBOOK-7.4.1 (new sub-section §7.4 "Close-ceremony delivery discipline").

**Evidence citations:**

- E4: commit `f341581a` (PR #3129 — Phase 4 close 1-PR bundle: close doc + ratification + arch amendments)
- E4: commit `1176b67a` (PR #3131 — Arc close 1-PR bundle: arc-close doc + ratification + I-030203 §8 append)
- E6: `docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md` (Phase 4 close ceremony trigger)
- E6: `docs/handoffs/SESSION_2751_I0302_ARC_CLOSED.md` (Arc close ceremony trigger)
- E2: `RATIFICATION_2026-07-10_i0302_arc_close.md` §5.2 (candidacy record)

**§6.6 threshold check:** [GR] requires ≥2 sources with at least one E1/E2 + at least one E6. Met: E2 + E6 (E4 supplemental).

### §4.3 Candidate §5.3 — Watchpoint-attestation SIGN (W1..Wn) shape

**Intent:** For phase-close or arc-close SIGN cycles, the SIGN request MUST be structured as numbered watchpoints (W1..Wn) each attesting a specific verification dimension. Reviewer response returns per-item PASS/BLOCK verdict + optional non-blocking asks. Watchpoint outcomes map directly into the close-doc SIGN log.

**Proposed statement class:** [GR] Governance Rule (SIGN-shape).

**Proposed slot (Option B):** PLAYBOOK-7.6.1 (new sub-section §7.6 "Session-close SIGN-cycle discipline").

**Evidence citations:**

- E6: `docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md` §SIGN (first watchpoint SIGN cycle)
- E6: `docs/handoffs/SESSION_2751_I0302_ARC_CLOSED.md` §SIGN (second watchpoint SIGN cycle)
- E2: `RATIFICATION_2026-07-10_i0302_arc_close.md` §5.3 + §10.1 (candidacy + retrospective)
- E3: `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` §SIGN (inherited SIGN methodology; watchpoint shape is a specialization)

**§6.6 threshold check:** [GR] requires ≥2 sources with at least one E1/E2 + at least one E6. Met: E2 + E6.

**Cross-chapter concern:** SIGN methodology inherited from ROS per PLAYBOOK-6.10.3. Adding SIGN-shape rules to the playbook creates a shared-authority surface. D-verdict needed on whether PLAYBOOK-7.6.1 SUPERSEDES the ROS SIGN-shape guidance or EXTENDS it (see Q3 in §8).

### §4.4 Candidate §5.4 — Phase-close doc serialization (anti-pattern → codified prohibition)

**Intent:** Phase-close doc mutations MUST NOT interleave with substrate PRs on the same arc doc. Close-doc PRs ship serially, or consolidate substrate + close changes into a single PR when compatible.

**Proposed statement class:** [GR] Governance Rule.

**Proposed slot (Option B):** PLAYBOOK-7.4.2 (adjacent to §5.2 rule, same §7.4 sub-section).

**Evidence citations:**

- E6: `docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md` §4 (anti-pattern first trigger: rebase-conflict on shared arc doc from interleaved substrate PRs)
- E6: `docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md` (second trigger: applied cleanly, single close-doc PR, no conflict)
- E2: `RATIFICATION_2026-07-10_i0302_arc_close.md` §5.4 (candidacy record)

**§6.6 threshold check:** [GR] requires ≥2 sources with at least one E1/E2 + at least one E6. Met: E2 + E6.

### §4.5 Candidate §5.5 — 1 close-doc PR + 1 cascade PR + combined-vs-split shape discipline

**Intent:** Every close (phase or arc) MUST ship a docs cascade output (INDEX refresh + embed batch), either combined with the handoff PR or as a follow-on. Decision criterion for combined-vs-split: combined when cascade output changes only `docs/INDEX.md` + a single embed batch; split when cascade generates cross-cutting artifacts that risk conflicting with handoff review.

**Proposed statement class:** [GR] Governance Rule.

**Proposed slot (Option B):** PLAYBOOK-7.4.3 (adjacent to §5.2/§5.4, same §7.4 sub-section).

**Evidence citations:**

- E4: commit `7fe19a1c` (S2750 SPLIT cadence — #3128 cascade-only after #3127 handoff-only)
- E4: commit `d5e54777` (S2751 COMBINED cadence — #3130 handoff + start-here + cascade in one)
- E6: `docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md` (SPLIT trigger)
- E6: `docs/handoffs/SESSION_2751_I0302_ARC_CLOSED.md` (COMBINED trigger)
- E2: `RATIFICATION_2026-07-10_i0302_arc_close.md` §5.5 (candidacy record + shape divergence note)

**§6.6 threshold check:** [GR] requires ≥2 sources with at least one E1/E2 + at least one E6. Met: E2 + E6.

## §5 Slot proposal summary (Option B)

Assuming Chris D-verdict on Option B:

| Rule ID | Class | Chapter §7 sub-section | Candidate |
|---|---|---|---|
| PLAYBOOK-7.4.1 | [GR] | §7.4 Close-ceremony delivery discipline | §5.2 Phase-close 1-PR |
| PLAYBOOK-7.4.2 | [GR] | §7.4 (same) | §5.4 Phase-close serialization |
| PLAYBOOK-7.4.3 | [GR] | §7.4 (same) | §5.5 Close-doc + cascade PR discipline |
| PLAYBOOK-7.5.1 | [GR] | §7.5 Staged codification of anti-pattern substrates | §5.1 Three-PR substrate |
| PLAYBOOK-7.6.1 | [GR] | §7.6 Session-close SIGN-cycle discipline | §5.3 Watchpoint-attestation SIGN |

Total: 5 rules, 3 new sub-sections under Ch 7. Ch 7 rule count: 3 existing (§7.1.1, §7.2.1, §7.3.1) + 5 new = 8. Playbook total rule count: 196 + 5 = 201.

## §6 Evidence manifest additions

Per PLAYBOOK-6.6.1, ratified rules must cite sources enumerated in the frozen evidence manifest (`docs/research/platform/engineering_playbook_evidence_manifest.md`). The v0.5 amendment MUST add the following entries to the manifest before dispatch to SIGN:

- E6: `docs/handoffs/SESSION_2749_I0302_PHASE_4_SUB_PHASE_3_SUBSTRATE_LARGELY_CLOSED.md`
- E6: `docs/handoffs/SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md`
- E6: `docs/handoffs/SESSION_2751_I0302_PHASE_4_CLOSED.md`
- E6: `docs/handoffs/SESSION_2751_I0302_ARC_CLOSED.md`
- E4: commit `f341581a` (PR #3129)
- E4: commit `1176b67a` (PR #3131)
- E4: commit `7fe19a1c` (PR #3128)
- E4: commit `d5e54777` (PR #3130)
- E4: commit `f586a2cf` (PR #3116 report-only)
- E4: commit `40f2bffc` (PR #3117 batch-fix)
- E4: commit `f1cf8950` (PR #3118 enforcement flip)
- E3: `docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md`
- E2: `RATIFICATION_2026-07-10_i0302_arc_close.md`

Manifest update is a Stage 2 mechanical task (fresh session).

## §7 Stage 2 execution plan (fresh session)

Per Chris's B pick (shape now, execute fresh session per §10.2.2 Stage 1):

1. **Session-open orientation** — new session reads this shape doc + arc-close ratification + v0.4.1 playbook state.
2. **Manifest update** — add §6 evidence entries to `engineering_playbook_evidence_manifest.md`.
3. **Draft §7.4/§7.5/§7.6 subsections** — RFC-2119 rule text per §4 shape, with full evidence citations.
4. **Draft Ch 7 frontmatter update** — bump `Last substantive change: v0.5.0`; update `Rule ID range: PLAYBOOK-7.1.1 through PLAYBOOK-7.6.1`; update `Statement classes present`.
5. **Update Appendix D chain row** — v0.5 ancestry entry.
6. **Run 6-check author verification** (PLAYBOOK-6.10.1 verifications 1-6) — record results in amendment provenance.
7. **Rigby SIGN cycle** — using watchpoint-attestation SIGN shape (dogfooding candidate §5.3 pre-ratification).
8. **Chris D-verdict** — ratify or block per SIGN findings.
9. **Body commit + tag `playbook-v0.5`** — single PR per candidate §5.2 shape (dogfooding).
10. **L7 anchor refresh in CLAUDE.md** — new v0.5 line + workspace ratification record.
11. **Cascade** — 4-step docs cascade per memory rule (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `sync_docs_index_to_documents --embed`).

Estimated Stage 2 effort: 1 focused session (drafting + verification + SIGN + ratification + PR). Feasible in a fresh session with clean context budget.

## §8 Open questions for Chris D-verdict (blocks Stage 2)

1. **Q1 — Chapter fit disposition (§3).** Confirm Option B (activate Ch 7 §7.4/§7.5/§7.6), or pick A/C/D?
   - **Claude lean: B** — activates STUB chapter within its declared scope; gives all 5 candidates a coherent home; no MAJOR bump needed.

2. **Q2 — Rule count target for v0.5.** All 5 candidates in v0.5, or split into v0.5 (close-ceremony triplet §5.2/§5.4/§5.5) + v0.6 (§5.1 staged-codification + §5.3 SIGN shape)?
   - **Claude lean: All 5 in v0.5** — all 5 have 2-trigger confirmation; splitting adds ceremony overhead without evidence benefit.

3. **Q3 — Watchpoint SIGN authority (§4.3 cross-chapter concern).** Does PLAYBOOK-7.6.1 SUPERSEDE the ROS SIGN-shape guidance or EXTEND it?
   - **Claude lean: EXTEND** — the ROS SIGN methodology is the parent contract; watchpoint shape is a specialization for close-cycle SIGN. Playbook rule scopes to close-cycle SIGN only; general SIGN remains ROS-hosted.

4. **Q4 — Stage 2 timing.** Fresh session immediately after this shape doc lands, or defer to a natural window (e.g., after CI billing recovery, or in the S2753+ range)?
   - **Claude lean: Fresh session immediately after shape doc lands** — 5 candidates all fresh, evidence still hot, no compounding drift risk.

5. **Q5 — Manifest freeze checkpoint.** Does the manifest update (§6) require its own SIGN cycle, or is it a mechanical dispatch under the same v0.5 SIGN?
   - **Claude lean: Mechanical dispatch under same SIGN** — manifest entries are cited by v0.5 rules; SIGN reviewer verifies both together.

## §9 Provenance chain

- **Ratification of candidacy** — `RATIFICATION_2026-07-10_i0302_arc_close.md` §5 (Chris D-verdict 2026-07-10 S2751; candidacy only, NOT codification).
- **Shape drafting** — Claude, S2752, HEAD `d5e54777`, this doc.
- **SIGN state** — pending Chris D-verdict on §8 questions; SIGN dispatched after D-verdict resolves.
- **Codification** — Stage 2 fresh session per §7 plan.
