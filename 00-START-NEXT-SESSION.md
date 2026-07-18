# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2821 CLOSED (2026-07-18 evening; picks up as S2822) — **SEMANTIC EVAL COMPLETE + CHRIS ROUTING-FIRST PIVOT + PHASE-0 METHODOLOGY PROPOSED**

**Refreshed 2026-07-18 evening (SESSION 2821 CLOSED — S2820 pivot directive executed: semantic retrieval EVALUATED against S2820 accidentally-built benchmark corpus. Chris mid-evaluation architectural re-framing: routing IS the boundary; fusion is downstream. Rigby joint-signed Phase-0 methodology proposal awaits Chris D-verdict at S2822 open. SIXTY-SIXTH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** First "routing not fusion" architectural pivot mid-evaluation; first per-family gate proposal (not global accuracy floor); first IS-ness vs aboutness architectural framing endorsed; first POINT relationship proposal; first IDENTITY+SELF-REFERENCE-C3 collapse candidate.**

**S2821 ship (0 feature PRs + 1 close cascade PR):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Close cascade (research/evaluation session — NO code) | **#TBD** · (SHA at merge) | main | handoff + envelope + 00-START update + pin rotation + docs pipeline |

**Handoff:** `docs/handoffs/SESSION_2821_SEMANTIC_RETRIEVAL_EVAL_ROUTING_PIVOT.md`
**Envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2821_semantic_eval_routing_pivot_phase0_proposed.md` (frozen at merge per PLAYBOOK-6.10.9)
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 114 rows unchanged (folds noted in envelope §5 for arc-close persistence per S2818/S2819/S2820 pattern; no in-session folds ledger-appended)

**Arc state at S2821 close:**
- **Discovery-layer arc:** **Lexical branch FEATURE COMPLETE** (S2818/S2819/S2820); **semantic branch EVALUATED** (S2821 — Path B hybrid drafted, then Chris re-framed as routing-first); **routing-first Phase-0 methodology PROPOSED** (joint-signed by Rigby, pending Chris ratification at S2822 open).
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817). §8 item #1 lexical execution: SHIPPED across S2818/S2819/S2820. §8 item #1 semantic-branch: EVALUATED at S2821. Full §8 item #1 discovery-layer arc now transitions to routing-first Phase-0 at S2822.

---

## S2822 CANDIDATES — SOLE RECOMMENDED DIRECTION

### ⭐ Chris-ratified architectural direction + Rigby joint-signed methodology

1. **⭐ Ratify Phase-0 methodology proposal + execute Phase-0** (SOLE recommended direction). Chris D-verdict at S2821 close-adjacent explicitly ratified routing-first architectural direction with 6 refinements. Rigby joint SIGN AGREE-no-blockers on Phase-0 methodology proposal with 4 schema refinements booked. Awaits Chris D-verdict on Phase-0 methodology proposal (as-is or with revisions).
   - **Phase-0 methodology detail:** See envelope §7 for full spec — 33-row expanded corpus, label schema with strict/loose target-set + answer_mode + has_literal_identifier fields, tri-state ambiguity/abstention policy, per-family gates (COUNT elevated to HIGH consequence), two-axis routing pressure-test (IDENTITY+SELF-REFERENCE-C3 collapse candidate + POINT relationship distinct from LOCATE).
   - **Concrete first steps for S2822 open:**
     1. Chris D-verdict on Phase-0 methodology proposal (envelope §7 as-is, or revise sections 7.1-7.9)
     2. Corpus expansion authoring (20 new labeled queries per §7.3 schema)
     3. Classifier A (flat) build + measure vs Classifier B (two-axis) build + measure
     4. Per-family precision/recall/F1 + confusion matrix + ambiguous-rate + abstention-rate + wrong-but-plausible rate
     5. Gate calibration from measurement (per §7.6 proposal frame)
     6. Two-axis collapse verification (IDENTITY+SELF-REF-C3 fold; POINT distinct)
     7. Route findings to Chris for Phase-1 (routing-table build) gate decision
   - **Non-goals for S2822 Phase 0 (Chris R#6):** no RRF / global fusion; no taxonomy constitutionalization; no routing-table implementation; no code substrate change.

### Available if Chris pivots away from Phase-0 execution

- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability
- **Stock Intelligence** — end-to-end verify (dashboard/brief/alert pipeline)
- **Playbook v0.9 amendment** — 10/10 triggers now including IN-LOOP variant + INITIAL-ESCALATE→RE-VERDICT-SHIP variant. Well past codification threshold.
- **Playbook v0.9-adjacent amendment (evidence-first baseline capture)** — 2 triggers (S2819 §5.1 surfacing + S2820 compliance). Wait for third trigger before codification per §20 two-triggers rule.
- **Remaining 2799 §8 queue** (items #4-#8): T5 clause update, file moves, per-handoff citation_health, retrieval-frequency telemetry, generator/automation coordination.
- **LegalDocument.generation_context** blank=True (Phase 2 model quirk)
- **GPT fallback for form-selection** on low-confidence

**Recommended default:** Item #1 Phase-0 ratification + execution. Chris explicitly asked me to return with the Phase-0 methodology + route through Rigby before execution. Both are done. Chris ratifies at S2822 open (or overrides with revisions).

---

## SESSION PIN — S2821 RETIRED (fresh mint required at S2822 open)

**Pin history (S2821):**

- `pa-c884459957614bbd` (label `s2821-semantic-evaluation`) minted at S2821 open; **retired at S2821 close (`force=true`, fifty-second consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2822 first-action fresh mint.

**S2822 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2821 handoff — §3 (novel precedent — first routing-first pivot mid-evaluation), §6 (S2822 direction), §7 (lessons)
# Read S2821 envelope — §7 for full Phase-0 methodology spec (label schema + gates + two-axis pressure-test)

# Sanity checks
brew services list | grep postgres

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2822-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2821 lessons to carry:**

1. **Routing IS the architectural boundary; fusion is per-family implementation detail.** Chris's re-framing at close-adjacent changed the S2822 shape from "how do we merge" to "how do we know which substrate to invoke." Non-obvious in advance; obvious in retrospect. Watch for similar pivots in future evaluation sessions.
2. **Retrieval-substrate specialization is real.** Lexical = IS-ness (this doc IS the answer); semantic = aboutness (this doc discusses the answer). Attempting to merge without routing accretes complexity that routing dissolves.
3. **Silent target-set relaxation is a real audit gotcha.** C2 T3 §7 target required BOTH 2701 + 2700; Claude initial evaluation accepted 2701 alone. Rigby caught via tool-grounded reading. Strict/loose target-set split now baked into Phase-0 label schema.
4. **Query-string stability matters.** Small variations flip top-1/top-3 across mechanisms. Locked BENCHMARK strings were the right mitigation. Future harnesses record queries verbatim.
5. **Per-family gates > global accuracy floor.** Chris explicit at Refinement #2: "high global score must not conceal failure in thin but high-consequence families like IDENTITY or SELF-REFERENCE." Per-family gates weight classifier accuracy floor by misroute consequence.
6. **Anti-rubber-stamp check via tool_runs works.** All 3 SIGN cycles had non-empty tool_runs. Rigby's live probes surfaced 5+ substantive refinements this session. Continue tool_runs check on every SIGN cycle.
7. **Fresh-session cascade close pattern applies to research sessions too.** No code changes this session, but full close cascade (handoff + envelope + 00-START update + pin rotation + docs pipeline + recycle) preserves continuity.

---

## Twin-pointer card

📁 **Repo — S2821 artifacts:**

- **Feature PR: NONE** (research/evaluation session, no code changes)
- **Close cascade PR:** #TBD (SHA at merge)
- **Substrate changes:** NONE (Chris lexical freeze extended; semantic default flip deferred)
- **Handoff:** `docs/handoffs/SESSION_2821_SEMANTIC_RETRIEVAL_EVAL_ROUTING_PIVOT.md`
- **Envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2821_semantic_eval_routing_pivot_phase0_proposed.md` (§3 evidence + §7 Phase-0 methodology proposal)
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session; folds noted in envelope §5)
- **Merge SHA:** filled at cascade PR merge
- **All 4 discovery-layer envelopes now live at:** `docs/research/implementation/RATIFICATION_2026-07-18_s2818_...md` + `s2819_shape_c_intent_gating.md` + `s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md` + `s2821_semantic_eval_routing_pivot_phase0_proposed.md`

