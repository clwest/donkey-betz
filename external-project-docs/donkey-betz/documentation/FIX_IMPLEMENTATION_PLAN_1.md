# Fix Implementation Order

## Phase 1: Critical Fixes (Today - 8 hours)

### 1. Fix User Data Isolation (URGENT - 30 minutes)
**Files to modify**:
- `backend/ukf_integration/simple_ukf_bridge.py`
- `backend/scripts/markdown_ingestion.py`

**Changes needed**:
```python
# backend/ukf_integration/simple_ukf_bridge.py:24-26
# OLD:
def __init__(self, user_id: Optional[int] = None):
    self.user_id = user_id if user_id is not None else 3

# NEW:
def __init__(self, user_id: int):  # Required, no default
    if not user_id:
        raise ValueError("user_id is required for SimpleUKFBridge")
    self.user_id = user_id
```

**Testing required**:
- Verify no cross-user data access
- Test with multiple concurrent users
- Audit all user_id references

### 2. Fix TaskOrchestration Attribute Error (1 hour)
**Files to modify**:
- `backend/agent_orchestra/models.py`

**Changes needed**:
```python
# backend/agent_orchestra/models.py:186 (add after line 186)
@property
def overall_progress(self):
    """Alias for completion_percentage for backward compatibility"""
    return self.completion_percentage

@overall_progress.setter
def overall_progress(self, value):
    """Setter for backward compatibility"""
    self.completion_percentage = value
```

**Testing required**:
- Test agent deployment
- Verify dashboard displays progress
- Check all 12 files using overall_progress

### 3. Fix Validation Concatenation Error (30 minutes)
**Files to modify**:
- `backend/ai_partner/personal_ai_services.py`

**Changes needed**:
```python
# backend/ai_partner/personal_ai_services.py:2525-2531
# OLD:
if isinstance(task_description, list):
    task_desc_str = ' '.join(str(item) for item in task_description)
else:
    task_desc_str = str(task_description)

# NEW:
# Ensure task_description is always a string
if task_description is None:
    task_desc_str = "No task description provided"
elif isinstance(task_description, list):
    # Filter out None values and convert to strings
    task_desc_str = ' '.join(str(item) for item in task_description if item is not None)
elif not isinstance(task_description, str):
    task_desc_str = str(task_description)
else:
    task_desc_str = task_description
```

**Testing required**:
- Test with list inputs
- Test with None values
- Test with mixed types

### 4. Fix Memory Context Filtering (2 hours)
**Files to modify**:
- `backend/ai_partner/personal_ai_services.py`

**Changes needed**:
```python
# backend/ai_partner/personal_ai_services.py:1334
# OLD:
validated_results = validator.filter_and_rank_contexts(
    query=query,
    contexts=combined_results,
    max_results=5
)

# NEW:
# Use the unified validation service instead
from core.services.validation_service import UnifiedValidationService
unified_validator = UnifiedValidationService()

# Be more lenient with filtering
validated_results = []
for result in combined_results:
    relevance = unified_validator.validate_context_relevance(
        str(result.get('content', '')), 
        query
    )
    if relevance > 0.1:  # Very low threshold to avoid over-filtering
        result['relevance_score'] = relevance
        validated_results.append(result)

# If we filtered out everything, use top 5 anyway
if not validated_results and combined_results:
    logger.warning("All results filtered out, using top 5 unfiltered")
    validated_results = combined_results[:5]
```

**Testing required**:
- Verify memories are included in context
- Test with various query types
- Monitor context quality

### 5. Fix Async Event Loop Conflicts (4 hours)
**Files to modify**:
- `backend/agent_orchestra/orchestrator.py`
- `backend/ukf_integration/simple_ukf_bridge.py`
- `backend/agent_orchestra/tasks.py`

**Changes needed**:
```python
# backend/ukf_integration/simple_ukf_bridge.py:49-65
# OLD:
import asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Complex nested async handling
        ...
    else:
        results = asyncio.run(search_memories(...))

# NEW:
from asgiref.sync import async_to_sync

# Use Django's async_to_sync for consistent handling
try:
    search_memories_sync = async_to_sync(self.unified_search.search_memories)
    results = search_memories_sync(
        query=query,
        agent_name='simple_ukf_bridge',
        user_id=self.user_id,
        limit=limit,
        search_type='hybrid'
    )
```

**Testing required**:
- Test agent execution flow
- Test with Celery tasks
- Verify no event loop errors

## Phase 2: Performance Fixes (Tomorrow - 8 hours)

### 1. Add Database Indexes (1 hour)
**Create migration**:
```python
# backend/shared_memory/migrations/0010_add_performance_indexes.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('shared_memory', '0009_auto_...'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_unified_memory_user_created ON unified_memory_entries(user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_unified_memory_user_created;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_unified_memory_embedding ON unified_memory_entries USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);",
            reverse_sql="DROP INDEX IF EXISTS idx_unified_memory_embedding;"
        ),
    ]
```

