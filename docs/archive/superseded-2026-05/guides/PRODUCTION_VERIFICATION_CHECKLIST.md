# Production Verification Checklist

**Last Updated:** January 22, 2026
**For:** Railway Deployment Verification

Use this checklist to verify your Railway deployment is fully operational.

---

## Quick Health Check

```bash
# 1. Basic health ping
curl https://donkeybetz.com/health/ping/
# Expected: {"ok": true}

# 2. Check Railway service status
railway status
```

---

## Service Verification

### 1. Web Service (Daphne)
- [ ] Health ping returns `{"ok": true}`
- [ ] Can access https://donkeybetz.com
- [ ] Can login to Django admin
- [ ] WebSocket connections work (no console errors)

### 2. PostgreSQL
- [ ] Database migrations applied
- [ ] Can query data (login to admin and check models)
- [ ] pgvector extension enabled

### 3. Redis
- [ ] Cache working (pages load quickly on repeat visits)
- [ ] Sessions working (stay logged in)
- [ ] Celery broker connected (check worker logs)

### 4. Celery Workers

**Check each worker's logs in Railway dashboard for "ready" message:**

| Service | Look For | Status |
|---------|----------|--------|
| celery-default | `celery@... ready.` | [ ] Running |
| celery-long-running | `celery@... ready.` | [ ] Running |
| celery-broadcast | `celery@... ready.` | [ ] Running |
| celery-beat | `Scheduler: ...` | [ ] Running |

---

## Integration Health Components

The Integration Health page checks 7 components. Here's what makes each healthy:

### 1. Spider Data
- **Healthy:** 50+ records in last 24h
- **Warning:** 1-49 records in 24h
- **Degraded:** 0 records in 24h

**To fix:** Wait for `run_all_spiders` Celery task (runs hourly via Beat)

### 2. Learning Patterns
- **Healthy:** 100+ patterns in last 7 days
- **Warning:** 1-99 patterns
- **Degraded:** 0 patterns

**To fix:** Agent executions automatically create learning patterns

### 3. Advisor System
- **Always healthy** (static configuration)

### 4. Feedback Loop
- **Healthy:** 80%+ success rate
- **Warning:** 50-79% success rate
- **Degraded:** <50% success rate

**To fix:** Check agent execution errors

### 5. Sci-Fi Context
- **Healthy:** Active moods OR evolution records
- **Warning:** Neither

**To fix:** Agent moods update automatically; evolution happens over time

### 6. Dream System
- **Healthy:** 10+ dreams in last 7 days
- **Warning:** 1-9 dreams
- **Degraded:** 0 dreams

**To fix:** Wait for `generate_agent_dreams` Celery task (runs every 90 minutes)

### 7. Body Systems
- **Healthy:** All 9 body systems operational
- **Degraded:** Some systems down
- **Error:** Critical systems down

**To fix:** Check individual body system endpoints

---

## Trigger Manual Tasks

If systems show degraded, you can manually trigger tasks:

```bash
# Run spiders manually (triggers data collection)
railway run python manage.py shell -c "
from core.tasks import run_all_spiders
run_all_spiders.delay()
print('Spider task queued!')
"

# Generate dreams manually
railway run python manage.py shell -c "
from core.tasks import generate_agent_dreams
generate_agent_dreams.delay()
print('Dream generation queued!')
"

# Check Celery Beat scheduled tasks
railway run python manage.py shell -c "
from core.celery import app
beat_schedule = app.conf.beat_schedule
print(f'Scheduled tasks: {len(beat_schedule)}')
for name in sorted(beat_schedule.keys())[:20]:
    print(f'  - {name}')
"
```

---

## Check Specific Pages

### Pages That Need Agent Execution Data
These pages require agents to have run recently:

| Page | Data Source | Expected After |
|------|-------------|----------------|
| Dashboard | AgentExecution | Few hours |
| Human Interface | HumanAttentionItem | Agent creates items |
| Neural Orchestra | AgentExecution, Learning | Few hours |
| Memory Palace | AgentMemory | Agent executions |

### Pages That Need Spider Data
These pages need spider runs:

| Page | Data Source | Expected After |
|------|-------------|----------------|
| Spider Integration | SpiderData | Spider runs (~1 hour) |
| Intelligence | SpiderData, Opportunities | Spider + analysis |

### Pages That Need Celery Beat
These pages need scheduled tasks:

| Page | Task | Schedule |
|------|------|----------|
| Dreams | `generate_agent_dreams` | Every 90 min |
| Learning | `run_knowledge_transfer` | Every 30 min |
| Body Health | Various pulse tasks | Every 60-90 sec |

---

## Common Issues

### 1. "Degraded" Integration Health
**Cause:** Celery workers just started, no data yet
**Fix:** Wait 1-2 hours for scheduled tasks to run

### 2. Pages Show No Data
**Cause:** No agent executions or spider runs yet
**Fix:** Either wait for scheduled tasks or trigger manually

### 3. WebSocket Errors in Console
**Cause:** Frontend trying to connect before backend ready
**Fix:** Refresh page after services fully start

### 4. Body System Shows "Paralyzed" or Error
**Cause:** Redis connection issue or missing data
**Fix:** Check Redis connection, wait for data

### 5. Spider Embedding Coverage 0%
**Cause:** Backfill task hasn't run yet
**Fix:** Wait for `backfill_spider_embeddings` (runs every 10 min)

---

## Verification Timeline

After a fresh deployment, expect this timeline:

| Time | What Should Be Working |
|------|------------------------|
| 0-5 min | Web UI, login, static pages |
| 5-15 min | Celery workers connected |
| 15-30 min | First scheduled tasks run |
| 30-60 min | Body systems showing data |
| 1-2 hours | Spider data appearing |
| 2-4 hours | Dreams, learning patterns |
| 6-12 hours | Full Integration Health "Healthy" |

---

## Production URLs

- **Main Site:** https://donkeybetz.com
- **Railway URL:** https://donkey-betz-platform-production.up.railway.app
- **Health Ping:** /health/ping/
- **Admin:** /admin/
- **AI Studio:** /ai-studio/

---

## Railway Commands

```bash
# Check service logs
railway logs -s donkey-betz-platform
railway logs -s celery-default
railway logs -s celery-beat

# Run Django management commands
railway run python manage.py shell
railway run python manage.py migrate

# Check environment
railway variables
```
