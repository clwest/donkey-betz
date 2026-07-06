---
title: "Implementation Operating System — how research findings become shipped code"
status: active v1.4 (v1 Chris-ratified 2026-07-06 with D1–D7, D9, D10, D12 accepted at recommended option; D8 deferred; D11 accepted with Wave 1 required before 3rd arc. v1.1 = execution-refinement patch 2026-07-06 after Part 11 first-execution surfaced 7 findings. v1.2 = execution-refinement patch 2026-07-06 after Arc I-0100 Stage 1 first-execution surfaced 4 findings. v1.3 = cascade-discipline refinement 2026-07-06 codifying pre-PR vs post-merge cascade policy + PR-body evidence block after the arc-open PR / separate-cascade-PR pattern recurred 3× same-day. v1.4 = fresh-session Stage 2 readiness refinement 2026-07-06 codifying B1–B6 gaps found when simulating a cold Claude session opening Stage 2 for Arc I-0100 after IB-Q1-BOOT-01 P0 prep PR opened: stage_state enum, Stage 2 entry gate + opening ceremony, design-prep equivalence via scoping §9, pr_refs/arc_ref inline syntax, implementation ADR SIGN cadence, and 00-START-NEXT-SESSION.md ownership — see verifier_loop.)
authority: process
session_added: 2500
last_verified: 2026-07-06
companion_anchors:
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md   # upstream truth-discovery OS
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md            # research-class specialization
  - docs/research/ARCHITECTURE_INDEX.md                  # research library navigation
  - docs/research/OPEN_ARCS.md                           # cross-session arc manifest
  - docs/research/platform/cross_domain_integration_audit.md  # bridge doc — disconnect map
  - docs/PLATFORM_INVENTORY.md                            # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                           # platform narrative anchor
  - docs/EMPLOYEE_OS_PRIMITIVES.md                        # anti-duplication matrix
  - docs/AUDIT_FINDINGS.md                                # Celery deferred list
  - CLAUDE.md                                             # session entry point
