---
title: "Arc I-0200 — Design Preparation for ADR-0004: RAG Corpus Substrate Maturity Gradient (PROVISIONAL)"
authority: design-preparation
status: active
arc_id: I-0200
arc_slug: rag_corpus_substrate_maturity
adr_target: ADR-0004
adr_slug_reserved: rag-corpus-substrate-maturity-gradient
session_authored: 2701
authored: 2026-07-07
authored_by: claude-code (Arc I-0200 Stage 2 opening)
source_finding_refs:
  - 2199 xx99 §1 line 74 (canonical seam statement — "design-governed corpus substrate; spec-complete via P3; evidence-supported via P4; execution-pending via post-arc T-slots; in transition toward runtime-governed institutional knowledge layer along the maturity gradient passive → spec-complete → execution-complete")
  - 2199 xx99 §1 line 76 (three-independent-incident evidence chain S1234 + S1802 + S2104 §14 F5 satisfying D2100.7 elevation criterion)
  - 2199 xx99 §1 line 78 (D-verdict summary — 10 D-verdicts at S2100 open + D2100.11 at S2102 close + 10-item S2104 close card)
  - 2199 xx99 §1 line 82 (T-slot follow-on queue — T22 D2100.9 metadata contract validation + T13 dual-cascade F3 R3.5 + 6 T1 + 9 T2 + 2 T3 distributed across 6 arcs + Employee OS)
  - 2199 xx99 §1 line 84 (5 institutional-knowledge-layer acceptance criteria all satisfied at design layer; runtime enforcement pending T18/T19/T21/T22/T13/T26a/T27/T29)
  - Arc I-0200 scoping doc §3.1 seed row (IB-2199-T0-01 default seed; NEEDS_ADR; SPEC_COMPLETE)
  - Arc I-0200 scoping doc §8 F1–F14 folds (selection SIGN + Stage 1 SIGN)
  - Arc I-0200 scoping doc §9.2 ADR checkpoint (default path → ADR-0004 target)
  - Arc I-0200 P1 severability determination §6 required ADR shape (5 authoring constraints — PROVISIONAL Option a/b + BOR-01 clause + T-slot naming + no runtime enforcement + Stage 5 doc-cross-check-only)
  - Arc I-0200 P1 severability determination §4.3 (F15 Stage 5 verification scope lock)
  - Arc I-0200 P1 severability determination §5.1 (Rigby SIGN Q3 non-contradiction cross-check pointers to 2199 §14 F5 + §2.2 + §8)
  - BACKLOG.md `IB-2199-T0-01` post-P1-close (IN_ARC (I-0200); design_state SPEC_COMPLETE; risk_class NEEDS_ADR)
sign_cycle_1: complete 2026-07-07 — Rigby SIGN-with-edits MED-HIGH overall (Q1 SIGN-clean 0.86 + Q2 SIGN-with-edits 0.78 + Q3 SIGN-clean 0.88 + Q4 SIGN-with-edits 0.74); two folds F17 (C9 downgrade to recommended-ops-constraint) + F18 (Stage 5 verification interface tool-realistic; deliverable_tool.list replaced with repo_tool.search + search_docs + kb_tool + repo_tool.read_file) applied in-branch pre-Chris-ratification
sign_cycle_1_pin: pa-1b76ee75adbf4031
chris_ratification: "Agree All" 2026-07-07 — ratified Option 1 (verbatim seam statement + two-field PROVISIONAL frontmatter + per-slot enumerated T-slots); C1–C12 with C9 as recommended ops/grep constraint (not ratified requirement); Stage 5 documentation cross-check only; verification interface must use repo/RAG-native tools (not deliverable_tool filesystem assumptions); Option 2 rejected (SUBSYSTEM blast radius + reversibility 3); Option 1 accepted (LOCAL blast radius + reversibility 5); §9.2 workflow-deviation recording accepted; ADR-0004 body drafting authorized after this ratification. Design-prep PR must merge before ADR-0004 body drafting opens.
companion_docs:
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md
  - docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md
  - docs/adr/ADR-0001-establish-adr-corpus.md
  - docs/topics/personal-assistant.md
  - docs/KNOWLEDGE_PIPELINE.md
verifier_loop: |
  Authored 2026-07-07 by Claude Code at Arc I-0200 Stage 2 opening
  ceremony per Chris explicit directive "Open Stage 2. Perform only
  the Stage 2 entry actions... Create the Stage 2 Design Prep document
  as the first-class artifact... Route the completed Design Prep
  through Rigby SIGN. Return the SIGN package for Chris ratification
  before any ADR drafting. Stop after the Design Prep and Rigby SIGN."
  Assessment: Chris's directive represents an arc-scoped workflow
  refinement of IOS §4.3.a — the canonical §4.3.a rule states
  "Design-prep artifacts are NOT independently SIGN'd — they are
  pressure-tested BY the SIGN cycle on the downstream ADR." Chris
  directive overrides this per IOS §14.2 Chris refinement-authority
  prerogative for Arc I-0200's Stage 2. Rationale (inferred from
  P1 close card constraint density + PROVISIONAL ADR shape novelty):
  de-risk ADR-0004 body authoring by pressure-testing the design-prep
  first. Codification candidate for IOS v-next §4.3.a variant:
  "arc-scoped workflow overrides recognized as first-class §14.2
  refinement instances; recording of the deviation required in
  design-prep §9 Provenance."
  Investigation of upstream code state was Yes-required per §4.3.a
  §1 Context rule (analog to Arc I-0100 ADR-B design-prep §1). For
  a docs-only maturity classification ADR the "code state" is the
  RAG retrieval-surface implementation code + docs cascade + BACKLOG
  authority binding — read pre-drafting (see §1 below).
  Anti-context-drift: this doc is authored by session slug
  `claude-arc-i0200-stage2-open-design-prep`; if a future session
  remembers different §4 option semantics or §7 recommendation than
  what appears here, this doc is truth per IOS §15.7.
