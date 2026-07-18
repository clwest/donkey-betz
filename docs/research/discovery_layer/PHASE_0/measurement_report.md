# Phase-0 Measurement Report — S2822

**Date:** 2026-07-18 (S2822 Phase-0 execution)
**Corpus:** `corpus.json` (33 rows, schema v0 per `field_dictionary.md`)
**Governing envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md`
**Classifiers:** `classifier_a.py` (flat regex/keyword per family) · `classifier_b.py` (two-axis subject×relationship)
**Analysis script:** `analyze.py` · **Raw JSON:** `analysis_full.json`

> Per Chris R3: measurements below use **query text only**. No conversational/workspace/task context fed to classifiers. Post-hoc context-needed analysis in §4.
> Per Chris R6: evidence in this report is presented before any recommendation is drawn. Recommendations live in `RECOMMENDATION_PHASE0_SUMMARY.md`.

---

## §1. Corpus provenance breakdown (R1 compliance)

| Tier | Count | % | Sources |
|---|---|---|---|
| **P1 (real operational)** | 5 | 15% | Rigby `search_docs`/`kb_tool.semantic_search`/`deliverable_tool.search` invocations logged in handoffs S1142, S1224, S1234, S1241 (×2) |
| **P2 (observed failure cases)** | 10 | 30% | S2818/S2819/S2820/S2821 baseline (Q1-Q8, C1, C4) — the "accidentally built" benchmark per S2820 §5 |
| **P3 (synthetic gap-fill, gap-tagged)** | 18 | 55% | PROCEDURAL (3 to family thin) · IDENTITY (4 for filename-shape variants + code-file variant) · SELF-REFERENCE (2 for nav/descriptor variants) · CONCEPTUAL (5, family had ZERO baseline rows) · AMBIGUOUS/MULTI-INTENT (4 stressors) |

**R1 honest assessment:** The P1/P2/P3 split is heavier on P3 than Chris R1 hierarchy prefers. Real-query harvest yield was lower than Rigby estimated (50-200 candidates) because handoffs mostly reference query strings inline in narrative, not as first-class harvest-able artifacts. The 5 P1 rows are direct grep hits from prior sessions' documented tool invocations.

---

## §2. Classifier A (flat) vs Classifier B (two-axis) — side-by-side per-family

| Family | n | Consequence | Prior floor | A F1 | B F1 | Δ (B−A) | Both meet prior? |
|---|---|---|---|---|---|---|---|
| COUNT | 5 | HIGH | 0.90 | **1.00** | **1.00** | 0.00 | ✅ both |
| PROCEDURAL | 4 | MEDIUM | 0.75 | **1.00** | **1.00** | 0.00 | ✅ both |
| DISCOVERY | 9 | LOW | 0.70 | **0.36** | **0.50** | +0.14 | ❌ NEITHER |
| IDENTITY | 6 | HIGH | 0.90 | **0.91** | 0.83 | −0.08 | ✅ A only |
| SELF-REFERENCE | 3 | HIGH | 0.90 | **1.00** | 0.86 | −0.14 | ✅ A only |
| CONCEPTUAL | 6 | LOW | 0.70 | **0.91** | **0.91** | 0.00 | ✅ both |

**Direction preserved:** Classifier A dominates B on HIGH-consequence families (IDENTITY, SELF-REFERENCE). Classifier B is only better on DISCOVERY, and even there both fail the LOW prior.

### §2.1 Precision / Recall / TP-FP-FN detail (Classifier A)

Per Rigby SIGN Q1 refinement — integer TP/FP/FN counts included as checksums for tool-side verification (floats may be redacted in some tool views).

| Family | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| COUNT | 5 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| PROCEDURAL | 4 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| DISCOVERY | 2 | 0 | 7 | 1.00 | **0.22** | 0.36 |
| IDENTITY | 5 | 0 | 1 | 1.00 | 0.83 | 0.91 |
| SELF-REFERENCE | 3 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| CONCEPTUAL | 5 | 0 | 1 | 1.00 | 0.83 | 0.91 |

**Pattern:** Classifier A is perfectly precise (never emits wrong family confidently) but under-recalls on DISCOVERY (2/9 correct) and misses 1 IDENTITY + 1 CONCEPTUAL.

### §2.2 Precision / Recall / TP-FP-FN detail (Classifier B)

| Family | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| COUNT | 5 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| PROCEDURAL | 4 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| DISCOVERY | 3 | 0 | 6 | 1.00 | **0.33** | 0.50 |
| IDENTITY | 5 | 1 | 1 | 0.83 | 0.83 | 0.83 |
| SELF-REFERENCE | 3 | 1 | 0 | 0.75 | 1.00 | 0.86 |
| CONCEPTUAL | 5 | 0 | 1 | 1.00 | 0.83 | 0.91 |

**Pattern:** Classifier B emits false positives on HIGH-consequence families (1 IDENTITY FP; 1 SELF-REF FP) — the two axes let confident-wrong outputs slip through.

### §2.3 Aggregate output distributions

| Output class | A (flat) | B (two-axis) |
|---|---|---|
| Confident family emission (rate) | 79% | 82% |
| AMBIGUOUS rate | 21% | 0% |
| UNCLASSIFIABLE rate | 3% | 18% |
| CONTEXT_NEEDED rate | 3% | 0% |
| Wrong-but-plausible count (R5 priority) | **0** | **2** |

Classifier B replaces A's AMBIGUOUS output with UNCLASSIFIABLE — which loses information (A distinguishes "some signal, uncertain family" from "no signal"). B also fails to detect the pronoun-only CONTEXT_NEEDED row that A catches.

---

## §3. Wrong-but-plausible catalog (R5 priority)

Per Chris R5: wrong-but-plausible receives equal-or-greater attention than obvious failures.

**Classifier A:** 0 wrong-but-plausible predictions. All A errors are AMBIGUOUS / UNCLASSIFIABLE / CONTEXT_NEEDED (honest failures, not confidently wrong).

**Classifier B:** 2 wrong-but-plausible predictions.

| Query | Intended | Predicted (B) | Root cause |
|---|---|---|---|
| R5 "BINDING DIRECTIVE" | DISCOVERY | IDENTITY | Uppercase-token detection (`_DOC_TITLE_TOKEN`) misread the controlled-phrase as filename-like. Then bare-DOC inference triggered `IDENTITY`. Would return the wrong doc type to a real user. |
| A4 "the current one" | CONCEPTUAL (with abstain expected_behavior) | SELF-REFERENCE | `_POINTER_PHRASE` matched "current" broadly. Would confidently emit self-reference target instead of surfacing context-needed. Especially concerning because ground-truth is `abstain`. |

**R5 verdict:** Classifier A's zero wrong-but-plausible is a genuine safety advantage. Classifier B's two-axis composition creates a class of failures where the wrong composed intent looks confident.

---

## §4. Context-needed analysis (R4 — measure only, do not solve)

Per Chris R4: measure how often context is required. Do NOT feed context into classifier.

### §4.1 Post-hoc "would context have helped?" analysis

3 rows were labeled at authoring time with `secondary_family` set (AMBIGUOUS ground-truth, `known_correct_target_strict=null`) — these are the ground-truth CONTEXT_NEEDED rows:

| Query | Ambiguity type | Context type that would resolve |
|---|---|---|
| A1 "how many models" | Word polysemy — "models" = DB models (COUNT→PLATFORM_INVENTORY) OR LLM models (CONCEPTUAL→providers) | **Operational** (current task/screen/recent activity would disambiguate) |
| A2 "spider network" | Bare noun phrase — DISCOVERY OR CONCEPTUAL OR IDENTITY | **Operational** (workspace/current-task) |
| A3 "session 2821" | Literal identifier + ambiguous target — handoff? envelope? both? | **Operational** (context of which artifact is under discussion) |

Additionally, A4 "the current one" has `expected_behavior=abstain` — pure conversational pronoun with no antecedent; requires **Conversational** context.

**Context type distribution (post-hoc):** 3 operational · 1 conversational · 0 repository-state.

### §4.2 Classifier CONTEXT_NEEDED detection

| Classifier | # emitted CONTEXT_NEEDED | Rows caught |
|---|---|---|
| A (flat) | 1 | A4 "the current one" (`_CONTEXT_NEEDED_PRONOUN` rule) |
| B (two-axis) | 0 | None — B's POINTER phrase pattern captured A4 as SELF-REFERENCE instead |

**Classifier detection vs post-hoc ground-truth:**
- A caught 1/4 rows where context is required (25%). Miss cases: A1/A2/A3 — the operational-context rows that need broader context-signal detection beyond pronoun-only.
- B caught 0/4 (0%). Regression vs A on this axis.

**R4 verdict:** Query-text-only classifier can catch pure conversational-pronoun cases (A4-shape) but cannot detect operational-context needed rows (A1/A2/A3-shape) — those look like normal DISCOVERY/COUNT/IDENTITY queries without context. **If a routing table dispatches A1/A2/A3-shape queries without context input, it will confidently emit a wrong answer ~50% of the time (either intended OR secondary_family target).**

Do NOT solve in Phase-0 per R4. Recorded as first-class observation for Phase-1 gate decision.

---

## §5. Per-family gate evaluation vs starting priors (R2 — priors are NOT targets)

Per Chris R2: gate values are starting priors. If evidence forces revision, recommend revised thresholds.

| Family | Prior classifier floor | Max observed F1 | Verdict |
|---|---|---|---|
| COUNT | 0.90 | 1.00 | **Prior met + significant headroom** — consider tightening to 0.95 if additional COUNT rows corroborate |
| PROCEDURAL | 0.75 | 1.00 | **Prior met + significant headroom** — consider tightening to 0.90 (family well-differentiated by verb-object shape) |
| DISCOVERY | 0.70 | 0.50 | **Prior SEVERELY missed** — classifier is fundamentally weak on this family. Recommend revised floor at 0.50 IF the routing table proceeds AND lexical is the default substrate for DISCOVERY (fusion-not-routing pattern); OR reject routing for DISCOVERY entirely. |
| IDENTITY | 0.90 | 0.91 | **Prior barely met** on Classifier A (0.91). B misses (0.83). Recommend keep prior at 0.90 with note: HIGH-consequence family; small F1 delta matters. |
| SELF-REFERENCE | 0.90 | 1.00 | **Prior met + significant headroom** on Classifier A. B misses (0.86). Recommend keep 0.90; flat classifier is the safer choice. |
| CONCEPTUAL | 0.70 | 0.91 | **Prior met + significant headroom** — consider tightening to 0.85 (family well-differentiated by explanatory question shape). |

**Global gate (all per-family gates pass):** **FAILS** — DISCOVERY family does not clear its prior on either classifier. No single classifier passes globally.

**Recommended calibration deltas (all EVIDENCE-BASED, not optimization):**
- COUNT: 0.90 → 0.95 (tighten)
- PROCEDURAL: 0.75 → 0.90 (tighten)
- DISCOVERY: 0.70 → 0.50 (loosen) IF routing table proceeds for DISCOVERY at all — OR drop DISCOVERY from routing
- IDENTITY: 0.90 → 0.90 (hold)
- SELF-REFERENCE: 0.90 → 0.90 (hold)
- CONCEPTUAL: 0.70 → 0.85 (tighten)

---

## §6. Provenance-tier stratified accuracy (major methodology finding)

| Tier | n | Classifier A accuracy | Classifier B accuracy |
|---|---|---|---|
| **P1 (real operational)** | 5 | **20%** | **20%** |
| P2 (observed failure) | 10 | 80% | 80% |
| P3 (synthetic gap-fill) | 18 | 83% | **89%** |

**Finding:** Real operational queries (P1) score DRAMATICALLY worse than synthetic queries (P3) — a 60-70 percentage-point gap. This is a stronger signal than any per-family metric.

**Why:** Real queries harvested from Rigby's own tool invocations (R1 "morning_brief workflow", R2 "agent router", R3 "AgentDecisionSummary writer", R4 "DecisionRecord boardroom", R5 "BINDING DIRECTIVE") are:
- Bare noun phrases (no verb-object cues)
- Uppercase-heavy identifier tokens (misread as IDENTITY by both classifiers)
- Short (2-3 words, well below the AMBIGUOUS bare-noun-phrase threshold)

**Implication:** Synthetic query corpora that mirror the intended taxonomy will confirm the classifier "works" — but real user queries stress-fracture the classifier assumptions. R1 provenance hierarchy is load-bearing; without it, we'd have concluded Classifier A hits 85%+ accuracy from a P3-heavy corpus.

**Corpus bias caveat:** 15% P1 rows is under-representative. If real query corpus were 50%+, aggregate accuracy would likely be 40-50%, not 80%+.

---

## §7. Two-axis pressure-test findings (S2821 §7.7 collapse candidates)

Per Classifier B evaluation:

### §7.1 IDENTITY + SELF-REFERENCE-C3 → (DOC, LOCATE) collapse candidate

- **IDENTITY → (DOC, LOCATE): 83% support** (5/6 IDENTITY rows classified as subject=DOC + relationship=LOCATE). Strong evidence IDENTITY reduces to (DOC, LOCATE) tuple.
- **SELF-REFERENCE → (DOC, LOCATE): 0% support** (0/3 SELF-REFERENCE rows). SELF-REFERENCE rows route through subject=POINTER + relationship=POINT instead.

**Verdict:** Collapse candidate is **PARTIALLY REFUTED**. IDENTITY collapses cleanly to (DOC, LOCATE); SELF-REFERENCE-C3 does NOT — it uses a distinct (POINTER, POINT) axis pair. **Recommendation:** Preserve IDENTITY vs SELF-REFERENCE as distinct families; do NOT fold 6→5.

### §7.2 POINT distinct from LOCATE

- **4 POINT hits vs 8 LOCATE hits** on the 33-row corpus. Both relationships are populated; neither is empty.
- POINT hits: Q8 "00-START-NEXT-SESSION", S1 "the next session start doc", S2 "where do I read this project's rules", A4 "the current one"
- LOCATE hits: C4, I1, I2, I3, I4 (all IDENTITY) plus Q7, C1, C2 (DISCOVERY with strong subject signal)

**Verdict:** POINT relationship is **CONFIRMED DISTINCT** from LOCATE. S2821 §7.5 Q8-evidence hypothesis holds. Do NOT collapse POINT into LOCATE.

---

## §8. Confusion matrices (raw evidence)

### Classifier A

```
                        AMBIGUOUS CONCEPTUAL CONTEXT_NE      COUNT  DISCOVERY   IDENTITY PROCEDURAL SELF-REFER UNCLASSIFI
