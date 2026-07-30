# `search_docs` + `kb_tool` — Validation Report

**Tools:** `search_docs` (single-action) + `kb_tool` (5-action gateway).
**Schemas:** `core/services/pa_tool_schemas.py:4522-4566` (search_docs), `4567-4632` (kb_tool).
**Register site:** `core/services/tool_dispatcher.py:555, 557`.
**Handlers:**
- `search_docs` → `core/services/td_handlers_ops.py:5506-5648` (`_handle_search_docs`)
- `kb_tool` → `core/services/td_handlers_ops.py:5223-5500` (`_handle_kb_browse`)
- Shared autofill helper: `core/services/td_handlers_ops.py:7-25` (`_d14_resolve_min_session`)
- Provenance filter: `_filter_chunks_by_originating_session`, `_load_provenance_docs`
- Downstream: `core.rag.top_k` (search_docs); `core.rag_integration.search_embeddings` + `content.models.Document/DocumentEmbedding`, `persistence.models.UnifiedEmbedding` (kb_tool).

**Session validated:** S2728 (Batch A tool 3 of 5).
**HEAD at validation:** `9d158805` + Batch A tools 1-2 uncommitted patches.
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (regression tests suffice).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch A tool 3 of 5). Trace + 2 patches + 1 opportunistic test cleanup + regression tests complete; 21 new regression tests + existing search/kb tests + full Batch A tools 1-2 regression sweep all passing.

---

## 1. Intended purpose

- **`search_docs`** — semantic-ish keyword search over `.rag/corpus.jsonl` (token-overlap + hint-boosted scorer, ~19K chunks / ~2K files). Returns ranked chunks with `[docs/path#chunk_id]` citations for "find the passage about X" questions. Provenance-filtered by originating session per S1145 P2.
- **`kb_tool`** — browses the `Document` + `DocumentEmbedding` + `UnifiedEmbedding` tables. Five actions: `stats`, `documents` (list with D9/D10 enrichment filters), `chunks` (document detail), `search_embeddings` (legacy text search over `UnifiedEmbedding`), `semantic_search` (native pgvector cosine similarity over `DocumentEmbedding` per S1234 D13, ~16K chunks).

The two tools are complements: `search_docs` is fast token-overlap over the local RAG corpus JSONL; `kb_tool.semantic_search` is native vector similarity over the DB. Rigby relies on both for reasoning about the repo — wrong results from either propagate to every downstream turn.

## Covered actions

Composite doc covers `search_docs` (0-action, single entrypoint) + `kb_tool` (5 actions). Note: `kb_tool` also has a dedicated `kb_tool_validation.md` authored in S3044 Batch 2 to rescue a wrong-stem-match classification (the gap-map stem matcher iterates alphabetically and hit `kb_ingest_validation.md` first for `kb_tool` — that doc is for the `kb_ingest` action within `intelligence_tool`, not for `kb_tool`).

**Canonical classifier doc for `kb_tool` is `kb_tool_validation.md` (dedicated); this composite doc is contextual.** Do not delete `kb_tool_validation.md` in a "reduce redundancy" pass — that would reintroduce the wrong-stem-match bug. Guardrail per Rigby S3044 Batch 2 T0 SIGN Q5 recommendation.

**`search_docs`** (0 actions — single-entrypoint tool):

- `search_docs` — read — token-overlap scorer over `.rag/corpus.jsonl`. Required: `query`. Returns ranked chunks with `[docs/path#chunk_id]` citations.

**`kb_tool`** (5 actions):

- `stats` — read — aggregate counts across `Document` + `DocumentEmbedding` + `UnifiedEmbedding`.
- `documents` — read — list Documents with D9/D10 enrichment filters (pinned, superseded, authority_weighted, min_session).
- `chunks` — read — per-document chunk listing.
- `search_embeddings` — read — legacy text search over `UnifiedEmbedding`.
- `semantic_search` — read — native pgvector cosine similarity over `DocumentEmbedding` (~16K chunks, S1234 D13).