### 2. Implement Redis Caching (2 hours)
**Files to modify**:
- `backend/ai_partner/personal_ai_services.py`

**Changes needed**:
```python
# Add caching for memory searches
from django.core.cache import cache

cache_key = f"memory_search:{user.id}:{hashlib.md5(query.encode()).hexdigest()}"
cached_results = cache.get(cache_key)

if cached_results:
    logger.info(f"Using cached memory results for query: {query[:50]}")
    combined_results = cached_results
else:
    # Existing search code...
    combined_results = await self._search_all_sources(query, user)
    # Cache for 5 minutes
    cache.set(cache_key, combined_results, 300)
```

### 3. Move Mythology Validation to Background (2 hours)
**Changes needed**:
- Make mythology validation async
- Return response immediately
- Validate in background and log results

### 4. Connection Pooling Setup (1 hour)
**Configure PgBouncer**:
```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
donkey_betz = host=localhost port=5432 dbname=donkey_betz

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### 5. Optimize Database Queries (2 hours)
- Add select_related() and prefetch_related()
- Fix N+1 query problems
- Batch database operations

## Phase 3: Missing Features (This Week - 16 hours)

### 1. Create Emotional Intelligence Templates (2 hours)
**Create management command**:
```python
# backend/ai_partner/management/commands/seed_emotional_templates.py
from django.core.management.base import BaseCommand
from ai_partner.models import EmotionalTemplate

class Command(BaseCommand):
    def handle(self, *args, **options):
        templates = [
            {
                'name': 'empathetic',
                'prompt': 'Respond with empathy and understanding...',
                'traits': {'empathy': 0.9, 'warmth': 0.8}
            },
            # Add 10+ templates
        ]
        
        for template_data in templates:
            EmotionalTemplate.objects.get_or_create(**template_data)
```

### 2. Fix WebSocket Real-time Updates (4 hours)
**Files to modify**:
- `backend/agent_orchestra/consumers.py`
- `backend/agent_orchestra/routing.py`

### 3. Add Error Recovery (4 hours)
**Wrap all critical operations**:
```python
try:
    result = await dangerous_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Fallback logic
    result = get_fallback_result()
    # Notify monitoring
    send_error_to_monitoring(e)
```

### 4. Implement Rate Limiting (2 hours)
```python
# backend/core/middleware/rate_limit.py
from django.core.cache import cache
from django.http import JsonResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            key = f"rate_limit:{request.user.id}"
            requests = cache.get(key, 0)
            if requests > 100:  # 100 requests per minute
                return JsonResponse({"error": "Rate limit exceeded"}, status=429)
            cache.set(key, requests + 1, 60)
        
        return self.get_response(request)
```

### 5. Security Fixes (4 hours)
- Sanitize logs
- Add CSRF protection
- Implement audit logging
- Encrypt sensitive data

## Testing Strategy

### Unit Tests Required
```python
# backend/tests/test_critical_fixes.py
class CriticalFixTests(TestCase):
    def test_user_isolation(self):
        # Test no cross-user data access
        pass
    
    def test_orchestration_progress(self):
        # Test overall_progress property
        pass
    
    def test_validation_concatenation(self):
        # Test with various input types
        pass
    
    def test_memory_context_inclusion(self):
        # Test memories are used
        pass
    
    def test_async_execution(self):
        # Test no event loop conflicts
        pass
```

### Integration Tests
- Full agent deployment flow
- Multi-user concurrent access
- Performance benchmarks
- WebSocket real-time updates

### Load Tests
```bash
# Use locust for load testing
locust -f load_tests.py --users 100 --spawn-rate 10 --host http://localhost:8000
```

## Rollback Plan

If any fix causes issues:

1. **Database**: Keep backups before migrations
```bash
pg_dump donkey_betz > backup_$(date +%Y%m%d_%H%M%S).sql
```

2. **Code**: Tag before changes
```bash
git tag pre-fixes-$(date +%Y%m%d)
git push --tags
```

3. **Quick Rollback**:
```bash
git checkout pre-fixes-20240101
python manage.py migrate shared_memory 0009  # Rollback migrations
```

## Success Metrics

After fixes, system should achieve:
- Response time: <3 seconds (from 10-21s)
- Memory usage in prompts: >0 (from 0)
- Agent deployment success: >95% (from 0%)
- No cross-user data leaks: 100% isolation
- No async errors in logs
- Error rate: <1% (from current ~20%)

## Timeline

- **Day 1 (8 hours)**: All Phase 1 critical fixes
- **Day 2 (8 hours)**: Phase 2 performance fixes
- **Days 3-5 (16 hours)**: Phase 3 missing features
- **Day 6**: Testing and verification
- **Day 7**: Documentation and deployment prep

Total: 40 hours (1 week with single developer)