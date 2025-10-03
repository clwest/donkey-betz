# 🚀 Embedding Optimization Implementation Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install diskcache
```

### 2. Update Settings
```python
# settings.py
EMBEDDING_CONFIG = {
    'model': 'text-embedding-3-small',  # or 'text-embedding-3-small' for 5x cost savings
    'dimensions': 1536,  # 1536 for ada-002, 1536 for 3-small
}

EMBEDDING_CACHE_DIR = '/var/cache/embeddings'
EMBEDDING_HOT_CACHE_SIZE = 1000  # In-memory entries
EMBEDDING_WARM_CACHE_GB = 10     # Disk cache size
EMBEDDING_CACHE_TTL = 3600       # 1 hour default
```

### 3. Update EmbeddingService
```python
# In embedding_service.py, replace __init__ with:
def __init__(self):
    self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    self.model = settings.EMBEDDING_CONFIG['model']
    self.dimensions = settings.EMBEDDING_CONFIG['dimensions']
    
    # Use new cache manager
    from ai_partner.cache_manager import get_cache_manager
    self.cache_manager = get_cache_manager()
```

### 4. Enable Deduplication
```python
# In UnifiedMemoryService.create_memory()
# Before generating embedding:
content_hash = hashlib.sha256(
    (content_text + str(user.id) + agent_name).encode()
).hexdigest()

# Check if already exists
existing = UnifiedMemoryEntry.objects.filter(
    user=user,
    content_hash=content_hash
).first()

if existing:
    logger.info(f"Skipping duplicate content: {content_hash[:8]}")
    return existing
```

### 5. Create PGVector Index
```sql
-- Run this migration
CREATE INDEX unified_memory_embedding_idx 
ON unified_memory_entries 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### 6. Update Search to Use Index
```python
# In _semantic_search(), replace the manual loop with:
from pgvector.django import CosineDistance

results = UnifiedMemoryEntry.objects.annotate(
    distance=CosineDistance('embedding', query_embedding)
).filter(
    user=user,
    is_active=True,
    embedding__isnull=False
).order_by('distance')[:limit]
```

## Management Commands

```bash
# View cache statistics
python manage.py manage_embedding_cache stats

# Prewarm cache on startup
python manage.py manage_embedding_cache prewarm --limit 500

# Export cache before deployment
python manage.py manage_embedding_cache export --file /tmp/embeddings_backup.json

# Import cache after deployment
python manage.py manage_embedding_cache import --file /tmp/embeddings_backup.json

# Clear cache if needed
python manage.py manage_embedding_cache clear --tier hot
```

## Monitoring

Add to your monitoring dashboard:
```python
# views.py
@api_view(['GET'])
def embedding_stats(request):
    from ai_partner.cache_manager import get_cache_manager
    cache_manager = get_cache_manager()
    
    return Response({
        'cache_stats': cache_manager.get_stats(),
        'recommendations': {
            'increase_hot_cache': cache_manager.stats['evictions'] > 100,
            'add_prewarm': cache_manager.stats['misses'] > cache_manager.stats['hot_hits']
        }
    })
```

## Cost Optimization Settings

### For Development (Fast & Cheap)
```python
EMBEDDING_CONFIG = {
    'model': 'text-embedding-3-small',
    'dimensions': 1536,
}
# 5x cheaper than ada-002, similar quality
```

### For Production (Quality)
```python
EMBEDDING_CONFIG = {
    'model': 'text-embedding-3-large', 
    'dimensions': 3072,
}
# Better quality, still 3x cheaper than ada-002
```

## Performance Targets

After implementation, you should see:
- Cache hit rate: >80%
- API calls: -70% reduction
- Search latency: <100ms (from >1s)
- Cost per 1K embeddings: <$0.02

## Rollback Plan

If issues arise:
1. Set `EMBEDDING_HOT_CACHE_SIZE = 100` (original)
2. Comment out cache_manager usage
3. Revert to original generate_embedding code
4. Drop PGVector index if causing issues

The system will continue working with original performance.