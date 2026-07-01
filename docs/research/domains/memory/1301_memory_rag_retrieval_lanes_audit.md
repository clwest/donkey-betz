---
title: "S1301 Memory RAG Retrieval Lanes — Category D Architecture Audit"
status: draft
authority: research
session_added: 1301
research_group: 1300
child_slot: P1
domain_slug: memory
date: 2026-07-01
last_verified: 2026-07-01
supersedes: none
related:
  - docs/research/domains/memory/1300_memory_domain_scoping.md   # parent (P0)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                    # process (v2, S1276)
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md           # OS v2.1
  - docs/research/platform_architecture_inventory.md             # §3.13, §3.14, §3.15, §5.4
  - docs/research/platform/cross_domain_integration_audit.md     # S1274 integration lens
  - docs/narratives/KNOWLEDGE_RAG_MEMORY.md                      # S1158 comprehensive narrative
  - docs/KNOWLEDGE_PIPELINE.md                                    # runtime flow map
  - docs/topics/personal-assistant.md                             # search_docs PA tool consumer
  - docs/topics/local-askdocs.md                                  # local askdocs vs prod RAG boundary
  - docs/handoffs/SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md  # search_docs origin
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                    # runtime anchor (counts)
  - docs/PLATFORM_WHAT_IT_IS.md                                   # narrative anchor (glossary)
  - docs/EMPLOYEE_OS_PRIMITIVES.md                                # anti-duplication matrix
  - docs/00-START-HERE/DOC_LIFECYCLE.md                           # inventory-wins-on-conflict
dependencies_on:
  - group: 1300
    slug: memory
    role: parent scoping — locks Category D as this child's exclusive scope; feeds §6 provenance-filter finding as §14 anchor evidence
delegates_to:
  - none
delegated_from:
  - group: 1300
    slug: memory
    scope: Category D — RAG / Document Retrieval subdomain per parent §3D (core/rag_integration.py, core/rag.py, Document, DocumentEmbedding, HNSW index, ScopedRetrievalService, RAGObservabilityService, search_docs PA tool, provenance filter mechanics)
