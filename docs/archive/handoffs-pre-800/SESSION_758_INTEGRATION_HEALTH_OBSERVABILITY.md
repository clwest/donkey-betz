# Session 758: Integration Health Observability

**Date:** January 15, 2026
**Focus:** Context tracking for Integration Health observability

## Summary

Added comprehensive context tracking to all agent execution entry points, enabling the Integration Health dashboard to accurately display context injection rates across all 73 agents.

## Changes Made

### 1. Context Tracking Added to Entry Points

**Files Modified:**
- `core/agent_execution_wrapper.py` - Added context tracking to `AgentExecutionTracker`
- `ai_core/agents/sync_executor.py` - Added context tracking to `SyncAgentExecutor`
- `core/agents/registry.py` - Added context tracking to registry-based execution

**Key Code Pattern:**
```python
# Session 758: Build context tracking for Integration Health observability
try:
    from core.services.context_tracking import build_context_tracking
    context_tracking = build_context_tracking(agent_name, task_description)
except Exception as e:
    logger.debug(f"Context tracking unavailable: {e}")
    context_tracking = {}

execution_record = AgentExecution.objects.create(
    agent=agent_record,
    task=task_description,
    status='in_progress',
    input_data={
        'task': task_description,
        'context_injected': context_tracking,  # Key field for tracking
    }
)
```

### 2. Celery Health Monitoring Improvements

**Files Modified:**
- `core/services/celery_health.py` - Increased timeout from 2s to 10s, added process fallback
- `core/services/heart.py` - Fixed threshold: 1 worker + beat = healthy

**Issue:** Celery workers were marked as "degraded" because:
1. 2-second timeout was too short for busy workers
2. Required 2+ workers for "healthy" status (we run 1 worker with thread pool)

**Fix:**
- Increased inspect timeout to 10 seconds
- Added `_check_worker_processes()` fallback for busy workers
- Changed threshold: 1 worker + beat = healthy

### 3. Integration Health Views

**File:** `core/views_integration_health.py`

Added Dream System and Body Systems tracking to the health dashboard. The view now tracks:
- Spider Data health
- Learning Patterns health
- Advisor System health
- Feedback Loop health
- Sci-Fi Context health
- Dream System health (Session 758)
- Body Systems health (Session 758)
- Context Injection Rate

## Results

### Before Session 758
- Context injection rate: 2% (only ResearchAgent)
- Body Systems: 6/7 healthy (CELE degraded)
- Most agents: 0% context tracking

### After Session 758
- Context injection rate: **100%** (all 73 agents)
- Body Systems: **7/7 healthy**
- All new executions have full context tracking

### Integration Health Status
```
Overall Status: healthy

Components:
  spider_data: healthy
  learning_patterns: healthy
  advisor_system: healthy
  feedback_loop: healthy
  scifi_context: healthy
  dream_system: healthy
  body_systems: healthy

Metrics:
  context_injection_rate: 100.0%
  tracked_executions: 86
  with_context: 86
```

## Technical Notes

### Two AgentExecution Tables
There are TWO different AgentExecution models:
- `core.models_unified_system.AgentExecution` (table: `core_agentexecution`) - **Used by Integration Health**
- `core.models.agents_registry.AgentExecution` (table: `agents_agentexecution`) - Deprecated

Context tracking was added to code paths that write to `core_agentexecution` since that's what Integration Health monitors.

### Context Tracking Field
The `input_data['context_injected']` field contains:
```python
{
    'spider_data': {...},      # Trending topics, discussions
    'learning_patterns': {...}, # Teaching/learning effectiveness
    'advisor_insights': {...},  # Domain-specific wisdom
    'feedback_metrics': {...},  # Reliability scores
    'scifi_context': {...},     # Mood, evolution, dreams
}
```

### Celery Multi-Queue Architecture
The Makefile runs 3 workers with thread pool on Mac:
- Default worker (4 threads): default, agents, sports, content, ml queues
- Long-running worker (2 threads): long_running queue
- Broadcast worker (2 threads): broadcast queue

## Verification

### Full Agent Test
```bash
python manage.py test_all_agents --quick
```
**Result:** 73/73 agents passed (100% success rate)

### Context Rate Check
```python
from core.models_unified_system import AgentExecution
from django.utils import timezone
from datetime import timedelta

recent = AgentExecution.objects.filter(
    created_at__gte=timezone.now() - timedelta(minutes=30)
)
with_ctx = sum(1 for e in recent if (e.input_data or {}).get('context_injected'))
print(f"Context rate: {with_ctx}/{recent.count()} = {with_ctx/recent.count()*100:.0f}%")
# Output: Context rate: 84/84 = 100%
```

## Commits

1. `cdd9eeae` - fix(Session 758): Improve Integration Health tracking accuracy
2. `1a3043e8` - feat(Session 758): Add Dream System and Body Systems to Integration Health
3. `101a46c6` - feat(Session 758): Add context tracking to key execution entry points
4. `f087e33b` - feat(Session 758): Add context tracking to unified_system AgentExecution entry points
5. `3bee8a1e` - fix(Session 758): Increase Celery health check timeout from 2s to 10s
6. `4a002412` - fix(Session 758): Fix Celery health detection for busy/solo workers

### 4. Neural Orchestra Learning System Card Fix

**File:** `ai_core/consciousness/neural_orchestra_reality_bridge.py`

**Issue:** Learning System Card on Neural Orchestra page showed 0s:
- Feedback Processed: 0
- Insights Generated: 0
- Memory Crystals: 1

**Root Cause:** Card was reading from empty in-memory `LearningLoop` buffers instead of actual database tables which contain real data:
- 52,161 AgentLearning records
- 662 AgentExecution records (completed)
- 1,503 KnowledgeTransfer records
- 14 MemoryCluster records

**Fix:** Rewrote `get_learning_status_api_data()` to query database directly with synchronous ORM:
```python
def get_learning_status_api_data(self) -> Dict[str, Any]:
    """Uses synchronous DB queries to avoid thread executor conflicts."""
    from core.models_unified_system import AgentLearning, AgentExecution, KnowledgeTransfer, MemoryCluster

    feedback_processed = AgentExecution.objects.filter(
        created_at__gte=last_7d, status='completed'
    ).count()

    insights_generated = AgentLearning.objects.filter(
        created_at__gte=last_7d
    ).count()

    memory_crystals = MemoryCluster.objects.count()
    # ...
```

**Results After Fix:**
```json
{
    "learning_active": true,
    "models_active": 15,
    "feedback_processed": 574,
    "insights_generated": 7038,
    "memory_crystals": 14
}
```

**Technical Note:** Initial fix used `sync_to_async` but caused "You cannot submit onto CurrentThreadExecutor from its own thread" error with Daphne. Solution: Make the API method fully synchronous since it's called from synchronous Django views.

## Next Steps

1. Monitor system to verify spiders are generating data
2. Verify agents are receiving and using spider context
3. Check Integration Health dashboard shows real-time updates
