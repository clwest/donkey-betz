# Session 2820 — Orientation-doc exclusion + LEXICAL PILOT FEATURE COMPLETE

**Date:** 2026-07-18 (afternoon; third same-day pilot in discovery-layer arc; S2818 → S2819 → S2820)
**Session:** S2820
**PRs shipped:** 1 feature (#TBD) + 1 close cascade (#TBD)
**Predecessor:** [SESSION_2819 Shape C intent-gating](SESSION_2819_SHAPE_C_INTENT_GATING.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 in-session recycle (post-implementation) + 1 post-merge + 1 close-cascade recycle

---

## §1 — Ship summary

**One PR ships the LAST lexical policy in the discovery-layer arc.** `_EXCLUDED_FILE_PATHS = frozenset({"00-START-NEXT-SESSION.md"})` in `core/rag.py`. Chris ratified this as "feature complete" for the lexical pilot chain S2818/S2819/S2820 and pivoted S2821+ to semantic retrieval evaluation against the benchmark corpus this arc built.

### PR #TBD — S2820 orientation-doc exclusion

**Files:**
- `core/rag.py` — new `_EXCLUDED_FILE_PATHS` frozenset + one `if row.get("file", "") in _EXCLUDED_FILE_PATHS: continue` inside `top_k` scoring loop, before the base-score computation.
- `core/tests/test_rag_orientation_doc_exclusion_2820.py` (new) — 5 tests (2 unit + 3 integration).
- `docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md` (new envelope + benchmark-corpus §5 + Chris's feature-complete directive §4.3).

**Key results (4-query baseline, evidence-first per S2819 §5.1 lesson):**

| Q | Baseline top-1 | 00-START rank | **Post-fix top-1** | 00-START post? | Verdict |
|---|---|---|---|---|---|
| (a) "add a new spider to the network" | 00-START#3 | **#1** (contamination) | **AGENTS_REFERENCE.md#35** | absent | **PASS** |
| (b) "Group 2700 T1 audit" | SESSION_2801 handoff | not in set | SESSION_2801 handoff | absent | **PASS** unchanged |
| (c) "00-START-NEXT-SESSION" self-ref | CLAUDE.md#6 pointer | not in set | CLAUDE.md#6 pointer | absent | **PASS** unchanged |
| (d) "How many spiders" | PLATFORM_INVENTORY.md#1 | not in set | PLATFORM_INVENTORY.md#1 | absent | **PASS** S2818 preserved |

**4/4 PASS.** Cross-cycle verification: post-fix Q(a) top-3 matches the S2818 §3.1 pre-pilot-arc baseline EXACTLY (AGENTS_REFERENCE + BACKEND_INTEGRATION_PROGRESS + LETTER_TO_FUTURE_CLAUDE). The 3-arc pilot chain successfully re-shaped counts + eliminated non-counts monoculture + eliminated orientation-doc contamination while leaving non-counts queries in their pre-pilot baseline shape.

---

## §2 — Rigby joint SIGN — TENTH-CONSECUTIVE OP3-ADJACENT + FIRST IN-LOOP VARIANT

**Pin:** `pa-a0dd969db550488d` (S2820 open fresh mint; retired at close, force=true, fifty-first consecutive per S2770+ pattern).

**Single continuous conversation, not separate open + post-authoring turns.** The OP3 discipline was preserved through Rigby's in-loop presence throughout: baseline capture → mechanism recommendation → in-conversation post-implementation measurement → 4/4 PASS verification. Envelope §4.2 documents this as a valid OP3 variant for narrow pilots where the whole cycle happens in a single conversation.

### 2.1 Open scope SIGN highlights

- **Q1 Baseline capture — evidence-first (per S2819 §5.1 lesson).** 4 live queries dispatched; baseline shapes locked the per-query success criteria. First time the S2819 methodology gotcha was applied in the very next arc after being surfaced.
- **Q2 Option B recommended.** Retrieval-time hard exclusion in `core/rag.py`. Simplest / most reversible / consistent with S2818/S2819 pattern / categorical stance justified.
- **Q3 Scope 00-START only.** Rigby verified S2819 handoff contains the phrase but is EMPIRICALLY absent from Q1(a) returned set. Scope creep avoided.
- **Q4 ARCHITECTURAL INFLECTION zoom-out (novel):** "We're near the point where more lexical ranker patches have diminishing ROI." Pattern: authority boosts (S2818) → intent gating (S2819) → exclusions (S2820) is exactly what embedding-based retrieval solves natively. Recommendation: next arc pivots to semantic retrieval evaluation.

### 2.2 Chris D-verdict + strategic pivot

Chris's response:

> "Approve S2820. Freeze lexical policy after it ships. Declare the current lexical pilot 'feature complete.' Spend the next engineering cycle evaluating semantic retrieval against the benchmark corpus you've accidentally built during the docs audit."

Four ratifications: (1) approve S2820; (2) freeze lexical policy — no more patches to AUTHORITY_FILE_BONUS / _COUNT_INTENT_PATTERNS / _EXCLUDED_FILE_PATHS; (3) declare lexical pilot feature complete; (4) pivot next cycle to semantic retrieval evaluation against the benchmark corpus this arc built.

---

## §3 — Novel precedent

1. **First "feature complete" declaration for a pilot chain.** S2818 + S2819 + S2820 = complete lexical policy for the discovery-layer arc. No follow-up "Shape D" iterations in this substrate. Book it.
2. **First in-loop OP3 variant.** Rigby's continuous conversation replaced separate post-authoring turn. Documented as valid for narrow pilots where the whole cycle happens in a single conversation.
3. **First evidence-first baseline capture applying S2819 §5.1 methodology gotcha.** The gotcha was surfaced in S2819 §5.1; S2820 opened by explicitly requesting empirical baseline as the criterion-grounding evidence rather than starting with aspirational targets. **Second empirical trigger for the potential Playbook v0.9-adjacent amendment** (first trigger: S2819 §5.1 itself; second trigger: S2820's compliance with it). One more trigger and this crosses the two-triggers threshold from Playbook §20.
4. **First "accidentally-built benchmark corpus" recognition.** Chris's pivot directive named a byproduct of the arc: 13+ queries with known-correct labels derived from either T3 audit or evidence-first baseline capture. Now the S2821 evaluation harness for semantic retrieval candidates.
5. **First direct-continuation three-pilot arc chain in a single day.** S2818 → S2819 → S2820 all shipped 2026-07-18, each building on the previous, closing the discovery-layer arc's lexical branch completely. Novel arc-shape: focused pilot chain (not audit-style research arc).
6. **First 3-arc chain with 4-verdict Chris D-response.** Chris's approval-plus-directive combined tactical ship approval with strategic freeze + declaration + pivot. Sets precedent for how to close a multi-arc pilot chain: don't just approve the last patch, name the completeness + set the next substrate.

---

## §4 — What shipped vs what didn't

**Shipped:**
- `_EXCLUDED_FILE_PATHS` mechanism + skip check in `top_k`
- 5 tests validating exclusion holds unconditionally
- Envelope with PLAYBOOK-6.10.9 evidence + §5 benchmark corpus recognition + §4.3 Chris directive + §7 sole recommended S2821 direction

**Not shipped (frozen or queued):**
- More lexical patches — FROZEN per Chris directive §4.3 (no additions to AUTHORITY_FILE_BONUS / _COUNT_INTENT_PATTERNS / _EXCLUDED_FILE_PATHS)
- Handoff exclusion — DEFERRED (empirically not needed at S2820 baseline; if surfaces later, would live in NEW substrate not this frozen one)
- S2820 dev-only debug score exposure — not needed; 4/4 PASS achieved without it
- Playbook v0.9-adjacent amendment for success-criterion hygiene — 2 triggers now (S2819 §5.1 + S2820 compliance); wait for third before codification per §20

---

## §5 — Ledger + provenance

- **Zoom-out ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows at S2820 open; folds this session:
  - Fold A (Rigby SIGN Q4 architectural-inflection zoom-out): `future_trigger` — highest-impact fold this session; drives S2821+ direction per Chris pivot directive.
  - Fold B (in-loop OP3 variant): `same_pr_mitigatable` — documented in envelope §4.2 as valid pattern for narrow pilots.
  - Fold C (accidentally-built benchmark corpus recognition per Chris): `same_pr_mitigatable` — captured in envelope §5 as first codification.
  - Post-close ledger: 117 rows (baseline 114 + 3 this session). *Note: ledger append per this session's folds will occur in a future arc-close per the pattern established at S2818/S2819 (fold recognition in envelopes; ledger persistence at arc close).*
- **Recycle log:** `logs/recycle_events.jsonl` — 1 in-session recycle (post-implementation) + 1 post-merge recycle + 1 close-cascade recycle.
- **Freshness log:** `logs/session_freshness.jsonl` — grew by 1 at S2820 open.
- **Baseline HEAD:** `87fef29d5333` (S2819 close cascade).
- **Ratification HEAD:** (filled at merge).

---

## §6 — Candidates for S2821

**Ranked per Chris's freeze + pivot directive:**

1. **⭐ Semantic retrieval evaluation against the accidentally-built benchmark corpus** (SOLE recommended direction per Chris §4.3 pivot). Concrete first steps per envelope §7:
   - Enumerate candidate mechanisms (`kb_tool.semantic_search` already exists but unused by `search_docs`; alternative embedding models; hybrid re-ranker).
   - Set up evaluation harness against §5 benchmark (13+ labeled queries).
   - Report per-mechanism: success@3, rank of known-correct target, regression check on lexical wins.
   - Route findings to Chris for S2822 migration decision.
2. **Non-discovery-layer work** (available but backgrounded): Colorado Phase 4, BettingPage first-user trace, Stock Intelligence, Playbook v0.9 amendment, remaining 2799 §8 items #4-#8.

**Recommended default:** Item #1 semantic retrieval evaluation. Chris explicitly named this as the next engineering cycle direction. The benchmark corpus is fresh; the pivot rationale (diminishing ROI on lexical patches) is empirically corroborated; the pivot substrate (`kb_tool.semantic_search` / embedding retrieval) already exists in the platform (production PA path uses it — just not `search_docs`).

---

## §7 — S2820 lessons to carry

1. **The lexical top_k ranker is now frozen policy** — S2818 + S2819 + S2820 = complete. Any new discovery-layer improvement lives in a different substrate. If S2821+ encounters a new discovery-layer failure mode, resist the urge to patch the frozen substrate.
2. **Evidence-first baseline capture (S2819 §5.1) IS the fix for aspirational-target-labeled criteria.** Applied S2820, worked exactly as expected — 4/4 PASS on empirically-grounded criteria. Second trigger for potential Playbook v0.9-adjacent amendment; watch for third.
3. **In-loop OP3 variant is valid for narrow pilots where the whole cycle happens in one conversation.** Preserves error-catching value without the round-trip cost of separate post-authoring dispatch. Not a general replacement — reserve for pilots with narrow scope + tool-grounded discipline throughout.
4. **The pilot chain built a benchmark corpus as a side effect.** Chris named it; §5 codifies it. Any future retrieval-substrate work in the platform has 13+ labeled queries with known-correct answers, ready to evaluate against.
5. **Arc-shape variety** — this arc was NOT audit-style (T1-T6 research shape) NOR platform-refactor style. It was a **focused-pilot-chain** shape: 3 direct-continuation pilots, each addressing an empirically-observed failure from the previous, all shipping same day. Novel arc-shape worth naming for future methodology reference.
6. **"Feature complete" is a valid arc-close pattern.** Not every substrate reaches an asymptote via arc close (2799 canonical summary) or refactor completion. Some substrates reach "we've done what we can with this tool; time to switch tools." Chris's 4-verdict D-response formalizes this shape.

---

**End of S2820 handoff. Close cascade PR + workspace deliverable mirror (deferred per S2818/S2819 pattern) + pin rotation follow this ship. Discovery-layer lexical-pilot chain S2818/S2819/S2820 is FEATURE COMPLETE. S2821 pivots to semantic retrieval evaluation against the benchmark corpus this arc built.**
