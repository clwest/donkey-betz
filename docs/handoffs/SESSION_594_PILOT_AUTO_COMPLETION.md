# Session 594: Pilot Auto-Completion + AI Content Generation

**Date:** December 29, 2025
**Previous Session:** 593 (ThinkingAgent Auto-Gate Integration)
**Focus:** Automated pilot evaluation, completion, and AI-generated checklist content

---

## Executive Summary

Session 594 implemented:
1. **Two-layer automated pilot evaluation system** - Reduces manual oversight while maintaining safety controls
2. **AI-powered checklist content generation** - System generates threat models, rollback procedures, success metrics, etc. so humans can review/approve instead of writing from scratch

---

## Implementation

### Layer A: Time-Based Auto-Completion

Simple, safe auto-completion after observation period.

| Rule | Value |
|------|-------|
| Minimum observation period | 24 hours |
| Kill switch check | Must be FALSE |
| Outcome check | Must be 'pending' |
| Result | Auto-complete as SUCCESS |

**Celery Task:** `auto_complete_pilots`
**Schedule:** Every 4 hours at :00

### Layer B: ThinkingAgent Smart Evaluation

AI-powered evaluation with reasoning and suggestions.

| Rule | Value |
|------|-------|
| Minimum before evaluation | 4 hours |
| Evaluation method | GPT-4o-mini analysis |
| Output | Suggested outcome + confidence + reasoning |
| Auto-action | None (suggestion only) |

**Celery Task:** `evaluate_pilots_with_thinking_agent`
**Schedule:** Every 6 hours at :30

---

## Flow Diagram

```
Pilot Started (status: 'running')
       │
       ├──── After 4 hours ────┐
       │                       ▼
       │              Layer B: ThinkingAgent
       │              ├─ Collects metrics
       │              ├─ Analyzes decision context
       │              ├─ Suggests outcome (SUCCESS/PARTIAL/FAILURE)
       │              └─ Stores in pilot.metrics['thinking_agent_evaluation']
       │
       └──── After 24 hours ───┐
                               ▼
                      Layer A: Auto-Complete
                      ├─ Check: kill_switch_triggered == False
                      ├─ Check: outcome == 'pending'
                      ├─ Auto-set: outcome = 'success'
                      ├─ Auto-set: status = 'completed'
                      └─ Discord notification sent
```

---

## New Functions

### `core/tasks.py`

| Function | Purpose |
|----------|---------|
| `auto_complete_pilots()` | Layer A - Time-based auto-completion |
| `evaluate_pilots_with_thinking_agent()` | Layer B - AI evaluation |
| `collect_pilot_metrics(decision, pilot)` | Gather relevant metrics for evaluation |

### Metrics Collection

Based on decision type, different metrics are collected:

| Decision Type | Metrics Collected |
|---------------|-------------------|
| All | concerns_during_pilot, agent_memories_created, conversations_during_pilot |
| Security | kill_switch_triggered, security_check status |
| Policy | compliance_issues, user_complaints |

---

## Celery Beat Schedules Added

```python
'auto-complete-pilots': {
    'task': 'core.tasks.auto_complete_pilots',
    'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
},

'evaluate-pilots-smart': {
    'task': 'core.tasks.evaluate_pilots_with_thinking_agent',
    'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours
},
```

---

## AI Content Generation (Layer C)

Transforms checklist items from manual documentation into AI-assisted review.

### How It Works

1. **On Gate Creation**: `generate_checklist_content_async` Celery task queued
2. **AI Generates**: GPT-4o-mini creates content for each checklist item type
3. **Human Reviews**: User sees AI content with "Approve & Complete" or "Regenerate" buttons
4. **Governance Enhanced**: Real threat models, real rollback procedures instead of checkbox clicking

### Supported Item Types

| Item Type | Generated Content |
|-----------|-------------------|
| `threat_model` | Identified threats, impact assessment, mitigation strategies |
| `rollback_procedure` | Triggers, steps, verification, communication plan |
| `success_metrics` | Primary KPIs, secondary indicators, measurement methods |
| `kill_switch` | Automatic triggers, manual triggers, mechanism, post-kill actions |
| `encryption_choice` | Data classification, encryption requirements, access controls |
| `adversarial_test` | Attack scenarios, test cases, red team checklist |
| `basic_review` | Decision clarity, stakeholder alignment, resources, timeline |

### New Service

**File:** `core/services/checklist_content_generator.py`

```python
class ChecklistContentGenerator:
    def generate_all_items(self, gate) -> Dict[str, str]
    def generate_for_item(self, item_type, context) -> Optional[str]
    def _build_decision_context(self, decision) -> Dict[str, Any]
    def _get_prompt_for_type(self, item_type, context) -> Optional[str]
```

### New API Endpoint

```
POST /api/pilot-gates/<gate_id>/regenerate/
```

Regenerates all checklist content for a gate.

### UI Changes

- Checklist items show "AI Ready" badge when content is generated
- Click to expand content panel
- "✅ Approve & Complete" button to accept AI content
- "🔄 Regenerate" button to request new content

---

## UI Fixes

### Fixed: toggleChecklistItem

**Problem:** JavaScript sent `status: 'completed'` but API expected `action: 'complete'`
**Fix:** Changed to send correct `action` parameter

### Fixed: startPilot

**Problem:** "Start Pilot" button called `updateGateStatus(id, 'pilot')` but 'pilot' isn't a valid status action
**Fix:** Created new `startPilot()` function that hits `/api/pilot-gates/<id>/pilot/` endpoint

### Added: Pilot Running Status

**Problem:** After starting a pilot, "Start Pilot" button remained clickable
**Fix:** API returns `running_pilot` info, UI shows "Pilot Running" badge with elapsed time and complete buttons

---

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py` | +4 functions (~250 lines) - auto_complete_pilots, evaluate_pilots_with_thinking_agent, generate_checklist_content_async, collect_pilot_metrics |
| `core/celery.py` | +2 Beat schedules |
| `core/services/checklist_content_generator.py` | NEW - AI content generation service (~330 lines) |
| `core/models_pilot_readiness.py` | Modified create_for_decision() to queue content generation |
| `core/views_agent_learning.py` | Added running_pilot info, generated_content to API, regenerate endpoint |
| `core/urls.py` | Added /regenerate/ endpoint route |
| `ai_core/templates/ai_image_studio.html` | Fixed JS functions, added content panels, approve/regenerate buttons |

---

## Testing

```bash
# Test auto-completion (will report no eligible if < 24h)
.venv/bin/python -c "
import os; os.environ['DJANGO_SETTINGS_MODULE']='core.settings'
import django; django.setup()
from core.tasks import auto_complete_pilots
print(auto_complete_pilots())
"

# Test evaluation (will report no eligible if < 4h)
.venv/bin/python -c "
import os; os.environ['DJANGO_SETTINGS_MODULE']='core.settings'
import django; django.setup()
from core.tasks import evaluate_pilots_with_thinking_agent
print(evaluate_pilots_with_thinking_agent())
"
```

---

## Session 595 Options

### Option A: UI Enhancement for Pilot Status

Show running pilots with:
- Progress indicator
- Time elapsed
- ThinkingAgent evaluation when available
- Manual complete/fail buttons

### Option B: Kill Switch Integration

Allow triggering kill switch from UI:
- "Stop Pilot" button
- Reason input
- Auto-fails the pilot
- Notifies via Discord

### Option C: Pilot Dashboard

Dedicated view for all pilots:
- Running pilots with live status
- Completed pilots with outcomes
- Learnings aggregation
- Success rate metrics

---

**Session 594: Pilot Auto-Completion System - COMPLETE**