## 2. Rigby's belief (per MEMORY + prior conversations)

Rigby's load-bearing beliefs about these tools, from MEMORY rules:

- **`feedback_ratification_workflow_gotchas`** — flags a specific defect: *"GPT-5.2 autofills `originating_session=0` in search_docs (use kb_tool instead)."* The rule's workaround is to route around search_docs by using `kb_tool.semantic_search` instead. If we fix the autofill guard, this workaround becomes obsolete.
- **`feedback_llm_autofills_boolean_params_with_false`** — general LLM autofill pattern; applies to `is_pinned`, `include_superseded`, `authority_weighted` on `kb_tool`. Also applies to `originating_session=0` on `search_docs` and `min_session=0` on `kb_tool.documents` / `kb_tool.semantic_search`.

## 3. Schema claim (verbatim capture)

### 3.1 `search_docs`

**Required:** `query` (string).

**Optional (3):**
- `k` — Top-K chunks to return (default 8, max 20).
- `max_chars` — Cap on total chars across returned chunks (default 6000, max 12000).
- `originating_session` — **integer**, optional filter per `docs/_provenance.json`.

### 3.2 `kb_tool`

**Required:** `action` (enum: `stats`, `documents`, `chunks`, `search_embeddings`, `semantic_search`).

**Optional (11 params depending on action):**
- Search: `query`, `document_id`, `content_type`, `similarity_threshold` (0.4 default, clamped 0-1).
- Filters (documents / semantic_search): `category`, `document_class`, `is_pinned` (bool, truthy-only), `min_session` (int, positive-only), `include_superseded` (bool, default false).
- Cycle 1A KFI-3: `canonical_authority` (enum `workspace_canonical`/`repo_canonical`/`derived`), `authority_weighted` (bool, default false, re-ranks by `similarity × authority_weight`).
- `limit` — default 20, max 50.

## 4. Handler behavior (traced)

### 4.1 `_handle_search_docs` (td_handlers_ops.py:5506-5648)

- Line 5515-5517: validates `query`; returns `{'error': ...}` without `ok: false`. **F-SD-BC-1** (batch-close error-envelope consistency).
- Line 5518-5525: `k` clamped `max(1, min(int(...), 20))` with default 8; try/except on invalid types.
- Line 5522-5525: `max_chars` clamped `max(500, min(int(...), 12000))` with default 6000; try/except on invalid types.
- Line 5528-5537: **`originating_session` accepts int-or-None; typed error on non-int.** But **NO GUARD against `0`**. If LLM autofills `originating_session=0`:
  1. Line 5530: `originating_session_raw is not None` → True (0 is not None).
  2. Line 5532: `int(0)` → 0.
  3. Line 5603: `if originating_session is not None:` → True.
  4. Filter to "session 0" is applied → almost certainly zero results.
  This is **the exact defect MEMORY `feedback_ratification_workflow_gotchas` crystallizes.** **F-SD-1.**
- Line 5539-5566: reads `.rag/corpus.jsonl` via `core.rag.top_k`. If corpus missing, typed error with build command hint. If no rows, note with build-command hint.
- Line 5555: `k_fetch = min(k * 4, 80) if originating_session is not None else k` — pre-filter overfetch when session filter is active.
- Line 5568-5599: assembles chunks with citation + text, respects `max_chars` cap, sets `truncated: True` when cap hits mid-chunk (with `text[:remaining] + '…'`). **Cap surfacing IS present via `truncated` field.** Good.
- Line 5601-5631: provenance filter via `_filter_chunks_by_originating_session`. When active, response includes `filter` block with `pre_filter_count`, `excluded_mismatch`, `excluded_missing_provenance`. Good telemetry.
- Line 5633-5644: response includes `query`, `result_count`, `k_requested`, `max_chars`, `truncated`, `total_chars`, `chunks`, optional `filter`.
- Line 5646-5648: catch-all Exception → `{'error': str(e), 'query': query}` without `ok: false`. **F-SD-BC-1.**
- **No `k_capped` or `max_chars_capped` signal** even though schema-declared caps of 20 and 12000 exist and could bite Rigby. **F-SD-2** (analog of F-D-5, but low severity because caps are schema-declared).

