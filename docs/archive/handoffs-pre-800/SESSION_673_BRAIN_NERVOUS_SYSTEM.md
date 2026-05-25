# Session 673: Brain-Nervous System Connection

**Date:** January 5, 2026
**Focus:** Connect Personal Assistant (Brain) to ML Opportunity Pipeline (Nervous System)

## Overview

Following Session 672's completion of the ML Opportunity Pipeline automation (Spiders → Score → Opportunity → Task → Agent → Outcome), this session implements the tools that allow the Personal Assistant (the "brain") to query and manage the pipeline (the "nervous system").

## The Analogy

- **Spiders** = Sensory inputs (gathering data from the world)
- **ML Scoring** = Reflex processing (quick pattern matching)
- **Agents** = Organs (specialized workers)
- **Personal Assistant** = Brain (conscious control and decision-making)

Before this session, the brain couldn't query its nervous system - it couldn't see what opportunities were flowing through, couldn't manage tasks, couldn't trigger manual execution, and couldn't track revenue outcomes.

## What Was Built

### 4 New PA Tools (77 → 81 total)

#### 1. `opportunity_manager_tool`
Query and filter opportunities from the ML Pipeline.

**Actions:**
- `list` - List opportunities with filters (status, category, min_score)
- `get` - Get detailed info about a specific opportunity
- `stats` - Get opportunity statistics (counts, averages)
- `search` - Search opportunities by keyword

**Example Usage:**
```
User: "Show my high-scoring opportunities"
PA: Uses opportunity_manager_tool(action='list', min_score=70)
```

#### 2. `task_manager_tool`
Manage OpportunityTasks (action items from high-scoring opportunities).

**Actions:**
- `list` - List tasks with filters (status, priority)
- `get` - Get detailed task info
- `accept` - Accept a task (pending → accepted)
- `start` - Start working on task (accepted → in_progress)
- `apply` - Mark as applied to the opportunity
- `complete` - Mark as won/lost (closes the feedback loop)
- `add_note` - Add timestamped notes to a task

**Example Usage:**
```
User: "Mark task X as won - I got the job!"
PA: Uses task_manager_tool(action='complete', task_id='X', outcome='won')
```

#### 3. `pipeline_orchestrator_tool`
Trigger agent execution manually and check pipeline status.

**Actions:**
- `execute_task` - Execute the agent assigned to a task
- `execute_opportunity` - Execute via task (if exists)
- `status` - Get pipeline overview (pending, in_progress, completed)
- `queue` - Show next tasks to be executed

**Example Usage:**
```
User: "What's the pipeline status?"
PA: Uses pipeline_orchestrator_tool(action='status')
→ Shows: pending_tasks, in_progress, completed_last_7_days
```

#### 4. `revenue_tracker_tool`
Track revenue and ML prediction accuracy.

**Actions:**
- `log_revenue` - Log revenue from an opportunity
- `list_revenue` - List recent revenue records
- `stats` - Get revenue statistics (gross, net, fees)
- `accuracy` - Calculate ML prediction accuracy
- `link_content` - Link revenue to content created

**Example Usage:**
```
User: "I earned $500 from that Upwork job"
PA: Uses revenue_tracker_tool(action='log_revenue', opportunity_id='X', amount=500, platform='upwork')
```

## Files Modified

### Tool Descriptions
`core/prompts/tool_descriptions.py` (+90 lines)
- Added detailed descriptions for all 4 tools
- Includes USE THIS WHEN patterns for routing

### Tool Definitions
`core/assistant/tool_definitions.py` (+180 lines)
- Added 4 function definition schemas
- Registered in `get_tool_definitions()`

### Tool Dispatch
`core/personal_ai_assistant_enhanced.py` (+8 lines dispatch, +700 lines handlers)
- Added dispatch cases for 4 tools
- Implemented `_handle_opportunity_manager_tool()`
- Implemented `_handle_task_manager_tool()`
- Implemented `_handle_pipeline_orchestrator_tool()`
- Implemented `_handle_revenue_tracker_tool()`

### Documentation
- `CLAUDE.md` - Updated PA Tools count (77 → 81)
- Added Session 672/673 to Recent Sessions

## Complete ML Pipeline (Session 672 + 673)

```
AUTOMATED FLOW:
Spiders ──► SpiderData ──► ML Score ──► Opportunity ──► OpportunityTask ──► Agent ──► Outcome
   │                          │              │               │                │         │
   │                          │              │               │                │         │
   └─ 77 spiders          v5.0 model    High-score       Auto-created     Celery     Revenue
      fetch data          scores data   threshold=70     from opp         executes   tracked

MANUAL CONTROL (NEW):
Personal Assistant (Brain)
    │
    ├── opportunity_manager_tool ──► Query opportunities
    ├── task_manager_tool ──► Manage task lifecycle
    ├── pipeline_orchestrator_tool ──► Manual execution
    └── revenue_tracker_tool ──► Track outcomes, ML accuracy
```

## Testing Verification

```bash
# All handlers exist and are callable
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django
django.setup()
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
print('Handlers:',
    hasattr(EnhancedPersonalAIAssistant, '_handle_opportunity_manager_tool'),
    hasattr(EnhancedPersonalAIAssistant, '_handle_task_manager_tool'),
    hasattr(EnhancedPersonalAIAssistant, '_handle_pipeline_orchestrator_tool'),
    hasattr(EnhancedPersonalAIAssistant, '_handle_revenue_tracker_tool'))
"
# Output: Handlers: True True True True
```

## Session 674 Recommendations

1. **End-to-End Test**: Test the complete flow from PA command through pipeline
2. **UI Dashboard**: Add a "Pipeline Status" widget to the frontend
3. **ML Accuracy Tracking**: As outcomes accumulate, monitor score correlation
4. **Notification System**: Alert user when high-value opportunities arrive