---

# ADR-0004 Design Preparation — RAG Corpus Substrate Maturity Gradient (PROVISIONAL)

**Purpose.** Author the canonical design-prep artifact for `ADR-0004-rag-corpus-substrate-maturity-gradient.md`. Per IOS v1.5 §4.3.a mandatory-design-prep rule + Arc I-0200 P1 severability determination §6 required ADR shape, this file scopes the design decisions ADR-0004 will resolve BEFORE the ADR body is drafted.

**Scope.** Four coupled decisions (see §2):

1. **Canonical text of the maturity classification statement.**
2. **PROVISIONAL frontmatter pattern.**
3. **Post-arc T-slot execution PR naming semantics.**
4. **ADR title + slug + verification-method interface for Stage 5.**

**Non-scope.**

- Discharge of `IB-2199-BOR-01` (RAG `search_docs` vs `kb_tool.semantic_search` retrieval-surface verification). Out-of-scope per P1 SEVERABLE determination §6 constraint 2 (BOR-01 is Stage-2-post-ratification requirement, not in-arc).
- Authoring or ratifying any of the T-slot execution PRs (T18/T19/T21/T22/T13/T26a/T27/T29). Named in ADR-0004 as post-arc requirements only.
- Runtime enforcement of the maturity classification (e.g., blocking retrieval, changing `search_docs` return shape). Anti-scope per Chris directive "No runtime code."
- Companion-row admission for `IB-2199-T1-01` or `IB-CXP10-T1-03`. Anti-scope per Chris directive "Do not admit companion rows."
- Re-negotiating 2199 xx99 §5.1 canonical seam statement wording. Chris ratified it via "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05; re-opening is anti-scope for I-0200.
- Changing the fallback-path arc slug or `IB-1999-T0-01` status. P1 close held SEVERABLE; fallback path not triggered.

**Workflow deviation from IOS §4.3.a (Chris-directed).** Per §4.3.a default, design-prep is NOT independently SIGN'd. Chris's Stage 2 directive 2026-07-07 explicitly overrides: SIGN this design-prep on `pa-1b76ee75adbf4031`, return SIGN package, Chris ratifies BEFORE any ADR body drafting. Recorded in Provenance §9 as arc-scoped IOS §14.2 refinement.

---

## 1. Context

### 1.1 What ADR-0004 must decide

ADR-0004 codifies the platform's ratified maturity classification of Rigby's RAG corpus substrate. The classification content is already Chris-ratified via 2199 xx99 §1 line 74 verbatim + 10-item S2104 close card 2026-07-05. What ADR-0004 adds is:

- Platform-ADR-canonical citation (ADR-N stable reference for downstream arcs).
- PROVISIONAL semantics reflecting `IB-2199-BOR-01` undischarged state.
- Explicit naming of the T-slot execution PRs as post-arc requirements.
- Stage 5 documentation-cross-check-only verification-method interface (per F15 lock).

### 1.2 Current code state (Yes-required per §4.3.a §1)

For a docs-only maturity classification ADR, "code state" comprises the RAG retrieval-surface implementation + docs cascade + ADR frontmatter conventions. Read pre-drafting:

