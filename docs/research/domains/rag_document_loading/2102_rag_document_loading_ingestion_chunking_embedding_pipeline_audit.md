---
title: "Session 2102 — Group 2100 P2 Ingestion / Chunking / Embedding Pipeline Audit"
status: active
authority: research
session: 2102
research_group: 2100
child_slot: P2
domain_slug: rag_document_loading
generated: 2026-07-04
head_commit: 7c84ff65
parent_doc: 2100_rag_document_loading_domain_scoping.md
predecessor: 2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/OPEN_ARCS.md
delegates_to:
  - S2103 P3 Retrieval Authority Framework + Corpus Governance Design
  - S2104 P4 Behavior Substrate Structured Observation + Integration
inherits_from:
  - S1304 T1, T2, T4, T5, T6, T7, T8 (Memory docs↔RAG boundary audit)
  - S1399 §19 R1 (ingested_via full-tree read-side sweep)
  - S2001 F3 (SPIDER_DATA MISSING-producer / WEAK consumer pattern)
  - S2001 F9 (dormant-consumer risk pattern)
  - S2101 F1 (source_type='api' monoculture)
  - S2101 F2 (metadata population asymmetry)
  - S2101 F3 D1a/D1b (silent-drop pattern at step 1)
  - S2101 F4 (build_docs_provenance unscheduled)
  - S2101 KD-2 (stale-embed-post-content-change detection substrate)
  - S2101 T4 (docs-ingestion-cascade topic doc unpublished)
verifier_loop: |
  Executed 2026-07-04 at HEAD 7c84ff65. Level A verifier-loop pre-draft
  per START-NEXT §51 step 5: (1) 4 cascade command source samples via 5
  parallel Explore sub-agents (playbook §13 promoted rule);
  (2) _derive_source_type at content/embeddings.py:45-63 read in full;
  (3) three ingested_via write-sites at core/tasks_agents.py:4223/4290/4351
  read with 15-25 line context each; (4) refresh_docs_corpus task body
  read + docs_cascade.py MissionRunner read; (5) DocumentEmbedding
  chunk_size + overlap_size + ingested_via distributions sampled via
  Django shell against local Postgres (n=51,952 chunks LOCAL).
  Chunk-per-doc distribution p50=11, p95=47, p99=169, max=443 confirmed
  matches S2101 baseline (drift ≤0.2%).
owner: claude (drafted S2102 P2)
---

# Group 2100 P2 — Ingestion / Chunking / Embedding Pipeline Audit

> **Second child audit under Group 2100 RAG / Document Loading
> (Knowledge Loop) arc.** Playbook §11.2 20-section child-audit template
> TENTH-consecutive application. Delegated under NINTH Research OS arc
> per parent scoping §5.2. Preserved arc pin `pa-18b095bb7c4740be`
> per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED
> at S1999 close (with S2099 MC-4 scope-guardrail generalization).
>
> **Scope.** The ingestion cascade end-to-end. `build_docs_index` →
> `build_rag_corpus` → `sync_docs_index_to_documents [--embed]` →
> `embed_documents` (via `content/embeddings.RAGSystem`). Two-lane
> structure (LOCAL keyword vs PROD pgvector). Chunking strategy
> analysis. Refresh triggers + cadence. Content-hash / stale-detection
> substrate design space.
>
> **Anti-scope.** No implementation. No schema migrations. No cascade
> command changes. No retrieval ranker changes. Per parent §7.1.

---

## 1. Executive Summary

**What is this domain.** The docs ingestion cascade is the write-side
of the RAG / Document Loading substrate — the mechanism by which
Markdown files on disk (`docs/*.md` + repo-root `CLAUDE.md` +
`00-START-NEXT-SESSION.md`) become searchable knowledge artifacts
in three distinct forms: (a) a JSONL keyword-search corpus for the
LOCAL Ollama-backed `askdocs` lane; (b) `Document` model rows
carrying raw + processed content, metadata, and enrichment; (c)
`DocumentEmbedding` model rows carrying vector representations for
PROD pgvector retrieval. The cascade is nominally a 4-step ordered
mission: index → corpus → sync → embed.

**The biggest gaps.**

**Ranking rubric (Q1 SIGN STRENGTHEN 2026-07-04) — severity × blast
radius × compounding × fix cost.** The audit ranks F1..F8 along
two orthogonal dimensions per Rigby SIGN fold:

- **Impact ranking** (compounding downstream retrieval variance):
  F1 ≥ F3 — chunk-level heterogeneity affects every future
  retrieval query.
- **Architectural-debt ranking** (fracture of ownership,
  observability, safety rails): F3 ≥ F1 — dual-cascade paths
  fracture the entire cascade operation surface.
- **Co-top classification:** F1 and F3 are jointly-first. F1
  bounds every re-chunking / migration design; F3 bounds every
  operational-safety design. F7 EventBus MISSING is the enabling
  substrate for observability of nearly every other finding
  (F4, F8 depend on F7 for cleaner signals).

- **F1 — Three chunkers, three regimes.** Parent §5.2 framed the
  problem as "two-lane LOCAL vs PROD chunking" — the audit refines
  this to **three physical chunkers with distinct regimes**:
  (a) `build_rag_corpus.chunk_text()` fixed 1200-char no-overlap
  no-boundary → LOCAL `.rag/corpus.jsonl`;
  (b) `sync_docs_index_to_documents.chunk_content()` 1000-char +
  200-char overlap + paragraph/sentence boundaries → 24,980 LOCAL
  `DocumentEmbedding` rows via the sync-cascade path;
  (c) `content/embeddings.TextSplitter` 1000-char + 200-char overlap
  + paragraph/sentence boundaries → 26,972 LOCAL `DocumentEmbedding`
  rows via the async-embed path. The two `DocumentEmbedding` sub-
  populations coexist in the same table with different chunker
  provenance and no schema field records which chunker produced
  which chunk.
- **F2 — Overlap-metadata data lie.** All 24,980 sync-cascade chunks
  overlap semantically (200 chars carried across chunk boundaries by
  `chunk_content()` line 432 `start = end - overlap`) but the
  `DocumentEmbedding.overlap_size` field is never set at write time →
  defaults to 0. Downstream retrieval that treats `overlap_size=0` as
  "non-overlapping" over-counts coverage by ~20% for that population.
- **F3 — Dual cascade paths coexist without integration.** Two
  orchestrators run the same 4-step cascade: `refresh_docs_corpus`
  (Celery daily @ 4 AM Denver, hash-delta gated, per-doc embedding
  fan-out, `[DOCS_CORPUS_REFRESH]` log line, NO OpsRun, NO
  escalation) AND `rigby_documentation_manager_daily` →
  `docs_cascade.py` MissionRunner (4-step orchestrator with hard-
  timeout subprocess, step_5 drift observation, OpsRunEvent timeline,
  escalation Deliverable) — but the MissionRunner path has NO beat
  entry and only fires via manual `.delay()` or PA `run_now`. The
  scheduled path has fewer safety rails; the richer path is dormant.
- **F4 — `build_rag_corpus` silent-drop callback is never wired.**
  `iter_corpus_rows(on_warning=None)` supports drop-count telemetry
  but `refresh_docs_corpus` calls `call_command('build_rag_corpus',
  stdout=out, stderr=out)` without wiring a callback, so any file
  that's missing / unreadable / empty at step 2 is dropped without a
  log line. S2101 D1b's "silent-drop telemetry gap" applies verbatim
  to step 2, not just step 1.
- **F5 — `source_type='api'` monoculture root-cause is UPSTREAM.**
  `_derive_source_type` at `content/embeddings.py:45-63` defaults to
  `'unknown'`, NOT `'api'`. The 100% `api` value in LOCAL DB comes
  from `Document.source == 'api'` (or `'imported'`) hitting the 4th
  branch. Discharges S2101 R2.4 by pointing at the upstream write-
  sites, not the derivation function itself.
- **F6 — Backfill dormancy is design intent, not drift.** The three
  `ingested_via='backfill'` write-sites at
  `core/tasks_agents.py:4223/4290/4351` are internal-content
  embeddings (agent dreams / hive-mind sessions / knowledge sources)
  produced by `embed_agent_activity()`, which is NOT scheduled.
  S2101 D5's "0 backfill LOCAL" reclassifies from drift to
  design-intent. `ingested_via='backfill'` is aspirational
  infrastructure.
- **F7 — Neither cascade path emits EventBus events.** Both
  orchestrators are effectively invisible to any external observer.
  MissionRunner uses OpsRunEvent (ORM rows on OpsRun); the daily
  Celery task uses structured logger lines only. Cross-refs S2001 F3
  SPIDER_DATA MISSING-producer as the same architectural pattern
  applied to docs.
- **F8 — Step 4 hard timeout enforced only on the dormant path.**
  `docs_cascade.step_4_embed()` uses `subprocess.run(timeout=1800s)`
  with a 600s warning event; the scheduled `refresh_docs_corpus` path
  has no equivalent wall-clock enforcement for the per-doc embedding
  fan-out. If per-doc embeddings hang (OpenAI dropped conn, network
  stall), the scheduled path has no visibility surface — the
  MissionRunner escalation Deliverable path would surface it but
  isn't wired.

**What should be researched next.**

- **P3 (S2103) — Retrieval Authority Framework + Corpus Governance
  Design.** F1's three-chunker regime, F2's overlap-metadata gap,
  F3's dual-cascade debt, and F6's backfill dormancy all raise
  governance questions (ownership, activation criteria, contract
  enforcement) that P3's 8-axis framework + governance design must
  answer. Metadata contract shape (D2100.9) needs to cover
  `chunker_id` + `overlap_size_actual` + upstream `Document.source`
  provenance.
- **P4 (S2104) — Behavior Substrate Structured Observation.** F5's
  upstream Document.source assignment mechanism + F7's
  observability gap + F8's timeout-only-on-dormant-path pattern feed
  P4 observation targets. If N ≥ 10 observed cases show
  DocumentEmbedding chunker-population imbalance correlates with
  SIGN-quality degradation (via specific query types selecting for
  chunker C's 200-overlap semantic-boundary lane vs chunker B's
  under-recorded overlap lane), Q11 conditional-elevation rule fires
  and F2 elevates from MEDIUM to HIGH.

---

## 2. Domain Purpose

**Question #1 — What is this domain trying to do?** The docs
ingestion cascade converts Markdown source files into three
retrieval-ready knowledge artifact populations: (a) a JSONL
keyword-searchable corpus consumed by `manage.py askdocs` (LOCAL
Ollama lane); (b) `Document` model rows carrying raw + processed
content, enrichment metadata, and per-document status; (c)
`DocumentEmbedding` model rows carrying chunk-level vector
embeddings for PROD pgvector semantic retrieval.

The substrate is one half of the write-side pair: this audit covers
the write half (ingestion → corpus → embed); S2101 covered the
retrieval-adjacent read half via the Corpus State snapshot.

**Question #2 — What are the actors?** Primary actor is
`refresh_docs_corpus` Celery task (daily @ 4 AM Denver), which
dispatches four sub-actors: `build_docs_index` (index scan),
`build_rag_corpus` (JSONL keyword corpus), `sync_docs_index_to_documents`
(Document row create/update), and per-doc `generate_document_embeddings`
Celery fan-out for the embed step. Secondary orchestrator is
`docs_cascade.py` MissionRunner, dormant. Human actors: developers
running `python manage.py <cmd>` invocations directly (documented in
each command's docstring examples). Rigby (as Documentation Manager
per Employee OS) has manual `run_now` on the MissionRunner path.

**Boundaries.**
- IN scope: the 4-step cascade, its two orchestrators, its three
  chunkers, its four database write-sites, its cadence + refresh
  triggers, its content-hash substrate, its silent-drop telemetry.
- OUT of scope: `AgentMemory` / two-lane conversation memory
  (Group 1300 territory per parent §7.2); EventBus / HAI event
  contracts (Group 2000+ territory per parent §7.3); pipeline
  implementation changes (parent §7.1 anti-scope).

---

## 3. Canonical Entry Points

The cascade has four command entry points, two orchestrator entry
points, one API endpoint, and one direct-import service surface.

**Exhaustiveness method (Q2 SIGN STRENGTHEN 2026-07-04).** Entry-point
enumeration performed via: (a) `find core/management/commands -maxdepth 2 -type f -name "*.py"`
grep for the four canonical cascade command names; (b) source read
of `core/management/commands/embed_documents.py`; (c) source read of
`content/embeddings.py:395-1105` for `RAGSystem` surface; (d) source
read of `core/tasks.py:5802-5946` (`refresh_docs_corpus`), `core/tasks_documentation_manager.py:104-131`,
`core/jobs/docs_cascade.py:352-751`; (e) grep for `DocumentEmbedding.objects.create(`
across `core/tasks_agents.py`, `content/embeddings.py`, `sync_docs_index_to_documents.py`.
**Potential additional entrypoint pending sweep:** `content/rag_integration.py`
write-side has NOT been fully swept in this audit — noted for R2.9
follow-up. If a write-site exists there, F1 chunker inventory needs
extension. Similarly, `core/tasks_misc.py` beyond the wrapper at line
1728 was not audited for other embedding write-sites.

### 3.1 Management commands (STEP 1..4)

