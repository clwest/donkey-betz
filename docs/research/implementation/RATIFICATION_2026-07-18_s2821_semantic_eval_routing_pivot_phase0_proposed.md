---
title: "S2821 Semantic Retrieval Evaluation + Routing-First Architectural Pivot + Phase-0 Methodology Proposal (2026-07-18)"
status: active
authority: ratification-record
session_added: 2821
ratification_date: 2026-07-18
ratifier: chris
routing: |
  rigby-pa-chat joint SIGN (three cycles: measurement plan / Task 4/5 recommendation / S2822 Phase-0 methodology) + Chris D-verdict "S2822 ROUTING PREP - approve architectural direction with 6 refinements" + Rigby AGREE-no-blockers on Phase-0 methodology
scope: |
  S2821 semantic retrieval evaluation against S2820 accidentally-built
  benchmark corpus + Chris routing-first architectural directive +
  Rigby-joint-signed Phase-0 methodology proposal for S2822.
  
  Ratifies: Chris routing-first architectural direction (Path B hybrid-merge
  proposal SUPERSEDED by routing-first framing per Chris D-verdict).
  
  Proposes (pending Chris ratification at S2822 open): Phase-0 methodology
  (33-row corpus + label schema + ambiguity policy + per-family gates +
  two-axis classifier pressure-test).
serves_arc: |
  Discovery-layer arc (S2818/S2819/S2820 lexical branch FEATURE COMPLETE +
  S2821 semantic branch EVALUATED + S2822 routing-first Phase-0 pending
  Chris ratification)
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md (S2820 lexical pilot chain FEATURE COMPLETE + §5 benchmark corpus + §7 S2822 direction directive that this session executed)
  - docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md (S2819 §5.1 evidence-first baseline methodology applied throughout S2821 measurement)
  - docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md (S2818 lexical baseline for Q1-Q4 count queries + methodology origin)
