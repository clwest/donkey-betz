# Session 597 - Start Here

**Previous Session:** 596
**Date:** December 29, 2025
**Focus:** Experiment Tracking Registry

---

## Session 596 Accomplishments

### Experiment Tracking Registry (Complete)

Built a system to connect pilots to formal experiments with KPI ownership:

| Component | Description |
|-----------|-------------|
| **Experiment Model** | Links to PilotExecution, tracks KPI owner, target, current value |
| **Auto-Create** | Experiment created automatically when pilot starts |
| **API Endpoints** | 4 new endpoints for experiments |
| **Dashboard UI** | Full portfolio view in Intelligence Command Center |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/experiments/` | GET | List all experiments |
| `/api/experiments/portfolio/` | GET | Portfolio metrics & KPI owners |
| `/api/experiments/<id>/update-kpi/` | POST | Update KPI value |
| `/api/experiments/<id>/complete/` | POST | Mark experiment complete |

### Database Fix

Resolved migration issue where pilot/experiment tables weren't created despite migrations showing as applied. Tables recreated manually.

**Note:** The 18 pilots from Session 594 were lost during table recreation. Need to restart pilots to populate the system.

---

## Session 597 Options

### Option A: Kill Switch Integration

Add ability to stop experiments mid-run:
- "Stop Experiment" button on dashboard
- Reason input required
- Auto-fails the experiment
- Discord notification

### Option B: Experiment Learning Loop

Improve future decision-making from outcomes:
- Capture experiment outcomes when complete
- Feed learnings back to decision-making
- Improve future success predictions
- Track success patterns by decision type

### Option C: KPI Owner Assignment UI

Make accountability explicit:
- Allow manual KPI owner assignment
- Send notifications to owners
- Owner-specific dashboard view

---

## Current System Stats

| Component | Count |
|-----------|-------|
| **Agents** | 71 (47 routable) |
| **Spiders** | 77 (72 working) |
| **PA Tools** | 77 |
| **Decisions (Draft)** | 645 |
| **Decisions (Canonical)** | 127 |
| **Pilot Readiness Gates** | 0 (tables recreated) |
| **Running Pilots** | 0 (tables recreated) |
| **Experiments** | 0 (waiting for pilots) |
| **Celery Tasks** | 228 |

---

## Test Commands

```bash
# Start services
make start && make celery

# Test experiment API
curl -s http://localhost:8000/api/experiments/portfolio/ | python3 -m json.tool

# Start a pilot to create experiment
# 1. Open AI Studio: http://localhost:8000/ai-studio/
# 2. Go to Intelligence Command Center tab
# 3. Find a gate with "Ready" status
# 4. Click "Start Pilot" button
# 5. Check Experiment Tracking Registry section
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `core/models_pilot_readiness.py` | Gate, Checklist, Execution, Experiment models |
| `core/views_agent_learning.py:3070-3328` | Experiment API endpoints |
| `core/urls.py:2730-2734` | Experiment URL routes |
| `ai_core/templates/ai_image_studio.html` | Experiment Dashboard UI |
| `docs/handoffs/SESSION_596_EXPERIMENT_TRACKING.md` | Session 596 handoff |

---

**Session 596: Experiment Tracking Registry - COMPLETE**