verifier_loop: |
  v1.1 (2026-07-01, S1301 Rigby SIGN cycle 1 fold): fresh isolation pin
  pa-a23736a833f646cf (title "S1301 SIGN — RAG Retrieval Lanes audit
  pressure-test (isolation)"; owner chris; ownership match confirmed).
  Rigby's provisional verdict SIGN-with-edits (4 must-fix + 6 nice-to-
  have; claims 1-3 CONFIRMED by her via direct read; claims 4-8
  UNVERIFIABLE-in-pin due to repo_tool file-size caps on
  docs/_provenance.json and pending greps). Parent-agent ran the
  outstanding greps + folded 4 must-fix edits + at least 1 nice-to-have
  hedge before returning to Rigby for final verdict:
  - MF1 (§14.1 denominator) FOLDED — added verbatim _meta block quote
    with docs/_provenance.json:2-14 citation (doc_count: 2156;
    confidence_breakdown HIGH 1356 / MEDIUM 336 / LOW 0 / UNKNOWN 464;
    464 / 2156 = 21.5%).
  - MF2 (§14.3 D3 source_type/ingested_via read) FOLDED — grep
    `source_type|ingested_via` returned 0 hits on core/rag_integration.py,
    core/rag.py, core/services/scoped_retrieval.py; 3 hits in
    core/services/td_handlers_ops.py at lines 617, 691, 4842 are on
    unrelated non-RAG handlers (annotated in the drift matrix).
  - MF3 (§9.1 MISSING inbound) FOLDED — grep-verified: 0 files
    matched for `kb_tool|search_docs|search_embeddings|
    ScopedRetrievalService|rag_integration|core\.rag` across
    core/services/content*.py, core/employees/mission_runner.py,
    core/services/signal_aggregation_service.py; hedged the "MISSING"
    classification to the specific grep scope.
  - MF4 (§14.2 silent-failure claim) FOLDED — system-wide grep of
    `excluded_missing_provenance|excluded_mismatch|pre_filter_count`
    across core/**/*.py returned 2 files (td_handlers_ops.py handler +
    test_search_docs_originating_session_filter.py); added explicit
    scope note that the load-bearing claim is scoped to core/ tree.
  - NH1 (over-binary language) partial fold — Content Pipeline note
    now hedged with "grep-verified for listed symbols only"; Signal
    Engine note similarly. Not all binary phrasings across the audit
    were audited; deferred as follow-up.
  Rigby final verdict after fold (2026-07-01, same fresh pin
  pa-a23736a833f646cf): **SIGN-clean.** All 8 numbered load-bearing
  claims independently CONFIRMED via direct read + grep; MF1-MF4 folds
  re-verified; NH2-NH6 deferred as non-blocking (correctness intact).
  Additional risks Rigby surfaced during re-review: (a) counter-name
  coupling meta-risk — future refactor renaming counters would make
  the "no consumer" grep proof stale without changing underlying
  reality; (b) path-normalization join fragility between
  .rag/corpus.jsonl and docs/_provenance.json remains highest-leverage
  operational failure mode. Both accepted as-recorded in §14 / §7.3;
  neither blocks SIGN. Ratification path per playbook §16: Chris
  commit-gate → status: draft → active on merge.
  v1 (2026-07-01, S1301 synthesis): audit doc synthesized from playbook §13 6-parallel Explore sweep. Category D scope locked by parent §3D + §5D + §6. Chris ratified D6 (immediate launch) + D7 (skip SIGN on parent) in terminal 2026-07-01, logged via Rigby pin pa-aa54193f240f4846.

  Sweep composition:
  - Agent 1 Models & Persistence — Document (content/models.py:325-705), DocumentEmbedding (content/models.py:707-873), UserEmbedding (core/models/users/models.py:886-976), AgentKnowledgeSource (core/models_unified_system.py:521-628); HNSW index migration 0037 (content/migrations/0037_session_730_pgvector_documentembedding.py:35-43); provenance field migration 0044 (content/migrations/0044_provenance_and_promotion.py:29-62).
  - Agent 2 Services & Runtime Flows — filter mechanism trace at td_handlers_ops.py:78-127 (verifier-loop confirmed via direct read); search_docs → core.rag.top_k lane binding at td_handlers_ops.py:5502; kb_tool → rag_integration.search_embeddings binding at td_handlers_ops.py:5202.
  - Agent 3 APIs/Tools/Tasks/Commands — search_docs schema at pa_tool_schemas.py:4526; kb_tool at :4568+; brainstorm_tool at :56; refresh_docs_corpus task at core/tasks.py:5803 (crontab 4:00 AM Denver daily); build_docs_provenance mgmt command; 4-step cascade verified.
  - Agent 4 Integrations — STRONG inbound (PA + BaseAgent + Agent Router); MISSING inbound (Content Pipeline, Employee OS/MissionRunner, Signal Engine); STRONG outbound (EmbeddingService + Redis 7-day cache + pgvector); PA turn enrichment does NOT auto-invoke RAG (grepped unified_pa_entrypoint.py, zero RAG imports).
  - Agent 5 Docs & Prior Research — S1273 §3.14 already answers 13 of 28 canonical playbook questions (cite, don't re-answer); S1142 chunk-coverage gap classified as ingestion-issue, distinct class from parent §6 provenance-filter finding.
  - Agent 6 Drift/Debt/Ownership/Maturity — 6-drift matrix; 9-item debt matrix; root cause analysis (HYP-1 migration-incomplete + HYP-4 never-wired-into-ingestion); verdict WORKING (dropped from STABLE due to corpus-completeness gap; retrieval mechanism itself remains sound).

  Parent-agent verifier-loop spot-checks (direct file reads before including load-bearing claims):
  - td_handlers_ops.py:78-127 — provenance filter mechanism (Agent 2 + 6 claims): CONFIRMED. @lru_cache(maxsize=1); missing-provenance = "exclude when filter is active" (design comment lines 82-85); mismatch vs missing counter split matches sub-agent trace.
  - td_handlers_ops.py:5468-5610 — _handle_search_docs: CONFIRMED runs core.rag.top_k (local keyword lane) at line 5502; filter only activated when originating_session is not None (line 5565); counters embedded in result['filter'] dict (lines 5585-5590), not logged/metricked/alerted.
  - Two-lane split confirmed: search_docs → LOCAL keyword rag.py, kb_tool → PROD pgvector rag_integration.py. This resolves parent §6 finding scope: the excluded_missing_provenance count was against the LOCAL corpus, not the prod pgvector lane.

  Rigby SIGN routing: pending. Playbook §15 requires full SIGN on child audits — will route to a fresh isolation pin (not pa-aa54193f240f4846 the arc pin) after Chris review of this draft. Fold cycle per §16 before considering canonical.
owner: claude (drafted S1301)
---

# S1301 Memory RAG Retrieval Lanes — Category D Architecture Audit

> **What this is.** The first child audit under Research Group 1300
> (Memory / Knowledge / Embeddings). Scope = Category D from the
> S1300 parent scoping doc: RAG / Document Retrieval. This audit
> answers the 28 canonical playbook questions (§9) for Category D
> and traces the parent §6 provenance-filter finding to root cause.
>
> **What this is not.** A design proposal. An implementation plan.
> An audit of Categories A/B/C/E/F/H (they have their own child
> audits — see parent §5). Category G is delegated to the Employee
> OS 1200s follow-up arc per parent §7 anti-scope.
>
> **How to read.** Executive Summary (§1) tells you what shipped
> and what remains open. §14 (Known Drift) is the finding backbone —
> start there if you're triaging. §7 (Runtime Flows) is the
> mechanism map. §19 (Recommended Future Research) queues the
> next arcs.

---

## 1. Executive Summary

Category D is the RAG / Document Retrieval subsystem of Donkey Betz.
It runs two **parallel retrieval lanes** exposed as separate PA
tools:

- **`search_docs`** → keyword scan of a local corpus file
  (`.rag/corpus.jsonl`) via `core.rag.top_k` at `core/rag.py:39-82`.
  Post-ranking, an optional `originating_session` filter applies
  provenance-based exclusion via `docs/_provenance.json`
  (built by `build_docs_provenance` management command).
- **`kb_tool` `action=semantic_search`** → pgvector cosine
  similarity over the `DocumentEmbedding` table via
  `core.rag_integration.search_embeddings` at
  `core/rag_integration.py:27-224`, backed by an HNSW index
  (`content/migrations/0037_session_730_pgvector_documentembedding.py:35-43`).

**These are not two implementations of the same thing.** They
share models (`Document` is common) but their retrieval paths,
storage backends, and provenance semantics diverge completely.
`search_docs` runs the keyword local lane; `kb_tool` runs the
prod pgvector lane. There is **no runtime selector** that
switches between them — the caller chooses by picking a tool.
Playbook §12 flagged the two-lane call-time selector as
outstanding research; this audit confirms nothing has been
implemented.

**The subsystem verdict is WORKING**, dropped from STABLE.
Retrieval mechanism is sound and tested; the corpus that
powers it has completeness gaps that surface as **silent
zero-result queries** to the caller.

The parent §6 provenance-filter finding — 8 semantically-matched
chunks pre-filter → 7 `excluded_missing_provenance` + 1
`excluded_mismatch` → 0 returned — is a **local-lane
corpus-completeness finding**, not a prod-lane retrieval bug.
Root cause: `docs/_provenance.json` has 464 UNKNOWN-session
entries out of 2156 total docs (per the file's `_meta.confidence_breakdown`),
and the filter treats "path not in index" as
`excluded_missing_provenance` by design (`td_handlers_ops.py:82-85`
comment: "search_docs treats 'no provenance for path' as 'exclude
when filter is active'"). The provenance metadata is **external
to chunks** — computed at query time by joining chunk file paths
to the git-history-derived index — and the ingestion pipeline
never wired session tracking onto DocumentEmbedding rows even
though the row-level `source_type` / `ingested_via` fields exist.
**Two provenance systems coexist and do not talk to each other.**

The biggest external gaps are (a) **silent-failure observability**
— filter counters land in the response payload only, with no log
line, no metric, no alert; the S1300 finding was surfaced by
manual tool inspection, not observability; (b) **asymmetric filter
coverage** — the prod pgvector lane is not subject to the
provenance filter at all, so `kb_tool` returns different results
from `search_docs` on the same query; (c) **PA turn enrichment
does not auto-invoke RAG** — `search_docs` and `kb_tool` are
tool-call-only, so a user asking "what did Session 1142 produce?"
gets no docs context unless they explicitly call the tool.

**Recommended next research** (§19): S1302 Memory Persistence
Architecture should own the row-level provenance semantics
question (Categories A + B + C carry the same "who writes what
metadata when" concern); S1304 Documentation Corpus ↔ RAG
Boundary should own the ingestion→retrieval provenance handoff;
Group 1700 Observability should own filter-drop telemetry. A
future design-preparation doc may propose a unified provenance
model — that is not this audit's job.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** RAG Retrieval Lanes is the
subsystem that lets callers pull ranked, cited chunks of platform
content (either the `/docs/` markdown corpus or the
`DocumentEmbedding` table) in response to a semantic or keyword
query. It is the retrieval half of retrieval-augmented generation;
prompt injection consumes its output.

**Q2 — What problem does it solve?** Without it, LLM callers on
this platform would either (a) rely on the model's training data
(stale, hallucination-prone), or (b) receive the entire `/docs/`
corpus in every prompt (cost-prohibitive at 2K+ files). The
retrieval lanes give callers precise, cited passages so LLM
prompts can be grounded and short. `search_docs` optimizes for
"find me the passage that says X"; `kb_tool semantic_search`
optimizes for "give me the semantically closest chunks in the
Document table."

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?**

| Surface | Entry point | File:line | Notes |
|---------|-------------|-----------|-------|
| PA tool (local keyword lane) | `search_docs` handler | `core/services/td_handlers_ops.py:5468` | Runs `core.rag.top_k` on `.rag/corpus.jsonl` |
| PA tool (prod pgvector lane) | `kb_tool action=semantic_search` handler | `core/services/td_handlers_ops.py:5202` (approx — inside `_handle_kb_browse`) | Runs `core.rag_integration.search_embeddings` on `DocumentEmbedding` |
| Python API (prod lane) | `search_embeddings(query, ...)` | `core/rag_integration.py:27-224` | Cosine-distance annotated pgvector query |
| Python API (prod lane) | `search_personal_memories(user, query, ...)` | `core/rag_integration.py:328-439` | Reads `UserEmbedding` (JSONField vector, not pgvector) |
| Python API (local lane) | `top_k(question, k, boost_hints)` | `core/rag.py:39-69` | Token-overlap scoring over JSONL corpus |
| Python API (local lane) | `build_docs_context(question, k, ...)` | `core/rag.py:70-82` | Wrapper that assembles context from `top_k` |
| Agent-layer consumer | `BaseAgent._get_relevant_knowledge_for_task` | `core/agents/base_agent.py:1435` | Three-source retrieval (spider semantic → AgentKnowledgeSource keyword → ScopedRetrievalService docs) |
| Agent-layer consumer | `ScopedRetrievalService.search` | `core/services/scoped_retrieval.py:75` | Used inside `_get_relevant_knowledge_for_task` |
| Agent router (routing enrichment) | `get_scoped_retrieval_service().search` | `core/agent_router.py:2254-2256` | Optional context enrichment for routing decisions |
| Beat task (ingestion cascade) | `refresh_docs_corpus` | `core/tasks.py:5803` | Daily 4:00 AM Denver crontab |
| Beat task (spider embedding backfill) | `backfill_spider_embeddings` | `core/tasks.py` (ml queue) | Every 15 minutes |
| Management command | `build_docs_index` | `core/management/commands/build_docs_index.py:46` | Step 1 of 4-step cascade |
| Management command | `build_rag_corpus` | `core/management/commands/build_rag_corpus.py:56` | Step 2 |
| Management command | `sync_docs_index_to_documents` | `core/management/commands/sync_docs_index_to_documents.py:55` | Step 3 (`--embed` for step 4) |
| Management command | `build_docs_provenance` | `core/management/commands/build_docs_provenance.py` | Writes `docs/_provenance.json` (git-history-derived) |

**REST + WebSocket:** No dedicated REST endpoints; no WebSocket
consumers. All retrieval flows through the PA tool → dispatcher
→ handler path, or through direct Python API on the agent layer.

---

## 4. Major Models

**Q4 — What are the major models?**

| Model | File:line | Purpose | FK graph | Retention | Unique constraints | Ownership |
|-------|-----------|---------|----------|-----------|-------------------|-----------|
| `Document` | `content/models.py:325` | Master corpus item: title, content, metadata, status, tags, category, owner, access control, `source_system` / `source_reference` / `source_url` provenance fields | FK `owner`→User; FK `parent_document`→self; M2M `related_documents`→self; M2M `allowed_users`→User | No auto-retention; `is_pinned=True` overrides; `data_sensitivity` determines eligibility | `(document_type, status)` index only; no content/title uniqueness | this-domain (Category D) |
| `DocumentEmbedding` | `content/models.py:707` | Vector embedding row: `chunk_text`, `embedding_vector` (`VectorField(dimensions=1536)`, pgvector), `chunk_index`, `embedding_model` (`OPENAI_SMALL` default), `chunk_index_end`, `context_before` / `context_after`, `embedding_cost`, per-migration-0044 `source_type` + `ingested_via` provenance fields | FK `document`→Document CASCADE; inherits UnifiedBaseModel | Cascade on parent Document delete | `(document, chunk_index, embedding_model)` per Meta.unique_together | this-domain (Category D) |
| `UserEmbedding` | `core/models/users/models.py:886` | User-scoped personal memory embedding: content, `embedding_vector` **JSONField** (not pgvector), source (agent/system), confidence + usage tracking | FK `user`→User CASCADE; FK `source_application`→JobApplication nullable | Cascade on user | `(user, content_type)` index only | shared (Category D × Category B UserAgentLearning; queried by `rag_integration.search_personal_memories` at `core/rag_integration.py:328-439`) |
| `AgentKnowledgeSource` | `core/models_unified_system.py:521` | Cross-agent knowledge aggregate from spider data: title, summary, key_insights, confidence/relevance/freshness scores, source attribution | FK `agent`→Agent CASCADE; FK `spider_category`→SpiderCategory nullable; FK `source_project`, `source_research` nullable | `expires_at` nullable; `is_active=False` soft-delete; 14-day freshness heuristic in ConversationOrchestrator | `(agent, knowledge_type, spider_category)` index only | shared (Category D × Category A — S1273 §5.4 overlap flag; no direct RAG integration in `rag_integration.py`) |

**Non-D provenance models (inventoried but out-of-scope):**

- `ContentProvenance` at `core/models_unified_system.py:15558` — Category C media provenance (images / video / audio / 3D / text lineage). Distinct from RAG retrieval provenance.
- `DataProvenance` at `core/models_unified_system.py:19099` — Category H market intelligence lineage. Distinct from RAG retrieval provenance.

**pgvector HNSW index (schema, not a Django model):**

- Migration: `content/migrations/0037_session_730_pgvector_documentembedding.py:35-43`
  ```sql
  CREATE INDEX IF NOT EXISTS documentembedding_vector_hnsw_idx
  ON content_documentembedding
  USING hnsw (embedding_vector vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
  ```
- ORM state sync: `content/migrations/0040_documentembedding_hnsw_index_state.py:19-26` (SeparateDatabaseAndState).
- Meta.indexes reflection: `content/models.py:833-836` (`HnswIndex(...)` when `HAS_PGVECTOR` at import time).
- Distance operator: `vector_cosine_ops` (cosine similarity).

**Provenance-field migration (row-level, on DocumentEmbedding):**

- Migration: `content/migrations/0044_provenance_and_promotion.py:29-62` (2026-03-01)
- Added `source_type` (CharField, choices `('internal', 'web', 'spider', 'user_upload', 'api', 'unknown')`, default `'unknown'`) and `ingested_via` (CharField, choices `('auto_research', 'manual', 'spider_pipeline', 'sync_docs', 'backfill', 'unknown')`, default `'unknown'`).
- **Critical finding:** Because both fields are CharField with `default='unknown'` (no `null=True`), all pre-migration rows landed as literal `'unknown'` values, not NULL. **The `excluded_missing_provenance` counter therefore does NOT mean "rows with NULL DocumentEmbedding.source_type."** See §7 Runtime Flows for the actual filter mechanism.

**S1273 §5.4 overlap re-verification (playbook §7 policy: cite, don't restate):**

Per `docs/research/platform_architecture_inventory.md:2657-2672`, five memory / knowledge stores + two RAG lanes are named as an overlap concern. Direct schema comparison of the two RAG-adjacent models:

- `DocumentEmbedding.embedding_vector`: `VectorField(dimensions=1536, null=True, blank=True)` — pgvector, prod HNSW.
- `AgentKnowledgeSource`: **no embedding field.** Stores structured summary + `key_insights` (JSONField).
- `UserEmbedding.embedding_vector`: `JSONField` — cosine computed in Python, not pgvector.

Verdict: **no schema duplication.** The S1273 §5.4 flag is at the **integration/cognitive-load** layer, not the schema layer. Different embedding models, different tables, complementary purposes. Further boundary discussion in §17.

---

## 5. Major Services

**Q5 — What are the major services?**

| Service / module | File:line | Line count (approx) | Purpose | God-service risk |
|-------------------|-----------|---------------------|---------|------------------|
| `core/rag_integration.py` | `core/rag_integration.py:1-466` | 466 | Prod pgvector retrieval module: `create_embedding`, `search_embeddings`, `get_rag_context`, `search_personal_memories` | No — bounded module, single-concern |
| `core/rag.py` | `core/rag.py:1-82` | 82 | Local keyword retrieval: `top_k`, `build_docs_context` over `.rag/corpus.jsonl` | No — tiny |
| `core/services/embedding_service.py` — `EmbeddingService` | `core/services/embedding_service.py:66-407` | 341 | Central OpenAI wrapper for `text-embedding-3-small`; Redis cache (`CACHE_TTL = 7 * 86400` at line 80); cost tracking; batch API | No — bounded |
| `core/services/scoped_retrieval.py` — `ScopedRetrievalService` | `core/services/scoped_retrieval.py:75` (`search` method) | UNKNOWN (Agent 2 did not measure); used by BaseAgent + Agent Router | Wraps `search_embeddings` with domain scoping (per file name; interior not sweep-verified) | UNKNOWN — needs read |
| `core/services/rag_observability_service.py` — `RAGObservabilityService` | `core/services/rag_observability_service.py:124-200` | ~200 | Telemetry surface for RAG queries; risk-aware critical-doc boost; context budget tracking. Session 954 introduction | No |
| `content/embeddings.py` — `process_document_for_rag` + `_derive_source_type` | `content/embeddings.py:600-696` (main), `:45-63` (`_derive_source_type`), `:642-656` (create call) | 696 | Ingestion-side embedding generation; populates `DocumentEmbedding.source_type` from Document metadata | No |

**Two-lane persistence split (verified):**

- **Prod lane (`rag_integration.py`)** reads from `DocumentEmbedding` table via Django ORM + pgvector `CosineDistance` annotation. Query at `core/rag_integration.py:120-127`:
  ```python
  qs = (
      DocumentEmbedding.objects
      .filter(document__file_path__isnull=False)
      .exclude(document__file_path='')
      .annotate(distance=CosineDistance('embedding_vector', query_embedding))
      .filter(distance__lt=(1 - similarity_threshold))
  )
  ```
- **Local lane (`rag.py`)** reads from `.rag/corpus.jsonl` (JSON-lines file). Query at `core/rag.py:59` — pure Python token-overlap scan:
  ```python
  q_terms = set(question.lower().split())
  for line in CORPUS_PATH.open():
      row = json.loads(line)
      base = sum(1 for w in q_terms if w in tl)
  ```

The lanes **share the Document model** conceptually, but the local corpus is a **derived artifact** produced by `build_rag_corpus` from `docs/_index.json`. The chunk unit differs: prod = `DocumentEmbedding` rows (`chunk_index` per document, `embedding_model`-scoped); local = arbitrary 1200-char text chunks in a flat JSONL file.

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs?**

### 6.1 `search_docs` PA tool

- **Schema**: `core/services/pa_tool_schemas.py:4524-4566`.
- **Handler**: `core/services/td_handlers_ops.py:5468-5610`.
- **Parameters** (verifier-loop confirmed via direct read):
  | Param | Type | Required | Default | Bounds | Purpose |
  |-------|------|----------|---------|--------|---------|
  | `query` | string | yes | — | non-empty | Search terms |
  | `k` | integer | no | 8 | clamped `[1, 20]` (line 5481) | Top-K chunks |
  | `max_chars` | integer | no | 6000 | clamped `[500, 12000]` (line 5485) | Cross-chunk char cap |
  | `originating_session` | integer | no | None | must be int-parseable | Provenance filter — when set, drop chunks whose file path isn't in `docs/_provenance.json` or whose stored `originating_session` doesn't match |
- **Return shape** (line 5595-5606):
  ```python
  {
      'query': str,
      'result_count': int,
      'k_requested': int,
      'max_chars': int,
      'truncated': bool,
      'total_chars': int,
      'chunks': [{'file': str, 'chunk_id': ..., 'citation': str, 'text': str}],
      'filter'?: {  # only present when originating_session was set
          'originating_session': int,
          'pre_filter_count': int,
          'excluded_mismatch': int,
          'excluded_missing_provenance': int,
      },
  }
  ```

### 6.2 `kb_tool` PA tool (`action=semantic_search` and adjacent)

- **Schema**: `core/services/pa_tool_schemas.py:4568+` (`kb_tool`).
- **Handler**: `core/services/td_handlers_ops.py:5202` (`_handle_kb_browse` or similar).
- **Actions**: `stats`, `documents` (with D9/D10 filter set from S1234), `chunks`, `search_embeddings`, `semantic_search`.
- **`semantic_search` action** → `core/rag_integration.search_embeddings` (prod pgvector lane).
- **Filters exposed**: `query`, `document_id`, `content_type`, `category`, `document_class`, `is_pinned`, `min_session`, `include_superseded`, `similarity_threshold`.

### 6.3 `brainstorm_tool` PA tool

- **Schema**: `core/services/pa_tool_schemas.py:56`.
- **Purpose**: search discussion panels / multi-agent debates. **Not RAG retrieval** — separate corpus. Included in inventory only because sub-agent grep surfaced it as adjacent to RAG naming.

### 6.4 No REST / WebSocket surface

Grep across `core/urls*.py` returned zero hits for `search_docs`, `search-docs`, or RAG-scoped endpoint patterns. Retrieval is intentionally PA-tool-scoped (Agent 3).

---

## 7. Runtime Flows

**Q9 — What are the major runtime flows?**

### 7.1 Query flow — `search_docs` (LOCAL keyword lane)

Verifier-loop confirmed via direct read of `td_handlers_ops.py:5468-5610` and `core/rag.py:39-82`:

```
1. Caller (PA tool dispatcher) invokes _handle_search_docs(payload)
                    │
                    ▼  td_handlers_ops.py:5477-5487
2. Validate query (non-empty); clamp k ∈ [1,20]; clamp max_chars ∈ [500,12000]
                    │
                    ▼  td_handlers_ops.py:5489-5499
3. Parse originating_session (int) if passed; return error on invalid
                    │
                    ▼  td_handlers_ops.py:5501-5511
4. Import core.rag.top_k + CORPUS_PATH; return regen hint if corpus missing
                    │
                    ▼  td_handlers_ops.py:5517-5518
5. k_fetch = min(k*4, 80) if originating_session else k  (overshoot for post-filter)
                    │
                    ▼  core/rag.py:39-69
6. top_k(query, k=k_fetch, boost_hints=False):
   - Open .rag/corpus.jsonl (file-based, JSONL rows: {file, chunk_id, text, ...})
   - For each row: token-overlap score = |q_terms ∩ text_lowercase_terms|
   - Sort descending; return top k_fetch as dicts {file, chunk_id, text}
                    │
                    ▼  td_handlers_ops.py:5530-5561
7. Assemble chunks list with citation-prefixed truncation; enforce max_chars budget
                    │
                    ▼  td_handlers_ops.py:5563-5590  ★★ PROVENANCE FILTER ★★
8. If originating_session is not None:
   a. provenance_docs = _load_provenance_docs()  [lru_cache(maxsize=1)]
      - Reads docs/_provenance.json once per process
      - Returns docs dict {file_path: {originating_session, confidence, ...}}
   b. If provenance_docs empty (file missing): return 0 results with regen note
   c. _filter_chunks_by_originating_session(chunks, originating_session, provenance_docs):
      For each chunk:
        path = chunk['file']
        - if no path: missing += 1, drop
        - meta = provenance_docs.get(path)
        - if not meta: missing += 1, drop  ← "excluded_missing_provenance"
        - if meta['originating_session'] != originating_session: mismatch += 1, drop  ← "excluded_mismatch"
        - else: kept.append(chunk)
      Return (kept, mismatch, missing)
   d. Trim kept[:k]
   e. Attach filter_meta {originating_session, pre_filter_count, excluded_mismatch, excluded_missing_provenance}
                    │
                    ▼  td_handlers_ops.py:5595-5606
9. Return result dict {query, result_count, chunks, filter?: filter_meta, ...}
```

**Load-bearing observations from this trace:**

- **Filter is post-ranking, not query-side.** The token-overlap scorer returns matches; the filter drops them afterward. The filter cannot "widen" the search to compensate for exclusions — it only trims.
- **Filter is opt-in.** When `originating_session` is None, no filter runs, no `filter` block appears in the response. So a bare `search_docs(query='X')` call returns all matches; the S1300 finding required a caller to explicitly pass `originating_session=N`.
- **Filter is CONSERVATIVE-BY-DESIGN.** The comment at `td_handlers_ops.py:82-85` (`_load_provenance_docs` docstring) is explicit: *"search_docs treats 'no provenance for path' as 'exclude when filter is active', so a missing index degrades gracefully (filter just excludes everything, surfacing the regen hint to the user)."* This is Rigby's S1145 P2 spec.
- **Filter counters are payload-only.** No log line, no metric, no alert emits when `excluded_missing_provenance > 0`. See §10 Event Flows and §14.2 Silent-Failure Surface.

### 7.2 Query flow — `kb_tool semantic_search` (PROD pgvector lane)

Sub-agent trace (Agent 2) — spot-check confirms structural claims but interior of `_handle_kb_browse` was not fully re-read by parent-agent verifier; treat internal line numbers as SPECULATIVE where called out.

```
1. Caller (PA tool dispatcher) invokes _handle_kb_browse(action='semantic_search', payload)
                    │
                    ▼  td_handlers_ops.py:~5379-5428 (approx, per Agent 2)
2. Route to semantic_search branch; validate query
                    │
                    ▼  core/rag_integration.py:16-25
3. create_embedding(query) → EmbeddingService.create_embedding(model='text-embedding-3-small')
   - Redis cache probe (7-day TTL, embedding_service.py:80-116)
   - Miss → OpenAI batch API call; store in cache; return vector
                    │
                    ▼  core/rag_integration.py:120-139  (pgvector similarity search)
4. qs = DocumentEmbedding.objects
        .filter(document__file_path__isnull=False)
        .exclude(document__file_path='')
        .annotate(distance=CosineDistance('embedding_vector', query_embedding))
        .filter(distance__lt=(1 - similarity_threshold))
   Then filter pushdown on Document fields:
     category, document_class, is_pinned, min_session, promotion_status
                    │
                    ▼  core/rag_integration.py:~140-224
5. .order_by('distance')[:limit] → list of {id, content, content_type, metadata, importance_score, similarity_score}
                    │
                    ▼  td_handlers_ops.py (kb_tool handler)
6. Return payload
```

**Load-bearing observations from this trace:**

- **NO provenance filter.** Neither `_load_provenance_docs` nor `_filter_chunks_by_originating_session` appear in the `kb_tool` path. The provenance-filter concern is **local-lane-only**.
- **Filter pushdown IS on the prod lane** — but it filters on `Document` fields (`category`, `document_class`, `min_session`, etc.), not on the local `docs/_provenance.json` index.
- **Row-level `DocumentEmbedding.source_type` / `ingested_via` fields are NOT read** during prod retrieval either. They exist on rows (populated by `content/embeddings.py:642-656` at ingestion) but no query path consults them. This confirms Agent 6 drift finding: **two provenance systems coexist and neither system's data participates in the other system's query.**

### 7.3 Ingestion flow — 4-step docs cascade

Verifier-loop verified through management-command entry points and cross-referenced with `docs/AUDIT_FINDINGS.md` §12 canonical Celery deferred list per memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md`:

```
Trigger: refresh_docs_corpus beat task (core/tasks.py:5803, crontab hour=4, minute=0)
                                       OR
         manual: python manage.py <command>
                    │
                    ▼  Step 1
1. build_docs_index (core/management/commands/build_docs_index.py:46)
   - Walk /docs tree
   - Write docs/INDEX.md (markdown) + docs/_index.json (structured)
                    │
                    ▼  Step 2
2. build_rag_corpus (core/management/commands/build_rag_corpus.py:56)
   - Read docs/_index.json
   - Chunk into fixed-size text pieces (default 1200 chars)
   - Write .rag/corpus.jsonl (JSONL: {file, chunk_id, text})
                    │
                    ▼  Step 3
3. sync_docs_index_to_documents (core/management/commands/sync_docs_index_to_documents.py:55)
   - Read docs/_index.json
   - Upsert into Document table (map type via TYPE_MAPPING; status via STATUS_MAPPING)
   - Does NOT generate DocumentEmbedding rows (that's step 4)
                    │
                    ▼  Step 4 (with --embed flag)
4. sync_docs_index_to_documents --embed
   - Fan out generate_document_embeddings.delay() per unembedded Document
   - Each task calls process_document_for_rag(document, ingested_via='sync_docs')
   - Populates DocumentEmbedding rows with:
     * chunk_text (from document splitting)
     * embedding_vector (via EmbeddingService.create_embedding)
     * source_type (derived by _derive_source_type from Document metadata)
     * ingested_via = 'sync_docs' (parameter)
```

**Separate provenance-index build (NOT part of the 4-step cascade):**

```
Independent trigger: manual invocation (no beat schedule found by sub-agent grep)
                    │
                    ▼
build_docs_provenance (core/management/commands/build_docs_provenance.py)
   - Walk git log for each doc file in /docs
   - Extract originating_session from commit subject tag (`docs(session-NNNN):`)
     with a confidence ladder:
       HIGH — session tag in commit subject
       MEDIUM — session mention in commit body
       LOW — YAML frontmatter session:
       UNKNOWN — no session reference found
   - Default excludes docs/archive/** and docs/docs-pattern/**
     (--include-archive / --include-framework override)
   - Write docs/_provenance.json:
     {
       "_meta": {generated, doc_count, confidence_breakdown, ...},
       "docs": {
         "docs/path.md": {
           originating_session: int|null,
           confidence: "HIGH"|"MEDIUM"|"LOW"|"UNKNOWN",
           match_source, first_commit_sha, first_commit_date,
           first_commit_subject, sessions_touched, commit_count, prs
         },
         ...
       }
     }
```

**Critical observation:** `build_docs_provenance` writes a **file-path-keyed** index, and `_filter_chunks_by_originating_session` looks up chunk metadata by `chunk['file']` path. But `chunk['file']` comes from the `.rag/corpus.jsonl` produced by `build_rag_corpus` in Step 2. **If the two commands run against different file trees or with different path-normalization, the join is broken silently.** No integrity check validates that every `corpus.jsonl` chunk's `file` exists as a key in `_provenance.json`.

### 7.4 Two-lane selector

Verifier-loop confirmed: **no runtime selector exists.**

- `search_docs` handler hardcodes `from core.rag import top_k` at `td_handlers_ops.py:5502`. No branch to `rag_integration`.
- `kb_tool semantic_search` handler routes to `core.rag_integration.search_embeddings` (Agent 2 trace). No branch to `core.rag`.
- No `if settings.RAG_LANE == 'prod'` pattern; no env-var switch; no runtime probe.
- The **caller decides which lane** by picking which PA tool to call. **The LLM caller (Rigby / a user's LLM turn) does not have visible guidance for when to call which.**

**PA schema descriptions** (verifier-loop-confirmed):

- `search_docs` description ends: *"Powered by `core.rag.build_docs_context` over `.rag/corpus.jsonl` (19K+ chunks across 2K+ files). Returns [docs/path#chunk_id] citations. Session 1145 P2: optional originating_session filter…"*
- `kb_tool` description (via schema Agent 3): browsing + semantic search over `DocumentEmbedding`.

So the LLM caller has to read the tool descriptions carefully to distinguish. **Playbook §12 §3.13 note flagged this as outstanding research; the audit confirms no selector was ever built.**

### 7.5 Observability flow

Verifier-loop confirmed via grep + direct read:

- `search_docs` counters (`pre_filter_count`, `excluded_mismatch`, `excluded_missing_provenance`) live in `result['filter']` dict at `td_handlers_ops.py:5585-5590`.
- `logger.error(f"[SEARCH_DOCS] error: {e}")` at line 5609 fires **only on exception**, not on 0-results-with-filter-drop.
- No Prometheus metric found in `core/services/rag_observability_service.py`. Its role appears to be prod-lane risk-aware scoring (critical-doc boost, context budget) rather than filter-drop telemetry (SPECULATIVE — parent-agent verifier did not read the full RAGObservabilityService class; Agent 6 flagged ownership as UNCLEAR).
- No alert / notification rule consumes the counters (Agent 6 grep).

---

## 8. Data Ownership and Lifecycle

**Q16 — What data does this domain own?**

Category D owns:
- `Document` table (shared with Category E docs corpus governance for the ingestion side — see §17 and §19 for boundary questions).
- `DocumentEmbedding` table (exclusive; vector storage + row-level provenance fields).
- `.rag/corpus.jsonl` file (build artifact of Step 2 cascade).
- `docs/_provenance.json` file (build artifact of `build_docs_provenance` — arguably owned by Category E, see §18 Ownership Gaps).

**Q17 — What data does it consume?**

- **From docs corpus (Category E):** `/docs/**/*.md` source content.
- **From spider network:** spider-sourced documents ingested with `ingested_via='spider_pipeline'` (per DocumentEmbedding choices at content/models.py:802-823).
- **From OpenAI:** embeddings via `EmbeddingService.create_embedding` (`text-embedding-3-small`, 1536D).
- **From Redis:** cached embeddings (7-day TTL per `core/services/embedding_service.py:80`).
- **From git history:** originating_session provenance via `build_docs_provenance` (per docs/_provenance.json build).

**Q18 — What data does it produce?**

- Search results (chunk lists with citations) to PA tool callers.
- Knowledge injection payloads to agents via `BaseAgent._get_relevant_knowledge_for_task` (`core/agents/base_agent.py:1435`).

### 8.1 Retention / lifecycle

| Surface | Retention policy | Cadence | Owner |
|---------|-----------------|---------|-------|
| `Document` rows | No auto-retention. `is_pinned=True` overrides. `data_sensitivity` gates policy eligibility. | Ad-hoc | Category D + Category E overlap (unclear — §18) |
| `DocumentEmbedding` rows | Cascade delete on parent Document delete (Meta.on_delete=CASCADE) | Reactive | Category D |
| `.rag/corpus.jsonl` | Rebuilt entirely each Step 2 cascade run; no incremental update | Daily 4:00 AM Denver (via `refresh_docs_corpus` beat) | Category D |
| `docs/_provenance.json` | Rebuilt entirely each `build_docs_provenance` run | **NO scheduled cadence found** — manual only (Agent 3 grep found no beat schedule) | UNCLEAR — see §18 |
| Redis embedding cache | 7-day TTL | Automatic (Redis) | Category D |

### 8.2 Embedding refresh cadence — UNKNOWN

Per S1273 §3.14 known drift bullet: *"Embedding cadence for documents UNKNOWN."* This audit re-verifies:

- Spider-sourced embeddings: 15-minute backfill via `backfill_spider_embeddings` beat task (per Agent 3 + S1273 §3.8).
- `/docs/` corpus embeddings: **ad-hoc only.** Triggered by `refresh_docs_corpus` daily beat if hash-delta detects unembedded rows; otherwise no automatic refresh when a Document is edited in place.
- The auto-cascade `refresh_docs_corpus` at `core/tasks.py:5803` has hash-delta gating — verifier-loop-verified via Agent 3 trace but did NOT re-read the task source. **SPECULATIVE:** whether hash-delta correctly detects content edits (vs. only detecting new file additions) is not verified in this audit; would require reading the task source.

### 8.3 Chunk-coverage baseline (S1142 finding, re-verified)

Per SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md:17-19, 56 (Agent 5):

- **Before S1142:** `Document` table empty; corpus stale 17 days.
- **After S1142 close:** 852 docs synced; 14,149 chunks indexed.

**Current coverage** as of S1301: **UNKNOWN** — no periodic health check emits corpus size. Agent 5 flagged: *"KNOWLEDGE_RAG_MEMORY.md §6 marks current coverage as UNKNOWN."* Recommended §19 follow-on: standing observability metric for corpus size + embedding coverage delta.

**Classification (playbook §12 anti-duplication):** This S1142 chunk-coverage baseline is **not the same class** as the parent §6 provenance-filter finding. S1142 = ingestion-completeness (corpus size); parent §6 = filter-completeness (provenance index coverage). See §14.4 for the cross-classification.

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22.** Integration Strength values per playbook §12: `STRONG` / `WEAK` / `MISSING` / `OVERCOUPLED` / `UNKNOWN`. Cross-referenced with `docs/research/platform/cross_domain_integration_audit.md` (S1274).

### 9.1 Inbound consumers

| Consumer domain | Entry point | File:line | Purpose | Strength |
|-----------------|-------------|-----------|---------|----------|
| **Personal Assistant (Rigby)** | `search_docs` PA tool handler | `core/services/td_handlers_ops.py:5468` | Docs-corpus retrieval (LOCAL keyword lane) | STRONG |
| **Personal Assistant (Rigby)** | `kb_tool` PA tool handler (`semantic_search` action) | `core/services/td_handlers_ops.py:5202` | Semantic retrieval over `DocumentEmbedding` (PROD pgvector lane) | STRONG |
| **Agent System (BaseAgent)** | `BaseAgent._get_relevant_knowledge_for_task` | `core/agents/base_agent.py:1435-1609` | 3-source knowledge injection: (1) spider semantic search first; (2) `AgentKnowledgeSource` keyword; (3) `ScopedRetrievalService.search` (docs). Injected during `_build_prompt` at lines 1692, 1886, 2328. | STRONG |
| **Agent System (Agent Router)** | `get_scoped_retrieval_service().search` | `core/agent_router.py:2254-2256` | Docs-scoped context enrichment for routing decisions | WEAK (optional path) |
| **Content Pipeline** | — | Grep of `kb_tool\|search_docs\|search_embeddings\|ScopedRetrievalService\|rag_integration\|core\.rag` in `core/services/content*.py` returns **zero files matched** (Rigby SIGN cycle grep-verified 2026-07-01) | Should query RAG for claim verification but does not; ClaimsPack builder reads spider data only. NOTE: Content Pipeline has its own provenance-tracking via `ContentProvenance` (`core/models_unified_system.py:15558`) — that surface is out-of-scope for Category D | **MISSING (grep-verified for the listed retrieval symbols in `core/services/content*.py` only)** |
| **Employee OS / MissionRunner** | — | Grep of the same symbols in `core/employees/mission_runner.py` returns **zero files matched** (Rigby SIGN cycle grep-verified 2026-07-01) | Mission planning does not inject retrieval context; job step functions call *ingestion* commands (`build_docs_index`, `sync_docs_index_to_documents`) but not retrieval | **MISSING on the mission_runner.py surface (grep-verified); STRONG on producer / ingestion-driving side** (`core/jobs/docs_cascade.py:352-376`) |
| **Signal Engine** | — | Grep of the same symbols in `core/services/signal_aggregation_service.py` returns **zero files matched** (Rigby SIGN cycle grep-verified 2026-07-01) | Signal patterns could cross-reference documented precedent; do not | **MISSING (grep-verified for the listed symbols on `signal_aggregation_service.py` only — broader Signal Engine files not exhaustively grepped)** |

### 9.2 Outbound dependencies

| Dependency | Called at file:line | Purpose | Strength |
|------------|--------------------|---------|----------|
| **EmbeddingService** (OpenAI `text-embedding-3-small`) | `core/rag_integration.py:16-25` (`create_embedding` wrapper) | Query embedding for pgvector cosine | STRONG |
| **`EmbeddingService` singleton** | `core/services/embedding_service.py:66-407` | Central OpenAI wrapper; cost tracking; Redis cache; batch API | STRONG |
| **Redis embedding cache** | `core/services/embedding_service.py:80, 95-116` | `CACHE_TTL = 7 * 86400` (7 days) | STRONG |
| **pgvector Postgres extension** | `core/rag_integration.py:120-127` | `CosineDistance` annotation on `DocumentEmbedding.embedding_vector` | STRONG |
| **`Document` + `DocumentEmbedding` ORM models** | `core/rag_integration.py:94, 121-139` | Filter pushdown + HNSW similarity | STRONG |
| **Documentation Corpus (Category E ingestion)** | `core/jobs/docs_cascade.py:352-376` | 4-step cascade orchestration (step_1_build_docs_index → step_2_build_rag_corpus → step_3_sync_docs_index_to_documents → step_4_embed) | STRONG (ingestion side) |
| **Local keyword corpus (`.rag/corpus.jsonl`)** | `core/rag.py:39-82` | Token-overlap ranking; fallback quality vs prod | WEAK |
| **OpenAI client factory** | `core/services/embedding_service.py:121-123` | Cost-tracking wrapper per memory rule `feedback_openai_client_factory` | STRONG |
| **git history (via `build_docs_provenance`)** | `core/management/commands/build_docs_provenance.py` | Session origin extraction for provenance index | STRONG (indirect — provenance builder) |

### 9.3 Cross-domain findings

- **Asymmetric consumer zones.** The platform bifurcates: (a) **PA + Agent System** are STRONG RAG consumers via multiple entry points; (b) **Content Pipeline + Employee OS + Signal Engine** have MISSING RAG consumption despite semantic-signal potential. This is a design boundary worth surfacing to future arcs (see §19).
- **PA turn enrichment is TOOL-CALL-ONLY.** Verifier-loop confirmed by Agent 4: grep of `core/services/unified_pa_entrypoint.py` returned zero RAG imports. `search_docs` and `kb_tool` fire only when the LLM caller (Rigby) issues a tool call; they are not auto-injected into every PA turn. So a user asking Rigby "tell me about OpsRun" without triggering a tool call gets **zero docs context** — Rigby answers from LLM training + conversation memory, not from the corpus.
- **BaseAgent three-source retrieval order** at `core/agents/base_agent.py:1435-1609`: (1) spider semantic; (2) `AgentKnowledgeSource` keyword; (3) `ScopedRetrievalService.search`. No published ranking rationale; if the three sources return conflicting knowledge, no tie-break rule is documented (Agent 4 gap).

### 9.4 S1274 cross-domain audit re-cite

Per `docs/research/platform/cross_domain_integration_audit.md` §2.5 (S1274, cited by Agent 4 at cross_domain_integration_audit.md:300-302): PA and Agent paths both classified STRONG. No S1274 finding contradicts this audit.

---

## 10. Event Flows

**Q19 — What events does this domain emit?**

Grep-verified: **no dedicated event emission from the retrieval path.** Neither `search_docs` nor `search_embeddings` publishes to any event bus, django signal, or telemetry topic. Filter counters (`excluded_missing_provenance`, `excluded_mismatch`, `pre_filter_count`) live exclusively in the `result['filter']` payload returned to the tool caller.

Adjacent event-emitting surfaces (out-of-scope but named for reader orientation):

- Ingestion side: `generate_document_embeddings.delay()` is a Celery task — Celery task lifecycle events (SEND / RECEIVED / SUCCESS / FAILURE) exist but are Celery-native, not RAG-domain semantic events.
- `RAGObservabilityService` (`core/services/rag_observability_service.py`) may emit prod-lane query telemetry (critical-doc boost, context budget). **SPECULATIVE** — parent-agent verifier did not read the service body; Agent 6 flagged its ownership as UNCLEAR and its wiring to the query path as UNKNOWN.

**Q20 — What events should it emit?**

Per S1274 §6 gap analysis discipline, this audit surfaces the following event-emission gaps:

1. **Filter-drop event** — every `search_docs` call with `excluded_missing_provenance > 0` OR `excluded_mismatch > 0`. Would enable a monitoring query for "silent zero-result rate."
2. **Corpus staleness event** — when `refresh_docs_corpus` beat runs and `_meta.doc_count` on the newly-built corpus differs from the prior run by more than a threshold.
3. **Provenance-index rebuild event** — since `build_docs_provenance` has no beat schedule, an event emitted on manual invocation would let downstream consumers (e.g., an lru_cache invalidator) know to reset.
4. **Query-per-lane telemetry** — inbound query rate on `search_docs` vs `kb_tool semantic_search` to inform the two-lane selector research question.

None of the above events exist today. This audit does not recommend implementing them (that's design-preparation-phase work); it only names the gaps for §19 downstream missions.

---

## 11. Existing Documentation

**Q10 — What documentation exists?** Per Agent 5 sweep:

| Doc | Path | Scope | Covers Category D? |
|-----|------|-------|--------------------|
| `KNOWLEDGE_PIPELINE.md` | `docs/KNOWLEDGE_PIPELINE.md` | Flow map: spider → embeddings → bridges → prompts | YES-PARTIAL |
| `KNOWLEDGE_RAG_MEMORY.md` | `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` | S1158 comprehensive narrative: 5 memory surfaces + 2 RAG paths + 8 milestones | **YES-FULL** |
| `PLATFORM_WHAT_IT_IS.md` | `docs/PLATFORM_WHAT_IT_IS.md` | Platform narrative anchor | TANGENTIAL |
| `DATABASE_MODEL_REFERENCE.md` | `docs/DATABASE_MODEL_REFERENCE.md` | DB table reference | YES-PARTIAL |
| `personal-assistant.md` | `docs/topics/personal-assistant.md` | PA system; includes `search_docs` tool coverage | YES-PARTIAL |
| `local-askdocs.md` | `docs/topics/local-askdocs.md` | Dedicated topic: `core.rag` vs `core.rag_integration` boundary | YES-FULL (local lane) |
| `platform_architecture_inventory.md` §3.13 | `docs/research/platform_architecture_inventory.md:1073-1198` | Memory / Knowledge / Embeddings inventory | YES-PARTIAL |
| `platform_architecture_inventory.md` §3.14 | `docs/research/platform_architecture_inventory.md:1199-1249` | **RAG / Document Loading** — CANONICAL for Category D | **YES-FULL** |
| `platform_architecture_inventory.md` §3.15 | `docs/research/platform_architecture_inventory.md:1250+` | Docs corpus governance | TANGENTIAL (E-side) |
| `platform_architecture_inventory.md` §5.4 | `docs/research/platform_architecture_inventory.md:2657-2672` | Multiple memory stores overlap | YES-PARTIAL |
| `1300_memory_domain_scoping.md` | `docs/research/domains/memory/1300_memory_domain_scoping.md` | Parent scoping — defines Category D scope + §6 finding | YES-FULL (scoping) |
| `SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md` | `docs/handoffs/…` | `search_docs` introduction + baseline chunk-coverage | YES-PARTIAL |
| `cross_domain_integration_audit.md` | `docs/research/platform/cross_domain_integration_audit.md` | S1274 integration map; Category D consumer classifications | YES-PARTIAL |

### 11.1 Gap analysis (what documentation does NOT cover)

Ranked by Category-D-relevance:

- **Provenance-filter mechanism.** No doc explains the `_load_provenance_docs` → `_filter_chunks_by_originating_session` chain, the "missing-provenance = exclude by design" contract, or the lru_cache staleness rule. The contract lives only in the source-code docstring at `td_handlers_ops.py:82-85`.
- **Two-lane selector guidance.** No doc tells the LLM caller (or human operator) which lane to prefer for which query class.
- **`RAGObservabilityService` role.** Service exists but is undocumented in topic docs; only referenced obliquely in S1273 §3.13.
- **Provenance index gap.** The `docs/_provenance.json` file's 464 UNKNOWN-session entries are surfaced only via the file's own `_meta.confidence_breakdown` — not documented in any topic doc.
- **Row-level `DocumentEmbedding.source_type` / `ingested_via` role.** Fields exist and are populated at ingestion, but no doc explains that no query path reads them.

---

## 12. Research Coverage

**Q11 + Q13 — What research already exists? What is the coverage class?**

Per playbook §12: `NONE` / `LIGHT` / `MODERATE` / `DEEP` / `CANONICAL`.

**Coverage class (pre-S1301): MODERATE.**

**Coverage class (post-S1301 landing): DEEP.**

**Evidence for pre-S1301 MODERATE:**

- S1273 §3.14 provides CANONICAL inventory (deep model + service inventory with file:line cites) but stops at the mechanism boundary — does not trace the provenance filter or the two-lane selector question.
- `KNOWLEDGE_RAG_MEMORY.md` (S1158) is CANONICAL narrative but predates S1145 P2 provenance filter introduction.
- `local-askdocs.md` covers only the local lane; does not address the two-lane boundary.
- S1142 handoff documents `search_docs` origin + chunk-coverage baseline; does not cover the S1145 P2 filter changes.

**Evidence for post-S1301 DEEP:**

- This audit adds: end-to-end filter mechanism trace (§7.1); two-lane selector confirmation (§7.4); root-cause analysis for parent §6 finding (§14); ownership matrix (§18); silent-failure surface characterization (§14.2 + §10); consumer registry with STRONG / MISSING classification (§9).

**Anti-duplication per playbook §9 rule:** 13 of 28 canonical questions were already fully answered by S1273 §3.14 (Agent 5 map). This audit **cites** S1273 §3.14 for Q1 / Q2 (purpose/problem — §2 above), Q4 (models — §4), Q5 (services — §5), Q6 (API basics — §6), Q11 (research coverage), Q13 (drift subset). It does not re-answer.

---

## 13. Architecture Maturity

**Q12 — What is the architecture maturity?**

Per playbook §12: `EXPERIMENTAL` / `PARTIAL` / `WORKING` / `STABLE` / `CANONICAL`.

**Prod pgvector lane:** verdict **STABLE**. Retrieval mechanism is tested (regression tests: `test_rag_integration_search_embeddings.py`, `test_d14_min_session_autofill_guard.py`, `test_d15_similarity_threshold_default.py` per Agent 6). pgvector HNSW is production-grade. Consumers: PA (`kb_tool`), agent prompt injection, ~13 production files per KNOWLEDGE_RAG_MEMORY.md:60.

**Local Ollama keyword lane:** verdict **PARTIAL** (unchanged from S1273 §3.14). Token-overlap only; explicitly a dev-convenience lane; production code does not use it (KNOWLEDGE_RAG_MEMORY.md:65).

**Combined subsystem verdict:** **WORKING** (dropped from STABLE).

**Reason for drop:** Retrieval mechanism itself is sound, but the corpus governance surrounding it has completeness gaps that surface as silent zero-result queries. Specifically:

- `docs/_provenance.json` has 464 UNKNOWN-session entries out of 2156 total docs (per the file's `_meta.confidence_breakdown` — Agent 6 read the file directly).
- Corpus refresh cadence for row-edited documents is UNKNOWN — hash-delta gating in `refresh_docs_corpus` is not verified for edit detection.
- Provenance-index refresh has no beat cadence — manual only.
- Filter is silent-failure — no operator observability.

The subsystem "works" when its data is complete; the audit's finding is that operators cannot detect when data is incomplete.

**Parent §3D pre-classified §3.14 as STABLE prod + PARTIAL local.** This audit confirms both individual verdicts but adds the combined-subsystem "WORKING" classification to capture the corpus-completeness gap that neither individual verdict conveys.

---

## 14. Known Drift

**Q27 — What is drift? With evidence.**

### 14.1 Parent §6 anchor finding — root-cause analysis

**Symptom** (from `1300_memory_domain_scoping.md` §6, Chris-ratified 2026-07-01):

```
result_count: 0
filter:
  originating_session: 0
  pre_filter_count: 8
  excluded_mismatch: 1
  excluded_missing_provenance: 7
```

Two `search_docs` calls at S1300 open against OpsRun / MissionRunner / JobContract terms both returned this result. Semantic engine surfaced 8 candidates; provenance filter dropped all 8 (7 missing provenance + 1 mismatch). Operator saw 0 results.

**Root cause (verifier-loop-confirmed via `td_handlers_ops.py:78-127` + `td_handlers_ops.py:5468-5610` reads):**

The finding is a **local-lane corpus-completeness gap**, not a prod-lane retrieval bug. It arises from the intersection of four design choices that individually are reasonable and collectively produce silent zero-result queries:

1. **`search_docs` is hardcoded to the LOCAL keyword lane.** `td_handlers_ops.py:5502` imports `top_k` from `core.rag`. The prod pgvector lane is not consulted. So even if `DocumentEmbedding` rows exist for the query's semantic neighborhood, `search_docs` cannot see them.

2. **Provenance is external to chunks.** The local corpus chunk (`{file, chunk_id, text}` in `.rag/corpus.jsonl`) carries no session metadata. Session origin is looked up at query time from `docs/_provenance.json` by joining on the chunk's `file` path.

3. **Provenance-index has coverage gaps.** Direct read of `docs/_provenance.json` `_meta` block (`docs/_provenance.json:2-14`) yields, verbatim:
   ```
   "doc_count": 2156,
   "confidence_breakdown": {
     "HIGH": 1356,
     "MEDIUM": 336,
     "LOW": 0,
     "UNKNOWN": 464
   },
   ```
   Generated 2026-06-23T19:06:58+00:00; git_head `6bceca1e7a17`; `excludes: ["docs/archive/", "docs/docs-pattern/"]`. 464 / 2156 = **21.5% of indexed docs land in UNKNOWN confidence** (git history yielded no reliable session signal). Any chunk whose `file` path resolves to an UNKNOWN entry — or is missing from the index entirely — fails the filter as `excluded_missing_provenance`.

4. **Filter is "exclude by default" when metadata is missing.** `td_handlers_ops.py:82-85` docstring: *"search_docs treats 'no provenance for path' as 'exclude when filter is active', so a missing index degrades gracefully (filter just excludes everything, surfacing the regen hint to the user)."* This is Rigby's S1145 P2 spec — the conservative bias is intentional. The alternative ("include when metadata is missing") would produce false-positive cross-session leakage.

**Drift class:** `partial_implementation` — the filter mechanism is complete; the data model that powers it (external index, git-history-derived, incomplete) does not meet the filter's implicit precondition ("every chunk's file path exists in the index with a known session"). Per Agent 6 hypothesis classification: **HYP-1 (migration-incomplete) × HYP-4 (never-wired-into-ingestion)**.

**Why the 1 `excluded_mismatch`:** Of the 8 candidates, 1 chunk had a file path present in `docs/_provenance.json` with a known session, but that session did not equal Rigby's filter value. This is the filter working correctly — it's the "found provenance, session doesn't match" branch of `_filter_chunks_by_originating_session` at `td_handlers_ops.py:122-125`. That 1 is not a drift — it's expected behavior when a caller specifies a session other than the chunk's origin.

**Why the 7 `excluded_missing_provenance`:** Of the 8 candidates, 7 chunks had file paths that were EITHER (a) not in `docs/_provenance.json` at all, OR (b) in the index but with `originating_session: null` (the UNKNOWN confidence tier). Both cases collapse into the `excluded_missing_provenance` counter — the branch cannot distinguish them.

**Load-bearing consequence:** The operator cannot tell from the `excluded_missing_provenance` count alone whether the fix is (a) rebuild the provenance index (`build_docs_provenance` — case-a resolution), (b) run `--include-archive` / `--include-framework` if the excluded chunks are from the intentionally-excluded subtrees, (c) accept that 21% of the corpus is fundamentally UNKNOWN-session because git history doesn't record it, or (d) some combination. **The filter surface does not communicate the sub-classification.**

### 14.2 Silent-failure surface

Verifier-loop confirmed via direct read of `td_handlers_ops.py:5468-5610` **plus Rigby SIGN cycle grep** (2026-07-01, fresh pin `pa-a23736a833f646cf`) of `excluded_missing_provenance|excluded_mismatch|pre_filter_count` across the entire `core/` tree:

**Grep results (system-wide across `core/**/*.py`):**
- `core/services/td_handlers_ops.py:101, 5578, 5587-5589` — the handler itself (declaration + call site + response payload keys). This is where the counters are produced.
- `core/tests/test_search_docs_originating_session_filter.py:12, 14` — unit-test assertions on the counter names.
- **No other files matched.** No `logger.info` / `logger.warning` emitting the counters. No Prometheus `Counter` / `Histogram` reads. No alert rule or notification-wiring consumer.

Consequences by surface:

- **No log line** fires when `excluded_missing_provenance > 0`. `logger.error("[SEARCH_DOCS] error: ...")` at line 5609 fires only on exception path.
- **No metric emission across `core/`** — the counter names appear only in the handler + its test.
- **No alert / notification rule** for silent-drop patterns.
- **Counters live only in `result['filter']` payload** — visible only to the direct caller (the LLM turn or an operator who reads the tool response). Not persisted.

**Scope note (Rigby SIGN fold):** The system-wide grep covers `core/`. A broader search across the entire repo (`docs/`, `dbao/`, other apps) was not performed in this SIGN cycle. The load-bearing claim is **scoped to `core/` — the retrieval subsystem's home tree.** External consumers outside `core/` are extraordinarily unlikely to consume PA-tool-internal filter counters (no mechanism to reach the payload); the risk is negligible but explicitly acknowledged.

**Consequence:** The S1300 anchor finding surfaced only because Rigby ran the tool interactively and inspected the response. **A production PA turn that hits this filter class silently returns "no matching chunks" to the LLM, which then answers from training + conversation context without any indication that 7 semantically-matched chunks existed but were dropped.**

### 14.3 Additional drift matrix (beyond parent §6 anchor)

Per Agent 6 sweep, verifier-loop spot-checked. `docs_stale` / `partial_implementation` / `never_implemented` classes per playbook §12 finding-type enum.

| Drift | Doc claim | Runtime reality | Class | Severity | Evidence |
|-------|-----------|-----------------|-------|----------|----------|
| **D1 — lru_cache staleness after `build_docs_provenance`** | `KNOWLEDGE_RAG_MEMORY.md:103-104` (memory-rule mention: restart workers after regen) | `td_handlers_ops.py:78` `@lru_cache(maxsize=1)` — no invalidation hook; workers serve stale index until process restart | `docs_stale` (rule lives in memory, not in code / topic doc) | HIGH | Verifier-loop confirmed decorator at line 78; no cache-busting mechanism in `_load_provenance_docs` |
| **D2 — Filter counters observable in payload only** | Response-shape doc implies filter counters are diagnostic | Zero log / metric / alert consumption | `partial_implementation` | MEDIUM | §14.2 above |
| **D3 — Two provenance systems, no integration** | Migration 0044 provenance fields on `DocumentEmbedding` (row-level, ingested-at-write); `build_docs_provenance` provenance index (git-derived, computed-at-query) | Row-level fields populated by ingestion but not read by any RAG retrieval query path; git-derived index read only by local-lane filter; no bridge | `partial_implementation` | HIGH | `content/models.py:802-823` (fields defined); `td_handlers_ops.py:96-126` (filter reads external index only). Grep of `source_type\|ingested_via` on retrieval paths returned **zero hits** in `core/rag_integration.py`, `core/rag.py`, `core/services/scoped_retrieval.py` (Rigby SIGN cycle folded 2026-07-01 with explicit grep receipts — the 3 `source_type` hits in `core/services/td_handlers_ops.py` at lines 617, 691, 4842 are on other unrelated handlers, not RAG lanes). |
| **D4 — Local lane bypasses filter when called outside `search_docs`** | Parent scope implies both lanes participate uniformly | `core/rag.py:39-82` `top_k` has no filter parameter — direct callers of `core.rag.top_k` (management commands, tests, `core/codebase_awareness.py`) don't get provenance filtering | `partial_implementation` | LOW (no known prod callers) | `core/rag.py` signature; grep confirms filter only wraps `top_k` via `td_handlers_ops.py` |
| **D5 — Embedding refresh cadence UNKNOWN for edited docs** | S1273 §3.14 explicitly names cadence UNKNOWN | No PeriodicTask for Document embedding refresh; spider embeddings have 15-min backfill (S1273 §3.8) but doc-corpus does not; `refresh_docs_corpus` daily cascade has hash-delta gating (SPECULATIVE — edit-detection reliability not verified) | `partial_implementation` | MEDIUM | Agent 3 + Agent 6 grep for scheduled tasks; only `refresh_docs_corpus` schedule found |
| **D6 — Two-lane selector never implemented** | Playbook §12 §3.13 note: research question outstanding | `td_handlers_ops.py:5502` hardcodes `top_k` for `search_docs`; kb_tool handler routes to `search_embeddings`; no runtime selector | `never_implemented` | HIGH (LLM caller has no dynamic guidance) | Verifier-loop-confirmed; grep found no lane-switch logic |

### 14.4 Classification vs S1142 chunk-coverage gap

Per Agent 5 finding, the S1142 chunk-coverage gap (852 / 14,149 chunks per S1273 §3.13 known drift) is **NOT the same class** as parent §6:

| Finding | Class | Layer | Fix path |
|---------|-------|-------|----------|
| S1142 chunk-coverage gap | Ingestion-completeness | Corpus size | Full corpus sync (done at S1142 close: 0 → 852 docs → 14,149 chunks) |
| Parent §6 provenance-filter finding | Filter-completeness (via external index gap) | Provenance-index coverage | Rebuild + include-archive / include-framework flags OR accept UNKNOWN-session bias |

The audit tracks them as separate drift classes. Future arcs may find them related (both surface as "silent 0-results to caller") but the mechanisms differ.

---

## 15. Known Technical Debt

**Q26 — What is technical debt? With severity.**

Per Agent 6 debt matrix, verifier-loop-consolidated:

| Debt item | Location file:line | Severity | Introduced | Blocks | Enables |
|-----------|-------------------|----------|------------|--------|---------|
| **T1 — Two-module confusion (`rag.py` vs `rag_integration.py`)** | `core/rag.py` + `core/rag_integration.py`; naming similarity | MEDIUM | S1108-S1109 local; S1234 rag_integration pivot | Clear caller routing; onboarding | Local dev + prod isolation |
| **T2 — `lru_cache(1)` per-process staleness** | `td_handlers_ops.py:78` | HIGH | S1142 search_docs + S1145 P2 filter | Automatic cache management | Fast per-process access |
| **T3 — Embedding cadence UNKNOWN for `/docs/` edits** | No PeriodicTask; ad-hoc only | MEDIUM | Ongoing | Freshness guarantees | On-demand cost efficiency |
| **T4 — Local lane keyword-only quality delta** | `core/rag.py:39-69` | MEDIUM | S1108-S1109 (intentional dev tradeoff) | Using askdocs as prod-quality proxy | Offline / no-OpenAI-quota Q&A |
| **T5 — Two provenance systems, no bridge** | `content/models.py:802-823` (row-level) vs `docs/_provenance.json` (external) | MEDIUM | Migration 0044 (row-level); S1145 P2 (external) | Unified provenance semantics | Row-level: pipeline traceability; external: git-derived accuracy |
| **T6 — S1142 chunk-coverage baseline stale claim** | `KNOWLEDGE_RAG_MEMORY.md:71,176` (852 / 14,149 baseline; current UNKNOWN) | MEDIUM | S1142 baseline never re-measured | Knowing corpus health | Incremental backfill without gating |
| **T7 — Two-lane selector never built** | `td_handlers_ops.py:5502` hardcoded lane | HIGH | Ongoing | Dynamic lane selection based on query context / cost | Encapsulation under one tool namespace |
| **T8 — `RAGObservabilityService` ownership UNCLEAR** | `core/services/rag_observability_service.py:124-200`; `core/views_rag_observability.py` | MEDIUM | S954 introduction | Accountable telemetry evolution | Risk-aware scoring (critical-doc boost, context budget) |
| **T9 — Filter counters have no operator surface** | `td_handlers_ops.py:5585-5590` | MEDIUM | S1145 P2 | Automatic detection of silent-0-result queries | Caller-visible diagnostics on tool response |

Severity ranking per playbook §12: `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`. No `CRITICAL` items — the subsystem does not fail; it silently returns 0 in specific configurations.

---

## 16. Boundary Violations

**Q24 — What services violate boundaries?**

Per Agent 4 sweep, verifier-loop-consolidated. Boundary types per S1274 §7.

| Violation | Location | Severity | Nature |
|-----------|----------|----------|--------|
| **B1 — PA tool descriptions carry mechanism detail** | `pa_tool_schemas.py:4524-4566` (`search_docs` description mentions "core.rag.build_docs_context over .rag/corpus.jsonl") | LOW | Cosmetic — schema description leaks implementation. Fine for LLM guidance; would be a problem if any external consumer treated schema as stable contract |
| **B2 — BaseAgent imports `ScopedRetrievalService` directly** | `core/agents/base_agent.py:1587` | LOW (intentional per S1568) | No abstraction layer; retrieval backend changes force agent-side updates |
| **B3 — `_load_provenance_docs` reads a hardcoded relative path** | `td_handlers_ops.py:75` (`PROVENANCE_INDEX_PATH = Path("docs/_provenance.json")`) | LOW | Path is relative to cwd. Works because Django management commands run from repo root, but a caller invoking the handler from a different cwd could see the "missing file" branch fire |
| **B4 — Ingestion path (Category E) writes external file (`docs/_provenance.json`) consumed by retrieval path (Category D)** | Producer: `build_docs_provenance`; consumer: `_load_provenance_docs` | MEDIUM | Cross-category coupling via filesystem side effect. No integrity check; no schema contract; no versioning |

**No CRITICAL boundary violations.** No direct DB access bypassing service layer; no cross-domain internal imports of retrieval private methods; no unsafe pgvector access outside the retrieval service.

---

## 17. Duplicate or Overlapping Systems

**Q23 — What models overlap with other domains?**

Per Agent 1 schema comparison + S1273 §5.4 re-verification:

### 17.1 `DocumentEmbedding` vs `AgentKnowledgeSource`

| Aspect | `DocumentEmbedding` | `AgentKnowledgeSource` |
|--------|--------------------|-----------------------|
| Vector column | `embedding_vector` (pgvector, 1536D) | None |
| Content | `chunk_text` | `summary` + `key_insights` (JSONField) |
| Retrieval path | `rag_integration.search_embeddings` (cosine) | No direct RAG integration; agent-side prompt-injection reads it as structured knowledge, not chunks |
| Purpose | Semantic retrieval over document chunks | Cross-agent knowledge aggregation from spider data |

**Verdict:** **Not schema duplicates.** Different roles (chunks vs facts), different retrieval mechanisms. The S1273 §5.4 overlap flag lives at the **cognitive-load** layer (5+ memory stores for an operator to reason about) — not at the schema layer.

### 17.2 `DocumentEmbedding` vs `UserEmbedding`

| Aspect | `DocumentEmbedding` | `UserEmbedding` |
|--------|--------------------|-----------------|
| Vector column | `VectorField(dimensions=1536)` (pgvector) | `JSONField` (Python-side cosine) |
| Scope | Corpus-wide | Per-user |
| Purpose | RAG retrieval | Personal-memory retrieval |
| Consumer | `search_embeddings` | `search_personal_memories` at `core/rag_integration.py:328-439` |

**Verdict:** **Two vector storage substrates in the same domain module.** `rag_integration.py` reads from both. Divergence is real (per-user privacy scope vs corpus-wide) but the fact that one uses pgvector and one uses JSONField is a legacy split. This is **Category D × Category B (Personal / Adaptive Memory)** overlap surface — S1302 owns the persistence architecture question here; do not resolve in this audit.

### 17.3 Two RAG lanes (`rag.py` vs `rag_integration.py`)

- **`rag.py`** — 82 lines, local, keyword, JSONL corpus. Dev-lane.
- **`rag_integration.py`** — 466 lines, prod, pgvector, Django ORM. Prod-lane.
- **Shared:** the `Document` model conceptually; nothing at runtime storage.

**Verdict:** **Intentional lane split, but two-lane selector was never implemented** (per §7.4 + T7). This is the highest-value overlap concern for future design-preparation work. The audit does not recommend consolidation — this is scoping, not design.

### 17.4 Two provenance systems (row-level DocumentEmbedding fields vs `docs/_provenance.json`)

Per §14.3 D3 + T5. Two independent provenance representations that do not synchronize. Not a duplicate model, but a duplicate concept with divergent data. **Highest-priority follow-on candidate** for S1302 (Memory Persistence Architecture — the parent §5 "Categories A + B + C" child audit will inherit this question because "who writes what metadata when" is a persistence-architecture concern that reaches beyond retrieval).

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?**

Per Agent 6 ownership matrix, verifier-loop-consolidated:

| Surface | Current owner | UNCLEAR rationale | Impact |
|---------|--------------|------------------|--------|
| **Provenance semantics** (which chunk belongs to which session, and by what mechanism) | UNCLEAR | Two systems (row-level DocumentEmbedding fields + external `docs/_provenance.json`) exist without a naming authority. No doc names the primary system | Mismatched writer/reader expectations; drift class D3 |
| **Two-lane selector decision** | UNOWNED (research-only per playbook §12 §3.13) | Selector was never built. Would live between Category D (retrieval mechanism) and the PA tool layer (`unified_pa_entrypoint` + tool_dispatcher) — cross-category ownership | LLM caller has no dynamic guidance; two tools with overlapping-seeming names |
| **`RAGObservabilityService`** | UNCLEAR — Category D (RAG) or Group 1700 (Observability)? | Service name says "RAG" but its role (telemetry surface, critical-doc boost, context budget) is observability-flavored. Parent §3D scope includes it in Category D; the observability arc will want it | Changes may not coordinate with actual retrieval path |
| **Chunk-coverage remediation for S1142 baseline (852/14,149 vs current UNKNOWN)** | UNOWNED / backfill-implied | `backfill_spider_embeddings` handles spider sources on 15-min cadence; corpus edits handled ad-hoc via `sync_docs_index_to_documents --embed`. No standing monitor for coverage delta | Cannot detect if backfill has stalled |
| **Embedding refresh cadence policy** | UNOWNED | No PeriodicTask; on-demand only. No policy on (a) when a Document should be re-embedded, (b) staleness threshold, (c) refresh priority | Stale embeddings possible after doc edits |
| **`search_docs` filter surfacing to operator** | UNCLEAR (Category D vs Group 1700) | Counters exist; nobody owns making them operator-visible | Silent-failure class continues |
| **`docs/_provenance.json` build cadence** | UNOWNED (E-side per §3.15 or D-side per §3.14?) | Build command exists; no beat schedule. Parent §3D lists provenance filter mechanics under Category D but the *index-build* concern is closer to Category E docs corpus governance | Index goes stale silently; workers restart doesn't help if the file itself is out of date |

---

## 19. Recommended Future Research

**Q28 — What should be researched next? Ranked by architectural uncertainty × risk × unblocked flows.**

### 19.1 In-arc (Group 1300 child audits, cross-boundary questions this audit surfaces)

| Rank | Recommended child audit | Owned by | Why this audit surfaces it |
|------|-------------------------|----------|----------------------------|
| **1** | **S1302 Memory Persistence Architecture (Categories A + B + C)** — must own the row-level provenance semantics question | Group 1300 P2 | Provenance is a persistence-architecture concern that reaches beyond retrieval. DocumentEmbedding.source_type/ingested_via fields exist but no consumer; this is a broader "who writes what metadata when, and who reads it?" question that spans A/B/C. |
| **2** | **S1304 Documentation Corpus ↔ RAG Boundary (E ↔ D)** — must own the ingestion → retrieval provenance handoff | Group 1300 P4 | `docs/_provenance.json` is arguably an E-artifact consumed by D. Ownership belongs to whichever domain declares the schema — parent §3D suggests D; S1273 §3.15 governance framing suggests E. S1304 resolves. |
| **3** | **S1399 Group 1300 Canonical Summary** — must resolve the cross-cutting "provenance drift class" pattern if it recurs across P1 / P2 / P4 | Group 1300 P6 | If P2 and P4 also find provenance-writer / provenance-reader mismatches, S1399 should name the class explicitly rather than each child folding independently. |

### 19.2 Cross-arc follow-on

| Rank | Recommended arc | Owned by | Why |
|------|----------------|----------|-----|
| **1** | **Group 1700 Observability filter-drop telemetry** — event emission spec for `excluded_missing_provenance > 0` and `excluded_mismatch > 0` | Group 1700 | Silent-failure surface (§14.2) cannot be closed by Category D alone. Requires cross-arc event-emission ownership. |
| **2** | **Group 1400 Revenue** — if RAG-augmented content generation becomes a revenue path (currently no Content-Pipeline consumption per §9.1), integration lens joins Categories D + Content Pipeline + Revenue | Group 1400 | Not blocking — this is a MISSING inbound consumer surface that may become relevant to Group 1400 arc. |

### 19.3 Not-recommended (research anti-patterns per playbook §14.5)

- **Do not propose implementation of the two-lane selector here.** That is design-preparation-phase work. S1301 surfaces the gap; a future `authority: design-preparation` doc (post-S1399 synthesis) recommends a shape.
- **Do not propose consolidation of the two provenance systems here.** Same reason — surfacing the gap is this audit's job; recommending a specific consolidation is not.
- **Do not propose UI or CLI surfaces for filter counters.** Same reason.

---

## 20. Appendix

### 20.1 Files inspected

Grouped by sub-agent.

**Agent 1 (Models & Persistence):**
- `content/models.py:325-873` — Document + DocumentEmbedding
- `core/models/users/models.py:886-976` — UserEmbedding
- `core/models_unified_system.py:521-628, 15558-15689, 19099-19250` — AgentKnowledgeSource + ContentProvenance + DataProvenance
- `content/migrations/0037_session_730_pgvector_documentembedding.py:35-43` — HNSW index
- `content/migrations/0040_documentembedding_hnsw_index_state.py:19-26` — ORM sync
- `content/migrations/0044_provenance_and_promotion.py:29-62` — provenance fields
- `content/embeddings.py:45-63, 600-696` — provenance derivation + processor
- `core/tasks_agents.py:4205-4224, 4272-4292, 4333-4353` — backfill embedding writers

**Agent 2 (Services & Runtime Flows):**
- `core/rag_integration.py:1-466` — prod lane full file
- `core/rag.py:1-82` — local lane full file
- `core/services/td_handlers_ops.py:78-127, 5460-5610` — filter mechanism + handler
- `core/services/embedding_service.py:66-407` — EmbeddingService (partial)
- `core/services/scoped_retrieval.py:75` — ScopedRetrievalService.search (referenced)
- `core/services/rag_observability_service.py:124-200` — RAGObservabilityService (partial)

**Agent 3 (APIs / Tools / Tasks / Commands):**
- `core/services/pa_tool_schemas.py:56, 4524-4566, 4568+` — brainstorm_tool + search_docs + kb_tool schemas
- `core/services/td_handlers_ops.py:5202, 5379-5428, 5468` — kb_tool + search_docs handlers
- `core/tasks.py:5803` — refresh_docs_corpus beat task
- `core/management/commands/build_docs_index.py:46`
- `core/management/commands/build_rag_corpus.py:56`
- `core/management/commands/sync_docs_index_to_documents.py:55`
- `core/management/commands/build_docs_provenance.py` (all)
- `docs/AUDIT_FINDINGS.md` §12 — canonical Celery deferred list re-cite

**Agent 4 (Integrations):**
- `core/services/td_handlers_ops.py:5202, 5468` — PA handlers (STRONG inbound)
- `core/agents/base_agent.py:1435-1609` — BaseAgent 3-source retrieval (STRONG inbound)
- `core/agent_router.py:2254-2256` — agent router enrichment (WEAK inbound)
- `core/services/content*.py` — grep 0 hits for RAG imports (MISSING inbound)
- `core/employees/mission_runner.py` — grep 0 hits for RAG consumption (MISSING inbound)
- `core/jobs/docs_cascade.py:352-376` — 4-step cascade orchestration (STRONG ingestion producer)
- `core/services/unified_pa_entrypoint.py` — grep 0 hits for RAG imports (PA turn enrichment tool-call-only)

**Agent 5 (Docs & Prior Research):**
- `docs/KNOWLEDGE_PIPELINE.md`
- `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`
- `docs/topics/personal-assistant.md`
- `docs/topics/local-askdocs.md`
- `docs/PLATFORM_WHAT_IT_IS.md`
- `docs/DATABASE_MODEL_REFERENCE.md`
- `docs/research/platform_architecture_inventory.md` §3.13, §3.14, §3.15, §5.4
- `docs/research/platform/cross_domain_integration_audit.md` §2.5 (line 300-302)
- `docs/handoffs/SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md`

**Agent 6 (Drift / Debt / Ownership / Maturity):**
- `docs/_provenance.json` — direct read of `_meta.confidence_breakdown` (1356 HIGH / 336 MEDIUM / 0 LOW / 464 UNKNOWN = 2156 total; generated 2026-06-23; 1034674 bytes)
- `td_handlers_ops.py:78-93, 5563-5590, 5609` — filter + logger for silent-failure characterization
- `core/rag.py:39-69` — local-lane signature confirms no filter param
- `core/services/rag_observability_service.py:124-200` — partial read for ownership assessment

**Parent-agent (Claude) verifier-loop reads:**
- `core/services/td_handlers_ops.py:60-160` (Read tool) — imports, PROVENANCE_INDEX_PATH constant, `_load_provenance_docs`, `_filter_chunks_by_originating_session` — confirms mechanism claims
- `core/services/td_handlers_ops.py:5460-5620` (Read tool) — `_handle_search_docs` full body — confirms `search_docs` runs `core.rag.top_k` (local keyword lane), filter is opt-in via `originating_session`, counters embedded in `result['filter']`, only exception path logs

### 20.2 Docs inspected (companion anchors + related traversed)

- `docs/research/domains/memory/1300_memory_domain_scoping.md` — parent doc, all sections
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` — §5, §6, §7, §9, §11, §13, §14, §15, §16
- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` — §0-§5 (bootstrap + classify)
- `docs/research/ARCHITECTURE_INDEX.md` — §1 preamble + §1.13 parent doc row + §1.14 OS row
- `docs/research/OPEN_ARCS.md` — Group 1300 in-progress row
- `docs/research/platform_architecture_inventory.md` — §2 cluster map, §3.13/§3.14/§3.15 rows, §5.4 overlap flag
- `docs/research/platform/cross_domain_integration_audit.md` — Category D consumer classifications
- `docs/AUDIT_FINDINGS.md` §12 — Celery deferred list (cross-ref for `rag_retrieval_canary`)
- `CLAUDE.md` + `MEMORY.md` — session workflow + auto-memory rules

### 20.3 Grep patterns used

Reproducible search queries used across the sweep:

- `originating_session` — 8 hits (all in td_handlers_ops.py + pa_tool_schemas.py)
- `_filter_chunks_by_originating_session` — 2 hits (declaration + call site)
- `_load_provenance_docs` — 3 hits (declaration + docstring reference + call site)
- `excluded_missing_provenance` — 3 hits (in-code counter + parent §6 + this audit)
- `PROVENANCE_INDEX_PATH` — 4 hits (declaration + branches)
- `build_docs_provenance` — 7+ hits across mgmt commands + docs + memory rules
- `CosineDistance` — hits localized to `rag_integration.py`
- `HnswIndex` — 1 hit (`content/models.py:833-836`)
- `search_docs` — many hits (schema, handler, docs, memory rules)
- `kb_tool` — many hits (schema, handler, tests)
- `ScopedRetrievalService` — hits in scoped_retrieval.py + base_agent.py + agent_router.py
- `RAGObservabilityService` — hits localized to `rag_observability_service.py` + views_rag_observability.py

### 20.4 Unresolved unknowns (per playbook §14 rule — legitimate finding, not guessing)

- **UNKNOWN — current chunk coverage as of S1301.** S1142 baseline was 852 / 14,149; no standing metric measures current state. Only manual `.rag/corpus.jsonl` line count would resolve.
- **UNKNOWN — RAGObservabilityService full role.** Parent-agent verifier read only lines 124-200 (partial). Whether it consumes `search_docs` filter counters is not confirmed by direct read.
- **UNKNOWN — `refresh_docs_corpus` hash-delta edit-detection reliability.** Task source (`core/tasks.py:5803`) not fully re-read; whether hash-delta correctly triggers re-embedding on file-content edits (not just new file additions) is unverified.
- **UNKNOWN — count of production callers of `core.rag.top_k` outside `search_docs` handler.** Agent grep found `codebase_awareness.py` + `views/main.py` as callers; whether these are dead / test-only / production is not classified.
- **UNKNOWN — precise line count of `ScopedRetrievalService.search` and its interior.** Only the `search` method entry at `core/services/scoped_retrieval.py:75` was cited; the class body was not read by any sub-agent.

### 20.5 Conflicts between sources (parent-agent resolutions)

- **`search_docs` runs prod pgvector vs LOCAL keyword lane.** Parent doc §3D lists prod-plus-local as scope surface without distinguishing which tool runs which. Verifier-loop resolved by direct read of `td_handlers_ops.py:5502`: **`search_docs` = LOCAL keyword lane; `kb_tool` = PROD pgvector lane.** This is a scoping precision, not a contradiction — parent scope was correct to include both; the specific tool-to-lane mapping needed re-verification.
- **`excluded_missing_provenance` mechanism.** Agent 1 initial pass suggested NULL `DocumentEmbedding.source_type` rows might drive the counter. Verifier-loop-corrected: migration 0044 uses `default='unknown'` so no NULL rows exist; the counter is driven by **missing entries in `docs/_provenance.json` (external file), not NULL rows in DocumentEmbedding.** Agent 1's initial framing appears in the final matrix as clarified in §14.1.

### 20.6 Verifier-loop corrections

- Sub-agent Agent 1 initially framed provenance drift as row-level NULL; parent-agent corrected via direct read of migration 0044 to distinguish row-level (CharField default 'unknown') from external-index (file path missing / null session).
- Sub-agent Agent 2's `HYP-1` (docs/_provenance.json not rebuilt) and `HYP-2` (intentionally-excluded subtrees) both fit the evidence; §14.1 synthesizes both without collapsing.
- Sub-agent Agent 4 initially classified the S1274 §2.5 citation as line 300-302 without direct re-read; parent-agent kept the cite but flagged it as sub-agent-provided in this audit's §20.1 provenance list.

### 20.7 Rigby SIGN fold notes

**Cycle 1 — 2026-07-01, fresh isolation pin `pa-a23736a833f646cf`.**

Provisional verdict: **SIGN-with-edits (4 must-fix + 6 nice-to-have)**
pending grep-verification of claims 5-8 that Rigby could not close in
her pin due to `repo_tool` file-size caps on `docs/_provenance.json`
(1.03 MB) and time-bounded grep budget.

**Rigby's independent verifications in-pin:**
- Claim 1 (search_docs = local keyword lane) — **CONFIRMED** via direct read of `core/services/td_handlers_ops.py:5468-5520` (import at :5502, call at :5518, docstring contrast at :5472-5475).
- Claim 2 (filter design: missing provenance = exclude) — **CONFIRMED** via direct read of `_load_provenance_docs` docstring at `td_handlers_ops.py:80-86` + filter logic at `:99-126`.
- Claim 3 (kb_tool bypasses provenance filter) — **CONFIRMED** via grep: only call site of `_filter_chunks_by_originating_session` is `_handle_search_docs` at `td_handlers_ops.py:5579`.

**Parent-agent grep-verification of Rigby's UNVERIFIABLE claims (4-8):**
- Claim 4 (2156 denominator + 21% UNKNOWN) — **CONFIRMED** via direct read of `docs/_provenance.json:2-14`; folded into §14.1 with verbatim `_meta` block quote.
- Claim 5 (row-level fields not read by retrieval paths) — **CONFIRMED** via targeted greps in retrieval-path files (0 hits in rag_integration.py / rag.py / scoped_retrieval.py; 3 hits in td_handlers_ops.py at lines 617/691/4842 are on other unrelated handlers, not RAG lanes); folded into §14.3 D3.
- Claim 6 (MISSING inbound consumers) — **CONFIRMED (grep-scope-bounded)** via grep of `kb_tool|search_docs|search_embeddings|ScopedRetrievalService|rag_integration|core\.rag` returning zero files matched in each named file/directory; folded into §9.1 with hedging that the grep is scoped to the listed symbols on the listed paths.
- Claim 7 (unified_pa_entrypoint no RAG imports) — **CONFIRMED** via grep of `unified_pa_entrypoint.py`: 0 matches. Folded implicitly (§9.3 claim stands as written).
- Claim 8 (silent-failure surface) — **CONFIRMED (`core/` tree-scoped)** via grep of `excluded_missing_provenance|excluded_mismatch|pre_filter_count` across `core/**/*.py`: 2 files match (handler + its test). Folded into §14.2 with explicit tree-scope note; broader repo grep not performed.

**Must-fix edits folded:**
- **MF1 (§14.1 denominator citation)** — replaced narrative "~21%" with verbatim `_meta` block + `docs/_provenance.json:2-14` cite + explicit arithmetic.
- **MF2 (§14.3 D3 grep evidence)** — added targeted-grep receipts for retrieval-path files; annotated the 3 same-name hits in td_handlers_ops.py as unrelated to RAG.
- **MF3 (§9.1 MISSING scoping)** — hedged each MISSING classification to the specific grep scope (path + symbol set); added Content Pipeline provenance-tracking note referencing `ContentProvenance` as an out-of-scope adjacent surface.
- **MF4 (§14.2 silent-failure scope)** — added system-wide grep receipts + explicit `core/`-tree-scope disclaimer.

**Nice-to-have edits addressed in fold:**
- **NH1 (binary language hedging)** — partial fold: Content Pipeline / Signal Engine / silent-failure claims now scope-bounded with grep receipts. Not all binary phrasings audited; the remaining hedging is deferred as a §19 audit-hygiene follow-on.
- **NH2-NH6** — not addressed in this fold cycle; Rigby's second-pass verdict will name whether they block canonical status.

**Cycle 1 close — 2026-07-01, fresh isolation pin `pa-a23736a833f646cf`.**

**Final verdict: SIGN-clean.**

Rigby's re-review, in-pin, confirmed:
- All 8 numbered load-bearing claims — CONFIRMED via direct read + grep receipts.
- All 4 must-fix folds (MF1 denominator citation, MF2 grep evidence for D3, MF3 MISSING scope hedging, MF4 silent-failure tree-scope) — verified as folded.
- Nice-to-have items NH2–NH6 — all deferrable / non-blocking; correctness of the audit is not affected by deferring.

**Additional risks surfaced during Rigby's re-review (recorded, not fold-blocking):**
- **Counter-name coupling meta-risk.** The "no consumer" proof (§14.2) is keyed on grep for specific counter names (`excluded_missing_provenance`, `excluded_mismatch`, `pre_filter_count`). A future refactor renaming these keys would make the grep proof stale without any change to the underlying silent-failure reality. Verification-method meta-risk, not an audit flaw.
- **Join fragility.** §7.3 correctly names the highest-leverage operational failure mode: path normalization between `.rag/corpus.jsonl` (produced by `build_rag_corpus`) and `docs/_provenance.json` (produced by `build_docs_provenance`) is not enforced by any integrity check. Rigby confirmed this stands as the sharpest operational edge.

**Ratification path per playbook §16:** Rigby SIGN-clean is a completed review, not a canonicalization signal. Chris commit-gate flips `status: draft` → `active` on merge. Fresh isolation pin `pa-a23736a833f646cf` may retire at Chris's discretion after commit.
