# Session 766: Human Page Data Quality Fixes

**Date:** January 16, 2026
**Focus:** Fix Human Page displaying incorrect data (ContentWriterAgent 516, ArbitrageDetector 473)

## Problem

User reported Human Page showing:
- ContentWriterAgent: 516
- ArbitrageDetector: 473
- These were running 400x more than other agents

## Root Causes Found

### 1. by_source and by_type queries showing ALL items, not just pending
The `get_attention_stats()` method was showing total counts including expired/acted items, making ArbitrageDetector appear at 473 when only 1 was pending (450 expired).

### 2. Runaway blog generation
The Celery Beat schedule for `generate-self-blog` task had a bug:
- **Bug:** `crontab(hour='*/6')` - missing minute specification
- **Effect:** Ran every minute during hours 0, 6, 12, 18 (240 runs/day potential)
- **Actual:** 116 blogs generated in 24 hours

### 3. Duplicate attention items
251 duplicate attention items found (items with identical title and source).

## Fixes Applied

### Fix 1: Pending-only queries (human_interface_service.py)
```python
# Session 766: By item type (pending items only)
pending_items = items.filter(status='pending')
by_type = dict(
    pending_items.values('item_type')
    .annotate(count=Count('id'))
    .values_list('item_type', 'count')
)

# Session 766: By source agent (pending items only)
by_source = dict(
    pending_items.exclude(source_agent='')
    .values('source_agent')
    .annotate(count=Count('id'))
    .order_by('-count')[:10]
    .values_list('source_agent', 'count')
)
```

### Fix 2: Blog generation schedule (settings.py + database)
```python
# BEFORE (bug):
'schedule': crontab(hour='*/6'),  # Every 6 hours - WRONG! minute=* by default

# AFTER (fixed):
'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours at :00
```

Also fixed in django_celery_beat database:
```python
# Changed crontab from "* */6 * * *" to "0 */6 * * *"
CrontabSchedule.objects.get_or_create(
    minute='0',
    hour='*/6',
    ...
)
```

### Fix 3: Duplicate cleanup
Ran cleanup to remove 251 duplicate attention items (keeping newest of each).

## Results After Fixes

| Metric | Before | After |
|--------|--------|-------|
| ArbitrageDetector (pending) | 473 | 1 |
| ContentWriterAgent (pending) | 516 | 284 |
| Duplicate items | 251 | 0 |
| Blog generation rate | 240/day potential | 4/day |

## Files Modified

1. **core/services/human_interface_service.py** - Fixed by_source and by_type to filter pending only
2. **core/settings.py** - Fixed crontab to include minute=0

## Verification Commands

```bash
# Check pending items by source
.venv/bin/python manage.py shell -c "
from core.models_human_interface import HumanAttentionItem
from django.db.models import Count
pending = HumanAttentionItem.objects.filter(status='pending')
by_source = pending.values('source_agent').annotate(count=Count('id')).order_by('-count')
for s in by_source[:10]:
    print(f'{s[\"source_agent\"]}: {s[\"count\"]}')"

# Check blog generation schedule
.venv/bin/python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
task = PeriodicTask.objects.get(name='generate-self-blog')
print(f'Schedule: {task.crontab}')"
```

## Related Sessions

- Session 763: Mission Control System (created attention item → action flow)
- Session 759: Memory & Blog Fixes (backfill command that created many items)
- Session 687: Human Interface Layer (original implementation)