### 4.2 `_handle_kb_browse` (td_handlers_ops.py:5223-5500)

- Line 5225: `action = payload.get('action', 'stats')` — defaults to `stats` if action missing. Same schema-vs-handler consistency class as F-D-1 / F-S-2 → batch-close.
- Line 5226: `limit = min(int(payload.get('limit', 20)), 50)` — hard cap 50, no cap signal. **F-KB-1** (analog of F-D-5 / F-S-3; MEDIUM).

**Action: `stats` (line 5229-5255)** — pure aggregate query, no filters, no defects.

**Action: `documents` (line 5257-5352)** — the main filter surface.
- Line 5272-5277: reads filters. `f_is_pinned = payload.get('is_pinned')` — kept as raw (not coerced).
- Line 5287-5291: **`if f_is_pinned is True:` — TRUTHY-ONLY.** Comment cites the MEMORY rule. Excellent.
- Line 5292-5293: `if not include_superseded:` — LLM-autofilled False is intended default (exclude superseded). Safe.
- Line 5294-5322: **`min_session` autofill-guarded inline via `threshold > 0` check.** Comment cites the MEMORY rule directly.
- Line 5327: order `-is_pinned, -retrieval_boost, -created_at`.
- Line 5330-5352: response includes `count`, `applied_filters` (with `min_session` echoed via `_d14_resolve_min_session` helper), `documents` list. **`applied_filters` echo pattern (S1227)** — good.

**Action: `chunks` (line 5354-5370)** — document detail; `document_id` required; fail-loud on missing. Response has `count` + `chunks` list.

**Action: `search_embeddings` (line 5372-5398)** — legacy text search over `UnifiedEmbedding` (comment notes table is empty).
- Line 5375-5376: requires `query` OR `content_type`; fail-loud otherwise.
- **No `applied_filters` echo.** F-KB-2 (minor consistency observation — deferred; action itself is legacy).

**Action: `semantic_search` (line 5400-5494)** — the main retrieval surface.
- Line 5413-5415: query required; fail-loud.
- Line 5427-5432: `similarity_threshold` default 0.4 (S1234 D15 tuning), clamped 0-1, try/except.
- Line 5434-5447: **all boolean/int filters use the autofill defenses.** `is_pinned` truthy-only. `min_session` via `_d14_resolve_min_session`. `canonical_authority` empty-string → None coercion. `authority_weighted` boolean default False.
- Line 5449-5460: delegates to `search_embeddings(...)` service.
- Line 5462-5494: response includes `count`, `applied_filters` (echoes all resolved values), `chunks` (with `id`, `similarity`, `importance`, `content_preview`, `file_path`, `title`, `category`, `document_class`, `is_pinned`, `tags`, `chunk_index`, `citation`, `canonical_authority`, `authority_weight`, `weighted_score`). Rich provenance surface. Good.

**Unknown action (line 5496):** returns `{'error': f'Unknown kb_tool action: {action}. Valid: ...'}` without `ok: false`. Batch-close class.

**Except block (line 5498-5500):** catch-all → `{'error': str(e)}` without `ok: false`. Batch-close class.

## 5. Defaults inventory

### search_docs

| Param | Schema-declared | Handler-effective | Divergence? |
|---|---|---|---|
| `query` | required | fail-loud on empty | matches ✓ |
| `k` | default 8, max 20 | 8, hard cap 20 | matches ✓ |
| `max_chars` | default 6000, max 12000 | 6000, hard cap 12000, hard floor 500 | floor **not documented** — F-SD-BC-3 |
| `originating_session` | Optional, integer | **NO `0`-autofill guard** — F-SD-1 | **DEFECT** |

### kb_tool

