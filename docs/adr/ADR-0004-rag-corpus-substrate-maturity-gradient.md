---
title: "ADR-0004 — RAG Corpus Substrate Maturity Gradient (PROVISIONAL)"
adr_id: ADR-0004
slug: rag-corpus-substrate-maturity-gradient
status: accepted
provisional: true
provisional_reason: "IB-2199-BOR-01 (RAG search_docs + kb_tool retrieval end-to-end verification) undischarged; post-ratification discharge required per Arc I-0200 P1 severability determination §6 constraint 2. Post-BOR-01 discharge OR any T-slot ship (T18/T19/T21/T22/T13/T26a/T27/T29 per §4 Consequences) triggers an ADR-0004-successor that may flip provisional → false."
authority: design-decision
proposed: 2026-07-07
ratified: 2026-07-07
ratifier: chris
chris_ratification: "Agree All" 2026-07-07 — Rigby SIGN Cycle 1 SIGN-with-edits MED-HIGH; three folds F19-F21 applied pre-Chris-ratification; verbatim seam statement + two-field PROVISIONAL frontmatter + per-slot T-slot enumeration + BOR-01 post-ratification clause + no runtime enforcement claims + Stage 5 documentation cross-check only + F20 forward-compat rule for ADR corpus consumers + F21 embedding cleanup de-speculation all ratified. ADR-0004 body drafting authorized post-design-prep-PR-merge per Chris directive 2026-07-07 following Stage 2 design-prep close.
supersedes: (none)
superseded_by: (none)
intake_id: IB-2199-T0-01
arc_ref: I-0200
design_prep: docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md
source_refs:
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md §1 line 74 (canonical seam statement — the classification codified here)
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md §1 line 76 (three-independent-incident evidence chain S1234 + S1802 + S2104 §14 F5 satisfying D2100.7 elevation criterion)
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md §1 line 78 (Chris D-verdict ratifications — D2100.1a/1b/2/3/4/5/6/7/8/9/10 at S2100 open + D2100.11 at S2102 close + 10-item S2104 close card)
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md §1 line 82 (T-slot follow-on queue — 2 T0/Gate + 6 T1 + 9 T2 + 2 T3; distributed across 6 arcs + Employee OS)
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md §1 line 84 (5 institutional-knowledge-layer acceptance criteria; runtime enforcement pending T18/T19/T21/T22/T13/T26a/T27/T29)
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md §3.1 seed row + §8 F1-F14 folds + §9.2 ADR checkpoint
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md §6 required ADR shape (5 authoring constraints — Chris "Agree All" ratified 2026-07-07)
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md (this ADR's canonical design source; Chris "Agree All" ratified Option 1 2026-07-07)
  - docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md §2 (second-arc selection ratification card)
  - docs/adr/ADR-0001-establish-adr-corpus.md §3.3 (frontmatter schema; §3.4 body-section template followed here) + §3.7 (coupling to intake IB-2199-T0-01)
  - docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md (frontmatter + body-section reference implementation)
  - docs/adr/ADR-0003-mission-runner-staged-enable-posture.md (frontmatter + body-section reference implementation)
reversibility: 5
  # See §6. This is a docs-only classification ADR. Rollback is
  # `git revert <merge_commit_sha>`; downstream consumers filtering on
  # `status: accepted` continue to surface pre-existing ADR-0001/2/3
  # unchanged. Zero DB migration; zero runtime code; zero feature flag
  # change; zero data-shape change; the additive `provisional:` +
  # `provisional_reason:` frontmatter fields are ignored by any consumer
  # that doesn't opt-in to reading them.
sign_cycle_1: complete 2026-07-07 — Rigby SIGN-with-edits MED-HIGH overall (Q1 SIGN-with-edits 0.84 + Q2 SIGN-clean 0.86 + Q3 SIGN-with-edits 0.77 + Q4 SIGN-with-edits 0.74); three folds F19 (§3.1 strict-verbatim seam — remove outer double-quotes) + F20 (§4.4 forward-compat rule — consumers must ignore unknown frontmatter keys) + F21 (§6 rollback step 4 de-speculate cleanup command existence + soften retrieval-impact claim) applied in-branch pre-Chris-ratification; awaiting Chris "Agree All" or fold-by-fold response
sign_cycle_1_pin: pa-1b76ee75adbf4031
companion_docs:
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md
  - docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md
  - docs/adr/ADR-0001-establish-adr-corpus.md
  - docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md
  - docs/adr/ADR-0003-mission-runner-staged-enable-posture.md
---

# ADR-0004 — RAG Corpus Substrate Maturity Gradient (PROVISIONAL)

## 1. Status

**Accepted** — Chris ratified 2026-07-07 via "Agree All" following Rigby SIGN Cycle 1 SIGN-with-edits MED-HIGH (Q1 SIGN-with-edits 0.84 + Q2 SIGN-clean 0.86 + Q3 SIGN-with-edits 0.77 + Q4 SIGN-with-edits 0.74). Three folds F19-F21 applied pre-Chris-ratification: F19 (§3.1 strict-verbatim seam — remove outer double-quotes) + F20 (§4.4 forward-compat rule — consumers MUST ignore unknown frontmatter keys) + F21 (§6 rollback step 4 de-speculate cleanup command + soften retrieval-impact claim). No BLOCKED verdicts; Cycle 2 not requested.

**PROVISIONAL** — `provisional: true` per frontmatter (see §3.3 semantics + §4.4 corpus schema extension).

**PROVISIONAL** — `provisional: true` per frontmatter. The classification codified here is design-layer-ratified but its runtime enforceability depends on the post-ratification discharge of `IB-2199-BOR-01` (RAG `search_docs` + `kb_tool` retrieval end-to-end verification). Post-BOR-01 discharge OR any T-slot ship named in §4 Consequences triggers an ADR-0004-successor that may flip `provisional: true` → `false`. Per Arc I-0200 P1 severability determination §6 constraint 2 (Chris "Agree All" ratified 2026-07-07).

### 1.1 Ratification lineage

This ADR is the Stage 2 output of Arc I-0200 (second production implementation arc under IOS active v1.5). Prior Chris ratifications along the arc chain:

- **2026-07-06 (RATIFICATION_2026-07-06_first_queue.md)** — Tier-band ratification of implementation backlog; `IB-2199-T0-01` admitted at T0 band level.
- **2026-07-07 (RATIFICATION_2026-07-07_second_arc_I-0200.md)** — Chris "Agree All" ratified second-arc selection (Rigby SIGN-with-edits MED with 8 folds F1-F8); contingency-gated seed `IB-2199-T0-01` DEFAULT with `IB-1999-T0-01` fallback.
- **2026-07-07 (I-0200_scoping.md Stage 1 exit)** — Chris "Agree All" ratified 6 SIGN folds F9-F14 (Rigby SIGN-with-edits MED-HIGH); Stage 1 exit-gate cleared.
- **2026-07-07 (I-0200_severability_determination.md P1 close)** — Chris "Agree All" ratified SEVERABLE outcome (Rigby SIGN-with-edits MED-HIGH with folds F15-F16); `IB-2199-T0-01` flipped `TRIAGED → IN_ARC (I-0200)`.
- **2026-07-07 (I-0200_design_prep_rag_corpus_substrate_maturity.md Stage 2 design-prep close)** — Chris "Agree All" ratified Option 1 (Rigby SIGN-with-edits MED-HIGH with folds F17-F18); ADR-0004 body drafting authorized per this ADR.

## 2. Context

### 2.1 Upstream research

Group 2100 RAG / Document Loading research arc (Sessions S2100–S2104 + S2199 canonical summary) closed 2026-07-05 with a Chris-ratified canonical seam statement at 2199 xx99 §1 line 74. The arc consumed a parent scoping doc + four child slots (P1 Corpus State + P2 Ingestion Pipeline + P3 Retrieval Authority FRAMEWORK + Governance Design + P4 Behavior Substrate Structured Observation + Integration) totalling ~9,200 lines of new evidence. Chris ratified 10 D-verdicts at S2100 open + D2100.11 at S2102 close + a 10-item close card at S2104 close (2199 xx99 §1 line 78).

The arc's central finding was that Rigby's RAG corpus at HEAD `5d16a662` had crossed the design threshold — Chris ratified the 8-axis retrieval authority framework (D2100.8), the hybrid metadata contract (D2100.9), the 5-state artifact lifecycle model (S2103 F7), the standing Corpus Health Score with phased rollout (D2100.10), and the D2100.7 elevation from hypothesis to provisional contract — but had NOT crossed the execution threshold. T18 (axis-scoring ranker), T19 (conflict-resolution engine), T21 (lifecycle state-machine), T22 (metadata contract validation), and T13 (dual-cascade resolution) all sat in Track A + Track B post-arc queues awaiting Chris-ratified execution PRs (2199 xx99 §1 line 82 T-slot follow-on queue).

### 2.2 The problem this ADR resolves

Without a platform-ADR-canonical codification of the maturity classification:

- **Downstream implementation arcs cannot cite the classification via a stable ADR-N reference.** They must cite `2199 xx99 §1 line 74` — a research-doc reference — as the canonical source, mixing research-authority and implementation-authority.
- **The T-slot execution PRs (T18/T19/T21/T22/T13/T26a/T27/T29) lack a platform-ADR anchor** naming them as prerequisites. A future contributor could ship one T-slot without ratifying design decisions from the others.
- **The PROVISIONAL posture** (captured in P1 severability determination §6 as a constraint imposed on this ADR) is not yet at ADR corpus level. Future ADR corpus consumers (Rigby SIGN preamble, doc-claim verifier, cross-arc audit refresh) cannot query "which ADRs are PROVISIONAL" without a corpus-level convention.

### 2.3 Design-preparation source

Per IOS v1.5 §4.3.a mandatory-design-prep rule + Chris-directed arc-scoped IOS §14.2 workflow refinement (recorded in design-prep §9.2 Provenance), this ADR's canonical design source is:

**`docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md`**

The design-prep document contains:
- §1 Context (incl. §1.2 Yes-required code-state read: RAG retrieval surfaces + docs cascade + ADR frontmatter conventions).
- §2 Q1–Q4 decision questions.
- §3 12 constraints C1–C12 sourced from P1 determination §6 + Chris directives + IOS + scoping doc anti-scope + LOCAL guardrail.
- §4 Three options × six-field consequence matrix (schema shape + backward compatibility + migration surface + Rigby tool-surface + runtime/storage + grep-discoverability).
- §5 Pressure test scoring matrix (12 constraints + 4 judgment criteria).
- §6 Verification implications (Stage 3 SKIPPED for docs-only ADR; Stage 5 documentation-cross-check-only interface).
- §7 Recommendation (Option 1 with sub-options 1(i)-1(iv)).
- §8 Alternatives considered.
- §9 Provenance (incl. §9.2 workflow-deviation recording).
- §10 Meta-methodology with codification candidates.

Rigby SIGN Cycle 1 on the design-prep returned SIGN-with-edits MED-HIGH; two folds F17 + F18 applied pre-Chris-ratification. Chris "Agree All" 2026-07-07 ratified Option 1. This ADR's §3 Decision, §4 Consequences, §5 Alternatives, and §6 Reversibility inherit from that analysis. Readers seeking the analytical work behind ratification should read the design-prep first.

### 2.4 What this ADR does NOT decide

- **The BOR-01 discharge outcome.** `IB-2199-BOR-01` (RAG `search_docs` + `kb_tool.semantic_search` retrieval end-to-end verification) remains `BLOCKED_ON_RESEARCH` per BACKLOG line 349. This ADR names BOR-01 as a post-ratification requirement but does not schedule or discharge it.
- **Individual T-slot execution timing.** T18 / T19 / T21 / T22 / T13 / T26a / T27 / T29 named as post-arc requirements but not scheduled here.
- **Whether the classification remains PROVISIONAL forever.** Post-BOR-01 discharge OR any T-slot ship can trigger an ADR-0004-successor.
- **Any runtime enforcement.** Per P1 determination §6 constraint 4 + Chris directive "No runtime code" carried forward from RATIFICATION_2026-07-07 §2 Axis 7.
- **Companion-row admission** for `IB-2199-T1-01` or `IB-CXP10-T1-03`. Per Chris directive "Do not admit companion rows."
- **The fallback path.** `IB-1999-T0-01` (Authority per-plane posture) fallback path was NOT triggered at P1 close (SEVERABLE determination held); that row remains `TRIAGED` for a future arc.

## 3. Decision

**Ratify the following maturity classification as a platform PROVISIONAL ADR.**

### 3.1 Canonical maturity classification statement

Verbatim from `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 line 74, ratified by Chris via "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05 (per Rigby SIGN Cycle 1 F19 fold: markdown blockquote preserves the source formatting; no outer double-quote wrapping — strict-verbatim to 2199 line 74):

> **The arc's principal finding is that Rigby's RAG corpus at HEAD `5d16a662` is a *design-governed corpus substrate — spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots — in transition toward runtime-governed institutional knowledge layer along the maturity gradient passive → spec-complete → execution-complete*.**

This is the canonical seam statement (2199 xx99 §5.1) synthesizing all four Group 2100 children per S2104 §17.3 + §20.1 defended-answer. **Not "passive search index" AND not "already governed at runtime."** The substrate has crossed the design threshold; it has NOT crossed the execution threshold.

### 3.2 Maturity gradient axes

Per 2199 xx99 §1 line 84:

> "**Runtime maturity classification arc-wide: DESIGN-COMPLETE + EVIDENCE-SUPPORTED at spec layer; EXECUTION-PENDING at runtime layer.** All 5 institutional-knowledge-layer acceptance criteria from parent §1 Q3 fold are SATISFIED at design layer... Chris ratified the design without ratifying execution timing; the arc closes at S2199 with the substrate at the **spec-complete threshold**, ready for post-arc execution PRs."

The five institutional-knowledge-layer acceptance criteria (from 2199 xx99 §1 line 84) that the substrate satisfies AT DESIGN LAYER:

1. Every canonical summary + closed child audit is embedded within cascade-close window — design-satisfied; enforcement pending T27 preamble gate.
2. Retrieval authority framework returns non-conflicting authorities for ≥95% of query classes — design-satisfied via S2103 F1 8-axis + F2 3-part conflict rule; runtime pending T18 / T19.
3. Superseded docs demoted or excluded from top-k retrieval for "current truth" queries — design-satisfied via S2103 F7 5-state lifecycle with Q11 STRENGTHEN DE-RANKED-not-EXCLUDED refinement; runtime pending T21.
4. Corpus health score is trackable + interpretable — design-satisfied via D2100.10 (c) standing-metric + S2104 §14.3 14-dimension list; runtime pending T29 phased rollout.
5. Freshness-bounds + authority conflicts surface visibly at retrieval time — design-satisfied via D2100.7 provisional contract + T26a Detect-and-Flag design; runtime pending T26a.

### 3.3 PROVISIONAL semantics

This ADR is **`status: accepted` + `provisional: true`** (two-field pattern). The distinction:

- **`status: accepted`** — Chris has ratified the classification content; downstream ADR corpus consumers filtering on `status: accepted` (search_docs, doc-claim verifier, cross-arc audit refresh) surface this ADR as canonical.
- **`provisional: true`** — the classification's runtime enforceability depends on a post-ratification research discharge (`IB-2199-BOR-01`). Consumers wanting to exclude PROVISIONAL ADRs from a "runtime-enforceable-only" query must add a `provisional == false` (or equivalently `provisional != true`) filter.

Post-BOR-01 discharge OR any T-slot ship (see §4 Consequences) can trigger an ADR-0004-successor. The successor may flip `provisional: true` → `provisional: false` (or omit the field entirely, reverting to the plain `status: accepted` shape). Successors use ADR-0001 §3.2 numbering + §3.6 lifecycle discipline.

## 4. Consequences

### 4.1 Post-arc T-slot execution PR requirements (Named per 2199 xx99 §8 T-slot follow-on queue)

The following T-slots are named as post-arc requirements. Each represents a separate future implementation PR (not authored in this ADR; not scheduled here; enumerated for platform-ADR canonical anchoring). Order per 2199 xx99 §1 line 82 T-slot listing:

- **T22** — D2100.9 metadata contract validation. **Track B canonical schema-shape gate that unblocks Track B execution.** Chief of Staff RECOMMEND schema; Rigby EXECUTE cascade. Named as the T0/Gate schema prerequisite for T18 / T19 / T21.
- **T13** — Dual-cascade F3 R3.5 resolution. **Track A canonical-path gate that unblocks Track A execution.** Chris D-verdict lean per S2102 close = (b) fold Path A into Path B.
- **T18** — Axis-scoring service + ranker. Chief of Staff RECOMMEND. Depends on T22.
- **T19** — Conflict-resolution rule engine. Chief of Staff RECOMMEND. Co-lands with T18.
- **T21** — Artifact lifecycle state machine (5-state model per S2103 F7). Rigby EXECUTE + Chief of Staff RECOMMEND. Depends on T22.
- **T26a** — Retrieval-surface consistency Detect-and-Flag. Rigby EXECUTE + Chief of Staff RECOMMEND. Directly discharges 2199 §14 F5 live-incident subject matter.
- **T27** — SIGN preamble corpus-hygiene gate. Rigby EXECUTE + Chief of Staff RECOMMEND with Chris ratification on threshold changes + TTL emergency override.
- **T29** — Corpus Health Score dashboard phased rollout (14 dimensions per S2104 §14.3). Rigby EXECUTE + Chief of Staff RECOMMEND.

Each T-slot is future implementation-arc scope. No T-slot is admitted to Arc I-0200. This ADR ratifies their identity as post-arc prerequisites; scheduling + Chris-per-slot ratification happen at the respective future arc-open events.

### 4.2 BOR-01 post-ratification requirement

**`IB-2199-BOR-01` (RAG `search_docs` + `kb_tool.semantic_search` retrieval end-to-end verification) discharge is a Stage-2-post-ratification requirement.**

Per Arc I-0200 P1 severability determination §6 constraint 2 (Chris "Agree All" ratified 2026-07-07): the classification codified in §3 is severable from BOR-01's verification harness at design-layer, but BOR-01 discharge is required before the classification's runtime enforceability question can advance. BOR-01 remains `BLOCKED_ON_RESEARCH` per BACKLOG line 349. Discharge requires a future research arc; this ADR does not schedule that discharge.

Until BOR-01 discharges:
- `provisional: true` remains in this ADR's frontmatter.
- Consumers wanting "runtime-enforceable-only" ADR queries must filter `provisional != true`.
- Any Stage 5 verification of this ADR is bounded to documentation cross-check only (per §5 verification interface below).

Post-BOR-01 discharge is one of two triggers that authorizes an ADR-0004-successor to remove or flip `provisional`. The other trigger is any T-slot ship from §4.1.

### 4.3 No runtime enforcement claims

This ADR codifies a **design-layer classification**. It does NOT claim:

- The 8-axis retrieval authority framework (D2100.8) is enforced at retrieval time.
- The D2100.9 hybrid metadata contract is validated at write-time.
- The 5-state lifecycle state-machine (S2103 F7) executes runtime state transitions.
- The Corpus Health Score dashboard (D2100.10) is deployed as a standing metric.
- Retrieval-surface disagreement is detected + flagged at query time (T26a design).

Each of the above is post-arc T-slot work (§4.1). The classification's "spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots" phrasing IS the ratified admission that runtime enforcement is deferred.

### 4.4 ADR corpus schema extension

This ADR introduces two additive optional frontmatter fields:

- **`provisional: bool`** — signals PROVISIONAL posture. Absent = not provisional (default).
- **`provisional_reason: str`** — free-text citation of the unmet condition. Required when `provisional: true`.

Per ADR-0001 §3.3 the enumerated optional-field list (`retracted`, `retraction_reason`, `sign_cycle`) is not explicitly declared exhaustive. The additive-field interpretation preserves backward compatibility: existing ADR-0001/0002/0003 do not use these fields; consumers filtering on `status: accepted` continue to surface all four ADRs unchanged. Consumers wanting to opt-in to PROVISIONAL awareness gain a new filter capability (`provisional == true` or `provisional_reason == populated`).

**If Rigby SIGN Cycle 1 on this ADR flags the schema extension as requiring an explicit ADR-0001 amendment,** the escalation path is: pause this ADR merge, author a companion PR to ADR-0001 §3.3 that explicitly permits additive optional fields (or explicitly enumerates the two new fields), Chris ratifies the amendment, then this ADR merges. Per design-prep §7.1 Sub-option 1(iv) guard clause.

**Forward-compatibility rule (per Rigby SIGN Cycle 1 F20 fold, ratification pending):** ADR corpus consumers **MUST ignore unknown frontmatter keys** rather than hard-fail on them. This preserves additive-field extensibility across ADR corpus growth without requiring a coordinated update of every consumer at each schema addition. If Chris wants this rule canonical at ADR-0001 level, the escalation path in the paragraph above serves as the codification vehicle — otherwise this rule holds as an ADR-0004-scoped consumer-side contract expressed in this ADR's Consequences.

### 4.5 Downstream ADR references

Once ratified, this ADR is the canonical citation target for any future arc or ADR referring to the RAG corpus maturity classification. Future ADRs SHOULD cite `ADR-0004 §3.1` (or the successor ADR-N if PROVISIONAL flips) instead of `2199 xx99 §1 line 74`. Research docs (xx99 canonical summaries, arc scoping docs) MAY continue to cite 2199 xx99 directly as their upstream evidence source.

### 4.6 Docs cascade + BACKLOG flip

At ADR PR merge:

- `docs/INDEX.md` gains a new ADR-0004 entry (autogen per `build_docs_index`).
- `docs/_provenance.json` gains ADR-0004 provenance metadata.
- ADR-0004 body embedded (~15–25 chunks estimated) via `embed_documents --all-unembedded`.
- BACKLOG.md `IB-2199-T0-01` row flips `IN_ARC (I-0200) → SHIPPED` with `pr_refs: #<ADR-0004-PR>` + `adr_ref: ADR-0004` per IOS §2.2 v1.4 Discipline B inline syntax.

No runtime code change. No DB migration. No feature flag introduction. No Celery task change. No API surface change.

## 5. Alternatives considered

Full alternative enumeration (inherited from design-prep §8; expanded here per ADR-0001 §3.4 body-section requirement).

### 5.1 Option 2 (rejected): Single-field PROVISIONAL + bundled T-slot reference

- Frontmatter: `status: provisional` (single field; enum extension of ADR-0001 §3.3 `status:` enum).
- T-slot naming: bundled reference — "See 2199 xx99 §8 for the enumerated list of 2 T0/Gate + 6 T1 + 9 T2 + 2 T3 items."

**Rejected because:**

- **Blast radius SUBSYSTEM.** Extending the `status:` enum ripples through downstream consumers filtering on `status: accepted`. Consumers regress silently (they no longer surface ADR-0004 unless they explicitly add `provisional` to their filter).
- **Reversibility 3** (per ADR-0001 §3.5 scale) vs Option 1's reversibility 5. Revert can restore the enum content in ADR-0001 but downstream corpus consumers may have already read the `status: provisional` value into their filter state; a full revert would leave latent code paths that reference the removed enum value.
- **Loses per-slot T-slot grep clarity.** `grep 'T22' docs/adr/ADR-0004-*.md` returns hit under Option 1's per-slot enumeration; requires reading 2199 §8 pointer under Option 2's bundled reference.

### 5.2 Option 3 (rejected): Two-field PROVISIONAL + bundled T-slot reference

- Frontmatter: same as Option 1 (`status: accepted` + `provisional: true`).
- T-slot naming: bundled reference (same as Option 2).

**Rejected because:** No schema advantage over Option 1 (same two-field pattern), loses C3 + C9 per-slot grep clarity from bundled reference. No compensating gain.

### 5.3 Custom classification wording (rejected)

Chris-refined re-write of 2199 xx99 §5.1 (e.g., different metaphor for the maturity gradient, different terminology for the axes).

**Rejected per anti-scope C6** (design-prep §3 constraints table): 2199 xx99 §5.1 canonical seam statement is already Chris-ratified via "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05. Re-opening the wording violates Arc I-0200 scope and would nullify the SEVERABLE severability determination that hinged on the ratified content being verbatim-adoptable.

### 5.4 Skip PROVISIONAL marker entirely (rejected)

Mark this ADR `status: accepted` without any `provisional:` field.

**Rejected because:** violates Arc I-0200 P1 severability determination §6 constraint 1 (Chris "Agree All" ratified 2026-07-07). Under this rejection path, the ADR would silently assert runtime enforcement is possible before BOR-01 discharge — which is precisely the claim BOR-01 is scheduled to test. Skipping PROVISIONAL erases the audit trail of the design-vs-runtime split.

### 5.5 Skip T-slot naming entirely (rejected)

Rely solely on 2199 xx99 §8 for post-arc requirements without naming T-slots in this ADR.

**Rejected per P1 determination §6 constraint 3** (Chris "Agree All" ratified 2026-07-07). Under this rejection path, this ADR would fail the "platform-anchor" role — a future contributor could ship one T-slot without a stable ADR reference to the classification's runtime-enforcement dependency structure.

### 5.6 Bundle this ADR with a T-slot ratification (rejected)

Ship ADR-0004 alongside a T-slot execution PR (e.g., T22 metadata contract validation runtime code).

**Rejected because:** violates Chris directive "No runtime code" carried forward from RATIFICATION_2026-07-07 §2 Axis 7 + Stage 2 directive 2026-07-07 + design-prep §3 constraint C7. Also violates IOS §4.3 Stage 2 single-decision-per-ADR discipline (each ADR ratifies one design decision; T-slot implementation is a separate future ADR track).

### 5.7 Defer this ADR until BOR-01 discharge lands (rejected)

Wait for a future research arc to discharge BOR-01, then author a non-PROVISIONAL ADR-0004.

**Rejected because:** would flip the I-0200 SEVERABLE determination to NOT SEVERABLE de-facto, re-opening a settled ratification. Chris ratified SEVERABLE 2026-07-07 with the PROVISIONAL shape as the accepted trade-off. Deferring would also unbind `IB-2199-T0-01`'s `IN_ARC (I-0200)` status and require a full ratification-chain rewind.

### 5.8 CX-P10 direct-ratification path (rejected)

Per IOS §3.1.b, CX-P10 items (`design_state: SPEC_COMPLETE` with populated `spec_ref` field) can skip Stage 2 ADR authoring — the spec IS the ADR.

**Rejected because:** `IB-2199-T0-01` at HEAD has no `spec_ref` column populated in BACKLOG.md. Per §3.1.b downgrade rule, absent `spec_ref` the item is not admissible as CX-P10; downgrade to normal `NEEDS_ADR` path. This ADR IS the required NEEDS_ADR discharge.

## 6. Reversibility

**Reversibility scale (per ADR-0001 §3.5): 5 (trivially reversible).**

Rollback method:

1. `git revert <ADR-0004-merge-commit-sha>` — removes ADR-0004 file + cascade artifacts + BACKLOG row flip.
2. BACKLOG.md `IB-2199-T0-01` unflip `SHIPPED → IN_ARC (I-0200)` (or `TRIAGED` if arc is re-opened) via the revert.
3. `docs/INDEX.md` + `docs/_provenance.json` unflip via revert (or via re-run `build_docs_index` + `build_docs_provenance`).
4. `DocumentEmbedding` rows for the removed file — orphan cleanup discipline per Rigby SIGN Cycle 1 F21 fold: if a cleanup management command exists at revert time (name TBD; not verified at authoring), run it; otherwise leave as acceptable low-severity storage residue. The retrieval-impact of orphan embeddings is not asserted here — post-BOR-01 discharge or a dedicated corpus-hygiene research arc would clarify whether orphan chunks materially affect retrieval quality.

**No irreversible operations. No DB migration. No feature flag change. No runtime code change. No data-shape change.**

Rollback triggers:

- Rigby SIGN Cycle 1 on this ADR returns BLOCKED verdict AFTER Chris ratification (unlikely given design-prep pre-SIGN).
- ADR-0001 §3.3 schema extension flagged as requiring explicit ADR-0001 amendment per §4.4 escalation path.
- Any downstream ADR consumer regresses on the additive `provisional:` field (e.g., a doc-claim verifier that hard-fails on unknown frontmatter fields).
- Chris explicit override.

Post-rollback state:
- `IB-2199-T0-01` returns to `IN_ARC (I-0200)` (Arc I-0200 stays active; a fresh ADR-0004 draft can start).
- Arc I-0200 scoping doc §10 CURRENT_GATE flips back to "Stage_2_design_prep_RATIFIED_pending_design_prep_PR_merge_then_ADR-0004_body_drafting" (post-P1-close analog state).

## 7. Provenance

- **Author.** Claude Code, Arc I-0200 Stage 2 ADR-0004 body drafting session (branch `docs/arc-i0200-adr-0004-body`), 2026-07-07.
- **Design-prep source (canonical).** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md` — Chris "Agree All" ratified Option 1 2026-07-07 (Rigby SIGN-with-edits MED-HIGH; folds F17 + F18).
- **Rigby SIGN Cycle 1 target.** Pending on arc-scoped pin `pa-1b76ee75adbf4031` per IOS §7.2 single-batch × 4-Q cadence. Q-set will pressure-test §3 Decision content fidelity + §4 Consequences per-slot enumeration + §4.4 ADR corpus schema extension + §5 Alternatives inheritance + §6 Reversibility rollback triggers.
- **Chris ratification target.** After Rigby SIGN + fold application + Chris review of ratification card.
- **Anti-context-drift.** This ADR is authored by session slug `claude-arc-i0200-adr-0004-body`; if a future session remembers different §3.1 classification wording or §4.1 T-slot list than what appears here, this doc is truth per IOS §15.7.

### 7.1 Consumed sources (verified at HEAD `c87878dd`)

- 2199 xx99 §1 line 74 (canonical seam statement — verbatim quoted at §3.1).
- 2199 xx99 §1 line 76 (three-independent-incident evidence chain — implicit in §2.1 upstream research).
- 2199 xx99 §1 line 78 (D-verdict summary — §1.1 ratification lineage + §2.1).
- 2199 xx99 §1 line 82 (T-slot follow-on queue — §4.1 per-slot enumeration order).
- 2199 xx99 §1 line 84 (5 acceptance criteria — §3.2 maturity gradient axes verbatim).
- Arc I-0200 scoping doc §3.1 seed row + §7.1 anti-scope + §8 F1-F14 folds + §9.2 ADR checkpoint.
- Arc I-0200 P1 severability determination §6 required ADR shape (5 authoring constraints — Chris "Agree All" ratified 2026-07-07); §4.3 F15 lock.
- Arc I-0200 design-prep §3 constraints C1-C12 + §7 recommendation Option 1 + §7.1 sub-options 1(i)-1(iv) + §8 alternatives + §9.2 workflow deviation.
- RATIFICATION_2026-07-07_second_arc_I-0200.md §2 Axis 2 + Axis 5 + Axis 7.
- ADR-0001 §3.3 frontmatter schema + §3.4 body-section template + §3.7 coupling to intake row.
- ADR-0002 + ADR-0003 as reference implementations of ADR corpus conventions.
- BACKLOG.md `IB-2199-T0-01` row (currently `IN_ARC (I-0200)` per P1 close).

### 7.2 IOS §4.3.a workflow deviation carrying forward from design-prep §9.2

This ADR is authored under Chris-directed arc-scoped IOS §14.2 workflow refinement: SIGN design-prep independently → Chris ratifies design-prep → author ADR body → SIGN ADR body → Chris ratifies ADR body → merge ADR PR. Default IOS §4.3.a collapses design-prep SIGN into ADR SIGN. Recorded in design-prep §9.2 Provenance; CC-1 codification candidate for IOS v-next §4.3.a variant (single trigger; awaiting second arc).

## 8. Follow-on ADRs (potentially blocked on this one)

- **ADR-N (successor to ADR-0004) — Post-BOR-01 discharge OR post-T-slot-ship maturity classification refresh.** Triggered by either (a) `IB-2199-BOR-01` discharged via future research arc → BOR-01 verification harness results inform whether the classification flips to `provisional: false`, OR (b) any T-slot from §4.1 ships → classification's "execution-pending" axis narrows for that specific T-slot's substrate component. Successor uses `supersedes: ADR-0004` frontmatter.
- **ADR-N (companion to ADR-0001) — Optional ADR-0001 §3.3 schema amendment.** Only triggered if Rigby SIGN Cycle 1 on this ADR flags the additive `provisional:` + `provisional_reason:` fields as requiring an explicit ADR-0001 amendment. Escalation path per §4.4.
- **ADR-N (Track A execution) — T13 dual-cascade F3 R3.5 resolution ratification.** Named as post-arc requirement (§4.1); when authored, MUST cite ADR-0004 §4.1 T13 entry.
- **ADR-N (Track B execution) — T22 D2100.9 metadata contract validation ratification.** Named as post-arc requirement (§4.1); when authored, MUST cite ADR-0004 §4.1 T22 entry (schema prerequisite for T18 / T19 / T21).
- **Additional T-slot ratifications** for T18 / T19 / T21 / T26a / T27 / T29 — each a separate future ADR track.