| Step | Command | File | Lines | Purpose | Args |
|------|---------|------|-------|---------|------|
| 1 | `build_docs_index` | `core/management/commands/build_docs_index.py` | 1,112 | Walk `docs/` + repo roots, write `docs/_index.json` (schema v2.2) | `--dry-run`, `--json-only` |
| 2 | `build_rag_corpus` | `core/management/commands/build_rag_corpus.py` | 178 | Read `_index.json` + walk source files, write `.rag/corpus.jsonl` | `--index`, `--output`, `--chunk-size=1200`, `--dry-run` |
| 3 | `sync_docs_index_to_documents` | `core/management/commands/sync_docs_index_to_documents.py` | 434 | Sync `_index.json` → `Document` rows; optional `--embed` chunks + `DocumentEmbedding` rows via own `chunk_content()` | `--dry-run`, `--active-only`, `--embed`, `--limit` |
| 4a | `embed_documents` | `core/management/commands/embed_documents.py` | 70 | Per-doc embedding via `content.embeddings.RAGSystem.process_document_for_rag_sync()` | `document_ids` (positional), `--all-unembedded`, `--type`, `--model=openai_small`, `--async` |
| 4b | `sync_docs_index_to_documents --embed` | (same as step 3) | 434 | Alternate embed entry: STEP 3 output triggers own `generate_embeddings()` inline synchronously | `--embed` flag on step 3 |
| supp | `build_docs_provenance` | `core/management/commands/build_docs_provenance.py` | (S1145 Plan B) | Generate `docs/_provenance.json` (git commit ancestry → session confidence tier) | `--dry-run`, `--include-archive` |
| supp | `backfill_doc_provenance` | `core/management/commands/backfill_doc_provenance.py` | (S1145 Plan B) | Write `originating_session:` YAML frontmatter for HIGH-confidence tier | (varies) |

### 3.2 Cascade orchestrators

| Path | Entry | File | Cadence | Path Type |
|------|-------|------|---------|-----------|
| **Path A (scheduled)** | `refresh_docs_corpus` Celery task | `core/tasks.py:5802-5946` | `crontab(hour=4, minute=0)` Denver daily (`core/celery.py:495-499`) | Lightweight; hash-delta gate; per-doc embed fan-out |
| **Path B (dormant)** | `rigby_documentation_manager_daily` Celery task | `core/tasks_documentation_manager.py:104-131` | UNSCHEDULED — no beat entry | MissionRunner 4-step; hard-timeout subprocess for step 4; drift observation; escalation Deliverable |
| **Path B factory** | `build_docs_manager_runner()` | `core/jobs/docs_cascade.py:699-751` | (via Path B task) | Wires steps 1-4 into MissionRunner + emits OpsRunEvent timeline |

### 3.3 Direct-call service

| Entry | Location | Callers |
|-------|----------|---------|
| `RAGSystem` (singleton) | `content/embeddings.py:395-1105` | `embed_documents.py:63`; `core/tasks_misc.py:1766`; `core/views_rag_embeddings.py:105-110`; `core/tasks.py:12974` |
| `RAGSystem.process_document_for_rag()` (async) | `content/embeddings.py:600-696` | (async caller — used via API endpoint) |
| `RAGSystem.process_document_for_rag_sync()` (sync) | `content/embeddings.py:702-792` | `embed_documents.py:65`; Celery `generate_document_embeddings` task |

---

## 4. Major Models

Per playbook §12 field types + severity.

| Model | File | Role | Key fields |
|-------|------|------|-----------|
| `Document` | `content/models.py` | Doc-level content + enrichment | `title`, `file_path`, `raw_content`, `processed_content`, `content_hash`, `source`, `document_type`, `status`, `extracted_metadata` (JSONField, cumulative), enrichment fields (`category`, `tags`, `document_class`, `is_pinned`, `retrieval_boost` per S1234 D9) |
| `DocumentEmbedding` | `content/models.py:~737-810` | Chunk-level vector + provenance | `document` (FK), `chunk_index`, `chunk_text`, `chunk_size`, `overlap_size` (default 0), `embedding_vector`, `embedding_dimension`, `embedding_model` (enum), `processing_time_ms`, `embedding_cost`, `metadata` (JSONField, default={}), `source_type` (derived), `ingested_via` (choices per §810-823: `auto_research`, `manual`, `spider_pipeline`, `sync_docs`, `backfill`, `unknown`) |
| `OpsRun` (`domain='mission'`) | `core/models_ops_runs.py` | MissionRunner audit trail | `run_key` (dedupe), `status`, `mission_class`, `started_at`, `finished_at`, `escalated`, `context` (JSONField) |
| `OpsRunEvent` | `core/models_ops_runs.py` | Timeline events per run | `run` (FK), `label`, `event_type`, `detail` (JSONField), `emitted_at` |
| `EmbeddingModel` (enum) | `content/models.py:116-123` | Model provenance | 6 choices: `openai_text_embedding_3_small`, `openai_text_embedding_3_large`, `openai_text_embedding_ada_002`, `sentence_transformer`, `cohere_embed_english`, `local_model` |

**Field integrity observations:**
- `Document.file_path` is the natural key for cascade sync (per
  `sync_docs_index_to_documents.py:261-263`); no `content_hash`
  primary lookup.
- `DocumentEmbedding.overlap_size` is populated only by the async
  path (`content/embeddings.py:645-646`). Sync-cascade path leaves
  it at model default 0 despite chunking with 200-char overlap.
  → F2.
- `DocumentEmbedding.metadata` is populated only by the async path
  (`content/embeddings.py:642-656`, 3 fields:
  `document_id`, `document_title`, `document_type`).
  Sync-cascade path leaves it at model default `{}`. → S2101 F2.
- `DocumentEmbedding.embedding_model` is populated (100% =
  `openai_text_embedding_3_small` LOCAL — unified, zero drift risk
  observed).
- `DocumentEmbedding.source_type` is populated by `_derive_source_type`
  at all three chunker sites (100% `'api'` LOCAL). → S2101 F1 root-
  cause: upstream `Document.source`. → F5.
- No `chunker_id` field exists. No `chunking_version` field exists.
  No `content_hash_at_chunk_time` field exists. → KD-2 substrate.

---

## 5. Major Services

| Service | Location | Role |
|---------|----------|------|
| `RAGSystem` | `content/embeddings.py:395-1105` | Coordinates provider registry (OpenAI + SentenceTransformer + Cohere), chunker (`TextSplitter`), embedding generation, `DocumentEmbedding` writes, semantic search API |
| `TextSplitter` | `content/embeddings.py:395-512` | Default chunker: 1000 char + 200 char overlap; paragraph-first + sentence-fallback boundary preservation via `_split_large_paragraph()` + `_get_overlap_text()` |
| `VideoTranscriptSplitter` | `content/embeddings.py:515-590` | Video-specific chunker; adds `start_ms`/`end_ms` timestamp metadata |
| `EmbeddingService` | `content/embeddings.py:~340-395` | Provider registry: OpenAI (small/large/ada) + SentenceTransformer + Cohere; conditional init based on `HAS_OPENAI` / `HAS_COHERE` + settings keys |
| `MissionRunner` | `core/jobs/mission_runner.py` (per Employee OS primitive) | Executes preflight → step_1..N → postflight → verdict → escalation; consumes `AIEmployee` + `JobContract` + step callable list; writes `OpsRun` + `OpsRunEvent` rows |
| `ErrorSignatureClassifier` | `core/jobs/error_signature.py` | Computes `(failed_step, error_tail[:100])` signature for escalation dedupe (24h window default) |
| _(implicit)_ Local corpus chunker | `core/management/commands/build_rag_corpus.py:49-54` | `chunk_text()`: pure `text[i:i+1200]`; no overlap, no boundary; produces `.rag/corpus.jsonl` |
| _(implicit)_ Sync-cascade chunker | `core/management/commands/sync_docs_index_to_documents.py:408-434` | `chunk_content()`: 1000 char + 200 char overlap + paragraph/sentence boundary; **THIRD chunker** — not `TextSplitter` |

---

## 6. Major APIs and Interfaces

### 6.1 CLI (management commands)

Per §3.1 table above. All commands invocable via
`python manage.py <cmd> [args]`. Callers within the codebase use
`django.core.management.call_command()` (in-process) or
`subprocess.run(['python', 'manage.py', ...], timeout=…)` (subprocess
for hard-timeout enforcement — only used at Path B step 4).

### 6.2 Celery task entrypoints

| Task | Route | Cadence | Purpose |
|------|-------|---------|---------|
| `core.tasks.refresh_docs_corpus` | queue=`default` | daily @ 4 AM Denver | Path A orchestrator |
| `core.tasks.generate_document_embeddings` | queue=`default` (fan-out target) | per-doc dispatch | Async embedding of a single Document |
| `core.tasks_documentation_manager.rigby_documentation_manager_daily` | (no beat entry) | UNSCHEDULED | Path B orchestrator |
| `core.tasks.embed_agent_activity` (via `core/tasks_agents.py:_impl_embed_agent_activity`) | (no beat entry) | UNSCHEDULED | Backfill flow (dreams / hive minds / knowledge sources); F6 |
| `core.tasks.backfill_spider_embeddings` | queue=`ml` | every 15 min via `crontab(minute='*/15')` (`core/celery.py:364-369`) | Spider-data embedding backfill; LOCAL_DENY_TASKS excludes locally |

### 6.3 HTTP endpoint

- `POST /api/rag/embeddings/` (per `core/views_rag_embeddings.py:105-110`) —
  triggers async `process_document_for_rag()` on a Document instance.

### 6.4 MissionRunner step contract (Path B)

Per `core/jobs/docs_cascade.py:699-751`:

- `step_1_build_docs_index` (line 352-355) — `call_command('build_docs_index')`
- `step_2_build_rag_corpus` (line 358-361) — `call_command('build_rag_corpus')`
- `step_3_sync_docs_index_to_documents` (line 364-367) — `call_command('sync_docs_index_to_documents')`
- `step_4_embed` (line 370-377) — `subprocess.run(['python', 'manage.py', 'sync_docs_index_to_documents', '--embed'], timeout=1800s)`; warning at 600s

Emits `step_N_<label>_started`, `step_N_<label>_passed` / `_failed` /
`_timeout` (step 4 only), `step_4_warning`, `step_5_drift_observed`,
`mission_started`, `mission_passed`, `mission_failed`,
`mission_escalated`, `authority_contract_observed`.

---

## 7. Runtime Flows

### 7.1 Path A — `refresh_docs_corpus` (scheduled, lightweight)

```
   ┌─────────────────────────────────────────────────────┐
   │ Celery beat: crontab(hour=4, minute=0) Denver time  │
   │ Queue: default   Soft: 600s   Hard: 720s            │
   └──────────────────────┬──────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ refresh_docs_corpus() @ core/tasks.py:5802          │
   │                                                     │
   │ Two-trigger gate:                                   │
   │   (a) SHA256(docs/_index.json) vs cached hash       │
   │       key='docs_corpus:last_index_hash' :5858       │
   │   (b) unembedded Document count > 0 :5869-5875      │
   │                                                     │
   │ If (!a && !b && !force) → SKIP + log                │
   │     [DOCS_CORPUS_REFRESH_SKIP] :5880                │
   └──────────────────────┬──────────────────────────────┘
                          │ (gate passes)
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ Cascade steps 1-3 via call_command() (in-process)   │
   │  :5900  build_docs_index                            │
   │  :5901  build_rag_corpus                            │
   │  :5902  sync_docs_index_to_documents (no --embed)   │
   │                                                     │
   │ If any raises → [DOCS_CORPUS_REFRESH_CASCADE_FAIL]  │
   │   :5905 (task fails soft)                           │
   └──────────────────────┬──────────────────────────────┘
                          │ (steps 1-3 pass)
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ Per-doc embed fan-out :5931-5933                    │
   │  for doc_id in unembedded_qs.values_list('id'):     │
   │      generate_document_embeddings.delay(            │
   │          str(doc_id), 'openai_small')               │
   │      embedding_tasks_dispatched += 1                │
   └──────────────────────┬──────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ Cache updated :5936; log [DOCS_CORPUS_REFRESH]      │
   │ :5939 index_changed=%s unembedded_before=%d         │
   │       tasks_dispatched=%d took=%.2fs hash=%s        │
   │ Return {success, index_changed, unembedded_before,  │
   │  sync_summary, embedding_tasks_dispatched,          │
   │  took_seconds, hash_short}                          │
   └─────────────────────────────────────────────────────┘
```

**Observability surface:** structured logger lines only; no EventBus
emission; no OpsRun row.

### 7.2 Path B — `docs_cascade.py` MissionRunner (dormant, full-lifecycle)

