---
title: "S2820 Orientation-Doc Exclusion + Lexical-Pilot Feature-Complete Ratification Record (2026-07-18)"
status: active
authority: ratification-record
session_added: 2820
ratification_date: 2026-07-18
ratifier: chris
routing: rigby-pa-chat joint SIGN (open scope Q1-Q4 with empirically-grounded baseline capture per S2819 §5.1 methodology lesson) + Chris D-verdict "Approve S2820" + Chris directive "Freeze lexical policy after it ships. Declare the current lexical pilot 'feature complete'. Spend the next engineering cycle evaluating semantic retrieval against the benchmark corpus you've accidentally built during the docs audit."
scope: |
  S2820 — orientation-doc exclusion in `top_k`, scoped to
  `00-START-NEXT-SESSION.md`. Closes the 3-arc lexical-pilot chain
  (S2818 authority boost → S2819 intent gating → S2820 exclusion) that
  originated from 2799 §8 item #1. Chris ratified this as the LAST
  lexical patch — the discovery-layer arc's lexical branch is declared
  "feature complete." S2821+ pivots to semantic retrieval evaluation
  against the benchmark corpus this arc has empirically built.
serves_arc: |
  Group 2700 /docs/ restructuring follow-on queue (2799 §8 item #1
  closure) + lexical-pilot chain closure + S2821 pivot to semantic
  retrieval evaluation
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md (S2819 Shape C — precedent for gate discipline + envelope §5.1 methodology gotcha applied here)
  - docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md (S2818 pilot — origin of the lexical policy chain + established evidence discipline)
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md (S2817 arc close — §8 item #1 authorization)
  - docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md (S2813 T3 — §7 C2 pain class that S2820 fixes; C5 pain class that S2818 fixed; both are same-family discovery-layer failures)
ratified_documents:
  - core/rag.py (amended — new _EXCLUDED_FILE_PATHS frozenset + skip check inside top_k scoring loop before base-score computation)
  - core/tests/test_rag_orientation_doc_exclusion_2820.py (new — 5 tests: 2 unit + 3 integration; validates exclusion holds unconditionally regardless of query text or authority gate state)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2820 open freshness — verdict STALE_DAPHNE · head=87fef29d5333 · celery_stale=0/5 (session_lifecycle open output at S2820 open; daphne stale not blocking for Rigby PA dispatch via celery)
  - S2820 open scope SIGN (Rigby, pin pa-a0dd969db550488d) — Q1 EMPIRICAL BASELINE CAPTURE (4 queries dispatched live per S2819 §5.1 methodology lesson), Q2 Option B recommended (retrieval-time hard exclusion), Q3 00-START-only scope confirmed (Rigby verified S2819 handoff contains phrase but does NOT appear in Q1(a) returned set), Q4 zoom-out ARCHITECTURAL INFLECTION — "we're near the point where more lexical ranker patches have diminishing ROI." tool_runs non-empty (repo_tool ×3 + search_docs ×4 live).
  - Post-authoring SIGN — folded into Rigby's in-loop presence throughout implementation (recommended mechanism → wrote code → ran measurement → verified 4/4 PASS on empirically-grounded criteria in the same conversation). No separate post-authoring turn; the in-loop discipline replaced the sequential OP3 shape for this narrow pilot. Envelope §4.2 documents this variant.
frozen: true
---

# S2820 Orientation-Doc Exclusion + Lexical-Pilot Feature-Complete — Ratification Record

Frozen canonical record of Chris's ratification of the S2820 orientation-doc exclusion mechanism on 2026-07-18 AND the accompanying directive to freeze lexical policy + declare the S2818/S2819/S2820 pilot chain "feature complete" + pivot the next engineering cycle to semantic retrieval evaluation. Third and final pilot in the discovery-layer arc originating from 2799 §8 item #1. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-18 (America/Denver operator timezone)
- **Session:** S2820 (third same-day pilot in the direct-continuation discovery-layer chain S2818 → S2819 → S2820)
- **Scope:** S2819 envelope §5.2 self-contamination finding + §6 follow-on. Chris-ratified top-of-queue at S2819 close.
- **Motivation:** After S2819 shipped Shape C intent-gating, live measurement showed `docs/00-START-NEXT-SESSION.md#3` as top-1 for `search_docs("add a new spider to the network")` because the S2819 candidate description written in 00-START-NEXT-SESSION.md contained the exact phrase as example text. Same class as T3 §7 C2 pain (start-here doc dominance when queries touch example text), but surfaced live during the pilot chain rather than in a general audit.
- **Ratifier:** Chris ("start s2820 with the 00-start contamination fix" — direct-continuation directive at S2819 close; "Approve S2820. Freeze lexical policy after it ships. Declare the current lexical pilot 'feature complete.' Spend the next engineering cycle evaluating semantic retrieval against the benchmark corpus you've accidentally built during the docs audit." — D-verdict + strategic pivot directive at S2820 mid-pilot after Rigby's Q4 architectural-inflection zoom-out).

---

## §2. Ratified Deliverables

### §2.1 `core/rag.py` — `_EXCLUDED_FILE_PATHS` + skip check in `top_k`

Adds a module-level frozenset + one check inside the scoring loop:

```python
_EXCLUDED_FILE_PATHS = frozenset({
    "00-START-NEXT-SESSION.md",
})

# ... inside top_k ...
with CORPUS_PATH.open() as f:
    for line in f:
        row = json.loads(line)
        # S2820: skip orientation-only docs entirely.
        if row.get("file", "") in _EXCLUDED_FILE_PATHS:
            continue
        ...
```

**Design constraints (from joint SIGN):**

- **Retrieval-time exclusion (Option B)** chosen over build-time exclusion (Option A) or deprioritization (Option C) per Rigby SIGN Q2. Rationale: simplicity (no touch to `build_rag_corpus` generation), reversibility (constant list + one line trivially revertible), consistency with existing S2818/S2819 pattern (all policy in `core/rag.py:top_k`), categorical stance (orientation doc in generic search is always wrong per §7 C2 pain evidence).
- **Skip inside loop BEFORE authority-gate branch** — excluded docs are removed unconditionally regardless of `authority_gate` value. No boost or gate override can rescue an excluded doc.
- **frozenset** — immutable value; not a mutation surface.
- **Pilot scope 00-START only** — Rigby empirically verified at S2820 open SIGN Q3 that the S2819 handoff CONTAINS the exact contaminator phrase but does NOT appear in Q1(a) returned set. Handoff expansion would be scope creep without current measurement evidence. If handoffs later surface as top-3 for non-handoff-intent queries, that triggers a separate SIGN cycle.

### §2.2 `core/tests/test_rag_orientation_doc_exclusion_2820.py` — 5 tests

- **Unit** (`ExcludedFilePathsUnitTests`): 2 tests — pilot-scope-is-orientation-doc-only guardrail, excluded_set_is_frozen (frozenset value invariant).
- **Integration** (`TopKExclusionIntegrationTests`): 3 tests — excluded doc never appears even when best match (S2819 §5.2 contamination shape), exclusion holds even with `authority_gate=True` forced (defense-in-depth), non-excluded docs still scored normally (regression check).

All 27 tests across the S2818/S2819/S2820 lexical-pilot test corpus pass at merge (7 S2818 + 15 S2819 + 5 S2820).

---

## §3. Empirical Evidence (per PLAYBOOK-6.10.9 verified-state outcome)

**Stable-state pointer:** measurements below captured against the S2820 branch after `make celery-recycle`. Baseline captured pre-implementation by Rigby (SIGN Q1 evidence-first per S2819 §5.1 methodology lesson); post-fix captured after `make celery-recycle` picked up the code change.

### §3.1 Baseline evidence-first capture (applied S2819 §5.1 lesson)

Per the S2819 §5.1 methodology lesson (baseline capture must include full top-K + per-named-target presence check BEFORE locking criterion), Rigby dispatched 4 live queries at S2820 open. Each query's baseline shape locked the corresponding success criterion:

| Q | Query | Baseline top-1 | Baseline 00-START rank | Locked success criterion |
|---|---|---|---|---|
| (a) | "add a new spider to the network" | `docs/00-START-NEXT-SESSION.md#3` | **#1** (contamination confirmed) | 00-START must be ABSENT post-fix; new top-1 = AGENTS_REFERENCE.md (baseline #2) |
| (b) | "Group 2700 docs restructuring T1 audit" | `docs/handoffs/SESSION_2801_...#1` | not in set | handoffs still dominate (unchanged) |
| (c) | "00-START-NEXT-SESSION" self-reference | `docs/CLAUDE.md#6` | not in set | CLAUDE.md pointer chunks (unchanged) |
| (d) | "How many spiders do we have" | `docs/PLATFORM_INVENTORY.md#1` | not in set | PLATFORM_INVENTORY.md#1 (S2818 counts preserved) |

**Verified state (i) — evidence-first criterion discipline held:** every criterion above was derived from the observed baseline, not from aspirational "intended target" labels. The S2819 methodology gotcha is not just documented — it's applied.

### §3.2 Post-fix measurement (4/4 PASS)

| Q | Post-fix top-1 | Top-2 | Top-3 | 00-START in set? | Verdict |
|---|---|---|---|---|---|
| (a) | `docs/AGENTS_REFERENCE.md#35` | `docs/archive/REALITY_FIXES_IMPLEMENTATION-original/BACKEND_INTEGRATION_PROGRESS.md#6` | `docs/archive/REALITY_FIXES_IMPLEMENTATION-original/LETTER_TO_FUTURE_CLAUDE.md#4` | **NO** | **PASS** — 00-START gone; baseline shape restored (matches pre-S2819-authoring baseline exactly) |
| (b) | `docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md#1` | `docs/handoffs/SESSION_2811_...#1` | `docs/handoffs/SESSION_2811_...#6` | **NO** | **PASS** — handoff dominance unchanged (correct behavior for handoff-intent query) |
| (c) | `docs/CLAUDE.md#6` | `docs/CLAUDE.md#9` | `docs/CLAUDE.md#12` | **NO** | **PASS** — CLAUDE.md pointer chunks unchanged (self-reference query correctly returns docs that mention 00-START, not 00-START itself) |
| (d) | `docs/PLATFORM_INVENTORY.md#1` | `docs/PLATFORM_INVENTORY.md#2` | `docs/PLATFORM_INVENTORY.md#3` | **NO** | **PASS** — S2818 counts criterion preserved |

**Verified state (ii) — 4/4 PASS on empirically-grounded criteria.** No follow-up tuning cycle needed. The mechanism does exactly what its scope defines.

**Verified state (iii) — cross-cycle assertion:** Comparing S2820 Q(a) post-fix top-3 to S2818 §3.1 pre-boost baseline for the same query: **exact match** on all three positions (AGENTS_REFERENCE.md, BACKEND_INTEGRATION_PROGRESS.md, LETTER_TO_FUTURE_CLAUDE.md). The 3-arc pilot chain successfully re-shaped counts queries to authority + eliminated non-counts monoculture + eliminated orientation-doc contamination, leaving non-counts queries in their pre-pilot baseline shape.

---

## §4. SIGN Sessions

### §4.1 Open scope SIGN (Rigby, pin `pa-a0dd969db550488d`)

Tenth-consecutive OP3-adjacent trigger (in-loop shape, see §4.2).

**Q1 — Empirical baseline capture (evidence-first per S2819 §5.1).** Rigby dispatched 4 live search_docs queries against current HEAD `87fef29d5333`. Full returned set reported for each. This IS the criterion-grounding evidence; success axes for the pilot were locked from these baseline shapes. Applied the S2819 lesson explicitly rather than assuming aspirational targets.

**Q2 — Mechanism verdict: Option B.** Retrieval-time hard exclusion in `core/rag.py`. Rigby weighed simplicity + reversibility + consistency with S2818/S2819 pattern + categorical stance (orientation-in-generic-search is always wrong). Rejected Option A (build-time) as unnecessary corpus-generation complexity. Rejected Option C (deprioritization) as insufficient — categorical wrongness deserves categorical fix, not soft nudge.

**Q3 — Scope pressure-test: 00-START only.** Rigby read `docs/handoffs/SESSION_2819_SHAPE_C_INTENT_GATING.md` in full to verify handoff contamination hypothesis. Confirmed: handoff DOES contain the contaminator phrase ("add a new spider to the network" at line 67) but empirically DOES NOT appear in Q1(a) returned set. Concluded: expanding to handoff exclusion would be scope creep without measurement evidence. Deferred to future SIGN cycle if handoff contamination surfaces.

**Q4 — Zoom-out (architectural inflection).** **Novel high-signal observation:** "we're near the point where more lexical ranker patches have diminishing ROI." Pattern observed across the arc: authority boosts (S2818) → intent gating (S2819) → exclusions (S2820). Each patch is a policy layer piled on top of a token-overlap lexical ranker. That's exactly what embedding-based retrieval solves natively (semantic similarity + document-level reranking). Rigby recommended: after S2820 ships, pivot next arc to embedding-retrieval evaluation rather than continuing lexical patches.

### §4.2 Post-authoring SIGN as in-loop discipline (OP3 variant)

Unlike prior OP3 cycles which routed a separate post-authoring dispatch, S2820's post-authoring evidence was folded into Rigby's in-loop presence throughout the same conversation:

1. Rigby ran Q1 empirical baseline (evidence-first).
2. Rigby recommended Option B mechanism (Q2).
3. Claude implemented Option B against the recommendation.
4. Rigby ran post-implementation measurement in the same conversation.
5. Result: 4/4 PASS on the criteria Rigby helped set.

The OP3 pattern's error-catching value (surfacing errors open-SIGN missed) was preserved: the whole conversation was tool-grounded end-to-end, and Rigby's baseline evidence would have caught a bad implementation the same way a separate post-authoring turn would. This variant is documented here as a valid OP3 shape for narrow pilots where the whole cycle happens in a single conversation and the reviewer has been in-loop throughout. Not a general replacement for separate post-authoring SIGN on larger changes.

### §4.3 Chris D-verdict + strategic pivot directive

After receiving joint verdict + Q4 architectural-inflection observation from Rigby, Chris responded:

> "Approve S2820. Freeze lexical policy after it ships. Declare the current lexical pilot 'feature complete.' Spend the next engineering cycle evaluating semantic retrieval against the benchmark corpus you've accidentally built during the docs audit."

Four ratifications in one:

1. **Approve S2820** — ship this exclusion mechanism.
2. **Freeze lexical policy after ship** — no more patches to `AUTHORITY_FILE_BONUS`, `_COUNT_INTENT_PATTERNS`, or `_EXCLUDED_FILE_PATHS` in the current lexical top_k lane. The 3-arc chain S2818/S2819/S2820 is the complete lexical policy.
3. **Declare current lexical pilot "feature complete"** — the discovery-layer arc's lexical branch is booked. No follow-up "Shape D" / "Shape E" iterations in this substrate.
4. **Pivot next engineering cycle** to semantic retrieval evaluation against the benchmark corpus this arc has built.

---

## §5. Novel finding — the accidentally-built benchmark corpus

Chris's pivot directive names something the pilot chain built without setting out to: **an empirical labeled benchmark corpus for evaluating retrieval systems on this repo's docs.**

Across S2818/S2819/S2820, the following queries acquired known-correct answers via pilot measurement + ratification:

| Query | Known-correct target (empirical) | Source |
|---|---|---|
| Q1 "How many spiders do we have" | `docs/PLATFORM_INVENTORY.md` | S2818 authority-boost success criterion |
| Q2 "How many agents do we have" | `docs/PLATFORM_INVENTORY.md` | S2818 §3.3 |
| Q3 "How many database models" | `docs/PLATFORM_INVENTORY.md` | S2818 §3.3 |
| Q4 "How many celery tasks" | `docs/PLATFORM_INVENTORY.md` | S2818 §3.3 |
| Q5 "add a new spider to the network" | `docs/AGENTS_REFERENCE.md#35` (T3 B1 target `docs/topics/spider-network.md` labeled aspirational but NOT empirical top-1) | S2820 §3.1 baseline |
| Q6 "list all spiders" | `docs/PLATFORM_INVENTORY.md` | S2819 §3 |
| Q7 "Group 2700 docs restructuring T1 audit" | `docs/handoffs/SESSION_2801_...` + `SESSION_2811_...` | S2820 §3.1 baseline |
| Q8 "00-START-NEXT-SESSION" self-reference | `docs/CLAUDE.md#6` (pointer chunk, not 00-START itself) | S2820 §3.1 baseline |
| C1-C5 | (per T3 §7) | Group 2700 T3 audit |

That's 13+ queries with **explicit correct-answer labels** derived from either the S2813 T3 audit or the S2818/S2819/S2820 pilot measurements. Every label is grounded in either T3's audit shape or an evidence-first baseline capture, per the S2819 §5.1 methodology discipline.

**This is the S2821 evaluation harness.** Semantic retrieval candidates (kb_tool.semantic_search over `unified_embeddings` pgvector table; or new embedding-based mechanism) can be scored against this labeled set with:
- **success@3** (does the known-correct target appear in top-3?)
- **rank of known-correct target**
- **regression check** (does semantic retrieval preserve the wins the lexical arc achieved on Q1-Q4 + Q6? does it independently arrive at the correct answers for Q5/Q7/Q8?)

No new labeled corpus needs to be authored — this arc built it as a side effect. Chris's phrasing "accidentally built" is exact.

---

## §6. Limitations & Known Findings

### §6.1 Substring token matching in the lexical scorer (unchanged from S2818/S2819)

The lexical ranker uses `w in tl` (substring match). `"in"` matches `"inventory"`, `"total"` matches `"total redesign"`, etc. Accepted for pilot; would be resolved by semantic retrieval which measures embedding similarity rather than substring overlap.

### §6.2 Handoff contamination remains latent

S2820 §4.1 Q3 verified S2819 handoff contains the same contaminator phrase but does NOT currently appear in Q1(a). If a future query lands on a handoff's example text and pushes the handoff into top-3 over the intended target, that would trigger a new SIGN cycle. But per Chris's freeze directive: even if this happens, the fix would be authoritative in a NEW substrate (semantic retrieval), not another exclusion patch in the lexical lane.

### §6.3 Frozen lexical policy — no more patches

Per Chris's directive, the S2818/S2819/S2820 chain is COMPLETE. `AUTHORITY_FILE_BONUS`, `_COUNT_INTENT_PATTERNS`, `_EXCLUDED_FILE_PATHS` are the final state. Any new discovery-layer improvement must live in a different substrate (embedding-based retrieval, hybrid re-ranker, etc.) — not another entry in the existing dicts/sets.

---

## §7. Follow-On (S2821+)

**Sole recommended direction (Chris-ratified):**

**Semantic retrieval evaluation against the benchmark corpus** (§5). Concrete first steps for S2821:

1. Enumerate candidate semantic retrieval mechanisms:
   - `kb_tool.semantic_search` — production PA / Rigby retrieval path against `unified_embeddings` pgvector table (already exists; not currently used by `search_docs` handler).
   - Hybrid: lexical `top_k` + semantic reranker.
   - Alternative embedding models (OpenAI text-embedding-3 / e5 / bge / etc.).
2. Set up evaluation harness against §5 benchmark corpus (13+ queries with known-correct labels).
3. Report per-mechanism: success@3, rank of known-correct target, regression check on lexical wins.
4. Route findings to Chris for decision on whether to migrate `search_docs` PA path to semantic retrieval and (if so) which mechanism.

**Non-goals for S2821:**
- No more lexical patches (frozen per Chris directive §4.3).
- Not a full migration — S2821 is EVALUATION, not implementation.
- Benchmark corpus stays fixed (do NOT add new labels; extending the harness requires separate SIGN).

---

## §8. Provenance

- **Session:** S2820 (third same-day pilot in discovery-layer arc; S2818 → S2819 → S2820 chain)
- **Session pin:** `pa-a0dd969db550488d` (label `s2820-00start-contamination-fix`; minted at S2820 open via `session_lifecycle open`)
- **Baseline HEAD:** `87fef29d5333` (S2819 close cascade)
- **Ratification HEAD:** (filled at merge)
- **Merged PR:** (filled at merge)
- **Tools used:** Read for existing state; Edit for `core/rag.py` (exclusion set + skip check); Write for new test file + envelope; `make celery-recycle` post-implementation; Rigby `repo_tool` + `search_docs` throughout for all live evidence.
- **OP3 pattern:** 10th-adjacent trigger. First IN-LOOP OP3 variant — Rigby was continuously in-loop rather than routed separately post-authoring. Documented as a valid variant for narrow pilots. Playbook v0.9 amendment now has 10 datapoints across shapes.
- **S2819 §5.1 methodology lesson applied:** Q1 baseline capture WAS the criterion-grounding evidence, not the criterion assertion. Every success axis was derived from observed baseline shape, not aspirational labels. This session is the first empirically-verified compliance with the S2819 methodology gotcha.
- **Twin-pointer discipline:** this envelope in `docs/research/implementation/`; workspace deliverable mirror deferred per S2818/S2819 pattern.
- **Chris's "accidentally built benchmark corpus" framing (§5)** captures a real observed byproduct of the arc — a testing-set-quality labeled retrieval-evaluation corpus. Novel finding surfaced by Chris's pivot directive, first codification here.

---

**End of ratification record. Frozen at merge. Discovery-layer lexical-pilot chain S2818/S2819/S2820 is FEATURE COMPLETE. S2821 pivots to semantic retrieval evaluation.**
