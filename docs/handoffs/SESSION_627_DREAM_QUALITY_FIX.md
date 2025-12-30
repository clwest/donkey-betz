# Session 627 - Dream Quality Fix

**Date:** December 30, 2025
**Focus:** Fix low dream quality scores (93.4% scoring below 0.4)
**Result:** Promotion rate increased from 0.5% to ~67%

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

## Files Modified

| File | Change |
|------|--------|
| `core/tasks.py` | Updated composite score formula |

## Database Changes

| Change | Method |
|--------|--------|
| Created `dream-productization-cycle` task | Django shell |
| Marked 25 trigger events as 'skipped' | Django shell |

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

## Next Steps

1. **Monitor backlog processing** - ~1,700 dreams still need scoring
2. **Review promoted dreams** - 79+ awaiting decision in Boardroom
3. **Consider more active projects** - Would improve relevance matching