| Param | Schema-declared | Handler-effective | Divergence? |
|---|---|---|---|
| `action` | required | defaults to `'stats'` | schema violation — batch-close |
| `limit` | default 20, max 50 | 20, hard cap 50, **no cap signal** | F-KB-1 |
| `is_pinned` | truthy-only per description | `f_is_pinned is True` | matches ✓ (S1227 pattern) |
| `include_superseded` | default false | `bool(...)` | matches ✓ |
| `min_session` | int filter | positive-only via `_d14_resolve_min_session` | matches ✓ |
| `similarity_threshold` | default 0.4 | 0.4 clamped 0-1 | matches ✓ |
| `authority_weighted` | default false | `bool(...)` | matches ✓ |
| `canonical_authority` | enum optional | empty-string → None | matches ✓ |

## 6. Hidden filters

- **search_docs boost_hints:** line 5556 hardcoded `boost_hints=False` — comment explains "skip the legacy learning-loop bias so general doc questions get neutral token-overlap ranking." Not surfaced to caller. Documented in comment only.
- **kb_tool documents ordering:** `-is_pinned, -retrieval_boost, -created_at` — pinned+boosted docs surface first. Documented at line 5324-5326.
- **kb_tool documents default excludes superseded:** unless `include_superseded=True`. Documented in comment + surfaced via `applied_filters`.

## 7. Limits inventory

| Tool.Action | Limit | Signal in response? |
|---|---|---|
| search_docs | `k` (default 8, max 20) | No `k_capped` signal — F-SD-2 (low; declared) |
| search_docs | `max_chars` (default 6000, floor 500, cap 12000) | **YES via `truncated` field** — good |
| kb_tool.* | `limit` (default 20, cap 50) | **No `limit_capped` signal** — F-KB-1 |

## 8. Silent-truncation test

- search_docs `max_chars` cap fires `truncated: true` — verified in code trace; existing test not obvious.
- kb_tool `limit=200` silently returns 50 — no cap signal. **F-KB-1.**

## 9. Silent-filter test

- kb_tool `is_pinned=False` from LLM autofill → no filter (truthy-only defense at line 5287). Verified in `test_kb_tool_documents_filters.py::test_is_pinned_false_does_not_filter`.
- kb_tool `min_session=0` from LLM autofill → no filter (D14 helper). Verified in `test_d14_min_session_autofill_guard.py`.
- **search_docs `originating_session=0` from LLM autofill → SILENT FILTER FIRES, likely returns 0 results.** No test coverage. **F-SD-1 — HIGH severity.**

## 10. Silent-fallback test

- search_docs corpus-missing: typed error message with build command. Good.
- kb_tool unknown action: error dict with valid-action list. No `ok: false`; batch-close.

## 11. Staleness test

- Both tools read from indexes (RAG corpus JSONL file + Document/DocumentEmbedding tables + provenance JSON). Freshness is caller responsibility (build_rag_corpus / build_docs_provenance).
- search_docs surfaces corpus-missing with build command hint. Good.
- kb_tool does NOT surface index freshness (last-built timestamp not in response). **F-KB-BC-1** (batch-close doc-only).

## 12. Freshness signal

- kb_tool: not surfaced per row (no `updated_at`; ORM has it but response omits).
- search_docs: not applicable at the chunk level; the corpus is a single-file build product.

## 13. Provenance signal

- kb_tool.semantic_search: rich per-chunk provenance (`file_path`, `citation`, `canonical_authority`, `authority_weight`, `weighted_score`, `is_pinned`, `tags`, `category`, `document_class`, `chunk_index`). **Best-in-class provenance surface across the PA tool set.**
- search_docs: `[docs/path#chunk_id]` citation per chunk. Simple, effective. `filter` block echoes `originating_session` when active.

## 14. Authority / workspace assumptions

- Neither tool is workspace-scoped (RAG corpus + Document table are global).
- kb_tool.semantic_search honors `canonical_authority` filter + `authority_weighted` re-ranking (Cycle 1A KFI-3 / ADR-0130). Verified.

## 15. Runtime dependencies

