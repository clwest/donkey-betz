# Code Changes File

## Fix 1: TaskOrchestration Attribute Error

### File: backend/agent_orchestra/models.py
**Issue**: Missing overall_progress attribute causing AttributeError
**Current Code (lines 175-187)**:
```python
def __str__(self):
    return f"{self.user.username} - {self.master_task[:50]}... ({self.overall_status})"

# Compatibility properties for field name differences
@property
def created_at(self):
    """Compatibility property - maps created_at to started_at"""
    return self.started_at

@property
def updated_at(self):
    """Compatibility property - uses completed_at if available, otherwise started_at"""
    return self.completed_at if self.completed_at else self.started_at
```

**Proposed Fix (add after line 187)**:
```python
@property
def overall_progress(self):
    """Compatibility property - maps overall_progress to completion_percentage"""
    return self.completion_percentage

@overall_progress.setter
def overall_progress(self, value):
    """Setter for backward compatibility"""
    self.completion_percentage = value

# Optional: Add deprecation warning
def save(self, *args, **kwargs):
    """Override save to ensure consistency"""
    # If overall_progress was set directly (shouldn't happen with property)
    # ensure completion_percentage is synced
    if hasattr(self, '_overall_progress'):
        self.completion_percentage = self._overall_progress
    super().save(*args, **kwargs)
```

**Explanation**: This creates a property alias that maps overall_progress to completion_percentage, maintaining backward compatibility without changing the database schema.

**Side Effects**: 
- All code using overall_progress will now work
- No database migration needed
- Future code should use completion_percentage directly

**Tests**:
```python
def test_overall_progress_compatibility():
    orch = TaskOrchestration.objects.create(
        user=test_user,
        master_task="Test task",
        completion_percentage=50
    )
    assert orch.overall_progress == 50
    orch.overall_progress = 75
    assert orch.completion_percentage == 75
```

---

## Fix 2: User Data Isolation Breach

### File: backend/ukf_integration/simple_ukf_bridge.py
**Issue**: Hardcoded fallback to user_id=3
**Current Code (lines 24-26)**:
```python
def __init__(self, user_id: Optional[int] = None):
    # Default to testuser (ID=3) if no user_id provided, but prefer authenticated user
    self.user_id = user_id if user_id is not None else 3
```

**Proposed Fix**:
```python
def __init__(self, user_id: int):
    """
    Initialize UKF Bridge for a specific user.
    
    Args:
        user_id: Required user ID - no defaults for security
        
    Raises:
        ValueError: If user_id is not provided or invalid
    """
    if not user_id or not isinstance(user_id, int) or user_id < 1:
        raise ValueError(f"Valid user_id required, got: {user_id}")
    
    self.user_id = user_id
    
    # Initialize unified memory service for the user
    if DJANGO_UKF_AVAILABLE:
        self.unified_search = UnifiedMemoryService(user_id=self.user_id)
    else:
        self.unified_search = None
        logger.warning(f"UnifiedMemoryService not available for user {user_id}")
```

**Explanation**: Removes the dangerous default that could cause cross-user data access. Forces explicit user_id provision.

**Side Effects**:
- All code calling SimpleUKFBridge must provide user_id
- Will break tests using default - they need updating
- Improves security significantly

---

## Fix 3: Async Event Loop Conflicts

### File: backend/ukf_integration/simple_ukf_bridge.py
**Issue**: Using asyncio.run() inside already-running event loops
**Current Code (lines 49-65)**:
```python
import asyncio
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = None

if loop and loop.is_running():
    # We're in an async context, use sync_to_async
    from asgiref.sync import sync_to_async
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(
            asyncio.run, 
            self.unified_search.search_memories(...)
        )
        results = future.result(timeout=30)
else:
    # We're in a sync context, safe to use asyncio.run()
    results = asyncio.run(self.unified_search.search_memories(...))
```