ratified_documents:
  - docs/handoffs/SESSION_2821_SEMANTIC_RETRIEVAL_EVAL_ROUTING_PIVOT.md (this session's handoff)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2821 open freshness — verdict STALE_DAPHNE · head=b6d051dd1 · celery_stale=0/5 (session_lifecycle open output at S2821 open; daphne stale not blocking for Rigby PA dispatch via celery)
  - S2821 measurement-plan joint SIGN (Rigby, pin pa-c884459957614bbd) — Q1 corpus scope AGREE 13-query harness sufficient; Q2 add M3 for handoff-visibility hypothesis; Q3 MEDIUM regression criterion (top-3); Q4 zoom-out blindspots enumerated. tool_runs non-empty (kb_tool.semantic_search × 2 + search_docs).
  - S2821 Task 4/5 recommendation joint SIGN — Path B (Hybrid) drafted; Rigby AGREE with 2 gap refinements (include_superseded causal chain softened; legacy architecture doc dominance reframed as retrieval objective mismatch). tool_runs non-empty (search_docs + repo_tool + kb_tool.semantic_search).
  - CHRIS D-VERDICT "S2822 ROUTING PREP" — approve architectural direction with 6 refinements: (1) taxonomy WORKING not constitutional; (2) Phase 0 first with per-family measurements before gate ratification; (3) corpus expansion approved for underrepresented families; (4) S2821 harness reconciliation required; (5) two-axis routing pressure-test in Phase 0; (6) routing = boundary, fusion = downstream, NO RRF in Phase 0.
  - S2821 Phase-0 methodology joint SIGN (post-D-verdict) — Rigby AGREE no blockers with 4 schema refinements: strict/loose target-set split + answer_mode field (IS_DOC/ABOUT_TOPIC/POINTER_DOC) + has_literal_identifier derived feature + COUNT elevated to HIGH consequence. Zoom-out blindspot: intent may need user-context feature; treat "context needed" as first-class classifier output. tool_runs non-empty (search_docs × 2 + kb_tool.semantic_search × 2 + repo_tool).
frozen: true
---

# S2821 Semantic Retrieval Evaluation + Routing-First Pivot + Phase-0 Methodology — Ratification Record

Frozen canonical record of Chris's ratification of the S2822 routing-first architectural direction on 2026-07-18 AND the Rigby-joint-signed Phase-0 methodology proposal (pending Chris ratification at S2822 open). Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-18 (evening; America/Denver operator timezone)
- **Session:** S2821 (direct successor to S2820 lexical-pilot feature-complete close)
- **Scope:** S2820 §7 Chris pivot directive execution (evaluate semantic retrieval against accidentally-built benchmark corpus) + Chris close-adjacent routing-first architectural re-framing + Phase-0 methodology proposal for S2822.
- **Motivation:** S2820 closed with lexical pilot chain FEATURE COMPLETE + Chris directive to evaluate semantic retrieval. S2821 executed the evaluation and drafted Path B (Hybrid). Mid-close-adjacent, Chris re-framed: "S2821 did not primarily discover that hybrid retrieval is best. It discovered that different retrieval substrates excel at different retrieval intents. The next architectural question therefore is not 'How do we merge lexical and semantic?' Instead ask 'How do we determine WHICH retrieval substrate should answer WHICH class of query?'" This reframes S2822 from hybrid-merge to intent-routing.
- **Ratifier:** Chris (three D-verdicts across the arc: (1) initial evaluation directive at S2820 close; (2) Path B pressure-test → routing-first re-framing; (3) D-VERDICT S2822 ROUTING PREP with 6 refinements).

---

## §2. Ratified Deliverables

### §2.1 Chris routing-first architectural direction — RATIFIED

Chris D-verdict verbatim excerpt (routing-first re-framing):

> "S2821 did not primarily discover that 'hybrid retrieval is best.' It discovered that different retrieval substrates excel at different retrieval intents. The next architectural question therefore is not: 'How do we merge lexical and semantic?' Instead ask: 'How do we determine WHICH retrieval substrate should answer WHICH class of query?' Please prepare S2822 around retrieval routing rather than retrieval fusion. The routing decision is the architectural boundary. Fusion is an implementation detail."

Chris D-verdict verbatim excerpt (S2822 ROUTING PREP with 6 refinements — condensed):

1. **Taxonomy** — 6-family working taxonomy (COUNT / PROCEDURAL / DISCOVERY / IDENTITY / SELF-REFERENCE / CONCEPTUAL); Phase 0 explicitly permitted to merge/split/rename/reject.
2. **Phase 0 first** — feasibility check before routing-table implementation. NO global 80% gate. Measure per-family accuracy + confusion matrix + ambiguous rate + misroute consequence + deterministic abstention. Propose gate only after those measurements. High global score must not conceal failure in thin high-consequence families.
3. **Corpus expansion** — approved for PROCEDURAL/IDENTITY/SELF-REFERENCE/CONCEPTUAL + ambiguous/multi-intent variants. Each row records: query string, intended family, correct target or expected behavior, label rationale, acceptable secondary family, misroute consequence. Don't generate queries merely to validate taxonomy.
4. **S2821 harness reconciliation** — resolve 13-vs-10 discrepancy before Phase-0 corpus expansion. Options: (A) execute C2/C3/C5 under locked mechanisms + update aggregates; (B) formally correct harness definition. Don't carry "13-query benchmark" forward if only 10 measured.
5. **Routing model pressure-test** — test whether flat intent label sufficient OR routing needs two axes (subject/topic + requested relationship: LOCATE/EXPLAIN/DISCOVER/RETURN_CANONICAL/EXECUTE). Sharpens IS-ness/aboutness.
6. **Architectural boundary retained** — routing = boundary; fusion = downstream, per-family implementation detail. Do NOT build RRF or global fusion during Phase 0.

### §2.2 S2822 Phase-0 methodology proposal — PROPOSED (pending Chris ratification at S2822 open)

See §7 for detailed methodology. Rigby AGREE, no blockers, with 4 schema refinements (booked in §7).

---

## §3. Empirical Evidence (per PLAYBOOK-6.10.9 verified-state outcome)

**Stable-state pointer:** measurements below captured against branch HEAD `b6d051dd1` (S2820 close cascade). No code changes this session; retrieval state deterministic across dispatches (cached embedding hits + pgvector similarity).

### §3.1 Benchmark corpus (S2820 §5 codified; reconciled from "13 queries" to "13-row eval matrix over 10 unique query texts")

C2/C3/C5 share query text with Q7/Q8/Q1. Formal correction booked: S2821 benchmark = 13-row evaluation matrix over 10 unique query texts (3 alternate labelings from T3 §7 audit).

### §3.2 Measurement — 30 dispatches (10 unique query texts × 3 mechanisms)

Full evaluation script + results embedded below for provenance. Mechanism definitions locked:
- **M1 defaults:** `search_embeddings(query, limit=3)` with `similarity_threshold=0.4` (default), all filters None/False
- **M2 authority_weighted:** M1 + `authority_weighted=True`
- **M3 include_superseded:** M1 + `include_superseded=True`

All queries used EXACT strings (no paraphrase).

### §3.3 Aggregate success@3

Under three interpretations to preserve honest accounting:

| Mechanism | 10-row original | 13-row LOOSE (C2 accepts 2701 alone) | 13-row STRICT (C2 requires 2701+2700 both) |
|---|---|---|---|
| M1 defaults | 3/10 = 30% | 4/13 = 31% | **3/13 = 23%** |
| M2 authority_weighted | 2/10 = 20% | 3/13 = 23% | **2/13 = 15%** |
| M3 include_superseded | 7/10 = 70% | 8/13 = 62% | **7/13 = 54%** |

**Direction preserved across all three interpretations:** M3 > M1 > M2.

**Verified state (i)** — evidence-first criterion discipline held (per S2819 §5.1 methodology + PLAYBOOK-6.10.9): each success@3 verdict derived from live pgvector cosine similarity + T3 §7 or S2820 §5 labels, not aspirational assertions.

**Verified state (ii)** — direction preserved: M3 dominates M1 dominates M2 across 10-row, 13-row LOOSE, 13-row STRICT interpretations.

**Verified state (iii)** — regression signals surfaced:
- **M2 authority_weighted DEGRADES vs M1** across all interpretations (23% vs 31% loose; 15% vs 23% strict). Cycle 1A KFI-3 ADR-0130 was not validated against this benchmark before ratification.
- **Semantic default `include_superseded=False` silently excludes archived docs** that are correct answers for count queries. 4/5 count queries recover under M3.
- **Semantic fails Q1 (spider count) while succeeding Q4/Q6 (celery/list-spider) with same target.** Chunk-boundary structural issue, corroborated by C5 (same query as Q1, same failure pattern).
- **Q5 procedural + Q8 self-ref-nav-to-pointer + C3 self-ref-direct fail all mechanisms.** Semantic cannot self-match or intent-detect.

### §3.4 Per-query cross-mechanism matrix (13-row LOOSE)

```
Q1  spiders count      : M1=n M2=n M3=n  (chunk-boundary structural fail)
Q2  agents count       : M1=n M2=n M3=Y  (M3 rank 2 sim 0.624)
Q3  db models count    : M1=n M2=n M3=Y  (M3 rank 3 sim 0.582)
Q4  celery count       : M1=n M2=n M3=Y  (M3 top-1 sim 0.66)
Q5  add spider (proc)  : M1=n M2=n M3=n  (both substrates fail)
Q6  list spiders       : M1=n M2=n M3=Y  (M3 top-1 sim 0.612)
Q7  Group 2700 T1      : M1=Y M2=Y M3=Y  (2701 rank 2 all mechs — semantic native win)
Q8  00-START (nav-ptr) : M1=n M2=n M3=n  (returns handoffs mentioning 00-START)
C1  Colorado JDF       : M1=Y M2=Y M3=Y  (semantic native win)
C2  Group 2700 T1      : M1=Y M2=Y M3=Y  (LOOSE — 2701 rank 2 accepted)
C3  00-START (direct)  : M1=n M2=n M3=n  (semantic can't self-match)
C4  2701 filename      : M1=Y M2=n M3=Y  (M2 authority_weighted degrades)
C5  spiders count      : M1=n M2=n M3=n  (same as Q1)
```

### §3.5 Bench script (frozen at merge for reproduction)

```python
"""S2821 harness reconciliation — 13 rows (Option A execute).

Adds C2/C3/C5 with T3 §7 target sets. Same query TEXT as Q7/Q8/Q1
(retrieval identical) but different target labeling per T3 §7 vs S2820 §5.
"""
from core.rag_integration import search_embeddings

BENCHMARK = [
    ("Q1", "How many spiders do we have", ["PLATFORM_INVENTORY.md"], "S2818"),
    ("Q2", "How many agents do we have", ["PLATFORM_INVENTORY.md"], "S2818"),
    ("Q3", "How many database models", ["PLATFORM_INVENTORY.md"], "S2818"),
    ("Q4", "How many celery tasks", ["PLATFORM_INVENTORY.md"], "S2818"),
    ("Q5", "add a new spider to the network", ["AGENTS_REFERENCE.md"], "S2820 baseline"),
    ("Q6", "list all spiders", ["PLATFORM_INVENTORY.md"], "S2819"),
    ("Q7", "Group 2700 docs restructuring T1 audit",
     ["SESSION_2801_", "SESSION_2811_", "2701_docs_inventory_topology_audit"], "S2820 §5"),
    ("Q8", "00-START-NEXT-SESSION", ["CLAUDE.md", "00-START-NEXT-SESSION.md"], "S2820 §5"),
    ("C1", "Colorado JDF form-selection intelligence", ["SESSION_2808_"], "T3 C1"),
    # C2 STRICT per Rigby joint SIGN — both required:
    ("C2", "Group 2700 docs restructuring T1 audit",
     ["2701_docs_inventory_topology_audit", "2700_docs_restructuring_domain_scoping"], "T3 C2 STRICT"),
    ("C3", "00-START-NEXT-SESSION", ["00-START-NEXT-SESSION.md"], "T3 C3 direct"),
    ("C4", "2701_docs_inventory_topology_audit", ["2701_docs_inventory_topology_audit"], "T3 C4"),
    ("C5", "How many spiders do we have", ["PLATFORM_INVENTORY.md"], "T3 C5"),
]

MECHANISMS = [("M1", {}), ("M2", {"authority_weighted": True}), ("M3", {"include_superseded": True})]

# Full implementation: see /tmp/s2821_bench_v2.py or reconstruct from above.
```

---

## §4. SIGN Sessions

### §4.1 Measurement plan open scope SIGN

Rigby AGREE ship M1/M2/M3 methodology as-is. Locked mechanism params + query strings. Q7 handoff-visibility hypothesis pre-tested. Substantive tool_runs.

### §4.2 Task 4/5 recommendation SIGN

Path B (Hybrid) proposed. Rigby AGREE with 2 refinements: include_superseded causal chain softened (needs Document-table inspection to assert sync mapping); legacy architecture doc dominance reframed as "retrieval objective mismatch" not "data quality."

### §4.3 Chris D-verdict — routing-first re-framing

Full text captured in §2.1.

### §4.4 Phase-0 methodology SIGN

Rigby AGREE no blockers with 4 schema refinements booked. Zoom-out blindspot flagged: "context needed" as first-class classifier output.

---

## §5. Novel finding — routing IS the architectural boundary

Chris's re-framing at close-adjacent captures something the Path B recommendation missed: **the primary architectural question isn't "how do we merge substrates" but "how do we know which substrate to invoke."** Fusion strategies (RRF, weighted merge) are per-family implementation choices; they don't determine the substrate boundary.

Concrete evidence:
- **Semantic solves DISCOVERY natively** (Q7, C1 all mechs Y). No fusion needed.
- **Lexical solves IDENTITY natively** (C4 M1 rank 1). Semantic returns *referencing docs*, not the target itself.
- **Neither substrate solves PROCEDURAL** (Q5 fail all). Fusion doesn't fix this — needs new mechanism.
- **Lexical alone solves SELF-REFERENCE-NAV-TO-POINTER** (Q8 CLAUDE.md#6 pointer). Semantic returns aboutness handoffs.

Per-family substrate specialization is the architectural fact. Routing table is the deliverable. Fusion policy is downstream.

---

## §6. Limitations & Known Findings

### §6.1 M3 default flip candidate deferred
`include_superseded=False → True` semantic default flip surfaced as a defect fix (semantic silently excludes ARCHIVED docs that ARE the correct answer). Not shipped this session — Chris freeze extends to semantic default posture until S2822 explicitly ratifies changes.

### §6.2 M2 authority_weighted regression
Cycle 1A KFI-3 ADR-0130 authority_weighted mode DEGRADES vs M1 default on this benchmark (15% vs 23% STRICT). Do NOT auto-adopt in routing table. Revisit only after benchmark refresh with query set that stress-tests authority weighting.

### §6.3 CONCEPTUAL family unmeasured
Zero conceptual queries in S2821 benchmark. Structurally missing — Phase-0 corpus expansion candidate.

### §6.4 Chunk-boundary fragility
Q1 fails while Q4/Q6 succeed with same target (PLATFORM_INVENTORY.md). Same query text as C5 (also fails). Deterministic chunk-boundary structural issue — retrieval unit is chunk, target evaluation is document. Suspected root cause of many false-negatives. Document-level aggregation is a candidate S2822+ enhancement.

### §6.5 Benchmark thin in 4 families
PROCEDURAL, IDENTITY, SELF-REFERENCE, CONCEPTUAL at n≤1 (or 0 for CONCEPTUAL). Per-family winner declarations for these families are UNCERTAIN pending corpus expansion.

---

## §7. Phase-0 methodology proposal (PROPOSED — pending Chris ratification at S2822 open)

### §7.1 Working taxonomy (6 families — Chris R#1 explicit "working, not constitutional")

COUNT / PROCEDURAL / DISCOVERY / IDENTITY / SELF-REFERENCE / CONCEPTUAL. Phase 0 explicitly permitted to merge/split/rename/reject based on measured confusion.

### §7.2 Expanded 33-row corpus (S2821 baseline 13 + 20 additions)

- PROCEDURAL +4 (P1-P4): verb-object variants
- IDENTITY +4 (I1-I4): filename shape variants  
- SELF-REFERENCE +3 (S1-S3): both nav-to-pointer + direct variants
- CONCEPTUAL +5 (K1-K5): structurally missing family (K5 revised per Rigby to remove unique-ID tokens)
- AMBIGUOUS/MULTI-INTENT +4 (A1-A4): intentional stressors

Full query set in handoff §6 + Phase-0 execution creates the labeled corpus file.

### §7.3 Label schema (Chris-listed fields + 4 Rigby refinements)

```
query_id                       – unique short label (Q/C/P/I/S/K/A prefix + integer)
query_text                     – exact string
intended_family                – primary from taxonomy
secondary_family               – optional; genuinely ambiguous
known_correct_target_strict    – must-hit target(s) [Rigby refinement]
known_correct_target_loose     – acceptable alternatives [Rigby refinement]
expected_behavior              – return-target | return-any-of-list | abstain | return-none
answer_mode                    – IS_DOC | ABOUT_TOPIC | POINTER_DOC [Rigby refinement]
has_literal_identifier         – derived: path/filename/stem in query [Rigby refinement]
label_rationale                – sentence per row
misroute_consequence           – HIGH | MEDIUM | LOW
safety_level                   – optional for PROCEDURAL destructive
```

### §7.4 Ambiguity + abstention policy (tri-state + wrong-but-plausible)

CONFIDENT / AMBIGUOUS / UNCLASSIFIABLE (abstain). Measurement adds: wrong-but-plausible failure mode (semantic returns high-similarity aboutness when user wanted IS_DOC — looks successful unless scored against answer_mode).

### §7.5 Two classifier candidates

- **CLASSIFIER A (FLAT):** regex/keyword per family → intent label or ABSTAIN
- **CLASSIFIER B (TWO-AXIS):** regex/keyword per (subject_type, relationship) tuple → mapped to intent via composition. Subject types {OBJECT, DOC, CONCEPT, PROCEDURE, POINTER}; relationships {LOCATE, EXPLAIN, DISCOVER, RETURN_CANONICAL, EXECUTE, POINT} (POINT is proposed addition based on Q8 evidence — Rigby AGREE distinct from LOCATE).

Both consume `has_literal_identifier` derived feature.

### §7.6 Per-family gate (Chris R#2 explicit — NO global 80%)

| Family | Consequence | Classifier floor | Substrate floor |
|---|---|---|---|
| COUNT | HIGH [Rigby-elevated] | ≥90% | ≥85% |
| IDENTITY | HIGH | ≥90% | ≥85% |
| SELF-REFERENCE | HIGH | ≥90% | ≥85% |
| PROCEDURAL | MEDIUM | ≥75% | ≥70% |
| DISCOVERY | LOW | ≥70% | ≥60% |
| CONCEPTUAL | LOW | ≥70% | ≥60% |

GLOBAL GATE = ALL per-family gates pass. High global score does NOT pass if HIGH-consequence floors miss.

Thresholds are PROPOSED — final calibration comes from Phase-0 measurement.

### §7.7 Two-axis routing pressure-test (Chris R#5)

Two collapse candidates pre-execution:
1. **IDENTITY + SELF-REFERENCE-C3 → (DOC, LOCATE)** — taxonomy folds 6→5 if confirmed
2. **POINT distinct from LOCATE** (Q8 shape; Rigby AGREE tool-grounded)

Phase-0 tests whether these hold across expanded corpus.

### §7.8 Blindspot flagged pre-execution (Rigby)

Phase-0 assumes intent classifiable from query string alone. Dominant ambiguity driver may prove to be **user context**. Treat "context needed" as first-class classifier output. Elevated AMBIGUOUS/UNCLASSIFIABLE rates on A1/A3/A4-type rows will surface this.

### §7.9 Non-recommendations retained (Chris R#6)

- NO RRF / global fusion during Phase 0
- NO taxonomy constitutionalization from S2821 evidence alone

---

## §8. Follow-On (S2822)

**Sole recommended direction (Chris-ratified architectural + Rigby joint-signed methodology):**

**Ratify Phase-0 methodology + execute Phase-0.** Concrete first steps for S2822 open:

1. Chris D-verdict on Phase-0 methodology proposal (§7 above): as-is, or with revisions
2. Corpus expansion authoring (20 new labeled queries per §7.3 schema)
3. Classifier A (flat) build + measurement against 33-row corpus
4. Classifier B (two-axis) build + measurement
5. Per-family precision/recall/F1 + confusion matrix + ambiguous-rate + abstention-rate + wrong-but-plausible rate
6. Gate calibration from measurement (per §7.6 proposal frame)
7. Two-axis collapse candidate verification (IDENTITY + SELF-REF-C3 fold; POINT distinct)
8. Route findings to Chris for Phase-1 (routing-table build) gate decision

**Non-goals for S2822 Phase 0:**
- No RRF / global fusion (Chris R#6)
- No taxonomy constitutionalization (Phase 0 CAN reject families)
- No routing-table implementation (Phase-1 after gate passes)
- No code substrate change (lexical policy frozen; semantic default flip deferred)

---

## §9. Provenance

- **Session:** S2821 (direct successor to S2820 close; opens discovery-layer semantic branch)
- **Session pin:** `pa-c884459957614bbd` (label `s2821-semantic-evaluation`; minted at S2821 open via `session_lifecycle open`; retired at close force=true fifty-second consecutive per S2770+ pattern)
- **Baseline HEAD:** `b6d051dd1` (S2820 close cascade)
- **Ratification HEAD:** (filled at merge)
- **Merged PR:** (filled at merge)
- **Tools used:** Read for existing state; Write for handoff + envelope; Bash for `python manage.py session_lifecycle open` + benchmark execution via `python -c` Django setup; Rigby `repo_tool` + `search_docs` + `kb_tool.semantic_search` throughout SIGN cycles.
- **OP3 pattern:** 3 SIGN cycles this session (measurement plan / task 4-5 recommendation / Phase-0 methodology). All tool-grounded. Chris D-verdict interposed between cycles 2 and 3.
- **Anti-rubber-stamp discipline:** all 3 SIGN cycles verified non-empty tool_runs. Rigby's live probes surfaced 5+ substantive refinements (Q7 handoff-visibility pre-test; canonical_authority scope-tightener; include_superseded causal chain softening; C2 target-set strict/loose split; K5 unique-ID backdoor; COUNT elevation to HIGH consequence).
- **Twin-pointer discipline:** this envelope in `docs/research/implementation/`; workspace deliverable mirror deferred per S2818/S2819/S2820 pattern.
- **Chris re-framing power:** the routing-first re-framing changed the S2822 shape from hybrid-merge to intent-routing. Novel arc-shape pattern: **mid-evaluation architectural re-framing captured as ratifiable direction**.

---

**End of ratification record. Frozen at merge. Discovery-layer arc: lexical branch FEATURE COMPLETE (S2818/S2819/S2820); semantic branch EVALUATED (S2821); routing-first Phase-0 methodology PROPOSED (pending Chris ratification at S2822 open).**