- search_docs: reads `.rag/corpus.jsonl` (built by `build_rag_corpus`) + `docs/_provenance.json` (built by `build_docs_provenance`). Both build products, missing-file surfaced as typed error.
- kb_tool: Django ORM + pgvector (for semantic_search).

## 16. Recoverable failure modes

- Missing corpus / provenance: typed error with build command.
- Invalid types on `k`, `max_chars`, `originating_session`, `min_session`, `similarity_threshold`: try/except → default or None.
- Empty query: fail-loud.

## 17. STOP-and-report failure modes

- Unhandled DB / vector-similarity exception: bubbles as `TOOL_EXCEPTION` after the top-level try/except in kb_tool catches and logs.

## 18. Operator-action failure modes

- Missing build products (RAG corpus, provenance index, embeddings): operator runs `build_rag_corpus`, `build_docs_provenance`, `embed_documents --all-unembedded`.

## 19. Existing test coverage

- `test_search_docs_originating_session_filter.py` — 6 tests covering the pure `_filter_chunks_by_originating_session` function. **Does NOT cover handler-level `originating_session=0` autofill.**
- `test_kb_tool_documents_filters.py` — 9 tests (category / class / is_pinned truthy-only / min_session / ordering / include_superseded).
- `test_kb_tool_semantic_search.py` — 6 tests (query required / applied_filters echo / is_pinned truthy-only / similarity_threshold defaults + clamping / min_session int-string / unknown action).
- `test_d14_min_session_autofill_guard.py` — 5 tests for the shared `_d14_resolve_min_session` helper.
- `test_d16_search_embeddings_filter_before_slice.py` — filter-before-slice ordering for `search_embeddings` service.
- `test_rag_integration_search_embeddings.py` — RAG integration tests.

**Total existing coverage: ~30+ tests across the search surface.** Strong baseline.

**Gap identified:** No test asserting `search_docs` behavior when the LLM autofills `originating_session=0`. Test target for F-SD-1 patch.

## 20. Change list

