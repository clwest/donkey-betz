---
originating_session: 889
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 889: Intel Tab + Podcast Tab Fixes

**Date:** January 31, 2026
**Status:** Complete

---

## Part 1: Intel Tab "Recent Thoughts" Fix

### Problem
The "Recent Thoughts" section on the Intelligence Tab showed "..." instead of actual thought content.

### Root Cause
API returns fields with different names than the frontend expected:
- API: `context_summary`, `cycle_type`, `started_at`
- Frontend expected: `content`, `thought_type`, `created_at`

### Fix
Added field mapping in `IntelligenceTab.tsx`:
```typescript
const mappedThoughts = (data.thoughts || data.results || []).map((t: any) => ({
  ...t,
  content: t.content || t.context_summary || t.reflection || '',
  thought_type: t.thought_type || t.cycle_type || 'scheduled',
  context: t.context || t.reflection || '',
  agent_name: t.agent_name || 'ThinkingAgent',
  created_at: t.created_at || t.started_at || new Date().toISOString(),
}))
```

### File Modified
- `frontend/src/pages/workspace/tabs/IntelligenceTab.tsx`

---

## Part 2: Podcast Tab Token Auth Fix

### Problem
Podcasts weren't displaying in Content Tab despite being created successfully:
- `POST /api/podcasts/create/` worked with Token auth
- `GET /api/podcasts/list/` returned 0 episodes
- `GET /api/podcasts/stats/` returned empty stats

### Root Cause
1. `/api/podcasts/` is in `PUBLIC_PATHS` in auth middleware
2. Middleware skips authentication for public paths
3. Endpoints returned empty for anonymous users (no session auth)
4. Token auth wasn't being checked

### Fix (PR #625)
Added manual Token auth check to both endpoints:

```python
# Session 887: Manual auth check to support Token auth
# /api/podcasts/ is in PUBLIC_PATHS so middleware skips auth
from rest_framework.authtoken.models import Token

if not request.user.is_authenticated:
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token_key = auth_header.split(' ', 1)[1]
        try:
            token = Token.objects.select_related('user').get(key=token_key)
            if token.user.is_active:
                request.user = token.user
        except Token.DoesNotExist:
            pass
```

### Files Modified
- `core/views_podcast.py` - Added Token auth to `podcast_list` and `podcast_stats`

---

## Part 3: Auto-Generate Podcast Task

### Feature
Added Celery Beat task to automatically generate podcast episode scripts from trending topics.

### Implementation
```python
@shared_task
def auto_generate_podcast_episode():
    """
    Auto-generate podcast episodes from trending topics.
    Runs every 12 hours. Creates a new podcast episode script based on:
    1. Recent spider intelligence trends
    2. ThinkingAgent insights
    3. Popular boardroom decisions
    """
    # ... gets system user, checks rate limit (max 2 per 6 hours)
    # ... gets topic from ThinkingCycleRecord, AgentDecisionSummary, or fallback
    # ... creates PodcastEpisode and queues generate_podcast_episode task
```

### Schedule
```python
'auto-generate-podcast-episode': {
    'task': 'core.tasks.auto_generate_podcast_episode',
    'schedule': crontab(minute=15, hour='*/12'),  # Every 12 hours at :15
},
```

### Files Modified
- `core/tasks.py` - Added `auto_generate_podcast_episode` task
- `core/settings.py` - Added Celery Beat schedule

---

## PRs Created

| PR | Description |
|----|-------------|
| #625 | Add Token auth to podcast_list and podcast_stats endpoints |

---

## Token Auth Pattern Reference

For endpoints under paths in `PUBLIC_PATHS` (like `/api/boardroom/`, `/api/podcasts/`), the auth middleware skips authentication. To support Token auth on these endpoints:

1. Remove `@login_required` decorator (only works with session auth)
2. Add `@csrf_exempt` decorator (Token auth doesn't need CSRF)
3. Add manual Token auth check at start of view:

```python
from rest_framework.authtoken.models import Token

if not request.user.is_authenticated:
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token_key = auth_header.split(' ', 1)[1]
        try:
            token = Token.objects.select_related('user').get(key=token_key)
            if token.user.is_active:
                request.user = token.user
        except Token.DoesNotExist:
            pass
```

---

## Endpoints Fixed with Token Auth

| Session | Endpoint | PR |
|---------|----------|-----|
| 887 | `/api/boardroom/decisions/{id}/promote/` | #618, #619 |
| 887 | `/api/boardroom/decisions/{id}/reject/` | #618, #619 |
| 887 | `/api/podcasts/create/` | Session fix |
| 889 | `/api/podcasts/list/` | #625 |
| 889 | `/api/podcasts/stats/` | #625 |

---

**Intel Tab thoughts display fixed. Podcast Tab now shows created podcasts. Auto-podcast generation active. System is healthy.**