- **Retrieval surfaces** — `search_docs` handler + `kb_tool.semantic_search` handler live in `core/services/tool_dispatcher.py` (search_docs registered per PA tool schema; kb_tool aggregates semantic search). Both were the subject of 2199 §14 F5 live-incident.
- **Docs cascade pipeline** — `python manage.py build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `embed_documents --all-unembedded` + `build_docs_provenance`. This is the substrate that keeps ADR content RAG-visible for Rigby SIGN/search. Currently at HEAD `c39db4394` (post-P1 merge): 2981 docs indexed, 34,727 chunks, 2430 docs with provenance.
- **ADR corpus frontmatter conventions** — `docs/adr/ADR-0001-establish-adr-corpus.md` (P0 prep from Arc I-0100 PR #2948) defines the ADR body-section requirement, `status:` enum (`draft` | `proposed` | `accepted` | `superseded` | `deprecated` | `rejected`), and cross-reference discipline. ADR-0002 and ADR-0003 (Arc I-0100 ADR-B and ADR-A) instantiate these conventions with `status: accepted`. Neither ADR-0002 nor ADR-0003 uses a `provisional:` boolean field — that would be new-to-corpus if Option (a) is picked (see §4).
- **`docs/topics/personal-assistant.md`** — narrates PA tool surfaces including retrieval; downstream reader of ADR-0004 if it lands.
- **`docs/KNOWLEDGE_PIPELINE.md`** — existing RAG narrative; predates 2199 xx99; may need refresh post-ADR-0004.
- **BACKLOG.md row `IB-2199-T0-01`** at HEAD: status `IN_ARC (I-0200)`; design_state `SPEC_COMPLETE`; risk_class `NEEDS_ADR`; affected_surfaces `docs/adr/`, `RAG substrate`. Per §3.1.b `spec_ref` field is absent → NEEDS_ADR path, not CX-P10 skip. ADR-0004 is required.

### 1.3 Observability / correctness / compliance gap

Without ADR-0004:

- Downstream implementation arcs cannot cite the ratified maturity classification via a stable ADR-N reference. They must cite `2199 xx99 §1 line 74` — a research-doc reference — as the canonical source, which mixes research-authority and implementation-authority.
- The T-slot execution PRs (T18/T19/T21/T22/T13/T26a/T27/T29) lack a platform-ADR anchor naming them as prerequisites. A future contributor could ship one T-slot without ratifying design decisions from the others.
- The PROVISIONAL posture is captured in P1 severability determination §6 but not yet at ADR corpus level. Future ADR corpus consumers (Rigby SIGN preamble, doc-claim verifier, cross-arc audit refresh) cannot query "which ADRs are provisional" without a corpus-level convention.

### 1.4 What ADR-0004 does NOT decide

- The BOR-01 discharge outcome. That's a research task requiring a separate research arc.
- Individual T-slot execution timing. Named as post-arc but not scheduled.
- Whether the classification will remain PROVISIONAL forever. Post-BOR-01 discharge OR any T-slot ship can trigger an ADR-0004-successor that flips PROVISIONAL to ACCEPTED-non-provisional.

---

## 2. Decision questions

**Q1** What is the canonical text of the maturity gradient classification that ADR-0004 codifies?

**Q2** What PROVISIONAL frontmatter pattern does ADR-0004 use — Option (a) two-field (`status: accepted` + `provisional: true` + `provisional_reason`) or Option (b) single-field (`status: provisional` + explicit ADR §1 definition)?

**Q3** How does ADR-0004 name the T-slot execution PRs (T18/T19/T21/T22/T13/T26a/T27/T29) as post-arc requirements — enumerated in Consequences section with per-slot dependency notes, or bundled as "all post-arc T-slots from 2199 §8 T-slot follow-on queue"?

**Q4** What is the ADR-0004 title + slug + Stage 5 verification-method interface (documentation cross-check only per F15 lock)?

---

## 3. Constraints

Hard requirements the ADR-0004 body must respect. Sources cited per constraint.

| # | Constraint | Source | Load-bearing implication |
|---|-----------|--------|-------------------------|
| C1 | PROVISIONAL marker in frontmatter | P1 determination §6 constraint 1 (Chris-ratified 2026-07-07) | Rules out plain `status: accepted` without provisional signal. Q2 picks Option (a) or (b). |
| C2 | Explicit "BOR-01 discharge is Stage-2-post-ratification requirement" clause in Consequences | P1 determination §6 constraint 2 | ADR Consequences section MUST name BOR-01 by intake_id; ADR must not claim runtime enforcement is possible before BOR-01 discharge. |
| C3 | T-slot execution PRs named as post-arc requirements | P1 determination §6 constraint 3 | ADR MUST name T18 / T19 / T21 / T22 / T13 / T26a / T27 / T29 as separate post-arc requirements; Q3 picks enumeration semantics. |
| C4 | No runtime enforcement claims | P1 determination §6 constraint 4 | ADR body cannot state "the framework is enforced at retrieval time" or similar; it can only state the classification (design-layer). |
| C5 | Stage 5 verification scope = documentation cross-check only | P1 determination §6 constraint 5 + F15 lock | Q4 verification-method interface bounded to git-log / file-read / BACKLOG status-column checks. No mgmt-command execution; no live-index query. |
| C6 | Verbatim adoption of 2199 xx99 §5.1 canonical seam statement | Scoping doc §7.1 anti-scope bullet 3 ("Re-negotiating 2199 xx99 §5.1 canonical seam statement wording. Chris ratified it… re-opening is anti-scope for I-0200") | Q1 cannot re-word the classification. ADR-0004 body IS the seam statement + provenance + Consequences. |
| C7 | No runtime code changes | Chris directive at RATIFICATION_2026-07-07 §2 Axis 7 + Stage 2 directive 2026-07-07 | Anti-scope bullet enforcement. ADR ships as docs-only. |
| C8 | No companion-row admission | Chris directive 2026-07-07 | Companion rows (`IB-2199-T1-01`, `IB-CXP10-T1-03`) do NOT enter ADR-0004 scope. |
| C9 | **[Recommended ops constraint, not ratified requirement — per Rigby F17 fold on this design-prep]** ADR title contains "PROVISIONAL" for grep-discoverability | Rigby SIGN Cycle 1 Q2 fold on this design-prep (author-side recommendation for maintenance ergonomics; not a P1-determination-ratified constraint) | ADR-0004 file name + `title:` frontmatter both surface PROVISIONAL. **Elevatable to ratified requirement by Chris explicit directive; otherwise treated as design-prep-author recommendation.** |
| C10 | LOCAL-only operating model | PR #2972 guardrail (Arc I-0100 close) | No prod verification is planned in Stage 5; guardrail carries forward. |
| C11 | Cascade co-location per ADR PR | IOS v1.3 §12.5.a | ADR PR must run 5-step cascade locally + include §12.5.d evidence block. (Ships when ADR PR opens — not for this design-prep PR.) |
| C12 | Fallback path not re-opened | P1 SEVERABLE ratification 2026-07-07 | ADR-0004 does not reference `IB-1999-T0-01` as an in-arc fallback; that path is retired for I-0200. |

---

## 4. Options × consequence-field matrix

Three options for ADR-0004 shape. Consequence fields per IOS §4.3.a required minimum (schema shape, backward compat, migration surface, Rigby tool-surface impact, runtime/storage/volume implications) + Q9 grep-discoverability field added per C9.

### Option 1 — Verbatim seam statement + PROVISIONAL Option (a) two-field frontmatter + per-slot enumerated T-slot post-arc requirements

- **Q1 answer:** ADR-0004 body quotes 2199 xx99 §1 line 74 verbatim as the ratified classification. No re-wording. §1 Context of ADR frames the quote as "Chris-ratified via 'agree all + (6)=(a) Group 2200 Frontend' 2026-07-05 at Arc S2199 xx99 close; ADR-0004 codifies as platform ADR."
- **Q2 answer:** Frontmatter Option (a): `status: accepted` + `provisional: true` + `provisional_reason: "IB-2199-BOR-01 (RAG search_docs + kb_tool retrieval end-to-end verification) undischarged; post-ratification discharge required per Arc I-0200 P1 severability determination §6 constraint 2"`.
- **Q3 answer:** ADR Consequences section enumerates each T-slot as a separate bullet: T18 axis-scoring ranker; T19 conflict-resolution rule engine; T21 lifecycle state machine; T22 metadata contract validation; T13 dual-cascade F3 R3.5 resolution; T26a retrieval-surface consistency Detect-and-Flag; T27 SIGN preamble corpus-hygiene gate; T29 Corpus Health Score dashboard phased rollout. Per-slot dependency notes cite 2199 §8 T-slot queue rows.
- **Q4 answer:** Title = `ADR-0004-rag-corpus-substrate-maturity-gradient.md` (PROVISIONAL marker in title body, not in filename — filename kept greppable). Stage 5 verification-method interface: `grep 'passive → spec-complete → execution-complete' docs/adr/ADR-0004-*.md` returns ratified verbatim + `git log --diff-filter=D docs/adr/ADR-0004-*.md` returns empty (no delete) + BACKLOG `IB-2199-T0-01` still `IN_ARC (I-0200)` at exercise time.

| Consequence field | Option 1 |
|-------------------|----------|
| Schema shape (ADR frontmatter fields) | Adds two new fields to the ADR corpus schema: `provisional: bool` + `provisional_reason: str`. New-to-corpus (neither ADR-0002 nor ADR-0003 uses them). Extends the frontmatter pattern for future PROVISIONAL ADRs. |
| Backward compatibility (existing ADR references + citations) | Existing ADR-0001/2/3 references unaffected — they don't cite `provisional` fields. Downstream corpus consumers (Rigby SIGN preamble, doc-claim verifier) that filter on `status: accepted` still surface ADR-0004; consumers wanting to exclude provisional ADRs must add a `provisional == true` filter (new capability). |
| Migration surface (docs cascade + BACKLOG refs + INDEX regen) | ADR PR runs 5-step cascade per §12.5.a; INDEX gains new ADR-0004 line. BACKLOG `IB-2199-T0-01` flips `IN_ARC → SHIPPED` at ADR PR merge + populates `pr_refs` + `adr_ref: ADR-0004` per IOS §2.2 v1.4 Discipline B inline syntax. No runtime migration. No feature flag introduction. |
| Rigby tool-surface / operator surface impact | `search_docs` for "maturity gradient" or "RAG substrate" surfaces ADR-0004 as canonical. `kb_tool.semantic_search` same. No new tool schema; no operator UI change. |
| Runtime / storage / volume implications | Zero runtime writes. `DocumentEmbedding` grows by ADR-0004 chunk count (est. ~15–25 chunks per cascade; single PR, one-time). Zero DB write volume beyond the ADR file. Zero API call rate change. |
| Grep-discoverability (C9) | ADR title contains "(PROVISIONAL)" tail for `grep -rn 'PROVISIONAL' docs/adr/` discovery. `provisional: true` field also greppable. |

### Option 2 — Verbatim seam statement + PROVISIONAL Option (b) single-field frontmatter + bundled T-slot post-arc reference

- **Q1 answer:** Same as Option 1 (verbatim seam statement).
- **Q2 answer:** Frontmatter Option (b): `status: provisional` (single field; `status` enum extended by Chris ratification at ADR merge time). ADR §1 Context defines `provisional` operationally: "ADR codifies a Chris-ratified classification whose runtime enforceability depends on a post-ratification research discharge (`IB-2199-BOR-01`). The ADR is authoritative at design-layer; post-BOR-01 discharge OR any T-slot ship triggers an ADR-0004-successor that may flip status."
- **Q3 answer:** ADR Consequences section bundles: "This ADR names all post-arc T-slots from 2199 xx99 §8 T-slot follow-on queue as prerequisites for classification maturity progression. See 2199 xx99 §8 for the enumerated list of 2 T0/Gate + 6 T1 + 9 T2 + 2 T3 items with owner assignments and dependency structure."
- **Q4 answer:** Title = `ADR-0004-rag-corpus-substrate-maturity-gradient.md` (same). Stage 5 verification-method interface identical to Option 1 (documentation cross-check).

| Consequence field | Option 2 |
|-------------------|----------|
| Schema shape (ADR frontmatter fields) | Extends `status:` enum with new value `provisional`. New-to-corpus. Requires update to `ADR-0001-establish-adr-corpus.md` if that ADR pins the enum (Chris ratification of enum extension implicit at ADR-0004 merge). |
| Backward compatibility (existing ADR references + citations) | Existing ADR-0001/2/3 unaffected (they use `status: accepted`). Downstream consumers filtering `status: accepted` do NOT surface ADR-0004 — this is either intentional (they want to skip provisional) or a regression (they want all ratified ADRs). Requires consumer-side decision. Larger ripple than Option 1. |
| Migration surface | Same cascade + BACKLOG flip pattern. Plus: optional refresh of `ADR-0001` §status-enum body if it pins the values. |
| Rigby tool-surface / operator surface impact | Same. |
| Runtime / storage / volume implications | Same. |
| Grep-discoverability (C9) | `grep -rn 'status: provisional' docs/adr/` returns ADR-0004. Single-field pattern is cleaner in the frontmatter block itself. |

### Option 3 — Verbatim seam statement + PROVISIONAL Option (a) two-field frontmatter + bundled T-slot post-arc reference

Combination of Option 1 (Q2 answer) and Option 2 (Q3 answer). Q1 + Q4 same as Options 1 and 2.

| Consequence field | Option 3 |
|-------------------|----------|
| Schema shape | Same as Option 1 (two new fields; no `status:` enum extension). |
| Backward compatibility | Same as Option 1. |
| Migration surface | Same as Option 1. |
| Rigby tool-surface / operator surface impact | Same. |
| Runtime / storage / volume implications | Same. |
| Grep-discoverability (C9) | Same as Option 1 for `provisional` field. But Q3 bundled reference is less directly greppable per T-slot than Option 1's enumerated pattern (`grep 'T22' docs/adr/ADR-0004-*.md` returns hit under Option 1; requires reading 2199 §8 pointer under Option 3). |

**No true fourth alternative.** A "non-verbatim maturity classification" would violate C6 (2199 seam statement already Chris-ratified); a "no PROVISIONAL marker" would violate C1; a "no T-slot naming" would violate C3.

---

## 5. Pressure test

Scoring matrix: option × criterion → verdict. Criteria drawn from §3 constraints + judgment criteria (blast radius per IOS §5.0, reversibility per ADR-0001 §3.5 scale 1–5, post-arc follow-on debt).

| Criterion | Option 1 (Two-field + enumerated) | Option 2 (Single-field + bundled) | Option 3 (Two-field + bundled) |
|-----------|-----------------------------------|-----------------------------------|-------------------------------|
| **C1 PROVISIONAL marker** | ✓ (two-field explicit) | ✓ (single-field explicit) | ✓ (two-field explicit) |
| **C2 BOR-01 clause** | ✓ (in `provisional_reason` field + Consequences body) | ✓ (in ADR §1 definition + Consequences body) | ✓ (in `provisional_reason` field + Consequences body) |
| **C3 T-slot naming** | ✓ per-slot enumeration (grep-friendly per-slot) | ⚠ bundled reference (requires 2199 §8 lookup) | ⚠ bundled reference |
| **C4 no runtime enforcement claims** | ✓ (Consequences body respects) | ✓ | ✓ |
| **C5 Stage 5 doc-cross-check-only** | ✓ (Q4 verification interface bounded) | ✓ | ✓ |
| **C6 verbatim seam statement** | ✓ (Q1 verbatim) | ✓ (Q1 verbatim) | ✓ (Q1 verbatim) |
| **C7 no runtime code** | ✓ (docs-only) | ✓ | ✓ |
| **C8 no companion-row admission** | ✓ (out-of-scope in ADR) | ✓ | ✓ |
| **C9 grep-discoverability** | ✓ (title + field + per-slot all greppable) | ⚠ (title + field greppable; per-slot requires 2199 §8) | ⚠ (title + field greppable; per-slot requires 2199 §8) |
| **C10 LOCAL-only** | ✓ | ✓ | ✓ |
| **C11 cascade co-location** | ✓ (ADR PR runs cascade) | ✓ | ✓ |
| **C12 fallback path not re-opened** | ✓ | ✓ | ✓ |
| **Blast radius (per §5.0)** | LOCAL (docs-only; ADR corpus schema extension additive) | SUBSYSTEM (extends `status:` enum → ripple through consumers filtering on `accepted`) | LOCAL |
| **Reversibility (per ADR-0001 §3.5, 1=irreversible, 5=trivial)** | 5 (revert commit; remove ADR file; no schema break) | 3 (revert commit; but `status: provisional` enum extension leaves corpus history with the enum value even after revert — downstream consumers may still filter on it) | 5 |
| **Post-arc follow-on debt** | Low (Option 1 enumeration commits ADR to naming exact T-slots; if any T-slot renames post-arc, ADR-0004 needs a supersede) | Medium (bundled reference is looser; renames don't force ADR update; but consumer-side filter decision is deferred debt) | Low-medium (mixes Option 1's schema simplicity with Option 2's naming looseness) |
| **Non-blocking counter-arguments (preserved for ADR §5 Alternatives inheritance)** | If Chris wants a provisional-status-visible-in-`status:` field for greppability, Option 2 wins there; but corpus-schema ripple cost is higher. | If Chris values grep-per-slot on ADR-0004 highly, Option 1 wins. | Middle-ground; loses per-slot grep and gains nothing over Option 1. |
| **IOS §14.2 codification signal** | Introduces two-field PROVISIONAL pattern as a codification candidate for future ADR-N (single trigger — awaiting second) | Introduces `status: provisional` enum extension as codification candidate (single trigger) | Redundant with Option 1 for schema; codification signal weaker |

### 5.1 Verdict summary

Option 1 dominates on C3 + C9 + blast radius + reversibility. Option 2 wins on Q3 bundled-reference elegance (single Consequences bullet vs eight). Option 3 loses to Option 1 on C3 + C9 without gaining anything over Option 1 on schema/backward-compat.

**Recommend Option 1.** Rationale expanded in §7.

---

## 6. Verification implications

Stage 3 pre-flight is SKIPPED per scoping doc §5 P2 row + §10 Stage 3 checklist entry ("SKIPPED — docs-only ADR has no runtime pre-flight; explicit note in close doc §7 rationale"). Stage 3 rollback plan is codified in scoping doc §7.2 F14 executable-commands table.

Stage 5 verification-method interface — bounded to documentation cross-check per F15 lock:

- **Under Option 1:** `grep -rn 'passive → spec-complete → execution-complete' docs/adr/ADR-0004-*.md` returns exactly one hit (Chris-ratified verbatim seam statement) + `grep -c '^- T' docs/adr/ADR-0004-*.md | head -1` returns count matching enumerated T-slot list (T18/T19/T21/T22/T13/T26a/T27/T29 = 8 items) + `git log --diff-filter=D docs/adr/ADR-0004-*.md` returns empty + BACKLOG `IB-2199-T0-01` row grep confirms `SHIPPED` status with `pr_refs` + `adr_ref: ADR-0004` populated.
- **Under Option 2:** Same first grep + `grep -rn '2199 xx99 §8' docs/adr/ADR-0004-*.md` returns hit for the bundled T-slot reference + same git-log + BACKLOG checks.
- **Under Option 3:** Same as Option 2 for T-slot checks; same as Option 1 for frontmatter checks.

Rigby-exercised surface (interface-level) at Stage 5 — **corrected per Rigby F18 fold to use tool-realistic repo/RAG checks only** (previous draft cited `deliverable_tool.list` on `docs/adr/` which is a filesystem-browse tool mismatch — `deliverable_tool` scopes to Deliverable ORM rows, not the repo tree):

- `search_docs` query for "RAG maturity gradient" returns ADR-0004 in top-k results (documentation retrieval via RAG corpus).
- `search_docs` query for "PROVISIONAL ADR" returns ADR-0004 (title + `provisional:` field greppability).
- `kb_tool.semantic_search` on the same queries as an independent-substrate cross-check (per F15 lock, this is documentation retrieval verification, not runtime disagreement probing — the same 2199 §14 F5 subject matter would be BOR-01 discharge and out-of-scope).
- `repo_tool.search` for frontmatter field patterns (`provisional: true` under Option 1/3; `status: provisional` under Option 2) returns ADR-0004 file.
- `repo_tool.read_file` on `docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md` returns the ratified verbatim seam statement + PROVISIONAL frontmatter as committed to `main`.

No runtime probe. No live-index query. No `manage.py` execution.

---

## 7. Recommendation

**Adopt Option 1 — Verbatim seam statement + PROVISIONAL Option (a) two-field frontmatter + per-slot enumerated T-slot post-arc requirements.**

### 7.1 Sub-decisions inside Option 1

- **Sub-option 1(i):** ADR-0004 filename remains `ADR-0004-rag-corpus-substrate-maturity-gradient.md` (Q4). PROVISIONAL is in `title:` body suffix and `provisional: true` field. Filename kept greppable.
- **Sub-option 1(ii):** T-slot enumeration order in ADR Consequences follows 2199 xx99 §1 line 82 listing order (T22 first per Track B canonical schema gate; T13 second per Track A canonical-path gate; then T18 / T19 / T21 / T26a / T27 / T29). Preserves the ratified §8 T-slot dependency structure.
- **Sub-option 1(iii):** `provisional_reason` field value is a single line naming `IB-2199-BOR-01` by intake_id + xx99 section pointer + P1 determination §6 constraint 2 citation. No prose expansion in the frontmatter; expansion goes in Consequences body.
- **Sub-option 1(iv):** ADR corpus schema extension (`provisional: bool` + `provisional_reason: str`) does NOT require a companion PR to `ADR-0001-establish-adr-corpus.md`. Per ADR-0001 §3.2 corpus-schema pattern, additive frontmatter fields are permitted without ADR-0001 amendment. If Rigby SIGN flags this, escalate to Chris.

### 7.2 Stage 3 pre-flight follow-on items

Per scoping doc §5 P2 row, Stage 3 is SKIPPED for docs-only ADR. The rollback plan is codified as executable commands per F14 (§7.2 of scoping doc). Post-ADR-merge Stage 5 verification method is documented at §6 above.

### 7.3 Explicit non-recommendations

- **Not Option 2** — even though single-field elegance is real, the `status: provisional` enum extension has SUBSYSTEM blast radius (downstream consumers filtering on `status: accepted` regress silently). Reversibility drops to 3.
- **Not Option 3** — no advantage over Option 1 on schema; loses C3 + C9 grep clarity.

---

## 8. Alternatives considered

Full alternative enumeration for ADR §5 Alternatives inheritance.

- **Option 2 (single-field PROVISIONAL + bundled T-slot).** Rejected — blast radius SUBSYSTEM (`status:` enum extension) + reversibility 3 + bundled reference weaker on C9 grep.
- **Option 3 (two-field PROVISIONAL + bundled T-slot).** Rejected — no schema advantage over Option 1; loses C3 + C9 per-slot grep.
- **Custom classification wording** (e.g., a Chris-refined re-write of 2199 §5.1). Rejected per anti-scope C6 — 2199 §5.1 is Chris-ratified; re-opening violates I-0200 scope.
- **Skip PROVISIONAL marker entirely** and mark ADR-0004 `status: accepted`. Rejected — violates C1 (P1 determination §6 constraint 1) + F15 Stage 5 verification scope lock (without PROVISIONAL, ADR asserts enforcement claims that require BOR-01 discharge).
- **Skip T-slot naming** (relying on 2199 §8 for post-arc requirements without ADR mention). Rejected — violates C3 (P1 determination §6 constraint 3) + weakens ADR-0004's platform-anchor role.
- **Bundle ADR-0004 with a T-slot ratification** (e.g., ship T22 alongside). Rejected — violates C7 "No runtime code" Chris directive + IOS §4.3 Stage 2 single-decision-per-ADR discipline.
- **Defer ADR-0004 authoring until BOR-01 discharge lands.** Rejected — this would flip the I-0200 SEVERABLE determination to NOT SEVERABLE de-facto, re-opening a settled ratification. Chris ratified SEVERABLE 2026-07-07 with PROVISIONAL shape as the accepted trade-off.
- **CX-P10 direct-ratification path** (skip Stage 2 ADR per IOS §3.1.b spec_ref rule). Rejected — BACKLOG `IB-2199-T0-01` row has no `spec_ref` column populated; §3.1.b downgrade rule applies; NEEDS_ADR path is required.

---

## 9. Provenance

### 9.1 Authorship + Consumed Sources

- **Author.** Claude Code, Arc I-0200 Stage 2 opening ceremony session (slug `claude-arc-i0200-stage2-open-design-prep`), 2026-07-07.
- **Consumed sources (files + lines).** As enumerated in frontmatter `source_finding_refs`. Read pre-drafting: 2199 xx99 §1 lines 74/76/78/82/84; Arc I-0200 scoping doc §3.1/§7.1/§8/§9.2/§10; Arc I-0200 P1 severability determination §4.3/§5.1/§6; RATIFICATION_2026-07-07 §2 Axis 7; BACKLOG row IB-2199-T0-01 post-P1 close; ADR-0001 §3.2 corpus-schema pattern; ADR-0002/0003 frontmatter conventions; `docs/topics/personal-assistant.md` retrieval surfaces; `docs/KNOWLEDGE_PIPELINE.md` narrative.
- **Rigby SIGN Cycle target.** Pending on arc-scoped pin `pa-1b76ee75adbf4031` per Chris directive 2026-07-07 (arc-scoped IOS §14.2 workflow refinement — see §9.2). Q-set will pressure-test §2 decision questions + §4 options matrix + §5 pressure test + §7 recommendation per IOS §7.2 single-batch × 4-Q cadence.
- **Chris ratification target.** This design-prep BEFORE ADR-0004 body drafting begins, per Chris directive 2026-07-07 "Return the SIGN package for Chris ratification before any ADR drafting."

### 9.2 IOS §4.3.a workflow deviation — recorded per Chris refinement-authority

**IOS §4.3.a default (lines 1124-1129 of `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`):**

> "SIGN routing (per §7.2 v1.4 shared-arc-pin rule). Design-prep artifacts are NOT independently SIGN'd — they are pressure-tested BY the SIGN cycle on the downstream ADR. Do NOT route a Rigby SIGN cycle for the design-prep alone. The ADR SIGN cycle Q-set naturally pressure-tests the design-prep §4 matrix + §5 pressure test + §7 recommendation (per Arc I-0100 ADR-B SIGN Cycle 1 Q1–Q4 pattern)."

**Chris directive 2026-07-07 (arc-scoped override):**

> "Route the completed Design Prep through Rigby SIGN. Return the SIGN package for Chris ratification before any ADR drafting. Stop after the Design Prep and Rigby SIGN."

**Interpretation.** This is a Chris refinement-authority prerogative per IOS §14.2. Arc I-0200's Stage 2 workflow is refined to: (1) design-prep authored → (2) design-prep SIGN'd on arc pin → (3) Chris ratifies design-prep → (4) ADR body drafted → (5) ADR SIGN'd on arc pin → (6) Chris ratifies ADR → (7) ADR PR merged. IOS §4.3.a default collapses steps 2–3 into step 5. Chris's refinement separates them, de-risking ADR body authoring by validating design-prep independently.

**Rationale (inferred).** Two signals converge: (a) P1 severability determination §6 imposed a novel 5-constraint PROVISIONAL ADR shape whose ADR-body encoding is high-stakes (getting Q2 or Q3 wrong ships bad platform-ADR content that ripples to downstream corpus consumers); (b) Arc I-0100 ADR-B SIGN Cycle 1 exposed design-prep gaps that were only caught during ADR SIGN — Chris's arc-scoped refinement is a targeted mitigation of that risk mode.

**Codification candidate for IOS v-next.** "Arc-scoped workflow overrides" as a first-class §4.3.a variant, with a recording discipline requiring design-prep §9 Provenance to name the deviation + citing §14.2 refinement-authority. Single trigger (this arc). Awaiting a second independent arc's deviation before proposing IOS §4.3.a amendment. Recorded here for §14.2 tracking.

### 9.3 Cross-references

- Scoping doc: `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md`.
- P1 severability determination: `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md`.
- Ratification record: `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
- IOS text: `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 §4.3 + §4.3.a + §4.3.0 stage-state enum + §7.2 SIGN routing + §14.2 Chris refinement-authority + §15.14 pin lifecycle.
- Canonical design-prep example: `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md` (Arc I-0100 ADR-B, cited by IOS §4.3.a line 1110-1114 as the reference implementation).
- 2199 xx99 canonical: `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 seam statement + §5.1 verbatim + §8 T-slot follow-on queue.
- ADR corpus schema: `docs/adr/ADR-0001-establish-adr-corpus.md`.

