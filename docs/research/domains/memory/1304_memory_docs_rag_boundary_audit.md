---
title: "Memory Domain (Categories E ↔ D) — Documentation Corpus ↔ RAG Boundary Audit"
status: draft
authority: research
session_added: 1304
research_group: 1300
child_slot: P4
domain_slug: memory
date: 2026-07-01
last_verified: 2026-07-01
supersedes: none
sign_status: SIGN-clean (cycles 1 + 2 complete — Rigby verified folds #1-#4 independently on `pa-2614a91a920642fa`)
scope_discipline: |
  BOUNDARY LENS ONLY. This audit is smaller than P1-P3 per parent §5
  P4 rationale ("smaller scope; benefits from §3.14 audit landing
  first"). It does NOT re-audit Category D internals (S1301 owns).
  It does NOT re-audit Category E docs corpus internals (belongs to
  a future Cat E arc if warranted). It focuses on the BOUNDARY: how
  does the corpus become RAG-visible? Where does ingestion hand off
  to retrieval? Where do the two provenance systems (external
  `_provenance.json` vs row-level `DocumentEmbedding.source_type` +
  `ingested_via`) disagree, and what routes read which?
related:
  - docs/research/domains/memory/1300_memory_domain_scoping.md              # parent (P0)
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md   # sibling (P1 — Cat D)
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md   # sibling (P2 — Cat A+B+C)
  - docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md   # sibling (P3 — Cat F)
  - docs/research/domains/memory/1301_followup_provenance_classifier_bug.md   # provenance classifier follow-up (S1301 → PR #2776)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                # process framework (v2)
  - docs/research/ARCHITECTURE_INDEX.md                                      # library navigation (v15 → v16)
  - docs/research/OPEN_ARCS.md                                               # cross-arc live manifest
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                       # OS §0–§9
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                               # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                              # narrative anchor
  - docs/research/platform_architecture_inventory.md                         # 32-domain map (S1273 §3.14 + §3.15)
  - docs/research/platform/cross_domain_integration_audit.md                 # integration lens (S1274)
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                      # inventory-wins-on-conflict discipline (§2c Cat E governance)
  - docs/KNOWLEDGE_PIPELINE.md                                               # runtime flow map (spider → embed → knowledge → agent prompt)
  - docs/narratives/KNOWLEDGE_RAG_MEMORY.md                                  # S1158 comprehensive narrative
  - docs/topics/local-askdocs.md                                             # S1108 LOCAL vs PROD lane boundary
dependencies_on:
  - group: 1300
    slug: memory
    role: "Parent §5 P4 locks E↔D boundary lens. S1301 §14.2 (21.5% coverage gap in provenance filter) + §19 (downstream routing including row-level orphan-write pattern of `DocumentEmbedding.source_type` + `ingested_via` populated at ingestion but never read by retrieval) are load-bearing evidence anchors. S1301 §19 D3 hypothesis IS PARTIALLY INVALIDATED by S1304 verifier loop: `source_type` HAS an owner-model-qualified consumer at `content/embeddings.py:965-973` (semantic_search_sync source_filter branch) + presentation at :1007; only `ingested_via` remains genuinely orphan (F1-CANDIDATE). S1302 §17.3 (name-collision resolution as boundary methodology — Django `ConversationMemory` = Cat B vs in-process `ConversationMemory` = Cat F) MUST hold as the pattern for any name-collision surfaced here. S1303 §9 (Cat F ↔ Cat D OBSERVED GAP) + §19 R3 (turn-context → RAG enrichment design proposal) are the load-bearing design-hypothesis input — S1304 decides whether the wiring gap is intentional separation (design choice) or genuine drift (bug)."
delegates_to: none
delegated_from: none
verifier_loop: |
  v0.4 draft SIGN-clean (2026-07-01, S1304 close cycle 2):
  Rigby returned SIGN-clean on fresh SIGN isolation pin
  `pa-2614a91a920642fa` after cycle 2 verification pass. She
  independently verified fold #1 (D6 beat-schedule positive
  citation quoting `core/celery.py:495-499` + call sites at
  `core/tasks.py:5900-5902`), fold #2 (§18 Documentation Manager
  JobContract evidence at `core/employees/jobs.py:187-395` +
  registration `:1336` + refined ownership matrix + softened
  bounded-language), fold #3 (§9 D→E cell + §14 D7 F4-CANDIDATE
  hedge on `ingested_via` — no residual bare 'never read'), fold
  #4 (§17 'complementary today does not imply optimal' guardrail
  + unification-vs-scoping paths + §19 R2 routing). Bonus
  check at `content/embeddings.py:904` (async-path SearchResult
  presentation citation) flagged as nice-to-have, NOT SIGN-blocking
  — current `:965-973` + `:1007` citations are sufficient. Cycle 2
  was a verification pass, not a structural rewrite — no additional
  edits required. Cycle 2 outcome: **SIGN-clean**. Frontmatter
  `sign_status:` flipped to SIGN-clean; §20.10 gating checklist
  cycle 2 box ticked. Remaining gate: Chris commit-gate per
  playbook §16.
  v0.3 draft with SIGN cycle 1 folds applied (2026-07-01, S1304 open):
  Rigby returned SIGN-with-edits on fresh SIGN isolation pin
  `pa-2614a91a920642fa` after independent verification of load-
  bearing claims 1-5. She grep-verified claim 1 (source_type has
  owner-model-qualified consumer) using her own repo_tool reads +
  found an additional consumer citation at `content/embeddings.py:904`
  (async-path SearchResult presentation) that S1304 v0.2 missed.
  Four must-fix folds returned + folded in place per S1303
  discipline: (1) beat-schedule positive citation for D6 — added
  `core/celery.py:495-499` sole `refresh-docs-corpus-daily` entry
  quote showing no `build_docs_provenance` companion + call-site
  citations at `core/tasks.py:5900-5902`; (2) §18 UNOWNED reframed
  with Documentation Manager `JobContract` positive evidence at
  `core/employees/jobs.py:187-395` (registered `:1336` as
  `docs_manager`, employee_handle=`rigby`, `mission_run_kind=
  docs_cascade`) — cascade steps 1-4 ARE owned; four specific
  boundary-maintenance responsibilities (provenance rebuild,
  cache invalidation, filter observability, row-level
  reconciliation) remain "no explicit named runtime owner";
  softened "CRITICAL" → "HIGH" per playbook §12 bounded language;
  (3) F4-CANDIDATE discipline reinforced on `ingested_via` — §9
  D→E edge cell rewritten to hedge, §14 D7 explicit F4-CANDIDATE
  hedge added, no bare "never read" language remaining on
  `ingested_via`; (4) §17 "complementary" reframe augmented with
  explicit "does not imply optimal" guardrail + unification-vs-
  scoping design-decision routing to §19 R2. Cycle 2 verification
  pass pending — target SIGN-clean.
  v0.1 draft skeleton (2026-07-01, S1304 open):
  Skeleton scaffolded after Chris ratified D12 (PROCEED) + D13
  (RETAIN pa-aa54193f240f4846) via arc pin.
  v0.2 draft with sweep evidence + verifier loop (2026-07-01, S1304 open):
  6-parallel Explore sweep completed. Verifier loop applied
  independent file:line reads on load-bearing claims per playbook
  §14. Four claims verified: (1) Agent 1 partial-invalidation of
  S1301 §19 D3 confirmed via `content/embeddings.py:931-1029`
  direct read — `source_type` IS read at :971-973 (source_filter
  branch in semantic_search_sync) + :1007 (SearchResult
  presentation); (2) Agent 3 `search_docs` handler location at
  `td_handlers_ops.py:5468` confirmed (S1301's :5502 cite is the
  inline `from core.rag import top_k` import at line 5502 within
  the handler — both correct at different granularity, no drift);
  (3) Agent 2 + Agent 6 no-beat-schedule for `build_docs_provenance`
  confirmed via grep — 3 files reference the command
  (`td_handlers_ops.py` suggests it in error path,
  `build_docs_provenance.py` is the command itself,
  `backfill_doc_provenance.py` is a separate mgmt command); zero
  refs in `core/tasks.py`, `core/celery.py`, or beat schedule
  config; (4) Agent 4 zero RAG imports in
  `unified_pa_entrypoint.py` confirmed via grep on
  `search_docs|kb_tool|semantic_search|search_embeddings` — 0
  matches. F4-CANDIDATE discipline (S1303 §14) enforced: no dead-
  code claim made without owner-model-qualified consumer inventory.
  §1 executive summary + §14 known-drift + §17 duplicate/overlap +
  §18 ownership + §19 future research populated. Skeleton
  §2/§3/§4/§5/§6/§7/§8/§9/§10/§11/§12/§13/§15/§16 folded from Agent
  1-6 evidence with §14 evidence rules honored.
owner: claude (drafted S1304 v0.1 → folded to v0.2)
---

# Memory Domain (Categories E ↔ D) — Documentation Corpus ↔ RAG Boundary Audit

