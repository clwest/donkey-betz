# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2820 CLOSED (afternoon close 2026-07-18; picks up as S2821) — **LEXICAL PILOT CHAIN FEATURE COMPLETE**

**Refreshed 2026-07-18 afternoon (SESSION 2820 CLOSED — third same-day pilot in discovery-layer chain S2818 → S2819 → S2820. Orientation-doc exclusion for `00-START-NEXT-SESSION.md`. Feature PR #3257 (`93aed786f`, +412 LOC across 3 files). **Chris ratified 4 things in one directive: (1) approve S2820, (2) FREEZE lexical policy, (3) declare lexical pilot FEATURE COMPLETE, (4) pivot S2821+ to semantic retrieval evaluation against the accidentally-built benchmark corpus.** SIXTY-FIFTH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** First "feature complete" declaration for a pilot chain; first IN-LOOP OP3 variant (Rigby continuously in-loop, no separate post-authoring turn); second trigger for potential Playbook v0.9-adjacent amendment on evidence-first baseline capture.**

**S2820 ship (1 feature PR + 1 close cascade PR, both merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Orientation-doc exclusion + lexical-pilot feature-complete | **#3257** · `93aed786f` | main | `core/rag.py` (mod), `core/tests/test_rag_orientation_doc_exclusion_2820.py` (new), `docs/research/implementation/RATIFICATION_2026-07-18_s2820_...md` (new envelope) |
| Close cascade | **#TBD** · (SHA at merge) | main | handoff + start-here + pin rotation + docs pipeline |

**Handoff:** `docs/handoffs/SESSION_2820_ORIENTATION_DOC_EXCLUSION_LEXICAL_FEATURE_COMPLETE.md`
**Envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md` (frozen at merge per PLAYBOOK-6.10.9)
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 114 rows unchanged (folds deferred per S2818/S2819 pattern; ledger persistence occurs at arc close, not per-pilot close).

**Arc state at S2820 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817). §8 item #1 lexical execution: SHIPPED across S2818 (unconditional boost) + S2819 (Shape C gate) + S2820 (orientation exclusion). **Lexical pilot chain FEATURE COMPLETE per Chris directive.** No more lexical patches in this substrate.
- **Discovery-layer arc:** lexical branch complete; **semantic branch opens at S2821**.

---

## S2821 CANDIDATES — SOLE RECOMMENDED DIRECTION

### ⭐ Chris-ratified pivot directive from S2820 close

1. **⭐ Semantic retrieval evaluation against the benchmark corpus** (SOLE recommended direction). Per Chris D-verdict: "Spend the next engineering cycle evaluating semantic retrieval against the benchmark corpus you've accidentally built during the docs audit." Concrete first steps (per S2820 envelope §7):
   - **Enumerate candidate mechanisms:** `kb_tool.semantic_search` already exists (production PA / Rigby retrieval against `unified_embeddings` pgvector table — NOT currently used by the `search_docs` PA tool handler); alternative embedding models (OpenAI text-embedding-3, e5, bge); hybrid lexical + semantic reranker.
   - **Benchmark corpus:** 13+ queries with known-correct labels codified in S2820 envelope §5 — Q1 counts (spiders/agents/models/celery) → PLATFORM_INVENTORY.md; Q5 non-counts "add spider" → AGENTS_REFERENCE.md#35; Q6 "list all spiders" → PLATFORM_INVENTORY.md; Q7 "Group 2700 T1 audit" → SESSION_2801/2811 handoffs; Q8 self-ref → CLAUDE.md pointer; plus T3 §7 C1-C5.
   - **Evaluation harness:** per-mechanism success@3 + rank of known-correct target + regression check on lexical wins.
   - **Route findings to Chris** for S2822+ migration decision.
   - **Non-goals:** no more lexical patches (frozen); not a full migration (S2821 is EVALUATION); benchmark corpus fixed (extending it requires separate SIGN).

### Available if Chris pivots away from semantic evaluation

- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability
- **Stock Intelligence** — end-to-end verify (dashboard/brief/alert pipeline)
- **Playbook v0.9 amendment (OP3 codification)** — 10/10 triggers now including IN-LOOP variant + INITIAL-ESCALATE→RE-VERDICT-SHIP variant. Well past codification threshold.
- **Playbook v0.9-adjacent amendment (evidence-first baseline capture)** — 2 triggers (S2819 §5.1 surfacing + S2820 compliance). Wait for third trigger before codification per §20 two-triggers rule.
- **Remaining 2799 §8 queue** (items #4-#8): T5 clause update, file moves, per-handoff citation_health, retrieval-frequency telemetry, generator/automation coordination.
- **LegalDocument.generation_context** blank=True (Phase 2 model quirk)
- **GPT fallback for form-selection** on low-confidence

**Recommended default:** Item #1 semantic retrieval evaluation. Chris explicitly named this as the next engineering cycle direction with clear scope + non-goals. The pivot rationale (diminishing ROI on lexical patches — Rigby's S2820 Q4 architectural-inflection observation) is empirically corroborated by the 3-arc pilot chain. The pivot substrate (`kb_tool.semantic_search` / embedding retrieval) already exists in the platform.

---

## SESSION PIN — S2820 RETIRED (fresh mint required at S2821 open)

**Pin history (S2820):**

- `pa-a0dd969db550488d` (label `s2820-00start-contamination-fix`) minted at S2820 open; **retired at S2820 close (`force=true`, fifty-first consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2821 first-action fresh mint.

**S2821 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2820 handoff — §3 (novel-precedent — first feature-complete + first IN-LOOP OP3 variant + first evidence-first baseline compliance), §6 (S2821 direction), §7 (lessons)
# If continuing semantic retrieval evaluation (default):
#   - Read S2820 envelope §5 (benchmark corpus definition — 13+ labeled queries) + §7 (S2821 concrete first steps)
#   - Read core/rag_integration or wherever kb_tool.semantic_search lives (production PA retrieval path uses it)
#   - Read core/services/td_handlers_ops.py:6011 (search_docs handler — the migration target)

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

python manage.py session_lifecycle open --label s2821-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2820 lessons to carry:**

1. **The lexical top_k ranker is FROZEN policy.** S2818 + S2819 + S2820 = complete. Any new discovery-layer improvement lives in a different substrate. If S2821+ encounters a new discovery-layer failure mode, resist the urge to patch the frozen substrate — the pivot is semantic retrieval.
2. **Evidence-first baseline capture (S2819 §5.1 methodology) works.** Applied S2820, worked exactly as expected — 4/4 PASS on empirically-grounded criteria. Second trigger for potential Playbook v0.9-adjacent amendment; watch for third to cross §20 codification threshold.
3. **In-loop OP3 variant is valid for narrow pilots where the whole cycle happens in one conversation.** Preserves error-catching value without separate post-authoring dispatch. Not a general replacement — reserve for narrow-scope + tool-grounded-throughout situations.
4. **The pilot chain built a benchmark corpus as side effect.** Chris named it "accidentally built"; S2820 §5 codifies 13+ labeled queries. **Any future retrieval-substrate work has a ready-to-use evaluation harness.**
5. **"Feature complete" is a valid arc-close pattern.** Not every substrate closes via arc canonical summary or refactor completion. Some substrates close via "we've done what we can with this tool; time to switch tools." Chris's 4-verdict D-response formalizes this shape.
6. **Focused-pilot-chain arc shape** (as opposed to audit-style research arc or platform-refactor) is a novel arc-shape worth naming for future methodology reference. Three direct-continuation pilots, each addressing an empirically-observed failure from the previous, all shipping same day. Fits when the substrate is fresh + scope narrows naturally.

---

## Twin-pointer card

📁 **Repo — S2820 artifacts:**

- **Feature PR (1, merged):** #3257 (Orientation-doc exclusion + lexical-pilot feature-complete · `93aed786f`)
- **Close cascade PR:** #TBD (SHA at merge)
- **Substrate changes:** `core/rag.py` (mod, +`_EXCLUDED_FILE_PATHS`), `core/tests/test_rag_orientation_doc_exclusion_2820.py` (new, 5 tests), `docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md` (new envelope + §5 benchmark corpus)
- **Handoff:** `docs/handoffs/SESSION_2820_ORIENTATION_DOC_EXCLUSION_LEXICAL_FEATURE_COMPLETE.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session; folds noted in envelope §5)
- **Merge SHA:** `93aed786f` (feature) → close-cascade SHA filled at merge
- **All 3 pilot envelopes now live at:** `docs/research/implementation/RATIFICATION_2026-07-18_s2818_...md` + `s2819_shape_c_intent_gating.md` + `s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md`

🖥️ **Workspace UI — S2820 has NO twin-pointer workspace deliverable this session** — pilots keep envelopes in `docs/research/implementation/` as authoritative; workspace mirror deferred per S2818/S2819 pattern. Group 2700 arc's workspace deliverable (`37d6ca76-89c3-4966-8f4c-decc52ce8169`) remains authoritative for the /docs/ restructuring arc under which S2818/S2819/S2820 are §8 executions.

---

## Current repository state (S2820 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2820 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment 10/10 corroborated including IN-LOOP + INITIAL-ESCALATE→RE-VERDICT-SHIP variants**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | **ARC CLOSED (S2817).** §8 item #1 SHIPPED across 3-pilot chain S2818/S2819/S2820. **LEXICAL PILOT FEATURE COMPLETE** per Chris directive. |
| **Discovery-layer arc state** | **Lexical branch COMPLETE.** Semantic branch pivot at S2821 per Chris directive. |
| Emergent candidates | Semantic retrieval evaluation (sole recommended); Playbook v0.9 (10/10); v0.9-adjacent evidence-first baseline (2 triggers); Colorado / BettingPage / Stock Intelligence available if Chris pivots |
| Session pin | `pa-a0dd969db550488d` (retired at S2820 close, force=true, fifty-first consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2821 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2820 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 in-session recycle + 1 post-merge + 1 close-cascade recycle to come |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session; folds tracked in envelope §5) |
| /docs/ restructuring | **ARC CLOSED (S2817).** §8 item #1 CLOSED across S2818+S2819+S2820. Discovery-layer lexical branch FEATURE COMPLETE. |
| Next move | Chris picks direction at S2821 open — semantic retrieval evaluation is Chris-ratified default; other candidates available |

---

## Recommended session-open protocol (S2821, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2820 handoff §3 + §6 + §7
4. **If continuing semantic retrieval evaluation (default):**
   - Read S2820 envelope §5 (benchmark corpus — 13+ labeled queries) + §7 (concrete first steps)
   - Read `core/rag_integration.py` (or equivalent) — where `kb_tool.semantic_search` lives against `unified_embeddings` pgvector
   - Read `core/services/td_handlers_ops.py:6011` — the `search_docs` PA tool handler that would be the eventual migration target (only after S2822+ decision)
5. Sanity checks (brew postgres + ledger 114 verify)
6. `git log --oneline -6` — should show S2820 feature + cascade + S2819 + S2818 chain
7. **Chris picks direction** — semantic retrieval evaluation is default; can override to Colorado / BettingPage / Stock Intelligence / Playbook amendments
8. Mint fresh pin scoped `s2821-<Chris's-direction>`
9. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
10. **BASELINE CAPTURE DISCIPLINE (S2819 §5.1 lesson; S2820 §3.1 empirical compliance):** for any pilot with named success criteria, include FULL top-K + per-named-target presence check BEFORE locking criteria
11. Route scope through Rigby joint SIGN before authoring
12. **For any implementation-shape work:** OP3 two-SIGN pattern (10/10 across shapes now including IN-LOOP variant + INITIAL-ESCALATE→RE-VERDICT-SHIP variant)
13. **UPPER BOUND / precision qualifiers** required for count claims
14. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
15. **Anchor-verify at every scope decision point** (18-session trend)
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`
17. **DO NOT patch the frozen lexical `top_k` policy** (per Chris directive at S2820 close). If a new discovery-layer failure emerges in semantic-evaluation work, that's evidence for the semantic pivot, not for another lexical bandaid.

---

## Reference documents

Ordered by frequency of use at S2821:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2820_ORIENTATION_DOC_EXCLUSION_LEXICAL_FEATURE_COMPLETE.md`](docs/handoffs/SESSION_2820_ORIENTATION_DOC_EXCLUSION_LEXICAL_FEATURE_COMPLETE.md) — **S2820 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md) — **S2820 envelope with §5 benchmark corpus + §4.3 Chris directive + §7 S2821 direction**
4. [`docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md) — S2819 envelope (predecessor 2 — §5.1 methodology gotcha origin)
5. [`docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md) — S2818 envelope (predecessor 1 — chain origin)
6. [`core/rag.py`](core/rag.py) — **FROZEN lexical policy** landing (`AUTHORITY_FILE_BONUS` + `_authority_bonus` + `_COUNT_INTENT_PATTERNS` + `_looks_like_count_query` + `top_k(authority_gate=)` + `_EXCLUDED_FILE_PATHS`)
7. [`core/services/td_handlers_ops.py:6011`](core/services/td_handlers_ops.py) — `search_docs` PA handler (S2821 evaluation target for semantic-vs-lexical migration)
8. [`docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`](docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md) — Group 2700 arc-close deliverable; §8 authorized the 3-arc chain
9. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3 C5+C2 pain source (lexical arc fixed both classes)
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 amendment 10/10 corroborated; v0.9-adjacent evidence-first baseline 2/3)
11. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2820 close (unchanged this session)
