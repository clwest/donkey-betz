---
title: "S2828 — Pattern D LITERAL-FILENAME Candidate Injection"
session: 2828
date: 2026-07-19
status: shipped
authority: implementation + governance
scope: |
  S2828 shipped Pattern D LITERAL-FILENAME candidate injection as one
  atomic PR (#3269, SHA `d26fe5311`). Post-implementation Phase-0.5
  re-measurement: 10/18 → 12/18 = 66.7% strict top-1 (Q20 + Q24
  conversions via P2 + P1 tiered bonuses; matches design projection
  exactly). Q28 preserved natively via Strategy C MISS path (no-perturb).
  Rigby joint SIGN reached joint agreement across 2 cycles (5 questions
  + reconciliation) before Chris routing per S2753 discipline. Chris
  D-Q1..D-Q7 all YES with refinements: measured smallest-per-gate
  discipline; per-regex bonus tiers as the mitigation for Rigby zoom-out
  fold (same_pr_mitigatable); shared "pointer-intent registry" primitive
  extraction sequenced as separate post-S2828 arc. SEVENTY-THIRD
  close-cycle post-PLAYBOOK-7.4.4.
predecessor: docs/handoffs/SESSION_2827_PATTERN_C_SELF_REFERENCE_INJECTION.md
merge_pr: 3269
merge_sha: d26fe5311
---

# S2828 — Pattern D LITERAL-FILENAME Candidate Injection

## §1 One-paragraph summary

Shipped Pattern D LITERAL-FILENAME candidate injection into
`core/rag_integration.py` embedding lane as a sibling to S2826 Pattern B
(COUNT) + S2827 Pattern C (SELF_REFERENCE). Whole-string `^...$` 4-regex
intent gate (P0 `.md` extension, P1 uppercase snake ≥2 segs, P2
hyphenated CAPS ≥3 segs, P3 numeric-prefix snake ≥3 segs) disjoint from
Pattern B/C multi-word patterns by construction. Curated 6-entry
`_LITERAL_FILENAME_ANCHORS` map (Strategy A per Chris D-Q2) + Strategy C
log-only miss path (`[S2828_PATTERN_D_MISS]` INFO); rejected Strategy B
dynamic Document.file_path lookup per Rigby SIGN Q2 over-match evidence.
Per-regex bonus tiers (Strategy 3-B per Rigby SIGN Q3 DISAGREE with flat
bonus) with per-gate sweep + ceilings — selected values P0=0.07,
P1=0.09, P2=0.32, P3=0.03. Chris D-Q1 discipline: smallest reliable per
gate; margins recorded; no ceiling raised. Chris D3 retrieval-integrity
preserved (bounded bonus, NOT force-rank-1). Chris D-Q4 Q28 no-perturb
tolerance validated. Post-implementation Phase-0.5 re-measurement:
6/18 → 10/18 → **12/18 = 66.7%** strict top-1. Pattern B/C smoke: no
regression. Pytest: 95/95 (61 Pattern D + 34 Pattern C regression).
Permanent architectural reference added to `docs/KNOWLEDGE_PIPELINE.md`
§Pattern D Measured Boundary Summary per Chris close directive.

## §2 Ship

### Files shipped

**PR #3269 — atomic per Chris D-Q7:**

| # | File | Change |
|---|---|---|
| 1 | `core/rag_integration.py` | +266 lines Pattern D impl (patterns/anchors/gate/fetch/composition/sort/WARN/diagnostics) |
| 2 | `docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md` | New — full v2 design + §7.5 measurement evidence |
| 3 | `tests/unit/test_s2828_pattern_d_literal_filename_gate.py` | New — 61 pytest cases |

**Merge:** SHA `d26fe5311` (2026-07-19) via `gh pr merge --admin --squash --delete-branch 3269`. Post-merge `make celery-recycle` executed per PLAYBOOK-7.4.4.

### Ledger delta

- Zoom-out ledger: **1 fold persisted** at S2828 (`same_pr_mitigatable`)
  — Rigby-proposed at SIGN Q5c, ratified by Chris D-Q6, mitigation IS
  the per-regex bonus tiers shipped in PR #3269. Persisted at close
  cascade in `logs/zoom_out_classifications.jsonl`.
- Pattern registry: now 3 intent-gated policy-class mechanisms (B/C/D).
  The 3-instance codification threshold (Chris D-Q3 forward-carry) is
  NOW met — shared "pointer-intent registry" primitive extraction is a
  candidate arc. Explicitly deferred per Chris D-Q7 to post-S2828.

## §3 Rigby joint SIGN records (S2828)

### §3.1 — First SIGN cycle (design v1)

5 questions routed with explicit anti-rubber-stamp directive (S2777
memory rule). Rigby tool_runs: `repo_tool.read_file` ×2 on
`core/rag_integration.py` + design doc; `kb_tool.semantic_search` ×6 on
README / 00-START-NEXT-SESSION / PLATFORM_INVENTORY / CLAUDE.md /
00-START-NEXT-SESSION.md / KNOWLEDGE_PIPELINE; `kb_tool.documents` ×1
(returned 0 — validated title-only lookup behavior); `search_docs` ×1.
Ten tool grounding calls — not rubber-stamp.

Rigby verdicts:
- **Q1** AGREE with load-bearing nuance — whole-string `^...$` anchoring
  is Chris D5 disjointness boundary; substring-relaxation would break
  it
- **Q2** AGREE Strategy A curated map + tiny Strategy C log-only fallback
  — over-match risk on Strategy B verified via tool_run #3 on `README`
- **Q3 DISAGREE with 3-A flat bonus** — Q20's +0.31 gap makes a single
  static +0.32ish bonus a "big hammer"; prefer 3-B per-regex tiers with
  cap + sweep
- **Q4 DISAGREE with force-rank-1** — even literal `00-START-NEXT-SESSION`
  has 0.7098-similarity topic competitor; bounded discipline still
  applies
- **Q5** (a) AGREE refactor-after-Pattern-D; (b) caution flag on
  negative-control coverage; (c) proposed zoom-out fold worth
  persisting BEFORE ship

### §3.2 — Reconciliation cycle (design v2)

R1-R5 refinements applied to §0/§4.1/§4.2/§4.3/§5/§7 of design doc.
Rigby re-read v2 (2 `repo_tool.read_file` calls covering full 658-line
doc) + returned explicit AGREE on R1/R2/R3/R4/R5(a/b/c) with one
implementation-clarity note (canonicalization spec mirror in pytest —
addressed by `TestCanonicalization` cases).

Joint Claude+Rigby agreement reached before Chris routing per S2753
"reach agreement before Chris yes/no."

## §4 Chris D-verdicts (all RATIFIED with refinements — same session)

- **D-Q1 YES** — Per-regex bonus sweep methodology + per-gate ceilings
  (P0/P2=0.35, P1=0.20, P3=0.10) ratified. Chris directive: benchmark
  does not choose the bonus; measurements choose the bonus. Record
  smallest successful value, winning margin, first failing value below,
  highest tested value. If gate cannot convert within ceiling, report
  explicitly + do NOT raise ceiling.
- **D-Q2 YES** — Strategy A curated map + Strategy C log-only miss
  fallback ratified. Explicitly rejected Strategy B dynamic
  Document.file_path discovery.
- **D-Q3 YES** — Retrieval-integrity invariant preserved as
  constitutional. Bounded bonus, NOT force-rank-1. Legitimate competitor
  may still win.
- **D-Q4 YES** — Q28 remains as intentional regression control. Pattern
  D firing on Q28 without perturbing rank order is evidence of correct
  behavior.
- **D-Q5 YES** — `CLAUDE.md` literal in scope even though not a corpus
  row. Literal canonical artifact references belong to this policy
  class.
- **D-Q6 YES** — Rigby fold persisted verbatim as `same_pr_mitigatable`.
  Mitigation (per-regex confidence tiers) already exists in design.
- **D-Q7 YES** — Atomic PR sequencing per S2827 D-Q5. Do NOT combine
  shared "pointer-intent registry" refactor with Pattern D. Evaluate as
  separate arc post-Pattern-D-ship.

## §5 Post-implementation measurement evidence — verbatim

### §5.1 — Chris D-Q1 per-gate sweep

**Coarse per-gate sweep** — bonus values `[0.03, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]`. Full table in design doc §7.5.1.

**Fine-grained per-gate sweep** — narrowed to smallest-flip vicinity:

| Gate | v=0.06 | v=0.07 | v=0.08 | v=0.09 | v=0.31 | v=0.32 | v=0.33 | v=0.35 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| P0 CLAUDE.md anchor rank | 2 | **1** | 1 | 1 | — | — | — | — |
| P1 PLATFORM_INVENTORY anchor rank | — | 4 | 2 | **1** | — | — | — | — |
| P2 00-START-NEXT-SESSION anchor rank | — | — | — | — | 2 (margin −0.0019) | **1** | 1 | 1 |

**Selected values + margins:**

| Gate | Selected | First failing below | Ceiling | Headroom | Neg regs at sr |
|---|:-:|:-:|:-:|:-:|:-:|
| P0 `.md` | **0.07** | 0.06 (rank 2) | 0.35 | +0.28 | 0/20 |
| P1 uppercase snake | **0.09** | 0.08 (rank 2) | 0.20 | +0.11 | 0/20 |
| P2 hyphen caps | **0.32** | 0.31 (rank 2, margin −0.0019) | 0.35 | **+0.03** | 0/20 |
| P3 numeric snake | **0.03** | — (Q28 wins natively via MISS path) | 0.10 | +0.07 | 0/20 |

### §5.2 — Per-query positive evidence

| qid | query | anchor natural? | injected? | orig sim | bonus | eff sim | final rank |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Q20 | `00-START-NEXT-SESSION` | False | True | 0.3979 | +0.32 (P2) | 0.7179 | **1** |
| Q24 | `PLATFORM_INVENTORY` | False | True | 0.4751 | +0.09 (P1) | 0.5651 | **1** |
| CLAUDE.md (adjacent) | `CLAUDE.md` | False | True | 0.5363 | +0.07 (P0) | 0.6063 | **1** |
| Q28 (no-perturb) | `2701_docs_inventory_topology_audit` | True (rank 1) | False (MISS path) | 0.5973 | 0.0 (P3 MISS) | 0.5973 | **1** |

### §5.3 — Negative controls (20 rows) — 0 regressions

Pattern B queries preserved (`how many spiders` etc.); Pattern C
queries preserved (`where do I start` etc.); whole-string invariant
holds (natural-language mentions of filenames don't fire); MISS path
proven (`SPIDER_NETWORK`, `README.md` fire gate but no injection);
2-seg-hyphen / single-word / lowercase / path-form all held. Full
table in design doc §7.5.3.

### §5.4 — Pattern B + C regression check

`How many spiders` → `docs/PLATFORM_INVENTORY.md` gate=count ✓;
`where do I start` → `00-START-NEXT-SESSION.md` gate=self_reference ✓;
`project rules` → `CLAUDE.md` gate=self_reference ✓. No regression.

### §5.5 — Full 18-row Phase-0.5 re-measurement

| Session | Strict top-1 hits | Delta | Mechanism family |
|---|:-:|:-:|---|
| S2825 baseline | 0/16 = 0.0% | — | none |
| S2826 (metadata repair + Pattern B) | 6/18 = 33.3% | +6 | 3× Pattern B + 3× metadata repair |
| S2827 (Pattern C + corpus repair) | 10/18 = 55.6% | +4 | 4× Pattern C SELF_REFERENCE |
| **S2828 (Pattern D)** | **12/18 = 66.7%** | **+2** | **Q20 P2 + Q24 P1 Pattern D conversions; Q28 natural preserved** |

Full table with per-query attribution in design doc §7.5.4.

### §5.6 — Pytest coverage

**95/95 PASSING** (`tests/unit/test_s2828_pattern_d_literal_filename_gate.py`
61 tests + `tests/unit/test_s2827_pattern_c_self_reference_gate.py` 34
regression tests):
- 10 positive gate-fire cases (curated map coverage)
- 3 miss-path cases (README.md, SPIDER_NETWORK, Q28)
- 20 negative gate-hold cases
- 9 canonicalization spec cases
- 13 cross-mechanism disjointness cases (Pattern B/C/D exclusion)
- 5 wiring invariants
- 6 whole-string invariant regression samples (LOAD-BEARING)

## §6 Pattern D measured boundary summary (permanent architectural record)

Per Chris close directive 2026-07-19: added to
`docs/KNOWLEDGE_PIPELINE.md` §Pattern D Measured Boundary Summary
(S2828 addendum) as companion to S2826 §retrieval-failure-diagnosis-order
+ S2827 §Pattern C Measured Boundary Summary.

Concise summary (verbatim from that section):

- **Selected per-gate bonuses:** P0=0.07, P1=0.09, P2=0.32, P3=0.03.
- **Q20 was the limiting case for P2** (largest measured gap +0.3119;
  P2 sits with only +0.03 headroom below ceiling).
- **Whole-string `^...$` invariant is LOAD-BEARING** for disjointness
  vs Pattern B/C.
- **Strategy A curated map + Strategy C log-only miss** — no Strategy
  B dynamic lookup (over-match risk).
- **Chris D3 retrieval-integrity preserved** — bounded per-gate bonus,
  NOT force-rank-1.
- **Q28 no-perturb tolerance** — MISS-path skips injection; natural
  rank 1 preserved.
- **Post-Pattern-D 3-instance codification threshold met** — Pattern
  B + C + D share skeleton; shared "pointer-intent registry" primitive
  extraction is a POST-Pattern-D candidate arc per Chris D-Q7.

Full details: `docs/KNOWLEDGE_PIPELINE.md` §Pattern D Measured Boundary
Summary + design doc §7.5.

## §7 Twin-pointer

Per parent handoff pattern + memory `feedback_twin_deliverable_at_every_ratification`:

- **Repo doc:** this handoff at merge SHA `d26fe5311`
- **Workspace deliverable:** `ceca32ff-a5b6-4fa0-8ada-20e436117b98`
  in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) —
  created at S2828 close cascade via ORM-direct per memory
  `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`
  (bypasses pa_deliverables_tool diagnostic-flag bug); type
  `ratification_record`, category `governance`, status `ready`, pinned,
  `diagnostic_status=None` (cleared).

## §8 Lessons for S2829

1. **The 3-instance codification threshold is met.** Shared
   "pointer-intent registry" primitive extraction (Chris D-Q3 forward-
   carry) is now a candidate arc. Pattern B/C/D share the skeleton
   (gate → anchor resolve → injection → bonus → diagnostics → drift
   WARN). Chris D-Q7 explicitly deferred this to POST-S2828 — evaluate
   as separate arc.
2. **Per-regex bonus tiers generalize the "smallest reliable
   adjustment" discipline.** Chris D-Q1 scalar-scope from S2827 extends
   cleanly to per-gate scope in S2828. Future intent-gated mechanisms
   with heterogeneous signal strengths should adopt per-gate ceilings +
   per-gate sweeps, not global constants.
3. **P2's tight +0.03 headroom below ceiling is a real signal.**
   00-START-NEXT-SESSION's raw anchor sim is low (0.3979) — the doc's
   embeddings are dissimilar from queries that literally name it. If a
   future canonical target has similar characteristics, expect similar
   tightness; per-gate ceilings must be sized deliberately.
4. **Strategy C log-only miss path proved cleanly.** N14/N16/N20
   negative controls (SESSION_2827_PATTERN_C, README.md, SPIDER_NETWORK)
   all validate that gate-fires-without-anchor is safe: natural
   retrieval unchanged, INFO log for future map graduation. Do NOT let
   Strategy C drift toward runtime resolution to non-canonical
   Documents.
5. **Q28 as regression control is architecturally load-bearing.** A
   naturally-winning literal-filename query that Pattern D must not
   perturb is a permanent invariant. If a future refactor breaks Q28's
   MISS-path handling, the test suite catches it.
6. **Whole-string `^...$` invariant is LOAD-BEARING and MUST NEVER be
   relaxed silently.** Pytest
   `test_whole_string_holds_across_natural_language` guards this.
   Substring-relaxation would immediately break disjointness vs Pattern
   B/C multi-word patterns.
7. **DO NOT relax `include_superseded=False` default** (Chris D6
   retrieval integrity rule; unchanged).
8. **DO NOT propose universal runtime injection at PA level** (Chris
   D3 "retrieval must prove retrieval").

## §9 Current repository state (S2828 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `d26fe5311` (S2828 PR #3269 merge) + close-cascade PR (filled at close-PR merge) |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Phase-0.5 arc state | **Pattern D SHIPPED. Post-Pattern-D baseline: 12/18 = 66.7% strict top-1. All literal-filename + intent-based policy classes shipped. Post-Pattern-D shared "pointer-intent registry" primitive extraction candidate for S2829.** |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| PHASE_0_5_ROUTER_ENABLED | false (default; unchanged) |
| S2827 pin | `pa-fdf0a44a75b34e8f` (retired at S2827 close) |
| S2828 pin | `pa-58fa25861f814309` (label `s2828-pattern-d-literal-filename-injection`, retired at S2828 close, force=true, fifty-ninth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2829 open) |
| Session close cascade | THIS session — S2828 |
| Docs cascade | 4-step per feedback_docs_cascade_at_every_close (build_docs_index / build_rag_corpus / sync_docs_index_to_documents / embed_documents --all-unembedded) |
| Recycle post-merge | ✅ `make celery-recycle` executed after #3269 merge (PLAYBOOK-7.4.4) |
| Metadata layer health | ✅ 0 mismatches vs docs/_index.json (post-S2826, unchanged) |

## §10 Twin-pointer card (for S2829 open protocol)

📁 **Repo — S2828 artifacts:**

- **Pattern D implementation:** `core/rag_integration.py` §S2828 Pattern D (patterns/anchors/gate/fetch at :258-410; composition + bonus at :627-680; drift WARN at :796-820)
- **Design + measurement evidence:** `docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md` (§7.5 full evidence)
- **Pattern D measured boundary summary:** `docs/KNOWLEDGE_PIPELINE.md` §Pattern D Measured Boundary Summary (S2828 addendum)
- **Pytest:** `tests/unit/test_s2828_pattern_d_literal_filename_gate.py` (61 tests)
- **This handoff:** `docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md`
- **Merge SHA:** `d26fe5311` · **PR:** #3269

🖥️ **Workspace UI — S2828 twin-pointer workspace deliverable:**

- **`ceca32ff-a5b6-4fa0-8ada-20e436117b98`** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) — type `ratification_record`, category `governance`, status `ready`, pinned, `diagnostic_status=None`. ORM-direct create bypasses `pa_deliverables_tool` diagnostic-flag bug per memory `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.

## §11 Appendix — Provenance

- **Predecessor:** S2827 (Pattern C SELF_REFERENCE candidate injection; PR #3267, SHA `47f3650d1`)
- **Novel this session:** first empirical validation of the Chris D-Q1 "smallest reliable adjustment" discipline generalized to per-regex bonus tiers with per-gate ceilings; first empirical validation of Rigby SIGN Q3 DISAGREE catching a design tension pre-Chris; first arc where the 3-instance codification threshold for a shared primitive is met (Pattern B/C/D); first arc with a Rigby-proposed zoom-out fold whose mitigation is IN the same PR (not deferred).
- **Chris D-verdict cascade:** D-Q1..D-Q7 all YES-with-refinements — refinements applied verbatim to the shipped implementation.
- **Rigby SIGN cycles:** 5 questions (10 tool_runs) → 4 DISAGREE + 1 AGREE-with-caveat → v2 reconciled → 2 read_file re-verify → explicit R1-R5 AGREE → joint Claude+Rigby agreement → Chris D-verdict.