> **What this doc is.** The fourth child audit under Research Group
> 1300 (Memory / Knowledge / Embeddings). Boundary lens between
> Category E (Documentation / Research Knowledge System — S1273
> §3.15) and Category D (RAG / Document Loading — S1273 §3.14 +
> S1301 P1 audit). Not a re-audit of either category's internals.
>
> **What this doc is not.** A re-audit of Cat D (S1301 owns) or Cat
> E internals. An implementation proposal. A design specification.
> This is boundary-integration research whose deliverable is
> evidence about how corpus content becomes retrieval-visible, and
> what breaks or drifts at that handoff.

---

## 1. Executive Summary

The Documentation Corpus ↔ RAG boundary is **FUNCTIONAL but UNMATURE**
(per playbook §12: PARTIAL maturity, not WORKING or STABLE). Core
mechanisms work: (a) the 4-step ingestion cascade
(`build_docs_index` → `build_rag_corpus` →
`sync_docs_index_to_documents` → `embed_documents`) runs daily via
the `refresh_docs_corpus` beat task at 04:00 Denver time
(`core/tasks.py:5803` — verified by Agent 2 + Agent 3); (b) two
retrieval lanes exist and are wired to the corpus without ambiguity
(`search_docs` → LOCAL keyword via `core.rag.top_k` at
`td_handlers_ops.py:5502`; `kb_tool semantic_search` → PROD pgvector
via `core.rag_integration.search_embeddings`); (c) the provenance
filter mechanism is logically sound and correctly implements the
S1301 §14 "missing provenance = exclude by design" contract.

**Five boundary gaps emerged:**

- **G1 — Two provenance systems partially decoupled** (S1301 §19 D3
  refined). External `docs/_provenance.json` (git-history-derived,
  read by `search_docs` filter) and row-level
  `DocumentEmbedding.source_type` + `ingested_via` (migration 0044,
  populated at ingestion) coexist. S1301 §19 D3 hypothesized both
  row-level fields are orphan-writes. **S1304 verifier-loop
  invalidates half of that hypothesis:** `source_type` HAS an
  owner-model-qualified consumer at `content/embeddings.py:965-973`
  (source_filter branch: `internal_only` / `external_only`) +
  presentation at `:1007`. Only `ingested_via` remains genuinely
  F1-CANDIDATE orphan — all 3 write-sites use fixed string
  constants (`'sync_docs'`, `'backfill'`, `'unknown'`) and no read
  path is qualified against `DocumentEmbedding`. Neither system
  synchronizes with the other; they encode different provenance
  semantics (session origin from git vs source-of-record enum from
  ingestion).

- **G2 — Provenance index rebuild unscheduled**. `build_docs_provenance`
  is load-bearing for the retrieval filter but has zero beat
  entries (verifier grep 2026-07-01: 3 refs — the command file, the
  filter's error-path suggestion, and a sibling backfill command;
  zero in `core/tasks.py`, `core/celery.py`). The daily
  `refresh_docs_corpus` cascade does NOT rebuild provenance. Result:
  provenance index staleness between manual runs is silent and
  undetectable. 464 UNKNOWN entries / 2156 docs (21.5%, per S1301
  §14.2) are the current-state gap; new docs added between manual
  provenance rebuilds inherit UNKNOWN by default.

- **G3 — `lru_cache(1)` staleness at boundary**. `_load_provenance_docs()`
  at `td_handlers_ops.py:78-93` caches the provenance dict
  per-process indefinitely. When `build_docs_provenance` writes a
  new `docs/_provenance.json`, running celery workers do not
  reload it until process restart. Combined with G2, this makes
  the retrieval-side provenance surface stale by two independent
  paths (index unrefreshed on disk + cached in memory).

- **G4 — Filter counters land in response payload only** (S1301
  §14.2 confirmed). `excluded_missing_provenance` +
  `excluded_mismatch` at `td_handlers_ops.py:5585-5590` are visible
  only to callers who inspect the tool response. No log, metric, or
  alert. S1300 §6 parked finding surfaced this by manual
  inspection, not observability.

- **G5 — Boundary is unowned**. Category E has implicit governance
  ownership (Chris + Claude Code via `DOC_LIFECYCLE.md`); Category D
  has implicit retrieval ownership (`search_docs` + `kb_tool`
  handlers). The E↔D handoff itself — who owns provenance-index
  freshness, cache invalidation, cascade-completion signals — has
  no explicit owner. The four preceding gaps exist *because* the
  boundary has no owner to reconcile them.

