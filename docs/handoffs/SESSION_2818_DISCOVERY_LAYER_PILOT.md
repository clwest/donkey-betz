# Session 2818 — Discovery-layer enforcement pilot (2799 §8 item #1)

**Date:** 2026-07-18 (afternoon; first post-Group-2700-arc-close session)
**Session:** S2818
**PRs shipped:** 1 — **PR #TBD** (fill at merge)
**Predecessor:** [SESSION_2817 Group 2700 arc close](SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 2 in-session recycles (magnitude iteration) + close-cascade recycle to come

---

## §1 — Ship summary

**One PR shipped: authority-boost mechanism in `core/rag.py` for `docs/PLATFORM_INVENTORY.md` at magnitude=8.** Executes 2799 §8 item #1 as a pilot with documented known regression. Empirical evidence value: proved that static per-chunk magnitude alone cannot satisfy both counts-query success and non-counts-query regression avoidance; escalates Shape C intent-gating as next arc.

### PR #TBD — S2818 discovery-layer authority-boost pilot

**Files:**
- `core/rag.py` (+22 LOC) — new `AUTHORITY_FILE_BONUS` dict + `_authority_bonus` helper; unconditional invocation in `top_k()`
- `core/tests/test_rag_authority_boost_2818.py` (new, +141 LOC) — 5 unit tests + 2 integration tests
- `docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md` (new, envelope with empirical evidence per PLAYBOOK-6.10.9)

**Key deliverables:**
- **Primary success criterion met:** T3 C5 regression fixed. `search_docs("How many spiders do we have")` now returns `docs/PLATFORM_INVENTORY.md#1 / #2 / #3` as top-3 (baseline: archive Oct 2025 morning report top-1 with PLATFORM_INVENTORY.md absent from returned set).
- **Generalizes across counts queries:** Q2 "how many agents" / Q3 "how many database models" / Q4 "how many celery tasks" all now dominated by PLATFORM_INVENTORY.md chunks post-boost (were archive/audit docs pre-boost).
- **Known regression documented:** Q5 non-counts query "add a new spider to the network" now dominated by PLATFORM_INVENTORY.md; `docs/topics/spider-network.md` (T3 B1 intended target) no longer in top-3. Rigby OP3 Q4 zoom-out identified the mechanism as result-set monoculture (PLATFORM_INVENTORY.md has 59 chunks in corpus; per-chunk +8 bonus floods the ranker).
- **Envelope §5 Limitations** documents the trade-off as the pilot's evidence value. Static magnitude architecturally cannot satisfy both criteria; magnitude tuning is empirically closed as a mechanism.
- **§6 Follow-on:** Chris ratified Shape C intent-gating as next arc — apply boost only for count-intent queries (heuristics on "how many"/"count of"/"total"/"number of"), preserving primary criterion while eliminating non-counts regression.

---

## §2 — Rigby joint SIGN cycles — EIGHTH-CONSECUTIVE OP3 TRIGGER (first post-arc, first pilot-shape)

**Pin:** `pa-43db3c9851764ee7` (S2818 open-ceremony fresh mint post-S2817-close; retired at close, force=true).

**Two SIGN cycles — 8/8 OP3 pattern (extends the Group 2700 S2811-S2817 7/7 streak to a first-post-arc + first-pilot-shape datapoint).** Both cycles produced substantive tool-grounded findings that shaped the ship path.

### 2.1 Open scope SIGN (Q1-Q4)

- **Q1 mechanism verify — AGREE (tool-verified).** Rigby `repo_tool` read `core/rag.py:1-82` + `core/services/td_handlers_ops.py:6045-6165`; ran `search_docs("How many spiders do we have")` live. Confirmed: `_file_bonus` fires only when `boost_hints=True`; `search_docs` passes `False`; Shape A (new always-on bonus list) is smallest correct mechanism. Baseline: PLATFORM_INVENTORY.md absent from returned set of 5 chunks — T3 C5 failure stable on current HEAD.
- **Q2 magnitude — PARTIAL AGREE.** Rigby recommended starting at +20 (headroom over legacy 8) since raw scores aren't visible from `search_docs` output. Flagged dev-only debug score exposure as tighter path; declined by Claude as scope creep. Consequence surfaced in post-authoring SIGN.
- **Q3 scope creep — DISAGREE expansion.** Rigby held the 2799 §8 explicit 1-doc constraint. Recorded as unit-test guardrail (`test_pilot_scope_is_one_doc`).
- **Q4 zoom-out (per PLAYBOOK-6.10.7) — AGREE real coupling risk.** Three concerns raised: rot/rename fragility (mitigated same-PR: exact-path match, not regex); hidden retrieval policy (mitigated: explicit comment + unit test); fork risk vs embedding stack (deferred: envelope §6 queues follow-on).

### 2.2 Post-authoring OP3 SIGN (Q1-Q4)

Dispatched after implementation at magnitude=20 + worker recycle + baseline + post-boost measurement.

- **Q1 empirical read — AGREE.** Q5 regression is real, not synthetic. Rigby re-ran Q5 live to confirm stable across dispatches.
- **Q2 magnitude feasibility — PARTIAL.** Static magnitude inherently a compromise; not provably infeasible; +8 worth trying with tight stop-condition.
- **Q3 recommendation — Path B (tune to +8) with stop-condition.** "If Q1 passes AND Q5 non-dominated → ship; if Q5 still dominated at +8 → escalate to Shape C rather than continue tuning cycles."
- **Q4 zoom-out — NEW empirical risk surfaced.** **Result-set monoculture** — per-chunk bonus on chunky doc (PLATFORM_INVENTORY.md = 59 chunks) crowds out complementary docs even for counts queries where the boost is otherwise correct. Named three mitigation paths for follow-on: (a) intent gating, (b) per-file caps in `top_k`, (c) embedding retrieval with document-level authority weighting.

### 2.3 Stop-condition triggered → escalation → Chris D-verdict on ship path

Tuned to +8, workers recycled, Rigby re-ran same 5 queries. Q1-Q4 counts queries all pass; Q5 still dominated → Rigby escalated per Q3 stop-condition. Claude presented 4 options to Chris (Shape C, ship-with-limitation, per-file cap, roll back). Chris D-verdict: "let's go with your suggestions" ratifying the ship-with-limitation path (option 2).

**Anti-rubber-stamp check:** both SIGN cycles had `tool_runs` non-empty (repo_tool + search_docs live dispatches). No rubber-stamp risk observed at either turn.

---

## §3 — Novel precedent

1. **First arc-close-to-pilot execution in same day.** Group 2700 closed at S2817 (early morning 2026-07-18); S2818 opened + shipped a §8 follow-on queue item on the same calendar day. Demonstrates the §8 queue is empirically actionable, not just documented.
2. **First OP3 trigger outside audit shape.** Sessions S2811-S2817 all ran OP3 in audit-shape (T1-T6 + canonical summary). S2818 runs OP3 in pilot shape (implementation + measurement + iteration). Rigby's post-authoring SIGN surfaced empirical monoculture finding that open SIGN didn't — extending OP3 cross-shape generality evidence.
3. **First measured-regression ratification.** Prior arc envelopes ratified clean successes (with follow-ons queued for improvements). S2818 ratifies a mechanism with a documented KNOWN regression as the deliverable's evidence value. Chris explicitly accepted the trade-off; envelope §5 Limitations codifies it as ratified rather than hidden.
4. **Escalation-not-tuning discipline.** Rigby's Q3 stop-condition prevented open-ended magnitude iteration. When +8 failed the same criterion +20 failed, the escalation path fired immediately rather than trying +5, +3, +2, etc. Playbook §7 "measure twice, cut once" applied via bounded iteration count.

---

## §4 — What shipped vs what didn't

**Shipped:**
- Authority-boost mechanism at magnitude=8, scoped to PLATFORM_INVENTORY.md only
- 7 unit + integration tests (magnitude-decoupled — no test edits needed for future tuning)
- Envelope with PLAYBOOK-6.10.9 stable-state-pointer + file+line evidence + (i)/(ii)/(iii) verified-state outcomes across baseline / +20 / +8 measurements

**Not shipped (queued):**
- Shape C query-intent gating (Chris ratified as next arc — top of S2819 queue)
- Additional authority anchors (DOC_LIFECYCLE, PLATFORM_WHAT_IT_IS, CLAUDE.md) — held per Rigby SIGN Q3 1-doc constraint; add after Shape C proves the mechanism
- Per-file cap in `top_k` (envelope §6 alternate mitigation)
- Embedding-retrieval migration (already in 2799 §8; reinforced priority)
- Fix for Q5 regression — accepted as documented trade-off per Chris D-verdict

---

## §5 — Ledger + provenance

- **Zoom-out ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows at S2818 open; two folds this session:
  - Fold A (Rigby SIGN Q4 open zoom-out — rot/hidden-policy/fork risk): `same_pr_mitigatable` — 2 mitigated same-PR (exact-path + explicit comment/test); 1 deferred to envelope §6 (fork risk).
  - Fold B (Rigby OP3 Q4 post-authoring — result-set monoculture): `future_trigger` — recorded as evidence for Shape C next arc scope + per-file cap as alternate mitigation.
  - Post-close ledger: 116 rows (baseline 114 + 2 this session).
- **Recycle log:** `logs/recycle_events.jsonl` — 2 in-session recycles (magnitude iteration between +20 and +8) + 1 close-cascade recycle post-merge per PLAYBOOK-7.4.4.
- **Freshness log:** `logs/session_freshness.jsonl` — grew by 1 at S2818 open.
- **Baseline HEAD:** `0f417301b35d` (S2817 close cascade).
- **Ratification HEAD:** (filled at merge).

---

## §6 — Candidates for S2819

**Ranked by architectural uncertainty × risk × unblocked flows:**

1. **⭐ Shape C — query-intent gating** (Chris-ratified follow-on from this session; top of queue). Smallest next mechanism: add count-intent heuristic (regex on "how many" / "count of" / "total" / "number of" / etc.); apply `_authority_bonus` only when heuristic fires. Re-run same 5-query batch. Success criterion: Q1-Q4 still in top-3 AND Q5 returns `docs/topics/spider-network.md` to top-3.
2. **Playbook v0.9 amendment (OP3 codification)** — 8/8 across arc + first post-arc datapoint. Well past codification threshold.
3. **Remaining 2799 §8 queue** (items #2 HIGH-DRIFT rule canonicalization, #4 parent §4 T5 clause update, #5-#8 per 2799 §8 ordering).
4. **Colorado Phase 4** statute-citation content quality.
5. **BettingPage first-user trace** / **Stock Intelligence** — real user-facing net-new work.

**Recommended default:** Shape C. It's the direct next iteration of this session's substrate; Chris explicitly ratified it as the ship path's follow-on; and it closes the loop on this pilot's known regression before compounding more discovery-layer work.

---

## §7 — S2818 lessons to carry

1. **Static magnitude on token-overlap scorers is a compromise, not a solution.** For chunky docs (PLATFORM_INVENTORY.md = 59 chunks), even +8 floods the ranker on any query with weak overlap.
2. **Rigby's Q2 initial recommendation (+20) was empirically too aggressive**, but the tuning-down path itself was insufficient — the ceiling is architectural, not magnitude. Accepting this early rather than iterating further saved cycles.
3. **OP3 empirical monoculture finding could not have surfaced in open SIGN** — it required measurement. Reinforces OP3's cross-shape value beyond audit sessions.
4. **Ratification of measured regressions is a valid pattern.** The pilot's evidence value IS the empirical finding that the mechanism has an architectural ceiling; documenting that as a first-class Limitations section (not hiding it) is what makes the follow-on Shape C well-motivated.
5. **`make celery-recycle` between measurement iterations works cleanly** — no session freshness drift observed between the +20 and +8 measurements; workers picked up code changes in both cycles.

---

**End of S2818 handoff. Close cascade PR + workspace deliverable mirror + pin rotation follow this ship.**