🖥️ **Workspace UI — S2821 has NO twin-pointer workspace deliverable this session** — evaluation sessions keep envelopes in `docs/research/implementation/` as authoritative; workspace mirror deferred per S2818/S2819/S2820 pattern. Group 2700 arc's workspace deliverable (`37d6ca76-89c3-4966-8f4c-decc52ce8169`) remains authoritative for the /docs/ restructuring arc under which S2818/S2819/S2820/S2821 are §8 executions.

---

## Current repository state (S2821 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2821 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment 10/10 corroborated**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | **ARC CLOSED (S2817).** §8 item #1 discovery-layer FULL: lexical branch SHIPPED (S2818/S2819/S2820); semantic branch EVALUATED (S2821); routing-first Phase-0 methodology PROPOSED. |
| **Discovery-layer arc state** | Lexical FEATURE COMPLETE; semantic EVALUATED; **routing-first Phase-0 methodology PROPOSED — awaits Chris ratification at S2822 open** |
| Emergent candidates | Phase-0 methodology ratification + execution (sole recommended); Playbook v0.9 (10/10); v0.9-adjacent evidence-first baseline (2 triggers); Colorado / BettingPage / Stock Intelligence available if Chris pivots |
| Session pin | `pa-c884459957614bbd` (retired at S2821 close, force=true, fifty-second consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2822 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2821 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 close-cascade recycle to come |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session) |
| /docs/ restructuring | **ARC CLOSED (S2817).** §8 item #1 discovery-layer FULL: lexical SHIPPED + semantic EVALUATED. Routing-first Phase-0 next. |
| Next move | Chris picks direction at S2822 open — Phase-0 methodology ratification + execution is Chris-ratified architectural direction default; other candidates available |

