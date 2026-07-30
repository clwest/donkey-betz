# `kb_tool` — Validation Report (S3044 Batch 2)

**Tool:** `kb_tool`
**Schema:** `core/services/pa_tool_schemas.py:4567` (5 actions: `stats`, `documents`, `chunks`, `search_embeddings`, `semantic_search`)
**Handler:** `core/services/td_handlers_ops.py:5223` (`_handle_kb_browse`)
**Register site:** `core/services/tool_dispatcher.py:557`
**Session:** S3044 Batch 2 (Path B systematic sweep FINISH — 2nd wrong-stem-match rescue after `workspace_tool` in Batch 1)
**HEAD at validation:** `17dd03f56` (2026-07-30)
**Ship shape:** Doc-only (S2796 shape). Dedicated doc supersedes prior wrong-stem match to `kb_ingest_validation.md` (which covers the `kb_ingest` action within `intelligence_tool`, not `kb_tool`).
**Category upgrade target:** `validated_doc_exists_unknown` (via wrong stem match) → `validated_full`
**Rigby SIGN:** S3044 Batch 2 T0 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** dry_run_supported

---

## 1. Purpose / when-to-use

Browse the platform's knowledge-base backing store: `Document` + `DocumentEmbedding` (pgvector, ~16K chunks per S1234 D13) + `UnifiedEmbedding` (legacy text search). Read-only gateway; complements `search_docs` (which searches the local `.rag/corpus.jsonl` file rather than the DB).

Use `kb_tool.semantic_search` when the caller needs native pgvector cosine similarity over the DB (canonical semantic search since S1234 D13). Use `kb_tool.documents` when the caller needs a filtered Document list (D9/D10 enrichment filters: pinned, superseded, authority_weighted, min_session). Use `kb_tool.stats` for dashboard aggregates.

Distinct from:
- `search_docs` — local RAG JSONL scorer; complementary. Both tools documented jointly in `search_docs_kb_tool_validation.md` (composite doc from S2728).
- `kb_ingest` — this is an ACTION within `intelligence_tool` (write side of the KB), not a separate tool. Documented in `kb_ingest_validation.md`.
- `intelligence_tool` — the parent gateway that owns `kb_ingest` + related actions.

## Covered actions

All 5 schema actions covered:

- `stats` — read — aggregate counts across `Document` + `DocumentEmbedding` + `UnifiedEmbedding` tables.
- `documents` — read — list Documents with D9/D10 enrichment filters (`is_pinned`, `include_superseded`, `authority_weighted`, `min_session`). Supports pagination.
- `chunks` — read — per-document chunk listing (`document_id` required). Returns ordered chunks + embedding metadata.
- `search_embeddings` — read — legacy text search over `UnifiedEmbedding`. Predates pgvector migration; still supported for backwards compat.
- `semantic_search` — read — native pgvector cosine similarity over `DocumentEmbedding`. Canonical semantic search since S1234 D13 (~16K chunks). Rigby's primary "find similar content" surface.

## 3. Schema notes

- **Required:** `action` (enum: 5 values above).
- **Conditional required (handler-enforced):**
  - `document_id` for `chunks` — fail-loud when missing.
  - `query` for `search_embeddings` + `semantic_search` — fail-loud when missing.
- **Optional (documents/semantic_search):** `is_pinned` (bool), `include_superseded` (bool), `authority_weighted` (bool), `min_session` (int — S1145 P2 provenance filter).
- **Optional (pagination):** `limit`, `offset`.
- **LLM autofill hazard (per MEMORY `feedback_llm_autofills_boolean_params_with_false`):** boolean params (`is_pinned`, `include_superseded`, `authority_weighted`) may be autofilled as `False` even when caller intended default `True` or omission. Recommendation: caller passes explicit values when intent is not the default.

## 4. Golden-path examples

**"KB dashboard:"**

```
kb_tool  action=stats
```

**"Find documents about X (semantic):"**

```
kb_tool  action=semantic_search  query="agent capability drift"  limit=10
```

**"List recently-added Documents (D9-filtered):"**

```
kb_tool  action=documents  is_pinned=false  include_superseded=false  min_session=3000  limit=25
```

**"Read chunks for a specific document:"**

```
kb_tool  action=chunks  document_id=<uuid>
```

## 5. Failure / empty-state / pagination notes

- **Missing `document_id` on `chunks`** — handler returns structured error envelope.
- **Missing `query` on search actions** — structured error envelope.
- **`documents` filter matches nothing** — returns `{ok: true, documents: [], total: 0}` (empty result, not error).
- **`semantic_search` with no embeddings for the corpus** — returns `{ok: true, results: [], reason: 'no_embeddings'}`.
- **Pagination** — cursor-style; `limit + offset` on `documents` + `chunks`; capped per action.

## 5c. Contract ↔ Implementation Consistency

### 5c.1 Handler / module header claims match action reality

**PASS.** Schema `description` names all 5 actions; handler at `td_handlers_ops.py:5223` dispatches per-action.

### 5c.2 Gating truth matches runtime behavior

**PASS.** No feature flag gates the tool. Runtime behavior depends only on which action is invoked + Document/Embedding table state.

### 5c.3 Shared handler-file coupling noted

Shared module: `td_handlers_ops.py`. Adjacent tools include `search_docs` (`_handle_search_docs` at line 5506 — composite validation doc in `search_docs_kb_tool_validation.md`), `ops_tool`, `agent_introspection_tool` (all in Batch 2 sweep).

## 6. Evidence

**Analyzed-mode validation.** Schema at `pa_tool_schemas.py:4567-4632` + handler at `td_handlers_ops.py:5223-5500` (`_handle_kb_browse`) read verbatim. Composite validation doc `search_docs_kb_tool_validation.md` (S2728) provides live-dispatch evidence for all 5 actions from prior sweep.

**Wrong-stem-match rescue rationale:** the gap-map stem matcher (`pa_tools_gap_map.find_matching_doc_stem`) iterates `per_tool_stems` in insertion order (alphabetical). For `kb_tool` (stripped stem `kb`), strategy 3 (`doc_stem.startswith(stem_without_suffix + '_')`) matches `kb_ingest_validation.md` first (alphabetically before `search_docs_kb_tool_validation.md`). Result: classifier hits `kb_ingest_validation.md` which has no `## Covered actions` heading → `doc_exists_unknown`.

Creating this dedicated `kb_tool_validation.md` makes strategy 1 (exact match on tool name) succeed first, correctly classifying `kb_tool` as `validated_full`. This is the **2nd wrong-stem-match rescue** in the Path B sweep (`workspace_tool` was #1 in Batch 1). Per `S3044_path_b_finish_plan.md §4`, this triggers the substrate ledger row promotion candidate for a lint proposal (warn when loose-containment fires and the containing stem is a distinct tool name).

## Related

- **Composite doc (kept for search_docs + kb_tool joint context):** `search_docs_kb_tool_validation.md` (S2728).
- **Wrong-stem-match precedent:** `workspace_tool_validation.md` (S3044 Batch 1).
- **`kb_ingest` action (NOT kb_tool):** `kb_ingest_validation.md` — documents the `kb_ingest` action within `intelligence_tool`.
- **Path B FINISH plan:** `docs/audits/pa_tools/substrate/S3044_path_b_finish_plan.md` §4 (wrong-stem-match discovery + mitigation).
- **Gap-map stem-matcher:** `core/services/pa_tools_gap_map.py:481` (`find_matching_doc_stem`).
- **Shared handler module:** `td_handlers_ops.py`.
- **S3044 Batch 2 T0 SIGN:** pending pre-merge.
