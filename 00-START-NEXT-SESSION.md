# Session 901 - Start Here

**Previous Session:** 900 (Signal Intelligence & Provenance)
**Date:** February 1, 2026
**Status:** 76 Agents | 77 Spiders | 25 Advisors | 139 Personas | **SIGNAL INTELLIGENCE: MODELS CREATED** | **820 SUCCESSFUL EXPERIMENTS**

---

## What Was Accomplished in Session 900

### Signal Intelligence Models for Origin & Trigger UI

Created new models to track WHY conversations happen (not just WHEN):

**Problem:** UI showed "Trigger: scheduled triggered conversation" - tells WHEN, not WHY

**Solution:** New provenance chain:
```
SpiderData[] → SignalCluster → AutoTopic → HiveMindSession → Decision → Initiative
```

**New Models:**
1. **SignalCluster** - Groups related spider signals into patterns
   - `source_breakdown`: `{"bluesky": 12, "reddit": 6, "job_listings": 4}`
   - `strength`, `novelty`, `confidence` metrics
   - `keywords`, `sample_signals` for display

2. **AutoTopic** - Records WHY a topic was chosen
   - Links to SignalCluster
   - `rationale` explaining the choice
   - `suggested_agent_names`, `suggested_conversation_type`

3. **TopicSuggestion** - Alternative topic options

**HiveMindSession Changes:**
- Added `signal_cluster` FK
- Added `auto_topic` FK
- Added `trigger_confidence` field

### Files Created/Changed
- `core/models_signal_intelligence.py` - NEW
- `core/models/__init__.py` - Added imports
- `core/models_unified_system.py` - Added FK fields to HiveMindSession
- `core/migrations/0211_session_900_signal_intelligence.py` - NEW

---

## What Was Added (Signal Aggregation)

### Signal Aggregation Service
**File:** `core/services/signal_aggregation_service.py`
- Clusters SpiderData by topic/keyword similarity
- Calculates strength, confidence, novelty metrics
- Detects pattern types (demand_spike, trend_emergence, etc.)
- Generates AutoTopics from actionable clusters

### Celery Tasks
**File:** `core/tasks.py` (bottom)
- `aggregate_spider_signals` - Clusters signals every 30 min
- `process_pending_auto_topics` - Triggers conversations hourly
- `trigger_signal_driven_conversation` - Creates HiveMindSession with provenance
- `cleanup_expired_signals` - Daily cleanup

### Celery Beat Schedule
**File:** `core/celery.py`
- Added schedules for signal intelligence tasks

---

## TOP PRIORITY for Session 901

### 1. Deploy to Railway
Apply migration and restart services to enable signal aggregation.

### 2. API Endpoint for Signal Provenance
`GET /api/initiatives/{id}/origin-signals/` returning:
```json
{
  "signal_cluster": {"source_breakdown": {...}, "strength": 0.81},
  "auto_topic": {"name": "...", "rationale": "..."}
}
```

### 3. UI Update - Origin Signals Section
Display in Initiative modal:
- Origin Signals (source breakdown)
- Detected Pattern (type, strength, confidence)
- Auto Topic (name, triggered time)

---

## Current Celery Architecture

```
celery-worker: -Q default,agents,sports,ml (4 concurrency)
celery-content: -Q content (4 concurrency)
celery-long-running: -Q long_running (2 concurrency)
celery-beat: scheduler
celery-broadcast: -Q broadcast (2 concurrency)
```

---

## Quick Commands

```bash
# Start platform
make start && make celery

# Apply new migration
python manage.py migrate core 0211_session_900_signal_intelligence

# Production experiment status
railway ssh -s donkey-betz-platform python manage.py check_experiment_status
```

---

## Recent PRs

| PR | Description |
|----|-------------|
| #675 | Signal Intelligence Models (Session 900) |
| #671 | Comprehensive Initiative View - Completed filter + origin trace modal |
| #670 | Initiative origin-trace API endpoint |
| #668 | Mythology Lab - Add agent name to Recent Events |

---

## Recent Session History

| Session | Focus | Handoff |
|---------|-------|---------|
| **900** | Signal Intelligence - SignalCluster, AutoTopic models for Origin & Trigger UI | `SESSION_900_SIGNAL_INTELLIGENCE.md` |
| **899** | Comprehensive Initiative View | `SESSION_899_COMPREHENSIVE_INITIATIVE_VIEW.md` |
| **898** | Mythology Lab Agent Name Fix | `SESSION_898_MYTHOLOGY_LAB_FIX.md` |
| **897** | Experiment Pipeline Fix + Initiatives Performance | `SESSION_897_COMPLETE.md` |
| **896** | Codebase Workspace Fix + PDF Export | `SESSION_896_CODEBASE_WORKSPACE_FIX.md` |

---

## System Stats

| Component | Count |
|-----------|-------|
| Agents | 76 |
| Spiders | 77 |
| Advisors | 25 |
| Personas | 139 |
| Database Models | 382+ |
| Celery Tasks | 281 |
| Services | 128 |
| Experiments (Success) | 820 |
| Learnings | 1,152,295 |
| Initiatives | 223 |

---

## Workspace Architecture

| Workspace | Path | Purpose |
|-----------|------|---------|
| `donkey-betz-codebase` | `/app` (production) | CodeGeneratorAgent source access |
| `System Autonomous Workspace` | `/app/workspace` | Generated content storage |
| `{username}-personal` | `/generated_content/users/{username}` | Per-user files |

---

**Next: Implement signal aggregation to wire up the Origin & Trigger UI!**
