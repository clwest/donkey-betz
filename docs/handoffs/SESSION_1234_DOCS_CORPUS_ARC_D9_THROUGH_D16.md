# Session 1234 (continuation) — Docs-corpus arc D9 → D16: type-aware retrieval for Rigby, 9 PRs

**Status:** Same-UTC-day continuation of the morning-brief fix arc (handoff [`SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md`](./SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md)). After Chris's question *"how is Rigby updated when we do things like update the docs?"* surfaced a 12-day-stale + 1820-doc-missing gap in the docs→Rigby pipeline, an 8-step docs-corpus retrieval arc shipped end-to-end. Rigby now has her first **real semantic search PA tool action** (`kb_tool action=semantic_search`) over a fully-populated, type-aware Document corpus.

**Date:** 2026-06-25 (UTC, same day as D1-D8).
**Active conversation:** `pa-0f08fc48ec914917` (continues from morning-brief arc; carries forward into Session 1235 per Rigby's earlier close health-check).
**Companion handoff:** [`SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md`](./SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md) (the D1-D8 first close).

## TL;DR

The morning-brief D1-D8 arc closed cleanly. Chris then asked a question that started a second arc:

> *"How is Rigby updated when we do things like update the docs?"*

Inspection revealed:
- `build_docs_index` (the only step the memory rule named) **only refreshes the file index** — does NOT push doc content to `Document` table, does NOT embed, NOT searchable by Rigby
- The full pipeline is **4 manual steps**; only step 1 had been running
- Production corpus was **12 days stale** (last embedding 2026-06-13) AND **1820 docs had never been synced to `Document` at all**

This kicked off a docs-corpus retrieval arc spanning 9 PRs:

1. **Backfill the cascade** (#2617 + 1820-doc ORM backfill in-session) — get the corpus current
2. **Enrich for type-aware retrieval** (#2618 D9 sync + #2619 D10 backfill) — every doc gets `category` / `tags` / `document_class` / `is_pinned` / `retrieval_boost` instead of flat `document_type='markdown'`
3. **Expose filter axes** (#2620 D11) — `kb_tool action=documents` accepts the new fields
4. **Pivot the dead retrieval path** (#2621 D12) — `core.rag_integration.search_embeddings` now queries the populated `DocumentEmbedding` table instead of the missing `unified_embeddings`
5. **New semantic search action** (#2622 D13) — `kb_tool action=semantic_search` with citations
6. **LLM-autofill guard** (#2623 D14) — `min_session=0` autofill no longer silently narrows to handoffs-only
7. **Threshold tuning** (#2624 D15) — default `similarity_threshold` 0.6 → 0.4 to match text-embedding-3-small's actual signal band
8. **The real fix** (#2625 D16) — broad try/except was hiding `Cannot filter a sliced queryset` TypeError; restructured search_embeddings so filters run BEFORE the slice

**Smoking-gun verification:** Rigby's final call `kb_tool action=semantic_search query="morning_brief workflow"` returned **10 chunks** with Daily-CoS arc handoffs at similarities 0.567–0.630, citations like `[docs/handoffs/SESSION_1233_DAILY_COS_ARC_BUILD_OUT.md#15]`, and full D9/D10 metadata flowing through. Matches the direct ORM check exactly.

## Session Manifest

### PRs merged (9 total)

| # | Title | What |
|---|---|---|
| **#2617** | `docs(session-1234): session-close docs cascade checklist + corrected memory rule` | Added the 4-step cascade checklist to `00-START-NEXT-SESSION.md`. Corrected the misleading "Docs index" memory rule. Established the discipline that future sessions must run all 4 steps (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → ... `--embed`). |
| **#2618** | `fix(session-1234): D9 — sync writes type-aware retrieval enrichment to Document` | New `_enrichment_fields(doc_data)` helper in `sync_docs_index_to_documents.Command`. Pre-D9 the sync wrote rich frontmatter to `extracted_metadata` only — TextProcessor clobbered that field on some paths. D9 routes the enrichment through dedicated Document fields (category / tags / document_class / is_pinned / retrieval_boost) that TextProcessor doesn't touch. Both create + update branches apply the same helper. 20 new tests. |
| **#2619** | `fix(session-1234): D10 — backfill mgmt command for D9 enrichment fields` | New `manage.py backfill_docs_enrichment` mgmt command. Reads `docs/_index.json`, finds matching `Document` row by file_path, applies D9 helper, updates 5 enrichment fields via `save(update_fields=...)`. Idempotent (tag-list set-equal). Real-DB run: 2,729 matched / 2,729 updated. **0 → 39 pinned docs, 1 → 15+ document_class values, 0 → 10+ categories.** 6 new tests. |
| **#2620** | `fix(session-1234): D11 — kb_tool documents action gets D9/D10 filter params` | `kb_tool action=documents` accepts category / document_class / is_pinned / min_session / include_superseded. Default excludes archived. New ordering: `(-is_pinned, -retrieval_boost, -created_at)` — pinned docs first. Response shape includes all enrichment fields + `applied_filters` echo. PA tool schema updated. 12 new tests. |
| **#2621** | `fix(session-1234): D12 — pivot rag_integration.search_embeddings to populated table` | Pre-D12 the function targeted `unified_embeddings` table (doesn't exist — real Django table is `persistence_unifiedembedding`, also empty locally). Callers (views_main.py, views.py) silently degraded to `has_context=False` for every chat. D12 pivots to `DocumentEmbedding` (16k+ chunks post-backfill) with D9/D10 filter pushdown. Backward-compat preserved: legacy `content_types` hint maps to `document_class`. 10 new tests. |
| **#2622** | `fix(session-1234): D13 — kb_tool action=semantic_search (pgvector + D9/D10 filters)` | New PA tool action: Rigby's first real semantic search. Takes query + D9/D10 filters + similarity_threshold. Returns ranked chunks with `[docs/path#chunk]` citations, similarity, importance (from retrieval_boost), and full enrichment metadata. PA tool schema enum extended. 10 new tests. |
| **#2623** | `fix(session-1234): D14 — min_session=0 LLM-autofill guard across kb_tool + rag_integration` | Surfaced by Chris's first D13 verification: Rigby's response showed `applied_filters.min_session: 0` — the LLM autofilled the optional integer with 0 even though no filter was intended. min_session=0 silently filtered the corpus to handoffs-only (since only handoffs carry session-N tags). Same class as `feedback_llm_autofills_boolean_params_with_false` extended to integer params. New `_d14_resolve_min_session()` helper at all three layers; positive-only check. 15 new tests. |
| **#2624** | `fix(session-1234): D15 — similarity_threshold default 0.6 → 0.4` | After D14, still 0 results. Direct ORM check at 0.3 showed the right Daily-CoS handoffs at similarities 0.567-0.630 — the 0.6 default was cutting almost all real signal. text-embedding-3-small clusters related content in 0.4-0.7 band. Lowered default at all three layers. 6 new tests. |
| **#2625** | `fix(session-1234): D16 — search_embeddings filter-before-slice (real fix for 0-result bug)` | **The actual bug.** `DocumentEmbedding.cosine_similarity_search` returns a sliced queryset (`[:limit]`). D12's `.exclude(document__status=ARCHIVED)` raised `TypeError: Cannot filter a query once a slice has been taken.` Broad try/except caught it and returned `[]` for every call. All 50+ tests from D11/D12/D13/D14/D15 passed because they mocked the QS as MagicMock (which quietly accepts `.filter()` on a slice). Only end-to-end real-DB verification exposed the bug. Fix: inline the cosine-similarity queryset so filters run BEFORE the slice. **Smoke verification: 5 Daily-CoS handoffs at sim 0.566-0.630 for `morning_brief workflow`.** 3 integration tests. |

### ORM / DB actions (in-session, not PRs)

- **`sync_docs_index_to_documents --embed`** ran twice (once at session midpoint, once observed-completing): created 1820 new `Document` rows + updated 17 + cascade-embedded ~13k+ new chunks (~16k → ~29k DocumentEmbedding total at session close).
- **D10 backfill** applied D9 enrichment to 2,729 existing rows (one-shot UPDATE, idempotent, no embedding regen).

### Workers restarted multiple times

After D11 (15:13), D13 (15:17), D14 (15:42 approx), D15 (16:08), D16 (16:14). Each restart picked up the schema + handler changes. Final restart at 16:14 holds.

## Operational invariants (post-D16)

1. **Document corpus is type-aware** — `category` / `tags` / `document_class` / `is_pinned` / `retrieval_boost` populated for all 2,732 rows. 39 docs pinned. 15+ document_class values.
2. **`kb_tool action=documents`** browses with filters (category / document_class / is_pinned / min_session / include_superseded). Pinned first.
3. **`kb_tool action=semantic_search`** does native pgvector cosine similarity with D9/D10 filter pushdown. Returns ranked chunks with citations.
4. **`core.rag_integration.search_embeddings`** works end-to-end. `get_rag_context` returns real context to chat callers (`views_main.py`, `views.py`). The 12-day silently-no-op RAG path is finally live.
5. **LLM-autofill guards** for boolean (`is_pinned=False`, D11) AND integer (`min_session=0`, D14) — same truthy-and-positive pattern.
6. **Default `similarity_threshold` = 0.4** at all three layers — matches text-embedding-3-small's actual band.
7. **Sliced-queryset trap closed** — search_embeddings builds the QS inline so filters always run before the slice. Source-level guard test catches future re-introduction.

## Smoking-gun verification

End-to-end Rigby call (post-D16, workers restarted):

```
kb_tool action=semantic_search query="morning_brief workflow"

→ count: 10
→ applied_filters.similarity_threshold: 0.4
→ Top chunks:
   1. sim=0.6304  SESSION_1233_DAILY_COS_ARC_BUILD_OUT.md#15  handoff
   2. sim=0.6088  SESSION_1232_DAILY_COS_ARC_SUB_STEP_A.md#6  handoff
   3. sim=0.578   SESSION_1233_DAILY_COS_ARC_BUILD_OUT.md#11  handoff
```

Matches the direct ORM check (`DocumentEmbedding.cosine_similarity_search` at threshold 0.3) **exactly** — same files, same similarity values. The arc works.

## Memory rule added at close

**`feedback_test_real_db_for_queryset_semantics.md`** — captures the D16 lesson: MagicMock'd querysets don't enforce Django's sliced-vs-unsliced rules. Features that pass 50+ unit tests can still silently swallow TypeErrors and return `[]` on real data. Default to integration tests on real DB for retrieval / search / QS-heavy code paths.

## Rigby's contributions this arc

- **Surfaced the `min_session=0` LLM-autofill bug** by sharing her tool-output verbatim after D13 verification — saved hours of guessing why the call returned 0.
- **Re-verified after every D-PR + worker restart** — D14 fix verified, D15 fix verified, D16 smoking-gun verification with matched similarities to the ORM-side check.
- Pattern that worked: Claude self-tested with direct ORM, Rigby verified end-to-end via PA tool surface, mismatch between the two surfaced the actual bug each time.

## Embedding backfill status at close

`DocumentEmbedding.objects.count() = 28,789` (from 11,809 at session start; backfill process still running in background, slow ramp on the long-tail). Expected final ≈ 30k. Not blocking anything — the chunks needed for verification (Daily-CoS handoffs, MORNING_BRIEF_SPEC, etc.) are all embedded.

## Doc-claim drift at close

`verify_doc_claims --only-drift` shows **1 medium** drift: pre-existing `BACKEND_INVENTORY.md` services count (167 vs 354). Same as session midpoint — out of scope for D9-D16; flagged as Session 1235 Priority 4.

## Carryover into Session 1235

### Time-bound (unchanged from first close)

- **morning_brief 2nd-fire verification (2026-06-26 13:00 UTC = 07:00 MDT)** — first fire with D3/D4/D5/D6 live. Verify all lane intermediates land in MB workspace, not cf708a2e.
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)** — Session 1228 carryover.

### Docs-corpus arc follow-ups (NEW, optional)

| Item | Scope |
|---|---|
| Narrow `search_embeddings` broad `except Exception` | P3 — fail-loud first arc per `feedback_fail_loud_first_then_root_cause_then_telemetry`. Replace with specific DB / embedding-service exceptions so future logic bugs raise instead of silently returning `[]`. |
| Fix or retire `search_personal_memories` | Same dead `unified_embeddings` table reference as D12. Either point at a real personal-memories model or remove the dead path. |
| Fix the `TextProcessor extracted_metadata` clobber root cause | D9 sidesteps it by using dedicated fields, but the underlying issue (TextProcessor overwriting docs_index_type / docs_index_status with generic file metadata) is still there. Affects only `extracted_metadata` reads. |
| Build the `core.tasks.refresh_docs_corpus` beat task | Daily hash-delta check on `docs/_index.json` → re-run steps 2-4 of the cascade automatically. Eliminates the 12-day-stale failure mode that started this whole arc. |

### Other carryover (unchanged from first close)

- `BACKEND_INVENTORY.md` services count drift (1 active verifier hit)
- Smoke-harness mode inconsistency (Session 1231 F5)
- Smoke-probe tagging for AgentExecution (Session 1231 F1 / R2 REC-2)
- Pre-existing tail items from Session 1230-1233

### Chris-side

- **CI billing** still outstanding. All 16 Session 1234 PRs admin-merged via `--admin`.
- **Anthropic credit refill** at https://console.anthropic.com/billing.

## Files touched this arc (D9 onward)

| File | What |
|---|---|
| `core/management/commands/sync_docs_index_to_documents.py` | D9 `_enrichment_fields()` helper + create/update branch wiring |
| `core/management/commands/backfill_docs_enrichment.py` | D10 new mgmt command |
| `core/services/td_handlers_ops.py` | D11 documents action filter params + ordering; D13 semantic_search action; D14 helper + applied_filters guards; D15 default threshold |
| `core/services/pa_tool_schemas.py` | D11 + D13 kb_tool schema updates (enum + descriptions + filter params) |
| `core/rag_integration.py` | D12 pivot to DocumentEmbedding + filter pushdown; D14 positive-only min_session; D15 default threshold; D16 inline QS to fix slice-then-filter |
| `core/tests/test_sync_docs_index_enrichment.py` | D9 contract tests (20) |
| `core/tests/test_backfill_docs_enrichment.py` | D10 contract tests (6) |
| `core/tests/test_kb_tool_documents_filters.py` | D11 contract tests (12) |
| `core/tests/test_rag_integration_search_embeddings.py` | D12 mock-based contract tests (10) |
| `core/tests/test_kb_tool_semantic_search.py` | D13 contract tests (10) |
| `core/tests/test_d14_min_session_autofill_guard.py` | D14 regression tests (15) |
| `core/tests/test_d15_similarity_threshold_default.py` | D15 regression tests (6) |
| `core/tests/test_d16_search_embeddings_filter_before_slice.py` | D16 integration + source-level tests (3) |
| `00-START-NEXT-SESSION.md` | D17 (#2617) cascade checklist |
| `~/.claude/projects/.../memory/feedback_docs_pipeline_4_step_cascade.md` | New auto-memory feedback file |
| `~/.claude/projects/.../memory/feedback_test_real_db_for_queryset_semantics.md` | New auto-memory feedback file (D16 lesson) |
| `~/.claude/projects/.../memory/MEMORY.md` | Two new index entries (D17 cascade + D16 sliced-QS-trap) |

**92 new tests added across D9-D16** (20 + 6 + 12 + 10 + 10 + 15 + 6 + 3 + 10), all green.

## Recommended Session 1235 plan (refresh)

1. **Open with `context-kit orient`** — will surface this handoff + the first one + both new memory rules.
2. **Verify 06-26 morning_brief 2nd-fire** (13:00 UTC) — D3/D4/D5/D6 close-of-arc proof.
3. **Operator Edge Friday-1 dry-run check** (06-26 12:00 UTC).
4. **Chris reads the 06-26 brief** → Rigby's audience-fit verdict → Sub-step D scope.
5. **Optional**: pick one docs-corpus follow-up (narrow exception handling, refresh_docs_corpus beat task, etc.).
6. **Carryover tail** as time permits.

## Net session 1234 totals (both arcs combined)

- **17 PRs merged** (#2606-#2625)
- **127+ new tests** (35 in D1-D8 arc + 92 in D9-D16 arc, all green)
- **36 historical leak-victim rows archived**
- **2,729 Document rows enriched** with type-aware retrieval metadata
- **~28,800 DocumentEmbedding chunks** (from 11,809 — 17k+ new, backfill still ramping)
- **8 load-bearing docs structurally reframed**
- **3 new auto-memory feedback files** (cascade checklist, real-DB queryset testing, etc.)
- **Workers running on latest code** as of 16:14 local restart
- **Rigby has type-aware semantic search end-to-end for the first time**