```
**OpsRun.status transitions per milestone (Q3 SIGN STRENGTHEN 2026-07-04):**

- Preflight: `created` (row insert) → `running` (mission_started emit)
- Steps 1-4: `running` throughout (no per-step status flip)
- Postflight success: `running` → `passed` (mission_passed emit)
- Postflight failure: `running` → `failed` (mission_failed emit)
- Postflight partial: `running` → `partial` (documented in Employee OS
  primitive contract; not observed in this audit's LOCAL sample)
- Escalation branch: `failed` → (dedupe classifier) → Deliverable emit
  → status unchanged (Deliverable is separate row)

**Authority contract hook timing (Q3 SIGN STRENGTHEN 2026-07-04).**
`authority_contract_observed` is a Session 1264 warn-mode observation
event emitted during preflight, BEFORE step_1. Its purpose:
observability, not gating (warn-mode not enforce-mode). If
Employee OS binding is present, this event confirms the mission is
running under a recognized `JobContract` from `core/employees/jobs.py`.
Absence would indicate contract lookup failed — mission would still
proceed under warn-mode.

   ┌─────────────────────────────────────────────────────┐
   │ Trigger: manual .delay() OR PA run_now              │
   │ (NO beat schedule entry)                            │
   └──────────────────────┬──────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ rigby_documentation_manager_daily()                 │
   │   @ core/tasks_documentation_manager.py:104-131     │
   │   → build_docs_manager_runner() @ docs_cascade.py:699│
   │   → MissionRunner.run()                             │
   └──────────────────────┬──────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ PREFLIGHT :~600                                     │
   │  → Emit mission_started event on OpsRun             │
   │  → Idempotency check (calendar day + run_key)       │
   └──────────────────────┬──────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ STEP 1 :352-355   step_1_index_started              │
   │  call_command('build_docs_index')                   │
   │  In-process. No hard timeout.                       │
   │  → step_1_index_passed / _failed                    │
   └──────────────────────┬──────────────────────────────┘
                          │ (pass)
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ STEP 2 :358-361   step_2_corpus_started             │
   │  call_command('build_rag_corpus')                   │
   │  In-process. No hard timeout.                       │
   │  → step_2_corpus_passed / _failed                   │
   └──────────────────────┬──────────────────────────────┘
                          │ (pass)
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ STEP 3 :364-367   step_3_sync_started               │
   │  call_command('sync_docs_index_to_documents')       │
   │  In-process. No hard timeout.                       │
   │  → step_3_sync_passed / _failed                     │
   └──────────────────────┬──────────────────────────────┘
                          │ (pass)
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ STEP 4 :370-377   step_4_embed_started              │
   │  subprocess.run(                                    │
   │    ['python', 'manage.py',                          │
   │     'sync_docs_index_to_documents', '--embed'],     │
   │    timeout=1800s                                    │
   │  )                                                  │
   │  Soft warning at 600s → step_4_warning event        │
   │  → step_4_embed_passed / _failed / _timeout         │
   └──────────────────────┬──────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ POSTFLIGHT :607-679                                 │
   │  On success:                                        │
   │    → verify_doc_claims --only-drift --format json   │
   │    → step_5_drift_observed event (drift_count,      │
   │      drift_items_count, source)                     │
   │  On any prior failure:                              │
   │    → step_5_skipped (reason=prior_failure)          │
   └──────────────────────┬──────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │ VERDICT + ESCALATION                                │
   │  If failure:                                        │
   │    → ErrorSignatureClassifier.compute(step, tail)   │
   │    → Deduped Deliverable (24h dedupe window)        │
   │    → mission_escalated event                        │
   └─────────────────────────────────────────────────────┘
```

**Observability surface:** OpsRunEvent ORM rows on OpsRun row per
mission. Idempotent, replayable via ORM query. No EventBus.

### 7.3 Chunking regime map

Same table (`DocumentEmbedding`) holds chunks from three different
chunkers with three different regimes.

| Chunker | File:Lines | Chunk size | Overlap | Boundary | Where chunks land | LOCAL count |
|---------|-----------|-----------|---------|----------|--------------------|-------------|
| **A** `chunk_text()` | `build_rag_corpus.py:49-54` | 1200 char (fixed) | 0 | none | `.rag/corpus.jsonl` | 30,974 lines (LOCAL keyword lane; NOT in DocumentEmbedding) |
| **B** `chunk_content()` | `sync_docs_index_to_documents.py:408-434` | 1000 char | 200 char | paragraph → sentence | `DocumentEmbedding` (`ingested_via='sync_docs'`) | 24,980 chunks (mean=849.9) |
| **C** `TextSplitter.split_text()` | `content/embeddings.py:395-512` | 1000 char | 200 char | paragraph → sentence | `DocumentEmbedding` (`ingested_via='unknown'` by default) | 26,972 chunks (mean=804.6) |

Populations B + C = 51,952 chunks total LOCAL (matches
`DocumentEmbedding.objects.count()`; 163 chunks above S2101 baseline
51,789 — daily beat fire since S2101 close).

**Empirical divergence** (per ORM verifier-loop 2026-07-04 20:22):
- Overall chunk_size: mean=826.4, median=889, p95=1000, p99=1125
- 63.3% of chunks in 800-1000 bucket (tail chunks shorter than
  configured 1000)
- 0.0% exactly at 1200 char (Chunker A operates on JSONL, not DB)
- overlap_size distribution: 26,072 chunks with 0 (all 24,980
  sync_docs + 1,092 first-chunks from async); 25,880 chunks with
  200 (all middle/tail chunks from async path)

Chunker A's LOCAL corpus.jsonl is measured as 10.66 chunks/file
per S2101 §14 baseline (fixed 1200-char no-overlap → fewer chunks
per file). Chunkers B + C on `DocumentEmbedding` yield 17.85
chunks/doc mean → the 20% higher chunk count is **entirely
explained by** the 200-char overlap + shorter chunk size (1000 vs
1200) + boundary shortening (some paragraphs break earlier than the
1000-char cap).

### 7.4 Cadence + refresh triggers

| Trigger | Path | Cadence | Notes |
|---------|------|---------|-------|
| Celery beat | Path A | daily @ 4 AM Denver | `crontab(hour=4, minute=0)`; `refresh-docs-corpus-daily` in `core/celery.py:495-499` |
| Content-hash delta | (Path A gate) | on beat fire | SHA256 on `docs/_index.json`; cache key `docs_corpus:last_index_hash` |
| Unembedded-doc gate | (Path A gate) | on beat fire | `Document.filter(embeddings__isnull=True).exists()` |
| `--force` flag | Path A | operator | Bypasses gate |
| Manual `.delay()` | Path A or B | operator/PA | Bypasses beat |
| Rigby `run_now` | Path B | Rigby manual | Via PA `run_now` action |
| File-watch | (none) | — | No file-watcher triggers cascade |
| Content-hash-per-file | (none) | — | KD-2 substrate; not implemented (`Document.content_hash` exists but no per-chunk hash and no chunk-time content-hash comparison at re-embed time) |
| Embedding-model change | (none) | — | No auto-invalidation; 100% model=`openai_text_embedding_3_small` LOCAL |

### 7.5 Failure modes per step

| Step | Path A failure mode | Path B failure mode |
|------|---------------------|---------------------|
| 1 | `call_command` raises → task logs `[DOCS_CORPUS_REFRESH_CASCADE_FAIL] stage=cascade_1_3` → return `{success: False, stage: 'cascade_1_3'}` | Runner catches SystemExit/Exception → `StepResult(passed=False)` → mission fails; drift observation skipped; escalation Deliverable emitted |
| 2 | Same as 1 | Same as 1 |
| 3 | Same as 1 | Same as 1 |
| 4 | Per-doc `.delay()` dispatched fire-and-forget; per-doc soft timeout 600s (from `generate_document_embeddings` decorator); no wall-clock timeout on the parent task's `4a` phase | subprocess hard timeout 1800s → `TimeoutExpired` → `StepResult(passed=False, was_timeout=True)`; escalation classifies as timeout |

**F8** — Path A step 4 has no wall-clock enforcement on the
per-doc fan-out; if OpenAI drops conns, each doc's soft-limit fires
independently but no aggregate signal. Path B step 4 has the
enforcement but is dormant.

---

## 8. Data Ownership and Lifecycle

### 8.1 Artifact ownership matrix

| Artifact | Owner (produces) | Consumer (reads) | Lifecycle |
|----------|-----------------|-------------------|-----------|
| `docs/_index.json` | STEP 1 (`build_docs_index`) | STEP 2, STEP 3, `refresh_docs_corpus` gate | Rewritten every cascade run (v2.2 schema hardcoded) |
| `.rag/corpus.jsonl` | STEP 2 (`build_rag_corpus`) | `core/rag.py:top_k()` for LOCAL askdocs/Ollama | Rewritten every cascade run; not consumed by PROD RAG |
| `Document` rows | STEP 3 (`sync_docs_index_to_documents`) | STEP 4, `content/embeddings.RAGSystem`, retrieval | Create-on-new-path / update-on-content-hash-delta; `file_path` is natural key |
| `DocumentEmbedding` rows (population B) | STEP 3 `--embed` path via `chunk_content()` | `content/rag_integration.py` semantic retrieval | Written once per doc-embed cycle; no per-chunk regeneration |
| `DocumentEmbedding` rows (population C) | STEP 4 via `TextSplitter` / `RAGSystem.process_document_for_rag[_sync]()` | Same as B | Same as B |
| `DocumentEmbedding` rows (population D — backfill) | `embed_agent_activity()` (dormant) | Retrieval (if enabled) | Never written LOCAL (F6) |
| `docs/_provenance.json` | `build_docs_provenance` (manual) | Documentation Manager mission postflight; deliverable auditors | Manual regeneration; no beat |
| `OpsRun` (`domain='mission'`) | MissionRunner (Path B) | Escalation classifier; audit deliverables | Idempotent per (calendar day, run_key) |
| `OpsRunEvent` | MissionRunner postflight | Downstream observers via ORM | Append-only |

### 8.2 Chunk lifecycle

```
   File on disk
   ─────┬──────
        │
        ▼
   Discovered by build_docs_index      → docs/_index.json entry
        │
        ▼
   Read by build_rag_corpus.chunk_text() → .rag/corpus.jsonl JSONL row
        │
        ▼
   Read by sync_docs_index_to_documents → Document row (create/update)
        │
        ▼
   ┌───┴──────────────────────────────────────────┐
   │                                              │
   ▼                                              ▼
 STEP 3 --embed inline                    STEP 4 dispatch or API
 chunk_content() 1000/200                 TextSplitter 1000/200
   │                                        │
   │                                        │
   ▼                                        ▼
 DocumentEmbedding                        DocumentEmbedding
 ingested_via='sync_docs'                 ingested_via='unknown'
 overlap_size=0 (data lie)                overlap_size=0 or 200 correct
 metadata={} (empty)                      metadata={doc_id, title, type}
```

**Chunks do not carry:**
- `chunker_id` (which of A/B/C produced them)
- `chunker_version` (config used at chunk time)
- `content_hash_at_chunk_time` (KD-2 substrate)
- `head_commit_at_chunk_time` (KD-3 substrate)
- `overlap_size_actual` for population B (F2)

### 8.3 Content-hash substrate maturity

- `Document.content_hash` field EXISTS. Populated at
  `sync_docs_index_to_documents.py:262-267, 297, 341` (used for
  create-vs-update decision at doc level).
- **NO chunk-level content hash exists.**
- `refresh_docs_corpus` gate uses SHA256 on `docs/_index.json` file
  bytes, NOT any per-doc or per-chunk content hash.
- **KD-2 detection substrate** (stale-embed-post-content-change) is
  NOT operational; requires new field(s) at chunk time.

---

## 9. Integrations With Other Domains

Per playbook §12 STRONG / WEAK / MISSING / OVERCOUPLED / UNKNOWN
integration classifications.