**Proposed Fix**:
```python
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

# Create a synchronous version of the async method
def search_knowledge(self, query: str, limit: int = 20, 
                    include_types: List[str] = None,
                    include_categories: List[str] = None,
                    include_participants: List[str] = None) -> Dict[str, Any]:
    """
    Unified search using Django models only - all data migrated from SQLite
    """
    if DJANGO_UKF_AVAILABLE and self.unified_search:
        try:
            logger.info(f"SimpleUKFBridge: Searching for '{query}' with user_id={self.user_id}")
            
            # Use Django's async_to_sync for reliable conversion
            search_memories_sync = async_to_sync(self.unified_search.search_memories)
            
            # Call the sync version
            results = search_memories_sync(
                query=query,
                agent_name='simple_ukf_bridge',
                user_id=self.user_id,
                limit=limit,
                search_type='hybrid'
            )
            
            logger.info(f"SimpleUKFBridge: Found {len(results)} results")
            return {'results': results, 'source': 'unified_memory'}
            
        except Exception as e:
            logger.error(f"SimpleUKFBridge: Search failed: {str(e)}")
            return {'results': [], 'error': str(e)}
    else:
        logger.warning("UnifiedMemoryService not available")
        return {'results': [], 'error': 'Service unavailable'}
```

**Explanation**: Uses Django's async_to_sync which properly handles event loop contexts, avoiding conflicts.

**Side Effects**:
- More reliable async/sync conversion
- No more event loop errors
- Slightly different error handling

---

## Fix 4: Validation Concatenation Error

### File: backend/ai_partner/personal_ai_services.py  
**Issue**: String concatenation with list type
**Current Code (lines 2525-2531)**:
```python
# Ensure task_description is a string (handle lists gracefully)
if isinstance(task_description, list):
    task_desc_str = ' '.join(str(item) for item in task_description)
else:
    task_desc_str = str(task_description)

base_message = f"""I'll help you with: {task_desc_str}
```

**Proposed Fix**:
```python
# Robust task_description handling
def safe_string_convert(obj):
    """Safely convert any object to string for concatenation"""
    if obj is None:
        return ""
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, (list, tuple)):
        # Filter None values and convert each item
        return ' '.join(safe_string_convert(item) for item in obj if item is not None)
    elif isinstance(obj, dict):
        # For dict, use key-value pairs
        return ' '.join(f"{k}: {v}" for k, v in obj.items() if v is not None)
    else:
        return str(obj)

# Use the safe converter
task_desc_str = safe_string_convert(task_description)
if not task_desc_str:
    task_desc_str = "your request"

base_message = f"""I'll help you with: {task_desc_str}

I'm preparing to deploy {agent_name} to assist with this task."""
```

**Explanation**: Handles all possible types that task_description might be, preventing concatenation errors.

**Side Effects**:
- No more concatenation errors
- Better handling of edge cases
- Cleaner error messages

---

## Fix 5: Memory Context Not Being Utilized

### File: backend/ai_partner/personal_ai_services.py
**Issue**: Over-filtering causing 0 memories to be used
**Current Code (lines 1334-1361)**:
```python
# Validate and rank contexts
validated_results = validator.filter_and_rank_contexts(
    query=query,
    contexts=combined_results,
    max_results=5
)

# Quality filtering
quality_threshold = self.user_profile.get('quality_threshold', 0.3)
validated_results = [
    r for r in validated_results 
    if r.get('quality_score', 0) >= quality_threshold
]

# Rank memories by quality and relevance
ranker = MemoryRanker()
ranked_results = ranker.rank_memories(validated_results, query)

# Take more results for better context
selected_results = ranked_results[:10]  # Increased from 5
```

