# Session 789: Railway Full Deployment Complete

**Date:** January 22, 2026
**Focus:** Complete Railway deployment with all 5 services + fixes
**Status:** ALL PHASES COMPLETE - Platform fully operational

---

## Overview

Completed the full production deployment of Donkey Betz AI Intelligence Platform to Railway. All 5 services are running, all Celery workers are processing tasks, and agents are actively executing conversations.

---

## Production URLs

- **Custom Domain:** `https://donkeybetz.com`
- **Railway URL:** `https://donkey-betz-platform-production.up.railway.app/`

---

## Architecture (All Phases Complete)

```
Railway Project: Donkey Betz
├── PostgreSQL (pgvector plugin)
│   └── DATABASE_URL → ${{pgvector.DATABASE_PRIVATE_URL}}
├── Redis (plugin)
│   └── REDIS_URL → ${{Redis.REDIS_URL}}
├── donkey-betz-platform (Web - Daphne ASGI)
│   └── Start: daphne -b 0.0.0.0 -p $PORT core.asgi:application
├── celery-default
│   └── Start: celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml
├── celery-long-running
│   └── Start: celery -A core worker -l info --pool=threads -c 2 -Q long_running
├── celery-broadcast
│   └── Start: celery -A core worker -l info --pool=threads -c 2 -Q broadcast
└── celery-beat (Scheduler)
    └── Start: celery -A core beat -l info
```

---

## Service Status (All Running)

| Service | Status | Notes |
|---------|--------|-------|
| PostgreSQL | ✅ Running | pgvector enabled |
| Redis | ✅ Running | Used for cache, sessions, Celery broker |
| donkey-betz-platform (web) | ✅ Running | Daphne ASGI server |
| celery-default | ✅ Running | Processing default, agents, sports, content, ml queues |
| celery-long-running | ✅ Running | Processing long_running queue |
| celery-broadcast | ✅ Running | Processing broadcast queue |
| celery-beat | ✅ Running | Scheduler for 238 periodic tasks |

---

## Session 789 Fixes

### Issue: Muscular System "Paralyzed"

**Symptom:** `/api/body/muscular/` returning 500 error with "Connection refused to localhost:6379"

