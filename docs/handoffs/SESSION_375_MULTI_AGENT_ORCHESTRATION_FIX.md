# Session 375: Multi-Agent Orchestration Fix

## Summary
Fixed the Multi-Agent Orchestration feature which was failing with `'NoneType' object has no attribute 'get'` error when users tried to "Create a complete logo package" from the Memory → Collaboration tab.

## Problem
User reported error when clicking "Orchestrate" button in the Collective Intelligence UI:
```
'NoneType' object has no attribute 'get'
```

## Root Causes Found

### Bug 1: NoneType Error on performance_metrics
**Location:** `core/services/collective_intelligence.py:944-946`

**Code Before:**
```python
metrics = agent.get('performance_metrics', {})
score += metrics.get('success_rate', 0.5) * 10
```

**Problem:** When `performance_metrics` key exists with value `None`, `agent.get('performance_metrics', {})` returns `None` (not `{}`). Calling `.get()` on `None` fails.

**Fix:**
```python
metrics = agent.get('performance_metrics') or {}
score += metrics.get('success_rate', 0.5) * 10
```

### Bug 2: AnonymousUser Assignment Error
**Error Message:**
```
Cannot assign "<django.contrib.auth.models.AnonymousUser object>": "CollaborationSession.user" must be a "UnifiedUser" instance.
```

**Location:** `core/services/collective_intelligence.py:150-153`

**Code Before:**
```python
def __init__(self, user=None):
    self.user = user
```

**Problem:** When endpoint is called without authentication, `request.user` is `AnonymousUser`. This was passed to `CollaborationSession.objects.create(user=self.user)`.

**Fix:**
```python
def __init__(self, user=None):
    # Only store user if it's a real authenticated user (not AnonymousUser)
    from django.contrib.auth.models import AnonymousUser
    self.user = user if user and not isinstance(user, AnonymousUser) else None
```

## Files Modified
- `core/services/collective_intelligence.py`
  - Line 150-153: Filter out AnonymousUser in `__init__`
  - Line 944-945: Handle None metrics with `or {}` pattern

## Testing

### Before Fix
```bash
curl -X POST "http://localhost:8000/api/collective/orchestrate/" \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Create a complete logo package"}'
```
Result: `{"error": "'NoneType' object has no attribute 'get'"}`

### After Fix
```bash
curl -X POST "http://localhost:8000/api/collective/orchestrate/" \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Create a complete logo package"}'
```
Result:
```json
{
    "orchestration_id": "c11a1b7f-cb40-4486-84d2-7c62aa67f65e",
    "session_id": "83deacbe-1786-4746-b97f-f0624bf87cf0",
    "status": "initiated",
    "selected_agents": [
        "CreativeDirectorAgent",
        "LogoAgent",
        "WorkflowCoordinatorAgent",
        "image-generation-agent",
        "AudioAgent"
    ],
    "agent_count": 5,
    "task_description": "Create a complete logo package",
    "timeout_seconds": 300
}
```

## Key Learnings

### Python Default Value Gotcha
When using `dict.get(key, default)`:
- If key doesn't exist → returns `default`
- If key exists with value `None` → returns `None` (NOT `default`)

**Safe pattern:** `dict.get(key) or default_value`

### Django AnonymousUser
When using `@permission_classes([AllowAny])`:
- `request.user` is `AnonymousUser` for unauthenticated requests
- Must check `isinstance(user, AnonymousUser)` before assigning to FK fields

## Related Sessions
- Session 374: Collective Intelligence Search Fix
- Session 373: Knowledge Gap Resolution System
