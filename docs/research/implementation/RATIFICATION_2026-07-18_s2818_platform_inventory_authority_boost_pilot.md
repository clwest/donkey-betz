---
title: "S2818 PLATFORM_INVENTORY.md Authority-Boost Pilot Ratification Record (2026-07-18)"
status: active
authority: ratification-record
session_added: 2818
ratification_date: 2026-07-18
ratifier: chris
routing: rigby-pa-chat joint SIGN (open scope Q1-Q4 + post-authoring OP3 Q1-Q4 with empirical stop-condition escalation) + Chris D-verdict on original spec + Chris mid-pilot escalation D-verdict on ship-with-limitation path
scope: |
  S2818 (2799 §8 item #1) — discovery-layer enforcement pilot for DOC_LIFECYCLE §2c
  "sole authoritative counts source" convention. Adds a per-file authority-bonus
  mechanism to core.rag.top_k that applies unconditionally (independent of boost_hints),
  scoped to docs/PLATFORM_INVENTORY.md only per 2799 §8 explicit 1-doc constraint.
  Ships at magnitude=8 with a documented known regression on non-counts how-to queries.
serves_arc: Group 2700 /docs/ restructuring follow-on queue (2799 §8 item #1)
precedent_ratifications:
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md (S2817 arc close — §8 follow-on queue authorizes this pilot)
  - docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md (S2813 T3 — C5 evidence that motivates this pilot)
ratified_documents:
  - core/rag.py (amended — new AUTHORITY_FILE_BONUS dict + _authority_bonus helper; applied unconditionally in top_k after the boost_hints gate)
  - core/tests/test_rag_authority_boost_2818.py (new — 5 unit tests + 2 integration tests; validates mechanism at whichever magnitude is set)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2818 open freshness — verdict FRESH · head=0f417301b35d · celery_stale=0/5 (session_lifecycle open output at S2818 open)
  - S2818 open scope SIGN (Rigby, pin pa-43db3c9851764ee7) — AGREE on mechanism (Q1 tool-verified), PARTIAL on magnitude (Q2 recommended +20 start), DISAGREE on scope expansion (Q3 keep 1-doc), AGREE on real coupling risk (Q4 zoom-out — rot / hidden-policy / fork). tool_runs non-empty (repo_tool ×2 + search_docs live).
  - S2818 post-authoring OP3 SIGN (Rigby, same pin) — AGREE regression is real (Q1), PARTIAL on magnitude feasibility (Q2 — "not provably infeasible but not guaranteed"), Path B ship-condition triggered escalation (Q3), NEW empirical risk surfaced (Q4 — result-set monoculture: per-chunk bonus on chunky doc floods ranker). tool_runs non-empty (repo_tool + re-run search_docs confirming regression stable).
frozen: true
---

# S2818 PLATFORM_INVENTORY.md Authority-Boost Pilot — Ratification Record

Frozen canonical record of Chris's ratification of the S2818 discovery-layer enforcement pilot on 2026-07-18 for `docs/PLATFORM_INVENTORY.md`. Ships the smallest possible mechanism that satisfies 2799 §8 item #1 while documenting an empirical finding that a follow-on Shape C (query-intent gating) is required before this pattern can scale beyond counts queries. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-18 (America/Denver operator timezone)
- **Session:** S2818 (first session after Group 2700 arc close at S2817)
- **Scope:** 2799 §8 item #1: "propose 1-doc retrieval-weight boost for PLATFORM_INVENTORY.md; measure post-boost success@3 rate on T3 (c) scenarios"
- **Motivation:** T3 (S2813) C5 evidence — `search_docs("How many spiders do we have")` returns archived Oct 2025 morning report as top-1 with PLATFORM_INVENTORY.md absent from returned set. The DOC_LIFECYCLE §2c "sole authoritative counts source" convention holds in-doc but is falsified at the discovery layer. Users searching for counts get archived stale answers instead of the canonical inventory. See `docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md` §7 C5 and §8 Rank 4 for the full pain diagnosis.
- **Ratifier:** Chris ("go ahead" D-verdict on original spec at S2818 open; "let's go with your suggestions" D-verdict on ship-with-limitation path at mid-pilot escalation).

---

## §2. Ratified Deliverables

### §2.1 `core/rag.py` — new `AUTHORITY_FILE_BONUS` + `_authority_bonus`

Adds a per-file authority-boost mechanism that applies unconditionally in `top_k()`:

```python
AUTHORITY_FILE_BONUS = {
    "PLATFORM_INVENTORY.md": 8,
}

def _authority_bonus(path: str) -> int:
    """S2818 pilot — exact-path authority boost per DOC_LIFECYCLE §2c."""
    if not path:
        return 0
    # Corpus stores paths without the leading 'docs/' prefix, but callers
    # may pass a full path. Normalize by stripping the prefix once.
    key = path[5:] if path.startswith("docs/") else path
    return AUTHORITY_FILE_BONUS.get(key, 0)
```

Invocation site inside `top_k` (post the `if boost_hints:` gate so the PA `search_docs` call path — which passes `boost_hints=False` — still receives the boost):

```python
# S2818: authority boost applies regardless of boost_hints.
base += _authority_bonus(row.get("file", ""))
```

**Design constraints (from joint SIGN):**

- **Exact-path match, not regex** (Rigby SIGN Q4 mitigation vs rot fragility). Rename of the target file breaks the boost loudly rather than silently boosting the wrong doc.
- **Applied unconditionally** — necessary because `search_docs` explicitly passes `boost_hints=False` to skip legacy learning-loop bias (see `core/services/td_handlers_ops.py:6072-6077`). Flipping to `True` was rejected as Shape B in the open SIGN.
- **Magnitude 8** — tuned down from Rigby's Q2 initial recommendation of +20 after post-authoring OP3 SIGN showed +20 causes result-set monoculture on non-counts queries (see §5). +8 matches the existing `_file_bonus()` legacy magnitude.
- **Pilot scope 1 doc** — Rigby SIGN Q3 held the 2799 §8 line against scope expansion during design; test `test_pilot_scope_is_one_doc` enforces this as a guardrail against silent later expansion.

### §2.2 `core/tests/test_rag_authority_boost_2818.py` — 7 tests

- **Unit** (`AuthorityBonusUnitTests`): 5 tests — exact match, docs/ prefix normalization, non-authority zero, empty path zero, pilot-scope-is-one-doc guardrail.
- **Integration** (`AuthorityBonusIntegrationTests`): 2 tests — T3 C5-shape lift-to-top-3 with `boost_hints=False` (primary success criterion), and unconditional-application check.

All 7 pass at magnitude=8 (tests reference `AUTHORITY_FILE_BONUS["PLATFORM_INVENTORY.md"]` directly rather than hardcoding the value, so tuning does not require test edits).

---

## §3. Empirical Evidence (per PLAYBOOK-6.10.9 verified-state outcome)

**Stable-state pointer:** measurements below were captured against the current-HEAD implementation in this PR's branch. Baseline captured before `core/rag.py` change was applied; post-boost captured after Celery workers were recycled via `make celery-recycle`. Both dispatches came from Rigby's `search_docs` handler at `core/services/td_handlers_ops.py:6011-6169`.

### §3.1 Baseline (pre-code, current HEAD `0f417301b35d`)

Dispatched by Rigby via 5 `search_docs` calls at S2818 open. All 5 queries returned zero PLATFORM_INVENTORY.md chunks in their result sets.

| Q | Query | Top-1 | PLATFORM_INVENTORY.md in set? |
|---|---|---|---|
| 1 | "How many spiders do we have" | `docs/archive/old-structure/status/historical/morning-report-2025-10-02.md#7` | **No** |
| 2 | "How many agents do we have" | `docs/audit-2026/00-AUDIT-PLAN.md#5` | **No** (AUDIT_FINDINGS.md#1 was in set, per Rigby report) |
| 3 | "How many database models" | `docs/archive/experimental/super_system/TESTING_VISION.md#22` | **No** |
| 4 | "How many celery tasks" | `docs/archive/handoffs-pre-800/SESSION_317_DREAM_JOURNAL_FIX.md#1` | **No** |
| 5 | "add a new spider to the network" | `docs/AGENTS_REFERENCE.md#35` | **No** |

**Verified state (i):** the T3 C5 finding is stable on current HEAD — the sole-counts-source convention is completely invisible at the discovery layer for the entire counts-query class.

### §3.2 Post-boost at magnitude=20 (rejected)

After first implementation (magnitude=20) and worker recycle, Rigby re-ran the same 5 queries:

| Q | Top-1 | PLATFORM_INVENTORY.md rank |
|---|---|---|
| 1 | `docs/PLATFORM_INVENTORY.md#1` | **1** ✅ primary criterion met |
| 2 | `docs/PLATFORM_INVENTORY.md#53` | **1** |
| 3 | `docs/PLATFORM_INVENTORY.md#1` | **1** |
| 4 | `docs/PLATFORM_INVENTORY.md#1` | **1** |
| 5 | `docs/PLATFORM_INVENTORY.md#10` | **1** ⚠️ regression |

**Verified state (ii):** primary criterion met, but Q5 regression confirmed empirically. `docs/topics/spider-network.md` (T3 B1 intended target for the "add a new spider" scenario) no longer appears in top-3. Rigby's post-authoring OP3 SIGN Q4 zoom-out surfaced the mechanism: **result-set monoculture** — PLATFORM_INVENTORY.md has 59 chunks in the corpus; with a per-chunk +20 bonus, many chunks with weak overlap crowd out complementary docs.

### §3.3 Post-boost at magnitude=8 (shipped)

After tuning to +8 (per Rigby's stop-condition Path B), workers recycled, same 5 queries:

| Q | Top-1 | PLATFORM_INVENTORY.md rank | Stop-condition |
|---|---|---|---|
| 1 | `docs/PLATFORM_INVENTORY.md#1` | **1** | Q1 passes ✅ |
| 2 | `docs/PLATFORM_INVENTORY.md#53` | **1** | passes |
| 3 | `docs/PLATFORM_INVENTORY.md#1` | **1** | passes |
| 4 | `docs/PLATFORM_INVENTORY.md#1` | **1** | passes |
| 5 | `docs/PLATFORM_INVENTORY.md#10` | **1** | Q5 still dominated — Escalate |

**Verified state (iii):** at +8 the primary criterion (Q1 in top-3) is still met AND the Q5 regression is not resolved. Static magnitude alone cannot satisfy both criteria — a structural limit of the per-chunk-bonus + substring-token-overlap mechanism. Rigby's stop-condition triggered escalation to Shape C intent-gating (see §6 follow-on).

---

## §4. SIGN Sessions (verbatim key content)

### §4.1 Open scope SIGN (Rigby, pin `pa-43db3c9851764ee7`)

**Q1 mechanism verify — AGREE (tool-verified).** Rigby ran `repo_tool` reads of `core/rag.py:1-82` + `core/services/td_handlers_ops.py:6045-6165` and re-ran `search_docs("How many spiders do we have")` to confirm current-HEAD baseline. Confirmed: (i) `_file_bonus` fires only when `boost_hints=True`; (ii) `search_docs` passes `False`; (iii) therefore Shape A (new always-on bonus list) is the smallest correct pilot mechanism.

**Q2 magnitude calibration — PARTIAL.** Rigby recommended starting at +20 (headroom over legacy 8) since raw scores aren't observable from `search_docs` output. Flagged that dev-only debug score exposure would allow tighter empirical calibration — declined by Claude as scope creep.

**Q3 scope creep pressure-test — DISAGREE expansion.** Rigby held the 2799 §8 1-doc constraint. Reasoning: adding DOC_LIFECYCLE/PLATFORM_WHAT_IT_IS/CLAUDE.md in the same change blurs the causal read on whether the mechanism works.

**Q4 zoom-out (per PLAYBOOK-6.10.7) — AGREE real coupling risk.** Rigby raised three concerns to mitigate in same PR: rot/rename fragility (mitigated: exact-path match); hidden retrieval policy (mitigated: explicit comment + unit test); fork risk vs embedding stack (deferred: envelope §6 queues follow-on).

### §4.2 Post-authoring OP3 SIGN (same pin — 7th consecutive OP3 trigger extending the S2811-S2817 Group 2700 arc streak)

Dispatched after implementation + worker recycle + baseline capture + post-boost measurement at magnitude=20. Rigby ran `repo_tool` re-read of `core/rag.py` (verified `AUTHORITY_FILE_BONUS` shipped correctly at lines 29-31 + unconditional invocation) + re-ran Q5 live (confirmed regression is stable, not a chunk-drift artifact).

**Q1 empirical read — AGREE.** Regression on Q5 is a real degradation, not an acceptable outcome.

**Q2 magnitude feasibility — PARTIAL AGREE.** Static magnitude is inherently a compromise but not provably infeasible; +8 worth trying with tight stop-condition.

**Q3 recommendation — Path B (tune to +8).** With explicit stop-condition: if Q1 stays top-3 AND Q5 non-dominated → ship; if Q5 still dominated at +8 → escalate to Shape C rather than continue tuning cycles.

**Q4 zoom-out — NEW empirical risk surfaced.** Result-set monoculture: unconditional per-chunk bonus on a large doc (PLATFORM_INVENTORY.md = 59 chunks) causes the ranker to return multiple chunks from the same file, crowding out complementary docs. Mitigation paths named: (a) intent gating, (b) per-file caps in `top_k`, (c) migration to embedding retrieval with document-level authority weighting.

### §4.3 Stop-condition triggered

Post-tune measurement at magnitude=8 showed Q5 remained dominated by PLATFORM_INVENTORY.md#10 top-1 with `docs/topics/spider-network.md` still absent from top-3. Per Rigby's Q3 stop-condition, **static magnitude tuning is empirically closed** — escalate to Shape C.

---

## §5. Limitations & Known Regressions (measured, ratified as accepted trade-off)

Chris ratified shipping the +8 mechanism WITH the following documented limitations, on condition that Shape C is queued as the next pilot arc:

1. **Non-counts how-to queries regressed on any query where PLATFORM_INVENTORY.md has weak token overlap.** Concrete evidence: `search_docs("add a new spider to the network")` returns PLATFORM_INVENTORY.md#10 / #59 / #1 as top-3; `docs/topics/spider-network.md` (T3 B1 intended target) no longer appears. B1 was already a MEDIUM-severity scenario per T3 §8 Rank 3 (Ambiguity); this pilot escalates it to HIGH severity for the counts-adjacent query surface.

2. **Result-set monoculture.** Because the bonus applies per-chunk, a doc with many chunks (PLATFORM_INVENTORY.md = 59) can dominate the top-K with multiple chunks from itself, reducing result diversity even when the boost is otherwise correct. Concrete evidence: Q1 top-3 is all PLATFORM_INVENTORY.md chunks (#1, #2, #3); no complementary docs (DOC_LIFECYCLE, "how to regenerate inventory," etc.) appear.

3. **Static magnitude cannot satisfy both criteria simultaneously.** Empirical stop-condition test at +8 confirmed the limit is structural, not a magnitude-selection error. Any future work in this substrate layer should not attempt further static-magnitude tuning.

4. **Substring-based token matching.** The `top_k` scorer uses `w in tl` (substring), so query token "in" matches "inventory," which contributes to the monoculture failure mode on unrelated queries. Not addressed here.

These limitations are the deliverable's evidence value — the pilot proved the mechanism has an architectural ceiling. Follow-on work (§6) addresses each explicitly.

---

## §6. Follow-On Queue (updates 2799 §8)

Adds to the Group 2700 §8 follow-on queue based on this pilot's empirical findings:

- **Shape C — query-intent gating** (was Rigby SIGN Q3 escalation path, now promoted to explicit next arc). Only apply `_authority_bonus` when the query matches a count-intent pattern (heuristics like "how many", "count of", "total", "number of"). Preserves counts-query success; eliminates non-counts regression. Smallest next evidence: implement + re-run same 5-query batch.
- **Per-file cap in `top_k`** (Rigby OP3 Q4 alternate mitigation). Cap max chunks per file in top-K to preserve diversity. Different architectural approach; may compose with Shape C.
- **Embedding-based retrieval migration** (already in 2799 §8 zoom-out; this pilot reinforces the priority). Move authority weighting into `kb_tool.semantic_search` where document-level reranking replaces per-chunk substring scoring.

Chris ratified: Shape C is next on the S2818+ queue, ahead of the other 2799 §8 items, on the strength of this pilot's evidence.

---

## §7. Provenance

- **Session:** S2818 (first post-Group-2700-arc-close session)
- **Session pin:** `pa-43db3c9851764ee7` (label `s2818-discovery-layer-pilot`; minted at S2818 open via `session_lifecycle open`)
- **Baseline HEAD:** `0f417301b35d` (Group 2700 arc close cascade at S2817)
- **Ratification HEAD:** (filled at merge)
- **Merged PR:** (filled at merge)
- **Tools used:** Read/Grep for existing implementation analysis; Edit for `core/rag.py`; Write for test + envelope; `make celery-recycle` between magnitude iterations; Rigby `repo_tool` + `search_docs` for all evidence.
- **OP3 pattern:** 7th consecutive trigger extending the Group 2700 S2811-S2817 arc streak. First post-arc trigger. Playbook v0.9 amendment remains queued (2799 §8 item #3); this session provides an 8th datapoint on the pattern's cross-shape generality (pilot-shape, not audit-shape).
- **Twin-pointer discipline** per parent §5 D7: this envelope in `docs/research/implementation/` + workspace deliverable mirror at close cascade in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via ORM-direct create per memory `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.

---

**End of ratification record. Frozen at merge.**