**Cat F ↔ Cat D reframe:** S1303 §9 OBSERVED GAP + §19 R3 turn-
context → RAG enrichment hypothesis. Evidence entering S1304 is
mixed: three signals tilt intentional-separation (design discipline
in the 8 enrichment services, tool-call-only pattern with two
first-class PA tools, conceptual scope separation between thread
memory and source memory); three signals tilt drift (no design
comment, no feature flag guarding the absence, asymmetry with
BaseAgent's `_get_relevant_knowledge_for_task`). **S1304 verdict:**
this is a design-decision boundary, not a bug fix — routed to §19
R5 as a hypothesis-decision request, not a wiring PR.

**Biggest gaps to research next (§19):** (R1) full-tree owner-model
verification of `ingested_via` orphan status per S1303 §14
F4-CANDIDATE discipline; (R2) provenance-system reconciliation
design (unify row-level + external, or explicitly bound their
scopes); (R3) rebuild cadence + cache invalidation design (add
provenance to the daily cascade OR move to Redis with TTL); (R4)
boundary ownership assignment (S1399 canonical summary should name
an owner or steering committee); (R5) turn-context → RAG enrichment
design decision (routed from S1303 §19 R3 — verdict: intentional or
drift, decided in design-preparation phase, not this audit).

## 2. Domain Purpose

**Q1 — What is the E↔D boundary for?**

The E↔D boundary exists to convert documentation stored on-disk
under `docs/` into a form the RAG retrieval layer can query at
runtime. It has two responsibilities:

1. **Corpus ingestion**: transform markdown files into structured
   corpus artifacts (`docs/_index.json`, `.rag/corpus.jsonl`,
   `Document` rows, `DocumentEmbedding` rows with pgvector).
2. **Provenance materialization**: annotate the corpus with
   attribution metadata (session origin, git-history signals,
   source-of-record enum) so retrieval can filter/rank.

The boundary is inherently bidirectional in intent — E "publishes"
corpus + provenance; D "consumes" them — but in practice today the
two sides synchronize incompletely (see §14 D2 + G2).

**Q2 — Who owns the boundary?**

**No explicit owner** (see §18). Category E is implicitly governed
by `DOC_LIFECYCLE.md` (Chris + Claude Code); Category D handlers
live in `td_handlers_ops.py` (also implicitly Chris + Claude Code).
The boundary itself is unowned; no `AIEmployee` handle in
`core/employees/jobs.py` binds to the E↔D handoff (Agent 6 §4
verified).

## 3. Canonical Entry Points

**Ingestion side (Category E, boundary-facing):**

| Entry | File:line | Role |
|-------|-----------|------|
| `build_docs_index` | `core/management/commands/build_docs_index.py:46-1113` | Scans `docs/`, builds `docs/_index.json` + `docs/INDEX.md`. Step 1 of cascade. Frontmatter parsing + link graph. |
| `build_rag_corpus` | `core/management/commands/build_rag_corpus.py:89-179` | Reads `_index.json`, writes `.rag/corpus.jsonl` (fixed 1200-char chunks). Step 2. |
| `sync_docs_index_to_documents` | `core/management/commands/sync_docs_index_to_documents.py:55-435` | Reads `_index.json`, upserts `Document` rows. Step 3. Enrichment fields (S1234 D9): category, tags, document_class, is_pinned, retrieval_boost. |
| `embed_documents` / `--embed` flag | `core/management/commands/embed_documents.py:14-71` + `sync_docs_index_to_documents.py:355-406` | Generates `DocumentEmbedding` rows (chunk + OpenAI embedding + pgvector). Step 4. |
| `build_docs_provenance` | `core/management/commands/build_docs_provenance.py:119-451` | Builds `docs/_provenance.json` from git history + frontmatter overrides. Separate materialization; **NOT part of `refresh_docs_corpus` beat**. |
| `verify_doc_claims` | `core/management/commands/verify_doc_claims.py:49-166` | Runs doc-vs-reality drift verifier (S1099). Boundary-adjacent — verifies doc claims against runtime, not part of ingestion. |

**Retrieval side (Category D, boundary-facing):**

| Entry | File:line | Role |
|-------|-----------|------|
| `_handle_search_docs` | `core/services/td_handlers_ops.py:5468` | PA tool handler for LOCAL keyword lane. Imports `core.rag.top_k` inline at line 5502. Applies `originating_session` provenance filter via `_load_provenance_docs()` (lines 5566-5590). |
| `_handle_kb_browse` / `kb_tool semantic_search` | `core/services/td_handlers_ops.py:5202` + `5379` | PA tool handler for PROD pgvector lane. Calls `rag_integration.search_embeddings()`. No provenance filter. |
| `_load_provenance_docs` | `core/services/td_handlers_ops.py:78-93` | `@lru_cache(maxsize=1)` load of `docs/_provenance.json`. Per-process cache; no invalidation. |
| `_filter_chunks_by_originating_session` | `core/services/td_handlers_ops.py:5579-5581` | Applies session filter post-ranking. Emits `excluded_missing_provenance` + `excluded_mismatch` counters into response payload. |
| `core.rag.top_k` | `core/rag.py:1-81` | Token-overlap ranker over `.rag/corpus.jsonl`. LOCAL lane. |
| `core.rag_integration.search_embeddings` | `core/rag_integration.py:1-465` | Pgvector cosine similarity over `DocumentEmbedding`. PROD lane. |

**Beat schedule:**

| Task | Schedule | Steps covered | Steps NOT covered |
|------|----------|---------------|-------------------|
| `refresh_docs_corpus` | `crontab(hour=4, minute=0)` Denver daily (`core/tasks.py:5803`) | Steps 1-3 + fans out step 4 embedding tasks | **build_docs_provenance is NOT included** — provenance rebuild is manual-only. |

## 4. Major Models

**Boundary-relevant model set:**

| Model | File:line | Fields relevant to boundary | Ownership | Notes |
|-------|-----------|-----------------------------|-----------|-------|
| `Document` | `content/models.py:325-705` | `file_path`, `raw_content`, `processed_content`, `content_hash`, `category`, `tags`, `document_class`, `is_pinned`, `retrieval_boost`, `source_system`, `source_url`, `promotion_status`, `data_sensitivity`, `extracted_metadata` | Cat E (owned by content app; owner FK line 483) | 21 indexes including `is_critical`, `risk_level`, `data_sensitivity`. 588 concrete models across the platform; Document is the corpus-side surface. |
| `DocumentEmbedding` | `content/models.py:707-918` | `document (FK)`, `embedding_model`, `chunk_index`, `chunk_text`, `embedding_vector` (pgvector), `source_type`, `ingested_via`, `embedding_cost`, `metadata` | Cat D (retrieval-side surface owned by content app but consumed by RAG) | HNSW index (line 834); unique_together `(document, chunk_index, embedding_model)` (line 837). Migration 0044 (2026-03-01) added `source_type` + `ingested_via`. |
| `KnowledgeBase` | `content/models.py:921-1050` | `name`, `embedding_model`, `chunk_size`, `document_count`, `categories`, `tags`, `domain`, `owner` | Cat E (organizational grouping) | Container for Document groups. No direct FK to DocumentEmbedding. Domain specialization (sports, betting, agents) at lines 1003-1050. |
| `LearningDocument` | `ai_core/intelligence/models.py` | FK to `DocumentEmbedding` (on_delete=CASCADE) | Cat A (Intelligence / Memory) | **Cross-domain boundary reach** — flagged in S1273 §5.4 "Multiple Memory / Knowledge Stores" overlap. Confirms E↔D is not the only edge into DocumentEmbedding. |

**Provenance sources (not Django models):**

| Artifact | Location | Owner | Contract |
|----------|----------|-------|----------|
| `docs/_index.json` | filesystem | build_docs_index | Corpus membership + metadata. Regenerated per-run (no upsert). |
| `docs/_provenance.json` | filesystem | build_docs_provenance | Per-doc session origin + confidence. Regenerated per-run. Schema at Agent 1 §3 (see `_meta` block + per-doc field set). |
| `.rag/corpus.jsonl` | filesystem (gitignored) | build_rag_corpus | JSONL chunks for LOCAL keyword lane. Regenerated per-run. |

**FK graph — what reaches Document / DocumentEmbedding from outside Cat D+E:**

- `DocumentEmbedding` → `Document` (line 715, CASCADE) — internal Cat D→E.
- `ContentGeneration` → `Document` (line 1200, OneToOneField SET_NULL) — Cat E internal.
- `LearningDocument` → `DocumentEmbedding` — **Cat A ↔ Cat D cross-boundary**. This is a S1273 §5.4 flagged overlap.
- No inbound FKs from Cat B (Spiders), Cat C (Agents), or Cat F (ConversationMemory). Corpus is not directly referenced by those domains.

## 5. Major Services

**Boundary-facing services:**

| Service | File:line | Line count | Role at boundary |
|---------|-----------|------------|------------------|
| `td_handlers_ops.py` (dispatcher) | `core/services/td_handlers_ops.py:1-6290` | **6290** — GOD-SERVICE | Owns `search_docs` handler + `kb_tool` handler + provenance filter + `_load_provenance_docs` cache. Single service is the entire retrieval-side boundary surface. |
| `doc_claim_verification.py` | `core/services/doc_claim_verification.py:1-3275` | **3275** — GOD-SERVICE CANDIDATE | Verification framework. 40+ registered claims. Lazy imports mitigate coupling; scope-cohesive. Not called by beat tasks or PA tools — CLI-only. |
| `EmbeddingService` | `core/services/embedding_service.py:66-413` | 413 | Wraps OpenAI embeddings API. Redis 7-day cache. LLMCallLog audit trail. Called by RAGSystem (Cat E→D ingestion) + rag_integration (Cat D internal). |
| `RAGObservabilityService` | `core/services/rag_observability_service.py:1-664` | 664 | Observability layer. Referenced by S1273 §3.13 but wiring to retrieval path SPECULATIVE — no direct confirmation in this sweep. |
| `RAGSystem` (inline in embeddings.py) | `content/embeddings.py` | (inline) | Owns `process_document_for_rag_sync` used by ingestion step 4a. |

**God-service ranking:** `td_handlers_ops.py` (6290 lines) exceeds
the 3000-line refactor threshold (playbook §13). Refactor
candidate: split by tool namespace (`ops/search_docs_handler.py`,
`ops/kb_tool_handler.py`, `ops/provenance_cache.py`).
`doc_claim_verification.py` (3275) is at threshold; cohesive
registry + lazy imports justify current size.

**Lazy import + cross-boundary reach:**

- `sync_docs_index_to_documents.py:358` inline imports
  `EmbeddingService` only if `--embed` flag set. Cat E→D lazy
  isolation.
- `td_handlers_ops.py:5502` inline imports `core.rag.top_k` inside
  `_handle_search_docs`. Retrieval-side lazy isolation.
- `doc_claim_verification.py` — every claim imports its dependencies
  inside the function to avoid circular-import + enable optional
  claims.

## 6. Major APIs and Interfaces

**PA tool surfaces (Rigby-facing):**

| Tool | Schema file:line | Handler file:line | Lane | Contract |
|------|------------------|-------------------|------|----------|
| `search_docs` | `pa_tool_schemas.py:4526` | `td_handlers_ops.py:5468` | LOCAL keyword (`.rag/corpus.jsonl`) | Token-overlap + hint-boost ranking. Returns `[docs/path#chunk_id]` citations. Accepts `originating_session` filter (S1145 P2). Schema truthful re LOCAL lane. |
| `kb_tool semantic_search` | `pa_tool_schemas.py:4570` | `td_handlers_ops.py:5379` | PROD pgvector (`DocumentEmbedding`) | Cosine similarity via pgvector HNSW. Returns ranked chunks. Filter: D9/D10 enrichment (category, document_class, is_pinned, min_session, include_superseded). Schema truthful re PROD lane. |

**Both schemas are live and exposed to Rigby via
`core/services/tool_dispatcher.py:555,557`** (Agent 3 verified).
S1301 §14 two-lane divergence claim: **CONFIRMED via schema
inspection and handler location.**

**REST/WS endpoints touching the boundary** (Agent 3 §4):

| Endpoint | View | Boundary touch |
|----------|------|----------------|
| `GET /api/docs/index/`, `/api/docs/stats/`, `/api/docs/graph/`, `/api/docs/detail/<path>/` | `core/views_docs_index.py` | Read-only exposure of `docs/_index.json` to frontend. |
| `GET /api/rag/observability/dashboard/`, `/inventory/` | `core/views_rag_observability.py` | Read-only observability. Reads Document/DocumentEmbedding for classification metrics. |
| `POST /api/v1/rag/upload-document/` | `core/views_rag_embeddings.py:63` | **Ingestion entry point** — creates Document + DocumentEmbedding out-of-band from the cascade. |
| `POST /api/v1/rag/semantic-search/` | `core/views_rag_embeddings.py:150` | Semantic search (pgvector lane). |

**Gaps discovered:**

- No `POST /api/docs/refresh/` — force-reindex is CLI-only.
- No progress WebSocket for ingestion cascade — no async telemetry
  to show "building index…" state.
- No bulk-ingest endpoint — `upload_document_for_rag` is single-doc.

## 7. Runtime Flows

**Flow 1 — 4-step docs ingestion cascade** (Agent 2 §2 full trace):

```
Step 1 build_docs_index (build_docs_index.py:46-1113)
  Reads:  docs/ (all *.md, recursive)
  Writes: docs/_index.json + docs/INDEX.md
  Upsert: full regeneration per run
  Failure: swallowed at parse (logger.warning), degrades to inferred metadata

Step 2 build_rag_corpus (build_rag_corpus.py:89-179)
  Reads:  docs/_index.json + file content on disk
  Writes: .rag/corpus.jsonl (fixed 1200-char chunks, deterministic order)
  Chunk semantics: no semantic boundary preservation; string prefix ops
  Path normalization: strips "docs/" prefix in corpus paths (join fragility per Agent 2)

Step 3 sync_docs_index_to_documents (sync_docs_index_to_documents.py:55-435)
  Reads:  docs/_index.json + file content
  Writes: Document rows (upsert via content_hash comparison)
  Enrichment (S1234 D9): category, tags, document_class, is_pinned, retrieval_boost
  Extracted metadata: scope='docs_index' marker
  Upsert: get_or_create by file_path + hash-delta gated update

Step 4 embed_documents / sync --embed (embed_documents.py:14-71 OR sync_...py:355-406)
  Reads:  Document.objects.exclude(id__in=docs_with_embeddings).filter(raw_content__gt='')
  Writes: DocumentEmbedding rows (create-only, unique_together enforced)
  Chunking: 1000-char chunks with 200-char overlap; semantic boundary preferred
  Embedding: EmbeddingService.create_embedding → OpenAI API + Redis 7-day cache
  Provenance-write: source_type via _derive_source_type + ingested_via='sync_docs' or 'backfill' or 'unknown'
```

**Flow 2 — Provenance materialization** (Agent 2 §3):

```
build_docs_provenance (build_docs_provenance.py:119-451)
  Reads:  .git/ (git log --all, two-pass parse: metadata + file list)
  Reads:  docs/*.md (first 30 lines, frontmatter session refs)
  Writes: docs/_provenance.json
  Per-doc: originating_session, confidence (HIGH/MEDIUM/LOW/UNKNOWN),
           match_source, first_commit_sha, first_commit_date,
           first_commit_subject, sessions_touched, commit_count, prs
  Confidence: HIGH if subject-tag match; MEDIUM if body-only; LOW if frontmatter-only
  Handoff filename override (S1147 P3.5): docs/handoffs/SESSION_NNNN_*.md uses filename as authoritative
  Meta: doc_count=2156, HIGH=1356, MEDIUM=336, LOW=0, UNKNOWN=464 (2026-06-23)
  Beat schedule: NONE (verified — grep 2026-07-01)
  Cadence: manual-only
```

**Flow 3 — Retrieval boundary + cache staleness** (Agent 2 §4):

```
_load_provenance_docs() @lru_cache(maxsize=1)  (td_handlers_ops.py:78-93)
  First call:  json.loads(docs/_provenance.json) → cache dict
  Subsequent:  returns cached dict (no re-read)
  Invalidation: NONE — worker restart is the only mechanism
  Consequence: build_docs_provenance updates disk file; running workers
               serve stale filter results until process restart

_handle_search_docs (td_handlers_ops.py:5468)
  Query → core.rag.top_k → chunks
  If originating_session: apply _filter_chunks_by_originating_session
    → reads _load_provenance_docs() (may be stale)
    → emits filter counters into response payload (no logging)
```

## 8. Data Ownership and Lifecycle

**Corpus authority chain (Cat E write side):**

```
docs/ (files on disk)
  → build_docs_index (rebuild)     → docs/_index.json (regenerable)
  → sync_docs_index_to_documents   → Document rows (upsert by hash)
  → embed_documents                → DocumentEmbedding rows (create-only)
```

**Provenance authority chain (parallel):**

```
Path A (external, git-history-derived):
  .git/ commit history
    → build_docs_provenance (rebuild)    → docs/_provenance.json
    → _load_provenance_docs (@lru_cache) → retrieval filter (search_docs only)

Path B (row-level, ingestion-time-derived):
  Document.extracted_metadata + document_type + source
    → _derive_source_type()                → DocumentEmbedding.source_type
    → ingested_via='sync_docs' / 'backfill' / 'unknown' (fixed constant per call site)
    → semantic_search_sync(source_filter=…) reads source_type at :971-973 (VERIFIED S1304)
    → SearchResult presentation reads source_type at :1007
    → ingested_via: NO READ PATH FOUND (F1-CANDIDATE per S1303 §14 discipline)
```

**Governance rule** (`DOC_LIFECYCLE.md` §2c, `:99-111`):
`PLATFORM_INVENTORY.md` + `docs/INDEX.md` are the ONLY authoritative
counts. All other doc claims are snapshots. Applied at boundary: the
21.5% UNKNOWN gap in `_provenance.json._meta.confidence_breakdown`
is the current-state snapshot; not a bug in retrieval mechanism.
Whether the gap should shrink is a corpus-completeness question
(§14 D1) whose remediation belongs to the ingestion side.

## 9. Integrations With Other Domains

**Load-bearing cross-domain edge classifications** (per S1274 §11
STRONG/WEAK/MISSING/OVERCOUPLED/UNKNOWN; Agent 4 §1):

| Edge | Direction | Strength | Evidence |
|------|-----------|----------|----------|
| **E → D** (this audit's scope, ingestion) | E→D | STRONG | 4-step cascade wired; post-save signal at `document_processing_signals.py:54-85` chains ingestion → embedding. |
| **D → E** (retrieval-side reads of corpus metadata) | D→E | PARTIAL — see §14 D3 refinement | Row-level `source_type` IS read (`content/embeddings.py:965-973` — semantic_search_sync source_filter branch); row-level `ingested_via` has **no owner-model-qualified consumer identified** per S1303 §14 F4-CANDIDATE discipline (verification pending §19 R1). External `_provenance.json` derived from git history not from `Document` metadata. Two provenance systems partially decoupled (§17 refined). |
| **F ↔ D** (PA turn enrichment ↔ RAG) | asymmetric | MISSING → design-decision | S1301 §14 + S1303 §9: PA turn enrichment has 0 RAG imports (S1304 grep verifier confirmed: `search_docs\|kb_tool\|semantic_search\|search_embeddings` = 0 in `unified_pa_entrypoint.py`). Two schools of evidence — see §19 R5. |
| **Agent System ↔ D** (BaseAgent knowledge injection) | Agent→D (partial) | STRONG (agent path) / TOOL-CALL-ONLY (PA path) | `BaseAgent._get_relevant_knowledge_for_task()` at `base_agent.py:1439-1510` calls spider semantic search; agent knowledge pipeline is spider-fed, not corpus-fed. Corpus is not the source for agent prompt injection. |
| **PA Enrichment ↔ D** | one-way (D avail as tool, not called from enrichment) | MISSING → confirmed intentional or drift (§19 R5) | Same evidence as F↔D — 0 RAG imports in enrichment pipeline. |
| **A (LearningDocument) → D** | A→D | STRONG (single FK) | `ai_core/intelligence/models.py` FK to DocumentEmbedding (CASCADE). S1273 §5.4 flagged overlap. |

**S1274 §2.5 baseline (Knowledge & Memory) compared to S1304
findings:**

- S1274 classified "Documentation (15) → RAG (14)" as STRONG. S1304
  agrees on the cascade wiring; but S1274 did not audit field-level
  provenance semantics — the D→E delta (MISSING row-level consumer
  for `ingested_via`) is new evidence.
- S1274 classified "RAG (14) → PA (1)" as STRONG. S1304 confirms
  both tools exist; also documents the tool-call-only pattern +
  Cat F ↔ Cat D gap.
- S1274 did not audit PA enrichment ↔ RAG separately. S1303 §9 +
  S1304 §9 add this finding.

## 10. Event Flows

**Ingestion completion signal:** PARTIAL.

- `Document.post_save(created=True)` fires at
  `document_processing_signals.py:54-85` → dispatches
  `process_document_async` → chains
  `generate_document_embeddings`.
- **No EventBus emission** for `DOCUMENT_EMBEDDED`. Event bus
  (`event_bus.py:21-30`) defines 8 streams
  (OPPORTUNITY_SCORED, SPIDER_DATA, VALIDATION_*, OUTCOME_RECORDED,
  SYSTEM_ALERT, MODEL_TRAINED, DLQ); none touch corpus embed
  completion. Inter-domain observers of corpus updates have no
  event surface (S1274 §1 EventBus adoption gap).

**Provenance rebuild signal:** MISSING.

- `_load_provenance_docs()` cache is per-process, unlimited TTL. No
  invalidation event when `build_docs_provenance` rewrites the
  file. Only mechanism: worker restart (memory rule
  `feedback_celery_pid_cache_blocks_restart.md`).

**Retrieval-miss telemetry:** RESPONSE-ONLY (S1301 §14.2 confirmed).

- Counters `excluded_missing_provenance`, `excluded_mismatch`,
  `pre_filter_count` at `td_handlers_ops.py:5585-5590` embedded
  in response dict. No log emission, no metrics endpoint, no
  alert. S1300 §6 parked finding surfaced this by manual tool
  inspection.

## 11. Existing Documentation

**Coverage inventory** (Agent 5 §1):

| Doc | Type | Coverage at boundary |
|-----|------|---------------------|
| `docs/00-START-HERE/DOC_LIFECYCLE.md` (S1143) | governance | §2c inventory-wins rule + §2b runtime-coupled paths |
| `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` (S1158) | narrative | Comprehensive 5-memory + 2-RAG overview; open questions §6 include current chunk coverage |
| `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (S1301) | research (sibling) | DEEP audit of Cat D internals + boundary drift claims S1304 verified |
| `docs/research/domains/memory/1301_followup_provenance_classifier_bug.md` (S1301) | research (follow-up) | Concrete instance of classifier precedence inversion |
| `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` (S1302) | research (sibling) | §17.3 name-collision boundary methodology reused |
| `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` (S1303) | research (sibling) | §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3 turn-context enrichment hypothesis (routed to S1304) + §14 F4-CANDIDATE discipline (applied to S1304) |
| `docs/research/platform_architecture_inventory.md` (S1273) | research | §3.13, §3.14, §3.15 + §5.4 overlap flag |
| `docs/research/platform/cross_domain_integration_audit.md` (S1274) | research | Cross-domain baseline for §9 comparison |
| `docs/topics/local-askdocs.md` (S1108) | topic | CANONICAL boundary-disambiguating doc — explicit LOCAL vs PROD lane separation |
| `docs/KNOWLEDGE_PIPELINE.md` (S400+) | flow map | Spider → embed → knowledge flow; complements this audit's corpus flow |
| `docs/handoffs/SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md` | handoff | Ingestion-moment snapshot: 852 → 14,149 chunks |

## 12. Research Coverage

- **Cat E internals**: **CANONICAL** (S1273 §3.15; DOC_LIFECYCLE
  §2c authoritative governance rule; verified).
- **Cat D internals**: **DEEP** (S1301 P1 audit; WORKING verdict).
- **E ↔ D boundary**: **LIGHT → MODERATE after S1304**. Prior work
  addressed each side independently; boundary-lens research
  begins here. Explicit gaps (see §19) remain after this audit.

## 13. Architecture Maturity

Per playbook §12 (EXPERIMENTAL / PARTIAL / WORKING / STABLE /
CANONICAL):

| Component | Maturity | Evidence |
|-----------|----------|----------|
| Ingestion cascade | **PARTIAL** | Cascade operates daily on beat; step 4 async fan-out is not gated by cascade completion; hash-delta gating in `refresh_docs_corpus` is edge-case fragile (Agent 6 SPECULATIVE); step 3 idempotency not verified. |
| Provenance filter mechanism | **WORKING** | Logic is sound. Downgrades: (a) 21.5% UNKNOWN input coverage, (b) counters have no operator visibility, (c) cache staleness gap. Mechanism STABLE; deployed data PARTIAL; observability MISSING. |
| Row-level provenance write path | **EXPERIMENTAL** | Fields exist + populated (migration 0044). `source_type` **has qualified consumers** (S1304 verified at `content/embeddings.py:965-973` + `:1007`); `ingested_via` is F1-CANDIDATE orphan. Deprecation vs consumer-wiring decision belongs to design-preparation phase. |
| **E↔D boundary as a whole** | **PARTIAL** | Functional but not mature. Ownership undefined (§18); provenance rebuild unscheduled; cache invalidation absent; observability response-only; documentation of cascade discipline unpublished. |

## 14. Known Drift

**D1 — 21.5% corpus-completeness gap** (S1301 §14.2 inherited,
S1304 confirmed boundary-relevant).
- 464 UNKNOWN / 2156 docs (`docs/_provenance.json._meta.confidence_breakdown`).
- Root cause per Agent 5: docs predating session-NNNN convention
  (introduced Session 1144) OR bulk commits lacking session
  attribution. Not a filter mechanism bug — a
  provenance-index-completeness signal.
- Boundary classification: origin is at the ingestion→retrieval
  handoff (the provenance index does not carry a signal for these
  docs; the filter cannot verify them and excludes by design per
  `td_handlers_ops.py:82-85`).

**D2 — `lru_cache(1)` staleness after `build_docs_provenance`**
(S1301 §14 inherited, S1304 confirmed load-bearing).
- `_load_provenance_docs()` at `td_handlers_ops.py:78-93` caches
  indefinitely per-process. No invalidation mechanism. Workers
  serve stale filter results between `build_docs_provenance`
  execution and worker restart.
- **HIGH severity** — this is the canonical write-side/read-side
  synchronization gap at the boundary.

**D3 — Row-level provenance orphan-write pattern, NARROWED** (S1301
§19 hypothesis partially invalidated by S1304 verifier-loop).
- **`source_type`** — NOT orphan. Consumers verified:
  1. `content/embeddings.py:965-973` — `semantic_search_sync`
     applies `source_filter='internal_only'` /
     `'external_only'` branches via `.filter(source_type__in=[…])`.
  2. `content/embeddings.py:1007` — SearchResult presentation
     reads `getattr(embedding, 'source_type', 'unknown')`.
  - Both are owner-model-qualified per S1303 §14 discipline
    (Django ORM query on `DocumentEmbedding` at :965 confirms
    consumer qualification).
- **`ingested_via`** — F1-CANDIDATE orphan-write. All 3 write-sites
  use fixed string constants:
  1. `sync_docs_index_to_documents.py:394` — `ingested_via='sync_docs'`.
  2. `core/tasks_agents.py:4223, 4290, 4351` — `ingested_via='backfill'`.
  3. `content/embeddings.py:654, 753` — `ingested_via='unknown'` default via `_derive_source_type` context.
  - Grep 2026-07-01 (Agent 1 + verifier): zero
    owner-qualified read consumers.
  - Admin (`content/admin.py:146-164`): NOT in `list_display`.
  - DRF serializer (`content/serializers.py:104-118`): NOT in
    field list.
  - **F1-CANDIDATE verdict** — subject to full-tree recheck per
    §19 R1 before declaring dead code.

**D4 — PA turn enrichment does not auto-invoke RAG** (S1301 §14
+ S1303 §9 inherited).
- S1304 verifier-loop grep confirmed: 0 matches for
  `search_docs|kb_tool|semantic_search|search_embeddings` in
  `unified_pa_entrypoint.py`.
- **OUT OF S1304 EXCLUSIVE SCOPE.** This is a Cat F ↔ Cat D
  finding, not an E ↔ D boundary drift. Routed to §19 R5 as
  design-decision hypothesis (intentional-separation vs drift)
  per S1303 §19 R3 handoff.

**D5 — Ingestion-cascade documentation coverage gap** (S1304-new).
- Memory rule `feedback_docs_pipeline_4_step_cascade.md`
  documents the cascade discipline, but there is no
  `docs/topics/` published user-facing reference. Operators
  learning the system have no canonical "what is the docs
  cascade" doc.
- **MEDIUM severity** — MEDIUM boundary drift (documentation-side).

**D6 — Provenance-index rebuild cadence unscheduled** (S1304-new,
LOAD-BEARING).
- **Positive beat-schedule evidence** (SIGN cycle 1 fold, Rigby
  edit #1): `core/celery.py:495-499` defines the sole
  `refresh-docs-corpus-daily` beat entry:
  ```python
  'refresh-docs-corpus-daily': {
      'task': 'core.tasks.refresh_docs_corpus',
      'schedule': crontab(hour=4, minute=0),  # 4:00 AM Denver
      'options': {'queue': 'default', 'expires': 3600},
  }
  ```
  No companion `build-docs-provenance-*` entry exists in
  `core/celery.py`.
- Inside `refresh_docs_corpus` at `core/tasks.py:5803`, the
  cascade calls are: `build_docs_index` at `:5900`,
  `build_rag_corpus` at `:5901`,
  `sync_docs_index_to_documents` at `:5902` — no
  `build_docs_provenance` call site. Verifier search returned
  zero matches for `build_docs_provenance` inside
  `core/tasks.py`.
- Absence-of-refs sweep (grep 2026-07-01): `build_docs_provenance`
  referenced only in 3 files — the command itself, a sibling
  `backfill_doc_provenance.py`, and `td_handlers_ops.py:5573-5576`
  (error-path suggestion). Not in `core/tasks.py` or
  `core/celery.py`.
- **HIGH severity** — load-bearing command with no scheduled
  execution. Combined with D2, this is the canonical E→D
  synchronization drift.

**D7 — Row-level provenance never wired into retrieval for
`ingested_via` field only** (S1304-new — narrowed from D3 pattern).
- `source_type` field: wired (D3 verifier-loop refuted broad
  hypothesis; owner-model-qualified consumer verified at
  `content/embeddings.py:965-973` + `:1007`).
- `ingested_via` field: **F4-CANDIDATE per S1303 §14 discipline** —
  no owner-model-qualified consumer identified in this sweep's
  grep, but per S1303 §14 rule ("dead-code claim requires
  owner-model-qualified consumer inventory, not keyword grep"),
  the claim is CANDIDATE not CONFIRMED until §19 R1 full-tree
  verification lands. Design intent ambiguous — was future
  retrieval consumer planned + not implemented, or is the field
  an audit-trail marker for future forensics?
- **MEDIUM severity** — deprecation vs consumer-wiring decision
  belongs to design-preparation phase; must not be executed on
  before §19 R1 completes.

**D8 — Retrieval-side filter counters invisible to operators**
(S1304-new, from S1301 §14.2 pattern).
- `excluded_missing_provenance`, `excluded_mismatch`,
  `pre_filter_count` at `td_handlers_ops.py:5585-5590` in
  response payload. No log emission, no metric, no alert.
  Silent failures at scale.
- **MEDIUM severity** — observability-side of the E↔D boundary.

## 15. Known Technical Debt

Per playbook §12 (Risk classifications), bounded remediation
sketches per Agent 6 §3:

| ID | Debt | Severity | Boundary-scope | Remediation sketch |
|----|------|----------|----------------|--------------------|
| T1 | Provenance-index rebuild cadence unmanaged | HIGH | Yes (E↔D) | Add `build_docs_provenance` to `refresh_docs_corpus` beat OR separate schedule; verify index timestamp newer than corpus timestamp. |
| T2 | `lru_cache(1)` staleness after index rebuild | HIGH | Yes (E↔D write-read sync) | Trigger worker restart on rebuild OR file-watcher OR move to Redis (queryable, no restart) OR time-based TTL. |
| T3 | Two provenance systems, partial-decoupled | MEDIUM | Yes (E↔D — narrowed from D3) | Design decision: consolidate, formally separate scopes, or deprecate one. Ownership: S1302 P2 owns row-level; S1304 identifies boundary asymmetry. |
| T4 | Ingestion cascade documentation unpublished | MEDIUM | Yes | Publish `docs/topics/docs-ingestion-cascade.md`: 4-step flow, preconditions, postconditions, failure/recovery, cadence rationale. |
| T5 | `ingested_via` write path not wired to retrieval | MEDIUM | Yes | Either (a) add filter on `kb_tool` to allow `ingested_via` filtering (similar to `source_type` at `content/embeddings.py:965-973`) OR (b) deprecate the field after full-tree verification. Recommend R1 first (F4-CANDIDATE verification). |
| T6 | Filter counters lack operator surface | MEDIUM | Yes (observability) | Emit `logger.warning` when drop rate exceeds threshold (e.g., >30% in 1-hr window). Prometheus counter `search_docs_filter_drops_total{reason}`. Grafana surface. Owner: Group 1700 Observability (delegate). |
| T7 | Corpus-completeness gap not auto-detected | MEDIUM | Yes | Add `verify_provenance_coverage` mgmt command; cache prior `_meta.confidence_breakdown`; warn on UNKNOWN increase. Surface in PLATFORM_INVENTORY.md. |
| T8 | No explicit ownership of provenance model | MEDIUM | Yes (governance) | S1304 verdict: **provenance index should be owned by Cat E** (git-history-derived, doc-file-scoped). Move `build_docs_provenance` into docs-governance mgmt command set; document in `DOC_LIFECYCLE.md §2b`; schedule alongside `build_docs_index`. |

## 16. Boundary Violations

**Definition**: places where one category reaches into another's
internals without a service abstraction.

**Findings:**

- **`td_handlers_ops.py` reads `docs/_provenance.json` directly**
  (`:78-93` `_load_provenance_docs`). Retrieval-side handler
  bypasses any Cat E-provided service abstraction. If the file
  schema changes (Cat E), the retrieval handler must update.
  Boundary-lens verdict: **not a violation** — the file is a
  contract artifact, and `_load_provenance_docs` is a wrapped
  reader. But the coupling is implicit; a formal reader service
  in Cat E owned by the docs-governance layer would clarify
  ownership.

- **Path normalization at `.rag/corpus.jsonl` ↔ cite
  reconstruction** (S1301-flagged, Agent 2 §7 point 2). Corpus
  paths drop `docs/` prefix; `td_handlers_ops.py:5537`
  re-adds it via string prefix. Coupling is deterministic but
  fragile — a Cat E path-normalization convention change would
  silently break Cat D citations.

- **Ingestion writes to `DocumentEmbedding` with fields only
  ingestion understands** (`source_type` derivation semantics at
  `content/embeddings.py:45-63`). Retrieval-side
  `semantic_search_sync` at :971-973 filters by hardcoded value
  sets (`['internal', 'user_upload']` / `['web', 'spider',
  'api']`). If ingestion adds a 7th value, retrieval will not
  auto-recognize it. Boundary contract on enum values is
  implicit — worth a shared const or enum type.

## 17. Duplicate or Overlapping Systems

Per S1302 §17.3 name-collision methodology + S1273 §5.4 overlap
flag.

**Two-provenance overlap** (S1304's canonical boundary finding):

| System | Location | Read consumers | Write producers | Owner |
|--------|----------|----------------|-----------------|-------|
| External `_provenance.json` | `docs/_provenance.json` | `td_handlers_ops.py:78-93` (`_load_provenance_docs` + filter at :5566-5590) — LOCAL keyword lane only | `build_docs_provenance.py` — manual/CLI only | UNOWNED (S1304 recommends Cat E) |
| Row-level `DocumentEmbedding.source_type` | `content/models.py:707-918` | `content/embeddings.py:965-973` (`semantic_search_sync` source_filter) + `:1007` (presentation) | `content/embeddings.py:654, 753` (`_derive_source_type` at ingestion) | Cat E (populated) → Cat D (consumed) |
| Row-level `DocumentEmbedding.ingested_via` | same | **NONE** (F1-CANDIDATE per §14 D3) | `sync_docs_index_to_documents.py:394` + `core/tasks_agents.py:4223/4290/4351` + `content/embeddings.py:654/753` | orphan |

**Applied S1302 §17.3 methodology:** The name-collision framing
resolves the ambiguity by asking which consumer reads which. External
JSON serves the LOCAL keyword lane (`search_docs`); row-level
`source_type` serves the PROD pgvector lane (`kb_tool` via
`semantic_search_sync` at `content/embeddings.py:965-973`);
`ingested_via` has no owner-model-qualified consumer identified
today (F4-CANDIDATE per §14 D3 pending §19 R1 verification). The
three systems encode **complementary** semantics (session origin vs
source-of-record enum vs write-audit marker), not redundant. **Not a
duplicate** — a partial-decoupled overlap where the write-audit
marker was over-designed for a retrieval consumer that never
materialized.

**Complementary today does not imply optimal** (SIGN cycle 1 fold #4).
The "complementary" framing describes current-state architecture; it
does NOT endorse the two-system split as the correct long-term
design. Two open design questions remain, routed to §19 R2
(provenance-system reconciliation):

- **Unification path** — collapse to a single provenance model
  (e.g., row-level source-of-truth with derived external JSON for
  LOCAL lane; OR external JSON as source-of-truth with row-level
  view/materialization).
- **Explicit scoping path** — canonicalize the current split with
  a documented boundary contract (e.g., "session-origin lives
  external; source-of-record enum lives row-level; write-audit
  markers are prohibited on retrieval-owned tables") and add an
  ADR.

The choice between them is not resolvable from static evidence
inside this audit — it requires product/architecture
decision-making with input on operational cost, migration risk,
and future retrieval requirements. Do NOT treat "complementary"
as exoneration of the split.

**Two RAG lanes** (S1301 §14 confirmed):

| Lane | Backend | Filter | Owner |
|------|---------|--------|-------|
| `search_docs` (LOCAL) | `.rag/corpus.jsonl` + `core.rag.top_k` | `originating_session` provenance filter (`_provenance.json`) | Cat D |
| `kb_tool semantic_search` (PROD) | `DocumentEmbedding` + pgvector | `source_filter` (row-level `source_type`) + D9/D10 enrichment filters (category, document_class, is_pinned, min_session) | Cat D |

**Not duplicates** — two lanes by design (per `docs/topics/local-askdocs.md`
S1108 CANONICAL: "completely independent, distinct modules with
non-overlapping consumers"). But the asymmetry — one filters by
external provenance, the other by row-level provenance — reflects the
partial-decoupling in the provenance model itself. If provenance
model unifies (§19 R2), the filter surfaces would also unify.

## 18. Ownership Gaps

Per playbook §11.2 §18 (question #27); Agent 6 §4; refined via SIGN
cycle 1 fold #2 (Rigby edit — soften blanket "UNOWNED" phrasing;
cite `core/employees/jobs.py` positive evidence).

**Positive ownership evidence — Documentation Manager (Employee OS
handle) DOES own the ingestion cascade.**

`core/employees/jobs.py:187-395` defines the `DOCUMENTATION_MANAGER`
`JobContract` (registered in `_JOBS_BY_EMPLOYEE` at `:1336` as
`"docs_manager": DOCUMENTATION_MANAGER`, employee_handle=`rigby`).
Load-bearing fields:

- Mission (`:193-203`): "Rigby owns running the documentation
  cascade, recording evidence, certifying successful runs, and
  escalating failures or drift. Sync between `docs/` on disk and
  the index / RAG corpus / Document table / DocumentEmbedding
  table is a best-effort operational target contingent on the
  cascade commands succeeding."
- `daily_routine` (`:222-231`): explicit Step 1 =
  `build_docs_index`; Step 2 = `build_rag_corpus`; Step 3 =
  `sync_docs_index_to_documents`; Step 4 = same command with
  `--embed`; Step 5 = `verify_doc_claims --only-drift`
  (observation only); Step 6 = `mission_verdict` emit.
- Authority (`:238-250`): `run_docs_cascade_commands=EXECUTE`;
  `run_drift_observation=OBSERVE`;
  `modify_docs_files=PROHIBITED`; `open_pull_request=PROHIBITED`;
  `delete_document_rows=PROHIBITED`;
  `delete_document_embedding_rows=PROHIBITED`.
- `mission_run_kind="docs_cascade"` (`:235`) with `OpsRun +
  OpsRunEvent` audit contract (`:295-301`).

**Refined ownership matrix:**

| Component | Owner | Gap severity |
|-----------|-------|--------------|
| Ingestion cascade steps 1-4 | **`docs_manager` (Documentation Manager JobContract, `rigby` handle)** — `core/employees/jobs.py:187-395`, registered at `:1336` | LOW — explicit `JobContract.daily_routine` names all 4 steps + `mission_run_kind="docs_cascade"` + OpsRun audit contract. |
| Drift observation (Step 5) | Documentation Manager (OBSERVE authority) | LOW — `verify_doc_claims --only-drift` runs as observation, does NOT fail mission. |
| Provenance filter mechanism | Cat D (`_load_provenance_docs` + filter at `td_handlers_ops.py:78-93` + `:5566-5590`) | LOW — clear implementation ownership. |
| Row-level provenance (`source_type` write + read) | Cat E writes (ingestion via `_derive_source_type`), Cat D reads (`semantic_search_sync` at `content/embeddings.py:965-973`) | LOW — bidirectional wiring exists. |
| **`build_docs_provenance` command** | **No explicit named runtime owner** — NOT in Documentation Manager `daily_routine` (`:222-231`); NOT in any `PeriodicTask`/beat entry (`core/celery.py`); NOT in any other `JobContract` in `core/employees/jobs.py` | HIGH — load-bearing command with zero scheduled execution (D6). |
| **`lru_cache(1)` invalidation** (`_load_provenance_docs`) | **No explicit named runtime owner** — cache is per-process; invalidation strategy not assigned to any role. | HIGH — canonical D2 write-read synchronization gap. |
| **Row-level `ingested_via` field consumer strategy** | **No explicit named runtime owner** — write-only per §14 D3; F4-CANDIDATE pending §19 R1 full-tree verification. | HIGH pending R1. |
| **Retrieval-side filter counter observability** (D8) | **No explicit named runtime owner** — Group 1700 Observability arc queued but not yet opened. | MEDIUM pending Group 1700. |
| **E↔D boundary handoff as a whole** (provenance freshness + cache invalidation + boundary observability + row-level model reconciliation) | **No explicit named runtime ownership** — no single `JobContract` or team binds these four responsibilities together. | **HIGH** (softened from "CRITICAL" per SIGN cycle 1 fold #2). Bounded language: **explicit ownership exists for cascade execution (Documentation Manager) but not for the four boundary-maintenance responsibilities** listed above. |

**Playbook §12 bounded-language check:** "UNOWNED" originally read
as binary. Refined: **explicit named runtime ownership** exists for
cascade execution (Documentation Manager JobContract). It does NOT
exist for the four specific boundary-maintenance responsibilities
(provenance rebuild cadence, cache invalidation, filter
observability, row-level model reconciliation). Cat D + Cat E have
implicit maintainers (Chris + Claude Code per CLAUDE.md); no
`AIEmployee` handle or `JobContract` explicitly binds
boundary-maintenance responsibilities.

**S1304 recommendation:** S1399 canonical summary should either
(a) expand Documentation Manager's authority to cover
`build_docs_provenance` + cache-invalidation trigger, OR
(b) create a distinct `AIEmployee` handle for boundary maintenance,
OR (c) delegate observability to Group 1700 while explicitly
assigning provenance-freshness + cache-invalidation to
Documentation Manager. At minimum, `DOC_LIFECYCLE.md` §2b
(runtime-coupled paths) should list `docs/_provenance.json` and
name its owner (S1304 verdict: Cat E, since it is
git-history-derived from doc files).

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows
(playbook §11.2 §19).

**R1 — Full-tree verification of `ingested_via` orphan status**
(HIGH priority; F4-CANDIDATE discipline per S1303 §14).
- Scope: enumerate every consumer of `DocumentEmbedding` (not just
  keyword grep of `ingested_via`). For each, verify whether
  `.ingested_via` is accessed via ORM query, values(), only(),
  serializer, admin, or template. Only after zero owner-qualified
  consumers are confirmed can this be declared dead code.
- Unblocks: T5 (deprecation-or-wire decision); §17 provenance-
  system reconciliation design; DB migration to remove the field
  if truly orphan.
- Owner: Cat E (populates) + Cat D (would-be consumer).

**R2 — Provenance-system reconciliation design**
(HIGH priority; blocks T3 remediation).
- Question: should external `_provenance.json` and row-level
  `source_type` remain complementary (session origin vs
  source-of-record), or should the model unify?
- Sub-decisions: does `search_docs` also gain `source_type`
  filtering? Does `kb_tool` also gain `originating_session`
  filtering? What is the migration path for the 21.5% UNKNOWN
  entries?
- Owner: S1302 P2 arc + S1399 canonical summary.

**R3 — Rebuild cadence + cache invalidation design**
(HIGH priority; blocks T1 + T2 remediation).
- Question: unify `refresh_docs_corpus` cascade to include
  `build_docs_provenance`, OR separate beat schedule, OR file
  watcher, OR Redis-backed provenance store.
- Blocker: staleness detection — how does an operator know the
  index is out-of-date?
- Owner: Cat E (governance) — recommend delegating to
  `DOC_LIFECYCLE.md` maintainer.

**R4 — Boundary ownership assignment**
(HIGH priority; blocks the four preceding drifts from
being systematically maintained).
- Question: which team/agent/JobContract owns E↔D handoff
  freshness, cache invalidation, cascade-completion signals?
- Recommend: S1399 canonical summary names a boundary owner OR
  creates a cross-category steering committee. If no obvious
  owner exists, add "Docs Corpus ↔ RAG boundary maintenance"
  responsibility to an existing role (candidate: Documentation
  Manager `AIEmployee` from Employee OS).
- Owner: S1399 canonical summary.

**R5 — Turn-context → RAG enrichment design decision** (routed
from S1303 §19 R3; MEDIUM priority; design-preparation phase,
not this arc).
- Question: is the absence of PA-turn → RAG enrichment
  intentional (thread memory vs source memory scope separation)
  or drift (missing wiring)?
- Evidence entering S1304 (Agent 4 §2): **mixed**.
  - Intentional signals: 8 enrichment services deliberately
    non-RAG; two first-class PA tools for explicit corpus
    access; thread-memory vs source-memory scope discipline;
    no event-driven wiring for turn signals to influence
    retrieval.
  - Drift signals: no design comment explaining absence;
    asymmetry with `BaseAgent._get_relevant_knowledge_for_task`
    (agents get auto-enrichment; PA does not); S1301 §6
    provenance-filter cost visible to users; no feature flag
    guarding the absence.
- Verdict: **cannot resolve from static evidence — requires
  product/architecture decision**. Route to design-preparation
  phase with R5.a (canonicalize separation) + R5.b (implement
  enrichment) as competing hypotheses.
- Owner: design-preparation phase (post-S1399); NOT this audit.

**R6 — Ingestion-cascade published documentation**
(MEDIUM priority; blocks T4 remediation).
- Publish `docs/topics/docs-ingestion-cascade.md`: 4-step flow,
  preconditions, postconditions, failure/recovery, cadence.
- Owner: Cat E (docs-governance).

**R7 — Filter-drop telemetry** (MEDIUM priority; blocks T6
remediation).
- Emit `[SEARCH_DOCS_FILTER_DROP]` warning + Prometheus counter
  when drop rate exceeds threshold. Grafana surface. Threshold
  alert.
- Owner: **delegate to Group 1700 Observability**.

**R8 — S1301 follow-up (classifier precedence bug)** (LOW
priority; standalone bugfix, not S1304 scope).
- `build_docs_provenance` classifier weights body-mention over
  subject-tag. S1301 follow-up documented one confirmed case.
  Scope: how many other docs are misclassified?
- Owner: standalone follow-up PR; NOT blocking Group 1300 arc.

## 20. Appendix

### 20.1 Sweep sub-agents (playbook §13)

Six parallel Explore agents launched at S1304 open:

| Agent | Focus | Verdict weight |
|-------|-------|----------------|
| Agent 1 | Models & Persistence | LOAD-BEARING — invalidated broad S1301 §19 D3 hypothesis; narrowed to `ingested_via` only. |
| Agent 2 | Services & Runtime Flows | LOAD-BEARING — verified `lru_cache(1)` claim; confirmed `build_docs_provenance` beat-schedule absence; identified two god-service candidates. |
| Agent 3 | APIs / Tools / Tasks / Commands | LOAD-BEARING — verified `search_docs` handler location; confirmed both PA tool schemas + `refresh_docs_corpus` beat schedule at 4:00 Denver daily. |
| Agent 4 | Integrations & Cross-Domain | LOAD-BEARING — Cat F ↔ Cat D decision framing (intentional vs drift); confirmed 0 RAG imports in PA enrichment. |
| Agent 5 | Documentation & Prior Research | LOAD-BEARING — DOC_LIFECYCLE §2c governance rule; explicit prior-research "already covered by X" pointers. |
| Agent 6 | Drift / Debt / Ownership / Maturity | LOAD-BEARING — T1–T8 debt matrix; ownership finding CRITICAL for §18; PARTIAL maturity verdict. |

### 20.2 Verifier-loop record

Applied per playbook §14 "trust but verify" rule. Four
load-bearing claims independently verified via direct file:line
read before folding into the audit:

1. **Agent 1's `source_type` reads at `content/embeddings.py:965-973`
   + `:1007`** — CONFIRMED. `semantic_search_sync` accepts
   `source_filter` param (default `'all'`), applies
   `DocumentEmbedding.objects.filter(source_type__in=[…])` for
   `internal_only` / `external_only` branches at :971-973;
   SearchResult presentation reads `source_type` at :1007.
   **S1301 §19 D3 broad hypothesis partially invalidated** —
   `source_type` is NOT orphan; only `ingested_via` remains
   F1-CANDIDATE.

2. **Agent 3's `search_docs` handler at
   `td_handlers_ops.py:5468`** — CONFIRMED. Handler starts at
   line 5468. S1301's `:5502` cite is the inline
   `from core.rag import top_k` import inside the handler body
   at line 5502. Both are correct at different granularity; no
   drift.

3. **Agent 2 + Agent 6 no-beat-schedule for
   `build_docs_provenance`** — CONFIRMED via grep 2026-07-01.
   Three files reference the command: (a) `td_handlers_ops.py`
   suggests it in error path (lines 5573-5576), (b) the command
   itself (`build_docs_provenance.py`), (c) a sibling backfill
   command (`backfill_doc_provenance.py`). Zero refs in
   `core/tasks.py`, `core/celery.py`, or any beat schedule
   config. `refresh_docs_corpus` (daily 4:00 Denver) does NOT
   include it.

4. **Agent 4's zero RAG imports in `unified_pa_entrypoint.py`**
   — CONFIRMED via grep. Zero matches for
   `search_docs|kb_tool|semantic_search|search_embeddings` in
   the 7,613-line PA entrypoint file.

### 20.3 Rigby SIGN cycles

*(To be filled after §15 SIGN routing on fresh isolation pin.)*

### 20.4 Provenance

- **Parent frontmatter provenance:**
  `docs/research/domains/memory/1300_memory_domain_scoping.md` §5 P4.
- **Prior sibling evidence:** S1301 §14.2 + §19 (Cat D — including
  the D3 hypothesis this audit partially invalidates); S1302
  §17.3 (name-collision boundary methodology); S1303 §9 + §19 R3
  + §14 F4-CANDIDATE discipline.
- **Runtime anchors:** `docs/PLATFORM_INVENTORY.md` (2026-06-22
  runtime snapshot); `docs/_provenance.json` (2026-06-23 rebuild;
  464/2156 UNKNOWN); `git rev-parse HEAD` at S1304 open:
  `6365f33f`.

### 20.5 Unresolved unknowns

Per playbook §14 evidence rules (flag UNKNOWN honestly, do not
guess to fill):

- **Step 4 embedding completion coverage** — hash-delta gating on
  `refresh_docs_corpus` skips embed if `unembedded==0`, but a
  partial embed failure (network / API / rate-limit) is not
  detected next-cycle unless the failure landed a `Document` row
  without an associated `DocumentEmbedding`. Coverage guarantee
  is SPECULATIVE (Agent 3 §6).
- **`RAGObservabilityService` wiring** — service exists (664
  lines); whether it is actually called by the retrieval path or
  is partially wired is UNKNOWN (Agent 2 §1 flagged).
- **`_derive_source_type` categorization accuracy** — how often
  it defaults to `'unknown'` in production is UNTRACKED. If most
  writes land as `'unknown'`, D3's row-level utility is degraded.
- **`kb_tool` and `search_docs` may share Document table but
  diverge on which lane a caller picks** — Agent 5 §5 flagged
  potential contradiction between "share source" and "completely
  independent" (per `local-askdocs.md`). S1304 verdict: they
  share Document + DocumentEmbedding tables (via pgvector) but
  the LOCAL lane also reads from `.rag/corpus.jsonl` (regenerated
  by `build_rag_corpus`), so the LOCAL lane has a redundant
  representation. Not a contradiction — a redundancy for local
  Ollama use cases.

### 20.6 Conflicts between sources

Per playbook §14 evidence rules.

- **`search_docs` handler line number:** S1301 cited `:5502`;
  Agent 3 cited `:5468`. **Resolved:** both correct — handler
  starts at 5468; inline import of `core.rag.top_k` at line
  5502 within the handler.
- **Row-level provenance orphan claim:** S1301 §19 hypothesized
  both `source_type` + `ingested_via` are orphan. **S1304
  verifier-loop refined:** `source_type` has qualified
  consumers; only `ingested_via` remains F1-CANDIDATE.

### 20.7 Grep patterns used

Documented per playbook §14 audit reproducibility rule; see
individual Explore agents' §7-§10 for full pattern inventories.
Cross-cutting patterns applied at parent-agent verification:

```bash
# Verify Agent 1's source_type read claim
grep -n "source_type" content/embeddings.py

# Verify Agent 3's search_docs handler location
grep -n "_handle_search_docs\|def _handle_search_docs" core/services/td_handlers_ops.py

# Verify Agent 2 + Agent 6 no-beat claim for build_docs_provenance
# (used Grep tool with glob="**/*.py")
build_docs_provenance across repo

# Verify Agent 4 zero-RAG-imports claim
grep -c "search_docs\|kb_tool\|semantic_search\|search_embeddings" core/services/unified_pa_entrypoint.py
```

### 20.8 Scope discipline check

Per parent §5 P4 rationale: boundary lens only.

- [x] No re-audit of Cat D internals — cited S1301 by section.
- [x] No re-audit of Cat E internals — cited DOC_LIFECYCLE.md
      by §.
- [x] No re-audit of Cat A/B/C — cited S1302 by §.
- [x] No re-audit of Cat F — cited S1303 by §; F↔D marked
      out-of-scope in §14 D4.
- [x] Focus preserved on ingestion→retrieval handoff, provenance
      partial-decoupling, cache staleness, boundary ownership.

### 20.9 F4-CANDIDATE discipline application

Per S1303 §14 methodology (owner-model-qualified consumer
inventory required before dead-code claim).

- Applied to `ingested_via` claim: Agent 1 grep + verifier
  spot-check confirmed zero owner-qualified consumers. Verdict:
  **F1-CANDIDATE, not F1-CONFIRMED.** Requires full-tree recheck
  per §19 R1 before deprecation.
- Applied to Cat F ↔ Cat D turn-context wiring: static evidence
  is mixed; declared **design-decision routing (§19 R5)**, not
  drift or dead code.

### 20.10 Gating checklist

- [x] §13 6-parallel Explore sweep launched.
- [x] Load-bearing claims verified via direct file:line read
      (playbook §14 verifier-loop). Four claims: Agent 1
      `source_type` reads (partial S1301 §19 D3 invalidation),
      Agent 3 handler location, Agent 2/6 no-beat schedule,
      Agent 4 zero RAG imports.
- [x] F4-CANDIDATE discipline enforced (`ingested_via` remains
      candidate, not confirmed dead code; Cat F ↔ Cat D routed
      to design-decision).
- [x] Boundary lens preserved (no re-audit of D or E
      internals).
- [x] §1 executive summary populated (~500 words, five gaps
      G1-G5 named).
- [x] §14 known drift consolidated (D1-D4 inherited + D5-D8
      S1304-new).
- [x] §17 duplicate/overlapping surfaces resolved via S1302
      §17.3 methodology (two provenance systems =
      complementary-not-duplicate; two RAG lanes = intentional).
- [x] §19 recommended future research ranked (R1-R8).
- [x] Rigby SIGN cycle 1 routed via fresh isolation pin `pa-2614a91a920642fa`. Verdict: SIGN-with-edits (4 must-fix folds). All 4 folded in place.
- [x] Rigby SIGN cycle 2 (verification pass) verdict: **SIGN-clean**. All 4 folds PASSES independently.
- [x] `sign_status:` frontmatter flipped to SIGN-clean.
- [ ] Chris commit-gate (playbook §16).
