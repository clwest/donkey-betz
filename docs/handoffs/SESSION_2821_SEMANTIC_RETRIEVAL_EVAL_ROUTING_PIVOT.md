# Session 2821 — Semantic Retrieval Evaluation + Chris Routing-First Architectural Pivot

**Date:** 2026-07-18 (evening; direct successor to S2820 lexical-pilot feature-complete)
**Session:** S2821
**PRs shipped:** 1 close cascade (SHA at merge; no feature PR — evaluation session, no substrate changes)
**Predecessor:** [SESSION_2820_ORIENTATION_DOC_EXCLUSION_LEXICAL_FEATURE_COMPLETE](SESSION_2820_ORIENTATION_DOC_EXCLUSION_LEXICAL_FEATURE_COMPLETE.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 0 in-session (no code changes) + 1 close-cascade recycle post-merge (PLAYBOOK-7.4.4)

---

## §1 — Ship summary

**No code changes.** S2821 was a pure evaluation session per Chris directive at S2820 close: "Spend the next engineering cycle evaluating semantic retrieval against the benchmark corpus you've accidentally built during the docs audit."

Three architectural artifacts shipped as docs:

1. **S2821 semantic-retrieval evaluation** (13-row eval matrix over 10 unique query texts × 3 mechanisms — M1 defaults, M2 authority_weighted, M3 include_superseded). Aggregate STRICT interpretation: **M1 23% · M2 15% · M3 54%** success@3. Direction preserved: M3 > M1 > M2, but semantic-only cannot replace lexical primary — confirmed by fail on Q1 count-monoculture + Q5 procedural + Q8 self-reference + C3 self-reference-direct + C5.
2. **Chris routing-first architectural pivot** (mid-evaluation): "Routing is the architectural boundary. Fusion is a downstream, per-family implementation choice." Reframes S2822 from hybrid-merge-planning to intent-family routing table construction.
3. **S2822 Phase-0 methodology proposal** (joint-signed by Rigby, pending Chris ratification at S2822 open): 6-family working taxonomy (COUNT / PROCEDURAL / DISCOVERY / IDENTITY / SELF-REFERENCE / CONCEPTUAL) + 33-row expanded benchmark + label schema (with strict/loose target-set split + `answer_mode` field + `has_literal_identifier` derived feature) + tri-state ambiguity policy + per-family gates (COUNT elevated to HIGH consequence) + two-axis classifier pressure-test.

**Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2821_semantic_eval_routing_pivot_phase0_proposed.md` (frozen at merge per PLAYBOOK-6.10.9)

---

## §2 — Rigby joint SIGN — THREE SIGN CYCLES

**Pin:** `pa-c884459957614bbd` (S2821 open fresh mint; retired at close, force=true, fifty-second consecutive per S2770+ pattern).

Three tool-grounded joint SIGN cycles, all substantive (non-empty tool_runs each):

### 2.1 Task #3 measurement plan SIGN
Rigby verdict: **ship M1/M2/M3 methodology as-is**. Locked mechanism params + query strings. Spot-check protocol agreed. Rigby's live probes surfaced pre-measurement signals: Q7 handoff-visibility hypothesis + `canonical_authority='repo_canonical'` scope-tightener (noise reduction, not M4 proposal).

### 2.2 Task #4/#5 recommendation SIGN
Claude proposed Path B (Hybrid lexical + semantic). Rigby AGREE with two refinements:
- Gap #1 (include_superseded default): specific "sync maps superseded→ARCHIVED" claim needs Document-table inspection to assert — softened accordingly
- Gap #8 (legacy architecture docs outrank PLATFORM_INVENTORY): reframed from "data-quality" to "retrieval objective mismatch" — canon pointers to PLATFORM_INVENTORY exist across docs; semantic doesn't respect the pointer relationships

Rigby methodology gap I missed: query-string stability matters; small variations flip top-1/top-3.

### 2.3 S2822 Phase-0 methodology SIGN
Post Chris routing-first D-verdict + 6 refinements. Rigby AGREE, no blockers, with four schema refinements booked:
1. Split target: `known_correct_target_strict` (must-hit) + `known_correct_target_loose` (acceptable alternatives) — prevents C2-like silent relaxation
2. Add `answer_mode` field (IS_DOC | ABOUT_TOPIC | POINTER_DOC) — encodes IS-ness/aboutness boundary
3. Add `has_literal_identifier` derived feature — cheap classifier input for IS_DOC prediction
4. Elevate COUNT misroute consequence from MEDIUM to HIGH — DOC_LIFECYCLE §2c "sole authoritative counts source" convention makes wrong-but-plausible for COUNT particularly dangerous

Zoom-out blindspot Rigby flagged: Phase-0 assumes intent classifiable from query string alone. Dominant ambiguity driver may be **user context** (recent activity, workspace, mode). Treat "context needed" as first-class classifier output.

---

## §3 — Novel precedent

1. **First "routing not fusion" architectural re-framing mid-evaluation.** Claude proposed Path B (Hybrid merge lexical + semantic); Chris re-framed at close-adjacent as: routing IS the architectural boundary, fusion is downstream. Captures the observation that different retrieval substrates excel at different retrieval intents — the primary question isn't "how do we merge" but "how do we know which substrate answers which class of query."
2. **First session with 3 substantive joint SIGN cycles + Chris D-verdict + follow-on joint SIGN.** Rigby was continuously in-loop across measurement planning, recommendation synthesis, and Phase-0 methodology drafting. All 3 cycles had non-empty tool_runs.
3. **First per-family gate proposal (no global accuracy floor).** Chris explicit at Refinement #2: "high global score must not conceal failure in thin but high-consequence families like IDENTITY or SELF-REFERENCE." Per-family gates weight classifier accuracy floor by misroute consequence.
4. **First silent target-set relaxation caught in joint SIGN.** C2 T3 §7 target = `2701_docs_inventory_topology_audit` + `2700_docs_restructuring_domain_scoping` (BOTH required). Claude initial evaluation accepted 2701 alone. Rigby caught; strict/loose split now baked into Phase-0 label schema.
5. **First IS-ness / aboutness architectural framing.** Emerged from measurement evidence: lexical = "IS-ness" retrieval (this doc IS the answer); semantic = "aboutness" retrieval (this doc discusses the answer). Rigby endorsed with tool evidence (C4 semantic returns docs that *mention* 2701 audit, not the audit itself; C1 semantic returns AGENTS_REFERENCE.md which is "about Colorado JDF" not SESSION_2808 which IS the answer).
6. **First "13 queries" harness reconciled to "13-row eval matrix over 10 unique query texts."** C2/C3/C5 share text with Q7/Q8/Q1. Harness definition formally corrected.
7. **First POINT relationship proposed as distinct from LOCATE.** Not in Chris's initial 5-relationship list. Based on Q8 evidence (target = CLAUDE.md#6 pointer chunk, NOT 00-START itself). Rigby AGREE POINT is genuinely distinct, not implementation detail.
8. **First IDENTITY + SELF-REFERENCE-C3 collapse candidate.** Both map to (DOC, LOCATE) in two-axis decomposition. Flat taxonomy may fold 6→5 if Phase-0 confirms.

---

## §4 — What shipped vs what didn't

**Shipped (as docs, no code):**
- 13-row semantic evaluation matrix + STRICT/LOOSE aggregate reconciliation
- Chris routing-first architectural directive (D-verdict on architectural direction with 6 refinements)
- Rigby-joint-signed Phase-0 methodology proposal (33-row corpus + label schema + ambiguity policy + per-family gates + two-axis pressure-test)
- Ratification envelope with §3 empirical evidence + §7 Phase-0 methodology detail

**Not shipped (deferred to S2822):**
- Phase-0 methodology CHRIS RATIFICATION — awaits D-verdict at S2822 open
- Phase-0 corpus expansion execution (20 new labeled queries)
- Classifier A (flat) vs Classifier B (two-axis) build + measurement
- Per-family gate calibration (evidence-based; comes from Phase-0 measurement)
- Routing table implementation (Phase-1 per Chris — after Phase-0 gate passes)
- Any code substrate change (no lexical patches per Chris freeze; no semantic default flip per non-recommendation)

**Explicit non-recommendations retained (Chris R#6):**
- NO RRF / global fusion during Phase 0
- NO taxonomy constitutionalization from S2821 evidence alone

---

## §5 — Ledger + provenance

- **Zoom-out ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows at S2821 open + close (unchanged this session; folds noted in envelope §5 for arc-close persistence per S2818/S2819/S2820 pattern)
- **Recycle log:** `logs/recycle_events.jsonl` — 0 in-session recycles (no code changes) + 1 close-cascade recycle post-merge
- **Freshness log:** `logs/session_freshness.jsonl` — grew by 1 at S2821 open (STALE_DAPHNE non-blocking)
- **Baseline HEAD:** `b6d051dd1` (S2820 close cascade)
- **Ratification HEAD:** (filled at merge)

---

## §6 — Candidates for S2822

**Ranked per Chris D-verdict + Rigby AGREE:**

1. **⭐ Ratify Phase-0 methodology + execute Phase-0** (SOLE recommended direction — joint-signed proposal awaits Chris D-verdict). Concrete first steps:
   - Chris D-verdict on Phase-0 methodology proposal (as-is, or with revisions to any of 8 sections)
   - Corpus expansion: author 20 new labeled queries per §7 label schema
   - Classifier A (flat) build + measure vs Classifier B (two-axis) build + measure
   - Per-family precision/recall/F1 + confusion matrix + ambiguous-rate + abstention-rate
   - Gate calibration from measurement
   - Route findings to Chris for Phase-1 gate decision
2. **Override Phase-0 methodology** (any of Refinements 1-6 revised; corpus subset differently; alternate taxonomy)
3. **Non-routing candidates (backgrounded):** Colorado Phase 4, BettingPage first-user trace, Stock Intelligence, Playbook v0.9 amendment.

**Recommended default:** Item #1 (Phase-0 ratification + execution). Chris explicitly asked me to return with the Phase-0 methodology + route through Rigby before execution. Both are done. Chris ratifies at S2822 open.

---

## §7 — S2821 lessons to carry

1. **Retrieval-substrate specialization is real.** Different substrates excel at different intent families. Lexical = IS-ness (this doc IS the answer); semantic = aboutness (this doc discusses the answer). Attempting to merge without routing accretes complexity that routing dissolves.
2. **Routing is the architectural boundary; fusion is per-family implementation detail.** Chris's re-framing at close-adjacent changed the S2822 shape from "how do we merge" to "how do we know which substrate to invoke." Non-obvious in advance; obvious in retrospect.
3. **Silent target-set relaxation is a real audit gotcha.** C2 T3 §7 target required BOTH 2701 + 2700; Claude initial evaluation accepted 2701 alone. Rigby caught via tool-grounded reading of T3 §7. Strict/loose target-set split now baked into Phase-0 label schema.
4. **Query-string stability matters.** Small query variations flip top-1/top-3 across mechanisms. Locked query strings from BENCHMARK constant were the right mitigation. Future harnesses record queries verbatim.
5. **Per-family gates > global accuracy floor.** Global 80% would have concealed IDENTITY/SELF-REFERENCE failures given their low sample count. Per-family gates weighted by misroute consequence make thin-family failures load-bearing.
6. **Anti-rubber-stamp check via tool_runs works.** All 3 SIGN cycles had non-empty tool_runs (repo_tool + search_docs + kb_tool.semantic_search live). Zero rubber-stamp signal this session.
7. **Fresh-session cascade close pattern applies to research sessions too.** Even without code changes, close cascade artifacts (handoff + envelope + 00-START update + pin rotation + docs pipeline) preserve continuity across sessions.

---

**End of S2821 handoff. Close cascade PR follows this ship. Discovery-layer arc now has BOTH lexical branch FEATURE COMPLETE (S2818/S2819/S2820) and semantic branch EVALUATED (S2821 evidence + S2822 Phase-0 methodology proposed). S2822 opens with Chris D-verdict on Phase-0 methodology.**
