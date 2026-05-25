---
originating_session: 885
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 885: Celery Content Pipeline & Operations Tab Fix

**Date:** January 30-31, 2026
**Status:** Complete

## Problems Found & Solved

### 1. Content Generation Not Working (Blogs, Podcasts, etc.)
**Problem:** No new blogs generated in 2+ days. Content tasks were stuck behind long-running conversation tasks.

**Root Cause:**
- `celery-long-running` worker (2 concurrency) was fully occupied by conversation tasks (6-10 min each)
- Content tasks queued behind them indefinitely

**Solution (PR #607):** Created dedicated `celery-content` worker with 4 concurrency slots.

### 2. Task Routing Issues
**Problem:** LLM/content tasks going to wrong queues, blocking other work.

**Solutions:**
- PR #605: Route LLM tasks to `long_running` queue
- PR #606: Rename `celery-default` to `celery-worker` to match Railway service names
- PR #607: Route all content tasks to dedicated `content` queue

### 3. Operations Tab Not Updating
**Problem:** Operations tab showed no new entries since January 29th.

**Root Causes:**
1. Workspace-writing tasks (`agent_daily_summary`, `agent_research_to_workspace`, etc.) were defined but NOT scheduled in `CELERY_BEAT_SCHEDULE`
2. Tasks were looking for superuser's workspace, but `setup_codebase_workspace` creates workspace for 'system' user

**Solution (PR #608):**
1. Added `_get_workspace_for_skin_layer()` helper that finds workspaces in order:
   - Codebase workspace (type='codebase')
   - Any active workspace with `allow_file_write=True`
   - Superuser's workspace (fallback)
2. Scheduled all workspace-writing tasks
3. Added 8 financial/sports agents to `AGENT_WORKSPACE_REGISTRY`

### 4. Stuck Initiatives Auto-Recovery
**Problem:** Initiatives getting stuck at Stage 1 with no progress.

**Solution (PR #604):** Added `auto_kickstart_stuck_initiatives` scheduled task that runs every 10 minutes.

---

## PRs in This Session

| PR | Description |
|----|-------------|
| #604 | Auto-kickstart stuck initiatives every 10 minutes |
| #605 | Route LLM tasks to long_running queue |
| #606 | Rename celery-default to celery-worker in Procfile |
| #607 | Add dedicated celery-content worker for content generation |
| #608 | Fix Operations tab - schedule workspace-writing tasks |

---

## Celery Architecture (After Session 885)

### Procfile Workers
```
celery-worker: -Q default,agents,sports,ml (4 concurrency)
celery-content: -Q content (4 concurrency)
celery-long-running: -Q long_running (2 concurrency)
celery-broadcast: -Q broadcast (2 concurrency)
celery-beat: scheduler
```

### Task Routing (CELERY_TASK_ROUTES)
```python
# Content generation - dedicated worker
'core.tasks.generate_self_blog_task': {'queue': 'content'},
'core.tasks.execute_initiative_stage_task': {'queue': 'content'},
'core.tasks.advance_initiative_pipeline': {'queue': 'content'},
'core.tasks.auto_kickstart_stuck_initiatives': {'queue': 'content'},
'autonomous_studio.run_main_loop': {'queue': 'content'},
'core.tasks.generate_podcast_task': {'queue': 'content'},
'core.tasks.generate_image_task': {'queue': 'content'},
'core.tasks.generate_video_task': {'queue': 'content'},

# Workspace-writing tasks (Operations tab)
'core.tasks.agent_daily_summary': {'queue': 'content'},
'core.tasks.agent_workspace_status_report': {'queue': 'content'},
'core.tasks.agent_research_to_workspace': {'queue': 'content'},
'core.tasks.agent_content_to_workspace': {'queue': 'content'},
'core.tasks.universal_agent_workspace_output': {'queue': 'content'},
'core.tasks.agent_category_rotation': {'queue': 'content'},

# Long-running tasks
'intelligence.*': {'queue': 'long_running'},
'core.tasks.run_spider_network': {'queue': 'long_running'},
'core.tasks.generate_agent_dreams': {'queue': 'long_running'},
# ... etc
```

### New Scheduled Tasks (CELERY_BEAT_SCHEDULE)
```python
# Operations tab entries
'agent-daily-summary': daily at 12:30 AM
'agent-workspace-status-report': every 8 hours at :00
'agent-research-to-workspace': every 4 hours at :45
'agent-content-to-workspace': every 6 hours at :15
'financial-agent-category-rotation': every 4 hours at :00

# Initiative recovery
'auto-kickstart-initiatives': every 10 minutes
```

---

## Agents Added to AGENT_WORKSPACE_REGISTRY

Session 885 added these agents to enable workspace writes:

| Agent | Category | Output Directory |
|-------|----------|------------------|
| StockAnalystAgent | financial | financial/stocks |
| StockAuditCoordinator | financial | financial/audits |
| BullCaseAgent | financial | financial/bull_cases |
| BearCaseAgent | financial | financial/bear_cases |
| MarketIntelligenceCoordinator | financial | financial/intelligence |
| PredictionMarketAnalyst | financial | financial/predictions |
| SportsOddsAnalyst | sports | sports/odds |
| ArbitrageDetector | sports | sports/arbitrage |

---

## Verification Commands

```bash
# Check if blogs are being generated
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/documents/?doc_type=blog&limit=5"

# Check workspace operations (Operations tab)
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/workspace-operations/?limit=10"

# Sync celery beat schedules
python manage.py sync_celery_beat --apply

# Check circuit breaker status
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/initiatives/circuit-breaker/"
```

---

## Current Status

| Component | Status |
|-----------|--------|
| Blogs | Working (new blogs being generated) |
| Content Queue | Working (dedicated celery-content worker) |
| Operations Tab | Pending verification (tasks scheduled, waiting for crontab times) |
| Initiative Pipeline | Fixed (auto-kickstart + circuit breaker active) |
| Celery Workers | All running on Railway |

---

## Next Steps for Session 886

1. **Verify Operations Tab** - Check if new operations appear after scheduled task times
2. **Monitor Financial Agent Rotation** - Verify stock reviews appear in Operations tab
3. **Check celery-beat logs** - Ensure scheduled tasks are being dispatched
4. **Consider adding manual trigger endpoint** - For testing workspace-writing tasks on demand

---

## Files Changed

| File | Changes |
|------|---------|
| `Procfile` | Added celery-content worker, renamed celery-default |
| `core/settings.py` | Updated CELERY_TASK_ROUTES, added workspace tasks to CELERY_BEAT_SCHEDULE |
| `core/tasks.py` | Added `_get_workspace_for_skin_layer()` helper, added financial agents to registry, added `auto_kickstart_stuck_initiatives` |
