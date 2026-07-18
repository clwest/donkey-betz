---
title: "S2819 Shape C Query-Intent Gating Ratification Record (2026-07-18)"
status: active
authority: ratification-record
session_added: 2819
ratification_date: 2026-07-18
ratifier: chris
routing: rigby-pa-chat joint SIGN (open scope Q1-Q4 with empirical "list all" pattern extension + post-authoring OP3 re-verdict with corrected success criterion) + Chris D-verdict on ship
scope: |
  S2819 Shape C — query-intent gating for the S2818 AUTHORITY_FILE_BONUS
  mechanism. Adds a count/inventory-intent pattern check that gates the
  authority boost, preserving S2818 counts-query success while eliminating
  the empirically-measured non-counts monoculture regression documented
  in S2818 envelope §5. Pattern set kept minimal (6 patterns); pilot scope
  still 1 doc (PLATFORM_INVENTORY.md).
serves_arc: Group 2700 /docs/ restructuring follow-on queue (S2818 envelope §6)
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md (S2818 pilot — envelope §6 queued Shape C as this arc)
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md (S2817 arc close — grand-parent authorization via §8 item #1)
  - docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md (S2813 T3 — C5 and B1 evidence)
ratified_documents:
  - core/rag.py (amended — new _COUNT_INTENT_PATTERNS + _looks_like_count_query helper; new authority_gate parameter on top_k with auto-compute default; docstring updated to reflect gated behavior)
  - core/tests/test_rag_authority_boost_2818.py (amended — one test now passes authority_gate=True explicitly per Shape C semantics)
  - core/tests/test_rag_intent_gating_2819.py (new — 15 tests: 10 unit + 5 integration; validates gate mechanics + explicit override semantics + list-all pattern preservation)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2819 open freshness — verdict FRESH · head=2a01bc537911 · celery_stale=0/5 (session_lifecycle open output at S2819 open)
  - S2819 open scope SIGN (Rigby, pin pa-ebadb78a43034ff7) — AGREE mechanism (Q1 tool-verified), PARTIAL on pattern coverage (Q2 empirically escalated "list all" via live search_docs; deferred amount-of/inventory-of), DISAGREE Option A gate location (Q3 recommended Option B new param), AGREE net-new failure modes (Q4 zoom-out — false negatives / false positives / coupling / discoverability with mitigations). tool_runs non-empty (repo_tool + search_docs live).
  - S2819 post-authoring OP3 SIGN (same pin) — INITIALLY escalate on flawed criterion (spider-network.md restore, which was never in baseline); RE-VERDICT AGREE ship after corrected criterion presented. Q1 AGREE corrected analysis; Q2 AGREE 00-START contamination is separate finding, not shipping blocker; Q3 AGREE success-criterion-hygiene is codifiable methodology gotcha. tool_runs non-empty (repo_tool + 2× search_docs live re-verification).
frozen: true
---

# S2819 Shape C Query-Intent Gating — Ratification Record

Frozen canonical record of Chris's ratification of the S2819 Shape C intent-gating mechanism on 2026-07-18. Closes the loop on the S2818 pilot's documented non-counts regression while preserving the counts-query success criterion. Surfaces two novel findings: success-criterion hygiene gotcha and start-here-doc example-text contamination. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-18 (America/Denver operator timezone)
- **Session:** S2819 (second post-Group-2700-arc-close session; direct next-day follow-on from S2818 pilot)
- **Scope:** S2818 envelope §6 Follow-On item — query-intent gating around the AUTHORITY_FILE_BONUS mechanism. Chris ratified Shape C as top-of-queue at S2818 close.
- **Motivation:** S2818 shipped an unconditional per-chunk +8 authority boost on PLATFORM_INVENTORY.md that satisfied the counts-query success criterion (Q1-Q4 all returned PLATFORM_INVENTORY.md#1/#2/#3) but caused **result-set monoculture** on non-counts queries: 59 chunks × per-chunk bonus flooded the ranker even on queries with weak token overlap (T3 B1 "add a new spider to the network"). Rigby OP3 identified static magnitude as architecturally insufficient; Shape C gates the boost on query intent.
- **Ratifier:** Chris ("start s2819 with shape c" — direct-continuation directive at S2818 close; "Go" D-verdict on Shape C ship after corrected success-criterion analysis at S2819 post-authoring OP3 re-verdict).

---

## §2. Ratified Deliverables

### §2.1 `core/rag.py` — new pattern set + helper + gate

Adds three surfaces:

```python
_COUNT_INTENT_PATTERNS = (
    "how many",
    "how much",
    "number of",
    "count of",
    "total",
    "list all",
)


def _looks_like_count_query(question: str | None) -> bool:
    """S2819 pilot — detect count/inventory intent in a query."""
    if not question:
        return False
    q = question.lower()
    return any(p in q for p in _COUNT_INTENT_PATTERNS)
```

New parameter on `top_k`:

```python
def top_k(
    question: str,
    k: int = 8,
    boost_hints: bool = True,
    authority_gate: bool | None = None,
) -> list[dict]:
    ...
    if authority_gate is None:
        authority_gate = _looks_like_count_query(question)
    ...
    # S2819: authority boost is gated on query intent.
    if authority_gate:
        base += _authority_bonus(row.get("file", ""))
```

**Design constraints (from joint SIGN):**

- **6 patterns kept minimal** — "how many" / "how much" / "number of" / "count of" / "total" / "list all". "list all" added per Rigby SIGN Q2 empirical evidence: `search_docs("list all spiders")` at HEAD `2a01bc537` returned PLATFORM_INVENTORY.md dominating (S2818 unconditional-boost behavior); gating on counts-only patterns would have regressed that legitimate inventory query. Alternates (amount-of / inventory-of) deferred pending evidence of demand.
- **Option B gate location** (new param with auto-compute default) chosen over Option A (inline only) per Rigby SIGN Q3. Trades slightly more surface area for (a) testability with explicit force-on/force-off, (b) caller override for future intent-aware layers, (c) A/B experiment capability.
- **Substring matching not regex** — kept from S2818 approach per T5 systematic `\b` bug lesson (Group 2700 T5 §6 grep methodology finding). Queries are short and human-typed; "somehow many" false positive is theoretical.
- **Docstring updated** — `top_k` now documents the gated behavior explicitly; the S2818 "applies ALWAYS" note is replaced with the S2819 gated-on-intent semantics.
- **Pilot scope still 1 doc** — Shape C narrows the mechanism trigger condition without expanding `AUTHORITY_FILE_BONUS` beyond PLATFORM_INVENTORY.md. Multi-doc expansion requires separate SIGN cycle.

### §2.2 `core/tests/test_rag_intent_gating_2819.py` — 15 tests (new file)

- **Unit** (`LooksLikeCountQueryUnitTests`): 10 tests — one per pattern (matches expected), case-insensitive, non-count queries don't match, empty query, pilot-scope-is-6-patterns guardrail.
- **Integration** (`TopKIntentGatingIntegrationTests`): 5 tests — auto-gate fires for count query, auto-gate skips for non-count query (the T3 B1 regression fix), explicit `authority_gate=True` override, explicit `authority_gate=False` suppression, list-all pattern integration.

### §2.3 `core/tests/test_rag_authority_boost_2818.py` — 1 test updated

`test_authority_bonus_applies_when_boost_hints_false` now passes `authority_gate=True` explicitly, reflecting the S2819 semantics change: the S2818 "authority boost fires when boost_hints=False" invariant is now conditional on the gate. Test docstring updated to reflect the new semantics.

All 22 tests (7 from S2818 + 15 new S2819) pass at merge.

---

## §3. Empirical Evidence (per PLAYBOOK-6.10.9 verified-state outcome)

**Stable-state pointer:** measurements below captured against the S2819 branch after `make celery-recycle`. Baseline references come from the S2818 envelope §3.1 pre-boost measurements (at HEAD `0f417301b35d`) and S2818 envelope §3.3 post-boost measurements (at HEAD `90ab139a9`).

### §3.1 Full 6-query batch comparison

| Q | Pre-boost baseline (S2818 §3.1) | S2818 shipped +8 unconditional (§3.3) | S2819 Shape C (this ratification) | Shape C verdict |
|---|---|---|---|---|
| Q1 "How many spiders do we have" | archive/morning-report-2025-10-02 top-1 | PLATFORM_INVENTORY.md#1/#2/#3 | PLATFORM_INVENTORY.md#1/#2/#3 | ✅ counts preserved |
| Q2 "How many agents do we have" | audit-2026/00-AUDIT-PLAN.md top-1 | PLATFORM_INVENTORY.md#53/#1/#2 | PLATFORM_INVENTORY.md#53/#1/#2 | ✅ counts preserved |
| Q3 "How many database models" | archive/experimental/TESTING_VISION.md top-1 | PLATFORM_INVENTORY.md#1/#3/#30 | PLATFORM_INVENTORY.md dominates top-3 | ✅ counts preserved |
| Q4 "How many celery tasks" | archive/handoffs-pre-800/DREAM_JOURNAL_FIX top-1 | PLATFORM_INVENTORY.md#1/#3/#19 | PLATFORM_INVENTORY.md dominates top-3 | ✅ counts preserved |
| Q5 "add a new spider to the network" | AGENTS_REFERENCE.md#35 top-1, archive #2/#3, **PLATFORM_INVENTORY.md not in set** | PLATFORM_INVENTORY.md#10/#59/#1 (S2818 regression) | **PLATFORM_INVENTORY.md rank >20** (out of returned set); top-1 = 00-START-NEXT-SESSION.md (self-contamination — see §5) | ✅ monoculture eliminated |
| Q6 "list all spiders" (Rigby SIGN Q2 addition) | not measured pre-S2818 | dominates PLATFORM_INVENTORY.md (S2818 unconditional; observed at S2819 SIGN open) | PLATFORM_INVENTORY.md dominates top-3 | ✅ list-all preserved via pattern set |

**Verified state (i):** Shape C preserves the S2818 primary criterion — all four counts queries (Q1-Q4) plus Q6 list-all still return PLATFORM_INVENTORY.md in top-3.

**Verified state (ii):** Shape C eliminates the S2818 non-counts regression — Q5 no longer has PLATFORM_INVENTORY.md dominating; rank moved from #1 (S2818) to >20 (out of returned set). Result-set monoculture on B1-shape queries is resolved.

**Verified state (iii):** Q5 top-1 shifted from AGENTS_REFERENCE.md (pre-boost baseline) → PLATFORM_INVENTORY.md#10 (S2818) → 00-START-NEXT-SESSION.md#3 (S2819). The S2819 top-1 is caused by same-session self-contamination (this pilot's start-here doc text mentions "add a new spider to the network" as example wording); **the Shape C mechanism itself is exonerated** — see §5.2.

### §3.2 Success-criterion misdiagnosis + correction

**Initial (flawed) criterion set at S2819 SIGN open:**
> "Q5 returns `docs/topics/spider-network.md` to top-3"

**Empirical baseline reality:** S2818 envelope §3.1 pre-boost top-1 for Q5 was `docs/AGENTS_REFERENCE.md#35`; full baseline top-3 was AGENTS_REFERENCE + 2 archive/REALITY_FIXES docs. **`docs/topics/spider-network.md` was NEVER in the pre-boost top-3.** The T3 §3 B1 label "intended target" was aspirational (identifying where the user *should* end up), not empirical (what search *actually* returned).

**Corrected criterion (post OP3 re-verdict):**
> "PLATFORM_INVENTORY.md monoculture eliminated (rank drops from top-3 to out-of-top-K) AND counts-query top-3 preserved AND Q6 list-all preserved."

Under the corrected criterion, Shape C succeeded on all three axes. Under the flawed criterion, no mechanism could have succeeded (spider-network.md would have to be lifted from absent-in-baseline to top-3 — that's not a regression fix, that's a novel discovery task).

---

## §4. SIGN Sessions

### §4.1 Open scope SIGN (Rigby, pin `pa-ebadb78a43034ff7`)

Ninth-consecutive OP3 trigger extending the Group 2700 arc streak into a second pilot-shape session.

**Q1 mechanism verify — AGREE (tool-verified) with 2 integration notes.** Rigby `repo_tool` read `core/rag.py` at HEAD `2a01bc537911`. Confirmed insertion points clean. Integration notes: (a) `top_k` docstring says "applies unconditionally per S2818" — will become false, must update; (b) `build_docs_context` calls `top_k` — new param is optional so no caller breakage. Both applied.

**Q2 pattern coverage — PARTIAL AGREE; empirical extension.** Rigby dispatched `search_docs("list all spiders")` LIVE and observed PLATFORM_INVENTORY.md dominating (S2818 unconditional-boost residual). Concluded: "list all" queries are in the same "inventory-ish intent" family as counts queries. Gating on counts-only patterns would REGRESS that behavior. Recommendation adopted: add "list all" to pattern set. amount-of / inventory-of deferred.

**Q3 gate-location — DISAGREE Option A; AGREE Option B.** Recommended new param `authority_gate: bool | None = None` on `top_k` with auto-compute default. Rationale: testability + caller override + A/B capability. Tri-state enum `Literal["auto","on","off"]` noted as future-consideration but not needed for pilot.

**Q4 zoom-out (per PLAYBOOK-6.10.7) — AGREE net-new failure modes.** Four risks named:
1. **False negatives** (count query worded unusually, boost silently skipped) — mitigated: regression test suite covering Q1-Q4 phrasings.
2. **False positives** (`"total"` as high-risk token: "total redesign", "total failure") — accepted for pilot; watch for Q5-like regressions.
3. **Coupling** (multi-authority-doc expansion needs per-doc intent maps) — deferred: envelope §6 queues per-doc gate design.
4. **Discoverability** (future dev sees mystery "why isn't search finding X") — mitigated: explicit helper name, updated docstring, tests as executable contract.

### §4.2 Post-authoring OP3 SIGN — INITIAL ESCALATE → RE-VERDICT SHIP

**Initial verdict:** After implementation + worker recycle + live 6-query measurement, Rigby verdict was **ESCALATE** because Q5 top-1 was `docs/00-START-NEXT-SESSION.md` (not the "expected" `docs/topics/spider-network.md` per my SIGN-routing criterion).

**Correction routed:** Claude noted the criterion was flawed — S2818 pre-boost baseline never had `docs/topics/spider-network.md` in top-3; the T3 "intended target" label was aspirational. Real Q5 goal was "monoculture elimination + baseline-shape restoration."

**Re-verdict SIGN (same pin):**

**Q1 corrected analysis — AGREE.** Rigby re-ran Q5 live to confirm current top-3 matches Claude's report. Confirmed Shape C succeeded at underlying goal even though literal criterion was unwinnable-as-stated.

**Q2 shipping blocker classification — AGREE separate finding.** 00-START-NEXT-SESSION.md contamination is same class as T3 C2 (start-here doc dominance when queries touch its example text). Not caused by Shape C mechanism. Ship Shape C + queue contamination fix as follow-on.

**Q3 zoom-out (success-criterion hygiene) — AGREE codifiable gotcha.** Rigby articulated the rule: "A success criterion must be empirically grounded in the pre-change baseline, not an 'intended target' label from narrative analysis. Baseline capture must include: top-K list + ranks for all named target docs + explicit 'was it present?' check before locking criteria." Novel, generalizable, not one-off.

**Bottom line:** RE-VERDICT = SHIP Shape C.

---

## §5. Limitations & Known Findings

### §5.1 Codifiable methodology gotcha — success-criterion hygiene

**Finding (Rigby OP3 Q3 zoom-out — novel):** A success criterion phrased as "restore doc X to top-3" is unwinnable-as-stated if doc X was never in the pre-change top-3. The T3 §3 "intended target" labels are aspirational (where the user *should* end up), not empirical (where search *actually* went). Baseline capture must include, per named target doc, an explicit "present in top-K? (yes/no)" check before locking a criterion.

**Recommendation for future pilot arcs:**
- When routing a scope SIGN, include the FULL top-K list from the baseline (not just top-1), with named target docs called out per-doc as present or absent.
- If a target doc is absent from the baseline, the criterion "restore X to top-K" cannot apply. Reframe as "eliminate regression on axis Y" or "restore baseline-shape top-K."

**Playbook candidate:** proposed as v0.9-adjacent minor amendment. One trigger observed (S2819); no cross-arc corroboration yet; observe next 2 pilot-arcs before codification per PLAYBOOK §20 two-triggers rule.

### §5.2 Start-here doc example-text contamination

**Finding:** current Q5 top-1 is `docs/00-START-NEXT-SESSION.md#3` because the Shape C candidate description I wrote at S2818 close contains the exact phrase "add a new spider to the network" as example text. Docs cascade re-embedded that doc, and Rigby's `search_docs` now surfaces it for the same phrase used to describe it.

This is the same class as T3 §7 C2 (`search_docs("Group 2700 docs restructuring T1 audit")` returned three consecutive chunks of `00-START-NEXT-SESSION.md`) and T3 §8 Rank 1 (misleading-meta-dominance). Not new; not caused by Shape C.

**Mitigation options (queued as follow-on):**
- Exclude `docs/00-START-NEXT-SESSION.md` and `docs/handoffs/SESSION_*.md` from `search_docs` corpus (surgical fix).
- Reduce per-chunk weight for start-here-class docs.
- Elevate example-text detection into the ranker.

### §5.3 Substring matching risk on `"total"`

Per Rigby SIGN Q4 (2): `"total"` as a bare pattern matches "total redesign", "total failure", etc. For pilot, accepted because PLATFORM_INVENTORY.md only receives the boost — if the query's other terms have zero overlap with inventory content, the boost still can't create signal from nothing. But if we add more authority docs later, per-doc intent gates would be needed (envelope §6 follow-on).

### §5.4 Empirical evidence-grounding requirement for gate patterns

Per Rigby SIGN Q2: "list all" was added ONLY because live `search_docs` at HEAD confirmed the current behavior would regress without it. amount-of / inventory-of were declined because there's no empirical evidence of demand. Adding patterns speculatively expands the false-positive surface. Any future pattern additions should follow the same empirical-evidence-first rule.

---

## §6. Follow-On Queue (updates S2818 envelope §6)

Adds to the follow-on queue based on S2819 empirical findings:

- **Start-here doc example-text contamination fix** (novel from §5.2). Options: corpus exclusion of `docs/00-START-NEXT-SESSION.md` and `docs/handoffs/SESSION_*.md`; or reduced per-chunk weight for these classes; or example-text detection in ranker. Highest-impact next mechanism for the discovery-layer arc after this pilot.
- **Success-criterion hygiene amendment** (novel from §5.1) — codify as playbook rule after 1-2 more pilot-arc triggers.
- **Per-doc intent gates** (from S2819 SIGN Q4 coupling risk) — needed when `AUTHORITY_FILE_BONUS` expands beyond 1 doc. Different authority docs may want different intent patterns (e.g., DOC_LIFECYCLE.md wants "how do I" or "process for", not "how many").
- **Expand `AUTHORITY_FILE_BONUS` to additional authority anchors** (deferred from S2818 SIGN Q3) — now unblocked by Shape C proving the gated mechanism works. Candidates: `DOC_LIFECYCLE.md`, `PLATFORM_WHAT_IT_IS.md`, `CLAUDE.md`.
- **Embedding-based retrieval migration** (in 2799 §8 originally; now reinforced by S2818 + S2819 findings) — move authority weighting into `kb_tool.semantic_search` where document-level reranking replaces per-chunk substring scoring.

---

## §7. Provenance

- **Session:** S2819 (second post-Group-2700-arc-close session)
- **Session pin:** `pa-ebadb78a43034ff7` (label `s2819-shape-c-intent-gating`; minted at S2819 open via `session_lifecycle open`)
- **Baseline HEAD:** `2a01bc537911` (S2818 close cascade)
- **Ratification HEAD:** (filled at merge)
- **Merged PR:** (filled at merge)
- **Tools used:** Read/Grep for existing state; Edit for `core/rag.py` (helper + gate + docstring) + test update; Write for new test file + envelope; `make celery-recycle` post-implementation; Rigby `repo_tool` + `search_docs` for all live evidence.
- **OP3 pattern:** 9th consecutive trigger. First INITIAL-ESCALATE → RE-VERDICT-SHIP flow in the streak — Rigby's initial verdict was based on my flawed success criterion; corrected framing produced ship. Reinforces that post-authoring SIGN can catch criterion errors, not just implementation errors.
- **Novel finding:** the "success-criterion-hygiene" methodology observation (§5.1) is a first-trigger for a potential v0.9-adjacent playbook amendment. Observe next 2 pilot-arcs for corroboration.
- **Twin-pointer discipline** per parent §5 D7: this envelope in `docs/research/implementation/`; workspace deliverable mirror deferred per S2818 pilot pattern (envelope is authoritative; workspace mirror at arc closure).

---

**End of ratification record. Frozen at merge.**
