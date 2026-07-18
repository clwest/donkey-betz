# Session 2819 — Shape C query-intent gating (S2818 follow-on)

**Date:** 2026-07-18 (afternoon; direct continuation of S2818 close)
**Session:** S2819
**PRs shipped:** 1 feature (#TBD) + 1 close cascade (#TBD)
**Predecessor:** [SESSION_2818 discovery-layer pilot](SESSION_2818_DISCOVERY_LAYER_PILOT.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 in-session recycle (post-implementation) + post-merge recycle to come + close-cascade recycle to come

---

## §1 — Ship summary

**One PR shipped: query-intent gate around the S2818 `AUTHORITY_FILE_BONUS` mechanism.** Closes the loop on S2818's documented non-counts regression while preserving both the counts-query success AND the "list all" behavior Rigby empirically discovered.

### PR #TBD — S2819 Shape C intent-gating

**Files:**
- `core/rag.py` — new `_COUNT_INTENT_PATTERNS` (6 patterns) + `_looks_like_count_query()` helper + `authority_gate` param on `top_k` with auto-compute default. Docstring updated.
- `core/tests/test_rag_intent_gating_2819.py` (new) — 15 tests (10 unit + 5 integration).
- `core/tests/test_rag_authority_boost_2818.py` — 1 test updated (`authority_gate=True` explicit) per new gate semantics.
- `docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md` (new envelope with PLAYBOOK-6.10.9 evidence).

**Key results (full 6-query batch):**

| Q | Pre-boost baseline | S2818 unconditional | **S2819 Shape C** |
|---|---|---|---|
| Q1-Q4 counts | archive/audit docs top-1 ❌ | PLATFORM_INVENTORY.md dominates ✅ | **PLATFORM_INVENTORY.md dominates ✅** preserved |
| Q5 non-counts "add spider" | AGENTS_REFERENCE.md top-1 | PLATFORM_INVENTORY.md dominates ⚠️ regression | **PLATFORM_INVENTORY.md rank >20 ✅** monoculture eliminated |
| Q6 "list all spiders" | not measured | dominates (S2818 residual) | **PLATFORM_INVENTORY.md dominates ✅** preserved via pattern |

Both S2818 goals achieved simultaneously: counts + list-all preserved, non-counts monoculture eliminated.

---

## §2 — Rigby joint SIGN cycles — NINTH-CONSECUTIVE OP3 TRIGGER (first ESCALATE→SHIP re-verdict)

**Pin:** `pa-ebadb78a43034ff7` (S2819 open-ceremony fresh mint post-S2818-close; retired at close, force=true).

### 2.1 Open scope SIGN (Q1-Q4)

- **Q1 mechanism verify — AGREE (tool-verified) with 2 integration notes.** Rigby read `core/rag.py` at S2818 close HEAD. Confirmed clean insertion points. Notes: docstring update needed (was "applies ALWAYS", becomes "gated"); `build_docs_context` caller unaffected (new param optional). Both applied.
- **Q2 pattern coverage — PARTIAL AGREE; empirical extension.** Rigby dispatched `search_docs("list all spiders")` LIVE — observed PLATFORM_INVENTORY.md dominating (S2818 unconditional-boost residual). Concluded gating on counts-only patterns would REGRESS legitimate inventory query. **Adopted: add "list all" to pattern set.** amount-of / inventory-of deferred (no empirical demand evidence).
- **Q3 gate-location — Option B recommended.** New param `authority_gate: bool | None = None` on `top_k`; auto-compute default. Rationale: testability + caller override + A/B capability. Tri-state enum future-considered.
- **Q4 zoom-out — AGREE net-new failure modes.** 4 risks named (false negatives, false positives on "total", coupling for multi-doc expansion, discoverability), each with mitigation.

### 2.2 Post-authoring OP3 SIGN — FIRST INITIAL-ESCALATE → RE-VERDICT-SHIP CYCLE

**Initial verdict: ESCALATE.** Rigby's first pass verdict was ESCALATE because Q5 top-1 (`docs/00-START-NEXT-SESSION.md#3`) didn't match my SIGN-routing "expected" target of `docs/topics/spider-network.md`.

**Correction routed:** Claude noted the criterion itself was flawed. S2818 pre-boost baseline never had `docs/topics/spider-network.md` in top-3 — the T3 §3 "intended target" label was aspirational, not empirical. Real Q5 goal was "monoculture elimination + baseline-shape restoration."

**Re-verdict SIGN (corrected framing):**
- Q1 AGREE — Shape C succeeded at underlying goal (monoculture eliminated + counts preserved).
- Q2 AGREE — 00-START-NEXT-SESSION.md top-1 is same-session self-contamination (T3 C2 class), not Shape C failure. Separate follow-on.
- Q3 AGREE — success-criterion-hygiene is codifiable methodology gotcha. Novel finding, first trigger; observe next 2 pilot-arcs before Playbook amendment per §20 two-triggers rule.

**Anti-rubber-stamp check:** both SIGN cycles had `tool_runs` non-empty (repo_tool + multiple search_docs live dispatches, including re-verification runs during OP3).

---

## §3 — Novel precedent

1. **First INITIAL-ESCALATE → RE-VERDICT-SHIP cycle** in the OP3 streak. Rigby's initial verdict was based on my flawed success criterion; corrected framing produced ship. Reinforces that OP3 post-authoring SIGN catches CRITERION errors, not just implementation errors.
2. **First success-criterion-hygiene gotcha surfaced.** Novel finding: "restore doc X to top-3" is unwinnable if X was never in baseline top-3. The T3 "intended target" labels are aspirational (where the user *should* end up), not empirical (where search *actually* went). Baseline capture must include per-target-doc presence check before locking criterion.
3. **First direct-continuation pilot-arc (S2818 → S2819 same day).** S2818 shipped afternoon; S2819 opened + shipped same afternoon. Demonstrates a follow-on arc can close within-day when substrate is fresh in context.
4. **First self-contamination finding of a pilot's own start-here doc.** Writing about the pilot scenario in `00-START-NEXT-SESSION.md` re-embedded that doc; now `search_docs("add a new spider to the network")` returns 00-START top-1 because the phrase appears verbatim in the S2819 candidate description I wrote. Same class as T3 C2 pain, but surfaced live during a pilot.
5. **Empirical-pattern-extension discipline.** Rigby SIGN Q2 added "list all" ONLY after live `search_docs` confirmed the current behavior would regress without it. amount-of / inventory-of declined for lack of empirical evidence. Sets precedent for future pattern-set expansions: evidence-first, not speculation-first.

---

## §4 — What shipped vs what didn't

**Shipped:**
- Query-intent gate mechanism with 6 patterns + auto-compute default + explicit force-on/force-off override
- 15 new tests (10 unit + 5 integration) covering gate mechanics, override semantics, list-all preservation
- Envelope with PLAYBOOK-6.10.9 stable-state-pointer + file+line evidence + (i)/(ii)/(iii) verified-state outcomes + success-criterion-hygiene novel finding + self-contamination novel finding

**Not shipped (queued):**
- 00-START-NEXT-SESSION.md example-text contamination fix (novel from S2819 §5.2)
- Success-criterion-hygiene Playbook amendment (novel from S2819 §5.1; 1 trigger; wait for 2 more)
- Per-doc intent gates (needed when `AUTHORITY_FILE_BONUS` expands beyond 1 doc)
- Multi-doc `AUTHORITY_FILE_BONUS` expansion (deferred from S2818 SIGN Q3; now unblocked by Shape C proving mechanism works — CLAUDE.md / DOC_LIFECYCLE.md / PLATFORM_WHAT_IT_IS.md candidates)
- Embedding-based retrieval migration (reinforced by S2818 + S2819 findings)

---

## §5 — Ledger + provenance

- **Zoom-out ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows at S2819 open; folds this session:
  - Fold A (Rigby SIGN Q4 open zoom-out — false-negatives/positives/coupling/discoverability): mixed — false-positive on "total" accepted for pilot (`future_trigger`); coupling for multi-doc queued (`future_trigger`); discoverability mitigated in same PR (`same_pr_mitigatable`); false-negatives mitigated by test suite (`same_pr_mitigatable`).
  - Fold B (Rigby OP3 Q3 zoom-out — success-criterion-hygiene): `future_trigger` — 1st trigger for potential Playbook amendment; observe next 2 pilot-arcs per §20 two-triggers rule.
  - Fold C (Q5 self-contamination finding): `same_pr_mitigatable` — mitigated by envelope §5.2 documentation as separate follow-on; not blocked shipping.
  - Post-close ledger: 117 rows (baseline 114 + 3 this session).
- **Recycle log:** `logs/recycle_events.jsonl` — 1 in-session recycle (post-implementation before Rigby measurement) + 1 post-merge recycle + 1 close-cascade recycle.
- **Freshness log:** `logs/session_freshness.jsonl` — grew by 1 at S2819 open.
- **Baseline HEAD:** `2a01bc537911` (S2818 close cascade).
- **Ratification HEAD:** (filled at merge).

---

## §6 — Candidates for S2820

**Ranked by architectural uncertainty × risk × unblocked flows:**

1. **⭐ 00-START-NEXT-SESSION.md self-contamination fix** (novel from S2819 §5.2). Highest-leverage next step: eliminate the last remaining discovery-layer confound in the counts-adjacent query surface. Smallest scope: exclude `docs/00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_*.md` from `search_docs` corpus OR reduce their per-chunk weight. Same 6-query batch as S2818+S2819 for direct comparison.
2. **Multi-doc `AUTHORITY_FILE_BONUS` expansion.** Now unblocked by Shape C proving gated mechanism works. Candidates from S2818 SIGN Q3: `DOC_LIFECYCLE.md`, `PLATFORM_WHAT_IT_IS.md`, `CLAUDE.md`. Requires per-doc intent gates (S2819 §5 Q4 coupling risk) since each doc has different intent match.
3. **Playbook v0.9 amendment (OP3 codification)** — 9/9 triggers now with INITIAL-ESCALATE → RE-VERDICT-SHIP variant. Well past codification threshold.
4. **Remaining 2799 §8 queue** (items #2 HIGH-DRIFT / #4 T5 clause / #5-#8).
5. **Colorado Phase 4** statute-citation quality.
6. **BettingPage first-user trace / Stock Intelligence** end-to-end verify.

**Recommended default:** Item #1 (00-START contamination fix). It closes the last observable regression from the two-pilot discovery-layer arc; substrate is maximally fresh; same 6-query batch reusable for direct pre/post.

---

## §7 — S2819 lessons to carry

1. **Success criteria must be empirically grounded in the pre-change baseline.** T3 §3 "intended target" labels are aspirational (where the user *should* end up), not empirical (where search *actually* went). Baseline capture must include per-named-target presence check.
2. **Post-authoring SIGN catches criterion errors, not just implementation errors.** Rigby's initial ESCALATE verdict was based on my flawed criterion; corrected framing produced SHIP. The OP3 pattern isn't just about code — it's about *evidence framing*.
3. **Same-session doc-writes can contaminate the corpus.** Writing example text in start-here docs re-embeds them and biases future retrieval. Self-observation opportunity: watch for this in future pilot arcs.
4. **Empirical-pattern-extension discipline works.** Rigby SIGN Q2 added exactly one pattern (`list all`) based on live evidence; declined two speculative additions. Ships a defensible pattern set with clean expansion criteria.
5. **INITIAL-ESCALATE → RE-VERDICT-SHIP is a valid closure pattern.** Rigby was right to escalate on the criterion I gave her; correction was Claude's responsibility. Both roles executed their contract; the joint verdict flow adapted.
6. **Direct-continuation pilot arcs are viable when substrate is fresh.** S2818 → S2819 same day worked because Shape C was already the top-of-queue Chris-ratified follow-on with narrow scope.

---

**End of S2819 handoff. Close cascade PR + workspace deliverable mirror (deferred, per S2818 pilot pattern) + pin rotation follow this ship.**