| Pair | Direction | Integration | Cite |
|------|-----------|-------------|------|
| Docs ingestion ↔ Documentation Manager (Employee OS) | ↔ | STRONG for Path B (MissionRunner is Documentation Manager's job execution surface); **OVERCOUPLED / MIS-BOUND for Path A** (Q5 SIGN STRENGTHEN 2026-07-04 reclassification — Path A executes scheduled work that Documentation Manager owns per Employee OS intent, but no mission/ownership contract binding exists; scheduled work happens OUTSIDE the Employee OS binding) | `core/tasks_documentation_manager.py:104-131`, `docs_cascade.py:699-751` |
| Docs ingestion ↔ Corpus State (P1 audit territory) | → | STRONG | This audit builds on S2101 §14/§15/§19.1 baseline |
| Docs ingestion ↔ Retrieval Authority (P3 territory) | → | MISSING at metadata contract level | D2100.9 hybrid contract must cover chunker provenance + overlap_size accuracy + Document.source semantics |
| Docs ingestion ↔ Behavior Substrate (P4 territory) | → | MISSING for structured observation | P4 tests F5 upstream-Document.source hypothesis + F1 chunker-population imbalance hypothesis |
| Docs ingestion ↔ AgentMemory (Group 1300) | ↔ | STRONG for retrieval (S1304 canonical baseline); OUT OF SCOPE for write-side per parent §7.2 | Parent scoping §7.2 |
| Docs ingestion ↔ EventBus (Group 2000+) | → | MISSING (F7) | Cross-refs S2001 F3 SPIDER_DATA MISSING-producer pattern; parent §7.3 defers Group 2000+ territory |
| Docs ingestion ↔ Spider network | → | MISSING for docs; `backfill_spider_embeddings` handles spider-data separately at 15-min cadence | `core/celery.py:364-369` |
| Docs ingestion ↔ Provenance | ↔ | WEAK | `build_docs_provenance` produces `docs/_provenance.json`; consumers include Documentation Manager postflight + `_load_provenance_docs()` @lru_cache with S1304 T2 staleness |
| Docs ingestion ↔ Rigby PA tools | → | STRONG for retrieval (Rigby's RAG queries via `content/rag_integration.py`) | S1304 baseline; Group 1300 territory |
| Docs ingestion ↔ Frontend/UI | → | MISSING for cascade telemetry | No UI observation surface for docs-ingestion state |
| Docs ingestion ↔ Discord | → | MISSING | No cross-integration |
| Docs ingestion ↔ Signal aggregation | → | MISSING | No signal-cluster emission from cascade |

**S2001 F3 cross-reference (playbook §7 requirement).** S2001 F3
found `SPIDER_DATA` events had MISSING producer / WEAK consumer.
The docs-cascade EventBus pattern is the same: MISSING producer
(neither Path A nor Path B publishes to EventBus) + WEAK consumer
(observers rely on ORM queries against OpsRun/OpsRunEvent for Path B
or `grep [DOCS_CORPUS_REFRESH]` in logs for Path A). This is F7.

---

## 10. Event Flows

### 10.1 EventBus emissions

**NONE from either cascade path.** No `event_bus.publish(...)` call
in `refresh_docs_corpus`, `docs_cascade.py`, or the four cascade
commands (grep confirmed). → **F7**.

### 10.2 OpsRunEvent emissions (Path B only)

Per `docs_cascade.py:124-139, 212-246, 383-465, 607-679`:

- `mission_started` (preflight)
- `authority_contract_observed` (per Session 1264 warn-mode)
- `step_1_index_started` / `_passed` / `_failed`
- `step_2_corpus_started` / `_passed` / `_failed`
- `step_3_sync_started` / `_passed` / `_failed`
- `step_4_embed_started` / `_warning` / `_passed` / `_failed` / `_timeout`
- `step_5_drift_observed` (postflight, on success) or `step_5_skipped` (postflight, on prior failure)
- `mission_passed` / `mission_failed`
- `mission_escalated` (if error-signature classifier fires
  Deliverable)

All rows land on `OpsRun` (`domain='mission'`) row. Query surface is
ORM only.

### 10.3 Logger emissions

**Path A:**
- `[DOCS_CORPUS_REFRESH_SKIP]` (line 5880) — gate no-op
- `[DOCS_CORPUS_REFRESH_CASCADE_FAIL]` (line 5905) — steps 1-3 fail
- `[DOCS_CORPUS_REFRESH]` (line 5939) — full run summary

**Path B:** all timeline events are OpsRunEvent rows; the runner
does not emit `logger.info` for step transitions.

**Cascade commands:**
- `build_docs_index`: 5 `logger.warning` sites (title/frontmatter/
  links/count/session extraction failures) + 5 stdout style writes
  (error/warning/success)
- `build_rag_corpus`: no `logger` sites; only `self.stdout` style
  writes; **`iter_corpus_rows(on_warning=None)` callback OPTIONAL**;
  `refresh_docs_corpus` never passes a callback → **F4**
- `sync_docs_index_to_documents`: stats-based stdout output only
- `embed_documents` / `content/embeddings.RAGSystem`: `logger.info`/
  `logger.error` at chunk failure boundaries

### 10.4 What events should exist that don't

Per F7 and R2.6 from S2101 §19.1. Per **Q6 SIGN STRENGTHEN
2026-07-04**, the 7 candidate events split into three event
classes (state-transition milestones / delta-events / alerts) with
different emission cardinalities and different downstream
subscribers. Recommended two-layer design:

**Layer 1 — Coarse EventBus milestones** (cross-service
subscribers; low cardinality; every cascade run):
- `docs_cascade.completed` — full cascade success (or bundled `_failed`)
- `docs_cascade.drift_detected` — postflight step_5 emission

**Layer 2 — Detailed OpsRunEvent** (canonical query surface for
docs-substrate observers; per-step + delta payload; every run):
- `step_1_index_built` (delta: docs indexed, silent-drops)
- `step_2_corpus_built` (delta: chunks written, silent-drops)
- `step_3_documents_synced` (delta: created / updated / errored)
- `step_4_embeddings_completed` (delta: chunks embedded, cost)

**Alert-class events** (rate-limited; anomaly signals only):
- `docs_cascade.silent_drop` — emitted only when D1a/D1b/F4 gap
  observed (mismatch between index count and downstream row count)
- `docs_cascade.chunker_regime_change` — emitted only on F1
  chunker version bump

P3 design output: whether to emit Layer 1 to EventBus + Layer 2
via OpsRunEvent promotion query API + Layer 3 as rate-limited
alerts, or fold into a unified surface. The two-layer split
prevents EventBus cardinality noise from swamping cross-service
subscribers while keeping fine-grained observability queryable
via ORM.

---

## 11. Existing Documentation

| Doc | Location | Status | Purpose |
|-----|----------|--------|---------|
| `docs/topics/docs-ingestion-cascade.md` | (NOT YET WRITTEN) | S1304 T4 STILL-VALID → S2101 T4 → S2102 R3.1 discharges | Topic doc unpublished; R3.1 delivers |
| S1304 `1304_memory_docs_rag_boundary_audit.md` | `docs/research/domains/memory/` | canonical (Group 1300) | Baseline for docs↔RAG boundary; S1304 D3 (source_type/orphan-write, refuted at S1304 verifier) — refined by F5 here |
| S2101 P1 audit | `docs/research/domains/rag_document_loading/2101_...` | active | This audit's predecessor; verifier-loop evidence at S2101 §20 |
| Parent scoping S2100 | `docs/research/domains/rag_document_loading/2100_...` | active | 10 D-verdicts RATIFIED; §5.2 defined this audit's scope |
| `docs/topics/personal-assistant.md` | `docs/topics/` | active | Rigby's retrieval consumer surface (context only) |
| `MEMORY.md` rules (feedback_docs_pipeline_4_step_cascade, feedback_docs_cascade_at_every_close, feedback_cascade_pr_must_include_embed_step) | user auto-memory | active | Governance around cascade discipline; **R3.4 candidate for canonical governance doc** per parent §5.3 |
| CLAUDE.md live-counts autoblock (Frontend row 4th line: "docs cascade / cadence") | `CLAUDE.md` | auto-generated | No direct row for docs cascade but implicit via task counts (~415 tasks) |

**Research Coverage classification: MODERATE** — dedicated
S1304 boundary audit + S2101 corpus state + this P2; but no
canonical topic doc yet. R3.1 discharges.

---

## 12. Research Coverage

Per playbook §12 classifications:

- **Prior audits:** S1304 (Group 1300 Memory docs↔RAG boundary
  — canonical baseline); S2101 Group 2100 P1 (Corpus State); S1145
  Plan B (provenance-index); S1234 D9 (Document enrichment retrofit);
  S1235 P5#1 (metadata clobber self-heal); S1252/S1253 (MissionRunner
  cascade lift, incomplete beat wiring).
- **Prior handoff research:** S1268-S1275 foundational + S1276
  playbook v2 (methodology).
- **Coverage classification: MODERATE.** Multiple focused docs,
  but no canonical topic doc + no design-preparation doc for
  chunker-provenance metadata + no ADR for dual-cascade path
  reconciliation.

---

## 13. Architecture Maturity

Per playbook §12 maturity classifications.

**Maturity classification: PARTIAL.**

**Tipping rule (Q7 SIGN STRENGTHEN 2026-07-04) — PARTIAL vs WORKING.**
For this substrate class, WORKING requires all three conditions:

1. **Canonical or explicitly governed dual-path** — single
   cascade orchestrator OR explicit dual-path design with
   defined activation criteria for each.
2. **Reliable end-to-end embed completion with backstops** —
   per-doc dispatch has aggregate completion signal + retry /
   escalation for hangs (not just per-doc soft-timeout).
3. **Basic observability** — OpsRun or EventBus surface for
   step transitions + drift / alerting on anomalies.

Lacking any two conditions → PARTIAL. This substrate lacks
condition (1) (F3 dual-cascade), condition (2) (F8 per-doc
aggregate cap), and condition (3) (F7 EventBus MISSING) — three
of three. PARTIAL is honest.

- **Works in places:**
  - Path A hash-delta gate is efficient and honest about no-op cases
    (S1235 remediation of unembedded-count trigger).
  - Path B MissionRunner has hard-timeout + drift observation +
    escalation Deliverable design — comprehensive.
  - `Document` model enrichment (S1234 D9) + metadata self-heal
    (S1235 P5#1) show iterative hardening.
- **Not cohesive or fully wired:**
  - Path B never fires (dormant scheduling) → F3.
  - Three chunkers produce heterogeneous `DocumentEmbedding`
    populations with no chunker-provenance field → F1.
  - Overlap-metadata data lie in sync-cascade path → F2.
  - EventBus emission missing across both paths → F7.
  - Backfill flow dormant-by-design but enum value exposed as if
    active → F6 (design intent vs enum honesty).
- **Not tested at scale:** LOCAL 51,952 chunks; PROD scale
  unknown from this audit.

Not STABLE; not WORKING (dual-path integration + chunker regime
integrity issues); PARTIAL is honest.

**Acceptance criteria (parent §5.1 institutional-knowledge-layer):**
- Criterion 1 (embed coverage): S2101 MET
- Criterion 2 (semantic completeness / chunker provenance): NOT MET
  — F1 shows populations B + C indistinguishable
- Criterion 3 (freshness bounds / staleness detection): NOT MET —
  KD-2 substrate absent
- Criterion 4 (governance ownership): PARTIALLY MET — Path B has
  Documentation Manager Employee OS ownership but Path B is dormant;
  Path A has no assigned owner
- Criterion 5 (behavior integration): NOT MET — no P4 observation
  yet

---

## 14. Known Drift

**Convention.** Findings labeled F1..F8. Each carries inheritance
tag (S1304 / S2101 / S2001 / S2102-new) and disposition
(CONFIRMED / STILL-VALID / F-CANDIDATE / REMEDIATED-ELSEWHERE /
DESIGN-INTENT).

### F1 — Three chunkers, three regimes (S2102-new; extends parent §5.2 framing)

- **Evidence:** three chunker functions exist —
  `build_rag_corpus.chunk_text` (line 49-54), `sync_docs_index_to_documents.chunk_content` (line 408-434),
  `content/embeddings.TextSplitter` (line 395-512). Parent §5.2
  framed the divergence as "two-lane LOCAL vs PROD"; the audit
  refines this: LOCAL vs PROD is one axis (JSONL vs
  DocumentEmbedding), and WITHIN PROD DocumentEmbedding there are
  two more sub-populations from two different chunkers with same
  parameters but different implementations.
- **Regime table:** see §7.3.
- **Divergence root cause:** chunk size (1200 vs 1000) + overlap
  (0 vs 200) + boundary policy (none vs paragraph/sentence)
  explains the 10.66 LOCAL vs 17.85 PROD (populations B + C mean)
  chunks/doc divergence.
- **Consequence:** no schema field records `chunker_id`; downstream
  cannot filter by chunker; cross-chunker retrieval mixes regimes
  silently.
- **Likely-cause tag** (Q5 SIGN boundary — hypothesis):
  `sync_docs_index_to_documents.chunk_content` predates
  `content/embeddings.TextSplitter`; the two were never
  reconciled; step 3's `--embed` inline path never migrated to the
  centralized chunker.
- **Severity (Q8 SIGN STRENGTHEN 2026-07-04):** **MEDIUM-now /
  HIGH-blocker-for-P3.** No chunker_id consumer exists today so
  chunk-level heterogeneity is invisible to ranking; but the
  moment D2100.9 hybrid metadata contract starts enforcing
  cross-chunker filtering at P3, F1 becomes HIGH gating criticality.
  Severity-vs-roadmap split honors both current-state truth and
  P3-blocker warning.
- **Disposition:** P3 D2100.9 hybrid metadata contract MUST cover
  `chunker_id` + `chunker_version` fields at core-required tier for
  DocumentEmbedding rows.

### F2 — Overlap-metadata data lie in sync-cascade path (S2102-new)

- **Evidence:** `sync_docs_index_to_documents.chunk_content()` at
  line 432: `start = end - overlap` — adjacent chunks share ~200
  chars of text. Caller `generate_embeddings()` at lines 385-395
  creates `DocumentEmbedding` WITHOUT `overlap_size` kwarg →
  defaults to 0. All 24,980 `sync_docs` chunks report
  `overlap_size=0` in LOCAL DB despite actually overlapping.
- **ORM verification:** overlap_size=0 chunks = 26,072
  (24,980 sync_docs + 1,092 first-chunks from async path);
  overlap_size=200 chunks = 25,880 (all middle/tail chunks from
  async path). Sync path uniform 0. Async path correct 0 for
  first chunk, 200 for rest.
- **Consequence:** downstream retrieval computing "coverage" from
  `overlap_size` over-counts sync-cascade population by ~20%;
  ranking that penalizes duplicate-hits has hidden false-negative
  for sync_docs slice; migration tools cannot reconstruct chunk
  boundaries from persisted metadata.
- **Likely-cause tag:** `sync_docs_index_to_documents.generate_embeddings()`
  was written without awareness of the `overlap_size` schema
  field; the create call passes only the fields it consciously
  populates.
- **Severity (Q9 SIGN STRENGTHEN 2026-07-04):** **MEDIUM+ / HIGH**.
  This is a **data integrity defect** (recorded metadata contradicts
  semantic truth). Plain MEDIUM under-sells it; elevate to MEDIUM+
  for current absence of downstream consumer harm, HIGH for any
  future logic that trusts `overlap_size`. This is the sync-cascade
  chunk population's persistence contract failure — not merely
  metadata absence.
- **Backfill decision (Q9 SIGN STRENGTHEN 2026-07-04) — explicit
  branches:**
  - (a) **Forward-fix only** — 1-line change at `sync_docs_index_to_documents.py:~394`
    passes `overlap_size=200` on future create calls; historical
    24,980 sync_docs rows carry the lie forever.
  - (b) **Forward-fix + retrofill historical rows** — same
    forward-fix + one-time management command backfills historical
    `overlap_size=200` for all `ingested_via='sync_docs'` rows.
    Requires migration intent + rollback plan since it touches
    shared state.
- **Chris D-verdict candidate at close card** — because
  retrofill touches shared state and requires intent + rollback
  planning, this MUST be surfaced as a Chris-ratified D-verdict at
  close card, not silently deferred to P3.
- **Disposition:** F-CANDIDATE + Chris D-verdict at S2102 close.
  R2.7 (see §19) captures the forward-fix; retrofill decision goes
  to close-card D-verdict.

### F3 — Dual cascade paths coexist without integration (S2102-new; ARCHITECTURAL DEBT)

- **Evidence:** Path A `refresh_docs_corpus` scheduled daily
  4 AM Denver (`core/celery.py:495-499`); Path B
  `rigby_documentation_manager_daily` → `docs_cascade.py`
  MissionRunner NOT SCHEDULED (`core/celery.py:857, 913` register
  the module but no beat entry). Path B has richer safety
  scaffolding (hard timeout on step 4, drift observation, OpsRun
  audit, escalation Deliverable, Employee OS ownership); Path A
  is the one that fires.
- **Historical trail:** S1252/S1253 hotfix built Path B (Documentation
  Manager Employee OS lift) but never wired the beat entry OR
  retired Path A. Both paths persist.
- **Consequence:** production runs get Path A's fewer safety
  rails; Path B's escalation Deliverable path never fires
  automatically; Employee OS observation surface unused for docs
  cascade.
- **Severity:** HIGH. This is the biggest ownership + audit-trail
  gap surfaced by P2 and is a first-order input to P3 governance
  design.
- **Disposition (Q10 SIGN STRENGTHEN 2026-07-04) — recommended
  lean:** F-CANDIDATE + P3 R3.5 discharge. Four options:
  - (a) **Wire Path B beat + deprecate Path A** — most consistent
    with S1252/S1253 intent (staged migration).
  - (b) **Fold Path A gate into Path B preflight** — merges the
    hash-delta efficiency into MissionRunner shell; retires Path A
    at cutover.
  - (c) Retire Path B — **UNLIKELY / contradicts S1252/S1253 intent
    unless evidence says Path B is dead**. Not recommended.
  - (d) Explicit dual-path design with defined activation criteria
    for each path.
  - **Recommended lean:** prefer (b) fold A into B OR (a) wire B +
    deprecate A. Both preserve richer safety scaffolding. Final
    ratification is Chris's; but (c) is off the table absent
    contrary evidence.

### F4 — `build_rag_corpus` silent-drop callback is optional and never wired (S2102-new; extends S2101 D1b)

- **Evidence:** `iter_corpus_rows()` at `build_rag_corpus.py:57-86`
  accepts `on_warning=None` (default). `refresh_docs_corpus.py:5901`
  calls `call_command('build_rag_corpus', stdout=out, stderr=out)`
  — no `on_warning` callback. All silent-drops at STEP 2 (missing
  source, unreadable source, empty source per lines 71-83) produce
  zero telemetry signal to the daily cascade.
- **Consequence:** S2101 D1b's "silent-drop telemetry gap"
  generalization pattern applies to STEP 2 not just STEP 1. Even
  the S1802 6-unembedded-docs incident pattern (docs synced but
  never embedded because cascade PR forgot step 4) has a STEP 2
  cousin: docs indexed but never entered corpus.jsonl because
  STEP 2 silently dropped them.
- **Likely-cause tag:** `iter_corpus_rows` was designed with the
  callback for testability; production caller never wired it
  because `call_command` output-capture already collects the
  warning-tinted stdout writes at line 161 — but `refresh_docs_corpus`
  captures BOTH stdout and stderr into a StringIO and only
  writes to task log summary, so the WARN lines get buried unless
  explicitly grepped.
- **Severity (Q11 SIGN STRENGTHEN 2026-07-04):** **MEDIUM**.
  Risk-class = silent-drop observability defect; **no known
  incidents yet** in LOCAL observation.
  - *Why not HIGH:* no evidence of step-2 drop in observed daily
    runs; index count and corpus row count remain aligned in
    S2101 + S2102 verifier-loop.
  - *Promote-to-HIGH trigger:* any observed mismatch between
    `docs/_index.json` document count and `.rag/corpus.jsonl`
    unique-file count OR any on_warning-worthy condition
    (missing / unreadable / empty source) observed in a daily run
    with the callback wired.
- **Disposition:** F-CANDIDATE. R2.6 (see §19) proposes wire
  `on_warning=logger.warning` at `refresh_docs_corpus.py:5901` OR
  reroute the WARN lines to a structured `[DOCS_CORPUS_REFRESH_STEP2_SKIP]`
  log line at the callback callsite.

### F5-partial — `source_type='api'` monoculture — derivation function ACQUITTED, upstream write-site trace UNRESOLVED (S2101 F1 PARTIAL REFINEMENT; Q12 SIGN STRENGTHEN 2026-07-04)

- **Evidence:** `_derive_source_type()` at `content/embeddings.py:45-63`
  defaults to `'unknown'`. Precedence tree:
  1. `document.extracted_metadata.get('auto_research')` → `'web'`
  2. `document.extracted_metadata.get('spider_name')` OR
     `document.source == 'scraped'` → `'spider'`
  3. `document.document_type == 'youtube'` → `'web'`
  4. `document.source in ('api', 'imported')` → `'api'`
  5. `document.source in ('upload', 'user_upload')` → `'user_upload'`
  6. `document.document_type == 'markdown'` OR `document.source in ('', 'internal', 'system')` → `'internal'`
  7. Default → `'unknown'`
- **LOCAL DB slice:** 100% `source_type='api'` (51,952 chunks).
  This means 100% of Documents that produced chunks have
  `Document.source == 'api'` or `'imported'` at chunk time —
  branch 4 always fires before branches 5-7 have a chance.
- **Where does `Document.source='api'` come from?** Verifier-loop
  did NOT trace this — the write-site sweep in START-NEXT §51
  step 5 point 5 covers `_derive_source_type` at `content/embeddings.py:45-63`
  (this function) but does NOT trace the upstream. Grep target
  for follow-up: `Document(source='api'`, `Document.objects.create(source='api'`,
  `Document.source = 'api'`. Suspected primary write-site:
  `sync_docs_index_to_documents.py:334` (create call) — needs
  inspection.
- **S2101 F1 update — PARTIAL DISCHARGE (Q12 SIGN STRENGTHEN
  2026-07-04):** the derivation function `_derive_source_type` is
  ACQUITTED — it works correctly given input. The upstream
  Document.source write-sites that cause the `api` monoculture
  are NOT traced in this audit and remain UNRESOLVED (see U1).
  The audit does NOT claim to have fully resolved S2101 F1;
  it partially discharges by acquitting the derivation surface
  and pointing the remaining trace-work at U1.
- **S1304 D3 partial corroboration:** S1304's finding "the
  consumer exists AND the write-site populates the field" is
  CONFIRMED for the DE-write side — the DE-populated value is
  honestly derived from `Document.source`. What S1304 did not
  address and what S2101 partially reframed: WHERE `Document.source`
  gets its uniform `api` value. That upstream trace is U1's
  remaining work.
- **Severity:** MEDIUM (unchanged from S2101 F1).
- **Disposition:** **F-PARTIAL** + P3 governance input. R2.4 in
  S2101 remains not-fully-discharged; F5-partial acquits the
  derivation function only. R2.4-full-discharge decides whether
  to (a) diversify at Document create-time by ingest path; (b)
  diversify at `_derive_source_type` input by consulting
  additional signal; or (c) deprecate the field. P2 recommends
  option (a) as the cleanest fix and a candidate for D2100.9
  hybrid contract enforcement, but this recommendation is
  contingent on the U1 trace confirming create-time is the
  right injection point.

### F6 — Backfill dormancy is design intent, not drift (S2101 D5 RECLASSIFIED)

- **Evidence:** `embed_agent_activity()` Celery task at
  `core/tasks.py:2803` wrapping `core/tasks_agents.py:_impl_embed_agent_activity` (line 4092).
  Three write-sites at lines 4223 (dreams), 4290 (hive minds), 4351 (knowledge sources).
  **NO beat schedule entry** for `embed_agent_activity` or
  `embed-agent-activity` in `core/celery.py:37-800`.
- **LOCAL DB slice:** 0 chunks with `ingested_via='backfill'`
  (confirmed via ORM at 2026-07-04 20:22).
- **S2101 D5 said:** LOCAL 0 `backfill` chunks "the `backfill` write-
  site never fires locally (backfill flow does not run in dev
  environment)." This audit refines: the task never fires
  ANYWHERE unless manually triggered — LOCAL vs PROD environment
  is not the discriminator; scheduling absence is.
- **Consequence:** `ingested_via='backfill'` is aspirational
  infrastructure; the enum value is exposed but never populated
  automatically. Not a bug; not drift; a **deliberate non-
  activation**.
- **Severity (Q13 SIGN STRENGTHEN 2026-07-04):** **LOW severity,
  category = incomplete wiring** (NOT drift AND NOT design intent).
  Downgrade to LOW because no observable harm; category reclassify
  because "design intent" over-claims charity — the task exists,
  has three materialized write-sites, and is never scheduled. That
  is incomplete infrastructure / dormant feature, which IS a risk
  class (S2001 F9 pattern).
- **Governance note (Q13 SIGN STRENGTHEN 2026-07-04):** P3 governance
  must decide explicitly — either (a) de-scope: document that
  `embed_agent_activity` is manual-only and remove the enum value's
  aspirational status; OR (b) add scheduling and make it real with
  observation targets. Do NOT imply intent unless there IS an
  explicit product decision.
- **Over-claim admission (Q20 SIGN STRENGTHEN 2026-07-04):** the
  initial F6 draft called this "design intent" — that was too
  charitable. May actually be incomplete infrastructure absent an
  explicit decision from Chris. This is called out honestly to
  prevent the reclassification itself from becoming a new form of
  drift.
- **Disposition:** F-CANDIDATE + P3 governance decision. R3.6 in
  §19 proposes P3 documents the activation criteria explicitly
  OR retires the enum + evaluates whether the three internal-content
  categories (dreams, hive minds, knowledge sources) SHOULD activate
  now that Group 2100 arc has visibility into the substrate.

### F7 — Neither cascade path emits EventBus events (S2102-new; cross-refs S2001 F3)

- **Evidence:** grep for `event_bus.publish` in `refresh_docs_corpus`
  body (lines 5802-5946), `docs_cascade.py` (all 766 lines), and
  the four cascade commands returns zero hits. Path B uses
  OpsRunEvent (ORM rows on OpsRun) as its timeline substrate; Path A
  uses structured `[DOCS_CORPUS_REFRESH*]` logger lines.
- **Cross-reference:** S2001 F3 (SPIDER_DATA MISSING-producer /
  WEAK consumer). The docs-cascade EventBus pattern is architecturally
  identical: MISSING producer + WEAK consumer (Path B ORM queries
  or Path A log grep).
- **Consequence:** external observers (dashboards, drift
  detectors, health monitors, Rigby SIGN preambles per D2100.10)
  cannot subscribe to cascade lifecycle. Even the Corpus Health
  Score §5.5 dimensions Chris ratified would need to poll or
  reconstruct from OpsRunEvent + logger lines.
- **Severity (Q14 SIGN STRENGTHEN 2026-07-04):** **MEDIUM current
  harm / HIGH criticality as enabling substrate**. F7 is a
  multiplier: it blocks observability + enables downstream
  subscriptions and is one of the few findings that improves
  everything else. The missing substrate is what would carry F4
  telemetry signals + F8 aggregate embed completion signals cleanly.
  Sever as MEDIUM for current user-visible harm (nothing is broken
  today); mark criticality as HIGH-as-enabler for the compounding
  benefit of emission at P3.
- **Disposition:** F-CANDIDATE. P3 governance decision on whether
  to emit EventBus + which events (see §10.4 two-layer candidate
  list post-Q6 fold).

### F8 — Step 4 hard timeout enforced only on dormant path (S2102-new; DERIVATIVE / CONTINGENT on F3 resolution)

- **Evidence:** `docs_cascade.step_4_embed()` at line 370-377
  uses `subprocess.run([..., 'sync_docs_index_to_documents',
  '--embed'], timeout=1800s)` with soft warning event at 600s.
  `refresh_docs_corpus` calls per-doc `.delay('generate_document_embeddings')`
  fan-out — each task has its own soft_time_limit but the parent
  task has soft=600s/hard=720s covering only steps 1-3 (docstring
  line 5834 confirms).
- **Consequence:** if per-doc embedding hangs on Path A (OpenAI
  dropped conn, network stall on 2900+ document fan-out), each
  task times out independently but the parent's `[DOCS_CORPUS_REFRESH]`
  summary line reports `embedding_tasks_dispatched=%d` — the
  count of dispatches, NOT the count of completed embeddings.
  Success telemetry is misleading if dispatch and completion
  diverge.
- **Severity:** MEDIUM.
- **Dependency note (Q15 SIGN STRENGTHEN 2026-07-04):** F8 is
  partially subsumed by F3 but not fully. Explicit dependency
  on F3 option choice:
  - If F3 discharges option (b) fold A into B — F8 auto-resolves
    because B's subprocess caps + aggregate embed caps propagate to
    the merged path.
  - If F3 discharges option (a) wire B + deprecate A — F8 auto-
    resolves at cutover when Path A retires.
  - If F3 discharges option (d) explicit dual-path — F8 PERSISTS
    unless Path A gets its own aggregate-cap design.
  - If F3 discharges option (c) retire B — F8 becomes primary
    finding (safety-rail defect on the surviving path).
  F8 remains as a separate finding for now to preserve the
  observation, marked derivative / contingent.
- **Disposition:** F-CANDIDATE. R2.8 in §19 proposes a follow-up
  Celery telemetry surface: aggregate `generate_document_embeddings`
  completion rate per `refresh_docs_corpus` run via a group
  callback or bounded polling — CONTINGENT on F3 resolution
  keeping Path A alive.

### S1304 re-attestations (partial, per Q10 SIGN STRENGTHEN convention)

| S1304 finding | S2101 status | S2102 status | Boundary |
|---------------|--------------|--------------|----------|
| S1304 D2 (`@lru_cache(1)` staleness) | STILL-VALID | RE-ATTESTED STILL-VALID at HEAD `7c84ff65` — provenance-index cache invalidation still not implemented | belongs to P3 governance (owner + mechanism) |
| S1304 D3 (source_type consumer alive) | S2101 refinement F1 | CORROBORATED + REFINED at F5 upstream | Owner: P3 governance |
| S1304 T1 (provenance rebuild cadence unmanaged) | STILL-VALID | RE-ATTESTED — 0 periodic tasks `provenance`; `build_docs_provenance` DESIGN-INTENT manual per S1145 Plan B | Owner: P3 governance decision — schedule or not? Chris directive `feedback_docs_cascade_at_every_close` implies YES |
| S1304 T4 (docs-ingestion-cascade topic doc) | STILL-VALID | STILL-VALID + deferred | Owner: R3.1 discharges by publishing `docs/topics/docs-ingestion-cascade.md` |
| S1304 T5 (`ingested_via` write-only status) | STILL-VALID | F-CANDIDATE-STILL-OPEN — S1399 §19 R1 full-tree recheck deferred to R2.5 discharge | Owner: R2.5 |
| S1304 T6 (filter counters lack operator surface) | DELEGATED TO GROUP 1700 | UNCHANGED delegation | Owner: Group 1700 Observability |
| S1304 T7 (corpus-completeness gap auto-detection) | PARTIALLY REMEDIATED | UNCHANGED — refresh_docs_corpus unembedded-count trigger provides partial detection; `verify_provenance_coverage` mgmt command not built | Owner: P3 governance |
| S1304 T8 (provenance model ownership unassigned) | STILL-VALID | STILL-VALID | Owner: R3.3 discharges |

### S2001 cross-arc reference

- **S2001 F3 SPIDER_DATA MISSING-producer / WEAK consumer** applies
  verbatim to docs cascade (F7).
- **S2001 F9 dormant-consumer risk pattern** applies to Path B
  MissionRunner scheduling absence (F3).

---

## 15. Known Technical Debt

Per playbook §12 debt classifications. Bounded remediation sketches
only per Q5 SIGN belongs-to boundary.

### 15.1 Debt-table roll-up (S2101 T1-T10 re-attested + S2102 additions)

| ID | Debt | Severity | Origin | Remediation sketch |
|----|------|----------|--------|--------------------|
| T1 | Provenance-index rebuild cadence unmanaged | HIGH | S1304 T1 → S2101 T1 STILL-VALID | See F-D6 reclassification below: DESIGN-INTENT per S1145 Plan B vs Chris directive; P3 decision |
| T2 | `@lru_cache(maxsize=1)` staleness at `_load_provenance_docs()` | HIGH | S1304 T2 STILL-VALID | Worker-restart trigger / file-watcher / Redis / TTL |
| T3 | `source_type` monoculture despite live consumer | MEDIUM | S2101-new (F1/D4) → F5 (root-cause traced upstream) | Diversify `Document.source` at ingest OR augment `_derive_source_type` input OR deprecate |
| T4 | Ingestion cascade documentation as topic-doc unpublished | MEDIUM | S1304 T4 STILL-VALID | R3.1: publish `docs/topics/docs-ingestion-cascade.md` |
| T5 | `ingested_via` write-path not wired to retrieval | MEDIUM | S1304 T5 STILL-VALID | R2.5: full-tree read-side sweep discharges S1399 §19 R1 |
| T6 | Filter counters lack operator surface | MEDIUM | Group 1700 delegation | Unchanged |
| T7 | Corpus-completeness gap not auto-detected | MEDIUM | S1304 T7 PARTIALLY REMEDIATED | `verify_provenance_coverage` mgmt command; cache confidence breakdown; UNKNOWN warning |
| T8 | Provenance model ownership unassigned | MEDIUM | S1304 T8 STILL-VALID | R3.3 discharges |
| T9 | Cascade emits no lifecycle events | MEDIUM | S2101-new (D7) → F7 | Design decision at P3 |
| T10 (renamed to **T10' Contract fields + population discipline**, Q16 SIGN STRENGTHEN 2026-07-04 — MERGES T11) | Metadata JSONField schema absent for research-artifact fields AND absent for chunker-provenance fields (`chunker_id` + `chunker_version`); population discipline gap (48.2% empty per S2101 F2 → chunker B; missing chunker_id + chunker_version fields → F1) | MEDIUM | S2101 D3 + S2102 F1 (merged per Q16 fold to prevent T-table bloat) | D2100.9 hybrid contract at P3 — covers both metadata fields absent AND population discipline in a single contract surface |
| **T12** | **Overlap-metadata data lie in sync-cascade path** | MEDIUM | **S2102-new (F2)** | 1-line fix at `sync_docs_index_to_documents.py:394` to pass `overlap_size=200`; retrofill decision at P3 |
| **T13** | **Dual cascade paths (F3) — architectural debt** | HIGH | **S2102-new (F3)** | P3 governance decision + wire beat OR retire Path A OR fold |
| **T14** | **`build_rag_corpus` on_warning never wired** | MEDIUM | **S2102-new (F4)** | Wire callback at `refresh_docs_corpus.py:5901` OR route to structured log |
| **T15** | **Path A no aggregate embedding completion telemetry** | MEDIUM | **S2102-new (F8)** | Celery group callback OR bounded polling on dispatched tasks |
| **T16** | **KD-2 substrate absent — no per-chunk content_hash / chunker_version at chunk time** | HIGH | **S2102-new (extends S2101 KD-2)** | Schema addition; R2.3 discharges design; execution deferred post-arc |
| **T17** | **Backfill enum value exposed but flow dormant** | LOW | **S2102-new (F6)** | R3.6: document activation criteria explicitly OR retire enum value |

### 15.2 Debt-severity re-attestation summary

| Severity | S2101 baseline | S2102 status | Change |
|----------|----------------|--------------|--------|
| HIGH | T1, T2 | T1, T2 STILL-VALID; **T13 NEW (F3 dual cascade)**; **T16 NEW (KD-2 substrate)** | +2 net HIGH additions |
| MEDIUM | T3-T10 | T3-T10 STILL-VALID (T10 renamed to T10' + T11 merged in per Q16 fold); **T12, T14, T15 NEW** | +3 net MEDIUM additions (T11 was merged into T10', not additive) |
| LOW | (none) | **T17 NEW (F6 backfill enum honesty)** | +1 net LOW addition |

### 15.3 Knowledge-debt (KD-1..KD-7) re-observation

Per S2101 §15.3 taxonomy.

| Category | S2101 baseline (LOCAL) | S2102 status (LOCAL) | Substrate readiness |
|----------|------------------------|----------------------|---------------------|
| KD-1 unembedded-on-disk | 0 | 0 | READY (Path A gate detects) |
| KD-2 stale-embed-post-content-change | UNMEASURABLE | **STILL UNMEASURABLE** — T16 confirms substrate absent | NOT READY; R2.3 designs |
| KD-3 cascade-PR-forgot-embed-step | 0 currently | 0 currently — S1802 remediation holds | READY (Path A gate) |
| KD-4 metadata-blank-at-ingest | 24,980 (48.2%) | **24,980 (48.1% of 51,952)** — sync-cascade population unchanged | KD-2 root-cause resolved via F2 + T12 |
| KD-5 provenance-index-stale | INDETERMINATE | STILL INDETERMINATE — no automated freshness check per T1 | NOT READY; P3 mechanism |
| KD-6 orphan-Document-row-post-file-move | 0 | 0 | READY (spot-check) |
| KD-7 mis-linked-embeddings | 0 detected coarse | 0 detected coarse; fine-grained deferred | Coarse READY; fine-grained NOT READY |

### 15.4 Provenance-index rebuild cadence — reclassification proposal

S2101 F4 said `build_docs_provenance` unscheduled is drift. This
audit finds two competing dispositions:

- **S1145 Plan B design intent:** git-driven metadata, manual
  regeneration only — no benefit from scheduling.
- **Chris directive (S1399 close) via `feedback_docs_cascade_at_every_close`:**
  "run `build_docs_provenance` before declaring done" at every arc
  or session close.

The gap: manual-at-arc-close is fragile (humans must remember).
Scheduled would harden but the S1145 argument still holds for
frequency.

Recommended reclassification: **DELIBERATE-DESIGN + FRAGILE-EXECUTION**.
Downgrade from S2101 F4 DRIFT to design gap. P3 decides whether to
add to `refresh_docs_corpus` cascade tail OR keep manual with an
enforcement lint (CI check that verifies `docs/_provenance.json`
mtime is newer than latest handoff commit).

---

## 16. Boundary Violations

Per playbook §12 finding types.

**None observed at the docs-ingestion domain boundary.** The
cascade respects:

- Group 1300 (Memory) boundary — no `AgentMemory` writes.
- Group 2000+ (Event architecture) boundary — no direct EventBus
  emission (F7 is a MISSING integration, not a violation).
- Group 1700 (Observability) boundary — `logger.warning` calls
  respect the delegated telemetry pattern.

Adjacent-but-not-violating patterns:

- Path B MissionRunner uses OpsRunEvent (Employee OS primitive) —
  correct use per EMPLOYEE_OS_PRIMITIVES §4 anti-duplication.
- Path A stays inside `core/tasks.py` module — no cross-module
  circular imports.

---

## 17. Duplicate or Overlapping Systems

Per playbook §12 duplicate_model / overcoupling classifications.
Per **Q17 SIGN STRENGTHEN 2026-07-04**, this section primarily
covers **Path A vs Path B** as the true duplicate (§17.1); chunkers
B vs C live in a shorter subsection (§17.2) framed as "overlapping
chunker regimes with contract divergence" (near-isomorphism, not
duplication).

### 17.1 Duplicate — dual cascade orchestrators (F3, PRIMARY §17 finding)

Path A and Path B run the SAME 4 commands with different scaffolding.
Non-orthogonal duplication:

- Path A: hash-delta gate + per-doc `.delay()` fan-out.
- Path B: MissionRunner + subprocess step 4 + drift observation +
  escalation.

Not two lanes serving different needs — two implementations of the
same cascade with different maturity levels. Path B is the intended
future (S1252/S1253 lift); Path A is the fallback that ended up
being the only production path because Path B was never scheduled.

**Extraction candidate.** Fold Path A's hash-delta gate into Path B's
preflight step; wire Path B beat; retire Path A. Deferred to P3
decision.

### 17.2 Overlapping chunker regimes with contract divergence (F1, SECONDARY §17 finding, Q4 + Q17 SIGN STRENGTHEN 2026-07-04)

Chunker A (`chunk_text` in `build_rag_corpus.py:49-54`) is
legitimately distinct: writes to `.rag/corpus.jsonl`, not
`DocumentEmbedding`. Different consumer path (LOCAL keyword lane).

**Chunkers B and C are NEAR-ISOMORPHIC in chunking regime but
NON-ISOMORPHIC in persistence/metadata contract.** Not duplication —
regime similarity with contract divergence. That distinction is
precisely why F2 matters as a separate finding.

Both B and C:
- Produce `DocumentEmbedding` rows.
- Use 1000-char chunk size.
- Use 200-char overlap semantically.
- Apply paragraph → sentence boundary preservation.

Differences (contract divergence, not implementation divergence):
- Chunker B (`chunk_content` in `sync_docs_index_to_documents.py:408-434`)
  is a self-contained implementation inside the sync command.
- Chunker C (`TextSplitter.split_text` in `content/embeddings.py:395-512`)
  is the centralized library used by the async and per-doc embedding
  paths.
- Chunker B fails to persist `overlap_size` (F2) — chunk boundaries
  overlap in memory but persisted metadata reports 0.
- Chunker B fails to populate `metadata` (S2101 F2) — the 48.2%
  empty-metadata slice.

**Extraction candidate.** Retire Chunker B in favor of Chunker C;
STEP 3 `--embed` inline path should call `TextSplitter` directly.
This would resolve F1's B/C near-isomorphism + F2's overlap-metadata
lie + S2101 F2's 48.2%-empty-metadata slice in a single minimal-diff
PR — but PARENT ANTI-SCOPE §7.1 forbids implementation in this arc;
the extraction candidate ships as R3.7 for P3 handoff.

### 17.3 Overlapping — provenance systems

Per S1304 D3: `docs/_provenance.json` + `Document.extracted_metadata`
+ `DocumentEmbedding.metadata` are complementary, not duplicate.
S2102 re-attests this; no new duplication finding here.

---

## 18. Ownership Gaps

Per playbook §12 unclear_owner findings.

### 18.1 Ownership matrix

| Concern | Employee OS owner | Codebase owner | Ownership state |
|---------|-------------------|-----------------|-----------------|
| Path A `refresh_docs_corpus` | NONE ASSIGNED | `core/tasks.py:5802-5946` | **UNASSIGNED** — no Employee OS mission binding |
| Path B `rigby_documentation_manager_daily` | Documentation Manager (Rigby) | `core/tasks_documentation_manager.py` + `core/jobs/docs_cascade.py` | ASSIGNED but DORMANT — no beat |
| `build_docs_index` command | (via caller) | `core/management/commands/build_docs_index.py` | Delegated to caller |
| `build_rag_corpus` command | (via caller) | `core/management/commands/build_rag_corpus.py` | Delegated to caller |
| `sync_docs_index_to_documents` command | (via caller) | `core/management/commands/sync_docs_index_to_documents.py` | Delegated to caller |
| `embed_documents` command | (via caller) | `core/management/commands/embed_documents.py` | Delegated to caller |
| Chunker A regime | UNASSIGNED | `build_rag_corpus.py` | UNASSIGNED |
| Chunker B regime | UNASSIGNED | `sync_docs_index_to_documents.py` | UNASSIGNED |
| Chunker C regime | UNASSIGNED | `content/embeddings.py` | UNASSIGNED |
| `_derive_source_type` derivation | UNASSIGNED | `content/embeddings.py:45-63` | UNASSIGNED |
| `Document.source` field values | UNASSIGNED | (write-sites TBD per R2.4) | UNASSIGNED |
| `docs/_provenance.json` writes | UNASSIGNED | `build_docs_provenance` command | UNASSIGNED (S1304 T8 STILL-VALID) |
| DocumentEmbedding schema | UNASSIGNED | `content/models.py` | UNASSIGNED |
| Retrieval semantics (7-tier metadata contract) | UNASSIGNED — P3 decides | (aspirational) | To be assigned at P3 |

### 18.2 Ownership gap synthesis

The docs-cascade write-side has **NO Employee OS ownership binding
that fires today**. Path B (Documentation Manager) is the intended
owner but is unscheduled. Path A runs without an owner. This is the
first-order gap P3 governance must resolve (see R3.3 + R3.5).

Chunker ownership is fully unassigned across all three regimes. F1's
regime map has no responsible party for reconciling B vs C.
`_derive_source_type` has no owner despite being the discriminative
axis for retrieval provenance.

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows.

### 19.1 P2 → P3 (S2103 — Retrieval Authority Framework + Governance)

**P3 triage list (Q18 SIGN STRENGTHEN 2026-07-04).** 8 handoffs is
a lot for one P3 session. Explicit triage split so P3 knows what
MUST ship vs what is BACKLOG:

- **P3.1 must-ship — R3.5 dual-cascade resolution** (F3 discharge).
  Sets the canonical path and therefore CONSTRAINS every other P3
  handoff (contract fields, observability, backfill semantics).
- **P3.2 must-ship — R3.2 D2100.9 hybrid contract chunker fields.**
  Depends on P3.1's canonical-path decision (which chunker regime
  wins).
- **P3.3 must-ship — R3.3 owner assignments.** Blocks all execution.
- **P3.x backlog** (Chris may split into P3a/P3b or defer to post-arc):
  R3.1, R3.4, R3.6, R3.7, R3.8.

Alternative structure: 2-child split (P3a/P3b) covering must-ships +
backlog respectively; parent-plan does not require this and single-
child P3 with triage-triage is the recommended default.

**Individual handoffs:**

- **R3.1 — Publish `docs/topics/docs-ingestion-cascade.md`** (S1304 T4, S2101 T4, S2102 T4 STILL-VALID). Cover: 4-step flow, three chunker regimes, dual orchestrator paths, cadence, failure modes.
- **R3.2 — D2100.9 hybrid metadata contract** MUST cover `chunker_id`, `chunker_version`, `overlap_size_actual` (fix F2 by contract), upstream `Document.source` provenance carry-forward.
- **R3.3 — Owner assignments** for the §18.1 UNASSIGNED axes:
  Path A cascade, chunker regimes, `_derive_source_type`,
  `Document.source` write-sites, DocumentEmbedding schema,
  `docs/_provenance.json` writes. Discharges S1304 T8 STILL-VALID.
- **R3.4 — Cascade governance canonical doc.** Replace informal
  MEMORY.md rules (`feedback_docs_pipeline_4_step_cascade`,
  `feedback_docs_cascade_at_every_close`,
  `feedback_cascade_pr_must_include_embed_step`) with a canonical
  governance doc under `docs/00-START-HERE/` per parent §5.3.
- **R3.5 — Cascade dual-path resolution** (F3 discharges). Decide:
  (a) wire Path B beat + retire Path A; (b) fold Path A gate into
  Path B preflight; (c) retire Path B; (d) explicit dual-path with
  activation criteria.
- **R3.6 — Backfill activation criteria** (F6 discharges). Document
  activation criteria for `embed_agent_activity` OR retire enum
  value. Cross-reference S1304 D5 knowledge-source substrate
  observation.
- **R3.7 — Chunker consolidation candidate** (F1 discharges).
  Design decision: retire Chunker B, migrate STEP 3 `--embed`
  inline path to `TextSplitter`. Ships as design-preparation
  recommendation only; implementation deferred to post-arc.
- **R3.8 — Provenance-index scheduling decision** (T1 STILL-VALID +
  §15.4 reclassification). Choose scheduling mechanism vs CI-lint
  enforcement.

### 19.2 P2 → P4 (S2104 — Behavior Substrate Structured Observation)

**Handoff structure (Q19 SIGN STRENGTHEN 2026-07-04).** Five R4.x
items fit a single P4 session tagged as follows:
- **Measurement bundle:** R4.1, R4.2, R4.3 — observational KPIs
- **Governance test:** R4.4 — discharge D2100.7 conditional-elevation
- **Conditional:** R4.5 — activation observation, gated by P3
  decision on Path B beat

**Explicit branch for R4.5 (Q19 SIGN STRENGTHEN 2026-07-04):**
```
   Does P3 wire Path B beat OR fold A into B?
     ├── YES → P4 runs R4.5 (Path A/B activation observation)
     │        Observation targets: N≥10 daily runs;
     │        escalation Deliverable dedupe accuracy;
     │        step_5 drift observation reliability.
     └── NO (Path B remains dormant OR retired) → R4.5 SKIPPED
              or deferred to post-P4 execution item.
```

- **R4.1 — Chunker-population correlation observation.** Test
  whether recent SIGN cycles that failed retrieval-quality checks
  correlate with hitting Chunker B (sync-cascade) or Chunker C
  (async) populations. If N ≥ 10 observed cases show B-vs-C
  imbalance, F2 elevates from MEDIUM to HIGH.
- **R4.2 — Institutional-knowledge-layer acceptance criteria
  observation** (per parent §5.1 criteria 2-5). Criterion 2
  becomes measurable once F1 chunker regimes are documented in
  §14 (this audit).
- **R4.3 — Corpus Health Score dimension additions.** Add
  dimensions for F1 chunker-provenance ambiguity, F2 overlap-
  metadata integrity, F4 cascade telemetry emission rate, F7
  EventBus emission rate. Feeds §5.5 dimension list per D2100.10.
- **R4.4 — D2100.7 conditional-elevation logic for freshness bounds.**
  P4 explicitly discharges the D2100.7 rule per Q15 SIGN
  STRENGTHEN 2026-07-04 at S2101 close.
- **R4.5 — Path A vs Path B activation-observation.** If P3 wires
  Path B beat, P4 observes N ≥ 10 daily runs for escalation
  Deliverable dedupe accuracy + step_5 drift observation reliability.

### 19.3 P2-scoped fold-back to STEP 3 write-sites (R2.x — S2101 predecessor handoffs discharged)

- **R2.1 — Mechanism-level cascade documentation.** DISCHARGED
  IN-DOC (this audit §3 + §7). Formal topic doc = R3.1.
- **R2.2 — Two-lane chunking-strategy audit.** DISCHARGED IN-DOC
  (§7.3 regime map + F1 refinement).
- **R2.3 — `content_hash` propagation to chunk-time.** DESIGN-
  PREPARATION deferred to P3 per parent §5.2 mechanism-vs-
  governance boundary (Q15 SIGN STRENGTHEN 2026-07-04).
- **R2.4 — `source_type` monoculture root-cause.** DISCHARGED
  IN-DOC (F5) with upstream tracing; execution to P3 owner
  assignment per R3.3.
- **R2.5 — Discharge S1399 §19 R1 for `ingested_via`.** DEFERRED to
  P3 R3.1 topic-doc drafting time (full-tree read-side sweep).
- **R2.6 — Cascade EventBus emission design.** DISCHARGED IN-DOC
  §10.4 candidate list + F7; formal design at P3.
- **R2.7 (NEW) — Overlap-metadata fix at sync-cascade path.** F2
  discharge candidate: pass `overlap_size=200` at
  `sync_docs_index_to_documents.py:394`. 1-line fix; NOT shipped
  this arc (parent §7.1 anti-scope) but named for
  post-arc execution.
- **R2.8 (NEW) — Path A aggregate embed telemetry.** F8 discharge
  candidate: Celery group callback OR bounded polling. Post-arc
  execution.

### 19.4 P2 flags for future non-Group-2100 arcs

- **Group 1700 Observability delegation:** S1304 T6 filter-counter
  operator-surface remediation UNCHANGED.
- **Documentation / Research Knowledge System (§3.15 future arc):**
  R3.4 cascade governance doc — same argument as S2101 §19.4;
  cross-arc concern.
- **Group 2000+ EventBus arc (closed at S2099):** F7's cascade
  EventBus emission is a candidate for Group 2000+ retroactive
  fold-in if any Group 2000+ close-out lands another round of
  event-contract additions.

### 19.5 P2-scoped follow-ups (must land pre-close if adopted)

None mandatory. All above route to P3/P4 handoffs. P2 status flips
`draft` → `active` on Chris ratification post-Rigby SIGN cycle 1.

---

## 20. Appendix

### 20.1 Verifier-loop evidence log

Executed 2026-07-04 at HEAD `7c84ff65`. All queries LOCAL DB unless
otherwise noted.

**ORM chunk distribution (single-transaction sample):**
- `DocumentEmbedding.objects.count()` = 51,952 (S2101 baseline 51,789 → +163 = 1 daily beat fire since close)
- `Document.objects.filter(embeddings__isnull=False).count()` = 2,911
- Chunks/doc: mean=17.85, median=11, p50=11, p90=33, p95=47, p99=169, max=443 (matches S2101 §14 shape)
- chunk_size: mean=826.4, median=889, min=0, max=30152, stdev=263.7
- chunk_size percentiles: p10=552, p50=889, p90=993, p95=1000, p99=1125
- chunk_size buckets:
  - <500: 4,132 (8.0%) — mostly last-chunk short tails
  - 500-800: 12,021 (23.1%) — tail chunks
  - 800-1000: 32,867 (63.3%) — bulk (both B + C)
  - =1000: 882 (1.7%)
  - 1000-1200: 1,854 (3.6%)
  - =1200: 1 (0.0%)
  - 1200-2000: 158 (0.3%)
  - >=2000: 37 (0.1%)
- chunk_size by ingested_via:
  - `unknown` (n=26,972, async/sync path via TextSplitter): mean=804.6
  - `sync_docs` (n=24,980, sync-cascade path via chunk_content): mean=849.9
  - `backfill` (n=0): none
- overlap_size distribution:
  - 0: 26,072 (50.2%) — 24,980 sync_docs + 1,092 first-chunks async
  - 200: 25,880 (49.8%) — all middle/tail chunks async

**Cascade source samples:**
- `build_docs_index.py:195-196`: unconditional `_` prefix skip (S2101 F3 confirmed)
- `build_rag_corpus.py:49-54`: chunk_text pure fixed 1200-char
- `build_rag_corpus.py:57-86, 71-83`: iter_corpus_rows + silent-drop callback OPTIONAL (F4)
- `sync_docs_index_to_documents.py:394`: ingested_via='sync_docs' create call
- `sync_docs_index_to_documents.py:408-434`: chunk_content 1000/200 with paragraph/sentence (F1 Chunker B)
- `content/embeddings.py:45-63`: _derive_source_type precedence tree, default 'unknown'
- `content/embeddings.py:395-512`: TextSplitter (F1 Chunker C)
- `content/embeddings.py:600-696`: process_document_for_rag async path; populates metadata
- `content/embeddings.py:642-656`: DocumentEmbedding.create() write kwargs (async path)
- `content/embeddings.py:653-656`: metadata + overlap_size + source_type + ingested_via kwargs present
- `content/embeddings.py:702-792`: process_document_for_rag_sync mirrors async
- `core/tasks_agents.py:4092, 4177-4223, 4237-4290, 4304-4351`: embed_agent_activity three write-sites (F6 dormant)
- `core/tasks.py:5802-5946`: refresh_docs_corpus body
- `core/tasks.py:5877-5892`: two-trigger gate logic
- `core/tasks.py:5900-5902`: cascade steps 1-3 call_command
- `core/tasks.py:5931-5933`: per-doc fan-out
- `core/tasks.py:5939-5945`: [DOCS_CORPUS_REFRESH] log line
- `core/celery.py:495-499`: refresh-docs-corpus-daily beat entry
- `core/celery.py:364-369`: backfill-spider-embeddings beat entry
- `core/jobs/docs_cascade.py:352-355, 358-361, 364-367, 370-377`: MissionRunner step wiring
- `core/jobs/docs_cascade.py:312-317`: subprocess timeout enforcement
- `core/jobs/docs_cascade.py:212-246`: step_4 warning timer
- `core/jobs/docs_cascade.py:383-465`: verify_doc_claims drift observation
- `core/jobs/docs_cascade.py:607-679`: postflight step_5 emission
- `core/jobs/docs_cascade.py:699-751`: build_docs_manager_runner factory
- `core/tasks_documentation_manager.py:104-131`: rigby_documentation_manager_daily task (dormant per F3)

**Grep sweeps executed:**
- `event_bus.publish` in refresh_docs_corpus / docs_cascade.py / 4 cascade commands = 0 hits (F7 confirmed)
- `chunker_id` field in DocumentEmbedding = 0 hits (T11 confirmed)
- `chunking_version` field anywhere = 0 hits (S2101 KD-2 substrate confirmed absent)
- `PeriodicTask` for `provenance` = 0 hits (S2101 F4 confirmed; §15.4 reclassification)
- Beat entry for `embed_agent_activity` = 0 hits (F6 confirmed)
- Beat entry for `rigby_documentation_manager_daily` = 0 hits (F3 confirmed)

### 20.2 Files inspected

| File | Purpose in this audit |
|------|-----------------------|
| `core/management/commands/build_docs_index.py` (1,112 lines) | STEP 1 mechanism + F3-corroboration |
| `core/management/commands/build_rag_corpus.py` (178 lines) | STEP 2 mechanism + F1 Chunker A + F4 |
| `core/management/commands/sync_docs_index_to_documents.py` (434 lines) | STEP 3 mechanism + F1 Chunker B + F2 + S2101 F2 root-cause |
| `core/management/commands/embed_documents.py` (70 lines) | STEP 4a entry |
| `content/embeddings.py` (1,106 lines) | STEP 4b entry + F1 Chunker C + F5 + T10-relevant models |
| `core/tasks_agents.py:4092-4400` (excerpt) | F6 backfill write-sites |
| `core/tasks.py:5802-5946` (excerpt) | Path A orchestrator + F7 + F8 |
| `core/tasks.py:1440-1467` (excerpt) | Cross-check backfill_spider_embeddings depth-gate pattern |
| `core/tasks_documentation_manager.py:104-131` (excerpt) | Path B task entry |
| `core/jobs/docs_cascade.py` (766 lines) | Path B MissionRunner + F3 + F8 timeout enforcement |
| `core/celery.py:37-800` (grep) | Beat schedule inventory (§15 T-table + F3/F6 dormancy) |
| `content/models.py:116-123, 737-810` (excerpt) | EmbeddingModel enum + DocumentEmbedding schema fields (T10/T11/T12) |

### 20.3 Docs inspected

| Doc | Section | Purpose |
|-----|---------|---------|
| `docs/research/domains/rag_document_loading/2100_...` | §5.2, §7, §8 | Parent scope + anti-scope + ratified D-verdicts |
| `docs/research/domains/rag_document_loading/2101_...` | §14, §15, §19.1, §20 | S2101 baseline + P2 handoff list + verifier evidence |
| `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` | §11.2, §15 | Child-audit template + Rigby SIGN process |
| `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` | §0-§5, §8.1 | Bootstrap + RESEARCH class contract |
| `docs/research/OPEN_ARCS.md` | Group 2100 In-progress row | Cross-arc state |
| `00-START-NEXT-SESSION.md` | §1-§101 | Session priorities + verifier-loop checklist |
| CLAUDE.md | Detailed Breakdown + Frontend row | Live counts + subsystem pointer |
| MEMORY.md workflow rules | feedback_docs_pipeline_4_step_cascade + companions | Cascade discipline rules → R3.4 candidate |

### 20.4 Unresolved unknowns

Per playbook §12 UNKNOWN honesty convention.

- **U1 — `Document.source='api'` write-sites full trace.** F5 identified
  the derivation function returns `'api'` via branch 4 when
  `Document.source in ('api', 'imported')`. The upstream write-sites
  populating `Document.source` were NOT fully traced in this audit.
  Grep target: `Document.objects.create(source=...)`, `Document(source=...)`,
  direct field assignments. R2.4-followup / R3.1 topic doc drafting
  discharges.
- **U2 — Path A per-doc embed completion rate.** F8 named the
  telemetry gap. Actual completion rate for LOCAL fan-out today is
  unknown from this audit. R2.8-followup discharges via bounded
  measurement.
- **U3 — Chunker B → Chunker C migration feasibility.** F1 §17.1
  proposed retiring Chunker B. Migration effort + retrofill impact
  on existing 24,980 sync_docs rows is unknown. Design-preparation
  work for R3.7.
- **U4 — Path B step_4 warning threshold appropriateness.** 600s soft
  warning + 1800s hard timeout are `docs_cascade.py` constants.
  Whether these are calibrated to observed embedding times is unknown
  without live PROD observation (parent §7.3 anti-scope).
- **U5 — refresh_docs_corpus SIGSEGV / OSError branch.** LOCAL only
  probed happy path. `docs/_index.json` missing branch (line 87-89)
  never observed in verifier-loop.
- **U6 (Q20 SIGN STRENGTHEN 2026-07-04) — LOCAL ↔ PROD comparability
  meta-unknown.** The audit runs entirely against LOCAL Postgres.
  Findings that depend on beat schedules, observed warning
  thresholds, or real execution rates require PROD validation:
  - F1 chunker regime counts (B=24,980 / C=26,972) — LOCAL only;
    PROD split may differ if refresh_docs_corpus behaves differently
    at PROD scale.
  - F2 overlap-metadata data lie (24,980 rows) — LOCAL; PROD retrofill
    scope depends on PROD historical row count.
  - F3 dual-cascade dormancy — both paths' LOCAL activation status
    is known; PROD beat schedule verified only through code (not
    live PROD probe).
  - F4 silent-drop observability — no known incidents LOCAL; PROD
    may have observed step-2 drops that never surfaced.
  - F5-partial upstream Document.source trace — LOCAL 100% `api`;
    PROD may have observed diversity.
  - F6 backfill dormancy — verified NOT scheduled in code; PROD
    beat could have local overrides (unlikely per S1252/S1253
    pattern but not verified).
  - F7 EventBus emission — LOCAL grep zero; PROD grep same source
    but not probed at runtime.
  - F8 aggregate telemetry — U2 unmeasured LOCAL; PROD unmeasured
    also.
  P3 governance decisions should be gated on PROD validation for
  findings that would drive schema migrations, retrofills, or
  path-retirement actions.

### 20.5 Conflicts between sources

- **S2101 D5 vs S2102 F6 (reclassification).** S2101 called
  0-backfill-LOCAL a drift finding attributed to "backfill flow
  does not run in dev environment"; S2102 refines to design intent
  (task not scheduled anywhere). **Resolution:** S2102 F6
  supersedes S2101 D5 with disposition change LOW / DESIGN-INTENT.
  S2101 D5's finding text remains accurate; the classification
  changes.
- **S2101 F4 vs S2102 §15.4 (reclassification).** S2101 called
  `build_docs_provenance` unscheduled a DRIFT finding; S2102 finds
  it is deliberate per S1145 Plan B design vs Chris directive
  fragile execution. **Resolution:** downgraded to design gap
  requiring P3 decision (schedule or CI-lint).
- **Parent §5.2 "two-lane" framing vs F1 three-chunker refinement.**
  Parent §5.2 defined the scope as LOCAL vs PROD divergence
  (10.66 vs 17.81); F1 refines to three chunkers with two lanes on
  the PROD side. **Resolution:** F1 EXPANDS the parent framing;
  parent §5.2 scope description is CORRECT for its abstraction
  level (LOCAL vs PROD lane count); F1 is a substrate-level
  refinement.

### 20.6 Verifier-loop corrections (Rigby SIGN fold notes)

**Rigby SIGN cycle 1 completed 2026-07-04** on preserved Group 2100
arc pin `pa-18b095bb7c4740be` across 4 batches (Q1-Q5 executive
summary + entry points + runtime flows + chunker regime + integrations;
Q6-Q10 event flows + maturity + F1 + F2 + F3; Q11-Q15 F4 + F5 + F6 +
F7 + F8; Q16-Q20 T-table + duplicates + P3/P4 handoffs + unknowns +
conflicts).

**Cycle 1 result: CLEAN with 20 STRENGTHEN + 0 CLEAN + 0 FOLD +
0 REJECT.** All 20 STRENGTHEN folds landed pre-commit. Cycle 2 not
required per Rigby explicit closure statement 2026-07-04.

**Fold summary by section:**
- §1 Executive Summary: ranking rubric added (Q1); F1/F3 co-top
  classification made explicit.
- §3 Canonical Entry Points: exhaustiveness method line added (Q2);
  potential `content/rag_integration.py` sweep flagged as R2.9.
- §7 Runtime Flows: OpsRun.status transitions + authority hook
  timing added to Path B diagram (Q3).
- §9 Integrations: Docs↔Documentation Manager Path A reclassified
  MISSING → OVERCOUPLED/MIS-BOUND (Q5).
- §10 Event Flows: two-layer event architecture (EventBus milestones
  + OpsRunEvent + alert-class) recommended (Q6).
- §13 Architecture Maturity: PARTIAL vs WORKING tipping rule
  documented (Q7).
- §14 Known Drift F1-F8:
  - F1: MEDIUM-now / HIGH-blocker-for-P3 (Q8)
  - F2: MEDIUM+/HIGH + backfill decision + Chris D-verdict (Q9)
  - F3: recommended lean = option (b) or (a); option (c) off-table
    (Q10)
  - F4: risk-class label + why-not-HIGH note + promote-to-HIGH
    trigger (Q11)
  - F5-partial: derivation acquitted; upstream unresolved to U1
    (Q12)
  - F6: LOW + category=incomplete wiring (not drift not design
    intent) + over-claim admission (Q13, Q20)
  - F7: MEDIUM current harm / HIGH criticality as enabling substrate
    (Q14)
  - F8: derivative/contingent on F3 option choice (Q15)
- §15 Debt Table: T11 merged into T10 as T10' (Q16); T10' renamed
  to "Contract fields + population discipline"
- §17 Duplicates: renamed and re-ordered — Path A/B is primary
  §17.1; chunker B/C is §17.2 "overlapping chunker regimes with
  contract divergence" (Q4, Q17)
- §19 Recommended Future Research: P3 triage list — P3.1 R3.5 /
  P3.2 R3.2 / P3.3 R3.3 must-ship; others backlog (Q18); §19.2 P4
  handoff shape with explicit R4.5 branch structure (Q19)
- §20.4 Unknowns: U6 LOCAL↔PROD comparability meta-unknown added
  (Q20)

### 20.7 Chunk-per-doc distribution comparison table

| Statistic | S2101 baseline | S2102 re-measure | Drift |
|-----------|----------------|-------------------|-------|
| total chunks | 51,789 | 51,952 | +163 (+0.3%) — 1 daily beat fire |
| mean chunks/doc | 17.81 | 17.85 | +0.04 |
| p50 chunks/doc | 11 | 11 | 0 |
| p95 chunks/doc | 47 | 47 | 0 |
| p99 chunks/doc | 169 | 169 | 0 |
| max chunks/doc | 443 | 443 | 0 |

**Drift bound:** all quantile shape invariants preserved within
0.2%. S2101 baseline valid for P2 findings.

### 20.8 Naming conventions used

- **F1..F8** — S2102-new drift findings.
- **T1..T17** — S2101 debt table extended with S2102 additions.
- **KD-1..KD-7** — S2101 knowledge-debt taxonomy re-observed.
- **R2.x** — P2-scoped follow-up recommendations.
- **R3.x** — P2 → P3 handoffs.
- **R4.x** — P2 → P4 handoffs.
- **U1..U5** — Unresolved unknowns.
- **D2100.x** — Chris-ratified D-verdicts from parent §8.

---

**End of S2102 P2 audit doc.** Total lines: 1,795 post-fold. `status:
active` post Rigby SIGN cycle 1 CLEAN + Chris "agree all" ratification
of 10-item close card 2026-07-04.

**Chris ratified 10 items 2026-07-04:**
1. F1 three-chunker regime + severity split MEDIUM-now / HIGH-blocker-for-P3
2. F2 overlap-metadata data lie → **D2100.11 candidate** surfaced as
   Chris D-verdict at close; retrofill choice (a) forward-fix only vs
   (b) forward-fix + retrofill remains OPEN — deferred to R2.7 execution
   PR OR P3 governance-decision, whichever lands first
3. F3 dual-cascade paths HIGH + recommended lean (b) fold A into B
4. F4 build_rag_corpus on_warning MEDIUM
5. F5-partial upstream trace deferred to U1
6. F6 backfill dormancy LOW / incomplete-wiring category + over-claim
   admission
7. F7 EventBus MISSING dual-severity (MEDIUM current / HIGH criticality)
8. F8 step-4 timeout derivative/contingent on F3
9. §15 T-table additions +2 HIGH + 3 MEDIUM + 1 LOW + T11-into-T10' merge
10. Draft → Active + commit/PR + full 4-step docs cascade + `build_docs_provenance`
