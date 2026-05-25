---
originating_session: 915
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 915: Stage Document Backfill Pipeline

## Summary

Fixed the initiative stage document backfill pipeline. Initiatives that advance to Stage 1 (and beyond) now get documents generated automatically. A Celery Beat task runs every 30 minutes to catch any initiatives with missing stage documents.

## Changes Made

### PRs Merged

| PR | Title | Description |
|----|-------|-------------|
| #759 | Add backfill API endpoint | Created `/api/initiatives/backfill-documents/` endpoint |
| #760 | Route task to default queue | Added `queue='default'` to task decorator |
| #761 | Fix import error and varchar overflow | Fixed ImportError in tasks.py, truncated titles to 200 chars |
| #762 | Add to Celery Beat schedule | Added `backfill-stage-documents` to `core/celery.py` |
| #763 | Add to critical tasks | Added task to `add_critical_celery_tasks.py` |

### Key Files Modified

1. **core/tasks.py** - Added `backfill_stage_documents` task (lines 32346-32420)
   - Runs every 30 minutes via Celery Beat
   - Processes up to 50 initiatives per run
   - Finds initiatives with stages missing documents
   - Triggers `generate_initiative_stage_document` for each

2. **core/celery.py** (lines 312-321) - Added to beat_schedule:
   ```python
   'backfill-stage-documents': {
       'task': 'core.tasks.backfill_stage_documents',
       'schedule': crontab(minute='*/30'),
       'kwargs': {'stage_num': 1, 'limit': 50},
       'options': {'expires': 1800, 'queue': 'default'}
   }
   ```

3. **intelligence/spider_agent_connector.py** (lines 220-222) - Fixed varchar overflow:
   ```python
   title = title[:200] if title else f"Opportunity from {spider_data.spider_name}"
   ```

4. **core/views_initiative_kickstart.py** (lines 723-830) - Added API endpoint for manual triggering

5. **core/management/commands/add_critical_celery_tasks.py** - Added task for DB sync

## How It Works

1. **Automatic Triggering**: Celery Beat runs `backfill_stage_documents` every 30 minutes
2. **Task Logic**: Finds initiatives where `current_stage >= 1` but Stage 1 has no document
3. **Document Generation**: Calls `generate_initiative_stage_document.delay()` for each
4. **Database Sync**: `sync_celery_beat --apply` runs on web deploy to register task

## Deployment Notes

- The web service Procfile runs `sync_celery_beat --apply` on each deploy
- This syncs the task from `core/celery.py` to the django_celery_beat PeriodicTask table
- Celery Beat detects the schedule change and starts triggering the task

## Errors Fixed

1. **ImportError**: Changed `from core.models import UserMessage, Conversation` to proper imports
2. **Varchar Overflow**: Truncated AgentSolution.title to 200 chars before saving
3. **Queue Routing**: Added explicit `queue='default'` to ensure worker receives task

## Pending Work

- ~177 initiatives are missing Stage 1 documents
- At 50 per run, every 30 minutes, should be caught up in ~2 hours
- New initiatives will trigger document generation automatically via `auto_kickstart_stuck_initiatives`

## Monitoring

Check for backfill task execution:
```bash
railway logs --service celery-beat 2>&1 | grep "backfill-stage"
railway logs --service celery-worker 2>&1 | grep "backfill_stage_documents"
```

Verify documents are being created:
```python
from core.models_document_registry import InitiativeStage
InitiativeStage.objects.filter(stage=1, document__isnull=False).count()
```
