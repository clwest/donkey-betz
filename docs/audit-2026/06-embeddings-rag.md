# Dossier #6: Embeddings + RAG

**Audited:** April 6, 2026
**Status:** WORKING — centralized embedding service, 7 embedding stores, multiple search implementations

---

## 1. Purpose

The Embeddings and RAG system enables semantic search across ALL platform data — spider intelligence, agent memories, user documents, internal docs, conversations, code, and legal research. It powers the knowledge retrieval layer that feeds agent prompts (Dossier #5, Layers 6 and 10) and enables the content pipeline's claims assembly (Dossier #4, Stage 1).

## 2. Runtime Evidence

- **Centralized EmbeddingService** with cost tracking, 7-day Redis cache
- **7 embedding stores** across different models (spider, memory, conversation, document, code, legal, business research)
- **pgvector** extension with HNSW indexes for fast cosine similarity
- **Backfill tasks** running every 15 minutes for spider data
- **LLMCallLog** records every embedding API call with cost

## 3. Entry Points

| Trigger | What Gets Embedded | Schedule |
|---------|-------------------|----------|
| Celery Beat | SpiderData (backfill) | Every 15 minutes, batch=100 |
| Celery Beat | AgentMemory (backfill) | Disabled (token conservation) |
| Celery Beat | ConversationMemory (backfill) | Disabled (token conservation) |
| Agent execution | New AgentMemory | On each successful execution |
| Spider crawl | New SpiderData | After `process_core_spider_data` |
| User upload | DocumentEmbedding | On upload via `/api/rag/upload` |
| Management command | docs/ index | `python manage.py build_docs_index` (not embeddings, metadata only) |

## 4. Execution Chain — What Gets Embedded and How

### Centralized Embedding Service
```
core/services/embedding_service.py
  │
  ├─ Model: text-embedding-3-small (1536 dimensions)
  ├─ Cost: $0.02 per 1M tokens
  ├─ Cache: Redis, 7-day TTL
  │   Key format: emb:{model}:{sha256(text)[:16]}
  │
  ├─ create_embedding(text) → single vector
  │   1. Check Redis cache → return if hit
  │   2. Call OpenAI API
  │   3. Cache result (7 days)
  │   4. Log to LLMCallLog (cost, tokens)
  │   5. Return 1536-dim vector
  │
  └─ create_embeddings(texts[]) → batch vectors
      1. Check cache for each text → split hits/misses
      2. API call only for misses
      3. Cache new results
      4. Return BatchEmbeddingResult with stats
```

### 7 Embedding Stores

| Store | Model | Table | Dimensions | Index | Purpose |
|-------|-------|-------|-----------|-------|---------|
| SpiderData | `core_spiderdata` | embedding + item_embeddings | 1536 | B-tree | Spider intelligence search |
| AgentMemory | `core_agentmemory` | embedding | 1536 | — | Agent learning retrieval |
| ConversationMemory | `core_conversationmemory` | embedding | 1536 | HNSW | Dialog personalization |
| DocumentEmbedding | `content_documentembedding` | embedding_vector | 1536 | HNSW (m=16, ef=64) | User document RAG |
| CodeEmbedding | `self_awareness_codeembedding` | embedding_vector | 1536 | — | Code semantic search |
| LegalDocument | `core_legaldocument` | embedding | 1536 | — | Legal research |
| BusinessResearch | `core_businessresearchresult` | embedding | 1536 | — | Business research |

### Semantic Search Implementations

**5 independent search engines**, all using cosine similarity:

```
1. Spider Semantic Search
   core/services/spider_semantic_search.py:162-275
   → Scans max 200 entries (optimization)
   → Min similarity: 0.3
   → Fallback: keyword search if embedding fails
   → Used by: Agent prompt injection (Layer 9)

2. Memory Semantic Search
   core/services/memory_embedding_service.py:279-348
   → Searches per-agent memories
   → Min similarity: 0.2 (lowered from 0.4 — best matches in 0.13-0.33 range)
   → Updates access_count on retrieval
   → Used by: Agent prompt injection (Layer 6)

3. Document RAG Search
   content/embeddings.py:931-1029
   → Chunk-based (1000 chars, 200 overlap)
   → Source filter: internal_only | external_only | all
   → Promotion gate: only 'promoted' docs searchable
   → Min similarity: 0.7
   → Used by: ClaimsPack builder, user queries

4. Knowledge Similarity Search
   core/services/knowledge_similarity.py:68-338
   → Cross-agent knowledge deduplication
   → 24-hour cache
   → Used by: Knowledge sharing system

5. Code Semantic Search
   self_awareness/embeddings.py:631-672
   → Min similarity: 0.5
   → Sorted by (similarity, importance_score)
   → Used by: Self-awareness system
```

### Risk-Aware Document Retrieval (Dossier #5 supplement)

```
core/services/scoped_retrieval.py:307-662
  │
  Dual-channel search merges 4 result streams:
  ├─ Channel 1: Semantic similarity results
  ├─ Channel 2: Critical docs (always included, limit=3)
  ├─ Channel 3: Incident docs (postmortems, 30-day window, limit=3)
  └─ Channel 4: Audit findings (open P0/P1, limit=3)
  │
  Risk re-ranking boosts:
    is_critical: +0.30
    postmortem: +0.20
    incident_report: +0.15
    security: +0.15
    constraint: +0.10
    architecture: +0.05
```

## 5. Data Contracts

| Model | Key Fields |
|-------|------------|
| EmbeddingService (singleton) | model, dimensions, cache_ttl, cost tracking |
| SpiderData.embedding | VectorField(1536), embedding_text, item_embeddings(JSON) |
| AgentMemory.embedding | VectorField(1536), safety_class, poison_risk_score |
| ConversationMemory.embedding | VectorField(1536), user(FK) |
| DocumentEmbedding.embedding_vector | VectorField(1536), chunk_index, chunk_text, processing_time_ms, embedding_cost |
| LLMCallLog | model, tokens, cost, agent_name, created_at |

## 6. External Dependencies

| Dependency | Purpose | Cost |
|------------|---------|------|
| OpenAI text-embedding-3-small | All embedding generation | $0.02/1M tokens |
| PostgreSQL pgvector | Vector storage + HNSW indexing | Included in DB |
| Redis | Embedding cache (7-day TTL) | Included in infra |

## 7. Outputs/Artifacts

Users don't see embeddings directly. They enable:
- **Relevant knowledge in agent responses** — agents cite learned patterns
- **Document search results** — `/api/rag/search` returns similarity-ranked docs
- **Spider intelligence in prompts** — trending topics matched by relevance
- **Content claims** — ClaimsPack finds evidence from embedded spider data
- **Memory retrieval** — agents recall past successes/failures

## 8. Failure Modes

| Failure | Cause | Impact | Mitigation |
|---------|-------|--------|------------|
| OpenAI API down | Embedding generation fails | New content not searchable | Keyword fallback in spider search |
| Stale embeddings | Backfill disabled/delayed | Search returns old results | 15-min backfill schedule, 7-day cache |
| pgvector not installed | Extension missing | All vector queries fail | Migration 0003 ensures extension |
| Cache miss storm | Redis restart | All embeddings re-generated | Non-fatal cache, graceful degradation |
| Embedding dimension mismatch | Model change | Similarity calculations wrong | Hardcoded 1536 everywhere |
| Memory poisoning | Test content embedded | Bad retrieval results | safety_class filter (test_only excluded) |

## 9. Current Status: WORKING (Partial)

**Active:**
- Centralized EmbeddingService with caching and cost tracking
- Spider data embedding backfill (every 15 minutes)
- Document RAG upload and search endpoints
- All 5 semantic search implementations
- pgvector HNSW indexes on DocumentEmbedding and ConversationMemory

**Disabled (token conservation):**
- AgentMemory embedding backfill
- ConversationMemory embedding backfill

**Not embedding-based (metadata only):**
- `build_docs_index` — generates JSON index + markdown, NOT vector embeddings

## Verified Data (April 6, 2026)

- **SpiderData**: 20.1% embedded (22,007 of 109,716) — significant gap
- **AgentMemory**: 97.6% embedded (1,053 of 1,079) — healthy
- **AgentKnowledgeSource**: 5,213 records (embedding coverage not measured)
- **LLM embedding cost**: $0.52 total across 258,292 embedding API calls

## 10. Truth Gaps

- ~~Embedding coverage~~: **RESOLVED** — Spider 20.1%, Memory 97.6%
- **Search quality**: DESIGN QUESTION — No evaluation of whether semantic search returns relevant results — no precision/recall metrics
- ~~Cost per month~~: **RESOLVED** — $0.52 total embedding cost
- **HNSW index effectiveness**: DESIGN QUESTION — Indexes exist on DocumentEmbedding and ConversationMemory but SpiderData uses brute-force scan (max 200 entries)
- **Cache hit rate**: DESIGN QUESTION — Redis cache logs hits/misses in batch mode but no aggregate dashboard
- **Stale embedding detection**: DESIGN QUESTION — No mechanism to detect when content changes but embedding doesn't update
- **Cross-store search**: DESIGN QUESTION — Each store has its own search — no unified search across all 7 embedding stores
- **Embedding model lock-in**: DESIGN QUESTION — Everything hardcoded to text-embedding-3-small/1536 dims — model upgrade would require full re-embedding

## Key Patent Claims (Embeddings + RAG)

1. **Multi-store vector embedding architecture** — 7 independent embedding stores across different data types, all using centralized service with cost tracking
2. **Risk-aware dual-channel retrieval** — merges semantic search with forced inclusion of critical/incident/audit documents, re-ranked by risk classification
3. **Safety-classified embedding space** — 4-tier classification prevents test/poisoned content from entering the retrieval pipeline
4. **Chunk-based document RAG with promotion gate** — user documents must be promoted before entering searchable space, with configurable chunk size/overlap
5. **Hybrid semantic-keyword search** — automatic fallback from embedding-based to keyword-based search when embedding generation fails
6. **Cross-agent knowledge deduplication** — knowledge similarity service detects near-duplicate knowledge items across the agent fleet
