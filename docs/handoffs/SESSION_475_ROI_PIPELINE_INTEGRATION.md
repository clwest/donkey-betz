# Session 475: ROI Pipeline Integration - Systems Connected

**Date:** December 17, 2025
**Status:** COMPLETE
**Type:** System Integration + Bug Fixes + ROI Automation

---

## Summary

Connected the ROI metrics system to the actual data flow, fixed the model conflict, and added provenance hooks throughout the pipeline. The system is now fully wired to track:
- Opportunity views → clicks → applications → revenue
- Narrative evidence → shifts → content episodes
- All with provenance tracking

---

## What Was Fixed

### 1. Model Conflict Resolution

**Problem:** `core/models_learning_loop.py` had duplicate `PredictionOutcome`, `UserBriefFeedback`, and `AgentAccuracyMetrics` models that conflicted with the same models in `core/models_unified_system.py`.

**Solution:** Removed the orphaned `models_learning_loop.py` file. All models already existed in the canonical location.

```bash
# Removed file
rm core/models_learning_loop.py
```

### 2. ROI Tracking Hooks Added

Added ROI event tracking to key opportunity endpoints:

| Endpoint | Event Tracked |
|----------|---------------|
| `GET /api/opportunities/<id>/` | `view` |
| `POST /api/opportunities/<id>/act/` | `click` |
| `POST /api/opportunity-tasks/<id>/apply/` | `application` |
| `POST /api/opportunity-tasks/<id>/won/` | `revenue` |

### 3. Provenance Hooks Added

Added provenance tracking to data creation points:

| Location | Entity Type |
|----------|-------------|
| `narrative_historian_agent.py:385` | `narrative_evidence` |
| `trend_break_detector_agent.py:539` | `narrative_shift` |
| `autonomous_content_studio_coordinator.py:605` | `content_episode` |
| `tasks.py:12229` | `content_episode` |

### 4. New Celery Tasks

Created 6 new tasks in `core/tasks.py`:

| Task | Purpose | Schedule |
|------|---------|----------|
| `aggregate_roi_metrics_daily` | Aggregate ROI metrics | Daily 2:00 AM |
| `generate_weekly_intelligence_brief` | Create weekly brief | Monday 7:00 AM |
| `record_opportunity_view` | Track views | On-demand |
| `record_opportunity_click` | Track clicks | On-demand |
| `record_opportunity_application` | Track applications | On-demand |
| `record_revenue_event` | Track revenue | On-demand |

### 5. Celery Beat Schedules

Added to `core/celery.py`:

```python
'roi-metrics-daily-aggregation': {
    'task': 'roi_metrics.aggregate_daily',
    'schedule': crontab(minute=0, hour=2),  # Daily 2:00 AM
},
'roi-metrics-weekly-brief': {
    'task': 'roi_metrics.generate_weekly_brief',
    'schedule': crontab(minute=0, hour=7, day_of_week='monday'),  # Monday 7:00 AM
},
```

---

## Complete Data Flow (Now Connected!)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FULLY CONNECTED PIPELINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  SPIDER NETWORK (67 spiders)                                        │
│       ↓                                                              │
│  SpiderData → Opportunity → ScoringResult                           │
│       ↓                                                              │
│  NarrativeEvidence → NarrativeShift → ChannelEpisode                │
│       ↓                                                              │
│  ROI TRACKING:                                                       │
│     View → Click → Application → Revenue                             │
│       ↓                                                              │
│  PROVENANCE: Full data lineage with hash chains                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Files Changed

### Deleted
- `core/models_learning_loop.py` - Orphaned file with duplicate models

### Modified
- `core/tasks.py` - Added 6 new ROI tasks (~280 lines)
- `core/celery.py` - Added 2 beat schedules for ROI automation
- `core/views_opportunity.py` - Added ROI tracking to 4 endpoints
- `core/agents/narrative/narrative_historian_agent.py` - Added evidence provenance
- `core/agents/narrative/trend_break_detector_agent.py` - Added shift provenance
- `core/agents/autonomous_content_studio_coordinator.py` - Added episode provenance

---

## System Statistics After Session 475

| Metric | Value |
|--------|-------|
| SpiderData | 18,964 records |
| Narratives | 30 |
| NarrativeEvidence | 730 records |
| NarrativeShifts | 1 |
| ContentChannels | 3 |
| Episodes | 3 |
| ConversionEvents | 6 |
| Provenance Records | 2 (will grow as system runs) |

---

## Verification Commands

```bash
# Check all tasks import
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.tasks import (
    aggregate_roi_metrics_daily,
    generate_weekly_intelligence_brief,
    record_opportunity_view
)
print('Tasks OK')
"

# Check provenance functions
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
from core.services.provenance_tracker import (
    create_narrative_evidence_provenance,
    create_narrative_shift_provenance,
    create_content_episode_provenance
)
print('Provenance functions OK')
"

# Run ROI aggregation manually
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.tasks import aggregate_roi_metrics_daily
result = aggregate_roi_metrics_daily()
print(f'Aggregations: {result}')
"
```

---

## What Happens Next (Automatic)

Once Celery is restarted:

1. **Daily at 2:00 AM:** ROI metrics aggregation runs
2. **Monday 7:00 AM:** Weekly intelligence brief generated
3. **Every 12 hours:** Unified pipeline runs all 3 Tier 1 systems
4. **Every 2 hours:** Health check verifies all systems operational

---

## Discord Commands (Already Exist)

From Session 472, these ROI commands are available:
- `/roi-summary` - Show ROI summary metrics
- `/roi-dashboard` - Dashboard overview
- `/roi-brief` - Generate/view weekly brief
- `/roi-funnel` - Conversion funnel metrics
- `/roi-attribution` - Revenue attribution by source

---

## To Restart and Activate

```bash
# Restart Celery to pick up new schedules
pkill -f celery
make celery

# Verify schedules are active
celery -A core inspect scheduled
```

---

**Session 475 Complete - ROI Pipeline Fully Integrated!**

The system now tracks the complete journey:
```
Spider Data → Opportunity → View → Click → Apply → Revenue
     ↓
Provenance Chain: Every step tracked with blockchain-style integrity
```
