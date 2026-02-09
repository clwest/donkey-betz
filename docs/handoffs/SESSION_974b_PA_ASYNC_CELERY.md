# Session 974b — PA Chat Async Processing (Celery + Polling)

**Date:** February 9, 2026
**Previous Session:** 974 (PA Conversation History)
**Branch:** `main` (direct push)

---

## Problem

After deploying the PA Conversation History feature (PR #1011), complex PA queries on Railway timeout because GPT-5.1 takes 117-172 seconds to respond, exceeding Railway's ~30s proxy timeout. Short messages like "hi" work fine — only LLM-heavy queries fail.

## Solution

Offloaded PA processing to a Celery task. The HTTP endpoint now returns a `task_id` instantly, and the frontend polls a new status endpoint every 2 seconds until the result is ready. This follows the proven blog v2 deliberation pattern (`generate_v2_blog_api` in `views_research_demo.py`).

---

## Changes

### Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | Added `process_pa_chat_task` Celery task (5 min time limit) |
| `core/views_personal_assistant.py` | `unified_pa_chat` now dispatches Celery task; added `pa_chat_status` polling endpoint |
| `core/urls.py` | Added `api/pa/chat/status/<task_id>/` URL pattern |
| `frontend/src/lib/api.ts` | Added `PAChatAsyncResponse`, `PAChatStatusResponse` interfaces; added `paChatStatus()` method; changed `paChat` return type |
| `frontend/src/components/GlobalPADock.tsx` | Async dispatch + 2s polling with `isPolling` state |
| `frontend/src/pages/CommandCenterPage.tsx` | Same async polling pattern |
| `frontend/src/pages/AssistantPage.tsx` | Same async polling pattern |

No new files, no migrations.

### Backend

#### 1. `process_pa_chat_task` (core/tasks.py)

```python
@shared_task(bind=True, time_limit=300, soft_time_limit=280)
def process_pa_chat_task(self, user_id, message, context=None, generate_audio=False, conversation_id=None)
```

- Accepts `user_id` (int) — re-fetches User in worker (Celery JSON serialization)
- Runs `UnifiedPAEntrypoint.process_message()` via `async_to_sync`
- Persists to `ChatConversation` (moved from view into task)
- Returns full response dict stored in Redis result backend
- 5 min hard kill, 4:40 graceful soft limit

#### 2. `unified_pa_chat` (core/views_personal_assistant.py)

Changed from synchronous processing to:
```python
task = process_pa_chat_task.delay(user_id=request.user.id, message=message, ...)
return Response({'success': True, 'task_id': str(task.id), 'status': 'processing'})
```

#### 3. `pa_chat_status` (core/views_personal_assistant.py)

New polling endpoint:
- `GET /api/pa/chat/status/<task_id>/`
- Returns `{status: 'processing'}`, `{status: 'completed', content: ..., tool_runs: ...}`, or `{status: 'failed', error: ...}`
- Uses `AsyncResult(task_id, app=current_app)`

### Frontend

All three PA chat consumers (GlobalPADock, CommandCenterPage, AssistantPage) updated:

1. `chatMutation.onSuccess` receives `task_id` and starts `setInterval` polling every 2s
2. `isPolling` state tracks whether we're waiting for Celery result
3. `isBusy = chatMutation.isPending || isPolling` replaces all `chatMutation.isPending` references
4. "Thinking..." indicator shows during both dispatch and polling phases
5. Input disabled during both phases
6. `pollRef` cleaned up on component unmount via `useEffect` return

---

## Key Design Decisions

1. **Follow existing blog v2 pattern** — proven in production
2. **Persistence in the Celery task** — ChatConversation rows created after LLM completes, not in the view
3. **2-second polling interval** — balances responsiveness vs request volume (worst case: 172s = ~86 polls)
4. **5-minute hard time limit** — prevents zombie tasks
5. **`user_id` not `user` in task args** — Celery JSON serializes primitives only

---

## Verification

- Python syntax: `py_compile` passes for both `tasks.py` and `views_personal_assistant.py`
- TypeScript: zero new errors (all pre-existing)
- Railway test needed: Send PA message → verify instant response → polling picks up completed result