CONCEPTUAL                      0          5          1          0          0          0          0          0          0
COUNT                           0          0          0          5          0          0          0          0          0
DISCOVERY                       6          0          0          0          2          0          0          0          1
IDENTITY                        1          0          0          0          0          5          0          0          0
PROCEDURAL                      0          0          0          0          0          0          4          0          0
SELF-REFERENCE                  0          0          0          0          0          0          0          3          0
```

### Classifier B

```
                       CONCEPTUAL      COUNT  DISCOVERY   IDENTITY PROCEDURAL SELF-REFER UNCLASSIFI
CONCEPTUAL                      5          0          0          0          0          1          0
COUNT                           0          5          0          0          0          0          0
DISCOVERY                       0          0          3          1          0          0          5
IDENTITY                        0          0          0          5          0          0          1
PROCEDURAL                      0          0          0          0          4          0          0
SELF-REFERENCE                  0          0          0          0          0          3          0
```

---

## §9. Field dictionary derivation accuracy (auxiliary)

`has_literal_identifier` derived from query text vs labeled value: **87.9% match (29/33)** on both classifiers (same rule).

The 4 mismatches suggest the derivation regex is slightly off. Not load-bearing for family classification — auxiliary feature.

---

## §10. Raw data pointers

- Full analysis JSON: `docs/research/discovery_layer/PHASE_0/analysis_full.json` (826 lines; per-row + confusion matrices + all metrics)
- Corpus: `docs/research/discovery_layer/PHASE_0/corpus.json` (33 rows, schema v0)
- Classifier A source: `docs/research/discovery_layer/PHASE_0/classifier_a.py`
- Classifier B source: `docs/research/discovery_layer/PHASE_0/classifier_b.py`
- Analysis harness: `docs/research/discovery_layer/PHASE_0/analyze.py`
- Field dictionary: `docs/research/discovery_layer/PHASE_0/field_dictionary.md`

---

**End of measurement report. Recommendation for Chris in `RECOMMENDATION_PHASE0_SUMMARY.md`.**