---

## Recommended session-open protocol (S2822, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2821 handoff §3 + §6 + §7
4. Read S2821 envelope §7 (Phase-0 methodology detailed spec — label schema + gates + two-axis pressure-test)
5. Sanity checks (brew postgres + ledger 114 verify)
6. `git log --oneline -6` — should show S2821 close cascade + S2820 feature+cascade + S2819 chain
7. **Chris D-verdict on Phase-0 methodology proposal** — as-is (default) or revise sections 7.1-7.9
8. Mint fresh pin scoped `s2822-phase0-<subdirection>`
9. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty (all 3 S2821 SIGN cycles verified non-empty; Rigby surfaced 5+ refinements)
10. **STRICT/LOOSE target-set discipline** — Phase-0 corpus rows record both `known_correct_target_strict` and `known_correct_target_loose`
11. **`answer_mode` scoring discipline** — semantic wrong-but-plausible hides in file-match-only metrics; score against IS_DOC/ABOUT_TOPIC/POINTER_DOC
12. Route Phase-0 execution scope through Rigby joint SIGN before authoring corpus
13. **For any implementation-shape work:** OP3 two-SIGN pattern (10/10 across shapes now including IN-LOOP variant)
14. **UPPER BOUND / precision qualifiers** required for count claims
15. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
16. **Anchor-verify at every scope decision point** (19-session trend)
17. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`
18. **DO NOT patch the frozen lexical `top_k` policy** (per Chris directive at S2820 close). If a new discovery-layer failure emerges, that's Phase-0 evidence for routing decision, not lexical bandaid.
19. **DO NOT auto-adopt semantic default flips** (per S2821 non-recommendation). include_superseded=False → True is a defect fix candidate; deferred to Phase-1 gate decision.
20. **DO NOT build RRF or global fusion during Phase 0** (per Chris R#6).

---

## Reference documents

Ordered by frequency of use at S2822:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2821_SEMANTIC_RETRIEVAL_EVAL_ROUTING_PIVOT.md`](docs/handoffs/SESSION_2821_SEMANTIC_RETRIEVAL_EVAL_ROUTING_PIVOT.md) — **S2821 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-18_s2821_semantic_eval_routing_pivot_phase0_proposed.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2821_semantic_eval_routing_pivot_phase0_proposed.md) — **S2821 envelope with §3 evidence + §7 Phase-0 methodology + Chris D-verdict routing-first + Rigby joint SIGN AGREE**
4. [`docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md) — S2820 envelope (predecessor — §5 benchmark corpus origin)
5. [`docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md) — S2819 envelope (§5.1 evidence-first baseline methodology origin)
6. [`docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md) — S2818 envelope (lexical baseline for count queries + benchmark origin)
7. [`core/rag.py`](core/rag.py) — **FROZEN lexical policy** (AUTHORITY_FILE_BONUS + _authority_bonus + _COUNT_INTENT_PATTERNS + _looks_like_count_query + top_k(authority_gate=) + _EXCLUDED_FILE_PATHS)
8. [`core/rag_integration.py`](core/rag_integration.py) — semantic search entry point (search_embeddings function; called by kb_tool.semantic_search action)
9. [`core/services/td_handlers_ops.py:5905`](core/services/td_handlers_ops.py) — kb_tool.semantic_search PA handler (calls rag_integration.search_embeddings)
10. [`core/services/td_handlers_ops.py:6011`](core/services/td_handlers_ops.py) — `search_docs` PA handler (lexical; frozen)
11. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3 §7 C1-C5 pain-point source (STRICT target-set definitions for C1/C2/C3/C4/C5)
12. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 amendment 10/10 corroborated; v0.9-adjacent evidence-first baseline 2/3)
13. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2821 close (unchanged this session)
