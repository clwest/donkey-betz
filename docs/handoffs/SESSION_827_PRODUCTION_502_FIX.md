---
originating_session: 827
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 827: Production 502 Fix

**Date:** January 25, 2026
**Status:** ✅ COMPLETE
**Issue:** Production 502 timeout on `/api/agent-conversations/trigger/`

---

## Summary

Fixed production 502 timeout errors on agent conversation endpoints by implementing async Celery task execution. The endpoint now returns immediately with a task_id, and clients can poll for completion.

---

## Root Cause Analysis

### The Problem

When calling `/api/agent-conversations/trigger/` on Railway production:

```json
{"status":"error","code":502,"message":"Application failed to respond"}
```

### Investigation Findings

1. **Railway logs** showed conversations taking ~283 seconds (4-5 minutes)
2. **Procfile** showed Daphne with `--http-timeout 120` (2 minutes)
3. **Root cause**: `trigger_agent_conversation` was **synchronous**
   - It called `async_to_sync(consumer.generate_live_conversation)` inline
   - This blocked the request for the entire conversation duration
   - Railway's gateway timeout (~30-60s) was exceeded

### Code Before (Problematic)

```python
# core/views_agent_learning.py - Line 709
def trigger_agent_conversation(request):
    # ...
    consumer = AgentConversationConsumer()
    result = async_to_sync(consumer.generate_live_conversation)(  # BLOCKS FOR 4-5 MINUTES!
        topic=topic,
        # ...
    )
    return JsonResponse({'success': True, 'result': result})
```

---

## Solution Implemented

### 1. New Celery Task

**File:** `core/tasks.py`

```python
@shared_task(bind=True, max_retries=1, default_retry_delay=60)
def run_triggered_conversation(
    self,
    topic: str,
    conversation_type: str = 'general',
    objective: str = None,
    success_criteria: list = None,
    auto_select_agents: bool = False,
    participant_ids: list = None
):
    """
    Session 827: Run a triggered agent conversation asynchronously.
    """
    from core.agent_conversation_consumer import AgentConversationConsumer
    import asyncio

    consumer = AgentConversationConsumer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(
            consumer.generate_live_conversation(
                topic=topic,
                conversation_type=conversation_type,
                objective=objective,
                success_criteria=success_criteria or [],
                auto_select_agents=auto_select_agents
            )
        )
    finally:
        loop.close()

    return {
        'success': True,
        'conversation_id': result.get('conversation_id'),
        'participants': result.get('participants', []),
        'quality_score': result.get('quality_score', 0),
        'result': result
    }
```

### 2. Updated Endpoint

**File:** `core/views_agent_learning.py`

```python
def trigger_agent_conversation(request):
    # ...

    # Session 827: Check if sync execution requested (for local testing)
    run_sync = body.get('sync', False)

    if run_sync:
        # Synchronous execution (original behavior, for local testing)
        # ... original code ...
        return JsonResponse({'success': True, 'result': result})

    # Session 827: Async execution via Celery (default for production)
    from core.tasks import run_triggered_conversation

    task_result = run_triggered_conversation.delay(
        topic=topic,
        conversation_type=conversation_type,
        objective=objective,
        success_criteria=success_criteria,
        auto_select_agents=auto_select_agents,
        participant_ids=participant_ids
    )

    return JsonResponse({
        'success': True,
        'status': 'queued',
        'task_id': task_result.id,
        'poll_url': f'/api/agent-conversations/task/{task_result.id}/'
    })
```

### 3. New Task Status Endpoint

**File:** `core/views_agent_learning.py`

```python
@csrf_exempt
@require_http_methods(["GET"])
def get_conversation_task_status(request, task_id):
    """
    GET /api/agent-conversations/task/<task_id>/
    """
    from celery.result import AsyncResult
    from celery import current_app

    result = AsyncResult(task_id, app=current_app)

    if result.state == 'PENDING':
        return JsonResponse({'state': 'PENDING', 'message': 'Waiting to start...'})
    elif result.state == 'SUCCESS':
        return JsonResponse({'state': 'SUCCESS', 'result': result.result})
    elif result.state == 'FAILURE':
        return JsonResponse({'state': 'FAILURE', 'error': str(result.info)})
    # ...
```

### 4. URL Pattern

**File:** `core/urls.py`

```python
path('api/agent-conversations/task/<str:task_id>/', get_conversation_task_status, name='conversation-task-status'),
```

---

## API Changes

### Before (Synchronous - Caused 502)

```bash
POST /api/agent-conversations/trigger/
# Blocks for 4-5 minutes, times out on Railway
```

### After (Async - Fixed)

```bash
# Step 1: Trigger conversation (returns immediately)
POST /api/agent-conversations/trigger/
{
    "topic": "Best practices for logo design",
    "conversation_type": "analytical",
    "objective": "Determine the best approach",
    "success_criteria": ["Identify at least 3 options"]
}

# Response (immediate):
{
    "success": true,
    "status": "queued",
    "task_id": "abc123-def456-...",
    "poll_url": "/api/agent-conversations/task/abc123-def456-.../"
}

# Step 2: Poll for completion
GET /api/agent-conversations/task/abc123-def456-.../

# Response when pending:
{ "state": "PENDING", "message": "Waiting to start..." }

# Response when complete:
{
    "state": "SUCCESS",
    "result": {
        "success": true,
        "conversation_id": "...",
        "participants": ["Agent1", "Agent2"],
        "quality_score": 92
    }
}
```

### Backward Compatibility

For local testing where sync execution is desired:

```bash
POST /api/agent-conversations/trigger/
{ "topic": "...", "sync": true }
# Runs synchronously (original behavior)
```

---

## Files Modified

| File | Lines Changed | Description |
|------|---------------|-------------|
| `core/tasks.py` | +95 | Added `run_triggered_conversation` Celery task |
| `core/views_agent_learning.py` | +85 | Made trigger async, added status endpoint |
| `core/urls.py` | +2 | Added import and URL pattern |
| `00-START-NEXT-SESSION.md` | rewrite | Updated for Session 828 |

---

## Testing

### Local Testing

```bash
# 1. Start services
make start && make celery

# 2. Test async trigger
curl -X POST http://localhost:8000/api/agent-conversations/trigger/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test topic", "conversation_type": "analytical"}'

# 3. Note the task_id from response

# 4. Poll for completion
curl http://localhost:8000/api/agent-conversations/task/<task_id>/
```

### Production Testing

After deploying to Railway:

```bash
# Should return immediately with task_id
curl -X POST https://donkey-betz-platform-production.up.railway.app/api/agent-conversations/trigger/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test async", "conversation_type": "general"}'
```

---

## Key Learnings

1. **Long-running operations must be async** - Never block HTTP requests for operations that take more than ~30 seconds
2. **Railway has gateway timeouts** - Default ~30-60 seconds, Daphne's 120s timeout doesn't help if gateway times out first
3. **Celery is ideal for this** - Already configured, just needed to add the task
4. **Polling is simple but effective** - More complex alternatives (WebSocket progress) can be added later if needed

---

## Future Improvements

1. **WebSocket progress updates** - Instead of polling, push updates via existing WebSocket infrastructure
2. **Frontend integration** - Update UI to show progress indicator while conversation generates
3. **Task result caching** - Store completed results in DB to avoid Celery result expiration issues