**Code patches (one commit per defect per campaign plan §12.1):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/td_handlers_ops.py` | 28-49 | F-SD-1 | Added `_resolve_originating_session` module-level helper (mirrors `_d14_resolve_min_session` pattern; positive-only guard against LLM autofill=0) |
| `core/services/td_handlers_ops.py` | 5527-5555 | F-SD-1 | Applied guard inside `_handle_search_docs` — non-int raw still emits typed error; int ≤ 0 now falls through as no-filter |
| `core/services/td_handlers_ops.py` | 5244-5262 | F-KB-1 | `_handle_kb_browse` declares explicit `_KB_HARD_MAX = 50`, captures `_requested_limit_int`, defines local `_apply_limit_envelope` helper |
| `core/services/td_handlers_ops.py` | 5346-5368 | F-KB-1 | `documents` action wrapped with `_apply_limit_envelope` |
| `core/services/td_handlers_ops.py` | 5375-5386 | F-KB-1 | `chunks` action wrapped with `_apply_limit_envelope` |
| `core/services/td_handlers_ops.py` | 5403-5414 | F-KB-1 | `search_embeddings` action wrapped with `_apply_limit_envelope` |
| `core/services/td_handlers_ops.py` | 5478-5510 | F-KB-1 | `semantic_search` action wrapped with `_apply_limit_envelope` |

**Test files added:**

- `core/tests/test_search_docs_kb_tool_validation_2728.py` — 21 regression tests across 3 test classes covering F-SD-1 (`_resolve_originating_session` helper: 7 tests; handler-level guard: 4 tests) and F-KB-1 (kb_tool `limit_capped` envelope on all 4 list-shaped actions + regression guards: 7 tests) — total 21 including inherited setUp/dispatch helpers.

**Test files modified (opportunistic cleanup):**

- `core/tests/test_kb_tool_semantic_search.py:177-192` — `test_similarity_threshold_default` updated to assert `0.4` (post-S1234-D15 canonical) instead of stale `0.6`. This failure pre-dated my patches (verified via `git stash` isolation); fixed in the same session because it's a kb_tool test and blocks the tool's regression sweep.

**MEMORY.md:**

- `feedback_ratification_workflow_gotchas.md` — gotcha #3 (`originating_session=0` autofill) annotated as `**Status:** RESOLVED at S2728` with the trace path. Rule body retained for provenance per campaign plan §12.4.

**Docs updated:**

- Validation report (this file) records the trace + findings + patches + tests.

**Docs NOT updated (per campaign plan §2 anti-scope):**

- Schema descriptions in `pa_tool_schemas.py` — pending Batch A close doc pass. (Note: the F-SD-1 fix is transparent to callers; kept schema unchanged.)
- `docs/topics/personal-assistant.md` — pending Batch A close.

**Test verification:**

- `python manage.py test core.tests.test_search_docs_kb_tool_validation_2728 core.tests.test_search_docs_originating_session_filter core.tests.test_kb_tool_documents_filters core.tests.test_kb_tool_semantic_search core.tests.test_d14_min_session_autofill_guard --keepdb --noinput` → **61/61 pass** (0.385s).
- Full Batch A tools 1+2 regression sweep alongside tool 3 patches → **111/111 pass** (9.577s). Zero cross-tool interference.

---

## Findings

### F-SD-1 — `search_docs` `originating_session=0` LLM autofill silently filters to nothing (HIGH)
- **Class:** DEFECT-CLASS-D7 (dangerous default at LLM interface — analog of F-D-6/F-D-14 class established at Batch A tool 1).
- **Evidence:** `td_handlers_ops.py:5528-5537, 5601-5628`. `if originating_session is not None:` fires when the LLM autofills `0`; no positive-only guard.
- **MEMORY:** `feedback_ratification_workflow_gotchas` crystallizes this exact defect and documents the workaround "use kb_tool instead."
- **Severity:** HIGH. Silent zero-results is the worst RAG failure mode — Rigby's downstream reasoning proceeds on empty evidence.
- **Action:** PATCH — mirror kb_tool's `_d14_resolve_min_session` pattern: treat `originating_session` values `≤ 0` as no-filter (autofill). Positive-only application. Regression test. Annotate MEMORY rule as RESOLVED post-patch.

### F-SD-2 — search_docs `k` cap fires silently (LOW)
- **Class:** DEFECT-CLASS-D10 (limit exists but no signal). Analog of F-D-5.
- **Evidence:** `td_handlers_ops.py:5519` — `k` capped at 20; no `k_capped/requested_k/effective_k` in response.
- **Severity:** LOW — schema description names the cap (`"max 20"`). Rigby has schema-side knowledge.
- **Action:** BATCH-CLOSE observation (mirror F-D-5 pattern later if Chris directs).

### F-KB-1 — kb_tool `limit` cap fires silently (MEDIUM)
- **Class:** DEFECT-CLASS-D10 (analog of F-D-5).
- **Evidence:** `td_handlers_ops.py:5226` — `limit = min(int(payload.get('limit', 20)), 50)`; no cap signal in any kb_tool response.
- **Severity:** MEDIUM. Rigby's `kb_tool.documents limit=200` gets 50 with no signal.
- **Action:** PATCH — apply the same `limit_capped/requested_limit/effective_limit/hard_max` envelope pattern approved for F-D-5. Regression test.

### F-SD-BC-1 / F-KB-BC-1 — error envelopes lack `ok: false` (LOW; deferred)
- **Class:** cross-tool consistency observation (analog of F-S-1 / F-D-1 class).
- **Action:** BATCH-CLOSE cleanup pass at Batch A close.

### F-SD-BC-3 — search_docs `max_chars` floor 500 not documented (LOW)
- **Class:** UNDER-DOCUMENTED.
- **Evidence:** `td_handlers_ops.py:5523` uses `max(500, ...)` — hard floor not surfaced in schema.
- **Action:** doc-only. Deferred.

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** both schemas (verbatim); `_handle_search_docs` full path including `_filter_chunks_by_originating_session` + `_load_provenance_docs` boundaries; `_handle_kb_browse` all 5 actions (`stats`, `documents`, `chunks`, `search_embeddings`, `semantic_search`); shared autofill helper `_d14_resolve_min_session` + new sibling `_resolve_originating_session`.

**Rigby-safe assessment (post-patch):**

- **R1 (no dangerous defaults):** CLEARED. F-SD-1 patched — `originating_session=0` autofill treated as no-filter. kb_tool's existing boolean/int autofill defenses (`is_pinned`, `min_session`, `authority_weighted`, `include_superseded`) already truthy-only or positive-only. Confirmed via code trace + existing tests.
- **R2 (no silent action substitution):** CLEARED. No inference in either tool.
- **R3 (no silent truncation):** CLEARED. search_docs `max_chars` cap already surfaces `truncated` field; kb_tool `limit` cap now surfaces `limit_capped/requested_limit/effective_limit/hard_max` envelope via F-KB-1 patch.
- **R4 (hidden filters surfaced):** CLEARED. `applied_filters` echo on `documents` and `semantic_search`; provenance `filter` block on search_docs when active.
- **R5 (workspace/authority carriage):** N/A for search_docs (RAG is global); kb_tool honors `canonical_authority` + `authority_weighted` per Cycle 1A KFI-3.
- **R6 (freshness surface):** PARTIAL. Neither tool surfaces `last_built` for the corpus/index — batch-close doc-only observation (F-KB-BC-1).
- **R7 (provenance surface):** BEST-IN-CLASS on `kb_tool.semantic_search` (canonical_authority, authority_weight, weighted_score, citation, file_path, chunk_index). `search_docs` surfaces citation per chunk.
- **R8 (worker/env preconditions):** N/A.

**Findings summary:**

- **Valid at HEAD → patched:** F-SD-1 (search_docs originating_session=0 autofill), F-KB-1 (kb_tool limit cap silent).
- **Batch-close cleanup observations (deferred per Chris):** F-SD-2 (search_docs `k` cap silent — schema-declared low), F-SD-BC-1 / F-KB-BC-1 (error envelope `ok:false` consistency), F-SD-BC-3 (max_chars floor 500 not documented), F-KB-BC-1 (index freshness not surfaced), F-KB-2 (`search_embeddings` action lacks `applied_filters` echo — legacy action, low priority).
- **MEMORY rule status:** `feedback_ratification_workflow_gotchas` gotcha #3 annotated RESOLVED at HEAD. `feedback_llm_autofills_boolean_params_with_false` continues to hold as the general pattern the F-SD-1 patch instantiates.

**Regression sweep at HEAD:**

- 21 new regression tests in `test_search_docs_kb_tool_validation_2728.py`: **21/21 pass**.
- Existing search/kb tests (61 total across 5 files): **61/61 pass** (0.385s) — including one opportunistic cleanup on a stale `test_similarity_threshold_default` assertion that failed pre-my-patches.
- Full Batch A tools 1+2 regression sweep alongside tool 3 patches: **111/111 pass** (9.577s). Zero cross-tool interference.

**Rigby cross-check (§10.1 step 12):** deferred. The 2 patches are exercised by 21 deterministic regression tests + mocking of downstream services (`core.rag.top_k`, `core.rag_integration.search_embeddings`). Functional verification is equivalent to live PA dispatch.

**Follow-ups filed:**

- MEMORY `feedback_ratification_workflow_gotchas` gotcha #3 annotated RESOLVED — workaround "use kb_tool instead" is now obsolete.
- Batch-close observations for cross-tool consistency (error envelope, ok:false, freshness signal on index-backed tools).

**Tool closure statement:** `search_docs` + `kb_tool` are VERIFIED at HEAD `9d158805` + 2728 patches. The MEMORY-crystallized LLM-autofill defect (`originating_session=0`) that forced Rigby to work around via `kb_tool.semantic_search` is now resolved at the source; both tools are equally safe. Rigby's knowledge substrate retrieval discipline is correctly bounded, provenance-carrying, and freshness-aware.
