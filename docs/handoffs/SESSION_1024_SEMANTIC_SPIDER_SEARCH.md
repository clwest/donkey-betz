---
originating_session: 1024
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1024 — Semantic Spider Search (Root Cause Fix)

**Date:** February 17, 2026
**PR:** #1265

## Problem

`search_spider_data()` in `SpiderIntelligenceService` used word-boundary regex keyword matching over the 300 most recent SpiderData rows. This was the root cause behind all evidence gate issues:
- A HuggingFace ML page mentioning "blockchain" in a tag scored `relevance=1.0` for blockchain queries
- Keyword matching couldn't distinguish topical relevance from incidental word mentions
- Agents received irrelevant data and synthesized "beautiful nonsense"

## Solution

Replaced keyword search with **pgvector semantic similarity** as the primary search path in `core/services/spider_intelligence.py`.

### Architecture

```
search_spider_data(query)
  |
  +-> _semantic_search_db(query)     [PRIMARY]
  |     1. Generate query embedding (OpenAI text-embedding-3-small)
  |     2. pgvector CosineDistance KNN (HNSW index)
  |     3. Filter similarity >= 0.25
  |     4. Return top 50 results sorted by similarity
  |     Returns None on failure -> triggers fallback
  |
  +-> _keyword_search(query)         [FALLBACK]
        Original logic (word-boundary regex), unchanged
        Triggered when: pgvector ImportError, embedding API down,
        no embedded data in time window, any DB error
```

### Key Constants

```python
SEMANTIC_TOP_K = 50          # Max KNN results
SEMANTIC_MIN_SIMILARITY = 0.25  # Minimum cosine similarity threshold
NOISY_SPIDERS = frozenset({'noaa_weather', 'giphy', 'spotify', 'discord'})
```

### Infrastructure (pre-existing, no changes needed)

- `SpiderData.embedding` — pgvector VectorField(1536) with HNSW index (`spiderdata_embedding_hnsw_idx`)
- Backfill Celery task runs every 10 minutes, embeds new SpiderData via `text-embedding-3-small`
- 85% embedding coverage (4,520/5,264 entries in 72h window)

## All Callers (automatic, no changes needed)

| Caller | File | How |
|--------|------|-----|
| `spider_query` tool (ALL agents) | `base_agent.py:2701` | Calls `search_spider_data()` |
| Business research agents | `base_business_research_agent.py:767` | Calls `search_spider_data()` |
| Pre-prompt enrichment | `spider_context_builder.py:486` | Calls `search_spider_data()` |
| Research agent | `research_agent.py:1447` | Calls `search_spider_data()` |
| Frontend API | `views_spider_intelligence.py:196` | Calls `search_spider_data()` |
| Context aggregator | `super_platform/context_aggregator.py:234` | Calls `search_spider_data()` |

## Verification (Railway)

```bash
railway run python manage.py shell -c "
from core.services.spider_intelligence import SpiderIntelligenceService
svc = SpiderIntelligenceService()
results = svc.search_spider_data('blockchain security vulnerabilities', limit=5)
for r in results:
    print(f'{r[\"source\"]:20} sim={r[\"relevance\"]:.3f} {r[\"title\"][:60]}')
"
```

Results confirmed:
- Crypto queries return etherscan/blockchain data, NOT huggingface
- AI queries return relevant AI content (udemy, rel=0.576)
- No keyword fallback in normal operation
- All results show `matching_terms=['semantic_match']`

## Relationship to Evidence Gates

This is the **root cause fix** that completes the evidence gate roadmap:
- **Layers 1-3** (Session 1023): Defensive gates that reject bad data after it arrives
- **Root cause** (Session 1024): Prevents bad data from arriving in the first place

With semantic search active, the evidence gates in Layers 1-3 should rarely trigger — they remain as safety nets.

## Monitoring

- Check for `[spider_search] keyword fallback` in logs — should NOT appear in normal operation
- If it does appear, check: OpenAI API status, embedding backfill task health, pgvector availability
