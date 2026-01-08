# Session 730: pgvector Embedding Audit

**Date:** January 7, 2026
**Objective:** Ensure all embedding fields use pgvector VectorField instead of JSONField

---

## Summary

| Status | Count | Description |
|--------|-------|-------------|
| **Using pgvector** | 2 | Already migrated |
| **Need Migration** | 9 | Currently using JSONField |
| **Empty/No Table** | 2 | Can migrate without data concerns |

---

## Models Already Using pgvector

| Model | Location | Dimensions | Records |
|-------|----------|------------|---------|
| `UnifiedEmbedding` | `persistence/models.py:130` | 1536 | 0 |
| `ConversationMemory` | `core/models/conversations/models.py` | 1536 | 617 |

---

## Models Requiring Migration (JSONField → pgvector)

### Priority 1: High Volume (>1000 records)

| Model | Location | Field | Records | Dimensions |
|-------|----------|-------|---------|------------|
| `SpiderData` | `core/models_unified_system.py:3104` | `embedding` | 11,181 (10,253 populated) | 1536 |
| `DocumentEmbedding` | `content/models.py:642` | `embedding_vector` | 7,239 (all populated) | 1536 |

### Priority 2: Medium Volume (100-1000 records)

| Model | Location | Field | Records | Dimensions |
|-------|----------|-------|---------|------------|
| `AgentMemory` | `core/models_unified_system.py:9509` | `embedding` | 843 (all populated) | 1536 |

### Priority 3: Low Volume (<100 records)

| Model | Location | Field | Records | Dimensions |
|-------|----------|-------|---------|------------|
| `BusinessResearchResult` | `core/models_unified_system.py:13828` | `embedding` | 31 (all populated) | 1536 |
| `MemoryCluster` | `core/models_unified_system.py:9880` | `centroid_embedding` | 6 (all populated) | 1536 |
| `LegalResearchResult` | `core/models_unified_system.py:16227` | `embedding` | 2 (all populated) | 1536 |
| `LegalMemory` | `core/models_unified_system.py:16421` | `embedding` | 1 (0 populated) | 1536 |

### Priority 4: Empty Models (0 records)

| Model | Location | Field | Notes |
|-------|----------|-------|-------|
| `CodeEmbedding` | `self_awareness/models.py:224` | `embedding_vector` | No data, safe to migrate |
| `LearningEmbedding` | `ai_core/intelligence/models.py:185` | `embedding_vector` | Table doesn't exist (never migrated) |

### SpiderData item_embeddings (Special Case)

| Model | Location | Field | Notes |
|-------|----------|-------|-------|
| `SpiderData` | `core/models_unified_system.py:3110` | `item_embeddings` | Dict of embeddings, keep as JSONField |

---

## Migration Strategy

### Phase 1: Create Migration Files

For each model, create a migration that:
1. Drops existing JSONField column (if exists)
2. Adds pgvector VectorField with dimensions=1536
3. Creates HNSW index for cosine similarity search

### Phase 2: Update Model Definitions

Update each model to use:
```python
try:
    from pgvector.django import VectorField
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    VectorField = None

# In model:
embedding = VectorField(
    dimensions=1536,
    null=True,
    blank=True,
    help_text="Vector embedding for semantic search (pgvector)"
) if HAS_PGVECTOR else models.JSONField(
    null=True,
    blank=True,
    help_text="Vector embedding (JSON fallback)"
)
```

### Phase 3: Create Backfill Tasks

For models with existing data, create Celery tasks to:
1. Read existing JSON array from database
2. Convert to pgvector format
3. Save back to VectorField

---

## Index Strategy

Use HNSW index for all embedding fields:
```sql
CREATE INDEX IF NOT EXISTS {table}_{field}_hnsw_idx
ON {table}
USING hnsw ({field} vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## Files to Modify

1. `content/models.py` - DocumentEmbedding
2. `core/models_unified_system.py` - 6 models (SpiderData, AgentMemory, MemoryCluster, BusinessResearchResult, LegalResearchResult, LegalMemory)
3. `self_awareness/models.py` - CodeEmbedding
4. `ai_core/intelligence/models.py` - LearningEmbedding (optional, table doesn't exist)

---

## Notes

- All embeddings are 1536 dimensions (OpenAI text-embedding-3-small)
- `SpiderData.item_embeddings` should remain JSONField (dict structure, not simple vector)
- pgvector extension already installed (v0.8.1)
- HNSW indexes provide fast approximate nearest neighbor search
