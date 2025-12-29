# Session 596: Experiment Tracking Registry

**Date:** December 29, 2025
**Previous Session:** 595 (Pilot Dashboard)
**Focus:** Connect pilots to formal experiments with KPI ownership

---

## Executive Summary

Built a complete Experiment Tracking Registry that:
- Auto-creates experiments when pilots start
- Tracks KPI ownership and targets
- Provides portfolio-level visibility
- Reduces decision fatigue through systematic outcome tracking

Based on ThinkingAgent insight:
> *"Create an experiment-tracking template and KPI ownership registry to reduce decision fatigue and improve follow-through on the many Boardroom decisions"*

---

## Implementation

### 1. Database Model: Experiment

Created `Experiment` model in `core/models_pilot_readiness.py`:

```python
class Experiment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    pilot = models.OneToOneField(PilotExecution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    hypothesis = models.TextField(blank=True)
    kpi_owner = models.CharField(max_length=100, blank=True)
    primary_kpi = models.CharField(max_length=255, blank=True)
    target_value = models.CharField(max_length=100, blank=True)
    current_value = models.CharField(max_length=100, blank=True, null=True)
    secondary_kpis = models.JSONField(default=list, blank=True)
    status = models.CharField(choices=['running', 'success', 'failure', 'inconclusive'])
    extracted_metrics = models.JSONField(default=dict, blank=True)  # KPI history
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True)
    learnings = models.TextField(null=True)

    @classmethod
    def create_from_pilot(cls, pilot: PilotExecution):
        """Auto-creates experiment from pilot, extracting KPIs from AI-generated success_metrics"""
```

### 2. Auto-Create Experiment from Pilot

Modified `start_pilot_execution()` in `core/views_agent_learning.py` to auto-create experiments when pilots start:
- Extracts KPIs from AI-generated `success_metrics` checklist item
- Uses decision topic as experiment name
- Parses hypothesis from success criteria

### 3. API Endpoints

Added 4 new endpoints in `core/views_agent_learning.py`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/experiments/` | GET | List all experiments with KPI details |
| `/api/experiments/portfolio/` | GET | Portfolio metrics and KPI owner distribution |
| `/api/experiments/<id>/update-kpi/` | POST | Update current KPI value with history |
| `/api/experiments/<id>/complete/` | POST | Mark experiment as success/failure/inconclusive |

### 4. Experiment Dashboard UI

Added new section in Intelligence Command Center (`ai_core/templates/ai_image_studio.html`):

**Metrics Row (6 cards):**
| Metric | Description |
|--------|-------------|
| Success Rate | Percentage of successful experiments |
| Total Experiments | All experiments ever created |
| Active | Currently running experiments |
| Success | Count of successful outcomes |
| Failure | Count of failed outcomes |
| Inconclusive | Count of inconclusive outcomes |

**KPI Ownership Distribution:**
- Visual badges showing who owns how many experiments
- "Unassigned" badge for experiments without owners

**Running Experiments:**
- Experiment name and decision topic
- Days running counter
- KPI: Primary KPI name
- Target: Expected value
- Current: Latest measured value
- Owner: Who is accountable

**Recent Completions:**
- Outcome badge (Success/Failure/Inconclusive)
- KPI comparison (target vs actual)

---

## Files Modified

| File | Changes |
|------|---------|
| `core/models_pilot_readiness.py` | +Experiment model (~120 lines) |
| `core/views_agent_learning.py` | +4 API functions (~250 lines) |
| `core/urls.py` | +4 URL routes, +4 imports |
| `ai_core/templates/ai_image_studio.html` | +Experiment Dashboard UI, +loadExperimentPortfolio() |
| `core/migrations/0131_session_596_experiment_tracking.py` | Migration file |

---

## Database Note

During this session, a migration issue was discovered where pilot/experiment tables weren't being created despite migrations showing as applied. Fixed by:
1. Removing corrupted migration records from `django_migrations`
2. Manually creating tables via SQL
3. Tables are now working correctly

**Important:** The 18 pilots started in Session 594 were lost during table recreation. New pilots will need to be started to populate the Experiment Tracking Registry.

---

## Session 597 Options

### Option A: Kill Switch Integration
- Add "Stop Experiment" button to dashboard
- Reason input required
- Auto-fails the experiment
- Discord notification

### Option B: Experiment Learning Loop
- Capture experiment outcomes when complete
- Feed learnings back to decision-making
- Improve future success predictions
- Track success patterns by decision type

### Option C: KPI Owner Assignment UI
- Allow manual KPI owner assignment
- Send notifications to owners
- Owner dashboard view

---

**Session 596: Experiment Tracking Registry - COMPLETE**
