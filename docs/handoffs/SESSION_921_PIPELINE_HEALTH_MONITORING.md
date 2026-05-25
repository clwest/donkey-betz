---
originating_session: 921
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 921: Pipeline Health Monitoring

**Date:** February 3, 2026
**PRs:** #807 (Reset Premature), #808 (Pipeline Health)
**Status:** Complete

---

## Overview

Implemented real-time Pipeline Health monitoring to provide visibility into whether initiatives are actually making progress through the ConceptForge pipeline, not just showing static counts.

---

## Problem Solved

With 305 active initiatives, it was impossible to know:
1. Are initiatives actually moving through stages?
2. Which ones are stale (no activity in days)?
3. Is the pipeline working or stalled?

The previous view showed static counts but no proof of actual progress.

---

## Changes Made

### 1. Reset Premature Completed Initiatives (PR #807)

**File:** `core/views_initiative_kickstart.py`

Found and fixed 29 initiatives that were marked COMPLETED prematurely with 0% approved stages.

```python
@api_view(['POST', 'GET'])
def reset_premature_completed(request):
    """Reset COMPLETED initiatives with < 100% approved stages back to ACTIVE"""
    # GET: Preview (dry_run)
    # POST with dry_run=false: Execute reset
```

**URL:** `/api/initiatives/reset-premature-completed/`

---

### 2. Pipeline Health API (PR #808)

**File:** `core/views_initiative_kickstart.py`

New endpoint that returns comprehensive pipeline health data.

```python
@api_view(['GET'])
def pipeline_health(request):
    """Real-time pipeline health monitoring"""
    # Returns:
    # - summary: active_count, moved_last_24h, transitions_1h/24h, stale_count
    # - recent_transitions: Last 50 stage transitions with details
    # - stale_initiatives: Initiatives with no activity in 48+ hours
    # - stage_distribution: Count by status for each stage (1-5)
    # - hourly_activity: Transition counts for last 24 hours
    # - health_status: healthy/moderate/slow/stalled/critical
```

**URL:** `/api/initiatives/pipeline-health/`

**Response Example:**
```json
{
  "health_status": "healthy",
  "health_message": "Pipeline is active: 3 transitions in last hour",
  "summary": {
    "active_count": 305,
    "moved_last_24h": 12,
    "transitions_last_24h": 564,
    "transitions_last_1h": 3,
    "stale_count": 47
  },
  "recent_transitions": [
    {
      "initiative_name": "Targeted spider spawn...",
      "stage_number": 1,
      "from_status": "DRAFT",
      "to_status": "APPROVED",
      "time_ago": "2h ago",
      "triggered_by": "ContentWriterAgent"
    }
  ],
  "stage_distribution": {
    "stage_1": {"approved": 89, "draft": 12, "pending": 45},
    "stage_2": {"pending": 120, "draft": 8}
  },
  "hourly_activity": [
    {"hour": 0, "transitions": 3},
    {"hour": 1, "transitions": 5}
  ]
}
```

---

### 3. Frontend Health Tab (PR #808)

**File:** `frontend/src/pages/workspace/tabs/InitiativesTab.tsx`

Added new "Health" tab to Initiatives page with:

| Component | Description |
|-----------|-------------|
| Health Banner | Color-coded status (green=healthy, red=stalled) |
| Summary Cards | Active count, moved 24h, transitions 1h, stale count |
| Activity Chart | Bar chart of hourly transitions (last 24h) |
| Stage Distribution | Visual breakdown by stage and status |
| Live Feed | Recent transitions with timestamps and agents |
| Stale Warning | List of initiatives with no recent activity |

**Features:**
- Auto-refreshes every 15 seconds
- Pulsing indicator when healthy
- Shows who/what triggered each transition
- Quality scores displayed when available

---

## Key Data Points

From production data:
- **564** total StageTransitionLog entries
- **564** transitions in last 24 hours
- Most recent: "Targeted spider spawn..." - DRAFT → APPROVED (2h ago)
- Pipeline IS actively working

---

## Files Changed

| File | Lines | Description |
|------|-------|-------------|
| `core/views_initiative_kickstart.py` | +330 | Reset endpoint + Pipeline health API |
| `core/urls.py` | +2 | New URL routes |
| `frontend/.../InitiativesTab.tsx` | +294 | Health tab UI |

---

## Production Verification

```bash
# Reset the 29 prematurely-completed initiatives
railway run python manage.py shell -c "..."
# Result: 29 initiatives reset to ACTIVE

# Verify transition logs exist
railway run python manage.py shell -c "StageTransitionLog.objects.count()"
# Result: 564 entries
```

---

## Usage

### Access Pipeline Health

1. Navigate to Workspace → Initiatives
2. Click the "Health" tab
3. View real-time status, activity feed, and stale warnings

### Check Stale Initiatives

The Health tab shows initiatives with no activity in 48+ hours, sorted by staleness.

### Verify Pipeline Activity

The hourly activity chart proves work is happening over time, not just showing static counts.

---

## Next Steps

1. **Investigate stale initiatives** - Many may need manual intervention
2. **Add Celery task monitoring** - Link to actual background task execution
3. **Add alerts** - Notify when pipeline goes stalled/critical
4. **Add stage time tracking** - How long initiatives spend in each stage

---

## Related Sessions

- Session 920: Panel/Advisor System Improvements
- Session 916: StageTransitionLog model (hard invariants)
- Session 904: Initiative UI Overhaul

---

**Author:** Claude Code (Session 921)
