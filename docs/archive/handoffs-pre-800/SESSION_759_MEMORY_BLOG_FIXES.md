# Session 759: Memory Palace & Blog Surfacing Fixes

**Date:** January 15, 2026
**Focus:** Agent memory quality improvements and blog content visibility

## Summary

Fixed multiple issues related to agent memories and content visibility:
1. Neural Orchestra Learning System Card showing real data instead of 0s
2. ContentWriterAgent blogs now surface in Human Interface
3. Error messages properly captured in failure memories
4. Tool names correctly displayed instead of "unknown"

## Changes Made

### 1. Neural Orchestra Learning System Card Fix

**File:** `ai_core/consciousness/neural_orchestra_reality_bridge.py`

**Issue:** Learning System Card showed 0s for all metrics:
- Feedback Processed: 0
- Insights Generated: 0
- Memory Crystals: 1

**Root Cause:** Card was reading from empty in-memory `LearningLoop` buffers instead of actual database tables.

**Fix:** Rewrote `get_learning_status_api_data()` to use synchronous DB queries:
```python
def get_learning_status_api_data(self) -> Dict[str, Any]:
    """Uses synchronous DB queries to avoid thread executor conflicts."""
    from core.models_unified_system import AgentLearning, AgentExecution, MemoryCluster

    feedback_processed = AgentExecution.objects.filter(
        created_at__gte=last_7d, status='completed'
    ).count()

    insights_generated = AgentLearning.objects.filter(
        created_at__gte=last_7d
    ).count()

    memory_crystals = MemoryCluster.objects.count()
```

**Result After Fix:**
```json
{
    "learning_active": true,
    "models_active": 15,
    "feedback_processed": 574,
    "insights_generated": 7038,
    "memory_crystals": 14
}
```

### 2. ContentWriterAgent Blogs Surface in Human Interface

**File:** `core/tasks.py`

**Issue:** ContentWriterAgent was creating blogs (927 in SelfBlog table) but they weren't visible in the UI.

**Root Cause:** `generate_self_blog_task` didn't create `HumanAttentionItem` records.

**Fix:** Added attention item creation after blog generation:
```python
# Session 759: Create attention item so blogs surface in Human Interface
try:
    from core.services.human_attention_bridge import HumanAttentionBridge
    bridge = HumanAttentionBridge()
    bridge.create_content_review_attention(
        content_type='blog',
        title=blog.title,
        summary=f"New blog post generated: {blog.meta_description[:100]}",
        content_id=str(blog.id),
        agent_name='ContentWriterAgent',
        quality_score=80,
    )
except Exception as attention_error:
    logger.warning(f"Failed to create attention item: {attention_error}")
```

### 3. Backfill Command for Existing Blogs

**File:** `core/management/commands/backfill_blog_attention.py`

Created new management command to create attention items for existing blogs:
```bash
python manage.py backfill_blog_attention           # Process recent blogs (7 days)
python manage.py backfill_blog_attention --limit 100
python manage.py backfill_blog_attention --dry-run
python manage.py backfill_blog_attention --max-age-days 14
python manage.py backfill_blog_attention --all-time  # Include ALL blogs
```

**Key Features:**
- Default 7-day age filter to prevent old content surfacing
- `--all-time` flag to process all blogs regardless of age
- Dry-run mode for testing
- Deduplication (skips blogs that already have attention items)

**Initial Run:** Deleted 452 old attention items (>7 days), created ~500 for recent blogs.

### 4. Error Messages in Failure Memories

**Files:**
- `core/agents/base_agent.py`
- `core/agent_router.py`

**Issue:** Failed agent executions showed empty error messages in Memory Palace.

**Root Cause:**
- `result.error` wasn't being saved to execution record
- Memory builder used `result.message` (empty on failures) instead of `result.error`

**Fix in base_agent.py:**
```python
# Session 759: Use result.error for failures instead of result.message
if result.success:
    content_parts.append(f"{status}: {result.message or task[:100]}")
else:
    error_msg = result.error or result.message or "Unknown error"
    content_parts.append(f"{status}: {task[:100]}")
    content_parts.append(f"\nError: {error_msg}")
```

**Fix in agent_router.py:**
```python
# Session 759: Include result.error for failed executions
self._complete_execution(
    execution_record,
    agent_name,
    success=result.success,
    output_data={
        'error': result.error if not result.success else None,  # Session 759
    },
    error_message=result.error if not result.success else None,  # Session 759
)
```

### 5. Tool Names Display Correctly

**File:** `core/agents/base_agent.py`

**Issue:** All agent memories showed "Tools: unknown" in Memory Palace.

**Root Cause:** Different agents use different keys for tool calls:
- Some use `'name'`
- ResearchAgent uses `'tool'`
- OpenAI format uses `'function.name'`

**Fix:** Check multiple possible keys:
```python
# Session 759: Check for both 'name' and 'tool' keys
if result.tool_calls:
    tools_used = [
        tc.get('name') or tc.get('tool') or tc.get('function', {}).get('name') or 'unknown'
        for tc in result.tool_calls
    ]
    key_fields.append(f"Tools: {', '.join(tools_used[:5])}")
```

## Commits

1. `0b6a9da4` - fix(Session 758): Neural Orchestra Learning System Card shows real data
2. `658b0214` - fix(Session 759): ContentWriterAgent blogs now surface in Human Interface
3. `7097459e` - feat(Session 759): Add backfill_blog_attention management command
4. `cd2ea147` - fix(Session 759): Add age filter to backfill_blog_attention command
5. `35dd0251` - fix(Session 759): Include error message in failure memories
6. `b3b7eee4` - fix(Session 759): Capture error messages for failed agent executions
7. `79a8af9f` - fix(Session 759): Fix Tools showing as 'unknown' in agent memories

## Verification

### Check Blog Attention Items
```python
from core.models_human_interface import HumanAttentionItem
from django.utils import timezone
from datetime import timedelta

recent = HumanAttentionItem.objects.filter(
    source_type__startswith='content:blog',
    created_at__gte=timezone.now() - timedelta(days=7)
)
print(f"Recent blog attention items: {recent.count()}")
```

### Check Memory Error Messages
```python
from core.models_unified_system import AgentMemory

failures = AgentMemory.objects.filter(valence='negative').order_by('-created_at')[:5]
for m in failures:
    print(f"{m.title}: {m.content[:200]}")
```

### Check Tool Names
```python
from core.models_unified_system import AgentMemory

recent = AgentMemory.objects.order_by('-created_at')[:10]
for m in recent:
    if 'Tools:' in m.key_fields_summary:
        print(m.key_fields_summary)
```

## ResearchAgent Investigation

During this session, investigated ResearchAgent failures in Memory Palace:
- **24 successes, 8 failures** in memory records
- Failures typically from complex queries without clear tool triggers
- Spider services verified working (Pinterest: 1 result, AI: 10, Trending: 10)
- LLM doesn't always generate tool calls for vague/complex prompts

## Next Steps

1. Monitor new blog posts appear in Human Interface
2. Verify error messages show in Memory Palace for failures
3. Verify tool names display correctly in new memories