verifier_loop: |
  v1 (2026-07-06): initial draft authored by Claude Code in
  response to Chris's short command "start Implementation Operating
  System design arc." Draft written by consuming
  RESEARCH_OPERATING_SYSTEM.md structure (§0–§20), DOMAIN_RESEARCH
  _PLAYBOOK.md v2, and the 13 canonical xx99 summaries
  (Groups 1300–2600, minus intentionally-skipped 2300 Mobile) plus
  the cross_domain_integration_audit.md v4 (§14 through v4 arc
  closes for 1300–2400 and the emergent CX-P1 through CX-P8
  patterns).
  v1.1 (2026-07-06): Rigby SIGN cycle 1 completed via dedicated
  fresh SIGN isolation pin `pa-f9164418e56940ea` (single-batch × 4-Q
  cadence per S1300–S2400 established pattern). All four questions
  landed SIGN-with-edits at Medium confidence; no BLOCKED. 20 folds
  applied wholesale, covering: schema field additions
  (`design_state`, `spec_ref`, `adr_ref`, `verification_method`,
  `owner`, `delegate_owner`); 3 additional intake rejection
  conditions; six-dimension scoring split (revenue impact +
  attention preservation as separate dimensions); CX-P10 hard
  criterion via schema enum; SAFE_AUTONOMOUS irreversibility carve-
  out; Stage 3 SIGN mandatory conditions; §5.0 term definitions
  (consumer, owner-model-qualified, fleet-key surfaces,
  F4-CANDIDATE); §5.1 rules 6–10 preserved; §8.4 pointer discipline
  (removed verbatim restatement in §5.2 rule 1); §9.2 caps labeled
  as v1 hypotheses; §9.4 Stage 5 verification cap + no-new-arc-
  while-verification-debt rule; §9.5 Chris bandwidth ceilings
  labeled as observed defaults; §15.2 split into truth authority
  (§15.2.a) + read priority (§15.2.b) mirroring Research OS §7
  intro distinction (Rigby's most substantive fold); §15.6 rule 10
  PR-state drift detection added; §4.3 Stage 1 checklist snapshot
  requirement; D11 expanded to two-wave IOS gate runner; Appendix
  B T0–T5 tier fidelity table with citation anchors. Cycle 2 NOT
  required per Rigby explicit verdict pattern (no BLOCKED, all
  edits structural/clarifying). Chris ratification of D1–D12 open
  questions is the next gate before status flips `draft → active`.
  v1.2 (2026-07-06): Chris ratified D1–D12 via directive "Default
  stance: accept the IOS v1.1 recommendations unless there is a
  concrete reason not to." Ratifications recorded inline in §13
  under each D. D1–D7, D9, D10, D12 accepted at recommended option.
  D8 deferred until first-queue construction OR explicit Chris
  directive. D11 accepted with Wave 1 (build-docs-cascade.yml
  GitHub Action) required before scaling beyond two implementation
  arcs — Wave 1 becomes a first-class arc-open gate for the third
  arc. Status flipped `draft (v1.1) → active v1`. Rigby SIGN pin
  `pa-f9164418e56940ea` retired at v1.2 close per Research OS
  22-consecutive-arc SIGN-pin retirement discipline. Full 4-step
  docs cascade (build_docs_index → build_rag_corpus →
  sync_docs_index_to_documents → embed_documents --all-unembedded)
  + build_docs_provenance executed at v1.2 close per MEMORY rule
  feedback_cascade_pr_must_include_embed_step. First implementation
  arc identity remains open (D8 deferred); first-queue construction
  Part 11 procedure has NOT been executed and requires explicit
  Chris directive.
  IOS does NOT replace, edit, or collapse the Research OS; it adds
  the downstream execution-phase governance layer that §8.4
  IMPLEMENTATION contract calls for at phase scale.
  active v1.1 (2026-07-06): execution-refinement patch after IOS
  Part 11 first execution (Chris directive following the first
  production implementation-planning session — treated as the
  first real validation that Research OS + IOS were sufficient for
  a fresh Claude session). First execution surfaced 7 findings
  (A–J in that session's deliverable 5); Chris directed adoption
  ahead of the §14.2 two-trigger codification threshold. Applied
  edits: (1) §11.2 Step 1 leaf-decision granularity rule (one
  intake row per Chris-ratifiable decision unit, not per §8 tier
  bundle); (2) §2.4 cascade-housekeeping exclusion (PLATFORM_INVENTORY
  + ARCHITECTURE_INDEX + topic-doc refreshes discharged by the
  4-step docs cascade, not implementation intake); (3) §2.2
  `intake_id` scheme extended with 5 prefixes (IB-<arc>-<seq>,
  IB-Q<queue>-<seq>, IB-CDA-<seq>, IB-CDA14-<seq>,
  IB-CXP<n>-<seq>); (4) §15.3 phase-transition supersession rule
  (active IOS + implementation-planning Chris directive overrides
  `00-START-NEXT-SESSION.md` Research-OS next-session trajectory);
  (5) §11.2 Step 6 + §11.3 default Rigby routing for ratification
  cards via a fresh IOS-scoped SIGN pin, terminal-only only on
  explicit Chris directive; (6) §15.6 rule 6 `verify_doc_claims`
  command variant clarified (use unfiltered command; sum per-doc
  drift columns; total == 0 = clean; `--only-drift` returns
  "No matching claims to run" on zero drift, which is ambiguous);
  (7) new §15.14 Rigby SIGN pin lifecycle across phase
  transitions (paused research T-slot pin preserved as comment
  above `tools/pa_local.sh` `--conversation` line (grep-anchored, currently ~:411); fresh IOS-scoped pin minted per
  implementation session for Rigby interactions; on IOS phase exit
  → restore paused research pin). No open D-question reopened.
  Not routed to a fresh Rigby SIGN cycle — refinements derived
  from a live session's execution transcript + Chris directive;
  §14.2 two-trigger codification threshold not met on any single
  finding, but Chris explicitly waived the wait per his
  refinement-authority prerogative.
  active v1.4 (2026-07-06): fresh-session Stage 2 readiness refinement
  patch after Chris directed a cold-Claude simulation of Stage 2
  startup for Arc I-0100 (post-#2948 IB-Q1-BOOT-01 P0 prep PR open,
  pre-ADR-0002 authoring). The simulation walked Level A → Level B
  → Level C bootstrap treating only repo artifacts (CLAUDE.md +
  MEMORY.md + doc tree) as input, no conversation context. Six
  gaps (B1–B6) surfaced that would materially confuse a fresh
  session opening Stage 2. Chris ratified all six via directive
  "Proceed with full IOS v1.4: apply B1–B6. Accept all six
  findings as real fresh-session Stage 2 gaps." Applied edits:
  (B1) §4.3 preamble gains stage_state enum {exit-gate-cleared,
  p0-prep-in-flight, p0-prep-merged, active, awaiting-close}
  replacing the previous ad-hoc frontmatter values; (B2) §4.3
  Stage 2 gains explicit Entry gate clause — Stage 2 opens on
  (a) docs/adr/ exists on main AND (b) either Chris explicit
  directive OR P0-prep-PR merge for Option (a) arcs; frontmatter
  stage: flips 1 → 2 at Stage 2 opening; (B3) §4.3 Stage 2 gains
  design-prep equivalence clause — if scoping doc §9 pre-scopes
  the ADR with decision question + options + constraints +
  consequences + verification implications, that section IS the
  design-prep artifact; (B4) §2.2 schema gains inline-syntax
  requirement for arc_ref and pr_refs when BACKLOG table shape
  cannot expose them as proper columns; §15.6 rule 10 gains
  tolerance for the inline syntax; (B5) §7.2 Stage 2 SIGN row
  gains explicit cadence — one Rigby SIGN cycle per ADR on the
  active arc pin, 2-Q minimum / 4-Q typical / 6-Q max, no pin
  rotation between ADRs; (B6) new §15.15 codifies
  00-START-NEXT-SESSION.md as RAG-critical startup infrastructure
  co-committed to every arc-open PR / P0-prep PR / stage-
  transition PR / arc-close PR; adds refreshed-file schema
  requirement (phase + active arc + current stage + stage_state
  + next executable action + active SIGN pin + pending PRs).
  §14.2 two-trigger codification threshold: single trigger from
  Arc I-0100 pre-ADR-0002 cold-session simulation; Chris invoked
  refinement-authority prerogative on the ratification directive.
  No Rigby SIGN cycle routed — refinement is docs-only
  clarification with no runtime effect and no open D-question
  reopened. Applied under IOS v1.4 = active status via same-
  session commit. Dogfooded: this patch's own PR runs the full
  5-step cascade + build_docs_provenance locally before PR open
  per IOS v1.3 §12.5.a, commits docs/INDEX.md + docs/_provenance
  .json diffs alongside the IOS edit, includes the §12.5.d
  cascade evidence block, and updates 00-START-NEXT-SESSION.md
  per new §15.15 (structural test of the codified rule).
  active v1.3 (2026-07-06): cascade-discipline refinement patch
  after the arc-open PR / separate-cascade-PR pattern recurred three
  times same-day (#2941 seed → #2942 cascade; #2943 IOS v1.2 patch
  → #2946 cascade; #2945 Arc I-0100 Stage 1 arc-open bundle → #2946
  cascade). Between arc-open PR merge and cascade PR merge, Rigby's
  RAG could not search the new artifact — arc scoping docs, IOS
  refinements, and BACKLOG changes were invisible during exactly
  the window when Chris would ratify them. §12.5 previously
  described cascade as an arc-close activity only; in practice
  every RAG-critical doc surface — arc scoping docs, ADRs, close
  docs, IOS patches, RATIFICATION records, and BACKLOG/DEBT/
  OPEN_ARCS updates — needs to be RAG-visible as soon as the PR
  merges, which requires cascade to co-locate in the same PR, not
  a follow-up PR. Chris's directive naming the frequency and
  impact of the pattern was the trigger; §14.2 two-trigger
  codification threshold met via 3-in-one-day recurrence.
  Applied edits: (1) §4.3 Stage 1 exit gate + Stage 2 exit gate +
  Stage 6 close: cascade evidence block required in the SAME PR
  as the artifact, not a follow-up PR; (2) §5.2 pre-merge gate 10
  added — cascade evidence block for RAG-critical artifact types;
  (3) §12.5 expanded from 4 lines to full pre-PR vs post-merge
  policy: RAG-critical artifact list, PR-body evidence block
  template, Chris-explicit-deferral clause, D11 Wave 1 interaction
  note; (4) §13 D11 cross-reference added noting Wave 1 automation
  discharges the post-merge embed step while §12.5 v1.3 rule
  covers the pre-merge co-location discipline (superset). No
  §14.2 codification threshold ambiguity — three recurrences in
  one session meets the threshold; Chris invoked
  refinement-authority prerogative on the same directive
  triggering the patch. No Rigby SIGN cycle routed — refinement
  is docs-only clarification with no runtime effect and no open
  D-question reopened. Applied under IOS v1.3 = active status via
  same-session commit. Dogfooded: this patch's own PR runs the
  full 4-step cascade + `build_docs_provenance` locally before PR
  open, commits the two versioned cascade artifacts (`docs/INDEX
  .md` + `docs/_provenance.json`) alongside the IOS edit, and
  includes the §12.5 v1.3 PR-body cascade evidence block as its
  first structural test of the codified rule.
  active v1.2 (2026-07-06): execution-refinement patch after Arc
  I-0100 Stage 1 first execution (first production implementation
  arc under IOS v1.1). Fresh Claude session executed startup +
  Stage 1 scoping plan production per user directive following
  the seed PR merge (#2941). Session surfaced 4 findings during
  planning: (1) §4.3 mis-labeled Playbook §11.1 as "20-section"
  parent-scoping template — actual is 9-section (§11.2 is the
  20-section child audit template); (2) §4.3 Stage 1 mandates a
  "Stage checklist snapshot" section in exit-gate prose but does
  NOT enumerate it in the substitution list, risking omission by
  a fresh Claude session that reads the ordered substitutions
  and misses the exit-gate prose; (3) `00-START-NEXT-SESSION.md`
  §"SESSION READY CHECK" step 5 miscites `§14.14 pin lifecycle` —
  correct citation is §15.14 (§14 is Meta-learning ledger);
  (4) ADR corpus precondition unstated at Stage 1 exit — if any
  admitted intake row is `NEEDS_ADR` but `docs/adr/` directory
  does not yet exist on `main`, Stage 2 opens into an incoherent
  state ("ADR required, nowhere to put it"). Applied edits:
  §4.3 template size 20→9 with §11.1 section list inline;
  §4.3 substitution list gains §10 Stage checklist snapshot as
  explicit ordered substitution (removed from exit-gate prose,
  cited from exit gate); §4.3 exit gate gains ADR corpus
  precondition rule (verify `docs/adr/` exists; bundle
  `IB-Q1-BOOT-01` as in-arc prep PR OR block close); §D3 gains
  cross-reference to §4.3 Stage 1 exit precondition;
  `00-START-NEXT-SESSION.md` §"SESSION READY CHECK" step 5
  citation fixed §14.14 → §15.14. §14.2 two-trigger codification
  threshold not met (single trigger from Arc I-0100 Stage 1
  planning); Chris explicitly waived the wait per his
  refinement-authority prerogative on the session-open directive
  "Apply the four IOS refinements discovered in §6 first." No
  Rigby SIGN cycle routed for this patch — refinements are
  docs-only clarifications with no runtime effect and no
  open D-question reopened. Applied under IOS v1.2 = active
  status via same-session commit.

---

# 60-second TL;DR for a fresh Claude

- **What this doc is.** The operating rules for the phase after
  research. Consumes xx99 canonical summaries + the cross-domain
  integration audit; produces sequenced, safe, verifiable
  implementation arcs that ship code.
- **Why it exists.** Research produced findings faster than
  implementation can ship them. Without governance the risk is
  either (a) "start coding everything" chaos, or (b) research
  backlog rots because no one knows how to admit findings into a
  build queue.
- **Its relationship to Research OS.** IOS is downstream. Research
  OS discovers truth; IOS ships fixes for the disconnects truth
  revealed. IOS invokes §8.4 IMPLEMENTATION contract for
  individual PRs — IOS itself is a §8.10 META-PROCESS artifact.
- **What IOS is NOT.** IOS is not the ADR corpus (§8.3). IOS is
  not a rewrite of the Research OS. IOS does not decide what
  research is worth doing. IOS does not remove Chris from the
  ratification loop.
- **The core loop.** `xx99 summary + cross_domain audit →
  intake → prioritize → open implementation arc → design ADR →
  pre-flight → build PRs → verify → close → feed back into docs +
  audit refresh + implementation debt register`.
- **The hardest problem IOS solves.** Turning
  "STRONG/WEAK/MISSING/OVERCOUPLED + CX-P1…CX-P8" into a **globally
  ranked, Chris-sized, safety-gated queue** — without collapsing
  into a giant theoretical scheduler.
- **Read Part 15 FIRST.** If you are a fresh Claude session and
  the request is anywhere near implementation, `docs/`, PR
  work, or arc-state introspection, execute the Part 15
  Startup Protocol before you plan, edit, or ratify anything.
  Every rule elsewhere in IOS assumes the startup has run.

---

# Table of contents

- Part 0 — Preface (what/where/why)
- Part 1 — Implementation philosophy
- Part 2 — Intake: from research to backlog
- Part 3 — Prioritization
- Part 4 — Implementation arc lifecycle
- Part 5 — Verification gates and risk discipline
- Part 6 — PR sizing rules
- Part 7 — Chris and Rigby roles
- Part 8 — Feedback loop and implementation debt
- Part 9 — Anti-chaos rules
- Part 10 — Short start commands
- Part 11 — First-queue construction procedure
- Part 12 — Consumer relationship to research outputs
- Part 13 — Open questions and Chris decision points
- Part 14 — Meta-learning section (§10 analog)
- Part 15 — Startup protocol (fresh-session bootstrap + drift detection)
- Appendix — Evidence base + companion anchors + Rigby SIGN record

---

# Part 0 — Preface

## 0.1 What "Implementation OS" means

IOS is a **process document**. Its `authority: process` frontmatter
puts it on the same governance tier as the Research OS and the
Domain Research Playbook. It is a set of rules for how Claude
Code, Rigby, and Chris move accepted research into shipped code.

IOS is **not** runtime code. It is not a scheduler, not a build
tool, not a task queue. It is the same shape as the Playbook: a
class-scoped specialization of the Research OS, but for the
downstream execution phase rather than the upstream discovery
phase.

## 0.2 Relationship to Research OS, Playbook, and §8.4

Research OS classifies incoming work into 11 classes (§5.1) and
routes each to a §8.N contract. Class 4 is IMPLEMENTATION, and its
contract lives at §8.4. That contract answers **"how do I ship
one PR safely"** — anti-duplication scan, factory usage, typed
exceptions, Procfile ↔ Makefile parity, vertical-slice completion.

IOS is one level up. IOS answers **"how do we ship a hundred PRs
across a domain over months, without regression, without stalling
Chris ratification bandwidth, and without letting the research
backlog rot"**. IOS invokes §8.4 for each individual PR; IOS also
invokes §8.2 (design-preparation) and §8.3 (design-decision/ADR)
whenever an implementation arc includes non-trivial design work.

Mirror table:

| Research | Implementation | Same relationship |
|----------|----------------|-------------------|
| RESEARCH_OPERATING_SYSTEM.md | IMPLEMENTATION_OPERATING_SYSTEM.md (this doc) | Both `authority: process`. Both class-scoped operating systems. Both invoke §8.N contracts. |
| DOMAIN_RESEARCH_PLAYBOOK.md | (this doc extends into Part 4 arc lifecycle) | Playbook operationalizes Research OS §8.1 RESEARCH; this doc operationalizes §8.4 IMPLEMENTATION at phase scale. |
| xx99 canonical summary | Implementation arc **canonical close doc** (mirror shape: §10 methodology, §11 arc change log, §12 provenance) | Both close-of-arc canonical anchors. |
| `cross_domain_integration_audit.md` | Same doc — it is the **bridge**. IOS reads it as input; every closed implementation arc refreshes §14 with an implementation-side delta. | Consumed by both phases. |

**Load order summary (see Part 15 for the authoritative protocol):**

1. CLAUDE.md + MEMORY.md (auto-injected)
2. `00-START-NEXT-SESSION.md`
3. RESEARCH_OPERATING_SYSTEM.md §0–§5 (bootstrap + classification)
4. **This doc** if the request classifies to IMPLEMENTATION or crosses IOS's phase boundary
5. **Part 15 Startup Protocol** — the full three-level sequence
   (Level A universal / Level B research-class / Level C IOS
   implementation bootstrap), source-of-truth hierarchy, phase +
   arc + stage + gate + next-action determination, drift checks,
   anti-context-drift rule
6. The relevant xx99 canonical summaries + cross-domain audit rows
   + active-arc scoping / design-prep / ADR docs (loaded per
   Part 15 Level C steps C.4–C.6)

## 0.3 Non-goals

- **IOS does not rewrite Research OS or Playbook.** If a rule in
  the Research OS conflicts with a rule here, Research OS wins.
  IOS additive-only.
- **IOS does not decide research priority.** The research
  backlog is Chris's to sequence via the Research OS "Start
  research group NNNN" ritual.
- **IOS does not remove Chris ratification.** Every arc-scoping,
  every posture decision, every ADR, every commit gate that
  Research OS puts in Chris's lane stays in Chris's lane.
- **IOS does not attempt to be a project-management tool.** No
  burndown charts, no velocity, no sprint calendar. The unit of
  planning is the implementation arc, ratified per arc.
- **IOS is not "the queue".** IOS is the *rules for constructing
  a queue*. The queue itself is built by the Part 11 procedure
  when Chris explicitly asks.
- **IOS is not a runtime service.** No Celery task, no daemon, no
  admin UI represents IOS. It is a doc, and the discipline it
  encodes.

## 0.4 One-sentence summary

> IOS turns the accumulated `xx99` canonical summaries and the
> cross-domain integration audit into safe, sequenced,
> Chris-ratified, Rigby-pressure-tested implementation arcs that
> ship code — without collapsing into either "start coding
> everything" chaos or "the backlog rots" stagnation.

---

# Part 1 — Implementation Philosophy

## 1.1 What is the purpose of the implementation phase?

The purpose of implementation is to **discharge accepted research
findings by changing runtime behavior of the platform** — code
edits, migrations, config changes, deletions — such that the
platform's actual state moves closer to the state the research
recommended.

Every implementation arc has one job: turn one or more findings
into a state change that is **verifiable**, **rollbackable**, and
**observed by Rigby post-merge**.

## 1.2 When is implementation finished?

Implementation is never "finished" in the sense that research is
finished. There is always more findings, and there is always
more drift. Implementation is finished **per arc**, when:

1. Every PR in the arc has merged.
2. Every finding admitted to the arc is either **discharged**
   (implemented + verified) or **retracted** (marked as wrong
   under implementation contact — see §8.4 retraction path).
3. Post-merge Rigby verification has run for every PR touching a
   PA-adjacent, workspace-adjacent, or user-visible surface.
4. Docs cascade + `cross_domain_integration_audit.md §14` refresh
   have run.
5. The arc's canonical close doc exists with §10 methodology
   section and §12 provenance appendix.
6. `OPEN_ARCS.md` has been updated: arc moved from `Currently in
   progress` to `Closed`.

## 1.3 What implementation produces

Per implementation arc:

- **Runtime PRs** (unit of change).
- **Optional ADRs** (`docs/adr/` — see §2.5) when the arc
  ratifies a design-preparation recommendation.
- **A canonical close doc** at `docs/research/implementation/<slug>/NN99_<slug>_canonical_close.md` (mirroring xx99).
- **A cross-domain audit §14 refresh entry** for the arc.
- **Handoff document(s)** per session (existing convention).
- **Implementation debt register updates** if any finding was
  retracted, deferred, or partially discharged.

## 1.4 The anti-pattern: "start coding everything"

The failure mode IOS most exists to prevent is this: once
research finishes, a Claude Code session opens with a backlog of
120–240 findings and "starts fixing things." Symptoms include:

- Multi-domain PRs that touch unrelated surfaces.
- Findings addressed in a different order than Chris would have
  chosen if asked.
- Rigby SIGN skipped because "we're just shipping now."
- Prod migrations without rollback plans.
- No provenance chain from PR back to the xx99 finding it
  discharges.
- Research backlog burns down but Chris loses visibility into
  what got shipped and what was silently dropped.

IOS treats this pattern the same way Research OS treats
"research-for-its-own-sake" (§1.5 there): a category error to
be structurally prevented, not merely apologized for after the
fact.

## 1.5 Implementation philosophy in one paragraph

The platform's job is to make Chris money and preserve his
attention. Implementation is not intrinsically valuable; it is
valuable only insofar as it moves the platform closer to a state
where those two goals are more reliably met. Every implementation
arc must be defensibly connected to (a) a research finding that
identified a gap in that trajectory, (b) a Chris-ratified
decision to close that gap, and (c) a verifiable runtime change
that actually closes it. If any of the three links is missing,
the arc is not implementation — it is churn, and it should not
run.

---

# Part 2 — Intake: from research to backlog

## 2.1 Sources of intake

IOS admits findings from four sources, in decreasing order of
authority:

1. **xx99 canonical summary anchor-updates (§7 of each xx99).**
   These are the anchor changes the research explicitly asked
   downstream owners to make. Highest authority — they are the
   ratified output of a closed research arc.
2. **cross_domain_integration_audit.md §2 (STRONG/WEAK/MISSING/
   OVERCOUPLED) and §14 refresh log deltas.** These are the
   disconnect map. Any WEAK, MISSING, or OVERCOUPLED classification
   is an implementation candidate.
3. **CX-P1 through CX-Pn cross-cutting pattern crystallizations.**
   These describe patterns that recur across multiple research
   arcs. Discharging a CX-P pattern may require a **cross-arc
   implementation arc** (multi-domain scope, longer arc).
4. **xx99 §6 unresolved unknowns + §8 follow-on research queue.**
   Not directly implementation — but IOS reads them to flag
   findings whose implementation is blocked on further research.
   Those findings enter the backlog with status `BLOCKED_ON_RESEARCH`.

IOS does **not** admit findings from:

- Ad-hoc bug reports (route to §8.5 BUG INVESTIGATION).
- Feature ideas without research provenance (route to Research
  OS for scoping first — no "shortcut to implementation" path).
- MEMORY rules alone (MEMORY rules are behavioral guidance; if a
  MEMORY rule reveals a runtime gap, the gap goes through §8.5
  → §8.6 or through a new research arc, not directly to IOS
  intake).

## 2.2 The intake item schema

Every intake item is a row in an implementation backlog register
(location: `docs/research/implementation/BACKLOG.md`, proposed —
see §13 D2). Each row has the following fields:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `intake_id` | string | Yes | Stable ID per one of five schemes (codified at v1.1): `IB-<arc>-<seq>` (single sending-arc origin, e.g., `IB-2299-014`); `IB-Q<queue>-<seq>` (queue-construction rows without a single arc provenance — first queue = `Q1`, subsequent full reconstructions = `Q2`, etc.; e.g., `IB-Q1-BOOT-01`); `IB-CDA-<seq>` (cross_domain_integration_audit §2 STRONG/WEAK/MISSING/OVERCOUPLED rows, e.g., `IB-CDA-014`); `IB-CDA14-<seq>` (cross_domain_integration_audit §14 refresh deltas, e.g., `IB-CDA14-005`); `IB-CXP<n>-<seq>` (CX-P<n> pattern-derived, e.g., `IB-CXP3-01`). Prefixes distinguish provenance for cross-source dedup + backlog grep. |
| `source_ref` | string | Yes | Citation: `<xx99 doc>:§N` or `cross_domain_integration_audit.md:§14.N` or `<CX-P>` |
| `source_type` | enum | Yes | `xx99_anchor_update` \| `xx99_recommendation` \| `cross_domain_MISSING` \| `cross_domain_WEAK` \| `cross_domain_OVERCOUPLED` \| `cx_pattern` \| `t4_cross_arc_delegate` |
| `work_type_tier` | enum | Yes | `T0` \| `T1` \| `T2` \| `T3` \| `T4` \| `T5` — per §3.1 |
| `design_state` | enum | Yes | `NONE` \| `SPEC_COMPLETE` (CX-P10 — spec IS the ADR, per §3.1.b) \| `POSTURE_PENDING` (CX-P4 — Chris ADR must resolve first) \| `RATIFIED_ADR` |
| `spec_ref` | string | Conditional | Required when `design_state: SPEC_COMPLETE`. `file:line` cite of the Chris-ratified spec (typically an xx99 §N or an ADR section). |
| `adr_ref` | string | Conditional | Required when `design_state: RATIFIED_ADR`. Format: `ADR-NNNN` per §2.5. |
| `verification_method` | string | Yes | What Rigby will exercise post-merge. Format: PA tool call + expected output shape (e.g., `deliverable_tool.list workspace_id=X status=completed → count > 0`). Named at Stage 3 pre-flight; consumed at Stage 5 verify. |
| `owner` | string | Yes | Claude session-slug (`claude-<domain>-arc`) or `chris` or `rigby`. Who is responsible for progressing the item. |
| `delegate_owner` | string | Conditional | Required when `source_type: t4_cross_arc_delegate`. The receiving arc's xx99 canonical summary author. Blank until receiving arc opens. |
| `title` | short string | Yes | Human-readable, imperative form (e.g., "Wire pa consumer to workspace lifecycle events") |
| `affected_domains` | list of strings | Yes | Domain slugs from research library (e.g., `[pa, auth]`) |
| `affected_surfaces` | list of strings | Yes | Concrete surfaces: file paths, models, tools, tasks, routes |
| `blast_radius` | enum | Yes | `LOCAL` (single file/handler) \| `SUBSYSTEM` (single topic) \| `CROSS_DOMAIN` (multi-topic) \| `PLATFORM` (global) |
| `risk_class` | enum | Yes | `SAFE_AUTONOMOUS` \| `NEEDS_CHRIS_PRE_RATIFICATION` \| `NEEDS_RIGBY_SIGN_PLUS_CHRIS` \| `NEEDS_ADR` |
| `expected_ship_size` | enum | Yes | `S` (≤200 LOC, ≤3 files) \| `M` (≤600 LOC, ≤8 files) \| `L` (≤1500 LOC, ≤20 files) \| `XL` (over) — see Part 6 |
| `dependencies` | list of `intake_id` | No | Other backlog items that must ship first |
| `blocks` | list of `intake_id` | No | Backlog items that cannot start until this ships |
| `status` | enum | Yes | `INTAKE` \| `TRIAGED` \| `QUEUED` \| `IN_ARC` \| `SHIPPED` \| `RETRACTED` \| `BLOCKED_ON_RESEARCH` \| `DEFERRED` |
| `chris_gate` | enum | Yes | `RATIFIED` \| `PENDING` \| `NOT_REQUIRED` |
| `arc_ref` | string | No | Populated when item enters an arc: `<arc-slug>-<seq>` |
| `pr_refs` | list of URLs | No | Populated after PRs land |
| `rollback_note` | string | No | Populated at arc `pre-flight`; rollback procedure |
| `retraction_reason` | string | No | Populated only if `status: RETRACTED`; free-text why the finding did not survive contact with implementation |
| `notes` | string | No | Free-text |

The schema is deliberately minimal. It exists so that any Claude
session can grep the backlog by `status`, `affected_domain`,
`risk_class`, or `blast_radius` and answer "what's shippable
next?" without a human synthesizing.

**BACKLOG surface discipline for `arc_ref` and `pr_refs`
(v1.4).** The §2.2 schema treats `arc_ref` and `pr_refs` as
first-class fields, but the `BACKLOG.md` table shape today
collapses them into free-text `affected_surfaces` / `notes`
cells (10-column markdown tables cannot expose every field as
its own column without hurting grep-friendliness). To keep
§15.6 rule 10 (PR-state drift verification) mechanically
runnable, use one of the following disciplines:

- **Discipline A (preferred, adopt as tables migrate).** Expose
  `arc_ref` and `pr_refs` as their own table columns in
  `BACKLOG.md`. Rule 10 greps the column directly.
- **Discipline B (transitional / until tables migrate).**
  Embed the fields inline in the row's `affected_surfaces` or
  `notes` cell using the exact literal syntax:
  - `arc_ref: I-NNNN` (one arc per row; if the intake spans
    multiple arcs, list them comma-separated:
    `arc_ref: I-NNNN, I-MMMM`)
  - `pr_refs: #NNNN, #MMMM` (GitHub PR numbers with the `#`
    prefix; comma-separated; may include closed PRs — status
    is queried via `gh pr view` per §15.6 rule 10).
  - Additional related-ADR reference: `adr_ref: ADR-NNNN`.

The inline syntax is chosen so `grep -oE '(arc_ref|pr_refs|
adr_ref): [^|]*' BACKLOG.md` produces a mechanically parseable
result even when the fields live inside cell prose. Discipline
B is permitted indefinitely; Discipline A is the aspirational
target for the next BACKLOG structural refactor arc.

**Fresh Claude sessions MUST prefer Discipline A when present
and fall back to Discipline B grep only if the row lacks
dedicated columns.** Codified after v1.4 fresh-session Stage 2
simulation surfaced that §15.6 rule 10's `pr_refs` sweep could
not run against Discipline B rows without an explicit syntax.

## 2.3 Intake triggers

An intake item is **created** by one of:

- **Post-arc-close reflex.** When any research arc closes (xx99
  committed), the closing Claude iterates the xx99 §7 anchor-updates
  and §6 unresolved unknowns and drafts one intake row per
  discharge-worthy item. Chris ratifies at the same session close
  ("agree all" ratification is the typical shape).
- **cross_domain audit refresh reflex.** When
  `cross_domain_integration_audit.md §14` gets a new refresh row,
  the delta's MISSING and WEAK entries generate intake rows.
- **Explicit Chris directive.** *"Open intake for the RAG
  vectorstore path."* Chris can inject intake outside a research
  cycle.
- **CX-P codification.** When a CX-P pattern reaches the two-trigger
  codification threshold, one intake row per surface where the
  pattern manifests, tagged `source_type: cx_pattern`.

An intake item is **not** created for:

- Findings the research doc marked "research-only" or "not for
  implementation" (see Playbook §3 phase discipline).
- Findings whose evidence is UNKNOWN — those loop back to research.
- Findings that the cross_domain audit marks STRONG (no fix needed).

## 2.4 Intake rejections

Some findings look implementable but should be rejected at intake:

| Reject condition | Route to |
|------------------|----------|
| Underlying research produced UNKNOWN evidence | Research follow-on arc |
| Finding is a design decision (options exist, no recommendation) | §8.2 DESIGN-PREPARATION |
| Finding is a Chris-scope call ("should we support X at all?") | Chris directly, not IOS |
| Finding conflicts with a ratified ADR | ADR revision, not implementation |
| Finding is a MEMORY rule violation with no root-cause identified | §8.5 BUG INVESTIGATION |
| Finding blast-radius = PLATFORM and no design-preparation doc exists | §8.2 first, then re-intake |
| **Already shipped or superseded** — detected via `git log` search for the finding's `source_ref` or an existing `pr_refs` entry in `BACKLOG.md` | Backlog dedup: flip existing intake to `SHIPPED`; do not create a new row |
| **Cannot name `affected_surfaces` concretely** — no file paths / models / tools listed | Route back to research (evidence too thin) OR §8.5 BUG INVESTIGATION (if a specific symptom exists) |
| **Multi-domain finding with no cross_domain_integration_audit row** — the disconnect is claimed but not mapped | Route to cross_domain audit refresh first; re-intake after audit row lands |
| **Cascade-housekeeping anchor-update** — `PLATFORM_INVENTORY.md` refresh, `ARCHITECTURE_INDEX.md` v-bump, `docs/topics/*.md` refresh, `docs/INDEX.md` regeneration, `build_docs_provenance` output. Codified at v1.1 execution refinement. | Discharged by the 4-step docs cascade at every arc close (MEMORY rule `feedback_docs_cascade_at_every_close` + Wave 1 `build-docs-cascade.yml` per §D11). Do NOT create implementation intake — cascade is arc-orthogonal housekeeping, not a discharge-worthy fix. Substantive §7 anchor updates that are NOT covered by the cascade (e.g., new topic-doc creation for a new subsystem, structural inventory refactor) still admit as intake. |

## 2.5 The ADR corpus operationalization

Research OS §8.3 says: *"No formal ADR corpus exists. This is a
P1 gap called out in §17."* IOS cannot function without a place
to record design-decision ratifications. Therefore IOS **installs
the ADR corpus** as a first-class dependency:

- **Location.** `docs/adr/` — one file per ADR.
- **Naming.** `ADR-NNNN-<slug>.md`, numbered by ratification
  order (independent from session/arc numbering).
- **Contents.** Context, decision, consequences, alternatives
  considered, reversibility, status (`proposed` / `accepted` /
  `superseded`), source finding cite (`intake_id`).
- **Ratification.** Chris "ratified" statement in the ADR file
  itself (per §8.3 completion criteria).
- **Coupling to intake.** Every intake row with `risk_class:
  NEEDS_ADR` gets an `adr_ref` field populated when the ADR
  ratifies (points to `ADR-NNNN`). No PR ships against a
  `NEEDS_ADR` finding until the ADR ratifies.

If Chris rejects installing an ADR corpus, IOS collapses ADR
requirements onto "Chris ratifies in the arc parent-scoping doc's
`§Decisions ratified` section" — the current de-facto path. Doing
so preserves compatibility with today's habits but keeps §8.3 as
a P1 gap indefinitely. **Recommendation:** install `docs/adr/`.
Chris-gated in §13 D3.

---

# Part 3 — Prioritization

## 3.1 The T0–T5 work-type-plus-priority tier system

Every closed xx99 canonical summary from S1399 through S2699 uses
a common tier system to structure the follow-on work queue. IOS
**adopts this tier system unchanged** — it is already the language
Chris and Rigby recognize. Each intake item is classified into
one of six tiers:

| Tier | Work type | Priority signal | Chris ratification band |
|------|-----------|-----------------|-------------------------|
| **T0 / Gate** | Chris-gated meta-ADR bundle or blocking prerequisite that must resolve before any downstream T1 work opens | Highest — literally blocks | Chris ratifies via "agree all" on the T0 bundle before any dependent PR opens |
| **T1 CRITICAL/HIGH** | Post-arc architecture decision records (ADRs) unblocking runtime work | High — ranked by architectural uncertainty × risk × flow impact | ADR ratification per §8.3 + `NEEDS_ADR` intake path |
| **T2 MEDIUM** | Design-preparation follow-ons and posture-tied design documents | Medium — dependencies on T0/T1 resolution | Chris ratifies design-preparation recommendation |
| **T3 LOW-MEDIUM** | Bounded operational patches, small clarity fixes, non-blocking cleanup | Low — safe for `SAFE_AUTONOMOUS` or `NEEDS_CHRIS_PRE_RATIFICATION` paths | Standard PR gate, no ADR |
| **T4 Cross-arc delegate** | Explicitly delegated to a future arc's queue by the closing arc's §9 hand-off | Deferred | Receiving arc's xx99 canonical summary author owns pick-up |
| **T5 Optional / Low-priority** | Nice-to-have cleanup; documentation lineage; refinement | Deferred / never-scheduled | Ad-hoc contributor when capacity exists |

**Scoring the intake within a tier.** The tier defines the outer
priority band. Within a tier, IOS uses a six-dimension score to
order arc-open sequencing. Each rater must state *which* stated
Chris goal an Impact / Attention score serves — otherwise "impact"
becomes a proxy for the rater's own bias.

| Dimension | Question | 1 = low | 5 = high |
|-----------|----------|---------|----------|
| **Revenue impact** | If this ships, how much does it move the platform toward a revenue path? | No revenue link | Directly unblocks or preserves a revenue path |
| **Attention preservation** | Does shipping this reduce Chris's re-context / friction / session load? | No effect on Chris's attention | Removes a Chris-blocking friction or a repeated context re-explanation |
| **Urgency** | Does anything else break, drift, or accrue while this is unshipped? | Nothing depends on it | Blocks other arcs; drift accelerates; MEMORY rules already violated |
| **Confidence** | How well does the research evidence support the fix? | UNKNOWN / partial evidence / speculative (F1/F4-CANDIDATE, unqualified) | file:line evidence, cross-verified, Rigby SIGN-with-edits or better, owner-model-qualified consumer inventory complete |
| **Reversibility** | If shipped wrong, how easily rolled back? | Irreversible migration; data destructive; contract-breaking | Feature-flagged, config-only, or fully reversible in a follow-up PR |
| **Cost of delay** | Every session that ships something else instead, what does this arc pay in re-context / drift / debt? | Zero — can wait indefinitely | High — every session doubles the cost of picking it up |

Total score = sum of the six, ceiling of `30`. Within a tier, higher
score ships first. Scoring is **advisory**; Chris can override any
sequencing by explicit command. Rigby-usability improvements score
under **Attention preservation** (Rigby's usability *is* a Chris
attention multiplier).

## 3.1.b Distinct intake handling: Design-Complete + Runtime-Scaffolding

Cross-domain audit v4 identifies **CX-P10** as a distinct close
disposition: specification is Chris-ratified via multiple "agree
all" rounds; runtime binding is not yet wired. Confirmed in three
arcs (Authority S1999, Event S2099, RAG S2199).

**CX-P10 items DO NOT require a new ADR.** The spec IS the ADR. IOS
handles them via **hard schema criteria** (not free-text markers):

- Intake `source_type: xx99_recommendation`.
- **`design_state: SPEC_COMPLETE`** (required — enum value per §2.2).
- **`spec_ref` populated with `file:line`** citing the Chris-ratified
  spec (typically an xx99 §N or a design-preparation doc §N with an
  explicit "Chris agreed all" reference). Absent `spec_ref` → the
  item is not admissible as SPEC_COMPLETE; downgrade to normal
  `NEEDS_ADR` intake.
- `risk_class` is one tier lower than an unratified design would
  be — usually `NEEDS_CHRIS_PRE_RATIFICATION` rather than
  `NEEDS_ADR`.
- Implementation arc Stage 2 (Design-preparation + ADR) is SKIPPED
  for the item; Stage 3 pre-flight cites `spec_ref`.
- Only the runtime binding is authored; the spec is a **read-only
  reference**.

CX-P10 (`design_state: SPEC_COMPLETE`) is orthogonal to CX-P4
POSTURE-PENDING (`design_state: POSTURE_PENDING`) — spec state vs
decision state. The schema enum makes the distinction verifiable
rather than interpretive.

## 3.2 Chris ratification bands

Not every intake item requires Chris to look at it. The
`risk_class` field determines Chris's involvement:

| `risk_class` | What triggers it | Chris involvement |
|--------------|------------------|-------------------|
| `SAFE_AUTONOMOUS` | LOCAL blast radius, **reversibility ≥ 4**, high confidence, no user-visible change, **no migration**, **no destructive data change**, **no fleet-key surface change** | Claude opens PR under existing §8.4; Chris reviews at PR-merge time only |
| `NEEDS_CHRIS_PRE_RATIFICATION` | SUBSYSTEM blast radius, or reversibility ≤ 3, or any UI/UX change, **or any irreversible migration / destructive data change even if LOCAL** | Chris ratifies the intake **before** arc opens — usually via a PA chat "agree all" ratification card |
| `NEEDS_RIGBY_SIGN_PLUS_CHRIS` | CROSS_DOMAIN blast radius, or the fix depends on a design-preparation recommendation | Rigby SIGN first, then Chris ratifies, then arc opens |
| `NEEDS_ADR` | Design decision embedded in the fix (Option A vs B), or blast radius = PLATFORM | Design-preparation doc + ADR + Chris ratification of the ADR before arc opens |

**Hard rule (irreversibility trumps blast radius).** Any intake
whose PRs include an irreversible migration, destructive data
change, contract-breaking edit, or fleet-key surface deletion is
**never `SAFE_AUTONOMOUS`**, regardless of blast radius. Minimum
`risk_class: NEEDS_CHRIS_PRE_RATIFICATION`; escalates to
`NEEDS_ADR` if design content is embedded.

## 3.3 Cross-domain dependency scoring

Findings that fix a MISSING or WEAK connection between two domains
get a **priority bump of +2** on the total score (before tier
mapping) if:

- Both domains have closed xx99 canonical summaries (so both
  sides of the disconnect are well-understood), AND
- No other MISSING/WEAK connection to either domain is in a
  higher tier.

This encodes the principle: fix known disconnects when both ends
are stable, rather than fix disconnects to a domain whose
research is still in flight.

## 3.4 Re-prioritization triggers

The backlog is re-scored on any of:

- Cross-domain audit §14 refresh (post-arc-close).
- New research arc close.
- New MEMORY rule that changes confidence or reversibility for
  any pending intake item.
- Chris explicit re-score directive.
- A retracted finding (see §8.4) — the retraction reason may
  invalidate scoring for adjacent findings.

Re-scoring does NOT interrupt an active arc. It only affects
queue order for the next arc-open slot.

---

# Part 4 — Implementation arc lifecycle

## 4.1 The arc as unit of work

An **implementation arc** is a bounded, ratified sequence of PRs
that discharge a coherent set of intake items — typically 3–8
findings against a single domain or a single cross-cutting
pattern. The arc is IOS's unit of session-to-session planning,
mirroring the research arc from the Playbook.

## 4.2 Arc numbering

Implementation arc numbers use the same session-range convention
as research (Playbook §4), but with a distinct series to prevent
collision:

- **Research arcs.** `13xx`, `14xx`, `15xx` … (existing convention)
- **Implementation arcs.** `I-NNNN` prefix, starting at `I-0100`
  (proposed — see §13 D1). E.g., `I-0100_pa_workspace_contract_wire_up`,
  child sessions `I-0101 … I-0198`, canonical close `I-0199`.

Rationale: preserves the parent/children/close shape of the
Playbook without overloading the numeric session range that the
Research OS uses for arc classification. Chris can override this
choice in §13 D1 (e.g., merge into the same numeric space).

## 4.3 The six stages

Each implementation arc runs through six stages, mirroring the
research arc lifecycle from Playbook §2.

### 4.3.0 Stage-state vocabulary (v1.4)

The scoping doc's frontmatter `stage:` field names the current
Stage (1..6). The frontmatter `stage_state:` field names the
current sub-state within that Stage. Fresh Claude sessions grep
these two fields to determine "where the arc is right now"
without conversation context (per §15.8 cold-resume invariant).

The `stage_state:` enum, codified at v1.4 execution-refinement
patch after Arc I-0100 Stage 1 → Stage 2 transition surfaced
that ad-hoc frontmatter values could not distinguish
"exit-gate cleared" from "P0 prep in-flight" from "P0 prep
merged" from "Stage 2 opened":

| `stage_state` | Meaning | Applies to which stages |
|---------------|---------|-------------------------|
| **`exit-gate-cleared`** | The stage's exit checklist is complete but the next stage has not opened yet. Terminal state for the current stage. | Any of 1..6; typical for 1, 2, 3, 4, 5 |
| **`p0-prep-in-flight`** | A P0 prep PR (per Stage 1 v1.2 ADR corpus precondition Option (a) OR any future analogous bootstrap dependency) is open but not merged. Arc is in the transitional window between Stage 1 exit and Stage 2 open. | Between Stage 1 and Stage 2 only |
| **`p0-prep-merged`** | P0 prep PR merged; Stage 2 has not been formally opened yet (Chris directive or Option (a) auto-open per §4.3 Stage 2 Entry gate pending). | Between Stage 1 and Stage 2 only |
| **`active`** | Stage is open and doing work. PRs being drafted, SIGN cycles running, ratifications in-flight. | Any of 1..6 |
| **`awaiting-close`** | Stage 6 close doc is drafted + cascade run + audit refresh drafted; awaiting Chris "commit it". Terminal-of-arc precondition. | Stage 6 only |

**Frontmatter update discipline.** `stage:` and `stage_state:`
MUST flip in the same commit that produces the state change:

- **Stage N exit cleared → Stage N+1 pending.** `stage: N`
  unchanged; `stage_state:` flips to `exit-gate-cleared`.
- **P0 prep PR opens (Option (a) arcs).** `stage: 1` unchanged;
  `stage_state:` flips `exit-gate-cleared → p0-prep-in-flight`.
  The commit that opens the P0 prep PR includes the frontmatter
  flip.
- **P0 prep PR merges.** `stage: 1` unchanged; `stage_state:`
  flips `p0-prep-in-flight → p0-prep-merged`. Housekeeping
  flip; may batch with the next arc-touching PR.
- **Stage N+1 opens.** `stage:` flips `N → N+1`; `stage_state:`
  flips to `active`. The commit that OPENS Stage N+1 (the first
  Stage N+1 PR, or the Chris-directive-recording PR) carries
  the frontmatter flip.
- **Stage 6 close draft complete.** `stage: 6`; `stage_state:`
  flips `active → awaiting-close`. The commit that produces the
  Stage 6 close doc carries the flip.
- **Arc close.** Arc leaves `OPEN_ARCS.md#In-progress` and
  moves to `#Closed`. Scoping doc frontmatter `status:` may
  flip `active → superseded` per Playbook convention if the arc
  produced a canonical close doc that supersedes the scoping
  doc; otherwise `status: active` remains and the arc is
  "closed with the scoping doc still live as reference."

### Stage 1 — Scoping

**What.** Draft `docs/research/implementation/<slug>/I-NNNN_<slug>_scoping.md`
using the Playbook §11.1 **9-section** parent-scoping template
(§1 Why + §2 Existing inventory + §3 Candidate subdomain taxonomy
+ §4 Parent-vs-single recommendation + §5 Child mission sequence
+ §6 Parked candidate issues + §7 Anti-scope + §8 Decisions
recorded + §9 Next step + Appendix — Frontmatter provenance),
**modified for implementation** by these substitutions:

- §3 "Candidate subdomain taxonomy" → "Intake items admitted to
  this arc" (list of `intake_id`s + `title`s + `source_ref`s).
- §5 "Child mission sequence" → "Planned PR sequence" (one
  child per PR or bundle of PRs, with size + dependency graph).
- §7 "Anti-scope" → "Anti-scope + reversibility guardrails"
  (what this arc does NOT touch, plus how each planned PR gets
  reverted if it fails post-merge).
- §9 "Next step" → same, but with an **ADR checkpoint** if any
  admitted finding has `risk_class: NEEDS_ADR`.
- **§10 (added by IOS — NOT in Playbook §11.1) "Stage checklist
  snapshot"** — a mechanically-enumerated list of every exit-gate
  item for every planned stage, one line each, that a future
  Claude session can grep to determine current stage without
  interpretation. Without the snapshot, stage inference is
  interpretive and the arc is not cold-resumable per §15.8.
  Promoted from exit-gate prose to explicit substitution at IOS
  v1.2 execution-refinement patch (2026-07-06) after Arc I-0100
  Stage 1 first execution surfaced that a fresh Claude session
  reading the substitution list can miss a section mandated only
  in the exit-gate paragraph.

**Who.** Claude drafts; Rigby SIGN on Q1–Q4 as in research arcs;
Chris "agree all" or explicit ratification.

**Exit gate.** Chris "commit it"; parent doc status flips
`draft → active`; arc-pin minted. Scoping doc MUST include the
§10 Stage checklist snapshot (per substitution list above); if
missing, Stage 1 does not close.

**Cascade co-location (v1.3 §12.5 discipline).** The arc-open
PR that carries this Stage 1 scoping doc MUST run the full
5-step cascade locally BEFORE opening the PR, commit the
`docs/INDEX.md` + `docs/_provenance.json` diffs alongside the
scoping doc, and include the §12.5.d PR-body cascade evidence
block. A follow-up cascade PR is NOT permitted for arc-open —
the scoping doc must be RAG-visible for Rigby SIGN Cycle 1 to
work off corpus rather than diff hunk. Codified after the
arc-open PR / separate-cascade-PR pattern recurred 3× same-day
2026-07-06 (see verifier_loop v1.3).

**ADR corpus precondition (v1.2 execution refinement).** If any
admitted intake row has `risk_class: NEEDS_ADR`, Stage 1 close
additionally requires verification that `docs/adr/` directory
exists on `main` OR a concrete plan to establish it. If absent
at Stage 1 close time, one of the following MUST be true:

- **Option (a) — Bundle prep.** Admit `IB-Q1-BOOT-01`
  (author `ADR-0001-establish-adr-corpus.md` per IOS §D3
  Appendix C bootstrap) as an in-arc P0 prep PR that ships
  BEFORE Stage 2 opens. The prep PR creates `docs/adr/` and
  the recursive-bootstrap ADR; subsequent ADRs written in
  Stage 2 have a home.
- **Option (b) — Blocking gate.** Block Stage 1 close until
  `IB-Q1-BOOT-01` ships via a separate arc.

Both options are permitted; Claude drafts, Chris ratifies which
per arc. Missing this check produces the incoherent Stage 2
state of "ADR required but nowhere to put it" and stalls the arc
silently. Codified after Arc I-0100 Stage 1 first execution
surfaced that IB-Q1-BOOT-01 is a covert dependency of every
implementation arc whose intake includes any `NEEDS_ADR` row —
which is currently EVERY T0 arc and most T1 arcs — but the
dependency was not called out in the Stage 1 exit contract.

### Stage 2 — Design-preparation + ADR (if required)

**Entry gate (v1.4).** Stage 2 opens ONLY when BOTH of the
following are true:

1. **ADR corpus exists on `main`.** `docs/adr/` directory is
   committed to `main` AND `ADR-0001-establish-adr-corpus.md`
   is `status: accepted` on `main`. Verified via `git ls-tree
   main -- docs/adr/` and frontmatter grep.
2. **Opening event.** ONE of:
   - **Chris explicit directive.** `Open implementation arc
     I-NNNN Stage 2` OR equivalent session-scoped short command.
   - **Option (a) P0 prep PR merge (auto-open).** If the arc
     selected Option (a) at Stage 1 exit (bundle IB-Q1-BOOT-01
     as in-arc P0 prep PR — see the ADR corpus precondition
     block below), the P0 prep PR merge IS the Stage 2 opening
     event. No separate Chris directive required — the Chris
     ratification of Option (a) at Stage 1 exit carries forward
     to Stage 2 open. Claude records the auto-open in the next
     commit that advances the arc.

**Frontmatter flip discipline (per §4.3.0).** The commit that
records Stage 2 opening (Chris directive OR the first Stage 2
PR OR a housekeeping commit acknowledging Option (a) auto-open)
MUST flip the scoping doc frontmatter:

- `stage:` `1 → 2`
- `stage_state:` `p0-prep-merged → active` (Option (a) arcs) OR
  `exit-gate-cleared → active` (Chris-directive arcs that
  skipped the P0 prep path).

The `stage_state:` values enumerated in §4.3.0 make the
transition mechanically greppable by fresh Claude sessions.

**What.** For every intake item with `risk_class: NEEDS_ADR` or
`NEEDS_RIGBY_SIGN_PLUS_CHRIS`, produce a design-preparation doc
per §8.2 and (if `NEEDS_ADR`) a subsequent ADR per §8.3.

**Design-prep equivalence (v1.4).** If the arc scoping doc §9
(Next step + ADR checkpoint) pre-scopes an ADR with ALL of the
following:

- **Decision question** — the specific choice the ADR resolves
  ("shall we adopt X, Y, or Z for shape A?").
- **Options enumerated** — at least the top-N candidate options
  the ADR will consider, with the shape of each.
- **Constraints named** — hard requirements the ADR must respect
  (retention windows, compatibility promises, blast radius
  ceilings, ratified-upstream-decision inputs).
- **Consequences per option** — what each option enables and
  obligates, at least sketched.
- **Verification implications** — how ratifying this ADR affects
  the Stage 3 pre-flight verification-method interface for
  downstream intake rows.

… then that scoping doc §9 section IS the design-preparation
artifact for that ADR — no separate `I-NNNN_<slug>_design_prep_
<topic>.md` file is required. The ADR PR body cites the scoping
doc §9 subsection as its design-prep source (e.g., "design-prep:
`I-NNNN_scoping.md` §9.1 ADR-B pre-scoping"). Codified after
Arc I-0100 scoping doc §9.1 pre-scoped ADR-B/A/C without
separate design-prep files, matching Rigby SIGN Cycle 1 F5 fold
which specified the PA↔LLMCallEvent correlation contract inside
scoping §9 rather than a follow-on design-prep doc.

If the scoping doc §9 is INSUFFICIENT (e.g., only names the ADR
target without option enumeration OR omits constraints OR does
not name verification implications), a standalone design-prep
doc IS required at `docs/research/implementation/<slug>/
I-NNNN_<slug>_design_prep_<topic>.md` with `authority: design-
preparation`. Claude decides which shape at Stage 2 entry;
Rigby SIGN cycle on the ADR will pressure-test the design-prep
adequacy either way.

**Location.** Design-prep docs (when present) live at
`docs/research/implementation/<slug>/I-NNNN_<slug>_design_prep_<topic>.md`
with `authority: design-preparation`. ADRs live at
`docs/adr/ADR-MMMM-<slug>.md` with `authority: design-decision`.

**Exit gate.** Every `NEEDS_ADR` intake item has a ratified ADR
before Stage 3 begins.

**Cascade co-location per ADR PR (v1.3 §12.5 discipline).** Each
ADR PR (one ADR per PR default) MUST run the full 5-step cascade
locally BEFORE opening the PR, co-commit `docs/INDEX.md` +
`docs/_provenance.json`, and include the §12.5.d PR-body cascade
evidence block. Design-preparation docs (`I-NNNN_<slug>_design_
prep_<topic>.md`) that ship in the same PR as their ADR are
covered by that PR's cascade run; standalone design-prep PRs
without an ADR follow the same discipline (design-prep is
RAG-critical because Chris ratifies design decisions against
corpus context). If multiple ADRs bundle into one PR (permitted
per §6.3), one cascade run covers the bundle.

### Stage 3 — Pre-flight

**What.** For each PR planned in Stage 1:

1. **Rollback plan.** Concrete, executable rollback procedure
   documented in the scoping doc's Stage 1 §7. Not "revert the
   commit" — that's the last-resort. E.g., "toggle feature flag
   `INTAKE_IB_2299_014_ENABLED = False`" or "run migration
   `NNNN_rollback` which restores column X."
2. **Regression test named.** Test path + test name that will
   demonstrate the fix works.
3. **Verification method named.** What Rigby will exercise post-merge
   (usually a specific PA tool call + expected output shape).
4. **Blast radius double-check.** Grep for callers of any deleted
   / renamed symbols. Cross-repo sweep if implementation touches
   fleet-key surfaces (per MEMORY rule
   `feedback_fleet_caller_verification_before_celery_deletes`).
5. **D48 stability-probe gate.** Warmup-ping every arc-close
   checklist item planned for Stage 6 close. Per Content S1606
   F.vi ten-consecutive-fully-clean-arms sub-pattern (codification
   candidate for Playbook v3 §15). If any warmup-ping fails, do
   not open Stage 4; resolve the failing check first.
6. **Sub-agent verifier-loop scope.** If Stage 4 will use
   Explore / Plan / general-purpose sub-agents for research
   support, decide in Stage 3 which of their claims will be
   spot-checked at the parent level before routing to Rigby.
   Skipping this step reliably produces overreach that would
   otherwise ship (Memory S1399 §10.3 #1 pattern).

**Exit gate.** Pre-flight checklist committed to the scoping doc.
No PR opens without pre-flight.

### Stage 4 — Build

**What.** PRs open under §8.4 IMPLEMENTATION contract. Each PR:

- Cites its `intake_id` in the PR body.
- Cites the source xx99 finding by file:line.
- Includes the regression test named in Stage 3.
- Passes the §8.4 verification (factories, typed exceptions,
  Procfile↔Makefile parity, etc.).
- Respects the PR sizing rules in Part 6.

**Who.** Claude ships PRs. Rigby does not touch runtime code
(no repo write). Chris approves each merge unless the intake was
`SAFE_AUTONOMOUS` **and** Chris has pre-authorized auto-merge for
this arc (rare).

**Exit gate.** Every planned PR merged; every regression test
green.

### Stage 5 — Verify

**What.** For every merged PR:

1. **Rigby exercises the new surface.** Per the Stage 3
   verification method. Rigby's tool-output block is the
   ground truth — Claude does not trust her summary.
2. **Claude verifies independently** via Django ORM /
   `git log` / file Read.
3. **Local + prod parity check** if the fix affects fleet-key
   or prod-only state (per MEMORY rule
   `feedback_fleet_caller_verification_before_celery_deletes`).

**Exit gate.** Every PR verified; any regressions caught here
route back to Stage 3 with a fix plan.

### Stage 6 — Close

**What.**

1. **Canonical close doc.** `I-NNNN99_<slug>_implementation_close.md`
   authored using a template that mirrors Playbook §11.3 xx99:
   - §1 Executive summary
   - §2 What this arc shipped
   - §3 Anchor-updates to make (docs to update)
   - §4 Cross-cutting patterns observed
   - §5 Findings that did not ship (retracted, deferred, blocked)
   - §6 Implementation debt accrued
   - §7 Cross-domain audit §14 delta authored
   - §8 What this arc taught us about how to do implementation
     (mirrors xx99 §10)
   - §9 Provenance appendix
2. **cross_domain_integration_audit §14 refresh** — mandatory
   append with the implementation-side delta.
3. **Docs cascade** (4-step: `build_docs_index` +
   `build_rag_corpus` + `sync_docs_index_to_documents` +
   `sync_docs_index_to_documents --embed`) plus
   `build_docs_provenance`. Per §12.5 v1.3 discipline + MEMORY
   rule `feedback_cascade_pr_must_include_embed_step`, cascade
   runs LOCALLY BEFORE the close PR opens; `docs/INDEX.md` +
   `docs/_provenance.json` diffs co-commit alongside the close
   doc + audit refresh; PR body includes the §12.5.d cascade
   evidence block with chunk count for step 4. A follow-up
   cascade PR is NOT permitted for arc-close — the close doc is
   RAG-critical for Rigby SIGN on the close doc and for future
   research/intake cross-referencing the just-shipped arc.
4. **OPEN_ARCS.md update** — arc moved from `Currently in
   progress` to `Closed`.
5. **Backlog cleanup** — every discharged intake row flips to
   `status: SHIPPED` with `arc_ref` and `pr_refs` populated.
6. **Implementation debt entry** if any finding was retracted
   or deferred.
7. **Rigby SIGN on the close doc.**

**Exit gate.** All six items complete; Chris "commit it".

## 4.4 No-parallel-arcs rule (implementation extension)

MEMORY rule `feedback_no_parallel_research_arcs` extends to
implementation. Two implementation arcs must not run in parallel
on the same repo checkout when they share surface area — same
files, same models, same migrations, same PA tools.

**Distinct-surface parallelism is permitted** (e.g., a PA arc and
a spider arc running simultaneously). But shared-state files
(`OPEN_ARCS.md`, `ARCHITECTURE_INDEX.md`, `cross_domain_
integration_audit.md`, `BACKLOG.md`) are always serialized:
whichever arc opens first holds the pen.

**Research arc / implementation arc parallelism** is permitted
only if the implementation arc is on a domain whose research is
already closed (xx99 committed). Never open an implementation
arc against a domain whose research is still in flight.

## 4.5 Arc graduation criteria

An arc **cannot close** unless:

- Every intake item admitted at Stage 1 has status `SHIPPED`,
  `RETRACTED`, `DEFERRED`, or `BLOCKED_ON_RESEARCH`.
- Every retracted item has a `retraction_reason`.
- Every deferred item has a follow-up `intake_id` in the
  backlog with `status: TRIAGED` (not left as `INTAKE`).
- Post-merge Rigby verification completed for every PR.
- Docs cascade + audit §14 refresh landed.
- No unratified ADR from Stage 2 remains open.

An arc **can be stalled** (paused mid-flight) by:

- Chris directive.
- Discovery mid-arc that a finding needs new research (route to
  Research OS; mark intake `BLOCKED_ON_RESEARCH`; arc-close
  criteria adjusts).
- Rigby SIGN identifies a safety issue requiring re-design.

Stalled arcs are moved to `Stalled` in OPEN_ARCS.md, not closed.

---

# Part 5 — Verification gates and risk discipline

## 5.0 Term definitions (to make gate rules deterministic)

These terms recur across §5.1 gate rules. Two Claude sessions
should classify identically.

- **Consumer** (of a feature flag / config value / model field) —
  any of: (a) a runtime code branch reading the value, (b) a
  Celery task using it, (c) a management command using it, (d)
  a UI component reading it via API. Documentation mentions and
  test-only reads do NOT count. Zero-consumer values are dead
  weight (Sports F.F3 pattern) and disqualify the arc.
- **Owner-model-qualified consumer inventory** — a per-symbol
  (function / field / task / route) list of every direct caller
  and every stringified reference, produced by: (a) direct grep,
  (b) fleet-repo grep, (c) `docs/` grep, (d) last 5–10 handoffs
  grep, (e) `docs/AUDIT_FINDINGS.md` §18 cross-check for Celery
  tasks. Alternatively: verified `ops_tool.celery_task_history`
  30-day zero-fire + KNOWN_DEFERRED cross-check for tasks. Per
  MEMORY rule `feedback_verify_before_deleting_dead_code`. Until
  qualification lands, any "dead code" claim stays `F4-CANDIDATE`.
- **Fleet-key surfaces** — any of: `FleetServiceKey`,
  `FleetPAChatAuditRow`, `FleetArtifact` model rows; any Celery
  task in `td_handlers_gateway.ALLOWED_TASKS`; any code path
  reading `service_key` headers. Per MEMORY rule
  `feedback_fleet_caller_verification_before_celery_deletes`.
- **F4-CANDIDATE** — a claim about a symbol being dead / orphan /
  unreferenced that has NOT yet completed the owner-model-qualified
  consumer inventory. F4-CANDIDATE claims cannot back a deletion PR.

## 5.1 Pre-code gates (before writing a single line)

Every implementation arc, before Stage 4 opens, must pass:

1. **Anti-duplication scan.** Per §8.4 required-reads.
   `EMPLOYEE_OS_PRIMITIVES.md` §4 verified for any new
   model / handler / tool.
2. **Fleet-caller sweep.** Per MEMORY rule
   `feedback_fleet_caller_verification_before_celery_deletes`.
   3-axis sweep: repo grep + Rigby ops_tool.celery_task_history
   30d + ORM probe of FleetServiceKey / FleetPAChatAuditRow /
   FleetArtifact.
3. **Migration ordering check.** If any DB migration is planned,
   confirm the ordering does not break in-flight requests
   (blue/green safety).
4. **Rollback plan approved.** Every planned PR has a
   documented rollback in the scoping doc §7.
5. **Regression tests named.** Per Stage 3.
6. **F4-CANDIDATE dead-code discipline.** No code deletion is
   approved without owner-model-qualified consumer inventory.
   Keyword-grep alone is insufficient (Memory S1399 §10.3 #2 +
   #5). If the intake proposes deletion, the pre-flight checklist
   must include: (a) direct callers grep, (b) stringified refs
   grep, (c) fleet-repo sweep, (d) docs/handoff sweep, (e) explicit
   owner-model qualification. Until qualification lands, claim
   stays CANDIDATE and the PR does not open.
7. **Feature-flag consumer verification.** If the intake
   introduces or references a feature flag, verify ≥1 runtime
   consumer exists. Zero-consumer flags are `DECLARED-FEATURE-
   FLAG-GATES-NOTHING` (Sports F.F3 pattern) and disqualify the
   arc from opening.
8. **Beat-scheduled task registration.** If the intake proposes
   a Celery task claimed to run on schedule, verify:
   PeriodicTask row exists, `core/celery.py` beat entry exists,
   and `ops_tool.celery_task_history` shows non-zero events over
   30 days OR the task is documented as deferred in
   `docs/AUDIT_FINDINGS.md` §18. Zero-fire beat tasks are
   CRITICAL (Sports S1503 §14.1) — do not add another.
9. **Mock-data-in-production check.** Grep for `random.randint`
   / `random.uniform` / hardcoded demo generators in the paths
   the intake touches. If found in non-test, non-seed code path,
   flag as CRITICAL boundary violation (Sports S1505 F.E1 +
   S1506 F.F5). Fix the mock-data path in the same arc, not later.
10. **UNKNOWN honesty.** If any evidence in the intake's
    supporting research is marked UNKNOWN, the intake is
    `BLOCKED_ON_RESEARCH` — not "we'll figure it out during
    build." Route to research follow-on arc instead.

## 5.2 Pre-merge gates (before a PR lands)

Per PR, at review-time:

1. **Run the Research OS §8.4 verification checklist.** IOS does
   not restate its contents (prevents drift-by-paraphrase). §8.4
   is the authoritative per-PR contract.
2. **Vertical slice + last-mile UI.** Per MEMORY rules
   `feedback_vertical_slice` and `feedback_last_mile_ui`. If
   the PR is a user-facing feature, it must be visible + usable
   in the browser before merge.
3. **Test on real DB, not mocks** for QuerySet-heavy code. Per
   MEMORY rule `feedback_test_real_db_for_queryset_semantics`.
4. **Rigby SIGN** if the arc is `NEEDS_RIGBY_SIGN_PLUS_CHRIS`
   or `NEEDS_ADR`.
5. **PR body cites `intake_id` + xx99 file:line.**
6. **Pre-commit hooks pass.** No `--no-verify`.
7. **Silent-degrade emission rule.** Any try/except that catches
   an exception without re-raising MUST emit a degraded-status
   marker: (a) event row (e.g., DeliverableEvent, LLMCallEvent
   with degraded flag), (b) greppable log line, (c) metric
   increment. Per Content S1601 F2 pattern + CX-P8 auth
   silent-degrade two-trigger threshold. Consumers must be able
   to observe the degradation.
8. **Field-name validation on writes.** Every `.create(`,
   `.update(`, `.filter(**kwargs)` call using dynamic field names
   must be either (a) validated against the model's field set at
   arc scoping time, or (b) wrapped in a fail-loud guard. Prevents
   the Revenue S1406 F.F1 5-phantom-field-writer class of bugs.
9. **Verifier-loop pre-correction.** Every claim in the PR body
   ("this fixes X", "this closes finding Y", "no regressions in
   Z") gets an independent verification: ORM probe, `git log`
   cross-check, or file:line cite. Sub-agent claims (Explore /
   Plan / general-purpose) are especially subject to this rule.
10. **Cascade evidence block (v1.3).** If the PR touches any
    RAG-critical artifact type per §12.5.b (arc scoping docs,
    ADRs, close docs, IOS / RESEARCH OS / Playbook patches,
    RATIFICATION records, scope-changing BACKLOG / DEBT /
    OPEN_ARCS updates, or cross_domain_integration_audit §14
    appends), the PR MUST include the §12.5.d cascade evidence
    block AND co-commit the resulting `docs/INDEX.md` +
    `docs/_provenance.json` diffs from a locally-run 5-step
    cascade. Follow-up cascade PRs are permitted only for
    artifact types listed in §12.5.c OR under Chris-explicit
    deferral per §12.5.a.

## 5.3 Post-merge gates (before arc closes)

Per PR, within 24 hours of merge:

1. **Rigby exercises** the new surface via the Stage 3
   verification method.
2. **Claude verifies** independently by reading Rigby's
   `Tool Runs (verbose)` block and cross-checking via ORM / git
   log / file Read. Per MEMORY rule
   `feedback_claude_directs_rigby_then_verifies`.
3. **Prod parity** if the fix affects fleet-key surfaces.
4. **Handoff document updated.**

## 5.4 Migration + rollout + rollback discipline

### Migrations

- One migration per PR unless ordered atomically.
- Backward-compatible for one deploy cycle (blue/green safety).
- Roll-forward tested locally before merge.
- Roll-back script committed alongside the migration.

### Rollout patterns

Every intake item's arc scoping doc §7 declares one rollout pattern:

| Pattern | When to use | Rollback |
|---------|-------------|----------|
| **Straight ship** | LOCAL blast radius, invisible change, high confidence | Revert commit |
| **Feature flag** | SUBSYSTEM+ blast radius; any user-facing change | Toggle flag to `False` |
| **Dark launch** | Behavior change with runtime cost; want telemetry before user contact | Config: telemetry-only mode |
| **Canary** | PLATFORM blast radius; irreversible-if-wrong | Roll back canary cohort; revert commit |

### Rollback plan requirement

Every PR that touches:

- Migrations
- Prod configuration
- User-visible flows
- PA tool contracts
- Fleet-shared surfaces

… ships with a **documented, executable rollback**. Not a promise —
a command sequence or config toggle that has been dry-run before
merge.

### Regression test discipline

Per MEMORY rule `feedback_fail_loud_first_then_root_cause_then_
telemetry`, regressions get their own 3-PR arc: visibility →
root-cause fix → telemetry cleanup. Do NOT chain "fix + telemetry
adjustment" in a single PR when a masking pattern is in play.

---

# Part 6 — PR sizing rules

## 6.1 Line + file + surface caps

Per PR, the target ceilings:

| Size | LOC | Files | Distinct topics | Chris review effort |
|------|-----|-------|-----------------|---------------------|
| **S** | ≤200 | ≤3 | 1 | 5 min |
| **M** | ≤600 | ≤8 | 1 | 15 min |
| **L** | ≤1500 | ≤20 | ≤2 (with cross-cite) | 40 min |
| **XL** | over L | over L | any | ≥1 hour, requires pre-review |

**Ceiling is a target, not a hard block.** Cross the ceiling only
if the PR is genuinely atomic (splitting would leave prod in a
broken intermediate state). If crossing, note the reason in the
PR body and route to Rigby SIGN even if the arc did not otherwise
require it.

## 6.2 Vertical slice + last-mile UI requirement

Per MEMORY rules `feedback_vertical_slice` and
`feedback_last_mile_ui`, every user-facing feature ships as a
vertical slice: backend + API + frontend UI + E2E test + 60s demo.
No PR is "done" until Chris can see and use the feature in the
browser.

For non-user-facing changes (config, infra, dev-loop), vertical
slice does not apply; PR ships when tests green and Rigby
verified.

## 6.3 One-PR-per-finding vs bundled PRs

Default: **one PR per intake item.** Trace is cleaner, rollback is
per-finding, provenance chain is 1:1.

Bundling is permitted when:

- Findings share a file or refactor surface.
- Splitting would create in-review dependency chains.
- All bundled findings share `risk_class` and `chris_gate`.

Bundled PR body must list every `intake_id` bundled, each with
its own regression test.

## 6.4 Chris review bandwidth budget

Per session (rough estimate; Chris-tunable in §13 D5):

- **~3 M-sized PRs** OR
- **~1 L-sized PR + 1 M-sized PR** OR
- **~5 S-sized PRs**

Exceeding this budget in one arc = deferred PRs, not more Chris
attention. Better to split an arc than to over-batch a session.

---

# Part 7 — Chris and Rigby roles

## 7.1 Chris-gated decisions

Chris is the sole ratifier for:

- Arc scoping (Stage 1 exit).
- Every `NEEDS_CHRIS_PRE_RATIFICATION` or higher intake item.
- Every ADR (§8.3 requires Chris's explicit ratified statement).
- Every posture / architectural decision embedded in an
  implementation arc.
- Cross-domain contract changes.
- Any override of the priority rubric.
- Arc close (Stage 6 exit).

Chris is **not** required for:

- `SAFE_AUTONOMOUS` intake items (Chris reviews at PR-merge
  time only, same as any Chris-approved PR).
- Regression test authoring.
- Rollback plan authoring.
- Handoff writing.

## 7.2 Rigby SIGN routing per stage

| Stage | Rigby SIGN required? | Cadence |
|-------|---------------------|---------|
| 1 Scoping | Yes | Single-batch × 4-Q, matching S1300–S2400 pattern |
| 2 Design-prep + ADR | Yes | **One SIGN cycle per ADR** (v1.4). See implementation ADR SIGN cadence below. |
| 3 Pre-flight | **Conditional — see below** | Single-batch × 2-Q if triggered |
| 4 Build | No | Rigby has no repo-write surface |
| 5 Verify | Yes | Rigby exercises the surface; produces tool-output blocks. **Capped — see §9.4.** |
| 6 Close | Yes | Full SIGN on the canonical close doc |

**Implementation ADR SIGN cadence (v1.4).** Stage 2 SIGN
mechanics were previously under-specified (§7.2 pre-v1.4 only
said "per §8.2 / §8.3"). Codified after Arc I-0100 pre-ADR-0002
cold-session simulation surfaced that a fresh Claude session
would not know Q-count or pin discipline for ADR SIGN routing:

- **One Rigby SIGN cycle per ADR.** ADR-A, ADR-B, ADR-C each
  get their own dedicated SIGN cycle. Do NOT bundle multiple
  ADRs into one SIGN cycle — SIGN cross-contamination erodes
  fold-per-ADR traceability and violates the single-decision-
  per-cycle discipline.
- **Active arc SIGN pin — no rotation between ADRs.** ADRs
  within the same arc share the arc's SIGN pin (per §7.2
  isolation-pin discipline). Pin retirement is Stage 6 close
  ONLY, unless the arc stalls per §4.5. Fresh SIGN pin per
  ADR would fragment arc SIGN history and cost the arc-pin-
  durable-through-arc property.
- **Q-count sized to ADR decision complexity.**
  - **2-Q minimum.** ADRs with a single narrow decision (one
    option-shape to ratify, few constraints). Example: format-
    or naming-decision ADRs.
  - **4-Q typical.** ADRs with 2–3 decision axes OR
    correlation-contract semantics OR multi-option ratification.
    Example: Arc I-0100 ADR-B (PA write shape × correlation
    contract × keys × join path).
  - **6-Q max.** ADRs with 4+ decision axes OR posture bundles
    (spine-posture-plus-retention-constraints-plus-deprecation-
    plan). Example: Arc I-0100 ADR-C (D74 six-axis correlation-
    spine posture + retention as required decision input +
    deprecation plan sketch). Q-count above 6 → split the ADR
    into two independently-ratifiable ADRs; do not add a 7th Q.
- **Cadence style.** Match the S1300–S2699 established pattern:
  single-batch × N-Q per cycle. Streaming multi-batch SIGN is
  NOT the shape for ADRs (that pattern is Rigby SIGN-worker-
  instability recovery per MEMORY rule
  `feedback_rigby_sign_worker_instability_recovery`, not
  default cadence).
- **Cycle 2 requested only on BLOCKED verdict.** If Cycle 1
  returns SIGN-with-edits (no BLOCKED), fold and Chris-ratify;
  no Cycle 2 needed. If Cycle 1 returns BLOCKED on any Q, Cycle
  2 addresses only the BLOCKED items on the same pin.
- **ADR PR body cites the SIGN cycle.** Under a `## Rigby SIGN
  Cycle 1` section, the ADR PR body lists per-Q verdict +
  confidence + folds applied. Matches Stage 1 arc-open PR
  pattern from Arc I-0100 (#2945).

**SIGN vs ratification separation.** Rigby SIGN is a
pressure-test on the ADR's decision quality, not a
ratification. Chris ratification remains a separate act after
SIGN cycle 1 folds are applied (Chris "agree all F1-FN"
wholesale ratification is the S1399-forward pattern; per-fold
ratification is also acceptable).

**Stage 3 SIGN is mandatory when** the arc's planned PRs include
any of:

- A DB migration.
- A fleet-key surface change (per §5.0 definition).
- Any auth / session / permission-floor change.
- Any payment / revenue-write path change.
- Any intake with `blast_radius: CROSS_DOMAIN` OR `SUBSYSTEM` AND
  `reversibility ≤ 3` (per §3.1 scoring).

Stage 3 SIGN is optional if none of those trigger.

**Isolation-pin discipline.** Mint a fresh SIGN pin at arc-open;
retire at arc-close via `session_tool.retire force=true`, matching
the Research OS 17-consecutive-arc pattern.

## 7.3 Claude execution lane

Claude Code executes:

- All code edits, PR creation, and git ops.
- Migration authoring + roll-forward + roll-back scripts.
- Regression test authoring.
- Handoff writing.
- Docs cascade + `cross_domain_integration_audit.md §14`
  refresh at close.
- OPEN_ARCS.md updates.

Claude does NOT execute:

- Rigby's tool-surface work — for investigations, audits, deliverable
  edits, PA tool-surface queries, backlog scans, always route to
  Rigby first; verify independently. Per MEMORY rule
  `feedback_claude_directs_rigby_then_verifies`.

## 7.4 The Direct → Execute → Verify loop applied to implementation

Same three-step loop CLAUDE.md defines, mapped onto implementation:

| Step | Research phase | Implementation phase |
|------|---------------|---------------------|
| **Direct** | Claude writes concrete instruction for Rigby | Claude writes concrete instruction for Rigby (e.g., "run `deliverable_tool.list workspace_id=… status=in_progress` and report row count") |
| **Execute** | Rigby runs via PA tool surface | Rigby runs via PA tool surface; separately, Claude ships PRs |
| **Verify** | Claude reads Rigby's `Tool Runs (verbose)` block + ORM / git log | Same — plus Claude verifies the PR discharged the intake item as scoped |

---

# Part 8 — Feedback loop and implementation debt

## 8.1 Post-close docs update

Every closed arc updates:

1. **Topic docs.** If the implementation changed a subsystem's
   observable behavior, its `docs/topics/<subsystem>.md` file
   must be updated in the arc's close PR.
2. **PLATFORM_INVENTORY.md** if runtime counts changed. Regenerate
   via `refresh_doc_inventory_blocks`.
3. **PLATFORM_WHAT_IT_IS.md** narrative if a subsystem's shape
   materially changed.
4. **CLAUDE.md** if a new subsystem or workflow rule emerged.
5. **MEMORY.md** if the arc surfaced a new feedback rule worth
   persisting across sessions (opt-in — Chris ratifies).

## 8.2 Cross-domain audit refresh trigger

Every closed implementation arc appends a §14.N entry to
`cross_domain_integration_audit.md`, capturing:

- Which STRONG/WEAK/MISSING/OVERCOUPLED classifications the arc
  changed.
- Which CX-P patterns the arc discharged (or partially discharged).
- Any new disconnects surfaced during implementation that
  research had not flagged.

This closes the loop: research produces the audit; implementation
refreshes the audit; the audit is always current.

## 8.3 Implementation debt register

Location: `docs/research/implementation/IMPLEMENTATION_DEBT.md`
(proposed — see §13 D6). Structure mirrors the Research Debt
concept from Research OS §15:

| Field | Meaning |
|-------|---------|
| `debt_id` | `ID-NNNN` |
| `origin_intake_id` | Which intake produced the debt |
| `origin_arc_ref` | Which arc surfaced the debt |
| `debt_type` | `RETRACTED` \| `DEFERRED` \| `PARTIAL_DISCHARGE` \| `TECH_DEBT_ACCRUED` \| `CONTRACT_VIOLATION` |
| `severity` | `LOW` \| `MEDIUM` \| `HIGH` |
| `description` | Free-text |
| `resolution_path` | What would discharge it (new research arc / new intake / redesign / ADR revision) |
| `status` | `ACTIVE` \| `RESOLVED` |

Debt is paid down in dedicated arcs or piggybacked on adjacent
arcs — same pattern as Research Debt.

## 8.4 Retracted findings register

A **retracted finding** is an intake item that did not survive
first contact with implementation. Categories:

- **Root cause was wrong.** Research misdiagnosed; the fix
  described would not solve the problem.
- **Fix would introduce worse problem.** Cure worse than disease.
- **Superseded by adjacent finding.** A different arc already
  discharged it.
- **Deferred to research.** New evidence surfaced mid-arc that
  requires re-research before implementation.

Every retraction goes into the implementation debt register with
`debt_type: RETRACTED` and a `retraction_reason` written by
Claude, verified by Rigby, ratified by Chris (light touch — usually
"agree" without further discussion).

Retracted findings are NOT deleted from `cross_domain_integration_
audit.md` — the audit is truth-history, not just current state.
A retracted finding is annotated in the audit's §14 refresh log
so future research knows the finding was tried and did not hold.

## 8.5 §10 methodology section

Every implementation arc's canonical close doc includes a §8
"What This Arc Taught Us About How to Do Implementation" section,
mirroring the Playbook §11.3 xx99 §10 addition adopted at S1399
close. Structure:

- 8.1 What worked
- 8.2 What to codify into IOS v-next (two-triggers threshold)
- 8.3 Anti-patterns to avoid
- 8.4 Suggestions for IOS itself
- 8.5 Suggestions for future implementation arcs (optional)

Two-triggers threshold: an insight becomes an IOS codification
candidate only after **two independent implementation arcs**
surface it. Same rule as Playbook §20 for research.

---

# Part 9 — Anti-chaos rules

## 9.1 Sequential arcs on overlapping surface

Restated for emphasis (per §4.4): implementation arcs on the same
files / models / migrations / PA tools serialize. Distinct-surface
parallelism is permitted.

## 9.2 Batch size caps per arc

**Values are v1 default hypotheses, not canon.** All caps below
are calibrated from research-arc cadence (which averaged 5–7
sessions and 6–15 findings per arc across Groups 1300–2600).
Implementation cadence may differ. Recalibrate after the first 2
implementation arcs close, per §13 D5.

- Intake items admitted per arc: **3–8 (target), 12 (ceiling).**
- PRs per arc: **3–12 (target), 20 (ceiling).**
- LOC per arc: **≤3,000 (target), 8,000 (ceiling).**
- Arc duration: **3–8 sessions (target), 12 (ceiling).**

Ceilings triggered → split the arc.

## 9.3 Rigby SIGN load ceiling

Per MEMORY rule `feedback_rigby_sign_worker_instability_recovery`:

- Batch SIGN into **3–4 findings per prompt** for large audits.
- Two-pin ceiling before falling back to parent-Claude
  verifier-loop as compensating quality gate.
- Fresh pin per arc; retire at close via
  `session_tool.retire force=true`.

## 9.4 Stage 5 verification cap (Rigby post-merge exercise)

Rigby's Stage 5 post-merge exercise is a genuine load source —
each verification requires reading a `Tool Runs (verbose)` block,
cross-checking against ORM / git log, and often re-firing tool
calls. IOS caps Stage 5 verification volume to prevent verification
debt from accumulating past merged PRs.

- **≤3 PR verifications per session.** Any excess merged PRs wait
  for a subsequent verify session; they do NOT block the current
  session's Stage 4 build progress but DO block the arc from
  reaching Stage 6 close.
- **Verification debt is tracked** — the arc's scoping doc §7
  gains a running "Merged, unverified" tally that must reach zero
  before Stage 6 close.
- **No-new-arc-while-verification-debt rule.** No new implementation
  arc opens if any prior arc has unverified merged PRs, OR if
  §15.6 drift verification has failed for 2 consecutive sessions.
  This targets the real contention: verification stacking + drift
  sweeps competing with active arcs. Chris can override by
  explicit directive.

## 9.5 Chris ratification bandwidth ceiling

**Observed defaults, not caps.** Values calibrated from research-arc
Chris cadence across Groups 1300–2600. Chris can override any
ceiling by explicit directive; otherwise Claude must queue.

- **≤3 arc-scoping ratifications** per session.
- **≤5 ADR ratifications** per session.
- **≤1 posture/architectural decision** per session.

Exceeding these = queue for next session, not more Chris time.

## 9.6 Finding retraction path

Any Claude session that discovers an intake item does not
survive implementation contact:

1. Do NOT ship a "close-enough" PR.
2. Mark the intake `RETRACTED` in `BACKLOG.md`.
3. File an implementation-debt row.
4. Route Chris via PA chat for retraction ratification.
5. Continue the arc with remaining intake items.

Retraction is a **success mode** of the OS, not a failure. It
means research is being pressure-tested by implementation reality.

## 9.7 The "big-bang refactor" prohibition

IOS explicitly prohibits arcs that:

- Rewrite an entire subsystem in one arc.
- Delete + re-add a module.
- Change multiple contracts simultaneously.

If the research recommends such a change, IOS decomposes it into
sequenced arcs with intermediate states that Chris can verify.
See §4.4 no-parallel-arcs + §9.2 batch caps.

---

# Part 10 — Short start commands

Mirroring Playbook §21. Chris's terminal / PA short commands:

## 10.1 Opening

- `Open implementation arc I-NNNN: <slug>` — starts the arc at
  Stage 1 (scoping).
- `Open implementation arc from intake IB-<arc>-<seq>` — opens
  a single-finding arc.
- `Open implementation arc from CX-P<n>` — opens a cross-cutting
  arc addressing a pattern.

## 10.2 Advancing

- `Continue implementation arc I-NNNN` — resume at the current
  stage (Claude reads `OPEN_ARCS.md` to determine stage).
- `Advance implementation arc I-NNNN to <stage>` — jump stage
  (rare; requires ratification of the stage's exit gate).
- `Retract intake IB-<arc>-<seq>` — flip status to `RETRACTED`
  mid-arc.

## 10.3 Closing

- `Close implementation arc I-NNNN` — Claude authors the close
  doc, routes to Rigby SIGN, ratifies with Chris.

## 10.4 How Claude infers the arc shape

When Chris opens with a short command, Claude infers:

1. Read `BACKLOG.md` for matching `arc_ref` intake items.
2. Read `OPEN_ARCS.md` for arc history / stalled state.
3. Read the last handoff for context.
4. Route to Rigby if `service_context: local` is not verified.

---

# Part 11 — First-queue construction procedure

**IMPORTANT.** This procedure is provided as reference. **Do NOT
execute** until Chris explicitly asks. The procedure exists so
that when Chris does ask, the construction is legible and
repeatable, not ad-hoc.

## 11.1 Inputs required

1. All xx99 canonical summaries for closed research arcs
   (currently: 1399, 1499, 1599, 1699, 1799, 1899, 1999, 2099,
   2199, 2299, 2499, 2599, 2699 — 13 summaries; 2300 Mobile
   intentionally skipped).
2. Current `cross_domain_integration_audit.md` §2 + §14 refresh
   log through v4.
3. All CX-P pattern crystallizations (currently CX-P1 through
   CX-P8 per audit v4).
4. Latest MEMORY.md rules (behavioral guidance / anti-patterns).
5. Chris's current top-line goals (revenue, attention preservation,
   Rigby's usability).

## 11.2 The six-step procedure

**Step 1 — Extract.** Iterate every xx99 §7 anchor-updates + §8
follow-on queue + §5 recommendations. Iterate every §14 audit
row's MISSING/WEAK/OVERCOUPLED entry. Iterate every CX-P pattern.
Produce a raw candidate list (expected: 100–300 items).

**Leaf-decision granularity rule (v1.1 execution refinement).**
One intake row per Chris-ratifiable decision unit — NOT one row
per §8 tier bundle. A §8 block that reads "T1 CRITICAL ADRs (20
items)" produces 20 rows, one per sub-decision (each with its own
`source_ref: §8.2.<label>`), not 1 bundle row. A CX-P4 posture
gate that manifests across 7 domains produces 7 rows (one per
domain), not 1 row per pattern. If the source doc does not
enumerate the sub-decisions concretely enough to name
`affected_surfaces` for each, the extraction is under-specified —
route back to research (§2.4 reject condition "cannot name
affected_surfaces concretely") rather than emit a bundle row.

Rationale: bundle rows silently collapse ratifiable units under a
single `chris_gate: PENDING` and break §11.3 per-tier
ratification (Chris cannot "agree all" against a bundle he cannot
see). First execution surfaced this via ~20 bundle rows across
1699/1799/1899/1999/2099/2199/2299/2499/2599/2699 — the deep-late
arcs where §8 blocks are richest.

Extraction sizing hint: leaf granularity for the current 13-arc
corpus is expected to yield ~250–400 rows post-dedup, not ~150.
Extractors that return <200 rows for the current corpus are
likely bundling; re-run with explicit leaf-granularity
instructions.

**Step 2 — Dedup.** Merge duplicates: findings that appear in
multiple xx99 summaries or reference the same disconnect are
folded into a single intake row.

**Step 3 — Classify.** Fill in every field of the intake schema
(§2.2): `blast_radius`, `risk_class`, `expected_ship_size`,
`affected_surfaces`, dependencies.

**Step 4 — Score.** Apply the priority rubric (§3.1) to every
row. Apply the cross-domain dependency bump (§3.3).

**Step 5 — Tier.** Bucket into P0 / P1 / P2 / P3 / DEFER per
score-to-tier mapping.

**Step 6 — Ratify.** Present tiered backlog to Chris **via Rigby
in PA chat** (per MEMORY rule `feedback_rigby_comms` and v1.1
execution refinement) as an "agree all with overrides"
ratification card, using a **fresh IOS-scoped SIGN pin** minted
per §15.14 pin lifecycle (e.g.,
`session_tool.create_fresh label='ios-part11-first-queue-ratification'`).
Terminal-only presentation is permitted only when Chris
**explicitly** requests it in the same session (e.g., "present the
ratification card in the terminal, not via Rigby"). Chris
overrides any tier assignment; ratified backlog is written to
`BACKLOG.md` only **after** ratification closes; the SIGN pin
retires at ratification close per §15.14.

## 11.3 Chris ratification gate

The queue is not "the queue" until Chris ratifies it. Ratification
scope:

- **Per-tier ratification.** Chris agrees each tier's contents.
- **First-arc override.** Chris explicitly names the first
  implementation arc even if the top-scored P0 is not it.
- **Reversibility.** Chris can revoke tier assignments in any
  subsequent session.
- **Routing (v1.1 execution refinement).** Ratification card
  routes through Rigby via a fresh IOS-scoped SIGN pin (§15.14)
  by default. Chris may waive to terminal-only for a specific
  session by explicit directive; the waiver does not persist
  across sessions.

## 11.4 First queue is a snapshot, not a plan

The constructed queue reflects the world at Step 6. Every
subsequent research arc close or audit refresh re-scores the
backlog (§3.4). The queue evolves; IOS does not lock Chris into
a static plan.

---

# Part 12 — Consumer relationship to research outputs

IOS is a **downstream consumer** of the research library. This
section makes the consumption contract explicit.

## 12.1 xx99 canonical summaries → IOS intake

For each xx99, IOS reads:

- **§5 recommendations** → intake `source_type: xx99_recommendation`
- **§7 anchor-updates** → intake `source_type: xx99_anchor_update`
- **§6 unresolved unknowns** → `BLOCKED_ON_RESEARCH` intake rows
- **§8 follow-on research queue** → NOT intake; routed back to
  Research OS as new research arc candidates
- **§10 methodology** → NOT intake; consumed by IOS §14
  meta-learning ledger to evolve IOS itself

## 12.2 cross_domain_integration_audit.md → IOS priority

The audit is IOS's **canonical disconnect map**:

- §2 STRONG rows → NOT intake (no fix needed)
- §2 WEAK rows → intake with `source_type: cross_domain_WEAK`,
  default priority bump per §3.3
- §2 MISSING rows → intake with `source_type: cross_domain_MISSING`,
  higher default priority
- §2 OVERCOUPLED rows → intake with `source_type: cross_domain_
  OVERCOUPLED`, priority depends on blast radius
- §14 refresh log deltas → new intake rows or re-scoring of
  existing rows

## 12.3 CX-P pattern crystallizations → IOS cross-arc primitives

Each CX-Pn pattern that has crossed the two-trigger codification
threshold becomes a candidate **cross-arc implementation
initiative**. These arcs are named `I-Cxxx_<pattern-slug>_
codification`, mirror the CX-P handle, and address every surface
where the pattern manifests.

Current inventory (cross_domain_integration_audit.md v4 as of
2026-07-05):

| Pattern | State | IOS treatment |
|---------|-------|---------------|
| **CX-P1** Runtime-owner MISSING | 2 of 11 arcs confirmed, 1 candidate | Route Revenue + Sports + HumanAttention un-owned surfaces to Employee OS ownership assignment before implementation |
| **CX-P2** Write-only-forgotten | 1 arc | Single-arc; not IOS-actionable yet |
| **CX-P3** ZERO outbound delivery | 2 of 2 confirmed | Cross-arc initiative candidate: unified delivery layer for OutreachDraft + Newsletter (+ BlockchainAuditBrief pending posture) |
| **CX-P4** POSTURE-PENDING | 7 of 11 arcs confirmed | Every POSTURE-PENDING intake requires ADR before Stage 4 opens |
| **CX-P5** Meta-methodology §10 template | 11 of 11 (codified) | IOS §14 mirrors this |
| **CX-P6** Parallel-schema drift | 3+ of 11 arcs | Cross-arc initiative candidate: umbrella track for Revenue/Sports/Observability schema reconciliation |
| **CX-P7** Declared-but-unenforced contract | 2-trigger threshold MET | Scope-bounded IOS rule: auth-failure-handling codification (see §5.2 silent-degrade emission rule) |
| **CX-P8** Silent-degrade vs explicit-failure ambiguity | 2-trigger threshold MET (auth) | IOS §5.2 rule 7 codifies silent-degrade emission; general codification if 3rd non-auth trigger surfaces |
| **CX-P9** Monotonically-increasing SIGN confidence | 1 arc (candidate) | Not IOS-actionable yet; methodology observation |
| **CX-P10** Design-complete + runtime-scaffolding | 3 of 11 arcs | Distinct intake `source_type` per §3.1.b; skips Stage 2 ADR authoring |

## 12.4 T4 cross-arc delegate ownership

T4 findings are explicitly delegated by the closing arc's §9
hand-off to a future arc's queue. IOS assigns ownership as
follows:

- **Owner of pick-up.** The receiving arc's xx99 canonical
  summary author (i.e., the Claude that closes the receiving
  arc) is responsible for materializing T4 delegates into
  intake rows during the arc-open step.
- **T4 intake row status.** Enters `BACKLOG.md` with
  `status: TRIAGED`, `arc_ref` populated with the sending arc,
  and `notes` citing the sending arc's §9 hand-off row.
- **Cross-arc-owed tracking.** The delegate remains visible in
  the sending arc's xx99 §9 forever (never removed) so future
  Claudes can trace the hand-off if the delegate is dropped.

## 12.5 Cascade discipline

Per MEMORY rules `feedback_docs_pipeline_4_step_cascade`,
`feedback_docs_cascade_at_every_close`, and
`feedback_cascade_pr_must_include_embed_step`, the full 4-step
docs cascade + `build_docs_provenance` MUST run so Rigby's RAG
stays in-sync with `main`. IOS v1.3 (2026-07-06) refines the
timing rule after the arc-open PR / separate-cascade-PR pattern
recurred three times same-day (see verifier_loop entry).

### 12.5.a The rule (pre-PR vs post-merge cascade)

Cascade timing is determined by the artifact type in the PR, not
by convenience.

**Pre-PR cascade required (co-locate in the same PR as the
artifact):** Any PR whose changed files include a RAG-critical
artifact type (see §12.5.b) MUST run the full 5-step cascade
locally before PR open, commit the resulting `docs/INDEX.md` +
`docs/_provenance.json` diffs to the same PR, and include the
PR-body cascade evidence block (§12.5.d). This prevents the
window between artifact merge and cascade-PR merge where the
artifact exists on `main` but is invisible to Rigby's RAG — the
exact window during which Chris typically ratifies via Rigby.

**Post-merge cascade PR permitted:** For PRs that do NOT change
any RAG-critical artifact type (§12.5.c), a follow-up cascade PR
may run after merge on a batched cadence (typically at session
close or arc-close). Post-merge cascade PRs must still cite the
5-step evidence block (§12.5.d) so the batching is auditable.

**Chris-explicit deferral clause:** Chris may explicitly defer
cascade to a follow-up PR by directive on any specific PR (e.g.,
urgent fix, blocked-on-embed-timing, prod incident). Deferral
must be recorded in the PR body under a `## Cascade deferral
(Chris-explicit)` section citing the directive.

### 12.5.b RAG-critical artifact types (pre-PR cascade required)

These artifact types are the ones Rigby must be able to search
during the review + ratification window. If any changed file
matches a bullet below, cascade co-locates:

- **Arc scoping docs.** `docs/research/implementation/<slug>/
  I-NNNN_<slug>_scoping.md` at Stage 1 open. Rigby SIGN Cycle 1
  reads the scoping doc; if it isn't in RAG, SIGN is grepping the
  diff hunk, not the corpus.
- **ADRs.** `docs/adr/ADR-NNNN-<slug>.md` at Stage 2 authoring.
  Chris ratifies ADRs against corpus context; RAG must have the
  ADR body when the ratification card lands.
- **Implementation arc close docs.** `docs/research/
  implementation/<slug>/I-NNNN99_<slug>_implementation_close.md`
  at Stage 6.
- **This doc (IOS) and companion OS docs.** `docs/research/
  process/IMPLEMENTATION_OPERATING_SYSTEM.md`,
  `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`,
  `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`. Any patch to
  process authority must land searchable so Rigby's next SIGN
  cycle reads the current version, not the pre-patch version.
- **RATIFICATION records.** `docs/research/implementation/
  RATIFICATION_YYYY-MM-DD_<slug>.md` frozen records.
- **BACKLOG + DEBT registers when changing scope, not
  housekeeping.** `docs/research/implementation/BACKLOG.md`
  when adding new intake rows, flipping `TRIAGED → IN_ARC`, or
  materializing T4 delegates. `docs/research/implementation/
  IMPLEMENTATION_DEBT.md` when adding rows at any severity.
  Status-flip-only housekeeping (e.g., `IN_ARC → SHIPPED` after
  merge) is exempt.
- **OPEN_ARCS.md at arc open or close.** `docs/research/
  OPEN_ARCS.md` when adding a new in-progress arc row, closing an
  arc row, or stalling an arc. Metadata-only touch-ups (e.g.,
  `last_updated:` banner refresh) are exempt.
- **Cross-domain integration audit §14 refresh appends.**
  `docs/research/platform/cross_domain_integration_audit.md`
  when appending §14.N implementation-side deltas per §8.2.

### 12.5.c Post-merge cascade PR permitted (deferrable)

Artifact types that do NOT require pre-PR cascade — a batched
follow-up PR is acceptable:

- Runtime code changes with no doc surface (`core/**`, `frontend
  /**`, `tests/**`, migrations, Procfile, Makefile).
- Handoff documents (`docs/handoffs/SESSION_NNNN_*.md`) — write
  history, not query surface.
- Topic doc refreshes (`docs/topics/<subsystem>.md`) triggered
  by mechanical drift — batchable at session close.
- PLATFORM_INVENTORY regenerations (`docs/PLATFORM_INVENTORY.md`
  via `generate_platform_inventory`).
- Auto-generated INDEX.md refresh when there is no other doc
  change (mechanical noise).
- Ephemeral scratch (`.claude/scratch/**`).

### 12.5.d PR-body cascade evidence block (canonical template)

Every PR — pre-PR co-located OR post-merge batched — records
cascade evidence via this block, so an auditor can reproduce the
run:

```
## Cascade evidence (per IOS §12.5)

| Step | Command | Result |
|------|---------|--------|
| 1 | `build_docs_index` | <N> docs indexed; <N> with frontmatter; <N> lines; active=<N>, draft=<N>, superseded=<N> |
| 2 | `build_rag_corpus` | **<N> chunks** across <N> files (chunk_size=1200); wrote `.rag/corpus.jsonl` |
| 3 | `sync_docs_index_to_documents` | Created <N>, Updated <N>, Skipped <N>, Errors <N> |
| 4 | `embed_documents --all-unembedded` | Found <N> unembedded docs; processed [list]; **embedded <N> chunks** |
| 5 | `build_docs_provenance` | <N> commits parsed; <N> docs indexed; wrote `_provenance.json` |

Files changed by cascade: `docs/INDEX.md`, `docs/_provenance.json`.
```

Step 4 chunk count is the critical evidence field per MEMORY rule
`feedback_cascade_pr_must_include_embed_step` — it demonstrates
that embed actually ran on the RAG-critical artifact, not just
that indexing swept it. A block with `<N> = 0` on step 4 for a
pre-PR-cascade artifact is a PR-body red flag (means the artifact
was already embedded from a prior sync, OR the artifact was not
actually picked up — verify which).

### 12.5.e Stage-by-Stage cascade contract

The rule concretely applies at these Stage boundaries per §4.3:

- **Stage 1 (Scoping) exit → arc-open PR.** Pre-PR cascade
  REQUIRED (scoping doc is RAG-critical per §12.5.b). Cascade
  runs BEFORE the arc-open PR opens; evidence block included in
  the PR body; INDEX.md + `_provenance.json` co-committed.
- **Stage 2 (Design-prep + ADR) → each ADR PR.** Pre-PR cascade
  REQUIRED per ADR PR (ADRs are RAG-critical per §12.5.b).
- **Stage 3 (Pre-flight).** No cascade — pre-flight is a scoping-
  doc §7 update; cascade of the scoping doc already ran at
  Stage 1. Pre-flight §7 edit rides on the next Stage 4 PR OR
  batches into a Stage 6 cascade.
- **Stage 4 (Build).** No pre-PR cascade unless the Stage 4 PR
  itself touches a RAG-critical artifact (rare — most Stage 4
  PRs are runtime code). Topic doc drift touched by Stage 4 PRs
  can batch to Stage 6 cascade.
- **Stage 5 (Verify).** No cascade — verification produces tool-
  output blocks, not doc changes.
- **Stage 6 (Close) → close doc PR.** Pre-PR cascade REQUIRED
  (close doc is RAG-critical; audit §14 refresh is RAG-critical).
  This IS the "cascade at every close" MEMORY rule's canonical
  application.

### 12.5.f Interaction with D11 Wave 1 automation

D11 Wave 1 (`build-docs-cascade.yml` GitHub Action, per §13 D11)
partially discharges this rule but does NOT replace it. Wave 1
automates the post-merge embed step on any PR whose body cites
`arc-close: I-NNNN99`. The §12.5 v1.3 rule is a superset:

- **§12.5 v1.3 pre-PR co-location covers everything Wave 1 does
  NOT.** Wave 1 runs after merge; §12.5 v1.3 runs before PR open.
  The two do not conflict — Wave 1 backstops the post-merge
  embed step, §12.5 v1.3 covers the pre-merge review window.
- **§12.5 v1.3 also covers arc-open and Stage 2 PRs**, which are
  NOT arc-close and therefore NOT triggered by Wave 1's
  `arc-close:` body cite. Without §12.5 v1.3, Wave 1 alone would
  leave every Stage 1 and Stage 2 PR under the stale-RAG risk
  the pattern already exhibited.
- **Wave 2 (§13 D11)** — future `manage.py ios_gate_check` command
  — could enforce §12.5 v1.3 as a pre-Stage-6-close check by
  validating that every RAG-critical artifact touched in the arc
  has a corresponding cascade evidence block in the PR history.

Rule prioritization: §12.5 v1.3 discipline is the primary mechanism;
Wave 1 automation is the safety net; Wave 2 is the auditor.

---

# Part 13 — Open questions and Chris decision points

The following decisions require Chris's explicit ratification
before IOS graduates from `draft` to `active`. Each is a distinct
question, ratifiable separately.

**Ratified 2026-07-06 (Chris directive):** "Default stance: accept
the IOS v1.1 recommendations unless there is a concrete reason not
to." D1–D7, D9, D10, D12 accepted at the recommended option. D8
deferred. D11 accepted with Wave 1 required before scaling beyond
two implementation arcs. Ratifications recorded inline below;
recommendations preserved as historical record.

## D1 — Implementation arc tree location

Two options:

- **Option A (recommended).** Implementation arcs live under
  `docs/research/implementation/<slug>/` — one folder per
  domain-flavored implementation arc, mirroring
  `docs/research/domains/<slug>/`. Keeps one arc manifest, one
  cascade, one INDEX.
- **Option B.** Implementation arcs live under a parallel
  `docs/implementation/<slug>/` tree. Cleaner separation but
  doubles OPEN_ARCS / INDEX / cascade infrastructure.

**Recommendation:** Option A. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — implementation arcs
live under `docs/research/implementation/<slug>/`.

## D2 — Implementation arc numbering

Two options:

- **Option A (recommended).** `I-NNNN` prefix, distinct from
  research session ranges. Prevents collision.
- **Option B.** Merge into the same numeric space (e.g., 3000+
  reserved for implementation).

**Recommendation:** Option A. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — `I-NNNN` prefix.
First implementation arc will be numbered `I-0100` per §4.2.

## D3 — ADR corpus establishment

- **Option A (recommended).** Install `docs/adr/` with the format
  described in §2.5. Wire IOS to require ADR ratification for
  every `NEEDS_ADR` intake.
- **Option B.** Do not install; collapse ADR requirements onto
  arc-scoping doc §Decisions ratified sections. Keeps existing
  habits but leaves §8.3 P1 gap open.

**Recommendation:** Option A. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — install `docs/adr/`.
Closes the Research OS §8.3 P1 gap. Bootstrap ADR
(`ADR-0001-establish-adr-corpus.md`) is one of the three
Appendix C first-artifact deliverables.

**Cross-reference (v1.2 execution refinement).** Enforcement of
this ratification at implementation arcs is deferred to §4.3
Stage 1 exit gate ADR corpus precondition. Any arc admitting a
`NEEDS_ADR` intake MUST verify `docs/adr/` exists on `main` at
Stage 1 close OR bundle `IB-Q1-BOOT-01` as an in-arc P0 prep PR
OR block Stage 1 close until a separate arc ships the corpus.
See §4.3 Stage 1 for the concrete rule.

## D4 — Backlog register location

- **Option A (recommended).** `docs/research/implementation/
  BACKLOG.md` — plain markdown, grep-friendly, versioned in
  git.
- **Option B.** Store as PA tool state (deliverables, workspace
  tickets). Better UI, worse cross-session grep.
- **Option C.** Both — canonical in git, mirrored to PA tool
  state.

**Recommendation:** Start with A; upgrade to C if usage volume
justifies. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — start with
`docs/research/implementation/BACKLOG.md`. Upgrade to Option C
mirror if usage volume justifies (revisit after 2 arcs per D5
cadence).

## D5 — Batch size ceilings + Chris review bandwidth

Values proposed in §6.4 + §9.2 are estimates. Chris may want
tighter or looser ceilings based on real capacity.

**Recommendation:** Ratify proposed values as v1; revisit after
2 arcs run. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Values ratified as v1 defaults.
Recalibrate after the first 2 implementation arcs close. §9.2
+ §9.5 already labeled as "v1 default hypotheses" and "observed
defaults" respectively — no further edits needed.

## D6 — Implementation debt register scope

- **Option A (recommended).** Establish `docs/research/
  implementation/IMPLEMENTATION_DEBT.md` mirroring Research OS
  §15 Research Debt.
- **Option B.** Fold implementation debt into existing Research
  Debt register.

**Recommendation:** Option A. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — separate
`IMPLEMENTATION_DEBT.md`. Distinct register from Research Debt;
keeps phase debt scoped by phase authority.

## D7 — Rigby SIGN pacing against research arcs

If research arcs are still opening (e.g., a future 2700+ arc),
does IOS defer to research pacing? Options:

- **Option A (recommended).** Research arcs continue; IOS runs
  distinct-surface arcs in parallel. Same-surface implementation
  waits for the research arc to close.
- **Option B.** Freeze research once IOS activates; drain the
  backlog; resume research after.

**Recommendation:** Option A. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — distinct-surface
parallel permitted. Same-surface implementation waits for research
arc close per §4.4 no-parallel-arcs rule.

## D8 — First implementation arc identity

**IOS does not preselect the first arc.** Chris ratifies which
arc runs first once the first queue is constructed (Part 11) OR
directly ("open implementation arc I-NNNN: <slug>" as a Chris
directive without queue construction).

Chris directive to run first-queue construction is separate from
this question.

**Ratified 2026-07-06 (Chris):** **DEFERRED** — decision held
until after first-queue construction (Part 11) OR an explicit
Chris directive. No first arc chosen at v1.2 ratification. IOS
graduates to `active v1` without a first-arc pick.

## D9 — IOS install-record location

Mirroring Research OS §19 install record + §20 mission
deliverables. Where does the IOS install record live?

- **Option A (recommended).** Appendix of this doc (§A.4).
- **Option B.** Separate `IOS_INSTALL.md`.

**Recommendation:** Option A. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — install record lives
at Appendix §A.4 of this doc. Kept co-located with the OS itself.

## D10 — Enforcement of cross_domain audit refresh at implementation arc close

The audit refresh is drift-prone even in research (§14 has been
lagging). At implementation arc close, should refresh be:

- **Option A (recommended).** Hard gate — arc cannot close
  without §14 entry.
- **Option B.** Soft gate — Claude reports drift but arc closes;
  refresh caught up in a batch.

**Recommendation:** Option A. Chris ratification needed.

**Ratified 2026-07-06 (Chris):** Option A — hard gate. Every
implementation arc close (Stage 6) requires the
`cross_domain_integration_audit.md §14.N` refresh entry as a
non-skippable exit condition per §4.3 Stage 6.

## D11 — IOS gate runner (automation scope)

Should IOS install a lightweight gate runner + CI hooks that
automate the parts of §5.1 / §15.6 that historically drift?

- **Option A (recommended).** Yes, in two waves:
  - **Wave 1 (before scaling past 2 arcs).** Install
    `build-docs-cascade.yml` GitHub Action triggered on merge of
    any PR whose body cites `arc-close: I-NNNN99`. Fixes the
    memory-rule-drift pattern
    `feedback_cascade_pr_must_include_embed_step`.
  - **Wave 2 (before scaling past 5 arcs).** Add a manual-invoked
    `manage.py ios_gate_check` command that checks: (a) docs
    cascade drift (`verify_doc_claims --only-drift`), (b) migration
    state, (c) feature-flag consumer existence per §5.1 rule 7,
    (d) beat-task ZERO-FIRE per §5.1 rule 8, (e) PR-state drift
    per §15.6 rule 10. Runs as a pre-Stage-6 close check.
- **Option B.** No — enforce manually via §5.1 + §15.6
  checklists. Keeps CI simple; accepts drift risk.

**Recommendation:** Option A. Wave 1 is **strongly recommended to
move IOS from draft v1 → active v1** if the goal is trustworthiness
at volume. Wave 2 can lag behind Wave 1. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — two-wave gate-runner
accepted. **Wave 1 required before scaling beyond two implementation
arcs.** Wave 2 remains recommended before scaling past 5 arcs but
is not blocking at v1.2. The Wave 1 requirement becomes a
first-class arc-open gate: no third implementation arc opens
until `build-docs-cascade.yml` GitHub Action is installed and
green on at least one prior arc-close PR.

**Cross-reference (v1.3 §12.5.f).** IOS v1.3 codifies pre-PR
cascade co-location for RAG-critical artifacts as a superset of
Wave 1's post-merge coverage. Wave 1 automates the post-merge
embed backstop on arc-close PRs; §12.5 v1.3 covers arc-open
(Stage 1) + ADR (Stage 2) + close (Stage 6) PR bodies + the
pre-review-window RAG visibility contract. Wave 1 is still
required per this D11 ratification; §12.5 v1.3 does not
substitute for it. Wave 2 could additionally enforce §12.5 v1.3
as a pre-Stage-6-close check that every RAG-critical artifact
in the arc has a cascade evidence block in the PR history.

## D12 — Playbook v3 update cadence

Every implementation arc §8 methodology section may propose
Playbook or IOS codifications. Should IOS reserve a dedicated
"process update session" cadence?

- **Option A (recommended).** After every 2 arcs that surface
  playbook/IOS candidate patterns, schedule an explicit
  process-update session (§8.10 META-PROCESS class).
- **Option B.** Ad-hoc when Chris notices drift.

**Recommendation:** Option A. **Ratification needed.**

**Ratified 2026-07-06 (Chris):** Option A — every 2 arcs that
surface candidate patterns, schedule an explicit process-update
session. Prevents playbook / IOS drift while keeping cadence
predictable.

---

# Part 14 — Meta-learning section (§10 analog)

## 14.1 What IOS itself will teach us

Every implementation arc's canonical close doc's §8 methodology
section (per §8.5 above) feeds back into IOS. When two independent
arcs surface the same insight, it becomes a candidate for IOS
codification (two-triggers threshold from Playbook §20).

Examples of insights IOS anticipates learning but has not yet
codified:

- **Rollback plan drift.** Documented rollbacks may not survive
  first invocation. If two arcs discover this, IOS §5.4 codifies
  "rollback dry-run required."
- **Backlog scoring drift.** Priority rubric may over-index one
  dimension. If two arcs re-rank against Chris's overrides,
  IOS §3.1 re-weights.
- **Batch size ceilings.** If arc after arc hits ceilings, IOS
  §9.2 revises the ceilings.
- **Cross-domain arc scope.** If cross-cutting arcs recur, IOS
  may need a distinct "cross-arc" child template.

## 14.2 Codification triggers

Codification of a new IOS rule requires:

1. **Two independent arc close docs** surface the same insight
   in §8 methodology.
2. Chris ratification of the codification (draft PR → Chris
   review → ratified → IOS v-bump).
3. INDEX entry noting the version bump.

## 14.3 IOS versioning

IOS follows Research OS's additive-first evolution policy
(Playbook §20). Rules are not removed; older rules may be marked
`superseded` with a pointer to the newer rule. Version bumps at
the frontmatter `status` line, e.g., `draft` → `active v1` →
`active v2`.

---

# Part 15 — Startup protocol (fresh-session bootstrap + drift detection)

## 15.0 Why this section exists

Today, every fresh Claude session boots by reading Context Kit,
CLAUDE.md, and the documentation tree — but that behavior is an
*implementation detail* of the harness plus habit, not an
*explicit operating rule*. Research OS §4 defines a Bootstrap
Sequence (Level A universal + Level B class-scoped) tuned for
research-class work. That sequence is authoritative for research.
It is **not sufficient for implementation** because implementation
introduces state surfaces research does not have:

- **Live PR state.** Between sessions, PRs merge, get reverted,
  or stall in review. Implementation resume must read that state.
- **Backlog state.** `BACKLOG.md` intake rows flip
  status out-of-band; a fresh session that plans against a stale
  backlog will duplicate or contradict prior work.
- **Migration state.** A migration may already have applied. Fresh
  session must not re-run it.
- **Prod parity.** Fleet-key surfaces may drift between local
  and prod (per MEMORY rule
  `feedback_fleet_caller_verification_before_celery_deletes`).
- **Cross-arc dependency state.** A T4 delegate may have been
  materialized by the receiving arc; a fresh session must not
  re-materialize.

Part 15 codifies the startup that handles all of the above. It is
**additive** to Research OS §4 — everything §4 requires still
runs; Part 15 adds implementation-specific steps after §4 has
completed. Part 15 is **not** an arc lifecycle stage (see §15.9);
it is a per-session pre-stage bootstrap that runs before any stage
engages, every session.

## 15.1 The three-level startup sequence

**Level A — universal (from Research OS §4.1).** Runs every
session regardless of request class. Not restated here — trust
Research OS.

**Level B — class-scoped (from Research OS §4.2 + §5 router).**
Runs after Level A. The §5 router classifies the incoming request
into one of 11 classes. For classes 4 (IMPLEMENTATION), 2
(DESIGN-PREPARATION), 3 (DESIGN-DECISION / ADR), and 6 (BUG FIX),
Level B routes into IOS.

**Level C — IOS implementation bootstrap (this section).** Runs
after Level B routes to IOS. Consists of these ordered steps:

**C.1 — Load IOS itself.** Read this file (`IMPLEMENTATION_OPERATING_
SYSTEM.md`) in full. Cache the source-of-truth hierarchy (§15.2),
the six-stage lifecycle (§4.3), and the pre-code / pre-merge /
post-merge gates (§5.1 / §5.2 / §5.3). If IOS status is `draft`
(not `active`), pause and route to Chris — IOS is not ratified.

**C.2 — Load the backlog register.** Read `docs/research/
implementation/BACKLOG.md`. Cache the row set for the target
domain(s). Verify no intake is stuck in `INTAKE` state that
should have progressed to `TRIAGED`.

**C.3 — Load the implementation debt register.** Read `docs/
research/implementation/IMPLEMENTATION_DEBT.md`. Any `ACTIVE`
debt whose resolution path names the target domain or arc must
be considered before opening or advancing an arc.

**C.4 — Load the cross-domain audit.** Read
`docs/research/platform/cross_domain_integration_audit.md` §2
(STRONG/WEAK/MISSING/OVERCOUPLED table) and §14 refresh log for
the target domain(s). This is the disconnect map the arc will
consume or update.

**C.5 — Load the relevant xx99 canonical summaries.** For each
target domain, read the xx99 summary. Cache §5 recommendations,
§6 unresolved unknowns, §7 anchor-updates, §8 follow-on queue,
§10 methodology.

**C.6 — Load active-arc documents (if resuming).** If the request
is `Continue implementation arc I-NNNN`, read the arc's scoping
doc, any design-preparation docs, any ADRs referenced, the
current-stage exit-gate checklist, and the last handoff for the
arc.

**C.7 — Load OPEN_ARCS.md arc state.** Cache which arcs are
active / awaiting summary / stalled / closed. Verify the request
does not conflict with a stalled arc that must resume first.

**C.8 — Run the drift verification checklist.** See §15.6. If any
drift check fails, escalate to Chris before touching code, docs,
or arc state.

**C.9 — Determine phase, active arc, current stage, blocking
gates, next executable action.** See §15.3–§15.5. Record all
five in the session's opening message to Chris before any
planning happens.

## 15.2 Source-of-truth precedence hierarchy

Research OS Part 7 makes an important distinction: **truth
authority** (who wins on conflict) and **read priority** (what
Claude reads first for orientation) are two different rankings.
IOS §15.2 preserves that distinction — do not conflate them.

**This section is an implementation-specific view.** It does NOT
supersede Research OS §7.1 Tier structure. On any factual
conflict with Research OS §7.1, **Research OS §7.1 applies.**

### 15.2.a Truth authority (who wins on conflict)

Runtime is Tier 0 — the ultimate truth. All other layers are
derivations or claims about Tier 0. Preserves Research OS §7.1
Tier 0 verbatim.

1. **Tier 0 — Runtime.** Code + database + Redis + Celery. Wins
   over every doc, every memory, every remembered decision.
   Preserved verbatim from Research OS §7.1.
2. **Tier 1 — Auto-generated runtime derivations.**
   `PLATFORM_INVENTORY.md` (sole authoritative counts per
   `DOC_LIFECYCLE.md` §2c), `docs/INDEX.md`, other
   `<!-- DOC-AUTOGEN -->` files. Overrides any hand-written
   claim.
3. **Tier 2 — CLAUDE.md + Research OS + Playbook + IOS
   (governance layer).** CLAUDE.md session-wide operating rules;
   Research OS phase discipline (§3), classification (§5),
   per-class contracts (§8.N); Playbook for research-class
   specialization; **IOS for implementation-class specialization**.
   Within Tier 2, on conflict: **Research OS wins over IOS**
   (IOS is downstream). CLAUDE.md wins over both (session-
   scoped override).
4. **Tier 3 — Ratified authority docs.** `cross_domain_
   integration_audit.md` (sole authoritative disconnect map);
   ratified ADRs (`docs/adr/`); ratified design-preparation
   docs (`authority: design-preparation` with a Chris ratification
   line); xx99 canonical summaries (`authority: research`,
   status `active`).
5. **Tier 4 — Arc-state / backlog-state / debt-state.**
   `OPEN_ARCS.md`, `BACKLOG.md`, `IMPLEMENTATION_DEBT.md`,
   current implementation arc scoping + design-prep + ADR docs
   within the arc folder.
6. **Tier 5 — Subsystem topic docs.** `docs/topics/*.md`.
   Authoritative for current subsystem shape; overridden by any
   higher tier that disagrees.
7. **Tier 6 — Behavioral guidance.** MEMORY.md rules. Bind
   Claude's conduct; do not override an authoritative doc.
8. **Tier 7 — Historical narrative.** `docs/handoffs/*.md`,
   commit messages. Useful for context; never overrides
   current-state docs.
9. **Tier 8 — Session context.** Prior conversation turns,
   remembered context. **Lowest authority.** See §15.7 anti-
   context-drift rule.

### 15.2.b Read priority (what to load first for orientation)

Distinct from truth authority. What Claude reads first to orient
the session. Lower authority sources may appear higher in read
order because they aggregate state (e.g., Context Kit orient).

1. `context-kit orient` output — state-orientation snapshot;
   points at source-of-truth chain + latest handoff.
2. CLAUDE.md — session-wide operating rules.
3. MEMORY.md — behavioral guidance and known feedback rules.
4. `00-START-NEXT-SESSION.md` — session-scoped priority.
5. Research OS §0–§5 (if request may touch research / docs /
   governance).
6. **IOS Part 15** (if request classifies to implementation).
7. Active-arc docs (scoping / design-prep / ADR) if resuming.
8. `OPEN_ARCS.md`, `BACKLOG.md`, `IMPLEMENTATION_DEBT.md`.
9. Relevant xx99 canonical summaries + `cross_domain_integration
   _audit.md` rows for target domains.
10. Topic docs for affected subsystems.

**Rule.** Read in read-priority order. On conflict, apply
truth-authority order. `context-kit orient` output is a
starting point, NOT a decision — it points at Tier 0 sources
that must be verified before Claude commits to any decision.

## 15.3 Phase detection

Before any work begins, determine which phase the incoming
request occupies:

| Detected phase | Signal | Route |
|----------------|--------|-------|
| **Research** | Chris opens with "Start / Continue / Close research group NNNN" | Research OS §8.1 + Playbook |
| **Design-preparation** | Request says "recommend", "pick between options", "draft schema"; no ADR file target | §8.2 |
| **Design-decision (ADR)** | Request says "ratify X"; targets `docs/adr/ADR-NNNN` | §8.3 |
| **Implementation** | Request cites an `intake_id`, an `I-NNNN` arc, or names a runtime PR to open | IOS Parts 4–9 |
| **Bug investigation** | Request says "why doesn't X work", "debug Y" | §8.5 |
| **Bug fix** | Request follows an investigation with a Chris-approved root cause | §8.6 |
| **Ops** | Request touches prod health, deploys, Celery workers | §8.11 |
| **Doc cleanup** | Request says "remove drift" or "reorganize" | §8.8 |
| **Nav query** | Request is a lookup ("what is X", "where does Y live") | §8.9 |
| **Meta-process** | Request modifies this doc, Research OS, or the Playbook | §8.10 |
| **Mixed** | Multiple phases needed sequentially (e.g., "research + implement") | Decompose into ordered contracts per Research OS §5.3 |

Ambiguous phase → ask Chris. Never guess.

**Phase-transition supersession rule (v1.1 execution refinement).**
When IOS is `status: active` AND Chris opens a session with an
implementation-planning framing (examples: "first implementation-
planning session," "start Part 11," "open implementation arc
I-NNNN," "construct the first implementation backlog"), the
Research-OS next-session trajectory encoded in
`00-START-NEXT-SESSION.md` (typically a "T-slot Group NNNN
arc-open" row inherited from the last research arc close) does
**NOT** override IOS phase detection. The active implementation
phase supersedes the paused research trajectory until Chris
explicitly re-enters research via a Research OS command
(`Start / Continue / Close research group NNNN`).

Rationale: `00-START-NEXT-SESSION.md` is Research-OS-authored at
the previous research arc close and does not know about IOS
activation or Chris's per-session phase directive. Session-scoped
Chris directive is authoritative per CLAUDE.md tier precedence +
§15.2.a Tier 2 (CLAUDE.md wins over Research OS + IOS on
session-scoped override). Corollary: `00-START-NEXT-SESSION.md`
should be updated at IOS phase entry to reflect *paused research
trajectory + active implementation phase*, but a stale file does
not block implementation session start. Fresh Claude sessions
must apply this rule during Level C step C.9 phase determination
rather than defaulting to the file's stale row.

## 15.4 Active-arc detection

For an implementation phase request, determine:

- **Is a mid-flight arc named or implied by the request?**
  If yes, that is the active arc.
- **Is there exactly one arc in `OPEN_ARCS.md` under `Currently
  in progress` with matching domain?** If yes, that is likely
  the active arc — confirm with Chris.
- **Is there no active arc?** Two paths: open a new arc (route
  to Stage 1 Scoping per §4.3), or discharge a single intake
  item without an arc (rare; only permitted for
  `SAFE_AUTONOMOUS` + `T3` items per §3.1).

## 15.5 Current-stage + blocking-gate + next-action determination

Once the active arc is identified, read its scoping doc and any
stage-exit checklists to determine:

| Determination | Read | Then decide |
|---------------|------|-------------|
| **Current stage** | Scoping doc frontmatter `status` + stage exit-gate checklists | Stage 1 / 2 / 3 / 4 / 5 / 6 |
| **Blocking gates** | Per-stage gates in §4.3 + §5.1/§5.2/§5.3; intake `risk_class` + `chris_gate` | Which intake items cannot progress this session |
| **Next executable action** | Combination of stage + gates + available intake | The specific action Claude may take THIS session |

Record all three in the session's opening message to Chris.
Do NOT plan code changes, edit docs, or run tools that mutate
state until Chris confirms the determination (or explicitly waves
confirmation for a low-risk continuation).

## 15.6 Startup verification checklist (drift detection)

Before the session declares startup complete, verify:

1. **OPEN_ARCS.md matches reality.** Every arc marked `Currently
   in progress` has an arc pin in `tools/pa_local.sh` header
   or an explicit note that its pin retired at prior close.
   Every arc marked `Closed` has an xx99 (or IOS canonical close
   doc for implementation arcs).
2. **BACKLOG.md is consistent.** No row has `status: IN_ARC` and
   `arc_ref` empty. No row has `status: SHIPPED` with empty
   `pr_refs`.
3. **Cross-domain audit is current.** The audit's §14 refresh
   log has an entry for every arc closed in the last N sessions
   (N configurable; default 5). If gap exists, flag drift.
4. **Referenced xx99 summaries are canonical.** For each xx99
   the active arc cites, verify `status: active` and `authority:
   research`. Draft xx99 summaries are not admissible input.
5. **Ratified ADRs exist for every `NEEDS_ADR` intake in the
   active arc.** No arc advances past Stage 2 with an
   unratified ADR.
6. **Docs cascade currency.** Run `python manage.py
   verify_doc_claims` (unfiltered) and sum the per-doc `drift`
   column across the summary table. **Total drift == 0 is
   clean.** The `--only-drift` filter returns "No matching claims
   to run" when zero rows drift — that message is ambiguous
   (indistinguishable from "no claims registered") and is NOT a
   substitute for the unfiltered summary. Report the drift count
   from the unfiltered run. Do NOT auto-fix drift during a
   startup — surface it and let the request continue only if
   drift is orthogonal to the arc's surface. Command variant
   clarified at v1.1 execution refinement.
7. **Fleet-key surface parity.** If the arc touches
   `FleetServiceKey`, `FleetPAChatAuditRow`, `FleetArtifact`, or
   any Procfile-routed queue, run the 3-axis sweep from MEMORY
   rule `feedback_fleet_caller_verification_before_celery_deletes`
   before opening Stage 4.
8. **PA `service_context: local`.** If the arc will make PA
   calls, verify via `platform_config_tool overview`. Per
   `feedback_pa_worker_function_calling_env.md`.
9. **Migration state.** For any migration the arc plans, verify
   the migration has NOT already been applied via
   `python manage.py showmigrations`.
10. **PR state drift.** For every `BACKLOG.md` row with
    `status: IN_ARC` and a populated `pr_refs`, verify the PR
    state via `gh pr view <ref>` — must be merged, open, or
    explicitly stalled. Verify the referenced commit SHA exists
    in `git log` locally. Catches: "we thought it merged" (squash
    changed SHA), "it got reverted" (revert commit not applied
    to backlog), "PR closed without merging" (session state
    drifted from GitHub). **v1.4 tolerance:** if the BACKLOG row
    uses Discipline B inline syntax (per §2.2 v1.4), grep for
    `pr_refs: #NNNN, #MMMM` inside the row's `notes` or
    `affected_surfaces` cell — same downstream `gh pr view`
    check applies to each `#NNNN` extracted. Rows with no
    `pr_refs` field populated (neither column nor inline) are
    skipped by this rule; the arc's Stage 6 close checklist
    (§4.3) still requires per-row `pr_refs` before close.

Any check failing → escalate to Chris before proceeding. Do not
auto-remediate.

## 15.7 Anti-context-drift rule

**When an authoritative repository document exists, remembered
conversation context does not override it.** Concretely:

- If Claude remembers "we decided to skip step X last session"
  but the arc scoping doc still lists step X in its Stage 3
  checklist, step X runs. Memory is not authority.
- If Claude remembers a PR merged when `git log` shows it did
  not, `git log` wins.
- If Claude remembers an intake row status, `BACKLOG.md` wins.
- If Claude remembers Chris ratified an ADR but no ADR file
  exists, the ratification did not happen — route Chris for
  formal ratification.
- If Claude remembers a design choice but no design-preparation
  doc or ADR captures it, treat as un-decided — recommend, do
  not decide.

This rule is the mirror of Research OS §7.1's "reality wins over
the playbook" (Playbook §20). Implementation extends it to
memory: **reality wins over remembered context, always.**

Corollary: prior-conversation *facts* (e.g., "the last session's
PR touched file X.py") are usable but require verification
against `git log` before Claude plans against them. Prior-
conversation *decisions* (ratifications, ADRs, scope changes) are
NEVER usable unless the corresponding artifact exists in the
repo.

## 15.8 Cold-resume completeness test

**Claim.** A fresh Claude session, given only:

- Context Kit orient output
- CLAUDE.md
- MEMORY.md
- The repository documentation tree

… should be able to resume any implementation arc without any
prior conversation history.

**Test.** For every active arc, verify that the following
questions are answerable from repo artifacts alone:

| Question | Repo artifact source |
|----------|---------------------|
| What arc am I resuming? | `OPEN_ARCS.md` currently-in-progress table |
| What is the arc's scope? | Arc scoping doc (Playbook §11.1 template applied) |
| What intake items belong to it? | `BACKLOG.md` `arc_ref` column |
| What stage is it in? | Scoping doc `status` + stage exit-gate checklists |
| What is blocked and why? | Intake `risk_class` + `chris_gate` fields |
| What are the design-preparation recommendations? | Design-prep docs in the arc folder |
| Which ADRs ratify what? | `docs/adr/ADR-NNNN` files |
| What PRs have shipped for the arc? | `BACKLOG.md` `pr_refs` + `git log` |
| What debt has accrued? | `IMPLEMENTATION_DEBT.md` |
| What did the last session decide? | Last handoff doc |

If any question is un-answerable from repo artifacts, an
**artifact is missing** — file it as an implementation debt row
with `debt_type: PARTIAL_DISCHARGE` and `severity: HIGH`,
because the arc is not cold-resumable.

Cold-resume completeness is a **standing invariant** of IOS. Every
arc close (Stage 6) must verify it before ratifying the close.

## 15.9 Startup is a pre-stage bootstrap, not a lifecycle stage

Considered: should startup be added as "Stage 0" to the six-stage
arc lifecycle (§4.3)?

**Answer: no.** Rationale:

- Stages 1–6 describe the arc's *progression through work*.
  Startup describes *a session's entry into the arc*.
- Startup runs on **every session** touching the arc, regardless
  of stage — a Stage 4 build session runs startup exactly like
  a Stage 1 scoping session does. Making it Stage 0 would imply
  it runs once per arc, which is wrong.
- Startup is orthogonal to the six-stage exit gates.
- Modeling startup as pre-stage bootstrap preserves compatibility
  with Research OS §4, which itself is a pre-stage bootstrap for
  research sessions.

**Consequence.** Every session's opening message to Chris
declares which stage of which arc it is entering, plus the
outputs of §15.3–§15.5 (phase, arc, stage, gates, next action).
That declaration IS the startup handshake. It runs at the top
of the session, not inside any lifecycle stage.

## 15.10 Prohibited actions before startup completes

Before §15.1 Level C completes and §15.6 verification passes,
Claude MUST NOT:

- Plan or draft code changes.
- Edit any file under `docs/research/implementation/`.
- Modify `BACKLOG.md`, `IMPLEMENTATION_DEBT.md`,
  `OPEN_ARCS.md`, or `cross_domain_integration_audit.md`.
- Open a PR.
- Ratify anything.
- Retire any Rigby SIGN pin.
- Mint any Rigby SIGN pin.

Permitted actions during startup:

- Read files.
- Run diagnostic commands (`git status`, `git log`,
  `python manage.py showmigrations`, `verify_doc_claims`,
  `platform_config_tool overview`).
- Route Chris questions via PA chat (info-gathering only, no
  ratifications).
- Route Rigby questions via existing warm pins (info-gathering
  only).

## 15.11 Startup failure modes and recovery

| Failure | Symptom | Recovery |
|---------|---------|----------|
| IOS status is `draft` not `active` | Frontmatter check fails at §15.1 C.1 | Route Chris; IOS ratification required before any implementation session |
| `OPEN_ARCS.md` shows arc active but no arc pin | Drift check §15.6 fails | Route Chris; determine if arc silently stalled or if pin retirement was skipped |
| `BACKLOG.md` inconsistent | Rows with `status: IN_ARC` and empty `arc_ref` | Route Chris; do NOT auto-fix; may indicate uncommitted mid-arc work |
| Cross-domain audit stale (§14 refresh gap) | Drift check §15.6 fails | Route Chris; may block Stage 6 close on adjacent arcs |
| Fleet-key drift | 3-axis sweep finds prod-only consumers not in local | Escalate before Stage 4 opens |
| Migration already applied | `showmigrations` shows expected-new migration as applied | Verify not accidentally applied; may indicate parallel-session collision |
| ADR referenced but file missing | Startup fails at §15.6 rule 5 | Route Chris; either ADR authoring is queued or the reference is stale |

Every failure surfaces to Chris. No auto-remediation during
startup — surfacing failures IS the startup's value.

## 15.12 What startup improves

**Determinism.** Two independent Claude sessions given the same
repo state produce the same phase / arc / stage / gates / next-
action determination. Chris does not have to re-explain the
current arc's state each session.

**Context-drift avoidance.** §15.7 prohibits acting on remembered
context when a doc exists. §15.10 prohibits state mutations before
verification completes. Together they eliminate the class of bugs
where Claude "remembers" a decision that never persisted.

**Research OS compatibility.** Level A and Level B remain
Research OS's. Level C adds; it does not replace. Research OS
§4 unchanged. Research OS §5 router still classifies. Research
OS §7.1 truth hierarchy is extended (§15.2), not overwritten.

**Cold-resume guarantee.** §15.8 makes it a testable invariant:
every arc must be resumable from repo artifacts alone. If it is
not, the artifact gap is a first-class implementation debt row,
not a "we'll remember it next time" hope.

## 15.13 Interaction with Research OS §4

Research OS §4.1 Level A is unchanged. Research OS §4.2 Level B
is unchanged. Part 15 is Level C — a downstream extension routed
to by §5.1 class 4 (IMPLEMENTATION) and its sibling classes 2,
3, 6.

If Research OS §4 is ever revised such that Level B expects a
class-scoped bootstrap document per class (a Playbook-style
formalization), Part 15 becomes the reference implementation for
implementation-class Level B. No IOS content changes; the pointer
in Research OS §4.2 catches up.

## 15.14 Rigby SIGN pin lifecycle across phase transitions

Chris's session pin lives at `tools/pa_local.sh` `--conversation` line (grep-anchored, currently ~:411) (per S1300+
convention). Under Research OS, arc pins are minted at arc-open,
preserved through the arc, and retired at arc-close (Research OS
22-consecutive-arc SIGN-pin retirement discipline; IOS §7.2 for
implementation arcs mirrors this). IOS activation introduces a
new lifecycle question: what happens to the paused research
T-slot pin when IOS supersedes for an implementation session?

**Rule (v1.1 execution refinement).**

- **On IOS phase entry with a research pin still active in
  `:361`.** Preserve the research pin as a comment line above
  `:361` in the wrapper header (e.g.,
  `# paused-research-T4-Group1700: pa-44a6eb70d8814e34 (from S2699 close)`)
  and rotate `:361` to a **fresh IOS-scoped pin** minted via
  `session_tool.create_fresh label='ios-<phase>-<seq>'`.
  Example labels: `ios-part11-first-queue-ratification`,
  `ios-arc-open-I-0100`. This isolates IOS routing from
  paused-research context and prevents SIGN cross-contamination
  (per MEMORY rule
  `feedback_rigby_sign_worker_instability_recovery`).
- **During IOS Part 11 first-queue construction (pre-arc).** One
  IOS-scoped pin per Chris ratification cycle. Retire the pin at
  ratification close via `session_tool.retire force=true`
  (matching Research OS + IOS §7.2 SIGN-pin retirement
  discipline).
- **On implementation arc open (`I-NNNN`).** Mint an arc-scoped
  pin at Stage 1 open, matching Research OS + IOS §7.2. Preserve
  through Stages 1–6; retire at Stage 6 close.
- **On IOS phase exit** (Chris opens a Research OS command
  `Start / Continue / Close research group NNNN`). **Restore**
  the paused research pin — rotate `:361` back to the preserved
  value from the comment line, and delete the comment. If IOS
  minted a session-scoped pin that has not yet retired, retire
  it first per §11.2 Step 6 close discipline.
- **On terminal-only ratification (Chris explicit directive).**
  No pin minted; execution stays in shell + doc surface. Skip
  §15.14 pin lifecycle entirely for that specific ratification.

**Prohibitions.**

- Do NOT overwrite a paused-research pin without preserving it
  as a comment above `:361`.
- Do NOT retire a paused-research pin during IOS activity — it
  belongs to the paused research arc, not to IOS. Retirement is
  the sending arc's Stage 6 or xx99 canonical close author's
  responsibility.
- Do NOT reuse a paused-research pin for IOS routing — arc
  context bleeds across pins (violates SIGN isolation
  discipline; see MEMORY rule
  `feedback_rigby_sign_worker_instability_recovery`).
- Do NOT mint a fresh IOS pin before IOS Level C startup
  completes (§15.10 pin-mint prohibition remains in force during
  startup itself; the rule applies to post-startup implementation
  session work).

**Rationale.** First execution surfaced ambiguity when T4 Group
1700 Observability arc pin `pa-44a6eb70d8814e34` was live at
`:361` while IOS Part 11 Step 6 needed a Rigby route.
Alternatives evaluated:
- Reuse the T4 pin → mixes arc contexts (SIGN cross-contamination).
- Mint without preserving → loses the T4 resume path (Research
  OS arc-pin-durable-through-arc discipline broken).
- Retire the T4 pin → misappropriates the pin from the paused
  research arc.

Preserve + rotate is the only shape that satisfies all three
constraints simultaneously.

## 15.15 `00-START-NEXT-SESSION.md` ownership (v1.4)

`00-START-NEXT-SESSION.md` is the fresh-session entry point —
Level A universal bootstrap (Research OS §4.1) reads it in the
first three files of every new session. §15.3 phase-transition
supersession rule already establishes that a stale file does
not BLOCK implementation session start (fresh sessions apply
supersession during Level C step C.9 rather than defaulting to
the file's row). But "stale but not blocking" is not the same
as "current" — a stale file wastes fresh-session context on
disambiguating what the current state actually is.

Codified after v1.4 fresh-session Stage 2 simulation surfaced
that the file remained anchored on "IOS Part 11 first-queue
ratification COMPLETED; Seed PR PENDING Chris approval" while
main had already moved through IOS v1.1 / v1.2 / v1.3 / seed
PR merge / Arc I-0100 Stage 1 arc-open merge / P0 prep PR
opening — five session-scale state transitions un-reflected.

### 15.15.a Classification

`00-START-NEXT-SESSION.md` is **RAG-critical startup
infrastructure**, on par with the artifact types enumerated in
§12.5.b. Cascade discipline (§12.5.a v1.3) applies to any PR
that modifies it.

### 15.15.b Update-triggering PR types

Every PR of any of the following types MUST co-commit a
refreshed `00-START-NEXT-SESSION.md`:

- **Arc-open PR.** The PR that opens a new implementation arc
  (Stage 1 arc-open bundle).
- **P0 prep PR.** The PR that discharges IB-Q1-BOOT-01 or any
  future analogous P0 prep dependency (per §4.3 Stage 1 v1.2
  ADR corpus precondition Option (a)).
- **Stage-transition PR.** Any PR that flips the scoping doc
  frontmatter `stage:` field (per §4.3.0 discipline). This
  covers: Stage 2 opening PR, Stage 3 pre-flight completion,
  Stage 4→5 completion of the last planned PR, Stage 5→6
  verification-completion, Stage 6 close doc PR.
- **Arc-close PR.** The Stage 6 close doc PR.
- **IOS / Research OS / Playbook patch PRs.** Meta-process
  changes that alter the fresh-session experience directly
  (any patch to `IMPLEMENTATION_OPERATING_SYSTEM.md`,
  `RESEARCH_OPERATING_SYSTEM.md`, or `DOMAIN_RESEARCH_
  PLAYBOOK.md`).

Update-triggering PRs that do NOT touch `00-START-NEXT-SESSION
.md` are considered incomplete — the reviewer (Chris) is
authorized to request the refresh before merge.

### 15.15.c Refreshed-file schema

The refreshed `00-START-NEXT-SESSION.md` MUST contain:

1. **Phase** — one of `research` / `implementation` /
   `mixed` (with which phase leads). If `implementation`,
   note the active IOS status (`active vN.M`) and any
   supersession-of-research-trajectory rule per §15.3.
2. **Active arc** — arc ID + slug + scoping doc path.
3. **Current stage** — `1` / `2` / `3` / `4` / `5` / `6` per
   scoping doc frontmatter.
4. **`stage_state`** — enum value per §4.3.0.
5. **Next executable action** — one sentence naming the
   specific concrete next commit / PR / SIGN cycle. Not "keep
   working on the arc"; instead "author ADR-0002 (pa-write-
   shape-and-correlation-contract) per Arc I-0100 scoping doc
   §9.1 line 2 and route to Rigby SIGN Cycle 1 on arc pin."
6. **Active SIGN pin** — the arc-scoped SIGN pin (per §7.2
   isolation discipline), with its label + creation session
   + any paused-research-pin preservation note per §15.14.
7. **Pending PRs** — every open PR by number + title + state
   (`OPEN`, `REVIEW_REQUESTED`, `CHANGES_REQUESTED`,
   `MERGED_AWAITING_HOUSEKEEPING`). List merged-but-frontmatter
   -unflipped PRs as `MERGED_AWAITING_HOUSEKEEPING` so the
   next session knows housekeeping is due.
8. **Read as background** — pointer list to xx99 summaries,
   scoping doc, BACKLOG, DEBT, and other Level C step C.4-C.6
   loads specific to the active arc.
9. **Session ready check** — a numbered ordered list a fresh
   session runs BEFORE opening its planned Stage entry
   (mirrors the existing `SESSION READY CHECK` section
   pattern used in previous file revisions).

### 15.15.d Interaction with §12.5 cascade discipline

`00-START-NEXT-SESSION.md` diffs run the cascade per §12.5.a
because the file is RAG-critical per §15.15.a. Cascade evidence
block per §12.5.d appears in the update-triggering PR's body
alongside any other RAG-critical artifact evidence. If the PR
touches ONLY `00-START-NEXT-SESSION.md` and no other artifact
(rare, but possible for pure housekeeping refreshes at Stage
transition boundaries), the cascade evidence block covers that
single file.

### 15.15.e Interaction with §15.3 supersession rule

§15.3 corollary "should be updated at IOS phase entry" is
now enforceable per §15.15.b. The rule remains that a stale
file does not block session start — but stale files are
progressively rarer as §15.15 discipline takes hold. Fresh
sessions should still apply §15.3 supersession as a safety
net during Level C step C.9, not as the primary reliance path.

### 15.15.f v1.4 dogfood

This v1.4 patch PR (which codifies §15.15) itself refreshes
`00-START-NEXT-SESSION.md` per §15.15.b (IOS patch PR type).
The refreshed file reflects: IOS `active v1.4`; active arc
`I-0100`; current stage `1`; `stage_state: p0-prep-in-flight`
(PR #2948 open, not merged); next executable action = merge
this v1.4 patch and #2948 in the correct order, then flip
frontmatter, then author ADR-0002; active SIGN pin
`pa-c5b235f7b15f45be`; pending PRs = #2948 (P0 prep) and this
v1.4 patch PR.

---


## A.1 Evidence base

This draft was authored 2026-07-06 by Claude Code, in response
to Chris's short command "start Implementation Operating System
design arc." Draft consumed:

- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (3814 lines,
  read §0–§5, §7.1, §8.1–§8.4, §8.10, §12–§15 in full; skimmed
  remainder)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (2037 lines, read
  §3 phase discipline + §11.1/§11.3 templates + §20 evolution
  policy + §21 short commands in full; skimmed remainder)
- `docs/research/ARCHITECTURE_INDEX.md` (§7 decision matrix +
  §8 timeline — TOC only)
- `docs/research/OPEN_ARCS.md` (S2500 current-state header —
  first 10 lines only, file is 353KB and dominated by narrative)
- `docs/research/platform/cross_domain_integration_audit.md`
  (frontmatter + §14 verifier_loop v1–v4 through S2400 close
  — first 80 lines)
- All 13 xx99 canonical summaries (Groups 1300, 1400, 1500,
  1600, 1700, 1800, 1900, 2000+, 2100, 2200, 2400, 2500, 2600
  — read via Explore agent parallel harvest; harvest output
  folded into §3.1 T0–T5 tier system, §3.1.b CX-P10 spec-complete
  handling, §5.1 rules 6–10 (F4-CANDIDATE / feature-flag consumer
  / beat-task ZERO-FIRE / mock-data prohibition / UNKNOWN
  honesty), §5.2 rules 7–9 (silent-degrade emission / field-name
  validation / verifier-loop pre-correction), §4.3 Stage 3
  rules 5–6 (D48 stability-probe / sub-agent verifier-loop
  scope), §12.3 CX-P1–P10 inventory, §12.4 T4 delegate ownership,
  §13 D11 + D12 open questions)
- CLAUDE.md + MEMORY.md (auto-injected)

## A.2 What this doc does NOT verify

- Whether the `docs/research/implementation/` tree already
  exists (§13 D1).
- Whether any existing PR or code already implements a would-be
  intake item (would require full BACKLOG construction — §13 D8).
- Whether Rigby's tool surface can accept `intake_tool` or
  `implementation_arc_tool` handlers (deferred to a subsequent
  IOS implementation arc).

## A.3 UNKNOWNs

- **U1.** ~~Exact CX-P count~~ RESOLVED via harvest: 10 patterns
  (CX-P1 through CX-P8 crystallized; CX-P9 and CX-P10 as
  pattern-candidates awaiting second-arc confirmation). See §12.3.
- **U2.** Exact Group 2699 close state (2699 canonical summary
  filesystem-present at draft time; verify committed / merged
  vs mid-flight branch).
- **U3.** Whether the "first-queue construction" produces a
  workable backlog or reveals structural gaps in IOS's intake
  schema (test at first-queue construction time, not now).
- **U4.** Whether the T0–T5 tier system carries the same
  Chris-recognized semantics for implementation work as it does
  for research work — the harvest confirmed T0–T5 as the
  canonical research language, but implementation may need a
  sub-taxonomy inside T3 for the S/M/L/XL PR-sizing dimension.

## A.4 What must be true for this doc to be canonical

- Chris ratifies D1–D10 with explicit answers.
- Rigby SIGN routed and folded (first cycle expected during
  drafting session, before this draft moves from `draft` →
  `active`).
- Companion anchors verified as reachable and non-drift.
- One implementation arc runs end-to-end under IOS; if it
  survives without needing an IOS emergency amendment, IOS
  v1 is validated.

## A.5 What this doc supersedes

Nothing. IOS is new. Research OS §8.4 IMPLEMENTATION contract
remains authoritative for individual PRs; IOS wraps the phase.

## A.6 What this doc anticipates being superseded by

- **IOS v2** after two implementation arcs surface codifiable
  patterns via their §8 methodology sections.
- The eventual dissolution of both Research OS and IOS into a
  unified `PLATFORM_OPERATING_SYSTEM.md` if operational scale
  demands single-tree governance. Not planned; noted as a
  possible future.

## A.7 Rigby SIGN record

Fresh isolation pin, single-batch × 4-Q cadence per S1300–S2400
established pattern (mirroring the parent-scoping SIGN cadence
IOS itself specifies at §7.2).

- **Cycle 1 (2026-07-06):** **CLOSED — 20 folds applied, no
  BLOCKED.** Fired on dedicated fresh SIGN isolation pin
  `pa-f9164418e56940ea` (`session_tool.create_fresh label='IOS v1
  SIGN cycle 1'`) after Group 2600 PA merge (PR #2937 at commit
  `e4dfa851`). All four questions returned SIGN-with-edits at
  Medium confidence. 20 discrete folds applied per §A.7.3 ledger.
  Cycle 2 not required per Rigby verdict pattern (no BLOCKED
  condition on any question; all edits structural/clarifying).
  **Pin retired 2026-07-06 at v1.2 close** via
  `session_tool.retire conversation_id=pa-f9164418e56940ea
  force=true` per Research OS 22-consecutive-arc SIGN-pin
  retirement discipline (FIRST SIGN-pin retirement under IOS;
  ripples the Research OS retirement pattern forward into
  implementation-phase governance).

### A.7.1 Cycle 1 pressure-test payload (4 questions)

**Framing.** You are Rigby, pressure-testing the v1 draft of
`docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`. The
IOS is a new process document. It does NOT replace the Research
OS; it wraps §8.4 IMPLEMENTATION at phase scale. It consumes
xx99 canonical summaries + `cross_domain_integration_audit.md`
and produces sequenced, safe, verifiable implementation arcs.

Please read the draft in full, then respond in single-batch
× 4-Q cadence per the S1300–S2400 established pattern. For each
question, return: verdict (SIGN-clean / SIGN-with-edits /
BLOCKED) + confidence (Low / Medium / High) + specific folds
+ file:line evidence where applicable.

**Q1 — Compatibility with Research OS.** Does IOS preserve
Research OS §7.1 truth hierarchy? Does it duplicate any rule
already in Research OS §8.4 or the Playbook §3 phase discipline?
Where does IOS overreach into research territory or under-invoke
existing contracts? Specifically: does §3.1 T0–T5 tier system
faithfully mirror the tier language used across the 13 xx99
canonical summaries, or does IOS invent semantics that the
research library will not recognize?

**Q2 — Safety of the intake schema and priority rubric.** Do
the §2.2 intake fields cover every real finding class in the
xx99 summaries + cross_domain audit? Is the §2.4 rejection
list complete? Does the §3.1 five-dimension scoring capture
the tradeoffs Chris actually cares about (revenue + attention
preservation + Rigby usability + prod risk + reversibility)?
Specifically: does §3.1.b's handling of CX-P10 spec-complete
items (skip Stage 2 ADR authoring) correctly distinguish them
from POSTURE-PENDING (CX-P4) items?

**Q3 — Repeatability of the arc lifecycle + gate discipline.**
Can two independent Claude sessions run Stages 1–6 identically
given the same intake set? Is the §5.1 pre-code gate list
(rules 6–10 folded from the harvest: F4-CANDIDATE, feature-flag
consumer, beat-task ZERO-FIRE, mock-data prohibition, UNKNOWN
honesty) enforceable at the human level, or does IOS need
automation (D11) to be trustworthy? Are the §9 anti-chaos
caps (3–8 findings per arc, ≤3,000 LOC, 3–8 sessions per arc)
grounded in observed research-arc cadence, or invented?

**Q4 — Chris ratification bandwidth + Rigby SIGN load
protection.** Does the §3.2 Chris ratification band matrix
correctly reserve Chris's attention for architecture / posture
/ blast-radius decisions and shield him from `SAFE_AUTONOMOUS`
churn? Does the §9.3 SIGN load ceiling (fresh pin per arc, two-pin
recovery, 3–4 findings per prompt) faithfully carry the
`feedback_rigby_sign_worker_instability_recovery.md` memory
rule forward into implementation-phase pacing? Are there
implementation-specific SIGN load risks the memory rule doesn't
cover (e.g., per-PR post-merge verification stacking on top of
per-arc pre-scoping SIGN)?

### A.7.2 Fire command (for Chris, post-2699-merge)

Once Group 2600 PA closes and the closing-Claude retires its
arc pin, Chris fires IOS SIGN Cycle 1 with:

```
python tools/pa_chat.py \
  "$(cat docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md \
      | awk '/^## A.7.1/,/^### A.7.2/')" \
  --tools \
  --conversation <fresh-pin-id>
```

… after minting a fresh SIGN pin via `session_tool.create_fresh
label='IOS v1 SIGN cycle 1'` and rotating `tools/pa_local.sh:342`
to the new pin.

At cycle close, retire the pin per MEMORY rule
`feedback_session_tool_retire_works.md` — `session_tool.retire
conversation_id=<pin> force=true`.

- **Cycle 2 (if required):** _Not required per Cycle 1 verdict._

### A.7.3 Cycle 1 fold ledger

| # | Question | Fold | IOS location touched |
|---|----------|------|----------------------|
| 1 | Q1 | Split §15.2 truth authority (§15.2.a — Runtime Tier 0 preserved) vs read priority (§15.2.b) | §15.2 |
| 2 | Q1 | Add explicit "Research OS §7.1 wins on conflict" clause inside §15.2 | §15.2 header |
| 3 | Q1 | §8.4 pointer discipline — remove verbatim restatement in §5.2 rule 1 | §5.2 rule 1 |
| 4 | Q1 | Add T0–T5 tier fidelity appendix with citation anchors | Appendix B |
| 5 | Q2 | Add `adr_ref`, `verification_method`, `owner`, `delegate_owner` schema fields | §2.2 |
| 6 | Q2 | Add 3 rejection conditions: already-shipped / no-affected-surfaces / multi-domain-without-audit | §2.4 |
| 7 | Q2 | Split "Impact" into "Revenue impact" + "Attention preservation" as separate scoring dimensions (score ceiling 25 → 30) | §3.1 |
| 8 | Q2 | CX-P10 hard criterion: `design_state: SPEC_COMPLETE` + `spec_ref` file:line required (replaces notes-marker approach) | §3.1.b + §2.2 |
| 9 | Q2 | Confirm §2.5 ADR corpus + ensure `adr_ref` in schema | §2.2 + §2.5 |
| 10 | Q3 | Stage 1 exit gate: scoping doc must include "Stage checklist snapshot" | §4.3 Stage 1 |
| 11 | Q3 | D11 elevated to two-wave scope (cascade CI + `ios_gate_check` command) | §13 D11 |
| 12 | Q3 | §9.2 caps labeled "v1 default hypotheses" with post-2-arc recalibration | §9.2 |
| 13 | Q3 | §5.0 term definitions block: consumer, owner-model-qualified, fleet-key surfaces, F4-CANDIDATE | §5.0 |
| 14 | Q3 | §15.6 rule 10 PR-state drift detection | §15.6 |
| 15 | Q3 | D11 flagged "strongly recommended before draft → active" for trustworthiness at scale | §13 D11 |
| 16 | Q4 | SAFE_AUTONOMOUS never applies to irreversible migrations / destructive changes / fleet-key deletions | §3.2 |
| 17 | Q4 | §9.4 Stage 5 verification cap (≤3 PRs/session) + verification debt tracking | §9.4 |
| 18 | Q4 | §7.2 Stage 3 SIGN mandatory conditions (migrations / fleet / auth / payments / CROSS_DOMAIN+low-reversibility) | §7.2 |
| 19 | Q4 | No-new-arc-while-verification-debt rule (also triggers on 2-consecutive drift failures) | §9.4 |
| 20 | Q4 | §9.5 Chris bandwidth ceilings labeled "observed defaults" with explicit override language | §9.5 |

---

# Appendix B — T0–T5 tier fidelity

IOS §3.1 adopts the T0–T5 tier system directly from xx99 canonical
summary language. This appendix pins the fidelity: the semantics
IOS assigns to each tier match the canonical phrasing used across
the research library.

**IOS uses the same labels.** Where implementation needs a
sub-taxonomy for engineering-effort estimation, IOS uses the S/M/L/XL
PR-sizing dimension (Part 6) — NOT a redefined tier. Tiers stay
faithful to xx99 usage.

| Tier | Canonical phrasing (representative citations) | IOS §3.1 use |
|------|---------------------------------------------|--------------|
| **T0 / Gate** | "Chris-gated meta-ADR or blocking prerequisite that must resolve before downstream work" — Content S1699 §8.1 (D65a/b/c/e four-axis ADR bundle); Observability S1799 §8.1 (Chris-gated posture decisions); Authority S1999 §8.1 (pre-P2 blockers). | Meta-ADR bundles; blocking prerequisites. |
| **T1 CRITICAL/HIGH** | "Post-arc architecture decision records (ADRs) unblocking downstream implementation. Ranked by architectural uncertainty × risk × flow impact." — Content S1699 §8.2 (20 items); Observability S1799 §8.2 (R1–R7); Auth S2499 §8.2. | Post-arc ADRs; unblocks runtime work. |
| **T2 MEDIUM** | "Design-preparation follow-ons and posture-tied design documents. Dependencies on T0/T1 resolution." — Content S1699 §8.3 (26 items); Observability S1799 §8.3; Auth S2499 §8.3. | Design-prep follow-ons; posture-tied. |
| **T3 LOW-MEDIUM** | "Bounded operational patches, nice-to-have clarity, non-blocking cleanup." — Content S1699 §8.4 (5 items per Cat F); Authority S1999 §8.4 (6 items). | Bounded ops patches; no ADR. |
| **T4 Cross-arc delegate** | "Remediation or follow-on explicitly delegated to a future arc's queue" — Content S1699 §8.5 (Sports + Revenue + Memory arc handoffs); Authority S1999 §8.4 T4. | Delegated to receiving arc. Owner = receiving xx99 author. |
| **T5 Optional / Low-priority** | "Cleanup PRs, documentation lineage, refinement with optional implementation." — Content S1699 §8.6 (F1/F4 cleanup). | Nice-to-haves; ad-hoc pickup. |

**Fidelity rule.** If a future xx99 canonical summary uses a
tier label with materially different semantics, IOS is the
downstream party — IOS §3.1 must update, not the xx99. Research
OS §7.1 Tier structure wins on conflict per §15.2.

---

# Appendix C — Suggested first three IOS-produced artifacts

Not intake items. These are IOS infrastructure that the first
implementation arc will need in place:

1. `docs/research/implementation/BACKLOG.md` — the intake register.
2. `docs/research/implementation/IMPLEMENTATION_DEBT.md` — the
   debt register.
3. `docs/adr/ADR-0001-establish-adr-corpus.md` — the ADR corpus
   bootstrap (recursive: an ADR that installs the ADR corpus).

Chris may direct the first implementation arc to include these
three artifacts as its scoping-doc first step, OR run a separate
`I-0000_ios_bootstrap` arc to produce them first. Deferred to
D8.

---

**END IMPLEMENTATION_OPERATING_SYSTEM.md v1 (draft).**