---

## 10. Meta-methodology (optional; per §4.3.a v1.5)

### 10.1 What this design-prep taught us about how to do design-prep

- **Two-turn design-prep-vs-ADR split** (Chris-directed for I-0200): decouples design-prep pressure-testing from ADR body authoring. Reduces "ADR body ships bad design because SIGN caught it too late" risk mode. Cost: adds one extra Chris ratification cycle per ADR.
- **PROVISIONAL ADR frontmatter novelty:** ADR-0004 is the first PROVISIONAL ADR in the corpus. Getting the pattern right (Option a vs b) sets the platform template for future PROVISIONAL ADRs (BOR-blocked, T-slot-blocked, external-dependency-blocked). Design-prep §4 Options + §5 Pressure test is the right structural venue to resolve the pattern before the ADR ships.
- **Anti-scope preservation across Stage 1 → Stage 2:** scoping doc §7.1 anti-scope bullets survived Stage 1 SIGN + P1 SIGN + P1 ratification and shape §3 Constraints C6–C8 of this design-prep. Anti-scope bullets are more load-bearing than they appear at Stage 1.

### 10.2 Codification candidates surfacing

- **CC-1 Arc-scoped workflow overrides** (§9.2 above). Single trigger.
- **CC-2 PROVISIONAL ADR pattern selection.** Whichever Option (a) or (b) Chris ratifies becomes candidate platform template. Single trigger; awaiting a second PROVISIONAL ADR before proposing ADR-0001 §3.2 amendment.
- **CC-3 Design-prep §1.2 "current code state" for docs-only ADR.** Novel to this arc — a docs-only ADR's "code state" is retrieval-surface implementation + docs cascade + ADR frontmatter conventions. Establishes a template for future docs-only ADR design-preps. Single trigger.

### 10.3 Meta-observations for §14.2 tracking

- **Chris's directive language pattern** ("Perform only the Stage 2 entry actions... Stop after…") is high-precision: it names both the do-list and the stop-list. This is the arc-execution-safety pattern established at Arc I-0100 Stage 6 (LOCAL-only guardrail) + refined here. Codification candidate: name it explicitly as a Chris directive style pattern. Single trigger.