**Proposed Fix**:
```python
# Import the correct validation service
from core.services.validation_service import UnifiedValidationService

# More lenient validation to avoid over-filtering
unified_validator = UnifiedValidationService()

# First, score all results without filtering
scored_results = []
for result in combined_results:
    # Extract content for relevance scoring
    content = ""
    if isinstance(result, dict):
        content = result.get('content', '') or result.get('text', '') or str(result)
    else:
        content = str(result)
    
    # Calculate relevance score
    relevance = unified_validator.validate_context_relevance(content, query)
    
    # Add score to result
    if isinstance(result, dict):
        result['relevance_score'] = relevance
    else:
        result = {'content': content, 'relevance_score': relevance, 'original': result}
    
    scored_results.append(result)

# Sort by relevance
scored_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

# Apply minimal quality threshold (much lower than before)
quality_threshold = self.user_profile.get('quality_threshold', 0.1)  # Reduced from 0.3
validated_results = [
    r for r in scored_results 
    if r.get('relevance_score', 0) >= 0.05  # Very low threshold
]

# If we filtered everything out, use top 10 anyway
if not validated_results and scored_results:
    logger.warning(f"All {len(scored_results)} results filtered out, using top 10 unfiltered")
    validated_results = scored_results[:10]

# Don't need additional ranking since we already sorted by relevance
selected_results = validated_results[:15]  # Take more for better context

logger.info(f"Memory selection: {len(combined_results)} found -> {len(validated_results)} validated -> {len(selected_results)} selected")
```

**Explanation**: Reduces filtering aggressiveness to ensure memories are actually used in prompts.

**Side Effects**:
- More memories included in context
- Potentially some less relevant memories included
- Better AI responses with context

---

## Fix 6: Performance - Add Database Indexes

### File: New migration - backend/shared_memory/migrations/0010_performance_indexes.py
**Issue**: No indexes causing slow queries
**Proposed Fix**:
```python
from django.db import migrations
from django.contrib.postgres.operations import BtreeGinExtension

class Migration(migrations.Migration):
    
    atomic = False  # For large tables, non-atomic is safer
    
    dependencies = [
        ('shared_memory', '0009_auto_20240101_0000'),  # Update with actual latest
    ]

    operations = [
        # Enable extensions if needed
        BtreeGinExtension(),
        
        # User + Created index for fast user queries
        migrations.RunSQL(
            sql="CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_unified_memory_user_created ON unified_memory_entries(user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_unified_memory_user_created;",
        ),
        
        # Content search index
        migrations.RunSQL(
            sql="CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_unified_memory_content ON unified_memory_entries USING gin(to_tsvector('english', content_text));",
            reverse_sql="DROP INDEX IF EXISTS idx_unified_memory_content;",
        ),
        
        # Quality score index for filtering
        migrations.RunSQL(
            sql="CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_unified_memory_quality ON unified_memory_entries(quality_score DESC) WHERE quality_score > 0;",
            reverse_sql="DROP INDEX IF EXISTS idx_unified_memory_quality;",
        ),
        
        # Composite index for common query pattern
        migrations.RunSQL(
            sql="CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_unified_memory_composite ON unified_memory_entries(user_id, quality_score DESC, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_unified_memory_composite;",
        ),
        
        # If using embeddings with pgvector
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN 
                IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
                    EXECUTE 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_unified_memory_embedding ON unified_memory_entries USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);';
                END IF;
            END $$;
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_unified_memory_embedding;",
        ),
    ]
```

**Explanation**: Adds critical indexes for common query patterns, dramatically improving performance.

**Side Effects**:
- Initial index creation may take time on large tables
- Slight overhead on inserts (worth it for query speed)
- 50-80% query performance improvement expected

**Tests**:
```python
def test_query_performance():
    import time
    
    # Test query before indexes
    start = time.time()
    memories = UnifiedMemoryEntry.objects.filter(
        user_id=1,
        quality_score__gte=0.5
    ).order_by('-created_at')[:100]
    list(memories)  # Force evaluation
    duration_before = time.time() - start
    
    # Apply indexes
    call_command('migrate', 'shared_memory', '0010')
    
    # Test query after indexes
    start = time.time()
    memories = UnifiedMemoryEntry.objects.filter(
        user_id=1,
        quality_score__gte=0.5
    ).order_by('-created_at')[:100]
    list(memories)  # Force evaluation
    duration_after = time.time() - start
    
    # Should be at least 50% faster
    assert duration_after < duration_before * 0.5
```