**Root Cause:** `ai_core/agents/execution_tracker.py` was using `REDIS_HOST`/`REDIS_PORT` settings (which don't exist in production), falling back to localhost:6379

**Fix:** Modified `execution_tracker.py` to use `REDIS_URL` environment variable:

```python
# OLD (broken):
def __init__(self):
    self.redis_client = redis.Redis(
        host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
        port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
        db=0,
        decode_responses=True
    )

# NEW (fixed):
def __init__(self):
    import os
    redis_url = os.environ.get('REDIS_URL', getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'))
    self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
```

**File Modified:** `ai_core/agents/execution_tracker.py`

---

## Celery Worker Configuration

### Key Insight: Start Command Override

The `entrypoint.sh` file uses `PROCESS_TYPE` environment variable to determine the start command. However, for Celery workers, it's more reliable to set an explicit **Start Command** in Railway dashboard:

| Service | Start Command |
|---------|---------------|
| donkey-betz-platform | `daphne -b 0.0.0.0 -p $PORT core.asgi:application` |
| celery-default | `celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml` |
| celery-long-running | `celery -A core worker -l info --pool=threads -c 2 -Q long_running` |
| celery-broadcast | `celery -A core worker -l info --pool=threads -c 2 -Q broadcast` |
| celery-beat | `celery -A core beat -l info` |

### Verification

Workers show "ready" message in logs:
```
[INFO/MainProcess] celery@77586738312f ready.
```

---

## Platform Activity Verified

After deployment, the platform showed active AI operations:

| Metric | Value |
|--------|-------|
| Agent Conversations | 6+ agents participating (image, video, audio, 3d, etc.) |
| Messages Generated | 17 in single conversation |
| Dreams Generated | 66 today |
| Learning System | 141 agents registered |

---

## Environment Variables

All services share the same environment variables (copy from web service):

### Required
```bash
SECRET_KEY=<64-char-random-string>
DEBUG=False
ALLOWED_HOSTS=donkeybetz.com,www.donkeybetz.com,.railway.app,.up.railway.app
ENVIRONMENT=production
DJANGO_SETTINGS_MODULE=core.settings

DATABASE_URL=postgres://...  # From pgvector plugin
REDIS_URL=redis://...        # From Redis plugin
CELERY_BROKER_URL=redis://...
CELERY_RESULT_BACKEND=redis://...
```

### AI APIs
```bash
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...
GROQ_API_KEY=...
TOGETHER_AI_API_KEY=...
STABILITY_API_KEY=...
ELEVENLABS_API_KEY=...
# ... (50+ API keys total)
```

---

## Deployment Phases Complete

| Phase | Services | Status |
|-------|----------|--------|
| **Phase 1** | Web + PostgreSQL + Redis | ✅ Complete |
| **Phase 2** | + celery-default | ✅ Complete |
| **Phase 3** | + celery-long-running, celery-broadcast, celery-beat | ✅ Complete |
| **Phase 4** | Monitoring + optimization | In progress |

---

## What's Working

- ✅ User authentication and login
- ✅ Dashboard with real-time data
- ✅ All 9 Body Systems (HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN)
- ✅ Agent registry (141 agents)
- ✅ Advisor network (25 advisors)
- ✅ WebSocket real-time updates
- ✅ Agent conversations and task execution
- ✅ Dream generation
- ✅ Spider data collection
- ✅ Scheduled tasks (238 tasks via Celery Beat)
- ✅ Custom domain (donkeybetz.com)

---

## Cost Estimate (Current)

| Service | Monthly |
|---------|---------|
| PostgreSQL (pgvector) | ~$10-15 |
| Redis | ~$10-15 |
| Web Service | ~$15-20 |
| celery-default | ~$15-20 |
| celery-long-running | ~$10-15 |
| celery-broadcast | ~$10-15 |
| celery-beat | ~$5-10 |
| **Total** | ~$75-110 |

Plus API costs (variable):
- OpenAI/Anthropic: $50-200+/month
- Other APIs: $10-50/month

---

## Troubleshooting Notes

### 1. Worker stuck at "Connected to redis" (no "ready")
- **Cause:** PROCESS_TYPE set incorrectly (e.g., "web" instead of "celery-default")
- **Fix:** Set explicit Start Command in Railway dashboard

### 2. Queued deployments flooding
- **Cause:** Each variable set via CLI triggers a new deployment
- **Fix:** Set all variables at once in Raw Editor mode

### 3. Redis connection refused (localhost:6379)
- **Cause:** Code using hardcoded localhost instead of REDIS_URL
- **Fix:** Use `REDIS_URL` environment variable everywhere

### 4. entrypoint.sh not executing as expected
- **Cause:** Railway may not always run the entrypoint
- **Fix:** Set explicit Start Command in Railway dashboard

---

## Files Modified This Session

| File | Change |
|------|--------|
| `ai_core/agents/execution_tracker.py` | Use REDIS_URL instead of REDIS_HOST/REDIS_PORT |

---

## Related Documentation

- [Session 788 Handoff](SESSION_788_RAILWAY_DEPLOYMENT_COMPLETE.md) - Phase 1 & 2 deployment
- [Session 787 Handoff](SESSION_787_RAILWAY_DEPLOYMENT.md) - Initial deployment attempt
- [Railway Deployment Guide](../guides/RAILWAY_DEPLOYMENT.md) - Full deployment guide
- [Architecture](../ARCHITECTURE.md) - System architecture

---

## Next Steps

1. ✅ All services deployed and running
2. Monitor for any production issues
3. Set up Sentry for error tracking (Phase 4)
4. Configure uptime monitoring (Phase 4)
5. Optimize resource allocation based on usage
