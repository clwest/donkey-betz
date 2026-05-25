# Session 786: Curated Documentation Embedding Pipeline

**Date:** January 20, 2026
**Focus:** Semantic search infrastructure for curated documentation
**Status:** COMPLETE

---

## Summary

Built a complete pipeline to embed curated documentation from the Docs Index (`docs/_index.json`) and enable scope-aware semantic search. The system prioritizes curated active docs, auto-expands to superseded docs if needed, and falls back to all repo markdown.

---

## What Was Built

### 1. Document Sync Command
**File:** `core/management/commands/sync_docs_index_to_documents.py`

Syncs documents from `docs/_index.json` to the Django `Document` model with embedding generation.

```bash
# Usage
python manage.py sync_docs_index_to_documents           # Sync all
python manage.py sync_docs_index_to_documents --dry-run # Preview
python manage.py sync_docs_index_to_documents --embed   # Sync + embed
python manage.py sync_docs_index_to_documents --active-only  # Only active docs
```

**Features:**
- Maps docs index types to DocumentType (all markdown)
- Maps docs index status to ContentStatus (active→processed, superseded→archived)
- Content hashing for deduplication
- Chunking with 1000 char chunks, 200 char overlap
- Breaks at paragraph/sentence boundaries

### 2. Scoped Retrieval Service
**File:** `core/services/scoped_retrieval.py`

Scope-aware semantic search with smart defaults.

```python
from core.services.scoped_retrieval import ScopedRetrievalService, DocumentScope

service = ScopedRetrievalService()

# Default: search curated active docs only
results = service.search("agent architecture")

# Include superseded docs
results = service.search("old feature", include_superseded=True)

# Expand to all repo markdown
results = service.search("something rare", scope=DocumentScope.REPO_MARKDOWN)

# Get scope statistics
stats = service.get_scope_stats()
```

**Scopes:**
| Scope | Description |
|-------|-------------|
| `DOCS_INDEX_ACTIVE` | Curated docs with status=active (default) |
| `DOCS_INDEX_ALL` | All curated docs including superseded |
| `REPO_MARKDOWN` | All markdown in repo (uncurated) |

**Auto-Expansion:** If no results in primary scope, automatically expands to next broader scope.

### 3. Knowledge Audit Command
**File:** `core/management/commands/repo_knowledge_audit.py`

Single source of truth for document/embedding state.

```bash
python manage.py repo_knowledge_audit          # Formatted report
python manage.py repo_knowledge_audit --json   # JSON output
python manage.py repo_knowledge_audit --output=report.json  # Save to file
```

**Reports:**
- Repo markdown file counts by category
- Docs Index document counts by status
- Document model counts by type/status/source
- Embedding counts and coverage
- Sync status between systems
- Actionable recommendations

---

## Bug Fixes

### 1. EmbeddingResult Vector Extraction
**Commit:** `701baa9d`

The `EmbeddingService.create_embedding()` returns an `EmbeddingResult` dataclass, not a raw vector.

```python
# Before (broken)
embedding_vector=embedding  # Passed entire object

# After (fixed)
embedding_vector=embedding.embedding  # Extract vector from object
embedding_dimension=len(embedding.embedding)  # Add required field
```

### 2. Similarity Threshold Tuning
**Commit:** `11046a87`

OpenAI's `text-embedding-3-small` model returns similarity scores in the 0.3-0.6 range, not 0.7+.

```python
# Before
self.min_similarity = 0.7  # Too high, no results

# After
self.min_similarity = 0.4  # Appropriate for this model
```

---

## Final Statistics

| Metric | Value |
|--------|-------|
| Curated Documents | 394 |
| Curated Embeddings | 7,850 chunks |
| Total Embeddings | 18,857 |
| Avg Chunks/Document | 47.3 |
| Orphaned Embeddings | 0 |

---

## Semantic Search Test Results

| Query | Top Match | Similarity |
|-------|-----------|------------|
| "agent architecture" | Handoff 02: Agent Architecture Unification | 0.55 |
| "spider network" | Spiders Documentation | 0.66 |
| "body systems HEART" | Body Systems Reference | 0.66 |
| "celery tasks" | Celery Tasks Documentation | 0.60 |
| "websocket updates" | Rich Data Audit | 0.67 |
| "agent communication" | Agent Conversations - AI-to-AI Chat | 0.62 |

---

## Files Created/Modified

| File | Type | Purpose |
|------|------|---------|
| `core/management/commands/sync_docs_index_to_documents.py` | NEW | Sync curated docs |
| `core/management/commands/repo_knowledge_audit.py` | NEW | Knowledge audit |
| `core/services/scoped_retrieval.py` | NEW | Semantic search service |

---

## Architecture

```
docs/_index.json (1,535 docs)
        │
        ▼ sync_docs_index_to_documents
        │
Document Model (394 active docs)
        │
        ▼ EmbeddingService
        │
DocumentEmbedding (7,850 chunks)
        │
        ▼ ScopedRetrievalService
        │
Semantic Search Results
```

**Scope Expansion Flow:**
```
DOCS_INDEX_ACTIVE → DOCS_INDEX_ALL → REPO_MARKDOWN
     (curated)        (+ superseded)    (all markdown)
```

---

## Usage Examples

### Search Documentation
```python
from core.services.scoped_retrieval import get_scoped_retrieval_service

service = get_scoped_retrieval_service()

# Find agent-related docs
results = service.search("how do agents communicate")
for r in results:
    print(f"[{r.similarity_score:.2f}] {r.title}")
    print(f"  Path: {r.path}")
    print(f"  Curated: {r.is_curated}")
```

### Audit Knowledge Base
```bash
python manage.py repo_knowledge_audit
```

### Re-sync and Re-embed
```bash
# If docs index changes, re-sync
python manage.py sync_docs_index_to_documents --embed
```

---

## Next Steps (Optional)

1. **Embed Superseded Docs:** Currently only active docs are embedded. Could extend to superseded for historical context.

2. **API Endpoint:** Create REST endpoint for semantic search (e.g., `/api/docs/search/?q=agent+routing`)

3. **RAG Integration:** Connect to agent context injection for documentation-aware responses.

4. **Incremental Updates:** Add file watcher or scheduled task to detect and re-embed changed docs.

---

## Commits

1. `701baa9d` - fix(sync_docs_index): Extract embedding vector from EmbeddingResult
2. `11046a87` - fix(scoped_retrieval): Fix semantic search vector extraction and threshold

---

*Session 786 Complete - Curated documentation is now searchable via semantic search.*
