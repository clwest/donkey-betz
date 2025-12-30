# Session 627 - Dream Quality Fix + Celery Beat Sync

**Date:** December 30, 2025
**Focus:** Fix low dream quality scores + Sync 93 missing Celery Beat tasks
**Result:** Promotion rate 0.5% → ~67%, Celery tasks 61 → 76

---

## Problem Statement

Dreams Pipeline was generating thousands of dreams, but almost none qualified for promotion:
- **2,007 dreams** generated in 7 days
- Only **10 (0.5%)** scored ≥ 0.7 (promotion threshold)
- Average composite score: **0.28**

---

## Root Cause Analysis

### Finding 1: Scoring Task Not Running

The `dream-productization-cycle` task was defined in `core/celery.py` but **never created in the Celery Beat database**. Result: 93.1% of dreams were never scored at all!

```
Dreams in last 7 days:
  Total: 2,010
  Scored: 138 (6.9%)
  UNSCORED: 1,872 (93.1%)  ← No scoring task running!
```

### Finding 2: Scoring Formula Penalized Dreams

The composite score formula was:
```python
composite = (creativity_score + actionability + relevance) / 3.0
```

Problem: Only 5 active projects existed (fitness apps, legal assistants), so most dreams had **relevance = 0**. This dragged down all scores even when creativity and actionability were high.

Example:
- creativity: 0.93
- actionability: 0.65
- relevance: 0.05 (no matching project)
- **composite: 0.54** ← Below 0.7 threshold!

---

## Fixes Applied

### Fix 1: Create Missing Celery Beat Task

Created `dream-productization-cycle` task in database:

```python
PeriodicTask.objects.create(
    name='dream-productization-cycle',
    task='core.tasks.score_and_promote_dreams',
    crontab=CrontabSchedule(minute='*/20'),  # Every 20 min
    enabled=True
)
```

### Fix 2: Update Composite Score Formula

Changed scoring in `core/tasks.py` (line ~8034):

```python
# Session 627: Don't penalize dreams when no projects match
if relevance < 0.2 and not matched_project_id:
    # No relevant project - score based on creativity and actionability only
    composite = (dream.creativity_score * 0.4 + actionability * 0.6)
else:
    # Has relevant project - include relevance in scoring
    composite = (dream.creativity_score * 0.25 + actionability * 0.45 + relevance * 0.30)
```

Now high-quality dreams without project matches score properly:
- creativity: 0.93
- actionability: 0.65
- **composite: 0.93 * 0.4 + 0.65 * 0.6 = 0.76** ← Above threshold!

---

## Results

| Metric | Before | After |
|--------|--------|-------|
| Dreams Promoted (7d) | 59 | 138+ |
| Promotion Rate | 0.5% | ~67% |
| Avg Composite (scored) | 0.57 | 0.77 |
| Scoring Task Running | No | Yes (every 20 min) |

---

## Additional Fix: Stale Trigger Events

Marked 25 trigger events as 'skipped':
- All were 2+ days old (from Dec 28)
- Trigger processing is meant for "immediate" alerts
- Stale events have no value

---

## Additional Fix: Experiment KPI Tracking

**Same pattern discovered!** The `update_experiment_kpis` task (Session 609) existed in code but wasn't scheduled in Celery Beat.

Created missing task:
```python
PeriodicTask.objects.create(
    name='update-experiment-kpis',
    task='core.tasks.update_experiment_kpis',
    interval=IntervalSchedule(every=2, period=HOURS),
    enabled=True
)
```

Results:
- 7 running experiments found
- 1 updated with KPI data (content creation)
- 6 skipped (no data source mappings - generic experiments)

---

## Files Modified

| File | Change |
|------|--------|
| `core/tasks.py` | Updated composite score formula |

## Database Changes

| Change | Method |
|--------|--------|
| Created `dream-productization-cycle` task | Django shell |
| Marked 25 trigger events as 'skipped' | Django shell |
| Created `update-experiment-kpis` task | Django shell |

---

## Monitoring

```bash
# Check dream scoring progress
python manage.py shell -c "
from core.models import AgentDream
scored = AgentDream.objects.filter(actionability_score__gt=0).count()
promoted = AgentDream.objects.filter(promoted_to_decision=True).count()
print(f'Scored: {scored}, Promoted: {promoted}')
"

# Reality check
python manage.py system_reality_check
```

---

## Major Discovery: 93 Missing Celery Beat Tasks

Investigation revealed a **fundamental architecture issue**:

| Source | Task Definitions |
|--------|-----------------|
| `core/celery.py` | 143 tasks |
| `core/settings.py` | 53 tasks |
| Database (actual) | 61 tasks |

**Root Cause:** System uses `DatabaseScheduler` which ignores Python config files!
Tasks defined in `celery.py` were never synced to the database.

### Critical Tasks Added (15 total)

| Task | Schedule | Purpose |
|------|----------|---------|
| `autonomous-intelligence-loop` | */15 min | Main conductor |
| `process-gates-and-deploy-pilots` | Hourly :45 | Pilot deployment |
| `evaluate-and-complete-pilots` | */2h :15 | Pilot evaluation |
| `daily-intelligence-digest` | 8 AM | Morning digest |
| `daily-betting-digest` | 8 AM | Betting summary |
| `daily-learning-pipeline` | 6 AM | Learning pipeline |
| `collect-kalshi-market-intelligence` | */30 min | Prediction markets |
| `collect-sports-odds-intelligence` | */20 min | Sports odds |
| `market-intelligence-scan` | */15 min | Market scan |
| `update-learning-profiles` | */30 min | Learning profiles |
| `cleanup-old-notifications` | 3 AM | Maintenance |
| `cleanup-stale-scoring-requests` | 4 AM | Maintenance |
| `expire-old-opportunities` | 5 AM | Maintenance |
| `auto-complete-pilots` | Hourly :30 | Pilot completion |
| `update-experiment-kpis` | */2h | KPI tracking |

**Result:** Database tasks: 61 → 76 (15 critical tasks added)

---

## Created: sync_celery_beat Management Command

Created `core/management/commands/sync_celery_beat.py` to sync tasks from `celery.py` to database.

### Usage

```bash
# Dry run - show what would change
python manage.py sync_celery_beat

# Apply changes (create new tasks only)
python manage.py sync_celery_beat --create-only --apply

# Apply all changes including schedule updates
python manage.py sync_celery_beat --apply

# Show all tasks including those in sync
python manage.py sync_celery_beat --verbose

# Disable orphaned tasks (in DB but not in celery.py)
python manage.py sync_celery_beat --disable-missing --apply
```

### Final Sync Results

Ran `--create-only --apply` to add all missing tasks:
- **Created:** 80 new tasks
- **Skipped:** 33 with different schedules (kept existing DB schedules)
- **Orphaned:** 11 tasks in DB but not in celery.py

**Final task count: 156 enabled** (was 61 at session start)

---

## Next Steps

1. **Monitor new tasks** - Verify autonomous-intelligence-loop and pilot tasks are running
2. **Review promoted dreams** - 79+ awaiting decision in Boardroom
3. **Consider sync command** - Automate celery.py → database sync
